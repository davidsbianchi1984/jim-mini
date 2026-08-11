"""A page never prints what it was given.

0.59.3 found reflected cross-site scripting on the sign-in callback by
sweeping every f-string that builds markup — by hand, once, and then throwing
the sweep away. Escaping is the first line of defence and the policy is the
second; that round shipped the second and left the first unguarded.

    asked     is this page correct
    mattered  can the next value somebody interpolates be markup

## What the sweep does

It walks every f-string in this package whose literal parts contain real
markup, and reports each interpolation whose expression does not reach an
escape. "Reaches" is followed properly rather than looked for on the same
line, because most of this estate escapes one line above the template:

    ref = html.escape(card["reference"])
    body = f'<p class="ref">{ref}</p>'

A sweep that only asked whether `html.escape` appears inside the braces
reported 32 rows in this product, of which six were the defect and the rest
were that pattern. Following single assignments, and functions whose every
return is escaped, cuts it to eight — and all eight are composites the
analysis cannot follow rather than values anybody reads.

## Two things it deliberately does not do

**It does not read prose as markup.** The first draft matched any f-string
containing `<` and `>`, which flagged a WebAuthn diagnostic containing
`http://localhost:<port>`. It now wants a closing tag, or an opening tag
carrying an attribute.

**It does not decide.** The rows below are recorded, not fixed. Whether
`{body}` is safe depends on how `body` was built three functions ago, and
that is a reading a person does once and writes down — which is what the
record is for. What the ratchet guarantees is that the **next** one fails on
the day it is written rather than four hundred releases later.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from . import ratchets

#: A closing tag, or an opening tag carrying an attribute. Prose with angle
#: brackets in it — 'http://localhost:<port>' — is not markup, and the first
#: draft of this sweep reported it as such.
MARKUP = re.compile(r'</[a-zA-Z]|<[a-zA-Z][\w-]*\s+[\w-]+=')

ESCAPERS = {"escape", "quote", "quoteattr", "urlencode", "_js", "b64encode"}
NUMERIC = {"len", "int", "float", "round", "sum", "min", "max", "abs"}

def _callee(node):
    f = node.func
    while isinstance(f, ast.Attribute):
        return f.attr
    return f.id if isinstance(f, ast.Name) else ""

class Scope:
    def __init__(self, module_safe):
        self.bound = {}
        self.module_safe = module_safe

    def safe(self, node, depth=0):
        if depth > 6:
            return False
        if isinstance(node, ast.Constant):
            return True
        if isinstance(node, ast.Name):
            b = self.bound.get(node.id)
            return b is not None and self.safe(b, depth + 1)
        if isinstance(node, ast.Call):
            name = _callee(node)
            if name in ESCAPERS or name in NUMERIC:
                return True
            if name in self.module_safe:
                return True
            if name == "join" and isinstance(node.func, ast.Attribute):
                return all(self.safe(a, depth + 1) for a in node.args)
            if name == "format":
                return all(self.safe(k.value, depth + 1) for k in node.keywords) \
                    and all(self.safe(a, depth + 1) for a in node.args) \
                    and self.safe(node.func.value, depth + 1)
            return False
        if isinstance(node, ast.IfExp):
            return self.safe(node.body, depth + 1) and self.safe(node.orelse, depth + 1)
        if isinstance(node, ast.BoolOp):
            return all(self.safe(v, depth + 1) for v in node.values)
        if isinstance(node, (ast.BinOp,)):
            return self.safe(node.left, depth + 1) and self.safe(node.right, depth + 1)
        if isinstance(node, ast.JoinedStr):
            return all(self.safe(v.value, depth + 1) if isinstance(v, ast.FormattedValue)
                       else True for v in node.values)
        if isinstance(node, (ast.Compare,)):
            return True
        return False

def module_safe_helpers(tree):
    """Functions in this module whose every return is escaped output."""
    safe = set()
    for _ in range(3):                       # let helpers build on helpers
        grew = False
        for fn in [n for n in ast.walk(tree)
                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            if fn.name in safe:
                continue
            sc = Scope(safe)
            for node in ast.walk(fn):
                if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                        and isinstance(node.targets[0], ast.Name):
                    sc.bound[node.targets[0].id] = node.value
            rets = [n.value for n in ast.walk(fn)
                    if isinstance(n, ast.Return) and n.value is not None]
            if rets and all(sc.safe(r) for r in rets):
                safe.add(fn.name); grew = True
        if not grew:
            break
    return safe

def rows(root: pathlib.Path):
    out = []
    for path in sorted(root.rglob("*.py")):
        if "/tests/" in str(path) or path.name.startswith("test_"):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        helpers = module_safe_helpers(tree)
        for fn in [n for n in ast.walk(tree)
                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))] + [tree]:
            sc = Scope(helpers)
            for node in ast.walk(fn):
                if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                        and isinstance(node.targets[0], ast.Name):
                    sc.bound[node.targets[0].id] = node.value
            for node in ast.walk(fn):
                if not isinstance(node, ast.JoinedStr):
                    continue
                lits = "".join(p.value for p in node.values
                               if isinstance(p, ast.Constant))
                if not MARKUP.search(lits):
                    continue
                for part in node.values:
                    if not isinstance(part, ast.FormattedValue):
                        continue
                    if sc.safe(part.value):
                        continue
                    # File and expression, deliberately **not** the line
                    # number. 0.59.4 recorded the line and 0.59.5 invalidated
                    # every row in this product by adding one function above
                    # them — a record that goes stale on an unrelated edit is
                    # a record people regenerate without reading, which is the
                    # one thing it must not become.
                    #
                    # The cost is a second identical expression in the same
                    # file reading as already-recorded. That is a narrower
                    # blind spot than a record nobody reads.
                    out.append(f"{path.relative_to(root)}: "
                               f"{{{ast.unparse(part.value)[:70]}}}")
    return sorted(set(out))

def _repo_package() -> Path:
    """The product package this suite belongs to.

    Spelled out rather than derived: this product's tests sit *inside* the
    package and QRME's sit *beside* it, so `parent.parent` means two
    different things in three repositories. Getting that wrong in either
    direction is silent — one way sweeps the whole checkout, the other sweeps
    a directory that does not exist and reports nothing at all, which is why
    the floor below exists.
    """
    return Path(__file__).resolve().parent.parent


TESTS = Path(__file__).resolve().parent
RECORD = TESTS / "unescaped_markup.txt"


def scanned() -> int:
    """How many markup f-strings the sweep can see.

    The sweep's own liveness, and deliberately not the row count: that is a
    backlog being paid down, so a floor under it would fail on the good news.
    """
    total = 0
    for path in sorted(_repo_package().rglob("*.py")):
        if "/tests/" in str(path) or path.name.startswith("test_"):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.JoinedStr):
                lits = "".join(p.value for p in node.values
                               if isinstance(p, ast.Constant))
                if MARKUP.search(lits):
                    total += 1
    return total


def _recorded() -> set[str]:
    return {line.strip() for line in RECORD.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


def _ceiling() -> int:
    return int(re.search(r"# ceiling: (\d+)",
                         RECORD.read_text(encoding="utf-8")).group(1))


def test_no_page_interpolates_something_new_without_escaping_it():
    """The next one, caught on the day it is written.

    `?error=<script>…` on the sign-in callback shipped for four hundred
    releases. What made it invisible was not that it was hard to see — it is
    three lines of obvious — but that nothing was looking.
    """
    found = rows(_repo_package())
    ceiling = _ceiling()
    fresh = sorted(set(found) - _recorded())
    assert len(found) <= ceiling, (
        f"{len(found)} unescaped interpolations into markup, above the "
        f"{ceiling} recorded:\n    " + "\n    ".join(fresh[:20])
        + "\n  Escape it where it is interpolated. If it is already escaped "
          "somewhere the analysis cannot follow, record the row and say so — "
          "recording is ratcheted.")


def test_the_record_matches_what_is_actually_there():
    """A record that has drifted from the code makes the ceiling a number
    about a file rather than about the product."""
    found, recorded = set(rows(_repo_package())), _recorded()
    stale = sorted(recorded - found)
    assert not stale, (
        f"{len(stale)} recorded row(s) are gone or moved — strike them from "
        "unescaped_markup.txt:\n    " + "\n    ".join(stale[:20]))


def test_the_sweep_is_actually_reading_pages():
    """A sweep that stopped matching would report no unescaped interpolations
    and a clean bill — the failure this whole session keeps finding."""
    seen = scanned()
    assert seen >= ratchets.floor("markup.strings_scanned"), (
        f"the sweep found only {seen} markup f-strings — it has stopped "
        "matching, and a backlog that shrinks because nothing was read looks "
        "exactly like one that was paid down")


def _analyse(source: str) -> list[str]:
    """Run the sweep over a string, for the units below."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        (d / "sample.py").write_text(source, encoding="utf-8")
        return rows(d)


def test_an_unescaped_value_is_caught():
    """The defect, as a unit, in the shape it actually took."""
    assert _analyse(
        'def page(error):\n'
        '    return f"<p class=\'e\'>{error} — try again</p>"\n')


def test_an_escaped_value_is_not():
    assert not _analyse(
        'import html\n'
        'def page(error):\n'
        '    return f"<p class=\'e\'>{html.escape(error)}</p>"\n')


def test_the_analysis_follows_a_name_to_its_escape():
    """The pattern most of this estate uses, and the reason a same-line check
    reported four times as many rows as there are."""
    assert not _analyse(
        'import html\n'
        'def page(card):\n'
        '    ref = html.escape(card["reference"])\n'
        '    return f"<p class=\'ref\'>{ref}</p>"\n')


def test_a_helper_whose_returns_are_all_escaped_is_followed_too():
    assert not _analyse(
        'import html\n'
        'def _row(v):\n'
        '    return html.escape(v)\n'
        'def page(v):\n'
        '    return f"<td class=\'c\'>{_row(v)}</td>"\n')


def test_prose_with_angle_brackets_is_not_markup():
    """`http://localhost:<port>` is a sentence. The first draft called it a
    page and reported the diagnostic around it as an injection."""
    assert not _analyse(
        'def hint(host):\n'
        '    return f"Reach this page on http://localhost:<port> not {host}"\n')


def test_a_value_cannot_close_the_script_element_it_sits_in():
    """`json.dumps` escapes what would end a *JS string*; the HTML parser
    ends the element at the first `</script` regardless of quoting. The
    helper escapes both layers, and the test stands in all three suites,
    because the copy that drifted was the one whose entire job is to be
    safe — and a guard that only exists where the bug never was guards
    nothing."""
    from jim import landing
    out = landing._js("</script><svg onload=x>")
    assert "</script" not in out
