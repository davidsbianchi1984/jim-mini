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
    provider_consent   INTEGER NOT NULL DEFAULT 0,  -- allow provider-portal summary
    cloud_contribution INTEGER NOT NULL DEFAULT 0,  -- opt-in: anonymized outcomes improve the cloud model
    devices            TEXT NOT NULL DEFAULT '[]',  -- e.g. ["smart_watch","phone"]
    personality        TEXT,                        -- counselor adaptation prefs
    sensitivity        TEXT NOT NULL DEFAULT 'balanced', -- cautious | balanced | assertive
    created_at         TEXT NOT NULL
);

-- Rolling per-metric baselines (EMA). Detection thresholds float with the
-- person: a resting-state sample with no active condition nudges the baseline
-- (value ← value + α·(sample − value), α≈0.05). Until enough resting samples
-- have accrued the baseline is provisional and the enrolled/default seed is
-- used instead.
CREATE TABLE IF NOT EXISTS baselines (
    user_id    TEXT NOT NULL REFERENCES users(id),
    metric     TEXT NOT NULL,       -- heart_rate | hrv | respiratory_rate | ...
    value      REAL NOT NULL,       -- current EMA estimate
    samples    INTEGER NOT NULL DEFAULT 0,  -- resting samples folded in
    updated_at TEXT NOT NULL,
    PRIMARY KEY (user_id, metric)
);

-- Capability tokens. A user proves "I am this user" by holding the token
-- minted at enrollment (returned once). Every /{user_id} surface — biometric
-- monitoring, journal, provider portal, erasure — is PHI, so all of them are
-- gated behind it. Only the SHA-256 hash is stored.
CREATE TABLE IF NOT EXISTS api_tokens (
    token_hash TEXT PRIMARY KEY,
    role       TEXT NOT NULL,   -- user
    subject_id TEXT NOT NULL,   -- user_id
    created_at TEXT NOT NULL
);

-- Shareable Medical ID card: an opaque, rotatable token behind a printable /
-- lock-screen QR code. Scanning it resolves to the user's condition-level
-- Medical ID *without* their auth token — the phone is locked in an emergency,
-- so the card itself is the (revocable) credential. Only the hash is stored.
CREATE TABLE IF NOT EXISTS medical_cards (
    user_id    TEXT PRIMARY KEY REFERENCES users(id),
    token_hash TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
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
    user_id              TEXT PRIMARY KEY REFERENCES users(id),
    qrme_interactor_id   TEXT NOT NULL,
    qrme_interactor_token TEXT,     -- QRME interactor capability token: lets
                                    -- JIM read back the shared thread's memory
                                    -- for cross-device/-product continuity
    created_at           TEXT NOT NULL
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

-- Safe knowledge excursions. When the Guardian needs to study an unfamiliar
-- condition or topic, it gathers general knowledge from a SANITIZED brief (the
-- user's name and emergency contact redacted). ``brief`` is exactly what could
-- leave; ``left_host`` records whether anything did (offline: never).
CREATE TABLE IF NOT EXISTS excursions (
    id           TEXT PRIMARY KEY,
    user_id      TEXT NOT NULL REFERENCES users(id),
    topic        TEXT NOT NULL,       -- stays local
    brief        TEXT NOT NULL,       -- sanitized outbound query
    redactions   INTEGER NOT NULL DEFAULT 0,
    left_host    INTEGER NOT NULL DEFAULT 0,
    findings     TEXT,
    learned      INTEGER NOT NULL DEFAULT 0,
    created_at   TEXT NOT NULL
);

-- Connected-app connectors. Each links a user to an AI-integrated app from the
-- catalog (Apple Photos, Google Calendar, Microsoft 365, Canva, …). The
-- Guardian's agents then collect context in, act on the app, or produce media.
CREATE TABLE IF NOT EXISTS app_connectors (
    id           TEXT PRIMARY KEY,
    user_id      TEXT NOT NULL REFERENCES users(id),
    provider     TEXT NOT NULL,   -- apple | google | microsoft | canva
    app          TEXT NOT NULL,
    label        TEXT NOT NULL,
    capabilities TEXT NOT NULL DEFAULT '[]',
    directions   TEXT NOT NULL DEFAULT '[]',
    status       TEXT NOT NULL DEFAULT 'active',
    collected    INTEGER NOT NULL DEFAULT 0,
    actions      INTEGER NOT NULL DEFAULT 0,
    created_at   TEXT NOT NULL
);

-- Social-platform connections. collect pulls the account's posts in as
-- consented context that informs guidance; publish shares an update on the
-- platform, reachable by a QR beacon.
CREATE TABLE IF NOT EXISTS social_connections (
    id          TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL REFERENCES users(id),
    platform    TEXT NOT NULL,   -- instagram | x | tiktok | facebook | linkedin | youtube | reddit | threads
    direction   TEXT NOT NULL,   -- collect | publish
    handle      TEXT,
    scope       TEXT NOT NULL DEFAULT '[]',
    status      TEXT NOT NULL DEFAULT 'active',  -- active | revoked
    collected   INTEGER NOT NULL DEFAULT 0,
    published   INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL
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

-- Free-form journal entries (vaulted when PDI tandem is on).
CREATE TABLE IF NOT EXISTS journal (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    text       TEXT,            -- NULL when sealed in the PDI vault
    created_at TEXT NOT NULL
);

-- User feedback on guidance/coaching — the continuous-improvement loop.
CREATE TABLE IF NOT EXISTS feedback (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    rating     TEXT NOT NULL,   -- up | down
    note       TEXT,
    created_at TEXT NOT NULL
);

-- Proactive nudges generated from check-ins, goals, streaks, and context.
CREATE TABLE IF NOT EXISTS insights (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    area       TEXT,
    kind       TEXT NOT NULL,      -- praise | alert | suggestion | milestone | forecast
    message    TEXT NOT NULL,
    source     TEXT,
    created_at TEXT NOT NULL
);

-- Numeric trend points for predictive early warnings. Context payloads are
-- vaulted under PDI, so prediction keeps only bare numbers locally (a value
-- and a metric name — no categories, notes, or payloads): enough to see a
-- slope forming, nothing worth stealing.
CREATE TABLE IF NOT EXISTS trend_points (
    user_id    TEXT NOT NULL REFERENCES users(id),
    metric     TEXT NOT NULL,      -- sleep_hours | spend_amount | ...
    value      REAL NOT NULL,
    created_at TEXT NOT NULL
);

-- Physical embodiments (clause 16): wearables, stationary systems, and
-- networked autonomous devices — with transport (e.g. Bluetooth), an
-- optional on-device LLM, and links between devices (watch → phone).
CREATE TABLE IF NOT EXISTS devices (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    name       TEXT NOT NULL,   -- smart_watch | kitchen_console | helper_bot …
    kind       TEXT NOT NULL,   -- wearable | stationary | autonomous
    transport  TEXT,            -- bluetooth | wifi | cellular | wired
    has_llm    INTEGER NOT NULL DEFAULT 0,  -- device carries its own LLM
    linked_to  TEXT,            -- name of the device it relays through
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

-- Per-user LLM provider preference. 'auto' (or a missing row) defers to the
-- platform default; any other value is a jim.llm registry name the user picked
-- (anthropic | openai | grok | perplexity | gemini | stub).
CREATE TABLE IF NOT EXISTS model_prefs (
    user_id    TEXT PRIMARY KEY REFERENCES users(id),
    provider   TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS language_prefs (
    user_id    TEXT PRIMARY KEY REFERENCES users(id),
    language   TEXT NOT NULL,   -- jim.i18n.SUPPORTED code, e.g. "es"
    mode       TEXT NOT NULL DEFAULT 'pre',  -- pre | on_demand
    updated_at TEXT NOT NULL
);

-- Robot helpers bound to a user (see jim/robotics.py for the catalog). Each
-- binding also registers a devices row, so escalation alerts dispatch to the
-- robot like any other device; the device row's name mirrors the robot's.
-- Family: the recorded guardian/child relationship behind guardian-consented
-- enrollment. Oversight is sized by the child's age (full under 13,
-- alerts_only 13-17) and ends by itself at 18.
CREATE TABLE IF NOT EXISTS guardian_links (
    guardian_id  TEXT NOT NULL REFERENCES users(id),
    child_id     TEXT NOT NULL REFERENCES users(id),
    relationship TEXT NOT NULL DEFAULT 'parent',  -- parent | legal_guardian
    oversight    TEXT NOT NULL,                   -- full | alerts_only (at setup)
    paused       INTEGER NOT NULL DEFAULT 0,      -- holds everyday guidance only
    quiet_start  TEXT,                            -- HH:MM (may wrap midnight)
    quiet_end    TEXT,
    created_at   TEXT NOT NULL,
    PRIMARY KEY (guardian_id, child_id)
);

CREATE TABLE IF NOT EXISTS waivers (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    kind       TEXT NOT NULL,   -- autonomous_resuscitation
    signature  TEXT NOT NULL,   -- typed legal name
    signed_at  TEXT NOT NULL,
    revoked    INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS robots (
    id           TEXT PRIMARY KEY,
    user_id      TEXT NOT NULL REFERENCES users(id),
    model        TEXT NOT NULL,   -- robotics.BY_KEY key, e.g. neo, saros_20
    name         TEXT NOT NULL,   -- household name, e.g. "hall NEO"
    llm_provider TEXT,            -- jim.llm registry name loaded onboard
    status       TEXT NOT NULL DEFAULT 'docked',  -- docked | active | responding
    created_at   TEXT NOT NULL
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
        conn.execute("PRAGMA journal_mode=WAL")  # concurrent readers
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
