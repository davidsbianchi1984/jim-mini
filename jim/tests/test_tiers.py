"""Membership: Basic, Pro, and the line no plan may stand in front of.

The first section is the one that matters. JIM-mini is a guardian for people
with known conditions, and the failure this module has to make impossible is a
paywall between somebody and an emergency. It is asserted rather than reviewed
because the failure is silent: a gate in front of an alarm looks exactly like a
gate in front of anything else until the day it matters, and on that day nobody
is reading the table.

The first implementation had that bug. `/monitor` was listed as the "proactive
monitoring" capability, which reads correctly and is wrong — `/monitor` is the
*ingest*, and a Basic member submitting a blood oxygen of 84 got a 402 instead
of an escalation. `test_a_critical_reading_escalates_on_the_cheapest_plan` is
the test that would have caught it, written here so it cannot come back.
"""

import pytest

from jim import tiers
from jim.tests.conftest import as_user, enroll, user_header


# -- the paywall never stands in front of an emergency ------------------------

def test_no_gated_pattern_can_reach_a_safety_path(client):
    """The two lists must not overlap. Checked through `capability_for`, so it
    tests what the gate *does* rather than comparing two regexes."""
    for path in tiers.NEVER_GATED_SAMPLES:
        for method in ("GET", "POST", "PUT", "DELETE"):
            assert tiers.capability_for(method, path) is None, (
                f"{method} {path} is gated, and it is on the never-gated list")


def test_the_safety_list_wins_even_when_a_gate_is_added_over_it(monkeypatch,
                                                                client):
    """The test above passes trivially while nothing gates those paths, which
    is exactly the state that lets somebody add a gate over one later and see
    nothing fail. This one plants that mistake and asserts the safety check
    still wins.

    A hostile pattern is added to GATED covering **every** path — the widest
    version of the accident — and every safety sample must still come back
    ungated, because `capability_for` consults the never-gated list first.
    """
    monkeypatch.setattr(
        tiers, "GATED", ((r"^/", "marketplace"),) + tiers.GATED)
    assert tiers.capability_for("POST", "/journal/usr_1") == "marketplace"
    for path in tiers.NEVER_GATED_SAMPLES:
        for method in ("GET", "POST", "PUT", "DELETE"):
            assert tiers.capability_for(method, path) is None, (
                f"a gate added over {method} {path} was not overridden by the "
                "safety list")


def test_every_safety_sample_is_matched_by_a_never_gated_pattern(client):
    """A sample nothing matches would pass the test above for the wrong
    reason — by being ungated anyway rather than by being protected."""
    for path in tiers.NEVER_GATED_SAMPLES:
        assert tiers.is_never_gated(path), f"{path} matches no NEVER_GATED rule"


def test_a_critical_reading_escalates_on_the_cheapest_plan(client):
    """The bug this module was written with and then corrected.

    A blood oxygen of 84 is a critical reading. On Basic it must produce an
    escalation, not a price.
    """
    user = enroll(client, plan="basic", emergency_name="Pat",
                  emergency_phone="+1-555-0199", contact_consent=True)
    r = client.post(f"/monitor/{user}", json={"blood_oxygen": 84})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["severity"] == "critical"
    assert body["escalation"] is not None


def test_the_emergency_path_works_with_no_membership_at_all(client):
    """Not merely on the cheap plan — with the subscription cancelled."""
    user = enroll(client, plan="basic", emergency_name="Pat",
                  emergency_phone="+1-555-0199", contact_consent=True)
    tiers.cancel(user)
    assert tiers.plan_of(user) == "visitor"

    r = client.post(f"/monitor/{user}", json={"blood_oxygen": 84})
    assert r.status_code == 200, r.text
    assert r.json()["severity"] == "critical"
    assert client.get(f"/users/{user}/alarms").status_code == 200


def test_the_pricing_page_says_the_emergency_path_is_never_withheld(client):
    """"Will this stop my alarm working" is the first question worth
    answering on a health product's price list, so it is answered without
    being asked."""
    page = client.get("/plans").json()
    assert "never withheld" in page["emergency"]
    assert page["never_gated"]
    assert "emergency" in tiers.CAPABILITIES
    assert tiers.entitles("basic", "emergency")


def test_a_refusal_says_the_emergency_path_is_unaffected(client):
    """Somebody who has just hit a paywall on a health app should not have to
    wonder whether they have also lost the alarm."""
    user = enroll(client, plan="basic")
    r = client.get(f"/insights/{user}")
    assert r.status_code == 402, r.text
    assert r.json()["detail"]["emergency_unaffected"] is True


# -- what Pro actually buys ----------------------------------------------------

def test_basic_is_the_guardian_and_pro_reaches_further(client):
    assert tiers.entitles("basic", "guardian")
    assert tiers.entitles("basic", "emergency")
    for capability in ("watch", "monitoring", "marketplace", "synthetic_agents"):
        assert not tiers.entitles("basic", capability), capability
        assert tiers.entitles("pro", capability), capability


def test_the_plans_are_the_prices_that_were_agreed(client):
    # The agreement changed on 2026-08-10: every plan is $0 while the beta
    # runs, with the returning prices named in each plan's own copy.
    assert tiers.PLANS["basic"]["price_usd"] == 0
    assert "beta" in tiers.PLANS["basic"]["means"]
    assert "$20" in tiers.PLANS["basic"]["means"]
    assert tiers.PLANS["pro"]["price_usd"] == 0
    assert "beta" in tiers.PLANS["pro"]["means"]
    assert "$130" in tiers.PLANS["pro"]["means"]
    assert tiers.PLANS["basic"]["period"] == "month"
    assert tiers.PLANS["pro"]["period"] == "month"


def test_the_watch_is_pro(client):
    """"Not the watch features" was the line drawn for Basic."""
    user = enroll(client, plan="basic")
    assert client.post(f"/devices/{user}",
                       json={"kind": "watch", "name": "wrist"}).status_code == 402
    assert client.put(f"/users/{user}/mic",
                      json={"device": "watch"}).status_code == 402


def test_early_warning_is_pro_but_the_reading_still_gets_an_answer(client):
    """Skipped rather than refused. A Basic member submitting a reading gets a
    real answer about *that* reading; they do not get the trend model looking
    ahead."""
    basic = enroll(client, plan="basic")
    r = client.post(f"/monitor/{basic}", json={"heart_rate": 72})
    assert r.status_code == 200, r.text
    assert r.json()["predictive"] is False
    assert r.json()["forecast"] is None

    pro = enroll(client, plan="pro")
    r = client.post(f"/monitor/{pro}", json={"heart_rate": 72})
    assert r.json()["predictive"] is True


def test_insights_are_gated_on_the_read(client):
    """The one place a GET is gated in these three products: an insight is not
    a shop window, it *is* the predictive product, and the only door it has."""
    assert tiers.capability_for("GET", "/insights/usr_1") == "monitoring"
    user = enroll(client, plan="basic")
    assert client.get(f"/insights/{user}").status_code == 402


def test_summoning_a_synthetic_agent_is_pro(client):
    user = enroll(client, plan="basic")
    r = client.post(f"/users/{user}/specialist-tasks",
                    json={"specialist_id": "spc_1", "goal": "help"})
    assert r.status_code == 402
    assert r.json()["detail"]["capability"] == "synthetic_agents"


# -- the table is bound to the routes ------------------------------------------

def _sample_paths(client) -> list[str]:
    import re

    return [re.sub(r"\{[^}]+\}", "x", p) for p in client.app.openapi()["paths"]]


def test_every_gated_pattern_is_a_route_that_exists(client):
    """A pattern nothing matches is a paywall in front of a wall: it reads as
    protection, protects nothing, and survives because nothing fails."""
    import re

    samples = _sample_paths(client)
    for pattern, _ in tiers.GATED:
        assert any(re.search(pattern, p) for p in samples), (
            f"{pattern} gates nothing — no served route matches it")


def test_every_never_gated_pattern_is_a_route_that_exists(client):
    """The same check on the safety list, and it matters more here: a
    misspelled pattern would silently protect nothing."""
    import re

    samples = _sample_paths(client)
    for pattern in tiers.NEVER_GATED:
        assert any(re.search(pattern, p) for p in samples), (
            f"{pattern} protects nothing — no served route matches it")


def test_every_gated_pattern_names_a_real_capability(client):
    for _pattern, capability in tiers.GATED:
        assert capability in tiers.CAPABILITIES


def test_the_named_exceptions_are_routes_that_exist(client):
    spec = client.app.openapi()
    for method, path in tiers.OPEN:
        assert path in spec["paths"], f"{path} is OPEN but is not a route"
        assert method.lower() in spec["paths"][path]


def test_what_a_plan_includes_is_computed_not_typed(client):
    page = client.get("/plans").json()
    for row in page["plans"]:
        assert row["includes"] == tiers.includes(row["plan"])
        assert set(row["includes"]) | set(row["locked"]) == set(tiers.CAPABILITIES)


# -- joining, moving, leaving --------------------------------------------------

def test_enrolling_puts_a_new_person_on_free(client):
    """And the response says what free means before they have written
    anything — see `test_storage_posture.py`. Nobody is asked for a card to
    reach the Guardian; what $20 buys is the vault."""
    r = client.post("/enroll", json={"display_name": "Sam",
                                     "birthdate": "1990-01-01",
                                     "terms_consent": True})
    assert r.status_code == 201, r.text
    membership = r.json()["membership"]
    assert membership["plan"] == "free"
    assert membership["storage"]["not_private"] is True


def test_moving_plan_replaces_rather_than_stacks(client):
    user = enroll(client, plan="basic")
    client.post(f"/memberships/{user}", json={"plan": "pro"})
    from jim import db

    live = db.connect().execute(
        "SELECT COUNT(*) AS n FROM memberships WHERE account_id=? AND"
        " ended_at IS NULL", (user,)).fetchone()["n"]
    assert live == 1 and tiers.plan_of(user) == "pro"


def test_cancelling_keeps_the_record_and_the_conditions(client):
    """A lapsed subscription must not quietly remove somebody's ability to
    call for help, or their history."""
    user = enroll(client, plan="pro")
    client.delete(f"/memberships/{user}")
    assert tiers.plan_of(user) == "visitor"
    assert client.get(f"/users/{user}/incidents").status_code == 200


def test_an_unknown_plan_is_refused(client):
    user = enroll(client)
    assert client.post(f"/memberships/{user}",
                       json={"plan": "platinum"}).status_code == 422
    with pytest.raises(tiers.TierError):
        tiers.subscribe(user, "visitor")


def test_somebody_elses_membership_is_not_yours_to_read_or_cancel(client):
    mine = enroll(client, plan="pro")
    my_token = client.headers["authorization"].split()[1]
    theirs = enroll(client, plan="basic")
    del theirs

    as_user(client, my_token)
    other = enroll(client, plan="basic", display_name="Rae")
    as_user(client, my_token)
    assert client.get(f"/memberships/{other}").status_code == 403
    assert client.delete(f"/memberships/{other}").status_code == 403
    assert tiers.plan_of(other) == "basic"


# -- the money is simulated ----------------------------------------------------

def test_every_money_bearing_response_discloses_the_simulation(client):
    user = enroll(client, plan="basic")
    assert "simulated" in client.get("/plans").json()["billing"]
    assert "simulated" in client.get(
        f"/memberships/{user}").json()["billing"]
    refused = client.get(f"/insights/{user}")
    assert refused.status_code == 402
    assert "simulated" in refused.json()["detail"]["billing"]


def test_nothing_here_reaches_a_payment_processor(client):
    import inspect

    src = inspect.getsource(tiers).lower()
    for real in ("stripe", "paypal", "braintree", "charge(", "http://",
                 "https://"):
        assert real not in src, f"{real!r} appears in tiers.py"


def test_a_user_token_is_the_account(client):
    """Unlike QRME, where an owner token's subject is a profile and the
    account sits behind it."""
    user = enroll(client, plan="pro")
    import types

    fake = types.SimpleNamespace(
        method="GET", url=types.SimpleNamespace(path=f"/insights/{user}"),
        headers=user_header(client.headers["authorization"].split()[1]))
    assert tiers.account_of(fake) == user
