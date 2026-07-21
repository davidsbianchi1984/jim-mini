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
        if amount:
            _trend_point(user_id, "spend_amount", amount)
            spend_ahead = forecast_spending(user_id)
            if spend_ahead:
                out.append(spend_ahead)
        if amount >= _SPEND_ALERT:
            out.append(_insight(
                user_id, "alert",
                f"High spending alert: {data.get('category', 'a purchase')} at "
                f"{amount:.0f} — that's above your usual. Want to review it?",
                area="finance", source=source))
    elif kind == "sleep":
        hours = float(data.get("hours", 0))
        if hours:
            _trend_point(user_id, "sleep_hours", hours)
            debt_ahead = forecast_sleep_debt(user_id)
            if debt_ahead:
                out.append(debt_ahead)
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
# predictive early warnings — catch it before it happens
# --------------------------------------------------------------------------- #

def _trend_point(user_id: str, metric: str, value: float) -> None:
    conn = db.connect()
    conn.execute(
        "INSERT INTO trend_points (user_id, metric, value, created_at)"
        " VALUES (?,?,?,?)", (user_id, metric, float(value), db.utcnow()))
    conn.commit()


def _recent(user_id: str, metric: str, n: int) -> list[float]:
    rows = db.connect().execute(
        "SELECT value FROM trend_points WHERE user_id=? AND metric=?"
        " ORDER BY created_at DESC, rowid DESC LIMIT ?",
        (user_id, metric, n)).fetchall()
    return [r["value"] for r in reversed(rows)]


def forecast_mood(user_id: str) -> dict | None:
    """A sliding mood: three strictly declining check-ins ending low — flag it
    before it becomes a crisis-level low."""
    rows = db.connect().execute(
        "SELECT mood FROM checkins WHERE user_id=?"
        " ORDER BY created_at DESC, rowid DESC LIMIT 3", (user_id,)).fetchall()
    moods = [r["mood"] for r in reversed(rows)]
    if len(moods) == 3 and moods[0] > moods[1] > moods[2] and moods[2] <= 3:
        return _insight(
            user_id, "forecast",
            f"Your mood has been sliding ({' → '.join(map(str, moods))}). "
            "A low may be building — a check-in with the mental-health coach "
            "now could head it off.",
            area="mental_health", source="forecast")
    return None


def forecast_sleep_debt(user_id: str) -> dict | None:
    """Accumulating sleep debt: three consecutive short nights — flag the
    debt before exhaustion shows up in mood or biometrics."""
    nights = _recent(user_id, "sleep_hours", 3)
    if len(nights) == 3 and all(h < 6.5 for h in nights):
        debt = round(3 * 8 - sum(nights), 1)
        return _insight(
            user_id, "forecast",
            f"Three short nights in a row ({', '.join(f'{h:g}h' for h in nights)}) "
            f"— roughly {debt:g}h of sleep debt building. Tonight is the one "
            "to protect.",
            area="health_fitness", source="forecast")
    return None


def forecast_spending(user_id: str) -> dict | None:
    """Accelerating spend: the last three purchases together are at least
    double the prior three — an early financial-stress signal even when no
    single purchase trips the high-spend alert."""
    amounts = _recent(user_id, "spend_amount", 6)
    if len(amounts) < 6:
        return None
    prior, recent = sum(amounts[:3]), sum(amounts[3:])
    if prior > 0 and recent >= 2 * prior:
        return _insight(
            user_id, "forecast",
            f"Spending is accelerating: your last three purchases total "
            f"{recent:.0f}, up from {prior:.0f} — worth a look before it "
            "becomes a stress.",
            area="finance", source="forecast")
    return None


def forecast_spo2(user_id: str) -> dict | None:
    """A physical abnormality forming before it manifests: three strictly
    declining blood-oxygen readings ending ≤ 94% — still above the 90%
    detection threshold, but heading for it."""
    readings = _recent(user_id, "blood_oxygen", 3)
    if (len(readings) == 3 and readings[0] > readings[1] > readings[2]
            and readings[2] <= 94):
        return _insight(
            user_id, "forecast",
            f"Blood oxygen has been slipping ({' → '.join(f'{r:g}%' for r in readings)}). "
            "Breathe deeply, get some fresh air, and rest — worth heading off "
            "before it drops further.",
            area="health_fitness", source="forecast")
    return None


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
    sliding = forecast_mood(user_id)
    if sliding:
        generated.append(sliding)
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
# journal, feedback, progress report, provider portal
# --------------------------------------------------------------------------- #

def add_journal(user_id: str, text: str, pdi=None) -> dict:
    conn = db.connect()
    entry_id = db.new_id("jrn")
    stored = text
    if pdi is not None:
        key = vault_store(pdi, user_id,
                          f"jim/{user_id}/medical/journal/{entry_id}",
                          {"text": text})
        stored = f"pdi:{key}"
    conn.execute(
        "INSERT INTO journal (id, user_id, text, created_at) VALUES (?,?,?,?)",
        (entry_id, user_id, stored, db.utcnow()),
    )
    conn.commit()
    return {"id": entry_id, "vaulted": pdi is not None}


def journal_entries(user_id: str, pdi=None) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM journal WHERE user_id=? ORDER BY created_at, rowid",
        (user_id,)).fetchall()
    out = []
    for row in rows:
        item = dict(row)
        if item["text"] and item["text"].startswith("pdi:") and pdi is not None:
            raw = pdi.get(item["text"][4:])
            item["text"] = json.loads(raw)["text"] if raw else None
        out.append(item)
    return out


def add_feedback(user_id: str, rating: str, note: str | None) -> dict:
    conn = db.connect()
    feedback_id = db.new_id("fbk")
    conn.execute(
        "INSERT INTO feedback (id, user_id, rating, note, created_at)"
        " VALUES (?,?,?,?,?)",
        (feedback_id, user_id, rating, note, db.utcnow()),
    )
    conn.commit()
    return {"id": feedback_id, "rating": rating}


def progress_report(user_id: str) -> dict:
    """Progress reports & insights: one condensed view of how it's going."""
    conn = db.connect()
    moods = conn.execute(
        "SELECT COUNT(*) AS n, AVG(mood) AS mood, AVG(energy) AS energy"
        " FROM checkins WHERE user_id=?", (user_id,)).fetchone()
    detections = conn.execute(
        "SELECT severity, COUNT(*) AS n FROM events"
        " WHERE user_id=? AND type='detection' GROUP BY severity",
        (user_id,)).fetchall()
    fb = conn.execute(
        "SELECT rating, COUNT(*) AS n FROM feedback WHERE user_id=?"
        " GROUP BY rating", (user_id,)).fetchall()
    return {
        "checkins": {"count": moods["n"],
                     "avg_mood": round(moods["mood"], 2) if moods["mood"] else None,
                     "avg_energy": round(moods["energy"], 2) if moods["energy"] else None},
        "goals": [{"title": g["title"], "area": g["area"],
                   "progress": g["progress"], "status": g["status"]}
                  for g in goals(user_id)],
        "habits": [{"name": h["name"], "streak": h["streak"]}
                   for h in habits(user_id)],
        "detections": {r["severity"]: r["n"] for r in detections},
        "insights": len(insights(user_id)),
        "journal_entries": conn.execute(
            "SELECT COUNT(*) AS n FROM journal WHERE user_id=?",
            (user_id,)).fetchone()["n"],
        "feedback": {r["rating"]: r["n"] for r in fb},
    }


def provider_summary(user: dict) -> dict:
    """Consent-gated provider-portal view: condition-level facts only —
    no notes, no journal text, no raw biometrics."""
    conn = db.connect()
    user_id = user["id"]
    recent = conn.execute(
        "SELECT condition, severity, created_at FROM events"
        " WHERE user_id=? AND type='detection'"
        " ORDER BY created_at DESC, rowid DESC LIMIT 10", (user_id,)).fetchall()
    escalations = conn.execute(
        "SELECT COUNT(*) AS n FROM events WHERE user_id=? AND type='escalation'",
        (user_id,)).fetchone()["n"]
    moods = conn.execute(
        "SELECT AVG(mood) AS mood FROM checkins WHERE user_id=?",
        (user_id,)).fetchone()
    return {
        "user_id": user_id,
        "display_name": user["display_name"],
        "known_conditions": user["known_conditions"],
        "recent_detections": [dict(r) for r in recent],
        "escalations": escalations,
        "avg_mood": round(moods["mood"], 2) if moods["mood"] else None,
    }


# --------------------------------------------------------------------------- #
# access log — "see who accessed my data"
# --------------------------------------------------------------------------- #

_ACCESS_VERB = {"put": "stored", "get": "read", "delete": "erased"}


def access_log(user_id: str, pdi=None) -> dict:
    """A user-facing view of every access to *their* vaulted data. Reads PDI's
    tamper-evident audit chain and filters it to this user's key namespace
    (`jim/{user}/…`), so one user can never see another's. When no vault is
    configured, the user's data never left this system, and we say so."""
    if pdi is None:
        return {"vaulted": False, "entries": [],
                "note": "no vault configured — your data is stored locally on "
                        "this system only; nothing is shared externally"}
    raw = pdi.audit()
    if raw is None:
        return {"vaulted": True, "available": False,
                "note": "the vault audit is temporarily unavailable"}
    prefix = f"jim/{user_id}/"
    entries = []
    for e in raw:
        ref = e.get("ref") or ""
        if not ref.startswith(prefix):
            continue
        scope = ref[len(prefix):].rsplit("/", 1)[0] or "data"
        entries.append({"action": _ACCESS_VERB.get(e["action"], e["action"]),
                        "scope": scope, "at": e["at"]})
    return {
        "vaulted": True, "available": True,
        "tamper_evident": pdi.audit_verify(),
        "count": len(entries),
        "entries": entries,
        "note": "every access to your sealed data, verifiable against PDI's "
                "hash-chained audit log",
    }


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
                  "journal", "feedback", "vault_keys", "events",
                  "baselines", "trend_points", "medical_cards",
                  "tandem_links", "users"):
        deleted[table] = conn.execute(
            f"DELETE FROM {table} WHERE {'id' if table == 'users' else 'user_id'}=?",
            (user_id,),
        ).rowcount
    conn.commit()
    return {"deleted": deleted}
