"""Product metrics from PRD section 10, computed from what the app already records.

* Flag confirmation: of the flagged accounts (score >= 60) a user made a call on,
  the share they confirmed as bots (removed, queued, or "Definitely a bot")
  rather than rejected ("Real person" or "I re-added them"). Target >= 90%.
* First-scan completion: of users who ran a scan, the share who went on to
  remove at least one account. Target >= 60%.
* Scan-to-clean: minutes from a user's first scan to their first finished
  removal job. Median target <= 10 minutes.
* Platform restrictions: accounts users report as restricted by a platform
  after using the app. Target: zero.
* Module B overturn rate across all tenants. Target <= 5%.
"""
from __future__ import annotations

import statistics
from typing import Optional

from . import security as sec
from .db import DB

CONFIRM = {"removed", "failed", "confirmed_bot"}
REJECT = {"whitelisted", "readded"}
TARGETS = {
    "flag_confirmation_rate": 0.90,
    "first_scan_completion_rate": 0.60,
    "median_scan_to_clean_minutes": 10.0,
    "platform_restrictions": 0,
    "overturn_rate": 0.05,
}


def _rate(n: int, d: int) -> Optional[float]:
    return round(n / d, 4) if d else None


def product_metrics(db: DB) -> dict:
    # Latest decision per flagged account, from the undo log.
    latest: dict[tuple, str] = {}
    for r in db.q("SELECT user_id, platform, account_id, event, score FROM undo_log"
                  " WHERE event IN ('removed','failed','confirmed_bot','whitelisted','readded') ORDER BY id"):
        if (r["score"] or 0) >= 60:
            latest[(r["user_id"], r["platform"], r["account_id"])] = r["event"]
    # Accounts queued for removal but not yet re-checked count as confirmed too.
    for r in db.q("SELECT user_id, platform, account_id FROM flags WHERE status='pending' AND score >= 60"):
        latest.setdefault((r["user_id"], r["platform"], r["account_id"]), "removed")
    confirmed = sum(1 for e in latest.values() if e in CONFIRM)

    scanned = {r["user_id"]: sec.parse_iso(r["t"]) for r in db.q(
        "SELECT user_id, MIN(finished_at) t FROM scans GROUP BY user_id")}
    removers = {r["user_id"] for r in db.q(
        "SELECT DISTINCT j.user_id FROM removal_items i JOIN removal_jobs j ON j.id=i.job_id"
        " WHERE i.status IN ('removed','pending')")}
    durations = []
    for r in db.q("SELECT user_id, MIN(finished_at) t FROM removal_jobs WHERE state='done' GROUP BY user_id"):
        start, end = scanned.get(r["user_id"]), sec.parse_iso(r["t"])
        if start and end and end >= start:
            durations.append((end - start).total_seconds() / 60)

    restrictions = db.one("SELECT COUNT(*) n FROM alerts WHERE kind='platform_restriction'")["n"]

    appeals = {r["status"]: r["n"] for r in db.q("SELECT status, COUNT(*) n FROM t_appeals GROUP BY status")}
    decided = appeals.get("approved", 0) + appeals.get("denied", 0)

    out = {
        "flag_confirmation_rate": _rate(confirmed, len(latest)),
        "flag_decisions": len(latest),
        "first_scan_completion_rate": _rate(len(removers & set(scanned)), len(scanned)),
        "users_scanned": len(scanned),
        "median_scan_to_clean_minutes": round(statistics.median(durations), 1) if durations else None,
        "scan_to_clean_samples": len(durations),
        "platform_restrictions": restrictions,
        "overturn_rate": _rate(appeals.get("approved", 0), decided),
        "appeals_decided": decided,
    }
    met = {}
    for k, target in TARGETS.items():
        v = out[k]
        if v is None:
            met[k] = None
        elif k in ("median_scan_to_clean_minutes", "platform_restrictions", "overturn_rate"):
            met[k] = v <= target
        else:
            met[k] = v >= target
    return {**out, "targets": TARGETS, "met": met}
