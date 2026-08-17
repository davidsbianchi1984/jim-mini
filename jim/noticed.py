"""What the coach noticed, and when that is worth paying a turn to handle.

The field ask, in its own words: *for autonomous stuff throughout your day to
save tokens I want coach to be running most of those, and when something is
identified by coach, it could then start using tokens as Jim to better handle
the situation — not only that, Jim has much more tools and internet access.*

    asked     does the free half run the day and the paid half only what it cannot
    mattered  is the decision to spend made by something, and can it be read back

Half of that ladder already existed and shipped in 0.82.0.
:mod:`jim.errands` is the **knowledge** half: the offline coach writes down
what it could not answer, and a bounded unattended pass goes and studies it.
What had no path at all was the other half — a *situation*. The guardian
records detections all day (``events`` of type ``detection``), and nothing
ever decided that one of them warranted a paid turn. A gap became study; a
situation became a row in a table.

This module is that decision.

## The free half runs first, every time

Each notice is put to the offline stack before anything is bought — the same
:func:`jim.pipeline.run` that answers all day for nothing, over the curated
pack, what JIM learned on excursions and what earlier paid turns deposited. If
it settles the situation, the pass records that it did and **spends nothing**.

That ordering is the whole feature, not an optimisation in front of it. *The
coach runs most of these* is only true if the coach is actually asked first,
and a design that asked the model first and consulted the store afterwards
would produce the same answers at a price. It also gets better on its own: a
paid turn deposits what it learned, so a situation bought once is settled for
free the next time it happens. The ladder pays down its own bill.

## The decision to spend is bounded by the same ceiling as the other half

There are now two unattended passes that can cost money. Giving each its own
daily budget would mean the real ceiling is the sum of them, and
:mod:`jim.errands` already says why that is how a limit stops meaning
anything. So there is **one** ceiling — :data:`jim.errands.DAILY` — and
:func:`jim.errands.spent_today` counts both kinds against it. Study and
handling compete for the same day's spending, which is what a person means
when they ask what their guardian spent today.

The permit is its own, because the acts differ in the way that matters most:
**what leaves**. ``study_on_your_own`` sends a general topic out through the
sanitiser and brings knowledge back, and nothing about this person goes with
it. This one is the opposite shape. The situation is theirs, and it goes to a
model with the same context a coach turn carries — which is no wider than an
attended coach turn, and is emphatically not nothing.

That is why the permit sentence says so before anybody agrees to it, and why
these are two switches rather than one. Somebody may reasonably want a
guardian that studies on its own and does not put their day to a vendor's
model unattended; folding both into one yes would take that choice away.

## It advises. It does not act

The ask mentions JIM's tools. This pass does not use them, and that is a
decision rather than an omission: :mod:`jim.engaged` puts every acting tool
behind a session a person opened, with the reach shown at the door and an undo
trail on every act. An unattended pass that could act would be that whole
apparatus with the person taken out of it. What this produces is guidance,
recorded where the person reads it, and the store is better afterwards.

Acting unattended is a real thing somebody may want. It is a separate decision
and nobody has made it.

## Emergencies are not this pass's business

``critical`` detections are excluded — see :data:`HANDLES`. The escalation
ladder in :mod:`jim.escalation` already owns those and takes them to a person:
a contact, or emergency services. Putting a model turn in front of that path
would add latency to the one case where latency is the harm, and would make an
unattended generation the thing standing between somebody and an ambulance.

This pass is for the ordinary day. The ordinary day is what it was asked for.
"""

from __future__ import annotations

from . import db, errands, i18n, llm, permits, pipeline
from .guidance import _DENY

#: The severities this pass will touch. `critical` is deliberately absent and
#: a test holds it absent: that path belongs to :mod:`jim.escalation`, which
#: takes it to a human rather than to a model.
HANDLES = ("info", "guidance")

#: The permit this pass runs under. Named here rather than passed in, so a
#: caller cannot hand it a different one.
PERMIT = "handle_what_you_notice"

#: How the situation was settled, and by whom. The whole economic story of the
#: product is in this column: `coach` cost nothing, `jim` cost a turn.
SETTLED_BY = ("coach", "jim")

#: How many detections one pass will look at. A bound on the work, not on the
#: spending — the spending is bounded by the shared ceiling, and most of these
#: are settled for nothing.
LOOK_AT = 10


class NotPermitted(RuntimeError):
    """Refused: nobody said this account's guardian may handle what it
    notices."""


#: The permit's refusal, in the sentence a person reads. A constant so it is
#: translated once and raised from one place.
NOT_PERMITTED = ("this guardian has not been allowed to handle what it "
                 "notices on its own — turn it on in what it may do for you, "
                 "where it says what it looks at and what it does about it")


def _room_to_spend(user_id: str) -> bool:
    """Whether the day's shared ceiling has anything left.

    A question rather than a refusal, and that distinction is the whole
    shape of this pass. Running out of budget is not an error here: the free
    half is still worth running, and a version of this that raised would
    refuse to do the work that costs nothing because it could not do the work
    that costs. The first draft did exactly that, and a test that expected a
    429 is what showed it up.

    The ceiling takes no argument, for the reason :mod:`jim.errands` gives:
    every case for raising one for a single call is reasonable at the time,
    and the sum of them is why this kind of limit stops meaning anything.
    """
    return errands.spent_today(user_id) < errands.DAILY


def spent_today(user_id: str) -> int:
    """Paid turns this pass has opened since midnight UTC, from the ledger.

    Only rows the model actually answered. A notice the offline coach settled
    cost nothing and is not spending; a turn that degraded to the stub bought
    nothing and never became a row at all.
    """
    return db.connect().execute(
        "SELECT COUNT(*) AS n FROM notices WHERE user_id=? AND settled_by='jim'"
        " AND substr(noticed_at, 1, 10) = substr(?, 1, 10)",
        (user_id, db.utcnow())).fetchone()["n"]


def _in_words(condition: str) -> str:
    """The condition as something to put to the coach and to a model.

    The stored form is a key — `elevated_heart_rate` — and both the local
    store's keyword scoring and a model read words. This is not a sentence
    composed for a person to read: nothing here reaches a screen.
    """
    return (condition or "").replace("_", " ").strip()


def due(user_id: str, limit: int = LOOK_AT) -> list[dict]:
    """Detections nothing has looked at yet, oldest first.

    Oldest first because a situation that has been sitting unhandled since
    this morning has a better claim on the day's budget than one from a
    minute ago — and because a newest-first pass under a ceiling would starve
    the backlog forever.

    `critical` never appears here. That is not a filter applied later; it is
    the query, so no caller can reach one by asking differently.
    """
    rows = db.connect().execute(
        "SELECT e.* FROM events e"
        " LEFT JOIN notices n ON n.event_id = e.id"
        " WHERE e.user_id=? AND e.type='detection' AND n.id IS NULL"
        f"   AND e.severity IN ({','.join('?' * len(HANDLES))})"
        " ORDER BY e.created_at, e.rowid LIMIT ?",
        (user_id, *HANDLES, limit)).fetchall()
    return [{"event_id": r["id"], "condition": r["condition"],
             "severity": r["severity"], "noticed_at": r["created_at"]}
            for r in rows]


def _ask_the_coach(user_id: str, item: dict) -> str | None:
    """The free attempt. Returns what the offline stack had, or None.

    No network, no key, nothing per turn — :mod:`jim.pipeline` is the part
    that works in a tunnel, and it is asked before anything is bought.
    """
    ran = pipeline.run(user_id, "", _in_words(item["condition"]))
    return ran["text"]


_SYSTEM = (
    "You are JIM, handling something the offline coach noticed and could not "
    "settle from what it already knows. Situation: {situation}. Be brief, "
    "practical and calm. Never diagnose; for medical, legal or financial "
    "decisions, point to a qualified professional. If this person may be in "
    "danger, say plainly that they should seek immediate help.\n{context}"
)


def _ask_jim(user_id: str, item: dict, cloud=None) -> dict:
    """The paid turn. JIM answers the situation the coach could not.

    Returns what was generated and who generated it. A turn that degraded to
    the stub is reported as such and is **not** spending: nothing was bought,
    so nothing is charged and the situation stays open for a pass on a day the
    model is reachable.
    """
    from . import coach
    situation = _in_words(item["condition"])
    system = _SYSTEM.format(situation=situation,
                            context=coach._context(user_id))
    system += i18n.directive(i18n.effective_language(user_id))
    gen = llm.generate_for_user(user_id, system, situation, cloud=cloud)
    return {"text": gen["text"], "provider": gen["provider"],
            "degraded": bool(gen.get("degraded")), "reason": gen.get("reason")}


def _record(user_id: str, item: dict, settled_by: str, said: str) -> dict:
    nid = db.new_id("ntc")
    conn = db.connect()
    conn.execute(
        "INSERT INTO notices (id, user_id, event_id, condition, severity,"
        " settled_by, said, noticed_at) VALUES (?,?,?,?,?,?,?,?)",
        (nid, user_id, item["event_id"], item["condition"] or "",
         item["severity"] or "", settled_by, said, db.utcnow()))
    conn.commit()
    return {"id": nid, "event_id": item["event_id"],
            "condition": item["condition"], "severity": item["severity"],
            "settled_by": settled_by, "said": said}


def run(user_id: str, cloud=None, limit: int = LOOK_AT) -> dict:
    """The unattended pass. Try the coach on each; pay only where it failed.

    Returns what it settled for nothing and what it had to buy, kept apart,
    because *the coach handled all of it* and *it spent three turns* are the
    two different days a person wants to be able to tell apart at a glance.

    The permit is checked once, up front. That is deliberate: a pass that ran,
    settled four things for free and then reported it was not allowed would be
    a confusing way to say *you never turned this on*.
    """
    if not permits.granted(user_id, PERMIT):
        raise NotPermitted(NOT_PERMITTED)

    by_coach, by_jim, unreachable, over_budget = [], [], [], []
    for item in due(user_id, limit):
        # Free first, always.
        free = _ask_the_coach(user_id, item)
        if free:
            by_coach.append(_record(user_id, item, "coach", free))
            continue
        # Only now is spending even a question — and running out of it does
        # not end the pass. `continue`, not `break`: the situations after
        # this one may well be ones the coach can settle for nothing, and
        # stopping here would withhold free work over a spent budget.
        if not _room_to_spend(user_id):
            over_budget.append({"event_id": item["event_id"],
                                "condition": item["condition"]})
            continue
        answered = _ask_jim(user_id, item, cloud=cloud)
        if answered["degraded"] or not (answered["text"] or "").strip():
            # Nothing was bought. No row, no charge, and the situation is
            # still there for a day the model can be reached.
            unreachable.append({"event_id": item["event_id"],
                                "condition": item["condition"],
                                "because": answered["reason"]})
            continue
        said = answered["text"]
        if _DENY.search(said):
            # The safety line the rest of the product answers to. An unsafe
            # generation is not filed and not charged for.
            unreachable.append({"event_id": item["event_id"],
                                "condition": item["condition"],
                                "because": "refused"})
            continue
        by_jim.append(_record(user_id, item, "jim", said))
        # The paid turn becomes a permanent asset, exactly as a coach turn
        # does: distilled into the store the offline stack predicts from, so
        # the next time this situation arises the free half settles it.
        pipeline.deposit(user_id, "", _in_words(item["condition"]), said,
                         "noticed", answered["provider"])

    return {
        "by_coach": by_coach,
        "by_jim": by_jim,
        # Named rather than folded into a count: a pass that could not reach a
        # model is not a quiet pass, and a screen showing them the same way
        # would be reporting a silent failure as calm.
        "unreachable": unreachable,
        # What needed paying for on a day with nothing left to pay with. Not
        # an error and not a failure — the ordinary end of a budgeted day —
        # but it is the difference between *there was nothing to do* and
        # *there was, and it waits for tomorrow*.
        "over_budget": over_budget,
        "remaining_today": max(0, errands.DAILY - errands.spent_today(user_id)),
        "nothing_noticed": not (by_coach or by_jim or unreachable
                                or over_budget) and not due(user_id, 1),
    }


def ledger(user_id: str, limit: int = 20) -> list[dict]:
    """What it noticed and what settled it, newest first.

    `settled_by` is the column worth reading. *It handled six things today*
    is a fact about the guardian; *five of them cost nothing* is the fact
    about the product, and it is the one this whole ladder exists to make
    true.
    """
    return [{"id": r["id"], "event_id": r["event_id"],
             "condition": r["condition"], "severity": r["severity"],
             "settled_by": r["settled_by"], "said": r["said"],
             "noticed_at": r["noticed_at"]}
            for r in db.connect().execute(
                "SELECT * FROM notices WHERE user_id=?"
                " ORDER BY noticed_at DESC, rowid DESC LIMIT ?",
                (user_id, limit)).fetchall()]


def standing(user_id: str) -> dict:
    """How the ladder is actually performing for this person.

    The one number worth putting on a screen: of everything the guardian
    handled unattended, how much of it the free half settled. A ladder whose
    paid half is doing most of the work is not saving anybody anything, and
    this is where that would show.
    """
    rows = db.connect().execute(
        "SELECT settled_by, COUNT(*) AS n FROM notices WHERE user_id=?"
        " GROUP BY settled_by", (user_id,)).fetchall()
    counts = {r["settled_by"]: r["n"] for r in rows}
    free, paid = counts.get("coach", 0), counts.get("jim", 0)
    # `settled_free` / `settled_paid` rather than `by_coach` / `by_jim`:
    # those are the names the *lists* of notices carry on a pass, and one
    # wire name carries one type. Counts and rows are not the same thing.
    return {"settled_free": free, "settled_paid": paid,
            # None rather than 0 when nothing has been handled: *the coach
            # settled none of them* and *nothing has happened yet* are
            # different, and a bare 0% would say the first about the second.
            "free_share": round(free / (free + paid), 2) if free + paid else None,
            "permitted": permits.granted(user_id, PERMIT),
            "spent_today": errands.spent_today(user_id),
            "daily": errands.DAILY}
