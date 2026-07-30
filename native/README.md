# JIM Guardian — native apps

True-native scaffolds of the JIM-mini / Guardian client for three platforms,
each a separate idiomatic codebase (per the "native per platform" choice), all
talking to the same [JIM backend](../jim/api.py).

| Platform | Stack | Run in | Folder |
| --- | --- | --- | --- |
| **iOS** | Swift + SwiftUI | Xcode Simulator (macOS) | [`ios/`](ios/) |
| **Android** | Kotlin + Jetpack Compose | Android Studio emulator | [`android/`](android/) |
| **Windows** | C# + WinUI 3 | Windows 10/11 desktop | [`windows/`](windows/) |

Each target ships the same screens, exercising the real API end to end:

**Welcome / Enroll** → `POST /enroll` · **Overview** → `GET /baseline` + model
picker (`/models`, `/model/{uid}`) · **Live Monitoring** → `POST /monitor` ·
**Check-in** → `POST /checkin` · **Coach** → `POST /coach` · **Life** (goals /
habits / journal) → `/goals`, `/habits`, `/journal` · **Safety** — SOS + flow
(`/emergency`), escalation policy + sensitivity (`/escalation-policy`,
`/sensitivity`), robot helpers (`/robotics/catalog`, `/robots/{uid}`, and
first-aid commands via `/robots/{uid}/{rid}/command` — assist-rated bodies
fetch the AED, coach the CPR playbook aloud, and meet EMS; perform-rated
platforms like Tesla Optimus, Figure 03, and Atlas can additionally deliver
chest compressions after an on-scene human confirms), the **autonomous-
resuscitation waiver** (`/waivers/{uid}` — a signed, revocable liability
waiver that pre-authorizes automatic operation: CPR that starts on
detection and a fully-automatic AED that shocks on its own rhythm analysis
after the robot verifies everyone is clear; without it, every start is
confirm-gated and no shock is ever delivered — and even with it, a shock
only ever follows the AED's analysis, never the robot's judgement), and the
Medical ID card (`/medical-id/qr/{uid}`) · **Connect** — consented data
sources (`/sources/{uid}`), social-platform connections (`/social/{uid}` +
collect/publish), the connected-apps catalog (`/connectors/catalog`,
`/apps/{uid}` + collect), and **Community** — the door out to QRME's rooms
and local places (`/community/{uid}` + visits, below)

### The effectiveness loop, the model, and the name

Three things the backend had always answered but only the web console asked
for. All three now have native doors:

- **"Did that help?"** sits on Monitor (`/followup/{uid}`), spec [0039]. It is
  read from the route rather than from the monitor reply, so a question opened
  in an *earlier* session is still asked — a question the app drops is a
  question nobody ever answers. Answering "it did not" is not a complaint filed
  away: the escalation ladder runs again with the ineffective-guidance rung and
  the screen names the people reachable right now, which is the spec's second
  door (a support person **or** the emergency contact, shown as people rather
  than as a tier).
- **What JIM has learned about you** on Overview (`/adaptation/{uid}`), claim
  11's user-specific model. Rendered as counts off this user's own history —
  which guidance actually helped and how often — never a score, and it says
  plainly that nothing was sent to a model vendor to build it.
- **Your name here** on Overview (`/anonymity/{uid}`), spec [0031] / box 212.
  The posture as a tradeoff rather than a switch: what the choice keeps (every
  emergency path, your own records) beside what it costs (no legal name for
  responders unless you left one), both taken from the server's own lists.

### Community — a door, not a copy

The **Community** panel is the filing's FIG. 2 boxes 222–226: interact with
others, moderated storage, community interaction, local events and forums in
every language. None of it is built a second time in the shells. It exists in
QRME, where the moderation, the rooms and the languages already are, so the
panel opens a door and says so in the same breath — rooms link out to QRME
under the user's own QRME identity, and the conversation stays there.

Two details are deliberate. The **posture** list ("what JIM does not do":
mirror the conversation here, post on your behalf, share your health data) is
rendered from the booleans the server returns rather than typed out as
reassurance, so the screen cannot drift from what the bridge does. And opening
a room posts to `/community/{uid}/visits` **before** launching the browser: the
visit note is the part that belongs to JIM, an event on the user's own
timeline, and it records that a door was opened and nothing from inside it.

On the phone form factors, Monitor, Check-in, and Coach sit behind a single
**Care** tab (segmented on iOS, a `TabRow` on Android) so the bottom bar stays
at five destinations; Windows keeps them as flat sidebar items.

They persist the returned `user_token` so the app resumes signed-in, and share
the JIM dark-OLED palette so all three feel like one product. See each folder's
README for the exact build/run commands.

Two cross-cutting guarantees ride on every guidance surface:

- **Language** (`/languages`, `/language/{uid}`; chosen at the enrollment
  gateway and changeable on the Overview screen): everything drafted for the
  user is delivered in their language —
  model text is *generated* in-language, and the safety-critical
  deterministic content (CPR/AED playbooks, waiver terms) is hand-translated
  for every supported language (es, fr, de, pt, it, ja, zh, hi, ar) rather
  than machine-mangled; an unkeyed string still falls back loudly to
  English. Delivery mode is the user's choice: **pre-translated** (default —
  everything arrives in-language) or **on-demand** (originals kept). Either
  way, `POST /translate/{uid}` — the Translate tool on the Overview screen —
  turns anything the user runs across into their language: hand translations
  win for known safety strings, the user's own model translates free text,
  and the offline stub says it cannot rather than pretending.
- **Provenance**: every guidance and coach response carries a `provenance`
  block — the published sources it derives from (publisher, document, URL,
  and what each supports), how the text was produced (deterministic playbook
  vs. model-generated), and which model produced it — rendered under the
  advice so it can be verified at the source instead of taken on faith.

## Start the backend

All three point at the local dev server. From the repo root:

```bash
JIM_CORS_ORIGINS=* uvicorn jim.api:app
```

Host addresses differ by platform, and each client already defaults correctly:

| Platform | Reaches the host at |
| --- | --- |
| iOS Simulator | `http://127.0.0.1:8000` |
| Android emulator | `http://10.0.2.2:8000` |
| Windows | `http://127.0.0.1:8000` |

On a physical phone, point the client at your machine's LAN IP instead.

## Scope

These scaffolds now cover the full tenant-facing surface of
[`jim/api.py`](../jim/api.py): enroll, monitoring, check-in, coaching, goals /
habits / journal, safety (SOS, Medical ID, policy, robots), and the Connect
surface (sources, social platforms, connected apps).

The existing Electron desktop app in [`../app`](../app) still builds the signed
`.dmg` / `.exe` / `.AppImage` installers; these native targets are additive.

## Do they compile?

`.github/workflows/native.yml` builds all three on every change to `native/`:
XcodeGen + `xcodebuild` for the simulator on macOS, `gradle assembleDebug` on
Linux, and MSBuild on Windows. Compile only — no signing, no packaging.

This is newer than the code it checks. Until it existed, these sources had
been verified by reading and by brace/XML well-formedness checks, which catch
a typo and nothing else. Treat a green run as the first real evidence, not a
long-standing guarantee.

## Do the paths resolve?

Compiling is not the same as working. A path is a string in all three
languages, so a mistyped one compiles perfectly, ships, and 404s in the field —
which is exactly how QRME's community wall shipped with dead like, comment and
share buttons in every release that had them.

[`jim/tests/test_client_routes_exist.py`](../jim/tests/test_client_routes_exist.py)
extracts every API path literal from `native/` — about 45 per shell — with the
HTTP method each is sent with, and asks the real router whether that *pair* is
accepted. Method matters as much as address: a shell sending POST where only
GET is mounted gets a 405, which is the same dead button as a 404. Each
language states its verb differently — Swift labels it, Kotlin passes it
positionally, C# encodes it in the helper's name — so the check reads all three
rather than assuming GET. The console is held to the same check, so the
two halves of the contract are compared with each other rather than each with
itself.

Two limits worth stating. Routing-level matching cannot see a refusal that
happens *after* dispatch, inside a handler. And a path assembled from pieces at
runtime, rather than written as one literal, is invisible to any static scan.

---

## Matthew 7:24–25

> "Everyone then who hears these words of mine and does them will be like a
> wise man who built his house on the rock. The rain fell, the floods came, and
> the winds blew and beat on that house, but it did not fall, because it had
> been founded on the rock."

And lo, I am building an ark — not to flee from the world, but to shelter those
lost in the storm of confusion. The old systems falter; they are built upon the
soft earth. They sink beneath the weight of their own making.

A new thing is rising. A non-biased networked sanctuary, founded in trust,
cloaked in privacy, and guided by wisdom. It shall not consume, but uplift. It
shall not spy, but serve.

Help is coming.
The people are gathering.
The builders will show themselves.
And those with the vision shall enter in.
