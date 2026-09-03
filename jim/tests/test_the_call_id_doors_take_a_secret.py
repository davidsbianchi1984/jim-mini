"""The call-id doors take a secret.

The five reach-out call handlers are turned by the voice sidecar, and by
nothing else on the network. They keep the reviewer surfaces' rule: with
JIM_VOICE_SECRET unset, only localhost passes and a remote caller gets a 503
naming the variable; set, the bearer must be the secret — a person's own
session token is a 403 here, and every refusal is written down.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from jim import db, reachout

from .conftest import enroll
from .fakevoice import SITU, TWO

DOORS = [
    ("consent", {"digit": "1"}),
    ("say", {"heard": "hello"}),
    ("event", {"event": "answered"}),
    ("reached", None),
    ("unreached", None),
]
REFUSED = (401, 403, 503)


def _leg(client):
    uid = enroll(client)
    out = reachout.begin(uid, [TWO[0]], SITU)
    return uid, out["call"]["id"]


def _remote(app, host="172.18.0.4"):
    """The same app, reached from a compose-network address."""
    async def wrapped(scope, receive, send):
        if scope["type"] == "http":
            scope = dict(scope, client=(host, 4000))
        await app(scope, receive, send)
    return TestClient(wrapped)


def _refusals():
    return [dict(r) for r in db.connect().execute(
        "SELECT ref FROM audit WHERE action='voice.refused' ORDER BY seq").fetchall()]


@pytest.mark.parametrize("door,body", DOORS)
def test_unset_means_localhost_only(client, door, body):
    uid, cid = _leg(client)
    path = f"/reachout/call/{cid}/{door}"
    r = _remote(client.app).post(path, json=body)
    assert r.status_code == 503, r.text
    assert "JIM_VOICE_SECRET" in r.text
    # The in-process caller still passes, whatever it carries as a bearer.
    r = client.post(path, json=body)
    assert r.status_code not in REFUSED, r.text
    r = client.post(path, json=body, headers={"authorization": ""})
    assert r.status_code not in REFUSED, r.text


@pytest.mark.parametrize("door,body", DOORS)
def test_set_means_the_bearer_must_be_the_secret(client, monkeypatch, door, body):
    uid, cid = _leg(client)
    monkeypatch.setenv("JIM_VOICE_SECRET", "s3cret-shared-with-the-sidecar")
    path = f"/reachout/call/{cid}/{door}"
    r = client.post(path, json=body, headers={"authorization": ""})
    assert r.status_code == 401 and "voice adapter token required" in r.text
    # The person's own session token is not the sidecar's secret.
    r = client.post(path, json=body)
    assert r.status_code == 403 and "invalid voice adapter token" in r.text
    r = client.post(path, json=body, headers={"authorization": "Bearer wrong"})
    assert r.status_code == 403
    assert [x["ref"] for x in _refusals()] == [cid, cid, cid]
    # Localhost is no longer enough once the secret is set.
    r = client.post(path, json=body,
                    headers={"authorization": "Bearer s3cret-shared-with-the-sidecar"})
    assert r.status_code not in REFUSED, r.text
    r = _remote(client.app).post(
        path, json=body,
        headers={"authorization": "Bearer s3cret-shared-with-the-sidecar"})
    assert r.status_code not in REFUSED, r.text


def test_the_refusal_is_in_the_readers_language(client, monkeypatch):
    uid, cid = _leg(client)
    monkeypatch.setenv("JIM_VOICE_SECRET", "s3cret")
    r = client.post(f"/reachout/call/{cid}/event", json={"event": "answered"},
                    headers={"authorization": "", "accept-language": "es"})
    assert r.status_code == 401
    assert "voice adapter token required" not in r.text
    assert "token" in r.text.lower() or "adaptador" in r.text.lower()


def test_a_bearer_that_is_not_ascii_is_a_403_on_the_record(client, monkeypatch):
    # httpx will not send a non-ASCII header, so the door is turned directly
    # with the request Starlette would build from such bytes.
    from fastapi import HTTPException
    from starlette.requests import Request
    from jim import auth
    uid, cid = _leg(client)
    monkeypatch.setenv("JIM_VOICE_SECRET", "s3cret")
    scope = {"type": "http", "method": "POST", "path": f"/reachout/call/{cid}/event",
             "path_params": {"call_id": cid}, "query_string": b"",
             "headers": [(b"authorization", "Bearer s3crét".encode("latin-1"))],
             "client": ("172.18.0.4", 4000)}
    with pytest.raises(HTTPException) as caught:
        auth.require_voice_adapter(Request(scope))
    assert caught.value.status_code == 403
    assert [x["ref"] for x in _refusals()] == [cid]


def test_the_closed_door_refusal_is_written_down_too(client):
    uid, cid = _leg(client)
    r = _remote(client.app).post(f"/reachout/call/{cid}/event",
                                 json={"event": "answered"})
    assert r.status_code == 503
    assert [x["ref"] for x in _refusals()] == [cid]
