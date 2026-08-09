"""An export is measured against the schema too — and drops the credentials.

0.59.9 derived the **erase** from the schema in all three products, because
the lists that stood in for it had gone stale: an operation advertised as
*every trace* reached a third of the tables. The export is the same question
turned round, and it was worse.

## What it was

This product had **no export at all**. It keeps a medicine cabinet, a money
guardian's accounts and mandates, clinical captures, a journal and a
continuity vector, and offered its owner a way to erase all of it and no way
to take it — while the suite gateway's GDPR Article 20 bundle listed this
product's contribution as *a progress report*.

Next door, QRME's `GET /profiles/{id}/export` said *full data export — access
everything, anytime (You Own It)*, had a README row pointing at it under **You
own it / total control**, and returned **six tables of sixty-six**.

    asked     can a person delete everything we hold
    mattered  can a person see everything we hold

## Two properties, and the second is not the first

An export must be **complete** and must **not hand back a live credential**.
Those pull in opposite directions, and the honest resolution is per column
rather than per table: a row is the person's own history, and the token
inside it is not theirs to mail to a clinician or drop in a cloud folder.

`watch_channels` is this product's sharp case. The row says a wrist is
depositing readings and when it started, which the person should see. The
`token` in it is a deposit address printed into their phone automation, which
an exported bundle should never carry.

## How this checks it

The same way the erase guard does — plant a row in every scoped table, ask
for the export, and look. A completeness check that only visits tables some
feature happens to fill is the same blind spot as the list it replaced.
"""

from __future__ import annotations

import ast
import inspect
import textwrap

import pytest

from jim import db, life

from . import ratchets
from .test_an_erase_is_measured_against_the_schema import (
    SUBJECT, _columns, _plant, _scoped_from_the_schema)


def _enroll(client) -> dict:
    made = client.post("/enroll", json={"display_name": "Ada",
                                        "terms_consent": True})
    assert made.status_code == 201, made.text
    return made.json()


def test_the_export_reaches_every_table_the_schema_scopes(client):
    """The completeness half."""
    conn = db.connect()
    subject = _enroll(client)["id"]
    planted = [t for t in _scoped_from_the_schema(conn)
               if t != "users" and _plant(conn, t, subject)]
    conn.commit()
    assert len(planted) >= ratchets.floor("erase.tables_planted"), (
        f"only planted rows in {len(planted)} tables — the planter is failing "
        "and the check below would pass on almost nothing")

    bundle = life.export_user_data(subject)
    missing = sorted(t for t in planted if t not in bundle["tables"])
    assert not missing, (
        f"{len(missing)} table(s) hold rows for this person and are not in "
        "their export:\n    " + "\n    ".join(missing)
        + "\n  *Everything we hold* is a claim about the schema. Derive the "
          "export from it, as the erase cascade does.")


def test_the_export_carries_no_live_credential(client):
    """The half that is not completeness.

    Checked against the rows that come back rather than against the redaction
    tuple: a tuple is a list of names somebody wrote, and this file exists
    because lists of names go stale.
    """
    conn = db.connect()
    subject = _enroll(client)["id"]
    for table in _scoped_from_the_schema(conn):
        if table != "users":
            _plant(conn, table, subject)
    conn.commit()

    leaked = []
    for table, rows in life.export_user_data(subject)["tables"].items():
        for row in rows:
            for column in row:
                # The same marks the redaction rule uses, and deliberately
                # not the bare word `hash`: a hash-linked record is something
                # a person verifies their own export with, and a credential
                # is something somebody can present.
                if any(mark in column.lower() for mark in
                       ("token", "secret", "password", "api_key",
                        "private_key", "grant_hash", "check_value")):
                    leaked.append(f"{table}.{column}")
    assert not leaked, (
        "the export hands back live credentials:\n    "
        + "\n    ".join(sorted(set(leaked)))
        + "\n  A bundle is downloaded, mailed and copied. Carry the row and "
          "drop the column.")


def test_the_export_is_not_a_hand_written_list():
    """The structural half, which survives the next migration."""
    source = inspect.getsource(life.export_user_data)
    tree = ast.parse(textwrap.dedent(source))
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Tuple, ast.List)):
            continue
        words = [e.value for e in node.elts
                 if isinstance(e, ast.Constant) and isinstance(e.value, str)]
        assert len(words) < 5, (
            f"the export carries a list of {len(words)} table names "
            f"({words[:4]}…). Read the schema instead.")
    assert "user_scoped_tables" in source, (
        "export_user_data no longer asks the schema what this person has")


def test_the_export_and_the_erase_reach_the_same_tables(client):
    """The symmetry, asserted rather than assumed.

    A table the erase clears and the export omits is a person who can delete
    something they were never shown. A table the export carries and the erase
    misses is the defect 0.59.9 was about. Both are one comparison.
    """
    conn = db.connect()
    subject = _enroll(client)["id"]
    planted = {t for t in _scoped_from_the_schema(conn)
               if t != "users" and _plant(conn, t, subject)}
    conn.commit()
    shown = set(life.export_user_data(subject)["tables"]) & planted
    life.delete_user_data(subject)
    left = {t for t in planted
            if conn.execute(f"SELECT COUNT(*) FROM {t} WHERE {SUBJECT}=?",
                            (subject,)).fetchone()[0]}
    cleared = planted - left
    assert shown == cleared, (
        "the export and the erase disagree about this person's data:\n"
        f"    shown but not cleared: {sorted(shown - cleared)}\n"
        f"    cleared but not shown: {sorted(cleared - shown)}")


def test_the_route_is_reachable_and_owner_only(client):
    """A person's own bundle, and nobody else's."""
    mine = _enroll(client)
    theirs = _enroll(client)
    ok = {"authorization": f"Bearer {mine['user_token']}"}
    assert client.get(f"/data/{mine['id']}", headers=ok).status_code == 200
    assert client.get(f"/data/{mine['id']}", headers={}).status_code == 401
    assert client.get(f"/data/{theirs['id']}", headers=ok).status_code in (403, 404)
