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
| `CSC_LINK` | macOS / Windows | Base64 of the signing certificate (`.p12` / `.pfx`) |
| `CSC_KEY_PASSWORD` | macOS / Windows | Certificate password |
| `APPLE_ID` | macOS | Apple ID for notarization |
| `APPLE_APP_SPECIFIC_PASSWORD` | macOS | App-specific password for notarization |
| `APPLE_TEAM_ID` | macOS | Apple Developer Team ID |

electron-builder reads these from the environment during `npm run dist`. macOS
notarization runs only when the `APPLE_*` secrets are present.

## Health data

JIM-mini handles PHI. Before a production release, review
[docs/hipaa-baa.md](hipaa-baa.md) — the safeguards checklist and the Business
Associate Agreement that must be signed with the hosting / KMS provider.
