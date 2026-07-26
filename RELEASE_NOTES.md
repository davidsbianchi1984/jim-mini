# JIM-mini v0.3.0 — release notes

*Ready-to-paste body for the GitHub Release created when you push the
`app-v0.3.0` tag. Kept in sync with [CHANGELOG.md](CHANGELOG.md).*

---

**JIM-mini v0.3.0** — the release where the Guardian reaches a person. It could
delegate a condition to a synthetic specialist; now it can hand over a task that
outlives the app being closed, and find a **real clinician** near the user. One
of three interoperating products (with
[qrme](https://github.com/davidsbianchi1984/qrme) and
[pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
version.

### Highlights

- **Reaching a real clinician** (`jim/referral.py`). Maps a condition to a care
  area, finds clinicians near the user, and asks QRME to assemble the summary
  and raise the signature that would release it.

  **JIM never holds the credential and never relays the assertion.** The
  signature is against *QRME's* relying party, over a challenge QRME minted, so
  the Face ID prompt belongs to QRME and the assertion travels from the user's
  device to QRME directly. A guardian product that could mint the consent for
  releasing its own user's health record would be exactly the wrong shape, and
  standing in the middle of the one exchange that proves the user was present
  would defeat the point of collecting it. JIM stores a handle — not the
  summary, the signature, or the link — and a test asserts the transcript never
  reaches its database.

  **Locality is a town, not a position.** `sources` already carries a consented
  `location` feed and this deliberately does not read it: live position is a
  stream, and matching a clinic needs a place name. Typing "Leeds" once is a
  smaller disclosure than a product inferring it continuously.

- **Handing a specialist a task, not a turn** (`jim/handoff.py`). Tandem
  guidance sends one message and gets one reply — right for *"say something
  supportive"*, wrong for *"read what we have, draft the summary, hold it until
  somebody confirms"*. QRME runs the second as a workflow; this is JIM's side.

  **Never on the emergency path.** `escalation.decide` resolves in one call and
  must keep doing so — multi-step work is by definition slower than the thing it
  would be blocking. Nothing here is reachable from `monitor`, and starting one
  is explicit: a detection can *warrant* a handoff, a person starts it.

  JIM keeps the task's **status only**. The drafts stay in QRME under its own
  moderation and the user's capability token; mirroring them here would quietly
  make JIM a second store of somebody's generated health correspondence.

- **Contribution preview and revoke** (`jim/contribution.py`). The settings
  screen has offered *"Contribute data — preview before it leaves"* since the
  cloud tier shipped, and **the API could do neither half**: `cloud.contribute`
  posted a payload, returned a bool, and wrote nothing down. There was nothing
  to preview, and consent described as *revocable* meant only *stoppable*.

  **One payload builder, used by both paths** — the preview calls the same
  function the real send calls. A preview assembled separately is a
  *description* of the payload, and descriptions drift from what they describe.
  A refused post is not logged, because that would offer a revoke button for
  data that never left; and revoke reports its local and gateway halves
  separately, because a gateway that cannot be reached must neither fail the
  button nor let JIM claim a deletion that did not happen.

### Screens

**61 · What Would Be Shared** (every line a real field of the payload),
**62 · Specialist Working**, **63 · Find a Clinician**, **64 · Sign to Release**.

### Verification

346 tests green (34 new this release). 96 routes. 128 screens. Mutation-checked:
logging a refused send, claiming gateway deletion regardless of the answer, and
treating an empty phase intersection as a startable task each fail the test that
forbids them.

### Install

Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
`python -m jim` from source and pick your device — see the [README](README.md). Installers are signed
only if signing secrets are configured; otherwise they are unsigned (see
[docs/releasing.md](docs/releasing.md)).

**Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
