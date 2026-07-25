# Changelog

All notable changes to JIM-mini are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Care beacons and the workplace relay are built** — `jim/beacons.py`,
  `jim/relay.py`, 13 routes, 25 tests. A printed QR goes on the things around a
  watched person — a fridge door, a wristband, a walker — and a stranger who
  finds it can raise whoever is watching.

  **The alarm comes before the disclosure.** Stage one is a first name, one
  sentence and a button; raising the alarm is the act that turns a passer-by
  into a responder, and that is what earns them the Medical ID. The order is
  QRME's desk beacon in reverse, because health is not a shop sign — and the
  gate is affordable precisely because the ungated path already ships on the
  person's own body, which is what `/medical-id/{token}` is for.

  **A beacon reports watch status, never subject status.** No health state, no
  location, ever: *is this person OK right now* is precisely the question a
  stalker is asking. Tested by serializing the whole card and searching it for
  the birthdate, the contact number, the label and the placement note, rather
  than by checking the handful of fields somebody remembered to omit.

  **`notify_contact` is now a ceiling as well as a floor.** `escalation.decide`
  gained a `ceiling` argument — the first rule in that module that *lowers* a
  tier, and it only ever applies to a caller who is not the user. A `critical`
  severity bases at `emergency_services`, so the ceiling is what stands between
  an anonymous tap and a dispatch; when it clips a floor it says so
  (`clipped_by_ceiling`, `call_emergency_services_yourself`) rather than quietly
  returning something lower. Existing callers pass no ceiling and are unchanged,
  which a regression test pins across every severity and sensitivity.

  **The cooldown coalesces rather than drops** — a second finder's words join
  the open alarm, because two people finding the same casualty is the case the
  feature exists for. And **a minor's beacon never opens the clinical stage**,
  to anyone; it is guardian-issued and routes to the guardian.

  For **lone and remote workers**, a site relay: it works the roster in order,
  distinguishes *accepted* (somebody is coming) from *cleared* (it is over),
  refuses an anonymous acceptance, and reports an exhausted roster rather than
  going quiet — still without dispatching. Incidents are built from the alarm,
  not the person, so the payload carries no name, condition or history.

  Two screens (59 Care Beacons, 60 Workplace Relay).

### Fixed

- **Nine screens had text running outside their cards**, found while checking
  the two new ones by rendering them rather than trusting the SVG to parse.
  Four subtitles overflowed the card edge and five titles collided with their
  own pill — worst on *Parent Setup*, where "cautious sensitivity · parent is
  the emergency contact" ran well past the phone frame. Also `icon="lock"`,
  used on that screen, is not in this repo's icon set at all and had been
  rendering as a bare dot; it is now `clip`, and a check confirms every icon
  named by a screen exists.

## [0.1.8] — 2026-07-25

### Fixed

- **`[0.1.5]` and `[0.1.6]` linked to releases that do not exist.** Both
  versions were cut — changelog, notes, version bumps — but their `app-v*` tags
  were never pushed, so those two entries pointed at 404s. They now point at
  their release-prep commits. Deliberately **not** fixed by backfilling the
  tags: pushing them now would fire the installer build and publish v0.1.5 and
  v0.1.6 releases *dated after* v0.1.7, putting superseded installers at the top
  of the page people download from. [docs/releasing.md](docs/releasing.md)
  records that reasoning.

### Changed

- **There are no functional changes to JIM-mini in this release.** No API, no
  schema, no behaviour moved. The substance at 0.1.8 is QRME's: a live
  desk stops being only something you watch — you can ask to come up on the
  stream, and the room's reactions render on the picture rather than beside it.
  Nothing in it asked JIM-mini to change.

## [0.1.7] — 2026-07-25

### Changed

- **The three products are now cut as one release** — documented in
  [docs/releasing.md](docs/releasing.md), and in QRME's and PDI's copies of the
  same file. Same number, same pass, even when a repository has nothing of its own
  to ship that round; an empty round says so in those words rather than being
  padded. Through v0.1.5 each repository cut whenever it happened to have work,
  so the numbers matched only by coincidence — which is how QRME reached 0.1.6
  alone while this one sat at 0.1.5. The doc also writes down the trap that
  follows: tag the release-prep commit rather than the tip of `main`, because
  work keeps landing while a release is cut and anything arriving after the
  changelog is sectioned belongs to `[Unreleased]`, not to the version being
  tagged.

## [0.1.6] — 2026-07-25

### Changed

- **Version aligned across the suite.** QRME, JIM-mini and PDI are built to run
  in tandem, but their version numbers drifted apart whenever a round of work
  landed in one repository and not the others — QRME reached 0.1.6 on its own
  while this one stayed at 0.1.5. From here the three carry the same number, so
  "the suite at 0.1.6" names one combination of three products rather than
  three that merely happen to be nearby. Anyone pinning all three can pin one
  number.

  **There are no functional changes to JIM-mini in this release.** Everything
  the Guardian does at 0.1.6 it did at 0.1.5: no API, schema, or app behaviour
  moved. The work that earned 0.1.6 is QRME's — AI marks burned into portrait
  pixels, live desks, and WebAuthn signing on Windows — and none of it reaches
  across into this repository. The number is the only thing that changed here,
  and saying so plainly is worth more than padding the entry.

## [0.1.5] — 2026-07-25

### Added

- **The native apps are compiled in CI** (`.github/workflows/native.yml`) —
  iOS via XcodeGen + `xcodebuild` on macOS, Android via `gradle assembleDebug`,
  Windows via MSBuild. The Swift, Kotlin and C# had never been through a
  compiler in this repository: they were checked by reading and by brace/XML
  well-formedness, which catches a typo and nothing else. Ported from QRME,
  where the same gate found five real defects. Compile only — signing and
  packaging stay in the release workflow — and it runs only when `native/`
  changes, since macOS runner minutes are not free.
- **Published deployments** — `JIM_PUBLIC_URL` makes `GET /pair` advertise
  the deployment's public address (QR included) instead of a LAN address, so
  the phone flow works hosted or local from one code path. `JIM_SIGNUP_KEY`
  gates enrollment behind an `x-signup-key` header so a published instance
  stays the operator's rather than open registration; unset leaves LAN use
  exactly as it was, and the gate never blocks an enrolled user or a parent
  adding a child under their own token.
- **Deployable as one container** — a two-stage `Dockerfile` builds the console
  and installs the API into a single image, so a hosted instance serves UI and
  API from one origin exactly as the phone flow does. Runs as a non-root user,
  keeps the database on a `/data` volume, honours `$PORT`, and reports health
  at `/health`. [docs/hosting.md](docs/hosting.md) covers the operator side:
  the two postures (local vs published), why TLS isn't optional here (tokens
  in headers, and browsers refuse geolocation without it — so escalation needs
  it), what holding someone else's health data commits you to including the
  HIPAA/BAA question, and plainly what the deployment does *not* give you (no
  multi-tenancy, rate limiting, backups, or uptime guarantee).

### Fixed

- **The iOS project spec was invalid** — its XcodeGen `info:` block had no
  `path` (required), while also setting `GENERATE_INFOPLIST_FILE`, which is
  mutually exclusive with it. `xcodegen generate` failed outright, so the
  Xcode project could never have been produced. The plist is now written from
  the spec, which also means the local-networking exemption the Simulator
  needs to reach `http://127.0.0.1:8000` actually applies.
- **Windows: the journal list would not compile.** `entries` is a
  `JournalItem[]`, and an array converts implicitly to `Span<T>`, so
  `.Reverse()` bound to `MemoryExtensions`' in-place **void** overload rather
  than LINQ's — leaving the following `.Select` attached to nothing.

## [0.1.4] — 2026-07-24

### Added

- **`python -m jim` launcher** — bare invocation prints the menu of every
  way to run the Guardian, one command each, so users choose their device:
  `phone` (builds the console if missing — npm install included on first
  run — prints the pairing URL with a scannable QR drawn straight into
  the terminal, serves on the local network; flags `--port`, `--rebuild`,
  `--no-build`, `--print-only`), `desktop` (the Electron app on this PC,
  or a pointer to the packaged installers when npm is absent), and
  `serve` (the headless API alone, `--host`/`--port`). Same backend,
  data, and token checks in every form.

## [0.1.3] — 2026-07-24

### Added

- **Run it on your phone** — the API serves the built console at `/app`, so a
  phone on the same Wi-Fi opens the Guardian with nothing to configure (one
  origin for UI and API, so no CORS and no "which host?" step). `GET /pair`
  resolves this machine's local-network address and returns the URL to open —
  with `GET /pair/qr.svg` as a scannable QR and a pairing card in the Privacy
  screen. Installable as a PWA (manifest, icon, standalone display, app-shell
  service worker that never caches API traffic), with a phone layout: the
  sidebar becomes a bottom tab bar, 16px inputs so iOS doesn't zoom, and
  safe-area insets for the notch and home indicator.

## [0.1.2] — 2026-07-24

### Added

- **Terms of Service** — docs/terms.md (v1.0: not a medical device, call
  911 first, assumption of risk and release, robot-resuscitation boundary,
  warranty disclaimer, liability cap) served versioned at `GET /terms`;
  enrollment records the accepted version and timestamp on the account,
  and the native welcome screens carry the clickwrap notice.
- **macOS notarization wiring** — hardened runtime + entitlements +
  `notarize` in the electron-builder config; docs/releasing.md walks
  through obtaining the macOS and Windows certificates.
- docs/hipaa-baa.md now points at the signable BAA template maintained in
  the PDI repo (docs/baa-template.md there).

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

[Unreleased]: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.1.8...HEAD
[0.1.8]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.1.8
[0.1.7]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.1.7
[0.1.6]: https://github.com/davidsbianchi1984/jim-mini/commit/a930bcf
[0.1.5]: https://github.com/davidsbianchi1984/jim-mini/commit/c80c227
[0.1.4]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.1.4
[0.1.3]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.1.3
[0.1.2]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.1.2
[0.1.1]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.1.1
[0.1.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.1.0
