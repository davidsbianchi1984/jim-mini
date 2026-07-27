"""SQLite persistence for JIM-mini (independent of QRME's database)."""

from __future__ import annotations

import os
import sqlite3
import threading
import uuid
from datetime import datetime, timezone

_SCHEMA = """
-- How far somebody has got through the Guardian's walkthrough. One row per
-- step rather than a cursor, so a learner who skipped ahead and came back is
-- not told they finished things they never saw.
CREATE TABLE IF NOT EXISTS tutorial_progress (
    learner_id TEXT NOT NULL,
    lesson     TEXT NOT NULL,
    done_at    TEXT NOT NULL,
    PRIMARY KEY (learner_id, lesson)
);

CREATE TABLE IF NOT EXISTS users (
    id                 TEXT PRIMARY KEY,
    display_name       TEXT NOT NULL,
    birthdate          TEXT,
    terms_consent      INTEGER NOT NULL DEFAULT 0,
    terms_version      TEXT,             -- ToS version accepted at enrollment
    terms_accepted_at  TEXT,
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

-- "Help us improve": product feedback anyone can send about the app itself
-- (distinct from the guidance `feedback` table above). Submitter is a
-- role:subject when authenticated, else 'anonymous'; a submitter sees only
-- their own words, everyone the aggregate tally.
CREATE TABLE IF NOT EXISTS improvements (
    id         TEXT PRIMARY KEY,
    submitter  TEXT NOT NULL DEFAULT 'anonymous',
    category   TEXT NOT NULL,          -- idea | improvement | bug | praise | other
    message    TEXT NOT NULL,
    rating     INTEGER,                -- optional 1..5 satisfaction
    status     TEXT NOT NULL DEFAULT 'received',   -- received | reviewed | planned | shipped
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

-- Everything this deployment has ever sent to the Cloud Model Gateway's
-- contribution intake, and the exact payload it sent.
--
-- Contribution used to be fire-and-forget: `cloud.contribute` returned a bool
-- and nothing was written down. That made two promises unkeepable. The
-- settings screen already offered "preview before it leaves", and there was
-- nothing to show; and consent described as revocable could only ever stop
-- *future* sends, because nothing identified what had already gone.
--
-- `ref` is the opaque handle sent alongside the payload. It carries no
-- identity — only this local table maps it back to a user — so revocation can
-- name items at the gateway without deanonymizing the person revoking.
CREATE TABLE IF NOT EXISTS contribution_log (
    ref            TEXT PRIMARY KEY,   -- opaque id sent with the payload
    user_id        TEXT NOT NULL REFERENCES users(id),
    payload        TEXT NOT NULL,      -- the exact JSON that was sent
    revoked        INTEGER NOT NULL DEFAULT 0,
    contributed_at TEXT NOT NULL
);

-- Multi-step work handed to a QRME specialist (see jim/handoff.py). The
-- workflow itself lives in QRME — this is JIM's handle on it.
--
-- Status only, never the working memory. The drafts a specialist produces stay
-- in QRME under its own moderation and the user's capability token; copying
-- them here would quietly make JIM a second store of somebody's generated
-- health correspondence, which is the opposite of what the tandem is for.
-- The town a referral searches near. Coarse and self-declared, and
-- deliberately *not* the consented `location` source: live position is a
-- stream, and matching a clinic needs a place name. A user typing "Leeds" once
-- is a smaller disclosure than a product inferring it continuously.
-- A wearable whose microphone the Guardian may borrow while the phone's is
-- occupied (see jim/mic.py). One per user: a second ear is a second ear, and
-- a list of them would be a room full of microphones by another name.
--
-- Attaching is not listening. This row says *which* device may be lent; the
-- lending is a `mic_sessions` row and needs a reason.
CREATE TABLE IF NOT EXISTS mic_channels (
    user_id     TEXT PRIMARY KEY REFERENCES users(id),
    device_id   TEXT NOT NULL REFERENCES devices(id),
    device_name TEXT NOT NULL,
    -- watch | earbuds | lapel | clip_on | … see jim/mic.py:MIC_TYPES. Stored
    -- because *what kind of microphone it is* is the thing that decided it
    -- could be lent, and that decision should be readable later.
    mic_type    TEXT NOT NULL,
    -- How wide channel 2 listens: near_field | normal | wide. Named `gain`
    -- rather than `sensitivity` because `users.sensitivity` is already the
    -- escalation dial, and two settings sharing a name is how somebody
    -- eventually turns the wrong one.
    --
    -- Not an audio preference. It is the mechanism behind "the agent hears
    -- you, not your call": a channel wide enough to pick up a room picks up
    -- the other party bleeding from an earpiece too. `mic.effective_gain`
    -- caps it at near_field whenever another person's voice is in the air, so
    -- the promise is a fact about capture width rather than a policy.
    gain        TEXT NOT NULL DEFAULT 'near_field',
    created_at  TEXT NOT NULL
);

-- Each period the agent actually held that microphone.
--
-- `route` is how the occupying call was being heard, and it is stored rather
-- than checked-and-forgotten because it is the whole justification: on an
-- earpiece the wearable hears the wearer, on speaker it hears the other party
-- as well — someone who is not a user here and was never asked.
--
-- Rows are never deleted on release. A listening permission that leaves no
-- trace is one nobody can audit, and this is the permission people most want
-- to check up on.
CREATE TABLE IF NOT EXISTS mic_sessions (
    id            TEXT PRIMARY KEY,
    user_id       TEXT NOT NULL REFERENCES users(id),
    device_id     TEXT NOT NULL,
    device_name   TEXT NOT NULL,
    reason        TEXT NOT NULL,   -- voice_call | video_call | recording | …
    route         TEXT NOT NULL,   -- earpiece | headset | bluetooth_headset
    mic_type      TEXT NOT NULL DEFAULT '',
    -- What it actually ran at, which is not always what the user asked for.
    gain          TEXT NOT NULL DEFAULT 'near_field',
    -- What was carrying the occupying call. Recorded because once anything
    -- worn can be channel 2, the two can collide: earbuds on a call are the
    -- *occupied* microphone, not a spare one.
    primary_device TEXT,
    started_at    TEXT NOT NULL,
    ended_at      TEXT,
    ended_because TEXT
);

CREATE TABLE IF NOT EXISTS user_locality (
    user_id    TEXT PRIMARY KEY REFERENCES users(id),
    locality   TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Referrals prepared through the Guardian. JIM keeps the handle only: the
-- summary, the signature and the one-time link all live in QRME, because the
-- assertion that releases them is against QRME's relying party and must
-- travel from the user's device to QRME without passing through here.
CREATE TABLE IF NOT EXISTS referral_requests (
    id               TEXT PRIMARY KEY,
    user_id          TEXT NOT NULL REFERENCES users(id),
    condition        TEXT NOT NULL,
    provider_id      TEXT NOT NULL,
    qrme_referral_id TEXT,
    created_at       TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS specialist_tasks (
    id               TEXT PRIMARY KEY,
    user_id          TEXT NOT NULL REFERENCES users(id),
    qrme_profile_id  TEXT NOT NULL,
    qrme_workflow_id TEXT NOT NULL,
    goal             TEXT NOT NULL,
    status           TEXT NOT NULL,   -- mirrors QRME's; refreshed on read
    created_at       TEXT NOT NULL,
    updated_at       TEXT NOT NULL
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

-- Care beacons (jim/beacons.py): a printed code on the things around a watched
-- person — a fridge door, a wristband, a walker — that a stranger can scan to
-- raise whoever is watching. Distinct from medical_cards: that card travels
-- with the person and is read, this code stays with a place and is *rung*.
-- Site beacons belong to a workplace deployment rather than a home; see
-- jim/relay.py. Full reasoning in docs/beacons.md.
CREATE TABLE IF NOT EXISTS care_beacons (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    label      TEXT NOT NULL,   -- the owner's own filing note; never shown
    placement  TEXT,            -- free text, e.g. "fridge door"; never shown
    kind       TEXT NOT NULL DEFAULT 'personal',  -- personal | site
    scans      INTEGER NOT NULL DEFAULT 0,
    active     INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);

-- An alarm raised from a beacon by a passer-by. `state` is open until the
-- owner (or a responder) clears it. Within the cooldown a second alarm
-- attaches its message to the open one rather than raising a new one or being
-- dropped — two people finding the same person must not race, and the second
-- must never be discarded.
CREATE TABLE IF NOT EXISTS beacon_alarms (
    id          TEXT PRIMARY KEY,
    beacon_id   TEXT NOT NULL REFERENCES care_beacons(id),
    user_id     TEXT NOT NULL REFERENCES users(id),
    messages    TEXT NOT NULL DEFAULT '[]',  -- every finder's words, in order
    state       TEXT NOT NULL DEFAULT 'open',  -- open | cleared
    tier        TEXT,            -- the escalation tier it landed on
    accepted_by TEXT,            -- the roster entry that took it (site beacons)
    created_at  TEXT NOT NULL,
    cleared_at  TEXT
);

-- An attempt to reach one responder about one alarm (see jim/notify.py). Its
-- own table rather than columns on the alarm, because working a rota means
-- several attempts per alarm, and the list somebody needs in the morning is
-- "which pages never landed" across all of them.
CREATE TABLE IF NOT EXISTS relay_pages (
    id          TEXT PRIMARY KEY,
    alarm_id    TEXT NOT NULL REFERENCES beacon_alarms(id),
    user_id     TEXT NOT NULL REFERENCES users(id),
    responder   TEXT NOT NULL,
    role        TEXT NOT NULL,
    on_shift    INTEGER NOT NULL DEFAULT 1,  -- was the rota actually covering?
    state       TEXT NOT NULL,   -- queued (no channel) | sent | failed
    attempts    INTEGER NOT NULL DEFAULT 0,
    last_error  TEXT,
    created_at  TEXT NOT NULL,
    sent_at     TEXT
);

-- Clinical captures: a photograph, clip or sound of the body (jim/capture.py).
--
-- Metadata only. The pixels live in the PDI vault under `vault_key`, and there
-- is deliberately no column that could hold them — a schema with a `content`
-- field here is one somebody eventually writes to, and the thing they would be
-- writing is an unencrypted photograph of somebody's skin.
--
-- `digest` and `bytes` describe what was sealed so a clinician can tell that
-- what they opened is what was taken. `stripped` records which metadata
-- segments were removed (EXIF/GPS among them) rather than claiming none
-- existed.
--
-- `deleted_at` is a tombstone: the vault record is destroyed, the row survives
-- so a clinician who was shown something sees it was withdrawn rather than
-- finding a dangling reference.
CREATE TABLE IF NOT EXISTS captures (
    id          TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL REFERENCES users(id),
    kind        TEXT NOT NULL,          -- photo | video | audio
    site        TEXT NOT NULL,          -- capture.SITES key
    provenance  TEXT NOT NULL,          -- captured | imported
    note        TEXT,
    condition   TEXT,
    intimate    INTEGER NOT NULL DEFAULT 0,
    vault_key   TEXT NOT NULL,
    digest      TEXT NOT NULL,          -- sha256 of the sealed bytes
    bytes       INTEGER NOT NULL,
    stripped    TEXT NOT NULL DEFAULT '[]',   -- JSON array
    captured_at TEXT NOT NULL,
    released_at TEXT,
    deleted_at  TEXT
);
CREATE INDEX IF NOT EXISTS captures_by_user ON captures (user_id, captured_at);

-- Where the helper dock sits and what it is showing (see jim/dock.py).
-- Preferences only; the pane shows and routes and cannot be granted anything,
-- because there is nothing to grant.
CREATE TABLE IF NOT EXISTS dock_prefs (
    user_id    TEXT PRIMARY KEY REFERENCES users(id),
    corner     TEXT NOT NULL DEFAULT 'bottom_right',
    state      TEXT NOT NULL DEFAULT 'handle',
    face       TEXT NOT NULL DEFAULT 'helper',
    faces      TEXT NOT NULL,                        -- JSON array
    updated_at TEXT NOT NULL
);

-- What a person has paid for (see jim/tiers.py). Keyed on the user, who here
-- *is* the account — unlike QRME, where an owner token's subject is a profile.
--
-- One live row per account, enforced by ending the previous one rather than by
-- a unique index, so the history survives a change of plan.
--
-- Billing is simulated: there is no processor and no token, and the row is the
-- subscription. Nothing on the emergency path consults this table at all.
CREATE TABLE IF NOT EXISTS memberships (
    id         TEXT PRIMARY KEY,
    account_id TEXT NOT NULL,
    plan       TEXT NOT NULL,          -- basic | pro
    started_at TEXT NOT NULL,
    ended_at   TEXT
);
CREATE INDEX IF NOT EXISTS memberships_live
    ON memberships (account_id, ended_at);

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
