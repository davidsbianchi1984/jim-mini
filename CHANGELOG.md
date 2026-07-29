# Changelog

All notable changes to JIM-mini are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

**Guided wellness — the on-purpose half of guidance.** From the field
videos, built as protocols rather than generations: guided calm
sessions (quick reset, box breathing, 4-7-8, a ten-minute sit) with
timed steps the console paces and can speak; workout plans shaped to
the minutes you have, your level and focus, warm-up and cool-down
non-negotiable; and meal plans shaped to goal and dietary preferences
with the honesty rails stated on the plan. Nutrition becomes a
first-class Coach area. All three land in the events stream, so the
insights layer sees practice the way it sees check-ins. New Wellness
tab in the console.

## [0.14.5] — 2026-07-29

**A fall reaches the Guardian.** The watch drip carried only numbers,
which silently dropped the one reading a senior on the floor most
needs delivered: the fall event. The drip now accepts the detector's
own vocabulary — `movement: fall/collapse/immobile`, Shortcuts'
`fall_detected: true`, `pulse: absent/weak` — whitelisted words, never
free text, so the deposit-only posture holds. A fall was already a
critical detection, so with the crash watch armed the whole senior
chain now runs end to end: the watch feels the fall, JIM asks "are
you okay?", and silence summons the programmed help. Every surface's
copy now names the fall.

**The crash watch reaches the native shells.** iOS (SwiftUI), Android
(Compose) and Windows (WinUI 3) each gain a Crash tab on Safety: the
arming form (trusted person, attempts, minutes per attempt, and the
emergency-services box worded as the request it is), the live "JIM is
asking: are you okay?" card with the I'm-okay button, the tripped
note, and the armed-quietly line — against the same
/crash-watch routes the console uses.

**The docs web catches the field round.** The crash watch and the
journal enter every binding the repo keeps: drawn screens 87 (Journal)
and 88 (Crash Watch), tutorial lessons claiming them, README gallery
rows, and a `crashwatch` dock face — the question and the attempt
count, never the reading. The journal stays out of the pane on
purpose: what somebody wrote about their own day is not a glance
(the NEVER list said so before the tab existed).

## [0.14.4] — 2026-07-29

**The voice orb, and the help box.** Talking with the Coach now looks
like talking: a breathing orb takes the screen while JIM listens
(green) or speaks (violet) — tap anywhere to end it. And JIM gets its
own help box on every screen, matching QRME's: written directions
about where each door lives (never a model call, so it cannot invent
a feature), handing anything beyond the app itself to the Coach —
which is JIM.

**The crash watch, and the journal's door.** Field request, verbatim
in spirit: "if pulse gets shallow and stops and JIM gets too many
non-responsive attempts, contact emergency services and a trusted
person." The crash watch (jim/crashwatch.py) is the vigil's acute
sibling — armed in advance by the user, off by default: a critical
reading opens "are you okay?", N unanswered attempts (each with its
window, deadlines marching from the moment the concern opened) trip
it, the trusted person is contacted (emailed for real when mail is
configured) and, only if the box was ticked, an emergency-services
dispatch request is recorded and relayed — worded as a request,
because a local app cannot itself place a call. Any sign of the
person ends it; drift check-ins stay calm and can never trigger it,
and the Baseline screen now says so accurately. And the journal the
backend always had finally gets its console tab — typed or spoken
(the mic transcribes into the box for the user to fix before saving),
newest first, sealed on private plans.

**Two versions answering is no longer a mystery.** Field report: a
fresh console over a stale backend answers "Not Found" on every newer
screen while looking otherwise alive — the shell refuses to adopt a
version-mismatched backend on its own port, but a stored base address
(for example the LAN address saved for the phone bridge) can still
steer the console to an old process. The console now performs the
version handshake itself: it compares its build version against
/health's on launch and, on mismatch, shows a banner naming both
versions and the address — with a one-click "use this app's own
backend" when a stored address is the culprit.

## [0.14.3] — 2026-07-29

**Every README ends on the rock.** The Matthew 7:24-25 passage that
closes the root README now closes every README in the repo (app,
native shells, and the rest), byte-identical, at the very end — and a
binding test enforces the standing rule so the next README added
cannot forget it.

## [0.14.2] — 2026-07-29

**Docs: suite mode enters the tandem contract.** `docs/tandem.md`
(byte-identical across the three repos) now describes how the suite
gateway wires both tandem joints itself — JIM's QRME client and QRME's
vault tenant (`suite:qrme-vault`) — and how the operations provenance
view re-draws PDI's per-tenant isolation by owner when every suite
identity's seals share the one tenant.

## [0.14.1] — 2026-07-29

**The coach knows a care plan landed.** One context line when the
care team wrote a joint plan in the last week — the goal, never the
plan text, worth walking through together and never presented as
homework.

## [0.14.0] — 2026-07-29

**Home and the pane learn the care team.** The Overview's action row
gains Medications and Care Team; the corner pane gains a careteam face
— whether a joint plan is waiting to be read, never its contents.

## [0.13.1] — 2026-07-29

**No functional changes here**: cut with the siblings. The shared
tandem contract and this repository's invention disclosure caught up
with the ecosystem round; in QRME, the demo org and hardening caps.

## [0.13.0] — 2026-07-29

**The care team is an organization.** Link your own QRME org and name
the desk that speaks for the Guardian; when concerns stack — a
drift-band crossing while a medication's adherence is below 75% — the
Guardian takes the situation to the whole team as one coordination
goal, and the joint plan lands back as a care plan. Your own
credential, pasted knowingly; summaries cross, never raw readings;
once a day at most, calm path only. Screen 86, and the console's Care
Team tab. Proved end-to-end against live QRME and PDI processes.

## [0.12.0] — 2026-07-29

**No functional changes here**: cut with the siblings. In QRME, the
filed patent specification was mined for everything the apps did
not yet do: hybrid profiles blended from several people, real-time
simulation of the represented person's likely decisions, and
replies that adapt to where the person actually is — backend and
console both.

## [0.11.1] — 2026-07-29

**No functional changes here**: cut with the siblings. In PDI, the
desktop app finally carries its own vault — bundled backend, persistent
master key, and a release gate that proves the first run.

## [0.11.0] — 2026-07-29

**There are no functional changes to JIM-mini in this release**: cut with
the siblings. In QRME, the console caught up with its backend — Discover,
Friends (founder first), Rooms, a memory vault that names names, and a
chat fallback that stopped performing a character.

## [0.10.0] — 2026-07-29

### Added

- **A real offline model** (`jim/llm.py`; the *Local (Ollama)* tile).
  The offline helper was a canned fallback and said so; now there is a
  door to actual local intelligence: install Ollama (ollama.com), pull a
  model like `deepseek-r1:1.5b`, and JIM finds the daemon on its own —
  the tile lights up configured, no key, and nothing ever leaves the
  machine. Automatic prefers it over the stub when no cloud key exists,
  and **offline mode uses it too**: `JIM_OFFLINE` forbids the network,
  and a loopback model isn't network. `JIM_OLLAMA_MODEL` /
  `JIM_OLLAMA_URL` override the defaults. The stub's chat reply now
  names both ways out: add a key, or install Ollama.

### Fixed

- **Settings stopped implying a tandem switch** — the backend status
  line read "tandem off" as if a button existed; it now says plainly the
  vault tandem is set by the deployment, not a switch. And **Your model
  API key** moved to sit directly under *Which model answers*, where it
  belongs, instead of stranded below Email delivery.

### Changed

- Version aligned to 0.10.0 across the API, the desktop app and the
  Python package — cut together with qrme and pdi at this version.

## [0.9.1] — 2026-07-29

### Fixed

- **The drip address is now an address something answers on** (Settings →
  *Apple Watch*; `app/electron/main.cjs`, `packaging/backend_entry.py`,
  `jim/watch.py`). Reported from the field: the setup card showed the
  machine's Wi-Fi address while the desktop backend listened only on
  loopback — a phone POSTing to it got "could not connect", and the card
  never said so.
  - The card now tells the truth: `phone_reachable` rides the setup
    response, and an amber notice explains when the phone cannot reach
    the address yet.
  - One press fixes it: **"Let my phone reach JIM on this Wi-Fi"**
    restarts the bundled backend listening on the network
    (`JIM_HOST=0.0.0.0`), persistently. Loopback remains the default —
    private until asked, and asked in the exact place the need arises.
    Everything per-user behind the port still requires that user's token.
  - The Shortcut recipe now names the paste spot in capitals — the drip
    address goes in **Get Contents of URL → URL** — and no longer
    promises an hourly trigger Shortcuts doesn't have: Time of Day,
    repeat daily, with a second automation for the evening if wanted.

### Changed

- Version aligned to 0.9.1 across the API, the desktop app and the Python
  package — cut together with qrme and pdi at this version.

## [0.9.0] — 2026-07-29

### Added

- **The medicine cabinet** (`jim/meds.py`; nav → *Medications*;
  `GET|POST /meds/{user_id}`, `PUT|DELETE …/{med_id}`,
  `POST …/{med_id}/log`, `GET …/adherence`). What the user takes, in
  their own words — "the little white one, 10 mg" is a valid name and
  dose.
  - The day's board knows done, due, upcoming and missed — with humane
    grace: 9:07 is not "missed" for the 8:00 pill; a board that says so
    teaches the person to ignore it.
  - One slot has one correctable answer: logging again replaces
    (skipped → taken happens; people find the pill in their pocket).
    Adherence counts whole past days only, so an afternoon dose is never
    "missed" at noon.
  - An as-needed medication can carry a per-day ceiling that **refuses
    to log past itself** and points at the prescriber — recording the
    overage would be complicity.
  - A missed dose — even one marked critical — is a check-in on the
    board and a line in the coach's context ("worth asking about gently,
    never scolding"), never an alarm: this module has no path into the
    escalation ladder.
  - Every dose logged is a sign of life the vigil counts: for the person
    whose only daily interaction is their pillbox, taking their
    medication quietly keeps the vigil stood down.
  - JIM is not a pharmacist: no interaction checker — a toy one would be
    trusted — and the board carries the line "your pharmacist does that"
    on its face.

### Changed

- Version aligned to 0.9.0 across the API, the desktop app and the Python
  package — cut together with qrme and pdi at this version.

## [0.8.0] — 2026-07-29

### Added

- **The vigil — the alarm that fires when the signals stop** (`jim/vigil.py`;
  Settings → *The vigil*; `GET|PUT|DELETE /vigil/{user_id}`,
  `POST …/sweep`, `POST …/resolve`). Every other alarm fires on a
  reading; this one fires on the *absence* of readings — the watch that
  went quiet, the check-in that never came.
  - The steward is chosen, and the message they will read is written, by
    the user in advance — a vigil that composes its own words speaks for
    someone at the exact moment they cannot correct it.
  - Silence is measured against the events table, so any sign of life
    resets it without bookkeeping — and the vigil's own trip is excluded,
    or every trip would reset the very silence it measured.
  - It never escalates past the steward: no emergency services, no
    ladder. Silence is weak evidence; the right response is a person who
    cares knocking on a door.
  - The trip is idempotent (the console sweeps on open; anything else
    may too), emails the steward when mail is configured (degrades to a
    loud console notice when not), and the next reading stands it down —
    showing up IS the all-clear.
  - Cross-product: the trip's event id serves as the attestation
    reference for QRME ownership succession and PDI bequest activation —
    one attested absence carries through all three products.

### Changed

- Version aligned to 0.8.0 across the API, the desktop app and the Python
  package — cut together with qrme and pdi at this version.

## [0.7.0] — 2026-07-29

### Added

- **The app keeps itself current** (`app/electron/main.cjs`,
  electron-updater). On launch the desktop shell asks GitHub Releases
  whether a newer version exists. Windows and Linux download it in the
  background and offer one restart; macOS — which cannot swap an unsigned
  app under itself — says a new version exists and opens the download
  page. Every failure path is silent by design: an update check must
  never stand between the user and the app. Ships *in* 0.7.0, so this is
  the last version anyone has to fetch by hand.

## [0.6.1] — 2026-07-29

### Fixed

- **The coach no longer performs distress it never detected, and the reply
  says who actually wrote it** (`jim/llm.py`, `jim/coach.py`, coach screen,
  Settings → *Which model answers*). Reported from the field: a career
  question got *"I'm here with you [stub guidance for distress]… let's take
  one slow breath together"* — every time, word for word.
  Three stacked causes, three fixes:
  - The deterministic stub keyed on a `condition:` line that chat prompts
    never carry and **defaulted to "distress"** — crisis phrasing in what
    was just a conversation. In chat the stub now explains itself honestly
    ("I'm the built-in offline helper… open Settings → Model") instead of
    playing a counselor.
  - Any model failure — missing key, missing SDK, network, a 529 —
    **silently degraded to the stub with only a server-side log line**,
    while the reply's `generated_by` named the provider that was *picked*,
    not the one that answered. `llm.generate_for_user()` now reports who
    actually produced the words, whether that was a degrade, and why in
    words a user can act on; the coach reply carries it and the console
    shows it — "Answered by anthropic", or an amber warning naming the
    fallback and the reason.
  - Settings said nothing in the worst case: **Automatic quietly resolving
    to the stub** under a screen full of provider logos. The model panel
    now says plainly when replies will come from the built-in helper and
    what to do about it.

### Changed

- Version aligned to 0.6.1 across the API, the desktop app and the Python
  package — cut together with qrme and pdi at this version.

## [0.6.0] — 2026-07-29

### Added

- **The Apple Watch bridge** (`jim/watch.py`; Settings → *Apple Watch*;
  `GET /watch/channel/{user_id}`, `POST …/rotate`,
  `POST /watch/drip/{token}`, `POST /watch/seed/{user_id}`). HealthKit only
  talks to App-Store apps, and JIM does not have one — but every iPhone has
  two free doors out, and both now lead here.
  - **The drip.** A Shortcuts personal automation POSTs Health samples to a
    per-user tokened URL on a schedule. The payload is forgiving on purpose
    (`heart_rate`, `heartRate`, `"72 count/min"`, SpO₂ as HealthKit's
    fraction or a typed percent — all one reading), and every drip runs the
    full detect → drift → escalate pipeline, exactly as if typed on the
    Monitor screen. The reply is deposit-only — received count and a
    noticed flag, never guidance — because the token rides in a URL and a
    URL-bearer credential must not read health guidance back out. A wrong
    token is a 404, not a 403: confirming a channel exists would itself be
    information. Rotating mints a new address and retires the old one
    immediately.
  - **The seed.** The Health app's *Export All Health Data* zip uploads
    straight in; per-day medians fold into the baselines chronologically —
    resting heart rate, HRV, oxygen, respiration, temperature — so months
    of history the watch already recorded become an **established baseline
    on day one** instead of five quiet days of "learning". History is
    context, not news: the seed writes no events and raises no check-ins,
    and raw heart-rate records without the sedentary motion context are
    excluded so exercise never teaches the bands a resting rate that
    isn't. Oxygen's fraction becomes a percent; `degF` becomes °C.
  - The new `watch_channels` table stores the drip token in the clear —
    deliberately, against the house never-return-the-secret rule — because
    this credential can only deposit readings and the setup screen must
    keep showing the URL for a person retyping it into a Shortcut weeks
    later. The comment on the table says so.

### Changed

- Version aligned to 0.6.0 across the API, the desktop app and the Python
  package — cut together with qrme and pdi at this version.

## [0.5.0] — 2026-07-29

### Added

- **Your own normal, and how far from it counts** (`jim/bands.py`, screen
  *Your Baseline*, `GET /bands/{user_id}`, `PUT|DELETE /bands/{id}/{metric}`).
  Detection has always answered *is this an episode?* against rules that hold
  for anybody. This answers the question a person actually asks of a watch
  they sleep in: **am I drifting from my own baseline, either way?** Every
  resting reading now folds into a per-metric baseline — heart rate, HRV,
  oxygen, respiration, temperature, not heart rate alone — and a **band**
  around it marks how far is far enough to say something. Crossing one
  produces a **check-in with the numbers in it**, never an escalation: the
  emergency ladder remains the alarm layer's alone. Bands wait for a
  non-provisional baseline (a threshold drawn around two samples is a line
  on noise), watch **both directions** independently (HRV falling and heart
  rate climbing are both news, and the default for HRV watches only the
  fall), scale with the sensitivity dial, and are adjustable per metric from
  the app.

- **Talk to it, and be answered out loud** (`jim/voice.py`,
  `GET|PUT|DELETE /settings/voice`, `POST /voice/speak`,
  `POST /voice/transcribe`). Typing at a wrist mid-panic is not a plausible
  interaction. **ElevenLabs** (five male voices offered, Daniel by default)
  or **OpenAI** `tts-1` speak the replies; recorded speech goes to Whisper
  or ElevenLabs to come back as words. Neither is required: **without a key
  the device's own voice reads replies aloud** — an app that goes mute
  because a key is missing has chosen the wrong failure. Audio is never
  stored, and the key is never returned by the API.

- **A picker for which model answers** (`app/src/ProviderTiles.tsx`). The
  switchboard has been in the backend since 0.4.3 and nowhere in the app:
  Claude, ChatGPT, Grok, Perplexity, Gemini and the offline stub are now
  tiles you click, each marked in its own colour, each saying whether it is
  configured here and what it resolves to if not. The marks are drawn in the
  app rather than fetched — an installer that reaches out to six vendors'
  CDNs is one that leaks which product you opened.

## [0.4.8] — 2026-07-28

### Added

- **Email delivery is configurable from the app itself** (`mail_settings`,
  `GET/PUT/DELETE /settings/mail`, `POST /settings/mail/test`). Until now
  the only way to make a verification email real was an environment
  variable, so a desktop install could never send one — which is exactly
  why a user watched an inbox that was never going to receive anything. The
  Settings screen now takes a mail server, username, app password, from
  address and link address, says plainly which of the three sources is in
  force (environment > settings > none), and **sends a real test message on
  demand**, reporting what the server actually said rather than claiming
  success. The password goes up and never comes back down. Configuring one
  turns local signup back into genuine email verification, link and all.

## [0.4.7] — 2026-07-28

### Fixed

- **An upgraded app kept meeting the first version's signup.** The desktop
  shell adopted whatever backend answered its port — and on Windows, killing
  the frozen backend's bootloader left the real process alive, so a zombie
  from an early install held port 8000 across every later upgrade and served
  its old API to every new console. Three changes make it impossible:
  `/health` now reports the backend's **version**; the shell adopts a running
  backend **only when that version is its own**, otherwise it takes a free
  port and starts its own there and tells the window which address to use
  (a stored loopback address never overrides it); and quitting kills the
  backend's **whole process tree** (`taskkill /T` on Windows) rather than
  just the launcher. The release gate now also asserts the frozen backend
  reports the version being packaged.

## [0.4.6] — 2026-07-28

### Fixed

- **A stranded pending account can no longer resurrect the email screen on
  a desktop install.** Databases from older builds hold half-made accounts
  (0.4.3 crashed mid-signup) that nothing can ever verify where no mail can
  be sent. Retrying signup on a no-mail deployment now finishes the pending
  account on the spot, under the newly-typed password — the machine owner
  is the only person there. A **verified** account is never overwritten
  this way, on any deployment; SMTP deployments still require the emailed
  proof.

## [0.4.5] — 2026-07-28

### Changed

- **Verification matches the deployment, and the email got a link.** A
  desktop install has no mail service, so no email can ever arrive — yet
  0.4.4's code screen sat waiting for one: a locked door in an empty house.
  Now, with no mail transport configured, signup activates the account
  directly (the machine owner is trusted on a single-user local install —
  there is no inbox to prove and nothing to prove it to). A deployment
  **with** SMTP configured enforces the real proof, and its email now leads
  with a **clickable verification link** (`GET /verify-email/click`) — the
  shape every mainstream flow uses — with the 6-digit code as the fallback
  for a mail client on another device. The app finishes on its own after
  the click: it holds the email and password, so it polls sign-in until the
  address is proven.

### Fixed

- **A crashed signup no longer strands the retry.** 0.4.3's mid-flight crash
  left pending accounts; retrying signup answered 409 and parked the person
  on the form. A pending-account signup now routes straight to the
  verification screen and issues a fresh code; an already-verified address
  routes to sign-in.

- **The packaged app can show you its own log.** The "console" mail
  transport writes to the spawned backend's log file, which the window
  never named and could not open. An "Open the log" button (Electron
  bridge) does now — relevant to resends on deployments without mail.

## [0.4.4] — 2026-07-28

### Fixed

- **Signup answered 500 on the frozen Windows backend.** With no mail server
  configured, the verification code is printed to the server console — in a
  banner drawn with box characters that Windows' cp1252 stdout cannot
  encode. The print raised mid-request and every signup died on the one
  platform the console transport serves most. The banner is ASCII now, the
  frozen entry point reconfigures stdout/stderr to replace rather than
  raise, and a test encodes the console delivery to cp1252 forever
  (mutation-checked).

- **The console showed a JSON-parse crash instead of the server's words.**
  A crashed server answers plain text ("Internal Server Error"), and
  `req()` assumed every body was JSON — so the person saw
  *Unexpected token 'I' … is not valid JSON* instead of the actual error.
  Non-JSON bodies now surface as-is.

## [0.4.3] — 2026-07-28

### Added

- **Accounts: email + password, the address verified before anything
  exists** (`jim/accounts.py`, `jim/mailer.py`). `POST /signup` takes email +
  password + the enrollment fields and creates nothing yet — a 6-digit code
  goes to the address (SMTP when `JIM_SMTP_HOST` is configured, printed to
  the server terminal otherwise), and only `POST /verify-email` enrolls the
  user and mints the first token, so a mistyped address never grows a record
  nobody can reach. `POST /signin` refuses unverified addresses and answers
  unknown-address and wrong-password identically;
  `POST /password/reset/request` + `POST /password/reset` change a forgotten
  password by the same emailed-code proof and revoke every existing session.
  Passwords are PBKDF2 with per-account salts; codes hashed at rest,
  single-use, 15-minute expiry. The console onboarding is now the
  conventional flow: create-account / emailed-code / sign-in tabs, show/hide
  password toggles, a re-enter field checked live, the requirement stated up
  front, and Forgot password.

- **Bring your own model key.** `x-llm-api-key` rides any request into a
  request-scoped context variable the provider layer reads — that request's
  generations run on the caller's credential, never persisted, never
  logged, gone when the request ends. An explicit provider choice plus a
  caller key counts as configured; a key on auto defaults to Claude rather
  than the stub; the deployment's env key remains the fallback (an operator
  lending theirs out). Settings stores the key device-side only.

- **The installer runs itself.** `packaging/backend_entry.py` freezes the
  whole backend with PyInstaller (CORS on, loopback only, data under the
  app's user-data directory); the release workflow builds it per-OS and
  ships it inside the installer; Electron probes `/health`, spawns the
  bundled backend when nothing answers, waits for it, and kills it on
  quit — double-click-and-done, no Python on the machine. A backend the
  user already runs is left alone.

## [0.4.2] — 2026-07-28

### Changed

- **The Anthropic provider defaults to `claude-opus-5`.** The default model
  string in `jim/llm.py` (and the README lines quoting it) still named the
  previous Opus generation. `JIM_MODEL` still overrides, and every other
  provider default is untouched. Mirrors the same change in QRME — the two
  provider layers deliberately share no code.

- **`python -m jim serve` answers the packaged console by default.** The
  installer ships only the console; the Guardian API it calls is started by
  hand — and a loopback `serve` never set `JIM_CORS_ORIGINS`, so every
  console request died as *"Failed to fetch"* against a backend that was
  running fine, including for a user following the app's own recovery
  instructions. A loopback serve now defaults CORS open (the posture the
  in-app hint has always instructed), announced on stdout, with `--no-cors`
  to keep it closed — and never when binding beyond loopback or when an
  explicit allowlist is set. Personal endpoints still require the user's
  bearer token. Four tests, mutation-checked.

### Fixed

- **The desktop installers were labelled 0.3.3.** `app/package.json` carries
  its own version and no cut ever bumped it, so the 0.4.0 and 0.4.1 releases
  both attached installers stamped with the stale number — built from the
  right tag, named for the wrong release, and invisible to the auto-updater,
  which compares package versions and saw nothing newer. Bumped, with a
  test asserting it always matches the API version, because a duplicated
  number with nothing to fail is how the last three of these happened. This
  release is the first whose installers come out named for it.

- **The enrollment form shipped with a developer's sample name and birthdate
  in the boxes** — reported from a real Windows install, by a user whose
  own name it happened to collide with. Identity fields start empty now, and
  Get Started stays disabled until name, birthdate and consent are all
  given: a pre-filled birthdate in an age field is a wrong answer already
  submitted.

- **"Failed to fetch" told a fresh install nothing.** Onboarding now checks
  for the Guardian backend before the form is filled in and, when
  unreachable, says exactly that — with the command to start one and an
  editable backend URL with retry. Every API call names the backend and the
  fix instead of surfacing the raw fetch error, and the command is the right
  one now: `python -m jim serve` (bare `python -m jim` only prints the
  launcher menu).

- **The desktop window was titled "QRME".** Retitled *JIM Guardian*, and the
  preload bridge renamed `jimDesktop` to match.

## [0.4.1] — 2026-07-28

### Added

- **Platform custody, and a vault gate that asks about the plan** —
  `storage.CUSTODY`, `storage.vault_for`. The free plan is the familiar
  hosted-assistant arrangement: JIM-mini holds the record and the person has
  access to it, over ordinary HTTPS, never through a vault. Named as **custody
  rather than ownership**, deliberately — a product decides who holds and
  operates a record, and does not get to decide away somebody's statutory
  rights over their own personal data. On a product holding medical data that
  distinction would be tested.

### Fixed

- **The README's own arithmetic was wrong** in three places — `jim/capture.py`
  claimed 27 tests against 35, `jim/tiers.py` 25 against 26, `jim/storage.py`
  36 against 51. A guard now verifies every "`module.py`, N tests" claim
  against the files, because nothing fails when a file grows a test.

- **A photograph never actually reached a clinician.** `jim/capture.py` said
  from its first line that one could "reach a real clinician through the
  referral flow that already exists", and for a release that sentence was true
  of nothing: `attach_to_referral` returned a decision no caller consumed,
  `mark_released` was dead code, and `referral.prepare` had no idea captures
  existed. The README, the walkthrough and the pull request all repeated the
  claim. `POST …/referral/prepare` now takes `capture_ids`; the package it
  returns carries their metadata — never bytes — so the person reads exactly
  what would go before signing; and `POST …/referral/requests/{id}/released`
  stamps them. Mutation-checked.

- **`seen_by_clinician` claimed something the app cannot know.** The signing
  ceremony belongs to QRME and JIM never observes a clinician opening
  anything, so the field is now `released_to_clinician`. Released is not
  opened, and on a record a clinician might later be asked about that is not
  a distinction worth blurring.

- **A skipped test on the feature's own join.** The first version of
  `test_a_prepared_referral_carries_the_captures` used a fixture with no
  tandem link and skipped rather than failed. A skip on the test that proves
  the whole feature works is not a pass; it now builds a real linked
  specialist.

- **The walkthrough and screen 79 described encryption but not custody**,
  which is the part the free plan is actually about. Both now say we hold it
  and you have access to it.

- **`docs/tandem.md` described sealing as unconditional.** It was written when
  a paid plan was the only kind. Now says which plans reach PDI at all —
  byte-identical in all three repositories, as that file always is.

- A guard ported from QRME rejecting user-facing copy that hardcodes a count
  of refusals disagreeing with `len(SENSITIVE)`. JIM-mini's count is right
  today; this is here for the day somebody adds a third.

- **A free account's record was being sealed into the vault.** Every seal
  point read `if pdi is not None` — whether the *deployment* has a vault, not
  whether the *account* is on a plan that uses one. On a PDI-backed deployment
  that put a free account's journal, check-in notes and detection detail in a
  vault it was not paying for and could not hold a key to. Twelve write sites
  now resolve through `_vault(user_id)`; guarded by counting vault writes
  rather than by reading call sites, because reading call sites is how they
  all stayed wrong.

  Reads and deletions deliberately keep the real vault: a plan-gated vault on
  a read strands a downgraded account's history behind a billing change, and
  on a delete it leaves records nobody can reach and calls that erasure. Both
  are asserted.

- **The access log told a free account a comfortable lie.** On a vault plan an
  empty list means nobody touched the records and the chain proves it. On an
  open plan there is no chain, so an empty list means nothing was *recorded* —
  and a bare `[]` reads as the first. `GET /access-log/{user_id}` now carries
  `access_record_kept` and says which of the two it is, including the awkward
  middle where an account downgraded off Basic has real earlier entries and
  nothing recorded since.

- **A free plan, with nothing private about it** — `jim/storage.py`, 36 tests,
  screens 78, 79 and 80. Two storage postures: **open cloud** (Free — JIM's own
  database, in the clear) and **encrypted vault** (Basic and Pro — journal
  entries, check-in notes, detection detail and every capture sealed in PDI
  under a key you can hold). `DEFAULT_PLAN` is now `free`, and the ladder runs
  visitor → free → basic → pro.

  **Free and Basic reach identical capabilities** — `guardian` and `emergency`
  both start at `free`, and `includes("free") == includes("basic")` is asserted
  by test. What $20 buys is the vault, not a feature.

  **This is partly an admission of an old behaviour.** JIM has always degraded
  gracefully when no PDI was configured — `life.add_journal`, `life.check_in`
  and `guardian._event` each fall back to writing the payload straight into the
  local table. A deployment without a vault has been storing check-in notes and
  medical event details in the clear the whole time and never said so on any
  screen. The free plan makes that a documented posture with a disclosure
  attached.

  **Two payloads the open store will not hold**: a photograph of a body
  (`jim/capture.py`), and a child's record on a guardian's account
  (`family.enroll_child`, plus `tiers.guard_dependant_write` for the diary
  afterwards — enrolling on Basic and moving to Free the next day is one API
  call, and the enrolment check alone would not have held).

  **And what is deliberately not on that list, which is the whole argument.**
  Blood oxygen, seizure detections, alarm history and the medical ID are the
  most medically sensitive rows in the product, and Free stores every one of
  them in the clear. Refusing them would mean refusing the emergency path,
  because they *are* the emergency path — a storage rule that declined to write
  a blood oxygen of 84 is a paywall in front of an alarm wearing a privacy
  argument as a disguise. `NEVER_GATED` exists because this codebase shipped
  that bug once already; `storage.py` does not get to reintroduce it one layer
  down. `guardian._event` is therefore left unguarded, and a test asserts it
  stays that way.

  A capture refusal reports the **missing vault (503) before the plan (402)**,
  deliberately: in a deployment with no PDI at all, telling somebody to pay $20
  for the vault would be selling what cannot be delivered there.

### Changed

- `POST /enroll` with no `plan` now lands on **Free** rather than Basic, and
  the response says what that means before anything has been written.

- **README: "No raw user data ever leaves your vault" now says on which
  plans.** It was true when every account had one; it is a claim about Basic
  and Pro, and the free plan is what it is being sold against.

## [0.4.0] — 2026-07-27

### Added

- **Membership: Basic $20/month, Pro $130/month** — `jim/tiers.py`, 4 routes,
  25 tests, screens 69 and 70. Basic is the Guardian itself — conditions,
  guidance, journal, habits, goals — and every emergency path. Pro adds the
  watch, early warning, specialists and synthetic agents.

  **Nothing that answers an emergency is ever behind a paywall**, and that is
  the rule the module exists to keep rather than a caveat on it. A lapsed card
  is a billing event; a seizure is not. `NEVER_GATED` names the alarm path,
  escalation, the medical ID a paramedic scans, incident history and the
  guidance given during an alarm — consulted **first**, so a pattern added
  later cannot reach them, and a test plants exactly that mistake and asserts
  each safety route still comes back ungated.

  **The first implementation had that bug.** `/monitor` was listed as the
  "proactive monitoring" capability, which reads correctly and is wrong:
  `/monitor` is the *ingest*. A Basic member submitting a blood oxygen of 84
  received a 402 instead of an escalation — the paywall standing between
  somebody and an emergency, indirectly but completely. The suite caught it.
  What Pro buys is `jim/earlywarning.py`, the trend model that looks *ahead* of
  a threshold, and it is **skipped rather than refused**: a Basic member gets a
  real answer about the reading they submitted, with `predictive: false` saying
  plainly what they did not get.

  Every 402 carries `emergency_unaffected: true`. Money is simulated.

- **The helper dock** — `jim/dock.py`, 5 routes, 15 tests, screen 71. The
  glances a watch face would carry, in a pane in the corner — which matters
  here because the watch is a Pro capability. **An active alarm opens it
  whatever it was set to**, and the alarm face cannot be configured out of the
  pane: this is the one place the rule deliberately departs from QRME's, whose
  dock hides itself during a broadcast. The same rule here would hide the thing
  a person most needs to see, and JIM-mini has no broadcast surface to leak an
  alarm into.

- **The Guardian gives the tour** — `jim/tutorial.py`, eleven lessons in the
  Guardian's own voice, because here the Guardian already *is* somebody to the
  user. Channel 2's screens 65 and 66 came back in the same change, found by
  the walkthrough's coverage test on its first run.


- **The Guardian gives a guided walkthrough** — `jim/tutorial.py`, 6 routes,
  11 tests. Eleven steps across four chapters, `?mode=voice` to be spoken —
  which matters more here than in QRME, because this is a product used
  hands-free by somebody who may not be well.

  **The Guardian gives it, rather than a faceless guide**, and that is the one
  place this deliberately differs from QRME's version. QRME's subject is
  synthetic people, so a guide with a persona would be the most convincing one
  on the platform. JIM-mini has exactly one voice and is not pretending to be
  anybody — a separate guide would be a *second* voice in a product built on
  there being one, and the first thing a new user learned would be that JIM
  talks to them from two places.

  **It never fires anything for you.** No lesson triggers an escalation,
  reaches an emergency contact or files a condition "to show you how" — in a
  product whose actions reach a real person's phone at three in the morning, a
  demonstration that fires for real is not a demonstration. Tests assert it,
  along with writing nothing but the learner's own progress and needing no
  model configured.

### Fixed

- **Screens 65 and 66 were missing.** The hold that pulled channel 2 before
  0.3.1 removed them, and green-lighting the feature restored QRME's screen 81
  without restoring these — so the microphone shipped with routes, tests and a
  README section, and no pictures. Found by the walkthrough's own coverage
  test on its first run, which is the argument for that test in one line.

### Changed

- **The video at the top of the README is no longer the whole header.** A bare
  user-attachments URL becomes a full-width player, which on this page meant a
  large black rectangle with a play button sitting above everything the README
  is actually about — it read as the header rather than as one thing offered in
  it. There is no width attribute to set, because GitHub generates the element;
  the only handle is the width of the box it lands in, so it now sits in a
  narrow table cell with the cover illustration beside it. Playback is
  untouched: it still opens full screen with audio, which is what a small frame
  is for.

### Added

- **Channel 2: a second microphone, for the agent** — `jim/mic.py`, 9 routes,
  34 tests. A phone has one microphone and one foreground claim on it. While
  somebody is on a call the Guardian is deaf — which is precisely when they
  might want to ask it something, and precisely when it cannot hear them ask.
  A watch already on the wrist has a microphone nothing else is using.

  **Permission and state only** — capture happens on the device; nothing in
  this module touches a sample. What the service owns is whether the agent may
  listen right now, on which device, and a record of when it did.

  Any personal microphone qualifies — watch, earbuds, headset, lapel, clip-on,
  bone-conduction, glasses. `GET /mic/types` publishes the list so a client
  offers the right one rather than guessing.

  Five refusals carry it:

  - **Only a microphone pointed at you.** The first cut of this allowed only
    `kind == "wearable"`, which was the right instinct reached by the wrong
    measure: a watch qualified and a lapel mic did not, though a lapel mic is
    aimed at one collar and a watch at a whole wrist. The axis is **who the
    microphone is pointed at** — a speakerphone or conference puck hears
    whoever is present, and those people never agreed. A stationary device is
    refused whatever microphone is in it.
  - **Not the microphone already carrying the call.** Broadening exposed a
    collision a watch never had: earbuds on a call are the *occupied*
    microphone, and lending them asks one microphone to be two channels.
  - **Only while the primary is actually occupied**, with the reason recorded.
    A second ear granted for no reason is just a second ear.
  - **Never on speakerphone.** On an earpiece the wearable hears the wearer; on
    speaker it hears **the other party too** — someone who is not a user of this
    product, was never asked, and cannot revoke anything. A microphone the
    Guardian holds must not become a way to record the person on the other end
    of somebody else's call. Likewise refused with others in earshot.
  - **A handover ends**, released explicitly or closed out with its reason, and
    every one is recorded: a listening permission that leaves no trace is one
    nobody can audit, and this is the permission people most want to check up
    on. A *refused* handover records nothing, so the history never implies the
    agent heard something it did not.

  Two bounds on what it hears, deliberately separate. **Focus** keys the
  channel on its wearer and drops the rest — background talk, a television, the
  people at the next table. It is not a setting: an option to include the
  chatter is an option to record people who never agreed, and nobody hands the
  agent a microphone in order to be told what the next table was saying.
  **Gain** is how far away that wearer can be. Focus decides what is *listened
  to*; gain decides what is *in range*, and keeping both means a failure of the
  first is still bounded by the second — which is the only reason to have a
  filter and a limit rather than a filter alone.

  Every gain level therefore describes **the user at a distance, never a level
  of company**: close to the microphone, at arm's length, from anywhere in the
  room. There is no setting whose answer to "what does it pick up" is "more
  people". `reaches_others` survives that reframing and is what the cap is
  judged on — not that others are transcribed, but that another voice is
  physically inside the pickup pattern, which is worse and is what a filter
  failure would expose.

  How wide the channel listens is not an audio-quality preference — it is
  **the mechanism** behind the sentence the product tells the user, *the agent
  hears you, not your call.* A promise enforced by a policy holds until
  somebody edits the policy; enforced by the capture width, it is a fact about
  what the microphone can pick up.

  `PUT /users/{id}/mic/gain` sets `near_field`, `normal` or `wide`, defaulting
  to the narrowest — a listening default that reaches other people is a default
  nobody chose. `GET /mic/gains` publishes the levels, `reaches_others`, and
  the focus guarantee.

  While the occupying reason is one where somebody else's voice is present
  (`voice_call`, `video_call`, `live_room`), the effective gain is **capped at
  near-field however the user has set it** — a dial that can be turned up into
  somebody else's conversation is not a safeguard, it is a suggestion. The
  adjustment is still accepted mid-call rather than refused, and takes effect
  when the call ends: refusing outright would teach people the control is
  broken, when what is happening is that the situation is temporarily narrower
  than their preference. Capped, not overwritten — the setting comes back. Each
  session records the gain it *actually ran at*, because an audit reporting the
  preference would overstate every capped call.

  The counterpart is `qrme/roommic.py`, which lends the same wearable to a live
  room's profiles — where the others *are* participants and can therefore be
  told, which is why that side discloses rather than refuses.

## [0.3.3] — 2026-07-27

**The round where a task working on its own stopped being something you had to
go and check** — and where the README stopped opening with a wall of text.

### Added

- **The agent status light, on three surfaces** — watch face 36, screens 67 and
  68, and the desktop console. Green *working*, amber *needs you*, red
  *stopped*, answering the one question a running task actually raises: does
  this need me right now? The word rides with the colour, because green alone
  cannot separate a task that is still going from one that has finished.

  **Watch face 36 is the ambient one** — three lights, three counts, dimmed at
  zero, and **no task names**. This is the surface that works while somebody is
  on their phone, and naming the tasks was the first cut and was wrong: a name
  is something you read, and reading is the thing a glance cannot do. The
  footer says *open on your phone*, because that is where the answer lives.

  **Screen 67** folds every task into one tappable group per light, so somebody
  opening it *because* amber appeared is not scanning a flat list for the one
  that changed. **The overlay** rides over an ordinary screen and over every
  desktop view — a task that reports only on its own screen is one you have to
  remember to check, and amber and red are exactly the states nobody thinks to
  look for. Shaped like the watch face rather than as a bar across the screen:
  a small translucent box in the corner, three stacked rows, each its own tap
  target.

  Screens 65 and 66 stay unused so held work keeps its numbers. The mapping
  lives once, in QRME's `agentlight.py`, for all three products.

### Changed

- **The README leads with the screens instead of with prose.** Everything you
  can look at is now above everything you have to read, and the run/config/API
  material is gathered under one **Reference** heading at the bottom — so a
  command spotted in a screenshot has one place to go and look it up. Those
  tables are set smaller, since they are for looking things up in rather than
  reading through.

## [0.3.2] — 2026-07-27

There are no functional changes to JIM-mini in this release — no new routes,
no schema, no behaviour. The version moves because the three products are
cut as one release, and a number naming one combination of three is only
useful if it never skips one.

### What changed in the siblings

- QRME's starter gallery now shows each of the 34 profiles as the card the app actually gives it, and the one starter that had no source material finally has a Field Pack of its own.

## [0.3.1] — 2026-07-26

**A documentation round for JIM-mini.** There are no functional changes to
JIM-mini in this release — no new routes, no schema, no behaviour. What changed
is that the README now says which version you are looking at, and four screens
that shipped in 0.3.0 became findable.

### Changed

- **The README names its release, and says what each one added.** It opened on
  a video and a patent notice and never stated a version, so a reader could not
  tell which release they were looking at or what had happened across thirteen
  of them. The changelog had it all; the changelog is not where somebody lands.
  The same section went into all three repositories, because the three are cut
  as one release and a reader arriving at any of them should be able to answer
  that question the same way.

### Fixed

- **Screens 61–64 existed in the repository and nowhere a reader would find
  them.** They shipped in 0.3.0 as files — *What Would Be Shared*, *Specialist
  Working*, *Find a Clinician*, *Sign to Release* — and were never added to the
  README gallery, so the four screens illustrating that round's headline feature
  were invisible on the page describing it.

## [0.3.0] — 2026-07-26

**The round where the tandem reaches a person.** The Guardian could delegate a
condition to a synthetic specialist; now it can hand over a task that outlives
the app being closed, and find a real clinician near the user. Plus the
settings screen finally keeps the promise it has been making about
contribution.

### Added

- **Reaching a real clinician** — `jim/referral.py`, 4 routes, 11 tests. The
  tandem could hand a condition to a synthetic specialist and (this round) a
  multi-step task. Neither reaches a human being. This maps a condition to a
  care area, finds real clinicians near the user, and asks QRME to assemble
  the summary and raise the signature that would release it.

  **JIM never holds the credential and never relays the assertion.** The
  signature is a WebAuthn assertion against *QRME's* relying party, over a
  challenge QRME minted, so the Face ID prompt belongs to QRME and the
  assertion travels from the user's device to QRME directly. A guardian
  product that could mint the consent for releasing its own user's health
  record would be exactly the wrong shape, and standing in the middle of the
  one exchange that proves the user was present would defeat the point of
  collecting it. JIM stores a handle — not the summary, the signature, or the
  link. A test asserts the transcript never reaches JIM's database.

  **Locality is a town, not a position.** `sources` already carries a
  consented `location` feed and this deliberately does not read it: live
  position is a stream, and matching a clinic needs a place name. Typing
  "Leeds" once is a smaller disclosure than a product inferring it
  continuously — and it is all the match can use anyway.

  Condition→area routing is coarse on purpose (`anxiety` → `mental_health`,
  everything unmapped → `medical`); anything finer would be JIM guessing at a
  clinical taxonomy it has no standing to define. Standalone JIM, an
  unregistered area, and a missing tandem link each answer plainly with a
  reason rather than raising — the caller is often a screen somebody opened
  while unwell.

- **Contribution preview and revoke** — `jim/contribution.py`, 2 routes, 11
  tests. The settings screen has offered *"Contribute data — preview before it
  leaves"* since the cloud tier shipped. **The API could do neither half.**
  `cloud.contribute` posted a payload, returned a bool, and wrote nothing
  down, so there was nothing to preview, and consent described as *revocable*
  meant only *stoppable* — turning the flag off prevented future sends while
  everything already contributed stayed at the gateway with nothing naming it.

  **One payload builder, used by both paths.** The preview calls the same
  function the real send calls, rather than reconstructing something that
  looks like it. A preview assembled separately is a *description* of the
  payload, and descriptions drift from what they describe — which is exactly
  the failure this endpoint exists to correct.

  A failed post is **not** logged: recording it would offer a revoke button
  for data that never left. On revoke, local rows are marked whether or not
  the gateway answered, and the response says which happened separately —
  leaving them unmarked on an outage would show a user their data as still
  shared after they revoked it, and marking them regardless would claim a
  deletion that never happened.

  What leaves is unchanged: condition domain, severity, rating. Never ids,
  names, notes, or raw biometrics. Contributions now carry a random `ref` so
  an item can be deleted at the gateway without deanonymizing the person
  revoking it.

- **Handing a specialist a task, not a turn** — `jim/handoff.py`, 4 routes, 12
  tests. `_tandem_guidance` sends one message and gets one reply. That is the
  right shape for *"say something supportive"* and the wrong one for *"read
  what we have, draft the summary, hold it until somebody confirms"*. QRME
  runs the second as a workflow; this is JIM's side of it.

  **Never on the emergency path.** `escalation.decide` resolves in one call and
  must keep doing so — multi-step work is by definition slower than the thing
  it would block. Nothing here is reachable from `monitor`.

  **Starting one is explicit.** Having a detection kick off a workflow by
  itself reads well and is the wrong default: it would let a noisy reading
  commit a specialist to unattended multi-phase work over the user's vaulted
  material.

  JIM keeps the task's **status only**. The drafts stay in QRME under its own
  moderation and the user's capability token; mirroring them here would quietly
  make JIM a second store of somebody's generated health correspondence. A
  narrower owner policy narrows the plan rather than failing it — but an empty
  intersection is a refusal, because a workflow with no phases completes
  instantly and reads as success.

### Screens

- **61 · What Would Be Shared** — the screen behind that settings row. Every
  line is a real field of the payload rather than a description of one.
- **62 · Specialist Working** — a handed-off task mid-flight, showing where it
  has got to and what it is waiting on.

## [0.2.2] — 2026-07-26

**A documentation release.** No code changed in any of the three products — no
new routes, no schema, no behaviour. Every entry below corrects something that
was *described* wrongly, which on this round turned out to be the thing costing
real time. The round started next door in QRME, whose seed endpoint was
advertising the opposite of what it did; the release checklist turned out to be
wrong here too, in the same way, so all three were fixed in one pass.

### Fixed

- **Changelog release links stopped at 0.1.8.** `[0.1.9]`, `[0.2.0]` and
  `[0.2.1]` had headings but no link definition, so three shipped versions
  rendered as literal `[0.2.1]` text instead of linking to their releases, and
  `[Unreleased]` still compared against `app-v0.1.8` — presenting a
  three-release diff as though it were an empty one.

- **The release checklist is why it kept happening.** `docs/releasing.md` step 1
  said to move the `Unreleased` items and date the heading, and never mentioned
  the link definition at the bottom of the file — so the step was skipped three
  releases running by someone following the instructions correctly. Step 2 was
  wrong in the same direction: it named `pyproject.toml` and `app/package.json`
  when the version string actually lives in **five** places, the two extra ones
  being the `FastAPI(...)` call and the second root entry in the lockfile.
  Both steps now say what they meant.

## [0.2.1] — 2026-07-26

### Added

- **How much to trust a reading** — `jim/signal.py`, 15 tests. The last
  standing gap: the Guardian assumed clean input. `escalation.decide` has
  always accepted a `confidence`, but only forecasts ever supplied one, so it
  gated *predictions* and never *measurements* — a reading was a fact by virtue
  of arriving.

  Consumer biometrics are not like that. An optical sensor loses skin contact,
  a chest strap catches a motion artifact, and the characteristic failure is
  not a small error but a plausible-looking number that is completely wrong,
  with the alarming direction as likely as the reassuring one. At the top of
  this ladder is a phone call to somebody's daughter, and an alert that is
  usually wrong spends the only thing escalation has: her willingness to pick
  up.

  **Confidence drops only on evidence the *sensor* misbehaved** — an
  impossible value, a jump no body could make between two readings, or the
  device reporting its own poor contact. Being clinically abnormal never
  lowers it. That distinction is the whole design, and it was learned the hard
  way: the first draft graded anything outside the ordinary range as suspect,
  which muted a lone SpO2 of 84 — the exact reading the ladder exists to carry.
  A regression test caught it.

  **A poor grade caps rather than silences.** Escalation stops at `check_in`:
  *"we got an odd reading, are you alright?"* is the honest sentence when the
  honest answer is that we do not know, and asking is also how the reading gets
  corroborated. Dropping the sample would be the same mistake pointed the other
  way — the noisy reading is sometimes real.

  **Words are never noise.** The crisis floor is applied after the cap and is
  never clipped by it. Nor can words make a heart rate of zero true: two
  impossible readings are not two witnesses but one broken device agreeing with
  itself, so corroboration only runs between *possible* readings. A fault is
  phrased as a fault — *check the strap* — because telling somebody whose
  sensor fell off that we are worried about them is how people learn to
  disbelieve the thing.

  A baseline is the one place a reading is dropped outright: it is a long-lived
  average of what normal looks like, so it takes only ordinary values. A
  merely-possible 195bpm is a real event worth detecting and a terrible thing
  to average into "resting".

### Fixed

- **The escalation decision was advisory; raw severity was in charge.**
  `monitor` reached out whenever `detection.severity == "critical"`, so the
  decision tree could resolve a disbelieved reading to `check_in` and the
  emergency contact was rung anyway. The tree is authoritative now. No
  behaviour changes for a trusted critical — its floor is `notify_contact`, so
  the comparison is exactly equivalent — and a test asserts that directly.

## [0.2.0] — 2026-07-25

### Fixed

- **Two workflows were writing the release body, and only one of them was
  right.** `desktop-release.yml` published the release with
  `body_path: RELEASE_NOTES.md` — the file verbatim, *"Ready-to-paste body for
  the GitHub Release…"* preamble and all — while `sync-release-notes.yml`
  published the same file with that preamble stripped. Both fired on the same
  tag push. The sync finished in about six seconds; the installer build
  finished two to four minutes later and overwrote it.

  So the build always won, and every release since the sync workflow existed
  has shipped the maintainer preamble at the top of its notes until somebody
  re-ran the sync by hand. The de-duplication logic already in the sync
  workflow — *"several releases carry it twice from a body that was pasted over
  one that already had it"* — was scar tissue from this, treating the symptom.

  The build step no longer sets a body at all; it attaches installers and lets
  GitHub generate the changelog. `sync-release-notes` now triggers on
  `workflow_run` when that workflow **completes**, rather than on the tag push,
  so the curated notes are the last write by construction instead of by luck.
  It runs on a failed build too — a build that fails after creating the release
  is exactly when a wrong body is least likely to be noticed.

  [docs/releasing.md](docs/releasing.md) says to leave the release body empty
  and records who owns it, along with the other trap in this area: tag names
  are case-sensitive to `tags: ["app-v*"]`, so `App-v0.1.9` silently triggers
  nothing.

## [0.1.9] — 2026-07-25

### Added

- **A rota, and an escalation that actually sends something** —
  `jim/rota.py`, `jim/notify.py`, 4 routes, 24 tests. Two gaps that were both
  documented as deliberate, and one of them was not defensible.

  **`JIM_SITE_ROSTER` was a flat list worked top to bottom, every time**, and
  `relay.py`'s own comment defended that: *a rota with shift patterns is a
  scheduling product and pretending otherwise would hide how little this
  knows*. That was honest but wrong about the size of the gap. The relay exists
  for **night shift** — lone workers, plant rooms, single-staffed sites — and a
  flat list pages the day person at 2am. The feature failing in the hour it was
  built for.

  So: `JIM_SITE_ROTA`, deliberately small. Named people, the days they work,
  the hours, and `JIM_SITE_TZ`. No leave, no swaps, no fairness, no recurrence
  grammar. Three things it does get right, because each is a way of paging the
  wrong person:

  - **Shifts cross midnight.** `18:00–06:00` is the shift this is all about,
    and `start <= now <= end` is false for every minute of it. A wrapping shift
    is two intervals and belongs to the day it *started*: at 02:00 on Saturday
    it is Friday's night worker on the floor, not the weekend rota.
  - **A site is somewhere.** Without a timezone a rota written in local time is
    evaluated in UTC, shifting every boundary by the offset — and by a
    *different* offset in summer, so it would look correct for half the year.
    An unrecognised zone is named in `GET /relay/roster`'s `warning` rather
    than silently treated as UTC.
  - **A rota has gaps.** Nobody rostered at 4am on a bank holiday is a real
    state. The relay works the whole rota — better to wake the wrong person
    than nobody — and reports `on_shift: false` on the escalation *and in the
    page itself*, so whoever it wakes knows they were a guess.

  `GET /relay/rota` answers *who would you page right now?* in the afternoon
  rather than leaving it to be discovered at 3am. `JIM_SITE_ROSTER` still works
  and still means plain names, always on — a test asserts the old
  configuration is unchanged.

  **And `escalate` sent nothing.** "Notified" meant a row in `events` saying
  somebody had been notified, while nothing had left the building — so the
  loop the relay is built around (*keep going until a human accepts*) could
  never close on its first step. JIM now posts a signed envelope to
  `JIM_NOTIFY_URL` and stops; the SMS gateway or pager behind it is the
  deployment's, and the envelope matches PDI's shape so one receiver can take
  both. An unreachable responder sets `reached_somebody: false` **and**
  `escalate_again_now`, because *waiting on a human* and *waiting on a human
  who was never told* need different next moves and only the first should wait.

  **Incident scope survives the trip out of the building.** A webhook is the
  easiest place in the system to turn an incident into a health record — "just
  add the name so they know who to look for" is a reasonable-sounding sentence
  that would undo the whole promise. So the envelope is built by copying named
  fields *out* of `relay.incident`, never by stripping fields from a user
  record, and not even the finder's words go out. A test reads the whole
  envelope as one string and looks for the name, birthdate, contact number,
  resting rate and the finder's message in it.

  The ceiling did not move: a notification channel is not a siren, and a test
  runs the roster to exhaustion to prove `notify_contact` still caps it.

  **Screen 60 was advertising the feature this replaced.** *"Roster in order ·
  night-tech → supervisor → lead"* is the flat list, drawn last round and still
  in the README gallery. It reads *On shift, not in order · 18:00–06:00 ·
  Friday's night* now, and the card next to it names the page rather than the
  note in a table. Rendered and checked; `clock` is not in this repo's icon set
  and would have drawn a bare dot, so it uses `watch`.

  **A config typo cannot take the escalation path down.** `RotaError`'s own
  docstring claimed it was *"raised at load, never at 3am"* — but nothing reads
  the rota at start-up, so it was raised at exactly 3am: one typo (`"funday"`
  for `"sunday"`) propagated out of `relay.roster()` and turned
  `POST …/escalate` into a 500, on the one path whose entire job is getting
  somebody help, and only once an alarm was already open. `rota.read()` never
  raises; the rota is ignored, the flat names take over, and somebody is still
  woken. The error is reported as `warning` on `GET /relay/roster` and
  `rota_error` on every escalation, while `GET /relay/rota` stays strict —
  degrading on the surface an operator uses to *check* their rota would hide
  the thing they came to find.

- **The tandem doc describes the architecture that actually exists** —
  [docs/tandem.md](docs/tandem.md), identical byte-for-byte in all three
  repositories. This copy was twelve lines and four `[planned]` markers behind
  QRME's: it described the suite gateway's erase, export, consent and metering
  as intentions when `suite/gateway.py` had shipped them, and the
  docker-compose e2e harness as planned when it runs in CI. A reader in this
  repo was told cross-app deletion did not exist.

  New sections for the arrow that runs out of PDI into QRME, for the beacon
  family across all three products, and for the notification channel — the one
  thing the suite genuinely cannot supply for itself.

- **The diagram is generated** — `tools/build_assets.py` writes
  `docs/diagrams/tandem-flow.svg`, from a block identical in all three repos so
  one picture cannot become three that disagree.

  The vault arrows name **what actually goes down them**. *"Medical payloads"*
  was true and incomplete: spending events, bank transactions, messages and
  location all ride the same wire, under the same consent gate, into the same
  `jim/{user}/context/…` namespace. A diagram — or a doc — naming only the
  medical half invites the reader to assume the rest is held somewhere else,
  and it is not. All four categories a person would be startled to find there
  now sit on the label's bold line together; putting two of them a row down in
  a smaller font would have re-made the same mistake more quietly. The QRME
  arrow got the same treatment, having been summarised to *"source material"*
  while also carrying rated placement earnings and adaptation runs.

- **A phone that scans a care beacon gets a page now** — `jim/landing.py`.
  `GET /c/{id}` served JSON, so a neighbour scanning a fridge magnet got a wall
  of braces; the JSON moved to `/c/{id}/card` and the scan URL serves HTML.

  Stage one is the whole page: a first name, one sentence, and a button — and
  the instruction to dial sits *above* the button in the document, because the
  one mistake that matters is somebody waiting for a page instead of calling.

  **The Medical ID is not in the served HTML at all.** It arrives in the
  alarm's own response and is rendered in place, so there is nothing on the
  page to reveal early even by mistake; a test asserts the name, resting rate,
  conditions and contact number are absent from stage one. For a minor the
  server returns `medical_id: None` and the page renders only what it is
  handed, so stage two simply never appears.

  One self-contained document, inline everything, alarm posting to a
  **relative** URL — somebody may be reading it kneeling next to a person on
  the floor, and an absolute URL from `JIM_PUBLIC_URL` breaks every LAN scan.
  The entrance animation moves `transform` only and honours
  `prefers-reduced-motion`, so a browser that drops it still shows the page
  rather than a blank card.

- **Care beacons and the workplace relay are built** — `jim/beacons.py`,
  `jim/relay.py`, 13 routes, 25 tests. A printed QR goes on the things around a
  watched person — a fridge door, a wristband, a walker — and a stranger who
  finds it can raise whoever is watching.

  **The alarm comes before the disclosure.** Stage one is a first name, one
  sentence and a button; raising the alarm is the act that turns a passer-by
  into a responder, and that is what earns them the Medical ID. The order is
  QRME's desk beacon in reverse, because health is not a shop sign — and the
  gate is affordable precisely because the ungated path already ships on the
  person's own body, which is what `/medical-id/{token}` is for.

  **A beacon reports watch status, never subject status.** No health state, no
  location, ever: *is this person OK right now* is precisely the question a
  stalker is asking. Tested by serializing the whole card and searching it for
  the birthdate, the contact number, the label and the placement note, rather
  than by checking the handful of fields somebody remembered to omit.

  **`notify_contact` is now a ceiling as well as a floor.** `escalation.decide`
  gained a `ceiling` argument — the first rule in that module that *lowers* a
  tier, and it only ever applies to a caller who is not the user. A `critical`
  severity bases at `emergency_services`, so the ceiling is what stands between
  an anonymous tap and a dispatch; when it clips a floor it says so
  (`clipped_by_ceiling`, `call_emergency_services_yourself`) rather than quietly
  returning something lower. Existing callers pass no ceiling and are unchanged,
  which a regression test pins across every severity and sensitivity.

  **The cooldown coalesces rather than drops** — a second finder's words join
  the open alarm, because two people finding the same casualty is the case the
  feature exists for. And **a minor's beacon never opens the clinical stage**,
  to anyone; it is guardian-issued and routes to the guardian.

  For **lone and remote workers**, a site relay: it works the roster in order,
  distinguishes *accepted* (somebody is coming) from *cleared* (it is over),
  refuses an anonymous acceptance, and reports an exhausted roster rather than
  going quiet — still without dispatching. Incidents are built from the alarm,
  not the person, so the payload carries no name, condition or history.

  Two screens (59 Care Beacons, 60 Workplace Relay).

### Changed

- **The four README illustrations are generated now**
  (`tools/build_assets.py`) rather than hand-built. They had been drawn before
  the escalation ceiling, care beacons, the workplace relay, the family
  oversight tiers and the rated robot first-aid roles existed, and were still
  showing an early product several releases later.

  They now read their palette from the same constants `docs/screens/build.py`
  uses, so they cannot drift away from what they are pictures of. The cover
  draws the escalation ladder as a ladder — with the `notify_contact` ceiling
  annotated on the rung it caps — and the tandem diagram states the line that
  matters most: crisis handling never routes through a synthetic profile.
  Regenerate with `python3 tools/build_assets.py`.

### Fixed

- **Nine screens had text running outside their cards**, found while checking
  the two new ones by rendering them rather than trusting the SVG to parse.
  Four subtitles overflowed the card edge and five titles collided with their
  own pill — worst on *Parent Setup*, where "cautious sensitivity · parent is
  the emergency contact" ran well past the phone frame. Also `icon="lock"`,
  used on that screen, is not in this repo's icon set at all and had been
  rendering as a bare dot; it is now `clip`, and a check confirms every icon
  named by a screen exists.

## [0.1.8] — 2026-07-25

### Fixed

- **`[0.1.5]` and `[0.1.6]` linked to releases that do not exist.** Both
  versions were cut — changelog, notes, version bumps — but their `app-v*` tags
  were never pushed, so those two entries pointed at 404s. They now point at
  their release-prep commits. Deliberately **not** fixed by backfilling the
  tags: pushing them now would fire the installer build and publish v0.1.5 and
  v0.1.6 releases *dated after* v0.1.7, putting superseded installers at the top
  of the page people download from. [docs/releasing.md](docs/releasing.md)
  records that reasoning.

### Changed

- **There are no functional changes to JIM-mini in this release.** No API, no
  schema, no behaviour moved. The substance at 0.1.8 is QRME's: a live
  desk stops being only something you watch — you can ask to come up on the
  stream, and the room's reactions render on the picture rather than beside it.
  Nothing in it asked JIM-mini to change.

## [0.1.7] — 2026-07-25

### Changed

- **The three products are now cut as one release** — documented in
  [docs/releasing.md](docs/releasing.md), and in QRME's and PDI's copies of the
  same file. Same number, same pass, even when a repository has nothing of its own
  to ship that round; an empty round says so in those words rather than being
  padded. Through v0.1.5 each repository cut whenever it happened to have work,
  so the numbers matched only by coincidence — which is how QRME reached 0.1.6
  alone while this one sat at 0.1.5. The doc also writes down the trap that
  follows: tag the release-prep commit rather than the tip of `main`, because
  work keeps landing while a release is cut and anything arriving after the
  changelog is sectioned belongs to `[Unreleased]`, not to the version being
  tagged.

## [0.1.6] — 2026-07-25

### Changed

- **Version aligned across the suite.** QRME, JIM-mini and PDI are built to run
  in tandem, but their version numbers drifted apart whenever a round of work
  landed in one repository and not the others — QRME reached 0.1.6 on its own
  while this one stayed at 0.1.5. From here the three carry the same number, so
  "the suite at 0.1.6" names one combination of three products rather than
  three that merely happen to be nearby. Anyone pinning all three can pin one
  number.

  **There are no functional changes to JIM-mini in this release.** Everything
  the Guardian does at 0.1.6 it did at 0.1.5: no API, schema, or app behaviour
  moved. The work that earned 0.1.6 is QRME's — AI marks burned into portrait
  pixels, live desks, and WebAuthn signing on Windows — and none of it reaches
  across into this repository. The number is the only thing that changed here,
  and saying so plainly is worth more than padding the entry.

## [0.1.5] — 2026-07-25

### Added

- **The native apps are compiled in CI** (`.github/workflows/native.yml`) —
  iOS via XcodeGen + `xcodebuild` on macOS, Android via `gradle assembleDebug`,
  Windows via MSBuild. The Swift, Kotlin and C# had never been through a
  compiler in this repository: they were checked by reading and by brace/XML
  well-formedness, which catches a typo and nothing else. Ported from QRME,
  where the same gate found five real defects. Compile only — signing and
  packaging stay in the release workflow — and it runs only when `native/`
  changes, since macOS runner minutes are not free.
- **Published deployments** — `JIM_PUBLIC_URL` makes `GET /pair` advertise
  the deployment's public address (QR included) instead of a LAN address, so
  the phone flow works hosted or local from one code path. `JIM_SIGNUP_KEY`
  gates enrollment behind an `x-signup-key` header so a published instance
  stays the operator's rather than open registration; unset leaves LAN use
  exactly as it was, and the gate never blocks an enrolled user or a parent
  adding a child under their own token.
- **Deployable as one container** — a two-stage `Dockerfile` builds the console
  and installs the API into a single image, so a hosted instance serves UI and
  API from one origin exactly as the phone flow does. Runs as a non-root user,
  keeps the database on a `/data` volume, honours `$PORT`, and reports health
  at `/health`. [docs/hosting.md](docs/hosting.md) covers the operator side:
  the two postures (local vs published), why TLS isn't optional here (tokens
  in headers, and browsers refuse geolocation without it — so escalation needs
  it), what holding someone else's health data commits you to including the
  HIPAA/BAA question, and plainly what the deployment does *not* give you (no
  multi-tenancy, rate limiting, backups, or uptime guarantee).

### Fixed

- **The iOS project spec was invalid** — its XcodeGen `info:` block had no
  `path` (required), while also setting `GENERATE_INFOPLIST_FILE`, which is
  mutually exclusive with it. `xcodegen generate` failed outright, so the
  Xcode project could never have been produced. The plist is now written from
  the spec, which also means the local-networking exemption the Simulator
  needs to reach `http://127.0.0.1:8000` actually applies.
- **Windows: the journal list would not compile.** `entries` is a
  `JournalItem[]`, and an array converts implicitly to `Span<T>`, so
  `.Reverse()` bound to `MemoryExtensions`' in-place **void** overload rather
  than LINQ's — leaving the following `.Select` attached to nothing.

## [0.1.4] — 2026-07-24

### Added

- **`python -m jim` launcher** — bare invocation prints the menu of every
  way to run the Guardian, one command each, so users choose their device:
  `phone` (builds the console if missing — npm install included on first
  run — prints the pairing URL with a scannable QR drawn straight into
  the terminal, serves on the local network; flags `--port`, `--rebuild`,
  `--no-build`, `--print-only`), `desktop` (the Electron app on this PC,
  or a pointer to the packaged installers when npm is absent), and
  `serve` (the headless API alone, `--host`/`--port`). Same backend,
  data, and token checks in every form.

## [0.1.3] — 2026-07-24

### Added

- **Run it on your phone** — the API serves the built console at `/app`, so a
  phone on the same Wi-Fi opens the Guardian with nothing to configure (one
  origin for UI and API, so no CORS and no "which host?" step). `GET /pair`
  resolves this machine's local-network address and returns the URL to open —
  with `GET /pair/qr.svg` as a scannable QR and a pairing card in the Privacy
  screen. Installable as a PWA (manifest, icon, standalone display, app-shell
  service worker that never caches API traffic), with a phone layout: the
  sidebar becomes a bottom tab bar, 16px inputs so iOS doesn't zoom, and
  safe-area insets for the notch and home indicator.

## [0.1.2] — 2026-07-24

### Added

- **Terms of Service** — docs/terms.md (v1.0: not a medical device, call
  911 first, assumption of risk and release, robot-resuscitation boundary,
  warranty disclaimer, liability cap) served versioned at `GET /terms`;
  enrollment records the accepted version and timestamp on the account,
  and the native welcome screens carry the clickwrap notice.
- **macOS notarization wiring** — hardened runtime + entitlements +
  `notarize` in the electron-builder config; docs/releasing.md walks
  through obtaining the macOS and Windows certificates.
- docs/hipaa-baa.md now points at the signable BAA template maintained in
  the PDI repo (docs/baa-template.md there).

## [0.1.1] — 2026-07-24

### Added

- **First-run onboarding screens** — provider login (Apple / Google / email),
  permissions, "about you", emergency contacts, and an "all set" confirmation,
  in iOS and Android chrome.
- **Native iOS / Android / Windows apps at parity** — Care (Monitor, Check-in,
  Coach, Family), Life (goals/habits/journal), Safety (SOS, escalation policy,
  robots, Medical ID card), Connect (sources, social, apps), Vault Custody,
  and the model picker — a 5-item nav with everything reachable.
- **Robots as guardian responders** — catalog binding, escalation directives,
  and **first-aid rated roles**: assist-rated platforms fetch the AED and
  coach the playbook; perform-rated may deliver compressions only after
  on-scene confirmation. **Autonomous resuscitation stays locked behind a
  signed liability waiver** — and can never be signed for a minor.
- **Predictive early warning**, the escalation decision tree, and the
  one-tap Emergency flow (services, location, family, Medical ID, AI first
  aid, all devices).
- **Family** — a parent enrolls and watches over a child's account: recorded
  consent (PDI-sealed when a vault is configured), age-scaled oversight that
  ends at 18, pause/quiet-hours that never hold safety, and the parent's
  wrist face — one light per child.
- **Provable custody** — tandem specialist exchanges sealed in the PDI vault,
  a custody viewer with provenance, and the native custody screen; the
  mental-health trio routes through live QRME personas with crisis
  escalation guaranteed local.
- **Language & provenance** — per-user language with hand-translated safety
  content in all supported languages, gateway language choice,
  translate-anything, and verifiable guidance provenance with published
  sources; **LLM provider choice** per user.
- **Starter specialists** — a named domain expert per condition, seeded on
  deploy, wired to QRME starter profiles in tandem.
- In-app **"Help us improve" feedback** (`POST`/`GET /improve`) and **chrome
  localization** — the apps' own tab/nav labels in all 10 languages — plus
  pull-to-refresh across the main screens.

## [0.1.0] — 2026-07-21

First public release. JIM-mini (Guardian) is the personal-guidance product of
the three-product suite (with
[qrme](https://github.com/davidsbianchi1984/qrme) and
[pdi](https://github.com/davidsbianchi1984/pdi)).

### Added

- **Monitor → predict → guide → escalate** — ingest biometric & contextual
  signals (`/monitor`, `/context`), build a personal baseline, detect known
  conditions before threshold, deliver guidance, and escalate to an emergency
  contact / live help on critical events (`/emergency`).
- **Tunable sensitivity** — per-user crisis-detection sensitivity
  (`PUT /sensitivity/{user}`) and confidence-scored handling of noisy signals.
- **Life layer** — consented data sources, mood/energy check-ins, smart goals,
  habit streaks (`/habits/{user}/{habit}/log`), proactive insights, journaling,
  and a 24/7 coach across six life areas.
- **Medical ID** — shareable, QR-linked medical identity for responders.
- **Provider handoff** — consent-gated, revocable packaging of context to a
  care provider.
- **Tandem with QRME** — delegates specialist guidance to QRME profiles over
  HTTP, with a standalone fallback so the user is never left without help.
- **PDI vault** — seals medical and context payloads in the encrypted vault;
  `GET /access-log/{user}` shows the user every access to their own records.
- **Data ownership** — `DELETE /data/{user}` erases every local table and
  purges the user's vault records; the user token dies with the data. Per-user
  bearer tokens stored only as SHA-256 hashes.
- **Apps** — a runnable React + Vite + Electron guardian console and mobile
  screen designs; CI that smoke-builds the console and a per-OS installer
  release workflow.

[Unreleased]: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.14.5...HEAD
[0.14.5]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.14.5
[0.14.4]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.14.4
[0.14.3]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.14.3
[0.14.2]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.14.2
[0.14.1]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.14.1
[0.14.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.14.0
[0.13.1]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.13.1
[0.13.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.13.0
[0.12.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.12.0
[0.11.1]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.11.1
[0.11.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.11.0
[0.10.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.10.0
[0.9.1]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.9.1
[0.9.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.9.0
[0.8.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.8.0
[0.7.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.7.0
[0.6.1]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.6.1
[0.6.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.6.0
[0.5.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.5.0
[0.4.8]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.4.8
[0.4.7]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.4.7
[0.4.6]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.4.6
[0.4.5]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.4.5
[0.4.4]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.4.4
[0.4.3]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.4.3
[0.4.2]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.4.2
[0.4.1]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.4.1
[0.4.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.4.0
[0.3.3]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.3.3
[0.3.2]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.3.2
[0.3.1]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.3.1
[0.3.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.3.0
[0.2.2]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.2.2
[0.2.1]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.2.1
[0.2.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.2.0
[0.1.9]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.1.9
[0.1.8]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.1.8
[0.1.7]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.1.7
[0.1.6]: https://github.com/davidsbianchi1984/jim-mini/commit/a930bcf
[0.1.5]: https://github.com/davidsbianchi1984/jim-mini/commit/c80c227
[0.1.4]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.1.4
[0.1.3]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.1.3
[0.1.2]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.1.2
[0.1.1]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.1.1
[0.1.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.1.0
