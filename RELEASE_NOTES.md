# JIM-mini v0.4.2 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.4.2` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.4.2** — the release where the installer you download actually
gets you running. One of three interoperating products (with
[qrme](https://github.com/davidsbianchi1984/qrme) and
[pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at
this version. Every change in it came from one first-run bug report against
a real Windows install of the .exe.

### The first run stops lying

- **The enrollment form pre-filled a developer's sample name and birthdate**
  — which the reporting user's own name happened to collide with. Identity
  fields start empty now, and Get Started stays disabled until name,
  birthdate and consent are all really given: a pre-filled birthdate in an
  age-verification field is a wrong answer already submitted.
- **"Failed to fetch" told a fresh install nothing.** The installer ships
  only the console; the Guardian runs as a local service. Onboarding now
  checks for it before the form is filled in and, when unreachable, says
  exactly that — with the command to start one and an editable backend URL
  with retry. Every API error names the backend and the fix.
- **The window was titled "QRME".** It says *JIM Guardian* now.

### `python -m jim serve` answers the packaged console

Even the app's own recovery instructions dead-ended: the console calls the
API cross-origin, and `serve` never set `JIM_CORS_ORIGINS` — so every
request died as *"Failed to fetch"* against a backend that was running
fine. A loopback serve now defaults CORS open (the posture the in-app hint
always instructed), announced on stdout, `--no-cors` to close it, never on
a non-loopback bind. Personal endpoints still require the user's bearer
token. And the command the console recommends is the right one now — bare
`python -m jim` only prints the launcher menu.

### The installers are named for their release now

0.4.0 and 0.4.1 both attached installers stamped **0.3.3** — built from the
right tag, named for the wrong release, invisible to the auto-updater. This
is the first release whose installers come out named for it, and the guard
got wider: **all five version strings must now agree** (pyproject had
quietly sat at 0.4.0, the lockfile roots at 0.3.3).

### The default model is current

The Anthropic provider defaults to **`claude-opus-5`** (`JIM_MODEL` still
overrides), matching QRME — the user can still route guidance through
ChatGPT, Grok, Perplexity, Gemini, or the offline stub via
`PUT /model/{user_id}`.

### Verification

530 tests green. The serve-CORS default and the five-way version agreement
are both guarded, the CORS guard mutation-checked; the fixed console was
driven end-to-end in a real browser against a bare `python -m jim serve` —
no env vars, panel clears, enrollment lands on Overview.

### Install

Download the installer for your OS from the assets below (built by the
`desktop-release` workflow from the `app-v0.4.2` tag — and named 0.4.2,
which is the point), run `python -m jim`, or open it on your phone — see
the README.

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
