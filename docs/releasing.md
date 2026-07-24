# Releasing

JIM-mini ships two artifacts: the Python backend and the guardian console. This
describes cutting a versioned release and how (optional) code-signing works.

## Cut a release

1. Update [CHANGELOG.md](../CHANGELOG.md) — move `Unreleased` items under the new
   version and date it. Refresh [RELEASE_NOTES.md](../RELEASE_NOTES.md).
2. Bump `version` in `pyproject.toml` and `app/package.json` if changed.
3. Tag and push:

   ```bash
   git tag app-v0.1.0
   git push origin app-v0.1.0
   ```

The `app-v*` tag triggers `.github/workflows/desktop-release.yml`, which builds
the console into per-OS installers (`.dmg` / `.exe` / `.AppImage`) on real
macOS / Windows / Linux runners and attaches them to a GitHub Release. Paste
`RELEASE_NOTES.md` into the release body.

A manual **Run workflow** builds and uploads the installers as artifacts
*without* publishing a Release — useful for a dry run.

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
