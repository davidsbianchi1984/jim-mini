"""Every route the backend serves is reachable from a client — or is on the list.

The inverse of the route guard. That one asks whether every call reaches a
route; this asks whether every route is reachable from a door a user can open.

It is the quieter of the two failures. A client asking for a route that does not
exist produces a 404 somebody eventually reports. A route no client asks for
produces nothing at all: the code is present, its tests pass, the changelog says
it shipped — and the capability is simply unreachable.

JIM has a long backlog of these, so the current state is recorded in
`doorless_routes.txt` rather than asserted to be empty. The list is a backlog,
not an approval. Two things follow from that, and both are the point:

* **It cannot grow.** A new route with no door fails this test, so the gap stops
  widening on the day it is noticed rather than the day someone goes looking.
* **It must shrink deliberately.** Building a door makes the test fail too,
  telling you to strike the line. A backlog that quietly re-fills is how the
  first five came to be there.

Browser-facing paths — a QR image used as an `<img src>`, a landing page reached
by scanning — are excluded in `clientpaths.NOT_A_CLIENT_CALL`, not listed here.
"""

from __future__ import annotations

from pathlib import Path

from jim.api import app

from . import clientpaths, ratchets

SNAPSHOT = Path(__file__).resolve().parent / "doorless_routes.txt"


def _recorded() -> list[str]:
    return [line.strip() for line in
            SNAPSHOT.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_the_doorless_backlog_matches_the_record():
    """Both directions, because both are news.

    A route that has gained a door is as much a change to report as one that has
    lost it — and if only growth were checked, the file would drift into a list
    of things that were true once.
    """
    actual = clientpaths.doorless(app)
    recorded = _recorded()

    appeared = sorted(set(actual) - set(recorded))
    resolved = sorted(set(recorded) - set(actual))

    problems = []
    if appeared:
        problems.append(
            f"{len(appeared)} route(s) added with no client door:\n    "
            + "\n    ".join(appeared)
            + "\n  (give it a door, or record it here with the reason)")
    if resolved:
        problems.append(
            f"{len(resolved)} route(s) now have a door — strike them from "
            f"{SNAPSHOT.name}:\n    " + "\n    ".join(resolved))
    assert not problems, "\n\n".join(problems)


def test_the_audit_is_actually_looking_at_something():
    """A guard on the guard.

    An empty route table would make the comparison meaningless, and so would a
    client whose calls stopped being extracted.

    It counts through `all_routes`, not `app.routes`, and the difference is the
    reason this test exists. FastAPI hides routes inside `_IncludedRouter`
    wrappers that carry no `path` of their own, so the flat list showed 8 of
    QRME's 409. The first version of this audit reported zero doorless routes on
    that basis and passed — which is exactly the vacuous green a guard on the
    guard is for.

    The snapshot used to be asserted non-empty for the same reason. It is empty
    now, on purpose, so the liveness check moved to where the meaning actually
    lives: **the console must still be producing calls.** If the extractor
    broke, `calls()` would collapse and every route would read as doorless —
    loudly, in the test above. If instead it were quietly narrowed to a handful
    of forms, the count here is what would notice.

    Asserting the snapshot non-empty was the same shape of mistake as the
    union guard next door: a check that could only be satisfied by the
    problem still existing. It passed for as long as the backlog did.
    """
    routed = clientpaths.all_routes(app)
    assert len(routed) >= ratchets.floor("route.table"), (
        f"only {len(routed)} routes found — the app did not build properly")
    made = clientpaths.calls(clientpaths.CONSOLE)
    assert len(made) >= ratchets.floor("route.calls.console"), (
        f"only {len(made)} console call sites extracted — the audit is "
        "reading almost nothing, so an empty backlog means nothing either")


def test_the_backlog_is_empty():
    """It reached zero, and that is a thing worth failing over.

    Separate from the record comparison above so the message is plain when it
    goes. That one says *strike this line*; this one says *the number is no
    longer zero*, which is the sentence somebody adding a route wants to read.
    """
    assert clientpaths.doorless(app) == [], (
        "the doorless backlog is no longer empty:\n    "
        + "\n    ".join(clientpaths.doorless(app)))
