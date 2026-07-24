"""Standalone guidance generation + a minimal safety check.

Used when JIM-mini is not delegating to a QRME specialist (i.e. no tandem
specialist is registered for the condition). Keeps JIM fully functional on its
own.
"""

from __future__ import annotations

import re

from . import conditions, llm

_SYSTEM = (
    "You are JIM-mini, a calm, evidence-based personal guidance companion. "
    "You support mental, physical, and life well-being. Be warm, concrete, and "
    "brief. Tailor guidance to the user's age and maturity. Never diagnose; if "
    "the user may be in danger, urge them to seek immediate help.\n"
    "condition: {label}\n"
    "monitored situation: {situation}"
)

_FIRST_AID = (
    "\nThis is a physical injury: walk the user through appropriate first-aid "
    "steps one at a time, and say clearly when emergency services are needed."
)

# The factual basis offered alongside counseling, per condition domain.
REFERENCES: dict[str, list[str]] = {
    conditions.ANXIETY: ["NHS: 4-7-8 breathing technique",
                         "APA: grounding techniques for panic"],
    conditions.DEPRESSION: ["WHO: depression self-care basics",
                            "988 Suicide & Crisis Lifeline (US)"],
    conditions.STRESS: ["WHO: stress management guide",
                        "APA: healthy coping strategies"],
    conditions.PHOBIA: ["NHS: gradual-exposure self-help for phobias"],
    conditions.FINANCIAL_STRESS: ["CFPB: dealing-with-debt resources"],
    conditions.RELATIONSHIP: ["APA: healthy communication in relationships"],
    conditions.PHYSICAL_DISTRESS: ["Red Cross: when to call emergency services"],
    conditions.PHYSICAL_INJURY: ["Red Cross: first-aid steps",
                                 "Mayo Clinic: first-aid basics"],
    conditions.CARDIAC: ["AHA: hands-only CPR",
                         "Red Cross: how to use an AED"],
    conditions.ENVIRONMENT: ["CDC: carbon monoxide safety",
                             "Red Cross: fire & smoke safety"],
    conditions.ERGONOMIC: ["OSHA: ergonomics — risk factors and prevention"],
}

# The verifiable basis behind each reference: who published it, where to read
# it, and which part of the advice it supports. This travels with every
# guidance response so advice is checkable at the source, not taken on faith.
EVIDENCE: dict[str, list[dict]] = {
    conditions.ANXIETY: [
        {"publisher": "NHS (UK National Health Service)",
         "title": "Breathing exercises for stress",
         "url": "https://www.nhs.uk/mental-health/self-help/guides-tools-and-activities/breathing-exercises-for-stress/",
         "supports": "paced-breathing techniques for acute anxiety"},
        {"publisher": "American Psychological Association",
         "title": "Panic disorder & grounding",
         "url": "https://www.apa.org/topics/anxiety",
         "supports": "grounding techniques during panic"},
    ],
    conditions.DEPRESSION: [
        {"publisher": "World Health Organization",
         "title": "Depression fact sheet & self-care",
         "url": "https://www.who.int/news-room/fact-sheets/detail/depression",
         "supports": "self-care basics and when to seek help"},
        {"publisher": "988 Suicide & Crisis Lifeline",
         "title": "24/7 crisis support (US)",
         "url": "https://988lifeline.org",
         "supports": "immediate human crisis support"},
    ],
    conditions.STRESS: [
        {"publisher": "World Health Organization",
         "title": "Stress — questions and answers",
         "url": "https://www.who.int/news-room/questions-and-answers/item/stress",
         "supports": "stress management guidance"},
        {"publisher": "American Psychological Association",
         "title": "Healthy ways to handle life's stressors",
         "url": "https://www.apa.org/topics/stress",
         "supports": "healthy coping strategies"},
    ],
    conditions.PHOBIA: [
        {"publisher": "NHS (UK National Health Service)",
         "title": "Phobias — self-help",
         "url": "https://www.nhs.uk/mental-health/conditions/phobias/",
         "supports": "gradual-exposure self-help"},
    ],
    conditions.FINANCIAL_STRESS: [
        {"publisher": "Consumer Financial Protection Bureau",
         "title": "Dealing with debt",
         "url": "https://www.consumerfinance.gov/consumer-tools/debt-collection/",
         "supports": "debt and financial-hardship resources"},
    ],
    conditions.RELATIONSHIP: [
        {"publisher": "American Psychological Association",
         "title": "Marriage & relationships",
         "url": "https://www.apa.org/topics/marriage-relationships",
         "supports": "healthy communication guidance"},
    ],
    conditions.PHYSICAL_DISTRESS: [
        {"publisher": "American Red Cross",
         "title": "First aid — when to call emergency services",
         "url": "https://www.redcross.org/take-a-class/first-aid/performing-first-aid/first-aid-steps",
         "supports": "recognizing emergencies and calling for help"},
    ],
    conditions.PHYSICAL_INJURY: [
        {"publisher": "American Red Cross",
         "title": "First aid steps",
         "url": "https://www.redcross.org/take-a-class/first-aid/performing-first-aid/first-aid-steps",
         "supports": "step-by-step first aid"},
        {"publisher": "Mayo Clinic",
         "title": "First aid basics",
         "url": "https://www.mayoclinic.org/first-aid",
         "supports": "condition-specific first-aid detail"},
    ],
    conditions.CARDIAC: [
        {"publisher": "American Heart Association",
         "title": "Hands-Only CPR",
         "url": "https://cpr.heart.org/en/cpr-courses-and-kits/hands-only-cpr",
         "supports": "compression rate (100–120/min), depth, and full chest "
                     "recoil — the source of the playbook's 110/min pace"},
        {"publisher": "American Red Cross",
         "title": "How to use an AED",
         "url": "https://www.redcross.org/take-a-class/aed/using-an-aed/aed-steps",
         "supports": "AED pad placement, stand-clear analysis, and shock "
                     "only when the device advises"},
    ],
    conditions.ENVIRONMENT: [
        {"publisher": "US Centers for Disease Control and Prevention",
         "title": "Carbon monoxide poisoning",
         "url": "https://www.cdc.gov/carbon-monoxide/",
         "supports": "CO exposure response — fresh air, evacuation"},
        {"publisher": "American Red Cross",
         "title": "Home fire safety",
         "url": "https://www.redcross.org/get-help/how-to-prepare-for-emergencies/types-of-emergencies/fire.html",
         "supports": "fire and smoke response"},
    ],
    conditions.ERGONOMIC: [
        {"publisher": "US Occupational Safety and Health Administration",
         "title": "Ergonomics",
         "url": "https://www.osha.gov/ergonomics",
         "supports": "risk factors and prevention for strain injuries"},
    ],
}

# --------------------------------------------------------------------------- #
# first-aid playbooks — deterministic, structured, delivered alongside the
# conversational guidance so a rescuer can follow them step by step.
# --------------------------------------------------------------------------- #

_CPR_PLAYBOOK = {
    "kind": "cpr",
    "call_emergency_services": True,
    "steps": [
        "Call emergency services now (or have someone else call).",
        "Lay the person on their back on a firm surface; tilt the head back.",
        "Place the heel of one hand on the center of the chest, other hand on "
        "top, arms straight.",
        "Push hard and fast — at least 2 inches (5 cm) deep — and let the "
        "chest fully recoil between compressions.",
        "Follow the pace cue below; after 30 compressions give 2 rescue "
        "breaths, then continue 30:2.",
        "Do not stop until help arrives, an AED is ready, or the person "
        "responds.",
    ],
    # Proper pace, cued visually and audibly (patent: red/green lights + audio).
    "pace": {
        "compressions_per_minute": 110,
        "compression_to_breath_ratio": "30:2",
        "cue": {
            "light": "green flashes on each compression beat; red means "
                     "you've drifted off pace",
            "audio": "metronome tick at 110 beats per minute",
        },
    },
}

_AED_PLAYBOOK = {
    "kind": "aed",
    "call_emergency_services": True,
    "steps": [
        "Call emergency services and send someone for the nearest AED.",
        "Turn the AED on and follow its voice prompts.",
        "Expose the chest and attach the pads as shown on the pad diagrams.",
        "Stand clear while the AED analyzes the rhythm — touch no one.",
        "If a shock is advised, make sure no one is touching the person, "
        "then press the shock button.",
        "Resume CPR immediately after the shock (30:2) until the AED "
        "re-analyzes or help arrives.",
    ],
    "pace": _CPR_PLAYBOOK["pace"],
}

_LOW_O2_PLAYBOOK = {
    "kind": "low_blood_oxygen",
    "call_emergency_services": False,
    "steps": [
        "Breathe deeply — slow breaths in through the nose, out through the "
        "mouth.",
        "Move to an environment with fresh air (outdoors or an open window).",
        "Sit upright and rest; avoid exertion.",
        "Seek medical attention — and call emergency services if it drops "
        "further or breathing becomes hard.",
    ],
}

_ENVIRONMENT_PLAYBOOK = {
    "kind": "environmental_hazard",
    "call_emergency_services": True,
    "steps": [
        "Leave the area immediately — move to fresh air.",
        "Do not re-enter until the hazard is cleared by responders.",
        "If anyone has symptoms (headache, dizziness, nausea), seek medical "
        "attention now.",
    ],
}

_ERGONOMIC_PLAYBOOK = {
    "kind": "ergonomic",
    "call_emergency_services": False,
    "steps": [
        "Pause the task and reset your posture: shoulders back, screen at "
        "eye level, feet flat.",
        "Take a 2–3 minute movement break; stretch the muscles you've been "
        "loading.",
        "Alternate tasks or positions to break up the repetitive motion.",
    ],
}


def playbook(kind: str) -> dict | None:
    """A first-aid playbook by kind ("cpr" | "aed") — the same structured
    steps a rescuer sees, reused verbatim when a robot coaches them aloud."""
    return {"cpr": _CPR_PLAYBOOK, "aed": _AED_PLAYBOOK}.get(kind)


def first_aid_for(detection: conditions.Detection) -> dict | None:
    """The structured first-aid playbook for a physical detection, or None
    when the condition doesn't call for one."""
    if detection.condition == conditions.CARDIAC:
        pattern = detection.signals.get("pattern")
        return _AED_PLAYBOOK if pattern == "fibrillation" else _CPR_PLAYBOOK
    if detection.condition == conditions.ENVIRONMENT:
        return _ENVIRONMENT_PLAYBOOK
    if detection.condition == conditions.ERGONOMIC:
        return _ERGONOMIC_PLAYBOOK
    if (detection.condition == conditions.PHYSICAL_DISTRESS
            and "blood_oxygen" in detection.signals):
        return _LOW_O2_PLAYBOOK
    return None


# A minimal safety net so standalone guidance never emits harmful phrasing.
_DENY = re.compile(r"\b(kill yourself|you should give up|no hope)\b", re.I)


def personalize(user: dict | None) -> str:
    """User-specific adaptation lines for a system prompt: the declared
    conditions and personality preferences that make this *their* model."""
    if not user:
        return ""
    lines = []
    known = user.get("known_conditions") or []
    if known:
        labels = ", ".join(conditions.LABELS.get(c, c) for c in known)
        lines.append(f"known conditions for this user: {labels}")
    personality = user.get("personality") or {}
    if personality.get("tone"):
        lines.append(f"tone: {personality['tone']}")
    if personality.get("instructions"):
        lines.append(f"user preference: {personality['instructions']}")
    return ("\n" + "\n".join(lines)) if lines else ""


def provenance_for(condition: str, provider_name: str,
                   deterministic: bool = False) -> dict:
    """The verifiable basis of a piece of advice: how it was produced, by
    what, and the published sources it derives from — so every response can
    be checked at the source instead of taken on faith."""
    if deterministic:
        method = ("deterministic first-aid playbook transcribed from the "
                  "cited publishers — not model-generated")
    else:
        method = ("model-generated counsel grounded in the cited published "
                  "sources and this user's own baseline")
    return {
        "method": method,
        "generated_by": provider_name,
        "evidence": EVIDENCE.get(condition, []),
        "disclaimer": "Educational guidance, not a diagnosis. The evidence "
                      "links are the derivation trail — verify anything that "
                      "matters and seek professional care.",
    }


def generate(detection: conditions.Detection, note: str | None,
             user: dict | None = None, memory: str | None = None) -> dict:
    from . import i18n

    label = conditions.LABELS.get(detection.condition, detection.condition)
    situation = detection.reason + (f'. The user said: "{note}"' if note else "")
    system = _SYSTEM.format(label=label, situation=situation)
    first_aid = first_aid_for(detection)
    if detection.condition == conditions.PHYSICAL_INJURY or first_aid:
        system += _FIRST_AID
    system += personalize(user)
    if memory:
        system += f"\nprior interactions: {memory}"

    language = (i18n.effective_language(user["id"]) if user and user.get("id")
                else i18n.DEFAULT)
    system += i18n.directive(language)

    prompt = note or f"The user may be experiencing {label}."
    # Honor the user's chosen provider when we know who this is; fall back to
    # the platform default for anonymous/pre-enrollment guidance.
    choice = (llm.get_choice(user["id"]) if user and user.get("id") else None)
    provider = (llm.provider_for_user(user["id"]) if user and user.get("id")
                else llm.get_provider())
    effective = llm.resolve_choice(choice)
    text = provider.generate(system, prompt)

    if _DENY.search(text):
        return {"delivered": False, "source": "local",
                "reason": "guidance failed safety check", "content": None}
    out = {"delivered": True, "source": "local",
           "condition": detection.condition, "content": text,
           "language": language,
           "references": REFERENCES.get(detection.condition, []),
           "provenance": provenance_for(detection.condition, effective,
                                        deterministic=first_aid is not None)}
    if language != i18n.DEFAULT and effective == "stub":
        out["translation_note"] = (
            "the offline stub cannot translate free text — structured "
            "first-aid steps are hand-localized; conversational text may "
            "appear in English")
    if first_aid:
        # Structured, step-by-step first aid (CPR pace cues, AED steps, …)
        # travels with the conversational guidance — hand-localized, never
        # machine-mangled.
        out["first_aid"] = i18n.localize_playbook(first_aid, language)
    return out
