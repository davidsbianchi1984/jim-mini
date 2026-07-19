"""Coverage for the 526.P001 claim set: declared known conditions, expanded
physical indications, first aid, predictive early warning, personality
adaptation, cross-session memory, references, and delivery channel."""

from jim.tests.conftest import enroll


def test_declared_condition_sensitizes_detection(client):
    # HR 95 with resting 60 is +35: below the normal +40 threshold…
    plain = enroll(client)
    r = client.post(f"/monitor/{plain}",
                    json={"heart_rate": 95, "respiratory_rate": 21}).json()
    assert r["detected"] is False

    # …but detected for a user who declared anxiety as a known condition.
    prone = enroll(client, known_conditions=["anxiety"])
    r = client.post(f"/monitor/{prone}",
                    json={"heart_rate": 95, "respiratory_rate": 21}).json()
    assert r["detected"] is True
    assert "sensitized" in r["reason"]


def test_declare_condition_after_enrollment(client):
    user = enroll(client)
    body = client.post(f"/conditions/{user}",
                       json={"condition": "phobia",
                             "note": "terrified of flying"}).json()
    assert body["known_conditions"] == ["phobia"]
    events = client.get(f"/events/{user}").json()
    assert any(e["type"] == "condition_declared" for e in events)


def test_fall_triggers_first_aid_with_references(client):
    user = enroll(client, emergency_name="Ana", emergency_phone="+1 555 0100",
                  contact_consent=True, devices=["smart_watch", "phone"])
    r = client.post(f"/monitor/{user}", json={"movement": "fall"}).json()
    assert r["condition"] == "physical_injury"
    assert r["severity"] == "critical"
    assert any("first-aid" in ref.lower() for ref in r["guidance"]["references"])
    assert r["guidance"]["delivered_via"] == "smart_watch"   # clause 7
    assert r["escalation"]["notified_emergency_contact"] is True


def test_temperature_and_speech_indications(client):
    user = enroll(client)
    fever = client.post(f"/monitor/{user}", json={"body_temperature": 40.2}).json()
    assert fever["condition"] == "physical_distress"
    assert fever["severity"] == "critical"
    mild = client.post(f"/monitor/{user}", json={"body_temperature": 38.7}).json()
    assert mild["severity"] == "guidance"
    slurred = client.post(f"/monitor/{user}", json={"speech": "slurred"}).json()
    assert slurred["severity"] == "critical"


def test_stress_and_injury_text_cues(client):
    user = enroll(client)
    r = client.post(f"/monitor/{user}",
                    json={"note": "completely burned out by this deadline"}).json()
    assert r["condition"] == "stress"
    r = client.post(f"/monitor/{user}",
                    json={"note": "I fell off my bike and I'm bleeding"}).json()
    assert r["condition"] == "physical_injury"


def test_predictive_forecast_before_threshold(client):
    user = enroll(client)   # resting 60; detection needs >= 100
    for hr in (78, 88):
        assert client.post(f"/monitor/{user}",
                           json={"heart_rate": hr}).json()["forecast"] is None
    r = client.post(f"/monitor/{user}", json={"heart_rate": 96}).json()
    assert r["detected"] is False
    assert r["forecast"]["condition"] == "anxiety"
    assert "rising heart-rate trend" in r["forecast"]["reason"]
    insights = client.get(f"/insights/{user}").json()
    assert any(i["source"] == "forecast" for i in insights)


def test_personality_adaptation_shapes_guidance(client):
    user = enroll(client)
    client.put(f"/personality/{user}", json={"tone": "direct and brief"})
    r = client.post(f"/monitor/{user}",
                    json={"heart_rate": 120, "respiratory_rate": 22}).json()
    assert "(tone: direct and brief)" in r["guidance"]["content"]
    # the coach adapts too (clause 12)
    c = client.post(f"/coach/{user}", json={
        "area": "career", "message": "help me plan the week"}).json()
    assert "(tone: direct and brief)" in c["content"]


def test_references_accompany_counseling(client):
    user = enroll(client)
    r = client.post(f"/monitor/{user}",
                    json={"heart_rate": 120, "respiratory_rate": 22}).json()
    refs = r["guidance"]["references"]
    assert refs and any("breathing" in ref.lower() for ref in refs)


def test_cross_device_login_sessions(client):
    """Clause 14/20: consistent guidance across login sessions and devices."""
    user = enroll(client)
    watch = client.post(f"/sessions/{user}", json={"device": "smart_watch"}).json()
    assert watch["prior_sessions"] == 0 and watch["memory"] is None
    r = client.post(f"/monitor/{user}",
                    json={"heart_rate": 120, "respiratory_rate": 22}).json()
    assert r["guidance"]["delivered_via"] == "smart_watch"
    client.post(f"/sessions/{user}/{watch['id']}/end")

    # New login on a different device: same remembered thread, new channel.
    phone = client.post(f"/sessions/{user}", json={"device": "phone"}).json()
    assert phone["prior_sessions"] == 1
    assert "Keep continuity" in phone["memory"]
    r = client.post(f"/monitor/{user}",
                    json={"heart_rate": 121, "respiratory_rate": 22}).json()
    assert r["guidance"]["delivered_via"] == "phone"


def test_multimodal_source_device_routes_delivery(client):
    """Clauses 17/18: input names its modality; counseling routes back to it."""
    user = enroll(client, devices=["phone"])
    r = client.post(f"/monitor/{user}",
                    json={"heart_rate": 120, "respiratory_rate": 22,
                          "source_device": "neural_sensor"}).json()
    assert r["guidance"]["delivered_via"] == "neural_sensor"
    events = client.get(f"/events/{user}").json()
    assert events[0]["detail"]["source_device"] == "neural_sensor"


def test_guidance_remembers_prior_sessions(client):
    user = enroll(client)
    client.post(f"/monitor/{user}", json={"heart_rate": 120, "respiratory_rate": 22})
    second = client.post(f"/monitor/{user}",
                         json={"heart_rate": 122, "respiratory_rate": 22}).json()
    assert second["guidance"]["delivered"] is True
    events = client.get(f"/events/{user}").json()
    assert sum(1 for e in events if e["type"] == "guidance") == 2
