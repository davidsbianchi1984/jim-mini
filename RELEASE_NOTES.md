# JIM-mini v0.17.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.17.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.17.0** — the community door opens on every shell.

The door out to QRME's rooms and local places reaches iOS, Android and
Windows — FIG. 2's boxes 222–226 as a fourth **Community** panel in
Connect, opened rather than reimplemented, because the moderation, the
rooms and the languages already live in QRME.

Two details are deliberate. The "what JIM does not do" list — mirror the
conversation here, post on your behalf, share your health data — is
rendered from the booleans the server returns rather than typed out as
reassurance, so the screen cannot drift from what the bridge does. And
opening a room records the visit *before* launching the browser: that note
is the part that belongs to JIM, an event on the user's own timeline
saying a door was opened and nothing from inside it.

Two things JIM already knew also got screens. **What JIM has learned about
you** shows the claim-11 adaptation profile in plain terms — the
confidence earned from your own history, which guidance actually helped
and how often — with the reminder that nothing was sent to a model vendor
to build it. **Your name here** states your anonymity posture: what the
choice keeps, and what it costs.

**Fixed** — the Windows palette had no `JimT3Brush`. The dimmest text tier
exists in the Android and iOS themes but the desktop resources stopped at
`T2`, so a page reaching for it would have failed to load its resources
rather than merely looking wrong.
