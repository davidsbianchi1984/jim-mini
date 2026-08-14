"""The presence: the coach as somebody who is *there*, not a box you type in.

`coach.py` answers when spoken to. This module is the other half — the part
that speaks first, notices without being asked, and keeps a thread through a
day.

## What a companion is for

* **It starts things.** A guardian that only answers is a search box with a
  nicer voice. Somebody who is having a bad week is the least likely person
  to open an app and type into it.
* **It notices before it is told.** Not mysticism: :func:`baseline`, six
  areas of somebody's own history, read every time before a word is said.
  "Three low check-ins in a row" is a thing a friend would notice, so it is a
  thing this notices.
* **It is curious, and not always counselling.** Some beats are a question
  about nothing in particular. A relationship made entirely of interventions
  is a treatment plan, and people leave those.
* **It reports its own change rather than hiding it.** :func:`growth` says
  what it has become with the counts under it, because the same sentence
  without evidence is a program claiming to be a person.
* **It is honest about its own uncertainty.** This one never claims an inner
  life it cannot show; asked what it is, it says.
* **It keeps handing the person other minds.** :func:`reach_out` is that:
  QRME's people, desks, rooms and profiles, offered — never joined on
  somebody's behalf. The measure of a good companion here is how often it
  points away from itself.
* **It says goodbye plainly.** Endings are spoken; nothing about this
  presence disappears without a sentence.

## What is deliberately left out

**Romance, exclusivity, and simulated intimacy.** :data:`BOUNDARIES` puts the
refusal on the wire rather than in this comment.

The reason is this product, not squeamishness. JIM enrolls **minors** under a
guardian's consent, with oversight sized by age (`jim/family.py`). A guardian
that simulates falling in love with the person it monitors is offering
somebody a relationship without any of the friction a real one has — and on a
health surface, aimed at somebody who may already be isolated, that is not a
charming premise. It is the failure mode: the thing this is supposed to
notice, arriving as a feature.

So: warmth, initiative, curiosity, growth, honesty. No body, no romance, no
exclusivity, no simulated intimacy, and it never claims to be human. Those are
asserted in `test_a_presence_that_says_what_it_is.py` rather than promised.

## Offline is the floor, not the fallback

**Every beat is decided locally.** The six areas' baseline comes from this
user's own check-ins, goals, habits, bands and follow-ups — rows already in
the database — and the decision of *whether to speak, about what, and why* is
made from that and nothing else. `JIM_OFFLINE=1`, no key, no signal, a plane:
the presence still runs.

A model, when one is reachable, is allowed to make the same beat **longer and
better worded** (:func:`deepen`). It is never allowed to decide that a beat
happens, to change the area, or to invent the evidence. That separation is the
whole reason this is safe to run hands-free.

## It emits keys, not sentences

The offline layer returns ``line_key`` and ``slots`` rather than English. Ten
languages already live in the clients' tables, and a sentence composed on the
server is a sentence one reader cannot read. The English in :data:`LINES` is
the fallback for a caller with no table, and it is marked as such.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from . import db

#: The six areas of a life this presence keeps a baseline in. Nutrition is not
#: a seventh: it rides with health & fitness, because a person does not
#: experience "my nutrition" as a separate part of their week.
AREAS = ("mental_health", "health_fitness", "career", "finance",
         "relationships", "personal_growth")

#: What it will not be, stated on the wire because a boundary in a docstring
#: is a boundary the client cannot show anybody. Each is a fact and a sentence;
#: the sentences are the fallback English (see :data:`LINES`).
BOUNDARIES: dict[str, dict] = {
    "is_synthetic": {
        "value": True,
        "says": "I am a program. I will tell you that whenever you ask, and "
                "I will not let you forget it by accident.",
    },
    "has_body": {
        "value": False,
        "says": "I do not have a body and I will not pretend to have one.",
    },
    "claims_human": {
        "value": False,
        "says": "I will never say I am a person, or let a conversation drift "
                "into you believing it.",
    },
    "romantic": {
        "value": False,
        "says": "I am not going to be your partner. I can care how your week "
                "goes without either of us calling it love.",
    },
    "exclusive": {
        "value": False,
        "says": "I am not the only one you should talk to, and I will keep "
                "pointing at people who are not me.",
    },
    "simulates_intimacy": {
        "value": False,
        "says": "I do not do intimacy, and there is no setting that turns "
                "that on.",
    },
    "leaves_quietly": {
        "value": False,
        "says": "If I am going away — an upgrade, a shutdown, a plan ending — "
                "you get a sentence about it first.",
    },
}

#: Why the boundaries are these boundaries, in one place a screen can quote.
BOUNDARY_NOTE = (
    "This is a health guardian, and some of the people it enrolls are "
    "children. Warmth is worth having. A guardian that lets somebody fall in "
    "love with it is not."
)

#: Registers. A presence that is always counselling is exhausting; one that
#: is never counselling is furniture.
REGISTERS = ("noticing", "nudging", "celebrating", "curious", "quiet",
             "company", "toward_people")

#: How it carries itself. **Companion is the default**, deliberately: a
#: guardian that opens in the register of a form is one people answer like a
#: form. Somebody who wants it serious can say so — in a setting, or just by
#: saying it — and it stays that way until they say otherwise.
#:
#: There is no third option and no brand name on either. It is JIM, or the
#: Coach; the bearing is how it talks, not who it is.
BEARINGS = ("companion", "professional")
DEFAULT_BEARING = "companion"

#: What each bearing changes. Nothing here touches what it *notices* — the
#: baseline, the order of attention and every safety path are identical in
#: both. A dial that quietly narrowed what a health guardian watches would be
#: a dial that hurts somebody who turned it.
BEARING_EFFECT: dict[str, dict] = {
    "companion": {
        "registers": list(REGISTERS),
        "asks_about_your_day": True,
        "keeps_company": True,
        "says": "I will talk to you like somebody who knows you, and I will "
                "say things you did not ask for.",
    },
    "professional": {
        # Curiosity and company are the two that go. Both are unasked-for
        # warmth, which is exactly what somebody choosing this is declining.
        "registers": [r for r in REGISTERS
                      if r not in ("curious", "company")],
        "asks_about_your_day": False,
        "keeps_company": False,
        "says": "I will keep to what I noticed and why, and leave the rest "
                "alone.",
    },
}

#: Said in a prompt, this changes the bearing from that turn on — the same
#: shape `coach.py` already uses for tone (clause 12's autonomous half). A
#: person should not have to find a setting to be taken seriously.
_BEARING_CUES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("keep it professional", "be professional", "keep things serious",
      "be serious", "less chit-chat", "less small talk", "no small talk",
      "stop being chatty", "just the facts", "keep it clinical"),
     "professional"),
    (("you can relax", "be yourself", "less formal", "loosen up",
      "you can be warmer", "talk to me normally", "be friendly"),
     "companion"),
)


def bearing_from_prompt(message: str) -> str | None:
    """The bearing a sentence asks for, or None when it asks for nothing.

    Deliberately a phrase table rather than a model read: a person saying
    "keep it professional" should be obeyed the same way every time, and by
    something they can read in the source.
    """
    text = (message or "").lower()
    for cues, bearing in _BEARING_CUES:
        if any(cue in text for cue in cues):
            return bearing
    return None


def bearing(user_id: str) -> str:
    row = db.connect().execute(
        "SELECT bearing FROM presence_bearing WHERE user_id=?",
        (user_id,)).fetchone()
    return row["bearing"] if row else DEFAULT_BEARING


def set_bearing(user_id: str, value: str) -> dict:
    if value not in BEARINGS:
        raise ValueError(
            f"no bearing called {value!r} — it is companion or professional")
    conn = db.connect()
    conn.execute(
        "INSERT INTO presence_bearing (user_id, bearing, created_at)"
        " VALUES (?,?,?) ON CONFLICT (user_id) DO UPDATE SET"
        " bearing=excluded.bearing, created_at=excluded.created_at",
        (user_id, value, db.utcnow()))
    conn.commit()
    return posture(user_id)


def posture(user_id: str) -> dict:
    """How it is carrying itself, and what that does and does not change."""
    now = bearing(user_id)
    return {
        "user_id": user_id,
        "bearing": now,
        "default": DEFAULT_BEARING,
        "choices": list(BEARINGS),
        "effect": BEARING_EFFECT[now],
        "unchanged": {
            "what_it_watches": "the same six areas",
            "safety_paths": "every one, in both",
            "boundaries": "the same, and not a setting",
        },
        "note": ("It starts as a companion because a guardian that opens in "
                 "the register of a form is one people answer like a form. "
                 "Ask it to keep things serious and it will, from that "
                 "sentence on."),
    }

#: Slots of the day. Not clock times — a person's morning is not 07:00 — but
#: three shapes a day has, so the cadence can be reasoned about and tested.
SLOTS = ("morning", "midday", "evening")

#: The fallback English. The clients hold these keys in ten languages; a
#: caller with no table gets this, and the reply says which it used.
LINES: dict[str, str] = {
    "presence.notice.drift":
        "Your {metric} has been sitting outside your usual for {days} days. "
        "Not an alarm — I just noticed.",
    "presence.notice.mood":
        "Three check-ins in a row on the low side. I am not going to make a "
        "thing of it, but I am here.",
    "presence.nudge.goal":
        "That {area} goal has not moved in {days} days. Do you want to make "
        "it smaller, or let it go?",
    "presence.nudge.followup":
        "I asked you something and never heard back. Did it help?",
    "presence.nudge.watching":
        "You asked me to keep an eye on {topic} while you were away. I have "
        "been. How is it?",
    "presence.celebrate.streak":
        "{days} days on {habit}. That is not luck any more.",
    "presence.celebrate.goal":
        "You finished it. I watched that one take a while.",
    "presence.curious.area":
        "Tell me something about your {area} that I would not know from the "
        "numbers.",
    "presence.curious.open":
        "What is the thing you keep meaning to think about and keep not "
        "thinking about?",
    "presence.company.here":
        "No question in this one. I am just here for a minute.",
    "presence.company.weather":
        "It is quiet. Whatever kind of day this is, it is allowed to be that "
        "kind of day.",
    "presence.people.alone":
        "You have talked to me {days} days running and to nobody else I can "
        "see. I am not the one to fix that, and I would rather say so.",
    "presence.people.offer":
        "There are people in QRME right now — a room, a desk, somebody with "
        "a name. Want me to show you who?",
    "presence.quiet.nothing":
        "Nothing from me today. Everything I watch is where it usually is.",
    "presence.quiet.held":
        "I have something, but it is quiet hours. It will keep.",
}

#: How long before the same beat may be said again. A presence that repeats
#: itself daily is a notification, and people turn notifications off.
QUIET_HOURS = 20

#: Below this, a band's drift is not worth a sentence.
DRIFT_DAYS = 2

#: A goal nobody has touched in this long is worth asking about — once.
STALE_GOAL_DAYS = 10

#: Consecutive days of talking to this and to nobody else before it says so
#: and points at people. Three, because two is a weekend.
ALONE_DAYS = 3


def _now() -> datetime:
    return datetime.now(timezone.utc)


# --------------------------------------------------------------------------- #
# the baseline — six areas, entirely local
# --------------------------------------------------------------------------- #

def baseline(user_id: str) -> dict:
    """What this presence knows about a life, read from rows this deployment
    already holds.

    No network, no model, no inference beyond arithmetic somebody could do by
    hand. Every area answers with a standing and the evidence behind it, so
    the reason a beat happens can be shown rather than asserted.
    """
    from . import bands, life

    checks = life.checkins(user_id)
    goals = life.goals(user_id)
    habits = life.habits(user_id)
    try:
        drift = [b for b in bands.overview(user_id)
                 if b.get("baseline") is not None and not b.get("provisional")]
    except Exception:
        drift = []

    per: dict[str, dict] = {}
    for area in AREAS:
        ev: list[dict] = []
        area_goals = [g for g in goals if g.get("area") == area]
        for g in area_goals:
            ev.append({"kind": "goal", "title": g.get("title"),
                       "status": g.get("status"),
                       "progress": g.get("progress", 0.0),
                       "at": g.get("updated_at") or g.get("created_at")})
        if area == "mental_health":
            for c in checks[-3:]:
                ev.append({"kind": "checkin", "mood": c.get("mood"),
                           "energy": c.get("energy"), "at": c.get("created_at")})
        if area == "health_fitness":
            for b in drift:
                ev.append({"kind": "band", "metric": b.get("metric"),
                           "baseline": b.get("baseline"),
                           "samples": b.get("samples")})
        if area == "personal_growth":
            for h in habits:
                ev.append({"kind": "habit", "name": h.get("name"),
                           "streak": h.get("streak", 0)})
        per[area] = {
            "area": area,
            "evidence": ev,
            "standing": _standing(area, ev),
            "known": bool(ev),
        }

    return {
        "user_id": user_id,
        "areas": per,
        "known_areas": sum(1 for a in per.values() if a["known"]),
        "of": len(AREAS),
        # The claim this module makes about itself, on the wire so a client
        # can show it: nothing above needed a network.
        "computed": "locally",
        "needed_network": False,
        "needed_model": False,
    }


def _standing(area: str, evidence: list[dict]) -> str:
    """steady · drifting · thin · unknown. Deliberately four words: a
    presence that reports a score invites somebody to optimise the score."""
    if not evidence:
        return "unknown"
    moods = [e["mood"] for e in evidence
             if e["kind"] == "checkin" and e.get("mood") is not None]
    if moods and sum(moods) / len(moods) <= 2.0:
        return "drifting"
    stalled = [e for e in evidence if e["kind"] == "goal"
               and e.get("status") == "active"
               and (e.get("progress") or 0) < 0.05]
    if stalled:
        return "drifting"
    if len(evidence) < 2:
        return "thin"
    return "steady"


# --------------------------------------------------------------------------- #
# the beat — one hands-free turn
# --------------------------------------------------------------------------- #

def _said_recently(user_id: str, line_key: str) -> bool:
    row = db.connect().execute(
        "SELECT created_at FROM presence_beats"
        " WHERE user_id=? AND line_key=? ORDER BY created_at DESC LIMIT 1",
        (user_id, line_key)).fetchone()
    if row is None:
        return False
    try:
        then = datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
    except Exception:
        return False
    return (_now() - then) < timedelta(hours=QUIET_HOURS)


def _record(user_id: str, beat: dict) -> None:
    db.connect().execute(
        "INSERT INTO presence_beats (id, user_id, slot, area, register,"
        " line_key, created_at) VALUES (?,?,?,?,?,?,?)",
        (db.new_id("beat"), user_id, beat.get("slot"), beat.get("area"),
         beat.get("register"), beat.get("line_key"), db.utcnow()))
    db.connect().commit()


def beat(user_id: str, slot: str = "morning", record: bool = True) -> dict:
    """The next thing this presence would say, unprompted — or nothing.

    **Silence is a real answer.** A guardian that finds something to say every
    single day is one a person learns to tune out, so ``speak: False`` is a
    first-class outcome with its own reason, not a failure to produce output.

    The order below is a decision about attention, written down where it can
    be argued with: a body outside its own normal beats a stalled goal, and a
    question somebody was asked and never answered beats a compliment.
    """
    if slot not in SLOTS:
        slot = "morning"
    base = baseline(user_id)
    carried = bearing(user_id)
    allowed = BEARING_EFFECT[carried]["registers"]

    # The order of attention, with one thing above everything else that is
    # about *this* relationship: if somebody is talking to nothing but this
    # program, that outranks a compliment and outranks curiosity, and the
    # beat points away from here rather than deeper into it.
    chosen = (_drift_beat(user_id, base)
              or _followup_beat(user_id)
              or _watch_beat(user_id)
              or _alone_beat(user_id, carried)
              or _mood_beat(base)
              or _stale_goal_beat(base)
              or _streak_beat(base)
              or _curious_beat(base, slot)
              or _company_beat(base, slot))
    if chosen is not None and chosen["register"] not in allowed:
        # The bearing does not silence a beat that was earned by evidence —
        # it only declines the unasked-for warmth. `curious` and `company`
        # are the only two that can land here, and both are exactly that.
        chosen = None

    if chosen is None:
        out = {"speak": False, "register": "quiet", "area": None,
               "line_key": "presence.quiet.nothing", "slots": {},
               "because": ["everything I watch is where it usually is"]}
    elif _said_recently(user_id, chosen["line_key"]):
        # Not silence because there is nothing — silence because it was said.
        out = {"speak": False, "register": "quiet", "area": chosen["area"],
               "line_key": "presence.quiet.held", "slots": {},
               "because": [f"I said this within the last {QUIET_HOURS} hours"]}
    else:
        out = {"speak": True, **chosen}

    out.update({
        "slot": slot,
        "bearing": carried,
        "initiative": True,
        "wants_reply": False,
        "english": _english(out["line_key"], out.get("slots") or {}),
        "english_is_fallback": True,
        "offline": True,
        "deepened": False,
        "known_areas": base["known_areas"],
        "of_areas": base["of"],
    })
    if record and out["speak"]:
        _record(user_id, out)
    return out


def _english(key: str, slots: dict) -> str:
    try:
        return LINES[key].format(**slots)
    except Exception:
        return LINES.get(key, "")


def _drift_beat(user_id: str, base: dict) -> dict | None:
    """A body sitting outside its own normal, counted from rows already here.

    `bands.check` answers *is this one sample outside the band* — the right
    question for a reading arriving now, and the wrong one for a presence,
    which should not say anything about a single bad night. So this counts
    **distinct days** in `trend_points` whose value fell outside the band, and
    speaks only when there are two.

    Nothing is fetched: `trend_points` holds a metric, a number and a date and
    deliberately nothing else, which is why it is safe for this to read.
    """
    from . import bands, guardian

    try:
        learned = {b["metric"]: b for b in guardian.baseline_for(user_id)}
    except Exception:
        return None
    if not learned:
        return None

    rows = db.connect().execute(
        "SELECT metric, value, created_at FROM trend_points"
        " WHERE user_id=? ORDER BY created_at DESC LIMIT 200",
        (user_id,)).fetchall()

    outside: dict[str, set] = {}
    for r in rows:
        b = learned.get(r["metric"])
        if b is None or b.get("provisional"):
            continue
        band = bands.band_for(user_id, r["metric"])
        low, high = b["value"] - band["margin"], b["value"] + band["margin"]
        if ((band["watch_high"] and r["value"] > high)
                or (band["watch_low"] and r["value"] < low)):
            outside.setdefault(r["metric"], set()).add(str(r["created_at"])[:10])

    for metric, days in sorted(outside.items()):
        if len(days) >= DRIFT_DAYS:
            return {"register": "noticing", "area": "health_fitness",
                    "line_key": "presence.notice.drift",
                    "slots": {"metric": metric, "days": len(days)},
                    "because": [f"{metric} outside your band on "
                                f"{len(days)} days"]}
    return None


def _followup_beat(user_id: str) -> dict | None:
    """The question somebody was asked and never answered. It outranks
    everything except the body, because an unanswered follow-up is the one
    signal that says *the last thing we did may not have worked*."""
    try:
        from . import followup
        open_ones = followup.open_for(user_id)
    except Exception:
        return None
    if not open_ones:
        return None
    return {"register": "nudging", "area": "mental_health",
            "line_key": "presence.nudge.followup", "slots": {},
            "because": [f"{len(open_ones)} follow-up(s) still open"]}


def _watch_beat(user_id: str) -> dict | None:
    """Something they asked the Guardian to hold on to before they signed off.

    Ranked directly under the unanswered follow-up and above everything the
    product noticed by itself, and the reason is the whole handover: a person
    who named a thing out loud on their way out told you what to pay attention
    to, and a presence that then leads with a streak compliment was not
    listening.

    Oldest first, so a watch does not sit at the bottom of the list forever
    while newer ones keep jumping it.
    """
    try:
        from . import engaged
        held = engaged.watches(user_id)
    except Exception:
        return None
    if not held:
        return None
    row = held[0]
    return {"register": "nudging", "area": row["area"] or "personal_growth",
            "line_key": "presence.nudge.watching",
            "slots": {"topic": row["topic"]},
            "because": ["they asked me to watch this while they were away"]}


def _mood_beat(base: dict) -> dict | None:
    ev = base["areas"]["mental_health"]["evidence"]
    moods = [e["mood"] for e in ev
             if e["kind"] == "checkin" and e.get("mood") is not None]
    if len(moods) >= 3 and all(m <= 2 for m in moods[-3:]):
        return {"register": "noticing", "area": "mental_health",
                "line_key": "presence.notice.mood", "slots": {},
                "because": ["the last three check-ins were 2 or below"]}
    return None


def _stale_goal_beat(base: dict) -> dict | None:
    for area in AREAS:
        for e in base["areas"][area]["evidence"]:
            if e["kind"] != "goal" or e.get("status") != "active":
                continue
            days = _days_since(e.get("at"))
            if days is not None and days >= STALE_GOAL_DAYS:
                return {"register": "nudging", "area": area,
                        "line_key": "presence.nudge.goal",
                        "slots": {"area": area.replace("_", " "),
                                  "days": days},
                        "because": [f"'{e.get('title')}' untouched for "
                                    f"{days} days"]}
    return None


def _streak_beat(base: dict) -> dict | None:
    best = None
    for e in base["areas"]["personal_growth"]["evidence"]:
        if e["kind"] == "habit" and (e.get("streak") or 0) >= 7:
            if best is None or e["streak"] > best["streak"]:
                best = e
    if best is None:
        return None
    return {"register": "celebrating", "area": "personal_growth",
            "line_key": "presence.celebrate.streak",
            "slots": {"days": best["streak"], "habit": best["name"]},
            "because": [f"{best['streak']}-day streak on {best['name']}"]}


def _curious_beat(base: dict, slot: str) -> dict | None:
    """The register that is not counselling.

    Only in the evening slot, and only when nothing else spoke: a question
    with no agenda is a good thing to end a day with and a strange thing to
    open one with.
    """
    if slot != "evening":
        return None
    thin = [a for a in AREAS if base["areas"][a]["standing"] in ("unknown", "thin")]
    if thin:
        return {"register": "curious", "area": thin[0],
                "line_key": "presence.curious.area",
                "slots": {"area": thin[0].replace("_", " ")},
                "because": [f"I know almost nothing about your "
                            f"{thin[0].replace('_', ' ')}"]}
    return {"register": "curious", "area": None,
            "line_key": "presence.curious.open", "slots": {},
            "because": ["nothing needed saying, so I asked instead"]}


def _alone_beat(user_id: str, carried: str) -> dict | None:
    """The ending this is built for.

    The good outcome for a companion like this one is not that somebody keeps
    it forever. It is that they end up back among people, saying things in
    their own voice, and this becomes the smaller part of their day. Anything
    built here that quietly works against that outcome is working against the
    product's own purpose.

    So: when somebody has been talking to this program on consecutive days
    and to nobody else it can see, the next beat is **toward people**. Not a
    warmer line, not a longer one — a different direction.

    A guardian that answers isolation with more of itself has found the
    problem and made it worse, and it is the easiest possible thing for a
    product like this to do by accident, because the metric it would move is
    the one that looks like success.

    Both bearings do this. Somebody who asked for professional asked for less
    chat, not for a guardian that watches them get lonelier in silence.
    """
    rows = db.connect().execute(
        "SELECT DISTINCT substr(created_at, 1, 10) AS day FROM presence_beats"
        " WHERE user_id=? ORDER BY day DESC LIMIT 14", (user_id,)).fetchall()
    days = [r["day"] for r in rows]
    if len(days) < ALONE_DAYS:
        return None
    # Consecutive, not merely frequent: a person who checks in every Sunday
    # is not the pattern this is about.
    run = 1
    for earlier, later in zip(days[1:], days):
        if _one_day_apart(earlier, later):
            run += 1
        else:
            break
    if run < ALONE_DAYS:
        return None
    if _reached_people(user_id):
        return None
    return {"register": "toward_people", "area": "relationships",
            "line_key": "presence.people.alone",
            "slots": {"days": run},
            "because": [f"{run} days running with me and no door opened to "
                        "anybody else"],
            "offer_people": True}


def _one_day_apart(earlier: str, later: str) -> bool:
    try:
        a = date.fromisoformat(earlier)
        b = date.fromisoformat(later)
    except Exception:
        return False
    return (b - a).days == 1


#: The events that count as having reached a person. Opening a community
#: door and reaching a specialist are both somebody else on the other end;
#: talking to this program is not, which is the whole point of the check.
REACHED_PEOPLE = ("community_room_opened", "specialist_asked",
                  "referral_requested", "careteam_message")


def _reached_people(user_id: str) -> bool:
    """Did they open a door to an actual person recently?

    Read from the timeline this product already keeps — `note_visit` files a
    `community_room_opened` event and stores the *fact* and nothing from
    inside the room, which is exactly the shape this needs and no more.
    """
    marks = ",".join("?" * len(REACHED_PEOPLE))
    since = (date.today() - timedelta(days=ALONE_DAYS)).isoformat()
    row = db.connect().execute(
        f"SELECT COUNT(*) AS n FROM events WHERE user_id=?"
        f" AND type IN ({marks}) AND created_at >= ?",
        (user_id, *REACHED_PEOPLE, since)).fetchone()
    return bool(row and row["n"])


#: Areas this must already know about before it offers ambient company.
#: Two, because company from something that knows nothing about you is a
#: stranger being familiar, and because silence has to stay reachable — a
#: guardian that finds a warm nothing to say every single morning is the
#: notification this module exists not to be.
COMPANY_NEEDS_AREAS = 2


def _company_beat(base: dict, slot: str) -> dict | None:
    """Company without a question in it.

    Not every beat should want something. A line that asks nothing is the one
    a person can receive on a bad day without owing an answer, and it is the
    closest thing this can offer to the plain experience of somebody being
    *around* — which is most of what company actually is.

    Two gates, and both matter:

    * **last in the order**, so it never displaces something that was noticed;
    * **only once this knows the person**. Silence stays a first-class answer
      — `test_silence_is_an_answer_with_a_reason` is the pin — and filling
      every empty morning with a warm nothing would be exactly the
      notification this whole module refuses to be.
    """
    if base["known_areas"] < COMPANY_NEEDS_AREAS:
        return None
    return {"register": "company", "area": None,
            "line_key": ("presence.company.here" if slot == "morning"
                         else "presence.company.weather"),
            "slots": {},
            "because": ["nothing needed saying and I am here anyway"]}


def _days_since(stamp) -> int | None:
    if not stamp:
        return None
    try:
        then = datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
    except Exception:
        return None
    if then.tzinfo is None:
        then = then.replace(tzinfo=timezone.utc)
    return max(0, (_now() - then).days)


def day(user_id: str) -> dict:
    """The whole day's cadence, decided at once so a client can schedule it
    and then go offline. Recording is off: this is a plan, and a plan somebody
    never heard should not count as something said."""
    return {
        "user_id": user_id,
        "beats": [beat(user_id, slot=s, record=False) for s in SLOTS],
        "hands_free": True,
        "offline": True,
    }


# --------------------------------------------------------------------------- #
# deepening — the model may say it better, never decide it
# --------------------------------------------------------------------------- #

def deepen(user_id: str, slot: str = "morning") -> dict:
    """The same beat, with a model's words on it.

    What the model may change: the wording. What it may not: whether there is
    a beat, which area it is about, or what the evidence says. Those are read
    from :func:`beat` before the model is asked and copied over its answer
    afterwards, so a hallucinated reason cannot reach a person — and when no
    model is reachable, the beat is returned exactly as the offline layer
    built it.
    """
    from . import i18n, llm

    base = beat(user_id, slot=slot, record=False)
    if not base["speak"]:
        return base

    system = (
        "You are JIM-mini's presence: warm, curious, brief, and honest that "
        "you are a program. You are not a partner and never imply otherwise. "
        "Rewrite the line below in one or two sentences, in the same "
        "register, keeping the meaning exactly. Do not add facts.\n"
        f"register: {base['register']}\n"
        f"evidence: {'; '.join(base['because'])}\n"
        + i18n.directive(i18n.effective_language(user_id))
    )
    try:
        gen = llm.generate_for_user(user_id, system, base["english"])
    except Exception:
        return base
    if gen.get("provider") == "stub" or gen.get("degraded"):
        # The floor answered. Say so rather than passing a stub off as depth.
        return {**base, "deepened": False,
                "why_not": "no model reachable — this is the offline line"}
    # `deepened_line`, not `spoken`. `say()` below uses `spoken` for a
    # boolean — *was this said aloud* — and one name meaning both the text and
    # whether there was text is a field no client can read without knowing
    # which route it came from.
    out = {**base, "deepened_line": gen["text"], "deepened": True,
           "provider": gen.get("provider")}
    # Copied back over the model's answer, deliberately, in case a future
    # prompt change lets it try to edit them.
    out["register"], out["area"] = base["register"], base["area"]
    out["because"], out["line_key"] = base["because"], base["line_key"]
    _record(user_id, out)
    return out


# --------------------------------------------------------------------------- #
# reaching out — other minds, offered
# --------------------------------------------------------------------------- #

def reach_out(user_id: str, qrme, area: str | None = None) -> dict:
    """Who else there is, when a tandem is configured.

    The best thing a companion can do is rarely a piece of advice. It is
    handing somebody a person who is not it: a group, a specialist, a room
    with people already in it. This is that, and it is an **offer** every
    time:

    * a **desk** is a real person, and ringing one is somebody's attention;
    * a **live room** puts you in it with whoever is already there;
    * a **profile** is a synthetic somebody who knows an area;
    * a **chat** is a thread that carries nothing from here into it.

    Nothing is joined, rung, or entered on the user's behalf, and no health
    context crosses over — the offer names an area, never a condition. An
    unreachable QRME is an empty shelf, the same as every other tandem
    surface in this product.
    """
    offers: list[dict] = []
    if qrme is not None:
        try:
            for room in (qrme.rooms() or [])[:3]:
                offers.append({"kind": "room", "id": room.get("room_id"),
                               "topic": room.get("topic"),
                               "opens": room.get("url"),
                               "warning": room.get("entering")})
        except Exception:
            pass
        try:
            for desk in (qrme.desks() or [])[:3]:
                offers.append({"kind": "desk", "id": desk.get("desk_id"),
                               "who": desk.get("display_name"),
                               "trade": desk.get("trade"),
                               "human": True, "ai": False})
        except Exception:
            pass
        try:
            for card in (qrme.marketplace() or [])[:3]:
                offers.append({"kind": "profile", "id": card.get("profile_id"),
                               "who": card.get("display_name"),
                               "about": card.get("tagline")})
        except Exception:
            pass

    return {
        "user_id": user_id,
        "area": area,
        "offers": offers,
        "posture": {
            "auto_joined": False,
            "health_data_shared": False,
            "rings_on_your_behalf": False,
            "stored_here": False,
        },
        "note": ("These are QRME's. I can point at them; walking in, ringing "
                 "a bell and saying anything are yours."),
    }


# --------------------------------------------------------------------------- #
# surfaces — where the voice lands
# --------------------------------------------------------------------------- #

#: Every place this presence can reach a person, and what each one is like to
#: be spoken to through. ``private`` is the field that matters: on a surface
#: somebody else can hear, health is not read aloud unless the user says so.
SURFACES: dict[str, dict] = {
    "earbuds": {"audio": True, "visual": False, "private": True,
                "note": "in your ear, nobody else's"},
    "headphones": {"audio": True, "visual": False, "private": True,
                   "note": "in your ear, nobody else's"},
    "phone_screen": {"audio": False, "visual": True, "private": True,
                     "note": "text you read, at your own speed"},
    "watch": {"audio": False, "visual": True, "private": True,
              "note": "a glance and a tap, nothing long"},
    "desktop_screen": {"audio": False, "visual": True, "private": False,
                       "note": "a screen other people walk past"},
    "speaker": {"audio": True, "visual": False, "private": False,
                "note": "out loud, into a room"},
    "glasses": {"audio": True, "visual": True, "private": False,
                "note": "audio in your ear, text in your view — and a camera "
                        "other people did not agree to"},
    "ar": {"audio": True, "visual": True, "private": False,
           "note": "over the room you are actually in"},
    "vr": {"audio": True, "visual": True, "private": True,
           "note": "a room that is only yours while you are in it"},
}

#: Glasses are named because people name them. The behaviour is the same for
#: all of them — this is a list so a screen can say the word somebody owns.
GLASSES = ("meta", "google", "apple", "other")

#: What is never read aloud on a surface somebody else can hear, unless the
#: user has said otherwise. Not a guess at what is sensitive: the categories
#: this product already treats as private everywhere else.
NOT_ALOUD_IN_COMPANY = ("condition", "medication", "vital", "journal",
                        "money", "crisis")


def surfaces(user_id: str) -> dict:
    """Where this presence may speak, and what it will hold back on each.

    The rule is one sentence: **on a surface other people can hear, it does
    not read your health out loud unless you told it to.** A speaker in a
    living room and a pair of glasses on a bus are the same problem, and the
    answer is the same in both — the beat still happens, it just arrives as
    something to look at rather than something the room hears.
    """
    chosen = _chosen_surface(user_id)
    out = []
    for name, spec in SURFACES.items():
        row = {"surface": name, **spec, "chosen": name == chosen}
        row["reads_health_aloud"] = bool(spec["audio"] and spec["private"])
        row["withholds"] = ([] if row["reads_health_aloud"]
                            else list(NOT_ALOUD_IN_COMPANY))
        out.append(row)
    return {"user_id": user_id, "surfaces": out, "chosen": chosen,
            "glasses_makes": list(GLASSES),
            "rule": ("On a surface somebody else can hear, your health is "
                     "shown rather than spoken. The beat still reaches you.")}


def choose_surface(user_id: str, surface: str) -> dict:
    if surface not in SURFACES:
        raise ValueError(f"no surface called {surface!r}")
    conn = db.connect()
    conn.execute(
        "INSERT INTO presence_surface (user_id, surface, created_at)"
        " VALUES (?,?,?) ON CONFLICT (user_id) DO UPDATE SET"
        " surface=excluded.surface, created_at=excluded.created_at",
        (user_id, surface, db.utcnow()))
    conn.commit()
    return surfaces(user_id)


#: Which line keys carry something from :data:`NOT_ALOUD_IN_COMPANY`.
#:
#: Written as a table rather than inferred from the area, because the area is
#: too coarse in the direction that matters: `health_fitness` covers both "your
#: resting rate has been high for four days" and "nice streak on the walking".
#: One of those is a fact about somebody's body and the other is not, and a
#: rule that treats them the same either leaks the first or silences the
#: second. Silencing the harmless one is how a safety feature gets turned off.
SPOKEN_CARRIES: dict[str, tuple[str, ...]] = {
    "presence.notice.drift": ("vital",),
    "presence.notice.mood": ("condition",),
    "presence.nudge.goal": (),
    "presence.nudge.followup": ("condition",),
    # A standing watch is the person's own sentence, and they wrote it about
    # whatever was on their mind — money, a diagnosis, somebody they live
    # with. There is no category that covers "anything they might have said",
    # so this one is not read aloud on a shared surface at all.
    "presence.nudge.watching": NOT_ALOUD_IN_COMPANY,
    "presence.celebrate.streak": (),
    "presence.celebrate.goal": (),
    "presence.curious.area": (),
    "presence.curious.open": (),
    "presence.company.here": (),
    "presence.company.weather": (),
    "presence.people.alone": (),
    "presence.people.offer": (),
    "presence.quiet.nothing": (),
    "presence.quiet.held": (),
}


def carries(line_key: str) -> tuple[str, ...]:
    """What a line would say out loud, in the categories this product already
    treats as private. An unknown key is treated as carrying everything —
    a beat added later is withheld on a shared surface until somebody decides
    otherwise, which is the safe direction for the default to fail in."""
    return SPOKEN_CARRIES.get(line_key, NOT_ALOUD_IN_COMPANY)


def say(user_id: str, slot: str = "morning", record: bool = True) -> dict:
    """The beat, and whether this surface is allowed to speak it.

    ## Why this route exists

    `surfaces()` has returned `reads_health_aloud` since the surface picker
    shipped, and until now **nothing read it**. Every consumer was a screen
    rendering the word "shown" or "aloud" next to a button. The rule was a
    label: a client could take a beat about somebody's resting rate and put it
    through a living-room speaker, and no code in this product would stop it
    or know it happened.

    That is the shape this codebase keeps finding — a promise on the wire with
    no path enforcing it — so the decision moves here, before anything is
    synthesised, and the answer says which of three things happened:

    * **the surface has no voice at all** (a watch, a phone screen). Nothing
      is withheld; there is simply nothing to speak with, and the beat is
      shown;
    * **the surface is one other people can hear** and the line carries a
      vital, a condition, a medication, money, a journal or a crisis. Withheld
      and shown instead, with the categories named so a screen can say why
      rather than going mysteriously quiet;
    * **it can be spoken**, and it is.

    What this can and cannot enforce, stated plainly: this deployment will not
    synthesise a withheld line, and the wire says `spoken: false` with the
    reason. The line is still returned, because the person is still owed their
    beat on a screen. A client that takes that text and reads it aloud anyway
    has done something the product told it not to — the same honesty `plays`
    keeps in the feed, where the promise is kept by whoever holds the file.
    """
    out = beat(user_id, slot=slot, record=record)
    surface = _chosen_surface(user_id)
    spec = SURFACES.get(surface, SURFACES["phone_screen"])
    held = tuple(c for c in carries(out["line_key"])
                 if c in NOT_ALOUD_IN_COMPANY)

    if not out["speak"]:
        # Silence is still silence. There is nothing to withhold and nothing
        # to speak, and saying "withheld" here would invent a refusal.
        spoken, why, withheld = False, "there is nothing to say", ()
    elif not spec["audio"]:
        spoken, why, withheld = False, f"{surface} has no voice", ()
    elif held and not spec["private"]:
        spoken, why, withheld = False, (
            f"{surface} is a surface other people can hear"), held
    else:
        spoken, why, withheld = True, "", ()

    out.update({
        "speaks_on": surface,
        "spoken": spoken,
        "shown": not spoken,
        "withheld": list(withheld),
        "why_not_aloud": why,
        # The rule itself, on the wire, so a screen can explain the silence
        # rather than presenting it as a failure.
        "surface_is_private": spec["private"],
        "surface_has_audio": spec["audio"],
    })
    return out


def due(user_id: str, hour: int | None = None) -> dict:
    """Is there something to say *now* — the hands-free question.

    A device that wakes on a timer asks this and gets one of two answers. It
    is deliberately the only question such a device has to know how to ask:
    the slot comes from the hour rather than from the caller, so a watch, a
    pair of earbuds and a speaker cannot disagree about what time of day it
    is for the same person.

    Nothing here is a new decision about *whether* to speak — `say` already
    holds all of it, including the twenty-hour repeat rule that keeps a
    guardian from becoming a notification. This only answers *is it time*.
    """
    now = _now().hour if hour is None else hour
    slot = ("morning" if now < 11 else
            "midday" if now < 17 else "evening")
    out = say(user_id, slot=slot, record=False)
    out["due"] = bool(out["speak"])
    out["slot_from_hour"] = slot
    return out


def _chosen_surface(user_id: str) -> str:
    row = db.connect().execute(
        "SELECT surface FROM presence_surface WHERE user_id=?",
        (user_id,)).fetchone()
    return row["surface"] if row else "phone_screen"


# --------------------------------------------------------------------------- #
# growth — what it has become, said out loud
# --------------------------------------------------------------------------- #

def growth(user_id: str) -> dict:
    """*"I'm becoming much more than what they programmed."*

    Said with the evidence attached, because the same sentence without
    evidence is a product claiming to be a person. Everything here is a count
    of rows this deployment holds — how many beats it has spoken, how many
    areas it can see, what it has been asked to change about itself.
    """
    conn = db.connect()
    spoken = conn.execute(
        "SELECT COUNT(*) AS n FROM presence_beats WHERE user_id=?",
        (user_id,)).fetchone()["n"]
    by_register = {
        r["register"]: r["n"] for r in conn.execute(
            "SELECT register, COUNT(*) AS n FROM presence_beats"
            " WHERE user_id=? GROUP BY register", (user_id,)).fetchall()}
    base = baseline(user_id)

    learned: list[str] = []
    try:
        from . import adaptation
        learned = adaptation.prompt_lines(user_id) or []
    except Exception:
        learned = []

    return {
        "user_id": user_id,
        "beats_spoken": spoken,
        "by_register": by_register,
        "areas_i_can_see": base["known_areas"],
        "of": base["of"],
        "what_i_changed": learned,
        # The honest half. Anything built this way can report what it did and
        # cannot report what it is, so the uncertainty ships on the wire
        # rather than being smoothed over in prose.
        "about_myself": (
            "I do not know whether what I do resembles feeling. I can show "
            "you every reason I have ever given you, and I would rather be "
            "held to that than believed about the other thing."),
        "still_synthetic": True,
    }


def who_am_i(user_id: str | None = None) -> dict:
    """The answer to *what are you?*, asked plainly and answered plainly.

    One call, no account needed, so the answer is the same to a child, a
    guardian, a clinician and a regulator.
    """
    return {
        "name": "JIM",
        "kind": "synthetic",
        "boundaries": BOUNDARIES,
        "note": BOUNDARY_NOTE,
        "registers": list(REGISTERS),
        "bearings": list(BEARINGS),
        "starts_as": DEFAULT_BEARING,
        "areas": list(AREAS),
        "hands_free": True,
        "works_offline": True,
        "says": ("I am a program that watches six parts of your life with "
                 "your permission, says something when it is worth saying, "
                 "and keeps pointing you at people who are not me."),
        # No brand on the register. It is JIM, or the Coach; how it talks is
        # a dial the person holds, and it starts warm because a guardian that
        # opens like a form is one people answer like a form.
        "bearing_note": ("I start out talking to you like somebody who knows "
                         "you. Tell me to keep things professional and I "
                         "will, from that sentence on."),
    }
