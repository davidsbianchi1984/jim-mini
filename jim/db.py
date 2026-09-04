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
    -- A pseudonym when `anonymous` is set (jim/identity.py): the app never
    -- learns the real name in that case. `legal_name` is what the user chose
    -- to leave for emergency briefings only, and may be NULL even then.
    display_name       TEXT NOT NULL,
    anonymous          INTEGER NOT NULL DEFAULT 0,
    legal_name         TEXT,
    birthdate          TEXT,
    terms_consent      INTEGER NOT NULL DEFAULT 0,
    terms_version      TEXT,             -- ToS version accepted at enrollment
    terms_accepted_at  TEXT,
    guardian_consent   INTEGER NOT NULL DEFAULT 0,
    emergency_name     TEXT,
    emergency_phone    TEXT,
    -- The far end of the escalation ladder: an address a *person* reads.
    -- The phone above is what a first responder dials; this is what JIM
    -- itself can actually reach (jim/farend.py). Without it, notify_contact
    -- is words.
    emergency_email    TEXT,
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
    forgot_at          TEXT,             -- when a forgetting door last touched
                                         -- this person; letters built before
                                         -- this rebuild (jim/letter.py shelf)
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

-- Sign-in accounts. An account is an email + password that *owns* a user;
-- the user (and its capability token) is only created once the email is
-- verified, so a mistyped address never grows a record nobody can reach.
-- Password: PBKDF2-HMAC-SHA256, per-account salt; only hashes at rest.
CREATE TABLE IF NOT EXISTS accounts (
    id              TEXT PRIMARY KEY,
    email           TEXT NOT NULL UNIQUE,   -- normalized lower-case
    password_hash   TEXT NOT NULL,
    salt            TEXT NOT NULL,
    pending_profile TEXT,                   -- Enroll payload, until verified
    user_id         TEXT,                   -- set at verification
    verified_at     TEXT,
    created_at      TEXT NOT NULL
);

-- One row per attempted "Sign in with ..." (jim/oauth.py). enroll parks the
-- Guardian's signup payload for a brand-new account; result holds the
-- finished session until the console claims it, exactly once.
CREATE TABLE IF NOT EXISTS oauth_states (
    state        TEXT PRIMARY KEY,
    provider     TEXT NOT NULL,
    redirect_uri TEXT NOT NULL,
    enroll       TEXT,
    result       TEXT,
    claimed_at   TEXT,
    created_at   TEXT NOT NULL
);

-- How this deployment speaks and listens (jim/voice.py). One row, set from
-- the Settings screen. Without it the app uses the device's own voice and
-- recogniser, which need no account and no key.
CREATE TABLE IF NOT EXISTS voice_settings (
    id            INTEGER PRIMARY KEY CHECK (id = 1),
    provider      TEXT NOT NULL,          -- elevenlabs | openai | device
    api_key       TEXT,
    voice_id      TEXT,
    speak_replies INTEGER NOT NULL DEFAULT 1,
    updated_at    TEXT NOT NULL
);

-- Personal drift bands: how far from *this person's own* baseline a metric
-- may wander before it is worth a check-in. One row per user per metric,
-- absent until they adjust it (jim/bands.py supplies the default). A band
-- has a width and two independent edges, because which direction matters
-- differs by metric — HRV falling and heart rate climbing are both news.
CREATE TABLE IF NOT EXISTS drift_bands (
    user_id    TEXT NOT NULL REFERENCES users(id),
    metric     TEXT NOT NULL,
    margin     REAL NOT NULL,
    watch_high INTEGER NOT NULL DEFAULT 1,
    watch_low  INTEGER NOT NULL DEFAULT 1,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (user_id, metric)
);

-- The medicine cabinet (jim/meds.py): what the user takes, in their own
-- words — name, dose, why — and when. JIM is not a pharmacist: it tracks
-- what it is told, it never claims to check interactions, and a missed
-- dose earns a check-in, never an alarm. ``schedule`` is JSON: either
-- {"times": ["08:00","20:00"]} or {"as_needed": true, "max_per_day": N}.
CREATE TABLE IF NOT EXISTS medications (
    id          TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL REFERENCES users(id),
    name        TEXT NOT NULL,
    dose        TEXT NOT NULL,   -- "10 mg", the user's words
    purpose     TEXT,            -- why, in the user's words
    schedule    TEXT NOT NULL,
    critical    INTEGER NOT NULL DEFAULT 0,  -- missing it is worth a check-in
    notes       TEXT,
    archived_at TEXT,
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

-- One row per answer to one slot on one day (or one as-needed take), so
-- "did I take it?" has exactly one answer that can be corrected — logging
-- again for the same slot replaces, it does not duplicate.
CREATE TABLE IF NOT EXISTS med_logs (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    med_id     TEXT NOT NULL REFERENCES medications(id),
    action     TEXT NOT NULL,   -- taken | skipped
    slot       TEXT,            -- schedule time answered ("08:00"); NULL = as-needed
    on_date    TEXT NOT NULL,   -- YYYY-MM-DD the slot belongs to
    note       TEXT,            -- "with food" / "felt dizzy, skipped"
    created_at TEXT NOT NULL
);

-- The vigil (jim/vigil.py): a steward who is told when the signals STOP.
-- Every other alarm in the product fires on a reading; this one fires on
-- the absence of readings — the watch that went quiet, the check-in that
-- never came. One row per user; silence is measured against the events
-- table, so any sign of life resets it without bookkeeping.
CREATE TABLE IF NOT EXISTS vigils (
    user_id         TEXT PRIMARY KEY REFERENCES users(id),
    steward_name    TEXT NOT NULL,
    steward_channel TEXT NOT NULL,   -- email or phone, the user's words
    quiet_days      REAL NOT NULL DEFAULT 3,
    note            TEXT,            -- what the steward is told, pre-written
    enabled         INTEGER NOT NULL DEFAULT 1,
    tripped_at      TEXT,
    resolved_at     TEXT,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

-- The user-specific model artifact (jim/adaptation.py, clause 11).
--
-- One row per user: the adaptation profile derived offline from that user's
-- own stored history, its evidence count and earned confidence, and the vault
-- key when a PDI tandem sealed it. The profile conditions prompts; it is not
-- a weight file, and `profile.method` says so in its own words.
-- The offline fine-tune (jim/finetune.py). Distinct from `user_models` beside
-- it and deliberately a separate table: that one holds a *profile* that
-- conditions a prompt, this one holds *weights* trained on this user's own
-- answered follow-ups. Confusing the two is the misreading the whole module
-- is written to prevent, and one table with a "kind" column would have
-- invited it. `active` is off on insert: training and using are two decisions.
CREATE TABLE IF NOT EXISTS user_finetunes (
    user_id    TEXT PRIMARY KEY REFERENCES users(id),
    version    INTEGER NOT NULL,
    backend    TEXT NOT NULL,       -- local-logistic | lora
    artifact   TEXT NOT NULL,       -- JSON: weights, vocab, provenance
    examples   INTEGER NOT NULL,
    digest     TEXT NOT NULL,       -- sha256 over the artifact
    pdi_key    TEXT,                -- set when sealed in the user's vault
    active     INTEGER NOT NULL DEFAULT 0,
    trained_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_models (
    user_id        TEXT PRIMARY KEY REFERENCES users(id),
    version        INTEGER NOT NULL,
    profile        TEXT NOT NULL,       -- JSON
    evidence_items INTEGER NOT NULL DEFAULT 0,
    confidence     REAL NOT NULL DEFAULT 0,
    pdi_key        TEXT,                -- set when sealed in the vault
    rebuilt_at     TEXT NOT NULL
);

-- The latent continuity vector (jim/continuity.py).
--
-- One row per user: six named 0..1 dimensions, EMA-updated at the three
-- moments a signal arrives — a check-in logged, a coach turn, an answered
-- follow-up. It is what survives between sessions, and it is the edge that
-- `user_models` above was missing: that profile is rebuilt by hand, and until
-- this table existed nothing in the product moved between rebuilds.
--
-- The row carries counts and timings only. No message text, no condition
-- name, nothing the person wrote. `test_the_vector_carries_no_content` holds
-- it there.
CREATE TABLE IF NOT EXISTS user_continuity (
    user_id      TEXT PRIMARY KEY REFERENCES users(id),
    vector       TEXT NOT NULL,        -- JSON, six named floats
    observations INTEGER NOT NULL DEFAULT 0,
    version      INTEGER NOT NULL DEFAULT 1,
    updated_at   TEXT NOT NULL
);

-- Did the counseling actually work? (jim/followup.py)
--
-- Spec [0039] closes the loop the product was missing: "If the counseling is
-- effective in managing the known condition … resume monitoring. If the
-- counseling provided is not effective, the personal guidance system may
-- alert a person to provide live assistance to the user … by connecting the
-- user to a support person associated with the personal guidance system or
-- by connecting the user with an emergency contact."
--
-- One row per delivered guidance: opened when guidance goes out, answered
-- when the user says whether it helped. `helped=0` re-runs the escalation
-- ladder with the ineffective-guidance rung applied, and the tier it lands
-- on is recorded here so the decision can be replayed later.
CREATE TABLE IF NOT EXISTS guidance_followups (
    id           TEXT PRIMARY KEY,
    user_id      TEXT NOT NULL REFERENCES users(id),
    condition    TEXT NOT NULL,
    severity     TEXT NOT NULL,
    asked_at     TEXT NOT NULL,
    answered_at  TEXT,
    helped       INTEGER,             -- NULL until answered
    note         TEXT,                -- the user's own words, optional
    escalated_to TEXT                 -- tier reached when it did not help
);

-- The crash watch (jim/crashwatch.py): the vigil's acute sibling. Armed in
-- advance by the user; a critical reading opens a question, N unanswered
-- attempts become a trip that contacts the trusted person (and, only if
-- consented, records an emergency-services dispatch request).
CREATE TABLE IF NOT EXISTS crash_watches (
    user_id           TEXT PRIMARY KEY REFERENCES users(id),
    trusted_name      TEXT NOT NULL,
    trusted_channel   TEXT NOT NULL,  -- email or phone, the user's words
    attempts          INTEGER NOT NULL DEFAULT 3,
    window_minutes    REAL NOT NULL DEFAULT 5,
    contact_ems       INTEGER NOT NULL DEFAULT 0,  -- pre-authorized, or never
    enabled           INTEGER NOT NULL DEFAULT 1,
    concern_opened_at TEXT,           -- a question is open
    concern           TEXT,           -- which condition opened it
    attempt           INTEGER NOT NULL DEFAULT 0,
    deadline_at       TEXT,           -- when the current attempt expires
    tripped_at        TEXT,
    resolved_at       TEXT,
    created_at        TEXT NOT NULL,
    updated_at        TEXT NOT NULL
);

-- The reach-out cascade: JIM calling emergency contacts in turn, and the
-- calls it placed. One cascade row holds the ordered attempt; each call row
-- is one contact tried, its consent choice, and the conversation transcript.
CREATE TABLE IF NOT EXISTS reachouts (
    id            TEXT PRIMARY KEY,
    user_id       TEXT NOT NULL REFERENCES users(id),
    situation     TEXT NOT NULL,   -- JSON: what JIM is calling about
    life_threat   INTEGER NOT NULL DEFAULT 0,  -- may the held 911 rung be reached
    status        TEXT NOT NULL,   -- calling | reached | exhausted
    idx           INTEGER NOT NULL DEFAULT 0,  -- which contact is current
    contacts      TEXT NOT NULL,   -- JSON: the ordered [{name, channel}] tried
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS reachout_calls (
    id            TEXT PRIMARY KEY,
    reachout_id   TEXT NOT NULL REFERENCES reachouts(id),
    user_id       TEXT NOT NULL,
    name          TEXT NOT NULL,
    channel       TEXT NOT NULL,
    status        TEXT NOT NULL,   -- ringing | consented | talking | reached | declined | unreached | unplaced
    transcript    TEXT NOT NULL DEFAULT '[]',  -- JSON: the conversation turns
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);
-- Numbers that pressed do-not-call-again. Checked before every reach-out so
-- a person who opted out is never rung for this user again.
CREATE TABLE IF NOT EXISTS do_not_call (
    user_id       TEXT NOT NULL,
    channel       TEXT NOT NULL,
    at            TEXT NOT NULL,
    PRIMARY KEY (user_id, channel)
);
-- What the phone line said about a leg, verbatim and in order (jim/telephony.py,
-- jim/reachout.py): a pickup, how it ended, how long it ran. The record the
-- reached-or-unreached decision is made from, kept beside the decision so a
-- reviewer can see both.
CREATE TABLE IF NOT EXISTS reachout_call_events (
    id            TEXT PRIMARY KEY,
    call_id       TEXT NOT NULL REFERENCES reachout_calls(id),
    user_id       TEXT NOT NULL,
    event         TEXT NOT NULL,   -- answered | completed | voicemail | no-answer | busy | failed | canceled
    seconds       INTEGER NOT NULL DEFAULT 0,
    detail        TEXT NOT NULL DEFAULT '',
    note          TEXT NOT NULL DEFAULT '',  -- 'late' when the leg had already ended
    at            TEXT NOT NULL
);

-- The moderated mailbox (jim/mailbox.py): the coach agent's correspondence,
-- and — when this seam is lifted into QRME — a synthetic profile's, answering
-- in its profession. A thread is one conversation with one correspondent;
-- every message the agent would send is composed as a DRAFT and held for a
-- person to approve, edit, or discard before a byte leaves. Nothing
-- auto-sends: moderation is the gate, the same shape the 911 dialer holds its
-- send with (jim/dialer.py). `role` carries the voice (coach, or a profession).
CREATE TABLE IF NOT EXISTS mail_threads (
    id            TEXT PRIMARY KEY,
    user_id       TEXT NOT NULL REFERENCES users(id),
    role          TEXT NOT NULL,   -- coach | <a profile's profession>
    correspondent TEXT NOT NULL,   -- the email address on the other end
    subject       TEXT NOT NULL,
    status        TEXT NOT NULL,   -- open | closed
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS mail_messages (
    id            TEXT PRIMARY KEY,
    thread_id     TEXT NOT NULL REFERENCES mail_threads(id),
    user_id       TEXT NOT NULL,
    direction     TEXT NOT NULL,   -- inbound | outbound
    state         TEXT NOT NULL,   -- received | draft | sent | staged | discarded
    from_addr     TEXT NOT NULL DEFAULT '',
    to_addr       TEXT NOT NULL DEFAULT '',
    subject       TEXT NOT NULL DEFAULT '',
    body          TEXT NOT NULL,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);

-- The offline training corpus (jim/corpus.py): every exchange the agents have
-- — JIM, the coach, the mailbox, the reach-out cascade — banked as a training
-- example at the one place they all pass through (jim.llm.generate_for_user),
-- so the local model trained from it grows able enough to run offline. The
-- person owns it: capture is consented (corpus_consent), off stops it, purge
-- clears it, and a full account erase reaches it with no line of its own —
-- this table is user_id-scoped and jim/life.py reads the schema.
CREATE TABLE IF NOT EXISTS training_examples (
    id            TEXT PRIMARY KEY,
    user_id       TEXT NOT NULL REFERENCES users(id),
    source        TEXT NOT NULL DEFAULT '',  -- coach | mailbox | reachout | ...
    provider      TEXT NOT NULL DEFAULT '',  -- who generated it (claude, stub, ...)
    system        TEXT NOT NULL,
    prompt        TEXT NOT NULL,
    completion    TEXT NOT NULL,
    archived_at   TEXT,                       -- when sealed to the vault, else NULL
    created_at    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS corpus_consent (
    user_id       TEXT PRIMARY KEY REFERENCES users(id),
    enabled       INTEGER NOT NULL DEFAULT 1,
    updated_at    TEXT NOT NULL
);

-- App edits (jim/appedits.py): a person's proposed change to the app itself.
-- Two lanes. On a self-hosted server the person has free rein and the edit
-- is approved on arrival; on the hosted cloud it is HELD for company
-- oversight to approve or reject. Either way an approved edit is queued to
-- ride the next publish-merge — this seam never writes to the running code
-- or deploys; the merge stays a reviewed human step (held at apply, the way
-- the 911 dialer holds its send).
CREATE TABLE IF NOT EXISTS app_edits (
    id            TEXT PRIMARY KEY,
    user_id       TEXT NOT NULL REFERENCES users(id),
    title         TEXT NOT NULL,
    description   TEXT NOT NULL,
    target        TEXT NOT NULL DEFAULT '',  -- the area or file the edit touches
    patch         TEXT NOT NULL DEFAULT '',  -- the proposed change, as a diff or text
    model         TEXT NOT NULL DEFAULT '',  -- which provider drafted it, if one did
    lane          TEXT NOT NULL,             -- self_hosted | cloud
    state         TEXT NOT NULL,             -- proposed | approved | rejected
    note          TEXT NOT NULL DEFAULT '',  -- oversight's words on the decision
    decided_by    TEXT,
    decided_at    TEXT,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);

-- The Apple Watch bridge (jim/watch.py): one drip channel per user, the
-- address an iPhone Shortcut deposits readings at. The token is stored in
-- the clear, deliberately breaking the never-return-the-secret house rule,
-- because this credential is the opposite shape of an API key: it can only
-- *deposit* readings into one user's stream and can never read anything
-- out, and the setup screen must be able to keep showing the URL — a
-- Shortcut is configured by a person retyping it, sometimes weeks later.
-- Rotation is the recovery from a leak, and rotation is one tap.
CREATE TABLE IF NOT EXISTS watch_channels (
    user_id      TEXT PRIMARY KEY REFERENCES users(id),
    token        TEXT NOT NULL UNIQUE,
    created_at   TEXT NOT NULL,
    rotated_at   TEXT,
    last_drip_at TEXT,
    drips        INTEGER NOT NULL DEFAULT 0
);

-- Where this deployment sends mail through. One row, set from the app's
-- own settings screen so an operator never has to touch environment
-- variables — an app that cannot send mail is the whole reason a
-- verification email never arrives. Env vars still win when set, so a
-- server deployment keeps its credentials out of the database.
CREATE TABLE IF NOT EXISTS mail_settings (
    id         INTEGER PRIMARY KEY CHECK (id = 1),
    host       TEXT NOT NULL,
    port       INTEGER NOT NULL DEFAULT 587,
    username   TEXT,
    password   TEXT,
    sender     TEXT,
    public_url TEXT,          -- what the verify link points at
    updated_at TEXT NOT NULL
);

-- Emailed verification codes. Hashed at rest (a database read must not be a
-- verification bypass), single-use, short-lived; issuing a new code retires
-- the previous ones for that address.
CREATE TABLE IF NOT EXISTS email_codes (
    email       TEXT NOT NULL,
    code_hash   TEXT NOT NULL,
    purpose     TEXT NOT NULL,              -- verify
    expires_at  TEXT NOT NULL,
    consumed_at TEXT,
    created_at  TEXT NOT NULL
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

-- One row per alert actually mailed to the far end (jim/farend.py), and the
-- acknowledgment when the person on that end clicked "seen". The token is a
-- single-purpose capability that can only mark this row acknowledged — it
-- reads nothing, so it is stored as given and dies with the row.
CREATE TABLE IF NOT EXISTS farend_alerts (
    id          TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL,
    condition   TEXT NOT NULL,
    severity    TEXT NOT NULL,
    tier        TEXT NOT NULL,
    sent_to     TEXT NOT NULL,
    token       TEXT NOT NULL UNIQUE,
    sent_at     TEXT NOT NULL,
    acked_at    TEXT
);

CREATE TABLE IF NOT EXISTS specialists (
    condition       TEXT PRIMARY KEY,   -- condition domain key (see conditions.py)
    mode            TEXT NOT NULL,      -- local | tandem
    label           TEXT,
    qrme_profile_id TEXT,               -- set when mode = tandem
    created_at      TEXT NOT NULL
);

-- The user's own synthetic profile in QRME — the one that speaks *as* them,
-- as opposed to the specialists above, which belong to other people. Held with
-- an OWNER token, not an interactor token: this profile is not a stranger to
-- them. `consented` is a JSON array of category names from
-- synthetic_self.CATEGORIES, empty until the person has seen the brief and
-- answered. Unlinking deletes the credential and the consent together.
CREATE TABLE IF NOT EXISTS self_links (
    user_id         TEXT PRIMARY KEY REFERENCES users(id),
    qrme_profile_id TEXT NOT NULL,
    owner_token     TEXT NOT NULL,
    consented       TEXT NOT NULL DEFAULT '[]',
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

-- The Guardian's calendar. Reminders ride the proactive ladder at its
-- bottom rung; each appointment reminds once (reminded_at). A booking
-- for a shop service carries the order's receipt id so cancelling the
-- appointment can hand the order back while it is still `placed`.
CREATE TABLE IF NOT EXISTS appointments (
    id             TEXT PRIMARY KEY,
    user_id        TEXT NOT NULL REFERENCES users(id),
    title          TEXT NOT NULL,
    whenat         TEXT NOT NULL,          -- ISO timestamp, tz-aware
    whereat        TEXT,
    email_reminder INTEGER NOT NULL DEFAULT 0,
    qrme_order_id  TEXT,                   -- links a shop_receipts row
    status         TEXT NOT NULL DEFAULT 'booked',  -- booked | cancelled
    reminded_at    TEXT,
    created_at     TEXT NOT NULL
);

-- Receipts for orders placed on QRME shops through the tandem. The
-- history lives HERE: QRME is never asked what this person bought,
-- because that answer held remotely would be a profile of them.
CREATE TABLE IF NOT EXISTS shop_receipts (
    id            TEXT PRIMARY KEY,
    user_id       TEXT NOT NULL REFERENCES users(id),
    qrme_order_id TEXT NOT NULL,
    shop_id       TEXT NOT NULL,
    title         TEXT NOT NULL,
    amount        REAL NOT NULL,
    currency      TEXT NOT NULL,
    status        TEXT NOT NULL,
    placed_at     TEXT NOT NULL
);

-- Your circle (jim/circle.py): an invitation is one direction; two
-- directions make contacts, and either side deleting theirs ends it.
CREATE TABLE IF NOT EXISTS circle_invites (
    user_id    TEXT NOT NULL REFERENCES users(id),
    other_id   TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (user_id, other_id)
);

-- Per-user feature switches, default on; everything downstream refuses
-- by naming the switch.
CREATE TABLE IF NOT EXISTS user_features (
    user_id    TEXT NOT NULL REFERENCES users(id),
    feature    TEXT NOT NULL,
    enabled    INTEGER NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (user_id, feature)
);

-- One thread per pair: the key is the sorted pair, so the conversation
-- has one identity from either side. Nothing here ever leaves this
-- deployment — there is no cloud relay for what neighbours say.
CREATE TABLE IF NOT EXISTS circle_messages (
    id        TEXT PRIMARY KEY,
    low_id    TEXT NOT NULL,
    high_id   TEXT NOT NULL,
    sender_id TEXT NOT NULL,
    body      TEXT NOT NULL,
    sent_at   TEXT NOT NULL
);

-- The homepage sandbox: one validated document per user (hex colors,
-- http(s) links, plain text), shown to signed-in neighbours only.
CREATE TABLE IF NOT EXISTS user_homepages (
    user_id    TEXT PRIMARY KEY REFERENCES users(id),
    doc        TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- The care team is an organization (QRME's operational ecosystem): the
-- user's own org, the department that speaks for the Guardian, and the
-- owner token they pasted to let JIM act on their behalf. Unlinking
-- deletes the credential.
CREATE TABLE IF NOT EXISTS care_teams (
    user_id       TEXT PRIMARY KEY REFERENCES users(id),
    org_id        TEXT NOT NULL,
    department_id TEXT NOT NULL,
    owner_token   TEXT NOT NULL,
    created_at    TEXT NOT NULL
);

-- Joint plans that came back from a coordination, with what triggered them.
CREATE TABLE IF NOT EXISTS care_plans (
    id              TEXT PRIMARY KEY,
    user_id         TEXT NOT NULL REFERENCES users(id),
    coordination_id TEXT,
    goal            TEXT NOT NULL,
    plan            TEXT,
    trigger         TEXT NOT NULL DEFAULT '{}',
    sealed          INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT NOT NULL
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
CREATE TABLE IF NOT EXISTS lookouts (
    id           TEXT PRIMARY KEY,
    user_id      TEXT NOT NULL REFERENCES users(id),
    url          TEXT NOT NULL,
    every_hours  REAL NOT NULL,
    task_id      TEXT NOT NULL,   -- the standing task in the vault
    created_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS excursions (
    id           TEXT PRIMARY KEY,
    user_id      TEXT NOT NULL REFERENCES users(id),
    topic        TEXT NOT NULL,       -- stays local
    brief        TEXT NOT NULL,       -- sanitized outbound query
    redactions   INTEGER NOT NULL DEFAULT 0,
    left_host    INTEGER NOT NULL DEFAULT 0,
    findings     TEXT,
    learned      INTEGER NOT NULL DEFAULT 0,
    answered_by  TEXT,                 -- who actually wrote the findings
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
-- Budgeting plans (jim/life.py): the user's own monthly limits, per
-- category or overall ('*'). budget_spend keeps only what the math needs —
-- an amount, a category, a month — while the transaction's story stays in
-- the vault with the rest of the context event.
CREATE TABLE IF NOT EXISTS budgets (
    user_id       TEXT NOT NULL REFERENCES users(id),
    category      TEXT NOT NULL,        -- lowercase; '*' = everything
    monthly_limit REAL NOT NULL,
    updated_at    TEXT NOT NULL,
    PRIMARY KEY (user_id, category)
);

CREATE TABLE IF NOT EXISTS budget_spend (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    category   TEXT NOT NULL,
    amount     REAL NOT NULL,
    month      TEXT NOT NULL,            -- YYYY-MM
    created_at TEXT NOT NULL
);

-- The money guardian (jim/money.py). Credentials never land in these
-- tables: `vault_key` is the PDI address of the sealed numbers, and the
-- only digits kept locally are the last four, which is what a screen may
-- show. A mandate row is the written handover — caps, classes, scope —
-- and an order row is a *proposal* under it, logged whether or not a
-- brokerage connector ever exists to execute it.
CREATE TABLE IF NOT EXISTS money_accounts (
    id          TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL REFERENCES users(id),
    kind        TEXT NOT NULL,            -- checking | savings | brokerage | crypto
    institution TEXT NOT NULL,
    label       TEXT NOT NULL,
    last4       TEXT,
    vault_key   TEXT,                     -- where the numbers actually live
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS money_balances (
    id          TEXT PRIMARY KEY,
    account_id  TEXT NOT NULL REFERENCES money_accounts(id),
    balance     REAL NOT NULL,
    note        TEXT,
    observed_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS savings_goals (
    user_id    TEXT PRIMARY KEY REFERENCES users(id),
    goal       REAL NOT NULL,
    note       TEXT,
    set_at     TEXT NOT NULL,
    reached_at TEXT
);

-- The low-balance floor, when its owner set one. No row means the floor is
-- derived (jim/money.py LOW_FLOOR / LOW_FRACTION), the way an absent
-- drift_bands row means the default band.
CREATE TABLE IF NOT EXISTS money_floors (
    user_id TEXT PRIMARY KEY REFERENCES users(id),
    floor   REAL NOT NULL,
    set_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS money_mandates (
    user_id       TEXT PRIMARY KEY REFERENCES users(id),
    enabled       INTEGER NOT NULL DEFAULT 0,
    cap_per_order REAL NOT NULL DEFAULT 0,
    monthly_cap   REAL NOT NULL DEFAULT 0,
    asset_classes TEXT NOT NULL DEFAULT '[]',
    scope         TEXT NOT NULL DEFAULT '',
    updated_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS money_orders (
    id          TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL REFERENCES users(id),
    asset_class TEXT NOT NULL,
    amount      REAL NOT NULL,
    month       TEXT NOT NULL,            -- YYYY-MM
    status      TEXT NOT NULL,            -- proposed (no connector executes)
    rationale   TEXT,
    created_at  TEXT NOT NULL
);

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
    stress     INTEGER,            -- 1 (calm) .. 5 (overwhelmed)
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

-- Accessibility reports: what somebody was trying to do, what stood in the
-- way, and what would have helped — in their own words, in their own
-- language. Deliberately narrower than improvements: there is no submitter
-- column at all, because a report about ability must not require disclosing
-- anything about the body that wrote it. When a PDI vault is configured the
-- report is sealed there too (pdi_key), same custody as the tandem.
CREATE TABLE IF NOT EXISTS access_reports (
    id         TEXT PRIMARY KEY,
    lang       TEXT NOT NULL DEFAULT 'en',
    doing      TEXT NOT NULL,           -- what the person was trying to do
    wall       TEXT NOT NULL,           -- what stood in the way
    help       TEXT,                    -- what would help, if they said
    status     TEXT NOT NULL DEFAULT 'received',  -- received | accepted | built
    pdi_key    TEXT,
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

-- Which captures a referral request is releasing.
--
-- A separate table rather than a column on `referral_requests`, because this
-- schema has no migrations — every statement here is CREATE TABLE IF NOT
-- EXISTS, so an added column never reaches a database that already exists.
-- A new table does.
CREATE TABLE IF NOT EXISTS referral_captures (
    referral_request_id TEXT NOT NULL REFERENCES referral_requests(id),
    capture_id          TEXT NOT NULL REFERENCES captures(id),
    created_at          TEXT NOT NULL,
    PRIMARY KEY (referral_request_id, capture_id)
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

-- The presence's own spoken beats (jim/presence.py). What it said, when, and
-- which line — never the sentence itself, because the sentence is composed in
-- the reader's language on the client and storing the English would make this
-- table a second, worse copy of what somebody actually heard.
--
-- It exists for one reason: so the presence does not repeat itself. A
-- guardian that says the same thing every morning is a notification, and
-- people turn notifications off.
CREATE TABLE IF NOT EXISTS presence_beats (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    slot       TEXT,            -- morning | midday | evening
    area       TEXT,            -- one of the six, or NULL for an open question
    register   TEXT,            -- noticing | nudging | celebrating | curious
    line_key   TEXT NOT NULL,   -- the key, not the words
    created_at TEXT NOT NULL
);

-- How the presence carries itself: `companion` (the default) or
-- `professional`. One row per user, written either from the setting or from
-- a sentence — "keep it professional" changes it from that turn on.
--
-- It is a register, never a capability. What the presence watches and every
-- safety path are identical in both, because a dial that quietly narrowed
-- what a health guardian sees would hurt the person who turned it.
CREATE TABLE IF NOT EXISTS presence_bearing (
    user_id    TEXT PRIMARY KEY REFERENCES users(id),
    bearing    TEXT NOT NULL,   -- companion | professional
    created_at TEXT NOT NULL
);

-- Where the presence speaks. One row per user: a choice, not a history.
CREATE TABLE IF NOT EXISTS presence_surface (
    user_id    TEXT PRIMARY KEY REFERENCES users(id),
    surface    TEXT NOT NULL,   -- earbuds | speaker | glasses | ar | vr | ...
    created_at TEXT NOT NULL
);

-- How the console looks. One row per user: a choice, not a history.
-- Colors only — never a filter over photos, and never a capability.
CREATE TABLE IF NOT EXISTS appearance (
    user_id    TEXT PRIMARY KEY REFERENCES users(id),
    theme      TEXT NOT NULL,   -- standard | midnight | paper
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

-- The offline coach's growing floor (jim/pipeline.py): what a paid model
-- turn or a learned excursion left behind, one row per lesson. The stack
-- predicts from these before the curated pack, because they were learned
-- for this user in particular.
CREATE TABLE IF NOT EXISTS deposits (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    area       TEXT NOT NULL,
    topic      TEXT NOT NULL,
    guidance   TEXT NOT NULL,
    source     TEXT NOT NULL,   -- coach | excursion
    model      TEXT,            -- who taught it, when a model did
    created_at TEXT NOT NULL
);

-- Questions the offline stack had no stored answer for (jim/pipeline.py):
-- the coach's own misses, recorded so JIM can study exactly what was
-- missing. The need writes the shopping list.
-- One logged meal (jim/meals.py): the note is the log (kept local so the
-- offline coach's nutrition area can read it), `logged` is that note tidied
-- by the online model when one stood — `described_by` says which — and the
-- photo, if any, is a sealed capture referenced here and never unsealed by
-- anything automatic.
CREATE TABLE IF NOT EXISTS meals (
    id           TEXT PRIMARY KEY,
    user_id      TEXT NOT NULL,
    note         TEXT,
    logged       TEXT NOT NULL,
    described_by TEXT NOT NULL,     -- note | model | photo
    capture_id   TEXT,
    created_at   TEXT NOT NULL
);

-- Statements: the raw file lives in the vault; the row is the reading.
CREATE TABLE IF NOT EXISTS statements (
    id          TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL,
    account_id  TEXT NOT NULL,
    filename    TEXT NOT NULL,
    line_count  INTEGER NOT NULL,
    total_in    REAL NOT NULL,
    total_out   REAL NOT NULL,
    end_balance REAL,
    created_at  TEXT NOT NULL
);

-- Bank links: a written aggregator consent; status never claims data
-- that was not pulled (consented | revoked; linked when credentials and
-- a client actually stand behind it).
CREATE TABLE IF NOT EXISTS bank_links (
    id          TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL,
    account_id  TEXT NOT NULL,
    institution TEXT NOT NULL,
    aggregator  TEXT NOT NULL,
    status      TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    revoked_at  TEXT
);

-- Interview drills: the question bank is code; the table is the practice.
CREATE TABLE IF NOT EXISTS drills (
    id           TEXT PRIMARY KEY,
    user_id      TEXT NOT NULL,
    kind         TEXT NOT NULL,
    question     TEXT NOT NULL,
    probes       TEXT NOT NULL,      -- newline-joined, as dealt
    response     TEXT,
    feedback     TEXT,               -- NULL when the checklist stood in
    described_by TEXT,               -- model | checklist
    created_at   TEXT NOT NULL,
    answered_at  TEXT
);

-- The weekly letter: composed only from what was logged, the digest kept
-- beside the prose so the reader can always see the facts under the words.
CREATE TABLE IF NOT EXISTS letters (
    id           TEXT PRIMARY KEY,
    user_id      TEXT NOT NULL,
    week_start   TEXT NOT NULL,      -- YYYY-MM-DD, seven days ending at compose
    body         TEXT NOT NULL,
    described_by TEXT NOT NULL,      -- model | digest
    digest       TEXT NOT NULL,
    -- The letter keeps the excursions' promise (jim/letter.py): whether
    -- composing it sent the (sanitized) digest to an external model, and
    -- how many private terms the sanitize pass took out first.
    left_host    INTEGER NOT NULL DEFAULT 0,
    redactions   INTEGER NOT NULL DEFAULT 0,
    -- When this body was last built. A letter is a cached view of its
    -- week: users.forgot_at newer than this means a forgetting has
    -- touched this person and the body rebuilds before it is shown.
    built_at     TEXT,
    created_at   TEXT NOT NULL
);

-- What the guardian went and studied on its own, and which monitor asked for
-- it. The excursion row holds what could have left; this holds why anybody
-- went. It is also the budget: errands opened today are counted from here, so
-- a restart is not a fresh day's spending.
CREATE TABLE IF NOT EXISTS errands (
    id           TEXT PRIMARY KEY,
    user_id      TEXT NOT NULL REFERENCES users(id),
    topic        TEXT NOT NULL,
    area         TEXT NOT NULL,
    why          TEXT NOT NULL,      -- the monitor that asked, in words
    excursion_id TEXT NOT NULL REFERENCES excursions(id),
    redactions   INTEGER NOT NULL DEFAULT 0,
    left_host    INTEGER NOT NULL DEFAULT 0,
    opened_at    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_errands_day
    ON errands (user_id, opened_at);

-- An assisted call: the agent on a shared-route call, with the far side told
-- out loud before anything listens. Nothing about the other party is stored —
-- no number, no name, no transcript — because they have no account here and
-- never will. What is kept is that a notice was given, when, and in what
-- words, which is the one fact they would ever want established.
--
-- `contact_id` looks like an exception and is not one: it points at a row in
-- *this person's own* `contacts`, which they put there themselves before the
-- call. The number still is not stored — what is stored is which of their own
-- contacts it matched, and a call matching none of them leaves nothing.
CREATE TABLE IF NOT EXISTS assisted_calls (
    id            TEXT PRIMARY KEY,
    user_id       TEXT NOT NULL REFERENCES users(id),
    route         TEXT NOT NULL,      -- speaker | speakerphone | car | conference
    recording     INTEGER NOT NULL DEFAULT 0,
    notice        TEXT NOT NULL,      -- the exact words, as they were spoken
    language      TEXT NOT NULL,      -- which language they were said in
    language_clue TEXT NOT NULL,      -- what that was inferred from (+34, …)
    contact_id    TEXT,               -- one of this person's own, or NULL
    announced_at  TEXT,               -- NULL until it actually went out
    opened_at     TEXT NOT NULL,
    ended_at      TEXT,
    ended_because TEXT
);

-- What may sense this person, through what device, and whether the people in
-- that space were told. `others_told` is somebody's assertion with a time on
-- it, not consent this product collected, and it is stored as what it is —
-- see jim/monitors.py. A switched-off row is kept rather than deleted: the
-- decision and when it was made are the point.
CREATE TABLE IF NOT EXISTS monitors (
    user_id     TEXT NOT NULL REFERENCES users(id),
    monitor     TEXT NOT NULL,
    device_name TEXT NOT NULL DEFAULT '',
    switched_on INTEGER NOT NULL DEFAULT 0,
    others_told INTEGER NOT NULL DEFAULT 0,
    keeping     INTEGER NOT NULL DEFAULT 0,
    decided_at  TEXT NOT NULL,
    PRIMARY KEY (user_id, monitor)
);

-- This person's own address book: who they know, and enough of each number to
-- recognise a call from them. Put here by the person, one at a time — nothing
-- harvested from a call ever lands in this table, which is the whole
-- asymmetry. A number somebody typed for their mother is their own record; a
-- number that merely rang them is read for the notice's language and dropped,
-- exactly as `assisted_calls` above says.
--
-- `digits` is the number reduced to digits and cut to its last nine, which is
-- what makes +1-555-0142 and (555) 0142 the same person. It is stored plainly
-- rather than hashed: a phone number is a ten-digit space and a laptop walks
-- it in minutes, so a hash here would be theatre. What protects it is that it
-- never leaves the deployment, and that it is the person's own book.
--
-- `jim_user_id` is set only where that contact also holds an account here. It
-- is what lets two guardians find each other at dial time, and it is NULL for
-- most rows — the majority of anybody's address book has no guardian in it,
-- and that is the case this table exists to serve properly.
CREATE TABLE IF NOT EXISTS contacts (
    id          TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL REFERENCES users(id),
    name        TEXT NOT NULL,
    digits      TEXT NOT NULL,
    jim_user_id TEXT,
    added_at    TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_contacts_digits
    ON contacts (user_id, digits);

-- Where a person's book actually lives. A row here means it is sealed into
-- PDI under `vault_key` and the `contacts` table holds nothing for them; no
-- row means platform custody and the rows are local. Never both — see
-- `jim/contacts.py`, and the guard that holds it.
CREATE TABLE IF NOT EXISTS contact_books (
    user_id   TEXT PRIMARY KEY REFERENCES users(id),
    vault_key TEXT NOT NULL,
    held      INTEGER NOT NULL DEFAULT 0,   -- how many, so a count needs no unseal
    sealed_at TEXT NOT NULL
);

-- Two guardians working together on behalf of two people who are already
-- each other's contacts. The link is never spoken on a call: it carries what
-- one guardian told the other, split by side, so each person can read their
-- own guardian's half afterwards. `task` is what outlives the call — a link
-- carrying one survives the call ending once both sides have agreed to it
-- (`liaison_task_agreed`), and closing the task closes it.
CREATE TABLE IF NOT EXISTS liaisons (
    id            TEXT PRIMARY KEY,
    low_id        TEXT NOT NULL REFERENCES users(id),
    high_id       TEXT NOT NULL,
    about         TEXT NOT NULL DEFAULT '',
    task          TEXT NOT NULL DEFAULT '',
    opened_at     TEXT NOT NULL,
    ended_at      TEXT,
    ended_because TEXT
);

-- One thing a guardian said across a link. `said_by` is the person it speaks
-- for, which is what makes "what did mine disclose" answerable.
CREATE TABLE IF NOT EXISTS liaison_lines (
    id      TEXT PRIMARY KEY,
    link_id TEXT NOT NULL REFERENCES liaisons(id),
    said_by TEXT NOT NULL,
    body    TEXT NOT NULL,
    said_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_liaison_lines ON liaison_lines (link_id);

-- Who has agreed to the task holding a link open. One row per side, and the
-- link outlives the call only when both are present.
--
-- A table rather than two columns on `liaisons`, because this schema has no
-- migrations — every statement here is CREATE TABLE IF NOT EXISTS, so an
-- added column never reaches a database that already exists. A new table
-- does.
--
-- It stores the **wording** beside the person, not just the fact that they
-- agreed. Agreeing to *book the venue* is not agreeing to *run the wedding*,
-- so re-wording the task leaves the other side's row behind and the link
-- needs agreeing again — the reset falls out of the key rather than being
-- remembered by some later edit to the update path.
CREATE TABLE IF NOT EXISTS liaison_task_agreed (
    link_id   TEXT NOT NULL REFERENCES liaisons(id),
    user_id   TEXT NOT NULL,
    task      TEXT NOT NULL,   -- the wording this side said yes to
    agreed_at TEXT NOT NULL,
    PRIMARY KEY (link_id, user_id)
);

-- Two people on one call, each with their own channel 2 (jim/mic.py).
--
-- It carries no audio, no content and nothing either guardian heard. What it
-- is for is the disclosure: on a call where both guardians are listening,
-- each person is entitled to know the other's is. Two private channels that
-- did not know about each other could each be honest and the pair of them
-- still be a surprise.
--
-- The pair never grants listening. Each side's channel 2 was opened by
-- `mic.handover` and passed every refusal there — a private route, a busy
-- primary, nobody else in earshot — before this row could name it. Joining a
-- pair is naming a channel that already exists, so no rule in that function
-- can be reached around by pairing first.
CREATE TABLE IF NOT EXISTS mic_pairs (
    id            TEXT PRIMARY KEY,
    low_id        TEXT NOT NULL REFERENCES users(id),
    high_id       TEXT NOT NULL,
    about         TEXT NOT NULL DEFAULT '',
    opened_at     TEXT NOT NULL,
    ended_at      TEXT,
    ended_because TEXT
);

-- One side of such a pair, and the channel-2 session it names. One row per
-- person: a pair is live only when both are here and neither has hung up.
CREATE TABLE IF NOT EXISTS mic_pair_sides (
    pair_id    TEXT NOT NULL REFERENCES mic_pairs(id),
    user_id    TEXT NOT NULL,
    session_id TEXT NOT NULL,   -- their own mic_sessions row, never read by
                                -- the other side
    joined_at  TEXT NOT NULL,
    PRIMARY KEY (pair_id, user_id)
);

-- The day as it was taken in, and what survived of it (jim/daybook.py).
--
-- One row per moment a monitor sensed something, **whether or not** its
-- content was kept. That is the whole point of the table: an accounting that
-- listed only what survived would be a record with its own omissions edited
-- out. `dropped_because` says which promise stopped it — the monitor's own
-- `holds`, a keeping switch left off, or the person going back and forgetting
-- one afterwards.
--
-- `content` is empty for everything the roster does not let this monitor
-- keep, and that decision is never the caller's. See `jim/monitors.py`,
-- whose `keeps` field is the same promise its `holds` sentence makes to the
-- person reading it before they switch anything on.
CREATE TABLE IF NOT EXISTS day_moments (
    id              TEXT PRIMARY KEY,
    user_id         TEXT NOT NULL REFERENCES users(id),
    monitor         TEXT NOT NULL,
    stretch_id      TEXT,            -- the meeting it fell inside, or NULL
    kept            INTEGER NOT NULL DEFAULT 0,
    content         TEXT NOT NULL DEFAULT '',   -- '' unless kept
    dropped_because TEXT NOT NULL DEFAULT '',   -- '' when it was kept
    sensed_at       TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_day_moments ON day_moments (user_id, sensed_at);

-- A meeting, a call, or a working stretch: a run of the day with one monitor
-- on it. `others_told` is the same claim `monitors.plug_in` demands, asked
-- again here — switching a room speaker on for a quiet house is not the same
-- decision as bringing four people into that room for an hour.
CREATE TABLE IF NOT EXISTS day_stretches (
    id          TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL REFERENCES users(id),
    monitor     TEXT NOT NULL,
    about       TEXT NOT NULL DEFAULT '',
    others_told INTEGER NOT NULL DEFAULT 0,
    opened_at   TEXT NOT NULL,
    ended_at    TEXT
);

-- What the coach noticed during the day, and what settled it (jim/noticed.py).
--
-- One row per detection this pass has looked at, which is also how it knows
-- not to look again: `due` is the detections with no row here.
--
-- `settled_by` is the column the whole ladder is about. `coach` means the
-- offline stack answered from what it already knew and the turn cost nothing;
-- `jim` means it could not, and a paid turn was spent. A pass that reached no
-- model writes no row at all — nothing was bought, so nothing is recorded and
-- the situation is still there tomorrow.
CREATE TABLE IF NOT EXISTS notices (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    event_id   TEXT NOT NULL REFERENCES events(id),
    condition  TEXT NOT NULL DEFAULT '',
    severity   TEXT NOT NULL DEFAULT '',   -- never 'critical': see jim/noticed.py
    settled_by TEXT NOT NULL,              -- coach | jim
    said       TEXT NOT NULL DEFAULT '',
    noticed_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_notices_event ON notices (event_id);

CREATE TABLE IF NOT EXISTS gaps (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    area       TEXT NOT NULL,
    question   TEXT NOT NULL,
    filled     INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
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

-- Error reports, folded into counters the moment they arrive (jim/problems.py).
-- No report is stored as a report: the key is what triage needs and nothing
-- narrower, because a row that identifies one install is what the whole
-- content-free design exists to avoid.
CREATE TABLE IF NOT EXISTS problem_reports (
    source      TEXT NOT NULL,
    app_version TEXT NOT NULL,
    platform    TEXT NOT NULL,
    op          TEXT NOT NULL,
    status      INTEGER NOT NULL,
    day         TEXT NOT NULL,
    count       INTEGER NOT NULL DEFAULT 0,
    last_seen   TEXT NOT NULL,
    PRIMARY KEY (source, app_version, platform, op, status)
);

-- An engaged session (jim/engaged.py): the online Guardian, left running
-- until the person signs off rather than closed after a turn. One open row
-- per user at a time — "engaged" is a state somebody is in, not a resource
-- they accumulate — which `engaged.open_session` keeps true by handing back
-- the open one rather than making a second.
CREATE TABLE IF NOT EXISTS engagements (
    id            TEXT PRIMARY KEY,
    user_id       TEXT NOT NULL REFERENCES users(id),
    area          TEXT NOT NULL,
    opened_at     TEXT NOT NULL,
    signed_off_at TEXT              -- NULL while it is still open
);

-- The transcript, kept here rather than by the console. A session a person
-- was told stays open until they sign off must survive the app being closed,
-- and one held in a browser tab does not.
CREATE TABLE IF NOT EXISTS engagement_turns (
    engagement_id TEXT NOT NULL REFERENCES engagements(id),
    seq           INTEGER NOT NULL,
    role          TEXT NOT NULL,    -- 'user' | 'assistant'
    content       TEXT NOT NULL,
    created_at    TEXT NOT NULL,
    PRIMARY KEY (engagement_id, seq)
);

-- The undo trail. `undo` holds the request that would take the act back,
-- built at act time because the material it needs — the id the write
-- returned, the value it overwrote — is only knowable then. `irreversible`
-- names why, in the rows where there is no way back; every acting row in
-- `engaged.TOOLS` carries exactly one of the two.
CREATE TABLE IF NOT EXISTS engagement_acts (
    id            TEXT PRIMARY KEY,
    engagement_id TEXT NOT NULL REFERENCES engagements(id),
    user_id       TEXT NOT NULL REFERENCES users(id),
    tool          TEXT NOT NULL,
    says          TEXT NOT NULL,    -- the sentence a person reads
    status        INTEGER NOT NULL,
    undo          TEXT,             -- JSON: {method, path, body} or NULL
    irreversible  TEXT,             -- refusal key naming why, or NULL
    created_at    TEXT NOT NULL,
    undone_at     TEXT
);

-- Which groups of switches an engaged session may touch (jim/permits.py).
-- One row per decision, not per area: an area with no row has never been
-- decided and falls back to its declared standing, so this table records what
-- somebody *did* rather than a copy of the defaults.
--
-- `granted` holds both answers. A row saying no is as real as a row saying
-- yes — it is how somebody switches off an area that opening a session would
-- otherwise have covered — and a schema that stored only the yeses would make
-- "I turned that off" and "I never looked" the same state.
CREATE TABLE IF NOT EXISTS engaged_permits (
    user_id    TEXT NOT NULL REFERENCES users(id),
    area       TEXT NOT NULL,
    granted    INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (user_id, area)
);

-- What the offline Guardian keeps holding after somebody signs off. The
-- handover made concrete: a sentence said to the online model while engaged
-- becomes a sentence the offline one is carrying once they have gone.
CREATE TABLE IF NOT EXISTS standing_watches (
    id            TEXT PRIMARY KEY,
    user_id       TEXT NOT NULL REFERENCES users(id),
    engagement_id TEXT,
    topic         TEXT NOT NULL,
    area          TEXT,
    created_at    TEXT NOT NULL,
    cleared_at    TEXT
);

-- The hash-chained audit log (jim/audit.py), ported from PDI.
--
-- Deliberately *not* the `events` table above. That one is the person's own
-- timeline — readings, detections, guidance, escalations — written for them
-- to read and shaped by what a screen needs. This is the other thing: a short
-- append-only record of the consequential acts, where each row's hash covers
-- the row before it, so a retroactive edit or a removed row breaks the chain
-- and `verify()` says at which sequence number.
--
-- No `REFERENCES users(id)`, and that is the point rather than an omission. A
-- chain whose rows can be taken out by a cascade when an account closes is
-- tamper-evident right up until somebody closes an account. What an erasure
-- removes is the person's data; `life.delete_user_data` writes that removal
-- here instead of erasing the record of it.
CREATE TABLE IF NOT EXISTS audit (
    seq       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id   TEXT,             -- NULL for deployment-wide events
    action    TEXT NOT NULL,    -- one of jim.audit.ACTIONS
    ref       TEXT,             -- resource reference, or a small detail
    at        TEXT NOT NULL,
    prev_hash TEXT NOT NULL,
    hash      TEXT NOT NULL
);

-- Widgets: small programs a person writes for themselves. The source is
-- theirs and is never run anywhere but the box in `jim/widgets.py` — no
-- network, one directory, no child processes, capped CPU and memory.
-- Scoped by user_id at every read and write and not only at the door,
-- because this deployment's disk holds other people's clinical captures.
-- The staleness contract (jim/freshness.py): every reading's age from
-- the source's own clock, every consumer's decision with the age it
-- decided on, and the wrist channel's heartbeat — so the two silences
-- can finally mean different things.
CREATE TABLE IF NOT EXISTS freshness_readings (
    user_id     TEXT NOT NULL,
    observed_at TEXT,
    received_at TEXT NOT NULL,
    skew_ms     REAL,
    age_ms      REAL
);
CREATE TABLE IF NOT EXISTS freshness_heartbeats (
    user_id     TEXT NOT NULL,
    received_at TEXT NOT NULL,
    skew_ms     REAL
);
CREATE TABLE IF NOT EXISTS freshness_decisions (
    user_id    TEXT NOT NULL,
    consumer   TEXT NOT NULL,
    age_ms     REAL,
    state      TEXT NOT NULL,
    decided_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS widgets (
    id          TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL REFERENCES users(id),
    name        TEXT NOT NULL,
    source      TEXT NOT NULL,
    version     INTEGER NOT NULL DEFAULT 1,
    created_at  INTEGER NOT NULL,
    updated_at  INTEGER NOT NULL
);

-- ===================================================================
-- The hands (jim/hands.py). The Guardian could already see, hear and
-- speak; these five tables are what it takes for it to ACT on a screen —
-- and four of the five exist to bound that rather than to enable it.
--
-- The authority a hand moves under. Never implicit, never inherited from a
-- conversation, never widened by anything read off a screen. `places` is a
-- JSON list of NAMED apps or hosts and the module refuses "*" outright,
-- because a grant that names everything is the absence of a grant wearing
-- its clothes.
CREATE TABLE IF NOT EXISTS hand_grants (
    id          TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL REFERENCES users(id),
    granted_by  TEXT NOT NULL,        -- who said yes
    surface     TEXT NOT NULL,        -- hands.SURFACES
    places      TEXT NOT NULL,        -- JSON list of named places, never "*"
    verbs       TEXT NOT NULL,        -- JSON subset of hands.VERBS
    steps       INTEGER NOT NULL,     -- step budget for the whole grant
    watched     INTEGER NOT NULL DEFAULT 1,   -- 1 = only while somebody watches
    door        TEXT NOT NULL,        -- picked | told — how it was granted
    said        TEXT,                 -- the words themselves, when `told`
    expires_at  TEXT NOT NULL,
    revoked_at  TEXT,
    created_at  TEXT NOT NULL
);

-- One session of the Guardian having hands on a surface. `mode` is the
-- whole difference between watching somebody work and doing the work:
-- `watching` is eyes only and cannot spend a step, `acting` moves.
CREATE TABLE IF NOT EXISTS reaches (
    id          TEXT PRIMARY KEY,
    user_id     TEXT NOT NULL REFERENCES users(id),
    grant_id    TEXT NOT NULL REFERENCES hand_grants(id),
    surface     TEXT NOT NULL,
    platform    TEXT NOT NULL,        -- hands.PLATFORMS
    errand      TEXT NOT NULL,        -- what it was asked to do, in words
    mode        TEXT NOT NULL,        -- watching | acting
    state       TEXT NOT NULL,        -- open | asking | done | stopped
    why         TEXT,                 -- why it stopped, in plain words
    handed_to   TEXT REFERENCES users(id),   -- who holds it now, if handed
    routine_id  TEXT,                 -- the routine being learned or replayed
    steps_used  INTEGER NOT NULL DEFAULT 0,
    opened_at   TEXT NOT NULL,
    closed_at   TEXT
);

-- Append-only. Nothing in the package updates or deletes a row here, and
-- `n` is unique per reach so a step cannot be quietly rewritten by a second
-- insert. `saw` keeps what the eyes reported at the moment the hand decided,
-- which is the only way a person reading this afterwards can tell whether
-- the move was reasonable on the evidence it actually had.
CREATE TABLE IF NOT EXISTS hand_actions (
    id         TEXT PRIMARY KEY,
    reach_id   TEXT NOT NULL REFERENCES reaches(id),
    user_id    TEXT NOT NULL REFERENCES users(id),   -- who moved
    n          INTEGER NOT NULL,      -- step number within the reach
    verb       TEXT NOT NULL,
    target     TEXT,                  -- what it aimed at, in words
    detail     TEXT,                  -- JSON argument, secrets never in it
    saw        TEXT,                  -- what the eyes reported before deciding
    outcome    TEXT NOT NULL,         -- done | refused | failed
    note       TEXT,
    at         TEXT NOT NULL,
    UNIQUE (reach_id, n)
);

-- What the machine reported back about a step it was handed.
--
-- `hand_actions.outcome` is written where the move is *permitted*, which is
-- the server, and the server cannot see a cursor. So `done` there has only
-- ever meant "chosen and allowed" — a dry run and a live one left identical
-- records, and a click that missed left one saying it landed. A permission
-- trail that cannot tell a rehearsal from the real thing is not a trail.
--
-- Its own table because `hand_actions` is append-only and stays that way:
-- the machine's report is a second fact about a step, arriving later from
-- somewhere else, not a correction to the first.
CREATE TABLE IF NOT EXISTS hand_landings (
    id       TEXT PRIMARY KEY,
    reach_id TEXT NOT NULL REFERENCES reaches(id),
    n        INTEGER NOT NULL,      -- the step in hand_actions this is about
    landed   TEXT NOT NULL,         -- landed | missed | rehearsed
    note     TEXT,
    at       TEXT NOT NULL,
    UNIQUE (reach_id, n)
);

-- A thing it can do again: learned by watching somebody do it (`shown`) or
-- by being told the steps in words (`told`). One table for both, because a
-- routine dictated over the phone and a routine demonstrated on screen are
-- the same object and the product should not have two of them.
CREATE TABLE IF NOT EXISTS routines (
    id         TEXT PRIMARY KEY,
    user_id    TEXT NOT NULL REFERENCES users(id),
    name       TEXT NOT NULL,
    surface    TEXT NOT NULL,
    learned    TEXT NOT NULL,         -- shown | told
    steps      TEXT NOT NULL,         -- JSON list of {verb, target, detail}
    runs       INTEGER NOT NULL DEFAULT 0,
    last_run   TEXT,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_actions_reach ON hand_actions (reach_id, n);
CREATE INDEX IF NOT EXISTS idx_landings_reach ON hand_landings (reach_id, n);
CREATE INDEX IF NOT EXISTS idx_reaches_user ON reaches (user_id);
"""

_local = threading.local()


def db_path() -> str:
    return os.environ.get("JIM_DB", "jim.db")


# Columns added to tables that already exist on somebody's disk. CREATE TABLE
# IF NOT EXISTS never revisits an existing table, so a new column needs this
# second list — (table, column, type) — applied by connect() when missing.
_NEW_COLUMNS = [
    ("checkins", "stress", "INTEGER"),
    # The standing learn task the tandem vault keeps for this person's
    # corpus (jim/corpus.py, 3.0.7). NULL is no task planted — no vault, an
    # older tandem, or capture off.
    ("corpus_consent", "learn_task_id", "TEXT"),
    # Anonymous enrollment (jim/identity.py, spec [0031] / FIG. 2 box 212):
    # `display_name` holds a pseudonym when `anonymous` is set, and
    # `legal_name` is the name — if any — the user chose to leave for
    # emergencies only. Never shown in the app.
    ("users", "anonymous", "INTEGER NOT NULL DEFAULT 0"),
    ("users", "legal_name", "TEXT"),
    # Whether the radio handshake actually happened — a Bluetooth device
    # the browser's chooser paired is a different fact from a name typed
    # into the manual row, and the card should be able to say which.
    ("devices", "paired", "INTEGER NOT NULL DEFAULT 0"),
    # Verified parental consent (spec [0024]/[0030]): the guardian address a
    # minor's verification code was delivered to, and when that inbox proved
    # it. NULL for adults and for the asserted-only token path.
    ("users", "guardian_email", "TEXT"),
    ("users", "guardian_verified_at", "TEXT"),
    # The crash watch's trip on the Needs-a-person queue (jim/crashwatch.py):
    # who said "I'm going", and when. Columns on the watch row rather than a
    # new table, because one watch per user means at most one open crash
    # alarm — the same reason its alarm id can be a constant.
    ("crash_watches", "accepted_by", "TEXT"),
    ("crash_watches", "accepted_at", "TEXT"),
    # Which of this person's own contacts the call matched (jim/contacts.py).
    # A column on the call rather than a table of its own, because a call has
    # at most one far side — and NULL is the ordinary case, not a gap: most
    # numbers anybody rings are not in their address book.
    ("assisted_calls", "contact_id", "TEXT"),
    # The call an appointment came out of. What survives a conversation is the
    # thing that has to be done, not the conversation — so this is a pointer
    # back to a call, and there is deliberately no column anywhere holding
    # what was said on it.
    ("appointments", "from_call_id", "TEXT"),
    # The ladder ends at a person: the address JIM can write to when the
    # escalation tree says notify_contact, and the last time the monthly
    # liveness note proved that mailbox is a real one (jim/farend.py).
    ("users", "emergency_email", "TEXT"),
    ("users", "farend_pinged_at", "TEXT"),
    ("letters", "left_host", "INTEGER NOT NULL DEFAULT 0"),
    ("letters", "redactions", "INTEGER NOT NULL DEFAULT 0"),
    ("letters", "built_at", "TEXT"),
    ("users", "forgot_at", "TEXT"),
    # The study says who answered (jim/research.py): the provider that
    # actually wrote an excursion's findings, recorded beside what could
    # have left. NULL on rows that predate the record — absence stays
    # absence, never a guess.
    ("excursions", "answered_by", "TEXT"),
    # When channel 2 last actually delivered something (jim/mic.py). The
    # module owns permission and state; until this column there was no
    # record of the second microphone ever having been *used*, so
    # "attached" was the strongest thing any screen could say — and it
    # said it as though it meant listening.
    ("mic_channels", "last_heard_at", "TEXT"),
    # Where the account holder signed up from (jim/loadouts.py). The model
    # menu is a per-region loadout — an account outside the US is not bound
    # by American-only rules, and a US account can be tapered to American
    # providers if the government asks — so the region has to be a fact on
    # the account, chosen at sign-up, not inferred from an address later.
    ("users", "region", "TEXT"),
    # The placed leg (jim/telephony.py, 3.0.8): whether the voice door took
    # the call, which house rang it and under what reference, the sentence
    # when it did not (`placement`), the line's word on how it ended
    # (`ended`), when it was placed and picked up, and how many spoken turns
    # it ran. `placed` is 0 for a leg that was only prepared — the honest
    # state on a box with no transport — so a screen can tell the two apart.
    ("reachout_calls", "placed", "INTEGER NOT NULL DEFAULT 0"),
    ("reachout_calls", "provider", "TEXT"),
    ("reachout_calls", "provider_call_id", "TEXT"),
    ("reachout_calls", "placement", "TEXT"),
    ("reachout_calls", "ended", "TEXT"),
    ("reachout_calls", "placed_at", "TEXT"),
    ("reachout_calls", "answered_at", "TEXT"),
    ("reachout_calls", "turns", "INTEGER NOT NULL DEFAULT 0"),
]


def connect() -> sqlite3.Connection:
    conn = getattr(_local, "conn", None)
    if conn is None or getattr(_local, "path", None) != db_path():
        conn = sqlite3.connect(db_path())
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")  # concurrent readers
        conn.executescript(_SCHEMA)
        for table, column, kind in _NEW_COLUMNS:
            have = {r["name"] for r in
                    conn.execute(f"PRAGMA table_info({table})")}
            if column not in have:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {kind}")
        conn.commit()
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
