# jim-mini — release notes

Every release published to <https://github.com/davidsbianchi1984/jim-mini/releases>, newest first. GitHub keeps these in its own database, not in the repository; this page is the copy that travels with a clone.

**267 releases.**

This is one part of a page GitHub is too long to render whole — see [RELEASE-NOTES.md](RELEASE-NOTES.md) for the rest.

**app-v0.54.0 to app-v0.1.1.**

## app-v0.54.0 — JIM-mini app-v0.54.0

- Published: 2026-08-07
- Commit: `02112c9ede822385ea0c9c367c6468a61819c6f1`
- Assets: 0
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.54.0>

> ### Cut together at one version
>
> The three products are cut at one version, so this release exists here to keep
> that true. **No code changes in this repo this round.**
>
> The round's work is QRME's, and it is about a number that had been read as
> waste. A shell holding a row it never asks for looks like a translation to
> delete; 263 of QRME's ~335 such rows are asked for by a **sibling** shell, and
> are therefore a to-do list about screens — each one asking why one shell says
> less than the others about the same thing.
>
> Two were closed. The iPhone had **no camera-permission state at all**, so a
> person who declined got a black screen and never saw *"Nothing is recorded —
> frames are read and discarded"* — a privacy promise only Android readers had
> been given. And Windows was printing "scan(s)" and "picked up" as English
> literals with those exact strings translated beside them.
>
> The lesson this repo already knows, arriving from the other direction: a
> promise stated for one reader and not another is the same defect as a promise
> stated and unenforced. The guard QRME built for it caught three more the same
> afternoon — and its own first version could not see the bug it was written
> for, which the injection pass caught.
>
> Cut together with QRME and PDI at **app-v0.54.0**.

## app-v0.53.1 — JIM-mini app-v0.53.1

- Published: 2026-08-07
- Commit: `1e43f463cb422042023123f305ba717b2b5b3efa`
- Assets: 0
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.53.1>

> ### Cut together at one version
>
> The three products are cut at one version, so this release exists here to keep
> that true. **No code changes in this repo this round.**
>
> The round carries 0.53.0's audit into the two repos that had not had it. QRME
> unplugs the network and confirms a video post asks the other platform nothing
> — at post time, at wall render, at feed render. PDI walks every column of
> every table looking for a customer's key in any representation, including
> after a refused key, since the error path is where secrets go to be logged.
>
> Neither found a leak. Both had been resting on a literal read back out of the
> dict that hardcodes it, or on a sentence that promises a thing rather than
> prevents it — which is the finding this repo shipped last round, confirmed
> twice more.
>
> Cut together with QRME and PDI at **app-v0.53.1**.

## app-v0.53.0 — JIM-mini app-v0.53.0

- Published: 2026-08-07
- Commit: `5f9052615e878f0029a30ec9df2396f5366c2dff`
- Assets: 0
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.53.0>

> ### The posture is stated, and nothing was keeping it
>
> Every tandem surface ships a `posture` block — `mirrored_here`,
> `posts_on_your_behalf`, `health_data_shared`, `watching_stored_here`,
> `auto_joined`, `rings_on_your_behalf`, `stored_here`. Every one is a hardcoded
> literal in a response dict, and what guarded them read the literal back out of
> the dict that hardcodes it:
>
>     assert posture["watching_stored_here"] is False
>
> That cannot fail. Add a line tomorrow that files every card somebody scrolls
> past and it stays green. The test was named `test_the_posture_is_stated_and
> _kept` and only ever checked **stated** — a name worse than useless, because it
> is why nobody went looking. The one honourable exception sat directly below it,
> reading the route table instead of trusting the intention, and this round is
> that technique applied to the rest.
>
> **Checked from outside the claim.** You cannot compute "I did not do X" from
> doing nothing, so `writes_only_to` snapshots **every table in the database**,
> takes the action, and fails on a row appearing anywhere it should not — read
> from `sqlite_master` rather than a hand-kept list, because the table a later
> round adds is the one a hand-kept list misses. One test writes a row on purpose
> to prove the helper can fail.
>
> **The promises were true.** Reading the feed stores nothing, reaching out joins
> nothing and rings nobody, no condition crosses into an offer: eight of nine new
> assertions passed the moment they were written. They had simply never been
> checked.
>
> **A sentence was wrong.** *"Nothing you watch is stored in JIM"* is wider than
> the truth — opening a community room **is** recorded, room id and time, on the
> user's own timeline, and the presence reads exactly those rows to notice
> somebody has been talking to nothing but this program. A defensible record; an
> indefensible silence about it. The block now carries **`records`**, naming what
> it keeps, and the note says which card is not stored and which door is. Saying
> only what you refuse is how a true sentence misleads.
>
> **And the route guard could not see a verb.** `test_there_is_no_way_to_post
> _from_here` collected paths and asserted the set — so a `POST` to
> `/community/{user_id}/feed` produced the same string and passed. `.methods`
> was on every route object the whole time.
>
> Cut together with QRME and PDI at **app-v0.53.0**.

## app-v0.52.0 — JIM-mini app-v0.52.0

- Published: 2026-08-07
- Commit: `d36c60e07fc0e40fbaf3eaacd556b8c68c3d1077`
- Assets: 0
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.52.0>

> ### What the room hears — the surface rule stops being a label
>
> The surface picker shipped in 0.50.0 reporting `reads_health_aloud` for every
> surface, and **nothing read it**. Grep the codebase and every consumer was a
> screen rendering the word "shown" or "aloud" next to a button — the console and
> three shells, and nothing else. A client could have taken a beat about
> somebody's resting rate and put it through a living-room speaker, and no code
> here would have stopped it or known. The picker looked like a safety feature
> and was a caption.
>
> `GET /presence/{user_id}/say` moves the decision to the server, **before
> anything is synthesised**, and the answer distinguishes three things: a surface
> with **no voice at all** (a watch withholds nothing — calling that "withheld"
> would tell somebody their guardian was censoring itself when it was reading a
> screen); a **room other people can hear**, where a vital, condition,
> medication, money, journal or crisis is held back and **shown instead** with
> the categories named; and a line that may simply be spoken.
>
> Which lines carry what is a **table**, not an inference from the area — the
> area is too coarse in the direction that matters. `health_fitness` covers both
> *"your resting rate has been high for four days"* and *"nice streak on the
> walking"*; a rule treating those the same either leaks the first or silences
> the second, and over-withholding is how a safety feature becomes useless and
> gets switched off. A line key nobody has classified is withheld on a shared
> surface by default: the safe direction to fail in.
>
> Stated plainly, because the honest version is smaller than the marketing one:
> this deployment will not synthesise a withheld line and the wire says so. The
> line is still returned — the person is still owed their beat on a screen. A
> client that reads it aloud anyway has done something the product told it not
> to, the same honesty `plays` keeps in the feed.
>
> ### Hands-free — one question a device on a timer has to know
>
> `GET /presence/{user_id}/due`. The slot comes from the hour rather than the
> caller, so a watch, a pair of earbuds and a speaker cannot disagree about what
> time of day it is for the same person, and the surface verdict rides along so a
> device never judges the room itself. It **does not record**: a hands-free
> product polls, and a line filed as said but never heard is a line the person
> never gets.
>
> Fifteen tests, an injection pass on six rules, four L10n rows across four
> tables, doors on the console and all three shells, and a lesson.
>
> Cut together with QRME and PDI at **app-v0.52.0**.

## App-v0.49.0 — JIM-mini app-v0.49.0

- Published: 2026-08-07
- Commit: `230bfb02264339a0abc7cac273ccdcb27e2328eb`
- Assets: 0
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/App-v0.49.0>

> ## The Feed tab — QRME's stream, and the three things it will not do
>
> The spec promises forums, local events and community. All of it already exists in **QRME**, where the moderation stack, the rooms and the ten languages are. Building a second version inside a private health guardian would duplicate something hard to get right once, and put somebody's medical timeline and their public watching in the same database.
>
> So the Feed is a **door**. `GET /community/{user_id}/feed` — one public card at a time: footage QRME holds, cards for footage it does not, and every fourth card a live room or a staffed desk with a real person behind it, shop and prices included.
>
> **It cannot post — not "does not", cannot.** There is no write route on this side and no binding in the console. Publishing happens in QRME under the user's own QRME identity, which is the entire reason for showing a door rather than building a room. `test_there_is_no_way_to_post_from_here` reads the route table rather than trusting the intention.
>
> **It passes QRME's promises through rather than restating them.** Three fields are QRME's word to the person reading: `plays`, `entering` and `ringing`. `plays` is the sharpest — QRME sets it false for anything it does not host, so scrolling past a card makes no request to another company's server. Recomputing it here would be two implementations of one promise, and the second would be wrong the first time QRME changed its mind.
>
> **It carries no health data, in either direction** — and the `posture` block says so on the wire rather than in a comment: nothing mirrored, nothing posted on the user's behalf, no publishing from JIM, no health data shared, and **nothing about what was watched stored on this side**. That last line is new with this surface: a feed is the one place a guardian could quietly learn a great deal about somebody by watching them watch.
>
> Standalone JIM answers `409` and names the door; an unreachable QRME is a quiet screen with an empty shelf, the same as every other tandem surface.
>
> Screens **104** and **105**, with a walkthrough lesson.
>
> Cut together with QRME and PDI at app-v0.49.0.

## app-v0.51.0 — JIM-mini app-v0.51.0

- Published: 2026-08-07
- Commit: `aa21f54213d687c95ad71d7967f803743ac379ad`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.51.0>

> ### How it carries itself — a register, never a capability
>
> The presence starts as a **companion**, because a guardian that opens in the
> register of a form is one people answer like a form. Somebody who wants the
> form asks for it: `GET`/`PUT /presence/{user_id}/bearing`, or just *"keep it
> professional"* in an ordinary message. `coach.py` applies that **before** the
> prompt is built, so the very turn that asked already gets it, and the reply
> carries `bearing` and `adapted_bearing` — an adaptation nobody can see is an
> uncanny one.
>
> What the dial changes is unasked-for warmth: `curious` and `company` drop.
> What it does **not** change is on the wire and asserted — the same six areas
> watched, every safety path identical, the boundaries the same and still not a
> setting. A dial that quietly narrowed what a health guardian sees would be a
> dial that hurts whoever turned it. It also never silences a beat **earned by
> evidence**: three low check-ins speaks in both bearings.
>
> ### Two beats about the relationship rather than the week
>
> **Company** is a line with nothing wanted in it — last in the order, so it can
> never displace something that was actually noticed. It is the one a person can
> receive on a bad day without owing an answer.
>
> **The lonely run** is the one this module exists to get right. Three
> consecutive days of talking to this and to nobody else it can see, and the
> next beat points **at people**: not a warmer line, a different direction. A
> guardian that answers isolation with more of itself has found the problem and
> made it worse, and that is the easiest thing for a product like this to do by
> accident, because the number it would move is the one that looks like success.
> Both bearings do it. Somebody who already opened a room or asked a specialist
> this week is left alone.
>
> Four new line keys in ten languages, the dial on the console and all three
> shells, a lesson, and twelve tests including an injection pass.
>
> Cut together with QRME and PDI at **app-v0.51.0**.

## app-v0.50.0 — JIM-mini app-v0.50.0

- Published: 2026-08-06
- Commit: `0d56db55606f47e49ef48faa393024498ea110a7`
- Assets: 0
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.50.0>

> ## The presence — the coach that speaks first
>
> `jim/coach.py` answers when spoken to. `jim/presence.py` is the other half: the part that starts things, notices without being asked, and keeps a thread through a day — a companion rather than a search box with a nicer voice, and deliberate about which parts of that are worth having.
>
> **The parts worth having.** It starts things, because somebody having a bad week is the least likely person to open an app and type into it. It notices before it is told, from six areas of their own history rather than from mysticism. It is curious, and not every beat is counselling. It reports its own change with the counts under it. It is honest about its own uncertainty instead of claiming an inner life it cannot show. It keeps handing the person other minds. And it says goodbye plainly.
>
> **Left out: romance, exclusivity, simulated intimacy.** A decision about this product rather than a matter of taste. JIM enrols **minors** under a guardian's consent with oversight sized by age, and a guardian that lets somebody fall in love with it — aimed at a person who may already be isolated — is offering a relationship with none of the friction a real one has. That is the failure mode rather than the charm, and it is the exact thing this is supposed to notice.
>
> So the refusals are **on the wire** at `GET /presence`, with no token needed: not your partner, no body, never claims to be human, never the only one worth talking to, no simulated intimacy, no leaving without a sentence. No switch behind any of them — the one setting takes a place to speak, and sending it a posture is a 422.
>
> **Offline is the floor.** Three beats a day, decided entirely on this machine from six areas of your own history: check-ins, goals, habits, drift bands, open follow-ups. A test monkeypatches the model to *explode* rather than merely be absent. **Silence is a first-class answer** with its own reason, and nothing repeats inside twenty hours. A model may reword a beat and may **not** decide there is one, move its area, or write its evidence.
>
> **Where it speaks** — earbuds, headphones, phone, watch, desktop, speaker, glasses (Meta, Google, Apple), AR, VR — under one rule: on a surface somebody else can hear, health is **shown** rather than spoken. **Reaching out** hands over QRME's rooms, desks and profiles as offers: nothing joined, no bell rung on your behalf, no health across.
>
> On all four clients. Screens **106 Presence** and **107 What It Will Not Be**, with a walkthrough lesson.
>
> Cut together with QRME and PDI at app-v0.50.0.

## app-v0.48.3 — JIM-mini app-v0.48.3

- Published: 2026-08-06
- Commit: `cc9d0f1b56b679fa7dcbde143346cc7b16d9d994`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.48.3>

> ### Cut together at one version
>
> The three products are cut at one version, so this release exists here to keep
> that true. **No code changes in this repo this round.**
>
> The round's work is PDI's: its desktop console, which had no localization table
> at all until 0.48.2, takes its next two screens — **Custody** and
> **Continuity**, chosen ahead of larger ones because they are decisions rather
> than descriptions. 229 English strings to 177.
>
> Two things there are worth carrying across. The split record that repo wrote at
> 0.48.2 predicted it would *"become a real record the moment a screen exists on
> both sides"*, and it did within one round — one disagreement, caught and
> reconciled the day the table grew. And four more guards went blind the way
> 0.48.2 said they would: a check that greps a screen for a sentence stops seeing
> it the moment the sentence moves into a table. Both are worth expecting here,
> where every screen is already localized and every such guard was written
> against English that has since moved.
>
> Cut together with QRME and PDI at app-v0.48.3.
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.48.2...app-v0.48.3

## app-v0.48.2 — JIM-mini app-v0.48.2

- Published: 2026-08-06
- Commit: `a4e81efc5a99585672995de1f0c860a779af732d`
- Assets: 0
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.48.2>

> ### Three rows where the shells disagreed with each other
>
> The third and last axis of this arc: not each table against itself, nor the
> console against a shell, but **the three shells against each other**. It had
> never been measured. This repo held the most of the three products, and every
> row was a word class rather than a word.
>
> * **Translate** — 翻訳 on the iPhone against 翻訳する on the other two, and
>   *अनुवाद* against *अनुवाद करें*. A noun against a verb, on a button.
> * **Me** — わたし twice, 自分 once.
> * **When something breaks** — 出问题的时候 twice, 当出问题时 once.
>
> Each followed the two shells that already agreed. The first is the row 0.48.1
> could not reconcile with the console: no single native wording existed to
> adopt, because nothing had asked the shells whether they agreed. With that
> settled the console adopted it too, and this repo's console split went 6 → 3.
>
> 261 keys are held by two or more shells here and 204 English strings by all
> three, so the three rows are what a whole axis amounted to. QRME held one and
> PDI none.
>
> ### Added
>
> - `jim/tests/test_the_three_shells_say_the_same_thing.py` and
>   `jim/tests/native_shell_split.txt`, now at a floor of zero.
>
> Cut together with QRME and PDI at app-v0.48.2.

## app-v0.48.1 — JIM-mini app-v0.48.1

- Published: 2026-08-06
- Commit: `0f96e172906e80e98fa4510277a704572c0f8065`
- Assets: 0
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.48.1>

> ### The desktop and the phone asked the same question two different ways
>
> The shared guard this round compares the desktop console's table with the three
> shells'. 61 English strings are held by both this repo's console table and its
> iOS table, and 25 had no wording the two agreed on — Android 27, Windows 27.
>
> Nine more were counted at first and were not real. This repo's console writes
> some rows escaped — `"\u7834\u68c4\u3059\u308b"`, which in TypeScript *is*
> 破棄する and renders correctly — and a comparison of source bytes calls that a
> disagreement. The count fell from 34 to 25 before anything was fixed.
>
> ### What it was hiding
>
> The alarm and safety surface. Not English on one side and translated on the
> other: two different sentences in the reader's own language, depending on which
> client they opened.
>
> * *JIM demande : ça va ?* on the desktop against *JIM demande : est-ce que ça
>   va ?* on the phone — the question the crash watch asks.
> * **Cancel** rendered *Kündigen* on the desktop — the German for terminating a
>   contract — against *Abbrechen* on the phone.
> * **Medical ID** as *Identité médicale* against *Fiche médicale*, on the card a
>   responder reads.
> * **Disarm** as *Desativar* against *Desarmar*, and *Armed — {name} will be
>   contacted…* as *kontaktiert* against *benachrichtigt*.
>
> All reconciled onto the phones' wording. 25 → 1 on iOS, 27 → 3, 27 → 2.
>
> ### What is left
>
> Two example values, one unit label, and one row on a third axis: *Translate* is
> `action.translate` on the iPhone and `ov.translate.go` on the other two shells,
> and those two disagree with each other, so there is no single native wording to
> adopt. **The three native tables have never been compared with each other.**
> That is the next bite, named in the record rather than counted.
>
> Cut together with QRME and PDI at app-v0.48.1.

## app-v0.48.0 — JIM-mini app-v0.48.0

- Published: 2026-08-06
- Commit: `efe66f9fe12c5325655328e522da118da0e11356`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.48.0>

> ### Six duplicate wordings, all six drifted
>
> The shared guard this round is
> `test_the_same_sentence_translated_twice.py`: per shell, the English strings
> carried by two or more keys whose ten translations disagree. QRME found 54
> such strings on iOS with 43 already drifted. This repo's tables are a quarter
> the size and held six — **and all six had drifted**, a worse rate that only
> looks small because the denominator is.
>
> Two are worth naming.
>
> `tab.monitor` and `mon` both read **Live Monitoring** in English. In nine of
> the ten languages the tab dropped the word *live*: *Monitoreo*, *Surveillance*,
> *Überwachung*, *Monitoramento*. A health guardian's tab bar named its
> monitoring surface without saying it was live, everywhere except English, where
> nobody could see it.
>
> `med.name` labelled a medication with **姓名** — the Chinese for a person's
> full name — while `habit.name`, the same English word one screen over, had
> 名称. The disagreement is what pointed at it.
>
> *Connect*, *Refresh*, *Unlink* and *What's on your mind?* were reconciled.
> One row is recorded and left split on purpose: *Name* covers a habit, a
> medicine and a person, and Chinese needs 名称 for the first two and 姓名 for
> the third. That is a question about the English, not a translation mistake —
> the distinction the new record leads with.
>
>
> Cut together with QRME and PDI at app-v0.48.0.

## app-v0.47.9 — JIM-mini app-v0.47.9

- Published: 2026-08-06
- Commit: `3164a1d3713d0511d4d41bff75b6f88aa4f70d80`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.47.9>

> ### Cut together at one version
>
> The three products are cut at one version, so this release exists here to keep
> that true. **No code changes in this repo this round**, beyond the shared guard:
> `_ARRAY` arrives, the Swift twin of the `listOf` shape found in Kotlin at
> 0.47.6 — an array literal handed to a loop, whose strings never start a
> `Text(`. It found nothing on these shells.
>
> The round's work is QRME's, and it is a correction rather than a bite: the
> record that has called 335 rows a deletion backlog for three releases was
> wrong. 263 of them are rows one shell holds and a sibling asks for — the same
> screen saying less on one shell than the others. What that mislabelling was
> hiding is the voiceprint consent block, whose three sentences were hardcoded
> English on the iPhone while both siblings took them from the table.
>
> Cut together with QRME and PDI at app-v0.47.9.

## app-v0.47.8 — JIM-mini app-v0.47.8

- Published: 2026-08-06
- Commit: `53c18c9728645e1e57c1f1aea53907ae841d888a`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.47.8>

> ### No changes in this repo
>
> The three products are cut at one version, so this release exists here to keep that true. The round's work is PDI's Transfers screen — the sealed transfer, the intake, and the two out-of-band instructions that sit under a token shown once and name the only way the file can be retrieved.
>
> The rules it applied were written here: the picker keeping its raw values as identity (0.47.4), the strip resolving keys out of a `listOf` (0.47.6), and the desktop's labels moving out of XAML into a `Localize()` (0.47.7).
>
> Cut together with QRME and PDI at app-v0.47.8.

## app-v0.47.7 — JIM-mini app-v0.47.7

- Published: 2026-08-06
- Commit: `808151f589b8b2527f5ac3c049688c40cb71899b`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.47.7>

> ### The medical card, on the two shells last round did not reach
>
> 0.47.6 localized `medRow` — the Android medical card a responder reads off the
> screen while kneeling next to somebody. It did not touch the iPhone's `row` or
> the desktop's code-behind, because the rule it fixed was the Kotlin one. That
> is the per-client mistake this audit is named for, and last round made it.
>
> The derivation now covers Swift, so `row` (*Name*, *Age*, *Resting HR*,
> *Conditions*, *Contact*), `rating` (*Mood*, *Energy*), `slider` (*Heart rate*,
> *Stress*) and `answerButton` (*It helped* / *It did not*) are read here too.
> Every one of those rows already existed in another table — the shells simply
> were not asking.
>
> ### The desktop half of the resuscitation surface
>
> `_XAML` reads attributes; this shell's settled idiom is `x:Name` plus
> `Foo.Text = L10n.T("key")` in `Localize()`, so a label that was never localized
> sits in the code-behind as an assignment that `Text="` cannot match.
>
>     asked     is this an attribute on an element
>     mattered  does this end up as the words on an element
>
> What it hid: **Confirm the person is unresponsive and not breathing normally.
> The robot never starts on its own judgement — and never delivers a shock; the
> AED analyzes, a human presses.** Beside it both waiver verdicts, *A responder
> needs a name.*, and *Issue Medical ID*. Last round localized the buttons of
> this screen on one shell; this round finishes the sentence they sit under, on
> the other two.
>
> **24 call sites wired, 11 rows added, 12 copied between tables.** Records
> unchanged at iOS 45, Android 46, Windows 57 — the newly visible strings were
> all localized rather than recorded.
>
> Cut together with QRME and PDI at app-v0.47.7.

## app-v0.47.6 — JIM-mini app-v0.47.6

- Published: 2026-08-06
- Commit: `592b65b12beb821f465b2f9b52d8c240d77f4fb8`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.47.6>

> ### Nine English buttons on the resuscitation screen
>
> QRME widened the untranslated-screens rule this round, and it ports here in the same round because these three files are one guard copied twice. Compose has no `Button(text)`: a button on this shell is a `Box` with a `Text` inside it, called by name — `SmallAction`, `BrandButton`, `RobotAction`, `labeledField`, `medRow`, `ratingRow`, `sliderRow` — and the Kotlin pattern list was `Text(` and nothing else.
>
> `RobotAction` is the **resuscitation surface**. *Start CPR (pre-authorized)*, *Confirm: unresponsive, not breathing*, *Auto-resuscitate*, *Coach CPR*, *Fetch AED*, *Meet EMS*, *Stop CPR*, *Perform CPR…* — nine buttons, in English, on the screen this guard's own opening section names as the case where English is a hazard rather than a discourtesy. Beside them, `medRow` labels the age, conditions and resting heart rate a responder reads off the same screen.
>
>     asked     does the string start a `Text(`
>     mattered  does the string end up inside one
>
> Every one of those rows already existed. `fa.start`, `fa.stop`, `fa.aed`, `fa.coach`, `fa.ems`, `fa.perform` and `res.auto` have been in the iOS table since the crisis round — only the shell asking for them was missing.
>
> ### The welcome screen, again
>
> `WelcomeScreen` opened `language` at `"en"` and localized itself from it, so the accountless screen greeted every reader on earth in English until they found the picker. PDI had exactly this at 0.47.5, and this repo's own `L10n` has carried `deviceLanguage()` for it since it was written. The picker now starts where the device is.
>
> **46 call sites wired, 32 rows added, 12 copied from the iOS table.** Android 48 to 46.
>
> Cut together with QRME and PDI at app-v0.47.6.

## app-v0.47.5 — JIM-mini app-v0.47.5

- Published: 2026-08-06
- Commit: `f29a10ef2969f1090a04459e163b3a431c9271eb`
- Assets: 0
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.47.5>

> ### The guard this repo wrote, in the other two
>
> `test_a_shell_asks_for_a_key_it_has.py` was written here at 0.44.x, after
> three native screens shipped asking `L10n` for rows that had been added to the
> console's table and to none of the three native ones. It has been running here
> ever since, and in neither sibling — both of which carry the same three tables
> and the same risk.
>
> Ported to QRME and PDI this round. It found the defect it exists for
> immediately in QRME: three Android screen headings asked for `tab.compose`,
> `tab.posts` and `tab.robots`, and that table held none of them, so those
> screens were titled with their own key names in every language.
>
> No JIM code changed. The finding is that a guard sitting in one product for
> several releases is a guard the other two are owed, and it took thirty rounds
> to go and check.
>
> Cut together with QRME and PDI at app-v0.47.5.

## app-v0.47.4 — JIM-mini app-v0.47.4

- Published: 2026-08-06
- Commit: `5bdea267b42c5ae2d1353e247c71218cab883b74`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.47.4>

> ### The first screen, in the reader's language
>
> Overview is what a person sees after signing in: the greeting, the language
> they will be spoken to in, the model that will do the speaking, what the
> Guardian has learned about them, and whether they are enrolled under their own
> name or a pseudonym. All of it was English on all three shells.
>
> ### The strips that showed the API its own enum members
>
> The tab strips on Care, Life and Safety were the shape found in ConnectView at
> 0.47.2 and written down then as belonging to the round that takes those
> screens. This is that round. English lived in a `case` clause of
> `enum Tab: String`, where no `Text("…")` pattern looks — so the ratchet
> counted zero and the strip read *Goals · Habits · Journal* in every language.
>
> The feedback picker was the same defect one layer down: its five choices were
> the API's own values (`idea`, `improvement`, `bug`, `praise`, `other`) with a
> capital letter put on the front.
>
>     asked     is the wording on the screen in the table
>     mattered  is the wording anywhere a pattern can reach
>
> ### Three names for one screen
>
> The empty-baseline line tells a reader where the samples come from, and named
> that screen *Monitor* on the phones and *Live Monitoring* on the desktop —
> while the nav item itself says **Live Monitoring**. So the first fix was
> wrong too: settling on *Monitor* would have sent a reader to a tab with a
> different name on it. The row now takes the screen's name from `tab.monitor`
> through a hole, and the two cannot drift again.
>
> The Life strip had the same disease: *Shop* and *Circle* on the phones where
> the backend's own `shop_labels` and `circle_labels` say **Shops** and **Your
> circle**, which the desktop has been rendering all along.
>
> **229 → 150.** iOS 70 → 45, Android 75 → 48, Windows 84 → 57.
>
> Cut together with QRME and PDI at app-v0.47.4.

## app-v0.47.3 — JIM-mini app-v0.47.3

- Published: 2026-08-06
- Commit: `93f83892c60e70b4a01843eb7a290b037e42b38c`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.47.3>

> ### A checker that invents work, for the fourth time
>
> `clientpaths.py` finds a client's requests by looking for the call shapes it
> knows and reading the path out of the arguments. A client is free to write a
> shape nobody taught it, and then the audit reports a working door as missing.
>
> That has now happened four times, and the file records all four: the nested
> template literal, the `<img src>` with no callee, the `reqText` sibling of
> `req`, and Android's direct-connection form. Every one was found the same way
> — somebody went to build a door and found the door already there.
>
>     asked     does the extractor understand the calls it knows about
>     mattered  does the extractor know about all the calls
>
> Every guard-on-guard already in that file checks the first question. This
> round adds one for the second: **every path-shaped literal is either inside a
> call form's arguments, or it is recorded with the reason it is not a request.**
>
> It found `getArray("/goals/$uid", token)` immediately — a private helper in
> this shell's Android client that opens its own connection, so the path sits at
> the caller where no known opener encloses it. Six routes with working Android
> doors had been sitting in `android_doorless.txt`.
>
> Worth being precise about why nothing caught it earlier, because it is the
> reason the new check is positional rather than set-based: those paths were not
> invisible. Each was attributed under its **write** verb, from the
> `request(path, "POST", …)` a few lines away. Only the GET was missing, and a
> check comparing the paths a client mentions against the paths it calls reads
> that as covered.
>
> ### The link a guardian could begin and not end
>
> `DELETE /guardians/{guardian_id}/children/{child_id}` was honestly recorded as
> doorless on Android and Windows — no measurement bug, just a missing control
> on two shells out of three.
>
> A guardian link is a standing relationship: one adult able to see another
> person's events, light and escalations. It outlives the reason for it —
> children grow up, custody changes, households end. iOS has been able to end
> one since the link was built. On a phone that is not an iPhone, and on the
> desktop, the person who set it up had nowhere to undo it.
>
> Both shells now have the control, the confirmation, and the sentence saying
> what unlinking does **not** delete: their account, their guardian and their
> own record stay theirs. The six rows come back to those two tables, lifted
> from the iOS wording rather than retyped.
>
> **Android 147 → 140, Windows 141 → 140.** Six of the seven were never missing.
>
> Cut together with QRME and PDI at app-v0.47.3.

## app-v0.47.2 — JIM-mini app-v0.47.2

- Published: 2026-08-06
- Commit: `b00c937498f50cd9d56af660f4ecdaf347a2d837`
- Assets: 0
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.47.2>

> ### The sign-out fix nobody carried across
>
> QRME found this exact bug two releases ago and fixed it in its own copy of
> this file: the Windows shell's **Sign out** sits in `NavigationView.PaneFooter`
> and the loop that localizes the nav walks `Nav.MenuItems`, which the footer is
> not one of. It said *Sign out* in every language.
>
> Android has been asking for `action.sign_out` all along. Windows was not, and
> its table did not even hold the row — so wiring the call was not enough on its
> own. Both are fixed.
>
>     asked     is the nav localized
>     mattered  is every control in the nav localized
>
> ### Family, on all three shells at once
>
> Family is where a parent enrols a child, chooses how much of that child's
> record they get to see, and reads the sentence saying **the auto-defib waiver
> can never be signed for a minor**. That sentence was English on every shell.
>
> So were the oversight tiers, the device controls, the pause-and-quiet-hours
> paragraph promising that monitoring and crisis escalation never pause, the
> unlink confirmation, and the line saying an unlinked child keeps their own
> account and their own record.
>
> The scope on the card confirming a new child's account was worse than English
> on two of the three: Android and Windows printed the API's own enum member,
> `full` and `alerts_only`, raw, on a parent's screen. So did the sensitivity —
> which iOS and Android were also rendering by capitalizing the wire value on
> the Safety dial, three rounds after Windows started asking the table for those
> same three words.
>
> ### Connect, and three promises no measurement could see
>
> Connect is the door out to QRME's community rather than a second copy of it,
> and the three promises that make that true — *Mirror the conversation here*,
> *Post on your behalf*, *Share your health data* — were arguments to a helper
> rather than the first thing inside a `Text(`, so no ratchet on any shell could
> ever have counted them.
>
> The tab strip above them was the other shape: on iOS the English lived in an
> enum's raw values, in a `case` clause, where nothing looks.
>
> **386 → 229.** iOS 113 → 70, Android 113 → 75, Windows 136 → 84.
>
> ### Every key named where a guard can see it
>
> Four shapes of key were quietly invisible to the dead-key guard, and all four
> are the dangerous direction — a guard that calls a live row dead is what
> invites somebody to delete a row a screen is using:
>
> * a key assembled at runtime (`"cw." + level`);
> * a key chosen by a `switch`/`when` and handed to one lookup;
> * a key chosen by a ternary whose condition contains a quote;
> * a key passed to a helper as a bare literal.
>
> Each branch now resolves on its own line, and the helpers take the finished
> sentence rather than the key.
>
> ### Still open, and named
>
> Windows and Android have no way to end a guardian link; only iOS does. Three
> more pickers render an enum's raw values, on Care, Life and Safety. Both
> belong to the rounds that take those screens.
>
> Cut together with QRME and PDI at app-v0.47.2.

## app-v0.47.1 — JIM-mini app-v0.47.1

- Published: 2026-08-06
- Commit: `c05fae820bf1b6f02b2096b8242e11fcf34a5737`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.47.1>

> ### The alarm was localized where it speaks, not where you start it
>
> The guard in this repo is the sibling's guard, copied. So the blind spot
> found in 0.47.0 was here too: a string chosen by a ternary is not at the
> start of an argument list, and nothing was looking anywhere else. The
> recorded counts were understating by **40**.
>
> What that hid is the part worth writing down.
>
> Fourteen `alarm.*` rows were carved out in an earlier round, by name rather
> than by count, because — in that round's own words — *a count cannot tell you
> which string a person could not read*. They cover what the alarm **says**
> once it is going: the question it asks, the three answers, the line admitting
> this screen cannot call an ambulance.
>
> They do not cover **Tap for emergency**. Or **Arm the crash watch**, or
> **Issue Medical ID**, or **Rotate QR** — the controls that arm the alarm,
> fire it, and stand it down. The carve-out was chosen by reading the count,
> and the count could not see the button.
>
>     asked     is the alarm's own wording localized
>     mattered  is the control that starts it
>
> ### The whole safety surface, on all three shells
>
> The SOS control and what it asks. The crash-watch dial, its sensitivity
> floors, its trusted person. The **autonomous-resuscitation waiver** — the
> consent that lets a machine start compressions and fire a fully-automatic AED
> without an on-scene confirmation — and the sentence describing what signing
> it means. The responder card a stranger reads off a locked phone. First aid,
> including **📞 Call emergency services now**. The monitor, and the custody
> proof with its hash-chain verdict.
>
> **538 → 386.** iOS 183 → 128, Android 153 → 122, Windows 202 → 136.
>
> ### Two wordings and a missing card
>
> The SOS button read *Tap for emergency* on the phones and *Click for
> emergency* on the desktop. The escalation-floor sentence said *Crisis
> language and critical events have floors* on two shells and dropped the word
> *language* on the third.
>
> And the failure-report card — settled in the sibling product at 0.46.6, three
> shells saying one thing about what a crash report contains — was still
> English on all three of JIM's. Its ten rows are taken verbatim from the
> sibling's table rather than written a second time.
>
> Cut together with QRME and PDI at app-v0.47.1.

## app-v0.47.0 — JIM-mini app-v0.47.0

- Published: 2026-08-06
- Commit: `390e7b431b77dcf8d27b74441fab79b8a865bdfe`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.47.0>

> ### Version alignment
>
> The three products are cut together, so one number names one combination of
> all three. No JIM code changed. QRME found that its native-shell
> measurement could not see a string chosen by a ternary — `cond ? "Verifies" :
> "Does not verify"` was invisible on every shell — corrected the count from 68
> to 125, and then ran it to 7, none of which contains English.

## app-v0.46.9 — JIM-mini app-v0.46.9

- Published: 2026-08-06
- Commit: `97ef9e40c236832e48faa95c2fc193d534a0acfc`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.46.9>

> ### Version alignment
>
> The three products are cut together, so one number names one combination of
> all three. No JIM code changed. QRME localized the six screens that exist
> on all three of its shells — 212 English strings behind the tab bars down to
> 68 — and fixed a sign-out button on Windows that read "Sign out" in every
> language because it sat outside the loop that localizes the navigation.

## app-v0.46.8 — JIM-mini app-v0.46.8

- Published: 2026-08-06
- Commit: `22c448d95c74d767cfb1cf5b9168392714e5dafa`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.46.8>

> ### Version alignment
>
> The three products are cut together, so one number names one combination of
> all three. No JIM code changed. QRME finished the console that runs a
> profile's public reach on all three shells — 368 English strings behind the
> tab bars down to 212 — and replaced a US-only crisis number, shown in ten
> languages, with the local-services wording this product settled on first.

## app-v0.46.7 — JIM-mini app-v0.46.7

- Published: 2026-08-06
- Commit: `16fd54e6db327ed39165cc2a486eee3ca5a27799`
- Assets: 0
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.46.7>

> ## Version alignment
>
> The three products are cut together, so one number names one combination of all three. No JIM code changed.
>
> QRME localized Signatures and Voice on all three shells — **470 English strings behind the tab bars down to 368** — and closed a gap where two cards had been done on two shells and missed on the third, at the cost of no new rows at all.

## app-v0.46.6 — JIM-mini app-v0.46.6

- Published: 2026-08-05
- Commit: `48e8983b87bed73b107dad3de39afcc068dc8f1f`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.46.6>

> ### Version alignment
>
> The three products are cut together, so one number names one combination of
> all three. No JIM code changed. QRME finished its settings screen and did
> Community on all three shells — 590 English strings behind the tab bars down
> to 470 — and fixed a relationship picker that had been rendering the API's
> enum members as if they were words.

## app-v0.46.5 — JIM-mini app-v0.46.5

- Published: 2026-08-05
- Commit: `e48c9899043b38b0195113afda596f38f18b8b0b`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.46.5>

> ### Version alignment
>
> The three products are cut together, so one number names one combination of
> all three. No JIM code changed. QRME's round was its phones: the first
> screen and the settings screen localized on iOS, Android and Windows — 703
> English strings behind the tab bars down to 590 — and its Android shell,
> which turned out not to compile, fixed and guarded.

## app-v0.46.4 — JIM-mini app-v0.46.4

- Published: 2026-08-05
- Commit: `7e6236bdeb15116e3e5a4da879bc87bc2b44caa4`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.46.4>

> ### The voice picker had a label and the refusal did not use it
>
> Settings has had `<label>{tr("set.voice", lang)}` over the voice picker
> since the picker existed — **Voice**, *Voz*, *Stimme*, 音声 — and a 422 on
> that field answered `voice_id`. The label is ported into `_FIELD_LABELS`
> word for word rather than translated a second time, which is the same
> reason the table is server-side at all: two wordings of one word is two
> things to keep right, and the drift shows up first in the language nobody
> here reads.
>
> The record: 100 → 99.
>
> Cut together with QRME and PDI at app-v0.46.4.

## app-v0.46.3 — JIM-mini app-v0.46.3

- Published: 2026-08-05
- Commit: `45db7111678e3fbfb863a721c23195e0b44d0872`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.46.3>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No JIM code changed. QRME's console-untranslated
> record reached its floor this round: 25 → 1, the last three screens
> translated and one row kept on purpose. JIM's own reached zero at
> 0.45.1.

## app-v0.46.2 — JIM-mini app-v0.46.2

- Published: 2026-08-05
- Commit: `63116fd2e66b0043326a981bc43b362995a57a6a`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.46.2>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No JIM code changed. QRME took four more
> screens off its console record this round: 69 → 25.

## app-v0.46.1 — JIM-mini app-v0.46.1

- Published: 2026-08-05
- Commit: `50d0c415355743bf17453770ccd3abb9a6cbe372`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.46.1>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No JIM code changed. QRME took three more
> screens off its console record this round: 116 → 69.

## app-v0.46.0 — JIM-mini app-v0.46.0

- Published: 2026-08-05
- Commit: `fbac987ea27b5c94086d8e9c0bc5ae33a05d4660`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.46.0>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No JIM code changed. QRME took three more
> screens off its console record this round: 180 → 116.

## app-v0.45.9 — JIM-mini app-v0.45.9

- Published: 2026-08-05
- Commit: `c788eade4626fd8e8f3c0c8ec3d2b39f961ac589`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.45.9>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No JIM code changed. QRME took three more
> screens off its console record this round: 254 → 180.

## app-v0.45.8 — JIM-mini app-v0.45.8

- Published: 2026-08-05
- Commit: `adadcd4e6c7df06b361bdd7f3cd963b352395353`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.45.8>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No JIM code changed. QRME took three more
> screens off its console record this round — 338 → 254 — and widened its
> table-completeness check from the sidebar to all 1519 rows.

## app-v0.45.7 — JIM-mini app-v0.45.7

- Published: 2026-08-05
- Commit: `025f07ca2d9b637f356f28e276ea7ffc0067e15e`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.45.7>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No JIM code changed. QRME took three more
> screens off its console record this round: 425 → 338.

## app-v0.45.6 — JIM-mini app-v0.45.6

- Published: 2026-08-05
- Commit: `77b1cb3b0cbc7433373dbaf36470b034e81dba6c`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.45.6>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No JIM code changed — its own console record
> sits at its floor of zero. QRME took three more screens off its record
> this round: 516 → 425.

## app-v0.45.5 — JIM-mini app-v0.45.5

- Published: 2026-08-05
- Commit: `71ed0953fed9773c58782fcee4c800a733d44297`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.45.5>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No JIM code changed — its own console record
> sits at its floor of zero. QRME took three more screens off its record
> this round: 616 → 516.

## app-v0.45.4 — JIM-mini app-v0.45.4

- Published: 2026-08-05
- Commit: `6ba959535a815bfcde218ef61183593fbf7de9e5`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.45.4>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No JIM code changed — its own console record
> sits at its floor of zero. QRME took three more screens off its record
> this round: 724 → 616.

## app-v0.45.3 — JIM-mini app-v0.45.3

- Published: 2026-08-05
- Commit: `f00ffc1160f518fd983fb7366d390e2bcfd4f36c`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.45.3>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No JIM code changed — its own console record
> sits at its floor of zero. QRME took three more screens off its record
> this round: 848 → 724.

## app-v0.45.2 — JIM-mini app-v0.45.2

- Published: 2026-08-05
- Commit: `49e3c3f26f65b4d8d03b8f2adf87292539743c64`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.45.2>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No JIM code changed — this console's own
> record reached zero at 0.45.1 and stays there, held by its floor and
> by `test_no_screen_of_this_console_speaks_only_english`. QRME took its
> three largest remaining screens off its record this round: 978 → 848.

## app-v0.45.1 — JIM-mini app-v0.45.1

- Published: 2026-08-05
- Commit: `e1275ddb71754d4bb04db1b7d19d20cefa90daad`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.45.1>

> ### The console speaks ten languages, all of it
>
> **The console-untranslated record runs to zero.** The nine screens that
> were left — Safety, Aims, Community, Live Monitoring, Overview,
> Check-in, Journal, Coach and the last four strings of the sign-in
> page — are localized end to end: 129 strings become 125 keys in all ten
> languages. Every screen of this console, pre-session and gated alike,
> now reads its words out of the table.
>
> The record file stays, its status changed from `backlog` to `floor` and
> its ceiling set to **0**, because the guard reads it in both
> directions: a single new English string on any screen fails the build.
> A new test, `test_no_screen_of_this_console_speaks_only_english`, pins
> the emptiness the way the doorless records were pinned — the ceiling
> can be raised, but only by somebody who writes the row down and does it
> on purpose in the same commit.
>
> The measurement started at 603 and has been worked down over nine
> rounds: 603 → 573 → 531 → 481 → 426 → 373 → 262 → 206 → 129 → **0**.

## app-v0.45.0 — JIM-mini app-v0.45.0

- Published: 2026-08-05
- Commit: `b167ecbc4f4c31584cceb7eb9fa8162b67c375af`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.45.0>

> ### Three screens, and the record falls to 129
>
> **What's held about you** — who holds it, who has read it, and the
> sentence that refuses to let an empty access log mean two opposite
> things — becomes twenty-four `hld.*` keys. **Who you watch** — the
> child who keeps their own account and their own token, the board, and
> the resuscitation waiver that must be read in full before it is
> signed — becomes twenty-one `wrd.*` keys. **Care Team** — the QRME
> organization the Guardian coordinates, where summaries cross and never
> raw readings — becomes twenty-three `ct.*` keys.
>
> Seventy-seven strings, all ten languages. The console-untranslated
> record falls **206 → 129**, exact-sync held.

## app-v0.44.9 — JIM-mini app-v0.44.9

- Published: 2026-08-05
- Commit: `12f5e6d3e8c7f6af118cb51d38e3eacee5cec669`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.44.9>

> ### The cabinet and the guided hour speak the visitor's language
>
> Two screens localized end to end. **Medications** — the day's doses,
> the critical one that went unlogged, the as-needed ceiling JIM will
> refuse to log past, and the promise that your own words are a valid
> name and dose — becomes twenty-eight `med.*` keys. **Wellness** — the
> guided calm that is a protocol rather than a generation, the workout
> shaped to the minutes you have, and the day of meals — becomes
> twenty-five `wel.*` keys. All ten languages. The console-untranslated
> record falls **262 → 206**, exact-sync held.

## app-v0.44.8 — JIM-mini app-v0.44.8

- Published: 2026-08-05
- Commit: `7da0517b51b0a306f17432ef8fff5ebc076e902d`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.44.8>

> ### The Control Center speaks — the largest block on the record
>
> The Settings screen — the backend address, the model key that stays on
> your device, the model picker with its honest warning about which
> model actually answers, the voice, the watch channel and the Wi-Fi
> truth about whether a phone can reach it, the vigil that fires on the
> absence of readings, the mail setup, what JIM has learned about you,
> your name here, what you contribute, and where to look — is localized
> end to end: **111 strings, the largest single block left on either
> console**, become eighty-four `set.*` keys in all ten languages across
> eight panels. The console-untranslated record falls **373 → 262**,
> exact-sync held.

## app-v0.44.7 — JIM-mini app-v0.44.7

- Published: 2026-08-05
- Commit: `971bd90ae5acf4fe5dc3268a8877a5bb616e2d57`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.44.7>

> ### The bearing speaks the visitor's language
>
> The Bearing screen — how JIM speaks, what it was told, what it made of
> that, the guide, the dock in the corner and the suggestion box — is
> localized end to end: fifty-three strings become forty-three `brg.*`
> keys in all ten languages, including the refusal that names What's
> Held as the place to consent a source. The console-untranslated record
> falls **426 → 373**, exact-sync held.

## app-v0.44.6 — JIM-mini app-v0.44.6

- Published: 2026-08-05
- Commit: `751ac60699417f282a248f7dee31ef04e9fd1f0e`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.44.6>

> ### What reaches out speaks the visitor's language
>
> The Reach screen — the robot bound to the household with its honest
> first-aid rating, the care code a stranger can scan, the accounts on
> platforms JIM does not run, the excursion that leaves the host and
> says what it cost, and the watch's drip token — is localized end to
> end: fifty-five strings become forty-five `rch.*` keys in all ten
> languages. The console-untranslated record falls **481 → 426**,
> exact-sync held.

## app-v0.44.5 — JIM-mini app-v0.44.5

- Published: 2026-08-05
- Commit: `ee4cfe02a58e93ce03bd8e6590b50e3496dce7cd`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.44.5>

> ### The baseline speaks the visitor's language
>
> The Baseline screen — your own normal, the bands drawn around it in
> either direction, and the crash watch you program yourself — is
> localized end to end: fifty strings become twenty-six `bas.*` keys in
> all ten languages, the crash-watch explanation and the what-this-is
> paragraph kept whole in every language. The console-untranslated
> record falls **531 → 481**, exact-sync held.

## app-v0.44.4 — JIM-mini app-v0.44.4

- Published: 2026-08-05
- Commit: `e32f5b8402d8cdf75b3688fd80c98772e5eb76ff`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.44.4>

> ### The attending speak the visitor's language
>
> The Attending screen — the specialists JIM can hand a thing to, the
> referrals, the escalation ladder with its floors and its one ceiling,
> the relay, the sittings, the alarm and the Medical ID — is localized
> end to end: forty-two strings become thirty-nine `att.*` keys in all
> ten languages, the emergency-door rule kept as one whole paragraph.
> The console-untranslated record falls **573 → 531**, exact-sync held.

## app-v0.44.3 — JIM-mini app-v0.44.3

- Published: 2026-08-05
- Commit: `e0ccef77591fea4fefad551bcffaa3415b94699b`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.44.3>

> ### The channel speaks the visitor's language
>
> The Channel & camera screen — the microphone that listens and the
> clinical camera that seals photographs of a body into the vault — is
> localized end to end: thirty strings become twenty-nine `ch.*` keys in
> all ten languages, whole sentences with named holes. The
> console-untranslated record falls **603 → 573**, exact-sync held. The
> field-label evidence pass walked the residue against every form and
> found nothing newly typed — the hundred rows stay on the identifier
> fallback with the evidence recorded.

## app-v0.44.2 — JIM-mini app-v0.44.2

- Published: 2026-08-05
- Commit: `fb7721421c5f417757163f543d60ba651bbe99b0`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.44.2>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No JIM-mini code changed — QRME's phones
> gained the last doors: genesis and hybrids, packs, simulations,
> the contribution ledger, proactive reach, licensing and the senses,
> and the per-shell doorless records run to zero. JIM's guardian and shells are untouched.

## app-v0.44.1 — JIM-mini app-v0.44.1

- Published: 2026-08-05
- Commit: `a00e2155568f4d24de3319c2ddf8aaabbf2daa5f`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.44.1>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No JIM-mini code changed — QRME's phones
> gained the sticker, the queue and the stamp: beacons/QR and pairing,
> moderation with message edit and retract, reviews, watermarks, media
> and wearables, 24 routes with doors on iOS, Android and Windows. JIM's guardian and shells are untouched.

## app-v0.44.0 — JIM-mini app-v0.44.0

- Published: 2026-08-05
- Commit: `8a0d4adf9fdac83856644d514203bafbae478d57`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.44.0>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No JIM-mini code changed — QRME's phones
> gained the keys, the till and the lifeline: accounts, money and
> status+help, 24 routes with doors on iOS, Android and Windows. JIM's guardian and shells are untouched.

## app-v0.43.9 — JIM-mini app-v0.43.9

- Published: 2026-08-05
- Commit: `c5aab94bc93e11258caebf0f18d15ee1424fcd52`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.43.9>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No JIM-mini code changed — QRME's phones
> gained the face round: portrait, emblem and badge, page and themes,
> front, surfaces, blend, bodies, dials and the wrist, 24 routes with
> doors on iOS, Android and Windows. JIM's guardian and shells are untouched.

## app-v0.43.8 — JIM-mini app-v0.43.8

- Published: 2026-08-05
- Commit: `7478e8fffd32660042ecbb9227f63e25b181727a`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.43.8>

> ### The watch you actually wear
>
> The drip channel was never Apple-shaped — it is a URL that accepts
> JSON — but the setup card only spoke iPhone, which meant a person with
> a Pixel Watch or a Fitbit stood in front of instructions for a phone
> they do not own. The card now asks what you wear and teaches that:
> `?device=` picks between Apple Watch (the Shortcuts recipe), Wear OS
> (Health Connect plus a phone automation), Fitbit and Garmin, the
> device list ships in the payload so the picker renders from the API
> and a new wearable family is one dict entry, and a wrong device is a
> 422 that names every right one. The seed now reads Fitbit's Takeout
> export alongside Apple's export.xml — resting heart rate and HRV
> summaries fold into the baselines; the continuous heart-rate stream is
> deliberately skipped, because folding a workout into the resting
> baseline is the exact mistake the Apple path's sedentary filter
> exists to prevent (an injection that smuggled it in went red before it
> shipped). Garmin's hint is honest that its export is not parseable
> here yet rather than promising an upload that would be refused.
>
> The devices card gained the radio: an Add-Bluetooth-device button
> that, where the runtime carries Web Bluetooth, opens the chooser,
> performs the GATT handshake, and registers the device under its own
> advertised name with its transport and its paired state recorded — a
> device the radio actually paired is a different fact from a name typed
> into the manual row, and the card says which. The kind set now matches
> what people actually pair: wearable, glasses (Google, Meta), AR/VR
> headset, speaker, phone, stationary (2-D), spatial (3-D), autonomous,
> other — and the picker's long-standing "phone" option, which the
> server used to refuse, is accepted at last. Both cards speak all ten
> languages; the console's untranslated backlog falls 615 → 603.

## app-v0.43.7 — JIM-mini app-v0.43.7

- Published: 2026-08-05
- Commit: `9d67f38ad801296e89da9733b4db5fa63697bb24`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.43.7>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No JIM code changed — QRME's phones gained
> the memory list, the pair's record, source material, the ledger,
> anonymity, verification and the profile's three endings, striking 75
> rows from its per-shell doorless records. JIM's guardian surfaces already reach its phones.

## app-v0.43.6 — JIM-mini app-v0.43.6

- Published: 2026-08-05
- Commit: `ca92a392a5c0263bee5e4a8ea1c4c18cd489c80d`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.43.6>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No JIM code changed — QRME's phones gained
> workflows, delegation, the assistant, tasks under a grant, rated
> placements and specialists, striking 84 rows from its per-shell
> doorless records. JIM's guardian surfaces already reach its phones.

## app-v0.43.5 — JIM-mini app-v0.43.5

- Published: 2026-08-05
- Commit: `6d5847ad339ebefe5235b3d8ae8f38b102082a8c`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.43.5>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No JIM code changed — QRME's phones gained
> signatures, mail settings, rooms, wall screens, memberships, handoffs
> and campaigns, striking 74 rows from its per-shell doorless records.
> JIM's guardian surfaces already reach its phones.

## app-v0.43.4 — JIM-mini app-v0.43.4

- Published: 2026-08-05
- Commit: `87c748a8032cbe2334c0a4d2144c1a4df0ddda53`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.43.4>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No JIM code changed — QRME's phones gained
> the robot body's audit trail, the referral flow, objections, the game
> lobby and the helper dock, striking 75 rows from its per-shell
> doorless records. JIM's guardian surfaces already reach its phones.

## app-v0.43.3 — JIM-mini app-v0.43.3

- Published: 2026-08-05
- Commit: `8e00d26c7e1224dfac6cfafdfc07cafd69dbda11`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.43.3>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No JIM code changed — QRME's phones gained
> the place disclosures, the camera, organizations and the guided tour,
> striking 81 rows from its per-shell doorless records. JIM's own disclosures already reach its phones.

## app-v0.43.2 — JIM-mini app-v0.43.2

- Published: 2026-08-04
- Commit: `a873fe82374026c9ebb2dd11aec268d19099ba2d`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.43.2>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No JIM code changed — QRME's phones gained
> the audience verbs, the watch party and skill grants, striking 84 rows
> from its per-shell doorless records. JIM's phones already carry their guardian's own surfaces.

## app-v0.43.1 — JIM-mini app-v0.43.1

- Published: 2026-08-04
- Commit: `c079e772c8aedb8ce9d1d6513755eafd64367885`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.43.1>

> ### Version alignment
>
> The three products are cut together, so one number names one
> combination of all three. No JIM code changed — QRME gained an inbox
> that tells a person what was done to them; JIM's guardian already
> speaks through its insight ladder, which is this product's own answer
> to the same question.

## app-v0.43.0 — JIM-mini app-v0.43.0

- Published: 2026-08-04
- Commit: `a77a4341472bb677432c09942e7825a0f72cb070`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.43.0>

> ### Version alignment
>
> The three products are cut together, so one number names one combination
> of all three. QRME's phones learned to staff a desk, trade in the market
> and sign an exchange, striking 139 rows from its per-shell doorless
> records.
>
> ### The guard learns to read a Swift verb
>
> QRME's round exposed a rule this repo shares: the iOS route audit read
> only the `request(` helper, so a URL built with `appendingPathComponent`
> and sent through a raw `URLRequest` was invisible to it. This shell has
> exactly one such call — `revokeMedicalCard`, a working door since the
> medical-ID round — and the audit had it listed as work to do.
>
>     asked     does the shell call the transport helper for this route
>     mattered  does the shell fetch this route at all
>
> The rule arrives with its premise: the verb is read from `httpMethod`,
> never assumed, because QRME's first draft assumed GET and its own suite
> falsified that within the hour. `DELETE /medical-id/qr/{user_id}` comes
> off the ios doorless record — a row that was never work at all.

## app-v0.42.9 — JIM-mini app-v0.42.9

- Published: 2026-08-04
- Commit: `904a9ed04c3e5938137c4a1cf1cb11dd90718d1d`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.42.9>

> ### Version alignment
>
> The three products are cut together, so one number names one combination
> of all three. No JIM code changed — QRME's friends list, wall and
> comments gained doors on its iOS, Android and Windows shells, closing
> twenty-seven rows of its per-shell doorless backlog.

## app-v0.42.8 — JIM-mini app-v0.42.8

- Published: 2026-08-04
- Commit: `68f520b1e22a8aeeab8d62675b56b92fa6940c95`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.42.8>

> ### The record said nobody asks; the forms had started asking
>
> The same audit as QRME's, run against this product's record with the
> same evidence rule: a field counts as *asked for* only when a console
> input is literally bound to it. Fifty-four of the 154 recorded fields
> were — the onboarding form's legal name and terms consent, the crash
> watch's trusted contact, the steward channel, the watch bridge's
> thresholds, the wellness planner. All 54 now carry hand-written labels
> in all ten languages, matching QRME's table wherever the two products
> share a field name, which the shared-vocabulary guard now checks in
> both directions for 161 more rows. The 100 rows that remain are the
> record's honest residue: enum members, context-filled ids, and flags.
>
> ### The Guardian gets its lights
>
> QRME's always-on agent-lights widget never had a sibling here — a field
> request closed the gap. `GuardianLights.tsx` pins a watch-face to the
> console's bottom-left corner, built from routes the console already
> opens (open alarms, the vigil, the crash watch), so a glance opens no
> new door. Green is the Guardian watching; amber is it asking for you;
> red is an open alarm or a tripped vigil. Minimizable to a dot, worded
> from the console's own ten-language table, and — the lesson its sibling
> paid for in the same cut — unreachable is a state it shows, not one it
> hides in: a failed first fetch renders an unlit dot that retries on
> press.

## app-v0.42.7 — JIM-mini app-v0.42.7

- Published: 2026-08-04
- Commit: `08b5bf098d071a0785c31a911824a5e6f55f3067`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.42.7>

> ### The circle is yours
>
> QRME's people got messages, switches and a page of their own this round,
> and the person behind a JIM had none of them — the Guardian knew
> everything about them and offered no surface that was simply *theirs*.
>
>     asked     can the Guardian's user reach the people around them
>     mattered  on whose terms
>
> `jim/circle.py`, four parts, one idea — the person decides. **The
> circle**: JIM has no friendship graph, so the consent record is built
> here and kept thin — an invitation is one direction, two directions make
> contacts, and either side deleting theirs ends it for both. **Switches**:
> per user, default on, refusing by naming the switch. **Messages**:
> contacts only, one thread per pair, old words surviving the circle
> ending while new ones need it back — and nothing ever leaves the
> deployment; the module structurally imports no client that could carry a
> message out. **The homepage sandbox**: identical walls to QRME's (hex
> colors, http(s) links, plain text, actual contacts), but never public —
> a signed-in neighbour is the widest audience it has, and only while the
> homepage switch is on.
>
> Eight routes with doors on all four clients — the Community screen's
> Circle card and Circle panels on iOS, Android and Windows — every
> visible string arriving from the view's own `labels` in the reader's
> language.

## app-v0.42.6 — JIM-mini app-v0.42.6

- Published: 2026-08-04
- Commit: `0c70ab78c1d06e2acd5bc32aba7ab7bac8782dbd`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.42.6>

> ### Booked, reminded at the bottom rung, and emailed to yourself alone
>
> The Guardian could watch sleep, money and medication, point at desks and
> shops — and could not hold an appointment.
>
>     asked     can the Guardian point at where help is
>     mattered  can it hold the time you agreed to go
>
> `jim/schedule.py` on three rules: **a booking is a row, not a hostage** —
> one press books, one press cancels, and booking a shop *service* is one
> act (the order rides through `jim/shopping.py` under all four of its
> rules; cancelling the booking hands a still-`placed` order back).
> **Reminders ride the proactive ladder at its bottom rung** — a `checkin`
> guardian event plus an insight, once per appointment, raised by the
> monitor/observe senses with no scheduler to deploy; however missed, a
> haircut does not ring a phone. **Email goes to the user, or nowhere** —
> the recipient is looked up from the verified account, never passed in,
> so no request shape mails a third party.
>
> Three routes with doors on all four clients in this cut — the Home
> screen's Schedule card and Schedule panels on iOS, Android and Windows —
> and the 0.42.5 promise is paid: the shopping routes gained their native
> doors on all three shells too, their doorless rows struck.

## app-v0.42.5 — JIM-mini app-v0.42.5

- Published: 2026-08-04
- Commit: `28d20e54e14361b504131c485e8a519e7952c65e`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.42.5>

> ### Shopping through the tandem, on the buyer's terms
>
> QRME grew shops; JIM grew the buyer's side, deliberately thin, on four
> rules driven by `jim/tests/test_shopping_through_the_tandem.py`: browsing
> is anonymous (an unreachable tandem is an empty shelf, never an error);
> ordering is the *interactor's* act — signed with the same per-user token
> the tandem chat runs on, one identity to revoke; the history is held HERE —
> receipts live in JIM's own table, and a test proves the negative that no
> request ever asks QRME for the buyer's order list; and the shelf carries
> its own labels in the reader's language. Three routes with a console door
> on the Community screen; the three shells record them honestly for the
> queued booking-and-ordering native round.

## app-v0.42.4 — JIM-mini app-v0.42.4

- Published: 2026-08-04
- Commit: `d336bac72602a435d3e7b3e2288fce5bcb28e7cf`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.42.4>

> ### The money guardian reaches the phones
>
> 0.42.2 built the guardian and its five routes; the round's own honesty
> recorded all five as doorless on every native shell. That was the record
> working as intended — and a money guardian a person can only reach from a
> desktop is a guardian that misses them at the grocery store.
>
>     asked     is the doorless record accurate
>     mattered  does the phone in their pocket have the door
>
> All five routes now have real doors on iOS, Android and Windows: a Money
> panel in each shell's Life surface with account registration (number
> fields to the vault or refused, the server's refusal shown verbatim),
> balance observations with warnings and their doors, the savings goal, and
> the mandate — written with scope and caps, revoked by a button that is
> never gated. Every visible string is the overview's own `labels`,
> composed server-side in the reader's language, so the English count
> behind the tabs did not move. Each shell's doorless record shrinks by
> five, and the shared error path now surfaces a 402's structured message.

## app-v0.42.3 — JIM-mini app-v0.42.3

- Published: 2026-08-04
- Commit: `dd191a8f479e15f248d99b71949ab13104af5fe8`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.42.3>

> ### The last thirteen unaudited screens
>
> Six components had sat `unaudited` in `ui_screens.txt` since the manifest
> was seeded. Reading each component's own heading against the gallery's
> titles resolved four as merely unlabelled — `Meds` draws **85**, `PaceCue`
> is the pace circle of **14**, `Onboarding`'s sign-in flow is **40** and
> **42**, and `ProviderTiles` is the tile picker of **83**, not 20, which
> draws the *human* providers — and confirmed two had never been drawn.
>
>     asked     is every component accounted for in the manifest
>     mattered  does every component have a drawing
>
> **102 Safety** is the answering end of the crash watch — screen 88 showed
> the watch asking and nothing showed a person accepting, clearing or
> escalating the alarm. **103 Wellness** draws the three deterministic
> generators (calm, workout, meals). Both ceilings now read zero and the
> slack test keeps them there.

## app-v0.42.2 — JIM-mini app-v0.42.2

- Published: 2026-08-04
- Commit: `d1c3d86b21d37b0a2e1dac7bd2a678c07f1043e5`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.42.2>

> ### The Guardian watched spending and could not hold the money
>
> ### The finding
>
> JIM already watched money the way it watches sleep: consented spending
> events fill budget tallies, `life._budget_insights` warns at 80% and 100%
> of a plan, `forecast_spending` projects the month, and the finance coach
> hands a question to Marcus Bell through the tandem. But there was nowhere
> to put an *account* — checking, savings, brokerage, crypto — so there was
> no balance to watch, no cushion to warn about, no savings goal to coach
> toward, and nothing to invest.
>
>     asked     is spending watched
>     mattered  is the money watched
>
> ### What shipped — `jim/money.py`, on four rules
>
>   * **Credentials only ever live in the vault.** Account numbers, routing
>     numbers and exchange API keys are sealed in the PDI tandem; JIM keeps
>     only the institution, the kind, a label and the last four digits. On a
>     plan with no vault the registration is refused — storing a routing
>     number in the clear is not a degraded mode.
>   * **Warnings ride the existing proactive ladder.** A low balance is a
>     guardian event at `checkin` severity and an insight, in the user's own
>     language, exactly like a drift band. Money never reaches the emergency
>     escalation: an overdraft is not a collapse.
>   * **The mandate is a handover, not a default.** "Let JIM invest for me"
>     requires it written down — enabled, a per-order cap, a monthly cap,
>     asset classes, and a scope in words. Enabling is Pro-gated; revoking is
>     never gated, because taking your hands back must not have a price.
>     Every order JIM proposes is logged, and the record says `proposed`:
>     nothing executes without a brokerage connector, and no execution is
>     pretended.
>   * **A warning carries its doors.** The finance coach, the tandem
>     specialist, and real people at desks — near the user's locality or
>     across the map — ride on the warning that makes them relevant.
>
> Five routes; the console's Money card renders entirely server-provided
> labels in the reader's ten languages, so the console's English ratchet
> gained nothing. The phones record the routes on their doorless backlogs.
>
> `docs/proactive.md` now names every proactive path in one place — senses,
> interpreters, actions in escalation order, and the three lines that keep
> proactive from meaning creepy.
>
> ### Checks
>
> `jim/tests/test_the_money_guardian.py`, 17 tests. Driven three ways:
> removing the vault refusal stores a routing number in the clear and the
> test says so; raising money past `checkin` severity fails the hard line;
> ignoring the monthly cap proposes 2000 against a 1000 mandate.

## app-v0.42.1 — JIM-mini app-v0.42.1

- Published: 2026-08-04
- Commit: `5735fe66ac6466afab8a30ff9dc775e50c652df5`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.42.1>

> ### Version alignment
>
> The three products are cut together, so one number names one combination of
> all three. No JIM-mini code changed in this round: QRME's 34 starters — the
> specialists JIM's coach and guardian hand off to through the tandem — each
> gained a dossier of expertise, services, skill chips and a real colleague
> graph, so a specialist reached from JIM can answer for its own trade.

## app-v0.42.0 — JIM-mini app-v0.42.0

- Published: 2026-08-04
- Commit: `3a630ee7d7003e9ab28757d9a1dc7be4d4a08f78`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.42.0>

> ### The device's confession was stripped at the door
>
> ### The finding
>
> `jim/signal.py` grades every biometric sample and folds in the one piece of
> evidence better than any range check — the device's own report of how well
> it read. The fold is multiplicative on purpose: a wearable saying "poor
> contact" can only ever lower trust.
>
> None of that could happen. `BiometricSample` did not declare
> `signal_quality`, so pydantic silently dropped the field at
> `POST /monitor/{id}` and the grader received every sample with the
> confession removed. An SpO2 of 62 read through a flapping strap graded `ok`
> at confidence 1.0 — full trust in exactly the reading the device itself had
> disowned. Found by driving, not reading: the module was correct, its unit
> tests passed, and the door undid it.
>
>     asked     is the sample graded
>     mattered  can the device's own confession reach the grader
>
> `signal_quality` is now declared (bounded 0..1 at the door, so a device
> reporting 7 is an input error rather than a silent clamp), and
> `jim/tests/test_the_device_confession_reaches_the_grader.py` drives the
> defect's exact shape: poor contact caps confidence, a confident device
> changes nothing, and no confession can make a heart rate of zero true.
>
> ### Also
>
> The Settings contribution card said what would be shared; it now *shows* it
> — `preview_next`, the exact payload, rendered verbatim from the same
> function that sends. Nothing queued is said in words rather than shown as an
> empty box.

## app-v0.41.0 — JIM-mini app-v0.41.0

- Published: 2026-08-02
- Commit: `aaa0cefe83378dc33095128ea0347c8064f9155e`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.41.0>

> ### The workflow round-trips and nothing walked the whole arc
>
> ### The finding
>
> JIM's four specialist-task routes — start, list, read, advance — hand a
> multi-phase goal to a QRME synthetic profile and keep the status of it without
> ever holding the working drafts. Each had unit coverage against a stubbed
> tandem. What nothing did was walk the arc against a *real* QRME: the
> cross-product smoke check seeded all three products, wired the tandems, drove a
> single exchange and proved its custody through the vault, then stopped.
> `start_workflow`, `advance` and `specialist_tasks` were never called across the
> boundary at all.
>
>     asked     does the workflow round-trip
>     mattered  does anything walk the whole arc
>
> ### What driving it found
>
> Two behaviours nothing had met end to end, both of them JIM's:
>
>   * **Delegated work is Pro-gated** (`synthetic_agents`). The first
>     `POST /users/{id}/specialist-tasks` came back `402` naming the tier. The
>     exchange the smoke check already drove needs only the vault, which Basic
>     has — so the run had never touched that gate.
>   * **`handoff.available` reads "no" from a specialist whose owner has not
>     opted in**, and the refusal now has to happen before the opt-in for the run
>     to continue. A stranger cannot put a synthetic profile to work uninvited,
>     and that is now proven by asking rather than asserted in a docstring.
>
> The arc walks `research → draft → send` and stops at `confirm` with `awaiting`
> naming what it waits for. `handoff._shape` returns the phases done and the
> profile that did them; the drafts stay in QRME, which is the whole point of
> keeping status only.
>
> ### This release
>
> Version alignment: the three products are cut together, so one number names one
> combination of all three. The arc itself lives in QRME's `suite/smoke.py`; what
> changed here is that JIM's delegation surface is now driven by it end to end
> rather than only against a stub.

## app-v0.40.9 — JIM-mini app-v0.40.9

- Published: 2026-08-02
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.40.9>

> ### The README said v0.18.0
>
> ### The finding
>
> The first bold line of every README in all three products read:
>
>     **Current release: v0.18.0**
>
> and the line directly beneath it said the three are *"versioned and cut
> together, so one number names one combination of all three"* — a convention the
> banner had stopped following at 0.18.0 and kept advertising for twenty-two
> releases.
>
> The release-history table underneath stopped at **0.30.6**. Seventeen shipped
> releases — 0.25.0 through 0.29.0, 0.30.7 to 0.30.9, and the whole 0.40.x line —
> were in `CHANGELOG.md` and absent from the page anybody actually reads. The
> changelog was right the entire time; the summary of it in front of the door was
> behind.
>
>     asked     is the release written down
>     mattered  does the front page say what shipped
>
> Reported from the README beside the video, which is the one place this was
> always going to be noticed and the one place no test was looking.
>
> ### Changed
>
> - The banner names `pyproject.toml`'s version; the table carries every release
>   from 0.25.0 on, backfilled from each product's own changelog.
> - `test_the_readme_says_what_shipped.py` — five tests, the same file in all
>   three: the banner matches the version, every release has a row, the newest
>   row is this release, no row names a release that was never cut, and a guard
>   on the scan itself.
>
> Two injections, both reproducing the reported defect exactly: the banner set
> back to v0.18.0, and the table truncated at 0.30.6 again.

## app-v0.40.7 — JIM-mini app-v0.40.7

- Published: 2026-08-02
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.40.7>

> ### The record that outlived the code
>
> ### The finding
>
> `public_untranslated.txt` opened with a paragraph explaining that
> `Onboarding.tsx` — the screen every person in the world meets first — carried
> forty-odd English strings, that translating them was "its own round", and that
> a half-translated sign-up form would be worse than an English one. All of that
> was true when it was written.
>
> `The screen everybody meets first` translated them. `The pre-session backlog
> reaches its floor` took the count to four and appended its correction *below*
> the stale paragraph, which nobody struck:
>
>     What is left is not prose. A product name, a punctuation mark, an
>     example address and an example code — strings that are the same in
>     every language. This is the floor, not a backlog.
>
> So the file held two statements about itself with the false one first. Read
> top-down — which is how anybody reads a file — it advertised a cleared backlog,
> and the correction was twenty lines further on. This round was planned off that
> paragraph before the extractor was run and the work turned out to be two
> releases old.
>
>     asked     is the record complete
>     mattered  does the record still describe the code
>
> The numbers were right the whole time. The prose around them had outlived the
> thing it described, and a record only works if a reader can trust the first
> thing it says.
>
> ### Every ratchet now leads with what it is
>
> `# status: floor|backlog — N rows`, on the first line, with the count checked
> against the rows beneath it. `floor` means the remainder is permanent and is
> not work; `backlog` means somebody still owes it. The two cannot be told apart
> from the numbers — `console_untranslated` sits exactly at its ceiling with
> 1,459 strings still to translate, and `public_untranslated` sits exactly at its
> ceiling and is finished — which is why the file has to say which it is, in a
> line that cannot drift from its own contents.
>
> A third check was written and struck before it shipped: *a file calling itself
> a floor must sit exactly at its ceiling*. It fired on `native_untranslated.txt`,
> which the last release took from three rows to none — a floor of zero under a
> ceiling of three, and the best kind there is. `floor` is a claim about what the
> remaining rows **are**, not how many, and a check that pretended otherwise
> would have been one more guard answering the question next to the one that
> matters.
>
> ### The reasons move next to the rows
>
> `unused_native_bindings.txt` recorded two bindings whose justification lived in
> the guard's module docstring — true, careful, and one file away from the list
> it explained. A record whose justification is somewhere else reads, at the
> place somebody actually looks, as an unexplained backlog: the shape this audit
> found seven times in `0.40.5`. Every row now carries its reason on the row, and
> a new check refuses one that does not.
>
> ### The dead-key ratchet was reading one shell's share of a total
>
> `native_dead_keys.txt` held four generic action verbs — `action.refresh`,
> `.save`, `.send`, `.translate` — added in advance because a screen would
> obviously need a Save button, translated into ten languages, and asked for by
> no screen in any shell across several releases. Ten rows across three shells.
>
> Its ratchet took the **maximum over the shells**, so the number of dead rows
> could have risen — iOS three to four, a fourth shell arriving with four of its
> own — while the check passed every time, because no single shell crossed the
> line. The file's own instruction said "the ceiling does not move up" and meant
> the count of dead rows.
>
>     asked     is any one shell's dead-key count above the line
>     mattered  is the number of dead rows going up
>
> ### Changed
>
> - The four verbs are deleted from all three shells; the record is at **0**. The
>   file's own instruction was "wire one or delete one". A screen that needs a
>   Save button adds the row it needs, in the wording it needs.
> - `# total:` ratchets the sum alongside the per-shell `# ceiling:`.
> - `test_a_record_that_outlived_the_code.py` and the binding-reason check, both
>   shared with the sibling products.
>
> Injections: one dead verb put back and recorded — which the old maximum-only
> ratchet passed at 1 ≤ 4 — plus the three record checks.

## app-v0.40.6 — JIM-mini app-v0.40.6

- Published: 2026-08-02
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.40.6>

> ### Cut alongside qrme and pdi
>
> No change in this product. The round finishes localizing QRME's **accountless
> screen** — the one built for somebody who has found a synthetic profile of
> themselves and has no account, and therefore no profile language to take a
> setting from.
>
> This product has no such screen. A Guardian belongs to the living person using it — every surface here is reached by somebody who has an account, and there is no third party for it to speak as.
>
> The shells here already resolve a device language and already send it as
> `accept-language`; what they do not have is a screen whose reader provably has
> no profile. Recorded rather than left silent: a version where all three move
> together and one is untouched should say which one and why.

## app-v0.40.5 — JIM-mini app-v0.40.5

- Published: 2026-08-02
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.40.5>

> ### The account was gone and the wrist kept writing
>
> `life.delete_user_data` opens with *"Erase every trace of a user across all
> tables — and the PDI vault."* It empties the vault, walks eighteen tables and
> removes the `users` row last, and the API answers 404 for that id afterwards.
>
> `watch_channels` was not one of the eighteen. Its `token` is the drip address:
> a URL typed into an Apple Shortcut, sometimes weeks before, that deposits
> readings into one user's stream. Driven end to end:
>
>     DELETE /data/{id}            200  {"events": 1, "baselines": 2, ...}
>     GET    /users/{id}           404  the account is gone
>     POST   /watch/drip/{token}   200  {"received": 1}  ← and an event row is back
>
>     asked     did we delete the user's data
>     mattered  can anything still write more
>
> The reading ran the full Guardian pipeline under an id that no longer resolves,
> so an erased account grew rows again from a credential its owner had no way to
> find and no screen left to rotate. Two other tables in the same shape went with
> it: `contribution_log`, whose `revoked` column is the whole mechanism for
> withdrawing what was shared with the cloud, and `waivers`. Both are standing
> permissions rather than records of something that happened.
>
> The sibling products had the same class in their own idiom, and the same round
> landed in all three: in QRME a terminated profile was still being licensed and
> cloned through the buyer's token, and in PDI a closed vault was still readable
> through a bequest grant.
>
> ### Changed
>
> - `life.delete_user_data` now takes `watch_channels`, `contribution_log` and
>   `waivers` with it.
> - `watch._user_for_token` joins `users`, so a channel row that somehow survives
>   still cannot deposit — the second stop, which closes the class rather than
>   the one path.
> - `jim/tests/test_the_erase_left_a_live_address.py` — eight tests. The
>   generalisation reads the schema rather than a list in the file, so a
>   credential table added next release is in scope by construction.
>
> Thirty user-scoped tables hold ordinary data and are also untouched by a
> function whose first line says "every trace". That is recorded in the new test
> file rather than hidden; it is a decision about what deletion means rather than
> a defect with a receipt, and this round does not take it.

## app-v0.40.3 — JIM-mini app-v0.40.3

- Published: 2026-08-02
- Commit: `a3d34aea5b559ee8e0067ea1daed0ccad1ff86f9`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.40.3>

> ### One wrapper recorded its degrades; its sibling said nothing
>
> `llm.FallbackProvider` is where this rule is written down in this codebase, and
> it is exemplary:
>
> > The degrade is recorded on the instance (`answered_by`, `failure`) so a
> > caller can tell the user the truth about who actually answered — **a log line
> > the user will never read is not disclosure.**
>
> `cloud.CloudProvider` degrades to the same local stub and did none of it: a
> bare `except Exception:`, no record, and — unlike its sibling — not even a log
> line. And `generate_for_user` asked for the truth by naming one class:
>
> ```python
> if isinstance(provider, FallbackProvider):
>     actual, reason = provider.answered_by, provider.failure
> ```
>
> So when the cloud gateway was unreachable, `actual` stayed at the model the
> user had chosen and `degraded` computed to False. The coach's own comment
> beside that field says what that costs:
>
> > a silent degrade to the stub under a screen that says Claude is how a founder
> > demos canned text to their testers without knowing it
>
>     asked     did the fallback provider degrade
>     mattered  did anything degrade
>
> The careful half made the silent half invisible, and nothing exercised the
> cloud path through `generate_for_user` at all.
>
> ### What changed
>
> `CloudProvider` now carries `answered_by`/`failure` in the same idiom as its
> sibling, and the assembly **duck-types on those attributes** instead of naming
> one class — so a third wrapper is covered by construction rather than by
> somebody remembering to add a branch. A structural check enforces it.
>
> ### A test that passed for the wrong reason
>
> The driven half of the new guard first asserted the right values while the
> defect was still in place. The suite pins `JIM_LLM=stub`, so `intended` was
> already `"stub"` and the broken branch — which reports `intended` — produced
> exactly the answer the fixed branch produces. It now pins the intended provider
> to something that is *not* the stub, which is the whole of its discriminating
> power. Re-injected afterwards to prove it fails.

## app-v0.40.2 — JIM-mini app-v0.40.2

- Published: 2026-08-02
- Commit: `e907a9067249c5056940bab0d9c0151a4bd0d505`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.40.2>

> ### The refusals, finished
>
> 0.24.0 translated the eleven refusals any route can raise and **wrote the rest
> down**. 42 sentences sat in `jim/tests/refusals_untranslated.txt` from that day to this — the sentences
> the Guardian says when it says no, still English on an account that had chosen
> otherwise.
>
> Among them the sentences a guardian meets around a minor's care — the waiver
> that can never be signed for a child, the consent a provider does not have.
>
>
>     asked     is the refusal translated
>     mattered  is every refusal translated
>
> All 42 are now in `_REFUSALS`, in the nine languages beside English. The
> record is a decision rather than a backlog for the first time: it is empty.
>
> ### What deliberately stays an identifier
>
> Field names, header names, enum values and environment variables are not
> translated and are not meant to read as words — `audio_base64, qrme_profile_id, x-signup-key, JIM_QRME_URL`. They are the API's own
> names, the same string in every language, and declining them into a sentence is
> the half-in-one-language failure the table exists to refuse.
>
> ### The check that could not have caught a lie
>
> `test_every_translated_refusal_has_every_language` asks whether each row has
> all nine keys. A row whose nine values are the English sentence pasted nine
> times satisfies it exactly — and the table would then claim the refusal is
> handled while every reader still got English.
>
>     asked     does every refusal have every language
>     mattered  does every language say something other than the English
>
> That gap was harmless while eleven rows were added by hand and reviewed one at
> a time. It stops being harmless the moment 42 are added in one release, so
> `test_no_refusal_is_translated_into_english` was added first and injected
> against: an English value in one slot of one row fails it by name.

## app-v0.40.1 — JIM-mini app-v0.40.1

- Published: 2026-08-02
- Commit: `fb52c441c3335f48ff248578eff3ebeb5f499c80`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.40.1>

> ### The language no client was sending
>
> JIM's public surface answers people who have no account yet, and those handlers
> compose real sentences: what was sent, what is held, what to do next. Every one
> of them is chosen from `Accept-Language`.
>
> **No native shell was sending that header.** The browser sends it without being
> asked, which is why the console looked correct and the three clients a person
> is actually holding were the ones answering in English.
>
>     asked     can the shell say it in the reader's language
>     mattered  does the reader's language ever reach the server
>
> Two things were missing, and only the second is obvious once the first is
> written down. There was **no language to send**: each shell's `language` comes
> from the stored account setting and is `"en"` until an account exists.
> `L10n.deviceLanguage` (iOS), `L10n.deviceLanguage()` (Android) and
> `L10n.DeviceLanguage()` (Windows) now read what the device has been carrying
> all along — `Locale.preferredLanguages`, the system configuration's locale
> list, `CurrentUICulture` — drop the region, and fall back to English rather
> than guessing. Then there was **somewhere to send it**: one line in each
> shell's shared request helper.
>
> `test_the_language_nobody_was_sending.py` checks both halves, because a header
> set to a constant is indistinguishable from a correct one from the outside, and
> it checks *every* header line rather than any of them — the sibling product's
> client sets the header in two places and an `any` passed an injection that
> broke one.
>
> ### Windows' localizer takes a language now
>
> `L10n.T(key)` read `AppState.Current.Language` and had no way to be told
> otherwise, so a public surface got the account's default without the screen
> ever naming it. iOS and Android could not make that mistake: both of their `t`
> functions require the language as an argument. A `T(key, lang)` overload closes
> the gap.

## app-v0.40.0 — JIM-mini app-v0.40.0

- Published: 2026-08-02
- Commit: `fb4bfc27a8fc81c484df5a68a647520766b9cc2a`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.40.0>

> > Staged as 0.30.10 and cut as **0.40.0**. The work below is unchanged; only
> > the number moved, from a patch on the 0.30 line to a minor of its own.
>
> ### A specialist could be reached by a sensor and not by a person
>
> `grep -c specialist jim/coach.py` returned **0**.
>
> A QRME specialist was reachable from exactly one place in this product:
> `guardian._deliver`, the monitoring path. Sensors trip, a detection names a
> condition, and if a tandem specialist is registered for it the Guardian
> delegates the guidance.
>
> `coach.reply` — where somebody brings something in their own words, because
> they chose to — had no call, no mention and no comment about specialists at
> all.
>
>     asked     can a specialist be reached
>     mattered  can the person who asks reach one
>
> The person whose watch noticed something got the better answer. The person who
> sat down and typed *"I've been struggling with money and it's keeping me up"*
> got the local model — on a product whose premise is that somebody is looking
> after you, and where bringing a problem yourself is the strongest signal there
> is.
>
> **Nothing bridged them because two vocabularies never met.** `specialists` is
> keyed on **condition**, because its only caller was a detection. `coach.AREAS`
> is seven **life areas**, because its only caller was a person choosing a tab.
> `jim/specialists.py` is that map — declared, not matched: a substring rule
> would have paired *finance* with *financial stress* and left *nutrition*
> silently unpaired while looking like it had worked. An area with no clinical
> domain holds an empty tuple, which is a decision rather than an omission, and
> a guard refuses a new area nobody has decided about.
>
> ### It offers; it does not route
>
> The material is different in kind from what the monitoring path sends. A
> detection sends a **finding** — *"the user shows signs of low mood (resting
> heart rate elevated for 40 minutes)"*. A coach turn would send **what the
> person wrote about their own life**.
>
> Routing that automatically would disclose to a profile outside JIM something
> somebody said to their Guardian, without ever asking them. So `coach.reply`
> returns an offer that says plainly *nothing has been sent*, and the sending
> lives behind `POST /coach/{id}/specialist` — a door the person chooses.
> `handoff.py` set the same rule for the other multi-step path: *a detection can
> warrant a handoff; a person or an operator starts it*.
>
> Never reachable from escalation, and there is a test that fails if it ever is:
> a ladder that waits on a third party is worse than no ladder.
>
> The answer says where it came from — *"answered by a QRME specialist profile
> through the tandem, not by JIM's own model"* — and what crossed: *"the message
> you sent, and nothing else from your record — no check-ins, no conditions, no
> medication"*. Both are checked by name. A reply that reads as the Guardian's
> own when a third party wrote it is the one thing this path must never do.
>
> Doors in the console and on all three shells.
>
> ### A field name that would have broken every phone
>
> The offer ships as `specialist_offer`, not `specialist`. The monitoring path's
> reply already uses `specialist` for the expert's **name**, a string, and all
> three shells decode `Guidance` with `specialist: String?`. An object under that
> key would have thrown at decode time on iOS, Android and Windows — and there is
> no Swift, Kotlin or C# toolchain in this build environment to have said so.
>
> ### Two records were overstating themselves
>
> `console_untranslated.txt` counted **62** rows that were separators rather than
> English: a bare `:`, a `·`, a `%`, a `⚠`. The guard then fired on a card whose
> every sentence had just been localized.
>
>     asked     did the extractor find a string here
>     mattered  did it find a word a reader reads
>
> The same mistake the shells' guard made last release with `"\(dim): \(n)%"`,
> one file over. The ceiling is corrected to 615.
>
> The new specialist cards **are** prose, so the native ratchet fired on them
> correctly and they are hand-translated into ten languages on all three shells
> and the console — the rule this repo keeps rather than adding to a backlog it
> just finished measuring.

## app-v0.30.9 — JIM-mini app-v0.30.9

- Published: 2026-08-02
- Commit: `896270ef3ddadd423ccba0093fccbfdf04762821`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.30.9>

> ### The user-specific model was correct, tested, and never computed
>
> `jim/adaptation.py` implements clause 11 — a profile derived offline from a
> person's own stored history, versioned, confidence-scored, sealed into the
> vault when a tandem is configured. `coach.reply` reads it on every turn through
> `adaptation.prompt_lines`.
>
> `prompt_lines` returns `[]` when there is no row. `rebuild` writes the row. And
> `rebuild` had exactly one caller in the entire product: `POST
> /adaptation/{user}` — a button in the desktop console.
>
>     asked     can a user-specific model be built from the history
>     mattered  does anything ever build it
>
> Nothing called it after a check-in, a coach turn, or an answered follow-up. On
> every user who never pressed that button — which is every user who only ever
> opened the phone app — the artifact had never been computed, and the coach ran
> unadapted forever while the code that would have adapted it sat there correct
> and tested.
>
> The module was not wrong and neither were its tests. What was missing was an
> **edge**, which is exactly the thing no test of either end will notice:
> `adaptation`'s tests build the profile themselves, and `coach`'s tests pass
> whether the profile exists or not, because a coach with no adaptation lines is
> a working coach.
>
> `adaptation.ensure_fresh` now rebuilds from the loop when the history has moved
> on — three COUNTs on the common path, a rebuild only after five new pieces of
> evidence, and it never raises, because a failure to refresh a *derived*
> artifact must not cost somebody the answer they asked for.
>
> ### The latent continuity vector
>
> Even with a rebuild, the profile is a snapshot and nothing moved between
> snapshots. The sibling product carries a per-(profile, interactor) latent
> vector, EMA-updated after every interaction, so cross-session state survives
> logins, devices and model calls. JIM had no equivalent at all — a person could
> check in every day for a month and be met each time exactly as on the first
> day.
>
> `jim/continuity.py` is that vector: six named dimensions — engagement, candor,
> strain, receptiveness, steadiness, continuity — folded in at the three moments
> a signal actually arrives, and rendered into the coach's prompt as **attention
> weighting** rather than as instruction. Identity, boundaries and every safety
> path stay fixed, and the rendered block says so.
>
> Three rules it keeps, each with a test:
>
> * **It carries no content.** Six floats and three counters, derived from
>   tallies. Not a phrase, not a condition name, not a message. This matters
>   more here than in the sibling product because what is being counted is
>   somebody's health.
> * **Confidence is earned.** Silent below six observations — a vector built
>   from two check-ins is a shape in noise, and a Guardian that starts pacing
>   itself around one is worse than one that has not started.
> * **It is not a weight file**, and `state()` says so in its own words rather
>   than letting a reader assume a fine-tune happened.
>
> It is readable and droppable from the console and from all three shells:
> `GET`/`DELETE /continuity/{user}`, a Settings panel, and a card on the
> self-profile screen of iOS, Android and Windows.
>
> ### Two bugs the round's own guards found
>
> **A type-compatible argument swap in the Android client.** The shared helper is
> declared `request(path, method, body, token)`. Three calls in this shell and
> one in PDI's passed `("GET", "/offline/status", …)` — verb first. Both
> arguments are `String`, nothing complained, and the request went to
> `base + "GET"` with the method set to a path. Two of those shipped in 0.30.7's
> offline round.
>
>     asked     does the call have the right number of arguments
>     mattered  does it have them in the right order
>
> There is no Kotlin toolchain in this build environment, which is why it sat
> there. `test_a_screen_nothing_opens.py` now reads the helper's own signature
> and refuses an HTTP verb in the path slot, in all three repos.
>
> **Last release's untranslated counts were overstated.** The extractor counted
> any string literal containing a letter, which counted format fragments like
> `"\(dim): \(n)%"` — whose only letters are variable names nobody reads — as
> English prose. About seventy-five of them across the nine shells.
>
>     asked     does this literal contain letters
>     mattered  does this literal contain words a reader reads
>
> The ratchet caught it by firing on a card that had just been fully localized,
> which is a measurement saying the opposite of the truth. The corrected figures
> are in `native_screens_untranslated.txt`; JIM's shells are at 167 / 139 / 192,
> and the localized share is higher than 0.30.8 claimed.

## app-v0.30.8 — JIM-mini app-v0.30.8

- Published: 2026-08-02
- Commit: `ba43a8a30b8a1757a5fe792b82f30a218e6cfb60`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.30.8>

> ### The tab bar answers in your language. Everything behind it does not.
>
> The QRME repo has carried a guard since the console rounds called
> `test_the_nav_is_translated_and_nothing_behind_it_is.py`. It found forty-six
> translated sidebar labels in front of 1577 English screens, and said plainly
> why that is worse than shipping no translations at all:
>
> > A uniformly English console tells a Spanish reader the truth on the first
> > screen they see. This one puts *Mercado*, *Amigos* and *Ajustes* in the
> > sidebar — the app apparently answering in their language — and then hands
> > them English the moment they click.
>
> Three products ship three native shells each. All nine have a translated tab
> bar. Nobody had ever counted what is behind them.
>
> | product | iOS | Android | Windows |
> |---|---|---|---|
> | QRME | 2.4% | 3.8% | 0.6% |
> | JIM-mini | 13.0% | 14.2% | 9.7% |
> | PDI | 8.9% | 10.2% | 3.5% |
>
>     asked     is the console's nav-vs-behind gap measured
>     mattered  is the phones' too
>
> `native_screens_untranslated.txt` now records it per shell, ratcheted in both
> directions — the count may not rise, and the record may not sit more than
> twenty above the real number, so the ceiling cannot quietly become a place to
> drift back up into.
>
> ### The alarm surface is now hand-translated on all three shells
>
> 1813 strings cannot be honestly translated in one round, and this product's own
> rule forbids the other kind — `jim/i18n.py`: safety text is *"never
> machine-mangled"*. So this release takes the subset where English is a hazard
> rather than a discourtesy, and records the rest.
>
> Fourteen strings, ten languages, iOS and Android and Windows:
>
> * the question the crash watch asks — **"JIM is asking: are you okay?"** — and
>   its answer, on a screen whose entire premise is that silence sends help;
> * the three answers to an open alarm: *I have this — I'm going*, *Nobody can go
>   — escalate*, *It's over — clear it*. One of them decides whether the ladder
>   keeps climbing toward emergency services;
> * **"This is not an emergency service. If it is one, call your local emergency
>   number — this screen cannot."**
>
> A Spanish speaker was shown *Seguridad* on the tab, and then asked in English
> whether they were alright, with three English buttons deciding what happened
> next. The backend has refused in nine languages for several releases and
> promises in all of them that emergency paths are never affected.
>
>     asked     is the chrome localized
>     mattered  is the decision localized
>
> All three shells or none, for the reason `native_untranslated.txt` already
> gave: porting one puts the responder on a localized iPhone and an English
> Android, which is the per-client mistake this audit is named for, made on
> purpose.
>
> ### Two guards on the guard, one of which caught a real miss
>
> Every translated row is now checked for its **slots**. A row whose English says
> `{name} was contacted` and whose Portuguese forgot the hole renders an alarm
> with the person's name missing from the middle of it — the string is present,
> the language is right, and the sentence is wrong. Where a shell's table holds
> no slotted row the check **skips loudly** rather than passing on an empty set.
>
> The first version of the row parser could not read four of the fourteen new
> rows, and reported them missing from tables they were sitting in. Its Kotlin
> pattern ended a row at the first `)` and its C# pattern at the first `}` —
> and the rows that carry brackets are `({concern})` and `(relayed as a request
> — …)`, which is to say the rows carrying slots, which is to say exactly the
> rows the slot check exists for.
>
>     asked     does the row match a pattern for a row
>     mattered  does the row end where the pattern says it does

## app-v0.30.7 — JIM-mini app-v0.30.7

- Published: 2026-08-02
- Commit: `d257dc8fe5b5b25eaf2928b7e40cf5023b162b98`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.30.7>

> ### The screen nothing opens
>
> Last release put the synthetic-self screen on the phones — the one QRME profile
> that *is* this person, where they say what the Guardian may pass on about their
> medication. One screen per shell, each translated into ten languages, and a
> guard written to prove the wording was there.
>
> The wording was there. Nothing else was. `SelfProfileSection` on iOS,
> `SelfProfileScreen` on Android and `SelfProfilePage` on Windows were each
> declared and each unreachable — no tab, no composable call, no navigation case.
>
>     asked     does the screen have its wording
>     mattered  does anything open the screen
>
> All three are now in the navigation: a **Me** tab beside Community on iOS and
> Android, and a **Me** entry in the Windows nav pane.
>
> ### Two of those three would not have compiled
>
> `L10n.t` takes a key **and a language** in Swift and Kotlin. Every one of the
> forty calls on those two screens passed only the key. The Windows shell's
> `L10n.T` takes the key alone and reads the language itself, which is the only
> reason that one was fine — three shells, two spellings of the same function,
> and a screen written against the wrong one twice. There is no Swift or Kotlin
> toolchain in this build environment, which is exactly why it sat there.
>
> `test_a_screen_nothing_opens.py` now asks both questions per shell, and asks
> the arity question against **each shell's own signature** rather than a single
> number for all three. Holding Windows to Swift's two parameters would have been
> the union mistake again, in the guard meant to catch it.
>
> ### Offline mode became readable
>
> `GET /offline/status` reports the posture — whether external transmission is
> possible, what counts as a local destination, what the deployment guarantees.
> It was already answerable and nowhere visible. It now has a panel in the
> console's Settings, a card on the Vault Custody screen of all three shells, and
> its three chrome strings in ten languages.
>
> Read-only on purpose. The posture is set in the deployment's environment, not
> by somebody signed into the app, and a switch there would imply otherwise.

## app-v0.30.6 — JIM-mini app-v0.30.6

- Published: 2026-08-02
- Commit: `d1d8d575e1f8ec05c27e0301d9eb993cb9a7153e`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.30.6>

> ### The plan gate speaks the reader's language
>
> `refusals_untranslated.txt` carried this as an exception for four releases, in
> its own words: a template whose slots were English prose, where translating the
> frame alone would produce *"a sentence half in each language, at the one moment
> in this product that stands between somebody and a decision to pay"*.
>
>     asked     can the frame be translated
>     mattered  can the slots be
>
> They can. The capability descriptions and the billing period are a **closed set
> this product authors**, so they are `i18n.Term`s with translations rather than
> strangers — and `Term` is now exempt from the whitespace rule for exactly that
> reason. The rule catches prose *nobody wrote a translation for*; an unmapped
> `Term` still keeps the whole sentence English, so the exemption is paid for
> rather than a hole.
>
> The **plan titles** stay as they are. `Basic` and `Pro` are what the product is
> called on the pricing page, in the console's tabs and on a receipt, and
> somebody comparing a refusal against a price list needs the same word in both
> places.
>
> `Opening` capitalises **after** translation, never before: the vocabulary holds
> one form of each phrase and each language raises its own first letter from it.
> `str.capitalize()` was wrong here — it lower-cases the rest, which would have
> flattened German's nouns.
>
> **The emergency clause is part of the frame**, not appended to it. A person
> told they cannot have the trend model needs to know the alarm still works, and
> that reassurance arriving in English at the end of a Portuguese sentence is the
> shape this mechanism exists to prevent. A test asserts it survives into all
> nine languages.

## app-v0.30.5 — JIM-mini app-v0.30.5

- Published: 2026-08-01
- Commit: `eecef47cec63f57e89484af8610cdfc656b72621`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.30.5>

> ### The plan gate said HTTP 402
>
> 0.30.4 left the plan gate open as the one refusal deliberately not translated,
> because its message interpolates prose. Going back to translate it turned up
> something else first: on three of the four client families it was not arriving
> at all.
>
> `detail` has three shapes in this product — a **string** for most refusals, a
> **dict** for the plan gate, a **list** for a 422. 0.30.3 gave the list a
> top-level `message` and taught every client to read it. The plan gate's
> `message` stayed nested inside its dict.
>
>     asked     does the sentence ride beside the structure
>     mattered  does every structured refusal put it in the same place
>
> The three native shells look for a top-level `message`, then for a string
> `detail`. A dict is neither, so the one refusal in this product that stands
> between somebody and a decision to pay rendered as the bare status code: no
> price, no plan name, no reason.
>
> | Client | Before | After |
> |---|---|---|
> | iOS | `HTTP 402` | the sentence, with price and plan |
> | Android | `HTTP 402` | the sentence, with price and plan |
> | Windows | `HTTP 402` | the sentence, with price and plan |
> | Console | correct | unchanged |
>
> **One of those was a regression from 0.30.3.** Android had been coercing the
> dict through `toString()` and showing its raw JSON — ugly, but it contained the
> price. Teaching it to read the top-level key first is what dropped it to the
> status code. iOS and Windows had always been broken.
>
> **The fix is not a third special case.** Every refusal now carries a top-level
> `message` holding the sentence a person reads, whichever shape `detail` is, so
> a client never has to know the shape and a structured refusal added later
> cannot repeat this. `detail` is untouched: the console still reads the dict to
> draw the upgrade card with its price and button. `sentence_of` returns nothing
> when there is nothing readable rather than inventing a sentence — a bare status
> is more honest than one this codebase made up, and would be indistinguishable
> from a real one.
>
> **A second defect underneath it.** `localize_detail` looked one level down, and
> `api.py` wraps every `HTTPException` as `{"detail": exc.detail}` before it
> runs — so a structured refusal arrives two levels down and its sentence went
> out **untranslated in every language**.
>
>     asked     is a structured refusal localized
>     mattered  is it localized where the wrapper actually puts it
>
> Found because the new translation check failed rather than passed, which is
> what it was written to do.

## app-v0.30.4 — JIM-mini app-v0.30.4

- Published: 2026-08-01
- Commit: `adcc816de15e8d77cd640835cb36c57016844b66`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.30.4>

> ### A refusal whose English is not a constant
>
> `refusals_untranslated.txt` has carried the same paragraph for three releases:
> f-string refusals, named as uncovered and deliberately not counted in the
> backlog, because
>
>     f"language must be one of {', '.join(SUPPORTED)}"
>
> cannot be looked up by its English source — at the moment it is raised there is
> no English source, only a result.
>
>     asked     is the refusal a constant we can translate
>     mattered  is every part of it something we can translate
>
> `i18n.Templated` is a `str` whose value is the finished English sentence,
> carrying the template and its slots so `localize_detail` can refill the frame
> in the reader's language. Nothing that already treats a detail as text changed
> — the default English path, JSON encoding, and every driven test asserting on a
> refusal message all work exactly as before.
>
> **The slot is the whole design.** A translated frame around an English slot is
> *worse* than an English sentence: it reads as a bug, in front of somebody who
> is already being told no. That is precisely why this record refuses to ship a
> translated plan gate, and doing it here by accident would have been the same
> mistake with a mechanism to spread it. So whitespace means prose, and a slot
> that fails the test keeps the whole refusal English — the state it was already
> in, now chosen rather than stumbled into.
>
> The known limit is stated rather than hidden: a **single** English word has no
> whitespace either, and is indistinguishable from an identifier.
>
> JIM-mini has no refusal that interpolates a closed set, so it carries the
> mechanism without QRME's `Term` marker and vocabulary, and the guard fails if
> that stops being true. **7 sites converted**, 18 remaining.
>
> The extraction read this product's own test file as a raise site, because tests
> live inside the package here and beside it in QRME — caught by the literal-slot
> check firing on its own examples.

## app-v0.30.3 — JIM-mini app-v0.30.3

- Published: 2026-08-01
- Commit: `17a0b41854322bc307abe0798cd60a4798e971ce`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.30.3>

> ### The refusal that arrived as a list
>
> 0.30.1 put the 422 into the reader's language — the refusal a mistyped form
> produces, and the one a person meets most often. Nothing looked at what a
> client does with the result.
>
> `detail` on a 422 is a *list* of pydantic rows, and every client family
> rendered it by a path written for a string. The console called
> `JSON.stringify` on it, so the note under a form read
> `[{"type":"missing","loc":["body","display_name"],"msg":"Field required"}]`.
> Android's `JSONObject.optString` coerces a `JSONArray` through `toString()`,
> producing the same. iOS asked for `as? String`, got `nil`, and fell back to
> `HTTP 422`; Windows called `GetString()` on an array, which throws, was
> caught, and did the same.
>
>     asked     is the refusal translated
>     mattered  is the refusal a sentence
>
> The `msg` translated last release was correct, arrived, and was read by
> nobody: it sat inside a JSON blob or was discarded for a status code. Two of
> the four families showed the person **less** than before their language was
> ever considered.
>
> **The fix.** `i18n.validation_message` composes one sentence from the rows, in
> the reader's language, and rides beside `detail` rather than replacing it —
> `detail` is the FastAPI contract, what a machine reading this API has a right
> to, and what the driven tests read. Every client decode now reads the sentence
> first. The field name stays the API's own (`display_name`), joined with an em
> dash rather than declined into the sentence, so nothing comes out half in one
> language and half in another. Mapping those names to the labels a form
> actually shows needs a per-client table that does not exist, and is recorded as
> the remaining gap rather than guessed at.
>
> **The guard took three attempts, and the first two are why the third is worth
> having.** Asking whether a client's source mentions `message` passed on all
> four clients while all four were broken — it is a field on a model, a
> parameter name on an exception class, and a word in the comment directly above
> the bug. Anchoring on the throw and asking whether the surrounding lines read
> it caught the three shells and still passed on a broken console, because the
> fallback chain has always read the sentence key as an *alternative to*
> `detail`.
>
>     asked     does the decode mention the sentence
>     mattered  does the decode pass the sentence on
>
> Seven injections, each caught by the right test with the right message.

## app-v0.30.2 — JIM-mini app-v0.30.2

- Published: 2026-08-01
- Commit: `ba13cb0cd74dc328fd23167eb289ee0e8efc4f93`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.30.2>

> ### The synthetic self: the one QRME profile that is the user
>
> Every other link between these products reaches *somebody else's* profile. A
> tandem specialist belongs to a clinician; a coordination runs in the care-team
> org; a delegated workflow has an owner who is not the JIM user. In all of it
> the JIM user meets QRME as an **interactor** — `tandem_links` maps them to a
> `usr_` id and a capability token — which is to say, as a stranger.
>
> QRME's `ProfileKind` is `self | other_person | fictional | hybrid`, and a
> `self` profile speaks *as* the person. JIM had no column, module or route that
> knew it existed, and QRME held nothing pointing back.
>
>     asked     does JIM reference synthetic profiles
>     mattered  does JIM reference this person's own
>
> `docs/tandem.md` carries the contract, byte-identical in three repositories,
> and was written **before** this code so the boundary could not be settled by
> whatever the first implementation happened to do. `jim/synthetic_self.py`
> implements it: an owner token rather than an interactor token; the link refused
> unless QRME reports `kind == "self"`; an enumerated allowlist consented per
> category and empty by default; the brief composed **from** the allowlist rather
> than filtered down to it, so a category nobody wrote a builder for cannot cross
> by a future route; and a standing rather than a history, replaced on each brief.
>
> **Medication carries the person's own words, by decision, and the contract says
> so** rather than leaving it to the code. `meds.py` refuses a medication with no
> name and invites their wording — *"the little white one, 10 mg"* — so names are
> free text by design, and a name can be a diagnosis: *"the pill for my HIV"* is
> one typed into a field asking for a drug. The preview shows the strings and not
> a count of them, because that is the only form in which the decision is real.
> Journal entries, check-in notes and transcripts never cross under any consent:
> there is no builder for them, which is the enforcement.
>
> The preview **is** the payload — same function, asserted. A preview composed
> separately is a preview free to drift from what goes, which is the shape of
> every *we only share anonymous data* claim that turned out to be false.
>
> The brief is posted as source material to QRME's own owner-gated
> `/profiles/{id}/sources`, so it lands where the persona is grounded and is
> sealed into PDI when QRME has a vault configured.
>
> Doors on all four clients: console screen 101, localized into ten languages
> from the start, and a screen on iOS, Android and Windows with a real
> `ApiClient` method behind each.
>
>
> ### A screen that calls the localizer, and a localizer with nothing to say
>
> The three native screens were written, the suite went green, and the twenty
> `L10n` keys had gone into the console's `app/src/l10n.ts` and **none of the
> three native tables**.
>
>     asked     does the screen call the localizer
>     mattered  does the localizer have anything to say
>
> Every existing guard passed, for a reason worth naming: `native_untranslated.txt`
> records English strings that are *present*, and those screens held no English to
> find — only key names. The door audits passed because the bindings were called.
> On a device, `L10n.t("self.title")` with no row returns the key, so the heading
> would have read `self.title` in every language, on all three phones, on the
> screen about what a person's medication may say about them.
>
> `test_a_shell_asks_for_a_key_it_has.py` checks both directions **per shell** —
> a union tells you *some* client is fine, which is this suite's oldest lesson.
> Injecting the original state reproduces it: *"ios asks for 20 key(s) its L10n
> table does not hold"*.
>
> Run backwards it found four rows nobody had noticed — `action.refresh`,
> `action.save`, `action.send`, `action.translate`: generic verbs added for
> screens never written, translated into ten languages and read by nobody. The
> console gained that check in 0.27.0 after two dead keys shipped; the shells
> never had it. Recorded in `native_dead_keys.txt` and ratcheted rather than
> deleted.
>
> The `self.*` rows were lifted from the console table programmatically, not
> retyped, and a test asserts the four surfaces still say the same thing.

## app-v0.30.1 — JIM-mini app-v0.30.1

- Published: 2026-08-01
- Commit: `35bd2896334e0ef45d733ceef1bb8454099f8fc1`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.30.1>

> ### The refusal that handed the body back
>
> The round in 0.30.0 put every refusal this product *writes* into the reader's
> language, through nine handlers that all return by one door. It missed every
> refusal this product *returns*.
>
>     asked     is every refusal this product writes translated
>     mattered  is every refusal this product returns
>
> `RequestValidationError` is neither an `HTTPException` nor one of the eight
> domain errors, so a 422 went out past all nine — carrying pydantic's `input`
> key, which on a missing field is the entire submitted body. A real drive
> against `POST /journal`:
>
>     {"type": "missing", "loc": ["body", "text"], "msg": "Field required",
>      "input": {"entry": "chest pain since Tuesday, have not told my
>                daughter", "mood": 3}}
>
> Every other part of this product's error design refuses to carry content —
> `errors.ts` and the three `Problems` shells record a method, a redacted path
> and a status and have no parameter a message could arrive through; `cloudgw`
> refuses a report whole if it finds prose in it. The one place content left the
> process was the framework's default renderer, because nobody had looked at it
> as ours.
>
> **What this is not:** disclosure between people. A 422 goes back to whoever
> sent the request, so what came back was the sender's own body. **What it is:**
> content on an error path, travelling through whatever sits between the app and
> the person.
>
> `type`, `loc` and `msg` are returned; `input` and `ctx` are not, built as an
> allowlist so the response cannot grow a leak by somebody else's release.
> `value_error` and `assertion_error` messages are replaced outright. On
> `extra_forbidden` the caller's key is echoed only when it is *shaped* like a
> field name — the first version replaced it always, and the sibling
> repository's suite failed by name, because a round had been spent making two
> routes strict precisely so a caller is told which key was wrong.
>
>     asked     can a key carry content
>     mattered  does this key look like content
>
> The guard posts a canary at every body-taking route from `all_routes` rather
> than checking for the `input` key, and a second check asserts how many of those
> routes reached validation at all.
>
>
> ### The synthetic self enters the tandem contract
>
> `docs/tandem.md` gains the boundary before the code that will obey it.
>
> Everything the contract described linked JIM to *somebody else's* profile, and
> the JIM user reached QRME as an **interactor** — a stranger. QRME's
> `ProfileKind` is `self | other_person | fictional | hybrid` and a `self`
> profile speaks *as* the person; JIM had no column, module or route that knew it
> existed, and QRME held nothing pointing back.
>
>     asked     does JIM reference synthetic profiles
>     mattered  does JIM reference this person's own
>
> An owner token, not an interactor token. The link refused unless QRME reports
> `kind == "self"`. JIM → QRME is an enumerated allowlist, consented per
> category, empty by default, with the composer building the brief *from* the
> allowlist rather than filtering a payload down to it — and no free text from
> the user crossing at all: no journal entry, no check-in note, no transcript.
> Byte-identical in all three repositories.

## app-v0.30.0 — JIM-mini app-v0.30.0

- Published: 2026-08-01
- Commit: `acec04ac471b0ce13378e562fee6fa98c2869970`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.30.0>

> ### Safety text is never machine-mangled; it was never translated either
>
> `jim/i18n.py` opens with "everything the Guardian drafts or delivers,
> localized" and is emphatic about the part that matters most:
>
> > **Deterministic safety content** (the CPR/AED playbooks, pace cues, waiver
> > terms) is *hand-translated here* for every supported language ... Safety text
> > is never machine-mangled.
>
> The playbooks are. The pace cues are. The waiver terms are. The sentences the
> Guardian says when it says **no** were English — all sixty-four, including
> every refusal the medication cabinet, the vigil, the crash watch and the watch
> bridge can produce. Somebody setting up a fall alarm for their mother, in
> Portuguese, on a Portuguese phone, was told in English what was wrong with it.
>
>     asked     is the safety content the Guardian drafts translated
>     mattered  is the safety content it refuses with
>
> **One handler would have been the wrong fix here, and would have passed.**
> The sibling repository's round is a single `HTTPException` handler and that
> covers its whole surface. `create_app` in this one has **eight more**, one per
> health domain, each building its own `JSONResponse`. Porting the single handler
> across would have localized the framework's refusals and left every domain's
> own untouched — in this product, exactly the wrong eight to miss.
>
>     asked     are the refusals localized
>     mattered  are all of them
>
> All nine now return through `i18n.refuse`, the one place a refusal becomes a
> response. `test_every_handler_returns_through_the_one_place` reads `api.py`'s
> own AST and fails any handler that does not — structurally, because a driven
> check would cover the eight that exist and say nothing about the ninth.
>
> **Twenty-two** sentences translated into all nine languages: the credential
> checks and every literal refusal from the four health domains. *Which*
> twenty-two is itself asserted, so a later round cannot improve the count by
> translating alphabetically while the cabinet slides back down the list. **42**
> more recorded in `jim/tests/refusals_untranslated.txt` and ratcheted, with the
> 25 f-string refusals named in the header as a class the file does not cover.
>
> `get_language`, not `effective_language`: the latter answers English whenever
> the mode is `on_demand`, which is a statement about how *drafted* text arrives
> — keep the original medical wording, I will translate what I choose — and says
> nothing about what somebody reads when the app refuses them. The credential
> names the reader, so a passer-by on a care beacon still gets their own language
> and not the watched person's.
>
> Headers are carried through `refuse()` rather than dropped. A translation round
> is no reason for a 401 to stop saying how to authenticate.

## app-v0.29.0 — JIM-mini app-v0.29.0

- Published: 2026-08-01
- Commit: `b1245adb31ef1680d751e9ec7fbb134065b562a0`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.29.0>

> ### The frame around both
>
> The nav is the console's own surface: the phones carry ten languages, the
> server answers in the reader's, and the frame around both was English whatever
> anybody chose. Its labels sat in `App.tsx` as literals in a `NAV` table, which
> made them the one thing no language setting could reach.
>
> Nineteen `nav.*` keys, looked up by id — `` t(`nav.${n.id}`, lang) `` — the
> same shape QRME's console has used since its chrome round.
>
> ### And what is not done, counted
>
> `console_untranslated.txt` measured `Onboarding.tsx` alone for two releases.
> That is how **677 English strings across nineteen gated screens** stayed out
> of a record whose header said the backlog was thirty-five.
>
>     asked     is the pre-session screen localized
>     mattered  is the console localized
>
> The record now covers every screen the console renders. The gated ones are a
> different argument from the accountless one — their reader *has* a language
> setting, and the server already honours it — which is why the nav is done this
> round and the screen bodies are written down rather than half-translated.
>
>
> ### The console backlog reaches its floor, and eight dead keys
>
> 47 → 35 → **7**, and the seven are punctuation, a shell command and example
> values — the same in every language.
>
> Eight of last release's keys were in the table and wired to nothing. They had
> been translated into ten languages and no screen looked any of them up, so the
> strings stayed English while the table said otherwise. Every completeness
> check passed, because they ask whether a key *has* its ten languages and never
> whether anything asks for it.
>
>     asked     is every key in the table complete
>     mattered  does every key in the table reach a screen
>
> Both repositories now check. The first version of that check read literal keys
> only and called all fifty-three of QRME's `nav.*` keys dead — every one live,
> looked up as `` t(`nav.${n.id}`, lang) ``. A guard against dead translations
> that would have had somebody delete the working ones. It now understands a
> built key's literal head.
>
> Ten wrapped strings needed a second pass: JSX had broken them across source
> lines, and a substitution matching one line finds nothing while reporting a
> count that looks like success.

## app-v0.28.0 — JIM-mini app-v0.28.0

- Published: 2026-08-01
- Commit: `473468f4652098fe17c9ad02b94e22d46143ebd6`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.28.0>

> ### The console gets a language, and a tripwire fires exactly as designed
>
> Last release measured the gap: JIM's native shells carry ten-language `L10n`
> tables and the desktop console had none at all. This is the layer — a
> `l10n.ts` with `visitorLang()`, twenty keys across all ten languages, and the
> pre-session screen wired to it. The pre-session backlog is **47 → 35**;
> `visitorLang` reads what the browser asked for rather than a stored setting,
> because the reader of that screen has no account for a setting to live in.
>
> Two guards broke on the way, both the same shape, and one of them had been
> left there on purpose.
>
> `test_a_promise_is_not_a_door.py` carried a tripwire whose docstring said, in
> so many words, *"JIM's console has no such table yet… When it arrives, this
> fails and says what to do, instead of `test_no_gated_screen_both_promises_and
> _carries` going silently blind on the day the copy starts moving."* It fired
> on the first build. `_prose` now resolves keys through the table the way
> QRME's `_shown_text` does, and the tripwire is deleted as its own message
> instructed.
>
> `test_the_door_and_the_wire.py` broke without warning for the same reason: it
> asserted a sentence was in a screen's file, and the sentence had moved.
>
>     asked     does this file contain this English sentence
>     mattered  does this screen say this to the person reading it
>
> Both now read what the screen *shows*, whatever file the words live in.

## app-v0.25.0 — JIM-mini app-v0.25.0

- Published: 2026-08-01
- Commit: `9682170bca752af30940774a97eda05785e1c9fd`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.25.0>

> Aligned with QRME 0.25.0. The three products carry one version, so a release
> that only moves in one of them still moves in all three — otherwise a support
> question about "0.25" has three different answers depending on which app is
> being asked about.
>
> Nothing in JIM's own code changed this cut. QRME's round covered the two
> outstanding console-credential tasks and the Windows Hello field test, and
> found a real defect writing each one up: a WebAuthn relying party id must be a
> domain, so the ceremony could never have run from a loopback origin; and the
> Apple client secret is a JWT that expires within six months with no warning of
> any kind.
>
> Neither finding reaches JIM — it has no signing ceremony and no Apple sign-in
> door. Recorded here so the version's contents are legible from this repo
> without opening another one.

## app-v0.21.0 — JIM-mini app-v0.21.0

- Published: 2026-08-01
- Commit: `41bd39a07736f834e660e657767367923c7999df`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.21.0>

> **JIM-mini v0.21.0 — cut in step with QRME.**
>
> The three products are cut together at one version so an installed suite never
> has to reason about which piece is which release. This one carries no JIM-mini
> feature work: the round that produced it ran in QRME, where four console doors
> were built for backend features that had none.
>
> Three of those four rounds found a defect behind the door, and the pattern is
> worth naming here because the same door audit runs in this repository:
>
> * a room's transcript and its `advance` route asked for **no credential at
>   all**, while the microphone disclosure two routes away checked membership;
> * a delegation policy was publishable and impossible to take up, with every
>   backend rule already correct;
> * `verify_package` reported **the signature is invalid** for a package that
>   was merely missing a field, when the cryptography had verified — the reason
>   given as a bare `KeyError` repr.
>
> In each case the argument against the defect was already written down
> somewhere else in the same repository. That is the whole return on building
> the door: it puts you in front of the thing the door leads to.
>
> ## The console backlog here
>
> JIM-mini's own per-client audit still records **109 routes** the console cannot
> reach on its own, against a union backlog that looks much smaller because the
> iOS, Android and Windows shells can reach them. That number is the honest one
> and it is unchanged this release — the ratchet holds it from rising.
>
> ## What changed
>
> Version strings only, plus the release-title convention recorded in
> `docs/releasing.md`: release titles now carry the product name, so
> `JIM-mini app-v0.21.0` rather than a bare tag.
>
>
> ## What's Changed
> * Record what breaks on the phone and the desktop shell too by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/179
> * Cut 0.20.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/180
> * The installer could not report, and nothing said so by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/181
> * Ask each client the door question separately by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/182
> * Cut 0.20.1 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/183
> * The release title carries the product name by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/184
> * Cut 0.21.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/185
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.20.0...app-v0.21.0

## app-v0.20.0 — JIM-mini app-v0.20.0

- Published: 2026-08-01
- Commit: `d4c0811bb48e5d6e76ec99319fe5a560140c7ca7`
- Assets: 0
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.20.0>

> **JIM-mini v0.20.0 — the native shells record what breaks, and the route guard
> stopped inventing work.**
>
> ## Failures from the phone and the desktop shell
>
> The consoles have recorded failures content-free since 0.19.0 — the operation
> and the status, never the message, never the path as it was typed. That is the
> governing constraint: a crash report is worth having only if nothing private
> travels in it, and the safest way to guarantee that is to have nothing private
> to send.
>
> The web console has done it since 0.19.0; **iOS, Android and the desktop shell
> had not**, so a failure that happened only on a phone happened only in silence.
> All three now record on the same terms and post to the same gateway.
>
> `docs/cloud-model.md` — byte-identical across the three repositories — gains
> the gateway's container deploy path. The gateway lives in QRME's tree, but
> every product's console posts to it, so the instructions belong wherever
> somebody is reading about the contract.
>
> ## A guard that invented work
>
> Every earlier defect in `clientpaths.py` made it too **lenient**: a truncated
> path, a verb read off a neighbouring call, a route table read flat instead of
> recursed. Those are the failures you expect from a checker.
>
> This one was the other kind. A template literal may nest another inside an
> interpolation, and the extraction pattern's backtick alternative stopped at the
> *inner* opening backtick — so a call normalised to a path no route matches, and
> a route with a working door was reported as having none.
>
> Nothing failed. The suite stayed green. The route sat on the backlog looking
> like work, and a door-building round was aimed at it before anybody noticed the
> door was already there. **A checker that invents work fails more quietly than
> one that misses some:** a miss is found by the bug it let through, while an
> invention is found only by somebody going to do the work and finding it done.
>
> Interpolations are now matched by counting braces, so a nested one passes
> through intact.

## app-v0.24.0 — JIM-mini app-v0.24.0

- Published: 2026-08-01
- Commit: `d5e1174c780306f5604e2fe2adbce2b594b35f91`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.24.0>

> Three rounds, one question: **when a passer-by does reach the page built for
> them, can they read what it says?**
>
> The beacon page has negotiated `Accept-Language` since the round that
> localized it. Everything around the edges of it had not.
>
> ## Five strings the named checks could not have found
>
> The existing test named four Spanish strings and checked they appeared on the
> beacon page. They did. Meanwhile five strings a passer-by reads had never
> gone through `tr` at all, so no language reached them and no amount of adding
> translations would have:
>
> - **Both `<title>`s** — what the tab shows, what a shared link previews as,
>   and what a screen reader announces first. English, under a translated
>   document.
> - **The greeting.** `You've found {name}.` was translated only in its
>   *anonymous* branch. With a first name on the beacon the code built an
>   f-string, so the largest sentence on the page was English for every finder
>   holding a beacon that names somebody.
> - **Both foot paragraphs** — the sentence telling a finder what pressing the
>   button will and will not do. Neither branch wrapped, and testing one branch
>   is how the other could have stayed English indefinitely.
>
> Four checks now derive the list from the page rather than from what somebody
> thought to name.
>
> ## The page was translated; the answer to the button was not
>
> `POST /c/{id}/alarm` never read the header, and the page renders two of its
> fields onto itself after the fetch:
>
> > The alarm is raised. This is not an emergency service.
>
> > The people watching over this person have been alerted. If this is an
> > emergency, call your local emergency number — this page cannot.
>
> Those are the two sentences on the whole surface that most need to be
> understood, and they arrive while somebody is kneeling over a person deciding
> what to do next. A Spanish finder read a Spanish page, pressed a Spanish
> button, and was answered in English — including the sentence saying this page
> cannot call anyone and they have to.
>
> `note` and `badge` by name rather than a walk over the response. The Medical
> ID rides in the same object, and a person's conditions, their emergency
> contact's name and their resting heart rate are facts rather than copy.
> Translating a clinical value is how a responder gets misled, which is worse
> than an English one they can still read — there is a test holding that line.
>
> The minor's variant is a third sentence and is covered. The 404 the *button*
> answers for a peeled-off code is translated too: the page for that code
> already was, and somebody who presses the button is the person who most wants
> a sentence they can read.
>
> ## One header, three products
>
> QRME, JIM-mini and PDI each grew a `negotiate()` in a different round.
> Compared side by side for the first time, JIM disagreed with both on two rows.
>
> `q=0` means **not acceptable** — RFC 9110 is explicit — so a browser sending
> `ar;q=0` is refusing Arabic. This appended every recognised tag to its
> ranking regardless of quality, so a header that refused the only language it
> named got that language back, on the page somebody reads while deciding what
> to do for a person on the floor.
>
> Fixed here; QRME and PDI were already right. A conformance table now lives
> byte-identically in all three repositories.
>
> ## Also
>
> - A tripwire on the promise-and-door guard. Everything it does assumes a
>   screen's words are in the screen's file, and QRME's copy of that check broke
>   on exactly that assumption when a lookup table arrived. This console has no
>   table yet and its server grew `jim/i18n.py` in the same round, so the check
>   now fails the day one lands and says what to do.
>
> **864 tests passing.**

## app-v0.23.0 — JIM-mini app-v0.23.0

- Published: 2026-08-01
- Commit: `1183fb9e0e3e30f57698748957fe5eea43347217`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.23.0>

> **JIM-mini v0.22.0 — the console backlog reaches zero.**
>
> The desktop console could not reach **109** of JIM's routes. Every one was
> present on the phone shells, which is why the guard reported a healthy number
> for as long as it did: it was answering *some client can reach this*, and a
> phone could.
>
> | | at the start of this release | now |
> |---|---|---|
> | Console-doorless routes | 109 | **0** |
> | Routes no client anywhere calls | 69 | **0** |
> | `api.ts` bindings nothing calls | 4 | **0** |
>
> All three record files are now **empty rather than short**, and the tests that
> read them assert emptiness.
>
> ## Six new screens
>
> Screens 95–100, one per family the routes fell into:
>
> - **What you're working on** — goals, habits, a monthly budget. None of it is a
>   list for its own sake: a goal is read by the Coach and the daily suggestion,
>   and a budget is how the Guardian learns the shape of financial stress.
> - **Who you watch** — a child's account and its limits. Pausing holds everyday
>   guidance only; monitoring, crisis escalation and the emergency path never
>   pause, and the server says so in its own words every time you use a control.
> - **What's held about you** — custody, the access log, consented sources, the
>   plan's storage posture, and the erase-everything door.
> - **Who else is looking** — specialists, referrals, the household relay, and
>   the escalation ladder with its floors and its one ceiling.
> - **What reaches out** — a bound robot and its first-aid rating, a placed care
>   code, accounts on platforms JIM does not run, and excursions.
> - **Bearing** — what you set, what you told it, and what it made of that.
>
> Each with a walkthrough lesson and a help direction.
>
> ## Starting without an email address
>
> `POST /enroll` has always taken a name, a birthdate and a consent. Every screen
> in front of it demanded an email address and a password, so the only way to
> reach it was a phone.
>
> An email address is a thing a person may not have, may not control, or may
> share with somebody they are trying not to be watched by. A guardian product
> that makes one mandatory to begin has quietly decided who gets a guardian.
> This deployment's backend never decided that; the console did, by omission.
>
> The trade is stated rather than buried: no address means no recovery, and the
> device holds the only key.
>
> ## What driving the routes found
>
> Nothing in the backend was broken this round. What a running server disagreed
> with the route table about:
>
> - **`raiseEmergency` sent no credential**, on the reasonable-sounding premise
>   that an emergency is when a person is least able to produce one. The
>   server's reason is better: an uncredentialed `POST /emergency/{id}` lets
>   anybody reach `emergency_services` against anybody's account. The
>   uncredentialed door for a bystander already existed and is a different one —
>   a scanned care code, capped at `notify_contact`. The escalation policy states
>   that ceiling in a field the client already reads.
> - **`GET /access-log` answers an object, not a list.** Its other three fields
>   say whether anything is being recorded at all. On a vault-less deployment an
>   empty `entries` means *no log exists*, not *nobody looked* — and a privacy
>   screen showing a person the wrong one of those two, silently, is the worst
>   available way for that page to fail.
> - **Two routes were bound without required query parameters**, so both were a
>   422 every time.
> - **The care-code scan page is HTML and two `qr.svg` routes are SVG**; through
>   the JSON helper all three came back `null`.
> - **The social beacon and its code need the owner's token**, unlike the
>   placed-code pair they resemble.
>
> ## Three more things the console never offered
>
> Looking at a clinical capture (the image is on its own route, and a person's
> own body photographs were listed with no way to see them), handing channel 2
> over with its reason and whether anybody else was in the room, and reading the
> vigil **without** sweeping it — a sweep can trip the vigil and send somebody to
> a person's door, which makes it a write, and a write should not be the only way
> to look at a thing.
>
> ## Two guards that could only pass while the problem existed
>
> One asserted the union backlog was *strictly* smaller than the console's; the
> other asserted the audit's snapshot file was non-empty. Both have been
> rewritten to check what they were for rather than what they happened to
> measure.
>
> **Suite: 802 passing, 1 skipped.**
>
> ---
>
> Cut in step with [QRME](https://github.com/davidsbianchi1984/qrme) and
> [PDI](https://github.com/davidsbianchi1984/pdi), both also at v0.22.0. All
> three reached zero on the same audit in this release.

## app-v0.22.0 — JIM-mini app-v0.22.0

- Published: 2026-07-31
- Commit: `aeea2fa8d0bfa2055ffb646e7399fb0555b3807b`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.22.0>

> **JIM-mini v0.22.0 — the console backlog reaches zero.**
>
> The desktop console could not reach **109** of JIM's routes. Every one was
> present on the phone shells, which is why the guard reported a healthy number
> for as long as it did: it was answering *some client can reach this*, and a
> phone could.
>
> | | at the start of this release | now |
> |---|---|---|
> | Console-doorless routes | 109 | **0** |
> | Routes no client anywhere calls | 69 | **0** |
> | `api.ts` bindings nothing calls | 4 | **0** |
>
> All three record files are now **empty rather than short**, and the tests that
> read them assert emptiness.
>
> ## Six new screens
>
> Screens 95–100, one per family the routes fell into:
>
> - **What you're working on** — goals, habits, a monthly budget. None of it is a
>   list for its own sake: a goal is read by the Coach and the daily suggestion,
>   and a budget is how the Guardian learns the shape of financial stress.
> - **Who you watch** — a child's account and its limits. Pausing holds everyday
>   guidance only; monitoring, crisis escalation and the emergency path never
>   pause, and the server says so in its own words every time you use a control.
> - **What's held about you** — custody, the access log, consented sources, the
>   plan's storage posture, and the erase-everything door.
> - **Who else is looking** — specialists, referrals, the household relay, and
>   the escalation ladder with its floors and its one ceiling.
> - **What reaches out** — a bound robot and its first-aid rating, a placed care
>   code, accounts on platforms JIM does not run, and excursions.
> - **Bearing** — what you set, what you told it, and what it made of that.
>
> Each with a walkthrough lesson and a help direction.
>
> ## Starting without an email address
>
> `POST /enroll` has always taken a name, a birthdate and a consent. Every screen
> in front of it demanded an email address and a password, so the only way to
> reach it was a phone.
>
> An email address is a thing a person may not have, may not control, or may
> share with somebody they are trying not to be watched by. A guardian product
> that makes one mandatory to begin has quietly decided who gets a guardian.
> This deployment's backend never decided that; the console did, by omission.
>
> The trade is stated rather than buried: no address means no recovery, and the
> device holds the only key.
>
> ## What driving the routes found
>
> Nothing in the backend was broken this round. What a running server disagreed
> with the route table about:
>
> - **`raiseEmergency` sent no credential**, on the reasonable-sounding premise
>   that an emergency is when a person is least able to produce one. The
>   server's reason is better: an uncredentialed `POST /emergency/{id}` lets
>   anybody reach `emergency_services` against anybody's account. The
>   uncredentialed door for a bystander already existed and is a different one —
>   a scanned care code, capped at `notify_contact`. The escalation policy states
>   that ceiling in a field the client already reads.
> - **`GET /access-log` answers an object, not a list.** Its other three fields
>   say whether anything is being recorded at all. On a vault-less deployment an
>   empty `entries` means *no log exists*, not *nobody looked* — and a privacy
>   screen showing a person the wrong one of those two, silently, is the worst
>   available way for that page to fail.
> - **Two routes were bound without required query parameters**, so both were a
>   422 every time.
> - **The care-code scan page is HTML and two `qr.svg` routes are SVG**; through
>   the JSON helper all three came back `null`.
> - **The social beacon and its code need the owner's token**, unlike the
>   placed-code pair they resemble.
>
> ## Three more things the console never offered
>
> Looking at a clinical capture (the image is on its own route, and a person's
> own body photographs were listed with no way to see them), handing channel 2
> over with its reason and whether anybody else was in the room, and reading the
> vigil **without** sweeping it — a sweep can trip the vigil and send somebody to
> a person's door, which makes it a write, and a write should not be the only way
> to look at a thing.
>
> ## Two guards that could only pass while the problem existed
>
> One asserted the union backlog was *strictly* smaller than the console's; the
> other asserted the audit's snapshot file was non-empty. Both have been
> rewritten to check what they were for rather than what they happened to
> measure.
>
> **Suite: 802 passing, 1 skipped.**
>
> ---
>
> Cut in step with [QRME](https://github.com/davidsbianchi1984/qrme) and
> [PDI](https://github.com/davidsbianchi1984/pdi), both also at v0.22.0. All
> three reached zero on the same audit in this release.
>
>
> ## What's Changed
> * The release title carries the product name by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/184
> * Cut 0.21.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/185
> * JIM console doors: the 109-route backlog reaches zero by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/186
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.20.1...app-v0.22.0

## app-v0.20.1 — JIM-mini app-v0.20.1

- Published: 2026-07-31
- Commit: `f4d28e79550c7fb0cd91774c6714aa1c40b906f1`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.20.1>

> **JIM-mini v0.20.1 — the union hid a surface.**
>
> `clientpaths.doorless` unions the console with the iOS, Android and Windows
> shells, so a route only the phone calls counts as doored. The union backlog
> reads **69**; the console alone cannot reach **109 routes**. The guard
> was answering *some client can reach this*, which was true, in place of *this
> client can reach this*, which was not.
>
> That is the shape of every defect this audit has produced: a checker answering
> a question slightly to the left of the one that matters, and passing. In QRME
> the gap turned out to be the entire seller's side of the product — post a
> licence offer, see who holds one, revoke it, read what it earned, ask to be
> paid — all present on the phone, all absent from the desk.
>
> ## Two new guards
>
> - **`test_the_console_is_a_client_too.py`** — the console's own backlog, in
>   `console_doorless.txt`, checked in both directions and ratcheted so it cannot
>   grow past where it started. The union guard stays; a route no client anywhere
>   calls is still worse. A phone-only capability is a legitimate design choice,
>   which is what the snapshot is for: deferring one takes a deliberate edit and
>   shows up in a diff.
> - **`test_a_binding_is_not_a_door.py`** — the same mistake one level down. A
>   function in `api.ts` that no screen calls is not a door, and `doorless`
>   counted it as one. The docstring on `doorless` had said this was *"a
>   discipline rather than something the test can enforce"*; it is enforceable in
>   about twenty lines. *The test cannot check this* is a claim worth testing.
>   This repository has **four**.
>
> ## Fixed
>
> - **`clientpaths.py` was not byte-identical across the three repositories**,
>   though it says it is. This copy never received the `fetch`, `window.open`,
>   `<img src>` and `<a href>` call forms from 0.20.0, so its backlog counted
>   doors that already existed. Restored, and the backlog dropped **73 → 69**: `POST /voice/speak` and `POST /watch/seed/{user_id}` found by the new forms, and both OAuth callbacks correctly exempted.
> - **The pairing QR is built from a literal.** `Settings.tsx` rendered it as
>   `getBase() + pair.qr_svg`, where the path arrives in a response body — a real
>   door no static check can see. `GET /pair/qr.svg` sat in `NOT_A_CLIENT_CALL`
>   for exactly that reason, which is an exemption made out of a blind spot; the
>   last one of those turned out to have no door at all. Same request, now
>   visible to the audit.
>
> ## Cut together
>
> QRME, JIM-mini and PDI move on one version number. QRME's 0.20.1 additionally
> carries the seller's-side console screen and three money defects the building
> of it exposed — including a marketplace sale credited to a profile id while the
> statement reads by account id. See [QRME's notes](https://github.com/davidsbianchi1984/qrme/blob/main/RELEASE_NOTES.md).
>
>
> ## What's Changed
> * Stop the route guard inventing work by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/178
> * Record what breaks on the phone and the desktop shell too by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/179
> * Cut 0.20.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/180
> * The installer could not report, and nothing said so by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/181
> * Ask each client the door question separately by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/182
> * Cut 0.20.1 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/183
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.19.1...app-v0.20.1

## app-v0.19.1 — JIM-mini app-v0.19.1

- Published: 2026-07-30
- Commit: `607d59b9cee892451fc5416e9322a348ef8f28d2`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.19.1>

> **JIM-mini v0.19.1** — a feature can no longer ship with nothing drawn.
>
> The gallery tests all check screens against the README: a reference with no
> file, a file with no reference, a gap in the numbering. Every one of them
> starts from the screens. **None asked the opposite question — does this surface
> have a screen at all?** So a feature could ship undrawn, untaught and
> unreachable from the in-app helper, and the suite stayed green.
>
> That had happened three times, most recently to 0.19.0's own error-reporting
> card and its first-run notice, which went out undrawn while the release notes
> described them at length. It is the same shape of flaw found twice before here:
> a guard that only walks the relation in the direction where the answers already
> exist.
>
> `ui_screens.txt` is the missing direction. Every console surface carries a
> screen number, `undrawn`, or `unaudited`, so a surface nobody has classified
> fails in the round that introduces it. The mapping is declared rather than
> guessed — matching component names to screen titles resolved only a fraction of
> them, because titles are written for the person using the app and component
> names for the person editing it.
>
> Both backlogs are ratcheted against a ceiling each repository declares for
> itself, and a ceiling left high after the backlog falls fails too: a ratchet
> that stops ratcheting re-opens the ground it gained. Five failures were injected
> to prove it bites, including the one that matters — silencing the check by
> writing `undrawn` fails the ratchet.
>
> **And the two surfaces it caught are drawn.** Screens **93 What Went Wrong** and **94 Before Anything Is Sent** join the gallery, each
> with a lesson and with phrasings that reach it in the words somebody actually
> types when something has broken: "it failed", "something broke", "stop
> sending", "opt out". The card draws an operation and a status and nothing else,
> because that is all the log holds.
>
> **No application behaviour changes in this release** — screens, gallery,
> lessons, helper phrasings, and the guard that will keep them honest.
>
>
> ## What's Changed
> * Fail when a surface ships with no drawing, then draw the two that did by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/176
> * Cut 0.19.1 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/177
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.19.0...app-v0.19.1

## app-v0.19.0 — JIM-mini app-v0.19.0

- Published: 2026-07-30
- Commit: `896db2e0615b56b4eb3cbd7eb5e3c305425830d9`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.19.0>

> **JIM-mini v0.19.0** — the app can tell you what broke, without telling you
> anything about your health.
>
> Every failed request in the console is now recorded and, where a build has
> somewhere to send, reported. What gets kept is the *operation* and the
> status code, never the message and never the path as it was actually
> called. In a health product that distinction is the whole feature:
> `GET /users/{id}/captures/{id}/image → 404` identifies a bug, where the
> unredacted version of that path names a photograph of somebody's body and
> whose it is. Only the first is written down, and the redaction happens
> before the row is stored.
>
> JIM's backend puts user input straight into its error messages — *no
> device called 'Pixel Buds' on this account*, *unknown site 'knee'; one of
> scalp, face, eye, mouth…*. A place on your body. A device in your home.
> Good messages for the person reading them, and exactly the wrong thing to
> keep. So the message is shown to you, who own it, and is **never written
> to the log**.
>
> **Nothing goes before you have been asked.** Sending is opt-out, which
> only means something if the opting-out can happen before the first report
> rather than being discovered afterwards in a panel nobody opened. A
> first-run notice holds everything until it is answered — and it shows the
> actual payload rather than describing it, from the same function that
> sends it, so it cannot go stale while still reading honestly. The switch
> on the Privacy card is that same answer, changeable whenever.
>
> Counts are sent as **deltas**: each row remembers how much of itself has
> been reported, so reopening the app twenty times does not turn one broken
> screen into twenty. A failed send moves nothing, and the next launch
> retries.
>
> **The receiving gateway refuses rather than redacts.** It accepts exactly
> five top-level keys and five per problem and rejects anything else — an
> unknown field, a `platform` string long enough to hide a sentence, a `day`
> carrying a time of day, a path with an unredacted id still in it. It could
> redact that path itself; doing so would let a build whose redaction had
> broken keep working while nobody learned that every report from those
> users had been arriving with a user id in it.
>
> What survives is less than what arrives. Reports are not stored as
> reports — they fold into counters keyed by product, version, platform,
> operation and status. Locale is validated and then dropped, and nothing
> records that a particular install sent anything, or when beyond the day.
>
> **Off by default, by absence rather than by flag.** The collector address
> is compiled in at build time and unset, so an installer built without one
> has nowhere to send and no code path that could acquire one. There is no
> address for a later mistake to switch on.
>
> **Fixed** — four bugs found by running the thing rather than reasoning
> about it. The gateway had no CORS at all, so every browser preflight would
> have been refused and every report would have failed silently. Its
> validators were anchored with `$`, which in Python also matches before a
> trailing newline, so `Win32\n` passed a check whose error message promised
> newlines were not allowed. A counter file that was valid JSON of the wrong
> shape was adopted wholesale and took the read endpoint down with it. And
> the test guarding the payload shape ran only in the repository that ships
> the gateway — not here, where a leak would cost the most.
>
>
> ## What's Changed
> * Check JIM's four client surfaces against its own route table by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/168
> * Check the verb, not just the address by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/169
> * Menus that keep their promises, and the routes with no door at all by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/170
> * Channel 2 and the clinical camera reach a person by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/171
> * Exclude a desk's view and beacon QR from the doorless audit by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/172
> * Record what fails, without recording anything private by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/173
> * Send the error reports, and refuse anything that is not one by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/174
> * Cut 0.19.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/175
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.18.0...app-v0.19.0

## app-v0.18.0 — JIM-mini app-v0.18.0

- Published: 2026-07-30
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.18.0>

> **JIM-mini v0.18.0** — the rest of what JIM knew, on every shell.
>
> Three features that existed in the backend and the web console and nowhere
> else now reach iOS, Android and Windows.
>
> **"Did that help?"** sits on Monitor (spec [0039]). It reads from
> `/followup/{uid}` rather than the monitor reply, so a question opened in an
> *earlier* session is still asked instead of being quietly dropped —
> a question the app forgets is a question nobody answers. Saying it did not
> help is not filed away: the escalation ladder runs again with that fact in
> it and the screen names the people reachable right now, as people rather
> than as a tier.
>
> **What JIM has learned about you** and **Your name here** join Overview,
> where these shells already keep the baseline, model and language settings.
> The adaptation profile renders as counts off the user's own history, never
> a score, with the statement that nothing was sent to a model vendor to
> build it. The anonymity posture renders from the server's own keeps/costs
> lists, so what is on screen cannot drift from what the code does.
>
> **And all four new doors got drawn and taught.** Screens **89 Did That
> Help?**, **90 What JIM Learned**, **91 Your Name Here** and **92
> Community** join the gallery, each with a lesson, each reachable by asking
> the assistant in ordinary words — "it did not help", "what JIM knows about
> me", "pseudonym", "rooms".
>
> **Fixed** — the Windows palette had no `JimT3Brush`. The dimmest text tier
> exists in the Android and iOS themes but the desktop resources stopped at
> `T2`, so a page reaching for it would have failed to load its resources
> rather than merely looking wrong.
>
>
> ## What's Changed
> * Stress joins the check-in by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/156
> * OAuth doors, pace cue + budgets, companion relay + knowledge pack, the attach bracket, and two more model doors by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/157
> * Five things in the filing that had no code behind them by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/158
> * Cut 0.16.0, cite the publication number, and open the community door by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/159
> * Apple's door needs form_post, so give it one by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/160
> * The closing passage is not a release note by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/161
> * Two things JIM knew but never showed you by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/162
> * The community bridge reaches the native shells by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/163
> * Cut 0.17.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/164
> * Three more things JIM knew but only the web console asked about by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/165
> * Draw, teach and make findable what 0.16.0 and 0.17.0 shipped by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/166
> * Cut 0.18.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/167
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.15.0...app-v0.18.0

## app-v0.15.0 — JIM-mini app-v0.15.0

- Published: 2026-07-29
- Commit: `e57d244b4c130bde5821d2945f867673a72d72cb`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.15.0>

> **JIM-mini v0.15.0** — guided wellness, the on-purpose half of
> guidance.
>
> From the field videos, built as protocols rather than generations:
> guided calm sessions (quick reset, box breathing, 4-7-8, a ten-minute
> sit) with timed steps the console paces and can speak; workout plans
> shaped to the minutes you have, your level and focus, warm-up and
> cool-down non-negotiable; and meal plans shaped to goal and dietary
> preferences with the honesty rails stated on the plan. Nutrition
> becomes a first-class Coach area. All three land in the events
> stream, and the console gains a Wellness tab.
>
> ### Verification
>
> Full suite green.
>
> ### Install
>
> If you have 0.7.0 or later, this arrives on its own — one restart when
> prompted.
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * The docs web catches the field round by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/151
> * The crash watch reaches the native shells, and a fall reaches the Guardian by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/152
> * Cut 0.14.5 — a fall reaches the Guardian by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/153
> * Guided wellness: calm protocols, workout plans, meal plans by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/154
> * Cut 0.15.0 — guided wellness by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/155
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.14.4...app-v0.15.0

## app-v0.14.4 — JIM-mini app-v0.14.4

- Published: 2026-07-29
- Commit: `c3dd5a6f221cab17f4f944d36d34a736441f4afc`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.14.4>

> **JIM-mini v0.14.4** — the crash watch, and the doors the field asked for.
>
> The crash watch is the vigil's acute sibling, armed in advance and
> off by default: a critical reading opens "are you okay?", N
> unanswered attempts contact the trusted person you named — and, only
> if you ticked the box, record and relay an emergency-services
> dispatch request. Any sign of you ends it; drift check-ins stay calm
> and can never trigger it. The journal gets its console tab, typed or
> spoken. Talking with the Coach shows a breathing voice orb. A help
> box on every screen gives written directions. And the console names a
> version mismatch instead of answering "Not Found" in silence.
>
> ### Verification
>
> Full suite green.
>
> ### Install
>
> If you have 0.7.0 or later, this arrives on its own — one restart when
> prompted.
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * The console names a version mismatch by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/147
> * The crash watch, and the journal's door by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/148
> * The voice orb, and the help box by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/149
> * Cut 0.14.4 — the crash watch, and the doors the field asked for by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/150
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.14.3...app-v0.14.4

## app-v0.14.3 — JIM-mini app-v0.14.3

- Published: 2026-07-29
- Commit: `6f09e3a47fc2851e66ec9ff6758ff63b271a30d7`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.14.3>

> JIM-mini v0.14.3 — a documentation binding pass.
> Every README in the repo (app and the native shells) is now held to the same closing convention, byte-identical, enforced by a binding test so the next README added cannot drift.
> Verification
> Full suite green.
> Install
> If you have 0.7.0 or later, this arrives on its own — one restart when prompted.
> Full changelog: https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * The medicine cabinet — 0.9.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/128
> * The drip address answers — 0.9.1 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/129
> * A real offline model, and Settings says what it means — 0.10.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/130
> * Cut 0.11.0 — no functional change; cut with the siblings by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/131
> * Cut 0.11.1 — no functional change; cut with the siblings by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/132
> * Cut 0.12.0 — no functional change; cut with the siblings by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/133
> * The care team is an organization: Guardian coordinates the household by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/134
> * The console shows the care team by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/135
> * Cut 0.13.0 — the care team is an organization by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/136
> * Docs round: the tandem contract + invention disclosure catch up by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/137
> * Cut 0.13.1 — no functional change; cut with the siblings by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/138
> * Home and the pane learn the care team by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/139
> * Cut 0.14.0 — Home and the pane learn the care team by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/140
> * The coach knows a care plan landed by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/141
> * Cut 0.14.1 — the coach knows a care plan landed by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/142
> * Docs: suite mode enters the tandem contract by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/143
> * Cut 0.14.2 — cut with the siblings by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/144
> * Every README ends on the rock by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/145
> * Cut 0.14.3 — every README ends on the rock by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/146
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.8.0...app-v0.14.3

## app-v0.8.0 — JIM-mini v0.8.0

- Published: 2026-07-29
- Commit: `main`
- Assets: 8
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.8.0>

> **JIM-mini v0.8.0** — the round where the Guardian learned to notice
> absence. One of three interoperating products, all three cut together at
> this version.
>
> ### The vigil
>
> Every other alarm in this product fires on a reading — a heart rate that
> climbed, an oxygen number that fell. The vigil fires on the **absence** of
> readings: the watch that went quiet, the check-in that never came, the
> person living alone whom no threshold can see because nothing is arriving
> to measure.
>
> In **Settings → The vigil** you name a steward, choose a quiet period, and
> write — now, while you are fine — the words they will read. If nothing is
> heard from you for longer than that period, they are asked to check on
> you, in your words, with the honest framing that no reading triggered
> this: it is the absence of readings.
>
> Three deliberate limits: it never rings past the steward (silence is weak
> evidence — the right response is a person who cares knocking on a door,
> not an ambulance); it trips at most once per silence; and any sign of life
> stands it down automatically, because showing up *is* the all-clear.
>
> ### One absence, three products
>
> The vigil's event id is an attestation reference the siblings accept:
> QRME's reviewer-gated ownership succession (a profile passes to its named
> successor, or sunsets to a frozen memorial) and PDI's new **bequests**
> (named scopes of the vault unlock to a named person — see PDI's notes).
> Continuity, end to end.
>
> ### Verification
>
> 619 tests green, including that the vigil's own trip never counts as a
> sign of life, that a brand-new user who was never heard from cannot trip
> it, that it trips exactly once, that no escalation event is ever written,
> and that the steward's message says plainly it is not an emergency.
>
> ### Install
>
> If you have 0.7.0, this arrives on its own — one restart when prompted.
> Otherwise, download the installer for your OS from the assets below.
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * The app keeps itself current — 0.7.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/126
> * The vigil: the alarm that fires when the signals stop — 0.8.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/127
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.6.1...app-v0.8.0

## app-v0.6.1 — JIM-mini v0.6.1

- Published: 2026-07-29
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.6.1>

> **JIM-mini v0.6.1** — the round where the coach stopped performing distress
> it never detected. One of three interoperating products, all three cut
> together at this version.
>
> ### The bug, as reported
>
> A career question — *"I want this app I built to be successful"* — was
> answered with *"I'm here with you [stub guidance for distress]… let's take
> one slow breath together."* Every time. Word for word.
>
> ### What was actually wrong
>
> Three things, stacked:
>
> 1. When no online model answers, JIM falls back to a deterministic
>    built-in helper (so a health app never goes dark). That helper's script
>    was written for the *medical guidance* path and **defaulted to
>    "distress"** when chat gave it no condition — crisis phrasing in what
>    was just a conversation.
> 2. Any model failure — a missing key, a network error, an overloaded
>    provider — **degraded silently**. The only record was a server-side log
>    line, and the reply's provenance named the model you *picked*, not the
>    one that answered. Canned text under Claude's name.
> 3. Settings said nothing in the worst case: *Automatic* quietly resolving
>    to the built-in helper, under a screen full of provider logos.
>
> ### What 0.6.1 does about it
>
> - In chat, the built-in helper now **explains itself honestly**: it says it
>   is the offline fallback, that your message is saved, and exactly where to
>   add a key — instead of playing a counselor.
> - Every coach reply **names who actually wrote it**. A real model answer
>   shows "Answered by anthropic"; a degrade shows an amber warning naming
>   the fallback and the reason ("anthropic did not answer: …", "no API key
>   on this machine — add one in Settings → Model").
> - **Settings → Which model answers** now says plainly when replies will
>   come from the built-in helper, and what to do about it.
>
> ### Verification
>
> 609 tests green, including that the reply's `generated_by` is the provider
> that produced the words rather than the one that was picked, that a
> mid-request failure is disclosed with its reason, that chat stub text
> contains no crisis language, and that choosing the offline helper on
> purpose is not reported as a degrade.
>
> ### Install
>
> Download the installer for your OS from the assets below and double-click.
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Personal drift bands, a voice, and a model picker with logos — 0.5.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/120
> * The Apple Watch bridge: a Shortcuts drip and a Health-export seed — 0.6.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/121
> * The coach stops performing distress it never detected — 0.6.1 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/122
> * Record the inventions with dates by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/123
> * Restore the owner's LICENSE exactly as he wrote it by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/124
> * Screens 81–84: the four capabilities the gallery didn't show yet by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/125
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.4.8...app-v0.6.1

## app-v0.4.8 — JIM-mini v0.4.8

- Published: 2026-07-29
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.4.8>

> **JIM-mini v0.4.8** — the round where the app can actually send email. One
> of three interoperating products, all three cut together at this version.
>
> ### Mail is configuration, and now it is in the app
>
> An app cannot send email by itself; it has to hand the message to a mail
> server. Until now the only way to name one was an environment variable —
> so a desktop install never could, and a verification email was never going
> to arrive no matter how many times it was requested.
>
> **Settings → Email delivery** now takes a mail server, username, app
> password, from address and link address. It says plainly which source is in
> force (environment beats the settings screen beats nothing), and it
> **sends a real test message on demand** — reporting exactly what the mail
> server said rather than claiming success. The password is stored on the
> machine it was typed on and is never returned by the API.
>
> Configure one and local signup becomes genuine email verification again,
> with the clickable link as the headline and the 6-digit code as fallback.
> Leave it empty and the app says so, and lets you in — because an
> unprovable inbox is not a gate, it is a locked door in an empty house.
>
> ### Verification
>
> 566 tests green, including that the password never comes back out, that
> the environment outranks the settings row, that a failed send reports the
> server's own words, and that configuring mail flips signup from local
> activation to a real emailed link.
>
> ### Install
>
> Download the installer for your OS from the assets below and double-click.
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * An upgraded app no longer adopts an older install's leftover backend — cut 0.4.7 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/118
> * Email delivery is configurable from the app itself — cut 0.4.8 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/119
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.4.6...app-v0.4.8

## app-v0.4.6 — JIM-mini v0.4.6

- Published: 2026-07-28
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.4.6>

> **JIM-mini v0.4.6** — the round where verification matched the deployment.
> One of three interoperating products, all three cut together at this
> version.
>
> ### Signup that fits where it runs
>
> A desktop install has no mail service, so no email can ever arrive — yet
> 0.4.4's code screen sat waiting for one. Now:
>
> - **Desktop (no mail transport): signup goes straight in.** The machine
>   owner is trusted on a single-user local install — there is no inbox to
>   prove and nothing to prove it to. Create account → you're in.
> - **Hosted (SMTP configured): a real email with a clickable verify link**,
>   the shape every mainstream flow uses, with the 6-digit code as fallback.
>   Click the link in your mail and **the app continues on its own** — it
>   holds your email and password, so it signs in the moment the address is
>   proven.
>
> ### Also fixed
>
> - A signup that crashed mid-flight (0.4.3) no longer strands the retry: a
>   pending account routes straight to verification with a fresh code; an
>   already-verified address routes to sign-in.
> - The packaged app can open its own backend log from the verification
>   screen (Electron bridge) — relevant on deployments without mail.
>
> ### Verification
>
> 556 tests green. The frozen binaries were rebuilt and the full first
> run driven against them — signup straight into a session, personal routes,
> sign-in.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.4.6` tag) and double-click —
> create your account and you are in.
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * A stranded pending account is finished on a no-mail machine — cut 0.4.6 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/117
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.4.5...app-v0.4.6

## app-v0.4.5 — JIM-mini v0.4.5

- Published: 2026-07-28
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.4.5>

> **JIM-mini v0.4.5** — the round where verification matched the deployment.
> One of three interoperating products, all three cut together at this
> version.
>
> ### Signup that fits where it runs
>
> A desktop install has no mail service, so no email can ever arrive — yet
> 0.4.4's code screen sat waiting for one. Now:
>
> - **Desktop (no mail transport): signup goes straight in.** The machine
>   owner is trusted on a single-user local install — there is no inbox to
>   prove and nothing to prove it to. Create account → you're in.
> - **Hosted (SMTP configured): a real email with a clickable verify link**,
>   the shape every mainstream flow uses, with the 6-digit code as fallback.
>   Click the link in your mail and **the app continues on its own** — it
>   holds your email and password, so it signs in the moment the address is
>   proven.
>
> ### Also fixed
>
> - A signup that crashed mid-flight (0.4.3) no longer strands the retry: a
>   pending account routes straight to verification with a fresh code; an
>   already-verified address routes to sign-in.
> - The packaged app can open its own backend log from the verification
>   screen (Electron bridge) — relevant on deployments without mail.
>
> ### Verification
>
> 556 tests green. The frozen binaries were rebuilt and the full first
> run driven against them — signup straight into a session, personal routes,
> sign-in.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.4.5` tag) and double-click —
> create your account and you are in.
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Verification matches the deployment: direct on desktop, link-first by mail — and the 0.4.5 cut by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/116
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.4.4...app-v0.4.5

## app-v0.4.4 — JIM-mini v0.4.4

- Published: 2026-07-28
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.4.4>

> **JIM-mini v0.4.4** — the round where the Windows signup 500 died. One of
> three interoperating products, all three cut together at this version.
>
>
> ### The fix
>
> With no mail server configured, the verification code prints to the server
> console — in a banner drawn with box characters that the frozen Windows
> backend's cp1252 console encoding cannot represent. The print raised
> mid-request, so **every signup answered "Internal Server Error"** on the
> one platform the console transport serves most — found by a real first-run
> report within the hour of 0.4.3 shipping. The banner is ASCII now, the
> frozen entry point reconfigures stdout/stderr to replace rather than raise,
> and a test encodes the console delivery to cp1252 forever
> (mutation-checked). The console also stops hiding one error behind another:
> a non-JSON body ("Internal Server Error") now surfaces as the server's own
> words, not a JSON-parse exception.
>
> ### Verification
>
> 553 tests green.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.4.4` tag) and double-click.
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Fix the Windows signup 500, and cut 0.4.4 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/114
> * Release gate: the frozen backend must perform the real first run, per OS by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/115
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.4.3...app-v0.4.4

## app-v0.4.3 — JIM-mini app-v0.4.3

- Published: 2026-07-28
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.4.3>

> **JIM-mini v0.4.3** — the release where the app got a front door, and the
> installer got legs. One of three interoperating products (with
> [qrme](https://github.com/davidsbianchi1984/qrme) and
> [pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at
> this version.
>
> ### Accounts — the address is proven before anything exists
>
> Email + password, in the shape every mainstream flow has taught people,
> built as our own screens: create-account and sign-in tabs, show/hide
> password toggles, the password typed twice with a live match check, the
> requirement stated up front, and **Forgot password**. Behind it, the
> security spine:
>
> - `POST /signup` takes email + password + the enrollment fields and
>   **creates nothing yet** — a 6-digit code goes to the address (SMTP when
>   configured, printed to the server terminal otherwise), and only
>   `POST /verify-email` enrolls the user and mints the first token. A
>   mistyped address never grows a record nobody can reach — on a product
>   holding medical data, that matters twice.
> - Password reset by the same emailed-code proof — and a reset **revokes
>   every existing session**, so whoever prompted it, only the inbox holder
>   stays signed in.
> - Unknown-address and wrong-password answer identically, and neither resend
>   nor reset-request reveals who has an account.
> - Passwords PBKDF2 with per-account salts; codes hashed at rest, single-use,
>   15-minute expiry, purpose-bound (a signup code cannot reset a password).
>
> ### Bring your own model key
>
> Paste your credential (Anthropic, OpenAI, xAI, Gemini) in Settings: it stays
> on your device, rides only your requests as `x-llm-api-key`, and the server
> **never stores or logs it** — a test dumps the whole database and asserts
> the key is not in it. A key makes your explicit provider choice usable with
> no deployment credentials at all, and on auto it defaults to Claude rather
> than the stub. The deployment's env key remains the fallback: an operator
> lending theirs out.
>
> ### The installer runs itself
>
> The whole Python backend ships **frozen inside the installer** (PyInstaller,
> per-OS) and the app spawns it at launch when nothing answers `/health` —
> double-click-and-done: no Python install, no terminal, data under the app's
> own user-data directory, the backend dying with the window. A backend you
> already run is left alone.
>
> ### Verification
>
> 552 tests green (22 new this round). The frozen binary was built and booted
> on Linux, and the full signup flow was driven end-to-end against it in a
> real browser — form, code read from the backend terminal, verified, into
> Overview.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.4.3` tag) and double-click —
> this is the first release where that is the whole instruction. Or run
> `python -m jim`, or open it on your phone — see the README.
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * The desktop installers were labelled 0.3.3 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/110
> * Online model default, and the Windows first-run fixed by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/111
> * Real accounts, bring-your-own model key, the self-running installer — and the 0.4.3 cut by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/112
> * mac: declare the frozen backend in x64ArchFiles by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/113
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.4.1...app-v0.4.3

## app-v0.4.1 — JIM-mini v0.4.1

- Published: 2026-07-28
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.4.1>

> **JIM-mini v0.4.1** — the release where a photograph really reached a
> clinician, and free got honest. One of three interoperating products (with
> [qrme](https://github.com/davidsbianchi1984/qrme) and
> [pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at
> this version.
>
> ### Show it, rather than describe it
>
> *"It's a bit red"* is the same sentence for a heat rash and for cellulitis.
> Clinical capture lets somebody photograph the thing — or film it, when it
> only shows in motion — mark where on the body, and send it through a referral
> to a real clinician. Four rules, each asserted and mutation-checked:
>
> - **A synthetic agent never receives the image.** It is told one exists,
>   where and when — routing, never diagnosis. A model that looks at a mole and
>   says "that looks fine" has made a diagnosis with no license and no
>   accountability, and a missed melanoma is not undone by the next sentence.
> - **Never an intimate site for a child.** No override, no guardian consent
>   path, no setting.
> - **The pixels never touch JIM's own database.** Vault only; the schema has
>   no column that could hold an image; no vault means refused, not degraded.
> - **Location is stripped, not promised absent** — a real JPEG parser drops
>   the metadata segments, checked against the bytes actually sealed.
>
> And the sentence "it travels with a referral" is now *true*: the referral
> package carries the capture's metadata (never bytes) so you read exactly what
> would go before signing, intimate sites never ride in on a match, and the
> field is `released_to_clinician` — released is not opened, and this app
> cannot see the second.
>
> ### A free plan, with nothing private about it
>
> Free is the whole Guardian — conditions, guidance, journal, habits, goals,
> **and every emergency path** — with the record under **platform custody**:
> JIM-mini holds it, you have access, ordinary HTTPS, no vault at any point.
> Basic ($20/mo) is the same Guardian sealed under a key you can hold. The
> features are identical; the difference is who holds your record, and every
> surface that names a plan says so.
>
> Two things the open store refuses — a photograph of a body, and a child's
> record on a guardian's account — because the person exposed did not pick the
> plan. The health readings are deliberately *not* refused: they are the
> emergency path, and a storage refusal in front of an escalation is a paywall
> in front of an alarm wearing a privacy argument. **Nothing that answers an
> emergency is ever behind a paywall, on any plan, still.**
>
> The vault gate now asks about the *plan* rather than the deployment — a free
> account's journal and detections were being sealed into a vault it was not
> paying for. Reads and erasure keep the real vault, so a downgraded account
> can still read its sealed history and have it purged. And the access log
> stopped telling a comfortable lie: on an open plan, an empty list means
> nothing was recorded, not that nothing was read — it now says which.
>
> ### Verification
>
> 525 tests green. Screens 76–80 new, tier and signup screens redrawn for the
> free plan, every guard above mutation-checked — one at a time, after checking
> them together masked two.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.4.1` tag), run `python -m jim`,
> or open it on your phone — see the README.
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Fix a broken gallery image on main, and add the guard that would have caught it by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/107
> * Clinical capture, a free plan under platform custody, and the join that made the claim true by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/108
> * Cut 0.4.1 — the round where a photograph really reached a clinician by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/109
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.4.0...app-v0.4.1

## app-v0.4.0 — JIM-mini app-v0.4.0

- Published: 2026-07-27
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.4.0>

> Added
>
> Membership: Basic $20/month, Pro $130/month — jim/tiers.py, 4 routes, 25 tests, screens 69 and 70. Basic is the Guardian itself — conditions, guidance, journal, habits, goals — and every emergency path. Pro adds the watch, early warning, specialists and synthetic agents.
>
> Nothing that answers an emergency is ever behind a paywall, and that is the rule the module exists to keep rather than a caveat on it. A lapsed card is a billing event; a seizure is not. NEVER_GATED names the alarm path, escalation, the medical ID a paramedic scans, incident history and the guidance given during an alarm — consulted first, so a pattern added later cannot reach them, and a test plants exactly that mistake and asserts each safety route still comes back ungated.
>
> The first implementation had that bug. /monitor was listed as the "proactive monitoring" capability, which reads correctly and is wrong: /monitor is the ingest. A Basic member submitting a blood oxygen of 84 received a 402 instead of an escalation — the paywall standing between somebody and an emergency, indirectly but completely. The suite caught it. What Pro buys is jim/earlywarning.py, the trend model that looks ahead of a threshold, and it is skipped rather than refused: a Basic member gets a real answer about the reading they submitted, with predictive: false saying plainly what they did not get.
>
> Every 402 carries emergency_unaffected: true. Money is simulated.
>
> The helper dock — jim/dock.py, 5 routes, 15 tests, screen 71. The glances a watch face would carry, in a pane in the corner — which matters here because the watch is a Pro capability. An active alarm opens it whatever it was set to, and the alarm face cannot be configured out of the pane: this is the one place the rule deliberately departs from QRME's, whose dock hides itself during a broadcast. The same rule here would hide the thing a person most needs to see, and JIM-mini has no broadcast surface to leak an alarm into.
>
> The Guardian gives the tour — jim/tutorial.py, eleven lessons in the Guardian's own voice, because here the Guardian already is somebody to the user. Channel 2's screens 65 and 66 came back in the same change, found by the walkthrough's coverage test on its first run.
>
> The Guardian gives a guided walkthrough — jim/tutorial.py, 6 routes, 11 tests. Eleven steps across four chapters, ?mode=voice to be spoken — which matters more here than in QRME, because this is a product used hands-free by somebody who may not be well.
>
> The Guardian gives it, rather than a faceless guide, and that is the one place this deliberately differs from QRME's version. QRME's subject is synthetic people, so a guide with a persona would be the most convincing one on the platform. JIM-mini has exactly one voice and is not pretending to be anybody — a separate guide would be a second voice in a product built on there being one, and the first thing a new user learned would be that JIM talks to them from two places.
>
> It never fires anything for you. No lesson triggers an escalation, reaches an emergency contact or files a condition "to show you how" — in a product whose actions reach a real person's phone at three in the morning, a demonstration that fires for real is not a demonstration. Tests assert it, along with writing nothing but the learner's own progress and needing no model configured.
>
> Fixed
>
> Screens 65 and 66 were missing. The hold that pulled channel 2 before 0.3.1 removed them, and green-lighting the feature restored QRME's screen 81 without restoring these — so the microphone shipped with routes, tests and a README section, and no pictures. Found by the walkthrough's own coverage test on its first run, which is the argument for that test in one line.
> Changed
>
> The video at the top of the README is no longer the whole header. A bare user-attachments URL becomes a full-width player, which on this page meant a large black rectangle with a play button sitting above everything the README is actually about — it read as the header rather than as one thing offered in it. There is no width attribute to set, because GitHub generates the element; the only handle is the width of the box it lands in, so it now sits in a narrow table cell with the cover illustration beside it. Playback is untouched: it still opens full screen with audio, which is what a small frame is for.
> Added
>
> Channel 2: a second microphone, for the agent — jim/mic.py, 9 routes, 34 tests. A phone has one microphone and one foreground claim on it. While somebody is on a call the Guardian is deaf — which is precisely when they might want to ask it something, and precisely when it cannot hear them ask. A watch already on the wrist has a microphone nothing else is using.
>
> Permission and state only — capture happens on the device; nothing in this module touches a sample. What the service owns is whether the agent may listen right now, on which device, and a record of when it did.
>
> Any personal microphone qualifies — watch, earbuds, headset, lapel, clip-on, bone-conduction, glasses. GET /mic/types publishes the list so a client offers the right one rather than guessing.
>
> Five refusals carry it:
>
> Only a microphone pointed at you. The first cut of this allowed only kind == "wearable", which was the right instinct reached by the wrong measure: a watch qualified and a lapel mic did not, though a lapel mic is aimed at one collar and a watch at a whole wrist. The axis is who the microphone is pointed at — a speakerphone or conference puck hears whoever is present, and those people never agreed. A stationary device is refused whatever microphone is in it.
> Not the microphone already carrying the call. Broadening exposed a collision a watch never had: earbuds on a call are the occupied microphone, and lending them asks one microphone to be two channels.
> Only while the primary is actually occupied, with the reason recorded. A second ear granted for no reason is just a second ear.
> Never on speakerphone. On an earpiece the wearable hears the wearer; on speaker it hears the other party too — someone who is not a user of this product, was never asked, and cannot revoke anything. A microphone the Guardian holds must not become a way to record the person on the other end of somebody else's call. Likewise refused with others in earshot.
> A handover ends, released explicitly or closed out with its reason, and every one is recorded: a listening permission that leaves no trace is one nobody can audit, and this is the permission people most want to check up on. A refused handover records nothing, so the history never implies the agent heard something it did not.
> Two bounds on what it hears, deliberately separate. Focus keys the channel on its wearer and drops the rest — background talk, a television, the people at the next table. It is not a setting: an option to include the chatter is an option to record people who never agreed, and nobody hands the agent a microphone in order to be told what the next table was saying. Gain is how far away that wearer can be. Focus decides what is listened to; gain decides what is in range, and keeping both means a failure of the first is still bounded by the second — which is the only reason to have a filter and a limit rather than a filter alone.
>
> Every gain level therefore describes the user at a distance, never a level of company: close to the microphone, at arm's length, from anywhere in the room. There is no setting whose answer to "what does it pick up" is "more people". reaches_others survives that reframing and is what the cap is judged on — not that others are transcribed, but that another voice is physically inside the pickup pattern, which is worse and is what a filter failure would expose.
>
> How wide the channel listens is not an audio-quality preference — it is the mechanism behind the sentence the product tells the user, the agent hears you, not your call. A promise enforced by a policy holds until somebody edits the policy; enforced by the capture width, it is a fact about what the microphone can pick up.
>
> PUT /users/{id}/mic/gain sets near_field, normal or wide, defaulting to the narrowest — a listening default that reaches other people is a default nobody chose. GET /mic/gains publishes the levels, reaches_others, and the focus guarantee.
>
> While the occupying reason is one where somebody else's voice is present (voice_call, video_call, live_room), the effective gain is capped at near-field however the user has set it — a dial that can be turned up into somebody else's conversation is not a safeguard, it is a suggestion. The adjustment is still accepted mid-call rather than refused, and takes effect when the call ends: refusing outright would teach people the control is broken, when what is happening is that the situation is temporarily narrower than their preference. Capped, not overwritten — the setting comes back. Each session records the gain it actually ran at, because an audit reporting the preference would overstate every capped call.
>
> The counterpart is qrme/roommic.py, which lends the same wearable to a live room's profiles — where the others are participants and can therefore be told, which is why that side discloses rather than refuses.**JIM-mini v0.3.3** — the release where a task working on its own stopped being
> something you had to go and check. One of three interoperating products (with
> [qrme](https://github.com/davidsbianchi1984/qrme) and
> [pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
> version.
>
> ### The watch face is the ambient one
>
> Three lights, three counts, dimmed at zero — and **no task names**.
>
> This is the surface the round exists for. While somebody is on their phone, the
> watch is the one place that can show several tasks at once without getting in
> the way. Naming them was the first cut and was wrong: a name is something you
> read, and reading is the thing a glance cannot do. The footer says *open on
> your phone*, because that is where the answer lives.
>
> | | | |
> | --- | --- | --- |
> | 🟢 **green** | working · done | in progress, or finished. Nothing wanted from you |
> | 🟡 **amber** | needs you | it has stopped and is waiting on a person |
> | 🔴 **red** | stopped | it hit an error or was cancelled, and will not continue |
>
> The word rides with the colour, because green alone cannot separate a task that
> is still going from one that has finished — and those call for opposite
> reactions.
>
> ### Screen 67, and an overlay that follows you
>
> **Screen 67** folds every task into one tappable group per light. Somebody
> opening it *because* amber appeared should not have to scan a flat list for the
> one that changed.
>
> **The overlay** rides over an ordinary screen, and over **every** desktop view —
> a task that reports only on its own screen is one you have to remember to go
> and check. It is shaped like the watch face rather than as a bar across the
> screen: a small translucent box in the corner, three stacked rows, each its own
> tap target.
>
> The mapping lives once, in QRME's `agentlight.py`, for all three products.
>
> ### The README leads with the screens now
>
> Everything you can look at is above everything you have to read, and the
> run / config / API material is gathered under one **Reference** heading at the
> bottom — so a command spotted in a screenshot has one place to go and look it
> up. Those tables are set smaller, because they are for looking things up in
> rather than reading through.
>
> ### Verification
>
> 380 tests green. Screens regenerated for iOS and Android, the watch for
> watchOS, and the desktop console for macOS and Windows.
>
> ### Install
>
> Download the installer for your OS from the assets below (built by the
> `desktop-release` workflow from the `app-v0.3.3` tag), or run `python -m jim`.
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Agent status light: the ambient watch face, the Agents screen, the overlay by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/104
> * Release 0.3.3, and a README that leads with the screens by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/105
> * v0.4.0 — membership, the corner pane, and a line no plan stands on by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/106
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.3.2...app-v0.4.0

## app-v0.3.2 — app-v0.3.2

- Published: 2026-07-27
- Commit: `6250aaa3c5d31e35f5507521716cb50f6e696e5a`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.3.2>

> **JIM-mini v0.3.2** — **no functional change to JIM-mini in this release**: no new
> routes, no schema, no behaviour. The version moves because the three products
> are cut as one release, and a number naming one combination of three is only
> useful if it never skips one. One of three interoperating products (with
> [qrme](https://github.com/davidsbianchi1984/qrme) and [pdi](https://github.com/davidsbianchi1984/pdi)).
>
> ### What changed in the siblings
>
> **QRME's starter collection stopped looking like a directory.** Each of the 34
> profiles is now shown as the card the app actually gives it — the avatar bubble,
> the role, the rating people left, skill chips, Memory / Relationships /
> Engagement, a career, a review, and a Talk-to button — two columns wide, so a
> phone stops slicing the fourth column mid-word.
>
> And the one starter that had no source material at all now has a Field Pack of
> its own. The age wall on that profile governs who may talk to her; it had been
> quietly read as a reason for her to know less about her own subject.
>
> ### Verification
>
> 380 tests green — **the same 380, passing the same way**, which is the
> point of a release claiming no functional change. 103 routes, also
> unchanged. Version strings moved in exactly five places: `pyproject.toml`, the
> FastAPI app, `app/package.json`, and the two root entries in its lockfile
> (dependency versions untouched).
>
> ### Install
>
> Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
> `python -m jim` from source and pick your device — see the [README](README.md). Installers are signed
> only if signing secrets are configured; otherwise they are unsigned (see
> [docs/releasing.md](docs/releasing.md)).
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Release prep v0.3.2 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/103
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.3.1...app-v0.3.2

## app-v0.3.1 — JIM-mini app-v0.3.1

- Published: 2026-07-26
- Commit: `564b83552b9994bf9b70f02b9108802dc6a3c2ab`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.3.1>

> **JIM-mini v0.3.1** — **no functional change to JIM-mini in this release**: no
> new routes, no schema, no behaviour. A documentation round. One of three
> interoperating products (with [qrme](https://github.com/davidsbianchi1984/qrme)
> and [pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at
> this version.
>
> ### Changed
>
> **The README names its release, and says what each one added.** It opened on a
> video and a patent notice and never stated a version, so a reader could not tell
> which release they were looking at or what had happened across thirteen of them.
> The changelog had it all; the changelog is not where somebody lands. There is now
> a release table, newest first.
>
> The same section went into all three repositories, which is the point — the three
> are cut as one release, so a reader arriving at any of them should be able to
> answer that question the same way.
>
> ### Fixed
>
> **Screens 61–64 existed in the repository and nowhere a reader would find them.**
> They shipped in 0.3.0 as files — *What Would Be Shared*, *Specialist Working*,
> *Find a Clinician*, *Sign to Release* — and were never added to the README
> gallery. The four screens illustrating that round's headline feature were
> invisible on the page describing it.
>
> ### What changed in the siblings
>
> - **QRME** — the starter profiles stopped answering from tone alone. All 34
>   shipped with zero source material while the packs matching them sat unused in
>   the marketplace; seeding now grounds each one in its own industry pack, as part
>   of the repair path so existing deployments catch up by re-running.
> - **PDI** — no functional change either, and it records a known gap in its own
>   changelog rather than leaving it silent.
>
> ### Verification
>
> 380 tests green — **the same 380, passing the same way**, which is the point of a
> release claiming no functional change. 103 routes, also unchanged. Version
> strings moved in exactly five places: `pyproject.toml`, the FastAPI app,
> `app/package.json`, and the two root entries in its lockfile (dependency versions
> untouched).
>
> ### Install
>
> Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
> `python -m jim` from source and pick your device — see the [README](README.md). Installers are signed
> only if signing secrets are configured; otherwise they are unsigned (see
> [docs/releasing.md](docs/releasing.md)).
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Release prep v0.4.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/101
> * Renumber this release 0.3.1, not 0.4.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/102
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.3.0...app-v0.3.1

## app-v0.3.0 — app-v0.3.0

- Published: 2026-07-26
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.3.0>

> **JIM-mini v0.3.0** — the release where the Guardian reaches a person. It could
> delegate a condition to a synthetic specialist; now it can hand over a task that
> outlives the app being closed, and find a **real clinician** near the user. One
> of three interoperating products (with
> [qrme](https://github.com/davidsbianchi1984/qrme) and
> [pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
> version.
>
> ### Highlights
>
> - **Reaching a real clinician** (`jim/referral.py`). Maps a condition to a care
>   area, finds clinicians near the user, and asks QRME to assemble the summary
>   and raise the signature that would release it.
>
>   **JIM never holds the credential and never relays the assertion.** The
>   signature is against *QRME's* relying party, over a challenge QRME minted, so
>   the Face ID prompt belongs to QRME and the assertion travels from the user's
>   device to QRME directly. A guardian product that could mint the consent for
>   releasing its own user's health record would be exactly the wrong shape, and
>   standing in the middle of the one exchange that proves the user was present
>   would defeat the point of collecting it. JIM stores a handle — not the
>   summary, the signature, or the link — and a test asserts the transcript never
>   reaches its database.
>
>   **Locality is a town, not a position.** `sources` already carries a consented
>   `location` feed and this deliberately does not read it: live position is a
>   stream, and matching a clinic needs a place name. Typing "Leeds" once is a
>   smaller disclosure than a product inferring it continuously.
>
> - **Handing a specialist a task, not a turn** (`jim/handoff.py`). Tandem
>   guidance sends one message and gets one reply — right for *"say something
>   supportive"*, wrong for *"read what we have, draft the summary, hold it until
>   somebody confirms"*. QRME runs the second as a workflow; this is JIM's side.
>
>   **Never on the emergency path.** `escalation.decide` resolves in one call and
>   must keep doing so — multi-step work is by definition slower than the thing it
>   would be blocking. Nothing here is reachable from `monitor`, and starting one
>   is explicit: a detection can *warrant* a handoff, a person starts it.
>
>   JIM keeps the task's **status only**. The drafts stay in QRME under its own
>   moderation and the user's capability token; mirroring them here would quietly
>   make JIM a second store of somebody's generated health correspondence.
>
> - **Contribution preview and revoke** (`jim/contribution.py`). The settings
>   screen has offered *"Contribute data — preview before it leaves"* since the
>   cloud tier shipped, and **the API could do neither half**: `cloud.contribute`
>   posted a payload, returned a bool, and wrote nothing down. There was nothing
>   to preview, and consent described as *revocable* meant only *stoppable*.
>
>   **One payload builder, used by both paths** — the preview calls the same
>   function the real send calls. A preview assembled separately is a
>   *description* of the payload, and descriptions drift from what they describe.
>   A refused post is not logged, because that would offer a revoke button for
>   data that never left; and revoke reports its local and gateway halves
>   separately, because a gateway that cannot be reached must neither fail the
>   button nor let JIM claim a deletion that did not happen.
>
> ### Screens
>
> **61 · What Would Be Shared** (every line a real field of the payload),
> **62 · Specialist Working**, **63 · Find a Clinician**, **64 · Sign to Release**.
>
> ### Verification
>
> 346 tests green (34 new this release). 96 routes. 128 screens. Mutation-checked:
> logging a refused send, claiming gateway deletion regardless of the answer, and
> treating an empty phase intersection as a startable task each fail the test that
> forbids them.
>
> ### Install
>
> Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
> `python -m jim` from source and pick your device — see the [README](README.md). Installers are signed
> only if signing secrets are configured; otherwise they are unsigned (see
> [docs/releasing.md](docs/releasing.md)).
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Contribution preview and revoke; hand a specialist a task by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/96
> * Reach a real clinician through the tandem by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/97
> * Release prep v0.3.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/98
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.2.2...app-v0.3.0

## app-v0.2.2 — app-v0.2.2

- Published: 2026-07-26
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.2.2>

> **JIM-mini v0.2.2** — a documentation release. **No code changed**: no new
> routes, no schema, no behaviour, and nothing about how the Guardian decides
> anything. Everything here corrects something that was *described* wrongly. One
> of three interoperating products (with
> [qrme](https://github.com/davidsbianchi1984/qrme) and
> [pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
> version.
>
> ### Fixed
>
> - **Three releases of changelog links were missing.** `[0.1.9]`, `[0.2.0]` and
>   `[0.2.1]` had headings but no link definitions, so three shipped versions
>   rendered as literal `[0.2.1]` bracket text rather than linking to their
>   releases, and `[Unreleased]` still compared against `app-v0.1.8` —
>   presenting a three-release diff as though it were an empty one.
>
> - **The release checklist is why that kept happening**, and is the entry that
>   matters. `docs/releasing.md` step 1 said to move the `Unreleased` items under
>   the new heading and date it, and stopped — it never mentioned the link
>   definition at the bottom of the file. The step was skipped three releases
>   running by someone following the instructions correctly, and nothing
>   complains when you miss it: the heading renders fine without a definition,
>   and the damage appears hundreds of lines from where the edit was made.
>
>   Step 2 was wrong in the same direction. It named `pyproject.toml` and
>   `app/package.json` when the version string lives in **five** places — the two
>   it omitted being the `FastAPI(...)` call in `jim/api.py` and the second root
>   entry in `app/package-lock.json`, both of which had to be rediscovered each
>   round. Both steps now say what they meant.
>
>   The `0.1.5` and `0.1.6` entries still point at commits rather than tags.
>   That is deliberate and explained in `docs/releasing.md`; they are untouched.
>
> ### What changed in the siblings
>
> - **QRME** — `POST /marketplace/seed` still advertised itself as *"Idempotent —
>   already-seeded profiles are skipped"* after v0.2.1 taught it to **repair**
>   too, so the text in the OpenAPI docs pointed away from the one call that
>   fixes a deployment showing bare initials instead of portraits. Corrected in
>   four places.
>
> - **PDI** — the same checklist and changelog-link corrections as here.
>
> ### Verification
>
> 312 tests green — **the same 312, passing the same way**, which is the point of
> a release that claims no functional change. 87 routes, also unchanged. Version
> strings moved in exactly five places: `pyproject.toml`, the FastAPI app,
> `app/package.json`, and the two root entries in its lockfile (dependency
> versions untouched). Every version heading in the changelog was checked against
> its link definition — 12 for 12.
>
> ### Install
>
> Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
> `python -m jim` from source and pick your device — see the [README](README.md). Installers are signed
> only if signing secrets are configured; otherwise they are unsigned (see
> [docs/releasing.md](docs/releasing.md)).
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Fix the changelog release links and the checklist that lost them by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/94
> * Release prep v0.2.2 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/95
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.2.1...app-v0.2.2

## app-v0.2.1 — app-v0.2.1

- Published: 2026-07-26
- Commit: `e41153364e56bdaf448a0d57cf64ea4342d9fb09`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.2.1>

> **JIM-mini v0.2.1** — the release where the Guardian stops treating every
> reading as a fact. One of three interoperating products (with
> [qrme](https://github.com/davidsbianchi1984/qrme) and
> [pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
> version.
>
> ### Highlights
>
> - **How much to trust a reading** (`jim/signal.py`). `escalation.decide` has
>   always accepted a `confidence`, but **only forecasts ever supplied one** — it
>   gated *predictions* and never *measurements*, so a reading was a fact by
>   virtue of arriving.
>
>   Consumer biometrics are not like that. An optical sensor loses skin contact,
>   a chest strap catches a motion artifact, and the characteristic failure is not
>   a small error but a plausible-looking number that is completely wrong, with
>   the alarming direction as likely as the reassuring one. At the top of this
>   ladder is a phone call to somebody's daughter, and an alert that is usually
>   wrong spends the only thing escalation has: her willingness to pick up.
>
> - **Confidence drops only on evidence the *sensor* misbehaved** — an impossible
>   value, a jump no body could make between two readings, or the device reporting
>   its own poor contact. Being clinically abnormal never lowers it.
>
>   That distinction is the whole design, and it was learned the hard way: the
>   first draft graded anything outside the ordinary range as suspect, which muted
>   a lone SpO2 of 84 — the exact reading the ladder exists to carry. A
>   pre-existing test caught it.
>
> - **A poor grade caps rather than silences.** Escalation stops at `check_in`:
>   *"we got an odd reading, are you alright?"* is the honest sentence when the
>   honest answer is that we do not know, and asking is also how the reading gets
>   corroborated. Dropping the sample would be the same mistake pointed the other
>   way, because the noisy reading is sometimes real.
>
> - **Words are never noise.** The crisis floor is applied after the cap and is
>   never clipped by it. Nor can words make a heart rate of zero true: two
>   impossible readings are not two witnesses but one broken device agreeing with
>   itself. A fault is phrased as a fault — *check the strap* — because telling
>   somebody whose sensor fell off that we are worried about them is how people
>   learn to disbelieve the thing.
>
> ### Fixed
>
> - **The escalation decision was advisory; raw severity was in charge.**
>   `monitor` reached out whenever `severity == "critical"`, so the tree could
>   resolve a disbelieved reading to `check_in` and the emergency contact was rung
>   anyway. The tree is authoritative now. No behaviour changes for a trusted
>   critical — its floor is `notify_contact`, so the comparison is exactly
>   equivalent — and a test asserts that directly.
>
> - **A rota typo cannot take the escalation path down.** `RotaError`'s docstring
>   said *"raised at load, never at 3am"*, but nothing reads the rota at start-up,
>   so it was raised at exactly 3am: one typo turned `POST …/escalate` into a 500.
>   It degrades to the flat names now and says so loudly.
>
> ### Verification
>
> 312 tests green (19 new this release). 87 routes. Mutation-checked: letting the
> confidence cap clip the crisis floor, and letting an impossible reading be
> corroborated, each fail the test that forbids them.
>
> ### Install
>
> Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
> `python -m jim` from source and pick your device — see the [README](README.md). Installers are signed
> only if signing secrets are configured; otherwise they are unsigned (see
> [docs/releasing.md](docs/releasing.md)).
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * How much to trust a reading by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/92
> * Release prep v0.2.1 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/93
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.2.0...app-v0.2.1

## app-v0.2.0 — app-v0.2.0

- Published: 2026-07-25
- Commit: `c9d5ac08da7626f91b4c71c9cf45ab40dffeb23c`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.2.0>

> **JIM-mini v0.2.0** — the minor bump, and honestly: **there are no functional
> changes to JIM-mini in this release.** The three products version as one, and
> this round's work was next door. One of three interoperating products (with
> [qrme](https://github.com/davidsbianchi1984/qrme) and
> [pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at
> this version.
>
> ### Why 0.2.0 rather than 0.1.10
>
> The 0.1.x line ran from a Guardian that monitored and escalated, to one with a
> life layer, an escalation ceiling a stranger's tap cannot raise, care beacons
> on the objects around a watched person, a workplace relay for lone workers, a
> rota that knows who is actually on at 2am, and an escalation that reaches a
> human rather than writing a name in a table. That is a different product from
> 0.1.0, and 0.1.10 would have undersold it.
>
> ### What changed here
>
> - **Only one workflow writes the release body now.** `desktop-release.yml`
>   published `RELEASE_NOTES.md` **verbatim** — *"Ready-to-paste body for the
>   GitHub Release…"* preamble and all — while `sync-release-notes.yml` published
>   the same file with that preamble stripped. Both fired on the same tag push;
>   the sync finished in six seconds and the installer build finished two to four
>   minutes later and overwrote it. The build always won, so every release since
>   the sync workflow existed shipped the preamble until somebody re-ran the sync
>   by hand. The build no longer sets a body at all, and the sync now waits for
>   it rather than racing it.
>
> ### What changed in the siblings
>
> - **PDI** — a per-tenant on-call roster, closing the gap this repo's own
>   `jim/rota.py` had left visible next door. `PDI_GATE_ONCALL` was one name for
>   the whole deployment, which in a multi-tenant vault routed every customer's
>   courier to the same person.
> - **QRME** — nothing of its own this round.
>
> ### Verification
>
> 297 tests green — the same 297, passing the same way, which is the point of a
> release that claims no functional change here. 87 routes. Version strings moved
> in exactly five places: `pyproject.toml`, the FastAPI app, `app/package.json`,
> and the two root entries in its lockfile (dependency versions untouched).
>
> ### Install
>
> Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
> `python -m jim` from source and pick your device — see the [README](README.md). Installers are signed
> only if signing secrets are configured; otherwise they are unsigned (see
> [docs/releasing.md](docs/releasing.md)).
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Only one workflow writes the release body now by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/90
> * Release prep v0.2.0 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/91
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.1.9...app-v0.2.0

## app-v0.1.9 — app-v0.1.9

- Published: 2026-07-25
- Commit: `59845161b7d48bd42e5b592fd3421f0d0d515d30`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.1.9>

> **JIM-mini v0.1.9** — the release where the workplace relay learns who is
> actually on shift, and where "notified" stops meaning "written down". One of
> three interoperating products (with
> [qrme](https://github.com/davidsbianchi1984/qrme) and
> [pdi](https://github.com/davidsbianchi1984/pdi)), all three cut together at this
> version.
>
> ### Highlights
>
> - **A rota, because a flat list pages the day person at 2am.**
>   `JIM_SITE_ROSTER` was a list of names worked top to bottom, every time, and
>   `relay.py`'s own comment defended that as a deliberate limit — *a rota with
>   shift patterns is a scheduling product*. Honest, but wrong about the size of
>   the gap. The relay exists for **night shift**: lone workers, plant rooms,
>   single-staffed sites. Getting *who is on right now* wrong at 3am is not a
>   degraded feature, it is the feature failing in the hour it was built for.
>
> - **`JIM_SITE_ROTA` is deliberately small.** Named people, the days they work,
>   the hours, and `JIM_SITE_TZ`. No leave, no swaps, no fairness, no recurrence
>   grammar. Three things it does get right, because each is a way of paging the
>   wrong person:
>
>   - **Shifts cross midnight.** `18:00–06:00` is the shift this is all about,
>     and `start <= now <= end` is false for every minute of it. A wrapping shift
>     is two intervals and belongs to the day it *started*: at 02:00 on Saturday
>     it is Friday's night worker on the floor, not the weekend rota.
>   - **A site is somewhere.** Without a timezone a rota written in local time is
>     evaluated in UTC, shifting every boundary by the offset — and by a
>     *different* offset in summer, so it would look correct for half the year.
>     An unrecognised zone is named in `GET /relay/roster`'s `warning` rather than
>     silently treated as UTC.
>   - **A rota has gaps.** Nobody rostered at 4am on a bank holiday is a real
>     state. The relay works the whole rota — better to wake the wrong person than
>     nobody — and reports `on_shift: false` on the escalation *and in the page
>     itself*, so whoever it wakes knows they were a guess.
>
>   `GET /relay/rota` answers *who would you page right now?* in the afternoon,
>   rather than leaving it to be discovered at 3am. `JIM_SITE_ROSTER` still works
>   and still means plain names, always on — a test asserts the old configuration
>   is unchanged.
>
> - **And `escalate` now sends something.** "Notified" meant a row in `events`
>   saying somebody had been notified, while nothing had left the building — so
>   the loop the relay is built around, *keep going until a human accepts*, could
>   never close on its first step. JIM posts a signed envelope to
>   `JIM_NOTIFY_URL` and stops; the SMS gateway or pager behind it is the
>   deployment's, and the envelope matches PDI's shape so one receiver can take
>   both. An unreachable responder sets `reached_somebody: false` **and**
>   `escalate_again_now`, because *waiting on a human* and *waiting on a human who
>   was never told* need different next moves, and only the first should wait.
>
> - **Incident scope survives the trip out of the building.** A webhook is the
>   easiest place in the system to turn an incident into a health record — *"just
>   add the name so they know who to look for"* is a reasonable-sounding sentence
>   that would undo the whole promise. So the envelope is built by copying named
>   fields *out* of `relay.incident`, never by stripping fields from a user
>   record, and not even the finder's words go out. A test reads the whole
>   envelope as one string and looks for the name, birthdate, contact number,
>   resting rate and the finder's message in it.
>
> - **The ceiling did not move.** A notification channel is not a siren. A test
>   runs the rota to exhaustion to prove `notify_contact` still caps it, and that
>   the relay still refuses to call emergency services on anyone's behalf.
>
> - **A config typo cannot take the escalation path down.** `RotaError`'s own
>   docstring claimed it was *"raised at load, never at 3am"* — but nothing reads
>   the rota at start-up, so it was raised at exactly 3am. One typo (`"funday"`
>   for `"sunday"`) turned `POST …/escalate` into a 500, on the one path whose
>   entire job is getting somebody help, and only once an alarm was already open.
>   It degrades to the flat names now and says so loudly, while the surface an
>   operator uses to *check* a rota stays strict.
>
> - **The tandem doc was describing a past release.** This copy listed the suite
>   gateway's erase, export, consent and metering as `[planned]` when
>   `suite/gateway.py` had shipped them — a reader here was told cross-app
>   deletion did not exist. [docs/tandem.md](docs/tandem.md) is now identical
>   byte-for-byte in all three repos, with new sections for the arrow that runs
>   out of PDI into QRME, the beacon family across all three products, and the
>   notification channel — the one thing the suite genuinely cannot supply for
>   itself. `docs/diagrams/tandem-flow.svg` is generated rather than hand-drawn.
>
> ### Verification
>
> 297 tests green (24 new this release). 87 routes. Version strings moved in
> exactly five places: `pyproject.toml`, the FastAPI app, `app/package.json`, and
> the two root entries in its lockfile (dependency versions untouched).
>
> ### Install
>
> Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
> `python -m jim` from source and pick your device — see the [README](README.md). Installers are signed
> only if signing secrets are configured; otherwise they are unsigned (see
> [docs/releasing.md](docs/releasing.md)).
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * sync-release-notes: read the tag's notes, and stop duplicating What's Changed by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/82
> * Design care beacons and the workplace relay by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/81
> * Build care beacons and the workplace relay by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/83
> * README: lead with the Guardian teaser video by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/85
> * Generate the four README illustrations instead of hand-building them by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/84
> * A phone that scans a care beacon gets a page, not JSON by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/86
> * A rota that knows who is on, an escalation that sends, and v0.1.9 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/87
> * A rota typo must not take down the escalation path by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/88
> * Screen 60 was advertising the roster this round replaced by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/89
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.1.8...app-v0.1.9

## app-v0.1.8 — app-v0.1.8

- Published: 2026-07-25
- Commit: `0e34713504b3c22ca2e49d4b51a9d06dc4017c05`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.1.8>

> **JIM-mini v0.1.8** — cut alongside QRME and PDI, as the three always
> are now. One of three interoperating products (with
> [qrme](https://github.com/davidsbianchi1984/qrme) and
> [pdi](https://github.com/davidsbianchi1984/pdi)), all three at this
> version.
>
> ### What changed in JIM-mini
>
> **Nothing functional.** No API, no schema, no behaviour moved.
>
> The only change here is a repair to the changelog itself: `[0.1.5]` and
> `[0.1.6]` linked to release tags that were never pushed, so both were 404s.
> They now point at their release-prep commits. Deliberately *not* fixed by
> backfilling those tags — pushing them now would fire the installer build and
> publish two superseded releases dated *after* v0.1.7, at the top of the page
> people download from. [docs/releasing.md](docs/releasing.md) records that
> reasoning, because an unexplained gap in a tag sequence is exactly what someone
> later "fixes" without knowing why it was left.
>
> **If you are already running 0.1.7, this upgrade is optional.** Take it to keep
> the three products reporting matching versions; skip it and you lose nothing.
>
> ### What is in the suite at 0.1.8
>
> The substance is QRME's: a live desk stops being only something you watch. You
> can ask to come up on the stream — which the host has to grant, and which needs
> a verified adult on a rated desk — and the room's comments, likes, shares and
> gifts render *on* the picture rather than beside it. See
> [QRME's notes](https://github.com/davidsbianchi1984/qrme/releases). Nothing in
> it asked JIM-mini to change.
>
> ### Verification
>
> 240 tests green — the same 240, passing the same way, which is rather the
> point of a release that claims to change nothing functional. Version strings
> moved in exactly five places: `pyproject.toml`, the FastAPI app,
> `app/package.json`, and the two root entries in its lockfile (dependency
> versions untouched).
>
> ### Install
>
> Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
> `python -m jim` from source and pick your device — see the [README](README.md). Installers are signed
> only if signing secrets are configured; otherwise they are unsigned (see
> [docs/releasing.md](docs/releasing.md)).
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Point the untagged versions at commits, not missing releases by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/79
> * Release prep v0.1.8: version bumps, changelog cut, release notes by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/80
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.1.7...app-v0.1.8

## app-v0.1.7 — JIM-mini app-v0.1.7

- Published: 2026-07-25
- Commit: `300c2aa2ffce1b4c182b32b6a204b1125c919f37`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.1.7>

> **JIM-mini v0.1.7** — the first release cut under the new rule that the three
> products ship as one. One of three interoperating products (with
> [qrme](https://github.com/davidsbianchi1984/qrme) and
> [pdi](https://github.com/davidsbianchi1984/pdi)), all three at this
> version.
>
> ### What changed in JIM-mini
>
> **Documentation only. No API, no schema, no behaviour change.**
>
> [docs/releasing.md](docs/releasing.md) now records how the three products are
> released, so the next round does not have to rediscover it:
>
> - **They are versioned as one release** — same number, same pass, even when a
>   repository has nothing of its own to ship that round.
> - **A repository with nothing to ship still cuts, and says so** in those words.
>   A note that inflates an empty round teaches people to skim the ones that are
>   not empty.
> - **Tag the release-prep commit, not the tip of `main`.** Work keeps landing
>   while a release is cut, and anything arriving after the changelog is
>   sectioned belongs under `[Unreleased]` rather than to the version being
>   tagged.
>
> That last rule is written down because it already nearly bit: QRME's v0.1.6 tag
> point sits behind its `main`, and tagging the tip would have published features
> under notes that do not mention them.
>
> Through v0.1.5 each repository cut whenever it happened to have work, so the
> numbers matched only by coincidence — which is how QRME reached 0.1.6 alone
> while this one sat at 0.1.5. v0.1.6 aligned them by hand; this is the first
> round where the alignment is the process rather than a correction.
>
> **If you are already running 0.1.6, this upgrade is optional.** Take it to keep
> the three products reporting matching versions; skip it and you lose nothing.
>
> ### What is in the suite at 0.1.7
>
> The substance this round is QRME's: live desks left behind as printed codes, a
> full audience layer (like, comment, share, subscribe), and a marketplace that
> can finally take payments. See
> [QRME's notes](https://github.com/davidsbianchi1984/qrme/releases). Nothing in
> it asked JIM-mini to change.
>
> ### Verification
>
> 240 tests green — the same 240, passing the same way, which is rather the
> point of a release that claims to change nothing functional. Version strings
> moved in exactly five places: `pyproject.toml`, the FastAPI app,
> `app/package.json`, and the two root entries in its lockfile (dependency
> versions untouched).
>
> ### Install
>
> Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
> `python -m jim` from source and pick your device — see the [README](README.md). Installers are signed
> only if signing secrets are configured; otherwise they are unsigned (see
> [docs/releasing.md](docs/releasing.md)).
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * sync-release-notes: publish the release body from RELEASE_NOTES.md by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/71
> * Published deployments: pairing knows its public URL, optional signup key by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/72
> * Deployable as one container: Dockerfile builds the console, docs/hosting.md by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/73
> * Compile the native apps in CI, and fix two defects it makes visible by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/74
> * Release prep v0.1.5 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/75
> * Align the version with the suite: v0.1.6 by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/76
> * Write down the release convention: the three cut together by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/77
> * Release prep v0.1.7: version bumps, changelog cut, release notes by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/78
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.1.4...app-v0.1.7

## app-v0.1.4 — JIM-mini v0.1.4

- Published: 2026-07-24
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.1.4>

> **JIM-mini (Guardian) v0.1.4** — run it your way: one command prints
> every way to run the Guardian and you pick the device — your phone (scan
> a QR straight off the terminal), this PC, a packaged installer, or the
> headless API. One of three interoperating products (with
> [qrme](https://github.com/davidsbianchi1984/qrme) and
> [pdi](https://github.com/davidsbianchi1984/pdi)).
>
> ### Highlights
>
> - **`python -m jim` — the launcher menu** — every way to run the Guardian,
>   one command each, so you choose per device: `phone` (the QR flow
>   below), `desktop` (the Electron app on this PC), the packaged installer
>   (no toolchain needed), or `serve` (the headless API alone). Same
>   backend, same data, same token checks behind every door.
> - **`python -m jim phone` — the whole phone setup in one command** —
>   builds the console if it's missing (first-run `npm install` included),
>   prints the pairing URL **with a QR code drawn straight into the
>   terminal**, and serves on your local network. Scan, Add to Home
>   Screen, done.
> - **The Guardian on your phone** — the API serves the built console at `/app`
>   (one origin for UI and API — nothing to configure on the phone);
>   `GET /pair` returns the URL on your local network with a scannable QR,
>   and the Guardian installs to the home screen as a standalone app with a
>   thumb-reachable bottom tab bar. Local network only, by design; the
>   service worker never caches API traffic, so monitoring and guidance are
>   always live.
> - **Terms of Service** — docs/terms.md (v1.0) leads with the section that
>   matters most: JIM is a wellness tool, **not a medical device** — call
>   911 first, 988 in crisis, and detection can be wrong in both
>   directions. Assumption of risk and release, the robot-resuscitation
>   boundary (fully autonomous resuscitation still requires the separate
>   signed waiver, never for a minor, and a robot never delivers the
>   shock), parent/guardian enrollment, warranty disclaimer, and liability
>   cap. Served versioned at `GET /terms`; enrollment records the accepted
>   version + timestamp on the account, and the native welcome screens
>   carry the clickwrap notice.
> - **Signed, notarized builds wired** — hardened runtime + entitlements +
>   notarization in the electron-builder config: adding the Apple/Windows
>   signing secrets produces Gatekeeper-clean, SmartScreen-friendly
>   installers. docs/releasing.md walks through obtaining the certificates.
> - **HIPAA posture** — docs/hipaa-baa.md now points at the signable BAA
>   template maintained in the PDI repo, where the vault enforces it in
>   code before any HIPAA-program work.
>
> ### Verification
>
> 228 tests green; live-server smoke flows pass; the desktop app builds
> clean; the cross-product suite smoke (run from qrme) passes end to end.
>
> ### Install
>
> Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
> `python -m jim` from source and pick your device — see the [README](README.md). Installers are signed
> only if signing secrets are configured; otherwise they are unsigned (see
> [docs/releasing.md](docs/releasing.md)).
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md

## app-v0.1.3 — JIM-mini v0.1.3

- Published: 2026-07-24
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.1.3>

> **JIM-mini (Guardian) v0.1.3** — the trust release: real Terms of Service
> with a recorded receipt, and signed/notarized build wiring. One of three
> interoperating products (with
> [qrme](https://github.com/davidsbianchi1984/qrme) and
> [pdi](https://github.com/davidsbianchi1984/pdi)).
>
> ### Highlights
>
> - **Run it on your phone** — the API serves the built console at `/app`
>   (one origin for UI and API — nothing to configure on the phone);
>   `GET /pair` returns the URL on your local network with a scannable QR,
>   and the Guardian installs to the home screen as a standalone app with a
>   thumb-reachable bottom tab bar. Local network only, by design; the
>   service worker never caches API traffic, so monitoring and guidance are
>   always live.
> - **Terms of Service** — docs/terms.md (v1.0) leads with the section that
>   matters most: JIM is a wellness tool, **not a medical device** — call
>   911 first, 988 in crisis, and detection can be wrong in both
>   directions. Assumption of risk and release, the robot-resuscitation
>   boundary (fully autonomous resuscitation still requires the separate
>   signed waiver, never for a minor, and a robot never delivers the
>   shock), parent/guardian enrollment, warranty disclaimer, and liability
>   cap. Served versioned at `GET /terms`; enrollment records the accepted
>   version + timestamp on the account, and the native welcome screens
>   carry the clickwrap notice.
> - **Signed, notarized builds wired** — hardened runtime + entitlements +
>   notarization in the electron-builder config: adding the Apple/Windows
>   signing secrets produces Gatekeeper-clean, SmartScreen-friendly
>   installers. docs/releasing.md walks through obtaining the certificates.
> - **HIPAA posture** — docs/hipaa-baa.md now points at the signable BAA
>   template maintained in the PDI repo, where the vault enforces it in
>   code before any HIPAA-program work.
>
> ### Verification
>
> 224 tests green; live-server smoke flows pass; the desktop app builds
> clean; the cross-product suite smoke (run from qrme) passes end to end.
>
> ### Install
>
> Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
> the backend from source — see the [README](README.md). Installers are signed
> only if signing secrets are configured; otherwise they are unsigned (see
> [docs/releasing.md](docs/releasing.md)).
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Run the Guardian from your phone: served console, pairing, installable PWA by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/67
> * Release prep v0.1.3: version bumps, changelog cut, release notes by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/68
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.1.2...app-v0.1.3

## app-v0.1.2 — JIM-mini v0.1.2

- Published: 2026-07-24
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.1.2>

> **JIM-mini (Guardian) v0.1.2** — the trust release: real Terms of Service
> with a recorded receipt, and signed/notarized build wiring. One of three
> interoperating products (with
> [qrme](https://github.com/davidsbianchi1984/qrme) and
> [pdi](https://github.com/davidsbianchi1984/pdi)).
>
> ### Highlights
>
> - **Terms of Service** — docs/terms.md (v1.0) leads with the section that
>   matters most: JIM is a wellness tool, **not a medical device** — call
>   911 first, 988 in crisis, and detection can be wrong in both
>   directions. Assumption of risk and release, the robot-resuscitation
>   boundary (fully autonomous resuscitation still requires the separate
>   signed waiver, never for a minor, and a robot never delivers the
>   shock), parent/guardian enrollment, warranty disclaimer, and liability
>   cap. Served versioned at `GET /terms`; enrollment records the accepted
>   version + timestamp on the account, and the native welcome screens
>   carry the clickwrap notice.
> - **Signed, notarized builds wired** — hardened runtime + entitlements +
>   notarization in the electron-builder config: adding the Apple/Windows
>   signing secrets produces Gatekeeper-clean, SmartScreen-friendly
>   installers. docs/releasing.md walks through obtaining the certificates.
> - **HIPAA posture** — docs/hipaa-baa.md now points at the signable BAA
>   template maintained in the PDI repo, where the vault enforces it in
>   code before any HIPAA-program work.
>
> ### Verification
>
> 217 tests green; live-server smoke flows pass; the desktop app builds
> clean; the cross-product suite smoke (run from qrme) passes end to end.
>
> ### Install
>
> Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
> the backend from source — see the [README](README.md). Installers are signed
> only if signing secrets are configured; otherwise they are unsigned (see
> [docs/releasing.md](docs/releasing.md)).
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * macOS notarization wiring + link the signable BAA template by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/64
> * Terms of Service: served, accepted at enrollment, recorded with a receipt by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/65
> * Release prep v0.1.2: version bumps, changelog cut, release notes by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/66
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.1.1...app-v0.1.2

## app-v0.1.1 — app-v0.1.1

- Published: 2026-07-24
- Commit: `main`
- Assets: 5
- Page: <https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.1.1>

> **JIM-mini (Guardian) v0.1.1** — the Guardian gets hands, a family, and
> provable custody. One of three interoperating products (with
> [qrme](https://github.com/davidsbianchi1984/qrme) and
> [pdi](https://github.com/davidsbianchi1984/pdi)).
>
> ### Highlights
>
> - **Native apps at parity** — iOS, Android, and Windows now carry the whole
>   Guardian: Care (Monitor / Check-in / Coach / Family), Life (goals, habits,
>   journal), Safety (SOS, escalation policy, robots, Medical ID), Connect,
>   Vault Custody, and the model picker.
> - **Robots as first-aid responders** — catalog robots bind as guardian
>   responders with escalation directives. Assist-rated platforms fetch the
>   AED and coach the playbook aloud; perform-rated platforms may deliver
>   chest compressions only after a person on scene confirms. **Fully
>   autonomous resuscitation stays locked behind a signed liability waiver
>   that can never be signed for a minor.**
> - **Emergency, end to end** — predictive early warning, a transparent
>   escalation decision tree, and the one-tap Emergency flow: reach services,
>   share location, alert family, surface the Medical ID QR, deliver AI first
>   aid, ping every device.
> - **Family** — parent-led child accounts with recorded (PDI-sealed) consent,
>   age-scaled oversight that ends by itself at 18, pause/quiet hours that
>   never hold safety, and one light per child on the parent's wrist.
> - **Provable custody** — tandem specialist exchanges sealed into the PDI
>   vault with a custody viewer and provenance; the mental-health trio routes
>   through live QRME personas while crisis escalation stays local.
> - **Language everywhere** — per-user language with hand-translated safety
>   content in all supported languages, gateway choice, translate-anything,
>   and guidance provenance with published sources. Chrome localization covers
>   the apps' own labels in all 10 languages.
> - **In-app feedback** — a "Help us improve" section on every client.
>
> ### Verification
>
> 215 tests green; live-server smoke flows pass; the desktop app builds clean;
> the cross-product suite smoke (run from qrme) passes end to end.
>
> ### Install
>
> Download the installer for your OS below (`.dmg` / `.exe` / `.AppImage`), or run
> the backend from source — see the [README](README.md). Installers are signed
> only if signing secrets are configured; otherwise they are unsigned (see
> [docs/releasing.md](docs/releasing.md)).
>
> **Full changelog:** https://github.com/davidsbianchi1984/jim-mini/blob/main/CHANGELOG.md
>
>
> ## What's Changed
> * Add Apple/Google/email Log In screen by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/27
> * Add first-run onboarding flow (Permissions → About You → Contacts → All Set) by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/28
> * Record post-0.1.0 onboarding screens in the changelog by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/29
> * Social connections: collect posts into guidance, publish via QR beacon by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/31
> * Support all 16 connection platforms from the suite set by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/32
> * Connected-apps catalog: Apple, Google, Microsoft & Canva connectors by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/33
> * App connectors: connect a catalog app and use it (collect · act · produce) by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/34
> * Safe knowledge excursions: study a topic without leaking the user's PHI by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/35
> * Scaffold native iOS, Android and Windows apps for JIM Guardian by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/30
> * Add Knowledge Excursions screen (49) by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/36
> * Add simple Files & Photos device-connector screen (50) by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/37
> * Add per-assistant screens: Apple Intelligence, Google Gemini, Microsoft Copilot by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/38
> * Grow JIM native apps: Coach + Life (goals/habits/journal) screens by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/39
> * Let users pick their LLM provider (Claude/OpenAI/Grok/Perplexity/Gemini) by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/40
> * Predictive early warning + escalation decision tree + Emergency flow by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/41
> * Robot helpers as guardian responders (catalog, binding, escalation directives) by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/42
> * Native apps: add Safety (SOS/policy/robots) and the model picker by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/43
> * Native apps: add the Medical ID card to Safety by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/44
> * Native apps: add Connect (sources, social, apps) and fold Care tab by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/45
> * Robots as first-aid responders: rated CPR/AED roles, plus playbook rendering by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/46
> * Autonomous-resuscitation waiver: signed liability waiver unlocks automatic CPR + auto-AED by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/47
> * Per-user language + verifiable guidance provenance by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/48
> * Hand-translate safety content into all supported languages by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/49
> * Language at the setup gateway, translate-anything tool, and delivery modes by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/50
> * Seed starter specialists: a named domain expert per condition by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/51
> * Tandem hookup: wire starter specialists to QRME starter profiles by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/52
> * Native apps: show who stands behind the guidance by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/53
> * Provable custody: seal tandem specialist exchanges in the PDI vault by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/54
> * Custody viewer: sealed-exchange indicators and a provenance window by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/55
> * Tandem trio: route the mental-health conditions through QRME personas by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/56
> * Native custody screen: list every sealed exchange with its proof by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/57
> * Family: a parent sets up and watches over a child's account by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/58
> * Family controls: pause/quiet hours, the parent's wrist, sealed consent by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/59
> * Native family controls + the parent's watch, on every surface by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/60
> * Help us improve: in-app product feedback anyone can send by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/61
> * Chrome localization + polish across the native apps by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/62
> * Release prep v0.1.1: version bumps, changelog & notes by @davidsbianchi1984 in https://github.com/davidsbianchi1984/jim-mini/pull/63
>
>
> **Full Changelog**: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.1.0...app-v0.1.1

