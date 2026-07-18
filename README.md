# JIM-mini / Guardian

![JIM-mini — Guardian](assets/cover.svg)

A standalone **personal-guidance** system (patent app 19/038,196): it monitors
a user's biometric and contextual signals, detects known conditions, delivers
guidance, and escalates to an emergency contact / live help on critical events.

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
```

`JIM_DB` sets the SQLite path (default `jim.db`). Set `ANTHROPIC_API_KEY` for
real `claude-opus-4-8` guidance; otherwise (or with `JIM_LLM=stub`) a
deterministic stub answers offline. `JIM_MODEL` overrides the model.

## API

| Endpoint | Purpose |
|---|---|
| `GET /health` | Status + whether tandem is configured |
| `POST /enroll` | Enroll a user: terms/guardian consent, emergency contact (+ consent), device pairing, resting-HR baseline, goals |
| `POST /specialists` | Register a condition specialist — `local` (JIM's own guidance) or `tandem` (a QRME `qrme_profile_id`) |
| `POST /monitor/{user_id}` | Ingest a biometric/context sample; runs detect → guide → escalate |
| `GET /events/{user_id}` | Event timeline (biometric → detection → guidance → escalation) |

## Condition detection (`jim/conditions.py`)

Transparent rules over a biometric sample (heart rate vs. the user's resting
baseline, respiratory rate, SpO₂) plus free-text and crisis cues, returning a
condition domain and `info` / `guidance` / `critical` severity.

## Guidance

- **Standalone** (`jim/guidance.py`): JIM generates condition-specific guidance
  through its own LLM provider, with a minimal safety check.
- **Tandem** (`jim/qrme_client.py`): delegates to a QRME specialist profile over
  HTTP; the reply is subject to QRME's moderation and stored in QRME's per-user
  memory. If a tandem specialist is registered but no QRME endpoint is
  configured, JIM falls back to standalone guidance and says so.

## Test

```bash
pytest jim/tests
```

Covers standalone detection/guidance/escalation and a real in-process tandem
run against a separate QRME instance (reached only through the HTTP client).

## Out of scope for v1

Live device streaming/pairing, real emergency-services dispatch, and a
specialist knowledge-pack marketplace — represented structurally, not as live
integrations.
