"""One home for the numbers that say *the reader is still reading*.

## Where this came from

Two rounds running found the same defect in two different instruments, and
0.58.9 closed by naming the general case rather than the instance: a floor
written when the surface was small, never raised as the surface grew. The
route reader's floor was set when the console was the only client. The
localizer's was ten, against nine hundred and forty-five.

Both were fixed one file at a time. This is the sweep, and the sweep needed a
convention before it needed code, because a floor is spelled a dozen ways —
`assert len(found) > 20`, `assert total >= 40`, a `FLOORS` tuple, a bare
`_MIN_PATHS`. Nothing could walk them all and ask the only question that
matters about a floor:

    asked     is the number satisfied
    mattered  is the number still near what it measures

## What a Ratchet is

A floor plus **the way to measure the same quantity now**. That second half is
the whole convention: a number with no attached measurement cannot be audited,
which is why 69 of them in this product, across 36 files, had never been
compared against anything.

Registering one has three effects. The number lives in one place instead of
inside an assertion. `test_a_floor_is_within_sight_of_what_it_measures.py`
checks it against reality every run. And it leaves the unregistered-floor
backlog, which only shrinks.

## What the sweep found on its first run

What the same standard finds here is not quite the same picture, and the
difference is the interesting part:

    l10n asked, per shell        10 against 279-312      ratio 0.04
    l10n held, per shell         20 against 286-312      ratio 0.07
    path literals, all surfaces  40 against 466          ratio 0.09
    native call sites            20 against 113-114      ratio 0.18
    console call sites          200 against 251          ratio 0.80  held

The last row is the one that makes the point, because it is the one that
passed. `assert len(made) > 200` sits at four-fifths of what this console
actually produces — an honest floor. The identical literal in QRME sits at
0.47 of a console that grew to 429 call sites, and the identical literal is
why: **one number written to work in three repositories is a number
calibrated for whichever of them was smallest when it was written.** It aged
into decoration in the largest product while reading as fine in this one.

`test_the_console_is_a_client_too.py` said as much in its own docstring — the
floor of twenty was set low deliberately *because the three products' shells
differ by a factor of three in size*. That is a true sentence about why the
number is small and a false one about what it holds. Twenty against this
product's 113 native call sites is a fifth.

That is why these live per product, measured per product, and not in a shared
constant.

## The floors are ratchets, not targets

Each records what its reader reaches today, set at roughly four-fifths. Raising
one when the surface grows is ordinary. Lowering one is a deliberate edit that
shows up in a diff, and the only honest reason is a surface that genuinely got
smaller.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Ratchet:
    """A floor, and how to read the same quantity now.

    `measure` is deliberately a callable rather than a recorded number. A
    recorded number would go stale in exactly the way this file exists to
    catch — it would be a second floor needing its own audit.
    """

    name: str
    floor: int
    measure: Callable[[], int]
    why: str


def _l10n(shell: str, half: str) -> Callable[[], int]:
    def go() -> int:
        from . import test_a_shell_asks_for_a_key_it_has as m
        return len((m._asked if half == "asked" else m._held)(shell))
    return go


def _calls(lang: str) -> Callable[[], int]:
    def go() -> int:
        from . import clientpaths
        return len(clientpaths.calls(getattr(clientpaths, lang.upper())))
    return go


def _route_table() -> int:
    from jim.api import app

    from . import clientpaths
    return len(clientpaths.all_routes(app))


def _path_literals() -> int:
    from . import clientpaths
    from .test_the_extractor_knows_every_call_shape import SURFACES
    return sum(len(clientpaths.paths(lang)) for lang in SURFACES.values())


def _console_files() -> int:
    from .test_a_value_in_a_script_is_not_markup import console_files
    return len(console_files())


def _markup_strings() -> int:
    from .test_a_page_never_prints_what_it_was_given import scanned
    return scanned()


def _guard_names() -> int:
    from .test_the_three_suites_ask_the_same_questions import TESTS, guard_names
    return len(guard_names(TESTS))


def _files_swept() -> int:
    from .test_a_floor_is_within_sight_of_what_it_measures import parsed_files
    return parsed_files()


#: The registry. Every entry replaced a bare literal inside an assertion; the
#: assertion now reads its number from here, which is what takes it out of the
#: unregistered backlog.
RATCHETS: tuple[Ratchet, ...] = (
    Ratchet("l10n.asked.ios", 240, _l10n("ios", "asked"),
            "screens on the iPhone that call the localizer"),
    Ratchet("l10n.asked.android", 245, _l10n("android", "asked"),
            "screens on Android that call the localizer"),
    Ratchet("l10n.asked.windows", 220, _l10n("windows", "asked"),
            "screens on the desktop that call the localizer"),
    Ratchet("l10n.held.ios", 240, _l10n("ios", "held"),
            "rows in the iPhone's own L10n table"),
    Ratchet("l10n.held.android", 245, _l10n("android", "held"),
            "rows in Android's own L10n table"),
    Ratchet("l10n.held.windows", 225, _l10n("windows", "held"),
            "rows in the desktop's own L10n table"),
    Ratchet("route.calls.console", 200, _calls("console"),
            "call sites the route audit reads out of the console"),
    Ratchet("route.calls.ios", 90, _calls("ios"),
            "call sites the route audit reads out of the iPhone shell"),
    Ratchet("route.calls.android", 90, _calls("android"),
            "call sites the route audit reads out of the Android shell"),
    Ratchet("route.calls.windows", 90, _calls("windows"),
            "call sites the route audit reads out of the desktop shell"),
    Ratchet("route.table", 220, _route_table,
            "routes reachable by walking the included routers"),
    Ratchet("extractor.path_literals", 370, _path_literals,
            "path literals found across all four surfaces"),
    Ratchet("console.source_files", 29, _console_files,
            "TypeScript sources the console sink sweep reads"),
    Ratchet("markup.strings_scanned", 7, _markup_strings,
            "f-strings in this package that build markup"),
    Ratchet("suite.guard_names", 1050, _guard_names,
            "test functions this suite declares"),
    Ratchet("sweep.files_parsed", 130, _files_swept,
            "test files the bare-floor sweep can read"),
)

_BY_NAME = {r.name: r for r in RATCHETS}


def floor(name: str) -> int:
    """The registered floor, by name.

    Assertions call this instead of carrying a literal. A name that is not
    registered is a mistake worth failing on rather than defaulting past — a
    silent default here would be a floor of nothing, which is the whole
    subject of this file.
    """
    try:
        return _BY_NAME[name].floor
    except KeyError:
        raise KeyError(
            f"no ratchet named {name!r}; registered: "
            + ", ".join(sorted(_BY_NAME))) from None
