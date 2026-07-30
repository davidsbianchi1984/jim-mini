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


@dataclass(frozen=True)
class Language:
    """One client surface: where its sources are and how it splices values in."""

    name: str
    root: Path
    suffixes: tuple[str, ...]
    interpolation: re.Pattern[str]
    literal: re.Pattern[str]


# Only the backtick form is scanned for TypeScript: a path with no interpolation
# at all is written in quotes there, but every such path in the consoles is a
# constant the router would accept trivially, and quoting would drag in every
# unrelated string in the file.
CONSOLE = Language(
    "console", REPO / "app" / "src", (".ts", ".tsx"),
    re.compile(r"\$\{[^{}]*\}"),
    re.compile(r"`(/[^`]*)`"),
)
# Swift's `\(…)` may hold one level of nested parentheses — `\(f(x))` — which is
# as deep as these clients go.
IOS = Language(
    "ios", REPO / "native" / "ios", (".swift",),
    re.compile(r"\\\((?:[^()]|\([^()]*\))*\)"),
    re.compile(r'"(/[^"\n]*)"'),
)
# Kotlin interpolates bare identifiers as well as braced expressions, and the
# clients use both.
ANDROID = Language(
    "android", REPO / "native" / "android", (".kt",),
    re.compile(r"\$\{[^{}]*\}|\$[A-Za-z_][A-Za-z0-9_]*"),
    re.compile(r'"(/[^"\n]*)"'),
)
WINDOWS = Language(
    "windows", REPO / "native" / "windows", (".cs",),
    re.compile(r"\{[^{}]*\}"),
    re.compile(r'"(/[^"\n]*)"'),
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
    """Every path this surface builds, mapped to (source file, the literal).

    Comments are stripped first — a path inside one is documentation, not a
    call. A lone `/` is dropped too: it is never an API path, only a separator
    being trimmed or split on (`hasSuffix("/")`, `substringBefore("/")`,
    base64url's `/` → `_`).
    """
    found: dict[str, tuple[str, str]] = {}
    if not lang.root.exists():
        return found
    for f in sorted(lang.root.rglob("*")):
        if f.suffix not in lang.suffixes or not f.is_file():
            continue
        text = _COMMENTS.sub("", f.read_text(encoding="utf-8"))
        for raw in lang.literal.findall(text):
            path = normalise(raw, lang)
            if path == "/" or not path.startswith("/"):
                continue
            if not _URLSAFE.match(path):
                continue
            found.setdefault(path, (str(f.relative_to(REPO)), raw))
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


def unresolved(app, lang: Language) -> list[str]:
    """Human-readable lines for every path of this surface no route accepts."""
    out = []
    for path, (source, literal) in sorted(paths(lang).items()):
        if not resolves(app, path):
            out.append(f"{path}  ({source}, from {literal!r})")
    return out
