# JIM-mini / Guardian

![JIM-mini — Guardian](assets/cover.svg)

A standalone **personal-guidance** system (patent app 19/038,196): it monitors
a user's biometric and contextual signals, detects known conditions, delivers
guidance, and escalates to an emergency contact / live help on critical events.
Around that core sits a **life layer** — consented data sources, mood/energy
check-ins, smart goals, habit streaks, proactive insights, and a 24/7 life
coach across six life areas.

JIM-mini is its own product. When configured for tandem it delegates guidance
to QRME specialist profiles over HTTP. See [docs/tandem.md](docs/tandem.md).

![Guardian tandem architecture](assets/guardian-tandem.svg)

*Wearable signals → Guardian detects a condition → triggers the matching
specialist → moderated guidance, escalating to an emergency contact on critical
events.*

## Run

```bash
pip install -e .[dev]
uvicorn jim.api:app            # standalone
JIM_QRME_URL=http://localhost:8000 uvicorn jim.api:app   # tandem with QRME
JIM_PDI_URL=http://localhost:8100 JIM_PDI_TOKEN=pdi_... uvicorn jim.api:app  # + PDI vault
```

`JIM_DB` sets the SQLite path (default `jim.db`). Set `ANTHROPIC_API_KEY` for
real `claude-opus-4-8` guidance; otherwise (or with `JIM_LLM=stub`) a
deterministic stub answers offline. `JIM_MODEL` overrides the model.

## API

| Endpoint | Purpose |
|---|---|
| `GET /health` | Status + whether tandem is configured |
| `POST /enroll` | Enroll a user: terms/guardian consent, emergency contact (+ consent), devices, resting-HR baseline, goals, declared known conditions |
| `POST /conditions/{user_id}` | Declare a known condition after enrollment ("receiving an indication of a known condition"); detection is sensitized for it |
| `PUT /personality/{user_id}` | Adapt the counselor from user input — tone and free-text preferences shape every guidance and coach prompt |
| `POST /specialists` | Register a condition specialist — `local` (JIM's own guidance) or `tandem` (a QRME `qrme_profile_id`) |
| `POST /monitor/{user_id}` | Ingest a biometric/context sample (optionally tagged with its `source_device` — smart watch, stationary system, neural sensor, gesture interface); runs detect → guide → escalate, with predictive early warning when nothing has manifested yet |
| `POST /sessions/{user_id}`, `POST …/{session_id}/end` | Login sessions per device; starting one returns the remembered interaction state, so any device resumes the same conversational thread and counseling routes to the session's device |
| `GET /events/{user_id}` | Event timeline (biometric → detection → guidance → escalation) |
| `GET`/`PUT /sources/{user_id}` | Per-source consent (wearable, health, calendar, spending, bank, messages, location) — nothing is read from a source the user hasn't allowed |
| `POST /context/{user_id}` | Ingest an event from a consented source (403 otherwise); transparent rules turn it into insights |
| `POST /checkin/{user_id}` | Mood & energy check-in; a worrying note still runs the full Guardian detect → escalate pipeline |
| `GET`/`POST /goals/{user_id}`, `PATCH /goals/{user_id}/{goal_id}` | Smart goals with progress; completion earns a praise insight |
| `GET`/`POST /habits/{user_id}`, `POST …/{habit_id}/log` | Habit tracking with streaks; milestones (7/30/100 days) earn insights |
| `POST`/`GET /coach/{user_id}` | 24/7 life coach across `mental_health`, `health_fitness`, `career`, `finance`, `relationships`, `personal_growth`, grounded in recent check-ins and active goals |
| `GET /insights/{user_id}` | Proactive nudges: spending alerts, sleep praise, interview prep, mindful-break suggestions, milestones |
| `DELETE /data/{user_id}` | Delete anything, anytime — erases every trace of the user |

## Condition detection (`jim/conditions.py`)

Transparent rules over a biometric sample — heart rate vs. the user's resting
baseline, respiratory rate, SpO₂, body temperature, movement (fall / collapse /
immobility), and speech (slurred / incoherent) — plus free-text and crisis
cues, returning a condition domain and `info` / `guidance` / `critical`
severity. Domains: anxiety/panic, depression, stress management, phobias,
financial stress, relationship distress, physical distress, and physical
injury (first-aid counseling with a clear call-for-help threshold).

Two things shape detection per user:

- **Declared known conditions** lower the heart-rate threshold, so episodes
  are caught earlier for users known to be prone to them.
- **Predictive early warning** (`conditions.forecast`): a steady heart-rate
  climb that hasn't crossed a threshold yet produces a `forecast` event and a
  "may be building" insight — identifying a potential abnormality before it
  manifests. Prior samples are read back from the PDI vault when tandem
  storage is on.

## Guidance

- **Standalone** (`jim/guidance.py`): JIM generates condition-specific guidance
  through its own LLM provider, with a minimal safety check. Every reply
  carries a **factual basis** (`references`, e.g. Red Cross first-aid steps,
  NHS breathing techniques), is shaped by the user's declared conditions and
  personality preferences (a user-specific adaptation of the model), keeps
  **continuity with prior sessions** via remembered interaction state, and
  reports its **delivery channel** (`delivered_via`: the user's smart watch or
  linked device when one is paired).
- **Tandem** (`jim/qrme_client.py`): delegates to a QRME specialist profile over
  HTTP; the reply is subject to QRME's moderation and stored in QRME's per-user
  memory. If a tandem specialist is registered but no QRME endpoint is
  configured, JIM falls back to standalone guidance and says so.

## PDI tandem — medical data in the encrypted vault (`jim/pdi_client.py`)

With `JIM_PDI_URL` + `JIM_PDI_TOKEN` set (or a `PDIClient` injected), JIM's
most sensitive payloads never touch its own database in the clear:

- **medical** — raw biometric samples (`/monitor`), detection details
  (readings + signals), and check-in notes go to PDI under
  `jim/{user}/medical/…`, sealed with AES-256-GCM by PDI
- **context** — payloads from consented sources (spending, health, calendar,
  messages, …) go under `jim/{user}/context/…`

JIM's SQLite keeps only `{"vaulted": true, "pdi_key": …}` references; insight
and detection rules run on the payload in memory before it is sealed, so
behavior is identical either way. Every vaulted key is tracked locally so
`DELETE /data/{user_id}` purges the PDI records too, and every vault access
lands in PDI's tamper-evident audit chain. Without PDI configured, JIM stores
data locally exactly as before.

## Test

```bash
pytest jim/tests
```

Covers standalone detection/guidance/escalation and a real in-process tandem
run against a separate QRME instance (reached only through the HTTP client).

## Life layer (`jim/life.py`, `jim/coach.py`)

![JIM-mini life layer](assets/life-layer.svg)

The guardrail is consent: context only flows from sources the user has
switched on, and `DELETE /data/{user_id}` erases everything on request.
Insight rules are deliberately transparent (a spending threshold, sleep-hours
bands, calendar keywords, mood ≤ 2, streak milestones) rather than opaque
scoring. The coach shares Guardian's LLM provider and safety net, and check-in
notes feed the same crisis detection as biometric monitoring.

## Out of scope for v1

Live device streaming/pairing, real bank/brokerage connections (spending
events are ingested, no auto-investing), voice mode, AR visualizations,
image insights, community challenges, real emergency-services dispatch, and a
specialist knowledge-pack marketplace — represented structurally, not as live
integrations.
