"""The crash watch's trip lands on the Needs-a-person queue.

The trip used to be fire-and-forget: one email to the trusted contact, a
dispatch request, and nobody ever confirming that a human was actually
coming — while the Safety screen's queue sat one card up with exactly the
accept-by-name loop this needs, fed only by beacon alarms. Now every way
help gets summoned is answered on one surface, with the doors that already
exist on every client: the trip is an alarm, accepting it names a
responder, escalating pages the trusted channel again, and the person's
own "I'm okay" still ends everything.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jim import crashwatch
from jim.tests.conftest import enroll


def _tripped(client, **extra):
    user = enroll(client)
    client.put(f"/crash-watch/{user}", json={
        "trusted_name": "Rosa", "trusted_channel": "rosa@example.com",
        "attempts": 2, "window_minutes": 5.0, **extra})
    client.post(f"/monitor/{user}", json={"blood_oxygen": 85})
    later = datetime.now(timezone.utc) + timedelta(hours=1)
    st = crashwatch.sweep(user, now=later)
    assert st["tripped"] is True
    return user


def test_a_trip_stands_first_on_the_alarm_queue(client):
    user = _tripped(client)
    rows = client.get(f"/users/{user}/alarms").json()
    assert rows and rows[0]["id"] == crashwatch.ALARM_ID
    first = rows[0]
    assert first["kind"] == "crash_watch"
    assert first["state"] == "open"
    assert first["accepted_by"] is None
    # A plain string, the queue's one shape — the shells decode [String].
    assert "Rosa was contacted" in first["messages"][0]


def test_the_tier_says_what_the_arming_chose(client):
    user = _tripped(client, contact_emergency_services=False)
    row = client.get(f"/users/{user}/alarms").json()[0]
    assert row["tier"] == "notify_contact"
    user2 = _tripped(client, contact_emergency_services=True)
    row2 = client.get(f"/users/{user2}/alarms").json()[0]
    assert row2["tier"] == "emergency_services"


def test_accepting_names_a_responder(client):
    user = _tripped(client)
    r = client.post(
        f"/users/{user}/alarms/{crashwatch.ALARM_ID}/accept",
        json={"responder": "Rosa"})
    assert r.status_code == 200
    assert r.json()["accepted_by"] == "Rosa"
    # Accepting says somebody is coming; it does not close the alarm.
    row = client.get(f"/users/{user}/alarms").json()[0]
    assert row["state"] == "open" and row["accepted_by"] == "Rosa"
    # And a nameless acceptance is refused, same as the relay's.
    r = client.post(
        f"/users/{user}/alarms/{crashwatch.ALARM_ID}/accept",
        json={"responder": "  "})
    assert r.status_code == 422


def test_clearing_resolves_the_trip_and_keeps_who_answered(client):
    user = _tripped(client)
    client.post(f"/users/{user}/alarms/{crashwatch.ALARM_ID}/accept",
                json={"responder": "Rosa"})
    r = client.post(f"/users/{user}/alarms/{crashwatch.ALARM_ID}/clear")
    assert r.status_code == 200 and r.json()["state"] == "cleared"
    assert client.get(f"/users/{user}/alarms").json() == []
    st = client.get(f"/crash-watch/{user}").json()
    assert st["tripped"] is False
    assert st["accepted_by"] == "Rosa"


def test_the_persons_own_answer_still_ends_it(client):
    """The all-clear from the only voice that can give it — unchanged."""
    user = _tripped(client)
    client.post(f"/crash-watch/{user}/respond")
    assert client.get(f"/users/{user}/alarms").json() == []


def test_escalating_pages_the_trusted_channel_again(client):
    user = _tripped(client)
    r = client.post(
        f"/users/{user}/alarms/{crashwatch.ALARM_ID}/escalate")
    assert r.status_code == 200
    out = r.json()
    assert out["re_paged"] == "Rosa"
    # With no mail transport configured the delivery is honest about it.
    assert out["delivery"] in ("console", "email", "email_failed")


def test_the_pages_ledger_shows_the_trips_page(client):
    """"What went out" answers for the crash watch too — a page that failed
    to deliver is the one the morning most needs to know about."""
    user = _tripped(client)
    client.post(f"/users/{user}/alarms/{crashwatch.ALARM_ID}/escalate")
    pages = client.get(f"/users/{user}/pages").json()
    ours = [p for p in pages if p.get("responder") == "Rosa"]
    assert len(ours) >= 2          # the trip's page, and the escalation's


def test_no_trip_means_no_crash_alarm_and_a_404_on_its_doors(client):
    user = enroll(client)
    assert client.get(f"/users/{user}/alarms").json() == []
    assert client.post(
        f"/users/{user}/alarms/{crashwatch.ALARM_ID}/clear").status_code == 404
    assert client.post(
        f"/users/{user}/alarms/{crashwatch.ALARM_ID}/accept",
        json={"responder": "Rosa"}).status_code == 404
