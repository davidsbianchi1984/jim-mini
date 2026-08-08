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

Nothing here, and that is what a pinned table looks like on the day it is
written: the rows are a contract somebody read at both ends, not a search.
The finding was next door — QRME's guided tour, blank on both phones and
correct on Windows, where `/tutorial` sends `chapters: [{chapter, steps}]`
and both phones read `key` and `title`, and where three more buttons decoded
a wrapper as the thing it wraps.

Windows had all four right, and carried a comment saying a chapter never had
a `key` or a `title` of its own. Somebody fixed one shell and the note never
crossed to the others, which is the argument for a file rather than a comment.
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
)

#: Kotlin declares no models — it reads keys inline, and one function may
#: legitimately descend through more than one shape. So a Kotlin pin names
#: every shape that function is allowed to read, and nothing else.
#:
#: This is a weaker check than the model one by construction: a key that
#: belongs to a *sibling* shape in the same feature passes. It still catches
#: the kind that matters most — a name the feature never sends at all.
#: Kotlin declares no models — it reads keys inline, and one function may
#: legitimately descend through more than one shape. So a Kotlin pin names
#: every shape that function is allowed to read, and nothing else.
#:
#: Empty here, and the reason is worth writing down rather than working
#: around: `emergency` descends into `robot_directives`, whose elements are
#: built by `directives.append(entry)` in a loop. This file reads a `return`
#: — a dict literal, or a name assigned one and then added to. A list built
#: by appending is not something it can read, and a pin that guesses at the
#: shape would be the inference this file exists to avoid.
KOTLIN_PINS: tuple = ()
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


def _keys(node: ast.Dict) -> set[str]:
    return {k.value for k in node.keys
            if isinstance(k, ast.Constant) and isinstance(k.value, str)}


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
            built, extra = None, set()
            for node in ast.walk(fn):
                if (isinstance(node, ast.Assign) and len(node.targets) == 1):
                    t = node.targets[0]
                    if isinstance(t, ast.Name) and t.id == ret.id:
                        built = _elem(node.value) or built
                    elif (isinstance(t, ast.Subscript)
                          and isinstance(t.value, ast.Name)
                          and t.value.id == ret.id
                          and isinstance(t.slice, ast.Constant)
                          and isinstance(t.slice.value, str)):
                        extra.add(t.slice.value)
            if built is not None and container is None:
                return _keys(built) | extra
            top = built
        if top is None:
            continue
        if container is None:
            return _keys(top)
        for k, v in zip(top.keys, top.values):
            if isinstance(k, ast.Constant) and k.value == container:
                inner = _elem(v)
                assert inner is not None, (
                    f"{module}.{func}[{container!r}] is not a list of dicts")
                return _keys(inner)
    raise AssertionError(f"{module}.{func} returns no dict this file can read")


# --- the shell side ----------------------------------------------------------

_STRUCT = re.compile(r'\bstruct\s+(\w+)\s*:[^{\n]*\bDecodable\b[^{\n]*\{')
_STORED = re.compile(r'^\s*(?:var|let)\s+(\w+)\s*:\s*[^\n={]+?$', re.M)
_RENAME = re.compile(r'^\s*case\s+(\w+)\s*=\s*"([^"]+)"', re.M)
_CREC = re.compile(r'public record (\w+)\(')
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
        out[m.group(1)] = set(_CPROP.findall(src[m.end():src.find(");", m.end())]))
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
        assert model in swift or model.split(".")[-1] in csharp, model
    for func_name, _shapes in KOTLIN_PINS:
        assert func_name in kotlin, func_name


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
