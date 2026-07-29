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
