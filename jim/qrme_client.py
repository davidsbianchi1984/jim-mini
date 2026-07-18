"""QRME tandem adapter.

The *only* connection between JIM-mini and QRME. It speaks QRME's public HTTP
API — it never imports QRME code — so the two remain separate products that
merely interoperate.

A ``client`` may be injected (any object exposing ``post(path, json=...)`` and
``get(path)`` returning a response with ``.status_code`` and ``.json()`` — e.g.
a FastAPI ``TestClient`` or an ``httpx.Client``). When none is given, a small
urllib-based client is used against ``base_url``.
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
        return json.loads(self._body)


class _UrllibClient:
    def __init__(self, base_url: str):
        self._base = base_url.rstrip("/")

    def _request(self, method: str, path: str, body=None) -> _Response:
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(
            self._base + path, data=data, method=method,
            headers={"content-type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req) as r:
                return _Response(r.status, r.read())
        except urllib.error.HTTPError as e:
            return _Response(e.code, e.read())

    def post(self, path, json=None):
        return self._request("POST", path, json)

    def get(self, path):
        return self._request("GET", path)


class QRMEClient:
    def __init__(self, base_url: str | None = None, client=None):
        if client is None:
            if not base_url:
                raise ValueError("QRMEClient needs base_url or an injected client")
            client = _UrllibClient(base_url)
        self._client = client

    def ensure_interactor(self, display_name: str, birthdate: str | None = None) -> str:
        body = {"display_name": display_name}
        if birthdate:
            body["birthdate"] = birthdate
        r = self._client.post("/interactors", json=body)
        if r.status_code >= 300:
            raise RuntimeError(f"QRME interactor create failed: {r.status_code}")
        return r.json()["id"]

    def specialist_reply(self, profile_id: str, interactor_id: str, message: str) -> dict:
        """Send a message to a QRME specialist profile and return its reply.

        The reply has already passed QRME's moderation pipeline; ``content`` is
        ``None`` if QRME held it for owner approval.
        """
        r = self._client.post(
            f"/profiles/{profile_id}/chat",
            json={"interactor_id": interactor_id, "message": message},
        )
        if r.status_code >= 300:
            raise RuntimeError(f"QRME chat failed: {r.status_code}")
        return r.json()["profile_message"]
