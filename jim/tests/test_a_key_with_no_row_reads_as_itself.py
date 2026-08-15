"""The tab said `nav.presence`, in Latin letters, in every language.

Found on a phone, between Community and Feed, by somebody looking at the
navigation strip for another reason entirely. `t()` falls back to the key
when the table has no row, so a lookup with nothing behind it renders its
own name — and has done since the screen shipped.

    asked     does every key in the table reach a screen
    mattered  does every key a screen asks for exist

The guard next door — `test_no_key_is_translated_into_ten_languages_and_used
_nowhere` — has been hunting the opposite failure for releases, and it is
elaborate about it: three escapes, each added after a narrow version called
live rows dead. Nothing looked the other way. A table can be complete in
every language and still be missing the row a screen actually asks for, and
that failure is the visible one: a dead key wastes a translation nobody
reads, while a missing row puts an identifier on screen in front of a
person.

One tab of twenty-four. The other twenty-three were fine, which is exactly
why nobody noticed — a strip of real words with a single key in it reads as
a typo rather than as a class of bug.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from .ratchets import floor

SRC = Path(__file__).resolve().parents[2] / "app" / "src"


def _table() -> set[str]:
    return set(re.findall(r'^  "([\w.]+)":',
                          (SRC / "l10n.ts").read_text("utf-8"), re.M))


def _tab_ids() -> list[str]:
    """The navigation's own list, read where it is declared.

    Deliberately the `{ id: … }` rows rather than the `Tab` union above them:
    the union is a type and the rows are what renders, and it was the rows
    that grew a member the table never got.
    """
    return re.findall(r'\{\s*id:\s*"(\w+)"',
                      (SRC / "App.tsx").read_text("utf-8"))


def test_the_tab_scan_is_finding_tabs():
    """A guard on the guard: a walk that stopped matching would report every
    tab labelled by finding none of them."""
    assert len(_tab_ids()) >= floor("console.nav_tabs"), (
        f"only {len(_tab_ids())} tab(s) parsed — this console has more, and "
        "the check below would pass on almost nothing")


def test_every_tab_has_a_label():
    """The defect, directly. A tab with no row is an identifier in the
    navigation, in all ten languages at once."""
    table = _table()
    bare = [f"nav.{i}" for i in _tab_ids() if f"nav.{i}" not in table]
    assert not bare, (
        f"{len(bare)} tab(s) render their own key as their label:\n    "
        + "\n    ".join(bare)
        + "\n  `t()` falls back to the key, so this shows in every language.")


def test_no_literal_lookup_is_missing_its_row():
    """The general case, of which the tab was one instance.

    Only literal keys — `t("a.b", lang)` — because a composed key cannot be
    resolved without running the app, and a check that guessed at those
    would fail on working code. The literal ones are most of them and were
    enough to have caught this.

    The comma at the end of the pattern is what makes "literal" mean it. The
    same check ported to PDI found six keys missing that were not keys at
    all: that console builds some of its lookups by concatenation —
    `t("pos.cap." + k, lang)` — and a pattern stopping at the closing quote
    read `pos.cap.` as a key in its own right. A guard against identifiers on
    screen that would have had somebody add six rows nothing reads.
    """
    table, asked = _table(), set()
    for f in list(SRC.rglob("*.tsx")) + list(SRC.rglob("*.ts")):
        if f.name == "l10n.ts":
            continue
        asked |= set(re.findall(r'\b(?:t|tr|L)\(\s*"([\w.]+)"\s*,',
                                f.read_text(encoding="utf-8")))
    missing = sorted(asked - table)
    assert not missing, (
        f"{len(missing)} key(s) are looked up and have no row:\n    "
        + "\n    ".join(missing)
        + "\n  Each renders as its own name on screen, in every language.")


# --------------------------------------------------------------------------- #
# The same failure, one level down: a value rather than a key
# --------------------------------------------------------------------------- #
#
# The tab above was a *key* with no row. Reported the same afternoon, from the
# same phone, was its sibling — a *value* with no row: the "Where I speak"
# picker drew nine buttons reading `earbuds`, `phone_screen`, `desktop_screen`,
# `ar`, straight off the wire.
#
#     asked     is every key a screen writes down present
#     mattered  is every value a screen renders a word
#
# The check above cannot see this one. `t("nav.presence", lang)` spells its key
# out and can be read from the file; `word("surface", s.surface, lang)` does
# not, and cannot — the tail arrives at runtime from a table that lives in
# Python. So the authority has to be that Python table, read here directly.
# Both halves of the failure were the same shape and only one of them was
# spellable, which is why the first guard shipped and the picker stayed raw.

PRESENCE = Path(__file__).resolve().parents[1] / "presence.py"


def _python_enum(name: str) -> list[str]:
    """The members of a top-level enum in `presence.py` — dict keys or tuple.

    Parsed rather than imported, and parsed rather than pattern-matched. Not
    imported because a guard that imports the module it checks inherits that
    module's import graph, and a table of nine strings is not worth standing a
    database up for. Not pattern-matched because the first version of this was
    a regex over the same text, and it read `SURFACES`' *inner* keys —
    `audio`, `visual`, `private`, `note` — as surfaces, then demanded rows for
    them. A guard that invents four members is no better than one that misses
    nine.
    """
    tree = ast.parse(PRESENCE.read_text(encoding="utf-8"))
    for node in tree.body:
        targets = getattr(node, "targets", []) or [getattr(node, "target", None)]
        if not any(isinstance(t, ast.Name) and t.id == name for t in targets
                   if t is not None):
            continue
        value = node.value
        members = value.keys if isinstance(value, ast.Dict) else value.elts
        return [m.value for m in members if isinstance(m, ast.Constant)]
    raise AssertionError(f"{name} is no longer declared in presence.py")


def test_the_enum_scan_is_finding_enums():
    """A guard on the guard, again: a walk that stopped matching would report
    every value labelled by finding none of them."""
    assert len(_python_enum("SURFACES")) >= floor("presence.surfaces")
    assert len(_python_enum("AREAS")) == 6


def test_every_surface_has_a_word_and_a_note():
    """The defect, directly. Nine buttons a person picks between, labelled
    with the identifiers the database stores."""
    table = _table()
    bare = [f"surface.{s}" for s in _python_enum("SURFACES")
            if f"surface.{s}" not in table]
    bare += [f"surface.{s}.note" for s in _python_enum("SURFACES")
             if f"surface.{s}.note" not in table]
    assert not bare, (
        f"{len(bare)} row(s) missing for surfaces the server offers:\n    "
        + "\n    ".join(sorted(bare))
        + "\n  Each renders as the wire's own name on a button somebody is "
          "being asked to choose between.")


def test_every_area_has_a_word():
    """The baseline card, beside the picker, doing the same thing — with the
    underscore swapped for a space, which is English in a thin disguise."""
    table = _table()
    bare = [f"area.{a}" for a in _python_enum("AREAS")
            if f"area.{a}" not in table]
    assert not bare, (
        f"{len(bare)} area(s) render as their own identifier:\n    "
        + "\n    ".join(sorted(bare)))


def test_the_fallback_is_the_value_and_not_the_key():
    """`word()` exists because `t()`'s fallback is wrong for wire values.

    A server one release ahead of a console will send a surface this build has
    never heard of. Falling back to `surface.holodeck` would put a key on the
    button; falling back to `holodeck` puts the thing itself there. The rows
    above are what keep the nine we do know from ever taking that path — the
    fallback is for a server ahead of us, not for a build that forgot.
    """
    src = (SRC / "l10n.ts").read_text(encoding="utf-8")
    body = src[src.index("export function word"):]
    body = body[:body.index("\n}")]
    assert 'replace(/_/g, " ")' in body, (
        "word() no longer opens the underscores out, so an unknown surface "
        "renders as `desktop_screen` rather than `desktop screen`")
    assert "prefix" in body and "key in TABLE" in body, (
        "word() no longer prefers the table, which is the whole of it")
