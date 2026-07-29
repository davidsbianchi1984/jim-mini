"""The medicine cabinet — what you take, in your words, and whether you did.

Medication adherence is the highest-leverage health behavior a guardian
can support and the easiest to get wrong by overreaching. The boundaries
this module keeps, in order of importance:

* **JIM is not a pharmacist.** It records what the user tells it — name,
  dose, purpose, all free text in their words — and never pretends to a
  clinical judgment it cannot back. There is no interaction checker here,
  and rather than ship a toy one that would be trusted, the API says so:
  ask your pharmacist. The coach may discuss medications like anything
  else, under the same provenance and disclaimers as every reply.
* **A missed dose is a check-in, never an alarm.** Even a ``critical``
  medication missed produces a question on the board and a line in the
  coach's context — not an escalation, not a call to anyone. The
  escalation ladder remains reading-driven (jim/conditions.py) and this
  module has no path into it.
* **One slot, one answer, correctable.** "Did I take the 8am dose?" has
  exactly one answer per day; logging again replaces it (skipped →
  taken happens: people find the pill in their pocket). No duplicates,
  no double-counted adherence.
* **A dose logged is a sign of life.** Every log lands in the events
  table, which is exactly what the vigil (jim/vigil.py) measures silence
  against — so for the person whose only daily interaction is their
  pillbox, taking their medication quietly keeps the vigil stood down.

Time is the backend's local clock. This product's deployment story is a
machine in the user's own house; their pills and their computer keep the
same hours. A hosted deployment serving another timezone would need a
per-user offset — a column for another day, noted here so it is a known
absence rather than an oversight.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta

from . import db

# A slot is "due" this long before its time, and "missed" this long after.
# Generous on purpose: a guardian that calls 8:07 "missed" for the 8:00
# pill teaches the person to ignore the board.
_DUE_BEFORE = timedelta(minutes=60)
_GRACE_AFTER = timedelta(minutes=90)


class MedError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


def _valid_schedule(schedule: dict) -> dict:
    if not isinstance(schedule, dict):
        raise MedError(422, "schedule must be an object")
    if schedule.get("as_needed"):
        out = {"as_needed": True}
        if schedule.get("max_per_day") is not None:
            n = int(schedule["max_per_day"])
            if n < 1:
                raise MedError(422, "max_per_day must be at least 1")
            out["max_per_day"] = n
        return out
    times = schedule.get("times") or []
    cleaned = []
    for t in times:
        try:
            datetime.strptime(str(t).strip(), "%H:%M")
        except ValueError:
            raise MedError(422, f"schedule time {t!r} is not HH:MM")
        cleaned.append(str(t).strip())
    if not cleaned:
        raise MedError(422, "a schedule names times (e.g. ['08:00','20:00'])"
                            " or is {'as_needed': true}")
    return {"times": sorted(set(cleaned))}


def add(user_id: str, name: str, dose: str, schedule: dict,
        purpose: str | None = None, critical: bool = False,
        notes: str | None = None) -> dict:
    name, dose = (name or "").strip(), (dose or "").strip()
    if not name or not dose:
        raise MedError(422, "a medication has a name and a dose — your "
                            "words are fine ('the little white one, 10 mg')")
    sched = _valid_schedule(schedule)
    conn = db.connect()
    mid = db.new_id("med")
    now = db.utcnow()
    conn.execute(
        "INSERT INTO medications (id, user_id, name, dose, purpose, schedule,"
        " critical, notes, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (mid, user_id, name, dose, purpose, json.dumps(sched),
         int(bool(critical)), notes, now, now))
    conn.commit()
    return _out(_row(mid))


def _row(mid: str):
    return db.connect().execute(
        "SELECT * FROM medications WHERE id=?", (mid,)).fetchone()


def _own(user_id: str, mid: str):
    row = _row(mid)
    if row is None or row["user_id"] != user_id:
        raise MedError(404, "no such medication")
    return row


def _out(row) -> dict:
    return {"id": row["id"], "name": row["name"], "dose": row["dose"],
            "purpose": row["purpose"],
            "schedule": json.loads(row["schedule"]),
            "critical": bool(row["critical"]), "notes": row["notes"],
            "archived": bool(row["archived_at"]),
            "created_at": row["created_at"]}


def update(user_id: str, mid: str, **fields) -> dict:
    row = _own(user_id, mid)
    allowed = {}
    for key in ("name", "dose", "purpose", "notes"):
        if fields.get(key) is not None:
            allowed[key] = fields[key].strip() if key in ("name", "dose") \
                else fields[key]
    if fields.get("schedule") is not None:
        allowed["schedule"] = json.dumps(_valid_schedule(fields["schedule"]))
    if fields.get("critical") is not None:
        allowed["critical"] = int(bool(fields["critical"]))
    if not allowed:
        return _out(row)
    sets = ", ".join(f"{k}=?" for k in allowed)
    conn = db.connect()
    conn.execute(f"UPDATE medications SET {sets}, updated_at=? WHERE id=?",
                 (*allowed.values(), db.utcnow(), mid))
    conn.commit()
    return _out(_row(mid))


def archive(user_id: str, mid: str) -> dict:
    """Stopped, not deleted: the history of what was taken stays honest."""
    _own(user_id, mid)
    conn = db.connect()
    conn.execute("UPDATE medications SET archived_at=?, updated_at=?"
                 " WHERE id=?", (db.utcnow(), db.utcnow(), mid))
    conn.commit()
    return _out(_row(mid))


def cabinet(user_id: str, include_archived: bool = False) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM medications WHERE user_id=? ORDER BY created_at",
        (user_id,)).fetchall()
    return [_out(r) for r in rows
            if include_archived or not r["archived_at"]]


# --------------------------------------------------------------------------- #
# The day's board

def _logs_for_day(user_id: str, day: str) -> dict:
    rows = db.connect().execute(
        "SELECT * FROM med_logs WHERE user_id=? AND on_date=?",
        (user_id, day)).fetchall()
    by_slot = {}
    as_needed: dict[str, list] = {}
    for r in rows:
        if r["slot"]:
            by_slot[(r["med_id"], r["slot"])] = r
        else:
            as_needed.setdefault(r["med_id"], []).append(r)
    return {"slots": by_slot, "as_needed": as_needed}


def board(user_id: str, now: datetime | None = None) -> dict:
    """Today, medication by medication: what is done, due, still to come,
    and missed — with the grace a human deserves."""
    now = now or datetime.now()
    day = now.strftime("%Y-%m-%d")
    logs = _logs_for_day(user_id, day)
    entries, missed_critical = [], []
    for med in cabinet(user_id):
        sched = med["schedule"]
        if sched.get("as_needed"):
            takes = logs["as_needed"].get(med["id"], [])
            entry = {**med, "kind": "as_needed",
                     "taken_today": len([t for t in takes
                                         if t["action"] == "taken"]),
                     "max_per_day": sched.get("max_per_day")}
            entries.append(entry)
            continue
        slots = []
        for t in sched["times"]:
            slot_dt = datetime.strptime(f"{day} {t}", "%Y-%m-%d %H:%M")
            log = logs["slots"].get((med["id"], t))
            if log is not None:
                status = log["action"]                     # taken | skipped
            elif now < slot_dt - _DUE_BEFORE:
                status = "upcoming"
            elif now <= slot_dt + _GRACE_AFTER:
                status = "due"
            else:
                status = "missed"
            if status == "missed" and med["critical"]:
                missed_critical.append({"name": med["name"], "slot": t})
            slots.append({"slot": t, "status": status,
                          "note": log["note"] if log else None})
        entries.append({**med, "kind": "scheduled", "slots": slots})
    return {"date": day, "medications": entries,
            "missed_critical": missed_critical,
            # The honesty line every client shows next to the cabinet.
            "disclaimer": "JIM tracks what you tell it. It does not check "
                          "drug interactions — your pharmacist does that."}


def log(user_id: str, mid: str, action: str, slot: str | None = None,
        note: str | None = None, now: datetime | None = None) -> dict:
    if action not in ("taken", "skipped"):
        raise MedError(422, "action is 'taken' or 'skipped'")
    med = _own(user_id, mid)
    sched = json.loads(med["schedule"])
    now = now or datetime.now()
    day = now.strftime("%Y-%m-%d")
    conn = db.connect()
    if sched.get("as_needed"):
        if slot:
            raise MedError(422, "an as-needed medication has no slots")
        if action == "taken" and sched.get("max_per_day"):
            taken = conn.execute(
                "SELECT COUNT(*) AS n FROM med_logs WHERE med_id=? AND"
                " on_date=? AND action='taken'", (mid, day)).fetchone()["n"]
            if taken >= sched["max_per_day"]:
                raise MedError(409, f"you noted a ceiling of "
                                    f"{sched['max_per_day']} per day for "
                                    f"{med['name']} — this take would be "
                                    f"{taken + 1}. Logged nothing; if this "
                                    "is real, talk to your prescriber.")
    else:
        if not slot or slot not in sched["times"]:
            raise MedError(422, f"slot must be one of {sched['times']}")
        # One slot, one answer: logging again replaces the earlier answer.
        conn.execute("DELETE FROM med_logs WHERE med_id=? AND on_date=?"
                     " AND slot=?", (mid, day, slot))
    conn.execute(
        "INSERT INTO med_logs (id, user_id, med_id, action, slot, on_date,"
        " note, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (db.new_id("mlg"), user_id, mid, action, slot, day, note,
         db.utcnow()))
    # A dose logged is a sign of life — it lands in the events table, which
    # is what the vigil measures silence against. The pillbox keeps watch.
    conn.execute(
        "INSERT INTO events (id, user_id, type, condition, severity, detail,"
        " created_at) VALUES (?,?,?,?,?,?,?)",
        (db.new_id("evt"), user_id, "medication", None, "info",
         json.dumps({"medication": med["name"], "dose": med["dose"],
                     "action": action, "slot": slot,
                     **({"note": note} if note else {})}),
         db.utcnow()))
    conn.commit()
    from . import vigil
    vigil.note_signal(user_id)
    return board(user_id, now=now)


# --------------------------------------------------------------------------- #
# Adherence

def adherence(user_id: str, days: int = 7, now: datetime | None = None) -> dict:
    """Taken vs expected per scheduled medication, over whole past days
    (today is excluded — it is not finished, and counting an afternoon
    dose as missed at noon would poison the number)."""
    now = now or datetime.now()
    days = max(1, min(int(days), 90))
    start = (now - timedelta(days=days)).strftime("%Y-%m-%d")
    today = now.strftime("%Y-%m-%d")
    conn = db.connect()
    out = []
    for med in cabinet(user_id):
        sched = med["schedule"]
        if sched.get("as_needed"):
            continue
        created = med["created_at"][:10]
        expected = 0
        for i in range(1, days + 1):
            d = (now - timedelta(days=i)).strftime("%Y-%m-%d")
            if d >= created:
                expected += len(sched["times"])
        taken = conn.execute(
            "SELECT COUNT(*) AS n FROM med_logs WHERE med_id=? AND"
            " action='taken' AND on_date>=? AND on_date<?",
            (med["id"], start, today)).fetchone()["n"]
        out.append({"id": med["id"], "name": med["name"],
                    "expected": expected, "taken": min(taken, expected),
                    "rate": round(min(taken, expected) / expected, 2)
                    if expected else None})
    return {"days": days, "medications": out}


def coach_context(user_id: str, now: datetime | None = None) -> list[str]:
    """What the coach should know, one line each — a guardian who chats
    about your week without noticing you stopped your heart pills isn't
    paying attention. Context only: it informs the reply, it never alarms."""
    lines = []
    b = board(user_id, now=now)
    for miss in b["missed_critical"]:
        lines.append(f"missed a dose they marked critical today: "
                     f"{miss['name']} ({miss['slot']}) — worth asking about "
                     "gently, never scolding")
    week = adherence(user_id, days=7, now=now)
    for m in week["medications"]:
        if m["rate"] is not None and m["expected"] >= 3 and m["rate"] < 0.5:
            lines.append(f"medication adherence low this week: {m['name']} "
                         f"taken {m['taken']} of {m['expected']}")
    return lines
