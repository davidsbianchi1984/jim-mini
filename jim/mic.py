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

Two things bound what it hears, and they are deliberately separate.
:data:`VOICE_FOCUS` keys the channel on its wearer and drops the chatter — the
next table, a television, the room. :data:`GAIN_LEVELS` sets how far away that
wearer can be, and is capped while another person's voice is in the air. Focus
decides what is *listened to*; gain decides what is *in range*. Keeping both
means a failure of the first is still bounded by the second, which is the only
reason to have a filter and a limit rather than a filter alone.
"""

from __future__ import annotations

from . import db, i18n

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
# Every level describes **the wearer at some distance**, never a level of
# company. There is no setting where the answer to "what does it pick up" is
# "more people", because there is no situation in which somebody else's chatter
# is what the microphone was lent for. What widens is how far from the
# microphone its wearer can be, not how many voices come with them.
#
# `reaches_others` survives that reframing and is the property the cap is
# judged on. It does not mean other people are transcribed — :data:`VOICE_FOCUS`
# is what handles that. It means another person's voice is physically inside
# the pickup pattern at that width, which is a different and worse fact: focus
# is a filter, and a filter is a thing that can fail. A safeguard that only
# holds while the filter works is one safeguard, not two.
GAIN_LEVELS: dict[str, dict] = {
    "near_field": {
        "reaches_others": False,
        "describes": "you, speaking close to the microphone",
    },
    "normal": {
        "reaches_others": True,
        "describes": "you, at arm's length or across a desk",
    },
    "wide": {
        "reaches_others": True,
        "describes": "you, from anywhere in the room",
    },
}
DEFAULT_GAIN = "near_field"

# Channel 2 keys on its wearer's voice and drops the rest — background talk,
# a television, the people at the next table. Not a setting, and deliberately
# not one: an option to include the chatter is an option to record people who
# never agreed, and nobody ever handed the agent a microphone in order to be
# told what the next table was saying.
#
# It does not replace the gain cap and is not allowed to be used as an excuse
# for one. Focus decides what is *listened to*; gain decides what is *in
# range*. Keeping both means a failure of the first is still bounded by the
# second.
VOICE_FOCUS = True
FOCUS_NOTE = ("it keys on your voice and drops the rest — background talk, a "
              "television, the people at the next table")

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
        raise MicError(i18n.fill(i18n.NO_SUCH_DEVICE, device=repr(device_name)))
    if mic_type not in MIC_TYPES:
        raise MicError(i18n.fill(i18n.UNKNOWN_MIC_TYPE, got=repr(mic_type),
                                 choices=", ".join(sorted(MIC_TYPES))))
    if not MIC_TYPES[mic_type]:
        raise MicError(i18n.fill(
            i18n.ROOM_MIC_REFUSED, mic_type=mic_type.replace("_", " "),
            choices=", ".join(t.replace("_", " ") for t in PERSONAL_TYPES)))
    if row["kind"] == "stationary":
        raise MicError(i18n.fill(i18n.STATIONARY_DEVICE,
                                 device=repr(device_name)))

    conn = db.connect()
    conn.execute(
        "INSERT INTO mic_channels (user_id, device_id, device_name, mic_type,"
        " created_at) VALUES (?,?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET"
        " device_id=excluded.device_id, device_name=excluded.device_name,"
        " mic_type=excluded.mic_type",
        (user_id, row["id"], device_name, mic_type, db.utcnow()))
    conn.commit()
    return {"attached": True, "device": device_name, "mic_type": mic_type,
            "channel": 2, "voice_focus": VOICE_FOCUS,
            "note": "attached, not listening — the agent gets this microphone "
                    "only while your main one is busy, and only if you hand "
                    f"it over. When it does, {FOCUS_NOTE}"}


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
        raise MicError(i18n.fill(i18n.MUST_BE_ONE_OF, field="gain",
                                 choices=", ".join(GAIN_LEVELS)))
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
            "describes": GAIN_LEVELS["near_field"]["describes"],
            "voice_focus": VOICE_FOCUS,
            "because": f"a {live['reason'].replace('_', ' ')} is in progress, "
                       "so another person's voice is in the air. Your setting "
                       "comes back when it ends",
        }
    return {"effective_gain": wanted, "capped": False,
            "because": None,
            "describes": GAIN_LEVELS[wanted]["describes"],
            "voice_focus": VOICE_FOCUS}


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
        raise MicError(i18n.fill(
            i18n.MIC_ALREADY_ON_CALL,
            device=chan["device_name"].replace("_", " ")))
    if reason not in REASONS:
        raise MicError(i18n.fill(i18n.REASON_MUST_BE,
                                 choices=", ".join(REASONS)))

    if route not in PRIVATE_ROUTES:
        raise MicError(i18n.fill(i18n.SPEAKER_ROUTE_REFUSED,
                                 route=repr(route)))
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
                    f"microphone is busy. It hears you, not your call — "
                    f"{FOCUS_NOTE}"}


def heard(user_id: str, device_name: str, audio: bytes = b"",
          filename: str = "channel2.webm", words: str = "") -> dict:
    """What channel 2 actually picked up, delivered by the device holding it.

    This module's header has always said capture happens on the device and
    nothing here touches a sample. That was a true description of the
    division and, for a long time, of a pipe that did not exist: the
    second microphone could be attached, handed over, gained and audited,
    and there was no way for the wearable to hand anything in. A field
    report put it plainly — the switches and the channel are permission,
    with nothing honouring them.

        asked     may the agent listen on this device
        mattered  can the device get what it hears to the agent

    So this is the pipe, and it is deliberately the narrowest one that
    could work. Four refusals, each of them a rule that already existed
    somewhere in this file and had nothing to enforce it:

    * **Nothing attached.** Audio arriving for a channel nobody lent is
      audio nobody agreed to.
    * **Not handed over.** `handover` is the moment the agent is allowed
      to listen, with a reason and a route recorded. Sound arriving
      outside one is a microphone that opened itself.
    * **A different device.** The channel is lent to *one* wearable. A
      second device delivering under the channel's name would make the
      audit line — which device heard this — a guess.
    * **Nothing in it.** An empty body is a delivery that says something
      arrived when nothing did, which is the defect this round exists to
      stop repeating.

    A device may hand in either **words** it recognised itself or the
    **audio** for this deployment's ears to transcribe, and words are the
    better half of that choice: a watch with an on-device recogniser can
    answer the Guardian with nothing but text ever leaving the wrist, and
    it keeps working on a deployment with no transcription key at all.
    Audio is the fallback for a device that cannot listen for itself —
    the same bargain the console already strikes between its own
    recogniser and the record-and-send path.

    What comes back is the words either way, and the channel row
    remembers that it delivered. That last part is the honesty half:
    `state` can now say whether this channel has ever carried anything,
    instead of leaving "attached" to be read as "listening".
    """
    chan = channel(user_id)
    if chan is None:
        raise MicError(
            "nothing is attached as channel 2, so there is no second "
            "microphone to have heard this. Attach a worn microphone first")
    live = _live(user_id)
    if live is None:
        raise MicError(
            "the agent is not listening on channel 2 right now. A microphone "
            "delivers what it heard during a handover, not outside one — "
            "hand the channel over first, and it will be recorded with the "
            "reason it was lent")
    if device_name and device_name != chan["device_name"]:
        raise MicError(i18n.fill(
            i18n.MIC_LENT_ELSEWHERE,
            yours=chan["device_name"].replace("_", " "),
            theirs=device_name.replace("_", " ")))
    said = words.strip()
    if not said and not audio:
        raise MicError("nothing arrived in that — an empty delivery is not "
                       "something the microphone heard")
    if said:
        text = said
    else:
        # Transcribed by whatever this deployment uses for every other
        # spoken thing. Imported here rather than at module scope:
        # `voice` reaches a provider, and this module is imported by
        # paths that must not.
        from jim import voice

        text = voice.transcribe(audio, filename)
    conn = db.connect()
    conn.execute("UPDATE mic_channels SET last_heard_at=? WHERE user_id=?",
                 (db.utcnow(), user_id))
    conn.commit()
    # No `channel` key here on purpose: elsewhere on this wire `channel`
    # is a *route* — "email", "call or text 988" — and a second meaning
    # under the same name is the reader being misled between routes. The
    # door itself says which channel this was.
    return {"heard": text, "device": chan["device_name"],
            "session": live["id"], "reason": live["reason"],
            **effective_gain(user_id)}


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
    # Whether this channel has ever actually carried anything. The same
    # rule the monitor roster learned: attached is a permission, and a
    # screen that prints it as listening is printing a promise as a fact.
    #   unattached — nothing lent
    #   silent     — lent, and nothing has ever come through it
    #   carrying   — something has
    last = (chan["last_heard_at"] if chan and "last_heard_at" in chan.keys()
            else None)
    return {
        "attached": chan["device_name"] if chan else None,
        "mic_type": chan["mic_type"] if chan else None,
        "gain": chan["gain"] if chan else None,
        "standing": "unattached" if not chan else (
            "carrying" if last else "silent"),
        "last_heard": last,
        **effective_gain(user_id),
        "listening": bool(live),
        "device": live["device_name"] if live else None,
        "since": live["started_at"] if live else None,
        "reason": live["reason"] if live else None,
        "route": live["route"] if live else None,
        "hears": ("you, on your "
                  f"{live['device_name'].replace('_', ' ')}") if live else
                 "nothing — your main microphone is the only one in use",
        # The disclosure belongs here, on the one function whose whole job is
        # *what can it hear right now, in words a person can check*. On a call
        # where both guardians are listening, "yours hears you" is a true
        # sentence and an incomplete one.
        **paired(user_id),
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


# --------------------------------------------------------------------------- #
# both parties on channel 2, at once
# --------------------------------------------------------------------------- #
#
# The field ask, in its own words: *both parties could use it while on the
# same call — both have profiles and both could be using them simultaneously.*
#
#     asked     can two people each have channel 2 on one call
#     mattered  does each of them know the other's guardian is listening
#
# Two people could already do the first half and neither could learn the
# second. `handover` is per person and always was: on a private route it hears
# its wearer and not the call, so two of them on one call never needed
# permission from each other and never conflicted. What was missing is that
# **nothing knew they were the same call** — so a person on a call where both
# guardians were listening had no way to find that out.
#
# That is the whole of what a pair is: a disclosure. It carries no audio, no
# content, and nothing either guardian heard. Each channel stays exactly as
# private as it was; what changes is that each person can see there are two.
#
# ## Pairing never grants listening
#
# A side may only join with a channel 2 it already has. Every refusal in
# `handover` — a private route, a busy primary, not the microphone carrying
# the call, nobody else in earshot — was passed before this row could name the
# session, so none of them can be reached around by pairing first. That
# ordering is deliberate and a test holds it: the cheap version of this
# function would open the channel itself, and would be a second door onto the
# thing that module spends four screens refusing.
#
# ## It forms only where both already knew each other
#
# `circle._mutual`, the same gate `jim/liaison.py` opens on, and for the same
# reason: a stranger who has your number should not be able to attach their
# guardian's session to yours, even as a label.
#
# ## The two halves never meet
#
# A pair names two session ids and neither side is ever handed the other's.
# What crosses is that somebody is listening and since when. Two guardians
# that need to say something to each other have a channel for it already, and
# it is not this one — `jim/liaison.py` is spoken over the network, recorded,
# split by side and readable afterwards by the person it works for. Audio
# never crosses either.

#: Why a pair ended. Words rather than a flag, because *they hung up* and
#: *somebody stopped it* read differently months later.
PAIR_ENDINGS = ("both_done", "left", "channel_closed", "stopped")


class NotMutual(RuntimeError):
    """Refused: these two are not each other's contacts."""


#: Its own sentence, because it is the rule the pairing is built on.
NOT_MUTUAL = ("these two are not each other's contacts — a channel pairs "
              "only where both people already had the other, and one side "
              "alone pairs with nothing")

#: Refused because there is no channel 2 to name yet. Pairing is a label on a
#: handover, never a way to get one.
NOTHING_TO_PAIR = ("your agent is not listening on a second microphone yet — "
                   "hand one over first, and then say who else is on the call")


def _pair_row(user_id: str) -> dict | None:
    """This person's open pair, if any."""
    row = db.connect().execute(
        "SELECT p.* FROM mic_pairs p JOIN mic_pair_sides s ON s.pair_id = p.id"
        " WHERE s.user_id=? AND p.ended_at IS NULL"
        " ORDER BY p.opened_at DESC, p.rowid DESC LIMIT 1",
        (user_id,)).fetchone()
    return dict(row) if row else None


def _sides(pair_id: str) -> dict[str, dict]:
    return {r["user_id"]: dict(r) for r in db.connect().execute(
        "SELECT * FROM mic_pair_sides WHERE pair_id=?", (pair_id,)).fetchall()}


def pair(user_id: str, other_id: str, about: str = "") -> dict:
    """Say that this person's channel 2 is one of two on the same call.

    Refused unless they already have one. The channel is opened by
    :func:`handover` and every refusal there has already been answered by the
    time this runs; naming it here adds a disclosure and adds nothing else.
    """
    from . import circle

    live = _live(user_id)
    if live is None:
        raise MicError(NOTHING_TO_PAIR)
    if not circle._mutual(user_id, other_id):
        raise NotMutual(NOT_MUTUAL)

    low, high = min(user_id, other_id), max(user_id, other_id)
    conn = db.connect()
    row = conn.execute(
        "SELECT * FROM mic_pairs WHERE low_id=? AND high_id=?"
        " AND ended_at IS NULL ORDER BY opened_at DESC, rowid DESC LIMIT 1",
        (low, high)).fetchone()
    if row is None:
        pair_id = db.new_id("pai")
        conn.execute(
            "INSERT INTO mic_pairs (id, low_id, high_id, about, opened_at)"
            " VALUES (?,?,?,?,?)",
            (pair_id, low, high, about.strip(), db.utcnow()))
    else:
        pair_id = row["id"]
    # `INSERT OR REPLACE`: joining twice is joining once, and a person whose
    # channel dropped and came back is naming a new session on the same call
    # rather than opening a second pair.
    conn.execute(
        "INSERT OR REPLACE INTO mic_pair_sides (pair_id, user_id, session_id,"
        " joined_at) VALUES (?,?,?,?)",
        (pair_id, user_id, live["id"], db.utcnow()))
    conn.commit()
    return paired(user_id)


def paired(user_id: str) -> dict:
    """Whether the other person's guardian is listening too — and nothing
    else about it.

    Deliberately thin. It answers *is there another channel on this call and
    since when*, which is the disclosure the pair exists for. It does not
    answer what they are hearing, on what, at what gain, or what their
    guardian did with it: none of that was ever this person's to read, and a
    pair that leaked it would be a worse arrangement than no pair at all.
    """
    row = _pair_row(user_id)
    if row is None:
        # Every key, on the empty answer too. A shape that grew fields only
        # when something was there would have four shells reading `undefined`
        # on the ordinary case, which is the one they meet most.
        return {"paired": False, "id": None, "with": None, "about": "",
                "yours_listening": _live(user_id) is not None,
                "theirs_listening": False, "theirs_since": None,
                "both": False, "opened_at": None}
    other = row["high_id"] if row["low_id"] == user_id else row["low_id"]
    sides = _sides(row["id"])
    theirs = sides.get(other)
    # Their side counts only while their own channel is actually open. A row
    # that outlived the session it names would report somebody as listening
    # after they hung up, which is the one thing this must never say.
    live_there = bool(theirs) and _live(other) is not None
    return {
        "paired": True,
        "id": row["id"],
        "with": other,
        "about": row["about"],
        "yours_listening": _live(user_id) is not None,
        "theirs_listening": live_there,
        "theirs_since": theirs["joined_at"] if theirs and live_there else None,
        # Both, or only mine so far. The honest middle state: this person has
        # said who else is on the call and the other side has not joined yet.
        "both": bool(live_there and _live(user_id) is not None),
        "opened_at": row["opened_at"],
    }


def unpair(user_id: str, why: str = "left") -> dict:
    """Leave the pair. It ends for both, because it was never more than the
    fact that there were two.

    The other person's channel 2 is untouched — it is theirs, they opened it,
    and one person leaving a call is not a reason for somebody else's agent to
    stop listening to them. What ends is the disclosure, and it ends on both
    sides at once because a pair one side still believed in would be exactly
    the wrong half to leave standing.
    """
    row = _pair_row(user_id)
    if row is None:
        return paired(user_id)
    conn = db.connect()
    conn.execute(
        "UPDATE mic_pairs SET ended_at=?, ended_because=? WHERE id=?",
        (db.utcnow(), why if why in PAIR_ENDINGS else "stopped", row["id"]))
    conn.commit()
    return paired(user_id)
