# JIM-mini v0.2.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.2.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.2.0** — the minor bump, and honestly: **there are no functional
changes to JIM-mini in this release.** The three products version as one, and
this round's work was next door. One of three interoperating products (with
[qrme](https://github.com/davidsbianchi1984/qrme) and
[pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at
this version.

### Why 0.2.0 rather than 0.1.10

The 0.1.x line ran from a Guardian that monitored and escalated, to one with a
life layer, an escalation ceiling a stranger's tap cannot raise, care beacons
on the objects around a watched person, a workplace relay for lone workers, a
rota that knows who is actually on at 2am, and an escalation that reaches a
human rather than writing a name in a table. That is a different product from
0.1.0, and 0.1.10 would have undersold it.

### What changed here

- **Only one workflow writes the release body now.** `desktop-release.yml`
  published `RELEASE_NOTES.md` **verbatim** — *"Ready-to-paste body for the
  GitHub Release…"* preamble and all — while `sync-release-notes.yml` published
  the same file with that preamble stripped. Both fired on the same tag push;
  the sync finished in six seconds and the installer build finished two to four
  minutes later and overwrote it. The build always won, so every release since
  the sync workflow existed shipped the preamble until somebody re-ran the sync
  by hand. The build no longer sets a body at all, and the sync now waits for
  it rather than racing it.

### What changed in the siblings

- **PDI** — a per-tenant on-call roster, closing the gap this repo's own
  `jim/rota.py` had left visible next door. `PDI_GATE_ONCALL` was one name for
  the whole deployment, which in a multi-tenant vault routed every customer's
  courier to the same person.
- **QRME** — nothing of its own this round.

### Verification

297 tests green — the same 297, passing the same way, which is the point of a
release that claims no functional change here. 87 routes. Version strings moved
in exactly five places: `pyproject.toml`, the FastAPI app, `app/package.json`,
and the two root entries in its lockfile (dependency versions untouched).

### Install

Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
`python -m jim` from source and pick your device — see the [README](README.md). Installers are signed
only if signing secrets are configured; otherwise they are unsigned (see
[docs/releasing.md](docs/releasing.md)).

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
