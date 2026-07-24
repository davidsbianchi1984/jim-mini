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
import urllib.parse
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

    def _request(self, method: str, path: str, body=None,
                 headers=None) -> _Response:
        data = json.dumps(body).encode() if body is not None else None
        h = {"content-type": "application/json"}
        if headers:
            h.update(headers)
        req = urllib.request.Request(
            self._base + path, data=data, method=method, headers=h,
        )
        try:
            with urllib.request.urlopen(req) as r:
                return _Response(r.status, r.read())
        except urllib.error.HTTPError as e:
            return _Response(e.code, e.read())

    def post(self, path, json=None, headers=None):
        return self._request("POST", path, json, headers)

    def get(self, path, headers=None):
        return self._request("GET", path, headers=headers)


class QRMEClient:
    def __init__(self, base_url: str | None = None, client=None):
        if client is None:
            if not base_url:
                raise ValueError("QRMEClient needs base_url or an injected client")
            client = _UrllibClient(base_url)
        self._client = client

    def ensure_interactor(self, display_name: str,
                          birthdate: str | None = None) -> tuple[str, str | None]:
        """Create a QRME interactor; returns (id, capability token). The token
        is what lets JIM read the shared thread back later (continuity)."""
        body = {"display_name": display_name}
        if birthdate:
            body["birthdate"] = birthdate
        r = self._client.post("/interactors", json=body)
        if r.status_code >= 300:
            raise RuntimeError(f"QRME interactor create failed: {r.status_code}")
        out = r.json()
        return out["id"], out.get("token")

    def thread_memory(self, profile_id: str, interactor_id: str,
                      token: str | None, limit: int = 5) -> list[dict] | None:
        """The shared conversation thread with a QRME profile, read back with
        the interactor's own capability token. None when unreadable."""
        if not token:
            return None
        try:
            r = self._client.get(
                f"/profiles/{profile_id}/memory/{interactor_id}",
                headers={"authorization": f"Bearer {token}"})
        except Exception:
            return None
        if r.status_code >= 300:
            return None
        return r.json()[-limit:]

    def resolve_handle(self, handle: str) -> dict | None:
        """Resolve a QRME @handle to its public profile card via summoning.
        None when the handle doesn't resolve or QRME is unreachable — ids
        are deployment-specific, so handles are the stable cross-product
        names."""
        ref = handle if handle.startswith("@") else "@" + handle
        try:
            r = self._client.get("/summon?ref=" + urllib.parse.quote(ref))
        except Exception:
            return None
        if r.status_code >= 300:
            return None
        out = r.json()
        return out.get("profile") if out.get("type") == "handle" else None

    def profile_info(self, profile_id: str) -> dict | None:
        """Fetch a QRME profile's public card (includes ``adult_mode`` and
        ``status``). Returns None if it can't be read — the caller then relies
        on QRME's own age-gate as the backstop."""
        try:
            r = self._client.get(f"/profiles/{profile_id}")
        except Exception:
            return None
        if r.status_code >= 300:
            return None
        return r.json()

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
