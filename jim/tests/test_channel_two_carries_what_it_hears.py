"""Channel 2 carries what it hears.

`jim/mic.py` has always said, honestly, that capture happens on the
device and nothing in that module touches a sample. That was a true
description of the division and — until this round — of a pipe that did
not exist. The second microphone could be attached, handed over, gained,
capped and audited, and there was no door for the wearable to hand
anything back.

    asked     may the agent listen on this device
    mattered  can the device get what it hears to the agent

A field report named it: the switches and the channel are permission,
with nothing honouring them. So the door is here, and it is the
narrowest one that works — every refusal below is a rule that already
existed in that module and had nothing enforcing it.
"""

from __future__ import annotations

import base64

from jim.tests.conftest import enroll

# Not silence: the transcriber never runs in these tests (the stub voice
# provider answers), but an empty body is its own refusal below, so the
# bytes have to be real bytes.
SOUND = base64.b64encode(b"\x1aE\xdf\xa3channel-two-audio").decode()


def _watch(client, uid, name="smart_watch"):
    r = client.post(f"/devices/{uid}", json={
        "name": name, "kind": "wearable", "transport": "bluetooth"})
    assert r.status_code in (200, 201), r.text


def _attached(client, name="smart_watch", mic_type="watch"):
    uid = enroll(client)
    _watch(client, uid, name=name)
    assert client.put(f"/users/{uid}/mic", json={
        "device_name": name, "mic_type": mic_type}).status_code == 200
    return uid


def _handed(client, uid):
    r = client.post(f"/users/{uid}/mic/handover", json={
        "reason": "voice_call", "route": "earpiece"})
    assert r.status_code in (200, 201), r.text


def _heard(client, uid, **body):
    """Words by default: a watch that recognised the speech itself is the
    preferred delivery, and it needs no transcription key to prove."""
    return client.post(f"/users/{uid}/mic/heard",
                       json={"words": "I think I need to sit down", **body})


# -- the four refusals -------------------------------------------------------

def test_a_channel_nobody_lent_cannot_have_heard_anything(client):
    uid = enroll(client)
    r = _heard(client, uid)
    assert r.status_code == 403
    assert "nothing is attached" in r.text


def test_audio_outside_a_handover_is_a_microphone_that_opened_itself(client):
    """`handover` is the moment the agent is allowed to listen, with a
    reason and a route on the record. Sound arriving outside one has no
    such moment behind it."""
    uid = _attached(client)
    r = _heard(client, uid)
    assert r.status_code == 403
    assert "not listening on channel 2" in r.text


def test_another_device_cannot_deliver_under_the_channels_name(client):
    """One channel, one wearable. Otherwise the audit line — which
    microphone heard this — becomes a guess."""
    uid = _attached(client)
    _handed(client, uid)
    r = _heard(client, uid, device_name="lapel_mic")
    assert r.status_code == 403
    assert "one device" in r.text.lower() or "not to" in r.text


def test_an_empty_delivery_is_not_something_it_heard(client):
    uid = _attached(client)
    _handed(client, uid)
    r = client.post(f"/users/{uid}/mic/heard", json={"words": "   "})
    assert r.status_code in (403, 422)


# -- and the pipe itself -----------------------------------------------------

def test_the_lent_device_can_hand_in_what_it_heard(client):
    uid = _attached(client)
    _handed(client, uid)
    r = _heard(client, uid, device_name="smart_watch")
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["device"] == "smart_watch"
    assert body["reason"] == "voice_call"
    assert "heard" in body


def test_attached_is_not_carrying(client):
    """The monitor roster's lesson, applied here: a screen must be able to
    tell a channel that has been lent from one that has actually carried
    something, instead of reading "attached" as "listening"."""
    uid = _attached(client)
    assert client.get(f"/users/{uid}/mic").json()["standing"] == "silent"
    _handed(client, uid)
    assert client.get(f"/users/{uid}/mic").json()["standing"] == "silent", (
        "handing the channel over is still not the same as it having "
        "carried anything")
    _heard(client, uid, device_name="smart_watch")
    state = client.get(f"/users/{uid}/mic").json()
    assert state["standing"] == "carrying"
    assert state["last_heard"], "the channel cannot say when it last carried"


def test_audio_is_the_fallback_for_a_device_that_cannot_listen(client):
    """A watch with its own recogniser sends words; one without sends the
    sound. On a deployment with no ears the audio path refuses in words —
    the same honest 503 every other spoken door gives — rather than
    pretending something was heard."""
    uid = _attached(client)
    _handed(client, uid)
    r = client.post(f"/users/{uid}/mic/heard", json={
        "audio_base64": SOUND, "device_name": "smart_watch"})
    assert r.status_code in (201, 503), r.text
    if r.status_code == 503:
        assert "listening service" in r.text


def test_nothing_attached_reads_as_unattached(client):
    uid = enroll(client)
    assert client.get(f"/users/{uid}/mic").json()["standing"] == "unattached"


def test_the_delivery_stays_this_persons(client):
    """A stranger holding a user id cannot hand audio in against it."""
    uid = _attached(client)
    _handed(client, uid)
    other = enroll(client)          # becomes the client's default token
    assert other != uid
    r = _heard(client, uid, device_name="smart_watch")
    assert r.status_code in (403, 404)
