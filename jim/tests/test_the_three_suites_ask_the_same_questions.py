"""Three products, three suites, and nothing comparing what they ask.

0.59.0 closed on the observation that a literal copied into three
repositories is calibrated for whichever of them was smallest. That is a
special case of something larger: **every guard in this estate exists in
three copies, and the copies drift silently in both directions.** A fix made
in one product and not ported looks exactly like a product that never needed
it.

Nothing anywhere was comparing them.

    asked     does this product pass its own suite
    mattered  do the three suites ask the same questions

## What the first sweep found

370 test-function names are carried by all three products. 140 were carried
by exactly two — and four of those were one defect, in the product that can
least afford it.

`test_serve_cors.py` existed in QRME and JIM-mini and not in PDI, and so did
the code it guards. Both siblings' `serve` opens CORS for a loopback bind
because the packaged console calls the API from its own origin and dies as
"Failed to fetch" otherwise. PDI's frozen backend does the same, so the
**installed** app worked. `python -m pdi serve` — the from-source path — set
nothing.

Measured over HTTP with the console's origin on the request, because CORS is
a browser rule and an in-process test client never sends an `Origin` at all:

    OPTIONS /terms   →  405, no access-control headers
    GET     /terms   →  200, no access-control-allow-origin

Every in-process test in that product passed throughout.

## Why a recorded manifest rather than a live comparison

The three repositories are rarely checked out together, so a live comparison
skips in CI. This estate already learned that lesson once — the sibling
vocabulary check in `test_the_refusal_names_the_field_on_the_form.py` carries
a comment saying its first draft looked in the wrong place and skipped every
run, and *a check that never runs is not a check*.

So the shared vocabulary is written down. `shared_guards.txt` lists what all
three carry and `guard_divergences.txt` lists what exactly two do, naming the
product that lacks each one. Both are byte-identical in the three
repositories. Every product can then check its own half alone:

* every name in the manifest must exist here;
* every divergence naming *another* product must exist here, because it is
  carried by two of the three and this is not the one that lacks it;
* every divergence naming *this* product must be absent here, so a port that
  lands without being recorded fails rather than passing quietly.

Three checks, no siblings required. The live three-way comparison runs on top
of that whenever the siblings are on disk.

## A name is not a behaviour

This compares function names. A guard ported under a different name reads as
missing; one that kept its name while its body was gutted reads as present.
PDI reports its version from `/health` under a differently-named test, and
this file would call that a gap if the record did not hold it as a row.

That limit is worth the check anyway, because the failure it catches is the
one that actually happens: not a renamed guard, but a fix that never
travelled.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from . import ratchets

#: This product's name in the records.
ME = "jim"

#: Where the siblings sit when they are checked out. Absolute paths included
#: on purpose: these three repositories live under different roots on the
#: machine they are developed on, and the sibling check that only looked at
#: `REPO.parent` skipped every run for releases.
SIBLINGS = {
    "qrme": ("/home/user/QRME/tests", "../QRME/tests", "../qrme/tests"),
    "pdi": ("/workspace/pdi/pdi/tests", "../pdi/pdi/tests",
            "../PDI/pdi/tests"),
}

TESTS = Path(__file__).resolve().parent
MANIFEST = TESTS / "shared_guards.txt"
RECORD = TESTS / "guard_divergences.txt"


def guard_names(root: Path) -> set[str]:
    """Every `def test_*` in a suite directory."""
    found: set[str] = set()
    for path in sorted(root.glob("test_*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:                     # pragma: no cover - none today
            continue
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                    and node.name.startswith("test_"):
                found.add(node.name)
    return found


def _rows(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")]


def _parsed() -> list[tuple[str, str, str, str]]:
    """Each row as (product that lacks it, guard name, class, note).

    The class is what turned this record from a heap into something a person
    can spend an afternoon on: it says which rows could possibly be defects.
    """
    out = []
    for row in _rows(RECORD):
        head, _, rest = row.partition("|")
        product, name = [x.strip() for x in head.split(":", 1)]
        cls, _, note = rest.partition("|")
        out.append((product, name, cls.strip(), note.strip()))
    return out


def _divergences() -> dict[str, str]:
    """name -> the product recorded as lacking it."""
    return {name: product for product, name, _cls, _note in _parsed()}


def _routes_here() -> set[tuple[str, ...]]:
    """This product's live route table, as segment tuples with `{...}` wild.

    Built here rather than read from a list, because the whole point of the
    `deliberate` class is that it is a claim about what this product serves
    *now* — a recorded list would be a second thing to keep true.
    """
    from . import clientpaths
    from .test_error_report_carries_nothing_private import _app

    return {tuple("*" if "{" in s else s
                  for s in route.path.strip("/").split("/"))
            for route in clientpaths.all_routes(_app())}


def _reaches(shape: str) -> bool:
    want = tuple("*" if "{" in s else s for s in shape.strip("/").split("/"))
    for served in _routes_here():
        if len(served) == len(want) and all(
                a == b or a == "*" or b == "*" for a, b in zip(want, served)):
            return True
    return False


def _sibling_dirs() -> dict[str, Path]:
    found = {}
    for name, candidates in SIBLINGS.items():
        for c in candidates:
            p = Path(c) if c.startswith("/") else (TESTS / c)
            if p.is_dir():
                found[name] = p.resolve()
                break
    return found


def test_a_deliberate_divergence_is_a_feature_this_product_still_lacks():
    """The class that carries 48 of these rows, checked rather than asserted.

    `deliberate` means this product serves none of the routes the sibling's
    guard drives, so the guard cannot be a lost fix — the feature is not here
    to have lost it for. That is a claim about today's route table, and route
    tables grow.

        asked     is this difference deliberate
        mattered  is it still

    A row that starts failing here is the interesting case and not a chore:
    the feature arrived and its guard did not travel with it, which is the
    exact defect this whole file was written after.
    """
    arrived = []
    for product, name, cls, note in _parsed():
        if product != ME or cls != "deliberate":
            continue
        for shape in note.split():
            if _reaches(shape):
                arrived.append(f"{name} — this product now serves {shape}")
                break
    assert not arrived, (
        f"{len(arrived)} divergence(s) recorded as deliberate are about "
        "routes this product now serves:\n    " + "\n    ".join(arrived[:20])
        + "\n  Port the guard, or move the row to `candidate` and say why "
          "not.")


def test_the_candidate_divergences_only_shrink():
    """The rows that could be defects, counted separately from the rows that
    could not. A backlog whose every row costs the same attention is a backlog
    nobody starts."""
    text = RECORD.read_text(encoding="utf-8")
    ceiling = int(re.search(r"# candidates: (\d+)", text).group(1))
    found = [n for _p, n, cls, _ in _parsed() if cls == "candidate"]
    assert len(found) <= ceiling, (
        f"{len(found)} candidate divergences, above the {ceiling} recorded:\n"
        "    " + "\n    ".join(sorted(found)[:20]))


def test_every_row_carries_a_class_this_file_knows():
    """A guard on the record. A row whose class is a typo would be counted by
    no check and read by nobody — the same silence the flat list had, in one
    row instead of all of them."""
    known = {"candidate", "deliberate", "answered", "unclassified"}
    strange = sorted({cls for _p, _n, cls, _ in _parsed()} - known)
    assert not strange, f"unknown class(es) in the record: {strange}"


def test_every_shared_guard_is_present_here():
    """The manifest, checked against this suite alone. A guard deleted from
    one product used to be invisible until somebody happened to diff two
    repositories."""
    mine = guard_names(TESTS)
    missing = sorted(set(_rows(MANIFEST)) - mine)
    assert not missing, (
        f"{len(missing)} guard(s) the three products share are not in this "
        "suite:\n    " + "\n    ".join(missing[:20])
        + "\n  Either it was deleted here alone, or it was renamed — and a "
          "rename is a divergence too, because the sibling still asks the "
          "question under the old name.")


def test_every_divergence_belonging_to_a_sibling_is_present_here():
    """The other half of what this product can verify alone. A row naming
    JIM-mini or PDI is carried by two of the three, and this is not the one
    that lacks it."""
    mine = guard_names(TESTS)
    missing = sorted(n for n, who in _divergences().items()
                     if who != ME and n not in mine)
    assert not missing, (
        f"{len(missing)} guard(s) recorded as carried here are gone:\n    "
        + "\n    ".join(missing[:20])
        + "\n  If this product genuinely stopped needing them, move the rows "
          "— but a row can only name one product, so two products lacking a "
          "guard means it leaves both records.")


def test_every_divergence_recorded_against_this_product_is_still_absent():
    """The direction that keeps the record from going stale in the good
    direction. A port that lands and is not recorded means the next sweep
    reports a divergence that was fixed a release ago."""
    mine = guard_names(TESTS)
    landed = sorted(n for n, who in _divergences().items()
                    if who == ME and n in mine)
    assert not landed, (
        f"{len(landed)} guard(s) recorded as missing from this product are "
        "now here:\n    " + "\n    ".join(landed[:20])
        + "\n  Move them to shared_guards.txt and lower the ceiling in "
          "guard_divergences.txt. Paying a backlog down is the one edit that "
          "file is for.")


def test_the_divergence_record_only_shrinks():
    """A new divergence is a fix that did not travel."""
    ceiling = int(re.search(r"# ceiling: (\d+)",
                            RECORD.read_text(encoding="utf-8")).group(1))
    rows = _rows(RECORD)
    assert len(rows) <= ceiling, (
        f"{len(rows)} divergences, above the {ceiling} recorded")


def test_the_records_name_only_the_three_products():
    """A guard on the record. A typo in the product column would make a row
    unverifiable by anyone: no product would claim it and none would deny it."""
    known = {ME} | set(SIBLINGS)
    unknown = sorted({row.split(": ", 1)[0] for row in _rows(RECORD)} - known)
    assert not unknown, f"unknown product(s) in the record: {unknown}"
    assert len(_divergences()) == len(_rows(RECORD)), (
        "a guard name appears twice in the divergence record, so one of the "
        "two rows is unreachable")


def test_the_reader_can_still_see_this_suite():
    """The 0.59.0 lesson applied to this file's own reader. A parser that
    stopped matching would report a suite with no guards, and every check
    above would pass on an empty set."""
    found = len(guard_names(TESTS))
    assert found >= ratchets.floor("suite.guard_names"), (
        f"only {found} test functions found in this suite — the reader has "
        "stopped matching, and a manifest checked against nothing passes")


def test_the_record_matches_the_siblings_when_they_are_checked_out():
    """The live three-way comparison, which is what keeps the two records
    honest. It skips when the siblings are absent — but it has to actually
    find them when they are there, so the skip reason names where it looked.
    """
    siblings = _sibling_dirs()
    if len(siblings) != len(SIBLINGS):
        pytest.skip(
            "siblings not checked out beside this product; looked in "
            + ", ".join(c for cs in SIBLINGS.values() for c in cs))
    suites = {ME: guard_names(TESTS)}
    suites.update({name: guard_names(d) for name, d in siblings.items()})

    shared, diverged = set(), {}
    for name in set().union(*suites.values()):
        carriers = [p for p, s in suites.items() if name in s]
        if len(carriers) == 3:
            shared.add(name)
        elif len(carriers) == 2:
            diverged[name] = next(p for p in suites if p not in carriers)

    problems = []
    if shared != set(_rows(MANIFEST)):
        gained = sorted(shared - set(_rows(MANIFEST)))
        lost = sorted(set(_rows(MANIFEST)) - shared)
        problems.append(
            f"shared_guards.txt is out of date: {len(gained)} name(s) now in "
            f"all three and unrecorded, {len(lost)} recorded and no longer "
            "shared:\n    " + "\n    ".join((gained + lost)[:20]))
    if diverged != _divergences():
        new = sorted(n for n, who in diverged.items()
                     if _divergences().get(n) != who)
        gone = sorted(n for n in _divergences() if n not in diverged)
        problems.append(
            f"guard_divergences.txt is out of date: {len(new)} new or "
            f"reassigned, {len(gone)} resolved:\n    "
            + "\n    ".join((new + gone)[:20]))
    assert not problems, "\n\n".join(problems) + (
        "\n  Both records are byte-identical in the three repositories; "
        "regenerate and copy them across together.")

def test_the_manifest_says_how_many_it_carries():
    """The count in the header is the number of rows beneath it.

    It said 482 while the file carried 490 — eight guards added over eight
    rounds, each one appending a line and none touching the sentence above
    them. Nothing read that number, so nothing noticed, and a header nobody
    checks is a comment wearing a status.

        asked     is the row here
        mattered  does the file still describe itself

    Cheap, and it earns its place by catching the edit that adds a name
    without thinking about the whole: the two go in together or they
    disagree. `release_fields.txt` has carried exactly this pairing since it
    was written, and is the reason its count never drifted.
    """
    lines = MANIFEST.read_text(encoding="utf-8").splitlines()
    stated = int(re.search(r"^# status: manifest — (\d+) guards", lines[0]).group(1))
    assert stated == len(_rows(MANIFEST)), (
        f"shared_guards.txt says it carries {stated} guards and lists "
        f"{len(_rows(MANIFEST))}"
    )
