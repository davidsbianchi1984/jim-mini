"""Email + password accounts, with the address verified before anything exists.

The order of operations is the design:

1. **Signup** records the email, the password hash, and the pending
   enrollment payload — and sends a six-digit code to the address. No user
   row, no capability token, no membership yet: nothing exists that a
   mistyped or someone-else's email address could reach.
2. **Verification** — presenting the code proves the caller can read that
   inbox. Only then is the Guardian user actually enrolled (same path as
   ``POST /enroll``) and the first capability token minted.
3. **Sign-in** afterwards checks the password and mints a fresh token; an
   unverified account cannot sign in at all.

Storage rules: passwords are PBKDF2-HMAC-SHA256 with a per-account salt and
never stored or logged in the clear; codes are hashed at rest (a database
read must not become a verification bypass), single-use, and expire in
15 minutes; issuing a new code retires the previous ones.
"""

from __future__ import annotations

import hashlib
import json
import re
import secrets
from datetime import datetime, timedelta, timezone

from . import db, mailer

CODE_TTL_MINUTES = 15
_PBKDF2_ITERATIONS = 600_000
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class AccountError(Exception):
    def __init__(self, status: int, detail: str) -> None:
        super().__init__(detail)
        self.status = status
        self.detail = detail


def _normalize(email: str) -> str:
    email = email.strip().lower()
    if not _EMAIL_RE.match(email):
        raise AccountError(422, "that does not look like an email address")
    return email


def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), _PBKDF2_ITERATIONS
    ).hex()


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def _public_url() -> str:
    return mailer.public_url()


def _send_code(email: str, purpose: str = "verify",
               deliver_to: str | None = None) -> str:
    """Issue a fresh code for ``email`` (retiring any previous ones for the
    same purpose), deliver it, and return the transport name — never the
    code. Verification mail leads with a **clickable link** (the shape every
    mainstream flow uses); the 6-digit code rides along as the fallback for
    a mail client on a different device than the app."""
    conn = db.connect()
    conn.execute(
        "UPDATE email_codes SET consumed_at=? WHERE email=? AND purpose IN (?,?)"
        " AND consumed_at IS NULL",
        (db.utcnow(), email, purpose, purpose + "-link"),
    )
    code = f"{secrets.randbelow(1_000_000):06d}"
    expires = (datetime.now(timezone.utc)
               + timedelta(minutes=CODE_TTL_MINUTES)).isoformat()
    conn.execute(
        "INSERT INTO email_codes (email, code_hash, purpose, expires_at, created_at)"
        " VALUES (?,?,?,?,?)",
        (email, _hash_code(code), purpose, expires, db.utcnow()),
    )
    if purpose == "verify":
        link_token = secrets.token_urlsafe(32)
        conn.execute(
            "INSERT INTO email_codes (email, code_hash, purpose, expires_at,"
            " created_at) VALUES (?,?,?,?,?)",
            (email, _hash_code(link_token), "verify-link", expires, db.utcnow()),
        )
    conn.commit()
    if purpose == "reset":
        return mailer.deliver(
            email,
            "Your JIM Guardian password reset code",
            f"Your password reset code is: {code}\n\n"
            f"It expires in {CODE_TTL_MINUTES} minutes. If you did not ask to "
            "reset your password, ignore this message — your password is "
            "unchanged without it.",
        )
    if deliver_to and deliver_to != email:
        # Verified parental consent (spec [0024]/[0030]): the code and link
        # stay keyed to the minor's account address, but the mail lands in
        # the guardian's inbox — activating the account is the guardian's
        # act, and the message says exactly what it authorizes.
        return mailer.deliver(
            deliver_to,
            "A minor is asking to join JIM Guardian — your consent is needed",
            f"Someone under 18 has created a JIM Guardian account with "
            f"{email} and named you as their parent or guardian.\n\n"
            f"If you consent, click to activate the account:\n\n"
            f"{_public_url()}/verify-email/click?token={link_token}\n\n"
            f"Or enter this code in the app: {code} (you can pass it to "
            f"them to type in — either way the consent is yours to give)\n\n"
            f"Both expire in {CODE_TTL_MINUTES} minutes. If you do not "
            "consent, ignore this message — without it the account cannot "
            "be activated.",
        )
    return mailer.deliver(
        email,
        "Verify your JIM Guardian account",
        f"Click to verify your account:\n\n"
        f"{_public_url()}/verify-email/click?token={link_token}\n\n"
        f"Or enter this code in the app: {code}\n\n"
        f"Both expire in {CODE_TTL_MINUTES} minutes. If you did not create a "
        "JIM Guardian account, ignore this message — without this the "
        "account cannot be activated.",
    )


def _consume_code(email: str, code: str, purpose: str) -> None:
    """Check-and-burn the newest live code, or raise."""
    conn = db.connect()
    row = conn.execute(
        "SELECT rowid, * FROM email_codes WHERE email=? AND purpose=?"
        " AND consumed_at IS NULL ORDER BY created_at DESC LIMIT 1",
        (email, purpose),
    ).fetchone()
    if row is None or not secrets.compare_digest(
            row["code_hash"], _hash_code(code.strip())):
        raise AccountError(403, "that code is not right")
    if row["expires_at"] < datetime.now(timezone.utc).isoformat():
        raise AccountError(403, "that code has expired — request a new one")
    conn.execute("UPDATE email_codes SET consumed_at=? WHERE rowid=?",
                 (db.utcnow(), row["rowid"]))
    conn.commit()


def signup(email: str, password: str, enroll_payload: dict) -> dict:
    """Create an unverified account holding the enrollment for later."""
    email = _normalize(email)
    if len(password) < 8:
        raise AccountError(422, "password must be at least 8 characters")
    conn = db.connect()
    existing = conn.execute(
        "SELECT * FROM accounts WHERE email=?", (email,)
    ).fetchone()
    if existing:
        if existing["verified_at"]:
            raise AccountError(
                409, "an account already exists for this address — sign in "
                     "instead")
        if mailer.configured_transport() == "console":
            # A pending half-account (a crashed or abandoned earlier signup)
            # on a machine with no mail transport: nothing can ever verify
            # it, and the machine owner is the only person here. Finish it
            # now, under the credentials just typed — the earlier attempt's
            # password may be lost to the crash that stranded it.
            salt = secrets.token_hex(16)
            conn.execute(
                "UPDATE accounts SET password_hash=?, salt=?,"
                " pending_profile=? WHERE id=?",
                (_hash_password(password, salt), salt,
                 json.dumps(enroll_payload), existing["id"]),
            )
            conn.commit()
            account = conn.execute(
                "SELECT * FROM accounts WHERE id=?", (existing["id"],)
            ).fetchone()
            user = _activate(account)
            user["verified"] = True
            user["verification"] = "local"
            return user
        raise AccountError(
            409, "an account is already pending for this address — verify "
                 "the emailed code, or resend it")
    salt = secrets.token_hex(16)
    account_id = db.new_id("acc")
    conn.execute(
        "INSERT INTO accounts (id, email, password_hash, salt, pending_profile,"
        " created_at) VALUES (?,?,?,?,?,?)",
        (account_id, email, _hash_password(password, salt), salt,
         json.dumps(enroll_payload), db.utcnow()),
    )
    conn.commit()
    # No mail transport means no inbox can ever be proven — and on a local
    # single-user install (the packaged desktop app) there is nothing to
    # prove: the person owns the machine and the database. Waiting on an
    # email that cannot arrive is a locked door in an empty house; activate
    # directly. A deployment with SMTP configured enforces the real proof.
    if mailer.configured_transport() == "console":
        account = conn.execute(
            "SELECT * FROM accounts WHERE id=?", (account_id,)).fetchone()
        user = _activate(account)
        user["verified"] = True
        user["verification"] = "local"
        return user
    guardian_to = (enroll_payload.get("guardian_email") or "").strip() or None
    delivery = _send_code(email, deliver_to=guardian_to)
    return {"account_id": account_id, "email": email, "verified": False,
            "code_delivery": delivery, "verification": "email",
            "code_sent_to": "guardian" if guardian_to else "account"}


def resend(email: str) -> dict:
    email = _normalize(email)
    row = db.connect().execute(
        "SELECT verified_at, pending_profile FROM accounts WHERE email=?",
        (email,)
    ).fetchone()
    # One response either way a code could not be sent: an endpoint that
    # answers "no such account" to strangers is an address oracle.
    if row is None or row["verified_at"]:
        return {"email": email, "code_delivery": "none"}
    # A minor's resend goes where the original went: the guardian's inbox.
    pending = json.loads(row["pending_profile"] or "{}")
    guardian_to = (pending.get("guardian_email") or "").strip() or None
    return {"email": email,
            "code_delivery": _send_code(email, deliver_to=guardian_to)}


def _activate(account) -> dict:
    """Enroll the pending user and mint the first session — the step that
    only happens once the address is proven (or, on a local install with no
    mail transport, trusted: see ``signup``)."""
    import json as _json

    from . import auth, guardian, i18n, tiers
    conn = db.connect()
    payload = _json.loads(account["pending_profile"] or "{}")
    user = guardian.enroll(_revive(payload))
    if payload.get("language") in i18n.SUPPORTED:
        i18n.set_language(user["id"], payload["language"])
        user["language"] = payload["language"]
    # A parked plan the catalogue does not know falls to the default rather
    # than raising: /signup validates plans now, but payloads parked before
    # it did — and the OAuth door's free-form enroll dict — still activate
    # here, and a raise at this line strands a just-created user with no
    # membership (every capability gate then reads "visitor"). Activation
    # is a click on an emailed link; there is nobody standing here to hand
    # a 422 to.
    plan = payload.get("plan")
    if plan not in tiers.PLANS or plan == "visitor":
        plan = tiers.DEFAULT_PLAN
    tiers.subscribe(user["id"], plan)
    user["membership"] = tiers.membership(user["id"])
    conn.execute(
        "UPDATE accounts SET user_id=?, verified_at=?, pending_profile=NULL"
        " WHERE id=?",
        (user["id"], db.utcnow(), account["id"]),
    )
    # Verified parental consent: the code that just activated this account
    # was delivered to the guardian's inbox, so the proof is theirs — record
    # whose it was and when it landed.
    if payload.get("guardian_email"):
        conn.execute(
            "UPDATE users SET guardian_email=?, guardian_verified_at=?"
            " WHERE id=?",
            (payload["guardian_email"], db.utcnow(), user["id"]))
        user["guardian_email"] = payload["guardian_email"]
        user["guardian_verified_at"] = db.utcnow()
    conn.commit()
    user["user_token"] = auth.issue("user", user["id"])
    user["account_id"] = account["id"]
    user["email"] = account["email"]
    return user


def verify(email: str, code: str) -> dict:
    """Prove the inbox with the 6-digit code, then enroll the pending user."""
    email = _normalize(email)
    account = db.connect().execute(
        "SELECT * FROM accounts WHERE email=?", (email,)
    ).fetchone()
    if account is None:
        raise AccountError(403, "no pending account for this address")
    if account["verified_at"]:
        raise AccountError(409, "this address is already verified — sign in")
    _consume_code(email, code, "verify")
    return _activate(account)


def verify_link(token: str) -> dict:
    """Prove the inbox with the emailed link's token. The click lands in a
    browser, not the app — the app learns of it by signing in (it holds the
    email and password already), so this returns only what a human-facing
    page needs."""
    row = db.connect().execute(
        "SELECT rowid, * FROM email_codes WHERE code_hash=?"
        " AND purpose='verify-link' AND consumed_at IS NULL",
        (_hash_code(token.strip()),),
    ).fetchone()
    if row is None:
        raise AccountError(403, "this link is not valid — it may have been "
                                "replaced by a newer email or already used")
    if row["expires_at"] < datetime.now(timezone.utc).isoformat():
        raise AccountError(403, "this link has expired — request a new one "
                                "from the app")
    account = db.connect().execute(
        "SELECT * FROM accounts WHERE email=?", (row["email"],)
    ).fetchone()
    if account is None:
        raise AccountError(403, "no pending account for this address")
    if account["verified_at"]:
        return {"email": row["email"], "already": True}
    conn = db.connect()
    conn.execute("UPDATE email_codes SET consumed_at=? WHERE rowid=?",
                 (db.utcnow(), row["rowid"]))
    conn.commit()
    _activate(account)
    return {"email": row["email"], "already": False}


def signin(email: str, password: str) -> dict:
    email = _normalize(email)
    account = db.connect().execute(
        "SELECT * FROM accounts WHERE email=?", (email,)
    ).fetchone()
    # Same answer for "unknown address" and "wrong password" — the split is
    # an address oracle. Constant-work: hash the password either way.
    if account is None:
        _hash_password(password, secrets.token_hex(16))
        raise AccountError(403, "email or password is not right")
    if not secrets.compare_digest(
            account["password_hash"],
            _hash_password(password, account["salt"])):
        raise AccountError(403, "email or password is not right")
    if not account["verified_at"]:
        raise AccountError(
            403, "this address has not been verified — enter the emailed "
                 "code, or request a new one")
    from . import auth
    user = db.connect().execute(
        "SELECT display_name FROM users WHERE id=?", (account["user_id"],)
    ).fetchone()
    return {"account_id": account["id"], "email": email,
            "user_id": account["user_id"],
            "display_name": user["display_name"] if user else None,
            "user_token": auth.issue("user", account["user_id"])}


def request_reset(email: str) -> dict:
    """Email a password-reset code. One response whether or not the address
    has a verified account — not an address oracle."""
    email = _normalize(email)
    row = db.connect().execute(
        "SELECT verified_at FROM accounts WHERE email=?", (email,)
    ).fetchone()
    if row is None or not row["verified_at"]:
        return {"email": email, "code_delivery": "none"}
    return {"email": email, "code_delivery": _send_code(email, "reset")}


def reset_password(email: str, code: str, new_password: str) -> dict:
    """Trade the emailed reset code for a new password. Every existing
    session token dies with the old password — whoever prompted the reset,
    only the person holding the inbox stays signed in."""
    email = _normalize(email)
    if len(new_password) < 8:
        raise AccountError(422, "password must be at least 8 characters")
    conn = db.connect()
    account = conn.execute(
        "SELECT * FROM accounts WHERE email=?", (email,)
    ).fetchone()
    if account is None or not account["verified_at"]:
        raise AccountError(403, "that code is not right")
    _consume_code(email, code, "reset")
    salt = secrets.token_hex(16)
    conn.execute(
        "UPDATE accounts SET password_hash=?, salt=? WHERE id=?",
        (_hash_password(new_password, salt), salt, account["id"]),
    )
    conn.commit()
    from . import auth
    auth.revoke_subject(account["user_id"])
    return {"email": email, "reset": True}


def _revive(payload: dict) -> dict:
    """The pending payload crossed JSON; give ``guardian.enroll`` back the
    shapes it expects (it calls ``.isoformat()`` on the birthdate)."""
    from datetime import date

    out = dict(payload)
    if out.get("birthdate"):
        out["birthdate"] = date.fromisoformat(out["birthdate"])
    return out
