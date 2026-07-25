# JIM-mini v0.1.8 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.1.8` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.1.8** — cut alongside QRME and PDI, as the three always
are now. One of three interoperating products (with
[qrme](https://github.com/davidsbianchi1984/qrme) and
[pdi](https://github.com/davidsbianchi1984/pdi)), all three at this
version.

### What changed in JIM-mini

**Nothing functional.** No API, no schema, no behaviour moved.

The only change here is a repair to the changelog itself: `[0.1.5]` and
`[0.1.6]` linked to release tags that were never pushed, so both were 404s.
They now point at their release-prep commits. Deliberately *not* fixed by
backfilling those tags — pushing them now would fire the installer build and
publish two superseded releases dated *after* v0.1.7, at the top of the page
people download from. [docs/releasing.md](docs/releasing.md) records that
reasoning, because an unexplained gap in a tag sequence is exactly what someone
later "fixes" without knowing why it was left.

**If you are already running 0.1.7, this upgrade is optional.** Take it to keep
the three products reporting matching versions; skip it and you lose nothing.

### What is in the suite at 0.1.8

The substance is QRME's: a live desk stops being only something you watch. You
can ask to come up on the stream — which the host has to grant, and which needs
a verified adult on a rated desk — and the room's comments, likes, shares and
gifts render *on* the picture rather than beside it. See
[QRME's notes](https://github.com/davidsbianchi1984/qrme/releases). Nothing in
it asked JIM-mini to change.

### Verification

240 tests green — the same 240, passing the same way, which is rather the
point of a release that claims to change nothing functional. Version strings
moved in exactly five places: `pyproject.toml`, the FastAPI app,
`app/package.json`, and the two root entries in its lockfile (dependency
versions untouched).

### Install

Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
`python -m jim` from source and pick your device — see the [README](README.md). Installers are signed
only if signing secrets are configured; otherwise they are unsigned (see
[docs/releasing.md](docs/releasing.md)).

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
