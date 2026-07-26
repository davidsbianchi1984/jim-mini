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

    # -- referrals: reaching a real clinician --------------------------------

    def match_clinicians(self, area: str, location: str | None = None,
                         limit: int = 5) -> list[dict]:
        """Real providers QRME knows about, by expertise and locality.

        An unreachable QRME is an empty list, not an exception: the caller is
        often a screen somebody opened while unwell, and "none found" degrades
        better than a traceback.
        """
        path = f"/referrals/match?area={urllib.parse.quote(area)}&limit={limit}"
        if location:
            path += f"&location={urllib.parse.quote(location)}"
        try:
            r = self._client.get(path)
        except Exception:
            return []
        return r.json() if r.status_code < 300 else []

    def prepare_referral(self, profile_id: str, interactor_id: str,
                         token: str | None, provider_id: str) -> dict | None:
        """Ask QRME to assemble the summary and mint the signature envelope.

        Releases nothing. The returned challenge is signed **against QRME**
        by the user's own device — JIM never relays the assertion, because a
        guardian product standing in the middle of the exchange that proves
        its user was present would defeat the point of collecting it.
        """
        if not token:
            return None
        try:
            r = self._client.post("/referrals/prepare", json={
                "interactor_id": interactor_id, "profile_id": profile_id,
                "provider_id": provider_id},
                headers={"authorization": f"Bearer {token}"})
        except Exception:
            return None
        return r.json() if r.status_code < 300 else None

    # -- delegated workflows: handing over a task, not a turn ----------------
    #
    # `specialist_reply` sends one message and gets one reply back, which is
    # the right shape for "say something supportive" and the wrong one for
    # work that takes several steps and has to survive the user closing the
    # app. QRME runs those as *workflows*, and its own workflow routes are
    # owner-only for good reason — a workflow reads the profile's vaulted
    # source material unattended. The delegated surface below is the one an
    # interactor may reach, inside an envelope the profile's owner declared.

    def delegation_offer(self, profile_id: str) -> dict:
        """What this profile permits a delegated caller to run.

        Asked *before* attempting a handoff, so a specialist that has not been
        opted in produces a clean fallback rather than a 403 in the middle of
        somebody's emergency. Unreachable QRME reads as "no delegation", which
        is the safe direction: JIM handles it standalone.
        """
        try:
            r = self._client.get(f"/profiles/{profile_id}/delegation")
        except Exception:
            return {"delegation": False, "phases": []}
        if r.status_code >= 300:
            return {"delegation": False, "phases": []}
        return r.json()

    def start_workflow(self, profile_id: str, interactor_id: str,
                       token: str | None, goal: str,
                       plan: list[str] | None = None) -> dict | None:
        """Ask a specialist to take on a multi-step task. None if refused.

        Needs the interactor's own capability token — the same one that reads
        the shared thread. Without it the caller is a stranger holding an id,
        which QRME declines by design.
        """
        if not token:
            return None
        body = {"goal": goal, "interactor_id": interactor_id}
        if plan is not None:
            body["plan"] = plan
        try:
            r = self._client.post(
                f"/profiles/{profile_id}/delegated-workflows", json=body,
                headers={"authorization": f"Bearer {token}"})
        except Exception:
            return None
        return r.json() if r.status_code < 300 else None

    def advance_workflow(self, profile_id: str, workflow_id: str,
                         token: str | None) -> dict | None:
        """Run the specialist's next phase. None if it could not be advanced."""
        if not token:
            return None
        try:
            r = self._client.post(
                f"/profiles/{profile_id}/delegated-workflows/{workflow_id}"
                "/advance", json={},
                headers={"authorization": f"Bearer {token}"})
        except Exception:
            return None
        return r.json() if r.status_code < 300 else None

    def workflow_status(self, profile_id: str, workflow_id: str,
                        token: str | None) -> dict | None:
        """Where a handed-off task has got to. None if unreadable."""
        if not token:
            return None
        try:
            r = self._client.get(
                f"/profiles/{profile_id}/delegated-workflows/{workflow_id}",
                headers={"authorization": f"Bearer {token}"})
        except Exception:
            return None
        return r.json() if r.status_code < 300 else None

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
