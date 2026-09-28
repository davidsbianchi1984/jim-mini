"""Module B — Platform Purge Console.

Flow: connect (ingest accounts) -> configure -> scan -> review/spot-check ->
dry run -> execute in batches (pause / rollback) -> notices -> appeals ->
permanent removal only after the appeal window AND a human reviewer's sign-off.

Every state change, decision and configuration change is written to the
tenant's hash-chained, append-only audit log.
"""
from __future__ import annotations

import csv
import hashlib
import hmac
import io
import json
import random
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Callable, Optional

from pydantic import BaseModel, Field, field_validator

from .. import security as sec
from ..db import DB, dumps, loads
from .signals import WEIGHTS as SITE_WEIGHTS
from .signals import SiteAccount, SiteScorer

TIER_STATE = {1: "challenged", 2: "restricted", 3: "suspended", 4: "removed"}
STATE_RANK = {"active": 0, "challenged": 1, "restricted": 2, "suspended": 3, "removed": 4}
ACTION_TEXT = {
    1: "We need you to confirm you're a person (CAPTCHA or email/phone check) before you continue.",
    2: "Posting, messaging and following are paused on your account until you verify it.",
    3: "Your account has been suspended because our systems believe it is automated or fake.",
    4: "Your account has been permanently removed.",
}


class Rule(BaseModel):
    """Owner rule layered on the model (B7). First matching rule wins."""

    id: str = Field(default_factory=lambda: sec.new_id("r_"))
    name: str
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    reasons_any: list[str] = Field(default_factory=list)
    reasons_all: list[str] = Field(default_factory=list)
    in_ring: Optional[bool] = None
    signup_after: Optional[datetime] = None
    signup_before: Optional[datetime] = None
    tags_any: list[str] = Field(default_factory=list)
    tier: Optional[int] = None      # 1-3 (tier 4 is only ever reached through the appeal window)
    exempt: bool = False

    @field_validator("tier")
    @classmethod
    def _tier(cls, v):
        if v is not None and v not in (0, 1, 2, 3):
            raise ValueError("rules can set tier 0-3; permanent removal needs the appeal window and a reviewer")
        return v

    @field_validator("reasons_any", "reasons_all")
    @classmethod
    def _codes(cls, v):
        bad = [c for c in v if c not in SITE_WEIGHTS]
        if bad:
            raise ValueError(f"unknown reason codes: {bad}")
        return v

    def matches(self, acc: dict) -> bool:
        s, codes = acc["score"] or 0, set(acc["reason_codes"])
        if self.min_score is not None and s < self.min_score:
            return False
        if self.max_score is not None and s > self.max_score:
            return False
        if self.reasons_any and not codes & set(self.reasons_any):
            return False
        if self.reasons_all and not set(self.reasons_all) <= codes:
            return False
        if self.in_ring is not None and bool(acc["ring_id"]) != self.in_ring:
            return False
        created = sec.parse_iso(acc.get("created_at"))
        if self.signup_after and (not created or created < _aware(self.signup_after)):
            return False
        if self.signup_before and (not created or created > _aware(self.signup_before)):
            return False
        if self.tags_any and not set(acc.get("tags", [])) & set(self.tags_any):
            return False
        return True


def _aware(d: datetime) -> datetime:
    from datetime import timezone

    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


class TenantConfig(BaseModel):
    tier1_min: float = 60
    tier2_min: float = 80
    tier3_min: float = 95
    ring_tier3_min_size: int = 3
    ring_tier3_min_mean: float = 80
    allowed_tiers: list[int] = Field(default_factory=lambda: [1, 2, 3, 4])
    appeal_window_days: int = 30
    review_sla_days: int = 7
    exempt_tags: list[str] = Field(default_factory=lambda: ["staff", "partner", "integration"])
    exempt_ids: list[str] = Field(default_factory=list)
    batch_size: int = 500
    appeal_base_url: str = "/appeal"
    enforcement_webhook: Optional[str] = None
    extra_disposable_domains: list[str] = Field(default_factory=list)
    extra_datacenter_asns: list[str] = Field(default_factory=list)

    @field_validator("tier3_min")
    @classmethod
    def _order(cls, v, info):
        d = info.data
        if not (d.get("tier1_min", 0) < d.get("tier2_min", 0) < v <= 100):
            raise ValueError("thresholds must satisfy tier1 < tier2 < tier3 <= 100")
        return v

    @field_validator("appeal_window_days")
    @classmethod
    def _window(cls, v):
        if v < 7:
            raise ValueError("the appeal window must be at least 7 days")
        return v


class Forbidden(PermissionError):
    pass


class PurgeService:
    def __init__(self, db: DB, enforcer: Optional[Callable[[str, dict], None]] = None,
                 clock: Callable[[], datetime] = sec.now, http=None):
        self.db = db
        self.enforcer = enforcer
        self.clock = clock
        self.http = http  # injected httpx client for adapters (tests)

    # ---- admin-API adapters (Discord, Discourse) -------------------------------------

    def set_adapter(self, tid: str, kind: str, settings: dict, secret: str) -> dict:
        from . import adapters

        adapters.build(kind, settings, secret)  # validates settings
        self.db.x("INSERT OR REPLACE INTO t_adapters VALUES (?,?,?,?)",
                  (tid, kind, dumps(settings), sec.seal(secret, f"{tid}:adapter")))
        self.audit(tid, "owner", "adapter.connected", {"kind": kind, "settings": settings})
        return {"kind": kind, "settings": settings}

    def adapter_info(self, tid: str) -> Optional[dict]:
        r = self.db.one("SELECT kind, settings_json FROM t_adapters WHERE tenant_id=?", (tid,))
        return {"kind": r["kind"], "settings": loads(r["settings_json"], {})} if r else None

    def remove_adapter(self, tid: str) -> None:
        self.db.x("DELETE FROM t_adapters WHERE tenant_id=?", (tid,))
        self.audit(tid, "owner", "adapter.disconnected", {})

    def adapter_for(self, tid: str):
        from . import adapters

        r = self.db.one("SELECT * FROM t_adapters WHERE tenant_id=?", (tid,))
        if not r:
            return None
        return adapters.build(r["kind"], loads(r["settings_json"], {}), sec.unseal(r["sealed"], f"{tid}:adapter"), http=self.http)

    def sync_adapter(self, tid: str) -> dict:
        a = self.adapter_for(tid)
        if not a:
            raise ValueError("No platform adapter is connected")
        return {**self.ingest(tid, a.fetch_accounts()), "source": a.kind}

    # ---- tenants & auth ------------------------------------------------------------

    def create_tenant(self, name: str, config: Optional[dict] = None) -> tuple[str, str]:
        cfg = TenantConfig(**(config or {}))
        tid, key = sec.new_id("t_"), "bcp_" + sec.new_token()
        self.db.x("INSERT INTO tenants VALUES (?,?,?,?,?)", (tid, name, sec.hash_token(key), cfg.model_dump_json(), sec.iso(self.clock())))
        self.audit(tid, "owner", "tenant.created", {"name": name, "config": cfg.model_dump()})
        return tid, key

    def auth(self, key: str) -> Optional[tuple[str, str, str]]:
        """Returns (tenant_id, role, actor) for an owner API key or a reviewer key."""
        h = sec.hash_token(key)
        r = self.db.one("SELECT id FROM tenants WHERE api_key_hash=?", (h,))
        if r:
            return r["id"], "owner", "owner"
        r = self.db.one("SELECT tenant_id, id, name FROM reviewers WHERE key_hash=?", (h,))
        if r:
            return r["tenant_id"], "reviewer", f"reviewer:{r['name']}"
        return None

    def add_reviewer(self, tid: str, name: str) -> dict:
        rid, key = sec.new_id("rv_"), "bcr_" + sec.new_token()
        self.db.x("INSERT INTO reviewers VALUES (?,?,?,?)", (tid, rid, name, sec.hash_token(key)))
        self.audit(tid, "owner", "reviewer.added", {"id": rid, "name": name})
        return {"id": rid, "name": name, "key": key}

    def config(self, tid: str) -> TenantConfig:
        r = self.db.one("SELECT config_json FROM tenants WHERE id=?", (tid,))
        if not r:
            raise LookupError("tenant")
        return TenantConfig.model_validate_json(r["config_json"])

    def set_config(self, tid: str, patch: dict) -> TenantConfig:
        cfg = TenantConfig(**{**self.config(tid).model_dump(), **patch})
        self.db.x("UPDATE tenants SET config_json=? WHERE id=?", (cfg.model_dump_json(), tid))
        self.audit(tid, "owner", "config.changed", patch)
        return cfg

    # ---- audit (B6) ----------------------------------------------------------------

    def audit(self, tid: str, actor: str, kind: str, payload: dict) -> None:
        with self.db.tx() as tx:
            last = tx.execute("SELECT seq, hash FROM t_audit WHERE tenant_id=? ORDER BY seq DESC LIMIT 1", (tid,)).fetchone()
            seq, prev = (last["seq"] + 1, last["hash"]) if last else (1, "0" * 64)
            at = sec.iso(self.clock())
            body = dumps(payload)
            h = hashlib.sha256(f"{tid}|{seq}|{at}|{actor}|{kind}|{body}|{prev}".encode()).hexdigest()
            tx.execute("INSERT INTO t_audit VALUES (?,?,?,?,?,?,?,?)", (tid, seq, at, actor, kind, body, prev, h))

    def audit_log(self, tid: str, since: int = 0, limit: int = 500, account_id: Optional[str] = None) -> list[dict]:
        sql, args = "SELECT * FROM t_audit WHERE tenant_id=? AND seq>?", [tid, since]
        if account_id:
            sql += " AND payload_json LIKE ?"
            args.append(f'%"{account_id}"%')
        rows = self.db.q(sql + " ORDER BY seq LIMIT ?", args + [limit])
        return [{**dict(r), "payload": loads(r["payload_json"])} for r in rows]

    def verify_audit(self, tid: str) -> dict:
        prev = "0" * 64
        n = 0
        for r in self.db.q("SELECT * FROM t_audit WHERE tenant_id=? ORDER BY seq", (tid,)):
            n += 1
            h = hashlib.sha256(f"{tid}|{r['seq']}|{r['at']}|{r['actor']}|{r['kind']}|{r['payload_json']}|{prev}".encode()).hexdigest()
            if r["prev_hash"] != prev or r["hash"] != h:
                return {"ok": False, "broken_at": r["seq"], "entries": n}
            prev = h
        return {"ok": True, "entries": n, "head": prev}

    # ---- ingest & scan ----------------------------------------------------------------

    def ingest(self, tid: str, accounts: list[SiteAccount]) -> dict:
        now = sec.iso(self.clock())
        with self.db.tx() as tx:
            for a in accounts:
                tx.execute(
                    "INSERT INTO t_accounts(tenant_id,account_id,data_json,updated_at) VALUES (?,?,?,?)"
                    " ON CONFLICT(tenant_id,account_id) DO UPDATE SET data_json=excluded.data_json, updated_at=excluded.updated_at"
                    " WHERE t_accounts.state != 'removed'",
                    (tid, a.account_id, a.model_dump_json(), now),
                )
        self.audit(tid, "owner", "accounts.ingested", {"count": len(accounts)})
        return {"ingested": len(accounts)}

    @staticmethod
    def parse_csv(text: str) -> list[SiteAccount]:
        out = []
        list_fields = {"login_ips", "login_asns", "action_timestamps", "posts", "tags"}
        bool_fields = {"webdriver", "honeypot_filled", "honeypot_link_hit", "email_verified", "phone_verified"}
        for row in csv.DictReader(io.StringIO(text)):
            d: dict = {}
            for k, v in row.items():
                if k is None or v is None or v == "":
                    continue
                k = k.strip()
                if k in list_fields:
                    d[k] = [x for x in v.split("|") if x]
                elif k in bool_fields:
                    d[k] = v.strip().lower() in ("1", "true", "yes", "y")
                else:
                    d[k] = v
            out.append(SiteAccount(**d))
        return out

    def _accounts(self, tid: str) -> list[SiteAccount]:
        return [SiteAccount.model_validate_json(r["data_json"])
                for r in self.db.q("SELECT data_json FROM t_accounts WHERE tenant_id=? AND state!='removed'", (tid,))]

    def scan(self, tid: str) -> dict:
        cfg = self.config(tid)
        accs = self._accounts(tid)
        scorer = SiteScorer(extra_disposable=set(cfg.extra_disposable_domains),
                            extra_datacenter_asns=set(cfg.extra_datacenter_asns))
        results = scorer.score(accs)
        exempt_ids = set(cfg.exempt_ids)
        by_id = {a.account_id: a for a in accs}
        now = sec.iso(self.clock())
        counts: Counter = Counter()
        with self.db.tx() as tx:
            for r in results:
                a = by_id[r.account_id]
                exempt = int(r.account_id in exempt_ids or bool(set(a.tags) & set(cfg.exempt_tags)))
                label = self._label(cfg, r.score)
                counts[label] += 1
                tx.execute(
                    "UPDATE t_accounts SET score=?, label=?, reasons_json=?, ring_id=?, exempt=MAX(exempt,?), updated_at=?"
                    " WHERE tenant_id=? AND account_id=?",
                    (r.score, label, dumps([x.model_dump() for x in r.reasons]), r.ring_id, exempt, now, tid, r.account_id),
                )
        rings = len({r.ring_id for r in results if r.ring_id})
        self.audit(tid, "system", "scan.completed", {"accounts": len(results), "labels": dict(counts), "rings": rings})
        return {"scanned": len(results), "labels": dict(counts), "rings": rings}

    @staticmethod
    def _label(cfg: TenantConfig, score: float) -> str:
        if score >= cfg.tier3_min:
            return "tier3"
        if score >= cfg.tier2_min:
            return "tier2"
        if score >= cfg.tier1_min:
            return "tier1"
        return "clear"

    # ---- explorer (B1) & spot checks --------------------------------------------------

    def _row(self, r) -> dict:
        data = loads(r["data_json"], {})
        reasons = loads(r["reasons_json"], []) or []
        return {
            "account_id": r["account_id"], "username": data.get("username"), "email": data.get("email"),
            "created_at": data.get("created_at"), "tags": data.get("tags", []),
            "score": r["score"], "label": r["label"], "reasons": [x["text"] for x in reasons[:3]],
            "reason_codes": [x["code"] for x in reasons], "ring_id": r["ring_id"], "state": r["state"],
            "exempt": bool(r["exempt"]), "human_reviewed": bool(r["human_reviewed"]),
        }

    def explore(self, tid: str, min_score: float = 0, max_score: float = 100, reason: Optional[str] = None,
                ring_id: Optional[str] = None, state: Optional[str] = None, signup_after: Optional[str] = None,
                signup_before: Optional[str] = None, limit: int = 200, offset: int = 0) -> dict:
        sql = "SELECT * FROM t_accounts WHERE tenant_id=? AND COALESCE(score,0) BETWEEN ? AND ?"
        args: list = [tid, min_score, max_score]
        if reason:
            sql += " AND reasons_json LIKE ?"
            args.append(f'%"code":"{reason}"%')
        if ring_id:
            sql += " AND ring_id=?"
            args.append(ring_id)
        if state:
            sql += " AND state=?"
            args.append(state)
        rows = [self._row(r) for r in self.db.q(sql + " ORDER BY score DESC", args)]
        if signup_after:
            rows = [r for r in rows if r["created_at"] and r["created_at"] >= signup_after]
        if signup_before:
            rows = [r for r in rows if r["created_at"] and r["created_at"] <= signup_before]
        return {"total": len(rows), "accounts": rows[offset:offset + limit]}

    def rings(self, tid: str) -> list[dict]:
        groups: dict[str, list] = defaultdict(list)
        for r in self.db.q("SELECT * FROM t_accounts WHERE tenant_id=? AND ring_id IS NOT NULL", (tid,)):
            groups[r["ring_id"]].append(r)
        out = []
        for rid, rows in groups.items():
            codes = Counter(c["code"] for r in rows for c in loads(r["reasons_json"], []))
            out.append({"ring_id": rid, "size": len(rows), "mean_score": round(sum(r["score"] for r in rows) / len(rows), 1),
                        "top_reasons": [c for c, _ in codes.most_common(3)],
                        "states": dict(Counter(r["state"] for r in rows)),
                        "members": [r["account_id"] for r in rows][:50]})
        return sorted(out, key=lambda d: (-d["size"], -d["mean_score"]))

    def sample(self, tid: str, per_label: int = 10, seed: Optional[int] = None) -> dict:
        rng = random.Random(seed)
        out = {}
        for label in ("tier3", "tier2", "tier1"):
            rows = [self._row(r) for r in self.db.q("SELECT * FROM t_accounts WHERE tenant_id=? AND label=?", (tid, label))]
            out[label] = rng.sample(rows, min(per_label, len(rows)))
        return out

    def mark_reviewed(self, tid: str, account_id: str, actor: str, is_bot: bool, note: str = "") -> dict:
        """Spot-check verdict. A 'not a bot' verdict exempts the account from automated action."""
        self._get(tid, account_id)
        self.db.x("UPDATE t_accounts SET human_reviewed=1, exempt=CASE WHEN ? THEN exempt ELSE 1 END WHERE tenant_id=? AND account_id=?",
                  (int(is_bot), tid, account_id))
        self.audit(tid, actor, "account.reviewed", {"account_id": account_id, "is_bot": is_bot, "note": note})
        return self._row(self._get(tid, account_id))

    def _get(self, tid: str, account_id: str):
        r = self.db.one("SELECT * FROM t_accounts WHERE tenant_id=? AND account_id=?", (tid, account_id))
        if not r:
            raise LookupError("account")
        return r

    # ---- rules (B7) -----------------------------------------------------------------

    def rules(self, tid: str) -> list[Rule]:
        return [Rule.model_validate_json(r["data_json"]) for r in self.db.q("SELECT data_json FROM t_rules WHERE tenant_id=? ORDER BY rowid", (tid,))]

    def put_rule(self, tid: str, rule: Rule) -> Rule:
        self.db.x("INSERT OR REPLACE INTO t_rules VALUES (?,?,?)", (tid, rule.id, rule.model_dump_json()))
        self.audit(tid, "owner", "rule.saved", json.loads(rule.model_dump_json()))
        return rule

    def delete_rule(self, tid: str, rule_id: str) -> None:
        self.db.x("DELETE FROM t_rules WHERE tenant_id=? AND id=?", (tid, rule_id))
        self.audit(tid, "owner", "rule.deleted", {"id": rule_id})

    # ---- dry run (B2) and batches (B3) ------------------------------------------------

    def _target(self, cfg: TenantConfig, rules: list[Rule], acc: dict, ring_stats: dict) -> tuple[int, str]:
        if acc["exempt"]:
            return 0, "exempt"
        for rule in rules:
            if rule.matches(acc):
                return (0 if rule.exempt else (rule.tier or 0)), f"rule:{rule.name}"
        s = acc["score"] or 0
        tier = 3 if s >= cfg.tier3_min else 2 if s >= cfg.tier2_min else 1 if s >= cfg.tier1_min else 0
        rs = ring_stats.get(acc["ring_id"])
        if rs and rs[0] >= cfg.ring_tier3_min_size and rs[1] >= cfg.ring_tier3_min_mean and s >= cfg.tier1_min:
            return 3, "confirmed ring"
        return tier, "model"

    def dry_run(self, tid: str, actor: str = "owner", extra_rules: Optional[list[Rule]] = None,
                only_tiers: Optional[list[int]] = None) -> dict:
        cfg = self.config(tid)
        rules = (extra_rules or []) + self.rules(tid)
        rows = [self._row(r) for r in self.db.q("SELECT * FROM t_accounts WHERE tenant_id=? AND score IS NOT NULL", (tid,))]
        ring_scores: dict[str, list[float]] = defaultdict(list)
        for r in rows:
            if r["ring_id"]:
                ring_scores[r["ring_id"]].append(r["score"])
        ring_stats = {k: (len(v), sum(v) / len(v)) for k, v in ring_scores.items()}
        items, by_cause = [], Counter()
        for acc in rows:
            tier, cause = self._target(cfg, rules, acc, ring_stats)
            if tier == 0 or tier not in cfg.allowed_tiers or (only_tiers and tier not in only_tiers):
                continue
            if STATE_RANK[acc["state"]] >= STATE_RANK[TIER_STATE[tier]]:
                continue  # already at or beyond this action
            items.append({"account_id": acc["account_id"], "current_state": acc["state"], "tier": tier,
                          "action": TIER_STATE[tier], "score": acc["score"], "reasons": acc["reasons"],
                          "ring_id": acc["ring_id"], "cause": cause})
            by_cause[cause] += 1
        items.sort(key=lambda i: (-i["tier"], -(i["score"] or 0)))
        bid = sec.new_id("b_")
        self.db.x("INSERT INTO t_batches VALUES (?,?,?,?,?,?,?,?)",
                  (tid, bid, sec.iso(self.clock()), actor, "planned", dumps(items), 0, cfg.batch_size))
        summary = {"batch_id": bid, "total": len(items), "by_tier": dict(Counter(i["tier"] for i in items)),
                   "by_cause": dict(by_cause)}
        self.audit(tid, actor, "dry_run", summary)
        return {**summary, "items": items}

    def batch(self, tid: str, bid: str) -> dict:
        r = self.db.one("SELECT * FROM t_batches WHERE tenant_id=? AND id=?", (tid, bid))
        if not r:
            raise LookupError("batch")
        plan = loads(r["plan_json"], [])
        return {**{k: r[k] for k in r.keys() if k != "plan_json"}, "total": len(plan), "items": plan}

    def batches(self, tid: str) -> list[dict]:
        return [{k: r[k] for k in r.keys() if k != "plan_json"}
                for r in self.db.q("SELECT * FROM t_batches WHERE tenant_id=? ORDER BY created_at DESC", (tid,))]

    def execute(self, tid: str, bid: str, actor: str = "owner") -> dict:
        b = self.batch(tid, bid)
        if b["state"] not in ("planned", "paused"):
            raise ValueError(f"batch is {b['state']}")
        self.db.x("UPDATE t_batches SET state='running' WHERE tenant_id=? AND id=?", (tid, bid))
        self.audit(tid, actor, "batch.started", {"batch_id": bid, "total": b["total"]})
        return self.step(tid, bid, actor)

    def step(self, tid: str, bid: str, actor: str = "owner") -> dict:
        """Apply the next ``batch_size`` items of a running batch (called repeatedly by the worker)."""
        b = self.batch(tid, bid)
        if b["state"] != "running":
            return self.batch_status(tid, bid)
        cfg = self.config(tid)
        start, end = b["cursor"], min(b["cursor"] + b["batch_size"], b["total"])
        now = self.clock()
        applied, skipped = 0, 0
        for item in b["items"][start:end]:
            cur = self.db.one("SELECT state, exempt FROM t_accounts WHERE tenant_id=? AND account_id=?", (tid, item["account_id"]))
            # The plan is exact: if the account changed since the dry run, don't act on it.
            if not cur or cur["state"] != item["current_state"] or cur["exempt"]:
                skipped += 1
                continue
            self._apply(tid, item["account_id"], item["tier"], cur["state"], actor, bid, item["reasons"], now, cfg)
            applied += 1
        state = "done" if end >= b["total"] else "running"
        self.db.x("UPDATE t_batches SET cursor=?, state=CASE WHEN state='running' THEN ? ELSE state END WHERE tenant_id=? AND id=?",
                  (end, state, tid, bid))
        self.audit(tid, actor, "batch.step", {"batch_id": bid, "from": start, "to": end, "applied": applied, "skipped": skipped})
        return self.batch_status(tid, bid)

    def batch_status(self, tid: str, bid: str) -> dict:
        b = self.batch(tid, bid)
        acts = self.db.one("SELECT COUNT(*) n, SUM(rolled_back) rb FROM t_actions WHERE tenant_id=? AND batch_id=?", (tid, bid))
        return {"batch_id": bid, "state": b["state"], "cursor": b["cursor"], "total": b["total"],
                "applied": acts["n"] or 0, "rolled_back": acts["rb"] or 0}

    def pause(self, tid: str, bid: str, actor: str = "owner") -> dict:
        self.db.x("UPDATE t_batches SET state='paused' WHERE tenant_id=? AND id=? AND state='running'", (tid, bid))
        self.audit(tid, actor, "batch.paused", {"batch_id": bid})
        return self.batch_status(tid, bid)

    def rollback(self, tid: str, bid: str, actor: str = "owner") -> dict:
        """Undo every action in the batch whose account hasn't moved on since."""
        acts = self.db.q("SELECT * FROM t_actions WHERE tenant_id=? AND batch_id=? AND rolled_back=0 ORDER BY id DESC", (tid, bid))
        restored = 0
        for a in acts:
            cur = self.db.one("SELECT state FROM t_accounts WHERE tenant_id=? AND account_id=?", (tid, a["account_id"]))
            with self.db.tx() as tx:
                tx.execute("UPDATE t_actions SET rolled_back=1 WHERE tenant_id=? AND id=?", (tid, a["id"]))
                if cur and cur["state"] == a["new_state"]:
                    tx.execute("UPDATE t_accounts SET state=?, state_changed_at=? WHERE tenant_id=? AND account_id=?",
                               (a["prev_state"], sec.iso(self.clock()), tid, a["account_id"]))
                    tx.execute("UPDATE t_appeals SET status='void', decided_at=?, decision_note='action rolled back'"
                               " WHERE tenant_id=? AND account_id=? AND status='open'", (sec.iso(self.clock()), tid, a["account_id"]))
                    restored += 1
            if cur and cur["state"] == a["new_state"]:
                self._enforce(tid, a["account_id"], a["prev_state"], None)
        self.db.x("UPDATE t_batches SET state='rolled_back' WHERE tenant_id=? AND id=?", (tid, bid))
        self.audit(tid, actor, "batch.rolled_back", {"batch_id": bid, "restored": restored})
        return {**self.batch_status(tid, bid), "restored": restored}

    def _apply(self, tid: str, account_id: str, tier: int, prev: str, actor: str, bid: Optional[str],
               reasons: list[str], now: datetime, cfg: TenantConfig) -> Optional[str]:
        new = TIER_STATE[tier]
        notice_id = sec.new_id("n_")
        deadline = now + timedelta(days=cfg.appeal_window_days)
        with self.db.tx() as tx:
            tx.execute("UPDATE t_accounts SET state=?, state_changed_at=? WHERE tenant_id=? AND account_id=?",
                       (new, sec.iso(now), tid, account_id))
            tx.execute("INSERT INTO t_actions(tenant_id,batch_id,account_id,tier,prev_state,new_state,at,actor)"
                       " VALUES (?,?,?,?,?,?,?,?)", (tid, bid, account_id, tier, prev, new, sec.iso(now), actor))
            if tier < 4:
                token = self.appeal_token(tid, notice_id)
                tx.execute("INSERT INTO t_notices VALUES (?,?,?,?,?,?,?,?,?)",
                           (tid, notice_id, account_id, sec.hash_token(token), tier, new, dumps(reasons[:3]),
                            sec.iso(now), sec.iso(deadline)))
        self.audit(tid, actor, "account.action", {"account_id": account_id, "tier": tier, "from": prev, "to": new,
                                                  "batch_id": bid, "notice_id": notice_id if tier < 4 else None,
                                                  "reasons": reasons[:3]})
        self._enforce(tid, account_id, new, notice_id if tier < 4 else None)
        return notice_id if tier < 4 else None

    # ---- notices (B5) & enforcement feed ------------------------------------------------

    @staticmethod
    def appeal_token(tid: str, notice_id: str) -> str:
        mac = hmac.new(sec._key(), f"appeal:{tid}:{notice_id}".encode(), hashlib.sha256).hexdigest()[:32]
        return f"{tid}.{notice_id}.{mac}"

    def notice_for_account(self, tid: str, account_id: str) -> Optional[dict]:
        r = self.db.one("SELECT * FROM t_notices WHERE tenant_id=? AND account_id=? ORDER BY created_at DESC LIMIT 1", (tid, account_id))
        return self._notice_out(tid, r) if r else None

    def _notice_out(self, tid: str, r) -> dict:
        cfg = self.config(tid)
        token = self.appeal_token(tid, r["id"])
        tenant = self.db.one("SELECT name FROM tenants WHERE id=?", (tid,))["name"]
        reasons = loads(r["reasons_json"], [])
        deadline = sec.parse_iso(r["appeal_deadline"])
        return {
            "notice_id": r["id"], "account_id": r["account_id"], "tier": r["tier"], "action": r["action"],
            "platform": tenant,
            "what_happened": ACTION_TEXT[r["tier"]],
            "why": reasons,
            "how_to_appeal": (f"If you're a real person, tell us at the link below before {deadline:%B %d, %Y}. "
                              "A person on our team reviews every appeal; if we got it wrong, your account is restored automatically."),
            "appeal_deadline": r["appeal_deadline"],
            "appeal_url": f"{cfg.appeal_base_url.rstrip('/')}/{token}",
            "appeal_token": token,
        }

    def _enforce(self, tid: str, account_id: str, state: str, notice_id: Optional[str]) -> None:
        payload = {"tenant_id": tid, "account_id": account_id, "state": state}
        if notice_id:
            r = self.db.one("SELECT * FROM t_notices WHERE tenant_id=? AND id=?", (tid, notice_id))
            payload["notice"] = self._notice_out(tid, r)
        try:
            if self.enforcer:
                self.enforcer(tid, payload)
            else:
                url = self.config(tid).enforcement_webhook
                if url:
                    import httpx

                    httpx.post(url, json=payload, timeout=10)
        except Exception as exc:  # the feed below is the source of truth; a failed push is retried by polling
            self.audit(tid, "system", "enforcement.push_failed", {"account_id": account_id, "error": str(exc)[:200]})
        try:
            adapter = self.adapter_for(tid)
            if adapter:
                adapter.enforce(account_id, state, payload.get("notice"))
        except Exception as exc:
            self.audit(tid, "system", "enforcement.adapter_failed",
                       {"account_id": account_id, "state": state, "error": str(exc)[:200]})

    def enforcement_feed(self, tid: str, since_id: int = 0, limit: int = 1000) -> list[dict]:
        """Actions for the platform to enforce, in order (poll with the last id you processed)."""
        out = []
        for a in self.db.q("SELECT * FROM t_actions WHERE tenant_id=? AND id>? ORDER BY id LIMIT ?", (tid, since_id, limit)):
            n = self.db.one("SELECT * FROM t_notices WHERE tenant_id=? AND account_id=? AND created_at=?",
                            (tid, a["account_id"], a["at"]))
            out.append({"id": a["id"], "account_id": a["account_id"], "state": a["prev_state"] if a["rolled_back"] else a["new_state"],
                        "tier": a["tier"], "rolled_back": bool(a["rolled_back"]), "at": a["at"],
                        "notice": self._notice_out(tid, n) if n else None})
        return out

    def report_verified(self, tid: str, account_id: str) -> dict:
        """The platform reports the user passed the challenge / re-verification (tiers 1-2)."""
        r = self._get(tid, account_id)
        if r["state"] not in ("challenged", "restricted"):
            raise ValueError(f"account is {r['state']}; only challenged or restricted accounts can verify")
        self.db.x("UPDATE t_accounts SET state='active', state_changed_at=?, exempt=1 WHERE tenant_id=? AND account_id=?",
                  (sec.iso(self.clock()), tid, account_id))
        self.db.x("INSERT INTO t_actions(tenant_id,batch_id,account_id,tier,prev_state,new_state,at,actor) VALUES (?,?,?,?,?,?,?,?)",
                  (tid, None, account_id, 0, r["state"], "active", sec.iso(self.clock()), "verification"))
        self.audit(tid, "system", "account.verified", {"account_id": account_id, "from": r["state"]})
        self._enforce(tid, account_id, "active", None)
        return self._row(self._get(tid, account_id))

    # ---- appeals (B4) -------------------------------------------------------------------

    def _notice_by_token(self, token: str):
        try:
            tid, nid, mac = token.split(".")
        except ValueError:
            raise LookupError("invalid appeal link")
        if not hmac.compare_digest(self.appeal_token(tid, nid), token):
            raise LookupError("invalid appeal link")
        r = self.db.one("SELECT * FROM t_notices WHERE tenant_id=? AND id=?", (tid, nid))
        if not r:
            raise LookupError("invalid appeal link")
        return tid, r

    def view_notice(self, token: str) -> dict:
        tid, n = self._notice_by_token(token)
        out = self._notice_out(tid, n)
        out.pop("appeal_token")
        acc = self._get(tid, n["account_id"])
        ap = self.db.one("SELECT * FROM t_appeals WHERE tenant_id=? AND notice_id=? ORDER BY created_at DESC LIMIT 1", (tid, n["id"]))
        out["current_state"] = acc["state"]
        out["appeal"] = ({"id": ap["id"], "status": ap["status"], "review_due": ap["review_due"],
                          "decision_note": ap["decision_note"]} if ap else None)
        out["can_appeal"] = (ap is None or ap["status"] == "void") and self.clock() <= sec.parse_iso(n["appeal_deadline"]) \
            and acc["state"] != "active"
        return out

    def submit_appeal(self, token: str, statement: str, contact: str = "") -> dict:
        tid, n = self._notice_by_token(token)
        statement = statement.strip()
        if len(statement) < 10:
            raise ValueError("Please tell us a little more (at least 10 characters)")
        if len(statement) > 5000:
            raise ValueError("Please keep it under 5,000 characters")
        if self.clock() > sec.parse_iso(n["appeal_deadline"]):
            raise ValueError("The appeal window for this notice has closed")
        if self.db.one("SELECT 1 FROM t_appeals WHERE tenant_id=? AND notice_id=? AND status!='void'", (tid, n["id"])):
            raise ValueError("You've already appealed this decision")
        cfg = self.config(tid)
        aid = sec.new_id("ap_")
        now = self.clock()
        self.db.x("INSERT INTO t_appeals VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                  (tid, aid, n["id"], n["account_id"], statement, contact[:200], "open", sec.iso(now),
                   sec.iso(now + timedelta(days=cfg.review_sla_days)), None, None, None))
        self.audit(tid, "appellant", "appeal.submitted", {"appeal_id": aid, "account_id": n["account_id"], "notice_id": n["id"]})
        return {"appeal_id": aid, "status": "open", "review_due": sec.iso(now + timedelta(days=cfg.review_sla_days))}

    def appeal_queue(self, tid: str, status: str = "open") -> list[dict]:
        now = self.clock()
        out = []
        for r in self.db.q("SELECT * FROM t_appeals WHERE tenant_id=? AND status=? ORDER BY review_due", (tid, status)):
            acc = self._row(self._get(tid, r["account_id"]))
            out.append({**dict(r), "overdue": r["status"] == "open" and now > sec.parse_iso(r["review_due"]), "account": acc})
        return out

    def decide(self, tid: str, appeal_id: str, reviewer: str, approve: bool, note: str = "") -> dict:
        r = self.db.one("SELECT * FROM t_appeals WHERE tenant_id=? AND id=?", (tid, appeal_id))
        if not r:
            raise LookupError("appeal")
        if r["status"] != "open":
            raise ValueError(f"appeal is already {r['status']}")
        if not reviewer.startswith(("reviewer:", "owner")):
            raise Forbidden("only reviewers can decide appeals")
        now = self.clock()
        self.db.x("UPDATE t_appeals SET status=?, reviewer=?, decided_at=?, decision_note=? WHERE tenant_id=? AND id=?",
                  ("approved" if approve else "denied", reviewer, sec.iso(now), note[:1000], tid, appeal_id))
        self.db.x("UPDATE t_accounts SET human_reviewed=1 WHERE tenant_id=? AND account_id=?", (tid, r["account_id"]))
        self.audit(tid, reviewer, "appeal.decided", {"appeal_id": appeal_id, "account_id": r["account_id"],
                                                     "approved": approve, "note": note[:1000]})
        if approve:
            acc = self._get(tid, r["account_id"])
            if acc["state"] not in ("active", "removed"):
                self.db.x("UPDATE t_accounts SET state='active', exempt=1, state_changed_at=? WHERE tenant_id=? AND account_id=?",
                          (sec.iso(now), tid, r["account_id"]))
                self.db.x("INSERT INTO t_actions(tenant_id,batch_id,account_id,tier,prev_state,new_state,at,actor) VALUES (?,?,?,?,?,?,?,?)",
                          (tid, None, r["account_id"], 0, acc["state"], "active", sec.iso(now), reviewer))
                self.audit(tid, reviewer, "account.restored", {"account_id": r["account_id"], "from": acc["state"], "appeal_id": appeal_id})
                self._enforce(tid, r["account_id"], "active", None)
        return dict(self.db.one("SELECT * FROM t_appeals WHERE tenant_id=? AND id=?", (tid, appeal_id)))

    # ---- tier 4: permanent removal ----------------------------------------------------------

    def removal_candidates(self, tid: str) -> list[dict]:
        """Suspended accounts whose appeal window lapsed with no open or successful appeal."""
        now = self.clock()
        out = []
        for acc in self.db.q("SELECT * FROM t_accounts WHERE tenant_id=? AND state='suspended'", (tid,)):
            n = self.db.one("SELECT * FROM t_notices WHERE tenant_id=? AND account_id=? AND tier=3 ORDER BY created_at DESC LIMIT 1",
                            (tid, acc["account_id"]))
            if not n or now <= sec.parse_iso(n["appeal_deadline"]):
                continue
            if self.db.one("SELECT 1 FROM t_appeals WHERE tenant_id=? AND account_id=? AND status IN ('open','approved')",
                           (tid, acc["account_id"])):
                continue
            out.append({**self._row(acc), "appeal_deadline": n["appeal_deadline"]})
        return out

    def remove_permanently(self, tid: str, account_ids: list[str], reviewer: str) -> dict:
        """Tier 4. Needs a human reviewer's sign-off; deletes the account data we hold."""
        if not reviewer.startswith(("reviewer:", "owner")):
            raise Forbidden("a human reviewer must approve permanent removal")
        cfg = self.config(tid)
        if 4 not in cfg.allowed_tiers:
            raise Forbidden("permanent removal is disabled for this platform")
        eligible = {c["account_id"] for c in self.removal_candidates(tid)}
        removed, refused = [], []
        for aid in account_ids:
            if aid not in eligible:
                refused.append(aid)
                continue
            self._apply(tid, aid, 4, "suspended", reviewer, None, [], self.clock(), cfg)
            self.db.x("UPDATE t_accounts SET data_json='{}', human_reviewed=1 WHERE tenant_id=? AND account_id=?", (tid, aid))
            removed.append(aid)
        self.audit(tid, reviewer, "accounts.removed_permanently", {"removed": removed, "refused": refused})
        return {"removed": removed, "refused": refused}

    # ---- real-time gate (B8) -----------------------------------------------------------------

    def gate_signup(self, tid: str, signup: SiteAccount) -> dict:
        cfg = self.config(tid)
        now = self.clock()
        signup = signup.model_copy(update={"created_at": signup.created_at or now})
        since = sec.iso(now - timedelta(hours=1))
        recent = [
            SiteAccount(account_id=f"recent{i}", signup_ip=r["ip"], signup_asn=r["asn"], device_fingerprint=r["fingerprint"],
                        email=r["email"], created_at=sec.parse_iso(r["at"]))
            for i, r in enumerate(self.db.q("SELECT * FROM t_signups WHERE tenant_id=? AND at>=?", (tid, since)))
        ]
        scorer = SiteScorer(extra_disposable=set(cfg.extra_disposable_domains), extra_datacenter_asns=set(cfg.extra_datacenter_asns))
        res = next(r for r in scorer.score(recent + [signup]) if r.account_id == signup.account_id)
        decision = "block" if res.score >= cfg.tier3_min else "challenge" if res.score >= cfg.tier1_min else "allow"
        from .signals import subnet_of

        self.db.x("INSERT INTO t_signups VALUES (?,?,?,?,?,?,?,?,?)",
                  (tid, sec.iso(signup.created_at), signup.signup_ip, subnet_of(signup.signup_ip), signup.signup_asn,
                   signup.device_fingerprint, signup.email, decision, res.score))
        return {"decision": decision, "score": res.score, "reasons": [r.text for r in res.reasons[:3]]}

    # ---- reports (B9) ------------------------------------------------------------------------

    def report(self, tid: str, days: int = 30) -> dict:
        states = {r["state"]: r["n"] for r in self.db.q("SELECT state, COUNT(*) n FROM t_accounts WHERE tenant_id=? GROUP BY state", (tid,))}
        labels = {r["label"]: r["n"] for r in self.db.q("SELECT label, COUNT(*) n FROM t_accounts WHERE tenant_id=? AND label IS NOT NULL GROUP BY label", (tid,))}
        appeals = {r["status"]: r["n"] for r in self.db.q("SELECT status, COUNT(*) n FROM t_appeals WHERE tenant_id=? GROUP BY status", (tid,))}
        decided = appeals.get("approved", 0) + appeals.get("denied", 0)
        actioned = self.db.one("SELECT COUNT(DISTINCT account_id) n FROM t_actions WHERE tenant_id=? AND tier>=1 AND rolled_back=0", (tid,))["n"]
        since = sec.iso(self.clock() - timedelta(days=days))
        trend = [dict(r) for r in self.db.q(
            "SELECT substr(at,1,10) day, tier, COUNT(*) n FROM t_actions WHERE tenant_id=? AND at>=? AND rolled_back=0 GROUP BY day, tier ORDER BY day",
            (tid, since))]
        reasons = Counter()
        for r in self.db.q("SELECT reasons_json FROM t_accounts WHERE tenant_id=? AND label IN ('tier1','tier2','tier3')", (tid,)):
            for x in loads(r["reasons_json"], [])[:3]:
                reasons[x["code"]] += 1
        gate = {r["decision"]: r["n"] for r in self.db.q("SELECT decision, COUNT(*) n FROM t_signups WHERE tenant_id=? GROUP BY decision", (tid,))}
        return {
            "accounts_by_state": states, "accounts_by_label": labels, "bots_removed": states.get("removed", 0),
            "accounts_actioned": actioned, "appeals": appeals,
            "appeal_rate": round(sum(appeals.values()) / actioned, 4) if actioned else 0.0,
            "overturn_rate": round(appeals.get("approved", 0) / decided, 4) if decided else 0.0,
            "overturn_target_met": (appeals.get("approved", 0) / decided <= 0.05) if decided else None,
            "trend": trend, "top_reasons": dict(reasons.most_common(8)), "signup_gate": gate,
        }
