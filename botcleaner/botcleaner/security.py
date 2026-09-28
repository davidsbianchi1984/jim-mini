"""Token hashing and sealing secrets at rest (OAuth tokens), plus id helpers."""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timezone


def now() -> datetime:
    return datetime.now(timezone.utc)


def iso(d: datetime | None = None) -> str:
    return (d or now()).isoformat()


def parse_iso(s: str | None) -> datetime | None:
    if not s:
        return None
    d = datetime.fromisoformat(s)
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def new_id(prefix: str = "") -> str:
    return prefix + secrets.token_urlsafe(9).replace("-", "a").replace("_", "b")


def new_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def token_matches(token: str, digest: str) -> bool:
    return hmac.compare_digest(hash_token(token), digest)


def _key() -> bytes:
    raw = os.environ.get("BOTCLEANER_SECRET")
    if raw:
        return hashlib.sha256(raw.encode()).digest()
    path = os.environ.get("BOTCLEANER_KEYFILE", ".botcleaner.key")
    if not os.path.exists(path):
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as f:
            f.write(secrets.token_bytes(32))
    with open(path, "rb") as f:
        return f.read()


def seal(plaintext: str, aad: str) -> bytes:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    nonce = secrets.token_bytes(12)
    return nonce + AESGCM(_key()).encrypt(nonce, plaintext.encode(), aad.encode())


def unseal(blob: bytes, aad: str) -> str:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    return AESGCM(_key()).decrypt(blob[:12], blob[12:], aad.encode()).decode()


def b64(s: bytes) -> str:
    return base64.urlsafe_b64encode(s).decode()
