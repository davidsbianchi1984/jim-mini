"""The error log must not be able to carry anything private.

`app/src/errors.ts` records failed requests so bugs can be found. It runs in
every console, on every failure, without asking — which makes it the one piece
of diagnostic code that could quietly undo what the rest of these products
promise. The backends put user input straight into their error messages:

    no device called 'Pixel Buds' on this account
    unknown site 'knee'; one of scalp, face, eye, mouth…

Those are good messages for the person reading them and terrible things to keep.
In JIM they could be health content. So the design is that the message is never
recorded at all, and this file exists to keep that true rather than trusting it
to stay true.

The tests are structural on purpose. A behavioural test would need a JavaScript
runtime, and the console CI job only builds; asserting on the *shape* of the
module runs in the suite that already exists and catches the changes that
matter — a message parameter appearing, a field being added, the redaction
being narrowed.

One limitation, stated rather than hidden: the redaction cases below apply the
patterns with Python's `re` after reading them out of the TypeScript. For these
four patterns — anchored character classes with simple quantifiers — the two
dialects agree, but a future pattern using JavaScript-specific syntax would be
tested by an approximation rather than by the real thing.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

def _repo_root() -> Path:
    """The directory holding pyproject.toml.

    Walked up rather than counted in `.parent`s: this file sits at `tests/` in
    one repo and `{pkg}/tests/` in the others, exactly as clientpaths.py does.
    """
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
ERRORS_TS = REPO / "app" / "src" / "errors.ts"
API_TS = REPO / "app" / "src" / "api.ts"

# Words that would mean the log had started keeping content.
FORBIDDEN_FIELDS = ("message", "detail", "body", "response", "text", "payload",
                    "url", "path", "error", "stack", "token")


def _source() -> str:
    return ERRORS_TS.read_text(encoding="utf-8")


def test_the_recorder_has_nowhere_to_put_a_message():
    """The signature is the safeguard.

    `recordProblem(method, path, status)` takes no message, so a caller cannot
    pass one by accident or in a hurry. If somebody needs to add one they have
    to change this signature, which changes this test, which is the
    conversation worth having.
    """
    src = _source()
    match = re.search(r"export function recordProblem\((.*?)\)\s*:", src, re.S)
    assert match, "recordProblem is gone or has been renamed"
    params = [p.strip().split(":")[0].strip()
              for p in match.group(1).split(",") if p.strip()]
    assert params == ["method", "path", "status"], (
        f"recordProblem now takes {params}. If one of those carries a message, "
        "the log can carry user input — device names, body sites, in JIM "
        "possibly health content."
    )


def test_the_stored_record_has_no_field_that_could_hold_content():
    """What the buffer may contain, checked against the interface itself.

    `sent` joined the four originals when sending was added: it counts how much
    of `count` has already gone, so relaunching an app does not report the same
    failure again. It is a number derived from another number and has no way to
    hold anything of anybody's — but it still had to be added here on purpose,
    which is exactly what this test is for.
    """
    src = _source()
    match = re.search(r"export interface Problem \{(.*?)\n\}", src, re.S)
    assert match, "the Problem interface is gone or has been renamed"
    fields = set(re.findall(r"^\s*(\w+)\??:", match.group(1), re.M))
    assert fields == {"op", "status", "count", "day", "fingerprint", "sent"}, (
        f"Problem now has {sorted(fields)}"
    )
    leaked = sorted(f for f in fields if f in FORBIDDEN_FIELDS)
    assert not leaked, f"these fields can hold user content: {leaked}"


def test_the_report_sends_only_what_the_screen_shows():
    """The payload's keys, pinned.

    The screen renders this exact object and the sender posts it, so a key
    added here is a key that leaves the device — shown to the user, but only if
    they look. Pinning it means a new key has to be a decision.
    """
    src = _source()
    match = re.search(r"export function problemReport\(.*?\n  return \{(.*?)\n  \};",
                      src, re.S)
    assert match, "problemReport is gone or has been restructured"
    keys = set(re.findall(r"^\s*(\w+):", match.group(1), re.M))
    assert keys == {"source", "app_version", "platform", "language",
                    "problems"}, f"the report now carries {sorted(keys)}"


def _outgoing_problem_fields() -> set[str]:
    """The per-problem object `problemReport` builds, which is not the stored
    row: `sent` is this device's bookkeeping and deliberately stays home."""
    match = re.search(r"\.map\(\(r\) => \(\{(.*?)\n    \}\)\)", _source(), re.S)
    assert match, "problemReport no longer builds its problems by mapping"
    return set(re.findall(r"^\s*(\w+):", match.group(1), re.M))


def test_the_outgoing_problem_carries_only_the_five():
    """Pinned here, without the gateway.

    The cross-check against `cloudgw/problems.py` below is the stronger test,
    but it only runs in the repo that ships the gateway — and JIM and PDI are
    where a leak would cost the most. This states the five names locally so
    all three repos catch a sixth appearing, whatever it is called.
    """
    fields = _outgoing_problem_fields()
    assert fields == {"op", "status", "count", "day", "fingerprint"}, (
        f"the wire now carries {sorted(fields)}")
    leaked = sorted(f for f in fields if f in FORBIDDEN_FIELDS)
    assert not leaked, f"these fields can hold user content: {leaked}"


def test_the_wire_shape_matches_what_the_gateway_will_accept():
    """The two halves of the contract, checked against each other.

    `cloudgw/problems.py` refuses any key it does not expect, so a field added
    to the payload here and not there turns every report from the next release
    into a 422 — silently, since the sender swallows failures. Only QRME ships
    the gateway; in the other two repos there is nothing to compare against and
    this is skipped rather than faked.
    """
    gateway = REPO / "cloudgw" / "problems.py"
    if not gateway.exists():
        pytest.skip("this repo does not ship the gateway")
    src = gateway.read_text(encoding="utf-8")
    top = set(re.findall(r'"(\w+)"',
                         re.search(r"TOP_LEVEL = \{(.*?)\}", src, re.S).group(1)))
    fields = set(re.findall(
        r'"(\w+)"',
        re.search(r"PROBLEM_FIELDS = \{(.*?)\}", src, re.S).group(1)))

    ts = _source()
    sent_top = set(re.findall(
        r"^\s*(\w+):",
        re.search(r"export function problemReport\(.*?\n  return \{(.*?)\n  \};",
                  ts, re.S).group(1), re.M))
    assert sent_top == top, (
        f"the console sends {sorted(sent_top)} and the gateway accepts "
        f"{sorted(top)}; the mismatch would 422 every report")

    sent_fields = _outgoing_problem_fields()
    assert sent_fields == fields, (
        f"the console sends problems shaped {sorted(sent_fields)} and the "
        f"gateway accepts {sorted(fields)}")
    assert "sent" not in sent_fields, (
        "the watermark is this device's bookkeeping and has no business on "
        "the wire")


def test_a_build_that_forgot_to_name_itself_cannot_impersonate_a_product():
    """The fallback source, which is not a product.

    `errors.ts` is byte-identical in three repos and learns which one it is
    from a build constant. If a vite.config.ts loses that define, a fallback
    naming any real product would file this app's bugs under that one, and the
    aggregate would look fine while being wrong — the worst kind of wrong,
    because there is no symptom. A source the gateway refuses turns it into a
    422 on the first report.
    """
    src = _source()
    match = re.search(r'__APP_SOURCE__ !== "undefined" \? __APP_SOURCE__\s*'
                      r': "([^"]*)"', src)
    assert match, "the source fallback is gone or has been restructured"
    assert match.group(1) not in {"qrme", "jim-mini", "pdi"}, (
        f"the fallback names {match.group(1)!r}, a real product — a repo that "
        "forgot its define would report as that one and nothing would notice")

    gateway = REPO / "cloudgw" / "problems.py"
    if gateway.exists():
        sources = re.search(r"SOURCES = \{(.*?)\}",
                            gateway.read_text(encoding="utf-8"), re.S).group(1)
        assert f'"{match.group(1)}"' not in sources, (
            "the gateway accepts the fallback source, so a misbuilt console "
            "would be recorded rather than refused")


def test_sending_is_impossible_without_an_address_somebody_configured():
    """Off by absence, not by flag.

    A default that lives in a build constant cannot be switched on by a
    mistake in a later release the way a boolean can — there is no address for
    the mistake to reach. This checks the early return is still the first
    thing `sendProblems` does.
    """
    src = _source()
    body = re.search(r"export async function sendProblems\(.*?\n\}", src, re.S)
    assert body, "sendProblems is gone or has been renamed"
    first = [ln.strip() for ln in body.group(0).splitlines()
             if ln.strip().startswith(("if ", "return", "const"))][:3]
    assert any('return "no-collector"' in ln for ln in first), (
        f"the collector check is no longer at the top of sendProblems: {first}")
    assert 'localStorage.getItem(COLLECTOR_KEY)' in src, (
        "the collector can no longer be overridden or emptied by the person "
        "whose device it is")


def test_the_sender_does_not_report_its_own_failures():
    """No feedback loop.

    `req()` records a failure whenever it fails, so a send routed through it
    would write a new row every launch the collector was unreachable — a log
    that fills up with the story of its own delivery. The send uses raw fetch,
    and this is the test that says so.
    """
    src = _source()
    body = re.search(r"export async function sendProblems\(.*?\n\}",
                     src, re.S).group(0)
    assert "fetch(" in body, "the sender no longer posts anything"
    assert "req(" not in body and "recordProblem" not in body, (
        "the sender is recording its own failures, which makes the buffer "
        "fill with delivery attempts instead of bugs")


def test_the_client_never_hands_the_recorder_a_message():
    """The call sites, not just the signature.

    TypeScript would already reject a fourth argument; this catches the subtler
    version where somebody widens the signature and passes `detail` through in
    the same change.
    """
    calls = re.findall(r"recordProblem\(([^)]*)\)",
                       API_TS.read_text(encoding="utf-8"))
    assert calls, "api.ts no longer records failures at all"
    for args in calls:
        parts = [a.strip() for a in args.split(",")]
        assert len(parts) == 3, f"recordProblem called with {parts}"
        assert "path" in parts[1], f"second argument is not the path: {parts}"
        assert not any(w in parts[2].lower() for w in ("detail", "message",
                                                       "text", "data")), (
            f"a message is being passed as the status: {parts[2]}"
        )


def _id_patterns() -> list[re.Pattern[str]]:
    """The real patterns, read out of the module rather than restated here."""
    src = _source()
    block = re.search(r"const ID_LIKE = \[(.*?)\n\];", src, re.S)
    assert block, "ID_LIKE is gone or has been restructured"
    out = []
    for body, flags in re.findall(r"/\^(.*?)\$/([a-z]*)", block.group(1)):
        out.append(re.compile("^" + body + "$",
                              re.I if "i" in flags else 0))
    assert out, "no ID_LIKE patterns could be read"
    return out


def _redact(path: str) -> str:
    pats = _id_patterns()
    head = path.split("?")[0]
    return "/".join("{id}" if seg and any(p.match(seg) for p in pats) else seg
                    for seg in head.split("/"))


@pytest.mark.parametrize("raw,expected", [
    ("/profiles/prf_0de08e794ed0/chat", "/profiles/{id}/chat"),
    # Short ids are still ids. Requiring six hex characters let these three
    # through when the pattern was first written, which is the whole reason
    # they are fixtures.
    ("/users/usr_8752921df161/captures/cap_9f2/image",
     "/users/{id}/captures/{id}/image"),
    ("/desks/dsk_abc/guests/req_7/accept", "/desks/{id}/guests/{id}/accept"),
    ("/meds/usr_1/adherence?days=7", "/meds/{id}/adherence"),
    ("/profiles/12345/friends/67890", "/profiles/{id}/friends/{id}"),
    # A query string can name a vault key. It never survives.
    ("/bequests/grant/read?key=notes/private", "/bequests/grant/read"),
    ("/health", "/health"),
])
def test_identifying_segments_are_replaced(raw, expected):
    assert _redact(raw) == expected


def _app():
    """The product's FastAPI app, found rather than named.

    Discovered so this file stays byte-identical across the three repos instead
    of carrying a per-product import line.

    The one with the *most* routes wins, which is not arbitrary: QRME also ships
    a `cloudgw` package with its own small `api.py`, and picking alphabetically
    chose that sidecar and read ten route segments instead of four hundred. The
    check still passed the eaten-segment assertion, so the only thing that
    caught it was the floor below — a reminder that "the app built" and "the
    right app built" are different questions.
    """
    import importlib

    best, most = None, -1
    from . import clientpaths

    for child in sorted(REPO.iterdir()):
        if not ((child / "api.py").exists() and (child / "__init__.py").exists()):
            continue
        try:
            app = importlib.import_module(f"{child.name}.api").app
        except Exception:  # noqa: BLE001 - a sidecar that will not import is fine
            continue
        count = len(clientpaths.all_routes(app))
        if count > most:
            best, most = app, count
    if best is None:
        raise RuntimeError("no importable {pkg}/api.py beside pyproject.toml")
    return best


def test_no_real_route_segment_is_mistaken_for_an_id():
    """The other direction, and the reason the pattern can be as wide as it is.

    Redacting aggressively only stays sensible while it does not eat the route
    names themselves — a report of `POST /{id}/{id}` would be private *and*
    useless. Every literal segment this product actually serves is checked, so
    the width of the pattern is measured against reality rather than guessed.

    The segments come from the live route table rather than from
    `doorless_routes.txt`, and that matters: the snapshot shrinks every time a
    door is built, so a check reading it would weaken as the backlog cleared and
    go vacuous the day it emptied. A test that gets less thorough as the project
    improves is worse than no test, because nothing announces the moment it
    stopped meaning anything.
    """
    from . import clientpaths

    segments = set()
    for route in clientpaths.all_routes(_app()):
        for seg in route.path.split("/"):
            if seg and not seg.startswith("{"):
                segments.add(seg)
    assert len(segments) > 30, (
        f"only {len(segments)} route segments read — the app did not build")
    eaten = sorted(s for s in segments if _redact("/" + s) == "/{id}")
    assert not eaten, (
        f"these are route names, not ids, and the redaction ate them: {eaten}"
    )
