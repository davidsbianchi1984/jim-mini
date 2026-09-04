"""The contact call rings through the voice door.

`jim.dialer.call_contact` was the one function the cascade promised would
change when a transport was wired. It has: with JIM_VOICE_URL and
JIM_VOICE_SECRET set, the online kind chosen and offline mode off, a leg is
handed to the voice sidecar and the house's reference comes back onto the
row. Everything honest at the edges stays honest: no door, offline, or the
device path leaves the leg *prepared* as before; a door that refuses or does
not answer leaves it *unplaced* with the sentence, and the next person is
rung — never a pretended ring.
"""

from __future__ import annotations

import pytest

from jim import db, dialer, reachout, telephony

from .conftest import enroll
from .fakevoice import SITU, TWO, wire


def _actions(uid):
    return [r["action"] for r in db.connect().execute(
        "SELECT action FROM audit WHERE user_id=? ORDER BY seq", (uid,)).fetchall()]


def _rows(rid):
    return reachout.status(rid)["calls"]


# --- the ring ------------------------------------------------------------------

def test_a_wired_ready_door_places_the_leg_and_records_the_house(client, monkeypatch):
    uid = enroll(client)
    fake = wire(monkeypatch)
    out = reachout.begin(uid, TWO, SITU)
    assert out["status"] == "calling"
    assert out["dialer"]["placed"] is True and out["dialer"]["prepared"] is False
    assert out["dialer"]["provider_call_id"] == "CA0001"
    call = out["call"]
    assert call["placed"] == 1 and call["provider"] == "twilio"
    assert call["provider_call_id"] == "CA0001" and call["placed_at"]
    body = fake.placed[0]
    assert body["call_id"] == call["id"] and body["to"] == "+15551110000"
    assert body["opening"].startswith("This is JIM calling on behalf of Ada")
    assert body == {**body, "language": "en", "provider": "twilio",
                    "limits": {"ring_seconds": 25, "max_call_seconds": 600,
                               "machine_detection": True}}
    assert "contact.called" in _actions(uid)
    row = _rows(out["reachout_id"])[0]
    assert row == {**row, "placed": True, "provider": "twilio",
                   "provider_call_id": "CA0001", "status": "ringing",
                   "turns": 0, "ended": None, "placement": None}


@pytest.mark.parametrize("channel,to", [
    ("(555) 111-0000", "+15551110000"),
    ("555.111.0000", "+15551110000"),
    ("1 555 111 0000", "+15551110000"),
    ("+1 555-111-0000", "+15551110000"),
    ("0044 20 7946 0958", "+442079460958"),
    ("+52 55 1234 5678", "+525512345678"),
])
def test_the_number_goes_out_the_way_the_house_wants_it(channel, to):
    assert telephony.normalize(channel) == to
    assert telephony.refuse_unless_dialable(channel) == to


def test_the_house_gets_the_normalised_number(client, monkeypatch):
    uid = enroll(client)
    fake = wire(monkeypatch)
    reachout.begin(uid, [{"name": "Rosa", "channel": "(555) 111-0000"}], SITU)
    assert fake.placed[0]["to"] == "+15551110000"


# --- honest at the edges -------------------------------------------------------

def test_a_house_that_refuses_the_number_leaves_the_leg_unplaced_and_rings_the_next(
        client, monkeypatch):
    uid = enroll(client)
    fake = wire(monkeypatch, refuse_to=("+15551110000",))
    out = reachout.begin(uid, TWO, SITU)
    assert out["status"] == "calling" and out["call"]["name"] == "Sam"
    rows = _rows(out["reachout_id"])
    assert rows[0]["status"] == "unplaced" and rows[0]["placed"] is False
    assert "the house refused this number" in rows[0]["placement"]
    assert rows[1]["status"] == "ringing" and rows[1]["placed"] is True
    acts = _actions(uid)
    assert acts.count("contact.unplaced") == 1 and acts.count("contact.called") == 1
    assert [b["to"] for b in fake.placed] == ["+15552220000"]


def test_a_door_that_does_not_answer_is_an_unplaced_leg_not_a_pretended_ring(
        client, monkeypatch):
    uid = enroll(client)
    fake = wire(monkeypatch, down=True)
    out = reachout.begin(uid, TWO, SITU)          # never raises
    assert out["status"] == "exhausted"
    rows = _rows(out["reachout_id"])
    assert [r["status"] for r in rows] == ["unplaced", "unplaced"]
    for r in rows:
        assert "did not answer" in r["placement"]
        assert "http://voice:8800" in r["placement"]
        assert "refusing to pretend" in r["placement"]
    assert fake.placed == []
    assert [p for _, p, _ in fake.seen].count("/calls") == 2
    acts = _actions(uid)
    assert acts.count("contact.unplaced") == 2 and "reachout.exhausted" in acts
    assert "contact.called" not in acts


def test_a_door_that_refuses_jims_secret_is_an_unplaced_leg(client, monkeypatch):
    uid = enroll(client)
    wire(monkeypatch, refuse_secret=True)
    out = reachout.begin(uid, [TWO[0]], SITU)
    row = _rows(out["reachout_id"])[0]
    assert row["status"] == "unplaced"
    assert "invalid voice adapter token" in row["placement"]


def test_with_no_door_configured_the_leg_is_prepared_as_before(client):
    uid = enroll(client)
    out = reachout.begin(uid, TWO, SITU)
    assert out["dialer"]["prepared"] is True and out["dialer"]["placed"] is False
    assert "telephony transport" in out["dialer"]["reason"]
    row = _rows(out["reachout_id"])[0]
    assert row["status"] == "ringing" and row["placed"] is False
    assert row["provider"] is None and row["provider_call_id"] is None
    assert dialer.posture()["wired"] is False


def test_offline_mode_keeps_the_call_home_even_with_a_door(client, monkeypatch):
    uid = enroll(client)
    fake = wire(monkeypatch)
    monkeypatch.setenv("JIM_OFFLINE", "1")
    out = reachout.begin(uid, [TWO[0]], SITU)
    assert out["dialer"]["placed"] is False
    assert "offline mode is on" in out["dialer"]["reason"]
    assert fake.seen == []


def test_the_device_path_is_honestly_unwired(client, monkeypatch):
    uid = enroll(client)
    fake = wire(monkeypatch)
    monkeypatch.setenv("JIM_TELEPHONY_KIND", "device_sim")
    out = reachout.begin(uid, [TWO[0]], SITU)
    assert out["dialer"]["placed"] is False
    assert "device path" in out["dialer"]["reason"]
    assert fake.seen == []
    assert dialer.posture()["device_sim_wired"] is False


def test_the_real_wire_reports_a_closed_door_as_unreachable(monkeypatch):
    monkeypatch.setenv("JIM_VOICE_URL", "http://127.0.0.1:9")
    monkeypatch.setenv("JIM_VOICE_SECRET", "x")
    with pytest.raises(telephony.SidecarUnreachable, match="did not answer"):
        telephony._request("GET", "/standing", timeout=1.0)


def test_the_wire_carries_the_bearer_and_nothing_else_opens_it(monkeypatch):
    seen = {}

    class _Resp:
        status = 201

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self):
            return b'{"placed": true, "provider": "twilio", "provider_call_id": "CA9"}'

    def fake_open(req, timeout=5.0):
        seen["url"] = req.full_url
        seen["auth"] = req.get_header("Authorization")
        seen["method"] = req.get_method()
        return _Resp()

    monkeypatch.setenv("JIM_VOICE_URL", "http://voice:8800/")
    monkeypatch.setenv("JIM_VOICE_SECRET", "s3cret")
    monkeypatch.setattr(telephony.urllib.request, "urlopen", fake_open)
    got = telephony.place("rcl_1", "+15551110000", "hello")
    assert got == {"provider": "twilio", "provider_call_id": "CA9"}
    assert seen == {"url": "http://voice:8800/calls", "auth": "Bearer s3cret",
                    "method": "POST"}
