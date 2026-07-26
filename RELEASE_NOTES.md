# JIM-mini v0.4.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.4.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.4.0** — **no functional change to JIM-mini in this release**: no
new routes, no schema, no behaviour. A documentation round. One of three
interoperating products (with [qrme](https://github.com/davidsbianchi1984/qrme)
and [pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at
this version.

### Changed

**The README names its release, and says what each one added.** It opened on a
video and a patent notice and never stated a version, so a reader could not tell
which release they were looking at or what had happened across thirteen of them.
The changelog had it all; the changelog is not where somebody lands. There is now
a release table, newest first.

The same section went into all three repositories, which is the point — the three
are cut as one release, so a reader arriving at any of them should be able to
answer that question the same way.

### Fixed

**Screens 61–64 existed in the repository and nowhere a reader would find them.**
They shipped in 0.3.0 as files — *What Would Be Shared*, *Specialist Working*,
*Find a Clinician*, *Sign to Release* — and were never added to the README
gallery. The four screens illustrating that round's headline feature were
invisible on the page describing it.

### What changed in the siblings

- **QRME** — the starter profiles stopped answering from tone alone. All 34
  shipped with zero source material while the packs matching them sat unused in
  the marketplace; seeding now grounds each one in its own industry pack, as part
  of the repair path so existing deployments catch up by re-running.
- **PDI** — no functional change either, and it records a known gap in its own
  changelog rather than leaving it silent.

### Verification

380 tests green — **the same 380, passing the same way**, which is the point of a
release claiming no functional change. 103 routes, also unchanged. Version
strings moved in exactly five places: `pyproject.toml`, the FastAPI app,
`app/package.json`, and the two root entries in its lockfile (dependency versions
untouched).

### Install

Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
`python -m jim` from source and pick your device — see the [README](README.md). Installers are signed
only if signing secrets are configured; otherwise they are unsigned (see
[docs/releasing.md](docs/releasing.md)).

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
