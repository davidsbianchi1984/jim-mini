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

## What the sweep decided a floor was, and why that changed

For its first several rounds this sweep took any comparison against an
integer of five or more. Five was a stand-in: below it lay indices, small
fixed cardinalities, and assertions about a single response — `body["count"]
>= 2` — which are claims about one answer rather than floors under a scan.

The stand-in was wrong in both directions, and the round that measured the
hidden ones proved it. Of the 112 comparisons under five across the three
suites, fifty-two were response-body assertions the cutoff was right to
exclude, forty were honest floors already in band, and twenty stood well
under what they guarded. The sharpest was an `n >= 2` over a shell building
a hundred and twenty-seven requests. Lowering the cutoff would have swept in
all fifty-two; leaving it kept hiding the twenty.

    asked     is this floor big enough to be worth auditing
    mattered  is this a floor at all

So the sweep asks the second question now, of the expression on the left
rather than the number on the right: is this a count of something the suite
went and found, or a value pulled out of what something returned.
`reads_a_result` below is that test, and it has its own guards in both
directions, because a classifier that answered "not a floor" to everything
would empty this backlog and read exactly like finishing it.
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

#: Calls that produce something to count by going and looking — a regex sweep,
#: a directory walk, an occurrence count. A `len()` around one of these counts
#: a surface this suite scanned, which is what a floor stands under.
SCANNERS = frozenset({"findall", "finditer", "glob", "rglob", "count",
                      "split", "splitlines", "readlines", "rsplit"})

#: Names that wrap a count around something else, and so pass the question
#: through to what they were handed.
WRAPPERS = frozenset({"len", "sum", "min", "max", "sorted", "set", "list",
                      "tuple", "abs", "int", "round"})

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


def _not_floors() -> set[str]:
    """`file.py: expr` pairs the record names as comparisons that are not floors.

    Keyed on the expression rather than the line, because a line number is a
    fact about today's file and an exemption keyed on one silently starts
    covering whatever moves into that slot. Paying down eighteen floors in
    this suite shifted five unrelated rows by a line each, which is exactly
    the accident this avoids.
    """
    out, inside = set(), False
    for line in RECORD.read_text(encoding="utf-8").splitlines():
        if line.startswith("# ## Not floors"):
            inside = True
            continue
        if inside:
            if line.startswith("# ## "):
                break
            if line.startswith("#   ") and not line.startswith("#     "):
                out.add(line[4:].strip())
    return out


def _asserts(tree: ast.Module):
    """Every assertion, paired with the scope whose names it can see.

    The scope is needed because most floors compare a local — `controls`,
    `sites`, `n` — and what that local was built from is the only thing that
    says whether the comparison is a floor or a claim about one answer.
    """
    out = []
    for scope in [tree] + [n for n in ast.walk(tree)
                           if isinstance(n, (ast.FunctionDef,
                                             ast.AsyncFunctionDef))]:
        for node in ast.walk(scope):
            if isinstance(node, ast.Assert):
                out.append((scope, node))
    seen, kept = set(), []
    for scope, node in out:
        # An assert inside a function is reached twice — once through the
        # module and once through the function. The function is the tighter
        # scope and the one that resolves its names, so it wins.
        key = (node.lineno, node.col_offset)
        if key in seen and isinstance(scope, ast.Module):
            continue
        if key in seen:
            kept = [(s, n) for s, n in kept
                    if (n.lineno, n.col_offset) != key]
        seen.add(key)
        kept.append((scope, node))
    return sorted(kept, key=lambda p: (p[1].lineno, p[1].col_offset))


def _assigned(scope) -> dict[str, ast.AST]:
    """Names this scope binds to an expression, for the one hop below.

    One hop, not a fixpoint: `controls = _scanned_controls()` is worth
    following and a chain of five is worth leaving alone. A name this cannot
    resolve is kept rather than dropped, which is the direction that errs
    toward counting a floor twice rather than losing one.
    """
    out = {}
    for node in ast.walk(scope):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    out.setdefault(target.id, node.value)
        elif isinstance(node, ast.AnnAssign) and node.value is not None:
            if isinstance(node.target, ast.Name):
                out.setdefault(node.target.id, node.value)
    return out


def reads_a_result(node: ast.AST, assigned: dict[str, ast.AST],
                   depth: int = 0) -> bool:
    """Is this expression a value pulled out of what something returned?

    The question the sweep used to answer with the size of the literal. A
    floor stands under a surface the suite went and scanned; `len(sites) >= 5`
    is one whether the five is five or fifty. `body["redactions"] >= 2` is not
    a floor at any number — it is a claim about a single answer, satisfied or
    not on its own terms, and no measurement of a surface would audit it.

        asked     is this floor big enough to be worth auditing
        mattered  is this a floor at all

    Selecting on size was a stand-in for selecting on kind, and it was wrong
    in both directions: it hid a two standing over a hundred and twenty-seven,
    and lowering it would have swept in fifty-two response-body assertions
    that no ratchet could ever measure.
    """
    if depth > 6:                               # pragma: no cover - no chain
        return False
    if isinstance(node, (ast.Subscript, ast.Attribute, ast.BoolOp, ast.Await)):
        return True
    if isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Attribute):
            if func.attr not in SCANNERS:
                return True
            return False
        if isinstance(func, ast.Name) and func.id in WRAPPERS:
            return any(reads_a_result(a, assigned, depth + 1)
                       for a in node.args)
        return False
    if isinstance(node, (ast.GeneratorExp, ast.ListComp, ast.SetComp)):
        return reads_a_result(node.elt, assigned, depth + 1)
    if isinstance(node, ast.BinOp):
        return (reads_a_result(node.left, assigned, depth + 1)
                or reads_a_result(node.right, assigned, depth + 1))
    if isinstance(node, ast.Name):
        value = assigned.get(node.id)
        if value is None:
            return False
        return reads_a_result(value, {}, depth + 1)
    return False


def _bare_floors() -> list[str]:
    """Every `assert <something> > <int>` still carrying its own number.

    A registered floor reads `ratchets.floor("name")`, which is a call and not
    a constant, so registering one removes it from this sweep without anybody
    having to edit the record by hand.
    """
    rows = []
    exempt = _not_floors()
    for path in sorted(TESTS.glob("test_*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:                     # pragma: no cover - none today
            continue
        for scope, node in _asserts(tree):
            test = node.test
            if not (isinstance(test, ast.Compare) and len(test.ops) == 1
                    and isinstance(test.ops[0], (ast.GtE, ast.Gt))):
                continue
            right = test.comparators[0]
            if not (isinstance(right, ast.Constant)
                    and isinstance(right.value, int)
                    and not isinstance(right.value, bool)):
                continue
            if reads_a_result(test.left, _assigned(scope)):
                continue
            expr = ast.unparse(test)[:88]
            if f"{path.name}: {expr}" in exempt:
                continue
            rows.append(f"{path.name}:{node.lineno}: {expr}")
    return rows


def _recorded() -> set[str]:
    return {line.strip() for line in RECORD.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


def _ceiling() -> int:
    return int(re.search(r"# ceiling: (\d+)",
                         RECORD.read_text(encoding="utf-8")).group(1))


def test_a_scanned_count_is_a_floor_and_a_returned_field_is_not():
    """The classifier in both directions, on lines taken from these suites.

    Both directions, because the two failures are not symmetrical and only one
    of them is loud. A rule that calls floors response fields shrinks this
    backlog to nothing and reads like the work being finished.
    """
    floors = ("len(sites) >= 5",
              "controls > 6000",
              "n >= 2",
              "app.count('onPlans={toPlans}') >= 20",
              "sum(len(k) for _, k in reads) >= 28",
              "english + calls >= 50",
              "len(re.findall(BUILT[name], code)) >= 2")
    returned = ("body['beats_spoken'] >= 1",
                "log['count'] >= 2",
                "exc['redactions'] >= 2",
                "visits.fold_old() >= 3",
                "escalation._SEVERITY_BASE['critical'] >= 4",
                "(hr.get('samples') or 0) >= 1",
                "len(out['messages']) >= 2")
    for src in floors:
        left = ast.parse(src, mode="eval").body.left
        assert not reads_a_result(left, {}), f"{src} is a floor"
    for src in returned:
        left = ast.parse(src, mode="eval").body.left
        assert reads_a_result(left, {}), f"{src} is not a floor"


def test_a_local_is_judged_by_what_it_was_built_from():
    """Most floors compare a local, so the name alone decides nothing.

    `len(rows)` and `len(found)` are the same three tokens. What separates
    them is one line above the assertion, which is why the sweep carries the
    scope down instead of looking at the comparison on its own.
    """
    tree = ast.parse(
        "def t():\n"
        "    rows = response.json()['rows']\n"
        "    found = _scan(REPO)\n"
        "    assert len(rows) >= 2\n"
        "    assert len(found) >= 2\n")
    fn = tree.body[0]
    assigned = _assigned(fn)
    out_of_a_response, off_the_repo = sorted(
        (n for n in ast.walk(fn) if isinstance(n, ast.Assert)),
        key=lambda n: n.lineno)
    assert reads_a_result(out_of_a_response.test.left, assigned)
    assert not reads_a_result(off_the_repo.test.left, assigned)


def test_the_classifier_keeps_what_it_cannot_read():
    """A name it cannot resolve is kept, not dropped.

    The direction matters. Keeping one it should have dropped puts a row in a
    backlog somebody reads; dropping one it should have kept removes a floor
    from the world silently, and the backlog shrinks in a way that looks like
    progress.
    """
    left = ast.parse("whatever_this_is >= 7", mode="eval").body.left
    assert not reads_a_result(left, {})


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


def test_every_exempted_comparison_is_still_there():
    """An exemption for a line nobody writes any more is an exemption for
    nothing, and it hides the next thing that takes the same shape."""
    live = set()
    for path in sorted(TESTS.glob("test_*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:                     # pragma: no cover - none today
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Assert) and isinstance(node.test, ast.Compare):
                live.add(f"{path.name}: {ast.unparse(node.test)[:88]}")
    phantom = sorted(_not_floors() - live)
    assert not phantom, (
        f"{len(phantom)} comparison(s) exempted as not-a-floor are no longer "
        "written anywhere — strike them from the record:\n    "
        + "\n    ".join(phantom))


def test_a_count_can_never_be_exempted():
    """The forward direction, and the one that matters.

    The record's exempt list is prose a person edits, which is the point: the
    ledger says telling a floor from a fixed cardinality "requires knowing
    what each one measures". Prose a person edits is also how a real floor
    gets quietly excused to make a backlog number fall.

        asked     is this comparison a floor
        mattered  could somebody call a floor something else

    So one property is checked mechanically rather than trusted: a comparison
    against `len(...)` or `sum(...)` is a count of a swept surface, and a
    count of a swept surface is always a floor. Those may never be exempted,
    whatever the record says about them. What remains exemptible is a value
    read out of a response or a fixture -- an age, a status code, a heart
    rate -- which is not a size and cannot be raised toward one.
    """
    counted = []
    for row in sorted(_not_floors()):
        expr = row.split(": ", 1)[1] if ": " in row else row
        try:
            tree = ast.parse(expr, mode="eval")
        except SyntaxError:                     # pragma: no cover - none today
            continue
        left = tree.body.left if isinstance(tree.body, ast.Compare) else None
        for node in ast.walk(left) if left is not None else ():
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id in ("len", "sum")):
                counted.append(row)
                break
    assert not counted, (
        f"{len(counted)} exempted comparison(s) measure a count, which is "
        "always a floor — register them in ratchets.py rather than excusing "
        "them:\n    " + "\n    ".join(counted))
