"""Terms of Service: version, key points, and the acceptance contract.

The full text lives in docs/terms.md; GET /terms serves the version and
key points so every client can display them, and enrollment records the
accepted version + timestamp — clickwrap with a server-side receipt.
Bump TERMS_VERSION when the document materially changes.
"""

from __future__ import annotations

TERMS_VERSION = "1.0"

DOCUMENT = "docs/terms.md"

KEY_POINTS = [
    "JIM-mini is a wellness tool, not a medical device — it does not "
    "diagnose or treat, and no doctor-patient relationship is formed.",
    "In an emergency call 911 first; in crisis call or text 988 (US). "
    "Escalation features supplement, never replace, emergency services.",
    "Detection can miss real events and flag non-events; do not delay "
    "professional care because of the app.",
    "You assume the risks of AI guidance, monitoring, escalation, and "
    "robot-assisted response, and release the operator except for gross "
    "negligence or willful misconduct.",
    "Fully autonomous resuscitation additionally requires the separate "
    "signed waiver — never available for a minor; a robot never delivers "
    "the shock.",
    "Guardians accept on a child's behalf; safety monitoring never pauses.",
    "The service is provided as-is; liability is capped.",
]
