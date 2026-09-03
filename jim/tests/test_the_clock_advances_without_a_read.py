"""The clock advances without a read.

Every deadline used to move only when something looked. The ticker
(jim/ticker.py) sweeps the running clocks — an open crash-watch question,
an armed vigil, a placed reach-out leg still live — through the same
functions the reads call, on its own thread, every JIM_TICK_SECONDS. Off in
this suite (conftest sets 0), so every test here turns the clock by hand
and the one that starts a thread stops it.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

import pytest

from jim import crashwatch, db, reachout, ticker, vigil

from .conftest import enroll
from .fakevoice import SITU, TWO, wire


def _arm(client, uid):
    r = client.put(f"/crash-watch/{uid}", json={
        "trusted_name": "Rosa", "trusted_channel": "rosa@example.com",
        "attempts": 3, "window_minutes": 5.0,
        "contact_emergency_services": False})
    assert r.status_code == 200, r.text


def _open(client, uid):
    r = client.post(f"/monitor/{uid}", json={"blood_oxygen": 85})
    assert r.status_code == 200 and r.json()["detected"] is True
    assert crashwatch.status(uid)["asking"] is True


def _later(minutes=20):
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)


# --- whose clock is running ------------------------------------------------------------

def test_only_running_clocks_are_due(client):
    a = enroll(client)
    _arm(client, a)
    _open(client, a)                               # an open question
    b = enroll(client)
    _arm(client, b)                                # armed, nothing open
    c = enroll(client)
    r = client.put(f"/vigil/{c}", json={"steward_name": "Sam",
                                        "steward_channel": "sam@example.com",
                                        "quiet_days": 2})
    assert r.status_code == 200, r.text
    due = ticker.due_users()
    assert due["crash"] == {a}
    assert c in due["vigil"] and a not in due["vigil"] and b not in due["vigil"]
    assert due["calls"] == set()


def test_a_placed_live_leg_is_a_running_clock_and_a_prepared_one_is_not(client, monkeypatch):
    a = enroll(client)
    reachout.begin(a, TWO, SITU)                   # no line: prepared, placed=0
    assert ticker.due_users()["calls"] == set()
    b = enroll(client)
    wire(monkeypatch)
    reachout.begin(b, TWO, SITU)                   # placed=1, ringing
    assert ticker.due_users()["calls"] == {b}


# --- a tick is a read nobody had to make -------------------------------------------------

def test_a_tick_trips_an_expired_watch_without_anyone_looking(client):
    uid = enroll(client)
    _arm(client, uid)
    _open(client, uid)
    out = ticker.tick(now=_later(20))
    assert out == {"swept": 1, "due": {"crash": 1, "vigil": 0, "calls": 0},
                   "error": None}
    st = crashwatch.status(uid)
    assert st["tripped"] is True and st["asking"] is False
    p = ticker.posture()
    assert p["ticks"] == 1 and p["last_swept"] == 1 and p["last_tick_at"]


def test_a_tick_re_asks_before_it_trips(client):
    uid = enroll(client)
    _arm(client, uid)
    _open(client, uid)
    ticker.tick(now=_later(6))
    st = crashwatch.status(uid)
    assert st["asking"] is True and st["attempt"] == 2 and st["tripped"] is False


def test_a_tick_settles_a_placed_leg_nobody_reported_on(client, monkeypatch):
    uid = enroll(client)
    wire(monkeypatch)
    out = reachout.begin(uid, TWO, SITU)
    cid = out["call"]["id"]
    db.connect().execute(
        "UPDATE reachout_calls SET placed_at=? WHERE id=?",
        ((datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(), cid))
    db.connect().commit()
    assert ticker.tick()["swept"] == 1
    row = reachout._call(cid)
    assert row["status"] == "unreached" and row["ended"] == "no-report"
    # The next contact rang from inside the tick, and is now the running clock.
    assert reachout.status(out["reachout_id"])["calls"][1]["name"] == "Sam"
    assert ticker.due_users()["calls"] == {uid}


def test_the_vigil_is_swept_too(client, monkeypatch):
    uid = enroll(client)
    client.put(f"/vigil/{uid}", json={"steward_name": "Sam",
                                      "steward_channel": "sam@example.com",
                                      "quiet_days": 2})
    seen = []
    monkeypatch.setattr(vigil, "sweep", lambda u: seen.append(u))
    assert ticker.tick()["swept"] == 1
    assert seen == [uid]


def test_a_user_with_nothing_running_is_not_touched(client, monkeypatch):
    uid = enroll(client)
    _arm(client, uid)                              # armed, no question
    calls = []
    monkeypatch.setattr(crashwatch, "sweep", lambda u, now=None: calls.append(u))
    assert ticker.tick() == {"swept": 0, "due": {"crash": 0, "vigil": 0, "calls": 0},
                             "error": None}
    assert calls == []


def test_one_failing_clock_does_not_stop_the_others(client, monkeypatch):
    a = enroll(client)
    _arm(client, a)
    _open(client, a)
    b = enroll(client)
    _arm(client, b)
    _open(client, b)
    real = crashwatch.sweep

    def flaky(uid, now=None):
        if uid == a:
            raise RuntimeError("boom")
        return real(uid, now=now)

    monkeypatch.setattr(crashwatch, "sweep", flaky)
    out = ticker.tick(now=_later(20))
    assert out["swept"] == 1 and "boom" in out["error"]
    assert crashwatch.status(b)["tripped"] is True
    assert ticker.posture()["last_error"].startswith(f"crash watch {a}")


# --- the setting, the thread, the posture ------------------------------------------------

@pytest.mark.parametrize("raw,want", [
    ("", 30), ("abc", 30), ("0", 0), ("-5", 0), ("2", 5), ("45", 45), ("12.9", 12),
])
def test_the_interval_is_read_honestly(monkeypatch, raw, want):
    monkeypatch.setenv("JIM_TICK_SECONDS", raw)
    assert ticker.seconds() == want


def test_off_means_no_thread_and_says_so(client):
    assert ticker.start() is None
    p = ticker.posture()
    assert p["running"] is False and p["every_seconds"] == 0
    assert "JIM_TICK_SECONDS=0" in p["note"]


def test_on_means_a_thread_that_ticks_and_stops(client, monkeypatch):
    monkeypatch.setattr(ticker, "MIN_SECONDS", 1)
    monkeypatch.setenv("JIM_TICK_SECONDS", "1")
    thread = ticker.start()
    try:
        assert thread is not None and thread.daemon
        assert ticker.start() is thread             # idempotent
        deadline = time.monotonic() + 5
        while ticker.posture()["ticks"] < 1 and time.monotonic() < deadline:
            time.sleep(0.1)
        p = ticker.posture()
        assert p["running"] is True and p["ticks"] >= 1 and p["every_seconds"] == 1
        assert "every 1 seconds" in p["note"]
    finally:
        ticker.stop()
    assert ticker.posture()["running"] is False
    assert not thread.is_alive()


def test_the_status_door_carries_the_posture(client):
    uid = enroll(client)
    unarmed = client.get(f"/crash-watch/{uid}").json()
    assert unarmed["armed"] is False and unarmed["ticker"]["running"] is False
    _arm(client, uid)
    st = client.get(f"/crash-watch/{uid}").json()
    assert st["ticker"] == {**st["ticker"], "running": False, "every_seconds": 0}
    assert st["ticker"]["note"]
