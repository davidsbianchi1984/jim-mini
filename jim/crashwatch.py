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

## The collapse path, framed

The trip used to decide its own tier — ``"emergency_services" if the box was
ticked else "notify_contact"`` — while every other way this product summons
help went through :func:`jim.escalation.decide` and came back with a ``path``
that can be replayed and defended. The one path where the person cannot
speak for themselves was the one with no reasoning on the record.

    asked     what tier did the trip reach
    mattered  why, in words somebody can argue with afterwards

It goes through the ladder now, and the ladder gives the same answer it
always did — deliberately, because this is not new behaviour, it is the
existing behaviour with its argument attached. Two choices are worth stating:

* **Sensitivity is pinned at balanced.** The dial governs how eagerly JIM
  escalates a *reading*. This is not a reading; it is a standing instruction
  the person wrote down while they were fine, and a preference about jumpiness
  must not quietly raise or lower what they asked for.
* **The arming is a ceiling, not a floor.** A person who did not tick
  emergency services gets ``notify_contact`` — as a *clipped* decision, so
  the result says out loud that a floor was cut and hands the need to the
  human standing there, exactly as an anonymous beacon alarm does.

And the sentence. The bystander's path has told a stranger to dial the number
themselves since it shipped; the collapse path — the acute one, the one this
module exists for — told the trusted contact to "treat it as real" and stopped
there. :data:`DIAL_YOURSELF` now ends every page the trip sends, on both
settings of the box, because the box changes whether a dispatch *request* goes
out to connected systems and changes nothing about whether a call was placed.
The tick is the moment the product most looks like it called for help, so it
is the moment the sentence matters most.
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

#: The one sentence that helps, in the wording jim/beacons.py uses on the
#: stranger's page, aimed at the surface this one lands on. It ends every page
#: the trip sends — the trusted contact reading it at 3am is the only person
#: in this story who can actually reach a dispatcher.
DIAL_YOURSELF = ("If you believe this is an emergency, call your local "
                 "emergency number yourself; this app cannot call anyone.")

#: Why the sentence is there, in each of the two ways the watch can be armed.
#: The ticked box is the one that most needs it: a dispatch *request* relayed
#: to connected systems is the thing that most looks like a call being placed.
#:
#: Written without "you", because this text has two readers — the trusted
#: contact opening a page at 3am, and whoever is looking at the alarm queue.
#: The two are rarely the same person and the sentence has to be true for both.
WHY_DIAL = {
    True: ("A dispatch request went out to every connected system. No call "
           "was placed from here."),
    False: ("This watch was armed to reach a trusted contact, not emergency "
            "services."),
}

#: The tier a trip may not exceed when the person did not pre-authorize the
#: emergency-services step. Their arming is a ceiling on their own behalf —
#: the same mechanic jim/beacons.py uses for a stranger, for a different
#: reason: there, the caller has no standing; here, the caller left standing
#: instructions and this is what they said.
UNTICKED_CEILING = "notify_contact"


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
        "accepted_by": row["accepted_by"],
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


def _decide(row) -> dict:
    """The trip's tier, from the ladder rather than from an ``if``.

    Called by both :func:`_trip` and :func:`as_alarm` so the queue and the
    record cannot drift apart — there is no ``tier`` column, and a second
    place computing one is how they would.

    ``sensitivity`` is deliberately not read off the user. See the module
    docstring: the dial is about readings, this is a standing instruction.
    """
    from . import escalation
    return escalation.decide(
        "critical", "balanced",
        contactable=bool(row["trusted_channel"]),
        ceiling=None if row["contact_ems"] else UNTICKED_CEILING)


def _trip(user_id: str, row, t: datetime) -> dict:
    from . import guardian, mailer
    user = guardian.get_user(user_id) or {}
    name = user.get("display_name", "someone you care about")
    decision = _decide(row)
    body = (f"This is {name}'s JIM Guardian. An alarming reading came in "
            f"({row['concern']}), JIM asked \"are you okay?\" "
            f"{row['attempts']} time(s) over "
            f"{row['attempts'] * row['window_minutes']:g} minutes, and "
            "nothing answered — no button, no message, no normal reading. "
            "They armed this watch themselves and asked that you be "
            "contacted when exactly this happens. Please treat it as real "
            "until they tell you otherwise.\n\n"
            f"{WHY_DIAL[bool(row['contact_ems'])]} {DIAL_YOURSELF}")
    delivery = "console"
    if mailer.configured_transport() == "smtp" and "@" in row["trusted_channel"]:
        try:
            mailer.deliver(row["trusted_channel"],
                           f"{name} is not answering — please act", body)
            delivery = "email"
        except Exception:  # noqa: BLE001 — the trip still stands, undelivered
            delivery = "email_failed"
    # The page lands in the same ledger the workplace relay writes, so
    # "What went out" shows the crash watch's pages beside everybody
    # else's — a message that failed to deliver is the one the morning
    # most needs to know about.
    _record_page(user_id, row["trusted_name"], delivery)
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
        # The ladder's own reasoning, kept so this decision can be replayed
        # and argued with — every other escalation in this product records
        # one, and the path where the person cannot speak recorded none.
        "tier": decision["tier"],
        "clipped_by_ceiling": decision["clipped_by_ceiling"],
        "escalation_path": decision["path"],
        # True on both settings of the box: what the tick changes is whether
        # a dispatch request is relayed, not whether a call was placed.
        "call_emergency_services_yourself": True,
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


# -- the trip on the Needs-a-person queue -------------------------------------

#: The id a tripped watch answers to on the alarm queue. A constant rather
#: than a row id: one watch per user means at most one open crash alarm,
#: and a name says what it is on every client that renders it.
ALARM_ID = "crash-watch"


def as_alarm(user_id: str) -> dict | None:
    """The tripped watch, shaped like an alarm.

    The trip used to be fire-and-forget: one email to the trusted contact
    and a dispatch request, with nobody ever confirming a human is coming —
    while the Needs-a-person queue sat one screen up with exactly the
    accept-by-name loop this needs, fed only by beacon alarms. Shaping the
    trip as an alarm row puts every way help gets summoned on one answering
    surface, worked with the doors that already exist on every client.
    """
    row = _row(user_id)
    if row is None or not row["tripped_at"] or row["resolved_at"]:
        return None
    decision = _decide(row)
    return {
        "id": ALARM_ID,
        "beacon_id": None,
        "kind": "crash_watch",
        # Plain strings, because that is what this queue's messages are —
        # every finder's words on a beacon alarm are strings, and every
        # shell decodes exactly that. The first version of this row carried
        # {from, text} objects and would have failed the whole alarm-list
        # decode on every phone the moment a trip was live.
        "messages": [
            (f"an alarming reading ({row['concern']}) went unanswered "
             f"through {row['attempts']} check-in(s); "
             f"{row['trusted_name']} was contacted"),
            # The dial sentence rides in `messages` and not only in a new
            # field, so it reaches a client that has never heard of the field
            # — every shell already renders these strings. The field below is
            # for the ones that want to render it like what it is.
            f"{WHY_DIAL[bool(row['contact_ems'])]} {DIAL_YOURSELF}",
        ],
        "state": "open",
        # From the ladder, not from an `if` on the tick. It answers the same
        # tier the `if` did; what is new is that it can say why.
        "tier": decision["tier"],
        "clipped_by_ceiling": decision["clipped_by_ceiling"],
        "call_emergency_services_yourself": True,
        "accepted_by": row["accepted_by"],
        "created_at": row["tripped_at"],
        "cleared_at": None,
    }


def accept_alarm(user_id: str, responder: str) -> dict | None:
    """A human takes the trip. Accepting says somebody is coming; clearing
    says it is over — the relay's distinction, kept on this queue too."""
    if not responder.strip():
        raise CrashWatchError(
            422, "a responder needs a name — 'someone accepted it' is the "
                 "thing this loop exists to stop being enough")
    if as_alarm(user_id) is None:
        return None
    conn = db.connect()
    now = db.utcnow()
    conn.execute(
        "UPDATE crash_watches SET accepted_by=?, accepted_at=?, updated_at=?"
        " WHERE user_id=?", (responder.strip(), now, now, user_id))
    conn.commit()
    from . import guardian
    guardian._event(user_id, "crash_watch",
                    detail={"alarm": ALARM_ID,
                            "accepted_by": responder.strip()})
    return {"alarm": ALARM_ID, "accepted_by": responder.strip(),
            "state": "open"}


def clear_alarm(user_id: str) -> dict | None:
    """A responder says it is over. Resolves the trip the way the person's
    own "I'm okay" would — the difference is who said it, and the
    acceptance record keeps that difference legible."""
    if as_alarm(user_id) is None:
        return None
    conn = db.connect()
    now = db.utcnow()
    conn.execute(
        "UPDATE crash_watches SET resolved_at=?, updated_at=? WHERE user_id=?",
        (now, now, user_id))
    conn.commit()
    return {"id": ALARM_ID, "state": "cleared"}


def escalate_alarm(user_id: str) -> dict | None:
    """Page the trusted channel again. The workplace relay works a roster;
    a personal deployment has one trusted person, so escalating means the
    one page is not the only page."""
    row = _row(user_id)
    if as_alarm(user_id) is None:
        return None
    from . import guardian, mailer
    user = guardian.get_user(user_id) or {}
    name = user.get("display_name", "someone you care about")
    delivery = "console"
    if mailer.configured_transport() == "smtp" and "@" in row["trusted_channel"]:
        try:
            mailer.deliver(
                row["trusted_channel"],
                f"{name} is still not answering — please act",
                f"This is {name}'s JIM Guardian, paging again: the crash "
                f"watch tripped ({row['concern']}) and nobody has confirmed "
                "they are going. Please treat it as real until they tell "
                f"you otherwise.\n\n{DIAL_YOURSELF}")
            delivery = "email"
        except Exception:  # noqa: BLE001 — the escalation still stands
            delivery = "email_failed"
    _record_page(user_id, row["trusted_name"], delivery)
    return {"alarm": ALARM_ID, "re_paged": row["trusted_name"],
            "delivery": delivery}


def _record_page(user_id: str, responder: str, delivery: str) -> None:
    """One row in the ledger the relay writes. `alarm_id` carries the
    constant — this schema's foreign keys are declarative, and the pages
    list is a flat read."""
    conn = db.connect()
    now = db.utcnow()
    conn.execute(
        "INSERT INTO relay_pages (id, alarm_id, user_id, responder, role,"
        " on_shift, state, attempts, last_error, created_at, sent_at)"
        " VALUES (?,?,?,?,?,1,?,1,NULL,?,?)",
        (db.new_id("page"), ALARM_ID, user_id, responder, "trusted contact",
         "sent" if delivery == "email"
         else ("failed" if delivery == "email_failed" else "queued"),
         now, now if delivery == "email" else None))
    conn.commit()
