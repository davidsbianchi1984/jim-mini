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


def test_the_footsteps_count_enrolled_people(client):
    """The counter in the corner: how many people are enrolled here.

    An aggregate, never a roster — the payload carries the number and
    nothing else about anybody. A user row only exists once enrollment
    finished (an email account creates its user at verification), so the
    count is people, not attempts.
    """
    before = client.get("/health").json()["footsteps"]
    enroll(client)
    joined = 1
    assert client.get("/health").json()["footsteps"] == before + joined


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


def test_critical_escalates_to_emergency_contact(client, mail_server):
    user = enroll(client, emergency_name="Pat", emergency_phone="+1-555-0199", emergency_email="pat@example.com",
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


# -- the rate alone can be the emergency (found live: 199 bpm, "all calm") ---

def test_extreme_rate_with_slow_breathing_is_cardiac_not_calm():
    """The exact sample from the live find: 199 bpm at rest, respiration
    10, stress 0.8 — it walked past the anxiety rule (which wants fast
    breathing) and landed in the calm drift layer. Slow breathing must
    sharpen an extreme rate, never excuse it."""
    d = conditions.detect({"heart_rate": 199, "resting_heart_rate": 66,
                           "respiratory_rate": 10, "stress": 0.8})
    assert d is not None, "199 bpm at rest must never be 'all calm'"
    assert d.condition == conditions.CARDIAC
    assert d.severity == "critical"
    assert d.signals["pattern"] == "tachycardia"


def test_a_high_but_not_extreme_rate_with_slow_breathing_gets_guidance():
    d = conditions.detect({"heart_rate": 155, "resting_heart_rate": 60,
                           "respiratory_rate": 12})
    assert d is not None and d.condition == conditions.CARDIAC
    assert d.severity == "guidance"


def test_fast_breathing_keeps_the_anxiety_reading():
    """Exercise and panic live with the anxiety rule — the cardiac rule
    only speaks when the breathing that would explain the rate is
    absent."""
    d = conditions.detect({"heart_rate": 155, "resting_heart_rate": 60,
                           "respiratory_rate": 28})
    assert d is not None and d.condition == conditions.ANXIETY


def test_bradycardia_counts_without_a_collapse():
    """The mirror hole: a pulse in the 30s only counted beside a fall."""
    d = conditions.detect({"heart_rate": 27})
    assert d is not None and d.condition == conditions.CARDIAC
    assert d.severity == "critical"
    slow = conditions.detect({"heart_rate": 38})
    assert slow is not None and slow.condition == conditions.CARDIAC
    assert slow.severity == "guidance"


def test_a_mild_fever_does_not_mask_a_critical_rate():
    """Cardiac outranks distress: the rate rules sit with the other
    cardiac rules, so a 38.6° reading cannot answer first with guidance
    while 199 bpm stands in the same sample."""
    d = conditions.detect({"heart_rate": 199, "resting_heart_rate": 66,
                           "respiratory_rate": 10,
                           "body_temperature": 38.6})
    assert d is not None and d.condition == conditions.CARDIAC
    assert d.severity == "critical"
