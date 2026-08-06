"""One English sentence, two keys, and the two copies no longer agree.

## The finding

Three releases of this arc have been about the same thing: the measurement was
reading one shape and calling the rest finished. 0.47.9 ended by correcting
what a number *meant* — 263 of the 335 rows in `native_dead_keys.txt` are not
waste but cross-shell asymmetry, a row one shell holds and another shell's
screen has not been built to use yet.

This round asks the next question about those 263, and the answer is worse
than asymmetry. **Sixty of them are a sentence the shell already says under a
different key.** `nc.find` is dead on the iPhone and on Android; the Windows
shell uses it for the Community screen's join button. The iPhone has that same
button and calls it `nc.match.find`. Same screen, same button, two rows, two
translations:

| | Windows (`nc.find`) | iPhone (`nc.match.find`) |
|---|---|---|
| es | Buscar una coincidencia | Buscar a alguien |
| fr | Trouver une mise en relation | Trouver un binôme |
| de | Eine Verbindung suchen | Gegenüber finden |

An English reader sees one product. A Spanish reader sees a different button
on the phone than on the desktop, for the same press.

Counted across the whole table rather than only the dead rows, QRME carries 54
English strings under two or more keys on iOS, 55 on Android and 60 on
Windows — around 215 redundant rows, which is 2,150 translations maintained
twice. **In forty-three of the fifty-four iOS sets the copies have already
drifted.** Redundancy is not the defect. Drift is: redundancy only means
somebody will have to do the work twice, while drift means it has already been
done twice and come out differently, and a reader is looking at the difference.

    asked     is every string on the screen translated
    mattered  does the product say the same thing twice the same way

## A duplicate is a question, not a defect

This guard deliberately does not ban duplicates, and it does not demand that
every duplicate be reconciled. Three different things produce one English
string under two keys, and only the last is a bug:

1. **English hides the gender.** `ava.show`, `cam.show`, `lend.show`,
   `org.show` and `work.show` all read *Show it*. Spanish has to choose
   *Mostrarlo* or *Mostrarla* depending on what *it* is — an avatar, a camera,
   a loan, an organization, a workshop. Five rows is the correct number of
   rows. Collapsing them would be a regression that the English cannot see.

2. **One English word is two words.** `counter.trade` is a *trade* as in a
   craft — *Oficio*, *Métier*, *Gewerk*, 手艺. `tab.trade` is trade as in
   commerce — *Comercio*, *Négoce*, 交易. The translations are right and the
   English is wrong: one word doing two jobs. Recorded by name, because the
   fix is to change the English, which changes what is on the screen.

3. **The same thing said two ways for no reason.** *Refresh* is
   *ताज़ा करें* on two screens and *रीफ़्रेश* on a third. *Send* is *إرسال*
   under two keys and *أرسل* under three. Nobody decided this. **This is the
   defect**, and 0.48.0 reconciles it.

So the record below holds rows, not a bare count, and each row can be read and
argued with. The ratchet is on the total, in the direction that matters: the
number of split wordings may not rise.

## The two tabs with the same name

The measurement turned up one thing nobody was looking for. `tab.counter` and
`tab.desk` are two different entries in the same tab bar — the Counter and the
Desk — and in Spanish both read *Mostrador*, in French both *Comptoir*, in
Portuguese both *Balcão*. Three languages in which this product's own tab bar
names two destinations identically. The Manage screen's mirror of those tabs
had it right (`nmg.t.counter` is *Ventanilla* / *Guichet* / *Guichê*), which is
how it was found: by asking why the two copies disagreed.

## Where the duplicates came from

Some of them came from this audit. 0.47.6 wired 91 Android sites that Compose
had hidden from the extractor, and did it by inserting new rows — `nmg.t.desk`,
`nmg.t.gaming`, `nmg.t.sign` — beside `tab.desk`, `tab.gaming` and `nsig.sign`,
which already held those words. 0.47.7 hit a key collision on
`nmg.filter.industry` and renamed its way around it to `nmg.f.industry`
instead of reconciling the two rows. Both are in the record below under my own
hand. The rule this round adds is the one that would have stopped them: before
inserting a row, look for the sentence.

## Why this file is in this repo too

The finding and the guard are the sibling product's; the surfaces are the same
three shells written the same way, and a blind spot in one copy of a guard is a
blind spot in all three by construction. This repo's tables are a quarter the
size and held six duplicate sets, **all six of them drifted** — a worse rate
than QRME's 43-in-54, which only looks small because the denominator is.

Two are worth naming here. `tab.monitor` and `mon` both read *Live Monitoring*
in English, and in nine of the ten languages the tab dropped the word *live*:
*Monitoreo*, *Surveillance*, *Überwachung*. A health guardian's tab bar naming
its monitoring surface without saying it was live, everywhere but English. And
`med.name` labelled a medication with 姓名 — the Chinese for a person's full
name — while `habit.name`, the same English word one screen over, had 名称. The
disagreement is what pointed at it.

## What this file checks

1. **no new split wordings** — the measured set matches `native_split_wordings.txt`
   exactly, in both directions: a new one fails, and one that has been
   reconciled must be struck from the record rather than left to rot;
2. **the total only shrinks** — against the `# ceiling:` the record carries;
3. **the extraction still reads the tables** — every false pass in this audit
   came from a pattern that quietly stopped matching, so the parse is checked
   against a known row before anything is concluded from it;
4. **no unbraced unicode escape in the Swift table** — see below.

## The thing found by asking why two copies differed

`people.say` and `party.say` both read *Say something*. Their Italian differed,
so the measurement printed both, and one of them was:

    "it": "Di\\u0027 qualcosa"

A literal `\\u0027` — the JSON escape for an apostrophe — sitting in a Swift
string literal, where the escape is `\\u{0027}` and `\\u0027` is not a valid
escape sequence at all. `L10n.swift` does not compile. There is no Swift
toolchain in this repo's CI, so nothing has said so; the Android and Windows
tables carry the same row correctly. It reached the file through some
long-forgotten JSON round-trip, and it was found by comparing a sentence with
its own twin.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

import pytest


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
RECORD = Path(__file__).resolve().parent / "native_split_wordings.txt"

#: Each shell's table. Same three files the rest of this audit reads.
TABLES = {
    "ios": REPO / "native" / "ios" / "Sources" / "L10n.swift",
    "android": (REPO / "native" / "android" / "app" / "src" / "main" / "java"
                / "app" / "jim" / "guardian" / "L10n.kt"),
    "windows": REPO / "native" / "windows" / "L10n.cs",
}

LANGS = ["en", "es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar"]

#: A floor under the parse, and a row every shell in this repo holds. The two
#: together are what stops a pattern that has stopped matching from reporting a
#: table in perfect agreement. Both change per repo; nothing else here does.
FLOOR, PROBE = 240, "alarm.not_emergency"

#: A double-quoted literal with escapes left intact — `\\"` must not end it.
_STR = r'"((?:[^"\\]|\\.)*)"'

#: The head of a row, in each of the three syntaxes the tables are written in.
_HEAD = {
    "ios": re.compile(r'^\s*' + _STR + r'\s*:\s*\['),
    "android": re.compile(r'^\s*' + _STR + r'\s+to\s+mapOf\('),
    "windows": re.compile(r'^\s*\[' + _STR + r'\]\s*=\s*new\(\)\s*\{'),
}

#: One language inside a row.
_PAIR = {
    "ios": re.compile(r'"(\w\w)"\s*:\s*' + _STR),
    "android": re.compile(r'"(\w\w)"\s+to\s+' + _STR),
    "windows": re.compile(r'\["(\w\w)"\]\s*=\s*' + _STR),
}


def _table(shell: str) -> dict[str, dict[str, str]]:
    """`{key: {lang: text}}` for one shell.

    Rows are one line each in all three tables, but a row is read as a window
    of lines rather than a single one: a table that is ever reformatted should
    make this guard wrong-and-loud, not silently empty.
    """
    lines = TABLES[shell].read_text(encoding="utf-8").splitlines()
    out: dict[str, dict[str, str]] = {}
    for i, line in enumerate(lines):
        head = _HEAD[shell].match(line)
        if not head:
            continue
        langs: dict[str, str] = {}
        for m in _PAIR[shell].finditer("\n".join(lines[i:i + 14])):
            code, value = m.group(1), m.group(2)
            if code in LANGS and code not in langs:
                langs[code] = value
        if "en" in langs:
            out[head.group(1)] = langs
    return out


def _by_english(table: dict[str, dict[str, str]]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = defaultdict(list)
    for key, row in table.items():
        out[row["en"]].append(key)
    return out


def _disagrees(table: dict[str, dict[str, str]], keys: list[str]) -> bool:
    """Do these keys' rows say different things in any of the nine?"""
    return any(len({table[k].get(lang) for k in keys}) > 1 for lang in LANGS[1:])


def _split(shell: str) -> dict[str, list[str]]:
    """`{English: keys}` for the English strings carried by two or more keys
    whose translations do not all agree."""
    table = _table(shell)
    return {english: sorted(keys)
            for english, keys in _by_english(table).items()
            if len(keys) > 1 and _disagrees(table, keys)}


def _measured() -> set[str]:
    return {f"{shell}: {' '.join(keys)}"
            for shell in TABLES
            for keys in _split(shell).values()}


def _recorded() -> set[str]:
    return {line.split("  (")[0].strip()
            for line in RECORD.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


def test_the_tables_still_parse():
    """A guard on the guard. Every false pass in this audit came from a
    pattern that stopped matching; a table read as empty holds no duplicates
    and no drift, and would report perfect agreement."""
    for shell in TABLES:
        table = _table(shell)
        assert len(table) > FLOOR, (
            f"{shell}'s table parsed to {len(table)} rows, which is far below "
            "what it holds — the row pattern has stopped matching and every "
            "check below is passing on nothing")
        row = table.get(PROBE)
        assert row and sorted(row) == sorted(LANGS), (
            f"{shell}: `{PROBE}` did not parse into all ten languages "
            f"({sorted(row or [])}) — the per-language pattern has drifted")


def test_no_english_sentence_is_translated_two_different_ways():
    """The defect, directly, and in both directions.

    Exact equality rather than a ceiling: a row that has been reconciled must
    leave the record. `test_a_record_that_outlived_the_code.py` exists because
    a record that keeps its cleared entries stops being read.
    """
    measured, recorded = _measured(), _recorded()
    problems = []
    new = sorted(measured - recorded)
    if new:
        problems.append(
            f"{len(new)} English string(s) are carried by two keys whose "
            "translations disagree and are not in native_split_wordings.txt. "
            "A reader of that language sees two different words for one "
            "thing:\n    " + "\n    ".join(new[:20]))
    stale = sorted(recorded - measured)
    if stale:
        problems.append(
            f"{len(stale)} recorded row(s) no longer disagree — strike them "
            "from native_split_wordings.txt:\n    " + "\n    ".join(stale[:20]))
    assert not problems, "\n\n".join(problems)


def test_the_split_wording_backlog_only_shrinks():
    text = RECORD.read_text(encoding="utf-8")
    ceiling = int(re.search(r"^# ceiling: (\d+)$", text, re.M).group(1))
    assert len(_measured()) <= ceiling, (
        f"{len(_measured())} split wordings, above the {ceiling} recorded")


def test_the_swift_table_has_no_unbraced_unicode_escape():
    """Swift writes a code point as `\\u{0027}`. `\\u0027` is not an escape
    sequence in Swift at all — it is a compile error, and one was sitting in
    `people.say`'s Italian until its twin `party.say` was put beside it."""
    bad = [line for line in TABLES["ios"].read_text(encoding="utf-8").splitlines()
           if re.search(r"\\u[0-9a-fA-F]{4}", line)]
    assert not bad, (
        f"{len(bad)} line(s) in L10n.swift carry a `\\uXXXX` escape. Swift "
        "spells a code point `\\u{XXXX}`; the unbraced form does not compile, "
        "and no Swift toolchain runs here to say so:\n    "
        + "\n    ".join(b.strip()[:120] for b in bad[:5]))


def test_the_comparison_can_tell_agreement_from_drift():
    """A guard on the guard, on a table small enough to read.

    The check above concludes something from `_disagrees` returning False, and
    a comparison that had quietly stopped looking at anything would return
    False for every pair in the repo and report nine perfect tables. So it is
    exercised here on rows whose answer is known by inspection: two that agree,
    two that differ in one language, and two that differ only in the language
    nobody would think to put last.
    """
    same = {lang: "x" for lang in LANGS}
    made = {
        "a": dict(same),
        "b": dict(same),
        "c": dict(same, es="y"),
        "d": dict(same, ar="y"),
    }
    assert not _disagrees(made, ["a", "b"])
    assert _disagrees(made, ["a", "c"])
    assert _disagrees(made, ["a", "d"]), (
        "the last language in the list is not being compared — a loop that "
        "stops one short passes every check in this file")
    assert set(_by_english(made)) == {"x"}


@pytest.mark.parametrize("shell", sorted(TABLES))
def test_a_duplicate_that_agrees_is_not_recorded_as_a_split(shell):
    """The record is about disagreement, not duplication. Rows that say the
    same thing under two keys are left out on purpose — see the docstring's
    first two cases, where more than one row is the correct number of rows."""
    table = _table(shell)
    by_english = _by_english(table)
    recorded = {r.split(": ", 1)[1] for r in _recorded()
                if r.startswith(shell + ": ")}
    for english, keys in by_english.items():
        if len(keys) > 1 and not _disagrees(table, keys):
            assert " ".join(sorted(keys)) not in recorded, (
                f"{shell}: {english!r} agrees in all ten languages and is "
                "still recorded as a split wording")
