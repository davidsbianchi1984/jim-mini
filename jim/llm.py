"""LLM provider for JIM-mini's own (standalone) guidance.

Mirrors QRME's provider pattern but is independent — JIM ships its own so the
two projects share no code. Claude (Anthropic) is the default; without
credentials (or with ``JIM_LLM=stub``) a deterministic stub keeps standalone
guidance working offline.

A user is not locked to Claude. They can route their guidance through
**ChatGPT (OpenAI)**, **Grok (xAI)**, **Perplexity**, or **Gemini (Google)**,
or pin the offline stub, via ``PUT /model/{user_id}``. The choice is stored per
user and honored on every coaching reply and guidance generation.

Design rules:

* **Deterministic stub is the floor.** Any network provider that errors (bad
  key, outage, missing SDK) degrades to the stub instead of failing — a health
  app must never go dark because a third-party model is down — and the degrade
  is logged.
* **Offline is absolute.** In ``JIM_OFFLINE`` mode every network provider is
  bypassed regardless of the per-user choice.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from contextvars import ContextVar
from typing import Protocol

logger = logging.getLogger("jim.llm")

# Bring-your-own key: a caller may send ``x-llm-api-key`` and the request's
# generations run on *their* credential instead of the deployment's. The key
# lives in a request-scoped context variable set by API middleware — it is
# never persisted, never logged, and gone when the request ends. The
# deployment's own env key (the operator lending theirs out) stays the
# fallback for requests that bring none.
_REQUEST_KEY: ContextVar[str | None] = ContextVar("jim_llm_request_key",
                                                  default=None)


def set_request_key(key: str | None):
    """Install a caller-supplied API key for the current request; returns the
    reset token. Middleware owns the set/reset pairing."""
    return _REQUEST_KEY.set(key or None)


def reset_request_key(token) -> None:
    _REQUEST_KEY.reset(token)


def request_key() -> str | None:
    return _REQUEST_KEY.get()

MODEL = os.environ.get("JIM_MODEL", "claude-opus-5")

_OPENAI_MODEL = os.environ.get("JIM_OPENAI_MODEL", "gpt-4o")
_GROK_MODEL = os.environ.get("JIM_GROK_MODEL", "grok-2-latest")
_PPLX_MODEL = os.environ.get("JIM_PERPLEXITY_MODEL", "sonar")
_GEMINI_MODEL = os.environ.get("JIM_GEMINI_MODEL", "gemini-2.0-flash")

_TIMEOUT = int(os.environ.get("JIM_LLM_TIMEOUT", "30"))


class Provider(Protocol):
    def generate(self, system: str, user: str) -> str: ...


def _offline() -> bool:
    return os.environ.get("JIM_OFFLINE", "").strip().lower() in {"1", "true", "yes", "on"}


# --------------------------------------------------------------------------- #
# Providers
# --------------------------------------------------------------------------- #

class AnthropicProvider:
    def __init__(self, api_key: str | None = None) -> None:
        import anthropic

        self._client = (anthropic.Anthropic(api_key=api_key) if api_key
                        else anthropic.Anthropic())

    def generate(self, system: str, user: str) -> str:
        response = self._client.messages.create(
            model=MODEL,
            max_tokens=1024,
            thinking={"type": "adaptive"},
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in response.content if b.type == "text").strip()


class OpenAICompatibleProvider:
    """OpenAI ``/chat/completions``-shaped API: OpenAI, xAI (Grok), Perplexity."""

    def __init__(self, name: str, base_url: str, api_key: str, model: str) -> None:
        self.name = name
        self._base = base_url.rstrip("/")
        self._key = api_key
        self._model = model

    def generate(self, system: str, user: str) -> str:
        payload = {
            "model": self._model,
            "max_tokens": 1024,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        body = _post_json(
            f"{self._base}/chat/completions",
            payload,
            {"Authorization": f"Bearer {self._key}"},
        )
        try:
            return body["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"{self.name}: unexpected response shape") from exc


class GeminiProvider:
    """Google Gemini via the Generative Language REST API."""

    def __init__(self, api_key: str, model: str) -> None:
        self._key = api_key
        self._model = model

    def generate(self, system: str, user: str) -> str:
        payload = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
        }
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self._model}:generateContent?key={self._key}"
        )
        body = _post_json(url, payload, {})
        try:
            parts = body["candidates"][0]["content"]["parts"]
            return "".join(p.get("text", "") for p in parts).strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("gemini: unexpected response shape") from exc


class StubProvider:
    def generate(self, system: str, user: str) -> str:
        label = _extract(system, "condition: ")
        tone = _extract(system, "tone: ")
        if label is None:
            # No condition line means this is conversation — coaching, a
            # check-in — not the medical-guidance path. The stub used to
            # answer chat with crisis language ("stub guidance for
            # distress... one slow breath together"), which read as the
            # coach diagnosing distress that was never there. In chat the
            # only honest stub reply is an explanation of itself. (The tone
            # marker still rides along — it is how tests prove personality
            # reaches the prompt.)
            text = (
                "I'm the built-in offline helper, so I can't give you a real "
                "coaching reply — no online model answered this request. "
                "Your message is saved. To get full answers, open Settings → "
                "Model, pick a provider, and add its API key."
            )
            return text + (f" (tone: {tone})" if tone else "")
        text = (
            f"I'm here with you. [stub guidance for {label}] "
            "Let's take one slow breath together, and tell me what feels most urgent."
        )
        if tone:
            text += f" (tone: {tone})"
        return text


class FallbackProvider:
    """Degrade any network provider to a local fallback (the stub) on failure,
    logging the degrade. A health app must never go dark on a model outage.

    The degrade is recorded on the instance (``answered_by``, ``failure``) so
    a caller can tell the user the truth about who actually answered —
    a log line the user will never read is not disclosure."""

    def __init__(self, name: str, primary: Provider, fallback: Provider) -> None:
        self.name = name
        self._primary = primary
        self._fallback = fallback
        self.answered_by = name
        self.failure: str | None = None

    def generate(self, system: str, user: str) -> str:
        try:
            text = self._primary.generate(system, user)
            self.answered_by, self.failure = self.name, None
            return text
        except Exception as exc:  # noqa: BLE001
            logger.warning("provider %s failed, using local fallback: %s",
                           self.name, exc)
            self.answered_by = "stub"
            self.failure = f"{self.name} did not answer: {exc}"
            return self._fallback.generate(system, user)


# --------------------------------------------------------------------------- #
# Registry
# --------------------------------------------------------------------------- #

_REGISTRY: dict[str, dict] = {
    "stub": {"label": "Deterministic stub (offline)", "kind": "stub",
             "network": False, "env": [], "model": "stub"},
    "anthropic": {"label": "Claude (Anthropic)", "kind": "anthropic",
                  "network": True, "env": ["ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"],
                  "model": MODEL},
    "openai": {"label": "ChatGPT (OpenAI)", "kind": "openai", "network": True,
               "env": ["OPENAI_API_KEY"], "base": "https://api.openai.com/v1",
               "model": _OPENAI_MODEL},
    "grok": {"label": "Grok (xAI)", "kind": "openai", "network": True,
             "env": ["XAI_API_KEY", "GROK_API_KEY"], "base": "https://api.x.ai/v1",
             "model": _GROK_MODEL},
    "perplexity": {"label": "Perplexity", "kind": "openai", "network": True,
                   "env": ["PERPLEXITY_API_KEY", "PPLX_API_KEY"],
                   "base": "https://api.perplexity.ai", "model": _PPLX_MODEL},
    "gemini": {"label": "Gemini (Google)", "kind": "gemini", "network": True,
               "env": ["GEMINI_API_KEY", "GOOGLE_API_KEY"], "model": _GEMINI_MODEL},
}

CHOICES = ("auto", *_REGISTRY.keys())


def _env_value(name: str) -> str | None:
    for key in _REGISTRY[name].get("env", []):
        val = os.environ.get(key)
        if val:
            return val
    return None


def is_configured(name: str) -> bool:
    if name == "stub":
        return True
    if name == "anthropic" and os.environ.get("JIM_LLM") == "anthropic":
        return True
    if name not in _REGISTRY:
        return False
    return _env_value(name) is not None


def available() -> list[dict]:
    return [
        {"name": name, "label": spec["label"], "network": spec["network"],
         "model": spec["model"], "configured": is_configured(name)}
        for name, spec in _REGISTRY.items()
    ]


def default_name() -> str:
    env = os.environ.get("JIM_LLM")
    if env in _REGISTRY and is_configured(env):
        return env
    # A caller who typed a key in wants a real model, not the stub — and the
    # product's default model is Claude.
    if is_configured("anthropic") or request_key():
        return "anthropic"
    return "stub"


def resolve_choice(choice: str | None) -> str:
    if choice and choice != "auto":
        if choice in _REGISTRY and (is_configured(choice) or request_key()):
            # A caller-supplied key IS the configuration for their explicit
            # choice — the deployment needing no credential of its own is the
            # whole point of bring-your-own.
            return choice
        logger.warning("requested provider %r is not available; using default",
                       choice)
    return default_name()


def _build(name: str) -> Provider:
    spec = _REGISTRY.get(name, _REGISTRY["stub"])
    stub = StubProvider()
    if name == "stub":
        return stub
    # The request's own key outranks the deployment's env key: somebody who
    # typed their credential in expects their requests billed to it.
    key = request_key() or _env_value(name)
    try:
        if spec["kind"] == "anthropic":
            primary: Provider = AnthropicProvider(api_key=request_key())
        elif spec["kind"] == "openai":
            primary = OpenAICompatibleProvider(
                name, spec["base"], key or "", spec["model"])
        elif spec["kind"] == "gemini":
            primary = GeminiProvider(key or "", spec["model"])
        else:
            return stub
    except Exception as exc:  # noqa: BLE001 — e.g. missing SDK
        logger.warning("could not build provider %s: %s", name, exc)
        return stub
    return FallbackProvider(name, primary, stub)


def get_provider(cloud=None, choice: str | None = None) -> Provider:
    """Return the provider to generate with.

    * **Offline** (``JIM_OFFLINE``) always returns the local stub.
    * An **explicit** ``choice`` is honored directly (with stub fallback) and is
      not routed through the cloud gateway.
    * Otherwise the default provider is used, optionally via the cloud gateway's
      greater model with local fallback (unchanged behavior).
    """
    if _offline():
        return StubProvider()

    explicit = bool(choice) and choice != "auto"
    name = resolve_choice(choice)
    base = _build(name)

    if not explicit:
        if cloud is None and os.environ.get("JIM_CLOUD_URL"):
            from .cloud import CloudModelClient
            cloud = CloudModelClient(token=os.environ.get("JIM_CLOUD_TOKEN", ""),
                                     base_url=os.environ["JIM_CLOUD_URL"])
        if cloud is not None:
            from .cloud import CloudProvider
            return CloudProvider(cloud, fallback=base)
    return base


# --------------------------------------------------------------------------- #
# Per-user preference (stored in the ``model_prefs`` table)
# --------------------------------------------------------------------------- #

def get_choice(user_id: str) -> str:
    from . import db
    row = db.connect().execute(
        "SELECT provider FROM model_prefs WHERE user_id=?", (user_id,)
    ).fetchone()
    return row["provider"] if row else "auto"


def set_choice(user_id: str, provider: str) -> str:
    if provider not in CHOICES:
        raise ValueError(f"unknown provider {provider!r}")
    from . import db
    conn = db.connect()
    conn.execute(
        "INSERT INTO model_prefs (user_id, provider, updated_at) VALUES (?,?,?)"
        " ON CONFLICT(user_id) DO UPDATE SET provider=excluded.provider,"
        " updated_at=excluded.updated_at",
        (user_id, provider, db.utcnow()),
    )
    conn.commit()
    logger.info("user %s set model provider -> %s", user_id, provider)
    return provider


def provider_for_user(user_id: str, cloud=None) -> Provider:
    return get_provider(cloud=cloud, choice=get_choice(user_id))


def generate_for_user(user_id: str, system: str, user: str, cloud=None) -> dict:
    """Generate a reply and report honestly who produced the words.

    ``provider_for_user().generate()`` answers, but it cannot say *who*
    answered: a network failure, a missing key or a missing SDK all degrade
    to the stub with only a server-side log line — so a user whose Claude
    was never reachable saw stub text under a screen that said Claude.
    This wrapper is the disclosure: ``provider`` is whoever actually
    generated the text, ``degraded`` says it wasn't who they meant, and
    ``reason`` says why in words a user can act on.
    """
    choice = get_choice(user_id)
    intended = resolve_choice(choice)
    provider = get_provider(cloud=cloud, choice=choice)
    text = provider.generate(system, user)

    actual, reason = intended, None
    if isinstance(provider, FallbackProvider):
        actual, reason = provider.answered_by, provider.failure
    elif isinstance(provider, StubProvider):
        actual = "stub"

    degraded = actual == "stub" and choice != "stub"
    if degraded and reason is None:
        if _offline():
            reason = "offline mode is on, so no request leaves this machine"
        elif choice != "auto":
            reason = (f"{choice} has no API key on this machine — add one "
                      "in Settings → Model")
        elif intended == "stub":
            reason = ("no online model is configured on this machine — add "
                      "an API key in Settings → Model")
        else:
            reason = f"{intended} could not start on this machine"
    return {"text": text, "provider": actual, "degraded": degraded,
            "reason": reason}


def _extract(text: str, marker: str) -> str | None:
    for line in text.splitlines():
        if marker in line:
            return line.split(marker, 1)[1].strip().rstrip(".")
    return None


# --------------------------------------------------------------------------- #
# Low-level HTTP (stdlib only, matching jim.cloud)
# --------------------------------------------------------------------------- #

def _post_json(url: str, payload: dict, headers: dict) -> dict:
    data = json.dumps(payload).encode()
    h = {"content-type": "application/json", **headers}
    req = urllib.request.Request(url, data=data, method="POST", headers=h)
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:200]
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"network error: {exc}") from exc
