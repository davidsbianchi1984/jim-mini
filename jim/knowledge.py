"""The offline knowledge pack — what the assistant knows before any API key.

The field ask, verbatim: "develop a knowledge pack for the assistant/guide
until we can get JIM-mini up and running with an API key … preloaded with
all kinds of biometric-sensor-related remedies for any known conditions
covering those six industries, so it's well informed enough to answer most
questions offline."

So: a curated, deterministic reference the coach consults when the model
answering is the offline stub. Every entry is hand-written, carries its
references, and stays on the guidance side of the line the whole product
draws — remedies a layperson can apply, never a diagnosis or a dose. When a
real model is configured it answers instead, with all of its nuance; this
pack is the floor, not the ceiling.

Matching is transparent: lowercase keyword hits, the asked area worth a
nudge, highest score wins, and below the threshold the pack stays silent so
the stub's honest "I'm a stub" text shows rather than a wrong-topic answer.
"""

from __future__ import annotations

# The six areas of the practice, plus the sensor-borne conditions the
# Guardian already knows how to detect.
ENTRIES: list[dict] = [
    # -- biometric-sensor remedies -------------------------------------------
    {"topic": "resting heart rate running high",
     "area": "health_fitness",
     "keywords": ["heart rate", "pulse", "bpm", "racing", "tachy",
                  "heart pounding"],
     "guidance": "A resting pulse that runs above your own baseline for days "
                 "is worth attention before alarm: check sleep, caffeine, "
                 "alcohol, dehydration and any new stress first — each can "
                 "add 5–15 bpm on its own. Rehydrate, cut caffeine after "
                 "noon, and re-measure seated after five quiet minutes. If "
                 "it stays elevated for a week, or comes with chest pain, "
                 "breathlessness or fainting, that is a clinician's question "
                 "— bring the watch data with you, it helps.",
     "references": ["AHA: all-about-heart-rate", "CDC: heart-disease basics"]},
    {"topic": "blood oxygen reading low",
     "area": "health_fitness",
     "keywords": ["blood oxygen", "spo2", "oxygen", "shallow breathing",
                  "short of breath", "breathless"],
     "guidance": "First, trust but verify the sensor: cold fingers, nail "
                 "polish and a loose watch all fake low SpO2 — warm the "
                 "hand, sit still, re-read. A genuine reading under 92%, or "
                 "shallow breathing that doesn't ease: move to fresh air (a "
                 "window open wide counts), sit upright, breathe slowly and "
                 "deeply, and have someone call emergency services while "
                 "you keep at it — the companion relays your readings in "
                 "the background so responders arrive briefed.",
     "references": ["WHO: pulse-oximetry training manual",
                    "NHS: shortness-of-breath guidance"]},
    {"topic": "heart-rate variability dropping",
     "area": "health_fitness",
     "keywords": ["hrv", "variability", "recovery"],
     "guidance": "Falling HRV across days usually reads 'under-recovered': "
                 "the classics are late meals, alcohol, illness brewing, "
                 "overtraining and unprocessed stress. Pick the easy lever "
                 "first — a consistent bedtime for three nights — and watch "
                 "the trend, not any single morning. Box breathing before "
                 "bed measurably helps most people's overnight HRV.",
     "references": ["NIH/PMC: HRV and stress review"]},
    {"topic": "fever or elevated body temperature",
     "area": "health_fitness",
     "keywords": ["temperature", "fever", "hot", "chills"],
     "guidance": "For an adult: fluids, rest, light clothing, and measure "
                 "again in an hour — a wearable's skin temperature runs "
                 "under a true core reading. Seek care the same day for "
                 "103°F/39.4°C or higher, a stiff neck, confusion, a rash, "
                 "or any fever past three days. For infants and the "
                 "immunocompromised the threshold is immediate, not "
                 "same-day.",
     "references": ["CDC: fever management", "AAP: fever in children"]},
    {"topic": "blood pressure reading high",
     "area": "health_fitness",
     "keywords": ["blood pressure", "bp", "hypertension", "systolic"],
     "guidance": "One high cuff reading is weather, a pattern is climate: "
                 "re-measure seated, back supported, arm at heart level, "
                 "after five quiet minutes and no caffeine for half an "
                 "hour. Above 180/120 with chest pain, weakness or vision "
                 "change is emergency-now territory. A steady pattern above "
                 "130/80 belongs in front of a clinician with your log — "
                 "salt, sleep, movement and alcohol are the levers they'll "
                 "start with.",
     "references": ["AHA: blood-pressure categories"]},
    {"topic": "sleep running short",
     "area": "health_fitness",
     "keywords": ["sleep", "insomnia", "tired", "can't sleep", "awake"],
     "guidance": "Protect the same wake time seven days a week — the wake "
                 "anchor does more than any bedtime rule. Keep the last "
                 "hour dim and screen-light, the room cool, caffeine before "
                 "noon, and if you're awake past twenty minutes, get up and "
                 "do something dull in low light rather than negotiating "
                 "with the ceiling. Three bad weeks despite this is worth a "
                 "clinician conversation about insomnia care that works "
                 "(CBT-I outperforms pills long-term).",
     "references": ["AASM: healthy sleep habits", "NIH: CBT-I overview"]},
    {"topic": "panic attack riding a racing pulse",
     "area": "mental_health",
     "keywords": ["panic", "panic attack", "hyperventilat", "racing",
                  "can't breathe", "doom"],
     "guidance": "A panic attack is a false alarm with a real physiology, "
                 "and it always passes — usually inside twenty minutes. "
                 "Lengthen the exhale (in for four, out for eight), drop "
                 "your shoulders, name five things you can see. Don't flee "
                 "the place if you can stand to stay; leaving teaches the "
                 "alarm it was right. If attacks recur, panic disorder "
                 "responds very well to treatment — that's a professional "
                 "conversation worth having early.",
     "references": ["APA: panic disorder", "NHS: panic attack self-help"]},
    {"topic": "anxiety running high",
     "area": "mental_health",
     "keywords": ["anxiety", "anxious", "worry", "on edge", "stress"],
     "guidance": "Anxiety shrinks when scheduled: give the worries a "
                 "fifteen-minute daily appointment on paper, and outside it "
                 "practice returning attention to the task at hand. Slow "
                 "breathing (the Wellness tab's protocols), daily movement, "
                 "and less caffeine are the three levers with the best "
                 "evidence a layperson can pull today. Persistent anxiety "
                 "that crowds work or sleep deserves professional care — "
                 "it is among the most treatable conditions there is.",
     "references": ["WHO: anxiety fact sheet", "NICE: GAD pathway"]},
    {"topic": "low mood that lingers",
     "area": "mental_health",
     "keywords": ["depress", "low mood", "hopeless", "no energy",
                  "nothing matters"],
     "guidance": "Depression lies about what will help, so borrow the "
                 "evidence: daily light (morning walk beats midday), "
                 "scheduled contact with one person, one small completed "
                 "task, and a fixed wake time — behavioral activation "
                 "works before motivation returns, not after. Two weeks of "
                 "most-days low mood is the clinical line: bring it to a "
                 "professional. If any thought of self-harm arrives, use "
                 "the crisis line (988 in the US) now — that is what it is "
                 "for.",
     "references": ["NIMH: depression basics", "988 Suicide & Crisis Lifeline"]},
    {"topic": "facing a phobia",
     "area": "mental_health",
     "keywords": ["phobia", "afraid of", "terrified", "avoid"],
     "guidance": "Avoidance feeds a phobia; graded exposure starves it. "
                 "Build a ladder from 'can barely think about it' to 'the "
                 "real thing', climb one comfortable-ish rung at a time, "
                 "and stay on each rung until the fear drops by half before "
                 "moving. This is the rare condition where self-guided "
                 "work genuinely moves the needle — and where a few "
                 "sessions of professional exposure therapy often finishes "
                 "the job.",
     "references": ["APA: specific phobias", "NHS: phobias self-help"]},
    # -- the remaining industries --------------------------------------------
    {"topic": "eating better without a diet",
     "area": "nutrition",
     "keywords": ["eat", "diet", "meal", "nutrition", "weight", "protein",
                  "hungry"],
     "guidance": "Skip the named diets and pull the boring levers: protein "
                 "and plants at every meal, water before snacks, and a "
                 "kitchen that only stocks what you want to be eating — "
                 "environment beats willpower every week. The Wellness "
                 "tab builds a concrete day of meals around your goal and "
                 "preferences; a registered dietitian outranks all of it "
                 "when a diagnosis is in the picture.",
     "references": ["USDA: dietary guidelines", "AND: find a dietitian"]},
    {"topic": "money stress and the plan",
     "area": "finance",
     "keywords": ["money", "budget", "debt", "spending", "afford", "bills",
                  "savings"],
     "guidance": "Money stress shrinks when the numbers stop being vague: "
                 "set a monthly plan in Budgets (per category and overall) "
                 "and let spending report against it — the app speaks up "
                 "at 80% with days left, which is when a plan can still be "
                 "saved. For debt, list balances and rates once, pay "
                 "minimums everywhere plus everything spare at either the "
                 "smallest balance (momentum) or highest rate (math) — "
                 "both work, the one you'll stick to works best. Nonprofit "
                 "credit counseling is free and legitimate (NFCC).",
     "references": ["CFPB: dealing-with-debt", "NFCC: credit counseling"]},
    {"topic": "career stuck or burning out",
     "area": "career",
     "keywords": ["job", "career", "burnout", "boss", "work", "interview",
                  "promotion"],
     "guidance": "Burnout has three faces — exhaustion, cynicism, and "
                 "feeling ineffective — and recovery starts with subtraction "
                 "(one commitment down, real breaks, a hard stop time) "
                 "before any addition. For being stuck: interview two "
                 "people who hold the job you think you want before "
                 "changing anything big. The coach can rehearse the hard "
                 "conversation with you; scheduling it is yours.",
     "references": ["WHO: burnout classification"]},
    {"topic": "a relationship under strain",
     "area": "relationships",
     "keywords": ["relationship", "partner", "argument", "marriage",
                  "lonely", "friend", "family fight"],
     "guidance": "The evidence on repair is unglamorous: raise issues "
                 "softly (complaint about the thing, never the person's "
                 "character), take breaks when flooded — twenty minutes "
                 "minimum, pulse back under 100 — and aim for five kind "
                 "moments for every hard one. Loneliness responds to "
                 "scheduled contact, not spontaneous intention. If contempt "
                 "has moved in, couples work with a professional earns its "
                 "cost.",
     "references": ["Gottman Institute research summaries"]},
    {"topic": "carbon monoxide or bad air",
     "area": "health_fitness",
     "keywords": ["carbon monoxide", "co alarm", "smoke", "fumes", "air",
                  "headache dizzy nausea together"],
     "guidance": "Headache + dizziness + nausea together indoors is CO "
                 "until proven otherwise: get everyone outside now, leave "
                 "the door open behind you, count heads, and call emergency "
                 "services from the fresh air — not from inside. Don't "
                 "re-enter to open windows. The fix is a CO alarm on every "
                 "sleeping floor; they cost less than one urgent-care "
                 "visit.",
     "references": ["CDC: carbon monoxide poisoning"]},
    # -- health & fitness, deeper shelf --------------------------------------
    {"topic": "starting to exercise from zero",
     "area": "health_fitness",
     "keywords": ["start exercising", "get in shape", "couch", "sedentary",
                  "out of shape", "beginner workout"],
     "guidance": "The dose that changes lives is smaller than people think: "
                 "brisk walking thirty minutes most days meets the guideline "
                 "that moves mortality curves. Start at ten minutes if "
                 "thirty sounds like a wall, add five a week, and put it at "
                 "the same time daily so it stops being a decision. Add two "
                 "days of simple strength work (squats to a chair, wall "
                 "push-ups, carries) once walking is boring. Soreness is "
                 "normal; joint pain that sharpens is a stop sign.",
     "references": ["WHO: physical activity guidelines",
                    "CDC: physical activity basics"]},
    {"topic": "back pain from sitting",
     "area": "health_fitness",
     "keywords": ["back pain", "backache", "sitting all day", "lower back",
                  "stiff back", "desk job"],
     "guidance": "Most desk-borne back pain is a movement famine, not an "
                 "injury: stand or walk two minutes every half hour, raise "
                 "the screen to eye height, and strengthen what sitting "
                 "weakens — hips and core — with bridges and bird-dogs. "
                 "Heat helps more than rest; bed rest past a day usually "
                 "makes it worse. Pain that runs down a leg, numbness, or "
                 "any bladder change is a clinician's question now, not a "
                 "stretching question.",
     "references": ["NHS: back pain", "ACP: low back pain guideline"]},
    {"topic": "hydration you can feel",
     "area": "health_fitness",
     "keywords": ["dehydrated", "hydration", "drink water", "thirsty",
                  "dry mouth", "dark urine"],
     "guidance": "Urine the color of pale straw is the whole dashboard — "
                 "darker means drink, clear means you can ease off. Front-"
                 "load the day, keep a bottle where your hand already goes, "
                 "and add a pinch more with heat, altitude, alcohol or a "
                 "fever. Headache + fatigue + dark urine together is "
                 "usually yesterday's water arriving late.",
     "references": ["CDC: water and healthier drinks"]},
    {"topic": "screens eating the night",
     "area": "health_fitness",
     "keywords": ["screen time", "doomscroll", "phone at night", "blue light",
                  "scrolling", "late night phone"],
     "guidance": "The phone steals sleep twice — the light delays melatonin "
                 "and the feed delays you. Move the charger out of the "
                 "bedroom, put the last hour behind a boring dim activity, "
                 "and use the device's own downtime scheduler so the "
                 "decision is made once, not nightly. A paper book at the "
                 "same spot each night becomes a sleep cue in about two "
                 "weeks.",
     "references": ["AASM: bedtime screen use", "Sleep Foundation: blue light"]},
    # -- mental health, deeper shelf -----------------------------------------
    {"topic": "grief that has nowhere to go",
     "area": "mental_health",
     "keywords": ["grief", "grieving", "loss", "died", "mourning", "bereaved"],
     "guidance": "Grief is not a problem to solve; it is love with nowhere "
                 "to land, and it comes in waves rather than stages. Let "
                 "the waves come, keep one anchor routine (a walk, a meal "
                 "time), and say the person's name out loud with somebody "
                 "who knew them. Grief that after months still stops eating, "
                 "sleeping or working — or any wish not to be here — "
                 "deserves professional company; that too is normal to "
                 "need.",
     "references": ["CDC: grief and loss", "APA: grief"]},
    {"topic": "anger arriving faster than thought",
     "area": "mental_health",
     "keywords": ["anger", "temper", "rage", "snapped", "irritable",
                  "short fuse"],
     "guidance": "Anger is a fast system; give it a slower lane. Name the "
                 "body's first signal (jaw, heat, fists), take the twenty-"
                 "minute walk *before* the conversation, and come back with "
                 "one sentence that starts with 'I' rather than 'you'. "
                 "Track the triggers for a week — most people find two, "
                 "not twenty. If anger is leaving marks on people or "
                 "property, a professional course works faster than will "
                 "power.",
     "references": ["APA: controlling anger"]},
    {"topic": "focus in a distracted season",
     "area": "mental_health",
     "keywords": ["focus", "concentrate", "distracted", "attention",
                  "procrastinat", "adhd"],
     "guidance": "Attention responds to architecture: one task visible, "
                 "phone in another room, twenty-five minutes on a timer "
                 "and a real break after. Start with the ugliest five "
                 "minutes of the avoided task — starting is the whole "
                 "battle, momentum is cheap after. Chronic, life-long "
                 "distractibility that costs jobs and relationships is "
                 "worth a proper assessment rather than another app.",
     "references": ["APA: multitasking research", "CDC: adult ADHD basics"]},
    {"topic": "burnout versus depression",
     "area": "mental_health",
     "keywords": ["burned out", "burnout", "exhausted", "empty", "drained",
                  "nothing left"],
     "guidance": "Burnout lifts when the load lifts — a real week away, a "
                 "boundary that holds, help that arrives. Depression "
                 "follows you into the time off. Run the experiment "
                 "honestly: subtract load for two weeks and watch. If rest "
                 "restores you, the fix is structural; if it doesn't, treat "
                 "it as mood and bring a professional in. Both are common, "
                 "neither is weakness, and the treatments differ — which "
                 "is why the distinction earns its own entry.",
     "references": ["WHO: burnout classification", "NIMH: depression basics"]},
    # -- nutrition, deeper shelf ---------------------------------------------
    {"topic": "protein without the powder aisle",
     "area": "nutrition",
     "keywords": ["protein", "protein shake", "muscle food", "amino",
                  "how much protein"],
     "guidance": "Most adults do fine around 0.7–1g per pound of goal "
                 "weight spread over the day — eggs, dairy, beans, fish, "
                 "chicken and tofu get there without a single scoop. Put "
                 "protein first at breakfast (it steadies appetite all "
                 "day), and treat powder as a convenience, not a "
                 "requirement. Kidney disease changes this math — that's "
                 "a dietitian's call, not a forum's.",
     "references": ["NIH: protein fact sheets", "AND: protein and health"]},
    {"topic": "sugar that hides in plain sight",
     "area": "nutrition",
     "keywords": ["sugar", "sweet tooth", "soda", "cravings", "cutting sugar"],
     "guidance": "The big wins are liquid: swapping sweet drinks for water "
                 "or unsweetened anything removes more added sugar than "
                 "any dessert rule. Read labels for the -ose family in the "
                 "first three ingredients, keep fruit where snacks used to "
                 "live, and let cravings crest — they pass in about "
                 "fifteen minutes whether or not you feed them. Total "
                 "bans backfire; small portions on purpose beat large "
                 "portions by accident.",
     "references": ["AHA: added sugars", "CDC: rethink your drink"]},
    {"topic": "feeding a family on a budget",
     "area": "nutrition",
     "keywords": ["cheap meals", "grocery budget", "meal prep", "food budget",
                  "eating cheap", "groceries expensive"],
     "guidance": "Beans, lentils, eggs, oats, rice, frozen vegetables and "
                 "whatever fruit is in season outperform most of the "
                 "middle aisles per dollar and per nutrient. Cook once, "
                 "eat twice: double the pot, freeze half. Shop with a "
                 "list built from three planned dinners, and let the "
                 "store's own brand win ties. Frozen produce is picked "
                 "riper than much of the fresh shelf — it is not the "
                 "compromise it looks like.",
     "references": ["USDA: MyPlate on a budget", "SNAP-Ed recipe resources"]},
    {"topic": "eating for steady energy",
     "area": "nutrition",
     "keywords": ["energy crash", "afternoon slump", "blood sugar", "sleepy "
                  "after lunch", "carb crash"],
     "guidance": "The slump is usually the meal before it: refined carbs "
                 "alone spike and drop. Pair carbs with protein or fat "
                 "(apple + peanut butter beats apple alone), keep lunch a "
                 "plate rather than a bag, and take ten minutes of "
                 "daylight after eating — the walk does more than the "
                 "espresso. Caffeine after 2pm borrows tonight's energy "
                 "for this afternoon.",
     "references": ["Harvard T.H. Chan: carbohydrates and blood sugar"]},
    # -- career, deeper shelf ------------------------------------------------
    {"topic": "the resume that gets read",
     "area": "career",
     "keywords": ["resume", "cv", "cover letter", "applying", "job search",
                  "applications"],
     "guidance": "One page, newest first, every bullet an outcome with a "
                 "number where one exists ('cut onboarding from 3 weeks "
                 "to 4 days') rather than a duty. Mirror the posting's "
                 "own words — software and humans both scan for them. "
                 "Tailoring the top third per application beats sending "
                 "fifty identical ones; referrals beat both, so tell "
                 "people you're looking. The coach can rehearse your "
                 "walkthrough of it.",
     "references": ["DOL CareerOneStop: resumes"]},
    {"topic": "negotiating an offer without losing it",
     "area": "career",
     "keywords": ["negotiate", "salary", "raise", "offer", "counteroffer",
                  "pay"],
     "guidance": "Companies expect the ask; almost nobody rescinds over a "
                 "respectful one. Research the band first, let them name "
                 "the number when possible, then ask above your target "
                 "with one sentence of evidence and stop talking. "
                 "Everything is negotiable once: start date, remote days, "
                 "review timing, vacation. Practice the ask out loud "
                 "twice — the wobble lives in the first two attempts.",
     "references": ["DOL: occupational wage data (OEWS)"]},
    {"topic": "the interview as a rehearsable skill",
     "area": "career",
     "keywords": ["interview", "interviewing", "behavioral questions",
                  "tell me about yourself"],
     "guidance": "Interviews reward preparation over charisma: prepare six "
                 "stories in situation-action-result shape and you can "
                 "answer eighty percent of behavioral questions. Research "
                 "the team enough to ask two questions that couldn't be "
                 "asked of any other company. Rehearse out loud, once "
                 "with a person; thinking it through silently is not the "
                 "same sport. Send the thank-you the same day.",
     "references": ["DOL CareerOneStop: interview tips"]},
    {"topic": "learning a skill beside a full-time life",
     "area": "career",
     "keywords": ["upskill", "learn to code", "certification", "new skill",
                  "career change", "reskill"],
     "guidance": "Twenty focused minutes daily beats three ambitious hours "
                 "on Sunday — attach it to an anchor (after coffee, "
                 "before mail) and keep a visible streak. Pick projects "
                 "over courses as soon as possible: a small real thing "
                 "you finished teaches and *proves* more than a "
                 "certificate row. Tell someone the deadline; accountability "
                 "is a feature, not a weakness.",
     "references": ["DOL: apprenticeship and reskilling resources"]},
    # -- finance, deeper shelf -----------------------------------------------
    {"topic": "the emergency fund that ends emergencies",
     "area": "finance",
     "keywords": ["emergency fund", "rainy day", "unexpected expense",
                  "no savings", "broke when"],
     "guidance": "An emergency fund converts crises into inconveniences. "
                 "First target: one month of essentials, autopiloted — a "
                 "transfer on payday you never see, sized so you don't "
                 "feel it, raised when you stop noticing. Keep it in a "
                 "separate high-yield savings account with no card "
                 "attached; friction is the point. Three to six months is "
                 "the destination, one month already changes how "
                 "emergencies feel.",
     "references": ["CFPB: essential guide to building an emergency fund"]},
    {"topic": "credit score mechanics without the myths",
     "area": "finance",
     "keywords": ["credit score", "credit report", "fico", "credit card debt",
                  "utilization"],
     "guidance": "Two levers dominate: pay every bill on time (autopay the "
                 "minimum as a floor) and keep card balances under about "
                 "30% of their limits — under 10% is better. Don't close "
                 "old cards before a big application; age helps. Check "
                 "all three reports free at annualcreditreport.com and "
                 "dispute errors — they're common. Credit repair "
                 "companies can't do anything you can't do free.",
     "references": ["CFPB: credit reports and scores",
                    "FTC: free credit reports"]},
    {"topic": "starting to invest without a finance degree",
     "area": "finance",
     "keywords": ["invest", "investing", "retirement", "401k", "index fund",
                  "compound"],
     "guidance": "The boring answer wins: capture any employer match first "
                 "(it is a 50–100% instant return), then automate a fixed "
                 "amount into a broad low-cost index fund and stop "
                 "watching it. Time in the market beats timing it; fees "
                 "compound against you exactly like returns compound for "
                 "you. Anyone promising guaranteed returns is selling "
                 "risk with the label peeled off. For decisions with "
                 "real stakes, a fee-only fiduciary advisor — the word "
                 "'fiduciary' does the work.",
     "references": ["SEC: investor.gov basics", "CFPB: saving for retirement"]},
    {"topic": "a scam has your details or your money",
     "area": "finance",
     "keywords": ["scam", "scammed", "fraud", "phishing", "identity theft",
                  "gift cards"],
     "guidance": "Act in this order: stop contact, screenshot everything, "
                 "call the bank or card issuer now (reversals are "
                 "time-boxed), change the password anywhere it was "
                 "reused, and freeze credit at all three bureaus — it's "
                 "free and takes minutes. Report at reportfraud.ftc.gov "
                 "and identitytheft.gov for a recovery plan. Anyone who "
                 "demands payment by gift card is a scam by definition, "
                 "no exceptions. Shame keeps people silent; these "
                 "operations are industrial and the reporting helps the "
                 "next person.",
     "references": ["FTC: what to do if you were scammed",
                    "IdentityTheft.gov"]},
    # -- relationships, deeper shelf -----------------------------------------
    {"topic": "a hard conversation you keep postponing",
     "area": "relationships",
     "keywords": ["hard conversation", "confront", "bring it up", "avoid "
                  "talking", "difficult talk"],
     "guidance": "Open soft and specific: 'I felt X when Y happened, and I "
                 "need Z' survives contact with a defensive listener far "
                 "better than a case file of grievances. Pick a calm "
                 "moment you scheduled, not the heat of the next "
                 "incident; lead with what you want going forward, not "
                 "an audit of the past. One issue per conversation. "
                 "Rehearse the first sentence out loud — it is the only "
                 "one you can control.",
     "references": ["Gottman Institute: softened startup"]},
    {"topic": "loneliness as a solvable logistics problem",
     "area": "relationships",
     "keywords": ["lonely", "no friends", "isolated", "meet people",
                  "make friends"],
     "guidance": "Adult friendship runs on repetition + vulnerability, and "
                 "repetition can be engineered: join something weekly "
                 "(class, league, volunteering) and attend six times "
                 "before judging it. Move one 'we should hang out' to a "
                 "date on the calendar within 48 hours. Reaching out "
                 "first feels riskier than it is — research keeps "
                 "finding people underestimate how glad others are to "
                 "hear from them.",
     "references": ["US Surgeon General: loneliness advisory"]},
    {"topic": "setting a boundary that actually holds",
     "area": "relationships",
     "keywords": ["boundary", "boundaries", "say no", "people pleaser",
                  "taken advantage"],
     "guidance": "A boundary is a statement about what *you* will do, not "
                 "a rule for them: 'I'm leaving events at nine' holds "
                 "without anyone's permission. Say it once, kindly, "
                 "without a courtroom of justifications; expect a "
                 "pushback wave and let it pass like weather. Guilt "
                 "after saying no is a sign the boundary was needed, "
                 "not that it was wrong.",
     "references": ["APA: healthy boundaries"]},
    {"topic": "co-parenting through friction",
     "area": "relationships",
     "keywords": ["co-parent", "coparent", "custody", "ex", "divorce kids",
                  "parenting plan"],
     "guidance": "The evidence is blunt: children do well in both "
                 "arrangements and badly in conflict, so protect them "
                 "from the friction rather than the schedule. Keep "
                 "handoffs businesslike, never message through the "
                 "child, and move logistics into a written plan or a "
                 "co-parenting app so memory stops being a battlefield. "
                 "Speak of the other parent neutrally where small ears "
                 "are — they are half them, and they know it.",
     "references": ["AAP: co-parenting guidance"]},
]

# Below this score the pack stays silent and the stub's honest fallback
# shows instead — a wrong-topic answer is worse than a plain one.
_THRESHOLD = 2


def search(message: str, area: str | None = None) -> dict | None:
    """The best entry for this question, or None. Transparent scoring:
    +2 per keyword hit, +1 when the asked area matches."""
    text = (message or "").lower()
    best, best_score = None, 0
    for entry in ENTRIES:
        score = sum(2 for k in entry["keywords"] if k in text)
        if area and entry["area"] == area:
            score += 1
        if score > best_score:
            best, best_score = entry, score
    if best is None or best_score < _THRESHOLD:
        return None
    return best


def catalog() -> dict:
    """What the pack covers, for the docs and the curious."""
    areas: dict[str, list[str]] = {}
    for e in ENTRIES:
        areas.setdefault(e["area"], []).append(e["topic"])
    return {"entries": len(ENTRIES), "areas": areas,
            "posture": "curated, deterministic, referenced — the floor "
                       "under the coach when no model key is configured, "
                       "never a diagnosis or a dose"}
