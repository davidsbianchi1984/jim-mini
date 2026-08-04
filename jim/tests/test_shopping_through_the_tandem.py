"""Shopping through the tandem, on the buyer's terms.

## The finding

QRME grew shops — standalone storefronts, deliberately not desks — and the
tandem contract already gives every JIM user a QRME interactor. What did
not exist was the buyer's side: JIM had no way to browse the shops, no way
to place an order as the user, and nowhere to keep the receipt that did
not amount to asking QRME to keep it.

    asked     can QRME sell things
    mattered  can a JIM user buy them without growing a profile elsewhere

## The four rules of jim/shopping.py, driven from the outside

1. browsing is anonymous — the catalog is read over public routes and an
   unreachable tandem is an empty shelf, never an error;
2. ordering is the interactor's act — signed with the same token the
   tandem chat runs on, one identity to revoke;
3. the history is held HERE — receipts live in JIM's own table, and this
   file *proves the negative*: no request ever asks QRME for the buyer's
   order list;
4. labels ride the view in the reader's language, because the console has
   no translation table of its own.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from jim import db


class _Resp:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class FakeShopQRME:
    """QRME's shop surface at the HTTP-client boundary — and a log of every
    path asked, because rule 3 is a claim about what is *not* requested."""

    def __init__(self):
        self.asked: list[str] = []
        self.orders: dict[str, dict] = {}
        self._n = 0

    def get(self, path, headers=None):
        self.asked.append(path)
        if path.startswith("/shops/shp_1"):
            return _Resp(200, {
                "id": "shp_1", "name": "Marta's Candles", "blurb": None,
                "seller": "Marta", "offerings": [
                    {"id": "off_1", "shop_id": "shp_1", "kind": "goods",
                     "title": "Beeswax pillar", "blurb": None, "price": 18.0,
                     "currency": "USD", "availability": "in_stock",
                     "retired": 0}]})
        if path.startswith("/shops"):
            return _Resp(200, [
                {"id": "shp_1", "name": "Marta's Candles", "seller": "Marta",
                 "tag": "crafts", "offerings": 1}])
        return _Resp(404, {})

    def post(self, path, json=None, headers=None):
        self.asked.append(path)
        if path == "/interactors":
            self._n += 1
            return _Resp(201, {"id": f"usr_fake{self._n}",
                               "token": f"itk_fake{self._n}"})
        if path == "/shops/shp_1/orders":
            auth = (headers or {}).get("authorization", "")
            if not auth.startswith("Bearer itk_"):
                return _Resp(401, {"detail": "no token"})
            order_id = f"ord_{len(self.orders) + 1}"
            self.orders[order_id] = {"status": "placed"}
            return _Resp(201, {
                "id": order_id, "shop_id": "shp_1", "offering_id": "off_1",
                "buyer_id": (json or {}).get("buyer_id"),
                "quantity": (json or {}).get("quantity", 1),
                "amount": 18.0 * (json or {}).get("quantity", 1),
                "currency": "USD", "status": "placed",
                "title": "Beeswax pillar", "kind": "goods"})
        if "/advance" in path:
            order_id = path.split("/")[-2]
            if order_id in self.orders:
                self.orders[order_id]["status"] = (json or {}).get("to")
                return _Resp(200, {"id": order_id, "shop_id": "shp_1",
                                   "status": (json or {}).get("to"),
                                   "title": "Beeswax pillar",
                                   "kind": "goods", "offering_id": "off_1",
                                   "buyer_id": "x", "quantity": 1,
                                   "amount": 18.0, "currency": "USD"})
            return _Resp(404, {})
        return _Resp(404, {})


@pytest.fixture()
def tandem(tmp_path, monkeypatch):
    monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
    monkeypatch.setenv("JIM_LLM", "stub")
    db.reset()
    from jim.api import create_app
    from jim.qrme_client import QRMEClient

    fake = FakeShopQRME()
    tc = TestClient(create_app(qrme_client=QRMEClient(client=fake)))
    tc.__enter__()
    yield tc, fake
    tc.__exit__(None, None, None)
    db.reset()


def _user(client):
    r = client.post("/enroll", json={"display_name": "Vera",
                                     "birthdate": "1979-04-02",
                                     "terms_consent": True})
    assert r.status_code == 201, r.text
    u = r.json()
    client.headers["authorization"] = f"Bearer {u['user_token']}"
    return u


# --- rule 1: the shelf --------------------------------------------------------

def test_the_shelf_lists_qrme_shops(tandem):
    client, _ = tandem
    u = _user(client)
    view = client.get(f"/shopping/{u['id']}").json()
    assert [s["name"] for s in view["shops"]] == ["Marta's Candles"]


def test_no_tandem_is_an_empty_shelf_not_an_error(client):
    """The standalone fixture: app.state.qrme is None."""
    u = client.post("/enroll", json={"display_name": "Solo",
                                     "birthdate": "1979-04-02",
                                     "terms_consent": True}).json()
    client.headers["authorization"] = f"Bearer {u['user_token']}"
    r = client.get(f"/shopping/{u['id']}")
    assert r.status_code == 200
    assert r.json()["shops"] == []
    # And ordering refuses with a sentence, not a stack trace.
    r = client.post(f"/shopping/{u['id']}/order",
                    json={"shop_id": "shp_1", "offering_id": "off_1"})
    assert r.status_code == 422
    assert "tandem" in r.json()["detail"]


# --- rule 2: the interactor's act --------------------------------------------

def test_an_order_is_signed_with_the_interactor_token(tandem):
    client, fake = tandem
    u = _user(client)
    r = client.post(f"/shopping/{u['id']}/order",
                    json={"shop_id": "shp_1", "offering_id": "off_1",
                          "quantity": 2})
    assert r.status_code == 201, r.text
    placed = r.json()
    assert placed["status"] == "placed" and placed["amount"] == 36.0
    # The fake refused unsigned orders, so reaching `placed` proves the
    # token went with it — and the link row shows whose it was.
    link = db.connect().execute(
        "SELECT * FROM tandem_links WHERE user_id=?", (u["id"],)).fetchone()
    assert link is not None and link["qrme_interactor_token"]


def test_one_identity_to_revoke_not_two(tandem):
    """Ordering reuses the tandem interactor rather than minting a shopper —
    the docs/tandem.md promise, held on a new surface."""
    client, fake = tandem
    u = _user(client)
    client.post(f"/shopping/{u['id']}/order",
                json={"shop_id": "shp_1", "offering_id": "off_1"})
    client.post(f"/shopping/{u['id']}/order",
                json={"shop_id": "shp_1", "offering_id": "off_1"})
    assert fake.asked.count("/interactors") == 1, (
        "a second interactor was minted for shopping")


# --- rule 3: the history is held here ----------------------------------------

def test_receipts_live_in_jim_and_qrme_is_never_asked(tandem):
    client, fake = tandem
    u = _user(client)
    client.post(f"/shopping/{u['id']}/order",
                json={"shop_id": "shp_1", "offering_id": "off_1"})
    view = client.get(f"/shopping/{u['id']}").json()
    assert len(view["receipts"]) == 1
    assert view["receipts"][0]["title"] == "Beeswax pillar"
    # The negative that is the rule: no request ever asked QRME for the
    # buyer's order list.
    assert not any("/orders/of/" in p for p in fake.asked), fake.asked


def test_cancel_while_placed_updates_the_receipt(tandem):
    client, fake = tandem
    u = _user(client)
    placed = client.post(f"/shopping/{u['id']}/order",
                         json={"shop_id": "shp_1",
                               "offering_id": "off_1"}).json()
    r = client.post(f"/shopping/{u['id']}/cancel",
                    json={"qrme_order_id": placed["id"]})
    assert r.status_code == 200, r.text
    view = client.get(f"/shopping/{u['id']}").json()
    assert view["receipts"][0]["status"] == "cancelled"


def test_cancelling_an_order_not_in_your_history_is_refused(tandem):
    client, _ = tandem
    u = _user(client)
    r = client.post(f"/shopping/{u['id']}/cancel",
                    json={"qrme_order_id": "ord_nothere"})
    assert r.status_code == 422
    assert "history" in r.json()["detail"]


# --- rule 4: the labels ------------------------------------------------------

def test_the_shelf_carries_its_own_labels(tandem):
    client, _ = tandem
    u = _user(client)
    client.put(f"/language/{u['id']}", json={"language": "ja"})
    view = client.get(f"/shopping/{u['id']}").json()
    assert view["labels"]["title"] == "ショップ"
    assert "QRME" in view["note"]
