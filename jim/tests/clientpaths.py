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
    default: str = "GET"


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
CONSOLE = Language(
    "console", REPO / "app" / "src", (".ts", ".tsx"),
    re.compile(r"\$\{[^{}]*\}"),
    re.compile(r"`(/[^`]*)`|\"(/[^\"\n]*)\""),
    (CallForm(re.compile(r"\breq\s*(?:<.*?>)?\s*\(", re.S),
              verb_in_body=re.compile(r'method:\s*"([A-Z]+)"')),),
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
    re.compile(r'"(/[^"\n]*)"'),
    (CallForm(re.compile(r"\brequest\s*\("),
              verb_in_body=re.compile(
                  r'"/[^"\n]*"\s*,\s*"(GET|POST|PUT|PATCH|DELETE)"')),),
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
    on is dropped.
    """
    for m in lang.interpolation.finditer(raw):
        if '"?' in m.group(0) or "'?" in m.group(0):
            raw = raw[: m.start()]
            break
    filled = lang.interpolation.sub("x", raw)
    return filled.split("?", 1)[0].rstrip("/") or "/"


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


def _call_body(text: str, open_paren: int) -> str:
    """The text between a call's parentheses, respecting nesting and strings.

    Scanning forward to some delimiter instead is what made the first version of
    this wrong: it let a *neighbouring* call's `method:` be read as this call's,
    because the neighbour wrote its path in a form the scan skipped over.
    """
    depth, i, n, quote = 0, open_paren, len(text), None
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
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[open_paren + 1:i]
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
                body = _call_body(text, m.end() - 1)
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
                    hit = form.verb_in_body.search(body)
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
        ok = methods_for(app, path)
        why = (f"accepted here: {', '.join(ok)}" if ok
               else "no route is mounted at this path")
        out.append(f"{method} {path}  ({source}, from {literal!r}) — {why}")
    return out
