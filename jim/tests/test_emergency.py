"""Emergency mode: one coordinated response mirroring the Emergency screen —
call services, share location, contact family, Medical ID, AI first aid, and
connected-device alerts."""

from jim.tests.conftest import enroll


def _enroll_full(client):
    return enroll(client, birthdate="1984-06-01", resting_heart_rate=60,
                  contact_consent=True, emergency_name="Maria Bianchi",
                  emergency_phone="+15551234567",
                  known_conditions=["anxiety"])


def test_emergency_bundles_the_coordinated_response(client):
    uid = _enroll_full(client)
    client.post(f"/devices/{uid}", json={"name": "watch", "kind": "wearable"})
    client.post(f"/devices/{uid}", json={"name": "home_hub",
                                         "kind": "stationary"})

    r = client.post(f"/emergency/{uid}", json={
        "situation": "he collapsed and isn't breathing well",
        "location": "37.77,-122.41",
        "sample": {"blood_oxygen": 85}})
    assert r.status_code == 201
    body = r.json()
    assert body["emergency"] is True

    # Call services.
    assert body["call_emergency_services"]["number"] == "911"
    # Share location — with family and responders.
    assert body["share_location"]["location"] == "37.77,-122.41"
    assert "Maria Bianchi" in body["share_location"]["shared_with"]
    # Contact family.
    assert body["contact_family"]["phone"] == "+15551234567"
    assert body["contact_family"]["notified"] is True
    # Medical ID.
    med = body["medical_id"]
    assert med["name"] == "Jordan"       # enroll default display name
    assert med["age"] >= 40
    assert "acute anxiety / panic" in med["known_conditions"]
    assert med["emergency_contact"]["name"] == "Maria Bianchi"
    # AI guidance — the low-oxygen first-aid playbook, from the live sample.
    aid = body["ai_guidance"]["first_aid"]
    assert aid["kind"] == "low_blood_oxygen"
    assert any("fresh air" in s.lower() for s in aid["steps"])
    # Connected-device alerts.
    assert body["dispatched_alerts"] == ["watch", "home_hub"]


def test_emergency_needs_no_situation(client):
    uid = _enroll_full(client)
    body = client.post(f"/emergency/{uid}", json={}).json()
    # Even with nothing described, the response still reaches services and
    # surfaces the Medical ID.
    assert body["call_emergency_services"]["number"] == "911"
    assert body["medical_id"]["name"] == "Jordan"
    assert body["ai_guidance"] is None
    assert body["share_location"] is None


def test_emergency_situation_without_a_detection_gives_general_guidance(client):
    uid = _enroll_full(client)
    body = client.post(f"/emergency/{uid}", json={
        "situation": "my father is confused and pale"}).json()
    # No specific detection fires, but general first-aid guidance is provided.
    assert body["ai_guidance"] is not None
    assert "calm" in body["ai_guidance"]["content"].lower()


def test_emergency_is_logged_and_token_gated(client):
    uid = _enroll_full(client)
    client.post(f"/emergency/{uid}", json={"situation": "chest pain"})
    events = [e["type"] for e in client.get(f"/events/{uid}").json()]
    assert "emergency" in events
    # A different user's token cannot trigger emergency mode for this user.
    other = enroll(client)              # switches the client's default token
    assert client.post(f"/emergency/{uid}", json={}).status_code == 403
