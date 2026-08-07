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
"""

import pathlib
import re
from collections import Counter

REPO = pathlib.Path(__file__).resolve().parents[2]

SWIFT = sorted(REPO.glob("native/ios/Sources/**/*.swift"))
KOTLIN = sorted(REPO.glob("native/android/**/*.kt"))
CSHARP = sorted(REPO.glob("native/windows/**/*.cs"))

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


# --- the checks have to be able to see, and to fail --------------------------

def test_there_are_shell_sources_to_read():
    """A glob that matched nothing would report three clean shells by finding
    none of them — the failure this whole arc keeps producing."""
    assert len(SWIFT) >= 24, len(SWIFT)
    assert len(KOTLIN) >= 6, len(KOTLIN)
    assert len(CSHARP) >= 18, len(CSHARP)


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


def test_the_brace_check_can_fail(tmp_path):
    open_file = tmp_path / "Open.swift"
    open_file.write_text('struct A {\n    var x = 0\n')
    closed = tmp_path / "Closed.swift"
    closed.write_text('struct A {\n    var x = "}"\n}\n')
    assert _unbalanced([open_file])
    assert not _unbalanced([closed]), "a brace inside a string is not a brace"
