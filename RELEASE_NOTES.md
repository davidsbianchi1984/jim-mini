# JIM-mini v0.4.7 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.4.7` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.4.7** — the round where an upgrade actually replaced the old
app. One of three interoperating products, all three cut together at this
version.

### The upgrade that never took

Three releases in a row fixed signup, and a real install kept meeting the
*first* version's screen anyway. The cause was not in signup at all: the
desktop shell adopted whatever backend answered its port, and on Windows
quitting the app killed the frozen backend's launcher while leaving the
real process alive. So a zombie from an early install kept port 8000 across
every upgrade, and each new console dutifully talked to it.

Three changes make that impossible:

- **`/health` reports the backend's version**, so the shell can tell its
  own backend from a stranger's.
- **The shell adopts a running backend only when that version matches its
  own** — otherwise it takes a free port, starts its own there, and tells
  the window that exact address (a stored loopback address never overrides
  it).
- **Quitting kills the backend's whole process tree** (`taskkill /T` on
  Windows), so nothing survives to squat the port.

The release gate now also asserts the frozen backend reports the version
being packaged, and the fix was verified against a simulated impostor: an
old backend answering 8000, the shell refusing it, starting its own on a
free port, and signup going straight through.

### Verification

558 tests green.

### Install

Download the installer for your OS from the assets below and double-click.
If an older version is still running, close it (or just install over it) —
this build no longer trusts it.

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
