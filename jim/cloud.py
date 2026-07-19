"""Cloud Model Gateway client — a greater model, and a way to give back.

The local provider stack (Anthropic SDK or the offline stub) always works.
When a Cloud Model Gateway is configured (`JIM_CLOUD_URL` +
`JIM_CLOUD_TOKEN`, or an injected client), JIM-mini can additionally:

- **use a greater model** — inference routes to the gateway's hosted tier
  (the latest, most capable model, e.g. `claude-fable-5`) with automatic
  fallback to the local provider if the gateway is unreachable; and
- **contribute to it** — strictly opt-in per user (`cloud_contribution`
  at enrollment): anonymized guidance outcomes (condition, severity, rating)
  are sent to the gateway's contribution intake to improve the shared model.
  No user ids, names, notes, or raw biometrics ever leave; consent is
  revocable and turning it off stops all future contributions.

The gateway contract is documented in ``docs/cloud-model.md`` and is shared
by QRME, JIM-mini, and PDI (whose encrypted vault serves as the audited
intake where contribution data is stored).
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request


class _Response:
    def __init__(self, status_code: int, body: bytes):
        self.status_code = status_code
        self._body = body

    def json(self):
        return json.loads(self._body) if self._body else None


class _UrllibClient:
    def __init__(self, base_url: str):
        self._base = base_url.rstrip("/")

    def request(self, method, path, json_body=None, headers=None) -> _Response:
        data = json.dumps(json_body).encode() if json_body is not None else None
        h = {"content-type": "application/json"}
        if headers:
            h.update(headers)
        req = urllib.request.Request(
            self._base + path, data=data, method=method, headers=h)
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return _Response(r.status, r.read())
        except urllib.error.HTTPError as e:
            return _Response(e.code, e.read())


class CloudModelClient:
    """HTTP client for the Cloud Model Gateway (see docs/cloud-model.md)."""

    def __init__(self, token: str = "", base_url: str | None = None, client=None):
        self._token = token
        self._client = client
        self._urllib = _UrllibClient(base_url) if base_url else None
        if client is None and base_url is None:
            raise ValueError("CloudModelClient needs base_url or a client")

    def _auth(self):
        return {"Authorization": f"Bearer {self._token}"}

    def _do(self, method, path, body=None):
        if self._client is not None:
            fn = getattr(self._client, method.lower())
            if body is not None:
                return fn(path, json=body, headers=self._auth())
            return fn(path, headers=self._auth())
        return self._urllib.request(method, path, json_body=body,
                                    headers=self._auth())

    def generate(self, system: str, user: str) -> dict:
        r = self._do("POST", "/v1/generate",
                     {"system": system,
                      "messages": [{"role": "user", "content": user}]})
        if r.status_code >= 300:
            raise RuntimeError(f"cloud generate failed: {r.status_code}")
        return r.json()   # {"content": ..., "model": ...}

    def model_info(self) -> dict | None:
        try:
            r = self._do("GET", "/v1/model")
            return r.json() if r.status_code < 300 else None
        except Exception:
            return None

    def contribute(self, payload: dict) -> bool:
        r = self._do("POST", "/v1/contributions", payload)
        return r.status_code < 300


class CloudProvider:
    """Greater-model inference with automatic local fallback."""

    def __init__(self, client: CloudModelClient, fallback):
        self._client = client
        self._fallback = fallback

    def generate(self, system: str, user: str) -> str:
        try:
            return self._client.generate(system, user)["content"].strip()
        except Exception:
            # The gateway being down never breaks the product.
            return self._fallback.generate(system, user)
