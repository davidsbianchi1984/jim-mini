"""Two guardians talking to each other, quietly, on behalf of two people.

The field ask, in its own words: *both parties have profiles and both could be
using them simultaneously, and then those two collaborate together — capable of
collaborating silently in the background. They may not be able to share
information through the line like the users can with their voice, but they know
both parties' IDs, and can reach out to each other in other ways than the
phone, via online.*

So: the line carries human voice, and the guardians talk over the network. That
also means none of this needs a phone — the same link serves two people in a
room, on a video call, or in a thread.

    asked     can two guardians work together
    mattered  is each one still working for its own person

## It forms only where both sides already knew each other

:func:`jim.circle._mutual` is the gate, and it is exactly right for this: an
invitation is one direction, two directions make contacts, and either side
deleting theirs closes the door for both. Each guardian recognises the other
from a record its own person already holds, so nobody has to publish a
directory and nobody can be reached by a stranger who happens to have their
number. One-sided contact reaches nothing, which is the whole point — the
alternative is a stranger's agent calling yours.

## Silent, and readable afterwards by the person it works for

The exchange is never spoken on the line and neither person hears it happen.
That is the ask, and it is also where a guardian could quietly stop being
yours: two agents negotiating on a channel neither human can inspect are two
principals with counsel who never report back.

So the link keeps **both halves, split by side**. :func:`half` gives a person
what *their* guardian said and what it was told — not the other person's
private half, which was never theirs to read. A person on a wage call can see
afterwards precisely what their own agent disclosed.

## It lives as long as the work does

The link opens with the call and closes with it. What extends it is not an
agreement to stay connected — it is a **task**: something that came out of the
conversation and has to be finished. The task is the reason the link is still
open, both people can see it in the same place they see everything else
running, and closing it closes the link.

That is a better rule than a standing connection because it has an end in it.
Two guardians that met during one conversation and stayed in touch afterwards
is a different product from two that had a job to finish, and only one of them
is what anybody would assume from *they collaborated on the call*.

## What it may say is bounded by what its person allowed

A link is a channel, not a mandate. What a guardian may disclose about its own
person across it is the ``speak_for_you`` permit and nothing wider — `asked`
rather than assumed, because this is the one surface where somebody else's
guardian is on the other end of the sentence.
"""

from __future__ import annotations

from . import circle, db, i18n, permits

#: The permit a guardian needs before it may say anything about its person to
#: another guardian. Named here rather than passed in, so a caller cannot hand
#: it a different one.
PERMIT = "speak_for_you"

#: Why a link ended. Kept as words rather than a flag because *the call ended*
#: and *somebody stopped it* are different things to read months later.
ENDINGS = ("call_ended", "task_done", "stopped", "contact_left")


class NotAllowed(RuntimeError):
    """Refused: this person has not let their guardian speak for them."""


#: The permit's refusal, in the sentence a person reads.
NOT_ALLOWED = ("your guardian has not been allowed to speak for you to "
               "somebody else's — turn it on in what it may do for you, "
               "where it says what it may say")


class NotMutual(RuntimeError):
    """Refused: these two are not each other's contacts."""


class NoSuchLink(ValueError):
    """No link by that id."""


class NotYours(RuntimeError):
    """Refused: that link does not belong to this person."""


#: Refused because only one side has the other stored. Its own sentence
#: because it is the rule this module is built on, not an incidental check.
NOT_MUTUAL = ("these two are not each other's contacts — a guardian only "
              "reaches another when both people already had the other, and "
              "one side alone reaches nothing")


def open(user_id: str, other_id: str, about: str = "") -> dict:
    """Open a link between this person's guardian and another's.

    ``about`` is what the conversation is, in the person's own words. It is
    not a task yet: a link with no task closes when the call does.
    """
    if not circle._mutual(user_id, other_id):
        raise NotMutual(NOT_MUTUAL)
    if not permits.granted(user_id, PERMIT):
        raise NotAllowed(NOT_ALLOWED)
    link_id = db.new_id("lnk")
    conn = db.connect()
    conn.execute(
        "INSERT INTO liaisons (id, low_id, high_id, about, task, opened_at)"
        " VALUES (?,?,?,?,'',?)",
        (link_id, min(user_id, other_id), max(user_id, other_id), about,
         db.utcnow()))
    conn.commit()
    return summary(link_id, user_id)


def _row(link_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM liaisons WHERE id=?", (link_id,)).fetchone()
    if row is None:
        raise NoSuchLink("no such link")
    return dict(row)


def _mine(link_id: str, user_id: str) -> dict:
    row = _row(link_id)
    if user_id not in (row["low_id"], row["high_id"]):
        raise NotYours("that link is between two other people")
    return row


def say(link_id: str, user_id: str, what: str) -> dict:
    """One guardian tells the other something, on its person's behalf.

    Recorded against the side that said it, because the whole value of
    reading this back is knowing which guardian disclosed what.
    """
    row = _mine(link_id, user_id)
    if row["ended_at"]:
        raise NoSuchLink("that link has closed")
    if not permits.granted(user_id, PERMIT):
        raise NotAllowed(NOT_ALLOWED)
    conn = db.connect()
    conn.execute(
        "INSERT INTO liaison_lines (id, link_id, said_by, body, said_at)"
        " VALUES (?,?,?,?,?)",
        (db.new_id("lln"), link_id, user_id, what, db.utcnow()))
    conn.commit()
    return {"link_id": link_id, "said": what}


def half(link_id: str, user_id: str) -> dict:
    """What this person's own guardian said, and what it was told.

    Their half, not the other person's. *What my agent disclosed* is a thing
    somebody is entitled to; *what yours told mine in confidence* is not
    theirs to read, and a link that showed both would be a link neither
    person could use honestly.
    """
    row = _mine(link_id, user_id)
    lines = db.connect().execute(
        "SELECT * FROM liaison_lines WHERE link_id=? ORDER BY said_at, rowid",
        (link_id,)).fetchall()
    return {
        "link_id": link_id, "about": row["about"], "task": row["task"],
        "running": row["ended_at"] is None,
        "ended_because": row["ended_because"],
        "said_by_mine": [r["body"] for r in lines if r["said_by"] == user_id],
        "said_to_mine": [r["body"] for r in lines if r["said_by"] != user_id],
    }


def take_on(link_id: str, user_id: str, task: str) -> dict:
    """Name the work that came out of the conversation.

    This is what outlives the call. A link with a task on it survives the
    call ending; a link without one does not, and that is the difference
    between two guardians that had a job to finish and two that stayed in
    touch.
    """
    _mine(link_id, user_id)
    if not task.strip():
        raise NoSuchLink("say what the task is, in one line")
    conn = db.connect()
    conn.execute("UPDATE liaisons SET task=? WHERE id=? AND ended_at IS NULL",
                 (task.strip(), link_id))
    conn.commit()
    return summary(link_id, user_id)


def close(link_id: str, user_id: str, why: str = "call_ended") -> dict:
    """End it. A link with an unfinished task survives the call ending.

    The one exception is a person stopping it, which is why ``why`` is
    checked rather than trusted: *the call ended* must not be able to close
    something the task is holding open, and *somebody stopped it* always can.
    """
    row = _mine(link_id, user_id)
    if row["ended_at"]:
        return summary(link_id, user_id)
    if why == "call_ended" and row["task"]:
        return summary(link_id, user_id)
    conn = db.connect()
    conn.execute(
        "UPDATE liaisons SET ended_at=?, ended_because=? WHERE id=?",
        (db.utcnow(), why if why in ENDINGS else "stopped", link_id))
    conn.commit()
    return summary(link_id, user_id)


def summary(link_id: str, user_id: str) -> dict:
    row = _mine(link_id, user_id)
    other = row["high_id"] if row["low_id"] == user_id else row["low_id"]
    return {"id": row["id"], "with": other, "about": row["about"],
            "task": row["task"], "running": row["ended_at"] is None,
            "ended_because": row["ended_because"],
            "opened_at": row["opened_at"]}


def running(user_id: str) -> list[dict]:
    """Every link of this person's, open ones first.

    The answer to *which of these is still going, and why* — which is the
    question the task window asks about everything else this product runs.
    A closed link stays: what two guardians did on somebody's behalf is not
    something to tidy away.

    `running`, not `open`: this API already carries `open` as a list of
    unanswered follow-ups, and one wire name carries one type.
    """
    rows = db.connect().execute(
        "SELECT * FROM liaisons WHERE low_id=? OR high_id=?"
        " ORDER BY ended_at IS NULL DESC, opened_at DESC, rowid DESC",
        (user_id, user_id)).fetchall()
    return [summary(r["id"], user_id) for r in rows]
