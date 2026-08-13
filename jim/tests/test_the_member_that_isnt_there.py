"""Every screen reaches for the same few objects. Nothing checked what they hold.

0.58.0 ended by restating the standing gap: there is no Swift, Kotlin or C#
toolchain on this machine, so the native UI is asserted by reading and not by
running, and that round widened the amount of screen riding on it. The honest
response is not to pretend a compiler exists. It is to find the classes of
compile error that can be caught by reading, and close them one at a time —
0.57.5 took duplicate declarations and unbalanced braces, 0.57.6 took the
markup. This takes the next one.

## The receivers whose type is known for free

Most expressions in these trees need a type checker to judge. A few do not.
Where a screen names an object that exactly one file declares, the member it
asks for can be looked up without resolving anything:

    iOS      `state.x`                `AppState.swift`
             `ApiClient.shared.x`     `ApiClient.swift`
             `Theme.x`                `Theme.swift`
    Android  `vm.x`                   `AppState.kt`
             `ApiClient.x`            `ApiClient.kt`
             `Qrme.x`                 `ui/Theme.kt`
    Windows  `AppState.Current.X`     `AppState.cs`
             `ApiClient.Shared.X`     `ApiClient.cs`
             `{StaticResource X}`     `App.xaml`

A member one of these does not declare is not a style question. Swift says
*value of type 'AppState' has no member 'userId'*, Kotlin says *unresolved
reference*, and the shell does not build.

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

## What widening it to the other receivers found

One more, and it is the cheapest kind of break there is. QRME's Android
problem-report card painted itself with `Qrme.Card2`; the theme declares
`Card` and has never declared a second. Both sibling products paint the same
card with `Card`, so it was a one-character slip that no amount of reading
the diff would have caught — and Compose has no fallback for an unresolved
colour, so the whole screen file fails to compile with it.

The API clients came back clean: 1,613 call sites across nine shells, every
one of them naming a method the client actually has. That is worth asserting
anyway. The value of a guard is not only what it finds on the day it is
written — 0.58.1's own defect had been in `main` for rounds.

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
ANDROID = f"native/android/app/src/main/java/{PKG}"
#: The Android theme object.
THEME = "Jim"

#: (label, language, the file that declares the object, how a caller names it,
#:  where the callers are, which suffixes count, the floor of distinct members
#:  the scan must still reach). The declaring file is skipped by name — it
#:  refers to its own members without the receiver, and reading it back would
#:  make every row self-satisfying.
RECEIVERS = (
    ("ios/state", "swift", "native/ios/Sources/AppState.swift",
     r'\bstate\.(\w+)', "native/ios/Sources/Views", (".swift",), 8),
    ("ios/api", "swift", "native/ios/Sources/ApiClient.swift",
     r'\bApiClient\.shared\.(\w+)', "native/ios/Sources", (".swift",), 90),
    ("ios/theme", "swift", "native/ios/Sources/Theme.swift",
     r'\bTheme\.(\w+)', "native/ios/Sources", (".swift",), 10),

    ("android/state", "kotlin", f"{ANDROID}/AppState.kt",
     r'\bvm\.(\w+)', f"{ANDROID}/ui", (".kt",), 8),
    ("android/api", "kotlin", f"{ANDROID}/ApiClient.kt",
     r'\bApiClient\.(\w+)', ANDROID, (".kt",), 92),
    ("android/theme", "kotlin", f"{ANDROID}/ui/Theme.kt",
     rf'\b{THEME}\.(\w+)', ANDROID, (".kt",), 10),

    ("windows/state", "csharp", "native/windows/AppState.cs",
     r'\bAppState\.Current\.(\w+)', "native/windows", (".cs",), 6),
    ("windows/api", "csharp", "native/windows/ApiClient.cs",
     r'\bApiClient\.Shared\.(\w+)', "native/windows", (".cs",), 90),
)

#: What counts as declaring a member, per language. Each of these was widened
#: once, by a false finding — see the docstring.
DECLARES = {
    "swift": [r'\b(?:var|let)\s+(\w+)', r'\bfunc\s+(\w+)'],
    # `fun <T> call(` — the type parameter sits between the keyword and the
    # name, and the first pass read straight past it. And `data class
    # ProblemRow(` — a type nested in the client object is a member too
    # (`ApiClient.ProblemRow` in a screen is an unresolved reference without
    # it), which this row learned the evening the problems reader landed in
    # all three products at once.
    "kotlin": [r'\b(?:var|val)\s+(\w+)', r'\bfun\s*(?:<[^>]*>\s*)?(\w+)',
               r'\b(?:data\s+|enum\s+|sealed\s+)?class\s+(\w+)',
               r'\bobject\s+(\w+)'],
    # `public bool IsSignedIn => …` has neither `{` nor `(` after the name,
    # and `public Task<System.Collections.Generic.Dictionary<string, bool>>
    # Features(` puts dots inside the return type — which is how widening
    # this row to the API clients started by reporting two methods that are
    # right there in the file.
    "csharp": [r'public\s+(?:static\s+)?[\w<>?\[\], .]+?\s(\w+)\s*(?:\{|\(|=>)'],
}

#: WinUI ships brushes of its own (`TextFillColorPrimaryBrush` and friends)
#: which no `App.xaml` declares. Nothing in these pages uses one yet; the set
#: exists so that the day one does, the answer is a named exemption rather
#: than a weakened check.
SYSTEM_BRUSHES: set[str] = set()


#: The C# singletons a page can put in a local before using it. `var st =
#: AppState.Current;` then `st.Uid` is the same reach as `AppState.Current.Uid`
#: and the pattern below saw none of it — which is how a `st.UserId` on an
#: `AppState` that holds `Uid` sat in `main` through a release: the reader
#: found no call sites at all on that page and reported agreement.
SINGLETONS = ("AppState.Current", "ApiClient.Shared")


def _expand_aliases(text: str) -> str:
    """Rewrite `st.X` back to `AppState.Current.X` where `st` is that object.

    Only for a local assigned the singleton outright, which is the whole of
    what these pages do. Anything cleverer needs a type checker, and this file
    is explicitly the set of errors catchable without one.

    **And only when the name means that and nothing else anywhere in the
    file.** C# scopes a local to its method; this reader has no scopes, so a
    page that says `var s = AppState.Current;` in one handler and
    `mine.Select(s => …)` in another would have every member of every `s` in
    it attributed to the state object. The first cut did exactly that and
    reported twenty-eight members that are all perfectly real — which is the
    failure mode this file's own docstring is about. A name that is bound to
    anything else, even once, is left alone: an unexpanded alias costs a
    missed call site, and a wrong one costs the guard its readers.
    """
    for singleton in SINGLETONS:
        for local in set(re.findall(
                rf"\b(?:var|[\w.<>?\[\]]+)\s+(\w+)\s*=\s*{re.escape(singleton)}\s*;",
                text)):
            bindings = re.findall(
                rf"\b(?:var|[\w.<>?\[\]]+)\s+{local}\s*=\s*([^;]+);", text)
            lambdas = re.search(rf"[(,]\s*{local}\s*(?:,[^)]*)?\)?\s*=>", text)
            if lambdas or any(b.strip() != singleton for b in bindings):
                continue
            text = re.sub(rf"\b{local}\.", f"{singleton}.", text)
    return text


def _code(path: Path) -> str:
    """Source with comments stripped. Prose about a member is not a member,
    and prose about a *missing* member is how this file would report a
    sentence as a defect."""
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"^\s*(?://|///|\*)[^\n]*$", "", text, flags=re.M)
    if path.suffix == ".cs":
        text = _expand_aliases(text)
    return text


def _declared(lang: str, path: Path) -> set[str]:
    src = _code(path)
    out: set[str] = set()
    for pattern in DECLARES[lang]:
        out |= set(re.findall(pattern, src))
    return out


def _reached(use: str, root: Path, exts, declares: str = "") -> dict[str, set[str]]:
    """{member: the files asking for it} across everything under `root`,
    minus the file named by `declares`."""
    found: dict[str, set[str]] = {}
    for path in sorted(root.rglob("*")):
        if path.suffix not in exts or path.name == declares:
            continue
        for name in re.findall(use, _code(path)):
            found.setdefault(name, set()).add(path.name)
    return found


def _brushes(repo: Path | None = None) -> tuple[set[str], dict[str, set[str]]]:
    """The keys `App.xaml` declares, and the keys the pages ask it for."""
    repo = REPO if repo is None else repo
    app = (repo / "native/windows/App.xaml").read_text(encoding="utf-8")
    keys = set(re.findall(r'x:Key\s*=\s*"([^"]+)"', app))
    used: dict[str, set[str]] = {}
    for path in sorted((repo / "native/windows").rglob("*")):
        if path.name == "App.xaml":
            continue
        if path.suffix == ".xaml":
            names = re.findall(r'\{StaticResource\s+([^}]+?)\s*\}',
                               path.read_text(encoding="utf-8"))
        elif path.suffix == ".cs":
            # `Application.Current.Resources[valid ? "A" : "B"]` — every
            # literal inside the indexer, however the choice is made.
            names = [n for span in re.findall(r'Resources\[(.*?)\]',
                                              _code(path), flags=re.S)
                     for n in re.findall(r'"([^"]+)"', span)]
        else:
            continue
        for name in names:
            used.setdefault(name, set()).add(path.name)
    return keys, used


# --- the guard ---------------------------------------------------------------

def test_every_member_a_screen_reaches_for_is_declared():
    """0.58.1's defect and 0.58.2's. `state.userId` on an `AppState` that
    holds `uid`, and `Qrme.Card2` on a theme with one card colour, are not
    style questions — the shell does not build."""
    missing = []
    for label, lang, decl, use, root, exts, _floor in RECEIVERS:
        declared = _declared(lang, REPO / decl)
        reached = _reached(use, REPO / root, exts, Path(decl).name)
        for name, files in sorted(reached.items()):
            if name not in declared:
                missing.append(f"{label}: {name!r} — asked for by "
                               f"{', '.join(sorted(files))}, declared by "
                               f"{Path(decl).name} nowhere")
    assert not missing, "\n    ".join([""] + missing) + (
        "\n  Use the name the object actually has, or declare it.")


def test_every_brush_a_page_paints_with_is_declared():
    """The Windows half of the theme check. There is no colour object in the
    C# — the palette is `App.xaml`, and a page naming a key it does not hold
    throws at load rather than at compile, which is worse."""
    keys, used = _brushes()
    missing = [f"{name!r} — painted by {', '.join(sorted(files))}"
               for name, files in sorted(used.items())
               if name not in keys and name not in SYSTEM_BRUSHES]
    assert not missing, "\n    ".join([""] + missing) + (
        "\n  Declare the key in App.xaml, or name one it already has.")


# --- the scan has to be able to see, and to fail -----------------------------

def test_the_scan_reads_every_receiver():
    """A declaration file that moved, or a receiver spelling that changed,
    makes the check above compare against an empty set — which passes."""
    for label, lang, decl, use, root, exts, floor in RECEIVERS:
        assert (REPO / decl).exists(), f"{label}: {decl} is gone"
        assert len(_declared(lang, REPO / decl)) >= 5, label
        reached = _reached(use, REPO / root, exts, Path(decl).name)
        assert len(reached) >= floor, (
            f"{label}: only {len(reached)} member(s) reached, floor {floor} — "
            f"the receiver spelling or the caller root has moved")


def test_the_brush_scan_reads_the_pages():
    keys, used = _brushes()
    assert len(keys) >= 12, f"only {len(keys)} key(s) in App.xaml"
    assert len(used) >= 10, f"only {len(used)} key(s) painted with"


def test_a_singleton_put_in_a_local_is_still_a_use(tmp_path):
    """The gap that let a `st.UserId` ship. Every other page in these trees
    spells the singleton out, so the row's floor stayed comfortably met while
    the pages that alias it were read as using nothing at all."""
    page = tmp_path / "CustodyPage.xaml.cs"
    page.write_text("var st = AppState.Current;\n"
                    "if (st.Uid is null || st.Token is null) return;\n")
    reached = set(re.findall(r'\bAppState\.Current\.(\w+)', _code(page)))
    assert reached == {"Uid", "Token"}


def test_an_alias_does_not_leak_across_names(tmp_path):
    """`client.Foo` is not `AppState.Current.Foo` just because some other
    local in the file happens to hold the state."""
    page = tmp_path / "SomePage.xaml.cs"
    page.write_text("var st = AppState.Current;\n"
                    "var other = Something.Else;\n"
                    "var a = st.Uid; var b = other.Whatever;\n")
    assert set(re.findall(r'\bAppState\.Current\.(\w+)', _code(page))) == {"Uid"}


def test_a_name_bound_to_two_things_is_not_expanded(tmp_path):
    """The first cut of the expansion reported twenty-eight real members as
    missing: one page said `var s = AppState.Current;` in one handler and
    `mine.Select(s => new Row(s.Subject))` in another, and this reader has no
    scopes. A name that means two things is left alone."""
    page = tmp_path / "PeoplePage.xaml.cs"
    page.write_text("var s = AppState.Current;\n"
                    "var a = s.Uid;\n"
                    "CamList.ItemsSource = mine.Select(s => new Row(s.Subject));\n")
    assert set(re.findall(r'\bAppState\.Current\.(\w+)', _code(page))) == set()


def test_a_generic_function_is_a_declaration():
    """`fun <T> call(` — the first pass read past the type parameter and
    reported `call` missing on every Android view model in the estate."""
    src = "fun <T> call(block: suspend () -> T, onResult: (Result<T>) -> Unit) {}"
    found = set()
    for pattern in DECLARES["kotlin"]:
        found |= set(re.findall(pattern, src))
    assert "call" in found


def test_a_nested_data_class_is_a_declaration():
    """`data class ProblemRow(` inside the client object. A screen that says
    `ApiClient.ProblemRow` is reaching for a member exactly the way it
    reaches for a method, and the first pass reported it missing in all
    three products the evening the problems reader landed."""
    src = ("    data class ProblemRow(val op: String, val statusCode: Int,\n"
           "                          val count: Int)")
    found = set()
    for pattern in DECLARES["kotlin"]:
        found |= set(re.findall(pattern, src))
    assert "ProblemRow" in found


def test_an_expression_bodied_property_is_a_declaration():
    """`public bool IsSignedIn => …` has neither `{` nor `(` after the name,
    and the first pass reported it missing in all three products."""
    src = "    public bool IsSignedIn => !string.IsNullOrEmpty(Pid);"
    found = set()
    for pattern in DECLARES["csharp"]:
        found |= set(re.findall(pattern, src))
    assert "IsSignedIn" in found


def test_a_qualified_return_type_is_a_declaration():
    """`Task<System.Collections.Generic.Dictionary<string, bool>>` has dots in
    it. Without them in the pattern this file reported `Features` and
    `SetFeature` missing from a client that declares both, on the first run
    of the widened check."""
    src = ("    public Task<System.Collections.Generic.Dictionary<string, bool>> "
           "Features(string pid, string token) =>")
    found = set()
    for pattern in DECLARES["csharp"]:
        found |= set(re.findall(pattern, src))
    assert "Features" in found


def test_prose_about_a_member_is_not_a_use(tmp_path):
    """A comment naming `state.somethingGone` is a sentence, and reporting it
    would be this file inventing a defect out of its own documentation."""
    view = tmp_path / "View.swift"
    view.write_text("/// Reads state.somethingGone, which no longer exists.\n"
                    "let x = state.uid\n")
    assert set(re.findall(r'\bstate\.(\w+)', _code(view))) == {"uid"}


def test_the_declaring_file_is_not_read_back(tmp_path):
    """`ApiClient.swift` names its own members constantly. Counting those as
    calls would make every client row compare a set against itself."""
    root = tmp_path / "Sources"
    root.mkdir()
    (root / "ApiClient.swift").write_text("let x = ApiClient.shared.onlyHere\n")
    (root / "HomeView.swift").write_text("let y = ApiClient.shared.listRooms()\n")
    reached = _reached(r'\bApiClient\.shared\.(\w+)', root, (".swift",),
                       "ApiClient.swift")
    assert sorted(reached) == ["listRooms"]


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
    declared = _declared("swift", state)
    reached = _reached(r'\bstate\.(\w+)', view, (".swift",), "AppState.swift")
    assert "uid" in declared and "userId" not in declared
    assert sorted(set(reached) - declared) == ["userId"]


def test_the_theme_check_can_fail(tmp_path):
    """0.58.2's defect, verbatim: one card colour declared, a second painted
    with. Kotlin calls this an unresolved reference and stops."""
    theme = tmp_path / "Theme.kt"
    theme.write_text("object Qrme {\n"
                     "    val Card = Color(0xFF182238)\n"
                     "}\n")
    screens = tmp_path / "ui"
    screens.mkdir()
    (screens / "Screens.kt").write_text(
        "    Card(colors = CardDefaults.cardColors("
        "containerColor = Qrme.Card2)) {\n")
    declared = _declared("kotlin", theme)
    reached = _reached(r'\bQrme\.(\w+)', screens, (".kt",), "Theme.kt")
    assert sorted(set(reached) - declared) == ["Card2"]


def test_the_brush_check_can_fail(tmp_path):
    """A page painting with a key `App.xaml` never declared."""
    win = tmp_path / "native/windows"
    win.mkdir(parents=True)
    (win / "App.xaml").write_text(
        '<Application><SolidColorBrush x:Key="QrmeCardBrush" Color="#182238"/>'
        '</Application>\n')
    (win / "HomePage.xaml").write_text(
        '<Page Background="{StaticResource QrmeCard2Brush}" />\n')
    keys, used = _brushes(tmp_path)
    assert sorted(set(used) - keys) == ["QrmeCard2Brush"]


def test_a_brush_named_in_a_ternary_is_a_use(tmp_path):
    """`Resources[valid ? "QrmeGreenBrush" : "QrmeRedBrush"]` — the page
    paints with both, and reading only the first would let the other rot."""
    win = tmp_path / "native/windows"
    win.mkdir(parents=True)
    (win / "App.xaml").write_text('<Application />\n')
    (win / "SignaturesPage.xaml.cs").write_text(
        'target.Foreground = (SolidColorBrush)Application.Current.Resources[\n'
        '    valid ? "QrmeGreenBrush" : "QrmeRedBrush"];\n')
    _keys, used = _brushes(tmp_path)
    assert sorted(used) == ["QrmeGreenBrush", "QrmeRedBrush"]
