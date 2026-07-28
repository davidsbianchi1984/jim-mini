# JIM-mini v0.4.4 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.4.4` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.4.4** — the round where the Windows signup 500 died. One of
three interoperating products, all three cut together at this version.


### The fix

With no mail server configured, the verification code prints to the server
console — in a banner drawn with box characters that the frozen Windows
backend's cp1252 console encoding cannot represent. The print raised
mid-request, so **every signup answered "Internal Server Error"** on the
one platform the console transport serves most — found by a real first-run
report within the hour of 0.4.3 shipping. The banner is ASCII now, the
frozen entry point reconfigures stdout/stderr to replace rather than raise,
and a test encodes the console delivery to cp1252 forever
(mutation-checked). The console also stops hiding one error behind another:
a non-JSON body ("Internal Server Error") now surfaces as the server's own
words, not a JSON-parse exception.

### Verification

553 tests green.

### Install

Download the installer for your OS from the assets below (built by the
`desktop-release` workflow from the `app-v0.4.4` tag) and double-click.

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
