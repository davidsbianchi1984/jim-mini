"""What may watch, through what, and who else it catches.

The field ask, in its own words: *cameras, speakers, screens, monitors capable
of monitoring, any type of wearables or stationary systems that can connect to
the human body, always on, always there — and somewhere to plug all of these
remote features and components in.*

This is that place. Three tables already exist and none of them answers this:
``devices`` says what is registered, ``sources`` says which categories of data
the guardian may read, and :data:`jim.mic.MIC_TYPES` says whether a microphone
is worn or pointed at a room. What was missing is the sentence a person
actually needs before switching one on —

    asked     can this device sense me
    mattered  who else does it sense, and what does it keep

## Three things every row says

**senses** — what it can actually perceive: sound, sight, vitals, a screen, a
presence in a room, a signal off the body. Not the product's name for the
device; what it takes in.

**catches_others** — whether it perceives people who never chose it. A wrist
strap reads one pulse. A hall camera sees whoever walks through the hall, and
a kitchen speaker hears whoever is in the kitchen. This is a field rather than
a paragraph because it has to be checkable: **nothing that catches others is
ever on by default**, and a guard reads the table rather than trusting anybody
to have read it.

**holds** — what stays behind afterwards. "It notices you fell" and "it keeps
the video of you falling" are different agreements, and only one of them is
what the code does. A row that keeps nothing says so.

## The obligation follows the sense, not the device

:mod:`jim.oncall` settled the shape for a phone call: where the far side's
voice is in the room, the far side is told before anything listens. The same
rule holds here and is harder, because a hall camera has no far side to play a
notice to — so the honest primitive is that a monitor which catches others
cannot simply be switched on. Somebody has to say, in the record, that the
people in that space have been told. That claim is not proof, and this module
does not pretend it is: what it does is refuse to let the claim go unmade.

## Always-on is a property, not a default

The ask is for something always there, and that is a good product. It is not a
reason for a switch to arrive already flipped. A person who turns a hall
camera on has decided; a person who finds one already on has been decided
about, and no amount of usefulness afterwards converts the second into the
first.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import db, i18n

#: What a monitor can take in. Named rather than free text so a client can
#: group by it and a new one cannot arrive without a decision.
SENSES = ("sound", "sight", "vitals", "screen", "presence", "signal")

#: Where a monitor sits, which is what decides who else it reaches.
PLACINGS = ("worn", "held", "stationary", "on_body", "on_screen")


#: What may survive of what a monitor took in, as a rule the code can follow.
#:
#: ``holds`` is the same promise in the person's own words, and until 0.84.0
#: it was the only form of it — which meant the promise was readable and not
#: checkable. :mod:`jim.daybook` needed to obey it, and obeying an English
#: sentence means parsing one; the first draft of that did
#: ``holds.startswith("nothing")`` and would have quietly started keeping
#: screen content the day somebody rewrote the sentence to begin *"Nothing"*.
#:
#: So the promise is a field, the sentence stays, and
#: :func:`_keeping_is_honest` holds the two together.
KEEPS = (
    "nothing",   # never the content, whatever anybody switches on
    "if_kept",   # only where this person has switched keeping on
    "always",    # it is their own history — readings they asked to have
)


@dataclass(frozen=True)
class Monitor:
    """One thing that can be plugged in and sense somebody."""

    name: str
    senses: tuple[str, ...]
    placing: str
    says: str                       # what it does, in the person's words
    holds: str = ""                 # what stays behind; empty means nothing
    keeps: str = "nothing"          # the same promise, as a rule (see KEEPS)
    catches_others: bool = False    # does it sense people who never chose it
    default: bool = False


#: Everything that can be plugged in. Adding a row is a decision made here,
#: beside what it senses and who else it reaches, rather than a string that
#: quietly becomes load-bearing somewhere else.
MONITORS: dict[str, Monitor] = {m.name: m for m in (
    # -- worn, and pointed at one person ----------------------------------
    Monitor("wrist", ("vitals",), "worn",
            says="read your pulse, your sleep and your movement from a watch "
                 "or band",
            holds="the readings, as your own history", keeps="always"),
    Monitor("ring", ("vitals",), "worn",
            says="read your pulse and your sleep from a ring",
            holds="the readings, as your own history", keeps="always"),
    Monitor("patch", ("vitals", "signal"), "on_body",
            says="read what a stuck-on or implanted sensor reports",
            holds="the readings, as your own history", keeps="always"),
    Monitor("earpiece", ("sound",), "worn",
            says="hear you, and answer where only you can hear it",
            holds="nothing — it is a channel, not a recording",
            keeps="nothing"),
    Monitor("glasses", ("sound", "sight"), "worn",
            says="see and hear what you are looking at",
            holds="nothing unless you keep something", keeps="if_kept",
            # Worn, and still pointed outward at whoever is in front of you.
            catches_others=True),

    # -- a screen somebody is working at -----------------------------------
    Monitor("screen", ("screen",), "on_screen",
            says="see what is on your screen while you work",
            holds="nothing — what it notices is offered and dropped",
            keeps="nothing"),

    # -- stationary, and pointed at a room ---------------------------------
    Monitor("room_camera", ("sight", "presence"), "stationary",
            says="see the room — that you are up, that you fell, that you did "
                 "not come back",
            holds="nothing unless you switch keeping on", keeps="if_kept",
            catches_others=True),
    Monitor("room_speaker", ("sound", "presence"), "stationary",
            says="hear the room, and speak into it",
            holds="nothing unless you switch keeping on", keeps="if_kept",
            catches_others=True),
    Monitor("doorway", ("presence",), "stationary",
            says="notice somebody passing, without seeing or hearing them",
            # The times are the moment rows themselves. Nothing of what it
            # perceived is content, so it keeps none.
            holds="the times, and nothing else", keeps="nothing",
            catches_others=True),
    Monitor("bed", ("vitals", "presence"), "stationary",
            # The reviewer's wording: say who it notices, not where the
            # strip is installed. The id stays `bed` — records point at it.
            says="read the breathing and movement of someone in the house",
            holds="the readings, as your own history", keeps="always",
            # A second person in the bed is read by the same strip.
            catches_others=True),
)}


class NotPluggedIn(RuntimeError):
    """Refused: this monitor is not switched on for this person."""


class NobodyTold(RuntimeError):
    """Refused: it catches other people and nobody has said they were told."""


class NoSuchMonitor(ValueError):
    """No monitor by that name."""


def _defaults_are_honest() -> list[str]:
    """Rows whose default contradicts who they reach.

    Read by a guard rather than asserted at import, so the failure arrives
    with a test name that says what went wrong. Anything that senses people
    who did not choose it is off until somebody turns it on.
    """
    return sorted(m.name for m in MONITORS.values()
                  if m.default and m.catches_others)


def _keeping_is_honest() -> list[str]:
    """Rows where the promise in words and the rule in code disagree.

    ``holds`` is what a person reads before switching a monitor on; ``keeps``
    is what :mod:`jim.daybook` actually obeys. Two spellings of one promise is
    two places for it to drift, and the drift would be silent in the direction
    that matters — a sentence saying *nothing* over code that kept everything.

    Two checks, both exact rather than clever:

    * a row whose sentence opens with *nothing* must not keep content
      unconditionally;
    * a row that keeps only when somebody switches keeping on must say so with
      an *unless*, and a row that says *unless* must be that kind of row.
    """
    wrong = []
    for m in MONITORS.values():
        opens_with_nothing = m.holds.lower().startswith("nothing")
        conditional = "unless" in m.holds.lower()
        if opens_with_nothing and m.keeps == "always":
            wrong.append(m.name)
        elif conditional != (m.keeps == "if_kept"):
            wrong.append(m.name)
    return sorted(wrong)


def _placings_are_honest() -> list[str]:
    """Rows filed somewhere their reach does not fit.

    A stationary thing hears or sees a room, whatever the marketing calls it —
    `jim/mic.py` settled that for microphones and it holds for everything
    else. So a stationary monitor that claims to catch nobody is a row
    somebody has mis-declared, and this is what says so.
    """
    return sorted(m.name for m in MONITORS.values()
                  if m.placing == "stationary" and not m.catches_others)


def roster(user_id: str) -> list[dict]:
    """Every monitor, what it senses, who else it reaches, and whether it is
    on for this person.

    The whole list every time, off rows included. A roster that shows only
    what somebody already switched on is a roster nobody can add to.
    """
    rows = {r["monitor"]: r for r in db.connect().execute(
        "SELECT * FROM monitors WHERE user_id=?", (user_id,)).fetchall()}
    out = []
    for m in MONITORS.values():
        row = rows.get(m.name)
        out.append({
            "name": m.name, "senses": list(m.senses), "placing": m.placing,
            # `holds` is the promise in words; `keeps` is the same promise as
            # the rule `jim/daybook.py` obeys. Both travel, so a screen can
            # show the sentence and branch on the rule.
            "says": m.says, "holds": m.holds, "keeps": m.keeps,
            "catches_others": m.catches_others,
            "on": bool(row["switched_on"]) if row else m.default,
            "device": row["device_name"] if row else None,
            "others_told": bool(row["others_told"]) if row else False,
            "keeping": bool(row["keeping"]) if row else False,
        })
    return out


def plug_in(user_id: str, name: str, device_name: str = "",
            others_told: bool = False, keeping: bool = False) -> list[dict]:
    """Switch one on for this person, and get the whole roster back.

    ``others_told`` is the claim that the people in that space know. It is
    required for anything that catches them and it is stored as what it is —
    somebody's assertion, with a time on it — rather than dressed up as
    consent this product collected. What it prevents is a hall camera going
    on with nobody having thought about the hall.
    """
    monitor = MONITORS.get(name)
    if monitor is None:
        raise NoSuchMonitor(i18n.fill(i18n.MUST_BE_ONE_OF, field="monitor",
                                      choices=",".join(sorted(MONITORS))))
    if monitor.catches_others and not others_told:
        raise NobodyTold(NOBODY_TOLD)
    conn = db.connect()
    conn.execute(
        "INSERT INTO monitors (user_id, monitor, device_name, switched_on,"
        " others_told, keeping, decided_at) VALUES (?,?,?,1,?,?,?)"
        " ON CONFLICT (user_id, monitor) DO UPDATE SET switched_on=1,"
        " device_name=excluded.device_name, others_told=excluded.others_told,"
        " keeping=excluded.keeping, decided_at=excluded.decided_at",
        (user_id, name, device_name, int(others_told), int(keeping),
         db.utcnow()))
    conn.commit()
    return roster(user_id)


def unplug(user_id: str, name: str) -> list[dict]:
    """Switch one off. The row stays, carrying the decision and its time."""
    if name not in MONITORS:
        raise NoSuchMonitor(i18n.fill(i18n.MUST_BE_ONE_OF, field="monitor",
                                      choices=",".join(sorted(MONITORS))))
    conn = db.connect()
    conn.execute(
        "INSERT INTO monitors (user_id, monitor, device_name, switched_on,"
        " others_told, keeping, decided_at) VALUES (?,?,'',0,0,0,?)"
        " ON CONFLICT (user_id, monitor) DO UPDATE SET switched_on=0,"
        " decided_at=excluded.decided_at", (user_id, name, db.utcnow()))
    conn.commit()
    return roster(user_id)


def switched_on(user_id: str, name: str) -> bool:
    row = db.connect().execute(
        "SELECT switched_on FROM monitors WHERE user_id=? AND monitor=?",
        (user_id, name)).fetchone()
    if row is not None:
        return bool(row["switched_on"])
    monitor = MONITORS.get(name)
    return bool(monitor and monitor.default)


def may_sense(user_id: str, name: str) -> None:
    """The chokepoint. Refuse unless this person switched this on.

    One function, so a monitor cannot be read by a path that forgot to ask —
    the argument :func:`jim.oncall.may_listen` makes for a call and
    :func:`jim.offline.allow` makes for a socket.
    """
    if switched_on(user_id, name):
        return
    monitor = MONITORS.get(name)
    if monitor is None:
        raise NoSuchMonitor(i18n.fill(i18n.MUST_BE_ONE_OF, field="monitor",
                                      choices=",".join(sorted(MONITORS))))
    raise NotPluggedIn(i18n.fill(i18n.MONITOR_NOT_ON,
                                 doing=i18n.Term(monitor.says)))


#: Refused because nobody has said the room knows. Kept as a constant so the
#: sentence is translated once and raised from one place.
NOBODY_TOLD = ("this one senses people who did not choose it — say that the "
               "people in that space have been told before switching it on")
