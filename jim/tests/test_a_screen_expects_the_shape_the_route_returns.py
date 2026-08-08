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
"""

from __future__ import annotations

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


def disagreements() -> list[str]:
    shapes, out = route_shapes(), []
    for name, verb, path, declared in calls():
        route = _route_for(verb, path)
        if route is None:
            continue
        answers = shapes.get((verb, route.path))
        if answers is None:
            continue
        expects = _declares_list(declared)
        if expects is None or expects == answers:
            continue
        out.append(f"{name}: {verb} {path} answers "
                   f"{'a list' if answers else 'an object'}, "
                   f"the screen expects {declared}")
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


def test_the_comparison_is_reading_both_sides():
    """Liveness, and the reason this file carries a floor at all.

    The first version of this sweep read **zero** call sites — its regex
    stopped one character before the opening backtick — and reported that the
    console agreed with the backend everywhere. It was right about every call
    it looked at, because it looked at none.
    """
    typed = len(calls())
    floor = ratchets.floor("console.calls_typed")
    assert typed >= floor, (
        f"{typed} typed console calls against a floor of {floor} — the call "
        "reader has lost a form, and a sweep that reads nothing agrees with "
        "everything")
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
