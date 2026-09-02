"""What the coach noticed, and when that is worth paying a turn to handle.

The field ask, in its own words: *for autonomous stuff throughout your day to
save tokens I want coach to be running most of those, and when something is
identified by coach, it could then start using tokens as Jim to better handle
the situation — not only that, Jim has much more tools and internet access.*

    asked     does the free half run the day and the paid half only what it cannot
    mattered  is the decision to spend made by something, and can it be read back

Half of that ladder shipped in 0.82.0: `jim/errands.py` turns what the coach
could not *answer* into a bounded study pass. The other half had no path at
all. The guardian records detections all day and nothing ever decided that one
of them warranted a paid turn — a gap became study, a situation became a row.

## What these guards hold

* the offline coach is asked **first**, every time, and what it settles costs
  nothing — the ordering is the feature, not an optimisation in front of it;
* what it settles and what had to be bought are reported apart, because *the
  coach handled all of it* and *it spent three turns* are two different days;
* both unattended passes spend against **one** ceiling, since two budgets
  would make the real ceiling their sum;
* a paid turn is deposited, so the same situation is settled for free the next
  time — the ladder pays down its own bill;
* a turn that reached no model buys nothing, is charged nothing, and leaves
  the situation open rather than recording a silent failure as handled;
* `critical` never reaches this pass at all. That path belongs to the
  escalation ladder, which takes it to a person;
* and it advises rather than acts, which is a decision this file records
  rather than a gap it apologises for.
"""

from __future__ import annotations

import inspect

import pytest

from jim import db, errands, escalation, noticed, permits, pipeline

from .conftest import enroll


def _allow(client, user_id, permit=noticed.PERMIT):
    r = client.put(f"/engaged/{user_id}/permits/{permit}",
                   json={"granted": True})
    assert r.status_code == 200, r.text


def _detect(user_id, condition="restless nights", severity="guidance"):
    """A detection, written the way the guardian writes one."""
    from jim import guardian
    return guardian._event(user_id, "detection", condition=condition,
                           severity=severity,
                           detail={"reason": "for the test"})["id"]


def _store(user_id, topic, guidance="drink water and go to bed earlier"):
    """Something the offline coach can answer from, deposited the way a paid
    turn deposits it."""
    pipeline.deposit(user_id, "", topic, guidance, "test", "test")


# --------------------------------------------------------------------------
# The free half runs first, every time.
# --------------------------------------------------------------------------

def test_what_the_coach_can_settle_costs_nothing(client):
    """The whole feature. *The coach runs most of these* is only true if the
    coach is actually asked first."""
    uid = enroll(client)
    _allow(client, uid)
    _detect(uid, condition="restless nights")
    _store(uid, "restless nights")

    out = client.post(f"/noticed/{uid}").json()
    assert [n["condition"] for n in out["by_coach"]] == ["restless nights"]
    assert out["by_jim"] == []
    assert errands.spent_today(uid) == 0, "the free half spent nothing"


def test_the_coach_is_asked_before_anything_is_bought():
    """Checked in the source rather than inferred from a result: a pass that
    asked the model first and consulted the store afterwards would produce
    the same answers at a price."""
    source = inspect.getsource(noticed.run)
    assert source.index("_ask_the_coach") < source.index("_ask_jim")
    # And the spend check sits after the free attempt, not before it.
    assert source.index("_ask_the_coach") < source.index("_room_to_spend")


def _model_answers(monkeypatch, text="try a wind-down hour before bed"):
    """A reachable model, so the paid rung can actually be walked.

    The stub answers in tests, and a stub answer is correctly reported as
    *nothing was bought* — which leaves the rung this whole round exists for
    untested unless something stands in for a real provider.
    """
    def answered(user_id, system, message, cloud=None, source=None):
        return {"text": text, "provider": "claude", "degraded": False,
                "reason": None}
    monkeypatch.setattr("jim.llm.generate_for_user", answered)


def test_what_the_coach_cannot_settle_is_put_to_jim(client, monkeypatch):
    """The other half of the ladder. Nothing in the store answers this, so
    the free attempt fails and a turn is spent."""
    uid = enroll(client)
    _allow(client, uid)
    _detect(uid, condition="a thing nothing in the pack has ever covered")
    _model_answers(monkeypatch)

    out = client.post(f"/noticed/{uid}").json()
    assert out["by_coach"] == []
    assert [n["condition"] for n in out["by_jim"]] == [
        "a thing nothing in the pack has ever covered"]
    assert out["by_jim"][0]["settled_by"] == "jim"
    assert errands.spent_today(uid) == 1, "a bought turn is spending"


def test_the_bought_turn_is_on_the_ledger_with_who_settled_it(client,
                                                              monkeypatch):
    """*It handled six things today* is a fact about the guardian; *five of
    them cost nothing* is the fact about the product."""
    uid = enroll(client)
    _allow(client, uid)
    _detect(uid, condition="something unheard of")
    _model_answers(monkeypatch, "a practical suggestion")
    client.post(f"/noticed/{uid}")

    rows = client.get(f"/noticed/{uid}").json()["handled"]
    assert [r["settled_by"] for r in rows] == ["jim"]
    assert rows[0]["said"] == "a practical suggestion"


def test_the_same_situation_is_bought_once(client, monkeypatch):
    """The ladder pays down its own bill. What a paid turn learned is
    deposited where the offline stack reads it, so the next time this
    happens the free half settles it."""
    uid = enroll(client)
    _allow(client, uid)
    _detect(uid, condition="a singular unheard-of situation")
    _model_answers(monkeypatch, "keep a steady routine and rest properly")
    first = client.post(f"/noticed/{uid}").json()
    assert len(first["by_jim"]) == 1

    # The same thing happens again tomorrow.
    _detect(uid, condition="a singular unheard-of situation")
    second = client.post(f"/noticed/{uid}").json()
    assert second["by_jim"] == [], "bought twice"
    assert len(second["by_coach"]) == 1
    assert errands.spent_today(uid) == 1, "and charged once"


def test_one_bought_turn_settles_the_situations_near_it(client, monkeypatch):
    """Found by a ceiling test that would not fail.

    It created five near-identical situations expecting three to be bought,
    and one was: the deposit the first paid turn left answered the rest, for
    nothing, on the same pass. That is not a quirk to work around — it is the
    ladder's whole economic claim, that spending is front-loaded and decays,
    and it was worth a test of its own rather than a note in another one.
    """
    uid = enroll(client)
    _allow(client, uid)
    for n in range(4):
        _detect(uid, condition=f"restless nights in the small hours {n}")
    _model_answers(monkeypatch, "keep the room cool and the hour steady")

    out = client.post(f"/noticed/{uid}").json()
    assert len(out["by_jim"]) == 1, "the first one paid"
    assert len(out["by_coach"]) == 3, "and carried the rest for nothing"
    assert errands.spent_today(uid) == 1


def test_the_days_ceiling_stops_the_paid_rung_and_says_so(client,
                                                          monkeypatch):
    """The free half keeps going when the budget is gone — which is the
    ordinary state of this product rather than a degraded one."""
    uid = enroll(client)
    _allow(client, uid)
    # Not one word in common between them, deliberately. A paid turn deposits
    # what it learned and the store scores on the topic's own words of four
    # letters or more, so a shared "an unheard-of matter of ..." would have
    # the first deposit settling the rest for free — the ladder working, and
    # this test measuring the wrong thing. It did exactly that twice before
    # the conditions got this plain.
    for word in ("quartz", "ferrets", "trombones", "monsoons", "lattices"):
        _detect(uid, condition=word)
    _model_answers(monkeypatch)

    out = client.post(f"/noticed/{uid}").json()
    assert len(out["by_jim"]) == errands.DAILY
    assert errands.spent_today(uid) == errands.DAILY

    # A spent day is reported, not refused: the pass still runs, still tries
    # the coach on everything, and names what it could not pay for.
    again = client.post(f"/noticed/{uid}")
    assert again.status_code == 201, again.text
    assert [n["condition"] for n in again.json()["over_budget"]] == [
        "monsoons", "lattices"]
    assert again.json()["remaining_today"] == 0


def test_the_two_passes_take_from_the_same_day(client, monkeypatch):
    """Spending on handling leaves less to spend on studying, because there
    is one ceiling rather than one each."""
    uid = enroll(client)
    _allow(client, uid)
    _allow(client, uid, errands.PERMIT)
    _detect(uid, condition="an unheard-of situation")
    _model_answers(monkeypatch)
    client.post(f"/noticed/{uid}")

    left = client.get(f"/errands/{uid}").json()
    assert left["spent_today"] == 1
    assert left["daily"] == errands.DAILY


def test_an_unsafe_generation_is_neither_filed_nor_charged(client,
                                                           monkeypatch):
    """The safety line the rest of the product answers to, on the one path
    where nobody is watching the answer arrive."""
    uid = enroll(client)
    _allow(client, uid)
    _detect(uid, condition="an unheard-of situation")
    from jim.guidance import _DENY
    unsafe = next(w for w in ("suicide", "kill yourself", "overdose")
                  if _DENY.search(w))
    _model_answers(monkeypatch, f"you should {unsafe}")

    out = client.post(f"/noticed/{uid}").json()
    assert out["by_jim"] == []
    assert out["unreachable"] and out["unreachable"][0]["because"] == "refused"
    assert errands.spent_today(uid) == 0


# --------------------------------------------------------------------------
# What it settled free and what it had to buy are different answers.
# --------------------------------------------------------------------------

def test_the_two_halves_are_reported_apart(client):
    """*The coach handled all of it* and *it spent three turns* are two
    different days, and a screen showing them the same way would be hiding
    the only number this ladder exists to move."""
    uid = enroll(client)
    _allow(client, uid)
    out = client.post(f"/noticed/{uid}").json()
    for half in ("by_coach", "by_jim", "unreachable"):
        assert half in out, half


def test_the_standing_says_how_much_the_free_half_carried(client):
    """The one number worth putting on a screen. A ladder whose paid half
    does most of the work is not saving anybody anything."""
    uid = enroll(client)
    _allow(client, uid)
    for n in range(3):
        _detect(uid, condition=f"restless nights {n}")
        _store(uid, f"restless nights {n}")
    client.post(f"/noticed/{uid}")

    standing = client.get(f"/noticed/{uid}").json()["settlement"]
    assert standing["settled_free"] == 3
    assert standing["settled_paid"] == 0
    assert standing["free_share"] == 1.0


def test_nothing_handled_is_not_the_same_as_none_settled_free(client):
    """A bare 0% would say *the coach settled none of them* about an account
    where nothing has happened yet."""
    uid = enroll(client)
    assert client.get(f"/noticed/{uid}").json()["settlement"]["free_share"] is None


# --------------------------------------------------------------------------
# One ceiling across both unattended passes.
# --------------------------------------------------------------------------

def test_both_passes_spend_against_one_ceiling(client):
    """Two budgets would mean the real ceiling is their sum, which is the
    failure `DAILY` is written to avoid arriving by a different road."""
    assert "noticed" in inspect.getsource(errands.spent_today)

    uid = enroll(client)
    # A handled-by-jim notice is spending, and the errands ledger sees it.
    db.connect().execute(
        "INSERT INTO notices (id, user_id, event_id, condition, severity,"
        " settled_by, said, noticed_at) VALUES (?,?,?,?,?,?,?,?)",
        ("ntc_x", uid, "ev_x", "a thing", "guidance", "jim", "said",
         db.utcnow()))
    db.connect().commit()
    assert errands.spent_today(uid) == 1


def test_what_the_coach_settled_is_not_spending(client):
    """Free is free. A notice the offline stack answered never touches the
    budget, which is the point of asking it first."""
    uid = enroll(client)
    db.connect().execute(
        "INSERT INTO notices (id, user_id, event_id, condition, severity,"
        " settled_by, said, noticed_at) VALUES (?,?,?,?,?,?,?,?)",
        ("ntc_y", uid, "ev_y", "a thing", "guidance", "coach", "said",
         db.utcnow()))
    db.connect().commit()
    assert errands.spent_today(uid) == 0


def test_no_argument_raises_the_ceiling():
    """Crude on purpose, and the same rule the errands pass holds: every
    reason to lift a budget for one call is reasonable at the time."""
    assert list(inspect.signature(noticed._room_to_spend).parameters) == [
        "user_id"]
    assert "errands.DAILY" in inspect.getsource(noticed._room_to_spend)


def test_a_spent_budget_does_not_stop_the_free_half(client, monkeypatch):
    """The design this round got wrong first.

    The pass raised when the budget was gone, which refused the work costing
    nothing because it could not do the work that costs — and it broke out of
    the loop, so situations further down that the coach could have settled for
    free were never even tried. Running out of budget is a fact this pass
    reports, not an error it raises.
    """
    uid = enroll(client)
    _allow(client, uid)
    # One the coach cannot settle, then one it can.
    _detect(uid, condition="trombones")
    _detect(uid, condition="restless nights")
    _store(uid, "restless nights")
    # Nothing left to spend today.
    for n in range(errands.DAILY):
        db.connect().execute(
            "INSERT INTO notices (id, user_id, event_id, condition, severity,"
            " settled_by, said, noticed_at) VALUES (?,?,?,?,?,?,?,?)",
            (f"ntc_spent{n}", uid, f"ev_spent{n}", "x", "guidance", "jim",
             "s", db.utcnow()))
    db.connect().commit()

    out = client.post(f"/noticed/{uid}").json()
    assert out.get("over_budget"), "it says what it could not pay for"
    assert [n["condition"] for n in out["by_coach"]] == ["restless nights"], \
        "and carried on to the one that was free"


# --------------------------------------------------------------------------
# A paid turn is bought once.
# --------------------------------------------------------------------------

def test_a_bought_turn_is_deposited_so_it_is_free_next_time(client):
    """The ladder pays down its own bill: a situation bought once is settled
    by the free half the next time it happens."""
    assert "pipeline.deposit" in inspect.getsource(noticed.run)


def test_a_pass_that_reached_no_model_buys_nothing(client):
    """Nothing was bought, so nothing is charged — and the situation stays
    open for a day the model can be reached, rather than being recorded as
    handled by a silent failure."""
    uid = enroll(client)
    _allow(client, uid)
    _detect(uid, condition="a thing nothing in the pack has ever covered")

    out = client.post(f"/noticed/{uid}").json()
    assert out["unreachable"], "the stub answers in tests"
    assert errands.spent_today(uid) == 0
    assert noticed.ledger(uid) == [], "no row for something never bought"
    # Still there to try again.
    assert [d["condition"] for d in noticed.due(uid)] == [
        "a thing nothing in the pack has ever covered"]


# --------------------------------------------------------------------------
# Emergencies are not this pass's business.
# --------------------------------------------------------------------------

def test_a_critical_detection_never_reaches_this_pass(client):
    """The escalation ladder owns those and takes them to a person. Putting
    a model turn in front of that path would add latency to the one case
    where latency is the harm."""
    uid = enroll(client)
    _allow(client, uid)
    _detect(uid, condition="cardiac event", severity="critical")

    assert noticed.due(uid) == []
    out = client.post(f"/noticed/{uid}").json()
    assert out["by_coach"] == [] and out["by_jim"] == []


def test_critical_is_excluded_by_the_query_not_by_a_later_filter():
    """So no caller can reach one by asking differently."""
    assert "critical" not in noticed.HANDLES
    assert "severity IN" in inspect.getsource(noticed.due)


def test_the_severity_this_pass_skips_is_the_one_the_ladder_escalates():
    """The two modules agree about which word means an emergency, rather
    than each carrying its own idea of it."""
    assert "critical" in escalation._SEVERITY_BASE
    assert escalation._SEVERITY_BASE["critical"] >= 4


# --------------------------------------------------------------------------
# Asked, not assumed. And it advises rather than acts.
# --------------------------------------------------------------------------

def test_it_is_refused_until_somebody_allows_it(client):
    uid = enroll(client)
    r = client.post(f"/noticed/{uid}")
    assert r.status_code == 403, r.text
    assert "turn it on" in r.text


def test_the_permit_is_asked_rather_than_covered_by_opening_a_session():
    spec = permits.AREAS[noticed.PERMIT]
    assert spec["standing"] == "asked"
    # It says what it looks at and what it does about it, in the sentence a
    # person reads before saying yes.
    assert "advises, never acts" in spec["says"]


def test_the_permit_is_its_own_and_not_the_study_one():
    """Sending a general topic out and bringing knowledge back, and putting
    this person's own situation to a model, are opposite shapes. Separate
    yeses."""
    assert noticed.PERMIT != errands.PERMIT


def test_this_pass_reaches_no_acting_tool():
    """An unattended pass that could act would be the engaged session's whole
    apparatus with the person taken out of it."""
    source = inspect.getsource(noticed)
    assert "engaged" not in source.replace("jim.engaged", "")


@pytest.mark.parametrize("settled", noticed.SETTLED_BY)
def test_every_way_a_notice_settles_is_a_word_somebody_can_read(settled):
    assert settled and settled.isalpha()


# -- the ladder winds itself -----------------------------------------------
#
# The whole module shipped and then closed only from a button on the Coach
# screen — the loop-that-a-person-has-to-know-about defect its own header
# quotes jim/errands.py naming, rebuilt one module over. "For autonomous
# stuff throughout your day" is the ask; the trigger is the traffic where
# the work is born, handed to the response's background at the doors that
# take a reading, a check-in, a journal line, an activity, or a coach turn.


def test_the_pass_runs_on_the_heels_of_a_reading(client):
    """No button anywhere in this test: a reading arrives, and the ladder
    has run by the time the response has gone out."""
    uid = enroll(client)
    _allow(client, uid)
    _detect(uid, condition="restless nights")
    _store(uid, "restless nights")
    r = client.post(f"/monitor/{uid}", json={"heart_rate": 72})
    assert r.status_code == 200, r.text
    handled = noticed.ledger(uid)
    assert [n["condition"] for n in handled] == ["restless nights"]
    assert handled[0]["settled_by"] == "coach"
    assert errands.spent_today(uid) == 0, "the free half spent nothing"


def test_without_the_permit_the_traffic_winds_nothing(client):
    """The person said nothing may run unattended, and honoring that
    silently IS the honoring — no rows, and no refusal into a background
    task nobody can hear."""
    uid = enroll(client)
    _detect(uid, condition="restless nights")
    _store(uid, "restless nights")
    r = client.post(f"/monitor/{uid}", json={"heart_rate": 72})
    assert r.status_code == 200, r.text
    assert noticed.ledger(uid) == []


def test_a_failing_pass_never_breaks_the_door_it_rides(client, monkeypatch):
    """A band posting a pulse must never learn that an unattended nicety
    behind its door fell over."""
    uid = enroll(client)
    _allow(client, uid)
    _detect(uid, condition="restless nights")

    def falls_over(*a, **k):
        raise RuntimeError("the nicety fell over")

    monkeypatch.setattr(noticed, "run", falls_over)
    r = client.post(f"/monitor/{uid}", json={"heart_rate": 72})
    assert r.status_code == 200, r.text


def test_every_door_where_work_is_born_winds_the_pass():
    """Checked in the source, per door: the winding is only autonomous if it
    rides EVERY door its work is born at — four kinds of detection traffic
    and the coach turn where knowledge gaps come from. A door that forgot
    is a day that quietly stops handling itself for people who only use
    that door."""
    from pathlib import Path

    import jim.api as api_mod

    src = Path(api_mod.__file__).read_text(encoding="utf-8")
    for door in ('"/monitor/{user_id}"', '"/checkin/{user_id}"',
                 '"/journal/{user_id}"', '"/activity/{user_id}"',
                 '"/coach/{user_id}"'):
        # Without the closing paren: three of these doors carry a
        # status_code in the same decorator.
        at = src.index(f"@app.post({door}")
        block = src[at:src.index("@app.", at + 1)]
        assert "noticed.after_traffic" in block, (
            f"the {door} door takes traffic the ladder feeds on and does "
            "not wind it")


def test_the_study_half_rides_the_same_traffic_behind_its_own_permit(
        client, monkeypatch):
    """Both halves wind, each behind its own yes — the two-switch split is
    about what leaves, and a person who allowed study and not handling gets
    exactly the half they allowed."""
    uid = enroll(client)
    _allow(client, uid, permit=errands.PERMIT)

    studied = []
    monkeypatch.setattr(errands, "due",
                        lambda user_id, limit=errands.DAILY:
                        [{"topic": "sleep", "area": "health_fitness",
                          "why": "for the test"}][:limit])
    monkeypatch.setattr(errands, "run",
                        lambda user_id, cloud=None, limit=errands.DAILY,
                        pdi=None: studied.append(user_id))
    r = client.post(f"/monitor/{uid}", json={"heart_rate": 72})
    assert r.status_code == 200, r.text
    assert studied == [uid], "the study half did not ride the traffic"
    # And the handling half, unpermitted, stayed home.
    assert noticed.ledger(uid) == []
