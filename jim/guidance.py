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

# A minimal safety net so standalone guidance never emits harmful phrasing.
_DENY = re.compile(r"\b(kill yourself|you should give up|no hope)\b", re.I)


def generate(detection: conditions.Detection, note: str | None) -> dict:
    label = conditions.LABELS.get(detection.condition, detection.condition)
    situation = detection.reason + (f'. The user said: "{note}"' if note else "")
    system = _SYSTEM.format(label=label, situation=situation)
    user = note or f"The user may be experiencing {label}."
    text = llm.get_provider().generate(system, user)

    if _DENY.search(text):
        return {"delivered": False, "source": "local",
                "reason": "guidance failed safety check", "content": None}
    return {"delivered": True, "source": "local", "condition": detection.condition,
            "content": text}
