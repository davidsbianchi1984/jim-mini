"""A screen that calls the localizer, and a localizer with nothing to say.

## The finding

Three native screens were written for the synthetic self, one per shell, each
asking `L10n` for its wording the way every other screen in those shells does.
The keys were added to the **console's** `app/src/l10n.ts` and to none of the
three native tables.

The suite was green. Every existing language guard passed:
`native_untranslated.txt` records English strings that are *there*, and these
were not there — the screens held no English to find, only key names. The
per-shell door audit passed too, because the bindings were called. Nothing
asked the one question that mattered.

    asked     does the screen call the localizer
    mattered  does the localizer have anything to say

On a device, `L10n.t("self.title")` with no row returns the key, so the screen
renders the literal string `self.title` where a heading belongs — in every
language including English, on all three phones, on a screen about what a
person's medication is allowed to say about them.

## What this checks

Both directions are wrong in different ways, so both are checked:

* a key a shell **asks for** and does not hold is a screen showing its own
  source code;
* a key a shell **holds** and never asks for is a translation somebody paid
  attention to that no reader will ever get — the same defect
  `test_no_key_is_translated_into_ten_languages_and_used_nowhere` catches in
  the console, which the shells never had.

The extraction is per shell, because that is the whole lesson of
`test_the_phone_is_a_client_too`: a union tells you *some* client is fine.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()

#: Each shell: where its screens live, what its sources are called, and where
#: its table is. Derived per shell rather than unioned — see the docstring.
SHELLS = {
    "ios": (REPO / "native" / "ios", (".swift",),
            REPO / "native" / "ios" / "Sources" / "L10n.swift"),
    "android": (REPO / "native" / "android", (".kt",),
                REPO / "native" / "android" / "app" / "src" / "main" / "java"
                / "app" / "jim" / "guardian" / "L10n.kt"),
    "windows": (REPO / "native" / "windows", (".cs", ".xaml"),
                REPO / "native" / "windows" / "L10n.cs"),
}

#: `L10n.t("key")` in Swift and Kotlin, `L10n.T("key")` in C#. One pattern:
#: the method name differs only in case and nothing else in these trees looks
#: like it.
_ASKED = re.compile(r'\bL10n\s*\.\s*[tT]\s*\(\s*"([\w.]+)"')

#: **Also 0.47.1.** `fill` takes the key first exactly as `t` does, and this
#: pattern did not know the method existed — so every row whose only caller
#: interpolates a value into it read as asked for by nobody. Nine of them, on
#: the screens this round wired.
#:
#:     asked     does a shell call L10n.t with this key
#:     mattered  does a shell ask for this row at all
_ASKED_FILL = re.compile(r'\bL10n\s*\.\s*[fF]ill\s*\(\s*"([\w.]+)"')

#: **Added in 0.47.1**, and it is the mirror image of what the ratchet guard
#: was missing in the same round. That one could not see a *string* chosen by
#: a ternary; this one could not see a *key* chosen by one:
#:
#:     L10n.t(armed ? "action.update" : "cw.arm", lang)
#:
#: The key is not the first thing after the paren, so `_ASKED` read past it
#: and this file reported seventy-five live rows as asked for by nobody.
#:
#:     asked     is the key the first argument
#:     mattered  does the shell ask for it
#:
#: The failure mode is the dangerous direction: a guard that calls a row dead
#: invites somebody to delete a row a screen is using. Two branches, both
#: captured, in Swift/C# ternary form and Kotlin if/else form.
_ASKED_TERNARY = [
    re.compile(r'\bL10n\s*\.\s*[tTfF][a-zA-Z]*\s*\([^()"]*\?\s*"([\w.]+)"\s*:\s*"([\w.]+)"'),
    re.compile(r'\bL10n\s*\.\s*[tTfF][a-zA-Z]*\s*\(\s*if\s*\([^)]*\)\s*"([\w.]+)"\s*else\s*"([\w.]+)"'),
]

#: A row in any of the three table syntaxes — Swift `"k": [`, Kotlin
#: `"k" to mapOf(`, C# `["k"] = new()`.
_HELD = re.compile(r'"([\w.]+)"\s*(?::\s*\[|\s+to\s+mapOf\(|"?\]\s*=\s*new)')


def _asked(shell: str) -> dict[str, list[str]]:
    root, suffixes, table = SHELLS[shell]
    found: dict[str, list[str]] = {}
    for path in sorted(root.rglob("*")):
        if path.suffix not in suffixes or path == table:
            continue
        text = path.read_text(encoding="utf-8")
        keys = list(_ASKED.findall(text))
        keys += _ASKED_FILL.findall(text)
        keys += [k for rx in _ASKED_TERNARY for pair in rx.findall(text)
                 for k in pair]
        for key in keys:
            found.setdefault(key, []).append(path.name)
    return found


def _held(shell: str) -> set[str]:
    return set(_HELD.findall(SHELLS[shell][2].read_text(encoding="utf-8")))


@pytest.mark.parametrize("shell", sorted(SHELLS))
def test_every_key_a_shell_asks_for_is_in_its_own_table(shell):
    """The defect, directly. A missing row is a screen showing a key name."""
    held, asked = _held(shell), _asked(shell)
    missing = sorted(k for k in asked if k not in held)
    assert not missing, (
        f"{shell} asks for {len(missing)} key(s) its L10n table does not "
        "hold, so those screens render the key name itself:\n    "
        + "\n    ".join(f"{k}  ({', '.join(sorted(set(asked[k])))})"
                        for k in missing[:20]))


@pytest.mark.parametrize("shell", sorted(SHELLS))
def test_the_extraction_finds_something(shell):
    """A guard on the guard: a pattern that stopped matching reports a shell
    with no missing keys because it found no keys at all."""
    asked, held = _asked(shell), _held(shell)
    assert len(asked) >= 10, (
        f"only {len(asked)} L10n lookups found in {shell} — the call pattern "
        "has stopped matching, and the check above would pass on nothing")
    assert len(held) >= 20, (
        f"only {len(held)} rows parsed from {shell}'s table — the row pattern "
        "has stopped matching, and every key would look missing")


@pytest.mark.parametrize("shell", sorted(SHELLS))
def test_no_row_is_translated_into_ten_languages_and_asked_for_by_nobody(shell):
    """The other direction.

    The console gained this check after two keys shipped translated and wired
    to nothing; the shells never had it. A dead row is not merely waste — it is
    a translation sitting beside the English it was meant to replace, with
    nothing to say which one a reader gets.

    Chrome the shell renders from a list rather than a literal is excluded by
    prefix, the way the console's version handles `nav.${id}`.
    """
    built_from_a_list = ("tab.",)
    dead = sorted(k for k in _held(shell) - set(_asked(shell))
                  if not k.startswith(built_from_a_list))
    recorded = {line.split(": ", 1)[1] for line in _dead_record()
                if line.startswith(f"{shell}: ")}
    undecided = sorted(set(dead) - recorded)
    stale = sorted(recorded - set(dead))
    problems = []
    if undecided:
        problems.append(
            f"{shell} holds {len(undecided)} translated row(s) nothing asks "
            "for:\n    " + "\n    ".join(undecided[:20])
            + "\n  Wire it, delete it, or record it — but recording is "
              "ratcheted.")
    if stale:
        problems.append(
            f"{shell}: {len(stale)} recorded row(s) are alive or gone — strike "
            "them from native_dead_keys.txt:\n    " + "\n    ".join(stale))
    assert not problems, "\n\n".join(problems)


def _dead_record() -> set[str]:
    path = Path(__file__).resolve().parent / "native_dead_keys.txt"
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


def test_the_dead_key_backlog_only_shrinks():
    ceiling = int(re.search(
        r"# ceiling: (\d+)",
        (Path(__file__).resolve().parent / "native_dead_keys.txt")
        .read_text(encoding="utf-8")).group(1))
    per_shell = {}
    for line in _dead_record():
        shell = line.split(": ", 1)[0]
        per_shell[shell] = per_shell.get(shell, 0) + 1
    worst = max(per_shell.values()) if per_shell else 0
    assert worst <= ceiling, (
        f"{worst} dead rows in one shell, above the {ceiling} this started at")

    # The total, as well as the worst shell.
    #
    # `worst` is a maximum over three shells, so the number of dead rows could
    # rise — iOS 3 to 4, a fourth shell added carrying four of its own — with
    # this check passing every time, because no single shell crossed the line.
    # The file's own header says "the ceiling does not move up" and meant the
    # count of dead rows; the ratchet was reading one shell's share of it.
    #
    #     asked     is any one shell's dead-key count above the line
    #     mattered  is the number of dead rows going up
    total_ceiling = int(re.search(
        r"# total: (\d+)",
        (Path(__file__).resolve().parent / "native_dead_keys.txt")
        .read_text(encoding="utf-8")).group(1))
    total = sum(per_shell.values())
    assert total <= total_ceiling, (
        f"{total} dead rows across the shells, above the {total_ceiling} "
        "recorded. A row translated into ten languages that nothing asks for "
        "is a translation sitting beside the English it was meant to replace.")


def test_the_three_shells_agree_with_the_console_on_shared_keys():
    """One wording, four surfaces.

    The `self.*` rows were lifted from `app/src/l10n.ts` into the shells rather
    than retyped, so a person reading the same sentence on a phone and on the
    desktop reads the same sentence. Retyping is how they drift.
    """
    console = REPO / "app" / "src" / "l10n.ts"
    text = console.read_text(encoding="utf-8")
    wanted = {}
    for m in re.finditer(r'^  "(self\.[\w.]+)":\s*\{(.*?)\n  \},', text,
                         re.S | re.M):
        english = re.search(r'\ben:\s*"((?:[^"\\]|\\.)*)"', m.group(2))
        if english:
            wanted[m.group(1)] = english.group(1)
    assert len(wanted) >= 20, (
        f"only {len(wanted)} self.* keys read from the console table")

    for shell, (_, _, table) in SHELLS.items():
        source = table.read_text(encoding="utf-8")
        for key, english in wanted.items():
            if f'"{key}"' not in source:
                # Not every console string has a counterpart on a phone: the
                # shells have no signed-out branch, so `self.signin` is the
                # console's alone. What matters is that a row a shell *does*
                # carry says what the console's says.
                continue
            row = source[source.index(f'"{key}"'):]
            row = row[:row.index("\n")]
            assert english.replace('\\"', '"') in row.replace('\\"', '"'), (
                f"{shell}'s {key} does not say what the console's does. These "
                "were lifted from one table so the phone and the desktop "
                "cannot tell somebody different things.")
