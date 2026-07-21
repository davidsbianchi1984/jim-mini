# JIM-mini v0.1.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.1.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini (Guardian) v0.1.0** — the first public release of the
personal-guidance product, one of three interoperating products (with
[qrme](https://github.com/davidsbianchi1984/qrme) and
[pdi](https://github.com/davidsbianchi1984/pdi)).

Guardian monitors a user's biometric and contextual signals, detects known
conditions before they cross threshold, delivers guidance, and escalates to an
emergency contact or live help on critical events — wrapped in a life layer of
sources, check-ins, goals, habits, insights, and a 24/7 coach.

### Highlights

- **Monitor → predict → guide → escalate** — personal baselines, early
  detection, guidance, and emergency escalation.
- **Tunable sensitivity** — per-user crisis-detection sensitivity and
  confidence-scored handling of noisy signals.
- **Life layer** — consented data sources, mood/energy check-ins, smart goals,
  habit streaks, proactive insights, journaling, and a six-area coach.
- **Medical ID** — shareable, QR-linked medical identity for responders.
- **Provider handoff** — consent-gated, revocable packaging of context to a
  care provider.
- **Tandem with QRME** — delegates specialist guidance to QRME profiles over
  HTTP, with a standalone fallback so the user is never left without help.
- **PHI protection** — data sealed in the PDI vault, every access user-visible
  via the access log, complete erasure that revokes the user token with the
  data. See [docs/hipaa-baa.md](docs/hipaa-baa.md).
- **Apps** — a runnable guardian console; this release attaches per-OS
  installers built and (optionally) signed in CI.

### Install

Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
the backend from source — see the [README](README.md). Installers are signed
only if signing secrets are configured; otherwise they are unsigned (see
[docs/releasing.md](docs/releasing.md)).

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
