"""X (Twitter) API v2 connector: the one platform with official one-click removal.

* Reading: ``GET /2/users/:id/followers`` and ``/following`` with profile fields.
* Unfollow: ``DELETE /2/users/:id/following/:target_user_id``.
* Remove follower: X has no "remove follower" endpoint, so we block then
  immediately unblock (``POST /2/users/:id/blocking`` then
  ``DELETE /2/users/:id/blocking/:target``). Some API tiers no longer allow
  write access to blocking; when X refuses, the removal falls back to
  Assisted mode instead of failing silently.

Auth is OAuth 2.0 with PKCE; we never see the user's password. Scopes needed:
``tweet.read users.read follows.read follows.write block.read block.write offline.access``.
Verify the current API tier's terms and limits before enabling in production.
"""
from __future__ import annotations

import base64
import hashlib
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Iterator, Optional
from urllib.parse import urlencode

import httpx

from ..models import Connection, Direction, Platform

API = "https://api.x.com/2"
AUTHORIZE = "https://x.com/i/oauth2/authorize"
TOKEN = "https://api.x.com/2/oauth2/token"
SCOPES = "tweet.read users.read follows.read follows.write block.read block.write offline.access"
USER_FIELDS = "created_at,description,profile_image_url,public_metrics,verified,username,name"


class XError(RuntimeError):
    def __init__(self, status: int, message: str):
        super().__init__(f"X API {status}: {message}")
        self.status = status


class NotPermitted(XError):
    """The API tier does not allow this action; caller should fall back to Assisted mode."""


@dataclass
class PKCE:
    verifier: str
    challenge: str
    state: str

    @classmethod
    def new(cls) -> "PKCE":
        verifier = secrets.token_urlsafe(64)[:96]
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
        return cls(verifier, challenge, secrets.token_urlsafe(24))


def authorize_url(client_id: str, redirect_uri: str, pkce: PKCE) -> str:
    return AUTHORIZE + "?" + urlencode({
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": SCOPES,
        "state": pkce.state,
        "code_challenge": pkce.challenge,
        "code_challenge_method": "S256",
    })


@dataclass
class RateLimiter:
    """Client-side pacing: at most ``per_window`` calls per ``window`` seconds per endpoint.

    Also honours X's ``x-rate-limit-reset`` header when a 429 comes back.
    """

    per_window: int = 15
    window: float = 900.0
    sleep: Callable[[float], None] = time.sleep
    clock: Callable[[], float] = time.monotonic
    _calls: dict[str, list[float]] = field(default_factory=dict)

    def wait(self, endpoint: str) -> None:
        now = self.clock()
        calls = [t for t in self._calls.get(endpoint, []) if now - t < self.window]
        if len(calls) >= self.per_window:
            self.sleep(self.window - (now - calls[0]))
            now = self.clock()
            calls = [t for t in calls if now - t < self.window]
        calls.append(now)
        self._calls[endpoint] = calls


class XClient:
    def __init__(
        self,
        access_token: str,
        http: Optional[httpx.Client] = None,
        limiter: Optional[RateLimiter] = None,
        max_retries: int = 2,
    ):
        self.http = http or httpx.Client(timeout=30)
        self.headers = {"Authorization": f"Bearer {access_token}"}
        self.limiter = limiter or RateLimiter()
        self.max_retries = max_retries

    # ---- OAuth -------------------------------------------------------------------

    @staticmethod
    def exchange_code(client_id: str, code: str, redirect_uri: str, verifier: str,
                      http: Optional[httpx.Client] = None) -> dict:
        http = http or httpx.Client(timeout=30)
        r = http.post(TOKEN, data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri,
            "code_verifier": verifier, "client_id": client_id,
        })
        if r.status_code != 200:
            raise XError(r.status_code, r.text)
        return r.json()

    # ---- plumbing ------------------------------------------------------------------

    def _req(self, method: str, path: str, endpoint: str, **kw) -> dict:
        for attempt in range(self.max_retries + 1):
            self.limiter.wait(endpoint)
            r = self.http.request(method, API + path, headers=self.headers, **kw)
            if r.status_code == 429 and attempt < self.max_retries:
                reset = float(r.headers.get("x-rate-limit-reset", "0") or 0)
                self.limiter.sleep(max(1.0, reset - time.time()) if reset else 60.0)
                continue
            if r.status_code in (401, 403) and endpoint.startswith("blocking"):
                raise NotPermitted(r.status_code, r.text)
            if r.status_code >= 400:
                raise XError(r.status_code, r.text)
            return r.json() if r.content else {}
        raise XError(429, "rate limited")

    def me(self) -> dict:
        return self._req("GET", "/users/me", "me", params={"user.fields": USER_FIELDS})["data"]

    # ---- reading ---------------------------------------------------------------------

    def _pages(self, user_id: str, kind: str) -> Iterator[dict]:
        token = None
        while True:
            params = {"max_results": 1000, "user.fields": USER_FIELDS}
            if token:
                params["pagination_token"] = token
            body = self._req("GET", f"/users/{user_id}/{kind}", kind, params=params)
            yield from body.get("data", []) or []
            token = (body.get("meta") or {}).get("next_token")
            if not token:
                return

    def connections(self, user_id: str) -> list[Connection]:
        out: list[Connection] = []
        for kind, direction in (("followers", Direction.follower), ("following", Direction.following)):
            for u in self._pages(user_id, kind):
                out.append(to_connection(u, direction))
        return out

    # ---- removal ---------------------------------------------------------------------

    def unfollow(self, user_id: str, target_id: str) -> bool:
        body = self._req("DELETE", f"/users/{user_id}/following/{target_id}", "unfollow")
        return not (body.get("data") or {}).get("following", False)

    def remove_follower(self, user_id: str, target_id: str) -> bool:
        """Soft-block: block then unblock, which removes them from your followers."""
        self._req("POST", f"/users/{user_id}/blocking", "blocking_add", json={"target_user_id": target_id})
        self._req("DELETE", f"/users/{user_id}/blocking/{target_id}", "blocking_remove")
        return True

    def still_connected(self, user_id: str, target_id: str, direction: Direction) -> bool:
        """Re-check after removal (step 6 of the flow)."""
        kind = "followers" if direction == Direction.follower else "following"
        return any(u.get("id") == target_id for u in self._pages(user_id, kind))


def to_connection(u: dict, direction: Direction) -> Connection:
    pm = u.get("public_metrics") or {}
    img = u.get("profile_image_url") or ""
    created = u.get("created_at")
    return Connection(
        platform=Platform.x,
        account_id=str(u["id"]),
        handle=u.get("username", ""),
        name=u.get("name", ""),
        direction=direction,
        profile_url=f"https://x.com/{u.get('username', '')}",
        created_at=datetime.fromisoformat(created.replace("Z", "+00:00")) if created else None,
        followers_count=pm.get("followers_count"),
        following_count=pm.get("following_count"),
        bio=u.get("description"),
        has_default_avatar=("default_profile_images" in img) if img else None,
        verified=u.get("verified"),
    )
