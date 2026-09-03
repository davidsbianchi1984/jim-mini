"""The transport never carries 911.

The reach-out cascade rings real people through the voice door now
(jim/telephony.py). Three locks keep that transport away from emergency
services, and none of them is a setting:

* the 911 dialer's send is a source constant, still False, and the dialer's
  own path never touches the voice door — pinned by reading the source;
* the transport refuses an emergency short code before a request is built,
  whatever a contact's channel holds;
* a live, ready line changes nothing about the held rung: exhausting into it
  asks the door for nothing.
"""

from __future__ import annotations

import inspect
import pathlib

import pytest

from jim import dialer, reachout, telephony

from .conftest import enroll
from .fakevoice import SITU, TWO, wire

SOURCE = pathlib.Path(dialer.__file__).read_text()


def _actions(uid):
    from jim import db
    return [r["action"] for r in db.connect().execute(
        "SELECT action FROM audit WHERE user_id=? ORDER BY seq", (uid,)).fetchall()]


# --- the source ------------------------------------------------------------------

def test_the_send_is_still_held_in_source():
    assert "SEND_ENABLED = False" in SOURCE
    assert dialer.SEND_ENABLED is False


def test_the_911_path_never_names_the_voice_door():
    for fn in (dialer.place, dialer._transmit):
        src = inspect.getsource(fn)
        assert "telephony." not in src and "import telephony" not in src
    # The module reaches for the transport only inside a function — the
    # wiring question, the contact path, the posture read — never at import.
    for line in SOURCE.splitlines():
        if "import" in line and "telephony" in line:
            assert line.startswith("    "), line


def test_wiring_the_transport_does_not_open_the_send(client, monkeypatch):
    wire(monkeypatch)
    post = dialer.posture()
    assert post["transport_ready"] is True
    assert post["send_enabled"] is False


# --- the number rules --------------------------------------------------------------

@pytest.mark.parametrize("number", [
    "911", "+1911", "1911", "1-911", "9 1 1", "112", "999", "000", "110", "119",
])
def test_emergency_short_codes_are_refused_before_any_request(number):
    with pytest.raises(telephony.RefusedNumber, match="never to emergency services"):
        telephony.refuse_unless_dialable(number)


@pytest.mark.parametrize("channel", ["rosa@example.com", "123", "call me", "",
                                     "＋１５５５１１１００００", "+1555111000000000"])
def test_a_channel_that_is_not_a_number_is_refused(channel):
    with pytest.raises(telephony.RefusedNumber, match="not a phone number"):
        telephony.refuse_unless_dialable(channel)


def test_a_contact_whose_channel_is_911_is_unplaced_and_the_door_is_never_asked(
        client, monkeypatch):
    uid = enroll(client)
    fake = wire(monkeypatch)
    out = reachout.begin(uid, [{"name": "Bad", "channel": "911"}, TWO[1]], SITU)
    calls = reachout.status(out["reachout_id"])["calls"]
    assert calls[0]["status"] == "unplaced"
    assert "never to emergency services" in calls[0]["placement"]
    assert calls[1]["status"] == "ringing" and calls[1]["placed"] is True
    assert [b["to"] for b in fake.placed] == ["+15552220000"]
    assert "contact.unplaced" in _actions(uid)


# --- the held rung, with a live line ---------------------------------------------

def test_the_held_rung_asks_the_door_for_nothing(client, monkeypatch):
    uid = enroll(client)
    fake = wire(monkeypatch)
    dialer.place({"who": "Ada", "about": "a fall", "reached_no_contact": True},
                 user_id=uid)
    assert fake.placed == []
    assert not [p for _, p, _ in fake.seen if p == "/calls"]
    assert "dial.held" in _actions(uid)


def test_exhausting_into_the_911_rung_never_opens_the_wire(client, monkeypatch):
    uid = enroll(client)
    fake = wire(monkeypatch)
    out = reachout.begin(uid, [TWO[0]], SITU, life_threatening=True)
    spent = reachout.event(out["call"]["id"], "no-answer")
    assert spent["status"] == "exhausted"
    assert spent["emergency_services"] is not None
    # Rosa's leg was the only thing the door was ever asked for.
    assert [b["to"] for b in fake.placed] == ["+15551110000"]
    assert "dial.held" in _actions(uid)
