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
