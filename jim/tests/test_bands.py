"""Personal drift bands: your own normal, and how far from it counts.

The alarm layer (jim/conditions.py) answers *is this an episode?*. This
answers *am I drifting from my own baseline, either way?* — and must never
become a second, jumpier alarm.
"""

from __future__ import annotations

from jim import bands, guardian


def _enroll(client):
    r = client.post("/enroll", json={
        "display_name": "Dana", "birthdate": "1990-01-01",
        "terms_consent": True, "resting_heart_rate": 60})
    assert r.status_code == 201
    return r.json()


def _auth(u):
    return {"authorization": f"Bearer {u['user_token']}"}


def _establish(user_id, metric, value, n=8):
    """Fold enough resting samples to leave 'provisional' behind."""
    for _ in range(n):
        guardian.update_baseline(user_id, metric, value)


def test_every_metric_has_a_band_with_two_edges(client):
    u = _enroll(client)
    body = client.get(f"/bands/{u['id']}", headers=_auth(u)).json()
    metrics = {b["metric"] for b in body["bands"]}
    assert {"heart_rate", "hrv", "blood_oxygen", "respiratory_rate",
            "body_temperature"} <= metrics
    for b in body["bands"]:
        assert b["margin"] > 0
        assert "watch_high" in b and "watch_low" in b


def test_a_provisional_baseline_reports_no_edges_and_no_drift(client):
    u = _enroll(client)
    guardian.update_baseline(u["id"], "heart_rate", 60)   # one sample only
    band = next(b for b in client.get(f"/bands/{u['id']}", headers=_auth(u))
                .json()["bands"] if b["metric"] == "heart_rate")
    assert band["provisional"] is True
    assert band["low_edge"] is None and band["high_edge"] is None
    # A band around a number learned from one sample is noise with a line on it.
    assert bands.check(u["id"], {"heart_rate": 95}) == []


def test_drift_is_detected_in_both_directions(client):
    u = _enroll(client)
    _establish(u["id"], "heart_rate", 60)
    high = bands.check(u["id"], {"heart_rate": 75})
    low = bands.check(u["id"], {"heart_rate": 45})
    assert high and high[0]["direction"] == "above"
    assert low and low[0]["direction"] == "below"
    # Inside the band is silence.
    assert bands.check(u["id"], {"heart_rate": 62}) == []


def test_a_metric_can_have_one_edge_switched_off(client):
    """HRV is the case: the fall is the news, the rise usually is not."""
    u = _enroll(client)
    _establish(u["id"], "hrv", 60)
    default = bands.band_for(u["id"], "hrv")
    assert default["watch_low"] is True and default["watch_high"] is False
    assert bands.check(u["id"], {"hrv": 30})            # the fall speaks
    assert bands.check(u["id"], {"hrv": 120}) == []      # the rise does not


def test_the_band_is_the_users_to_widen_or_narrow(client):
    u = _enroll(client)
    _establish(u["id"], "heart_rate", 60)
    assert bands.check(u["id"], {"heart_rate": 70})      # crosses the default
    r = client.put(f"/bands/{u['id']}/heart_rate", json={"margin": 20},
                   headers=_auth(u))
    assert r.status_code == 200, r.text
    assert r.json()["source"] == "user"
    assert bands.check(u["id"], {"heart_rate": 70}) == []   # now inside
    # And back to the default.
    client.delete(f"/bands/{u['id']}/heart_rate", headers=_auth(u))
    assert bands.check(u["id"], {"heart_rate": 70})


def test_a_zero_width_band_is_refused(client):
    u = _enroll(client)
    r = client.put(f"/bands/{u['id']}/heart_rate", json={"margin": 0},
                   headers=_auth(u))
    assert r.status_code == 422


def test_drift_is_a_check_in_and_never_an_escalation(client):
    """The whole point: crossing a personal band asks a question. It must not
    reach the escalation ladder — that stays the alarm layer's alone."""
    u = _enroll(client)
    _establish(u["id"], "heart_rate", 60)
    r = client.post(f"/monitor/{u['id']}",
                    json={"heart_rate": 72, "activity_level": 1},
                    headers=_auth(u))
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["detected"] is False          # not an episode
    assert body["escalation"] is None         # and nobody is called
    assert body["drift"]["crossings"][0]["direction"] == "above"
    q = body["drift"]["question"]
    assert "?" in q and "72" in q and "alarm" in q.lower()


def test_the_question_names_the_numbers_and_stays_a_question(client):
    u = _enroll(client)
    _establish(u["id"], "blood_oxygen", 97)
    drifts = bands.check(u["id"], {"blood_oxygen": 94})
    q = bands.question(drifts)
    assert "94" in q and "97" in q
    assert q.rstrip().endswith("?")
    # Not a diagnosis.
    for word in ("diagnos", "you have", "condition is"):
        assert word not in q.lower()


def test_bands_cover_every_metric_the_guardian_learns(client):
    """A band can only exist around a baseline, so monitor must learn one for
    each metric a band watches — heart rate alone was the old behaviour."""
    u = _enroll(client)
    client.post(f"/monitor/{u['id']}",
                json={"heart_rate": 60, "hrv": 55, "blood_oxygen": 98,
                      "respiratory_rate": 14, "body_temperature": 36.6,
                      "activity_level": 1},
                headers=_auth(u))
    learned = {b["metric"] for b in guardian.baseline_for(u["id"])}
    assert {"heart_rate", "hrv", "blood_oxygen", "respiratory_rate",
            "body_temperature"} <= learned


def test_exertion_never_becomes_the_baseline(client):
    """A hard workout must not teach the Guardian that 150 is this person's
    resting rate — otherwise every band drifts up with the exercise."""
    u = _enroll(client)
    client.post(f"/monitor/{u['id']}",
                json={"heart_rate": 150, "activity_level": 9},
                headers=_auth(u))
    learned = {b["metric"]: b for b in guardian.baseline_for(u["id"])}
    # The enrolment seed may be present, but nothing folded into it.
    assert learned.get("heart_rate", {"samples": 0})["samples"] == 0
    assert learned.get("heart_rate", {"value": 60})["value"] == 60
