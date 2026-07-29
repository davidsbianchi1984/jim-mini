"""The crash watch — the vigil's acute sibling: a critical reading opens
"are you okay?", N unanswered attempts summon the help the user programmed
in advance, and any sign of the person ends it.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jim import crashwatch, db
from jim.tests.conftest import enroll


def _arm(client, user, **extra):
    body = {"trusted_name": "Rosa", "trusted_channel": "rosa@example.com",
            "attempts": 3, "window_minutes": 5.0,
            "contact_emergency_services": True}
    body.update(extra)
    r = client.put(f"/crash-watch/{user}", json=body)
    assert r.status_code == 200, r.text
    return r.json()


def test_arming_is_the_consent_moment(client):
    user = enroll(client)
    assert client.get(f"/crash-watch/{user}").json() == {"armed": False}
    st = _arm(client, user)
    assert st["armed"] and st["trusted_name"] == "Rosa"
    assert st["contact_emergency_services"] is True
    assert st["asking"] is False and st["tripped"] is False
    # Refusals a person can read.
    r = client.put(f"/crash-watch/{user}", json={
        "trusted_name": "", "trusted_channel": ""})
    assert r.status_code == 422
    r = client.put(f"/crash-watch/{user}", json={
        "trusted_name": "Rosa", "trusted_channel": "rosa@example.com",
        "attempts": 99})
    assert r.status_code == 422


def test_a_critical_reading_opens_the_question(client):
    user = enroll(client)
    _arm(client, user)
    # Blood oxygen at 85 is a critical detection (jim/conditions.py).
    r = client.post(f"/monitor/{user}", json={"blood_oxygen": 85})
    assert r.status_code == 200 and r.json()["detected"] is True
    st = client.get(f"/crash-watch/{user}").json()
    assert st["asking"] is True and st["attempt"] == 1
    # The "I'm okay" button is the all-clear.
    st = client.post(f"/crash-watch/{user}/respond").json()
    assert st["asking"] is False and st["tripped"] is False


def test_a_normal_reading_answers_a_concerning_one_does_not(client):
    user = enroll(client)
    _arm(client, user)
    client.post(f"/monitor/{user}", json={"blood_oxygen": 85})
    assert client.get(f"/crash-watch/{user}").json()["asking"] is True
    # The emergency continuing is not an answer.
    client.post(f"/monitor/{user}", json={"blood_oxygen": 84})
    assert client.get(f"/crash-watch/{user}").json()["asking"] is True
    # The body reporting back in is.
    client.post(f"/monitor/{user}", json={"heart_rate": 62})
    assert client.get(f"/crash-watch/{user}").json()["asking"] is False


def test_unanswered_attempts_trip_and_summon_the_programmed_help(client):
    user = enroll(client)
    _arm(client, user, attempts=3, window_minutes=5.0)
    client.post(f"/monitor/{user}", json={"blood_oxygen": 85})
    # Silence, straight through every attempt's deadline.
    later = datetime.now(timezone.utc) + timedelta(minutes=30)
    st = crashwatch.sweep(user, now=later)
    assert st["tripped"] is True
    # The trip event carries the whole story: the trusted person, the
    # unanswered count, and the emergency-services request — recorded as a
    # request, never a claim that a call was placed.
    row = db.connect().execute(
        "SELECT * FROM events WHERE user_id=? AND type='crash_watch' AND"
        " severity='alert'", (user,)).fetchone()
    assert row is not None
    import json as _json
    detail = _json.loads(row["detail"])
    assert detail["trusted"] == "Rosa"
    assert detail["unanswered_attempts"] == 3
    assert detail["emergency_services"]["requested"] is True
    assert "cannot itself place a call" in detail["emergency_services"]["note"]


def test_without_the_ticked_box_no_emergency_services(client):
    user = enroll(client)
    _arm(client, user, contact_emergency_services=False)
    client.post(f"/monitor/{user}", json={"blood_oxygen": 85})
    later = datetime.now(timezone.utc) + timedelta(hours=1)
    st = crashwatch.sweep(user, now=later)
    assert st["tripped"] is True
    import json as _json
    row = db.connect().execute(
        "SELECT detail FROM events WHERE user_id=? AND type='crash_watch'"
        " AND severity='alert'", (user,)).fetchone()
    assert _json.loads(row["detail"])["emergency_services"]["requested"] is False


def test_unarmed_users_are_never_asked(client):
    user = enroll(client)
    client.post(f"/monitor/{user}", json={"blood_oxygen": 85})
    assert client.get(f"/crash-watch/{user}").json() == {"armed": False}
    rows = db.connect().execute(
        "SELECT COUNT(*) AS n FROM events WHERE user_id=? AND"
        " type='crash_watch'", (user,)).fetchone()
    assert rows["n"] == 0


def test_drift_checkins_stay_calm(client):
    """A band crossing is a question, never a crash concern — the bands'
    oldest commitment, restated here so nobody softens it by accident."""
    user = enroll(client)
    _arm(client, user)
    crashwatch.note_concern(user, "drift", "checkin")
    assert client.get(f"/crash-watch/{user}").json()["asking"] is False


def test_disarm_stands_everything_down(client):
    user = enroll(client)
    _arm(client, user)
    client.post(f"/monitor/{user}", json={"blood_oxygen": 85})
    st = client.delete(f"/crash-watch/{user}").json()
    assert st["armed"] is False and st["asking"] is False
    # Silence after disarm trips nothing.
    later = datetime.now(timezone.utc) + timedelta(hours=1)
    assert crashwatch.sweep(user, now=later)["tripped"] is False


def _drip_path(client, user):
    r = client.get(f"/watch/channel/{user}")
    assert r.status_code == 200, r.text
    return "/watch/drip/" + r.json()["drip_url"].rsplit("/", 1)[1]


def test_a_fall_through_the_watch_opens_the_question(client):
    """The senior scenario, end to end: the watch feels the fall, the drip
    carries it (words, not numbers), the detector calls it critical, and
    the armed crash watch asks — silence from here summons the programmed
    help. Before this test the drip dropped non-numeric readings, which
    silently excluded exactly this event."""
    user = enroll(client)
    _arm(client, user)
    drip = _drip_path(client, user)
    r = client.post(drip, json={"movement": "fall"})
    assert r.status_code == 200 and r.json()["noticed"] is True
    st = client.get(f"/crash-watch/{user}").json()
    assert st["asking"] is True

    # Shortcuts' boolean shape works too, and so does the arrest pattern.
    client.post(f"/crash-watch/{user}/respond")
    r = client.post(drip, json={"fall_detected": True, "pulse": "absent"})
    assert r.status_code == 200 and r.json()["noticed"] is True
    st = client.get(f"/crash-watch/{user}").json()
    assert st["asking"] is True and st["concern"] == "cardiac_event"


def test_free_text_never_rides_the_drip(client):
    """The whitelist holds: an unknown word in movement is ignored, and a
    payload with nothing recognizable is refused with the fall hint."""
    user = enroll(client)
    drip = _drip_path(client, user)
    r = client.post(drip, json={"movement": "dancing"})
    assert r.status_code == 422
    assert "movement: fall" in r.json()["detail"]
