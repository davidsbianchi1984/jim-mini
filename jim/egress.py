"""The general-terms door: what the coach may say to a model, and the log
of every sentence that left.

The coach (:mod:`jim.pipeline`) is the offline model. It answers from what
it has already learned, on this device, for nothing, and it touches no
network. When it lacks something it does not hand the person's question to
a vendor's model. It asks **in general terms** — the question is rewritten
so that it is about *a person* and not this person, every identifier is
taken out and every exact value is taken out and kept here — and what comes
back is learned into the store, so the same gap is never bought twice.

    asked     was the private data redacted
    mattered  can a person read, word for word, everything that went

Two things this module owns, and nothing else does:

* **The composer.** :func:`compose` is the only function that turns text
  about a person into a sentence that may leave. It strips names (the
  person's own, their emergency contact, their contacts' book, and any term
  the caller marks private — through :func:`jim.research.sanitize`, which
  it extends rather than replaces), addresses, links, phones, dates, times,
  ages, readings and every bare number, and it turns the first person into
  the third. What it took out is returned beside the sentence as ``kept``,
  which stays on this device.
* **The ledger.** :func:`note` writes one row per outbound sentence, word
  for word as it was sent, with the fixed framing that went with it, what
  was taken out first, where it went and who answered. It is written by the
  two places anything can go out — the study path
  (:func:`jim.research.excursion`) and the model door
  (:func:`jim.llm.generate_for_user`) — and it is read by
  ``GET /egress/{user}``. A log a person cannot read is a claim; this one is
  the record they check the claim against.

The ledger is append-only and it is complete by construction for those two
doors. It does not pretend to cover paths that never go through them: a
picture read by the eyes, a translation, the monitoring guidance path each
go out on their own terms, which their own modules say. The guard in the
tests names each such path so that a new one has to be added on purpose.
"""

from __future__ import annotations

import json
import re

from . import db

#: The permit the coach's general-terms posture runs under. Its own switch,
#: because what changes is exactly *what leaves* — see :mod:`jim.permits`.
PERMIT = "ask_in_general_terms"

#: The purpose written on a ledger row the coach's general-terms ask left.
#: Distinct from ``coach``, which is a coach turn sent as written by a
#: person who did not switch this posture on.
PURPOSE = "general_terms"

#: The fixed framing sent with a general-terms question. No slot in it is
#: ever filled from the person's records.
FRAMING = (
    "You are a research assistant. The question below is general and has "
    "been stripped of every name, number, date and place. Answer with "
    "concise, general guidance that would help anyone in that situation. "
    "Never ask for, guess at or infer anything about a particular "
    "individual."
)

_WS = re.compile(r"\s+")

# --------------------------------------------------------------------------- #
# the composer
# --------------------------------------------------------------------------- #

# Each pass takes a class of value out and says what it was. Ordered from
# the most specific shape to the least, so that a date is a date before its
# digits could be read as a bare number, and a blood-pressure reading is a
# reading before its halves could be read as two of them.
_MONTHS = ("january|february|march|april|may|june|july|august|september|"
           "october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|"
           "oct|nov|dec")
_UNITS = (r"mg|mcg|µg|ug|g|kg|kgs|lb|lbs|oz|ml|l|litres?|liters?|bpm|mmhg|"
          r"kcal|cal|calories|steps|km|mi|miles?|cm|mm|ft|in|inches|"
          r"hours?|hrs?|h|minutes?|mins?|m|seconds?|secs?|s|days?|weeks?|"
          r"wks?|months?|years?|yrs?|%|percent|°[cf]?|degrees")

_PASSES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("[email]", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")),
    ("[link]", re.compile(r"(?:https?://|www\.)\S+", re.I)),
    ("[date]", re.compile(r"\b\d{4}-\d{2}-\d{2}\b")),
    ("[date]", re.compile(r"\b\d{1,2}[/.]\d{1,2}[/.]\d{2,4}\b")),
    ("[date]", re.compile(
        rf"\b(?:{_MONTHS})\.?\s+\d{{1,2}}(?:st|nd|rd|th)?(?:,?\s+\d{{4}})?\b",
        re.I)),
    ("[date]", re.compile(
        rf"\b\d{{1,2}}(?:st|nd|rd|th)?\s+(?:of\s+)?(?:{_MONTHS})\.?(?:,?\s+\d{{4}})?\b",
        re.I)),
    ("[time]", re.compile(r"\b\d{1,2}(?::\d{2})?\s*(?:am|pm|a\.m\.|p\.m\.)\b",
                          re.I)),
    ("[time]", re.compile(r"\b\d{1,2}:\d{2}\b")),
    ("[age]", re.compile(
        r"\b\d{1,3}\s*(?:years?|yrs?)[\s-]*old\b|\b\d{1,3}\s*y/?o\b|"
        r"\bage(?:d)?\s+\d{1,3}\b|\b(?:I'?m|I am)\s+\d{1,3}\b", re.I)),
    ("[reading]", re.compile(r"\b\d{2,3}\s*/\s*\d{2,3}\b")),
    ("[phone]", re.compile(r"(?<![\w/])\+?\d[\d\s().-]{7,}\d(?![\w/])")),
    ("[amount]", re.compile(rf"\b\d+(?:[.,]\d+)?\s*(?:{_UNITS})\b", re.I)),
    ("[number]", re.compile(r"(?<![\w\[])[-+]?\d+(?:[.,]\d+)?(?![\w\]])")),
)

# First person into third. The sentence that leaves is about a person, not
# this person; "I keep waking" becomes "a person keeps waking" only in the
# pronoun, and the grammar is allowed to show the seam — the ledger is read
# by people, and a seam is more honest than a polish that hides the edit.
_PERSON: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bI am\b"), "a person is"),
    (re.compile(r"\bI'm\b"), "a person is"),
    (re.compile(r"\bI've\b"), "a person has"),
    (re.compile(r"\bI'll\b"), "a person will"),
    (re.compile(r"\bI'd\b"), "a person would"),
    (re.compile(r"\bI\b"), "a person"),
    (re.compile(r"\bmy\b", re.I), "their"),
    (re.compile(r"\bmyself\b", re.I), "themselves"),
    (re.compile(r"\bmine\b", re.I), "theirs"),
    (re.compile(r"\bme\b", re.I), "them"),
)


def _norm(s: str) -> str:
    return _WS.sub(" ", s or "").strip()


def compose(user_id: str, text: str, extra: list[str] | None = None,
            limit: int = 500) -> dict:
    """Turn text about this person into a sentence that may leave.

    Returns ``sentence`` (what may go), ``redactions`` (how many things
    were taken out or generalised) and ``kept`` — each thing taken out,
    with the marker it became, which stays here and is never sent.
    """
    from . import research
    sentence = _norm(text)
    kept: list[dict] = []
    # Shapes first — an address is taken out whole, before a name inside
    # it could be redacted on its own and leave the domain standing.
    for marker, pattern in _PASSES:
        def _take(m: re.Match, marker=marker) -> str:
            kept.append({"took": m.group(0), "as": marker})
            return marker
        sentence = pattern.sub(_take, sentence)
    # Then names, through the sanitiser the excursions have always used:
    # the person's own, their emergency contact's, their contacts' book
    # and any term the caller marked. A name is a whole word.
    sentence, names = research.sanitize(
        user_id, sentence, list(extra or []) + _contacts(user_id))
    generalised = 0
    for pattern, replacement in _PERSON:
        def _swap(m: re.Match, replacement=replacement) -> str:
            word = m.group(0)
            return replacement.capitalize() if word[0].isupper() and \
                word.lower() not in ("i", "i'm", "i've", "i'll", "i'd") \
                else replacement
        sentence, n = pattern.subn(_swap, sentence)
        generalised += n
    sentence = _norm(sentence)[:limit]
    redactions = names + len(kept) + generalised
    if names:
        # The names themselves are not written down even here: the count
        # is enough to check the sentence against, and a row that repeats
        # the name it removed has removed nothing.
        kept.insert(0, {"took": f"{names} name(s)", "as": research.REDACTION})
    return {"sentence": sentence, "redactions": redactions, "kept": kept,
            "generalised": generalised}


def _contacts(user_id: str) -> list[str]:
    """The names and numbers in this person's own contact book, and every
    part of every name on the account, so that a question about "whether
    Marguerite should…" leaves without Marguerite — and "Ana" alone goes
    when the contact is "Ana Reyes". The sanitiser matches whole terms; a
    first name on its own is the way a person actually writes."""
    conn = db.connect()
    terms: list[str] = []
    u = conn.execute(
        "SELECT display_name, legal_name, emergency_name, emergency_phone,"
        " emergency_email FROM users WHERE id=?", (user_id,)).fetchone()
    if u:
        for key in u.keys():
            if u[key] and len(u[key]) >= 2:
                terms.append(u[key])
    for r in conn.execute("SELECT name, digits FROM contacts WHERE user_id=?",
                          (user_id,)).fetchall():
        for value in (r["name"], r["digits"]):
            if value and len(value) >= 2:
                terms.append(value)
    parts = [w for term in terms for w in re.split(r"[\s,.-]+", term)
             if len(w) >= 3 and w.isalpha()]
    return terms + parts


# --------------------------------------------------------------------------- #
# the ledger
# --------------------------------------------------------------------------- #

def note(user_id: str, purpose: str, sentence: str, framing: str = "",
         redactions: int = 0, kept: list[dict] | None = None,
         destination: str = "", answered_by: str | None = None,
         left_host: bool = False) -> str:
    """One row per sentence that could leave, word for word.

    ``left_host`` is whether it went to another party's machine; the vault's
    wire and the local stub are recorded with it False, and the row is kept
    anyway so that *nothing left* is a fact on the record rather than a
    row that is missing.
    """
    eid = db.new_id("egr")
    conn = db.connect()
    conn.execute(
        "INSERT INTO egress (id, user_id, purpose, sentence, framing,"
        " redactions, kept, destination, answered_by, left_host, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (eid, user_id, purpose, sentence, framing or "", int(redactions or 0),
         json.dumps(kept or []), destination or "", answered_by,
         1 if left_host else 0, db.utcnow()))
    conn.commit()
    return eid


def left(provider: str | None) -> bool:
    """Whether a sentence sent to this provider left the host: a network
    provider that is not the vault, and not in offline mode — the same
    reading the excursions and the letter give ``left_host``."""
    from . import llm, offline
    if not provider or provider == "vault" or offline.enabled():
        return False
    return llm.is_network(provider)


def ledger(user_id: str, limit: int = 50) -> dict:
    """Everything that left, newest first, for a person to read.

    Each row is the sentence exactly as sent, the fixed framing it went
    with, what was taken out of it (kept here), where it went, who answered
    and whether it left the host at all.
    """
    rows = db.connect().execute(
        "SELECT * FROM egress WHERE user_id=? ORDER BY created_at DESC,"
        " rowid DESC LIMIT ?", (user_id, limit)).fetchall()
    total = db.connect().execute(
        "SELECT COUNT(*) AS n, COALESCE(SUM(left_host), 0) AS gone"
        " FROM egress WHERE user_id=?", (user_id,)).fetchone()
    return {
        "sentences": [{
            "id": r["id"], "purpose": r["purpose"],
            "sentence": r["sentence"], "framing": r["framing"],
            "redactions": r["redactions"], "kept": json.loads(r["kept"]),
            "destination": r["destination"], "answered_by": r["answered_by"],
            "left_host": bool(r["left_host"]), "created_at": r["created_at"],
        } for r in rows],
        "count": total["n"], "left": total["gone"],
        "note": ("every sentence that could leave this device, word for "
                 "word as it was sent; `kept` is what was taken out first "
                 "and never went"),
    }


# --------------------------------------------------------------------------- #
# the coach's ask
# --------------------------------------------------------------------------- #

def ask(user_id: str, area: str, message: str, pdi=None) -> dict | None:
    """The coach lacked something: ask in general terms, learn the answer.

    Returns what happened — the sentence that went, what was taken out,
    where it went and whether the answer was learned — or None when there
    was nobody worth asking: the person's provider is the local stub, so
    a general question would only be answered by the built-in helper's
    description of itself, and learning that would be learning nothing.
    """
    from . import llm, research
    from .guidance import _DENY
    choice = llm.resolve_choice(llm.get_choice(user_id))
    if choice == "stub":
        return None
    topic = _norm(message)[:120]
    if not topic:
        return None
    # The study path is the one door out: it composes, sends, records the
    # excursion row and the ledger row. `learn` stays False here because
    # whether the answer is worth learning is decided below, on who
    # answered — a degrade to the stub must not be folded into the store.
    cid = research.excursion(user_id, topic, cloud=None, learn=False,
                             pdi=pdi, choice=choice, purpose=PURPOSE,
                             framing=FRAMING)
    conn = db.connect()
    row = conn.execute("SELECT * FROM excursions WHERE id=?",
                       (cid,)).fetchone()
    findings = _norm(row["findings"] or "")
    learned = bool(findings) and row["answered_by"] not in (None, "stub") \
        and not _DENY.search(findings)
    if learned:
        conn.execute("UPDATE excursions SET learned=1 WHERE id=?", (cid,))
        conn.execute("UPDATE gaps SET filled=1 WHERE user_id=? AND"
                     " lower(question)=lower(?)", (user_id, topic))
        conn.commit()
    egr = conn.execute(
        "SELECT id, sentence, kept FROM egress WHERE user_id=? AND"
        " purpose=? ORDER BY created_at DESC, rowid DESC LIMIT 1",
        (user_id, PURPOSE)).fetchone()
    return {"excursion_id": cid, "ledger_id": egr["id"] if egr else None,
            "sentence": row["brief"], "redactions": row["redactions"],
            "kept": json.loads(egr["kept"]) if egr else [],
            "destination": choice, "answered_by": row["answered_by"],
            "left_host": bool(row["left_host"]), "learned": learned,
            "findings": findings if learned else None}
