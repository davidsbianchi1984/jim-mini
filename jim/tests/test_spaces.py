"""A room microphone, and what it costs to have one honestly.

`jim/mic.py` refuses anything room-facing as channel 2, and is right to: one
person cannot lend the voices of everyone around them. This is the *other*
arrangement — an ambient microphone with its own consent model rather than an
exemption from having one.

The load-bearing test is `test_anybody_can_silence_it_without_an_account`.
The rest of the design leans on it.
"""

from jim import db, spaces
from jim.tests.conftest import enroll


def _console(client, uid, name="kitchen_console", kind="stationary"):
    r = client.post(f"/devices/{uid}", json={"name": name, "kind": kind})
    assert r.status_code in (200, 201), r.text
    return r.json()


def _space(client, **over):
    uid = enroll(client)
    _console(client, uid)
    body = {"device_name": "kitchen_console", "space": "kitchen",
            "disclosure": ["indicator_light", "chime_on_wake"],
            "activation": "wake_word"}
    body.update(over)
    r = client.post(f"/users/{uid}/spaces", json=body)
    assert r.status_code == 201, r.text
    return uid, r.json()


# -- setting one up ----------------------------------------------------------

def test_a_stationary_device_can_listen_in_a_named_space(client):
    uid, space = _space(client)
    assert space["space"] == "kitchen"
    assert space["activation"] == "wake_word"
    assert "anyone in this room can silence it" in space["note"]


def test_a_worn_device_is_not_a_room_microphone(client):
    """A watch is channel 2 — a different arrangement with a different
    consent story. The two must not be reachable through each other."""
    uid = enroll(client)
    client.post(f"/devices/{uid}", json={"name": "smart_watch",
                                         "kind": "wearable"})
    r = client.post(f"/users/{uid}/spaces", json={
        "device_name": "smart_watch", "space": "kitchen",
        "disclosure": ["indicator_light"], "activation": "wake_word"})
    assert r.status_code == 422
    assert "channel 2" in r.json()["detail"]


def test_a_disclosure_in_the_room_is_required(client):
    """A setting in the owner's app tells the owner, who already knew."""
    uid = enroll(client)
    _console(client, uid)
    r = client.post(f"/users/{uid}/spaces", json={
        "device_name": "kitchen_console", "space": "kitchen",
        "disclosure": [], "activation": "wake_word"})
    assert r.status_code == 422
    assert "you already knew" in r.json()["detail"]


def test_continuous_listening_is_not_offered(client):
    """A microphone that never stops is a different object from one that
    wakes, and no notice makes it the first one."""
    uid = enroll(client)
    _console(client, uid)
    r = client.post(f"/users/{uid}/spaces", json={
        "device_name": "kitchen_console", "space": "kitchen",
        "disclosure": ["indicator_light"], "activation": "continuous"})
    assert r.status_code == 422
    assert "continuous" not in spaces.ACTIVATIONS


def test_the_household_is_recorded(client):
    """One person's purchase is not everyone's decision about their home."""
    uid, space = _space(client, household=["Ruth", "Ade"])
    assert space["household"] == ["Ruth", "Ade"]


# -- the hold: the affordance the rest leans on ------------------------------

def test_anybody_can_silence_it_without_an_account(client):
    """The load-bearing one. A guest, a cleaner, a visiting nurse, a child —
    whoever can reach the device mutes it, with no token, no enrolment, and
    without asking whoever bought it."""
    uid, space = _space(client)
    client.headers.pop("authorization", None)   # a true stranger

    out = client.post(f"/spaces/{space['id']}/hold",
                      json={"minutes": 30, "reason": "I did not agree to this"})
    assert out.status_code == 201
    assert out.json()["held"] is True
    assert "Nobody was asked to approve it" in out.json()["note"]

    state = client.get(f"/spaces/{space['id']}").json()
    assert state["listening"] is False
    assert "silenced until" in state["hears"]


def test_a_guest_need_not_say_who_they_are(client):
    """Nobody should have to identify themselves to stop being recorded."""
    uid, space = _space(client)
    client.headers.pop("authorization", None)
    assert client.post(f"/spaces/{space['id']}/hold", json={}).json()["held"]
    assert spaces.holds_for(space["id"])[0]["placed_by"] is None


def test_the_state_is_readable_without_a_token(client):
    """"Is this thing listening to me" is a question the people least likely
    to have an account most need answered."""
    uid, space = _space(client)
    client.headers.pop("authorization", None)
    out = client.get(f"/spaces/{space['id']}")
    assert out.status_code == 200
    assert out.json()["anyone_can_silence"] is True


def test_a_hold_expires(client):
    uid, space = _space(client)
    spaces.hold(space["id"], minutes=30)
    assert spaces.state(space["id"])["listening"] is False

    conn = db.connect()
    conn.execute("UPDATE ambient_holds SET until='2000-01-01T00:00:00Z'"
                 " WHERE space_id=?", (space["id"],))
    conn.commit()
    assert spaces.state(space["id"])["listening"] is True


def test_a_hold_can_be_lifted_early_by_anyone(client):
    """Whoever placed it may not be the one still in the room."""
    uid, space = _space(client)
    held = spaces.hold(space["id"], minutes=60, placed_by="a visitor")
    client.headers.pop("authorization", None)
    assert client.post(
        f"/spaces/{space['id']}/hold/{held['id']}/lift").status_code == 200
    assert spaces.state(space["id"])["listening"] is True


def test_a_hold_is_capped_and_never_zero(client):
    uid, space = _space(client)
    assert spaces.hold(space["id"], minutes=0)["minutes"] == 1
    assert spaces.hold(space["id"], minutes=99999)["minutes"] == \
        spaces.MAX_HOLD_MINUTES


def test_holds_are_kept_for_the_owner_to_notice(client):
    """A pattern of holds is the room telling its owner something."""
    uid, space = _space(client)
    spaces.hold(space["id"], reason="visitors")
    spaces.hold(space["id"], reason="visitors again")
    rows = client.get(f"/users/{uid}/spaces/{space['id']}/holds").json()
    assert [r["reason"] for r in rows] == ["visitors again", "visitors"]


# -- what the agent may take -------------------------------------------------

def test_a_held_space_yields_nothing_to_the_agent(client):
    uid, space = _space(client)
    assert spaces.can_listen(uid, "kitchen") is True
    spaces.hold(space["id"])
    assert spaces.can_listen(uid, "kitchen") is False


def test_an_unenrolled_space_yields_nothing(client):
    uid, space = _space(client)
    assert spaces.can_listen(uid, "bedroom") is False


def test_removing_the_space_ends_it(client):
    uid, space = _space(client)
    client.delete(f"/users/{uid}/spaces/{space['id']}")
    assert spaces.can_listen(uid, "kitchen") is False


# -- the owner's to set up, not to silence -----------------------------------

def test_another_user_cannot_enrol_a_space_on_your_account(client):
    uid, space = _space(client)
    enroll(client, display_name="Mal")
    r = client.post(f"/users/{uid}/spaces", json={
        "device_name": "kitchen_console", "space": "hallway",
        "disclosure": ["indicator_light"], "activation": "wake_word"})
    assert r.status_code == 403
    assert client.get(f"/users/{uid}/spaces").status_code == 403


def test_silencing_does_not_disable_escalation(client):
    """The hold is only safe because nothing on the emergency path runs on
    room audio. If that stopped being true, the ladder would be the thing
    that had gone wrong."""
    uid, space = _space(client)
    spaces.hold(space["id"])
    body = client.post(f"/monitor/{uid}", json={
        "heart_rate": 190, "blood_oxygen": 84,
        "note": "I can't breathe"}).json()
    # The ladder runs on worn sensors, not on the room. A silenced kitchen
    # does not change what a collapse does.
    assert body["escalation"] is not None
