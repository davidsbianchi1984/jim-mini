"""Ambient background observation — the "Jiminy Cricket" jump-in: JIM watches
an activity and offers help proactively when a struggle builds, before asked."""

from jim import conditions
from jim.tests.conftest import enroll


def test_detect_ambient_rules():
    # Nothing concerning → no intervention.
    assert conditions.detect_ambient({"activity": "editing", "retries": 1}) is None
    # Frustrated words alone aren't quite enough; repeated attempts + words are.
    d = conditions.detect_ambient(
        {"activity": "editing video", "retries": 6},
        "ugh why won't this render")
    assert d is not None and d.condition == conditions.FRUSTRATION
    assert d.severity == "guidance"          # proactive help, never auto-escalates
    assert "editing video" in d.reason


def test_activity_triggers_proactive_intervention(client):
    uid = enroll(client)
    r = client.post(f"/activity/{uid}", json={
        "activity": "fixing the car",
        "signals": {"retries": 7, "duration_min": 50},
        "note": "come on, this makes no sense, I'm so stuck"})
    assert r.status_code == 201
    body = r.json()
    assert body["proactive"] is True
    assert body["source"] == "ambient"
    assert body["condition"] == "frustration"
    assert body["intervention"]["delivered"] is True

    # It surfaces as a proactive detection event, plus an insight.
    events = client.get(f"/events/{uid}").json()
    types = [e["type"] for e in events]
    assert "activity" in types and "detection" in types and "guidance" in types
    insights = client.get(f"/insights/{uid}").json()
    assert any(i["source"] == "ambient" for i in insights)


def test_calm_activity_is_watched_not_interrupted(client):
    uid = enroll(client)
    r = client.post(f"/activity/{uid}", json={
        "activity": "reading", "signals": {"retries": 0, "duration_min": 10}})
    body = r.json()
    assert body["proactive"] is False
    assert body["intervention"] is None
    assert body["watching"] is True
    # The activity is still logged, but no guidance was pushed.
    types = [e["type"] for e in client.get(f"/events/{uid}").json()]
    assert "activity" in types and "guidance" not in types


def test_crisis_language_during_activity_still_escalates(client):
    uid = enroll(client, contact_consent=True, emergency_name="Sam",
                 emergency_phone="+1000", birthdate="1990-01-01")
    r = client.post(f"/activity/{uid}", json={
        "activity": "late-night work",
        "signals": {"retries": 1},
        "note": "I don't want to live anymore"})
    body = r.json()
    assert body["source"] == "crisis"
    assert body["escalation"]["escalated"] is True
    assert body["escalation"]["live_support"] is True
