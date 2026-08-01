"""The refusals that could not be keyed, and the slot that could ruin them.

`tests/refusals_untranslated.txt` has carried this for three releases:
f-string refusals, named as uncovered and deliberately not counted, because

    f"language must be one of {', '.join(SUPPORTED)}"

cannot be looked up by its English source — at the moment it is raised there is
no English source, only a result.

    asked     is the refusal a constant we can translate
    mattered  is every part of it something we can translate

`i18n.Templated` carries the template and its slots alongside the finished
English sentence, so `localize_detail` can refill the frame in the reader's
language. It is a `str`, and its value is that English sentence, so nothing
that already treats a detail as text needed to change.

## The slot is the whole design

A translated frame around an English slot is *worse* than an English sentence:
it reads as a bug, in front of somebody who is already being told no. So a slot
holding whitespace — prose, in any language — sets `translatable = False` and
the whole refusal stays English, which is the state it was already in, now
chosen rather than stumbled into.

The known limit: a *single* English word has no whitespace either. QRME's copy
of this mechanism carries a `Term` marker and a translated vocabulary for the
closed sets its refusals interpolate; JIM-mini has no refusal that
interpolates one, and `test_no_slot_is_filled_from_a_string_literal` fails if
that stops being true.

## What this file does not claim

7 sites are converted. 8 f-string refusals remain, and the
record now names the reason per site rather than "f-string".
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from jim import i18n


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
PACKAGE = REPO / "jim"


def test_a_templated_refusal_is_its_own_english_sentence():
    """The property everything else rests on. If this stopped being true,
    every driven test asserting on a refusal message, and the default English
    path itself, would be reading an object repr."""
    said = i18n.fill(i18n.MUST_BE_ONE_OF, field="language", choices="en, es")
    assert isinstance(said, str)
    assert said == "language must be one of en, es"


@pytest.mark.parametrize("language", ["pt", "es", "de", "ja", "ar"])
def test_the_frame_arrives_translated_and_the_slot_survives(language):
    said = i18n.fill(i18n.MUST_BE_ONE_OF, field="language",
                     choices=", ".join(i18n.SUPPORTED))
    out = i18n.localize_detail(said, language)
    assert out != str(said), f"the frame stayed English for {language}: {out}"
    assert ", ".join(i18n.SUPPORTED) in out, (
        f"the slot was lost in translation: {out}")


def test_every_template_is_translated_into_every_language():
    missing = []
    for template in i18n.TEMPLATES:
        table = i18n._TEMPLATES.get(template, {})
        for code in i18n.SUPPORTED:
            if code != i18n.DEFAULT and code not in table:
                missing.append(f"{template!r} has no {code}")
    assert not missing, "\n    ".join(missing)


def test_a_translation_keeps_every_slot_the_template_has():
    """A frame missing `{choices}` renders a sentence with the list silently
    dropped — grammatical, translated, and wrong."""
    problems = []
    for template in i18n.TEMPLATES:
        wanted = set(re.findall(r"\{(\w+)\}", template))
        for code, text in i18n._TEMPLATES[template].items():
            got = set(re.findall(r"\{(\w+)\}", text))
            if got != wanted:
                problems.append(f"{code} of {template!r}: has {sorted(got)}, "
                                f"template has {sorted(wanted)}")
    assert not problems, "\n    ".join(problems)


@pytest.mark.parametrize("value", [
    "en, es, fr", "openai", "usr_9f2c", "12.00", "pre, on_demand", "",
])
def test_a_token_slot_is_translatable(value):
    said = i18n.fill(i18n.MUST_BE_ONE_OF, field="x", choices=value)
    assert said.translatable, f"{value!r} was refused and should not have been"


@pytest.mark.parametrize("value", [
    "in development",
    "the mail server refused the connection",
    "a name somebody typed",
])
def test_a_prose_slot_makes_the_whole_refusal_stay_english(value):
    """The safety valve, and the reason this mechanism is safe to use widely.

    Not an exception and not a partial translation: the English sentence,
    whole, which is what the reader would have got anyway.
    """
    said = i18n.fill(i18n.MUST_BE_ONE_OF, field="x", choices=value)
    assert not said.translatable, f"{value!r} was accepted as a token"
    assert i18n.localize_detail(said, "pt") == str(said), (
        "a prose slot reached a translated frame — the sentence is now half in "
        "one language and half in another")


def _template_calls() -> list[tuple[str, int, dict]]:
    found = []
    for path in sorted(PACKAGE.rglob("*.py")):
        # This product keeps its tests inside the package, so the scan would
        # otherwise read this file's own examples as raise sites.
        if "tests" in path.parts:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if not isinstance(node, ast.Call):
                continue
            if getattr(node.func, "attr", "") != "fill":
                continue
            found.append((str(path.relative_to(REPO)), node.lineno,
                          {kw.arg: ast.unparse(kw.value)
                           for kw in node.keywords if kw.arg}))
    return found


def test_the_raise_sites_were_actually_converted():
    """A guard on the guard: everything below passes vacuously on no calls."""
    calls = _template_calls()
    assert len(calls) >= 6, (
        f"only {len(calls)} `i18n.fill` call(s) found — either the conversion "
        "was reverted or this extraction has stopped matching")


def test_no_slot_is_filled_from_a_string_literal():
    """The hole the whitespace rule cannot close, closed here instead.

    The rule sees values, and a single English word looks exactly like an
    identifier. What it cannot see is *where the value came from*. A slot
    filled from a variable, an attribute or a `join` is data; a slot filled
    from a literal is a word somebody typed into this codebase.

    `field` is the deliberate exception: it names the field being validated,
    which is the API's own name for it and the same in every language.
    """
    offenders = []
    for path, line, slots in _template_calls():
        for name, expression in slots.items():
            if name == "field":
                continue
            if re.fullmatch(r"""['"].*['"]""", expression, re.S):
                offenders.append(f"{path}:{line} {name}={expression}")
    assert not offenders, (
        "a slot is filled from a string literal, which the whitespace rule "
        "cannot tell from an identifier:\n    " + "\n    ".join(offenders))


def test_the_english_default_is_untouched():
    """Every driven test in this suite reads English refusals. The mechanism
    must be invisible when the reader's language is the default."""
    said = i18n.fill(i18n.MUST_BE_ONE_OF, field="mode",
                     choices=", ".join(i18n.MODES))
    assert i18n.localize_detail(said, i18n.DEFAULT) == said
