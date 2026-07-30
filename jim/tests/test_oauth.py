"""Sign in with Google/Apple, the Guardian's way: the provider vouches for
the inbox, never for the consent questions — a brand-new account still
carries its full enrollment, parked on the state by the console.
"""

import base64
import json

from jim import db, oauth


def _id_token(email, name="Signer"):
    payload = base64.urlsafe_b64encode(
        json.dumps({"email": email, "email_verified": True,
                    "name": name}).encode()).rstrip(b"=").decode()
    return f"h.{payload}.s"


ENROLL = {"display_name": "Jordan", "birthdate": "1995-05-05",
          "terms_consent": True, "resting_heart_rate": 60}


def test_unconfigured_providers_say_so(client):
    listed = client.get("/auth/oauth/providers").json()["providers"]
    assert {p["provider"] for p in listed} == {"google", "apple"}
    assert all(p["configured"] is False for p in listed)
    r = client.post("/auth/oauth/google/start", json={})
    assert r.status_code == 503


def test_signup_with_google_still_answers_the_guardian(client, monkeypatch):
    monkeypatch.setenv("JIM_GOOGLE_CLIENT_ID", "cid")
    monkeypatch.setenv("JIM_GOOGLE_CLIENT_SECRET", "sec")
    monkeypatch.setattr(oauth, "_exchange", lambda spec, code, uri: {
        "id_token": _id_token("jordan@example.com", "Jordan")})

    # Without the enrollment, a new address is refused — the provider's
    # word covers the inbox, not the consent questions.
    bare = client.post("/auth/oauth/google/start", json={}).json()
    r = client.get("/auth/oauth/google/callback",
                   params={"code": "c", "state": bare["state"]})
    assert r.status_code == 422 and "enrollment" in r.text

    # With it, the account activates the moment the provider vouches.
    started = client.post("/auth/oauth/google/start",
                          json={"enroll": ENROLL}).json()
    r = client.get("/auth/oauth/google/callback",
                   params={"code": "c", "state": started["state"]})
    assert r.status_code == 200 and "jordan@example.com" in r.text

    claimed = client.get("/auth/oauth/claim",
                         params={"state": started["state"]}).json()
    assert claimed["ready"] is True and claimed["user_token"]
    assert claimed["display_name"] == "Jordan"
    # The account is verified and owns a real enrolled user.
    row = db.connect().execute(
        "SELECT verified_at, user_id FROM accounts WHERE"
        " email='jordan@example.com'").fetchone()
    assert row["verified_at"] and row["user_id"] == claimed["id"]
    # The state is spent after one claim.
    assert client.get("/auth/oauth/claim",
                      params={"state": started["state"]}).status_code == 403


def test_an_enrolled_account_signs_straight_in(client, monkeypatch):
    monkeypatch.setenv("JIM_GOOGLE_CLIENT_ID", "cid")
    monkeypatch.setenv("JIM_GOOGLE_CLIENT_SECRET", "sec")
    monkeypatch.setattr(oauth, "_exchange", lambda spec, code, uri: {
        "id_token": _id_token("back@example.com")})

    first = client.post("/auth/oauth/google/start",
                        json={"enroll": ENROLL}).json()
    client.get("/auth/oauth/google/callback",
               params={"code": "c", "state": first["state"]})
    client.get("/auth/oauth/claim", params={"state": first["state"]})

    again = client.post("/auth/oauth/google/start", json={}).json()
    client.get("/auth/oauth/google/callback",
               params={"code": "c", "state": again["state"]})
    claimed = client.get("/auth/oauth/claim",
                         params={"state": again["state"]}).json()
    assert claimed["ready"] is True and claimed["user_token"]
    # Same user both times — one Guardian per address.
    users = db.connect().execute(
        "SELECT COUNT(*) AS n FROM accounts WHERE email='back@example.com'"
    ).fetchone()
    assert users["n"] == 1


def test_apple_asks_for_form_post_and_the_door_accepts_it(client, monkeypatch):
    """Apple's rule, not our preference: requesting any scope forces
    response_mode=form_post, so the browser returns as a POST. Sending
    response_mode=query with a scope is rejected by Apple outright — which
    would have surfaced as "sign-in is broken" on the very first attempt with
    a freshly registered client."""
    from jim import oauth
    monkeypatch.setenv("JIM_APPLE_CLIENT_ID", "com.example.jim")
    monkeypatch.setenv("JIM_APPLE_CLIENT_SECRET", "secret-jwt")
    started = oauth.start("apple", "http://127.0.0.1:8000/auth/oauth/apple/callback")
    assert "response_mode=form_post" in started["url"]
    assert "scope=email" in started["url"]

    # The POST door exists and reads the urlencoded body Apple sends.
    r = client.post("/auth/oauth/apple/callback",
                    content="error=user_cancelled_authorize",
                    headers={"content-type": "application/x-www-form-urlencoded"})
    assert r.status_code == 400
    assert "user_cancelled_authorize" in r.text


def test_google_still_comes_back_on_the_query_string(client, monkeypatch):
    from jim import oauth
    monkeypatch.setenv("JIM_GOOGLE_CLIENT_ID", "gid")
    monkeypatch.setenv("JIM_GOOGLE_CLIENT_SECRET", "gsecret")
    started = oauth.start("google", "http://127.0.0.1:8000/auth/oauth/google/callback")
    assert "response_mode" not in started["url"]
    r = client.get("/auth/oauth/google/callback", params={"error": "access_denied"})
    assert r.status_code == 400 and "access_denied" in r.text
