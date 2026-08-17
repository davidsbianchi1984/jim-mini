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

## It lives as long as the work does, and only if both said so

The link opens with the call and closes with it. What extends it is not an
agreement to stay connected — it is a **task**: something that came out of the
conversation and has to be finished. The task is the reason the link is still
open, both people can see it in the same place they see everything else
running (:mod:`jim.underway`), and closing it closes the link.

That is a better rule than a standing connection because it has an end in it.
Two guardians that met during one conversation and stayed in touch afterwards
is a different product from two that had a job to finish, and only one of them
is what anybody would assume from *they collaborated on the call*.

**Both sides name it, or the call ends it.** The first version of this stored
the task in one column and let either person write it, which meant one person
could keep a channel to somebody else's guardian open past the conversation
that justified it, on their own say-so. That is the same shape as the
one-sided contact this module refuses at :func:`open` — and refusing a
stranger at the door while letting one party extend the stay unilaterally is
the door mattering less than it looks.

So agreement is recorded per side, against the **wording**:
:func:`take_on` proposes a task and counts as the proposer's own yes;
:func:`agree` is the other side's. Only when both are present does the link
outlive the call. Re-wording it drops the other side's agreement, because
agreeing to *book the venue* is not agreeing to *run the wedding*.

A task nobody has agreed to is not lost — it stays on the link and can be
agreed to later. It simply does not hold anything open in the meantime, which
is the honest state: one person has proposed some work and the other has not
yet said yes.

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


class Closed(NoSuchLink):
    """Refused: that link has ended.

    Its own type so every route answers a closed link the same way. It began
    as one: `say` raised `NoSuchLink` for it and answered 404, and when
    `take_on` and `agree` gained the same check they inherited their route's
    422 — the status for *you did not say what the task is*, which is a
    different thing entirely. A reader cannot tell those apart from the
    status, and the status is what they have.

    A subclass rather than a new exception, so `except NoSuchLink` on any
    route that has not been taught the difference still catches it.
    """


class NotYours(RuntimeError):
    """Refused: that link does not belong to this person."""


#: Refused because only one side has the other stored. Its own sentence
#: because it is the rule this module is built on, not an incidental check.
NOT_MUTUAL = ("these two are not each other's contacts — a guardian only "
              "reaches another when both people already had the other, and "
              "one side alone reaches nothing")

#: Asked to agree to a task on a link that has none. Its own sentence rather
#: than a bare 404, because *there is nothing here to agree to* and *that
#: link is gone* are different things to be told.
NOTHING_TO_AGREE = ("there is no task on this link yet — one side names the "
                    "work first, and the other agrees to it")


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
        raise Closed("that link has closed")
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
        "link_id": link_id, "about": row["about"],
        "running": row["ended_at"] is None,
        "ended_because": row["ended_because"],
        "said_by_mine": [r["body"] for r in lines if r["said_by"] == user_id],
        "said_to_mine": [r["body"] for r in lines if r["said_by"] != user_id],
        **_standing(row, user_id),
    }


def _agreed_to(link_id: str, task: str) -> set[str]:
    """Who has said yes to this exact wording.

    Matched on the wording rather than on the link alone, so re-wording the
    task drops the other side's agreement without anybody having to remember
    to clear it.
    """
    if not task:
        return set()
    return {r["user_id"] for r in db.connect().execute(
        "SELECT user_id FROM liaison_task_agreed WHERE link_id=? AND task=?",
        (link_id, task)).fetchall()}


def _both_agreed(row: dict) -> bool:
    """Whether the task on this row is holding the link open.

    Both sides, against the current wording. One person cannot reach this on
    their own, which is the whole point of the table it reads.
    """
    agreed = _agreed_to(row["id"], row["task"])
    return bool(row["task"]) and {row["low_id"], row["high_id"]} <= agreed


def _record_agreement(link_id: str, user_id: str, task: str) -> None:
    """This side says yes to this wording. Idempotent — saying yes twice is
    saying yes."""
    conn = db.connect()
    conn.execute(
        "INSERT OR REPLACE INTO liaison_task_agreed (link_id, user_id, task,"
        " agreed_at) VALUES (?,?,?,?)",
        (link_id, user_id, task, db.utcnow()))
    conn.commit()


def take_on(link_id: str, user_id: str, task: str) -> dict:
    """Name the work that came out of the conversation, and say yes to it.

    Proposing is this side's own agreement — nobody has to name a task and
    then separately approve their own wording. What it is *not* is the other
    side's: until :func:`agree` records theirs, the task sits on the link
    holding nothing open, and the call ending still closes it.

    Re-wording replaces the task and drops the other side's agreement, since
    what they said yes to is no longer what the link says.
    """
    row = _mine(link_id, user_id)
    if row["ended_at"]:
        raise Closed("that link has closed")
    if not task.strip():
        raise NoSuchLink("say what the task is, in one line")
    conn = db.connect()
    conn.execute("UPDATE liaisons SET task=? WHERE id=? AND ended_at IS NULL",
                 (task.strip(), link_id))
    conn.commit()
    _record_agreement(link_id, user_id, task.strip())
    return summary(link_id, user_id)


def agree(link_id: str, user_id: str) -> dict:
    """The other side says yes to the task as it currently stands.

    Deliberately takes no wording. A second party who could pass their own
    text would be proposing rather than agreeing, and the two sides could
    hold a link open on the strength of two different sentences that only
    looked like one agreement.
    """
    row = _mine(link_id, user_id)
    if row["ended_at"]:
        raise Closed("that link has closed")
    if not row["task"]:
        raise NoSuchLink(NOTHING_TO_AGREE)
    _record_agreement(link_id, user_id, row["task"])
    return summary(link_id, user_id)


def close(link_id: str, user_id: str, why: str = "call_ended") -> dict:
    """End it. A link with an agreed, unfinished task survives the call.

    The one exception is a person stopping it, which is why ``why`` is
    checked rather than trusted: *the call ended* must not be able to close
    something the task is holding open, and *somebody stopped it* always can
    — either side, alone. Ending a link needs one person; extending one needs
    both, and that asymmetry is deliberate in both directions.
    """
    row = _mine(link_id, user_id)
    if row["ended_at"]:
        return summary(link_id, user_id)
    if why == "call_ended" and row["task"] and _both_agreed(row):
        return summary(link_id, user_id)
    conn = db.connect()
    conn.execute(
        "UPDATE liaisons SET ended_at=?, ended_because=? WHERE id=?",
        (db.utcnow(), why if why in ENDINGS else "stopped", link_id))
    conn.commit()
    return summary(link_id, user_id)


def _standing(row: dict, user_id: str) -> dict:
    """Where the task has got to, from this person's side.

    Three separate answers rather than one flag, because *you have not
    agreed*, *they have not* and *nobody named anything* are three different
    things for a screen to say, and a single boolean would make a client
    guess which one it was looking at.
    """
    agreed = _agreed_to(row["id"], row["task"])
    other = row["high_id"] if row["low_id"] == user_id else row["low_id"]
    mine, theirs = user_id in agreed, other in agreed
    return {"task": row["task"],
            "you_agreed": mine,
            "they_agreed": theirs,
            # What the person actually wants to know: is this task the reason
            # the link will still be here after the call. Read off the set
            # already fetched rather than through `_both_agreed`, which would
            # ask the same question of the database a second time — and
            # `running()` builds one of these per link, on every poll of the
            # task window.
            "holds_it_open": bool(row["task"]) and mine and theirs}


def summary(link_id: str, user_id: str) -> dict:
    row = _mine(link_id, user_id)
    other = row["high_id"] if row["low_id"] == user_id else row["low_id"]
    return {"id": row["id"], "with": other, "about": row["about"],
            "running": row["ended_at"] is None,
            "ended_because": row["ended_because"],
            "opened_at": row["opened_at"], **_standing(row, user_id)}


def running(user_id: str) -> list[dict]:
    """Every link of this person's, open ones first.

    The answer to *which of these is still going, and why* — which is the
    question :mod:`jim.underway` asks about everything else this product runs,
    and takes the links half of its answer from here. A closed link stays:
    what two guardians did on somebody's behalf is not something to tidy
    away.

    `running`, not `open`: this API already carries `open` as a list of
    unanswered follow-ups, and one wire name carries one type.
    """
    rows = db.connect().execute(
        "SELECT * FROM liaisons WHERE low_id=? OR high_id=?"
        " ORDER BY ended_at IS NULL DESC, opened_at DESC, rowid DESC",
        (user_id, user_id)).fetchall()
    return [summary(r["id"], user_id) for r in rows]
