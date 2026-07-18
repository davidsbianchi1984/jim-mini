"""JIM-mini running on its own — no QRME."""

from jim import conditions
from jim.tests.conftest import enroll


def test_detect_panic_from_biometrics():
    d = conditions.detect({"heart_rate": 130, "resting_heart_rate": 65,
                           "respiratory_rate": 24})
    assert d.condition == conditions.ANXIETY


def test_detect_low_oxygen_critical():
    d = conditions.detect({"blood_oxygen": 86})
    assert d.condition == conditions.PHYSICAL_DISTRESS and d.severity == "critical"


def test_crisis_language_escalates():
    assert conditions.detect({}, "I don't want to live anymore").severity == "critical"


def test_health_reports_no_tandem(client):
    body = client.get("/health").json()
    assert body["status"] == "ok" and body["tandem"] is False


def test_enroll_requires_terms_consent(client):
    r = client.post("/enroll", json={"display_name": "X", "terms_consent": False})
    assert r.status_code == 403


def test_minor_requires_guardian_consent(client):
    minor = {"display_name": "Teen", "birthdate": "2012-01-01", "terms_consent": True}
    assert client.post("/enroll", json=minor).status_code == 403
    minor["guardian_consent"] = True
    assert client.post("/enroll", json=minor).status_code == 201


def test_monitor_delivers_local_guidance(client):
    user = enroll(client)
    body = client.post(f"/monitor/{user}",
                       json={"heart_rate": 118, "respiratory_rate": 22,
                             "note": "panic attack coming on"}).json()
    assert body["detected"] and body["condition"] == "anxiety"
    g = body["guidance"]
    assert g["delivered"] and g["source"] == "local"
    assert g["content"]


def test_critical_escalates_to_emergency_contact(client):
    user = enroll(client, emergency_name="Pat", emergency_phone="+1-555-0199",
                  contact_consent=True)
    body = client.post(f"/monitor/{user}", json={"blood_oxygen": 84}).json()
    assert body["severity"] == "critical"
    esc = body["escalation"]
    assert esc["escalated"] and esc["notified_emergency_contact"]
    assert esc["emergency_contact"]["name"] == "Pat"


def test_tandem_specialist_without_endpoint_falls_back_local(client):
    client.post("/specialists", json={"condition": "anxiety", "mode": "tandem",
                                      "qrme_profile_id": "prf_x"})
    user = enroll(client)
    g = client.post(f"/monitor/{user}",
                    json={"heart_rate": 130, "respiratory_rate": 24}).json()["guidance"]
    assert g["source"] == "local"          # no QRME endpoint configured
    assert "no QRME endpoint" in g["note"]


def test_event_timeline(client):
    user = enroll(client)
    client.post(f"/monitor/{user}", json={"heart_rate": 150, "respiratory_rate": 26})
    types = [e["type"] for e in client.get(f"/events/{user}").json()]
    assert types == ["biometric", "detection", "guidance", "escalation"]
