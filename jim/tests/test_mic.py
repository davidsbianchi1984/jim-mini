"""Channel 2: a second microphone, for the agent.

A phone has one microphone and one foreground claim on it. On a call the
Guardian is deaf — exactly when somebody might want to ask it something.
Most people already carry a second microphone: a watch, earbuds, a lapel or
clip-on mic, glasses.

The assertions worth reading are the refusals. The speakerphone one most of
all — on speaker the second microphone hears the *other party*, who is not a
user of this product, was never asked, and cannot revoke anything — and the
collision one, which only exists because anything worn now qualifies: earbuds
carrying the call are the *occupied* microphone, not a spare.
"""

from jim import db
from jim.tests.conftest import enroll


def _watch(client, uid, name="smart_watch", kind="wearable"):
    r = client.post(f"/devices/{uid}", json={
        "name": name, "kind": kind, "transport": "bluetooth"})
    assert r.status_code in (200, 201), r.text
    return r.json()


def _attached(client, name="smart_watch", mic_type="watch"):
    uid = enroll(client)
    _watch(client, uid, name=name)
    assert client.put(f"/users/{uid}/mic", json={
        "device_name": name, "mic_type": mic_type}).status_code == 200
    return uid


# -- attaching ---------------------------------------------------------------

def test_attaching_is_not_listening(client):
    uid = _attached(client)
    state = client.get(f"/users/{uid}/mic").json()
    assert state["attached"] == "smart_watch"
    assert state["listening"] is False
    assert "nothing" in state["hears"]


def test_a_room_facing_microphone_cannot_be_channel_2(client):
    """The axis is who the microphone is pointed at. A conference puck hears
    whoever is present, and they never agreed."""
    uid = enroll(client)
    _watch(client, uid, name="desk_puck")
    r = client.put(f"/users/{uid}/mic", json={"device_name": "desk_puck",
                                              "mic_type": "conference"})
    assert r.status_code == 422
    assert "pointed at a room" in r.json()["detail"]
    assert "without being asked" in r.json()["detail"]


def test_a_stationary_device_is_refused_whatever_mic_it_claims(client):
    """Something bolted to a room hears the room, whatever is inside it."""
    uid = enroll(client)
    _watch(client, uid, name="kitchen_console", kind="stationary")
    r = client.put(f"/users/{uid}/mic", json={"device_name": "kitchen_console",
                                              "mic_type": "lapel"})
    assert r.status_code == 422
    assert "bolted to a room" in r.json()["detail"]


def test_every_worn_microphone_qualifies(client):
    """Earbuds, lapel, clip-on, glasses — a watch was never special, it was
    just the one that happened to be implemented first."""
    for name, mic_type in (("earbuds", "earbuds"), ("lapel_mic", "lapel"),
                           ("clip_mic", "clip_on"), ("specs", "glasses"),
                           ("bt_headset", "headset")):
        uid = enroll(client)
        _watch(client, uid, name=name)
        r = client.put(f"/users/{uid}/mic", json={"device_name": name,
                                                  "mic_type": mic_type})
        assert r.status_code == 200, f"{mic_type}: {r.text}"
        assert r.json()["channel"] == 2


def test_the_type_list_is_published(client):
    """So a client offers the right list rather than guessing, and the reason
    a room microphone is excluded is discoverable before it is a refusal."""
    out = client.get("/mic/types").json()
    assert "earbuds" in out["personal"] and "lapel" in out["personal"]
    assert "conference" in out["ambient"] and "speakerphone" in out["ambient"]
    assert "pointed at a room" in out["rule"]


def test_earbuds_carrying_the_call_cannot_also_be_channel_2(client):
    """The collision broadening this exposed: one microphone cannot be both
    the call and the agent's channel. A watch never had this problem."""
    uid = _attached(client, name="earbuds", mic_type="earbuds")
    r = client.post(f"/users/{uid}/mic/handover", json={
        "reason": "voice_call", "route": "bluetooth_headset",
        "primary_device": "earbuds"})
    assert r.status_code == 403
    assert "cannot be both channels" in r.json()["detail"]
    assert client.get(f"/users/{uid}/mic").json()["listening"] is False


def test_a_different_device_on_the_call_is_fine(client):
    uid = _attached(client, name="lapel_mic", mic_type="lapel")
    r = client.post(f"/users/{uid}/mic/handover", json={
        "reason": "voice_call", "route": "bluetooth_headset",
        "primary_device": "earbuds"})
    assert r.status_code == 201
    assert r.json()["mic_type"] == "lapel"


def test_an_unknown_device_cannot_be_lent(client):
    uid = enroll(client)
    r = client.put(f"/users/{uid}/mic", json={"device_name": "nobodys_watch",
                                              "mic_type": "watch"})
    assert r.status_code == 422
    assert "no device called" in r.json()["detail"]


def test_handover_without_anything_attached_is_refused(client):
    uid = enroll(client)
    r = client.post(f"/users/{uid}/mic/handover",
                    json={"reason": "voice_call", "route": "earpiece"})
    assert r.status_code == 403
    assert "nothing attached" in r.json()["detail"]


# -- the refusals that carry the design --------------------------------------

def test_speakerphone_is_refused(client):
    """The load-bearing one. On speaker the watch hears whoever is on the
    other end of the call, and they are not a user here."""
    uid = _attached(client)
    r = client.post(f"/users/{uid}/mic/handover",
                    json={"reason": "voice_call", "route": "speaker"})
    assert r.status_code == 403
    detail = r.json()["detail"]
    assert "not a user here" in detail
    assert "never asked" in detail
    # And nothing was recorded as listening.
    assert client.get(f"/users/{uid}/mic").json()["listening"] is False


def test_others_in_earshot_is_refused(client):
    uid = _attached(client)
    r = client.post(f"/users/{uid}/mic/handover", json={
        "reason": "voice_call", "route": "earpiece", "others_present": True})
    assert r.status_code == 403
    assert "did not agree" in r.json()["detail"]


def test_a_reason_is_required_and_checked(client):
    """What is occupying the primary is what justifies lending a second one,
    so it is recorded rather than inferred."""
    uid = _attached(client)
    r = client.post(f"/users/{uid}/mic/handover",
                    json={"reason": "just_because", "route": "earpiece"})
    assert r.status_code == 422        # rejected by the schema


# -- lending it --------------------------------------------------------------

def test_handover_on_an_earpiece_works_and_is_visible(client):
    uid = _attached(client)
    out = client.post(f"/users/{uid}/mic/handover",
                      json={"reason": "voice_call", "route": "earpiece"}).json()
    assert out["listening"] is True
    assert "hears you, not your call" in out["note"]

    state = client.get(f"/users/{uid}/mic").json()
    assert state["listening"] is True
    assert state["device"] == "smart_watch"
    assert state["reason"] == "voice_call"
    assert "you, on your smart watch" == state["hears"]


def test_handing_over_twice_does_not_start_a_second_session(client):
    uid = _attached(client)
    first = client.post(f"/users/{uid}/mic/handover",
                        json={"reason": "voice_call", "route": "earpiece"}).json()
    again = client.post(f"/users/{uid}/mic/handover",
                        json={"reason": "voice_call", "route": "headset"}).json()
    assert again["already_live"] is True
    assert again["id"] == first["id"]
    assert len(client.get(f"/users/{uid}/mic/history").json()) == 1


def test_releasing_gives_it_back(client):
    uid = _attached(client)
    client.post(f"/users/{uid}/mic/handover",
                json={"reason": "voice_call", "route": "earpiece"})
    out = client.post(f"/users/{uid}/mic/release").json()
    assert out["listening"] is False
    assert client.get(f"/users/{uid}/mic").json()["listening"] is False


def test_releasing_when_not_listening_is_not_an_error(client):
    uid = _attached(client)
    out = client.post(f"/users/{uid}/mic/release").json()
    assert out["listening"] is False
    assert "was not listening" in out["note"]


def test_detaching_ends_a_live_handover(client):
    """Removing the watch must not leave a permission behind it."""
    uid = _attached(client)
    client.post(f"/users/{uid}/mic/handover",
                json={"reason": "voice_call", "route": "earpiece"})
    out = client.request("DELETE", f"/users/{uid}/mic").json()
    assert out["attached"] is False
    assert out["ended_session"] is True

    state = client.get(f"/users/{uid}/mic").json()
    assert state["attached"] is None and state["listening"] is False


# -- the record --------------------------------------------------------------

def test_every_handover_is_recorded_with_why_and_how(client):
    """A listening permission that leaves no trace is one nobody can audit,
    and this is the permission people most want to check up on."""
    uid = _attached(client)
    client.post(f"/users/{uid}/mic/handover",
                json={"reason": "voice_call", "route": "earpiece"})
    client.post(f"/users/{uid}/mic/release")
    client.post(f"/users/{uid}/mic/handover",
                json={"reason": "dictation", "route": "headset"})

    rows = client.get(f"/users/{uid}/mic/history").json()
    assert len(rows) == 2
    assert rows[0]["reason"] == "dictation" and rows[0]["live"] is True
    assert rows[1]["reason"] == "voice_call" and rows[1]["live"] is False
    assert rows[1]["ended_at"] and rows[1]["ended_because"] == "released"


def test_a_refused_handover_leaves_no_record_of_listening(client):
    """A refusal is not a session. The history must not imply the agent heard
    something it never did."""
    uid = _attached(client)
    client.post(f"/users/{uid}/mic/handover",
                json={"reason": "voice_call", "route": "speaker"})
    assert client.get(f"/users/{uid}/mic/history").json() == []


# -- it is per user ----------------------------------------------------------

def test_another_user_cannot_lend_or_read_your_microphone(client):
    uid = _attached(client)
    enroll(client, display_name="Mal")        # client now holds Mal's token
    assert client.get(f"/users/{uid}/mic").status_code == 403
    assert client.post(f"/users/{uid}/mic/handover", json={
        "reason": "voice_call", "route": "earpiece"}).status_code == 403
    assert client.get(f"/users/{uid}/mic/history").status_code == 403
