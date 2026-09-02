"""The emergency-services dialer is built to the send and held there.

The owner's line: build the emergency connection out so JIM can make it, but
the dialer must never actually place a 911 call. These tests pin that line
where it lives — a source constant, off — and prove the two ways it stays
safe:

* held, and honest: `place()` assembles and routes the connection, records
  `dial.held`, and returns a receipt that never claims a call;
* armed without a transport: flipping the constant does not buy a silent
  call — it raises, because no code path in the dialer emits to a network.

If a future change wires a real provider under review, these tests are the
ones that should have to change on purpose — a green suite must never quietly
coexist with a dialer that has started placing 911 calls.
"""

import pytest

from jim import audit, db, dialer


@pytest.fixture()
def a_db(tmp_path, monkeypatch):
    monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
    db.reset()
    yield
    db.reset()


def test_the_send_is_off_in_source():
    """Not an env var, not a column — a source constant, and it is False."""
    assert dialer.SEND_ENABLED is False


def test_place_makes_the_connection_but_holds_the_send(a_db):
    receipt = dialer.place(
        {"who": "Rosa", "concern": "blood_oxygen 84", "channels": []},
        user_id="usr_x")
    # The connection was made — assembled and routed to the number.
    assert receipt["assembled"] is True
    assert receipt["routed"] is True
    assert receipt["to"] == dialer.EMERGENCY_NUMBER
    # And the send was held. Never a claim that a call happened.
    assert receipt["placed"] is False
    assert receipt["held"] is True
    assert "does not place the call" in receipt["reason"]


def test_a_held_send_is_recorded_not_dropped(a_db):
    dialer.place({"who": "Rosa", "concern": "fall"}, user_id="usr_rec")
    rows = [r["action"] for r in db.connect().execute(
        "SELECT action FROM audit WHERE user_id=?", ("usr_rec",)).fetchall()]
    assert "dial.held" in rows, (
        "a held emergency connection left no trace — it must be recorded")


def test_arming_without_a_transport_raises_rather_than_dialing(monkeypatch,
                                                               a_db):
    """The safe direction for a mistake to fall: flip the flag with nothing
    wired and the dialer refuses loudly instead of pretending — or worse,
    dialing."""
    monkeypatch.setattr(dialer, "SEND_ENABLED", True)
    with pytest.raises(dialer.DialerArmedWithoutTransport):
        dialer.place({"who": "Rosa", "concern": "fall"}, user_id="usr_y")


def test_the_posture_says_it_is_built_and_held():
    p = dialer.posture()
    assert p["built"] is True
    assert p["send_enabled"] is False
    assert p["would_reach"] == dialer.EMERGENCY_NUMBER
