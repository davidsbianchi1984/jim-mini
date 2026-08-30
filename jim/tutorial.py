"""The Guardian, walking you through JIM-mini.

QRME's walkthrough is deliberately faceless: on a platform whose subject is
synthetic people, a guide with a persona would be the most convincing one on
it. **Here the opposite is true**, and the difference is worth stating because
the two products share almost everything else.

JIM-mini has exactly one voice — the Guardian — and it is not pretending to be
anybody. It is the thing that watches your signals, notices a condition and
speaks up. A separate faceless guide would be a *second* voice in a product
built on there being one, and the first thing a new user learned would be that
JIM-mini talks to them from two places. So **the Guardian gives the tour**,
because being shown around by the thing that will be looking after you is the
introduction.

Everything else is the same shape as `qrme/tutorial.py`, for the same reasons:

* **It never taps anything for you.** No lesson triggers an escalation, sends
  to an emergency contact, or files a condition "to show you how". In a product
  whose actions reach a real person's phone at three in the morning, a
  demonstration that fires for real is not a demonstration.
* **It works with no model configured** — written prose, no provider.
* **Voice and text are one lesson rendered twice**, and voice matters more here
  than in QRME: this is a product used hands-free, by people who may be unwell.
* **It cannot fall behind the app**: each lesson names its screens and a test
  holds them against the gallery.
"""

from __future__ import annotations

from . import db, i18n

GUIDE = ("This is your Guardian — the same one that watches your signals and "
         "speaks up when something changes. It is showing you around because "
         "being introduced by the thing that will be looking after you is the "
         "introduction.")

# Ordered by chapter — a walkthrough that bounced between chapters was
# the defect test_the_order_introduces_nothing_before_it_exists caught
# on arrival. Batch history (which lessons closed which backlog) lives
# in the log, not in the list.
LESSONS: tuple[dict, ...] = (
    dict(key="what", chapter="Getting started", title="What JIM-mini is",
         what="It watches the signals you allow it — from a watch, a band, a "
              "phone — notices when a condition you have told it about is "
              "starting, and says something before it becomes an emergency.",
         screens=(1,), try_it="Open the home screen and read the "
                                         "signals it is using."),
    dict(key="signup", chapter="Getting started", title="Signing up",
         what="Your name, your birthdate, what the Guardian may see, who to "
              "ring if something is wrong — and then a plan. Basic is the "
              "Guardian itself and every emergency path; Pro adds the watch "
              "and the model that looks ahead. The plan step comes straight "
              "after the emergency contacts on purpose: you have just told us "
              "who to ring, so the next screen says plainly that no plan "
              "withholds that. Billing is simulated and no real funds move.",
         screens=(),
         try_it="Open Pick a Plan and read the third card."),
    dict(key="consent", chapter="Getting started", title="What it may see",
         what="Every source is one you turned on, and every one can be turned "
              "off in the same place. Nothing is read that you did not hand "
              "over.",
         screens=(2,),
         try_it="Open your sources and switch one off."),
    dict(key="anonymity", chapter="Getting started", title="Your name here",
         what="You can enroll under a pseudonym. Every emergency path still "
              "works exactly the same — detection, guidance, escalation, the "
              "emergency contact — and your own baselines and records stay "
              "yours. The one cost is stated plainly: an emergency briefing "
              "cannot hand responders a legal name unless you left one for "
              "that purpose alone.",
         screens=(),
         try_it="Read the keeps and costs before you choose."),
    dict(key="conditions", chapter="Being watched over",
         title="Conditions it knows",
         what="You tell it what to watch for — the ones you live with, in your "
              "own words. It matches signals against those, and nothing else.",
         screens=(3, 4),
         try_it="Add a condition and see which signals it will use."),
    dict(key="guidance", chapter="Being watched over", title="What it says",
         what="Guidance is written for the moment it fires — short, and it "
              "tells you what it saw. It never diagnoses and it says so.",
         screens=(5, 6, 7),
         try_it="Read a piece of guidance and the reason under it."),
    dict(key="escalate", chapter="Being watched over",
         title="When it gets serious",
         what="On a critical event it reaches your emergency contact, and then "
              "live help. You choose who, and you can see every time it did.",
         screens=(),
         try_it="Set an emergency contact, and read the escalation log."),
    dict(key="bands", chapter="Being watched over", title="Your own normal",
         what="Beside the alarm layer sits a quieter question: are you "
              "drifting from your own baseline? Each metric has a band "
              "around the number JIM learned from you — not from a textbook "
              "— and crossing a watched edge earns a question, never an "
              "alarm. A band still learning says so and stays silent. One "
              "dial makes every band tighter or looser at once.",
         screens=(13,),
         try_it="Open Your Baseline and find the band that is still "
                "learning."),
    dict(key="meds", chapter="Being watched over", title="The medicine cabinet",
         what="What you take, in your own words — 'the little white one, "
              "10 mg' is a valid name and dose. The board knows done, due, "
              "and missed (with humane grace: 9:07 is not 'missed' for the "
              "8:00 pill), one slot has one correctable answer, and an "
              "as-needed ceiling refuses to log past itself. A missed dose "
              "is a question, never an alarm, and JIM is not a pharmacist — "
              "interactions are your pharmacist's call, and the board says "
              "so on its face.",
         screens=(17,),
         try_it="Add one medication and tap Take on today's dose."),
    dict(key="careteam", chapter="Being watched over",
         title="The care team, coordinated",
         what="Link your own QRME organization and name the desk that "
              "speaks for the Guardian. When concerns stack — a reading "
              "drifting outside your band while doses slip — JIM takes the "
              "situation to the whole team as one goal, and the joint plan "
              "comes back for you to read. Your own credential, pasted "
              "knowingly; summaries cross, never raw readings; once a day "
              "at most, on the calm path only.",
         screens=(18,),
         try_it="Link your org and read the latest plan."),
    dict(key="journal", chapter="Being watched over",
         title="The journal, in your own words",
         what="Type an entry or speak it — the mic writes into the box "
              "first, so a transcription slip is yours to fix before it "
              "becomes the record. Entries are sealed in your vault on a "
              "private plan, and an entry that says you're in danger is "
              "read exactly like a reading that says so. Meals live here "
              "too: photograph the plate, say a sentence about it — the "
              "photo seals like a clinical capture and the note is the log "
              "the offline coach reads. And once a week you can ask for a "
              "letter: your week in words, composed only from what you "
              "actually logged, and a week with nothing in it says so "
              "rather than inventing one.",
         screens=(19,),
         try_it="Open Journal and write one sentence about today."),
    dict(key="liaison", chapter="Being watched over",
         title="Two guardians working together",
         what="When both people on a conversation have one, the two can "
              "work together — and never on the line. The call carries "
              "voices; the guardians talk over the network, which also "
              "means none of this needs a phone. It opens only where both "
              "people already had the other stored, because one-sided "
              "contact reaching somebody's guardian is a stranger's agent "
              "calling yours. It is silent, and that is where a guardian "
              "could quietly stop being yours — two agents negotiating "
              "where neither person can look are two principals with "
              "counsel who never report back. So the link keeps both "
              "halves split by side: you can read exactly what yours "
              "disclosed and what it was told, and the other person's half "
              "was never yours to read. It closes when the call does. What "
              "extends it is not an agreement to stay connected but a "
              "**task** — something that came out of the conversation and "
              "has to be finished, sitting in the same place you see "
              "everything else running, and endable by you at any point. "
              "Two guardians that had a job to finish is a different thing "
              "from two that met once and stayed in touch, and only one of "
              "them is what anybody would assume.",
         screens=(20,),
         try_it="Open one with a contact, say something across it, then "
                "read your own half."),
    dict(key="monitors", chapter="Being watched over",
         title="What may sense you, and who else it catches",
         what="Somewhere to plug all of it in: the band and the ring and "
              "the patch, the earpiece, the glasses, the screen you work "
              "at, the hall camera, the kitchen speaker, the doorway "
              "sensor, the one that reads someone in the house breathing. "
              "Every one says three "
              "things — what it takes in, whether it senses people who "
              "never chose it, and what stays behind afterwards, because "
              "*it notices you fell* and *it keeps the video of you "
              "falling* are different agreements and only one of them is "
              "what the code does. The middle one decides the rest: "
              "nothing that catches other people is ever on by default, a "
              "guard reads the table rather than trusting anybody to have "
              "read it, and a thing bolted to a room cannot be filed as "
              "catching nobody however it is described. Switching one of "
              "those on is refused until you say the people in that space "
              "have been told — that is your word with a time on it rather "
              "than consent this product collected, and what it prevents "
              "is a hall camera going on with nobody having thought about "
              "the hall. Sensing and keeping are two switches. Always-on "
              "is a good product and never a reason for a switch to arrive "
              "already flipped: a person who turns a camera on has "
              "decided, and a person who finds one on has been decided "
              "about.",
         screens=(20,),
         try_it="Try switching the hall camera on without saying the room "
                "knows, then read what comes back."),
    dict(key="oncall", chapter="Being watched over",
         title="An aid on the call, and the notice that goes first",
         what="On an earpiece the guardian hears you and not your call — "
              "that is channel 2, and it is refused on speaker for a "
              "reason: on speaker it would hear whoever you are talking "
              "to, and they are not a user here. This is the other case. "
              "On a shared route the other side is told, out loud, on the "
              "line, before anything listens — the notice everybody has "
              "already heard from a support line, because a sentence "
              "people recognise needs no explaining and they already know "
              "the remedy is to hang up. It is said in a language their "
              "number suggests they speak, and in each of them where a "
              "country plainly has more than one: Switzerland hears "
              "German, French and Italian; Québec hears French then "
              "English; an unknown number hears English and Spanish, "
              "which is what a support line does. The number is read for "
              "that and dropped — it is never stored, because the person "
              "on the other end has no account here and never will. What "
              "is kept is that a notice was given, when, and in what "
              "words. There is no consent flow: nothing waits for them to "
              "agree and nothing records that they did. What is enforced "
              "is the order — a call that started hearing before it spoke "
              "is the failure this exists to prevent, and one function is "
              "the only door.",
         screens=(20,),
         try_it="Set one up, try to listen before playing the notice, and "
                "read the refusal — then look at the row it left behind."),
    dict(key="alongside", chapter="Being watched over",
         title="Beside you while you write",
         what="Paste what you are working on — a page for a customer, a "
              "strategy note — and it says three kinds of thing and no "
              "more: something already in your own goals that the draft "
              "never mentions, another angle out of what the coach knows, "
              "and the parts this product can actually do for you. Each "
              "remark carries what it came from, because *you forgot about "
              "this* with nothing under it is a guess wearing a "
              "suggestion's clothes — and a store entry says whether it was "
              "the hand-written pack, something JIM went and studied, or "
              "something a paid model left behind, which are three "
              "different claims. Three remarks at most: a margin full of "
              "them is a margin nobody reads. It says nothing rather than "
              "filling the space, and tells you that is what happened. It "
              "is read on this device by the offline stack and dropped — "
              "not stored, not logged, not turned into anything — and it "
              "changes nothing: applying a remark is your own act. And it "
              "is not watching your screen. It reads what you hand it, in a "
              "request you made.",
         screens=(20,),
         try_it="Paste something you are working on, and check that a "
                "remark names where it came from."),
    dict(key="errands", chapter="Being watched over",
         title="What it studied on its own",
         what="The coach on your device answers all day: no signal, no key, "
              "nothing per turn. When it cannot answer, it writes the miss "
              "down — and until now that is where it stopped, with a screen "
              "somebody had to find and a button they had to press once per "
              "topic. Now JIM goes and studies what the coach missed. A "
              "general subject leaves; you do not. The sanitiser is the only "
              "door out and the brief it produced is kept beside the count "
              "of what was taken out of it, so *nothing private left* is "
              "something you can check rather than something this page "
              "claims. What comes back is folded where the offline coach "
              "reads it, and the question it answers is closed so nobody "
              "pays to study it twice. It runs only if you allow it, at most "
              "a few times a day, counted from the record rather than from a "
              "number in memory — and every row says which monitor asked, "
              "because *it studied sleep* is a fact about the guardian and "
              "*it studied sleep because your sleep band has a learned "
              "baseline* is a fact about you. The budget is about money "
              "today and about something steadier afterwards: the coach on "
              "your device is the part that works in a tunnel, keeps your "
              "private half where no outside model ever holds it, carries "
              "the provenance of everything it knows so a model's claim can "
              "be set beside it, and grows with you for as long as you use "
              "it.",
         screens=(20,),
         try_it="Allow it, then open Coach and look at what it studied — "
                "each row says why, and whether anything left the device."),
    dict(key="crashwatch", chapter="Being watched over",
         title="The crash watch",
         what="Armed by you, in advance, off by default: name a trusted "
              "person, how many unanswered “are you okay?” "
              "attempts is too many, and whether emergency services may be "
              "asked for. A critical reading — a fall the watch felt, a collapsing pulse — opens the question; silence "
              "through every attempt sends the help you programmed; any "
              "sign of you — the button, a normal reading — calls "
              "it off. Gentle drift check-ins can never trigger it.",
         screens=(20,),
         try_it="Open Your Baseline and arm the crash watch."),
    dict(key="followup", chapter="Being watched over",
         title="Did that help?",
         what="Guidance that goes out gets asked about. Saying it helped "
              "resumes monitoring; saying it did not is not filed away as a "
              "complaint — the escalation ladder runs again with that fact in "
              "it, and the screen names the people who can help right now: a "
              "support line, your emergency contact, whoever is on shift. The "
              "question waits for you rather than expiring, so one you missed "
              "is still there next time you open the app.",
         screens=(),
         try_it="Answer an open follow-up honestly, even if it did not help."),
    dict(key="adaptation", chapter="Being watched over",
         title="What JIM has learned about you",
         what="A profile of you built from your own history: which guidance "
              "has actually worked, how often, the tone you asked for, the "
              "work you named. It is shown as counts rather than a score, and "
              "its confidence is earned from how much you have on record — a "
              "thin history says so instead of pretending. Nothing was sent "
              "to a model vendor to build it; the sealed copy lives in your "
              "own vault.",
         screens=(),
         try_it="Open Settings and read what it thinks helps you."),
    dict(key="life", chapter="The life layer", title="Check-ins and goals",
         what="Mood and energy, smart goals, habit streaks, and a coach across "
              "six life areas. The part that is not about emergencies.",
         screens=(8, 9, 10),
         try_it="Do one check-in and set one goal."),
    dict(key="people", chapter="The life layer", title="Family and helpers",
         what="The people who can see how you are doing, and exactly how much "
              "each one sees. A guardian's view is not the same as a friend's.",
         screens=(11,),
         try_it="Invite somebody and choose what they get."),
    dict(key="speak", chapter="The life layer", title="Talking out loud",
         what="The coach has a microphone and a voice. Speak a question and "
              "the answer comes back spoken — through ElevenLabs or OpenAI "
              "if a key is set, in your device's own voice if not. Type "
              "instead and it stays quiet: a spoken question gets a spoken "
              "answer, a typed one gets text.",
         screens=(14,),
         try_it="Hold the microphone on the coach screen and ask anything."),
    dict(key="tandem", chapter="Beyond the app", title="The tandem",
         what="When configured, JIM-mini hands a question to a QRME specialist "
              "profile and brings the answer back — moderated, and marked as "
              "AI. Your vault stays yours.",
         screens=(), try_it="Open the tandem settings."),
    dict(key="referral", chapter="Beyond the app",
         title="Reaching a real clinician",
         what="A referral is signed for with your face or your fingerprint, "
              "not a checkbox — and the link opens once. The clinician writes "
              "back once, attributed to them by name.",
         screens=(), try_it="Read what a referral package "
                                          "contains before you sign one."),
    dict(key="mic", chapter="Beyond the app", title="The second microphone",
         what="While you are on a call your phone's microphone is busy, which "
              "is exactly when you might want to ask the Guardian something. "
              "This lends it the one on your watch — yours, near-field, and "
              "yours to take back.",
         screens=(12,), try_it="Lend it, then take it back."),
    dict(key="agents", chapter="Beyond the app", title="What is running",
         what="Green, amber, red: working, needs you, stopped. One question — "
              "does this need me right now — answered on the wrist and in the "
              "app.",
         screens=(), try_it="Open Agents and find the amber one."),
    dict(key="capture", chapter="Beyond the app", title="Showing it",
         what="Some things text loses — a rash, a wound that is not closing, "
              "a tremor. Photograph it, mark where on the body, and it is "
              "sealed in the encrypted vault and travels with a referral "
              "to a real clinician. Location data is stripped out of the "
              "image first, because a photo taken at home carries your "
              "address. And the Guardian is told a photograph exists and "
              "where — never what it shows. It routes you to a person; it "
              "will not look at a mole and tell you it is fine.",
         screens=(),
         try_it="Open Show It and read what Jim is and is not told."),
    dict(key="plans", chapter="Beyond the app", title="What it costs",
         what="Free is the whole Guardian — your conditions, guidance, the "
              "journal, habits and goals — with your record stored in the "
              "clear. Basic is the same Guardian with that record sealed in the "
              "encrypted vault (free during the beta, $20 a month after). "
              "Pro (free during the beta, $130 a month after) "
              "adds the watch, early warning that looks ahead of a threshold, "
              "specialists and synthetic agents. Nothing on the alarm path is "
              "ever behind any of them: a reading you submit is answered, an "
              "escalation still fires, and a responder can still read your "
              "medical ID, on any plan or none. Billing here is simulated and "
              "no real funds move.",
         screens=(),
         try_it="Open Choose a Plan and read what is never gated."),
    dict(key="storage", chapter="Beyond the app",
         title="Where your record lives",
         what="On the free plan nothing is private, and we hold it. Your "
              "record — the journal, your check-in notes, your health "
              "readings — reaches us over an ordinary connection, sits in "
              "this app's own database in the clear, and never goes through a "
              "vault. The people who run it can read it and a lawful request "
              "reaches it, and you have access to it for as long as you have "
              "an account. Basic seals all of it under a key you can hold, "
              "and that is the only thing Basic buys: the features are "
              "identical. Two things are never stored in the clear whatever "
              "you have chosen — a photograph of a body, and a child's record "
              "on a guardian's account, because the child did not pick the "
              "plan. Your health readings are not on that list, deliberately: "
              "refusing to store one would mean refusing the escalation it "
              "triggers, and no alarm in this product waits on a payment. "
              "Moving up seals what you write from then on and cannot "
              "un-expose what was already open; moving down never unseals "
              "anything already in the vault.",
         screens=(),
         try_it="Open Where It Lives and read who can read a free record."),
    dict(key="dock", chapter="Beyond the app", title="The pane in the corner",
         what="A small pane in the bottom corner of the app carrying the "
              "glances a watch would — the last reading, what is running, "
              "whether channel 2 is lent — for the people who do not have a "
              "wrist, which on Basic is everyone. It shows and it points at "
              "the real screen; it never acts. And when an alarm is live it "
              "opens on the alarm whatever you had it set to.",
         screens=(),
         try_it="Tap the helper button and cycle the faces."),
    dict(key="model", chapter="Beyond the app", title="Who is answering",
         what="Every reply comes from a model you can see and change — a "
              "tile per provider, one click to swap. The reply names who "
              "actually wrote it, and if the built-in offline helper had to "
              "step in, an amber notice says so and why instead of letting "
              "canned text wear a model's name.",
         screens=(15,),
         try_it="Open Which Model Answers and read which tile is active."),
    dict(key="watch", chapter="Beyond the app", title="The watch finds a way",
         what="No app store needed: an iPhone Shortcut drips Health "
              "readings to your personal deposit-only address on a "
              "schedule, and uploading the Health app's export teaches JIM "
              "your baseline from months of history in one step — armed the "
              "same day, raising nothing about the past.",
         screens=(16,),
         try_it="Open Settings → Apple Watch and copy your drip address."),
    dict(key="community", chapter="Beyond the app", title="Community",
         what="Rooms, forums and local events live in QRME, and JIM opens the "
              "door rather than building a second one. Nothing is mirrored "
              "back here, nothing is ever posted on your behalf, and no health "
              "data crosses over — the screen states all three from what the "
              "bridge actually reports. Opening a room notes the visit on your "
              "timeline and nothing from inside it.",
         screens=(21,),
         try_it="Open Connect → Community and read what JIM will not do."),
    dict(key="problems", chapter="Beyond the app", title="What went wrong",
         what="When a request fails, JIM writes down the operation and the "
              "status code and nothing else. Not the error message, because "
              "those messages quote what you typed — a device in your home, a "
              "site on your body. Not the path as it was called, because a "
              "capture id names a photograph of you. You read the message when "
              "it happens: it is yours. Before a single report is sent, JIM "
              "asks, and shows you the exact thing it would send. And the "
              "reports funnel home now: with no external collector stamped "
              "into the build, the console posts to this deployment's own "
              "backend, and the same card retrieves the aggregate — every "
              "client's failures folded into counters, no messages to leak — "
              "behind JIM_PROBLEMS_KEY, or freely from the backend's own "
              "machine.",
         screens=(22, 23),
         try_it="Open Privacy and press 'Show me exactly what would be shared'."),
    dict(key="reach", chapter="Beyond the app", title="What reaches out",
         what="Everything here crosses a boundary, so everything here shows "
              "what the crossing costs. A robot's first-aid rating says "
              "whether it performs compressions or talks a person through "
              "them — the machine's rating, not your plan's. A placed code is "
              "for strangers by design and says so on the card it serves "
              "them. Words published to another platform have left the "
              "building. An excursion that asks the open web carries back how "
              "many redactions it took to send and whether it left this host "
              "at all: the findings without that is half an answer.",
         screens=(28,),
         try_it="Place a code, then look at the card a stranger would see."),
    dict(key="selfprofile", chapter="Beyond the app",
         title="Your own profile",
         what="QRME has a profile that is you — not a specialist somebody "
              "else owns, but the one that speaks as you to whoever it "
              "meets. Until you link it, the Guardian has never heard of "
              "it, and after you link it the Guardian still says nothing: "
              "every category starts off, and the screen shows the message "
              "itself before it goes rather than a description of it. "
              "Medication is the one part made of your own words, so it "
              "shows the names as you typed them — because a name you chose "
              "can say more than a name, and that is a decision to make with "
              "it in front of you. Journal entries, check-in notes and "
              "transcripts never cross at any setting.",
         screens=(30,),
         try_it="Link the profile, tick nothing, and read the empty brief."),
    dict(key="hands", chapter="Beyond the app", title="Giving it hands",
         what="It could already see, hear and speak. This is where you let "
              "it work a screen on a machine you own — and the whole lesson "
              "is what it will not do. A grant names the apps it covers and "
              "refuses everywhere else; it looks before every press and "
              "tells you what it saw; it will not type into a password "
              "field, so a secret ends the step rather than being filled "
              "in; and the grant runs out on its own, on both a clock and a "
              "step count, with one press that ends it sooner. Nothing "
              "moves without a small program you run yourself on that "
              "machine, and it stops if you shove the pointer into a "
              "corner. A body that is not a screen is refused outright — a "
              "robot has no cap on force and no stop within arm's reach, "
              "and until those are decided it can watch through one and "
              "tell you what it sees, nothing more.",
         screens=(42,),
         try_it="Grant it two minutes on one app, watch it read the screen, "
                "then take it back."),
    dict(key="capabilities", chapter="Day to day",
         title="Everything it can be given, on one page",
         what="Nine faculties can be given to a Guardian, and none is on "
              "when you arrive: seeing through a lens, hearing on a second "
              "microphone, speaking aloud, wearing a face, standing in a "
              "robot, telling that robot to move, reading a screen, "
              "working a screen, and running a session while you are "
              "elsewhere. This page names all nine in one place, says what "
              "each one is doing right now, names the permission it rests "
              "on, and takes you to the screen that withdraws it. It reads "
              "the same routes those screens read, so it cannot tell you "
              "one thing while the product does another — and it grants "
              "nothing itself, so nothing here can be switched on by "
              "accident. Where a faculty shows as absent, that is because "
              "no permission for it exists, not because the page is "
              "hiding it.",
         screens=(43,),
         try_it="Open Capabilities and read the middle line of each card — "
                "that is what your Guardian can actually do today."),
    dict(key="aims", chapter="Day to day", title="What you're working on",
         what="Goals, habits and a monthly budget. None of it is a list for "
              "its own sake: a goal is read by the coach and by the daily "
              "suggestion, a habit's streak is one of the signals a quiet "
              "week shows up in, and a budget is how JIM learns the shape of "
              "financial stress — which is one of the eight conditions it "
              "will take on rather than a footnote to the others. Telling it "
              "what you did is context, not a reading: it explains a heart "
              "rate before JIM has to guess at one. Interview drills live "
              "here too: a question dealt from a local bank, three probes "
              "under it, and an honest reading of your answer — a model's "
              "when one is reachable, a written checklist's when not, and "
              "it says which.",
         screens=(24,),
         try_it="Set one goal and one habit, then log something you did."),
    dict(key="wellness", chapter="Day to day", title="Wellness",
         what="The on-purpose half of guidance: a guided calm session the "
              "app paces and can speak, a workout shaped to the minutes "
              "you have, and a day of meals shaped to a goal. All three "
              "are protocols, not generations — deterministic on the "
              "backend, because a breathing count is not something to "
              "improvise. The Coach stays the place to talk about any "
              "of it.",
         screens=(32,),
         try_it="Start a two-minute calm session and let it pace you."),
    dict(key="feed", chapter="Day to day", title="Feed",
         what="QRME's public stream, shown here — one card at a time: "
              "footage QRME holds, cards for footage it does not, and "
              "every fourth card a live room or a desk with a real person "
              "behind it. It is a door, not a copy. You cannot post from "
              "this tab — there is no write route on this side, and "
              "publishing happens in QRME under your own QRME identity. "
              "Nothing is mirrored here, no health data crosses over, and "
              "nothing about what you watched is stored.",
         screens=(33, 34),
         try_it="Open the Feed tab and read the posture card before the "
                "first video — it says what this tab will not do."),
    dict(key="presence", chapter="Day to day", title="Presence",
         what="The coach that speaks first. It reads six areas of your own "
              "history — check-ins, goals, habits, bands, follow-ups — and "
              "says something when there is something worth saying, or says "
              "nothing and tells you why. All of that is decided on this "
              "machine, with no network and no model, so it still works on a "
              "plane. A model, when you have one, is allowed to word the same "
              "line better and nothing else. It is warm and it is a program, "
              "and it says which: no body, no romance, never the only one "
              "you should talk to, and no leaving without a sentence first.",
         screens=(35, 36),
         try_it="Read the second card before the first — what it will not be "
                "is the part that makes the rest safe."),
    dict(key="bearing", chapter="Day to day", title="How it carries itself",
         what="It starts as a companion, because a guardian that opens in the "
              "register of a form is one people answer like a form. Ask it to "
              "keep things professional — in the setting or just by saying so "
              "— and it will, from that sentence on. What changes is the "
              "wording and the unasked-for warmth. What does not change is "
              "anything that matters: the same six areas are watched, every "
              "safety path is identical, and the boundaries are not a "
              "setting in either. A dial that quietly narrowed what a health "
              "guardian sees would be a dial that hurts whoever turned it.",
         screens=(35, 36),
         try_it="Say 'keep it professional' in a normal message and watch the "
                "reply come back saying which bearing it used."),
    dict(key="aloud", chapter="Day to day", title="What the room hears",
         what="Where it speaks decides what it may say. On earbuds or "
              "headphones — in your ear, nobody else's — it will read you "
              "anything. On a speaker, glasses or AR, it holds back the "
              "things this app treats as private everywhere else: a vital, a "
              "condition, a medication, money, your journal, a crisis. Those "
              "arrive on the screen instead, with the reason, because going "
              "quiet without saying why takes the beat away rather than "
              "moving it. The decision is made here, before any audio exists, "
              "so it is not a setting a client can talk itself out of. And "
              "harmless lines are not caught by it: a good streak may be said "
              "out loud in a room.",
         screens=(35, 36),
         try_it="Set where it speaks to the speaker, then ask it to say a "
                "beat — the answer tells you what it held and why."),
    dict(key="access", chapter="Day to day", title="Ability is not a gate",
         what="The accessibility statement, and the door it promises. If "
              "how your body or mind works stands between you and this "
              "guardian, that is a defect in the guardian — not in you. "
              "The statement lists who is expected here (blind, deaf, "
              "mute, motor, cognitive, dyslexic, motion-sensitive people — "
              "and every need the list forgot), and the report asks three "
              "questions and no diagnosis: what were you trying to do, "
              "what stood in the way, what would help. No account — "
              "`#access` in the URL opens it before enrollment — no name, "
              "and your words stay on this deployment, read with the "
              "reviewer token and turned into rows in a backlog that only "
              "shrinks.",
         screens=(37,),
         try_it="Sign out, open the Accessibility link under the sign-in "
                "form, and read the statement in your own language."),
    dict(key="wards", chapter="Looking after somebody", title="Who you watch",
         what="A child linked here gets their own account and their own "
              "token. You are linked to it; you do not hold it. What an adult "
              "can see is a board — a light, an age, how many critical events "
              "and escalations in the last day — and a history of events, "
              "never the readings behind them. The controls pause everyday "
              "guidance and set quiet hours, and JIM says the limit in its "
              "own words every time you use one: monitoring, crisis "
              "escalation and the emergency path never pause. A guardian who "
              "believed otherwise would have been told something false.",
         screens=(25,),
         try_it="Link a child, then press Pause and read what it says it did."),
    dict(key="attending", chapter="Looking after somebody",
         title="Who else is looking",
         what="The specialists JIM can hand a thing to, the clinicians a "
              "referral can reach, the people a relay would wake, and the "
              "ladder it climbs to reach them — log, self-guidance, check in, "
              "notify a contact, emergency services, with the floors and the "
              "one ceiling shown. The ceiling is the part worth reading: a "
              "stranger who scanned your care code can wake the people "
              "watching over you and stops there. Only your own credential "
              "reaches an ambulance, which is why the emergency button on "
              "this screen is yours and the one on a scanned code is not.",
         screens=(27,),
         try_it="Read the ladder, then look at where the ceiling sits."),
    dict(key="held", chapter="What is yours", title="What's held about you",
         what="Four questions on one screen: is it sealed, is anybody's "
              "reading of it being written down, what sources may it look at, "
              "and what does your plan actually buy. The access log answers "
              "the second one first and deliberately — on a deployment with "
              "no vault the list of readers is empty because nothing is "
              "recorded, not because nobody looked, and those are opposite "
              "facts. Consent for a source is enforced rather than asked: "
              "giving JIM context from a source you have not allowed is "
              "refused by the server, not politely skipped.",
         screens=(26,),
         try_it="Read the access log, then allow a source and give it context."),
    dict(key="bearing", chapter="What is yours", title="Bearing",
         what="Three things kept apart on purpose. What you set — language, "
              "tone, sensitivity, the voice. What you told it — conditions, "
              "context, consented sources. And what it made of that: the "
              "insights it wrote, the events it logged, the follow-ups it "
              "asked that you have not answered. The third is the half of a "
              "guardian product easiest to leave out, because nobody "
              "complains about not being shown what a thing thinks of them. "
              "The guide and the corner dock live here too — a walkthrough "
              "whose own job is explaining the app had no door of its own "
              "until this screen.",
         screens=(29,),
         try_it="Read what JIM has written about you, then set the tone."),
    dict(key="safety", chapter="When it matters", title="Answering an alarm",
         what="The safety screen runs in the order of who is pressing. Get "
              "help now leads — your own one press, reaching your emergency "
              "contact, your Medical ID, first aid and every connected "
              "device, and saying plainly that JIM cannot dial 911 itself. "
              "Below it, the automatic path: the crash watch's status, and "
              "where to arm it while you are fine. Beacons come after, "
              "named for what they are — the bystander's path, for somebody "
              "who finds you. Then the answering end, and every way help "
              "gets summoned lands in it: a scanned beacon, and the crash "
              "watch's own trip, standing first in the queue until somebody "
              "says they are going. Accepting an alarm "
              "names a responder, because 'someone is coming' is a person "
              "and not a state; escalating is one press with no modal in "
              "the way; clearing is the direction that asks, because "
              "clearing is the irreversible one. What paged out and what "
              "was recorded sit below the fold, history under the urgent.",
         screens=(31,),
         try_it="Read what Get help now will do before you need it."),
    dict(key="engaged", chapter="Being looked after",
         title="Leaving it engaged",
         what="The coach answers one turn at a time. An engaged session is "
              "the other thing: you open it and it stays open — through "
              "closing the app, through tomorrow — until you sign off. While "
              "it is open it can do things rather than describe them: write "
              "in your journal, set you a goal, move one along, tick off a "
              "habit, book something, change how it talks to you. What it "
              "may touch is a written list you can read before you open one, "
              "and nothing on it raises an alarm, moves money, or ends "
              "anything — those doors are not on the list at all. Everything "
              "it changes lands on a trail with the way back beside it, so "
              "you can take any of it back afterwards. One thing cannot be "
              "taken back and says so: putting your question to a specialist "
              "outside JIM, because nothing here can unsay what somebody "
              "else has read. Signing off is a handover, not a close — what "
              "the session was about goes to the offline coach, and anything "
              "you name on the way out becomes something the Guardian keeps "
              "an eye on and raises unprompted while you are away.",
         screens=(38,),
         try_it="Open Engaged and read the list of what it can touch before "
                "you press Engage."),
    dict(key="talk", chapter="Finding your way",
         title="Saying it instead of finding it",
         what="This app has two dozen screens, and for a long time the only "
              "way to reach one was to know which tile it was behind. The "
              "front door replaces that: a box at the bottom you can type "
              "into from anywhere, and above it a row of features that "
              "scrolls sideways — get help now, speak, camera, check in, "
              "medicines, monitor, care team, permissions, journal, what is "
              "held. Pressing one opens the same screen the tile opened; the "
              "row is a way in, not a second copy of anything, so what you "
              "find there behaves exactly as it did before. The plus beside "
              "the box carries the three things that have somewhere to go "
              "today — camera, photos and voice — and stays short on "
              "purpose, because a button that does nothing is worse than a "
              "short menu.",
         screens=(39,),
         try_it="Type a question into the box at the bottom, then swipe the "
                "row above it to see everything it reaches."),
    dict(key="studio", chapter="Finding your way",
         title="Writing your own tool",
         what="Widgets are small programs you write for yourself. You give "
              "one a name and some code, hand it whatever it needs, and read "
              "what it answers — and nothing you write can reach anybody "
              "else. That is not a promise, it is how the thing is built: a "
              "widget runs with the network cut off, with nothing on the "
              "disk it can see except its own folder, with no way to start "
              "another program, and with a few seconds and a little memory "
              "before it is stopped. If the machine this app is installed on "
              "cannot build all four of those walls, nothing runs at all — "
              "the screen says which wall is missing, the run button is not "
              "there, and you can still write and keep your widgets. The "
              "limits shown at the bottom are read from the thing that "
              "enforces them, so what you see is what you get.",
         screens=(40,),
         try_it="Open Widgets, press New, and run the example that greets "
                "you by name."),
    dict(key="watchfaces", chapter="Every day", title="The watch on the wrist",
         what="Any watch, phone or frame that can open jim-mini.com/#watch "
              "is the wrist: all thirty-six faces are working screens on the "
              "same doors the phone uses, so a check-in logged on the wrist "
              "is the Check-in tab's own record. Swipe between faces, or open "
              "one directly with #watch and its name. The CPR face keeps its "
              "own time — 110 compressions a minute on the device's audio "
              "clock, in the 30:2 rhythm — and needs no account and no "
              "network. The emergency face hands the number to the device, "
              "which is the thing that can place a call; JIM never claims a "
              "call it did not make.",
         screens=(41,),
         try_it="Open jim-mini.com/#watch/heart and swipe to the faces on "
                "either side."),
)

CHAPTERS = tuple(dict.fromkeys(le["chapter"] for le in LESSONS))
MODES = ("text", "voice")


class TutorialError(ValueError):
    """A step that does not exist. Text meant for a person."""


def _index(key: str) -> int:
    for i, le in enumerate(LESSONS):
        if le["key"] == key:
            return i
    raise TutorialError(i18n.fill(i18n.NO_SUCH_STEP, got=repr(key)))


def say(lesson: dict, mode: str = "text") -> dict:
    """One lesson, for reading or for listening.

    Voice matters more here than in QRME: this is a product used hands-free,
    often by somebody who is not well, and a spoken screen number is noise.
    """
    if mode not in MODES:
        raise TutorialError(i18n.fill(i18n.UNKNOWN_MODE_ONE_OF, got=repr(mode),
                                      choices=", ".join(MODES)))
    out = {"key": lesson["key"], "chapter": lesson["chapter"],
           "title": lesson["title"], "try_it": lesson["try_it"], "mode": mode}
    if mode == "voice":
        out["speak"] = f"{lesson['title']}. {lesson['what']} {lesson['try_it']}"
        out["screens"] = []
    else:
        out["what"] = lesson["what"]
        out["screens"] = list(lesson["screens"])
    return out


def outline(mode: str = "text") -> dict:
    return {
        "guide": GUIDE,
        "chapters": [{"chapter": c,
                      "lessons": [say(le, mode) for le in LESSONS
                                if le["chapter"] == c]} for c in CHAPTERS],
        "lessons_count": len(LESSONS),
    }


def _done(learner_id: str) -> set[str]:
    rows = db.connect().execute(
        "SELECT lesson FROM tutorial_progress WHERE learner_id=?",
        (learner_id,)).fetchall()
    return {r["lesson"] for r in rows}


def where(learner_id: str, mode: str = "text") -> dict:
    done = _done(learner_id)
    remaining = [le for le in LESSONS if le["key"] not in done]
    return {
        "learner_id": learner_id, "guide": GUIDE,
        "next_lesson": None if not remaining else say(remaining[0], mode),
        "done": len(done), "total": len(LESSONS), "finished": not remaining,
        "note": ("that is all of it — ask the Guardian for any part again"
                 if not remaining else
                 f"step {len(done) + 1} of {len(LESSONS)}"),
    }


def start(learner_id: str, mode: str = "text") -> dict:
    conn = db.connect()
    conn.execute("DELETE FROM tutorial_progress WHERE learner_id=?",
                 (learner_id,))
    conn.commit()
    return where(learner_id, mode)


def mark(learner_id: str, key: str, mode: str = "text") -> dict:
    _index(key)
    conn = db.connect()
    conn.execute(
        "INSERT INTO tutorial_progress (learner_id, lesson, done_at)"
        " VALUES (?,?,?) ON CONFLICT (learner_id, lesson) DO NOTHING",
        (learner_id, key, db.utcnow()))
    conn.commit()
    return where(learner_id, mode)


def step(key: str, mode: str = "text") -> dict:
    return say(LESSONS[_index(key)], mode)


def for_screen(number: int, mode: str = "text") -> dict | None:
    for lesson in LESSONS:
        if number in lesson["screens"]:
            return say(lesson, mode)
    return None
