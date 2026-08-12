"""The plug-ins carry the readings (jim/app_connectors.py → jim/pipeline.py).

The collect note has said "context from X now informs guidance" since the
connectors landed, and nothing read what was collected. This round gives
the sentence behavior, three ways: a collected *reading* walks through the
same intake the watch uses; a collected *environment* item lands where the
offline stack's environment layer — which could never fire before — reads;
and collected *context* rides into both the offline stack and the online
model's system prompt.
"""

from jim.tests.conftest import enroll


def _connect(client, user):
    r = client.post(f"/apps/{user}", json={
        "provider": "apple", "app": "photos", "capabilities": []})
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _collect(client, cid, items):
    r = client.post(f"/apps/connector/{cid}/collect", json={"items": items})
    assert r.status_code == 201, r.text
    return r.json()


def _reply(client, user, message, area="mental_health"):
    return client.post(f"/coach/{user}", json={
        "area": area, "message": message}).json()


def _layer(body, name):
    return next(l for l in body["provenance"]["pipeline"]
                if l["layer"] == name)


def test_a_collected_reading_walks_the_watch_intake(client):
    """A heart rate from a connected health app is a heart rate: same
    vigil stand-down, same detection, same baseline as the wrist."""
    user = enroll(client)
    out = _collect(client, _connect(client, user), [
        {"content": "morning sync", "kind": "reading",
         "metric": "heart_rate", "value": 72}])
    assert out["ingested"] == 1 and out["readings"] == 1
    # The sample entered the record the watch writes into.
    baseline = client.get(f"/baseline/{user}").json()
    hr = next(m for m in baseline if m["metric"] == "heart_rate")
    assert (hr.get("samples") or 0) >= 1


def test_environment_walks_in_and_the_layer_finally_fires(client):
    """add.environment shipped as a layer nothing could ever feed —
    JIM has no environment writer of its own. The plug-ins are the
    writer."""
    user = enroll(client)
    before = _layer(_reply(client, user, "how are things looking"),
                    "add.environment")
    assert before["added"] == 0
    out = _collect(client, _connect(client, user), [
        {"content": "home office, 28°C, poor air quality reported nearby",
         "kind": "environment"}])
    assert out["environment"] == 1
    after = _layer(_reply(client, user, "how are things looking"),
                   "add.environment")
    assert after["added"] >= 1


def test_collected_context_finally_informs_guidance(client):
    """The note's exact claim, held: what a connected app collected shows
    up in the stack's collected layer, and in the words the online model
    would be handed."""
    from jim import coach
    user = enroll(client)
    _collect(client, _connect(client, user), [
        {"content": "calendar shows three late-night deadlines this week"}])
    body = _reply(client, user, "I feel stretched thin")
    assert _layer(body, "add.collected")["added"] >= 1
    assert _layer(body, "norm.collected")["kept"] >= 1
    assert "collected context: calendar shows three late-night" in (
        coach._context(user))


def test_the_stack_still_orders_its_layers(client):
    user = enroll(client)
    body = _reply(client, user, "I keep having panic attacks and my pulse races")
    layers = [l["layer"] for l in body["provenance"]["pipeline"]]
    assert layers.index("add.collected") > layers.index("norm.signals")
    assert layers.index("norm.collected") > layers.index("add.collected")
    assert layers.index("add.learned") > layers.index("norm.collected")
