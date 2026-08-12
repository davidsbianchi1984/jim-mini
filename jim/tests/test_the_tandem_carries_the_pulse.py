"""The tandem carries the pulse, not a sentence about it.

Amended claim 6: real-time biometric data indicating stress or condition
changes, received *during* the interaction, modifies the profile's behavior.
Guardian already told the QRME specialist "the user shows signs of X" in
prose; the readings themselves stayed home. Now the triggering sample rides
the chat as ``biometrics``, so QRME conditions the specialist's reply on the
pulse and folds it into its latent embedding — the same current-readings
conditioning the offline coach applies locally.
"""

import pytest
from fastapi.testclient import TestClient

from jim import db as jim_db
from jim.tests.conftest import FakeQRME, enroll


@pytest.fixture()
def pulse_tandem(tmp_path, monkeypatch):
    """A JIM app with a tandem specialist, holding the FakeQRME so the test
    can read what actually crossed."""
    monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
    monkeypatch.setenv("JIM_LLM", "stub")
    jim_db.reset()
    from jim.api import create_app
    from jim.qrme_client import QRMEClient

    fake = FakeQRME()
    client = TestClient(create_app(qrme_client=QRMEClient(client=fake)))
    client.__enter__()
    client.post("/specialists", json={"condition": "anxiety",
                                      "mode": "tandem",
                                      "label": "Dr Whitcomb",
                                      "qrme_profile_id": "prf_anx"})
    uid = enroll(client)
    yield client, uid, fake
    client.__exit__(None, None, None)
    jim_db.reset()


def test_the_triggering_sample_rides_the_handoff(pulse_tandem):
    client, uid, fake = pulse_tandem
    sample = {"heart_rate": 124, "respiratory_rate": 24}
    r = client.post(f"/monitor/{uid}", json=sample)
    assert r.status_code == 200
    guidance = r.json()["guidance"]
    assert guidance["source"] == "tandem"

    handoff = [c for c in fake.chats if "biometrics" in c]
    assert handoff, "no chat carried biometrics across the tandem"
    sent = handoff[-1]["biometrics"]
    assert sent["heart_rate"] == 124
    assert sent["respiratory_rate"] == 24
    # The prose is still there too — the reason travels beside the readings.
    assert "signs of" in handoff[-1]["message"]


def test_a_note_only_crisis_sends_no_readings(pulse_tandem):
    client, uid, fake = pulse_tandem
    client.post("/specialists", json={"condition": "panic",
                                      "mode": "tandem",
                                      "label": "Dr Whitcomb",
                                      "qrme_profile_id": "prf_anx"})
    before = len([c for c in fake.chats if "biometrics" in c])
    r = client.post(f"/monitor/{uid}",
                    json={"note": "I feel a panic attack starting"})
    assert r.status_code == 200
    # A detection with no vitals hands off with no biometrics field —
    # nothing invented, nothing padded.
    with_biometrics = [c for c in fake.chats if "biometrics" in c]
    assert len(with_biometrics) == before
