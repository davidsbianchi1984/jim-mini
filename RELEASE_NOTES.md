# JIM-mini v0.8.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.8.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.8.0** — the round where the Guardian learned to notice
absence. One of three interoperating products, all three cut together at
this version.

### The vigil

Every other alarm in this product fires on a reading — a heart rate that
climbed, an oxygen number that fell. The vigil fires on the **absence** of
readings: the watch that went quiet, the check-in that never came, the
person living alone whom no threshold can see because nothing is arriving
to measure.

In **Settings → The vigil** you name a steward, choose a quiet period, and
write — now, while you are fine — the words they will read. If nothing is
heard from you for longer than that period, they are asked to check on
you, in your words, with the honest framing that no reading triggered
this: it is the absence of readings.

Three deliberate limits: it never rings past the steward (silence is weak
evidence — the right response is a person who cares knocking on a door,
not an ambulance); it trips at most once per silence; and any sign of life
stands it down automatically, because showing up *is* the all-clear.

### One absence, three products

The vigil's event id is an attestation reference the siblings accept:
QRME's reviewer-gated ownership succession (a profile passes to its named
successor, or sunsets to a frozen memorial) and PDI's new **bequests**
(named scopes of the vault unlock to a named person — see PDI's notes).
Continuity, end to end.

### Verification

619 tests green, including that the vigil's own trip never counts as a
sign of life, that a brand-new user who was never heard from cannot trip
it, that it trips exactly once, that no escalation event is ever written,
and that the steward's message says plainly it is not an emergency.

### Install

If you have 0.7.0, this arrives on its own — one restart when prompted.
Otherwise, download the installer for your OS from the assets below.

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
