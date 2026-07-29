"""The vigil: the alarm that fires when the signals stop.

The properties under test: silence is measured against real signs of life
(the vigil's own trip never counts as one), the trip happens at most once
per silence and never escalates past the steward, and the next reading —
not a menu — is the all-clear.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jim import db, vigil


def _enroll(client, name="Ada"):
    r = client.post("/enroll", json={
        "display_name": name, "birthdate": "1950-03-01",
        "terms_consent": True, "resting_heart_rate": 62})
    assert r.status_code == 201
    return r.json()


def _auth(u):
    return {"authorization": f"Bearer {u['user_token']}"}


def _age_events(user_id, days):
    """Backdate every non-vigil event, as if the user went quiet."""
    then = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    conn = db.connect()
    conn.execute("UPDATE events SET created_at=? WHERE user_id=?"
                 " AND type != 'vigil'", (then, user_id))
    conn.commit()


def test_arming_needs_a_reachable_steward(client):
    u = _enroll(client)
    r = client.put(f"/vigil/{u['id']}", json={
        "steward_name": "", "steward_channel": ""}, headers=_auth(u))
    assert r.status_code == 422


def test_a_quiet_user_trips_the_vigil_once(client):
    u = _enroll(client)
    client.put(f"/vigil/{u['id']}", json={
        "steward_name": "Sam", "steward_channel": "sam@example.com",
        "quiet_days": 2, "note": "I live alone — please knock."},
        headers=_auth(u))
    client.post(f"/monitor/{u['id']}", json={"heart_rate": 62},
                headers=_auth(u))
    _age_events(u["id"], days=3)
    first = client.post(f"/vigil/{u['id']}/sweep", headers=_auth(u)).json()
    assert first["tripped"] is True
    second = client.post(f"/vigil/{u['id']}/sweep", headers=_auth(u)).json()
    assert second["tripped_at"] == first["tripped_at"]   # once, not again
    events = client.get(f"/events/{u['id']}", headers=_auth(u)).json()
    vigils = [e for e in events if e["type"] == "vigil"]
    assert len(vigils) == 1
    assert "please knock" in vigils[0]["detail"]["message"].lower()


def test_the_trip_itself_is_not_a_sign_of_life(client):
    """The vigil's own event lands in the events table — it must not reset
    the very silence it measured."""
    u = _enroll(client)
    client.put(f"/vigil/{u['id']}", json={
        "steward_name": "Sam", "steward_channel": "sam@example.com",
        "quiet_days": 2}, headers=_auth(u))
    client.post(f"/monitor/{u['id']}", json={"heart_rate": 62},
                headers=_auth(u))
    _age_events(u["id"], days=3)
    client.post(f"/vigil/{u['id']}/sweep", headers=_auth(u))
    st = client.get(f"/vigil/{u['id']}", headers=_auth(u)).json()
    assert st["silent_hours"] >= 48        # still counting from the real quiet


def test_a_fresh_reading_stands_the_vigil_down(client):
    u = _enroll(client)
    client.put(f"/vigil/{u['id']}", json={
        "steward_name": "Sam", "steward_channel": "sam@example.com",
        "quiet_days": 1}, headers=_auth(u))
    client.post(f"/monitor/{u['id']}", json={"heart_rate": 62},
                headers=_auth(u))
    _age_events(u["id"], days=2)
    client.post(f"/vigil/{u['id']}/sweep", headers=_auth(u))
    assert client.get(f"/vigil/{u['id']}", headers=_auth(u)).json()["tripped"]
    client.post(f"/monitor/{u['id']}", json={"heart_rate": 63},
                headers=_auth(u))
    st = client.get(f"/vigil/{u['id']}", headers=_auth(u)).json()
    assert st["tripped"] is False          # showing up IS the all-clear


def test_the_vigil_never_reaches_the_escalation_ladder(client):
    """Silence is weak evidence: the steward is told, and nobody else. No
    escalation event, no emergency dispatch."""
    u = _enroll(client)
    client.put(f"/vigil/{u['id']}", json={
        "steward_name": "Sam", "steward_channel": "sam@example.com",
        "quiet_days": 1}, headers=_auth(u))
    _age_events(u["id"], days=2)
    client.post(f"/vigil/{u['id']}/sweep", headers=_auth(u))
    events = client.get(f"/events/{u['id']}", headers=_auth(u)).json()
    assert not [e for e in events if e["type"] == "escalation"]


def test_disarm_holds_even_through_silence(client):
    u = _enroll(client)
    client.put(f"/vigil/{u['id']}", json={
        "steward_name": "Sam", "steward_channel": "sam@example.com",
        "quiet_days": 1}, headers=_auth(u))
    client.delete(f"/vigil/{u['id']}", headers=_auth(u))
    _age_events(u["id"], days=5)
    st = client.post(f"/vigil/{u['id']}/sweep", headers=_auth(u)).json()
    assert st["armed"] is False and st["tripped"] is False


def test_the_im_okay_button_resolves(client):
    u = _enroll(client)
    client.put(f"/vigil/{u['id']}", json={
        "steward_name": "Sam", "steward_channel": "sam@example.com",
        "quiet_days": 1}, headers=_auth(u))
    _age_events(u["id"], days=2)
    client.post(f"/vigil/{u['id']}/sweep", headers=_auth(u))
    st = client.post(f"/vigil/{u['id']}/resolve", headers=_auth(u)).json()
    assert st["tripped"] is False


def test_vigil_surfaces_require_the_users_own_token(client):
    u, other = _enroll(client), _enroll(client, "Robin")
    for call in (
        lambda h: client.get(f"/vigil/{u['id']}", headers=h),
        lambda h: client.put(f"/vigil/{u['id']}", json={
            "steward_name": "S", "steward_channel": "s@x.com"}, headers=h),
        lambda h: client.post(f"/vigil/{u['id']}/sweep", headers=h),
    ):
        assert call(_auth(other)).status_code in (401, 403)


def test_the_steward_message_names_the_silence_not_a_diagnosis(client):
    u = _enroll(client)
    vigil.arm(u["id"], "Sam", "sam@example.com", quiet_days=1)
    client.post(f"/monitor/{u['id']}", json={"heart_rate": 62},
                headers=_auth(u))
    _age_events(u["id"], days=2)
    vigil.sweep(u["id"])
    events = client.get(f"/events/{u['id']}", headers=_auth(u)).json()
    msg = [e for e in events if e["type"] == "vigil"][0]["detail"]["message"]
    assert "not an emergency" in msg
    assert "absence of readings" in msg


def test_a_user_never_heard_from_cannot_trip(client):
    """No events at all means silence cannot be measured — a brand-new user
    who armed the vigil and walked away is not a missing person."""
    u = _enroll(client)
    db.connect().execute("DELETE FROM events WHERE user_id=?", (u["id"],))
    db.connect().commit()
    vigil.arm(u["id"], "Sam", "sam@example.com", quiet_days=1)
    st = vigil.sweep(u["id"])
    assert st["tripped"] is False and st["silent_hours"] is None
