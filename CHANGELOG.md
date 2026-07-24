# Changelog

All notable changes to JIM-mini are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] — 2026-07-24

### Added

- **First-run onboarding screens** — provider login (Apple / Google / email),
  permissions, "about you", emergency contacts, and an "all set" confirmation,
  in iOS and Android chrome.
- **Native iOS / Android / Windows apps at parity** — Care (Monitor, Check-in,
  Coach, Family), Life (goals/habits/journal), Safety (SOS, escalation policy,
  robots, Medical ID card), Connect (sources, social, apps), Vault Custody,
  and the model picker — a 5-item nav with everything reachable.
- **Robots as guardian responders** — catalog binding, escalation directives,
  and **first-aid rated roles**: assist-rated platforms fetch the AED and
  coach the playbook; perform-rated may deliver compressions only after
  on-scene confirmation. **Autonomous resuscitation stays locked behind a
  signed liability waiver** — and can never be signed for a minor.
- **Predictive early warning**, the escalation decision tree, and the
  one-tap Emergency flow (services, location, family, Medical ID, AI first
  aid, all devices).
- **Family** — a parent enrolls and watches over a child's account: recorded
  consent (PDI-sealed when a vault is configured), age-scaled oversight that
  ends at 18, pause/quiet-hours that never hold safety, and the parent's
  wrist face — one light per child.
- **Provable custody** — tandem specialist exchanges sealed in the PDI vault,
  a custody viewer with provenance, and the native custody screen; the
  mental-health trio routes through live QRME personas with crisis
  escalation guaranteed local.
- **Language & provenance** — per-user language with hand-translated safety
  content in all supported languages, gateway language choice,
  translate-anything, and verifiable guidance provenance with published
  sources; **LLM provider choice** per user.
- **Starter specialists** — a named domain expert per condition, seeded on
  deploy, wired to QRME starter profiles in tandem.
- In-app **"Help us improve" feedback** (`POST`/`GET /improve`) and **chrome
  localization** — the apps' own tab/nav labels in all 10 languages — plus
  pull-to-refresh across the main screens.

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
