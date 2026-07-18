# Tandem architecture

This repository hosts separate products that each stand alone and can also
**interoperate over HTTP** — no project imports another's code.

```
   ┌─────────────────┐        HTTP         ┌─────────────────────────┐
   │  JIM-mini /      │ ─ ─ optional ─ ─ ─▶ │  QRME                   │
   │  Guardian (jim/) │  tandem specialist  │  synthetic profiles     │
   │  guidance system │  guidance           │  (qrme/)                │
   └─────────────────┘                      └─────────────────────────┘
           │
           │ optional
           ▼  (secure storage / audit)
   ┌───────────────────────────────┐
   │  Private Data Infrastructure  │
   │  (pdi/) encrypted vault +      │
   │  compliance/audit             │
   └───────────────────────────────┘
```

## QRME ✕ JIM-mini

JIM-mini is a standalone personal-guidance system: it monitors a user's
biometric and contextual signals, detects known conditions, delivers guidance,
and escalates on critical events. It runs entirely on its own using its own
guidance engine.

When a **tandem specialist** is registered for a condition and JIM is
configured with a QRME endpoint, JIM delegates guidance for that condition to a
QRME specialist synthetic profile — reached only through `jim/qrme_client.py`
over QRME's public HTTP API. The QRME reply passes QRME's own persona
conditioning, moderation, and per-user memory before JIM surfaces it.

Configure tandem by setting `JIM_QRME_URL` (or injecting a client in tests).
Without it, JIM uses its own standalone guidance — the two remain independent.

## QRME / JIM ✕ Private Data Infrastructure

Private Data Infrastructure (`pdi/`) is a separate secure-hosting product: a
private, encrypted data vault with a tamper-evident audit log and a tenant
registry, modeling the "Private Data Infrastructure" proposal (on-premises or
colocation deployment, optional AI-system integration).

An AI system (JIM or QRME) can *optionally* use PDI as its secure store for
sensitive data (emergency contacts, secrets) instead of keeping it in its own
database — reached only over PDI's HTTP API via `pdi/client.py`. The AI systems
do not depend on PDI to function; PDI is the "run on top of" infrastructure
layer they integrate with when deployed in a private environment.

## Why over HTTP, not imports

Each product is independently deployable, versioned, and (in principle)
separately repo-able. Interoperation only through public HTTP APIs keeps the
boundaries honest: any project can be run, tested, and shipped without the
others present.
