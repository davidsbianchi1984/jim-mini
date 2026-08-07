"""The same question as 0.57.2, asked of the three clients it could not read.

0.57.2 checked what the *console* sends against the model FastAPI validates
with, and closed by noting that the finding which motivated it — a field all
four clients sent and no model declared — had been visible only because I read
the four clients by hand. The guard read one.

    asked     does the console send a body the route can accept
    mattered  does any client send a body the route can accept

So this file reads the other three. The comparison is identical and imported
from the console guard; only the extraction differs, and it has to, because
these clients do not resemble each other:

    C#      Post($"/organizations", new { name }, token)
    Swift   request("/rooms", method: "POST", body: ["topic": t])
    Kotlin  request("/profiles/$id/compose", "POST", JSONObject().put("topic", t))

Three languages, three shapes, one question. 0.56.5 established that a
borrowed pattern must be re-written per client rather than re-pointed, and
every release since has re-proved it; this file assumes it from the start.

## The anonymous-object trap

C# infers a property name when it is not given:

    new { name }                        // a property called `name`
    new { learner_id = learnerId }      // a property called `learner_id`

Reading only the `x = y` form found the second and missed the first, which
meant eleven routes were accused of never sending fields they send on every
call. That is the fifth time in this arc that the extractor, not the client,
produced the findings — and the first four were caught the same way this one
was: by looking at a result that was too dramatic to be true, and checking it
against the file.

## Why the reach floors are the important assertions

A body this guard cannot read is a body it does not judge, so an extractor
that quietly stops matching reports a clean client rather than failing. The
floors below are what each client honestly yields today. They are not
decoration: 0.57.2's two real findings existed only on the far side of a
reach fix, and were invisible while the guard was green.
"""

import pathlib
import re

from .test_the_body_the_route_requires import _models

RECORD = (pathlib.Path(__file__).resolve().parent
          / "native_bodies_unverified.txt")
REPO = pathlib.Path(__file__).resolve().parents[2]

CLIENTS = {
    "the Windows client": REPO / "native/windows/ApiClient.cs",
    "the iOS client": REPO / "native/ios/Sources/ApiClient.swift",
    "the Android client":
        REPO / "native/android/app/src/main/java/app/jim/guardian/ApiClient.kt",
}

WRITES = ("POST", "PUT", "PATCH")


def _shape(path: str) -> str:
    r"""A path in the one spelling all four sides can be compared in.

    Each language interpolates differently — C# `{id}`, Swift `\(id)`,
    Kotlin `$id` and `${id}` — and the console guard's normaliser knows only
    the first two of those. Importing it read the iOS client's paths
    literally, so 39 of its writes matched a route instead of 162, and the
    guard was quieter for it rather than louder.
    """
    path = re.sub(r'\\\([^)]*\)', '{}', path)          # Swift
    path = re.sub(r'\$\{[^}]*\}|\$\w+', '{}', path)     # Kotlin
    path = re.sub(r'\{[^}]*\}', '{}', path)              # C#, and the rest
    return path.split("?")[0]


def _matched(text: str, i: int, opener: str, closer: str) -> int:
    """Index just past the bracket matching `text[i]`, or -1."""
    depth = 0
    while i < len(text):
        c = text[i]
        if c == '"':
            i += 1
            while i < len(text) and text[i] != '"':
                i += 2 if text[i] == "\\" else 1
        elif c == opener:
            depth += 1
        elif c == closer:
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return -1


def _args(text: str, open_paren: int) -> str:
    """The text inside this call's own parentheses.

    Every one of these extractors reads the body out of *this* call, not out
    of the next four hundred characters. A window instead of a bound is how
    `POST /profiles` was credited with a dictionary belonging to the function
    below it.
    """
    end = _matched(text, open_paren, "(", ")")
    return text[open_paren + 1:end - 1] if end > 0 else ""


def _outermost(text: str, openers: str = "([{", closers: str = ")]}") -> str:
    """The text with every nested bracket body emptied.

    A body is what the *top level* of the literal declares. Swift writes

        body: ["items": [["content": content]]]

    which sends one key, `items`; a flat scan of that text finds `content`
    too and reports the route for a field that is a key inside an element of
    the array it does send. Three of the first run's findings were that, and
    `/rooms` supplied two more from inside `participants`.

    Sixth time in this arc — the console guard has `_top_level` for exactly
    this and I did not carry the idea across, only the file.
    """
    out, depth = [], 0
    for ch in text:
        if ch in openers:
            depth += 1
            if depth == 1:
                out.append(ch)
        elif ch in closers:
            depth -= 1
            if depth == 0:
                out.append(ch)
        elif depth == 0:
            out.append(ch)
    return "".join(out)


def _csharp_keys(inner: str) -> list[str]:
    """The properties of a C# anonymous object, inferred names included."""
    parts, depth, buf = [], 0, []
    for ch in inner:
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    parts.append("".join(buf))
    out = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if "=" in part and not part.split("=")[0].strip().endswith(("!", "<", ">")):
            name = part.split("=")[0].strip()
        else:
            name = part.split(".")[-1].strip()   # `row.Title` declares `Title`
        if re.fullmatch(r'\w+', name):
            out.append(name)
    return out


def _csharp(src: str):
    """Both shapes this codebase's C# clients use.

    QRME wraps writes in a helper — `Put($"/path", new { k }, token)`. PDI
    builds the message by hand:

        new HttpRequestMessage(HttpMethod.Put, "/records")
        {
            Content = JsonContent.Create(new { key, value }),
        }

    Reading only the helper found 170 writes in QRME and **zero** in PDI, and
    zero found is indistinguishable from zero wrong. 0.56.5 established that a
    borrowed pattern must be re-written per client; this is the same fact one
    level up — per *product*, in the same language.
    """
    for m in re.finditer(r'new HttpRequestMessage\(\s*HttpMethod\.'
                         r'(Post|Put|Patch)\s*,\s*\$?"([^"]+)"', src):
        verb, path = m.group(1).upper(), m.group(2)
        tail = src[m.end():m.end() + 600]
        body = re.search(r'JsonContent\.Create\(\s*new\s*\{', tail)
        if not body:
            yield verb, path, None
            continue
        opened = tail.index("{", body.start() + len("JsonContent.Create("))
        end = _matched(tail, opened, "{", "}")
        yield verb, path, _csharp_keys(tail[opened + 1:end - 1])
    for m in re.finditer(r'\b(Post|Put|Patch)\(', src):
        args = _args(src, m.end() - 1)
        path = re.match(r'\s*\$?"([^"]+)"', args)
        if not path:
            continue
        body = re.search(r'\bnew\s*\{', args)
        if not body:
            yield m.group(1).upper(), path.group(1), None
            continue
        opened = args.index("{", body.start())
        end = _matched(args, opened, "{", "}")
        yield (m.group(1).upper(), path.group(1),
               _csharp_keys(args[opened + 1:end - 1]))


def _swift(src: str):
    for m in re.finditer(r'\brequest\(', src):
        args = _args(src, m.end() - 1)
        path = re.match(r'\s*"([^"]+)"', args)
        verb = re.search(r'method:\s*"(POST|PUT|PATCH)"', args)
        if not path or not verb:
            continue
        body = re.search(r'body:\s*\[', args)
        if not body:
            yield verb.group(1), path.group(1), None
            continue
        end = _matched(args, body.end() - 1, "[", "]")
        yield (verb.group(1), path.group(1),
               re.findall(r'"([\w_]+)"\s*:',
                          _outermost(args[body.end():end - 1], "[({", "])}")))


def _kotlin_keys(chain: str) -> list[str]:
    """The keys `.put` on the outer object, not on one nested inside it.

    `JSONObject().put("a", JSONObject().put("b", x))` sets one key. Emptying
    the nested brackets the way the Swift reader does is wrong here, because
    the key *is* inside the `.put(` parentheses — stripping depth-1 content
    removed every key in the file and turned the Android client into a
    hundred and forty "never sends required". Depth has to be measured at the
    `.put`, not applied to the text.
    """
    out, depth, i = [], 0, 0
    while i < len(chain):
        c = chain[i]
        if c == '"':
            i += 1
            while i < len(chain) and chain[i] != '"':
                i += 2 if chain[i] == "\\" else 1
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif chain.startswith(".put(", i) and depth == 0:
            key = re.match(r'\.put\(\s*"([\w_]+)"', chain[i:])
            if key:
                out.append(key.group(1))
        i += 1
    return out


def _kotlin(src: str):
    for m in re.finditer(r'\brequest\(', src):
        args = _args(src, m.end() - 1)
        path = re.match(r'\s*"([^"]+)"', args)
        verb = re.search(r'"(POST|PUT|PATCH)"', args)
        if not path or not verb:
            continue
        body = re.search(r'JSONObject\(\)', args)
        if not body:
            yield verb.group(1), path.group(1), None
            continue
        yield (verb.group(1), path.group(1),
               _kotlin_keys(args[body.end():]))


READERS = {
    "the Windows client": _csharp,
    "the iOS client": _swift,
    "the Android client": _kotlin,
}


def _sent(client: str):
    src = CLIENTS[client].read_text(encoding="utf-8")
    return [row for row in READERS[client](src) if row[0] in WRITES]


def _findings() -> list[str]:
    models = _models()
    out = []
    for client in CLIENTS:
        for verb, template, keys in _sent(client):
            if keys is None:
                continue
            schema = models.get((verb, _shape(template)))
            if schema is None:
                continue
            required = set(schema.get("required", []))
            properties = set(schema.get("properties", {}))
            shown = _shape(template)
            for field in sorted(required - set(keys)):
                out.append(f"{client}: {verb} {shown} never sends "
                           f"required {field!r}")
            for field in sorted(set(keys) - properties):
                if properties:
                    out.append(f"{client}: {verb} {shown} sends {field!r}, "
                               f"which the model has no property for")
    return out


def _recorded() -> set[str]:
    rows = (line.split("#")[0].strip()
            for line in RECORD.read_text(encoding="utf-8").splitlines())
    return {row for row in rows if row}


# --- the guard ---------------------------------------------------------------

def test_no_native_write_sends_a_body_the_route_cannot_accept():
    """A required field a phone never sends is a 422 the user reads as a
    button that does nothing. A field the model has no property for is a value
    they typed and the server discarded."""
    loose = [row for row in _findings() if row not in _recorded()]
    assert not loose, (
        "these native writes and their routes disagree:\n    "
        + "\n    ".join(sorted(set(loose)))
        + "\n  Send the field the model declares, or correct the model — "
          "recording is ratcheted.")


def test_the_unverified_record_only_shrinks():
    text = RECORD.read_text(encoding="utf-8")
    ceiling = int(re.search(r"^# ceiling: (\d+)$", text, re.M).group(1))
    assert len(_recorded()) <= ceiling, (
        f"{len(_recorded())} rows recorded, above the {ceiling} ceiling")


# --- the scan has to be able to see, and to fail -----------------------------

def test_every_client_is_read_at_a_share_of_its_writes():
    """Per client, because the failure this catches is per client: a pattern
    that stops matching one file leaves the other two green and says nothing.

    0.57.2 shipped with JIM-mini's console read at 28 writes of 113 and every
    check passing. The floors are the only thing that would have caught it.
    """
    floors = {"the Windows client": (50, 48),
              "the iOS client": (50, 34),
              "the Android client": (50, 34)}
    for client, (writes, readable) in floors.items():
        rows = _sent(client)
        read = [r for r in rows if r[2] is not None]
        assert len(rows) >= writes, (client, len(rows))
        assert len(read) >= readable, (client, len(read))


def test_a_real_share_of_native_writes_meets_a_model():
    models = _models()
    for client in CLIENTS:
        matched = sum(1 for verb, template, _ in _sent(client)
                      if (verb, _shape(template)) in models)
        assert matched >= 44, (client, matched)


def test_the_csharp_reader_sees_an_inferred_property_name():
    """`new { name }` declares a property called `name`. Reading only the
    `x = y` form missed every inferred one and produced eleven findings
    against routes that send those fields on every call — the fifth time in
    this arc that the extractor wrote the defects it reported."""
    assert _csharp_keys(" name ") == ["name"]
    assert _csharp_keys(" learner_id = learnerId, lesson ") == [
        "learner_id", "lesson"]
    assert _csharp_keys(" row.Title ") == ["Title"]


def test_each_reader_reads_its_own_language_and_not_the_others():
    """A borrowed pattern finds nothing here, and nothing found reads exactly
    like nothing wrong — 0.56.5, restated per language."""
    cs = 'Send<X>(Post($"/a/{b}", new { k = v }, token));'
    sw = 'try await request("/a", method: "POST", body: ["k": v])'
    kt = 'request("/a", "POST", JSONObject().put("k", v), token)'
    assert list(_csharp(cs)) == [("POST", "/a/{b}", ["k"])]
    assert list(_swift(sw)) == [("POST", "/a", ["k"])]
    assert list(_kotlin(kt)) == [("POST", "/a", ["k"])]
    assert list(_swift(cs)) == [] and list(_kotlin(cs)) == []
    assert list(_csharp(sw)) == [] and list(_csharp(kt)) == []


def test_only_the_top_level_of_a_body_is_read():
    """A key inside a nested value is not a field of the body. Swift's
    `["items": [["content": c]]]` sends `items`; reading `content` too
    reported three routes for fields they never send at that level."""
    assert list(_swift('request("/a", method: "POST", '
                       'body: ["items": [["content": c]]])')) == [
        ("POST", "/a", ["items"])]
    assert list(_kotlin('request("/a", "POST", JSONObject()'
                        '.put("outer", JSONObject().put("inner", x)))')) == [
        ("POST", "/a", ["outer"])]


def test_a_body_is_read_from_its_own_call_and_not_the_next_one():
    """A four-hundred-character window instead of a bound is how a call with
    no body at all was credited with the dictionary of the function below."""
    two = ('try await request("/first", method: "POST")\n'
           'try await request("/second", method: "POST", body: ["k": v])\n')
    assert list(_swift(two)) == [("POST", "/first", None),
                                 ("POST", "/second", ["k"])]
