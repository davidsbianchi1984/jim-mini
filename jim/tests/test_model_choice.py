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


# --------------------------------------------------------------------------- #
# Honest provenance: the reply says who actually answered
# --------------------------------------------------------------------------- #

def test_coach_reply_names_who_actually_answered(client):
    """In the test env nothing is configured, so every reply is the stub's —
    and the reply must SAY so, instead of naming the provider that was
    picked. (The founder demoed canned distress text believing it was
    Claude; that is the bug this pins closed.)"""
    u = _enroll(client)
    client.put(f"/model/{u['id']}", json={"provider": "anthropic"},
               headers=_auth(u))
    r = client.post(f"/coach/{u['id']}",
                    json={"area": "career", "message": "I want this app "
                          "I built to be successful"},
                    headers=_auth(u)).json()
    prov = r["provenance"]
    assert prov["generated_by"] == "stub"          # who answered, not who was picked
    assert prov["degraded"] is True
    assert "anthropic" in prov["degraded_reason"]  # and why, actionably
    assert "Settings" in prov["degraded_reason"]


def test_a_stub_chat_reply_is_not_crisis_language(client):
    """The stub's medical-guidance script has a 'condition:' line to key on;
    chat has none. Chat must get an honest explanation of the fallback,
    never 'stub guidance for distress' with breathing instructions the
    user did not ask for."""
    u = _enroll(client)
    r = client.post(f"/coach/{u['id']}",
                    json={"area": "career", "message": "Any tips today?"},
                    headers=_auth(u)).json()
    assert "distress" not in r["content"]
    assert "breath" not in r["content"]
    assert "stub guidance" not in r["content"]
    assert "Settings" in r["content"]              # it points at the fix


def test_a_configured_model_is_reported_undegraded(client, monkeypatch):
    """When the picked provider genuinely answers, the reply says so and
    carries no warning."""
    from jim import llm

    class Fake:
        def generate(self, system, user):
            return "A real reply."

    monkeypatch.setattr(llm, "_build", lambda name: llm.FallbackProvider(
        name, Fake(), llm.StubProvider()))
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    u = _enroll(client)
    client.put(f"/model/{u['id']}", json={"provider": "anthropic"},
               headers=_auth(u))
    r = client.post(f"/coach/{u['id']}",
                    json={"area": "career", "message": "hello"},
                    headers=_auth(u)).json()
    assert r["content"] == "A real reply."
    assert r["provenance"]["generated_by"] == "anthropic"
    assert r["provenance"]["degraded"] is False
    assert r["provenance"]["degraded_reason"] is None


def test_a_mid_request_failure_reports_the_degrade(client, monkeypatch):
    """A provider that dies mid-request still answers (the stub steps in),
    but the reply discloses the swap and carries the failure."""
    from jim import llm

    class Dying:
        def generate(self, system, user):
            raise RuntimeError("HTTP 529: overloaded")

    monkeypatch.setattr(llm, "_build", lambda name: llm.FallbackProvider(
        name, Dying(), llm.StubProvider()) if name != "stub"
        else llm.StubProvider())
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-test")
    u = _enroll(client)
    client.put(f"/model/{u['id']}", json={"provider": "anthropic"},
               headers=_auth(u))
    r = client.post(f"/coach/{u['id']}",
                    json={"area": "career", "message": "hello"},
                    headers=_auth(u)).json()
    prov = r["provenance"]
    assert prov["generated_by"] == "stub"
    assert prov["degraded"] is True
    assert "did not answer" in prov["degraded_reason"]


def test_choosing_the_stub_on_purpose_is_not_a_degrade(client):
    u = _enroll(client)
    client.put(f"/model/{u['id']}", json={"provider": "stub"},
               headers=_auth(u))
    r = client.post(f"/coach/{u['id']}",
                    json={"area": "career", "message": "hello"},
                    headers=_auth(u)).json()
    assert r["provenance"]["generated_by"] == "stub"
    assert r["provenance"]["degraded"] is False


# --------------------------------------------------------------------------- #
# A real offline model: Ollama as a first-class provider
# --------------------------------------------------------------------------- #

def test_ollama_is_in_the_catalog_and_honest_about_absence(client):
    """The tile exists even when the daemon doesn't — configured says which."""
    body = client.get("/models").json()
    ollama = next(p for p in body["providers"] if p["name"] == "ollama")
    assert ollama["network"] is False          # nothing leaves the machine
    assert ollama["configured"] is False       # no daemon in the test env


def test_a_running_local_model_wins_auto_over_the_stub(client, monkeypatch):
    from jim import llm
    monkeypatch.delenv("JIM_LLM", raising=False)   # conftest pins the stub
    monkeypatch.setattr(llm, "_ollama_alive", lambda: True)
    assert llm.default_name() == "ollama"


def test_offline_mode_still_uses_a_running_local_model(client, monkeypatch):
    """JIM_OFFLINE forbids the network — and Ollama isn't network: it
    answers on loopback. A real local answer beats a canned one."""
    from jim import llm
    monkeypatch.setenv("JIM_OFFLINE", "1")
    monkeypatch.setattr(llm, "_ollama_alive", lambda: True)
    provider = llm.get_provider()
    assert isinstance(provider, llm.FallbackProvider)
    assert provider.name == "ollama"
    monkeypatch.setattr(llm, "_ollama_alive", lambda: False)
    assert isinstance(llm.get_provider(), llm.StubProvider)


def test_the_stub_now_points_at_the_free_local_option(client):
    u = _enroll(client)
    r = client.post(f"/coach/{u['id']}",
                    json={"area": "career", "message": "any tips?"},
                    headers=_auth(u)).json()
    assert "ollama.com" in r["content"]
    assert "offline" in r["content"]


def test_deepseek_and_the_founders_own_algorithm_are_on_the_menu(client):
    """The field ask: "implement deepseek for the time being until I can
    upload my algorithm … or any others on the market … to where they can
    pick and choose". Both new doors show on the menu."""
    by_name = {p["name"]: p for p in client.get("/models").json()["providers"]}
    assert by_name["deepseek"]["label"] == "DeepSeek"
    assert by_name["custom"]["label"] == "Your own algorithm"


def test_custom_provider_stays_dark_until_its_url_is_set(monkeypatch):
    """A key alone points at nothing: the plug-in-your-algorithm tile only
    lights once JIM_CUSTOM_LLM_URL names the endpoint."""
    from jim import llm
    monkeypatch.setenv("JIM_CUSTOM_LLM_KEY", "sk-somekey")
    monkeypatch.setitem(llm._REGISTRY["custom"], "base", "")
    assert llm.is_configured("custom") is False
    monkeypatch.setitem(llm._REGISTRY["custom"], "base",
                        "http://127.0.0.1:9999/v1")
    assert llm.is_configured("custom") is True
