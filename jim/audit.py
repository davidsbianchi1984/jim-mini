"""Append-only, hash-chained audit log — ported from PDI.

Each entry's hash covers the previous entry's hash, so a retroactive edit or a
deleted row breaks the chain and :func:`verify` says where.

    asked     is there a record of what this Guardian did
    mattered  can somebody tell whether that record was edited afterwards

## Why this is not `events`

`events` is the person's own timeline: readings, detections, guidance, the
escalation ladder's decisions. It is written to be read on a screen, its shape
follows what the screen needs, and it is theirs. This is the other reader —
somebody asking, later and possibly in an argument, whether the record they
are looking at is the record that was written. Those are different jobs and
one table doing both would serve neither: a timeline gets pruned, reshaped and
paginated, and every one of those is indistinguishable from tampering once the
same rows are load-bearing for evidence.

So `events` is untouched by this file. Nothing is moved, nothing is
deprecated, and the consequential acts appear in both — the timeline for the
person, the chain for the question about the timeline.

## What is on the chain

Not everything, on purpose. A chain of every read is a chain nobody verifies
and a database that grows without a reader; PDI's covers the vault's doors and
nothing else. This one covers the acts that reach outside the person's own
screen — help being summoned, a human answering it, a mandate over money, a
grant being opened or closed, and the two ends of a life: consent given, and
data erased.

## The chain's own honesty

The stored and hashed fields are fixed (:data:`EVENT_FIELDS`). `category` is
derived from the action at read time rather than stored, so the catalogue below
can be enriched forever without altering — or breaking — a single existing
hash. That is PDI's design and the reason its chain has survived a dozen
releases of new actions; it is repeated here deliberately rather than
improved on.
"""

from __future__ import annotations

import hashlib
import json

from . import db

_GENESIS = "0" * 64

#: The catalogue: action -> (category, human description).
#:
#: Deliberately short to begin with. The specification this answers says to
#: start with three conditions rather than thirty, and the same discipline
#: applies to an audit catalogue: a small set somebody actually reads beats a
#: large one nobody does. It grows when an act arrives that a reader would ask
#: about, which is a lower bar than "an act happened".
ACTIONS: dict[str, tuple[str, str]] = {
    # -- the safety path: everything that can end with somebody arriving ----
    "watch.arm": ("safety", "crash watch armed — the consent moment, made while the person was well"),
    "watch.disarm": ("safety", "crash watch disarmed — nobody is being watched for from this moment"),
    "watch.trip": ("safety", "crash watch tripped: an alarming reading went unanswered and help was summoned"),
    "alarm.accept": ("safety", "a named human said they are going"),
    "alarm.clear": ("safety", "an alarm was closed — the person is safe"),
    "alarm.escalate": ("safety", "the trusted channel was paged again; the first page was not the only one"),
    "beacon.alarm": ("safety", "a passer-by raised an alarm from a care beacon"),
    "emergency.raise": ("safety", "the account holder pressed Get help now"),
    "dial.held": ("safety", "an emergency connection was assembled and routed to the dialer, and the dialer held the send shut — no call was placed"),
    "contact.called": ("safety", "an emergency contact was called with a JIM-composed message — the reach-out cascade's first act toward a person"),
    "contact.reached": ("safety", "an emergency contact chose to receive the message; the exchange with them is documented"),
    "contact.declined": ("safety", "an emergency contact pressed do-not-call-again; that number is not called for this person again"),
    "contact.unreached": ("safety", "an emergency contact did not answer or consent; the cascade moves to the next person"),
    "reachout.exhausted": ("safety", "every emergency contact was tried without reaching one; the held 911 rung is where the cascade ends"),
    "mail.received": ("life", "an inbound email was taken into the moderated mailbox for the agent to answer"),
    "mail.drafted": ("life", "the agent composed an email reply and held it for a person to approve before sending"),
    "mail.sent": ("life", "a moderator approved a drafted email and it was carried out over the configured mail transport"),
    "mail.staged": ("life", "a moderator approved a drafted email but no mail transport is wired, so it is held composed rather than sent"),
    "mail.discarded": ("life", "a moderator discarded a drafted email; nothing was sent and the draft was thrown away"),

    # -- money: no transaction can occur, so the audited act is the grant ---
    "mandate.set": ("money", "a written mandate over money was granted, with caps"),
    "mandate.clear": ("money", "a money mandate was withdrawn"),

    # -- what the Guardian was allowed to touch ----------------------------
    "grant.open": ("access", "a permission area was opened to the Guardian"),
    "grant.close": ("access", "a permission area was closed"),
    "engaged.act": ("access", "an engaged session changed something on the account"),
    "engaged.undo": ("access", "an engaged session's change was taken back"),

    # -- the two ends of a life --------------------------------------------
    "account.enroll": ("life", "an account was created and terms consented to"),
    "account.export": ("life", "the person took a copy of their own data"),
    "account.erase": ("life", "the person's data was erased at their request"),
}

#: The fields that are stored and hashed. Fixed — see the module docstring.
EVENT_FIELDS = {
    "seq": "monotonic sequence number (chain order)",
    "user_id": "the person the event belongs to (null for deployment-wide events)",
    "action": "one of the catalogued actions",
    "category": "derived group for the action (safety, money, access, life)",
    "ref": "resource reference — an alarm id, an area name, or a small detail",
    "at": "UTC ISO-8601 timestamp",
    "prev_hash": "SHA-256 of the previous entry (chain link)",
    "hash": "SHA-256 over prev_hash + {user_id, action, ref, at}",
}


def category(action: str) -> str:
    return ACTIONS.get(action, ("other", ""))[0]


def schema() -> dict:
    """The audit schema: fields, the catalogue, and the retention stance."""
    return {
        "event_fields": EVENT_FIELDS,
        "actions": [{"action": a, "category": c, "description": d}
                    for a, (c, d) in sorted(ACTIONS.items())],
        "retention": ("append-only and SHA-256 hash-chained; kept for the "
                      "life of the deployment. Erasing a person's data is "
                      "itself recorded here rather than removing what the "
                      "chain already said — a chain with a hole in it is not "
                      "evidence of anything."),
    }


def _hash(prev_hash: str, entry: dict) -> str:
    payload = prev_hash + json.dumps(entry, sort_keys=True)
    return hashlib.sha256(payload.encode()).hexdigest()


def record(action: str, *, user_id: str | None = None,
           ref: str | None = None) -> dict:
    """Append one entry. Unknown actions are accepted rather than refused:
    a call site that reaches for a name nobody catalogued should still leave
    a trace — `category()` reports it as `other`, and the guard on this module
    fails the build so it is named before it ships."""
    conn = db.connect()
    row = conn.execute(
        "SELECT hash FROM audit ORDER BY seq DESC LIMIT 1").fetchone()
    prev_hash = row["hash"] if row else _GENESIS
    entry = {"user_id": user_id, "action": action, "ref": ref,
             "at": db.utcnow()}
    h = _hash(prev_hash, entry)
    conn.execute(
        "INSERT INTO audit (user_id, action, ref, at, prev_hash, hash)"
        " VALUES (?,?,?,?,?,?)",
        (user_id, action, ref, entry["at"], prev_hash, h))
    conn.commit()
    return {**entry, "hash": h}


def entries(user_id: str | None = None) -> list[dict]:
    """The chain, in order. Scoped to one person, or the whole thing."""
    conn = db.connect()
    if user_id:
        rows = conn.execute(
            "SELECT * FROM audit WHERE user_id=? ORDER BY seq",
            (user_id,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM audit ORDER BY seq").fetchall()
    return [{**dict(r), "category": category(r["action"])} for r in rows]


def verify() -> dict:
    """Recompute the chain; report whether it is intact.

    Always over the whole chain rather than one person's slice: the links run
    through every row in sequence, so a per-user verification would be
    checking a subset of a structure the subset does not describe.

    Two names differ from PDI's, and the same guard asked for both.

    `broken_at_seq` is always present — null when the chain is whole. PDI
    omits the key on the intact path and this port deliberately does not: four
    clients decode this, and a key that appears and disappears is two shapes
    on one wire.

    The row count is `hashed` rather than PDI's `entries`, because `entries`
    already means *a list of rows* elsewhere in this API and here it would
    have meant *a number*. `checked` was the first attempt and it was taken
    too — `jim/voice.py` returns it as a boolean. One wire name, one type,
    even when it costs the obvious word twice.
    """
    conn = db.connect()
    rows = conn.execute("SELECT * FROM audit ORDER BY seq").fetchall()
    prev_hash = _GENESIS
    for r in rows:
        entry = {"user_id": r["user_id"], "action": r["action"],
                 "ref": r["ref"], "at": r["at"]}
        expected = _hash(prev_hash, entry)
        if r["prev_hash"] != prev_hash or r["hash"] != expected:
            return {"intact": False, "broken_at_seq": r["seq"],
                    "hashed": len(rows)}
        prev_hash = r["hash"]
    return {"intact": True, "broken_at_seq": None, "hashed": len(rows)}
