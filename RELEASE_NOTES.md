# JIM-mini v0.4.6 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.4.6` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.4.6** — the round where verification matched the deployment.
One of three interoperating products, all three cut together at this
version.

### Signup that fits where it runs

A desktop install has no mail service, so no email can ever arrive — yet
0.4.4's code screen sat waiting for one. Now:

- **Desktop (no mail transport): signup goes straight in.** The machine
  owner is trusted on a single-user local install — there is no inbox to
  prove and nothing to prove it to. Create account → you're in.
- **Hosted (SMTP configured): a real email with a clickable verify link**,
  the shape every mainstream flow uses, with the 6-digit code as fallback.
  Click the link in your mail and **the app continues on its own** — it
  holds your email and password, so it signs in the moment the address is
  proven.

### Also fixed

- A signup that crashed mid-flight (0.4.3) no longer strands the retry: a
  pending account routes straight to verification with a fresh code; an
  already-verified address routes to sign-in.
- The packaged app can open its own backend log from the verification
  screen (Electron bridge) — relevant on deployments without mail.

### Verification

556 tests green. The frozen binaries were rebuilt and the full first
run driven against them — signup straight into a session, personal routes,
sign-in.

### Install

Download the installer for your OS from the assets below (built by the
`desktop-release` workflow from the `app-v0.4.6` tag) and double-click —
create your account and you are in.

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
