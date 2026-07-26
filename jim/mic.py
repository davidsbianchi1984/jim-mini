"""Channel 2: a second microphone, for the agent.

A phone has one microphone and one foreground claim on it. While somebody is
on a call, the Guardian is deaf — which is precisely when they might want to
ask it something, and precisely when it cannot hear them ask.

Most people are already carrying a second microphone: a watch, earbuds, a
lapel or clip-on mic, glasses. This is the surface that lends one to the agent
as its own input channel — **channel 2** — for as long as the primary is
occupied, and takes it back afterwards.

**What lives here is permission and state, not audio.** Capture happens on the
device; nothing in this module touches a sample. What the service owns is
whether the agent may listen right now, on which microphone, and a record of
when it did — the same division as everywhere else in this codebase.

Five refusals carry the design.

**Only a microphone pointed at you** (:data:`MIC_TYPES`). A worn or clipped-on
mic hears mostly its wearer; a speakerphone, conference puck, or room array
hears whoever is present, and those people never agreed and usually do not
know there is a decision being made. A stationary device is refused whatever
microphone is in it, because something bolted to a room hears the room.

**Only while the primary is actually occupied.** If the phone's microphone is
free the agent should use it. A second ear granted for no reason is just a
second ear, and the reason is what bounds it.

**Not the microphone already carrying the call.** Once anything worn can be
channel 2, the two can collide: earbuds on a call are the *occupied*
microphone, and lending them asks one microphone to be two channels. A watch
never had this problem, which is why the first version of this module did not
look for it.

**Never on speakerphone.** The load-bearing one. On an earpiece or a headset
channel 2 hears its wearer; on speaker it hears *the other party too* —
someone who is not a user of this product, was never asked, and cannot revoke
anything. A microphone the Guardian holds must not become a way to record the
person on the other end of somebody else's call.

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

# Routings where the second microphone hears only its wearer. Anything else —
# notably `speaker` — puts a non-consenting voice in range.
PRIVATE_ROUTES = ("earpiece", "headset", "bluetooth_headset")

# What may become channel 2, and what may not.
#
# The first version of this allowed only `kind == "wearable"`, which was the
# right *instinct* reached by the wrong measure: a watch qualified and a lapel
# mic did not, though a lapel mic is aimed at one collar and a watch is aimed
# at a whole wrist. The axis that matters is not how the device attaches — it
# is **who the microphone is pointed at**.
#
# A personal microphone is worn or clipped on one person and hears mostly them.
# An ambient one sits in a room and hears whoever is in it, which is the thing
# that cannot be lent: the people it picks up never agreed and are usually not
# even aware there is a decision being made.
MIC_TYPES: dict[str, bool] = {          # name -> personal?
    # Personal — worn, clipped, or in the ear.
    "watch": True,
    "earbuds": True,
    "headset": True,
    "lapel": True,
    "clip_on": True,
    "bone_conduction": True,
    "glasses": True,
    "collar_tag": True,
    "handheld": True,                   # a stick mic somebody is holding
    # Ambient — pointed at a room.
    "speakerphone": False,
    "conference": False,
    "console": False,
    "laptop": False,
    "room_array": False,
    "doorbell": False,
}
PERSONAL_TYPES = tuple(k for k, v in MIC_TYPES.items() if v)

# How much channel 2 picks up. Named `gain` rather than `sensitivity` because
# `users.sensitivity` is already the escalation dial, and two settings with one
# name is how somebody eventually turns the wrong one.
#
# This is not an audio-quality preference. It is **the mechanism** behind the
# sentence the product tells the user — *the agent hears you, not your call.*
# On an earpiece the other party's voice is in the air near the wearer, and a
# channel wide enough to pick up a room picks that up too. A promise enforced
# by a policy is a promise until somebody edits the policy; enforced by the
# capture width, it is a fact about what the microphone can hear.
#
# `reaches_others` is what the level is judged on: not how loud, but whether
# somebody who did not agree ends up inside it.
GAIN_LEVELS: dict[str, dict] = {
    "near_field": {
        "reaches_others": False,
        "describes": "your own voice, close to the microphone",
    },
    "normal": {
        "reaches_others": True,
        "describes": "you and whatever is happening near you",
    },
    "wide": {
        "reaches_others": True,
        "describes": "the room, including people who are not talking to you",
    },
}
DEFAULT_GAIN = "near_field"

# Reasons where another person's voice is in the air. While one of these is
# what occupies the primary, channel 2 stays near-field however the user has
# set it — a dial that can be turned up into somebody else's conversation is
# not a safeguard, it is a suggestion.
OTHERS_AUDIBLE = ("voice_call", "video_call", "live_room")


class MicError(ValueError):
    """A handover that must not happen. Carries text meant for a person."""


# --------------------------------------------------------------------------- #
# attaching a wearable
# --------------------------------------------------------------------------- #

def attach(user_id: str, device_name: str, mic_type: str) -> dict:
    """Nominate a registered device's microphone as **channel 2** — the
    agent's own input, separate from the one carrying the user's voice.

    Attaching is not listening. It says *which* microphone may be lent, and
    nothing more — the lending is :func:`handover`, and it needs a reason.
    """
    row = db.connect().execute(
        "SELECT * FROM devices WHERE user_id=? AND name=?"
        " ORDER BY created_at DESC, rowid DESC LIMIT 1",
        (user_id, device_name)).fetchone()
    if row is None:
        raise MicError(f"no device called {device_name!r} on this account")
    if mic_type not in MIC_TYPES:
        raise MicError(
            f"unknown microphone type {mic_type!r} — one of "
            f"{', '.join(sorted(MIC_TYPES))}")
    if not MIC_TYPES[mic_type]:
        raise MicError(
            f"a {mic_type.replace('_', ' ')} microphone is pointed at a room, "
            "not at you. Everyone it picks up would be lending their voice "
            "without being asked, so it cannot be channel 2. A worn or "
            "clipped-on microphone can: "
            f"{', '.join(t.replace('_', ' ') for t in PERSONAL_TYPES)}")
    if row["kind"] == "stationary":
        raise MicError(
            f"{device_name!r} is registered as a stationary device. Something "
            "bolted to a room hears the room, whatever kind of microphone is "
            "in it")

    conn = db.connect()
    conn.execute(
        "INSERT INTO mic_channels (user_id, device_id, device_name, mic_type,"
        " created_at) VALUES (?,?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET"
        " device_id=excluded.device_id, device_name=excluded.device_name,"
        " mic_type=excluded.mic_type",
        (user_id, row["id"], device_name, mic_type, db.utcnow()))
    conn.commit()
    return {"attached": True, "device": device_name, "mic_type": mic_type,
            "channel": 2,
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
# gain — how wide the channel listens
# --------------------------------------------------------------------------- #

def set_gain(user_id: str, gain: str) -> dict:
    """Turn channel 2 up or down. Adjustable any time, including mid-session.

    The setting is honoured everywhere it is safe to honour it, and **capped
    while somebody else's voice is in the air** — see :func:`effective_gain`.
    Turning the dial up during a call does not fail; it is recorded, and it
    takes effect when the call ends. Refusing the adjustment outright would
    teach people the control is broken, when what is actually happening is
    that the situation is temporarily narrower than their preference.
    """
    if gain not in GAIN_LEVELS:
        raise MicError(
            f"gain must be one of {', '.join(GAIN_LEVELS)}")
    if channel(user_id) is None:
        raise MicError("nothing attached — attach a microphone first")
    conn = db.connect()
    conn.execute("UPDATE mic_channels SET gain=? WHERE user_id=?",
                 (gain, user_id))
    conn.commit()
    return {"gain": gain, **effective_gain(user_id)}


def effective_gain(user_id: str) -> dict:
    """What the microphone is actually running at, and why.

    The user's setting is the ceiling they asked for; this is the ceiling they
    get. The two differ exactly when somebody who never agreed would otherwise
    be inside the capture.
    """
    chan = channel(user_id)
    if chan is None:
        return {"effective_gain": None, "capped": False, "because": None}
    wanted = chan["gain"] or DEFAULT_GAIN
    live = _live(user_id)
    if live and live["reason"] in OTHERS_AUDIBLE and wanted != "near_field":
        return {
            "effective_gain": "near_field",
            "capped": True,
            "requested_gain": wanted,
            "because": f"a {live['reason'].replace('_', ' ')} is in progress, "
                       "so another person's voice is in the air. Your setting "
                       "comes back when it ends",
        }
    return {"effective_gain": wanted, "capped": False,
            "because": None,
            "describes": GAIN_LEVELS[wanted]["describes"]}


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
             others_present: bool = False,
             primary_device: str | None = None) -> dict:
    """Lend the agent channel 2 while the primary is busy.

    ``route`` is how the occupying call is being heard. It is required rather
    than optional because the safe answer depends entirely on it, and a
    default would pick one on the user's behalf.

    ``primary_device`` is what is carrying that call. Once anything worn can
    be channel 2, the two can collide: earbuds on a call are *the occupied
    microphone*, and lending them to the agent asks one microphone to be two
    channels. A watch never had this problem, which is why the first version
    did not look for it.
    """
    chan = channel(user_id)
    if chan is None:
        raise MicError(
            "nothing attached — attach a microphone before handing it over")
    if primary_device and primary_device == chan["device_name"]:
        raise MicError(
            f"your {chan['device_name'].replace('_', ' ')} is already carrying "
            "the call — one microphone cannot be both channels. Attach a "
            "different one as channel 2, or take the call on something else")
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
        " reason, route, mic_type, gain, primary_device, started_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?)",
        (session_id, user_id, chan["device_id"], chan["device_name"], reason,
         route, chan["mic_type"],
         "near_field" if reason in OTHERS_AUDIBLE
         else (chan["gain"] or DEFAULT_GAIN),
         primary_device, db.utcnow()))
    conn.commit()
    return {"id": session_id, "listening": True, "channel": 2,
            "device": chan["device_name"], "mic_type": chan["mic_type"],
            **effective_gain(user_id),
            "reason": reason, "route": route,
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
        "mic_type": chan["mic_type"] if chan else None,
        "gain": chan["gain"] if chan else None,
        **effective_gain(user_id),
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
    return [{"id": r["id"], "device": r["device_name"],
             "mic_type": r["mic_type"], "gain": r["gain"],
             "reason": r["reason"],
             "route": r["route"], "started_at": r["started_at"],
             "ended_at": r["ended_at"],
             "ended_because": r["ended_because"],
             "live": r["ended_at"] is None}
            for r in rows]
