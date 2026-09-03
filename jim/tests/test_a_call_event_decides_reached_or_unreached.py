"""A call event decides reached or unreached.

The phone line's word on a leg — a pickup, or how it ended — arrives at one
door, and that door is the one place *reached* is decided: pressed 1 and
heard a turn, then the line ended, is reached; everything else is unreached
with the word for why. The row is its own mutex, so a house that repeats
itself advances the cascade once; a placed leg nobody reported on is settled
by the crash watch's sweep and never by a read.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from jim import crashwatch, db, reachout, telephony

from .conftest import enroll
from .fakevoice import AS_SIDECAR, SITU, TWO, wire


def _actions(uid):
    return [r["action"] for r in db.connect().execute(
        "SELECT action FROM audit WHERE user_id=? ORDER BY seq", (uid,)).fetchall()]


def _begin(client, monkeypatch, contacts=TWO, **kw):
    uid = enroll(client)
    fake = wire(monkeypatch)
    out = reachout.begin(uid, contacts, SITU, **kw)
    return uid, fake, out


def _rows(rid):
    return reachout.status(rid)["calls"]


def _count():
    return db.connect().execute("SELECT COUNT(*) FROM reachout_calls").fetchone()[0]


def _event(client, cid, word, **extra):
    r = client.post(f"/reachout/call/{cid}/event", json={"event": word, **extra},
                    headers=AS_SIDECAR)
    assert r.status_code == 200, r.text
    return r.json()


def _age(cid, **stamps):
    """Backdate a row's stamps directly — the only way to make time pass."""
    sets = ", ".join(f"{k}=?" for k in stamps)
    db.connect().execute(f"UPDATE reachout_calls SET {sets} WHERE id=?",
                         (*stamps.values(), cid))
    db.connect().commit()


def _ago(seconds):
    return (datetime.now(timezone.utc) - timedelta(seconds=seconds)).isoformat()


# --- the pickup -----------------------------------------------------------------

def test_answered_is_noted_and_the_line_asks_for_the_key(client, monkeypatch):
    uid, fake, out = _begin(client, monkeypatch)
    cid = out["call"]["id"]
    body = _event(client, cid, "answered", detail="AnsweredBy=human")
    assert body["decided"] == "noted" and body["status"] == "ringing"
    line = body["line"]
    assert line["then"] == "gather_digit"
    assert line["say"].startswith("This is JIM calling on behalf of Ada")
    assert line["again"] and line["close"] and line["trouble"]
    assert line["language"] == "en"
    assert reachout._call(cid)["answered_at"]
    assert "contact.answered" in _actions(uid)
    ev = reachout.events(cid)
    assert len(ev) == 1
    assert ev[0] == {**ev[0], "event": "answered", "detail": "AnsweredBy=human",
                     "note": ""}
    # Told twice, the pickup time is kept, not moved.
    first = reachout._call(cid)["answered_at"]
    _event(client, cid, "answered")
    assert reachout._call(cid)["answered_at"] == first


# --- the decision ------------------------------------------------------------------

def test_pressed_one_heard_a_turn_and_the_line_ended_is_reached(client, monkeypatch):
    uid, fake, out = _begin(client, monkeypatch)
    cid = out["call"]["id"]
    assert reachout.consent(cid, "1")["status"] == "consented"
    said = client.post(f"/reachout/call/{cid}/say", json={"heard": ""},
                       headers=AS_SIDECAR).json()
    assert said["status"] == "talking" and said["line"]["then"] == "gather_speech"
    body = _event(client, cid, "completed", seconds=42, detail="CallStatus=completed")
    assert body["decided"] == "reached" and body["status"] == "reached"
    row = reachout._call(cid)
    assert row["status"] == "reached" and row["ended"] == "completed"
    assert row["turns"] == 1
    assert reachout.status(out["reachout_id"])["status"] == "reached"
    assert _count() == 1
    assert "contact.reached" in _actions(uid)


@pytest.mark.parametrize("word", ["completed", "failed", "canceled"])
def test_a_line_that_ended_mid_conversation_is_still_reached(client, monkeypatch, word):
    uid, fake, out = _begin(client, monkeypatch)
    cid = out["call"]["id"]
    reachout.consent(cid, "1")
    reachout.say(cid, "")
    body = _event(client, cid, word)
    assert body["decided"] == "reached"
    assert reachout._call(cid)["ended"] == word


def test_pressed_one_and_nothing_spoken_is_unreached(client, monkeypatch):
    uid, fake, out = _begin(client, monkeypatch)
    cid = out["call"]["id"]
    reachout.consent(cid, "1")
    body = _event(client, cid, "completed", seconds=9)
    assert body["decided"] == "unreached"
    assert body["status"] == "calling" and body["call"]["name"] == "Sam"
    row = reachout._call(cid)
    assert row["status"] == "unreached" and row["ended"] == "consented-unspoken"
    assert _count() == 2


def test_a_pickup_that_never_pressed_one_is_unreached(client, monkeypatch):
    uid, fake, out = _begin(client, monkeypatch)
    cid = out["call"]["id"]
    _event(client, cid, "answered")
    body = _event(client, cid, "completed", seconds=12)
    assert body["decided"] == "unreached"
    row = reachout._call(cid)
    assert row["status"] == "unreached"
    assert row["ended"] == "completed-without-consent"
    assert _count() == 2


@pytest.mark.parametrize("word", ["voicemail", "no-answer", "busy", "failed", "canceled"])
def test_the_lines_word_while_ringing_is_unreached_with_that_word(client, monkeypatch, word):
    uid, fake, out = _begin(client, monkeypatch)
    cid = out["call"]["id"]
    body = _event(client, cid, word, detail=f"CallStatus={word}")
    assert body["decided"] == "unreached"
    row = reachout._call(cid)
    assert row["status"] == "unreached" and row["ended"] == word
    assert "contact.unreached" in _actions(uid)
    assert _rows(out["reachout_id"])[1]["name"] == "Sam"


# --- once, however many times the house repeats itself ----------------------------

def test_a_repeated_status_callback_advances_the_cascade_once(client, monkeypatch):
    uid, fake, out = _begin(client, monkeypatch)
    cid = out["call"]["id"]
    assert _event(client, cid, "completed")["decided"] == "unreached"
    assert _count() == 2
    again = _event(client, cid, "completed")
    assert again["decided"] == "already" and again["already"] is True
    assert again["status"] == "unreached"
    assert _count() == 2
    ev = reachout.events(cid)
    assert [e["note"] for e in ev] == ["", "late"]


def test_no_choice_then_completed_advances_once(client, monkeypatch):
    uid, fake, out = _begin(client, monkeypatch)
    cid = out["call"]["id"]
    nxt = reachout.consent(cid, "")
    assert nxt["status"] == "calling" and nxt["call"]["name"] == "Sam"
    assert reachout._call(cid)["ended"] == "no-choice"
    assert _count() == 2
    assert _event(client, cid, "completed")["decided"] == "already"
    assert _count() == 2


def test_a_late_word_after_reached_changes_nothing(client, monkeypatch):
    uid, fake, out = _begin(client, monkeypatch)
    cid = out["call"]["id"]
    reachout.consent(cid, "1")
    reachout.say(cid, "")
    reachout.reached(cid)
    late = _event(client, cid, "completed")
    assert late["decided"] == "already"
    assert reachout.status(out["reachout_id"])["status"] == "reached"
    assert reachout.events(cid)[-1]["note"] == "late"
    assert _count() == 1


def test_a_declined_leg_then_a_late_completed(client, monkeypatch):
    uid, fake, out = _begin(client, monkeypatch)
    cid = out["call"]["id"]
    reachout.consent(cid, "2")
    assert reachout._call(cid)["ended"] == "declined"
    assert _event(client, cid, "completed")["decided"] == "already"
    assert _count() == 2


def test_a_key_that_arrives_after_the_leg_ended_says_already(client, monkeypatch):
    uid, fake, out = _begin(client, monkeypatch)
    cid = out["call"]["id"]
    _event(client, cid, "no-answer")
    r = client.post(f"/reachout/call/{cid}/consent", json={"digit": "1"},
                    headers=AS_SIDECAR)
    assert r.status_code == 200
    assert r.json()["already"] is True
    assert r.json()["line"]["then"] == "hangup"
    assert _count() == 2


# --- refusals and ceilings ---------------------------------------------------------

def test_an_unknown_word_is_refused_naming_the_field(client, monkeypatch):
    uid, fake, out = _begin(client, monkeypatch)
    cid = out["call"]["id"]
    r = client.post(f"/reachout/call/{cid}/event", json={"event": "ringing"},
                    headers=AS_SIDECAR)
    assert r.status_code == 422
    assert "phone line" in r.text
    with pytest.raises(ValueError, match="not an event the phone line reports"):
        reachout.event(cid, "ringing")
    assert reachout.events(cid) == []


def test_the_turn_ceiling_hangs_up_with_the_closing(client, monkeypatch):
    monkeypatch.setattr(telephony, "MAX_TURNS", 2)
    uid, fake, out = _begin(client, monkeypatch)
    cid = out["call"]["id"]
    reachout.consent(cid, "1")
    first = client.post(f"/reachout/call/{cid}/say", json={"heard": ""},
                       headers=AS_SIDECAR).json()
    assert first["line"]["then"] == "gather_speech"
    assert first["line"]["again"] == telephony.phrases()["silence"]
    second = client.post(f"/reachout/call/{cid}/say", json={"heard": "and then?"},
                        headers=AS_SIDECAR).json()
    assert second["line"]["then"] == "hangup"
    assert second["line"]["say"].endswith(telephony.phrases()["closing"])
    assert reachout._call(cid)["turns"] == 2


def test_a_missing_call_is_a_404_on_every_door(client):
    enroll(client)
    for door, body in (("event", {"event": "answered"}), ("consent", {"digit": "1"}),
                       ("say", {"heard": ""}), ("reached", None), ("unreached", None)):
        r = client.post(f"/reachout/call/rcl_nope/{door}", json=body)
        assert r.status_code == 404, (door, r.text)
        assert "no such call" in r.text


# --- a ring nobody reported on --------------------------------------------------------

def test_a_placed_ring_nobody_reported_on_is_settled_by_the_sweep_only(client, monkeypatch):
    uid, fake, out = _begin(client, monkeypatch)
    cid = out["call"]["id"]
    _age(cid, placed_at=_ago(telephony.RING_SECONDS + reachout.STALE_RING_GRACE_S + 5))
    # Reads never settle.
    assert reachout.status(out["reachout_id"])["calls"][0]["status"] == "ringing"
    assert reachout.for_user(uid)[0]["calls"][0]["status"] == "ringing"
    assert _count() == 1
    assert reachout.settle_stale(uid) == [cid]
    row = reachout._call(cid)
    assert row["status"] == "unreached" and row["ended"] == "no-report"
    assert _count() == 2 and _rows(out["reachout_id"])[1]["name"] == "Sam"
    # Settled once; the next sweep finds nothing stale.
    assert reachout.settle_stale(uid) == []


def test_a_fresh_ring_is_left_alone(client, monkeypatch):
    uid, fake, out = _begin(client, monkeypatch)
    assert reachout.settle_stale(uid) == []
    assert reachout._call(out["call"]["id"])["status"] == "ringing"


def test_a_live_conversation_is_never_settled_under(client, monkeypatch):
    uid, fake, out = _begin(client, monkeypatch)
    cid = out["call"]["id"]
    reachout.consent(cid, "1")
    reachout.say(cid, "")
    _age(cid, placed_at=_ago(3600))                 # placed an hour ago …
    assert reachout.settle_stale(uid) == []           # … but the row moved on every turn
    assert reachout._call(cid)["status"] == "talking"
    _age(cid, updated_at=_ago(telephony.MAX_CALL_SECONDS + reachout.STALE_TALK_GRACE_S + 5))
    assert reachout.settle_stale(uid) == [cid]
    assert reachout._call(cid)["ended"] == "no-report"


def test_a_prepared_leg_has_no_line_to_go_quiet(client):
    uid = enroll(client)
    out = reachout.begin(uid, TWO, SITU)              # no door: prepared, placed=0
    cid = out["call"]["id"]
    _age(cid, placed_at=_ago(3600), updated_at=_ago(3600), created_at=_ago(3600))
    assert reachout.settle_stale(uid) == []
    assert reachout._call(cid)["status"] == "ringing"


def test_the_crash_watch_sweep_settles(client, monkeypatch):
    uid, fake, out = _begin(client, monkeypatch)
    cid = out["call"]["id"]
    _age(cid, placed_at=_ago(3600))
    crashwatch.sweep(uid)
    assert reachout._call(cid)["status"] == "unreached"
    assert reachout._call(cid)["ended"] == "no-report"


# --- the turn that lands after the line ended ------------------------------------------

def test_a_turn_that_lands_after_the_line_ended_does_not_resurrect_the_leg(client, monkeypatch):
    uid, fake, out = _begin(client, monkeypatch)
    cid = out["call"]["id"]
    reachout.consent(cid, "1")
    # The contact hangs up while the model is composing: the line's word
    # arrives first and the cascade moves on …
    assert _event(client, cid, "completed")["decided"] == "unreached"
    assert _count() == 2
    # … then the turn lands. It must not pull the leg back to talking.
    r = client.post(f"/reachout/call/{cid}/say", json={"heard": ""}, headers=AS_SIDECAR)
    assert r.status_code == 409
    row = reachout._call(cid)
    assert row["status"] == "unreached" and row["ended"] == "consented-unspoken"
    assert row["turns"] == 0
    assert _count() == 2


def test_the_wires_other_failures_are_unplaced_legs_not_stranded_ones(client, monkeypatch):
    uid = enroll(client)
    wire(monkeypatch)
    from jim import dialer

    def broken(*a, **k):
        raise RuntimeError("the wire caught fire")

    monkeypatch.setattr(dialer, "call_contact", broken)
    out = reachout.begin(uid, TWO, SITU)              # never raises
    assert out["status"] == "exhausted"
    rows = _rows(out["reachout_id"])
    assert [r["status"] for r in rows] == ["unplaced", "unplaced"]
    assert "RuntimeError: the wire caught fire" in rows[0]["placement"]
    assert _actions(uid).count("contact.unplaced") == 2
