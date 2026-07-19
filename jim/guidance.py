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
}

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
    if detection.condition == conditions.PHYSICAL_INJURY:
        system += _FIRST_AID
    system += personalize(user)
    if memory:
        system += f"\nprior interactions: {memory}"
    prompt = note or f"The user may be experiencing {label}."
    text = llm.get_provider().generate(system, prompt)

    if _DENY.search(text):
        return {"delivered": False, "source": "local",
                "reason": "guidance failed safety check", "content": None}
    return {"delivered": True, "source": "local", "condition": detection.condition,
            "content": text,
            "references": REFERENCES.get(detection.condition, [])}
