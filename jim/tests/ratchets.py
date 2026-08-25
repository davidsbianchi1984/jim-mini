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


# -- what each shell puts on a screen ---------------------------------------
#
# Registered per shell rather than once, because the assertion runs inside a
# loop over SHELLS and one number cannot be four-fifths of three different
# surfaces. The same reason `l10n.asked.ios` and its siblings are separate
# entries: this estate has already learned that a literal shared across
# shells is calibrated for whichever was smallest.
#
# The floor was 100 for all three, against 1,453 / 1,089 / 3,302 — three per
# cent in the Windows shell, under a docstring that says a scan "reporting a
# handful is far more likely to be broken than to be good news".


def _shell_shown(shell: str):
    def go() -> int:
        from .test_a_shell_does_not_print_what_it_translated import SHELLS, _shown
        return len(_shown(SHELLS[shell]))
    return go


def _shell_fragments(shell: str):
    def go() -> int:
        from .test_a_shell_does_not_print_what_it_translated import SHELLS, _fragments
        return len(_fragments(SHELLS[shell]))
    return go


def _form_asked_for() -> int:
    from .test_a_form_that_asks_for_it_has_a_label_for_it import _asked_for
    return len(_asked_for())


# -- what each receiver declares --------------------------------------------
#
# `RECEIVERS` already carries a floor per receiver, and
# `test_the_scan_reads_every_receiver` uses it — for the *reached* count. The
# line above it floored the *declared* count at a blanket 5, for receivers
# holding between eight and one thousand two hundred and fifty-two members.
#
#     asked     did the scan read this receiver
#     mattered  did it read enough of it to be reading it at all
#
# The number was in the data the whole time; the tuple's own floor sits one
# line below, doing this job for the other half of the check. Two quantities,
# one of them measured per receiver and one of them guessed at once for all of
# them — which is the same defect as a value handed to a function that never
# reads it, and this estate has now found that shape four times in a day.


def _receiver_declared(label: str):
    def go() -> int:
        from . import test_the_member_that_isnt_there as m
        for row in m.RECEIVERS:
            if row[0] == label:
                return len(m._declared(row[1], m.REPO / row[2]))
        raise KeyError(f"no receiver labelled {label!r}")
    return go


# -- the guards on the guards -----------------------------------------------
#
# Every floor below stands under a docstring that says, in its own file's
# words, that a reader which stopped reading would report a clean result. Four
# of them carried the same literal in all three products, and three carried
# some version of the same sentence:
#
#     Thresholds are kept low enough to hold in all three repositories, which
#     have consoles of very different sizes.
#
# This file's header diagnosed that sentence once already, in
# `test_the_console_is_a_client_too.py` — a true sentence about why the number
# is small and a false one about what it holds. It was fixed there and never
# carried anywhere else. Twenty against this console's 342 bindings is six per
# cent; the identical twenty in QRME is three.
#
#     asked     does one number hold in all three products
#     mattered  does it hold anything in any of them
#
# Two more of these sat inside a loop, where one literal has to be
# four-fifths of three surfaces at once and settles for being four-fifths of
# none. Those are registered per surface.


def _console_bindings() -> int:
    from .test_a_binding_is_not_a_door import _bindings
    return len(_bindings())


def _api_functions(shell: str):
    def go() -> int:
        from .test_a_native_binding_is_not_a_door_either import _api_functions
        return len(_api_functions(shell))
    return go


def _path_segments() -> int:
    from .test_error_report_carries_nothing_private import _segments
    return len(_segments())


def _scanned_controls() -> int:
    from .test_a_form_that_asks_for_it_has_a_label_for_it import (
        _scanned_controls as go)
    return go()


def _egress_sites() -> int:
    from .test_nothing_leaves_the_host import _egress_sites
    return len(_egress_sites())


def _body_matched(slug: str):
    def go() -> int:
        from . import test_the_body_the_native_clients_send as m
        for client, short in m.SLUG.items():
            if short == slug:
                return m._writes_meeting_a_model(client)
        raise KeyError(f"no native client slugged {slug!r}")
    return go


def _template_calls() -> int:
    from .test_a_refusal_whose_english_is_not_a_constant import _template_calls
    return len(_template_calls())


# -- the floors the sweep was too coarse to see -----------------------------
#
# `SMALLEST_FLOOR` was five, so `assert n >= 2` never entered the backlog. The
# cutoff was right about most of what it hid: a two or a three is usually a
# shape check on a response body, not a floor on a scanned surface. It was
# wrong about these — and measuring them is what retired the cutoff, which the
# sweep now replaces with a question about the expression rather than the
# number.
#
#     asked     is this floor big enough to be worth auditing
#     mattered  is this floor smaller than what it stands over
#
# It filters on the number's size as a stand-in for the number's kind, and
# the stand-in fails in both directions — it would drag in fifty-two runtime
# assertions if it were lowered, and it hides a two standing over a hundred
# and twenty-seven.

def _requests_built(shell: str):
    def go() -> int:
        import re
        from . import test_the_language_nobody_was_sending as m
        for name, _, _, _, client, _ in m.SHELLS:
            if name == shell:
                return len(re.findall(m.BUILT[name], m._code(m.REPO / client)))
        raise KeyError(f"no shell named {shell!r}")
    return go


def _ratchet_files() -> int:
    from .test_a_record_that_outlived_the_code import _ratchets
    return len(_ratchets())


def _readme_files() -> int:
    from .test_readme_scripture import _readmes
    return len(_readmes())


def _verbs_min() -> int:
    """The fewest distinct verbs any one surface reports.

    A minimum rather than a total, because the assertion runs per surface: a
    floor on the sum would be satisfied by one surface reading well while
    another had gone silent.
    """
    from .test_client_routes_exist import CONSOLE, NATIVE, calls
    return min(len({method for method, _ in calls(lang)})
               for lang in (CONSOLE,) + NATIVE)


# -- the floors that were already holding ----------------------------------
#
# These are the other half of what widening the sweep turned up, and the half
# that is easy to leave alone: measured, in band, several at exactly the
# number they stand over. Nothing here is being corrected.
#
#     asked     is this floor wrong
#     mattered  is anything comparing it to what it measures
#
# A floor at 1.00 today is a floor at 0.30 in a year, and the run it starts
# being wrong on is a run nobody watches. What registering buys one that
# holds is not a different number — it is the measurement attached, and the
# audit every run. Each keeps the number it had unless four-fifths of what it
# measures is higher, because lowering a guard that currently holds tight, to
# satisfy a convention about where floors usually sit, is following the rule
# off a cliff.


def _workflow_files() -> int:
    from .test_a_check_that_cannot_fail_before_the_merge import _files
    return len(_files())


def _places_named() -> int:
    from .test_a_confident_wrong_diagnosis import _places_named
    return _places_named()


def _caller_total() -> int:
    from .test_a_derived_artifact_nothing_derives import _caller_total
    return _caller_total()


def _console_self_keys() -> int:
    from .test_a_shell_asks_for_a_key_it_has import _wanted
    return len(_wanted())


def _coach_live_regions() -> int:
    from .test_ability_is_not_a_gate import _live_regions
    return _live_regions("Coach.tsx")


def _degrading_wrappers() -> int:
    from .test_every_degrading_path_says_so import _degrading_wrappers
    return len(_degrading_wrappers())


def _writes_meeting_a_model() -> int:
    from .test_the_body_the_route_requires import _writes_meeting_a_model
    return _writes_meeting_a_model()


def _close_reasons() -> int:
    from .test_the_conversation_leaves_the_application import (
        _error_handler_body)
    return _error_handler_body().count("close(reason =")


def _gallery_tables() -> int:
    from .test_the_gallery_is_a_grid import _galleries
    return len(list(_galleries()))


def _echo_guards() -> int:
    from .test_the_guardian_does_not_answer_herself import SPEECH
    return SPEECH.count("echoOfTheGuardian(")


def _echo_reports() -> int:
    from .test_the_guardian_does_not_answer_herself import _echo_reports
    return len(_echo_reports())


def _exception_handlers() -> int:
    from .test_the_guardian_refuses_in_one_language import _handlers
    return len(_handlers())


def _build_steps() -> int:
    from .test_the_installer_can_actually_report import _build_steps
    return len(_build_steps())


def _console_request_headers() -> int:
    from .test_the_language_nobody_was_sending import _console_headers
    return len(_console_headers())


def _brushes(half: int):
    def go() -> int:
        from .test_the_member_that_isnt_there import _brushes
        return len(_brushes()[half])
    return go


def _thinnest_pin() -> int:
    from .test_the_shape_inside_the_shape import contract, _pin_rows
    return min(len(contract(*row)) for row in _pin_rows())


def _answer_pieces() -> int:
    from .test_the_answer_begins_before_it_ends import LONG_ANSWER, _pieces
    return len(_pieces(LONG_ANSWER)[0])


# -- the floors the parametrize hid -----------------------------------------
#
# Every one of these sat inside a `@pytest.mark.parametrize("shell", ...)`,
# which is the same defect as a literal under a loop wearing pytest's
# clothes: one number standing for three shells, calibrated for none of
# them, and invisible to the replay harness because the name `shell` only
# exists while pytest is running.
#
# The sharpest fossil: a docstring reading "QRME's Windows shell makes
# exactly two localizer calls — the nav loop and one button". It makes
# 1,278 now. The floor of 2 under it was two tenths of one per cent of the
# surface it claimed to hold, under a sentence that had been precisely true
# the day it was written.


def _screens_declared(shell: str):
    def go() -> int:
        from .test_a_screen_nothing_opens import _declared
        return len(_declared(shell))
    return go


def _screens_localizer_calls(shell: str):
    def go() -> int:
        from .test_a_screen_nothing_opens import _call_sites
        return len(_call_sites(shell))
    return go


def _problems_recorded(shell: str):
    def go() -> int:
        from .test_native_shells_record_nothing_private import _record_calls
        return len(_record_calls(shell))
    return go


def _tabs_onscreen(shell: str):
    def go() -> int:
        from .test_the_tabs_are_translated_and_the_screens_are_not import (
            _measure)
        english, calls = _measure(shell)
        return english + calls
    return go


def _tabs_localizer_calls(shell: str):
    def go() -> int:
        from .test_the_tabs_are_translated_and_the_screens_are_not import (
            _measure)
        return _measure(shell)[1]
    return go


def _tabs_table_rows(shell: str):
    def go() -> int:
        from .test_the_tabs_are_translated_and_the_screens_are_not import (
            _rows)
        return len(_rows(shell))
    return go


def _shared_with_console(shell: str):
    def go() -> int:
        from .test_the_desktop_and_the_phone_say_different_things import (
            _shared_with_console)
        return len(_shared_with_console(shell))
    return go


RATCHETS: tuple[Ratchet, ...] = (
    Ratchet("screens.declared.android", 8, _screens_declared("android"),
            "the screens android declares, as the navigation scan reads them"),
    Ratchet("screens.declared.ios", 15, _screens_declared("ios"),
            "the screens ios declares, as the navigation scan reads them"),
    Ratchet("screens.declared.windows", 11, _screens_declared("windows"),
            "the screens windows declares, as the navigation scan reads them"),
    Ratchet("screens.localizer_calls.android", 622, _screens_localizer_calls("android"),
            "the localizer call sites the android screen scan finds"),
    Ratchet("screens.localizer_calls.ios", 688, _screens_localizer_calls("ios"),
            "the localizer call sites the ios screen scan finds"),
    Ratchet("screens.localizer_calls.windows", 703, _screens_localizer_calls("windows"),
            "the localizer call sites the windows screen scan finds"),
    Ratchet("problems.recorded.android", 3, _problems_recorded("android"),
            "the failure kinds android's client records — the refusal and the never-reached case"),
    Ratchet("problems.recorded.ios", 4, _problems_recorded("ios"),
            "the failure kinds ios's client records — the refusal and the never-reached case"),
    Ratchet("problems.recorded.windows", 2, _problems_recorded("windows"),
            "the failure kinds windows's client records — the refusal and the never-reached case"),
    Ratchet("tabs.onscreen.android", 622, _tabs_onscreen("android"),
            "the on-screen strings the android extraction reads"),
    Ratchet("tabs.onscreen.ios", 689, _tabs_onscreen("ios"),
            "the on-screen strings the ios extraction reads"),
    Ratchet("tabs.onscreen.windows", 703, _tabs_onscreen("windows"),
            "the on-screen strings the windows extraction reads"),
    Ratchet("tabs.localizer_calls.android", 622, _tabs_localizer_calls("android"),
            "the localizer calls the android tabs scan finds"),
    Ratchet("tabs.localizer_calls.ios", 688, _tabs_localizer_calls("ios"),
            "the localizer calls the ios tabs scan finds"),
    Ratchet("tabs.localizer_calls.windows", 703, _tabs_localizer_calls("windows"),
            "the localizer calls the windows tabs scan finds"),
    Ratchet("tabs.table_rows.android", 692, _tabs_table_rows("android"),
            "the rows the android table parser reads"),
    Ratchet("tabs.table_rows.ios", 690, _tabs_table_rows("ios"),
            "the rows the ios table parser reads"),
    Ratchet("tabs.table_rows.windows", 672, _tabs_table_rows("windows"),
            "the rows the windows table parser reads"),
    Ratchet("table.shared_with_console.android", 443, _shared_with_console("android"),
            "the English strings android's table shares with the console"),
    Ratchet("table.shared_with_console.ios", 440, _shared_with_console("ios"),
            "the English strings ios's table shares with the console"),
    Ratchet("table.shared_with_console.windows", 440, _shared_with_console("windows"),
            "the English strings windows's table shares with the console"),
    Ratchet("workflow.files", 4, _workflow_files,
            "the workflow files the gating sweep reads"),
    Ratchet("refusal.places_named", 3, _places_named,
            "the known causes this refusal names"),
    Ratchet("deriver.call_sites", 4, _caller_total,
            "the calls to a deriver across the package"),
    Ratchet("console.self_keys", 22, _console_self_keys,
            "the `self.*` rows the console table declares"),
    Ratchet("console.coach_live_regions", 2, _coach_live_regions,
            "the regions on the coach screen that announce themselves"),
    Ratchet("degrading.wrappers", 2, _degrading_wrappers,
            "the wrappers that degrade quietly, as the walk finds them"),
    Ratchet("route.writes_meeting_a_model", 98, _writes_meeting_a_model,
            "the clients' writes whose verb and shape meet a model"),
    Ratchet("service.close_reasons", 3, _close_reasons,
            "the ways the listening service says why it stopped"),
    Ratchet("gallery.tables", 2, _gallery_tables,
            "the gallery tables the README carries"),
    Ratchet("speech.echo_guards", 3, _echo_guards,
            "the places the shell checks a heard line against the guardian"),
    Ratchet("speech.echo_reports", 2, _echo_reports,
            "the listening paths that report an echo rather than swallow it"),
    Ratchet("api.exception_handlers", 10, _exception_handlers,
            "the exception handlers `api.py` declares"),
    Ratchet("installer.build_steps", 3, _build_steps,
            "the steps that run the packaging command"),
    Ratchet("console.request_headers", 2, _console_request_headers,
            "the headers the console attaches to every request"),
    Ratchet("brush.keys", 16, _brushes(0),
            "the brush keys App.xaml declares"),
    Ratchet("brush.used", 10, _brushes(1),
            "the brush keys the screens actually paint with"),
    Ratchet("pin.thinnest", 2, _thinnest_pin,
            "the keys on the thinnest pinned contract"),
    Ratchet("speech.pieces_from_a_long_answer", 2, _answer_pieces,
            "the pieces a long answer splits into before it is spoken"),
    # Per shell, and the reason is in the numbers: this one literal stood
    # over 4, 7 and 127 requests built. It was honest about the
    # iPhone and decoration on the desktop, which is what a single floor
    # under a loop over three surfaces always ends up being.
    Ratchet("language.requests_built.ios", 3, _requests_built("ios"),
            "the requests the iPhone client builds"),
    Ratchet("language.requests_built.android", 5, _requests_built("android"),
            "the requests the Android client builds"),
    Ratchet("language.requests_built.windows", 101, _requests_built("windows"),
            "the requests the desktop client builds"),
    Ratchet("ratchet.files", 18, _ratchet_files,
            "the ratchet records this suite keeps"),
    Ratchet("route.verbs_min", 4, _verbs_min,
            "the distinct verbs the thinnest-reading surface reports"),
    Ratchet("readme.files", 5, _readme_files,
            "the READMEs the passage check reads"),
    Ratchet("console.bindings_scanned", 273, _console_bindings,
            "the bindings the console scan parses out of api.ts"),
    Ratchet("native.api_functions.ios", 270, _api_functions("ios"),
            "the calls the iPhone's ApiClient declares"),
    Ratchet("route.path_segments", 202, _path_segments,
            "the literal path segments this product's routes contribute"),
    Ratchet("form.controls_scanned", 13349, _scanned_controls,
            "the characters of form control the screen scan matches"),
    Ratchet("host.egress_sites", 13, _egress_sites,
            "the calls in this package that can put bytes on a wire"),
    Ratchet("native.body_matched.windows", 96, _body_matched("windows"),
            "the desktop client's writes that meet a declared model"),
    Ratchet("native.body_matched.ios", 95, _body_matched("ios"),
            "the iPhone client's writes that meet a declared model"),
    Ratchet("native.body_matched.android", 95, _body_matched("android"),
            "the Android client's writes that meet a declared model"),
    Ratchet("refusals.template_calls", 78, _template_calls,
            "the `i18n.fill` call sites the conversion left behind"),
    Ratchet("receiver.declared.ios.state", 12, _receiver_declared("ios/state"),
            "the members ios/state declares"),
    Ratchet("receiver.declared.ios.api", 879, _receiver_declared("ios/api"),
            "the members ios/api declares"),
    Ratchet("receiver.declared.ios.theme", 12, _receiver_declared("ios/theme"),
            "the members ios/theme declares"),
    Ratchet("receiver.declared.android.state", 13, _receiver_declared("android/state"),
            "the members android/state declares"),
    Ratchet("receiver.declared.android.api", 1001, _receiver_declared("android/api"),
            "the members android/api declares"),
    Ratchet("receiver.declared.android.theme", 14, _receiver_declared("android/theme"),
            "the members android/theme declares"),
    Ratchet("receiver.declared.windows.state", 11, _receiver_declared("windows/state"),
            "the members windows/state declares"),
    Ratchet("receiver.declared.windows.api", 489, _receiver_declared("windows/api"),
            "the members windows/api declares"),
    Ratchet("shell.shown.ios", 1162, _shell_shown("ios"),
            "the literals the iOS scan finds on any screen"),
    Ratchet("shell.shown.android", 871, _shell_shown("android"),
            "the literals the Android scan finds on any screen"),
    Ratchet("shell.shown.windows", 2641, _shell_shown("windows"),
            "the literals the Windows scan finds on any screen"),
    Ratchet("shell.fragments.ios", 58, _shell_fragments("ios"),
            "the fragments split out of the iOS table's slotted rows"),
    Ratchet("shell.fragments.android", 57, _shell_fragments("android"),
            "the fragments split out of the Android table's slotted rows"),
    Ratchet("shell.fragments.windows", 58, _shell_fragments("windows"),
            "the fragments split out of the Windows table's slotted rows"),
    Ratchet("form.asked_for", 20, _form_asked_for,
            "the request fields the form check knows a control for"),
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
