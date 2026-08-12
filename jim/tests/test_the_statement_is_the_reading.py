"""Money guardian statements and bank links (jim/money.py).

The statement file is sealed like account credentials — the vault or
nowhere — and read by deterministic local arithmetic, never a model. When
it closes with a balance, that balance walks the same observe path a
hand-typed reading takes, so the guardian ladder wakes off the file
itself. A bank link is a written aggregator consent whose status never
claims data that was not pulled. This deployment has no vault at the
door, so the working paths are proven at the module with a fake vault —
exactly as the guardian's own credential tests do.
"""

import base64

from jim import money
from jim.tests.conftest import enroll


class _FakeVault:
    def __init__(self):
        self.sealed: dict[str, str] = {}

    def put(self, key, value):
        self.sealed[key] = value

    def get(self, key):
        return self.sealed.get(key)


_CSV = ("date,description,amount,balance\n"
        "2026-08-01,salary,2400.00,2650.00\n"
        "2026-08-03,rent,-1200.00,1450.00\n"
        "2026-08-05,groceries,-84.50,1365.50\n")


def test_the_statement_reads_locally_and_wakes_the_ladder(client):
    user = enroll(client)
    vault = _FakeVault()
    account = money.add_account(user, "checking", "First Street Bank",
                                "Everyday", None, None, None, pdi=vault)
    reading = money.drop_statement(
        user, account["id"], "august.csv",
        base64.b64encode(_CSV.encode()).decode(), "en", pdi=vault)
    assert reading["statement_sealed"] is True
    assert reading["line_count"] == 3
    assert reading["total_in"] == 2400.0
    assert reading["total_out"] == 1284.5
    assert reading["end_balance"] == 1365.5
    # The raw file went to the vault, whole.
    assert any("groceries" in base64.b64decode(v).decode()
               for v in vault.sealed.values())
    # The closing balance walked the observe path — recorded, interpreted.
    assert reading["observed"]["recorded"] is True

    # The shelf shows the readings, never the files.
    shelf = client.get(f"/money/{user}/statements").json()
    assert len(shelf) == 1 and shelf[0]["filename"] == "august.csv"
    assert "content" not in shelf[0]


def test_the_statement_needs_the_vault_at_the_door(client):
    user = enroll(client)
    r = client.post(f"/money/{user}/accounts", json={
        "kind": "checking", "institution": "First Street Bank"})
    account = r.json()
    r = client.post(f"/money/{user}/statements", json={
        "account_id": account["id"],
        "content": base64.b64encode(b"a,b,c").decode()})
    assert r.status_code == 422
    assert "vault" in r.json()["detail"]


def test_the_link_is_a_consent_and_the_sync_tells_the_truth(client):
    user = enroll(client)
    vault = _FakeVault()
    link = money.link_bank(user, "First Street Bank", "plaid", pdi=vault)
    # The consent stands; no data was claimed.
    assert link["status"] == "consented"

    links = client.get(f"/money/{user}/links").json()
    assert len(links) == 1
    # The link registered a watchable account under the guardian.
    accounts = client.get(f"/money/{user}").json()["accounts"]
    assert any(a["id"] == link["account_id"] for a in accounts)

    # No aggregator credentials on this deployment: the sync refuses with
    # the truth instead of inventing balances.
    r = client.post(f"/money/{user}/links/{link['id']}/sync")
    assert r.status_code == 422
    assert "no plaid credentials" in r.json()["detail"]

    # Taking your hands back is never gated — and needs no vault.
    r = client.request("DELETE", f"/money/{user}/links/{link['id']}")
    assert r.status_code == 200
    assert r.json()["status"] == "revoked"
    r = client.post(f"/money/{user}/links/{link['id']}/sync")
    assert r.status_code == 422
    assert "revoked" in r.json()["detail"]


def test_the_link_door_refuses_without_a_vault_and_strange_aggregators(client):
    user = enroll(client)
    r = client.post(f"/money/{user}/links", json={
        "institution": "First Street Bank", "aggregator": "plaid"})
    assert r.status_code == 422
    assert "vault" in r.json()["detail"]

    r = client.post(f"/money/{user}/links", json={
        "institution": "First Street Bank", "aggregator": "moonshot"})
    assert r.status_code == 422
    assert "plaid" in r.json()["detail"]
