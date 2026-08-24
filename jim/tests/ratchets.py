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


def _erase_planted() -> int:
    from .test_an_erase_is_measured_against_the_schema import plantable
    return plantable()


def _erase_scoped() -> int:
    from .test_an_erase_is_measured_against_the_schema import scoped_tables
    return len(scoped_tables())


def _route_shapes() -> int:
    from .test_a_screen_expects_the_shape_the_route_returns import route_shapes
    return len(route_shapes())


def _calls_typed() -> int:
    from .test_a_screen_expects_the_shape_the_route_returns import calls
    return len(calls())


def _guard_names() -> int:
    from .test_the_three_suites_ask_the_same_questions import TESTS, guard_names
    return len(guard_names(TESTS))


def _files_swept() -> int:
    from .test_a_floor_is_within_sight_of_what_it_measures import parsed_files
    return parsed_files()


def _pack_entries() -> int:
    from jim import knowledge
    return len(knowledge.ENTRIES)


def _pack_thinnest_area() -> int:
    from jim import knowledge
    return min(len(t) for t in knowledge.catalog()["areas"].values())


def _nav_tabs() -> int:
    from .test_a_key_with_no_row_reads_as_itself import _tab_ids
    return len(_tab_ids())


def _surfaces() -> int:
    from .test_a_key_with_no_row_reads_as_itself import _python_enum
    return len(_python_enum("SURFACES"))


#: The registry. Every entry replaced a bare literal inside an assertion; the
#: assertion now reads its number from here, which is what takes it out of the
#: unregistered backlog.
def _language_tables() -> int:
    """How many of `jim/i18n.py`'s translation tables the reader finds.

    The quantity the floor in `test_the_table_is_complete_in_every_language`
    guards. That guard walks every `_UPPER_CASE` dict on the module and checks
    each row for a missing language; a reader that stopped matching would walk
    nothing and report a clean sweep over zero sentences — which is precisely
    what the first draft did, because `"_FIELD_LABELS".isupper()` is True and
    the clause meant to exclude constants excluded every table.
    """
    from jim import i18n

    return len([n for n in dir(i18n)
                if n.startswith("_") and n[1:].isupper()
                and isinstance(getattr(i18n, n), dict)])



def _literal_refusals() -> int:
    """Refusal sentences written as a plain string, as the classifier counts
    them now. The floor is here rather than inside the assertion because a
    number in an assertion is a number nothing compares against what it
    measures — and this one guards the walk that every other refusal check
    is built on."""
    from pathlib import Path

    from .test_the_guardian_refuses_in_one_language import REPO, _refusals
    return len(_refusals(REPO / "jim")["literal"])


def _translated_refusals() -> int:
    """Rows in the hand-translated refusal table.

    Its assertion carried a literal 21 while the table held 147 — a floor far
    below what it measures, which answers "is the number satisfied" every run
    and would not notice the table being gutted. Registered so the comparison
    happens rather than being assumed.
    """
    from jim import i18n
    return len(i18n._REFUSALS)


# -- the client-shape extractors -------------------------------------------
#
# The largest cluster in `unregistered_floors.txt`, and the one the first
# sweep predicted would be worst: every one of these reads a shell that has
# roughly tripled since its floor was written. `wire.declared` was 240 against
# 688 — two-thirds of the wire surface could vanish under it. The README pair
# were 40 against 256 and 261, which is a sixth.


def _swift_structs() -> int:
    from .test_the_shape_the_swift_client_expects import _structs
    return len(_structs())


def _swift_fields() -> int:
    from .test_the_shape_the_swift_client_expects import _structs
    return sum(len(f) for f in _structs().values())


def _swift_bindings() -> int:
    from .test_the_shape_the_swift_client_expects import _bindings
    return len(_bindings())


def _console_shapes() -> int:
    from .test_the_shape_the_console_expects import _shapes
    return len(_shapes())


def _console_shape_fields() -> int:
    from .test_the_shape_the_console_expects import _shapes
    return sum(len(f) for f in _shapes().values())


def _console_gets() -> int:
    from .test_the_shape_the_console_expects import _gets
    return len(_gets())


def _client_bindings() -> int:
    from .test_the_shape_the_client_expects import _bindings
    return len(_bindings())


def _wire_declared() -> int:
    from .test_one_name_one_type_on_the_wire import _declared
    return len(_declared())


def _shell_files(kind: str):
    def go() -> int:
        from . import test_the_shells_still_parse as m
        return len(getattr(m, kind))
    return go


def _xaml_named() -> int:
    from .test_the_shells_still_parse import XAML, _XNAME
    return sum(len(set(_XNAME.findall(p.read_text(encoding="utf-8"))))
               for p in XAML)


def _xaml_handlers() -> int:
    from .test_the_shells_still_parse import XAML, _handlers
    checked, _ = _handlers(XAML)
    return checked


def _xaml_driveable() -> int:
    from .test_the_shells_still_parse import XAML, _undriveable
    driven, _ = _undriveable(XAML)
    return driven


def _readme_rows() -> int:
    from .test_the_readme_says_what_shipped import _rows
    return len(_rows())


def _readme_released() -> int:
    from .test_the_readme_says_what_shipped import _released
    return len(_released())


def _validation_messages() -> int:
    from jim import i18n
    return len(i18n._VALIDATION)


# -- the readers that stand between a guard and nothing ---------------------
#
# Every one of these sits under a docstring saying, in its own words, that a
# reader which stopped reading would report a clean result by finding nothing
# to complain about. `console.l10n_keys` is the sharpest in the estate so far:
# a floor of 15 against 1,351, under a guard whose own words are "an empty
# table reports a perfect zero". It would have passed on one per cent.


def _route_writes() -> int:
    from .test_the_body_the_route_requires import WRITES, _sent
    return len([w for w in _sent() if w[0] in WRITES])


def _route_writes_readable() -> int:
    from .test_the_body_the_route_requires import WRITES, _sent
    return len([w for w in _sent() if w[0] in WRITES
                and w[2] in ("literal", "parameter") and w[3] is not None])


def _route_models() -> int:
    from .test_the_body_the_route_requires import _models
    return len(_models())


def _key_vocabulary() -> int:
    from .test_the_key_the_server_never_sends import _vocabulary
    return len(_vocabulary())


def _form_declared_fields() -> int:
    from .test_the_refusal_names_the_field_on_the_form import _declared
    return len(_declared())


def _console_l10n_keys() -> int:
    import re
    from .test_the_console_speaks_one_language import SRC
    return len(re.findall(r'^  "([\w.]+)":',
                          (SRC / "l10n.ts").read_text("utf-8"), re.M))


def _android_reads() -> int:
    from .test_the_keys_the_android_client_reads import _reads
    return len(_reads())


def _android_read_keychars() -> int:
    from .test_the_keys_the_android_client_reads import _reads
    return sum(len(k) for _, k in _reads())


RATCHETS: tuple[Ratchet, ...] = (
    Ratchet("route.writes", 124, _route_writes,
            "the write calls the extractor reads off the clients"),
    Ratchet("route.writes_readable", 80, _route_writes_readable,
            "the write calls whose body it can actually read"),
    Ratchet("route.models", 100, _route_models,
            "the request models FastAPI publishes in the schema"),
    Ratchet("key.vocabulary", 1872, _key_vocabulary,
            "the field names the leak check knows to look for"),
    Ratchet("form.declared_fields", 181, _form_declared_fields,
            "the request-model fields the refusal check maps to a control"),
    Ratchet("console.l10n_keys", 1080, _console_l10n_keys,
            "the keys in the console's translation table"),
    Ratchet("android.reads", 88, _android_reads,
            "the key reads the Android extractor finds"),
    Ratchet("android.read_keychars", 310, _android_read_keychars,
            "the characters across those keys, as a shape check on them"),
    Ratchet("swift.structs", 247, _swift_structs,
            "the Swift client's declared shapes"),
    Ratchet("swift.struct_fields", 1057, _swift_fields,
            "the fields across the Swift client's shapes"),
    Ratchet("swift.bindings", 129, _swift_bindings,
            "the Swift screens' bindings to those shapes"),
    Ratchet("console.shapes", 130, _console_shapes,
            "the console's declared shapes"),
    Ratchet("console.shape_fields", 789, _console_shape_fields,
            "the fields across the console's shapes"),
    Ratchet("console.gets", 116, _console_gets,
            "the console's read calls"),
    Ratchet("console.bindings", 53, _client_bindings,
            "the console screens' bindings to route shapes"),
    Ratchet("wire.declared", 550, _wire_declared,
            "every name declared on the wire, across all four clients"),
    Ratchet("shells.swift_files", 45, _shell_files("SWIFT"),
            "the Swift sources the shell parser reads"),
    Ratchet("shells.kotlin_files", 7, _shell_files("KOTLIN"),
            "the Kotlin sources the shell parser reads"),
    Ratchet("shells.csharp_files", 18, _shell_files("CSHARP"),
            "the C# sources the shell parser reads"),
    Ratchet("shells.xaml_files", 13, _shell_files("XAML"),
            "the XAML screens the markup checks reach"),
    Ratchet("shells.xaml_named", 751, _xaml_named,
            "the named elements across those XAML screens"),
    Ratchet("shells.xaml_handlers", 170, _xaml_handlers,
            "the XAML handlers checked against their code-behind"),
    Ratchet("shells.xaml_driveable", 672, _xaml_driveable,
            "the XAML elements the drive check reaches"),
    Ratchet("readme.history_rows", 204, _readme_rows,
            "the release history rows the README table carries"),
    Ratchet("readme.released", 208, _readme_released,
            "the releases the CHANGELOG declares"),
    Ratchet("i18n.validation_messages", 8, _validation_messages,
            "the validation sentences with a row in every language"),
    Ratchet("refusals.translated", 147, _translated_refusals,
            "rows in the hand-translated refusal table"),
    Ratchet("refusals.literal", 60, _literal_refusals,
            "refusals written as a plain string — the walk every other\n            refusal check stands on"),
    Ratchet("i18n.language_tables", 8, _language_tables,
            "translation tables the completeness sweep reads"),
    Ratchet("l10n.asked.ios", 612, _l10n("ios", "asked"),
            "screens on the iPhone that call the localizer"),
    # Raised from 390 in 0.84.0. It was the one l10n floor still sitting at
    # half its surface while its five siblings had all been carried up to
    # roughly four-fifths — 390 against 785, ratio 0.50, on the exact edge of
    # the guard that asks whether a floor is still near what it measures. A
    # handful of new call sites tipped it under and the guard said so, which
    # is the whole reason that guard exists: the drift had been there a while
    # and nothing had been failing.
    Ratchet("l10n.asked.android", 628, _l10n("android", "asked"),
            "screens on Android that call the localizer"),
    Ratchet("l10n.asked.windows", 578, _l10n("windows", "asked"),
            "screens on the desktop that call the localizer"),
    Ratchet("l10n.held.ios", 625, _l10n("ios", "held"),
            "rows in the iPhone's own L10n table"),
    Ratchet("l10n.held.android", 637, _l10n("android", "held"),
            "rows in Android's own L10n table"),
    Ratchet("l10n.held.windows", 602, _l10n("windows", "held"),
            "rows in the desktop's own L10n table"),
    Ratchet("route.calls.console", 200, _calls("console"),
            "call sites the route audit reads out of the console"),
    Ratchet("route.calls.ios", 245, _calls("ios"),
            "call sites the route audit reads out of the iPhone shell"),
    Ratchet("route.calls.android", 245, _calls("android"),
            "call sites the route audit reads out of the Android shell"),
    Ratchet("route.calls.windows", 240, _calls("windows"),
            "call sites the route audit reads out of the desktop shell"),
    Ratchet("route.table", 220, _route_table,
            "routes reachable by walking the included routers"),
    Ratchet("extractor.path_literals", 604, _path_literals,
            "path literals found across all four surfaces"),
    Ratchet("console.source_files", 29, _console_files,
            "TypeScript sources the console sink sweep reads"),
    Ratchet("console.calls_typed", 195, _calls_typed,
            "console calls that declare the shape they expect back"),
    Ratchet("erase.tables_planted", 40, _erase_planted,
            "tables this suite can put a probe row into"),
    Ratchet("erase.scoped_tables", 52, _erase_scoped,
            "tables the schema scopes to a single user"),
    Ratchet("route.declared_shapes", 210, _route_shapes,
            "routes whose answer is decisively a list or an object"),
    Ratchet("markup.strings_scanned", 7, _markup_strings,
            "f-strings in this package that build markup"),
    # 1685, from 1050. The floor had fallen to under half of the 2107
    # functions actually there, and a floor at half is decoration: the
    # suite could lose a thousand guards and this would still pass. Raised
    # to four-fifths of the real count, which is what the sibling check
    # `test_no_registered_floor_is_decoration` asks of every row here.
    Ratchet("suite.guard_names", 1685, _guard_names,
            "test functions this suite declares"),
    Ratchet("sweep.files_parsed", 130, _files_swept,
            "test files the bare-floor sweep can read"),
    Ratchet("knowledge.entries", 39, _pack_entries,
            "hand-written entries in the offline pack"),
    Ratchet("knowledge.thinnest_area", 5, _pack_thinnest_area,
            "entries in the offline pack's thinnest area — the target was "
            "'jampacked', held per area rather than in total"),
    Ratchet("console.nav_tabs", 20, _nav_tabs,
            "tabs the console's navigation declares — the floor under the "
            "check that every one of them has a label"),
    Ratchet("presence.surfaces", 8, _surfaces,
            "surfaces the presence can speak through — the floor under the "
            "check that every one of them has a word and a note"),
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
