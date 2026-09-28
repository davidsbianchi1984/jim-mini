"""Removal orchestrator: one queue, three modes.

* one_click (X only): official API calls after the user confirms the batch,
  paced below X's write limits. If X refuses an action (API tier), the item
  drops to Assisted mode instead of failing.
* assisted: the browser extension (or the web app) opens each flagged profile
  in the user's own logged-in browser, one at a time at a human pace. The USER
  clicks Remove/Unfollow; nothing is ever auto-clicked.
* guided: the full list with platform- and device-specific steps; the user
  ticks each one off.

Assisted and guided items end in ``pending`` until the next import re-checks
them (then Removed or Failed). One-click items are verified by the API.
"""
from __future__ import annotations

from datetime import timedelta
from typing import Callable, Optional

from . import security as sec
from .db import DB
from .instructions import PLATFORM_ACTIONS
from .personal import NotFound, PersonalService

ACTION_FOR = {"friend": "unfriend", "follower": "remove_follower", "following": "unfollow"}

# Seconds between items. X: unfollow is limited to ~50 per 15 minutes per user.
PACE = {"one_click": 20.0, "assisted": 25.0, "guided": 0.0}
MAX_BATCH = {"one_click": 400, "assisted": 200, "guided": 500}


def modes_for(platform: str) -> list[str]:
    return ["one_click", "assisted", "guided"] if platform == "x" else ["assisted", "guided"]


class RemovalService:
    def __init__(self, db: DB, personal: PersonalService,
                 x_client_for: Optional[Callable[[str], tuple[object, str]]] = None):
        """``x_client_for(user_id)`` returns ``(XClient, x_user_id)`` for one-click removal."""
        self.db = db
        self.personal = personal
        self.x_client_for = x_client_for

    def create_job(self, user_id: str, platform: str, accounts: list[dict], mode: Optional[str] = None) -> dict:
        """``accounts``: [{account_id, direction}] the user selected and confirmed."""
        mode = mode or modes_for(platform)[0]
        if mode not in modes_for(platform):
            raise ValueError(f"{mode} is not available for {platform}; use one of {modes_for(platform)}")
        if not accounts:
            raise ValueError("Select at least one account")
        if len(accounts) > MAX_BATCH[mode]:
            raise ValueError(f"At most {MAX_BATCH[mode]} accounts per {mode} batch")
        items = []
        for a in accounts:
            f = self.db.one("SELECT status FROM flags WHERE user_id=? AND platform=? AND account_id=? AND direction=?",
                            (user_id, platform, a["account_id"], a["direction"]))
            if not f:
                raise NotFound(f"{a['account_id']} is not in your {platform} lists")
            if f["status"] == "whitelisted":
                raise ValueError(f"{a['account_id']} is whitelisted as a real person; remove it from the whitelist first")
            action = ACTION_FOR[a["direction"]]
            if action not in PLATFORM_ACTIONS[platform]:
                raise ValueError(f"{platform} doesn't support {action}")
            items.append((a["account_id"], a["direction"], action))
        job_id = sec.new_id("j_")
        now = sec.iso()
        with self.db.tx() as tx:
            tx.execute("INSERT INTO removal_jobs(id,user_id,platform,mode,state,created_at,pace_seconds,next_at) VALUES (?,?,?,?,?,?,?,?)",
                       (job_id, user_id, platform, mode, "running", now, PACE[mode], now))
            for i, (aid, direction, action) in enumerate(items):
                tx.execute("INSERT INTO removal_items(job_id,idx,platform,account_id,direction,action,mode,updated_at)"
                           " VALUES (?,?,?,?,?,?,?,?)", (job_id, i, platform, aid, direction, action, mode, now))
                tx.execute("UPDATE flags SET status='pending' WHERE user_id=? AND platform=? AND account_id=? AND direction=?",
                           (user_id, platform, aid, direction))
        return self.job(user_id, job_id)

    def job(self, user_id: str, job_id: str) -> dict:
        j = self.db.one("SELECT * FROM removal_jobs WHERE id=? AND user_id=?", (job_id, user_id))
        if not j:
            raise NotFound("job")
        items = [dict(r) for r in self.db.q(
            "SELECT i.*, f.handle, f.name, f.profile_url, f.score FROM removal_items i LEFT JOIN flags f"
            " ON f.user_id=? AND f.platform=i.platform AND f.account_id=i.account_id AND f.direction=i.direction"
            " WHERE i.job_id=? ORDER BY idx", (user_id, job_id))]
        counts: dict[str, int] = {}
        for it in items:
            counts[it["status"]] = counts.get(it["status"], 0) + 1
        return {**dict(j), "items": items, "counts": counts, "total": len(items)}

    def jobs(self, user_id: str) -> list[dict]:
        return [dict(r) for r in self.db.q("SELECT * FROM removal_jobs WHERE user_id=? ORDER BY created_at DESC", (user_id,))]

    def set_state(self, user_id: str, job_id: str, state: str) -> dict:
        if state not in ("running", "paused", "cancelled"):
            raise ValueError("state must be running, paused or cancelled")
        j = self.job(user_id, job_id)
        if j["state"] in ("done", "cancelled"):
            raise ValueError(f"job is already {j['state']}")
        with self.db.tx() as tx:
            tx.execute("UPDATE removal_jobs SET state=?, next_at=?, finished_at=CASE WHEN ?='cancelled' THEN ? ELSE finished_at END"
                       " WHERE id=?", (state, sec.iso(), state, sec.iso(), job_id))
            if state == "cancelled":
                for it in j["items"]:
                    if it["status"] in ("queued", "opened"):
                        tx.execute("UPDATE removal_items SET status='skipped', updated_at=? WHERE job_id=? AND idx=?",
                                   (sec.iso(), job_id, it["idx"]))
                        tx.execute("UPDATE flags SET status='active' WHERE user_id=? AND platform=? AND account_id=? AND direction=?",
                                   (user_id, it["platform"], it["account_id"], it["direction"]))
        return self.job(user_id, job_id)

    # ---- one-click (X) -----------------------------------------------------------

    def run_one_click(self, user_id: str, job_id: str, max_items: int = 50, sleep: Callable[[float], None] = lambda s: None) -> dict:
        """Process due one-click items. Called by the worker loop; ``sleep`` paces between calls."""
        j = self.job(user_id, job_id)
        if j["mode"] != "one_click" or j["state"] != "running":
            return j
        if not self.x_client_for:
            raise RuntimeError("X is not connected")
        client, me = self.x_client_for(user_id)
        from .connectors.x import NotPermitted, XError

        done = 0
        for it in j["items"]:
            if done >= max_items:
                break
            if it["status"] != "queued" or it["mode"] != "one_click":
                continue
            state = self.db.one("SELECT state FROM removal_jobs WHERE id=?", (job_id,))["state"]
            if state != "running":
                break
            if done:
                sleep(j["pace_seconds"])
            status, error, mode = "removed", None, "one_click"
            try:
                if it["action"] == "unfollow":
                    ok = client.unfollow(me, it["account_id"])
                else:
                    ok = client.remove_follower(me, it["account_id"])
                status = "removed" if ok else "failed"
            except NotPermitted:
                status, mode, error = "queued", "assisted", "X API tier does not allow this; switched to Assisted"
            except XError as exc:
                status, error = "failed", str(exc)[:300]
            self._finish_item(user_id, job_id, it, status, error, mode)
            done += 1
        self._maybe_done(job_id)
        return self.job(user_id, job_id)

    def recheck_x(self, user_id: str, job_id: str) -> dict:
        """After a one-click job, fetch lists once and mark anything still connected as Failed."""
        j = self.job(user_id, job_id)
        client, me = self.x_client_for(user_id)
        from .models import Direction

        for direction in ("follower", "following"):
            removed = [it for it in j["items"] if it["status"] == "removed" and it["direction"] == direction]
            if not removed:
                continue
            present = {c.account_id for c in client.connections(me) if c.direction == Direction(direction)}
            for it in removed:
                if it["account_id"] in present:
                    self._finish_item(user_id, job_id, it, "failed", "Still connected on re-check", it["mode"])
        return self.job(user_id, job_id)

    # ---- assisted / guided -------------------------------------------------------------

    def next_assisted(self, user_id: str, job_id: str, device: str = "web") -> dict:
        """The next profile for the extension/web app to open. Enforces human pacing."""
        j = self.job(user_id, job_id)
        if j["state"] != "running":
            return {"state": j["state"], "item": None}
        now = sec.now()
        nxt = sec.parse_iso(j["next_at"])
        if nxt and now < nxt:
            return {"state": "waiting", "wait_seconds": round((nxt - now).total_seconds(), 1), "item": None}
        it = next((i for i in j["items"] if i["status"] == "queued" and i["mode"] in ("assisted", "one_click")), None)
        if it is None:
            it = next((i for i in j["items"] if i["status"] == "opened"), None)
            return {"state": "awaiting_confirmation" if it else "empty", "item": it}
        self.db.x("UPDATE removal_items SET status='opened', mode='assisted', attempts=attempts+1, updated_at=? WHERE job_id=? AND idx=?",
                  (sec.iso(), job_id, it["idx"]))
        self.db.x("UPDATE removal_jobs SET next_at=? WHERE id=?",
                  (sec.iso(now + timedelta(seconds=PACE["assisted"])), job_id))
        return {"state": "open", "item": {**it, "status": "opened"},
                "steps": self._steps(it["platform"], device, it["action"]),
                "note": "Click Remove/Unfollow yourself on the page that just opened, then confirm here."}

    def confirm(self, user_id: str, job_id: str, idx: int, outcome: str) -> dict:
        """User reports what happened: done | skipped | failed."""
        if outcome not in ("done", "skipped", "failed"):
            raise ValueError("outcome must be done, skipped or failed")
        j = self.job(user_id, job_id)
        it = next((i for i in j["items"] if i["idx"] == idx), None)
        if not it:
            raise NotFound("item")
        if it["status"] not in ("queued", "opened", "failed"):
            raise ValueError(f"item is already {it['status']}")
        status = {"done": "pending", "skipped": "skipped", "failed": "failed"}[outcome]
        self._finish_item(user_id, job_id, it, status, None, it["mode"] if it["mode"] != "one_click" else "assisted")
        self._maybe_done(job_id)
        return self.job(user_id, job_id)

    def guided(self, user_id: str, job_id: str, device: str = "web") -> dict:
        j = self.job(user_id, job_id)
        steps = {a: self._steps(j["platform"], device, a) for a in {i["action"] for i in j["items"]}}
        return {**j, "steps": steps, "device": device}

    def _steps(self, platform: str, device: str, action: str) -> dict:
        from .instructions_store import InstructionStore

        return InstructionStore(self.db).best(platform, device, action)

    # ---- internals ------------------------------------------------------------------------

    def _finish_item(self, user_id: str, job_id: str, it: dict, status: str, error: Optional[str], mode: str) -> None:
        flag_status = {"removed": "removed", "failed": "failed", "pending": "pending", "skipped": "active", "queued": "pending"}[status]
        with self.db.tx() as tx:
            tx.execute("UPDATE removal_items SET status=?, error=?, mode=?, updated_at=? WHERE job_id=? AND idx=?",
                       (status, error, mode, sec.iso(), job_id, it["idx"]))
            tx.execute("UPDATE flags SET status=? WHERE user_id=? AND platform=? AND account_id=? AND direction=?",
                       (flag_status, user_id, it["platform"], it["account_id"], it["direction"]))
            if status in ("removed", "failed"):
                f = tx.execute("SELECT * FROM flags WHERE user_id=? AND platform=? AND account_id=? AND direction=?",
                               (user_id, it["platform"], it["account_id"], it["direction"])).fetchone()
                if f:
                    PersonalService._log(tx, user_id, status, f)

    def _maybe_done(self, job_id: str) -> None:
        left = self.db.one("SELECT COUNT(*) n FROM removal_items WHERE job_id=? AND status IN ('queued','opened')", (job_id,))["n"]
        if left == 0:
            self.db.x("UPDATE removal_jobs SET state='done', finished_at=? WHERE id=? AND state='running'", (sec.iso(), job_id))

