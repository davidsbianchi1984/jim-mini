"""Life layer: connected sources, check-ins, goals, habits, and insights.

Extends Guardian beyond condition monitoring into everyday guidance:

- **Sources + consent** — context is only accepted from sources the user has
  explicitly allowed; everything else is rejected at the door.
- **Context events** — consented sources feed events (a transaction, a night
  of sleep, a calendar entry) that transparent rules turn into insights.
- **Check-ins** — mood/energy tracking; low mood produces a gentle nudge.
- **Goals & habits** — smart goals with progress, habit logs with streaks.
- **Erasure** — delete everything about a user, anytime.
"""

from __future__ import annotations

import json
from datetime import date, timedelta

from . import db

# Streak lengths worth celebrating.
_MILESTONES = {7, 30, 100}

# Spending above this (single transaction) triggers an alert; a real build
# would learn a per-user budget — the rule keeps v1 transparent.
_SPEND_ALERT = 200.0


# --------------------------------------------------------------------------- #
# sources & consent
# --------------------------------------------------------------------------- #

def set_source(user_id: str, source: str, consented: bool) -> dict:
    conn = db.connect()
    conn.execute(
        "INSERT INTO sources (user_id, source, consented, created_at)"
        " VALUES (?,?,?,?)"
        " ON CONFLICT (user_id, source) DO UPDATE SET consented=excluded.consented",
        (user_id, source, int(consented), db.utcnow()),
    )
    conn.commit()
    return {"source": source, "consented": consented}


def sources(user_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT source, consented FROM sources WHERE user_id=? ORDER BY source",
        (user_id,),
    ).fetchall()
    return [{"source": r["source"], "consented": bool(r["consented"])} for r in rows]


def source_allowed(user_id: str, source: str) -> bool:
    row = db.connect().execute(
        "SELECT consented FROM sources WHERE user_id=? AND source=?",
        (user_id, source),
    ).fetchone()
    return bool(row and row["consented"])


# --------------------------------------------------------------------------- #
# PDI vault (tandem)
# --------------------------------------------------------------------------- #

def vault_store(pdi, user_id: str, key: str, payload: dict) -> str:
    """Seal a payload in the tandem PDI vault and remember the key locally."""
    pdi.put(key, json.dumps(payload))
    conn = db.connect()
    conn.execute(
        "INSERT OR REPLACE INTO vault_keys (user_id, key) VALUES (?,?)",
        (user_id, key),
    )
    conn.commit()
    return key


# --------------------------------------------------------------------------- #
# insights
# --------------------------------------------------------------------------- #

def _insight(user_id, kind, message, *, area=None, source=None) -> dict:
    conn = db.connect()
    insight_id = db.new_id("ins")
    conn.execute(
        "INSERT INTO insights (id, user_id, area, kind, message, source, created_at)"
        " VALUES (?,?,?,?,?,?,?)",
        (insight_id, user_id, area, kind, message, source, db.utcnow()),
    )
    conn.commit()
    return {"id": insight_id, "area": area, "kind": kind,
            "message": message, "source": source}


def insights(user_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM insights WHERE user_id=? ORDER BY created_at DESC, rowid DESC",
        (user_id,),
    ).fetchall()
    return [dict(r) for r in rows]


# --------------------------------------------------------------------------- #
# context events → insight rules
# --------------------------------------------------------------------------- #

def add_context(user_id: str, source: str, kind: str, data: dict,
                pdi=None) -> dict:
    conn = db.connect()
    event_id = db.new_id("ctx")
    stored = data
    if pdi is not None and data:
        key = vault_store(pdi, user_id, f"jim/{user_id}/context/{event_id}", data)
        stored = {"vaulted": True, "pdi_key": key}
    conn.execute(
        "INSERT INTO context_events (id, user_id, source, kind, data, created_at)"
        " VALUES (?,?,?,?,?,?)",
        (event_id, user_id, source, kind, json.dumps(stored), db.utcnow()),
    )
    conn.commit()
    # Rules run on the raw payload in memory — the vault is for storage.
    generated = _context_rules(user_id, source, kind, data)
    return {"id": event_id, "source": source, "kind": kind,
            "vaulted": pdi is not None and bool(data),
            "insights": generated}


def _context_rules(user_id, source, kind, data) -> list[dict]:
    out = []
    if kind == "transaction":
        amount = float(data.get("amount", 0))
        if amount >= _SPEND_ALERT:
            out.append(_insight(
                user_id, "alert",
                f"High spending alert: {data.get('category', 'a purchase')} at "
                f"{amount:.0f} — that's above your usual. Want to review it?",
                area="finance", source=source))
    elif kind == "sleep":
        hours = float(data.get("hours", 0))
        if hours >= 7.5:
            out.append(_insight(
                user_id, "praise",
                f"You slept better last night ({hours:g}h). Keep it up!",
                area="health_fitness", source=source))
        elif hours and hours < 6:
            out.append(_insight(
                user_id, "suggestion",
                f"Short night ({hours:g}h). An earlier wind-down tonight "
                "would help tomorrow.",
                area="health_fitness", source=source))
    elif kind == "event":
        title = str(data.get("title", ""))
        if "interview" in title.lower():
            when = data.get("time", "soon")
            out.append(_insight(
                user_id, "suggestion",
                f"Interview tips ready for '{title}' at {when} — want a "
                "practice round with the career coach?",
                area="career", source=source))
    return out


# --------------------------------------------------------------------------- #
# check-ins
# --------------------------------------------------------------------------- #

def check_in(user_id: str, mood: int, energy: int | None, note: str | None,
             pdi=None) -> dict:
    conn = db.connect()
    checkin_id = db.new_id("chk")
    stored_note = note
    if pdi is not None and note:
        # A check-in note is mental-health data — it belongs in the vault.
        key = vault_store(pdi, user_id,
                          f"jim/{user_id}/medical/checkin/{checkin_id}",
                          {"note": note})
        stored_note = f"pdi:{key}"
    conn.execute(
        "INSERT INTO checkins (id, user_id, mood, energy, note, created_at)"
        " VALUES (?,?,?,?,?,?)",
        (checkin_id, user_id, mood, energy, stored_note, db.utcnow()),
    )
    conn.commit()
    generated = []
    if mood <= 2:
        generated.append(_insight(
            user_id, "suggestion",
            "Time for a mindful break? A two-minute breathing pause can help — "
            "the mental-health coach is here if you want to talk.",
            area="mental_health", source="checkin"))
    return {"id": checkin_id, "mood": mood, "energy": energy,
            "insights": generated}


def checkins(user_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM checkins WHERE user_id=? ORDER BY created_at, rowid",
        (user_id,),
    ).fetchall()
    return [dict(r) for r in rows]


# --------------------------------------------------------------------------- #
# goals
# --------------------------------------------------------------------------- #

def add_goal(user_id: str, area: str, title: str, target: str | None) -> dict:
    conn = db.connect()
    goal_id = db.new_id("gol")
    now = db.utcnow()
    conn.execute(
        "INSERT INTO goals (id, user_id, area, title, target, progress, status,"
        " created_at, updated_at) VALUES (?,?,?,?,?,0,'active',?,?)",
        (goal_id, user_id, area, title, target, now, now),
    )
    conn.commit()
    return _goal(goal_id)


def _goal(goal_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM goals WHERE id=?", (goal_id,)
    ).fetchone()
    return dict(row) if row else None


def update_goal(user_id: str, goal_id: str,
                progress: float | None, status: str | None) -> dict | None:
    goal = _goal(goal_id)
    if goal is None or goal["user_id"] != user_id:
        return None
    conn = db.connect()
    if progress is not None:
        if progress >= 1 and status is None:
            status = "completed"
        conn.execute("UPDATE goals SET progress=?, updated_at=? WHERE id=?",
                     (progress, db.utcnow(), goal_id))
    if status is not None:
        conn.execute("UPDATE goals SET status=?, updated_at=? WHERE id=?",
                     (status, db.utcnow(), goal_id))
    conn.commit()
    updated = _goal(goal_id)
    result = {**updated, "insights": []}
    if status == "completed" and goal["status"] != "completed":
        result["insights"].append(_insight(
            user_id, "praise",
            f"Great job! Goal complete: {goal['title']}. You're on track.",
            area=goal["area"], source="goals"))
    return result


def goals(user_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM goals WHERE user_id=? ORDER BY created_at, rowid",
        (user_id,),
    ).fetchall()
    return [dict(r) for r in rows]


# --------------------------------------------------------------------------- #
# habits & streaks
# --------------------------------------------------------------------------- #

def add_habit(user_id: str, name: str) -> dict:
    conn = db.connect()
    habit_id = db.new_id("hab")
    conn.execute(
        "INSERT INTO habits (id, user_id, name, created_at) VALUES (?,?,?,?)",
        (habit_id, user_id, name, db.utcnow()),
    )
    conn.commit()
    return {"id": habit_id, "name": name, "streak": 0}


def _habit(user_id: str, habit_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM habits WHERE id=? AND user_id=?", (habit_id, user_id)
    ).fetchone()
    return dict(row) if row else None


def log_habit(user_id: str, habit_id: str, day: date | None) -> dict | None:
    habit = _habit(user_id, habit_id)
    if habit is None:
        return None
    day = day or date.today()
    conn = db.connect()
    conn.execute(
        "INSERT OR IGNORE INTO habit_logs (habit_id, day) VALUES (?,?)",
        (habit_id, day.isoformat()),
    )
    conn.commit()
    current = streak(habit_id)
    result = {"habit_id": habit_id, "day": day.isoformat(),
              "streak": current, "insights": []}
    if current in _MILESTONES:
        result["insights"].append(_insight(
            user_id, "milestone",
            f"{current}-day streak on '{habit['name']}' — that's how habits "
            "are built!",
            area="personal_growth", source="habits"))
    return result


def streak(habit_id: str) -> int:
    """Consecutive logged days ending at the most recent log."""
    rows = db.connect().execute(
        "SELECT day FROM habit_logs WHERE habit_id=? ORDER BY day DESC", (habit_id,)
    ).fetchall()
    days = [date.fromisoformat(r["day"]) for r in rows]
    if not days:
        return 0
    count, cursor = 1, days[0]
    for d in days[1:]:
        if d == cursor - timedelta(days=1):
            count += 1
            cursor = d
        else:
            break
    return count


def habits(user_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM habits WHERE user_id=? ORDER BY created_at, rowid",
        (user_id,),
    ).fetchall()
    return [{**dict(r), "streak": streak(r["id"])} for r in rows]


# --------------------------------------------------------------------------- #
# erasure — "delete anything, anytime"
# --------------------------------------------------------------------------- #

def delete_user_data(user_id: str, pdi=None) -> dict:
    """Erase every trace of a user across all tables — and the PDI vault."""
    conn = db.connect()
    deleted = {}
    vaulted = [r["key"] for r in conn.execute(
        "SELECT key FROM vault_keys WHERE user_id=?", (user_id,)).fetchall()]
    if vaulted:
        deleted["pdi_records"] = sum(
            1 for key in vaulted if pdi is not None and pdi.delete(key))
    habit_ids = [r["id"] for r in conn.execute(
        "SELECT id FROM habits WHERE user_id=?", (user_id,)).fetchall()]
    if habit_ids:
        marks = ",".join("?" for _ in habit_ids)
        deleted["habit_logs"] = conn.execute(
            f"DELETE FROM habit_logs WHERE habit_id IN ({marks})", habit_ids
        ).rowcount
    for table in ("habits", "goals", "checkins", "insights", "context_events",
                  "coach_messages", "sources", "sessions", "devices",
                  "vault_keys", "events", "tandem_links", "users"):
        deleted[table] = conn.execute(
            f"DELETE FROM {table} WHERE {'id' if table == 'users' else 'user_id'}=?",
            (user_id,),
        ).rowcount
    conn.commit()
    return {"deleted": deleted}
