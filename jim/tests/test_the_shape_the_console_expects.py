"""The same question, asked of the client that most people actually use.

0.56.4 through 0.57.0 built this guard three times — for the Windows client's
C# records, the iOS client's Swift structs, and the Android client's `org.json`
reads. Nineteen defects in C#, nine in Swift, eight in Kotlin, and the running
lesson of all three was that fixing a defect in one client is not fixing the
defect.

There is a fourth client. `test_the_console_is_a_client_too.py` next door was
written for exactly this reason — it found that the union of four surfaces was
hiding sixty-four routes a desktop owner could not reach — and it asks whether
the console *calls* each route. It has never asked what the console does with
the answer.

    asked     can the console reach every route
    mattered  does the console read back what the route sends

This client declares more than the other three combined. Every call carries
its expected shape as a type argument:

    req<{ provider: string; effective: string }>(`/profiles/${pid}/model`)

which is the same claim a C# record makes, written differently. And it fails
the same quiet way Kotlin does, for a different reason: TypeScript is erased
at build time, so nothing checks that declaration against reality at runtime.
A field the route does not send is `undefined`, and `{undefined}` in JSX
renders as nothing at all. Not a crash, not a blank where a value should be —
*nothing*, with the layout closing up around it as though the field were never
meant to be there.

## Optional means optional

The Swift guard treats `let x: T?` as a field that must still be present, and
absorbed the difference into a record file of conditional states. That was the
right call there, because that client marks nearly everything optional.

This one does not: it writes `answered?: number` where the field genuinely
comes and goes, and `answered: number` where it does not. So a `?` here is a
declaration that absence is expected, and reporting it as missing would be
reporting the client for being right. Required fields must be on the wire;
optional ones are checked for type when they arrive and left alone when they
do not.

That is a deliberate difference from the sibling guards rather than an
oversight, and it is the reason this one can be read as a list of defects
instead of a list of states.
"""

import json
import pathlib
import re

from .test_the_shape_the_client_expects import (
    _descend, _returned_keys, _shape_of, _standing)
from . import ratchets

REPO = pathlib.Path(__file__).resolve().parents[2]
CONSOLE_CLIENT = REPO / "app/src/api.ts"
RECORD = pathlib.Path(__file__).resolve().parent / "console_shapes_unverified.txt"


def _without_comments(text: str) -> str:
    """Comments, gone — but not the `//` inside a URL.

    `req<Health>("http://...")` is not a comment, and stripping from the
    slashes to end of line ate the closing paren of every call that mentioned
    one. A `//` that follows a colon is part of a scheme.
    """
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    return re.sub(r'(?<!:)//[^\n]*', '', text)


_SRC = _without_comments(CONSOLE_CLIENT.read_text(encoding="utf-8"))

# `interface X { ... }` and `type X = { ... }` are the same declaration to a
# reader of this file, and the client uses both.
_DECL = re.compile(r'(?:export )?(?:interface (\w+)\s*|type (\w+)\s*=\s*)(?=\{)')
_FIELD = re.compile(r'(?:^|;|\n)\s*(\w+)(\??)\s*:\s*([^;\n]+)')


def _matched(text: str, i: int, opener: str, closer: str) -> int:
    """Index just past the bracket matching `text[i]`, or -1.

    Written as a walk rather than a regex because both things this file has to
    read — a type body and a type argument — nest, and both can contain a
    string with a bracket in it. `req<Record<string, unknown>>` closes on the
    *second* `>`, and a pattern that stopped at the first read the shape as
    `Record<string, unknown` and resolved it to nothing.
    """
    depth = 0
    while i < len(text):
        c = text[i]
        if c in '"\'`':
            quote, i = c, i + 1
            while i < len(text) and text[i] != quote:
                i += 2 if text[i] == '\\' else 1
        elif c == opener:
            depth += 1
        elif c == closer:
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return -1


def _top_level(body: str) -> str:
    """The fields of this type, with nested object bodies emptied.

    `{ card: { id: string }, name: string }` declares two fields, and a flat
    scan of that text finds three — `id` among them, credited to the response
    rather than to `card`. The C# guard learned this in 0.56.4 and the Swift
    guard in 0.56.8, both after reporting a real route for a field belonging
    to something inside it.

    **Emptied, not deleted.** Removing the braces along with their contents
    turned `delegation: { ... } | null` into `delegation: | null`, and the
    guard then reported a real field as *declared `| null` and arriving as a
    bool* — a sentence that should have been unwriteable. The nested body is
    not this type's business; the fact that a body was *there* is.
    """
    out, depth = [], 0
    for ch in body:
        if ch == '{':
            depth += 1
            if depth == 1:
                out.append('{')
        elif ch == '}':
            depth -= 1
            if depth == 0:
                out.append('}')
        elif depth == 0:
            out.append(ch)
    return ''.join(out)


def _shapes() -> dict[str, list[tuple[str, bool, str]]]:
    """Type name -> [(wire name, optional, declared type)].

    The property name *is* the wire name: this client does no key mapping,
    which is why its declarations are snake_case in a camelCase file.
    """
    out = {}
    for m in _DECL.finditer(_SRC):
        name = m.group(1) or m.group(2)
        start = _SRC.index('{', m.end() - 1)
        end = _matched(_SRC, start, '{', '}')
        if end < 0:
            continue
        out[name] = [(f, opt == '?', t.strip().rstrip(',;'))
                     for f, opt, t in _FIELD.findall(_top_level(_SRC[start + 1:end - 1]))]
    return out


def _bindings() -> list[tuple[str, str, str]]:
    """[(declared shape, path template, the whole argument list)] per call.

    The arguments are read to the call's own closing paren rather than to the
    end of the line, and that is not tidiness. This client writes

        req<WallPost>(`/profiles/${profileId}/wall`,
          { method: "POST", body, token }),

    with the verb on the *second* line. A GET check that read one line called
    that a GET, drove `GET /profiles/{id}/wall`, and compared `WallPost`
    against whatever the list route returns — every field missing, in five
    different types at once. Thirty of this guard's first thirty-eight
    findings were that.

    It is the third time in three releases that the verb check has been the
    defect: the Kotlin guard looked for the keyword `method` when the verb was
    positional, and before that the C# guard read a write's reply as a read's.
    Whatever says *this is a GET* is worth more care than the rest of the
    extractor put together, because getting it wrong does not fail — it
    accuses.
    """
    out = []
    for m in re.finditer(r'\breq<', _SRC):
        opened = m.end() - 1
        end = _matched(_SRC, opened, '<', '>')
        if end < 0 or end >= len(_SRC) or _SRC[end] != '(':
            continue
        close = _matched(_SRC, end, '(', ')')
        if close < 0:
            continue
        args = _SRC[end:close]
        path = re.match(r'\(\s*[`"\']([^`"\']+)[`"\']', args)
        if not path:
            continue
        out.append((_SRC[opened + 1:end - 1].strip(), path.group(1), args))
    return out


def _gets() -> list[tuple[str, str]]:
    """[(declared shape, path)] for every call that is a GET."""
    return [(shape, path) for shape, path, args in _bindings()
            if "method:" not in args]


def _recorded() -> set[str]:
    rows = (line.split("#")[0].strip()
            for line in RECORD.read_text(encoding="utf-8").splitlines())
    return {row for row in rows if row}


def _accepts(ts: str, shape: str) -> bool:
    """Whether a value of that shape can inhabit this declared type."""
    t = ts.replace(" ", "")
    if shape == "null":
        return True
    # `A | null`, `"a" | "b"`, `number | string` — a union accepts anything any
    # arm accepts. Written before the array check because `(A | B)[]` is a
    # list, not a union, and the parens are what say so.
    if "|" in t and not t.endswith("[]"):
        return any(_accepts(arm, shape) for arm in t.split("|"))
    if t.endswith("[]") or t.startswith("Array<"):
        return shape == "list"
    if t.startswith("Record<") or t.startswith("Partial<"):
        return shape == "object"
    if t == "string" or (t.startswith('"') and t.endswith('"')):
        return shape == "string"
    if t == "number":
        return shape == "number"
    if t == "boolean":
        return shape == "bool"
    if t in {"unknown", "any", "object"}:
        return True
    return shape == "object"


def _fields_of(ts: str, shapes) -> list[tuple[str, bool, str]] | None:
    """The declared fields behind a type expression, or None if it is opaque.

    Handles the two composites this client writes: `T[]`, and the intersection
    `Profile & { owner_token: string }`, which is one shape with the fields of
    both and is how nearly every create-and-return call declares itself.
    """
    t = ts.strip()
    if t.endswith("[]"):
        return _fields_of(t[:-2].strip().strip("()"), shapes)
    if "&" in t and not t.startswith("{"):
        out = []
        for arm in t.split("&"):
            got = _fields_of(arm.strip(), shapes)
            if got:
                out += got
        return out or None
    if t.startswith("{"):
        end = _matched(t, 0, '{', '}')
        return [(f, opt == '?', ty.strip().rstrip(',;'))
                for f, opt, ty in _FIELD.findall(_top_level(t[1:end - 1]))]
    return shapes.get(t)


def _arms(ts: str) -> list[str]:
    """The arms of a top-level union, or the one type if it is not a union.

    Split at depth zero only: `{ a: string | null }` is one arm, and slicing
    it at the inner `|` produced two halves that were not types at all.
    """
    out, depth, buf = [], 0, []
    for ch in ts:
        if ch in '{[(<':
            depth += 1
        elif ch in '}])>':
            depth -= 1
        if ch == '|' and depth == 0:
            out.append(''.join(buf))
            buf = []
        else:
            buf.append(ch)
    out.append(''.join(buf))
    return [a.strip() for a in out if a.strip()]


def _findings(ts: str, body, shapes, seen=()) -> list[str]:
    """What this declaration promises that the response cannot give it.

    A union is satisfied by *any* arm. The friends-suggestions call declares
    `{ suggestions: ... } | { ... }[]`, and reading the first arm alone
    reported it against a shape it never claimed to be the only one. It was
    wrong anyway — the key is `suggested`, and neither arm had it — but a
    guard that is right by accident is a guard that will be wrong on purpose
    the next time.
    """
    arms = _arms(ts)
    if len(arms) > 1:
        each = [_findings(arm, body, shapes, seen) for arm in arms]
        if any(not f for f in each):
            return []
        return min(each, key=len)
    fields = _fields_of(ts, shapes)
    if not fields or ts in seen:
        return []
    if not isinstance(body, dict):
        if isinstance(body, list):
            body = next((x for x in body if isinstance(x, dict)), None)
        if body is None:
            return []
    named = ts.strip().rstrip("[]").strip()
    out = []
    for wire, optional, typ in fields:
        if wire not in body:
            # A `?` is the client saying this comes and goes. Believing it is
            # the difference between a list of defects and a list of states.
            if not optional:
                out.append(f"{named}.{wire} is not on the wire")
            continue
        found = _shape_of(body[wire])
        if not _accepts(typ, found):
            out.append(f"{named}.{wire} is declared {typ} and arrives as a "
                       f"{found}")
            continue
        out += _findings(typ, _descend(body, wire), shapes, seen + (ts,))
    return out


# A template expression this fixture can supply a value for. Anything else —
# `${encodeURIComponent(state)}`, `${page * size}` — is a value only the
# running app knows, and the path is unreachable rather than wrong.
_SUBS = ("id", "uid", "userId", "profileId", "pid", "profile",
         "interactorId", "interactor", "otherId")


def _drive(client, uid: str, other_id: str):
    """Every GET binding, driven. Yields (path, shape, findings|None)."""
    shapes = _shapes()
    values = {"id": uid, "uid": uid, "userId": uid, "profileId": uid,
              "pid": uid, "profile": uid, "interactorId": other_id,
              "interactor": other_id, "otherId": other_id}
    for ts, template in _gets():
        if _fields_of(ts, shapes) is None:
            continue
        path = template
        for name in _SUBS:
            path = path.replace("${" + name + "}", values[name])
        if "${" in path or "{" in path:
            yield template, ts, None
            continue
        # A query string whose value was an expression is now a bare `?k=`,
        # which asks a different question than the app ever asks. 0.57.0 shipped
        # this lesson in the Kotlin guard after reporting a route for a key it
        # sends perfectly well.
        if path.rstrip().endswith(("=", "&", "?")):
            yield template, ts, None
            continue
        response = client.get(path)
        if response.status_code != 200:
            yield template, ts, None
            continue
        try:
            body = response.json()
        except (ValueError, json.JSONDecodeError):
            yield template, ts, None
            continue
        if _returned_keys(body) is None:
            yield template, ts, None
            continue
        yield template, ts, _findings(ts, body, shapes)


# --- the guard ---------------------------------------------------------------

def test_no_console_declaration_promises_what_the_route_cannot_give_it(client):
    """A required field the route never sends is `undefined` in a component,
    and `{undefined}` renders as nothing — the layout closes up around it and
    the screen looks finished."""
    uid, other = _standing(client)
    loose = []
    for _, _, findings in _drive(client, uid, other):
        for row in findings or []:
            if row.split(" is ")[0] not in _recorded():
                loose.append(row)
    assert not loose, (
        "the console declares these and the route disagrees:\n    "
        + "\n    ".join(sorted(set(loose)))
        + "\n  Correct the declaration to the shape the route actually has, "
          "mark it optional if it genuinely comes and goes, or record it with "
          "the state that produces it — recording is ratcheted.")


def test_the_unverified_record_only_shrinks():
    text = RECORD.read_text(encoding="utf-8")
    ceiling = int(re.search(r"^# ceiling: (\d+)$", text, re.M).group(1))
    assert len(_recorded()) <= ceiling, (
        f"{len(_recorded())} rows recorded, above the {ceiling} ceiling")


def test_every_recorded_row_names_a_field_that_exists():
    """A row that describes nothing holds the ceiling up for nothing."""
    declared = {f"{name}.{f}"
                for name, fields in _shapes().items() for f, _, _ in fields}
    stale = sorted(_recorded() - declared)
    assert not stale, (
        "these rows name fields the console no longer declares:\n    "
        + "\n    ".join(stale) + "\n  Strike them.")


# --- the scan has to be able to see, and to fail -----------------------------

def test_the_extractor_reads_this_clients_declarations():
    """Neither the C#, the Swift nor the Kotlin pattern finds anything in a
    TypeScript file, and nothing found reads exactly like nothing wrong."""
    shapes = _shapes()
    assert len(shapes) >= ratchets.floor("console.shapes"), len(shapes)
    assert sum(len(f) for f in shapes.values()) >= ratchets.floor("console.shape_fields"), shapes
    assert len(_gets()) >= ratchets.floor("console.gets"), len(_gets())


def test_no_extracted_declaration_swallowed_the_next_one():
    """Fourth time this assertion is written, in the fourth language. The C#
    record ate a closing paren, the Swift struct ate the next struct, the
    Kotlin split ate a helper — each one found by writing this down."""
    for name, fields in _shapes().items():
        for wire, _, typ in fields:
            assert "interface " not in typ and "\n" not in typ, (name, wire)


def test_the_type_argument_is_read_to_its_own_closing_bracket():
    """`req<Record<string, unknown>>` closes on the second `>`. Stopping at the
    first read the shape as `Record<string, unknown`, which resolves to no
    declaration at all — and a binding that resolves to nothing is silently
    skipped, which is the failure that looks like success.

    Asserted on the walker rather than on a binding that happens to exist:
    the first version required this file to contain a `Record<>` call, which
    is true of one of the three consoles and made the check a fact about
    QRME's api.ts instead of a fact about the extractor.
    """
    assert _matched("<Record<string, unknown>>rest", 0, '<', '>') == 25
    assert _matched('<{ a: "x>y" }>after', 0, '<', '>') == 14
    assert _matched("<unclosed", 0, '<', '>') == -1


def test_optional_is_believed_and_required_is_not():
    """The whole reason this guard reads as defects rather than states."""
    shapes = {"Card": [("here", False, "string"), ("gone", True, "string")]}
    assert _findings("Card", {"here": "x"}, shapes) == []
    assert _findings("Card", {"gone": "x"}, shapes) == [
        "Card.here is not on the wire"]


def test_the_guard_would_catch_both_shapes_of_defect():
    """A required field no route sends, and a list declared for a map — the
    two shapes the other three clients were wrong in."""
    shapes = {"Board": [("widths", False, "Record<string, string>"),
                        ("kinds", False, "string[]")]}
    assert _findings("Board", {"kinds": {"watch": "on the wrist"}}, shapes) == [
        "Board.widths is not on the wire",
        "Board.kinds is declared string[] and arrives as a object"]


def test_the_scan_reaches_a_real_share_of_the_bindings(client):
    uid, other = _standing(client)
    driven = [f for _, _, f in _drive(client, uid, other)
              if f is not None]
    assert len(driven) >= ratchets.floor("console.driven"), (
        f"only {len(driven)} binding(s) were reachable — the fixture or the "
        f"extractor has stopped working")


def test_all_four_clients_agree_about_what_a_list_is():
    """Four guards that disagreed about a shape would be worse than one."""
    from .test_the_shape_the_client_expects import _accepts as _cs
    from .test_the_shape_the_swift_client_expects import _accepts as _swift
    for shape in ("list", "object", "string", "number", "bool"):
        assert _accepts("string[]", shape) == _cs("string[]", shape)
        assert _accepts("string[]", shape) == _swift("[String]", shape)
        assert _accepts("string", shape) == _cs("string", shape)
        assert _accepts("boolean", shape) == _cs("bool", shape)
