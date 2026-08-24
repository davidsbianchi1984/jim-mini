"""A member that isn't there, one layer out: a key that isn't on the wire.

0.58.2 closed by naming where the seam goes next. The receivers whose type is
known for free are now checked; the tier past them is the receiver whose
members are *keyed* rather than named — `optString("worn")`,
`GetProperty("mode")`, a `Decodable` property whose name **is** the wire key.
A renamed backend field is the same silent break as a renamed method, except
it does not fail on a build machine. It fails on a phone, quietly, as an empty
list or a nil string, and the screen renders as though the server had nothing
to say.

## What can be judged, and what cannot

Matching a key to the *route* it came from needs a type checker this machine
does not have. Matching it to the backend's whole vocabulary does not. So this
guard asks only the question it can answer honestly:

    is this key one the server can emit anywhere at all?

A key that appears nowhere in the backend is wrong with no judgement call
attached. A key that appears on some other route passes — this check is a
floor, not a ceiling, and it will not catch a field read off the wrong
response. Narrow and true.

## What the first run found

Four live breaks in this product, each of them a screen that renders empty:

* `GET /places/{surface}/{id}/overlay` answers with `overlays`. The iPhone and
  the Android read `worn`. That is the disclosure naming who in a place is
  wearing a face over their camera — the reason the feature is allowed at all
  — and on both phones it was always the empty list.
* `POST /auth/oauth/{provider}/start` answers with `url`. Both phones read
  `authorize_url`, got nil, and had nothing to open. Sign in with Google and
  Apple could not start on either.
* `/dock/where/{face}` answers with `screen`, `path` and `title`. The Android
  helper printed `screen · tab`, so half of every "where does this live"
  answer was blank.
* `/interactors/{id}/referrals` answers with `provider_id` and `opened_at`.
  All three shells read `specialist_profile_id` and a boolean `opened`.

Windows had the overlay, the sign-in and the fine-tuning run right, and the
referral wrong; the iPhone had them all wrong. There is no shell that is
reliably the correct one, which is the argument for checking all three.

## The rest of what it found

Nine `Decodable` structs whose result is discarded — `let _: Out = try await
request(…)` — named keys the routes do not send. Nothing read them, so nothing
broke; they were documentation of a wire shape that was never true. They are
empty structs now, which is what "this call's body is not read" actually looks
like.

## The traps it walked into first

Three, all in the reader rather than the code:

1. A regex that ends a struct at the first `\\n}` swallows everything after a
   nested one. `CustodyProvenance` has three.
2. `var stands: Bool { valid ?? verified ?? false }` is a computed property,
   and `let _: Ok = try await …` is a discarded binding. Neither is a key.
3. `case profileId = "profile_id"` renames it. Reporting `profileId` would be
   reporting the shell's own spelling as the server's.

And one in the vocabulary: the backend puts keys on the wire by four routes —
a dict literal, `out["key"] = …` after the fact, a Pydantic field, and
`dict(row)` over a SELECT, which makes every *column* a key. Reading only the
first of those reported some sixty fields that are on the wire every day.
"""

from __future__ import annotations

import re
from pathlib import Path
from . import ratchets


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
PKG = "jim"
ANDROID = "native/android/app/src/main/java/app/jim/guardian"

#: Keys that reach a screen verbatim from a *sibling* product's API, proxied
#: through this backend without reshaping — `pdi_client.provenance()` and
#: `qrme_client.localities()` / `.rooms()` both `return r.json()`. This
#: backend's vocabulary cannot judge them, and reporting them would be this
#: file inventing defects out of the tandem's own architecture. Each was
#: checked by hand against the emitting product before it was written down.
PROXIED: set[str] = {
    # PDI `GET /provenance/{key}` — pdi/api.py builds all five.
    "origin", "cipher", "audit", "chain", "intact",
    # QRME `GET /marketplace/localities` and the rooms feed.
    "region", "listings", "participants",
}

#: (label, the one file that decodes bodies, the floor of distinct keys)
SHELLS = (
    ("ios", "native/ios/Sources/ApiClient.swift", 280),
    ("android", f"{ANDROID}/ApiClient.kt", 230),
    ("windows", "native/windows/ApiClient.cs", 245),
)


def _code(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"^\s*(?://|///|\*)[^\n]*$", "", text, flags=re.M)


# --- what each shell reads ---------------------------------------------------

_STRUCT = re.compile(r'\bstruct\s+(\w+)\s*:[^{\n]*\bDecodable\b[^{\n]*\{')
#: A *stored* property. `var x: T { … }` is computed and `let _: Ok = try …`
#: is a discarded binding; neither names a key.
_STORED = re.compile(r'^\s*(?:var|let)\s+(\w+)\s*:\s*[^\n={]+?$', re.M)
_RENAME = re.compile(r'^\s*case\s+(\w+)\s*=\s*"([^"]+)"', re.M)
_KOTLIN = re.compile(r'\.(?:opt|get)'
                     r'(?:String|Int|Boolean|Double|Long|JSONArray|JSONObject)'
                     r'\(\s*"([^"]+)"')
_CSHARP = re.compile(r'JsonPropertyName\("([^"]+)"\)|'
                     r'(?:Try)?GetProperty\("([^"]+)"\)')


def _structs(src: str):
    """(name, body) per Decodable struct, brace-matched. Ending at the first
    `\\n}` swallows whatever follows a nested struct — see the docstring."""
    for m in _STRUCT.finditer(src):
        depth, i = 1, m.end()
        while i < len(src) and depth:
            depth += (src[i] == "{") - (src[i] == "}")
            i += 1
        yield m.group(1), src[m.end():i - 1]


def _swift(path: Path) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}

    def take(name: str, body: str) -> None:
        renames = dict(_RENAME.findall(body))
        nested = {n for _n, b in _structs(body) for n in _STORED.findall(b)}
        for prop in _STORED.findall(body):
            if prop not in nested:
                out.setdefault(renames.get(prop, prop), set()).add(name)

    for name, body in _structs(_code(path)):
        take(name, body)
        for inner, inner_body in _structs(body):
            take(f"{name}.{inner}", inner_body)
    return out


def _keys(shell: str, path: Path) -> dict[str, set[str]]:
    if shell == "ios":
        return _swift(path)
    src = _code(path)
    found = _KOTLIN.findall(src) if shell == "android" else [
        a or b for a, b in _CSHARP.findall(src)]
    return {k: {path.name} for k in found}


# --- what the backend can emit -----------------------------------------------

def _vocabulary() -> set[str]:
    """Every name this backend can put on the wire. Four routes, because the
    backend uses four: a dict literal, a key assigned after the dict is built,
    a model field, and `dict(row)` — which makes every column a key."""
    out: set[str] = set()
    for path in sorted((REPO / PKG).rglob("*.py")):
        if "tests" in path.parts:
            continue
        src = path.read_text(encoding="utf-8")
        out |= set(re.findall(r'''["']([A-Za-z_]\w*)["']\s*:''', src))
        out |= set(re.findall(r'''\[\s*["']([A-Za-z_]\w*)["']\s*\]''', src))
        out |= set(re.findall(r'\b([a-z_]\w*)\s*=', src))
        out |= set(re.findall(r'^\s{4}([a-z_]\w*)\s*:', src, flags=re.M))
        out |= set(re.findall(r'\bAS\s+([a-z_]\w*)', src))
        out |= set(re.findall(r'^\s+(\w+)\s+(?:TEXT|INTEGER|REAL|BLOB|NUMERIC)',
                              src, flags=re.M | re.I))
        for cols in re.findall(r'INSERT\s+INTO\s+\w+\s*\(([^)]*)\)', src,
                               flags=re.I | re.S):
            out |= {c.strip() for c in cols.replace('"', " ").split(",")
                    if re.fullmatch(r'[a-z_]\w*', c.strip())}
        for cols in re.findall(r'SELECT\s+(.*?)\s+FROM', src, flags=re.I | re.S):
            out |= {c.strip() for c in cols.split(",")
                    if re.fullmatch(r'[a-z_]\w*', c.strip())}
    return out


# --- the guard ---------------------------------------------------------------

def test_every_key_a_shell_reads_is_one_the_server_can_send():
    """The 0.58.3 defects. A shell reading `worn` off a body that says
    `overlays` does not crash — it renders an empty list, which is worse."""
    vocabulary = _vocabulary()
    missing = []
    for shell, path, _floor in SHELLS:
        for key, where in sorted(_keys(shell, REPO / path).items()):
            if key in vocabulary or key in PROXIED:
                continue
            missing.append(f"{shell}: {key!r} — read by {', '.join(sorted(where))}, "
                           f"sent by {PKG}/ nowhere")
    assert not missing, "\n    ".join([""] + missing) + (
        "\n  Read the name the route actually sends, or send it.")


# --- the scan has to be able to see, and to fail -----------------------------

def test_the_scan_reads_every_shell():
    """A decoder that moved makes the check above compare an empty set against
    a vocabulary of thousands, which passes in silence."""
    for shell, path, floor in SHELLS:
        assert (REPO / path).exists(), f"{shell}: {path} is gone"
        found = _keys(shell, REPO / path)
        assert len(found) >= floor, (
            f"{shell}: only {len(found)} key(s) read, floor {floor} — "
            f"the decoding style in {Path(path).name} has changed")


def test_the_vocabulary_is_not_empty():
    """A vocabulary that failed to read the package is a check that passes on
    everything."""
    vocabulary = _vocabulary()
    assert len(vocabulary) >= ratchets.floor("key.vocabulary"), len(vocabulary)
    assert {"display_name", "created_at", "status"} <= vocabulary


def test_a_key_reaches_the_wire_four_ways(tmp_path):
    """Reading only dict literals reported some sixty fields that are on the
    wire every day. The backend puts a key on a response four ways, and each
    of them counts."""
    pkg = tmp_path / PKG
    pkg.mkdir()
    (pkg / "m.py").write_text(
        'SCHEMA = """CREATE TABLE t (\\n    seat_id TEXT NOT NULL\\n);"""\n'
        'class Body(BaseModel):\n'
        '    typed_field: str\n'
        'def read():\n'
        '    out = {"literal_key": 1}\n'
        '    out["assigned_key"] = 2\n'
        '    rows = conn.execute("SELECT seat_id FROM t").fetchall()\n'
        '    return out, [dict(r) for r in rows]\n')
    globals()["REPO"], old = tmp_path, REPO
    try:
        vocabulary = _vocabulary()
    finally:
        globals()["REPO"] = old
    assert {"literal_key", "assigned_key", "typed_field",
            "seat_id"} <= vocabulary


def test_a_nested_struct_does_not_end_the_outer_one(tmp_path):
    """`CustodyProvenance` holds three. A regex that stops at the first
    `\\n}` reads the rest of the file as though it were not in a struct."""
    src = ('struct Provenance: Decodable {\n'
           '    struct Sealed: Decodable { let cipher: String? }\n'
           '    let key: String\n'
           '}\n'
           'let x = 1\n')
    path = tmp_path / "ApiClient.swift"
    path.write_text(src)
    assert set(_swift(path)) == {"cipher", "key"}


def test_a_computed_property_is_not_a_key(tmp_path):
    """`var stands: Bool { valid ?? verified ?? false }` is code the shell
    runs, not a name the server sends."""
    path = tmp_path / "ApiClient.swift"
    path.write_text('struct Verdict: Decodable {\n'
                    '    let valid: Bool?\n'
                    '    var stands: Bool { valid ?? false }\n}\n')
    assert set(_swift(path)) == {"valid"}


def test_a_discarded_binding_is_not_a_key(tmp_path):
    """`let _: Ok = try await request(…)` sits inside a function. Counting it
    reported a dozen route names as wire keys."""
    path = tmp_path / "ApiClient.swift"
    path.write_text('struct Ok: Decodable {}\n'
                    'func leave() async throws {\n'
                    '    let _: Ok = try await request("/x", method: "DELETE")\n'
                    '}\n')
    assert set(_swift(path)) == set()


def test_a_renamed_case_is_the_wire_key(tmp_path):
    """`case profileId = "profile_id"` — the property is the shell's spelling
    and the string is the server's. Reporting the former invents a defect."""
    path = tmp_path / "ApiClient.swift"
    path.write_text('struct Status: Decodable {\n'
                    '    var linked: Bool\n    var profileId: String?\n'
                    '    enum CodingKeys: String, CodingKey {\n'
                    '        case linked\n'
                    '        case profileId = "profile_id"\n    }\n}\n')
    assert set(_swift(path)) == {"linked", "profile_id"}


def test_the_check_can_fail(tmp_path):
    """The real one: the overlay route answers with `overlays`, and two
    shells read `worn`."""
    path = tmp_path / "ApiClient.swift"
    path.write_text('struct WornDisclosure: Decodable {\n'
                    '    let worn: [Worn]?\n}\n')
    vocabulary = {"surface", "surface_id", "overlays", "note"}
    assert sorted(set(_swift(path)) - vocabulary) == ["worn"]
