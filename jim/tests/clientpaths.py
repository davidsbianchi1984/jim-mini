"""Where a client's API paths come from, and how to ask the router about them.

Four languages build the same paths four ways — a template literal in
TypeScript, `\\(x)` in Swift, `$x` in Kotlin, `{x}` in an interpolated C#
string — and every one of them is just a string until somebody presses the
button. This module extracts them and hands them to the real router, so the two
halves of the contract are checked against each other rather than each against
itself.

Byte-identical in qrme, jim-mini and pdi: the question does not differ by
product, so neither should the answer. The repo root is located rather than
hardcoded, which is the only thing that would otherwise differ between them.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from starlette.routing import Match


def _repo_root() -> Path:
    """The directory holding pyproject.toml.

    Found by walking up rather than counted in `.parent`s, because this file
    sits at `tests/` in one repo and `{pkg}/tests/` in the others.
    """
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above clientpaths.py")


REPO = _repo_root()

_COMMENTS = re.compile(r"//[^\n]*|/\*.*?\*/", re.S)
# After interpolation a real path holds only URL-safe characters. Prose that
# happens to sit in a string does not, which is the cheap way to tell the two
# apart when one survives comment-stripping.
_URLSAFE = re.compile(r"^[A-Za-z0-9/_.~%:@!$&'()*+,;=-]*$")


VERBS = ("GET", "POST", "PUT", "PATCH", "DELETE")


@dataclass(frozen=True)
class CallForm:
    """One way this surface writes a request, and where the verb lives in it.

    Three arrangements occur across the four clients. TypeScript and Swift name
    the method in a labelled argument (`method: "POST"`); Kotlin passes it
    positionally right after the path; C# encodes it in the helper's own name
    (`Post(...)`, `Put(...)`) or in an `HttpMethod.Post` constant. So the verb is
    either fixed by the form or read out of the arguments, never guessed.
    """

    opener: re.Pattern[str]
    verb: str | None = None
    verb_in_body: re.Pattern[str] | None = None
    #: How far past the end of the call to keep looking for the verb.
    #:
    #: Zero for every helper that names its method inside its own arguments.
    #: Kotlin's direct-connection idiom does not: the URL is built in one call
    #: and the verb set in the `.apply { }` block that follows, so a search
    #: bounded by the call's own parentheses finds nothing and the default
    #: stands. That default was "GET", and PDI submits an intake with it —
    #: reported as a GET against a POST-only route, a phantom mismatch created
    #: by looking in the wrong place and calling the silence an answer.
    verb_after: int = 0
    default: str = "GET"
    #: The bracket pair enclosing the call's arguments. Parentheses for every
    #: function call, braces for a JSX attribute — `src={…}` is a request the
    #: browser makes with no function anywhere in it.
    delims: str = "()"


@dataclass(frozen=True)
class Language:
    """One client surface: where its sources are and how it splices values in."""

    name: str
    root: Path
    suffixes: tuple[str, ...]
    interpolation: re.Pattern[str]
    literal: re.Pattern[str]
    calls: tuple[CallForm, ...] = ()


# Both quote styles are scanned. A path with no interpolation is written in
# double quotes in TypeScript, and skipping those left a third of each console's
# call sites outside the check — 33 of QRME's, on a guard that claimed to cover
# the console.
# A template literal may nest another inside an interpolation —
# `` `/marketplace${tag ? `?tag=${enc(tag)}` : ""}` `` — so the backtick
# alternative cannot be `` [^`]* ``: that stops at the *inner* opening
# backtick and captures `/marketplace${tag ? `, a path no route matches.
# Matching the interpolation by its braces instead lets the nested backticks
# pass through, because they are inside `${ … }` where only braces count.
_TS_TEMPLATE = r"`(/(?:\$\{(?:[^{}]|\{[^{}]*\})*\}|[^`$]|\$(?!\{))*)`"

CONSOLE = Language(
    "console", REPO / "app" / "src", (".ts", ".tsx"),
    re.compile(r"\$\{[^{}]*\}"),
    re.compile(_TS_TEMPLATE + r"|\"(/[^\"\n]*)\""),
    # `req` and its sibling `reqText`, matched as one form. The sibling
    # exists because `req` parses the body as JSON and falls back to `null`
    # on anything it cannot — right for a crashed server answering plain
    # text, wrong for a route whose job is to return a page. Three of them
    # do: the scan page at `/c/{bid}` is HTML and two `qr.svg` routes are
    # SVG.
    #
    # Adding the helper made those three doors **invisible to this audit**,
    # which reported them as newly doorless while the console had just
    # gained working buttons for all three. That is the third time an
    # extractor has produced a false positive here — after the nested
    # template and the `<img src>` — and it is the same lesson each time:
    # the audit reads one shape of call, so a new shape of call reads as no
    # call.
    #
    # The alternation is spelled out rather than written `req\w*`, which
    # would also swallow `api.requestReset(` — harmless today, because that
    # call holds no path literal to find, and exactly the kind of accidental
    # match that turns into a phantom door the first time one does.
    (CallForm(re.compile(r"\breq(?:Text)?\s*(?:<.*?>)?\s*\(", re.S),
              verb_in_body=re.compile(r'method:\s*"([A-Z]+)"')),
     # `req()` serialises JSON, so anything that cannot — a raw-bytes upload
     # — reaches for `fetch` directly. Without this form the audit is blind
     # to exactly those calls: `POST /profiles/{id}/media` had a working
     # door and still counted as doorless, which is the guard failing in the
     # direction that produces busywork rather than the one that hides a
     # dead button, but failing either way.
     CallForm(re.compile(r"\bfetch\s*\("),
              verb_in_body=re.compile(r'method:\s*"([A-Z]+)"')),
     # A page the browser navigates to is still a door, and the WebAuthn
     # ceremony has to be one: it is served from the relying party's own
     # origin because an opaque origin has no `rpId` to match. The audit
     # counted it doorless in every client that opens it.
     CallForm(re.compile(r"\bwindow\.open\s*\("), verb="GET"),
     # The two requests with no function call in them at all. A QR code is an
     # `<img src>` and a scanned page is an `<a href>`; the browser fetches
     # both, and neither passes through `req()` or `fetch()` on the way. The
     # audit could not see either, which is why `/beacons/{id}/qr.svg` and
     # `/b/{id}` sat on the doorless backlog while Placements had been
     # rendering both since it was written — the same false-positive failure
     # the nested-template bug produced, from a different direction.
     #
     # Braces rather than parentheses: a JSX attribute is not a call, and
     # scanning it for `(` finds the wrong span or none.
     CallForm(re.compile(r"\bsrc=\{"), verb="GET", delims="{}"),
     CallForm(re.compile(r"\bhref=\{"), verb="GET", delims="{}"),),
)
# Swift's `\(…)` may hold one level of nested parentheses — `\(f(x))` — which is
# as deep as these clients go.
IOS = Language(
    "ios", REPO / "native" / "ios", (".swift",),
    re.compile(r"\\\((?:[^()]|\([^()]*\))*\)"),
    re.compile(r'"(/[^"\n]*)"'),
    (CallForm(re.compile(r"\brequest\s*(?:<[^>]*>)?\s*\("),
              verb_in_body=re.compile(r'method:\s*"([A-Z]+)"')),),
)
# Kotlin interpolates bare identifiers as well as braced expressions, and the
# clients use both. Its verb is positional, so it is only read when it sits
# immediately after the path — anything else falls back to the default.
ANDROID = Language(
    "android", REPO / "native" / "android", (".kt",),
    re.compile(r"\$\{[^{}]*\}|\$[A-Za-z_][A-Za-z0-9_]*"),
    # Two literal shapes. The shared `request()` helper is handed a bare
    # path — `"/users/$uid/meds"` — but a route answering a JSON **array**
    # cannot use that helper, because it returns a JSONObject. Those open the
    # connection directly and build the whole URL in the literal:
    # `URL("$base/baseline/$uid")`. That form starts with `$`, not `/`, so
    # the original pattern could not see it.
    #
    # `GET /baseline/{user_id}` proves the cost: the Android shell has had a
    # working door for it since the baseline round, and this audit counted it
    # doorless the entire time. A false positive produces busywork rather than
    # a dead button, but it is still the guard being wrong.
    re.compile(r'"\$base(/[^"\n]*)"|"(/[^"\n]*)"'),
    (CallForm(re.compile(r"\brequest\s*\("),
              verb_in_body=re.compile(
                  r'"/[^"\n]*"\s*,\s*"(GET|POST|PUT|PATCH|DELETE)"')),
     # The direct-connection form above. This used to be declared `verb="GET"`
     # with the reasoning "it exists because the response is an array, and
     # every array route in this shell is a GET" — true of the shell it was
     # written in, and carried into the other two products when the rule was
     # shared. PDI opens a direct connection to POST an intake submission, and
     # the ported assumption reported it as a GET against a POST-only route:
     # a phantom mismatch produced by a rule that travelled without its
     # premise.
     #
     #     asked     what does this call shape mean in the shell it was written for
     #     mattered  what does this call shape mean here
     #
     # So the verb is read. `conn.requestMethod = "POST"` sits a line or two
     # below the URL, inside the same call scope. Absent, it stays GET —
     # which is what HttpURLConnection itself defaults to, so the fallback is
     # the platform's answer rather than a guess.
     CallForm(re.compile(r"\bURL\s*\("), verb_after=400,
              verb_in_body=re.compile(
                  r'requestMethod\s*=\s*"(GET|POST|PUT|PATCH|DELETE)"')),),
)
# C# names the verb in the helper. `Send<Post>(Post(...))` is not ambiguous
# here: the model type is followed by `>`, never by `(`.
WINDOWS = Language(
    "windows", REPO / "native" / "windows", (".cs",),
    re.compile(r"\{[^{}]*\}"),
    re.compile(r'"(/[^"\n]*)"'),
    (
        CallForm(re.compile(r"\bPost\s*\("), verb="POST"),
        CallForm(re.compile(r"\bPut\s*\("), verb="PUT"),
        CallForm(re.compile(r"\bPatch\s*\("), verb="PATCH"),
        CallForm(re.compile(r"\bDelete\s*\("), verb="DELETE"),
        CallForm(re.compile(r"\bGet\s*\("), verb="GET"),
        CallForm(re.compile(r"\bnew\s+HttpRequestMessage\s*\("),
                 verb_in_body=re.compile(
                     r"HttpMethod\.(Get|Post|Put|Patch|Delete)")),
    ),
)
NATIVE = (IOS, ANDROID, WINDOWS)


def normalise(raw: str, lang: Language) -> str:
    """The concrete path this literal sends, ready to hand to the router.

    Interpolations are filled in *before* the query is cut, and the order is the
    whole point. An interpolated segment can sit ahead of the `?` —
    `/meds/${uid}/adherence?days=${days}` — and cutting at the first
    interpolation instead leaves `/meds`, a prefix that resolves for the wrong
    reason and takes the real tail with it. That is not hypothetical: it is how
    `/profiles/{id}/feed` and the media upload went unchecked by the very test
    written to check them.

    One interpolation genuinely does belong to the query — the optional-parameter
    idiom, `${adult ? "?adult=true" : ""}`, whose value is a suffix rather than a
    segment. A quoted `?` inside the braces marks it, and everything from there
    on is dropped. The quote may be a backtick: the same idiom is often written
    with a nested template, `${tag ? `?tag=${enc(tag)}` : ""}`, and reading only
    `"` and `'` missed it.

    Interpolations are found by :func:`_spans` rather than by the language's
    regex alone, because that regex cannot span a nested one — see there.
    """
    for start, end in _spans(raw, lang):
        chunk = raw[start:end]
        if '"?' in chunk or "'?" in chunk or "`?" in chunk:
            raw = raw[:start]
            break
    filled = raw
    for start, end in reversed(_spans(filled, lang)):
        filled = filled[:start] + "x" + filled[end:]
    return filled.split("?", 1)[0].rstrip("/") or "/"


def _spans(raw: str, lang: Language) -> list[tuple[int, int]]:
    r"""Every interpolation in `raw`, as (start, end) — nesting included.

    The language patterns match one flat interpolation each, which is right
    until somebody nests one. `${tag ? `?tag=${enc(tag)}` : ""}` has an inner
    `${…}` with no braces of its own, so `\$\{[^{}]*\}` matches *that* and
    leaves the outer opener stranded; the leftover `${tag ` then survives into
    the path, the query cut lands on the literal `?` inside it, and the call
    normalises to `/marketplace${tag ` — a path no route matches.

    The cost was not a missed leak but a **false positive**: `GET /marketplace`
    was reported as having no client door while `api.marketplace()` had been
    calling it all along, and a door-building round was aimed at it. A guard
    that invents work is a quieter failure than one that misses some, and a
    harder one to notice, because the work looks real until you go to do it.

    So `${`-style interpolations are matched by counting braces instead. The
    other syntaxes — Swift's `\(…)`, C#'s `{…}` — keep their patterns, which
    already handle the nesting each of them actually shows.
    """
    if "${" not in lang.interpolation.pattern.replace("\\", ""):
        return [m.span() for m in lang.interpolation.finditer(raw)]
    out, i = [], 0
    while (i := raw.find("${", i)) != -1:
        depth, j = 0, i + 1
        while j < len(raw):
            if raw[j] == "{":
                depth += 1
            elif raw[j] == "}":
                depth -= 1
                if depth == 0:
                    out.append((i, j + 1))
                    break
            j += 1
        else:
            break  # unbalanced: leave the rest alone rather than guess
        i = j + 1
    return out


# ---------------------------------------------------------------------------
# A note on what this file is for, after it produced its first false positive.
#
# Every earlier defect here made the guard too *lenient*: a truncated path, a
# verb read off the wrong call, a route table read flat instead of recursed.
# Those are the failures you expect from a checker, and the ones its own
# guard-on-guard was written to catch.
#
# The nested-template bug was the other kind. `GET /marketplace` had a door —
# `api.marketplace()`, called by Discover since it was written — and the guard
# said it did not, because the literal regex stopped at a backtick nested
# inside an interpolation. Nothing failed. The suite stayed green. The route
# simply sat on the backlog looking like work, and a door-building round was
# aimed at it before anyone noticed the door was already there.
#
# One route out of 218, so the guard was substantially right. But a checker
# that invents work fails more quietly than one that misses some: a miss is
# found by the bug it let through, while an invention is found only by
# somebody going to do the work and finding it done.
# ---------------------------------------------------------------------------


def paths(lang: Language) -> dict[str, tuple[str, str]]:
    """Every path-shaped literal in this surface → (source file, the literal).

    Deliberately a superset of what the client actually requests, and therefore
    not a pass/fail set: `"/app"` appears in the console because `defaultBase()`
    asks whether `window.location.pathname` starts with it, which is a question
    about where the page is served, not a call. Only :func:`calls` knows the
    difference, because only it looks at what encloses the literal.

    Its job here is liveness — a count that would collapse if an extraction
    pattern stopped matching. Comments are stripped first: a path inside one is
    documentation, not code.
    """
    found: dict[str, tuple[str, str]] = {}
    if not lang.root.exists():
        return found
    for f in sorted(lang.root.rglob("*")):
        if f.suffix not in lang.suffixes or not f.is_file():
            continue
        text = _COMMENTS.sub("", f.read_text(encoding="utf-8"))
        for m in lang.literal.finditer(text):
            raw = next(g for g in m.groups() if g is not None)
            path = normalise(raw, lang)
            if not _usable(path):
                continue
            found.setdefault(path, (str(f.relative_to(REPO)), raw))
    return found


def _usable(path: str) -> bool:
    """A lone `/` is never an API path — only a separator being trimmed or
    split on — and anything that is not URL-safe after interpolation is prose.
    """
    return (path != "/" and path.startswith("/") and bool(_URLSAFE.match(path)))


def _call_body(text: str, opener: int, delims: str = "()") -> str:
    """The text between a call's brackets, respecting nesting and strings.

    Scanning forward to some delimiter instead is what made the first version of
    this wrong: it let a *neighbouring* call's `method:` be read as this call's,
    because the neighbour wrote its path in a form the scan skipped over.

    `delims` is the bracket pair, because not every request is a function call:
    a JSX `src={…}` fetches a URL with no callee at all.
    """
    lo, hi = delims
    depth, i, n, quote = 0, opener, len(text), None
    while i < n:
        c = text[i]
        if quote:
            if c == "\\":
                i += 2
                continue
            if c == quote:
                quote = None
        elif c in "\"'`":
            quote = c
        elif c == lo:
            depth += 1
        elif c == hi:
            depth -= 1
            if depth == 0:
                return text[opener + 1:i]
        i += 1
    return ""


def calls(lang: Language) -> dict[tuple[str, str], tuple[str, str]]:
    """Every (method, path) this surface sends → (source file, the literal).

    The method matters as much as the path. A route table match that ignores it
    accepts a client sending POST where only GET is mounted, and the 405 that
    comes back is, from the user's side, the same dead button as a 404.
    """
    found: dict[tuple[str, str], tuple[str, str]] = {}
    if not lang.root.exists() or not lang.calls:
        return found
    for f in sorted(lang.root.rglob("*")):
        if f.suffix not in lang.suffixes or not f.is_file():
            continue
        text = _COMMENTS.sub("", f.read_text(encoding="utf-8"))
        for form in lang.calls:
            for m in form.opener.finditer(text):
                body = _call_body(text, m.end() - 1, form.delims)
                if not body:
                    continue
                lit = lang.literal.search(body)
                if not lit:
                    continue
                raw = next(g for g in lit.groups() if g is not None)
                path = normalise(raw, lang)
                if not _usable(path):
                    continue
                verb = form.verb
                if verb is None and form.verb_in_body is not None:
                    look = body if not form.verb_after else (
                        body + text[m.end():m.end() + form.verb_after])
                    hit = form.verb_in_body.search(look)
                    verb = hit.group(1).upper() if hit else form.default
                found.setdefault((verb or form.default, path),
                                 (str(f.relative_to(REPO)), raw))
    return found


def resolves(app, path: str) -> bool:
    """True when some route accepts this path, by method or not.

    Matching goes through Starlette's own router rather than string comparison,
    because several routes are generic in their first segment; a shape test
    would either miss those or invent shapes the app does not have.
    """
    scope = {"type": "http", "method": "GET", "path": path,
             "root_path": "", "headers": []}
    for route in app.routes:
        match, _ = route.matches(scope)
        if match in (Match.FULL, Match.PARTIAL):
            return True
    return False


def accepts(app, method: str, path: str) -> bool:
    """True only on a FULL match — the path *and* the method both fit."""
    scope = {"type": "http", "method": method, "path": path,
             "root_path": "", "headers": []}
    return any(r.matches(scope)[0] == Match.FULL for r in app.routes)


def methods_for(app, path: str) -> list[str]:
    """Every verb some route would accept at this path."""
    return [v for v in VERBS if accepts(app, v, path)]


def refused(app, lang: Language) -> list[str]:
    """Lines for every (method, path) this surface sends that no route accepts.

    The message distinguishes the two failures, because the fixes differ: a path
    nothing is mounted at is a typo or a route that was never added, while a path
    that exists under other verbs is a client using the wrong one — a 405 rather
    than a 404, and the same dead button either way.
    """
    out = []
    for (method, path), (source, literal) in sorted(calls(lang).items()):
        if accepts(app, method, path):
            continue
        # Addressed to a different deployment — see ANOTHER_SERVICE below.
        # Checked here rather than by dropping the literal at extraction time,
        # so the call stays visible to everything else that reads `calls()`.
        if path in ANOTHER_SERVICE:
            continue
        ok = methods_for(app, path)
        why = (f"accepted here: {', '.join(ok)}" if ok
               else "no route is mounted at this path")
        out.append(f"{method} {path}  ({source}, from {literal!r}) — {why}")
    return out


# Paths nothing in this product ever asks for: a page somebody is *sent* to
# from outside — a link in an email, a provider's redirect back. No client
# builds these, and none should.
#
# This list used to be longer, and the extra entries were a different thing
# wearing the same coat. `/pair/qr.svg`, `/desks/{id}/view.webp` and
# `/desk-beacons/{id}/qr.svg` were all exempted as "rendered in an `<img
# src>`, not fetched by the API client" — but an `<img src>` *is* a fetch,
# and a door. They were on this list because the extractor could not see
# them, which made an exemption out of a blind spot: the guard stopped
# asking, and one of the three turned out to have no door at all. A desk's
# view frame was never rendered anywhere in the console, and the honesty
# note attached to it — *not live, and not claimed to be* — was therefore
# being shown to nobody.
#
# So the rule this list now holds to: exempt a path because nothing should
# ever call it, never because the audit cannot see the call.
NOT_A_CLIENT_CALL = (
    "/terms",
    "/verify-email/click",
    "/medical-id/{token}/qr.svg",
    # Where Google and Apple send the browser back. The console starts the
    # flow at `/auth/oauth/{provider}/start` and claims the session at
    # `/auth/oauth/claim`; the address in between is built by the **API**
    # (`request.url_for`) and handed to the provider, so no client of this
    # product ever constructs it — and none should, because a redirect_uri a
    # client could choose is a redirect_uri an attacker could choose.
    #
    # Two of them because Apple requires `response_mode=form_post` whenever
    # a scope is requested, so its half of the door arrives as a POST with
    # the code in a urlencoded body.
    "/auth/oauth/{provider}/callback",
)


# Paths that belong to **another service**, so this product's router is the
# wrong table to check them against.
#
# Not the same thing as NOT_A_CLIENT_CALL above, and kept apart on purpose.
# That list is for paths nothing should ever call; these are called, on every
# launch, deliberately — just not here. The Cloud Model Gateway (`cloudgw/`)
# is a separate deployment with its own address, and the shells reach it with
# the collector URL a release stamps in, never with this product's base URL.
#
# The rule for this list: a path goes here only when a *different* service
# owns it and something in this repo can be pointed at that service. If the
# path could ever be served by this app, it does not belong here — it belongs
# in the router.
ANOTHER_SERVICE = (
    "/v1/problems",
)


def all_routes(app) -> list:
    """Every route with a path and methods, including those inside routers.

    `app.routes` is not the flat list it looks like. FastAPI wraps each
    `include_router` in an `_IncludedRouter`, which carries no `path` or
    `methods` of its own and delegates matching to the router it wrapped. Walking
    the top level alone therefore sees only the handful of routes declared
    directly on the app — 8 of QRME's, against more than two hundred real ones —
    and any audit built on that count is not wrong so much as vacuous.

    Route *matching* is unaffected, which is why the guards that call
    `route.matches()` were never misled: the wrapper implements `matches` and
    delegates. Only enumeration needs this.
    """
    out, seen = [], set()

    def walk(routes):
        for route in routes:
            inner = getattr(route, "original_router", None)
            if inner is not None:
                walk(inner.routes)
                continue
            nested = getattr(route, "routes", None)
            if nested and not getattr(route, "methods", None):
                walk(nested)
                continue
            path = getattr(route, "path", None)
            methods = getattr(route, "methods", None)
            if path and methods and (path, tuple(sorted(methods))) not in seen:
                seen.add((path, tuple(sorted(methods))))
                out.append(route)

    walk(app.routes)
    return out


def doorless(app, surfaces=None) -> list[str]:
    """Every route+method the backend serves that no client ever calls.

    The inverse of :func:`refused`. That one asks whether every call reaches a
    route; this asks whether every route is reachable from a door a user can
    open. A feature with no door reads, in the field, as a feature that does not
    exist — and it is the quieter failure of the two, because nothing errors and
    no test goes red. The code is present, the tests pass, and the capability is
    simply unreachable.

    Documentation endpoints and the browser-facing paths in
    :data:`NOT_A_CLIENT_CALL` are excluded; everything else is reported.

    Know what "door" means here, because the word is doing less work than it
    looks like. This counts *call sites*, so a binding added to `api.ts` and
    wired to no screen counts as a door and takes its route off the list — the
    capability is still unreachable, and the number says otherwise. A round
    that adds thirty bindings and five screens will report thirty doors and
    have built five.

    That paragraph used to end "a discipline rather than something the test
    can enforce", and it was wrong. `test_a_binding_is_not_a_door.py` enforces
    it in about twenty lines, and found twenty-five bindings that nothing
    called. *The test cannot check this* is a claim worth testing.

    ``surfaces`` is the other half of the same caution. It defaults to the
    union of all four clients, which answers *some client can reach this* — a
    weaker question than *this client can*, and the difference is a route only
    the phone calls. Pass a single language to ask the narrower one:
    `test_the_console_is_a_client_too.py` does, and the union read zero while
    the console alone could not reach sixty-four routes.
    """
    langs = surfaces if surfaces is not None else (CONSOLE, *NATIVE)
    made: set[tuple[str, str]] = set()
    for lang in langs:
        made |= set(calls(lang))

    out: list[str] = []
    for route in all_routes(app):
        path = route.path
        methods = route.methods
        if path.startswith(("/openapi", "/docs", "/redoc", "/app")):
            continue
        if path in NOT_A_CLIENT_CALL:
            continue
        for method in sorted(methods - {"HEAD", "OPTIONS"}):
            reached = False
            for m, p in made:
                if m != method:
                    continue
                scope = {"type": "http", "method": m, "path": p,
                         "root_path": "", "headers": []}
                if route.matches(scope)[0] == Match.FULL:
                    reached = True
                    break
            if not reached:
                out.append(f"{method} {path}")
    return sorted(out)
