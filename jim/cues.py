"""What a room sees and hears, read as cues rather than kept as footage.

The field ask, in its own words: *monitor you from devices in your home such
as cameras, speakers, looking for visual cues and verbal cues.*

    asked     can it read a cue off a camera or a speaker
    mattered  can it do that without keeping what it read the cue from

:mod:`jim.monitors` said what may sense and who else it catches.
:mod:`jim.daybook` recorded what was taken in and dropped most of it, because
most of the roster promises to hold nothing. Neither ever read a **cue**. The
camera could be switched on and the room could be described to it, and nothing
looked at the description.

## The whole point: read on the way through, not out of storage

`jim/monitors.py` opens with the distinction this module exists to make true:

    "It notices you fell" and "it keeps the video of you falling" are
    different agreements, and only one of them is what the code does.

Until now that sentence was honest only because the code did neither. Reading
a cue out of stored content would have collapsed the two: it would mean the
useful half — noticing — was available only for the monitors that keep things,
and every promise of *nothing* in that roster would have become a promise of
*nothing useful*.

So :func:`jim.daybook.sensed` reads cues **before** it asks whether any of the
content may survive. A screen or a room camera with keeping switched off gets
exactly the same cue detection as one keeping everything, and stores exactly
as little as it promised. Noticing is free of retention, which is the only
arrangement under which a person can switch retention off without switching
off their guardian.

## The words are never what is kept

A cue row holds the cue and the monitor. It does not hold the sentence the cue
was read from, and :func:`seen` is written so it cannot: the text is a local,
the row takes the cue's name, and a test asserts no column exists to put the
words in. Otherwise this module would be the back door round the roster —
read the cue *and* stash the description, on a monitor that promised nothing.

## A monitor only yields cues its own senses can produce

A doorway senses a presence and nothing else, so it never yields a verbal cue
however the passing text is worded. This is checked against
:data:`jim.monitors.Monitor.senses` rather than trusted, because the cheap
version — scan every text for every cue — would have a presence sensor
reporting slurred speech, and the roster's `senses` column would be decoration.

## Critical cues go to a person

Each cue carries a severity in the vocabulary :mod:`jim.escalation` already
speaks, and :func:`seen` resolves it through that ladder rather than inventing
a second one. A `critical` cue is the one case in this product that must reach
a human quickly, and :mod:`jim.noticed` excludes `critical` from the pass that
puts things to a model — so the two compose the right way round without either
knowing about the other.

## What it cannot do, and says so

The table is plain phrase matching, deliberately, for the reasons
:mod:`jim.hazards` gives: it must work with the network cut, cost nothing, and
be auditable line by line. What it flags it can explain and what it misses a
person still can. It does not see; something else describes what it saw, and
this reads the description.

And it cannot tell **whose** cue it is. A room camera catches whoever is in
the room, and a cue read off one of them lands on the account holder's record
because that is the only record there is. The roster already refuses to switch
such a monitor on until somebody says the people in that space were told; this
module cannot improve on that claim, and does not pretend to. The monitor is
named on every cue so a reader can at least see it came from a room rather
than from a wrist.
"""

from __future__ import annotations

from . import db, escalation, monitors

#: What a cue can be read out of. A monitor whose `senses` do not include the
#: cue's sense never yields it, whatever the text says.
SENSES = ("sight", "sound")

#: Every cue this product will read, what it is read from, and what it means.
#:
#: Severities are :mod:`jim.escalation`'s vocabulary — `info`, `guidance`,
#: `critical` — rather than a second scale of this module's own. A cue that
#: had to be translated into the ladder's words on the way in would be a cue
#: whose urgency was decided twice.
CUES: dict[str, dict] = {
    # -- seen ---------------------------------------------------------------
    "fall": {
        "sense": "sight",
        "severity": "critical",
        "phrases": ("on the floor", "fell over", "has fallen", "collapsed",
                    "slumped", "lying on the ground"),
        "says": "you may have fallen",
        "reference": "CDC STEADI — older adult fall prevention",
    },
    "not_moving": {
        "sense": "sight",
        "severity": "critical",
        "phrases": ("not moving", "has not moved", "motionless",
                    "unresponsive"),
        "says": "you have not moved for a while",
        "reference": "CDC STEADI — older adult fall prevention",
    },
    "unsteady": {
        "sense": "sight",
        "severity": "guidance",
        "phrases": ("unsteady", "stumbling", "holding the wall", "swaying",
                    "staggering"),
        "says": "you looked unsteady on your feet",
        "reference": "CDC STEADI — gait, strength and balance",
    },
    # -- heard --------------------------------------------------------------
    "calling_for_help": {
        "sense": "sound",
        "severity": "critical",
        "phrases": ("help me", "call an ambulance", "i can't get up",
                    "i have fallen", "somebody help"),
        "says": "you called out for help",
        "reference": "NHS — when to call 999",
    },
    "slurred_speech": {
        "sense": "sound",
        "severity": "critical",
        # One of the three FAST signs. It is `critical` for the reason the
        # campaign exists: the window in which a stroke can be treated is
        # measured in hours, and the person having one is the least able to
        # judge that.
        "phrases": ("slurred", "slurring", "words are jumbled",
                    "cannot get the words out"),
        "says": "your speech sounded slurred",
        "reference": "NHS / CDC — FAST stroke signs",
    },
    "in_pain": {
        "sense": "sound",
        "severity": "guidance",
        "phrases": ("it hurts", "in pain", "my chest hurts", "groaning",
                    "crying out"),
        "says": "you sounded like you were in pain",
        "reference": "NHS — chest pain and when it is urgent",
    },
    "confusion": {
        "sense": "sound",
        "severity": "guidance",
        "phrases": ("does not know where", "doesn't know where", "confused",
                    "repeating the same question"),
        "says": "you sounded confused",
        "reference": "NHS / CDC — FAST stroke signs",
    },
    "distress": {
        "sense": "sound",
        "severity": "guidance",
        "phrases": ("crying", "sobbing", "panicking", "distressed"),
        "says": "you sounded distressed",
        "reference": "NHS — anxiety, fear and panic",
    },
}


def _senses_are_honest() -> list[str]:
    """Cues read out of a sense nothing on the roster has.

    A cue nothing can produce is a row that will never fire, and the failure
    is silent — it does not error, it simply never appears. Read by a guard
    rather than asserted at import so the failure arrives with a test name.
    """
    available = {s for m in monitors.MONITORS.values() for s in m.senses}
    return sorted(name for name, c in CUES.items()
                  if c["sense"] not in available)


def _severities_are_the_ladders() -> list[str]:
    """Cues carrying a severity the escalation ladder does not know.

    `jim/hazards.py` grades its rows `critical` / `warning` / `notice`, which
    is a perfectly good scale and is not this one. A cue graded in the wrong
    vocabulary would reach :func:`jim.escalation.decide` as an unknown word
    and be quietly treated as the mildest thing it could be.
    """
    return sorted(name for name, c in CUES.items()
                  if c["severity"] not in escalation._SEVERITY_BASE)


def for_monitor(monitor: str) -> list[str]:
    """The cues this monitor could ever yield, from what it can sense.

    Public because it is the honest thing for a screen to show beside the
    switch: *this one can notice you fell; it cannot hear you call out.*
    """
    spec = monitors.MONITORS[monitor]
    return sorted(name for name, c in CUES.items()
                  if c["sense"] in spec.senses)


def read(monitor: str, text: str) -> list[dict]:
    """Every cue this text indicates, worst first — and none this monitor
    could not have sensed.

    Deterministic, offline, and exactly as good as its table, which is the
    point: what it flags it can explain, and what it misses a person still
    can.
    """
    if monitor not in monitors.MONITORS:
        raise monitors.NoSuchMonitor("no such monitor")
    lowered = (text or "").lower()
    can = set(for_monitor(monitor))
    found = [{"cue": name, "sense": c["sense"], "severity": c["severity"],
              "says": c["says"], "reference": c["reference"]}
             for name, c in CUES.items()
             if name in can and any(p in lowered for p in c["phrases"])]
    found.sort(key=lambda c: -escalation._SEVERITY_BASE[c["severity"]])
    return found


def seen(user_id: str, monitor: str, text: str) -> list[dict]:
    """Read the cues in what a monitor just sensed, and record them.

    Called from :func:`jim.daybook.sensed` **before** the roster is asked
    whether any of the content may survive — which is the whole arrangement:
    noticing does not depend on keeping.

    Each cue is resolved through :func:`jim.escalation.decide` rather than
    through a second ladder of this module's own, and lands as a `detection`
    event in the vocabulary the rest of the product already reads. A
    `guidance` cue is therefore something :mod:`jim.noticed` will try to
    settle for nothing; a `critical` one is excluded from that pass by design
    and goes to a person.
    """
    from . import guardian

    found = read(monitor, text)
    if not found:
        return []
    user = guardian.get_user(user_id) or {}
    contact = bool(user.get("emergency_phone"))
    sensitivity = user.get("sensitivity") or "balanced"
    out = []
    for cue in found:
        decision = escalation.decide(
            cue["severity"], sensitivity,
            known=user.get("known_conditions") or [], contactable=contact)
        # The cue's name and the monitor that read it. Not the text: that is
        # a local in this function and there is nowhere in the row to put it,
        # which is what stops this module being the way round the roster.
        guardian._event(user_id, "detection", condition=cue["cue"],
                        severity=cue["severity"],
                        detail={"reason": cue["says"], "monitor": monitor,
                                "reference": cue["reference"],
                                "tier": decision["tier"]})
        out.append({**cue, "monitor": monitor, "tier": decision["tier"]})
    return out


def lately(user_id: str, limit: int = 20) -> list[dict]:
    """The cues read for this person, newest first.

    Off the `events` table rather than a table of its own: a cue **is** a
    detection, and a second store for them would be a second answer to *what
    has this guardian noticed* — which is the question `jim/underway.py` and
    the escalation ladder both already read from `events`.
    """
    import json
    rows = db.connect().execute(
        "SELECT * FROM events WHERE user_id=? AND type='detection'"
        " AND condition IN (%s)" % ",".join("?" * len(CUES))
        + " ORDER BY created_at DESC, rowid DESC LIMIT ?",
        (user_id, *CUES, limit)).fetchall()
    out = []
    for r in rows:
        detail = json.loads(r["detail"] or "{}")
        out.append({"cue": r["condition"], "severity": r["severity"],
                    "says": detail.get("reason", ""),
                    "monitor": detail.get("monitor", ""),
                    "reference": detail.get("reference", ""),
                    "tier": detail.get("tier", ""),
                    "at": r["created_at"]})
    return out
