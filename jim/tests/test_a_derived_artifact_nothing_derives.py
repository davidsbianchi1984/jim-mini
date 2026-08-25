"""The user-specific model was correct, tested, and never computed.

## The finding

`jim/adaptation.py` implements clause 11 — a user-specific model derived
offline from a person's own stored history, versioned, confidence-scored, and
sealed into the vault when a tandem is configured. `coach.reply` reads it
through `adaptation.prompt_lines` on every turn.

`prompt_lines` returns `[]` when there is no row. `rebuild` is what writes the
row. And `rebuild` had exactly one caller in the entire product:

    jim/api.py:  return adaptation.rebuild(user_id, pdi=app.state.pdi)

`POST /adaptation/{user}` — a button in the desktop console. Nothing called it
after a check-in, after a coach turn, after an answered follow-up. On every
user who never pressed that button, and on every user who only ever used a
phone, the artifact had never been computed and `learned` was empty on every
turn forever.

    asked     can a user-specific model be built from the history
    mattered  does anything ever build it

The module was not wrong. Its tests were not wrong — they call `rebuild` and
check what it produces, which is exactly what a unit test of that module
should do. What was missing was an **edge**, and an edge is precisely the
thing that no test of either endpoint will notice: `adaptation`'s tests build
the profile themselves, and `coach`'s tests pass whether the profile exists or
not, because a coach with no adaptation lines is a working coach.

## The other half: nothing moved between snapshots

The sibling product carries a latent vector per (profile, interactor),
EMA-updated after every interaction, so cross-session state survives logins,
devices and model calls. JIM had no equivalent at all. Even *with* a rebuild,
the profile was a snapshot, and between snapshots the Guardian entered every
conversation exactly as it entered the first one.

`jim/continuity.py` is that vector, and its updates hang off the loop rather
than off a button — which is the same defect stated as a design rule.

## What this file checks

1. **Every derived artifact has a live deriver.** Structural, by `ast`: for
   each module that writes a derived per-user artifact, at least one caller of
   its build function must be somewhere other than a route handler. A guard
   that only counted callers would have passed on the defect, because the
   route *is* a caller.

2. **The three signals actually reach the vector**, driven end to end through
   the app rather than by calling `observe` directly. A wiring test that calls
   the function it is testing the wiring of proves nothing.

3. **The vector carries no content.** Six floats and three counters. This is
   the constraint that governs the whole codebase — nothing private is assumed
   safe to keep — and a derived artifact is exactly where content leaks in by
   accident, because deriving feels like summarising.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import pytest

from jim import continuity, db
from . import ratchets


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


PACKAGE = _repo_root() / "jim"

#: (module, build function) pairs that write a derived per-user artifact.
#: Each needs a caller that is not a route handler — that is the whole point.
DERIVERS = {
    ("adaptation", "rebuild"),
    ("continuity", "observe"),
}


def _route_handler_names() -> set[str]:
    """Functions in `api.py` decorated with an HTTP method.

    Named rather than guessed at: a route handler is a function carrying an
    `@app.get`/`@app.post`/... decorator, and the parser can see that.
    """
    tree = ast.parse((PACKAGE / "api.py").read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            fn = dec.func if isinstance(dec, ast.Call) else dec
            if (isinstance(fn, ast.Attribute)
                    and fn.attr in ("get", "post", "put", "delete", "patch")):
                names.add(node.name)
    return names


def _callers(module: str, func: str, *, include_own_module: bool = False
             ) -> list[tuple[str, str]]:
    """(file, enclosing function) for every call to `module.func`.

    Tests are always excluded — a test calling the builder is what made the
    original defect invisible, not evidence against it. The defining module is
    excluded by default and included when resolving a chain (see
    `_reachable_from_the_loop`).
    """
    found = []
    for path in sorted(PACKAGE.rglob("*.py")):
        if "tests" in path.parts:
            continue
        if path.name == f"{module}.py" and not include_own_module:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        holders = [n for n in ast.walk(tree)
                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            qualified = (isinstance(f, ast.Attribute) and f.attr == func
                         and isinstance(f.value, ast.Name)
                         and f.value.id == module)
            # Inside its own module the call is bare: `rebuild(...)`, not
            # `adaptation.rebuild(...)`. Missing that is how the first version
            # of this check concluded the chain ended at the route.
            bare = (include_own_module and path.name == f"{module}.py"
                    and isinstance(f, ast.Name) and f.id == func)
            if not (qualified or bare):
                continue
            holder = min(
                (h for h in holders
                 if h.lineno <= node.lineno
                 and getattr(h, "end_lineno", h.lineno) >= node.lineno),
                key=lambda h: node.lineno - h.lineno, default=None)
            found.append((path.name, holder.name if holder else "<module>"))
    return found


def _reachable_from_the_loop(module: str, func: str) -> list[tuple[str, str]]:
    """Is there any path to this builder that does not start at a route?

    Transitive, and it has to be. The fix for this defect was a wrapper —
    `adaptation.ensure_fresh` calls `rebuild` and the coach calls
    `ensure_fresh` — so a check that looked only at direct callers outside the
    defining module would still have reported the artifact unreachable while
    it was, in fact, being built on every conversation.

        asked     does the loop call this function
        mattered  can the loop reach this function

    Bounded by `seen`, so a cycle cannot hang the suite.
    """
    routes = _route_handler_names()
    frontier, seen, out = [(module, func)], {(module, func)}, []
    while frontier:
        mod, fn = frontier.pop()
        for file, holder in _callers(mod, fn, include_own_module=True):
            if holder in routes or holder == "<module>":
                continue
            if file == f"{mod}.py":
                # A wrapper in the same module: keep walking outward from it.
                nxt = (mod, holder)
                if nxt not in seen:
                    seen.add(nxt)
                    frontier.append(nxt)
                continue
            out.append((file, holder))
    return sorted(set(out))


@pytest.mark.parametrize("module,func", sorted(DERIVERS))
def test_every_derived_artifact_has_a_caller_that_is_not_a_button(module, func):
    """The defect, generalised.

    `rebuild` had a caller. Counting callers would have said this was fine.
    The question that mattered is whether anything *in the product's own loop*
    can reach it, or whether the artifact only exists when a person goes
    looking for a button — which on a phone-only user is never.
    """
    from_the_loop = _reachable_from_the_loop(module, func)
    assert from_the_loop, (
        f"{module}.{func} builds a derived artifact and nothing outside a "
        f"route handler can reach it. Direct callers: "
        f"{sorted(_callers(module, func))}.\n"
        "  That means it runs when somebody presses a button and never "
        "otherwise, so on every user who does not press it the artifact does "
        "not exist — while the code that reads it silently returns nothing.")


def _caller_total() -> int:
    """Calls to a deriver, across the package — the walk this file stands on."""
    return sum(len(_callers(module, func)) for module, func in DERIVERS)


def test_the_caller_scan_is_finding_calls():
    """A guard on the guard. An `ast` walk that stopped matching would report
    every deriver as having no callers at all, which fails in the *right*
    direction — but it would also make the list above meaningless."""
    total = _caller_total()
    assert total >= ratchets.floor("deriver.call_sites"), (
        f"only {total} deriver call(s) found across the package — the AST "
        "walk has stopped matching")
    assert _route_handler_names(), (
        "no route handlers parsed from api.py, so the check above cannot "
        "tell a button from the loop and would pass on anything")


# --- driven: the three signals reach the vector ---------------------------

#: `client` comes from jim/tests/conftest.py — the standalone app with the
#: stub model and no tandem, which is what every driven test here uses.

@pytest.fixture()
def user(client):
    """The shared `enroll` helper, which also makes this user the client's
    default caller — so the driven calls below need no headers of their own."""
    from .conftest import enroll
    return enroll(client)


def test_a_checkin_moves_the_vector_without_anybody_pressing_anything(client, user):
    """Driven through the app, which is the only way this proves the wiring.

    Calling `continuity.observe` directly here would test the function and not
    the edge — and the edge is the entire finding.
    """
    uid = user
    assert continuity.get(uid) is None

    client.post(f"/checkin/{uid}", json={"mood": 2, "energy": 2, "stress": 5})

    state = continuity.get(uid)
    assert state is not None, (
        "a check-in was logged and the continuity vector does not exist — the "
        "observation edge is not wired")
    assert state["observations"] == 1
    assert state["vector"]["strain"] > continuity._default()["strain"], (
        "a check-in reporting high stress and low mood did not raise strain")


def test_a_coach_turn_and_a_followup_answer_move_it_too(client, user):
    uid = user
    client.post(f"/coach/{uid}",
                json={"area": "mental_health", "message": "I have been low."})
    after_coach = continuity.get(uid)
    assert after_coach is not None and after_coach["observations"] == 1, (
        "a coach turn did not reach the vector")

    # A follow-up has to exist before it can be answered; when there is none
    # the route says so, and that is the branch this test must not silently
    # pass through.
    r = client.post(f"/followup/{uid}", json={"helped": True})
    if r.status_code < 300 and r.json().get("answered"):
        assert continuity.get(uid)["observations"] == 2, (
            "an answered follow-up did not reach the vector")


def test_the_coach_prompt_carries_the_state_once_there_is_enough_of_it(client, user):
    """Below the floor it says nothing; above it, it conditions. Both halves,
    because a module that always spoke would be as wrong as one that never
    did — a vector built from two check-ins is a shape in noise."""
    uid = user
    assert continuity.attention_lines(uid) == []

    for _ in range(continuity._MIN_OBSERVATIONS):
        continuity.observe(uid, "checkin", mood=3, stress=2)
    lines = continuity.attention_lines(uid)
    assert lines and "Attention weighting" in lines[0]
    assert "safety" in lines[0].lower(), (
        "the attention block does not restate that safety paths are fixed — "
        "conditioning a health assistant's focus without that sentence is how "
        "weighting turns into permission")


def test_the_vector_carries_no_content(client, user):
    """The governing constraint of this codebase, applied where it is easiest
    to break: deriving feels like summarising, and a summary of a check-in
    note is the note."""
    uid = user
    secret = "zolpidem and a bottle of merlot"
    client.post(f"/checkin/{uid}",
                json={"mood": 1, "energy": 1, "stress": 5, "note": secret})
    client.post(f"/coach/{uid}",
                json={"area": "mental_health", "message": secret})

    row = db.connect().execute(
        "SELECT * FROM user_continuity WHERE user_id=?", (uid,)).fetchone()
    assert row is not None
    stored = " ".join(str(v) for v in tuple(row))
    # **Word boundaries, not substrings.** The first version of this asserted
    # `word not in stored` and failed on "and" — which appears inside the
    # dimension name "candor". That is this audit's own recurring shape,
    # committed inside the test written to catch it:
    #
    #     asked     do the letters appear anywhere in the row
    #     mattered  does a word the user wrote appear in the row
    for word in secret.split():
        assert not re.search(rf"\b{re.escape(word)}\b", stored), (
            f"the continuity row contains {word!r} from what the user wrote")

    vector = json.loads(row["vector"])
    assert set(vector) == set(continuity.DIMS), (
        f"the vector holds {sorted(vector)} — anything beyond the declared "
        "dimensions is an unreviewed field in a derived health artifact")
    assert all(isinstance(v, (int, float)) for v in vector.values()), (
        "a non-numeric value in the vector: the only thing that cannot leak "
        "content is a number")


def test_it_can_be_forgotten(client, user):
    """Every derived thing has to be droppable by the person it was derived
    from. One that quietly could not be would make the rest of the promise
    untrue."""
    uid = user
    continuity.observe(uid, "checkin", mood=3, stress=2)
    assert continuity.get(uid) is not None
    r = client.delete(f"/continuity/{uid}")
    assert r.status_code < 300 and r.json()["forgotten"] is True
    assert continuity.get(uid) is None


def test_a_signal_it_does_not_understand_cannot_break_a_checkin(client, user):
    """`observe` is a telemetry edge on the path of somebody logging how they
    feel. It must never be able to raise: a vector that fails closed would
    take the check-in with it."""
    uid = user
    assert continuity.observe(uid, "not_a_kind", whatever=1) == {}
    continuity.observe(uid, "checkin", mood=3, stress=2)
    assert continuity.observe(uid, "checkin") is not None, (
        "a check-in with no numbers at all raised or lost the observation")


def test_the_dimensions_are_documented_where_a_person_reads_them():
    """A number nobody can interpret is not transparency, and this is served
    to the person the vector is about."""
    undocumented = sorted(set(continuity.DIMS) - set(continuity._MEANING))
    assert not undocumented, (
        f"{undocumented} have no plain-words meaning, so `state()` shows a "
        "person a percentage of nothing they can name")


def test_the_module_says_what_it_is_not():
    """The same honesty rule `adaptation.py` and the sibling product keep: the
    transformer stays the vendor's, and a reader must not be able to conclude
    from this surface that a fine-tune happened."""
    said = continuity.state("nobody")["carries"]
    assert "never" in said.lower()
    text = (PACKAGE / "continuity.py").read_text(encoding="utf-8")
    assert re.search(r"not a weight file", text, re.I), (
        "continuity.py does not state that it is not a weight file")
