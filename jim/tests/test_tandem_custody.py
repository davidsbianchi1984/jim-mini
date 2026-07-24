"""Provable custody for tandem specialist chats: when both tandems are
configured, every exchange with a QRME specialist profile is sealed into
the PDI vault under a jim/ key — attributed, hash-chained, erasable."""

import json

import pytest
from fastapi.testclient import TestClient

from jim import conditions
from jim import db as jim_db
from jim.tests.conftest import FakeQRME, _Resp, enroll
from jim.tests.test_pdi_tandem import FakePDIHttp


@pytest.fixture()
def triple(tmp_path, monkeypatch):
    """JIM wired to both tandems: a FakeQRME and a FakePDI."""
    monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
    monkeypatch.setenv("JIM_LLM", "stub")
    jim_db.reset()
    from jim.api import create_app
    from jim.pdi_client import PDIClient
    from jim.qrme_client import QRMEClient

    fake_pdi = FakePDIHttp()
    with TestClient(create_app(
            qrme_client=QRMEClient(client=FakeQRME()),
            pdi_client=PDIClient(token="pdi_test", client=fake_pdi))) as c:
        yield c, fake_pdi
    jim_db.reset()


def _wire(jim):
    jim.post("/specialists/seed")
    jim.post("/specialists/seed/tandem")


def test_tandem_exchange_sealed_in_the_vault(triple):
    jim, fake = triple
    _wire(jim)
    user = enroll(jim)
    g = jim.post(f"/monitor/{user}",
                 json={"note": "I lost my job and can't pay rent"}
                 ).json()["guidance"]
    assert g["source"] == "tandem"
    custody = g["custody"]
    assert custody["vaulted"] is True
    assert custody["pdi_key"].startswith(f"jim/{user}/tandem/prf_marcus_bell/")

    sealed = json.loads(fake.store[custody["pdi_key"]])
    assert sealed["condition"] == conditions.FINANCIAL_STRESS
    assert "[Guardian monitoring]" in sealed["message"]
    assert sealed["reply"] == g["content"]
    assert "Marcus Bell" in sealed["specialist"]


def test_local_guidance_has_no_custody_record(triple):
    jim, fake = triple
    _wire(jim)
    user = enroll(jim)
    g = jim.post(f"/monitor/{user}",
                 json={"rhythm": "fibrillation"}).json()["guidance"]
    assert g["source"] == "local"                # cardiac stays local
    assert "custody" not in g
    assert not any("/tandem/" in k for k in fake.store)


def test_erasure_purges_sealed_exchanges(triple):
    jim, fake = triple
    _wire(jim)
    user = enroll(jim)
    jim.post(f"/monitor/{user}", json={"note": "drowning in debt"})
    assert any("/tandem/" in k for k in fake.store)
    jim.delete(f"/data/{user}")
    assert fake.store == {}                      # right-to-erasure reaches PDI


def test_vault_outage_never_costs_the_user_guidance(tmp_path, monkeypatch):
    monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
    monkeypatch.setenv("JIM_LLM", "stub")
    jim_db.reset()
    from jim.api import create_app
    from jim.pdi_client import PDIClient
    from jim.qrme_client import QRMEClient

    class FlakyPDI(FakePDIHttp):
        """Healthy for the medical event stream, down for custody seals —
        isolates the new sealing path's failure handling."""

        def put(self, path, json=None, headers=None):
            if "/tandem/" in json["key"]:
                return _Resp(503, {"detail": "vault unavailable"})
            return super().put(path, json=json, headers=headers)

    with TestClient(create_app(
            qrme_client=QRMEClient(client=FakeQRME()),
            pdi_client=PDIClient(token="pdi_test", client=FlakyPDI()))) as jim:
        _wire(jim)
        user = enroll(jim)
        g = jim.post(f"/monitor/{user}",
                     json={"note": "totally broke, rent is due"}
                     ).json()["guidance"]
        assert g["source"] == "tandem" and g["delivered"] is True
        assert g["custody"]["vaulted"] is False
        assert "not sealed" in g["custody"]["note"]
    jim_db.reset()
