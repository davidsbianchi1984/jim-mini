"""The device's own confession was stripped at the door.

## The finding

`jim/signal.py` grades every biometric sample and folds in the one piece of
evidence better than any range check — the device's own report of how well
it read: *"A device that reports its own signal quality is better evidence
about itself than any range check."* The fold is multiplicative on purpose,
so a wearable saying "poor contact" can only ever lower trust.

None of that could happen. `BiometricSample` did not declare
``signal_quality``, so pydantic silently dropped the field at
``POST /monitor/{id}`` and the grader received a sample with the confession
removed. An SpO2 of 62 read through a flapping strap graded ``ok`` at
confidence 1.0 — full trust in exactly the reading the device itself had
disowned.

    asked     is the sample graded
    mattered  can the device's own confession reach the grader

Found by driving, not reading: the module was correct, the unit tests
passed, and the door undid it. A binding is not a door; neither is a
grader.
"""

from __future__ import annotations


def _user(client):
    r = client.post("/enroll", json={"display_name": "Ned",
                                     "birthdate": "1955-03-09",
                                     "terms_consent": True})
    assert r.status_code == 201, r.text
    u = r.json()
    client.headers["authorization"] = f"Bearer {u['user_token']}"
    return u


def test_the_confession_now_reaches_the_grader(client):
    """The driven case: a plausible-but-alarming reading with the device
    reporting poor contact must not arrive at full confidence."""
    u = _user(client)
    r = client.post(f"/monitor/{u['id']}",
                    json={"blood_oxygen": 62, "signal_quality": 0.2})
    assert r.status_code == 200, r.text
    sig = r.json()["signal"]
    assert sig["confidence"] <= 0.2, sig
    assert sig["trusted"] is False, sig
    assert any("its own signal quality" in reason
               for reason in sig["reasons"]), sig


def test_a_confident_device_changes_nothing(client):
    u = _user(client)
    r = client.post(f"/monitor/{u['id']}",
                    json={"heart_rate": 72, "signal_quality": 1.0})
    assert r.json()["signal"]["confidence"] == 1.0, r.json()["signal"]


def test_the_field_is_bounded_at_the_door(client):
    """0..1 is the contract `signal.assess` clamps to; the door now says so
    too, so a device reporting 7 is an input error rather than a quiet
    clamp that hides the device's bug."""
    u = _user(client)
    r = client.post(f"/monitor/{u['id']}",
                    json={"heart_rate": 72, "signal_quality": 7})
    assert r.status_code == 422, r.text


def test_a_confession_cannot_manufacture_trust(client):
    """Multiplicative, so an impossible reading stays untrusted no matter
    what quality the device claims. Two liars are not a witness."""
    u = _user(client)
    r = client.post(f"/monitor/{u['id']}",
                    json={"heart_rate": 0, "signal_quality": 1.0})
    sig = r.json()["signal"]
    assert sig["grade"] == "implausible", sig
    assert sig["trusted"] is False, sig
