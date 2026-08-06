"""The third axis: the three shells' tables against each other.

## Where this came from

0.48.0 compared keys *inside* one table. 0.48.1 compared the console's table
with each shell's. Both rounds ended by naming the same gap: two rows could not
be reconciled because **the three native tables disagreed with each other**, so
there was no single native wording for the console to adopt. Neither round
could fix them, because nothing had ever compared the shells.

    asked     does each table agree with itself, and with the console
    mattered  do the three shells agree with each other

This file closes that. It is the third and last of the three axes, and the
honest result is that it was nearly closed already:

| | same key, 2+ shells | disagreeing | same English, all three | with no shared wording |
|---|---|---|---|---|
| QRME | 1056 | **1** | 972 | **1** |
| JIM-mini | 261 | 0 | 204 | **3** |
| PDI | 51 | 0 | 47 | 0 |

Four rows across three products. Recording that plainly matters more than the
size of it: the previous two rounds each pointed at this axis as the next
large thing, and it is not large. A guard that had been written on the
assumption it would be would have been built to find much more than exists.

## The four

* **`action.sign_out`, Portuguese.** The phones said *Sair*; the Windows shell
  said *Terminar sessão*. *Sair* is *leave* or *exit*; ending a session in
  pt-PT is *terminar sessão*, so the odd shell out was the correct one and the
  other two moved to it.
* **JIM's `Translate`** — 翻訳 on the iPhone against 翻訳する on the other two,
  and अनुवाद against अनुवाद करें. A noun against a verb, on a button.
* **JIM's `Me`** — わたし on two shells and 自分 on the third.
* **JIM's `When something breaks`** — 出问题的时候 against 当出问题时.

## Majority, not a favourite

Where two shells agree and one does not, the odd one out is the drift, and the
fix follows the two. Where all three differ there is no majority to follow, the
row is a judgement rather than a defect, and it is recorded instead — the same
rule `native_split_wordings.txt` leads with. No row in any of the three
products needed that yet; the check exists so that the first one to arrive is
recorded rather than guessed at.

## What it held here

Three rows, the most of any of the three products, and all three were a word
class rather than a word. **Translate** was 翻訳 on the iPhone and 翻訳する on
the other two — a noun against a verb, on a button — and अनुवाद against
अनुवाद करें. **Me** was わたし twice and 自分 once. **When something breaks**
was 出问题的时候 twice and 当出问题时 once. Each followed the two that agreed.

The first of those is the row 0.48.1 could not reconcile with the console: no
single native wording existed to adopt, because the shells had never been asked
whether they agreed.

## What this file checks

1. **a key two shells share says the same thing** — the strict half, since two
   shells holding one key mean it by construction;
2. **an English string all three hold has a wording all three share** — the
   looser half, which catches the same defect written under different keys;
3. both matched exactly against `native_shell_split.txt`, in both directions;
4. **the tables still parse**, and **the overlap is still large** — 972 English
   strings are common to all three shells here, and a number far below that
   means the extraction changed rather than the product.
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
RECORD = Path(__file__).resolve().parent / "native_shell_split.txt"

TABLES = {
    "ios": REPO / "native" / "ios" / "Sources" / "L10n.swift",
    "android": (REPO / "native" / "android" / "app" / "src" / "main" / "java"
                / "app" / "jim" / "guardian" / "L10n.kt"),
    "windows": REPO / "native" / "windows" / "L10n.cs",
}
SHELLS = ("ios", "android", "windows")
LANGS = ["en", "es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar"]

#: Floors under the parse, a row all three hold, and a floor under the overlap.
#: Per repo; nothing else in this file is.
FLOOR, PROBE, OVERLAP = 240, "alarm.not_emergency", 170

_STR = r'"((?:[^"\\]|\\.)*)"'
_HEAD = {
    "ios": re.compile(r'^\s*' + _STR + r'\s*:\s*\[', re.M),
    "android": re.compile(r'^\s*' + _STR + r'\s+to\s+mapOf\(', re.M),
    "windows": re.compile(r'^\s*\[' + _STR + r'\]\s*=\s*new\(\)\s*\{', re.M),
}
_PAIR = {
    "ios": re.compile(r'"(\w\w)"\s*:\s*' + _STR),
    "android": re.compile(r'"(\w\w)"\s+to\s+' + _STR),
    "windows": re.compile(r'\["(\w\w)"\]\s*=\s*' + _STR),
}
_SIMPLE = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\", "'": "'"}


def _decode(text: str) -> str:
    """A string is what it renders as. See 0.48.1's guard, which shipped a
    count that was nine rows wrong before this existed."""
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
                    out.append(chr(int(text[i + 3:end], 16))); i = end + 1; continue
                except ValueError:
                    pass
        if nxt == "u" and re.match(r"[0-9a-fA-F]{4}", text[i + 2:i + 6]):
            out.append(chr(int(text[i + 2:i + 6], 16))); i += 6; continue
        if nxt in _SIMPLE:
            out.append(_SIMPLE[nxt]); i += 2; continue
        out.append(nxt); i += 2
    return "".join(out)


def _table(shell: str) -> dict[str, dict[str, str]]:
    text = TABLES[shell].read_text(encoding="utf-8")
    heads = list(_HEAD[shell].finditer(text))
    out: dict[str, dict[str, str]] = {}
    for i, m in enumerate(heads):
        stop = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        langs: dict[str, str] = {}
        for p in _PAIR[shell].finditer(text[m.end():stop]):
            if p.group(1) in LANGS and p.group(1) not in langs:
                langs[p.group(1)] = _decode(p.group(2))
        if "en" in langs:
            out[m.group(1)] = langs
    return out


def _tables() -> dict[str, dict[str, dict[str, str]]]:
    return {s: _table(s) for s in SHELLS}


def _shared_keys(t) -> set[str]:
    """Rows two or more shells hold under one key, with one English."""
    holders = defaultdict(list)
    for s in SHELLS:
        for k in t[s]:
            holders[k].append(s)
    return {k for k, ss in holders.items()
            if len(ss) > 1 and len({t[s][k]["en"] for s in ss}) == 1}


def _by_english(t, shell) -> dict[str, list[str]]:
    out = defaultdict(list)
    for k, r in t[shell].items():
        out[r["en"]].append(k)
    return out


def _measured() -> set[str]:
    t = _tables()
    rows = set()

    holders = defaultdict(list)
    for s in SHELLS:
        for k in t[s]:
            holders[k].append(s)
    for key in sorted(_shared_keys(t)):
        for lang in LANGS[1:]:
            if len({t[s][key].get(lang) for s in holders[key]} - {None}) > 1:
                rows.add(f"key: {key}")
                break

    by = {s: _by_english(t, s) for s in SHELLS}
    for english in sorted(set.intersection(*(set(by[s]) for s in SHELLS))):
        for lang in LANGS[1:]:
            vals = [{t[s][k].get(lang) for k in by[s][english]} - {None}
                    for s in SHELLS]
            if all(vals) and not set.intersection(*vals):
                rows.add("english: " + " :: ".join(
                    ",".join(sorted(by[s][english])) for s in SHELLS))
                break
    return rows


def _recorded() -> set[str]:
    return {line.split("  (")[0].strip()
            for line in RECORD.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


def test_the_tables_still_parse_and_still_overlap():
    """A guard on the guard, and the one this file most needs.

    Three tables read as empty share nothing, disagree about nothing, and
    report a product in perfect agreement — which is what this whole audit is
    named after.
    """
    t = _tables()
    for shell in SHELLS:
        assert len(t[shell]) > FLOOR, (
            f"{shell}'s table parsed to {len(t[shell])} rows, far below what "
            "it holds — the row pattern has stopped matching")
        row = t[shell].get(PROBE)
        assert row and sorted(row) == sorted(LANGS), (
            f"{shell}: `{PROBE}` did not parse into all ten languages")
    common = set.intersection(*(set(_by_english(t, s)) for s in SHELLS))
    assert len(common) > OVERLAP, (
        f"only {len(common)} English strings are held by all three shells, "
        "which is too few to conclude anything from — check the parse before "
        "the product")


def test_the_three_shells_do_not_disagree():
    """The defect, directly, and in both directions."""
    measured, recorded = _measured(), _recorded()
    problems = []
    new = sorted(measured - recorded)
    if new:
        problems.append(
            f"{len(new)} row(s) where the shells of one product say different "
            "things and are not in native_shell_split.txt. Where two shells "
            "agree, the third is the drift:\n    " + "\n    ".join(new[:20]))
    stale = sorted(recorded - measured)
    if stale:
        problems.append(
            f"{len(stale)} recorded row(s) now agree — strike them from "
            "native_shell_split.txt:\n    " + "\n    ".join(stale[:20]))
    assert not problems, "\n\n".join(problems)


def test_the_shell_split_backlog_only_shrinks():
    text = RECORD.read_text(encoding="utf-8")
    ceiling = int(re.search(r"^# ceiling: (\d+)$", text, re.M).group(1))
    assert len(_measured()) <= ceiling, (
        f"{len(_measured())} split rows, above the {ceiling} recorded")


@pytest.mark.parametrize("pair", [("ios", "android"), ("ios", "windows"),
                                  ("android", "windows")])
def test_each_pair_of_shells_really_shares_keys(pair):
    """Named pairs rather than a total, because a total can stay healthy while
    one shell drifts out of the set entirely — which is the shape of every
    per-client mistake this audit is named for."""
    t = _tables()
    shared = set(t[pair[0]]) & set(t[pair[1]])
    assert len(shared) > OVERLAP // 2, (
        f"{pair[0]} and {pair[1]} share only {len(shared)} keys")
