"""Hosting posture: reachable from a LAN or from the internet, safely.

The same deployment serves a laptop on Wi-Fi and a published instance the
operator and their colleagues reach from anywhere. What changes between the
two is what pairing advertises and whether enrolling is gated.
"""

from jim import mobile


def test_pairing_advertises_the_published_url_when_hosted(client, monkeypatch):
    """A hosted deployment's QR must point at the address the phone can
    actually reach — its public URL, not a LAN address the phone can't see."""
    monkeypatch.setenv("JIM_PUBLIC_URL", "https://guardian.example.com/")
    body = client.get("/pair").json()
    assert body["hosted"] is True
    assert body["console_url"] == "https://guardian.example.com/app/"
    assert body["reachable"] is True
    assert "HTTPS" in body["note"]


def test_pairing_falls_back_to_lan_when_not_published(client, monkeypatch):
    """No public URL = the laptop posture, unchanged."""
    monkeypatch.delenv("JIM_PUBLIC_URL", raising=False)
    monkeypatch.setenv("JIM_LAN_HOST", "192.168.1.42")
    body = client.get("/pair").json()
    assert body["hosted"] is False
    assert body["console_url"].startswith("http://192.168.1.42:")
    assert "local network only" in body["note"].lower()


def test_public_base_normalises_trailing_slash(monkeypatch):
    monkeypatch.setenv("JIM_PUBLIC_URL", "https://guardian.example.com/")
    assert mobile.public_base() == "https://guardian.example.com"
    monkeypatch.delenv("JIM_PUBLIC_URL")
    assert mobile.public_base() is None


def _enroll_body():
    return {"display_name": "David", "birthdate": "1984-05-02",
            "terms_consent": True}


def test_signup_key_gates_enrollment_when_set(client, monkeypatch):
    """A published instance stays the operator's: without the key, nobody
    new enrolls; with it, enrollment works normally."""
    monkeypatch.setenv("JIM_SIGNUP_KEY", "let-me-in")
    refused = client.post("/enroll", json=_enroll_body())
    assert refused.status_code == 403
    assert "signup key" in refused.json()["detail"]

    wrong = client.post("/enroll", json=_enroll_body(),
                        headers={"x-signup-key": "guess"})
    assert wrong.status_code == 403

    ok = client.post("/enroll", json=_enroll_body(),
                     headers={"x-signup-key": "let-me-in"})
    assert ok.status_code == 201
    assert ok.json()["user_token"]


def test_health_says_whether_signup_needs_a_key(client, monkeypatch):
    """The signup screen reads this to know whether to ask for an invite key.

    Without it, a gated deployment collects a whole form and answers 403 —
    a refusal the person cannot act on, because nothing ever asked them for
    the key. The flag says only that a key is required, never what it is.
    """
    monkeypatch.delenv("JIM_SIGNUP_KEY", raising=False)
    assert client.get("/health").json()["signup_key"] is False
    monkeypatch.setenv("JIM_SIGNUP_KEY", "let-me-in")
    assert client.get("/health").json()["signup_key"] is True


def test_no_signup_key_leaves_local_use_open(client, monkeypatch):
    """Unset = the LAN/laptop default: reaching it is enough."""
    monkeypatch.delenv("JIM_SIGNUP_KEY", raising=False)
    assert client.post("/enroll", json=_enroll_body()).status_code == 201


def test_gate_does_not_block_an_enrolled_user_or_their_child(client, monkeypatch):
    """The gate is on creating an account here. Someone already enrolled
    keeps working, and a parent adding a child is authorized by their own
    token — not asked for the key again."""
    monkeypatch.delenv("JIM_SIGNUP_KEY", raising=False)
    # Basic, not the free default: this test is about the signup key, and a
    # child's record does not go in the open store (jim/storage.py), so free
    # would fail it for an unrelated reason.
    parent = client.post("/enroll", json={
        "display_name": "Parent", "birthdate": "1984-05-02",
        "terms_consent": True, "plan": "basic"}).json()
    auth = {"authorization": f"Bearer {parent['user_token']}"}

    monkeypatch.setenv("JIM_SIGNUP_KEY", "let-me-in")
    # The parent's own surfaces still answer.
    assert client.post(f"/monitor/{parent['id']}", json={"heart_rate": 70},
                       headers=auth).status_code in (200, 201)
    # And enrolling their child goes through the family route, under their
    # token, without the deployment key.
    child = client.post(f"/guardians/{parent['id']}/children", json={
        "display_name": "Kid", "birthdate": "2015-04-01"}, headers=auth)
    assert child.status_code in (200, 201), child.text
