"""The room warns before it wounds (jim/hazards.py).

P001 clause 2's extension: environmental hazards and ergonomic risk factors,
identified before they manifest as injuries. Collected environment items
were landing as context the coach could read; now they are also read for
the room's dangers on arrival — deterministic, offline, referenced — and
each hazard lands as an insight and rides back to the caller with advice.
"""

from jim.tests.conftest import enroll


def _connect(client, user):
    r = client.post(f"/apps/{user}", json={
        "provider": "google", "app": "photos", "capabilities": []})
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _collect(client, cid, items):
    r = client.post(f"/apps/connector/{cid}/collect", json={"items": items})
    assert r.status_code == 201, r.text
    return r.json()


def test_a_dangerous_room_is_named_with_referenced_advice(client):
    user = enroll(client)
    out = _collect(client, _connect(client, user), [
        {"kind": "environment",
         "content": "Kitchen smells of gas near the stove; wet floor by "
                    "the sink."}])
    hazards = out["room_hazards"]
    names = [h["hazard"] for h in hazards]
    assert names == ["gas_leak", "fall_risk"]   # worst first
    gas = hazards[0]
    assert gas["severity"] == "critical"
    assert "leave immediately" in gas["advice"].lower()
    assert gas["reference"]                     # advice carries its source

    # The hazard landed as an insight the Life view shows.
    insights = client.get(f"/insights/{user}").json()
    hazard_notes = [i for i in insights if i["kind"] == "hazard"]
    assert any("gas leak" in i["message"] for i in hazard_notes)


def test_a_benign_room_raises_nothing(client):
    user = enroll(client)
    out = _collect(client, _connect(client, user), [
        {"kind": "environment",
         "content": "Sunny living room, plants watered, quiet street."}])
    assert out["room_hazards"] == []
    insights = client.get(f"/insights/{user}").json()
    assert not any(i["kind"] == "hazard" for i in insights)


def test_only_environment_items_are_scanned(client):
    """A chat message mentioning smoke is a topic, not a room. The scan
    runs on what describes the surroundings, nothing else."""
    user = enroll(client)
    out = _collect(client, _connect(client, user), [
        {"kind": "context",
         "content": "read an article about wildfire smoke"}])
    assert out["room_hazards"] == []
