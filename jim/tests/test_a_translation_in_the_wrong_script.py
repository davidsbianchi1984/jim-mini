"""A translated refusal that is not in the language it claims to be.

`refusals_untranslated.txt` counts the sentences that have **no** translation
yet, and it only shrinks. Nothing has ever looked at the ones that do. The
whole backlog can reach zero with a Chinese row written in Cyrillic in it, and
every guard in this estate would report the paydown as complete.

    asked     is every refusal translated
    mattered  is each translation in the language it is filed under

## Where this came from

Two of them, written by hand into `_REFUSALS` during a round and caught by
eye rather than by anything: the word `как` inside a Chinese string, and the
syllable `각` inside a Japanese one. Both were single characters in otherwise
correct sentences, both would have rendered, and neither would have failed a
test. They were noticed because somebody happened to read the diff.

A reader of that language sees a sentence with a word from another alphabet in
it, at the moment the product is telling them no. That is the worst moment to
look unreliable, and it is the reason the refusals were translated first.

## What this asks

Per language, the script the language is written in — and the two failure
modes that are not about script at all:

* a value **identical to the English key**, which is a row somebody added to
  make the count go up;
* a row that does not carry every language, which the backlog file cannot see
  because a row is either in it or not.

It is deliberately narrow. It cannot tell a good translation from a poor one,
and nothing here pretends to: it catches the class that got through twice,
which is *this is not that language at all*.

Byte-identical in QRME, JIM-mini and PDI, like `release_fields.txt` — the
defect is the estate's and so is the check.
"""

from __future__ import annotations

import importlib
import re

import pytest


def _i18n():
    """This product's `i18n`, whichever of the three this repository is."""
    for name in ("qrme", "jim", "pdi"):
        try:
            return importlib.import_module(f"{name}.i18n")
        except ModuleNotFoundError:
            continue
    raise RuntimeError("no i18n module found for this repository")


I18N = _i18n()
REFUSALS: dict[str, dict[str, str]] = getattr(I18N, "_REFUSALS", {})

#: The nine this estate translates into, beside English.
LANGUAGES = ("es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar")

_LATIN = re.compile(r"[A-Za-z]{4}")


def _in(text: str, lo: int, hi: int) -> bool:
    return any(lo <= ord(c) <= hi for c in text)


def _cyrillic(text: str) -> bool:
    return _in(text, 0x0400, 0x04FF)


def _hangul(text: str) -> bool:
    return _in(text, 0xAC00, 0xD7AF) or _in(text, 0x1100, 0x11FF)


def _kana(text: str) -> bool:
    return _in(text, 0x3040, 0x30FF)


def _han(text: str) -> bool:
    return _in(text, 0x4E00, 0x9FFF)


def _devanagari(text: str) -> bool:
    return _in(text, 0x0900, 0x097F)


def _arabic(text: str) -> bool:
    return _in(text, 0x0600, 0x06FF)


def test_there_are_refusals_to_check_at_all():
    """A guard on the guard: everything below passes on an empty table."""
    assert REFUSALS, "no _REFUSALS table found — these checks read nothing"


def test_every_row_carries_every_language():
    """The backlog file cannot see this.

    A row is either in `refusals_untranslated.txt` or not. One that is out of
    it because eight of its nine languages arrived reads as paid off.
    """
    short = {eng: sorted(set(LANGUAGES) - set(tr))
             for eng, tr in REFUSALS.items()
             if set(LANGUAGES) - set(tr)}
    assert not short, (
        "rows missing languages:\n    "
        + "\n    ".join(f"{eng[:60]!r} — no {', '.join(missing)}"
                        for eng, missing in list(short.items())[:10]))


def test_no_translation_is_the_english_again():
    same = [(eng, lang) for eng, tr in REFUSALS.items()
            for lang, text in tr.items()
            if text.strip() == eng.strip()]
    assert not same, (
        "these rows are filed as translated and are the English sentence:\n"
        "    " + "\n    ".join(f"{lang}: {eng[:60]!r}"
                               for eng, lang in same[:10]))


@pytest.mark.parametrize("lang", LANGUAGES)
def test_no_cyrillic_anywhere(lang):
    """The first of the two that got through: `как`, inside a Chinese row.

    None of the nine is written in Cyrillic, so a Cyrillic character anywhere
    in this table is a word that came from somewhere else.
    """
    bad = [eng for eng, tr in REFUSALS.items()
           if lang in tr and _cyrillic(tr[lang])]
    assert not bad, (
        f"{lang} rows carrying Cyrillic:\n    "
        + "\n    ".join(f"{eng[:50]!r} -> {REFUSALS[eng][lang][:50]!r}"
                        for eng in bad[:6]))


def test_japanese_is_not_written_in_hangul():
    """The second: `各` became `각` in a sentence that was otherwise correct."""
    bad = [eng for eng, tr in REFUSALS.items()
           if "ja" in tr and _hangul(tr["ja"])]
    assert not bad, (
        "Japanese rows carrying Hangul:\n    "
        + "\n    ".join(f"{eng[:50]!r} -> {REFUSALS[eng]['ja'][:50]!r}"
                        for eng in bad[:6]))


def test_chinese_is_not_written_in_kana_or_hangul():
    bad = [eng for eng, tr in REFUSALS.items()
           if "zh" in tr and (_kana(tr["zh"]) or _hangul(tr["zh"]))]
    assert not bad, (
        "Chinese rows carrying kana or Hangul:\n    "
        + "\n    ".join(f"{eng[:50]!r} -> {REFUSALS[eng]['zh'][:50]!r}"
                        for eng in bad[:6]))


@pytest.mark.parametrize("lang,script,name", [
    ("hi", _devanagari, "Devanagari"),
    ("ar", _arabic, "Arabic"),
])
def test_a_row_is_written_in_its_own_script(lang, script, name):
    """Hindi and Arabic are the two where a missed row is unmistakable.

    A Latin run of four or more with none of the language's own script in the
    sentence is somebody's English or a placeholder, not a translation. Short
    Latin runs are left alone: a product name, a header, `QRME_ADMIN_TOKEN` —
    the same reasoning `refusals_untranslated.txt` uses to keep those in
    English on purpose.
    """
    bad = [eng for eng, tr in REFUSALS.items()
           if lang in tr and not script(tr[lang]) and _LATIN.search(tr[lang])]
    assert not bad, (
        f"{lang} rows with no {name} in them:\n    "
        + "\n    ".join(f"{eng[:50]!r} -> {REFUSALS[eng][lang][:50]!r}"
                        for eng in bad[:6]))


@pytest.mark.parametrize("lang", ["ja", "zh"])
def test_a_cjk_row_is_not_a_latin_sentence(lang):
    bad = [eng for eng, tr in REFUSALS.items()
           if lang in tr and not (_han(tr[lang]) or _kana(tr[lang]))
           and _LATIN.search(tr[lang])]
    assert not bad, (
        f"{lang} rows with no CJK in them:\n    "
        + "\n    ".join(f"{eng[:50]!r} -> {REFUSALS[eng][lang][:50]!r}"
                        for eng in bad[:6]))
