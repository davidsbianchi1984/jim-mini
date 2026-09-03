"""The line answers.

Since 3.0.8 the dialer's posture said calls go both ways and answering
waits. A contact the cascade rang who rings the line back inside the
window reaches the conversation about the reach-out they were part of: a
leg of its own, direction in, consented by the act of calling, opened with
what they are calling back about, then the same grounded turns. Anyone
else hears one fixed sentence, in their language, and nothing is kept but
the audit. A call back never advances the cascade, and a cascade a call
back reached rings nobody more.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jim import db, dialer, reachout, telephony

from .conftest import enroll
from .fakevoice import AS_SIDECAR, SITU, TWO, wire


def _actions(uid=None):
    q = "SELECT action, ref FROM audit" + (" WHERE user_id=?" if uid else
                                          " WHERE user_id IS NULL")
    return [dict(r) for r in db.connect().execute(
        q + " ORDER BY seq", (uid,) if uid else ()).fetchall()]


def _reach(client, monkeypatch):
    uid = enroll(client)
    wire(monkeypatch)
    out = reachout.begin(uid, TWO, SITU)
    return uid, out


def _ring_back(client, caller="+1 (555) 111-0000", ref="CAin1"):
    return client.post("/reachout/line/inbound", json={
        "caller": caller, "called": "+15550009999", "house": "twilio",
        "vendor_ref": ref}, headers=AS_SIDECAR)


def _count():
    return db.connect().execute("SELECT COUNT(*) FROM reachout_calls").fetchone()[0]


# --- a contact calling back ----------------------------------------------------------

def test_a_contact_calling_back_reaches_the_conversation(client, monkeypatch):
    uid, out = _reach(client, monkeypatch)
    r = _ring_back(client)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["matched"] is True and body["reachout_id"] == out["reachout_id"]
    call = body["call"]
    assert call == {**call, "direction": "in", "status": "consented",
                    "name": "Rosa", "placed": 1, "provider": "twilio",
                    "provider_call_id": "CAin1"}
    assert call["answered_at"]
    line = body["line"]
    assert line["then"] == "speak_first"
    assert line["say"].startswith("This is JIM for Ada. Rosa, you are calling back "
                                  "about a fall with no answer")
    assert {"action": "contact.called_back", "ref": "Rosa"} in _actions(uid)
    # The line speaks first through the same turn every leg takes …
    s = client.post(f"/reachout/call/{call['id']}/say", json={"heard": ""},
                    headers=AS_SIDECAR).json()
    assert s["status"] == "talking" and s["line"]["then"] == "gather_speech"
    # … and the number's own status callback ends it, by the house's reference.
    st = client.post("/reachout/line/inbound/status", json={
        "house": "twilio", "vendor_ref": "CAin1", "event": "completed",
        "seconds": 30}, headers=AS_SIDECAR)
    assert st.status_code == 200, st.text
    assert st.json()["decided"] == "reached"
    rows = reachout.status(out["reachout_id"])["calls"]
    assert [r["direction"] for r in rows] == ["out", "in"]
    assert rows[1]["status"] == "reached" and rows[1]["ended"] == "completed"
    assert reachout.status(out["reachout_id"])["status"] == "reached"


def test_a_call_back_never_advances_the_cascade(client, monkeypatch):
    uid, out = _reach(client, monkeypatch)
    _ring_back(client)
    assert _count() == 2                           # Rosa out, Rosa in — Sam never rung
    assert reachout._call(out["call"]["id"])["status"] == "ringing"
    # Hung up before a word: that leg ends, and still nobody more is rung.
    st = client.post("/reachout/line/inbound/status", json={
        "house": "twilio", "vendor_ref": "CAin1", "event": "completed"},
        headers=AS_SIDECAR).json()
    assert st["decided"] == "unreached" and st["status"] == "ended"
    assert _count() == 2
    assert reachout._call(out["call"]["id"])["status"] == "ringing"


def test_a_cascade_reached_by_a_call_back_rings_nobody_more(client, monkeypatch):
    uid, out = _reach(client, monkeypatch)
    cid_in = _ring_back(client).json()["call"]["id"]
    client.post(f"/reachout/call/{cid_in}/say", json={"heard": ""}, headers=AS_SIDECAR)
    client.post("/reachout/line/inbound/status", json={
        "house": "twilio", "vendor_ref": "CAin1", "event": "completed"},
        headers=AS_SIDECAR)
    # The outbound leg to Rosa ends with no answer: the cascade is reached,
    # so Sam is not rung.
    nxt = reachout.event(out["call"]["id"], "no-answer")
    assert nxt["decided"] == "unreached" and nxt["status"] == "reached"
    assert _count() == 2


def test_the_newest_reach_out_for_that_number_wins(client, monkeypatch):
    a = enroll(client)
    wire(monkeypatch)
    reachout.begin(a, TWO, SITU)
    b = enroll(client)
    second = reachout.begin(b, TWO, {**SITU, "who": "Ben"})
    body = _ring_back(client).json()
    assert body["reachout_id"] == second["reachout_id"]
    assert "This is JIM for Ben." in body["line"]["say"]


# --- everyone else ---------------------------------------------------------------------

def test_an_unknown_caller_hears_one_sentence_and_nothing_is_kept(client, monkeypatch):
    uid, out = _reach(client, monkeypatch)
    r = _ring_back(client, caller="+1 555 999 0000", ref="CAx")
    assert r.status_code == 200
    body = r.json()
    assert body == {"matched": False, "call": None,
                    "line": telephony.line("hangup",
                                           telephony.phrases()["unknown_caller"])}
    assert _count() == 1
    assert _actions() == [{"action": "call.unknown_caller", "ref": "+15559990000"}]


def test_the_window_closes(client, monkeypatch):
    uid, out = _reach(client, monkeypatch)
    old = (datetime.now(timezone.utc)
           - timedelta(hours=reachout.INBOUND_WINDOW_HOURS + 1)).isoformat()
    db.connect().execute("UPDATE reachout_calls SET created_at=? WHERE id=?",
                         (old, out["call"]["id"]))
    db.connect().commit()
    assert _ring_back(client).json()["matched"] is False


def test_an_unknown_reference_is_refused_in_words(client, monkeypatch):
    _reach(client, monkeypatch)
    r = client.post("/reachout/line/inbound/status", json={
        "house": "twilio", "vendor_ref": "CAnope", "event": "completed"},
        headers=AS_SIDECAR)
    assert r.status_code == 404
    assert "no call answers to that reference" in r.text


def test_the_inbound_doors_take_the_secret(client, monkeypatch):
    _reach(client, monkeypatch)                    # sets the secret via wire()
    for path, body in (("/reachout/line/inbound", {"caller": "+15551110000"}),
                       ("/reachout/line/inbound/status", {"vendor_ref": "x",
                                                     "event": "completed"})):
        assert client.post(path, json=body, headers={"authorization": ""}).status_code == 401
        assert client.post(path, json=body).status_code == 403     # a person's token


# --- the posture: receiving, proven -------------------------------------------------------

def test_receive_ready_is_proven_not_assumed(client, monkeypatch):
    assert dialer.posture()["receive_ready"] is False              # unwired
    wire(monkeypatch, inbound={"voice_url": "https://jim-mini.com/voice/twilio/inbound?sig=x",
                               "status_url": "https://jim-mini.com/voice/twilio/inbound/status?sig=x",
                               "pointed": True})
    post = dialer.posture()
    assert post["receive_ready"] is True
    assert post["standing"]["inbound"]["voice_url"].endswith("/inbound?sig=x")
    telephony.forget_standing()
    wire(monkeypatch, inbound={"voice_url": "u", "status_url": "s", "pointed": False})
    assert dialer.posture()["receive_ready"] is False
    telephony.forget_standing()
    wire(monkeypatch, inbound={"voice_url": "u", "status_url": "s", "pointed": None})
    assert dialer.posture()["receive_ready"] is None               # the house cannot say
    telephony.forget_standing()
    wire(monkeypatch)                                              # an older sidecar
    assert dialer.posture()["receive_ready"] is None
    assert dialer.posture()["standing"]["inbound"] is None
