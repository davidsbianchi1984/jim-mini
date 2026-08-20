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

The row also says **who answered**. ``answered_by`` is the excursion's
provenance fingerprint: the provider that actually wrote the findings — a
registry name when that model spoke, ``vault`` when the resident did,
``stub`` when a degrade or a keyless machine left the words to the local
deterministic provider. It is read from the provider that generated, the
same duck-typed record ``llm.generate_for_user`` trusts, never from the
choice that was asked for — the letter's rule, applied to the study: the
name on the record is whoever wrote the words.
"""

from __future__ import annotations

import os
import re
from contextvars import ContextVar

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


#: Who actually wrote the last gather on this request. Request-scoped like
#: the sibling product's `llm` record, because the provider is built and
#: discarded inside the gather — there is no instance for `excursion` to
#: interrogate afterwards, and a module global would let two concurrent
#: studies describe each other's findings.
_GATHERED_BY: ContextVar[str | None] = ContextVar(
    "jim_research_gathered_by", default=None)


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
    findings = provider.generate(_RESEARCH_SYSTEM, brief)
    # Who actually answered, duck-typed the way `generate_for_user` reads
    # it: the fallback and cloud wrappers carry `answered_by`, the bare
    # stub is itself, and anything else stays unrecorded rather than
    # guessed.
    who = getattr(provider, "answered_by", None)
    if who is None and isinstance(provider, llm.StubProvider):
        who = "stub"
    _GATHERED_BY.set(who)
    return findings


def gather_inside(brief: str, pdi=None) -> str:
    """The person chose the vault's voice: the brief goes to the resident
    and the findings are made on the facility's own hardware — even the
    sanitized brief never reaches an external model. An older tandem
    without the voice door falls to the local deterministic provider,
    because the honest fallback for "never send it out" is a worse
    answer made at home, not a better one made by shipping it anyway."""
    infer = getattr(pdi, "resident_infer", None) if pdi is not None else None
    if infer is not None:
        try:
            out = infer(f"{_RESEARCH_SYSTEM}\n\n{brief}")
        except Exception:  # noqa: BLE001
            out = None
        if out and (out.get("text") or "").strip():
            _GATHERED_BY.set("vault")
            return out["text"].strip()
    # The fall to the local provider is recorded as itself — an older
    # tandem's excursion must not wear the vault's name.
    _GATHERED_BY.set("stub")
    return llm.get_provider(None).generate(_RESEARCH_SYSTEM, brief)


def excursion(user_id: str, topic: str, question: str = "",
              private: list[str] | None = None, cloud=None,
              learn: bool = False, pdi=None) -> str:
    """Go and study one topic, and write down exactly what could have left.

    The whole outbound path, in one function. It was written twice inline in
    `api.py` — once for a person asking a question and once for the coach's
    own study — and the two copies had already drifted: one folded the
    findings into the store and closed the matching recorded miss, the other
    did neither, and nothing said which behaviour was the intended one.

        asked     is the brief sanitized before it leaves
        mattered  is there one path it can leave by

    ``learn`` is that difference, named. It folds the findings into the
    offline coach's store and closes any gap the topic answers — which is the
    loop this product is for: what the coach could not answer becomes what
    JIM went and learned, and the coach knows it next time.

    Returns the excursion id. The row is the audit trail: ``brief`` is
    precisely what could have gone out, ``redactions`` counts what was taken
    out of it, ``left_host`` says whether anything actually went — and
    ``answered_by``, who actually wrote what came back.
    """
    brief, redactions = sanitize(user_id, f"{topic}\n{question}".strip(),
                                 private)
    # The study speaks with the voice the person chose. A user whose
    # provider is the vault studies *inside*: the brief goes to the
    # resident, nothing reaches an external model, and left_host says so
    # — the choice they made for the coach was a choice about where
    # their words are made, and the study path is not entitled to a
    # different answer.
    # Who actually wrote the findings, recorded beside what could have
    # left. Cleared before the gather so an earlier study on this request
    # cannot describe this one, read after it, and put back the way it
    # was found.
    token = _GATHERED_BY.set(None)
    try:
        if llm.resolve_choice(llm.get_choice(user_id)) == "vault":
            left_host = False
            findings = gather_inside(brief, pdi)
        else:
            left_host = would_leave(cloud)
            findings = gather(brief, cloud)
        answered = _GATHERED_BY.get()
    finally:
        _GATHERED_BY.reset(token)
    cid = db.new_id("exc")
    conn = db.connect()
    conn.execute(
        "INSERT INTO excursions (id, user_id, topic, brief, redactions,"
        " left_host, findings, learned, answered_by, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?)",
        (cid, user_id, topic, brief, redactions, int(left_host), findings,
         1 if learn else 0, answered, db.utcnow()))
    if learn:
        conn.execute(
            "UPDATE gaps SET filled=1 WHERE user_id=?"
            " AND lower(question)=lower(?)", (user_id, topic))
    conn.commit()
    return cid
