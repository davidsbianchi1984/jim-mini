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

import re
import socket
import threading
import time
import urllib.error
import urllib.parse
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

#: The shape of a built console page: an external same-origin script with no
#: nonce, exactly what `vite build` writes. The suite runs without a
#: front-end build, so the fixture lays this down itself — the question here
#: is about the headers, not the bundle.
CONSOLE_PAGE = (
    "<!doctype html><html><head>"
    '<script type="module" crossorigin src="./assets/index-test.js"></script>'
    '<link rel="stylesheet" crossorigin href="./assets/index-test.css">'
    '</head><body><div id="root"></div></body></html>')


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


def _page(port: int, path: str):
    """Headers **and** body from one request.

    Two requests would not do, and the first draft of this file used two: the
    nonce is minted per response, so a header read from one request and a
    body read from another can never agree. That draft failed against correct
    code and the failure looked exactly like the defect it was written for —
    which is its own small lesson about measuring one thing twice.
    """
    req = urllib.request.Request(f"http://127.0.0.1:{port}{path}")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.headers, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.headers, e.read().decode("utf-8", "replace")


def _body(port: int, path: str) -> str:
    return _page(port, path)[2]


@pytest.fixture(scope="module")
def served(monkeypatch_session=None):
    """The real app, on a real port, behind a real HTTP server."""
    import os
    import tempfile
    from pathlib import Path

    import uvicorn

    # A console dist for the factory to find, whether or not app/ was built:
    # the blanking defect below lives in the headers stamped on the console's
    # HTML, and a suite that only measures it where somebody happened to run
    # `npm run build` is a suite that misses it on CI.
    dist = Path(tempfile.mkdtemp(prefix="console-dist-"))
    (dist / "assets").mkdir()
    (dist / "index.html").write_text(CONSOLE_PAGE)
    (dist / "assets" / "index-test.js").write_text("/* the bundle */\n")
    (dist / "assets" / "index-test.css").write_text("/* the styles */\n")

    before = os.environ.get("JIM_CORS_ORIGINS")
    console_before = os.environ.get("JIM_CONSOLE_DIR")
    os.environ["JIM_CORS_ORIGINS"] = "*"
    os.environ["JIM_CONSOLE_DIR"] = str(dist)
    try:
        app = create_app()
    finally:
        for name, kept in (("JIM_CORS_ORIGINS", before),
                           ("JIM_CONSOLE_DIR", console_before)):
            if kept is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = kept

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

#: The pages a person reaches without an account, on a device that is not
#: theirs. Each is (path, the status it answers with no data behind it).
#: A 404 page is still a page: it is served as HTML from this origin and a
#: browser applies the same rules to it.
STRANGER_PAGES = (("/verify-email/click", 403),)

#: Reflected straight into the OAuth callback's HTML until 0.59.3.
PAYLOAD = "<script>alert(document.domain)</script>"


@pytest.mark.parametrize("path,expected", STRANGER_PAGES,
                         ids=lambda v: str(v).strip("/") or "root")
def test_every_page_a_stranger_reaches_carries_a_policy(served, path, expected):
    """The headers a browser reads and an in-process client does not.

    Until 0.59.3 every HTML page in every one of the three products went out
    with none of these — measured over HTTP, which is the only place the
    question exists.
    """
    port, _ = served
    status, headers = _ask(port, path, origin=None)
    assert status == expected, f"{path} answered {status}"
    assert headers.get("content-type", "").startswith("text/html")
    missing = [name for name in ("content-security-policy",
                                 "x-content-type-options", "x-frame-options",
                                 "referrer-policy") if not headers.get(name)]
    assert not missing, (
        f"{path} is HTML a stranger reaches and carries no {missing}. "
        "See pagehead.py — the middleware stamps these on any text/html "
        "response, so a page without them is a page the middleware did not "
        "see.")


def test_the_policy_names_a_nonce_rather_than_permitting_everything(served):
    """A `Content-Security-Policy` with `script-src 'unsafe-inline'` permits
    exactly what an injected `<script>` needs. It would satisfy the check
    above and stop nothing, which is this session's recurring shape."""
    port, _ = served
    _, headers = _ask(port, STRANGER_PAGES[0][0], origin=None)
    policy = headers["content-security-policy"]
    script = next((part.strip() for part in policy.split(";")
                   if part.strip().startswith("script-src")), "")
    assert script, f"no script-src in the policy: {policy}"
    assert "'unsafe-inline'" not in script, (
        f"script-src permits inline script ({script}), so the policy is "
        "decoration: an injected tag runs under it.")
    assert "'nonce-" in script or script.endswith("'none'"), (
        f"script-src names neither a nonce nor 'none': {script}")


def test_the_page_and_its_policy_agree_about_the_nonce(served):
    """The failure that would ship silently.

    If the header's nonce and the page's `<script nonce=…>` ever stop
    matching, the policy is still perfect and the page's own script stops
    running — a screen that quietly loses its behaviour, which is exactly
    what nobody notices.
    """
    port, _ = served
    looked = 0
    for path, _expected in STRANGER_PAGES:
        _status, headers, body = _page(port, path)
        if "<script" not in body:
            continue
        looked += 1
        policy = headers["content-security-policy"]
        wanted = re.search(r"'nonce-([^']+)'", policy)
        assert wanted, f"{path} serves a script and the policy names no nonce"
        assert f'nonce="{wanted.group(1)}"' in body, (
            f"{path} carries an inline script whose nonce is not the one in "
            "the policy, so the browser refuses to run it")
    assert looked or not any("<script" in _body(port, p)
                             for p, _ in STRANGER_PAGES), (
        "no page reached here carries an inline script, so this check ran on "
        "nothing — the pages it was written for have moved")


def _directives(policy: str) -> dict[str, str]:
    """A CSP as a mapping, so an assertion can name the directive it means."""
    out: dict[str, str] = {}
    for part in policy.split(";"):
        name, _, rest = part.strip().partition(" ")
        if name:
            out[name] = rest
    return out


def test_the_console_is_not_blanked_by_its_own_policy(served):
    """The beta's first live defect, measured the only place it exists.

    The console's script and stylesheet are external same-origin files whose
    names are stamped at build time — no per-response nonce can ever reach
    them. Under the nonce policy the browser refuses the bundle and the
    console renders as a dark, empty page: HTML 200, nothing running. That is
    what 0.60.9 shipped to its first real host, on all three products, while
    every in-process test passed — a `TestClient` reads the policy and
    enforces none of it.
    """
    port, _ = served
    status, headers, body = _page(port, "/app/")
    assert status == 200, f"/app/ answered {status}"
    assert "<script" in body and "nonce" not in body, (
        "the fixture's console page no longer matches the shape this test "
        "was written for — an external script with no nonce")
    policy = headers.get("content-security-policy", "")
    assert policy, "/app/ went out with no Content-Security-Policy at all"
    got = _directives(policy)
    assert "'self'" in got.get("script-src", ""), (
        f"script-src is {got.get('script-src')!r}: the console's bundle is "
        "an external same-origin script with no nonce, and a policy that "
        "does not name 'self' blanks the whole console. See "
        "pagehead.console_policy.")
    assert "'unsafe-inline'" not in got.get("script-src", ""), (
        "the console policy permits inline script, which hands back exactly "
        "what the nonce policy exists to refuse")
    assert "'self'" in got.get("style-src", ""), (
        f"style-src is {got.get('style-src')!r} and the console's stylesheet "
        "is an external same-origin file")
    for name in ("worker-src", "manifest-src"):
        assert "'self'" in got.get(name, ""), (
            f"{name} is {got.get(name)!r}: under default-src 'none' the "
            "console's service worker and manifest are refused unless the "
            "policy names them")
    assert "blob:" in got.get("img-src", ""), (
        "img-src refuses blob:, so every preview the console builds from a "
        "local file renders broken")
    assert "blob:" in got.get("media-src", ""), (
        "media-src refuses blob:, so the wall's footage and the synthesised "
        "audio never play")


def test_the_stranger_pages_keep_the_nonce_policy(served):
    """The guard on the fix. Widening the console's policy must not widen the
    pages a stranger reaches — their scripts are inline, their policy names a
    nonce, and a `script-src 'self'` there would be a quiet retreat."""
    port, _ = served
    _, headers = _ask(port, STRANGER_PAGES[0][0], origin=None)
    got = _directives(headers["content-security-policy"])
    assert "'nonce-" in got.get("script-src", ""), (
        "the stranger pages lost their nonce policy — the console's wider "
        "policy has leaked past /app")
    assert "'self'" not in got.get("script-src", "")


def test_the_front_door_opens_on_the_console(served):
    """Measured live at 0.60.9: the bare domain answered
    {"detail": "Not Found"}, and a tester types the domain, not the mount
    point. The client here follows redirects the way a browser does — landing
    on the console's page is the assertion."""
    port, _ = served
    status, _headers, body = _page(port, "/")
    assert status == 200, f"the front door answered {status}"
    assert 'id="root"' in body, (
        "the root URL did not land on the console's page")


def test_a_reflected_parameter_is_not_markup(served):
    """The defect, directly.

    `?error=<script>…` on the sign-in callback came back verbatim, executing
    on this product's own origin — reachable by anyone who can get a person
    to follow a link.
    """
    port, _ = served
    body = _body(port, "/auth/oauth/google/callback?"
                 + urllib.parse.urlencode({"error": PAYLOAD}))
    assert PAYLOAD not in body, (
        "a query parameter came back as live markup on an HTML page served "
        "from this origin — that is reflected cross-site scripting. Escape "
        "it at the interpolation; the policy is the second line, not the "
        "first.")
    assert "&lt;script&gt;" in body, (
        "the payload is neither reflected nor escaped — this test has "
        "stopped exercising the path it was written for")


def test_the_api_is_left_alone(served):
    """A page policy on a JSON response would be noise at best. The
    middleware keys off the content type, and this is the check that it
    actually does."""
    port, _ = served
    _, headers = _ask(port, "/health")
    assert headers.get("content-type", "").startswith("application/json")
    assert not headers.get("content-security-policy")


def test_a_page_stamps_the_nonce_it_was_given():
    """The integration check above can only run where a reachable page carries
    an inline script. This is the same contract as a unit, so it holds in
    every product whatever their pages happen to serve today."""
    from jim import pagehead

    minted = pagehead.new_nonce()
    assert minted and pagehead.nonce() == minted
    assert pagehead.script_open() == f'<script nonce="{minted}">'
    assert f"'nonce-{minted}'" in pagehead.policy(minted)
    assert "'unsafe-inline'" not in [
        part.strip() for part in pagehead.policy(minted).split(";")
        if part.strip().startswith("script-src")][0]


def test_a_page_built_outside_a_request_carries_no_borrowed_nonce():
    """A builder called with no request behind it — a preview, a test — must
    not stamp a stale nonce from whatever ran last. It emits a bare tag, which
    the policy then refuses, which is the loud failure rather than the quiet
    one."""
    from jim import pagehead

    pagehead._NONCE.set("")
    assert pagehead.script_open() == "<script>"
    assert "script-src 'none'" in pagehead.policy("")
