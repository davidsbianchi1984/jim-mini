"""The far end of the ladder — a person, reached, or the truth that none is.

The escalation tree (:mod:`jim.escalation`) resolves a situation to a tier,
and ``notify_contact`` sits one rung below emergency services. For a long
time that rung was words: the guardian recorded ``notified_emergency_contact:
true`` whenever a phone number was on file, and nothing left the machine —
JIM cannot dial a phone. A health guardian that detects the crisis and then
whispers into an empty room is worse than one that says the room is empty.

    asked     does notify_contact notify a contact
    mattered  the ladder's whole promise is that it ends at a person

So this module gives the rung a real far end, three ways:

* **The alert.** When the tree says ``notify_contact`` or higher, the
  consented ``emergency_email`` gets a letter — condition, reason, tier, and
  an acknowledgment link. Clicking the link is the far end saying *a person
  has seen this*, and JIM records who was told, when, and when they answered.
  The token in the link is a single-purpose capability: it can mark exactly
  one alert as seen, and can read nothing.

* **The refusal.** With no consented address, the escalation result says so
  in the user's own language rather than pretending: there is no one on the
  far end of this today. An honest empty room can be fixed; a pretend
  notification cannot.

* **The liveness note.** Once a month the far end gets a short, useful note
  — what JIM watched, that nothing is asked of them — so a mailbox that has
  quietly died is discovered on a calm day instead of during an emergency.
  A backup you haven't restored from is a belief; an address you never
  write to is one too.

A crisis that keeps re-detecting does not flood the mailbox: while an
unacknowledged alert for the same condition is standing (half an hour), new
detections ride it — the far end was told, and telling them louder is not
telling them more.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone

from . import db, i18n, mailer

# A repeat detection of the same condition rides the standing alert this long
# (unless acknowledged sooner) instead of sending another mail.
STANDING_MINUTES = 30

# The liveness note's cadence. Monthly is often enough to catch a dead
# mailbox within one quarter and rare enough to stay a note, not noise.
PING_DAYS = 30


def address(user: dict | None) -> str | None:
    """The consented address JIM may write to, or None — consent covers the
    emergency contact as a whole, address and phone alike."""
    if user and user.get("contact_consent") and user.get("emergency_email"):
        return user["emergency_email"]
    return None


def _lang(user: dict | None) -> str:
    return (user or {}).get("language") or "en"


def notify(user_id: str, user: dict | None, condition: str, reason: str,
           severity: str, tier: str) -> dict:
    """Mail the far end about a detection, or say honestly that none exists.

    Returns the dict the escalation result carries as ``far_end`` —
    ``delivered`` is the honest flag: True only when a letter actually left
    (or one is already standing for this condition), never merely because a
    contact is on file, and never because one was printed on the server for
    want of a mail host. The console transport is a developer's terminal,
    not a person: it reaches nobody, so it reports ``delivered: False`` and
    says why in the wearer's language.
    """
    lang = _lang(user)
    to = address(user)
    if not to:
        return {"channel": None, "delivered": False, "standing": False,
                "note": i18n.farend_text("refusal", lang)}

    conn = db.connect()
    cutoff = (datetime.now(timezone.utc)
              - timedelta(minutes=STANDING_MINUTES)).isoformat()
    standing = conn.execute(
        "SELECT id FROM farend_alerts WHERE user_id=? AND condition=?"
        " AND acked_at IS NULL AND sent_at > ? ORDER BY sent_at DESC LIMIT 1",
        (user_id, condition, cutoff)).fetchone()
    if standing:
        return {"channel": "email", "delivered": True, "standing": True,
                "alert_id": standing["id"]}

    alert_id = db.new_id("fea")
    token = secrets.token_urlsafe(24)
    link = f"{mailer.public_url()}/farend/ack/{token}"
    name = user.get("display_name") or "the person you watch over"
    subject = i18n.farend_text("alert_subject", lang).format(name=name)
    body = i18n.farend_text("alert_body", lang).format(
        name=name, condition=condition, reason=reason, tier=tier, link=link)
    transport = mailer.deliver(to, subject, body)
    if transport != "smtp":
        # No mail server is configured, so deliver() printed the letter on
        # the server and returned. Nothing left the machine and nobody was
        # written to, and recording it would be two untruths rather than
        # one: `farend_alerts` is documented as one row per alert *actually
        # mailed* (jim/db.py), and a row here is what the standing check
        # reads — so a console print would ride as "already told" and
        # silence the next real detection for STANDING_MINUTES, including
        # one that could have left once mail was configured.
        return {"channel": "email", "delivered": False, "standing": False,
                "transport": transport,
                "note": i18n.farend_text("undelivered", lang)}
    conn.execute(
        "INSERT INTO farend_alerts (id, user_id, condition, severity, tier,"
        " sent_to, token, sent_at) VALUES (?,?,?,?,?,?,?,?)",
        (alert_id, user_id, condition, severity, tier, to, token, db.utcnow()))
    conn.commit()
    return {"channel": "email", "delivered": True, "standing": False,
            "alert_id": alert_id, "transport": transport}


def ack(token: str) -> dict | None:
    """The far end pressed the link. Returns what the thank-you page needs
    (in the wearer's language — the contact chose to stand beside them), or
    None for a token no alert ever carried."""
    conn = db.connect()
    row = conn.execute("SELECT * FROM farend_alerts WHERE token=?",
                       (token,)).fetchone()
    if row is None:
        return None
    user = conn.execute("SELECT * FROM users WHERE id=?",
                        (row["user_id"],)).fetchone()
    lang = _lang(dict(user) if user else None)
    if row["acked_at"]:
        return {"already": True, "lang": lang}
    conn.execute("UPDATE farend_alerts SET acked_at=? WHERE id=?",
                 (db.utcnow(), row["id"]))
    conn.commit()
    from . import guardian
    guardian._event(row["user_id"], "farend_ack", condition=row["condition"],
                    detail={"alert_id": row["id"],
                            "sent_at": row["sent_at"]})
    return {"already": False, "lang": lang}


def status(user_id: str, user: dict | None) -> dict:
    """What a console may say about the far end: configured or the refusal,
    the last alert and whether it was acknowledged — never the token."""
    lang = _lang(user)
    to = address(user)
    last = db.connect().execute(
        "SELECT condition, severity, tier, sent_at, acked_at"
        " FROM farend_alerts WHERE user_id=? ORDER BY sent_at DESC LIMIT 1",
        (user_id,)).fetchone()
    out = {"configured": bool(to), "address": to,
           "last_alert": dict(last) if last else None}
    if not to:
        out["note"] = i18n.farend_text("refusal", lang)
    return out


def liveness_pass(user_id: str, lang: str) -> dict | None:
    """The monthly proof-of-mailbox, ridden on the monitor sense the same way
    the calendar's reminder pass is: cheap to ask, sent at most once per
    :data:`PING_DAYS`. Returns what was sent, or None when nothing was due."""
    conn = db.connect()
    user_row = conn.execute("SELECT * FROM users WHERE id=?",
                            (user_id,)).fetchone()
    user = dict(user_row) if user_row else None
    to = address(user)
    if not to:
        return None
    if mailer.configured_transport() != "smtp":
        # The whole point of this note is to prove a mailbox is real. With
        # no mail server there is nothing to prove it against, and sending
        # anyway costs twice: this rides the monitor sense, so the console
        # banner would print on every reading, and the stamp below would
        # mark the far end pinged — so the note that could prove the
        # mailbox would not fall due again for PING_DAYS.
        return None
    last = (user or {}).get("farend_pinged_at")
    if last:
        try:
            sent = datetime.fromisoformat(last)
            if sent.tzinfo is None:
                sent = sent.replace(tzinfo=timezone.utc)
            if datetime.now(timezone.utc) - sent < timedelta(days=PING_DAYS):
                return None
        except ValueError:
            pass
    since = (datetime.now(timezone.utc)
             - timedelta(days=PING_DAYS)).isoformat()
    events = conn.execute(
        "SELECT COUNT(*) AS n FROM events WHERE user_id=? AND created_at > ?",
        (user_id, since)).fetchone()["n"]
    name = (user or {}).get("display_name") or "the person you watch over"
    subject = i18n.farend_text("ping_subject", lang).format(name=name)
    body = i18n.farend_text("ping_body", lang).format(
        name=name, days=PING_DAYS, events=events)
    transport = mailer.deliver(to, subject, body)
    conn.execute("UPDATE users SET farend_pinged_at=? WHERE id=?",
                 (db.utcnow(), user_id))
    conn.commit()
    from . import guardian
    guardian._event(user_id, "farend_ping",
                    detail={"events_counted": events, "transport": transport})
    return {"sent": True, "events": events, "transport": transport}
