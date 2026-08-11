"""The imported link, finally visited — the Guardian's side.

A ``collect`` connection has carried the account's public address since the
day it was made, and the collect door only ever stored what the owner pasted.
``POST /social/connection/{cid}/scrape`` goes to the address and ingests what
a browser would show anybody as a ``social:<platform>`` context event — the
title, the metadata bio, the visible text — so the Guardian understands more
of the life it is looking after.

The fetch is monkeypatched throughout; the one path that must never touch the
network — an offline deployment — is tested by poisoning the fetcher.
"""

from jim import offline, scrape
from jim.tests.conftest import enroll


def _connect(client, uid, **body):
    r = client.post(f"/social/{uid}", json=body)
    assert r.status_code == 201, r.text
    return r.json()


_PAGE = """
<html><head><title>Jordan (@jordan)</title>
<meta property="og:description" content="Runner. Rebuilding after an injury." />
</head><body>
<script>ignore me entirely</script>
<p>Back to easy 5ks this month.</p>
</body></html>
"""


def test_scrape_ingests_the_public_page_as_context(client, monkeypatch):
    uid = enroll(client)
    conn = _connect(client, uid, platform="instagram", direction="collect",
                    handle="@jordan")
    seen = {}

    def fake_fetch(url):
        seen["url"] = url
        return _PAGE
    monkeypatch.setattr(scrape, "fetch", fake_fetch)

    r = client.post(f"/social/connection/{conn['id']}/scrape")
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["ingested"] == 1
    assert out["url"] == "https://instagram.com/jordan"
    assert seen["url"] == out["url"]
    assert "Jordan" in out["title"]
    assert client.get(f"/social/{uid}").json()[0]["collected"] == 1


def test_offline_refuses_before_any_socket(client, monkeypatch):
    uid = enroll(client)
    conn = _connect(client, uid, platform="x", direction="collect",
                    handle="jordan")

    def explode(url):
        raise AssertionError("offline deployment opened a socket")
    monkeypatch.setattr(scrape, "fetch", explode)
    monkeypatch.setattr(offline, "enabled", lambda: True)

    r = client.post(f"/social/connection/{conn['id']}/scrape")
    assert r.status_code == 409
    assert "offline" in r.json()["detail"]


def test_a_connection_without_an_address_is_told_so(client):
    uid = enroll(client)
    conn = _connect(client, uid, platform="instagram", direction="collect")
    r = client.post(f"/social/connection/{conn['id']}/scrape")
    assert r.status_code == 400
    assert "handle" in r.json()["detail"]


def test_publish_connections_do_not_scrape(client):
    uid = enroll(client)
    conn = _connect(client, uid, platform="instagram", direction="publish",
                    handle="jordan")
    r = client.post(f"/social/connection/{conn['id']}/scrape")
    assert r.status_code == 409
