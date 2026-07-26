# JIM-mini v0.2.1 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.2.1` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.2.1** — the release where the Guardian stops treating every
reading as a fact. One of three interoperating products (with
[qrme](https://github.com/davidsbianchi1984/qrme) and
[pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
version.

### Highlights

- **How much to trust a reading** (`jim/signal.py`). `escalation.decide` has
  always accepted a `confidence`, but **only forecasts ever supplied one** — it
  gated *predictions* and never *measurements*, so a reading was a fact by
  virtue of arriving.

  Consumer biometrics are not like that. An optical sensor loses skin contact,
  a chest strap catches a motion artifact, and the characteristic failure is not
  a small error but a plausible-looking number that is completely wrong, with
  the alarming direction as likely as the reassuring one. At the top of this
  ladder is a phone call to somebody's daughter, and an alert that is usually
  wrong spends the only thing escalation has: her willingness to pick up.

- **Confidence drops only on evidence the *sensor* misbehaved** — an impossible
  value, a jump no body could make between two readings, or the device reporting
  its own poor contact. Being clinically abnormal never lowers it.

  That distinction is the whole design, and it was learned the hard way: the
  first draft graded anything outside the ordinary range as suspect, which muted
  a lone SpO2 of 84 — the exact reading the ladder exists to carry. A
  pre-existing test caught it.

- **A poor grade caps rather than silences.** Escalation stops at `check_in`:
  *"we got an odd reading, are you alright?"* is the honest sentence when the
  honest answer is that we do not know, and asking is also how the reading gets
  corroborated. Dropping the sample would be the same mistake pointed the other
  way, because the noisy reading is sometimes real.

- **Words are never noise.** The crisis floor is applied after the cap and is
  never clipped by it. Nor can words make a heart rate of zero true: two
  impossible readings are not two witnesses but one broken device agreeing with
  itself. A fault is phrased as a fault — *check the strap* — because telling
  somebody whose sensor fell off that we are worried about them is how people
  learn to disbelieve the thing.

### Fixed

- **The escalation decision was advisory; raw severity was in charge.**
  `monitor` reached out whenever `severity == "critical"`, so the tree could
  resolve a disbelieved reading to `check_in` and the emergency contact was rung
  anyway. The tree is authoritative now. No behaviour changes for a trusted
  critical — its floor is `notify_contact`, so the comparison is exactly
  equivalent — and a test asserts that directly.

- **A rota typo cannot take the escalation path down.** `RotaError`'s docstring
  said *"raised at load, never at 3am"*, but nothing reads the rota at start-up,
  so it was raised at exactly 3am: one typo turned `POST …/escalate` into a 500.
  It degrades to the flat names now and says so loudly.

### Verification

312 tests green (19 new this release). 87 routes. Mutation-checked: letting the
confidence cap clip the crisis floor, and letting an impossible reading be
corroborated, each fail the test that forbids them.

### Install

Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
`python -m jim` from source and pick your device — see the [README](README.md). Installers are signed
only if signing secrets are configured; otherwise they are unsigned (see
[docs/releasing.md](docs/releasing.md)).

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
