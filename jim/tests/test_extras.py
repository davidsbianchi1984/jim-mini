"""Architecture-poster extras: BP/HRV signals, journaling, progress reports,
feedback loop, and the consent-gated provider portal."""

from jim.tests.conftest import enroll


def test_blood_pressure_and_hrv_rules(client):
    user = enroll(client, emergency_name="Ana", emergency_phone="+1 555 0100",
                  contact_consent=True)
    crisis = client.post(f"/monitor/{user}",
                         json={"bp_systolic": 185, "bp_diastolic": 122}).json()
    assert crisis["condition"] == "physical_distress"
    assert crisis["severity"] == "critical"
    assert crisis["escalation"]["notified_emergency_contact"] is True

    elevated = client.post(f"/monitor/{user}",
                           json={"bp_systolic": 165, "bp_diastolic": 95}).json()
    assert elevated["severity"] == "guidance"

    strained = client.post(f"/monitor/{user}", json={"hrv": 15.0}).json()
    assert strained["condition"] == "stress"
    assert "variability" in strained["reason"]


def test_journal_runs_crisis_pipeline(client):
    user = enroll(client, emergency_name="Ana", emergency_phone="+1 555 0100",
                  contact_consent=True)
    calm = client.post(f"/journal/{user}",
                       json={"text": "Long walk today; felt lighter."}).json()
    assert calm["guardian"]["detected"] is False
    crisis = client.post(f"/journal/{user}",
                         json={"text": "I don't want to live"}).json()
    assert crisis["guardian"]["escalation"]["notified_emergency_contact"] is True
    entries = client.get(f"/journal/{user}").json()
    assert len(entries) == 2 and "lighter" in entries[0]["text"]


def test_progress_report_and_feedback_loop(client):
    user = enroll(client)
    client.post(f"/checkin/{user}", json={"mood": 4, "energy": 3})
    client.post(f"/checkin/{user}", json={"mood": 2})
    goal = client.post(f"/goals/{user}", json={
        "area": "health_fitness", "title": "Run 5k"}).json()
    client.patch(f"/goals/{user}/{goal['id']}", json={"progress": 0.4})
    habit = client.post(f"/habits/{user}", json={"name": "Stretch"}).json()
    client.post(f"/habits/{user}/{habit['id']}/log", json={})
    client.post(f"/monitor/{user}", json={"heart_rate": 120, "respiratory_rate": 22})
    client.post(f"/feedback/{user}", json={"rating": "up"})
    client.post(f"/feedback/{user}", json={"rating": "up", "note": "spot on"})
    client.post(f"/feedback/{user}", json={"rating": "down"})

    report = client.get(f"/report/{user}").json()
    assert report["checkins"]["count"] == 2
    assert report["checkins"]["avg_mood"] == 3.0
    assert report["goals"][0]["progress"] == 0.4
    assert report["habits"][0]["streak"] == 1
    assert report["detections"]["guidance"] == 1
    assert report["feedback"] == {"up": 2, "down": 1}


def test_provider_portal_requires_consent(client):
    private = enroll(client)
    assert client.get(f"/provider/{private}").status_code == 403

    shared = enroll(client, provider_consent=True,
                    known_conditions=["anxiety"])
    client.post(f"/monitor/{shared}",
                json={"heart_rate": 120, "respiratory_rate": 22,
                      "note": "racing thoughts before the meeting"})
    summary = client.get(f"/provider/{shared}").json()
    assert summary["known_conditions"] == ["anxiety"]
    assert summary["recent_detections"][0]["condition"] == "anxiety"
    # Condition-level facts only — the user's words never appear.
    import json
    assert "racing thoughts" not in json.dumps(summary)
