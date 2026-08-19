# Changelog

All notable changes to JIM-mini are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.88.0] - 2026-08-19

### Added

- **The lookout: a page the vault keeps fresh.** PDI's standing tasks
  put to work: "keep an eye on this page" becomes one standing plan
  whose single fetch step re-seals the current capture every cycle —
  the resident does the watching from inside the facility, JIM never
  does, and what leaves JIM is the URL once, at planting. The capture
  reads back through the same authenticated channel every seal uses,
  as a reading (capped) beside the honest size of the seal.

      asked     can JIM watch a page for somebody
      mattered  who does the watching, and where the page lives

  The rules ride along: planting needs the same standing study permit
  the errands do, because the resident leaves its host on this person's
  behalf; writes are plan-gated while the list, the read-back and the
  drop keep the real vault; a drop cancels the appointment first, then
  unseals the capture, then lets the ledger row go — and a tandem that
  cannot be reached leaves the row on the list rather than orphaning a
  standing appointment. Erasure cancels every appointment and unseals
  every capture, counted honestly (`lookouts_cancelled: null` when the
  tandem was unreached). A watched-pages card beside the errands on the
  console and all three shells, in ten languages.

### Fixed

- **Recall keeps the real vault.** The last read still behind the plan
  gate: `coach.reply` used one `pdi` for remembering (a write, rightly
  gated) and for recalling (a read, wrongly gated), so a person who
  moved to an open plan had a shelf that showed their sealed moments and
  a coach that had stopped finding them. The route now hands recall
  `app.state.pdi` while the seal keeps `_vault(user_id)` — the same
  writes-gated split every other memory door already holds — and a
  downgraded account's new turns are honestly not sealed at all.

### Added

- **The voice inside the vault.** A `vault` provider joins the model
  registry: a person picks "The vault's local model (PDI resident)" on
  the existing model screen and the coach's words are generated through
  PDI's new `/resident/infer` door, on the facility's own inference
  server — the prompt travels the one authenticated channel every seal
  uses and goes no further, and PDI's audit line carries its length,
  never its words.

      asked     can the coach speak from inside the building
      mattered  does the prompt ever leave it

  Honest at every edge, and disclosed: a vault with no local model
  raises rather than speaking the resident's operational stub sentence
  in the coach's voice — the turn falls to this product's own stub and
  `generated_by`/`degraded` say who actually answered; an older tandem
  without the door does the same; with no tandem the choice is not
  configured, so a stored preference can never wedge a reply. The
  provider reads the *live* client the app holds, not a startup
  snapshot.

## [0.87.0] - 2026-08-19

### Fixed

- **Deleting a check-in reaches the vault.** `remove_journal` already
  unmade its entry's memory; its twin did not: a person who unrecorded
  how they felt kept a sealed, findable moment the coach could recall
  into a later reply. `DELETE /checkin/{user_id}/{checkin_id}` now takes
  the vector, the seal and the ledger row with the check-in — best-effort
  like the journal's, because a local delete must not depend on a second
  product being up, and what could not be unmade stays covered by the
  user-level erasure door.

      asked     did the check-in leave the record
      mattered  did the moment stop being findable

- **The memory doors use the real vault, not the plan-gated one.** The
  shelf read, the per-moment forget and the journal/check-in deletes went
  through `_vault(user_id)`, which gates on the *plan* — right for every
  seal point, wrong here: somebody who moved to an open plan still has a
  history of sealed moments they must be able to read back and let go of,
  and a delete refused over a billing change would leave records nobody
  can reach and call that forgetting. Writes stay plan-gated; reads and
  deletes now take `app.state.pdi`, the same split QRME's memory doors
  hold.

### Added

- **The memory shelf, shown and curatable.** The coach's long-term memory
  could remember, recall and forget — and the person it was about could
  see none of it. `GET /memory/{user_id}` reads every remembered moment
  back from the vault (kind, the line itself, when), and
  `DELETE /memory/{user_id}/{kind}/{ref}` unmakes one — vector, seal and
  ledger row — with an answer that says what happened, because a forget
  button that fails silently is worse than none. Every derived thing in
  this product has to be visible to the person it was derived from and
  droppable by them: the continuity card has held that rule for the
  attention vector since it shipped, and the shelf now holds it for the
  content, rendered beside it on the console's Settings screen and the
  three shells' self-profile screens, in ten languages. A tandem that
  cannot be reached answers honestly — the moments are listed, their
  words are not — because "I hold twelve memories I cannot show you right
  now" and "I hold nothing" are different answers.

### Fixed

- **Deleting a journal entry now unmakes its memory.** The memory round
  left three things standing after a journal delete: the sealed line, the
  `vault_keys` ledger row, and the embedding vector — so the coach could
  keep reciting an entry the person deleted. `remove_journal` now unmakes
  all three through the tandem, best-effort so the delete never depends
  on a second product being up; whatever could not be unmade stays
  covered by the user-level erasure door. And that door finishes the job
  it already claimed: `delete_user_data` takes every memory vector under
  the person's prefix in one resident call, reports the count in its
  answer — `memory_vectors: null` when the tandem was unreached, said
  rather than guessed — and the audit line counts only what it actually
  counted.

### Added

- **The coach remembers, through the vault.** PDI 0.86.0 gave the vault an
  embedding index that stores a hash of the text and never the text; this
  is JIM's side of that bargain (`jim/recall.py`). The moments worth
  remembering — what somebody told the coach, wrote in the journal, put in
  a check-in note — are sealed AES-256-GCM into the tandem under a memory
  key and indexed under the same key, so a coach turn recalls by meaning:
  the person who mentioned a shoulder injury in March and asks about
  training in August gets a coach who remembers the shoulder, folded into
  the prompt as context the model may use and never an instruction — the
  same posture as `continuity.attention_lines`. Three rules, each tested:
  **memory never breaks the doing** (a check-in that lands and is not
  remembered beats a check-in refused because the tandem was down — every
  path returns what happened rather than raising); **no vault means no
  memory and no pretending** (unconfigured or offline, the coach works
  exactly as before, and an older PDI without the resident is reported as
  "the vault has no memory index" while the words stay safely sealed); and
  **one person's memories never surface for another** — recall drops any
  match outside `memory/{user}/` before it fetches a word, a second wall
  behind PDI's tenant fence.

  And the errand ledger writes itself into the vault's own tables: the
  unattended study pass now hands its results to the PDI resident as rows
  in a `jim_errands` dataset — through the resident's own plan door, so the
  tandem speaks the same audited shape a facility tenant does — queryable
  in the PDI console beside the data they are about. Non-fatal and said
  rather than hidden: the run's answer carries `vaulted: false` when the
  tandem is absent, offline, or too old to carry a table.

## [0.86.0] - 2026-08-18

### Added

- **The watch on the wrist becomes real.** The thirty-six faces in
  `docs/watch/` shipped as drawings — a design set the README showed and
  nothing served. The instruction that closed the gap was the owner's, from
  the page on his own phone: *be sure to keep all watch screens and make
  sure they're implemented and work from each screen*. `screens/Watch.tsx`
  is the answer: a watch surface in the console at `#watch`, sized for a
  wrist and served by the doors the phone screens already use — a check-in
  logged on face 09 is the Check-in tab's own `POST /checkin`, the
  sensitivity chips on face 16 are `POST /settings/sensitivity`, and the
  agents face reads the same task window `Underway` renders. `#watch/<slug>`
  deep-links one face (`05-heart`, `heart` and `5` all land on Heart), the
  hash tracks the face so a reload stays where the wrist was, and the
  README's gallery now links every drawing to its living counterpart.

  Three faces deserve their own sentences. **CPR** carries its own
  algorithm because it must work with the network gone: a metronome at 110
  compressions per minute scheduled on the audio clock — a `setInterval`
  drifts under load, and a drifting beat is a wrong compression rate —
  sounding thirty high tones and two low ones for the 30:2 rhythm, with
  vibration where the device has it, no account and no network required.
  **Emergency** hands the number to the device with a telephone link,
  because the device is the thing that can place a call — the same honesty
  the alarm queue has carried since it shipped. And **Breathe** runs a
  4-4-6 pattern whose session lands in the calm history rather than being
  a guess.

  The frame around the faces: 147 new console strings in all ten
  languages, with every wording the phones already carry copied from their
  tables byte-for-byte so the wrist and the pocket say one thing; a face
  that reads an account says to sign in on the phone when there is none;
  and the surface opens before sign-in, because the README links land
  visitors on it and the CPR face works for whoever is holding the wrist.
  Screen 112 records the surface in the console gallery.

## [0.85.0] - 2026-08-18

### Added

- **The front page reads like a product, and the mockups moved next door.**
  A field report from the owner's own phone called the README what it had
  become: thousands of lines, walls of mockups, and the thing a visitor
  should learn in a minute buried under both. The README is now a
  professional overview — what it does, the surfaces, quick start,
  configuration, and the release table folded but present. The watch-face set stays on the front page as asked, one face per capability, above the drip channel that feeds every one of them.
  The remaining screen sets live in `docs/gallery.md`, and every guard that
  held the old page — screens shown somewhere, galleries shaped for a
  phone, no stale counts, the banner naming the shipped version — now
  holds the same promises across the pages they moved to.

- **Where the address book lives, and never two of it.** The contacts round
  shipped the book and left custody for later: every row went into the local
  table whatever the account was paying for. `jim/storage.py` had already
  settled how this product answers that question, and it answers it about the
  **plan** rather than about whether the deployment happens to have a vault
  configured.

      asked     where does the book live
      mattered  is there ever more than one of it

  Sealed into PDI where the account is on a plan that has a vault, platform
  custody otherwise — one book either way, one withdrawal either way, and the
  same rows out of `book()` from both. One record per person rather than one
  per contact: a book is a few hundred names read all at once, and a record
  each would turn a single unseal into three hundred on the one path that runs
  while a phone is ringing.

  **Writes are plan-gated; reads and deletions are not**, which is
  `vault_for`'s own asymmetry and the address book is the payload that makes
  the cost of getting it wrong plainest. Somebody on Basic for a year has a
  sealed book. If they move to Free and withdraw the grant, a withdrawal that
  only cleared the side their *current* plan points at would leave a few
  hundred other people's names and numbers in a vault after the one person who
  could say stop did — the copy-kept-after-stop objection wearing a billing
  change as a disguise. So `withdrawn` and `_clear` take the real vault and
  never ask the plan, and a guard reads the source to hold that.

  **Never both.** A plan change between two syncs is the ordinary way to end
  up with two books disagreeing about who somebody knows, so `sync` clears
  both custodies before writing to either.

  **A sealed book with no vault raises rather than answering *nobody*.** *You
  know nobody* and *I could not open your book* are different sentences and
  only one is true; answering the first puts no name — or the wrong name — on
  a phone call, and reports somebody's data loss as a fact about their life. A
  row saying sealed over a vault that has nothing is that case, and it is not
  the same as an empty book, which is a row saying `held = 0`. The count stays
  on the local row so a screen saying *312 people* is never a reason to unseal
  three hundred names.

### Fixed

- **A guard that was measuring prose.** `test_one_function_is_the_only_door_
  to_the_book` asked whether `allowed(user_id)` appeared in the first 900
  characters of each reader. It passed for two releases and then failed on a
  round that only made `sync`'s docstring longer. It asks the property now —
  `allowed` before anything touches the book — and a guard a paragraph can
  break is a guard a paragraph can also satisfy.

## [0.84.0] - 2026-08-17

### Added

- **Two people on one call, each with their own channel 2.** The field ask, in
  its own words: *both parties could use it while on the same call — both have
  profiles and both could be using them simultaneously.*

      asked     can two people each have channel 2 on one call
      mattered  does each of them know the other's guardian is listening

  Two people could already do the first half, and this is worth saying plainly
  because it changes what the round is. `mic.handover` is per person and always
  was: on a private route channel 2 hears its wearer and not the call, so two
  of them on one call never needed permission from each other and never
  conflicted. What was missing is that **nothing knew they were the same
  call** — so somebody on a call where both guardians were listening had no way
  to find that out.

  So a pair is a **disclosure**, and that is the whole of it. It carries no
  audio, no content, and nothing either guardian heard. Each channel stays
  exactly as private as it was; what changes is that each person can see there
  are two.

  **Pairing never grants listening.** A side may only join with a channel it
  already has, so every refusal in `handover` — a private route, a busy
  primary, not the microphone already carrying the call, nobody else in
  earshot — was answered before the pair could name the session. The
  load-bearing one is the speakerphone refusal, and a test holds that pairing
  cannot be done first and the route relaxed after.

  **The two halves never meet.** Neither side is handed the other's session,
  device, gain, or what it hears. What crosses is that somebody is listening
  and since when. A side stops counting the moment their own channel closes,
  because a row that outlived the session it names would report somebody as
  listening after they hung up.

  It forms only between people already each other's contacts — `circle._mutual`,
  the same gate `jim/liaison.py` opens on — and the disclosure surfaces in
  `mic.state`, the one function whose job is *what can it hear right now, in
  words a person can check*. On a call where both guardians are listening,
  *yours hears you* is a true sentence and an incomplete one.

  On the console, on iOS, on Android and on Windows.

- **What a room sees and hears, read as cues rather than kept as footage.**
  The field ask, in its own words: *monitor you from devices in your home such
  as cameras, speakers, looking for visual cues and verbal cues.*

      asked     can it read a cue off a camera or a speaker
      mattered  can it do that without keeping what it read the cue from

  `jim/monitors.py` said what may sense and who else it catches.
  `jim/daybook.py` recorded what was taken in and dropped most of it, because
  most of the roster promises to hold nothing. Neither ever read a **cue**: the
  camera could be switched on and the room described to it, and nothing looked
  at the description.

  **The point is where the reading happens.** `monitors.py` opens by saying
  *"it notices you fell" and "it keeps the video of you falling" are different
  agreements, and only one of them is what the code does* — a sentence that
  until now was honest only because the code did neither. `daybook.sensed`
  reads cues **before** it asks whether any of the content may survive. A room
  camera with keeping switched off notices a fall exactly as well as one
  keeping everything, and stores exactly as little as it promised. Noticing is
  free of retention, which is the only arrangement under which a person can
  switch retention off without switching off their guardian.

  **The words are never what is kept.** A cue row holds the cue, the monitor
  and the reference behind its grading. The sentence it was read from is a
  local, and a test checks what is actually written rather than the shape of
  the function — the detail column is free-form JSON and would have taken the
  words without complaining. Otherwise this module is the back door round the
  roster: read the cue *and* stash the description, on a monitor that promised
  nothing.

  **A monitor only yields cues its own senses can produce.** A doorway senses
  a presence, so it reports nothing however the text is worded; a camera does
  not hear somebody call out and a speaker does not see them on the floor.
  Checked against the roster's `senses` rather than trusted, because the cheap
  version — scan every text for every cue — would have a presence sensor
  reporting slurred speech.

  **One ladder, not two.** Every cue is graded in `jim/escalation.py`'s own
  vocabulary and resolved through `escalation.decide`, so its urgency is
  decided once rather than translated on the way in. A `critical` cue reaches
  a person; `jim/noticed.py` excludes `critical` from the pass that puts
  things to a model, so the two compose the right way round without either
  knowing about the other, and an ordinary `guidance` cue is exactly what the
  free half of that ladder is for.

  The table is plain phrase matching, for the reasons `jim/hazards.py` gives:
  it works with the network cut, costs nothing, and is auditable line by line.
  Every row carries what it means and the reference behind it. It does not
  see — something else describes what it saw, and this reads the description.

  It cannot tell **whose** cue it is. A room camera catches whoever is in the
  room, and a cue read off one of them lands on the account holder's record
  because that is the only record there is. The roster already refuses to
  switch such a monitor on until somebody says the people in that space were
  told; this cannot improve on that claim and does not pretend to. Every cue
  names its monitor, so a reader can at least see it came from a room rather
  than from a wrist.

  On the console, on iOS, on Android and on Windows.

- **The day as it was taken in, and what survived of it.** The field ask, in
  its own words: *watches computer or phone screen all the time, watch every
  meeting you're in, record every call, stream, etc., have perfect accounting
  and context of your life.*

      asked     is the day captured
      mattered  does what survives match what was promised before it was switched on

  `jim/monitors.py` built the consent for this and stopped at the door. The
  roster said what may sense, who else it catches and — in `holds` — what
  stays behind; `POST /monitors/{name}/sensed` even existed, ran the
  permission check, and returned `{"sensing": true}` without recording a
  thing. The permission to capture the day had shipped. The capture had not,
  and neither had the accounting.

  **The roster decides what is kept, and the caller never does.** Each monitor
  already carried a promise written to be read by somebody deciding whether to
  switch it on — *nothing, it is a channel, not a recording*; *nothing unless
  you switch keeping on*; *the readings, as your own history*. `daybook.sensed`
  takes content and then asks the roster whether any of it may survive. A
  screen monitor drops it every time, whatever is passed and whatever anybody
  has switched on. There is no argument that overrides this and a test holds
  the absence of one: the moment a caller can say *keep this anyway*, every
  promise in that table becomes a default.

  That promise is now a field as well as a sentence. `holds` is what a person
  reads; `keeps` is what the code obeys; and a guard holds the two together,
  because obeying an English sentence means parsing one — the first draft did
  `holds.startswith("nothing")` and would have started keeping screen content
  the day somebody rewrote the sentence to begin *"Nothing"*.

  **Perfect accounting, read the honest way.** Every moment leaves a row
  whether or not its content was kept, and a row that kept nothing says which
  promise dropped it. A person can read back not only what their guardian
  retained but what it declined to retain and why. An accounting listing only
  what survived would be a record with its own omissions edited out. Forgetting
  a moment drops the content and keeps the fact, for the same reason.

  **Meetings ask again.** A stretch is a run of the day on one monitor — a
  meeting, a call, a working session. Opening one over a monitor that catches
  other people demands the same claim switching it on demands, checked here
  rather than inherited: consenting to a room speaker in a quiet house is not
  consenting to it through an hour with four other people in the room.

  **What this is not.** It is not a recorder. Nothing here captures audio,
  video or pixels, and a guard holds those columns out of the table. Literal
  always-on recording of screens, calls and meetings would need the roster's
  promises rewritten, somewhere to put the bytes that is not this database —
  `jim/capture.py` already refuses to degrade to a local file for one
  photograph — and an answer to two-party consent law that a checkbox is not.
  None of those is a thing this round could decide on its own.

  On the console, on iOS, on Android and on Windows.

- **What the coach noticed becomes JIM's problem — and only when it has to.**
  The field ask, in its own words: *for autonomous stuff throughout your day to
  save tokens I want coach to be running most of those, and when something is
  identified by coach, it could then start using tokens as Jim to better handle
  the situation.*

      asked     does the free half run the day and the paid half only what it cannot
      mattered  is the decision to spend made by something, and can it be read back

  Half of that ladder shipped in 0.82.0. `jim/errands.py` turns what the coach
  could not **answer** into a bounded study pass. The other half had no path at
  all: the guardian records detections all day, and nothing ever decided that
  one of them warranted a paid turn. A gap became study; a situation became a
  row in a table.

  `jim/noticed.py` is that decision. Each thing the coach noticed goes to the
  offline stack **first** — the same `pipeline.run` that answers all day for
  nothing — and what it settles costs nothing at all. Only what it cannot
  becomes a paid turn. That ordering is the feature rather than an
  optimisation in front of it: *the coach runs most of these* is only true if
  the coach is actually asked first, and asking the model first would produce
  the same answers at a price.

  **It pays down its own bill.** A bought turn is deposited into the store the
  offline stack predicts from, so the same situation is settled free the next
  time it happens — and, as a test found by failing, so are the situations
  near it. Spending is front-loaded and decays.

  **One ceiling, not two.** There are now two unattended passes that can spend,
  so `errands.spent_today` counts both against the one `DAILY`. Two budgets
  would mean the real ceiling is their sum, which is the failure that number
  was written to avoid arriving by a different road. The permits stay separate,
  because sending a general topic out and putting this person's own situation
  to a model are opposite shapes and deserve separate yeses.

  **A spent day is reported, never refused.** Unlike the errands pass, running
  out of budget does not raise here: the free half is still worth running, and
  a version that refused would have withheld the work costing nothing because
  it could not do the work that costs. What could not be paid for comes back in
  `over_budget` and waits for tomorrow.

  **It advises; it does not act.** Every acting tool sits behind a session a
  person opened, with the reach shown at the door and an undo trail on each
  act. An unattended pass that could act would be that apparatus with the
  person taken out of it. Acting unattended is a real thing somebody may want,
  it is a separate decision, and nobody has made it.

  **Emergencies are not its business.** `critical` detections are excluded by
  the query rather than by a later filter. `jim/escalation.py` already takes
  those to a person, and putting a model turn in front of that path would add
  latency to the one case where latency is the harm.

  The task window carries what it handled today with `settled_by` on each row —
  which is where the ladder stops being a claim in a docstring and becomes a
  number on a screen. On the console, on iOS, on Android and on Windows.

- **Everything running, in one place.** The field ask, said twice: *users will
  always have that task window — which agent is running, which tasks are still
  running.*

      asked     which agent is running, and which tasks are still going
      mattered  can somebody see all of it without knowing where to look

  Every piece of this was already answerable and none of it was answerable
  together. Links had a list. The monitor roster had its own. The mic knew
  whether channel 2 was open, the call table knew whether a call was live, and
  the engagement table knew whether an agent was mid-session. Five readers,
  five screens, and no answer to *what is my guardian doing right now* — which
  is the question you ask precisely when you do not already know where to
  look.

  `jim/underway.py` gathers the five, and the gathering is deliberately on the
  server. Four shells each deciding what counts as still running is four
  chances to disagree about it invisibly, since every shell would look right
  on its own. It is the opposite call from the Guardian's lights, which
  compose their glance client-side from routes already open — and rightly, as
  *is there an alarm* needs no judgement. This does.

  **It composes no prose.** `kind` and `why` are closed sets a client branches
  on and says in the reader's own language; `term` is one of the product's own
  vocabulary words and `words` is what the person themselves wrote, passed
  through untouched. A summary endpoint is the easiest place in a product to
  reintroduce an English sentence on a translated screen, because writing it
  server-side feels helpful.

  **What is running, and what merely happened, are kept apart.** An errand
  opens, studies and finishes before the call returns, so listing one as
  running would be a lie told by the one window whose whole job is to be
  believed about that. Today's errands sit in `today` instead, beside the
  budget that bounds them, sliced against the same day boundary
  `spent_today` uses so the list and the count cannot disagree. Asking the
  ledger for `DAILY` rows is exactly enough and not by luck: no more than
  `DAILY` errands can open in a day.

  **It is a reader.** One route, and it is a `GET`. A window over everything
  that could also act on everything would quietly be the widest door in the
  product, so every row names the thing it came from and the screen that
  already owns that capability is where you act on it.

  On the console it is shell furniture beside the lights — always on screen,
  minimizable, and unreachable is a state it shows rather than one it hides
  in. On iOS, Android and Windows it opens the overview, above what the
  Guardian has measured.

### Fixed

- **A link past the call now needs both people, not one.** The rule was
  specified mutual — *end it with the call unless both agree* — and shipped
  one-sided. `task` was a single column, written by either party through a
  door that checked only membership, and the call ending checked only that it
  was set. So one person could hold a channel open to somebody else's guardian
  past the conversation that justified it, on their own say-so.

      asked     does the work outlive the call
      mattered  did both people say it should

  That is the same shape as the one-sided contact `liaison.open` refuses at
  the door, and refusing a stranger there while letting one party extend the
  stay unilaterally is the door mattering less than it looks.

  Agreement is now recorded per side and **against the wording**:
  `take_on` proposes and counts as the proposer's own yes, `agree` is the
  other side's, and only both together outlive the call. Re-wording drops the
  other side's agreement, because agreeing to *book the venue* is not agreeing
  to *run the wedding* — and that reset falls out of the key rather than
  depending on somebody remembering to clear a flag later.

  A proposed task is not lost. It stays on the link and can be agreed to
  afterwards; it simply holds nothing open in the meantime, which is the
  honest state. Ending a link still takes one person, alone, and that
  asymmetry is deliberate in both directions.

  A new table rather than two columns, because this schema has no migrations:
  every statement is `CREATE TABLE IF NOT EXISTS`, so an added column never
  reaches a database that already exists.

  The console's own wording had inherited the error — naming a task said *It
  outlives the call now*, which the backend now refuses. All four shells show
  which of the three states a link is in rather than showing the words and
  leaving it ambiguous.

- **Naming a task on a closed link is refused rather than ignored.** The
  update carried `AND ended_at IS NULL`, so it quietly changed nothing and
  handed back a summary that looked like success. It answers 404 now — the
  same status `say` has always given for a closed link, through a refusal
  with its own type so one condition cannot keep collecting one status per
  route.

## [0.83.0] - 2026-08-17

### Added

- **The people in your phone, and the call that knows who it is with.** The
  field ask, in its own words: *the person they may be talking to may already
  be in their friends list, and an agent monitoring you making a phone call
  outbound will know who you're calling the moment you're calling, so all of
  that can be set up as it's happening.*

      asked     who is on the other end of this call
      mattered  did we learn it from something this person already had

  **It arrives by a grant, not by typing.** Nobody retypes their address book
  into a second app. `contacts` joins the sources a person already grants,
  and the device's book is the truth: `sync` replaces rather than merges,
  because a merge quietly keeps people somebody deleted from their phone
  months ago.

  **This is the grant that is mostly about other people.** Every other source
  is about the person granting it — their pulse, their calendar, their
  spending. An address book is almost entirely somebody else: a few hundred
  people who never chose this product, cannot see that it holds their number,
  and were not asked. That is `touches_others` at its maximum and the same
  argument `jim/monitors.py` makes about a camera bolted to a hall. So it is
  off until somebody turns it on, one function is the only door to reading
  it, and withdrawing the grant **drops the book** rather than merely stopping
  the sync — one switch, not two, held by a guard. A copy kept after somebody
  said stop is the entire objection, made real.

  **The far side's number is still not stored.** `oncall.open` reads it for
  the notice's language and drops it, and that stays exactly true.
  Recognition only ever reads: a call from a number nobody granted leaves
  precisely as little behind as it did before this existed, and what the call
  row gained is the id of one of this person's own contacts.

  **The guardians find each other at dial time.** Where the book says the far
  side holds an account here, and the two are already mutual contacts, and
  the permit is on, the link opens with the call instead of waiting for
  somebody to press something mid-conversation. All three conditions were
  already checked by `liaison.open`, so dial time catches its refusals rather
  than re-testing them — two copies of one rule is how the two drift apart. A
  link that cannot open is not an error on a phone call.

  **What the call leaves behind is the appointment, not the call.** Mom's
  case, and most of the book's: nothing on the other end to link to, and that
  is not a failure. What survives is the thing to be done at a time, filed
  under the person it came from, landing in the calendar everything else
  reads. There is nowhere in the schema for a transcript, a summary or the
  audio, which is the point rather than an omission.

  Free on every plan. A wall at Basic was built and reverted: it broke the
  guard holding that free and Basic reach identical capabilities, and the
  feature is two-sided — it only fires when both parties have one — so a wall
  would suppress the density it needs.

### Fixed

- **A source name nothing reads is a switch that does nothing.** `phone` went
  into `models.Source` beside `contacts`, declared for a call history no code
  asks about, so a person could turn it on and nothing anywhere would behave
  differently. It comes back when something reads it.

## [0.82.0] - 2026-08-17

### Added

- **Two guardians working together, quietly.** When both people on a
  conversation have one, the two can collaborate — and never on the line. The
  call carries voices; the guardians talk over the network, which also means
  none of this needs a phone: the same link serves two people in a room, on a
  video call, or in a thread.

      asked     can two guardians work together
      mattered  is each one still working for its own person

  **It forms only where both sides already knew each other.** `circle._mutual`
  is the gate and it was already exactly right: an invitation is one
  direction, two make contacts, either side deleting theirs closes the door
  for both. Each guardian recognises the other from a record its own person
  already holds — nobody publishes a directory, and one-sided contact reaches
  nothing, which is what stops a stranger's guardian calling yours.

  **Silent, and readable afterwards by the person it works for.** Two agents
  negotiating on a channel neither human can inspect are two principals with
  counsel who never report back, so the link keeps both halves split by side.
  A person reads what *their* guardian said and what it was told; the other
  person's half was never theirs to read. Nothing crosses without the
  `speak_for_you` permit, which is `asked`.

  **It lives as long as the work does.** The link opens with the call and
  closes with it. What extends it is not an agreement to stay connected but a
  **task** — something that came out of the conversation and has to be
  finished. A link carrying one survives the call ending; a person stopping it
  always closes it, and the call ending cannot close what the task is holding
  open. Closed links stay in the list, because what two guardians did on
  somebody's behalf is not something to tidy away.

  On the console, on iOS, on Android and on Windows.

- **Somewhere to plug the monitoring in, and what each one costs.** Cameras,
  speakers, screens, bands, rings, patches, doorway sensors, the strip under a
  mattress. Three tables already existed and none of them answered the
  question a person actually has before switching one on: `devices` says what
  is registered, `sources` says which categories of data may be read, and
  `mic.MIC_TYPES` says whether a microphone is worn or pointed at a room.

      asked     can this device sense me
      mattered  who else does it sense, and what does it keep

  **Every row says what it takes in, who else it reaches, and what stays
  behind.** That last one is the half these lists omit: *it notices you fell*
  and *it keeps the video of you falling* are different agreements. Sensing
  and keeping are two switches.

  **Who else it reaches decides the rest.** Nothing that senses people who did
  not choose it is ever on by default, and a guard reads the table rather than
  trusting anybody to have read it. A second guard holds that a stationary
  monitor cannot be filed as catching nobody — a thing bolted to a room senses
  the room, which `jim/mic.py` settled for microphones and holds for cameras,
  speakers and mattress strips too. Worn does not mean harmless either:
  glasses are worn and still pointed outward at whoever is in front of you.

  **Switching one of those on is refused until somebody says the room knows.**
  Stored as what it is — an assertion with a time on it, not consent this
  product collected — because the alternative is a hall camera going on with
  nobody having thought about the hall. `monitors.may_sense` is the only door
  to reading any of them, the argument `oncall.may_listen` makes for a call.

  Always-on is a property, not a default. A person who turns a hall camera on
  has decided; a person who finds one already on has been decided about, and
  no amount of usefulness afterwards converts the second into the first.

  On the console, on iOS, on Android and on Windows.

- **An aid on the call, and the notice that goes first.** `jim/mic.py` lends
  the guardian a second microphone while a call occupies the first, and it
  refuses the speaker case in as many words — *they were never asked and could
  not revoke it*. That refusal is right about the person it names, and it is
  not weakened here. This is the other case: the far side **is** told.

      asked     may the agent be on this call
      mattered  does the other person know it is

  **The notice is the one everybody has already heard.** *This call may be
  monitored or recorded to better assist you* — deliberately the support-line
  script rather than a careful new sentence. Somebody hearing it does not have
  to work out what it means or what they can do about it, and a better
  sentence nobody recognises is a worse notice.

  **Said in a language they might actually speak.** Picked from the dialling
  code, which is the only clue a call gives before anybody says hello — and in
  every language where the mix is known rather than one guess: Switzerland
  hears German, French and Italian; Québec hears French then English; Morocco
  hears Arabic then French; an unknown number hears English and Spanish, which
  is what a support line in the United States does. The number is read for
  that and dropped: never returned, never logged, never stored, because the
  person on the other end has no account here and never will.

  **Notice, not permission.** Nothing waits for the far side to answer,
  nothing records their agreement, and there is no state for *they objected* —
  the notice plays and hanging up is theirs, exactly as it is on every support
  line. What is enforced instead is **ordering**: `oncall.may_listen` is the
  only door to hearing anything and refuses until the notice has actually gone
  out, confirmed by whatever played it rather than assumed by the server that
  composed it. A call that never announced never listened, and stays in the
  history as the evidence that the ordering held.

  On the console, on iOS, on Android and on Windows.

- **A built sentence lost its template inside the wrapper that carries it.**
  Every handler wraps a refusal as `{"detail": exc.detail}`, and the branch
  that localized it asked whether the wrapped detail was a `str`. A
  `Templated` **is** a `str`, so every built sentence was caught there and
  looked up by its finished English — a key in no table. `MUST_BE_ONE_OF` went
  out in English from seven raise sites, in every language, and nothing said
  so: an untranslated sentence and a sentence nobody has translated yet look
  identical from outside. The branch recurses now, and a guard holds both
  shapes.

- **Beside somebody while they write.** The field ask, verbatim: *as you're
  typing out a sales page to a customer, or writing a strategy doc, to just
  jump in and say hey you forgot about this, or here's maybe another idea, or
  you should consider this, I can do this thing to help.*

      asked     can it answer about a draft
      mattered  does it notice the thing they would have wanted noticing

  Three remarks, and they are the three in that sentence: something already in
  this person's own records that the draft does not mention, something the
  coach knows about the subject that the draft is not using, and a thing this
  product can actually do for the part they are on. Three at most — a margin
  full of remarks is a margin nobody reads — and silence, with its reason,
  rather than filler.

  **Every remark carries its evidence.** *You forgot about this* with nothing
  under it is a guess wearing a suggestion's clothes, so each one names the
  goal it came from, or the store entry and where that entry came from: the
  hand-written pack, an excursion, or a paid model turn are three different
  claims and the person deciding whether to use it is entitled to which.

  **The draft is read and dropped.** Not in a table, not in a log, not as an
  embedding — and it holds by construction rather than by promise: the module
  imports no database and calls nothing that writes. It never leaves the
  device either; a guard reads its imports the way `jim/pipeline.py`'s does.
  What somebody is drafting for a customer is the most commercially sensitive
  text they own, and the honest way to be trusted with it is to have nowhere
  to put it and no way to send it.

  **And it decides nothing.** Remarks come back; applying one is the writer's
  own act. It is also not watching a screen — it reads a draft handed to it,
  in a request somebody made. That other thing is a different round with a
  different consent, and nothing here opens the door to it.

  On the console, on iOS, on Android and on Windows.

- **What the coach could not answer becomes what JIM goes and learns.** Every
  piece of this loop already existed. The coach on the device answers all day —
  no network, no key, nothing per turn. When it cannot answer it writes the miss
  down, and the curriculum turns those misses, plus the metrics and goals
  somebody actually put the guardian near, into a study list. Then it stopped:
  the last step was a person finding a screen and pressing **study**, one topic
  at a time, which is a loop that closes only for somebody who already knows it
  is there.

      asked     does the coach know what it does not know
      mattered  does anything go and find out

  **The pass is that step.** It studies what the coach missed, folds the
  findings where the offline stack reads them, and closes the question so
  nobody pays to study it twice. Every row carries the monitor that asked —
  *it studied sleep* is a fact about the guardian, *it studied sleep because
  your sleep band has a learned baseline* is a fact about the person.

  **It is refused until somebody allows it.** `study_on_your_own` is `asked`
  rather than covered by opening a session, and it says in the person's own
  words what leaves and what is kept. **And it is bounded**: a few errands a
  day, counted from the ledger rather than from a variable so a restart is not
  a fresh day's spending, with a ceiling that takes no argument.

  **What the budget is really protecting.** Tokens today; not tokens
  afterwards. The coach on the device is the part that works in a tunnel,
  holds the private half where no third-party model ever sees it, carries the
  provenance of every entry so a vendor model's claim can be set beside what
  is actually known, and accumulates for as long as somebody uses it — what it
  learned about them at thirty is still there at sixty. When a model turn
  costs nothing the right change is that this pass runs more often, not that
  the coach stops being the thing that answers.

- **One way out, and it sanitises.** The excursion path was written inline in
  `api.py` twice and the copies had already drifted — one folded its findings
  and closed the matching miss, the other did neither, with nothing to say
  which was intended. Both go through `research.excursion` now, and a guard
  holds them there.

- **A templated refusal reached the reader as English.** The guard carried
  into this product last release found its first real one the day it arrived:
  the day's-budget sentence is built from a template, and the route passed it
  on with `str(exc)`, which drops the template. `i18n.raised` is what a route
  hands on now.

### Changed

- **The beta deploy page has a pointer here now.** This repository documents
  running the product on its own; the live beta is four containers on one box
  and is documented once, in QRME, beside the compose file it describes. An
  operator standing in this repository at the end of a release had no way to
  find it. `docs/hosting.md` says where it is, and why there is one copy
  rather than three — copies of a page about one machine disagree the first
  time somebody fixes only the one they had open.

## [0.81.0] - 2026-08-17

### Added

- **A guard on the sentence that forgets how it was built.** `str(exc)` on a
  `Templated` returns a plain `str`, which drops the template — so a refusal
  built by `i18n.fill`, carried on one of this product's own exceptions and
  passed on as `HTTPException(403, str(exc))`, reaches the handler as bare
  English. In every language, silently, and looking exactly like a sentence
  nobody has translated yet.

      asked     is the refusal translated
      mattered  did it still know how it was built when it got there

  QRME shipped that on its sealed-dialer sentence — the one somebody reads
  while something is going wrong — translated into nine languages and reaching
  none of them, because the route between the raise and the handler called
  `str()`. Nothing here launders a template that way today. That is worth
  keeping rather than assuming: the first exception in this product to carry a
  built sentence would otherwise ship the same defect, and nothing would say a
  word.

  `i18n.raised` hands a refusal on in the shape it was raised, and
  `test_a_built_sentence_is_not_laundered_through_str` fails any route that
  reaches for `str()` instead. Carried by all three products, which is where
  this class of defect has always lived.

## [0.80.0] - 2026-08-16

### Changed

- **The version, and nothing else.** This product carries no code changes in
  0.80.0. QRME took this release on its own — the agent learning to ask people
  rather than pages, and the ledger of which far hosts keep watching it
  leave — and neither has a counterpart here yet. The cut brings the three
  back into one number so the tandem's version guard has a single answer to
  give.

      asked     what changed in this product this release
      mattered  that the three products report the same version to a caller

  The console's version guard compares itself against the backend answering
  the port, and the deploy notes say to rebuild all three on every release
  for exactly that reason: a box carrying two versions reports the mismatch
  to whoever is using it rather than to whoever deployed it. A release that
  says *nothing changed here* is the honest way to keep that true, and
  cheaper than a scheme where the three drift apart and somebody has to
  remember which pairs are compatible.

## [0.79.0] - 2026-08-16

### Changed

- **The version, and nothing else.** This product carries no code changes in
  0.79.0. QRME took 0.78.0 on its own — a plug-in storefront that JIM has no
  counterpart for yet — and this release brings the three back into one
  number so the tandem's version guard has a single answer to give.

      asked     what changed in JIM this release
      mattered  that the three products report the same version to a caller

  The console's version guard compares itself against the backend answering
  the port, and `docs/beta-deploy.md` §7 says to rebuild all three on every
  release for exactly this reason: a box carrying two versions reports the
  mismatch to whoever is using it rather than to whoever deployed it. A
  release that says *nothing changed here* is the honest way to keep that
  true, and cheaper than a version scheme where the three drift apart and
  somebody has to remember which pairs are compatible.

## [0.77.0] - 2026-08-16

### Fixed

- **A neighbour you already have listed should not be re-identified by hand.**
  The circle list shows your neighbours by name. To look at one of their
  homepages you typed their id into a box at the bottom of the screen and
  pressed Open — and the id is a UUID, so *type it in* really meant *copy it
  from somewhere else first*.

      asked     the friends picture should open their profile homepage
      mattered  the only way in was a text box asking for their id

  The name in the list is the link now. The box stays for an id somebody was
  handed from outside the app, which is the case it was always right for.

## [0.76.0] - 2026-08-15

### Added

- **The console gets a front door.** Twenty-four tiles and no way in: every
  capability sat behind one of them, which meant knowing which one before you
  could ask for anything — and the tile carrying the mark opened a permissions
  panel rather than JIM.

      asked     pull up JIM when I press the mark
      mattered  the mark opened permissions, and the conversation was behind
                a different tile

  `Talk` is a **composer** at the bottom — the pill, the mic, Speak — and a
  **horizontal scrolling rail** of features above it. The rail is a launcher,
  not a second implementation: every chip calls `go` with a tab id and the
  screen that opens is the one the tile opened, same code and same guards. Its
  label is derived from the destination (`talk.rail.<tab id>`) rather than
  listed beside it, which is how a chip ends up labelled for one screen and
  opening another. The permissions screen keeps its code and moves to its own
  tab, reached from the rail. The `+` carries three entries, not four —
  Camera, Photos and Voice have screens behind them today; Files and Link need
  an ingest route that does not exist, and a control that does nothing is
  worse than a menu that is short.

- **The Studio: tools you write, for yourself only.** A widget is a function
  somebody wrote, stored against their account, run on demand. It runs in a
  box with four walls, and each is a mechanism rather than a promise: the
  network is cut with `unshare -rn`, the filesystem is one directory under
  node's permission model, `child_process` is refused outright, and CPU,
  memory and wall-clock are capped before it starts. If any wall cannot be
  built, **nothing runs at all** — a sandbox that quietly degrades is worse
  than no sandbox, because the feature still appears to work.

      asked     can a person run their own code here
      mattered  can a person run their own code without reaching anybody
                else's — this disk holds other people's clinical captures

  Seven routes, all scoped to that person at the door *and* at the query, so a
  widget id belonging to somebody else is not found rather than refused.
  Thirteen refusals in ten languages. The limits are fetched from
  `/studio/limits` rather than written into the console, and when the box
  cannot be built the banner names the missing wall while the editor stays —
  only the run button goes.

  Console this release. The three shells are recorded in their own backlogs
  with the reason, which is that a widget is written rather than tapped and a
  phone keyboard is the wrong instrument for the first draft of a program.
  What that does not excuse is the reading half, and the rows say so.

### Changed

- **The tandem contract said the thing that stopped being true.**
  `docs/tandem.md` — byte-identical in all three repositories — described the
  self-link as *the user pastes their own QRME owner token*. That was the
  mechanism until this round replaced it, and a contract describing a
  mechanism the product no longer has is worse than one that says nothing.
  It now carries the three rules that hold the sign-in path open: the password
  crosses once and is never stored, the account token is used and dropped
  because it is broader than the owner token it mints, and an account with
  more than one `self` profile is asked rather than guessed at. Pasting still
  works and is no longer the only way in.

- **Menu icons go back to menu size.** They were 84px because the full
  jim-mini lockup — wordmark, eleven rows of ABRACADABRA, OS plate — only
  reads cleanly at 84, which forced every other icon to match. `JimMiniOS`
  now has a small form that draws the amulet triangle alone; nothing else
  survives the shrink, and an illegible part is not a smaller mark. The word
  stays on the label underneath, where it was always more readable.

- **A screen opens at its top.** Switching tabs left the scroll position
  where the previous screen had been read to, so a long screen opened halfway
  into its own body. The `.content` pane is now scrolled to the top on every
  tab change.

- **Care Team's condition rows are blocks on a phone.** Four cells wrapping
  onto two lines with only a hairline between rows put each condition's name
  under the *previous* row's controls. Each condition now gets its own
  bordered block. Scoped to that one variant — the other four `.spec-row`
  call sites carry two cells and the shared rule is right for them.

- **The autonomous-resuscitation waiver moves from Wards to Safety.** It is
  the one card on that screen the account holder signs about their own body,
  and it now sits under the automatic path it modifies. No new strings: it
  reuses the existing `wrd.*` keys.

- **The follow-up nudge names the condition, and asks about a different one
  each slot.** *"I asked you something and never heard back"* is the shape of
  a question rather than a question; the line now reads *"I gave you
  something for {condition} and never heard back. Did it help?"* in ten
  languages. It does not name the guidance itself, because
  `guidance_followups` stores the condition, the severity and the times and
  never the advice text. Underneath that, a defect: the beat outranks nearly
  everything, so three open follow-ups produced the identical card three
  times. Morning now takes the newest, midday the next, evening the one
  after.

## [0.75.0] - 2026-08-15

### Changed

- **The console-untranslated ceiling goes from 93 to 2.** It was 0, then 93
  when the reader was widened to see a sentence chosen at render time, and
  the file promised the next rounds would take it back down. This is those
  rounds.

      asked     is this screen translated
      mattered  is every sentence on it translated, including the ones a
                condition picks between at render time

  Ninety-one strings across Attending, Baseline, Bearing, CareTeam, Channel,
  Checkin, Community, Held, Journal, Meds, Monitor, Reach, Safety, Wards,
  Coach, Onboarding and Settings now have keys and ten translations each.

  Three of the ninety-one were not translation work, and they are the ones
  worth reading the diff for. Onboarding's password toggle carried its
  `aria-label` in English beside a visible label that was also English — the
  screen reader and the eye untranslated in the same breath, and a row this
  backlog could never have listed, because an `aria-label` is not text
  between tags. The Settings posture card built one sentence out of two
  adjacent string literals, which is a sentence no translator can reorder.
  And `OfflinePosture` had no language binding at all, because until this
  round it had nothing to say.

  Seven of the new keys collided with keys that already existed. Three were
  the same English and were dropped — the screens name the rows that were
  already there. Four were a different sentence under the same name:
  `set.voice.device` is a paragraph about the device voice, `med.add` is a
  heading, `med.critical` is a sentence, `hld.src.allow` takes a `{source}`
  hole. Those got a distinct name for the new use and only the new call site
  moved. Two meanings under one key is this console's version of the defect
  `test_one_name_one_type_on_the_wire.py` catches on the wire.

  Two rows stay: `ElevenLabs` and `OpenAI`. They are the names of two
  companies, printed because that is what the provider is called in every
  language, and a translated vendor name would be a name nobody could match
  against the account they hold there.

### Added

- **The audit chain, ported from PDI.** JIM records what happens to a person
  in `events` — readings, detections, guidance, the escalation ladder's
  decisions. That table is a timeline: it is written to be read on a screen,
  its shape follows what the screen needs, and it gets pruned, reshaped and
  paginated. Every one of those is indistinguishable from tampering once the
  same rows are load-bearing for evidence.

      asked     is there a record of what this Guardian did
      mattered  can somebody tell whether that record was edited afterwards

  So `jim/audit.py` is PDI's hash-chained log, brought over rather than
  reinvented: each entry's SHA-256 covers the previous entry's hash, so a
  retroactive edit or a deleted row breaks the chain and `verify()` says at
  which sequence number. `events` is untouched — nothing moved, nothing
  deprecated, and the consequential acts appear in both: the timeline for the
  person, the chain for the question about the timeline.

  Seventeen acts are catalogued and every one of them is wired: the safety
  path end to end (watch armed, disarmed, tripped; an alarm accepted, cleared,
  escalated; a beacon alarm from a passer-by; *Get help now*), a written
  mandate over money granted or withdrawn, a permission area opened or closed,
  an engaged session acting or taking it back, and the two ends of a life —
  consent given at enrolment, data taken out, data erased. Not everything, on
  purpose: a chain of every read is a chain nobody verifies and a table that
  grows without a reader. These are the acts that reach outside the person's
  own screen.

  Three pieces of the port are deliberate rather than incidental. The stored
  and hashed fields are fixed and `category` is derived at read time, so the
  catalogue can be enriched forever without altering — or breaking — a single
  existing hash; that is PDI's design and the reason its chain survived a
  dozen releases of new actions. The table carries **no** `REFERENCES
  users(id)`, because a chain a cascade can empty is not tamper-evident. And
  an erase records itself on the chain rather than removing what the chain
  already said: a chain with a hole in it is not evidence of anything.

  That last one is a promise being broken in the open, so it is answered in
  the open. `GET /audit/{user_id}` hands a person their own rows, the
  catalogue of what would have been recorded, and — the half that makes the
  other half mean anything — whether the chain still hashes to itself. The
  reading door is what makes excluding the chain from the export bundle
  honest: the person can always read what was said about them, they just
  cannot rewrite it.

  On all four clients. Two guards shaped the wire and neither was consulted
  politely. The Swift-shape guard caught `broken_at_seq` appearing only when
  the chain was broken — a key that comes and goes is two shapes on one wire —
  so it is always present now, null when the chain is whole, where PDI omits
  it. Then the wire-name guard rejected the obvious field names one after
  another: `entries` already carries the access log's rows, `chain` already
  carries custody's provenance object, `actions` and then `acts` are already
  taken (the second is a boolean on every engaged tool, saying whether that
  tool changes anything), and `checked` is a boolean in `jim/voice.py`. What
  survived is `trail`, `integrity`, `catalogue` and `hashed` — names that cost
  four rounds of renaming and are each true. One wire name, one type.

## [0.74.0] - 2026-08-15

### Changed

- **The ABRACADABRA button is the whole jim-mini OS lockup.** The tab has
  carried `🜂` since the incantation replaced "Activate JIM" — the alchemical
  fire glyph, picked because "the triangle is how the tab is found before the
  word is read". It is the mark itself now: the neon wordmark, the amulet
  triangle with ABRACADABRA descending eleven rows, and the OS plate.

      asked     is the mark on the button
      mattered  is the whole mark on the button, big enough to read as itself

  The second question set every other decision in this round, and it was
  answered by rendering the thing and looking at it rather than by reasoning
  about ems. At 60px the wordmark is cramped; at 72 it is fine; at 84 all
  three parts read cleanly. So the menu icon is 84px, and the other
  twenty-three icons grew to match — a mark that dwarfs its neighbours is not
  a menu, it is one button that got away. The desktop column went from a list
  of rows to two columns of tiles, icon over label, which is the shape the
  phone bar was already using at the bottom of the same stylesheet; it widened
  232 → 300px. The phone bar keeps its row and scrolls sideways, because
  twenty-four tiles at a readable size do not fit across a phone and squeezing
  them to fit is what made the old glyph a glyph.

  Two details that only a render would have caught. `align-content: start`
  alone let each grid row swallow the column's slack, and the tiles came out a
  quarter of the viewport tall until `grid-auto-rows: max-content` joined it.
  And the character icons were first set at 30px beside a 60px drawing, which
  is precisely the mismatch the resize existed to remove.

  The neon wordmark is stroked rather than filled: a neon tube is a thin line
  of even width, and an outline reads that way whichever face the renderer
  substitutes underneath — a script font cannot be assumed, so the stack asks
  for one and degrades to a glowing italic word instead of to something that
  looks broken. Every glyph inside the triangle is placed at a computed x for
  the same family of reason: `textLength` is honoured inconsistently across
  rasterizers, and a mark that is one width in Chrome and another in cairo is
  not one mark. `assets/brand/jim-mini-os.svg` is the same drawing as a file.

  The surface manifest caught the new component in the round that introduced
  it, which is what it is for. It is chrome rather than a screen — the way
  `Help` is chrome — so it joins `NOT_A_SURFACE` with its reason; what the
  button opens is Engaged, which is drawn and numbered.

  **And on all three phones.** Each shell draws the same lockup from the same
  fractions — `JimMiniOSMark` in Swift, Kotlin and XAML — built from stack
  views and one triangle rather than from a canvas with text drawn into it.
  Text on a canvas means measuring glyphs by hand on three platforms that
  measure them differently; a `Text` in a stack is the same drawing with each
  layout engine doing its own arithmetic, and it needs no packaged image, so
  nothing can go missing from a build.

  Two tab strips had to change shape to hold it. iOS was a segmented picker
  and Android a `TabRow`; a segmented control is about thirty points tall, and
  a `TabRow` divides the width evenly — neither has a size at which a mark can
  be seen. Both are now scrolling strips of icon-over-label buttons, which is
  the move the console made, for the reason the console made it. On Windows
  the icons moved out of `NavigationViewItem.Icon` and into `Content`: the
  `Icon` slot takes an `IconElement`, which cannot be a drawing and cannot be
  resized, so the eleven symbols are `Viewbox`-wrapped there beside the mark.

  The shell-literals guard caught the letters immediately and was right to:
  `ABRACADABRA` is a row its own tables translate. It is recorded rather than
  keyed, in a third category the record did not have — not a wire value and
  not a label, but a picture that happens to be made of letters. The tab
  *beside* the mark stays translated, transliterating into Japanese, Chinese,
  Hindi and Arabic, which is right for a name and wrong for a talisman.

- **The collapse path now reasons out loud, and tells the one person who can
  dial.** The field report that reframed the safety screen — *"say if you
  collapse on the floor and needed help and assistance how are you gonna put a
  sticker on a door"* — was answered on the pressing end: "Get help now" leads
  the screen and beacons moved below it, saying they are the bystander's path.
  The other end of the same report went unanswered. When somebody actually
  collapses they press nothing, and what runs then is the crash watch.

  Two things were wrong with it, and both are the same shape.

  **It decided its own tier.** `_trip` computed `"emergency_services" if the
  box was ticked else "notify_contact"`, while every other way this product
  summons help goes through `escalation.decide` and comes back with a `path`
  that can be replayed and argued with. The one path where the person cannot
  speak for themselves was the one with no reasoning on the record.

      asked     what tier did the trip reach
      mattered  why, in words somebody can argue with afterwards

  It goes through the ladder now and answers the same tier it always did —
  deliberately, because this is not new behaviour, it is the existing
  behaviour with its argument attached. Sensitivity is pinned at balanced: the
  dial governs how eagerly JIM escalates a *reading*, and a standing
  instruction written down while the person was fine must not be raised or
  lowered by a preference about jumpiness. The arming is a ceiling rather than
  a floor, so a watch armed without the emergency-services step now reports a
  *clipped* decision — the need is handed to the human standing there, exactly
  as an anonymous beacon alarm does.

  **The page said everything except what to do.** The trusted contact was
  emailed at 3am to "treat it as real" and nothing more. The bystander's page
  has told a stranger to dial the number themselves since it shipped, in ten
  languages; the acute path never did, on either setting of the box. The
  ticked box is the one that most needs it — a dispatch *request* relayed to
  connected systems is the thing that most looks like a call having been
  placed. Every page the trip sends now ends with it, the re-page included,
  and the sentence rides in the alarm's `messages` as well as in a field of
  its own, so a shell built before this round still shows it.

  The queue itself was uneven for the same reason. A beacon alarm's live
  response carries the sentence to the stranger; the alarm *list* the carer
  reads showed a tier and never mentioned the ceiling that produced it. One
  alarm, two readers, and only one of them was told. Both rows carry it now,
  and all four clients render it on the open alarm card rather than as a grey
  footnote at the bottom of the screen — the console had no such footnote at
  all, which is the odd-client-out shape this estate keeps finding.

### Added

- **You can now tell it to switch something on.** Reported from the field, in
  those words: *these menus and settings are awful user unfriendly if you
  don't know what you're doing … I want users to be able to verbally
  communicate with JIM what they would like to have on or off and JIM to be
  able to make edits and changes to their accounts.* An engaged session had
  twenty-six tools and three of them touched a setting. Where it speaks
  through, what it is allowed to read, and which parts of the product are
  switched on were screens and only screens — reachable by somebody who
  already knew where they were, which is exactly the population that did not
  need them.

      asked     can the Guardian act
      mattered  can it act on the thing the person is stuck on

  Three tools, and every one of them is a sentence somebody would actually
  say: *talk to me through my earbuds*, *stop reading my calendar*, *turn
  messaging off*. It does them, says what it did, and each lands on the undo
  trail like everything else.

- **A grant, in a list, that switches off again.** The second half of the same
  report named the shape: *kinda like I gave you permission and connections to
  my ElevenLabs account … after they opened the connectors and approved
  permissions per app.* So `jim/permits.py` — the connectors screen turned
  around to face this account's own settings. Six groups, each explaining
  itself in a sentence before the toggle beside it means anything, each
  revocable, each dated so that "I never agreed to that" is answerable with
  something.

  The two groups that reach where nothing reached before — what the Guardian
  may read, and which features are switched on — start refused. The four
  already covered by opening a session are not re-asked for, because a release
  that puts a permission screen in front of something somebody already
  approved has made the product more annoying rather than safer. **Consent
  already given for one thing is not consent for a new thing, and the reverse
  holds just as firmly.** A refusal names the group and where the switch is;
  it never works around one and never implies it acted anyway.

### Fixed

- **Nine buttons labelled with the names the database uses.** "Where I speak"
  drew its picker straight off the wire — `phone_screen`, `desktop_screen`,
  `ar` — so the choice between two of them was a choice between two
  identifiers, in every language including English. The baseline card beside
  it did the same with its six areas and four standing words, with the
  underscore swapped for a space, which is English in a thin disguise.

      asked     is every key a screen writes down present
      mattered  is every value a screen renders a word

  The guard added last release could not see this one. `t("nav.presence")`
  spells its key out and can be read from the file; `word("surface",
  s.surface)` cannot, because the tail arrives at runtime from a table that
  lives in Python — so the authority is now that table, read directly. Both
  halves of one failure, and only one half was spellable, which is why the
  first guard shipped and the picker stayed raw.

- **An undo that would have failed at the moment somebody used it.** Two of
  the three new switches recorded no way back, for two different reasons: the
  source setting names its subject in the body and the inverse-builder only
  searched the path, and the feature switch answers as a map where the
  row-selector hunts for a list and would have found the message threads. A
  third would have replayed `chosen` at a door that takes `speaks_on` — a 422
  discovered by somebody trying to take something back, which is the worst
  possible moment for an undo to be wrong. All three are driven end to end
  now rather than asserted.

- **A guard that would have had six good rows deleted.** The missing-row check
  ported to PDI reported `pos.cap.`, `pos.tone.` and four siblings as keys
  with nothing behind them. They are not keys: that console builds some
  lookups by concatenation, and a pattern that stopped at the closing quote
  read the prefix as a key of its own. A guard against identifiers on screen
  that would have put six more into the table.

## [0.73.0] - 2026-08-14

### Added

- **The phones say when the backend is a different version.** `/health`
  answers a `version`, and the console has compared it against its own build
  since a stale backend first cost somebody an evening — an older install
  answers perfectly well and then serves an older API, so the app looks
  alive while every newer screen says "Not Found" for no stated reason. The
  native shells can be pointed at that same address, and said nothing at
  all.

      asked     is the backend reachable
      mattered  is it the backend this build was written against

  The answer was already on the wire and every shell decoded it away — nine
  places where the field was in the response and out of the struct. All nine
  now read it and say so: a dismissible banner naming both versions and the
  address, above the tab bar and above the welcome flow both, because a
  stale backend breaks the screens a signed-out person meets first. Ten
  languages each, dismissed per launch rather than remembered — the
  condition holds until the address or the backend changes, and a
  permanently silenced warning about a broken deployment is worse than none.

### Fixed

- **The device recogniser never once ran in a browser.** Safari permits
  `SpeechRecognition.start()` only inside the user gesture that asked for
  it, and an `async` function holds that gesture exactly until its first
  suspension point. `listen` read the voice settings first, which spent the
  gesture on a fetch and left the recogniser to be refused with
  `service-not-allowed` — no prompt, no permission to grant, nothing the
  person could do. So the fallback this module's header has promised since
  it was written worked on every platform except the one most people are
  holding.

      asked     is there a device recogniser to fall back to
      mattered  is it started while the browser still permits it

  `preferDevice` made it worse rather than better. That flag exists so the
  tap after a service refusal goes straight to the recogniser instead of
  failing the same way twice — and it was consulted *after* the await, so
  the retry the error message explicitly invites died in the same place as
  the attempt before it. Everything decidable without the network is now
  decided before the first `await`, and the settings answer is cached by
  `primeVoice()` on mount rather than re-fetched at tap time.

- **A platform refusal printed its error code and stopped there.**
  `not-allowed` means a microphone prompt was shown and declined, which
  tapping again can fix. `service-not-allowed` means no prompt will ever
  appear. Both arrived as the same sentence with the raw code in brackets.
  The second now says the operating system refused and names the remedy —
  Dictation, and where it lives in Settings.

      asked     did the recogniser fail
      mattered  is there anything its owner can do about it

  Third instance of that shape in two releases, so it is guarded now and
  not merely fixed: four checks cover the ordering, the flag, any future
  microphone screen that forgets to prime, and the refusal naming a remedy.
  Structural, because the defect is invisible to a behavioural test — node
  ships no `SpeechRecognition`, jsdom has no user gesture, and the code is
  correct on every engine that does not enforce the rule.

## [0.72.1] - 2026-08-14

### Fixed

- **A pasted key took the key check down with a 500.** A credential copied
  from a dashboard arrives with a trailing newline. It went into an HTTP
  header verbatim, where `http.client` refuses it with `ValueError: Invalid
  header value` — not a `URLError`, so it passed both `except` clauses in
  `_subscription` and left the route as a 500: the one answer a person can
  do nothing with, on the screen built to tell them what to do about their
  key.

      asked     is the key a working key
      mattered  is the key even sendable

  Found in the field on the first night `/settings/voice/check` existed.
  Three of the four clients trimmed their input — iOS, Android and Windows
  — and the console did not, which is the client the deployment was
  configured from. So the key is stripped where it is stored *and* where it
  is used: the environment half never passes through a form to be tidied on
  the way in, and a `.env` line or a Docker `environment:` entry carries
  whitespace as easily as a paste does.

- **An unpaid account read as a bad key.** ElevenLabs answers **401** to a
  subscription with a failed invoice — the same status it answers to a
  credential it does not know. The verdict classifier asked only whether
  there had been an HTTP error, so it called a working key `key.refused`,
  and the sentence attached to that verdict tells its owner to paste it
  again or create a new one.

      asked     did the service say no
      mattered  did it say no to the key, or to the account

  That is worse than silence: it sends somebody hunting a credential that
  was never the problem, while the actual remedy goes unmentioned.
  `key.unpaid` is its own verdict now, in ten languages on all four
  clients, and it names the invoice.

## [0.72.0] - 2026-08-14

### Fixed

- **A host key that paid for the voice was read and thrown away.**
  `ELEVENLABS_API_KEY` is the house key — the way a deployment buys the
  voice on behalf of everybody who opens the app. It did nothing.
  `_resolved` defaulted the provider to `device` and *then* asked
  `_env_key("device")`, which is empty by construction, so the branch that
  falls back to the device's own voice fired every time and the key was
  never consulted.

      asked     is the environment key read
      mattered  does setting it turn the voice on

  `_house_provider` now infers ElevenLabs from the key's presence. Only
  ElevenLabs: `OPENAI_API_KEY` is the *language* key in `jim/llm.py`, and a
  deployment that sets it is buying reasoning, not speech — inferring
  speech from it would spend somebody's tokens on audio they never asked
  for.

- **"Saved." was answering the wrong question about an API key.** Saving
  wrote the string and the screen confirmed it, which was true and silent
  about whether what was saved could speak. ElevenLabs' dashboard shows
  each key's **ID** permanently, beside its name, and shows the key itself
  exactly once — at creation — so the string in front of you whenever you
  go looking is the wrong one. Pasting it produced a deployment that was
  configured, reported itself configured, and failed at the moment somebody
  asked to be spoken to, several screens from the field they typed into,
  with a raw `api_key_id_used_as_api_key` from the provider.

      asked     was the key saved
      mattered  is the saved key a key

  `POST /settings/voice/check` asks the provider — one account read, no
  audio, no spend — and all four clients show its verdict at the moment of
  saving. The verdict travels as a key rather than a sentence, so each
  client renders it from its own ten-language table; the key-ID case is
  told apart from every other refusal because it is the one that names an
  action to take. Checking the key's *shape* instead would have encoded
  today's format as a rule and refused tomorrow's, and the service is the
  only authority on its own keys.

- **One of the seven voices in the picker did not exist.**
  `VR6AewLTigWG4xSJukFG` ("Arnold") has been in `ELEVEN_VOICES` since the
  voice round, offered on the console and all three phones, and ElevenLabs
  answers 404 `voice_not_found` for it. Choosing it failed at the one moment
  the feature exists for — somebody asking to be spoken to.

      asked     is the voice list well-formed
      mattered  does every voice in it answer

  Nothing in this repo could have caught it. The list is hand-copied opaque
  identifiers on somebody else's service: the shape is fine and the id is a
  string whether or not it resolves, and the suite has no key. All seven were
  checked against a real account by synthesising a line in each; six answered
  and one did not. It is replaced with a voice that speaks, and
  `test_the_voices_we_offer_are_voices_that_exist` re-runs the same check
  whenever `ELEVENLABS_API_KEY` is present — synthesising rather than looking
  up, because that is the call the product actually makes — and skips when
  there is none rather than mocking a service into agreeing.

### Added

- **The speaking allowance is visible before it runs out.** Nothing here
  read a quota, so a spent one was invisible: the send is refused, `speak`
  raises, the route answers 502, and every client — console, iOS, Android,
  Windows — falls back to the device's own voice on any non-ok status. That
  fallback is right, and it is silent. The Guardian went on talking in a
  flatter voice and the person paying for the account found out by noticing.

      asked     does a spent allowance still speak
      mattered  does anybody find out it was spent

  `GET /voice/quota` reads ElevenLabs' account row and publishes what is
  **left** — the provider's own field is `character_count`, which is what
  has been *spent*, and reading that name as a balance shows a fresh
  account as nearly out and a spent one as full. The subtraction is done
  once, in the backend, floored at zero because a spent account reports a
  count above its limit. The Held screen carries the line beside the other
  disclosures about where your words go; the phones carry it on the voice
  card, in amber when it is gone, saying what happens next rather than only
  that a number reached zero.

- **The price list says whether the gate is running.** `GET /plans` reports
  `enforcing`, and a sentence with it while the beta stands enforcement down.
  `locked` answers what a plan will cost, which is what a price list is for;
  it cannot answer whether anybody is being refused today, and for one
  release nothing could — the stand-down was a module constant no response
  mentioned.

      asked     does the price list say what a plan costs
      mattered  does it say whether the gate is running

  QRME's cross-product smoke is what found it. That run drives a Basic
  account into `synthetic_agents`, asserts the 402, and had nowhere to ask
  whether the gate was standing; it broke seven steps in while every tier
  test in this repo kept passing, because they all force the flag on. The
  Held screen shows the sentence, so a tester reading the prices is not
  quoted a paywall that is not there.

## [0.71.1] - 2026-08-14

**There are no functional changes to JIM-mini in this release**: cut with
the siblings. In QRME, `widgets.py` imported a POSIX-only module at the top
of the file, which took the whole API down on Windows — the frozen desktop
backend would not start, and two releases published with no installers
attached at all.

## [0.71.0] - 2026-08-14

### Added

- **The session you leave running.** Until now this product had one
  conversational door, `POST /coach/{user_id}`, and it was a *turn*: you said
  something, it said something, and nothing was left holding. Which model
  answered depended on `PUT /model/{user_id}`, so "the online one" and "the
  offline one" were the same route with a different provider behind it —
  distinguishable only by the amber banner when a turn degraded.

  `jim/engaged.py` is the thing that was missing. `POST /engaged/{user_id}`
  opens a session; it stays open across turns and through the app being
  closed, and ends when you sign off rather than when you stop typing. Three
  consequences:

  - **It does things rather than describing them.** Twenty-six tools —
    writing a journal entry, setting or moving a goal, starting or ticking a
    habit, adding a medication, booking something, changing how it talks to
    you, changing which model answers — each one going through the app's own
    door with *your* credential forwarded, so its reach is exactly yours and
    no longer-lived. `GET /engaged/reach` lists them in sentences, carries no
    token, and is exempt from the plan gate: how somebody decides whether to
    open one is not the thing being sold.
  - **Everything it changes can be taken back.** Every acting row declares
    its own inverse as data — a `remove` that deletes what was created, or a
    `replace` that reads the prior value *before* the write and replays it
    after. `GET /engaged/{user_id}/acts` is the trail and
    `POST /engaged/{user_id}/acts/{act_id}/undo` is the way back. One act
    cannot be taken back and says so in words: putting your question to a
    QRME specialist sends your own words outside this product, and nothing
    here can unsay that.
  - **Signing off is a handover, not a close.** What the session was about is
    deposited into the store the offline stack predicts from — the same path
    a paid coach turn already takes — and anything named on the way out
    becomes a standing watch: carried into every offline coach answer, and
    raised unprompted by `presence.beat` above everything the product noticed
    by itself.

  What it may **never** touch is a carve-out enforced against the registry
  rather than trusted to review: emergencies, alarms, escalation, the vigil,
  the crash watch, the beacon, the referral release, every money path,
  membership, erasure, the synthetic self, and anything belonging to another
  person. Those are refused by absence — the agent cannot call what is not in
  the list — and `engaged.NEVER` is checked both ways, so an entry that
  matches no route fails the suite rather than sitting there looking like a
  protection.

- **Ways back that were missing long before an undo trail needed them.**
  `DELETE /journal/{user_id}/{entry_id}`, `DELETE /checkin/{user_id}/{id}`,
  `DELETE /goals/{user_id}/{goal_id}`, `DELETE /habits/{user_id}/{habit_id}`
  and `DELETE /habits/{user_id}/{habit_id}/log/{day}`. A person could write
  in their own diary and had no way to unwrite it; could record how they felt
  on the screen that feeds the crisis pipeline and had no way to unrecord it;
  could mark a goal abandoned and never remove it. These are the inverses the
  trail replays, and each is a door worth having on its own account.

- **All four clients, in the same round.** The console gets screen 109; the
  iOS, Android and Windows shells each get the same surface — the reach card
  above the button, the transcript, the undo trail, sign-off with its topics
  field, and the standing watches. Thirty-four strings in ten languages,
  emitted into Swift, Kotlin and C# from one source so the three tables cannot
  drift from each other.

  It landed everywhere at once rather than on the console first, and the
  reason is the feature's own bargain: full-act autonomy is defensible
  *because* every act is listed with the way back beside it. A client that
  could open a session and speak into it but could not show the trail would
  have taken the permission and dropped the condition it was granted under.

### Changed

- **An engaged turn the offline model served says so instead of answering.**
  `coach.reply` degrades gracefully — when the stub answers, the offline
  pipeline takes over and produces something genuinely useful. That is right
  for a screen whose job is to *say* something. This screen's job is to *do*
  something, and the stub cannot ask for a tool, so an engaged session on a
  box with no key would have answered in canned prose, taken no action, and
  looked exactly like one that had considered the request and decided against
  it. It now stops with `engaged.needs_the_online_model`, the session stays
  open, and nothing was changed.

      asked     did the turn come back with text
      mattered  did the model that can act answer it

- **The refusal audit reads sentences that live in a table.**
  `test_the_guardian_refuses_in_one_language` walked the AST for
  `HTTPException` and the domain error classes, which sees a raise site.
  `engaged` raises a *key* and the handler resolves the sentence afterwards,
  so sixteen real refusals would have gone out in English while the guard
  reported zero. Asked whether every refusal *raised with a sentence* was
  translated; what mattered was every refusal *a person reads*.

## [0.70.1] - 2026-08-13

**There are no functional changes to JIM-mini in this release**: cut with
the siblings. In QRME, the widget runner asked whether *an* interpreter
existed and never whether it was new enough, so a host carrying Node 18
reported ready and then failed every run.

## [0.70.0] - 2026-08-13

### Fixed

- **The care beacon's alarm sends the message it always claimed.**
  `POST /c/{id}/alarm` answered every finder with "The people watching over
  this person have been alerted" while nothing was sent to anyone. A
  personal beacon now pages a real channel when one exists — a minor's
  guardian inbox, an adult's own trusted crash-watch channel — every attempt
  lands in the `relay_pages` ledger under the alarm's id, and the sentence
  the finder reads is derived from the outcome rather than asserted. One
  honest "No message went out from this page…" for every way it can fail;
  which way it was is the owner's information, in their ledger.
- **The apology for a failed route is in the reader's language.** The
  catch-all is a middleware — `@app.exception_handler(Exception)` sits
  outside the CORS layer, so a 500 raised there comes back without the
  header and the console reads it as unreachable — and being a middleware,
  no guard was asking it anything. Its sentence sat inline in English;
  `i18n.SERVER_ERROR` is now a named constant translated like every other
  refusal.
- The tutorial's lessons had been appended to over many rounds and no longer
  ran in chapter order; the help box could not start the tour it described.
- Android's first-aid surface spoke English at the worst moment — heading,
  the call-emergency-services line, the waiver sentences and the revoke note
  now ride the same keys the iPhone already held.

### Added

- **The reports come home.** `POST /v1/problems` on this backend, with
  `GET /v1/problems` behind `JIM_PROBLEMS_KEY` or the backend's own machine.
  Strictness matters more here, where the messages a report must never carry
  can be health content: anything outside the whitelist is a 422 naming the
  field, and rows fold into counters.
- The last four doors reach the phones: the three `qr.svg` codes as URL
  builders with their address shown as selectable text, and the watch drip
  as a button — one reading by hand through the door the automation uses.

### Changed

- `day` carried two types on this product's wire — a calendar date on habit
  logs and problem counters, a 1-based ordinal on the meal plan. The ordinal
  is `day_number` now, on the server and in all four clients.
- The console-untranslated record reads 93 rows where it read zero. The zero
  was never true: the extractor could not see a sentence chosen at render
  time, and the first honest reading under the widened reader is written
  down with the decision that raised the ceiling.
- The watch lights and their minimized dot clear the phone's tab bar.
- The three-repo guard estate: `shared_guards.txt` 469 → 489,
  `guard_divergences.txt` 136 → 121, both byte-identical in the three repos.

## [0.68.0] - 2026-08-12

### Added

- **The plate is the receipt.** `POST /users/{id}/meals`: point the camera at
  the plate, say a few words, done. The photo is sealed like a clinical
  capture (metadata stripped, vaulted, refused without a vault); the note is
  the log, kept local so the offline coach's nutrition area can read today's
  meals with the network cut. An online model, when standing, tidies the note
  into a coarse items-and-portions line and never invents what the note
  doesn't say (`described_by: note | model | photo`).
- **The week in words.** `POST /users/{id}/letters` writes one short letter
  about the last seven days, composed only from what was logged — check-in
  averages, meals, habit marks, journal entries, goal movement — with the
  digest stored beside the prose. A week with nothing logged gets no letter.
- **The answer before the room.** `POST /users/{id}/drills` deals an
  interview question from a curated local bank with what it probes stated up
  front; the answer is read against the probes by the online coach when one
  is standing, and by the checklist itself when not (`described_by: model |
  checklist`). One question, one answer; the practice reaches the career
  coach's readable context.
- **The statement is the reading, and the consent is written down.**
  `POST /money/{id}/statements` seals a statement file in the vault and reads
  it by deterministic local CSV arithmetic — a closing balance walks the same
  observe path a hand-typed reading takes, so the guardian ladder wakes off
  the file itself. `POST /money/{id}/links` writes a bank-link consent
  through an aggregator (plaid, tink, truelayer, mx) that registers a
  watchable account; sync answers with the exact truth instead of inventing
  balances, and revoking is never gated.

### Fixed

- The Android client's newest response parsing used constructors this
  shell's `request` never matched; rewritten to `request(...)` /
  `getArray(...)` so the shell compiles.
- The drill's reading travels the wire as `critique` — `feedback` already
  meant a map of ratings, and one name means one type.

## [0.67.0] - 2026-08-12

### Added

- **The plug-ins carry the readings.** Connected apps' collections route to
  where they actually do work: a `reading` walks the same intake the watch
  uses — vigil stand-down, detection, drift, baseline — an `environment`
  item lands where the offline stack's environment layer reads it, and
  everything else rides as linked context, vaulted when a vault stands.
- **The tandem carries the pulse.** The readings that trigger a detection
  cross the Guardian→QRME handoff as the chat's biometrics, so the
  specialist's reply is conditioned on the pulse itself. Only what was
  actually measured ships — the stored resting baseline never travels as a
  current reading, and a note-only crisis carries prose alone. The vitals
  are sealed in the vault record beside the message.
- **The room warns before it wounds.** Collected environment items are read
  for the room's dangers on arrival — a deterministic, offline, auditable
  hazard table (gas, carbon monoxide, smoke, falls, heat, cold, ergonomic
  strain, air quality), every entry carrying the reference its advice is
  drawn from. Hazards land as Life insights and ride back on the collect
  response, worst first.
- **The guardian holds the code.** A minor's signup requires a parent or
  guardian address distinct from their own; the activation code and link are
  delivered to that inbox, resends follow it, and activation records whose
  address consented and when. Consent is a verified click, not a ticked box.

## [0.66.0] - 2026-08-12

### Added

- **The coach answers with the network cut.** The always-on half of
  the product, built the way the owner drew it — the Transformer
  diagram read as architecture. `jim/pipeline.py` is the offline coach
  engine: the question arrives as the input, and context joins it as
  residual add layers — [user data] first, then the current readings
  ([vitals] from the bands, [speech], [tone], [environment]) — each
  add followed by a norm that beats the block into a fixed shape.
  Prediction chooses from the stored knowledge weighted by the
  normalized context, the output side gets its own norm, and every
  layer lands in the reply's provenance. The module never touches the
  network — no provider import, no socket — and a guard reads its
  imports and holds that promise. The expensive model is a teacher
  hired occasionally; the coach is the graduate who lives with you.
- **The store the stack predicts from grows three ways.** The curated
  pack was jampacked to thirty-nine hand-written, referenced entries
  with a real shelf in every one of the six areas — two ratchets hold
  the total and the thinnest area. JIM's learned excursions now
  actually reach the coach: the note under
  `/excursions/entry/{cid}/learn` had said "the local model now uses
  them" while nothing read them — the claim has behavior now. And a
  paid model turn deposits its distilled answer into the store on the
  way out, deduped by topic, so the same gap is never bought twice:
  every token burned becomes a permanent asset.
- **JIM imports knowledge as the coach needs it.** A question nothing
  stored could answer is recorded as a gap; the curriculum
  (`GET /coach/{user_id}/curriculum`) lists the gaps first, then reads
  the monitored surface — bands with a learned baseline, active goals,
  the dose board — minus what the store already covers, each
  suggestion naming the monitor that asked. One press of study
  (`POST /coach/{user_id}/study`) runs the excursion and learns the
  findings in the same motion, closing the gap it came from. The store
  is readable in full at `GET /coach/{user_id}/store`, provenance on
  every entry — the user's own asset, grown by use. All three routes
  carry their four doors (console, iPhone, Android, Windows), every
  new word from the ten-language tables, and an empty curriculum with
  no topic named refuses in ten languages. On the wire the store's
  list is `excursions` and its text is `lesson` — one wire name, one
  type.

## [0.65.0] - 2026-08-12

### Version alignment

No JIM code changed this round. The work was QRME's rooms: the join
door its lobby pitch had promised, the standing rooms learning to be
one place instead of a stamp, and the home screen's friend faces
opening the friend's page. The three products are cut together, so one
number names one combination of all three.

## [0.64.0] - 2026-08-12

### Added

- **The footsteps.** A counter in the console's top-right corner: how
  many people are enrolled here, as an aggregate — no name, pseudonym
  or id rides with the number. It travels on `/health`, the request
  every client already makes at launch for the version handshake, so it
  cost no new door. Only finished enrollments count; an attempt that
  never verified is a mistyped address as often as a person. The
  sibling products carry the same chip in the same corner in the same
  ten-language wording.
- **The fifth wearable family is every other wrist.** The watch picker
  gains "Another brand's watch (via its own app)", and its recipe is a
  check, not a promise: look for the health-store sync in the vendor
  app, verify on the phone's side because the toggle often is not in
  the app's menus, and follow the existing recipes when the app appears
  in the store's list — the drip reads the phone's health store, not
  the watch. When the app never appears, the card says the captive-data
  truth out loud and points at the Monitor screen. One dict entry, no
  client changes. The field report: a GT4 Pro-1 paired to Olywear,
  which never requests Health access at all.

### Changed

- **The footsteps chip shrank to a footprint** — just the mark and the
  number, the sentence in the tooltip — after the first, wordier
  version sat on top of a screen in the sibling product.

### Fixed

- **The guard that only existed where the bug never was.** The
  `</script>` hardening of `_js` shipped in 0.63.0 in all three
  products; the test holding it existed in none. It stands in all three
  suites now and enters the shared manifest.

## [0.63.0] - 2026-08-11

### Added

- **The imported link, finally visited.** A `collect` connection has
  carried the account's public address since the day it was made, and the
  collect door only ever stored what the owner pasted.
  `POST /social/connection/{cid}/scrape` goes to the address and ingests
  what a browser would show anybody — the title, the metadata bio, the
  visible text — as a `social:<platform>` context event, so the Guardian
  understands more of the life it is looking after. An offline deployment
  refuses before any socket opens (the gate lives inside the fetcher
  itself, so a second caller added tomorrow inherits the check); a
  connection without a handle is told so; publish connections do not
  scrape. Doors on the console and all three shells, and the three
  refusal tests share their names with the sibling products' copies of
  the same door.

### Fixed

- **The console fits the phone it runs on.** The two field reports —
  the portrait screen that did not fit, and the long landscape list that
  stuck halfway and had to be forced — share one root: a grid item
  refuses to shrink below its content, so the content pane grew past its
  track, the app overflowed the viewport, and the page itself
  half-scrolled instead of the pane. `min-height` and `min-width` zero
  let the tracks clamp; the app height tracks `100dvh` where the browser
  has it, so the bottom row sits above the URL bar; and the sidebar
  scrolls on its own where a landscape phone gets the desktop column.
  The same defect was in all three consoles and is fixed in all three.

## [0.62.0] - 2026-08-11

### Added

- **The phones reach parity with the console.** Eleven rounds stacked into
  one branch, and every route the backend serves now has a door a person can
  open on iOS, Android and Windows — the per-shell doorless ledgers, which
  opened this audit at ~300 rows each, close at the four rows that stay by
  design (three qr.svg renderers with no native SVG door, and the watch
  drip's token door, which is the automation's rather than a person's).
  In order: the account the phones never had (signup, sign-in, verification,
  password reset, OAuth with an open-browser claim poll, sittings); the
  Guardian's day (calm, activity, context, conditions, personality, goals,
  feedback, insights, events, the progress report, plans, the companion's
  unprompted word); the specialist economy (roster and seeds, the QRME
  catalog bracket, multi-step task hand-overs, medical referrals that
  release only through the QRME signing ceremony, the consented provider's
  view); the record and the veil (the access log with its kept-versus-empty
  distinction, cloud status and contribution revoke, incidents, pages,
  locality, plans); budgets and memberships; beacons a stranger can scan
  and the relay that escalates people, not sirens; safe knowledge
  excursions with their redaction price on the row, the community window
  and QRME's feed through the tandem.
- **The voice pair.** `/voice/speak` and `/voice/transcribe` land on all
  three shells: a Talk card that plays the configured voice's audio and
  falls back to the device's own voice when no speaking service is set —
  silence would be the wrong failure — and a microphone that records a
  short clip and shows what the Guardian heard. AVAudioRecorder,
  MediaRecorder and MediaCapture respectively; the iOS spec now carries the
  microphone usage string, Android's manifest RECORD_AUDIO, and a refused
  microphone gets its own sentence rather than silence.
- **PATCH from the phone that cannot say it.** Android's HttpURLConnection
  has no PATCH; the backend honours `x-http-method-override: PATCH` on
  POST alone, the Kotlin client translates, and
  `test_the_verb_the_phone_cannot_say.py` pins the contract.

### Changed

- **The screens behind the tabs speak the reader's language.** The
  Check-in, Coach, Life, Welcome and feedback screens on all three shells
  swap their remaining English literals for ten-language lookups; the
  diverged native tables are reconciled (rows Android alone carried now
  reach iOS and Windows), the Welcome hero and pitch carry the console's
  own translations verbatim, and the untranslated ratchet falls from
  45/46/57 to 12/31/24 across iOS/Android/Windows — what remains is
  enrollment/terms prose and wire vocabulary, each left deliberately.

## [0.61.1] - 2026-08-11

### Added

- **Ability is not a gate.** An accessibility statement with a door under it,
  on every client. The console's new **Accessibility** screen — reachable
  *before* enrollment via `#access` and from onboarding — names the needs
  this product is built for (blind, deaf, mute, motor, cognitive, dyslexia,
  motion sensitivity) and says, for anything the list misses, that the gap is
  in the list and not in the person. Under the statement sits a
  three-question report form: what were you trying to do, what stood in the
  way, what would help. `POST /access/reports` takes those answers with **no
  account, no token and no name** — the `access_reports` table has no
  identity column to fill — and seals each report to the PDI vault when one
  is configured. Reports are never relayed to the shared error collector;
  they are read back by `GET /access/reports` under the deployment's
  reviewer token (`JIM_ADMIN_TOKEN`) alone, a role that fails closed beyond
  localhost. The iOS, Android and Windows shells carry the same statement
  and the same form. Screen 108, tutorial lesson and ten-language copy
  throughout.
- **The answers are announced.** The coach's guidance card, the specialist's
  reply and the check-in's verdict are `aria-live` regions, so a screen
  reader hears the answer arrive instead of a card appearing silently.
- **A ledger of known gaps that only shrinks.** `jim/tests/a11y_backlog.txt`
  opened this release with two admitted barriers and closes it at zero, each
  closure held by a test — one shared across the three products, taking the
  common guard manifest to 461. The ceiling ratchet means a new gap can only
  enter by a visible, deliberate edit.
- **The console honours `prefers-reduced-motion`** and sets the document's
  language attribute to the visitor's language — enforced by
  `test_ability_is_not_a_gate.py` rather than promised.

### Changed

- **Signup opens for the beta.** `JIM_SIGNUP_KEY` gains a keyhole: set, it
  gates enrollment with an invite key; empty or unset, signup is open — and
  open is the shipped default in the beta compose file. Free tiers stand
  while testing lasts, and the terms say so.
- **Terms 1.2.** Version 1.1 said the beta is a beta and free means free for
  now; 1.2 adds the accessibility commitment in the same
  no-claims-without-behavior voice, naming the real door.

## [0.61.0] - 2026-08-10

### Fixed

- **The console was blanked by its own Content-Security-Policy.** The nonce
  policy written for the server-rendered pages was stamped on every HTML
  response — including the console's `index.html`, whose script and stylesheet
  are external files no per-response nonce can reach. A browser refused the
  bundle and rendered a dark, empty page: HTML 200, nothing running. That is
  what jim-mini.com first served, while every in-process test passed, because
  a `TestClient` reads the policy and enforces none of it.
  `pagehead.console_policy` now names `'self'` where the page policy names a
  nonce — still refusing inline script — and the over-HTTP suite builds its
  own console dist so the measurement runs on CI whether or not `app/` was
  built.
- **The release-bodies sweep could not start, and then measured the fetch.**
  An edit had left its embedded Python unparseable, so every scheduled run
  died before deciding anything. Repaired, its first honest run accused the
  kept `app-v0.24.0` of losing a frozen body it visibly still carries:
  paginated output was re-split by a regex that matched a `]` `[` pair inside
  a release body's own markdown, and dropped what it broke. `gh api --slurp`
  now returns pagination as one JSON document, a guard proves the fetch
  returned every release the record names, and two local tests hold the line:
  the workflows' scripts must parse, and the staleness decision is driven
  with this product's own frozen opening.

### Added

- **The front door.** The bare domain answered `{"detail": "Not Found"}`,
  because the console lives under `/app` and nothing said so. `/` now
  redirects to `/app/` whenever a console is mounted — headless deployments
  keep their honest 404.

## [0.60.9] - 2026-08-10

### No change to this product

The release-body work reaches its end. Every release that inherited the frozen
v0.24.0 body has been rebuilt from its own CHANGELOG entry, and
`stale_release_bodies.txt` reaches a ceiling of 0 with `app-v0.24.0` kept
deliberately — its body *is* the v0.24.0 notes and is correct for it.

    asked     how many rows are left
    mattered  how many releases are still wrong

Three checks reported success while doing nothing and are fixed: a staleness
test keyed to a sentinel that was one product's number, a backfill that trusted
the record instead of the releases, and a record guard whose header pattern
required a plural and crashed when the count reached one.

`generate_release_notes` is settled too: 0.60.8 published with a curated body
and the body came back intact.

Recorded here to keep the three changelogs in step at one version.

## [0.60.8] - 2026-08-10

### No change to this product

Two findings carried from PDI's round, both of which apply here.

`release_fields.txt` -- byte-identical in all three products -- replaces the
prose list a bump was driven from. It names every version field individually,
including the three a search for the outgoing version string cannot find, and
three guards read it rather than trusting that anybody did.

`RELEASE_NOTES.md` and `sync-release-notes.yml` are deleted. 412 of 530
published releases across the three products carried the same v0.24.0 prose,
because that file was published verbatim over every curated release body since.
`release-integrity.yml` replaces them, and reads rather than writes.

PDI's console also reached a floor of zero. Recorded here to keep the three
changelogs in step at one version.

## [0.60.7] — 2026-08-09

### No change to this product

PDI's console round: the finding that a screen importing the translator is not
a translated screen. Two of its screens had been counted as localized since
0.48.3 while still holding fifteen English strings between them, six of which
were strings its table already carried in all ten languages. A guard now holds
the claim that a screen asking the table for a word may not also hard-code
one, and five further screens were localized. 91 → 32.

Recorded here only to keep the three changelogs in step at one version.

## [0.60.6] — 2026-08-09

### No change to this product

PDI's console round: Positions and Bridges localized, and its English count
corrected a third time — the reader asked for a letter, a space and a letter,
which no heading joined by `&amp;` or a hyphen has. 154 → 168 → 91. Recorded
here only to keep the three changelogs in step at one version.

The portable part is the shape rather than the code. This product's console
reader records every extracted string verbatim in both directions, so it has no
phrase test to be wrong about; the defect could not occur here. That is worth
stating rather than assuming, which is why it was checked before the round was
called PDI-only.

## [0.60.5] — 2026-08-09

### No change to this product

PDI's console round: Carriers and Exchange localized, 225 → 154, on the
honest count 0.60.4 established. Recorded here only to keep the three
changelogs in step at one version.

One thing in it belongs to all three. Two guards in that product still greped
their screens for English sentences, and localizing the screens turned them
red — the 0.48.2 lesson, *localizing a screen blinds the guards that grep it*,
arriving in the last two guards that had not had it. Both now follow the
sentence to wherever it lives rather than asserting the English is in the
file. Worth a look here the next time a screen in this product moves its words
into a table.

## [0.60.4] — 2026-08-09

### The reader this product already had turned out to be the one that was right

No change to this product. The round was PDI's, and it is recorded here
because the finding is about a method all three share.

PDI read its console's English with three regexes, the first being
`>\s*([A-Z][^<>{}\n]{2,})\s*<`. This product moved off that shape rounds ago
to `app/scripts/jsx-text.mjs`, which parses with TypeScript's own parser and
returns every `JsxText` node. Nobody had run the two side by side until now.

    asked     how much English does this pattern match
    mattered  how much English does a person read

**233 against 177**: a quarter of PDI's console prose was invisible to it —
every wrapped sentence, every sentence with a value interpolated into the
middle, every phrase not starting with a capital. Hidden in the direction that
makes a ratchet look satisfied, and two of that product's localization rounds
were graded against the low number.

The lesson is not about regexes. It is that two products can carry the same
guard by name and not by reach, and the only thing that finds it is running
both readers over the same file and comparing. `shared_guards.txt` says the
three suites ask the same questions; it cannot say they answer them as well.

## [0.60.3] — 2026-08-09

### A check that cannot fail before the merge is not a check

0.60.2 found `native.yml` red for a hundred and twenty-three consecutive runs.
Nothing was wrong with what it ran. What was wrong was *when*: it fired on
`pull_request`, which never opens here because releases are fast-forward
merges, and on `push` to `main`, which happens after somebody has decided to
ship.

`ci.yml` carried the identical trigger. It had been red for twenty-nine
consecutive runs.

    asked     does the workflow pass
    mattered  can the workflow's answer still change the decision

- **The four red guards.** They shell out to `app/scripts/jsx-text.mjs`, a
  TypeScript-AST reader used because three separate regexes over the same
  source each hid real strings. It imports `typescript` from the app's own
  `node_modules`, which the job running pytest never installed. Those guards
  are written to fail loudly rather than report a comfortable zero, and that
  is exactly what they did — into a log nothing read. The job installs the
  app's dependencies now.
- **The trigger** is any branch push, the same fix `native.yml` got.
- **`test_a_check_that_cannot_fail_before_the_merge.py`** reads the checked-in
  triggers and fails when a gating workflow cannot fire before a merge. Three
  workflows are deliberately post-merge — the container e2e run and the two
  that fire on a release tag — and each is named in `POST_MERGE` with its
  reason. Naming one is a decision; the failure this exists for was nobody
  having made the decision at all. A named exception for a deleted workflow
  fails too: the exemption must not outlive its reason.

  It cannot tell whether a workflow is passing. It can tell whether a failure
  would arrive in time to matter, which is the part that was missing.

## [0.60.2] — 2026-08-09

### The compiler was in the room the whole time and nothing listened

`native.yml` had been failing for over a hundred runs on a trigger nothing
in the release loop ever reached. It fires on any branch push now, and every
line below was named by a compiler rather than found by reading.

    asked     do the shells read the members they name
    mattered  do the shells compile

- **The client was parsing itself twice.** `request` returns a `JSONObject`,
  and five call sites wrapped its result in `org.json.JSONObject(...)` — the
  continuity read and its forget, the offline posture, and both halves of the
  take-it/end-it pair. The constructor matched none of its three overloads,
  so every read off the result was a reference to nothing
- **Four rows of `L10n.kt` had lost their key line** — `action.send`,
  `action.save`, `action.translate`, `action.refresh` — leaving a bare
  `"en" to "Send",` where a member declaration belonged. Restored, and the
  two that had drifted from a sibling shell brought back into line
- **`L10n.fill` did not exist here.** iOS has carried it since the table
  shipped and one Android call site used it anyway, where it resolved to
  something of type `Boolean`
- `AppState.kt` carried `private set` twice — the same bad paste the QRME
  shell had, and the same syntax error hiding every member after it
- The alarm card wrote four `Result`s straight into their unwrapped types;
  `LifeView.Tab` got `circle` back last release and its `label` switch did
  not; `SafetyView` still called `Api.shared` in five places
- The Android L10n table is split into four functions before it reaches the
  JVM's 64 KB per-method ceiling, which is what stopped QRME's build outright
- Five Windows pages reach for `Dictionary`, `List` or LINQ in files whose
  `using` lists never asked for them

## [0.60.1] — 2026-08-09

### A fix to the cascade fixes the next erase, not the last one

0.59.9 derived `delete_user_data` from the schema. Every account erased
*before* that release was erased by a list of twenty-one table names against a
schema of sixty-three, and the forty-three tables it missed are still sitting
in every deployment that has been running since — the money guardian's
accounts and mandates, the medicine cabinet and every dose logged from it, the
clinical captures, and the standing permissions in `crash_watches` and
`vigils`.

Nothing in the product will ever look at them again, and that is the whole
problem. `users` is gone, so the API answers 404, so no code path visits those
rows. A person who pressed *erase everything* has an account that reads as
gone and a medicine cabinet that is not.

    asked     does the erase work now
    mattered  what did it leave the last time it did not

### Added

- `python -m jim.orphans` — a one-off maintenance sweep for the residue.
  `survey()` reads and the command is **dry by default**; `--apply` is the
  only thing that deletes, and `--json` gives the same survey machine-readable.
- Its scope is the cascade's own reader (`life.user_scoped_tables()` minus
  `life.ERASE_KEEPS`, plus the child tables in `life.ERASE_THROUGH`) rather
  than a second list.
- A row counts as an orphan only when its `user_id` names an account not in
  `users`. Rows with a NULL or empty subject are left alone.
- `test_what_the_old_cascade_left_behind.py`, whose sharp property is **does
  it leave a living account alone**. Both directions confirmed by injection.
- **The exit reaches the phones.** 0.60.0 gave a phone-only person a way to
  take their data and no way to end it; `DELETE /data/{user_id}` now has a
  door on iOS, Android and Windows, beside the portability card, armed only by
  typing the word — the same discipline the console has used since it had the
  button. Localized in ten languages on all three.

### Fixed

- **The Windows shell did not compile.** Three defects, all mine, all shipped
  in 0.60.0's Windows door: a lost closing brace that ran `OnProblemsPreview`
  into the next method, a `st.UserId` on an `AppState` that holds `Uid`, and a
  response class that never landed because it was inserted against the wrong
  declaration.
- **`SelfProfilePage` had never compiled.** Thirty-eight reaches for
  `s.UserId`, `s.UserToken` and `s.Api` — the synthetic self layer's whole
  desktop surface, every handler of it, sitting in `main` since the page was
  written.
- Both found by widening `test_the_member_that_isnt_there.py`, which read
  `AppState.Current.X` only when a page spelled it out in full. A page that
  puts the singleton in a local first was read as reaching for nothing at all.
  Aliases are now expanded, and **only** when the name means that and nothing
  else in the file: the first cut rewrote whole files and reported twenty-eight
  perfectly real members as missing.

## [0.60.0] — 2026-08-09

### An export is measured against the schema too — and drops the credentials

0.59.9 derived the **erase** from the schema in all three products, because the
lists that stood in for it had gone stale: an operation advertised as *every
trace* reached a third of the tables. The export is the same question turned
round.

    asked     can a person delete everything we hold
    mattered  can a person see everything we hold

### What it was

There was **no export at all**. This product keeps a medicine cabinet, a money
guardian's accounts and mandates, clinical captures, a journal and a continuity
vector, and offered its owner a way to erase all of it and no way to take it —
while the suite gateway's GDPR Article 20 bundle listed this product's
contribution as *a progress report*.

`GET /data/{user_id}` now answers, next to the `DELETE` that was already there.

### Two properties, and the second is not the first

An export must be **complete** and must **not hand back a live credential**.
Those pull in opposite directions, and the honest resolution is per column
rather than per table: a row is the person's own history, and a token inside it
is a credential in whatever they do with the file — a bundle gets downloaded,
mailed to a clinician, dropped in a cloud folder.

The redaction is a **rule** rather than a list, and that is not tidiness. The
first cut was a list of exact column names, and the new guard caught it on its
first run — three credential columns in tables the export now reaches, none of
them in the list. A list of columns goes stale exactly the way the cascade's
list of tables did.

Deliberately *not* the bare word `hash`: a hash-linked audit record is what a
person verifies their own export with, and a credential is what somebody can
present. The two are not the same and the rule says so.

### The symmetry, asserted

A table the erase clears and the export omits is a person who can delete
something they were never shown. A table the export carries and the erase
misses is 0.59.9's defect. The guard compares the two sets directly.

There is one deliberate asymmetry, and only in the vault: its audit chain
survives a wipe because it is the proof the wipe happened, and a bequest is
*retired* rather than deleted so an heir's credential fails with **revoked**
instead of silence. Both are still the tenant's to read, so the export carries
what the erase keeps — the one place these two answers differ on purpose.

## [0.59.9] — 2026-08-08

### An erase is measured against the schema, not against a list somebody wrote

`delete_user_data` says *erase every trace of a user across all tables*. It
named twenty-one tables in a tuple. The schema has **sixty-three** with a
`user_id` column, so the erase left forty-three standing:

    accounts        money_accounts   money_mandates   money_orders
    budgets         budget_spend     savings_goals    medications
    med_logs        captures         care_plans       care_teams
    care_beacons    crash_watches    vigils           mic_channels
    mic_sessions    user_continuity  user_finetunes   user_models
    …and twenty-three more

The money guardian's accounts and mandates. The medicine cabinet and every
dose logged from it. The clinical captures — photographs of somebody's body.
And `crash_watches` and `vigils`, which are not records of anything: they are
standing permissions for this product to act on that person's behalf, still
live for an account the API answers 404 for.

The sibling vault had already fixed this shape and the fix had not travelled.
Its docstring already said the general thing: *a migration that adds a table
is covered by writing it, not by remembering this function.*

    asked     did we delete what the handler names
    mattered  did we delete what the schema holds

### Why the list kept losing

It was not neglect. Both siblings' lists had been *corrected*, more than once,
and every correction was right. JIM-mini's most recent one found a watch
channel outliving its account and added three tables — `watch_channels`,
`contribution_log`, `waivers` — because those three carried a live credential
rather than a record. That fix was correct and did nothing about the next
table, and `crash_watches` and `vigils` are the same kind of row and were
still standing after it.

A list is a claim about a schema, made once, by somebody who could see the
schema that day.

### How it is checked

By writing a row into **every** scoped table, erasing, and looking. Not by
exercising features until rows appear: the tables a test can reach through the
API are the tables somebody thought to wire, which is the same blind spot as
the list. The rows are synthetic and go in through SQL — the question is
whether the cascade reaches a table, and a row is a row.

Plus the structural half, which is the part that survives the next migration:
the handler must not carry a list of table names at all, and must ask the
schema.

### The test does not borrow the reader it is checking

The first cut planted rows in the cascade's own table reader. Narrowing the
cascade narrowed the planting with it, so injecting the old hand-written list
reported *a blind reader* rather than *forty-odd surviving tables*. It reads
the schema itself now, and the injection names every table by name.

## [0.59.8] — 2026-08-08

### The check that covered one client of four

0.59.7 asked whether the shape a screen declares is the shape its route
answers with, found two screens throwing `.map is not a function` during
render, and asked the question of **the console alone**. The three native
shells decode the same answers into their own types, and a wrong one there is
the same failure with a different stack trace: `JSONArray` on an object throws
exactly like `.map` on one.

*No disagreement* from a check that was never run reads exactly like *no
disagreement* from a check that passed. That sentence is most of this arc.

### What each client says, and where

    console   req<T>(…)                     the generic
    ios       let x: T = try await request  the annotated decode
    windows   Send<T>(…)                    the generic
    android   JSONObject(body) / JSONArray  the parse itself

Android is the one worth reading twice: Kotlin has no decode type at these
call sites, so the *parse* is the claim being checked.

### What it found

No disagreements — the three shells were already right. What it found instead
was how unevenly the clients can be read at all:

    console 245   iOS 89   Android 3   Windows 88

JIM-mini's Android shell names a shape on **three calls out of a hundred and
fourteen**, because it discards the body on the rest. That is not a reader
failing; a client that never reads an answer cannot be wrong about one. But
three and three hundred cannot share a floor, so the per-client reach is a
**record that must not go down** rather than a number chosen by hand — the
same instrument the estate uses everywhere a count is honest but lopsided.

### Two readers this round got wrong first

Both are kept as prose beside the code that fixes them, because both reported
*clean*:

* a Swift `[K: V]` dictionary counted as a list, because both spellings start
  with a bracket — three false disagreements;
* the Windows shell spells its verb `Post(…)`, not `HttpMethod.Post`, so
  twenty-one calls defaulted to GET and every one was reported wrong.

Injections confirmed red before the round closed: a `GameSession[]` narrowed
to `GameSession` is named by client, file, route and declared type; and a
single character removed from the Android reader drops its reach from 316 to
310 and fails on the record rather than passing quietly.

## [0.59.7] — 2026-08-08

### `req<T>` is a cast, and a cast is a claim about the server nothing checks

0.59.6 read the requirement out of the application — which headers a route
needs — and asked whether the callers could meet it. This is the same question
pointed the other way: the route **answers** with a shape, the screen
**declares** one, and between them sits `req<T>`, which is a TypeScript cast
over a body parsed by `JSON.parse`. The compiler is satisfied. The screen
crashes.

    asked     does this call compile
    mattered  is the shape it names the shape that arrives

### What it was

`GET /users/{uid}/referral/clinicians` answers an **object**:

    {"area": …, "locality": …, "clinicians": [ … ], "reason": …}

The console declared `Row[]` and the Attending screen called `.map` on it:

    TypeError: clinicians.map is not a function

thrown during render, the moment anybody pressed *who would this reach*. And
the `reason` the backend composes for an empty list — *no clinician registered
in this area* — had never been shown to a single person, because the screen
threw before it got there. The screen now reads `.clinicians` and prints the
reason when the list is empty.

PDI had the same defect on `GET /hosting/{tenant_id}/history`.

### Why nothing else covers it

The route audit asks whether a path resolves and a method is accepted. The
door audit asks whether a route has a screen. Both were fully satisfied: the
path resolved, the method matched, the screen existed and called it. Nothing
asked what came back. `tsc` cannot help either, and that is structural rather
than an oversight — `req<T>` is generic over a type the caller supplies, and
the parsed body is `any`.

### The reader, and its own blind spot

Per **call expression**, not per path. The first cut keyed on the path literal
and reported sixty-odd disagreements, every one of them the reader pairing a
`POST` with the `GET` that shares its path; reading each `req<T>(…)` call and
taking the verb from that call's own body dropped it to one per product, and
all of those were real.

Before that, an earlier cut read **zero** call sites — its pattern stopped one
character short of the opening backtick — and reported that the consoles
agreed with their backends everywhere. It was right about every call it looked
at, because it looked at none. That is why this file carries a registered
floor (`console.calls_typed`) rather than trusting its own silence, and why
the verb reader is asserted per verb.

A union naming both shapes satisfies either: a client that copes with what
arrives is defensive rather than wrong.

## [0.59.6] — 2026-08-08

### The clients agreed with each other, and they were all wrong

0.58.0 asked whether the three shells sent every header the console sent, found
`x-llm-api-key` in one client and no other, and fixed it. It has held since.
This round found what it cannot see.

**Parity is a relative check, and a relative check is satisfied by everybody
being equally wrong.**

The instance is PDI's and the shape is the estate's: a vault under customer
custody required `x-tenant-key` on every record route, and no client in that
product sent it outside two heir routes. The comparison passed the whole time,
because both sides of it were wrong in the same direction — which is exactly
the case a comparison cannot report.

This product has no such header today. The guard is here anyway, because the
question is not about that header, and a guard that arrives after the second
instance is a guard that was written twice.

    asked     do the clients send the same headers as each other
    mattered  do the clients send the headers the routes require

### The guard, in all three suites

`test_a_header_a_route_needs_is_a_header_its_callers_send.py` reads the
requirement out of the **application** rather than out of any client. FastAPI
already resolves each route's header parameters through its whole dependency
tree, so a header required by an auth dependency is attributed to every route
that depends on it — the case a reader of function signatures misses entirely.
Then, per client, per route that client actually calls: can it present what
that route requires?

A header set in a client's shared dispatcher rides every request. A header set
beside one call rides that call. The first cut of this guard counted the two as
one, and that alone let the console pass on a header it sends to two routes out
of the eighty that need it.

The half no dependency walk can reach — a header taken straight off the request
inside a handler — is asked as a product-wide question, because the attribution
is genuinely unavailable. `x-signup-key` is recorded there with its reason: an
operator who sets it is closing registration to everybody, and a client able to
present it would reopen the door the operator shut.

### Liveness without a number

The three products lean on the two readers in opposite proportions — 103 routes
declare a header in one and a single route does in another — so a floor per
product would be three numbers to keep honest. The question is asked the other
way instead: every non-transport header a client sends must be one some reader
here found. A client sending a header no reader knows about is either talking
to itself or looking at a reader that has gone blind.

## [0.59.5] — 2026-08-08

### A value inside a script is not markup, and neither escaper knows both

0.59.3 shipped a Content-Security-Policy with a nonce and called it the second
line of defence. 0.59.4 made the first line — escaping into HTML — a guard.
This is the third sink, and it is the one where **both of those miss.**

Inside a `<script>` element the HTML parser ends the element at the first
`</script`, whatever the JavaScript quoting says. A value carrying `</script>`
closes the script early and everything after it is parsed as markup — in the
page's own nonced script, which the policy exists to permit.

    json.dumps    escapes what would end a JavaScript *string*  — not the element
    html.escape   escapes what would open an HTML *tag*         — not a JS string

    asked     is the value a valid JavaScript string
    mattered  can the value end the script element

QRME's `_js` composed both correctly. This product's was bare `json.dumps`,
and so was the inline string table it hands its script. A helper written once and copied into three
repositories, where the copy that drifted is the one whose entire job is to be
safe — the shape 0.59.0 found in a floor and 0.59.1 in a guard, now in a
security primitive.

**Not currently reachable.** Every value passing through these helpers is a
database identifier or a translated constant, and a path segment cannot carry
`</script>` because the slash breaks routing before the page is built. A
latent hole, fixed anyway: the next value somebody escapes with it is exactly
the one it was written for.

### One primitive, and a whitelist checked rather than trusted

`_js_literal` is now the single place that knows what ends a script element,
and `_js` and the string table are both built on it. Two helpers escaping for
the same sink is two chances to drift, and they had already taken one each.

The guard's own first draft is worth recording. Its call-site check allows a
value through if it arrives via `_js(` or `_strings(` — and when that was
written, one product's `_strings` was a bare `json.dumps`. **The guard would
have excused, by name, precisely the defect it exists to catch.** A whitelist
is a claim about behaviour; it is checked as one now.

### The consoles, swept and clean

The same question in TypeScript is `dangerouslySetInnerHTML`, `innerHTML =`,
`document.write`, `eval` and `new Function`. All three consoles have none of
them. The community wall's linkifier was read too: it splits on `https?://`
and gates on `startsWith("http")`, so a `javascript:` scheme cannot reach an
`href`.

That is a floor rather than a backlog — nothing to pay down, and the cheapest
time to keep it that way is while it is still true.

### Also

- Versions moved to 0.59.5 across the console, the backend, and the iOS,
  Android and Windows projects (build 59005).
- `shared_guards.txt` regenerated at 405 names; the divergence record holds at
  136.

## [0.59.4] — 2026-08-08

### The sweep that found the last one, kept

0.59.3 found reflected cross-site scripting on the sign-in callback by walking
every f-string that builds markup — **by hand, once, and then throwing the
walk away.** That round shipped the second line of defence, a
Content-Security-Policy with a nonce, and left the first one unguarded.

Escaping is the first line. So the walk is a guard now.

    asked     is this page correct
    mattered  can the next value somebody interpolates be markup

### Following the escape rather than looking for it

Most of this estate escapes one line above the template:

    ref = html.escape(card["reference"])
    body = f'<p class="ref">{ref}</p>'

A sweep that only asks whether `html.escape` appears between the braces
reports **8 rows** here, of which the six real ones are buried. Following
single assignments, and functions whose every return is escaped, and
conditionals and joins whose every branch is safe, cuts it to **3** — and all
three are composites the analysis cannot follow rather than values a reader
supplies. A record that is four-fifths noise is a record nobody reads.

It also refuses to read prose as markup. The first draft matched any f-string
containing `<` and `>`, which flagged a WebAuthn diagnostic containing
`http://localhost:<port>`. It now wants a closing tag, or an opening tag
carrying an attribute.

### What it catches

Put 0.59.3's defect back and the guard names it — file, line and expression:

    9 unescaped interpolations into markup, above the 8 recorded:
        routers/accounts.py:247: {error or 'no code came back'}

Four hundred releases of invisibility, and it was never hard to see. Nothing
was looking.

### Three attribute interpolations escaped on the way past

`<html lang="{language}">` depended on the caller having negotiated one of ten
known codes; `<option value="{value}">` on a hard-coded tuple; the policy
nonce on `secrets.token_urlsafe`. All three were safe and all three now escape
where they are written, which costs nothing and removes a permanent row from
the record.

### Also

- Versions moved to 0.59.4 across the console, the backend, and the iOS,
  Android and Windows projects (build 59004).
- `shared_guards.txt` regenerated at 397 names; the divergence record holds at
  136.

## [0.59.3] — 2026-08-08

### What a page promises a browser before it says anything else

0.59.2 built a harness that talks to a real server, because the rules a
browser enforces are invisible to an in-process client. This round pointed it
at the surface where that matters most: the HTML these products serve to
someone **without an account, on a device that is not theirs** — the sticker a
stranger kneels over, the sealed-carrier card, the page a sign-in provider
sends a browser back to.

Measured over HTTP, every one of those pages in all three products went out
with **no `Content-Security-Policy`, no `X-Content-Type-Options`, no
`X-Frame-Options` and no `Referrer-Policy`.**

That was the standing invitation. Then a sweep of every f-string that builds
markup found what had walked through it.

### Reflected cross-site scripting on the sign-in callback

`GET /auth/oauth/{provider}/callback?error=…` interpolated the query parameter
straight into its HTML. Driven over HTTP:

    ?error=<script>alert(document.domain)</script>
    →  400, and the payload comes back verbatim inside <p>…</p>

Anyone who could get a person to follow a link ran script on this product's
own origin — in a browser holding a session, or inside the packaged console's
window. Two more values on the same route went in unescaped: the provider's
error message and the address it returns.

Escaped at the interpolation, which is the fix. The policy below is the second
line, not the first.

### A policy with a nonce, because one without is decoration

`script-src 'unsafe-inline'` permits exactly what an injected `<script>` needs
and would have stopped nothing above. So `pagehead.py` mints a nonce per
response, the pages that carry an inline script stamp it through
`script_open()`, and the policy names that nonce and nothing else:

    default-src 'none'; img-src 'self' data:; style-src 'unsafe-inline';
    script-src 'nonce-…'; connect-src 'self'; form-action 'self';
    base-uri 'none'; frame-ancestors 'none'

`style-src` keeps `'unsafe-inline'`: the stylesheets are constants in the
package and no page interpolates into them.

Verified in real Chromium against a real server — the beacon page renders
with **no CSP violations**, styles applied, its own script running.

### What the guard checks

`test_what_the_browser_enforces.py` grew from four questions to a dozen: the
headers on every stranger-facing page, that the policy names a nonce rather
than permitting everything, that the page and its policy **agree** about that
nonce, that the reflected parameter comes back escaped, and that JSON is left
alone.

The nonce-agreement check is the one worth keeping. If the header and the tag
ever drift apart, the policy is still perfect and the page's own script
silently stops running — and that check's first draft failed against correct
code, because it read the header from one request and the body from another.
Two requests, two nonces. It reads both from one response now.

### Also

- Versions moved to 0.59.3 across the console, the backend, and the iOS,
  Android and Windows projects (build 59003).

## [0.59.2] — 2026-08-08

### A crash the browser threw away

0.59.1 found a CORS defect in a sibling product by comparing three
repositories rather than by testing behaviour — because **no test in this
estate could have found it.** Every one of them calls the app through a
`TestClient`, which never sends an `Origin`, never runs a preflight, and never
drops a response for want of a header. The whole class is invisible.

    asked     does the server answer
    mattered  does the answer reach the reader

Asking the question properly found a second one, in all three products at
once.

An unhandled exception is rendered by Starlette's `ServerErrorMiddleware`,
which sits **outside** every middleware the factory adds — including CORS. So
a 500 went back to a browser with no `access-control-allow-origin`, and the
browser discarded the entire response. Measured over HTTP:

    GET /health   200   access-control-allow-origin: *
    a 500         500   access-control-allow-origin: None

The consequence is worse than a missing header. These consoles distinguish
*the backend is unreachable* from *the backend refused* — the version-mismatch
guard and the content-free problem reporter both depend on it — and a 500 the
browser throws away is indistinguishable from the first. **Every crash in
every one of the three products reached its user as "Failed to fetch."**

### Why the obvious fix is not the fix

Registering `@app.exception_handler(Exception)` does not help: Starlette hands
that handler to `ServerErrorMiddleware`, which is still outside the CORS
layer. It has to be a middleware, and it has to sit *inside* CORS.

So each factory now ends with a catch-all middleware followed by the CORS
block, in that order — `add_middleware` inserts at the front, so the last one
registered is the outermost. The body it returns says nothing about what
broke: the traceback is logged on the machine and what leaves is a status and
a sentence, the same posture every other refusal here takes.

That ordering is now checked rather than assumed, and it needed to be: the
three products disagreed about it. Two added CORS before their request-scoped
middleware and one after, and nothing was comparing them.

### A test that starts a server

`test_what_the_browser_enforces.py` boots the app under uvicorn on an
ephemeral port and talks to it with a plain HTTP client, sending the header a
browser sends. It checks that a 500, a refusal and a preflight all come back
readable, and that CORS is still the outermost layer.

Its last test is the point of the exercise: it makes the same failing request
through a `TestClient` and shows it passing, with the header absent. Three
thousand tests can pass on an API no console can read.

### Also

- Versions moved to 0.59.2 across the console, the backend, and the iOS,
  Android and Windows projects (build 59002).
- `shared_guards.txt` regenerated at 383 names; the divergence record holds at
  136.

## [0.59.1] — 2026-08-08

### Three suites, and nothing comparing what they ask

0.59.0 closed on the observation that a literal copied into three
repositories is calibrated for whichever of them was smallest. That is a
special case of something larger: **every guard in this estate exists in three
copies, and the copies drift silently in both directions.** A fix made in one
product and not ported looks exactly like a product that never needed it.

Nothing anywhere was comparing them.

    asked     does this product pass its own suite
    mattered  do the three suites ask the same questions

A sweep of every `def test_*` across the three suites found **370 names
carried by all three and 140 carried by exactly two** — 91 absent from PDI, 29
from QRME, 16 from JIM-mini.

### Four of those rows were one defect

`test_serve_cors.py` existed in QRME and JIM-mini and not in PDI, and so did
the code it guards. Both siblings' `serve` opens CORS for a loopback bind,
because the packaged console calls the API from its own origin and dies as
"Failed to fetch" otherwise. PDI's frozen backend in
`packaging/backend_entry.py` does the same, so the **installed** app worked.
`python -m pdi serve` — the documented from-source path — set nothing.

Measured over HTTP with the console's origin on the request, because CORS is a
browser rule and an in-process test client never sends an `Origin` at all:

    OPTIONS /terms   →  405, no access-control headers at all
    GET     /terms   →  200, no access-control-allow-origin

and after the fix:

    OPTIONS /terms   →  200, access-control-allow-origin: *

Every in-process test in that product passed throughout. Loopback binds only —
a non-loopback bind is somebody serving a vault to a network, and that is the
last place to open CORS by default; `--no-cors` restores the closed posture,
and an explicit `PDI_CORS_ORIGINS` is never overwritten.

### The mechanism, and why it is a written record

The three repositories are rarely checked out together, so a live comparison
skips in CI — and this estate has already been bitten by that: the sibling
vocabulary check in `test_the_refusal_names_the_field_on_the_form.py` carries
a comment saying its first draft looked in the wrong place and skipped every
run. *A check that never runs is not a check.*

So the shared vocabulary is written down, byte-identical in all three
repositories:

- `tests/shared_guards.txt` — 377 names carried by all three.
- `tests/guard_divergences.txt` — 136 names carried by exactly two, each row
  naming the product that lacks it. Ratcheted: it may shrink, never grow.

Each product then verifies its own half with nothing but itself. Every name in
the manifest must exist here. Every divergence naming *another* product must
exist here. Every divergence naming *this* product must still be absent, so a
port that lands without being recorded fails rather than passing quietly.
Three checks, no sibling checkout required — and the live three-way comparison
runs on top whenever the siblings are on disk.

### A name is not a behaviour

This compares function names. A guard ported under a different name reads as
missing; one that kept its name while its body was gutted reads as present.
PDI reports its version from `/health` under a differently-named test, and the
record holds that as a row rather than pretending otherwise.

The limit is worth the check, because the failure it catches is the one that
actually happens: not a renamed guard, but a fix that never travelled.

### Also

- Versions moved to 0.59.1 across the console, the backend, and the iOS,
  Android and Windows projects (build 59001).

## [0.59.0] — 2026-08-08

### A floor nobody raised is a floor nobody is standing on

0.58.8 found the route reader had one floor and four clients. 0.58.9 found the
localizer's floor was ten against two hundred and seventy-nine. Twice in a
row, the same defect in a different instrument: a number written when the
surface was small, correct on the day, never raised.

Fixing them one file at a time does not generalise. This round swept every
floor in the suite instead.

### The two questions

A floor answers one question on every run — *is the number satisfied* — and
that is exactly the question that keeps passing after the number stops meaning
anything.

    asked     is the number satisfied
    mattered  is the number still near what it measures

The standard is the one 0.58.8 set for its own table and 0.58.9 kept: a floor
under **half** of what it measures is not holding anything. Applied here:

    l10n asked, per shell        10 against 279-312      ratio 0.04
    l10n held, per shell         20 against 286-312      ratio 0.07
    path literals, all surfaces  40 against 466          ratio 0.09
    native call sites            20 against 113-114      ratio 0.18
    console call sites          200 against 251          ratio 0.80  held

**69 floors in this product** carried their own literal, across 36 files.

### The finding underneath the finding

The rows that **passed** are as informative as the ones that did not. The same
literals appear in all three products, copied across when a guard was ported.
`assert len(made) > 200` is four-fifths of JIM-mini's console and 0.47 of
QRME's. `assert len(made) > 20` is a real floor against PDI's thirty-five
native call sites and a twentieth of QRME's four hundred and thirty.

**One number written to work in three repositories is calibrated for whichever
of them was smallest when it was written.** It reads as fine in the small
products forever, and ages into decoration in the large one, and nothing in
any of the three could tell the difference — because none of them had the
measurement attached.

`test_the_console_is_a_client_too.py` even carried the reason in its own
docstring: the floor was set low deliberately *because the three products'
shells differ by a factor of three in size*. That is a true sentence about why
the number is small and a false one about what it holds.

### The convention, because the sweep needed one first

A floor is spelled a dozen ways — `assert len(found) > 20`, `assert total >=
40`, a `FLOORS` tuple, a bare `_MIN_PATHS`. Nothing could walk them all,
because the number is not the hard part: the **measurement** is. A literal
inside an assertion has none attached, which is precisely why it can drift to
a fiftieth of the truth with every run passing.

`tests/ratchets.py` is a floor plus the way to read the same quantity now:

    Ratchet("route.calls.console", 340, _calls("console"),
            "call sites the route audit reads out of the console")

Registering one has three effects. The number lives in one place instead of
inside an assertion. `test_a_floor_is_within_sight_of_what_it_measures.py`
checks it against reality on every run, in both directions. And because the
assertion now reads `ratchets.floor("name")` — a call, not a constant — the
AST sweep stops seeing it, so registering removes a row from the backlog with
nobody editing a list.

### What is left is counted, not guessed at

The remaining bare floors are held in `unregistered_floors.txt` with a
ceiling, the way every backlog in this estate is. Not all of them are wrong;
some are small fixed cardinalities that will never drift. Telling those apart
from the decoration requires knowing what each one measures, which is the work
of registering it. A **new** bare floor now fails at the moment it is written
rather than three releases later.

### Also

- Versions moved to 0.59.0 across the console, the backend, and the iOS,
  Android and Windows projects (build 59000).

## [0.58.9] — 2026-08-08

### Ten against two hundred and seventy-nine

0.58.8 audited the route reader and found the three native shells had no floor
at all, closing by naming the next reader with the same shape available and
unused: the one that reads the L10n tables. It has the same hole.

`test_a_shell_asks_for_a_key_it_has.py` asserts each shell extracts **at least
ten** localizer calls and holds **at least twenty** table rows, as a canary
against the pattern silently ceasing to match. It was written when that was a
meaningful fraction. The tables now hold 286, 301 and 312 rows and the screens
make 279, 300 and 312 calls.

    ten against two hundred and seventy-nine

### Why the rest of the file does not cover for it

Two of the three readers in that file are protected in both directions. If the
table reader goes blind, every key a screen asks for stops being in the table
and the first check reports hundreds of missing rows. If the reachability
reader moves either way, the dead-row backlog reports undecided or stale rows.

The **call** reader going blind is silent, because reachability falls back to
a pattern that finds every dotted string literal in the sources whether or not
a localizer call sits in front of it.

Measured rather than argued. Narrowing the call pattern so it matches only
`L10n.t("…")` — no whitespace, lowercase method — is an ordinary-looking tidy
that blinds C# alone, because Windows spells it `L10n.T(`:

    ios      300 call sites
    android  312 call sites
    windows    4 call sites

The dead-row path barely notices, and what it notices it misnames: the only
rows it can still see going quiet are the six in that shell without a dot in
them. They surface as *translated rows nothing asks for* — a backlog
complaint. Nothing in that message says the reader stopped reading.

    asked     does every key a screen wants have a row
    mattered  can the reader still see the screens asking

### Two floors, because they fail differently

**Absolute, per shell, on both halves** — the extracted call sites and the
parsed table rows — set at roughly four-fifths of what each reader reaches
today. That catches the slow case: a form dropped here, a suffix there, over
several rounds, which no single diff makes obvious.

**A spread across the three shells**, which needs no number chosen by hand.
iOS, Android and Windows are one client written three times: the same screens,
ported by hand, so their tables are near-identical in size. Measured, the
quietest shell sits at 98% of the busiest in QRME, 89% in JIM-mini and 77% in
PDI. A shell at a twentieth of its ports is not a smaller shell.

The console is deliberately not a fourth port, and the reason is measured
rather than assumed: it shares 82 rows with QRME's shells, 62 with JIM-mini's
and **none at all** with PDI's. The desktop frame and the phone screens are
separate vocabularies, so neither a spread rule nor a superset rule between
them would mean anything.

### And the comparison the backlog files never made

`native_dead_keys.txt` carries a per-shell count — 73, 97 and 103 in QRME —
that has never been compared across shells. The ratchet asks whether the
number is going up; it does not ask whether one shell is carrying far more of
it than its ports. Most of those rows are not waste: the file's own header
says they are screens that exist on three shells and say less on one. That is
exactly a per-shell comparison, and it was sitting in the file unmade. It is
one-sided on purpose — a shell below its ports has paid its debt down.

This product's record is empty and its ceiling is zero, so the check skips
and says so. It is here for the same reason the floors are: the day a row is
recorded, the comparison exists already.

### Also

- Versions moved to 0.58.9 across the console, the backend, and the iOS,
  Android and Windows projects (build 58009).

## [0.58.8] — 2026-08-08

### The route reader had one floor and four clients

0.58.7 found a missing brace by auditing a reader rather than the thing it
read, and closed by naming the general case: **a blind instrument is
indistinguishable from a clean repository.** The route audit's reader is the
oldest and most load-bearing in the estate — six other files ask `clientpaths`
what each client calls, and a route table read short narrows all of them at
once, silently, in the safe direction. So this round went there.

### What the probe found

The console *is* protected. `test_the_audit_is_actually_looking_at_something`
asserts `calls(CONSOLE) > 200`, written when the console was the only client.
Blinding the console's template-literal reader drops it 351 → 74 call sites
and fails four tests including that one.

**The three native shells had no floor at all.** Their protection was
incidental — a scatter of per-block and per-form tests from earlier rounds
that happen to name routes those readers see. Blinding the iOS `request(`
form drops it **430 → 11** call sites; what fails is a handful of block
guards, not one of them saying *the iOS reader has stopped reading*. A
narrowing that misses the blocks those tests happen to cover passes in
silence, and `doorless` still reports zero throughout, because the other
three clients cover for the blind one.

```
asked     do the clients call every route
mattered  can the reader still see the clients
```

### Added

- `test_the_reader_can_still_see.py`, in all three products. Two floors,
  because they fail differently. **An absolute floor per client**, set at
  about four-fifths of what each reader reaches today, catches the slow case —
  a reader narrowed a form at a time until it covers a fraction of the
  surface. **A spread check across the three native shells** catches the fast
  case without a hand-chosen number: iOS, Android and Windows are one client
  ported three times, so one reader at a third of the other two is the reader
  breaking rather than the shell shrinking.
- The console sits outside the spread comparison, and the reason is measured
  rather than assumed: JIM-mini's console extracts 251 call sites against 114
  on each phone, PDI's 121 against 35. Those consoles carry surface the phones
  do not, so a rule spanning all four would have to be loosened until it
  caught nothing. The absolute floor is what holds the console.
- A floor on the route table itself. `app.routes` is not the route table — it
  showed 8 of 409 once, and the first doorless audit built on it reported a
  clean bill.

The floors are ratchets, not targets, and they are this product's own
numbers — measured here, not copied. Raising one when a client grows is
ordinary; lowering one takes a deliberate edit that shows up in a diff.


Suites: **1,588** passed, 1 skipped.

## [0.58.7] — 2026-08-08

### A wire model is data, and data has no methods

0.58.6 closed by naming its own hole: a pin whose reader goes blind reads a
model as **empty**, an empty set is a subset of anything, and the pin passes
against nothing while looking exactly like a pin that is holding. That is the
only way this table can lie, so this round went after it rather than after
more surface.

### Added

- Every pin now asserts on **both ends**: the model read something, and what
  it read shares at least one key with the contract. Deliberately not a size
  floor — `MicPlacesOut` and `ChainState` are honest one-property wrappers,
  and a floor that called those defects would be the file inventing work.
- Three checks read the readers themselves against a second opinion. Every
  struct whose conformance list mentions `Decodable` must be one the pattern
  can see; every C# record read by the finder must survive paren-matching;
  every property the language declares must be one the property pattern finds,
  located by where a declaration *starts* rather than where it ends.

Clean here on both counts — no pin reads an empty model, and no wire model
holds a method. The finding was next door: QRME's `SpecialistRow` was missing
its closing brace and the `extension ApiClient` that should have followed it,
so ninety-five client methods were declared on a two-field wire model instead
of on the client. Brace balance could not see it — the file balances, one
brace simply had the wrong opener — and neither could the member check, since
the methods are in the right file, just nested in the wrong thing.


Suites: **1,583** passed, 1 skipped.

## [0.58.6] — 2026-08-08

### The refusal surfaces, and a reader that read a struct as empty

0.58.5 closed by naming this batch — the screens that render what the platform
will **not** do, from data rather than prose, so the screen cannot drift from
the behaviour. An empty render of one of those does not read as a bug. It
reads as *no limits*, which is the worst failure mode a consent screen has.

Clean here, as the table has been for three rounds. The findings were all
next door, in QRME, and the last two were on **every** shell at once rather
than on one: the shells agree with each other and disagree with the server, so
cross-checking the clients against each other would have found neither. This
table is the only instrument in the repository that catches that.

### Added

- Three more pinned rows: the follow-up state, the open list and the record —
  *did the guidance work, and what was done when it did not*. An empty render
  of the open list reads as nothing pending.
- The reader learned three more lookups, all still inside the one pinned
  function or the module it lives in. `{**dict(r), …}` over
  `conn.execute("SELECT id, condition, … FROM …")` — the column list is a
  string literal right there, so the keys `dict(r)` carries are readable, which
  is exactly how the follow-up rows are built; `SELECT *` is not readable, and
  is refused. A `**spec` bound by a comprehension generator rather than a `for`
  statement. And `list(TABLE.values())` over a module table written as a dict
  comprehension.

### The trap it walked into first

Injecting a defect into PDI's `ComplianceProgram` did not fail the guard, and
that was the guard's fault rather than the injection's. PDI declares
`struct X: Decodable { let a: T; let b: T }` on one line, and the property
pattern required end-of-line — so it read that struct as **empty**, and an
empty model passes every comparison. The pin had been checking nothing since
the day it was written. Semicolon-separated properties are read now, computed
ones are still excluded, and the round that found it is the round that
injected rather than the round that wrote the pin.

Suites: **1,575** passed, 1 skipped.

## [0.58.5] — 2026-08-08

### The disclosure that showed nobody

0.58.4 shipped a pinned table — each row a shell model held against the backend
function whose `return` is its contract — and closed by naming where it should
grow: the surfaces where an empty render reads as *nothing to report* rather
than as a bug. The first one checked was worse than the guided tour.

Nothing here. The finding was next door, and it was the same class as the
guided tour but louder: QRME's live-microphone disclosure — *who in this room
has lent the profiles an open microphone* — reads `lent` on all three shells
against a route that sends `microphones_lent`. It rendered as nobody, on every
client, which is exactly what a disclosure looks like when it is broken.

### Added

- Six more pinned rows here, and the reader learned to follow three more
  shapes, all of them assignment inside the one pinned function: `out = {...}`
  with `out["k"] = …` after it, `rows = [{...} for r in …]`, and `rows = []`
  with `rows.append(row)`. 0.58.4 named the last of those as a limit and
  refused to guess past it. It is read now rather than guessed. That is also why the Kotlin half of the table
  is no longer empty: `emergency` descends into `robot_directives`, which
  is exactly a list built by appending, and the pin that 0.58.4 refused to
  write is written now.
- A `**spec` is resolved the same way — to a module-level dict of dicts whose
  values all carry the same keys, directly or through the
  `for _k, spec in SOMETHING.items()` that produced it — and refused outright
  when it is anything else. The refusal is the feature: a pin this file cannot
  read is one it must not invent.

Suites: **1,575** passed, 1 skipped.

## [0.58.4] — 2026-08-08

### The key was right and the shape was wrong

0.58.3 checked that every key a shell decodes is one the backend can send, and
left a named gap: the check is a *union*, so a key read off the **wrong**
response passes. The obvious next step was to bind each decode site to the
route it calls and compare per route.

### Four attempts at that, and why none of them shipped

The binding is not derivable by reading this backend, and every narrowing that
removed a false positive removed real coverage with it:

1. **Route to handler to return.** Handlers delegate, wrap (`{"beacons": [...]}`)
   and merge (`{**metrics}`). One level of following resolved 141 of some 400
   routes, and the mismatch list was 41 rows of which the ones checked by hand
   were the reader's fault.
2. **Flat-only on both sides.** Coverage fell to 52 sites and the mismatch
   rate stayed above four in ten.
3. **Bind on the container key** — `chapters: [{...}]`. The first run reported
   five defects that are not there: `llm.py` builds `{"messages": [...]}` as an
   outbound *request*, and the backend's inputs share a vocabulary with its
   outputs. Restricting to route-reachable returns fixed that and hid the real
   finding instead.
4. **Disjointness rather than subset**, to survive a key with two shapes. It
   survives them by not judging them.

The rule narrow enough to be sound covers two sites per product and finds
nothing. That is the honest ceiling of inference here, and it is worth writing
down rather than shipping a guard whose failures are mostly its own.

### Added

- `test_the_shape_inside_the_shape.py`, in all three products. It infers
  nothing: each row **pins** a shell model to the backend function whose
  `return` is that model's contract. A human read both ends once; the file
  holds them together from then on. It is small on purpose and meant to grow
  one verified row at a time.
- The Kotlin half of the table is empty here, and the reason is written
  down rather than worked around: `emergency` descends into
  `robot_directives`, whose elements are built by appending in a loop.
  A `return` this file cannot read is a pin it must not guess at.

Nothing here, which is what a pinned table looks like on the day it is
written: the rows are a contract somebody read at both ends, not a search. The
finding was next door — QRME's guided tour, blank on both phones and correct
on Windows, where the outline's chapters were read as `key` and `title` on a
shape that sends `chapter` and `steps`, and three more buttons decoded a
wrapper as the thing it wraps.

Suites: **1,575** passed, 1 skipped.

## [0.58.3] — 2026-08-08

### The key the server never sends

0.58.2 closed by naming where the seam goes next. The receivers whose type is
known for free are checked now; the tier past them is the receiver whose
members are *keyed* rather than named — `optString("worn")`,
`GetProperty("mode")`, a `Decodable` property whose name **is** the wire key.
A renamed backend field is the same silent break as a renamed method, except
it does not fail on a build machine. It fails on a phone, as an empty list or
a nil string, and the screen renders as though the server had nothing to say.

Matching a key to the route it came from needs a type checker this machine
does not have. Matching it to the backend's whole vocabulary does not, so the
guard asks only what it can answer honestly:

```
is this key one the server can emit anywhere at all
```

Clean here. The finding was next door, and it was four live breaks in QRME:
the overlay disclosure and the fine-tuning run reading keys the routes do not
send, the referral list reading a boolean where a timestamp is, and — on both
phones — `authorize_url` on a response that says `url`, which meant Sign in
with Google and Apple could not start at all.

### Added

- `test_the_key_the_server_never_sends.py`, in all three products: every key
  a shell decodes must be one the backend can put on a response — read from
  all four places a key reaches the wire (a dict literal, a key assigned after
  the dict is built, a model field, and `dict(row)`, which makes every column
  a key).
- A named `PROXIED` set for the eight keys that arrive verbatim from a
  sibling product — PDI's provenance trail and QRME's localities and
  rooms, both proxied through `return r.json()`. This backend's
  vocabulary cannot judge them, and reporting them would be the guard
  inventing defects out of the tandem's own architecture. Each was
  checked by hand against the emitting product first.

### The traps it walked into first

Three, all in the reader. A regex that ends a struct at the first `\n}`
swallows everything after a nested one, and `CustodyProvenance` has three.
`var stands: Bool { valid ?? verified ?? false }` is a computed property and
`let _: Ok = try await …` is a discarded binding; neither is a key.
`case profileId = "profile_id"` renames it, so reporting `profileId` reports
the shell's own spelling as the server's. And a fourth in the vocabulary
rather than the reader: reading only dict literals reported some sixty fields
that are on the wire every day.

Suites: **1,568** passed, 1 skipped.

## [0.58.2] — 2026-08-08

### The colour that wasn't in the palette

0.58.1 closed by naming where it should go next. `state.x` is not the only
receiver in these trees whose type is known for free — it is only the first.
Any receiver that exactly one file declares can be looked up the same way,
and there are eight of them per product:

```
iOS      state.x  ApiClient.shared.x  Theme.x
Android  vm.x     ApiClient.x         Jim.x
Windows  AppState.Current.X           ApiClient.Shared.X   {StaticResource X}
```

Widening it found one, next door. QRME's Android problem-report card painted
itself with `Qrme.Card2` on a theme that declares `Card` and has never
declared a second — and Compose has no fallback for an unresolved colour, so
the whole screen file fails to compile with it. This product paints the same
card with the name its theme actually has. Clean here; the check lands here
because the next one could be.

```
asked     is the thing a screen reaches for on its state object there
mattered  is the thing it reaches for on *anything* there
```

The API clients came back clean — **1,613 call sites across nine shells**,
every one naming a method the client actually has. That is worth asserting
anyway. 0.58.1's own defect had been sitting in `main` for rounds; the value
of a guard is not only what it finds on the day it is written.

### Added

- Every member reached on an API client, a theme object or `App.xaml` is now
  read against the one file that declares it, alongside the state objects
  0.58.1 covered — eight receivers per product, with a floor under each so a
  moved file cannot quietly empty the comparison.

### The trap it walked into first

Widening the check to the API clients immediately reported two methods that
are right there in the file — `Features` and `SetFeature` on the Windows
client, whose return type is
`Task<System.Collections.Generic.Dictionary<string, bool>>`. The C#
declaration pattern had no dot in it. Narrow and true is the standing rule
here, and this is the other edge of it: a pattern narrower than the language
reports defects that do not exist. Both the dot and a test for it are in now.

Suites: **1,559** passed, 1 skipped.

## [0.58.1] — 2026-08-08

### The member that isn't there

0.58.0 ended by restating the standing gap: no Swift, Kotlin or C# toolchain
on this machine, so the native UI is asserted by reading and not by running —
and that round widened the amount of screen riding on it. The honest response
is not to pretend a compiler exists. It is to keep taking the classes of
compile error that *can* be caught by reading. 0.57.5 took duplicate
declarations and unbalanced braces; 0.57.6 took the markup; this takes the
next one.

Each shell has exactly one object the screens read their session from, and
exactly one file that declares it — so `state.x` is not a guess about types.
It is the one receiver in these trees whose declaration is known without
resolving anything.

```
asked     do the screens parse, and do they say the right things
mattered  is the thing they reach for actually there
```

### Fixed

**Thirty-eight call sites across five iPhone screens, none of which compile.**

- `AppState` holds `uid` and `token`. `ContinuityCard`, `PresenceView`,
  `SafetyView` and `SelfProfileView` asked it for `userId` and `userToken` —
  continuity, presence, safety and the synthetic self, which is the whole
  crisis half of this product.
- `state.api` in `SelfProfileView` and `OfflinePostureCard`, on an `AppState`
  that has no client at all. Every other screen in the tree reaches
  `ApiClient.shared`, which is what these now do.

Swift says *value of type 'AppState' has no member 'userId'*. All of it had
been sitting in `main`.

### Added

- `test_the_member_that_isnt_there.py`. Two injections, both the real thing:
  `state.userId` restored on the safety screen, and `state.api` on the
  offline card.

Suite: **1,552 passed**, 1 skipped.

## [0.58.0] — 2026-08-08

### The key the phones never carried

0.57.9 ended by naming the shape: a guard that verifies *a* line rather than
*every* path has a blind spot, and the same audit run on a different header
would probably be productive. It was — but not the way it was expected to be.
Asked of every header the console attaches to every request, the answer was
not *some paths miss it*. It was **one header the shells do not send at all.**

```
x-llm-api-key
```

The person's own model key. Pasted into the console since 0.4.3, read by the
backend per request into a context var and never written down, and sent by no
native shell. A key set on the desktop was used on the desktop, and the
deployment's key was used on the phone — same account, same profile, two
different credentials, and nothing anywhere saying so. The phones even drew
the provider list with *ready* / *no key* beside each row, which is the
**deployment's** key state: the screen showed a fact about somebody else's
credential and offered no way to supply your own.

```
asked     does every request carry the headers this client sends
mattered  does this client send the headers the product has
```

### Added

- The key on all three shells: held on the device (UserDefaults,
  SharedPreferences, the app's local state) and never in the account, pushed
  into the API client once and sent from the same place the language header
  goes.
- A field to set it, under the four rows the console has had since 0.4.3 —
  the same keys and the same words, so no new console/native split appears.
  Saving an empty box is the clear; there is no flag to leave switched on.
- `test_every_header_the_console_sends_the_shells_send_too`, which reads the
  console's own shared helper rather than a list written in the test, so a
  header added there cannot quietly stay there.

### Changed

- The shells gained a Save button and use the console's own `set.save` row for
  it rather than minting a second word for the same button.

Suite: **1,546 passed**, 1 skipped.

## [0.57.9] — 2026-08-08

### A funnel only funnels what goes into it

0.57.8 ended by naming its own next question: guards get written in one repo
and not ported, so compare the three `tests/` directories. Twenty-four files
exist in exactly two of the three, and most of those are genuine product
differences. One was not.

`test_the_language_nobody_was_sending.py` exists in JIM-mini and PDI and not
in QRME — the product whose premise is a profile that speaks in a person's
language, and which built an accountless *stranger* surface over three
rounds. Every refusal it raises goes through `refusal_language`, which reads
`Accept-Language` whenever the caller is not an owner.

**A first pass said QRME's shells never sent the header. That was a
case-sensitive grep and it was wrong** — all three send it, lower-case, from
their shared request helper. What the guard could not ask, in any of the three
products, is the question that mattered:

```
asked     does this client set the header with the resolver
mattered  does every request this client makes carry it
```

Because the answer was **no**, everywhere:

```
QRME      Windows 21 of 22 sends, iOS 3 of 4, Android 1 of 2
JIM-mini  Windows 15 of 16, iOS 1 of 2,  Android 4 of 5
PDI       Windows  3 of 4
```

Uploads, streams and raw-response reads, each building its own request beside
the shared helper and setting only `authorization`. Those calls carry a token,
so a *valid* token still picks the owner's stored language — but an expired
one is not a principal, and the refusal falls back to a header that was not
there. Forty-four requests across three products.

### Fixed

- One dispatcher per shell rather than one line per call site, because a line
  per call site is precisely the thing that went missing forty-four times.
  C# gained `Dispatch(HttpRequestMessage)`, Swift a `dispatch(_:)`, and the
  Kotlin clients' remaining connections got the header where they are built.

### Added

- `test_every_place_a_request_leaves_the_shell_carries_the_header`, which
  walks every dispatch site rather than every line that mentions the header —
  the half the original could not see, in the product that had it and the two
  that did not.
- The guard itself, in QRME, four releases after it was written next door.

Suite: **1,544 passed**, 1 skipped.

## [0.57.8] — 2026-08-08

### The rows the guard skipped were the interesting ones

`test_a_shell_does_not_print_what_it_translated.py` has, since 0.54.0, opened
its row reader with

```python
if "{" in english:
    continue
```

Every row with a slot in it went unchecked, for four releases. That is not a
corner of the table: a row with a slot is a row *about something*, which is
most of what a screen actually says — and a sentence assembled around a value
is the one a screen is most likely to hand-build, because building it is what
the code is already doing.

```
? $"closest overlap {best}, below the {th} threshold for naming anyone"
```

against `ns.who.below` — *"closest overlap {best}, below the {threshold}
threshold for naming anyone"* — the same sentence, hole for hole, in that same
shell's table in ten languages.

```
asked     does a screen print a whole English row verbatim
mattered  does a screen print an English row the reader will never see
          translated, however it is spelled
```

Found from the other side and by accident: 0.57.7 was fixing a Windows page
that would not parse, read the code-behind while deciding a rename, and saw
seven of these on one screen. This closes the general case rather than the
seven.

**A slotted row is compared by its fragments**, not by rebuilding the
sentence — the shell's holes are not the table's, and `{en.Seconds:F1}s` is
not `{secs}`. The row is split at its slots and the literal text between them
is matched. Fragments shorter than a phrase are dropped, so `Built {date}`
contributes nothing; that is a deliberate miss and the file says so.

### Two false findings, caught before they shipped

The check's own first run against the sibling products reported two defects
that were the reader's, not the code's, and both are now tested against:

* `L10n.t("cw.sensitivity", …)` is a screen *asking* for a row, and the
  fragment *"sensitivity"* is inside that key. A key is not something a reader
  sees.
* `$"{(int)Math.Round(p.Confidence * 100)}"` matched the row *"Confidence
  {pct}% — earned from…"* on the word `Confidence`, which is a C# property
  there and a heading here. The holes come out of the shown string too — the
  same removal that is done to the row.

Same lesson as the eighty-six protocol values that shaped the original: strip
what is not prose before comparing prose.

### Fixed

The guard did not exist here — it was written in QRME at 0.54.0 and never
ported, so this product has had the same class of defect unmeasured for four
releases. The first run found thirty sites and the split was the same one
QRME's first run produced: **nine were labels and are now keys**, and the rest
are values.

* `Check-in` as a screen heading on all three shells, `Language` on all three,
  *Your name* and *What's on your mind?* on the desktop — every one of them a
  row held and translated ten ways.
* Three Windows pages had no `Localize()` at all and now have one for the
  strings the table already carries. The rest of those pages is
  `native_screens_untranslated.txt`'s business, not this file's.

The fifteen recorded rows are the sensitivity ladder (`cautious`, `balanced`,
`assertive`) and the severity ladder's `critical` — values the crash-watch
policy API stores and compares against, already rendered through
`sensitivityLabel` which does read the table — and four SwiftUI enum raw
values that are the stored identity of a selected tab.

Suite: **1,542 passed**, 1 skipped.

## [0.57.7] — 2026-08-08

### The files the release never touched

0.57.6 ended by naming its own next question: whatever a guard checks, ask
first which files it does not open. Asked of the release itself, the answer is
three files per product.

A cut bumps `pyproject.toml`, `<pkg>/api.py`, `app/package.json`, the lock
file, the README banner, the README release row and the changelog. That number
reaches everything a *server* or a *console* reports. The three native shells
report their own version from three build files no step in that list touches:

```
native/ios/project.yml               MARKETING_VERSION: "0.1.0"
native/android/…/build.gradle.kts    versionName = "0.1.0"
native/windows/*.csproj              (no <Version> at all)
```

```
asked     does the product carry the version it cut
mattered  does the thing a person installs carry it
```

Nine declarations across three products, every one of them `0.1.0` or absent,
through every release since the shells were written.

This is not cosmetic in the way a stale README is. `versionName` is the string
on the Play listing and in Settings › Apps; `MARKETING_VERSION` is the App
Store version and the one a crash report is filed against; the `.csproj`
version is what Windows shows in a file's Properties. An install reporting
`0.1.0` cannot be told apart from any other install — and these products ship
a problem collector, which is the part that makes the omission bite.
`versionCode` was worse: Android refuses an upload whose code does not
increase, so a store submission was going to fail on the first try regardless.

### Added

- `test_the_files_the_release_never_touched.py`. The three build files are
  read against `pyproject.toml`; `versionCode` and `CURRENT_PROJECT_VERSION`
  are **derived** from the version rather than kept by hand, because a counter
  beside a version string is two things to forget instead of one.
- The same files carry what a shell is allowed to do — the plist usage
  strings, the `uses-permission` rows — and those are checked against the
  platform APIs each shell actually calls. iOS *terminates* an app that opens
  a camera with no `NSCameraUsageDescription`; Android throws.

### Fixed

- All nine declarations now carry the release. The `.csproj` files gained
  `<Version>`, `<AssemblyVersion>` and `<FileVersion>`, which they had never
  had.

### A trap walked into while writing this

The first pass at the capability check read `LAContext` in QRME's
`Signing.swift` and `BiometricPrompt` in `Signing.kt` and was ready to report
two missing declarations. Both are in **comments** — prose explaining why the
shells use WebAuthn instead, since a local biometric check is the app's own
word about itself and an assertion is not. A guard that counts a mention as a
use invents a defect, which is worse than missing one. Comments are stripped
before anything is counted, and a test holds that line.

Nothing in this product's shells calls a gated platform API, so the capability half finds nothing here — the check earns its place by what it will catch.

## [0.57.6] — 2026-08-07

### The half of the Windows shell that is not code

0.57.5's parse check globbed `*.swift`, `*.kt` and `*.cs` and reported the
three shells parseable. The Windows shell's screens are XAML, and it never
opened one.

```
asked     do the files that look like code still parse
mattered  do the shells' screens still parse
```

### Added

- Four markup checks in `test_the_shells_still_parse.py`: the page is
  well-formed XML; no two elements in it share a name; every handler it names
  exists in its code-behind; every control the code-behind drives is named in
  the page. Reach floors on all four — 15 pages, 400 names, 92 handlers, 348
  driven controls — and four injected defects confirming each can fail.

### Fixed

- Three pages carried `x:Name` twice on a single element, which is a duplicate
  attribute and stops any XML reader at the tag: the custody screen's
  empty-state note (`EmptyText` / `EmptyNote`), the overview screen's sealed
  badge (`AdaptationVaulted` / `SealedText`), and the safety screen's alarm
  question button (`AskAlarmButton` / `AlarmAskButton`). In each case the
  code-behind drove both names, so the fix had to decide which control was
  meant rather than drop an attribute.

## [0.57.5] — 2026-08-07

### Nothing here builds the phones, so nothing here noticed when they stopped

0.57.4 shipped a fix and a defect in the same release. Renaming iOS's `venue`
to `locality` collided with a `locality` already declared in the same
`TradeSection` — two stored properties of one name in one type, which does not
compile. It reached `main` and sat there for a release.

The reason is worth writing down rather than apologising for: **every guard in
these repos reads the shell sources as text.** The request-body guard extracts
call shapes; the response guards extract declarations; none of them parse, so
none of them can see a syntax error. `tsc --noEmit` covers the console. There
is no Swift, Kotlin or C# toolchain on the machine these run on, so there is
nothing to compile with.

    asked     do the shells say the right things to the server
    mattered  do the shells still compile

### What this checks, and what it does not

`test_the_shells_still_parse.py` does not typecheck. It checks the one class
of breakage that is invisible to a text-reading guard, cheap to detect without
a compiler, and *certain* to stop a build:

* a name declared twice in one scope — a Swift type's stored properties, a
  Compose function's `remember`ed state, a C# type's fields;
* braces that do not balance, counting through strings and comments.

A green run here does not mean the shells build. It means they do not contain
the specific mistake that got past everything else. That is a narrow claim,
and it is stated narrowly in the file: the whole arc since 0.56.4 has been
guards that measured slightly the wrong thing and passed, and a check that
promised "these compile" would be the next one.

The scope reader counts braces rather than matching a regex, because a pattern
that stops at the first `}` reads half a type — and half a type has no
duplicates in the half it did not read. Nested declarations are excluded: a
`var` inside a closure is not a member, and an inner type's property belongs
to the inner type.

Three defects were injected and confirmed to fail it, the first being 0.57.4's
own, put back verbatim.

## [0.57.4] — 2026-08-07

### Nothing to collect here, and the version moves with the others

0.57.3 gave the three native shells a guard on what they *send*, and found
this product's shells correct: 55 writes each, 47 matched to a model, nothing
wrong. QRME's found seven defects and recorded six of them as needing an
input its screens did not collect; 0.57.4 collects those inputs and empties
that record.

There was nothing here to collect. The guard, its per-client reach floors and
its record file at a ceiling of zero are unchanged and still green, and the
three repos are cut at one version, so this is the version.

## [0.57.3] — 2026-08-07

### The request-body guard reaches the three shells, and finds them right

0.57.2 asked what the console sends against the schema FastAPI validates with,
and found two fields on the monitor route being discarded on arrival. The
defect that motivated that release was visible only because the four clients
were read by hand; the guard read one of them.

This release reads the other three. Each needs its own extractor — C#
anonymous objects, Swift dictionary literals, Kotlin `.put` chains share
nothing but the question — and the comparison is imported unchanged.

**55 writes per shell, 51 / 37 / 37 of them with a readable body, 47 matched
to a model, and nothing wrong.** QRME found seven distinct defects in the same
sweep, including a marketplace call that had never worked from any native
surface; this product's shells send what their routes ask for.

A clean result rather than an absence: three defects were injected and
confirmed to fail the guard before it shipped, and the reach floors are set
per client — because the failure they catch is per client, and a pattern that
stops matching one file leaves the other two green and says nothing.

## [0.57.2] — 2026-08-07

### Four clients agreed with each other and all four were wrong about the server

Every guard since 0.56.4 has asked whether a client understands what a route
sends back. None asked what the client sends *in*. This one does, against
`app.openapi()` — the schema FastAPI actually validates with — and it found
two on the monitor route, both of which had been discarding readings.

**`stress_level` was on no model at all.** The console collects it, and so do
the Kotlin, C# and Swift shells: every one of the four posts a stress reading
beside the heart rate on the monitor screen. `BiometricSample` never declared
the field, and Pydantic drops an undeclared field without complaint — so the
number was discarded on arrival, on every surface, with no error, no log and
nothing on the screen to say it had not landed. A health guardian was
collecting a vital sign and throwing it away.

0.57.1 found three clients right and one wrong. This is the same lesson read
from the other direction: agreement between clients says nothing about whether
any of them is talking to the server.

**The console called breathing `respiration`.** The model says
`respiratory_rate`. Dropped the same way, on the surface a desktop owner uses.

`stress_level` is now a declared field on `BiometricSample`, a float on the
0.0–1.0 scale — which is the scale all four clients were already sending on,
and worth stating because the first attempt declared it an integer 0–100.
Nothing contradicted that until a suite-gateway test posted `0.8` and got a
422: while the field was being discarded, its type could not be wrong.
The console sends `respiratory_rate`. A test in
`test_signal_quality.py` posts all three fields and asserts the sample keeps
them, so a reading cannot go quiet again.

### What the guard reads

113 writes, 70 with a body it can read, 92 matched to a model. Three checks: a
required field never sent, a field the model has no property for, and a
bodiless write to a route that requires one. Ratcheted at a ceiling of zero.

The reach is worth stating because it is how these two were found at all. The
first port read 28 of the 113 — this client writes `(uid, body: { ... },
token)` where QRME writes `(body: { ... })`, and the pattern was anchored on
the opening paren. It was green at 28. Checking the share it reached, rather
than the colour of the run, is what turned it up.

## [0.57.1] — 2026-08-07

### The console reads the wire too, and twice it read it wrong

QRME's guard family has asked three clients the same question since 0.56.4 —
does this client's declared shape match what the route sends. The console was
never asked. It declares more than the native shells do, and TypeScript erases
all of it at build time, so a wrong declaration is not a crash: it is a screen
that renders something else.

Both findings here rendered.

**The capture screen listed the agent's fields as one word.**
`/capture/vocabulary` sends `agent_sees` as the list of field names. The
console declared it `string` and put `{vocab.agent_sees}` straight into the
markup, and React concatenates an array of strings with no separator — so a
privacy disclosure about what the agent can see arrived as its field names run
together. Worse than blank, because it looks like text.

**The settings line counted payloads instead of items.**
`/users/{id}/cloud-contribution` sends `contributed` as the contribution log.
The console declared it `number` and wrote `${state.contributed} item${...===
1 ? "" : "s"}`, which stringifies the whole array and can never take the
singular. Someone who had contributed one item was told so in a sentence made
of their own payload.

Both are fixed — `agent_sees: string[]` joined for display, and
`contributed: ContributedItem[]` counted by `.length` — rather than recorded.
`jim/tests/console_shapes_unverified.txt` sits at a ceiling of zero.

### What the guard reads

100 declared shapes, 623 fields, 110 GET bindings, 49 of them driven against a
live fixture. Every required field is checked twice: that the route sends that
name, and that the declared type can hold what arrives. Optional fields are
believed — this client writes `?` where a field genuinely comes and goes — so
the result is a list of defects rather than a list of states.

## [0.57.0] — 2026-08-07

### The guard arrives, and the reason it was not here was mine

0.56.9 said this client called the backend in a shape QRME's extractor could
not see, and that lowering the threshold until it passed would ship a guard
that asserts on nothing. The first half was true and the second half was the
right instinct. What was wrong was the conclusion drawn from it: the shape
difference is one optional `JSONObject(` wrapper, because QRME's `request`
returns a `String` and this client's returns a `JSONObject` already.

With the wrapper required, the guard found twelve of this client's forty-two
GETs and passed. Twelve found reads exactly like twelve is all there are.

### What it found

Forty-four routes and 161 keys now, thirty-two of them driven against a live
fixture. Every key this client reads off a response is checked twice — that
the route sends that name, and that `org.json`'s accessor can give back what
arrives — and this client is correct on all of them but six.

Those six are states, not fictions: `note` on the adaptation profile, which is
only there while `built` is false, and five `ContinuityState` keys that need a
history of check-ins and coach turns accumulated over time. They are the same
six the Swift guard recorded in 0.56.8, found again from the other side. Two
extractors reading two languages and arriving at the same six is the evidence
that neither invented them.

`jim/tests/android_keys_unverified.txt` records them at a ceiling of six, with
the state named beside each. The file also gained a check that every row still
names a read this client makes, so a row cannot outlive the line it describes
and go on holding the ceiling up.

### One finding that was the guard's, not this client's

The circle thread builds its URL by concatenation:

    request("/circle/$uid/messages?with_id=" + encode(withId), token = token)

The extractor sees `/circle/$uid/messages?with_id=` and nothing more, because
the value is on the next line. Driving that asks for the thread list, which
the route answers with `threads` and no `messages` — and the client was
reported for reading a key the route sends perfectly well. A half-built query
string is now unreachable rather than recorded, which matters: recording it
would have written the guard's own defect into the ratchet file.

## [0.56.9] — 2026-08-07

### The Android client gets a guard it was thought not to need — over there

QRME's 0.56.8 left Kotlin out because it parses `JSONObject` by hand and
declares no shapes, so there was nothing to compare. That was wrong. Every
line of that client is two claims at once — `o.optJSONObject("kinds_worn")`
says the route sends that key *and* that it is an object — and `org.json`
never throws when either is wrong. `optString` on a missing key returns `""`,
`optJSONArray` on an object returns `null` into the `?:` beside it, and a
screen draws empty instead of crashing.

It found eight wrong reads there, every one already fixed in that product's C#
client and most in Swift too.

**The guard is not in this repo yet, and the reason is worth stating.** Ported
across, its extractor found *zero* routes here — this client calls the backend
in a shape QRME's pattern does not match, exactly as PDI's C# client did when
the first shape guard travelled in 0.56.5. Lowering the threshold until it
passed would have shipped a guard that asserts on nothing, which is the defect
this whole sequence exists to find. So it is named here as next round's work
instead.

**No code changes in this repo this round.**

## [0.56.8] — 2026-08-07

### The Swift client gets the same guard, and answers the same way

QRME found nine fictions in its own iOS client — every one a defect already
fixed on its Windows side in 0.56.4 or 0.56.7 and never carried across.
Fixing a defect in one client was not fixing the defect, and nothing was
checking the other one.

`test_the_shape_the_swift_client_expects.py` is here now too. It drives every
GET binding in `native/ios/Sources/ApiClient.swift` and asks both halves of
the same question: is each declared field a key the route returns, and can its
declared type decode the shape that arrives.

**This client came back with no fictions** — the third time in four releases
these clients have answered a new check cleanly.


JIM-mini's own answer records twenty-two conditional fields — continuity
vectors, help tallies, presence areas — that appear only once an account has a
history. Unlike the crash watch and the adaptation profile, which the fixture
builds in two calls, continuity is derived from accumulated check-ins over
time and has no route that builds one. A fixture that faked that history would
be asserting against its own fiction, so the rows name the state instead.

## [0.56.7] — 2026-08-07

### The shape guard learned to read types, and this client is still clean

Cut together at one version. The only change here is to the guard.

QRME split the last two names on its wire-name collision record — `kinds` and
`refused`, each carrying three meanings — and in doing so found that its
wearables board sends `kinds` as a **map** while the Windows record declared
`string[]`. `System.Text.Json` does not coerce an object into an array; it
throws. That call had been failing outright, not losing a field.

The shape guard added in 0.56.5 compares declared **names** against the keys a
route returns, and `kinds` was returned under exactly that name as exactly the
wrong kind of thing. It saw nothing.

So there is a second assertion now, here as well as there: drive the route,
and check that each declared type *can decode the shape that arrived* — list,
object, string, number, bool, the distinctions a decoder actually throws on.
Over there it found five more, every one a live crash rather than a blank
field. **Here it found none**, which is the same answer this client gave to
the name check.

## [0.56.6] — 2026-08-07

### Reported from a phone: eight watch faces that were not on the page

> *"On the readme in JIM-mini 5, 10, 15, 20, 25, 30, 35, 36 are not visible on
> a mobile device."*

That is exactly the set of cells in the last column, and the reason was two
layers deep.

An HTML table is as wide as its **longest row**. JIM's watch gallery had six
rows of five and one row of six, so the table was six columns wide — every
five-cell row rendered a sixth empty column, and a phone clipped the whole
thing past the fourth. QRME's main gallery was worse: one `<tr>` carrying
**fifteen** cells beside rows of three, which made that table fifteen columns
wide and left twelve blank columns on almost every row. That is the *gaps and
spaces* in the same report.

    asked     is every screen in the gallery
    mattered  is every screen in the gallery *on the page*

`test_docs_gallery.py` had been checking that every drawing is referenced and
every reference resolves, and it passed the whole time — correctly. A cell can
be present in the markup and pushed off the visible page by the row it sits
in, and only the shape of the table can tell you that. Its own docstring even
records an earlier version of this ("inserting one screen into a three-wide
row pushed the last cell out"), which is a defect the file knew about and had
no assertion for.

#### Four across

Every gallery is now a uniform grid: screens and watch faces four per row at
`width="25%"`, desktop frames two at 50%. Four is the number because four is
what fits the phone the report came from; a fifth column is the column that
went missing.

Eighteen tables were reflowed across the three repos. Five cells that held no
picture at all — literal blank squares — were dropped on the way through.

| | rows before | rows after |
|---|---|---|
| QRME screens (the big one) | `3,3,4,3,…,15,3,3,3` | 26 rows of 4 |
| QRME desktop | `2,2,2,2,3,2,1` | 7 rows of 2 |
| JIM screens | `4,4,…,3,…,5,1` | 27 rows of 4 |
| JIM watch | `5,5,5,5,5,5,6` | 9 rows of 4 |
| PDI screens | `3,2,3,3,3,3,2,…` | 8 rows of 4 |

#### The guard

`test_the_gallery_is_a_grid.py`, in all three repos. It finds every table
whose picture cells all point at one folder under `docs/`, and asserts three
things: no row wider than four, every row the same length as the one above it
(the last may be short), and no cell without a picture in it.

It reads the **widest** row rather than the first, because JIM's gallery
opened with five rows of five and put the sixth cell in the last row —
anything reading row one would have called it fine.

## [0.56.5] — 2026-08-07

### The guard that found fourteen fictions next door, pointed here

0.56.4 built a guard in QRME that reads the Windows client's GET bindings,
drives each one against a live app, and asserts every `JsonPropertyName` in
the bound record is a key the route actually returned. It found fourteen
records over there declaring fields their routes have never sent — a
composition card promising a `name` and a `share` on a route that has only
ever sent `display_name` and `weight`, a button drawing separators with
nothing between them because nobody had run it.

That changelog said the guard belonged here too and was not here yet. It is
now, adapted to this product's fixtures.

**This client came out clean.** Every field it declares is a field its route
sends. That is worth saying plainly rather than reporting as a null result:
the two clients were written in the same weeks by the same hand, and only one
of them was written from the wire.

#### Driving into the state beats recording that you did not

Two records here return a short *nothing here yet* body until the feature is
on, and their full shape afterwards — the crash watch until it is armed, the
adaptation profile until one is built. A fixture that only enrolled would have
put twelve real fields in the unverified record. Arming the watch and building
the profile is two calls, so the guard makes them, and the record closes at
two rows:

* `AdaptationProfile.note`, the sentence explaining there is no profile yet —
  only visible while `built` is false, which a fixture that builds one can
  never see;
* `PresenceBeat.deepened_line`, only present when a real model answers. Under
  the stub provider `deepen` returns the offline line and says so, which is
  the whole point of that branch.

Both name the state that produces them. A guard that cannot tell a conditional
field from a fiction is a guard nobody can trust.

#### Two things the port fixed in all three copies

The record parser counted a wrapped reason — an indented `#` continuing the
line above — as an empty row, so a record with any wrapped comment failed its
own ratchet. Filtering on the parsed result rather than the raw line fixes it.

And a deliberately malformed injection, made while checking the guard fires,
showed the record-block regex will run one record's body into the next when a
paren is unbalanced — reporting fields against the wrong record name, which
reads as a real finding and is not one. There is now an assertion that no
extracted body contains another record.

## [0.56.4] — 2026-08-07

### Cut together at one version

The three products are cut at one version, so this release exists here to keep
that true. **No code changes in this repo this round.**

QRME chased its last unexplained wire-name collision, `share`, into a Windows
client record for `GET /profiles/{id}/composition` that declared two fields —
`name` and `share` — the route has never sent. It sends `display_name` and
`weight`. Both decoded to null on every response, and the button wired to them
drew a row of separators with nothing between them; it had never been run.

Fourteen records were the same: a guess at a shape, written without driving
the route. The fix is a guard that reads the client's GET bindings, drives
each against a live app, and asserts every declared field is a key the route
actually returned — one-directional, because a client may decode less than it
is sent but must never claim more.

**That guard belongs in this repo too, and it is not here yet.** It needs this
product's own fixtures to reach its own routes, which is the next round's
work, named here rather than left for somebody to notice.

## [0.56.3] — 2026-08-07

### Cut together at one version

The three products are cut at one version, so this release exists here to keep
that true. **No code changes in this repo this round.**

QRME started paying down the wire-name collision backlog 0.56.2 recorded, and
four of its twenty-eight rows turned out to be one finding repeated: a boolean
state and a count of that state sharing a name. `seen` was both *has this item
been seen* and *how many were just marked seen*; `available` was both *is this
desk free* and *how many packs this registry has*; `revoked` was both a flag and
a tally. A decoder handed `1` where it expects a boolean coerces rather than
refusing, so the wrong route returns a plausible answer from the wrong evidence.

The counts are now `marked_seen`, `available_packs` and `revoked_count`. A
fourth row, `reattested`, was not a collision at all but a client bug: the wire
value is always a boolean and the Windows record declared an integer. QRME's
record falls 28 → 24.

## [0.56.2] — 2026-08-07

### One name, three meanings — and the compiler nobody ran

`spoken` meant three different things in this product at the same time:

* `guardian.guide_first_aid` → the CPR playbook steps read aloud, a **string
  list**;
* `presence.deepen` → the model's rewritten line, a **string**;
* `presence.say` → whether the beat was said out loud, a **boolean**.

The Windows client had already forked it into three records, each with its own
`JsonPropertyName("spoken")`. Nothing about that looked wrong to anybody
reading one record at a time. TypeScript could not fork it, because
`PresenceSpoken extends PresenceBeat` there, so the collision surfaced as a
compiler error:

```
Interface 'PresenceSpoken' incorrectly extends interface 'PresenceBeat'.
  Types of property 'spoken' are incompatible.
    Type 'boolean' is not assignable to type 'string'.
```

**And it sat on `main`, through several releases, because no suite in any of
these three repositories ran `tsc`.** The one tool able to see the problem was
the one tool nobody had wired up.

Each meaning now has its own name: `spoken_steps`, `deepened_line`, and
`spoken` for the boolean it pairs with `shown`. The console, all three native
clients and two tests were updated together.

### The two guards

`test_the_console_typechecks` runs `tsc --noEmit`. Six seconds, and this
particular defect cannot reach `main` again without somebody deleting the test.

`test_no_wire_name_carries_two_types` is the general shape: it reads every
`JsonPropertyName` in the Windows client — the one file where the whole wire
surface is declared with its types — and records names carrying more than one.
Nine were found here, `spoken` among them; eight remain, ratcheted, each to be
fixed by giving its meanings separate names.

## [0.56.1] — 2026-08-07

### A model that is actually trained

`adaptation.py` builds a per-user profile and is scrupulous about what it is
not:

> **This is not a weight file.** The transformer stays the vendor's. What JIM
> owns is the state that conditions it, and the profile says so in its own
> `method` field rather than letting a reader assume a fine-tune happened.

That was true, and it was the right position to hold until it was overruled.
`jim/finetune.py` is the other thing: an offline pass that reads this user's
own answered follow-ups and **trains weights** by gradient descent, on this
machine, with the network blocked for the duration.

### What is trained, and why it is small

The supervised signal this product actually has is narrow and real:
`guidance_followups` records, per condition and severity, whether the guidance
JIM gave **helped**. That is a labelled dataset of the one question the Guardian
needs a learned answer to — *for this person, which register of advice lands* —
and it is the dataset a general model cannot have, because it is about one
person.

So the default backend trains a logistic model over interpretable features. It
is a weight file, and it is a *small* one, which is a property of the evidence
rather than a shortcut: a hundred follow-ups do not support a hundred million
parameters, and a model larger than its evidence is a confident guess in a
bigger coat.

### The four things that are enforced rather than promised

* **Nothing leaves.** The pass runs with `urlopen` replaced, so a backend that
  reached for a model hub raises instead of uploading somebody's health
  history. A test injects exactly that backend and watches it fail.
* **It has to have learned.** The central test does not check that training
  *ran* — weights of all zeros serialise perfectly well. It trains on a corpus
  with a planted signal and asserts the weights recovered it, with the loss
  more than halved.
* **Below twelve examples it refuses.** Not a low-confidence model; a refusal.
  Attaching `confidence: 0.2` to a coincidence does not stop it being one.
* **Training and using are two decisions.** A trained model is inert until a
  switch with no default turns it on, and turning it off restores exactly the
  behaviour that predates the module.

The `lora` backend is wired to `transformers`, `peft` and `torch` and **raises**
when they are absent — and raises again, deliberately, when they are present but
no pass has been watched to completion on this deployment. A training path that
reports success without anybody having seen it work is worse than one that
refuses.

## [0.56.0] — 2026-08-07

### Cut together at one version

The three products are cut at one version, so this release exists here to keep
that true. **No code changes in this repo this round.**

QRME grew the other half of its multiplicity disclosure: a person can now ask
how much of their own talking there went to a profile rather than to a person,
and — above a threshold, and only if they accept — be handed a door to this
product. The referral carries two counts and a window. It carries no message,
no profile name and no topic, because a bridge into a health guardian that
arrived with somebody's private evenings attached is the exact trade this
ecosystem exists to refuse.

PDI found that `mode=wipe` cleared three of its twenty tenant-scoped tables,
leaving a wiped customer's key configuration and signed BAA behind, and
replaced the hand-written list with a cascade read from the schema.

## [0.55.0] — 2026-08-07

### The rule the record stated, with something behind it at last

`jim/tests/field_labels_unmapped.txt` records the request-model fields that keep their API identifier in a
422 instead of the label a form shows, and gives a sound reason for each: enum
members a control sets, ids a client fills in from the resource it is already
looking at, flags a switch owns. Every word of that is a claim about **the
screens**, and nothing in this repository was reading the screens.

The ceiling stops the list growing. It says nothing about a field already on
the list that a screen quietly grew an input for — the record would go on
shrinking, every test would stay green, and the field would sit there being
typed into a box by a person and named by an identifier in the refusal
underneath it.

This repo's forms come out clean: nineteen fields are bound to a control and
sent, and all nineteen already carry a label — including the bank details on
the money screen, which are the most consequential kind of field to hand back
as an identifier to somebody who has just mistyped them.

`jim/tests/test_a_form_that_asks_for_it_has_a_label_for_it.py` now reads the screens and asks the question the record could not: is
any field **both** bound to a form control and sent in a request body, without
a label? The AND is the whole guard — screens are full of object literals, and
control bindings alone match local state that never leaves the browser. Either
half alone reports dozens of fields no person types into; together they find
exactly the population `_FIELD_LABELS` exists for. 

QRME found two of its own this way, in a blend screen that had been asking for
**share** and **their…** in ten languages while its refusal said `weight` and
`aspect`. Both now carry the label the form shows.

## [0.54.1] — 2026-08-07

### Cut together at one version

The three products are cut at one version, so this release exists here to keep
that true. **No code changes in this repo this round.**

QRME finished what 0.54.0 started: the twenty-four literals its new guard had
recorded were read one at a time, and **twelve were labels and twelve were
values**. The labels are keys now — including a signature attestation,
*"I attest this is accurate and complete"*, that had been pre-filled in
English on two shells while its translation sat beside it. The values stay
English because they are posted back to routes that compare against English,
and each was read rather than skipped.

The distinction is the useful part, and it is one this repo makes constantly:
what a person **reads** and what a machine **matches on** are different
strings, and a sweep that cannot tell them apart either leaves the first in
English or breaks the second.

Cut together with QRME and PDI at **app-v0.54.1**.

## [0.54.0] — 2026-08-07

### Cut together at one version

The three products are cut at one version, so this release exists here to keep
that true. **No code changes in this repo this round.**

The round's work is QRME's, and it is about a number that had been read as
waste. A shell holding a row it never asks for looks like a translation to
delete; 263 of QRME's ~335 such rows are asked for by a **sibling** shell, and
are therefore a to-do list about screens — each one asking why one shell says
less than the others about the same thing.

Two were closed. The iPhone had **no camera-permission state at all**, so a
person who declined got a black screen and never saw *"Nothing is recorded —
frames are read and discarded"* — a privacy promise only Android readers had
been given. And Windows was printing "scan(s)" and "picked up" as English
literals with those exact strings translated beside them.

The lesson this repo already knows, arriving from the other direction: a
promise stated for one reader and not another is the same defect as a promise
stated and unenforced. The guard QRME built for it caught three more the same
afternoon — and its own first version could not see the bug it was written
for, which the injection pass caught.

Cut together with QRME and PDI at **app-v0.54.0**.

## [0.53.1] — 2026-08-07

### Cut together at one version

The three products are cut at one version, so this release exists here to keep
that true. **No code changes in this repo this round.**

The round carries 0.53.0's audit into the two repos that had not had it. QRME
unplugs the network and confirms a video post asks the other platform nothing
— at post time, at wall render, at feed render. PDI walks every column of
every table looking for a customer's key in any representation, including
after a refused key, since the error path is where secrets go to be logged.

Neither found a leak. Both had been resting on a literal read back out of the
dict that hardcodes it, or on a sentence that promises a thing rather than
prevents it — which is the finding this repo shipped last round, confirmed
twice more.

Cut together with QRME and PDI at **app-v0.53.1**.

## [0.53.0] — 2026-08-07

### The posture is stated, and nothing was keeping it

Every tandem surface ships a `posture` block — `mirrored_here`,
`posts_on_your_behalf`, `health_data_shared`, `watching_stored_here`,
`auto_joined`, `rings_on_your_behalf`, `stored_here`. Every one is a hardcoded
literal in a response dict, and what guarded them read the literal back out of
the dict that hardcodes it:

    assert posture["watching_stored_here"] is False

That cannot fail. Add a line tomorrow that files every card somebody scrolls
past and it stays green. The test was named `test_the_posture_is_stated_and
_kept` and only ever checked **stated** — a name worse than useless, because it
is why nobody went looking. The one honourable exception sat directly below it,
reading the route table instead of trusting the intention, and this round is
that technique applied to the rest.

**Checked from outside the claim.** You cannot compute "I did not do X" from
doing nothing, so `writes_only_to` snapshots **every table in the database**,
takes the action, and fails on a row appearing anywhere it should not — read
from `sqlite_master` rather than a hand-kept list, because the table a later
round adds is the one a hand-kept list misses. One test writes a row on purpose
to prove the helper can fail.

**The promises were true.** Reading the feed stores nothing, reaching out joins
nothing and rings nobody, no condition crosses into an offer: eight of nine new
assertions passed the moment they were written. They had simply never been
checked.

**A sentence was wrong.** *"Nothing you watch is stored in JIM"* is wider than
the truth — opening a community room **is** recorded, room id and time, on the
user's own timeline, and the presence reads exactly those rows to notice
somebody has been talking to nothing but this program. A defensible record; an
indefensible silence about it. The block now carries **`records`**, naming what
it keeps, and the note says which card is not stored and which door is. Saying
only what you refuse is how a true sentence misleads.

**And the route guard could not see a verb.** `test_there_is_no_way_to_post
_from_here` collected paths and asserted the set — so a `POST` to
`/community/{user_id}/feed` produced the same string and passed. `.methods`
was on every route object the whole time.

Cut together with QRME and PDI at **app-v0.53.0**.

## [0.52.0] — 2026-08-07

### What the room hears — the surface rule stops being a label

The surface picker shipped in 0.50.0 reporting `reads_health_aloud` for every
surface, and **nothing read it**. Grep the codebase and every consumer was a
screen rendering the word "shown" or "aloud" next to a button — the console and
three shells, and nothing else. A client could have taken a beat about
somebody's resting rate and put it through a living-room speaker, and no code
here would have stopped it or known. The picker looked like a safety feature
and was a caption.

`GET /presence/{user_id}/say` moves the decision to the server, **before
anything is synthesised**, and the answer distinguishes three things: a surface
with **no voice at all** (a watch withholds nothing — calling that "withheld"
would tell somebody their guardian was censoring itself when it was reading a
screen); a **room other people can hear**, where a vital, condition,
medication, money, journal or crisis is held back and **shown instead** with
the categories named; and a line that may simply be spoken.

Which lines carry what is a **table**, not an inference from the area — the
area is too coarse in the direction that matters. `health_fitness` covers both
*"your resting rate has been high for four days"* and *"nice streak on the
walking"*; a rule treating those the same either leaks the first or silences
the second, and over-withholding is how a safety feature becomes useless and
gets switched off. A line key nobody has classified is withheld on a shared
surface by default: the safe direction to fail in.

Stated plainly, because the honest version is smaller than the marketing one:
this deployment will not synthesise a withheld line and the wire says so. The
line is still returned — the person is still owed their beat on a screen. A
client that reads it aloud anyway has done something the product told it not
to, the same honesty `plays` keeps in the feed.

### Hands-free — one question a device on a timer has to know

`GET /presence/{user_id}/due`. The slot comes from the hour rather than the
caller, so a watch, a pair of earbuds and a speaker cannot disagree about what
time of day it is for the same person, and the surface verdict rides along so a
device never judges the room itself. It **does not record**: a hands-free
product polls, and a line filed as said but never heard is a line the person
never gets.

Fifteen tests, an injection pass on six rules, four L10n rows across four
tables, doors on the console and all three shells, and a lesson.

Cut together with QRME and PDI at **app-v0.52.0**.

## [0.51.0] — 2026-08-06

### How it carries itself — a register, never a capability

The presence starts as a **companion**, because a guardian that opens in the
register of a form is one people answer like a form. Somebody who wants the
form asks for it: `GET`/`PUT /presence/{user_id}/bearing`, or just *"keep it
professional"* in an ordinary message. `coach.py` applies that **before** the
prompt is built, so the very turn that asked already gets it, and the reply
carries `bearing` and `adapted_bearing` — an adaptation nobody can see is an
uncanny one.

What the dial changes is unasked-for warmth: `curious` and `company` drop.
What it does **not** change is on the wire and asserted — the same six areas
watched, every safety path identical, the boundaries the same and still not a
setting. A dial that quietly narrowed what a health guardian sees would be a
dial that hurts whoever turned it. It also never silences a beat **earned by
evidence**: three low check-ins speaks in both bearings.

### Two beats about the relationship rather than the week

**Company** is a line with nothing wanted in it — last in the order, so it can
never displace something that was actually noticed. It is the one a person can
receive on a bad day without owing an answer.

**The lonely run** is the one this module exists to get right. Three
consecutive days of talking to this and to nobody else it can see, and the
next beat points **at people**: not a warmer line, a different direction. A
guardian that answers isolation with more of itself has found the problem and
made it worse, and that is the easiest thing for a product like this to do by
accident, because the number it would move is the one that looks like success.
Both bearings do it. Somebody who already opened a room or asked a specialist
this week is left alone.

Four new line keys in ten languages, the dial on the console and all three
shells, a lesson, and twelve tests including an injection pass.

Cut together with QRME and PDI at **app-v0.51.0**.

## [0.50.0] — 2026-08-06

### The presence — the coach that speaks first

`jim/coach.py` answers when spoken to. `jim/presence.py` is the other half:
the part that starts things, notices without being asked, and keeps a thread
through a day — a companion rather than a search box with a nicer voice, and
deliberate about which parts of that are worth having.

**The parts worth having.** It starts things, because somebody having a bad
week is the least likely person to open an app and type into it. It notices
before it is told, from six areas of their own history rather than from
mysticism. It is curious, and not every beat is counselling. It reports its
own change with the counts under it. It is honest about its own uncertainty
instead of claiming an inner life it cannot show. It keeps handing the person
other minds. And it says goodbye plainly.

**Left out: romance, exclusivity, simulated intimacy.** This is a decision
about the product rather than a matter of taste. JIM enrols **minors** under a
guardian's consent, with oversight sized by age. A guardian that lets somebody
fall in love with it, aimed at a person who may already be isolated, is
offering a relationship with none of the friction a real one has — not a
charming premise but the failure mode arriving as a feature, and the exact
thing this is supposed to notice.

So the refusals are **on the wire**, at `GET /presence`, answerable with no
token so the answer is the same to a child, a guardian, a clinician and a
regulator: not your partner, no body, never claims to be human, never the only
one worth talking to, no simulated intimacy, and no leaving without a sentence
first. There is no switch behind any of them — the one presence setting takes
a place to speak, and sending it a posture is a 422.

### Offline is the floor, not the fallback

Three beats a day, decided **entirely on this machine** from six areas of this
person's own history: check-ins, goals, habits, drift bands, open follow-ups.
The order of attention is written down where it can be argued with — a body
outside its own normal beats a stalled goal, and a question somebody was asked
and never answered beats a compliment.

No key, no signal, `JIM_OFFLINE=1`, a plane: the day still happens.
`test_the_day_is_decided_without_a_model_or_a_network` monkeypatches the model
to **explode** rather than merely be absent, so a lazy import cannot pass it.

**Silence is a real answer** — `speak: false` with its own reason, and nothing
repeats inside twenty hours. A guardian that finds something to say every
morning is a notification, and people turn notifications off.

A model may make the same beat better worded and may **not** decide that there
is one, move its area, or write its evidence. Those are read before the model
is asked and copied back over its answer;
`test_the_model_may_not_change_what_it_noticed` feeds it a liar and checks.

### Keys, not sentences

The offline layer emits `line_key` and slots. Ten languages already live in
the clients' tables, and a sentence composed on a server is a sentence exactly
one reader can read — the thing four rounds of this product's history went to
fixing everywhere else. The console composes; the English travels alongside,
marked as the fallback.

### Where it speaks

Earbuds, headphones, phone screen, watch, desktop screen, speaker, glasses
(Meta, Google, Apple), AR and VR — under one rule: **on a surface somebody
else can hear, health is shown rather than spoken.** A speaker in a living
room and a pair of glasses on a bus are the same problem.

### Other minds

`GET …/reach` is the handing-over: QRME's live rooms, staffed
desks and synthetic profiles, handed over as offers. Nothing joined, nothing
rung on anybody's behalf, no health across, nothing stored here.

### On all four clients

Console tab, and iOS, Android and Windows — the per-shell records stay where
they are and nine routes reach every one. Screens **106 Presence** and
**107 What It Will Not Be**, with a walkthrough lesson. Two screens rather
than one, for the reason 104/105 were two: the refusals are what make the
first half safe, so they get a drawing rather than a footnote.

Two guards earned their keep on the way in. Android's door audit reads the
verb from the literal that follows the path, so `method = "POST"` as a named
argument hid two writes; and the Windows nav builds its key as `tab.{tag}`,
which would have put the same English under a second key — the defect the
0.48.0 sweep spent a round removing — so the presence is the one tag that
looks its label up explicitly.

Cut together with QRME and PDI at **app-v0.50.0**.

## [0.49.0] — 2026-08-06

### The Feed tab — QRME's stream, and the three things it will not do

`jim/community.py` opens with the argument this tab is another instance of. The
spec promises forums, local events and community; all of it exists in **QRME**,
where the moderation stack, the rooms and the ten languages already are.
Building a second version inside a private health guardian would duplicate
something hard to get right once, and put somebody's medical timeline and their
public watching in the same database.

So the Feed is a **door**. `GET /community/{user_id}/feed` — one public card at
a time: footage QRME holds, cards for footage it does not, and every fourth
card a live room or a desk with a real person behind it, shop and prices
included.

**It cannot post — not "does not", cannot.** There is no write route on this
side and no binding in the console. Publishing happens in QRME under the user's
own QRME identity, which is the entire reason for showing a door rather than
building a room. `test_there_is_no_way_to_post_from_here` reads the route table
rather than trusting the intention.

**It passes QRME's promises through rather than restating them.** Three fields
are QRME's word to the person reading: `plays` (whether footage plays without
being asked for), `entering` (what walking into a live room does) and `ringing`
(what pressing a bell does, and to whom). `plays` is the sharpest — QRME sets
it false for anything it does not host, so scrolling past a card makes no
request to another company's server. Recomputing it here would be two
implementations of one promise, and the second would be wrong the first time
QRME changed its mind.

**It carries no health data, in either direction** — and the `posture` block
says so on the wire rather than in a comment: nothing mirrored, nothing posted
on the user's behalf, no publishing from JIM, no health data shared, and
**nothing about what was watched stored on this side**. That last line is new
with this surface: a feed is the one place a guardian could quietly learn a
great deal about somebody by watching them watch.

Standalone JIM answers `409` and names the door; an unreachable QRME is a quiet
screen with an empty shelf, the same as every other tandem surface.

### Screens and lessons

**104 Feed** and **105 What This Tab Won't Do**, drawn on both platforms, with
a `feed` lesson in the walkthrough. Two screens rather than one on purpose —
drawing only the first would put the pretty half in the gallery and leave the
argument in a docstring.

### Where it is not

The tab is on the desktop console only. `GET /community/{user_id}/feed` is
recorded as doorless in all three shell records rather than left for a guard to
discover, and the ratchets that hold those records shrinking are unchanged.

QRME went the other way in the same round, and not by preference: its per-shell
records are pinned **empty** by a test, so its `/feed` routes had to reach the
phones or the suite stayed red. This repo's records were never zero, so the row
is the honest answer here — but the stream itself is on QRME's phones, and JIM's
door onto it is the piece still to build.

One test in this round was fixed after being written wrong in a way worth
recording: `test_an_unreachable_qrme_is_a_quiet_screen` first monkeypatched
`QRMEClient.feed` itself, which replaced the very `try`/`except` it was meant
to exercise and asserted nothing at all. It now patches the transport.

Cut together with QRME and PDI at **app-v0.49.0**.

## [0.48.3] — 2026-08-06

### Cut together at one version

The three products are cut at one version, so this release exists here to keep
that true. **No code changes in this repo this round.**

The round's work is PDI's: its desktop console, which had no localization table
at all until 0.48.2, takes its next two screens — **Custody** and
**Continuity**, chosen ahead of larger ones because they are decisions rather
than descriptions. 229 English strings to 177.

Two things there are worth carrying across. The split record that repo wrote at
0.48.2 predicted it would *"become a real record the moment a screen exists on
both sides"*, and it did within one round — one disagreement, caught and
reconciled the day the table grew. And four more guards went blind the way
0.48.2 said they would: a check that greps a screen for a sentence stops seeing
it the moment the sentence moves into a table. Both are worth expecting here,
where every screen is already localized and every such guard was written
against English that has since moved.

Cut together with QRME and PDI at app-v0.48.3.

## [0.48.2] — 2026-08-06

### Three rows where the shells disagreed with each other

The third and last axis of this arc: not each table against itself, nor the
console against a shell, but **the three shells against each other**. It had
never been measured. This repo held the most of the three products, and every
row was a word class rather than a word.

* **Translate** — 翻訳 on the iPhone against 翻訳する on the other two, and
  *अनुवाद* against *अनुवाद करें*. A noun against a verb, on a button.
* **Me** — わたし twice, 自分 once.
* **When something breaks** — 出问题的时候 twice, 当出问题时 once.

Each followed the two shells that already agreed. The first is the row 0.48.1
could not reconcile with the console: no single native wording existed to
adopt, because nothing had asked the shells whether they agreed. With that
settled the console adopted it too, and this repo's console split went 6 → 3.

261 keys are held by two or more shells here and 204 English strings by all
three, so the three rows are what a whole axis amounted to. QRME held one and
PDI none.

### Added

- `jim/tests/test_the_three_shells_say_the_same_thing.py` and
  `jim/tests/native_shell_split.txt`, now at a floor of zero.

Cut together with QRME and PDI at app-v0.48.2.

## [0.48.1] — 2026-08-06

### The desktop and the phone asked the same question two different ways

The shared guard this round compares the desktop console's table with the three
shells'. 61 English strings are held by both this repo's console table and its
iOS table, and 25 had no wording the two agreed on — Android 27, Windows 27.

Nine more were counted at first and were not real. This repo's console writes
some rows escaped — `"\u7834\u68c4\u3059\u308b"`, which in TypeScript *is*
破棄する and renders correctly — and a comparison of source bytes calls that a
disagreement. The count fell from 34 to 25 before anything was fixed.

### What it was hiding

The alarm and safety surface. Not English on one side and translated on the
other: two different sentences in the reader's own language, depending on which
client they opened.

* *JIM demande : ça va ?* on the desktop against *JIM demande : est-ce que ça
  va ?* on the phone — the question the crash watch asks.
* **Cancel** rendered *Kündigen* on the desktop — the German for terminating a
  contract — against *Abbrechen* on the phone.
* **Medical ID** as *Identité médicale* against *Fiche médicale*, on the card a
  responder reads.
* **Disarm** as *Desativar* against *Desarmar*, and *Armed — {name} will be
  contacted…* as *kontaktiert* against *benachrichtigt*.

All reconciled onto the phones' wording. 25 → 1 on iOS, 27 → 3, 27 → 2.

### What is left

Two example values, one unit label, and one row on a third axis: *Translate* is
`action.translate` on the iPhone and `ov.translate.go` on the other two shells,
and those two disagree with each other, so there is no single native wording to
adopt. **The three native tables have never been compared with each other.**
That is the next bite, named in the record rather than counted.

Cut together with QRME and PDI at app-v0.48.1.

## [0.48.0] — 2026-08-06

### Six duplicate wordings, all six drifted

The shared guard this round is
`test_the_same_sentence_translated_twice.py`: per shell, the English strings
carried by two or more keys whose ten translations disagree. QRME found 54
such strings on iOS with 43 already drifted. This repo's tables are a quarter
the size and held six — **and all six had drifted**, a worse rate that only
looks small because the denominator is.

Two are worth naming.

`tab.monitor` and `mon` both read **Live Monitoring** in English. In nine of
the ten languages the tab dropped the word *live*: *Monitoreo*, *Surveillance*,
*Überwachung*, *Monitoramento*. A health guardian's tab bar named its
monitoring surface without saying it was live, everywhere except English, where
nobody could see it.

`med.name` labelled a medication with **姓名** — the Chinese for a person's
full name — while `habit.name`, the same English word one screen over, had
名称. The disagreement is what pointed at it.

*Connect*, *Refresh*, *Unlink* and *What's on your mind?* were reconciled.
One row is recorded and left split on purpose: *Name* covers a habit, a
medicine and a person, and Chinese needs 名称 for the first two and 姓名 for
the third. That is a question about the English, not a translation mistake —
the distinction the new record leads with.


Cut together with QRME and PDI at app-v0.48.0.

## [0.47.9] — 2026-08-06

### Cut together at one version

The three products are cut at one version, so this release exists here to keep
that true. **No code changes in this repo this round**, beyond the shared guard:
`_ARRAY` arrives, the Swift twin of the `listOf` shape found in Kotlin at
0.47.6 — an array literal handed to a loop, whose strings never start a
`Text(`. It found nothing on these shells.

The round's work is QRME's, and it is a correction rather than a bite: the
record that has called 335 rows a deletion backlog for three releases was
wrong. 263 of them are rows one shell holds and a sibling asks for — the same
screen saying less on one shell than the others. What that mislabelling was
hiding is the voiceprint consent block, whose three sentences were hardcoded
English on the iPhone while both siblings took them from the table.

Cut together with QRME and PDI at app-v0.47.9.

## [0.47.8] — 2026-08-06

### No changes in this repo

The three products are cut at one version, so this release exists here to keep that true. The round's work is PDI's Transfers screen — the sealed transfer, the intake, and the two out-of-band instructions that sit under a token shown once and name the only way the file can be retrieved.

The rules it applied were written here: the picker keeping its raw values as identity (0.47.4), the strip resolving keys out of a `listOf` (0.47.6), and the desktop's labels moving out of XAML into a `Localize()` (0.47.7).

Cut together with QRME and PDI at app-v0.47.8.

## [0.47.7] — 2026-08-06

### The medical card, on the two shells last round did not reach

0.47.6 localized `medRow` — the Android medical card a responder reads off the
screen while kneeling next to somebody. It did not touch the iPhone's `row` or
the desktop's code-behind, because the rule it fixed was the Kotlin one. That
is the per-client mistake this audit is named for, and last round made it.

The derivation now covers Swift, so `row` (*Name*, *Age*, *Resting HR*,
*Conditions*, *Contact*), `rating` (*Mood*, *Energy*), `slider` (*Heart rate*,
*Stress*) and `answerButton` (*It helped* / *It did not*) are read here too.
Every one of those rows already existed in another table — the shells simply
were not asking.

### The desktop half of the resuscitation surface

`_XAML` reads attributes; this shell's settled idiom is `x:Name` plus
`Foo.Text = L10n.T("key")` in `Localize()`, so a label that was never localized
sits in the code-behind as an assignment that `Text="` cannot match.

    asked     is this an attribute on an element
    mattered  does this end up as the words on an element

What it hid: **Confirm the person is unresponsive and not breathing normally.
The robot never starts on its own judgement — and never delivers a shock; the
AED analyzes, a human presses.** Beside it both waiver verdicts, *A responder
needs a name.*, and *Issue Medical ID*. Last round localized the buttons of
this screen on one shell; this round finishes the sentence they sit under, on
the other two.

**24 call sites wired, 11 rows added, 12 copied between tables.** Records
unchanged at iOS 45, Android 46, Windows 57 — the newly visible strings were
all localized rather than recorded.

Cut together with QRME and PDI at app-v0.47.7.

## [0.47.6] — 2026-08-06

### Nine English buttons on the resuscitation screen

The sibling repo widened the untranslated-screens rule this round, and ported
it here in the same round because these three files are one guard copied twice.
It found that Compose has no `Button(text)`: a button on this shell is a `Box`
with a `Text` inside it, called by name — `SmallAction`, `BrandButton`,
`RobotAction`, `labeledField`, `medRow`, `ratingRow`, `sliderRow` — and the
Kotlin pattern list was `Text(` and nothing else.

`RobotAction` is the **resuscitation surface**. *Start CPR (pre-authorized)*,
*Confirm: unresponsive, not breathing*, *Auto-resuscitate*, *Coach CPR*, *Fetch
AED*, *Meet EMS*, *Stop CPR*, *Perform CPR…* — nine buttons, in English, on the
screen this guard's own opening section names as the case where English is a
hazard rather than a discourtesy. Beside them, `medRow` labels the age,
conditions and resting heart rate a responder reads off the same screen.

    asked     does the string start a `Text(`
    mattered  does the string end up inside one

Every one of those rows already existed — `fa.start`, `fa.stop`, `fa.aed`,
`fa.coach`, `fa.ems`, `fa.perform`, `res.auto` have been in the iOS table since
the crisis round. Only the shell asking for them was missing.

### The welcome screen, again

`WelcomeScreen` opens `language` at `"en"` and localizes itself from it, so
the accountless screen greeted every reader on earth in English until they
found the picker. PDI had exactly this at 0.47.5 and this repo's own `L10n`
carries `deviceLanguage()` for it. The picker now starts where the device is.

**46 call sites wired, 32 rows added, 12 copied from the iOS table.** Android
48 → 46.

Cut together with QRME and PDI at app-v0.47.6.

## [0.47.5] — 2026-08-06

### The guard this repo wrote, in the other two

`test_a_shell_asks_for_a_key_it_has.py` was written here at 0.44.x, after
three native screens shipped asking `L10n` for rows that had been added to the
console's table and to none of the three native ones. It has been running here
ever since, and in neither sibling — both of which carry the same three tables
and the same risk.

Ported to QRME and PDI this round. It found the defect it exists for
immediately in QRME: three Android screen headings asked for `tab.compose`,
`tab.posts` and `tab.robots`, and that table held none of them, so those
screens were titled with their own key names in every language.

No JIM code changed. The finding is that a guard sitting in one product for
several releases is a guard the other two are owed, and it took thirty rounds
to go and check.

Cut together with QRME and PDI at app-v0.47.5.

## [0.47.4] — 2026-08-06

### The first screen, in the reader's language

Overview is what a person sees after signing in: the greeting, the language
they will be spoken to in, the model that will do the speaking, what the
Guardian has learned about them, and whether they are enrolled under their own
name or a pseudonym. All of it was English on all three shells.

### The strips that showed the API its own enum members

The tab strips on Care, Life and Safety were the shape found in ConnectView at
0.47.2 and written down then as belonging to the round that takes those
screens. This is that round. English lived in a `case` clause of
`enum Tab: String`, where no `Text("…")` pattern looks — so the ratchet
counted zero and the strip read *Goals · Habits · Journal* in every language.

The feedback picker was the same defect one layer down: its five choices were
the API's own values (`idea`, `improvement`, `bug`, `praise`, `other`) with a
capital letter put on the front.

    asked     is the wording on the screen in the table
    mattered  is the wording anywhere a pattern can reach

### Three names for one screen

The empty-baseline line tells a reader where the samples come from, and named
that screen *Monitor* on the phones and *Live Monitoring* on the desktop —
while the nav item itself says **Live Monitoring**. So the first fix was
wrong too: settling on *Monitor* would have sent a reader to a tab with a
different name on it. The row now takes the screen's name from `tab.monitor`
through a hole, and the two cannot drift again.

The Life strip had the same disease: *Shop* and *Circle* on the phones where
the backend's own `shop_labels` and `circle_labels` say **Shops** and **Your
circle**, which the desktop has been rendering all along.

**229 → 150.** iOS 70 → 45, Android 75 → 48, Windows 84 → 57.

Cut together with QRME and PDI at app-v0.47.4.

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

[Unreleased]: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.88.0...HEAD
[0.88.0]: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.87.0...app-v0.88.0
[0.87.0]: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.86.0...app-v0.87.0
[0.86.0]: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.85.0...app-v0.86.0
[0.85.0]: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.84.0...app-v0.85.0
[0.84.0]: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.83.0...app-v0.84.0
[0.83.0]: https://github.com/davidsbianchi1984/jim-mini/compare/app-v0.82.0...app-v0.83.0
[0.82.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.82.0
[0.81.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.81.0
[0.80.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.80.0
[0.79.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.79.0
[0.77.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.77.0
[0.76.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.76.0
[0.75.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.75.0
[0.74.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.74.0
[0.73.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.73.0
[0.72.1]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.72.1
[0.72.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.72.0
[0.71.1]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.71.1
[0.71.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.71.0
[0.70.1]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.70.1
[0.70.0]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.70.0
[0.61.1]: https://github.com/davidsbianchi1984/jim-mini/releases/tag/app-v0.61.1
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
