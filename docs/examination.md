# JIM-mini — for examination

This page is written to be checked, not believed. Every section grounds the
product in three things: the **technical problem** in the machine, the
**implementation** as built — named modules, named constants, named tests —
and a **measurable effect** that follows from the implementation and not
from a description of it. Three rules hold throughout:

- **A photograph outranks a drawing.** Every `.png` under `docs/screens/`
  and `docs/walkthrough/` is a capture of the running console taken by
  `tools/shoot_screens.py` and `tools/walkthrough.py` against a live
  backend; an `.svg` is a design drawing and is captioned as one. The 36
  watch faces are drawings by design, and each links to the working face at
  jim-mini.com.
- **Every behaviour stated is held by a test.** The suite
  (`python -m pytest`, 3,300-plus cases) reads the README: the release
  banner, the release table, the gallery, the screen numbering, the screen
  count and the closing passage all fail the build when they drift from the
  product.
- **Nothing is claimed that the product does not do.** Where a behaviour is
  deliberately held shut — the 911 send — the page says so, and a test reads
  the source to prove the hold.

The safety ladder these mechanisms serve is set out in
[the README](../README.md#the-safety-path-as-built), and the screens
referred to below are shown in [the README](../README.md#screenshots).

## The mechanisms on file

The seven numbered mechanisms in the invention disclosure. Each row names
the technical problem in the machine, the particular structure this code
uses to solve it, what that structure changes about how the machine
behaves, and where the structure is reduced to practice and held by a
test. None of them is a rule a person could follow with a pen; each is a
specific arrangement of data, channels and checks inside a running
system, and each is photographed on the screens below.

<table width="100%">
<thead>
<tr>
<th width="4%" align="left">§</th>
<th width="23%" align="left">The technical problem</th>
<th width="30%" align="left">The particular solution, as built</th>
<th width="26%" align="left">What it changes in the machine</th>
<th width="17%" align="left">Reduced to practice in</th>
</tr>
</thead>
<tbody>
<tr>
<td valign="top">1</td>
<td valign="top">A wrist sensor's readings are held inside a vendor's phone application and reach no other program without an application-store app.</td>
<td valign="top">A <strong>deposit-only channel</strong>: one URL per person carrying a per-person token, accepting a forgiving reading payload from the phone's own automation, with no read door on the same channel; and a <strong>fold</strong> that parses the phone's health export into the person's baseline without generating events.</td>
<td valign="top">Readings arrive at the guardian from a device the guardian has no application on, over a channel that cannot be read back, and the baseline exists before the first live reading.</td>
<td valign="top"><code>jim/<wbr>watch.py</code> — <code>test_<wbr>watch.py</code>,<br><code>test_<wbr>the_<wbr>wrist_<wbr>is_<wbr>a_<wbr>surface.py</code></td>
</tr>
<tr>
<td valign="top">2</td>
<td valign="top">Fixed clinical thresholds fire on an individual whose normal sits far from the population's, and stay silent on drift inside the population's range.</td>
<td valign="top">Two independent evaluation layers over every sample: a <strong>personal drift band</strong> computed from the person's own readings and a sensitivity setting, and a <strong>clinical alarm layer</strong> of fixed condition rules; each layer decides alone and both land on the escalation ladder.</td>
<td valign="top">A drift inside clinical range can open a check-in, and a clinical alarm can never be lowered by a personal setting; the two cannot mask each other.</td>
<td valign="top"><code>jim/<wbr>guardian.py</code>,<br><code>jim/<wbr>earlywarning.py</code>,<br><code>jim/<wbr>conditions.py</code> — <code>test_<wbr>sensitivity_<wbr>baseline.py</code>,<br><code>test_<wbr>the_<wbr>baseline_<wbr>screen_<wbr>is_<wbr>the_<wbr>home_<wbr>of_<wbr>limits.py</code></td>
</tr>
<tr>
<td valign="top">3</td>
<td valign="top">A plausible but wrong reading from a loose sensor, or a reading delayed for minutes in transit, drives an escalation as if it were true and current.</td>
<td valign="top">Every sample carries a <strong>quality</strong> and a <strong>staleness contract</strong> (device-stamped observation and send times, so device clock skew cancels out of the age); the escalation ladder reads both and <strong>caps the highest reachable rung</strong> by them, and a stranger's beacon scan is capped below contacting the person's own circle.</td>
<td valign="top">A poor or old signal can still open a check-in, and can never ring a contact or reach the held emergency send; the ladder's path is written down step by step and replayable.</td>
<td valign="top"><code>jim/<wbr>signal.py</code>,<br><code>jim/<wbr>freshness.py</code>,<br><code>jim/<wbr>escalation.py</code> — <code>test_<wbr>escalation_<wbr>tree.py</code>,<br><code>test_<wbr>signal_<wbr>quality.py</code>,<br><code>test_<wbr>how_<wbr>old_<wbr>is_<wbr>the_<wbr>reading.py</code></td>
</tr>
<tr>
<td valign="top">4</td>
<td valign="top">A model served over a network fails, is rate-limited, or is unreachable exactly when a health assistant is being asked for guidance.</td>
<td valign="top">A <strong>provider chain with a deterministic local floor</strong>: every provider error degrades to the offline stub rather than raising; every answer carries <strong>provenance</strong> — which provider produced it and, if degraded, from what — and the degrade is logged.</td>
<td valign="top">The assistant always answers, and the person and the record can tell a model's words from the stub's.</td>
<td valign="top"><code>jim/<wbr>llm.py</code> — <code>test_<wbr>byo_<wbr>key.py</code>,<br><code>test_<wbr>the_<wbr>study_<wbr>says_<wbr>who_<wbr>answered.py</code></td>
</tr>
<tr>
<td valign="top">5</td>
<td valign="top">A desktop shell can adopt whatever backend answers its port, including a stale one left running from an earlier version.</td>
<td valign="top">The shell reads the backend's <strong>version from <code>/<wbr>health</code></strong> and compares it to its own before adopting it; a mismatch is refused and shown.</td>
<td valign="top">A stale backend cannot be mistaken for the current one.</td>
<td valign="top"><code>jim/<wbr>_<wbr>_<wbr>main_<wbr>_<wbr>.py</code>,<br><code>app/<wbr>src</code> (<code>VersionGuard</code>) — <code>test_<wbr>accounts.py</code> (<code>test_<wbr>health_<wbr>reports_<wbr>the_<wbr>version</code>)</td>
</tr>
<tr>
<td valign="top">6</td>
<td valign="top">Every alarm in a monitor fires on a reading; a person on the floor with the sensor on its charger produces no reading and no alarm.</td>
<td valign="top">The <strong>vigil</strong> measures silence itself against the person's own event table — any sign of life is already an event, so activity resets the clock with no bookkeeping — and a <strong>ticker</strong> advances that clock on the server without anything reading it.</td>
<td valign="top">The absence of signals becomes an alarm condition that fires at three in the morning with every screen closed.</td>
<td valign="top"><code>jim/<wbr>vigil.py</code>,<br><code>jim/<wbr>ticker.py</code> — <code>test_<wbr>vigil.py</code>,<br><code>test_<wbr>the_<wbr>clock_<wbr>advances_<wbr>without_<wbr>a_<wbr>read.py</code></td>
</tr>
<tr>
<td valign="top">7</td>
<td valign="top">Three products that must share a person's memory, specialists and custody without sharing code or a database.</td>
<td valign="top">Three separately deployable services that interoperate over <strong>HTTP only</strong> with <strong>one tenant and one token per integration</strong>; the guardian keeps only key references locally and seals the sensitive payload in the vault; one version number is cut across the three.</td>
<td valign="top">A product can be replaced or moved without the others importing anything from it, and the sensitive record lives behind the vault's seal rather than in the guardian's database.</td>
<td valign="top"><code>jim/<wbr>qrme_<wbr>client.py</code>,<br><code>jim/<wbr>pdi_<wbr>client.py</code> — <code>test_<wbr>pdi_<wbr>tandem.py</code>,<br><code>test_<wbr>tandem.py</code></td>
</tr>
</tbody>
</table>

## Where each highlight is proven

Each row: the technical problem, the implementation with its own numbers, the test that holds it, and the photograph.

| Highlight | The technical problem | As built, with its numbers | Test | Screen |
|---|---|---|---|---|
| Offline is enforced at every socket | A privacy promise made in prose leaks through one forgotten HTTP call. | `jim/offline.py` refuses every non-loopback connect at the socket layer while the gate is up; no module opts in. | `test_nothing_leaves_the_host.py` | 23 |
| Ten languages, refusals included | A refusal in English to a reader in Arabic is a wall, not an answer. | `jim/i18n.py` keeps every refusal sentence as a constant with ten translations; a refusal raised anywhere is rendered through it. | `test_the_guardian_refuses_in_one_language.py` | every screen |
| Ability is not a gate | A screen that needs a mouse locks out the person the guardian exists for. | `app/src/screens/Access.tsx` exposes every control to keyboard and reader; the guard reads the markup rather than trusting a checklist. | `test_ability_is_not_a_gate.py` | 37 |
| The wrist channel and the watch | A watch app needs a store, a phone pairing and a vendor account before it shows one number. | `jim/watch.py` serves the face as one HTTP payload a browser on the wrist reads; 36 faces are drawn from the same rows; `native/wear/` is the same face packaged. | `test_watch.py`, `test_the_wrist_is_a_surface.py`, `test_the_watch_you_actually_wear.py` | 12, faces 01–36 |
| The personal baseline and every limit on one screen | Population thresholds fire on the wrong person and stay silent on the right one. | `jim/guardian.py` keeps a per-person resting baseline as an exponential average with `_BASELINE_ALPHA = 0.05`, provisional until `_BASELINE_MIN_SAMPLES = 5`; every limit is set on one screen and rounds up. | `test_sensitivity_baseline.py`, `test_the_baseline_screen_is_the_home_of_limits.py` | 08, 13 |
| Bring your own model key | A key in the server's configuration is every caller's key. | `jim/llm.py` reads the caller's key from one request header into a context variable for that request only; never stored, never logged. | `test_byo_key.py` | 15 |
| The coach, grounded in the vault and the watched pages | A model answering from its training answers about somebody else. | `jim/coach.py` conditions every answer on the person's sealed records; `jim/lookout.py` keeps watched pages fresh and says when one changed. | `test_the_lookout.py`, `test_the_lookout_grows_ears.py` | 07 |
| Signal quality caps the escalation | A loose sensor's plausible reading escalates as if it were true. | `jim/signal.py` carries a trust score per sample and no escalation rises above `TRUST_FLOOR = 0.5`; `jim/freshness.py` expects a heartbeat every `HEARTBEAT_MS = 90000` ms and keeps the last 500 readings for the judgement. | `test_how_old_is_the_reading.py` | 08 |
| The medicine cabinet | A dose forgotten and a dose doubled look the same to a reminder that only rings. | `jim/meds.py` records each dose taken against its schedule; the next reminder is computed from the record, not the clock alone. | `test_meds.py` | 17 |
| The care circle | Everyone in a family getting every alarm is nobody getting the right one. | `jim/careteam.py` holds roles and reach order; each escalation step names who was tried and how. | `test_careteam.py` | 18 |
| The money guardian | A rate limit on a card is a rule the bank keeps, not the person. | `jim/money.py` keeps the person's own ceilings and refuses over them before the request leaves. | `test_the_money_guardian.py` | 13 |
| Beacons and the rota | A printed code at a door that points somewhere new is a door that lies. | `jim/beacons.py` deactivates rather than deletes; `jim/rota.py` keeps who is on duty when the code is scanned. | `test_beacons.py` | 31 |
| The engaged session and its permits | An assistant session that outlives its owner's attention acts alone. | `jim/engaged.py` binds a session to a person's presence; `jim/permits.py` grants each reach as a revocable row. | `test_an_engaged_session_reaches_no_further_than_its_owner.py` | 38, 39 |
| The agent's hands and look permits | An agent that can see the screen can see everything on it. | `jim/hands.py` grants a look per screen per permit; the agent's hands reach the theme and the list switches, and nothing else. | `test_the_agents_hands_reach_the_look.py`, `test_the_guardian_gets_eyes_and_hands.py` | 42 |
| Widgets that cannot leave their box | A model-written widget runs in the page that holds the session. | `jim/widgets.py` serves each widget in a sandboxed frame with no ambient credential. | `test_the_widget_cannot_leave_its_box.py` | 40 |
| The moderated mailbox | Mail answered by a model in the person's name leaves before the person sees it. | `jim/mailbox.py` holds every outbound letter in a queue the person approves. | `test_the_moderated_mailbox.py` | 44 |
| The training corpus and the learn task | A local model cannot learn from exchanges nobody kept. | `jim/corpus.py` banks each exchange; the learn task plants itself when capture is on and archives the bank itself. | `test_the_training_corpus.py`, `test_the_learn_task_plants_itself.py` | 43 |
| App edits held for company oversight | A change a user proposes to the app lands nowhere, or lands everywhere. | `jim/appedits.py` holds each proposal as a row with a state; the reviewer's queue is a screen; `BOX_SLOTS = 2` bounds how many are tried at once. | `test_the_held_screens_buttons_match_the_wire.py` | 45 |
| The coding assistant's box — a draft tried inside four walls before a person judges it | A model's patch run on the server is the model running the server. | `jim/workroom.py` runs each draft under `unshare -rmnp` as `nobody`, with `LIMITS` of 300 s wall, 240 s CPU, 2 GiB address space, 32 processes above the account's running count, 16 MiB per file and 64 KiB of output; the tree is read-only, hidden places are covered by a 64 MiB tmpfs, scratch is 256 MiB; at most `MAX_ROUNDS = 3` tries; a probe forks 400 processes before the box is trusted. | `test_the_assistant_gets_a_box.py`, `test_the_box_opens_on_the_hosted_cloud.py` | 40, 45 |
| The dialer is built to the send, and held shut | An emergency call placed by software is either impossible or already happening. | `jim/dialer.py` carries the whole cascade to a real telephony transport and keeps `SEND_ENABLED = False` in source; no setting, plan or waiver opens it. | `test_the_dialer_posture_is_proven.py` | — |
| Two guardians working together | Two people's guardians that cannot see each other cannot cover for each other. | `jim/family.py` links two guardians with a mutual, revocable grant; each sees only what the other allowed. | `test_two_guardians_working_together.py` | 25 |

