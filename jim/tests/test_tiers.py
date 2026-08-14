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


@pytest.fixture(autouse=True)
def _enforcing(monkeypatch):
    """Every test in this file asks what the gate does when it is enforcing.

    `tiers.BETA_EVERYTHING_INCLUDED` stands the gate down while the beta
    runs, and without this fixture that would quietly empty this whole file:
    every `== 402` would meet a 200 instead, and the temptation would be to
    soften the assertions until they matched. The mechanism has to stay
    covered *while* it is switched off, because the day it switches back on
    is the day it has to still work.

    `test_the_beta_stands_the_whole_gate_down` is the other half: it turns
    the flag back on and checks it does what it says.
    """
    monkeypatch.setattr(tiers, "BETA_EVERYTHING_INCLUDED", False)


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

def test_enrolling_puts_a_new_person_on_the_default_plan(client):
    """Which is Pro while the beta runs, and the response still says what
    that plan's storage posture means before they have written anything —
    see `test_storage_posture.py`.

    This asserted `free` for most of this product's life, and the reason it
    changed is worth keeping: nobody is asked for a card either way, both
    paid plans cost nothing during the beta, and a tester who never chose was
    landing on the bottom tier and meeting a paywall quoting a price of $0.
    Read against `tiers.DEFAULT_PLAN` rather than a literal, so the day that
    constant moves back this test moves with it instead of failing.
    """
    r = client.post("/enroll", json={"display_name": "Sam",
                                     "birthdate": "1990-01-01",
                                     "terms_consent": True})
    assert r.status_code == 201, r.text
    membership = r.json()["membership"]
    assert membership["plan"] == tiers.DEFAULT_PLAN
    from jim import storage
    assert membership["storage"]["not_private"] is (
        not storage.is_private(tiers.DEFAULT_PLAN))


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


# -- the beta stands the whole gate down --------------------------------------
#
# Everything above runs with `_enforcing` forcing the gate on, which is the
# state this product ships back to. These two are the other half: what a
# tester actually meets today.


def test_the_beta_stands_the_whole_gate_down(client, monkeypatch):
    """Both enforcement points, through the door a person actually meets.

    The first attempt at this stood `require` down and left `gate` — the
    application-wide chokepoint — refusing exactly as before. Every test in
    this file still passed, because none of them reach the gate through
    `require`. So this drives HTTP: a Free account, a Pro-only capability,
    and a 200.
    """
    monkeypatch.setattr(tiers, "BETA_EVERYTHING_INCLUDED", True)
    user = enroll(client, plan="free")
    assert tiers.plan_of(user) == "free"
    # Pro-only, and the one the field report arrived about.
    assert client.get("/engaged/reach").status_code == 200
    opened = client.post(f"/engaged/{user}", json={"area": "personal_growth"})
    assert opened.status_code != 402, opened.text
    # And the non-HTTP path, which is the one `require` guards.
    tiers.require(user, "synthetic_agents")


def test_standing_the_gate_down_does_not_rewrite_what_a_plan_means(client,
                                                                   monkeypatch):
    """The pricing page keeps telling the truth about what is being sold.

    `entitles` is what `/plans` reads, and it must go on answering about the
    plans as they will be charged for — a beta that reported everything as
    included in Free would be advertising a product that does not exist.
    """
    monkeypatch.setattr(tiers, "BETA_EVERYTHING_INCLUDED", True)
    assert tiers.entitles("free", "synthetic_agents") is False
    assert tiers.entitles("pro", "synthetic_agents") is True
    listed = client.get("/plans").json()["plans"]
    free = next(p for p in listed if p["plan"] == "free")
    assert "synthetic_agents" not in free["includes"]
    assert "synthetic_agents" in free["locked"]


def test_the_price_list_says_whether_the_gate_is_running(client, monkeypatch):
    """A reader can tell the price from the posture, and both are true.

    `locked` answers what a plan will cost. It cannot answer whether anybody
    is being refused today, and for one release nothing could: the beta
    stand-down was a module constant that no response mentioned.

    QRME's cross-product smoke is what found it. That run drives a Basic
    account into `synthetic_agents` and asserts the 402 — correct while the
    gate stands, wrong the moment it does not, and it had nowhere to ask.
    Every test in this file kept passing, because they all force the flag on.

        asked     does the price list say what a plan costs
        mattered  does it say whether the gate is running
    """
    monkeypatch.setattr(tiers, "BETA_EVERYTHING_INCLUDED", True)
    stood_down = client.get("/plans").json()
    assert stood_down["enforcing"] is False
    assert stood_down["beta_note"], "a stood-down gate says so in words"
    # And the prices are unchanged by it — the other half of the promise.
    free = next(p for p in stood_down["plans"] if p["plan"] == "free")
    assert "synthetic_agents" in free["locked"]

    monkeypatch.setattr(tiers, "BETA_EVERYTHING_INCLUDED", False)
    running = client.get("/plans").json()
    assert running["enforcing"] is True
    assert running["beta_note"] is None
