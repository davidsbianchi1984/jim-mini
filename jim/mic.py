"""A second ear: lending the Guardian a wearable's microphone.

A phone has one microphone and one foreground claim on it. While somebody is
on a call, the Guardian is deaf — which is precisely when they might want to
ask it something, and precisely when it cannot hear them ask.

A watch already on the wrist has its own microphone. This is the surface that
lends it: the user hands the agent the wearable's mic *for the duration the
primary is occupied*, and takes it back afterwards.

**What lives here is permission and state, not audio.** Capture happens on the
device; nothing in this module touches a sample. What the service owns is
whether the agent may listen right now, on which device, and a record of when
it did — the same division as everywhere else in this codebase.

Four refusals carry the design, and the third is the one that matters.

**Only a wearable this user registered.** A kitchen console's microphone is a
*room* microphone — always somewhere people talk without thinking about it.
Lending that is a different decision with a different consent question, and
folding the two together would let the easy case argue for the hard one.

**Only while the primary is actually occupied.** If the phone's microphone is
free the agent should use it. A second ear granted for no reason is just a
second ear, and the reason is what bounds it.

**Never on speakerphone.** This is the load-bearing refusal. On an earpiece or
a headset the wearable hears the wearer; on speaker it hears *the other party
too* — someone who is not a user of this product, was never asked, and cannot
revoke anything. A microphone the Guardian holds must not become a way to
record the person on the other end of somebody else's call.

**A handover ends.** It is scoped to the call that justified it, released
explicitly or closed out when that call ends. Nothing here persists into
tomorrow quietly, because a permission that outlives its reason is one nobody
remembers granting.
"""

from __future__ import annotations

from . import db

# Why a primary microphone is unavailable. Recorded rather than inferred: the
# reason is the thing that justifies the handover, so it belongs in the row.
REASONS = ("voice_call", "video_call", "recording", "dictation", "live_room")

# Routings where the wearable hears only the wearer. Anything else — notably
# `speaker` — puts a non-consenting voice in range.
PRIVATE_ROUTES = ("earpiece", "headset", "bluetooth_headset")


class MicError(ValueError):
    """A handover that must not happen. Carries text meant for a person."""


# --------------------------------------------------------------------------- #
# attaching a wearable
# --------------------------------------------------------------------------- #

def attach(user_id: str, device_name: str) -> dict:
    """Nominate a registered wearable as the agent's secondary microphone.

    Attaching is not listening. It says *which* device may be lent, and
    nothing more — the lending is :func:`handover`, and it needs a reason.
    """
    row = db.connect().execute(
        "SELECT * FROM devices WHERE user_id=? AND name=?"
        " ORDER BY created_at DESC, rowid DESC LIMIT 1",
        (user_id, device_name)).fetchone()
    if row is None:
        raise MicError(f"no device called {device_name!r} on this account")
    if row["kind"] != "wearable":
        raise MicError(
            f"{device_name!r} is a {row['kind']} device. Only a wearable can "
            "be lent this way — a stationary microphone is a room microphone, "
            "which is a different decision")

    conn = db.connect()
    conn.execute(
        "INSERT INTO mic_channels (user_id, device_id, device_name, created_at)"
        " VALUES (?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET"
        " device_id=excluded.device_id, device_name=excluded.device_name",
        (user_id, row["id"], device_name, db.utcnow()))
    conn.commit()
    return {"attached": True, "device": device_name,
            "note": "attached, not listening — the agent gets this microphone "
                    "only while your main one is busy, and only if you hand "
                    "it over"}


def detach(user_id: str) -> dict:
    """Remove the wearable, ending any live handover with it."""
    conn = db.connect()
    live = _live(user_id)
    if live:
        _close(live["id"], "detached")
    conn.execute("DELETE FROM mic_channels WHERE user_id=?", (user_id,))
    conn.commit()
    return {"attached": False, "ended_session": bool(live)}


def channel(user_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM mic_channels WHERE user_id=?", (user_id,)).fetchone()
    return dict(row) if row else None


# --------------------------------------------------------------------------- #
# lending it
# --------------------------------------------------------------------------- #

def _live(user_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM mic_sessions WHERE user_id=? AND ended_at IS NULL"
        " ORDER BY started_at DESC, rowid DESC LIMIT 1", (user_id,)).fetchone()
    return dict(row) if row else None


def _close(session_id: str, why: str) -> None:
    conn = db.connect()
    conn.execute("UPDATE mic_sessions SET ended_at=?, ended_because=?"
                 " WHERE id=? AND ended_at IS NULL",
                 (db.utcnow(), why, session_id))
    conn.commit()


def handover(user_id: str, reason: str, route: str,
             others_present: bool = False) -> dict:
    """Lend the agent the wearable's microphone while the primary is busy.

    ``route`` is how the occupying call is being heard. It is required rather
    than optional because the safe answer depends entirely on it, and a
    default would pick one on the user's behalf.
    """
    chan = channel(user_id)
    if chan is None:
        raise MicError(
            "no wearable attached — attach one before handing it over")
    if reason not in REASONS:
        raise MicError(
            f"reason must be one of {', '.join(REASONS)} — what is occupying "
            "your microphone is what justifies lending another one")

    if route not in PRIVATE_ROUTES:
        raise MicError(
            f"not while the call is on {route!r}. On speaker the watch hears "
            "whoever you are talking to, and they are not a user here — they "
            "were never asked and could not revoke it. Switch to an earpiece "
            "or a headset and it can listen to you alone")
    if others_present:
        raise MicError(
            "not while other people are in earshot — the agent would be "
            "listening to them too, and they did not agree to that")

    live = _live(user_id)
    if live:
        return {**live, "already_live": True}

    session_id = db.new_id("mic")
    conn = db.connect()
    conn.execute(
        "INSERT INTO mic_sessions (id, user_id, device_id, device_name,"
        " reason, route, started_at) VALUES (?,?,?,?,?,?,?)",
        (session_id, user_id, chan["device_id"], chan["device_name"], reason,
         route, db.utcnow()))
    conn.commit()
    return {"id": session_id, "listening": True,
            "device": chan["device_name"], "reason": reason, "route": route,
            "note": "the agent is listening on your "
                    f"{chan['device_name'].replace('_', ' ')} while your main "
                    "microphone is busy. It hears you, not your call"}


def release(user_id: str, why: str = "released") -> dict:
    """Take the microphone back."""
    live = _live(user_id)
    if live is None:
        return {"listening": False, "note": "the agent was not listening"}
    _close(live["id"], why)
    return {"listening": False, "id": live["id"], "ended_because": why}


def state(user_id: str) -> dict:
    """What the agent can hear right now, in words a person can check.

    Deliberately answerable without any argument beyond the user: "is it
    listening" should never require knowing which endpoint to ask.
    """
    chan = channel(user_id)
    live = _live(user_id)
    return {
        "attached": chan["device_name"] if chan else None,
        "listening": bool(live),
        "device": live["device_name"] if live else None,
        "since": live["started_at"] if live else None,
        "reason": live["reason"] if live else None,
        "route": live["route"] if live else None,
        "hears": ("you, on your "
                  f"{live['device_name'].replace('_', ' ')}") if live else
                 "nothing — your main microphone is the only one in use",
    }


def history(user_id: str, limit: int = 20) -> list[dict]:
    """Every time the agent held the second microphone, and for how long.

    A listening permission that leaves no trace is one nobody can audit, and
    this is the kind of permission people most want to check up on.
    """
    rows = db.connect().execute(
        "SELECT * FROM mic_sessions WHERE user_id=?"
        " ORDER BY started_at DESC, rowid DESC LIMIT ?",
        (user_id, limit)).fetchall()
    return [{"id": r["id"], "device": r["device_name"], "reason": r["reason"],
             "route": r["route"], "started_at": r["started_at"],
             "ended_at": r["ended_at"],
             "ended_because": r["ended_because"],
             "live": r["ended_at"] is None}
            for r in rows]
