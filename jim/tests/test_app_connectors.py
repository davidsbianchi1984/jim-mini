"""Connected-app connectors: a user connects a catalog app and the Guardian's
agents collect context, act, or produce through it."""

from jim.tests.conftest import enroll


def _connect(client, uid, **body):
    r = client.post(f"/apps/{uid}", json=body)
    assert r.status_code == 201, r.text
    return r.json()


def test_connect_and_collect(client):
    uid = enroll(client)
    conn = _connect(client, uid, provider="apple", app="calendar")
    assert "collect" in conn["directions"]
    # Connecting a collect-capable app consents its source.
    sources = {s["source"]: s["consented"] for s in client.get(f"/sources/{uid}").json()}
    assert sources.get("app:apple:calendar") is True

    r = client.post(f"/apps/connector/{conn['id']}/collect",
                    json={"items": [{"content": "Dentist Tuesday 3pm"}]})
    assert r.status_code == 201, r.text
    assert r.json()["ingested"] == 1
    assert client.get(f"/apps/{uid}").json()[0]["collected"] == 1


def test_invoke_and_grants(client):
    uid = enroll(client)
    conn = _connect(client, uid, provider="canva", app="magic_studio",
                    capabilities=["magic-media"])
    r = client.post(f"/apps/connector/{conn['id']}/invoke",
                    json={"capability": "magic-media", "input": "a calm sunset"})
    assert r.status_code == 201, r.text
    assert r.json()["status"] == "performed"
    # Not-granted capability is refused.
    assert client.post(f"/apps/connector/{conn['id']}/invoke",
                       json={"capability": "magic-design"}).status_code == 422


def test_unknown_app_refused(client):
    uid = enroll(client)
    assert client.post(f"/apps/{uid}",
                       json={"provider": "apple", "app": "toaster"}).status_code == 404


def test_produce_only_app_cannot_collect(client):
    uid = enroll(client)
    conn = _connect(client, uid, provider="microsoft", app="paint")
    assert client.post(f"/apps/connector/{conn['id']}/collect",
                       json={"items": [{"content": "x"}]}).status_code == 409


def test_revoke_stops_use(client):
    uid = enroll(client)
    conn = _connect(client, uid, provider="google", app="gmail")
    assert client.delete(f"/apps/connector/{conn['id']}").json()["status"] == "revoked"
    assert client.post(f"/apps/connector/{conn['id']}/invoke",
                       json={"capability": "summaries"}).status_code == 409
