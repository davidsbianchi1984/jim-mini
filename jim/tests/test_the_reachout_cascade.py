"""The reach-out cascade: JIM calling emergency contacts, one after another.

The owner's ladder, driven end to end against the held seam (no telephony is
wired, so each call comes back *prepared*; the logic is exercised by calling
the handlers a provider's webhooks would call):

* a call opens with the keypad gate, 1 to hear it / 2 to never be called;
* on 1, JIM holds a real, grounded conversation and the exchange is reached;
* on 2, the number is opted out and never rung again, and the cascade moves on;
* no answer moves it on too;
* when the contacts are spent and the situation is life-threatening, the last
  rung is the 911 dialer — assembled, routed, and held shut.

Every step leaves a catalogued audit trace, so the chain a reviewer reads is
the chain of what actually happened.
"""

import pytest

from jim import db, dialer, reachout


@pytest.fixture()
def a_db(tmp_path, monkeypatch):
    monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
    monkeypatch.setenv("JIM_LLM", "stub")
    db.reset()
    # A user row for the FK.
    db.connect().execute(
        "INSERT INTO users (id, display_name, birthdate, created_at)"
        " VALUES ('usr_1','Ada','1950-01-01',?)", (db.utcnow(),))
    db.connect().commit()
    yield
    db.reset()


SItu = {"who": "Ada", "about": "a fall with no answer", "what_to_do": "check on her"}
TWO = [{"name": "Rosa", "channel": "+15551110000"},
       {"name": "Sam", "channel": "+15552220000"}]


def _actions(user_id="usr_1"):
    return [r["action"] for r in db.connect().execute(
        "SELECT action FROM audit WHERE user_id=? ORDER BY seq",
        (user_id,)).fetchall()]


def test_a_call_opens_prepared_not_placed(a_db):
    out = reachout.begin("usr_1", TWO, SItu)
    assert out["status"] == "calling"
    # The seam holds it: composed and routed, never placed.
    assert out["dialer"]["placed"] is False
    assert out["dialer"]["prepared"] is True
    assert "contact.called" in _actions()


def test_press_one_opens_a_grounded_conversation_and_reaches(a_db):
    out = reachout.begin("usr_1", TWO, SItu)
    call_id = out["call"]["id"]
    con = reachout.consent(call_id, "1")
    assert con["status"] == "consented"
    turn = reachout.say(call_id, "What happened to her?")
    assert turn["said"], "JIM said nothing back"
    done = reachout.reached(call_id)
    assert done["status"] == "reached"
    assert "contact.reached" in _actions()
    assert reachout.status(out["reachout_id"])["status"] == "reached"


def test_press_two_opts_out_and_cascades_to_the_next(a_db):
    out = reachout.begin("usr_1", TWO, SItu)
    first = out["call"]["id"]
    nxt = reachout.consent(first, "2")
    # Rosa opted out; the cascade rang Sam.
    assert nxt["status"] == "calling"
    assert nxt["call"]["name"] == "Sam"
    assert reachout.opted_out("usr_1", "+15551110000") is True
    assert "contact.declined" in _actions()


def test_no_answer_moves_on_then_exhausts_into_the_held_911_rung(a_db):
    out = reachout.begin("usr_1", TWO, SItu, life_threatening=True)
    first = out["call"]["id"]
    nxt = reachout.unreached(first)          # Rosa didn't answer -> Sam
    assert nxt["call"]["name"] == "Sam"
    spent = reachout.unreached(nxt["call"]["id"])   # Sam didn't answer -> spent
    assert spent["status"] == "exhausted"
    assert spent["life_threatening"] is True
    # The last rung is the dialer, assembled and routed but HELD.
    ems = spent["emergency_services"]
    assert ems["held"] is True and ems["placed"] is False
    acts = _actions()
    assert acts.count("contact.unreached") == 2
    assert "reachout.exhausted" in acts
    assert "dial.held" in acts


def test_not_life_threatening_exhausts_without_touching_the_dialer(a_db):
    out = reachout.begin("usr_1", TWO, SItu, life_threatening=False)
    spent = reachout.unreached(
        reachout.unreached(out["call"]["id"])["call"]["id"])
    assert spent["status"] == "exhausted"
    assert spent["emergency_services"] is None
    assert "dial.held" not in _actions()


def test_an_opted_out_only_list_exhausts_immediately(a_db):
    db.connect().execute(
        "INSERT INTO do_not_call (user_id, channel, at)"
        " VALUES ('usr_1','+15551110000',?)", (db.utcnow(),))
    db.connect().commit()
    out = reachout.begin("usr_1", [TWO[0]], SItu, life_threatening=True)
    assert out["status"] == "exhausted"
    assert out["emergency_services"]["held"] is True


# --- the HTTP doors, and who may turn them ---------------------------------

def test_the_begin_door_is_owner_only_and_the_call_ids_carry_the_rest(client):
    from jim.tests.conftest import enroll
    uid = enroll(client)   # the client is now authed as this user
    body = {"contacts": [{"name": "Rosa", "channel": "+15551110000"}],
            "situation": {"who": "Ada", "about": "a fall"},
            "life_threatening": True}
    # A token that is not this user's cannot open a reach-out for them.
    assert client.post(f"/reachout/{uid}", json=body,
                       headers={"authorization": "Bearer not-the-owner"}
                       ).status_code in (401, 403)
    # The owner can, and the first call comes back prepared, never placed.
    r = client.post(f"/reachout/{uid}", json=body)
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["dialer"]["placed"] is False
    call_id = out["call"]["id"]
    # The keypad + conversation run over the call-id handlers.
    assert client.post(f"/reachout/call/{call_id}/consent",
                       json={"digit": "1"}).status_code == 200
    said = client.post(f"/reachout/call/{call_id}/say",
                       json={"heard": "what's going on?"})
    assert said.status_code == 200 and said.json()["said"]
    assert client.post(f"/reachout/call/{call_id}/reached").status_code == 200


def test_the_dialer_posture_door_says_held(client):
    p = client.get("/dialer/posture")
    assert p.status_code == 200
    assert p.json()["send_enabled"] is False
