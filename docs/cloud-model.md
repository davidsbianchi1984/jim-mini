# Cloud Model Gateway

The product suite runs fully offline on local providers (the Anthropic SDK,
or the deterministic stub). A **Cloud Model Gateway** is the optional hosted
tier above that: a service the operator deploys that serves the latest, most
capable model — and accepts community contributions that improve it. Users
get a **greater model**; consenting users get to **help make it better**.

```
   qrme ──────────┐  POST /v1/generate         ┌─────────────────────────┐
                  ├───────────────────────────▶│  Cloud Model Gateway     │
   jim-mini ──────┘  (greater model, e.g.      │  hosted inference +      │
        │             claude-fable-5)          │  contribution intake     │
        │                                      └───────────┬─────────────┘
        │  automatic fallback to the                       │ sealed, audited
        ▼  local provider if unreachable                   ▼
   local provider                                pdi  POST /contributions
   (Anthropic SDK / offline stub)                (AES-256-GCM vault tenant)
```

## Using the greater model

Each AI system ships a `CloudModelClient` (`qrme/cloud.py`, `jim/cloud.py`)
and routes inference through it when configured:

| System | Configuration |
|---|---|
| qrme | `QRME_CLOUD_URL` + `QRME_CLOUD_TOKEN` |
| jim-mini | `JIM_CLOUD_URL` + `JIM_CLOUD_TOKEN` |

The gateway being down never breaks the product: `CloudProvider` falls back
to the local provider automatically. `GET /cloud/status` on either system
reports whether the gateway is configured and what model it serves.

## Contributing to the model

Contribution is **strictly opt-in, anonymized, and revocable**:

- **qrme** — per-profile `cloud_contribution` flag. Only positively-rated
  exchanges are contributed, with all ids stripped and the persona's display
  name replaced throughout. Raw memories, sources, and moderation-held
  content are never contributed.
- **jim-mini** — per-user `cloud_contribution` flag at enrollment. Only
  guidance *outcomes* are contributed: condition domain, severity, and the
  user's rating. Never ids, names, notes, journal text, or raw biometrics.
- Turning the flag off stops all future contributions immediately.

## PDI as the intake

The gateway stores contributed data in **pdi** as a tenant:
`POST /contributions` seals each contribution with AES-256-GCM under a
`contributions/{source}/…` key and records it in the tamper-evident audit
chain; `GET /contributions` lists what has been received. Training pipelines
read via the ciphertext snapshot — contributed data is encrypted at rest,
tenant-isolated, and auditable end to end.

## Gateway contract

| Endpoint | Purpose |
|---|---|
| `POST /v1/generate` | `{system, messages}` → `{content, model}` — inference on the hosted tier |
| `GET /v1/model` | `{model, tier}` — what the gateway serves |
| `POST /v1/contributions` | Anonymized contribution payload → `202` |

Authentication: `Authorization: Bearer <token>`. The gateway itself is
operator-deployed (it is not part of these repositories); everything on the
client side — routing, fallback, consent gating, anonymization — is
implemented and tested here.
