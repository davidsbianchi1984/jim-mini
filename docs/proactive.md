# How JIM-mini is proactive

JIM does not wait to be asked. This page names every path where the
Guardian notices something and moves first — what senses it, what
interprets it, and what it is allowed to do about it. Each row is real
code with its own tests; nothing here is aspiration.

## The shape: senses → interpreters → actions

**Senses** — where readings enter without a question attached:

| Sense | Door | What arrives |
|---|---|---|
| Biometric monitor | `POST /monitor/{id}` | wearable samples: heart rate, SpO₂, respiration, temperature, HRV, movement, rhythm, environment (smoke/CO), posture — and the device's own `signal_quality` confession |
| Check-ins | `POST /checkin/{id}` | mood, energy, stress, and a note that always passes through the crisis pipeline |
| Ambient activity | `POST /observe/{id}` | consented context events: transactions, sleep, retries at a task, idle time |
| Watch drip | the Apple Watch bridge | passive samples on a schedule |
| Crash watch | `jim/crashwatch.py` | the *absence* of an answer — an unanswered check-in is itself a signal |
| Money observations | `POST /money/{id}/observe` | balance readings against registered accounts |

**Interpreters** — what turns a reading into a meaning:

* `jim/signal.py` grades every sample first: confidence, corroboration,
  the crisis floor for words, and "a fault is reported as a fault." A
  distrusted reading caps how far the ladder may climb.
* `jim/conditions.py` answers *is this an episode* against rules that hold
  for anybody — deliberately conservative, because the top of its ladder
  is a phone call to somebody's daughter.
* `jim/bands.py` answers the other question: *am I drifting from my own
  normal*, both directions, only after a real baseline exists.
* `jim/earlywarning.py` fits the trend and projects minutes-to-threshold
  with a confidence — the nudge *before* the threshold.
* `jim/life.py` turns context into budget insights, spending forecasts,
  and sleep-debt projections.
* `jim/money.py` computes the cushion, the savings progress, and what the
  mandate permits.

**Actions** — what the Guardian may do uninvited, in escalation order:

1. **Insights** (`GET /insights/{id}`) — suggestions and alerts on the
   Home feed: budget at 80%, a spending forecast, a drift question.
2. **Check-in questions** — a band crossing or a money warning becomes a
   question, never an alarm (`severity="checkin"`).
3. **Coach nudges with doors** — the coach offers the matching QRME
   specialist (`specialist_offer`) in the same reply; the explicit
   handoff (`POST /coach/{id}/specialist`) is always the user's press.
4. **Proposed orders** — under a written, revocable, Pro-gated money
   mandate, spare cash above the cushion becomes a *logged proposal*.
5. **The escalation ladder** (`jim/escalation.py`) — for detections only:
   guidance, then contact, gated by signal confidence, with the crisis
   floor for the user's own words. Money and drift never enter it.
6. **Crash summon** — opt-in: an unanswered check-in after an alarming
   reading can summon help.
7. **Care-team coordination** — stacked concerns go to the user's own
   QRME organization as one goal, at most once a day, on the calm path.

## The three lines that keep "proactive" from meaning "creepy"

* **Consent gates every sense.** Sources are opted into per kind
  (`jim/sources`), contribution is previewed and revocable, and the vault
  holds anything private — account numbers included — or the feature
  refuses.
* **Severity is earned, not assumed.** A distrusted sensor cannot ring a
  phone; a low balance cannot either. Only `conditions.detect` and the
  user's own words reach the escalation ladder.
* **Every warning carries its doors.** A nudge that names a problem names
  where help is: the coach, the tandem specialist, a desk with a real
  person behind it — near the user's locality or across the map.
