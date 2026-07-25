"""The workplace relay — the agent that answers when nobody does.

The Guardian is a personal product, and for a desk-bound office worker a care
beacon adds little over walking to reception. The case where it earns its keep
is narrow, specific, and an established category: **lone and remote workers.**
Night shift, field engineers, plant rooms, single-staffed sites — anyone whose
failure mode is that nobody was there.

That case exposes a gap in :mod:`jim.beacons`. ``notify_contact`` assumes **a
contact who answers.** In a personal deployment that is a family member and
usually true. At 2am on a single-staffed site it may be nobody at all — and a
worker's personal emergency contact is the wrong recipient for a workplace
incident regardless.

So a site deployment adds a relay of last resort. It does three things, none of
them clinical:

* **Works the roster in order** rather than firing one notification into the
  void — on-call, then supervisor, then whoever the site listed after them.
* **Confirms a human actually accepted**, and keeps escalating until one does.
  This is the loop a fire-and-forget notification leaves open, and the whole
  reason to have a relay rather than a second phone number.
* **Answers the finder while they wait**, by calling the QRME first-aid
  guidance that already ships. A new caller to existing guidance, not a new
  model — JIM grows nothing here that it did not already have.

Two constraints do not bend.

**Incident scope, never person scope.** A corporate deployment must not become
a way for an employer to hold health data about employees. JIM's data promise
is per-user and does not bend because the licence was bought by a company. The
relay sees *an alarm was raised at this beacon and this is what is needed* —
not conditions, baseline, history, or check-ins. :func:`incident` is the whole
surface, and it is built from the alarm rather than from the person.

**The ceiling does not move.** A workplace relay still cannot reach
``emergency_services``; it escalates *people*, not sirens. An employer's agent
dispatching an ambulance for an employee is precisely the version of this that
should not exist.

See docs/beacons.md.
"""

from __future__ import annotations

import json
import os

from . import beacons, db, guardian, notify, rota

# The site's escalation order when nothing is configured. Per deployment
# rather than per user: it describes who is on shift, a property of the site.
DEFAULT_ROSTER = ("on-call", "supervisor", "site lead")


def roster() -> list[str]:
    """Who the relay works through, in order — **whoever is on shift first**.

    This used to be a flat comma-separated list, worked top to bottom every
    time, and its own comment admitted the limitation as a deliberate one. The
    limitation turned out to be the feature failing in the hour it was built
    for: the relay exists for night shift, and a flat list pages the day person
    at 2am. :mod:`jim.rota` answers *who is on now*; this puts them first.

    ``JIM_SITE_ROSTER`` still works and still means exactly what it meant —
    plain names, always on. ``JIM_SITE_ROTA`` adds days, hours and a timezone.
    """
    names, _ = rota.order()
    return names or list(DEFAULT_ROSTER)


def available() -> bool:
    """Whether a site deployment is configured at all.

    Unset is not a broken relay — it is a personal deployment, where the
    beacon's own ``notify_contact`` path is the right and only behaviour.
    """
    return rota.configured()


def incident(alarm: dict, beacon: dict) -> dict:
    """What the relay is allowed to know about an alarm.

    Everything here comes from the alarm and the beacon. Nothing comes from
    the person: no name, no conditions, no baseline, no history. That is the
    line that makes a workplace deployment acceptable rather than a
    surveillance product, and building the payload from the incident is how it
    is kept — rather than by remembering to strip fields from a user record.
    """
    return {
        "alarm": alarm["id"],
        "beacon": beacon["id"],
        "site_label": beacon["label"],
        "raised_at": alarm["created_at"],
        "reported": alarm["messages"],
        "state": alarm["state"],
        "accepted_by": alarm["accepted_by"],
        "needed": "a person to attend and confirm they are attending",
        "scope": "incident",
        "note": ("the relay sees the incident, never the worker's health "
                 "record — conditions, baseline and history stay with them"),
    }


def open_incidents(user_id: str) -> list[dict]:
    """Every unaccepted alarm on this account's site beacons."""
    out = []
    for a in beacons.alarms_for(user_id, open_only=True):
        b = beacons.get(a["beacon_id"])
        if b and b["kind"] == "site" and not a["accepted_by"]:
            out.append(incident(a, b))
    return out


def next_responder(alarm: dict) -> str | None:
    """The next name on the roster that has not already been tried.

    Position is derived from how many notifications the alarm has recorded, so
    a relay restarted mid-incident resumes where it was rather than beginning
    again at the top — the failure that turns an escalation into a loop.
    """
    tried = _notified(alarm["id"])
    names = roster()
    for n in names:
        if n not in tried:
            return n
    return None


def _notified(alarm_id: str) -> list[str]:
    row = db.connect().execute(
        "SELECT detail FROM events WHERE type='relay' AND detail LIKE ?"
        " ORDER BY created_at, rowid", (f'%"{alarm_id}"%',)).fetchall()
    out = []
    for r in row:
        try:
            d = json.loads(r["detail"])
        except ValueError:
            continue
        if d.get("alarm") == alarm_id and d.get("notified"):
            out.append(d["notified"])
    return out


def escalate(user_id: str, alarm_id: str, http=None) -> dict | None:
    """Notify the next person on the roster. Records who was tried.

    Returns ``exhausted`` when the roster runs out. That is deliberately not
    an error and deliberately not silent: a site whose whole roster failed to
    answer needs that fact visible, and there is nothing above it this relay
    is permitted to do.
    """
    alarms = [a for a in beacons.alarms_for(user_id) if a["id"] == alarm_id]
    if not alarms:
        return None
    alarm = alarms[0]
    if alarm["state"] != "open":
        return {"alarm": alarm_id, "state": alarm["state"],
                "note": "already resolved"}
    if alarm["accepted_by"]:
        return {"alarm": alarm_id, "accepted_by": alarm["accepted_by"],
                "note": "a person has already taken this"}

    who = next_responder(alarm)
    if who is None:
        return {
            "alarm": alarm_id,
            "exhausted": True,
            "tried": _notified(alarm_id),
            "call_emergency_services_yourself": True,
            "note": ("every name on the site roster has been notified and "
                     "none has accepted — this relay cannot escalate further, "
                     "and will not call emergency services on anyone's "
                     "behalf"),
        }

    # Actually send it. Until this existed, "notified" meant a row in `events`
    # saying somebody had been notified, and nothing had left the building —
    # so the loop this relay is built around could never close.
    on = rota.on_now()
    on_shift = any(p["name"] == who for p in on)
    role = next((p["role"] for p in on if p["name"] == who), "responder")
    beacon = beacons.get(alarm["beacon_id"])
    page = notify.page(incident(alarm, beacon), user_id, who, role, on_shift,
                       http)

    guardian._event(user_id, "relay", detail={"alarm": alarm_id,
                                              "notified": who})
    out = {
        "alarm": alarm_id,
        "notified": who,
        "role": role,
        # Named, because a page that went out only because the rota had run
        # dry is a guess, and the difference matters to whoever reads this.
        "on_shift": on_shift,
        "page": page,
        "reached_somebody": page["reached_somebody"],
        "remaining": [n for n in roster() if n not in _notified(alarm_id)],
        "awaiting": "acceptance — this stays open until a person confirms",
    }
    if not page["reached_somebody"]:
        # The caller has to be able to tell "waiting on a human" apart from
        # "waiting on a human who was never told". They escalate differently:
        # the second should move to the next name now, not after a timeout.
        out["unreached_note"] = notify.UNREACHED
        out["escalate_again_now"] = True
    return out


def accept(user_id: str, alarm_id: str, responder: str) -> dict | None:
    """A human takes the incident. This is what closes the loop.

    Not the same as clearing it: accepting says somebody is coming, clearing
    says it is over. Conflating them is how an alarm gets marked handled by
    the act of being *seen*.
    """
    if not responder.strip():
        raise ValueError("a responder needs a name — 'someone accepted it' is "
                         "the thing this relay exists to stop being enough")
    conn = db.connect()
    changed = conn.execute(
        "UPDATE beacon_alarms SET accepted_by=? WHERE id=? AND user_id=?"
        " AND state='open'", (responder.strip(), alarm_id, user_id)).rowcount
    conn.commit()
    if not changed:
        return None
    guardian._event(user_id, "relay", detail={"alarm": alarm_id,
                                              "accepted_by": responder.strip()})
    return {"alarm": alarm_id, "accepted_by": responder.strip(),
            "state": "open",
            "note": "still open — accepted means attending, not resolved"}


def guidance(alarm_id: str, question: str, qrme=None,
             profile_handle: str | None = None) -> dict:
    """What to tell the person waiting.

    Routed through QRME's existing first-aid specialists when tandem is
    configured, and otherwise answered with the one instruction that is always
    right and never depends on a model being reachable.
    """
    fallback = {
        "alarm": alarm_id,
        "source": "local",
        "answer": ("Call your local emergency number if you have not already. "
                   "Do not move them unless they are in danger where they "
                   "are. Stay with them until someone arrives."),
        "note": "standing guidance — no specialist was reachable",
    }
    handle = profile_handle or os.environ.get("JIM_SITE_FIRSTAID_PROFILE")
    if qrme is None or not handle:
        return fallback
    try:
        profile = qrme.resolve_handle(handle)
        # QRME's summon card names the profile `profile_id`, matching how
        # jim/seed.py reads it — `id` there is the interactor's.
        if not profile or not profile.get("profile_id"):
            return fallback
        interactor, _token = qrme.ensure_interactor("site responder")
        reply = qrme.specialist_reply(profile["profile_id"], interactor,
                                      question)
    except Exception:
        return fallback
    content = (reply or {}).get("content")
    if not content:
        return fallback
    return {
        "alarm": alarm_id,
        "source": "qrme",
        "answer": content,
        "ai": True,
        "note": "first-aid guidance from a QRME specialist; not a clinician",
    }
