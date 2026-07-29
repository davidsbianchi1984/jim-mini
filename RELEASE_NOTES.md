# JIM-mini v0.7.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.7.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.7.0** — the last version anyone fetches by hand. One of three
interoperating products, all three cut together at this version.

### The app keeps itself current

On launch, the desktop app asks GitHub Releases whether a newer version
exists.

- **Windows and Linux** download it quietly in the background and then
  ask once: *Restart now, or later?* One click and the new version is
  running; your data stays exactly where it was.
- **macOS** cannot swap an unsigned app under itself, so it does the next
  honest thing: tells you a new version exists and opens the download
  page.

Every failure path is silent by design — no network, no release, no
metadata means the app simply opens as normal. An update check must never
stand between you and the app.

Because the updater ships *inside* this version, 0.7.0 is the last one
that has to be downloaded by hand: install it once and every release
after this arrives on its own.

### Verification

609 tests green. Console build clean; all three desktop shells
syntax-checked, and the release workflow already publishes the update
metadata (`latest*.yml` + blockmaps) the updater feeds on.

### Install

Download the installer for your OS from the assets below and
double-click — for the last time.

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
