"""Capability-token authentication: every per-user surface is PHI and is
gated behind the user token minted at enrollment; setup/health stay open."""


def _enroll(client, **extra):
    """Enroll via the raw client, returning the JSON (with the one-time
    user_token) without mutating the client's default headers."""
    body = {"display_name": "Jordan", "birthdate": "1995-05-05",
            "terms_consent": True, "resting_heart_rate": 60}
    body.update(extra)
    r = client.post("/enroll", json=body, headers={})
    assert r.status_code == 201, r.text
    return r.json()


def test_enroll_returns_user_token_once(client):
    u = _enroll(client)
    assert u["user_token"] and u["id"]


def test_user_endpoints_require_a_token(client):
    u = _enroll(client)
    uid = u["id"]
    # No credential → 401 across representative PHI surfaces.
    assert client.get(f"/events/{uid}", headers={}).status_code == 401
    assert client.get(f"/journal/{uid}", headers={}).status_code == 401
    assert client.post(f"/monitor/{uid}", headers={},
                       json={"heart_rate": 80}).status_code == 401
    assert client.delete(f"/data/{uid}", headers={}).status_code == 401


def test_wrong_user_token_is_forbidden(client):
    a = _enroll(client)
    b = _enroll(client, display_name="Other")
    wrong = {"authorization": f"Bearer {b['user_token']}"}
    # B's valid token cannot read A's data → 403 (not 401).
    assert client.get(f"/events/{a['id']}", headers=wrong).status_code == 403
    assert client.get(f"/journal/{a['id']}", headers=wrong).status_code == 403
    # A garbage token → 401.
    assert client.get(f"/events/{a['id']}",
                      headers={"authorization": "Bearer nope"}).status_code == 401


def test_correct_user_token_authorizes(client):
    u = _enroll(client)
    ok = {"authorization": f"Bearer {u['user_token']}"}
    assert client.post(f"/monitor/{u['id']}", headers=ok,
                       json={"heart_rate": 72}).status_code == 200
    assert client.get(f"/events/{u['id']}", headers=ok).status_code == 200
    assert client.get(f"/report/{u['id']}", headers=ok).status_code == 200


def test_setup_and_health_need_no_token(client):
    assert client.get("/health", headers={}).status_code == 200
    assert client.get("/cloud/status", headers={}).status_code == 200
    # Enrolling and registering a specialist are open setup surfaces.
    assert client.post("/enroll", headers={}, json={
        "display_name": "New", "terms_consent": True}).status_code == 201
    assert client.post("/specialists", headers={}, json={
        "condition": "anxiety", "mode": "local"}).status_code == 200


def test_delete_revokes_the_user_token(client):
    u = _enroll(client)
    ok = {"authorization": f"Bearer {u['user_token']}"}
    assert client.delete(f"/data/{u['id']}", headers=ok).status_code == 200
    # The user is gone and the token no longer resolves.
    assert client.get(f"/events/{u['id']}", headers=ok).status_code == 404
