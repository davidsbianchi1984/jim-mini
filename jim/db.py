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
    known_conditions   TEXT NOT NULL DEFAULT '[]',  -- declared known conditions
    devices            TEXT NOT NULL DEFAULT '[]',  -- e.g. ["smart_watch","phone"]
    personality        TEXT,                        -- counselor adaptation prefs
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

-- Connected data sources; nothing is read from a source the user hasn't
-- explicitly consented to ("AI only sees what you allow").
CREATE TABLE IF NOT EXISTS sources (
    user_id    TEXT NOT NULL REFERENCES users(id),
    source     TEXT NOT NULL,   -- wearable | health | calendar | spending | bank | messages | location
    consented  INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    PRIMARY KEY (user_id, source)
);

-- Events ingested from consented sources (a calendar entry, a transaction, …).
CREATE TABLE IF NOT EXISTS context_events (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    source     TEXT NOT NULL,
    kind       TEXT NOT NULL,
    data       TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS checkins (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    mood       INTEGER NOT NULL,   -- 1 (low) .. 5 (great)
    energy     INTEGER,            -- 1 .. 5
    note       TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS goals (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    area       TEXT NOT NULL,      -- life area (see models.LifeArea)
    title      TEXT NOT NULL,
    target     TEXT,
    progress   REAL NOT NULL DEFAULT 0,   -- 0 .. 1
    status     TEXT NOT NULL DEFAULT 'active',  -- active | completed | abandoned
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS habits (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    name       TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS habit_logs (
    habit_id   TEXT NOT NULL REFERENCES habits(id),
    day        TEXT NOT NULL,      -- YYYY-MM-DD
    PRIMARY KEY (habit_id, day)
);

-- Proactive nudges generated from check-ins, goals, streaks, and context.
CREATE TABLE IF NOT EXISTS insights (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    area       TEXT,
    kind       TEXT NOT NULL,      -- praise | alert | suggestion | milestone
    message    TEXT NOT NULL,
    source     TEXT,
    created_at TEXT NOT NULL
);

-- Login sessions: guidance stays consistent across sessions and devices
-- (the remembered state is per user, so any device resumes the same thread).
CREATE TABLE IF NOT EXISTS sessions (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    device     TEXT,            -- smart_watch | phone | stationary | …
    started_at TEXT NOT NULL,
    ended_at   TEXT
);

-- Keys JIM has stored in the tandem PDI vault, tracked so that
-- DELETE /data/{user_id} can purge the vault as well.
CREATE TABLE IF NOT EXISTS vault_keys (
    user_id TEXT NOT NULL REFERENCES users(id),
    key     TEXT NOT NULL,
    PRIMARY KEY (user_id, key)
);

CREATE TABLE IF NOT EXISTS coach_messages (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    area       TEXT NOT NULL,
    role       TEXT NOT NULL,      -- user | coach
    content    TEXT NOT NULL,
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
