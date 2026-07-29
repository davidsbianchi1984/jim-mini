"""Where this deployment sends mail through, set from the app itself.

The reason this exists: an app that has no mail server cannot send a
verification email to anybody, and for three releases that produced a
screen waiting on a letter that could never arrive. Configuring a server
here turns the emails real — and turns local signup back into a genuine
email verification.
"""

from __future__ import annotations

from jim import mailer


def test_without_settings_nothing_can_be_emailed(client):
    body = client.get("/settings/mail").json()
    assert body["transport"] == "console"
    assert body["source"] == "none"
    assert body["host"] is None
    assert body["password_set"] is False


def test_saving_settings_makes_the_transport_smtp(client):
    r = client.put("/settings/mail", json={
        "host": "smtp.example.test", "port": 587,
        "username": "me@example.test", "password": "app-password",
        "sender": "me@example.test",
        "public_url": "https://guardian.example.test"})
    assert r.status_code == 200, r.text
    body = client.get("/settings/mail").json()
    assert body["transport"] == "smtp"
    assert body["source"] == "settings"
    assert body["host"] == "smtp.example.test"
    assert body["public_url"] == "https://guardian.example.test"


def test_the_password_never_comes_back_out(client):
    client.put("/settings/mail", json={
        "host": "smtp.example.test", "username": "me@example.test",
        "password": "app-password"})
    body = client.get("/settings/mail").json()
    assert "password" not in body
    assert body["password_set"] is True
    assert "app-password" not in str(body)


def test_configuring_mail_turns_signup_back_into_real_verification(
        client, monkeypatch):
    """With nowhere to send, signup activates locally. With a mail server,
    the address must be proven again — and the email leads with the link."""
    sent: list[dict] = []
    monkeypatch.setattr(mailer, "deliver",
                        lambda to, subject, body: (
                            sent.append({"to": to, "body": body}) or "smtp"))

    r = client.post("/signup", json={
        "email": "before@example.test", "password": "a-real-passphrase",
        "display_name": "Before", "birthdate": "1990-01-01",
        "terms_consent": True})
    assert r.json()["verification"] == "local"      # no mail server yet
    assert sent == []

    client.put("/settings/mail", json={
        "host": "smtp.example.test", "username": "me@example.test",
        "password": "app-password",
        "public_url": "https://guardian.example.test"})

    r = client.post("/signup", json={
        "email": "after@example.test", "password": "a-real-passphrase",
        "display_name": "After", "birthdate": "1990-01-01",
        "terms_consent": True})
    assert r.status_code == 201, r.text
    assert r.json()["verification"] == "email"
    assert r.json()["code_delivery"] == "smtp"
    assert len(sent) == 1 and sent[0]["to"] == "after@example.test"
    # The link is the headline, and it points at the configured address.
    assert "https://guardian.example.test/verify-email/click?token=" \
        in sent[0]["body"]
    # Sign-in refuses until the address is proven.
    assert client.post("/signin", json={
        "email": "after@example.test",
        "password": "a-real-passphrase"}).status_code == 403


def test_a_test_send_reports_what_the_server_said(client, monkeypatch):
    client.put("/settings/mail", json={
        "host": "smtp.example.test", "username": "me@example.test",
        "password": "app-password"})

    def refuse(to, subject, body):
        raise OSError("535 authentication failed")

    monkeypatch.setattr(mailer, "deliver", refuse)
    r = client.post("/settings/mail/test", json={"to": "me@example.test"})
    assert r.status_code == 502
    assert "535" in r.json()["detail"]

    monkeypatch.setattr(mailer, "deliver", lambda *a: "smtp")
    r = client.post("/settings/mail/test", json={"to": "me@example.test"})
    assert r.status_code == 200 and r.json()["sent"] is True


def test_a_test_send_without_a_server_is_refused(client):
    r = client.post("/settings/mail/test", json={"to": "me@example.test"})
    assert r.status_code == 422
    assert "configured" in r.json()["detail"]


def test_clearing_settings_returns_to_the_console_transport(client):
    client.put("/settings/mail", json={"host": "smtp.example.test"})
    assert client.get("/settings/mail").json()["transport"] == "smtp"
    client.delete("/settings/mail")
    assert client.get("/settings/mail").json()["transport"] == "console"


def test_the_environment_outranks_the_settings_screen(client, monkeypatch):
    """A server deployment keeps its credentials in the environment; the
    settings row must never quietly take over from them."""
    client.put("/settings/mail", json={"host": "settings.example.test"})
    monkeypatch.setenv("JIM_SMTP_HOST", "env.example.test")
    body = client.get("/settings/mail").json()
    assert body["source"] == "environment"
    assert body["host"] == "env.example.test"
