"""Email + password accounts: the address is verified before anything exists.

The order is the design: signup holds the enrollment pending and emails a
code; only the code creates the user and mints the first token; sign-in
refuses an unverified address. Codes are hashed at rest, single-use, expiring;
unknown-address and wrong-password answers are indistinguishable.
"""

from __future__ import annotations

from jim import accounts, db, mailer


def _capture_mail(monkeypatch):
    """Swap the mail transport for a recorder; return the list of messages."""
    sent: list[dict] = []

    def fake_deliver(to, subject, body):
        sent.append({"to": to, "subject": subject, "body": body})
        return "console"

    monkeypatch.setattr(mailer, "deliver", fake_deliver)
    return sent


def _code_from(message: dict) -> str:
    for line in message["body"].splitlines():
        if "code is:" in line:
            return line.rsplit(":", 1)[1].strip()
    raise AssertionError(f"no code in {message['body']!r}")


def _signup(client, email="dana@example.test", password="hunter2-hunter2"):
    return client.post("/signup", json={
        "email": email, "password": password,
        "display_name": "Dana", "birthdate": "1990-09-14",
        "terms_consent": True,
    })


def test_signup_sends_a_code_and_creates_no_user_yet(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    r = _signup(client)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["verified"] is False
    assert body["code_delivery"] == "console"
    # The code travelled by mail and only by mail.
    assert "user_token" not in body and "code" not in body
    assert len(sent) == 1 and sent[0]["to"] == "dana@example.test"
    # Nothing exists yet: no user row, no membership, no token.
    assert db.connect().execute(
        "SELECT user_id FROM accounts WHERE email='dana@example.test'"
    ).fetchone()["user_id"] is None


def test_the_code_creates_the_user_and_first_session(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    _signup(client)
    r = client.post("/verify-email", json={
        "email": "dana@example.test", "code": _code_from(sent[0])})
    assert r.status_code == 200, r.text
    user = r.json()
    assert user["user_token"]
    from jim import tiers
    assert user["membership"]["plan"] == tiers.DEFAULT_PLAN
    # The minted token authorizes a personal surface.
    r = client.get(f"/baseline/{user['id']}",
                   headers={"authorization": f"Bearer {user['user_token']}"})
    assert r.status_code == 200, r.text


def test_a_wrong_code_verifies_nothing(client, monkeypatch):
    _capture_mail(monkeypatch)
    _signup(client)
    r = client.post("/verify-email",
                    json={"email": "dana@example.test", "code": "000000"})
    assert r.status_code == 403
    assert db.connect().execute(
        "SELECT user_id FROM accounts WHERE email='dana@example.test'"
    ).fetchone()["user_id"] is None


def test_a_code_is_single_use(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    _signup(client)
    code = _code_from(sent[0])
    assert client.post("/verify-email", json={
        "email": "dana@example.test", "code": code}).status_code == 200
    # Replaying it cannot mint a second session for whoever saw the email.
    assert client.post("/verify-email", json={
        "email": "dana@example.test", "code": code}).status_code == 409


def test_an_expired_code_is_refused(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    _signup(client)
    conn = db.connect()
    conn.execute("UPDATE email_codes SET expires_at='2000-01-01T00:00:00+00:00'")
    conn.commit()
    r = client.post("/verify-email", json={
        "email": "dana@example.test", "code": _code_from(sent[0])})
    assert r.status_code == 403
    assert "expired" in r.json()["detail"]


def test_resend_retires_the_previous_code(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    _signup(client)
    old = _code_from(sent[0])
    assert client.post("/verify-email/resend",
                       json={"email": "dana@example.test"}).status_code == 200
    assert client.post("/verify-email", json={
        "email": "dana@example.test", "code": old}).status_code == 403
    assert client.post("/verify-email", json={
        "email": "dana@example.test", "code": _code_from(sent[1])}
    ).status_code == 200


def test_resend_is_not_an_address_oracle(client, monkeypatch):
    _capture_mail(monkeypatch)
    r = client.post("/verify-email/resend",
                    json={"email": "nobody@example.test"})
    assert r.status_code == 200
    assert r.json()["code_delivery"] == "none"


def test_signin_requires_a_verified_address(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    _signup(client)
    r = client.post("/signin", json={
        "email": "dana@example.test", "password": "hunter2-hunter2"})
    assert r.status_code == 403
    assert "verified" in r.json()["detail"]
    client.post("/verify-email", json={
        "email": "dana@example.test", "code": _code_from(sent[0])})
    r = client.post("/signin", json={
        "email": "dana@example.test", "password": "hunter2-hunter2"})
    assert r.status_code == 200, r.text
    assert r.json()["user_token"]


def test_wrong_password_and_unknown_address_answer_identically(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    _signup(client)
    client.post("/verify-email", json={
        "email": "dana@example.test", "code": _code_from(sent[0])})
    wrong = client.post("/signin", json={
        "email": "dana@example.test", "password": "not-the-password"})
    unknown = client.post("/signin", json={
        "email": "nobody@example.test", "password": "whatever-here"})
    assert wrong.status_code == unknown.status_code == 403
    assert wrong.json()["detail"] == unknown.json()["detail"]


def test_duplicate_email_is_refused(client, monkeypatch):
    _capture_mail(monkeypatch)
    assert _signup(client).status_code == 201
    r = _signup(client)
    assert r.status_code == 409
    assert "pending" in r.json()["detail"]


def test_passwords_and_codes_are_never_stored_in_the_clear(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    _signup(client)
    code = _code_from(sent[0])
    row = db.connect().execute(
        "SELECT * FROM accounts WHERE email='dana@example.test'").fetchone()
    assert "hunter2-hunter2" not in (row["password_hash"] + row["salt"])
    stored = db.connect().execute(
        "SELECT code_hash FROM email_codes WHERE email='dana@example.test'"
    ).fetchall()
    assert all(code != r["code_hash"] for r in stored)


def test_a_short_password_is_refused_before_any_email_is_sent(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    r = _signup(client, password="short")
    assert r.status_code == 422
    assert sent == []


def _verified(client, sent):
    _signup(client)
    r = client.post("/verify-email", json={
        "email": "dana@example.test", "code": _code_from(sent[0])})
    assert r.status_code == 200
    return r.json()


def test_forgot_password_resets_via_emailed_code(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    _verified(client, sent)
    assert client.post("/password/reset/request", json={
        "email": "dana@example.test"}).status_code == 200
    assert "reset code is:" in sent[-1]["body"]
    r = client.post("/password/reset", json={
        "email": "dana@example.test", "code": _code_from(sent[-1]),
        "new_password": "a-brand-new-passphrase"})
    assert r.status_code == 200, r.text
    # Old password out, new password in.
    assert client.post("/signin", json={
        "email": "dana@example.test",
        "password": "hunter2-hunter2"}).status_code == 403
    assert client.post("/signin", json={
        "email": "dana@example.test",
        "password": "a-brand-new-passphrase"}).status_code == 200


def test_a_reset_kills_every_existing_session(client, monkeypatch):
    """Whoever prompted the reset, only the inbox holder stays signed in."""
    sent = _capture_mail(monkeypatch)
    user = _verified(client, sent)
    old_token = user["user_token"]
    client.post("/password/reset/request", json={"email": "dana@example.test"})
    client.post("/password/reset", json={
        "email": "dana@example.test", "code": _code_from(sent[-1]),
        "new_password": "a-brand-new-passphrase"})
    r = client.get(f"/baseline/{user['id']}",
                   headers={"authorization": f"Bearer {old_token}"})
    assert r.status_code == 401


def test_a_verify_code_cannot_reset_a_password(client, monkeypatch):
    """Codes are purpose-bound: the signup code must not double as a reset
    credential."""
    sent = _capture_mail(monkeypatch)
    _signup(client)
    signup_code = _code_from(sent[0])
    client.post("/verify-email", json={
        "email": "dana@example.test", "code": signup_code})
    r = client.post("/password/reset", json={
        "email": "dana@example.test", "code": signup_code,
        "new_password": "a-brand-new-passphrase"})
    assert r.status_code == 403


def test_reset_request_is_not_an_address_oracle(client, monkeypatch):
    _capture_mail(monkeypatch)
    r = client.post("/password/reset/request",
                    json={"email": "nobody@example.test"})
    assert r.status_code == 200
    assert r.json()["code_delivery"] == "none"


def test_console_mail_survives_a_cp1252_stdout(capsys, monkeypatch):
    """The frozen Windows backend's stdout is cp1252. The first shipped
    banner used box-drawing characters that encoding cannot represent, so
    printing the verification code raised — and every signup answered 500 on
    the one platform the console transport serves most. The banner must be
    encodable there, forever."""
    monkeypatch.delenv("JIM_SMTP_HOST", raising=False)
    assert mailer.deliver("dana@example.test", "Your code",
                          "Your verification code is: 123456") == "console"
    out = capsys.readouterr().out
    assert "123456" in out
    out.encode("cp1252")   # raises if the banner regresses


def test_minor_without_guardian_consent_is_refused_at_signup(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    r = client.post("/signup", json={
        "email": "kid@example.test", "password": "hunter2-hunter2",
        "display_name": "Kid", "birthdate": "2015-01-01",
        "terms_consent": True,
    })
    assert r.status_code == 403
    assert sent == []
