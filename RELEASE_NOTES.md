# JIM-mini v0.6.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.6.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.6.0** — the round where the Apple Watch found its way in.
One of three interoperating products, all three cut together at this
version.

### Your watch reaches JIM — no App-Store app required

HealthKit only talks to apps installed from the App Store, and JIM does
not have one. But every iPhone ships two free doors out, and **Settings →
Apple Watch** now opens both:

**The drip.** A Shortcuts personal automation — built once, from the
numbered recipe on the setup card — POSTs Health readings to your personal
drip address on a schedule. Every arrival runs the full pipeline:
detection, your drift bands, escalation — exactly as if you had typed the
numbers yourself. The payload is forgiving on purpose: `heart_rate`,
`heartRate`, `"72 count/min"`, oxygen as HealthKit's fraction or a typed
percent — all one reading.

The drip address is deposit-only. Its reply is a count and a noticed flag,
never guidance — a credential that rides in a URL must not be able to read
health information back out. If the address ever leaks, **New address**
retires it in one tap.

**The seed.** The Health app already holds months of what your watch
recorded. Export it (Health → your picture → *Export All Health Data*),
upload the zip, and per-day medians fold into your baselines
chronologically — resting heart rate, HRV, oxygen, respiration,
temperature. **Your baseline is established on day one** instead of five
quiet days of "learning", and the drift bands arm the same afternoon.
History is context, not news: the seed writes no events and raises no
check-ins, and exercise heart-rate readings are excluded by motion context
so a workout never teaches the bands a resting rate that isn't.

### Verification

604 tests green, including that a seeded history raises not a single
event, that the drip reply carries no guidance or identity, that a rotated
address stops working immediately, that a wrong token is a 404 rather than
a confirmation, that exercise readings never reach the resting baseline,
and that a seeded baseline arms the drift bands the same day.

### Install

Download the installer for your OS from the assets below and double-click.

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
