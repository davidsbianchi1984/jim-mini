"""Guided calm — mindfulness on demand, not only in a crisis.

The Guardian has always been able to calm somebody *down* (the crisis
path's calming guidance); this module is the other direction the field
asked for: a person who simply wants a moment — a reset between meetings,
a breathing exercise before a hard call, a longer sit — starts one on
purpose, any hour, no episode required.

Deterministic by design. A breathing pattern is a *protocol*: box
breathing is 4-4-4-4 and stays 4-4-4-4, and a model that improvised the
counts would be worse than no model at all. The scripts live here as data,
timed step by step so a UI can pace them and the voice layer can speak
them. What the model IS for — reflecting on how the session landed — stays
in the Coach, where it already lives.

Sessions are logged as events (type ``calm``), which makes them visible to
the insights layer the same way check-ins are: a fortnight of daily
breathing sessions alongside a falling resting heart rate is exactly the
kind of pattern worth noticing out loud.
"""

from __future__ import annotations

import json

from . import db


class CalmError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


# kind -> the protocol. Steps carry seconds so a UI can pace and a voice can
# speak them; repeat says how many rounds the standard session runs.
SESSIONS: dict[str, dict] = {
    "quick_reset": {
        "title": "Quick reset",
        "minutes": 2,
        "what": "Sixty seconds of grounding for the moment everything is "
                "too much — five things routed through the senses.",
        "repeat": 1,
        "calm_steps": [
            {"say": "Sit back. Feel your feet on the floor.", "seconds": 10},
            {"say": "Name five things you can see.", "seconds": 15},
            {"say": "Four things you can feel.", "seconds": 15},
            {"say": "Three things you can hear.", "seconds": 15},
            {"say": "Two things you can smell, one you can taste.",
             "seconds": 15},
            {"say": "One slow breath. You're here.", "seconds": 10},
        ],
    },
    "box_breathing": {
        "title": "Box breathing",
        "minutes": 4,
        "what": "Four counts in, four held, four out, four held — the "
                "steadiest pattern there is, four rounds.",
        "repeat": 4,
        "calm_steps": [
            {"say": "Breathe in through the nose — two, three, four.",
             "seconds": 4},
            {"say": "Hold — two, three, four.", "seconds": 4},
            {"say": "Out through the mouth — two, three, four.", "seconds": 4},
            {"say": "Hold empty — two, three, four.", "seconds": 4},
        ],
    },
    "deep_breathing": {
        "title": "4-7-8 breathing",
        "minutes": 5,
        "what": "In for four, held for seven, out for eight — the long "
                "exhale is the point. Four rounds.",
        "repeat": 4,
        "calm_steps": [
            {"say": "In through the nose for four.", "seconds": 4},
            {"say": "Hold for seven.", "seconds": 7},
            {"say": "Out slowly for eight, like fogging a mirror.",
             "seconds": 8},
        ],
    },
    "meditation": {
        "title": "Seated meditation",
        "minutes": 10,
        "what": "A longer sit: settle, follow the breath, return when the "
                "mind wanders — which is the practice, not the failure.",
        "repeat": 1,
        "calm_steps": [
            {"say": "Settle into your seat. Let your shoulders drop.",
             "seconds": 30},
            {"say": "Close your eyes, or rest them low.", "seconds": 15},
            {"say": "Follow the breath at the nose. Nothing to fix.",
             "seconds": 180},
            {"say": "When the mind wanders, notice — and return. That "
                    "return is the practice.", "seconds": 180},
            {"say": "Widen out: the room, the sounds, the weight of you.",
             "seconds": 120},
            {"say": "Open your eyes. Carry the pace with you.",
             "seconds": 30},
        ],
    },
}


def catalog() -> list[dict]:
    return [{"kind": kind, "title": s["title"], "minutes": s["minutes"],
             "what": s["what"]} for kind, s in SESSIONS.items()]


def start(user_id: str, kind: str) -> dict:
    """One session, fully scripted, logged as an event. The UI paces the
    steps; the voice layer may speak each ``say``."""
    if kind not in SESSIONS:
        raise CalmError(422, f"no such session {kind!r}; one of "
                             f"{', '.join(SESSIONS)}")
    s = SESSIONS[kind]
    steps = s["calm_steps"] * s["repeat"]
    total = sum(st["seconds"] for st in steps)
    conn = db.connect()
    conn.execute(
        "INSERT INTO events (id, user_id, type, condition, severity, detail,"
        " created_at) VALUES (?,?,?,?,?,?,?)",
        (db.new_id("evt"), user_id, "calm", kind, "info",
         json.dumps({"title": s["title"], "seconds": total}), db.utcnow()))
    conn.commit()
    return {"kind": kind, "title": s["title"], "what": s["what"],
            "total_seconds": total, "calm_steps": steps,
            "note": "a protocol, not a generation — the counts never vary"}


def history(user_id: str, limit: int = 30) -> list[dict]:
    rows = db.connect().execute(
        "SELECT condition AS kind, detail, created_at FROM events"
        " WHERE user_id=? AND type='calm'"
        " ORDER BY created_at DESC, rowid DESC LIMIT ?",
        (user_id, limit)).fetchall()
    out = []
    for r in rows:
        d = json.loads(r["detail"])
        out.append({"kind": r["kind"], "title": d.get("title"),
                    "seconds": d.get("seconds"), "at": r["created_at"]})
    return out
