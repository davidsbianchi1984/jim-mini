"""Social-platform connections: collect posts into guidance context, or
publish an update reachable by a QR beacon."""

from jim.tests.conftest import enroll


def _connect(client, uid, **body):
    r = client.post(f"/social/{uid}", json=body)
    assert r.status_code == 201, r.text
    return r.json()


def test_collect_consents_source_and_ingests(client):
    uid = enroll(client)
    conn = _connect(client, uid, platform="instagram", direction="collect",
                    handle="@jordan")
    assert conn["direction"] == "collect"
    assert conn["beacon"] is None

    # Connecting a collector auto-consents the social:<platform> source.
    sources = {s["source"]: s["consented"] for s in client.get(f"/sources/{uid}").json()}
    assert sources.get("social:instagram") is True

    r = client.post(f"/social/connection/{conn['id']}/collect", json={"items": [
        {"content": "Slept badly, big week ahead."},
        {"content": "Walked 8k steps, feeling better."},
    ]})
    assert r.status_code == 201, r.text
    assert r.json()["ingested"] == 2
    assert client.get(f"/social/{uid}").json()[0]["collected"] == 2


def test_publish_and_beacon(client):
    uid = enroll(client)
    conn = _connect(client, uid, platform="x", direction="publish", handle="jordan")
    assert conn["beacon"] == f"/social/{conn['id']}/beacon"

    r = client.post(f"/social/connection/{conn['id']}/publish",
                    json={"content": "30-day streak — thanks Jim.", "topic": "milestone"})
    assert r.status_code == 201, r.text
    assert r.json()["status"] == "published"
    assert client.get(f"/social/{uid}").json()[0]["published"] == 1

    beacon = client.get(f"/social/connection/{conn['id']}/beacon").json()
    assert beacon["presence_url"] == "https://x.com/jordan"
    qr = client.get(f"/social/connection/{conn['id']}/qr.svg")
    assert qr.status_code == 200
    assert b"<svg" in qr.content


def test_direction_guards(client):
    uid = enroll(client)
    collect = _connect(client, uid, platform="tiktok", direction="collect")
    publish = _connect(client, uid, platform="youtube", direction="publish")
    assert client.post(f"/social/connection/{collect['id']}/publish",
                       json={"content": "x"}).status_code == 409
    assert client.post(f"/social/connection/{publish['id']}/collect",
                       json={"items": [{"content": "x"}]}).status_code == 409
    assert client.get(f"/social/connection/{collect['id']}/beacon").status_code == 409


def test_all_image_platforms_supported(client):
    uid = enroll(client)
    platforms = ["instagram", "x", "tiktok", "facebook", "linkedin", "youtube",
                 "reddit", "threads", "whatsapp", "meta", "mastodon", "twitch",
                 "snapchat", "roblox", "pinterest", "discord"]
    for p in platforms:
        assert _connect(client, uid, platform=p, direction="collect")["platform"] == p
    # A couple of the new platforms resolve to the right presence URL.
    for p, url in [("twitch", "https://twitch.tv/jordan"),
                   ("discord", "https://discord.com/users/jordan")]:
        conn = _connect(client, uid, platform=p, direction="publish", handle="jordan")
        assert client.get(f"/social/connection/{conn['id']}/beacon").json()["presence_url"] == url


def test_revoke_withdraws_consent(client):
    uid = enroll(client)
    conn = _connect(client, uid, platform="threads", direction="collect")
    assert client.delete(f"/social/connection/{conn['id']}").json()["status"] == "revoked"

    sources = {s["source"]: s["consented"] for s in client.get(f"/sources/{uid}").json()}
    assert sources.get("social:threads") is False
    # No further collection once revoked.
    r = client.post(f"/social/connection/{conn['id']}/collect",
                    json={"items": [{"content": "x"}]})
    assert r.status_code == 409
