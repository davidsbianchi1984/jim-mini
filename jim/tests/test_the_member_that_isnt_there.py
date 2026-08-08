"""Every screen reaches for the same object. Nothing checked what it holds.

0.58.0 ended by restating the standing gap: there is no Swift, Kotlin or C#
toolchain on this machine, so the native UI is asserted by reading and not by
running, and that round widened the amount of screen riding on it. The honest
response is not to pretend a compiler exists. It is to find the classes of
compile error that can be caught by reading, and close them one at a time —
0.57.5 took duplicate declarations and unbalanced braces, 0.57.6 took the
markup. This takes the next one.

## The one thing every screen touches

Each shell has exactly one object the screens read their session from, and
exactly one file that declares it:

    iOS      `AppState`            `@EnvironmentObject var state`  → `state.x`
    Android  the view model        `vm: StudioViewModel`           → `vm.x`
    Windows  `AppState.Current`    a singleton                     → `.Current.X`

So `state.x` is not a guess about types — it is the one receiver in these
trees whose declaration is known without resolving anything. A member it does
not declare is not a style question. Swift says *value of type 'AppState' has
no member 'userId'*, and the shell does not build.

    asked     do the screens parse, and do they say the right things
    mattered  is the thing they reach for actually there

## What the first run found

Thirty-eight call sites across six files in two products, all on the iPhone:

* JIM-mini's `AppState` holds `uid` and `token`; five screens asked it for
  `userId` and `userToken`. Continuity, presence, safety and the synthetic
  self — the whole crisis half of the product.
* `state.api` in JIM-mini and PDI, on an `AppState` that has no client at
  all. Every other screen in both trees reaches `ApiClient.shared`.

Not one of them compiles, and all of them had been sitting in `main`.

## The trap this walked into first

The first extractor reported four more: `call` on the Kotlin view models and
`IsSignedIn` / `IsEnrolled` on the C# ones. Both were the reader's fault —
`fun <T> call(` puts a type parameter between the keyword and the name, and
`public bool IsSignedIn => …` is an expression-bodied property with no `{` or
`(` after it. A guard that reports four defects that are not there is one
nobody reads, which is the lesson this repository keeps relearning. Both
shapes are matched now, and tested for below.
"""

from __future__ import annotations

import re
from pathlib import Path


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
PKG = "app/jim/guardian"

#: (label, the file declaring the object, how a screen names it, where the
#:  screens are, what a declaration looks like there)
SHELLS = (
    ("ios", "native/ios/Sources/AppState.swift", r'\bstate\.(\w+)',
     "native/ios/Sources/Views", (".swift",)),
    ("android", f"native/android/app/src/main/java/{PKG}/AppState.kt", r'\bvm\.(\w+)',
     f"native/android/app/src/main/java/{PKG}/ui", (".kt",)),
    ("windows", "native/windows/AppState.cs", r'AppState\.Current\.(\w+)',
     "native/windows", (".cs",)),
)

#: What counts as declaring a member, per language. Each of these was widened
#: once, by a false finding — see the docstring.
DECLARES = {
    "ios": [r'\b(?:var|let)\s+(\w+)', r'\bfunc\s+(\w+)'],
    # `fun <T> call(` — the type parameter sits between the keyword and the
    # name, and the first pass read straight past it.
    "android": [r'\b(?:var|val)\s+(\w+)', r'\bfun\s*(?:<[^>]*>\s*)?(\w+)'],
    # `public bool IsSignedIn => …` has neither `{` nor `(` after the name.
    "windows": [r'public\s+(?:static\s+)?[\w<>?\[\], ]+?\s(\w+)\s*(?:\{|\(|=>)'],
}


def _code(path: Path) -> str:
    """Source with comments stripped. Prose about a member is not a member,
    and prose about a *missing* member is how this file would report a
    sentence as a defect."""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"^\s*(?://|///|\*)[^\n]*$", "", text, flags=re.M)


def _declared(shell: str, path: Path) -> set[str]:
    src = _code(path)
    out: set[str] = set()
    for pattern in DECLARES[shell]:
        out |= set(re.findall(pattern, src))
    return out


def _reached(shell: str, use: str, root: Path, exts) -> dict[str, set[str]]:
    """{member: the files asking for it} across this shell's screens."""
    found: dict[str, set[str]] = {}
    for path in sorted(root.rglob("*")):
        if path.suffix not in exts or path.name == "AppState.cs":
            continue
        for name in re.findall(use, _code(path)):
            found.setdefault(name, set()).add(path.name)
    return found


# --- the guard ---------------------------------------------------------------

def test_every_member_a_screen_reaches_for_is_declared():
    """The 0.58.1 defect. `state.userId` on an `AppState` that holds `uid`
    is not a style question — the shell does not build."""
    missing = []
    for shell, decl, use, views, exts in SHELLS:
        declared = _declared(shell, REPO / decl)
        for name, files in sorted(_reached(shell, use, REPO / views, exts).items()):
            if name not in declared:
                missing.append(f"{shell}: {name!r} — asked for by "
                               f"{', '.join(sorted(files))}, declared by "
                               f"{Path(decl).name} nowhere")
    assert not missing, "\n    ".join([""] + missing) + (
        "\n  Use the name the object actually has, or declare it.")


# --- the scan has to be able to see, and to fail -----------------------------

def test_the_scan_reads_every_shell():
    """A declaration file that moved, or a receiver spelling that changed,
    makes the check above compare against an empty set — which passes."""
    for shell, decl, use, views, exts in SHELLS:
        assert (REPO / decl).exists(), f"{shell}: {decl} is gone"
        assert len(_declared(shell, REPO / decl)) >= 5, shell
        reached = _reached(shell, use, REPO / views, exts)
        assert len(reached) >= 5, f"{shell}: only {len(reached)} member(s) reached"


def test_a_generic_function_is_a_declaration():
    """`fun <T> call(` — the first pass read past the type parameter and
    reported `call` missing on every Android view model in the estate."""
    src = "fun <T> call(block: suspend () -> T, onResult: (Result<T>) -> Unit) {}"
    found = set()
    for pattern in DECLARES["android"]:
        found |= set(re.findall(pattern, src))
    assert "call" in found


def test_an_expression_bodied_property_is_a_declaration():
    """`public bool IsSignedIn => …` has neither `{` nor `(` after the name,
    and the first pass reported it missing in all three products."""
    src = "    public bool IsSignedIn => !string.IsNullOrEmpty(Pid);"
    found = set()
    for pattern in DECLARES["windows"]:
        found |= set(re.findall(pattern, src))
    assert "IsSignedIn" in found


def test_prose_about_a_member_is_not_a_use(tmp_path):
    """A comment naming `state.somethingGone` is a sentence, and reporting it
    would be this file inventing a defect out of its own documentation."""
    view = tmp_path / "View.swift"
    view.write_text("/// Reads state.somethingGone, which no longer exists.\n"
                    "let x = state.uid\n")
    assert set(re.findall(r'\bstate\.(\w+)', _code(view))) == {"uid"}


def test_the_check_can_fail(tmp_path):
    """The real thing: JIM-mini's `AppState` holds `uid`, and five screens
    asked it for `userId`."""
    state = tmp_path / "AppState.swift"
    state.write_text("final class AppState: ObservableObject {\n"
                     "    @Published var uid: String?\n"
                     "}\n")
    view = tmp_path / "Views"
    view.mkdir()
    (view / "SafetyView.swift").write_text("let u = state.userId\n")
    declared = _declared("ios", state)
    reached = _reached("ios", r'\bstate\.(\w+)', view, (".swift",))
    assert "uid" in declared and "userId" not in declared
    assert sorted(set(reached) - declared) == ["userId"]
