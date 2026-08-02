"""The account was gone and the wrist kept writing.

## The finding

`life.delete_user_data` opens with *"Erase every trace of a user across all
tables — and the PDI vault."* It empties the vault, walks eighteen tables and
removes the `users` row last, and the API answers 404 for that id afterwards.

`watch_channels` was not one of the eighteen. Its `token` is the drip address:
a URL typed into an Apple Shortcut, sometimes weeks before, that deposits
readings into one user's stream. Driven end to end:

    DELETE /data/{id}   200   {"events": 1, "baselines": 2, ...}
    GET    /users/{id}  404   the account is gone
    POST   /watch/drip/{token}
                        200   {"received": 1}   ← and an `events` row is back

    asked     did we delete the user's data
    mattered  can anything still write more

The reading ran the full Guardian pipeline under an id that no longer resolves,
so an erased account grew rows again from a credential its owner had no way to
find and no screen left to rotate.

Two other tables in the same shape went with it: `contribution_log` (which
records what was shared with the cloud, and whose `revoked` column is the whole
mechanism for withdrawing it) and `waivers`. Both are standing permissions
rather than records of something that happened.

## What this file checks, and what it does not

The generalisation here is deliberately narrow: **a user-scoped table carrying
a live credential or a standing permission must not survive the erase.** That
is checkable, and it is the class this defect belongs to.

It is not the wider question. Thirty user-scoped tables hold ordinary data and
are also untouched by a function whose first line says "every trace" — that is
a real gap, it is recorded here rather than hidden, and it is a decision about
what deletion means rather than a defect with a receipt. This round does not
take it.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from jim import db


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
LIFE = REPO / "jim" / "life.py"

#: User-scoped tables carrying a credential or standing permission that the
#: erase deliberately leaves, each with the reason. Empty, and that is the
#: point: three sat outside the erase and none of them was a decision.
EXEMPT: dict[str, str] = {}


def _credential_tables() -> list[tuple[str, list[str]]]:
    """Every user-scoped table with a token or a revocation flag, read from the
    schema the product creates rather than from a list in this file."""
    conn = db.connect()
    out = []
    for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'").fetchall():
        cols = [c["name"] for c in conn.execute(
            f"PRAGMA table_info({row['name']})")]
        if "user_id" not in cols:
            continue
        marks = [c for c in cols
                 if "revok" in c or c in ("token", "token_hash")]
        if marks:
            out.append((row["name"], marks))
    return sorted(out)


def _tables_the_erase_touches() -> set[str]:
    """Table names out of `delete_user_data`'s own string literals — bare words
    from the loop, plus any written into an f-string statement."""
    src = LIFE.read_text(encoding="utf-8")
    fn = next(n for n in ast.walk(ast.parse(src))
              if isinstance(n, ast.FunctionDef) and n.name == "delete_user_data")
    found: set[str] = set()
    for node in ast.walk(fn):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if re.fullmatch(r"\w+", node.value):
                found.add(node.value)
            found.update(re.findall(r"(?:DELETE FROM|UPDATE)\s+(\w+)",
                                    node.value))
    return found


def test_the_erase_takes_every_live_credential_with_it(client):
    """The generalisation. Naming the drip channel — the one found by hand —
    would have left the other two."""
    touched = _tables_the_erase_touches()
    left = [f"{name} ({', '.join(marks)})"
            for name, marks in _credential_tables()
            if name not in touched and name not in EXEMPT]
    assert not left, (
        f"{len(left)} table(s) survive an erase holding a live credential or a "
        "standing permission for a user who has been deleted:\n    "
        + "\n    ".join(left))


def test_the_credential_scan_is_finding_tables(client):
    """A guard on the guard: a scan that stopped matching would report nothing
    left behind and pass on an empty set."""
    found = _credential_tables()
    assert len(found) >= 4, (
        f"only {len(found)} user-scoped credential table(s) found — this "
        "schema has four, and the check above is passing on almost nothing")


def test_every_exemption_still_names_a_real_table(client):
    live = {name for name, _ in _credential_tables()}
    stale = sorted(t for t in EXEMPT if t not in live)
    assert not stale, (
        "these exemptions name tables that no longer carry a user-scoped "
        "credential — strike them:\n    " + "\n    ".join(stale))


# --- driven -----------------------------------------------------------------

def _enroll(client, name="Dana"):
    r = client.post("/enroll", json={
        "display_name": name, "birthdate": "1990-01-01",
        "terms_consent": True, "resting_heart_rate": 60})
    assert r.status_code == 201, r.text
    return r.json()


def _auth(u):
    return {"authorization": f"Bearer {u['user_token']}"}


def _drip_url(client, u):
    r = client.get(f"/watch/channel/{u['id']}", headers=_auth(u))
    assert r.status_code == 200, r.text
    return "/watch/drip/" + r.json()["drip_url"].rsplit("/", 1)[1]


def test_the_drip_address_dies_with_the_account(client):
    """The defect, driven. Before this round: 200, and the reading landed."""
    u = _enroll(client)
    url = _drip_url(client, u)
    assert client.post(url, json={"heart_rate": 62}).status_code == 200
    assert client.delete(f"/data/{u['id']}", headers=_auth(u)).status_code == 200
    r = client.post(url, json={"heart_rate": 62})
    assert r.status_code == 404, (
        f"an erased account still has a live deposit address ({r.status_code})")


def test_nothing_is_written_back_under_a_deleted_id(client):
    """The consequence rather than the status code: the erased account does not
    grow rows again."""
    u = _enroll(client)
    url = _drip_url(client, u)
    client.post(url, json={"heart_rate": 62})
    client.delete(f"/data/{u['id']}", headers=_auth(u))
    client.post(url, json={"heart_rate": 62})
    left = db.connect().execute(
        "SELECT COUNT(*) AS n FROM events WHERE user_id=?", (u["id"],)
    ).fetchone()["n"]
    assert left == 0, (
        f"{left} event row(s) exist for a user the API answers 404 for")


def test_a_live_account_still_drips(client):
    """The erase closes the channel and must not touch anybody else's."""
    mine = _enroll(client, "Dana")
    theirs = _enroll(client, "Sam")
    url = _drip_url(client, theirs)
    client.delete(f"/data/{mine['id']}", headers=_auth(mine))
    assert client.post(url, json={"heart_rate": 61}).status_code == 200


def test_the_channel_row_itself_is_gone(client):
    """The join in `_user_for_token` is the second stop, not the only one — a
    channel row left standing is a token still sitting in the database."""
    u = _enroll(client)
    _drip_url(client, u)
    client.delete(f"/data/{u['id']}", headers=_auth(u))
    left = db.connect().execute(
        "SELECT COUNT(*) AS n FROM watch_channels WHERE user_id=?", (u["id"],)
    ).fetchone()["n"]
    assert left == 0, "the drip channel row outlived the account"


def test_the_token_alone_is_not_enough(client):
    """The join, on its own. A channel row that somehow survives must still not
    resolve to a user who is gone — this is what closes the class rather than
    the one path."""
    from jim import watch

    u = _enroll(client)
    token = watch.channel(u["id"])["token"]
    db.connect().execute("DELETE FROM users WHERE id=?", (u["id"],))
    db.connect().commit()
    r = client.post(f"/watch/drip/{token}", json={"heart_rate": 62})
    assert r.status_code == 404, (
        f"a channel resolved to a user who does not exist ({r.status_code})")
