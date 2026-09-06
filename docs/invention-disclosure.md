# Invention Disclosure — JIM-mini / Guardian

*Inventor: David Bianchi. Recorded 2026-07-29. This document, together
with this repository's commit history and tagged releases, is a dated
public record of conception and reduction to practice. It is written to
be handed to a patent attorney as the starting point for provisional
applications. It is a factual record, not legal advice and not a license
(see LICENSE).*

Each item names the mechanism, where it is reduced to practice in this
repository, and the release that first shipped it.

*Updated 2026-09-06: mechanisms 8–15 added. Each names the release that first shipped it; the recorded date above is the original disclosure's and is unchanged.*

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

## 8. The reach-out cascade, with the contact's choice on the keypad

**The process:** when a critical reading goes unanswered the guardian
calls the person's emergency contacts one after another, from the
person outward. Before anything else the contact chooses on the keypad
— hear the message, or never be called again — and one call event
decides *reached* or *unreached* for the whole ladder, so a voicemail is
not a person. The cascade's acute trigger is a crash watch: the vigil
measures silence in days and wakes a steward, this measures a pulse
going shallow in minutes and starts the calls. The transport is real —
a telephony vendor rings, speaks, listens and reports, with the
guardian's half holding the number rules and the voice door
(`jim/reachout.py`, `jim/crashwatch.py`, `jim/telephony.py`; shipped
v3.0.1, v3.0.2, v3.0.8).

## 9. The emergency send built to completion and held shut in source

**The process:** the one thing a health product must not do by accident
is place an emergency call. The dialer assembles a dispatcher-ready
briefing — who, conditions, medications, vitals, the life-saving steps
in progress — relays it to the trusted person and every connected
device, and carries the whole cascade to the transport; and the send
itself is held by a constant in source, `SEND_ENABLED = False`, that no
setting, plan or waiver opens. The posture is proven rather than
described: a test walks every door and shows each one shut, and the
ladder is held to end at a person (`jim/dialer.py`; shipped v3.0.1 and
held at every release since; posture test v3.0.10).

## 10. The moderated mailbox

**The process:** the coach agent carries on correspondence — reads what
comes in, drafts a reply, answers back and forth — and nothing leaves
without a person approving it. Every message the agent would send is
composed as a draft and held in a moderation queue the owner reads; the
send is the owner's act. The same holding rule the dialer keeps, applied
to mail (`jim/mailbox.py`, `jim/mailer.py`; shipped v3.0.3).

## 11. The offline training corpus, and a learn task that plants itself

**The process:** a sealed machine with no local model answers with a
stub, and a local model cannot learn from exchanges nobody kept. Every
exchange the agents have is banked as a training record on the machine;
when capture is on, a standing learn task plants itself in the vault
and archives the bank on its own clock, and turning capture off takes
the task back. Nothing about the bank leaves the host (`jim/corpus.py`;
shipped v3.0.4, v3.0.7).

## 12. App edits held at apply, under company oversight

**The process:** a person proposes a change to the application itself —
with an assistant that writes the code, in the widget screen — and the
proposal is held as a row with a state rather than applied or lost.
Two lanes carry it: a submission the reviewer's queue shows on a
screen, and an apply that waits for that review. `BOX_SLOTS = 2`
bounds how many proposals are tried at once (`jim/appedits.py`; shipped
v3.0.5, v3.0.6).

## 13. The coding assistant's box

**The process:** a proposed change is tried inside four walls before a
person judges it: the assistant's draft runs in a workroom confined by
an AppArmor profile loaded on the host and a seccomp filter carried
with the container, with no route out. The box opens on the hosted
deployment and on a busy server alike, and the person sees what the
draft did rather than what it said it would do (`jim/workroom.py`,
`jim/appedits.py`, `docker/jim-box.apparmor`, `docker/jim-box.seccomp.json`;
shipped v3.0.11, v3.1.0).

## 14. The lookout: a page the vault keeps fresh on the person's behalf

**The process:** "keep an eye on this page" becomes one standing task in
the vault's resident, re-run on an interval inside the facility with no
cron, no worker and no caller. The coach conditions its answers on the
watched pages beside the person's sealed records, says when a page
changed and why a fetch failed, and the same task grows ears — a page
that is a video is heard into words before it is read
(`jim/lookout.py`, `jim/coach.py`; shipped v0.88.0–v0.90.0, ears
v0.94.0).

## 15. Cues read from a room, footage never kept

**The process:** the person's own cameras and speakers are read for
visual and verbal cues — a fall, a call for help, a silence where
speech should be — and what is kept is the cue, timestamped and graded,
never the footage or the audio. The cue lands on the same escalation
ladder as a reading, under the same quality caps (`jim/cues.py`;
shipped v0.98.0).

---

*Attorney notes: repository first became public before this disclosure;
for jurisdictions with grace periods, the earliest public commit and the
earliest tagged release containing each mechanism (listed above) are the
operative dates. Git tags `app-v*` are signed by the availability of the
corresponding GitHub Releases.*
