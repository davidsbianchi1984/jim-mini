"""Admin-API adapters: read a platform's accounts and apply tier actions there.

Each adapter maps the console's states onto what the platform can actually do.
Every mapping is reversible except "removed", matching the tier table:

    state        Discourse                          Discord (bot in the server)
    challenged   deactivate (email re-activation)   add the verification role, if configured
    restricted   silence (can't post or message)    timeout for 28 days (the maximum)
    suspended    suspend until the appeal deadline  ban (reversible with unban)
    removed      delete the user                    stays banned
    active       undo all of the above              undo all of the above

Credentials are sealed at rest; see ``PurgeService.set_adapter``.
Check each platform's current API docs and rate limits before production use.
"""
from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from typing import Optional

import httpx

from .signals import SiteAccount

DISCORD_EPOCH_MS = 1420070400000


class AdapterError(RuntimeError):
    pass


def _check(r: httpx.Response) -> httpx.Response:
    if r.status_code >= 400:
        raise AdapterError(f"{r.request.method} {r.request.url.path}: {r.status_code} {r.text[:200]}")
    return r


class DiscourseAdapter:
    kind = "discourse"

    def __init__(self, base_url: str, api_key: str, api_username: str = "system", http: Optional[httpx.Client] = None):
        self.base = base_url.rstrip("/")
        self.http = http or httpx.Client(timeout=30)
        self.headers = {"Api-Key": api_key, "Api-Username": api_username, "Accept": "application/json"}

    def _req(self, method: str, path: str, **kw) -> httpx.Response:
        for _ in range(3):
            r = self.http.request(method, self.base + path, headers=self.headers, **kw)
            if r.status_code == 429:
                time.sleep(float(r.headers.get("Retry-After", "2")))
                continue
            return _check(r)
        raise AdapterError("rate limited")

    def fetch_accounts(self, max_pages: int = 10_000) -> list[SiteAccount]:
        out: list[SiteAccount] = []
        for page in range(1, max_pages + 1):
            users = self._req("GET", "/admin/users/list/active.json", params={"show_emails": "true", "page": page}).json()
            if not users:
                break
            for u in users:
                tags = ["staff"] if u.get("admin") or u.get("moderator") else []
                out.append(SiteAccount(
                    account_id=str(u["id"]), username=u.get("username", ""), display_name=u.get("name") or "",
                    email=u.get("email"), created_at=u.get("created_at"),
                    signup_ip=u.get("registration_ip_address"), login_ips=[u["ip_address"]] if u.get("ip_address") else [],
                    email_verified=u.get("active"), tags=tags,
                ))
        return out

    def enforce(self, account_id: str, state: str, notice: Optional[dict] = None) -> None:
        uid = account_id
        reason = (notice or {}).get("what_happened", "Automated account review")
        if notice and notice.get("appeal_url"):
            reason += f" Appeal: {notice['appeal_url']}"
        if state == "challenged":
            self._req("PUT", f"/admin/users/{uid}/deactivate")
        elif state == "restricted":
            until = (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()
            self._req("PUT", f"/admin/users/{uid}/silence", json={"silenced_till": until, "reason": reason})
        elif state == "suspended":
            until = (notice or {}).get("appeal_deadline") or (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
            self._req("PUT", f"/admin/users/{uid}/suspend", json={"suspend_until": until, "reason": reason})
        elif state == "removed":
            self._req("DELETE", f"/admin/users/{uid}.json", json={"delete_posts": False, "block_email": True, "block_ip": False})
        elif state == "active":
            for path in ("unsuspend", "unsilence", "activate"):
                try:
                    self._req("PUT", f"/admin/users/{uid}/{path}")
                except AdapterError:
                    pass  # it wasn't in that state
        else:
            raise AdapterError(f"unknown state {state}")


class DiscordAdapter:
    kind = "discord"
    API = "https://discord.com/api/v10"

    def __init__(self, guild_id: str, bot_token: str, verify_role_id: Optional[str] = None,
                 http: Optional[httpx.Client] = None):
        self.guild = guild_id
        self.http = http or httpx.Client(timeout=30)
        self.headers = {"Authorization": f"Bot {bot_token}"}
        self.verify_role = verify_role_id

    def _req(self, method: str, path: str, reason: str = "", **kw) -> httpx.Response:
        headers = dict(self.headers)
        if reason:
            headers["X-Audit-Log-Reason"] = reason[:512]
        for _ in range(5):
            r = self.http.request(method, self.API + path, headers=headers, **kw)
            if r.status_code == 429:
                time.sleep(float(r.json().get("retry_after", 1)) if r.content else 1)
                continue
            return _check(r)
        raise AdapterError("rate limited")

    @staticmethod
    def created_at(snowflake: str) -> datetime:
        return datetime.fromtimestamp(((int(snowflake) >> 22) + DISCORD_EPOCH_MS) / 1000, tz=timezone.utc)

    def fetch_accounts(self) -> list[SiteAccount]:
        """Needs the Server Members privileged intent enabled for the bot."""
        out: list[SiteAccount] = []
        after = "0"
        while True:
            members = self._req("GET", f"/guilds/{self.guild}/members", params={"limit": 1000, "after": after}).json()
            if not members:
                break
            for m in members:
                u = m["user"]
                out.append(SiteAccount(
                    account_id=u["id"], username=u.get("username", ""), display_name=u.get("global_name") or "",
                    created_at=self.created_at(u["id"]), tags=["integration"] if u.get("bot") else [],
                ))
            after = members[-1]["user"]["id"]
            if len(members) < 1000:
                break
        return out

    def enforce(self, account_id: str, state: str, notice: Optional[dict] = None) -> None:
        g, u = self.guild, account_id
        reason = (notice or {}).get("what_happened", "Automated account review")
        if state == "challenged":
            if self.verify_role:
                self._req("PUT", f"/guilds/{g}/members/{u}/roles/{self.verify_role}", reason)
        elif state == "restricted":
            until = (datetime.now(timezone.utc) + timedelta(days=28) - timedelta(minutes=1)).isoformat()
            self._req("PATCH", f"/guilds/{g}/members/{u}", reason, json={"communication_disabled_until": until})
        elif state == "suspended":
            self._req("PUT", f"/guilds/{g}/bans/{u}", reason, json={"delete_message_seconds": 0})
        elif state == "removed":
            pass  # the ban stays; Discord accounts belong to Discord, so "removal" is permanent exclusion
        elif state == "active":
            for method, path, body in (("DELETE", f"/guilds/{g}/bans/{u}", None),
                                       ("PATCH", f"/guilds/{g}/members/{u}", {"communication_disabled_until": None}),
                                       ("DELETE", f"/guilds/{g}/members/{u}/roles/{self.verify_role}", None)):
                if "roles/None" in path:
                    continue
                try:
                    self._req(method, path, "Restored after review", **({"json": body} if body is not None else {}))
                except AdapterError:
                    pass  # not banned / not a member any more / no role
        else:
            raise AdapterError(f"unknown state {state}")


def build(kind: str, settings: dict, secret: str, http: Optional[httpx.Client] = None):
    if kind == "discourse":
        if not settings.get("base_url"):
            raise ValueError("Discourse needs base_url")
        return DiscourseAdapter(settings["base_url"], secret, settings.get("api_username") or "system", http=http)
    if kind == "discord":
        if not settings.get("guild_id"):
            raise ValueError("Discord needs guild_id")
        return DiscordAdapter(settings["guild_id"], secret, settings.get("verify_role_id"), http=http)
    raise ValueError(f"unknown adapter {kind}; supported: discourse, discord")
