"""Interview drills: practice the answer before the room is real.

The career area's most-asked exercise in the field research. The honest
offline shape: the questions are a curated local bank — asked with what
each one probes stated up front, because an interviewer's intent is half
the question — and the drill works with the network cut. When an online
model stands, it reads the answer against what the question probes and
says what landed and what was missing, never inventing facts about the
person; offline, the drill closes with the probe checklist itself, plainly
labeled — a mirror, not a pretended judge.
"""

from __future__ import annotations

import random

from . import db, life, llm


class DrillError(Exception):
    pass


#: The bank: (kind, question, what it probes). Curated, local, offline-safe.
QUESTIONS: list[dict] = [
    {"kind": "behavioral",
     "question": "Tell me about a time you disagreed with a decision at "
                 "work. What did you do?",
     "probes": ["a real situation, not a hypothetical",
                "what you actually said and did",
                "how it resolved and what you learned"]},
    {"kind": "behavioral",
     "question": "Describe a project that failed. What was your part in "
                 "the failure?",
     "probes": ["ownership without deflection",
                "the concrete mistake, named",
                "what changed in how you work"]},
    {"kind": "behavioral",
     "question": "Tell me about a time you had to deliver under a deadline "
                 "you thought was unreasonable.",
     "probes": ["how you triaged scope",
                "how you communicated the risk",
                "what shipped and what didn't"]},
    {"kind": "situational",
     "question": "Your teammate keeps missing handoffs and it is slowing "
                 "you down. What do you do first?",
     "probes": ["going to the person before the manager",
                "curiosity about causes before blame",
                "a concrete next step"]},
    {"kind": "situational",
     "question": "You inherit a mess with no documentation and a deadline "
                 "in two weeks. Walk me through your first three days.",
     "probes": ["mapping before changing",
                "finding who knows what",
                "earliest honest status signal"]},
    {"kind": "strengths",
     "question": "What is the piece of work you are proudest of, and what "
                 "did it take?",
     "probes": ["specifics a stranger could verify",
                "your part versus the team's, honestly split",
                "why it mattered to somebody"]},
    {"kind": "strengths",
     "question": "What do colleagues come to you for?",
     "probes": ["evidence, not adjectives",
                "a story where it happened",
                "self-knowledge that sounds lived-in"]},
    {"kind": "weaknesses",
     "question": "What is a real weakness of yours — not a strength in "
                 "disguise — and what are you doing about it?",
     "probes": ["a weakness that actually costs something",
                "a concrete practice against it",
                "no humble-brag"]},
    {"kind": "motivation",
     "question": "Why this role, and why now?",
     "probes": ["knowledge of the actual role",
                "a reason that survives a follow-up question",
                "what you are moving toward, not just from"]},
    {"kind": "motivation",
     "question": "Where do you want to be in three years, and how does "
                 "this job get you there?",
     "probes": ["a direction, not a title",
                "the honest link to this role",
                "what you would need to learn"]},
]

_KINDS = sorted({q["kind"] for q in QUESTIONS})

_COACH_SYSTEM = (
    "You are an interview coach reading one practice answer. The question "
    "and what it probes are given. Say plainly, in three or four "
    "sentences: which probes the answer actually hit, which it missed, "
    "and the one change that would most strengthen it. Judge only the "
    "answer's structure and specificity — never invent facts about the "
    "person, their story, or the job. No scores, no flattery.")


def start(user: dict, kind: str | None = None) -> dict:
    """Deal one question — with what it probes stated up front, because an
    interviewer's intent is half the question."""
    user_id = user["id"]
    pool = QUESTIONS
    if kind:
        pool = [q for q in QUESTIONS if q["kind"] == kind]
        if not pool:
            raise DrillError("no such drill kind — this bank holds: "
                             + ", ".join(_KINDS))
    q = random.choice(pool)
    conn = db.connect()
    drill_id = db.new_id("drl")
    conn.execute(
        "INSERT INTO drills (id, user_id, kind, question, probes,"
        " created_at) VALUES (?,?,?,?,?,?)",
        (drill_id, user_id, q["kind"], q["question"],
         "\n".join(q["probes"]), db.utcnow()))
    conn.commit()
    return {"id": drill_id, "kind": q["kind"], "question": q["question"],
            "probes": q["probes"]}


def answer(user: dict, drill_id: str, response: str, cloud=None) -> dict:
    """Read the answer against what the question probes — by the online
    coach when one is standing, by the checklist itself when not."""
    user_id = user["id"]
    text = (response or "").strip()
    if not text:
        raise DrillError("an empty answer drills nothing — say it out "
                         "loud, then write what you said")
    conn = db.connect()
    row = conn.execute(
        "SELECT * FROM drills WHERE id=? AND user_id=?",
        (drill_id, user_id)).fetchone()
    if row is None:
        raise DrillError("no such drill")
    if row["answered_at"] is not None:
        raise DrillError("this drill is already answered — deal another "
                         "question")

    probes = row["probes"].split("\n")
    feedback, described_by = None, "checklist"
    result = llm.generate_for_user(
        user_id, _COACH_SYSTEM,
        "Question: " + row["question"] + "\nProbes:\n- "
        + "\n- ".join(probes) + "\nAnswer:\n" + text, cloud=cloud)
    said = (result.get("text") or "").strip()
    if said and result.get("provider") not in (None, "stub"):
        feedback, described_by = said, "model"

    conn.execute(
        "UPDATE drills SET response=?, feedback=?, described_by=?,"
        " answered_at=? WHERE id=?",
        (text, feedback, described_by, db.utcnow(), drill_id))
    conn.commit()
    # The practice reaches the career area's readable context, like any
    # local note — the coach that plans your week should know you drilled.
    life.add_context(user_id, "drills", "career_drill",
                     {"content": "practiced: " + row["question"]}, pdi=None)
    return {"id": drill_id, "question": row["question"], "probes": probes,
            "feedback": feedback, "described_by": described_by}


def history(user_id: str, limit: int = 20) -> list[dict]:
    """Recent drills, newest first — question, whether answered, and how
    the reading was made."""
    rows = db.connect().execute(
        "SELECT id, kind, question, response, feedback, described_by,"
        " created_at, answered_at FROM drills WHERE user_id=?"
        " ORDER BY created_at DESC, rowid DESC LIMIT ?",
        (user_id, limit)).fetchall()
    return [dict(r) for r in rows]
