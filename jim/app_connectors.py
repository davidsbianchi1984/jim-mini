"""Connected-app connectors for the Guardian.

A user connects to an AI-integrated app from the catalog (``catalog.py``) — Apple
Photos, Google Calendar, Microsoft 365, Canva, … — and the Guardian's agents use
it in the direction the app supports:

- **collect** — pull context in as consented context that informs guidance;
- **act** — drive the app agentically (create an event, run a shortcut);
- **produce** — generate media.

Connecting grants a subset of the app's catalog capabilities; invoking one the
connector wasn't granted is refused.
"""

from __future__ import annotations

import json

from . import catalog, db, life


def entry(provider: str, app: str) -> dict | None:
    return catalog.BY_KEY.get((provider, app))


def get(cid: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM app_connectors WHERE id=?", (cid,)).fetchone()
    return dict(row) if row else None


def _out(row: dict) -> dict:
    return {
        "id": row["id"], "user_id": row["user_id"], "provider": row["provider"],
        "app": row["app"], "label": row["label"],
        "capabilities": json.loads(row["capabilities"]),
        "directions": json.loads(row["directions"]), "status": row["status"],
        "collected": row["collected"], "actions": row["actions"],
    }


def connect(user_id: str, e: dict, capabilities: list[str]) -> dict:
    caps = capabilities or list(e["capabilities"])
    conn = db.connect()
    cid = db.new_id("app")
    conn.execute(
        "INSERT INTO app_connectors (id, user_id, provider, app, label,"
        " capabilities, directions, status, collected, actions, created_at)"
        " VALUES (?,?,?,?,?,?,?, 'active', 0, 0, ?)",
        (cid, user_id, e["provider"], e["app"], e["label"],
         json.dumps(caps), json.dumps(e["directions"]), db.utcnow()),
    )
    conn.commit()
    if "collect" in e["directions"]:
        life.set_source(user_id, f"app:{e['provider']}:{e['app']}", True)
    return _out(get(cid))


def for_user(user_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM app_connectors WHERE user_id=? ORDER BY created_at, rowid",
        (user_id,)).fetchall()
    return [_out(dict(r)) for r in rows]


def revoke(row: dict) -> dict:
    db.connect().execute("UPDATE app_connectors SET status='revoked' WHERE id=?",
                         (row["id"],))
    db.connect().commit()
    return {"id": row["id"], "status": "revoked"}


def collect(row: dict, items: list[dict], pdi=None) -> dict:
    ingested = 0
    for item in items:
        life.add_context(row["user_id"], f"app:{row['provider']}:{row['app']}",
                         "linked_context", {"content": item.get("content", "")},
                         pdi=pdi)
        ingested += 1
    db.connect().execute(
        "UPDATE app_connectors SET collected = collected + ? WHERE id=?",
        (ingested, row["id"]))
    db.connect().commit()
    return {"connector": row["id"], "app": row["app"], "ingested": ingested,
            "note": f"context from {row['label']} now informs guidance"}


def invoke(row: dict, capability: str, inp: str | None) -> dict:
    db.connect().execute("UPDATE app_connectors SET actions = actions + 1 WHERE id=?",
                         (row["id"],))
    db.connect().commit()
    return {"connector": row["id"], "provider": row["provider"], "app": row["app"],
            "capability": capability, "directions": json.loads(row["directions"]),
            "status": "performed", "input": inp,
            "result": f"{row['label']} · {capability} performed"}
