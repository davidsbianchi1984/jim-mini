"""A path literal the route audit cannot see, and the work it invents.

## The finding

`clientpaths.py` extracts a client's requests by finding the openers it knows
— `request(`, `Post(`, `` req`…` `` — and reading the path out of the
arguments. Every one of those is a *shape* of call, and a client is free to
write a shape nobody taught it.

That has now happened four times, and the file records all four: the nested
template literal, the `<img src>` with no callee, the `reqText` sibling of
`req`, and Android's direct-connection form. Each was found the same way —
somebody went to build a door and found the door already there.

    asked     does the extractor understand the calls it knows about
    mattered  does the extractor know about all the calls

Every earlier guard-on-guard in this file checks the first question. This one
checks the second, which is the one that had been left to luck.

## What it found on the day it was written

Two shapes, both real, both producing routes that sat on a doorless backlog
with working doors behind them:

* `getArray("/goals/$uid", token)` — a private helper in JIM's Android client
  that opens its own connection, so the path literal is at the caller and no
  known opener encloses it. Six routes.

  Worth being precise about why nothing caught it earlier: those paths were
  not invisible. Each was attributed under its **write** verb, from the
  `request(path, "POST", …)` a few lines away, so any check comparing the set
  of *paths* a client mentions against the set it calls read them as covered.
  Only the GET was missing, and only a positional check can tell.

* `val path = if (…) "/packs" else "/packs?industry=" + enc(x)` then
  `request(path)` — in QRME's Android client. The literal is one statement
  away from the call, which an argument reader cannot follow. Fixed at the
  call site rather than by teaching the extractor to chase assignments: a
  path spelled where it is sent is easier to read too.

## What stays recorded

Not every path-shaped literal is a request. A URL handed to an image view, a
path shown to a person as text, a regex that begins with `/`. Those are listed
in `extractor_unattributed.txt` with a reason each, and the record is
ratcheted in both directions — a new one has to be justified, and one that has
gone has to be struck, or the record becomes a place where blind spots hide.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from . import clientpaths as cp

RECORD = Path(__file__).resolve().parent / "extractor_unattributed.txt"

SURFACES = {lang.name: lang for lang in (cp.CONSOLE, *cp.NATIVE)}


def _recorded() -> set[str]:
    return {line.strip() for line in RECORD.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


@pytest.mark.parametrize("surface", sorted(SURFACES))
def test_every_path_literal_is_inside_a_call_the_audit_knows(surface):
    """The defect, directly.

    A literal no call form encloses is either a path this surface does not
    request — which the record says, and says why — or a request the audit
    cannot see, and therefore a door the backlog is about to call missing.
    """
    found = set(cp.unattributed(SURFACES[surface]))
    undecided = sorted(found - _recorded())
    assert not undecided, (
        f"{len(undecided)} path literal(s) in the {surface} surface sit "
        "outside every call shape the route audit knows:\n    "
        + "\n    ".join(undecided)
        + "\n  If these are requests, teach clientpaths.py the shape or spell "
          "the path at the call site. If they are not, record them with the "
          "reason — but the record is ratcheted.")


def test_the_record_holds_nothing_that_has_gone():
    """The other direction.

    A line left in the record after the literal it names is deleted or moved
    into a call is a hole: the next literal to land on that exact text would
    be waved through. Records that only ever grow stop being records.
    """
    live = set()
    for lang in SURFACES.values():
        live |= set(cp.unattributed(lang))
    stale = sorted(_recorded() - live)
    assert not stale, (
        f"{len(stale)} recorded line(s) name a literal that is no longer "
        "unattributed — strike them from extractor_unattributed.txt:\n    "
        + "\n    ".join(stale))


def test_the_check_is_looking_at_something():
    """A guard on the guard, and this one has earned its place twice over.

    If `unattributed()` returned nothing because the literal patterns stopped
    matching, every test above would pass on an empty set — the exact failure
    mode this whole file exists to catch, reproduced inside it.
    """
    total = sum(len(cp.paths(lang)) for lang in SURFACES.values())
    assert total >= 40, (
        f"only {total} path literals found across {len(SURFACES)} surfaces — "
        "the extraction has stopped matching, and an emptiness check passes "
        "on nothing")
