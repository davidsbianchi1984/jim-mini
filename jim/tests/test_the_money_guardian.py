"""The Guardian watched spending and could not hold the money.

## The finding

JIM already watched money the way it watches sleep: consented spending
events fill budget tallies, `life._budget_insights` warns at 80% and 100%,
`forecast_spending` projects the month, and the finance coach hands a
question to Marcus Bell through the tandem. But there was nowhere to put an
account — checking, savings, brokerage, crypto — so there was no balance to
watch, no cushion to warn about, no savings goal to coach toward, and
nothing to invest.

    asked     is spending watched
    mattered  is the money watched

## What this file drives

The four rules of `jim/money.py`, each from the outside:

1. credentials are vaulted or refused — never stored in the clear, never
   echoed back;
2. a low balance is a `checkin`-severity guardian event and an insight —
   the proactive ladder, never an emergency escalation;
3. the mandate is a written, Pro-gated, revocable handover, and its orders
   are logged *proposals*;
4. a warning carries its doors — the coach, the tandem specialist, and
   real desks when the tandem is up.
"""

from __future__ import annotations

import pytest

from jim import db, money


def _user(client, plan="basic"):
    r = client.post("/enroll", json={"display_name": "Vera",
                                     "birthdate": "1979-04-02",
                                     "terms_consent": True})
    assert r.status_code == 201, r.text
    u = r.json()
    client.headers["authorization"] = f"Bearer {u['user_token']}"
    if plan:
        r = client.post(f"/memberships/{u['id']}", json={"plan": plan})
        assert r.status_code == 200, r.text
    return u


class _FakeVault:
    """Records what was sealed, so a test can prove the numbers went to the
    vault and nowhere else."""

    def __init__(self):
        self.sealed: dict[str, str] = {}

    def put(self, key, value):
        self.sealed[key] = value

    def get(self, key):
        return self.sealed.get(key)


# --- rule 1: vault or refused ------------------------------------------------

def test_credentials_are_refused_without_a_vault(client):
    u = _user(client, plan=None)          # visitor: no vault
    r = client.post(f"/money/{u['id']}/accounts", json={
        "kind": "checking", "institution": "First Street Bank",
        "account_number": "000123456789", "routing_number": "021000021"})
    assert r.status_code == 422, r.text
    assert "vault" in r.json()["detail"]
    row = db.connect().execute(
        "SELECT COUNT(*) AS n FROM money_accounts").fetchone()
    assert row["n"] == 0, "the account was stored despite the refusal"


def test_the_numbers_go_to_the_vault_and_never_come_back(client, monkeypatch):
    u = _user(client)
    vault = _FakeVault()
    monkeypatch.setattr("jim.storage.vault_for", lambda *a, **k: vault) \
        if hasattr(__import__("jim.storage", fromlist=["x"]), "vault_for") \
        else None
    made = money.add_account(
        u["id"], "checking", "First Street Bank", "Everyday",
        "000123456789", "021000021", None, pdi=vault)
    assert made["credentials"] == "vaulted"
    assert made["last4"] == "6789"
    # Sealed, whole, in the vault:
    assert any("000123456789" in v for v in vault.sealed.values())
    # And nowhere in JIM's own database:
    for table in ("money_accounts", "money_balances"):
        for row in db.connect().execute(f"SELECT * FROM {table}").fetchall():
            joined = " ".join(str(v) for v in dict(row).values())
            assert "000123456789" not in joined, (
                f"the account number leaked into {table}")
            assert "021000021" not in joined, (
                f"the routing number leaked into {table}")
    # The read path never carries it either.
    view = client.get(f"/money/{u['id']}").json()
    assert "000123456789" not in str(view)


def test_an_account_without_numbers_needs_no_vault(client):
    """A visitor can still budget by hand — refusing the *account* rather
    than the *numbers* would gate the whole feature on a plan."""
    u = _user(client, plan=None)
    r = client.post(f"/money/{u['id']}/accounts", json={
        "kind": "savings", "institution": "Mattress Bank"})
    assert r.status_code == 201, r.text
    assert r.json()["credentials"] == "none"


# --- rule 2: the proactive ladder --------------------------------------------

def _account(client, uid, kind="checking"):
    r = client.post(f"/money/{uid}/accounts",
                    json={"kind": kind, "institution": "First Street"})
    assert r.status_code == 201, r.text
    return r.json()


def test_a_low_balance_is_noticed_out_loud(client):
    u = _user(client)
    acc = _account(client, u["id"])
    r = client.post(f"/money/{u['id']}/observe",
                    json={"account_id": acc["id"], "balance": 40})
    assert r.status_code == 200, r.text
    warnings = r.json()["warnings"]
    assert any(w["kind"] == "low_balance" for w in warnings), warnings
    low = next(w for w in warnings if w["kind"] == "low_balance")
    # The warning is a sentence with the numbers in it, not a flag.
    assert "40" in low["message"]
    # And it landed on the ladder: a guardian event at checkin severity.
    ev = db.connect().execute(
        "SELECT * FROM events WHERE user_id=? AND type='money_low'",
        (u["id"],)).fetchone()
    assert ev is not None, "no guardian event — the warning never reached the ladder"
    assert ev["severity"] == "checkin", dict(ev)


def test_money_never_climbs_past_checkin(client):
    """Rule 2's hard line: an overdraft is not a collapse. However low the
    balance, the event severity stays `checkin` and no escalation row is
    written."""
    u = _user(client)
    acc = _account(client, u["id"])
    client.post(f"/money/{u['id']}/observe",
                json={"account_id": acc["id"], "balance": -5000})
    rows = db.connect().execute(
        "SELECT severity FROM events WHERE user_id=? AND type='money_low'",
        (u["id"],)).fetchall()
    assert rows and all(r["severity"] == "checkin" for r in rows)


def test_a_healthy_balance_raises_nothing(client):
    u = _user(client)
    acc = _account(client, u["id"])
    r = client.post(f"/money/{u['id']}/observe",
                    json={"account_id": acc["id"], "balance": 5000})
    assert r.json()["warnings"] == []


def test_reaching_the_savings_goal_is_celebrated_once(client):
    u = _user(client)
    acc = _account(client, u["id"], kind="savings")
    r = client.put(f"/money/{u['id']}/savings", json={"goal": 1000})
    assert r.status_code == 200, r.text
    first = client.post(f"/money/{u['id']}/observe",
                        json={"account_id": acc["id"], "balance": 1200})
    kinds = [w["kind"] for w in first.json()["warnings"]]
    assert "goal_reached" in kinds, first.json()
    again = client.post(f"/money/{u['id']}/observe",
                        json={"account_id": acc["id"], "balance": 1300})
    assert "goal_reached" not in [w["kind"] for w in again.json()["warnings"]]


def test_the_warning_speaks_the_users_language(client):
    u = _user(client)
    r = client.put(f"/language/{u['id']}", json={"language": "pt"})
    assert r.status_code == 200, r.text
    acc = _account(client, u["id"])
    low = client.post(f"/money/{u['id']}/observe",
                      json={"account_id": acc["id"], "balance": 12}).json()
    message = low["warnings"][0]["message"]
    assert "almofada" in message, message      # pt for "cushion"


# --- rule 3: the mandate ------------------------------------------------------

MANDATE = {"enabled": True, "cap_per_order": 500, "monthly_cap": 1000,
           "asset_classes": ["index_funds"], "scope":
           "Sweep spare cash above my cushion into index funds only."}


def test_the_handover_is_pro_gated_and_the_revoke_is_not(client):
    u = _user(client, plan="basic")
    r = client.put(f"/money/{u['id']}/mandate", json=MANDATE)
    assert r.status_code == 402, r.text       # the tier that buys it, named
    r = client.put(f"/money/{u['id']}/mandate", json={"enabled": False})
    assert r.status_code == 200, (
        "revoking must never be gated — taking your hands back has no price")


def test_an_enabled_mandate_needs_the_words_and_the_caps(client):
    u = _user(client, plan="pro")
    for broken, needle in ((dict(MANDATE, scope=""), "scope"),
                           (dict(MANDATE, cap_per_order=0), "caps"),
                           (dict(MANDATE, asset_classes=["memecoins"]),
                            "asset class")):
        r = client.put(f"/money/{u['id']}/mandate", json=broken)
        assert r.status_code == 422, (needle, r.text)
        assert needle in r.json()["detail"], r.text


def test_jim_invests_only_inside_the_mandate(client):
    """The whole feature, driven: spare cash above the cushion becomes a
    *proposed* order in the mandated class, capped per order — and nothing
    claims execution, because there is nothing to execute with."""
    u = _user(client, plan="pro")
    acc = _account(client, u["id"])
    assert client.put(f"/money/{u['id']}/mandate",
                      json=MANDATE).status_code == 200
    r = client.post(f"/money/{u['id']}/observe",
                    json={"account_id": acc["id"], "balance": 2000})
    orders = r.json()["orders_proposed"]
    assert len(orders) == 1, r.json()
    order = orders[0]
    assert order["asset_class"] == "index_funds"
    assert order["status"] == "proposed"
    assert order["amount"] <= 500                    # cap_per_order
    assert order["rationale"], "an order with no reason is a black box"


def test_no_mandate_means_no_orders_however_much_cash(client):
    u = _user(client, plan="pro")
    acc = _account(client, u["id"])
    r = client.post(f"/money/{u['id']}/observe",
                    json={"account_id": acc["id"], "balance": 100000})
    assert r.json()["orders_proposed"] == [], (
        "JIM proposed an investment with no mandate written")


def test_the_monthly_cap_holds_across_orders(client):
    u = _user(client, plan="pro")
    acc = _account(client, u["id"])
    client.put(f"/money/{u['id']}/mandate", json=MANDATE)
    total = 0.0
    for balance in (2000, 2000, 2000, 2000):
        r = client.post(f"/money/{u['id']}/observe",
                        json={"account_id": acc["id"], "balance": balance})
        total += sum(o["amount"] for o in r.json()["orders_proposed"])
    assert total <= 1000, f"{total} proposed against a 1000 monthly cap"


def test_revoking_stops_the_next_order(client):
    u = _user(client, plan="pro")
    acc = _account(client, u["id"])
    client.put(f"/money/{u['id']}/mandate", json=MANDATE)
    client.put(f"/money/{u['id']}/mandate", json={"enabled": False})
    r = client.post(f"/money/{u['id']}/observe",
                    json={"account_id": acc["id"], "balance": 5000})
    assert r.json()["orders_proposed"] == []


# --- rule 4: the doors --------------------------------------------------------

def test_the_warning_carries_its_doors(client):
    u = _user(client)
    acc = _account(client, u["id"])
    low = client.post(f"/money/{u['id']}/observe",
                      json={"account_id": acc["id"], "balance": 10}).json()
    doors = low["warnings"][0]["doors"]
    assert doors["coach"], "the coach door is always there"
    # Standalone (no tandem): the desk list is empty rather than an error.
    assert doors["desks"] == []


def test_somebody_elses_account_is_not_observable(client):
    u = _user(client)
    acc = _account(client, u["id"])
    r = client.post("/enroll", json={"display_name": "Other",
                                     "birthdate": "1990-01-01",
                                     "terms_consent": True})
    other = r.json()
    client.headers["authorization"] = f"Bearer {other['user_token']}"
    r = client.post(f"/money/{other['id']}/observe",
                    json={"account_id": acc["id"], "balance": 0})
    assert r.status_code == 422, r.text
    assert "somebody else" in r.json()["detail"]


def test_the_overview_carries_its_own_labels(client):
    """The console renders what the server hands it — labels in the
    reader's language — because the console has no translation table of
    its own and its English backlog is a ratchet that only shrinks."""
    u = _user(client)
    client.put(f"/language/{u['id']}", json={"language": "ja"})
    view = client.get(f"/money/{u['id']}").json()
    assert view["labels"]["title"] == "マネー"
    assert "封印" in view["note"] or "金庫" in view["note"]
