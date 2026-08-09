"""`req<T>` is a cast, and a cast is a claim about the server nothing checks.

## Where this came from

0.59.6 read the requirement out of the application — which headers a route
needs — and asked whether the callers could meet it. This is the same
question pointed the other way: the route **answers** with a shape, the screen
**declares** one, and between them sits `req<T>`, which is a TypeScript cast.
A cast type-checks against nothing. The compiler is satisfied; the screen
crashes.

    asked     does this call compile
    mattered  is the shape it names the shape that arrives

## What it was

`GET /users/{uid}/referral/clinicians` answers with an **object**:

    {"area": …, "locality": …, "clinicians": [ … ], "reason": …}

The console declared `Row[]` and the Attending screen called `.map` on it:

    TypeError: clinicians.map is not a function

thrown during render, the moment anybody pressed *who would this reach*. And
the `reason` the backend composes for an empty list — *no clinician
registered in this area* — had never been shown to a single person, because
the screen threw before it got there. It is shown now.

PDI had the same defect on `GET /hosting/{tenant_id}/history`, on any vault
that had ever been moved.

## Why the existing guards do not cover it

The route audit asks whether a path resolves and whether a method is
accepted. The door audit asks whether a route has a screen. Both were fully
satisfied here: the path resolved, the method matched, the screen existed and
called it. Nothing asked what came back.

`tsc` cannot help either, and that is the point rather than an oversight:
`req<T>` is generic over a type the caller supplies, and the body is parsed
with `JSON.parse`, which returns `any`. The cast is exactly where the type
system stops.

## What this reads

Per **call expression**, not per path. The first cut of this sweep keyed on
the path literal and reported sixty-odd disagreements, every one of them the
reader pairing a `POST` with the `GET` that shares its path. Reading each
`req<T>(…)` call and taking the verb out of *that* call's own body dropped it
to one per product, and all three of those were real.

A union that names both shapes satisfies either: `{comments: C[]} | C[]` is a
client that handles what arrives, which is defensive rather than wrong.

## 0.59.8: one client of four

The paragraph above describes what this file did when it was written, and it
was written against the console alone. The three shells decode the same
answers into their own types, and a wrong one there is the same failure with
a different stack trace — `JSONArray` on an object throws exactly like `.map`
on one.

Extending it multiplied the comparisons by four, and the interesting part was
not the disagreements — there were none — but how unevenly the clients can be
read at all:

    QRME       console 422   ios 300   android 316   windows 342
    JIM-mini   console 245   ios  89   android   3   windows  88
    PDI        console 116   ios  31   android  24   windows  20

JIM-mini's Android shell names a shape on three calls out of a hundred and
fourteen, because it discards the body on the rest. That is not a reader
failing — a client that never reads an answer cannot be wrong about it — but
three and three hundred cannot share a floor, so the per-client reach is a
**record** that must not go down rather than a number chosen by hand.

"""

from __future__ import annotations

import functools
import re
import typing
from pathlib import Path

import pytest

from jim.api import app

from . import clientpaths as cp
from . import ratchets

RECORD = Path(__file__).resolve().parent / "shape_disagreements.txt"

#: Where a call declares the shape it expects.
CALL = re.compile(r"req(?:Text)?<([^(]*?)>\(")


def _is_list(annotation) -> bool | None:
    """True/False when the annotation is decisive about list-ness, else None.

    `None` is the honest answer for `Any`, a bare `Response`, or a type
    variable — and a `None` here means this route is not compared rather than
    compared loosely.
    """
    if annotation is None:
        return None
    origin = typing.get_origin(annotation)
    if origin in (list, tuple, set):
        return True
    if origin is dict or annotation is dict:
        return False
    if isinstance(annotation, type):
        return issubclass(annotation, (list, tuple))
    return None


def route_shapes() -> dict[tuple[str, str], bool]:
    """(method, path template) -> True when the route answers with a list.

    `response_model` first, because a route that declares one is answering
    with it whatever the function returns; the return annotation second.
    """
    out: dict[tuple[str, str], bool] = {}
    for route in cp.all_routes(app):
        annotation = getattr(route, "response_model", None)
        if annotation is None and getattr(route, "endpoint", None):
            try:
                annotation = typing.get_type_hints(route.endpoint).get("return")
            except Exception:          # a forward reference we cannot resolve
                annotation = None
        shape = _is_list(annotation)
        if shape is None:
            continue
        for method in sorted(getattr(route, "methods", None) or []):
            if method not in ("HEAD", "OPTIONS"):
                out[(method, route.path)] = shape
    return out


def _route_for(method: str, path: str):
    from starlette.routing import Match

    scope = {"type": "http", "method": method, "path": path,
             "root_path": "", "headers": []}
    for route in cp.all_routes(app):
        if route.matches(scope)[0] == Match.FULL:
            return route
    return None


def _declares_list(declared: str) -> bool | None:
    """Whether the declared type is a list, an object, or honestly both.

    A union is not a hedge to be punished — `{comments: C[]} | C[]` is a
    client that copes with either answer. Only a union naming exactly one
    shape is a claim this file can check.
    """
    arms = [a.strip() for a in declared.split("|")]
    kinds = {a.endswith("[]") or a.startswith("Array<") for a in arms}
    return kinds.pop() if len(kinds) == 1 else None


def calls() -> list[tuple[str, str, str, str]]:
    """(file, verb, path, declared type) for every typed console call."""
    lang = cp.CONSOLE
    found = []
    if not lang.root.exists():
        return found
    for f in sorted(lang.root.rglob("*")):
        if f.suffix not in lang.suffixes or not f.is_file():
            continue
        text = cp._COMMENTS.sub("", f.read_text(encoding="utf-8", errors="ignore"))
        for m in CALL.finditer(text):
            body = cp._call_body(text, m.end() - 1)
            if not body:
                continue
            literal = lang.literal.search(body)
            if not literal:
                continue
            raw = next(g for g in literal.groups() if g is not None)
            verb = "GET"
            said = re.search(r'method:\s*"(\w+)"', body)
            if said:
                verb = said.group(1).upper()
            found.append((f.name, verb, cp.normalise(raw, lang), m.group(1).strip()))
    return found



# --------------------------------------------------------------------------- #
# the four clients, and how each one says what shape it expects
# --------------------------------------------------------------------------- #
#
# 0.59.7 asked this question of the console and found a crash in two of the
# three products. It asked it of one client out of four. *No disagreement*
# from a check that was never run reads exactly like *no disagreement* from a
# check that passed, which is the sentence this whole arc keeps arriving at.
#
# Each shell states the shape somewhere different:
#
#     console   req<T>(…)                     the generic
#     ios       let x: T = try await request  the annotated decode
#     windows   Send<T>(…)                    the generic
#     android   JSONObject(body) / JSONArray  the parse itself
#
# Android is the interesting one: Kotlin has no decode type here, so the
# *parse* is the claim — `JSONArray` on an object throws, which is the same
# failure as `.map` on one.


def _swift_is_list(declared: str) -> bool | None:
    """`[X]` is a list; `[K: V]` is a dictionary, which is an object.

    Both start with a bracket, and the first cut of this reader called a
    Swift dictionary a list and reported a disagreement that was its own.
    """
    d = declared.strip()
    if not d.startswith("["):
        return False
    depth = 0
    for ch in d[1:-1]:
        if ch in "[<(":
            depth += 1
        elif ch in "]>)":
            depth -= 1
        elif ch == ":" and depth == 0:
            return False
    return True


def _cs_is_list(declared: str) -> bool | None:
    d = declared.strip()
    return d.startswith("List<") or d.endswith("[]")


def _verb_in(body: str) -> str:
    """The verb of *this* call.

    Read from the call's own body, never from the path: keying on the path
    paired every POST with the GET beside it and produced sixty
    disagreements that were all one mistake. The Windows shell spells its
    verb with a `Post(…)`/`Get(…)` helper rather than `HttpMethod.Post`, and
    missing that spelling defaulted twenty-one calls to GET and reported
    every one of them wrong.
    """
    m = re.search(r'method:\s*"(\w+)"|HttpMethod\.(\w+)|\b(Post|Get|Put|Delete|Patch)\('
                  r'|"(GET|POST|PUT|DELETE|PATCH)"', body)
    if not m:
        return "GET"
    return next(g for g in m.groups() if g).upper()


def _console_calls(lang):
    for f, text in _client_sources(lang):
        for m in CALL.finditer(text):
            body = cp._call_body(text, m.end() - 1)
            if body:
                yield f.name, body, m.group(1).strip(), _declares_list


def _ios_calls(lang):
    annotated = re.compile(
        r"let\s+\w+\s*:\s*(?P<ret>[\w\[\]:<>,.? ]+?)\s*=\s*try await request\((?P<body>[^\n]{0,300})")
    returned = re.compile(
        r"->\s*(?P<ret>[\w\[\]:<>,.? ]+?)\s*\{\s*\n?\s*try await request\((?P<body>[^\n]{0,300})")
    for f, text in _client_sources(lang):
        for pattern in (annotated, returned):
            for m in pattern.finditer(text):
                yield f.name, m.group("body"), m.group("ret").strip(), _swift_is_list


def _windows_calls(lang):
    pattern = re.compile(r"Send<(?P<ret>[^>]+(?:<[^>]*>)?)>\((?P<body>[^;]{0,400})")
    for f, text in _client_sources(lang):
        for m in pattern.finditer(text):
            yield f.name, m.group("body"), m.group("ret").strip(), _cs_is_list


def _android_calls(lang):
    """The parse is the claim. Two spellings, because both are in use:
    wrapping the call, and binding it to a name first."""
    inline = re.compile(
        r"(?:org\.json\.)?JSON(?P<kind>Object|Array)\s*\(\s*\n?\s*request\((?P<body>.{0,300}?)\)\s*\n",
        re.S)
    # The third spelling, and in this shell the common one: `request` parses
    # centrally and returns a `JSONObject`, so the claim is not written at the
    # call site — it is the return type, and every such call claims Object.
    #
    # The reader saw only the first two spellings, which meant it read three
    # calls out of a client of this size. All three were code that wrapped an
    # already-parsed `JSONObject` in the `JSONObject` constructor and had
    # never compiled. The reader was measuring the bug.
    direct = re.compile(r"[=\s]request\((?P<body>.{0,300}?)\)\s*(?:\n|\.)", re.S)
    bound = re.compile(r"\bval\s+(?P<var>\w+)\s*=\s*request\((?P<body>.{0,300}?)\)\s*\n", re.S)
    for f, text in _client_sources(lang):
        seen = set()
        for m in inline.finditer(text):
            seen.add(m.start("body"))
            yield f.name, m.group("body"), m.group("kind"), _is_json_array
        for m in direct.finditer(text):
            if m.start("body") in seen:
                continue
            seen.add(m.start("body"))
            yield f.name, m.group("body"), "Object", _is_json_array
        for m in bound.finditer(text):
            if m.start("body") in seen:
                continue
            after = text[m.end():m.end() + 600]
            parsed = re.search(
                rf"(?:org\.json\.)?JSON(Object|Array)\s*\(\s*{re.escape(m.group('var'))}\s*\)",
                after)
            if parsed:
                yield f.name, m.group("body"), parsed.group(1), _is_json_array


def _is_json_array(kind: str) -> bool:
    return kind == "Array"


CLIENTS = {
    "console": (cp.CONSOLE, _console_calls),
    "ios": (cp.IOS, _ios_calls),
    "android": (cp.ANDROID, _android_calls),
    "windows": (cp.WINDOWS, _windows_calls),
}


@functools.lru_cache(maxsize=None)
def _client_sources(lang) -> tuple:
    return tuple((f, cp._COMMENTS.sub("", f.read_text(encoding="utf-8", errors="ignore")))
                 for f in sorted(lang.root.rglob("*"))
                 if f.suffix in lang.suffixes and f.is_file())


def typed_calls(client: str) -> list[tuple[str, str, str, str, object]]:
    """(file, verb, path, declared, reader) for every call that names a shape.

    A call whose answer the client never reads names no shape and is not
    counted — JIM-mini's Android shell discards the body on 111 of its 114
    calls, and a client that never reads an answer cannot be wrong about it.
    """
    lang, reader = CLIENTS[client]
    out = []
    if not lang.root.exists():
        return out
    for name, body, declared, is_list in reader(lang):
        literal = lang.literal.search(body)
        if not literal:
            continue
        raw = next(g for g in literal.groups() if g is not None)
        out.append((name, _verb_in(body), cp.normalise(raw, lang), declared, is_list))
    return out


def disagreements() -> list[str]:
    """Every client, every call that names a shape, against the route."""
    shapes, out = route_shapes(), []
    for client in sorted(CLIENTS):
        for name, verb, path, declared, is_list in typed_calls(client):
            route = _route_for(verb, path)
            if route is None:
                continue
            answers = shapes.get((verb, route.path))
            if answers is None:
                continue
            expects = is_list(declared)
            if expects is None or expects == answers:
                continue
            out.append(f"{client}/{name}: {verb} {path} answers "
                       f"{'a list' if answers else 'an object'}, "
                       f"the client expects {declared}")
    return sorted(set(out))


def _recorded() -> set[str]:
    return {ln.strip() for ln in RECORD.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.startswith("#")}


def test_every_typed_call_names_the_shape_the_route_answers():
    """The check.

    A screen that maps over an object throws where it renders. A screen that
    reads `.length` off a list it thought was an object renders nothing and
    says nothing, which is worse. Both are this comparison.
    """
    unrecorded = [row for row in disagreements() if row not in _recorded()]
    assert not unrecorded, (
        "these screens name a shape the route does not answer with:\n    "
        + "\n    ".join(unrecorded)
        + "\n  `req<T>` is a cast: it compiles whatever you write there, and "
          "the body is parsed by `JSON.parse`, which answers `any`.")


REACH = Path(__file__).resolve().parent / "shape_reach.txt"


def compared() -> dict[str, int]:
    """Per client: how many of its calls this file can actually compare."""
    shapes = route_shapes()
    out = {}
    for client in sorted(CLIENTS):
        n = 0
        for _name, verb, path, _declared, _is_list in typed_calls(client):
            route = _route_for(verb, path)
            if route is not None and (verb, route.path) in shapes:
                n += 1
        out[client] = n
    return out


def _reach() -> dict[str, int]:
    rows = [ln.strip() for ln in REACH.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.startswith("#")]
    return {a.strip(): int(b) for a, b in (r.split(":", 1) for r in rows)}


def test_the_comparison_is_reading_every_client():
    """Liveness, per client, against a record rather than a hand-set floor.

    The first version of this sweep read **zero** call sites — its regex
    stopped one character before the opening backtick — and reported that the
    console agreed with the backend everywhere. It was right about every call
    it looked at, because it looked at none.

    A record rather than a ratchet because the numbers here are honestly
    lopsided: this product's Android shell compares two dozen calls and
    JIM-mini's compares three, since that shell discards the body on 111 of
    its 114 calls. A floor of three would fail the estate's own rule that a
    floor be worth having; a recorded three that must not become two is the
    same protection without pretending it is a floor.
    """
    now, recorded = compared(), _reach()
    lost = sorted(f"{c}: {n} compared, was {recorded[c]}"
                  for c, n in now.items() if n < recorded.get(c, 0))
    assert not lost, (
        "these clients lost comparisons — a reader has stopped matching:\n    "
        + "\n    ".join(lost)
        + "\n  A sweep that reads nothing agrees with everything. Fix the "
          "reader, or lower the row deliberately and say why.")
    assert set(now) == set(recorded), (
        f"clients {sorted(now)} against recorded {sorted(recorded)}")


def test_every_client_is_reachable_at_all():
    """A client this file cannot read is a client it silently exempts."""
    blind = sorted(c for c, n in compared().items() if n == 0)
    assert not blind, (
        f"{blind} contribute no comparisons at all — either the shell is "
        "absent from this checkout or its reader has gone blind, and the two "
        "read identically from here")


def test_the_route_side_is_still_being_read():
    shapes = ratchets.floor("route.declared_shapes")
    assert len(route_shapes()) >= shapes, (
        f"only {len(route_shapes())} routes have a decisive shape against a "
        f"floor of {shapes} — the annotation reader has stopped resolving")


def test_a_union_that_names_both_shapes_is_not_a_disagreement():
    """The rule that keeps this from punishing a careful client, as a unit."""
    assert _declares_list("Row[]") is True
    assert _declares_list("Row") is False
    assert _declares_list("{ comments: C[] } | C[]") is None
    assert _declares_list("Array<Row>") is True


def test_the_route_reader_prefers_the_declared_response_model():
    """A route that declares `response_model` answers with it whatever the
    function's own annotation says, and the reader must agree with FastAPI
    rather than with the source."""
    shapes = route_shapes()
    assert any(v for v in shapes.values()), "no route reads as a list at all"
    assert any(not v for v in shapes.values()), "no route reads as an object"


def test_the_record_holds_only_live_rows():
    """A row for a disagreement that has since been fixed would excuse it
    coming back, so it fails rather than being tidied away later."""
    stale = sorted(_recorded() - set(disagreements()))
    assert not stale, ("these rows name a disagreement that no longer "
                       "exists — strike them:\n    " + "\n    ".join(stale))
    ceiling = int(re.search(r"# ceiling: (\d+)",
                            RECORD.read_text(encoding="utf-8")).group(1))
    assert len(_recorded()) <= ceiling


@pytest.mark.parametrize("verb", ["GET", "POST", "PUT", "DELETE"])
def test_the_verb_comes_from_the_call_and_not_the_path(verb):
    """The reader's own defect, kept as a test.

    Keying on the path literal instead of the call expression paired every
    `POST /x` with the `GET /x` beside it in the client, and reported sixty
    disagreements that were all the same mistake. Each verb must be reachable
    from the calls themselves.
    """
    seen = [c for c in calls() if c[1] == verb]
    assert seen, f"no {verb} call found — the verb reader has stopped matching"
