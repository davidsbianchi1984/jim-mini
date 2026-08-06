# Changelog

All notable changes to JIM-mini are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.47.3] — 2026-08-06

### A checker that invents work, for the fourth time

`clientpaths.py` finds a client's requests by looking for the call shapes it
knows and reading the path out of the arguments. A client is free to write a
shape nobody taught it, and then the audit reports a working door as missing.

That has now happened four times, and the file records all four: the nested
template literal, the `<img src>` with no callee, the `reqText` sibling of
`req`, and Android's direct-connection form. Every one was found the same way
— somebody went to build a door and found the door already there.

    asked     does the extractor understand the calls it knows about
    mattered  does the extractor know about all the calls

Every guard-on-guard already in that file checks the first question. This
round adds one for the second: **every path-shaped literal is either inside a
call form's arguments, or it is recorded with the reason it is not a request.**

It found `getArray("/goals/$uid", token)` immediately — a private helper in
this shell's Android client that opens its own connection, so the path sits at
the caller where no known opener encloses it. Six routes with working Android
doors had been sitting in `android_doorless.txt`.

Worth being precise about why nothing caught it earlier, because it is the
reason the new check is positional rather than set-based: those paths were not
invisible. Each was attributed under its **write** verb, from the
`request(path, "POST", …)` a few lines away. Only the GET was missing, and a
check comparing the paths a client mentions against the paths it calls reads
that as covered.

### The link a guardian could begin and not end

`DELETE /guardians/{guardian_id}/children/{child_id}` was honestly recorded as
doorless on Android and Windows — no measurement bug, just a missing control
on two shells out of three.

A guardian link is a standing relationship: one adult able to see another
person's events, light and escalations. It outlives the reason for it —
children grow up, custody changes, households end. iOS has been able to end
one since the link was built. On a phone that is not an iPhone, and on the
desktop, the person who set it up had nowhere to undo it.

Both shells now have the control, the confirmation, and the sentence saying
what unlinking does **not** delete: their account, their guardian and their
own record stay theirs. The six rows come back to those two tables, lifted
from the iOS wording rather than retyped.

**Android 147 → 140, Windows 141 → 140.** Six of the seven were never missing.

Cut together with QRME and PDI at app-v0.47.3.

## [0.47.2] — 2026-08-06

### The sign-out fix nobody carried across

QRME found this exact bug two releases ago and fixed it in its own copy of
this file: the Windows shell's **Sign out** sits in `NavigationView.PaneFooter`
and the loop that localizes the nav walks `Nav.MenuItems`, which the footer is
not one of. It said *Sign out* in every language.

Android has been asking for `action.sign_out` all along. Windows was not, and
its table did not even hold the row — so wiring the call was not enough on its
own. Both are fixed.

    asked     is the nav localized
    mattered  is every control in the nav localized

### Family, on all three shells at once

Family is where a parent enrols a child, chooses how much of that child's
record they get to see, and reads the sentence saying **the auto-defib waiver
can never be signed for a minor**. That sentence was English on every shell.

So were the oversight tiers, the device controls, the pause-and-quiet-hours
paragraph promising that monitoring and crisis escalation never pause, the
unlink confirmation, and the line saying an unlinked child keeps their own
account and their own record.

The scope on the card confirming a new child's account was worse than English
on two of the three: Android and Windows printed the API's own enum member,
`full` and `alerts_only`, raw, on a parent's screen. So did the sensitivity —
which iOS and Android were also rendering by capitalizing the wire value on
the Safety dial, three rounds after Windows started asking the table for those
same three words.

### Connect, and three promises no measurement could see

Connect is the door out to QRME's community rather than a second copy of it,
and the three promises that make that true — *Mirror the conversation here*,
*Post on your behalf*, *Share your health data* — were arguments to a helper
rather than the first thing inside a `Text(`, so no ratchet on any shell could
ever have counted them.

The tab strip above them was the other shape: on iOS the English lived in an
enum's raw values, in a `case` clause, where nothing looks.

**386 → 229.** iOS 113 → 70, Android 113 → 75, Windows 136 → 84.

### Every key named where a guard can see it

Four shapes of key were quietly invisible to the dead-key guard, and all four
are the dangerous direction — a guard that calls a live row dead is what
invites somebody to delete a row a screen is using:

* a key assembled at runtime (`"cw." + level`);
* a key chosen by a `switch`/`when` and handed to one lookup;
* a key chosen by a ternary whose condition contains a quote;
* a key passed to a helper as a bare literal.

Each branch now resolves on its own line, and the helpers take the finished
sentence rather than the key.

### Still open, and named

Windows and Android have no way to end a guardian link; only iOS does. Three
more pickers render an enum's raw values, on Care, Life and Safety. Both
belong to the rounds that take those screens.

Cut together with QRME and PDI at app-v0.47.2.

## [0.47.1] — 2026-08-06

### The alarm was localized where it speaks, not where you start it

The guard in this repo is the sibling's guard, copied. So the blind spot
found in 0.47.0 was here too: a string chosen by a ternary is not at the
start of an argument list, and nothing was looking anywhere else. The
recorded counts were understating by **40**.

What that hid is the part worth writing down.

Fourteen `alarm.*` rows were carved out in an earlier round, by name rather
than by count, because — in that round's own words — *a count cannot tell you
which string a person could not read*. They cover what the alarm **says**
once it is going: the question it asks, the three answers, the line admitting
this screen cannot call an ambulance.

They do not cover **Tap for emergency**. Or **Arm the crash watch**, or
**Issue Medical ID**, or **Rotate QR** — the controls that arm the alarm,
fire it, and stand it down. The carve-out was chosen by reading the count,
and the count could not see the button.

    asked     is the alarm's own wording localized
    mattered  is the control that starts it

### The whole safety surface, on all three shells

The SOS control and what it asks. The crash-watch dial, its sensitivity
floors, its trusted person. The **autonomous-resuscitation waiver** — the
consent that lets a machine start compressions and fire a fully-automatic AED
without an on-scene confirmation — and the sentence describing what signing
it means. The responder card a stranger reads off a locked phone. First aid,
including **📞 Call emergency services now**. The monitor, and the custody
proof with its hash-chain verdict.

**538 → 386.** iOS 183 → 128, Android 153 → 122, Windows 202 → 136.

### Two wordings and a missing card

The SOS button read *Tap for emergency* on the phones and *Click for
emergency* on the desktop. The escalation-floor sentence said *Crisis
language and critical events have floors* on two shells and dropped the word
*language* on the third.

And the failure-report card — settled in the sibling product at 0.46.6, three
shells saying one thing about what a crash report contains — was still
English on all three of JIM's. Its ten rows are taken verbatim from the
sibling's table rather than written a second time.

Cut together with QRME and PDI at app-v0.47.1.

## [0.47.0] — 2026-08-06

### Version alignment

The three products are cut together, so one number names one combination of
all three. No JIM code changed. QRME found that its native-shell
measurement could not see a string chosen by a ternary — `cond ? "Verifies" :
"Does not verify"` was invisible on every shell — corrected the count from 68
to 125, and then ran it to 7, none of which contains English.

## [0.46.9] — 2026-08-06

### Version alignment

The three products are cut together, so one number names one combination of
all three. No JIM code changed. QRME localized the six screens that exist
on all three of its shells — 212 English strings behind the tab bars down to
68 — and fixed a sign-out button on Windows that read "Sign out" in every
language because it sat outside the loop that localizes the navigation.

## [0.46.8] — 2026-08-06

### Version alignment

The three products are cut together, so one number names one combination of
all three. No JIM code changed. QRME finished the console that runs a
profile's public reach on all three shells — 368 English strings behind the
tab bars down to 212 — and replaced a US-only crisis number, shown in ten
languages, with the local-services wording this product settled on first.

## [0.46.7] — 2026-08-06

### Version alignment

The three products are cut together, so one number names one combination of
all three. No JIM code changed. QRME localized Signatures and Voice on all
three shells — 470 English strings behind the tab bars down to 368 — and
closed a gap where two cards had been done on two shells and missed on the
third.

## [0.46.6] — 2026-08-05

### Version alignment

The three products are cut together, so one number names one combination of
all three. No JIM code changed. QRME finished its settings screen and did
Community on all three shells — 590 English strings behind the tab bars down
to 470 — and fixed a relationship picker that had been rendering the API's
enum members as if they were words.

## [0.46.5] — 2026-08-05

### Version alignment

The three products are cut together, so one number names one combination of
all three. No JIM code changed. QRME's round was its phones: the first
screen and the settings screen localized on iOS, Android and Windows — 703
English strings behind the tab bars down to 590 — and its Android shell,
which turned out not to compile, fixed and guarded.

## [0.46.4] — 2026-08-05

### The voice picker had a label and the refusal did not use it

Settings has had `<label>{tr("set.voice", lang)}` over the voice picker
since the picker existed — **Voice**, *Voz*, *Stimme*, 音声 — and a 422 on
that field answered `voice_id`. The label is ported into `_FIELD_LABELS`
word for word rather than translated a second time, which is the same
reason the table is server-side at all: two wordings of one word is two
things to keep right, and the drift shows up first in the language nobody
here reads.

The record: 100 → 99.

Cut together with QRME and PDI at app-v0.46.4.

## [0.46.3] — 2026-08-05

### Version alignment

The three products are cut together, so one number names one
combination of all three. No JIM code changed. QRME's console-untranslated
record reached its floor this round: 25 → 1, the last three screens
translated and one row kept on purpose. JIM's own reached zero at
0.45.1.

## [0.46.2] — 2026-08-05

### Version alignment

The three products are cut together, so one number names one
combination of all three. No JIM code changed. QRME took four more
screens off its console record this round: 69 → 25.

## [0.46.1] — 2026-08-05

### Version alignment

The three products are cut together, so one number names one
combination of all three. No JIM code changed. QRME took three more
screens off its console record this round: 116 → 69.

## [0.46.0] — 2026-08-05

### Version alignment

The three products are cut together, so one number names one
combination of all three. No JIM code changed. QRME took three more
screens off its console record this round: 180 → 116.

## [0.45.9] — 2026-08-05

### Version alignment

The three products are cut together, so one number names one
combination of all three. No JIM code changed. QRME took three more
screens off its console record this round: 254 → 180.

## [0.45.8] — 2026-08-05

### Version alignment

The three products are cut together, so one number names one
combination of all three. No JIM code changed. QRME took three more
screens off its console record this round — 338 → 254 — and widened its
table-completeness check from the sidebar to all 1519 rows.

## [0.45.7] — 2026-08-05

### Version alignment

The three products are cut together, so one number names one
combination of all three. No JIM code changed. QRME took three more
screens off its console record this round: 425 → 338.

## [0.45.6] — 2026-08-05

### Version alignment

The three products are cut together, so one number names one
combination of all three. No JIM code changed — its own console record
sits at its floor of zero. QRME took three more screens off its record
this round: 516 → 425.

## [0.45.5] — 2026-08-05

### Version alignment

The three products are cut together, so one number names one
combination of all three. No JIM code changed — its own console record
sits at its floor of zero. QRME took three more screens off its record
this round: 616 → 516.

## [0.45.4] — 2026-08-05

### Version alignment

The three products are cut together, so one number names one
combination of all three. No JIM code changed — its own console record
sits at its floor of zero. QRME took three more screens off its record
this round: 724 → 616.

## [0.45.3] — 2026-08-05

### Version alignment

The three products are cut together, so one number names one
combination of all three. No JIM code changed — its own console record
sits at its floor of zero. QRME took three more screens off its record
this round: 848 → 724.

## [0.45.2] — 2026-08-05

### Version alignment

The three products are cut together, so one number names one
combination of all three. No JIM code changed — this console's own
record reached zero at 0.45.1 and stays there, held by its floor and
by `test_no_screen_of_this_console_speaks_only_english`. QRME took its
three largest remaining screens off its record this round: 978 → 848.

## [0.45.1] — 2026-08-05

### The console speaks ten languages, all of it

**The console-untranslated record runs to zero.** The nine screens that
were left — Safety, Aims, Community, Live Monitoring, Overview,
Check-in, Journal, Coach and the last four strings of the sign-in
page — are localized end to end: 129 strings become 125 keys in all ten
languages. Every screen of this console, pre-session and gated alike,
now reads its words out of the table.

The record file stays, its status changed from `backlog` to `floor` and
its ceiling set to **0**, because the guard reads it in both
directions: a single new English string on any screen fails the build.
A new test, `test_no_screen_of_this_console_speaks_only_english`, pins
the emptiness the way the doorless records were pinned — the ceiling
can be raised, but only by somebody who writes the row down and does it
on purpose in the same commit.

The measurement started at 603 and has been worked down over nine
rounds: 603 → 573 → 531 → 481 → 426 → 373 → 262 → 206 → 129 → **0**.

## [0.45.0] — 2026-08-05

### Three screens, and the record falls to 129

**What's held about you** — who holds it, who has read it, and the
sentence that refuses to let an empty access log mean two opposite
things — becomes twenty-four `hld.*` keys. **Who you watch** — the
child who keeps their own account and their own token, the board, and
the resuscitation waiver that must be read in full before it is
signed — becomes twenty-one `wrd.*` keys. **Care Team** — the QRME
organization the Guardian coordinates, where summaries cross and never
raw readings — becomes twenty-three `ct.*` keys.

Seventy-seven strings, all ten languages. The console-untranslated
record falls **206 → 129**, exact-sync held.

## [0.44.9] — 2026-08-05

### The cabinet and the guided hour speak the visitor's language

Two screens localized end to end. **Medications** — the day's doses,
the critical one that went unlogged, the as-needed ceiling JIM will
refuse to log past, and the promise that your own words are a valid
name and dose — becomes twenty-eight `med.*` keys. **Wellness** — the
guided calm that is a protocol rather than a generation, the workout
shaped to the minutes you have, and the day of meals — becomes
twenty-five `wel.*` keys. All ten languages. The console-untranslated
record falls **262 → 206**, exact-sync held.

## [0.44.8] — 2026-08-05

### The Control Center speaks — the largest block on the record

The Settings screen — the backend address, the model key that stays on
your device, the model picker with its honest warning about which
model actually answers, the voice, the watch channel and the Wi-Fi
truth about whether a phone can reach it, the vigil that fires on the
absence of readings, the mail setup, what JIM has learned about you,
your name here, what you contribute, and where to look — is localized
end to end: **111 strings, the largest single block left on either
console**, become eighty-four `set.*` keys in all ten languages across
eight panels. The console-untranslated record falls **373 → 262**,
exact-sync held.

## [0.44.7] — 2026-08-05

### The bearing speaks the visitor's language

The Bearing screen — how JIM speaks, what it was told, what it made of
that, the guide, the dock in the corner and the suggestion box — is
localized end to end: fifty-three strings become forty-three `brg.*`
keys in all ten languages, including the refusal that names What's
Held as the place to consent a source. The console-untranslated record
falls **426 → 373**, exact-sync held.

## [0.44.6] — 2026-08-05

### What reaches out speaks the visitor's language

The Reach screen — the robot bound to the household with its honest
first-aid rating, the care code a stranger can scan, the accounts on
platforms JIM does not run, the excursion that leaves the host and
says what it cost, and the watch's drip token — is localized end to
end: fifty-five strings become forty-five `rch.*` keys in all ten
languages. The console-untranslated record falls **481 → 426**,
exact-sync held.

## [0.44.5] — 2026-08-05

### The baseline speaks the visitor's language

The Baseline screen — your own normal, the bands drawn around it in
either direction, and the crash watch you program yourself — is
localized end to end: fifty strings become twenty-six `bas.*` keys in
all ten languages, the crash-watch explanation and the what-this-is
paragraph kept whole in every language. The console-untranslated
record falls **531 → 481**, exact-sync held.

## [0.44.4] — 2026-08-05

### The attending speak the visitor's language

The Attending screen — the specialists JIM can hand a thing to, the
referrals, the escalation ladder with its floors and its one ceiling,
the relay, the sittings, the alarm and the Medical ID — is localized
end to end: forty-two strings become thirty-nine `att.*` keys in all
ten languages, the emergency-door rule kept as one whole paragraph.
The console-untranslated record falls **573 → 531**, exact-sync held.

## [0.44.3] — 2026-08-05

### The channel speaks the visitor's language

The Channel & camera screen — the microphone that listens and the
clinical camera that seals photographs of a body into the vault — is
localized end to end: thirty strings become twenty-nine `ch.*` keys in
all ten languages, whole sentences with named holes. The
console-untranslated record falls **603 → 573**, exact-sync held. The
field-label evidence pass walked the residue against every form and
found nothing newly typed — the hundred rows stay on the identifier
fallback with the evidence recorded.

## [0.44.2] — 2026-08-05

### Version alignment

The three products are cut together, so one number names one
combination of all three. No JIM-mini code changed — QRME's phones
gained the last doors: genesis and hybrids, packs, simulations,
the contribution ledger, proactive reach, licensing and the senses,
and the per-shell doorless records run to zero. JIM's guardian and shells are untouched.

## [0.44.1] — 2026-08-05

### Version alignment

The three products are cut together, so one number names one
combination of all three. No JIM-mini code changed — QRME's phones
gained the sticker, the queue and the stamp: beacons/QR and pairing,
moderation with message edit and retract, reviews, watermarks, media
and wearables, 24 routes with doors on iOS, Android and Windows. JIM's guardian and shells are untouched.

## [0.44.0] — 2026-08-05

### Version alignment

The three products are cut together, so one number names one
combination of all three. No JIM-mini code changed — QRME's phones
gained the keys, the till and the lifeline: accounts, money and
status+help, 24 routes with doors on iOS, Android and Windows. JIM's guardian and shells are untouched.

## [0.43.9] — 2026-08-05

### Version alignment

The three products are cut together, so one number names one
combination of all three. No JIM-mini code changed — QRME's phones
gained the face round: portrait, emblem and badge, page and themes,
front, surfaces, blend, bodies, dials and the wrist, 24 routes with
doors on iOS, Android and Windows. JIM's guardian and shells are untouched.

## [0.43.8] — 2026-08-05

### The watch you actually wear

The drip channel was never Apple-shaped — it is a URL that accepts
JSON — but the setup card only spoke iPhone, which meant a person with
a Pixel Watch or a Fitbit stood in front of instructions for a phone
they do not own. The card now asks what you wear and teaches that:
`?device=` picks between Apple Watch (the Shortcuts recipe), Wear OS
(Health Connect plus a phone automation), Fitbit and Garmin, the
device list ships in the payload so the picker renders from the API
and a new wearable family is one dict entry, and a wrong device is a
422 that names every right one. The seed now reads Fitbit's Takeout
export alongside Apple's export.xml — resting heart rate and HRV
summaries fold into the baselines; the continuous heart-rate stream is
deliberately skipped, because folding a workout into the resting
baseline is the exact mistake the Apple path's sedentary filter
exists to prevent (an injection that smuggled it in went red before it
shipped). Garmin's hint is honest that its export is not parseable
here yet rather than promising an upload that would be refused.

The devices card gained the radio: an Add-Bluetooth-device button
that, where the runtime carries Web Bluetooth, opens the chooser,
performs the GATT handshake, and registers the device under its own
advertised name with its transport and its paired state recorded — a
device the radio actually paired is a different fact from a name typed
into the manual row, and the card says which. The kind set now matches
what people actually pair: wearable, glasses (Google, Meta), AR/VR
headset, speaker, phone, stationary (2-D), spatial (3-D), autonomous,
other — and the picker's long-standing "phone" option, which the
server used to refuse, is accepted at last. Both cards speak all ten
languages; the console's untranslated backlog falls 615 → 603.

## [0.43.7] — 2026-08-05

### Version alignment

The three products are cut together, so one number names one
combination of all three. No JIM code changed — QRME's phones gained
the memory list, the pair's record, source material, the ledger,
anonymity, verification and the profile's three endings, striking 75
rows from its per-shell doorless records. JIM's guardian surfaces already reach its phones.

## [0.43.6] — 2026-08-05

### Version alignment

The three products are cut together, so one number names one
combination of all three. No JIM code changed — QRME's phones gained
workflows, delegation, the assistant, tasks under a grant, rated
placements and specialists, striking 84 rows from its per-shell
doorless records. JIM's guardian surfaces already reach its phones.

## [0.43.5] — 2026-08-05

### Version alignment

The three products are cut together, so one number names one
combination of all three. No JIM code changed — QRME's phones gained
signatures, mail settings, rooms, wall screens, memberships, handoffs
and campaigns, striking 74 rows from its per-shell doorless records.
JIM's guardian surfaces already reach its phones.

## [0.43.4] — 2026-08-04

### Version alignment

The three products are cut together, so one number names one
combination of all three. No JIM code changed — QRME's phones gained
the robot body's audit trail, the referral flow, objections, the game
lobby and the helper dock, striking 75 rows from its per-shell
doorless records. JIM's guardian surfaces already reach its phones.

## [0.43.3] — 2026-08-04

### Version alignment

The three products are cut together, so one number names one
combination of all three. No JIM code changed — QRME's phones gained
the place disclosures, the camera, organizations and the guided tour,
striking 81 rows from its per-shell doorless records. JIM's own disclosures already reach its phones.

## [0.43.2] — 2026-08-04

### Version alignment

The three products are cut together, so one number names one
combination of all three. No JIM code changed — QRME's phones gained
the audience verbs, the watch party and skill grants, striking 84 rows
from its per-shell doorless records. JIM's phones already carry their guardian's own surfaces.

## [0.43.1] — 2026-08-04

### Version alignment

The three products are cut together, so one number names one
combination of all three. No JIM code changed — QRME gained an inbox
that tells a person what was done to them; JIM's guardian already
speaks through its insight ladder, which is this product's own answer
to the same question.

## [0.43.0] — 2026-08-04

### Version alignment

The three products are cut together, so one number names one combination
of all three. QRME's phones learned to staff a desk, trade in the market
and sign an exchange, striking 139 rows from its per-shell doorless
records.

### The guard learns to read a Swift verb

QRME's round exposed a rule this repo shares: the iOS route audit read
only the `request(` helper, so a URL built with `appendingPathComponent`
and sent through a raw `URLRequest` was invisible to it. This shell has
exactly one such call — `revokeMedicalCard`, a working door since the
medical-ID round — and the audit had it listed as work to do.

    asked     does the shell call the transport helper for this route
    mattered  does the shell fetch this route at all

The rule arrives with its premise: the verb is read from `httpMethod`,
never assumed, because QRME's first draft assumed GET and its own suite
falsified that within the hour. `DELETE /medical-id/qr/{user_id}` comes
off the ios doorless record — a row that was never work at all.

## [0.42.9] — 2026-08-04

### Version alignment

The three products are cut together, so one number names one combination
of all three. No JIM code changed — QRME's friends list, wall and
comments gained doors on its iOS, Android and Windows shells, closing
twenty-seven rows of its per-shell doorless backlog.

## [0.42.8] — 2026-08-04

### The record said nobody asks; the forms had started asking

The same audit as QRME's, run against this product's record with the
same evidence rule: a field counts as *asked for* only when a console
input is literally bound to it. Fifty-four of the 154 recorded fields
were — the onboarding form's legal name and terms consent, the crash
watch's trusted contact, the steward channel, the watch bridge's
thresholds, the wellness planner. All 54 now carry hand-written labels
in all ten languages, matching QRME's table wherever the two products
share a field name, which the shared-vocabulary guard now checks in
both directions for 161 more rows. The 100 rows that remain are the
record's honest residue: enum members, context-filled ids, and flags.

### The Guardian gets its lights

QRME's always-on agent-lights widget never had a sibling here — a field
request closed the gap. `GuardianLights.tsx` pins a watch-face to the
console's bottom-left corner, built from routes the console already
opens (open alarms, the vigil, the crash watch), so a glance opens no
new door. Green is the Guardian watching; amber is it asking for you;
red is an open alarm or a tripped vigil. Minimizable to a dot, worded
from the console's own ten-language table, and — the lesson its sibling
paid for in the same cut — unreachable is a state it shows, not one it
hides in: a failed first fetch renders an unlit dot that retries on
press.

## [0.42.7] — 2026-08-04

### The circle is yours

QRME's people got messages, switches and a page of their own this round,
and the person behind a JIM had none of them — the Guardian knew
everything about them and offered no surface that was simply *theirs*.

    asked     can the Guardian's user reach the people around them
    mattered  on whose terms

`jim/circle.py`, four parts, one idea — the person decides. **The
circle**: JIM has no friendship graph, so the consent record is built
here and kept thin — an invitation is one direction, two directions make
contacts, and either side deleting theirs ends it for both. **Switches**:
per user, default on, refusing by naming the switch. **Messages**:
contacts only, one thread per pair, old words surviving the circle
ending while new ones need it back — and nothing ever leaves the
deployment; the module structurally imports no client that could carry a
message out. **The homepage sandbox**: identical walls to QRME's (hex
colors, http(s) links, plain text, actual contacts), but never public —
a signed-in neighbour is the widest audience it has, and only while the
homepage switch is on.

Eight routes with doors on all four clients — the Community screen's
Circle card and Circle panels on iOS, Android and Windows — every
visible string arriving from the view's own `labels` in the reader's
language.

## [0.42.6] — 2026-08-04

### Booked, reminded at the bottom rung, and emailed to yourself alone

The Guardian could watch sleep, money and medication, point at desks and
shops — and could not hold an appointment.

    asked     can the Guardian point at where help is
    mattered  can it hold the time you agreed to go

`jim/schedule.py` on three rules: **a booking is a row, not a hostage** —
one press books, one press cancels, and booking a shop *service* is one
act (the order rides through `jim/shopping.py` under all four of its
rules; cancelling the booking hands a still-`placed` order back).
**Reminders ride the proactive ladder at its bottom rung** — a `checkin`
guardian event plus an insight, once per appointment, raised by the
monitor/observe senses with no scheduler to deploy; however missed, a
haircut does not ring a phone. **Email goes to the user, or nowhere** —
the recipient is looked up from the verified account, never passed in,
so no request shape mails a third party.

Three routes with doors on all four clients in this cut — the Home
screen's Schedule card and Schedule panels on iOS, Android and Windows —
and the 0.42.5 promise is paid: the shopping routes gained their native
doors on all three shells too, their doorless rows struck.

## [0.42.5] — 2026-08-04

### Shopping through the tandem, on the buyer's terms

QRME grew shops; JIM grew the buyer's side, deliberately thin, on four
rules driven by `jim/tests/test_shopping_through_the_tandem.py`: browsing
is anonymous (an unreachable tandem is an empty shelf, never an error);
ordering is the *interactor's* act — signed with the same per-user token
the tandem chat runs on, one identity to revoke; the history is held HERE —
receipts live in JIM's own table, and a test proves the negative that no
request ever asks QRME for the buyer's order list; and the shelf carries
its own labels in the reader's language. Three routes with a console door
on the Community screen; the three shells record them honestly for the
queued booking-and-ordering native round.

## [0.42.4] — 2026-08-04

### The money guardian reaches the phones

0.42.2 built the guardian and its five routes; the round's own honesty
recorded all five as doorless on every native shell. That was the record
working as intended — and a money guardian a person can only reach from a
desktop is a guardian that misses them at the grocery store.

    asked     is the doorless record accurate
    mattered  does the phone in their pocket have the door

All five routes now have real doors on iOS, Android and Windows: a Money
panel in each shell's Life surface with account registration (number
fields to the vault or refused, the server's refusal shown verbatim),
balance observations with warnings and their doors, the savings goal, and
the mandate — written with scope and caps, revoked by a button that is
never gated. Every visible string is the overview's own `labels`,
composed server-side in the reader's language, so the English count
behind the tabs did not move. Each shell's doorless record shrinks by
five, and the shared error path now surfaces a 402's structured message.

## [0.42.3] — 2026-08-04

### The last thirteen unaudited screens

Six components had sat `unaudited` in `ui_screens.txt` since the manifest
was seeded. Reading each component's own heading against the gallery's
titles resolved four as merely unlabelled — `Meds` draws **85**, `PaceCue`
is the pace circle of **14**, `Onboarding`'s sign-in flow is **40** and
**42**, and `ProviderTiles` is the tile picker of **83**, not 20, which
draws the *human* providers — and confirmed two had never been drawn.

    asked     is every component accounted for in the manifest
    mattered  does every component have a drawing

**102 Safety** is the answering end of the crash watch — screen 88 showed
the watch asking and nothing showed a person accepting, clearing or
escalating the alarm. **103 Wellness** draws the three deterministic
generators (calm, workout, meals). Both ceilings now read zero and the
slack test keeps them there.

## [0.42.2] — 2026-08-04

### The Guardian watched spending and could not hold the money

### The finding

JIM already watched money the way it watches sleep: consented spending
events fill budget tallies, `life._budget_insights` warns at 80% and 100%
of a plan, `forecast_spending` projects the month, and the finance coach
hands a question to Marcus Bell through the tandem. But there was nowhere
to put an *account* — checking, savings, brokerage, crypto — so there was
no balance to watch, no cushion to warn about, no savings goal to coach
toward, and nothing to invest.

    asked     is spending watched
    mattered  is the money watched

### What shipped — `jim/money.py`, on four rules

  * **Credentials only ever live in the vault.** Account numbers, routing
    numbers and exchange API keys are sealed in the PDI tandem; JIM keeps
    only the institution, the kind, a label and the last four digits. On a
    plan with no vault the registration is refused — storing a routing
    number in the clear is not a degraded mode.
  * **Warnings ride the existing proactive ladder.** A low balance is a
    guardian event at `checkin` severity and an insight, in the user's own
    language, exactly like a drift band. Money never reaches the emergency
    escalation: an overdraft is not a collapse.
  * **The mandate is a handover, not a default.** "Let JIM invest for me"
    requires it written down — enabled, a per-order cap, a monthly cap,
    asset classes, and a scope in words. Enabling is Pro-gated; revoking is
    never gated, because taking your hands back must not have a price.
    Every order JIM proposes is logged, and the record says `proposed`:
    nothing executes without a brokerage connector, and no execution is
    pretended.
  * **A warning carries its doors.** The finance coach, the tandem
    specialist, and real people at desks — near the user's locality or
    across the map — ride on the warning that makes them relevant.

Five routes; the console's Money card renders entirely server-provided
labels in the reader's ten languages, so the console's English ratchet
gained nothing. The phones record the routes on their doorless backlogs.

`docs/proactive.md` now names every proactive path in one place — senses,
interpreters, actions in escalation order, and the three lines that keep
proactive from meaning creepy.

### Checks

`jim/tests/test_the_money_guardian.py`, 17 tests. Driven three ways:
removing the vault refusal stores a routing number in the clear and the
test says so; raising money past `checkin` severity fails the hard line;
ignoring the monthly cap proposes 2000 against a 1000 mandate.

## [0.42.1] — 2026-08-04

### Version alignment

The three products are cut together, so one number names one combination of
all three. No JIM-mini code changed in this round: QRME's 34 starters — the
specialists JIM's coach and guardian hand off to through the tandem — each
gained a dossier of expertise, services, skill chips and a real colleague
graph, so a specialist reached from JIM can answer for its own trade.

## [0.42.0] — 2026-08-04

### The device's confession was stripped at the door

### The finding

`jim/signal.py` grades every biometric sample and folds in the one piece of
evidence better than any range check — the device's own report of how well
it read. The fold is multiplicative on purpose: a wearable saying "poor
contact" can only ever lower trust.

None of that could happen. `BiometricSample` did not declare
`signal_quality`, so pydantic silently dropped the field at
`POST /monitor/{id}` and the grader received every sample with the
confession removed. An SpO2 of 62 read through a flapping strap graded `ok`
at confidence 1.0 — full trust in exactly the reading the device itself had
disowned. Found by driving, not reading: the module was correct, its unit
tests passed, and the door undid it.

    asked     is the sample graded
    mattered  can the device's own confession reach the grader

`signal_quality` is now declared (bounded 0..1 at the door, so a device
reporting 7 is an input error rather than a silent clamp), and
`jim/tests/test_the_device_confession_reaches_the_grader.py` drives the
defect's exact shape: poor contact caps confidence, a confident device
changes nothing, and no confession can make a heart rate of zero true.

### Also

The Settings contribution card said what would be shared; it now *shows* it
— `preview_next`, the exact payload, rendered verbatim from the same
function that sends. Nothing queued is said in words rather than shown as an
empty box.

## [0.41.0] — 2026-08-02

### The workflow round-trips and nothing walked the whole arc

### The finding

JIM's four specialist-task routes — start, list, read, advance — hand a
multi-phase goal to a QRME synthetic profile and keep the status of it without
ever holding the working drafts. Each had unit coverage against a stubbed
tandem. What nothing did was walk the arc against a *real* QRME: the
cross-product smoke check seeded all three products, wired the tandems, drove a
single exchange and proved its custody through the vault, then stopped.
`start_workflow`, `advance` and `specialist_tasks` were never called across the
boundary at all.

    asked     does the workflow round-trip
    mattered  does anything walk the whole arc

### What driving it found

Two behaviours nothing had met end to end, both of them JIM's:

  * **Delegated work is Pro-gated** (`synthetic_agents`). The first
    `POST /users/{id}/specialist-tasks` came back `402` naming the tier. The
    exchange the smoke check already drove needs only the vault, which Basic
    has — so the run had never touched that gate.
  * **`handoff.available` reads "no" from a specialist whose owner has not
    opted in**, and the refusal now has to happen before the opt-in for the run
    to continue. A stranger cannot put a synthetic profile to work uninvited,
    and that is now proven by asking rather than asserted in a docstring.

The arc walks `research → draft → send` and stops at `confirm` with `awaiting`
naming what it waits for. `handoff._shape` returns the phases done and the
profile that did them; the drafts stay in QRME, which is the whole point of
keeping status only.

### This release

Version alignment: the three products are cut together, so one number names one
combination of all three. The arc itself lives in QRME's `suite/smoke.py`; what
changed here is that JIM's delegation surface is now driven by it end to end
rather than only against a stub.

## [0.40.9] — 2026-08-02

### The README said v0.18.0

### The finding

The first bold line of every README in all three products read:

    **Current release: v0.18.0**

and the line directly beneath it said the three are *"versioned and cut
together, so one number names one combination of all three"* — a convention the
banner had stopped following at 0.18.0 and kept advertising for twenty-two
releases.

The release-history table underneath stopped at **0.30.6**. Seventeen shipped
releases — 0.25.0 through 0.29.0, 0.30.7 to 0.30.9, and the whole 0.40.x line —
were in `CHANGELOG.md` and absent from the page anybody actually reads. The
changelog was right the entire time; the summary of it in front of the door was
behind.

    asked     is the release written down
    mattered  does the front page say what shipped

Reported from the README beside the video, which is the one place this was
always going to be noticed and the one place no test was looking.

### Changed

- The banner names `pyproject.toml`'s version; the table carries every release
  from 0.25.0 on, backfilled from each product's own changelog.
- `test_the_readme_says_what_shipped.py` — five tests, the same file in all
  three: the banner matches the version, every release has a row, the newest
  row is this release, no row names a release that was never cut, and a guard
  on the scan itself.

Two injections, both reproducing the reported defect exactly: the banner set
back to v0.18.0, and the table truncated at 0.30.6 again.


## [0.40.8] — 2026-08-02

### The refusal named the field the API calls it

### The finding

An earlier round took the 422 from `[{"type":"missing",...}]` to one sentence a
person can read, in their own language. It stopped one step short, and said so
in its own docstring:

> Mapping those names to the labels a form actually shows — *"Nome de
> exibição"* rather than `display_name` — is a per-client table this does not
> have, and is recorded as the remaining gap rather than guessed at.

So a person mistyping the sign-up form was told **`display_name — Field
required`** while the form beside it said **Profile name**, and had said it in
ten languages since the console was localized.

    asked     is the refusal a sentence in the reader's language
    mattered  does it name the field the reader can see

### Where the table lives

Server-side, beside the sentence, for the reason the sentence is composed there
at all: nine clients rendering it is nine chances to render it differently, and
six of those are in languages with no test runner in this repository.

Wording is ported — from the console's own labels in QRME (`onb.profile.name`,
`onb.persona`, `onb.email`, `onb.password`), and from QRME's table into the two
siblings for every row they share. One vocabulary across three products is one
thing to keep right; three is three.

There is no mechanical mapping for the rest: the console's rows are keyed by
screen, not by field, and a name-match across them returns `title` → *"A
profile depicts me"*, which is a heading. Guessing is what the docstring above
declined to do, and this table does not.

### The identifier stays the fallback

A field with no row keeps its API name. That is a decision, not a gap: an
identifier a reader can match to the form in front of them beats a word
invented for them — the same reasoning that keeps `QRME_ADMIN_TOKEN` in English
in `refusals_untranslated.txt`. The unmapped fields are recorded, and the
record only shrinks.

### Changed

- `_FIELD_LABELS` — 19 fields × ten languages — and `field_label()`;
  `validation_message` renders the label where there is one. Every row shared
  with QRME carries QRME's wording byte for byte, and a check fails if the two
  drift.
- `field_labels_unmapped.txt` records the other 158, with a status line.
- `test_the_refusal_names_the_field_on_the_form.py`, shared with the sibling
  products.

The cross-product drift check skipped every run in its first draft: it looked
for QRME at `REPO.parent`, and these repositories sit under different roots. A
check that never runs is not a check.

## [0.40.7] — 2026-08-02

### The record that outlived the code

### The finding

`public_untranslated.txt` opened with a paragraph explaining that
`Onboarding.tsx` — the screen every person in the world meets first — carried
forty-odd English strings, that translating them was "its own round", and that
a half-translated sign-up form would be worse than an English one. All of that
was true when it was written.

`The screen everybody meets first` translated them. `The pre-session backlog
reaches its floor` took the count to four and appended its correction *below*
the stale paragraph, which nobody struck:

    What is left is not prose. A product name, a punctuation mark, an
    example address and an example code — strings that are the same in
    every language. This is the floor, not a backlog.

So the file held two statements about itself with the false one first. Read
top-down — which is how anybody reads a file — it advertised a cleared backlog,
and the correction was twenty lines further on. This round was planned off that
paragraph before the extractor was run and the work turned out to be two
releases old.

    asked     is the record complete
    mattered  does the record still describe the code

The numbers were right the whole time. The prose around them had outlived the
thing it described, and a record only works if a reader can trust the first
thing it says.

### Every ratchet now leads with what it is

`# status: floor|backlog — N rows`, on the first line, with the count checked
against the rows beneath it. `floor` means the remainder is permanent and is
not work; `backlog` means somebody still owes it. The two cannot be told apart
from the numbers — `console_untranslated` sits exactly at its ceiling with
1,459 strings still to translate, and `public_untranslated` sits exactly at its
ceiling and is finished — which is why the file has to say which it is, in a
line that cannot drift from its own contents.

A third check was written and struck before it shipped: *a file calling itself
a floor must sit exactly at its ceiling*. It fired on `native_untranslated.txt`,
which the last release took from three rows to none — a floor of zero under a
ceiling of three, and the best kind there is. `floor` is a claim about what the
remaining rows **are**, not how many, and a check that pretended otherwise
would have been one more guard answering the question next to the one that
matters.

### The reasons move next to the rows

`unused_native_bindings.txt` recorded two bindings whose justification lived in
the guard's module docstring — true, careful, and one file away from the list
it explained. A record whose justification is somewhere else reads, at the
place somebody actually looks, as an unexplained backlog: the shape this audit
found seven times in `0.40.5`. Every row now carries its reason on the row, and
a new check refuses one that does not.

### The dead-key ratchet was reading one shell's share of a total

`native_dead_keys.txt` held four generic action verbs — `action.refresh`,
`.save`, `.send`, `.translate` — added in advance because a screen would
obviously need a Save button, translated into ten languages, and asked for by
no screen in any shell across several releases. Ten rows across three shells.

Its ratchet took the **maximum over the shells**, so the number of dead rows
could have risen — iOS three to four, a fourth shell arriving with four of its
own — while the check passed every time, because no single shell crossed the
line. The file's own instruction said "the ceiling does not move up" and meant
the count of dead rows.

    asked     is any one shell's dead-key count above the line
    mattered  is the number of dead rows going up

### Changed

- The four verbs are deleted from all three shells; the record is at **0**. The
  file's own instruction was "wire one or delete one". A screen that needs a
  Save button adds the row it needs, in the wording it needs.
- `# total:` ratchets the sum alongside the per-shell `# ceiling:`.
- `test_a_record_that_outlived_the_code.py` and the binding-reason check, both
  shared with the sibling products.

Injections: one dead verb put back and recorded — which the old maximum-only
ratchet passed at 1 ≤ 4 — plus the three record checks.

## [0.40.6] — 2026-08-02

### Cut alongside qrme and pdi

No change in this product. The round finishes localizing QRME's **accountless
screen** — the one built for somebody who has found a synthetic profile of
themselves and has no account, and therefore no profile language to take a
setting from.

This product has no such screen. A Guardian belongs to the living person using it — every surface here is reached by somebody who has an account, and there is no third party for it to speak as.

The shells here already resolve a device language and already send it as
`accept-language`; what they do not have is a screen whose reader provably has
no profile. Recorded rather than left silent: a version where all three move
together and one is untouched should say which one and why.

## [0.40.5] — 2026-08-02

### The account was gone and the wrist kept writing

`life.delete_user_data` opens with *"Erase every trace of a user across all
tables — and the PDI vault."* It empties the vault, walks eighteen tables and
removes the `users` row last, and the API answers 404 for that id afterwards.

`watch_channels` was not one of the eighteen. Its `token` is the drip address:
a URL typed into an Apple Shortcut, sometimes weeks before, that deposits
readings into one user's stream. Driven end to end:

    DELETE /data/{id}            200  {"events": 1, "baselines": 2, ...}
    GET    /users/{id}           404  the account is gone
    POST   /watch/drip/{token}   200  {"received": 1}  ← and an event row is back

    asked     did we delete the user's data
    mattered  can anything still write more

The reading ran the full Guardian pipeline under an id that no longer resolves,
so an erased account grew rows again from a credential its owner had no way to
find and no screen left to rotate. Two other tables in the same shape went with
it: `contribution_log`, whose `revoked` column is the whole mechanism for
withdrawing what was shared with the cloud, and `waivers`. Both are standing
permissions rather than records of something that happened.

The sibling products had the same class in their own idiom, and the same round
landed in all three: in QRME a terminated profile was still being licensed and
cloned through the buyer's token, and in PDI a closed vault was still readable
through a bequest grant.

### Changed

- `life.delete_user_data` now takes `watch_channels`, `contribution_log` and
  `waivers` with it.
- `watch._user_for_token` joins `users`, so a channel row that somehow survives
  still cannot deposit — the second stop, which closes the class rather than
  the one path.
- `jim/tests/test_the_erase_left_a_live_address.py` — eight tests. The
  generalisation reads the schema rather than a list in the file, so a
  credential table added next release is in scope by construction.

Thirty user-scoped tables hold ordinary data and are also untouched by a
function whose first line says "every trace". That is recorded in the new test
file rather than hidden; it is a decision about what deletion means rather than
a defect with a receipt, and this round does not take it.

## [0.40.4] — 2026-08-02

### Cut alongside qrme and pdi

No change in this product. The round is about a synthetic profile of a person
who has died, or whose subject is contesting that it should exist — states
QRME has and this product does not: a Guardian belongs to the living person
using it, and there is no third party for it to speak as.

Recorded rather than left silent, on the same reasoning as the last release: a
version where all three move together and one is untouched should say which
one and why.

## [0.40.3] — 2026-08-02

### One wrapper recorded its degrades; its sibling said nothing

`llm.FallbackProvider` is where this rule is written down in this codebase, and
it is exemplary:

> The degrade is recorded on the instance (`answered_by`, `failure`) so a
> caller can tell the user the truth about who actually answered — **a log line
> the user will never read is not disclosure.**

`cloud.CloudProvider` degrades to the same local stub and did none of it: a
bare `except Exception:`, no record, and — unlike its sibling — not even a log
line. And `generate_for_user` asked for the truth by naming one class:

```python
if isinstance(provider, FallbackProvider):
    actual, reason = provider.answered_by, provider.failure
```

So when the cloud gateway was unreachable, `actual` stayed at the model the
user had chosen and `degraded` computed to False. The coach's own comment
beside that field says what that costs:

> a silent degrade to the stub under a screen that says Claude is how a founder
> demos canned text to their testers without knowing it

    asked     did the fallback provider degrade
    mattered  did anything degrade

The careful half made the silent half invisible, and nothing exercised the
cloud path through `generate_for_user` at all.

### What changed

`CloudProvider` now carries `answered_by`/`failure` in the same idiom as its
sibling, and the assembly **duck-types on those attributes** instead of naming
one class — so a third wrapper is covered by construction rather than by
somebody remembering to add a branch. A structural check enforces it.

### A test that passed for the wrong reason

The driven half of the new guard first asserted the right values while the
defect was still in place. The suite pins `JIM_LLM=stub`, so `intended` was
already `"stub"` and the broken branch — which reports `intended` — produced
exactly the answer the fixed branch produces. It now pins the intended provider
to something that is *not* the stub, which is the whole of its discriminating
power. Re-injected afterwards to prove it fails.

## [0.40.2] — 2026-08-02

### The refusals, finished

0.24.0 translated the eleven refusals any route can raise and **wrote the rest
down**. 42 sentences sat in `jim/tests/refusals_untranslated.txt` from that day to this — the sentences
the Guardian says when it says no, still English on an account that had chosen
otherwise.

Among them the sentences a guardian meets around a minor's care — the waiver
that can never be signed for a child, the consent a provider does not have.


    asked     is the refusal translated
    mattered  is every refusal translated

All 42 are now in `_REFUSALS`, in the nine languages beside English. The
record is a decision rather than a backlog for the first time: it is empty.

### What deliberately stays an identifier

Field names, header names, enum values and environment variables are not
translated and are not meant to read as words — `audio_base64, qrme_profile_id, x-signup-key, JIM_QRME_URL`. They are the API's own
names, the same string in every language, and declining them into a sentence is
the half-in-one-language failure the table exists to refuse.

### The check that could not have caught a lie

`test_every_translated_refusal_has_every_language` asks whether each row has
all nine keys. A row whose nine values are the English sentence pasted nine
times satisfies it exactly — and the table would then claim the refusal is
handled while every reader still got English.

    asked     does every refusal have every language
    mattered  does every language say something other than the English

That gap was harmless while eleven rows were added by hand and reviewed one at
a time. It stops being harmless the moment 42 are added in one release, so
`test_no_refusal_is_translated_into_english` was added first and injected
against: an English value in one slot of one row fails it by name.

## [0.40.1] — 2026-08-02

### The language no client was sending

JIM's public surface answers people who have no account yet, and those handlers
compose real sentences: what was sent, what is held, what to do next. Every one
of them is chosen from `Accept-Language`.

**No native shell was sending that header.** The browser sends it without being
asked, which is why the console looked correct and the three clients a person
is actually holding were the ones answering in English.

    asked     can the shell say it in the reader's language
    mattered  does the reader's language ever reach the server

Two things were missing, and only the second is obvious once the first is
written down. There was **no language to send**: each shell's `language` comes
from the stored account setting and is `"en"` until an account exists.
`L10n.deviceLanguage` (iOS), `L10n.deviceLanguage()` (Android) and
`L10n.DeviceLanguage()` (Windows) now read what the device has been carrying
all along — `Locale.preferredLanguages`, the system configuration's locale
list, `CurrentUICulture` — drop the region, and fall back to English rather
than guessing. Then there was **somewhere to send it**: one line in each
shell's shared request helper.

`test_the_language_nobody_was_sending.py` checks both halves, because a header
set to a constant is indistinguishable from a correct one from the outside, and
it checks *every* header line rather than any of them — the sibling product's
client sets the header in two places and an `any` passed an injection that
broke one.

### Windows' localizer takes a language now

`L10n.T(key)` read `AppState.Current.Language` and had no way to be told
otherwise, so a public surface got the account's default without the screen
ever naming it. iOS and Android could not make that mistake: both of their `t`
functions require the language as an argument. A `T(key, lang)` overload closes
the gap.

## [0.40.0] — 2026-08-02

> Staged as 0.30.10 and cut as **0.40.0**. The work below is unchanged; only
> the number moved, from a patch on the 0.30 line to a minor of its own.

### A specialist could be reached by a sensor and not by a person

`grep -c specialist jim/coach.py` returned **0**.

A QRME specialist was reachable from exactly one place in this product:
`guardian._deliver`, the monitoring path. Sensors trip, a detection names a
condition, and if a tandem specialist is registered for it the Guardian
delegates the guidance.

`coach.reply` — where somebody brings something in their own words, because
they chose to — had no call, no mention and no comment about specialists at
all.

    asked     can a specialist be reached
    mattered  can the person who asks reach one

The person whose watch noticed something got the better answer. The person who
sat down and typed *"I've been struggling with money and it's keeping me up"*
got the local model — on a product whose premise is that somebody is looking
after you, and where bringing a problem yourself is the strongest signal there
is.

**Nothing bridged them because two vocabularies never met.** `specialists` is
keyed on **condition**, because its only caller was a detection. `coach.AREAS`
is seven **life areas**, because its only caller was a person choosing a tab.
`jim/specialists.py` is that map — declared, not matched: a substring rule
would have paired *finance* with *financial stress* and left *nutrition*
silently unpaired while looking like it had worked. An area with no clinical
domain holds an empty tuple, which is a decision rather than an omission, and
a guard refuses a new area nobody has decided about.

### It offers; it does not route

The material is different in kind from what the monitoring path sends. A
detection sends a **finding** — *"the user shows signs of low mood (resting
heart rate elevated for 40 minutes)"*. A coach turn would send **what the
person wrote about their own life**.

Routing that automatically would disclose to a profile outside JIM something
somebody said to their Guardian, without ever asking them. So `coach.reply`
returns an offer that says plainly *nothing has been sent*, and the sending
lives behind `POST /coach/{id}/specialist` — a door the person chooses.
`handoff.py` set the same rule for the other multi-step path: *a detection can
warrant a handoff; a person or an operator starts it*.

Never reachable from escalation, and there is a test that fails if it ever is:
a ladder that waits on a third party is worse than no ladder.

The answer says where it came from — *"answered by a QRME specialist profile
through the tandem, not by JIM's own model"* — and what crossed: *"the message
you sent, and nothing else from your record — no check-ins, no conditions, no
medication"*. Both are checked by name. A reply that reads as the Guardian's
own when a third party wrote it is the one thing this path must never do.

Doors in the console and on all three shells.

### A field name that would have broken every phone

The offer ships as `specialist_offer`, not `specialist`. The monitoring path's
reply already uses `specialist` for the expert's **name**, a string, and all
three shells decode `Guidance` with `specialist: String?`. An object under that
key would have thrown at decode time on iOS, Android and Windows — and there is
no Swift, Kotlin or C# toolchain in this build environment to have said so.

### Two records were overstating themselves

`console_untranslated.txt` counted **62** rows that were separators rather than
English: a bare `:`, a `·`, a `%`, a `⚠`. The guard then fired on a card whose
every sentence had just been localized.

    asked     did the extractor find a string here
    mattered  did it find a word a reader reads

The same mistake the shells' guard made last release with `"\(dim): \(n)%"`,
one file over. The ceiling is corrected to 615.

The new specialist cards **are** prose, so the native ratchet fired on them
correctly and they are hand-translated into ten languages on all three shells
and the console — the rule this repo keeps rather than adding to a backlog it
just finished measuring.

## [0.30.9] — 2026-08-02

### The user-specific model was correct, tested, and never computed

`jim/adaptation.py` implements clause 11 — a profile derived offline from a
person's own stored history, versioned, confidence-scored, sealed into the
vault when a tandem is configured. `coach.reply` reads it on every turn through
`adaptation.prompt_lines`.

`prompt_lines` returns `[]` when there is no row. `rebuild` writes the row. And
`rebuild` had exactly one caller in the entire product: `POST
/adaptation/{user}` — a button in the desktop console.

    asked     can a user-specific model be built from the history
    mattered  does anything ever build it

Nothing called it after a check-in, a coach turn, or an answered follow-up. On
every user who never pressed that button — which is every user who only ever
opened the phone app — the artifact had never been computed, and the coach ran
unadapted forever while the code that would have adapted it sat there correct
and tested.

The module was not wrong and neither were its tests. What was missing was an
**edge**, which is exactly the thing no test of either end will notice:
`adaptation`'s tests build the profile themselves, and `coach`'s tests pass
whether the profile exists or not, because a coach with no adaptation lines is
a working coach.

`adaptation.ensure_fresh` now rebuilds from the loop when the history has moved
on — three COUNTs on the common path, a rebuild only after five new pieces of
evidence, and it never raises, because a failure to refresh a *derived*
artifact must not cost somebody the answer they asked for.

### The latent continuity vector

Even with a rebuild, the profile is a snapshot and nothing moved between
snapshots. The sibling product carries a per-(profile, interactor) latent
vector, EMA-updated after every interaction, so cross-session state survives
logins, devices and model calls. JIM had no equivalent at all — a person could
check in every day for a month and be met each time exactly as on the first
day.

`jim/continuity.py` is that vector: six named dimensions — engagement, candor,
strain, receptiveness, steadiness, continuity — folded in at the three moments
a signal actually arrives, and rendered into the coach's prompt as **attention
weighting** rather than as instruction. Identity, boundaries and every safety
path stay fixed, and the rendered block says so.

Three rules it keeps, each with a test:

* **It carries no content.** Six floats and three counters, derived from
  tallies. Not a phrase, not a condition name, not a message. This matters
  more here than in the sibling product because what is being counted is
  somebody's health.
* **Confidence is earned.** Silent below six observations — a vector built
  from two check-ins is a shape in noise, and a Guardian that starts pacing
  itself around one is worse than one that has not started.
* **It is not a weight file**, and `state()` says so in its own words rather
  than letting a reader assume a fine-tune happened.

It is readable and droppable from the console and from all three shells:
`GET`/`DELETE /continuity/{user}`, a Settings panel, and a card on the
self-profile screen of iOS, Android and Windows.

### Two bugs the round's own guards found

**A type-compatible argument swap in the Android client.** The shared helper is
declared `request(path, method, body, token)`. Three calls in this shell and
one in PDI's passed `("GET", "/offline/status", …)` — verb first. Both
arguments are `String`, nothing complained, and the request went to
`base + "GET"` with the method set to a path. Two of those shipped in 0.30.7's
offline round.

    asked     does the call have the right number of arguments
    mattered  does it have them in the right order

There is no Kotlin toolchain in this build environment, which is why it sat
there. `test_a_screen_nothing_opens.py` now reads the helper's own signature
and refuses an HTTP verb in the path slot, in all three repos.

**Last release's untranslated counts were overstated.** The extractor counted
any string literal containing a letter, which counted format fragments like
`"\(dim): \(n)%"` — whose only letters are variable names nobody reads — as
English prose. About seventy-five of them across the nine shells.

    asked     does this literal contain letters
    mattered  does this literal contain words a reader reads

The ratchet caught it by firing on a card that had just been fully localized,
which is a measurement saying the opposite of the truth. The corrected figures
are in `native_screens_untranslated.txt`; JIM's shells are at 167 / 139 / 192,
and the localized share is higher than 0.30.8 claimed.

## [0.30.8] — 2026-08-02

### The tab bar answers in your language. Everything behind it does not.

The QRME repo has carried a guard since the console rounds called
`test_the_nav_is_translated_and_nothing_behind_it_is.py`. It found forty-six
translated sidebar labels in front of 1577 English screens, and said plainly
why that is worse than shipping no translations at all:

> A uniformly English console tells a Spanish reader the truth on the first
> screen they see. This one puts *Mercado*, *Amigos* and *Ajustes* in the
> sidebar — the app apparently answering in their language — and then hands
> them English the moment they click.

Three products ship three native shells each. All nine have a translated tab
bar. Nobody had ever counted what is behind them.

| product | iOS | Android | Windows |
|---|---|---|---|
| QRME | 2.4% | 3.8% | 0.6% |
| JIM-mini | 13.0% | 14.2% | 9.7% |
| PDI | 8.9% | 10.2% | 3.5% |

    asked     is the console's nav-vs-behind gap measured
    mattered  is the phones' too

`native_screens_untranslated.txt` now records it per shell, ratcheted in both
directions — the count may not rise, and the record may not sit more than
twenty above the real number, so the ceiling cannot quietly become a place to
drift back up into.

### The alarm surface is now hand-translated on all three shells

1813 strings cannot be honestly translated in one round, and this product's own
rule forbids the other kind — `jim/i18n.py`: safety text is *"never
machine-mangled"*. So this release takes the subset where English is a hazard
rather than a discourtesy, and records the rest.

Fourteen strings, ten languages, iOS and Android and Windows:

* the question the crash watch asks — **"JIM is asking: are you okay?"** — and
  its answer, on a screen whose entire premise is that silence sends help;
* the three answers to an open alarm: *I have this — I'm going*, *Nobody can go
  — escalate*, *It's over — clear it*. One of them decides whether the ladder
  keeps climbing toward emergency services;
* **"This is not an emergency service. If it is one, call your local emergency
  number — this screen cannot."**

A Spanish speaker was shown *Seguridad* on the tab, and then asked in English
whether they were alright, with three English buttons deciding what happened
next. The backend has refused in nine languages for several releases and
promises in all of them that emergency paths are never affected.

    asked     is the chrome localized
    mattered  is the decision localized

All three shells or none, for the reason `native_untranslated.txt` already
gave: porting one puts the responder on a localized iPhone and an English
Android, which is the per-client mistake this audit is named for, made on
purpose.

### Two guards on the guard, one of which caught a real miss

Every translated row is now checked for its **slots**. A row whose English says
`{name} was contacted` and whose Portuguese forgot the hole renders an alarm
with the person's name missing from the middle of it — the string is present,
the language is right, and the sentence is wrong. Where a shell's table holds
no slotted row the check **skips loudly** rather than passing on an empty set.

The first version of the row parser could not read four of the fourteen new
rows, and reported them missing from tables they were sitting in. Its Kotlin
pattern ended a row at the first `)` and its C# pattern at the first `}` —
and the rows that carry brackets are `({concern})` and `(relayed as a request
— …)`, which is to say the rows carrying slots, which is to say exactly the
rows the slot check exists for.

    asked     does the row match a pattern for a row
    mattered  does the row end where the pattern says it does

## [0.30.7] — 2026-08-02

### The screen nothing opens

Last release put the synthetic-self screen on the phones — the one QRME profile
that *is* this person, where they say what the Guardian may pass on about their
medication. One screen per shell, each translated into ten languages, and a
guard written to prove the wording was there.

The wording was there. Nothing else was. `SelfProfileSection` on iOS,
`SelfProfileScreen` on Android and `SelfProfilePage` on Windows were each
declared and each unreachable — no tab, no composable call, no navigation case.

    asked     does the screen have its wording
    mattered  does anything open the screen

All three are now in the navigation: a **Me** tab beside Community on iOS and
Android, and a **Me** entry in the Windows nav pane.

### Two of those three would not have compiled

`L10n.t` takes a key **and a language** in Swift and Kotlin. Every one of the
forty calls on those two screens passed only the key. The Windows shell's
`L10n.T` takes the key alone and reads the language itself, which is the only
reason that one was fine — three shells, two spellings of the same function,
and a screen written against the wrong one twice. There is no Swift or Kotlin
toolchain in this build environment, which is exactly why it sat there.

`test_a_screen_nothing_opens.py` now asks both questions per shell, and asks
the arity question against **each shell's own signature** rather than a single
number for all three. Holding Windows to Swift's two parameters would have been
the union mistake again, in the guard meant to catch it.

### Offline mode became readable

`GET /offline/status` reports the posture — whether external transmission is
possible, what counts as a local destination, what the deployment guarantees.
It was already answerable and nowhere visible. It now has a panel in the
console's Settings, a card on the Vault Custody screen of all three shells, and
its three chrome strings in ten languages.

Read-only on purpose. The posture is set in the deployment's environment, not
by somebody signed into the app, and a switch there would imply otherwise.

## [0.30.6] — 2026-08-01

### The plan gate speaks the reader's language

`refusals_untranslated.txt` carried this as an exception for four releases, in
its own words: a template whose slots were English prose, where translating the
frame alone would produce *"a sentence half in each language, at the one moment
in this product that stands between somebody and a decision to pay"*.

    asked     can the frame be translated
    mattered  can the slots be

They can. The capability descriptions and the billing period are a **closed set
this product authors**, so they are `i18n.Term`s with translations rather than
strangers — and `Term` is now exempt from the whitespace rule for exactly that
reason. The rule catches prose *nobody wrote a translation for*; an unmapped
`Term` still keeps the whole sentence English, so the exemption is paid for
rather than a hole.

The **plan titles** stay as they are. `Basic` and `Pro` are what the product is
called on the pricing page, in the console's tabs and on a receipt, and
somebody comparing a refusal against a price list needs the same word in both
places.

`Opening` capitalises **after** translation, never before: the vocabulary holds
one form of each phrase and each language raises its own first letter from it.
`str.capitalize()` was wrong here — it lower-cases the rest, which would have
flattened German's nouns.

**The emergency clause is part of the frame**, not appended to it. A person
told they cannot have the trend model needs to know the alarm still works, and
that reassurance arriving in English at the end of a Portuguese sentence is the
shape this mechanism exists to prevent. A test asserts it survives into all
nine languages.

## [0.30.5] — 2026-08-01

### The plan gate said HTTP 402

0.30.4 left the plan gate open as the one refusal deliberately not translated,
because its message interpolates prose. Going back to translate it turned up
something else first: on three of the four client families it was not arriving
at all.

`detail` has three shapes in this product — a **string** for most refusals, a
**dict** for the plan gate, a **list** for a 422. 0.30.3 gave the list a
top-level `message` and taught every client to read it. The plan gate's
`message` stayed nested inside its dict.

    asked     does the sentence ride beside the structure
    mattered  does every structured refusal put it in the same place

The three native shells look for a top-level `message`, then for a string
`detail`. A dict is neither, so the one refusal in this product that stands
between somebody and a decision to pay rendered as the bare status code: no
price, no plan name, no reason.

| Client | Before | After |
|---|---|---|
| iOS | `HTTP 402` | the sentence, with price and plan |
| Android | `HTTP 402` | the sentence, with price and plan |
| Windows | `HTTP 402` | the sentence, with price and plan |
| Console | correct | unchanged |

**One of those was a regression from 0.30.3.** Android had been coercing the
dict through `toString()` and showing its raw JSON — ugly, but it contained the
price. Teaching it to read the top-level key first is what dropped it to the
status code. iOS and Windows had always been broken.

**The fix is not a third special case.** Every refusal now carries a top-level
`message` holding the sentence a person reads, whichever shape `detail` is, so
a client never has to know the shape and a structured refusal added later
cannot repeat this. `detail` is untouched: the console still reads the dict to
draw the upgrade card with its price and button. `sentence_of` returns nothing
when there is nothing readable rather than inventing a sentence — a bare status
is more honest than one this codebase made up, and would be indistinguishable
from a real one.

**A second defect underneath it.** `localize_detail` looked one level down, and
`api.py` wraps every `HTTPException` as `{"detail": exc.detail}` before it
runs — so a structured refusal arrives two levels down and its sentence went
out **untranslated in every language**.

    asked     is a structured refusal localized
    mattered  is it localized where the wrapper actually puts it

Found because the new translation check failed rather than passed, which is
what it was written to do.

## [0.30.4] — 2026-08-01

### A refusal whose English is not a constant

`refusals_untranslated.txt` has carried the same paragraph for three releases:
f-string refusals, named as uncovered and deliberately not counted in the
backlog, because

    f"language must be one of {', '.join(SUPPORTED)}"

cannot be looked up by its English source — at the moment it is raised there is
no English source, only a result.

    asked     is the refusal a constant we can translate
    mattered  is every part of it something we can translate

`i18n.Templated` is a `str` whose value is the finished English sentence,
carrying the template and its slots so `localize_detail` can refill the frame
in the reader's language. Nothing that already treats a detail as text changed
— the default English path, JSON encoding, and every driven test asserting on a
refusal message all work exactly as before.

**The slot is the whole design.** A translated frame around an English slot is
*worse* than an English sentence: it reads as a bug, in front of somebody who
is already being told no. That is precisely why this record refuses to ship a
translated plan gate, and doing it here by accident would have been the same
mistake with a mechanism to spread it. So whitespace means prose, and a slot
that fails the test keeps the whole refusal English — the state it was already
in, now chosen rather than stumbled into.

The known limit is stated rather than hidden: a **single** English word has no
whitespace either, and is indistinguishable from an identifier.

JIM-mini has no refusal that interpolates a closed set, so it carries the
mechanism without QRME's `Term` marker and vocabulary, and the guard fails if
that stops being true. **7 sites converted**, 18 remaining.

The extraction read this product's own test file as a raise site, because tests
live inside the package here and beside it in QRME — caught by the literal-slot
check firing on its own examples.

## [0.30.3] — 2026-08-01

### The refusal that arrived as a list

0.30.1 put the 422 into the reader's language — the refusal a mistyped form
produces, and the one a person meets most often. Nothing looked at what a
client does with the result.

`detail` on a 422 is a *list* of pydantic rows, and every client family
rendered it by a path written for a string. The console called
`JSON.stringify` on it, so the note under a form read
`[{"type":"missing","loc":["body","display_name"],"msg":"Field required"}]`.
Android's `JSONObject.optString` coerces a `JSONArray` through `toString()`,
producing the same. iOS asked for `as? String`, got `nil`, and fell back to
`HTTP 422`; Windows called `GetString()` on an array, which throws, was
caught, and did the same.

    asked     is the refusal translated
    mattered  is the refusal a sentence

The `msg` translated last release was correct, arrived, and was read by
nobody: it sat inside a JSON blob or was discarded for a status code. Two of
the four families showed the person **less** than before their language was
ever considered.

**The fix.** `i18n.validation_message` composes one sentence from the rows, in
the reader's language, and rides beside `detail` rather than replacing it —
`detail` is the FastAPI contract, what a machine reading this API has a right
to, and what the driven tests read. Every client decode now reads the sentence
first. The field name stays the API's own (`display_name`), joined with an em
dash rather than declined into the sentence, so nothing comes out half in one
language and half in another. Mapping those names to the labels a form
actually shows needs a per-client table that does not exist, and is recorded as
the remaining gap rather than guessed at.

**The guard took three attempts, and the first two are why the third is worth
having.** Asking whether a client's source mentions `message` passed on all
four clients while all four were broken — it is a field on a model, a
parameter name on an exception class, and a word in the comment directly above
the bug. Anchoring on the throw and asking whether the surrounding lines read
it caught the three shells and still passed on a broken console, because the
fallback chain has always read the sentence key as an *alternative to*
`detail`.

    asked     does the decode mention the sentence
    mattered  does the decode pass the sentence on

Seven injections, each caught by the right test with the right message.

## [0.30.2] — 2026-08-01

### The synthetic self: the one QRME profile that is the user

Every other link between these products reaches *somebody else's* profile. A
tandem specialist belongs to a clinician; a coordination runs in the care-team
org; a delegated workflow has an owner who is not the JIM user. In all of it
the JIM user meets QRME as an **interactor** — `tandem_links` maps them to a
`usr_` id and a capability token — which is to say, as a stranger.

QRME's `ProfileKind` is `self | other_person | fictional | hybrid`, and a
`self` profile speaks *as* the person. JIM had no column, module or route that
knew it existed, and QRME held nothing pointing back.

    asked     does JIM reference synthetic profiles
    mattered  does JIM reference this person's own

`docs/tandem.md` carries the contract, byte-identical in three repositories,
and was written **before** this code so the boundary could not be settled by
whatever the first implementation happened to do. `jim/synthetic_self.py`
implements it: an owner token rather than an interactor token; the link refused
unless QRME reports `kind == "self"`; an enumerated allowlist consented per
category and empty by default; the brief composed **from** the allowlist rather
than filtered down to it, so a category nobody wrote a builder for cannot cross
by a future route; and a standing rather than a history, replaced on each brief.

**Medication carries the person's own words, by decision, and the contract says
so** rather than leaving it to the code. `meds.py` refuses a medication with no
name and invites their wording — *"the little white one, 10 mg"* — so names are
free text by design, and a name can be a diagnosis: *"the pill for my HIV"* is
one typed into a field asking for a drug. The preview shows the strings and not
a count of them, because that is the only form in which the decision is real.
Journal entries, check-in notes and transcripts never cross under any consent:
there is no builder for them, which is the enforcement.

The preview **is** the payload — same function, asserted. A preview composed
separately is a preview free to drift from what goes, which is the shape of
every *we only share anonymous data* claim that turned out to be false.

The brief is posted as source material to QRME's own owner-gated
`/profiles/{id}/sources`, so it lands where the persona is grounded and is
sealed into PDI when QRME has a vault configured.

Doors on all four clients: console screen 101, localized into ten languages
from the start, and a screen on iOS, Android and Windows with a real
`ApiClient` method behind each.


### A screen that calls the localizer, and a localizer with nothing to say

The three native screens were written, the suite went green, and the twenty
`L10n` keys had gone into the console's `app/src/l10n.ts` and **none of the
three native tables**.

    asked     does the screen call the localizer
    mattered  does the localizer have anything to say

Every existing guard passed, for a reason worth naming: `native_untranslated.txt`
records English strings that are *present*, and those screens held no English to
find — only key names. The door audits passed because the bindings were called.
On a device, `L10n.t("self.title")` with no row returns the key, so the heading
would have read `self.title` in every language, on all three phones, on the
screen about what a person's medication may say about them.

`test_a_shell_asks_for_a_key_it_has.py` checks both directions **per shell** —
a union tells you *some* client is fine, which is this suite's oldest lesson.
Injecting the original state reproduces it: *"ios asks for 20 key(s) its L10n
table does not hold"*.

Run backwards it found four rows nobody had noticed — `action.refresh`,
`action.save`, `action.send`, `action.translate`: generic verbs added for
screens never written, translated into ten languages and read by nobody. The
console gained that check in 0.27.0 after two dead keys shipped; the shells
never had it. Recorded in `native_dead_keys.txt` and ratcheted rather than
deleted.

The `self.*` rows were lifted from the console table programmatically, not
retyped, and a test asserts the four surfaces still say the same thing.

## [0.30.1] — 2026-08-01

### The refusal that handed the body back

The round in 0.30.0 put every refusal this product *writes* into the reader's
language, through nine handlers that all return by one door. It missed every
refusal this product *returns*.

    asked     is every refusal this product writes translated
    mattered  is every refusal this product returns

`RequestValidationError` is neither an `HTTPException` nor one of the eight
domain errors, so a 422 went out past all nine — carrying pydantic's `input`
key, which on a missing field is the entire submitted body. A real drive
against `POST /journal`:

    {"type": "missing", "loc": ["body", "text"], "msg": "Field required",
     "input": {"entry": "chest pain since Tuesday, have not told my
               daughter", "mood": 3}}

Every other part of this product's error design refuses to carry content —
`errors.ts` and the three `Problems` shells record a method, a redacted path
and a status and have no parameter a message could arrive through; `cloudgw`
refuses a report whole if it finds prose in it. The one place content left the
process was the framework's default renderer, because nobody had looked at it
as ours.

**What this is not:** disclosure between people. A 422 goes back to whoever
sent the request, so what came back was the sender's own body. **What it is:**
content on an error path, travelling through whatever sits between the app and
the person.

`type`, `loc` and `msg` are returned; `input` and `ctx` are not, built as an
allowlist so the response cannot grow a leak by somebody else's release.
`value_error` and `assertion_error` messages are replaced outright. On
`extra_forbidden` the caller's key is echoed only when it is *shaped* like a
field name — the first version replaced it always, and the sibling
repository's suite failed by name, because a round had been spent making two
routes strict precisely so a caller is told which key was wrong.

    asked     can a key carry content
    mattered  does this key look like content

The guard posts a canary at every body-taking route from `all_routes` rather
than checking for the `input` key, and a second check asserts how many of those
routes reached validation at all.


### The synthetic self enters the tandem contract

`docs/tandem.md` gains the boundary before the code that will obey it.

Everything the contract described linked JIM to *somebody else's* profile, and
the JIM user reached QRME as an **interactor** — a stranger. QRME's
`ProfileKind` is `self | other_person | fictional | hybrid` and a `self`
profile speaks *as* the person; JIM had no column, module or route that knew it
existed, and QRME held nothing pointing back.

    asked     does JIM reference synthetic profiles
    mattered  does JIM reference this person's own

An owner token, not an interactor token. The link refused unless QRME reports
`kind == "self"`. JIM → QRME is an enumerated allowlist, consented per
category, empty by default, with the composer building the brief *from* the
allowlist rather than filtering a payload down to it — and no free text from
the user crossing at all: no journal entry, no check-in note, no transcript.
Byte-identical in all three repositories.

## [0.30.0] — 2026-08-01

### Safety text is never machine-mangled; it was never translated either

`jim/i18n.py` opens with "everything the Guardian drafts or delivers,
localized" and is emphatic about the part that matters most:

> **Deterministic safety content** (the CPR/AED playbooks, pace cues, waiver
> terms) is *hand-translated here* for every supported language ... Safety text
> is never machine-mangled.

The playbooks are. The pace cues are. The waiver terms are. The sentences the
Guardian says when it says **no** were English — all sixty-four, including
every refusal the medication cabinet, the vigil, the crash watch and the watch
bridge can produce. Somebody setting up a fall alarm for their mother, in
Portuguese, on a Portuguese phone, was told in English what was wrong with it.

    asked     is the safety content the Guardian drafts translated
    mattered  is the safety content it refuses with

**One handler would have been the wrong fix here, and would have passed.**
The sibling repository's round is a single `HTTPException` handler and that
covers its whole surface. `create_app` in this one has **eight more**, one per
health domain, each building its own `JSONResponse`. Porting the single handler
across would have localized the framework's refusals and left every domain's
own untouched — in this product, exactly the wrong eight to miss.

    asked     are the refusals localized
    mattered  are all of them

All nine now return through `i18n.refuse`, the one place a refusal becomes a
response. `test_every_handler_returns_through_the_one_place` reads `api.py`'s
own AST and fails any handler that does not — structurally, because a driven
check would cover the eight that exist and say nothing about the ninth.

**Twenty-two** sentences translated into all nine languages: the credential
checks and every literal refusal from the four health domains. *Which*
twenty-two is itself asserted, so a later round cannot improve the count by
translating alphabetically while the cabinet slides back down the list. **42**
more recorded in `jim/tests/refusals_untranslated.txt` and ratcheted, with the
25 f-string refusals named in the header as a class the file does not cover.

`get_language`, not `effective_language`: the latter answers English whenever
the mode is `on_demand`, which is a statement about how *drafted* text arrives
— keep the original medical wording, I will translate what I choose — and says
nothing about what somebody reads when the app refuses them. The credential
names the reader, so a passer-by on a care beacon still gets their own language
and not the watched person's.

Headers are carried through `refuse()` rather than dropped. A translation round
is no reason for a 401 to stop saying how to authenticate.

## [0.29.0] — 2026-08-01

### The frame around both

The nav is the console's own surface: the phones carry ten languages, the
server answers in the reader's, and the frame around both was English whatever
anybody chose. Its labels sat in `App.tsx` as literals in a `NAV` table, which
made them the one thing no language setting could reach.

Nineteen `nav.*` keys, looked up by id — `` t(`nav.${n.id}`, lang) `` — the
same shape QRME's console has used since its chrome round.

### And what is not done, counted

`console_untranslated.txt` measured `Onboarding.tsx` alone for two releases.
That is how **677 English strings across nineteen gated screens** stayed out
of a record whose header said the backlog was thirty-five.

    asked     is the pre-session screen localized
    mattered  is the console localized

The record now covers every screen the console renders. The gated ones are a
different argument from the accountless one — their reader *has* a language
setting, and the server already honours it — which is why the nav is done this
round and the screen bodies are written down rather than half-translated.


### The console backlog reaches its floor, and eight dead keys

47 → 35 → **7**, and the seven are punctuation, a shell command and example
values — the same in every language.

Eight of last release's keys were in the table and wired to nothing. They had
been translated into ten languages and no screen looked any of them up, so the
strings stayed English while the table said otherwise. Every completeness
check passed, because they ask whether a key *has* its ten languages and never
whether anything asks for it.

    asked     is every key in the table complete
    mattered  does every key in the table reach a screen

Both repositories now check. The first version of that check read literal keys
only and called all fifty-three of QRME's `nav.*` keys dead — every one live,
looked up as `` t(`nav.${n.id}`, lang) ``. A guard against dead translations
that would have had somebody delete the working ones. It now understands a
built key's literal head.

Ten wrapped strings needed a second pass: JSX had broken them across source
lines, and a substitution matching one line finds nothing while reporting a
count that looks like success.

## [0.28.0] — 2026-08-01

### The console gets a language, and a tripwire fires exactly as designed

Last release measured the gap: JIM's native shells carry ten-language `L10n`
tables and the desktop console had none at all. This is the layer — a
`l10n.ts` with `visitorLang()`, twenty keys across all ten languages, and the
pre-session screen wired to it. The pre-session backlog is **47 → 35**;
`visitorLang` reads what the browser asked for rather than a stored setting,
because the reader of that screen has no account for a setting to live in.

Two guards broke on the way, both the same shape, and one of them had been
left there on purpose.

`test_a_promise_is_not_a_door.py` carried a tripwire whose docstring said, in
so many words, *"JIM's console has no such table yet… When it arrives, this
fails and says what to do, instead of `test_no_gated_screen_both_promises_and
_carries` going silently blind on the day the copy starts moving."* It fired
on the first build. `_prose` now resolves keys through the table the way
QRME's `_shown_text` does, and the tripwire is deleted as its own message
instructed.

`test_the_door_and_the_wire.py` broke without warning for the same reason: it
asserted a sentence was in a screen's file, and the sentence had moved.

    asked     does this file contain this English sentence
    mattered  does this screen say this to the person reading it

Both now read what the screen *shows*, whatever file the words live in.

## [0.27.0] — 2026-08-01

### The console speaks one language. Its own phones speak ten.

JIM's native shells each carry an `L10n` table in ten languages, and a round
two releases ago gave all three a `deviceLanguage` resolver so the accountless
screen could use it. The desktop console has **no `l10n.ts` at all** — no
table, no language type, no negotiation, nothing reading `navigator.languages`.
Every string on it is English and can only be English.

That is not a gap somebody left half-open. It is a surface nobody ever asked
the question of, and the reason is worth naming: QRME's console was audited
for language because QRME's console *had* a table to audit. The check followed
the infrastructure rather than the reader.

    asked     is the localized surface complete
    mattered  which surfaces were never localized at all

Forty-seven English strings sit on the screen a person meets before any
account exists. Recorded and ratcheted rather than half-fixed: building a
localization layer for a whole console is not one round, and translating a
handful of buttons would leave the same screen half-English with nothing
recording which half. This claims somebody knows it is not localized, and by
how much.

### Kotlin's other interpolation

`_spans` routes every `${`-carrying pattern to a brace counter, which is right
for the nested-template problem it was written for and blind to the *other*
form the same language uses. Kotlin interpolates `${expr}` **and** a bare
`$ident`, and only the first was ever substituted — so `"/users/$uid/meds"`
normalised to itself.

    asked     does this language interpolate with braces
    mattered  what are all the ways this language interpolates

It never produced a wrong verdict, which is why it lasted: Starlette's path
parameter matches any segment, so `$uid` resolved against `{uid}` by accident.
But the optional-parameter cut looks for a quoted `?` *inside an interpolation
span*, and a span never found cannot be looked inside — a Kotlin call written
with the `$flag` idiom would have carried its query into the path. The
divergence recorded last release is now closed rather than recorded.

## [0.26.0] — 2026-08-01

### Three copies of one guard, three different blind spots

`clientpaths.py` says of itself, in its own docstring, that it is *byte-
identical in qrme, jim-mini and pdi*. It was not, and nothing checked.

JIM's had grown two capabilities the other two never received. So the same
audit, asked the same question in three repositories, gave three different
answers — and each repository believed it was running the same check.

    asked     does this repo's audit pass
    mattered  is this repo's audit the same audit

PDI's Android client submits an intake through exactly the form its extractor
could not see. `POST /intakes/{iid}/submit` had a working door and sat in
`android_doorless.txt` as missing — the guard could see neither the call nor
its own error.

Porting the missing capability produced a second finding one layer in: the
rule arrived carrying its author's premise. The direct-connection form was
declared `verb="GET"` on the reasoning that *every array route in this shell
is a GET* — true where it was written, false in PDI, which POSTs. The verb is
now read from the `.apply { }` block, which needed the extractor to look past
a call's own parentheses for the first time (`verb_after`).

`test_the_extractors_agree.py` runs each extractor over a fixture whose answer
is written down, so a capability lost in any one repository fails **there**
rather than reporting a clean sweep. It immediately found a third divergence:
iOS and Windows normalise an interpolated segment to a placeholder and Kotlin
leaves `$id` standing. Harmless today — Starlette matches either — and written
down rather than quietly encoded, because a difference nobody has looked at is
how the first three started.

### The notice that makes it real

Last round's sender answered `awaitingNotice` on every launch, because there
was no surface to answer it on. That is the safe direction to be wrong in and
it is still wrong: a mechanism nobody can reach is a mechanism nobody chose.

Nine shells now carry a reporting card — on the screen each product already
uses for data posture. Two rules it exists to keep:

* **Show the report, do not describe it.** The preview is built by
  `Problems.report`, the same call the sender posts, so what is on screen is
  the payload. A card that said "we collect anonymous diagnostics" would be
  asking somebody to take our word for it, and would drift the first time the
  payload changed — silently, in the direction of a promise nobody is keeping.
* **No pre-ticked answer.** Neither button is painted as the expected one. A
  notice with a bright Yes and a grey No has made the choice already, and that
  is not consent — it is a layout that looks like consent.

Answering yes sends immediately rather than waiting for the next launch, so
the person who just agreed watches the buffer drain instead of being told
something happened later. A build with no address compiled in says so plainly
rather than asking for permission it has no use for.

The guard grew two checks that both caught the guard itself first. The
emphasis check searched whole files and failed on a button three sections up
that belongs to a different card; scoped to the answers, it then read one line
at a time and missed its own injection, because Swift puts the style on a
wrapped modifier below the label.

    asked     does this file mention the brand colour anywhere
    mattered  do the two answers differ in emphasis

### The drawer nobody empties

Task #110 gave all three native shells content-free error capture, and it did
that part well: `record` templates the route, drops the message, keeps the day
and not the time, and redacts on the way *in* so the buffer never holds
something that would later have to be scrubbed.

Then nothing sent it anywhere.

Nine shells across three products recorded failures into a fifty-row buffer
that filled and rolled over. Only the desktop console ever had the second
half. The tell was in the model the whole time: every shell declares a `sent`
field documented as *"how much of `count` has already been reported"*, and
nothing in any of them ever read it, because nothing ever reported. The
comment described behaviour that was not in the file.

    asked     is the failure recorded without recording anything private
    mattered  does the failure reach anybody

Written per shell rather than as a union — the console having both halves is
exactly what made this invisible for four releases. "Error reporting works"
was true of one client in four, per product.

Each of the nine now has a report builder, a watermark that advances **by
amount and not by a flag** (a row goes on counting while the request is in
flight, and a flag drops every occurrence that happened during the send), a
collector address that is empty until a release stamps one, a notice gate, and
a call at launch. The address comes from the build — `Info.plist` on iOS, a
gradle `buildConfigField` on Android, `AssemblyMetadata` on Windows — for the
same reason the console's does: an install with no address has nowhere to
send, and there is no flag for a later mistake to switch on.

**Nothing sends yet, deliberately.** `send` answers `awaitingNotice` until
somebody has been told what a report contains and chosen. The notice and the
off-switch need a surface on each shell's settings screen, and that is the
next round; until it lands the mechanism is inert by its own gate rather than
by omission.

### Two things the round turned up on its way through

**A path that belongs to another service.** The existing route guard refused
the new call: `/v1/problems` is on the Cloud Model Gateway, not on this
product's API. `NOT_A_CLIENT_CALL` was the wrong home for it — that list is
for paths *nothing should ever call*, and its own comment says to exempt a
path only for that reason and never because the audit cannot see the call. So
`ANOTHER_SERVICE` is a separate list with a separate rule: a different
deployment owns this path.

**The same guard in three repos disagrees about what it can see.** JIM's
extractor found the Android literal; QRME's and PDI's did not, and none of the
three sees the iOS or Windows equivalents. Recorded rather than fixed here —
three copies of one guard with three different blind spots is its own round,
and it is the audit's shape applied to the audit.

## [0.25.0] — 2026-08-01

Aligned with QRME 0.25.0. The three products carry one version, so a release
that only moves in one of them still moves in all three — otherwise a support
question about "0.25" has three different answers depending on which app is
being asked about.

Nothing in JIM's own code changed this cut. QRME's round covered the two
outstanding console-credential tasks and the Windows Hello field test, and
found a real defect writing each one up: a WebAuthn relying party id must be a
domain, so the ceremony could never have run from a loopback origin; and the
Apple client secret is a JWT that expires within six months with no warning of
any kind.

Neither finding reaches JIM — it has no signing ceremony and no Apple sign-in
door. Recorded here so the version's contents are legible from this repo
without opening another one.

## [0.24.0] — 2026-08-01

Three rounds, one question: **when a passer-by does reach the page built for
them, can they read what it says?** The beacon page has negotiated
`Accept-Language` since the round that localized it. Everything around the
edges of it had not.

### Five strings the named checks could not have found

`test_the_stranger_has_a_language_too.py` named four Spanish strings and
checked they appeared on the beacon page. They did. Meanwhile five strings a
passer-by reads had never gone through `tr` at all, so no language reached
them and no amount of adding translations would have:

- **Both `<title>`s** — what the tab shows, what a shared link previews as,
  and what a screen reader announces first, English under a translated
  document.
- **The greeting.** `You've found {name}.` was translated only in its
  *anonymous* branch. With a first name on the beacon the code built an
  f-string, so the largest sentence on the page was English for every finder
  holding a beacon that names somebody.
- **Both foot paragraphs** — the sentence telling a finder what pressing the
  button will and will not do. Neither branch wrapped, and testing one branch
  is how the other could have stayed English indefinitely.

Four checks now derive the list from the page rather than from what somebody
thought to name. The greeting is a whole sentence with its hole named, so
each language puts the name where its grammar wants it.

### The page was translated; the answer to the button was not

`POST /c/{id}/alarm` never read the header, and the page renders two of its
fields onto itself after the fetch: the badge saying the alarm is raised and
this is not an emergency service, and the note saying this page cannot call
anyone and you have to. Those are the two sentences on the whole surface that
most need to be understood, and they arrive while somebody is kneeling over a
person deciding what to do next. A Spanish finder read a Spanish page,
pressed a Spanish button, and was answered in English.

`note` and `badge` by name rather than a walk over the response — the Medical
ID rides in the same object, and a person's conditions, their contact's name
and their resting heart rate are facts rather than copy. Translating a
clinical value is how a responder gets misled, which is worse than an English
one they can still read. There is a test holding that line. The minor's
variant is a third sentence and is covered; the 404 the *button* answers for
a peeled-off code is translated too.

### One header, three products

QRME, JIM and PDI each grew a `negotiate()` in a different round. Compared
side by side for the first time, JIM disagreed with both on two rows.

`q=0` means **not acceptable** — RFC 9110 is explicit — so a browser sending
`ar;q=0` is refusing Arabic. This appended every recognised tag to its
ranking regardless of quality, so a header that refused the only language it
named got that language back, on the page somebody reads while deciding what
to do for a person on the floor. A malformed quality landed the same way.

Fixed here; QRME and PDI were already right. A conformance table now lives
byte-identically in all three repositories, written as decisions rather than
observations.

### Fixed

- A tripwire on `test_a_promise_is_not_a_door.py`: everything it does assumes
  a screen's words are in the screen's file, and QRME's copy of that check
  broke on exactly that assumption when a lookup table arrived. This console
  has no table yet and its server grew `jim/i18n.py` in the same round, so the
  check now fails the day one lands and says what to do.

## [0.23.0] — 2026-08-01

Two rounds, both the same question: can the person this was built for reach it?

### The ninety-second door

`relay_guidance` states its own audience in one sentence: *"What to tell
whoever is waiting. Public: the person standing over a colleague has no account
and needs an answer in ninety seconds."*

Three things were true of that route and false of the product. The console
binding sent a credential, so a route written for somebody with no account
could only be called by somebody with one. Its only caller was `Attending.tsx`,
behind the sign-in gate — and Attending is the *Guardian's* side of an alarm,
the person watching from a desk deciding whether to escalate, not the person on
the floor. And the surface the passer-by actually reaches, the page a camera
app opens when somebody scans a sticker, raised the alarm, showed the Medical
ID, and stopped.

The ninety seconds were being counted by somebody who could not get to the
thing being counted. The guidance box is now on that page, built from the alarm
id the alarm's own response carries, on a relative URL for the same reason the
alarm endpoint is relative. It renders whether or not the Medical ID opened: a
minor's beacon opens no clinical stage to anybody, and the person kneeling over
a child needs to know what to do more than anyone, not less.

### The stranger's language

Every localization path here takes a `user_id` — right for everything a user
reads, and useless for the one reader who has none. `landing.py` had known
since the day it was written that its reader is *"a stranger with no account"*,
kneeling next to somebody on the floor, and served them English everywhere in
the world: the sentence telling them to call an ambulance, and the instruction
not to move the person.

`Accept-Language` rides on every one of those requests and nothing read it.
`i18n.negotiate` now picks the **finder's** language — not the watched
person's, whose is known and is the wrong one, because the text is for whoever
is holding the phone. Forty-seven strings across nine languages, hand
translated, because `i18n.py` set that rule before this round: *safety text is
never machine-mangled*. The guidance answer itself is localized too, not just
the frame.

### Fixed

- `FamilyView` on iOS can unlink a child it linked. A guardian link is a
  surveillance relationship that outlives its reason — children grow up,
  custody changes, households end — and the surface that creates it could not
  end it.
- The console's `alarmGuidance` binding no longer sends a credential to a route
  whose documented caller has none.

## [0.22.0] — 2026-07-31

**The console backlog reaches zero.** The 109 routes the desktop app could
not reach now all have doors, and so do the four `api.ts` bindings nothing
called. All three record files — `console_doorless.txt`,
`doorless_routes.txt`, `unused_bindings.txt` — are empty rather than short,
and the tests that read them assert emptiness.

### Added

- **Six console screens** for the six families the routes fell into.
  *What you're working on* (goals, habits, budgets), *Who you watch*
  (a child's account and its limits), *What's held about you* (custody,
  access, plan, erasure), *Who else is looking* (specialists, referrals,
  the escalation ladder), *What reaches out* (a robot, a placed code, an
  account elsewhere, an excursion), and *Bearing* (how it speaks, what it
  was told, what it made of that). Screens 95–100, with lessons and help
  directions for each.
- **Starting without an email address.** `POST /enroll` has always taken a
  name, a birthdate and a consent — every screen in front of it demanded an
  address and a password, so the only way to reach it was a phone. An email
  address is a thing a person may not have, may not control, or may share
  with somebody they are trying not to be watched by. The trade is stated
  rather than buried: no address means no recovery.
- **Looking at a clinical capture.** The console listed a person's own body
  photographs with no way to see what was in them; the image is on its own
  route and is now fetched on request, one press per capture.
- **Handing channel 2 over**, with the reason, the route, and whether
  anybody else was in the room.
- **Reading the vigil without sweeping it.** Opening Privacy sweeps, which
  can *trip* the vigil and send somebody to a person's door — a write. There
  is now a way to look without acting.

### Fixed

- **`raiseEmergency` sent no credential.** The server requires one, and the
  reason is better than the premise the binding was written on: an
  uncredentialed `POST /emergency/{id}` lets anybody reach
  `emergency_services` against anybody's account. The uncredentialed door for
  a bystander already existed and is a different one — a scanned care code,
  capped at `notify_contact`. The escalation policy said so in a field the
  client already reads.
- **`accessLog` was typed as a list.** It answers an object whose other three
  fields say whether anything is being recorded at all. Typed as a list, the
  screen would have shown a person an empty access log when the truth was
  that no log exists.
- **`custodyProvenance` and `referralClinicians`** were bound without the
  query parameters they require, so both were a 422 every time.
- **The scan page and the QR routes** were bound through the JSON helper,
  which falls back to `null` on a body it cannot parse. All three came back
  as `null`.
- **The social beacon and its code** need the owner's token, unlike the
  placed-code pair they resemble.
- **`clientpaths` read one shape of call.** Adding the text helper made three
  working doors invisible to the audit — the third false positive from an
  extractor after the nested template and the `<img src>`.
- **Two guards that could only pass while the problem existed.** The union
  guard asserted its backlog was *strictly* smaller than the console's; the
  liveness guard asserted the snapshot file was non-empty. Both have been
  rewritten to check what they were for rather than what they happened to
  measure.

## [0.21.0] — 2026-07-31

Cut in step with QRME, which ran four door-audit rounds this
release. No JIM-mini feature work: version strings, and the
release-title convention recorded in `docs/releasing.md` — release
titles now carry the product name.

The console-only backlog here stands at **109 routes** and is
unchanged; the ratchet holds it from rising.

## [0.20.1] — 2026-07-31

**The union hid a surface.** `clientpaths.doorless` unions the console with the
iOS, Android and Windows shells, so a route only the phone calls counts as
doored — the union backlog said 69 while the console alone could not reach
**109 routes**. The guard was answering *some client can reach this*,
which was true, in place of *this client can reach this*, which was not.

### Added

- **`test_the_console_is_a_client_too.py`** — the console's own backlog, in
  `console_doorless.txt`, checked in both directions and ratcheted so it cannot
  grow past where it started. The union guard stays; a route no client anywhere
  calls is still worse. A phone-only capability is a legitimate design choice,
  which is what the snapshot is for: deferring one takes a deliberate edit and
  shows up in a diff.
- **`test_a_binding_is_not_a_door.py`** — a function in `api.ts` that no screen
  calls is not a door, and `doorless` counts it as one. The docstring on
  `doorless` had said this was "a discipline rather than something the test can
  enforce"; it turned out to be enforceable in about twenty lines. *The test
  cannot check this* is a claim worth testing.

### Fixed

- **`clientpaths.py` was not byte-identical across the three repositories**,
  though it says it is. This repository never received the `fetch`,
  `window.open`, `<img src>` and `<a href>` call forms from the previous
  round, so its backlog counted doors that existed and reported work already
  done. Restored. The backlog dropped 73 → 69 as a result.
- **The pairing QR is built from a literal.** `Settings.tsx` rendered it as
  `getBase() + pair.qr_svg`, where the path arrives in a response body — a
  real door no static check can see. `GET /pair/qr.svg` had been sitting in
  `NOT_A_CLIENT_CALL` for exactly that reason, which is an exemption made out
  of a blind spot; the last one of those turned out to have no door at all.
  Same request, now visible to the audit.

## [0.20.0] — 2026-07-31

**The native shells record what breaks, and the route guard stopped inventing
work.** Two rounds, and a suite-wide version cut that keeps QRME, JIM-mini and
PDI on one number.

### Failures from the phone and the desktop shell

The consoles have recorded failures content-free since 0.19.0 — the operation
and the status, never the message, never the path as it was typed. That is the
governing constraint on this feature: a crash report is worth having only if
nothing private travels in it, and the safest way to guarantee that is to have
nothing private to send. The web console has done it since 0.19.0; iOS, Android
and the desktop shell had not, so a failure that happened only on a phone
happened only in silence.

All three native surfaces now record on the same terms and post to the same
gateway. `docs/cloud-model.md` — byte-identical across the three repositories —
gains the gateway's container deploy path, because the gateway lives in QRME's
tree but every product's console posts to it, and the instructions belong
wherever somebody is reading about the contract.

### A guard that invented work

Every earlier defect in `clientpaths.py` made it too **lenient**: a truncated
path, a verb read off a neighbouring call, a route table read flat instead of
recursed. Those are the failures you expect from a checker, and the ones its
guard-on-guard was written to catch.

This one was the other kind. A template literal may nest another inside an
interpolation, and the backtick alternative in the extraction pattern stopped
at the *inner* opening backtick — so a call normalised to a path no route
matches, and a route that had a working door all along was reported as having
none.

Nothing failed. The suite stayed green. The route simply sat on the backlog
looking like work, and a door-building round was aimed at it before anybody
noticed the door was already there. **A checker that invents work fails more
quietly than one that misses some:** a miss is found by the bug it let through,
while an invention is found only by somebody going to do the work and finding
it done. Interpolations are now matched by counting braces, so a nested one
passes through intact.

## [0.19.1] — 2026-07-30

**A feature can no longer ship with nothing drawn.** The gallery tests all
check screens against the README — a reference with no file, a file with no
reference, a gap in the numbering. Every one of them starts from the screens,
and none asks the opposite question: does this surface have a screen at all?
So a feature could ship with nothing drawn, nothing taught and nothing for the
in-app helper to point at, and the suite stayed green.

That had happened three times, most recently to 0.19.0's own error-reporting
card and its first-run notice — undrawn while the release notes described them
at length. It is the same shape of flaw found twice before in this suite: a
guard that only walks the relation in the direction where the answers already
exist, like the doorless audit before it counted call sites, or the redaction
check that read a shrinking snapshot and would have gone vacuous the day it
emptied.

`ui_screens.txt` is the missing direction. Every console surface now carries a
screen number, `undrawn`, or `unaudited`, so a surface nobody has classified
fails the suite in the round that introduces it. The mapping is declared rather
than inferred on purpose: matching component names against screen titles
resolved only ten of twenty-four, because titles are written for the person
using the app and component names for the person editing it, and guessing the
rest would have produced a mapping that looked complete and was not.

Both backlogs are ratcheted against a ceiling each repository declares for
itself — one hardcoded number would be the largest of the three and leave the
other two slack to grow into. A ceiling left high after the backlog falls fails
too, because a ratchet that stops ratcheting re-opens the ground it gained.
Verified by injecting five failures, including the one that gives the check its
teeth: silencing it by writing `undrawn` fails the ratchet.

**And the two surfaces it caught are drawn.** Screens **93 What Went Wrong** and **94 Before Anything Is Sent** join the gallery, each
with a lesson and with phrasings that reach it by asking the helper in the
words somebody actually types when something has broken — "it failed",
"something broke", "stop sending", "opt out". The card draws an operation and a
status and nothing else, because that is all the log holds; drawing a message
there would depict a product that does not exist.

## [0.19.0] — 2026-07-30

**The apps now record what fails, without recording anything private.** Every
failed request passes through one function in the console, so one call there
catches the lot — but the obvious version of this feature would have quietly
undone what every other screen promises.

The backends put user input straight into their error messages: *no device
called 'Pixel Buds' on this account*, *unknown site 'knee'*, *unknown language
'xx'*. Those are good messages for the person reading them and bad things to
keep. In JIM those messages can be health content, which is why the rule is absolute rather than a judgement call per message. So the message is shown to the user, who owns it, and is **never
written to the log**. The same reasoning rules out the path:
`/profiles/prf_0de08e794ed0/chat` identifies a person, `POST /profiles/{id}/chat`
identifies a bug, and only the second is recorded.

What a report contains is the operation, the status, the app version, platform
and language, a count and a date — no ids, no messages, no bodies, no
timestamps finer than a day. The redaction happens on the way *in*, so there is
no moment at which the buffer holds something that would have to be scrubbed
later.

**Sent once at launch, if the build has anywhere to send.** A Settings card
shows the exact payload — the same object the copy button produces and the
sender posts, from one function, so the preview cannot drift from what leaves.
The address is compiled in at build time and unset by default, which is a
stronger "off" than a flag: with no address there is nothing for a later
mistake to switch on. Where one is set, the console posts alongside the update
check and swallows every failure, because a diagnostic that can delay a launch
has stopped being worth having. Anyone who would rather it did not happen can
turn it off on the same card.

Counts go as **deltas** — each row remembers how much of itself has been
reported, so reopening the app twenty times does not turn one broken screen
into twenty. A failed send moves nothing and the next launch tries again.

The gateway that receives them, `cloudgw` in QRME's repository, accepts exactly
five top-level keys and five per problem and **422s on anything else**: an
unknown field, a `platform` string long enough to hide a sentence, a `day`
carrying a time of day, or a path with an unredacted id still in it. It could
redact that path itself — the pattern is right there — but then a build whose
redaction had broken would keep working and nobody would learn that every
report from those users had been arriving with an id in it. For JIM that matters more than anywhere else in the suite: `cap_` is a clinical capture, and a path naming one is a photograph of somebody's body. What survives is
less than what arrives: reports fold into counters keyed by product, version,
platform, operation and status, locale is validated and then dropped, and
nothing records that a particular install sent anything. Reading that aggregate
needs a narrower permission than writing to it, because the posting token ships
inside every installer and is public the moment somebody unzips one.

**Nothing goes before you have been asked.** Sending is opt-*out*, which only
means something if the opting-out can happen before the first report rather
than being discovered afterwards in a settings panel nobody opened. So the
sender refuses until a first-run notice has been answered — and that notice
shows the actual payload rather than describing it, from the same function
that posts it, so it cannot go stale while still looking honest. Both answers
are offered, the answer is remembered, and the switch on the Settings card is
that same answer, changeable whenever. It only appears where a build has a
collector at all: interrupting somebody to explain a thing that cannot happen
teaches them these notices are noise.

Seventeen tests hold the shape in place here, with twenty-two more on the
gateway — that `recordProblem` has no parameter a message could arrive through,
that the stored record has no field one could sit in, that the wire shape and
the gateway's whitelist still agree, that the redaction catches short ids as
well as long ones, and that it never eats a real route name. Four leaks were
injected to prove they fail: a `detail` parameter on the recorder, the
redaction narrowed back to six-hex-character ids, a `detail` field added to the
outgoing report, and the send routed back through the recording client so it
would log its own delivery attempts. All four were caught — and the third
exposed a real gap while doing it, since that check only ran in the repo
shipping the gateway rather than here.


**Channel 2 and the clinical camera reach a person.** Both had complete
backends and no caller anywhere. The microphone could be attached to a device,
metered, handed to a call and released, and its whole history read back; the
camera could seal a photograph into the vault, release a chosen few to a
clinician and withdraw one afterwards. None of it was reachable from the
console or from any shell.

**Devices had to come first**, because they are the precondition rather than a
separate feature: a microphone attaches to a device the account already knows,
never to a name typed in the moment. What is listening is therefore always
something registered on purpose.

Every vocabulary on the new **Channel & camera** screen is fetched, not typed
out — the microphone types, the gain levels, the twenty-one capture sites, the
three kinds, and the list of which sites count as intimate. Two reasons, and
the second is the one that matters: a picker built from the server's own list
cannot offer a value the handler will refuse, and the *rules* travel with the
options instead of being restated in the client where they would drift.

Three details are the server's judgement rendered rather than the console's
invention:

- **Ambient microphones are shown as refused, with the reason.** A conference
  phone or a room array cannot be channel 2, because everyone it picks up would
  be lending their voice without being asked. Listing them as unavailable
  answers the question that a missing option would raise.
- **Gain is not volume.** Every level is the owner at a different distance, and
  the server says per level whether it `reaches_others` — so the buttons say it
  too. While somebody else's voice is in the air the agent narrows itself
  regardless of the setting, and the screen says the setting comes back
  afterwards rather than leaving a silent override to be discovered.
- **An intimate site needs its own tick before a file can be chosen**, and
  attaching to a referral reports how many had to be named one at a time —
  intimate captures are never swept in by a condition match.

Seventeen routes came off the doorless list, 90 → 73.


**The crash watch can now be answered.** JIM could already raise an alarm — an
unanswered check-in, a scanned beacon, a fall through the watch drip — and every
route for *resolving* one had existed for versions with nothing calling it.
Accepting an alarm, clearing it, escalating it, seeing which pages went out and
which incidents were recorded: all reachable from the backend, none reachable
from a person. An alarm nobody can answer is worse than no alarm at all, because
the system has already told somebody that help is coming.

A new **Safety** screen sits directly under Live Monitoring — the same
emergency, seen from the answering end rather than the raising end. Open alarms
come first and separately, because on arrival during an emergency the only
question is what still needs a human; history is below the fold rather than
mixed in. Accepting an alarm **names a responder**, which the backend requires
and which is the right requirement: "someone is coming" is not a state, it is a
person. Escalation is one press with no confirm — in the moment it is needed a
modal is an obstacle — while *clearing* asks, because clearing is the
irreversible direction. Beacons are placed and listed here too, and the pages
JIM sent on the user's behalf are shown with whether they arrived, since a
message that failed to deliver is the one most worth knowing about.

Two more doors in Privacy. **What you contribute** shows whether anything has
gone to the shared model and how much, with the button that stops it — counts
from the server rather than described in prose, because "some anonymised
signals" is the kind of reassurance that survives the behaviour changing
underneath it. **Where to look** sets the locality the community door searches
near, entered rather than inferred from an IP address: a guess about where
somebody lives is not a thing to make quietly.

Eleven routes came off the doorless list, 101 → 90.

**Scope, stated rather than implied.** Four families in the same block still
have no door — the channel-2 microphone, clinical captures, the medical referral
flow, and specialist tasks. Each needs real discovery first (the mic attaches
only to an already-registered device, captures validate against a site
vocabulary, referrals and specialist tasks want a configured tandem), and
half-wiring them would have been worse than leaving them listed. They stay on
the backlog, where the test keeps them visible.

**A limitation of the audit, found by using it.** The doorless check counts call
sites, so a binding added to `api.ts` and wired to no screen counts as a door
and takes its route off the list — while the capability stays unreachable. This
round's first pass added all 31 bindings before any screen existed, which would
have reported 31 doors built and delivered none. The 20 unwired ones were
removed rather than left to flatter the number, and the rule is now written into
the audit: add the binding in the same change as the screen that calls it.

**101 of JIM's 219 routes cannot be reached from any client.** The route guard
asks whether every call reaches a route. This asks the inverse — whether every
route is reachable from a door a user can open — and it is the quieter of the
two failures. A client calling a route that does not exist produces a 404
somebody reports. A route no client calls produces nothing at all: the code is
present, its tests pass, and the capability is simply unreachable.

The gap is not evenly spread. Thirty-one of them sit under `/users/{id}/`, and
they are not obscure: the **channel-2 microphone** (set, gain, handover,
release, history), **clinical captures** (create, attach, image, delete), the
**medical referral** flow (clinicians, prepare, requests, released),
**specialist tasks**, **cloud-contribution** preview and revoke, **alarms**
(accept, clear, escalate), **incidents**, **beacons**, **locality**. The helper
**dock** and the **tutorial** are two more families with routes and no caller.

Several of those have drawn screens in `docs/screens/` and rows in the README
gallery. Drawn, documented, and unreachable in every shipping client — which is
worth saying plainly, because the gallery is the thing that made them look done.

The count is recorded in `jim/tests/doorless_routes.txt`. The list is a backlog
rather than an approval: it cannot grow, because a new route with no door fails
the test; and it must shrink deliberately, because building a door fails the
test too, telling you to strike the line.

**Every option JIM offers, JIM now has to accept.** A catalog endpoint is a
menu — the console and the three shells render it directly, so whatever it lists
is what a user can pick. If the endpoint that *consumes* the choice refuses one
of those values, the user gets an error for doing exactly what they were
offered. That is the shape of the bug that left a sibling's community wall with
dead buttons, and the one the route guard says plainly it cannot see: the
request routes perfectly and the refusal happens inside the handler, after
dispatch.

Six checks now send the request rather than read the source — languages in both
delivery modes, the providers on the model menu, the robots in the catalog, the
connectors — plus one that is not about a dead button at all.

**`/languages` promises translated safety content per language, and now has to
keep it.** The flag tells a user whether the CPR and AED playbooks and the
waiver terms arrive in their language or fall back to English. The trap is
structural rather than present: `HAND_TRANSLATED` is *derived* — every supported
language except the default is flagged `true` automatically — while the strings
themselves live in a hand-written table of twenty. Adding a tenth language would
therefore promise translated resuscitation steps in the very commit that gives
it none, and nothing would have said so. The table is complete today; this keeps
it that way. Verified by adding Korean and watching the check name all twenty
missing strings.

**No field bug came out of this** — every advertised value is accepted, and
every language claiming translated safety content has all of it.

**The guard now checks the verb, not just the address.** Matching a path while
ignoring the method accepts a client that sends POST where only GET is mounted.
The answer is a 405 rather than a 404, and from the user's side that is the same
dead button. The check now requires a full router match, method included, and
reads the verb the way each language actually writes it: labelled in TypeScript
and Swift (`method: "PUT"`), positional in Kotlin, encoded in the helper's own
name in C# (`Post(...)`, `HttpMethod.Get`).

Scoping the check to the enclosing *call* rather than to loose path-shaped
strings is what made that possible, and it widened the net at the same time:
double-quoted paths, the ones written without interpolation, had been skipped
entirely, so JIM's console went from 33 checked paths to 65 verb-and-path pairs.

Each language's verb reader gets its own liveness test, because they are
separate code and they fail quietly. If one stops matching, every call from that
surface silently becomes a GET — and since most routes do serve a GET, the suite
would stay green while checking almost nothing.

All 243 verb-and-path pairs across JIM's four surfaces are accepted; no field
bug came out of this. Method-awareness was verified by injecting the mistake it
exists to catch and watching the check name the verb the route really accepts.

Earlier in this cycle, the guard arrived at all: **JIM's four client surfaces
now have what QRME got after its Wall bug.** In the sibling, every like, comment and share on the community wall
returned 404 for as long as the buttons had existed: the console asked for a
singular path segment the routes only map in the plural. The backend tests
passed because they used the reachable form, the console compiled because a
template literal is only a string, and nobody was comparing the two halves.

JIM had the same exposure and none of the checking. The console builds 33
paths in template literals; the iOS, Android and Windows shells build about
45 each in Swift, Kotlin and C#, where `native.yml` proves they *compile* and
cannot say whether they *resolve*. All four surfaces are now checked against
the real route table.

Two tests guard the guard. One fails if a language's extraction pattern stops
matching, because a scan that silently finds nothing reads exactly like a scan
that finds nothing wrong. The other pins a real defect found in the sibling's
extractor: it cut a path at its first interpolation whenever a query followed,
which turns `/meds/${uid}/adherence?days=${d}` into bare `/meds` — a prefix
that resolves for the wrong reason. JIM's medication adherence board is that
exact shape, so it is the fixture.

No field bug came out of this: every path JIM's four surfaces build resolves.
The checks were verified by injecting a broken path and watching each one
fail.

## [0.18.0] — 2026-07-30

**Four features get drawn, taught and findable.** The community door, the
effectiveness loop, the adaptation profile and the anonymity posture all
had code and screens in the app — and no drawing, no lesson, and no way
for the help assistant to point anybody at them.

Four screens join the gallery: **89 Did That Help?**, **90 What JIM
Learned**, **91 Your Name Here** and **92 Community**. Each gets a lesson,
and each is reachable by asking the assistant in ordinary words — "it did
not help", "what JIM knows about me", "pseudonym", "rooms" — rather than
by knowing which tab to open.

**Three more things JIM knew but only the web console asked about.** The
effectiveness loop, the user-specific model and the anonymity posture all
reach iOS, Android and Windows. This finishes a native round that shipped
the community bridge and stopped there — the other three features named
in its own scope had no native door at all, which is the same
"door nobody can open" failure this project keeps relearning.

**"Did that help?"** now sits on Monitor in all three shells (spec
[0039]). It reads from `/followup/{uid}` rather than from the monitor
reply, so a question opened in an *earlier* session is still asked instead
of being silently dropped. Answering "it did not" is not a complaint filed
away: the escalation ladder runs again with the ineffective-guidance rung
and the screen names the humans reachable right now — the spec's second
door, shown as people rather than as a tier.

**What JIM has learned about you** and **Your name here** join Overview,
which is where these shells already keep the baseline, model and language
settings. The adaptation profile is rendered as counts off the user's own
history — which guidance helped and how often — never a score, with the
statement that nothing was sent to a model vendor to build it and a note
when the sealed copy is in their own vault. The anonymity posture is
rendered from the server's own `keeps` and `costs` lists, so the tradeoff
on screen cannot drift from the one in the code.

## [0.17.0] — 2026-07-30

**The community bridge reaches the native shells.** The door out to
QRME's rooms and local places shipped in the web console only; iOS,
Android and Windows had no way to it at all. All three gain a
**Community** panel alongside Sources / Social / Apps in Connect —
FIG. 2's boxes 222–226, opened rather than reimplemented.

Two details are deliberate. The "what JIM does not do" list — mirror the
conversation here, post on your behalf, share your health data — is
rendered from the booleans the server returns rather than typed out as
reassurance, so the screen cannot drift from what the bridge actually
does. And opening a room posts the visit to `/community/{uid}/visits`
*before* launching the browser: the note is the part that belongs to JIM,
an event on the user's own timeline recording that a door was opened and
nothing from inside it.

**Fixed** — the Windows palette had no `JimT3Brush`. The dimmest text
tier exists in the Android and iOS themes but the desktop resources
stopped at `T2`, so any page reaching for it would have failed to load
its resources rather than merely looking wrong. Added, matching the
other two shells.

**Two things JIM knew but never showed you.** The user-specific model
and the anonymity posture were both real in the backend and invisible in
the app. Settings now carries them. **What JIM has learned about you**
shows the claim-11 profile in plain terms — the confidence it has earned
from your own history, which guidance has actually helped and how often,
the work you named, the tone you asked for — with a Rebuild button and
the reminder that nothing was sent to a model vendor to build it. **Your
name here** states your anonymity posture: the pseudonym you are known
by, what the choice keeps (every emergency path, your own records) and
what it costs (a legal name for responders, unless you left one).

**The community door: JIM points, QRME hosts.** FIG. 2 boxes 222–226
describe community inside the guidance product — interact with others,
moderate content, store it for community interaction — and [0020]
promises "our chat engines, your local events, and forums in all
languages". Every piece of that already exists in QRME, and the two
products are built to run in tandem, so the honest way to keep the
promise is a **door, not a second implementation**: `GET
/community/{user}` serves QRME's active rooms (topic, channel, heads,
an openable URL) and the places its listings actually claim
(`?locality=` filters them), in the language this user reads. A second
social network inside a private health guardian would duplicate a
moderation stack that is hard to get right once, and would put someone's
health data and their public posting in the same database — the exact
separation the suite exists to preserve. So nothing is mirrored into
JIM, nothing is ever posted on the user's behalf, no health data crosses
over, and the reply states all three in its own `posture` block.
Opening a door records **the fact only** on the user's timeline
(`POST /community/{user}/visits`) — never a word from inside the room.
409 without `JIM_QRME_URL`, and an unreachable QRME is a quiet screen
rather than an error page. Console: the new **Community** tab.

## [0.16.0] — 2026-07-30

**Anonymous by choice.** FIG. 2 box 212 of the filing says "choose name
(anonymized)", and spec [0031] spells it out: the user name "may be an
anonymous user name, the user's real name, or left to the user to
decide". QRME has had anonymity since its first round; JIM took a
`display_name` and that was your identity — which quietly excluded the
person the product most wants, somebody willing to tell a machine about
their panic attacks precisely because they are not ready to put their
name on it. Enrollment now takes `anonymous: true`: JIM mints a
pseudonym, **discards the typed name**, and never learns the real one.
Every emergency path is untouched. The one honest cost is a dispatcher
briefing, and it is handled rather than hidden: an anonymous user may
leave a `legal_name` used *only* in an emergency briefing, and if they
don't, the briefing states plainly that no legal name is on record
instead of passing a pseudonym off as an identity. `GET
/anonymity/{user}` says what the choice keeps and what it costs, and the
signup form says the same where the box is ticked.

**The loop closes: did the counseling actually work?** A verbatim
re-read of 526.P001 found four sentences of the filing with no code
behind them, and this is the largest. Spec [0039] describes what
happens *after* guidance: effective counseling resumes monitoring, and
counseling that is **not** effective "may alert a person to provide
live assistance". JIM delivered guidance and never asked. Now every
delivered guidance opens a follow-up (`GET/POST /followup/{user}`):
"it helped" is recorded and monitoring resumes, and "it didn't"
re-runs the escalation ladder with a new **ineffective-guidance
rung** — one tier up, floored at `check_in` — then names the humans
reachable right now: the deployment's own support person
(`JIM_LIVE_SUPPORT_NAME`/`_CHANNEL`), the 988 crisis line for a
psychological condition, whoever is on shift, and the emergency
contact. A rung and not a jump, deliberately: a breathing exercise
that didn't land must reach a person and must not dispatch an
ambulance on its own — while an unhelped *critical* event, already at
`notify_contact`, goes all the way to emergency services.

**A user-specific model, and an honest account of what that is.**
Claim 11 describes "training a user-specific version of the large
language model based on the received input … secure, decentralized
methods". JIM had only the last mile of that — live preferences
rendered into a prompt. Now there is an artifact: `POST
/adaptation/{user}` derives a versioned adaptation profile from this
user's own stored history — declared conditions, check-in trend, the
life areas they actually bring, the tone they asked for, and the
follow-up record of **what has actually helped them** — and seals it
into the PDI vault when a tandem is configured, keys the user's,
nothing to any model vendor. Confidence is earned from evidence
volume rather than fluency; the profile conditions prompts only where
the evidence supports it (three answered follow-ups before "this
works for you" is a claim, and guidance that keeps missing tells the
coach to change approach and offer a human); and the profile says in
its own `method` field that the transformer's weights belong to the
vendor and are not modified here.

**The coach learns your tone without being sent to a settings
screen.** Clause 12's second half — the system "may autonomously
refine its tone … to align with user preferences". "Keep it short" in
a coach prompt is now kept as a preference from that turn on (the
turn that asked already gets the shorter answer), via a transparent
phrase table rather than a hidden model read, and the reply reports
what it learned (`adapted_tone`) instead of silently changing
character.

**Neutral by default, and it says so.** Spec [0019] asks for guidance
"structured to be neutral to a person's background or beliefs, such
as religion, politics, sexual orientation … and in other examples …
derived with sensitivity to the user's beliefs", and tailored to "a
user's general intelligence or ability to quickly grasp and apply
guidance". Age and maturity already rode the prompt; the rest of that
sentence had no field anywhere. `PUT /personality` gains
`beliefs_posture` (`neutral` — the default, stated explicitly in
every prompt, with an instruction never to infer beliefs — or
`sensitive`, which honors only what the user themself declared and
falls back to neutral when nothing is) and `explain_level` (`plain` /
`standard` / `technical`). It also takes an `occupation` — claim 11's
"professional roles" — because a night-shift nurse and a long-haul
driver need different advice about the same bad night's sleep.

**Sign in with Google / Apple, the Guardian's way.** The provider
vouches for the inbox, never for the consent questions: signing *up*
with Google still carries the full enrollment (name, birthdate, terms),
parked on the flow's state by the console; a brand-new account activates
the moment the provider vouches, and a returning one signs straight in.
Configuration decides whether the buttons are live (`JIM_GOOGLE_CLIENT_ID`
and friends) — an unconfigured door is grey with its setup note.

**The pace cue reaches the screen, and spending gets a plan.** From the
full pre-publish sweep of both patent filings and the brand cards. The
CPR playbook always promised its pace "cued visually and audibly" —
the console now renders it: first-aid steps on the Monitor card and a
metronome that flashes green on every compression beat at the
playbook's 110/min with an audible tick, 30:2 called out, and a stopped
metronome shown red, because stopped is off pace. And the financial
card's "alignment with budgeting plans" stops being a hardcoded $200
alarm: users set monthly limits per category and overall
(`PUT /budgets/{user}`), consented spending consumes them (the tally
keeps only an amount, category and month — the transaction's story
stays vaulted), and crossing 80% or the plan itself speaks up with the
days left in the month.

**The companion splits in two, and the assistant learns to answer
offline.** At the top escalation tier the companion now works both
hands: guiding the person through the life-saving steps in the
foreground — the pace cue gains a vibration on every compression beat
and the word PUSH on the light, 2 BREATHS called every thirtieth —
while relaying a dispatcher-ready briefing in the background (who,
known conditions, critical medications, latest vitals, what's being
done), re-relayed with every new reading and honest that an app
cannot itself place a voice call. The coach gains an **offline
knowledge pack**: fifteen curated, referenced entries across the six
areas and the sensor-borne conditions (racing pulse, low SpO2, falling
HRV, fever, blood pressure, sleep, panic, phobias, budgets, burnout,
CO exposure …) that answer when no model key is configured — the floor
under the coach, never a pretender, and silent rather than
wrong-topic. The wordmark-and-pulse logo lands as-is at the top of
this README, and `docs/showcase.html` is a share-ready page for the
founder's social audience.

**Stress joins the check-in.** The field promise was "track your mood
*and stress levels* over time", and stress had no field anywhere. Check-ins
take an optional stress reading (1 calm — 5 overwhelmed) alongside mood and
energy; the progress report averages it; and three climbing readings ending
high produce a forecast that points at a concrete strategy — two minutes of
box breathing in Wellness, and the mental-health coach — not just the bad
news. Existing databases gain the column on first launch (the schema now
carries a proper add-column migration), and a check-in without stress stays
exactly what it was. On a phone, the help button now rides above the tab
bar instead of sitting on the right-most tabs.

**The attach bracket: click a QRME starter onto a condition.** Care Team
gains a "Specialists" card that lists every condition the Guardian routes
guidance for beside who holds it today, with the QRME Starter Collection —
the 33 preloaded industry experts, each already carrying its industry's
knowledge pack profile-side — as the shelf to pick from. One click attaches
a starter in tandem mode and that condition's guidance routes through it.
The catalog rides `GET /specialists/catalog` (a clear 409 pointing at
`JIM_QRME_URL` when no tandem is configured, and a quiet empty shelf when
QRME's marketplace can't be reached — never an error page).

**Two more doors on the model menu: DeepSeek, and your own algorithm.**
DeepSeek joins the provider registry as a first-class tile
(`JIM_DEEPSEEK_API_KEY` or `DEEPSEEK_API_KEY`), an interim guide until the
founder's algorithm takes over — and that plug now exists too: a **custom**
provider pointing at any endpoint speaking the OpenAI dialect
(`JIM_CUSTOM_LLM_URL` + `JIM_CUSTOM_LLM_KEY`, optional model and label
overrides). The custom tile stays dark until its URL is set — a key alone
points at nothing — and both degrade to the stub like every other
unconfigured provider, never breaking guidance.

## [0.15.0] — 2026-07-29

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

[Unreleased]: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.16.0...HEAD
[0.19.1]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.19.1
[0.19.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.19.0
[0.18.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.18.0
[0.17.0]: https://github.com/davidsbianchi1984/jim-mini/commit/1cb6e04
[0.16.0]: https://github.com/davidsbianchi1984/jim-mini/commit/39c6b0c
[0.15.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.15.0
[0.14.5]: https://github.com/davidsbianchi1984/jim-mini/commit/cc2b6daf0e7b4c6fa11d9dc9af5d11570e2bf89d
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
