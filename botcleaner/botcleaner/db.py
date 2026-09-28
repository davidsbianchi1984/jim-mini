"""SQLite storage for both modules.

Module A and Module B share a file but never a row: every Module B table is
keyed by ``tenant_id`` and every query filters on it (tenant isolation).
The audit log is append-only: triggers refuse UPDATE and DELETE, and each row
carries the hash of the previous one so tampering is detectable.
"""
from __future__ import annotations

import json
import os
import sqlite3
import threading
from contextlib import contextmanager
from typing import Any, Iterator

SCHEMA = """
PRAGMA foreign_keys = ON;

-- ---------------- Module A: personal cleaner ----------------
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    token_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    model_json TEXT NOT NULL DEFAULT '{}',
    rescan TEXT NOT NULL DEFAULT 'off',            -- off | weekly | monthly
    next_rescan_at TEXT,
    guardian_of TEXT,                               -- parent/guardian scanning a teen, with consent
    consent_at TEXT
);

-- Raw-ish connection detail from imports/APIs. Purged after the raw-data TTL (24h).
CREATE TABLE IF NOT EXISTS connections (
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    account_id TEXT NOT NULL,
    direction TEXT NOT NULL,
    data_json TEXT NOT NULL,
    imported_at TEXT NOT NULL,
    PRIMARY KEY (user_id, platform, account_id, direction)
);

-- What we keep: scores, labels, decisions, and just enough identity to show and undo.
CREATE TABLE IF NOT EXISTS flags (
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    account_id TEXT NOT NULL,
    direction TEXT NOT NULL,
    handle TEXT, name TEXT, profile_url TEXT, avatar_hash TEXT,
    connected_at TEXT,
    score REAL NOT NULL,
    label TEXT NOT NULL,
    reasons_json TEXT NOT NULL,
    is_clone INTEGER NOT NULL DEFAULT 0,
    clone_of TEXT,
    ring_id TEXT,
    status TEXT NOT NULL DEFAULT 'active',          -- active | whitelisted | pending | removed | failed
    scanned_at TEXT NOT NULL,
    PRIMARY KEY (user_id, platform, account_id, direction)
);

CREATE TABLE IF NOT EXISTS scans (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform TEXT,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    counts_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS removal_jobs (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    mode TEXT NOT NULL,                             -- one_click | assisted | guided
    state TEXT NOT NULL,                            -- running | paused | done | cancelled
    created_at TEXT NOT NULL,
    pace_seconds REAL NOT NULL,
    next_at TEXT
);

CREATE TABLE IF NOT EXISTS removal_items (
    job_id TEXT NOT NULL REFERENCES removal_jobs(id) ON DELETE CASCADE,
    idx INTEGER NOT NULL,
    platform TEXT NOT NULL,
    account_id TEXT NOT NULL,
    direction TEXT NOT NULL,
    action TEXT NOT NULL,                           -- unfriend | remove_follower | unfollow
    mode TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued',          -- queued | opened | pending | removed | failed | skipped
    attempts INTEGER NOT NULL DEFAULT 0,
    error TEXT,
    updated_at TEXT,
    PRIMARY KEY (job_id, idx)
);

CREATE TABLE IF NOT EXISTS undo_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    at TEXT NOT NULL,
    event TEXT NOT NULL,                            -- flagged | removed | failed | whitelisted | confirmed_bot | readded
    platform TEXT NOT NULL,
    account_id TEXT NOT NULL,
    direction TEXT NOT NULL,
    handle TEXT, name TEXT, profile_url TEXT,
    score REAL, reasons TEXT
);

CREATE TABLE IF NOT EXISTS alerts (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    at TEXT NOT NULL,
    kind TEXT NOT NULL,
    text TEXT NOT NULL,
    platform TEXT, account_id TEXT, link TEXT,
    read INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS secrets (
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    sealed BLOB NOT NULL,
    PRIMARY KEY (user_id, name)
);

CREATE TABLE IF NOT EXISTS oauth_pending (
    state TEXT PRIMARY KEY,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    verifier TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS instructions (
    id TEXT PRIMARY KEY,
    data_json TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS instruction_flags (
    instruction_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    at TEXT NOT NULL,
    PRIMARY KEY (instruction_id, user_id)
);

-- ---------------- Module B: platform purge console ----------------
CREATE TABLE IF NOT EXISTS tenants (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    api_key_hash TEXT NOT NULL,
    config_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reviewers (
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    id TEXT NOT NULL,
    name TEXT NOT NULL,
    key_hash TEXT NOT NULL,
    PRIMARY KEY (tenant_id, id)
);

CREATE TABLE IF NOT EXISTS t_accounts (
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    account_id TEXT NOT NULL,
    data_json TEXT NOT NULL,
    score REAL, label TEXT, reasons_json TEXT, ring_id TEXT,
    state TEXT NOT NULL DEFAULT 'active',           -- active | challenged | restricted | suspended | removed
    exempt INTEGER NOT NULL DEFAULT 0,
    human_reviewed INTEGER NOT NULL DEFAULT 0,
    state_changed_at TEXT,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (tenant_id, account_id)
);

CREATE TABLE IF NOT EXISTS t_rules (
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    id TEXT NOT NULL,
    data_json TEXT NOT NULL,
    PRIMARY KEY (tenant_id, id)
);

CREATE TABLE IF NOT EXISTS t_batches (
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    actor TEXT NOT NULL,
    state TEXT NOT NULL,                            -- running | paused | done | rolled_back
    plan_json TEXT NOT NULL,
    cursor INTEGER NOT NULL DEFAULT 0,
    batch_size INTEGER NOT NULL,
    PRIMARY KEY (tenant_id, id)
);

CREATE TABLE IF NOT EXISTS t_actions (
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id TEXT,
    account_id TEXT NOT NULL,
    tier INTEGER NOT NULL,
    prev_state TEXT NOT NULL,
    new_state TEXT NOT NULL,
    at TEXT NOT NULL,
    actor TEXT NOT NULL,
    rolled_back INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS t_notices (
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    token_hash TEXT NOT NULL,
    tier INTEGER NOT NULL,
    action TEXT NOT NULL,
    reasons_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    appeal_deadline TEXT NOT NULL,
    PRIMARY KEY (tenant_id, id)
);

CREATE TABLE IF NOT EXISTS t_appeals (
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    id TEXT NOT NULL,
    notice_id TEXT NOT NULL,
    account_id TEXT NOT NULL,
    statement TEXT NOT NULL,
    contact TEXT,
    status TEXT NOT NULL,                           -- open | approved | denied
    created_at TEXT NOT NULL,
    review_due TEXT NOT NULL,
    reviewer TEXT,
    decided_at TEXT,
    decision_note TEXT,
    PRIMARY KEY (tenant_id, id)
);

CREATE TABLE IF NOT EXISTS t_audit (
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    seq INTEGER NOT NULL,
    at TEXT NOT NULL,
    actor TEXT NOT NULL,
    kind TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    prev_hash TEXT NOT NULL,
    hash TEXT NOT NULL,
    PRIMARY KEY (tenant_id, seq)
);

CREATE TRIGGER IF NOT EXISTS t_audit_no_update BEFORE UPDATE ON t_audit
BEGIN SELECT RAISE(ABORT, 'audit log is append-only'); END;
CREATE TRIGGER IF NOT EXISTS t_audit_no_delete BEFORE DELETE ON t_audit
WHEN (SELECT COUNT(*) FROM tenants WHERE id = OLD.tenant_id) > 0
BEGIN SELECT RAISE(ABORT, 'audit log is append-only'); END;

CREATE TABLE IF NOT EXISTS t_signups (
    tenant_id TEXT NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    at TEXT NOT NULL,
    ip TEXT, subnet TEXT, asn TEXT, fingerprint TEXT, email TEXT,
    decision TEXT NOT NULL,
    score REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS t_signups_idx ON t_signups(tenant_id, at);
"""


class DB:
    def __init__(self, path: str | None = None):
        self.path = path or os.environ.get("BOTCLEANER_DB", "botcleaner.sqlite3")
        self.conn = sqlite3.connect(self.path, check_same_thread=False, isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        self.lock = threading.RLock()
        with self.lock:
            self.conn.executescript(SCHEMA)

    @contextmanager
    def tx(self) -> Iterator[sqlite3.Connection]:
        with self.lock:
            self.conn.execute("BEGIN IMMEDIATE")
            try:
                yield self.conn
                self.conn.execute("COMMIT")
            except BaseException:
                self.conn.execute("ROLLBACK")
                raise

    def q(self, sql: str, args: tuple | list = ()) -> list[sqlite3.Row]:
        with self.lock:
            return self.conn.execute(sql, args).fetchall()

    def one(self, sql: str, args: tuple | list = ()) -> sqlite3.Row | None:
        with self.lock:
            return self.conn.execute(sql, args).fetchone()

    def x(self, sql: str, args: tuple | list = ()) -> int:
        with self.lock:
            return self.conn.execute(sql, args).rowcount


def dumps(v: Any) -> str:
    return json.dumps(v, default=str, separators=(",", ":"))


def loads(s: str | None, default: Any = None) -> Any:
    return json.loads(s) if s else default
