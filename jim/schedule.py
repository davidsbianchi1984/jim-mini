"""Booking and scheduling: the Guardian keeps the calendar, quietly.

Three rules, in the order a person meets them:

1. **A booking is a row, not a hostage.** An appointment is a title, a
   time, and optionally where — cancellable in one press. Booking a shop
   *service* is one act: the order goes through `jim/shopping.py` under
   all four of its rules (the interactor signs, the receipt stays here),
   and the appointment carries the receipt so cancelling the booking
   while the order is still `placed` hands the order back too.
2. **Reminders ride the proactive ladder, at its bottom rung.** An
   appointment inside the reminder window becomes a guardian event at
   `checkin` severity and an insight — a question on the Home feed, never
   an alarm. However missed, a haircut does not ring a phone. Each
   appointment reminds once (``reminded_at``), on whatever sense fires
   first — the pass hangs off the monitor and observe paths the way the
   money check does, so there is no scheduler to run and nothing new to
   deploy.
3. **Email goes to the user, or nowhere.** With ``email_reminder`` opted
   in at booking, the reminder is also mailed — to the verified address
   that owns this user's account, and to no other address, structurally:
   the recipient is looked up, never passed in. A user with no verified
   email simply gets no mail, and the view says so rather than failing.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from . import db, i18n, shopping

#: How far ahead the bottom rung looks. A day is enough to act on and
#: short enough that the reminder still means "soon".
REMIND_WINDOW_HOURS = 24


class ScheduleError(ValueError):
    pass


def _parse_when(when: str) -> datetime:
    try:
        moment = datetime.fromisoformat(when)
    except ValueError:
        raise ScheduleError(
            "when is an ISO timestamp, e.g. 2026-08-05T15:00:00+00:00")
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    if moment <= datetime.now(timezone.utc):
        raise ScheduleError("that time has already passed")
    return moment


def book(user_id: str, user: dict, title: str, when: str,
         where: str | None = None, email_reminder: bool = False,
         shop_id: str | None = None, offering_id: str | None = None,
         qrme=None) -> dict:
    """One act: the appointment, and — when a shop service is named — the
    order that goes with it, placed under shopping's own rules."""
    if not (title or "").strip():
        raise ScheduleError("an appointment needs a title you will "
                            "recognise")
    moment = _parse_when(when)

    receipt_order = None
    if shop_id or offering_id:
        if not (shop_id and offering_id):
            raise ScheduleError("booking a service names both the shop and "
                                "the offering")
        placed = shopping.order(user_id, user, shop_id, offering_id, 1,
                                qrme=qrme)
        receipt_order = placed["id"]

    conn = db.connect()
    appointment_id = db.new_id("apt")
    conn.execute(
        "INSERT INTO appointments (id, user_id, title, whenat, whereat,"
        " email_reminder, qrme_order_id, status, reminded_at, created_at)"
        " VALUES (?,?,?,?,?,?,?,'booked',NULL,?)",
        (appointment_id, user_id, title.strip(), moment.isoformat(),
         where, 1 if email_reminder else 0, receipt_order, db.utcnow()))
    conn.commit()
    return appointment(appointment_id)


def appointment(appointment_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM appointments WHERE id=?", (appointment_id,)).fetchone()
    if row is None:
        raise ScheduleError("no such appointment")
    return dict(row)


def cancel(user_id: str, appointment_id: str, qrme=None) -> dict:
    """One press. A linked order still sitting at `placed` is handed back
    through shopping's own cancel — the buyer's exit, not a new one."""
    row = appointment(appointment_id)
    if row["user_id"] != user_id:
        raise ScheduleError("that appointment is somebody else's")
    if row["status"] == "cancelled":
        return row
    if row["qrme_order_id"]:
        try:
            shopping.cancel(user_id, row["qrme_order_id"], qrme=qrme)
        except shopping.ShoppingError:
            # The order was already past `placed` (or the tandem is down).
            # The appointment still cancels — the person is not coming —
            # and the receipt keeps whatever state the shop last confirmed.
            pass
    conn = db.connect()
    conn.execute("UPDATE appointments SET status='cancelled' WHERE id=?",
                 (appointment_id,))
    conn.commit()
    return appointment(appointment_id)


def upcoming(user_id: str) -> list[dict]:
    return [dict(r) for r in db.connect().execute(
        "SELECT * FROM appointments WHERE user_id=? AND status='booked'"
        " ORDER BY whenat", (user_id,)).fetchall()]


def _user_email(user_id: str) -> str | None:
    """The one address a reminder may go to: the verified account that owns
    this user. Looked up, never passed in — that is rule 3."""
    row = db.connect().execute(
        "SELECT email FROM accounts WHERE user_id=? AND verified_at IS NOT"
        " NULL", (user_id,)).fetchone()
    return row["email"] if row else None


def remind_pass(user_id: str, lang: str) -> list[dict]:
    """Rule 2, in code. Called from the monitor and observe senses; cheap
    enough to be. Returns the reminders raised this pass."""
    from . import guardian, life, mailer

    now = datetime.now(timezone.utc)
    horizon = now + timedelta(hours=REMIND_WINDOW_HOURS)
    raised: list[dict] = []
    conn = db.connect()
    for row in conn.execute(
            "SELECT * FROM appointments WHERE user_id=? AND status='booked'"
            " AND reminded_at IS NULL ORDER BY whenat",
            (user_id,)).fetchall():
        moment = datetime.fromisoformat(row["whenat"])
        if not (now <= moment <= horizon):
            continue
        message = i18n.schedule_text("reminder", lang).format(
            title=row["title"], when=row["whenat"][:16].replace("T", " "))
        guardian._event(user_id, "appointment_due", severity="checkin",
                        detail={"message": message,
                                "appointment_id": row["id"]})
        life._insight(user_id, "reminder", message)
        mailed = False
        if row["email_reminder"]:
            to = _user_email(user_id)
            if to:
                # `mailed` used to be set from having *called* deliver, which
                # made it true for a letter printed on a server with no mail
                # host — the same untruth the far end carried. It follows the
                # transport now. And the call is caught: this pass rides the
                # monitor and observe senses, so an unhandled refusal here
                # would lose the reading that carried it, and every later
                # appointment in this sweep with it.
                try:
                    mailed = mailer.deliver(
                        to, i18n.schedule_text("mail_subject", lang)
                        .format(title=row["title"]), message) == "smtp"
                except Exception:  # noqa: BLE001 — the reminder still stands
                    mailed = False
        conn.execute("UPDATE appointments SET reminded_at=? WHERE id=?",
                     (db.utcnow(), row["id"]))
        conn.commit()
        raised.append({"appointment_id": row["id"], "message": message,
                       "mailed": mailed})
    return raised


def view(user_id: str, lang: str) -> dict:
    """Everything the Schedule surface renders — labels included, in the
    reader's language, because no client of this route has a translation
    table of its own."""
    return {
        "appointments": upcoming(user_id),
        "email_available": _user_email(user_id) is not None,
        "labels": i18n.schedule_labels(lang),
        "note": i18n.schedule_text("mail_note", lang),
    }
