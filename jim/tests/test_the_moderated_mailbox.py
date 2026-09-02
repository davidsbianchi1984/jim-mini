"""The moderated mailbox: the coach agent's correspondence, held at the send.

The owner's line, the dialer's line one surface over — build the machinery so
the agent can read, draft, and reply, but **nothing leaves without a person
approving it.** These tests pin the gate where it lives:

* a reply is composed as a *draft* and is never sent by the composing;
* the only path that sends is a moderator's *approve*, and with no mail
  transport wired it *stages* — composed and held, never dropped, never
  claimed sent;
* edit keeps it held, discard throws it away, and every step is catalogued.
"""

import pytest

from jim import audit, db, mailbox
from jim.tests.conftest import enroll


def _actions(user_id):
    return [r["action"] for r in db.connect().execute(
        "SELECT action FROM audit WHERE user_id=? ORDER BY seq",
        (user_id,)).fetchall()]


def test_posture_says_it_is_moderated_and_which_way_mail_carries(client):
    p = mailbox.posture()
    assert p["built"] is True
    assert p["moderated"] is True
    assert p["inbound_ready"] is False        # a webhook/IMAP is the wiring step
    assert "read" in p["directions"] and "moderate" in p["directions"]
    assert "held for a person to approve" in p["note"]


def test_an_inbound_email_lands_in_a_thread(client):
    uid = enroll(client)
    out = mailbox.receive(uid, from_addr="rosa@example.com",
                          subject="checking in", body="How are you doing?")
    assert out["message"]["direction"] == "inbound"
    assert out["message"]["state"] == "received"
    assert "mail.received" in _actions(uid)
    # It shows up in the inbox, in its thread.
    box = mailbox.inbox(uid)
    assert len(box) == 1 and box[0]["correspondent"] == "rosa@example.com"
    assert box[0]["messages"][0]["body"] == "How are you doing?"


def test_a_reply_is_drafted_and_held_never_sent(client):
    uid = enroll(client)
    incoming = mailbox.receive(uid, from_addr="rosa@example.com",
                               subject="checking in", body="How are you?")
    drafted = mailbox.draft(uid, incoming["message"]["id"])
    d = drafted["draft"]
    assert d["direction"] == "outbound"
    assert d["state"] == "draft", "a drafted reply must be held, not sent"
    assert d["body"], "the agent said nothing"
    assert d["to_addr"] == "rosa@example.com"
    assert d["subject"].startswith("Re:")
    assert "mail.drafted" in _actions(uid)
    # Nothing has been sent or staged — only drafted.
    acts = _actions(uid)
    assert "mail.sent" not in acts and "mail.staged" not in acts


def test_approving_with_no_transport_stages_never_claims_a_send(client):
    uid = enroll(client)
    incoming = mailbox.receive(uid, from_addr="rosa@example.com",
                               subject="hi", body="hello?")
    d = mailbox.draft(uid, incoming["message"]["id"])["draft"]
    out = mailbox.moderate(uid, d["id"], "approve")
    # No SMTP is configured in the suite, so the approval STAGES: composed and
    # held, and the receipt never says it was sent.
    assert out["status"] == "staged"
    assert out["message"]["state"] == "staged"
    assert "no mail transport" in out["reason"]
    assert "mail.staged" in _actions(uid)
    assert "mail.sent" not in _actions(uid)


def test_approving_with_smtp_sends_through_the_mailer(client, monkeypatch):
    uid = enroll(client)
    sent = {}
    monkeypatch.setattr(mailbox.mailer, "configured_transport", lambda: "smtp")
    monkeypatch.setattr(mailbox.mailer, "deliver",
                        lambda to, subject, body: sent.update(
                            to=to, subject=subject, body=body) or "smtp")
    incoming = mailbox.receive(uid, from_addr="sam@example.com",
                               subject="re: plan", body="what's next?")
    d = mailbox.draft(uid, incoming["message"]["id"])["draft"]
    out = mailbox.moderate(uid, d["id"], "approve")
    assert out["status"] == "sent" and out["transport"] == "smtp"
    assert sent["to"] == "sam@example.com"
    assert "mail.sent" in _actions(uid)


def test_edit_keeps_it_held_and_discard_throws_it_away(client):
    uid = enroll(client)
    incoming = mailbox.receive(uid, from_addr="rosa@example.com",
                               subject="hi", body="hello?")
    d = mailbox.draft(uid, incoming["message"]["id"])["draft"]
    edited = mailbox.moderate(uid, d["id"], "edit",
                              edited="Hi Rosa — doing well, thank you!")
    assert edited["status"] == "held"
    assert edited["draft"]["body"] == "Hi Rosa — doing well, thank you!"
    # A moderator can then discard it; nothing is sent.
    thrown = mailbox.moderate(uid, d["id"], "discard")
    assert thrown["status"] == "discarded"
    assert "mail.discarded" in _actions(uid)
    assert "mail.sent" not in _actions(uid)


def test_an_originated_message_is_also_held_for_approval(client):
    uid = enroll(client)
    out = mailbox.compose(uid, to="clinic@example.com",
                          subject="appointment",
                          objective="ask to move the Tuesday appointment to "
                                    "the afternoon")
    d = out["draft"]
    assert d["direction"] == "outbound" and d["state"] == "draft"
    assert d["to_addr"] == "clinic@example.com" and d["body"]
    assert "mail.drafted" in _actions(uid)


def test_a_second_reply_is_not_a_draft_to_moderate(client):
    uid = enroll(client)
    incoming = mailbox.receive(uid, from_addr="rosa@example.com",
                               subject="hi", body="hello?")
    # The inbound message is not a draft; moderating it is refused.
    with pytest.raises(ValueError):
        mailbox.moderate(uid, incoming["message"]["id"], "approve")


def test_a_bad_moderation_word_is_refused(client):
    uid = enroll(client)
    incoming = mailbox.receive(uid, from_addr="rosa@example.com",
                               subject="hi", body="hello?")
    d = mailbox.draft(uid, incoming["message"]["id"])["draft"]
    with pytest.raises(ValueError):
        mailbox.moderate(uid, d["id"], "shred")


# --- the owner's doors, over HTTP ------------------------------------------

def test_the_mailbox_doors_are_the_owners(client):
    uid = enroll(client)
    # Posture and inbox read.
    assert client.get(f"/mail/{uid}/posture").json()["moderated"] is True
    assert client.get(f"/mail/{uid}").json() == []
    # Receive, draft, moderate — the whole loop over HTTP.
    got = client.post(f"/mail/{uid}/receive", json={
        "from_addr": "rosa@example.com", "subject": "hi", "body": "hello?"})
    assert got.status_code == 201
    mid = got.json()["message"]["id"]
    drafted = client.post(f"/mail/{uid}/message/{mid}/draft")
    assert drafted.status_code == 201
    did = drafted.json()["draft"]["id"]
    approved = client.post(f"/mail/{uid}/draft/{did}/moderate",
                           json={"action": "approve"})
    assert approved.status_code == 200
    assert approved.json()["status"] == "staged"


def test_the_mailbox_is_not_reachable_without_the_owners_token(client):
    uid = enroll(client)
    other = enroll(client)   # enroll leaves the second user's token on client
    # The client now carries `other`'s token; reading uid's mailbox is refused.
    assert other != uid
    assert client.get(f"/mail/{uid}").status_code == 403


def test_receive_refuses_a_message_with_no_sender_in_the_readers_language(client):
    uid = enroll(client)
    r = client.post(f"/mail/{uid}/receive", json={
        "from_addr": "", "subject": "hi", "body": "hello?"})
    assert r.status_code == 422
    assert "sender" in r.json()["detail"].lower()
