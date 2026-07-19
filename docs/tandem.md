# Tandem architecture

Three separate products in three separate repositories — each stands alone
and can also **interoperate over HTTP**. No project imports another's code.

- [`qrme`](https://github.com/davidsbianchi1984/qrme) — AI synthetic-profile
  platform (relationship-aware profiles, memory, moderation)
- [`jim-mini`](https://github.com/davidsbianchi1984/jim-mini) — Guardian
  personal-guidance system (monitor → predict → guide → escalate, life layer)
- [`pdi`](https://github.com/davidsbianchi1984/pdi) — Private Data
  Infrastructure (encrypted vault, tenant isolation, tamper-evident audit)

```
   ┌──────────────────┐        HTTP         ┌─────────────────────────┐
   │  jim-mini /      │ ─ ─ optional ─ ─ ─▶ │  qrme                   │
   │  Guardian        │  tandem specialist  │  synthetic profiles     │
   │                  │  guidance           │                         │
   └──────────────────┘                     └─────────────────────────┘
           │                                          │
           │ optional (medical &                      │ optional (profile
           │ context payloads)                        │ source material)
           ▼                                          ▼
   ┌──────────────────────────────────────────────────────────┐
   │  pdi — Private Data Infrastructure                       │
   │  AES-256-GCM vault · per-tenant isolation · audit chain  │
   └──────────────────────────────────────────────────────────┘
```

## qrme ✕ jim-mini

JIM-mini is a standalone personal-guidance system: it monitors a user's
biometric and contextual signals, detects known conditions, delivers guidance,
and escalates on critical events. It runs entirely on its own using its own
guidance engine.

When a **tandem specialist** is registered for a condition and JIM is
configured with a QRME endpoint (`JIM_QRME_URL`), JIM delegates guidance for
that condition to a QRME specialist synthetic profile — reached only through
`jim/qrme_client.py` over QRME's public HTTP API. The QRME reply passes QRME's
own persona conditioning, moderation, and per-user memory before JIM surfaces
it. Without the endpoint, JIM uses its own standalone guidance — the two
remain independent.

## qrme / jim-mini ✕ pdi

PDI is a separate secure-hosting product: a private, encrypted data vault with
a tamper-evident audit log and a tenant registry, modeling the "Private Data
Infrastructure" proposal (on-premises or colocation deployment, optional
AI-system integration).

Each AI system can *optionally* run on top of PDI as a tenant, each with its
own client and token — both integrations are live:

- **jim-mini** (`jim/pdi_client.py`, `JIM_PDI_URL` + `JIM_PDI_TOKEN`): medical
  payloads — biometric samples, detection details, forecast trends, check-in
  notes — and consented context payloads are sealed under `jim/{user}/…`
  keys; JIM's own database keeps only key references, prediction reads prior
  samples back from the vault, and `DELETE /data/{user_id}` purges the vault.
- **qrme** (`qrme/pdi_client.py`, `QRME_PDI_URL` + `QRME_PDI_TOKEN`): profile
  source material — life stories, writings, conversations, voice transcripts —
  is sealed under `qrme/{profile}/sources/…` keys, resolved on read for
  persona prompts and exports, and purged when the profile is deleted.

The AI systems do not depend on PDI to function; PDI is the "run on top of"
infrastructure layer they integrate with when deployed in a private
environment. Every vault access lands in PDI's hash-chained audit log, and
`GET /audit/verify` detects any retroactive edit.

## Why over HTTP, not imports

Each product is independently deployable, versioned, and separately repo'd.
Interoperation only through public HTTP APIs keeps the boundaries honest: any
project can be run, tested, and shipped without the others present.
