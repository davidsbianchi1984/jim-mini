"""A fix to the cascade fixes the next erase, not the last one.

0.59.9 derived `delete_user_data` from the schema. Every account erased
*before* that release was erased by a list of twenty-one table names against
a schema of sixty-three, and the forty-three tables it missed are still
sitting in every deployment that has been running since.

Nothing in the product will ever look at them again, and that is the whole
problem. `users` is gone, so the API answers 404, so no code path visits
those rows — they are not visible, they are not reachable, and they are still
there. A person who pressed *erase everything* has an account that reads as
gone and a medicine cabinet, a money mandate and a set of clinical captures
that are not.

    asked     does the erase work now
    mattered  what did it leave the last time it did not

## What this file checks, and what it refuses to borrow

The planting reads the schema **here**, not through `life.user_scoped_tables`,
for the reason 0.59.9's guard names: a test that asks the code under test
which tables to check plants rows only where that code already looks, so
narrowing the sweep narrows the test with it and the run stays green.

The sharp property is not "does it delete the orphans" — it is **"does it
leave a living account alone"**. A maintenance command that runs `DELETE`
across sixty-three tables on somebody else's deployment has exactly one way
to be catastrophic, and it is checked below with a live account seeded beside
the stranded one.
"""

from __future__ import annotations

import pytest

from jim import db, life, orphans

from . import ratchets

from .test_an_erase_is_measured_against_the_schema import (
    SUBJECT, _plant, _scoped_from_the_schema)


def _enroll(client) -> str:
    made = client.post("/enroll", json={"display_name": "Ada",
                                        "terms_consent": True})
    assert made.status_code == 201, made.text
    return made.json()["id"]


def _strand(conn, subject: str) -> list[str]:
    """Plant rows for `subject` in every scoped table and remove the account.

    This is what a pre-0.59.9 erase actually left: the `users` row deleted,
    the twenty-one listed tables cleared, and everything else untouched. The
    reconstruction plants everywhere and deletes only the account, which is
    the same residue with a bigger tail.
    """
    planted = [t for t in _scoped_from_the_schema(conn)
               if t != "users" and _plant(conn, t, subject)]
    conn.execute("DELETE FROM users WHERE id=?", (subject,))
    conn.commit()
    return planted


def test_the_survey_finds_the_rows_a_gone_subject_left(client):
    subject = _enroll(client)
    conn = db.connect()
    planted = _strand(conn, subject)
    assert len(planted) >= ratchets.floor("erase.tables_planted"), (
        f"only planted rows in {len(planted)} tables — the planter is failing "
        "and every assertion below would pass on almost nothing")

    found = orphans.survey()
    assert subject in found["subjects"]
    missing = sorted(t for t in planted if t not in found["tables"])
    assert not missing, (
        f"{len(missing)} table(s) hold rows for an account that no longer "
        "exists and the survey does not see them:\n    "
        + "\n    ".join(missing))
    assert found["rows"] >= len(planted)


def test_a_survey_changes_nothing(client):
    """Dry is the default, and the default is the one nobody types."""
    subject = _enroll(client)
    conn = db.connect()
    planted = _strand(conn, subject)

    orphans.survey()
    orphans.sweep()                       # no `apply` — still a read
    still = [t for t in planted
             if conn.execute(f"SELECT COUNT(*) FROM {t} WHERE {SUBJECT}=?",
                             (subject,)).fetchone()[0]]
    assert sorted(still) == sorted(planted), (
        "a survey deleted rows. The command a person runs to find out how bad "
        "it is must not be the command that changes it.")


def test_applying_clears_them(client):
    subject = _enroll(client)
    conn = db.connect()
    planted = _strand(conn, subject)

    done = orphans.sweep(apply=True)
    assert done["applied"] is True
    left = [t for t in planted
            if conn.execute(f"SELECT COUNT(*) FROM {t} WHERE {SUBJECT}=?",
                            (subject,)).fetchone()[0]]
    assert not left, (
        f"{len(left)} table(s) survived the sweep:\n    "
        + "\n    ".join(sorted(left)))
    assert orphans.survey()["rows"] == 0


def test_a_living_subject_is_not_touched(client):
    """The property that matters more than any of the above.

    This command deletes across sixty-three tables on a deployment whose data
    the person running it cannot see. If its predicate is wrong in the other
    direction it erases somebody who never asked for anything.
    """
    stranded = _enroll(client)
    living = _enroll(client)
    conn = db.connect()

    kept = [t for t in _scoped_from_the_schema(conn)
            if t != "users" and _plant(conn, t, living)]
    conn.commit()
    _strand(conn, stranded)
    assert len(kept) >= ratchets.floor("erase.tables_planted"), (
        "the living account was not seeded")

    orphans.sweep(apply=True)

    lost = [t for t in kept
            if not conn.execute(f"SELECT COUNT(*) FROM {t} WHERE {SUBJECT}=?",
                                (living,)).fetchone()[0]]
    assert not lost, (
        f"the sweep deleted {len(lost)} table(s) of data belonging to an "
        "account that still exists:\n    " + "\n    ".join(sorted(lost))
        + "\n  An orphan is a row whose subject is gone. Nothing else is.")
    assert conn.execute("SELECT COUNT(*) FROM users WHERE id=?",
                        (living,)).fetchone()[0] == 1


def test_a_row_with_no_subject_is_left_alone(client):
    """An empty `user_id` is not the residue of a deleted account.

    It is something else — a seed row, a migration default, a bug — and a
    maintenance command written for one problem does not get to decide what
    to do about a different one.
    """
    conn = db.connect()
    # The first table that will take one: several carry constraints that
    # refuse an empty subject outright, which is its own kind of correct.
    table = next((t for t in _scoped_from_the_schema(conn)
                  if t != "users" and _plant(conn, t, "")), None)
    assert table, "no scoped table accepts a row with an empty subject"
    conn.commit()
    before = conn.execute(
        f"SELECT COUNT(*) FROM {table} WHERE {SUBJECT}=''").fetchone()[0]
    assert before

    orphans.sweep(apply=True)
    after = conn.execute(
        f"SELECT COUNT(*) FROM {table} WHERE {SUBJECT}=''").fetchone()[0]
    assert after == before, (
        f"the sweep deleted {before - after} row(s) with no subject at all")


def test_a_healthy_deployment_reports_nothing(client):
    """And says so in a sentence, rather than printing an empty table."""
    _enroll(client)
    found = orphans.survey()
    assert found["rows"] == 0 and found["tables"] == {}
    assert "Nothing stranded" in orphans._report(found)


def test_the_scope_is_the_cascades_and_not_a_second_list():
    """The structural half, which survives the next migration.

    Two readers of *which tables hold a person's data* is two things to keep
    in step, and the one that falls behind is the one nobody runs.
    """
    import inspect
    source = inspect.getsource(orphans)
    assert "life.user_scoped_tables()" in source, (
        "the sweep no longer asks the cascade's reader which tables are in "
        "scope, so it has become a second list of the kind 0.59.9 removed")
    assert "life.ERASE_KEEPS" in source
    for table, _ in life.ERASE_THROUGH.items():
        assert table in orphans._in_scope(), (
            f"{table} is reached through a parent by the cascade and is not "
            "in the sweep's scope, so its rows outlive the sweep too")


def test_the_command_line_is_dry_by_default(client, capsys):
    subject = _enroll(client)
    conn = db.connect()
    planted = _strand(conn, subject)

    assert orphans.main([]) == 0
    assert "Nothing was changed" in capsys.readouterr().out
    assert conn.execute(
        f"SELECT COUNT(*) FROM {planted[0]} WHERE {SUBJECT}=?",
        (subject,)).fetchone()[0]

    assert orphans.main(["--apply"]) == 0
    assert "Cleared" in capsys.readouterr().out
    assert orphans.survey()["rows"] == 0

    assert orphans.main(["--wipe-everything"]) == 2
