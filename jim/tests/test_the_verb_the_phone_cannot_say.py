"""Android's HTTP stack cannot say PATCH.

`HttpURLConnection.setRequestMethod("PATCH")` throws ProtocolException on
every Android release — the allowed verbs are a hard-coded list from 1997 and
PATCH is not on it. The other clients are unaffected: the console's fetch,
the iPhone's URLSession and the desktop's HttpClient all speak it natively.

So the one PATCH route this product has (`PATCH /goals/{uid}/{goal_id}`)
would be reachable from three clients and not the fourth — not for a product
reason but for a transport one. The middleware under test converts
`POST` + `x-http-method-override: PATCH` into PATCH before routing, and the
Android client sends exactly that.

The override is deliberately narrow: only POST converts, and only to PATCH.
A header asking for DELETE is ignored — an attacker who can set headers on a
victim's request could otherwise turn an innocent-looking POST into a
destructive verb the CORS preflight never mentioned.
"""

from .conftest import enroll


def _goal(client, uid):
    return client.post(f"/goals/{uid}",
                       json={"area": "health_fitness",
                             "title": "Walk daily"}).json()


def test_the_override_reaches_the_patch_route(client):
    uid = enroll(client)
    goal = _goal(client, uid)
    done = client.post(
        f"/goals/{uid}/{goal['id']}",
        json={"progress": 1.0, "status": "completed"},
        headers={"x-http-method-override": "PATCH"})
    assert done.status_code == 200, done.text
    assert done.json()["status"] == "completed"
    assert done.json()["progress"] == 1.0


def test_without_the_header_the_post_still_404s(client):
    """No PATCH route gains a POST twin by accident: the bare POST answers
    exactly what it answered before the middleware existed."""
    uid = enroll(client)
    goal = _goal(client, uid)
    bare = client.post(f"/goals/{uid}/{goal['id']}", json={"progress": 1.0})
    assert bare.status_code in (404, 405)


def test_the_override_speaks_patch_and_nothing_else(client):
    """A DELETE override is ignored, not obeyed — the goal survives."""
    uid = enroll(client)
    goal = _goal(client, uid)
    tried = client.post(
        f"/goals/{uid}/{goal['id']}", json={},
        headers={"x-http-method-override": "DELETE"})
    assert tried.status_code in (404, 405)
    rows = client.get(f"/goals/{uid}").json()
    assert [g for g in rows if g["id"] == goal["id"]], "the goal was deleted"
