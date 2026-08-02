"""The README said v0.18.0 for twenty-two releases.

## The finding

The first bold line of every README in all three products read:

    **Current release: v0.18.0**

and the line directly beneath it said the three are *"versioned and cut
together, so one number names one combination of all three"* — a convention the
banner had stopped following at 0.18.0 and kept advertising ever since.

The release-history table underneath stopped at **0.30.6**. Seventeen shipped
releases — 0.25.0 through 0.29.0, 0.30.7 to 0.30.9, and the whole 0.40.x line —
were in `CHANGELOG.md` and absent from the page anybody actually reads. The
changelog was right the entire time; the summary of it in front of the door was
two years of habit behind.

    asked     is the release written down
    mattered  does the front page say what shipped

Reported by the person who owns the products, from the README beside a video —
which is the one place this was always going to be noticed, and the one place
no test was looking.

## What this checks

Two things, both mechanical, because the failure was never a judgement call:

* the banner names the version in `pyproject.toml`; and
* every release in the changelog from 0.25.0 on has a row in the table.

The floor exists because the table deliberately collapses the pre-0.25 history
into a shorter tail, which is a decision about how much of the beginning a
reader needs — not the same thing as forgetting the last seventeen.
"""

from __future__ import annotations

import re
from pathlib import Path


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
README = REPO / "README.md"
CHANGELOG = REPO / "CHANGELOG.md"

#: Releases below this are collapsed in the table on purpose. Named as a floor
#: rather than left implicit, so "the table is allowed to be short at the
#: bottom" cannot quietly become "the table is allowed to be short at the top".
OLDEST_ROW = (0, 25, 0)


def _version() -> str:
    return re.search(r'^version = "(.+)"',
                     (REPO / "pyproject.toml").read_text(encoding="utf-8"),
                     re.M).group(1)


def _tuple(v: str) -> tuple[int, ...]:
    return tuple(int(p) for p in v.split("."))


def _rows() -> list[str]:
    return re.findall(r"^\| \*\*(\d+\.\d+\.\d+)\*\*",
                      README.read_text(encoding="utf-8"), re.M)


def _released() -> list[str]:
    return re.findall(r"^## \[(\d+\.\d+\.\d+)\]",
                      CHANGELOG.read_text(encoding="utf-8"), re.M)


def test_the_banner_names_the_version_that_shipped():
    """The first bold line of the file, which is the first thing a reader
    takes on trust and the last thing anybody remembers to edit."""
    said = re.search(r"\*\*Current release: v([\d.]+)\*\*",
                     README.read_text(encoding="utf-8"))
    assert said, "the README no longer states a current release"
    assert said.group(1) == _version(), (
        f"the README says v{said.group(1)} and this product is at "
        f"v{_version()}. The line under it promises that one number names one "
        "combination of all three products, so a stale banner is not a typo — "
        "it is the convention advertising itself while not being kept.")


def test_every_release_since_the_floor_has_a_row():
    """The history table, against the changelog it summarises."""
    rows = set(_rows())
    missing = sorted((v for v in _released()
                      if _tuple(v) >= OLDEST_ROW and v not in rows),
                     key=_tuple)
    assert not missing, (
        f"{len(missing)} release(s) are in the changelog and not in the "
        "README's history:\n    " + ", ".join(missing))


def test_the_newest_row_is_this_release():
    """A table backfilled to within one release of the top is a table somebody
    will stop trusting the moment they notice."""
    rows = _rows()
    assert rows, "the README has no release history at all"
    assert rows[0] == _version(), (
        f"the newest row is {rows[0]} and this product is at {_version()}")


def test_no_row_names_a_release_that_was_never_cut():
    """The other direction. A row for a version with no changelog entry is the
    history describing something that did not happen."""
    released = set(_released())
    invented = sorted((v for v in _rows() if v not in released), key=_tuple)
    assert not invented, (
        "these rows name releases with no changelog entry:\n    "
        + ", ".join(invented))


def test_the_scan_is_reading_the_table():
    """A guard on the guard: a pattern that stopped matching would report a
    complete history by finding no rows to compare."""
    assert len(_rows()) >= 40, (
        f"only {len(_rows())} history row(s) parsed — the checks above would "
        "pass on almost nothing")
    assert len(_released()) >= 40, (
        f"only {len(_released())} changelog release(s) parsed")
