"""Module A — Personal Cleaner: import, scan, review, feedback, alerts, export, deletion.

Scans are limited to the signed-in user's own connections; there is no way to
look up an arbitrary third party's lists.
"""
from __future__ import annotations

import csv
import io
from datetime import timedelta
from typing import Optional

from . import security as sec
from .db import DB, dumps, loads
from .models import Connection, Direction, Label, Platform, ScoredAccount
from .scoring import PersonalModel, Scorer

RAW_TTL = timedelta(hours=24)

IMPERSONATION_REPORT = {
    "x": "https://help.x.com/forms/impersonation",
    "facebook": "https://www.facebook.com/help/174210519303259",
    "instagram": "https://help.instagram.com/446663175382270",
    "tiktok": "https://support.tiktok.com/en/safety-hc/report-a-problem/report-an-impersonation-account",
    "linkedin": "https://www.linkedin.com/help/linkedin/answer/a1338436",
}

TABS = ("likely_bot", "suspicious", "low_confidence", "clones", "whitelisted", "removed", "pending", "all")


class NotFound(LookupError):
    pass


class PersonalService:
    def __init__(self, db: DB, stock_hashes: tuple[str, ...] = ()):
        self.db = db
        self.stock_hashes = stock_hashes

    # ---- accounts ---------------------------------------------------------------

    def register(self, email: str, guardian_of: Optional[str] = None, teen_consent: bool = False) -> tuple[str, str]:
        email = email.strip().lower()
        if "@" not in email:
            raise ValueError("A valid email is required")
        if guardian_of and not teen_consent:
            raise ValueError("Scanning a teen's account needs the teen's consent")
        if self.db.one("SELECT 1 FROM users WHERE email=?", (email,)):
            raise ValueError("That email already has an account")
        uid, token = sec.new_id("u_"), sec.new_token()
        self.db.x(
            "INSERT INTO users(id,email,token_hash,created_at,guardian_of,consent_at) VALUES (?,?,?,?,?,?)",
            (uid, email, sec.hash_token(token), sec.iso(), guardian_of, sec.iso() if guardian_of else None),
        )
        return uid, token

    def auth(self, token: str) -> Optional[str]:
        row = self.db.one("SELECT id FROM users WHERE token_hash=?", (sec.hash_token(token),))
        return row["id"] if row else None

    def delete_everything(self, user_id: str) -> None:
        """One-tap data deletion."""
        self.db.x("DELETE FROM users WHERE id=?", (user_id,))

    def model(self, user_id: str) -> PersonalModel:
        row = self.db.one("SELECT model_json FROM users WHERE id=?", (user_id,))
        if not row:
            raise NotFound("user")
        return PersonalModel.from_dict(loads(row["model_json"], {}))

    def _save_model(self, user_id: str, m: PersonalModel) -> None:
        self.db.x("UPDATE users SET model_json=? WHERE id=?", (dumps(m.to_dict()), user_id))

    # ---- import & scan ------------------------------------------------------------

    def store_connections(self, user_id: str, platform: Platform, conns: list[Connection]) -> dict:
        """Replace the user's connection set for ``platform`` and reconcile pending removals."""
        now = sec.iso()
        present = {(c.account_id, c.direction.value) for c in conns}
        # Only the lists in this upload are replaced: people often upload followers and
        # following as separate files.
        directions = sorted({c.direction.value for c in conns})
        marks = ",".join("?" * len(directions))
        reconciled = {"removed": 0, "still_there": 0}
        with self.db.tx() as tx:
            tx.execute(f"DELETE FROM connections WHERE user_id=? AND platform=? AND direction IN ({marks})",
                       (user_id, platform.value, *directions))
            tx.executemany(
                "INSERT OR REPLACE INTO connections VALUES (?,?,?,?,?,?)",
                [(user_id, platform.value, c.account_id, c.direction.value, c.model_dump_json(), now) for c in conns],
            )
            # Re-check: anything we were waiting on that's gone is Removed; still there is Failed.
            for r in tx.execute(
                f"SELECT * FROM flags WHERE user_id=? AND platform=? AND status='pending' AND direction IN ({marks})",
                (user_id, platform.value, *directions),
            ).fetchall():
                gone = (r["account_id"], r["direction"]) not in present
                status = "removed" if gone else "failed"
                reconciled["removed" if gone else "still_there"] += 1
                tx.execute(
                    "UPDATE flags SET status=? WHERE user_id=? AND platform=? AND account_id=? AND direction=?",
                    (status, user_id, platform.value, r["account_id"], r["direction"]),
                )
                self._log(tx, user_id, status, r)
                tx.execute(
                    "UPDATE removal_items SET status=?, updated_at=? WHERE status='pending' AND platform=? AND account_id=?"
                    " AND direction=? AND job_id IN (SELECT id FROM removal_jobs WHERE user_id=?)",
                    (status, now, platform.value, r["account_id"], r["direction"], user_id),
                )
        return reconciled

    def load_connections(self, user_id: str, platform: Optional[str] = None) -> list[Connection]:
        sql, args = "SELECT data_json FROM connections WHERE user_id=?", [user_id]
        if platform:
            sql += " AND platform=?"
            args.append(platform)
        return [Connection.model_validate_json(r["data_json"]) for r in self.db.q(sql, args)]

    def scan(self, user_id: str, platform: Optional[str] = None) -> dict:
        """Score every connection (all platforms, so cross-platform signals work) and save flags."""
        scan_id, started = sec.new_id("s_"), sec.iso()
        m = self.model(user_id)
        conns = self.load_connections(user_id)
        if not conns:
            raise ValueError("Nothing to scan yet: connect X or upload a data export first")
        results = Scorer(model=m, stock_hashes=self.stock_hashes).score(conns)
        if platform:
            results = [r for r in results if r.connection.platform.value == platform]
        prior = {
            (r["platform"], r["account_id"], r["direction"]): r
            for r in self.db.q("SELECT platform,account_id,direction,status,is_clone,label FROM flags WHERE user_id=?", (user_id,))
        }
        counts: dict[str, int] = {}
        new_clones: list[ScoredAccount] = []
        with self.db.tx() as tx:
            for r in results:
                c = r.connection
                k = (c.platform.value, c.account_id, c.direction.value)
                old = prior.get(k)
                status = old["status"] if old and old["status"] in ("whitelisted", "pending", "removed") else "active"
                if old and old["status"] == "removed":
                    status = "active"  # they're back in the list, so it's live again
                if c.key in m.whitelist:
                    status = "whitelisted"
                counts[r.label.value] = counts.get(r.label.value, 0) + 1
                tx.execute(
                    "INSERT OR REPLACE INTO flags VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (user_id, *k, c.handle, c.name, c.profile_url, c.avatar_hash,
                     c.connected_at.isoformat() if c.connected_at else None,
                     r.score, r.label.value, dumps([x.model_dump() for x in r.reasons]),
                     int(r.is_clone), r.clone_of, r.ring_id, status, started),
                )
                newly_flagged = r.label in (Label.likely_bot, Label.suspicious) and (
                    not old or old["label"] not in ("likely_bot", "suspicious"))
                if newly_flagged:
                    self._log(tx, user_id, "flagged", {
                        "platform": k[0], "account_id": k[1], "direction": k[2], "handle": c.handle,
                        "name": c.name, "profile_url": c.profile_url, "score": r.score,
                        "reasons_json": dumps([x.model_dump() for x in r.reasons[:3]]),
                    })
                if r.is_clone and not (old and old["is_clone"]) and status != "whitelisted":
                    new_clones.append(r)
            # Drop flags for accounts no longer in this user's lists (except the history we keep).
            live = {(r.connection.platform.value, r.connection.account_id, r.connection.direction.value) for r in results}
            scanned_platforms = {p for p, _, _ in live} if not platform else {platform}
            for k, old in prior.items():
                if k[0] in scanned_platforms and k not in live and old["status"] not in ("removed", "failed", "pending"):
                    tx.execute("DELETE FROM flags WHERE user_id=? AND platform=? AND account_id=? AND direction=?", (user_id, *k))
            for r in new_clones:
                c = r.connection
                real = self.db.one(
                    "SELECT name, handle FROM flags WHERE user_id=? AND platform=? AND account_id=?",
                    (user_id, c.platform.value, r.clone_of),
                ) if r.clone_of else None
                who = (real["name"] or real["handle"]) if real else "one of your friends"
                tx.execute(
                    "INSERT INTO alerts VALUES (?,?,?,?,?,?,?,?,0)",
                    (sec.new_id("al_"), user_id, sec.iso(), "clone",
                     f"A new account '{c.name or c.handle}' on {c.platform.value} looks like a copy of {who}.",
                     c.platform.value, c.account_id, IMPERSONATION_REPORT[c.platform.value]),
                )
            tx.execute(
                "INSERT INTO scans VALUES (?,?,?,?,?,?)",
                (scan_id, user_id, platform, started, sec.iso(), dumps(counts)),
            )
        return {"scan_id": scan_id, "scanned": len(results), "counts": counts, "new_clone_alerts": len(new_clones)}

    # ---- review --------------------------------------------------------------------

    def dashboard(self, user_id: str) -> dict:
        per: dict[str, dict] = {}
        for r in self.db.q(
            "SELECT platform, direction, COUNT(*) n, SUM(label IN ('likely_bot','suspicious') AND status='active') f,"
            " SUM(status='removed') rm FROM flags WHERE user_id=? GROUP BY platform, direction", (user_id,)
        ):
            p = per.setdefault(r["platform"], {"directions": {}, "flagged": 0, "removed": 0, "last_scan": None})
            p["directions"][r["direction"]] = {"connections": r["n"], "flagged": r["f"] or 0}
            p["flagged"] += r["f"] or 0
            p["removed"] += r["rm"] or 0
        for r in self.db.q("SELECT platform, MAX(imported_at) t FROM connections WHERE user_id=? GROUP BY platform", (user_id,)):
            per.setdefault(r["platform"], {"directions": {}, "flagged": 0, "removed": 0, "last_scan": None})
        last = self.db.one("SELECT finished_at FROM scans WHERE user_id=? ORDER BY finished_at DESC LIMIT 1", (user_id,))
        for p in per:
            s = self.db.one(
                "SELECT MAX(scanned_at) t FROM flags WHERE user_id=? AND platform=?", (user_id, p))
            per[p]["last_scan"] = s["t"] if s else None
        user = self.db.one("SELECT rescan, next_rescan_at FROM users WHERE id=?", (user_id,))
        unread = self.db.one("SELECT COUNT(*) n FROM alerts WHERE user_id=? AND read=0", (user_id,))["n"]
        return {
            "platforms": per, "last_scan": last["finished_at"] if last else None,
            "rescan": user["rescan"], "next_rescan_at": user["next_rescan_at"], "unread_alerts": unread,
        }

    def list_flags(self, user_id: str, platform: Optional[str] = None, direction: Optional[str] = None,
                   tab: str = "likely_bot", sort: str = "score", reason: Optional[str] = None,
                   limit: int = 500, offset: int = 0) -> list[dict]:
        if tab not in TABS:
            raise ValueError(f"tab must be one of {TABS}")
        sql, args = "SELECT * FROM flags WHERE user_id=?", [user_id]
        if platform:
            sql += " AND platform=?"
            args.append(platform)
        if direction:
            sql += " AND direction=?"
            args.append(direction)
        if tab in ("likely_bot", "suspicious", "low_confidence"):
            sql += " AND label=? AND status IN ('active','failed')"
            args.append(tab)
        elif tab == "clones":
            sql += " AND is_clone=1 AND status IN ('active','failed')"
        elif tab in ("whitelisted", "removed", "pending"):
            sql += " AND status=?"
            args.append(tab)
        if reason:
            sql += " AND reasons_json LIKE ?"
            args.append(f'%"code":"{reason}"%')
        order = {"score": "score DESC", "date": "connected_at DESC", "name": "COALESCE(NULLIF(name,''),handle)"}.get(sort, "score DESC")
        sql += f" ORDER BY {order} LIMIT ? OFFSET ?"
        args += [limit, offset]
        return [self._flag_out(r) for r in self.db.q(sql, args)]

    @staticmethod
    def _flag_out(r) -> dict:
        reasons = loads(r["reasons_json"], [])
        return {
            "platform": r["platform"], "account_id": r["account_id"], "direction": r["direction"],
            "handle": r["handle"], "name": r["name"], "profile_url": r["profile_url"],
            "avatar_hash": r["avatar_hash"], "connected_at": r["connected_at"],
            "score": r["score"], "label": r["label"], "reasons": [x["text"] for x in reasons[:3]],
            "reason_codes": [x["code"] for x in reasons], "is_clone": bool(r["is_clone"]),
            "clone_of": r["clone_of"], "ring_id": r["ring_id"], "status": r["status"],
            "preselected": r["label"] == "likely_bot" and r["status"] == "active",
        }

    def get_flag(self, user_id: str, platform: str, account_id: str, direction: str) -> dict:
        r = self.db.one("SELECT * FROM flags WHERE user_id=? AND platform=? AND account_id=? AND direction=?",
                        (user_id, platform, account_id, direction))
        if not r:
            raise NotFound("account")
        return self._flag_out(r)

    # ---- feedback (A8) -----------------------------------------------------------------

    def feedback(self, user_id: str, platform: str, account_id: str, is_bot: bool) -> dict:
        rows = self.db.q("SELECT * FROM flags WHERE user_id=? AND platform=? AND account_id=?", (user_id, platform, account_id))
        if not rows:
            raise NotFound("account")
        m = self.model(user_id)
        key = f"{platform}:{account_id}"
        codes = {x["code"] for r in rows for x in loads(r["reasons_json"], [])} - {"user_confirmed"}
        m.learn(codes, is_bot)
        if is_bot:
            m.whitelist.discard(key)
            m.confirmed_bots.add(key)
        else:
            m.confirmed_bots.discard(key)
            m.whitelist.add(key)
        self._save_model(user_id, m)
        with self.db.tx() as tx:
            for r in rows:
                if is_bot:
                    tx.execute("UPDATE flags SET score=MAX(score,99), label='likely_bot', status=CASE WHEN status='whitelisted'"
                               " THEN 'active' ELSE status END WHERE user_id=? AND platform=? AND account_id=? AND direction=?",
                               (user_id, platform, account_id, r["direction"]))
                else:
                    tx.execute("UPDATE flags SET status='whitelisted' WHERE user_id=? AND platform=? AND account_id=? AND direction=?",
                               (user_id, platform, account_id, r["direction"]))
                self._log(tx, user_id, "confirmed_bot" if is_bot else "whitelisted", r)
        # Retrain: rescore everything still on hand with the updated personal model.
        if self.db.one("SELECT 1 FROM connections WHERE user_id=? LIMIT 1", (user_id,)):
            self.scan(user_id)
        return {"ok": True, "learned_from": sorted(codes)}

    def unwhitelist(self, user_id: str, platform: str, account_id: str) -> None:
        m = self.model(user_id)
        m.whitelist.discard(f"{platform}:{account_id}")
        self._save_model(user_id, m)
        self.db.x("UPDATE flags SET status='active' WHERE user_id=? AND platform=? AND account_id=? AND status='whitelisted'",
                  (user_id, platform, account_id))

    # ---- alerts, schedule, export -----------------------------------------------------

    def alerts(self, user_id: str) -> list[dict]:
        return [dict(r) for r in self.db.q("SELECT * FROM alerts WHERE user_id=? ORDER BY at DESC LIMIT 200", (user_id,))]

    def mark_alerts_read(self, user_id: str) -> None:
        self.db.x("UPDATE alerts SET read=1 WHERE user_id=?", (user_id,))

    def set_rescan(self, user_id: str, cadence: str) -> dict:
        if cadence not in ("off", "weekly", "monthly"):
            raise ValueError("cadence must be off, weekly or monthly")
        nxt = None if cadence == "off" else sec.iso(sec.now() + timedelta(days=7 if cadence == "weekly" else 30))
        self.db.x("UPDATE users SET rescan=?, next_rescan_at=? WHERE id=?", (cadence, nxt, user_id))
        return {"rescan": cadence, "next_rescan_at": nxt}

    def due_rescans(self, at=None) -> list[str]:
        """Users whose scheduled rescan is due. Sends reminders and advances the schedule.

        X accounts are rescanned automatically by the caller (it has the API token);
        export-based platforms get a reminder to upload a fresh export.
        """
        at = at or sec.now()
        due = [r for r in self.db.q("SELECT id, rescan, next_rescan_at FROM users WHERE rescan!='off' AND next_rescan_at<=?",
                                    (sec.iso(at),))]
        for r in due:
            days = 7 if r["rescan"] == "weekly" else 30
            self.db.x("UPDATE users SET next_rescan_at=? WHERE id=?", (sec.iso(at + timedelta(days=days)), r["id"]))
            self.db.x("INSERT INTO alerts VALUES (?,?,?,?,?,?,?,?,0)",
                      (sec.new_id("al_"), r["id"], sec.iso(at), "rescan",
                       "Time for your scheduled rescan. X rescans automatically; upload fresh exports for other platforms.",
                       None, None, None))
        return [r["id"] for r in due]

    def export_csv(self, user_id: str) -> str:
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["date", "event", "platform", "direction", "account_id", "handle", "name", "profile_url", "score", "reasons"])
        for r in self.db.q("SELECT * FROM undo_log WHERE user_id=? ORDER BY id", (user_id,)):
            reasons = "; ".join(x.get("text", "") for x in loads(r["reasons"], []) or [])
            w.writerow([r["at"], r["event"], r["platform"], r["direction"], r["account_id"], r["handle"], r["name"],
                        r["profile_url"], r["score"], reasons])
        return buf.getvalue()

    def undo_log(self, user_id: str, event: Optional[str] = None) -> list[dict]:
        sql, args = "SELECT * FROM undo_log WHERE user_id=?", [user_id]
        if event:
            sql += " AND event=?"
            args.append(event)
        return [dict(r) for r in self.db.q(sql + " ORDER BY id DESC LIMIT 1000", args)]

    def mark_readded(self, user_id: str, platform: str, account_id: str, direction: str) -> None:
        """User re-added someone removed by mistake: whitelist them so they're never flagged again."""
        r = self.db.one("SELECT * FROM flags WHERE user_id=? AND platform=? AND account_id=? AND direction=?",
                        (user_id, platform, account_id, direction))
        if not r:
            raise NotFound("account")
        m = self.model(user_id)
        m.whitelist.add(f"{platform}:{account_id}")
        m.confirmed_bots.discard(f"{platform}:{account_id}")
        m.learn({x["code"] for x in loads(r["reasons_json"], [])}, False)
        self._save_model(user_id, m)
        with self.db.tx() as tx:
            tx.execute("UPDATE flags SET status='whitelisted' WHERE user_id=? AND platform=? AND account_id=? AND direction=?",
                       (user_id, platform, account_id, direction))
            self._log(tx, user_id, "readded", r)

    # ---- retention ----------------------------------------------------------------------

    def purge_raw(self, at=None) -> int:
        """Delete imported connection detail older than 24h; scores and decisions stay."""
        cutoff = sec.iso((at or sec.now()) - RAW_TTL)
        return self.db.x("DELETE FROM connections WHERE imported_at < ?", (cutoff,))

    # ---- helpers ------------------------------------------------------------------------

    @staticmethod
    def _log(tx, user_id: str, event: str, r) -> None:
        g = (lambda k: r[k] if k in r.keys() else None) if hasattr(r, "keys") else r.get
        tx.execute(
            "INSERT INTO undo_log(user_id,at,event,platform,account_id,direction,handle,name,profile_url,score,reasons)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (user_id, sec.iso(), event, g("platform"), g("account_id"), g("direction"), g("handle"), g("name"),
             g("profile_url"), g("score"), g("reasons_json")),
        )
