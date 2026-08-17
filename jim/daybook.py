"""The day as it was actually taken in, and what survived of it.

The field ask, in its own words: *watches computer or phone screen all the
time, watch every meeting you're in, record every call, stream, etc., have
perfect accounting and context of your life.*

    asked     is the day captured
    mattered  does what survives match what was promised before it was switched on

:mod:`jim.monitors` built the consent for this and stopped at the door. The
roster says what may sense, who else it catches, and — in ``holds`` — what
stays behind. ``POST /monitors/{name}/sensed`` even existed, ran
:func:`jim.monitors.may_sense`, and returned ``{"sensing": true}`` without
recording a thing. The permission to capture the day had shipped; the capture
had not, and neither had the accounting.

## Perfect accounting, read the honest way

The phrase in the ask is *perfect accounting and context of your life*, and
there are two products behind it. One keeps everything it ever saw and calls
the pile a life. The other keeps a complete and truthful record of **what was
taken in and what survived**, which is the thing somebody can actually check.

This is the second. Every moment a monitor sensed leaves a row here whether or
not its content was kept, and a row that kept nothing says why in
``dropped_because``. A person can read back not just what their guardian
retained but what it declined to, and which promise made it decline. An
accounting that only listed what survived would be a record with its own
omissions edited out.

## The roster decides what is kept, and the caller never does

This is the load-bearing rule. Each monitor already carries a promise about
what stays behind — *nothing, it is a channel, not a recording*; *nothing
unless you switch keeping on*; *the readings, as your own history* — and those
sentences were written to be read by a person deciding whether to switch the
thing on.

So :func:`sensed` takes content from its caller and then asks
:data:`jim.monitors.Monitor.keeps` whether any of it may survive. A screen
monitor drops it, every time, whatever is passed and whatever anybody has
switched on, because that is what its row promised. There is no argument that
overrides this, and a test holds the absence of one: the moment a caller can
say *keep this anyway*, the roster stops being a promise and becomes a
default.

## Meetings, and the people in them who never chose this

A stretch is a run of the day with a monitor on it — a meeting, a call, a
working session. Opening one over a monitor that catches other people demands
the same claim :func:`jim.monitors.plug_in` demands, and for the same reason:
a hall camera has no far side to play a notice to, so somebody has to say, in
the record, that the people in that room were told. The claim is not proof.
Refusing to let it go unmade is what this can do.

That obligation is checked **again** here rather than trusted from the switch,
and the difference matters: switching a room speaker on for a quiet house is a
different decision from bringing four people into that room for an hour, and
consent given for the first is not consent for the second.

## What this is not

It is not a recorder. Nothing here captures audio, video or pixels; content is
whatever a caller hands over, and for most of the roster it is dropped on
arrival. Turning this into literal always-on recording of screens, calls and
meetings would need three things this round did not do and could not decide
alone: the roster's promises rewritten, somewhere to put the bytes that is not
this database (:mod:`jim.capture` already refuses to degrade to a local file
for exactly one photograph), and an answer to two-party consent law that a
checkbox is not.
"""

from __future__ import annotations

from . import db, monitors

#: Why a moment's content did not survive. Words rather than a flag, because
#: *this monitor never keeps anything* and *you have not switched keeping on*
#: are different things to read back — the first is the product's promise and
#: the second is a switch the person can go and change.
DROPPED = ("holds_nothing", "keeping_is_off", "nothing_to_keep", "forgotten")


class NotYours(RuntimeError):
    """Refused: that stretch belongs to somebody else."""


class NoSuchStretch(ValueError):
    """No stretch by that id."""


class NoSuchMoment(ValueError):
    """No moment by that id."""


def _may_keep(user_id: str, monitor: str) -> tuple[bool, str]:
    """Whether this monitor's content may survive, and why not when it may
    not.

    The roster is asked, never the caller. :data:`jim.monitors.KEEPS` is the
    promise as a rule: ``nothing`` refuses whatever anybody has switched on,
    ``if_kept`` defers to this person's own keeping switch, and ``always`` is
    a reading they asked to have in the first place.
    """
    spec = monitors.MONITORS[monitor]
    if spec.keeps == "nothing":
        return False, "holds_nothing"
    if spec.keeps == "always":
        return True, ""
    row = db.connect().execute(
        "SELECT keeping FROM monitors WHERE user_id=? AND monitor=?",
        (user_id, monitor)).fetchone()
    if row is not None and row["keeping"]:
        return True, ""
    return False, "keeping_is_off"


def sensed(user_id: str, monitor: str, content: str = "",
           stretch_id: str | None = None) -> dict:
    """One moment a monitor took something in.

    Goes through :func:`jim.monitors.may_sense` first — the one door, which
    refuses a monitor nobody switched on. What comes back says whether the
    content survived and, when it did not, which promise dropped it.

    Note what this signature does **not** have: any way for a caller to ask
    for content to be kept. The roster decides, and a keyword that overrode it
    would turn every promise in that table into a default.
    """
    monitors.may_sense(user_id, monitor)
    # A moment may only join a stretch of this person's own. Without this a
    # stranger could hand in moments against somebody else's meeting: their
    # content would stay their own — the row carries its own `user_id` — but
    # the meeting's counts would be inflated by somebody who was never in it,
    # and a record anybody can add to is not one its owner can rely on.
    if stretch_id:
        _mine(stretch_id, user_id)
    keep, because = _may_keep(user_id, monitor)
    body = (content or "").strip()
    if keep and not body:
        # Allowed to keep and given nothing: worth telling apart from a drop,
        # because *the promise stopped this* and *there was nothing there* are
        # not the same fact about the day.
        keep, because = False, "nothing_to_keep"
    moment_id = db.new_id("mom")
    conn = db.connect()
    conn.execute(
        "INSERT INTO day_moments (id, user_id, monitor, stretch_id, kept,"
        " content, dropped_because, sensed_at) VALUES (?,?,?,?,?,?,?,?)",
        (moment_id, user_id, monitor, stretch_id, int(keep),
         body if keep else "", "" if keep else because, db.utcnow()))
    conn.commit()
    return {"id": moment_id, "monitor": monitor, "kept": keep,
            "dropped_because": because, "stretch_id": stretch_id,
            # What the person was promised, handed back at the moment the
            # promise was applied. A screen that says "kept: false" is
            # information; one that also says why is an answer.
            "holds": monitors.MONITORS[monitor].holds}


def open_stretch(user_id: str, monitor: str, about: str = "",
                 others_told: bool = False) -> dict:
    """Begin a meeting, a call, or a working stretch on one monitor.

    The monitor must be switched on — the same door every moment goes
    through — and where it catches other people, somebody has to say they were
    told. Asked again here rather than inherited from the switch: consenting
    to a room speaker in an empty house is not consenting to it through an
    hour with four other people in the room.
    """
    monitors.may_sense(user_id, monitor)
    if monitors.MONITORS[monitor].catches_others and not others_told:
        raise monitors.NobodyTold(monitors.NOBODY_TOLD)
    stretch_id = db.new_id("str")
    conn = db.connect()
    conn.execute(
        "INSERT INTO day_stretches (id, user_id, monitor, about, others_told,"
        " opened_at) VALUES (?,?,?,?,?,?)",
        (stretch_id, user_id, monitor, about.strip(), int(others_told),
         db.utcnow()))
    conn.commit()
    return stretch(stretch_id, user_id)


def _row(stretch_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM day_stretches WHERE id=?", (stretch_id,)).fetchone()
    if row is None:
        raise NoSuchStretch("no such stretch")
    return dict(row)


def _mine(stretch_id: str, user_id: str) -> dict:
    row = _row(stretch_id)
    if row["user_id"] != user_id:
        raise NotYours("that stretch belongs to somebody else")
    return row


def close_stretch(user_id: str, stretch_id: str) -> dict:
    """End it. Closing twice is closing once — a meeting that ended does not
    end again, and a second press is a person making sure rather than an
    error."""
    row = _mine(stretch_id, user_id)
    if row["ended_at"] is None:
        conn = db.connect()
        conn.execute("UPDATE day_stretches SET ended_at=? WHERE id=?",
                     (db.utcnow(), stretch_id))
        conn.commit()
    return stretch(stretch_id, user_id)


def stretch(stretch_id: str, user_id: str) -> dict:
    row = _mine(stretch_id, user_id)
    counts = db.connect().execute(
        "SELECT COUNT(*) AS n, COALESCE(SUM(kept), 0) AS k FROM day_moments"
        " WHERE stretch_id=?", (stretch_id,)).fetchone()
    spec = monitors.MONITORS[row["monitor"]]
    return {"id": row["id"], "monitor": row["monitor"], "about": row["about"],
            "others_told": bool(row["others_told"]),
            "catches_others": spec.catches_others,
            "running": row["ended_at"] is None,
            "opened_at": row["opened_at"], "ended_at": row["ended_at"],
            "moments": counts["n"], "kept": counts["k"]}


def stretches(user_id: str, limit: int = 20) -> list[dict]:
    """This person's meetings and working stretches, open ones first."""
    rows = db.connect().execute(
        "SELECT id FROM day_stretches WHERE user_id=?"
        " ORDER BY ended_at IS NULL DESC, opened_at DESC, rowid DESC LIMIT ?",
        (user_id, limit)).fetchall()
    return [stretch(r["id"], user_id) for r in rows]


def day(user_id: str, on: str | None = None) -> dict:
    """The accounting for one day: what was sensed, and what survived.

    ``on`` is a date as ``YYYY-MM-DD``; today by default. Per monitor rather
    than one long list, because *the screen noticed four hundred things and
    kept none of them* is the shape of an ordinary working day and four
    hundred rows is not a thing anybody reads.
    """
    on = on or db.utcnow()[:10]
    rows = db.connect().execute(
        "SELECT monitor, kept, dropped_because, COUNT(*) AS n"
        " FROM day_moments WHERE user_id=? AND substr(sensed_at, 1, 10)=?"
        " GROUP BY monitor, kept, dropped_because"
        " ORDER BY monitor", (user_id, on)).fetchall()
    per: dict[str, dict] = {}
    for r in rows:
        entry = per.setdefault(r["monitor"], {
            "monitor": r["monitor"], "sensed": 0, "kept": 0, "dropped": 0,
            # Every reason that dropped something on this monitor today. A
            # list because one monitor can drop for two different reasons on
            # the same day — keeping switched off in the morning and on by
            # the afternoon is an ordinary thing to do.
            "because": [],
            "holds": monitors.MONITORS[r["monitor"]].holds,
        })
        entry["sensed"] += r["n"]
        if r["kept"]:
            entry["kept"] += r["n"]
        else:
            entry["dropped"] += r["n"]
            if r["dropped_because"] not in entry["because"]:
                entry["because"].append(r["dropped_because"])
    monitors_today = sorted(per.values(), key=lambda e: e["monitor"])
    return {
        # `date`, not `on`: the monitor roster already carries `on` as a
        # boolean saying whether a monitor is switched on, and one wire name
        # carries one type.
        "date": on,
        "monitors": monitors_today,
        "sensed": sum(e["sensed"] for e in monitors_today),
        "kept": sum(e["kept"] for e in monitors_today),
        # Stated rather than left to be inferred from an empty list, for the
        # same reason the task window states `quiet`: *nothing was sensed* is
        # a real answer and four shells should not each derive it.
        "quiet": not monitors_today,
    }


def kept(user_id: str, limit: int = 50) -> list[dict]:
    """The moments whose content actually survived, newest first.

    Deliberately separate from :func:`day`, which counts. This is the shorter
    list by construction and the one worth reading — and on an ordinary day,
    on an ordinary roster, most of what was sensed is not in it.
    """
    return [{"id": r["id"], "monitor": r["monitor"], "content": r["content"],
             "stretch_id": r["stretch_id"], "sensed_at": r["sensed_at"]}
            for r in db.connect().execute(
                "SELECT * FROM day_moments WHERE user_id=? AND kept=1"
                " ORDER BY sensed_at DESC, rowid DESC LIMIT ?",
                (user_id, limit)).fetchall()]


def forget(user_id: str, moment_id: str) -> dict:
    """Drop what was kept of one moment, keeping the fact that it happened.

    The row stays and the content goes, which is the shape the accounting
    needs: deleting the row outright would leave a day that reads as though
    the monitor never sensed at all, and a record that quietly loses its own
    entries is the thing this module exists not to be.
    """
    conn = db.connect()
    row = conn.execute(
        "SELECT id FROM day_moments WHERE id=? AND user_id=?",
        (moment_id, user_id)).fetchone()
    if row is None:
        raise NoSuchMoment("no such moment")
    conn.execute(
        "UPDATE day_moments SET kept=0, content='', dropped_because='forgotten'"
        " WHERE id=?", (moment_id,))
    conn.commit()
    return {"id": moment_id, "kept": False, "dropped_because": "forgotten"}
