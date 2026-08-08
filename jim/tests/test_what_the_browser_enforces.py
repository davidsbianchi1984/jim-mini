"""The rules the server declares and the browser enforces.

0.59.1 found a CORS defect in a sibling product by comparing three
repositories, not by testing behaviour — because **no test in this estate
could have found it.** Every one of them calls the app through a
`TestClient`, which never sends an `Origin`, never runs a preflight, and
never drops a response for want of a header. The whole class is invisible.

    asked     does the server answer
    mattered  does the answer reach the reader

## What that blindness was hiding here

An unhandled exception is rendered by Starlette's `ServerErrorMiddleware`,
which sits **outside** every middleware this app adds — including CORS. So a
500 went back to a browser with no `access-control-allow-origin`, and the
browser discarded the entire response. Measured over HTTP at 0.59.2, in all
three products:

    GET /health   200   access-control-allow-origin: *
    a 500         500   access-control-allow-origin: None

The consequence is worse than a missing header. This estate's consoles
distinguish *the backend is unreachable* from *the backend refused* — the
version-mismatch guard and the content-free problem reporter both depend on
it — and a 500 the browser throws away is indistinguishable from the first.
Every crash in this product reached its user as "Failed to fetch".

Registering `@app.exception_handler(Exception)` does not fix it: Starlette
hands that handler to `ServerErrorMiddleware`, still outside the CORS layer.
It has to be a middleware, inside CORS, which is why the CORS block is now the
last one the factory adds — and why the ordering has its own check below. The
three products used to disagree about it: two added CORS before their
request-scoped middleware and one after.

## Why this file starts a real server

Everything above is invisible from inside the process. So this file boots the
app under uvicorn on an ephemeral port and talks to it with a plain HTTP
client, sending the header a browser would send. It is slower than the rest of
the suite and it is the only way to ask the question at all.

The last test in this file is the point of the whole exercise: it makes the
same request through a `TestClient` and shows it passing.
"""

from __future__ import annotations

import socket
import threading
import time
import urllib.error
import urllib.request

import pytest
from fastapi.middleware.cors import CORSMiddleware

from jim.api import create_app

#: The origin a packaged console calls from. Any value works — what matters is
#: that one is sent at all, which is exactly what an in-process client omits.
ORIGIN = "http://localhost:5173"

#: Where the fixture hangs a route that raises. Added to a throwaway app built
#: by the factory, never to the module-level one, so nothing else in the suite
#: can meet it.
BOOM = "/__a_route_that_raises"


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _ask(port: int, path: str, method: str = "GET",
         origin: str | None = ORIGIN, extra: dict | None = None):
    """One request, the way a browser makes it. Returns (status, headers)."""
    headers = {} if origin is None else {"Origin": origin}
    headers.update(extra or {})
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}",
                                 headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.headers
    except urllib.error.HTTPError as e:
        return e.code, e.headers


@pytest.fixture(scope="module")
def served(monkeypatch_session=None):
    """The real app, on a real port, behind a real HTTP server."""
    import os

    import uvicorn

    before = os.environ.get("JIM_CORS_ORIGINS")
    os.environ["JIM_CORS_ORIGINS"] = "*"
    try:
        app = create_app()
    finally:
        if before is None:
            os.environ.pop("JIM_CORS_ORIGINS", None)
        else:
            os.environ["JIM_CORS_ORIGINS"] = before

    @app.get(BOOM)
    def _raises():
        raise RuntimeError("a route that fails the way routes fail")

    port = _free_port()
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port,
                                           log_level="critical"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(100):                       # ~10s, generous for a cold app
        if server.started:
            break
        time.sleep(0.1)
    if not server.started:                     # pragma: no cover - a bad day
        server.should_exit = True
        pytest.fail("the probe server never came up, so nothing below is a "
                    "measurement of anything")
    yield port, app
    server.should_exit = True
    thread.join(timeout=10)


def test_the_probe_is_actually_talking_to_a_server(served):
    """A guard on the guard. Every check here would pass on a server that
    answered nothing, if the client swallowed the failure."""
    port, _ = served
    status, headers = _ask(port, "/health")
    assert status == 200, f"/health answered {status}"
    assert headers.get("access-control-allow-origin") == "*", (
        "the probe server is up but CORS is not configured on it, so the "
        "checks below are measuring the wrong app")


def test_a_route_that_fails_still_answers_the_console(served):
    """The defect, directly. A 500 the browser discards is a crash the user
    meets as "Failed to fetch" — the same thing they see when the backend is
    not running at all."""
    port, _ = served
    status, headers = _ask(port, BOOM)
    assert status == 500
    assert headers.get("access-control-allow-origin") == "*", (
        "a 500 came back with no access-control-allow-origin, so a browser "
        "drops the whole response and the console cannot tell a crash from an "
        "unreachable backend. The catch-all middleware has to sit inside the "
        "CORS layer — see create_app.")


def test_a_refusal_reaches_the_reader(served):
    """Every refusal in this product is translated into the reader's language.
    None of that arrives if the response is discarded before it is read."""
    port, _ = served
    status, headers = _ask(port, "/no-such-route-at-all")
    assert status == 404
    assert headers.get("access-control-allow-origin") == "*", (
        "a refusal came back without the header, so the sentence it carries "
        "never reaches the person it was written for")


def test_a_preflight_is_answered(served):
    """Before any request a browser considers non-simple, it asks permission.
    A 405 here is the console's every write dying before it is sent."""
    port, _ = served
    status, headers = _ask(port, "/health", method="OPTIONS", extra={
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "content-type"})
    assert status == 200, f"the preflight answered {status}"
    assert headers.get("access-control-allow-origin") == "*"
    assert "POST" in (headers.get("access-control-allow-methods") or "")


def test_the_cors_layer_is_the_outermost_one(served):
    """Ordering, checked rather than assumed.

    `add_middleware` inserts at the front, so the last one registered is the
    outermost. If anything is added after CORS, the response that middleware
    builds — including the catch-all's 500 — goes back without the header
    again, and every test above starts passing for the wrong reason.
    """
    _, app = served
    assert app.user_middleware, "no user middleware at all"
    assert app.user_middleware[0].cls is CORSMiddleware, (
        "CORS is not the outermost middleware; it is "
        f"{[m.cls.__name__ for m in app.user_middleware]}. Whatever sits "
        "outside it answers without the header.")


def test_an_in_process_client_cannot_see_any_of_this(served):
    """The point of the file, as a unit.

    The same failing route, through the client the rest of the suite uses.
    It reports a clean 500 with a body, because a `TestClient` speaks ASGI
    directly: no origin is sent, no browser rule is applied, and nothing is
    discarded. Three thousand tests could pass on an API no console can read.
    """
    from fastapi.testclient import TestClient

    _, app = served
    with TestClient(app, raise_server_exceptions=False) as client:
        answer = client.get(BOOM)
    assert answer.status_code == 500
    assert "access-control-allow-origin" not in {k.lower() for k in answer.headers}
