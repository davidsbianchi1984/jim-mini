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
| `POST /v1/contributions/revoke` | `{refs}` → how many were deleted |
| `POST /v1/problems` | Content-free error report from a console → `202` |
| `GET /v1/problems` | The error aggregate, worst first |

Authentication: `Authorization: Bearer <token>`, one per contributing
deployment (`CLOUDGW_TOKENS=name:token,...`), so the intake records *which*
deployment contributed rather than only that something did. With none
configured the gateway is open to callers on this machine and closed to
everyone else — the same fail-closed posture as PDI's admin surface, because
an open gateway on a routable address is somebody else's model bill and an
unattributable corpus.

`GET /v1/problems` is the one endpoint with a *narrower* gate than the bearer
token, and the reason is worth stating: the token that posts error reports is
compiled into every installer, so it is public the moment somebody unzips one.
Writing is safe to hand out because a wrong write costs a wrong counter.
Reading is a live map of what fails on every build, so it stays with the caller
names in `CLOUDGW_PROBLEM_READERS` — unset meaning the local developer and
nobody else.

## Running the gateway

The gateway is in this repository (`cloudgw/`):

```bash
CLOUDGW_MODEL=claude-fable-5 ANTHROPIC_API_KEY=... \
CLOUDGW_TOKENS="acme:$(openssl rand -hex 24)" \
CLOUDGW_PDI_URL=https://vault.example.com CLOUDGW_PDI_TOKEN=pdi_... \
python -m cloudgw --port 8300
```

### In a container

```bash
docker build -f cloudgw/Dockerfile -t cloudgw .
docker run -d -p 8300:8300 -v cloudgw-data:/data \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -e CLOUDGW_TOKENS="consoles:$(openssl rand -hex 24)" \
  -e CLOUDGW_PROBLEM_READERS=me \
  cloudgw
```

A separate image from the QRME app on purpose: the gateway is the component
several deployments share, so it has a different lifecycle and no reason to
carry a Node toolchain or a studio build. It runs as a non-root user, writes
exactly one file, and reads none of yours. `CLOUDGW_PROBLEMS_PATH` defaults to
`/data/problems.json` inside the image, so the named volume is what makes the
error counters survive a redeploy.

The token in `CLOUDGW_TOKENS` under the name `consoles` is the one you compile
into installers as `PROBLEM_TOKEN`. It is public the moment somebody unzips an
installer, which is why it can post reports and not read them — give your own
name to `CLOUDGW_PROBLEM_READERS` and use a second token for that.

`/health` needs no token, deliberately: a health check an orchestrator cannot
run without a secret is one it will not run.

It prints what it is actually configured for at boot — an operator who thinks
they are serving a hosted model from a stub, or collecting into a vault that
isn't there, finds out immediately rather than from a quiet corpus later.

| Variable | Effect |
|---|---|
| `ANTHROPIC_API_KEY` | Serves the hosted tier. Unset = a deterministic stub, which names itself a stub in `/v1/model` and `/health` so nothing can mistake it for a real model. |
| `CLOUDGW_MODEL` | Which model to serve (default `claude-fable-5`). |
| `CLOUDGW_TOKENS` | `name:token` pairs. Required for any caller off this machine. |
| `CLOUDGW_PDI_URL` / `CLOUDGW_PDI_TOKEN` | The contribution vault. **Without it contributions are refused**, not written somewhere unencrypted — inference keeps working. |
| `CLOUDGW_PROBLEMS_PATH` | Where error counters are kept. Unset = counted in memory and gone when the process is. |
| `CLOUDGW_PROBLEM_READERS` | Caller names allowed to `GET /v1/problems`. Unset = the local developer only. |

### The intake refuses rather than sanitizes

Contributions arrive already anonymized: only the contributing deployment
knows what its identifiers are, so only it can strip them properly. The
gateway assumes that worked and checks anyway, because a gateway accumulates
a corpus from deployments it does not control running versions it did not
ship — and one client bug puts real names in the training data, discovered
much later if at all.

`cloudgw/screening.py` refuses a payload carrying an identifying field at any
depth, a product-shaped id, or an email address, with a **422 naming the
offending field**. Quietly sanitizing would hide the client bug that produced
it; refusing tells that deployment's operator their build is leaking, while
it can still be fixed. It is importable on its own, so an operator can run it
over a corpus they already have.

## Error reports

The consoles record every failed request — the operation and the status, never
the message and never the path as it was actually called.
`POST /profiles/{id}/chat → 500` identifies a bug, where
`POST /profiles/prf_0de08e794ed0/chat` identifies a person.
Only the first is written down, and the redaction happens before the
row is stored, so the buffer never holds a value that would have to be scrubbed
later.

The backends put user input straight into their error messages — a device name,
a body site, a language code. Those are good messages for the person reading
them and the wrong thing to keep, so they are shown and not recorded.

A build sends only if it was built with an address:

```bash
PROBLEM_COLLECTOR=https://gw.example.com PROBLEM_TOKEN=… npm run build
```

Unset, and the installer has nowhere to send. That is a stronger default than a
flag — there is no address for a later mistake to switch on. When an address is
set, the console posts once at launch, alongside the update check, and swallows
every failure; a diagnostic that can delay a launch has stopped being worth
having.

**Nothing is sent before the person has been asked.** Sending is opt-*out*,
which only means something if the opting-out can happen before the first
report rather than being discovered afterwards in a panel nobody opened. So
`sendProblems` refuses until a first-run notice has been answered, and that
notice renders the actual payload rather than describing it — the claim and
the object are the same thing, so the notice cannot go stale while still
looking honest. Both answers are offered, the answer is remembered, and the
switch on the Settings card is the same answer, changeable at any time.

Only where a collector exists. A build with nowhere to send has nothing to
explain, and interrupting somebody to describe something that cannot happen
teaches them these notices are noise.

Counts go as **deltas**. Each row remembers how much of itself has been
reported, so reopening the app twenty times does not turn one broken screen into
twenty. A failed send moves nothing, and the next launch tries again.

| Recorded | Never recorded |
|---|---|
| operation (`POST /profiles/{id}/chat`) | the error message |
| status (`0` = never reached a server) | ids, tokens, key names |
| count, date (day only) | request or response bodies |
| product, app version, platform | any time finer than a day |

### Cross-origin, on purpose

The gateway answers preflights from any origin with credentials off. That is
not a weakening: an Electron renderer's origin is `null` (it loads the console
from `file://`) and a dev console's is whatever port Vite picked, so there is
no allowlist that could be written and stay true. Without it the browser's
preflight gets a 405, every report fails, and the sender swallows failures —
the feature would be dead in the field with nothing to show for it.

What CORS protects is *ambient* authority: a hostile page using a cookie the
browser attaches for you. There is none here. Every endpoint needs a bearer
presented explicitly, and credentials stay off so it keeps working that way.

### This intake refuses too, and harder

`cloudgw/problems.py` accepts exactly five top-level keys and exactly five per
problem, and **422s on anything else** — an extra field, a path with an
unredacted id still in it, a `platform` string long enough to hide a sentence,
a `day` with a time of day in it.

It could redact that path itself; the pattern is right there. It does not,
because then a build whose redaction had broken would keep working and nobody
would learn that every report from those users had been arriving with a profile
id in it. Refusing is also cheaper here than next door: a rejected error report
costs one lost diagnostic, where a rejected contribution costs somebody their
donated work.

What survives is less than what arrives. Reports are not stored as reports —
they fold into counters keyed by product, version, platform, operation and
status. Locale is validated and then dropped, and nothing records that a
particular install sent anything, or when beyond the day. That is why these
counters sit in a plain file while contributions are sealed in PDI: the
contributions are people's own words, and these have no owner to protect.
Encrypting them would look careful and mean nothing.
