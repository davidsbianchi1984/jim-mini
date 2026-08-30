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

#: Calls that hand back what they were given, or a constant from a table
#: in this repository — never anything a reader supplied. Safe exactly
#: when their arguments are, which is why they are a separate set from
#: ESCAPERS: an escaper makes anything safe, and these make nothing safe.
TRANSPARENT = {"t", "tr", "tr_page", "_t"}
NUMERIC = {"len", "int", "float", "round", "sum", "min", "max", "abs"}

def _callee(node):
    f = node.func
    while isinstance(f, ast.Attribute):
        return f.attr
    return f.id if isinstance(f, ast.Name) else ""

#: Calls that read a list without changing it. A name handed to one of
#: these is still a name this analysis has seen every element of.
READ_ONLY = {"join", "len", "sorted", "reversed", "enumerate", "sum", "any",
             "all", "max", "min"}


class Scope:
    def __init__(self, module_safe):
        self.bound = {}
        self.grown = {}
        self.spoiled = set()
        self.module_safe = module_safe

    def learn(self, fn, skip=frozenset()):
        """Read one scope's assignments, and every mutation of a name in it.

        The bindings alone are not enough, and saying so cost a round. A list
        built as a literal and then appended to reads, to a scan that looks
        only at the assignment, as the literal it started as — so
        `out = []` followed by `out.append(request.args["q"])` would answer
        *safe*, having never seen the line that matters.

            asked     what was this name assigned
            mattered  what is in it by the time it is printed

        So `append` and `extend` are collected as more elements, and anything
        else that touches the name spoils it: a subscript assignment, a
        method this does not model, a pass into a call that could append
        inside. An unmodelled mutation must never read as safety.
        """
        for node in ast.walk(fn):
            if id(node) in skip:
                continue
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target = node.targets[0]
                if isinstance(target, ast.Name):
                    self.bound[target.id] = node.value
                elif isinstance(target, ast.Subscript) \
                        and isinstance(target.value, ast.Name):
                    self.spoiled.add(target.value.id)
            elif isinstance(node, ast.AugAssign) \
                    and isinstance(node.target, ast.Name):
                self.grown.setdefault(node.target.id, []).append(node.value)
            elif isinstance(node, ast.Call):
                f = node.func
                if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
                    if f.attr in ("append", "extend"):
                        self.grown.setdefault(f.value.id, []).extend(node.args)
                    else:
                        self.spoiled.add(f.value.id)
                if _callee(node) not in READ_ONLY:
                    for arg in node.args:
                        if isinstance(arg, ast.Name):
                            self.spoiled.add(arg.id)

    def _accumulator(self, name):
        """A name this analysis is treating as a container it has read.

        Spoiling matters for those and only those: a list can be appended to
        behind this scan's back, and a string cannot. Applying it to every
        name reported `card`, `html` and `language` as unreadable the moment
        any of them was passed to a function, which is a false alarm and the
        fastest way to make a record nobody reads.
        """
        if name in self.grown:
            return True
        b = self.bound.get(name)
        return isinstance(b, (ast.List, ast.Tuple))

    def safe(self, node, depth=0):
        # Ten, not six. A join over a comprehension over an f-string over an
        # escape is five levels before the answer, and six cut it off one
        # short — reporting a safe expression because the walk gave up
        # inside it rather than because anything was wrong.
        if depth > 10:
            return False
        if isinstance(node, ast.Constant):
            return True
        if isinstance(node, ast.Name):
            if node.id in self.spoiled and self._accumulator(node.id):
                return False
            b = self.bound.get(node.id)
            if b is None or not self.safe(b, depth + 1):
                return False
            return all(self.safe(g, depth + 1)
                       for g in self.grown.get(node.id, ()))
        if isinstance(node, ast.Call):
            name = _callee(node)
            if name in ESCAPERS or name in NUMERIC:
                return True
            if name in self.module_safe:
                return True
            if name == "join" and isinstance(node.func, ast.Attribute):
                return all(self.safe(a, depth + 1) for a in node.args)
            # A translator is transparent, not an escaper. `tr_page` returns
            # either the text it was handed — a literal at the call site — or
            # a value from `_PAGE_STRINGS`, which is a table in this
            # repository. So its answer is safe exactly when its argument is,
            # and `t(user_input)` is still reported.
            #
            #     asked     does the name look like a translator
            #     mattered  can anything a reader typed come back out of it
            if name in TRANSPARENT:
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
        # `"".join(f"<b>{escape(x)}</b>" for x in xs)` — the join above
        # asks whether its argument is safe, and its argument is the
        # comprehension. A comprehension is safe when the thing it builds is
        # safe: the loop is over a sequence, and every element it yields is
        # that one expression.
        if isinstance(node, (ast.GeneratorExp, ast.ListComp, ast.SetComp)):
            return self.safe(node.elt, depth + 1)
        # A list built up and then joined. Every element of the literal and
        # every value appended or extended onto it has to be safe, and the
        # name must not be touched any other way — a subscript assignment, a
        # pass into some other call, an `insert` this does not model. An
        # unmodelled mutation would make this answer "safe" about a list it
        # has not seen all of, which is the one failure mode that matters
        # here, so anything unrecognised disqualifies the whole name.
        if isinstance(node, (ast.List, ast.Tuple)):
            return all(self.safe(e, depth + 1) for e in node.elts)
        if isinstance(node, ast.JoinedStr):
            return all(self.safe(v.value, depth + 1) if isinstance(v, ast.FormattedValue)
                       else True for v in node.values)
        # `_TEMPLATE % {"endpoint": _js(...), "strings": ...}` — the BinOp
        # above asks about both sides, and the right-hand side of a percent
        # format is the mapping. Safe when every value in it is.
        if isinstance(node, ast.Dict):
            return all(v is not None and self.safe(v, depth + 1)
                       for v in node.values)
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
            sc.learn(fn)
            rets = [n.value for n in ast.walk(fn)
                    if isinstance(n, ast.Return) and n.value is not None]
            if rets and all(sc.safe(r) for r in rets):
                safe.add(fn.name); grew = True
        if not grew:
            break
    return safe

def imported_privates(root: pathlib.Path) -> set[str]:
    """Underscore-named things some other module imports.

    A private function's callers can all be read, which is what lets the
    parameter check below work at all. That is only true while the name
    stays inside its module, so the one thing that would make it false is
    looked for rather than assumed.
    """
    taken = set()
    for path in root.rglob("*.py"):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                taken.update(a.name for a in node.names
                             if a.name.startswith("_"))
    return taken


def _bind_safe_parameters(tree, scopes, borrowed):
    """Trust a private function's parameter when every caller passes safety.

    `_page(title, body, language)` interpolates `body` straight into the
    document, and no amount of reading `_page` can say whether that is safe
    — the answer is at the three call sites, each of which composes a body
    out of escaped parts. Read only inside the function, it is an
    unresolvable parameter, and it sat in the record as one.

        asked     is this value escaped where it is printed
        mattered  is it escaped everywhere it comes from

    Sound only for a name that cannot be called from outside: private, and
    imported nowhere else. Everything else keeps its parameters unknown.
    """
    funcs = {n.name: n for n in ast.walk(tree)
             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    callers = {}

    def visit(node, holder):
        """Every call, charged to the scope it is actually written in.

        `ast.walk` from each function *and* from the module reaches the same
        call several times, so a call inside a function was also read as a
        call at module level — where the local it passes is an unresolvable
        name, and the argument therefore never safe. Innermost owner only.
        """
        here = holder
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            here = node
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id in funcs:
            callers.setdefault(node.func.id, []).append((here, node))
        for child in ast.iter_child_nodes(node):
            visit(child, here)

    visit(tree, tree)

    for name, fn in funcs.items():
        if not name.startswith("_") or name in borrowed:
            continue
        sites = callers.get(name)
        if not sites:
            continue
        names = [a.arg for a in fn.args.args]
        # Defaults cover the tail of the signature.
        defaults = dict(zip(names[len(names) - len(fn.args.defaults):],
                            fn.args.defaults))
        for position, arg in enumerate(names):
            passed = []
            for holder, call in sites:
                if position < len(call.args):
                    passed.append((holder, call.args[position]))
                    continue
                keyword = [k for k in call.keywords if k.arg == arg]
                if keyword:
                    passed.append((holder, keyword[0].value))
                elif arg in defaults:
                    passed.append((holder, defaults[arg]))
                else:
                    passed = None
                    break
            if passed and all(scopes[id(h)].safe(e) for h, e in passed):
                scopes[id(fn)].bound[arg] = ast.Constant(value="")


def rows(root: pathlib.Path):
    out = []
    borrowed = imported_privates(root)
    for path in sorted(root.rglob("*.py")):
        if "/tests/" in str(path) or path.name.startswith("test_"):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        helpers = module_safe_helpers(tree)
        funcs = [n for n in ast.walk(tree)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        # The bindings written at module level, seen by every function.
        # Without these a module constant — a stylesheet, a template — is an
        # unresolvable Name *inside* a function, and was reported forever.
        module_bound = {}
        for node in tree.body:
            if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                    and isinstance(node.targets[0], ast.Name):
                module_bound[node.targets[0].id] = node.value
        # Each function is scanned once, in its own scope. The module scope
        # scans only what is NOT inside a function: walking the whole tree
        # again merged every function's assignments into one table, so a name
        # written safely in one function and unsafely in another took the
        # unsafe binding and was reported — a row for a line that is correct.
        inside = {id(n) for fn in funcs for n in ast.walk(fn)}
        scopes = {}
        for fn in funcs + [tree]:
            sc = Scope(helpers)
            sc.bound.update(module_bound)
            sc.learn(fn, skip=inside if fn is tree else frozenset())
            scopes[id(fn)] = sc
        _bind_safe_parameters(tree, scopes, borrowed)
        for fn in funcs + [tree]:
            sc = scopes[id(fn)]
            module_pass = fn is tree
            for node in ast.walk(fn):
                if module_pass and id(node) in inside:
                    continue
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
    """Run the sweep over a string, for the units below.

    The parse is checked here rather than left to `rows`, which skips a file
    it cannot read. That is right for a sweep over a package — one
    unparseable file must not stop the other four hundred — and wrong for a
    unit test, where it turns a sample with a typo in it into a sample with
    no findings. Two of the samples below were written with an f-string
    Python 3.11 cannot parse, and both of the *negative* tests using them
    passed while proving nothing at all.

        asked     did the sweep find anything in this sample
        mattered  did the sweep read this sample
    """
    import tempfile
    ast.parse(source)
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


# --- what 2.7.2 taught the sweep to follow ----------------------------------
#
# Five of PDI's rows, two of QRME's and one of JIM-mini's were composites the
# analysis could not walk: a join over a comprehension, a list built by
# `append`, a translated template, a private function's parameter. Each pair
# below is the widening and the thing it must still catch — because a sweep
# that learns to follow a safe shape has learned to walk past the unsafe one
# wearing it.
#
#     asked     can the sweep follow this
#     mattered  does it still stop at the one that matters


def test_a_join_over_a_comprehension_is_followed():
    assert not _analyse(
        'import html\n'
        'def page(names):\n'
        '    rows = "".join(f"<li>{html.escape(n)}</li>" for n in names)\n'
        '    return f"<ul>{rows}</ul>"\n')


def test_a_join_over_a_comprehension_that_escapes_nothing_is_caught():
    assert _analyse(
        'def page(names):\n'
        '    rows = "".join(f"<li>{n}</li>" for n in names)\n'
        '    return f"<ul>{rows}</ul>"\n')


def test_a_list_built_by_append_is_followed():
    assert not _analyse(
        'import html\n'
        'def page(name, note):\n'
        '    out = [f"<b>{html.escape(name)}</b>"]\n'
        '    out.append(f"<i>{html.escape(note)}</i>")\n'
        '    joined = "".join(out)\n'
        '    return f"<div>{joined}</div>"\n')


def test_an_unescaped_append_is_caught():
    """The reason the bindings alone were not enough.

    A scan that reads only the assignment sees the safe literal this list
    started as and never reaches the line that put a reader's words in it.
    """
    assert _analyse(
        'import html\n'
        'def page(name, note):\n'
        '    out = [f"<b>{html.escape(name)}</b>"]\n'
        '    out.append(f"<i>{note}</i>")\n'
        '    joined = "".join(out)\n'
        '    return f"<div>{joined}</div>"\n')


def test_a_list_touched_a_way_this_does_not_model_is_caught():
    """Anything unmodelled has to read as unknown, not as safe."""
    assert _analyse(
        'import html\n'
        'def page(name, note):\n'
        '    out = [f"<b>{html.escape(name)}</b>"]\n'
        '    out.insert(0, note)\n'
        '    joined = "".join(out)\n'
        '    return f"<div>{joined}</div>"\n')


def test_a_translated_template_is_followed():
    assert not _analyse(
        'import html\n'
        'def page(t, holder):\n'
        '    who = t("This belongs to {h}.").format(h=html.escape(holder))\n'
        '    return f"<p>{who}</p>"\n')


def test_a_translator_handed_a_readers_words_is_caught():
    """A translator is transparent, not an escaper. `tr_page` answers with
    the text it was given when it has no translation for it, so anything a
    reader can put in comes straight back out."""
    assert _analyse(
        'def page(t, whatever):\n'
        '    return f"<p>{t(whatever)}</p>"\n')


def test_a_private_functions_parameter_is_read_at_its_call_sites():
    assert not _analyse(
        'import html\n'
        'def _shell(body):\n'
        '    return f"<main>{body}</main>"\n'
        'def page(name):\n'
        '    return _shell(f"<h1>{html.escape(name)}</h1>")\n')


def test_one_unsafe_call_site_condemns_the_parameter():
    """Every caller, not any caller: the parameter is as safe as the worst
    thing anybody passes to it."""
    assert _analyse(
        'import html\n'
        'def _shell(body):\n'
        '    return f"<main>{body}</main>"\n'
        'def page(name):\n'
        '    return _shell(f"<h1>{html.escape(name)}</h1>")\n'
        'def other(raw):\n'
        '    return _shell(f"<h1>{raw}</h1>")\n')


def test_a_public_functions_parameter_is_never_assumed():
    """The call-site reading is sound only for a name that cannot be called
    from outside the module. A public one keeps its parameters unknown."""
    assert _analyse(
        'import html\n'
        'def shell(body):\n'
        '    return f"<main>{body}</main>"\n'
        'def page(name):\n'
        '    return shell(f"<h1>{html.escape(name)}</h1>")\n')
