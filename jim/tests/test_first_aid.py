"""Physical-condition first aid: CPR with pace cues, AED guidance for
fibrillation, the low-blood-oxygen playbook, environmental and ergonomic
indications, an SpO2 slide forecast before the threshold, and autonomous
alert dispatch to connected devices."""

from jim.tests.conftest import enroll


def test_collapse_with_absent_pulse_gets_cpr_with_pace_cues(client):
    uid = enroll(client, contact_consent=True, emergency_name="Sam",
                 emergency_phone="+1000")
    client.post(f"/devices/{uid}", json={"name": "kitchen_console",
                                         "kind": "stationary"})
    client.post(f"/devices/{uid}", json={"name": "helper_bot",
                                         "kind": "autonomous"})

    r = client.post(f"/monitor/{uid}", json={
        "movement": "collapse", "pulse": "absent"}).json()
    assert r["condition"] == "cardiac_event" and r["severity"] == "critical"

    aid = r["guidance"]["first_aid"]
    assert aid["kind"] == "cpr" and aid["call_emergency_services"] is True
    assert any("chest" in s.lower() for s in aid["steps"])
    # Proper pace, cued by lights and audio (the patent's red/green + audio).
    pace = aid["pace"]
    assert 100 <= pace["compressions_per_minute"] <= 120
    assert pace["compression_to_breath_ratio"] == "30:2"
    assert "green" in pace["cue"]["light"] and "red" in pace["cue"]["light"]
    assert "metronome" in pace["cue"]["audio"]

    # Autonomous coordinated response: alerts dispatched to every connected
    # system, contact notified, live help flagged.
    esc = r["escalation"]
    assert esc["dispatched_alerts"] == ["kitchen_console", "helper_bot"]
    assert esc["notified_emergency_contact"] is True
    assert esc["live_support"] is True


def test_fibrillation_gets_aed_guidance(client):
    uid = enroll(client)
    r = client.post(f"/monitor/{uid}", json={"rhythm": "fibrillation"}).json()
    assert r["condition"] == "cardiac_event" and r["severity"] == "critical"
    aid = r["guidance"]["first_aid"]
    assert aid["kind"] == "aed"
    assert any("AED" in s for s in aid["steps"])
    assert any("shock" in s.lower() for s in aid["steps"])


def test_plain_collapse_is_still_a_physical_injury(client):
    uid = enroll(client)
    r = client.post(f"/monitor/{uid}", json={
        "movement": "collapse", "heart_rate": 95}).json()
    assert r["condition"] == "physical_injury"       # pulse present — not cardiac


def test_low_blood_oxygen_playbook(client):
    uid = enroll(client)
    r = client.post(f"/monitor/{uid}", json={"blood_oxygen": 89}).json()
    assert r["condition"] == "physical_distress" and r["severity"] == "guidance"
    steps = " ".join(r["guidance"]["first_aid"]["steps"]).lower()
    # The patent's example: breathe deeply, fresh air, medical attention.
    assert "breathe deeply" in steps
    assert "fresh air" in steps
    assert "medical attention" in steps


def test_environmental_hazard_says_leave_now(client):
    uid = enroll(client)
    r = client.post(f"/monitor/{uid}", json={"air_quality": "smoke"}).json()
    assert r["condition"] == "environmental_hazard"
    assert r["severity"] == "critical" and r["escalation"]["escalated"]
    steps = " ".join(r["guidance"]["first_aid"]["steps"]).lower()
    assert "fresh air" in steps
    # CO by ppm works too, and merely poor air is guidance-level.
    co = client.post(f"/monitor/{uid}", json={"co_level": 12}).json()
    assert co["condition"] == "environmental_hazard" and co["severity"] == "critical"
    poor = client.post(f"/monitor/{uid}", json={"air_quality": "poor"}).json()
    assert poor["severity"] == "guidance" and poor["escalation"] is None


def test_ergonomic_risk_is_guidance_not_emergency(client):
    uid = enroll(client)
    r = client.post(f"/monitor/{uid}", json={
        "posture": "slouched", "repetitive_motion_min": 60}).json()
    assert r["condition"] == "ergonomic_strain" and r["severity"] == "guidance"
    assert r["escalation"] is None
    steps = " ".join(r["guidance"]["first_aid"]["steps"]).lower()
    assert "posture" in steps and "break" in steps


def test_spo2_slide_is_forecast_before_the_threshold(client):
    uid = enroll(client)
    result = None
    for spo2 in (97, 95, 93):                  # declining, all >= 90
        result = client.post(f"/monitor/{uid}",
                             json={"blood_oxygen": spo2}).json()
    assert result["detected"] is False          # nothing crossed the threshold
    assert result["forecast"] is not None       # but the slide was caught
    assert "slipping" in result["forecast"]["reason"]
    insights = client.get(f"/insights/{uid}").json()
    assert any(i["kind"] == "forecast" and "Blood oxygen" in i["message"]
               for i in insights)
