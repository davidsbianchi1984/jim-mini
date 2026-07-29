# JIM-mini v0.4.8 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.4.8` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.4.8** — the round where the app can actually send email. One
of three interoperating products, all three cut together at this version.

### Mail is configuration, and now it is in the app

An app cannot send email by itself; it has to hand the message to a mail
server. Until now the only way to name one was an environment variable —
so a desktop install never could, and a verification email was never going
to arrive no matter how many times it was requested.

**Settings → Email delivery** now takes a mail server, username, app
password, from address and link address. It says plainly which source is in
force (environment beats the settings screen beats nothing), and it
**sends a real test message on demand** — reporting exactly what the mail
server said rather than claiming success. The password is stored on the
machine it was typed on and is never returned by the API.

Configure one and local signup becomes genuine email verification again,
with the clickable link as the headline and the 6-digit code as fallback.
Leave it empty and the app says so, and lets you in — because an
unprovable inbox is not a gate, it is a locked door in an empty house.

### Verification

566 tests green, including that the password never comes back out, that
the environment outranks the settings row, that a failed send reports the
server's own words, and that configuring mail flips signup from local
activation to a real emailed link.

### Install

Download the installer for your OS from the assets below and double-click.

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
