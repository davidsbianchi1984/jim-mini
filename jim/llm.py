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
# The local model: whatever the user pulled into Ollama. deepseek-r1:1.5b
# is small enough for most machines; JIM_OLLAMA_MODEL overrides.
_OLLAMA_MODEL = os.environ.get("JIM_OLLAMA_MODEL", "deepseek-r1:1.5b")
_OLLAMA_BASE = os.environ.get("JIM_OLLAMA_URL",
                              "http://127.0.0.1:11434") + "/v1"

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

        # Gated here and not only where a provider is chosen — a gate on
        # the factory is walked past by anything constructing one directly.
        #
        #     asked     does offline mode pick a local provider
        #     mattered  can a remote one still be built and used
        from . import offline
        if offline.enabled():
            raise offline.LeftTheHost(
                "offline mode is on, so the Anthropic API cannot be reached. "
                "Nothing leaves this machine while JIM_OFFLINE is set.")
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
                "coaching reply — no model answered this request. Your "
                "message is saved. Two ways to get full answers: open "
                "Settings → Model and add a provider's API key, or install "
                "Ollama (ollama.com) and pull a model like deepseek-r1:1.5b "
                "— free, offline, and JIM will find it on its own."
            )
            return text + (f" (tone: {tone})" if tone else "")
        text = (
            f"I'm here with you. [stub guidance for {label}] "
            "Let's take one slow breath together, and tell me what feels most urgent."
        )
        if tone:
            text += f" (tone: {tone})"
        return text


#: The memory prefix the vault provider may ground on, set around a
#: generation by whoever knows whose turn this is (`generate_for_user`).
#: A contextvar rather than a constructor argument because providers are
#: built per call, below the layer that knows the person.
_GROUND_PREFIX: ContextVar[str | None] = ContextVar("jim_ground_prefix",
                                                    default=None)


class VaultProvider:
    """The vault's own local model, through PDI's resident voice door.

    The prompt travels the same authenticated channel every seal uses and
    goes no further: `/resident/infer` runs it on the facility's own
    inference server, and the audit line there carries the prompt's
    length, never its words — a coach that speaks from inside the
    building the data never leaves. A vault with *no* local model raises
    rather than speaking the resident's operational stub sentence in the
    coach's voice; `FallbackProvider` then hands the turn to this
    product's own stub, and the reason is in the log.
    """

    #: Whether the last answer was grounded in the vault's own seals —
    #: read by `generate_for_user` for the disclosure, because a person
    #: told "the coach remembers" is owed knowing when it could not.
    grounded = False
    drew_on: list = []

    def generate(self, system: str, user: str) -> str:
        from . import pdi_client
        client = pdi_client.active()
        if client is None:
            raise RuntimeError("no PDI tandem is configured")
        self.grounded, self.drew_on = False, []
        prefix = _GROUND_PREFIX.get()
        out = None
        if prefix:
            # Grounded: the vault ranks this person's own seals against
            # the question and answers from them — retrieval and
            # generation both inside the facility, with the prefix as the
            # per-person wall inside the shared tenant. An older PDI
            # without the ask door answers None and the voice door below
            # still speaks, ungrounded and said so.
            ask = getattr(client, "resident_ask", None)
            out = ask(user, prefix=prefix,
                      system=system + "\nSpeak as yourself, to the "
                      "person, in one reply.") if ask else None
            if out is not None:
                self.grounded = True
                self.drew_on = list(out.get("drew_on") or [])
        if out is None:
            out = client.resident_infer(
                system + "\n\nPerson: " + user + "\nYou: ")
        if out is None:
            raise RuntimeError("this PDI has no voice door (older tandem)")
        if out.get("model") == "stub":
            raise RuntimeError("the vault has no local model installed")
        text = (out.get("text") or "").strip()
        if not text:
            raise RuntimeError("the vault's model answered nothing")
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

_DEEPSEEK_MODEL = os.environ.get("JIM_DEEPSEEK_MODEL", "deepseek-chat")
# The founder's own algorithm, or anything speaking the OpenAI dialect: point
# JIM_CUSTOM_LLM_URL at it and it becomes a first-class provider tile. This
# is the plug David asked for — "the option to plug in my algorithm" — built
# as configuration so the day the algorithm exists, no release is needed.
_CUSTOM_BASE = os.environ.get("JIM_CUSTOM_LLM_URL", "")
_CUSTOM_MODEL = os.environ.get("JIM_CUSTOM_LLM_MODEL", "default")
_CUSTOM_LABEL = os.environ.get("JIM_CUSTOM_LLM_LABEL", "Your own algorithm")

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
    "deepseek": {"label": "DeepSeek", "kind": "openai", "network": True,
                 "env": ["JIM_DEEPSEEK_API_KEY", "DEEPSEEK_API_KEY"],
                 "base": "https://api.deepseek.com/v1",
                 "model": _DEEPSEEK_MODEL},
    # See _CUSTOM_BASE above: any OpenAI-dialect endpoint, the founder's own
    # algorithm first among them. Configured when the URL is set.
    "custom": {"label": _CUSTOM_LABEL, "kind": "openai", "network": True,
               "env": ["JIM_CUSTOM_LLM_KEY"], "base": _CUSTOM_BASE,
               "model": _CUSTOM_MODEL, "needs_base": True},
    # A real offline model, not the canned stub: Ollama (ollama.com) runs
    # models like deepseek-r1:1.5b or llama3.2 on the user's own machine —
    # free, no key, no internet once the model is pulled. JIM treats a
    # running Ollama as a configured provider; "network": False because no
    # request leaves the machine, which also means offline mode allows it.
    "ollama": {"label": "Local (Ollama)", "kind": "openai", "network": False,
               "env": [], "base": _OLLAMA_BASE, "model": _OLLAMA_MODEL},
    "vault": {"label": "The vault's local model (PDI resident)",
              "kind": "vault", "network": True, "env": [],
              "model": "resident-local"},
}

CHOICES = ("auto", *_REGISTRY.keys())


def _env_value(name: str) -> str | None:
    for key in _REGISTRY[name].get("env", []):
        val = os.environ.get(key)
        if val:
            return val
    return None


_OLLAMA_PROBE: dict = {"at": 0.0, "alive": False}


def _ollama_alive() -> bool:
    """Is a local Ollama daemon answering? Probed, because there is no key
    to check — the daemon running IS the configuration. Cached briefly so
    the settings screen doesn't knock on the port for every tile."""
    import time
    if time.monotonic() - _OLLAMA_PROBE["at"] < 10:
        return _OLLAMA_PROBE["alive"]
    alive = False
    try:
        probe = _OLLAMA_BASE.rsplit("/v1", 1)[0] + "/api/version"
        # "nothing leaves the machine" was true of the default and
        # never checked — the base URL is configurable.
        from . import offline
        offline.allow(probe, "the local model daemon")
        req = urllib.request.Request(probe)
        with urllib.request.urlopen(req, timeout=0.5) as r:
            alive = r.status == 200
    except Exception:  # noqa: BLE001 — not running is the common case
        alive = False
    _OLLAMA_PROBE.update(at=time.monotonic(), alive=alive)
    return alive


def is_configured(name: str) -> bool:
    if name == "stub":
        return True
    if name == "anthropic" and os.environ.get("JIM_LLM") == "anthropic":
        return True
    if name == "ollama":
        return _ollama_alive()
    if name == "vault":
        # Configured when a PDI tandem is attached: the model itself lives
        # on the vault's host, and a facility without one answers honestly
        # at generation time.
        from . import pdi_client
        return pdi_client.active() is not None
    if name not in _REGISTRY:
        return False
    # A provider whose whole point is a user-supplied endpoint (the
    # founder's own algorithm) is configured only once the URL is set —
    # a key alone points at nothing.
    if _REGISTRY[name].get("needs_base") and not _REGISTRY[name].get("base"):
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
    # No key anywhere, but a local model is running: a real answer beats a
    # canned one, and it never leaves the machine.
    if is_configured("ollama"):
        return "ollama"
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
        elif spec["kind"] == "vault":
            primary = VaultProvider()
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
        # Offline is absolute for the network — but Ollama IS offline: it
        # answers on loopback and nothing leaves the machine. A running
        # local model is exactly what offline mode wants.
        if is_configured("ollama"):
            return _build("ollama")   # already stub-backed via FallbackProvider
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


def is_network(name: str) -> bool:
    """Whether a resolved provider name reaches an external host — the
    registry's own `network` column, published rather than re-guessed by
    each caller. Unknown names answer False — a door not in the registry
    is not a door to the internet. Note the vault answers True: a socket
    does open; whether that counts as *leaving* is the caller's question
    (the excursions and the letter both say the facility's own wire does
    not)."""
    return bool(_REGISTRY.get(name, {}).get("network"))


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
    # The vault provider may ground on this person's own seals — and only
    # theirs: the prefix is the per-person wall inside the shared tenant.
    ground = _GROUND_PREFIX.set(f"jim/{user_id}/memory/")
    try:
        text = provider.generate(system, user)
    finally:
        _GROUND_PREFIX.reset(ground)

    actual, reason = intended, None
    # Duck-typed on the two attributes rather than isinstance-checked against
    # one class. It named `FallbackProvider` alone, so `cloud.CloudProvider` —
    # which degrades to the same stub — fell through to `intended` and was
    # reported as an undegraded answer from the model the user had chosen.
    #
    #     asked     did the fallback provider degrade
    #     mattered  did anything degrade
    if hasattr(provider, "answered_by"):
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
    # Whether the vault grounded this answer in the person's own seals —
    # walked off the provider duck-typed, through a fallback wrapper if
    # one is standing in front of it.
    inner = getattr(provider, "_primary", provider)
    grounded = bool(getattr(inner, "grounded", False)) and actual != "stub"
    return {"text": text, "provider": actual, "degraded": degraded,
            "reason": reason, "grounded": grounded,
            "drew_on": list(getattr(inner, "drew_on", []) or [])
                       if grounded else []}


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
    from . import offline
    offline.allow(url, "the model provider")
    req = urllib.request.Request(url, data=data, method="POST", headers=h)
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
            return json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:200]
        raise RuntimeError(f"HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"network error: {exc}") from exc
