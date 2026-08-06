"""Two tables, one product, and nothing compared them.

## The finding

0.48.0 compared keys *inside* one table and found 54 English strings carried
by two or more keys on iOS, 43 of them already drifted. This round asks the
same question one level out.

The desktop console has its own table — `app/src/l10n.ts`, 1,882 rows — and
the three shells have theirs. **223 English strings live in both the console
table and the iOS table, and 102 of them had no translation the two tables
agreed on.** Android 104, Windows 103. A person who opens QRME on their laptop
and then on their phone is reading two different products in their own
language, and reading one product in English.

    asked     does each table say the same thing twice the same way
    mattered  do the tables say the same thing as each other

Fifty keys are *the same key in both tables*. Two of those disagreed:
`corner.send` (ar) and `plc.venues` (fr, *Espaces* on the desktop and *Lieux*
on the phone). Identical key, identical English, different word.

## The register

The largest systematic cause is not vocabulary. It is **who the product thinks
it is talking to.**

| German | Sie / Ihnen / Ihre | du / dein / dich |
|---|---|---|
| console | **204** | 32 |
| phone | 7 | **60** |

The desktop addresses a German reader formally and the phone informally. That
is not a synonym choice; in a language with a T–V distinction it is a claim
about the relationship, and this product made both claims at once — *Wo Sie
stehen* on the desktop and *Wo du stehst* on the phone, *Ihre
Signatur-Berechtigungen* against *Deine Signaturberechtigungen*.

Spanish is milder and mostly settled: 20 rows say *usted* against 47 that say
*tú* in the console, 2 against 13 on the phone. French and Portuguese are
formal on both sides; Italian informal on both.

This round moves every row it reconciles onto the phones' wording, which means
onto *du* and *tú*. The whole-table register sweep is recorded rather than
done: converting German T–V is not a pronoun substitution — *Wo Sie stehen*
becomes *Wo du stehst* — and this repo's rule against machine-mangling text a
person relies on applies to 204 rows as much as to fourteen.

## What 0.48.0 did to this number

Widened it. Reconciling the Desk and the Counter inside the native tables
picked *Theke* for the Desk, so that German would stop naming two tab-bar
entries *Schalter*. The console still said *Schalter*, and nothing compared
them, so a fix in one table opened a gap with a table no guard could see.

That is this arc's shape exactly, committed once more inside its own fix, and
it is the argument for this file: the previous round could not have known.

## The measurement was nearly the bug again

The first version of this check compared source bytes. JIM-mini's console
table writes some rows escaped — `"\\u7834\\u68c4\\u3059\\u308b"` — which in
TypeScript **is** 破棄する and renders correctly. Nine of that repo's
thirty-four "disagreements" were the same string spelled two ways, and this
guard would have shipped demanding they be "fixed".

    asked     are these two source strings identical
    mattered  do these two strings render the same

So `_decode` came first and the count came second: JIM's number fell from 34
to 25 before a line of the fix was written. `test_the_escape_decoder_reads_each_syntax`
exists so that a decoder that quietly stopped decoding cannot bring the false
number back.

## Why this file is in this repo too

The finding and the guard are the sibling product's; these are the same two
kinds of table written the same way. 61 English strings are held by both this
repo's console table and its iOS table, and 25 had no wording the two agreed
on — Android 27, Windows 27.

**Nine of those twenty-five were not real**, and finding that out is what
produced `_decode`. This repo's console table writes some rows escaped —
`"\\u7834\\u68c4\\u3059\\u308b"`, which in TypeScript *is* 破棄する — and a
comparison of source bytes calls that a disagreement. The count fell from 34
to 25 before any of it was fixed.

The bite here is the **alarm and safety surface**, the set this audit has
repeatedly named as the case where English is a hazard rather than a
discourtesy. On it, the desktop and the phone were not both English; they were
two different sentences in the reader's own language. *JIM demande : ça va ?*
against *JIM demande : est-ce que ça va ?*; **Cancel** rendered *Kündigen* on
the desktop — the German for terminating a contract — against *Abbrechen* on
the phone; *Medical ID* as *Identité médicale* against *Fiche médicale*, on the
card a responder reads.

## What this file checks

1. **the two tables agree** — per shell, matched exactly against
   `console_native_split.txt` in both directions;
2. **the total only shrinks** — against the record's `# ceiling:`;
3. **both tables still parse** — a floor and a probe row, because every false
   pass in this audit came from a pattern that stopped matching;
4. **the decoder still decodes** — on the case that produced the false count.
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
RECORD = Path(__file__).resolve().parent / "console_native_split.txt"

CONSOLE = REPO / "app" / "src" / "l10n.ts"
TABLES = {
    "ios": REPO / "native" / "ios" / "Sources" / "L10n.swift",
    "android": (REPO / "native" / "android" / "app" / "src" / "main" / "java"
                / "app" / "jim" / "guardian" / "L10n.kt"),
    "windows": REPO / "native" / "windows" / "L10n.cs",
}

LANGS = ["en", "es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar"]

#: Floors under each parse, and a probe row per table in all ten languages —
#: one probe cannot serve both when the two tables share no key, which is the
#: state a console table starts in. Per repo; nothing else in this file is.
FLOOR, CONSOLE_FLOOR = 240, 550
NATIVE_PROBE, CONSOLE_PROBE = "cont.title", "cont.title"

_STR = r'"((?:[^"\\]|\\.)*)"'
_NATIVE_HEAD = {
    "ios": re.compile(r'^\s*' + _STR + r'\s*:\s*\[', re.M),
    "android": re.compile(r'^\s*' + _STR + r'\s+to\s+mapOf\(', re.M),
    "windows": re.compile(r'^\s*\[' + _STR + r'\]\s*=\s*new\(\)\s*\{', re.M),
}
_NATIVE_PAIR = {
    "ios": re.compile(r'"(\w\w)"\s*:\s*' + _STR),
    "android": re.compile(r'"(\w\w)"\s+to\s+' + _STR),
    "windows": re.compile(r'\["(\w\w)"\]\s*=\s*' + _STR),
}
_CONSOLE_HEAD = re.compile(r'^\s*"([\w.]+)"\s*:\s*\{', re.M)
_CONSOLE_PAIR = re.compile(r'\b(\w\w)\s*:\s*' + _STR)

_SIMPLE = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\",
           "'": "'", "0": "\0"}


def _decode(text: str) -> str:
    """What the string renders as, not what its source bytes are.

    All four syntaxes here accept `\\uXXXX`, Swift also spells it `\\u{XXXX}`,
    and a table is free to write a row either way. Comparing the bytes counts
    a spelling difference as a wording difference — see the docstring.
    """
    out, i = [], 0
    while i < len(text):
        c = text[i]
        if c != "\\" or i + 1 >= len(text):
            out.append(c); i += 1; continue
        nxt = text[i + 1]
        if nxt == "u" and text[i + 2:i + 3] == "{":
            end = text.find("}", i + 3)
            if end != -1:
                try:
                    out.append(chr(int(text[i + 3:end], 16))); i = end + 1
                    continue
                except ValueError:
                    pass
        if nxt == "u" and re.match(r"[0-9a-fA-F]{4}", text[i + 2:i + 6]):
            out.append(chr(int(text[i + 2:i + 6], 16))); i += 6; continue
        if nxt in _SIMPLE:
            out.append(_SIMPLE[nxt]); i += 2; continue
        out.append(nxt); i += 2
    return "".join(out)


def _rows(text: str, head: re.Pattern, pair: re.Pattern) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    heads = list(head.finditer(text))
    for i, m in enumerate(heads):
        stop = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        langs: dict[str, str] = {}
        for p in pair.finditer(text[m.end():stop]):
            if p.group(1) in LANGS and p.group(1) not in langs:
                langs[p.group(1)] = _decode(p.group(2))
        if "en" in langs:
            out[m.group(1)] = langs
    return out


def _console() -> dict[str, dict[str, str]]:
    if not CONSOLE.exists():
        return {}
    return _rows(CONSOLE.read_text(encoding="utf-8"), _CONSOLE_HEAD, _CONSOLE_PAIR)


def _native(shell: str) -> dict[str, dict[str, str]]:
    return _rows(TABLES[shell].read_text(encoding="utf-8"),
                 _NATIVE_HEAD[shell], _NATIVE_PAIR[shell])


def _by_english(table: dict[str, dict[str, str]]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = defaultdict(list)
    for key, row in table.items():
        out[row["en"]].append(key)
    return out


def _split(shell: str) -> list[str]:
    """Record rows: English strings both tables hold on which no console row
    and no native row share a wording, in some language."""
    con, nat = _console(), _native(shell)
    cb, nb = _by_english(con), _by_english(nat)
    rows = []
    for english in sorted(set(cb) & set(nb)):
        for lang in LANGS[1:]:
            cvals = {con[k].get(lang) for k in cb[english]} - {None}
            nvals = {nat[k].get(lang) for k in nb[english]} - {None}
            if cvals and nvals and not (cvals & nvals):
                rows.append(f"{shell}: {','.join(sorted(cb[english]))} "
                            f":: {','.join(sorted(nb[english]))}")
                break
    return rows


def _measured() -> set[str]:
    return {row for shell in TABLES for row in _split(shell)}


def _recorded() -> set[str]:
    return {line.split("  (")[0].strip()
            for line in RECORD.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


def test_both_tables_still_parse():
    """A guard on the guard. A table read as empty shares no strings with
    anything and would report two tables in perfect agreement."""
    con = _console()
    assert len(con) > CONSOLE_FLOOR, (
        f"the console table parsed to {len(con)} rows, far below what "
        f"{CONSOLE.name} holds — the row pattern has stopped matching")
    assert con.get(CONSOLE_PROBE) and sorted(con[CONSOLE_PROBE]) == sorted(LANGS), (
        f"console: `{CONSOLE_PROBE}` did not parse into all ten languages")
    for shell in TABLES:
        nat = _native(shell)
        assert len(nat) > FLOOR, (
            f"{shell}'s table parsed to {len(nat)} rows, far below what it holds")
        assert nat.get(NATIVE_PROBE) and sorted(nat[NATIVE_PROBE]) == sorted(LANGS), (
            f"{shell}: `{NATIVE_PROBE}` did not parse into all ten languages")


def test_the_escape_decoder_reads_each_syntax():
    """The check this file nearly shipped without.

    `"\\u7834..."` in TypeScript is 破 — a spelling, not a wording. A decoder
    that stopped decoding would bring back the nine false disagreements it
    was written to remove, and every one of them would look like real work.
    """
    # Built from an explicit backslash rather than written as `r"破"`.
    # The first draft of this test was written with the escapes already
    # decoded — it asserted `_decode("破") == "破"`, which is true of any
    # function that returns its argument, and it passed with the decoder
    # switched off. This file's own subject, one level in.
    bs = chr(92)
    assert _decode(bs + "u7834" + bs + "u68c4" + bs + "u3059" + bs + "u308b") == "破棄する"
    assert _decode("Todav" + bs + "u00eda nada.") == "Todavía nada."
    assert _decode(bs + "u{0027}ok") == "'ok"       # Swift's braced form
    assert _decode("a" + bs + '"b') == 'a"b'
    assert _decode("plain") == "plain"
    assert _decode("A" + bs + "u0042C") == "ABC", (
        "a decoder that handles one escape and not the next is worse than "
        "one that handles none, because the count it produces looks sane")


def test_the_desktop_and_the_phone_say_the_same_thing():
    """The defect, directly, and in both directions."""
    measured, recorded = _measured(), _recorded()
    problems = []
    new = sorted(measured - recorded)
    if new:
        problems.append(
            f"{len(new)} English string(s) are in both the console table and "
            "a shell's, with no wording the two agree on, and are not in "
            "console_native_split.txt. The desktop and the phone say "
            "different things to the same reader:\n    "
            + "\n    ".join(new[:20]))
    stale = sorted(recorded - measured)
    if stale:
        problems.append(
            f"{len(stale)} recorded row(s) now agree — strike them from "
            "console_native_split.txt:\n    " + "\n    ".join(stale[:20]))
    assert not problems, "\n\n".join(problems)


def test_the_console_native_split_only_shrinks():
    text = RECORD.read_text(encoding="utf-8")
    ceiling = int(re.search(r"^# ceiling: (\d+)$", text, re.M).group(1))
    assert len(_measured()) <= ceiling, (
        f"{len(_measured())} split rows, above the {ceiling} recorded")


@pytest.mark.parametrize("shell", sorted(TABLES))
def test_the_two_tables_share_enough_to_be_worth_comparing(shell):
    """If the overlap collapsed, every check above would pass on nothing.

    The two tables are written independently and share around sixty
    English strings; a number far below that means the extraction changed,
    not that the product did.
    """
    shared = set(_by_english(_console())) & set(_by_english(_native(shell)))
    assert len(shared) > 40, (
        f"{shell}: only {len(shared)} English strings are held by both the "
        "console table and this shell's, which is too few to conclude "
        "anything from — check the parse before the product")
