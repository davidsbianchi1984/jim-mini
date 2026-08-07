"""Nothing here builds the phones, so nothing here notices when they stop.

0.57.4 shipped a fix and a defect in the same release. Renaming iOS's `venue`
to `locality` collided with a `locality` already declared in the same
`TradeSection`:

    @State private var locality = ""      // the place card's
    ...
    @State private var locality = ""      // the listing card's

Two stored properties of one name in one type does not compile. It reached
`main` and sat there for a release, and the reason is worth writing down
rather than apologising for: **every guard in this repo reads these files as
text.** The request-body guard extracts call shapes, the response guards
extract declarations — none of them parse, so none of them can see a syntax
error. `tsc --noEmit` covers the console. There is no Swift, Kotlin or C#
toolchain on this machine, so there is nothing to run.

    asked     do the shells say the right things to the server
    mattered  do the shells still compile

This file does not typecheck anything, and says so plainly. It checks the one
class of breakage that is invisible to a text-reading guard, cheap to detect
without a compiler, and *certain* to stop a build: a name declared twice in
one scope, and braces that do not balance.

That is a narrow claim. A green run here does not mean the shells build; it
means they do not contain the specific mistake that got past everything else.
Narrow and true beats broad and hopeful — the whole arc since 0.56.4 has been
guards that measured slightly the wrong thing and passed.

## 0.57.6 — and the file it never opened

The paragraph above is exactly right about what it checks and exactly wrong
about what "the shells" are. It globs `*.swift`, `*.kt` and `*.cs`, calls that
three shells, and reports them parseable. The Windows shell's **screens are
not C#.** They are XAML — 1,900 lines of it here, more than every `.cs` file
in `Views/` put together — and the code-behind is the smaller half of each
page. This file read the half that happened to look like the other two shells
and pronounced on the whole thing.

Five pages across two products do not parse. Three of the five are here. Each one is a
single element carrying `x:Name` **twice**:

    <TextBlock x:Name="ConsentText" TextWrapping="Wrap" FontSize="12"
               Foreground="{StaticResource QrmeT2Brush}"
               x:Name="NothingNote" />

Duplicate attributes are forbidden by XML itself, so this is not a subtle
XAML rule — no conformant reader gets past the tag, and the build stops at
`MC3050`. It is the 0.57.4 defect in markup, arrived at the same way: a
second name was needed, and it was added to the element that was there
instead of to an element of its own.

    asked     do the files that look like code still parse
    mattered  do the shells' screens still parse

Four checks, all of them things a XAML compiler refuses outright rather than
things a reviewer would prefer: the file is well-formed XML; no two elements
in one page share a name; every handler a page names exists in its
code-behind; every control the code-behind drives is named in the page. The
last is `CS0103` — the code-behind's fields *are* the `x:Name`s, so a name
that is not in the markup is not a field, and setting `.Text` on it does not
compile.
"""

import pathlib
import re
import xml.etree.ElementTree as ET
from collections import Counter

REPO = pathlib.Path(__file__).resolve().parents[2]

SWIFT = sorted(REPO.glob("native/ios/Sources/**/*.swift"))
KOTLIN = sorted(REPO.glob("native/android/**/*.kt"))
CSHARP = sorted(REPO.glob("native/windows/**/*.cs"))
#: The half of the Windows shell that is not C#, and was not being read.
XAML = sorted(REPO.glob("native/windows/**/*.xaml"))

#: `struct X: View {`, `final class Y {`, `extension Z {`
SWIFT_SCOPE = re.compile(r'\b(?:struct|class|enum|actor)\s+(\w+)[^{\n]*\{')
#: a stored property at this type's own indent, attributes and all
SWIFT_MEMBER = re.compile(
    r'^\s{4}(?:@\w+(?:\([^)]*\))?\s+)*'
    r'(?:private\s+|fileprivate\s+|public\s+|internal\s+)*(?:var|let)\s+(\w+)',
    re.M)
KOTLIN_SCOPE = re.compile(r'\bfun\s+(\w+)\s*\([^{]*\{')
#: Compose state. Two of these with one name in a composable is the same bug.
KOTLIN_MEMBER = re.compile(r'^\s+var\s+(\w+)\s+by\s+remember', re.M)
CSHARP_SCOPE = re.compile(r'\b(?:class|struct)\s+(\w+)[^{;\n]*\{')
CSHARP_MEMBER = re.compile(
    r'^\s{4}(?:public\s+|private\s+|internal\s+|protected\s+|static\s+|'
    r'readonly\s+)*[\w<>\[\]?,\s.]+?\s(\w+)\s*(?:=|;|\{\s*get)', re.M)


def _shown(path: pathlib.Path) -> str:
    """Repo-relative where it can be, absolute where it cannot — the brace
    check is exercised on a tmp file, and a helper that only knows how to
    name files inside the repo made the test that proves it can fail, fail."""
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def _skip_strings(text: str, i: int) -> int:
    """Past a string literal starting at `i`, or `i` unchanged."""
    if text[i] != '"':
        return i
    i += 1
    while i < len(text) and text[i] != '"':
        i += 2 if text[i] == "\\" else 1
    return i


def _scopes(src: str, header: re.Pattern):
    """(name, body) for each declaration `header` matches.

    The body is read by counting braces rather than by regex, because a
    regex that stops at the first `}` reports half a type — and a guard that
    reads half a type finds no duplicates in the other half.
    """
    for m in header.finditer(src):
        i = src.index("{", m.end() - 1)
        depth, j = 0, i
        while j < len(src):
            c = src[j]
            if c == '"':
                j = _skip_strings(src, j)
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        yield m.group(1), src[i + 1:j]


def _own_lines(body: str) -> str:
    """This scope's own lines, with everything nested inside removed.

    A property of an inner type is not a property of the outer one, and a
    `var` inside a closure is not a member at all.
    """
    out, depth = [], 0
    for ch in body:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                out.append("\n")
        elif depth == 0:
            out.append(ch)
    return "".join(out)


def _duplicates(paths, scope: re.Pattern, member: re.Pattern) -> list[str]:
    found = []
    for path in paths:
        src = path.read_text(encoding="utf-8")
        for name, body in _scopes(src, scope):
            counts = Counter(member.findall(_own_lines(body)))
            for declared, n in sorted(counts.items()):
                if n > 1:
                    found.append(f"{_shown(path)}: {name} declares "
                                 f"{declared!r} {n} times")
    return found


def _unbalanced(paths) -> list[str]:
    """Files whose braces do not close, ignoring strings and comments."""
    bad = []
    for path in paths:
        src = re.sub(r'/\*.*?\*/', '', path.read_text(encoding="utf-8"), flags=re.S)
        src = re.sub(r'(?<!:)//[^\n]*', '', src)
        depth, i = 0, 0
        while i < len(src):
            c = src[i]
            if c == '"':
                i = _skip_strings(src, i)
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth < 0:
                    bad.append(f"{_shown(path)}: a closing brace "
                               f"with nothing open")
                    break
            i += 1
        else:
            if depth:
                bad.append(f"{_shown(path)}: {depth} brace(s) left "
                           f"open at end of file")
    return bad


# --- the shell whose screens are markup --------------------------------------

#: `x:Name="Foo"`. In WinUI this is both the element's identity inside the page
#: and the name of the field the code-behind gets, which is why one pattern
#: answers two different questions below.
_XNAME = re.compile(r'\bx:Name\s*=\s*"(\w+)"')

#: `Click="OnGrant"`. A literal identifier only — `Click="{x:Bind Go}"` is a
#: binding resolved elsewhere and is deliberately not matched.
_HANDLER = re.compile(
    r'\b(Click|Checked|Unchecked|Toggled|SelectionChanged|TextChanged|Loaded'
    r'|ItemClick|Tapped|ValueChanged|QuerySubmitted|SuggestionChosen'
    r'|Completed|PointerPressed)\s*=\s*"([A-Za-z_]\w*)"')

#: Assigning one of these is assigning to a control. Kept short on purpose:
#: every name here belongs to a XAML element and to almost nothing else, so a
#: bare identifier on the left of it is a page control or a compile error.
_DRIVEN = re.compile(
    r'\b([A-Z]\w*)\.(?:Text|Visibility|IsEnabled|IsChecked|ItemsSource'
    r'|PlaceholderText|SelectedIndex|Content|Source|Children|Value|Maximum'
    r'|Minimum|Foreground|Background)\s*=')

#: Anything the code-behind declares for itself: a local, a field, a
#: parameter. Without this the check below reports every local variable that
#: happens to have a `.Text`, which is a finding about nothing.
_DECLARED = [
    re.compile(r'\b(?:var|[\w<>\[\],.?]+)\s+([A-Za-z_]\w*)\s*='),
    re.compile(r'\b(?:private|public|internal|protected|static|readonly)\s'
               r'[\w<>\[\],.?\s]*?\b(\w+)\s*[;=]'),
    re.compile(r'\(\s*[\w<>\[\],.?]+\s+(\w+)\s*[,)]'),
]


def _code_behind(path: pathlib.Path) -> str | None:
    """`Foo.xaml.cs` for `Foo.xaml`, or None. `App.xaml` has one; a page
    written entirely in markup may not."""
    cs = path.with_suffix(".xaml.cs")
    return cs.read_text(encoding="utf-8") if cs.exists() else None


def _malformed(paths) -> list[str]:
    """XAML is XML before it is anything else. A duplicate attribute, an
    unclosed tag or a stray `&` stops the compiler at the tag."""
    bad = []
    for path in paths:
        try:
            ET.fromstring(path.read_text(encoding="utf-8"))
        except ET.ParseError as exc:
            bad.append(f"{_shown(path)}: {exc}")
    return bad


def _renamed_twice(paths) -> list[str]:
    """Two elements in one page answering to one name.

    The markup form of 0.57.4. A page is a single namescope, so this is not a
    shadowing question — it is two fields of one name on the generated
    partial class, which does not compile.
    """
    found = []
    for path in paths:
        counts = Counter(_XNAME.findall(path.read_text(encoding="utf-8")))
        for name, n in sorted(counts.items()):
            if n > 1:
                found.append(f"{_shown(path)}: {name!r} names {n} elements")
    return found


def _handlers(paths) -> tuple[int, list[str]]:
    """(how many were checked, the ones with nothing behind them)."""
    seen, missing = 0, []
    for path in paths:
        body = _code_behind(path)
        if body is None:
            continue
        for event, handler in _HANDLER.findall(path.read_text(encoding="utf-8")):
            seen += 1
            if not re.search(r'\b(?:void|Task)\s+%s\s*\(' % re.escape(handler),
                             body):
                missing.append(f"{_shown(path)}: {event}=\"{handler}\" has no "
                               f"method of that name behind it")
    return seen, missing


def _undriveable(paths) -> tuple[int, list[str]]:
    """(how many were checked, controls the code-behind drives and the page
    never names).

    The code-behind's controls are not declared in the code-behind — the XAML
    compiler generates them from `x:Name`. So a name only the `.cs` knows is
    not a field at all, and `Foo.Text = …` is `CS0103`.
    """
    seen, loose = 0, []
    for path in paths:
        body = _code_behind(path)
        if body is None:
            continue
        named = set(_XNAME.findall(path.read_text(encoding="utf-8")))
        own = {n for rx in _DECLARED for n in rx.findall(body)}
        for name in sorted(set(_DRIVEN.findall(body))):
            seen += 1
            if name not in named and name not in own:
                loose.append(f"{_shown(path)}: the code behind drives "
                             f"{name!r}, which this page never names")
    return seen, loose


# --- the guard ---------------------------------------------------------------

def test_no_swift_type_declares_one_name_twice():
    """The 0.57.4 defect. Two `@State` properties called `locality` in one
    `TradeSection`, shipped to main, invisible to every other guard here."""
    dups = _duplicates(SWIFT, SWIFT_SCOPE, SWIFT_MEMBER)
    assert not dups, "\n    ".join([""] + dups)


def test_no_composable_remembers_one_name_twice():
    dups = _duplicates(KOTLIN, KOTLIN_SCOPE, KOTLIN_MEMBER)
    assert not dups, "\n    ".join([""] + dups)


def test_no_csharp_type_declares_one_name_twice():
    dups = _duplicates(CSHARP, CSHARP_SCOPE, CSHARP_MEMBER)
    assert not dups, "\n    ".join([""] + dups)


def test_every_shell_source_closes_its_braces():
    bad = _unbalanced(SWIFT + KOTLIN + CSHARP)
    assert not bad, "\n    ".join([""] + bad)


def test_every_windows_screen_is_well_formed_markup():
    """The 0.57.6 defect. Five pages across two products carried `x:Name`
    twice on one element, which no XML reader gets past."""
    bad = _malformed(XAML)
    assert not bad, "\n    ".join([""] + bad)


def test_no_windows_screen_names_two_elements_alike():
    """0.57.4 in markup: one page is one namescope, so two elements of one
    name are two fields of one name on the generated class."""
    dups = _renamed_twice(XAML)
    assert not dups, "\n    ".join([""] + dups)


def test_every_handler_a_screen_names_exists_behind_it():
    """A button whose `Click` names nothing does not fail at the press — the
    page fails to compile."""
    _, missing = _handlers(XAML)
    assert not missing, "\n    ".join([""] + missing)


def test_every_control_the_code_behind_drives_is_named_in_its_screen():
    """`CS0103`. The rename half of the fix, watched from the other side: a
    duplicate name struck from the markup and left in the `.cs` lands here."""
    _, loose = _undriveable(XAML)
    assert not loose, "\n    ".join([""] + loose)


# --- the checks have to be able to see, and to fail --------------------------

def test_there_are_shell_sources_to_read():
    """A glob that matched nothing would report three clean shells by finding
    none of them — the failure this whole arc keeps producing."""
    assert len(SWIFT) >= 24, len(SWIFT)
    assert len(KOTLIN) >= 6, len(KOTLIN)
    assert len(CSHARP) >= 18, len(CSHARP)


def test_the_markup_checks_reach_the_windows_screens():
    """The same floor, for the half of that shell this file used to skip.

    Counted rather than assumed: `_handlers` and `_undriveable` both quietly
    return `(0, [])` for a page whose code-behind they cannot find, and a
    green run over nothing is what this arc keeps producing.
    """
    assert len(XAML) >= 13, len(XAML)
    named = sum(len(set(_XNAME.findall(p.read_text(encoding="utf-8"))))
                for p in XAML)
    assert named >= 340, named
    checked, _ = _handlers(XAML)
    assert checked >= 80, checked
    driven, _ = _undriveable(XAML)
    assert driven >= 300, driven


def test_the_scope_reader_reaches_the_whole_type():
    """A regex that stops at the first `}` reads half a type, and half a type
    has no duplicates in the half it did not read."""
    src = ('struct A {\n'
           '    var x = 0\n'
           '    func f() { let y = 1 }\n'
           '    var x = 2\n'
           '}\n')
    name, body = next(_scopes(src, SWIFT_SCOPE))
    assert name == "A" and "var x = 2" in body


def test_a_nested_declaration_is_not_the_outer_scopes():
    """`var x` inside a closure is not a member, and a property of an inner
    type belongs to the inner type."""
    body = "    var a = 0\n    func f() {\n        var a = 1\n    }\n"
    assert SWIFT_MEMBER.findall(_own_lines(body)) == ["a"]


def test_the_duplicate_check_catches_the_defect_that_shipped():
    """Written from the real thing: 0.57.4's `TradeSection`."""
    src = ('struct TradeSection: View {\n'
           '    @State private var locality = ""\n'
           '    @State private var blurb = ""\n'
           '    @State private var locality = ""\n'
           '}\n')
    counts = Counter(SWIFT_MEMBER.findall(
        _own_lines(next(_scopes(src, SWIFT_SCOPE))[1])))
    assert counts["locality"] == 2


#: A page root, with the namespaces every real one declares. The
#: well-formedness check reads whole files — a fragment using `x:Name` with no
#: `xmlns:x` above it is unbound-prefix rather than the thing being tested,
#: which is a fixture that fails for its own reason.
_ROOT = ('<Page xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"'
         ' xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">\n%s</Page>\n')


def test_the_markup_check_catches_the_defect_that_shipped(tmp_path):
    """Written from the real thing: QRME's `VoicePage.xaml` at 0.57.5.

    The second `x:Name` was added because a second sentence was needed. It
    went onto the element that was already there instead of onto an element
    of its own, and the page stopped parsing.
    """
    page = tmp_path / "VoicePage.xaml"
    page.write_text(_ROOT % '  <TextBlock x:Name="ConsentText" FontSize="12"\n'
                             '             x:Name="NothingNote" />\n')
    bad = _malformed([page])
    assert bad and "duplicate attribute" in bad[0]


def test_the_markup_checks_pass_a_page_that_is_right(tmp_path):
    """The other half of a check that can fail: one that does not fire on
    the fix. Two sentences, two elements, two names."""
    page = tmp_path / "VoicePage.xaml"
    page.write_text(_ROOT % '  <TextBlock x:Name="ConsentText" FontSize="12" />\n'
                             '  <TextBlock x:Name="NothingNote" FontSize="12" />\n'
                             '  <Button x:Name="WithdrawButton" Click="OnWithdraw" />\n')
    (tmp_path / "VoicePage.xaml.cs").write_text(
        'class VoicePage {\n'
        '    void OnWithdraw() { }\n'
        '    void Render(bool ok) {\n'
        '        ConsentText.Text = "";\n'
        '        NothingNote.Text = "";\n'
        '        WithdrawButton.Visibility = ok ? V.Visible : V.Collapsed;\n'
        '    }\n'
        '}\n')
    assert not _malformed([page])
    assert not _renamed_twice([page])
    assert _handlers([page]) == (1, [])
    driven, loose = _undriveable([page])
    assert driven == 3 and not loose


def test_two_elements_of_one_name_are_caught(tmp_path):
    page = tmp_path / "Page.xaml"
    page.write_text(_ROOT % '  <TextBlock x:Name="Note" />\n'
                             '  <TextBlock x:Name="Note" />\n')
    assert not _malformed([page]), "well-formed — this is the XAML rule, not XML's"
    assert _renamed_twice([page]) == [f"{page}: 'Note' names 2 elements"]


def test_a_handler_with_nothing_behind_it_is_caught(tmp_path):
    page = tmp_path / "Page.xaml"
    page.write_text(_ROOT % '  <Button Click="OnGone" />\n')
    (tmp_path / "Page.xaml.cs").write_text('class P { void OnHere() { } }\n')
    seen, missing = _handlers([page])
    assert seen == 1 and len(missing) == 1 and "OnGone" in missing[0]


def test_a_control_the_page_never_names_is_caught(tmp_path):
    """And a local of the same shape is not — the filter that keeps this
    check from reporting every variable with a `.Text`."""
    page = tmp_path / "Page.xaml"
    page.write_text(_ROOT % '  <TextBlock x:Name="Kept" />\n')
    (tmp_path / "Page.xaml.cs").write_text(
        'class P {\n'
        '    void Go() {\n'
        '        Kept.Text = "";\n'
        '        Struck.Visibility = V.Collapsed;\n'
        '        var Block = new TextBlock();\n'
        '        Block.Text = "";\n'
        '    }\n'
        '}\n')
    _, loose = _undriveable([page])
    assert len(loose) == 1 and "'Struck'" in loose[0]


def test_the_brace_check_can_fail(tmp_path):
    open_file = tmp_path / "Open.swift"
    open_file.write_text('struct A {\n    var x = 0\n')
    closed = tmp_path / "Closed.swift"
    closed.write_text('struct A {\n    var x = "}"\n}\n')
    assert _unbalanced([open_file])
    assert not _unbalanced([closed]), "a brace inside a string is not a brace"
