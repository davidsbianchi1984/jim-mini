"""A ratchet file has to say, at the top, what it currently is.

## The finding

`public_untranslated.txt` opened with a paragraph explaining that
`Onboarding.tsx` — the screen every person in the world meets first — carried
forty-odd English strings, that translating them was "its own round", and that
a half-translated sign-up form would be worse than an English one.

All of that was true when it was written. Two rounds later `The screen
everybody meets first` translated them and `The pre-session backlog reaches its
floor` took the count to four. Neither round struck the paragraph; the second
appended its own note *below* it:

    What is left is not prose. A product name, a punctuation mark, an
    example address and an example code — strings that are the same in
    every language. This is the floor, not a backlog.

So the file held two statements about itself, the false one first. Read
top-down — which is how anybody reads a file, and how the round that produced
this guard read it — it advertises a backlog that had been cleared, and the
correction is twenty lines further on.

    asked     is the record complete
    mattered  does the record still describe the code

Nothing was wrong with the ratchet: the numbers were right the whole time. The
prose around them had simply outlived the thing it described, and a record only
works if a reader can trust the first thing it says.

## What this checks

Every ratchet leads with a `# status:` line naming what it is and how many rows
it holds, and that count is checked against the rows. `floor` means the
remainder is permanent and is not work; `backlog` means somebody still owes it.
The two are indistinguishable from the numbers alone — `console_untranslated`
sits exactly at its ceiling with 1,459 strings still to translate, and
`public_untranslated` sits exactly at its ceiling and is finished — which is
precisely why the file has to say which it is, in a line that cannot drift from
the rows beneath it.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent

#: Every record with a ceiling — the ratchets proper. Files without one are
#: plain measurements (the doorless lists) and are rebuilt wholesale.
def _ratchets() -> list[Path]:
    return sorted(p for p in HERE.glob("*.txt")
                  if re.search(r"^# ceiling:", p.read_text(encoding="utf-8"),
                               re.M))


def _rows(path: Path) -> int:
    return len([l for l in path.read_text(encoding="utf-8").splitlines()
                if l.strip() and not l.lstrip().startswith("#")])


def test_there_are_ratchets_to_check():
    """A guard on the guard: a glob that stopped matching would report every
    ratchet in perfect order by finding none of them."""
    found = _ratchets()
    assert len(found) >= 2, (
        f"only {len(found)} ratchet file(s) found in {HERE.name} — the checks "
        "below are passing on almost nothing")


@pytest.mark.parametrize("path", _ratchets(), ids=lambda p: p.name)
def test_every_ratchet_says_what_it_is_before_it_says_anything_else(path):
    """The status line leads. Not "the file contains a status somewhere": a
    correction twenty lines below a stale claim is what this exists to stop."""
    first = path.read_text(encoding="utf-8").splitlines()[0]
    assert re.match(r"^# status: (floor|backlog) — \d+ rows$", first), (
        f"{path.name} opens with {first!r}. Every ratchet's first line must be "
        "`# status: floor|backlog — N rows`, because a reader takes the first "
        "claim a file makes and this one had a cleared backlog advertised at "
        "the top for two releases.")


@pytest.mark.parametrize("path", _ratchets(), ids=lambda p: p.name)
def test_the_status_line_counts_the_rows_that_are_there(path):
    """A summary nobody checks is the thing that went stale in the first
    place."""
    text = path.read_text(encoding="utf-8")
    said = int(re.search(r"^# status: \w+ — (\d+) rows$", text, re.M).group(1))
    actual = _rows(path)
    assert said == actual, (
        f"{path.name} says {said} rows and holds {actual}. The count in the "
        "status line is the one thing a reader takes on trust, so it is the "
        "one thing that must not be written by hand and left alone.")


# A third check was written here and struck before it shipped: "a file calling
# itself a floor must sit exactly at its ceiling". It fired on
# `native_untranslated.txt`, which this release took from three rows to none —
# a floor of zero under a ceiling of three, and the best kind there is.
#
# `floor` is a claim about what the remaining rows *are*, not how many. It
# cannot be derived from the numbers, which is the whole reason the file has to
# declare it, and a check that pretended otherwise would have been one more
# guard answering the question next to the one that matters.
