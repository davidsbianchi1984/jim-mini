"""HTTP client for the tandem PDI (Private Data Infrastructure) vault.

When configured, JIM stores its most sensitive payloads — medical/biometric
samples, detection details, check-in notes, and context-event data — in PDI's
encrypted vault instead of its own database, keeping only key references
locally. JIM never imports PDI internals; the boundary is HTTP.

Accepts an injected ``client`` (FastAPI ``TestClient`` / ``httpx.Client``) or
a ``base_url`` + tenant token for a real deployment.
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
            with urllib.request.urlopen(req) as r:
                return _Response(r.status, r.read())
        except urllib.error.HTTPError as e:
            return _Response(e.code, e.read())


class PDIClient:
    def __init__(self, token: str, base_url: str | None = None, client=None):
        self._token = token
        self._client = client
        self._urllib = _UrllibClient(base_url) if base_url else None
        if client is None and base_url is None:
            raise ValueError("PDIClient needs base_url or an injected client")

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

    def put(self, key: str, value: str) -> None:
        r = self._do("PUT", "/records", {"key": key, "value": value})
        if r.status_code >= 300:
            raise RuntimeError(f"PDI put failed: {r.status_code}")

    def get(self, key: str) -> str | None:
        r = self._do("GET", f"/records/{key}")
        if r.status_code == 404:
            return None
        if r.status_code >= 300:
            raise RuntimeError(f"PDI get failed: {r.status_code}")
        return r.json()["value"]

    def delete(self, key: str) -> bool:
        r = self._do("DELETE", f"/records/{key}")
        return r.status_code == 204
