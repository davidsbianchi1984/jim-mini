"""A function in `api.ts` that no screen calls is not a door.

`clientpaths.doorless` counts **call sites**, and `api.ts` is a console source
like any other, so a binding written there takes its route off the backlog
whether or not anything ever calls the binding. The docstring on `doorless`
says so plainly and then gives up:

    The rule that follows is a discipline rather than something the test can
    enforce: add the binding in the same change as the screen that calls it.
    A round that adds thirty bindings and five screens will report thirty
    doors and have built five.

It turns out to be enforceable in about twenty lines, and this is them. The
admission had been sitting there since the route audit was written, which is
its own small lesson: *the test cannot check this* is a claim worth testing.

The check itself is the same question one level down. `doorless` asks whether
the backend's routes are reachable from a client; this asks whether the
client's bindings are reachable from a screen. Twenty-five are not — routes
the audit has been counting as doored that a person cannot get to, because
the only thing that calls them is nothing.

## What it does not claim

Reachability stops here. A binding called by a screen that no tab renders is
still counted, and so is one behind a button that is never enabled. Those are
worth catching too and this is not the file that catches them; what it rules
out is the specific, checkable case of a call that literally does not exist
anywhere.
"""

from __future__ import annotations

import re
from pathlib import Path


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
API = REPO / "app" / "src" / "api.ts"
SNAPSHOT = Path(__file__).resolve().parent / "unused_bindings.txt"

#: Where it stood when this guard was written.
STARTED_AT = 4


def _bindings() -> dict[str, str]:
    """Every `name: (…) =>` in `api.ts`, mapped to the object exporting it.

    There are several — `api`, `accountApi`, `oauthApi` — and the object
    matters, because a caller writes `accountApi.signin(…)`. The first version
    of this ignored that and reported fifteen bindings as unused that were
    being called perfectly well under another name.
    """
    src = API.read_text(encoding="utf-8")
    starts = [(m.group(1), m.start())
              for m in re.finditer(r"^export const (\w+) = \{", src, re.M)]
    bounds = sorted(starts, key=lambda kv: kv[1]) + [("<end>", len(src))]
    owner: dict[str, str] = {}
    for (obj, start), (_, nxt) in zip(bounds, bounds[1:]):
        for name in re.findall(r"^  ([A-Za-z_]\w*):\s*\(", src[start:nxt],
                               re.M):
            owner[name] = obj
    return owner


def _console_sources() -> dict[Path, str]:
    return {f: f.read_text(encoding="utf-8")
            for f in sorted((REPO / "app" / "src").rglob("*"))
            if f.suffix in (".ts", ".tsx") and f.name != "api.ts"
            and f.is_file()}


def _unused() -> list[str]:
    texts = _console_sources()
    out = []
    for name, obj in _bindings().items():
        if not any(re.search(rf"\b{obj}\.{name}\s*\(", t)
                   for t in texts.values()):
            out.append(f"{obj}.{name}")
    return sorted(out)


def _recorded() -> list[str]:
    return [line.strip() for line in
            SNAPSHOT.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_the_unused_bindings_match_the_record():
    actual = _unused()
    recorded = _recorded()

    appeared = sorted(set(actual) - set(recorded))
    resolved = sorted(set(recorded) - set(actual))

    problems = []
    if appeared:
        problems.append(
            f"{len(appeared)} binding(s) nothing calls:\n    "
            + "\n    ".join(appeared)
            + "\n  (wire it to a screen, or record it here — but note that "
              "its route is being counted as doored either way)")
    if resolved:
        problems.append(
            f"{len(resolved)} binding(s) now have a caller — strike them from "
            f"{SNAPSHOT.name}:\n    " + "\n    ".join(resolved))
    assert not problems, "\n\n".join(problems)


def test_it_only_shrinks():
    assert len(_recorded()) <= STARTED_AT, (
        f"{len(_recorded())} unused bindings, above the {STARTED_AT} this "
        "guard started at — bindings are being written faster than the "
        "screens that call them, which is exactly what inflates the door "
        "count without building a door")


def test_the_scan_finds_the_bindings_at_all():
    """A guard on the guard. If the shape of `api.ts` changed — a different
    indent, a different declaration style — this would find nothing, every
    binding would read as used, and the file would pass vacuously.

    Thresholds are kept low enough to hold in all three repositories, which
    have consoles of very different sizes. What matters is that the number is
    not near zero.
    """
    found = _bindings()
    assert len(found) > 20, (
        f"only {len(found)} bindings parsed out of api.ts — the pattern has "
        "stopped matching, so 'nothing is unused' means nothing")
    exported = {m.group(1) for m in re.finditer(
        r"^export const (\w+) = \{", API.read_text(encoding="utf-8"), re.M)}
    assert set(found.values()) <= exported, (
        "a binding was attributed to an object that is not exported, so the "
        "caller pattern it builds cannot match anything")


def test_most_bindings_are_seen_as_used():
    """The positive control, and the reason it is a *fraction* rather than a
    named binding.

    A caller scan that broke completely would report every binding unused,
    and the honest-looking fix would be to grow the snapshot until the test
    passed again — red for the wrong reason, repaired the wrong way. Naming
    one binding would catch that, but ties this file to one product's screens;
    a proportion catches it in any of the three.
    """
    total = len(_bindings())
    unused = len(_unused())
    assert unused < total / 2, (
        f"{unused} of {total} bindings have no caller — that is not a "
        "backlog, that is the caller scan finding nothing")
