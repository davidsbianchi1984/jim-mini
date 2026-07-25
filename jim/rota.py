"""Who is actually on shift — a rota, rather than a list of names.

:mod:`jim.relay` shipped with ``JIM_SITE_ROSTER``: a comma-separated list, worked
top to bottom, every time. Its own docstring admitted the problem — *"a rota
with shift patterns is a scheduling product and pretending otherwise would hide
how little this knows"* — and that was honest, but it was also wrong about the
size of the gap. A flat list does not merely know less. At 2am it pages the
person who works days.

That matters more here than almost anywhere, because the case the relay exists
for **is** the night shift. Lone workers, plant rooms, single-staffed sites.
Getting "who is on right now" wrong at 3am is not a degraded feature; it is the
feature failing in exactly the hour it was built for.

So: a rota, and deliberately a small one. Not a scheduling product — no leave,
no swaps, no fairness, no recurrence grammar. Named people, the days they work,
and the hours. Three things it does get right, because each one is a way of
paging the wrong person:

**Shifts cross midnight.** ``18:00–06:00`` is the shift this whole module is
about, and it is the one a naive ``start <= now <= end`` comparison always gets
wrong — that test is false for every minute of a night shift. A wrapping shift
is checked as two intervals, and it belongs to the day it *started*: at 02:00
on Saturday, Friday's 18:00–06:00 shift is still running and it is Friday's
person who is on.

**A site is somewhere.** ``JIM_SITE_TZ`` is an IANA zone. Without it a rota
written in local time is evaluated in UTC, which in most of the world silently
shifts every boundary by hours — and does it *differently in summer*, so it
would look correct for half the year. UTC remains the default only because a
default has to be something; :func:`describe` reports which is in use.

**A rota has gaps.** Nobody is rostered at 4am on a bank holiday. That is a
real state, and the wrong response is to quietly fall back to the top of the
list as though it were a normal page. :func:`on_now` returns nobody, the relay
falls back to *everyone* — better to wake the wrong person than nobody — and
says that is what it did, so a gap shows up as a gap rather than as one person
being mysteriously popular at 4am.

``JIM_SITE_ROTA`` is JSON::

    [{"name": "Dana Okafor", "role": "on-call",
      "days": "mon-fri", "from": "18:00", "to": "06:00"},
     {"name": "Ash Bell", "role": "supervisor",
      "days": "sat,sun", "from": "08:00", "to": "20:00"}]

``days`` accepts ranges (``mon-fri``), lists (``sat,sun``), single days, and
``all``. Omitting ``days``/``from``/``to`` means always on — which is what
``JIM_SITE_ROSTER``'s plain names become, so the old configuration keeps
working and means what it always meant.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, time, timezone

DAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")


class RotaError(ValueError):
    """A rota that cannot be read. Raised at load, never at 3am."""


def timezone_name() -> str:
    return os.environ.get("JIM_SITE_TZ", "UTC")


def _tz():
    name = timezone_name()
    if name.upper() == "UTC":
        return timezone.utc
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo(name)
    except Exception:
        # An unknown zone must not take the relay down — but it must not be
        # silently treated as UTC either, because that is the bug this
        # module exists to prevent. describe() reports the fallback.
        return timezone.utc


def tz_is_valid() -> bool:
    name = timezone_name()
    if name.upper() == "UTC":
        return True
    try:
        from zoneinfo import ZoneInfo
        ZoneInfo(name)
        return True
    except Exception:
        return False


def _parse_days(spec) -> tuple[str, ...]:
    if spec is None:
        return DAYS
    s = str(spec).strip().lower()
    if not s or s == "all":
        return DAYS
    out: list[str] = []
    for part in s.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, _, b = part.partition("-")
            a, b = a.strip()[:3], b.strip()[:3]
            if a not in DAYS or b not in DAYS:
                raise RotaError(f"unknown day range {part!r}")
            i, j = DAYS.index(a), DAYS.index(b)
            # mon-fri and fri-mon are both meaningful; the second wraps the
            # week the same way a night shift wraps a day.
            out.extend(DAYS[i:j + 1] if i <= j
                       else DAYS[i:] + DAYS[:j + 1])
        else:
            d = part[:3]
            if d not in DAYS:
                raise RotaError(f"unknown day {part!r}")
            out.append(d)
    return tuple(dict.fromkeys(out))


def _parse_time(spec, fallback: time) -> time:
    if spec is None or str(spec).strip() == "":
        return fallback
    s = str(spec).strip()
    # 24:00 is a legal way to write "the end of the day" and datetime is not
    # willing to parse it, so it is normalised rather than rejected.
    if s in ("24:00", "2400"):
        return time(23, 59, 59)
    for fmt in ("%H:%M", "%H%M", "%H"):
        try:
            return datetime.strptime(s, fmt).time()
        except ValueError:
            continue
    raise RotaError(f"unreadable time {spec!r} — use HH:MM")


def entries() -> list[dict]:
    """The rota, normalised. ``JIM_SITE_ROTA`` wins; ``JIM_SITE_ROSTER``'s
    plain names become always-on entries so old configuration is unchanged."""
    raw = os.environ.get("JIM_SITE_ROTA", "").strip()
    if raw:
        try:
            parsed = json.loads(raw)
        except ValueError as exc:
            raise RotaError(f"JIM_SITE_ROTA is not valid JSON: {exc}") from exc
        if not isinstance(parsed, list):
            raise RotaError("JIM_SITE_ROTA must be a JSON list of shifts")
        out = []
        for i, e in enumerate(parsed):
            if not isinstance(e, dict) or not str(e.get("name", "")).strip():
                raise RotaError(f"rota entry {i} needs a name")
            out.append({
                "name": str(e["name"]).strip(),
                "role": str(e.get("role") or "responder").strip(),
                "days": _parse_days(e.get("days")),
                "from": _parse_time(e.get("from"), time(0, 0)),
                "to": _parse_time(e.get("to"), time(23, 59, 59)),
            })
        return out

    raw = os.environ.get("JIM_SITE_ROSTER", "")
    return [{"name": n.strip(), "role": n.strip(), "days": DAYS,
             "from": time(0, 0), "to": time(23, 59, 59)}
            for n in raw.split(",") if n.strip()]


def configured() -> bool:
    return bool(os.environ.get("JIM_SITE_ROTA", "").strip()
                or os.environ.get("JIM_SITE_ROSTER", "").strip())


def _wraps(e: dict) -> bool:
    return e["to"] <= e["from"]


def _covers(e: dict, at: datetime) -> bool:
    """Is this shift running at ``at``? ``at`` is site-local and aware.

    A wrapping shift is two intervals and is attributed to the day it started
    — the half after midnight belongs to *yesterday's* rostered day. Checking
    the wrapped half against today's weekday is the bug that puts Saturday's
    person on the floor at 2am on Saturday while Friday's night worker is
    still there.
    """
    today = DAYS[at.weekday()]
    yesterday = DAYS[(at.weekday() - 1) % 7]
    now = at.time()
    if not _wraps(e):
        return today in e["days"] and e["from"] <= now <= e["to"]
    if today in e["days"] and now >= e["from"]:
        return True                       # tonight's shift, before midnight
    return yesterday in e["days"] and now <= e["to"]   # last night's, after


def now() -> datetime:
    return datetime.now(_tz())


def on_now(at: datetime | None = None) -> list[dict]:
    """Who is on shift, in rota order. Possibly nobody."""
    at = at or now()
    if at.tzinfo is None:
        at = at.replace(tzinfo=_tz())
    else:
        at = at.astimezone(_tz())
    return [{"name": e["name"], "role": e["role"]}
            for e in entries() if _covers(e, at)]


def order(at: datetime | None = None) -> tuple[list[str], bool]:
    """``(names in the order to try, whether anybody was actually on)``.

    On-shift first. Then everybody else, because a rota gap must not mean
    nobody is woken — it means the relay is guessing, and the second element
    is how it admits that.
    """
    on = [p["name"] for p in on_now(at)]
    rest = [e["name"] for e in entries() if e["name"] not in on]
    return (on + rest, bool(on))


def describe(at: datetime | None = None) -> dict:
    """The rota as an operator should be able to read it — including at a
    given moment, so "who would you page right now?" is answerable before the
    night it matters rather than after."""
    at = at or now()
    names, anybody = order(at)
    return {
        "configured": configured(),
        "timezone": timezone_name(),
        "timezone_valid": tz_is_valid(),
        "evaluated_at": at.isoformat(),
        "on_now": on_now(at),
        "escalation_order": names,
        "anybody_on_shift": anybody,
        "shifts": [{
            "name": e["name"], "role": e["role"], "days": list(e["days"]),
            "from": e["from"].strftime("%H:%M"),
            "to": e["to"].strftime("%H:%M"),
            "crosses_midnight": _wraps(e),
        } for e in entries()],
        "note": (
            "nobody is rostered right now — the relay will work the whole "
            "rota rather than nobody" if configured() and not anybody else
            "site rota" if configured() else
            "no site rota configured; this is a personal deployment"),
    }


def next_free_slot_warning() -> str | None:
    """A configuration mistake worth naming out loud at read time.

    An unknown timezone falls back to UTC, and a rota written in local time
    then evaluates hours off — correctly for part of the year in some zones,
    which is worse than never working.
    """
    if configured() and not tz_is_valid():
        return (f"JIM_SITE_TZ={timezone_name()!r} is not a zone this system "
                f"knows; the rota is being evaluated in UTC, which will page "
                f"the wrong person by the size of the offset")
    return None
