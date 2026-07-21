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


def generate(detection: conditions.Detection, note: str | None,
             user: dict | None = None, memory: str | None = None) -> dict:
    label = conditions.LABELS.get(detection.condition, detection.condition)
    situation = detection.reason + (f'. The user said: "{note}"' if note else "")
    system = _SYSTEM.format(label=label, situation=situation)
    first_aid = first_aid_for(detection)
    if detection.condition == conditions.PHYSICAL_INJURY or first_aid:
        system += _FIRST_AID
    system += personalize(user)
    if memory:
        system += f"\nprior interactions: {memory}"
    prompt = note or f"The user may be experiencing {label}."
    text = llm.get_provider().generate(system, prompt)

    if _DENY.search(text):
        return {"delivered": False, "source": "local",
                "reason": "guidance failed safety check", "content": None}
    out = {"delivered": True, "source": "local",
           "condition": detection.condition, "content": text,
           "references": REFERENCES.get(detection.condition, [])}
    if first_aid:
        # Structured, step-by-step first aid (CPR pace cues, AED steps, …)
        # travels with the conversational guidance.
        out["first_aid"] = first_aid
    return out
