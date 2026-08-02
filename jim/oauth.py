"""Sign in with Google or Apple — mirrored from QRME's door, with JIM's own
twist: an account here is nothing without its enrollment, so "sign up with
Google" still answers the Guardian's questions first. The console collects
the same enrollment payload the password flow does and parks it on the
state; the provider's word replaces only the email-verification dance,
never the consent questions.

Configuration decides whether the buttons are live (JIM_GOOGLE_CLIENT_ID /
JIM_GOOGLE_CLIENT_SECRET, and the Apple pair). The id_token payload is read
without a signature check because it arrives directly from the issuer over
TLS — see qrme/oauth.py for the longer argument.
"""

from __future__ import annotations

import base64
import json
import os
import secrets
import urllib.parse
import urllib.request

from . import db

_STATE_TTL_MIN = 10


class OAuthError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


def _env(name: str) -> str | None:
    value = os.environ.get(name, "").strip()
    return value or None


def _providers() -> dict[str, dict]:
    return {
        "google": {
            "name": "Google",
            "client_id": _env("JIM_GOOGLE_CLIENT_ID"),
            "client_secret": _env("JIM_GOOGLE_CLIENT_SECRET"),
            "authorize": "https://accounts.google.com/o/oauth2/v2/auth",
            "token": "https://oauth2.googleapis.com/token",
            "scope": "openid email profile",
            "setup": "register an OAuth client at console.cloud.google.com "
                     "and set JIM_GOOGLE_CLIENT_ID / JIM_GOOGLE_CLIENT_SECRET",
        },
        "apple": {
            "name": "Apple",
            "client_id": _env("JIM_APPLE_CLIENT_ID"),
            "client_secret": _env("JIM_APPLE_CLIENT_SECRET"),
            "authorize": "https://appleid.apple.com/auth/authorize",
            "token": "https://appleid.apple.com/auth/token",
            "scope": "email",
            "setup": "register a Services ID at developer.apple.com, mint "
                     "the client-secret JWT, and set JIM_APPLE_CLIENT_ID / "
                     "JIM_APPLE_CLIENT_SECRET — Apple also requires an https "
                     "return URL, so the deployment must be reachable over "
                     "https",
        },
    }


def providers() -> dict:
    out = []
    for key, spec in _providers().items():
        configured = bool(spec["client_id"] and spec["client_secret"])
        entry = {"provider": key, "name": spec["name"],
                 "configured": configured}
        if not configured:
            entry["setup"] = spec["setup"]
        out.append(entry)
    return {"providers": out}


def _spec(provider: str) -> dict:
    spec = _providers().get(provider)
    if spec is None:
        raise OAuthError(404, f"no such provider {provider!r}")
    if not (spec["client_id"] and spec["client_secret"]):
        raise OAuthError(503, f"{spec['name']} sign-in is not configured on "
                              f"this deployment — {spec['setup']}")
    return spec


def start(provider: str, redirect_uri: str,
          enroll: dict | None = None) -> dict:
    """Mint a state and the provider's authorize URL. ``enroll`` is the
    Guardian's signup payload, parked here so a brand-new account can be
    activated the moment the provider vouches for the inbox."""
    spec = _spec(provider)
    state = secrets.token_urlsafe(24)
    conn = db.connect()
    conn.execute(
        "INSERT INTO oauth_states (state, provider, redirect_uri, enroll,"
        " created_at) VALUES (?,?,?,?,?)",
        (state, provider, redirect_uri,
         json.dumps(enroll) if enroll else None, db.utcnow()))
    conn.commit()
    params = {
        "client_id": spec["client_id"],
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": spec["scope"],
        "state": state,
    }
    if provider == "apple":
        # Apple's rule, not a preference: "if you request any scopes, the
        # value must be form_post". We ask for email, so the browser comes
        # back as a POST — which is why the callback accepts both verbs.
        params["response_mode"] = "form_post"
    return {"provider": provider, "state": state,
            "url": f"{spec['authorize']}?{urllib.parse.urlencode(params)}"}


def _exchange(spec: dict, code: str, redirect_uri: str) -> dict:
    body = urllib.parse.urlencode({
        "client_id": spec["client_id"],
        "client_secret": spec["client_secret"],
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }).encode()
    req = urllib.request.Request(
        spec["token"], data=body,
        headers={"content-type": "application/x-www-form-urlencoded"})
    from . import offline
    offline.allow(url, "the sign-in provider")
    with urllib.request.urlopen(req, timeout=15) as resp:   # noqa: S310
        return json.loads(resp.read().decode())


def _id_token_claims(id_token: str) -> dict:
    try:
        payload = id_token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload))
    except Exception as exc:
        raise OAuthError(502, "the provider's token could not be read") from exc


def callback(provider: str, code: str, state: str, exchange=None) -> dict:
    spec = _spec(provider)
    conn = db.connect()
    row = conn.execute(
        "SELECT * FROM oauth_states WHERE state=? AND provider=?"
        " AND claimed_at IS NULL AND result IS NULL",
        (state, provider)).fetchone()
    if row is None:
        raise OAuthError(403, "unknown or already-used state — start over "
                              "from the sign-in screen")

    tokens = (exchange or _exchange)(spec, code, row["redirect_uri"])
    claims = _id_token_claims(tokens.get("id_token", ""))
    email = (claims.get("email") or "").strip().lower()
    if not email:
        raise OAuthError(502, f"{spec['name']} returned no email address")

    from . import accounts, auth
    account = conn.execute("SELECT * FROM accounts WHERE email=?",
                           (email,)).fetchone()
    if account is None or not account["user_id"]:
        # A Guardian account is nothing without its enrollment — the
        # consent questions cannot be answered by a provider.
        enroll = json.loads(row["enroll"] or "null")
        if not enroll:
            raise OAuthError(
                422, "this address has no Guardian yet — use the sign-up "
                     "form, which sends its enrollment along")
        if account is None:
            account_id = db.new_id("act")
            salt = secrets.token_hex(16)
            conn.execute(
                "INSERT INTO accounts (id, email, password_hash, salt,"
                " pending_profile, created_at) VALUES (?,?,?,?,?,?)",
                (account_id, email,
                 accounts._hash_password(secrets.token_urlsafe(32), salt),
                 salt, json.dumps(enroll), db.utcnow()))
            conn.commit()
        else:
            account_id = account["id"]
            if not account["pending_profile"]:
                conn.execute(
                    "UPDATE accounts SET pending_profile=? WHERE id=?",
                    (json.dumps(enroll), account_id))
                conn.commit()
        fresh = conn.execute("SELECT * FROM accounts WHERE id=?",
                             (account_id,)).fetchone()
        # The provider vouched for the inbox: activation happens now, the
        # same step the emailed code would have unlocked.
        result = accounts._activate(fresh)
    else:
        if not account["verified_at"]:
            conn.execute("UPDATE accounts SET verified_at=? WHERE id=?",
                         (db.utcnow(), account["id"]))
            conn.commit()
        user = conn.execute("SELECT display_name FROM users WHERE id=?",
                            (account["user_id"],)).fetchone()
        result = {"account_id": account["id"], "email": email,
                  "id": account["user_id"],
                  "display_name": user["display_name"] if user else None,
                  "user_token": auth.issue("user", account["user_id"])}

    conn.execute("UPDATE oauth_states SET result=? WHERE state=?",
                 (json.dumps(result), state))
    conn.commit()
    return {"provider": provider, "email": email}


def claim(state: str) -> dict:
    conn = db.connect()
    row = conn.execute(
        "SELECT * FROM oauth_states WHERE state=? AND claimed_at IS NULL",
        (state,)).fetchone()
    if row is None:
        raise OAuthError(403, "unknown or already-claimed state")
    if not row["result"]:
        return {"ready": False}
    conn.execute("UPDATE oauth_states SET claimed_at=? WHERE state=?",
                 (db.utcnow(), state))
    conn.commit()
    return {"ready": True, **json.loads(row["result"])}
