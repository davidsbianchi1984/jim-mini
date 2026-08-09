"""What the old cascade left behind, for deployments that ran it.

0.59.9 derived the erase from the schema. Before that it ran off a list of
twenty-one table names while the schema had grown to sixty-three, so every
account erased on a pre-0.59.9 build left **forty-three tables standing** —
the money guardian's accounts and mandates, the medicine cabinet and every
dose logged from it, the clinical captures, and the standing permissions in
`crash_watches` and `vigils`.

Fixing the cascade fixes the next erase. It does not reach back. A deployment
that has been running since March holds rows for people who asked to be
forgotten, and nothing in the running product will ever look at them again:
`users` is gone, so the API answers 404, so no code path visits those rows.

    asked     does the erase work now
    mattered  what did it leave the last time it did not

This module is that reach-back, and it is deliberately a **separate command**
rather than something the app runs at startup. A sweep that deletes rows is
not a thing to do silently on somebody else's data on boot.

## What it will and will not touch

The scope is exactly what :func:`life.delete_user_data` would have cleared had
the account still existed — `life.user_scoped_tables()` minus
`life.ERASE_KEEPS`, plus the child tables in `life.ERASE_THROUGH`. It shares
that reader with the cascade on purpose: this is the cascade applied
retroactively, and a second opinion about which tables are in scope would be
a second thing to keep in step.

A row is an orphan only when its `user_id` names an account that is **not in
`users`**. Rows with a NULL or empty subject are left alone: they are not the
residue of a deleted account, they are something else, and this command does
not get to decide what.

## Dry by default

`survey()` reads. `sweep(apply=True)` writes, and nothing calls it without
that argument. The command line mirrors it::

    python -m jim.orphans              # count them, change nothing
    python -m jim.orphans --apply      # clear them
    python -m jim.orphans --json       # the same survey, machine-readable
"""

from __future__ import annotations

import json
import sys

from . import db, life

#: The identity table. A `user_id` naming no row here belongs to nobody.
LIVING = "users"


def _living(conn) -> set[str]:
    return {r[0] for r in conn.execute(f"SELECT id FROM {LIVING}").fetchall()}


def _in_scope() -> list[str]:
    """The tables the cascade reaches, in the order it reaches them.

    Children before parents: an orphaned habit's logs are found through the
    habit, so the habit has to still be there when they are counted.
    """
    through = list(life.ERASE_THROUGH)
    direct = [t for t in life.user_scoped_tables()
              if t not in life.ERASE_KEEPS and t not in through]
    return through + direct


def survey() -> dict:
    """Count rows belonging to accounts this deployment no longer has.

    Returns ``{"rows": int, "tables": {name: count}, "subjects": [id, ...]}``.
    ``tables`` carries only the tables that hold something, so an empty
    mapping is the answer a healthy deployment gives.
    """
    conn = db.connect()
    living = _living(conn)
    tables: dict[str, int] = {}
    subjects: set[str] = set()

    for table, (parent, column) in sorted(life.ERASE_THROUGH.items()):
        found = conn.execute(
            f"SELECT COUNT(*) FROM {table} WHERE {column} NOT IN "
            f"(SELECT id FROM {parent})").fetchone()[0]
        if found:
            tables[table] = found

    for table in life.user_scoped_tables():
        if table in life.ERASE_KEEPS:
            continue
        rows = conn.execute(
            f"SELECT user_id, COUNT(*) FROM {table} "
            "WHERE user_id IS NOT NULL AND user_id != '' "
            "GROUP BY user_id").fetchall()
        stranded = [(uid, n) for uid, n in rows if uid not in living]
        if stranded:
            tables[table] = tables.get(table, 0) + sum(n for _, n in stranded)
            subjects.update(uid for uid, _ in stranded)

    return {"rows": sum(tables.values()), "tables": tables,
            "subjects": sorted(subjects)}


def sweep(apply: bool = False) -> dict:
    """Survey, and — only when asked — delete what the survey found.

    The deletion repeats the survey's own predicate rather than working from
    the ids it collected: between the two, a row could have been written for
    an account that has since been created, and `NOT IN (SELECT id FROM
    users)` is true of exactly the rows that are still stranded at the moment
    the statement runs.
    """
    found = survey()
    found["applied"] = bool(apply)
    if not apply or not found["rows"]:
        return found

    conn = db.connect()
    for table in _in_scope():
        if table in life.ERASE_THROUGH:
            parent, column = life.ERASE_THROUGH[table]
            conn.execute(f"DELETE FROM {table} WHERE {column} NOT IN "
                         f"(SELECT id FROM {parent})")
        else:
            conn.execute(
                f"DELETE FROM {table} WHERE user_id IS NOT NULL "
                f"AND user_id != '' AND user_id NOT IN "
                f"(SELECT id FROM {LIVING})")
    conn.commit()
    return found


def _report(found: dict) -> str:
    if not found["rows"]:
        return ("Nothing stranded: every user-scoped row belongs to an "
                "account this deployment still has.")
    verb = "Cleared" if found.get("applied") else "Found"
    lines = [f"{verb} {found['rows']} row(s) across {len(found['tables'])} "
             f"table(s), belonging to {len(found['subjects'])} account(s) "
             "that no longer exist:"]
    for table, n in sorted(found["tables"].items(), key=lambda kv: -kv[1]):
        lines.append(f"    {n:>7}  {table}")
    if not found.get("applied"):
        lines.append("")
        lines.append("Nothing was changed. Re-run with --apply to clear them.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    unknown = [a for a in argv if a not in ("--apply", "--json")]
    if unknown:
        print(f"unknown argument(s): {' '.join(unknown)}\n"
              "usage: python -m jim.orphans [--apply] [--json]",
              file=sys.stderr)
        return 2
    found = sweep(apply="--apply" in argv)
    print(json.dumps(found, indent=2) if "--json" in argv else _report(found))
    return 0


if __name__ == "__main__":                                   # pragma: no cover
    raise SystemExit(main())
