# JIM-mini v0.1.7 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.1.7` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.1.7** — the first release cut under the new rule that the three
products ship as one. One of three interoperating products (with
[qrme](https://github.com/davidsbianchi1984/qrme) and
[pdi](https://github.com/davidsbianchi1984/pdi)), all three at this
version.

### What changed in JIM-mini

**Documentation only. No API, no schema, no behaviour change.**

[docs/releasing.md](docs/releasing.md) now records how the three products are
released, so the next round does not have to rediscover it:

- **They are versioned as one release** — same number, same pass, even when a
  repository has nothing of its own to ship that round.
- **A repository with nothing to ship still cuts, and says so** in those words.
  A note that inflates an empty round teaches people to skim the ones that are
  not empty.
- **Tag the release-prep commit, not the tip of `main`.** Work keeps landing
  while a release is cut, and anything arriving after the changelog is
  sectioned belongs under `[Unreleased]` rather than to the version being
  tagged.

That last rule is written down because it already nearly bit: QRME's v0.1.6 tag
point sits behind its `main`, and tagging the tip would have published features
under notes that do not mention them.

Through v0.1.5 each repository cut whenever it happened to have work, so the
numbers matched only by coincidence — which is how QRME reached 0.1.6 alone
while this one sat at 0.1.5. v0.1.6 aligned them by hand; this is the first
round where the alignment is the process rather than a correction.

**If you are already running 0.1.6, this upgrade is optional.** Take it to keep
the three products reporting matching versions; skip it and you lose nothing.

### What is in the suite at 0.1.7

The substance this round is QRME's: live desks left behind as printed codes, a
full audience layer (like, comment, share, subscribe), and a marketplace that
can finally take payments. See
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
