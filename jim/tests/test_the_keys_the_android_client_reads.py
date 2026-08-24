"""Kotlin declares nothing, and reads everything by name.

The Windows client says what it expects in records, and Swift in structs, so
0.56.4 through 0.56.8 could ask both of them the same question: is every
declared field a key the route sends, in a shape the declared type can decode.
Nineteen defects in C#, nine in Swift, every Swift one already fixed in C# and
never carried across.

The 0.56.8 changelog left Kotlin out with a hedge:

> *it parses `JSONObject` by hand rather than declaring shapes, so there is
> nothing to compare — which is either a reason it cannot have this defect, or
> the reason nobody would find it.*

It was the second one. This client declares nothing, but every line of it is
two claims at once:

    val o = JSONObject(request("/profiles/$id/wearables", token = token))
    val worn = o.optJSONObject("kinds_worn")

`"kinds_worn"` says the route sends that key. `optJSONObject` says it is an
object. Both can be wrong, and the way they go wrong here is worse than
elsewhere, because `org.json` does not throw:

* `optString` on a key the route never sends returns `""`;
* `optInt` on a string returns `0`;
* `optJSONArray` on an object returns `null`, and the `?:` beside it quietly
  substitutes an empty one.

A C# client with the wrong type throws and somebody sees a crash. This one
draws a screen with nothing on it, and that is the harder defect to notice —
so *no declarations* was never a reason it could not have this defect. It was
a reason it would never be found.

    asked     does the client declare the right shape
    mattered  does the client ask for the right thing

## What is checked

Every GET whose response this client reads, in the four shapes these three
clients read one in:

* bound and read by name — `val o = ...request(...)`, then `o.optString("k")`;
* handed to a parse helper — `crashWatchOf(request(...))`, whose reads off its
  `JSONObject` parameter are this route's claims one indirection away;
* read inline — `request(...).getString("provider")`;
* chained — `...request(...).getJSONArray("providers")`, where the chained key
  is the claim and what hangs off it is not.

The `JSONObject(` constructor around the call is **optional**, and that single
character of laxity is most of this guard's reach. QRME's `request` returns a
`String` and every read wraps it; JIM-mini's returns a `JSONObject` and none
of them do. Requiring the wrapper read one client whole and the other at
twelve routes out of forty-two — which looked exactly like a client with
twelve routes.

Keys read off a *nested* object are not claims about the response:
`worn.optString(k)` is about `kinds_worn`'s contents, and crediting it to the
top level accused three routes of fields they never read there.

Scalar accessors are held to the coercion `org.json` actually performs:
`optString` on a number or a boolean is a deliberate stringification and is
allowed. `optString` on an *object* or an *array* is not, and neither is
`optInt` on a string — those are the reads that return a plausible wrong
answer instead of failing.
"""

import json
import pathlib
import re

from .test_the_shape_the_client_expects import (
    _returned_keys, _shape_of, _standing)
from . import ratchets

REPO = pathlib.Path(__file__).resolve().parents[2]
ANDROID_CLIENT = (
    REPO / "native/android/app/src/main/java/app/jim/guardian/ApiClient.kt")
RECORD = pathlib.Path(__file__).resolve().parent / "android_keys_unverified.txt"

_SRC = ANDROID_CLIENT.read_text(encoding="utf-8")

# One entry per function, so a key read in one cannot be attributed to the
# route another one calls. Splitting on `suspend fun` alone was not enough:
# a plain `fun` helper sitting between two of them stayed in the preceding
# chunk, and because `o` is the conventional name for the decoded body here,
# its reads were credited to whatever route that chunk began with. The
# voiceprint route was accused of reading thirteen shop fields.
_FUNCTION = re.compile(r'\n    (?=(?:private )?(?:suspend )?fun )')
# The binding must be the *whole* response. Admits every shape these three
# clients use: a bare or fully-qualified `JSONObject`, the `request(` on the
# same line or the next, and the verb passed either positionally or by
# keyword.
#
# **The constructor is optional, and that is the whole reach of this guard.**
# QRME's `request` returns a `String`, so its every read is wrapped —
# `JSONObject(request(...))` — and a pattern that requires the wrapper reads
# this client completely. Hand the same pattern to JIM-mini, whose `request`
# returns a `JSONObject` already, and the ordinary line
#
#     val o = request("/money/$uid", token = token)
#
# matches nothing. Forty-two GETs in that client, twelve of them found, and
# twelve found reads exactly like twelve is all there are. The C# guard
# learned this in 0.56.5 and the lesson did not survive the language change:
# a borrowed pattern that finds *some* of a file is worse than one that finds
# none, because none is obviously broken.
_BOUND = re.compile(
    r'val (\w+) = (?:(?:org\.json\.)?JSONObject\(\s*\n?\s*)?'
    r'request\(\s*"([^"]+)"([^\n]*)')
_INLINE = re.compile(
    r'(?:(?:org\.json\.)?JSONObject\(\s*\n?\s*)?request\(\s*"([^"]+)"([^\n]*?)'
    r'\)\s*\)?\s*\n?\s*\.(opt\w+|get\w+)\(\s*"([\w_]+)"')

# What org.json will hand back without complaining.
ACCEPTS = {
    "optString": {"string", "number", "bool"},
    "getString": {"string"},
    "optInt": {"number"}, "getInt": {"number"},
    "optLong": {"number"}, "optDouble": {"number"}, "getDouble": {"number"},
    "optBoolean": {"bool"}, "getBoolean": {"bool"},
    "optJSONArray": {"list"}, "getJSONArray": {"list"},
    "optJSONObject": {"object"}, "getJSONObject": {"object"},
}


def _is_get(rest: str) -> bool:
    """Whether the call is a GET.

    This client passes the verb *positionally* — `request(path, "DELETE",
    null, token)` — so a check for the word `method` sees a GET. That is how
    the revoke-voiceprint and pair-wearable replies were read as though they
    were what `GET` of those paths returns.
    """
    return not any(v in rest for v in ('"POST"', '"PUT"', '"DELETE"',
                                       '"PATCH"'))


# `private fun crashWatchOf(o: JSONObject) = ...` — a parse helper. JIM-mini's
# client routes nearly every route through one of nineteen of these, so its
# reads sit one call away from the request that fetched them. A pattern that
# only looks inside the calling function finds two routes there out of fifty.
_HELPER = re.compile(
    r'(?:private )?fun (\w+)\((\w+): (?:org\.json\.)?JSONObject')


def _chain(text: str) -> tuple[str, str] | None:
    """The accessor chained directly onto the request call, if there is one.

    A binding that chains binds *that* value, not the response:
    `val f = JSONObject(request(...)).getJSONObject("funnel")` holds the
    funnel, and crediting `f`'s reads to the top level accused the placements
    route of three fields it never reads there. But the chained key is itself
    a claim — `funnel` has to be on the wire, as an object, for the line to
    mean anything — so it is read rather than discarded.

    **Anchored, not searched.** The first version scanned a 240-character
    window for `).accessor("key")` and found, in two different functions, a
    chain belonging to something else entirely:

        val o = JSONObject(request("/displays/vocabulary"))
        o.optJSONArray("never")?.let { a ->
            out.add(a.getJSONObject(i).optString("why"))   // <- matched this

    `why` is a key on the objects *inside* `never`, and `light` in the watch
    face is a key inside `profile`. Both were reported as missing from the
    response, and both were the guard reading a line it had no business
    reading. So: walk the call's own parentheses to their close, and take the
    chain only if it attaches there.
    """
    i = text.index("request(") + len("request(")
    depth = 1
    while i < len(text) and depth:
        c = text[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
        elif c == '"':
            i += 1
            while i < len(text) and text[i] != '"':
                i += 2 if text[i] == "\\" else 1
        i += 1
    # An optional `)` for the `JSONObject(` wrapper, where this client uses one.
    m = re.match(r'\)?\s*\n?\s*\.(opt\w+|get\w+)\(\s*"([\w_]+)"', text[i:])
    return m.groups() if m else None


def _helpers() -> dict[str, list[tuple[str, str]]]:
    """Parse helper -> the keys it reads off its JSONObject parameter."""
    out = {}
    for body in _FUNCTION.split(_SRC):
        m = _HELPER.search(body)
        if not m:
            continue
        name, param = m.groups()
        out[name] = re.findall(
            r'\b%s\.(opt\w+|get\w+)\(\s*"([\w_]+)"' % re.escape(param), body)
    return out


def _reads() -> list[tuple[str, list[tuple[str, str]]]]:
    """[(path template, [(accessor, key)])] for every GET this client reads."""
    out = []
    helpers = _helpers()
    for body in _FUNCTION.split(_SRC):
        # A route handed straight to a parse helper: the helper's reads are
        # this route's claims, one indirection away.
        # The constructor is optional: QRME's `request` returns a String and
        # is wrapped, JIM-mini's returns a JSONObject and is handed straight
        # to the helper.
        handed = re.search(
            r'(\w+)\(\s*\n?\s*(?:(?:org\.json\.)?JSONObject\(\s*\n?\s*)?'
            r'request\(\s*"([^"]+)"([^\n]*)', body)
        if handed and handed.group(1) in helpers and _is_get(handed.group(3)):
            keys = helpers[handed.group(1)]
            if keys:
                out.append((handed.group(2), keys))
                continue
        bound = _BOUND.search(body)
        if not bound:
            continue
        var, path, rest = bound.groups()
        if not _is_get(rest):
            continue
        chained = _chain(body[bound.start():])
        if chained:
            # The var holds the nested value, so its own reads say nothing
            # about the response. The key that reached it does.
            out.append((path, [chained]))
            continue
        keys = re.findall(
            r'\b%s\.(opt\w+|get\w+)\(\s*"([\w_]+)"' % re.escape(var), body)
        if keys:
            out.append((path, keys))
    for path, rest, accessor, key in _INLINE.findall(_SRC):
        # `request("/feedback", "POST", body, token)` is not a GET, and the
        # key it reads off the *reply* to a write says nothing about what the
        # GET of that path returns.
        if not _is_get(rest):
            continue
        out.append((path, [(accessor, key)]))
    return out


def _recorded() -> set[str]:
    rows = (line.split("#")[0].strip()
            for line in RECORD.read_text(encoding="utf-8").splitlines())
    return {row for row in rows if row}


def _drive(client, uid: str, other_id: str):
    """Every readable GET, driven. Yields (path, findings|None)."""
    subs = {"id": uid, "uid": uid, "userId": uid, "otherId": other_id}
    for template, keys in _reads():
        path = template
        for name, value in subs.items():
            path = path.replace("$" + name, value).replace(
                "${" + name + "}", value)
        # A query string this client builds by concatenation — `request(
        # "/circle/$uid/messages?with_id=" + encode(withId), ...)` — reaches
        # the extractor as the literal prefix only, because the value is on
        # the next line and is not a literal at all. Driving that prefix asks
        # for `?with_id=` with nothing after it, and JIM's route answers a
        # *different* shape for the empty case: the thread list, with no
        # `messages` key in it. The guard reported the client for reading a
        # key the route sends perfectly well.
        #
        # It is the fixture that cannot reach this, not the client that is
        # wrong, so it is unreachable rather than recorded. Recording it would
        # have put this guard's own defect in the ratchet file and called it
        # a backlog.
        if path.rstrip().endswith(("=", "&", "?")):
            yield template, None
            continue
        if "$" in path or "{" in path:
            yield template, None
            continue
        response = client.get(path)
        if response.status_code != 200:
            yield template, None
            continue
        try:
            body = response.json()
        except (ValueError, json.JSONDecodeError):
            yield template, None
            continue
        if not isinstance(body, dict):
            yield template, None
            continue
        found = []
        # Rows name the route, not the id a fixture happened to mint.
        shown = re.sub(r'(prf|usr)_[0-9a-f]+', '{id}', path)
        for accessor, key in keys:
            if key not in body:
                found.append(f"{shown} reads {key!r} — not on the wire")
                continue
            shape = _shape_of(body[key])
            allowed = ACCEPTS.get(accessor)
            if allowed and shape not in allowed and shape != "null":
                found.append(f"{shown} reads {key!r} with {accessor} "
                             f"and it arrives as a {shape}")
        yield template, found


# --- the guard ---------------------------------------------------------------

def test_the_android_client_asks_for_what_the_route_sends(client):
    """`org.json` does not throw. A key this client asks for and does not get
    is an empty string on a screen, which is the defect nobody reports."""
    uid, other = _standing(client)
    loose = []
    for _, found in _drive(client, uid, other):
        for row in found or []:
            key = re.search(r"reads '([\w_]+)'", row).group(1)
            path = row.split(" reads ")[0]
            if f"{path} {key}" not in _recorded():
                loose.append(row)
    assert not loose, (
        "the Android client asks for these and the route disagrees:\n    "
        + "\n    ".join(sorted(set(loose)))
        + "\n  Read the key the route actually sends, with the accessor its "
          "type deserves — or record `<path> <key>` with the state that "
          "produces it. Recording is ratcheted.")


def test_the_unverified_record_only_shrinks():
    text = RECORD.read_text(encoding="utf-8")
    ceiling = int(re.search(r"^# ceiling: (\d+)$", text, re.M).group(1))
    assert len(_recorded()) <= ceiling, (
        f"{len(_recorded())} rows recorded, above the {ceiling} ceiling")


_VAR = re.compile(r'\$\{?(\w+)\}?')


def test_every_recorded_row_names_a_read_this_client_still_makes():
    """A row that describes nothing is a ratchet that has stopped ratcheting.

    The Swift record grew this check in 0.56.8 for the same reason: once a
    line is in the file the ceiling counts it, and a stale row buys headroom
    for a defect nobody has fixed. The paths are compared in the shape the
    findings are written in — the fixture's minted ids masked back to `{id}`.
    """
    asked = {f"{_VAR.sub('{id}', path)} {key}"
             for path, keys in _reads() for _, key in keys}
    stale = sorted(_recorded() - asked)
    assert not stale, (
        "these rows name reads the client no longer makes:\n    "
        + "\n    ".join(stale) + "\n  Strike them.")


# --- the scan has to be able to see, and to fail -----------------------------

def test_the_extractor_reads_this_clients_calls():
    """Neither the C# nor the Swift pattern finds anything in a file that
    declares no shapes, and nothing found reads as nothing wrong."""
    reads = _reads()
    assert len(reads) >= ratchets.floor("android.reads"), len(reads)
    assert sum(len(k) for _, k in reads) >= ratchets.floor("android.read_keychars"), sum(len(k) for _, k in reads)


def test_no_function_body_swallowed_the_next_one():
    """Third time this assertion is written, in the third language — and the
    first time the assertion itself was wrong. It counted `suspend fun` when
    the split needed to be on any `fun`, so a plain helper between two
    suspend functions kept its reads in the preceding chunk and passed this
    check while poisoning the results. Counting the thing you split on is the
    whole point."""
    for body in _FUNCTION.split(_SRC)[1:]:
        # Counting the thing the split matches: a declaration at this file's
        # member indent. A *local* `fun` nested inside one — this client has
        # `fun strings(key)` inside `exchangeVocabulary` — is part of that
        # body and not a boundary the split should have found.
        assert len(re.findall(r'^    (?:private )?(?:suspend )?fun ',
                              body, re.M)) <= 1, body[:160]


def test_the_scan_reaches_a_real_share_of_the_routes(client):
    uid, other = _standing(client)
    driven = [f for _, f in _drive(client, uid, other)
              if f is not None]
    assert len(driven) >= 30, (
        f"only {len(driven)} route(s) were reachable — the fixture or the "
        f"extractor has stopped working")


def test_the_guard_holds_org_json_to_the_coercions_it_actually_performs():
    """`optString` on a number is a deliberate stringification and is allowed.
    `optString` on an object is the read that returns a plausible wrong
    answer, and is not."""
    assert "number" in ACCEPTS["optString"]
    assert "object" not in ACCEPTS["optString"]
    assert "list" not in ACCEPTS["optString"]
    assert ACCEPTS["optInt"] == {"number"}
