# JIM-mini / Guardian internals

The exact rules behind detection, prediction, escalation, and the life layer.
**[implemented]** = in code and tested; **[planned]** = intended design.

## Personal biometric baseline

- **Seeded** at enrollment: `resting_heart_rate` is captured on `/enroll`.
  Detection thresholds are computed *relative* to this baseline, not to
  population constants — a resting-60 user and a resting-80 user trigger at
  different absolute heart rates. **[implemented]**
- **Per-sample fallback**: a sample may carry its own `resting_heart_rate`;
  otherwise the enrolled baseline is used; otherwise a conservative default
  of 70 bpm. **[implemented]** (`guardian.monitor`, `conditions.detect`)
- **Rolling update** **[planned]**: the baseline should adapt over time. The
  design: an EMA of resting-state samples (samples taken while `activity_level`
  is low and no condition is active), `baseline ← baseline + α·(sample −
  baseline)` with α≈0.05, updated nightly. Baselines are stored per-metric
  (HR, HRV, respiration, SpO₂, BP) so each threshold floats with the person.
  Until enough resting samples exist, the enrolled/default seed is used and
  the system is explicit that the baseline is provisional.

## Detection rules **[implemented]** (`jim/conditions.py`)

Evaluated in priority order; the first match wins (highest-severity signals
are checked first):

1. **Crisis language** in free text (regex: "kill myself", "end it all",
   "suicide", "hurt myself", "don't want to live") → `anxiety`, **critical**.
2. **Movement** `fall`/`collapse` → `physical_injury` critical; `immobile` →
   guidance.
3. **Speech** `slurred`/`incoherent` → `physical_distress` critical (stroke
   pattern).
4. **Body temperature** ≥38.5 °C or <35 → guidance; ≥40 or <35 → critical.
5. **Blood pressure** systolic ≥160 or diastolic ≥100 → guidance; ≥180/≥120
   → critical (hypertensive crisis).
6. **HRV** <20 ms → `stress` guidance (sustained load).
7. **SpO₂** <90 % → guidance; <88 → critical.
8. **Heart rate** ≥ resting + threshold, with respiratory-rate corroboration
   (≥20/min or absent). Threshold is **+40 bpm** normally, **+30 bpm** if the
   user declared an HR-sensitive known condition (anxiety/stress/phobia).
   ≥ resting + 70 → critical.
9. **Text cues** for anxiety, depression, stress, phobia, financial stress,
   relationship distress, physical injury → guidance.

Severity ladder: `info` (log only) → `guidance` (deliver help) →
`critical` (deliver help **and** escalate).

## Predictive early warning **[implemented]** (`conditions.forecast`)

Fires when nothing has crossed a threshold yet. Logic: given the current HR
and the last two prior HRs, if the three are strictly rising, the current HR
is ≥ resting + 25, and the rise across the window is ≥ 15 bpm, emit a
`forecast` event (`info`) and a "may be building" insight — catching a stress
or anxiety episode before it manifests. Prior samples are read back from the
PDI vault when tandem storage is on, so prediction works without keeping
medical data locally.

**Knowledge packs for thresholds** **[planned]**: the request for
"purchaseable/downloadable knowledge for thresholds" maps to a
*specialist knowledge-pack* model — signed, versioned rule bundles per domain
(cardiac, metabolic, mental-health, financial-stress, career, etc.) that
supply threshold tables and baseline-update coefficients. A pack is a JSON
manifest (`domain`, `version`, `signals`, `thresholds`, `baseline_alpha`,
`references`) loaded into the detection layer; the current transparent rules
are the built-in default pack. Distribution would ride the marketplace.

## Handling conflicting / noisy signals

- **Corroboration today** **[implemented]**: the HR rule already requires
  respiratory-rate agreement (or absence) before firing, so a lone HR spike
  from a loose strap doesn't escalate on its own.
- **Confidence & sensor fusion** **[planned]**: each sample carries an
  optional `confidence` (0–1) per sensor; a detection's effective severity is
  gated by the minimum confidence of the signals that produced it. Conflicting
  signals (e.g. high HR but normal HRV and normal respiration) lower
  confidence and downgrade critical→guidance→info. A short debounce window
  (N consecutive corroborating samples) suppresses transient artifacts before
  escalation.

## Escalation decision tree **[implemented]** (`guardian._escalate`)

For a **critical** detection:

1. **Guidance is always delivered** first (local engine or the tandem QRME
   specialist), regardless of severity.
2. **Emergency contact** is notified when the user enrolled one *and* gave
   `contact_consent`. The escalation event records
   `notified_emergency_contact` and the contact.
3. **Live human help** is flagged (`live_support: true`) on every critical
   escalation — the handoff to a live counselor / emergency services.

**Tunable sensitivity** **[planned]**: a per-user `sensitivity` setting
(`cautious` / `balanced` / `assertive`) shifts the guidance/critical
boundaries — `cautious` escalates earlier (lower thresholds, contact on
guidance-level for declared conditions), `assertive` requires stronger
signals. Exposed as `PUT /sensitivity/{user_id}`; defaults to `balanced`.
Escalation routing (contact vs. live help vs. guidance-only) is expressed as
an ordered policy the user can reorder.

## Life layer details **[implemented]** (`jim/life.py`, `jim/coach.py`)

- **Smart goals**: progress is a 0–1 float; reaching 1.0 flips status to
  `completed` and emits a praise insight.
- **Habit streaks**: `streak()` counts consecutive logged days ending at the
  most recent log (a gap resets it); milestones at 7/30/100 days emit
  insights.
- **Proactive insight rules** (deliberately transparent): spending ≥ $200 →
  alert; sleep ≥7.5 h → praise, <6 h → nudge; calendar keyword "interview" →
  career prep; mood ≤2 → mindful-break suggestion.
- **Journaling + check-in crisis pipeline**: a journal entry or check-in note
  runs the *same* `guardian.monitor` detection as a biometric sample, so
  crisis language in a sad entry escalates identically — contact notified when
  consented.

## Provider handoff **[implemented, in QRME]**

JIM-mini surfaces the local-provider directory and consented session handoff
through the tandem QRME community layer (`/providers`, `/handoffs`): the AI
specialist's session summary is packaged **only with explicit consent**,
sealed in the PDI vault, released to the provider via a revocable token, and
purged on revocation. See QRME `docs/design/lifecycle-and-consent.md` and the
tandem doc.

## Physical-embodiment session continuity **[implemented]**

`POST /sessions/{user_id}` starts a per-device login; the remembered
interaction state is **per user**, so any device (wearable, stationary
console, phone, robot) that starts a session resumes the same conversational
thread, and guidance routes to the active session's device. See the README
API table and `guardian.start_session`.

## DELETE /data/{user_id} propagation **[implemented]**

Full erasure removes every local table for the user (events, sources,
check-ins, goals, habits, journal, feedback, sessions, devices, insights,
coach messages, tandem links) **and** purges the user's records from the PDI
vault via the tracked `vault_keys`. Cross-system propagation to QRME is
covered in the tandem doc.
