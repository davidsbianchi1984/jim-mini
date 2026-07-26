"""Cloud contribution: what would leave, what has left, and undoing it.

JIM's settings screen has always offered *"Contribute data — preview before it
leaves"*. The API behind it could do neither half. ``cloud.contribute`` posted a
payload, returned a bool, and wrote nothing down, so:

* **there was no preview** — the screen promised to show what would be sent and
  nothing could answer; and
* **"revocable" meant only "stoppable"** — turning the flag off prevented
  future sends, while everything already contributed stayed at the gateway with
  no record naming it.

Health data makes both worse than they would be elsewhere. A user deciding
whether to share guidance outcomes is entitled to see the actual bytes, not a
description of them, and a decision they can only apply going forward is not
the consent the screen implies.

**One payload builder, used by both paths.** :func:`payload_for` produces what
a contribution sends, and the preview calls that same function rather than
reconstructing something that looks like it. A preview assembled separately is
a *description* of the payload, and descriptions drift from what they describe
— which is the exact failure mode this endpoint exists to correct.

What is sent stays as narrow as it always was: the condition domain, the
severity, and the rating. Never ids, names, notes, or raw biometrics. The
``ref`` is random and carries no identity — only :data:`contribution_log` maps
it back to a user — so a revocation can name items at the gateway without
telling it who is revoking.
"""

from __future__ import annotations

import json

from . import db


def payload_for(user_id: str, rating: str | None) -> dict | None:
    """The exact payload a contribution sends, or None if there is nothing to
    contribute yet.

    ``rating`` is the one field supplied by the moment rather than the record,
    so the preview passes None and the real send passes the rating being given.
    """
    last = db.connect().execute(
        "SELECT condition, severity FROM events"
        " WHERE user_id=? AND type='guidance'"
        " ORDER BY created_at DESC, rowid DESC LIMIT 1",
        (user_id,)).fetchone()
    if last is None:
        return None
    return {
        "source": "jim-mini",
        "kind": "guidance_outcome",
        "condition": last["condition"],
        "severity": last["severity"],
        "rating": rating,
    }


def send(user_id: str, rating: str, cloud) -> bool:
    """Contribute one guidance outcome and log exactly what left.

    The log is written only on a send the gateway accepted — a failed post
    contributed nothing, and recording it would offer the user a revoke button
    for data that never left.
    """
    payload = payload_for(user_id, rating)
    if payload is None:
        return False
    ref = db.new_id("ctb")
    payload = {"ref": ref, **payload}
    if not cloud.contribute(payload):
        return False
    conn = db.connect()
    conn.execute(
        "INSERT INTO contribution_log (ref, user_id, payload, contributed_at)"
        " VALUES (?,?,?,?)", (ref, user_id, json.dumps(payload), db.utcnow()))
    conn.commit()
    return True


def history(user_id: str) -> list[dict]:
    """Everything this user has ever contributed, with the payload verbatim."""
    return [{"ref": r["ref"], "at": r["contributed_at"],
             "revoked": bool(r["revoked"]),
             "payload": json.loads(r["payload"])}
            for r in db.connect().execute(
                "SELECT * FROM contribution_log WHERE user_id=?"
                " ORDER BY contributed_at, rowid", (user_id,)).fetchall()]


def view(user_id: str, opted_in: bool) -> dict:
    """The whole picture for the settings screen: whether it is on, exactly
    what the next contribution would carry, and everything already sent."""
    preview = payload_for(user_id, None)
    return {
        "opted_in": opted_in,
        "policy": "only the condition domain, severity, and your rating of "
                  "the guidance — never ids, names, notes, or raw biometrics; "
                  "each item carries a random ref so it can be deleted at the "
                  "gateway without identifying you",
        "preview_next": preview,
        "preview_note": None if preview is None else
                        "exactly what the next contribution would send; "
                        "`rating` is filled in with the rating you give",
        "contributed": history(user_id),
    }


def revoke(user_id: str, cloud) -> dict:
    """Turn contribution off **and** delete what has already gone.

    The local rows are marked revoked whether or not the gateway could be
    reached, and the result says which happened. Leaving them unmarked on an
    outage would show the user their data as still-shared after they revoked
    it, and quietly marking them regardless would claim a deletion that never
    happened — so the honest answer is both facts, separately.
    """
    conn = db.connect()
    conn.execute("UPDATE users SET cloud_contribution=0 WHERE id=?", (user_id,))
    refs = [r["ref"] for r in conn.execute(
        "SELECT ref FROM contribution_log WHERE user_id=? AND revoked=0",
        (user_id,)).fetchall()]
    conn.execute("UPDATE contribution_log SET revoked=1 WHERE user_id=?",
                 (user_id,))
    conn.commit()

    if not refs:
        deleted = True
    elif cloud is None:
        deleted = False
    else:
        deleted = cloud.revoke_contributions(refs)
    return {
        "opted_in": False,
        "revoked": len(refs),
        "gateway_deleted": deleted,
        "note": "contribution is off and your local record is marked revoked"
                + ("; the gateway confirmed deletion" if deleted else
                   "; the gateway could not be reached, so deletion there is "
                   "not confirmed — the refs stay recorded so it can be "
                   "retried"),
    }
