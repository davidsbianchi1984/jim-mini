# Changelog

All notable changes to JIM-mini are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **First-run onboarding screens** — provider login (Continue with Apple /
  Google / email), permissions, "about you" (name, known conditions, focus),
  emergency contacts, and an "all set" confirmation — completing the Welcome →
  protected-profile journey, rendered in both iOS and Android chrome.

## [0.1.0] — 2026-07-21

First public release. JIM-mini (Guardian) is the personal-guidance product of
the three-product suite (with
[qrme](https://github.com/davidsbianchi1984/qrme) and
[pdi](https://github.com/davidsbianchi1984/pdi)).

### Added

- **Monitor → predict → guide → escalate** — ingest biometric & contextual
  signals (`/monitor`, `/context`), build a personal baseline, detect known
  conditions before threshold, deliver guidance, and escalate to an emergency
  contact / live help on critical events (`/emergency`).
- **Tunable sensitivity** — per-user crisis-detection sensitivity
  (`PUT /sensitivity/{user}`) and confidence-scored handling of noisy signals.
- **Life layer** — consented data sources, mood/energy check-ins, smart goals,
  habit streaks (`/habits/{user}/{habit}/log`), proactive insights, journaling,
  and a 24/7 coach across six life areas.
- **Medical ID** — shareable, QR-linked medical identity for responders.
- **Provider handoff** — consent-gated, revocable packaging of context to a
  care provider.
- **Tandem with QRME** — delegates specialist guidance to QRME profiles over
  HTTP, with a standalone fallback so the user is never left without help.
- **PDI vault** — seals medical and context payloads in the encrypted vault;
  `GET /access-log/{user}` shows the user every access to their own records.
- **Data ownership** — `DELETE /data/{user}` erases every local table and
  purges the user's vault records; the user token dies with the data. Per-user
  bearer tokens stored only as SHA-256 hashes.
- **Apps** — a runnable React + Vite + Electron guardian console and mobile
  screen designs; CI that smoke-builds the console and a per-OS installer
  release workflow.

[Unreleased]: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.1.0...HEAD
[0.1.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.1.0
