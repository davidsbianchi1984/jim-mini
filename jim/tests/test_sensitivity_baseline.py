"""Tunable escalation sensitivity (cautious/balanced/assertive) and the
rolling per-metric EMA baseline."""

from jim import conditions
from jim.tests.conftest import enroll


# -- sensitivity dial -------------------------------------------------------

def test_sensitivity_shifts_hr_thresholds():
    # resting 60; +45 over resting = 105 bpm, respiration corroborating.
    sample = {"heart_rate": 105, "resting_heart_rate": 60, "respiratory_rate": 22}
    # balanced needs +40 → detects (guidance).
    assert conditions.detect(sample, sensitivity="balanced").severity == "guidance"
    # assertive needs +50 → 45 isn't enough, no detection.
    assert conditions.detect(sample, sensitivity="assertive") is None
    # cautious needs only +30 → detects earlier.
    assert conditions.detect(sample, sensitivity="cautious").severity == "guidance"


def test_set_sensitivity_endpoint(client):
    uid = enroll(client)
    r = client.put(f"/sensitivity/{uid}", json={"level": "assertive"})
    assert r.status_code == 200 and r.json()["sensitivity"] == "assertive"
    bad = client.put(f"/sensitivity/{uid}", json={"level": "reckless"})
    assert bad.status_code == 422


def test_cautious_mode_reaches_out_early_for_declared_condition(client):
    uid = enroll(client, resting_heart_rate=60, contact_consent=True,
                 emergency_name="Sam", emergency_phone="+1000",
                 known_conditions=["anxiety"])
    client.put(f"/sensitivity/{uid}", json={"level": "cautious"})
    # A guidance-level (not critical) anxiety reading: cautious mode escalates
    # to the emergency contact anyway because anxiety is declared.
    r = client.post(f"/monitor/{uid}", json={
        "heart_rate": 100, "respiratory_rate": 22}).json()
    assert r["detected"] and r["severity"] == "guidance"
    assert r["escalation"]["escalated"] is True
    assert r["escalation"]["notified_emergency_contact"] is True
    assert "cautious-mode" in r["escalation"]["reason"]


def test_balanced_mode_does_not_escalate_guidance(client):
    uid = enroll(client, resting_heart_rate=60, contact_consent=True,
                 emergency_name="Sam", emergency_phone="+1000",
                 known_conditions=["anxiety"])
    r = client.post(f"/monitor/{uid}", json={
        "heart_rate": 100, "respiratory_rate": 22}).json()
    assert r["severity"] == "guidance"
    assert r["escalation"] is None


# -- rolling baseline -------------------------------------------------------

def test_baseline_seeded_at_enrollment_is_provisional(client):
    uid = enroll(client, resting_heart_rate=60)
    bl = client.get(f"/baseline/{uid}").json()
    hr = next(b for b in bl if b["metric"] == "heart_rate")
    assert hr["value"] == 60 and hr["samples"] == 0 and hr["provisional"] is True


def test_resting_samples_move_the_baseline(client):
    uid = enroll(client, resting_heart_rate=60)
    # Feed calm resting-state samples above the seed; the EMA drifts upward.
    for _ in range(6):
        client.post(f"/monitor/{uid}", json={
            "heart_rate": 70, "activity_level": 1})
    bl = client.get(f"/baseline/{uid}").json()
    hr = next(b for b in bl if b["metric"] == "heart_rate")
    assert 60 < hr["value"] <= 70
    assert hr["samples"] == 6 and hr["provisional"] is False


def test_exertion_samples_do_not_fold_into_baseline(client):
    uid = enroll(client, resting_heart_rate=60)
    before = client.get(f"/baseline/{uid}").json()[0]["value"]
    # A high-activity sample must not inflate the resting baseline.
    client.post(f"/monitor/{uid}", json={
        "heart_rate": 150, "activity_level": 9})
    after = client.get(f"/baseline/{uid}").json()[0]
    assert after["value"] == before and after["samples"] == 0


def test_learned_baseline_drives_detection_once_established(client):
    uid = enroll(client, resting_heart_rate=60)
    # Establish a higher learned resting baseline (~80) with calm samples.
    for _ in range(40):
        client.post(f"/monitor/{uid}", json={
            "heart_rate": 85, "activity_level": 1})
    bl = next(b for b in client.get(f"/baseline/{uid}").json()
              if b["metric"] == "heart_rate")
    assert not bl["provisional"] and bl["value"] >= 75

    # 110 bpm is +50 over the *enrolled* 60 (would detect) but only ~+30 over
    # the learned baseline — with the baseline in force it should not fire.
    r = client.post(f"/monitor/{uid}", json={
        "heart_rate": 110, "respiratory_rate": 22, "activity_level": 9}).json()
    assert r["detected"] is False
