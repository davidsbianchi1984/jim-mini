"""Reaching the person the relay picked.

:func:`jim.relay.escalate` chose a name and wrote it down. That was the whole
escalation: a row in `events` saying *on-call was notified*, when nothing had
been sent anywhere. The loop the relay exists to close — *keep going until a
human accepts* — cannot close if the first step never happened.

Like PDI's `pdi/notify.py`, and for the same reason, this ships **no vendor**.
JIM cannot know how a site reaches its people: a manned control room, one
on-call phone, a pager, a chat webhook, a script that rings a desk. So it posts
a signed JSON envelope to ``JIM_NOTIFY_URL`` and stops. The two products use
the same shape deliberately — an operator running both should be able to point
them at one receiver.

What is different here is what may go in the envelope, and it is the whole
reason this module is not a copy.

**Incident scope, never person scope.** :func:`jim.relay.incident` already
draws that line: a corporate deployment must not become a way for an employer
to hold health data about employees, so the relay is built from the alarm
rather than from the person. An outbound webhook is the easiest place in the
system to lose that — it is a payload leaving the building, quite possibly into
a third-party chat room, and "just add the name so they know who to look for"
is a reasonable-sounding sentence that would undo it. So :func:`_envelope`
takes the incident and copies named fields out of it. It never sees a user
record, and there is no field it could add by accident.

Not even the finder's words go out. Somebody typed those into a page at the
scene; they are evidence and they belong in the alarm, which the responder
reads with their own credentials. A page says *go, now, here* — the rest is one
authenticated request away.

**The alarm is not resolved by being sent.** A delivered page means a phone
rang, not that a person is coming. Acceptance stays a separate, named act
(`relay.accept`), and this module never touches it.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import urllib.error
import urllib.request

from . import db

ENVELOPE = "jim-page/v1"
STATES = ("queued", "sent", "failed")

# What the relay says when it could not reach the person it picked. It is
# surfaced on the escalation result rather than buried in a log, because the
# caller — usually the alarm's own follow-up loop — needs to escalate *past*
# an unreachable name rather than waiting on an acceptance that cannot come.
UNREACHED = ("nobody was reached at this name — the page did not go out, so "
             "do not wait on an acceptance from them")

_TIMEOUT = 4.0


def channel() -> dict:
    """What this deployment has configured, without revealing the URL."""
    url = os.environ.get("JIM_NOTIFY_URL")
    return {
        "configured": bool(url),
        "signed": bool(os.environ.get("JIM_NOTIFY_SECRET")),
        "envelope": ENVELOPE,
        "note": ("escalations are delivered to the configured webhook" if url
                 else "no notification channel is configured — escalations "
                      "are recorded and queued, and say nobody was reached"),
    }


def _sign(body: str, at: str) -> dict:
    secret = os.environ.get("JIM_NOTIFY_SECRET")
    if not secret:
        return {}
    mac = hmac.new(secret.encode(), f"{at}.{body}".encode(), hashlib.sha256)
    return {"X-JIM-Timestamp": at,
            "X-JIM-Signature": f"sha256={mac.hexdigest()}"}


def _post(url: str, envelope: dict, http=None) -> None:
    body = json.dumps(envelope, sort_keys=True)
    headers = {"content-type": "application/json",
               **_sign(body, envelope["at"])}
    if http is not None:                       # injected in tests
        resp = http.post(url, data=body, headers=headers)
        if resp.status_code >= 300:
            raise RuntimeError(f"webhook returned {resp.status_code}")
        return
    from . import offline
    offline.allow(url, "the escalation webhook")
    req = urllib.request.Request(url, data=body.encode(), method="POST",
                                 headers=headers)
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as r:
        if r.status >= 300:
            raise RuntimeError(f"webhook returned {r.status}")


def _envelope(page_id: str, incident: dict, responder: str, role: str,
              on_shift: bool, at: str) -> dict:
    """Built from the incident by copying named fields out of it.

    Not by taking the incident and removing things — a payload assembled by
    deletion is one forgotten line away from being a health record.
    """
    return {
        "envelope": ENVELOPE,
        "id": page_id,
        "at": at,
        "responder": responder,
        "role": role,
        # Whether the rota actually had somebody on. A page that arrives
        # because the relay ran out of rostered people should say so, or the
        # recipient has no way to know they were a guess.
        "on_shift": on_shift,
        "alarm": incident["alarm"],
        "site_label": incident["site_label"],
        "raised_at": incident["raised_at"],
        "needed": incident["needed"],
        "scope": "incident",
        "finder_words_withheld": True,
        "read_the_alarm_at": f"/alarms/{incident['alarm']}",
        "note": ("this is an incident at a site, not a person's health "
                 "record; accepting means attending, and is a separate act"),
    }


class NotifyError(Exception):
    """A page that cannot be sent for a reason the caller should hear."""


def page(incident: dict, user_id: str, responder: str, role: str = "responder",
         on_shift: bool = True, http=None) -> dict:
    """Try to reach one responder about one incident. Never raises."""
    at = db.utcnow()
    page_id = db.new_id("page")
    url = os.environ.get("JIM_NOTIFY_URL")

    state, attempts, err = "queued", 0, None
    if url:
        attempts = 1
        try:
            _post(url, _envelope(page_id, incident, responder, role, on_shift,
                                 at), http)
            state = "sent"
        except (urllib.error.URLError, OSError, RuntimeError, ValueError) as exc:
            # Never re-raised: a webhook that times out must not become an
            # exception on the path that is trying to get somebody help.
            state, err = "failed", f"{type(exc).__name__}: {exc}"[:300]

    conn = db.connect()
    conn.execute(
        "INSERT INTO relay_pages (id, alarm_id, user_id, responder, role,"
        " on_shift, state, attempts, last_error, created_at, sent_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (page_id, incident["alarm"], user_id, responder, role,
         1 if on_shift else 0, state, attempts, err, at,
         at if state == "sent" else None))
    conn.commit()
    return out(page_id)


def retry(page_row: dict, incident: dict, http=None) -> dict:
    """Send a queued or failed page again."""
    if page_row["state"] == "sent":
        raise NotifyError("this page was already delivered")
    if not os.environ.get("JIM_NOTIFY_URL"):
        raise NotifyError("no notification channel is configured")

    at = db.utcnow()
    state, err = "sent", None
    try:
        _post(os.environ["JIM_NOTIFY_URL"],
              _envelope(page_row["id"], incident, page_row["responder"],
                        page_row["role"], bool(page_row["on_shift"]), at), http)
    except (urllib.error.URLError, OSError, RuntimeError, ValueError) as exc:
        state, err = "failed", f"{type(exc).__name__}: {exc}"[:300]

    conn = db.connect()
    conn.execute(
        "UPDATE relay_pages SET state=?, attempts=attempts+1, last_error=?,"
        " sent_at=? WHERE id=?",
        (state, err, at if state == "sent" else None, page_row["id"]))
    conn.commit()
    return out(page_row["id"])


def row(page_id: str) -> dict | None:
    r = db.connect().execute("SELECT * FROM relay_pages WHERE id=?",
                             (page_id,)).fetchone()
    return dict(r) if r else None


def out(page_id: str) -> dict:
    r = row(page_id)
    return {
        "id": r["id"],
        "alarm": r["alarm_id"],
        "responder": r["responder"],
        "role": r["role"],
        "on_shift": bool(r["on_shift"]),
        "state": r["state"],
        "attempts": r["attempts"],
        "last_error": r["last_error"],
        "created_at": r["created_at"],
        "sent_at": r["sent_at"],
        "reached_somebody": r["state"] == "sent",
    }


def for_user(user_id: str, undelivered_only: bool = False) -> list[dict]:
    sql = "SELECT id FROM relay_pages WHERE user_id=?"
    if undelivered_only:
        sql += " AND state != 'sent'"
    sql += " ORDER BY created_at DESC, rowid DESC"
    return [out(r["id"])
            for r in db.connect().execute(sql, (user_id,)).fetchall()]


def for_alarm(alarm_id: str) -> list[dict]:
    return [out(r["id"]) for r in db.connect().execute(
        "SELECT id FROM relay_pages WHERE alarm_id=? ORDER BY created_at,"
        " rowid", (alarm_id,)).fetchall()]
