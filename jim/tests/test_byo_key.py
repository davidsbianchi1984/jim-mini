"""Bring-your-own model key: ``x-llm-api-key`` rides the request.

The caller's generations run on their credential; the deployment's env key
(the operator lending theirs out) is the fallback; the key is request-scoped
— never persisted, gone when the request ends.
"""

from __future__ import annotations

from jim import llm


def _enroll(client):
    r = client.post("/enroll", json={
        "display_name": "Jordan", "birthdate": "1995-05-05",
        "terms_consent": True})
    assert r.status_code == 201
    return r.json()


def _auth(u, **extra):
    return {"authorization": f"Bearer {u['user_token']}", **extra}


def test_a_request_key_makes_the_chosen_provider_usable(client, monkeypatch):
    """With no env keys at all, an explicit choice + a caller key resolves to
    that provider instead of being dropped for the default."""
    u = _enroll(client)
    r = client.put(f"/model/{u['id']}", json={"provider": "anthropic"},
                   headers=_auth(u, **{"x-llm-api-key": "sk-their-own"}))
    assert r.status_code == 200, r.text
    assert r.json()["effective"] == "anthropic"


def test_without_a_key_the_unconfigured_choice_still_falls_back(client):
    u = _enroll(client)
    r = client.put(f"/model/{u['id']}", json={"provider": "anthropic"},
                   headers=_auth(u))
    assert r.status_code == 200, r.text
    assert r.json()["effective"] == "stub"


def test_a_key_with_auto_defaults_to_a_real_model_not_the_stub(client, monkeypatch):
    # The test env pins JIM_LLM=stub — an explicit operator choice that
    # outranks auto. A fresh install has no such pin; simulate that here.
    monkeypatch.delenv("JIM_LLM", raising=False)
    u = _enroll(client)
    r = client.get(f"/model/{u['id']}",
                   headers=_auth(u, **{"x-llm-api-key": "sk-their-own"}))
    assert r.status_code == 200
    assert r.json()["effective"] == "anthropic"
    # And the same request without the key answers stub — the key was
    # request-scoped, not remembered.
    r = client.get(f"/model/{u['id']}", headers=_auth(u))
    assert r.json()["effective"] == "stub"


def test_the_key_reaches_the_provider_build(client, monkeypatch):
    """The generation path constructs the provider with the caller's key."""
    seen: dict = {}

    class FakeAnthropic:
        def __init__(self, api_key=None, timeout=None):
            seen["api_key"] = api_key
            seen["timeout"] = timeout      # JIM_LLM_TIMEOUT bounds this path too
            raise RuntimeError("stop here — construction is the assertion")

    import sys
    import types

    fake_mod = types.SimpleNamespace(Anthropic=FakeAnthropic)
    monkeypatch.setitem(sys.modules, "anthropic", fake_mod)
    monkeypatch.delenv("JIM_LLM", raising=False)   # drop the test env's stub pin

    u = _enroll(client)
    client.put(f"/model/{u['id']}", json={"provider": "anthropic"},
               headers=_auth(u, **{"x-llm-api-key": "sk-their-own"}))
    r = client.post(f"/coach/{u['id']}",
                    json={"area": "health_fitness",
                          "message": "How do I wind down at night?"},
                    headers=_auth(u, **{"x-llm-api-key": "sk-their-own"}))
    # The failed construction degrades to the stub — the reply still comes.
    assert r.status_code == 200, r.text
    assert seen["api_key"] == "sk-their-own"
    assert seen["timeout"] == 30            # the default ceiling, on every path


def test_the_key_is_never_persisted(client):
    u = _enroll(client)
    client.put(f"/model/{u['id']}", json={"provider": "anthropic"},
               headers=_auth(u, **{"x-llm-api-key": "sk-their-own"}))
    from jim import db
    row = db.connect().execute(
        "SELECT provider FROM model_prefs WHERE user_id=?", (u["id"],)
    ).fetchone()
    assert row["provider"] == "anthropic"          # the choice is stored
    assert llm.request_key() is None               # the key is gone
    # And nowhere in the database either.
    dump = "\n".join(db.connect().iterdump())
    assert "sk-their-own" not in dump
