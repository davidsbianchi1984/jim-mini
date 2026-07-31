# JIM-mini v0.21.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.21.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.21.0 — cut in step with QRME.**

The three products are cut together at one version so an installed suite never
has to reason about which piece is which release. This one carries no JIM-mini
feature work: the round that produced it ran in QRME, where four console doors
were built for backend features that had none.

Three of those four rounds found a defect behind the door, and the pattern is
worth naming here because the same door audit runs in this repository:

* a room's transcript and its `advance` route asked for **no credential at
  all**, while the microphone disclosure two routes away checked membership;
* a delegation policy was publishable and impossible to take up, with every
  backend rule already correct;
* `verify_package` reported **the signature is invalid** for a package that
  was merely missing a field, when the cryptography had verified — the reason
  given as a bare `KeyError` repr.

In each case the argument against the defect was already written down
somewhere else in the same repository. That is the whole return on building
the door: it puts you in front of the thing the door leads to.

## The console backlog here

JIM-mini's own per-client audit still records **109 routes** the console cannot
reach on its own, against a union backlog that looks much smaller because the
iOS, Android and Windows shells can reach them. That number is the honest one
and it is unchanged this release — the ratchet holds it from rising.

## What changed

Version strings only, plus the release-title convention recorded in
`docs/releasing.md`: release titles now carry the product name, so
`JIM-mini app-v0.21.0` rather than a bare tag.
