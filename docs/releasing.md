# Releasing

JIM-mini ships two artifacts: the Python backend and the guardian console. This
describes cutting a versioned release and how (optional) code-signing works.

## The three products cut together

JIM-mini, [QRME](https://github.com/davidsbianchi1984/qrme) and [PDI](https://github.com/davidsbianchi1984/pdi) are built to run in
tandem, and they are versioned as **one release**: the same number, cut in the
same pass, even when a repository has nothing of its own to ship that round.

This is a deliberate reversal. Through v0.1.5 each repository cut whenever it
happened to have work, so the numbers matched only by coincidence — QRME
reached 0.1.6 alone while the other two sat at 0.1.5, and "the suite" named no
particular combination of anything. Now a version names one combination of
three products, and anyone running all three can pin one number.

Three rules make that hold up:

**A repository with nothing to ship still cuts, and says so.** Its changelog
entry reads *there are no functional changes to JIM-mini in this release*, in those
words, rather than being padded with restated work. A note that inflates an
empty round teaches people to skim the ones that are not empty.

**Tag the release-prep commit, not the tip of `main`.** Work keeps landing
while a release is cut, and anything that arrives after the changelog is
sectioned belongs under `[Unreleased]` — not to the version being tagged.
Tagging the tip publishes features under notes that do not describe them.
Check what `[Unreleased]` holds before choosing the commit.

**Cut all three even when only one has content.** The moment one is skipped the
numbers drift again, and the next round has to decide whether to re-align or
let them diverge — which is the state this rule exists to end.

### v0.1.5 and v0.1.6 have no tags

They were released — changelog, notes, version bumps — but the `app-v*` tags
were never pushed, so no GitHub Release exists for either. Their CHANGELOG
entries link to the release-prep **commit** instead of a tag, which is why
those two lines look different from the rest.

They are deliberately **not** being backfilled. Pushing those tags now would
fire `desktop-release.yml`, build installers on real runners, and publish
v0.1.5 and v0.1.6 Releases dated *after* v0.1.7 — putting superseded
installers at the top of a page people download from. The dead links were the
only real problem, and pointing them at commits fixes that without publishing
anything.

## Cut a release

1. Update [CHANGELOG.md](../CHANGELOG.md) — move `Unreleased` items under the new
   version and date it. Refresh [RELEASE_NOTES.md](../RELEASE_NOTES.md). Do the
   same in the sibling repositories, in the same pass.

   **Add the link definition at the bottom of the file, and repoint
   `[Unreleased]` at the version you are cutting:**

   ```markdown
   [Unreleased]: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.2.1...HEAD
   [0.2.1]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.2.1
   ```

   This is the step that gets missed, because nothing complains. The heading
   renders fine without a definition and the damage shows up hundreds of lines
   away — a released version rendering as literal `[0.2.1]` text, and an
   `[Unreleased]` link quietly diffing against a tag three releases old.
   0.1.9, 0.2.0 and 0.2.1 were all cut without it.

2. Bump the version string in **all five places**: `pyproject.toml`, the
   `FastAPI(...)` call in `jim/api.py`, `app/package.json`, and the **two root
   entries** in `app/package-lock.json` — the top-level `"version"` and the one
   under `packages` → `""`. Leave every other version in the lockfile alone;
   dependency pins look identical and are not yours.
3. Tag and push:

   ```bash
   git tag app-v0.1.0
   git push origin app-v0.1.0
   ```

   **Tag creation is the maintainer's step, and it needs a link.** Claude
   cannot push tags here — the attempt is refused — so the hand-off has to be
   one click rather than a commit SHA to copy and a form to fill in. Every
   time a cut is ready, give a prefilled release link per repository:

   ```
   https://github.com/davidsbianchi1984/jim-mini/releases/new?tag=app-v0.19.0&target=<sha>&title=JIM-mini%20app-v0.19.0
   ```

   `target` takes the full SHA of the release-prep commit — the same one rule
   two above says to tag, not the tip of `main` if anything landed after it.
   The tag is created on publish, and a tag created this way *does* emit the
   `push` event, so both workflows fire exactly as they would from a terminal.

   **The title carries the product name**: `JIM-mini app-v0.19.0`, not
   `app-v0.19.0`. Three repositories cut the same number in the same pass, so
   a release list, a notification and a search result all show three entries
   reading `app-v0.20.1` with nothing to tell them apart. The name is the
   only thing in the title that says which product this is.

   **A draft creates no tag.** Saving the form as a draft stores the release
   and leaves the tag unmade — the draft's URL says `untagged-…` — so neither
   workflow fires, no installers are built, and the notes are not laid over
   the body, because the thing they all listen for is the tag push. That is
   also why *Generate release notes* has nothing to offer on a draft. Publish
   and all of it happens; until then the release exists and the tag does not.

The `app-v*` tag triggers `.github/workflows/desktop-release.yml`, which builds
the console into per-OS installers (`.dmg` / `.exe` / `.AppImage`) on real
macOS / Windows / Linux runners and attaches them to a GitHub Release, with
GitHub's generated changelog as the body.

**Leave the release body empty when you create the tag.** When that workflow
finishes, `sync-release-notes.yml` runs and lays `RELEASE_NOTES.md` over the
top — dropping the maintainer preamble above the `---`, and keeping exactly one
copy of the generated *What's Changed*. Anything typed by hand is replaced.

Only one workflow writes that body, and it is that one. Both used to: the
installer build published `RELEASE_NOTES.md` verbatim, preamble included, two
to four minutes after the sync had already published it correctly. The build
always won, so every release needed re-syncing by hand. The build no longer
sets a body at all, and the sync waits for it rather than racing it.

Tag names are **case-sensitive** to the trigger. `App-v0.1.9` matches
`tags: ["app-v*"]` in neither workflow and silently does nothing.

A manual **Run workflow** on the build workflow uploads the installers as
artifacts *without* publishing a Release — useful for a dry run. To repair an
already-published body, run **sync-release-notes** manually with the tag; it
checks out that tag, so it publishes the notes that shipped with it rather than
whatever `main` says today.

## Code signing (optional)

Signing is driven entirely by repository **secrets** — nothing is committed, and
if the secrets are absent the installers are simply built **unsigned**. Set them
under *Settings → Secrets and variables → Actions*:

| Secret | Platform | Purpose |
| --- | --- | --- |
| `CSC_LINK` | macOS | Base64 of the Apple Developer ID certificate (`.p12`) |
| `CSC_KEY_PASSWORD` | macOS | Password for the `.p12` |
| `WIN_CSC_LINK` | Windows | Base64 of the Windows code-signing certificate (`.pfx`) |
| `WIN_CSC_KEY_PASSWORD` | Windows | Password for the `.pfx` |
| `APPLE_ID` | macOS | Apple ID for notarization |
| `APPLE_APP_SPECIFIC_PASSWORD` | macOS | App-specific password for notarization |
| `APPLE_TEAM_ID` | macOS | Apple Developer Team ID |

electron-builder reads these from the environment during `npm run dist`. macOS
notarization runs only when the `APPLE_*` secrets are present. The app is
built with the hardened runtime and the entitlements in
`app/build/entitlements.mac.plist`, which notarization requires.

### Getting the certificates (one-time)

**macOS**: join the [Apple Developer Program](https://developer.apple.com/programs/)
($99/yr); create a **Developer ID Application** certificate and export it
from Keychain as a `.p12`; `base64 -i cert.p12` → `CSC_LINK`, export
password → `CSC_KEY_PASSWORD`. For notarization, create an
[app-specific password](https://account.apple.com/account/manage) →
`APPLE_APP_SPECIFIC_PASSWORD`, plus `APPLE_ID` (account email) and
`APPLE_TEAM_ID` (Membership page).

**Windows**: buy an **OV or EV code-signing certificate** from a CA
(Sectigo, DigiCert, SSL.com; ~$80–400/yr; EV clears SmartScreen fastest);
export as `.pfx`; `base64 -i cert.pfx` → `WIN_CSC_LINK`, password →
`WIN_CSC_KEY_PASSWORD`.

Add the secrets (repo- or org-level), push the next tag or re-run the
workflow, and the installers come out signed — no code changes needed.

## Health data

JIM-mini handles PHI. Before a production release, review
[docs/hipaa-baa.md](hipaa-baa.md) — the safeguards checklist and the Business
Associate Agreement that must be signed with the hosting / KMS provider.
