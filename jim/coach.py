"""The 24/7 life coach — guidance across life areas, not just conditions.

Where ``guidance.py`` answers a *detected condition*, the coach answers the
user directly in a chosen life area (mental health, health & fitness, career,
finance, relationships, personal growth), grounded in their recent check-ins
and active goals. Uses JIM's own LLM provider and the same safety net.
"""

from __future__ import annotations

from . import db, guardian, life, llm
from .guidance import _DENY, personalize

AREAS = {
    "mental_health": "mental health — support, coping strategies, resources",
    "health_fitness": "health & fitness — workouts, nutrition, sleep, recovery",
    "career": "career & growth — resume feedback, skills, interview prep",
    "finance": "finance — budgeting, saving, and general money habits",
    "relationships": "relationships — communication and connection",
    "personal_growth": "personal growth — habits, focus, becoming your best self",
}

_SYSTEM = (
    "You are JIM-mini's life coach: calm, evidence-based, warm, and brief. "
    "Coaching area: {area}. Never diagnose; for medical, legal, or investment "
    "decisions, recommend a qualified professional. If the user may be in "
    "danger, urge them to seek immediate help.\n"
    "{context}"
)


def _context(user_id: str) -> str:
    lines = []
    recent = life.checkins(user_id)[-1:]
    if recent:
        c = recent[0]
        lines.append(f"latest check-in: mood {c['mood']}/5"
                     + (f", energy {c['energy']}/5" if c["energy"] else ""))
    active = [g for g in life.goals(user_id) if g["status"] == "active"][:3]
    for g in active:
        lines.append(f"active goal ({g['area']}): {g['title']}"
                     f" — {round(g['progress'] * 100)}% done")
    prior = history(user_id)
    if prior:
        lines.append(f"{len(prior)} prior coach message(s) on record — keep "
                     "continuity with earlier sessions")
    return "\n".join(lines) if lines else "no recent check-ins or goals"


def reply(user_id: str, area: str, message: str) -> dict:
    system = _SYSTEM.format(area=AREAS[area], context=_context(user_id))
    system += personalize(guardian.get_user(user_id))
    text = llm.provider_for_user(user_id).generate(system, message)

    safe = not _DENY.search(text)
    conn = db.connect()
    now = db.utcnow()
    conn.execute(
        "INSERT INTO coach_messages (id, user_id, area, role, content, created_at)"
        " VALUES (?,?,?,?,?,?)",
        (db.new_id("msg"), user_id, area, "user", message, now),
    )
    if safe:
        conn.execute(
            "INSERT INTO coach_messages (id, user_id, area, role, content, created_at)"
            " VALUES (?,?,?,?,?,?)",
            (db.new_id("msg"), user_id, area, "coach", text, now),
        )
    conn.commit()

    if not safe:
        return {"delivered": False, "area": area,
                "reason": "coach reply failed safety check", "content": None}
    return {"delivered": True, "area": area, "content": text}


def companion_checkin(user_id: str) -> dict:
    """An unprompted, ambient check-in: the coach reaches out first,
    grounded in the user's latest mood and goals. Opt-in by nature — it is
    only ever triggered by an explicit API call on the user's behalf."""
    user = guardian.get_user(user_id)
    recent = life.checkins(user_id)[-1:]
    mood_note = (f"their last check-in was mood {recent[0]['mood']}/5"
                 if recent else "they haven't checked in lately")
    system = _SYSTEM.format(
        area="ambient companionship — a brief, warm, unprompted check-in",
        context=_context(user_id))
    system += personalize(user)
    system += (f"\n\nYou are reaching out first ({mood_note}). One or two "
               "sentences, warm and unpressured; invite, never demand.")
    text = llm.provider_for_user(user_id).generate(system, "Reach out and check in.")

    if _DENY.search(text):
        return {"delivered": False, "reason": "failed safety check",
                "content": None}
    conn = db.connect()
    conn.execute(
        "INSERT INTO coach_messages (id, user_id, area, role, content,"
        " created_at) VALUES (?,?,?,?,?,?)",
        (db.new_id("msg"), user_id, "mental_health", "coach", text,
         db.utcnow()),
    )
    conn.commit()
    return {"delivered": True, "unprompted": True, "content": text}


def history(user_id: str, area: str | None = None) -> list[dict]:
    conn = db.connect()
    if area:
        rows = conn.execute(
            "SELECT * FROM coach_messages WHERE user_id=? AND area=?"
            " ORDER BY created_at, rowid", (user_id, area)).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM coach_messages WHERE user_id=?"
            " ORDER BY created_at, rowid", (user_id,)).fetchall()
    return [dict(r) for r in rows]
