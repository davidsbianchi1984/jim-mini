# JIM-mini v0.18.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.18.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.18.0** — the rest of what JIM knew, on every shell.

Three features that existed in the backend and the web console and nowhere
else now reach iOS, Android and Windows.

**"Did that help?"** sits on Monitor (spec [0039]). It reads from
`/followup/{uid}` rather than the monitor reply, so a question opened in an
*earlier* session is still asked instead of being quietly dropped —
a question the app forgets is a question nobody answers. Saying it did not
help is not filed away: the escalation ladder runs again with that fact in
it and the screen names the people reachable right now, as people rather
than as a tier.

**What JIM has learned about you** and **Your name here** join Overview,
where these shells already keep the baseline, model and language settings.
The adaptation profile renders as counts off the user's own history, never
a score, with the statement that nothing was sent to a model vendor to
build it. The anonymity posture renders from the server's own keeps/costs
lists, so what is on screen cannot drift from what the code does.

**And all four new doors got drawn and taught.** Screens **89 Did That
Help?**, **90 What JIM Learned**, **91 Your Name Here** and **92
Community** join the gallery, each with a lesson, each reachable by asking
the assistant in ordinary words — "it did not help", "what JIM knows about
me", "pseudonym", "rooms".

**Fixed** — the Windows palette had no `JimT3Brush`. The dimmest text tier
exists in the Android and iOS themes but the desktop resources stopped at
`T2`, so a page reaching for it would have failed to load its resources
rather than merely looking wrong.
