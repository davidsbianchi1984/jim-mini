"""A letter printed on the server reached nobody, and says so.

``farend.notify`` returned ``delivered: True`` the moment it had written a
letter — including when ``mailer.deliver`` had no mail server to hand it to,
printed the whole thing on the server's stdout, and returned ``"console"``.
Three separate places in this codebase state the opposite claim:

* ``farend.notify``'s own docstring — *True only when a letter actually left*
* ``guardian._deliver``'s comment on ``notified_emergency_contact``
* ``jim/db.py`` on ``farend_alerts`` — *one row per alert actually mailed*

    asked     was a letter written
    mattered  did a person receive one

The console transport is a developer's terminal. On the beta host, where no
SMTP was configured, every far-end escalation reported the emergency contact
had been notified while the letter went to a container log. This module holds
the flag to a letter that left, and holds the ledger to the same standard —
because a row in ``farend_alerts`` is what the standing check reads, so a
console print recorded as an alert rides as *already told* and silences the
next real detection for half an hour.
"""

from jim import db
from .conftest import enroll


def _alert_rows(user_id: str) -> list:
    return db.connect().execute(
        "SELECT * FROM farend_alerts WHERE user_id=?", (user_id,)).fetchall()


def _with_far_end(client):
    return enroll(client, emergency_name="Pat", emergency_phone="+1-555-0199",
                  emergency_email="pat@example.com", contact_consent=True)


def _critical(client, user_id: str) -> dict:
    body = client.post(f"/monitor/{user_id}", json={"blood_oxygen": 84}).json()
    return body["escalation"]


def test_no_mail_server_means_the_contact_was_not_notified(client):
    """The real deliver() runs with nothing configured: it prints, and the
    escalation says plainly that nobody was reached."""
    user = _with_far_end(client)
    esc = _critical(client, user)
    far = esc["far_end"]
    assert far["transport"] == "console"
    assert far["delivered"] is False
    assert esc["notified_emergency_contact"] is False


def test_the_refusal_says_why_in_the_wearers_language(client):
    """Not merely False — a person reading the console is told the letter was
    printed rather than sent, which is a thing they can go and fix."""
    user = _with_far_end(client)
    far = _critical(client, user)["far_end"]
    assert "mail server" in far["note"]
    from jim import i18n
    assert far["note"] == i18n.farend_text("undelivered", "en")


def test_a_printed_letter_is_not_written_into_the_ledger(client):
    """`farend_alerts` is one row per alert actually mailed. Nothing was."""
    user = _with_far_end(client)
    _critical(client, user)
    assert _alert_rows(user) == []


def test_a_printed_letter_does_not_silence_the_next_real_one(client,
                                                             monkeypatch):
    """The standing check reads `farend_alerts` to stop a re-detecting crisis
    from flooding a mailbox. A console print that recorded a row would ride as
    'the far end was told' — so the first letter that could really leave, once
    mail is configured, would be suppressed as a duplicate. It is not."""
    user = _with_far_end(client)
    printed = _critical(client, user)["far_end"]
    assert printed["delivered"] is False

    from jim import mailer
    sent: list[dict] = []
    monkeypatch.setattr(mailer, "deliver",
                        lambda to, subject, body: sent.append(
                            {"to": to, "subject": subject, "body": body})
                        or "smtp")
    monkeypatch.setattr(mailer, "configured_transport", lambda: "smtp")

    far = _critical(client, user)["far_end"]
    assert far["standing"] is False, "the console print rode as already-told"
    assert far["delivered"] is True
    # Mail coming up also makes the monthly liveness note due, which rides
    # the same monitor sense — so count the alerts, not the letters.
    alerts = [m for m in sent if "may need help" in m["subject"]]
    assert len(alerts) == 1 and alerts[0]["to"] == "pat@example.com"
    assert len(_alert_rows(user)) == 1


def test_a_real_letter_still_reports_delivered(client, monkeypatch):
    """The honest flag is not a flag stuck off: a letter that leaves says so,
    and is recorded."""
    from jim import mailer
    monkeypatch.setattr(mailer, "deliver", lambda to, s, b: "smtp")
    monkeypatch.setattr(mailer, "configured_transport", lambda: "smtp")
    user = _with_far_end(client)
    esc = _critical(client, user)
    assert esc["far_end"]["delivered"] is True
    assert esc["notified_emergency_contact"] is True
    assert len(_alert_rows(user)) == 1


def test_the_monthly_proof_is_not_attempted_without_a_mailbox_to_prove(client):
    """The liveness note exists to prove a mailbox is real on a calm day. With
    no mail server there is nothing to prove it against, and sending anyway
    costs twice: it rides the monitor sense, so the console banner prints on
    every reading, and the stamp it leaves means the note that could prove the
    mailbox is not due again for PING_DAYS."""
    from jim import farend
    user = _with_far_end(client)
    assert farend.liveness_pass(user, "en") is None
    row = db.connect().execute("SELECT farend_pinged_at FROM users WHERE id=?",
                               (user,)).fetchone()
    assert row["farend_pinged_at"] is None, "the retry window was burned"
