"""PDI tandem: JIM's sensitive payloads live in the encrypted vault.

Uses a FakePDI double at the HTTP-client boundary (same pattern as FakeQRME),
so the test exercises jim/pdi_client.py plus the vault paths without a running
PDI. For a full cross-service run, point JIM at a live PDI via
JIM_PDI_URL + JIM_PDI_TOKEN.
"""

import json

import pytest
from fastapi.testclient import TestClient

from jim import db as jim_db
from jim.tests.conftest import _Resp, enroll


class FakePDIHttp:
    """Implements the three PDI record endpoints over an in-memory dict."""

    def __init__(self):
        self.store = {}

    def put(self, path, json=None, headers=None):
        assert path == "/records"
        self.store[json["key"]] = json["value"]
        return _Resp(200, {"key": json["key"]})

    def get(self, path, headers=None):
        key = path[len("/records/"):]
        if key in self.store:
            return _Resp(200, {"key": key, "value": self.store[key]})
        return _Resp(404, {})

    def delete(self, path, headers=None):
        key = path[len("/records/"):]
        return _Resp(204 if self.store.pop(key, None) is not None else 404, None)


@pytest.fixture()
def pdi_pair(tmp_path, monkeypatch):
    """A JIM app wired to a FakePDI through the real PDIClient."""
    monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
    monkeypatch.setenv("JIM_LLM", "stub")
    monkeypatch.delenv("JIM_QRME_URL", raising=False)
    jim_db.reset()
    from jim.api import create_app
    from jim.pdi_client import PDIClient

    fake = FakePDIHttp()
    with TestClient(create_app(
            pdi_client=PDIClient(token="pdi_test", client=fake))) as c:
        yield c, fake
    jim_db.reset()


def test_health_reports_pdi(pdi_pair):
    jim, _ = pdi_pair
    body = jim.get("/health").json()
    assert body["pdi"] is True


def test_biometric_sample_stored_in_vault_not_locally(pdi_pair):
    jim, fake = pdi_pair
    user = enroll(jim)
    result = jim.post(f"/monitor/{user}",
                      json={"heart_rate": 120, "respiratory_rate": 22}).json()
    assert result["detected"] is True          # detection still works

    events = jim.get(f"/events/{user}").json()
    biometric = next(e for e in events if e["type"] == "biometric")
    detection = next(e for e in events if e["type"] == "detection")
    # Local rows hold only vault references…
    assert biometric["detail"] == {
        "vaulted": True, "pdi_key": f"jim/{user}/medical/biometric/{biometric['id']}"}
    assert detection["detail"]["vaulted"] is True
    # …while the raw medical payloads sit sealed in PDI.
    sample = json.loads(fake.store[biometric["detail"]["pdi_key"]])
    assert sample["heart_rate"] == 120
    signals = json.loads(fake.store[detection["detail"]["pdi_key"]])
    assert signals["signals"]["heart_rate"] == 120


def test_context_payload_vaulted_but_rules_still_fire(pdi_pair):
    jim, fake = pdi_pair
    user = enroll(jim)
    jim.put(f"/sources/{user}", json={"source": "spending", "consented": True})
    body = jim.post(f"/context/{user}", json={
        "source": "spending", "kind": "transaction",
        "data": {"amount": 320, "category": "dining out"}}).json()
    assert body["vaulted"] is True
    assert body["insights"][0]["kind"] == "alert"   # rules ran on raw data
    stored = json.loads(fake.store[f"jim/{user}/context/{body['id']}"])
    assert stored["amount"] == 320


def test_checkin_note_vaulted_and_crisis_still_escalates(pdi_pair):
    jim, fake = pdi_pair
    user = enroll(jim, emergency_name="Ana", emergency_phone="+1 555 0100",
                  contact_consent=True)
    body = jim.post(f"/checkin/{user}", json={
        "mood": 1, "note": "I don't want to live"}).json()
    assert body["guardian"]["escalation"]["notified_emergency_contact"] is True
    note_key = f"jim/{user}/medical/checkin/{body['id']}"
    assert json.loads(fake.store[note_key])["note"] == "I don't want to live"


def test_erasure_purges_the_vault_too(pdi_pair):
    jim, fake = pdi_pair
    user = enroll(jim)
    jim.put(f"/sources/{user}", json={"source": "wearable", "consented": True})
    jim.post(f"/monitor/{user}", json={"heart_rate": 120, "respiratory_rate": 22})
    jim.post(f"/context/{user}", json={
        "source": "wearable", "kind": "sleep", "data": {"hours": 8}})
    jim.post(f"/checkin/{user}", json={"mood": 2, "note": "rough day"})
    assert len(fake.store) > 0

    deleted = jim.delete(f"/data/{user}").json()["deleted"]
    assert deleted["pdi_records"] == deleted["vault_keys"]
    assert fake.store == {}                      # nothing left in the vault
    assert jim.get(f"/events/{user}").status_code == 404
