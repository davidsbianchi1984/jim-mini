"""The crash watch — when the person cannot answer.

The vigil (:mod:`jim.vigil`) measures silence in *days* and wakes a
steward, never an ambulance, because slow silence is weak evidence. This
module is its acute sibling, for the scenario silence-in-days cannot
catch: a crash, a collapse — the pulse goes shallow while the person goes
quiet, *right now*. The Guardian asks "are you okay?"; when too many of
those questions go unanswered, a person who pre-authorized it gets help
sent, not another question.

Design commitments, argued in the same order the vigil's were:

* **Programmed in advance, by the user, off by default.** Who gets
  contacted (a trusted person, and — only if the box was ticked —
  emergency services), how many unanswered attempts is too many, and how
  long each attempt waits. Consent is the arming, and it happens while the
  person is fine. Nothing here fires for a user who never armed it.
* **It fires on evidence stacked three deep**: an alarming reading (the
  clinical detector already called it critical), then repeated
  questions, then silence through all of them. A single missed ping is a
  phone left in a jacket; N missed pings *while the pulse looks wrong* is
  the emergency this exists for.
* **Any sign of the person ends it.** The "I'm okay" button or a normal
  reading — the person (or their body) reporting in is the all-clear, and
  it resolves a trip too, same as the vigil. A concerning reading does
  not count: a stream of bad readings is the emergency continuing, not
  an answer.
* **Degrade, never pretend.** This app cannot dial 911. If mail is
  configured, the trusted contact is actually emailed; the
  emergency-services step is recorded as a dispatch *request* the console
  shows loudly and connected systems relay — and the wording never claims
  a call was placed when one wasn't.
* **The drift bands stay calm.** A band crossing is still a question and
  never opens a crash concern; only the clinical detector's critical
  findings do. A drift notice that could summon an ambulance would
  just be a jumpier alarm with a softer name (jim/bands.py said so first).
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from . import db

# The one severity that opens a concern: the clinical detector's
# "critical" — the severity that already escalates. Never "guidance"
# (advice, not an emergency) and never the bands' calm "checkin".
CONCERNING = {"critical"}
MAX_ATTEMPTS_CAP = 10
MIN_WINDOW_MINUTES = 1.0
MAX_WINDOW_MINUTES = 60.0


class CrashWatchError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


def _row(user_id: str):
    return db.connect().execute(
        "SELECT * FROM crash_watches WHERE user_id=?", (user_id,)).fetchone()


def arm(user_id: str, trusted_name: str, trusted_channel: str,
        attempts: int = 3, window_minutes: float = 5.0,
        contact_emergency_services: bool = False) -> dict:
    """Arm the watch — the consent moment. The user writes down, while they
    are fine, who is called for them when they cannot answer."""
    trusted_name = (trusted_name or "").strip()
    trusted_channel = (trusted_channel or "").strip()
    if not trusted_name or not trusted_channel:
        raise CrashWatchError(
            422, "the crash watch needs a trusted person's name and a way "
                 "to reach them")
    if not (1 <= int(attempts) <= MAX_ATTEMPTS_CAP):
        raise CrashWatchError(
            422, f"attempts must be between 1 and {MAX_ATTEMPTS_CAP}")
    if not (MIN_WINDOW_MINUTES <= float(window_minutes) <= MAX_WINDOW_MINUTES):
        raise CrashWatchError(
            422, "window_minutes must be between "
                 f"{MIN_WINDOW_MINUTES:g} and {MAX_WINDOW_MINUTES:g}")
    conn = db.connect()
    conn.execute(
        "INSERT INTO crash_watches (user_id, trusted_name, trusted_channel,"
        " attempts, window_minutes, contact_ems, enabled, created_at,"
        " updated_at) VALUES (?,?,?,?,?,?,1,?,?)"
        " ON CONFLICT(user_id) DO UPDATE SET"
        " trusted_name=excluded.trusted_name,"
        " trusted_channel=excluded.trusted_channel,"
        " attempts=excluded.attempts,"
        " window_minutes=excluded.window_minutes,"
        " contact_ems=excluded.contact_ems, enabled=1,"
        " updated_at=excluded.updated_at",
        (user_id, trusted_name, trusted_channel, int(attempts),
         float(window_minutes), int(bool(contact_emergency_services)),
         db.utcnow(), db.utcnow()))
    conn.commit()
    return status(user_id)


def disarm(user_id: str) -> dict:
    conn = db.connect()
    conn.execute(
        "UPDATE crash_watches SET enabled=0, concern_opened_at=NULL,"
        " attempt=0, deadline_at=NULL, updated_at=? WHERE user_id=?",
        (db.utcnow(), user_id))
    conn.commit()
    return status(user_id)


def _now(now: datetime | None) -> datetime:
    return now or datetime.now(timezone.utc)


def _parse(iso: str | None) -> datetime | None:
    if not iso:
        return None
    t = datetime.fromisoformat(iso)
    return t.replace(tzinfo=timezone.utc) if t.tzinfo is None else t


def status(user_id: str) -> dict:
    row = _row(user_id)
    if row is None:
        return {"armed": False}
    return {
        "armed": bool(row["enabled"]),
        "trusted_name": row["trusted_name"],
        "trusted_channel": row["trusted_channel"],
        "attempts": row["attempts"],
        "window_minutes": row["window_minutes"],
        "contact_emergency_services": bool(row["contact_ems"]),
        # The live question, when one is open: the console renders this as
        # the big "I'm okay" button.
        "asking": bool(row["concern_opened_at"]) and not row["tripped_at"],
        "attempt": row["attempt"],
        "deadline_at": row["deadline_at"],
        "concern": row["concern"],
        "tripped": bool(row["tripped_at"]) and not row["resolved_at"],
        "tripped_at": row["tripped_at"],
        "resolved_at": row["resolved_at"],
    }


def note_concern(user_id: str, condition: str, severity: str,
                 now: datetime | None = None) -> None:
    """An alarming reading arrived. Open the question (attempt 1) if the
    watch is armed and no question is already open. Called from the
    Guardian's ingest path; cheap no-op otherwise."""
    if severity not in CONCERNING:
        return
    row = _row(user_id)
    if row is None or not row["enabled"] or row["concern_opened_at"]:
        return
    t = _now(now)
    deadline = t + timedelta(minutes=row["window_minutes"])
    conn = db.connect()
    conn.execute(
        "UPDATE crash_watches SET concern_opened_at=?, concern=?, attempt=1,"
        " deadline_at=?, tripped_at=NULL, resolved_at=NULL, updated_at=?"
        " WHERE user_id=?",
        (t.isoformat(), condition, deadline.isoformat(), db.utcnow(),
         user_id))
    conn.execute(
        "INSERT INTO events (id, user_id, type, condition, severity, detail,"
        " created_at) VALUES (?,?,?,?,?,?,?)",
        (db.new_id("evt"), user_id, "crash_watch", condition, "asking",
         json.dumps({"attempt": 1, "of": row["attempts"],
                     "deadline_at": deadline.isoformat(),
                     "question": "JIM is asking: are you okay?"}),
         db.utcnow()))
    conn.commit()


def respond(user_id: str) -> dict:
    """The person answered — the button, a chat, any deliberate act. Close
    the question and resolve any trip. The all-clear, from the only voice
    that can give it."""
    row = _row(user_id)
    if row is None:
        return status(user_id)
    conn = db.connect()
    conn.execute(
        "UPDATE crash_watches SET concern_opened_at=NULL, concern=NULL,"
        " attempt=0, deadline_at=NULL,"
        " resolved_at=CASE WHEN tripped_at IS NOT NULL THEN ? ELSE resolved_at END,"
        " updated_at=? WHERE user_id=?",
        (db.utcnow(), db.utcnow(), user_id))
    conn.commit()
    return status(user_id)


def note_signal(user_id: str, severity: str | None = None) -> None:
    """A reading arrived. A *normal* one answers the question — the person's
    body reporting in counts. A concerning one does not: a stream of bad
    readings is the emergency continuing, not an answer."""
    if severity in CONCERNING:
        return
    row = _row(user_id)
    if row is None or (not row["concern_opened_at"] and not row["tripped_at"]):
        return
    respond(user_id)


def sweep(user_id: str, now: datetime | None = None) -> dict:
    """Advance the clock. Re-ask when a deadline passed; trip when the last
    allowed attempt passed unanswered. Safe to call from anywhere, any
    number of times — the console poll, the ingest path, a status read."""
    row = _row(user_id)
    st = status(user_id)
    if (row is None or not row["enabled"] or not row["concern_opened_at"]
            or row["tripped_at"]):
        return st
    t = _now(now)
    # Deadlines march window-by-window from the moment the concern opened —
    # never re-anchored to "now", or a long gap (the sweeper waking after a
    # crash is exactly a long gap) could only ever consume one attempt.
    conn = db.connect()
    while True:
        row = _row(user_id)
        deadline = _parse(row["deadline_at"])
        if deadline is None or t < deadline:
            return status(user_id)
        if row["attempt"] >= row["attempts"]:
            return _trip(user_id, row, t)
        next_deadline = deadline + timedelta(minutes=row["window_minutes"])
        conn.execute(
            "UPDATE crash_watches SET attempt=attempt+1, deadline_at=?,"
            " updated_at=? WHERE user_id=?",
            (next_deadline.isoformat(), db.utcnow(), user_id))
        conn.execute(
            "INSERT INTO events (id, user_id, type, condition, severity,"
            " detail, created_at) VALUES (?,?,?,?,?,?,?)",
            (db.new_id("evt"), user_id, "crash_watch", row["concern"],
             "asking",
             json.dumps({"attempt": row["attempt"] + 1, "of": row["attempts"],
                         "deadline_at": next_deadline.isoformat(),
                         "question": "JIM is asking again: are you okay?"}),
             db.utcnow()))
        conn.commit()


def _trip(user_id: str, row, t: datetime) -> dict:
    from . import guardian, mailer
    user = guardian.get_user(user_id) or {}
    name = user.get("display_name", "someone you care about")
    body = (f"This is {name}'s JIM Guardian. An alarming reading came in "
            f"({row['concern']}), JIM asked \"are you okay?\" "
            f"{row['attempts']} time(s) over "
            f"{row['attempts'] * row['window_minutes']:g} minutes, and "
            "nothing answered — no button, no message, no normal reading. "
            "They armed this watch themselves and asked that you be "
            "contacted when exactly this happens. Please treat it as real "
            "until they tell you otherwise.")
    delivery = "console"
    if mailer.configured_transport() == "smtp" and "@" in row["trusted_channel"]:
        try:
            mailer.deliver(row["trusted_channel"],
                           f"{name} is not answering — please act", body)
            delivery = "email"
        except Exception:  # noqa: BLE001 — the trip still stands, undelivered
            delivery = "email_failed"
    # Autonomous coordinated response, same as the clinical ladder: every
    # connected system the user registered relays the alert, so whichever
    # is nearest can surface it — or a human near it can act.
    dispatched = [d["name"] for d in guardian.devices_for(user_id)]
    detail = {
        "trusted": row["trusted_name"], "delivery": delivery,
        "concern": row["concern"],
        "unanswered_attempts": row["attempts"],
        "dispatched_alerts": dispatched,
        "message": body,
        # Recorded as a *request*, in words that stay honest about what a
        # local app can and cannot do — see the module docstring.
        "emergency_services": (
            {"requested": True,
             "note": "dispatch requested via every connected system; this "
                     "app cannot itself place a call"}
            if row["contact_ems"] else {"requested": False}),
    }
    conn = db.connect()
    now_iso = db.utcnow()
    conn.execute(
        "UPDATE crash_watches SET tripped_at=?, resolved_at=NULL,"
        " concern_opened_at=NULL, deadline_at=NULL, updated_at=?"
        " WHERE user_id=?", (t.isoformat(), now_iso, user_id))
    conn.execute(
        "INSERT INTO events (id, user_id, type, condition, severity, detail,"
        " created_at) VALUES (?,?,?,?,?,?,?)",
        (db.new_id("evt"), user_id, "crash_watch", row["concern"], "alert",
         json.dumps(detail), now_iso))
    conn.commit()
    return status(user_id)
