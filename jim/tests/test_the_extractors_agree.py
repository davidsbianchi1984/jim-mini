"""Three copies of one guard, and three different blind spots.

## The finding

`clientpaths.py` says of itself, in its own docstring, that it is *byte-
identical in qrme, jim-mini and pdi*. It was not, and nothing checked.

JIM's had grown two capabilities the other two never received: a `reqText`
console helper, and Kotlin's direct-connection form where the whole URL sits
in the literal (`URL("$base/baseline/$uid")`) rather than a bare path. So the
same audit, asked the same question in three repositories, gave three
different answers — and every repository believed it was running the same
check.

    asked     does this repo's audit pass
    mattered  is this repo's audit the same audit

PDI's Android client submits an intake through exactly the form its extractor
could not see. The door was there, the route was there, and the guard that
exists to notice a mismatch could not see either.

Porting the missing capability then produced a *second* finding, of the same
kind one layer in: the rule arrived carrying JIM's premise. Its direct-
connection form was declared `verb="GET"` because "every array route in this
shell is a GET" — true where it was written, false in PDI, which POSTs. The
verb is now read from the `.apply { }` block rather than assumed, which
needed the extractor to look past the call's own parentheses for the first
time.

## What this file does

Runs each extractor over a fixture whose answer is written down here. A
capability lost, in any one of the three repositories, fails here — in that
repository — instead of quietly reporting a clean sweep.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from . import clientpaths


FIXTURES = (Path(__file__).resolve().parent
            / "extractor_fixtures")

#: What every one of the three copies must find.
#:
#: Written down rather than compared between repos, because a cross-repo
#: comparison is a check no single repository can run — and one that nobody
#: runs is the state this file exists to end.
#:
#: **The Android row is deliberately not the same shape as the other two.**
#: iOS and Windows normalise an interpolated segment to a placeholder;
#: Kotlin's leaves `$id` standing. Route matching is unaffected — Starlette's
#: path parameter matches any segment either way — so this costs nothing
#: today. It is written here rather than quietly encoded because a difference
#: nobody has looked at is how the last three divergences started, and the
#: point of this file is to stop that happening a fourth time.
EXPECTED = {
    "ios": {("GET", "/fixture/plain"), ("DELETE", "/fixture/x/nested")},
    "android": {("GET", "/fixture/plain"), ("POST", "/fixture/direct"),
                ("DELETE", "/fixture/$id/nested")},
    "windows": {("POST", "/fixture/plain"), ("DELETE", "/fixture/x/nested")},
}


def _language(name):
    for lang in clientpaths.NATIVE:
        if lang.name == name:
            return lang
    raise AssertionError(f"no {name} language in this extractor")


@pytest.mark.parametrize("shell", sorted(EXPECTED))
def test_the_extractor_reads_every_shape_it_claims_to(shell):
    lang = _language(shell)
    probe = clientpaths.Language(lang.name, FIXTURES, lang.suffixes,
                                 lang.interpolation, lang.literal, lang.calls)
    found = set(clientpaths.calls(probe))
    missing = EXPECTED[shell] - found
    extra = found - EXPECTED[shell]
    assert not missing and not extra, (
        f"{shell}'s extractor no longer reads the fixture as documented.\n"
        f"  missing: {sorted(missing)}\n  unexpected: {sorted(extra)}\n"
        "  A capability lost here is a door this audit stops being able to "
        "see, and it reports that as a clean result.")


def test_the_fixture_is_actually_there():
    """A guard on the guard: an empty directory reads as three clean shells."""
    files = sorted(p.name for p in FIXTURES.iterdir() if p.is_file())
    assert len(files) == 3, f"expected three fixture files, found {files}"
