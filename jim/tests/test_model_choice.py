"""Per-user LLM provider selection (GET /models, GET/PUT /model/{user_id})."""


def _enroll(client, **extra):
    body = {"display_name": "Jordan", "birthdate": "1995-05-05",
            "terms_consent": True, "resting_heart_rate": 60}
    body.update(extra)
    r = client.post("/enroll", json=body, headers={})
    assert r.status_code == 201, r.text
    return r.json()


def _auth(u):
    return {"authorization": f"Bearer {u['user_token']}"}


def test_list_models_includes_all_providers(client):
    body = client.get("/models").json()
    names = {p["name"] for p in body["providers"]}
    assert {"stub", "anthropic", "openai", "grok", "perplexity", "gemini"} <= names
    assert body["default"] == "stub"  # only the stub is configured in tests


def test_user_defaults_to_auto(client):
    u = _enroll(client)
    r = client.get(f"/model/{u['id']}", headers=_auth(u))
    assert r.status_code == 200, r.text
    assert r.json()["provider"] == "auto"
    assert r.json()["effective"] == "stub"


def test_user_can_choose_provider(client):
    u = _enroll(client)
    r = client.put(f"/model/{u['id']}", json={"provider": "openai"}, headers=_auth(u))
    assert r.status_code == 200, r.text
    assert r.json()["provider"] == "openai"
    assert r.json()["effective"] == "stub"  # no key in test env → degrades
    assert client.get(f"/model/{u['id']}", headers=_auth(u)).json()["provider"] == "openai"


def test_model_endpoints_require_the_user_token(client):
    u = _enroll(client)
    assert client.get(f"/model/{u['id']}", headers={}).status_code == 401
    assert client.put(f"/model/{u['id']}", json={"provider": "openai"},
                      headers={}).status_code == 401


def test_unknown_provider_rejected(client):
    u = _enroll(client)
    r = client.put(f"/model/{u['id']}", json={"provider": "nope"}, headers=_auth(u))
    assert r.status_code == 422


def test_coach_still_works_with_a_chosen_provider(client):
    # An unconfigured provider must never break guidance — it degrades to stub.
    u = _enroll(client)
    client.put(f"/model/{u['id']}", json={"provider": "grok"}, headers=_auth(u))
    r = client.post(f"/coach/{u['id']}",
                    json={"area": "mental_health", "message": "I feel stuck"},
                    headers=_auth(u))
    assert r.status_code == 200, r.text
    assert r.json()["content"]
