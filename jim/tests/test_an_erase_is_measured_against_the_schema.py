"""An erase is measured against the schema, not against a list somebody wrote.

## What it was

`delete_user_data` says *erase every trace of a user across all tables*. It
named twenty-one tables in a tuple. The schema has **sixty-three** with a
`user_id` column, so the erase left forty-three standing:

    accounts        money_accounts   money_mandates   money_orders
    budgets         budget_spend     savings_goals    medications
    med_logs        captures         care_plans       care_teams
    care_beacons    crash_watches    vigils           mic_channels
    mic_sessions    user_continuity  user_finetunes   user_models
    …and twenty-three more

The money guardian's accounts and mandates. The medicine cabinet and every
dose logged from it. The clinical captures — photographs of somebody's body.
And `crash_watches` and `vigils`, which are not records of anything: they are
standing permissions for this product to act on that person's behalf, still
live for an account the API answers 404 for.

The sibling vault had already found and fixed the same shape, and its fix did
not travel. Its docstring says why in one line: *a migration that adds a table
is covered by writing it, not by remembering this function.*

    asked     did we delete what the handler names
    mattered  did we delete what the schema holds

## Why the list kept losing

It was not neglect. The list had been *corrected twice*, both times
correctly, and both times three tables at a time — the round that found a
watch channel outliving its account added `watch_channels`,
`contribution_log` and `waivers` and closed. Every one of those fixes was
right and none of them changed the thing that makes the next one necessary.

## How this checks it

By writing a row into **every** scoped table, erasing, and looking. Not by
exercising features until rows appear: the tables a test can reach through
the API are the tables somebody thought to wire, which is the same blind spot
as the list. The rows are synthetic and go in through SQL — the question here
is whether the cascade reaches a table, and a row is a row.
"""

from __future__ import annotations

import ast
import inspect
import textwrap
from pathlib import Path

import pytest

from . import ratchets

from jim import db, life

#: The column that names the subject, per table shape.
SUBJECT = "user_id"


def _columns(conn, table: str) -> list[tuple]:
    return list(conn.execute(f"PRAGMA table_info({table})"))


def _filler(kind: str):
    kind = (kind or "").upper()
    if "INT" in kind:
        return 0
    if any(k in kind for k in ("REAL", "FLOA", "DOUB", "NUM", "DEC")):
        return 0.0
    if "BLOB" in kind:
        return b""
    return ""


def _plant(conn, table: str, subject: str) -> bool:
    """Put one row naming `subject` into `table`. False if it will not take."""
    names, values = [], []
    for cid, name, kind, notnull, default, pk in _columns(conn, table):
        if name == SUBJECT:
            names.append(name)
            values.append(subject)
        elif name == "id":
            names.append(name)
            values.append(f"erase-probe-{table}")
        elif notnull and default is None and not pk:
            names.append(name)
            values.append(_filler(kind))
    marks = ",".join("?" for _ in names)
    try:
        conn.execute(f"INSERT INTO {table} ({','.join(names)}) VALUES ({marks})",
                     values)
        return True
    except Exception:
        return False


def plantable() -> int:
    """How many scoped tables will take a probe row.

    Registered as a floor of its own: the planter is the half of this file
    that can go quiet without the sweep noticing — every insert failing looks
    exactly like a schema with nothing in it.
    """
    conn = db.connect()
    return sum(1 for t in _scoped_from_the_schema(conn)
               if _plant(conn, t, "erase-probe-count"))


def scoped_tables() -> list[str]:
    """The registry's reader: this file's own view of the schema."""
    return _scoped_from_the_schema(db.connect())


def _scoped_from_the_schema(conn) -> list[str]:
    """The tables this test will plant in — read here, not borrowed.

    Deliberately not `life.user_scoped_tables()`. A test that asks the code
    under test which tables to check plants rows only where that code already
    looks, so narrowing the cascade narrows the test with it and the run stays
    green. Found by injecting the old hand-written list: the check reported a
    blind *reader* rather than forty-three surviving tables.
    """
    out = []
    for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%'").fetchall():
        if SUBJECT in {c[1] for c in _columns(conn, row[0])}:
            out.append(row[0])
    return sorted(out)


def test_the_erase_reaches_every_table_the_schema_scopes(client):
    """The whole check, and it needs no feature to be wired to find a gap."""
    conn = db.connect()
    subject = "usr_erase_probe"
    planted = [t for t in _scoped_from_the_schema(conn)
               if _plant(conn, t, subject)]
    conn.commit()
    assert len(planted) >= ratchets.floor("erase.tables_planted"), (
        f"only planted rows in {len(planted)} tables — the planter is failing "
        "on this schema and the check below would pass on almost nothing")

    life.delete_user_data(subject)

    left = []
    for table in planted:
        n = conn.execute(
            f"SELECT COUNT(*) FROM {table} WHERE {SUBJECT}=?", (subject,)
        ).fetchone()[0]
        if n and table not in life.ERASE_KEEPS:
            left.append(table)
    assert not left, (
        f"{len(left)} table(s) still hold rows for a user who asked to be "
        "forgotten:\n    " + "\n    ".join(sorted(left))
        + "\n  The handler says *every trace*. Derive the cascade from the "
          "schema, or put the table in ERASE_KEEPS with the reason.")


def test_the_cascade_is_not_a_hand_written_list():
    """The structural half.

    A behavioural check passes the moment the list is long enough *today*,
    and says nothing about the table added next week. This is the part that
    survives the next migration.
    """
    source = inspect.getsource(life.delete_user_data)
    # `cleandoc` normalises a docstring, not a function body — it strips the
    # `def` line's indentation and leaves the rest, which does not parse.
    tree = ast.parse(textwrap.dedent(source))
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Tuple, ast.List)):
            continue
        words = [e.value for e in node.elts
                 if isinstance(e, ast.Constant) and isinstance(e.value, str)]
        assert len(words) < 5, (
            f"the cascade carries a list of {len(words)} table names "
            f"({words[:4]}…). Every list of this shape in the estate has gone "
            "stale; read the schema instead.")
    assert "user_scoped_tables" in source, (
        "delete_user_data no longer asks the schema which tables to clear")


def test_the_scoped_reader_sees_the_whole_schema(client):
    """A reader that goes blind reports an erase with nothing left to do."""
    conn = db.connect()
    tables = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' "
        "AND name NOT LIKE 'sqlite_%'").fetchall()]
    scoped = life.user_scoped_tables()
    assert len(scoped) >= ratchets.floor("erase.scoped_tables"), (
        f"{len(scoped)} scoped tables out of {len(tables)} — the schema "
        "reader has stopped matching, and an empty cascade deletes nothing "
        "while reporting success")
    assert set(scoped) <= set(tables)


def test_what_is_kept_is_named_and_reasoned():
    """`ERASE_KEEPS` is the only way a table survives, so it is the only place
    a promise is broken. A row in it is a deliberate edit that a reader can
    see and argue with — `audit` is the first, and its reason is written
    beside it in `life.py`."""
    assert isinstance(life.ERASE_KEEPS, frozenset)
    for table in life.ERASE_KEEPS:
        assert table in life.user_scoped_tables(), (
            f"{table!r} is kept from an erase and is not in the schema")


def test_the_child_tables_are_reached_through_their_parent(client):
    """A habit log names its habit, not its person. Nothing scoped by
    `user_id` can see it, which is why the cascade carries a second map."""
    assert life.ERASE_THROUGH, "no child tables declared at all"
    conn = db.connect()
    for table, (parent, column) in life.ERASE_THROUGH.items():
        cols = {c[1] for c in _columns(conn, table)}
        assert column in cols, f"{table} has no {column}"
        assert SUBJECT not in cols, (
            f"{table} carries {SUBJECT} and does not need reaching through "
            f"{parent} — the schema sweep already has it")
