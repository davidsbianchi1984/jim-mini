"""Social-platform connections for the Guardian.

Two directions, mirroring the rest of the suite:

- **collect** — pull the account's posts in as *consented context* that informs
  guidance. Each item is ingested exactly like any other context event
  (``social:<platform>`` source), sealed in the PDI vault when configured, so
  the Guardian understands more of the user's life.
- **publish** — share an update *on* the platform (a milestone, an all-clear),
  reachable by a QR beacon.

Collecting auto-consents the ``social:<platform>`` source; revoking withdraws
that consent, so no further context is ingested.
"""

from __future__ import annotations

import json

from . import db, life

_PLATFORM_URL = {
    "instagram": "https://instagram.com/{h}",
    "x": "https://x.com/{h}",
    "tiktok": "https://tiktok.com/@{h}",
    "facebook": "https://facebook.com/{h}",
    "linkedin": "https://linkedin.com/in/{h}",
    "youtube": "https://youtube.com/@{h}",
    "reddit": "https://reddit.com/user/{h}",
    "threads": "https://threads.net/@{h}",
    "whatsapp": "https://wa.me/{h}",
    "meta": "https://meta.com/{h}",
    "mastodon": "https://mastodon.social/@{h}",
    "twitch": "https://twitch.tv/{h}",
    "snapchat": "https://snapchat.com/add/{h}",
    "roblox": "https://roblox.com/users/{h}",
    "pinterest": "https://pinterest.com/{h}",
    "discord": "https://discord.com/users/{h}",
}


def _out(row: dict) -> dict:
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "platform": row["platform"],
        "direction": row["direction"],
        "handle": f"@{row['handle']}" if row["handle"] else None,
        "scope": json.loads(row["scope"]),
        "status": row["status"],
        "collected": row["collected"],
        "published": row["published"],
        "beacon": f"/social/{row['id']}/beacon" if row["direction"] == "publish" else None,
    }


def get(cid: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM social_connections WHERE id=?", (cid,)).fetchone()
    return dict(row) if row else None


def connect(user_id: str, platform: str, direction: str,
            handle: str | None, scope: list[str]) -> dict:
    conn = db.connect()
    cid = db.new_id("soc")
    handle = (handle or "").lstrip("@") or None
    conn.execute(
        "INSERT INTO social_connections (id, user_id, platform, direction,"
        " handle, scope, status, collected, published, created_at)"
        " VALUES (?,?,?,?,?,?, 'active', 0, 0, ?)",
        (cid, user_id, platform, direction, handle, json.dumps(scope), db.utcnow()),
    )
    conn.commit()
    if direction == "collect":
        # Pulling posts in is a consented data source like any other.
        life.set_source(user_id, f"social:{platform}", True)
    return _out(get(cid))


def for_user(user_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM social_connections WHERE user_id=?"
        " ORDER BY created_at, rowid", (user_id,)).fetchall()
    return [_out(dict(r)) for r in rows]


def revoke(row: dict) -> dict:
    conn = db.connect()
    conn.execute("UPDATE social_connections SET status='revoked' WHERE id=?",
                 (row["id"],))
    conn.commit()
    if row["direction"] == "collect":
        others = conn.execute(
            "SELECT COUNT(*) AS c FROM social_connections WHERE user_id=?"
            " AND platform=? AND direction='collect' AND status='active' AND id<>?",
            (row["user_id"], row["platform"], row["id"])).fetchone()["c"]
        if not others:
            life.set_source(row["user_id"], f"social:{row['platform']}", False)
    return {"id": row["id"], "status": "revoked"}


def collect(row: dict, items: list[dict], pdi=None) -> dict:
    ingested = 0
    for item in items:
        life.add_context(row["user_id"], f"social:{row['platform']}",
                         "social_post", {"content": item.get("content", "")},
                         pdi=pdi)
        ingested += 1
    conn = db.connect()
    conn.execute("UPDATE social_connections SET collected = collected + ? WHERE id=?",
                 (ingested, row["id"]))
    conn.commit()
    return {"connection": row["id"], "platform": row["platform"],
            "ingested": ingested,
            "note": "collected posts now inform this user's guidance"}


def publish(row: dict, content: str, topic: str | None) -> dict:
    conn = db.connect()
    conn.execute("UPDATE social_connections SET published = published + 1 WHERE id=?",
                 (row["id"],))
    conn.commit()
    return {"connection": row["id"], "platform": row["platform"],
            "surface": f"social:{row['platform']}", "topic": topic,
            "content": content, "status": "published"}


def presence_url(row: dict, public_base: str) -> str:
    if row["handle"] and row["platform"] in _PLATFORM_URL:
        return _PLATFORM_URL[row["platform"]].format(h=row["handle"])
    return f"{public_base}/social/{row['id']}"
