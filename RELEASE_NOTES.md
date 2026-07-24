# JIM-mini v0.1.4 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.1.4` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini (Guardian) v0.1.4** — run it your way: one command prints
every way to run the Guardian and you pick the device — your phone (scan
a QR straight off the terminal), this PC, a packaged installer, or the
headless API. One of three interoperating products (with
[qrme](https://github.com/davidsbianchi1984/qrme) and
[pdi](https://github.com/davidsbianchi1984/pdi)).

### Highlights

- **`python -m jim` — the launcher menu** — every way to run the Guardian,
  one command each, so you choose per device: `phone` (the QR flow
  below), `desktop` (the Electron app on this PC), the packaged installer
  (no toolchain needed), or `serve` (the headless API alone). Same
  backend, same data, same token checks behind every door.
- **`python -m jim phone` — the whole phone setup in one command** —
  builds the console if it's missing (first-run `npm install` included),
  prints the pairing URL **with a QR code drawn straight into the
  terminal**, and serves on your local network. Scan, Add to Home
  Screen, done.
- **The Guardian on your phone** — the API serves the built console at `/app`
  (one origin for UI and API — nothing to configure on the phone);
  `GET /pair` returns the URL on your local network with a scannable QR,
  and the Guardian installs to the home screen as a standalone app with a
  thumb-reachable bottom tab bar. Local network only, by design; the
  service worker never caches API traffic, so monitoring and guidance are
  always live.
- **Terms of Service** — docs/terms.md (v1.0) leads with the section that
  matters most: JIM is a wellness tool, **not a medical device** — call
  911 first, 988 in crisis, and detection can be wrong in both
  directions. Assumption of risk and release, the robot-resuscitation
  boundary (fully autonomous resuscitation still requires the separate
  signed waiver, never for a minor, and a robot never delivers the
  shock), parent/guardian enrollment, warranty disclaimer, and liability
  cap. Served versioned at `GET /terms`; enrollment records the accepted
  version + timestamp on the account, and the native welcome screens
  carry the clickwrap notice.
- **Signed, notarized builds wired** — hardened runtime + entitlements +
  notarization in the electron-builder config: adding the Apple/Windows
  signing secrets produces Gatekeeper-clean, SmartScreen-friendly
  installers. docs/releasing.md walks through obtaining the certificates.
- **HIPAA posture** — docs/hipaa-baa.md now points at the signable BAA
  template maintained in the PDI repo, where the vault enforces it in
  code before any HIPAA-program work.

### Verification

228 tests green; live-server smoke flows pass; the desktop app builds
clean; the cross-product suite smoke (run from qrme) passes end to end.

### Install

Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
`python -m jim` from source and pick your device — see the [README](README.md). Installers are signed
only if signing secrets are configured; otherwise they are unsigned (see
[docs/releasing.md](docs/releasing.md)).

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
