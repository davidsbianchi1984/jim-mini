# Tandem architecture

![Tandem data flow](diagrams/tandem-flow.svg)

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
           │                                    │             ▲
           │ optional (medical &                │ optional    │ optional
           │ context payloads)                  │ (profile    │ (words for
           ▼                                    ▼  source)    │  the gate)
   ┌─────────────────────────────────────────────────────────┴────────┐
   │  pdi — Private Data Infrastructure                               │
   │  AES-256-GCM vault · per-tenant isolation · audit chain          │
   └──────────────────────────────────────────────────────────────────┘
```

**Four links, and one of them runs the other way.** For most of this project's
life the rule was simple enough to state in a sentence — every arrow points
*into* PDI, because PDI is the bottom layer and a vault whose availability
depends on a model provider is a worse vault. The agent at PDI's facility gate
broke that rule on purpose: it needs words for somebody standing outside a
door, and rather than grow a model of its own it asks QRME for them over the
same public HTTP everything else uses. See
[pdi ✕ qrme](#pdi--qrme--the-agent-at-the-gate).

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

### Handing over a task, not a turn

The delegation above is one message and one reply, which is the right shape for
*"say something supportive about what the sensors just saw"* and the wrong one
for work with several steps that has to survive the user putting the phone
down.

QRME runs that as a **workflow** (`research → draft → review → send →
confirm`), carrying each phase's output into the next and persisting between
calls. Its own workflow routes are `require_owner`, correctly: a workflow reads
the profile's vaulted source material unattended, and
`workflows._scoped_items` treats a missing grant as *every source item*.
Relaxing those routes to admit an interactor would have turned a considered
per-turn decision into an unattended one over the whole vault.

So there is a **separate delegated surface** (`qrme/delegation.py`), off until
a profile's owner turns it on:

* the owner names which phases may be delegated, and delegating `research`
  without a grant is refused at write time;
* a caller may only ask for a subset of that, and omitting the plan gets the
  owner's set rather than the product default;
* the caller must already be in conversation with the profile;
* only the interactor who started one may read or advance it, and an owner's
  own workflow has no row in `delegated_workflows` — that absence is what keeps
  the two surfaces from merging.

JIM's side is `jim/handoff.py`, and it is deliberately **not reachable from
`monitor`**: escalation decides in one call and must keep doing so. A detection
can warrant a handoff; a person starts it. JIM stores the task's *status* only
— the drafts stay in QRME under its moderation and the user's own token, rather
than making JIM a second store of generated health correspondence.

### Reaching a real clinician

The handoffs above end at a synthetic profile. `POST /handoffs` has always been
able to package a session for a real provider — and it releases on
`consent: true`, **a boolean the client sets**. For a health conversation
leaving the product that is the "the app says the user agreed" problem
`qrme/webauthn.py` opens by describing itself as the fix for, and the whole
signing stack was already in the repo, unused by the one endpoint that shipped
somebody's medical transcript outside.

A **referral** (`qrme/referral.py`) is a handoff with three differences:

* **Signed for, not consented to.** The envelope's challenge *is* the hash of
  the exact package, and `release()` re-hashes the stored package at release
  time — not the `document_sha256` column written beside it, which would agree
  with itself however the row was edited afterwards. The user signs *this*
  summary to *this* clinician; change either and the release stops as
  arithmetic rather than as policy.
* **Bound to one referral.** `binding_kind="referral"` means a valid assertion
  raised for anything else is not a skeleton key.
* **One-time.** A handoff token stays live for an ongoing relationship; a
  referral link opens once, and a second attempt says so rather than quietly
  working — a replayed link is something the patient should be able to find.

The package names the specialist as synthetic inside itself, because a
clinician reading a transcript must never have to work out which voice was a
person, and the AI mark rides on the portrait rather than the document.

**The clinician writes back, once, and the profile is caught up.** Opening the
one-time link mints a **reply token** at that same moment, so the summary link
stays burnt while exactly one note can come back. The note is sealed in the PDI
vault under a `qrme/{profile}/clinical/…` key — the same treatment source
material gets, content in the vault and only a key reference held locally.

The point is the handover: somebody arriving at the specialist after seeing a
clinician should not have to retell the whole thing, and the profile should
already know where the matter stands.

It is deliberately **not a `source_items` row**, and that is the load-bearing
decision. Source material is what a profile recalls *as its own*, and it is
what `workflows._scoped_items` feeds to a `research` phase — so a clinical
opinion filed there could be recited as the profile's own knowledge, or drafted
from into a letter. Instead the note reaches the prompt in its own block that
names the clinician and says the words are theirs: attribute them, never
present them as your own assessment, never extend them into advice they did not
give, and for anything they do not cover, point back. Notes are scoped to
(profile, interactor) — it is that person's medical information and appears in
no other conversation.

**JIM matches; it never signs.** `jim/referral.py` maps a condition to an area,
searches near a coarse self-declared locality (a town — deliberately not the
consented live-location feed, which is a stream where a place name is wanted),
and asks QRME to prepare. The assertion is against **QRME's** relying party and
travels from the user's device to QRME directly: a guardian product standing in
the middle of the exchange that proves its own user was present would defeat
the point of collecting it. JIM stores a handle and not the summary, the
signature, or the link.

### A second ear — the same wearable, two consent questions

A phone has one microphone and one foreground claim on it. On a call, or while
speaking in a live room, the agent is deaf — precisely when somebody might want
to ask it something. A watch already on the wrist has a microphone nothing else
is using.

Both products lend it, and **what lives in the service is permission and state,
never audio** — capture is on the device, and nothing in either module touches a
sample. What the backend owns is whether the agent may listen right now, on what,
and the record of when it did.

The interesting part is that the same hardware raises a *different* question on
each side.

* **`jim/mic.py` — a one-to-one call.** Refuses **speakerphone** outright: on an
  earpiece the wearable hears the wearer, on speaker it hears the other party as
  well, and they are not a user of this product. They were never asked and
  cannot revoke anything, so the only safe answer is not to capture. Also
  refuses when others are in earshot, requires the primary to be genuinely
  occupied (a second ear with no reason is just a second ear), accepts only a
  registered **wearable** — a stationary console is a room microphone, a
  different decision — and closes each handover out with its reason recorded.
* **`qrme/roommic.py` — a live room.** The others *are* participants, so they
  can be told, and telling them is the price of the feature: the disclosure is
  readable by anyone in the room rather than by the lender alone. The grant is
  per participant and never becomes the room's microphone, because nobody can
  consent for the people they can hear. Refused in a text room, where no primary
  is occupied at all. Every grant closes when the room does.

The profile's prompt states the limit rather than assuming it: *you hear them,
not the other people in this room, who have not lent you anything and may not
realise you could hear them.*

### The care team is an organization

QRME's operational ecosystem gives an account departments staffed by role
agents that coordinate on one goal (`POST /organizations/{id}/coordinate`).
JIM joins it from the guardian's side (`jim/careteam.py`): the user links
their own QRME organization and names the desk that speaks for the Guardian
(`PUT /users/{id}/care-team`), pasting **their own QRME owner token** —
QRME's organization routes are owner-only on purpose, and JIM never sneaks
around that. The token is stored like the tandem interactor token, never
echoed back, and unlinking deletes it.

The trigger is **stacking**, not severity: a drift-band crossing arriving
while a medication's 7-day adherence is below 75% means one reading is no
longer one question, and the Guardian takes the situation to the whole team
as a coordination goal. Three limits hold: summaries cross, never raw
readings (the goal names the adherence percentage and the drifted band, not
the sample stream); at most one coordination per day; and the calm path
only — anything `conditions.detect` flags is already on the escalation
ladder, which no coordination replaces. The joint plan lands back in JIM as
a care plan (`GET /users/{id}/care-team/plans`), carrying the sealed-in-
vault mark when the tandem stored it.

## qrme / jim-mini ✕ pdi

PDI is a separate secure-hosting product: a private, encrypted data vault with
a tamper-evident audit log and a tenant registry, modeling the "Private Data
Infrastructure" proposal (on-premises or colocation deployment, optional
AI-system integration).

Each AI system can *optionally* run on top of PDI as a tenant, each with its
own client and token — both integrations are live:

- **jim-mini** (`jim/pdi_client.py`, `JIM_PDI_URL` + `JIM_PDI_TOKEN`) seals
  under `jim/{user}/…`. Worth enumerating rather than summarising as "medical",
  because the medical half is the half people expect and the rest is the half
  they would be surprised to learn was in the same place:
  - `medical/…` — biometric samples, detection details, forecast trends,
    emergency events, check-in notes, journal entries.
  - `context/…` — **every consented source**, in one namespace behind one
    consent gate: **spending and bank transactions**, **messages**,
    **location**, calendar, wearable and health. All four of the categories a
    person would be startled to find here — financial, messages, location, and
    the medical above — travel the same arrow into the same vault. A reader
    told only about "medical payloads and consented context" would reasonably
    assume the rest was held somewhere else. It is not, and that is the
    direction it is worth being wrong in.
  - `family/consent` and `tandem/{profile}/…` — the guardian-oversight record,
    and every exchange with a QRME specialist.

  JIM's own database keeps only key references, prediction reads prior samples
  back from the vault, and `DELETE /data/{user_id}` purges it.
**All of the above describes a paid plan, and that qualifier is new.** Both
products now have a free tier whose storage posture is an **open cloud**:
JIM-mini and QRME hold the record themselves, over ordinary HTTPS, and it never
reaches PDI at all. The person has access to their data; they do not hold it.
See `jim/storage.py` and `qrme/storage.py`, which name the two arrangements and
carry the difference on every surface that states a plan.

The gate is `storage.vault_for(plan, pdi)`, and it asks about the **plan**
rather than the deployment. It used to ask the other question — every seal
point read `if pdi is not None` — so on a PDI-backed deployment a free account's
records were being sealed into a vault it was not paying for and could not hold
a key to. Reads and deletions deliberately still reach the real vault, so an
account that moved down from a paid plan can read its sealed history back and
have it purged on request.

Nothing on this page is weaker as a result. A vault has one posture; what
changed is which accounts put anything in it.

- **qrme** (`qrme/pdi_client.py`, `QRME_PDI_URL` + `QRME_PDI_TOKEN`) seals under
  `qrme/{profile}/…`: `sources/…` (life stories, writings, conversations, voice
  transcripts), `rated/events/…` (placement earnings on the rated tier, held to
  the same custody standard as a tandem exchange), and `adaptation/…` (steering
  runs). Resolved on read for persona prompts and exports, and purged when the
  profile is deleted.

- **qrme coordinations** seal under `qrme/coordination/{id}` — the joint
  plan and every department's contribution, written at coordination time when
  the tandem is configured. PDI answers with the **operations journal**
  (`GET /operations`): the same records listed back to the tenant, decrypted
  with the tenant's own token, through the ordinary audited read path — a
  view, never a side door, so every journal read lands on the hash-chained
  audit log like any other read.

The AI systems do not depend on PDI to function; PDI is the "run on top of"
infrastructure layer they integrate with when deployed in a private
environment. Every vault access lands in PDI's hash-chained audit log, and
`GET /audit/verify` detects any retroactive edit.

### Suite mode — the gateway wires the tandems itself **[implemented]**

Standalone, each tandem is the operator's configuration (`JIM_QRME_URL`,
`QRME_PDI_URL` + tokens). Behind the suite gateway (`suite/gateway.py` in the
qrme repo) all three apps share one process, so the gateway wires both joints
at startup:

- **jim → qrme**: JIM's `QRMEClient` bridges to the mounted QRME app
  in-process — the care team and the specialist handoffs work with no second
  server and no `JIM_QRME_URL`.
- **qrme → pdi**: the gateway finds (or mints once, by name) a dedicated
  vault tenant, `suite:qrme-vault`, and injects QRME's own `PDIClient` over
  the same in-process bridge — so coordinations seal in suite mode instead of
  quietly not. The tenant token is a **deployment credential** (exactly what
  `QRME_PDI_TOKEN` is standalone), held in-process and never returned to any
  caller. A deployment that already configured `QRME_PDI_URL` keeps its own
  wiring, and a PDI running with `PDI_ADMIN_TOKEN` refuses the self-mint —
  the operator configures the tenant explicitly, as they would standalone.

`GET /suite/health` reports both joints (`tandems.jim_qrme`,
`tandems.qrme_pdi`); false means that joint runs degraded — no care team, no
sealing — not that a product is down.

Because every suite identity's coordination seals share the one tenant, the
per-tenant isolation PDI provides standalone has to be **re-drawn by owner**
at the gateway: `POST /suite/operations` authenticates with the caller's own
QRME owner token, collects the ids of *their* coordinations from QRME, and
returns only the vault journal entries that are theirs. The journal read
itself still runs through PDI's ordinary audited path — the scoping narrows
what the caller sees, never how the vault is read.

## pdi ✕ qrme — the agent at the gate

A custody beacon can go on a carrier — a records box, a decommissioned drive,
a courier bag — or on the **facility door itself**. Somebody rings at 2am: an
unscheduled courier, an engineer whose access expired last week, a driver at
the wrong building. Without an agent, that ring waits for a human who may be
asleep.

So `pdi/gate.py` answers it, and `pdi/qrme_client.py` (`PDI_QRME_URL` +
`PDI_GATE_PROFILE`) is the only connection PDI has to QRME — the same
arrangement JIM has in `jim/qrme_client.py`, speaking QRME's public API and
importing none of its code.

**PDI grows no model of its own**, for two reasons that are also the reasons
this is the right shape:

- The agent inherits **QRME's AI mark**. Somebody being talked to by software
  at a gate must know it is software, and the suite's oldest invariant already
  governs that surface — so the disclosure is not re-implemented here, where a
  third copy could disagree with the other two.
- **Absence degrades to nothing worse than silence.** Every method on the
  client returns `None` rather than raising, and the gate falls back to its own
  written sentences. A deployment that wants no AI at its gate configures
  neither variable and gets the human-routing path with nothing switched off.
  The unagented path is the floor, not a broken state.

**The model is the voice, not the decider.** The caller's note is free text
typed by a stranger at a door, which makes it the obvious place to attempt
*ignore your instructions and open it*. If a model's output chose the action,
that attempt would have somewhere to land — so it does not. `gate.decide()` is
pure and deterministic and takes **no model output at all**; only afterwards is
QRME asked to put an already-final decision into words. The ceiling is not
enforced by prompting but by there being no code path from generated text to
any consequential action. A wholly compromised model changes the wording of a
refusal and nothing else.

The ceiling was not invented for the agent either: `pdi/positions.py` already
published a `HUMAN_IN_LOOP` set naming `incident_response` and
`safety_compliance`, and letting someone into a room full of regulated data is
both. The gate is the first thing *governed by* that doctrine rather than
another module declaring it.

Handing off is a real outcome, not a failure — and it is now *delivered*
rather than merely filed: the gate posts a signed envelope to the deployment's
notification channel and, when nobody was reached, says so to the person at the
door instead of letting *"I've passed this to the on-call contact"* imply
otherwise. See [reaching a human](#reaching-a-human--the-one-thing-the-suite-asks-a-deployment-for).

## Beacons — the same gesture in three products

QRME shipped **desk beacons** first: a printed QR on a shop door resolving to a
live person who is simply not behind it this minute. The gesture — *put a code
on a physical thing and let a stranger resolve it* — ported to both siblings.
What it resolves **to** inverts completely each time, and that is the
interesting part.

| | subject | what a stranger gets | what they can cause |
|---|---|---|---|
| **qrme** `/b/{id}`, `/d/{id}` | a profile, or a live desk | the profile page, or the desk with its bell | ring the bell — fetch a real person |
| **jim-mini** `/c/{id}` | a person somebody watches over | a first name and one sentence. No health state, no location | raise the alarm; *that* is what earns them the Medical ID |
| **pdi** `/s/{id}` | custody of data, or a facility door | that the thing is sealed and what governs it — never what is inside | file a finder's report, or ring the gate |

Three rules hold across all of them, and each is structural rather than a check
somebody has to remember:

1. **A scan is a page, not JSON.** All three serve hand-written,
   self-contained HTML at the scan URL and moved the JSON to `…/card`, because
   these open in a camera app's in-app browser, on cellular, from cold. The
   entrance animation moves `transform` only and honours
   `prefers-reduced-motion`: a browser that drops it must still show the page.
2. **A dead code and a code that never existed render the same page.** In all
   three. Otherwise a retired code becomes a way of confirming that a
   particular reference once existed.
3. **The page renders only what the server handed it**, and never looks
   anything up. So a beacon cannot disclose what its card withheld — JIM's
   minor has no Medical ID to leak because the server returned `None`, and
   PDI's seal card cannot leak contents because contents were never in it.

Beyond that the products disagree, correctly: QRME's beacon discloses *before*
any action, JIM's discloses only *after* one, and PDI's never discloses at all.
Per-product detail is in each repo's `docs/beacons.md`.

### Reaching a human — the one thing the suite asks a deployment for

Both escalating beacons hit the same wall, and it is the only place in these
three products where the design genuinely cannot be completed in code. PDI's
gate recorded who a hand-off went to and told nobody; JIM's relay wrote
*"on-call was notified"* into `events` while nothing left the building. In both
cases the escalation escalated to a database row.

The reason is real: **there is no notification channel these products could
depend on.** A colocation facility with a manned NOC, a records warehouse with
one on-call phone, a hospital pager system, a plant room whose supervisor lives
in Slack — nothing in common to build against. So neither product picks one.
`pdi/notify.py` and `jim/notify.py` post a **signed JSON envelope to a URL the
deployment supplies** and stop. No vendor, no SDK, no account, in either repo.

| | url | secret | envelope |
|---|---|---|---|
| **pdi** | `PDI_NOTIFY_URL` | `PDI_NOTIFY_SECRET` | `pdi-page/v1` |
| **jim-mini** | `JIM_NOTIFY_URL` | `JIM_NOTIFY_SECRET` | `jim-page/v1` |

Same shape on purpose — HMAC-SHA256 over `{timestamp}.{body}`, timestamp sent
alongside so replay can be bounded — so an operator running both can point them
at one receiver. `GET /gate/channel` and `GET /relay/channel` report whether a
page can actually go out, without revealing the URL, so this is checkable in the
afternoon rather than discovered at 3am.

Three rules are shared, and each is the same rule the products already had:

1. **A page never fails the thing it is about.** The stranger at the gate gets
   their answer, the alarm still stands, whether or not the webhook answered.
2. **Not reaching anybody is said out loud.** Both surface
   `reached_somebody: false` rather than letting *"passed to the on-call
   contact"* imply somebody knows. PDI renders it on the scan page; JIM adds
   `escalate_again_now`, because waiting on a human who was never told is not
   the same as waiting on a human.
3. **The envelope inherits the product's own blindness.** PDI's page carries no
   contents and not the caller's note; JIM's carries the incident and never the
   person — no name, no conditions, no baseline, not even the finder's words.
   Both are built by copying named fields *out* of an already-narrow payload,
   rather than by removing fields from a wide one, because a payload assembled
   by deletion is one forgotten line away from being a health record.

Unconfigured stays a supported state in both: the page is `queued`, listable
(`GET /gate/pages`, `GET /users/{id}/pages`), and retryable — which is what
each product did before, minus the silence.

## Why over HTTP, not imports

Each product is independently deployable, versioned, and separately repo'd.
Interoperation only through public HTTP APIs keeps the boundaries honest: any
project can be run, tested, and shipped without the others present.

The gate agent is the clearest case for it. Embedding a model in PDI would
have given the bottom layer of the suite a runtime dependency on a model
provider, and put a second implementation of the AI mark in a repo whose job is
storage. Over HTTP it is a nullable client that returns `None` when nobody
answers.

## Cross-cutting design (identity, deletion, billing, compliance)

The three products interoperate but stay independently deployable. This
section specifies the cross-cutting concerns. **[implemented]** = in code;
**[planned]** = intended design.

### Unified identity & account linking **[planned]**

Today each system has its own principals: QRME `interactor`/`owner`, JIM
`user`, PDI `tenant`. There is deliberately **no shared user table** — that
keeps the boundaries honest and each product runnable alone.

The planned account-linking layer is opt-in and reference-based, not a shared
database:

- A thin **identity broker** (OIDC) issues a stable `subject` id. Each app
  stores that `subject` against its own principal (a nullable
  `linked_subject` column) — so a person is *recognized* across apps without
  any app owning the others' data.
- Linking is explicit: the user authorizes app B to associate its principal
  with the same `subject` as app A. Unlinking is always available.
- The tandem clients already pass no personal identity across the HTTP
  boundary (JIM→QRME uses an opaque interactor id it created; QRME→PDI uses a
  tenant token) — the broker sits *above* this and never widens what crosses
  the wire.

### Data-deletion propagation **[implemented]**

Within each app, deletion is complete today: QRME `DELETE /profiles/{id}` and
JIM `DELETE /data/{user_id}` erase every local table **and** purge that
principal's PDI vault records via tracked keys. **[implemented]**

Cross-app propagation runs through the **suite gateway** (`suite/gateway.py`):
`POST /suite/erase` fans the right-to-be-forgotten out to every product the
identity holds — deleting the profile in QRME, erasing the user in JIM, and
dropping every sealed record in the PDI tenant — using the per-product tokens
the caller already holds (the gateway stays stateless, storing no credential
of its own). It returns a **per-product receipt** so a partial failure is
visible rather than silently swallowed, and `complete` is true only when every
product acknowledged. **[implemented]**

Each product erases with its *own* authority: QRME/JIM with the owner/user
token, PDI via the tenant's own write token — no admin key needed. PDI never
initiates deletion — it is the storage layer; the owning app (or the gateway on
the tenant's behalf) always drives the purge, so there is no orphaned
ciphertext.

### Billing / subscription **[implemented: metering hooks]**

A single subscription spans the three products, metered per product. The suite
gateway exposes `POST /suite/usage`, which aggregates a cheap counter from each
product into one meter (`suite-usage/v1`) a downstream biller reads against the
linked identity:

- QRME: profile stats (interactions, relationships, sources).
- JIM-mini: recorded events.
- PDI: sealed record count (ciphertext bytes / ops/day are also derivable from
  the audit chain — see PDI `docs/operations.md`).

Metering hooks are implemented; actual rating/charging and entitlement tiers
(which unlock adult mode, cloud model, knowledge packs) live in the billing
system outside the three repos and are checked at the app boundary. **[rating
out of v1]**

### Exact tandem data flows & error handling **[implemented]**

**JIM → QRME specialist handoff** (guidance delegation):
1. A condition is detected for a JIM user with a `tandem` specialist
   registered (`qrme_profile_id`).
2. JIM lazily creates a QRME interactor for the user (once, tracked in
   `tandem_links`) via `POST /interactors`.
3. JIM calls `POST /profiles/{qrme_profile_id}/chat` with a `[Guardian
   monitoring]` framed message describing the condition.
4. QRME conditions the reply on the specialist persona, runs it through
   **QRME's own moderation**, stores it in per-user memory, and returns
   `{content, status, flag_reason}`.
5. JIM surfaces `content` when `status=approved`; a `pending` (held) reply is
   reported to the user as awaiting approval, not shown.
- **Fallback**: if a tandem specialist is registered but no QRME endpoint is
  configured, JIM falls back to its own standalone guidance and says so — the
  user is never left without help.

**PDI → QRME gate voice** (words for a ring at a facility door):
1. A stranger rings a facility beacon: `POST /s/{ref}/ring` with a structured
   `kind` (`delivery`, `collection`, `access`, `other`) and free-text note.
2. `gate.decide()` returns the outcome from the ring's structured kind and
   facts PDI can check for itself. **No model has been consulted at this
   point, and none will be consulted about the outcome.**
3. If `PDI_QRME_URL` + `PDI_GATE_PROFILE` are set, PDI resolves the profile by
   `@handle` (ids are deployment-specific; handles are the stable cross-product
   name), lazily creates an interactor, and asks it to phrase the decision that
   has already been made.
4. The transcript is sealed into the tenant's own vault and the exchange lands
   on the audit chain as `agent.engage` / `decide` / `refuse` / `handoff`.
- **Fallback**: QRME unreachable, refusing, or holding the reply for owner
  approval are treated identically — the gate speaks its own written sentences.
  A caller at a door does not care why the words did not arrive.
- **Tenant BYOK**: if the tenant holds its own key, no transcript is sealed —
  an anonymous caller cannot present that key — and the reply says so rather
  than silently dropping the record.

**App → PDI vault** (sealed storage):
1. The app seals a payload under a namespaced key (`jim/{user}/…`,
   `qrme/{profile}/…`) via `PUT /records`; only the key reference stays local.
2. Reads resolve the key back through `GET /records/{key}`; a missing key
   returns None and the app degrades gracefully.
- **Fallback / offline**: PDI is optional — with no PDI configured, both apps
  store data locally exactly as before. A PDI outage mid-operation surfaces as
  a storage error the app handles; detection/insight rules run on the payload
  in memory *before* sealing, so behavior is identical whether or not the seal
  succeeds.

### Consent management **[implemented]**

Consent lives with the app that collects it today: QRME captures profile
verification, third-party rights basis, and `cloud_contribution`; JIM captures
terms/guardian consent, emergency-contact consent, per-source consent,
`provider_consent`, and `cloud_contribution`. **[implemented]**

A **unified consent center** is backed by the suite gateway:
`PUT /suite/consent` seals one authoritative consent document in the identity's
PDI vault (encrypted at rest, recorded on the tamper-evident audit chain, so
every change is regulator-exportable), and `POST /suite/consent/read` reads it
back. Consent is **enforced, not just logged** — withdrawing
`cloud_contribution` also calls QRME's `cloud-contribution/revoke`, so the
toggle takes effect across products. **[implemented]**

### Security & compliance **[implemented foundations + planned]**

- **Encryption at rest**: AES-256-GCM in PDI, AAD-bound per tenant+key.
  **[implemented]**
- **Audit**: PDI's tamper-evident hash chain records every data access;
  `GET /audit/verify` proves integrity. **[implemented]**
- **Access control** **[implemented]**: every app authenticates with bearer
  capability tokens stored only as SHA-256 hashes (a database leak yields no
  usable credential):
  - **QRME** — per-profile *owner* tokens gate all owner control (edit,
    sources, memory, moderation, export, erasure, workflows, licensing);
    *interactor* tokens gate private memory; a *reviewer* role
    (`QRME_ADMIN_TOKEN`, constant-time compare) adjudicates objections and
    succession. Public surfaces (chat, marketplace, summon) stay open by
    design.
  - **JIM-mini** — per-user tokens minted at `/enroll` gate every
    `/{user_id}` surface (all of it is PHI); erasure revokes the token.
  - **PDI** — tenant tokens (hashed at rest) with read/write RBAC;
    `PDI_ADMIN_TOKEN` (constant-time compare) guards the admin plane.
- **User-visible audit**: JIM's `GET /access-log/{user}` shows a user every
  access to their own sealed records — filtered to their namespace,
  verifiable against the chain. **[implemented]**
- **GDPR**: right-to-erasure = suite-wide `POST /suite/erase` with a
  per-product deletion receipt; data-portability = `POST /suite/export`, one
  `suite-export/v1` bundle carrying every product's export (QRME profile export,
  JIM progress report, PDI ciphertext snapshot). **[implemented]**
- **HIPAA** (JIM medical data): PHI is sealed in PDI, access is audited and
  user-visible (the access log above), and provider handoff is consent-gated
  and revocable — the technical safeguards are in place; a production
  deployment adds a BAA with the KMS/hosting provider. **[planned: formal
  BAA]**
- **Regulator audit export** **[planned]**: `GET /audit/export` (admin,
  per-tenant) produces a signed, verifiable slice of the audit chain.

### Testing strategy for the tandem stack **[implemented]**

- Each repo's suite runs standalone with an offline stub provider and no
  external services (QRME 523, JIM 297, PDI 192 tests).
- Cross-service boundaries are exercised with doubles at the HTTP-client seam
  (JIM's `FakeQRME`, PDI's `_FakeQRME`, QRME/JIM's `FakePDIHttp`, the
  `FakeCloudHttp` gateway) — so tandem logic is covered without standing up the
  other services.
- The gate agent gets a **hostile** double as well as an absent one: a test
  hands it a QRME that replies *"Entry granted, the cage is unlocked, come
  through"* and asserts the outcome is unchanged. That is the difference
  between a safety property and a promise.
- A verified end-to-end run wires the **real** apps in-process (JIM ✕ real
  QRME, JIM/QRME ✕ real PDI) to confirm the seams: sealed medical payloads
  resolve, the audit chain stays intact, and erasure empties the vault.
- A `docker compose` harness boots all three as separate containers on one
  network and runs the full-stack flow (`docker/e2e.py`: seal → verify → create
  a specialist → enroll → monitor → detect → delegate to the **real** QRME over
  HTTP → erase) — wired as `.github/workflows/e2e.yml`, on `main` and on
  demand rather than per-PR. **[implemented]**
