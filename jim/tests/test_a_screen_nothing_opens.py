"""The synthetic self shipped into three shells, and no shell could show it.

## The finding

Last round put the `self` profile screen on the phones — the one QRME profile
that *is* this person, the surface where they say what their Guardian may pass
on about their medication. One screen per shell, each with its wording in ten
languages, and `test_a_shell_asks_for_a_key_it_has.py` written to prove the
wording was there.

It was there. Nothing else was.

| Shell | Screen | State |
|---|---|---|
| iOS | `SelfProfileSection` | declared; nothing rendered it |
| Android | `SelfProfileScreen` | declared; nothing called it |
| Windows | `SelfProfilePage` | declared; nothing navigated to it |

And on two of the three it would not have compiled if something had. `L10n.t`
takes a key **and a language** in Swift and Kotlin; every one of the forty
calls on those two screens passed only the key. The Windows shell's `L10n.T`
takes the key alone and reads the language itself, which is why that one was
fine — three shells, two spellings of the same function, and a screen written
against the wrong one twice.

    asked     does the screen have its wording
    mattered  does anything open the screen

The previous guard is not wrong; it is one question short. It was written
after keys shipped into the console and not the shells, so it asks about keys.
A screen is reached by three separate things — its strings, its bindings, and
somebody putting it in the navigation — and this audit now has a guard for
each of the first two.

## Why an arity check without a compiler

There is no Swift or Kotlin toolchain in this environment, which is the whole
reason forty calls to a two-parameter function sat in the tree unnoticed. A
source-level check cannot replace a compiler, and this one does not try: it
reads each shell's own localizer for how many parameters it declares, and
holds that shell's call sites to that number. It is the narrowest form of the
question that can be asked here, and it is the exact question that was missed.

## What counts as a screen

The naming convention each shell already keeps: `…View`/`…Section` conforming
to `View` in Swift, `…Screen` composables in Kotlin, `…Page : Page` in C#. A
card is not covered — `OfflinePostureCard` and the rest are components, and
the line has to fall somewhere. Screens are where the convention is uniform
enough to check without inventing one.

Comments are stripped before matching. That is not caution in the abstract:
the version of the offline-posture check written earlier in this same round
passed on `null /* api.offlineStatus() */`, and the version of the egress
check before that passed on a comment containing `offline.enabled()`. A
corpus that contains prose about a name will satisfy a search for that name.
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

_BLOCK = re.compile(r"/\*.*?\*/", re.S)
_LINE = re.compile(r"//[^\n]*")


def _code(path: Path) -> str:
    """The file with its comments removed. See the docstring — twice in this
    audit a check has been satisfied by prose describing the thing it was
    looking for."""
    return _LINE.sub("", _BLOCK.sub(
        "", path.read_text(encoding="utf-8", errors="ignore")))


# --- a screen nothing opens ------------------------------------------------

#: shell -> (tree, suffixes, how a screen is declared, how one is opened,
#:           how to blank the declaration before searching)
SHELLS = {
    "ios": (
        REPO / "native/ios", {".swift"},
        re.compile(r"^(?:public )?struct (\w+(?:View|Section)): View\b", re.M),
        lambda n: rf"\b{n}\s*\(",
        lambda n: rf"struct {n}: View",
    ),
    "android": (
        REPO / "native/android", {".kt"},
        re.compile(r"^fun (\w+Screen)\(", re.M),
        lambda n: rf"\b{n}\s*\(",
        lambda n: rf"fun {n}\(",
    ),
    "windows": (
        REPO / "native/windows", {".cs"},
        re.compile(r"class (\w+Page) : Page"),
        lambda n: rf"typeof\(\s*{n}\s*\)",
        lambda n: rf"class {n} : Page",
    ),
}


def _files(shell: str) -> list[Path]:
    base, suffixes, *_ = SHELLS[shell]
    if not base.exists():
        return []
    return [p for p in sorted(base.rglob("*")) if p.suffix in suffixes]


def _declared(shell: str) -> set[str]:
    _, _, decl, _, _ = SHELLS[shell]
    return {n for p in _files(shell) for n in decl.findall(_code(p))}


def _unopened(shell: str) -> list[str]:
    _, _, _, opens, strip = SHELLS[shell]
    corpus = "\n".join(_code(p) for p in _files(shell))
    # **Blanking the declaration first.** Kotlin declares and calls a
    # composable with the same `Name(` spelling, so a search over the whole
    # tree finds the definition and calls it a caller. That is the same shape
    # `test_a_native_binding_is_not_a_door_either` had to fix when its Swift
    # check matched each binding's own `func` line.
    return sorted(n for n in _declared(shell)
                  if not re.search(opens(n), re.sub(strip(n), "", corpus)))


@pytest.mark.parametrize("shell", sorted(SHELLS))
def test_every_screen_this_shell_defines_can_be_reached(shell):
    """The defect, directly. A screen nothing opens is work that shipped and
    cannot be used, and it does not announce itself: it compiles, its strings
    pass the language guards, and its bindings pass the door guards."""
    unopened = _unopened(shell)
    assert not unopened, (
        f"{shell} defines {len(unopened)} screen(s) nothing opens:\n    "
        + "\n    ".join(unopened)
        + "\n  Put it in the navigation, or delete it — but it is not "
          "shipped while it sits here.")


@pytest.mark.parametrize("shell", sorted(SHELLS))
def test_the_screen_extraction_finds_something(shell):
    """A guard on the guard. Every false pass in this audit has come from a
    pattern that stopped matching, and a check over an empty set is green."""
    found = _declared(shell)
    assert len(found) >= 5, (
        f"only {len(found)} screen(s) found in {shell} — the declaration "
        "pattern has stopped matching, and the check above would pass on "
        "nothing")


# --- and can compile when it is opened -------------------------------------

#: shell -> (how that shell's localizer declares itself, how it is called)
LOCALIZERS = {
    "ios": (REPO / "native/ios/Sources/L10n.swift",
            re.compile(r"static func t\(([^)]*)\)"),
            re.compile(r"\bL10n\s*\.\s*t\s*\(")),
    "android": (next(iter((REPO / "native/android").rglob("L10n.kt")), None),
                re.compile(r"fun t\(([^)]*)\)"),
                re.compile(r"\bL10n\s*\.\s*t\s*\(")),
    "windows": (REPO / "native/windows/L10n.cs",
                re.compile(r"public static string T\(([^)]*)\)"),
                re.compile(r"\bL10n\s*\.\s*T\s*\(")),
}


def _declared_arity(shell: str) -> int:
    path, decl, _ = LOCALIZERS[shell]
    params = decl.search(path.read_text(encoding="utf-8")).group(1).strip()
    return len([p for p in params.split(",") if p.strip()])


def _args_at(text: str, open_paren: int) -> int:
    """Top-level arguments in the call whose `(` is at `open_paren`.

    Depth- and string-aware, because an argument can itself be a call and a
    string can contain a comma. Returns 0 for `()`.
    """
    depth, count, i, quote = 0, 1, open_paren, ""
    while i < len(text):
        c = text[i]
        if quote:
            if c == "\\":
                i += 2
                continue
            if c == quote:
                quote = ""
        elif c in "\"'":
            quote = c
        elif c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
            if depth == 0:
                return 0 if text[open_paren + 1:i].strip() == "" else count
        elif c == "," and depth == 1:
            count += 1
        i += 1
    return -1  # unbalanced — reported by the caller rather than guessed at


def _call_sites(shell: str) -> list[tuple[str, int, int]]:
    path, _, call = LOCALIZERS[shell]
    sites = []
    for p in _files(shell):
        if p == path:
            continue
        text = _code(p)
        for m in call.finditer(text):
            open_paren = m.end() - 1
            line = text[:open_paren].count("\n") + 1
            sites.append((p.name, line, _args_at(text, open_paren)))
    return sites


@pytest.mark.parametrize("shell", sorted(LOCALIZERS))
def test_every_localizer_call_passes_what_that_shell_declares(shell):
    """Forty calls passed one argument to a two-parameter function, on the
    two shells with no compiler in this environment.

    Per shell, against that shell's own signature — `L10n.T` on Windows takes
    the key alone and reads the language itself, and holding all three to one
    number would be the union mistake again.
    """
    want = _declared_arity(shell)
    wrong = [f"{f}:{line} — {n} argument(s)"
             for f, line, n in _call_sites(shell) if n != want]
    assert not wrong, (
        f"{shell}'s localizer takes {want} argument(s); {len(wrong)} call "
        "site(s) pass a different number, so those files do not "
        "compile:\n    " + "\n    ".join(wrong[:20]))


@pytest.mark.parametrize("shell", sorted(LOCALIZERS))
def test_the_call_extraction_finds_something(shell):
    """The floor is 2, not 5, and the number is a finding rather than a
    convenience.

    QRME's Windows shell makes exactly two localizer calls — the nav loop and
    one button — where its iOS shell makes seven and its Android shell eight.
    That shell renders nearly all of its chrome from XAML literals, so a
    German user gets a German nav and English everything else. It is a real
    gap, it is not what this file is about, and raising the floor to hide it
    would be worse than recording it. A regex that has stopped matching
    reports zero, which this still catches.
    """
    sites = _call_sites(shell)
    assert len(sites) >= 2, (
        f"only {len(sites)} localizer call(s) found in {shell} — the call "
        "pattern has stopped matching")
    assert _declared_arity(shell) >= 1, (
        f"{shell}'s localizer signature parsed as taking no arguments, which "
        "would make every call site look wrong")


def test_the_argument_counter_counts():
    """The counter is the only non-trivial piece here, and a counter that is
    wrong in one direction turns this file into forty false failures."""
    assert _args_at('f()', 1) == 0
    assert _args_at('f("a")', 1) == 1
    assert _args_at('f("a", b)', 1) == 2
    assert _args_at('f("a,b")', 1) == 1, "a comma inside a string is not a separator"
    assert _args_at('f(g(x, y), b)', 1) == 2, "a nested call is one argument"
    assert _args_at('f("a", [x, y])', 1) == 2

# --- and the arguments are in the order the helper declares -----------------

#: Each shell's shared request helper: where it is declared and how.
#:
#: Swift and C# name their arguments at the call site or take a URL, so an
#: order mistake there is visible. Kotlin's helper takes
#: `(path, method, body, token)` — four positional strings and objects — and
#: two of the first three are `String`. Passing the verb first compiles
#: perfectly and sends `GET /GET` to a server that answers 404.
_KOTLIN_HELPER = re.compile(
    r"private suspend fun request\(\s*(\w+): String,\s*(\w+): String")
_VERBS = ("GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS")


def _kotlin_client() -> Path | None:
    return next(iter((REPO / "native/android").rglob("ApiClient.kt")), None)


def test_the_kotlin_client_passes_a_path_where_a_path_goes():
    """A type-compatible argument swap, in the one shell with no compiler here.

    Found by the route-door guard rather than by this one, and only because a
    DELETE went missing from the backlog: three calls in this shell and one in
    the sibling's passed `("GET", "/offline/status", ...)` to a helper
    declared `(path, method, ...)`. Both arguments are `String`, so nothing
    complained, and the request went to `base + "GET"` with the method set to
    a path.

        asked     does the call have the right number of arguments
        mattered  does it have them in the right order

    The check is narrow on purpose: it knows the helper's first parameter is
    the path, and an HTTP verb is never a path.
    """
    path = _kotlin_client()
    if path is None:
        pytest.skip("no Kotlin client in this repo")
    text = _code(path)
    declared = _KOTLIN_HELPER.search(text)
    assert declared, (
        "the shared `request` helper's signature no longer parses, so this "
        "check cannot tell which argument is the path")
    assert declared.group(1) == "path", (
        f"the helper's first parameter is now {declared.group(1)!r}; this "
        "check assumes it is the path and must be updated deliberately")

    wrong = []
    for m in re.finditer(r'\brequest\s*\(\s*"([^"\n]*)"', text):
        first = m.group(1)
        if first in _VERBS:
            wrong.append(f"line {text[:m.start()].count(chr(10)) + 1}: "
                         + 'request("' + first + '", ...) '
                         + "\u2014 verb in the path slot")
    assert not wrong, (
        f"{len(wrong)} call(s) pass an HTTP verb where the helper wants a "
        "path, which compiles and then requests the wrong URL:\n    "
        + "\n    ".join(wrong))
