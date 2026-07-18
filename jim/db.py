"""SQLite persistence for JIM-mini (independent of QRME's database)."""

from __future__ import annotations

import os
import sqlite3
import threading
import uuid
from datetime import datetime, timezone

_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id                 TEXT PRIMARY KEY,
    display_name       TEXT NOT NULL,
    birthdate          TEXT,
    terms_consent      INTEGER NOT NULL DEFAULT 0,
    guardian_consent   INTEGER NOT NULL DEFAULT 0,
    emergency_name     TEXT,
    emergency_phone    TEXT,
    contact_consent    INTEGER NOT NULL DEFAULT 0,
    device_paired      INTEGER NOT NULL DEFAULT 0,
    resting_heart_rate INTEGER,
    goals              TEXT,
    created_at         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS specialists (
    condition       TEXT PRIMARY KEY,   -- condition domain key (see conditions.py)
    mode            TEXT NOT NULL,      -- local | tandem
    label           TEXT,
    qrme_profile_id TEXT,               -- set when mode = tandem
    created_at      TEXT NOT NULL
);

-- Per-user mapping to a QRME interactor, created lazily for tandem guidance.
CREATE TABLE IF NOT EXISTS tandem_links (
    user_id            TEXT PRIMARY KEY REFERENCES users(id),
    qrme_interactor_id TEXT NOT NULL,
    created_at         TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    type       TEXT NOT NULL,   -- biometric | detection | guidance | escalation
    condition  TEXT,
    severity   TEXT,
    detail     TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);
"""

_local = threading.local()


def db_path() -> str:
    return os.environ.get("JIM_DB", "jim.db")


def connect() -> sqlite3.Connection:
    conn = getattr(_local, "conn", None)
    if conn is None or getattr(_local, "path", None) != db_path():
        conn = sqlite3.connect(db_path())
        conn.row_factory = sqlite3.Row
        conn.executescript(_SCHEMA)
        _local.conn = conn
        _local.path = db_path()
    return conn


def reset() -> None:
    conn = getattr(_local, "conn", None)
    if conn is not None:
        conn.close()
        _local.conn = None
        _local.path = None


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()
