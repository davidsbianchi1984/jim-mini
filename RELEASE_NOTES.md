# JIM-mini v0.1.6 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.1.6` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini (Guardian) v0.1.6** — a version-alignment release. QRME, JIM-mini
and PDI are built to run in tandem, and from here they carry the same version
number, so *the suite at 0.1.6* names one combination of three products rather
than three that happen to be nearby. One of three interoperating products
(with [qrme](https://github.com/davidsbianchi1984/qrme) and
[pdi](https://github.com/davidsbianchi1984/pdi)).

### What changed in JIM-mini

Nothing functional. That is the honest headline, and it is short on purpose.

Everything the Guardian does at 0.1.6 it did at 0.1.5 — no API, no schema, no
app behaviour moved. The work that earned the suite its 0.1.6 is QRME's: AI
marks burned into portrait pixels so they survive a screenshot, live desks for
real people behind a counter, and WebAuthn signing on Windows. None of it
reaches across into this repository, and nothing in it asked the Guardian to
change.

**If you are already running 0.1.5, this upgrade is optional.** Take it if you
want the three products to report matching versions; skip it and you lose
nothing.

### Still true from v0.1.5

The substance of the last release is what you are actually running:

- **The native apps are compiled in CI** — iOS via XcodeGen + `xcodebuild`,
  Android via `gradle assembleDebug`, Windows via MSBuild, on every change
  that touches `native/`, with diagnostics re-surfaced on failure.
- **Deployable as one container** — a two-stage `Dockerfile` builds the
  console and installs the API into one image, non-root, database on a `/data`
  volume, health at `/health`.
- **Published deployments** — `JIM_PUBLIC_URL` makes `GET /pair` advertise the
  deployment's public address, and `JIM_SIGNUP_KEY` keeps a published instance
  the operator's rather than open registration.
- **[docs/hosting.md](docs/hosting.md)** — the two postures, why TLS is not
  optional here, the HIPAA/BAA question, and plainly what the deployment does
  **not** give you: no multi-tenancy, no rate limiting, no backups, no uptime
  guarantee.

### Verification

240 tests green — the same 240, passing the same way, which is rather the
point of a release that claims to change nothing. Version strings moved in
exactly five places: `pyproject.toml`, the FastAPI app, `app/package.json`,
and the two root entries in its lockfile (dependency versions untouched).

### Install

Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
`python -m jim` from source and pick your device — see the [README](README.md). Installers are signed
only if signing secrets are configured; otherwise they are unsigned (see
[docs/releasing.md](docs/releasing.md)).

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
