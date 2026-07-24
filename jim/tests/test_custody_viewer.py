"""The custody viewer: a user can list their sealed tandem exchanges and
read PDI's provenance for each — origin, seal, audit trail, chain status —
through JIM, scoped strictly to their own records."""

import pytest
from fastapi.testclient import TestClient

from jim import db as jim_db
from jim.tests.conftest import FakeQRME, _Resp, enroll
from jim.tests.test_pdi_tandem import FakePDIHttp

ORIGIN = "JIM Guardian (sealed via the JIM tandem client)"


class ProvenancePDI(FakePDIHttp):
    """FakePDI that also answers /provenance and /audit/verify, mirroring
    the real PDI's shapes."""

    def get(self, path, headers=None):
        if path.startswith("/provenance/"):
            key = path[len("/provenance/"):]
            if key not in self.store:
                return _Resp(404, {"detail": "record not found"})
            return _Resp(200, {
                "key": key, "origin": ORIGIN,
                "sealed": {"cipher": "AES-256-GCM (envelope encryption)"},
                "audit": {"count": 1}, "chain": {"intact": True}})
        if path == "/audit/verify":
            return _Resp(200, {"intact": True})
        return super().get(path, headers)


@pytest.fixture()
def triple(tmp_path, monkeypatch):
    monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
    monkeypatch.setenv("JIM_LLM", "stub")
    jim_db.reset()
    from jim.api import create_app
    from jim.pdi_client import PDIClient
    from jim.qrme_client import QRMEClient

    fake_pdi = ProvenancePDI()
    with TestClient(create_app(
            qrme_client=QRMEClient(client=FakeQRME()),
            pdi_client=PDIClient(token="pdi_test", client=fake_pdi))) as c:
        yield c, fake_pdi
    jim_db.reset()


def _sealed_exchange(jim):
    jim.post("/specialists/seed")
    jim.post("/specialists/seed/tandem")
    user = enroll(jim)
    g = jim.post(f"/monitor/{user}",
                 json={"note": "I lost my job and can't pay rent"}
                 ).json()["guidance"]
    return user, g["custody"]["pdi_key"]


def test_custody_lists_sealed_exchanges_with_chain_status(triple):
    jim, _ = triple
    user, key = _sealed_exchange(jim)
    out = jim.get(f"/custody/{user}").json()
    assert out["count"] == 1 and out["records"] == [key]
    assert out["chain_intact"] is True
    # Medical event keys are vaulted too, but they are not custody records.
    assert all("/tandem/" in k for k in out["records"])


def test_custody_provenance_reads_the_pdi_trail(triple):
    jim, _ = triple
    user, key = _sealed_exchange(jim)
    p = jim.get(f"/custody/{user}/provenance", params={"key": key}).json()
    assert p["origin"] == ORIGIN
    assert p["chain"]["intact"] is True
    assert "AES-256-GCM" in p["sealed"]["cipher"]


def test_custody_provenance_is_scoped_to_own_records(triple):
    jim, _ = triple
    user, key = _sealed_exchange(jim)
    # A key outside the user's tandem namespace (their own medical event)
    # is not a custody record; a foreign key 404s the same way.
    events = jim.get(f"/events/{user}").json()
    medical_key = next(e["detail"]["pdi_key"] for e in events
                       if e["type"] == "biometric")
    r = jim.get(f"/custody/{user}/provenance", params={"key": medical_key})
    assert r.status_code == 404
    r = jim.get(f"/custody/{user}/provenance",
                params={"key": "jim/usr_other/tandem/prf_x/txc_1"})
    assert r.status_code == 404


def test_custody_without_pdi_conflicts(client):
    user = enroll(client)
    r = client.get(f"/custody/{user}")
    assert r.status_code == 409
    assert "JIM_PDI_URL" in r.json()["detail"]
