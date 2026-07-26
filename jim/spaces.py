"""A room microphone, and what it costs to have one honestly.

(Named for the *space* it listens in. "Ambient" already means something else
here — `jim/guardian.py`'s background observation, the jump-in before you
ask — and reusing it for a microphone would blur two unrelated ideas.)

``jim/mic.py`` refuses anything pointed at a room, and gives the reason: the
people it picks up never agreed and usually do not know a decision is being
made. That refusal is right for *channel 2*, which is one person lending their
own voice.

It is not an argument that a room microphone can never exist. A kitchen
console that hears "I've fallen" is the thing a guardian product is for, and
this codebase already ships stationary devices — they just deliver guidance
and cannot take any in. What an ambient microphone needs is a **different**
consent model, not an exemption from having one.

Four things make it defensible, and the fourth is the one that matters.

**People are told, by the room itself.** A disclosure is required at
enrolment, and it must be something present in the space — an indicator, a
chime when it wakes, a spoken announcement, a posted notice. A setting buried
in the owner's app tells the owner, who already knew. Anyone else in the
kitchen learns nothing from it.

**It is never continuously listening.** Activation is a wake word or a
deliberate press. "Always on" is not a microphone with a long duty cycle; it
is a different object, and no disclosure makes it the first one.

**The household consents, not just the buyer.** The people who live with a
device are listed, because one person's purchase is not everyone's decision
about their own home.

**Anyone present can silence it, including someone with no account here.**
:func:`hold` takes no token. A guest, a cleaner, a visiting nurse, a child —
anybody who can reach the thing can mute it for a while, and nobody has to
enrol, log in, or ask the owner. This is the affordance that separates a room
microphone somebody could accept from one they merely have to tolerate: the
person with the least power in the room can turn it off.

That is only safe because **nothing here is load-bearing for safety**. The
escalation ladder runs on biometrics from worn sensors, not on room audio, so
silencing this microphone cannot silence an emergency. If that ever stopped
being true, the hold would have to be reconsidered — and the ladder, not the
hold, would be the thing that had gone wrong.

Permission and state only; capture is on the device.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from . import db

# How the room tells the people in it. At least one is required, and every
# option is something you could notice while standing there.
DISCLOSURES = ("indicator_light", "chime_on_wake", "spoken_announcement",
               "posted_notice")

# How it starts listening. `continuous` is deliberately absent: a microphone
# that never stops is a different object from one that wakes.
ACTIVATIONS = ("wake_word", "press_to_talk")

DEFAULT_HOLD_MINUTES = 60
MAX_HOLD_MINUTES = 60 * 24


class SpaceError(ValueError):
    """A room microphone that must not be set up this way."""


def _now() -> datetime:
    return datetime.now(timezone.utc)


# --------------------------------------------------------------------------- #
# enrolling a space
# --------------------------------------------------------------------------- #

def enroll(user_id: str, device_name: str, space: str, disclosure: list[str],
           activation: str, household: list[str] | None = None) -> dict:
    """Let a stationary device listen in a named space.

    Every argument after the device is a condition of doing so, which is why
    none of them has a default.
    """
    row = db.connect().execute(
        "SELECT * FROM devices WHERE user_id=? AND name=?"
        " ORDER BY created_at DESC, rowid DESC LIMIT 1",
        (user_id, device_name)).fetchone()
    if row is None:
        raise SpaceError(f"no device called {device_name!r} on this account")
    if row["kind"] != "stationary":
        raise SpaceError(
            f"{device_name!r} is a {row['kind']} device. A room microphone is "
            "for something that stays in the room — a worn one is channel 2, "
            "which is a different arrangement with a different consent story")

    unknown = [d for d in disclosure if d not in DISCLOSURES]
    if unknown:
        raise SpaceError(
            f"unknown disclosure {', '.join(unknown)} — one of "
            f"{', '.join(DISCLOSURES)}")
    if not disclosure:
        raise SpaceError(
            "a room microphone needs a way of telling the people in the room. "
            "A setting in your app tells you, and you already knew — pick "
            f"something present in the space: {', '.join(DISCLOSURES)}")
    if activation not in ACTIVATIONS:
        raise SpaceError(
            f"activation must be one of {', '.join(ACTIVATIONS)}. Continuous "
            "listening is not offered: a microphone that never stops is a "
            "different object from one that wakes, and no notice makes it the "
            "first one")

    space_id = db.new_id("spc")
    conn = db.connect()
    conn.execute(
        "INSERT INTO ambient_spaces (id, user_id, device_id, device_name,"
        " space, disclosure, activation, household, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        (space_id, user_id, row["id"], device_name, space,
         ",".join(disclosure), activation, ",".join(household or []),
         db.utcnow()))
    conn.commit()
    return {"id": space_id, "space": space, "device": device_name,
            "disclosure": disclosure, "activation": activation,
            "household": household or [],
            "note": "anyone in this room can silence it without an account — "
                    "that is deliberate, and nothing about your safety alerts "
                    "depends on it"}


def get(space_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM ambient_spaces WHERE id=?", (space_id,)).fetchone()
    if row is None:
        return None
    out = dict(row)
    out["disclosure"] = [d for d in out["disclosure"].split(",") if d]
    out["household"] = [h for h in out["household"].split(",") if h]
    return out


def spaces_for(user_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT id FROM ambient_spaces WHERE user_id=? ORDER BY created_at",
        (user_id,)).fetchall()
    return [state(r["id"]) for r in rows]


def remove(space_id: str) -> dict:
    conn = db.connect()
    conn.execute("DELETE FROM ambient_spaces WHERE id=?", (space_id,))
    conn.commit()
    return {"id": space_id, "removed": True}


# --------------------------------------------------------------------------- #
# the hold — the affordance that makes the rest defensible
# --------------------------------------------------------------------------- #

def hold(space_id: str, minutes: int = DEFAULT_HOLD_MINUTES,
         reason: str | None = None, placed_by: str | None = None) -> dict:
    """Silence this room's microphone for a while. **No token required.**

    Deliberately unauthenticated. A guest, a cleaner, a visiting nurse, a
    child — anybody who can reach the device can mute it, without enrolling,
    logging in, or asking the person who bought it. A mute only the owner can
    apply is a mute for the one person who was never going to need it.

    ``placed_by`` is free text and optional. Nobody should have to identify
    themselves to stop being recorded.
    """
    if get(space_id) is None:
        raise SpaceError("no such space")
    minutes = max(1, min(int(minutes), MAX_HOLD_MINUTES))
    until = _now() + timedelta(minutes=minutes)
    hold_id = db.new_id("hld")
    conn = db.connect()
    conn.execute(
        "INSERT INTO ambient_holds (id, space_id, until, reason, placed_by,"
        " created_at) VALUES (?,?,?,?,?,?)",
        (hold_id, space_id, until.isoformat().replace("+00:00", "Z"), reason,
         placed_by, db.utcnow()))
    conn.commit()
    return {"id": hold_id, "space_id": space_id, "held": True,
            "minutes": minutes,
            "until": until.isoformat().replace("+00:00", "Z"),
            "note": "this microphone is off. Nobody was asked to approve it "
                    "and nobody is notified who did it"}


def _active_hold(space_id: str) -> dict | None:
    now = _now().isoformat().replace("+00:00", "Z")
    row = db.connect().execute(
        "SELECT * FROM ambient_holds WHERE space_id=? AND lifted_at IS NULL"
        " AND until > ? ORDER BY until DESC LIMIT 1",
        (space_id, now)).fetchone()
    return dict(row) if row else None


def lift(hold_id: str) -> dict:
    """End a hold early. Also unauthenticated — whoever placed it may not be
    the one still here, and requiring the placer would strand the room."""
    conn = db.connect()
    row = conn.execute("SELECT * FROM ambient_holds WHERE id=?",
                       (hold_id,)).fetchone()
    if row is None:
        raise SpaceError("no such hold")
    conn.execute("UPDATE ambient_holds SET lifted_at=? WHERE id=?",
                 (db.utcnow(), hold_id))
    conn.commit()
    return {"id": hold_id, "held": False}


# --------------------------------------------------------------------------- #
# what it can hear
# --------------------------------------------------------------------------- #

def state(space_id: str) -> dict:
    """The whole picture for anyone who asks — including a guest at the door.

    Readable without a token on purpose: "is this thing listening to me" is a
    question the people least likely to have an account most need answered.
    """
    space = get(space_id)
    if space is None:
        raise SpaceError("no such space")
    held = _active_hold(space_id)
    return {
        "id": space_id,
        "space": space["space"],
        "device": space["device_name"],
        "listening": not held,
        "activation": space["activation"],
        "disclosure": space["disclosure"],
        "held_until": held["until"] if held else None,
        "hold_id": held["id"] if held else None,
        "hears": (
            "nothing — it is silenced until " + held["until"] if held else
            f"only after {space['activation'].replace('_', ' ')}; it is not "
            "listening the rest of the time"),
        "anyone_can_silence": True,
    }


def can_listen(user_id: str, space: str) -> bool:
    """Whether the agent may take audio from this space right now."""
    row = db.connect().execute(
        "SELECT id FROM ambient_spaces WHERE user_id=? AND space=?",
        (user_id, space)).fetchone()
    return bool(row) and _active_hold(row["id"]) is None


def holds_for(space_id: str, limit: int = 20) -> list[dict]:
    """Every time this room was silenced. Kept, because a pattern of holds is
    the room telling its owner something they should probably hear."""
    rows = db.connect().execute(
        "SELECT * FROM ambient_holds WHERE space_id=?"
        " ORDER BY created_at DESC, rowid DESC LIMIT ?",
        (space_id, limit)).fetchall()
    return [{"id": r["id"], "until": r["until"], "reason": r["reason"],
             "placed_by": r["placed_by"], "at": r["created_at"],
             "lifted_at": r["lifted_at"]} for r in rows]
