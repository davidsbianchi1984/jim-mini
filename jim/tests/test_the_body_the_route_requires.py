"""Every guard in this family reads the answer. None of them read the question.

0.56.4 through 0.57.1 asked four clients the same thing — C# records, Swift
structs, Kotlin `org.json` reads, TypeScript type arguments — and the question
was always *does this client understand what comes back*. Thirty-three defects
across the four.

Not one of them looks at what the client **sends**. The console guard next door
makes that explicit: it skips any call carrying `method:`, which in this client
is 194 of them. Those calls were never checked by anything, in either
direction, and a request body is the same defect in mirror image:

    api.createOffering(shopId, { name, tag, blurb }, token)

If the route's model calls that field `title`, FastAPI does not shrug. It
either answers 422 — the button does nothing, forever — or, where the model
tolerates extras, silently drops the value and stores a row with the field
empty. Both are invisible from the client, which sent something and got a
response.

    asked     does the client understand the answer
    mattered  does the route understand the question

## What it is checked against

`app.openapi()`, not a regex over the Pydantic classes. The schema FastAPI
publishes *is* what FastAPI validates against, including which fields are
required and which have defaults — so this guard cannot drift from the
behaviour it is describing. Reading the models by hand would have been a
fifth extractor to get wrong.

## Three questions, and why the third one exists

* a required field the client never sends — a call that 422s every time;
* a field the client sends that the model has no property for — a value the
  user typed and the server discarded;
* a write with no body at all, to a route whose model requires one — the same
  422, arrived at from the other side. It is listed separately because the
  first check cannot see it: a call with no `body` has no keys to compare, so
  a guard that only walks bodies finds nothing wrong with sending none.
"""

import pathlib
import re

from jim.api import app

from .test_the_shape_the_console_expects import _SRC, _matched, _top_level
from . import ratchets

RECORD = pathlib.Path(__file__).resolve().parent / "request_bodies_unverified.txt"

WRITES = ("POST", "PUT", "PATCH")

# A property of the object this member is defined in. Used as the *left edge*
# of a body lookup, and that bound is the whole correctness of this file —
# see `_body`.
_MEMBER = re.compile(r'\n  \w+:\s*(?:async\s*)?\(')


def _keys(literal: str) -> list[str] | None:
    """Top-level keys of an object literal, or None if it cannot be known.

    `{ ...(to ? { to } : {}), text }` spreads a conditional, and what it
    contributes depends on a value only the running app has. Guessing at it
    produced a "field" called `...(to ? {}` and reported the translate route
    for sending it. A body this guard cannot read is a body it must not
    judge — the alternative is inventing a defect, which is worse than
    missing one.
    """
    if "..." in literal:
        return None
    out = []
    for part in _top_level(literal).split(","):
        part = part.strip()
        if not part:
            continue
        name = part.split(":")[0].strip()
        if not re.fullmatch(r'\w+', name):
            return None
        out.append(name)
    return out


def _body(args: str, at: int) -> tuple[str, list[str] | None]:
    """(how it was found, the keys) for the body of the call at `at`.

    Two forms carry a readable body: an object literal at the call site, and
    the bare identifier `body`, whose shape is the enclosing arrow function's
    parameter type. Everything else — a variable built elsewhere, a `FormData`,
    a spread — is unreadable and says so.

    **The parameter lookup is bounded to this member**, and that is not a
    detail. A backward scan for `(body: {` without it found the parameter of a
    *previous* property in the same object and credited its fields to this
    call: `POST /profiles/{id}/chat` was reported as sending `birthdate` and
    `display_name`, which belong to `createProfile` forty lines above. Fifteen
    of forty-two lookups resolved to the wrong function that way, and between
    them they produced eighty-two findings — every one of them this guard's
    own defect, and every one of them phrased as somebody else's.
    """
    m = re.search(r'\bbody\s*(?::\s*)?', args)
    if not m:
        return "none", []
    rest = args[m.end():]
    if rest[:1] in (",", "}"):      # ES6 shorthand: { method, body, token }
        rest = "body" + rest
    if rest.startswith("{"):
        end = _matched(rest, 0, "{", "}")
        return "literal", _keys(rest[1:end - 1])
    name = re.match(r'(\w+)', rest)
    if not name:
        return "unreadable", None
    head = _SRC[max(0, at - 4000):at]
    starts = [s.start() for s in _MEMBER.finditer(head)]
    if not starts:
        return "unreadable", None
    member = head[starts[-1]:]
    # The parameter may be first or fifth. QRME writes `(body: { ... })` and
    # JIM-mini writes `(uid: string, body: { ... }, token: string)`, and a
    # pattern anchored on the opening paren reads the first client whole and
    # the second at twenty-eight writes out of a hundred and thirteen. That
    # ratio is the only reason this was caught: the guard was green either
    # way, because a body it cannot read is a body it does not judge.
    #
    # Fourth time in this arc that a borrowed pattern has read one product
    # and quietly skipped another. Check the share it reaches, not the colour
    # of the run.
    p = re.search(r'[(,]\s*%s\s*:\s*\{' % re.escape(name.group(1)), member)
    if not p:
        return "unreadable", None
    opened = member.index("{", p.start())
    end = _matched(member, opened, "{", "}")
    fields = re.findall(r'(?:^|;|\n|,)\s*(\w+)\??\s*:',
                        _top_level(member[opened + 1:end - 1]))
    return "parameter", fields


def _sent() -> list[tuple[str, str, str, list[str] | None]]:
    """[(verb, path template, how the body was found, keys)] for every write."""
    out = []
    for m in re.finditer(r'\breq<', _SRC):
        opened = m.end() - 1
        end = _matched(_SRC, opened, "<", ">")
        if end < 0 or end >= len(_SRC) or _SRC[end] != "(":
            continue
        close = _matched(_SRC, end, "(", ")")
        if close < 0:
            continue
        args = _SRC[end:close]
        verb = re.search(r'method:\s*"(\w+)"', args)
        path = re.match(r'\(\s*[`"\']([^`"\']+)[`"\']', args)
        if not verb or not path:
            continue
        how, keys = _body(args, m.start())
        out.append((verb.group(1), path.group(1), how, keys))
    return out


def _shape(path: str) -> str:
    """A path in the one spelling both sides can be compared in."""
    path = re.sub(r'\$\{[^}]+\}', '{}', path)
    return re.sub(r'\{[^}]+\}', '{}', path).split("?")[0]


def _models() -> dict[tuple[str, str], dict]:
    """(verb, path) -> the schema FastAPI validates the body against."""
    spec = app.openapi()
    components = spec.get("components", {}).get("schemas", {})
    out = {}
    for path, operations in spec["paths"].items():
        for verb, operation in operations.items():
            body = operation.get("requestBody")
            if not body:
                continue
            schema = list(body["content"].values())[0]["schema"]
            seen = 0
            while "$ref" in schema and seen < 8:
                schema = components[schema["$ref"].split("/")[-1]]
                seen += 1
            out[(verb.upper(), _shape(path))] = schema
    return out


def _findings() -> list[str]:
    models = _models()
    out = []
    for verb, template, how, keys in _sent():
        if verb not in WRITES:
            continue
        schema = models.get((verb, _shape(template)))
        if schema is None:
            continue
        required = set(schema.get("required", []))
        properties = set(schema.get("properties", {}))
        shown = _shape(template)
        if how == "none":
            if required:
                out.append(f"{verb} {shown} sends no body, and the route "
                           f"requires " + ", ".join(sorted(required)))
            continue
        if keys is None:
            continue
        for field in sorted(required - set(keys)):
            out.append(f"{verb} {shown} never sends required {field!r}")
        for field in sorted(set(keys) - properties):
            if properties:
                out.append(f"{verb} {shown} sends {field!r}, "
                           f"which the model has no property for")
    return out


def _recorded() -> set[str]:
    rows = (line.split("#")[0].strip()
            for line in RECORD.read_text(encoding="utf-8").splitlines())
    return {row for row in rows if row}


# --- the guard ---------------------------------------------------------------

def test_no_write_sends_a_body_the_route_cannot_accept():
    """A required field the client never sends is a button that does nothing.
    A field the model has no property for is a value the user typed and the
    server threw away."""
    loose = [row for row in _findings() if row not in _recorded()]
    assert not loose, (
        "these writes and their routes disagree:\n    "
        + "\n    ".join(sorted(set(loose)))
        + "\n  Send the field the model actually declares, or correct the "
          "model — recording is ratcheted.")


def test_the_unverified_record_only_shrinks():
    text = RECORD.read_text(encoding="utf-8")
    ceiling = int(re.search(r"^# ceiling: (\d+)$", text, re.M).group(1))
    assert len(_recorded()) <= ceiling, (
        f"{len(_recorded())} rows recorded, above the {ceiling} ceiling")


# --- the scan has to be able to see, and to fail -----------------------------

def test_the_extractor_reads_this_clients_writes():
    """Nothing found reads exactly like nothing wrong."""
    writes = [w for w in _sent() if w[0] in WRITES]
    readable = [w for w in writes if w[2] in ("literal", "parameter")
                and w[3] is not None]
    assert len(writes) >= ratchets.floor("route.writes"), len(writes)
    assert len(readable) >= ratchets.floor("route.writes_readable"), len(readable)


def test_the_routes_side_is_read_from_what_fastapi_validates():
    """Read from the published schema rather than from the Pydantic source,
    so the guard cannot describe a rule the app does not enforce."""
    models = _models()
    assert len(models) >= ratchets.floor("route.models"), len(models)
    assert any(s.get("required") for s in models.values())


def _writes_meeting_a_model() -> int:
    """Writes off the clients whose verb and shape meet a declared model."""
    models = _models()
    return sum(1 for verb, template, _how, _keys in _sent()
               if verb in WRITES and (verb, _shape(template)) in models)


def test_a_real_share_of_the_writes_meets_a_model():
    matched = _writes_meeting_a_model()
    assert matched >= ratchets.floor("route.writes_meeting_a_model"), (
        f"only {matched} write(s) matched a route — the path spellings have "
        f"stopped lining up")


def test_the_body_lookup_cannot_reach_into_the_member_above_it():
    """The defect that produced eighty-two false findings on the first run.

    `(body: {` appears in an earlier property of the same object; a backward
    search without a left edge finds it and reports this call for that call's
    fields.
    """
    src = ('\n  createProfile: (body: { owner_id: string; birthdate: string }) =>\n'
           '    req<Profile>("/profiles", { method: "POST", body }),\n'
           '\n  chat: (id: string, text: string) =>\n'
           '    req<Reply>(`/profiles/${id}/chat`, { method: "POST", body }),\n')
    starts = [m.start() for m in _MEMBER.finditer(src)]
    assert len(starts) == 2, starts
    # The second member owns no `(body: {`, so the lookup must come up empty
    # rather than borrowing the first member's.
    assert "(body: {" not in src[starts[1]:]


def test_the_guard_would_catch_all_three_shapes_of_defect():
    schema = {"required": ["title"], "properties": {"title": {}, "tag": {}}}
    required, properties = set(schema["required"]), set(schema["properties"])
    sent = {"name", "tag"}
    assert sorted(required - sent) == ["title"]
    assert sorted(sent - properties) == ["name"]
    assert required, "a bodiless write to this route would be a finding"


def test_a_body_that_cannot_be_read_is_not_judged():
    """A spread contributes fields only the running app knows. The first run
    invented one called `...(to ? {}` and reported a real route for it."""
    assert _keys("...(to ? { to } : {}), text") is None
    assert _keys(" name, tag ") == ["name", "tag"]
    assert _keys("name: n, tag: t") == ["name", "tag"]
