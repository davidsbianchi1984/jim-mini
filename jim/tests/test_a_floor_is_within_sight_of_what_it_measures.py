"""A floor nobody raised is a floor nobody is standing on.

0.58.8 found the route reader had one floor and four clients. 0.58.9 found the
localizer's floor was ten against nine hundred and forty-five. Both were the
same defect in different instruments: a number written when the surface was
small, correct on the day, never raised.

Fixing them one file at a time does not generalise. This is the sweep, and
`ratchets.py` is the convention it needed first.

## The two questions

A floor answers one question every run — *is the number satisfied* — and that
is the question that keeps passing while the floor stops meaning anything. The
second question has to be asked separately:

    asked     is the number satisfied
    mattered  is the number still near what it measures

Both live here. A floor above what its reader reaches fails every run and gets
lowered until it means nothing. A floor far below it is decoration. The
standard is the one 0.58.8 set for its own table and 0.58.9 kept: **half.** A
floor under half of what it measures is not holding anything.

## What that standard found when it was applied to everything

Most floors in this product that could be reached by a measurement failed it,
and the ones that passed are as informative as the ones that did not:

    l10n asked, per shell        10 against 279-312      ratio 0.04
    l10n held, per shell         20 against 286-312      ratio 0.07
    path literals, all surfaces  40 against 466          ratio 0.09
    native call sites            20 against 113-114      ratio 0.18
    console call sites          200 against 251          ratio 0.80  held

The last row passed, and it is the one worth reading twice. `len(made) > 200`
sits at four-fifths of this console — an honest floor. The identical literal
in QRME sits at 0.47 of a console that grew to 429 call sites. One number
written to work in three repositories is calibrated for whichever of them was
smallest when it was written, and it ages into decoration in the largest while
reading as fine in the others. Neither repository could tell, because neither
had the measurement attached.

## Why the unregistered ones are counted rather than fixed

The AST sweep below finds every bare numeric floor left in this suite: an
`assert` comparing something to an integer literal with `>` or `>=`. There are
dozens. Most are fine, some are decoration, and telling them apart requires
knowing what each one measures — which is the work of registering it.

So they are held in a ratcheted backlog instead of guessed at. The count may
shrink and may not grow. A new bare floor is a new number nothing will ever
audit, and the file says so at the moment it is written rather than three
releases later.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from . import ratchets

#: A floor under this fraction of what it measures is decoration. The number
#: is not arbitrary: it is the one 0.58.8 chose for its own floors table and
#: 0.58.9 kept, applied now to every floor rather than to the two tables whose
#: authors happened to think of it.
HEADROOM = 0.5

#: Integer literals below this are not floors — they are counts of a handful
#: of things, indices, small fixed cardinalities. Sweeping them in would bury
#: the real ones under noise.
SMALLEST_FLOOR = 5

TESTS = Path(__file__).resolve().parent
RECORD = TESTS / "unregistered_floors.txt"


def parsed_files() -> int:
    """How many test files the sweep can actually read.

    This is the sweep's own liveness, and it is deliberately *not* the count
    of floors found: that count is a backlog being paid down, so a floor under
    it would fail on the good news. What must not quietly drop is the number
    of files being looked at.
    """
    n = 0
    for path in sorted(TESTS.glob("test_*.py")):
        try:
            ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:                     # pragma: no cover - none today
            continue
        n += 1
    return n


def _bare_floors() -> list[str]:
    """Every `assert <something> > <int>` still carrying its own number.

    A registered floor reads `ratchets.floor("name")`, which is a call and not
    a constant, so registering one removes it from this sweep without anybody
    having to edit the record by hand.
    """
    rows = []
    for path in sorted(TESTS.glob("test_*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:                     # pragma: no cover - none today
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assert):
                continue
            test = node.test
            if not (isinstance(test, ast.Compare) and len(test.ops) == 1
                    and isinstance(test.ops[0], (ast.GtE, ast.Gt))):
                continue
            right = test.comparators[0]
            if not (isinstance(right, ast.Constant)
                    and isinstance(right.value, int)
                    and not isinstance(right.value, bool)
                    and right.value >= SMALLEST_FLOOR):
                continue
            rows.append(f"{path.name}:{node.lineno}: {ast.unparse(test)[:88]}")
    return rows


def _recorded() -> set[str]:
    return {line.strip() for line in RECORD.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


def _ceiling() -> int:
    return int(re.search(r"# ceiling: (\d+)",
                         RECORD.read_text(encoding="utf-8")).group(1))


@pytest.mark.parametrize("ratchet", ratchets.RATCHETS, ids=lambda r: r.name)
def test_every_registered_floor_is_reachable_now(ratchet):
    """The ordinary direction. A floor above the truth fails every run, and
    what happens next is that somebody lowers it until it stops complaining."""
    found = ratchet.measure()
    assert found >= ratchet.floor, (
        f"{ratchet.name}: floor {ratchet.floor} above actual {found} — "
        f"{ratchet.why} has shrunk, or its reader has")


@pytest.mark.parametrize("ratchet", ratchets.RATCHETS, ids=lambda r: r.name)
def test_no_registered_floor_is_decoration(ratchet):
    """The direction nothing was asking. A floor of ten satisfies its
    assertion on every run it will ever have."""
    found = ratchet.measure()
    assert ratchet.floor >= found * HEADROOM, (
        f"{ratchet.name}: floor {ratchet.floor} is under {HEADROOM:.0%} of "
        f"{found} — {ratchet.why} could halve without this noticing. Raise it "
        "to about four-fifths of what is actually there.")


def test_the_registry_names_are_distinct_and_sorted_by_meaning():
    """A guard on the registry. Two entries sharing a name means one of them
    is unreachable through `floor()` and nobody would see it."""
    names = [r.name for r in ratchets.RATCHETS]
    assert len(names) == len(set(names)), "duplicate ratchet name"
    for r in ratchets.RATCHETS:
        assert r.why and not r.why.endswith("."), (
            f"{r.name}: `why` should name the quantity, lowercase, no period "
            "— it is pasted into failure messages mid-sentence")


def test_the_unregistered_floors_only_shrink():
    """Every number left carrying its own literal, counted rather than guessed
    at. Registering one is what removes it; nothing here has to be edited by
    hand except the ceiling, and that only downward."""
    bare = _bare_floors()
    ceiling = _ceiling()
    assert len(bare) <= ceiling, (
        f"{len(bare)} bare floors, above the {ceiling} recorded. A number "
        "written into an assertion is a number nothing will ever compare "
        "against what it measures — register it in ratchets.py instead:\n    "
        + "\n    ".join(sorted(set(bare) - _recorded())[:20]))


def test_the_record_matches_what_is_actually_there():
    """A backlog that has drifted from the code is worse than none: it makes
    the ceiling a number about a file rather than about the suite."""
    bare, recorded = set(_bare_floors()), _recorded()
    stale = sorted(recorded - bare)
    assert not stale, (
        f"{len(stale)} recorded floor(s) are gone or moved — strike them from "
        "unregistered_floors.txt:\n    " + "\n    ".join(stale[:20]))


def test_the_sweep_is_actually_looking_at_something():
    """The failure this whole file is about, reproduced inside it. A sweep
    reading half the suite reports half the floors and a shrinking backlog,
    which reads exactly like progress."""
    seen = parsed_files()
    assert seen >= ratchets.floor("sweep.files_parsed"), (
        f"the sweep parsed only {seen} test files — it has stopped reaching "
        "them, and a backlog that shrinks because nothing was read looks the "
        "same as one that was paid down")


def test_a_decorative_floor_is_caught():
    """The real thing, as a unit: the localizer's floor as it stood before
    0.58.9, against the surface it was nominally holding."""
    assert not (10 >= 279 * HEADROOM)
    assert 240 >= 300 * HEADROOM
