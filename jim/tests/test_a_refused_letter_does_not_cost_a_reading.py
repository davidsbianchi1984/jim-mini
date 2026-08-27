"""A refused letter does not cost a reading.

Two courtesies ride the monitor and observe senses: the calendar's reminder
pass (`schedule.remind_pass`) and the far end's monthly proof-of-mailbox
(`farend.liveness_pass`). Both were written when `mailer.deliver` could not
fail — with no mail server it prints on the server and returns — so neither
call was ever wrapped, and both sit *above* `guardian.monitor` in the route.

    asked     did the letter go
    mattered  did the reading get recorded

Configuring a real mail server is what made that reachable. A refusal, or an
SMTP connection that hangs to its thirty-second timeout, would raise straight
out of `POST /monitor/{user_id}` — so a reading taken because somebody's
blood oxygen was falling would be discarded with a 500, and no detection or
escalation would run, because the mailbox was having a bad day.

The courtesy is the letter. The duty is the reading. These hold that order.
"""

import smtplib

import pytest

from jim import db
from .conftest import enroll


def _refusing_server(monkeypatch, exc=None):
    from jim import mailer

    def refuse(*a, **k):
        raise exc or smtplib.SMTPServerDisconnected("connection lost")

    monkeypatch.setattr(mailer, "configured_transport", lambda: "smtp")
    monkeypatch.setattr(mailer, "deliver", refuse)


def _events(user_id: str) -> int:
    """A reading that was taken leaves events behind; one discarded with a
    500 leaves none."""
    return db.connect().execute(
        "SELECT COUNT(*) AS n FROM events WHERE user_id=?",
        (user_id,)).fetchone()["n"]


def _verified_account(user_id: str, email: str = "jordan@example.com"):
    """`schedule._user_email` reads `accounts` and requires `verified_at`.
    An enrolled test user has no account row at all, so without this the
    reminder's mail branch is never entered — and a test asserting on
    `mailed` passes whatever the branch does. It did, until a sabotage that
    should have failed it did not."""
    conn = db.connect()
    conn.execute(
        "INSERT INTO accounts (id, email, password_hash, salt, user_id,"
        " verified_at, created_at) VALUES (?,?,?,?,?,?,?)",
        (db.new_id("acc"), email, "x", "y", user_id, db.utcnow(),
         db.utcnow()))
    conn.commit()


def _watched(client):
    return enroll(client, emergency_name="Pat",
                  emergency_email="pat@example.com", contact_consent=True)


@pytest.mark.parametrize("boom", [
    smtplib.SMTPServerDisconnected("connection lost"),
    smtplib.SMTPAuthenticationError(535, b"authentication failed"),
    TimeoutError("timed out"),
])
def test_the_reading_lands_however_the_mail_server_fails(client, monkeypatch,
                                                         boom):
    """Refused, unauthenticated, or hung — the reading is still recorded."""
    user = _watched(client)
    _refusing_server(monkeypatch, boom)
    resp = client.post(f"/monitor/{user}", json={"blood_oxygen": 84})
    assert resp.status_code == 200, resp.text
    assert _events(user), "the reading left no trace — it was discarded"


def test_the_detection_still_runs(client, monkeypatch):
    """Not merely a 200: the reading was low, so the escalation the reading
    exists to trigger has to have happened."""
    user = _watched(client)
    _refusing_server(monkeypatch)
    body = client.post(f"/monitor/{user}", json={"blood_oxygen": 84}).json()
    assert body["severity"] == "critical"
    assert body["escalation"]["escalated"] is True


def test_the_observe_sense_survives_it_too(client, monkeypatch):
    """The same two courtesies ride `observe` — a route that is easy to fix
    on the monitor path alone and leave broken here."""
    user = _watched(client)
    _refusing_server(monkeypatch)
    resp = client.post(f"/activity/{user}",
                       json={"activity": "cooking",
                             "signals": {"pace": "slowing"}})
    assert resp.status_code == 201, resp.text


def test_a_refused_proof_says_so_rather_than_claiming_it_sent(client,
                                                              monkeypatch):
    """The failure is not swallowed into silence: the pass reports it, and
    records it as an event an operator can find."""
    from jim import farend
    user = _watched(client)
    _refusing_server(monkeypatch)
    out = farend.liveness_pass(user, "en")
    assert out["sent"] is False
    assert out["transport"] == "failed"
    assert "refused" in out
    rows = db.connect().execute(
        "SELECT detail FROM events WHERE user_id=? AND type='farend_ping'",
        (user,)).fetchall()
    assert rows and "failed" in rows[-1]["detail"]


def test_a_refusing_mailbox_is_tried_once_not_once_per_reading(client,
                                                               monkeypatch):
    """`farend_pinged_at` is stamped even on failure, and it has to be. This
    rides every reading, and each attempt against a dead server pays the SMTP
    timeout before it fails — so an unstamped failure turns one bad mailbox
    into a slow request for every reading the wearer takes."""
    from jim import mailer
    user = _watched(client)
    calls: list[int] = []

    def refuse(*a, **k):
        calls.append(1)
        raise smtplib.SMTPServerDisconnected("connection lost")

    monkeypatch.setattr(mailer, "configured_transport", lambda: "smtp")
    monkeypatch.setattr(mailer, "deliver", refuse)
    for _ in range(4):
        assert client.post(f"/monitor/{user}",
                           json={"blood_oxygen": 97}).status_code == 200
    assert len(calls) == 1, f"the dead mailbox was dialled {len(calls)} times"


def test_a_reminder_is_only_mailed_when_a_letter_left(client, monkeypatch):
    """`mailed` was set from having *called* deliver, so it was true for a
    letter printed on a server with no mail host — the far end's untruth, in
    the calendar. It follows the transport now."""
    from datetime import datetime, timedelta, timezone
    from jim import schedule
    user = _watched(client)
    _verified_account(user)
    soon = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    r = client.post(f"/schedule/{user}",
                    json={"title": "Cardiology", "when": soon,
                          "email_reminder": True})
    assert r.status_code in (200, 201), r.text
    # No mail server: deliver() prints on the server and returns "console".
    raised = schedule.remind_pass(user, "en")
    assert raised, "the appointment was inside the window and did not raise"
    assert any(r["mailed"] is not None for r in raised)
    assert all(r["mailed"] is False for r in raised), \
        "a letter printed on the server was reported as mailed"

def test_a_refused_reminder_does_not_cost_the_reading_either(client,
                                                             monkeypatch):
    """The calendar's own send, under a refusing server, on the monitor path.

    Every other test here reaches `mailer.deliver` through the far end, so
    narrowing `schedule`'s own `except` to something that never fires left
    them all green. This is the one that walks the calendar's branch: a
    verified account (which is what `_user_email` requires), an appointment
    inside the reminder window asking for email, and a server that refuses.
    """
    from datetime import datetime, timedelta, timezone
    user = _watched(client)
    _verified_account(user)
    soon = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    assert client.post(f"/schedule/{user}",
                       json={"title": "Cardiology", "when": soon,
                             "email_reminder": True}).status_code in (200, 201)
    _refusing_server(monkeypatch)
    resp = client.post(f"/monitor/{user}", json={"blood_oxygen": 84})
    assert resp.status_code == 200, resp.text
    assert _events(user), "the reading was discarded with the reminder"

def test_a_refused_verification_does_not_strand_the_address(client,
                                                            monkeypatch):
    """The account row is written and committed before the code is sent.

    An unhandled refusal there costs more than the letter: the caller sees a
    500, the pending account survives, and the next attempt from the same
    address is told *an account is already pending — verify the emailed
    code*, naming a code nobody ever received. The self-repair path above it
    only runs when the transport is `console`, so on a deployment with a real
    mail server a transient outage locked that address out of signup.

    Signup answers now, saying the code did not go, and `resend` is still the
    way back once the server recovers.
    """
    from jim import accounts
    _refusing_server(monkeypatch)
    out = accounts.signup("stranded@example.com", "a-long-enough-password",
                          {"display_name": "Sam", "birthdate": "1990-01-01",
                           "terms_consent": True})
    assert out["verified"] is False
    assert out["code_delivery"] == "failed"
    # And the way back is open rather than a 409 about a code never sent.
    again = accounts.resend("stranded@example.com")
    assert again["code_delivery"] == "failed"
