# JIM-mini v0.2.2 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.2.2` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.2.2** — a documentation release. **No code changed**: no new
routes, no schema, no behaviour, and nothing about how the Guardian decides
anything. Everything here corrects something that was *described* wrongly. One
of three interoperating products (with
[qrme](https://github.com/davidsbianchi1984/qrme) and
[pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
version.

### Fixed

- **Three releases of changelog links were missing.** `[0.1.9]`, `[0.2.0]` and
  `[0.2.1]` had headings but no link definitions, so three shipped versions
  rendered as literal `[0.2.1]` bracket text rather than linking to their
  releases, and `[Unreleased]` still compared against `app-v0.1.8` —
  presenting a three-release diff as though it were an empty one.

- **The release checklist is why that kept happening**, and is the entry that
  matters. `docs/releasing.md` step 1 said to move the `Unreleased` items under
  the new heading and date it, and stopped — it never mentioned the link
  definition at the bottom of the file. The step was skipped three releases
  running by someone following the instructions correctly, and nothing
  complains when you miss it: the heading renders fine without a definition,
  and the damage appears hundreds of lines from where the edit was made.

  Step 2 was wrong in the same direction. It named `pyproject.toml` and
  `app/package.json` when the version string lives in **five** places — the two
  it omitted being the `FastAPI(...)` call in `jim/api.py` and the second root
  entry in `app/package-lock.json`, both of which had to be rediscovered each
  round. Both steps now say what they meant.

  The `0.1.5` and `0.1.6` entries still point at commits rather than tags.
  That is deliberate and explained in `docs/releasing.md`; they are untouched.

### What changed in the siblings

- **QRME** — `POST /marketplace/seed` still advertised itself as *"Idempotent —
  already-seeded profiles are skipped"* after v0.2.1 taught it to **repair**
  too, so the text in the OpenAPI docs pointed away from the one call that
  fixes a deployment showing bare initials instead of portraits. Corrected in
  four places.

- **PDI** — the same checklist and changelog-link corrections as here.

### Verification

312 tests green — **the same 312, passing the same way**, which is the point of
a release that claims no functional change. 87 routes, also unchanged. Version
strings moved in exactly five places: `pyproject.toml`, the FastAPI app,
`app/package.json`, and the two root entries in its lockfile (dependency
versions untouched). Every version heading in the changelog was checked against
its link definition — 12 for 12.

### Install

Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
`python -m jim` from source and pick your device — see the [README](README.md). Installers are signed
only if signing secrets are configured; otherwise they are unsigned (see
[docs/releasing.md](docs/releasing.md)).

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
