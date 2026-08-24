"""The same question, asked of the iOS client.

0.56.4 built a guard that drives every GET binding in the **Windows** client
and checks each record against what the route actually returns. 0.56.7 taught
it to check declared types as well as names, and between them they found
nineteen defects in that one file.

Then, by hand, chasing something else:

    struct WearableBoard: Decodable {
        let kinds: [String]?          // the route sends a map
        let refused: [String: String]?
    }
    struct MicVocabularyOut: Decodable {
        let widths: [String: String]?  // no route has ever sent `widths`
    }

iOS was wrong in four places, in exactly the two ways the Windows guard was
built to catch, and **nothing would have told me**. I found them by reading.
The 0.56.7 changelog says so in as many words: *"nothing yet reads Swift or
Kotlin the same way, and that is the next thing this guard is missing."*

    asked     is the client we check correct
    mattered  is every client checked

## Why this is a separate file rather than a parameter

The Windows guard's docstring explains that C# records are the one place in
this codebase where the whole wire surface is declared with its types. That is
still true, and it is why that file reads them. But *only-place* was doing two
jobs in that sentence: the best place to enumerate the surface, and the only
place worth checking. It was never the second.

Swift declares its shapes differently — `struct X: Decodable { let f: T }`,
with the property name doing what `JsonPropertyName` does in C# because this
client sets no key-decoding strategy. So the extractor is this language's, and
`test_the_extractor_reads_the_swift_client` exists because a pattern borrowed
from the C# guard finds nothing here, and nothing found reads as nothing
wrong.

The comparison itself — what shape a JSON value is, and whether a declared
type can decode it — is imported from the Windows guard rather than copied.
Two guards that disagree about what `list` means would be worse than one.
"""

import json
import pathlib
import re

from .conftest import enroll
from .test_the_shape_the_client_expects import (
    _accepts as _cs_accepts, _descend, _returned_keys, _shape_of, _standing)
from . import ratchets

REPO = pathlib.Path(__file__).resolve().parents[2]
SWIFT_CLIENT = REPO / "native/ios/Sources/ApiClient.swift"
RECORD = pathlib.Path(__file__).resolve().parent / "swift_shapes_unverified.txt"

_SRC = SWIFT_CLIENT.read_text(encoding="utf-8")

# A body with no braces in it. This client writes both
#     struct Health: Decodable { let status: String }
# and the multi-line form, and a pattern anchored on `\n}` misses the first —
# then runs on to the *next* struct's closing brace and reports that struct's
# fields under this one's name. Fifty of the first run's "findings" were that.
_STRUCT = re.compile(r'struct (\w+): (?:Decodable|Codable)[^{]*\{([^{}]*)\}')
_LET = re.compile(r'let (\w+):\s*([^;\n/]+)')
# `func x() async throws -> T { try await request("/path") }`. A binding that
# passes `method:` is not a GET and is left alone.
_BINDING = re.compile(
    r'->\s*([\w\[\]:\s]+?)\s*\{\s*\n?\s*try await request\(\s*"([^"]+)"([^\n]*)')


def _structs() -> dict[str, list[tuple[str, str]]]:
    """Struct name -> [(wire name, declared Swift type)].

    The property name *is* the wire name here: this client sets no
    `keyDecodingStrategy`, which is why its properties are snake_case.
    """
    return {name: [(f, t.strip().rstrip("?")) for f, t in _LET.findall(body)]
            for name, body in _STRUCT.findall(_SRC)}


def test_no_extracted_struct_swallowed_the_next_one():
    """The C# guard grew this assertion last release after a malformed record
    let one body run into the next. The Swift extractor made the same mistake
    for a different reason — single-line structs — and this is the same
    assertion, which is the point of writing it down."""
    for name, body in _STRUCT.findall(_SRC):
        assert "struct " not in body, name


def _bindings() -> list[tuple[str, str]]:
    """[(struct name, path template)] for every GET this client makes."""
    return [(t.strip().strip("[]").strip(), p)
            for t, p, rest in _BINDING.findall(_SRC) if "method:" not in rest]


def _recorded() -> set[str]:
    rows = (line.split("#")[0].strip()
            for line in RECORD.read_text(encoding="utf-8").splitlines())
    return {row for row in rows if row}


def _accepts(swift: str, shape: str) -> bool:
    """Whether a Swift type can decode a value of that shape."""
    t = swift.replace(" ", "")
    if shape == "null":
        return True
    if t.startswith("[") and ":" in t:
        return shape == "object"
    if t.startswith("["):
        return shape == "list"
    if t == "String":
        return shape == "string"
    if t == "Bool":
        return shape == "bool"
    if t in {"Int", "Double", "Float"}:
        return shape == "number"
    if t in {"AnyCodable", "JSONValue"}:
        return True
    return shape == "object"


def _findings(struct: str, body, structs, seen=()) -> list[str]:
    """Fields this struct declares that the response cannot give it."""
    if struct not in structs or struct in seen:
        return []
    if not isinstance(body, dict):
        if isinstance(body, list):
            body = next((x for x in body if isinstance(x, dict)), None)
        if body is None:
            return []
    out = []
    for wire, typ in structs[struct]:
        if wire not in body:
            out.append(f"{struct}.{wire} is not on the wire")
            continue
        shape = _shape_of(body[wire])
        if not _accepts(typ, shape):
            out.append(f"{struct}.{wire} is declared {typ} and arrives as a "
                       f"{shape}")
            continue
        nested = typ.strip("[]").split(":")[-1].strip()
        out += _findings(nested, _descend(body, wire), structs, seen + (struct,))
    return out


def _drive(client, uid: str, other_id: str):
    """Every GET binding, driven. Yields (path, struct, findings|None)."""
    structs = _structs()
    subs = {"id": uid, "uid": uid, "userId": uid, "otherId": other_id}
    for struct, template in _bindings():
        if struct not in structs:
            continue
        path = template
        for key, value in subs.items():
            path = path.replace("\\(" + key + ")", value)
        if "\\(" in path or "{" in path:
            yield template, struct, None
            continue
        response = client.get(path)
        if response.status_code != 200:
            yield template, struct, None
            continue
        try:
            body = response.json()
        except (ValueError, json.JSONDecodeError):
            yield template, struct, None
            continue
        if _returned_keys(body) is None:
            yield template, struct, None
            continue
        yield template, struct, _findings(struct, body, structs)


# --- the guard ---------------------------------------------------------------

def test_no_swift_struct_promises_what_the_route_cannot_give_it(client):
    """Both halves at once: a field the route never sends, and a field whose
    declared type cannot decode what arrives. iOS had four of these and no
    guard read it."""
    uid, other = _standing(client)
    loose = []
    for _, _, findings in _drive(client, uid, other):
        for row in findings or []:
            if row.split(" is ")[0] not in _recorded():
                loose.append(row)
    assert not loose, (
        "the iOS client declares these and the route disagrees:\n    "
        + "\n    ".join(sorted(set(loose)))
        + "\n  Correct the struct to the shape the route actually has, or "
          "record the field with the state that produces it — recording is "
          "ratcheted.")


def test_the_unverified_record_only_shrinks():
    text = RECORD.read_text(encoding="utf-8")
    ceiling = int(re.search(r"^# ceiling: (\d+)$", text, re.M).group(1))
    assert len(_recorded()) <= ceiling, (
        f"{len(_recorded())} rows recorded, above the {ceiling} ceiling")


def test_every_recorded_row_names_a_field_that_exists():
    declared = {f"{s}.{f}"
                for s, fields in _structs().items() for f, _ in fields}
    stale = sorted(_recorded() - declared)
    assert not stale, (
        "these rows name fields the client no longer declares:\n    "
        + "\n    ".join(stale) + "\n  Strike them.")


# --- the scan has to be able to see, and to fail -----------------------------

def test_the_extractor_reads_the_swift_client():
    """A pattern borrowed from the C# guard finds nothing in this file, and
    nothing found reads exactly like nothing wrong."""
    fields = sum(len(f) for f in _structs().values())
    assert len(_structs()) >= ratchets.floor("swift.structs"), len(_structs())
    assert fields >= ratchets.floor("swift.struct_fields"), fields
    assert len(_bindings()) >= ratchets.floor("swift.bindings"), len(_bindings())


def test_the_scan_reaches_a_real_share_of_the_bindings(client):
    uid, other = _standing(client)
    driven = [f for _, _, f in _drive(client, uid, other)
              if f is not None]
    assert len(driven) >= 15, (
        f"only {len(driven)} binding(s) were reachable — the fixture or the "
        f"extractor has stopped working")


def test_the_guard_would_catch_both_shapes_of_defect():
    """Driven against what iOS actually had: a field no route sends, and a
    list declared for a map."""
    structs = {"Board": [("widths", "[String: String]"),
                         ("kinds", "[String]")]}
    body = {"kinds": {"watch": "on the wrist"}}
    assert _findings("Board", body, structs) == [
        "Board.widths is not on the wire",
        "Board.kinds is declared [String] and arrives as a object"]


def test_swift_and_csharp_agree_about_what_a_list_is():
    """Two guards that disagreed about a shape would be worse than one."""
    for shape in ("list", "object", "string", "number", "bool"):
        assert _accepts("[String]", shape) == _cs_accepts("string[]", shape)
        assert _accepts("String", shape) == _cs_accepts("string", shape)
