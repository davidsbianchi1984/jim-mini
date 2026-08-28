"""How old is the reading, and am I allowed to act on something that old.

The network-engineering read of claim 23 ("real-time biometric monitoring
data during the interaction"): real-time is a network word, and between
the wrist and the decision sit five hops this code cannot see. So the
application stops asking *what is the reading* and asks *how old is it* —
a staleness contract, three parts, and a number you can produce on demand
when somebody finally asks what real-time means in seconds.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jim import db, freshness

from jim.tests.conftest import enroll  # noqa: F401


def _iso(**delta) -> str:
    return (datetime.now(timezone.utc) - timedelta(**delta)).isoformat()


# -- part 1: timestamp at the source -----------------------------------------

def test_the_age_is_the_sources_not_the_queues(client):
    """A reading that sat in a phone's outbox arrives old and must look
    old — the age comes off the device's own clock at both ends, so the
    device's skew cancels out of it entirely."""
    user = enroll(client)
    r = client.post(f"/monitor/{user}", json={
        "heart_rate": 72,
        "observed_at": _iso(minutes=4),
        "device_now": _iso(seconds=0)})
    assert r.status_code == 200, r.text
    aged = r.json()["freshness"]
    assert 230_000 < aged["age_ms"] < 250_000, (
        "a four-minute-old reading was stamped on arrival and looks newborn")


def test_a_reading_with_no_stamps_is_of_unknown_age(client):
    """Three shipped clients predate the stamps. Their readings are kept —
    and their age is unknown, which is stale, never fresh."""
    user = enroll(client)
    client.post(f"/monitor/{user}", json={"heart_rate": 72})
    assert freshness.read(user, "display")["state"] == "stale", (
        "an unstamped reading passed as fresh — unknown age became zero age")


def test_a_future_observed_at_is_not_clamped_to_zero(client):
    user = enroll(client)
    client.post(f"/monitor/{user}", json={
        "heart_rate": 72,
        "observed_at": _iso(minutes=-5),
        "device_now": _iso(seconds=0)})
    row = db.connect().execute(
        "SELECT age_ms FROM freshness_readings WHERE user_id=?"
        " ORDER BY rowid DESC LIMIT 1", (user,)).fetchone()
    assert row["age_ms"] is None, (
        "a reading from the future was clamped instead of being logged as "
        "a skew measurement that failed")


# -- part 2: every consumer declares a window --------------------------------

def test_fresh_inside_the_window_stale_past_it(client):
    user = enroll(client)
    client.post(f"/monitor/{user}", json={
        "heart_rate": 72, "observed_at": _iso(seconds=2),
        "device_now": _iso(seconds=0)})
    assert freshness.read(user, "display")["state"] == "fresh"
    client.post(f"/monitor/{user}", json={
        "heart_rate": 70, "observed_at": _iso(minutes=2),
        "device_now": _iso(seconds=0)})
    assert freshness.read(user, "display")["state"] == "stale"
    assert freshness.read(user, "trend")["state"] == "fresh", (
        "one global window — a trend consumer refused data that is "
        "exactly what a trend is made of")


def test_no_reading_ever_is_unreachable_not_stale(client):
    user = enroll(client)
    assert freshness.read(user, "escalation")["state"] == "unreachable"


def test_an_undeclared_consumer_is_refused():
    """The contract's whole posture: no code path reads a value without
    declaring the age it will act on."""
    try:
        freshness.read("usr_nobody", "vibes")
    except KeyError:
        return
    raise AssertionError("an undeclared consumer read a biometric value")


# -- part 3: the two silences ------------------------------------------------

def test_readings_dark_heartbeat_alive_is_the_person(client):
    user = enroll(client)
    r = client.post(f"/heartbeat/{user}", json={"device_now": _iso()})
    assert r.status_code == 201, r.text
    assert freshness.silences(user)["verdict"] == "person-quiet", (
        "the watch is off the wrist and the product blamed the network")


def test_both_dark_is_the_network(client):
    user = enroll(client)
    assert freshness.silences(user)["verdict"] == "network-dark"


def test_current_readings_are_alive_whatever_the_heartbeat(client):
    user = enroll(client)
    client.post(f"/monitor/{user}", json={
        "heart_rate": 72, "observed_at": _iso(seconds=1),
        "device_now": _iso(seconds=0)})
    assert freshness.silences(user)["verdict"] == "alive"


# -- the number you can produce on demand ------------------------------------

def test_the_p95_at_decision_is_measured_not_designed(client):
    user = enroll(client)
    client.post(f"/monitor/{user}", json={
        "heart_rate": 72, "observed_at": _iso(seconds=3),
        "device_now": _iso(seconds=0)})
    for _ in range(5):
        freshness.read(user, "conditioning")
    r = client.get(f"/freshness/{user}")
    assert r.status_code == 200, r.text
    facts = r.json()["consumers"]["conditioning"]
    assert facts["p95_age_at_decision_ms"] is not None, (
        "the one number a deposition will ask for is not being measured")
    assert facts["decisions"].get("fresh", 0) >= 1
    assert r.json()["ingress"]["readings"] >= 1


def test_every_shell_pays_the_heartbeat_door():
    """The BLE link to the watch lives in a shell; each owed the beat, and
    the second doorless close paid it. The guard flips with the debt: a
    shell that loses its heartbeat call has reopened a door this file
    watched close, and the ledger must say so again before this passes."""
    from pathlib import Path
    root = Path(__file__).resolve().parent
    repo = root.parents[1]
    clients = {
        "ios": repo / "native/ios/Sources/ApiClient.swift",
        "android": repo / "native/android/app/src/main/java/app/jim/guardian/ApiClient.kt",
        "windows": repo / "native/windows/ApiClient.cs",
    }
    for shell, path in clients.items():
        assert "/heartbeat/" in path.read_text(encoding="utf-8"), (
            f"the {shell} client no longer calls the heartbeat door")
        ledger = (root / f"{shell}_doorless.txt").read_text(encoding="utf-8")
        assert "POST /heartbeat/{user_id}" not in ledger, (
            f"the {shell} ledger still owes a door its client pays")
