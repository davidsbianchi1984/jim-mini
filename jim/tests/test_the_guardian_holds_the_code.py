"""Parental consent is verified, not asserted (spec [0024]/[0030]).

A minor could tick guardian_consent themselves — a checkbox proves nothing.
On the account path the proof is real now: the activation code and link are
delivered to the guardian's own inbox, activating the account is the
guardian's act, and the user record keeps whose address consented and when.
"""

from jim.tests.test_accounts import _capture_mail, _code_from


def _minor_signup(client, guardian_email="parent@example.test", **extra):
    return client.post("/signup", json={
        "email": "kid@example.test", "password": "hunter2-hunter2",
        "display_name": "Sam", "birthdate": "2012-03-01",
        "terms_consent": True, "guardian_consent": True,
        "guardian_email": guardian_email, **extra})


def test_the_code_lands_in_the_guardians_inbox(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    r = _minor_signup(client)
    assert r.status_code == 201, r.text
    assert r.json()["code_sent_to"] == "guardian"

    assert sent[-1]["to"] == "parent@example.test"
    assert "consent" in sent[-1]["subject"].lower()
    assert "kid@example.test" in sent[-1]["body"]

    # The guardian's code activates the minor's account, and the record
    # keeps whose proof it was.
    code = _code_from(sent[-1])
    v = client.post("/verify-email", json={"email": "kid@example.test",
                                           "code": code})
    assert v.status_code == 200, v.text
    user = v.json()
    assert user["guardian_email"] == "parent@example.test"
    assert user["guardian_verified_at"]


def test_a_minor_without_a_guardian_address_is_refused(client, monkeypatch):
    _capture_mail(monkeypatch)
    r = _minor_signup(client, guardian_email=None)
    assert r.status_code == 403
    assert "guardian_email" in r.json()["detail"]

    # And the guardian's address must be genuinely somebody else's.
    r = _minor_signup(client, guardian_email="kid@example.test")
    assert r.status_code == 422
    assert "different" in r.json()["detail"]


def test_an_adults_code_still_goes_to_their_own_inbox(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    r = client.post("/signup", json={
        "email": "dana@example.test", "password": "hunter2-hunter2",
        "display_name": "Dana", "birthdate": "1990-09-14",
        "terms_consent": True})
    assert r.status_code == 201, r.text
    assert r.json()["code_sent_to"] == "account"
    assert sent[-1]["to"] == "dana@example.test"


def test_a_resend_follows_the_guardian_too(client, monkeypatch):
    sent = _capture_mail(monkeypatch)
    assert _minor_signup(client).status_code == 201
    r = client.post("/verify-email/resend", json={"email": "kid@example.test"})
    assert r.status_code == 200, r.text
    assert sent[-1]["to"] == "parent@example.test"
