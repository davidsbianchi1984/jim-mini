"""The coach runs the day; JIM is what it calls when it cannot settle it.

Every piece of this loop already existed. The offline coach answers for
nothing and touches no network. When it cannot answer it writes the miss down.
The curriculum turns those misses — plus the metrics and goals this person
actually put the guardian near — into a study list. And then the last step was
a person opening a screen and pressing **study**, one topic at a time, which is
a loop that closes only for somebody who already knows it is there.

    asked     does the coach know what it does not know
    mattered  does anything go and find out

## What these guards hold

* the pass is refused outright without an explicit permit — going out to
  study unattended is `asked`, never assumed by opening a session;
* the day's budget is counted from the ledger, so a restart is not a fresh
  day's spending, and no argument raises the ceiling;
* an errand only ever studies something the offline coach could not already
  answer, so the thing that spends never spends on what the free thing has;
* what comes back is folded where the offline coach reads it, and the miss it
  answers is closed;
* every row says which monitor asked for it — *it studied sleep* is a fact
  about the guardian, *it studied sleep because your sleep band has a learned
  baseline* is a fact about the person;
* and there is one way out. Both excursion routes were written inline and had
  already drifted; a guard holds them to the single path that sanitises.

## What the budget is actually protecting

Tokens, today. Not tokens, afterwards — and these guards are written for the
second case, because the first is the reading that would delete them once a
model turn is cheap enough to run constantly.

The local coach is the product: it answers with no signal and no key, it holds
the private half where no third party ever sees it, its store carries the
provenance of every entry so a vendor model's claim can be set beside what is
actually known, and it accumulates for as long as somebody uses it — what it
learned about them at thirty is still there at sixty. None of that gets
cheaper to give up. So the shape these hold is *local first, and outside only
for what the local half could not answer*, which stays right at any price.
"""

from __future__ import annotations

import inspect

import pytest

from jim import errands, permits, research

from .conftest import enroll


def _allow(client, user_id):
    r = client.put(f"/engaged/{user_id}/permits/{errands.PERMIT}",
                   json={"granted": True})
    assert r.status_code == 200, r.text


def _miss(client, user_id, question="what helps a 3am wake-up"):
    """Make the offline coach fail to answer, which is what records a gap.

    Through the coach rather than by writing the row: the gap is only worth
    studying if the pipeline itself could not answer, and a test that inserts
    the row directly would pass over a pipeline that had stopped recording
    them.
    """
    r = client.post(f"/coach/{user_id}", json={"area": "personal_growth",
                                               "message": question})
    assert r.status_code in (200, 201), r.text
    return question


# --------------------------------------------------------------------------
# Nobody said it could.
# --------------------------------------------------------------------------

def test_the_pass_is_refused_until_somebody_allows_it(client):
    """Going out to study unattended is not covered by opening a session. It
    spends, and it reaches outside the host."""
    user_id = enroll(client)
    _miss(client, user_id)
    r = client.post(f"/errands/{user_id}")
    assert r.status_code == 403, r.text
    assert "study" in r.text


def test_the_permit_says_what_leaves_and_what_is_kept(client):
    """A person deciding says yes to a sentence, not to a switch label."""
    user_id = enroll(client)
    says = permits.AREAS[errands.PERMIT]["says"]
    assert "never you" in says
    assert permits.AREAS[errands.PERMIT]["standing"] == "asked"


# --------------------------------------------------------------------------
# The thing itself.
# --------------------------------------------------------------------------

def test_a_miss_becomes_an_errand_and_the_coach_keeps_it(client):
    """The whole loop, end to end: the coach could not answer, JIM went and
    studied it, and what came back is where the offline coach reads it."""
    user_id = enroll(client)
    _allow(client, user_id)
    asked = _miss(client, user_id)

    out = client.post(f"/errands/{user_id}")
    assert out.status_code == 201, out.text
    studied = out.json()["errands"]
    assert studied, "nothing was studied although the coach had missed"
    assert any(row["topic"].lower() == asked.lower() for row in studied)

    store = client.get(f"/coach/{user_id}/store").json()
    assert any(e["source"] == "excursion" for e in store["excursions"]), (
        "the findings are not where the offline coach reads them")


def test_the_miss_it_answered_is_closed(client):
    """A gap that stays open after the thing that fills it is a gap that gets
    studied again tomorrow, on somebody's money."""
    user_id = enroll(client)
    _allow(client, user_id)
    _miss(client, user_id)
    client.post(f"/errands/{user_id}")

    again = client.post(f"/errands/{user_id}").json()
    topics = [row["topic"] for row in again["errands"]]
    assert "what helps a 3am wake-up" not in topics


def test_every_row_says_which_monitor_asked_for_it(client):
    user_id = enroll(client)
    _allow(client, user_id)
    _miss(client, user_id)
    client.post(f"/errands/{user_id}")

    ledger = client.get(f"/errands/{user_id}").json()
    assert ledger["errands"], "nothing in the ledger"
    for row in ledger["errands"]:
        assert row["why"], f"{row['topic']} was studied for no stated reason"


def test_an_errand_never_studies_what_the_coach_already_knows(client):
    """The thing that spends does not spend on what the free thing has. The
    curriculum subtracts the store; this holds that it still does."""
    user_id = enroll(client)
    _allow(client, user_id)
    _miss(client, user_id)
    client.post(f"/errands/{user_id}")

    store = client.get(f"/coach/{user_id}/store").json()
    known = {e["topic"].lower() for e in store["excursions"] + store["deposits"]}
    for item in errands.due(user_id):
        assert item["topic"].lower() not in known


# --------------------------------------------------------------------------
# What it costs.
# --------------------------------------------------------------------------

def test_the_day_has_a_ceiling_and_the_ledger_is_what_counts_it(client):
    """Counted from the rows, not from a variable — a counter can only agree
    with itself, and a restart would hand back a fresh day's spending."""
    user_id = enroll(client)
    _allow(client, user_id)
    for n in range(errands.DAILY + 2):
        _miss(client, user_id, f"an unanswerable question number {n}")

    client.post(f"/errands/{user_id}")
    assert errands.spent_today(user_id) <= errands.DAILY

    refused = client.post(f"/errands/{user_id}")
    assert refused.status_code == 429, refused.text
    assert "tomorrow" in refused.text


def test_no_argument_raises_the_ceiling():
    """Crude on purpose. Every reason to lift a budget for one call is
    reasonable at the time, and the sum of them is why budgets stop meaning
    anything."""
    assert list(inspect.signature(errands._may_spend).parameters) == ["user_id"]
    assert "DAILY" in inspect.getsource(errands._may_spend)


def test_a_quiet_pass_and_a_spent_one_are_different_answers(client):
    """A screen that showed *nothing to study* and *nothing left to spend*
    the same way would be lying about one of them."""
    user_id = enroll(client)
    _allow(client, user_id)
    out = client.post(f"/errands/{user_id}").json()
    assert out["errands"] == [] or out["errands"]
    assert "remaining_today" in out and "nothing_to_study" in out


# --------------------------------------------------------------------------
# One way out.
# --------------------------------------------------------------------------

def test_there_is_one_path_out_and_it_sanitises(client):
    """Both excursion routes were written inline in `api.py` and had already
    drifted — one folded its findings and closed the matching miss, the other
    did neither, with nothing to say which was intended."""
    from jim import api
    source = inspect.getsource(api)
    assert "research.gather(" not in source, (
        "a route gathers directly again; the sanitised path is "
        "`research.excursion`")
    assert "research.excursion(" in source
    assert "sanitize" in inspect.getsource(research.excursion)


def test_the_errand_pass_cannot_reach_the_network_except_through_it():
    """The pass decides *whether* to spend. The going-out is not its to do,
    so it holds no provider and opens no socket of its own."""
    source = inspect.getsource(errands)
    assert "llm" not in source
    assert "research.excursion(" in source


def test_what_left_is_recorded_beside_what_was_studied(client):
    """`brief` is exactly what could have gone out. The ledger carries the
    count of what was taken out of it, so *nothing private left* is a thing
    somebody can check rather than a thing this page claims."""
    user_id = enroll(client, display_name="Marguerite")
    _allow(client, user_id)
    _miss(client, user_id, "what Marguerite should do about 3am waking")
    client.post(f"/errands/{user_id}")

    # The ledger is newest first and a pass runs several errands, so the row
    # is found by its topic rather than taken off the top — an assertion about
    # *this* brief has to be made about this brief.
    rows = client.get(f"/errands/{user_id}").json()["errands"]
    row = next(r for r in rows if "Marguerite" in r["topic"])
    assert "redactions" in row and "left_host" in row
    excursion = client.get(f"/excursions/entry/{row['excursion_id']}").json()
    assert "Marguerite" not in excursion["brief"]
    assert excursion["redactions"] >= 1


@pytest.mark.parametrize("field", ["spent_today", "daily", "permitted", "due"])
def test_the_ledger_says_what_is_left_and_what_is_waiting(client, field):
    """An empty ledger has three different causes, and a person is entitled to
    tell them apart: nothing worth studying, nothing left to spend, or nobody
    ever allowed it."""
    user_id = enroll(client)
    assert field in client.get(f"/errands/{user_id}").json()
