"""The vigil — the alarm that fires when the signals *stop*.

Everything else in the Guardian fires on a reading: a heart rate that
climbed, an oxygen number that fell, a fall the watch felt. This module
answers the opposite and older question — the one a neighbour checking on
someone answers by knocking: **nothing has come from you in days; are you
there?**

A person living alone can be beyond every threshold this product watches
and still be fine; they can also be on the floor with the watch on the
charger, producing no readings at all, and every threshold is silent. The
vigil measures *silence itself* against the events table: any sign of
life — a drip from the watch, a typed reading, a check-in, a chat — is
already an event, so silence needs no bookkeeping and any activity resets
the clock without this module being told.

Design commitments, in the order they were argued:

* **The steward is chosen and worded in advance.** Who gets told, over
  which channel, and — ``note`` — what they are told, written by the user
  while they were fine. A vigil that composes its own message speaks for
  someone at the exact moment they cannot correct it.
* **It never escalates past the steward.** No emergency services, no
  escalation ladder. Silence is weak evidence; the correct response is a
  person who cares knocking on a door, not an ambulance. The clinical
  ladder (jim/conditions.py, jim/escalation.py) remains reading-driven
  and unchanged.
* **Tripping is idempotent and recovery is automatic.** ``sweep`` may be
  called by anything, any number of times — the console on open, a
  sibling product, a cron — and trips at most once per silence. The next
  reading resolves it (``note_signal``, called from the Guardian's ingest
  path), because the person showing up *is* the all-clear.
* **If mail is configured the steward is actually emailed**; if not, the
  trip is an event the console shows loudly. Degrade, never pretend.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from . import db


class VigilError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


def _row(user_id: str):
    return db.connect().execute(
        "SELECT * FROM vigils WHERE user_id=?", (user_id,)).fetchone()


def arm(user_id: str, steward_name: str, steward_channel: str,
        quiet_days: float = 3.0, note: str | None = None) -> dict:
    steward_name = (steward_name or "").strip()
    steward_channel = (steward_channel or "").strip()
    if not steward_name or not steward_channel:
        raise VigilError(422, "a vigil needs a steward's name and a way to "
                              "reach them")
    if not (0.5 <= float(quiet_days) <= 60):
        raise VigilError(422, "quiet_days must be between half a day and 60")
    conn = db.connect()
    conn.execute(
        "INSERT INTO vigils (user_id, steward_name, steward_channel,"
        " quiet_days, note, enabled, created_at, updated_at)"
        " VALUES (?,?,?,?,?,1,?,?)"
        " ON CONFLICT(user_id) DO UPDATE SET steward_name=excluded.steward_name,"
        " steward_channel=excluded.steward_channel,"
        " quiet_days=excluded.quiet_days, note=excluded.note, enabled=1,"
        " updated_at=excluded.updated_at",
        (user_id, steward_name, steward_channel, float(quiet_days), note,
         db.utcnow(), db.utcnow()))
    conn.commit()
    return status(user_id)


def disarm(user_id: str) -> dict:
    conn = db.connect()
    conn.execute("UPDATE vigils SET enabled=0, updated_at=? WHERE user_id=?",
                 (db.utcnow(), user_id))
    conn.commit()
    return status(user_id)


def _last_heard(user_id: str) -> str | None:
    # The vigil's own trip is an event too — and it must not count as a sign
    # of life, or every trip would reset the very silence it measured.
    row = db.connect().execute(
        "SELECT created_at FROM events WHERE user_id=? AND type != 'vigil'"
        " ORDER BY created_at DESC, rowid DESC LIMIT 1", (user_id,)).fetchone()
    return row["created_at"] if row else None


def _hours_since(iso: str | None) -> float | None:
    if not iso:
        return None
    then = datetime.fromisoformat(iso)
    if then.tzinfo is None:
        then = then.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - then).total_seconds() / 3600


def status(user_id: str) -> dict:
    row = _row(user_id)
    if row is None:
        return {"armed": False}
    last = _last_heard(user_id)
    silent = _hours_since(last)
    threshold = row["quiet_days"] * 24
    return {
        "armed": bool(row["enabled"]),
        "steward_name": row["steward_name"],
        "steward_channel": row["steward_channel"],
        "quiet_days": row["quiet_days"],
        "note": row["note"],
        "last_heard_at": last,
        "silent_hours": round(silent, 1) if silent is not None else None,
        "threshold_hours": threshold,
        "tripped": bool(row["tripped_at"]) and not row["resolved_at"],
        "tripped_at": row["tripped_at"],
        "resolved_at": row["resolved_at"],
    }


def sweep(user_id: str) -> dict:
    """Check the silence; trip at most once. Safe to call from anywhere,
    any number of times."""
    from . import guardian, mailer
    row = _row(user_id)
    st = status(user_id)
    if row is None or not row["enabled"] or st["tripped"]:
        return st
    silent = st["silent_hours"]
    if silent is None or silent < st["threshold_hours"]:
        return st
    user = guardian.get_user(user_id) or {}
    name = user.get("display_name", "someone you care about")
    body = (f"This is {name}'s JIM Guardian. Nothing has been heard from "
            f"them for {round(silent / 24, 1)} days — no readings, no "
            "check-ins. That is longer than the quiet period they chose "
            "when they named you their steward.")
    if row["note"]:
        body += f"\n\nIn their own words: {row['note']}"
    body += ("\n\nThis is not an emergency alert — no reading triggered "
             "it. It is the absence of readings. Please check on them.")
    delivery = "console"
    if mailer.configured_transport() == "smtp" and "@" in row["steward_channel"]:
        try:
            mailer.deliver(row["steward_channel"],
                           f"Please check on {name}", body)
            delivery = "email"
        except Exception:  # noqa: BLE001 — the trip still stands, undelivered
            delivery = "email_failed"
    conn = db.connect()
    now = db.utcnow()
    conn.execute(
        "UPDATE vigils SET tripped_at=?, resolved_at=NULL, updated_at=?"
        " WHERE user_id=?", (now, now, user_id))
    conn.execute(
        "INSERT INTO events (id, user_id, type, condition, severity, detail,"
        " created_at) VALUES (?,?,?,?,?,?,?)",
        (db.new_id("evt"), user_id, "vigil", "silence", "alert",
         json.dumps({"steward": row["steward_name"],
                        "delivery": delivery,
                        "silent_hours": round(silent, 1),
                        "message": body}),
         now))
    conn.commit()
    return status(user_id)


def note_signal(user_id: str) -> None:
    """A sign of life arrived. Resolve a tripped vigil — the person showing
    up is the all-clear. Called from the Guardian's ingest path; cheap
    no-op when nothing is tripped."""
    row = _row(user_id)
    if row is None or not row["tripped_at"] or row["resolved_at"]:
        return
    conn = db.connect()
    conn.execute(
        "UPDATE vigils SET resolved_at=?, updated_at=? WHERE user_id=?",
        (db.utcnow(), db.utcnow(), user_id))
    conn.commit()


def resolve(user_id: str) -> dict:
    """The "I'm okay" button."""
    conn = db.connect()
    conn.execute(
        "UPDATE vigils SET resolved_at=?, updated_at=? WHERE user_id=?"
        " AND tripped_at IS NOT NULL",
        (db.utcnow(), db.utcnow(), user_id))
    conn.commit()
    return status(user_id)
