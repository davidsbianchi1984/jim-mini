"""The task window: everything this guardian has running, in one place.

The field ask, said twice: *users will always have that task window — which
agent is running, which tasks are still running.*

    asked     which agent is running, and which tasks are still going
    mattered  can somebody see all of it without knowing where to look

Every piece of this was already answerable and none of it was answerable
together. :func:`jim.liaison.running` knew about links. The monitor roster
knew what was sensing. The mic knew whether channel 2 was open, the call
table knew whether a call was live, and the engagement table knew whether an
agent was mid-session. Five readers, five screens, and no answer to the only
question a person actually asks — *what is my guardian doing right now* —
which is the question you ask precisely when you do not already know where to
look.

## Why the gathering is here and not in each shell

Four clients, and each would otherwise decide for itself what counts as
running. That is four chances to disagree about whether a proposed-but-not-
agreed task keeps a link in the list, and the disagreement would be invisible
— every shell would look right on its own. The rule is written once here, and
the shells render what they are handed.

It is the opposite call from :class:`GuardianLights` on the console, which
composes its glance client-side from routes already open — and rightly, since
*is there an alarm* needs no judgement. This does: what counts as still
running is exactly the part worth stating once.

## What a row says, and what it is careful not to say

``kind`` and ``why`` are closed sets, so a client branches on them and says
them in the reader's own language. Prose is never composed here. The two text
fields are kept apart on purpose:

* ``term`` is one of this product's own vocabulary words — a monitor's name, a
  call's route — which a shell translates through the table it already has;
* ``words`` is what the **person** wrote, and is passed through untouched.
  Their task, what the conversation was about, the name they gave a device.

A row carrying English prose composed in this module would arrive in English
on a Portuguese screen, which is the failure the whole i18n mechanism exists
to prevent — and the one place it is easiest to reintroduce is a summary
endpoint like this one, where writing the sentence server-side feels helpful.

## What is running, and what merely happened

``running`` holds only what is still going. Errands are not in it: an errand
opens, studies and is finished before the call returns, so listing one as
running would be a lie told by a window whose whole job is to be believed
about that. What it did today is real and belongs to the same glance, so it
sits in ``today`` instead, beside the budget that bounds it.

Excursions have no row of their own for the same reason, one step further on:
an errand *is* an excursion with the reason it was worth paying for attached,
and a person reading two rows for one act would reasonably conclude their
guardian went out twice.

## What this window is not

It is a reader. Nothing here starts, stops or changes anything — every row
names the thing it came from so a shell can open the screen that already owns
that capability. A window over everything, that could also act on everything,
would quietly become the widest door in the product.
"""

from __future__ import annotations

from . import db, engaged, errands, liaison, mic, monitors, noticed, permits

#: How many of today's handled notices the window carries. A glance, not the
#: ledger — and a plain number rather than a budget borrowed from somewhere
#: else, because most of these cost nothing and no ceiling bounds them.
NOTICED_SHOWN = 5

#: The sorts of thing that can be running. A closed set: a client branches on
#: these to say them in the reader's language, and a new one cannot arrive
#: without somebody deciding what it is called on four shells.
KINDS = ("engaged", "liaison", "call", "listening", "monitor")

#: Why a row is still open, from the same closed set discipline. `agreed` and
#: `proposed` are the two states of a link's task and they are worth telling
#: apart on sight: only the first will survive the call.
WHYS = ("open", "agreed", "proposed", "announced", "not_announced", "on")


def _engaged(user_id: str) -> list[dict]:
    """The literal *which agent is running*. At most one, by construction —
    :func:`jim.engaged.current` returns the session with no sign-off."""
    now = engaged.current(user_id)
    if now is None:
        return []
    return [{"kind": "engaged", "id": now["id"], "term": now["area"],
             "words": None, "since": now["opened_at"], "why": "open"}]


def _liaisons(user_id: str) -> list[dict]:
    """Open links, and whether the task on one is actually holding it there.

    A task nobody has agreed to yet still shows — it is real work somebody
    proposed — but it reads `proposed`, because a person looking at this
    window to decide whether the link survives the call is owed the
    difference.
    """
    out = []
    for link in liaison.running(user_id):
        if not link["running"]:
            continue
        out.append({
            "kind": "liaison", "id": link["id"], "term": None,
            # Their own words either way: the task if there is one, otherwise
            # what they said the conversation was.
            "words": link["task"] or link["about"] or None,
            "since": link["opened_at"],
            "why": ("agreed" if link["holds_it_open"]
                    else "proposed" if link["task"] else "open"),
        })
    return out


def _calls(user_id: str) -> list[dict]:
    """Assisted calls still open.

    `not_announced` is not a footnote. A call in that state is one where the
    notice has not gone out, which is the one state in which nothing is
    allowed to listen — see :mod:`jim.oncall` — so a window that showed it
    the same as any other live call would be reporting listening that is not
    happening.
    """
    rows = db.connect().execute(
        "SELECT id, route, announced_at, opened_at FROM assisted_calls"
        " WHERE user_id=? AND ended_at IS NULL"
        " ORDER BY opened_at DESC, rowid DESC", (user_id,)).fetchall()
    return [{"kind": "call", "id": r["id"], "term": r["route"],
             "words": None, "since": r["opened_at"],
             "why": "announced" if r["announced_at"] else "not_announced"}
            for r in rows]


def _listening(user_id: str) -> list[dict]:
    """Channel 2, where it is open. The device name is the person's own."""
    state = mic.state(user_id)
    if not state["listening"]:
        return []
    return [{"kind": "listening", "id": None, "term": None,
             "words": state["device"], "since": state["since"],
             "why": "open"}]


def _monitors(user_id: str) -> list[dict]:
    """What is sensing. Off rows are left out — this window is what is
    running, and the roster is where the whole list lives.

    `why` carries the monitor's standing rather than the constant `"on"`
    it used to. A field report read this window against a house with
    nothing paired: "all showing sensing, but without actually being able
    to physically connect the device, JIM has no way to actually monitor
    what I have stored." The window was printing a permission as an
    activity — every switched-on row said `sensing`, whether or not
    anything had ever come from it.

        asked     is this monitor switched on
        mattered  has anything ever arrived from it

    A row that is waiting still belongs here: it is a thing this person
    switched on and is owed an answer about. What changes is the word.
    """
    return [{"kind": "monitor", "id": None, "term": m["name"],
             "words": m["device"] or None, "since": m["last_sensed"],
             "why": m["standing"]}
            for m in monitors.roster(user_id) if m["on"]]


def _errands_today(user_id: str) -> list[dict]:
    """What it went and learned on this person's behalf since midnight UTC.

    Asking the ledger for :data:`jim.errands.DAILY` rows is exactly enough,
    and not by luck: the budget is what makes it so. No more than ``DAILY``
    errands can open in a day, so the newest ``DAILY`` rows necessarily
    contain every one of today's. If that ceiling ever stops being enforced
    this slice stops being complete — which is the right coupling, since a
    window over an unbounded spend would have a worse problem than a short
    list.

    The same day boundary as :func:`jim.errands.spent_today`, spelled the
    same way, so the list and the count beside it cannot disagree about when
    today started.
    """
    today = db.utcnow()[:10]
    return [row for row in errands.ledger(user_id, limit=errands.DAILY)
            if row["opened_at"][:10] == today]


def _noticed_today(user_id: str) -> list[dict]:
    """What the coach noticed and something settled, since midnight UTC.

    Unbounded by a budget, unlike the errands beside it: most of these cost
    nothing, which is the entire point of the pass, so there is no ceiling to
    borrow as a slice size. :data:`NOTICED_SHOWN` is a glance's worth, and
    :func:`jim.noticed.ledger` remains the place that answers *everything it
    has ever handled*.
    """
    today = db.utcnow()[:10]
    return [row for row in noticed.ledger(user_id, limit=NOTICED_SHOWN)
            if row["noticed_at"][:10] == today]


def window(user_id: str) -> dict:
    """Everything running for this person, what it did today, and what is
    left to spend.

    ``quiet`` is derived rather than left to the reader. *Nothing is running*
    is a real answer to this question and the one a person most wants stated
    plainly; making four shells each work it out from an empty list is how
    one of them ends up showing a bare heading over nothing.
    """
    rows = (_engaged(user_id) + _liaisons(user_id) + _calls(user_id)
            + _listening(user_id) + _monitors(user_id))
    return {
        # `underway`, not `running`: this API already carries `running` as a
        # boolean on a link, and one wire name carries one type. The same
        # rule that made this list `running` in the first place is the rule
        # that says it cannot be.
        "underway": rows,
        "quiet": not rows,
        # What it did today, and the ceiling it did it under. Both, because a
        # person seeing nothing studied should be able to tell *there was
        # nothing worth studying* from *it has spent everything it may spend
        # today*.
        "today": _errands_today(user_id),
        # What it noticed and settled today, and which half settled it. The
        # errand list above says what it went and learned; this says what it
        # dealt with — and `settled_by` on each row is where the ladder stops
        # being a claim in a docstring and becomes a number on a screen.
        "handled": _noticed_today(user_id),
        # `spent_today` rather than `errands`, which the ledger already
        # carries as a list of them. Same name as the ledger's own count,
        # because it is the same number and one name should mean one thing in
        # both directions.
        #
        # It counts both unattended passes, because they share one ceiling —
        # so `permitted` here would be answering about only one of the two
        # switches that can spend it. Both are named.
        "spend": {"spent_today": errands.spent_today(user_id),
                  "daily": errands.DAILY,
                  "permitted": permits.granted(user_id, errands.PERMIT),
                  "handling_permitted": permits.granted(user_id,
                                                        noticed.PERMIT)},
    }
