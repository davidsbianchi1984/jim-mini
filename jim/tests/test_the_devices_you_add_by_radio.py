"""The devices you add by radio: speakers, phones, and the honest bucket.

The console's device picker offered "phone" for a while before the
server accepted it — a choice on screen that the handler refused with a
422 nobody saw coming. The kind set now matches what people actually
pair over Bluetooth: the clause-16 embodiment classes, plus speaker,
phone, and other. The Add-Bluetooth button registers the device under
its own advertised name with its transport recorded, so what is
listening (or speaking) is always something registered on purpose.
"""

from __future__ import annotations

from .test_watch import _auth, _enroll


def _pro(client):
    """Devices are a pro capability; the picker's kinds are tested on an
    account entitled to them."""
    u = _enroll(client)
    r = client.post(f"/memberships/{u['id']}", json={"plan": "pro"},
                    headers=_auth(u))
    assert r.status_code == 200, r.text
    return u


def test_every_kind_the_picker_offers_is_accepted(client):
    u = _pro(client)
    for kind in ("wearable", "speaker", "stationary", "phone", "glasses",
                 "headset", "spatial", "other", "autonomous"):
        r = client.post(f"/devices/{u['id']}", headers=_auth(u), json={
            "name": f"my {kind}", "kind": kind, "transport": "bluetooth"})
        assert r.status_code == 201, (kind, r.text)
        assert r.json()["kind"] == kind
    rows = client.get(f"/devices/{u['id']}", headers=_auth(u)).json()
    assert {d["kind"] for d in rows} >= {"speaker", "phone", "glasses",
                                         "headset", "spatial", "other"}
    # The transport travels with the row — the card can say how it talks.
    assert all(d["transport"] == "bluetooth" for d in rows)


def test_the_handshake_is_a_recorded_fact_not_an_assumption(client):
    """A device the browser's chooser actually paired is a different fact
    from a name typed into the manual row — the row says which."""
    u = _pro(client)
    shook = client.post(f"/devices/{u['id']}", headers=_auth(u), json={
        "name": "kitchen speaker", "kind": "speaker",
        "transport": "bluetooth", "paired": True}).json()
    typed = client.post(f"/devices/{u['id']}", headers=_auth(u), json={
        "name": "garage speaker", "kind": "speaker",
        "transport": "bluetooth"}).json()
    assert shook["paired"] is True
    assert typed["paired"] is False
    rows = {d["name"]: d for d in
            client.get(f"/devices/{u['id']}", headers=_auth(u)).json()}
    assert rows["kitchen speaker"]["paired"] is True
    assert rows["garage speaker"]["paired"] is False


def test_a_kind_the_picker_does_not_offer_is_still_refused(client):
    u = _pro(client)
    r = client.post(f"/devices/{u['id']}", headers=_auth(u), json={
        "name": "mystery box", "kind": "teleporter"})
    assert r.status_code == 422
