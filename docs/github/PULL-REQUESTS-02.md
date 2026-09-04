# jim-mini — pull requests

Every pull request opened against <https://github.com/davidsbianchi1984/jim-mini>, newest first, with the body as written. The body is the argument for the change; git keeps the diff but not the argument.

**279 pull requests, 277 merged.**

This is one part of a page GitHub is too long to render whole — see [PULL-REQUESTS.md](PULL-REQUESTS.md) for the rest.

**#157 to #1.**

## #157 — OAuth doors, pace cue + budgets, companion relay + knowledge pack, the attach bracket, and two more model doors

- merged · opened 2026-07-29 · merged 2026-07-30
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/157>

> The pre-publish sweep round plus the specialist/provider round, JIM side.
>
> ## What's here (by commit)
>
> **Sign in with Google / Apple, the Guardian's way** — the provider vouches for the inbox, never the consent questions: signing *up* still carries the full enrollment (parked on the flow's state), a returning account signs straight in. Buttons light only when `JIM_GOOGLE_CLIENT_ID`/`JIM_APPLE_CLIENT_ID` and friends are configured; an unconfigured door is grey with its setup note.
>
> **The pace cue reaches the screen, and spending gets a plan** — the CPR playbook's promised visual/audible pace is rendered: first-aid steps on Monitor, a metronome flashing green at the playbook's 110/min with an audible tick, 30:2 called out, red when stopped. Budgets: monthly limits per category and overall (`PUT /budgets/{user}`), consented spending consumes them (amount/category/month only — the story stays vaulted), 80% and past-the-plan insights with days left.
>
> **The companion splits in two, and the assistant learns to answer offline** — at the top escalation tier the companion guides the hands on scene (vibration per compression beat, PUSH on the light, 2 BREATHS every thirtieth) while relaying a dispatcher-ready briefing in the background (who, known conditions, critical meds, latest vitals, what's being done) — honest that an app cannot itself place a voice call. Plus the **offline knowledge pack**: fifteen curated, referenced entries across the six areas and the sensor-borne conditions, answering when no model key is configured — silent rather than wrong-topic. Logo lands as-is atop the README; `docs/showcase.html` is the share page. Stress joins the check-in (optional 1–5, averaged in the report, climbing forecasts point at box breathing).
>
> **The attach bracket, and two more doors on the model menu** — Care Team gains a Specialists card: every condition beside who holds it today, stocked from the QRME Starter Collection (each starter already carries its industry's knowledge pack profile-side); one click attaches in tandem mode. `GET /specialists/catalog` serves it — 409 pointing at `JIM_QRME_URL` when standalone, an empty shelf when QRME's marketplace is down. And the model menu grows **DeepSeek** (`JIM_DEEPSEEK_API_KEY`/`DEEPSEEK_API_KEY`) and **Your own algorithm** (`JIM_CUSTOM_LLM_URL` + `JIM_CUSTOM_LLM_KEY`, OpenAI dialect) — the custom tile stays dark until its URL is set.
>
> ## Tests
>
> New: `test_oauth.py` (3), stress + budgets in `test_life.py`, companion briefing in `test_escalation_tree.py`, `test_knowledge.py` (3), `test_specialist_catalog.py` (4), provider doors in `test_model_choice.py` (2). Console builds green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #156 — Stress joins the check-in

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/156>

> From the transcript re-audit: the field video promises "track your mood **and stress levels** over time", and stress had no field anywhere in the product. The one genuinely missing promise, now built:
>
> - **Check-ins carry an optional stress reading** (1 calm – 5 overwhelmed) beside mood and energy — `CheckIn.stress`, stored on the row, returned in the result.
> - **The progress report averages it** (`checkins.avg_stress`), next to mood and energy.
> - **Climbing stress speaks up**: three strictly rising readings ending ≥4 produce a forecast insight that points at a concrete strategy — two minutes of box breathing in Wellness, and the mental-health coach — mirroring the sliding-mood forecast.
> - **Databases migrate themselves**: `db.connect()` gains an add-column migration list (`_NEW_COLUMNS`), verified against a pre-stress DB — the column arrives on first launch, old rows read `stress=None`, and a stress-less check-in stays exactly what it was.
> - Console: stress slider on the Check-in screen; on phones the help fab rides above the tab bar instead of covering the right-most tabs (same fix as QRME's).
>
> Tests: `test_stress_rides_the_checkin_and_climbing_stress_speaks_up`, `test_a_stressless_checkin_stays_exactly_what_it_was`. Full suite 664 green; console build green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #155 — Cut 0.15.0 — guided wellness

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/155>

> Release cut for **0.15.0**, in train with qrme and pdi. JIM's content this round is the guided-wellness feature set merged in #154: calm protocols, workout plans, meal plans, the nutrition Coach area and the Wellness tab.
>
> - CHANGELOG heading over the existing [Unreleased] story, RELEASE_NOTES.md, README current-release line and table row, five version strings.
> - Tag `app-v0.15.0` on the squash commit; release body stays empty for sync-release-notes.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #154 — Guided wellness: calm protocols, workout plans, meal plans

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/154>

> The transcript-mining round, JIM half — the field's promises ("quick mindfulness sessions, deep breathing, longer meditations… a ten-minute session or a full workout adapted to your level… personalized meal plans for your goals and preferences"), built as **protocols rather than generations**, because a breathing count, a rep dose, and a menu are things a model could only make worse:
>
> - **`jim/calm.py`** — guided sessions: quick reset (5-4-3-2-1 grounding), box breathing (4-4-4-4 × 4, provably sixteen 4-second steps), 4-7-8 breathing, and a ten-minute sit. Timed steps the console paces and can speak (the same `say()` voice layer); sessions land in the events stream so insights sees practice like check-ins. `GET /calm` (public catalog), `POST /calm/{uid}/{kind}`, history.
> - **`jim/fitness.py`** — workout plans shaped to minutes (5–90), level (beginner/intermediate/advanced scales time-under-work), and focus (full body / cardio / strength / yoga / mobility), from a curated movement table with a cue on every block. Warm-up and cool-down are non-negotiable — the ten-minute user is exactly who'd skip them. `POST /fitness/{uid}/plan`.
> - **`jim/nutrition.py`** — meal plans by goal (lose weight / gain muscle / eat healthier) and preferences (vegetarian / vegan / dairy-free / gluten-free) as exclusion filters over tagged meals; protein-forward for muscle, plants-lead for health; orientation calories, and the disclaimer on every plan: meal structure, not medical nutrition therapy. `POST /nutrition/{uid}/plan`.
> - **Nutrition becomes a first-class Coach area** ("meal planning, eating patterns, hydration; never a diet prescription"); health & fitness stops claiming it.
> - **Console**: a new **Wellness tab** — calm sessions with a paced, speakable runner; the workout builder; the meal planner with preference toggles.
>
> Tests: `jim/tests/test_wellness.py` (4 — the protocol invariants, adaptation, preference exclusions, the new coach area). Full suite 662 green; console build green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #153 — Cut 0.14.5 — a fall reaches the Guardian

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/153>

> Release cut for **0.14.5**, in train with qrme and pdi. Carries two commits:
>
> - **The README speaks the campaign's language** — the masthead gains the product tagline (*Network Responsive Personal Guidance System for Known Conditions*) and the seniors mission line from the brand cards.
> - **The cut** — CHANGELOG heading over the Unreleased content (the fall through the drip, the native crash watch, the docs web, the conscious-branch pin), RELEASE_NOTES.md, README current-release line and table row, five version strings.
>
> Tag `app-v0.14.5` on the squash commit; release body stays empty for sync-release-notes.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #152 — The crash watch reaches the native shells, and a fall reaches the Guardian

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/152>

> Two commits, one story — the crash watch grows to cover the senior scenario end to end:
>
> **1. The crash watch reaches the native shells.** iOS (SwiftUI), Android (Compose) and Windows (WinUI 3) each gain a **Crash tab** on Safety: API clients (`crashWatch`/`armCrashWatch`/`disarmCrashWatch`/`imOkay`; Windows gains the missing `Put` helper), the arming form (trusted person, attempts 1–10, minutes per attempt, the EMS checkbox worded as the request it is), the live amber "JIM is asking: are you okay?" card with the **I'm okay** button, the tripped note, and the armed-quietly line — against the same `/crash-watch` routes the console uses.
>
> **2. A fall reaches the Guardian.** Field request: "in case of fall for seniors." The detector already treated a fall as critical — but the **watch drip only carried numbers**, silently dropping the one reading a senior on the floor most needs delivered. The drip now accepts the detector's own vocabulary — `movement: fall/collapse/immobile`, Shortcuts' `fall_detected: true`, `pulse: absent/weak` — whitelisted words, never free text, so the deposit-only posture holds. With the crash watch armed the whole chain runs: **the watch feels the fall → JIM asks "are you okay?" → silence summons the programmed help** (and fall + absent pulse escalates as the cardiac-arrest pattern). Copy on every surface — console, tutorial lesson, all three native shells — now names the fall.
>
> Tests: 10 crash-watch tests including the fall-through-the-drip chain and the free-text-never-rides refusal; watch + tutorial suites green (42 total in the affected files). Console build green; CI's native jobs compile the three shells.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #151 — The docs web catches the field round

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/151>

> Today's two field features — the crash watch and the journal — shipped ahead of the repo's binding web. This round brings the web up to the product:
>
> - **Drawn screens**: 87 *Journal* ("your words, typed or spoken" — the mic writes into the box first, sealed on a plan, read like a reading, newest first) and 88 *Crash Watch* ("if you stop answering" — the asking pill, the trusted person, EMS-only-if-ticked worded as a request, any-sign-of-you ends it). Regenerated for both platforms (176 SVGs).
> - **Tutorial lessons** `journal` and `crashwatch` (chapter *Being watched over*) claiming screens 87 and 88, each with a try-it.
> - **Dock**: a `crashwatch` face — *"whether JIM is asking 'are you okay?' — the question and the attempt count, never the reading"* — routed to screen 88 `/crash-watch`. The **journal deliberately gets no face**: the pane's NEVER list has said "what somebody wrote about their own day is not a glance" since before the tab existed, and this round honors it.
> - **README**: gallery rows for 87 and 88.
>
> Full suite 655 green (screens↔lessons↔gallery↔dock bindings all enforce the above).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #150 — Cut 0.14.4 — the crash watch, and the doors the field asked for

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/150>

> Release cut for **0.14.4**, in train with qrme and pdi at the same version.
>
> - CHANGELOG: 0.14.4 heading over the Unreleased content (the crash watch; the Journal tab, typed or spoken; the voice orb; the help box; the version-mismatch banner), link definitions repointed
> - RELEASE_NOTES.md rewritten for 0.14.4
> - README: "Current release" line and release-table row
> - Version strings: pyproject.toml, jim/api.py, app/package.json, app/package-lock.json (root entries)
>
> Tag `app-v0.14.4` on the squash commit fires the desktop-release workflow; the release body stays empty for sync-release-notes to fill.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #149 — The voice orb, and the help box

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/149>

> Live-testing feedback, applied:
>
> - **The voice orb** — talking with the Coach now looks like talking, ChatGPT-style: a breathing orb takes the screen while JIM **listens** (green) or **speaks** (violet), with a label and tap-anywhere to stop/hush. (The "Talk to it" failure in the screenshot was the stale-backend issue — the transcription route doesn't exist on the old process; the version banner catches that now.)
> - **The help box** — JIM gets its own faceless help fab on every screen, matching QRME's. Backed by new `jim/help.py` + public `POST /help` / `GET /help/topics`: a table of **written directions** (one per door — meds, baseline, crash watch, care team, journal, the "Not Found" case itself), matched by keyword and never a model call, so it cannot invent a feature. Anything beyond the app's own doors it hands to the Coach — which is JIM, exactly as suggested.
>
> Tests: `jim/tests/test_help.py` (3). `npm run build` green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #148 — The crash watch, and the journal's door

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/148>

> Two field requests from live testing, built as asked:
>
> **1. The crash watch** (`jim/crashwatch.py`) — "if pulse gets shallow and stops and JIM gets too many non-responsive attempts, contact emergency services and a trusted person."
>
> - **Armed in advance, off by default**: the user names a trusted person + channel, how many unanswered attempts is too many (1–10), each attempt's window (1–60 min), and ticks — or doesn't — "may request emergency services". Consent happens while they're fine.
> - **Fires on evidence stacked three deep**: a *critical* clinical detection opens "are you okay?"; unanswered deadlines march window-by-window from the moment the concern opened (a sweep waking after a long gap consumes every missed attempt, not one); the final unanswered attempt trips it.
> - **On trip**: the trusted person is contacted (actually emailed when SMTP is configured — degrade, never pretend), every connected system relays the alert, and the emergency-services step is recorded and relayed as a dispatch *request*, worded honestly: a local app cannot itself place a call.
> - **Any sign of the person ends it**: the "I'm okay" button or a normal reading; a stream of bad readings is the emergency continuing, not an answer. Drift-band check-ins stay calm and can never trigger it — the Baseline screen's "it never calls anybody" copy is replaced with the accurate story, plus the arming card and the live "JIM is asking: are you okay?" prompt.
> - Routes: `GET/PUT/DELETE /crash-watch/{user_id}`, `POST /crash-watch/{user_id}/respond`; wired into the Guardian's ingest path (sweep + open + resolve), never allowed to break biometric ingest.
>
> **2. The Journal tab** — the backend has carried `POST/GET /journal` for a long time; the console finally gives it a door: typed or **spoken** (the mic transcribes into the box for the user to fix before saving, via the same `speech.ts` the Coach uses), newest first, with the vault posture and the crisis-language behavior stated on-screen.
>
> Tests: `jim/tests/test_crashwatch.py` (8 — consent, open/answer, normal-vs-concerning readings, multi-attempt trip with the EMS request recorded, no-EMS-without-the-box, unarmed silence, drift stays calm, disarm). Full suite 660 green locally; `npm run build` green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #147 — The console names a version mismatch

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/147>

> Field report from live testing: a fresh console over a stale backend answers **"Not Found"** on the medication cabinet, care team, coach and check-in while looking otherwise alive — the old process still holds the address the console is using (the shell refuses mismatched backends on its own port, but a stored base address like the LAN one saved for the phone/watch bridge deliberately wins over the desktop URL, and that's the leak).
>
> The console now performs the version handshake itself (sibling PRs in qrme and pdi):
>
> - `vite.config.ts` injects `__APP_VERSION__` → `CONSOLE_VERSION`.
> - **`VersionGuard.tsx`** compares it against `/health.version` on launch; on mismatch, a fixed red banner on every screen names both versions and the address, with a one-click **"Use this app's own backend"** repoint when a stored address is the culprit, or instructions to end the leftover `jim-backend` process otherwise. Wraps onboarding too.
>
> `npm run build` green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #146 — Cut 0.14.3 — every README ends on the rock

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/146>

> Release cut for **0.14.3**, in train with qrme and pdi at the same version.
>
> - CHANGELOG: 0.14.3 heading over the Unreleased content (the scripture closing every README, test-enforced), link definitions repointed
> - RELEASE_NOTES.md rewritten for 0.14.3
> - README: "Current release" line and release-table row
> - Version strings: pyproject.toml, jim/api.py, app/package.json, app/package-lock.json (root entries)
>
> Tag `app-v0.14.3` on the squash commit fires the desktop-release workflow; the release body stays empty for sync-release-notes to fill.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #145 — Every README ends on the rock

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/145>

> Standing rule, per request: the scripture closes **every** README from here on.
>
> - The Matthew 7:24–25 passage (with the ark prose) that closes the root README now closes `app/README.md` and all four `native/` READMEs, byte-identical, at the very end.
> - `jim/tests/test_readme_scripture.py` enforces it: every tracked README must end with the root README's passage block, so the next README added cannot forget the rule.
> - CHANGELOG entry added. Sibling PRs apply the same rule in qrme and pdi.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #144 — Cut 0.14.2 — cut with the siblings

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/144>

> Release cut for **0.14.2**, in train with qrme and pdi at the same version. Docs only in JIM this round (the tandem contract documents suite mode).
>
> - CHANGELOG: 0.14.2 heading over the Unreleased content, link definitions repointed
> - RELEASE_NOTES.md rewritten for 0.14.2
> - README: "Current release" line and release-table row
> - Version strings: pyproject.toml, jim/api.py, app/package.json, app/package-lock.json (root entries)
>
> Tag `app-v0.14.2` on the squash commit fires the desktop-release workflow; the release body stays empty for sync-release-notes to fill.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #143 — Docs: suite mode enters the tandem contract

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/143>

> `docs/tandem.md` (kept byte-identical across qrme, jim-mini and pdi) gains a **"Suite mode — the gateway wires the tandems itself"** section: the gateway wires JIM's QRME client and QRME's `suite:qrme-vault` tenant at startup, `GET /suite/health` reports both joints, and `POST /suite/operations` re-draws PDI's per-tenant isolation by owner. Plus a CHANGELOG entry. Sibling PRs carry the identical file to qrme and pdi.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #142 — Cut 0.14.1 — the coach knows a care plan landed

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/142>

> Release cut for **0.14.1**, in train with qrme and pdi at the same version.
>
> - CHANGELOG: 0.14.1 section under Unreleased (the coach's prompt now carries a one-line note when a joint care plan landed — goal only, never plan text, quiet after seven days), link definitions repointed
> - RELEASE_NOTES.md rewritten for 0.14.1
> - README: "Current release" line and release-table row
> - Version strings: pyproject.toml, jim/api.py, app/package.json, app/package-lock.json (root entries)
>
> Tag `app-v0.14.1` on the squash commit fires the desktop-release workflow; the release body stays empty for sync-release-notes to fill.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #141 — The coach knows a care plan landed

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/141>

> `careteam.coach_context` feeds the coach the same way `meds.coach_context` does: one line when the care team wrote a joint plan in the last week — the goal, never the plan text, "worth walking through together if it hasn't come up, never presented as homework." Nothing older than a week; silent when no plan exists.
>
> Test proves all four properties: the line appears with the goal, the plan text never rides into the prompt, freshness wording ("today"), and week-old plans go quiet. Care-team suite: 7 passed.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #140 — Cut 0.14.0 — Home and the pane learn the care team

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/140>

> The 0.14.0 release-train cut for JIM-mini: the Overview's Medications and Care Team buttons plus the careteam pane face from #139. Cut mechanics as always; siblings cut alongside.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #139 — Home and the pane learn the care team

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/139>

> Two front-door touches:
>
> - The Overview's action row gains **Medications** and **Care Team** buttons.
> - The corner pane gains a **careteam** face — whether a joint plan is waiting to be read, **never its contents** (plan text is guidance-shaped and stays off captured surfaces, per the pane's NEVER stance) — routing to screen 86.
>
> Dock/tutorial/care-team suites: 32 passed; console build clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #138 — Cut 0.13.1 — no functional change; cut with the siblings

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/138>

> The 0.13.1 release-train cut for JIM-mini — no functional change; the docs round (#137) rode after 0.13.0, and QRME carries the demo org and hardening. Cut mechanics as always; siblings cut alongside.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #137 — Docs round: the tandem contract + invention disclosure catch up

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/137>

> Two documents catch up with the ecosystem round (siblings in qrme and pdi): docs/tandem.md byte-identical across the three repositories (care-team section + the coordination key space and operations journal), and docs/invention-disclosure.md gains the care-team stacking rule as a dated section for counsel.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #136 — Cut 0.13.0 — the care team is an organization

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/136>

> The 0.13.0 release-train cut for JIM-mini. This round: the care team is an organization (#134) with its console tab (#135) — proved end-to-end against live QRME and PDI processes.
>
> Cut mechanics: CHANGELOG section + link definitions, RELEASE_NOTES for the `app-v0.13.0` tag, README release line + table row, five version strings.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #135 — The console shows the care team

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/135>

> The console half of #134: a **Care Team** tab in the desktop console.
>
> - Link form: org id, the desk that speaks for the Guardian, and your QRME owner token — a password field, cleared the moment the link succeeds; the backend never echoes it and unlinking deletes it.
> - Once linked: the stacking-rule explainer (drift + slipping doses → the whole team, once a day, calm path only), a manual "take a goal to the team" box, unlink.
> - Joint plans render newest first with the sealed-in-vault mark when the tandem carried them there.
>
> Console `tsc --noEmit && vite build` clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #134 — The care team is an organization: Guardian coordinates the household

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/134>

> QRME's operational ecosystem (qrme#185), joined from JIM's side — the tandem round.
>
> ## What it does
> - `PUT /users/{id}/care-team` links the user's **own QRME organization** and names the department that speaks for the Guardian. Validated at link time against QRME (org readable, department present, at least two desks — a lone department is not a team).
> - **The stacking rule** (`jim/careteam.py`, hooked into the Guardian's calm path): a drift-band crossing arriving while any medication's 7-day adherence is below 75% takes the situation to the whole team as one coordination goal. The joint plan comes back and lands as a care plan (`GET …/care-team/plans`), with what triggered it recorded.
> - `POST …/care-team/coordinate` is the same path by hand, minus the rule.
>
> ## The three rules that keep it honest
> - **The user's own credential, pasted knowingly.** QRME's org routes are owner-only on purpose and JIM never sneaks around that; the owner token is stored like the tandem interactor token, never echoed back, and unlinking deletes it.
> - **Summaries cross, never raw readings.** The goal names the adherence percentage and which band drifted — not the sample stream.
> - **A care team is not an alarm.** Calm path only, at most once per 24h, and `careteam.consider` never raises into biometric ingest — anything `conditions.detect` flags is already on the escalation ladder, which no coordination replaces.
>
> ## Product binding
> Screen **86 · Care Team** (both platforms), the `careteam` tutorial lesson, README gallery row + API-table row.
>
> ## Verification
> `jim/tests/test_careteam.py` (6 tests: link validation, lone-department refusal, manual coordination, credential deletion on unlink, the stacking rule with cooldown, no-slipping-meds no-op) — full suite **642 passed**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #133 — Cut 0.12.0 — no functional change; cut with the siblings

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/133>

> The 0.12.0 release-train cut for JIM-mini. **No functional changes to JIM-mini in this release** — cut with the siblings per the convention.
>
> In QRME this round, the filed patent specification (App. 19/056,418) was mined: hybrid profiles blended from several people, real-time simulation of the represented person's likely decisions, and replies that adapt to where the person actually is — backend and console both.
>
> - CHANGELOG 0.12.0 section + link definitions repointed
> - RELEASE_NOTES.md refreshed for the `app-v0.12.0` tag
> - README current-release line and release-table row
> - Version bumped in all five places (pyproject, `jim/api.py`, package.json, both lockfile root entries)
>
> 636 tests green, unchanged in behaviour.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #132 — Cut 0.11.1 — no functional change; cut with the siblings

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/132>

> In PDI, the desktop app finally carries its own vault. **636 tests green**, unchanged in behaviour.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #131 — Cut 0.11.0 — no functional change; cut with the siblings

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/131>

> In QRME, the console caught up with its backend. **636 tests green**, unchanged in behaviour.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #130 — A real offline model, and Settings says what it means — 0.10.0

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/130>

> Field report: the offline helper "doesn't want to give real coaching replies" — correct, it was a canned fallback and could only explain itself. This round gives it a brain.
>
> ## Local (Ollama) — a real offline model
>
> - Install Ollama (ollama.com), `ollama pull deepseek-r1:1.5b`, done: **JIM finds the daemon on its own.** The daemon running IS the configuration, so `is_configured("ollama")` probes `127.0.0.1:11434` (500 ms timeout, 10 s cache) instead of looking for a key that doesn't exist.
> - New **Local (Ollama)** tile in both pickers, `network: False` — nothing ever leaves the machine.
> - **Automatic prefers a running local model over the stub** when no cloud key exists (Claude still wins when a key is present).
> - **Offline mode uses it too**: `JIM_OFFLINE` forbids the network, and a loopback model isn't network.
> - `JIM_OLLAMA_MODEL` / `JIM_OLLAMA_URL` override the defaults. The stub's chat reply now names both ways out: add a key, or install Ollama.
>
> ## Settings honesty (also field-reported)
>
> - The backend status line said "tandem off" as if a switch existed — it now says the vault tandem is **set by the deployment, not a switch**.
> - **Your model API key** moved to sit directly under *Which model answers* instead of stranded below Email delivery.
>
> Cut **0.10.0** with the siblings.
>
> ## Verification
>
> **636 tests green** (4 new): the Local tile is honest about an absent daemon; a running local model wins Automatic over the stub; offline mode uses a running local model and degrades to the stub without one; the fallback's reply names both ways out. Console build clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #129 — The drip address answers — 0.9.1

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/129>

> Field report, mid-setup: the Apple Watch panel handed out the machine's Wi-Fi address (`http://192.168.x.x:8000/…`) while the desktop app's bundled backend listened only on loopback. A phone POSTing to it got "could not connect", and the card never said so.
>
> ## Three fixes
>
> 1. **The card tells the truth** — `phone_reachable` rides the `/watch/channel` response; an amber notice explains when the phone cannot reach the address yet, instead of letting the user build a Shortcut against a dead URL. The CLI's `phone`/`serve` modes now record how they bound (`JIM_HOST`) so the card is honest there too.
> 2. **One press opens the door** — *"Let my phone reach JIM on this Wi-Fi"* writes a persistent flag; the shell restarts the bundled backend with `JIM_HOST=0.0.0.0`. Loopback stays the default — private until asked, and asked in the exact place the need arises. Everything per-user behind the port still requires that user's token.
> 3. **The recipe names the paste spot** — the drip address goes in **Get Contents of URL → URL** ("THIS is where it goes", in capitals), and the recipe stops promising an hourly trigger Shortcuts doesn't have: Time of Day, repeat daily, second automation for the evening if wanted.
>
> Cut **0.9.1** with the siblings.
>
> ## Verification
>
> **632 tests green** (2 new): the setup card reports unreachable on a loopback bind and reachable on a network bind; the recipe names the paste spot. `main.cjs`/`preload.cjs` syntax-checked; console build clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #128 — The medicine cabinet — 0.9.0

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/128>

> What the user takes, **in their own words** — *"the little white one, 10 mg"* is a valid name and dose. `jim/meds.py`, a **Medications** screen in the nav, and the boundaries that make a medication tracker guardian-grade instead of overreaching:
>
> ## The board
>
> - **Done / due / upcoming / missed, with humane grace** — a dose is "due" from an hour before its time to 90 minutes after; 9:07 is not "missed" for the 8:00 pill, because a board that scolds seven minutes teaches the person to ignore it.
> - **One slot, one answer, correctable** — logging again replaces (skipped → taken happens; people find the pill in their pocket). No duplicates, no double-counted adherence.
> - **Adherence counts whole past days only** — an afternoon dose is never "missed" at noon.
>
> ## The lines it will not cross
>
> - **The as-needed ceiling refuses to log past itself** (409, pointing at the prescriber) — recording the overage would be complicity.
> - **A missed dose is a check-in, never an alarm** — even one marked critical produces an amber note on the board and a line in the coach's context ("worth asking about gently, never scolding"). No path from this module into the escalation ladder; the test suite asserts no escalation event is ever written.
> - **JIM is not a pharmacist** — no interaction checker (a toy one would be trusted); the board carries *"your pharmacist does that"* on its face.
>
> ## The layers reinforce each other
>
> Every dose logged lands in the events table — **a sign of life the vigil counts**. For the person whose only daily interaction is their pillbox, taking their medication quietly keeps the steward unalarmed. Tested end-to-end: a tripped vigil stands down when a dose is logged.
>
> ## Ships with
>
> Screen **85 · Medications** (iOS + Android), tutorial lesson (`meds`), README route-table row + gallery cell, coach context integration. Cut **0.9.0** with the siblings.
>
> ## Verification
>
> **630 tests green** (11 new). Console `npm run build` clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #127 — The vigil: the alarm that fires when the signals stop — 0.8.0

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/127>

> Every other alarm fires on a reading; this one fires on the **absence** of readings — the watch that went quiet, the check-in that never came, the person living alone whom no threshold can see because nothing arrives to measure.
>
> ## `jim/vigil.py`
>
> - **Steward chosen and worded in advance** — who is told, over which channel, and (the `note`) *what they read*, written by the user while they were fine. A vigil that composes its own message speaks for someone at the exact moment they cannot correct it.
> - **Silence measured against the events table** — any sign of life resets it with zero bookkeeping. The vigil's own trip is excluded from the measurement, or every trip would reset the very silence it measured.
> - **Never past the steward** — no emergency services, no escalation ladder. Silence is weak evidence; the right response is a person who cares knocking on a door.
> - **Idempotent trip, automatic stand-down** — `sweep` is safe from anywhere (the console sweeps on open) and trips at most once per silence; the next reading resolves it, because showing up *is* the all-clear. Steward emailed when SMTP is configured; loud console notice when not — degrade, never pretend.
> - A user never heard from at all cannot trip it — a brand-new account that armed the vigil and walked away is not a missing person.
>
> ## Continuity across the three products
>
> The trip's event id serves as the attestation reference for QRME's reviewer-gated ownership succession and PDI's new bequests — **one attested absence carries through all three products**. Recorded in `docs/invention-disclosure.md`.
>
> ## Console
>
> **Settings → The vigil**: arm/disarm, quiet-days dial, the pre-written note, armed status with last-heard, and an amber tripped notice with an **I'm okay** button.
>
> ## Verification
>
> **619 tests green** (10 new), including: the trip never counts as a sign of life; exactly one trip per silence; no escalation event is ever written; the steward's message says plainly it is not an emergency; a fresh reading stands it down; disarm holds through any silence. Console build clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #126 — The app keeps itself current — 0.7.0

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/126>

> On launch the desktop shell asks GitHub Releases whether a newer version exists (`electron-updater`; the release workflow already publishes the `latest*.yml` metadata and blockmaps it feeds on, so no CI change was needed).
>
> - **Windows / Linux**: the update downloads in the background, then one dialog — *Restart now, or later?* `killBackend()` runs before `quitAndInstall()`, so the new version starts its own backend instead of adopting the old one (the 0.4.7 lesson, honored here too).
> - **macOS**: an unsigned app cannot swap itself, so it does the next honest thing — says a new version exists and opens the download page.
> - Every failure path is silent by design: no network, no release, no metadata → the app simply opens. An update check must never stand between the user and the app.
>
> Ships *in* 0.7.0 — the last version anyone fetches by hand.
>
> Also: the tutorial guard caught that screens 81–84 had no lessons. Four added (bands, speaking out loud, the model picker, the watch bridge) — the guard doing exactly what it exists for.
>
> ## Verification
>
> **609 tests green.** Console build clean; `main.cjs` syntax-checked; `electron-updater` added as a runtime dependency so electron-builder packages it; `build.publish` set to this repo so the update metadata points at the right releases.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #125 — Screens 81–84: the four capabilities the gallery didn't show yet

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/125>

> Four new screens in `docs/screens/build.py`, generated for **iOS and Android**, validated as SVG, and added to the README gallery:
>
> - **81 · Your Baseline** — the drift bands: per-metric band around the learned baseline, HRV and oxygen watching the low side, a temperature band still *LEARNING* at 3 of 5 samples.
> - **82 · Coach, Out Loud** — hold to talk, the transcribed question, the reply spoken by Daniel (ElevenLabs), and the device-voice fallback.
> - **83 · Which Model Answers** — Claude active, five providers one tap away, the on-device key, and the amber honesty when a reply degraded.
> - **84 · Apple Watch** — the two doors: the hourly Shortcut drip with its deposit-only address, and the export.zip seed with 62 days folded.
>
> Every `docs/**.svg` referenced by the README verified present on disk.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #124 — Restore the owner's LICENSE exactly as he wrote it

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/124>

> PR #123 squash-merged a stale snapshot that still carried the license rewrite, so the rewrite reached main against the owner's explicit instruction. This restores the LICENSE byte-identical to his last deliberate license commit (`4f3a019` — "Revise MIT License to include notarization clause"), along with the MIT metadata lines in `pyproject.toml` and `app/package.json` that accompanied it.
>
> The invention disclosure (`docs/invention-disclosure.md`) stays.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #123 — Record the inventions with dates

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/123>

> `docs/invention-disclosure.md` — a dated disclosure of each distinctive mechanism, where it is reduced to practice in this repo, and the release that first shipped it: the watch bridge (deposit-only drip credential, 404-not-403 channel privacy, same-day baseline seeding by chronological per-day medians with motion-context exercise exclusion), drift bands as a check-in layer that can never escalate, signal-quality-capped escalation, the degrade-not-fail model layer with disclosed provenance, and version-matched backend adoption. Written to be handed to a patent attorney as the starting point for provisional applications, and standing as a public, git-timestamped priority-of-invention record.
>
> **The LICENSE is untouched — it stays exactly as the owner wrote it.**
>
> Not legal advice, and no substitute for counsel. No version cut: nothing behavioral changed.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #122 — The coach stops performing distress it never detected — 0.6.1

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/122>

> Field report: a career question — *"I want this app I built to be successful"* — answered with *"I'm here with you [stub guidance for distress]… let's take one slow breath together."* Every time, word for word. Three stacked causes, three fixes.
>
> ## 1. The stub answered chat with crisis language
>
> The deterministic fallback keyed on a `condition:` line that only the *medical guidance* path puts in the system prompt, and **defaulted to "distress"** when chat gave it none. In chat, the stub now explains itself honestly — it is the offline fallback, the message is saved, and Settings → Model is where the fix lives — instead of playing a counselor. (The tone marker still rides along; it is how tests prove personality reaches the prompt.)
>
> ## 2. Degrades were silent, and provenance named the wrong author
>
> Any model failure — missing key, missing SDK, network, a 529 — degraded to the stub with only a server-side log line, while the reply's `generated_by` named the provider that was **picked**, not the one that **answered**. Canned text under Claude's name.
>
> `llm.generate_for_user()` is the disclosure: `provider` is whoever actually produced the words, `degraded` says it wasn't who was meant, `reason` says why in words a user can act on ("anthropic did not answer: …", "no API key on this machine — add one in Settings → Model"). The coach reply carries all three; the console renders *"Answered by anthropic"* under a real answer, or an amber warning under a fallback.
>
> ## 3. Settings was silent in the worst case
>
> *Automatic* quietly resolving to the stub, under a screen full of provider logos. The model panel now shows an amber notice when replies will come from the built-in helper — and what to do about it.
>
> ## Release
>
> Cut **0.6.1** with the siblings: CHANGELOG, README, RELEASE_NOTES, all five version strings.
>
> ## Verification
>
> **609 tests green** (5 new), including: `generated_by` is the stub when the stub answered, with an actionable reason naming Settings; a mid-request 529 is disclosed as "did not answer" while the reply still delivers; chat stub text contains no "distress", no breathing instructions, and points at Settings; a genuinely configured provider reports undegraded with no reason; and picking the stub on purpose is not called a degrade. Console `npm run build` clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #121 — The Apple Watch bridge: a Shortcuts drip and a Health-export seed — 0.6.0

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/121>

> HealthKit only talks to App-Store apps, and JIM does not have one. Every iPhone still has two free doors out, and `jim/watch.py` is the receiving end of both — so testers' Apple Watches can reach a shared Windows-hosted backend with nothing to install.
>
> ## The drip — live readings from a Shortcuts automation
>
> A per-user tokened URL (`POST /watch/drip/{token}`), POSTed to by an iPhone **Shortcuts personal automation** on a schedule. Built once from the numbered recipe on the setup card.
>
> - **Forgiving payload**: `heart_rate`, `heartRate`, `"72 count/min"`, SpO₂ as HealthKit's fraction (0.97) or a typed percent (97) — all one reading. Unknown keys are ignored, never an error.
> - Every arrival runs the **full pipeline** — detection, drift bands, escalation — exactly as if typed on the Monitor screen.
> - The reply is **deposit-only**: a received count and a noticed flag, never guidance. The token rides in a URL, and a URL-bearer credential must not read health information back out.
> - A wrong token is a **404, not a 403** — confirming a channel exists would itself be information.
> - **Rotate** retires a leaked address in one tap.
>
> ## The seed — the Health export becomes the baseline
>
> `POST /watch/seed/{user_id}` takes the Health app's *Export All Health Data* zip (or the bare export.xml) as the raw request body — no new multipart dependency in the frozen backend.
>
> - **Per-day medians fold chronologically** into the baselines: resting heart rate, HRV, oxygen, respiration, temperature. Months of history the watch already recorded become an **established baseline on day one**, drift bands armed the same afternoon.
> - **History is context, not news**: the seed writes no events and raises no check-ins.
> - Raw heart-rate records without the **sedentary motion context** are excluded, so exercise never teaches the bands a resting rate that isn't.
> - Unit honesty: oxygen's fraction → percent, `degF` → °C.
>
> ## Storage note
>
> The new `watch_channels` table stores the drip token in the clear — deliberately against the house never-return-the-secret rule — because this credential can only deposit readings and the setup screen must keep showing the URL for a person retyping it into a Shortcut weeks later. The schema comment argues the case; rotation is the recovery.
>
> ## Console
>
> Settings grew an **Apple Watch** panel: drip address with copy + rotate, the Shortcut recipe, the export upload with a per-metric report ("resting heart rate: 62 days folded, baseline 58.4 — established"), and the arrival counter.
>
> ## Release
>
> Cut **0.6.0** with the siblings: CHANGELOG, README (route-table row + release row), RELEASE_NOTES, all five version strings.
>
> ## Verification
>
> **604 tests green** (19 new), including: a seeded history raises not a single event; the drip reply carries no guidance or identity; a rotated address stops working immediately; a wrong token is a 404; exercise readings never reach the resting baseline; a day's readings fold once as their median; the zip the Health app actually makes (with `export_cda.xml` beside the real one) parses; and a seeded baseline arms the drift bands the same day. Console `npm run build` clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #120 — Personal drift bands, a voice, and a model picker with logos — 0.5.0

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-bands-voice-picker` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/120>

> Three things a guardian needs that JIM did not have.
>
> ## Drift bands — a threshold around *your* baseline
>
> `jim/bands.py` keeps a band per metric — heart rate, resting heart rate, HRV, blood oxygen, respiratory rate, body temperature — measured as a distance from the learned baseline rather than a population range. Each band has a low and a high edge, and each edge is watched or ignored: HRV and blood oxygen watch only the low side, because a high number there is good news.
>
> A band whose baseline is still provisional stays silent — the guardian will not raise a threshold against a number it has barely seen. One sensitivity dial (cautious / balanced / assertive) scales every band at once.
>
> Crossing a watched edge produces a check-in that is a question, not a verdict: what crossed, which direction, by how much, and *"How have you been feeling?"* The guardian now updates the baseline for **every** metric rather than heart rate alone — which is what made the other five bands possible in the first place.
>
> New screen: **Settings → Baseline**, with a slider and watch-low/watch-high per metric, the current baseline, its sample count, and a reset.
>
> ## Voice — speak to it, hear it back
>
> `jim/voice.py` is a provider layer in the shape of `llm.py` and `mailer.py`:
>
> - **ElevenLabs** (male voices first — Daniel the default, plus Adam, Josh, Arnold, George) or **OpenAI** (onyx, echo)
> - environment beats the settings screen beats nothing
> - the key is never returned by the API
> - an unconfigured service **degrades** to the browser's own speech (preferring a male system voice) instead of failing the request
>
> The coach screen gained a microphone and a read-aloud button. A spoken question gets a spoken answer; a typed one stays quiet.
>
> ## Model picker with logo tiles
>
> Settings shows a tile per provider — Claude, ChatGPT, Grok, Perplexity, Gemini, plus Auto — each with its own glyph, drawn here rather than copied, so the choice is visible at a glance instead of being a string in a dropdown.
>
> ## Release
>
> Cut **0.5.0** with the siblings: CHANGELOG, README, RELEASE_NOTES, and all five version strings.
>
> ## Verification
>
> **585 tests green**, including: a provisional baseline raises nothing; assertive narrows the band while cautious widens it; an ignored edge is never reported; the voice key never comes back out of the API; an unconfigured voice service degrades rather than fails. Console `npm run build` clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #119 — Email delivery is configurable from the app itself — cut 0.4.8

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-mail-settings` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/119>

> **Answering the question directly: no verification email was ever sent because there was nowhere to send it through.** An app hands mail to a mail server; until now the only way to name one was an environment variable, so a desktop install could never send one at all.
>
> **Settings → Email delivery** (`mail_settings`, `GET/PUT/DELETE /settings/mail`, `POST /settings/mail/test`) now takes a mail server, username, app password, from address and link address. It reports which of three sources is in force — environment > settings screen > none — and **sends a real test message on demand**, surfacing exactly what the mail server said rather than claiming success. The password goes up and never comes back down.
>
> Configuring one turns local signup back into genuine email verification, clickable link and all; leaving it empty keeps the honest local behaviour.
>
> 566 tests green — including that the password never comes back out, the environment outranks the settings row, a refused send reports the server's own words, and configuring mail flips signup from local activation to a real emailed link. 0.4.8 release prep included.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #118 — An upgraded app no longer adopts an older install's leftover backend — cut 0.4.7

- merged · opened 2026-07-29 · merged 2026-07-29
- `claude/jim-stale-backend` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/118>

> **The root cause behind three "fixed" signups that weren't.** A field screenshot showed 0.4.5+ console copy demanding a code — which only a pre-0.4.5 backend does. The shell adopted whatever backend answered its port, and on Windows quitting killed the frozen backend's *launcher* while leaving the real Python process alive. A zombie from an early install held 8000 across every upgrade and served its old API to each new console.
>
> - `/health` reports the backend's **version**.
> - The shell adopts a running backend **only when that version is its own**; otherwise it takes a free port, starts its own there, and passes that exact address to the window (a stored loopback address never overrides it).
> - Quitting kills the backend's **whole process tree** (`taskkill /T` on Windows).
> - The release gate now asserts the frozen backend reports the version being packaged.
>
> Verified against a simulated impostor: an old backend answering 8000 → shell refuses it → starts its own on a free port → signup goes straight through, no code screen. 558 tests green. 0.4.7 release prep included.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #117 — A stranded pending account is finished on a no-mail machine — cut 0.4.6

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/jim-signup-recovery` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/117>

> Databases from older builds hold half-made accounts (0.4.3 crashed mid-signup) that nothing can ever verify where no mail can be sent — and they were resurrecting the email screen on desktop installs. Retrying signup on a no-mail deployment now finishes the pending account on the spot, under the newly-typed password. A **verified** account is never overwritten this way, on any deployment; SMTP deployments still require the emailed proof. Guard test covers both sides. 557 tests green. 0.4.6 release prep included.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #116 — Verification matches the deployment: direct on desktop, link-first by mail — and the 0.4.5 cut

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/jim-signup-recovery` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/116>

> From the 0.4.4 field report: the code screen waited for an email that can never arrive — a desktop install has no mail service.
>
> - **Desktop (no mail transport): signup activates directly.** The machine owner is trusted on a single-user local install; there is no inbox to prove. Create account → in.
> - **Hosted (SMTP): the email now leads with a clickable verify link** (`GET /verify-email/click`, human-facing result page), 6-digit code as fallback; the app polls sign-in with the credentials it already holds and continues on its own after the click.
> - A pending account left by 0.4.3's crashed signup routes straight to verification with a fresh code instead of stranding the retry; already-verified routes to sign-in.
> - The packaged app can open its own backend log (Electron bridge button).
> - Smoke gate updated: the frozen binary must now sign up **straight into a session** on each OS.
>
> 556 tests green; frozen binary rebuilt and smoke-passed locally; consoles typecheck and build. 0.4.5 release prep included.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #115 — Release gate: the frozen backend must perform the real first run, per OS

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/jim-win-signup-500` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/115>

> No installer ships a first run that was not performed. Before electron-builder touches anything, the exact PyInstaller binary that will be packaged runs the whole flow **on the runner's real OS** — signup, the code read from the console log the way Electron pipes it, verify, a personal route, sign-in — with `PYTHONIOENCODING=cp1252:strict` so the Windows console-encoding class of failure is exercised on every platform, Linux included.
>
> 0.4.3 shipped a Windows-only signup 500 this step would have refused to package. "It worked on Linux" stops being a release argument here.
>
> Verified locally against fresh frozen binaries, twice in a row each (the double-run caught and fixed a leftover-process bug in the gate itself: PyInstaller one-file spawns a child the parent's kill doesn't reach — per-run ports + process-group kill now).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #114 — Fix the Windows signup 500, and cut 0.4.4

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/jim-win-signup-500` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/114>

> Reported from a real 0.4.3 Windows install within the hour of shipping: signup answered `Unexpected token 'I', "Internal S"… is not valid JSON`.
>
> Two stacked bugs:
>
> - **The backend 500'd**: with no mail server configured, the verification code prints to the server console — in a banner drawn with `═` box characters that the frozen Windows backend's cp1252 stdout cannot encode. The print raised mid-request, so every signup died on the one platform the console transport serves most. ASCII banner now; `packaging/backend_entry.py` reconfigures stdout/stderr to replace rather than raise; a test encodes the console delivery to cp1252 forever (mutation-checked: restoring one box character fails it).
> - **The console hid the real error**: `req()` assumed every body is JSON, so the person saw a JSON.parse exception instead of "Internal Server Error". Non-JSON bodies now surface as the server's own words.
>
> Plus the 0.4.4 release prep (changelog, notes, README table, five version strings under the guard). 553 tests green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #113 — mac: declare the frozen backend in x64ArchFiles

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/jim-packaged-signup` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/113>

> The `app-v0.4.3` build failed on macOS only: the universal build merges the x64 and arm64 app bundles, and `@electron/universal` refuses any file identical in both that is not declared — which the PyInstaller backend binary is, being one file for both architectures. One config line: `mac.x64ArchFiles: "Contents/Resources/backend/*"`.
>
> Windows and Linux built fine; the release job skipped (and no installers attached) only because the matrix had this one failure. After merging, move the `app-v0.4.3` tag to the fix commit and the workflow will attach the full installer set.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #112 — Real accounts, bring-your-own model key, the self-running installer — and the 0.4.3 cut

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/jim-packaged-signup` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/112>

> Two commits: the packaging round (accounts + BYO key + frozen backend, described below) and the 0.4.3 release prep (changelog, release notes, README table, all five version strings under the five-way guard).
>
> ### Accounts, with the email proven first (`jim/accounts.py`, `jim/mailer.py`)
>
> `POST /signup` takes email + password + the enrollment fields and **creates nothing yet** — a 6-digit code goes to the address (SMTP when `JIM_SMTP_*` is configured, printed to the server terminal otherwise), and only `POST /verify-email` enrolls the user and mints the first token, so a mistyped address never grows a record nobody can reach. `POST /signin` refuses unverified addresses and answers unknown-address and wrong-password identically; `POST /password/reset/request` + `POST /password/reset` change a forgotten password by the same emailed-code proof and revoke every existing session. Passwords are PBKDF2 with per-account salts; codes are hashed at rest, single-use, 15-minute expiry, purpose-bound.
>
> The console's onboarding is the conventional flow — create-account / emailed-code / sign-in tabs, show/hide password toggles, a re-enter field checked live, the requirement stated up front, and **Forgot password?** — studied against mainstream signup conventions and built as our own screens.
>
> ### Bring-your-own model key
>
> `x-llm-api-key` rides any request into a request-scoped context variable the provider layer reads — that request's generations run on the caller's credential, **never persisted, never logged**. An explicit provider choice plus a caller key counts as configured; a key on auto defaults to Claude rather than the stub; the deployment's env `ANTHROPIC_API_KEY` remains the fallback. Settings stores the key device-side only.
>
> ### The installer runs itself
>
> `packaging/backend_entry.py` freezes the whole backend with PyInstaller (CORS on, loopback only, data under the app's user-data directory); the release workflow builds it per-OS and ships it via `extraResources`; Electron probes `/health`, spawns the bundled backend when nothing answers, waits for it, and kills it on quit.
>
> ### Verification
>
> 552 tests green (22 new). The frozen binary was built and booted on Linux, and the **full signup flow was driven end-to-end against it in a real browser** — form → code read from the backend terminal → verified → Overview.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #111 — Online model default, and the Windows first-run fixed

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/jim-online-model` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/111>

> Three commits, all from running the product for real today.
>
> ### Default the Anthropic provider to claude-opus-5
>
> The default model string in `jim/llm.py` (and the README lines quoting it) still named the previous Opus generation. `JIM_MODEL` still overrides; every other provider default untouched. Mirrors the same change in qrme.
>
> ### Fix the Windows first-run (reported from a real install of the .exe)
>
> - **The enrollment form shipped with a developer's sample name and birthdate in the boxes.** Identity fields now start empty, and Get Started stays disabled until name, birthdate and consent are all given — a pre-filled birthdate in an age field is a wrong answer already submitted.
> - **"Failed to fetch" on Get Started** meant no Guardian backend at `127.0.0.1:8000` — the installer ships only the console. Onboarding now checks for the backend up front and, when unreachable, says exactly that, with the command to start one and an editable backend URL with retry. Every API call now names the backend and the fix instead of surfacing the raw fetch error.
> - **The window was titled "QRME"** — retitled "JIM Guardian", preload bridge renamed `jimDesktop`.
>
> ### serve: default CORS open on loopback, so the console's own advice works
>
> Following the app's recovery instructions still dead-ended: the packaged console calls the API cross-origin, and `python -m jim serve` never set `JIM_CORS_ORIGINS`, so every request died as "Failed to fetch" against a backend that was running fine. A loopback serve now defaults CORS open — the posture the in-app hint has always instructed — announced on stdout, with `--no-cors` to keep it closed, and never when binding beyond loopback or when an explicit allowlist is set. Personal endpoints still require bearer tokens. Four tests, mutation-checked. The console's messages now name `python -m jim serve` (bare `python -m jim` only prints the launcher menu).
>
> Verified: `tsc --noEmit && vite build` clean; drove the built console in a real browser against a bare `python -m jim serve` — no env vars, panel clears, enrollment goes through to Overview. 530 backend tests green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #110 — The desktop installers were labelled 0.3.3

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/jim-capture` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/110>

> Found while verifying the app-v0.4.1 release: the attached installers are named `JIM.Guardian-0.3.3-universal.dmg`, `JIM.Guardian.Setup.0.3.3.exe`, etc.
>
> `app/package.json` carries its own version and no cut ever bumped it — 0.4.0 and 0.4.1 both shipped installers stamped 0.3.3. Built from the right tag, current code; stale label, and invisible to the auto-updater, which compares package versions.
>
> - `app/package.json` → `0.4.1`
> - A guard test asserting it always matches the API version (mutation-checked in QRME; identical guard here)
>
> The published 0.4.1 installers keep working; the next tag builds correctly named ones.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #109 — Cut 0.4.1 — the round where a photograph really reached a clinician

- merged · opened 2026-07-28 · merged 2026-07-28
- `claude/jim-capture` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/109>

> Release housekeeping only — no code beyond the version string. 525 tests unchanged.
>
> - CHANGELOG: `[Unreleased]` → `[0.4.1] — 2026-07-28`
> - `jim/api.py` version `0.4.0` → `0.4.1`
> - README: header to v0.4.1, a 0.4.1 row in the release-history table
> - `RELEASE_NOTES.md` rewritten as the ready-to-paste body for the `app-v0.4.1` release
>
> Same two leftovers from the previous cut as QRME, fixed while passing: the `[Unreleased]` compare link still pointed at `app-v0.3.3` with no `[0.4.0]` ref, and `RELEASE_NOTES.md` was still the 0.3.3 body.
>
> After merging: create the `app-v0.4.1` tag on the merge commit and paste `RELEASE_NOTES.md` as the release body.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #108 — Clinical capture, a free plan under platform custody, and the join that made the claim true

- merged · opened 2026-07-27 · merged 2026-07-28
- `claude/jim-capture` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/108>

> Five commits that interlock — a photograph of a body is the sharpest test of what an open store may hold. 525 tests pass.
>
> ## Clinical capture — showing it, rather than describing it
>
> `jim/capture.py`, 6 routes, 35 tests, screens **76** and **77**. Photograph a rash, film a tremor, attach it to a condition. Four rules, each asserted and mutation-checked: **a synthetic agent never receives the image** (told it exists, where and when — routing, never diagnosis; AST-checked); **never an intimate site for a child** — no override, no guardian consent path; **the pixels never touch JIM's own database** (vault only, schema has no column that could hold an image, no fallback — the graceful version is an unencrypted photo of somebody's skin in a SQLite file); **location is stripped, not promised absent** — a real JPEG segment parser drops Exif/XMP/ICC/IPTC, checked against the sealed bytes.
>
> ## The join that made the claim true
>
> `capture.py` said a photograph could "reach a real clinician through the referral flow that already exists" — and for one round that was true of nothing: `attach_to_referral` returned a decision no caller consumed, `mark_released` was dead code, `referral.prepare` had no idea captures existed. **The README, the walkthrough and this PR's own first body repeated the claim.**
>
> Now: `POST …/referral/prepare` takes `capture_ids`; the package carries their **metadata, never bytes**, so the person reads exactly what would go before signing; intimate sites are filtered by going back through `attach_to_referral`, so one place holds that rule; `POST …/referral/requests/{id}/released` stamps them. And `seen_by_clinician` is now `released_to_clinician` — released is not opened, and JIM has no way to observe the second.
>
> ## A free plan, with nothing private about it
>
> `jim/storage.py`, 51 tests, screens **78–80**. Free is the whole Guardian with the record under **platform custody**: JIM-mini holds it, the person has access, ordinary HTTPS, no vault at any point — custody, not ownership, because statutory rights over personal data survive whatever a plan says. Free and Basic reach identical capabilities; **$20 buys the vault, not a feature**.
>
> The open store refuses a photograph of a body and a child's record (refused at enrolment, and `guard_dependant_write` covers the diary after a downgrade — enrolling on Basic then moving to Free is one API call). The health readings are deliberately **not** refused: they are the emergency path, and a storage refusal in front of an escalation is a paywall in front of an alarm wearing a privacy argument. `guardian._event` stays unguarded and a test asserts it.
>
> ## The vault gate asked the wrong question
>
> Every seal point read `if pdi is not None` — the *deployment*, not the *account* — so a free account on a PDI-backed deployment had its journal, check-ins and detections sealed into a vault it wasn't paying for. Twelve write sites now resolve through `_vault(user_id)`, guarded by **counting vault writes across an ordinary day**. Reads and deletions keep the real vault so a downgraded account can still read and purge its sealed history. The access log stopped telling the comfortable lie that an empty list means nothing was read — on an open plan it means nothing was *recorded*, and it now says which.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #107 — Fix a broken gallery image on main, and add the guard that would have caught it

- merged · opened 2026-07-27 · merged 2026-07-27
- `claude/jim-0.3.3` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/107>

> Found while checking whether anything needed pruning after the v0.4.0 release. It did not — but this did.
>
> ## The bug, on `main` right now
>
> Screen 74, **"You're on Basic"**, was written to `74-you're-on-basic.svg` while the README points at `74-youre-on-basic.svg`. GitHub's raw host escapes the apostrophe to `%27`, so the plain-character reference resolves to nothing and the gallery draws a broken icon.
>
> ```
> docs/screens/74-youre-on-basic.svg    -> HTTP 404
> docs/screens/74-you%27re-on-basic.svg -> HTTP 200
> ```
>
> ## Why it got through
>
> Not a typo. QRME had been bitten by this exact class **twice** — a comma, then a `?` — and gained a `slug()` function plus a test asserting no screen file is named something a URL cannot carry.
>
> **Neither reached this repository.** jim-mini went on slugging titles by hand at the point of writing the file:
>
> ```python
> slug = s["title"].lower().replace(" & ", "-").replace(" ", "-")
> fn = f'{s["num"]:02d}-{slug}.svg'
> ```
>
> …with nothing checking the result. So the first title containing an apostrophe produced an unaddressable filename and no failure anywhere. I wrote the README reference assuming the sibling repo's fix applied here, which it did not.
>
> ## Two changes, and the second matters more
>
> **One `slug()` and one `filename()`**, ported from QRME. The apostrophe, `?`, `#`, comma and friends are stripped.
>
> **The gallery test this repo never had.** Every referenced screen and watch face exists, every screen is shown somewhere, the numbering skips nothing, and no filename carries a character a URL cannot. A sixth test asserts the slug expression appears **exactly once** in the builder, because the duplication is the actual root cause — two copies that disagree is how the comma reached a filename in QRME.
>
> Mutation-checked by renaming the file back to the broken form: the guard fails two ways, on the unsafe name and on the dangling reference.
>
> A broken image is invisible to whoever wrote it — it renders on somebody else's machine, in somebody else's browser, days later. That is why this is asserted rather than looked at.
>
> 438 tests pass.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #106 — v0.4.0 — membership, the corner pane, and a line no plan stands on

- merged · opened 2026-07-27 · merged 2026-07-27
- `claude/jim-0.3.3` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/106>

> **Cuts v0.4.0.** Seven commits, 432 tests, 75 phone screens, 36 watch faces.
>
> Merged with `main` along the way — #104 and #105 landed while this was in flight, without conflicts.
>
> ## Membership: Basic $20/month, Pro $130/month
>
> `jim/tiers.py`, 4 routes, 25 tests, screens 69, 70, 72–75.
>
> | | | |
> | --- | --- | --- |
> | **Visitor** | free | read a shared page or a scanned medical ID |
> | **Basic** | $20/month | the Guardian itself — conditions, guidance, journal, habits, goals, **and every emergency path** |
> | **Pro** | $130/month | the watch, early warning, specialists, and synthetic agents through the QRME tandem |
>
> ### Nothing that answers an emergency is ever behind a paywall
>
> That is the rule the module exists to keep rather than a caveat on it. A lapsed card is a billing event; a seizure is not.
>
> `tiers.NEVER_GATED` names the alarm path, escalation, the medical ID a paramedic scans, incident history, waivers, and the guidance a person receives *during* an alarm. `capability_for` consults it **first**, so a pattern added to the gated table later cannot reach any of them — and a test plants exactly that mistake, adding a hostile pattern covering **every** path, then asserts each safety route still comes back ungated.
>
> ### The first implementation had this bug
>
> Recorded here rather than quietly fixed, because it is the most important thing in the diff.
>
> `/monitor` was listed as the "proactive monitoring" capability. That reads correctly and is wrong: **`/monitor` is not the predictive feature, it is the ingest.** A sample arrives there, `jim/conditions.py` asks *is something wrong right now*, and a critical reading escalates to the emergency contact.
>
> Gating it meant a Basic member submitting a blood oxygen of 84 received a **402 instead of an escalation** — the paywall standing between somebody and an emergency, indirectly but completely. The suite caught it in `test_critical_escalates_to_emergency_contact`.
>
> So the line moved to where it belongs. What Pro buys is `jim/earlywarning.py`: the trend model that projects a vital toward its threshold and says something is *about to* go wrong before anything is crossed. That is a real feature and a fair thing to charge for. Evaluating a reading somebody just submitted is not — and it is **skipped rather than refused**, so a Basic member gets a real answer about that reading, with `predictive: false` saying plainly what they did not get. The trend point is recorded on every plan, because a history with holes would make the forecast wrong for somebody the day they upgrade.
>
> `/insights` is the one GET gated anywhere across these three products: an insight is not a shop window, it *is* the predictive product and the only door it has.
>
> Every 402 carries `emergency_unaffected: true`, because somebody who has just hit a paywall on a health app should not have to wonder whether they have also lost the alarm. Money is simulated. Cancelling keeps the record, the conditions and every emergency path.
>
> ### Signing up carries the plan
>
> Screens 72–75. The step sits between **45 Emergency Contacts** and **46 All Set**, and the order is the argument: somebody has just handed over the number to ring if they collapse, so the very next screen is the one that says no plan withholds that.
>
> **74 You're on Basic** leads with what still works rather than with features — on a health product that is the thing to say first. **75 This Needs Pro** carries *"Your alarms are unaffected"*.
>
> Walked end to end against the running app: enrolling on Basic locks watch, monitoring, marketplace and synthetic agents; a blood oxygen of 84 still returns `200 critical` with an escalation; an ordinary reading answers with `predictive: false`; pairing a watch returns 402 with `emergency_unaffected: true`; and **with the subscription cancelled to visitor, the critical reading still escalates.**
>
> ## The helper dock
>
> `jim/dock.py`, 5 routes, 15 tests, screen 71. The glances a watch face would carry, in a pane in the bottom corner behind the helper button. It matters more here than in QRME because **the watch is a Pro capability** — so the people most in need of a glance without a wrist are exactly the ones who do not have one.
>
> **It shows and it routes; it never acts** — for QRME's reason and one specific to this product: the surfaces it floats over include a live alarm, and a control in a 168px box beside the button that clears an escalation is a mis-tap during the worst minute of somebody's week.
>
> **But it is never silent about an alarm**, and this is the one place the rule deliberately departs from QRME's. QRME's dock tucks itself away on a surface being broadcast, because a pinned pane is inside every screenshot. The same rule here would hide the thing a person most needs to see — so `ALWAYS_SHOWN` names the alarm face and it opens regardless, with the preference returned as `wanted` rather than overwritten. The alarm face also **cannot be configured out of the pane**: a pane somebody tidied up months ago is not a decision they made about the day it fires.
>
> Not a privacy compromise, and argued rather than assumed: an alarm belongs to the person holding the phone, and JIM-mini has no broadcast surface to leak it into. Where the reasoning differs, the rule differs — rather than being copied because the module next door has one.
>
> ## The Guardian gives the tour
>
> `jim/tutorial.py` — twelve lessons, 6 routes. The third of three guides, and the voice is the difference: QRME's has no name and no face because a tutorial guide with a persona would be the most convincing synthetic profile on that platform. **Here the Guardian already is somebody to the user**, so the walkthrough is in the Guardian's voice rather than a second one.
>
> It never taps anything for you, writes to nothing but the learner's progress, works with no model configured, and renders voice and text from one lesson rather than two scripts.
>
> **Channel 2's screens 65 and 66 had gone missing**, and the thing that found them was the tutorial's own coverage test on its first run: every lesson names the screens it covers, and two numbers had no lesson because two files had no screens.
>
> ## The README video, and the passage
>
> A bare user-attachments URL becomes a full-width player, which made a large black rectangle with a play button the de-facto header. There is no width attribute to reach for — GitHub generates the element from the link — so the only handle is the box it lands in. It now sits in a narrow table cell with the cover illustration beside it. Playback is untouched: still full screen with audio on click.
>
> The blank lines around the URL inside the cell are load-bearing and the comment now says so.
>
> Matthew 7:24–25 and the ark text are at the foot of the README, identical across all three repositories.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code)_

## #105 — Release 0.3.3, and a README that leads with the screens

- merged · opened 2026-07-27 · merged 2026-07-27
- `claude/jim-0.3.3` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/105>

> Cuts **0.3.3** across the suite, and reorders the README so the screens come first.
>
> ## The README
>
> The page led with prose and put the galleries below it, which is backwards: the screens are the part you understand at a glance, and the prose is the part you read only if a screen raised a question.
>
> New shape:
>
> 1. **Title and intro** — unchanged
> 2. **The screens** — desktop app, phone app, and the watch faces
> 3. **What it does** — the capability sections
> 4. **Reference** — Run, Run it on your phone, API, Configuration, Test, all under one heading at the bottom
>
> The Reference block exists so it has an address: a command spotted in a screenshot is in one place at the end rather than scattered through the middle. Those tables are **set smaller**, because they are for looking things up in rather than reading through.
>
> Two implementation notes, since neither is obvious:
>
> - GitHub's markdown sanitiser **strips `style`**, so `<sub>` is the only size control actually available.
> - Markdown is **not processed inside an HTML block**, so the converted cells emit their own `<code>`, `<b>` and `<a>` rather than leaving backticks and brackets to render literally.
>
> ## Release contents
>
> The agent status light: **watch face 36** as the ambient one — three lights, three counts, no task names, for the moments somebody is on their phone and the watch is the only surface that can answer *does this need me* without getting in the way — plus screen 67's grouped Agents view and the corner overlay on screen 68 and every desktop view. Full detail in [CHANGELOG.md](CHANGELOG.md).
>
> Version bumped in all five places (`pyproject.toml`, the `FastAPI(...)` call, `app/package.json`, and both root entries in `app/package-lock.json` — dependency pins left alone), the `[0.3.3]` link definition added, and `[Unreleased]` repointed.
>
> ## What is deliberately not in this release
>
> The held work stays under `[Unreleased]` and is named nowhere in the changelog entry or the release notes. I also checked what GitHub will auto-generate for *What's Changed*: the only PR merged since `app-v0.3.2` is #104, whose title is about the agent light. That is the surface that leaked once before, so it is checked rather than assumed.
>
> ## Verification
>
> - 380 tests pass.
> - The restructure was verified by diffing the prose line-by-line against the previous README: **nothing lost**, the only difference being the new Reference intro.
> - Every generated table was checked for a uniform column count and rendered in a browser to confirm it reads as smaller without losing its code spans or links.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #104 — Agent status light: the ambient watch face, the Agents screen, the overlay

- merged · opened 2026-07-27 · merged 2026-07-27
- `claude/jim-agent-light` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/104>

> One question, answered everywhere: **does this task need me right now?** Green working, amber needs you, red stopped. The meaning is defined once, in QRME's `agentlight.py`, and JIM renders it.
>
> ## Watch face 36 — the ambient one
>
> Three lights, three counts, dimmed at zero. **No agent names and no tap targets.**
>
> This is the piece the round exists for: while somebody is on their phone, the watch is the surface that can show several agents at once without getting in the way. Naming them was the first cut and was wrong — a name is something you read, and reading is the thing a glance cannot do. The footer says *open on your phone*, because that is where the answer lives.
>
> ## Screen 67 — Agents
>
> The same three lights, each a tappable group: what is working, what needs you, what stopped. Somebody opening this *because* amber appeared should not have to scan a flat list for the one that changed. Grouping puts the answer first and the roster second.
>
> ## Screen 68 and the desktop console — the overlay
>
> A pinned strip above the tab bar with the three counts and a way in. A task that reports only on its own screen is one you have to remember to go and check, and amber and red are exactly the states nobody thinks to look for. On the desktop console it rides on **every** view, not just Home — those users have no wrist to glance at, which is the whole reason the overlay exists.
>
> Screens 65 and 66 are deliberately skipped so the held work keeps its numbers and nothing has to be renumbered when it lands.
>
> ## Also
>
> - The README carries the colour table, the reasoning, and a table of the three surfaces with what each shows and why it has that shape.
> - `agent_groups()` length-guards its subtitles — the chevron owns the right edge of the row, and a sub running under it reads as a rendering fault. Caught at build time rather than in a screenshot.
>
> ## Verification
>
> 380 tests pass. Screens rebuilt for iOS and Android (66 × 2) and the desktop console for macOS and Windows; every new screen was rendered to PNG and looked at, which is how the subtitle overrun was found. The length guard was mutation-checked.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #103 — Release prep v0.3.2

- merged · opened 2026-07-27 · merged 2026-07-27
- `claude/jim-v032` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/103>

> Cuts **v0.3.2**. **No functional change to JIM-mini** — no new routes, no
> schema, no behaviour. The version moves because the three products are cut as
> one release.
>
> The round belongs to QRME: its starter gallery now shows each of the 34 profiles
> as the card the app actually gives it, and the one starter that had no source
> material finally has a Field Pack of its own.
>
> ## What stays under `[Unreleased]`
>
> Channel 2, same as 0.3.1.
>
> ## Release mechanics
>
> Version moved in all five places, lockfile's two root entries verified as
> exactly two changed lines. Changelog sectioned, link definition added,
> `[Unreleased]` repointed. README current-release line and table row updated.
>
> **Tag this commit, not the tip of `main`.**
>
> ## Verification
>
> 380 tests green — the same 380, passing the same way. 103 routes, unchanged.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #102 — Renumber this release 0.3.1, not 0.4.0

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/jim-renumber-031` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/102>

> The jump was wrong. 0.2.2 went to 0.3.0 and this round went to 0.4.0, which
> walks through the numbers far faster than the work warrants. **The convention
> from here is to stay in the 0.3.x line and only reach 0.4.0 after 0.3.9.**
>
> ## Why this costs nothing
>
> **No `app-v0.4.0` tag was ever pushed**, in any of the three repositories.
> 0.4.0 existed only as strings in files on `main` — nothing was built, no GitHub
> Release was published, and no installer carries the number. This is a text
> change, not a retraction.
>
> ## What moved
>
> - The five version places, with the lockfile's two root entries verified as
>   exactly two changed lines
> - `CHANGELOG.md` — section heading and both link definitions
> - `RELEASE_NOTES.md` — title, body, and the tag it tells you to push
> - `README.md` — the current-release line, plus a row for this release
>
> ## Verification
>
> 380 tests green, 103 routes. No microphone content in the diff.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #101 — Release prep v0.4.0

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/jim-v040-release` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/101>

> Cuts **v0.4.0**. **No functional change to JIM-mini in this release** — no new
> routes, no schema, no behaviour. The version moves because the three products
> are cut as one release.
>
> ## What did change
>
> - **The README names its version**, with a release table, matching the section
>   added to the other two repositories.
> - **Fixed:** screens 61–64 existed in the repository and nowhere a reader would
>   find them. They shipped in 0.3.0 as files — *What Would Be Shared*, *Specialist
>   Working*, *Find a Clinician*, *Sign to Release* — and were never added to the
>   README gallery, so the four screens illustrating that round's headline feature
>   were invisible on the page describing it.
>
> ## What stays under `[Unreleased]`
>
> Channel 2. Its code is on `main`, but it is not part of a described release —
> these notes say what shipped, not what exists.
>
> ## Release mechanics
>
> Version moved in all five places: `pyproject.toml`, the `FastAPI(...)` call,
> `app/package.json`, and the **two root entries** in `app/package-lock.json` —
> verified as exactly two changed lines, dependency pins untouched. Changelog
> sectioned, link definition added, `[Unreleased]` repointed at `app-v0.4.0`.
>
> **Do not tag until this is merged**, and tag this commit rather than the tip of
> `main`.
>
> ## Verification
>
> 380 tests green — the same 380, passing the same way, which is the point of a
> release claiming no functional change. 103 routes, also unchanged.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #100 — Say what version this is, and what each release actually added

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/jim-readme-release-summary` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/100>

> The README opened on a video and a patent notice and never named a version, so
> a reader could not tell which release they were looking at or what had happened
> across thirteen of them. The changelog has it all, but the changelog is not
> where somebody lands.
>
> ## What changed
>
> - A line at the top naming the current release (**v0.3.0**) and the two products
>   cut alongside it.
> - New **What's in the current release** table — newest first, what each release
>   actually added.
>
> Matches the section added to QRME's README, which is the point: the three are
> cut as one release, so a reader arriving at any of them should be able to answer
> the same question the same way.
>
> ## Scope
>
> README only, one file. The table stops at v0.3.0, which is the current release.
>
> ## Verification
>
> Every relative link in the file resolves, and the new table is well-formed
> (11 rows, 2 columns throughout).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #99 — A second ear: borrow a wearable's microphone

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/jim-second-ear` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/99>

> A phone has one microphone and one foreground claim on it. **While somebody is on a call the Guardian is deaf** — which is precisely when they might want to ask it something, and precisely when it cannot hear them ask. A watch already on the wrist has a microphone nothing else is using.
>
> ## Permission and state, not audio
>
> Capture happens on the device; nothing in this module touches a sample. What the service owns is whether the agent may listen right now, on which device, and a record of when it did — the same division as everywhere else here.
>
> ## Four refusals, and the third is the one that matters
>
> | Refusal | Why |
> | --- | --- |
> | **Only a registered wearable** | A kitchen console's mic is a *room* microphone — always somewhere people talk without thinking about it. Folding the two together lets the easy case argue for the hard one |
> | **Only while the primary is occupied**, reason recorded | A second ear granted for no reason is just a second ear. The reason is what bounds it |
> | **Never on speakerphone** | On an earpiece the wearable hears the wearer. On speaker it hears **the other party too** — someone who is not a user of this product, was never asked, and cannot revoke anything. A microphone the Guardian holds must not become a way to record the person on the other end of somebody else's call. Also refused with others in earshot |
> | **A handover ends, and is recorded** | A listening permission that leaves no trace is one nobody can audit — and this is the permission people most want to check up on. A *refused* handover records nothing, so the history never implies the agent heard something it did not |
>
> `GET /users/{id}/mic` answers "is it listening" in a sentence a person can check, without needing to know which endpoint to ask.
>
> ## The QRME counterpart
>
> `qrme/roommic.py` lends the **same wearable** to a live room's profiles. The same hardware raises a *different* question there, because a room has other people in it — and they're participants, so they *can* be told. That side **discloses** where this side **refuses**: the disclosure is readable by anyone in the room, not by the lender alone.
>
> ## Verification
>
> - **361 tests**, 15 new. Existing 346 unchanged. **100 routes** (was 96).
> - **Mutation-checked**: allowing speakerphone, and allowing a stationary room microphone to be lent, each fail the test that forbids them.
>
> Companion: qrme `claude/qrme-starter-grounding` (which also carries the starter grounding and the bubble-glow fix).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #98 — Release prep v0.3.0

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/jim-release-v0.3.0` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/98>

> Cuts **v0.3.0** across all three products.
>
> ## What's in it
>
> **The round where the Guardian reaches a person.** It could delegate a condition to a synthetic specialist; now it can hand over a task that outlives the app being closed, and find a **real clinician** near the user.
>
> - **Reaching a real clinician** (#97) — maps a condition to a care area, matches on a coarse self-declared locality, and asks QRME to prepare. **JIM never holds the credential and never relays the assertion**: it goes from the user's device to QRME directly, because a guardian standing in the middle of the exchange that proves its own user was present would defeat the point of collecting it. JIM stores a handle, not the summary.
> - **Handing a specialist a task** (#96) — deliberately **not** on the emergency path: `escalation.decide` resolves in one call and must keep doing so. JIM keeps status only; the drafts stay in QRME.
> - **Contribution preview and revoke** (#96) — closes a promise the settings screen has been making since the cloud tier shipped. One payload builder serves both the preview and the real send, so the preview can't drift into describing something the send doesn't do.
>
> Screens **61–64**: What Would Be Shared, Specialist Working, Find a Clinician, Sign to Release.
>
> ## Release mechanics
>
> Version bumped in **all five places**:
>
> | | |
> | --- | --- |
> | `pyproject.toml` | ✅ |
> | `FastAPI(...)` in `jim/api.py` | ✅ |
> | `app/package.json` | ✅ |
> | `app/package-lock.json` top-level | ✅ |
> | `app/package-lock.json` → `packages` → `""` | ✅ |
>
> `[0.3.0]` link definition added, `[Unreleased]` repointed to `app-v0.3.0`.
>
> ## Verification
>
> - **346 tests green**, 34 new this release. **96 routes** (was 87 at 0.2.2). **128 screens** (was 120). `create_app().version` reads `0.3.0`.
> - All **14** changelog headings checked against their link definitions.
> - Siblings in the same pass: qrme **589**, pdi **192**.
>
> ## After merge
>
> The `app-v0.3.0` tag has to come from you — the git proxy refuses `refs/tags/*`. `sync-release-notes.yml` lays `RELEASE_NOTES.md` over the release body once the build finishes.
>
> Companion PRs: qrme #146, pdi `claude/pdi-release-v0.3.0`.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #97 — Reach a real clinician through the tandem

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/jim-clinician-referral` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/97>

> **Stacked on #96** — these share `api.py`, `db.py` and `qrme_client.py`, and splitting them would have been a fictional history. Base retargets to `main` once #96 merges; the diff shown here is this change alone.
>
> ## What it adds
>
> The tandem could hand a condition to a *synthetic* specialist, and (in #96) a multi-step task. Neither reaches a human being. This maps a condition to a care area, finds real clinicians near the user, and asks QRME to assemble the summary and raise the signature that would release it. QRME's half is qrme#145.
>
> ## JIM never signs, and that is the point
>
> The signature is a WebAuthn assertion against **QRME's** relying party, over a challenge QRME minted. So the Face ID prompt belongs to QRME, and the assertion travels from the user's device to QRME **directly**.
>
> A guardian product that could mint the consent for releasing its own user's health record would be exactly the wrong shape. Standing in the middle of the one exchange that exists to prove the user was present would defeat the point of collecting it.
>
> JIM stores a **handle** — not the summary, not the signature, not the link. A test asserts the transcript never reaches JIM's database at all.
>
> ## Locality is a town, not a position
>
> `sources` already carries a consented `location` feed, and this deliberately doesn't read it. Live position is a stream; matching a clinic needs a place name. A user typing "Leeds" once is a smaller disclosure than a product inferring it continuously — and it's all the match can use anyway.
>
> Condition→area routing is coarse on purpose (`anxiety` → `mental_health`, everything unmapped → `medical`). Anything finer would be JIM guessing at a clinical taxonomy it has no standing to define.
>
> ## Degrading well
>
> Standalone JIM, an unregistered area, and a missing tandem link each answer plainly with a reason rather than raising. The caller here is often a screen somebody opened while unwell — "none found" degrades better than a traceback.
>
> ## Screens
>
> - **63 · Find a Clinician** — expertise first, then near you.
> - **64 · Sign to Release** — the moment the whole path exists for. Every line is a real field of what would be sent.
>
> Both rendered before shipping; 63 had the same pill/text collision that bit screens 62 and the chat dot in earlier rounds, fixed by moving the long string to the subtitle line. It doesn't show up in a diff.
>
> ## Verification
>
> **346 tests**, 11 new. Existing 335 unchanged. **96 routes** (was 92). **128 screens** (was 124).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #96 — Contribution preview and revoke; hand a specialist a task

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/jim-contribution-preview-and-task-handoff` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/96>

> Two gaps, both where a promise outran the code.
>
> ## 1. The screen promised a preview the API couldn't serve
>
> JIM's settings screen has offered *"Contribute data — preview before it leaves"* since the cloud tier shipped. `cloud.contribute` posted a payload, returned a bool, and **wrote nothing down**. So:
>
> - **there was no preview** — nothing could answer; and
> - **"revocable" meant only "stoppable"** — turning the flag off stopped future sends, while everything already contributed stayed at the gateway with nothing naming it.
>
> Health data makes both worse. Someone deciding whether to share guidance outcomes is entitled to the actual bytes, not a description; and a decision they can only apply going forward isn't the consent the screen implies.
>
> **One payload builder, used by both paths.** The preview calls the same function the real send calls rather than reconstructing something that looks like it. A separately-assembled preview is a *description* of the payload, and descriptions drift from what they describe — the exact failure this endpoint exists to correct. A test pins them together.
>
> Two smaller judgements, both tested:
>
> - **A refused post is not logged.** Recording it would offer a revoke button for data that never left.
> - **Revoke reports its two halves separately.** Local rows are marked whether or not the gateway answered. Leaving them unmarked on an outage would show a user their data as still shared after they revoked it; marking them and claiming success would assert a deletion that never happened.
>
> What leaves is unchanged — condition, severity, rating; never ids, names, notes, or raw biometrics. Contributions now carry a random `ref` so an item can be deleted at the gateway without deanonymizing the person revoking.
>
> ## 2. A specialist could be sent a turn, but not a task
>
> `_tandem_guidance` sends one message and gets one reply — right for *"say something supportive"*, wrong for *"read what we have, draft the summary, hold it until somebody confirms"*. QRME runs the second as a workflow (see qrme#143); `jim/handoff.py` is JIM's side.
>
> - **Never on the emergency path.** `escalation.decide` resolves in one call and must keep doing so — multi-step work is by definition slower than what it would block. Nothing here is reachable from `monitor`.
> - **Starting one is explicit.** Having a detection kick off a workflow itself reads well and is the wrong default: it would let a noisy reading commit a specialist to unattended multi-phase work over the user's vaulted material.
> - **JIM keeps status only.** The drafts stay in QRME under its own moderation and the user's capability token. Mirroring them here would quietly make JIM a second store of somebody's generated health correspondence — a test asserts the phase *contents* never reach JIM's database.
> - A narrower owner policy **narrows the plan** rather than failing it; an empty intersection is a **refusal**, because a workflow with no phases completes instantly and reads as success.
>
> ## Screens
>
> - **61 · What Would Be Shared** — the screen behind that settings row. Every line is a real field of the payload rather than a description of one.
> - **62 · Specialist Working** — a handed-off task mid-flight.
>
> Both were rendered and fixed before shipping: 61's destructive button was passing a tone that doesn't exist (`"red"` → the neutral fallback, so a delete button didn't look like one), and 62 had a pill colliding with the row text. Neither shows up in a diff.
>
> ## Verification
>
> - **335 tests**, 23 new. Existing 312 unchanged.
> - **92 routes** (was 87). **124 screens** (was 120).
> - **Mutation-checked** — each fails the test that forbids it: logging a refused send; claiming gateway deletion regardless of the answer; treating an empty phase intersection as a startable task.
> - One pre-existing assertion updated: `test_guidance_outcome_contribution` pinned the payload to exactly five keys, and `ref` is a sixth. It now asserts the ref exists and carries no identity, keeping its original guarantees intact.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #95 — Release prep v0.2.2

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/jim-release-v0.2.2` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/95>

> Cuts **v0.2.2** across all three products. A documentation release — **no code changed**: no new routes, no schema, no behaviour, and nothing about how the Guardian decides anything.
>
> ## What's in it
>
> - **Three releases of changelog link definitions were missing.** `[0.1.9]`, `[0.2.0]` and `[0.2.1]` had headings but no definitions, so three shipped versions rendered as literal `[0.2.1]` bracket text, and `[Unreleased]` still compared against `app-v0.1.8` — presenting a three-release diff as though it were an empty one.
>
> - **The release checklist was why.** `docs/releasing.md` step 1 said to move the `Unreleased` items and date the heading, and stopped — never mentioning the link definition at the bottom of the file. The step was skipped three releases running by someone following the instructions correctly. Step 2 was wrong the same way: it named two version locations when there are five. (Shipped in #94.)
>
> The `0.1.5` and `0.1.6` entries still point at commits rather than tags. That is deliberate and explained in `docs/releasing.md`; untouched here.
>
> ## Release mechanics
>
> Version bumped in **exactly five places**, per the checklist this round fixed:
>
> | Location | |
> | --- | --- |
> | `pyproject.toml` | ✅ |
> | `FastAPI(...)` in `jim/api.py` | ✅ |
> | `app/package.json` | ✅ |
> | `app/package-lock.json` top-level `"version"` | ✅ |
> | `app/package-lock.json` → `packages` → `""` | ✅ |
>
> Dependency versions in the lockfile untouched.
>
> ## Verification
>
> - **312 tests green** — the same 312, passing the same way, which is the point of a release claiming no functional change.
> - **87 routes**, also unchanged. `create_app().version` reads `0.2.2`.
> - All **13** changelog headings checked against their link definitions — 13 for 13, including the new `[0.2.2]`. `[Unreleased]` repointed to `app-v0.2.2`.
>
> ## After merge
>
> The `app-v0.2.2` tag has to be pushed by you — the git proxy here refuses `refs/tags/*` writes. Leave the release body empty when you create it; `sync-release-notes.yml` lays `RELEASE_NOTES.md` over the top once the build finishes.
>
> Companion PRs: qrme #142, pdi `claude/pdi-release-v0.2.2`.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #94 — Fix the changelog release links and the checklist that lost them

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/jim-changelog-release-links` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/94>

> Documentation only. No behaviour change — 312 tests pass unchanged.
>
> ## The broken links
>
> `[0.1.9]`, `[0.2.0]` and `[0.2.1]` had headings but no link definitions, so three shipped versions rendered as literal `[0.2.1]` bracket text rather than linking to their releases. `[Unreleased]` still compared against `app-v0.1.8`, presenting a three-release diff as though it were an empty one.
>
> ## Why it happened three times running
>
> `docs/releasing.md` step 1 said to move the `Unreleased` items under the new heading and date it, and stopped there. It never mentioned the link definition at the bottom of the file — so the step was skipped by somebody following the instructions correctly.
>
> Nothing complains when you miss it. The heading renders fine without a definition, and the damage shows up hundreds of lines away from where the edit was made. Step 1 now shows the two lines to add, and says plainly that this is the step that gets missed.
>
> ## Step 2 was wrong in the same direction
>
> It named `pyproject.toml` and `app/package.json`. The version string actually lives in **five** places:
>
> | | |
> | --- | --- |
> | `pyproject.toml` | named already |
> | `app/package.json` | named already |
> | the `FastAPI(...)` call in `jim/api.py` | **omitted** |
> | `app/package-lock.json` top-level `"version"` | **omitted** |
> | `app/package-lock.json` → `packages` → `""` → `"version"` | **omitted** |
>
> Those three had to be rediscovered every round. The step now names all five and warns off the dependency pins in the lockfile, which look identical to the two that matter.
>
> ## Across the three repos
>
> All three had drifted identically — every one stopped at `0.1.8`. Companion PRs: qrme #141, and pdi on `claude/pdi-changelog-release-links`.
>
> The `0.1.5` and `0.1.6` entries still point at commits rather than tags. That is deliberate and documented in `docs/releasing.md`; those two are untouched here.
>
> ## Verification
>
> `JIM_CONSOLE_DIR=/nonexistent python3 -m pytest -q` → **312 passed**, unchanged.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #93 — Release prep v0.2.1

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/jim-mini-v0.2.1` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/93>

> Version strings in the five places, changelog cut, release notes rewritten. All three products cut together at this version.
>
> ## What this release carries
>
> **Signal confidence for biometrics.** `escalation.decide` has always accepted a `confidence`, but only forecasts ever supplied one — it gated *predictions* and never *measurements*, so a reading was a fact by virtue of arriving. A reading the system doesn't trust now caps at `check_in` instead of ringing an emergency contact.
>
> Confidence drops only on evidence the **sensor** misbehaved — never because a value is clinically abnormal. That distinction was learned the hard way: the first draft muted a lone SpO2 of 84, the exact reading the ladder exists to carry.
>
> Plus the two fixes that came with it: the escalation decision is authoritative over raw severity, and a rota typo can no longer take the escalation path down.
>
> ## Verification
>
> **312 tests green. 87 routes.** Mutation-checked: letting the confidence cap clip the crisis floor, and letting an impossible reading be corroborated, each fail the test that forbids them.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #92 — How much to trust a reading

- merged · opened 2026-07-26 · merged 2026-07-26
- `claude/jim-signal-confidence` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/92>

> The last standing gap: the Guardian assumed clean input.
>
> `escalation.decide` has always accepted a `confidence`, but **only forecasts ever supplied one** — it gated *predictions* and never *measurements*. So a reading was a fact by virtue of arriving.
>
> Consumer biometrics are not like that. An optical sensor loses skin contact, a chest strap catches a motion artifact. The characteristic failure is not a small error but a **plausible-looking number that is completely wrong**, with the alarming direction as likely as the reassuring one. At the top of this ladder is a phone call to somebody's daughter, and an alert that is usually wrong spends the only thing escalation has: her willingness to pick up.
>
> ## Confidence drops only on evidence the *sensor* misbehaved
>
> An impossible value, a jump no body could make between two readings, or the device reporting its own poor contact. **Being clinically abnormal never lowers it.**
>
> That distinction is the whole design, and I got it wrong first. The initial draft graded anything outside the ordinary range as suspect — which muted a lone SpO2 of 84, *the exact reading this ladder exists to carry*. A pre-existing test caught it. The rule is now stated the other way round: an alarming reading is signal, not noise.
>
> ## A poor grade caps rather than silences
>
> Escalation stops at `check_in`. *"We got an odd reading, are you alright?"* is the honest sentence when the honest answer is that we do not know — and asking is also how the reading gets corroborated. Dropping the sample would be the same mistake pointed the other way, because the noisy reading is sometimes real.
>
> ## Words are never noise
>
> The crisis floor is applied **after** the cap and is never clipped by it. Nor can words make a heart rate of zero true: two impossible readings are not two witnesses but one broken device agreeing with itself, so corroboration only runs between *possible* readings.
>
> A fault is phrased as a fault — *check the strap* — because telling somebody whose sensor fell off that we are worried about them is how people learn to disbelieve the thing.
>
> A baseline is the one place a reading is dropped outright: it is a long-lived average of what normal looks like, so it takes only ordinary values. A merely-possible 195bpm is a real event worth detecting and a terrible thing to average into "resting".
>
> ## Also fixed, and load-bearing for the above
>
> **The escalation decision was advisory while raw severity was in charge.** `monitor` reached out whenever `detection.severity == "critical"`, so the tree could resolve a disbelieved reading to `check_in` and the contact was rung anyway. The tree is authoritative now.
>
> No behaviour changes for a trusted critical — its floor is `notify_contact`, so the comparison is exactly equivalent — and a test asserts that directly.
>
> ## Verification
>
> **312 tests green (15 new).** Mutation-checked: letting the cap clip the crisis floor, and letting an impossible reading be corroborated, each fail the test that forbids them. `docs/guardian-internals.md`'s *"Confidence & sensor fusion **[planned]**"* is now **[implemented]**, with debounce left as the remaining planned item.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #91 — Release prep v0.2.0

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/jim-mini-v0.2.0` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/91>

> **No functional changes to JIM-mini in this release.** The round was next door, where PDI grew a per-tenant on-call roster — closing the gap this repo's own `jim/rota.py` had left visible in the comparison. The three products version as one, so this repo cuts the same number in the same pass; `docs/releasing.md` says an empty round says so plainly rather than padding.
>
> ## Why 0.2.0 rather than 0.1.10
>
> The 0.1.x line ran from a Guardian that monitored and escalated, to one with a life layer, an escalation ceiling a stranger's tap cannot raise, care beacons on the objects around a watched person, a workplace relay for lone workers, a rota that knows who is actually on at 2am, and an escalation that reaches a human rather than writing a name in a table.
>
> That is a different product from 0.1.0. 0.1.10 would have undersold it.
>
> ## What is in here
>
> Version strings in the five places, changelog cut, release notes rewritten — plus the workflow race fix that merged earlier today, which is the only functional change this repo carries into 0.2.0.
>
> ## Verification
>
> **297 tests green** — the same 297, passing the same way, which is rather the point of a release claiming no functional change here. 87 routes.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #90 — Only one workflow writes the release body now

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/jim-mini-release-body-race` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/90>

> Two of them did.
>
> `desktop-release.yml` published the release with `body_path: RELEASE_NOTES.md` — the file **verbatim**, *"Ready-to-paste body for the GitHub Release…"* preamble and all — while `sync-release-notes.yml` published the same file with that preamble stripped. Both fired on the same tag push, and the installer build finished two to four minutes after the sync had already got it right.
>
> The build always won. Every release since the sync workflow existed has shipped the maintainer preamble until somebody re-ran the sync by hand — v0.1.9 included.
>
> The de-duplication logic already in the sync workflow — *"several releases carry it twice from a body that was pasted over one that already had it"* — is scar tissue from this, treating the symptom of a race nobody had spotted as a race.
>
> ## Fixed at both ends
>
> **The build stops writing a body.** It attaches installers and lets GitHub generate the changelog.
>
> **The sync stops racing.** It triggers on `workflow_run` when the build **completes**, so the curated notes are the last write by construction:
>
> ```yaml
> workflow_run:
>   workflows: ["Guardian release"]
>   types: [completed]
> ```
>
> The tag comes from `workflow_run.head_branch`, and the job is guarded so manual artifact-only builds don't trigger a pointless sync. `types: [completed]` rather than success-only is deliberate — a build that fails *after* creating the release is when a wrong body is least likely to be noticed.
>
> ## Also
>
> [docs/releasing.md](docs/releasing.md) says to leave the release body empty when tagging, records which workflow owns it, and names the neighbouring trap: tag names are case-sensitive to `tags: ["app-v*"]`, so `App-v0.1.9` silently triggers nothing.
>
> ## Verification
>
> Both workflow files parse as YAML, and the `workflows:` name is checked against this repo's actual `name:` — it is `Guardian release` here, not `Desktop release`, and a mismatch would have failed silently.
>
> **297 tests green.**
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #89 — Screen 60 was advertising the roster this round replaced

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/jim-relay-screen` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/89>

> Found on a sweep before the v0.1.9 tags go up.
>
> Screen 60 (*Workplace Relay*) carried the card:
>
> > **Roster in order** · night-tech → supervisor → lead
>
> That is the flat list — the exact behaviour `jim/rota.py` was built to fix — drawn last round and still sitting in the README gallery. A screen is a claim, and this one had become false.
>
> ## Now
>
> | | |
> |---|---|
> | **On shift, not in order** | 18:00–06:00 · Friday's night |
> | **Paged, then accepted** | a webhook, not a note in a table |
>
> The second replaces *"Accepted, not cleared"*, whose claim it keeps (accepting is still named) while adding the thing that was missing: the page actually goes out.
>
> Kept to **five cards**, which is this gallery's maximum — no screen has six — so the rota and the page displace the two cards whose claims they subsume, rather than being appended past the fold.
>
> ## Verification
>
> Rendered in a browser and looked at, not trusted to parse. `clock` would have been the obvious icon for a shift and **is not in this repo's icon set** — it would have drawn a bare dot, the same defect found on screens 57 and 60 last round. It uses `watch`.
>
> 126 SVGs parse. **297 tests green.**
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #88 — A rota typo must not take down the escalation path

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/jim-rota-typo-guard` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/88>

> A defect I shipped in #87, found on a sweep before the v0.1.9 tags go up.
>
> `RotaError`'s own docstring said *"Raised at load, never at 3am."* There is no load step — nothing reads the rota at start-up — so it was raised at **exactly** 3am.
>
> ```
> JIM_SITE_ROTA='[{"name": "Dana", "days": "funday"}]'   # typo for "sunday"
>
> POST /users/{id}/alarms/{id}/escalate  ->  RotaError: unknown day 'funday'
> GET  /relay/roster                     ->  RotaError: unknown day 'funday'
> ```
>
> One typo propagated out of `relay.roster()` and turned the escalation endpoint into a 500 — the one path whose entire job is getting somebody help, failing only *after* an alarm was already open. That is the worst possible moment to discover a config mistake, and there was no earlier moment available.
>
> ## The fix
>
> `rota.read()` returns `(entries, error)` and **never raises**. `on_now()` and `order()` go through it, so an unreadable rota is ignored, `JIM_SITE_ROSTER`'s flat names take over (and `DEFAULT_ROSTER` if that is unset), and somebody is still woken.
>
> `entries()` keeps raising and is no longer on any live path.
>
> ## Degrading is not hiding
>
> That distinction is the whole design here, and it is the same one this feature already makes about an unknown timezone.
>
> | surface | behaviour |
> |---|---|
> | `POST …/escalate` | degrades, and reports `rota_error` on the result |
> | `GET /relay/roster` | degrades, and reports `warning` |
> | `GET /relay/rota` | **422, still strict** |
>
> The validation surface stays strict deliberately: degrading on the endpoint an operator uses to *check* their rota would hide the exact thing they came to find.
>
> `next_free_slot_warning()` is renamed `problem()` — which is what it does — and now reports an unreadable rota ahead of the timezone warning, since a rota being ignored entirely is the larger silence.
>
> ## Verification
>
> **297 tests green (4 new).** Mutation-checked: restoring the raise fails three of the four. Also corrects JIM's test count in `RELEASE_NOTES.md`, `CHANGELOG.md` and `docs/tandem.md` (293 → 297), keeping the three copies of the shared doc byte-identical.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #87 — A rota that knows who is on, an escalation that sends, and v0.1.9

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/jim-rota-and-paging` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/87>

> Two gaps the workplace relay had been carrying, both documented as deliberate. One of them was not defensible.
>
> ## A flat list pages the day person at 2am
>
> `JIM_SITE_ROSTER` was a list of names worked top to bottom, every time, and `relay.py`'s own comment defended it: *"a rota with shift patterns is a scheduling product and pretending otherwise would hide how little this knows."*
>
> Honest, but wrong about the size of the gap. The relay exists for **night shift** — lone workers, plant rooms, single-staffed sites. Getting *who is on right now* wrong at 3am is not a degraded feature; it is the feature failing in the hour it was built for.
>
> ## `jim/rota.py` is deliberately small
>
> Named people, the days they work, the hours, and `JIM_SITE_TZ`. No leave, no swaps, no fairness, no recurrence grammar. Three things it does get right, because each is a way of paging the wrong person:
>
> - **Shifts cross midnight.** `18:00–06:00` is the shift this is all about, and `start <= now <= end` is false for **every minute of it**. A wrapping shift is two intervals and belongs to the day it *started*: at 02:00 on Saturday it is Friday's night worker on the floor, not the weekend rota.
> - **A site is somewhere.** Without a timezone a rota written in local time is evaluated in UTC, shifting every boundary by the offset — and by a *different* offset in summer, so it would look correct for half the year. An unrecognised zone is named in `GET /relay/roster`'s `warning` rather than silently treated as UTC.
> - **A rota has gaps.** Nobody rostered at 4am on a bank holiday is a real state. The relay works the whole rota — better to wake the wrong person than nobody — and reports `on_shift: false` on the escalation **and in the page itself**, so whoever it wakes knows they were a guess.
>
> `GET /relay/rota` answers *who would you page right now?* in the afternoon, rather than leaving it to be discovered at 3am. `JIM_SITE_ROSTER` still works and still means plain names, always on — a test asserts the old configuration is unchanged.
>
> ## And `escalate` sent nothing
>
> "Notified" meant a row in `events` saying somebody had been notified, while nothing had left the building — so the loop the relay is built around (*keep going until a human accepts*) could never close on its first step.
>
> `jim/notify.py` posts a signed envelope to `JIM_NOTIFY_URL` and stops; the SMS gateway or pager behind it is the deployment's, and the envelope matches PDI's shape so one receiver can take both. An unreachable responder sets `reached_somebody: false` **and** `escalate_again_now`, because *waiting on a human* and *waiting on a human who was never told* need different next moves, and only the first should wait.
>
> ## Incident scope survives the trip out of the building
>
> A webhook is the easiest place in the system to turn an incident into a health record — *"just add the name so they know who to look for"* is a reasonable-sounding sentence that would undo the whole promise.
>
> So the envelope is built by copying named fields **out of** `relay.incident`, never by stripping fields from a user record, and not even the finder's words go out. A test reads the whole envelope as one string and looks for the name, birthdate, contact number, resting rate and the finder's message in it.
>
> ## The ceiling did not move
>
> A notification channel is not a siren. A test runs the rota to exhaustion to prove `notify_contact` still caps it, and that the relay still refuses to call emergency services on anyone's behalf.
>
> ## Also
>
> `docs/tandem.md` is byte-identical across the three repos again — this copy described the suite gateway's erase, export and consent as `[planned]` when they had shipped, so a reader here was told cross-app deletion did not exist. `docs/diagrams/tandem-flow.svg` is generated now.
>
> ## Release prep v0.1.9
>
> Version strings in the five places, changelog cut, release notes rewritten. All three products cut together at this version.
>
> ## Verification
>
> **293 tests green (20 new). 87 routes.** The new tests were mutation-checked: replacing the wrapping-shift logic with the naive comparison fails five of them, and leaking the finder's words into the envelope fails the scope test.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #86 — A phone that scans a care beacon gets a page, not JSON

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/jim-scan-page` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/86>

> ## Why
>
> `GET /c/{id}` answered JSON, so a neighbour scanning a fridge magnet got a wall of braces. `jim/landing.py` serves HTML there; the JSON moved to **`/c/{id}/card`**.
>
> ## The order is the design
>
> **Stage one is the whole page**: a first name, one sentence, and a button. The instruction to dial sits *above* the button in the document and is the loudest thing on the screen — the one mistake that matters here is somebody waiting for a page instead of calling.
>
> **The Medical ID is not in the served HTML at all.** It arrives in the alarm's own response and is rendered in place, so there's nothing on the page to reveal early even by mistake. A test asserts the name, resting rate, conditions and contact number are absent from stage one.
>
> For a minor the server returns `medical_id: None`, and the page renders only what it's handed — so stage two simply never appears. No second check to forget.
>
> ## What the page has to survive
>
> One self-contained document, inline everything, no fetch it has to wait on: somebody may be reading this kneeling next to a person on the floor, on cellular, from cold. The alarm posts to a **relative** URL, since an absolute one from `JIM_PUBLIC_URL` breaks every LAN scan.
>
> The entrance animation moves `transform` only and honours `prefers-reduced-motion`. Fading `opacity` from zero — the obvious way to write it, and what I wrote first — means a browser that drops the animation shows a blank card, on a page whose entire job is being legible in one second.
>
> ## A test I had to correct, not the code
>
> I asserted `"MEDICAL ID"` was absent from stage one. It's present — as a *label* inside the script that builds stage two once the alarm returns. That scaffolding holds no data, so the assertion was testing the wrong thing. The claim is about the values, and the test now names them explicitly.
>
> ## Changes
>
> | | |
> |---|---|
> | `jim/landing.py` | new — the page |
> | `jim/api.py` | `/c/{id}` → HTML, `/c/{id}/card` → JSON |
> | `jim/tests/test_beacons.py` | JSON assertions repointed, 8 page tests added |
> | `docs/beacons.md`, `README.md`, `CHANGELOG.md` | the "not built" caveat removed |
>
> ## Verification
>
> **273 tests green** (was 265). Both stages rendered in headless Chromium at 390×844 and inspected — stage two by replaying the real alarm response through the page's own script, so what I looked at is what a responder would see.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #85 — README: lead with the Guardian teaser video

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/jim-readme-video` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/85>

> ## What this is
>
> The 15-second Guardian teaser at the top of the README, above the cover illustration.
>
> https://github.com/user-attachments/assets/eab7d192-7b18-464d-9b67-bd512ae87957
>
> ## Two constraints, both invisible until they fail
>
> Written into a comment beside the URL so the next person doesn't undo them by tidying up.
>
> **A video committed into the repo cannot play.** GitHub's markdown sanitizer strips `<video>`, and image syntax pointing at an `.mp4` renders broken — there is no relative-path route to a player. The only thing that works is a `user-attachments` URL, **bare, on its own line**. That's why it looks like a stray URL in the source and must not be wrapped in link syntax or folded inline.
>
> **The file is H.264/AAC, not the HEVC original.** GitHub accepts HEVC in a `.mov` quite happily — and then Chrome and Firefox can't decode it. It plays on Safari and is a dead black box everywhere else: a silent failure that looks fine to whoever uploaded it and broken to most visitors. Transcoding also took it from **6.3 MB to 2.8 MB**, well under the 10 MB attachment limit, with `+faststart` so playback begins before the whole file arrives.
>
> ## Why the cover stays
>
> Directly beneath the video. Outside github.com — a mirror, a package page, anywhere else a README gets rendered — the video degrades to a plain link, and `assets/cover.svg` is what carries the page there.
>
> ## Verification
>
> Checked that the URL sits bare on its own line with blank lines either side, unwrapped by link or code syntax — the exact shape GitHub requires to render a player. I could not fetch the asset itself from this sandbox (the agent proxy refuses non-repo-scoped `github.com` paths, returning its own 403), so the confirmation that it plays is the rendered comment on #84, not something I verified directly.
>
> No code touched; the suite is unaffected (265 tests, unchanged).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #84 — Generate the four README illustrations instead of hand-building them

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/jim-generated-art` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/84>

> jim-mini-teaser.mp4
> ## Why
>
> `cover.svg`, `guardian-tandem.svg`, `life-layer.svg` and `embodiments.svg` were hand-built one-offs and had aged the way hand-built one-offs do — drawn **before** the escalation ceiling, care beacons, the workplace relay, the family oversight tiers and the rated robot first-aid roles existed, and still showing an early product several releases later.
>
> ## What changed
>
> `tools/build_assets.py` generates all four from the same palette constants `docs/screens/build.py` uses, so they cannot drift away from the screens they sit above. Dependency-free, stdlib only.
>
> What they say now is what the product does:
>
> - **cover** draws the escalation ladder as an actual ladder, with the `notify_contact` ceiling annotated on the rung it caps and the reason written beside it — *a stranger's tap never dispatches an ambulance*
> - **guardian-tandem** states the line that matters most rather than implying it: crisis handling never routes through a synthetic profile, tandem or not — and neither absence (QRME, PDI) degrades safety
> - **life-layer** drops the six identical *"consent required · revocable · yours"* straplines, which had become a motif nobody reads, and states it once in the footer
> - **embodiments** keeps assist / perform / autonomous as the three rated roles and gives the AED its own line, because *"a robot never delivers the shock"* is the sentence that stops the rest being misread
>
> ## Verified by looking
>
> Each rendered to PNG and inspected, not trusted to parse. That's how the repeated strapline on life-layer got caught — it's valid SVG and reads as lazy.
>
> ## Verification
>
> 172 SVGs parse; every README image reference resolves on disk. No application code touched, so the suite is unaffected (265 tests, unchanged).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

### Comment — davidsbianchi1984, 2026-07-25

> jim-mini-teaser.mp4

### Comment — davidsbianchi1984, 2026-07-25

> jim-mini-teaser.mp4
>
> https://github.com/user-attachments/assets/eab7d192-7b18-464d-9b67-bd512ae87957

## #83 — Build care beacons and the workplace relay

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/jim-care-beacons-build` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/83>

> ## What this is
>
> Implements the design merged in #81 — `jim/beacons.py`, `jim/relay.py`, a `ceiling` in `jim/escalation.py`, two tables, thirteen routes, twenty-five tests.
>
> A printed QR goes on the things around a watched person — a fridge door, a wristband, the frame of a walker — and a stranger who finds it can raise whoever is watching.
>
> ## Part one — the beacon
>
> **The alarm comes before the disclosure.** Stage one is a first name, one sentence and a button. Raising the alarm is the act that turns a passer-by into a responder, and *that* is what earns them the Medical ID. QRME's desk beacon in reverse, because health is not a shop sign — and the gate is affordable precisely because the ungated path already ships on the person's own body, which is what `/medical-id/{token}` is for.
>
> **A beacon reports watch status, never subject status.** No health state and no location, ever: *is this person OK right now* is precisely the question a stalker is asking. Tested by serializing the whole card and searching it for the birthdate, the contact number, the label and the placement note — rather than checking the handful of fields somebody remembered to omit.
>
> **`notify_contact` is now a ceiling as well as a floor.** `escalation.decide` gained a `ceiling` argument — the first rule in that module that *lowers* a tier, and it only ever applies to a caller who is not the user.
>
> This is not decorative: a `critical` severity **bases at `emergency_services`**, so the ceiling is the thing standing between an anonymous tap and a dispatch. When it clips a floor it says so — `clipped_by_ceiling`, `call_emergency_services_yourself` — rather than quietly returning something lower, because the need did not vanish; it moved to the person standing there, who is faster than any escalation. A test drives `crisis=True` (the hardest floor in the module) into the ceiling and asserts where it lands.
>
> Existing callers pass no ceiling and are unchanged, pinned by a regression test across every severity × sensitivity.
>
> **The cooldown coalesces rather than drops** — a second finder's words join the open alarm, since two people finding the same casualty is the case this exists for. **A minor's beacon** is guardian-issued, routes to the guardian, and never opens the clinical stage to anyone.
>
> ## Part two — the workplace relay
>
> For lone and remote workers, where `notify_contact`'s assumption of *a contact who answers* fails.
>
> It works the roster in order (and doesn't repeat), distinguishes **accepted** — somebody is coming — from **cleared**, refuses an anonymous acceptance (*"someone accepted it"* is the thing it exists to stop being enough), and reports an exhausted roster rather than going quiet. Still without dispatching.
>
> **Incident scope, never person scope.** The payload is built from the alarm rather than the person, so it carries no name, condition or history — asserted by searching the serialized incident for all of them. The employer bought the deployment; that does not entitle them to what is inside it.
>
> ## Found while verifying the screens
>
> I rendered the two new screens and looked at them rather than trusting the SVG to parse — which turned up **nine pre-existing defects** in the existing set:
>
> - four subtitles running outside their card (worst: *Parent Setup*'s "cautious sensitivity · parent is the emergency contact", well past the phone frame)
> - five titles colliding with their own pill
> - **`icon="lock"` is not in this repo's icon set at all** and had been rendering as a bare dot on *Parent Setup*
>
> All fixed, plus a check that every icon a screen names actually exists. My first pass at the new screens had the same class of bug — a `stat=()` that JIM's `card_block` doesn't support, silently dropped — so the calibration was measured against real renders, twice.
>
> ## Honest gaps
>
> In the doc and the README, not just here:
>
> - **No HTML scan page.** `GET /c/{id}` returns JSON — useful to an app, raw to a phone.
> - **No notification transport.** `escalate` records who was notified; JIM rings nobody. "Notified" currently means "written down".
> - **No shift awareness.** `JIM_SITE_ROSTER` is a list of names in order, not a rota.
>
> ## Changes
>
> | | |
> |---|---|
> | `jim/beacons.py`, `jim/relay.py` | new |
> | `jim/escalation.py` | `ceiling` — the first rule that lowers a tier |
> | `jim/db.py` | `care_beacons`, `beacon_alarms` |
> | `jim/api.py`, `jim/models.py` | 13 routes + schemas |
> | `jim/tests/test_beacons.py` | 25 tests |
> | `docs/screens/` | screens 59–60, plus 9 overflow fixes |
> | `docs/beacons.md`, `README.md`, `CHANGELOG.md` | design → shipped |
>
> ## Verification
>
> 265 tests green (was 240), 107 routes, 168 SVGs parse. New screens rendered to PNG and inspected on both platforms.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #82 — sync-release-notes: read the tag's notes, and stop duplicating What's Changed

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/jim-sync-release-notes` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/82>

> ## Why
>
> Ported from [pdi#63](https://github.com/davidsbianchi1984/pdi/pull/63), where two defects in this workflow surfaced while repairing a release body that a stray paste had overwritten. The file was **byte-identical across all three repos**, so both defects are here too.
>
> ## The defects
>
> **1. It read the wrong file.** `actions/checkout@v4` had no `ref`, so it checked out the default branch — where `RELEASE_NOTES.md` always holds the *newest* version's notes. Syncing a tag push was correct by accident (the tag is the tip). Repairing anything older was actively wrong: it would publish the current version's notes onto an old release — the same failure this workflow exists to prevent, arriving by a different route. It now checks out the tag it is syncing.
>
> **2. It discarded the PR list.** `gh release edit --notes-file` replaces the whole body, so every sync silently dropped the auto-generated *What's Changed* section. It's now read off the release first and re-appended — and **de-duplicated on the way past**, since `app-v0.1.3` here carries that block twice, from a body pasted over one that already had it.
>
> ## State of this repo's releases
>
> Checked while investigating: **jim-mini's `app-v0.1.8` body is correct** — it is exactly the JIM-mini v0.1.8 notes, not affected by the paste that hit PDI. The only defect found here is the duplicated *What's Changed* on `app-v0.1.3`.
>
> ## Note on the preamble
>
> The workflow already stripped the *"Ready-to-paste body for the GitHub Release… Kept in sync with CHANGELOG.md"* line — a maintainer instruction that reads oddly to somebody who came for an installer. It survives on releases only because they were pasted by hand rather than synced. Any release this runs against loses it.
>
> ## Verification
>
> No application code touched — workflow only, so the suite is unaffected (240 tests, unchanged). The rebuild logic was tested against the real tags in the PDI PR before being ported here.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #81 — Design care beacons and the workplace relay

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/jim-care-beacons` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/81>

> ## What this is
>
> **Design only.** No code, no schema, no routes — [docs/beacons.md](https://github.com/davidsbianchi1984/jim-mini/blob/claude/jim-care-beacons/docs/beacons.md) is the decision record the implementation round will follow.
>
> QRME ships **desk beacons**: a printed QR on a shop door, resolving to a real person who simply is not behind it this minute, with a bell a stranger can ring. The gesture ports to the Guardian; the thing it points at does not — there is no desk here, and inventing one would be cargo-culting the feature rather than porting it.
>
> What JIM-mini has is **a person somebody is watching over**, and the physical anchors that person already leaves lying around: a fridge door, a wristband, a car window, the frame of a walker.
>
> ## Part one — the beacon
>
> **The alarm comes before the disclosure.** QRME shows the desk card freely and puts the bell underneath — a tradesperson's name is a shop sign. Health is not, so the order flips. Stage one is a first name and a button; raising the alarm is the act that turns a passer-by into a responder, and *that* is what earns them the Medical ID at stage two.
>
> The friction objection answers itself: the zero-friction path already ships on the person's own body, which is exactly what the Medical ID QR is for. The beacon can afford a gate **because** the ungated card exists alongside it.
>
> **`notify_contact` is a ceiling.** Every existing rule in `escalation.py` is a *floor* — crisis language never lands below `emergency_services`. This is the first pointing the other way, because a stranger's tap must never dispatch an ambulance on someone else's behalf: a false dispatch is a real one not going somewhere else.
>
> **The cooldown coalesces rather than drops.** A spammed alarm trains a family to ignore the one that matters — but the second person finding the same casualty is the case the feature exists for, so their message attaches to the open alarm.
>
> **Watch status, never subject status.** QRME's desk beacon exists *to* publish presence; this must publish the opposite. *Is this person OK right now* is precisely the question a stalker is asking. Location is withheld always, not just on rated codes.
>
> **A minor's beacon never opens the clinical stage**, to anyone. Parent-issued only, alarm routes to the parent, dies when oversight does at 18.
>
> **It is not a second Medical ID** — that one is a *disclosure* read by a responder already on scene; this is a *summons* found by anyone walking past. The doc draws the line explicitly.
>
> ## Part two — the workplace relay
>
> Asked directly whether a corporate deployment has a real case here: **yes, but a narrow one**, and it is an established category — **lone and remote workers.** Night shift, field engineers, plant rooms, single-staffed sites, anyone whose failure mode is that nobody was there. For a desk-bound office worker a care beacon adds little over walking to reception, and the doc says so.
>
> That case exposes a gap in part one: **`notify_contact` assumes a contact who answers.** In a personal deployment that is a family member and usually true. At 2am on a single-staffed site it may be nobody at all — and a worker's personal emergency contact is the wrong recipient for a workplace incident regardless.
>
> So a corporate deployment adds a **relay of last resort**:
>
> - **works the on-call roster in order** rather than firing one notification into the void;
> - **confirms a human actually accepted**, and keeps escalating until one does — the loop a fire-and-forget notification leaves open, and the reason to have an agent rather than a second phone number;
> - **answers the finder while they wait**, by calling the QRME first-aid guidance that already ships. A new caller to existing guidance, not a new model.
>
> Two constraints that do not bend:
>
> **Incident scope, never person scope.** A corporate deployment must not become a way for an employer to hold health data about employees. The agent sees that an alarm was raised at a beacon and what is needed — not conditions, baseline, history, or check-ins. The party who paid for the deployment is not thereby entitled to what is inside it. Same decision as PDI's blind-by-default, same reason.
>
> **The `notify_contact` ceiling holds.** A workplace agent escalates *people*, not sirens. An employer's agent dispatching an ambulance for an employee is precisely the version of this that should not exist.
>
> **It closes a loop with the other two products.** A workplace incident is a recordkeeping obligation, and PDI already carries **OSHA** with retention attached — so the alarm seals an incident record into the vault on the hash chain without anyone filling in a form at the time. Narrower than PDI's facility agent, and worth building second.
>
> ## Changes
>
> | File | |
> |---|---|
> | `docs/beacons.md` | new — the design |
> | `README.md` | "Designed, not yet built" pointer under Out of scope |
> | `CHANGELOG.md` | `[Unreleased] → Added` |
>
> ## Verification
>
> 240 tests green (`JIM_CONSOLE_DIR=/nonexistent python3 -m pytest -q`). Docs-only change; every relative link target checked to exist.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #80 — Release prep v0.1.8: version bumps, changelog cut, release notes

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/jim-release-v0.1.8` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/80>

> Cut alongside QRME and PDI, as the three always are now. This is the case the convention was written for: a repository with nothing of its own to ship still cuts, and **says so in those words** rather than padding the entry.
>
> ## What changed in JIM-mini
>
> **Nothing functional.** No API, no schema, no behaviour moved. I checked rather than assumed — the diff against the v0.1.7 tag touches zero files under `jim/` or `tests/`.
>
> The only change here is a repair to the changelog itself: `[0.1.5]` and `[0.1.6]` linked to release tags that were never pushed, so both were 404s. They now point at their release-prep commits.
>
> ## What's in the suite at 0.1.8
>
> The substance is QRME's: a live desk stops being only something you watch. You can ask to come up on the stream — which the host has to grant, and which needs a verified adult on a rated desk — and the room's comments, likes, shares and gifts render *on* the picture rather than beside it. Nothing in it asked the Guardian to change.
>
> ## What's in the diff
>
> - **Versions to 0.1.8** — `pyproject.toml`, the FastAPI app, `app/package.json`, and the two root entries in its lockfile. Dependency versions untouched.
> - **CHANGELOG** cuts `[0.1.8] — 2026-07-25`, with the anchors.
> - **RELEASE_NOTES.md** rewritten, telling an operator already on 0.1.7 that the upgrade is optional — because it is.
> - Also fixes a possessive typo I left in the 0.1.7 entry last round (`PDI' copies`).
>
> ## Verification
>
> 240 tests green — the same 240, passing the same way, which is rather the point of a release that claims to change nothing functional. FastAPI reports `0.1.8`.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #79 — Point the untagged versions at commits, not missing releases

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/jim-changelog-anchors` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/79>

> v0.1.5 and v0.1.6 were released — changelog, notes, version bumps — but their `app-v*` tags were never pushed, so no GitHub Release exists for either and the CHANGELOG entries linked to two 404s.
>
> ## The fix
>
> Those two entries now point at their **release-prep commits** (`c80c227`, `a930bcf`). The link then means "here is what that version was", which is what someone following it actually wants, and it resolves.
>
> `[0.1.4]` and below keep their release-tag links, because those releases are real. `[0.1.7]` keeps its tag link, because that tag is about to be pushed.
>
> ## Why not just backfill the tags
>
> I considered it and decided against it. Pushing `app-v0.1.5` and `app-v0.1.6` now would fire `desktop-release.yml`, build installers on real macOS/Windows/Linux runners, and publish two Releases **dated after v0.1.7** — putting superseded installers at the top of the page people download from. That's a worse outcome than the dead links were.
>
> `docs/releasing.md` records that reasoning, because an unexplained gap in a tag sequence is exactly the sort of thing someone finds later and "fixes" without knowing why it was left.
>
> ## Scope
>
> Docs only — no code, no version change, no new release.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #78 — Release prep v0.1.7: version bumps, changelog cut, release notes

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/jim-release-v0.1.7` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/78>

> The first release cut under the rule written down last round: the three products ship as one, same number, same pass, **even when a repository has nothing of its own to ship**.
>
> This is that case, and the notes say so in those words rather than padding the entry.
>
> ## What changed in JIM-mini
>
> **Documentation only.** No API, no schema, no behaviour change. Everything the Guardian does at 0.1.7 it did at 0.1.6.
>
> The substance at 0.1.7 is QRME's — live desks left behind as printed codes, a full audience layer (like, comment, share, subscribe), and a marketplace that can finally take payments. None of it asked the Guardian to change.
>
> Through v0.1.5 each repository cut whenever it happened to have work, so the numbers matched only by coincidence. v0.1.6 aligned them by hand; **this is the first round where the alignment is the process rather than a correction.**
>
> ## What's in the diff
>
> - **Versions to 0.1.7** — `pyproject.toml`, the FastAPI app, `app/package.json`, and the two root entries in its lockfile. Dependency versions untouched: the lockfile edit is pinned to lines 3 and 9 by an assertion, not a blind replace.
> - **CHANGELOG** cuts `[0.1.7] — 2026-07-25` from Unreleased, with the anchors.
> - **RELEASE_NOTES.md** rewritten for v0.1.7, leading with what did *not* change and telling an operator already on 0.1.6 that the upgrade is optional — because it is.
>
> ## Verification
>
> 240 tests green — the same 240, passing the same way, which is rather the point of a release that claims to change nothing functional. FastAPI reports `0.1.7`.
>
> ## After merge
>
> The `app-v0.1.7` tag goes on **this** commit, not on whatever `main` reaches later.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #77 — Write down the release convention: the three cut together

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/jim-release-convention` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/77>

> QRME, JIM-mini and PDI are built to run in tandem, but through v0.1.5 each repository cut whenever it happened to have work, so the numbers matched only by coincidence — which is how QRME reached 0.1.6 alone while this one sat at 0.1.5. v0.1.6 aligned them by hand. This writes down the rule that keeps them aligned, so the next round doesn't have to rediscover it.
>
> ## Three rules, in `docs/releasing.md`
>
> - **The three are versioned as one release** — same number, same pass, even when a repository has nothing of its own to ship that round.
> - **A repository with nothing to ship still cuts, and says so** in those words. A note that inflates an empty round teaches people to skim the ones that aren't empty.
> - **Tag the release-prep commit, not the tip of `main`.** Work keeps landing while a release is cut, and anything arriving after the changelog is sectioned belongs under `[Unreleased]` rather than to the version being tagged.
>
> That last one is written down because it already nearly bit: QRME's v0.1.6 tag point sits two commits behind its `main`, and tagging the tip would have published two features under notes that don't mention them.
>
> ## Scope
>
> Docs only — no code, no API, no behaviour change. `docs/releasing.md` gains the section and step 1 of "Cut a release" now says to do the same in the sibling repositories in the same pass.
>
> ## Verification
>
> 240 tests green.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #76 — Align the version with the suite: v0.1.6

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/jim-align-v0.1.6` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/76>

> QRME, JIM-mini and PDI are built to run in tandem, but their version numbers only ever matched by coincidence: a round of work would land in one repository and not the others, and the numbers drifted. QRME reached 0.1.6 on its own while this stayed at 0.1.5.
>
> From here the three carry the same number, so "the suite at 0.1.6" names one combination of three products rather than three that happen to be nearby — and anyone pinning all three can pin one number.
>
> ## There are no functional changes to JIM-mini here
>
> The notes say that in those words rather than padding the entry. Everything the Guardian does at 0.1.6 it did at 0.1.5 — no API, no schema, no app behaviour moved. The work that earned the suite its 0.1.6 is QRME's: AI marks burned into portrait pixels, live desks, WebAuthn signing on Windows. None of it crosses into this repository.
>
> The release notes tell an operator already on 0.1.5 that the upgrade is optional, because it is.
>
> ## What's in the diff
>
> - **Versions to 0.1.6** — `pyproject.toml`, the FastAPI app, `app/package.json`, and the two root entries in its lockfile. Dependency versions untouched: the lockfile edit is pinned to lines 3 and 9 by an assertion, not a blind find-and-replace.
> - **CHANGELOG** cuts `[0.1.6] — 2026-07-25` from Unreleased, with the compare/tag anchors.
> - **RELEASE_NOTES.md** rewritten for v0.1.6. It leads with what did *not* change and then carries the v0.1.5 substance forward — the compile gate, the container, published deployments, `docs/hosting.md` — because that is what someone installing this actually gets.
>
> ## Verification
>
> 240 tests green — the same 240, passing the same way, which is rather the point of a release that claims to change nothing. Checked `README.md`, `docs/` and `.github/` for stray `0.1.5` references; there are none.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #75 — Release prep v0.1.5

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/jim-release-v0.1.5` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/75>

> v0.1.4 led on choice — one command, every way to run the Guardian. This one leads on something less glamorous and more overdue: **the native apps now go through a compiler.**
>
> ## What changed
>
> - Versions to `0.1.5`: `pyproject.toml`, the FastAPI app, `app/package.json`, and the two root entries in its lockfile. Dependency versions untouched — the lockfile edits anchor on position, not on a bare version string.
> - `CHANGELOG.md` cuts `[0.1.5] — 2026-07-25` from Unreleased, with the compare/tag link anchors.
> - `RELEASE_NOTES.md` rewritten for v0.1.5.
>
> ## Why the compile gate is the headline
>
> A gate that finds nothing is a claim. This one found two defects that no amount of reading had caught, and the notes name both rather than saying "various fixes":
>
> - The **iOS project spec was invalid** — no `path` on the XcodeGen `info:` block, so `xcodegen generate` failed outright and the Xcode project could never have been produced at all.
> - **Windows would not compile the journal list** — an array converts implicitly to `Span<T>`, so `.Reverse()` bound to the in-place *void* overload instead of LINQ's, leaving the following `.Select` attached to nothing.
>
> ## Verification
>
> `JIM_CONSOLE_DIR=/nonexistent python3 -m pytest -q` → **240 passed**.
>
> This PR touches no code, so the native jobs won't run on it — they were green on the merge that introduced them (#74) and on the log-readability follow-up.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #74 — Compile the native apps in CI, and fix two defects it makes visible

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/jim-native-ci` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/74>

> ## Why
>
> Ported from QRME, where this gate found **five real defects** in code that had never been through a compiler. The Swift, Kotlin and C# here is in exactly the same position: checked by reading, and by brace/XML well-formedness, which catches a typo and nothing else.
>
> ## Two of QRME's findings are already present here
>
> Fixed in the same commit rather than left for the first red run.
>
> **The iOS project spec has never been valid.** Its XcodeGen `info:` block has no `path` (required), while also setting `GENERATE_INFOPLIST_FILE`, which is mutually exclusive with it. `xcodegen generate` fails outright — nobody could ever have produced `JimGuardian.xcodeproj`. It also means the local-networking exemption that lets the Simulator reach `http://127.0.0.1:8000` could not have applied either way.
>
> **The Windows journal list would not compile.** In `LifePage`, `entries` is a `JournalItem[]`, and an array converts implicitly to `Span<T>` — so `.Reverse()` binds to `MemoryExtensions.Reverse`, which reverses **in place and returns void**, instead of LINQ's. The following `.Select` then has nothing to attach to. `Enumerable.Reverse` is now named explicitly.
>
> ## Swept for the other two classes, found none
>
> - **Kotlin calls treating `request()`'s return as JSON** — QRME's `request()` returns `String` and three call sites forgot the `JSONObject(...)` wrap. This repo's already returns `JSONObject`, so there's nothing to fix.
> - **Swift calls missing an argument label** — none.
>
> ## The build recipe, already proven
>
> - **iOS**: XcodeGen → `xcodebuild` against the simulator SDK, signing disabled. `-quiet` plus a grouped grep for `error:` lines on failure, because xcodebuild's default output buries the diagnostic hundreds of lines above the exit.
> - **Android**: JDK 17, Gradle 8.9 via `setup-gradle` (no `gradlew` in the repo), `assembleDebug`.
> - **Windows**: Visual Studio's **MSBuild**, not `dotnet build` — the Windows App SDK's PRI packaging task ships with VS and is absent from the standalone .NET SDK at *every* version. `global.json` pins the SDK line the App SDK targets.
>
> Compile only — signing and packaging stay in the release workflow. Runs on changes under `native/` and on demand, since macOS runner minutes aren't free.
>
> ## Verification
>
> `JIM_CONSOLE_DIR=/nonexistent python3 -m pytest -q` → **240 passed** (unchanged; this adds no Python).
>
> The native jobs' first run is this PR. Both fixes above are ones the compiler already confirmed in QRME, but nothing here has been compiled yet — a red run is a real finding, and I'll read it rather than route around it.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #73 — Deployable as one container: Dockerfile builds the console, docs/hosting.md

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/jim-deploy` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/73>

> ## Why
>
> Publishing a Guardian should keep the property that makes the phone flow work: the console and the API on **one origin**, nothing to configure on the device. The existing `Dockerfile` shipped the API only, so hosting meant standing the UI up separately and reintroducing the "which host is the backend?" question that `/pair` exists to eliminate.
>
> ## What changed
>
> **`Dockerfile` — two stages.** `node:20-slim` builds `app/dist`; `python:3.12-slim` installs the package and takes only the built console across, so the Node toolchain never ships in the runtime image.
>
> - Runs as a non-root service user (uid 10001).
> - `JIM_DB` defaults under the declared `/data` volume — a restart must not lose someone's health history *or* the baseline the Guardian learned for them.
> - Honours `$PORT`; `HEALTHCHECK` on `/health`, on 8200 to match what the suite harness expects.
>
> **One real bug, found by reading rather than building.** `console_dir()` resolves `app/dist` relative to the *package*, and after `pip install` the package lives in site-packages — nowhere near the dist the image copies to `/srv`. The console would have been found only by accident, when the working directory happened to shadow the installed copy. Fixed by setting `JIM_CONSOLE_DIR=/srv/app/dist` explicitly.
>
> **`jim/tests/test_container.py`** pins that agreement so it can't drift back, plus the volume path, the non-root user, the `0.0.0.0` bind, and the 8200 default. Static checks, deliberately — see the caveat below.
>
> **`docs/hosting.md`** — the operator's side, with the parts that are specific to a guardian rather than generic hosting advice:
>
> - **Escalation still has to work.** `POST /emergency` is what makes this a guardian rather than a dashboard; exercise it on your deployment, with a real contact, before anyone relies on it.
> - **TLS is not optional, twice over.** Tokens travel in headers and unlock biometrics, medications, and a medical ID — and browsers refuse the geolocation API over plain HTTP, so an escalation payload from a hosted phone would arrive with no location.
> - **Holding other people's health data**: the ToS review, the HIPAA/BAA question (hosting for a household is a different posture from hosting for a clinic — know which you're in *before* taking the data), that encryption at rest belongs to PDI because JIM's own database is not encrypted, that `DELETE /data/{user_id}` must be tested before it's promised, and that children's accounts raise the stakes.
> - A **"What this does not give you"** section: no multi-tenancy, no rate limiting, no backups, no uptime guarantee — and a guardian that is down is not guarding.
>
> ## Caveat, stated up front
>
> **The image was not built or run here.** The Docker CLI is present in this environment but there is no daemon, so every check on it is static. Build it once before trusting it.
>
> ## Verification
>
> `JIM_CONSOLE_DIR=/nonexistent python3 -m pytest -q` → **240 passed** (6 new).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #72 — Published deployments: pairing knows its public URL, optional signup key

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/jim-hosting` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/72>

> ## Why
>
> Completes the hosting round (pdi#51, qrme#104). The phone flow assumed a laptop on Wi-Fi; troubleshooting alongside colleagues means the same deployment also has to be reachable from the internet. Both postures now come from one code path.
>
> ## What
>
> | Variable | Effect |
> |---|---|
> | `JIM_PUBLIC_URL` | `GET /pair` advertises the deployment's own address, **QR included**, instead of a LAN address the phone can't see from outside. The hosted note names **HTTPS** explicitly — user tokens travel in headers and this is health data. Unset → LAN behaviour unchanged. |
> | `JIM_SIGNUP_KEY` | Enrolling requires the key as an `x-signup-key` header, so a published instance stays the operator's rather than open registration. Unset → open, the right default on a LAN. |
>
> The gate rides as a **route dependency**, not a call in the handler — so it never reaches `guardian.enroll()`. That's what keeps **a parent adding a child working**, authorized by their own token rather than asked for the deployment key again. A test pins that behaviour, along with an already-enrolled user's surfaces still answering while the gate is set.
>
> Note PDI remains entirely optional here: with `JIM_PDI_URL` unset, JIM runs standalone against its own SQLite, hosted or not.
>
> ## Testing
>
> `jim/tests/test_hosting.py` (6): hosted pairing advertises the public URL; unhosted falls back to LAN; trailing-slash normalisation; the signup key refuses missing *and* wrong keys and accepts the right one; unset leaves local use open; and the gate blocks neither an enrolled user's own surfaces nor child enrollment under the parent's token.
>
> Full suite: **234 passed**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #71 — sync-release-notes: publish the release body from RELEASE_NOTES.md

- merged · opened 2026-07-25 · merged 2026-07-25
- `claude/jim-sync-release-notes` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/71>

> ## Why
>
> Release bodies have been pasted by hand, and v0.1.4 hit both failure modes: copying from a rendered page silently strips the markdown, and a manual "delete the old half" edit truncated a line mid-sentence. `RELEASE_NOTES.md` is already the source of truth, so there's no reason a human should be moving that text through a clipboard.
>
> ## What
>
> `.github/workflows/sync-release-notes.yml` (same workflow as the sibling repos) sets a published release's body from `RELEASE_NOTES.md`:
>
> - **`workflow_dispatch`** with a `tag` input — fixes an existing release from the Actions tab.
> - **`push` on `app-v*` tags** — every future release gets its body automatically.
>
> It strips the file's internal "ready-to-paste" preamble so the published body starts at the headline, then `gh release edit --notes-file` does the rest. Uses the repo's own `GITHUB_TOKEN` (`contents: write`) — no new secrets.
>
> ## Testing
>
> - YAML parses.
> - Extraction verified against the real `RELEASE_NOTES.md`: 3161 chars, starts at `**JIM-mini (Guardian) v0.1.4** — run it your way…`, no preamble.
> - After merge I'll dispatch it against `app-v0.1.4` to repair the current body.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #70 — Release prep v0.1.4: version bumps, changelog cut, release notes

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-release-v014` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/70>

> ## What
>
> Release mechanics for **v0.1.4** — the launcher round rolls in, and the headline moves with it. v0.1.2/v0.1.3 led on trust (terms with a receipt, signed builds); this one leads on **choice**:
>
> > **JIM-mini (Guardian) v0.1.4** — run it your way: one command prints every way to run the Guardian and you pick the device — your phone (scan a QR straight off the terminal), this PC, a packaged installer, or the headless API.
>
> - Versions to **0.1.4**: `pyproject.toml`, FastAPI app, `app/` package.json + lockfile root entries (dependency versions untouched — the lockfile edits anchor on the package name).
> - CHANGELOG cuts **[0.1.4] — 2026-07-24** from Unreleased with its link anchor.
> - `RELEASE_NOTES.md` rewritten for v0.1.4: new headline, launcher and one-command phone setup leading the highlights.
>
> After merge, creating the `app-v0.1.4` tag fires the `desktop-release` workflow and builds the installers.
>
> ## Testing
>
> - Full suite: **228 passed** (run headless, the CI condition).
> - `app/` desktop console builds clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #69 — python -m jim: launcher menu — phone, desktop, installer, or headless, one command each

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-phone-cmd` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/69>

> ## What
>
> Users choose how and where to run the Guardian — every option is one command, and the choice itself is a command:
>
> ```bash
> python -m jim            # the launcher menu: choose your device
> ```
>
> | Choice | Command | What happens |
> |---|---|---|
> | **On your phone** | `python -m jim phone` | builds the console if missing (first-run `npm install` included), prints the pairing URL **with a QR drawn straight into the terminal**, serves on the local network — scan, Add to Home Screen, done |
> | **On this PC** | `python -m jim desktop` | the Electron desktop app (builds the console first when needed); without npm it points at the packaged installers instead |
> | **Packaged installer** | releases/latest | `.dmg`/`.exe`/`.AppImage` — no toolchain needed |
> | **Headless API** | `python -m jim serve` | backend alone, localhost by default (`--host`/`--port`) |
>
> Every option runs the same backend with the same data and token checks. Headless checkouts without npm still work everywhere — the pairing block and the desktop command both say exactly what's missing and where to go instead of failing silently. `phone` flags: `--port`, `--rebuild`, `--no-build`, `--print-only`. Serving uses the `"jim.api:app"` import string so the console mount happens *after* the build step.
>
> README's "Run it on your phone" now leads with the launcher; manual steps stay as the alternative.
>
> ## Testing
>
> - 4 new tests: built path prints URL + terminal QR; headless path prints build guidance and no QR; the bare menu lists all four ways; `desktop` without npm points at the installers.
> - Full suite: **228 passed** (run headless, the CI condition).
> - Manual: `python -m jim` renders the menu; `python -m jim phone --print-only` renders a clean scannable QR block.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY

## #68 — Release prep v0.1.3: version bumps, changelog cut, release notes

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-release-v013` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/68>

> ## What
>
> Release mechanics for **v0.1.3** — the phone round rolls in: console served at `/app`, `GET /pair` with the scannable QR, and the installable PWA. The release-notes headline stays exactly as it was in v0.1.2 (the trust release); the phone feature leads the highlights.
>
> - Versions to **0.1.3**: `pyproject.toml`, FastAPI app, `app/` package.json + lockfile root entries (dependency versions untouched).
> - CHANGELOG cuts **[0.1.3] — 2026-07-24** from Unreleased and adds the release link anchor.
> - `RELEASE_NOTES.md` updated as the ready-to-paste v0.1.3 GitHub Release body.
>
> After merge, creating the `app-v0.1.3` tag fires the `desktop-release` workflow and builds the installers.
>
> ## Testing
>
> - Full suite: **224 passed**.
> - `app/` desktop console builds clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #67 — Run the Guardian from your phone: served console, pairing, installable PWA

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-mobile` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/67>

> ## What
>
> Operate JIM-mini from a phone, with nothing to install and nothing to configure.
>
> **The API serves the console.** The built console mounts at `/app`, so the UI and the API share one origin — the phone loads the page and calls the address it came from. No CORS setup, no "which host is the backend?" step. Mounted last so it can never shadow an API route, and skipped entirely when `app/` hasn't been built (the API stays headless as before).
>
> **`GET /pair` finds the machine.** It resolves this machine's local-network address from the routing table (a UDP connect binds a local address without sending a packet) and returns the URL to open, plus `GET /pair/qr.svg` as a scannable QR — both surfaced in a pairing card on the Privacy screen. Loopback is treated as a failure, not a fallback: on a phone `127.0.0.1` means the phone, so pairing reports `reachable: false` and says to set `JIM_LAN_HOST` rather than handing over an address that can't work.
>
> **Installable as a PWA** — manifest, icon, standalone display, and a service worker that caches the **app shell only**. It never caches API traffic: monitoring, guidance, and escalation must always be live, because a stale answer in a health app is worse than an error.
>
> **Phone layout** — the sidebar becomes a thumb-reachable bottom tab bar (brand block, guardian chip, and sign-out fold away; sign-out already lives in Privacy), inputs sit at 16px so iOS doesn't zoom on focus, and the layout respects the notch and home indicator. Also fixes the app title, which said "QRME".
>
> ```bash
> npm --prefix app run build          # build the console once
> uvicorn jim.api:app --host 0.0.0.0  # listen on the network
> curl localhost:8000/pair            # what to open on the phone
> ```
>
> The address is local-network only and not reachable from the internet — health data stays on your own network, and every personal endpoint still requires the user's bearer token.
>
> ## Testing
>
> - `jim/tests/test_mobile.py` (6): pairing returns a reachable address (never loopback) and a QR encoding it; the loopback case is reported honestly with the fix; the console mounts at `/app` when built without shadowing the API; the API stays headless when it isn't; the shipped PWA declares itself installable and its worker leaves API traffic alone.
> - Full suite: **223 passed**; console builds clean.
> - **Live-server check against the LAN address** (what the phone would do): `/app/`, manifest, service worker, icon, and QR all serve; enroll (with terms receipt), a calm monitor reading, an alarming one (detection → guidance → escalation), check-in, and the one-tap emergency flow all work from that origin.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #66 — Release prep v0.1.2: version bumps, changelog cut, release notes

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-release-v012` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/66>

> ## What
>
> Release mechanics for **v0.1.2 — the trust release**: Terms of Service with a recorded enrollment receipt, signed/notarized build wiring, and the BAA pointer into the PDI repo all roll into this version.
>
> - Versions to **0.1.2**: `pyproject.toml`, FastAPI app, `app/` package.json + lockfile root entries.
> - CHANGELOG cuts **[0.1.2] — 2026-07-24** from Unreleased and repairs the release links at the bottom (adds the missing 0.1.1/0.1.2 anchors).
> - `RELEASE_NOTES.md` rewritten as the ready-to-paste v0.1.2 GitHub Release body.
>
> After merge, creating the `app-v0.1.2` tag fires the `desktop-release` workflow and builds the installers.
>
> ## Testing
>
> - Full suite: **217 passed**.
> - `app/` desktop console builds clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #65 — Terms of Service: served, accepted at enrollment, recorded with a receipt

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-terms` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/65>

> ## What
>
> Full Terms of Service for JIM-mini, wired so acceptance is provable:
>
> - **docs/terms.md (v1.0)** — leads with the section that matters most: JIM is a wellness tool, **not a medical device** — call 911 first, 988 in crisis, and detection can be wrong in both directions (false positives *and* negatives). Then: assumption of risk and a release/waiver (carving out gross negligence and willful misconduct), the robot-resuscitation boundary (fully autonomous resuscitation requires the separate signed waiver, never for a minor, and a robot never delivers the defibrillation shock), parent/guardian enrollment of minors, user responsibilities, health-data pointer to the HIPAA posture, an as-is warranty disclaimer, a liability cap (greater of 12-month fees or US $100), indemnification, and termination/changes. Governing law is left as a counsel placeholder, and the whole document is marked as a template requiring counsel review before commercial launch.
> - **`GET /terms`** — serves the version, the key points, and the document path, so clients always show the current terms.
> - **Server-side receipt** — enrollment records `terms_version` + `terms_accepted_at` on the user row when consent is given, so there's proof of which version was accepted and when.
> - **Clickwrap in every native app** — the iOS, Android, and Windows welcome screens carry the "By enrolling you agree to the Terms of Service…" notice next to the enroll action.
>
> ## Testing
>
> - `jim/tests/test_terms.py`: terms are served versioned with the not-a-medical-device and 911 key points; enrollment stamps the version + timestamp receipt.
> - Full suite: **217 passed**.
> - Static native checks: all XAML/SVG parse, brace/paren balance on Swift/Kotlin/C#, all `Jim*` brushes referenced in Views are defined in App.xaml.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #64 — macOS notarization wiring + link the signable BAA template

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-signing-baa` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/64>

> The JIM slice of the deferred-items sweep.
>
> ## Signing
>
> `hardenedRuntime` + Gatekeeper entitlements + `notarize: true` in the electron-builder config, so adding the Apple secrets produces a fully notarized build — **previously signing ran but notarization silently never happened**. `docs/releasing.md` gains the certificate-acquisition walkthrough for both platforms. Unsigned builds still succeed exactly as before.
>
> ## BAA
>
> `docs/hipaa-baa.md` — JIM's HIPAA posture and pre-production checklist — now points at the production-ready, signable BAA template maintained in the PDI repo (`docs/baa-template.md`), so each signature on the checklist has a document to start from.
>
> **215 tests pass.**
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #63 — Release prep v0.1.1: version bumps, changelog & notes

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-release-0.1.1` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/63>

> Everything between the `app-v0.1.0` tag (41 commits back) and now rolls into **v0.1.1**: native parity (Care / Life / Safety / Connect / Custody), robot first-aid responders with the waiver hard line, predictive early warning + the Emergency flow, the family layer with the parent's wrist, provable PDI custody with the tandem trio, language + provenance everywhere, starter specialists, in-app feedback, and chrome l10n.
>
> This PR is the release mechanics:
>
> - **Versions to 0.1.1** — pyproject, FastAPI app, `app/` package.json + lockfile
> - **CHANGELOG** `[0.1.1]` section covering everything since the tag
> - **RELEASE_NOTES.md** rewritten as the ready-to-paste v0.1.1 GitHub Release body
>
> ## Verified for release
>
> 215 tests green · live-server smoke flows pass · the desktop app builds clean · the cross-product suite smoke passes end to end.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #62 — Chrome localization + polish across the native apps

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-nav-l10n-polish` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/62>

> The apps' own frame now follows the user's language, and the main screens refresh properly — the JIM slice of the backlog sweep's localization/polish items.
>
> Note on the nav-crowding item: it was **already resolved** — the Android bottom nav has been 5 items since Care folded in Monitor / Check-in / Coach / Family — so this round is localization + polish.
>
> ## Localization
>
> A chrome string table (`L10n`) on each platform covers tab/nav names and the most common actions in all 10 backend-supported languages (en/es/fr/de/pt/it/ja/zh/hi/ar), falling back to English per key. The chosen user language — loaded at Overview and remembered in AppState / SharedPreferences / session.json — drives it, so picking Español relabels the iOS tab bar, the Android bottom nav, and the Windows nav pane (re-applied on every pane selection so a change lands immediately). Guidance, coaching, and safety content were always localized server-side; this closes the frame around them.
>
> ## Polish
>
> - iOS: pull-to-refresh on Overview / Life (`.refreshable`)
> - Android: Compose `PullToRefreshBox` on Overview; sign-out localized
> - Windows: Refresh action on Overview
>
> ## Verification
>
> No backend changes; **215 tests still pass**; native XML parse, brace balance, and brush audit clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #61 — Help us improve: in-app product feedback anyone can send

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-feedback` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/61>

> A **"Help us improve"** section now lives on the Overview screen on every client — send an idea, an improvement, a bug, or praise about the app itself, with an optional 1–5 rating.
>
> This is **distinct from the guidance feedback loop** (`POST /feedback/{user_id}`, rating a specific piece of guidance): it's about the app, open to anyone, and private per submitter.
>
> Feedback is **private**: a submitter sees only their own submissions plus the public tally by category (how many ideas, bugs, …), so the "you're heard" loop shows without exposing anyone's words. An authenticated caller's role/subject is recorded so they can find their submissions again; otherwise it's anonymous.
>
> ## Changes
>
> - `improvements` table (`id, submitter, category, message, rating, status, created_at`) + `ImprovementSubmit` model
> - `POST /improve` validates category, non-empty message, 1–5 rating (422s); `GET /improve` returns `{mine, tally, total, categories}` — `mine` only for the authenticated submitter, `tally` aggregate over all
> - Native UI, all on the Overview screen, wired to submit + load: iOS `ImproveCard`, Android `ImproveCard`, Windows "Help us improve" card
> - README documents `POST`/`GET /improve`
>
> ## Tests
>
> `jim/tests/test_improve.py` (4): anyone can submit and it tallies; bad category/rating/message refused; an authenticated submitter sees only their own; two users don't see each other's words.
>
> **215 tests pass**; native XML parse, brace balance, and brush audit clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #60 — Native family controls + the parent's watch, on every surface

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-family-native` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/60>

> ## Summary
>
> The family-controls backend (#59) reaches the apps and the watch gallery:
>
> - **iOS** (`FamilyView`) — a **Family watch** strip up top: per-child light (green/orange/red), critical/escalated chips, paused + 🌙 quiet-hours chips, and a **⌚ TAPPED** badge when the wrist alerted. Opening a child adds a **Device controls** card: pause toggle, quiet-hours HH:MM fields (prefilled from the child's current state), Apply, and the safety-never-pauses note.
> - **Android** (`FamilyPanel`) — the same strip and controls card (Switch + OutlinedTextFields), state prefilled on open.
> - **Windows** (`FamilyPage`) — a Family watch card and a Device controls card (ToggleSwitch + quiet boxes + Apply) fed by the new `GuardianWatch` / `SetFamilyControls` client methods.
> - **Watch gallery** — new face **35 · Family**: the guardian's wrist with Riley quiet, Sam escalated with tap-to-open, and the quiet-hours chip ("safety never pauses"). README watch-gallery cell added.
>
> All three ApiClients gain `guardianWatch()` and `setFamilyControls()`.
>
> ## Verification
>
> Static (no native toolchains): all XAML/SVG parse (35 watch faces regenerate clean), brace/paren balance clean, and the Windows brush audit passes. Backend untouched — **211 tests pass**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #59 — Family controls: pause/quiet hours, the parent's wrist, sealed consent

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-family-controls` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/59>

> ## Summary
>
> Three follow-ups to the parent-led setup (#58), with one safety rule threaded through all of them: **safety never pauses**.
>
> - **Device controls** — `PUT /guardians/{gid}/children/{cid}/controls`: guardian pause and HH:MM quiet hours (midnight-wrapping windows like 21:00–07:00) hold *everyday* guidance only. Detection still runs, a held delivery lands as an audited `guidance_held` event, and a **critical detection never even checks the hold** — crisis guidance and escalation flow in full.
> - **The parent's wrist** — `GET /guardians/{gid}/watch`: one light per child from the last 24 hours of alert-level events (green quiet · orange escalated · red critical), `haptic: alert` when a child needs someone, and the pause/quiet chip per child. Alert-level only, so the teen tier's privacy holds by construction — the wrist never sees a diary.
> - **Sealed consent** — with a PDI vault configured, the guardian-consent record is sealed under `jim/{child}/family/consent/…`: locally only the vault reference remains, and PDI's provenance + hash-chained audit make *who consented, as what, when* provable — the same custody the medical stream gets.
>
> ## Tests
>
> `jim/tests/test_family_controls.py` (4): pause holding everyday guidance while a crisis escalates in full, quiet hours holding then releasing when the window moves, watch lights + haptic with the paused chip (teen crisis → red + tap; sibling stays green), and the vaulted consent record with only the reference kept locally.
>
> **211 passed** (207 existing + 4 new).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #58 — Family: a parent sets up and watches over a child's account

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-parent-setup` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/58>

> ## Summary
>
> The bare `guardian_consent` flag becomes a **recorded relationship**, with the full parent-led setup flow — logic, screens, and coding — behind it.
>
> **Backend** (`jim/family.py` + routes)
> - `POST /guardians/{gid}/children` — a **verified-adult** guardian enrolls their child (a minor can't be a guardian; an adult "child" is refused — adults enroll themselves). Consent lands on the child's timeline as an event: *who* consented, *as what* (parent / legal_guardian), *when*. Protective defaults: `cautious` sensitivity, the guardian as the consented emergency contact, cloud contribution and provider access hard-off. The child's device token is shown exactly once — the guardian puts it on the child's watch or phone.
> - **Oversight sized by age**: `full` under 13 (condition-level timeline — never raw notes or payloads), `alerts_only` 13–17 (**escalations reach the parent; a teenager's check-ins, notes, and everyday guidance stay private**), and the window **closes itself the day they turn 18**.
> - `GET` children list · `GET` child overview · `DELETE` unlink (the account and the recorded consent remain; only the window closes).
> - **Hard line**: the autonomous-resuscitation waiver can never be signed for a minor — not by the minor, not by a guardian; confirm-gated operation is the ceiling.
>
> **Native (all three apps)** — iOS `FamilyView` behind a new *Family* tab in Care (create-child form, one-time token card, family list with oversight lights, tap-through window); Android `FamilyPanel` behind the same tab in `CareScreen`; Windows `FamilyPage` + *Family* nav item.
>
> **Screens/docs** — gallery screens **57 · Parent Setup** and **58 · Family Oversight** (116 SVGs regenerate clean); README endpoint row + gallery cells.
>
> ## Tests
>
> `jim/tests/test_parent_setup.py` (7): recorded consent + protective defaults + a working child token; the adult/minor boundary in both directions; age-sized tiers; teen privacy (a crisis note escalates to the parent while the diary stays out of the window); oversight ending at 18; the never-waive guarantee; unlink keeping the account alive.
>
> **207 passed** (200 existing + 7 new); XAML/SVG parse, brace balance, and brush audit clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #57 — Native custody screen: list every sealed exchange with its proof

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-custody-screen` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/57>

> ## Summary
>
> The custody viewer backend (#55) shipped without a home in the apps. All three clients now carry a **Vault** screen listing the user's sealed tandem exchanges from `GET /custody/{user_id}`, with the audit-chain status up top ("🔗 Audit chain intact") and per-record provenance on tap/select — origin (*JIM Guardian*), seal cipher, audit event count, hash-chain status — from `GET /custody/{user_id}/provenance`.
>
> - **iOS** — new `CustodySection` (`Views/CustodyView.swift`) behind a **Vault** tab added to the Safety switcher; `ApiClient` gains `custody()` / `custodyProvenance()` with `CustodyList` / `CustodyProvenance` models. Records expand in place with chevron toggles; provenance is fetched lazily and cached.
> - **Android** — `CustodyPanel` behind the same **Vault** tab in `SafetyScreen`; `ApiClient` parses both payloads (URL-encoded key lookup for the provenance query).
> - **Windows** — new `CustodyPage` + **Vault Custody** item in the shell `NavigationView`; `ApiClient` records + `Custody()` / `CustodyProvenance()` with `Uri.EscapeDataString` on the key. Selecting a record in the ListView fills the provenance card.
>
> The empty state explains that exchanges appear after a tandem specialist chat, and a deployment without a PDI vault surfaces the backend's 409 detail as the error message.
>
> ## Verification
>
> Static only (no native toolchains in this environment): all `.xaml` parse as XML (including the new `CustodyPage.xaml` — all referenced brushes verified present in `App.xaml`); brace/paren balance clean across `.swift`/`.kt`/`.cs`. Backend untouched — **200 tests pass**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #56 — Tandem trio: route the mental-health conditions through QRME personas

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-tandem-trio` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/56>

> ## Summary
>
> QRME's starter collection now carries a mental-health trio (qrme#72) matching JIM's starter specialists, so `TANDEM_HANDLES` extends from two pairs to five:
>
> - `anxiety` → **`@dr_lena_whitcomb`** (clinical psychologist, anxiety & panic)
> - `depression` → **`@dr_marcus_adeyemi`** (psychiatrist, mood disorders)
> - `relationship` → **`@dr_priya_nair`** (family & couples therapist)
>
> The safety lines are unchanged and now explicitly tested: **crisis language still escalates through JIM's own tree regardless of guidance routing** — a tandem specialist chat never replaces the emergency-contact escalation. All existing rails (minor/age gate, departed-profile fallback, local fallback on QRME refusal, PDI custody sealing) apply to the new pairs automatically, since they ride the same `_deliver` path.
>
> ## Tests
>
> `test_tandem_starters.py` updated: map/label parity asserted for all five pairs, link/kept/unresolved counts made map-relative, a new anxiety end-to-end test (biometric panic detection → tandem guidance through `prf_dr_lena_whitcomb` with the specialist attribution), and the crisis-escalation-not-bypassed guarantee. `FakeQRME` resolves the trio's handles.
>
> **200 passed** (198 existing + 2 new).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #55 — Custody viewer: sealed-exchange indicators and a provenance window

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-custody-viewer` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/55>

> ## Summary
>
> Tandem exchanges get sealed into the PDI vault (#54), but nothing showed the user. This PR makes custody visible end to end:
>
> **Backend**
> - `GET /custody/{user_id}` — lists the user's sealed tandem exchanges (vault keys) plus PDI's tamper-evident audit-chain status.
> - `GET /custody/{user_id}/provenance?key=` — reads PDI's full derivation trail for one sealed exchange: origin (*JIM Guardian*), seal details (AES-256-GCM envelope), audit history, chain status. Scoped strictly to the user's own `jim/{user}/tandem/…` namespace — medical event keys and foreign keys 404. 409 without a PDI vault configured, 502 when the vault is unreachable.
> - `jim/pdi_client.py` gains `provenance(key)` against PDI's public `/provenance/{key}` endpoint (HTTP boundary preserved).
>
> **Native**
> - iOS, Android, and Windows decode the guidance `custody` block and render it with the guidance: a **🔒 Sealed in the PDI vault** line with the PDI key (the provenance lookup handle) when custody held, and the honest ⚠️ unsealed note when the vault was down.
>
> ## Tests
>
> `jim/tests/test_custody_viewer.py` (JIM wired to FakeQRME + a FakePDI that also serves `/provenance` and `/audit/verify`): custody listing with chain status, provenance passthrough, own-records scoping (medical keys and foreign keys both 404), and the 409 without PDI.
>
> **198 passed** (194 existing + 4 new); native XAML parse + brace-balance checks clean.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #54 — Provable custody: seal tandem specialist exchanges in the PDI vault

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-tandem-custody` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/54>

> ## Summary
>
> Closes the loop between the three products: chats with QRME specialist profiles initiated from JIM now get provable custody in PDI.
>
> - **`jim/guardian.py`** — `pdi` is threaded through `_deliver`/`_tandem_guidance` from every guidance path (monitor, emergency, ambient activity). When a tandem exchange completes, the full record — condition, specialist label, the Guardian's monitoring message, the specialist's moderated reply, status, timestamp — is sealed into the PDI vault under `jim/{user}/tandem/{qrme_profile_id}/{id}` via the existing `life.vault_store` (so the key is tracked locally and `DELETE /data/{user}` purges the sealed exchanges along with everything else).
> - **Custody surfaced, never fatal** — the delivered guidance carries a `custody` block naming the vault key. A PDI outage never costs the user their guidance: sealing failure is reported as `{"vaulted": false, …}` in the payload, not raised.
> - **PDI does the proving** — `jim/` keys are already attributed to *JIM Guardian* by PDI's `/provenance` endpoint, sealed AES-256-GCM with tenant+key AAD binding, and hash-chained in the tamper-evident audit log. No PDI changes needed.
>
> ## Tests
>
> `jim/tests/test_tandem_custody.py` (JIM wired to both a FakeQRME and a FakePDI): sealed exchange content and key shape for a financial-stress tandem chat with `@marcus_bell`, local guidance carrying no custody record, right-to-erasure purging the sealed exchanges, and the vault-outage fallback (guidance still delivered, custody honestly reports unsealed).
>
> **194 passed** (190 existing + 4 new).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #53 — Native apps: show who stands behind the guidance

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-native-specialist` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/53>

> ## Summary
>
> The backend names the covering specialist on every guidance (#51) and marks tandem routing (#52), but the native guidance screens didn't surface either. All three clients now show the attribution:
>
> - **iOS** — `Guidance` gains `specialist` + `qrme_profile_id`; the shared `GuidanceExtras` view renders the attribution row with a green **LIVE · QRME** capsule when `source == "tandem"`. Monitor, Check-in, and Coach all inherit it.
> - **Android** — `Guidance` data class and `parseGuidance` pick up the two fields; `GuidanceExtras` renders the same attribution row + tandem badge for every screen that shows guidance.
> - **Windows** — `Guidance` record gains the fields; `MonitorPage` shows a `ResultSpecialist` line, and a shared `MonitorPage.FormatSpecialist` helper feeds the Check-in and Coach pages the same attribution (`… · LIVE VIA QRME` when tandem-routed).
>
> ## Verification
>
> Static only (no native toolchains in this environment): all `.xaml` parse as XML; brace/paren balance clean across `.swift`/`.kt`/`.cs`. Backend untouched — **190 tests pass**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #52 — Tandem hookup: wire starter specialists to QRME starter profiles

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-tandem-starters` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/52>

> ## Summary
>
> The starter specialists (#51) shipped in local mode with two labels intentionally matching QRME Starter Collection personas (qrme#71). This PR wires them together:
>
> - **`jim/seed.py`** — `TANDEM_HANDLES` maps the conditions with a genuine QRME domain counterpart: `financial_stress` → `@marcus_bell`, `physical_distress` → `@dr_amara_osei`. `seed_tandem(qrme)` upgrades those specialists to tandem mode by resolving each @handle **live** against the connected QRME deployment — profile ids differ per deployment, so handles are the stable cross-product names. `python -m jim.seed` runs the hookup automatically when `JIM_QRME_URL` is set.
> - **`jim/qrme_client.py`** — `resolve_handle()` speaks QRME's public `GET /summon?ref=@handle` (still no QRME code imported; the two products only interoperate over HTTP).
> - **`jim/api.py`** — `POST /specialists/seed/tandem`; 409 when no QRME endpoint is configured.
> - **Idempotent and operator-respecting**: existing tandem links (operator or prior run) are kept, unresolved handles leave their specialist local, and conditions without a real QRME counterpart are never wired.
> - Guidance for the wired conditions now routes through the matching live synthetic persona, with all existing tandem safety rails unchanged (minor/age-restriction gate, departed/suspended profile fallback, local fallback when QRME declines).
>
> ## Tests
>
> `jim/tests/test_tandem_starters.py`: mapping sanity (handle persona = local expert), linking with locals untouched, idempotency + operator-link preservation, end-to-end financial-stress guidance routed through `@marcus_bell` with the specialist attribution intact, 409 without QRME, and the unresolved-handle local fallback. `FakeQRME` now answers `/summon` for the starter handles.
>
> **190 passed** (184 existing + 6 new).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #51 — Seed starter specialists: a named domain expert per condition

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-starter-specialists` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/51>

> ## Summary
>
> A fresh Guardian deployment has an empty specialist registry — guidance works, but no named expert stands behind any condition. This PR seeds the cold start, mirroring QRME's Starter Collection (qrme#71):
>
> - **`jim/seed.py`** — `SPECIALISTS`: a curated named domain expert for every one of the 12 detectable conditions (e.g. *Dr. Elena Rios — cardiologist, resuscitation science* for cardiac events; *Marcus Bell — retired fee-only financial planner* for financial stress). `seed()` registers them in `local` mode, idempotently: conditions that already have a specialist are skipped, so operator overrides — including `tandem` upgrades to QRME profiles — survive re-seeding. Runnable as `python -m jim.seed`.
> - **`jim/api.py`** — `GET /specialists` lists the registry; `POST /specialists/seed` runs the seeder.
> - **`jim/guardian.py`** — guidance now names the covering specialist (`delivered["specialist"]`) in both local and tandem modes, so seeding is visible in every delivered guidance.
> - Several labels intentionally match QRME Starter Collection personas (Marcus Bell, Dr. Amara Osei) for a later tandem hookup.
>
> ## Tests
>
> `jim/tests/test_starter_specialists.py`: full condition coverage with distinct experts, registry listing after seeding, idempotency + operator-override preservation, `specialist` attribution on cardiac guidance, and the unseeded baseline (no attribution).
>
> **184 passed** (179 existing + 5 new).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #50 — Language at the setup gateway, translate-anything tool, and delivery modes

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-translate-gateway` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/50>

> Three additions to the language system:
>
> ## 1. Language at the setup gateway
>
> `POST /enroll` accepts a `language`, applied before the first response ever reaches the user. All three native Welcome screens gain the picker (populated from the public `/languages` catalog), so a Spanish speaker's very first guidance — playbooks included — arrives in Spanish.
>
> ## 2. Translate anything (`POST /translate/{user_id}`)
>
> Anything the user runs across — a note, a message, a document snippet — translates into their language (or an explicit `to` target) through a three-tier pipeline: **hand translations win** for known safety strings, **the user's own model** translates free text, and **the offline stub says it cannot** (`engine: "stub"` + note, original returned) rather than pretending. All three clients gain a Translate tool on the Overview screen showing the translation and which engine produced it.
>
> ## 3. Delivery mode: pre-translated vs on-demand
>
> The language preference now carries a `mode`:
> - **`pre`** (default): everything drafted for the user arrives already translated — the existing behavior.
> - **`on_demand`**: originals are kept (some users want the original medical text) and the Translate tool covers selective translation.
>
> Guidance generation, coaching, the CPR/AED playbooks, waiver terms, and robot CPR coaching all honor the mode; flipping back to `pre` restores in-language delivery immediately. A "Pre-translate everything" toggle rides on every client's language card.
>
> ## Verification
>
> - 4 new tests: gateway enrollment with language (first guidance in Spanish), unknown-language rejection, on-demand mode keeping originals + round-trip back to pre, and the translate tool's hand/explicit-target/stub-honesty/invalid-target paths.
> - Full suite: **179 passed**. XAML parses clean; brace/paren balance passes.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #49 — Hand-translate safety content into all supported languages

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-all-languages` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/49>

> Extends the hand-translated safety content from Spanish + French to **every language in the catalog**: German, Portuguese, Italian, Japanese, Chinese, Hindi, and Arabic join them — 20 safety strings × 9 languages.
>
> ## What's covered in all nine languages
>
> - The full **CPR playbook** (6 steps) and **AED playbook** (6 steps).
> - The **pace cues** (green/red light cue, 110-bpm metronome line).
> - All six **autonomous-resuscitation waiver terms**, so the liability waiver a user signs reads in their own language.
>
> `/languages` now reports `safety_content_translated: true` for all ten entries, so the native pickers' "(safety steps in English)" caveat disappears everywhere.
>
> ## Design unchanged, now enforced
>
> Translations remain string-keyed against the exact English source — an edit to the English falls back *loudly* to English rather than drifting. A new **completeness test** locks the invariant: every safety string must be covered in every supported language, and every playbook step and waiver term must be keyed to a translation entry, so a future English edit or a partial translation fails CI instead of shipping silently.
>
> ## Verification
>
> - Updated tests: Japanese playbook assertions, unknown-string fallback, full-coverage guard.
> - Full suite: **175 passed**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #48 — Per-user language + verifiable guidance provenance

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-language-provenance` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/48>

> Two cross-cutting guarantees for every guidance surface: users receive everything in **their language**, and every piece of advice shows **where it came from** — publisher, document, URL — so it can be verified at the source instead of taken on faith.
>
> ## Language (`/languages`, `GET/PUT /language/{user_id}`)
>
> - **Model-generated text** (guidance counsel, coaching, robot speech) is *generated in-language* via a system-prompt directive — a configured LLM answers natively rather than translating after the fact. The offline stub can't translate free text, and responses honestly say so via `translation_note` instead of pretending.
> - **Safety-critical deterministic content is hand-translated** (Spanish and French today): the full CPR and AED playbooks, the 110/min pace cues, and the autonomous-resuscitation waiver terms. Translations are string-keyed against the English source, so an edit to the English falls back *loudly* to English rather than silently drifting — safety text is never machine-mangled. Robot CPR coaching (`guide_first_aid`) speaks the localized playbook.
> - Ten languages in the catalog; those without hand-translated safety content keep English safety steps, flagged visibly in every client's language picker.
> - All three native apps (iOS / Android / Windows) gain the language picker on the Overview screen, beside the model picker — user setting, persisted server-side, applied to everything drafted or received.
>
> ## Provenance (`provenance` on every guidance and coach response)
>
> - **Structured evidence per condition** — publisher, document title, URL, and what each source supports: AHA Hands-Only CPR (the source of the playbook's 110/min pace), Red Cross AED steps, WHO, NHS, APA, CDC, OSHA, CFPB, Mayo Clinic, and the 988 Suicide & Crisis Lifeline.
> - **Method transparency**: whether the text is a *deterministic playbook transcribed from the cited publishers* or *model-generated counsel grounded in them*, plus **which model** produced it (`generated_by`) — so the platform's outputs are auditable rather than a black box.
> - A verify-at-the-source disclaimer travels with every response.
> - All three native clients render the derivation trail beneath the advice on Monitor, Check-in, and Coach.
>
> ## Verification
>
> - 10 new tests (`test_language_provenance.py`): language catalog + validation, hand-translated Spanish CPR / French AED steps, waiver-term localization, robot coaching in-language, English fallback for uncovered languages, and provenance shape/citations on cardiac, anxiety, and coach responses.
> - Full suite: **173 passed**. XAML parses clean; brace/paren balance passes on all three clients.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #47 — Autonomous-resuscitation waiver: signed liability waiver unlocks automatic CPR + auto-AED

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-resuscitation-waiver` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/47>

> Enrolled users who **sign a liability waiver** pre-authorize fully automatic operation of their CPR-rated robots. The design mirrors FDA-approved **fully-automatic AEDs**, which already deliver shocks with no button press after warning bystanders to stand clear — the waiver replaces the human button-press, while the clinical decision stays with the device.
>
> ## The waiver (`/waivers/{user_id}`)
>
> - **GET** returns the terms and signed state. **POST** signs it: requires explicit `accept: true` and a typed legal-name signature that must match the enrolled name; signing is recorded in the events audit trail. **DELETE** revokes it at any time, restoring confirm-gated operation.
> - Terms spell out exactly what is authorized: automatic CPR on detection, fully-automatic AED operation, liability acceptance, EMS-first, revocability — and that a shock is *only ever delivered when the AED's rhythm analysis advises it*.
>
> ## What a signed waiver unlocks
>
> - `perform_cpr` starts **without** the on-scene confirmation step (result notes "pre-authorized by waiver").
> - New **`auto_defib`** command engages the full sequence: EMS called → fully-automatic AED pads attached → device analyzes rhythm (compressions paused) → robot verifies everyone is clear (vision + audible warning) → **shock delivered automatically ONLY if the device advises it**, otherwise compressions resume.
> - Cardiac escalations direct perform-rated bodies (Optimus, Figure 03, Atlas) to `auto_resuscitate_cpr_plus_auto_aed`, tagged "autonomous resuscitation pre-authorized".
>
> ## Invariants, waiver or not
>
> - The AED's rhythm analysis is the **only** shock decision-maker — never the robot's own judgement.
> - Assist-rated bodies never gain compression or shock roles (the rating gate is independent of the waiver).
> - Compressions pause for AED analysis and stop when a human responder takes over.
> - Without a waiver, nothing changes from the previous PR: confirm-gated CPR, and no shock is ever delivered.
> - Every signing, revocation, and command lands in the audit trail.
>
> ## Native clients (iOS / Android / Windows)
>
> Safety → Robots gains the waiver card: full terms, typed-signature signing, SIGNED badge, and one-tap revoke. Once signed, CPR-rated bodies show **Start CPR (pre-authorized)** and **Auto-resuscitate** in place of the two-step confirm flow; revoking restores it.
>
> ## Verification
>
> - 7 new tests (`test_waiver.py`): terms, signature/acceptance validation, `auto_defib` locked without waiver, unlock + sequencing, assist-rating independence, revocation restoring gates, escalation directive upgrade. Full suite: **163 passed**.
> - XAML parses clean; brace/paren balance passes on all three clients.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #46 — Robots as first-aid responders: rated CPR/AED roles, plus playbook rendering

- merged · opened 2026-07-24 · merged 2026-07-24
- `claude/jim-robot-first-aid` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/46>

> Gives the Guardian's bound robots a real first-aid role — modeled on how machine-delivered compressions actually work today (LUCAS/AutoPulse-class mechanical CPR) — and fixes the gap where the native apps silently dropped the first-aid playbook and crisis references the backend was already sending.
>
> ## Backend
>
> - **Catalog**: adds the current humanoid generation — **Tesla Optimus, Figure 03 (Figure AI), Atlas (Boston Dynamics), Unitree G1** — and a per-model `first_aid` rating capturing the competitive variance: `perform` (force-controlled, mechanical-CPR-class: Optimus, Figure 03, Atlas) vs `assist` (fetch-and-coach: NEO, G1, U1 series, Memo, Isaac 1). Vacuums stay unrated — their emergency job is clearing the floor.
> - **Commands** (new `POST /robots/{uid}/{rid}/command`): rated bodies unlock `fetch_aed`, `guide_first_aid` (speaks the CPR/AED playbook aloud with the 110/min pace cue), and `meet_responders`; perform-rated bodies add `perform_cpr`/`stop_cpr`.
> - **Safety model, explicit in code and API**: `perform_cpr` is a deliberate **two-step** — the robot returns `confirmation_required` and does not touch the person until someone on scene confirms they are unresponsive and not breathing normally. **No rating ever authorizes a shock**: rhythm analysis stays with the AED, and the shock button stays with a human. Compressions pause for AED analysis and stop when a human takes over. Every command lands in the events audit trail.
> - **Escalation**: cardiac detections (fibrillation / arrest) upgrade robot directives by rating — `begin_hands_only_cpr_110bpm_until_aed_or_ems` (perform), `fetch_aed_and_coach_cpr_pace` (assist) — while non-cardiac escalations keep the existing `navigate_to_user` / `dock_and_clear_floor` behavior.
> - **Tests**: 10 new (`test_robot_first_aid.py`) covering ratings, allowlist gating, the confirm gate, playbook coaching, and cardiac vs non-cardiac directives. Full suite: 156 pass.
>
> ## Native (iOS / Android / Windows)
>
> - **Monitor and Check-in now render** the structured `first_aid` playbook (numbered CPR/AED steps, call-EMS banner, the 110/min · 30:2 pace with light/audio cues) and the guidance `references` — including the **988 Suicide & Crisis Lifeline** — which all three clients previously discarded.
> - **Safety → Robots** shows each body's rating badge (CPR-rated / first-aid assist) and offers Fetch AED / Coach CPR / Meet EMS; perform-rated bodies get Perform CPR behind an explicit in-UI confirmation step (mirroring the API gate) and Stop CPR while compressions run.
>
> ## Verification
>
> - All XAML parses clean; brace/paren balance checks pass on the new Swift/Kotlin/C#.
> - `python3 -m pytest`: **156 passed**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #45 — Native apps: add Connect (sources, social, apps) and fold Care tab

- merged · opened 2026-07-23 · merged 2026-07-23
- `claude/jim-native-connect` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/45>

> Adds the **Connect** surface to all three native clients — consented data sources, social-platform connections, and the connected-apps catalog — completing tenant-facing parity with `jim/api.py`. To make room, Monitor, Check-in, and Coach fold into a single segmented **Care** tab on the phone form factors, so the bottom bars land at five destinations (Overview · Care · Life · Safety · Connect).
>
> ## What's included
>
> - **iOS (SwiftUI)**: new `ConnectView` (Sources / Social / Apps segmented) and `CareView` (Monitor / Check-in / Coach segmented, reusing the existing views). `ApiClient` gains `SourceRow`, `SocialConn`, `CatalogApp`/`CatalogProvider`/`AppsCatalog`, `AppConn` and the ten Connect endpoints (`/sources`, `/social` connect + collect/publish, `/connectors/catalog`, `/apps` connect + collect).
> - **Android (Compose)**: `ConnectScreen` with Sources / Social / Apps `TabRow` panels (green consent switches, platform chips, collect/publish actions, catalog with Connect/Collect) and `CareScreen` wrapping the three existing screens; matching models and methods on `ApiClient`; bottom bar rewired to the five-tab layout.
> - **Windows (WinUI 3)**: new `ConnectPage` Pivot (sources toggles, social connections, apps catalog) and a Connect sidebar item; matching records and calls on `ApiClient`. The `NavigationView` sidebar scales, so Monitor/Check-in/Coach stay flat there.
> - READMEs updated: the "not yet wired" scope note is gone — the scaffolds now cover the full tenant-facing surface.
>
> ## Verification
>
> - All XAML parses clean (`xml.dom.minidom`).
> - Brace/paren balance checks pass on the new Swift/Kotlin/C#.
> - Backend untouched: 146 pytest tests pass.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #44 — Native apps: add the Medical ID card to Safety

- merged · opened 2026-07-23 · merged 2026-07-23
- `claude/jim-native-medicalid` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/44>

> ## Summary
> Fourth Safety segment on iOS/Android/Windows (**SOS / Med ID / Policy / Robots**):
>
> - **Issue (or rotate)** the first-responder Medical ID via `POST /medical-id/qr/{uid}`; the printable/lock-screen QR URL is shown.
> - The public card view (`GET /medical-id/{token}` — the card is the credential, no auth) renders **exactly what a responder would see**: name, age, resting HR, declared conditions, emergency contact — condition-level facts only.
> - **Revoke** (`DELETE /medical-id/qr/{uid}`) kills the card; rotating invalidates the old QR.
>
> ## Verification
> Static: all XAML/XML well-formed, braces/parens balanced. Backend untouched — `pytest` **146 passed**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #43 — Native apps: add Safety (SOS/policy/robots) and the model picker

- merged · opened 2026-07-23 · merged 2026-07-23
- `claude/jim-native-screens` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/43>

> ## Summary
> Brings the iOS/Android/Windows native scaffolds up to date with the new backend surfaces. One new **Safety** destination (iOS segmented / Android TabRow / Windows Pivot) plus a model picker in Overview:
>
> - **SOS** — the Emergency button → `POST /emergency/{uid}` with optional situation + location; renders the ordered coordinated-response flow (call → notify → locate → medical ID → guide) and any robot directives.
> - **Policy** — the escalation ladder from `GET /escalation-policy/{uid}` (how each severity resolves under the current dial), with the sensitivity picker wired to `PUT /sensitivity/{uid}`.
> - **Robots** — bind guardian responders from `GET /robotics/catalog` via `POST /robots/{uid}`; each bound body shows live status and its on-escalation directive (mobile → comes to you, vacuum → docks & clears floors).
> - **Overview** gains the model picker (`GET /models`, `GET/PUT /model/{uid}`) so a user chooses which LLM powers coaching and guidance.
>
> ## Verification
> Static: all XAML/XML well-formed (incl. the new `JimRedBrush` resource), braces/parens balanced. Backend untouched — `pytest` **146 passed**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #42 — Robot helpers as guardian responders (catalog, binding, escalation directives)

- merged · opened 2026-07-23 · merged 2026-07-23
- `claude/jim-robotics` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/42>

> ## Summary
> Same robotics catalog as QRME (`jim/robotics.py`; each repo ships its own copy): Isaac 1, NEO, UWorld U1 Lite/Pro/Ultra, Memo, Saros 20 / Saros 20 Sonic, Qrevo Curv 2 Flow. In JIM a bound robot is a **guardian responder**.
>
> ## Behavior
> - `POST /robots/{user_id}` binds a robot: it registers a `devices` row (so escalation alerts dispatch to it like any other device) and, for LLM-capable platforms, records which `jim.llm` provider rides onboard (defaults to the user's model preference)
> - **On escalation** — detection-driven or the Emergency button — every bound robot receives a role-appropriate directive: mobile bodies (humanoids, home robots) `navigate_to_user`; vacuums `dock_and_clear_floor` so floors are open for people and responders. Robots flip to `responding` status
> - `GET /robotics/catalog`, list, unbind; all per-user endpoints user-token gated
>
> ## Verification
> 7 new tests (catalog/directives, device registration, escalation + emergency directives, LLM rules, unbind, auth); **full suite 146 passed**. Screen 56 (Robot Helpers) rendered and verified.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #41 — Predictive early warning + escalation decision tree + Emergency flow

- merged · opened 2026-07-23 · merged 2026-07-23
- `claude/jim-early-warning-escalation` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/41>

> ## Summary
> Turns the Guardian from reactive to **anticipatory**, and makes every escalation an explicit, auditable decision. Two new transparent modules wired into the existing pipeline with zero behavior changes to prior paths (all 124 pre-existing tests pass unmodified).
>
> ## `jim/earlywarning.py` — the predictive algorithm
> Fits a least-squares trend line over each vital's recent readings (`heart_rate`, `respiratory_rate`, `hrv`, `blood_oxygen`) and projects **when it crosses the same danger thresholds the reactive rules use** — so prediction and detection always agree. A warning fires only when: the trend heads toward danger, the projected crossing lands inside the sensitivity lead-time window, and the fit is clean enough:
>
> | Sensitivity | Lookahead | Min R² |
> |---|---|---|
> | cautious | 30 min | 0.35 |
> | balanced | 20 min | 0.55 |
> | assertive | 10 min | 0.75 |
>
> Every forecast carries `risk` (0–1), `horizon_min`, `confidence` (R²), and the trend itself — fully explainable, never a black box.
>
> ## `jim/escalation.py` — the decision tree
> Ladder: `log → self_guidance → check_in → notify_contact → emergency_services`. `decide()` starts from severity, shifts by sensitivity (cautious +1 rung, assertive −1), applies explicit modifiers (declared-condition bump, low-confidence forecast cap, unreachable-contact reconciliation), and enforces **safety floors no dial can lower**: crisis language ⇒ `emergency_services`; critical ⇒ at least `notify_contact`. Returns the ordered `path` of rules that fired, so every decision can be replayed and defended.
>
> ## Wiring
> - `monitor()` enriches forecasts with risk/horizon/confidence and reports `escalation_decision` on every detection
> - `_escalate()` carries the tier + decision path into the event log (PDI-sealed via existing vault scopes)
> - `emergency()` returns the ordered watch/mobile `flow` (`armed → call → notify → locate → medical_id → guide`) plus its top-tier decision
> - New `GET /escalation-policy/{user_id}` — how the user's dial maps each severity, shown before anything happens (user-token gated)
>
> ## Screens & docs
> Screens **54 · Escalation Ladder** (sensitivity dial + tiers + safety floors) and **55 · Emergency Watch** (hold-SOS + 5-step coordinated flow); full write-up with the decision-tree diagram in `docs/early-warning-escalation.md`.
>
> ## Verification
> 15 new tests (trend projection, sensitivity windows, noise gate, tier resolution, floors, policy endpoint, monitor/emergency integration); **full suite 139 passed**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #40 — Let users pick their LLM provider (Claude/OpenAI/Grok/Perplexity/Gemini)

- merged · opened 2026-07-23 · merged 2026-07-23
- `claude/jim-llm-providers` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/40>

> ## Summary
> Mirrors the QRME provider selection in JIM's independent `llm` module: a registry with OpenAI-compatible (OpenAI, xAI Grok, Perplexity) and Gemini adapters alongside the Anthropic provider and deterministic stub. Each user chooses which model powers their coaching and guidance.
>
> ## Endpoints
> - `GET /models` — providers + configured flags + default
> - `GET /model/{user_id}` — the user's stored `provider` and `effective` resolution (user-token gated — this is PHI-adjacent)
> - `PUT /model/{user_id}` — body `{provider}` ∈ `auto|anthropic|openai|grok|perplexity|gemini|stub`
>
> Choice is stored in a new `model_prefs` table; `coach.reply`, the ambient companion, and `guidance.generate` route through `llm.provider_for_user`.
>
> ## Design guarantees
> - **A health app must never go dark on a model outage** — any network provider that errors degrades to the deterministic stub and logs it.
> - **Offline is absolute** — `JIM_OFFLINE` bypasses every network provider regardless of choice.
> - stdlib `urllib` only (matches `jim.cloud`), **no new dependencies**.
>
> ## Verification
> 6 new tests; **full suite 124 passed**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #39 — Grow JIM native apps: Coach + Life (goals/habits/journal) screens

- merged · opened 2026-07-23 · merged 2026-07-23
- `claude/jim-native-grow` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/39>

> ## Summary
> Grows the existing native clients (iOS SwiftUI, Android Jetpack Compose, Windows WinUI 3) with two new destinations, wired to backend endpoints that previously had no native screen. No backend changes.
>
> ## New screens & wire contracts
> - **Coach** → `POST /coach/{uid}` (`{area, message}`, area ∈ the six `LifeArea` values) → renders the coach reply
> - **Life** — one screen grouping three panels behind a segmented switcher:
>   - **Goals** → `GET /goals/{uid}` + `POST /goals/{uid}` (`{area, title}`)
>   - **Habits** → `GET /habits/{uid}` + `POST /habits/{uid}` (`{name}`) + `POST /habits/{uid}/{id}/log`
>   - **Journal** → `GET /journal/{uid}` + `POST /journal/{uid}` (`{text}`)
>
> Grouping Goals/Habits/Journal under **Life** (iOS `Picker`, Android `TabRow`, Windows `Pivot`) keeps each nav bar at five destinations. ApiClient gains the matching wire models/methods on all three platforms (Android/Windows also gain a `coach` call).
>
> ## Verification
> Static checks only (no native toolchain on Linux CI): all XAML/XML well-formed, braces/parens balanced across every `.swift`/`.kt`/`.cs`, `Symbol` enum values valid. `python3 -m pytest -q` → **118 passed** (backend untouched).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #38 — Add per-assistant screens: Apple Intelligence, Google Gemini, Microsoft Copilot

- merged · opened 2026-07-23 · merged 2026-07-23
- `claude/jim-assistant-screens` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/38>

> ## Summary
> Adds three dedicated per-assistant drill-down screens (51 Apple Intelligence, 52 Google Gemini, 53 Microsoft Copilot) to the mobile screen gallery. Each screen lists the on-device apps the assistant reaches (collect) and its headline capabilities (act / produce).
>
> ## Changes
> - `docs/screens/build.py`: new portable `assistant` hero (no `icon()` calls), parameterized by `provider` (apple/google/microsoft). Three new `SCREENS` entries (51–53, `accent="cyan"`).
> - Six new SVGs (iOS + Android).
> - `README.md`: gallery cells for the three screens.
>
> ## Verification
> - `python3 docs/screens/build.py` runs clean (106 screens).
> - Rendered all three to PNG and eyeballed: 13-chip Apple screen wraps cleanly; capability cards clear the JIM tab bar.
> - `python3 -m pytest -q` → 118 passed (backend untouched).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #37 — Add simple Files & Photos device-connector screen (50)

- merged · opened 2026-07-23 · merged 2026-07-23
- `claude/jim-files-photos` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/37>

> Simple connector surface — Files/Folders and Photos on iOS, Android, Windows — alongside the Connected Apps catalog (both kept). Screen **50 · Files & Photos**. Generator-only; rendered and verified no clipping.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #36 — Add Knowledge Excursions screen (49)

- merged · opened 2026-07-23 · merged 2026-07-23
- `claude/jim-excursions-screen` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/36>

> Adds the missing screen for the Guardian's safe-knowledge-excursions feature (`jim/research.py`): a condition being studied with a **SANITIZED** brief showing `[private]` redactions, "nothing left the host · local model," and findings folded into guidance context. Screen **49 · Knowledge Excursions** (iOS + Android), README gallery updated.
>
> Generator-only change; rendered and verified no clipping; full suite **118 green**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #35 — Safe knowledge excursions: study a topic without leaking the user's PHI

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/jim-knowledge-excursions` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/35>

> ## Summary
>
> When the Guardian needs to study an unfamiliar condition, treatment, or topic to help, it can gather **general knowledge without carrying the user's PHI out**, then bring it back for the local model.
>
> - **Sanitized brief** — the user's name and their emergency contact's name, plus caller-marked private terms, are redacted. General medical topics (e.g. "managing type 2 diabetes") survive; the person they belong to never leaves. `brief` is auditable.
> - **Nothing private leaves** — offline (`JIM_OFFLINE=1`) the gather runs on the local provider (no network); even with a cloud model only the sanitized brief is sent (`left_host` reports whether anything did).
> - Findings fold into the user's **guidance context** as a knowledge note (`POST /excursions/entry/{id}/learn`); the local model then uses them.
>
> ## Endpoints
>
> `POST/GET /excursions/{user_id}` · `GET /excursions/entry/{cid}` · `POST /excursions/entry/{cid}/learn`
>
> ## Tests
>
> 4 new tests (brief redacts user + contact, caller private terms, nothing leaves by default/offline, learn folds into context). **Full suite 118 passing.**
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #34 — App connectors: connect a catalog app and use it (collect · act · produce)

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/jim-app-connectors` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/34>

> ## Summary
>
> Makes the connected-apps catalog usable for the Guardian. A user connects to a catalog app (Apple Calendar, Google Gmail, Canva, …), granting a capability subset; the Guardian's agents then **collect** context (consented, informs guidance) or **invoke** a granted capability (`act` / `produce`).
>
> ## Endpoints
>
> | Method | Path | Purpose |
> |--------|------|---------|
> | POST | `/apps/{user_id}` | connect a catalog app |
> | GET | `/apps/{user_id}` | list |
> | DELETE | `/apps/connector/{cid}` | revoke |
> | POST | `/apps/connector/{cid}/collect` | pull context → guidance |
> | POST | `/apps/connector/{cid}/invoke` | run a granted capability |
>
> Connecting a collect-capable app consents its source; ungranted capability / unsupported direction refused. New `jim/app_connectors.py`, `app_connectors` table, models, inline routes.
>
> ## Tests
>
> 5 new tests. **Full suite 114 passing.**
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #33 — Connected-apps catalog: Apple, Google, Microsoft & Canva connectors

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/jim-connector-catalog` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/33>

> ## Summary
>
> Beyond the 16 social platforms, the Guardian and its agents can connect to the **AI-integrated apps** on a person's devices — Apple Intelligence, Google Gemini, Microsoft Copilot, Canva. Adds a connector **catalog** capturing them, each with `capabilities` and `directions` (`collect` · `act` · `produce`).
>
> ## Endpoint & screen
>
> - `GET /connectors/catalog` returns the catalog grouped by provider.
> - New **Screen 48 · Connected Apps** (iOS + Android).
>
> ## Tests
>
> 3 new tests. **Full suite 109 passing.**
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #32 — Support all 16 connection platforms from the suite set

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/jim-all-platforms` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/32>

> Expands the social-platform set from 8 to the full **16** the suite connects to. Adds **WhatsApp, Meta, Mastodon, Twitch, Snapchat, Roblox, Pinterest, Discord**, each with a presence-URL template for its QR beacon. The Social Connections screen shows the full platform palette.
>
> Test covers connecting all 16 and the new beacons' presence URLs. Full suite **106 passing**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #31 — Social connections: collect posts into guidance, publish via QR beacon

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/jim-social-connections` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/31>

> ## Summary
>
> A social-platform **connection** layer for the Guardian, in two directions:
>
> - **collect** — pulls the account's posts *in* as **consented context** that informs guidance. Connecting a collector auto-consents the `social:<platform>` source; revoking withdraws it, so nothing is ingested without consent. Items are sealed in the PDI vault when configured.
> - **publish** — shares an update *on* the platform (a milestone, an all-clear), reachable by a **QR beacon** (`segno`).
>
> ## Endpoints
>
> | Method | Path | Purpose |
> |--------|------|---------|
> | POST | `/social/{user_id}` | connect a platform |
> | GET | `/social/{user_id}` | list connections |
> | DELETE | `/social/connection/{cid}` | revoke (withdraws source consent) |
> | POST | `/social/connection/{cid}/collect` | ingest posts → guidance context |
> | POST | `/social/connection/{cid}/publish` | share an update |
> | GET | `/social/connection/{cid}/beacon` | presence URL + QR path |
> | GET | `/social/connection/{cid}/qr.svg` | the QR beacon |
>
> ## Also
>
> - New `jim/social.py`, a `social_connections` table, models, and **Screen 47 · Social Connections** (iOS + Android).
>
> ## Tests
>
> 4 new tests (collect consents + ingests, publish + beacon/QR, direction guards, revoke withdraws consent). **Full suite: 105 passing** (was 101).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #30 — Scaffold native iOS, Android and Windows apps for JIM Guardian

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/jim-native-apps` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/30>

> ## Summary
>
> Three **true-native** client scaffolds for JIM Guardian, one idiomatic codebase per platform (the "native per platform" choice), all wired to the existing JIM backend. Additive alongside the Electron desktop app.
>
> | Platform | Stack | Run in | Folder |
> | --- | --- | --- | --- |
> | iOS | Swift + SwiftUI | Xcode Simulator (macOS) | `native/ios/` |
> | Android | Kotlin + Jetpack Compose | Android Studio emulator | `native/android/` |
> | Windows | C# + WinUI 3 (Windows App SDK) | Windows 10/11 | `native/windows/` |
>
> ## What each app does
>
> The same first slice, exercising the real API end to end and persisting the returned `user_token`:
>
> **Welcome / Enroll** → `POST /enroll` · **Overview** → `GET /baseline` · **Live Monitoring** → `POST /monitor` · **Check-in** → `POST /checkin`
>
> All three share the JIM dark-OLED palette. Host defaults are per-platform correct: `127.0.0.1:8000` for iOS/Windows, `10.0.2.2:8000` for the Android emulator.
>
> ## Run
>
> Each folder's README has exact commands. In short:
>
> - **iOS:** `cd native/ios && xcodegen generate && open JimGuardian.xcodeproj` → ⌘R
> - **Android:** open `native/android` in Android Studio → Run (or `./gradlew installDebug`)
> - **Windows:** open `native/windows/JimGuardian.csproj` in VS 2022 → F5 (or `dotnet run -r win-x64`)
>
> Backend first: `JIM_CORS_ORIGINS=* uvicorn jim.api:app`.
>
> ## Status
>
> Purely additive — a new `native/` directory that does not touch the Python backend, so merging it does not affect backend CI (**118 tests green** on this branch, now up to date with main). Statically reviewed: XML/XAML/manifest well-formedness, XcodeGen YAML, and brace balance all check out, and the Android review cleanups are included.
>
> **Still needs a real toolchain build** (Xcode / Android Studio / Windows App SDK) to compile and run — expect minor first-build fix-ups. Merging lands the scaffold; the pattern can then be replicated to QRME and PDI.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)

## #29 — Record post-0.1.0 onboarding screens in the changelog

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/jim-changelog-unreleased` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/29>

> ## Summary
>
> The provider-login and first-run onboarding screens added since **v0.1.0** (Log In, Permissions, About You, Emergency Contacts, All Set) weren't reflected in the changelog. This records them under `## [Unreleased]` so the next release notes stay honest.
>
> Docs-only. No code changes.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #28 — Add first-run onboarding flow (Permissions → About You → Contacts → All Set)

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/jim-onboarding` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/28>

> ## Summary
>
> Fills in the first-time-setup screens so a brand-new user is guided from **Welcome** and **Log In** all the way to a ready, protected profile — then out again at **End Session**.
>
> ## New screens (43–46)
>
> | # | Screen | What it does |
> |---|--------|--------------|
> | 43 | **Permissions** | Toggle what Jim can access — notifications, health & motion, emergency access, location |
> | 44 | **About You** | Name, known conditions, and what matters most (feeds the Guardian's sensitivity) |
> | 45 | **Emergency Contacts** | Who Jim can reach and who it will alert |
> | 46 | **All Set** | Confirmation the Guardian is watching |
>
> The full journey now reads **01 Welcome → 42 Log In → 43 Permissions → 44 About You → 45 Emergency Contacts → 46 All Set → … → 41 End Session**.
>
> ## Changes
>
> - Four new hero renderers (`consent`, `aboutyou`, `contacts`, `ready`) in `docs/screens/build.py`, built from existing primitives.
> - Regenerated for both **iOS** and **Android**; README gallery + first-run note updated.
>
> Rendered and visually verified. Purely additive.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #27 — Add Apple/Google/email Log In screen

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/jim-auth-screen` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/27>

> ## Summary
>
> Adds a provider **Log In** screen (screen 42) — *Continue with Apple / Google / Email* — so JIM-mini onboards through the same single suite account as QRME and PDI. The vault still unlocks with Face ID after sign-in.
>
> ## Changes
>
> - New `auth` hero in `docs/screens/build.py` with `apple_mark` / `google_mark` / `envelope` helpers (shared idiom across the three repos).
> - Screen spec `42 · Log In` added; regenerated for both **iOS** (`docs/screens/`) and **Android** (`docs/screens/android/`).
> - README screen gallery updated.
>
> Rendered and visually verified. Purely additive — no existing screens changed.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #26 — Per-platform code signing (macOS vs Windows certs independent)

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/per-os-signing` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/26>

> ## Summary
>
> The signed build fed the **same** `CSC_LINK` to every OS, so adding only a macOS certificate would make the **Windows** job try to sign with the Apple `.p12` and fail the whole release. Make signing **per-platform and opt-in**: macOS uses `CSC_LINK`, Windows uses `WIN_CSC_LINK`, Linux never signs. Each platform sees only its own cert. Docs updated.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #25 — Build a universal (Intel + Apple Silicon) macOS dmg

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/universal-mac` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/25>

> ## Summary
>
> The macOS build produced an **arm64-only** dmg, leaving Intel Macs uncovered. Switch the `mac` target to a single **universal** binary that runs natively on both Intel and Apple Silicon.
>
> Next tagged release produces `…-universal.dmg` in place of the arm64-only one.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #24 — Fix desktop-release packaging (electron-builder)

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/fix-desktop-packaging` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/24>

> ## Summary
>
> Mirrors the QRME packaging fix, surfaced by a dry run of `desktop-release.yml`:
>
> 1. **Empty `CSC_LINK` broke the build** — electron-builder treats an empty-string cert path as a file and fails. Split into a **signed** build (cert secret present) and an explicitly **unsigned** build (`CSC_IDENTITY_AUTO_DISCOVERY=false`).
> 2. **Missing package metadata** made `computeChannelNames` throw `Cannot read properties of null (reading 'channel')`. Added `author` + `repository` and set `build.publish: null`.
>
> Installers package unsigned by default, signed when secrets are configured. Renderer build unchanged.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #23 — Use RELEASE_NOTES.md as the GitHub Release body

- merged · opened 2026-07-22 · merged 2026-07-22
- `claude/release-notes-body` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/23>

> ## Summary
>
> The desktop-release job used `generate_release_notes: true` only, so the curated `RELEASE_NOTES.md` wasn't used. Point the release at it (`body_path: RELEASE_NOTES.md`, with a checkout so the file is present); the auto-generated changelog is still appended.
>
> No behavior change until an `app-v*` tag is pushed. Prep for cutting v0.1.0.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #22 — Backend image, release notes, releasing & HIPAA BAA docs

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/jim-release-ops` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/22>

> ## Summary
>
> Closes the remaining open items before v0.1.0.
>
> - **`Dockerfile` + `.dockerignore`** for the backend image — used by the suite full-stack e2e harness (in the qrme repo) and for standalone deployment.
> - **`RELEASE_NOTES.md`** — ready-to-paste v0.1.0 GitHub Release body.
> - **`docs/releasing.md`** — tag→build→sign→release flow and the optional signing secrets.
> - **`docs/hipaa-baa.md`** — maps HIPAA Security Rule safeguards to what JIM already implements (per-user tokens, AES-256-GCM at rest, hash-chained audit, user-visible access log, erasure), plus a pre-production checklist and a **Business Associate Agreement template**. The BAA signature is the legal/ops step; the safeguards are already in code.
>
> ## Testing
>
> Docs/infra only; `pytest` (101) and the console smoke build are unchanged.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #21 — Release polish: CHANGELOG, CONTRIBUTING, project URLs

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/jim-release-polish` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/21>

> ## Summary
>
> Release scaffolding for v0.1.0 (docs only, no behavior change):
>
> - **CHANGELOG.md** — Keep a Changelog format, v0.1.0 feature summary (monitor→predict→guide→escalate, life layer, medical ID, provider handoff, PDI vault, data ownership, apps).
> - **CONTRIBUTING.md** — dev setup, PHI-handling guidance, decoupling, PR flow.
> - **pyproject** — add `Homepage` and `Changelog` project URLs.
>
> ## Testing
>
> Docs/metadata only; `pytest` (101) and the console smoke build are unchanged. TOML validated.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #20 — CI: smoke-build the guardian console on every PR

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/jim-ci-app-smoke` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/20>

> ## Summary
>
> Adds an `app` job to CI that runs `npm ci && npm run build` in `app/`, so every PR proves the JIM guardian desktop console still type-checks and builds — matching the smoke-build jobs already in the QRME and PDI repos so the whole suite has build coverage.
>
> Skips the Electron binary download (`ELECTRON_SKIP_BINARY_DOWNLOAD=1`) — the renderer build doesn't need it.
>
> ## Testing
>
> - `npm run build` (console) — clean type-check + Vite build locally.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #19 — Add a runnable JIM guardian console (React + Vite + Electron)

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/jim-desktop-app` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/19>

> ## What this adds
>
> A **real, runnable guardian console** wired to the JIM-mini API — React + TypeScript + Vite, wrapped in **Electron** for an installable desktop binary, plus a per-OS CI release workflow.
>
> ### `app/` — the console
> - **`api.ts`** — typed JIM client (enroll, monitor, checkin, coach, baseline).
> - **screens**:
>   - Onboarding → `POST /enroll`
>   - Overview → `GET /baseline/{user}`
>   - Live Monitoring → `POST /monitor/{user}` — **detect → guide → escalate**, with guidance content + clinical references
>   - Coach → `POST /coach/{user}`
>   - Check-in → `POST /checkin/{user}` (surfaces guardian flags)
>   - Privacy → `GET /health` (tandem status), sign out
> - **`electron/`** wrapper; README with run + release instructions.
> - **`.github/workflows/desktop-release.yml`** — macOS/Windows/Linux matrix building `.dmg`/`.exe`/`.AppImage` on tag `guardian-v*`, signing via repo secrets.
>
> ### Backend
> - `create_app()` gains **optional CORS** (`JIM_CORS_ORIGINS`, off by default). All 101 tests still pass.
>
> ## Verified end to end
> Driven against a live backend with headless Chromium: enrolled, submitted a biometric sample → **guardian detected anxiety with guidance + references**, logged a check-in, and asked the coach — all round-trip. `tsc + vite build` clean; build artifacts gitignored.
>
> ## Run
> ```bash
> JIM_CORS_ORIGINS='*' uvicorn jim.api:app
> cd app && npm install && npm run dev          # or npm run electron:dev / npm run dist
> ```
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #18 — Add session-lifecycle screens; fix renderer-opaque white tints

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/jim-lifecycle` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/18>

> ## What this does
>
> Completes the mockup journey (**sign in → running → end session**) and cleans up a rendering bug that affected many screens.
>
> - **Two new mobile screens** (both platforms): **Sign In** (returning-user unlock) and **End Session** (session summary + Sign Out; "Guardian keeps watching in the background"). 41 screens × 2 platforms.
> - **Cleanup:** white overlay fills used 8-digit hex alpha (`#ffffff10`, `#ffffff12`, `#ffffff22`, `#ffffff55`), which some SVG converters render **opaque** — turning ghost buttons and chat bubbles into solid white blocks. All converted to `rgba()`, so they render correctly everywhere (phone + watch generators).
> - **Verified the app runs:** `pytest` passes (101 tests) and the FastAPI app boots.
>
> ## Notes
>
> - Additive/cleanup — generators + regenerated SVGs + README; no backend code touched.
> - Branch reset off latest `main`.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #17 — Add iOS/Android and macOS/Windows platform chrome variants

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/jim-platforms` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/17>

> ## What this adds
>
> Every screen now ships in **each platform's native OS chrome**, from the same generators — no content duplicated, only the frame.
>
> - **Mobile** (`docs/screens/build.py`): **iOS** (Dynamic Island notch, iOS status icons, home indicator) → `docs/screens/`; **Android** (punch-hole camera, Android status icons, three-button gesture nav) → `docs/screens/android/`. 39 screens × 2 platforms.
> - **Desktop** (`docs/desktop/build.py`): **macOS** (traffic-lights, rounded window) → `docs/desktop/`; **Windows** (caption min/max/close, squarer window) → `docs/desktop/windows/`. 6 views × 2 platforms.
> - The **watch** stays watchOS-only.
>
> A shared `PLATFORM` / `PLATFORM_D` switch drives the chrome. The README grows a **Platforms** comparison band.
>
> ## Notes
>
> - Pure additive — docs/assets + README; no app code touched.
> - Branch reset off latest `main` (prior PRs #13–#16 merged).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #16 — Add the Jim Mini desktop app — wide guardian workspace

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/jim-desktop` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/16>

> ## What this adds
>
> A **desktop** form of Jim Mini alongside the phone app and the watch — one world, three products, in the guardian-green identity accent.
>
> - **`docs/desktop/build.py`** — generates 6 self-contained desktop-window SVGs (1280×820) with a sidebar nav, top bar, and a workspace of panels. It **reuses the mobile generator's icon + colour library** so the galleries stay one system; tints use `rgba()` for renderer-agnostic output. Regenerate with `python3 docs/desktop/build.py`.
> - **The views:**
>
> | # | View | Content |
> |---|---|---|
> | 01 | Overview | Vitals tiles, heart-rate chart with baseline line, learned-baseline ring, recent guardian events, today |
> | 02 | Live Monitoring | Elevated vitals + rising HR chart + the detect→guide→escalate timeline |
> | 03 | Health | Tiles, resting-HR 14-day trend, monthly summary, foresight sparklines |
> | 04 | Emergency & Guardian | Coordinated response (Call 911), Medical ID, providers & handoff |
> | 05 | Coach & Life | Life-coach areas, goal bars, proactive insights, habit streaks |
> | 06 | Privacy & Data | Connected sources, devices, model & cloud, offline |
>
> - **`README.md`** grows a **Desktop app** section above the phone and watch galleries.
>
> ## Notes
>
> - Pure additive — docs/assets + README only; no code paths touched.
> - Branch started fresh off `main` (prior galleries PRs #13/#14/#15 are merged).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #15 — Complete the screen galleries: fill gaps + renderer-safe tints

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/jim-screens-complete` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/15>

> ## What this does
>
> Rounds out both screen galleries so **every capability has a screen**, and fixes a rendering bug on tinted surfaces.
>
> ### New screens
>
> - **Phone (34 → 39):** Rate Guidance, Counselor Style, History, Baseline, Tandem Specialist.
> - **Watch (22 → 34):** Breathe, Feedback, Journal, Coach, Baseline, Sources, Privacy, Handoff, Offline, Known Conditions, Counselor Style, History.
>
> ### Tint fix (renderer-agnostic)
>
> Chip/pill/ring backgrounds and the feedback tiles used 8-digit hex alpha (`#rrggbbaa`), which some SVG converters (e.g. cairosvg) render **opaque** — hiding same-coloured icons and labels. A shared `A(hex, alpha)` helper now emits `rgba()`, which is honoured everywhere; the watch generator imports it from the phone module. All existing SVGs were regenerated, and the README galleries rebuilt to include every screen.
>
> ## Notes
>
> - Branch started fresh off `main` (the prior gallery PRs #13/#14 are already merged).
> - Regenerate with `python3 docs/screens/build.py && python3 docs/watch/build.py`.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #14 — Add watch-screen gallery: the same system on the wrist

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/jim-watch-screens` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/14>

> ## Summary
>
> **22 glanceable Apple-Watch faces** (`docs/watch/*.svg`), one per capability, in the product's dark-OLED style — generated by `docs/watch/build.py`, which **reuses the phone generator's icon and colour library** so both galleries stay pixel-identical in style.
>
> - **Everyday (1–10):** Home, Talk, Voice, Health (2×2 complication tiles), Heart, Rings, Daily Briefing, Streak, Check-in, Insight.
> - **Guardian & emergency (11–16):** Live Monitoring, Foresight, Emergency SOS, **CPR** (compression ring + pace light), **Medical ID** (QR), Sensitivity dial.
> - **Ambient, data & system (17–22):** Ambient Jump-in, Companion, Notifications, Devices/Continuity, Guardian status, Settings.
>
> Watch-appropriate layout throughout: rounded case with a **digital crown + side button**, time top-right, glanceable tiles / activity rings / hero graphics, and page dots — matching the watch mockup sheet.
>
> ## Notes
>
> - Verified renders with cairosvg (Health tiles, CPR ring, activity rings, SOS all clean and on-brand).
> - Each SVG is static + self-contained, so it renders inline on GitHub.
> - No application code changed; `JIM_LLM=stub python3 -m pytest jim/tests -q` → **101 passed**.
>
> ## Docs
>
> README gains a grouped **Watch screens** gallery (22 faces across 3 sections), beneath the phone gallery.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #13 — Add app-screen gallery: a screen for every capability

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/jim-app-screens` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/13>

> ## Summary
>
> **34 full-colour SVG app screens** in the product's dark-OLED style — one per capability — generated by `docs/screens/build.py` and embedded in the README as a grouped gallery.
>
> - **Core (1–12):** Welcome, Home, Chat, Voice, Daily Briefing, Health, Memories, Profile, Goals, Finance, Emergency, Settings.
> - **Guardian & health (13–20):** Live Monitoring, **CPR Coach** (compression ring + pace light + 30:2), Emergency Response, **Medical ID** (rendered QR), Foresight, Sensitivity dial, Known Conditions, Providers.
> - **Life layer (21–27):** Habits, Check-in, Journal, Life Coach, Insights, Companion, Ambient Jump-in.
> - **Data / privacy / system (28–34):** Connected Sources, Privacy & Data, Devices, Continuity, Notifications, Progress Report, Model & Cloud.
>
> Every screen maps to a shipped endpoint. `docs/screens/build.py` is a small self-contained generator — a component library (device frame, cards, chips, drawn vector icons, sparklines, meters, hero graphics like the CPR ring and the QR) plus a data-driven screen list — so the whole set regenerates deterministically with `python3 docs/screens/build.py`.
>
> ## Notes
>
> - Colour-matched to the existing mockups (dark OLED, purple→blue orb, colored icon chips, tab bar); native SF type; each SVG is static and self-contained so it renders inline on GitHub.
> - No application code changed; `JIM_LLM=stub python3 -m pytest jim/tests -q` → **101 passed**.
>
> ## Docs
>
> README gains a grouped **App screens** gallery (34 thumbnails across 4 sections).
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #12 — Wire the Medical ID into a shareable, scan-to-view QR

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/jim-medical-id-qr` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/12>

> ## Summary
>
> A first responder can scan a printable / lock-screen QR and read the user's Medical ID **without unlocking the phone** — the card itself is the credential.
>
> - `medical_cards` table + `guardian.issue/rotate/revoke/resolve_medical_card`: an opaque `med_` token per user, stored **only as its SHA-256 hash**; issuing again rotates it (the old QR stops resolving).
> - `POST /medical-id/qr/{user_id}` (user-token gated) — mint/rotate; returns the token, `view_url`, and `qr_svg_url`. `DELETE` revokes.
> - `GET /medical-id/{token}` (public) — resolves the scanned token to the condition-level Medical ID; **no auth token required** (locked phone). 404 on unknown/revoked.
> - `GET /medical-id/{token}/qr.svg` (public) — the printable QR (`segno`, medical red on white) encoding the view URL.
> - `segno` added to dependencies; `medical_cards` purged on erasure.
>
> The Medical ID is condition-level only (name, age, known-condition labels, resting-HR baseline, emergency contact, recent detections) — no notes or raw biometrics — matching the real medical-ID-on-lock-screen model.
>
> ## Testing
>
> New `jim/tests/test_medical_id_qr.py` (7): issue + no-auth scan returning condition-level facts only; the QR SVG served (and gone after revoke); rotation invalidating the old code; revoke killing the card; unknown-token 404; issue requiring the user's own token; hashed-at-rest + erased. `JIM_LLM=stub python3 -m pytest jim/tests -q` → **101 passed**.
>
> ## Docs
>
> README gains the `/medical-id/qr` and scan-to-view rows.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #11 — Add Emergency mode: one coordinated response

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/jim-emergency-mode` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/11>

> ## Summary
>
> Wires the product's **Emergency screen** (Call 911 · Share Location · Contact Family · Medical ID · AI Guidance) into a single coordinated endpoint.
>
> - `POST /emergency/{user_id}` (user-token gated) → `guardian.emergency()`:
>   - **call_emergency_services** — the services action + number (region note).
>   - **share_location** — when a location is passed, shared with the emergency contact and responders.
>   - **contact_family** — notifies the registered emergency contact.
>   - **medical_id** — a first-responder Medical ID: name, age, known-condition labels, resting HR (learned baseline if established, else enrolled), emergency contact, recent detections. Condition-level facts only — no notes or raw biometrics, and no provider-consent gate (it's the user's own info).
>   - **ai_guidance** — runs detection over an optional live `sample`/`situation` and delivers the matching first-aid playbook (CPR/AED/low-oxygen/…); falls back to general steps when a situation is described but nothing specific is detected.
>   - **dispatched_alerts** — every registered connected device is alerted.
>   - the whole event is logged (`medical/emergency` vault scope).
> - `EmergencyRequest` model (`situation`, `location`, `sample` — all optional).
>
> ## Testing
>
> New `jim/tests/test_emergency.py` (4): the full bundle from a low-O₂ sample (services, location shared with family, contact notified, Medical ID, low-oxygen first aid, device alerts); the no-input case still reaching services + Medical ID; general guidance when a situation has no detection; and event logging + token gating (another user's token → 403). `JIM_LLM=stub python3 -m pytest jim/tests -q` → **94 passed**.
>
> ## Docs
>
> README gains the `/emergency` API row.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #10 — First-aid layer: CPR/AED playbooks, hazards, ergonomics, SpO₂ forecast

- merged · opened 2026-07-21 · merged 2026-07-21
- `claude/jim-first-aid` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/10>

> ## Summary
>
> Implements the physical-conditions counseling passage of the Guardian spec — first aid for physical injuries and abnormalities, with an autonomous coordinated response. (Matches the product mockup's Emergency Mode → "AI Guidance — Get step-by-step instructions".)
>
> **Detection** (`jim/conditions.py`; cardiac patterns outrank the generic collapse rule):
> - `rhythm: fibrillation` → `cardiac_event` critical (**AED** path).
> - `fall`/`collapse` with an absent pulse or HR < 30 → `cardiac_event` critical (suspected arrest, **CPR** path); a plain collapse stays `physical_injury`.
> - **Environmental hazards** from connected sensors: smoke/CO air quality or CO ≥ 9 ppm → critical (leave-now); `poor` air → guidance.
> - **Ergonomic risk factors**: slouched/hunched/awkward posture or ≥ 45 min of repetitive motion → guidance-level strain warning.
> - New `BiometricSample` fields: `rhythm`, `pulse`, `air_quality`, `co_level`, `posture`, `repetitive_motion_min`.
>
> **First aid** (`jim/guidance.py`): physical detections carry a deterministic step-by-step `first_aid` block alongside the conversational guidance — **CPR** (30:2, pace cued at **110 compressions/min with green/red lights and a metronome audio tick**), **AED** steps, the **low-blood-oxygen** playbook (breathe deeply → fresh air → seek medical attention), environmental-hazard and ergonomic playbooks, plus references (AHA/Red Cross/CDC/OSHA).
>
> **Coordinated response** (`guardian._escalate`): critical escalations **dispatch alerts to every registered connected device** (`dispatched_alerts`), so the nearest embodiment surfaces the guidance.
>
> **Predict before it manifests**: three strictly declining SpO₂ readings ending ≤ 94% (still above the 90% threshold) raise a forecast + insight.
>
> ## Testing
>
> New `jim/tests/test_first_aid.py` (7): CPR with pace cues + device dispatch, AED on fibrillation, plain collapse unchanged, the low-O₂ playbook wording, smoke/CO/poor-air severities, ergonomic guidance without escalation, and the SpO₂ slide forecast. `JIM_LLM=stub python3 -m pytest jim/tests -q` → **90 passed**.
>
> ## Docs
>
> `docs/guardian-internals.md` detection ladder + first-aid section; README `/monitor` row.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #9 — Docs: escalation diagram, data promise, security section update

- merged · opened 2026-07-20 · merged 2026-07-20
- `claude/jim-docs-cleanup` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/9>

> ## Summary
>
> Final cleanup items 3–5 (JIM's share) — no code changes.
>
> - `docs/diagrams/escalation.svg` — the Guardian decision tree: crisis check first, the transparent rule ladder (sensitivity dial and learned baseline noted), and the three outcomes (info/forecast, guidance, critical) with the never-withheld-guidance footnote; linked from `guardian-internals.md`.
> - README **"Your data promise"** — vaulted PHI with key references only, the user-visible access log, numbers-only prediction, consent-gated provider portal, and full erasure.
> - `docs/tandem.md` security section updated to reality (same text as QRME's copy): capability-token auth across all three apps, the user-visible access log, HIPAA access-log item moved to implemented.
>
> ## Testing
>
> Docs only; `JIM_LLM=stub python3 -m pytest jim/tests -q` → **83 passed** (unchanged). SVG validates as XML.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #8 — Cross-product session continuity: resume the QRME thread on any device

- merged · opened 2026-07-20 · merged 2026-07-20
- `claude/jim-session-continuity` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/8>

> ## Summary
>
> Cleanup item #2 — a conversation begun with a QRME specialist now follows the user across products and devices.
>
> - `tandem_links` stores the QRME interactor's **capability token** alongside its id; `qrme_client.ensure_interactor` returns `(id, token)` and the new `thread_memory()` reads the shared thread back with it (the urllib client now passes headers).
> - `guardian.start_session(qrme=…)` returns a `continuity` block when the user has an existing specialist thread: the specialist profile, the shared interactor id, and the recent turns — so a chat begun in QRME picks up on a kitchen console, wearable, or robot mid-conversation.
> - Standalone JIM (no QRME wired) and users without a thread report `continuity: null` — behavior unchanged.
>
> ## Testing
>
> New `jim/tests/test_continuity.py` (3): a new device session carries the thread's turns (the memory read is gated on the interactor token, like real QRME); no-thread and no-tandem cases stay null. `JIM_LLM=stub python3 -m pytest jim/tests -q` → **83 passed**.
>
> ## Docs
>
> README sessions row documents the continuity block.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #7 — Predictive early warnings beyond the heart-rate climb

- merged · opened 2026-07-20 · merged 2026-07-20
- `claude/jim-more-forecasts` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/7>

> ## Summary
>
> Cleanup item #1 — three more "catch it before it happens" signals, each a transparent trend rule:
>
> - **Sliding mood** — three strictly declining check-ins ending ≤ 3 raise a mental-health forecast before the low lands.
> - **Sleep debt** — three consecutive nights under 6.5 h flag the accumulated debt while tonight can still fix it.
> - **Spending acceleration** — the last three purchases totalling ≥ 2× the prior three raise a financial-stress warning even when no single purchase trips the high-spend alert.
>
> Because context payloads are vaulted under PDI, prediction runs on a new `trend_points` table holding **bare numbers only** (metric name + value — no categories, notes, or payloads). Forecasts land as `forecast` insights from check-in and context ingestion. Erasure now also removes `trend_points` **and `baselines`** (the latter was missing from `delete_user_data`).
>
> ## Testing
>
> New `jim/tests/test_forecasts.py` (5): each rule fires; non-patterns and a good-night reset stay silent; the spend forecast fires below the alert bar; the trend store holds numbers only and is erased. `JIM_LLM=stub python3 -m pytest jim/tests -q` → **80 passed**.
>
> ## Docs
>
> `docs/guardian-internals.md` documents the three rules under predictive early warning.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #6 — Reference a departed specialist's QRME memorial in the fallback note

- merged · opened 2026-07-20 · merged 2026-07-20
- `claude/jim-memorial-reference` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/6>

> ## Summary
>
> Companion piece to QRME #26 (memorial mode) — the "JIM can also reference it" half. When a tandem specialist profile has departed, JIM's fallback note now points the user to the profile's QRME memorial (`/profiles/{id}/memorial`) while still delivering standalone guidance — the memorial the tandem partner keeps is surfaced, not hidden behind a generic "departed" message.
>
> ## Testing
>
> New case in `test_adult_tandem_safety.py` proving guidance still arrives locally and the note carries the memorial path. `JIM_LLM=stub python3 -m pytest jim/tests -q` → **75 passed**.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #5 — User-facing "who accessed my data" access log

- merged · opened 2026-07-20 · merged 2026-07-20
- `claude/jim-data-access-view` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/5>

> ## Summary
>
> Medium item — revocable access tokens + audit visibility *for users*. PDI has a tamper-evident audit chain, but a JIM user had no way to see who accessed their own data. This surfaces it.
>
> - `jim/pdi_client`: `audit()` and `audit_verify()` fetch the tenant's audit log and chain-integrity status (None when unreadable).
> - `life.access_log(user_id, pdi)`: reads PDI's audit, **filters to the user's own `jim/{user}/` key namespace** (so one user never sees another's), renders each entry as a plain-language action (`stored`/`read`/`erased`) + scope + time, and reports `tamper_evident`. With no vault configured it says the data is stored locally on this system only.
> - `GET /access-log/{user_id}` (user-token gated).
>
> ## Testing
>
> New `jim/tests/test_access_log.py` (3): the log lists the user's vault accesses with friendly verbs and a verified chain; per-user isolation (plus a 403 reading another user's log); and the local-only message when no vault is configured. `JIM_LLM=stub python3 -m pytest jim/tests -q` → **74 passed**.
>
> ## Docs
>
> README API table documents the endpoint.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #4 — Guard tandem handoff: never connect a minor to an adult QRME profile

- merged · opened 2026-07-20 · merged 2026-07-20
- `claude/jim-adult-tandem-safety` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/4>

> ## Summary
>
> Medium item — adult-content handling across the tandem. JIM handed guidance to a QRME specialist profile without checking that profile's audience rating, and a QRME age-gate rejection (403) would **crash** the handoff instead of falling back.
>
> - `qrme_client.profile_info()` — fetches a QRME profile's public card (`adult_mode`, `status`), returning None when unreadable.
> - `guardian._tandem_safe()` — before a handoff, a **minor or unknown-age user is never connected to an `adult_mode` profile**, and a non-`active` profile is not used; either way JIM falls back to standalone guidance with a note. If the card can't be read, it proceeds and relies on QRME's own age-gate as the backstop.
> - `_deliver()` wraps the handoff so a QRME `RuntimeError` (e.g. its age-gate) falls back to local guidance rather than crashing.
>
> ## Testing
>
> New `jim/tests/test_adult_tandem_safety.py` (4). `JIM_LLM=stub python3 -m pytest jim/tests -q` → **71 passed**.
>
> ## Docs
>
> `docs/guardian-internals.md` gains a tandem-specialist-safety section.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #3 — Implement tunable sensitivity and rolling EMA baseline

- merged · opened 2026-07-20 · merged 2026-07-20
- `claude/jim-sensitivity-baseline` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/3>

> ## Summary
>
> Turns two `[planned]` Guardian specs into working, tested behavior.
>
> **Tunable sensitivity** (`cautious`/`balanced`/`assertive`): `conditions.detect` shifts the HR guidance/critical thresholds by ±10 bpm; cautious also notifies the emergency contact at guidance level for a **declared** condition. `PUT /sensitivity/{user_id}` + `sensitivity` column (default `balanced`).
>
> **Rolling per-metric baseline (EMA)**: new `baselines` table + `guardian.update_baseline` — a resting-state sample (`activity_level ≤ 3`, no condition) folds into the metric EMA (α=0.05). HR baseline seeded at enrollment; detection uses the learned baseline once ≥ 5 resting samples, else the seed. `GET /baseline/{user_id}` reports provisional state.
>
> ## Testing
>
> New `jim/tests/test_sensitivity_baseline.py` (8). `JIM_LLM=stub python3 -m pytest jim/tests -q` → **67 passed**.
>
> ## Docs
>
> README API table + `docs/guardian-internals.md` flipped both to `[implemented]`.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #2 — Ambient activity observation with proactive intervention

- merged · opened 2026-07-20 · merged 2026-07-20
- `claude/jim-ambient-intervention` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/2>

> ## Summary
>
> Backlog item #4 — the "Jiminy Cricket" proactive jump-in (the core magic). JIM only reacted to biometric samples and explicit check-ins; it had no way to watch what someone is *doing* and step in before being asked. This adds **ambient observation**.
>
> - `conditions.detect_ambient()` — a transparent, additive rule layer over an activity's signals: repeated attempts (`retries`/`errors`), a long stall (`idle_seconds`), frustration in what they said, a long stretch without progress. It decides when to offer help *before it's asked for*. New `FRUSTRATION` condition, `guidance` severity only — it never auto-escalates.
> - `guardian.observe_activity()` — logs the activity, runs the **crisis pipeline on the note first** (crisis language escalates exactly as elsewhere), then the ambient detector. A struggle raises a **proactive intervention** (delivered through the same local/tandem guidance path) plus an insight; a calm signal is logged and left uninterrupted.
> - `POST /activity/{user_id}` (user-token gated) + `ActivityObserve` model.
>
> ## Testing
>
> New `jim/tests/test_ambient.py` (4): the detection rules; a proactive intervention with its `activity`/`detection`/`guidance` events and ambient insight; a calm signal that is watched but not interrupted; and crisis language during an activity still escalating (contact + live support). `JIM_LLM=stub python3 -m pytest jim/tests -q` → **59 passed**.
>
> ## Docs
>
> README API table gains the `/activity` row.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

## #1 — Capability-token authentication for user data

- merged · opened 2026-07-19 · merged 2026-07-19
- `claude/jim-auth` → `main`
- Author: davidsbianchi1984
- Page: <https://github.com/davidsbianchi1984/jim-mini/pull/1>

> ## Summary
>
> JIM holds **PHI** — biometric streams, crisis notes, journals, provider summaries — yet identity was **self-asserted**: any caller who knew a `user_id` could read events/journal/provider data, ingest biometric samples, or erase a user. This adds **bearer capability tokens**.
>
> - `jim/auth.py` — issue/verify tokens; only the SHA-256 hash is persisted (`api_tokens`), so a DB leak yields no usable credential.
> - `POST /enroll` mints and returns `user_token` **once**.
> - Every `/{user_id}` endpoint now requires that user's token — folded into the existing `_user_or_404` gate, so it stays one line per endpoint. Missing/invalid → **401**; valid token for another user → **403**.
> - `DELETE /data/{user_id}` **revokes** the token along with the data.
> - **Open (no token):** `GET /health`, `GET /cloud/status`, `POST /enroll`, `POST /specialists` (service setup).
>
> The tandem direction is JIM→QRME (JIM as client), so JIM's own auth doesn't affect tandem guidance.
>
> ## Testing
>
> - New `jim/tests/test_auth.py` (6 tests): 401/403/200 gating, open setup surfaces, delete-revokes-token.
> - The `enroll` test helper carries the user token; multi-user tests switch explicitly.
> - `JIM_LLM=stub python3 -m pytest jim/tests -q` → **55 passed**.
>
> ## Docs
>
> README gains an **Authentication & access control** section.
>
> 🤖 Generated with [Claude Code](https://claude.com/claude-code)
>
> https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY
>
> ---
> _Generated by [Claude Code](https://claude.ai/code/session_015e8tKrkr36nt7UTKUPtELY)_

