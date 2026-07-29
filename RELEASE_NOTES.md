# JIM-mini v0.9.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.9.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.9.0** — the medicine cabinet. One of three interoperating
products, all three cut together at this version.

### What you take, in your words

A new **Medications** screen. Add what you take exactly as you'd say it —
*"the little white one, 10 mg"* is a valid name and dose — with a
schedule (8:00 and 20:00) or as-needed, what it's for, and whether
missing it is worth a check-in.

### A board with humane grace

The day's board knows **done, due, later, and missed** — and it is
generous on purpose: 9:07 is not "missed" for the 8:00 pill, because a
board that scolds seven minutes teaches you to ignore it. One tap takes
or skips; one slot has exactly one answer and it's correctable — skipped
becomes taken when you find the pill in your pocket. Adherence bars cover
whole past days only, so an afternoon dose is never counted against you
at noon.

### The lines it will not cross

- An as-needed ceiling **refuses to log past itself** — it won't record
  the fourth ibuprofen of a three-max day; it points at your prescriber
  instead. Recording the overage would be complicity.
- A missed dose — even one marked critical — is a **question, never an
  alarm**: an amber note on the board and a gentle line in the coach's
  awareness ("worth asking about, never scolding"). There is no path from
  this feature into the escalation ladder.
- **JIM is not a pharmacist.** There is no interaction checker, because a
  toy one would be trusted; the board says on its face that interactions
  are your pharmacist's call.

### And it keeps watch

Every dose you log is a sign of life the vigil counts — for someone whose
only daily interaction is their pillbox, taking their medication quietly
keeps the steward unalarmed.

### Verification

630 tests green, including that the ceiling refuses rather than records,
that a skipped dose can become taken, that a missed critical dose writes
no escalation event, that adherence never counts the unfinished day, and
that logging a dose stands a tripped vigil down.

### Install

If you have 0.7.0 or later, this arrives on its own — one restart when
prompted. Otherwise, download the installer for your OS from the assets
below.

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
