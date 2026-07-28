"""Outbound email for JIM-mini — verification codes, nothing else.

Two transports, chosen by configuration rather than code:

* **smtp** — when ``JIM_SMTP_HOST`` is set, real delivery via ``smtplib``
  (``JIM_SMTP_PORT`` default 587 with STARTTLS, ``JIM_SMTP_USER`` /
  ``JIM_SMTP_PASSWORD`` optional, ``JIM_SMTP_FROM`` default the user name).
* **console** — otherwise the message is printed to the server's stdout.
  A laptop deployment has no mail credentials and still needs a working
  signup: the person reads the code from the terminal they started
  ``python -m jim serve`` in. The transport name travels in the API
  response, so a client can say where to look — but never the code itself.
"""

from __future__ import annotations

import logging
import os
import smtplib
from email.message import EmailMessage

logger = logging.getLogger("jim.mailer")


def configured_transport() -> str:
    return "smtp" if os.environ.get("JIM_SMTP_HOST") else "console"


def deliver(to: str, subject: str, body: str) -> str:
    """Send ``body`` to ``to``; return the transport that carried it."""
    if configured_transport() == "smtp":
        host = os.environ["JIM_SMTP_HOST"]
        port = int(os.environ.get("JIM_SMTP_PORT", "587"))
        user = os.environ.get("JIM_SMTP_USER")
        password = os.environ.get("JIM_SMTP_PASSWORD")
        sender = os.environ.get("JIM_SMTP_FROM") or user or "jim@localhost"
        msg = EmailMessage()
        msg["From"], msg["To"], msg["Subject"] = sender, to, subject
        msg.set_content(body)
        with smtplib.SMTP(host, port, timeout=30) as smtp:
            smtp.starttls()
            if user and password:
                smtp.login(user, password)
            smtp.send_message(msg)
        logger.info("verification email sent to %s via smtp", to)
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
