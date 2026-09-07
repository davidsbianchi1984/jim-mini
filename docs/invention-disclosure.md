# Invention Disclosure — JIM-mini / Guardian

*Inventor: David Bianchi. Recorded 2026-07-29. This document, together
with this repository's commit history and tagged releases, is a dated
public record of conception and reduction to practice. It is written to
be handed to a patent attorney as the starting point for provisional
applications. It is a factual record, not legal advice and not a license
(see LICENSE).*

Each item names the mechanism, where it is reduced to practice in this
repository, and the release that first shipped it.

## 1. Wearable-to-guardian bridge requiring no vendor app store

**The process:** health readings from a closed wearable ecosystem
(Apple Watch / HealthKit) reach an independent guardian service on any
host OS using only capabilities every iPhone ships with — with the two
halves designed as one channel:

- **Deposit-only drip channel.** A per-user URL-borne token
  (`POST /watch/drip/{token}`) receives samples POSTed by a phone-native
  automation (Shortcuts) on a schedule. The credential is intentionally
  asymmetric: it can deposit readings into exactly one user's stream and
  can never read guidance, identity, or health state back out — the
  response is limited to a receipt count and a boolean. An unknown token
  answers 404, never 403, so the endpoint cannot be used to confirm a
  channel exists. Rotation retires an address in one step.
  (`jim/watch.py`; shipped v0.6.0.)
- **Historical export as instant baseline.** The wearable vendor's
  user-initiated data export (`export.zip`) is folded into per-metric
  personal baselines as *one value per metric per day — the median of
  that day's resting readings — applied in chronological order* to an
  exponential moving average, so the learned baseline walks the same
  path the person did. Exercise contamination is excluded by the
  vendor's own motion-context annotation (only sedentary heart-rate
  records fold). The import writes no events and raises no alerts:
  history is treated as context, never as news. Combined effect: the
  personal baseline and its thresholds are *armed the same day the user
  enrolls* instead of after days of live learning.
  (`jim/watch.py:seed`; shipped v0.6.0.)

## 2. Personal drift bands distinct from a clinical alarm layer

**The process:** two separate questions answered by two separate layers —
"is this an episode?" (population-rule detection with an escalation
ladder) and "am I drifting from my own normal?" (per-metric bands around
the individually learned baseline). Distinctives: each band has
independently watchable low/high edges with per-metric defaults matching
physiology (HRV and SpO₂ watch only the low side); one sensitivity dial
scales every band; a band whose baseline is provisional stays silent by
design; a crossing produces a *question* (`severity="checkin"`) that can
never escalate to an emergency contact — the alarm layer remains the only
path there. (`jim/bands.py`, `jim/guardian.py`; shipped v0.5.0.)

## 3. Signal-quality-capped escalation

**The process:** every incoming sample is graded for believability
(skin-contact loss, physiologically implausible jumps, sensor artifacts)
and the grade travels with the sample, capping how far the escalation
ladder may climb on it — rather than dropping the reading or alarming on
it. (`jim/signal.py`, `jim/guardian.py`; shipped v0.4.x line.)

## 4. Degrade-not-fail model layer with disclosed provenance

**The process:** any model-provider failure (missing key, SDK, network,
overload) degrades to a deterministic local fallback so a health product
never goes dark — and the reply carries honest provenance: which provider
actually produced the words, whether that was a degrade, and an
actionable reason, rendered to the user. A request-scoped
bring-your-own-key header outranks the deployment credential and is never
persisted or logged. (`jim/llm.py:generate_for_user`,
`FallbackProvider`; shipped v0.6.1. BYO-key: v0.4.3 line.)

## 5. Version-matched backend adoption in the desktop shell

**The process:** the desktop shell adopts an already-running local
backend only when the backend's self-reported version matches the shell's
own; otherwise it takes a free port and starts its matching backend —
eliminating the class of upgrade bug where a stale resident backend
serves an old API to a new UI. (`app/electron/main.cjs`, `/health`
version handshake; shipped v0.4.7.)

## 6. The vigil — an alarm on the absence of signals

**The process:** every monitored-person product alarms on readings; this
alarms on their *absence*. A steward is named, and the message they will
receive is authored, by the user in advance; silence is measured against
the product's own event stream (any sign of life resets it without
bookkeeping, and the vigil's own trip is excluded from the measurement);
the trip is idempotent, never escalates past the steward, and is stood
down automatically by the next reading. Cross-product: the trip's event
id serves as the attestation reference for ownership succession (QRME)
and bequest activation (PDI). (`jim/vigil.py`; shipped v0.8.0.)

## 7. Interoperating three-product architecture

**The process:** a guardian (JIM-mini), a synthetic-profile studio
(QRME), and an encrypted personal-data vault (PDI) cut as one versioned
combination, with cross-product session continuity, sealed tandem
exchanges with auditable custody, and per-plan custody postures. (See
the sibling repositories' disclosures; convention documented in each
CHANGELOG since v0.1.6.)

## The care-team stacking rule

**The process:** a guardian system that escalates to cross-agent
coordination on *stacked* signals rather than severity — a personal
drift-band crossing arriving while medication adherence is below a
floor — taking the situation to the user's own organization of
role-specific agents as one goal, under three structural limits:
summaries cross but raw readings never do; at most one coordination per
cooldown period; calm path only, with the escalation ladder untouched.
The user's own credential authorizes it, stored like the tandem token,
never echoed, deleted on unlink (`jim/careteam.py`; shipped v0.13.0,
recorded 2026-07-29).

---

*Attorney notes: repository first became public before this disclosure;
for jurisdictions with grace periods, the earliest public commit and the
earliest tagged release containing each mechanism (listed above) are the
operative dates. Git tags `app-v*` are signed by the availability of the
corresponding GitHub Releases.*
