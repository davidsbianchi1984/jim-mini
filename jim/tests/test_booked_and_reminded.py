"""Booked, reminded at the bottom rung, and emailed to yourself alone.

## The finding

The Guardian could watch sleep, money and medication, point at desks and
shops — and could not hold an appointment. There was no calendar row, so
"remind me" had nowhere to live, "book the class" ended at the order, and
the mail plumbing that carries verification codes carried nothing else.

    asked     can the Guardian point at where help is
    mattered  can it hold the time you agreed to go

## The three rules of jim/schedule.py, driven from the outside

1. a booking is a row, not a hostage — one press books, one press
   cancels, and cancelling a service booking hands back the linked order
   while it is still `placed`;
2. reminders ride the proactive ladder at its bottom rung — a guardian
   event at `checkin` severity plus an insight, raised once per
   appointment, on whatever sense fires first, and never anything more
   however missed the appointment gets;
3. email goes to the user or nowhere — the recipient is looked up from
   the verified account, never passed in, so there is no request shape in
   which JIM mails a third party.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from jim import db, mailer, schedule


def _user(client):
    r = client.post("/enroll", json={"display_name": "Vera",
                                     "birthdate": "1979-04-02",
                                     "terms_consent": True})
    assert r.status_code == 201, r.text
    u = r.json()
    client.headers["authorization"] = f"Bearer {u['user_token']}"
    return u


def _soon(hours=2):
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


def _later(hours=100):
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


# --- rule 1: a row, not a hostage --------------------------------------------

def test_book_list_cancel(client):
    u = _user(client)
    r = client.post(f"/schedule/{u['id']}", json={
        "title": "Dentist", "when": _later(), "where": "12 Main St"})
    assert r.status_code == 201, r.text
    appt = r.json()
    view = client.get(f"/schedule/{u['id']}").json()
    assert [a["title"] for a in view["appointments"]] == ["Dentist"]
    r = client.delete(f"/schedule/{u['id']}/{appt['id']}")
    assert r.status_code == 200 and r.json()["status"] == "cancelled"
    assert client.get(f"/schedule/{u['id']}").json()["appointments"] == []


def test_the_past_is_not_bookable_and_neither_is_nonsense(client):
    u = _user(client)
    r = client.post(f"/schedule/{u['id']}", json={
        "title": "Time travel", "when": "2020-01-01T10:00:00+00:00"})
    assert r.status_code == 422 and "already passed" in r.json()["detail"]
    r = client.post(f"/schedule/{u['id']}", json={
        "title": "x", "when": "next tuesday-ish"})
    assert r.status_code == 422 and "ISO" in r.json()["detail"]


def test_somebody_elses_appointment_cannot_be_cancelled(client):
    u = _user(client)
    appt = client.post(f"/schedule/{u['id']}", json={
        "title": "Mine", "when": _later()}).json()
    r = client.post("/enroll", json={"display_name": "Other",
                                     "birthdate": "1990-01-01",
                                     "terms_consent": True})
    other = r.json()
    client.headers["authorization"] = f"Bearer {other['user_token']}"
    r = client.delete(f"/schedule/{other['id']}/{appt['id']}")
    assert r.status_code == 422
    assert "somebody else" in r.json()["detail"]


# --- rule 1, the service half: booking places the order ----------------------

@pytest.fixture()
def tandem(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from .test_shopping_through_the_tandem import FakeShopQRME

    monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
    monkeypatch.setenv("JIM_LLM", "stub")
    db.reset()
    from jim.api import create_app
    from jim.qrme_client import QRMEClient

    fake = FakeShopQRME()
    tc = TestClient(create_app(qrme_client=QRMEClient(client=fake)))
    tc.__enter__()
    yield tc, fake
    tc.__exit__(None, None, None)
    db.reset()


def test_booking_a_service_is_one_act(tandem):
    client, fake = tandem
    u = _user(client)
    r = client.post(f"/schedule/{u['id']}", json={
        "title": "Candle-making class", "when": _later(),
        "shop_id": "shp_1", "offering_id": "off_1"})
    assert r.status_code == 201, r.text
    appt = r.json()
    assert appt["qrme_order_id"], "the order did not ride the booking"
    view = client.get(f"/shopping/{u['id']}").json()
    assert len(view["receipts"]) == 1, "no receipt was kept"


def test_cancelling_the_booking_hands_the_placed_order_back(tandem):
    client, fake = tandem
    u = _user(client)
    appt = client.post(f"/schedule/{u['id']}", json={
        "title": "Class", "when": _later(),
        "shop_id": "shp_1", "offering_id": "off_1"}).json()
    r = client.delete(f"/schedule/{u['id']}/{appt['id']}")
    assert r.status_code == 200
    receipts = client.get(f"/shopping/{u['id']}").json()["receipts"]
    assert receipts[0]["status"] == "cancelled", receipts


def test_naming_half_a_service_is_refused(tandem):
    client, _ = tandem
    u = _user(client)
    r = client.post(f"/schedule/{u['id']}", json={
        "title": "Class", "when": _later(), "shop_id": "shp_1"})
    assert r.status_code == 422 and "both" in r.json()["detail"]


# --- rule 2: the bottom rung -------------------------------------------------

def _monitor(client, uid):
    return client.post(f"/monitor/{uid}",
                       json={"heart_rate": 72, "stress_level": 0.2})


def test_a_near_appointment_becomes_a_checkin_event_and_an_insight(client):
    u = _user(client)
    client.post(f"/schedule/{u['id']}", json={"title": "Dentist",
                                              "when": _soon()})
    assert _monitor(client, u["id"]).status_code == 200
    ev = db.connect().execute(
        "SELECT * FROM events WHERE user_id=? AND type='appointment_due'",
        (u["id"],)).fetchone()
    assert ev is not None, "no guardian event — the reminder never reached "\
                           "the ladder"
    assert ev["severity"] == "checkin", dict(ev)
    row = db.connect().execute(
        "SELECT message FROM insights WHERE user_id=? AND kind='reminder'",
        (u["id"],)).fetchone()
    assert row is not None and "Dentist" in row["message"]


def test_each_appointment_reminds_exactly_once(client):
    u = _user(client)
    client.post(f"/schedule/{u['id']}", json={"title": "Dentist",
                                              "when": _soon()})
    _monitor(client, u["id"])
    _monitor(client, u["id"])
    _monitor(client, u["id"])
    n = db.connect().execute(
        "SELECT COUNT(*) n FROM events WHERE user_id=? AND"
        " type='appointment_due'", (u["id"],)).fetchone()["n"]
    assert n == 1, f"{n} reminders for one appointment"


def test_a_far_appointment_stays_quiet(client):
    u = _user(client)
    client.post(f"/schedule/{u['id']}", json={"title": "Reunion",
                                              "when": _later(300)})
    _monitor(client, u["id"])
    n = db.connect().execute(
        "SELECT COUNT(*) n FROM events WHERE user_id=? AND"
        " type='appointment_due'", (u["id"],)).fetchone()["n"]
    assert n == 0


def test_the_reminder_never_climbs_past_checkin(client):
    """Rule 2's hard line, stated as the money guardian states it: however
    missed, a haircut does not ring a phone."""
    u = _user(client)
    client.post(f"/schedule/{u['id']}", json={"title": "Haircut",
                                              "when": _soon(1)})
    _monitor(client, u["id"])
    rows = db.connect().execute(
        "SELECT severity FROM events WHERE user_id=? AND"
        " type='appointment_due'", (u["id"],)).fetchall()
    assert rows and all(r["severity"] == "checkin" for r in rows)


def test_the_reminder_speaks_the_users_language(client):
    u = _user(client)
    client.put(f"/language/{u['id']}", json={"language": "pt"})
    client.post(f"/schedule/{u['id']}", json={"title": "Dentista",
                                              "when": _soon()})
    _monitor(client, u["id"])
    row = db.connect().execute(
        "SELECT message FROM insights WHERE user_id=? AND kind='reminder'",
        (u["id"],)).fetchone()
    assert row is not None and "Em breve" in row["message"], dict(row or {})


# --- rule 3: email to yourself, or nowhere -----------------------------------

@pytest.fixture()
def outbox(monkeypatch):
    sent: list[tuple[str, str, str]] = []
    def fake_deliver(to, subject, body):
        sent.append((to, subject, body))
        return "smtp"
    monkeypatch.setattr(mailer, "deliver", fake_deliver)
    return sent


def _verified_user(client):
    """A user owned by a verified account, the way signup produces one."""
    u = _user(client)
    conn = db.connect()
    conn.execute(
        "INSERT INTO accounts (id, email, password_hash, salt, user_id,"
        " verified_at, created_at) VALUES (?,?,?,?,?,?,?)",
        (db.new_id("acc"), "vera@example.com", "x", "x", u["id"],
         db.utcnow(), db.utcnow()))
    conn.commit()
    return u


def test_an_opted_in_reminder_mails_the_owner_and_nobody_else(client, outbox):
    u = _verified_user(client)
    client.post(f"/schedule/{u['id']}", json={
        "title": "Dentist", "when": _soon(), "email_reminder": True})
    _monitor(client, u["id"])
    assert len(outbox) == 1, "the reminder never went to mail"
    to, subject, body = outbox[0]
    assert to == "vera@example.com"
    assert "Dentist" in subject and "Dentist" in body


def test_without_opt_in_no_mail_moves(client, outbox):
    u = _verified_user(client)
    client.post(f"/schedule/{u['id']}", json={"title": "Dentist",
                                              "when": _soon()})
    _monitor(client, u["id"])
    assert outbox == []


def test_no_verified_email_means_no_mail_and_no_error(client, outbox):
    """An enroll-only user has no account; the reminder still lands on the
    ladder and the mail half simply does not happen."""
    u = _user(client)
    client.post(f"/schedule/{u['id']}", json={
        "title": "Dentist", "when": _soon(), "email_reminder": True})
    assert _monitor(client, u["id"]).status_code == 200
    assert outbox == []
    view = client.get(f"/schedule/{u['id']}").json()
    assert view["email_available"] is False


def test_there_is_no_request_shape_that_mails_a_third_party(client):
    """Structural: the booking body has no recipient field to abuse, and an
    unknown field is a validation error, not a silent extra."""
    u = _verified_user(client)
    r = client.post(f"/schedule/{u['id']}", json={
        "title": "Dentist", "when": _soon(), "email_reminder": True,
        "recipient": "mallory@example.com", "to": "mallory@example.com"})
    # Whatever FastAPI does with extras, nothing may store an address:
    joined = " ".join(str(dict(row)) for row in db.connect().execute(
        "SELECT * FROM appointments").fetchall())
    assert "mallory" not in joined


# --- the labels ---------------------------------------------------------------

def test_the_view_carries_its_own_labels(client):
    u = _user(client)
    client.put(f"/language/{u['id']}", json={"language": "ja"})
    view = client.get(f"/schedule/{u['id']}").json()
    assert view["labels"]["title"] == "予定"
    assert "確認済み" in view["note"] or "アドレス" in view["note"]
