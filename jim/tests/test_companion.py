"""Ambient companion check-in: the coach reaches out first."""

from jim.tests.conftest import enroll


def test_companion_reaches_out_first(client):
    user = enroll(client)
    client.post(f"/checkin/{user}", json={"mood": 2, "energy": 2})
    r = client.post(f"/companion/{user}")
    assert r.status_code == 200
    body = r.json()
    assert body["delivered"] is True and body["unprompted"] is True
    assert body["content"]
    # The outreach is part of the coach thread, like any other message.
    history = client.get(f"/coach/{user}",
                         params={"area": "mental_health"}).json()
    assert history[-1]["role"] == "coach"


def test_companion_respects_personality(client):
    user = enroll(client)
    client.put(f"/personality/{user}", json={"tone": "direct and brief"})
    body = client.post(f"/companion/{user}").json()
    assert "(tone: direct and brief)" in body["content"]
