"""Capability-token authentication.

JIM-mini holds a person's most sensitive data — biometric streams, crisis
notes, a journal, a provider-shareable summary. Identity must be proven, not
asserted. Enrollment mints a **user token** (returned once); every
per-user surface requires it.

Only the SHA-256 hash of a token is persisted, so a database leak never yields
a usable credential. Setup and health surfaces (`/health`, `/cloud/status`,
`/enroll`, `/specialists`) need no token.

Above that sits an optional **deployment gate**. On a laptop or a LAN,
anyone who can reach the API can enroll — the right default when reaching it
already means being in the house. A deployment published to the internet is
different: without a gate, whoever finds the URL can enroll on it. Setting
``JIM_SIGNUP_KEY`` requires that key to enroll, so a hosted instance stays
the operator's and their colleagues'. Unset, nothing changes.
"""

from __future__ import annotations

import hashlib
import os
import secrets

from fastapi import HTTPException, Request

from . import db


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def issue(role: str, subject_id: str) -> str:
    """Mint a token for ``subject_id`` in ``role`` and return it once."""
    token = secrets.token_urlsafe(32)
    conn = db.connect()
    conn.execute(
        "INSERT INTO api_tokens (token_hash, role, subject_id, created_at)"
        " VALUES (?,?,?,?)",
        (_hash(token), role, subject_id, db.utcnow()),
    )
    conn.commit()
    return token


def bearer(request: Request) -> str | None:
    header = request.headers.get("authorization", "")
    if header.lower().startswith("bearer "):
        return header[7:].strip() or None
    return None


def principal(request: Request) -> dict | None:
    """Resolve the caller's token to ``{role, subject_id}``, or None."""
    token = bearer(request)
    if not token:
        return None
    row = db.connect().execute(
        "SELECT role, subject_id FROM api_tokens WHERE token_hash=?",
        (_hash(token),),
    ).fetchone()
    return dict(row) if row else None


def require(request: Request, role: str, subject_id: str) -> None:
    """Authorize the caller for (``role``, ``subject_id``) or raise: 401 when
    no valid token is presented, 403 when the token grants something else."""
    who = principal(request)
    if who is None:
        raise HTTPException(401, "authentication required")
    if who["role"] != role or who["subject_id"] != subject_id:
        raise HTTPException(403, "not authorized for this user")


def revoke_subject(subject_id: str) -> None:
    """Drop every token for a subject (called on erasure)."""
    conn = db.connect()
    conn.execute("DELETE FROM api_tokens WHERE subject_id=?", (subject_id,))
    conn.commit()


def require_signup_key(request: Request) -> None:
    """Deployment-level gate for enrolling.

    Unset ``JIM_SIGNUP_KEY`` means open, which is what a laptop or LAN
    deployment wants. When it is set — the sensible posture for anything
    published — the caller must present it as ``x-signup-key``. This gates
    *who may create an account here*; it does not replace the per-user
    token, which still authorizes every personal surface afterwards.
    """
    required = os.environ.get("JIM_SIGNUP_KEY")
    if not required:
        return
    presented = request.headers.get("x-signup-key", "")
    # Constant-time compare so a wrong key can't be recovered by timing.
    if not (presented and secrets.compare_digest(presented, required)):
        raise HTTPException(
            403, "this deployment requires a signup key to enroll — send it "
                 "as the x-signup-key header")
