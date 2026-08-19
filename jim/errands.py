"""What the coach could not answer becomes what JIM goes and learns.

The offline coach (:mod:`jim.pipeline`) runs the day. It touches no network,
costs nothing per turn, and answers from the curated pack, what JIM learned on
past excursions, and what paid turns deposited. When it cannot answer, it
writes the miss down — :func:`jim.pipeline._record_gap` — and
:func:`jim.pipeline.curriculum` turns those misses, plus the metrics and goals
this person actually put the guardian near, into a study list.

Then nothing happened. Every piece of that loop existed and the last step was
a person opening a screen and pressing **study** on one topic at a time, which
is a loop that closes only for somebody who already knows it is there.

    asked     does the coach know what it does not know
    mattered  does anything go and find out

This module is that step. The coach runs the day and JIM is what it calls when
it cannot settle something — which is the right way round for cost as well as
for privacy: the free thing runs constantly, and the thing that spends runs
when the free thing has already failed and said so in writing.

## Spending is a decision, and it is bounded

An unattended pass that can spend without limit is a bill somebody discovers.
So:

* it does not run at all without an explicit permit (``study_on_your_own``,
  in :mod:`jim.permits`), which is `asked` rather than assumed by opening a
  session;
* it runs at most :data:`DAILY` errands in a day, counted from the ledger
  rather than from a variable, so a restart does not reset the budget — and
  since 0.84.0 that ceiling is **shared** with :mod:`jim.noticed`, the other
  unattended pass, because two budgets would mean the real ceiling is their
  sum;
* the ceiling takes no argument. Every reason to raise one for a single call
  is reasonable at the time, and the sum of them is why this kind of limit
  stops meaning anything.

## This is a step, and the local half is not the part that goes away

The obvious reading of a budget is *tokens are expensive*, and today that is
true. It is not why this is shaped this way, and saying so matters because the
cheap reading is the one that would get this deleted the moment the price of a
model turn falls far enough to run one constantly.

The local half is the product:

* **It works with nothing.** No signal, no plan, no key — a phone in a tunnel
  still has its coach, and that is when somebody is most likely to need it.
* **It is private by design rather than by policy.** Everything the coach
  knows about a person stays on their machine. What leaves is a general
  subject with the person taken out of it, and the sanitiser is the only door.
  A third-party model never holds the private half, so no promise about how
  that model is operated has to be believed.
* **It keeps the other half honest.** The store's every entry carries its
  provenance — hand-written pack, excursion, deposited model turn — so what a
  vendor's model asserts can be set beside what is actually known, by
  somebody who did not write either. A guardian with one voice and no record
  is a guardian nobody can argue with.
* **It grows with the person.** The store is cumulative and it is theirs: what
  was learned about them at thirty is still there at sixty, adapting as they
  change rather than resetting with each new model release. That is the asset
  a general model cannot have, and it is why the fold-back is permanent and
  the provenance is kept.

So when a model turn costs nothing, the right change is that this pass runs
more often and reaches further — not that the coach stops being the thing that
answers. The budget below is a cost measure today and a discipline afterwards.

## Nothing private rides along

An errand's brief goes through the same sanitiser as any excursion, and the
excursion path is the only way out — see :func:`jim.research.excursion`. What
comes back is general knowledge about a topic, folded into the store the
offline coach predicts from. The topic itself stays local: it is in the
ledger and in the excursion row, never in the brief beyond what the sanitiser
already cleared.

That is the shape the whole product needs: the local half can know everything
about somebody, and the half that goes outside knows a subject and not a
person.
"""

from __future__ import annotations

from . import db, i18n, permits, pipeline, research

#: Errands one day may spend. Small on purpose: this is the unattended pass,
#: and a person who wants more study can ask for it directly and watch it
#: happen. Read by :func:`spent_today` against the ledger rather than held in
#: memory, so a restart is not a fresh budget.
DAILY = 3

#: The permit this pass runs under. Named here rather than passed in, so a
#: caller cannot hand it a different one.
PERMIT = "study_on_your_own"


class NotPermitted(RuntimeError):
    """Refused: nobody said this account's guardian may study unattended."""


class Spent(RuntimeError):
    """Refused: the day's errands are used up."""


def spent_today(user_id: str) -> int:
    """Unattended turns spent for this user since midnight UTC, from the
    ledgers — errands **and** the situations :mod:`jim.noticed` had to pay to
    handle.

    The ledger and not a counter, because the question a person asks is *what
    did it spend today* and a counter cannot answer it — it can only agree
    with itself.

    Both kinds, against one ceiling, because there are now two passes that can
    spend unattended and giving each its own budget would make the real
    ceiling their sum — which is the failure :data:`DAILY` is written to avoid,
    arriving by a different road. Study and handling compete for the same day.
    """
    from . import noticed
    mine = db.connect().execute(
        "SELECT COUNT(*) AS n FROM errands WHERE user_id=?"
        " AND substr(opened_at, 1, 10) = substr(?, 1, 10)",
        (user_id, db.utcnow())).fetchone()["n"]
    return mine + noticed.spent_today(user_id)


def _may_spend(user_id: str) -> None:
    """The chokepoint: permit first, then budget. One function, so a second
    caller cannot arrive with its own idea of either."""
    if not permits.granted(user_id, PERMIT):
        raise NotPermitted(
            "this guardian has not been allowed to go and study on its own — "
            "turn it on in what it may do for you, where it says what it "
            "sends and what it keeps")
    if spent_today(user_id) >= DAILY:
        raise Spent(i18n.fill(i18n.ERRANDS_SPENT, count=DAILY))


def due(user_id: str, limit: int = DAILY) -> list[dict]:
    """What is worth studying next, and why — the coach's own misses first.

    Straight off :func:`jim.pipeline.curriculum`, which already subtracts
    everything the store covers. That subtraction is the reason this is cheap
    to be wrong about: a topic the offline coach can already answer is never
    an errand, so the pass cannot spend on something it already has.
    """
    return pipeline.curriculum(user_id)["suggested"][:limit]


def run(user_id: str, cloud=None, limit: int = DAILY, pdi=None) -> dict:
    """The unattended pass. Study what the coach missed, fold it back.

    Returns what it did and what it did not: a pass that studied nothing
    because there was nothing to study and a pass that studied nothing
    because the budget was gone are different answers, and a screen that
    showed them the same way would be lying about one of them.
    """
    _may_spend(user_id)
    room = min(limit, DAILY - spent_today(user_id))
    ran, conn = [], db.connect()
    for item in due(user_id, room):
        cid = research.excursion(user_id, item["topic"], cloud=cloud,
                                 learn=True, pdi=pdi)
        row = conn.execute(
            "SELECT redactions, left_host FROM excursions WHERE id=?",
            (cid,)).fetchone()
        eid = db.new_id("err")
        conn.execute(
            "INSERT INTO errands (id, user_id, topic, area, why, excursion_id,"
            " redactions, left_host, opened_at) VALUES (?,?,?,?,?,?,?,?,?)",
            (eid, user_id, item["topic"], item["area"], item["why"], cid,
             row["redactions"], row["left_host"], db.utcnow()))
        conn.commit()
        ran.append({"id": eid, "topic": item["topic"], "area": item["area"],
                    "why": item["why"], "excursion_id": cid,
                    "left_host": bool(row["left_host"]),
                    "redactions": row["redactions"]})
    # The ledger writes itself into the vault's own tables (jim/recall.py →
    # PDI resident): rows the PDI console can query beside the data they are
    # about. Non-fatal, and said rather than hidden — `vaulted` is False
    # when the tandem is absent, offline, or too old to carry a table.
    from . import recall as recall_mod
    vaulted = recall_mod.tabulate(
        pdi, "jim_errands",
        [{"errand": e["id"], "topic": e["topic"], "area": e["area"],
          "why": e["why"], "left_host": 1 if e["left_host"] else 0,
          "redactions": e["redactions"]} for e in ran],
        source_ref=user_id) if ran else False
    # `errands`, not `studied`: the study route's `studied` is the name of
    # one topic, and one wire name carries one type.
    return {"errands": ran, "remaining_today": DAILY - spent_today(user_id),
            "nothing_to_study": not ran and not due(user_id, 1),
            "vaulted": vaulted}


def ledger(user_id: str, limit: int = 20) -> list[dict]:
    """What it went and learned on this person's behalf, newest first.

    Every row carries the monitor that asked for it. *It studied sleep* is a
    fact about the guardian; *it studied sleep because your sleep band has a
    learned baseline* is a fact about the person, and only the second one is
    worth reading.
    """
    return [{"id": r["id"], "topic": r["topic"], "area": r["area"],
             "why": r["why"], "excursion_id": r["excursion_id"],
             "redactions": r["redactions"],
             "left_host": bool(r["left_host"]), "opened_at": r["opened_at"]}
            for r in db.connect().execute(
                "SELECT * FROM errands WHERE user_id=?"
                " ORDER BY opened_at DESC, rowid DESC LIMIT ?",
                (user_id, limit)).fetchall()]
