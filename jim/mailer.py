"""Outbound email for JIM-mini — verification codes and links, nothing else.

Where mail goes through is configuration, not code. In order of precedence:

* **environment** — ``JIM_SMTP_HOST`` and friends. A server deployment sets
  these and keeps its credentials out of the database entirely.
* **the app's own settings** (``mail_settings``, one row) — set from the
  Settings screen, so somebody running the desktop app can point it at their
  own mail account without ever meeting an environment variable. This is
  what turns "no email ever arrives" into a real inbox message.
* **neither** — the message is printed to the server's stdout, and signup
  stops pretending an inbox can be proven (see ``jim/accounts.py``): a
  machine that cannot send mail cannot verify an address, so the local
  account is activated directly instead of waiting for a letter that will
  never come.

The password is stored as given. It is the machine owner's own credential
on the machine they own — but it is never returned by the API, and an
app-specific password (Gmail's, and every provider's equivalent) is the
right thing to paste in, because it can be revoked without touching the
account it belongs to.
"""

from __future__ import annotations

import logging
import os
import smtplib
from email.message import EmailMessage

logger = logging.getLogger("jim.mailer")

DEFAULT_PORT = 587


def stored_settings() -> dict | None:
    """The row from the app's Settings screen, if one has been saved."""
    from . import db

    try:
        row = db.connect().execute(
            "SELECT * FROM mail_settings WHERE id=1").fetchone()
    except Exception:  # noqa: BLE001 — a database older than this table
        return None
    return dict(row) if row else None


def save_settings(host: str, port: int = DEFAULT_PORT, username: str = "",
                  password: str = "", sender: str = "",
                  public_url: str = "") -> dict:
    from . import db

    if not host.strip():
        raise ValueError("a mail server host is required")
    conn = db.connect()
    conn.execute(
        "INSERT INTO mail_settings (id, host, port, username, password,"
        " sender, public_url, updated_at) VALUES (1,?,?,?,?,?,?,?)"
        " ON CONFLICT(id) DO UPDATE SET host=excluded.host, port=excluded.port,"
        " username=excluded.username, password=excluded.password,"
        " sender=excluded.sender, public_url=excluded.public_url,"
        " updated_at=excluded.updated_at",
        (host.strip(), int(port), username.strip(), password,
         sender.strip(), public_url.strip().rstrip("/"), db.utcnow()),
    )
    conn.commit()
    logger.info("mail settings saved: %s:%s", host.strip(), port)
    return describe_settings()


def clear_settings() -> dict:
    from . import db

    conn = db.connect()
    conn.execute("DELETE FROM mail_settings WHERE id=1")
    conn.commit()
    return describe_settings()


def describe_settings() -> dict:
    """What the API may say about the mail configuration — never the
    password, and never the environment's secrets either."""
    row = stored_settings()
    env_host = os.environ.get("JIM_SMTP_HOST")
    return {
        "transport": configured_transport(),
        "source": "environment" if env_host else ("settings" if row else "none"),
        "host": env_host or (row["host"] if row else None),
        "port": int(os.environ.get("JIM_SMTP_PORT", 0)) or (
            row["port"] if row else DEFAULT_PORT),
        "username": os.environ.get("JIM_SMTP_USER") or (
            row["username"] if row else None),
        "sender": os.environ.get("JIM_SMTP_FROM") or (
            row["sender"] if row else None),
        "public_url": public_url(),
        "password_set": bool(os.environ.get("JIM_SMTP_PASSWORD")
                             or (row and row["password"])),
    }


def _resolved() -> dict | None:
    """The settings actually used to send, or None when nothing is set."""
    if os.environ.get("JIM_SMTP_HOST"):
        return {
            "host": os.environ["JIM_SMTP_HOST"],
            "port": int(os.environ.get("JIM_SMTP_PORT", DEFAULT_PORT)),
            "username": os.environ.get("JIM_SMTP_USER", ""),
            "password": os.environ.get("JIM_SMTP_PASSWORD", ""),
            "sender": os.environ.get("JIM_SMTP_FROM", ""),
        }
    row = stored_settings()
    return dict(row) if row else None


def public_url() -> str:
    """What a verification link should point at."""
    env = os.environ.get("JIM_PUBLIC_URL")
    if env:
        return env.rstrip("/")
    row = stored_settings()
    if row and row["public_url"]:
        return row["public_url"].rstrip("/")
    return f"http://127.0.0.1:{os.environ.get('JIM_PORT', '8000')}"


def configured_transport() -> str:
    return "smtp" if _resolved() else "console"


def deliver(to: str, subject: str, body: str) -> str:
    """Send ``body`` to ``to``; return the transport that carried it."""
    settings = _resolved()
    if settings:
        sender = settings.get("sender") or settings.get("username") \
            or "jim@localhost"
        msg = EmailMessage()
        msg["From"], msg["To"], msg["Subject"] = sender, to, subject
        msg.set_content(body)
        from . import offline
        offline.allow_host(settings["host"], "sending mail")
        with smtplib.SMTP(settings["host"], int(settings["port"]),
                          timeout=30) as smtp:
            smtp.starttls()
            if settings.get("username") and settings.get("password"):
                smtp.login(settings["username"], settings["password"])
            smtp.send_message(msg)
        logger.info("mail sent to %s via %s", to, settings["host"])
        return "smtp"
    # Console delivery: deliberately print()ed rather than logged, so it shows
    # at every log level, in the terminal the operator is already watching.
    # ASCII only: the frozen Windows backend's stdout is cp1252, and a banner
    # drawn with box characters raised UnicodeEncodeError — which turned
    # every signup into a 500 on the one platform this path serves most.
    print(f"\n=== JIM mail (no SMTP configured) ===\n"
          f"To: {to}\nSubject: {subject}\n\n{body}\n"
          f"=====================================\n")
    return "console"
