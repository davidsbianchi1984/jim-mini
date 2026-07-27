# JIM-mini v0.3.2 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.3.2` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.3.2** — **no functional change to JIM-mini in this release**: no new
routes, no schema, no behaviour. The version moves because the three products
are cut as one release, and a number naming one combination of three is only
useful if it never skips one. One of three interoperating products (with
[qrme](https://github.com/davidsbianchi1984/qrme) and [pdi](https://github.com/davidsbianchi1984/pdi)).

### What changed in the siblings

**QRME's starter collection stopped looking like a directory.** Each of the 34
profiles is now shown as the card the app actually gives it — the avatar bubble,
the role, the rating people left, skill chips, Memory / Relationships /
Engagement, a career, a review, and a Talk-to button — two columns wide, so a
phone stops slicing the fourth column mid-word.

And the one starter that had no source material at all now has a Field Pack of
its own. The age wall on that profile governs who may talk to her; it had been
quietly read as a reason for her to know less about her own subject.

### Verification

380 tests green — **the same 380, passing the same way**, which is the
point of a release claiming no functional change. 103 routes, also
unchanged. Version strings moved in exactly five places: `pyproject.toml`, the
FastAPI app, `app/package.json`, and the two root entries in its lockfile
(dependency versions untouched).

### Install

Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
`python -m jim` from source and pick your device — see the [README](README.md). Installers are signed
only if signing secrets are configured; otherwise they are unsigned (see
[docs/releasing.md](docs/releasing.md)).

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
