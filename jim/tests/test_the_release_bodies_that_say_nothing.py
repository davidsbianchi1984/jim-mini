"""The releases whose body says nothing about the release it belongs to.

412 of 530 published releases across the three products carried the same
v0.24.0 prose, because `RELEASE_NOTES.md` was published verbatim over every
curated body since v0.24.0. The file and the workflow that did it are deleted;
`stale_release_bodies.txt` is what remains to be repaired, one row per release.

    asked     which workflow owns the release body
    mattered  does the body say what shipped

**This file cannot check the bodies.** They live on GitHub and this suite is
hermetic — a guard that needs the network is either a skip, which is a check
that does not run, or a hard failure offline, which breaks the rule that the
local suite must be green before a push. So the comparison against GitHub is
`.github/workflows/release-bodies-sweep.yml`, and what is left here is the
record's own integrity: it parses, it counts what it says it counts, and it
only ever shrinks.
"""
from __future__ import annotations

import re
from pathlib import Path

RECORD = Path(__file__).resolve().parent / "stale_release_bodies.txt"

_TAG = re.compile(r"^app-v\d+\.\d+\.\d+$")


def _rows() -> list[tuple[str, str]]:
    """`(tag, reason)` per row — releases still to repair."""
    out = []
    for line in RECORD.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        tag, _, reason = line.partition("  ")
        out.append((tag.strip(), reason.strip()))
    return out


def _kept() -> dict[str, str]:
    """`{tag: reason}` for releases deliberately left as they are.

    These live in `# kept:` lines rather than in rows, because the ceiling
    counts what is still wrong and they are not wrong. `app-v0.24.0`'s body
    *is* the v0.24.0 notes; repairing it would replace a correct body to make
    a total read zero.

    They stay in the file rather than becoming an exemption in code, and the
    sweep reads the same lines, so a kept release is expected to still carry
    the frozen body and fails nothing.
    """
    return {m.group(1): m.group(2).strip() for m in re.finditer(
        r"^# kept: (app-v[\d.]+) — (.+)$",
        RECORD.read_text(encoding="utf-8"), re.M)}


def test_the_stale_release_body_record_is_readable():
    """A guard on the record. A file that parsed to nothing would let the
    ceiling below pass while measuring no releases at all — the failure shape
    this estate has produced more often than any other."""
    rows = _rows()
    text = RECORD.read_text(encoding="utf-8")
    # `rows?` because the record reaches one row and stays there — the
    # singular is correct English and the plural-only pattern crashed on
    # it, which is a guard failing at exactly the moment its subject was
    # finished.
    stated = int(re.search(r"^# status: (?:backlog|floor) — (\d+) rows?$",
                           text, re.M).group(1))
    assert stated == len(rows), (
        f"the record says {stated} rows and carries {len(rows)}")
    bad = [t for t, _ in rows if not _TAG.match(t)]
    assert not bad, f"rows that are not release tags: {bad[:5]}"
    assert len({t for t, _ in rows}) == len(rows), "a tag is recorded twice"


def test_the_stale_release_body_record_only_shrinks():
    """A row leaves when that release's body is rebuilt from its own CHANGELOG
    entry. Nothing may be added: a body written stale today is a defect at the
    moment it is published, which `release-integrity.yml` fails on rather than
    recording here.

    `app-v0.24.0` is the row that never leaves. Its body *is* the v0.24.0
    notes — correct for that release and wrong for the 411 that inherited it —
    so it carries its reason on the row rather than an exemption in code, where
    nobody would read it again.
    """
    text = RECORD.read_text(encoding="utf-8")
    ceiling = int(re.search(r"^# ceiling: (\d+)$", text, re.M).group(1))
    rows = _rows()
    assert len(rows) <= ceiling, (
        f"{len(rows)} stale bodies recorded, above the {ceiling} ceiling — "
        "this record may only shrink")
    kept = _kept()
    assert "app-v0.24.0" in kept and kept["app-v0.24.0"], (
        "app-v0.24.0 must stay in this file under `# kept:` with its reason. "
        "Its body is the v0.24.0 notes and is correct; a file with neither a "
        "row nor a kept line for it would read as though no release was ever "
        "stale, which is the opposite of what happened")


# ---------------------------------------------------------------------------
# The two workflows that read this record embed their Python inside YAML,
# where no interpreter, linter or test ever looks at it. That blindness
# shipped a sweep whose script did not parse: an edit left `problems = []`
# after the first append and dropped an `if gone:` line, so every scheduled
# run died on an IndentationError before checking anything — a checker that
# cannot start, failing in a place nothing was watching.

WORKFLOWS = tuple(
    (Path(__file__).resolve().parents[2] / ".github" / "workflows" / name)
    for name in ("release-bodies-sweep.yml", "release-integrity.yml"))


def _embedded_script(path: Path) -> str:
    """The Python between `python3 - <<'PY'` and its closing `PY`, dedented."""
    text = path.read_text(encoding="utf-8")
    inside, lines = False, []
    for line in text.splitlines():
        if line.strip() == "python3 - <<'PY'":
            inside = True
            continue
        if inside and line.strip() == "PY":
            break
        if inside:
            lines.append(line)
    assert lines, f"{path.name} carries no embedded Python heredoc"
    import textwrap
    return textwrap.dedent("\n".join(lines))


def test_the_workflow_scripts_still_parse():
    """The check that was missing when the sweep shipped unrunnable."""
    import ast

    for path in WORKFLOWS:
        try:
            ast.parse(_embedded_script(path))
        except SyntaxError as exc:
            raise AssertionError(
                f"{path.name}'s embedded script does not parse "
                f"(line {exc.lineno}: {exc.msg}). Every run of that workflow "
                "dies before it checks anything, and nothing else reads this "
                "code.") from exc


def test_the_frozen_opening_decides_staleness_for_this_product():
    """The decision, injected — with this repository's own frozen opening.

    The sweep once looked for `414 tests passing` anywhere in the body. That
    count is PDI's, so the check was dead in the other two products; and it
    matched a release that *quoted* the phrase. The decision is now
    `prose(body).startswith(opens)` with `opens` read from this record — and
    this test drives that exact decision, taking `prose` from the sweep's own
    script so the logic proven here is the logic that runs.
    """
    import ast

    tree = ast.parse(_embedded_script(WORKFLOWS[0]))
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "prose")
    ns: dict = {}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "<prose>", "exec"), ns)
    prose = ns["prose"]

    opens = re.search(r"^# frozen-opens: (.+)$",
                      RECORD.read_text(encoding="utf-8"), re.M)
    assert opens, "the record has no `# frozen-opens:` header"
    mark = opens.group(1).strip()

    frozen = (f"{mark}: **the rest of the frozen notes**\n\nBody.\n\n"
              "**Full Changelog**: https://example.invalid/compare/a...b")
    fresh = ("The console the policy blanked.\n\nWhat shipped, described "
             "for this release.\n\n## What's Changed\n* generated rows")
    quoting = (f"Strikes the old sweep: it matched any body quoting "
               f"\u201c{mark}\u201d, like this one.")

    assert prose(frozen).startswith(mark), (
        "a body opening with this product's frozen text is not seen as "
        "stale — the sweep has gone dead in this repository")
    assert not prose(fresh).startswith(mark), (
        "a fresh body is classified stale, so every honest release would "
        "be flagged")
    assert not prose(quoting).startswith(mark), (
        "a body merely quoting the frozen opening is classified stale — "
        "the defect the startswith decision replaced is back")
