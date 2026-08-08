"""A header a route needs is a header its callers send.

## Where this came from

0.58.0 asked whether the three shells sent every header the console sent, and
found `x-llm-api-key` in one client and no other. It has held since, and this
round found what it cannot see.

**Parity is a relative check, and a relative check is satisfied by everyone
being equally wrong.** Every client in this product agreed about
`x-tenant-key`: none of them sent it outside two bequest calls. The comparison
passed. The vault was unusable.

    asked     do the clients send the same headers as each other
    mattered  do the clients send the headers the routes require

## What it was, next door

The instance is PDI's and the shape is the estate's. A tenant there that moved
its vault under a customer-managed key locked **every client in that product**
out of every record — console and all three shells alike — because
`x-tenant-key` is required by the auth dependency and was sent by nobody
outside two heir routes. The comparison 0.58.0 wrote passed the whole time:
the clients agreed with each other.

This product has no such header today. The file is here because the question
is not about that header, and a guard that arrives after the second instance
is a guard that was written twice.

## What this asks instead

The requirement is read from the **application**, not from any client:
FastAPI already resolves each route's header parameters through its whole
dependency tree, so `_tenant`'s `x_tenant_key` is attributed to every route
that depends on it, and `_writer`'s to everything under that. Nothing here
parses Python to work it out, and nothing here can be satisfied by a client.

Then, per client, per route that client actually calls: can it send what the
route requires? A client that has no door to a route is not asked about its
headers — this is a question about the clients that go there.

## The record

`unsendable_headers.txt` carries the pairs that are deliberate. There is one
kind so far, and it needs a reason rather than a shrug: a header no client is
*meant* to send, because the route is not for a client. Every row names the
client and the header, and the ceiling only comes down.
"""

from __future__ import annotations

import functools
import re
from pathlib import Path

import pytest
from starlette.routing import Match

from jim.api import app

from . import clientpaths as cp
from . import ratchets

#: Headers the transport sets on its own, or that this suite already guards
#: elsewhere. `accept-language` has a whole file of its own
#: (`test_the_language_nobody_was_sending.py`) and `authorization` is the
#: subject of every auth test in the suite; repeating them here would report
#: the same defect twice and hide a new one in the noise.
CARRIED = {"authorization", "content-type", "accept", "accept-language",
           "user-agent", "host", "cookie", "referer", "origin",
           "content-length"}

#: Per client: how a header is spelled, where the shared dispatcher starts,
#: and what ends it.
#:
#: The split between *dispatched* and *at the call site* is the whole point of
#: this file. A header set in the dispatcher rides every request the client
#: makes. A header set beside one call rides that call. Counting the two as
#: one is what let the console pass: it can spell `x-tenant-key`, on the two
#: heir routes, and nowhere near the forty that need it.
CLIENTS = {
    "console": (cp.CONSOLE, r'headers\[\s*"([\w-]+)"\s*\]|"([xX]-[\w-]+)"\s*:',
                (r"async function req<T>\(", r"async function reqText\("),
                "\n}"),
    "ios": (cp.IOS, r'forHTTPHeaderField:\s*"([\w-]+)"',
            (r"private func request<T: Decodable>\(",), "\n    }"),
    "android": (cp.ANDROID, r'setRequestProperty\(\s*"([\w-]+)"',
                (r"private suspend fun request\(",), "\n    }"),
    "windows": (cp.WINDOWS,
                r'Headers\.(?:TryAddWithoutValidation|Add)\(\s*"([\w-]+)"',
                (r"private Task<HttpResponseMessage> Dispatch\(",), "\n    }"),
}

#: How far from a path literal a header may be set and still belong to that
#: request. The sibling `test_the_language_nobody_was_sending.py` windows the
#: same way for the same reason — a header set a page away belongs to a
#: different call — and this is its 900, measured rather than guessed: the
#: iOS intake submit sets `X-Submit-Token` twelve lines below its path,
#: because a comment explaining the language header sits between them.
WINDOW = 900

RECORD = Path(__file__).resolve().parent / "unsendable_headers.txt"

#: The header this product's own clients must carry on every request. One
#: question, three answers — see the named check at the bottom of this file.
NAMED_HEADER = "x-llm-api-key"

#: This product's package directory name, walked up to from this file.
PACKAGE = "jim"


def _dependant_headers(dep) -> set[str]:
    """Every header this route reads, including through its dependencies.

    FastAPI has already done this resolution to build the route; walking its
    `dependant` tree is reading the application's own answer rather than
    forming a second opinion about it in a regex.
    """
    found = {p.alias.lower() for p in dep.header_params}
    for sub in dep.dependencies:
        found |= _dependant_headers(sub)
    return found


def declared() -> dict[tuple[str, str], set[str]]:
    """(method, path) -> every header that route reads, `CARRIED` included.

    The liveness reader. `required()` below subtracts the headers the
    transport carries, and in two of the three products that subtraction is
    everything — which is a true answer about those products and
    indistinguishable from `_dependant_headers` having broken.
    """
    out: dict[tuple[str, str], set[str]] = {}
    for route in _table():
        dep = getattr(route, "dependant", None)
        if dep is None:
            continue
        found = _dependant_headers(dep)
        if not found:
            continue
        for method in sorted(getattr(route, "methods", None) or []):
            if method not in ("HEAD", "OPTIONS"):
                out[(method, route.path)] = found
    return out


#: How a header is read outside a signature: straight off the request, inside
#: a handler or a helper a handler calls. FastAPI knows nothing about these,
#: so no dependency walk can attribute them to a route — but a client still
#: has to be able to send them, and this is the whole story in two of the
#: three products.
_OFF_THE_REQUEST = re.compile(r'headers\.get\(\s*["\']([\w-]+)["\']')


def read_anywhere() -> dict[str, set[str]]:
    """header -> the modules that read it off the request directly."""
    out: dict[str, set[str]] = {}
    # From the checkout root rather than by walking up from here: this file
    # sits under `tests/` in one product and `<pkg>/tests/` in the others,
    # and a loop looking upward for a directory named after the package
    # finds it in two of the three and runs off the top of the filesystem in
    # the third.
    root = next(d for d in Path(__file__).resolve().parents
                if (d / "pyproject.toml").exists())
    for f in sorted((root / PACKAGE).rglob("*.py")):
        if "tests" in f.parts:
            continue
        for h in _OFF_THE_REQUEST.findall(f.read_text(encoding="utf-8")):
            if h.lower() not in CARRIED:
                out.setdefault(h.lower(), set()).add(f.name)
    return out


def required() -> dict[tuple[str, str], set[str]]:
    """(method, path template) -> the headers that route reads."""
    out: dict[tuple[str, str], set[str]] = {}
    for route in _table():
        dep = getattr(route, "dependant", None)
        if dep is None:
            continue
        needs = _dependant_headers(dep) - CARRIED
        if not needs:
            continue
        for method in sorted(getattr(route, "methods", None) or []):
            if method in ("HEAD", "OPTIONS"):
                continue
            out[(method, route.path)] = needs
    return out


@functools.lru_cache(maxsize=1)
def _table() -> tuple:
    """The flat route table, walked once.

    `cp.all_routes` rather than `app.routes`: FastAPI wraps every
    `include_router` in an `_IncludedRouter` that carries no path of its own,
    so the top level shows a handful of routes against the hundreds actually
    mounted. Cached because the pass below asks it a question per call site,
    and this product has hundreds of those.
    """
    return tuple(cp.all_routes(app))


@functools.lru_cache(maxsize=None)
def _route_for(method: str, path: str):
    """The route a client's (method, path) actually reaches, or None."""
    scope = {"type": "http", "method": method, "path": path,
             "root_path": "", "headers": []}
    for route in _table():
        if route.matches(scope)[0] == Match.FULL:
            return route
    return None


def _names(pattern: str, text: str) -> set[str]:
    return {g.lower() for m in re.finditer(pattern, text) for g in m.groups()
            if g}


@functools.lru_cache(maxsize=None)
def _sources(lang) -> tuple[tuple[Path, str], ...]:
    """Every source file of a client, read once.

    Cached because the call-site pass below asks about hundreds of paths and
    the largest of these clients is fifty files; reading them per question
    turned this file into the slowest in the suite by an order of magnitude.
    """
    return tuple((f, f.read_text(encoding="utf-8", errors="ignore"))
                 for f in sorted(lang.root.rglob("*"))
                 if f.suffix in lang.suffixes and f.is_file())


def dispatched(name: str) -> set[str]:
    """Headers this client sets on **every** request it makes.

    Read out of the shared dispatcher's own body rather than the whole file:
    0.57.9 consolidated each client onto one send site precisely so that a
    header could be set once, and this is the set that consolidation buys.
    """
    lang, header, openers, closer = CLIENTS[name]
    found: set[str] = set()
    if not lang.root.exists():
        return found
    for _, text in _sources(lang):
        for opener in openers:
            for m in re.finditer(opener, text):
                end = text.find(closer, m.end())
                found |= _names(header, text[m.start():end if end > 0 else None])
    return found


def at_call(name: str) -> dict[str, set[str]]:
    """path literal -> the headers set beside the call that sends it."""
    lang, header, _, _ = CLIENTS[name]
    out: dict[str, set[str]] = {}
    if not lang.root.exists():
        return out
    by_name: dict[str, list[str]] = {}
    for f, text in _sources(lang):
        by_name.setdefault(f.name, []).append(text)
    for (_method, path), (rel, raw) in cp.calls(lang).items():
        for text in by_name.get(rel.split("/")[-1], ()):
            for m in re.finditer(re.escape(raw), text):
                window = text[max(0, m.start() - WINDOW):m.end() + WINDOW]
                out.setdefault(path, set()).update(_names(header, window))
    return out


def sendable(name: str) -> set[str]:
    """Every header this client can spell anywhere. Used only by the named
    check below and by the liveness guard — never to excuse a route."""
    lang, header, _, _ = CLIENTS[name]
    found: set[str] = set()
    if not lang.root.exists():
        return found
    for _, text in _sources(lang):
        found |= _names(header, text)
    return found


def _recorded() -> set[tuple[str, str]]:
    rows = [ln.strip() for ln in RECORD.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.startswith("#")]
    out = set()
    for row in rows:
        client, header = row.split(": ", 1)
        out.add((client.strip(), header.strip()))
    return out


def gaps() -> list[tuple[str, str, tuple[str, str]]]:
    """(client, header, the first route it calls that needs it)."""
    need = required()
    out: list[tuple[str, str, tuple[str, str]]] = []
    for name in sorted(CLIENTS):
        lang = CLIENTS[name][0]
        always, beside = dispatched(name), at_call(name)
        missing: dict[str, tuple[str, str]] = {}
        for method, path in sorted(cp.calls(lang)):
            route = _route_for(method, path)
            if route is None:
                continue
            here = always | beside.get(path, set())
            for header in sorted(need.get((method, route.path), ())):
                if header not in here:
                    missing.setdefault(header, (method, path))
        out += [(name, h, where) for h, where in sorted(missing.items())]
    return out


def test_every_header_a_route_requires_its_callers_can_send():
    """The check that does not depend on any client being right.

    A client is asked only about the routes it has a door to. What it is
    asked is whether it can present what the application requires there —
    which is a claim about the application and this client, and never about
    what the other clients happen to do.
    """
    unrecorded = [(c, h, w) for c, h, w in gaps() if (c, h) not in _recorded()]
    assert not unrecorded, (
        "these clients call routes whose headers they cannot send:\n    "
        + "\n    ".join(f"{c}: never sends {h!r}, and calls {w[0]} {w[1]}"
                        for c, h, w in unrecorded)
        + "\n  Every one of those calls is refused by the application before "
          "it reaches a handler, in a way no test that calls the app "
          "in-process can see.")


def test_the_key_this_product_asks_for_is_sendable_by_every_client():
    """The named instance, spelled out as well as swept for.

    A sweep that stops matching goes quiet, and the quiet reads exactly like a
    fix — so the one header this product's clients must carry is asserted by
    name, in the dispatcher, where it rides every request rather than two.

    The name is the same in all three suites and the header is not: this is
    one question with three answers, and giving it three names would put two
    rows in the divergence backlog for a guard that did travel.
    """
    blind = [name for name in sorted(CLIENTS)
             if NAMED_HEADER not in dispatched(name)]
    assert not blind, (
        f"{', '.join(blind)} cannot present {NAMED_HEADER} on every request, "
        f"which this product requires to carry the person's own model key. A client that can "
        "spell it beside one call can spell it nowhere that matters.")


def test_the_readers_account_for_every_header_a_client_sends():
    """Liveness, with no number chosen by hand.

    Two readers feed this file — the dependency walk and the off-the-request
    sweep — and the three products lean on them in opposite proportions: 103
    routes declare a header in one, and one route does in another. A floor
    tuned per product would be three numbers to keep honest.

    So the question is asked the other way round. Every non-transport header
    a client sends must be one some reader here found. A header a client
    sends that neither reader knows about is either a client talking to
    itself or a reader gone blind, and both are worth stopping on.
    """
    known = set(read_anywhere())
    for headers in declared().values():
        known |= headers
    sent = {h for name in CLIENTS for h in sendable(name)} - CARRIED
    unread = sorted(sent - known)
    assert not unread, (
        "clients send these and neither reader in this file finds the "
        f"backend reading them: {unread}\n  Either the backend stopped "
        "reading a header its clients still send, or the readers here have "
        "gone blind and every check in this file is passing on nothing.")


def test_the_dependency_walk_descends():
    """The reader itself, as a unit.

    `_dependant_headers` is the whole basis of the route-level check, and its
    one interesting property is that it goes *through* dependencies rather
    than reading signatures. Two of the three products barely exercise that
    today, so it is exercised here instead of being assumed.
    """
    from fastapi import Depends, FastAPI, Header

    def inner(x_deep: str = Header(default="")) -> str:
        return x_deep

    def outer(who: str = Depends(inner)) -> str:
        return who

    probe = FastAPI()

    @probe.get("/probe")
    def _handler(who: str = Depends(outer)) -> dict:
        return {"who": who}

    route = next(r for r in probe.routes if getattr(r, "path", None) == "/probe")
    found = _dependant_headers(route.dependant)
    assert "x-deep" in found, (
        f"the walk found {sorted(found)} — it is reading signatures rather "
        "than descending, and every inherited requirement is invisible to it")


def test_every_client_is_still_being_read():
    """Four clients, each of which must be found and must set some header.

    A moved directory or a renamed helper makes `sendable()` answer the empty
    set, and an empty set is indistinguishable from a client that sends
    nothing — except that one of them is this file going blind.
    """
    for name in sorted(CLIENTS):
        found, always = sendable(name), dispatched(name)
        assert found, f"{name}: no headers found at all — the reader is blind"
        assert always, (f"{name}: the shared dispatcher reads as empty — "
                        "its opener or its closer has moved, and an empty "
                        "dispatcher makes every route below look uncovered")
        assert "authorization" in found, f"{name}: found {sorted(found)}"


def test_the_record_holds_only_deliberate_rows():
    """The backlog only shrinks, and every row in it still describes reality.

    A row for a client that has since learned the header is a row that would
    excuse the next regression, so it is a failure rather than a tidy-up.
    """
    reach = {h for name in CLIENTS for h in sendable(name)}
    recorded = _recorded()
    actual = {(c, h) for c, h, _ in gaps()}
    # The `*` rows answer the product-wide question rather than the
    # route-level one, so they are stale on the same terms: when a client
    # learns the header, the row goes.
    actual |= {("*", h) for h in read_anywhere() if h not in reach}
    stale = sorted(recorded - actual)
    assert not stale, (
        "these rows name a gap that no longer exists — strike them:\n    "
        + "\n    ".join(f"{c}: {h}" for c, h in stale))
    ceiling = int(re.search(r"# ceiling: (\d+)",
                            RECORD.read_text(encoding="utf-8")).group(1))
    assert len(recorded) <= ceiling, f"{len(recorded)} rows against {ceiling}"


@pytest.mark.parametrize("name", sorted(CLIENTS))
def test_every_client_reaches_some_route(name):
    """The other half of the liveness question: a client whose call reader
    stopped matching calls nothing, needs nothing, and passes.

    The floor comes from `ratchets` rather than a literal, because a literal
    here would be a tenth bare floor in a suite whose whole 0.59.0 round was
    about floors nobody could audit — and `route.calls.<client>` already
    measures this exact quantity for the route audit.
    """
    lang = CLIENTS[name][0]
    floor = ratchets.floor(f"route.calls.{name}")
    found = len(cp.calls(lang))
    assert found >= floor, (
        f"{name}: only {found} call(s) extracted against a floor of {floor} "
        "— the reader has lost a form, and a client that calls nothing is "
        "asked nothing here")


def test_every_header_read_off_the_request_is_sendable_or_recorded():
    """The half no dependency walk can reach.

    A header taken straight off the request inside a handler is invisible to
    FastAPI's signature machinery, so `required()` never sees it and the
    route-level check above never asks about it. In two of the three products
    that is *every* non-transport header there is, which would leave this
    file passing on nothing at all in those repositories.

    Asked as a product-wide question, because the attribution is genuinely
    unavailable: some client must be able to present it, or the pair is
    recorded with its reason.
    """
    reach = {h for name in CLIENTS for h in sendable(name)}
    orphan = sorted((h, sorted(where)) for h, where in read_anywhere().items()
                    if h not in reach and ("*", h) not in _recorded())
    assert not orphan, (
        "the backend reads these headers and no client can send one:\n    "
        + "\n    ".join(f"{h!r}, read in {', '.join(w)}" for h, w in orphan)
        + "\n  Either a client should be presenting it, or the row belongs "
          "in unsendable_headers.txt with the reason it should not.")
