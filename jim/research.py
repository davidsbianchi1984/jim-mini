"""Safe knowledge excursions for the Guardian.

When the Guardian needs to study an unfamiliar condition, treatment, or topic to
help, it can go and gather **general knowledge** without carrying the user's
private data (PHI) out with it.

- The outbound brief is SANITIZED: the user's name and their emergency contact's
  name, plus any caller-marked private terms, are redacted. General medical
  topics (e.g. "managing arthritis") are fine to research; the person they
  belong to never leaves.
- Nothing private leaves the host: offline (``JIM_OFFLINE=1``) the gather runs on
  the local provider — no network; even with a cloud model attached only the
  sanitized brief is sent.

Findings come back as general knowledge and fold into the user's guidance
context as a ``knowledge`` note; the local model then answers using them plus the
private context that never left.
"""

from __future__ import annotations

import os
import re

from . import db, llm

REDACTION = "[private]"
_TRUTHY = {"1", "true", "yes", "on"}

_RESEARCH_SYSTEM = (
    "You are a research assistant gathering general background on a topic. The "
    "brief below has been stripped of all private data. Return concise, general "
    "notes that would help someone learn the topic. Never ask for or infer any "
    "personal or medical details about an individual."
)


def _offline() -> bool:
    return os.environ.get("JIM_OFFLINE", "").strip().lower() in _TRUTHY


def _private_terms(user_id: str) -> list[str]:
    u = db.connect().execute(
        "SELECT display_name, emergency_name FROM users WHERE id=?",
        (user_id,)).fetchone()
    terms: set[str] = set()
    if u:
        for key in ("display_name", "emergency_name"):
            if u[key]:
                terms.add(u[key])
    return [t for t in terms if len(t) >= 2]


def sanitize(user_id: str, text: str, extra: list[str] | None = None) -> tuple[str, int]:
    terms = set(_private_terms(user_id)) | set(extra or [])
    out, total = text, 0
    for term in sorted(terms, key=len, reverse=True):
        if not term:
            continue
        out, n = re.compile(rf"\b{re.escape(term)}\b", re.I).subn(REDACTION, out)
        total += n
    return out, total


def would_leave(cloud) -> bool:
    return (not _offline()) and (cloud is not None)


def gather(brief: str, cloud=None) -> str:
    provider = llm.get_provider(None if _offline() else cloud)
    return provider.generate(_RESEARCH_SYSTEM, brief)
