"""The key was right and the shape was wrong.

0.58.3 checked that every key a shell decodes is one the backend can send. It
found four live breaks and left a named gap: the check is a *union*, so a key
read off the wrong response passes. The obvious next step was to bind each
decode site to the route it calls and compare per route.

## Four attempts at that, and why none of them shipped

The binding is not derivable by reading this backend, and each narrowing that
removed a false positive removed real coverage with it:

1. **Route -> handler -> return.** Handlers delegate (`return desks.leave(...)`),
   wrap (`return {"beacons": [...]}`), and merge (`{**metrics}`). Following one
   level resolved 141 of some 400 routes, and the resulting mismatch list was
   41 rows of which the ones checked by hand were the reader's fault.
2. **Flat-only, both sides.** Restricting to handlers returning one flat dict
   and models with only scalar properties cut coverage to 52 sites and still
   left a 42% mismatch rate.
3. **Bind on the container key instead of the route** — `chapters: [{...}]`.
   The first run reported five defects that are not there, because `llm.py`
   builds `{"messages": [...]}` as an outbound *request*. Restricting to
   route-reachable returns fixed that and broke the real finding instead.
4. **Disjointness rather than subset**, to survive a key with two shapes. It
   survives them by not judging them: `members` is built two ways, one of
   them behind a variable, so the union it compares against is incomplete.

The rule narrow enough to be sound — container key appearing exactly once in
the package, element model named exactly once in the shell — covers two sites
per product and finds nothing. That is the honest ceiling of inference here.

## So this file infers nothing

It pins. Each row names a shell model, and the backend function whose `return`
is that model's contract. No resolution, no guessing which route a call site
hits: a human read both ends once, and the file holds them together from then
on. It is small on purpose, and it is meant to grow one verified row at a time.

## What the pinning found

Nothing here, across four rounds of growing it. The findings were all next
door, in QRME, and two of them were on **every** shell at once rather than on
one: the shells agree with each other and disagree with the server, so
cross-checking the clients against each other would have found neither.

## What it found in itself

0.58.6 injected a defect into PDI's `ComplianceProgram` and the guard did not
fail. PDI writes `struct X: Decodable { let a: T; let b: T }` on one line and
the property pattern required end-of-line, so the reader saw that struct as
**empty** — and an empty set is a subset of anything, so the pin passed against
nothing for a whole release.

That is the failure this file now refuses to have twice. Every pin asserts on
both ends: the model read something, and what it read shares at least one key
with the contract. Deliberately not a size floor — `MicPlacesOut` and
`ChainState` are honest one-property wrappers — because a floor that called
those defects would be this file inventing work.

Two more checks read the readers themselves against a second opinion: every
struct whose conformance list mentions `Decodable` must be one `_STRUCT` can
see, and every C# record read by the finder must match a paren-matched
extraction of the same record. A reader that goes blind is indistinguishable
from a guard that is holding, and that is the only way this table can lie.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
PKG = "jim"

#: (shell model, backend module, function, container key or None).
#: The function's `return` is the contract. With a container key, the contract
#: is the element dict of the list under that key. Every row was read at both
#: ends by hand before it was written down — that is the whole point.
PINS = (
    ("FlowStep", "guardian", "emergency", "flow"),
    ("RobotDirective", "guardian", "_robot_directives", None),
    ("PresenceSurfaces", "presence", "surfaces", None),
    ("PresenceSurfaceRow", "presence", "surfaces", "surfaces"),
    ("FollowupState", "api", "open_followups", None),
    ("OpenFollowup", "followup", "open_for", None),
    ("FollowupRecord", "followup", "history", None),
)

#: Kotlin declares no models — it reads keys inline, and one function may
#: legitimately descend through more than one shape. So a Kotlin pin names
#: every shape that function is allowed to read, and nothing else.
#:
#: This is a weaker check than the model one by construction: a key that
#: belongs to a *sibling* shape in the same feature passes. It still catches
#: the kind that matters most — a name the feature never sends at all.
KOTLIN_PINS = (
    ("emergency", (("guardian", "emergency", None),
                   ("guardian", "emergency", "flow"),
                   ("guardian", "_robot_directives", None))),
)
IOS = "native/ios/Sources/ApiClient.swift"
ANDROID = "native/android/app/src/main/java/app/jim/guardian/ApiClient.kt"
WINDOWS = "native/windows/ApiClient.cs"


# --- the backend side: one named function, read exactly ----------------------

def _elem(node) -> ast.Dict | None:
    if isinstance(node, (ast.ListComp, ast.GeneratorExp)):
        node = node.elt
    elif isinstance(node, ast.List) and node.elts:
        node = node.elts[0]
    return node if isinstance(node, ast.Dict) else None


def _module_dict(tree: ast.Module, name: str) -> set[str] | None:
    """A module-level dict of dicts, all of whose values carry the same keys.
    Anything else returns None and the pin is refused rather than guessed."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            ident = target.id if isinstance(target, ast.Name) else None
            value = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            ident, value = node.target.id, node.value
        else:
            continue
        if ident != name:
            continue
        if isinstance(value, ast.DictComp):
            # `{key: {...} for … in _ROWS}` — one shape, written once.
            return (_keys(value.value)
                    if isinstance(value.value, ast.Dict) else None)
        if not isinstance(value, ast.Dict):
            continue
        shapes = []
        for v in value.values:
            if not isinstance(v, ast.Dict):
                return None
            shapes.append(_keys(v))
        if not shapes or any(sh != shapes[0] for sh in shapes[1:]):
            return None
        return shapes[0]
    return None


_SELECT = re.compile(r'\bSELECT\s+(.*?)\s+FROM\b', re.I | re.S)


def _columns(fn, ident: str) -> set[str] | None:
    """`[{**dict(r), …} for r in conn.execute("SELECT a, b, c FROM …")]`.

    The column list is a string literal in the function being read, so the
    keys `dict(r)` will carry are readable too. `SELECT *` is not — the
    columns are in a schema this file is not looking at — and that returns
    None so the pin is refused rather than guessed.
    """
    for node in ast.walk(fn):
        targets = []
        if isinstance(node, (ast.ListComp, ast.GeneratorExp)):
            targets = [(g.target, g.iter) for g in node.generators]
        elif isinstance(node, ast.For):
            targets = [(node.target, node.iter)]
        for target, source in targets:
            if not (isinstance(target, ast.Name) and target.id == ident):
                continue
            sources = [source]
            if isinstance(source, ast.Name):
                # `rows = conn.execute("SELECT …").fetchall()` on its own
                # line, then `[... for r in rows]`.
                sources += [n.value for n in ast.walk(fn)
                            if isinstance(n, ast.Assign) and len(n.targets) == 1
                            and isinstance(n.targets[0], ast.Name)
                            and n.targets[0].id == source.id]
            sql = "".join(n.value for src in sources for n in ast.walk(src)
                          if isinstance(n, ast.Constant)
                          and isinstance(n.value, str))
            found = _SELECT.search(sql)
            if not found:
                continue
            cols = set()
            for raw in found.group(1).split(","):
                col = raw.strip().split()[-1] if raw.strip() else ""
                if not re.fullmatch(r'[a-z_]\w*', col):
                    return None            # `*`, an expression, a function
                cols.add(col)
            return cols or None
    return None


def _listed(tree: ast.Module, node) -> set[str] | None:
    """`list(_PROGRAMS.values())` — the element shape is the table's."""
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in {"list", "sorted"} and len(node.args) == 1):
        return None
    inner = node.args[0]
    if (isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute)
            and inner.func.attr == "values"
            and isinstance(inner.func.value, ast.Name)):
        return _module_dict(tree, inner.func.value.id)
    return None


def _spread(tree: ast.Module, fn, name: str) -> set[str] | None:
    """`{"surface": name, **spec, …}` — resolve what `spec` holds.

    Either a module-level dict of dicts by that name, or the value half of a
    `for _k, spec in SOMETHING.items()` in the function being read. Both are
    lookups; neither is a guess.
    """
    direct = _module_dict(tree, name)
    if direct is not None:
        return direct
    pairs = []
    for node in ast.walk(fn):
        if isinstance(node, ast.For):
            pairs.append((node.target, node.iter))
        elif isinstance(node, (ast.ListComp, ast.GeneratorExp, ast.DictComp)):
            pairs += [(g.target, g.iter) for g in node.generators]
    for target, it in pairs:
        if not (isinstance(target, ast.Tuple) and len(target.elts) == 2
                and isinstance(target.elts[1], ast.Name)
                and target.elts[1].id == name):
            continue
        if (isinstance(it, ast.Call) and isinstance(it.func, ast.Attribute)
                and it.func.attr == "items"
                and isinstance(it.func.value, ast.Name)):
            return _module_dict(tree, it.func.value.id)
    return None


def _keys(node: ast.Dict, tree: ast.Module | None = None, fn=None) -> set[str]:
    out = set()
    for k in node.keys:
        if isinstance(k, ast.Constant) and isinstance(k.value, str):
            out.add(k.value)
        elif k is None and tree is not None:
            # `{"surface": name, **spec, …}` — the spread is part of the
            # contract, and skipping it would call a real key a defect.
            v = node.values[node.keys.index(k)]
            spread = None
            if fn is not None:
                if isinstance(v, ast.Name):
                    spread = _spread(tree, fn, v.id) or _columns(fn, v.id)
                elif (isinstance(v, ast.Call) and isinstance(v.func, ast.Name)
                      and v.func.id == "dict" and len(v.args) == 1
                      and isinstance(v.args[0], ast.Name)):
                    spread = _columns(fn, v.args[0].id)
            assert spread is not None, (
                "a `**` this file cannot resolve is a pin it must not guess at")
            out |= spread
    return out


def _named(fn, ident: str) -> tuple[ast.Dict | None, set[str]]:
    """Resolve a local name to the dict it holds, inside one pinned function.

    Three shapes, all of them assignment in the body being read — no
    cross-function inference:

        out = {...}                     a dict, built at once
        out["k"] = ...                  and added to afterwards
        rows = [{...} for r in …]       a list of dicts
        rows = []; rows.append(row)     a list built by appending one

    0.58.4 named the last of these as a limit and refused to guess past it.
    Lifting it is the same promise kept differently: still one function, still
    read rather than inferred.
    """
    found, extra = None, set()
    for node in ast.walk(fn):
        if not (isinstance(node, ast.Assign) and len(node.targets) == 1):
            continue
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id == ident:
            found = _elem(node.value) or (
                node.value if isinstance(node.value, ast.Dict) else found)
        elif (isinstance(target, ast.Subscript)
              and isinstance(target.value, ast.Name)
              and target.value.id == ident
              and isinstance(target.slice, ast.Constant)
              and isinstance(target.slice.value, str)):
            extra.add(target.slice.value)
    if found is None:
        for node in ast.walk(fn):
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "append"
                    and isinstance(node.func.value, ast.Name)
                    and node.func.value.id == ident and node.args):
                arg = node.args[0]
                if isinstance(arg, ast.Dict):
                    found = arg
                elif isinstance(arg, ast.Name):
                    found, more = _named(fn, arg.id)
                    extra |= more
    return found, extra


def contract(module: str, func: str, container: str | None) -> set[str]:
    """What the named function returns, or the element shape under a key."""
    path = next((p for p in (REPO / PKG).rglob(f"{module}.py")
                 if "tests" not in p.parts), None)
    assert path is not None, f"{PKG}/{module}.py is gone"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    fn = next((n for n in ast.walk(tree)
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
               and n.name == func), None)
    assert fn is not None, f"{module}.{func} is gone"
    for ret in (n.value for n in ast.walk(fn)
                if isinstance(n, ast.Return) and n.value is not None):
        top = _elem(ret)
        if top is None and isinstance(ret, ast.Name):
            # `out = {...}` … `out["speak"] = …` … `return out`. Built in
            # pieces is still built here, and this is a pinned function: the
            # whole body is fair to read.
            built, extra = _named(fn, ret.id)
            if built is not None and container is None:
                return _keys(built, tree, fn) | extra
            top = built
        if top is None:
            continue
        if container is None:
            return _keys(top, tree, fn)
        for k, v in zip(top.keys, top.values):
            if isinstance(k, ast.Constant) and k.value == container:
                inner = _elem(v)
                spread: set[str] = set()
                if inner is None and isinstance(v, ast.Name):
                    inner, spread = _named(fn, v.id)
                if inner is None and not spread:
                    # `"programs": list(_PROGRAMS.values())` — a module-level
                    # table handed out whole.
                    from_table = _listed(tree, v)
                    if from_table is not None:
                        return from_table
                assert inner is not None, (
                    f"{module}.{func}[{container!r}] is not a list of dicts")
                return _keys(inner, tree, fn) | spread
    raise AssertionError(f"{module}.{func} returns no dict this file can read")


# --- the shell side ----------------------------------------------------------

_STRUCT = re.compile(r'\bstruct\s+(\w+)\s*:[^{\n]*\bDecodable\b[^{\n]*\{')
#: A stored property, whether it ends the line or is separated from the
#: next by a `;`. PDI declares `struct X: Decodable { let a: T; let b: T }`
#: on one line, and requiring end-of-line read that struct as empty —
#: which made its pin pass against nothing at all.
_STORED = re.compile(
    r'(?:^|\{|;)\s*(?:var|let)\s+(\w+)\s*:\s*[^\n={;}]+?(?=\s*(?:$|;|\}))',
    re.M)
_RENAME = re.compile(r'^\s*case\s+(\w+)\s*=\s*"([^"]+)"', re.M)
_CREC = re.compile(r'public record (\w+)\(')
# A record's parameter list ends at `);` — unless the record carries a body,
# which is legal C# and ends the list at `)` followed by `{`. `PackInstalled`
# is one, and reading past its close swallowed the record declared after it.
_CREC_END = re.compile(r'\)\s*[;{]')


def _crec_end(src: str, at: int) -> int:
    """Index just past the record's closing paren, from the open paren."""
    m = _CREC_END.search(src, at)
    return m.start() if m else len(src)

_CPROP = re.compile(r'JsonPropertyName\("([^"]+)"\)')
_KFUN = re.compile(r'\n    (?:private\s+)?suspend fun\s+(\w+)\s*\([^\n]*')
_KKEY = re.compile(r'\.(?:opt|get)'
                   r'(?:String|Int|Boolean|Double|Long|JSONArray|JSONObject)'
                   r'\(\s*"([^"]+)"')


def _matched(src: str, start: int) -> str:
    depth, i = 1, start
    while i < len(src) and depth:
        depth += (src[i] == "{") - (src[i] == "}")
        i += 1
    return src[start:i - 1]


def _swift_models(src: str) -> dict[str, set[str]]:
    """`Name` and `Outer.Inner` -> the wire keys each declares."""
    out: dict[str, set[str]] = {}

    def take(prefix: str, s: str) -> None:
        for m in _STRUCT.finditer(s):
            body = _matched(s, m.end())
            name = f"{prefix}{m.group(1)}"
            renames = dict(_RENAME.findall(body))
            nested = {p for i in _STRUCT.finditer(body)
                      for p in _STORED.findall(_matched(body, i.end()))}
            out[name] = {renames.get(p, p) for p in _STORED.findall(body)
                         if p not in nested}
            take(f"{name}.", body)

    take("", src)
    return out


def _code(path: Path) -> str:
    return re.sub(r'^\s*(?://|///)[^\n]*$', "",
                  path.read_text(encoding="utf-8"), flags=re.M)


def _csharp_models(src: str) -> dict[str, set[str]]:
    out = {}
    for m in _CREC.finditer(src):
        out[m.group(1)] = set(_CPROP.findall(src[m.end():_crec_end(src, m.end())]))
    return out


def _kotlin_functions(src: str) -> dict[str, set[str]]:
    out = {}
    for m in _KFUN.finditer(src):
        brace = src.find("{", m.end() - 1)
        if brace < 0:
            continue
        out[m.group(1)] = set(_KKEY.findall(_matched(src, brace + 1)))
    return out


# --- the guard ---------------------------------------------------------------

def test_every_pinned_model_matches_the_shape_it_decodes():
    """0.58.4's defect. `TutorialOutline.Chapter` reading `key` and `title`
    off `{chapter, steps}` does not fail — it renders a column of `?`."""
    swift = _swift_models(_code(REPO / IOS))
    csharp = _csharp_models(_code(REPO / WINDOWS))
    wrong = []
    for model, module, func, container in PINS:
        sent = contract(module, func, container)
        for shell, models in (("ios", swift), ("windows", csharp)):
            keys = models.get(model if shell == "ios" else model.split(".")[-1])
            if keys is None:
                continue
            extra = sorted(keys - sent)
            if extra:
                wrong.append(f"{shell}: {model} reads {extra} — "
                             f"{PKG}/{module}.py:{func}"
                             f"{'[' + container + ']' if container else ''} "
                             f"sends {sorted(sent)}")
    assert not wrong, "\n    ".join([""] + wrong) + (
        "\n  Read the shape the function returns, or change what it returns.")


def test_every_pinned_kotlin_read_matches_the_shape():
    """Kotlin declares no models; the keys are in the function body, which
    makes them exactly as wrong and rather harder to see."""
    functions = _kotlin_functions(_code(REPO / ANDROID))
    wrong = []
    for func_name, shapes in KOTLIN_PINS:
        keys = functions.get(func_name)
        assert keys is not None, f"{func_name} is gone from ApiClient.kt"
        allowed: set[str] = set()
        for module, func, container in shapes:
            allowed |= contract(module, func, container)
        extra = sorted(keys - allowed)
        if extra:
            named = ", ".join(f"{m}.{f}" + (f"[{c}]" if c else "")
                              for m, f, c in shapes)
            wrong.append(f"android: {func_name} reads {extra} — "
                         f"{named} send {sorted(allowed)}")
    assert not wrong, "\n    ".join([""] + wrong) + (
        "\n  Read the name the function actually returns.")


# --- the pins have to point at something, and to fail ------------------------

def test_every_pin_still_points_at_a_function():
    """A pin whose function was renamed is a row that quietly stops
    checking — `contract` raises rather than returning an empty set."""
    rows = [(m, f, c) for _model, m, f, c in PINS]
    rows += [row for _name, shapes in KOTLIN_PINS for row in shapes]
    for module, func, container in rows:
        sent = contract(module, func, container)
        assert len(sent) >= 2, f"{module}.{func}: only {len(sent)} key(s)"


def test_at_least_one_end_of_every_pin_is_present():
    """A pinned model that no shell declares is a row checking nothing."""
    swift = _swift_models(_code(REPO / IOS))
    csharp = _csharp_models(_code(REPO / WINDOWS))
    kotlin = _kotlin_functions(_code(REPO / ANDROID))
    for model, *_rest in PINS:
        found = [k for k in (swift.get(model),
                             csharp.get(model.split(".")[-1])) if k]
        assert found, f"{model}: no shell declares it, or both read as empty"
    for func_name, _shapes in KOTLIN_PINS:
        assert func_name in kotlin, func_name


def test_no_pin_reads_an_empty_or_unrelated_model():
    """The hole 0.58.6 fell into, closed.

    A model the reader parses as **empty** passes every comparison there is —
    an empty set is a subset of anything — so a pin whose reader has gone
    blind looks exactly like a pin that is holding. PDI's one-line structs
    were read that way for a whole release, and the round that caught it
    caught it by injecting, not by running.

    Two floors, and neither of them is a size:

        it read something         an empty model is a blind reader
        it read the right thing   a model sharing no key with the contract
                                  is reading some other shape entirely

    Deliberately *not* `len(keys) >= 2`. `MicPlacesOut` and `ChainState` are
    honest one-property wrappers, and a floor that called those defects would
    be this file inventing work.
    """
    swift = _swift_models(_code(REPO / IOS))
    csharp = _csharp_models(_code(REPO / WINDOWS))
    blind = []
    for model, module, func, container in PINS:
        sent = contract(module, func, container)
        for shell, models in (("ios", swift), ("windows", csharp)):
            name = model if shell == "ios" else model.split(".")[-1]
            if name not in models:
                continue
            keys = models[name]
            if not keys:
                blind.append(f"{shell}: {model} read as empty — the reader "
                             f"cannot see this declaration")
            elif not (keys & sent):
                blind.append(f"{shell}: {model} reads {sorted(keys)}, and "
                             f"{PKG}/{module}.py:{func} sends {sorted(sent)} "
                             f"— not one key in common")
    assert not blind, "\n    ".join([""] + blind) + (
        "\n  A pin that reads nothing is a pin that checks nothing.")


def test_no_kotlin_pin_reads_nothing():
    """Same floor on the half that has no models to read."""
    functions = _kotlin_functions(_code(REPO / ANDROID))
    blind = []
    for func_name, shapes in KOTLIN_PINS:
        keys = functions.get(func_name) or set()
        allowed: set[str] = set()
        for row in shapes:
            allowed |= contract(*row)
        if not keys:
            blind.append(f"android: {func_name} reads no keys at all")
        elif not (keys & allowed):
            blind.append(f"android: {func_name} reads {sorted(keys)} and "
                         f"shares nothing with {sorted(allowed)}")
    assert not blind, "\n    ".join([""] + blind)


# --- the readers themselves, checked against a second opinion ---------------

def test_the_swift_reader_sees_every_decodable_struct():
    """`_STRUCT` matches a one-line declaration. A struct that spreads its
    conformance list over two lines would be invisible — and invisible is
    indistinguishable from correct, which is the whole lesson of 0.58.6."""
    src = _code(REPO / IOS)
    seen = {m.group(1) for m in _STRUCT.finditer(src)}
    missed = []
    for m in re.finditer(r'\bstruct\s+(\w+)\s*:', src):
        head = src[m.end():m.end() + 200].split("{")[0]
        if "Decodable" in head and m.group(1) not in seen:
            missed.append(m.group(1))
    assert not missed, (
        f"the Swift reader cannot see {sorted(set(missed))} — widen _STRUCT")


def test_the_csharp_reader_reads_a_whole_record():
    """The record finder ends at the first `);`. Paren-matching is the second
    opinion: where the two disagree the finder has truncated a record, and a
    truncated record is a model with fewer keys than it really has."""
    src = _code(REPO / WINDOWS)
    truncated = []
    for m in _CREC.finditer(src):
        shipped = set(_CPROP.findall(src[m.end():_crec_end(src, m.end())]))
        depth, i = 1, m.end()
        while i < len(src) and depth:
            depth += (src[i] == "(") - (src[i] == ")")
            i += 1
        whole = set(_CPROP.findall(src[m.end():i - 1]))
        if shipped != whole:
            truncated.append(f"{m.group(1)}: missed {sorted(whole - shipped)}")
    assert not truncated, "\n    ".join([""] + truncated)


def test_the_swift_reader_reads_every_property_it_can_see():
    """A second opinion on the property pattern, found by where a declaration
    *starts* rather than where it ends.

    The both-ends floor below catches a reader that reads **nothing**. It does
    not catch one that reads **less** — 0.58.6's bug left `ComplianceProgram`
    with one of its two keys, which is still a non-empty set sharing a key
    with the contract, and would have passed. Counting declaration starts is
    simple enough to be a fair check on the pattern that parses their values.
    """
    src = _code(REPO / IOS)
    starts = re.compile(r'(?:^|[{;])\s*(?:let|var)\s+(\w+)\s*:', re.M)
    computed = re.compile(r'(?:^|[{;])\s*(?:let|var)\s+(\w+)\s*:[^\n=;{]*\{', re.M)
    short = []
    for m in _STRUCT.finditer(src):
        body = _matched(src, m.end())
        nested = {p for i in _STRUCT.finditer(body)
                  for p in _STORED.findall(_matched(body, i.end()))}
        inner_bodies = "".join(_matched(body, i.end())
                               for i in _STRUCT.finditer(body))
        outer = body
        for chunk in (_matched(body, i.end()) for i in _STRUCT.finditer(body)):
            outer = outer.replace(chunk, "")
        expected = (set(starts.findall(outer)) - set(computed.findall(outer))
                    - nested)
        read = {renames.get(p, p) for renames in
                [dict(_RENAME.findall(body))] for p in _STORED.findall(outer)}
        missing = sorted(expected - {p for p in _STORED.findall(outer)})
        if missing:
            short.append(f"{m.group(1)}: declares {missing} and the reader "
                         f"does not see them")
    assert not short, "\n    ".join([""] + short) + (
        "\n  The property pattern is narrower than the language.")


def test_a_wire_model_holds_no_methods():
    """The defect the second opinion turned up, checked directly.

    `struct SpecialistRow: Decodable {` was missing its closing brace and the
    `extension ApiClient {` that should have followed it. Ninety-five client
    methods — the whole *face it shows the world* block, avatar through
    experience — were declared as members of a two-field wire model instead of
    on the client, so every screen calling `ApiClient.shared.avatar(…)` had
    nothing to call.

    Brace *balance* could not see it: the file balanced perfectly, one brace
    simply belonged to the wrong opener. The member check could not see it
    either: the methods are in `ApiClient.swift`, just nested. What gives it
    away is the thing that is obviously true and was never asserted — a wire
    model is data, and data has no methods.
    """
    src = _code(REPO / IOS)
    holding = []
    for m in _STRUCT.finditer(src):
        body = _matched(src, m.end())
        for inner in _STRUCT.finditer(body):
            body = body.replace(_matched(body, inner.end()), "")
        found = re.findall(r'^\s*func\s+(\w+)', body, re.M)
        if found:
            holding.append(f"{m.group(1)} holds {len(found)} method(s), "
                           f"starting with {found[0]!r} — a brace is missing")
    assert not holding, "\n    ".join([""] + holding) + (
        "\n  A wire model is data. Methods in one mean a `}` went astray.")


def test_a_one_line_struct_is_not_empty(tmp_path):
    """0.58.6's own defect, as a unit. PDI writes them this way, and reading
    such a struct as empty made its pin pass against nothing for a release."""
    path = tmp_path / "ApiClient.swift"
    path.write_text("struct Program: Decodable { let key: String; "
                    "let label: String }\n")
    assert _swift_models(path.read_text())["Program"] == {"key", "label"}


def test_a_computed_property_is_still_not_a_key(tmp_path):
    """The fix for the line above widened the property pattern. This is the
    thing that widening must not break."""
    src = ('struct Chapter: Decodable {\n'
           '    let chapter: String?\n'
           '    var id: String { chapter ?? "?" }\n}\n')
    assert _swift_models(src)["Chapter"] == {"chapter"}


def test_a_container_pin_reads_the_element_not_the_wrapper(tmp_path):
    """`chapters` is a list of dicts. Reading the wrapper's own keys would
    compare a chapter against `guide` and `chapters`."""
    src = ('def outline():\n'
           '    return {"guide": G, "chapters": [{"chapter": c, "steps": s}\n'
           '                                     for c in CHAPTERS]}\n')
    tree = ast.parse(src)
    fn = tree.body[0]
    ret = fn.body[0].value
    top = _elem(ret)
    inner = _elem(dict(zip([k.value for k in top.keys], top.values))["chapters"])
    assert _keys(top) == {"guide", "chapters"}
    assert _keys(inner) == {"chapter", "steps"}


def test_the_check_can_fail():
    """The real one: the chapter carries `chapter` and `steps`, and the
    iPhone read `key` and `title`."""
    sent = contract("tutorial", "outline", "chapters")
    assert sorted({"key", "title"} - sent) == ["key", "title"]
    assert "chapter" in sent and "steps" in sent


def test_a_wrapper_is_not_its_contents():
    """`tutorial.where` wraps the step. Decoding it as a bare step is how
    three buttons on two phones came back blank."""
    wrapper = contract("tutorial", "where", None)
    step = contract("tutorial", "say", None)
    assert "step" in wrapper
    assert not (step & wrapper), sorted(step & wrapper)
