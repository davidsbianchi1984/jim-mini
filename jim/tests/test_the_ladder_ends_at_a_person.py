"""The ladder ends at a person.

``notify_contact`` used to be words: the guardian recorded
``notified_emergency_contact: true`` whenever a phone number was on file,
and nothing left the machine — JIM cannot dial a phone. These tests hold
the rung to a letter that actually leaves, an acknowledgment a person can
press, a refusal that says the room is empty, and a monthly note that
proves the mailbox on a calm day.

    asked     does notify_contact notify a contact
    mattered  the ladder's whole promise is that it ends at a person
"""

from .conftest import enroll


def _mail_spy(monkeypatch):
    from jim import mailer
    sent: list[dict] = []

    def fake_deliver(to, subject, body):
        sent.append({"to": to, "subject": subject, "body": body})
        return "smtp"

    monkeypatch.setattr(mailer, "deliver", fake_deliver)
    monkeypatch.setattr(mailer, "configured_transport", lambda: "smtp")
    return sent


def _ack_token(mail_body: str) -> str:
    line = next(l for l in mail_body.splitlines() if "/farend/ack/" in l)
    return line.rsplit("/", 1)[1].strip()


def test_a_critical_actually_reaches_the_far_end(client, monkeypatch):
    """A critical detection mails the consented address, and the honest flag
    is true because a letter left — not because a contact row exists."""
    sent = _mail_spy(monkeypatch)
    user = enroll(client, emergency_name="Pat", emergency_phone="+1-555-0199",
                  emergency_email="pat@example.com", contact_consent=True)
    body = client.post(f"/monitor/{user}", json={"blood_oxygen": 84}).json()
    esc = body["escalation"]
    assert esc["notified_emergency_contact"] is True
    assert esc["far_end"]["channel"] == "email"
    assert esc["far_end"]["delivered"] is True
    alerts = [m for m in sent if "/farend/ack/" in m["body"]]
    assert len(alerts) == 1 and alerts[0]["to"] == "pat@example.com"


def test_without_an_address_the_room_is_honestly_empty(client, monkeypatch):
    """A phone number alone is something a responder dials, not something
    this product can reach: the flag says so, in words, and no mail leaves."""
    sent = _mail_spy(monkeypatch)
    user = enroll(client, emergency_name="Pat", emergency_phone="+1-555-0199",
                  contact_consent=True)
    body = client.post(f"/monitor/{user}", json={"blood_oxygen": 84}).json()
    esc = body["escalation"]
    assert esc["notified_emergency_contact"] is False
    assert esc["far_end"]["delivered"] is False
    assert "far end" in esc["far_end"]["note"]
    assert sent == []


def test_the_ack_link_records_a_person_seeing_it(client, monkeypatch):
    """The emailed link marks the alert seen exactly once, records the
    acknowledgment as an event, and an unknown token is a 404 — the token
    is a capability to mark one alert, not a door into anything."""
    sent = _mail_spy(monkeypatch)
    user = enroll(client, emergency_email="pat@example.com",
                  contact_consent=True)
    client.post(f"/monitor/{user}", json={"blood_oxygen": 84})
    alert = next(m for m in sent if "/farend/ack/" in m["body"])
    token = _ack_token(alert["body"])
    assert client.get(f"/farend/ack/{token}").status_code == 200
    assert client.get(f"/farend/ack/{token}").status_code == 200  # already
    events = client.get(f"/events/{user}").json()
    assert sum(e["type"] == "farend_ack" for e in events) == 1
    assert client.get("/farend/ack/never-was-a-token").status_code == 404


def test_a_storm_does_not_flood_the_mailbox(client, monkeypatch):
    """While an unacknowledged alert stands, a re-detection of the same
    condition rides it: the far end was told, and telling them louder is
    not telling them more."""
    sent = _mail_spy(monkeypatch)
    user = enroll(client, emergency_email="pat@example.com",
                  contact_consent=True)
    client.post(f"/monitor/{user}", json={"blood_oxygen": 84})
    body = client.post(f"/monitor/{user}", json={"blood_oxygen": 83}).json()
    esc = body["escalation"]
    assert esc["notified_emergency_contact"] is True
    assert esc["far_end"]["standing"] is True
    assert len([m for m in sent if "/farend/ack/" in m["body"]]) == 1


def test_the_monthly_note_proves_the_mailbox(client, monkeypatch):
    """A calm sample sends the liveness note once — and only once — so a
    dead mailbox is discovered on a calm day, not during an emergency."""
    sent = _mail_spy(monkeypatch)
    user = enroll(client, emergency_email="pat@example.com",
                  contact_consent=True)
    client.post(f"/monitor/{user}", json={"heart_rate": 62})
    client.post(f"/monitor/{user}", json={"heart_rate": 63})
    pings = [m for m in sent if "/farend/ack/" not in m["body"]]
    assert len(pings) == 1
    assert pings[0]["to"] == "pat@example.com"


def test_the_rung_can_be_built_before_the_person_is_chosen(client,
                                                           monkeypatch):
    """The reviewer's sequencing, end to end: enrollment names nobody, the
    status says so honestly, and the address arrives later through its own
    door — after which the same critical really is delivered."""
    _mail_spy(monkeypatch)
    user = enroll(client)
    status = client.get(f"/farend/{user}").json()
    assert status["configured"] is False and "far end" in status["note"]
    r = client.put(f"/farend/{user}",
                   json={"email": "kin@example.com", "consent": True})
    assert r.status_code == 200 and r.json()["configured"] is True
    body = client.post(f"/monitor/{user}", json={"blood_oxygen": 84}).json()
    assert body["escalation"]["notified_emergency_contact"] is True
    bad = client.put(f"/farend/{user}", json={"email": "not an address"})
    assert bad.status_code == 422


def test_the_status_shows_the_alert_but_never_the_token(client, monkeypatch):
    """The console's view carries the last alert and its acknowledgment
    state; the token stays in the letter it was minted for."""
    sent = _mail_spy(monkeypatch)
    user = enroll(client, emergency_email="pat@example.com",
                  contact_consent=True)
    client.post(f"/monitor/{user}", json={"blood_oxygen": 84})
    status = client.get(f"/farend/{user}").json()
    last = status["last_alert"]
    assert last and last["acked_at"] is None
    assert "token" not in last
    token = _ack_token(next(m for m in sent
                            if "/farend/ack/" in m["body"])["body"])
    client.get(f"/farend/ack/{token}")
    assert client.get(f"/farend/{user}").json()["last_alert"]["acked_at"]
