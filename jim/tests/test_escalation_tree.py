"""Predictive early-warning algorithm + the escalation decision tree, and the
Emergency-button flow that sits on top of them."""

from jim import earlywarning, escalation


def _enroll(client, **extra):
    body = {"display_name": "Jordan", "birthdate": "1995-05-05",
            "terms_consent": True, "resting_heart_rate": 60}
    body.update(extra)
    r = client.post("/enroll", json=body, headers={})
    assert r.status_code == 201, r.text
    return r.json()


def _auth(u):
    return {"authorization": f"Bearer {u['user_token']}"}


# --- earlywarning: the trend-projection algorithm -------------------------- #

def test_forecast_projects_a_rising_heart_rate():
    fc = earlywarning.assess({"heart_rate": [80, 90, 100]}, resting=70)
    assert fc is not None and fc.signal == "heart_rate"
    assert fc.condition == "anxiety"
    assert 0 < fc.horizon_min <= 20          # balanced window
    assert fc.confidence == 1.0              # perfectly linear series
    assert "projected to cross" in fc.reason


def test_forecast_projects_a_falling_spo2():
    fc = earlywarning.assess({"blood_oxygen": [97, 95, 93]}, resting=70)
    assert fc is not None and fc.signal == "blood_oxygen"
    assert fc.condition == "physical_distress"


def test_flat_or_noisy_trends_do_not_fire():
    assert earlywarning.assess({"heart_rate": [80, 80, 80]}, resting=70) is None
    # Noisy series fails the balanced R² gate even though the mean is rising.
    noisy = earlywarning.assess(
        {"heart_rate": [80, 105, 82, 104, 84]}, resting=70,
        sensitivity="balanced")
    assert noisy is None


def test_sensitivity_widens_or_narrows_the_lookahead():
    # Slow climb: crossing projected ~25 min out at 5-min spacing.
    slow = {"heart_rate": [86, 90, 94]}     # +4/reading toward 110
    assert earlywarning.assess(slow, resting=70, sensitivity="cautious") is not None
    assert earlywarning.assess(slow, resting=70, sensitivity="assertive") is None


def test_already_over_threshold_is_not_a_forecast():
    # Detection's job, not prediction's.
    assert earlywarning.assess({"heart_rate": [120, 125, 130]}, resting=70) is None


# --- escalation: the decision tree ----------------------------------------- #

def test_tiers_by_severity_and_sensitivity():
    assert escalation.decide("guidance", "balanced")["tier"] == "self_guidance"
    assert escalation.decide("guidance", "cautious")["tier"] == "check_in"
    assert escalation.decide("guidance", "assertive")["tier"] == "log"
    assert escalation.decide("critical", "balanced",
                             contactable=True)["tier"] == "emergency_services"


def test_critical_floor_survives_assertive():
    d = escalation.decide("critical", "assertive", contactable=True)
    assert d["tier"] == "notify_contact"     # shifted down, but never below
    assert any("floor" in step for step in d["path"])


def test_crisis_language_is_a_hard_floor():
    d = escalation.decide("guidance", "assertive", crisis=True)
    assert d["tier"] == "emergency_services"
    assert d["call_emergency_services"] is True


def test_declared_condition_bumps_guidance():
    d = escalation.decide("guidance", "balanced", condition="anxiety",
                          known=["anxiety"])
    assert d["tier"] == "check_in"


def test_low_confidence_forecast_stays_gentle():
    d = escalation.decide("info", "cautious", confidence=0.3)
    assert d["tier"] == "self_guidance"      # capped despite the cautious shift


def test_unreachable_contact_is_visible_in_the_path():
    d = escalation.decide("critical", "balanced", contactable=False)
    assert d["notify_contact"] is False
    assert d["notify_contact_intended"] is True
    assert any("unmet" in step for step in d["path"])


# --- API integration ------------------------------------------------------- #

def test_escalation_policy_endpoint(client):
    u = _enroll(client)
    client.put(f"/sensitivity/{u['id']}", json={"level": "cautious"},
               headers=_auth(u))
    policy = client.get(f"/escalation-policy/{u['id']}", headers=_auth(u)).json()
    assert policy["sensitivity"] == "cautious"
    assert policy["by_severity"]["critical"] == "emergency_services"
    assert policy["safety_floors"]["crisis_language"] == "emergency_services"
    # PHI-adjacent: requires the user's token.
    assert client.get(f"/escalation-policy/{u['id']}", headers={}).status_code == 401


def test_monitor_forecast_carries_risk_and_horizon(client):
    u = _enroll(client)
    h = _auth(u)
    # Build the rising-but-under-threshold trend the forecaster watches.
    for hr in (78, 85, 92):
        r = client.post(f"/monitor/{u['id']}", json={"heart_rate": hr},
                        headers=h).json()
    assert r["detected"] is False
    fc = r["forecast"]
    assert fc is not None and fc["condition"] == "anxiety"
    assert 0 < fc["risk"] < 1
    assert fc["horizon_min"] > 0
    assert fc["confidence"] > 0.5


def test_detection_reports_the_escalation_decision(client):
    u = _enroll(client, emergency_name="Ma", emergency_phone="555-1",
                contact_consent=True)
    r = client.post(f"/monitor/{u['id']}",
                    json={"heart_rate": 145}, headers=_auth(u)).json()
    assert r["detected"] is True and r["severity"] == "critical"
    d = r["escalation_decision"]
    assert d["tier"] == "emergency_services"
    assert isinstance(d["path"], list) and d["path"]
    # The escalation payload itself carries the tier + auditable path.
    assert r["escalation"]["tier"] == "emergency_services"
    assert r["escalation"]["decision_path"]


def test_emergency_button_flow(client):
    u = _enroll(client, emergency_name="Ma", emergency_phone="555-1",
                contact_consent=True)
    r = client.post(f"/emergency/{u['id']}",
                    json={"situation": "I fell off a ladder",
                          "location": "12 Oak St"},
                    headers=_auth(u)).json()
    assert r["emergency"] is True
    steps = [s["step"] for s in r["flow"]]
    assert steps == ["armed", "call", "notify", "locate", "medical_id", "guide"]
    assert r["flow"][2]["detail"] == "Ma"
    assert r["flow"][3]["detail"] == "12 Oak St"
    d = r["escalation_decision"]
    assert d["tier"] == "emergency_services"     # deliberate press = top tier
    assert any("crisis" in p for p in d["path"])
