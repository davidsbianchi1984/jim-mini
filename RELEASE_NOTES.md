# JIM-mini v0.1.5 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.1.5` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini (Guardian) v0.1.5** — the release where the native apps stop
being source code and start being builds. Every phone and desktop app in
this repository now goes through a real compiler on every change, and the
whole Guardian ships as one container you can host. One of three
interoperating products (with
[qrme](https://github.com/davidsbianchi1984/qrme) and
[pdi](https://github.com/davidsbianchi1984/pdi)).

### Highlights

- **The native apps are compiled in CI.** Until this release the Swift,
  Kotlin and C# in `native/` had never been through a compiler here — they
  were checked by reading, and by brace/XML well-formedness, which catches a
  typo and nothing else. iOS builds via XcodeGen + `xcodebuild`, Android via
  `gradle assembleDebug`, Windows via Visual Studio's MSBuild. The gate found
  real defects the moment it ran.
- **Two of them the compiler caught, not a reviewer.**
  - The **iOS project spec was invalid** — its XcodeGen `info:` block had no
    `path`, so `xcodegen generate` failed outright and the Xcode project could
    never have been produced at all. Fixing it also restores the
    local-networking exemption the Simulator needs to reach the API.
  - **Windows would not compile the journal list** — `entries` is an array, an
    array converts implicitly to `Span<T>`, and so `.Reverse()` bound to the
    in-place **void** overload instead of LINQ's, leaving the following
    `.Select` attached to nothing.
- **Failures are readable now.** Gradle prints Kotlin diagnostics well above
  its `FAILURE` block and MSBuild scrolls errors past the per-project noise,
  so a red run used to report an exit code and nothing else. Both steps now
  re-surface the actual diagnostics in a collapsed group on failure.
- **Deployable as one container** — a two-stage `Dockerfile` builds the
  console and installs the API into a single image, so a hosted instance
  serves UI and API from one origin exactly as the phone flow does. Non-root
  user, database on a `/data` volume, honours `$PORT`, health at `/health`.
- **Published deployments** — `JIM_PUBLIC_URL` makes `GET /pair` advertise the
  deployment's public address (QR included) instead of a LAN address, so the
  phone flow works hosted or local from one code path. `JIM_SIGNUP_KEY` gates
  enrollment behind a header so a published instance stays the operator's
  rather than open registration — and it never blocks an enrolled user, or a
  parent adding a child under their own token.
- **[docs/hosting.md](docs/hosting.md) — the operator's side, stated plainly.**
  The two postures, why TLS is not optional here (tokens ride in headers, and
  browsers refuse geolocation without it, so escalation needs it), what
  holding someone else's health data commits you to including the HIPAA/BAA
  question, and what the deployment does **not** give you: no multi-tenancy,
  no rate limiting, no backups, no uptime guarantee.

### Verification

240 tests green. The console builds clean. The native compile gate is green
on all three platforms — which for this release is the headline rather than a
footnote: it is the first time that has ever been true here.

### Install

Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
`python -m jim` from source and pick your device — see the [README](README.md). Installers are signed
only if signing secrets are configured; otherwise they are unsigned (see
[docs/releasing.md](docs/releasing.md)).

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
