"""A specialist could be reached by a sensor and not by a person.

## The finding

`grep -c specialist jim/coach.py` returned **0**.

A QRME specialist was reachable from exactly one place in this product:
`guardian._deliver`, the monitoring path. Sensors trip, a `Detection` names a
condition, `_specialist(condition)` looks one up, and if it is a tandem
specialist the Guardian delegates the guidance to it.

`coach.reply` is where somebody brings something in their own words, because
they chose to. It had no call, no mention and no comment about specialists at
all.

    asked     can a specialist be reached
    mattered  can the person who asks reach one

The person whose watch noticed something got the better answer. The person who
sat down and typed *"I've been struggling with money and it's keeping me up"*
got the local model — on a product whose premise is that somebody is looking
after you, and where bringing a problem yourself is the strongest signal there
is.

## Why nothing bridged them

Two vocabularies that never met. `specialists` is keyed on **condition**,
because its only caller was a detection. `coach.AREAS` is seven **life areas**,
because its only caller was a person choosing a tab. Nothing mapped one to the
other, so even a coach that wanted a specialist could not have named one.

`specialists.AREA_CONDITIONS` is that map, declared rather than matched — a
substring rule would have paired *finance* with *financial stress* and left
*nutrition* silently unpaired while looking like it had worked.

## Why the fix offers instead of routing

The material is different in kind from what the monitoring path sends. A
detection sends a **finding** — "the user shows signs of low mood (resting
heart rate elevated for 40 minutes)". A coach turn would send **what the
person wrote about their own life**.

Routing that automatically would disclose to a profile outside JIM something
somebody said to their Guardian, without asking. So `coach.reply` returns an
offer that says plainly nothing has been sent, and the sending lives behind a
route the person chose. `handoff.py` set the same rule for the other
multi-step path:

    A detection can *warrant* a handoff; a person or an operator starts it.

## What this file checks

The asymmetry structurally, so it cannot come back; the offer's honesty, since
a surface naming a third party without saying whether it has been spoken to
has answered the wrong question; and every refusal path, because somebody who
asked a question must never end up with nothing.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

from jim import coach, conditions, db, specialists

from .conftest import enroll


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


PACKAGE = _repo_root() / "jim"


# --- the asymmetry, structurally ------------------------------------------

def _reaches_a_specialist(module: str, function: str) -> bool:
    """Does *this function* contain a call that resolves a specialist?

    Scoped to one function, not the module. The first version of this asked
    the module, and passed on an injected regression: deleting the offer from
    `coach.reply` left `coach.ask_specialist` in the same file still calling
    `specialists.for_area`, so the module could reach one and the person
    reading a reply could not discover that.

        asked     can this module reach a specialist
        mattered  can the surface a person is looking at reach one

    That is the same shape as every other miss in this audit, committed once
    more inside the guard written for it.

    By `ast` and by *call* rather than by mention: a sibling guard here was
    once satisfied by a comment containing the name it was looking for.
    """
    tree = ast.parse((PACKAGE / f"{module}.py").read_text(encoding="utf-8"))
    target = next((n for n in ast.walk(tree)
                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                   and n.name == function), None)
    if target is None:
        return False
    for node in ast.walk(target):
        if not isinstance(node, ast.Call):
            continue
        fn = node.func
        name = getattr(fn, "attr", None) or getattr(fn, "id", None)
        base = getattr(getattr(fn, "value", None), "id", "")
        if base == "specialists" and name in ("for_area", "offer"):
            return True
        if name == "_specialist":
            return True
    return False


def test_the_reply_a_person_reads_can_name_a_specialist():
    """The defect, directly. `guardian._deliver` could; `coach.reply` could
    not — and a capability nobody can discover is one nobody has."""
    assert _reaches_a_specialist("coach", "reply"), (
        "coach.reply cannot resolve a specialist, so a person reading an "
        "answer has no way to learn one covers this area. A sensor reading "
        "reaches a QRME specialist through guardian._deliver — the strongest "
        "signal in the product on the weakest path.")


def test_and_asking_actually_sends_to_one():
    """The other half. An offer that leads nowhere is worse than no offer."""
    assert _reaches_a_specialist("coach", "ask_specialist"), (
        "coach.ask_specialist does not resolve a specialist — the door the "
        "offer points at opens onto nothing")


def test_the_monitoring_path_still_can_too():
    """A guard on the guard, and on the fix: closing the asymmetry by taking
    the specialist away from the detections would satisfy the tests above and
    be a straight regression."""
    assert _reaches_a_specialist("guardian", "_deliver"), (
        "guardian._deliver no longer resolves a specialist — the monitoring "
        "path has lost the tandem it always had")


def test_the_area_map_is_declared_for_every_area():
    """A new life area that nobody has decided about would silently get no
    specialist and look exactly like an area that correctly has none."""
    missing = sorted(set(coach.AREAS) - set(specialists.AREA_CONDITIONS))
    assert not missing, (
        f"{missing} are coach areas with no entry in AREA_CONDITIONS. An "
        "empty tuple is a decision; an absent key is an oversight, and they "
        "behave identically at runtime — which is why this asks.")
    stale = sorted(set(specialists.AREA_CONDITIONS) - set(coach.AREAS))
    assert not stale, (
        f"{stale} are mapped and are not coach areas any more")


def test_every_mapped_condition_exists():
    """A typo'd condition key maps an area to a specialist that can never be
    found, and the failure looks exactly like nobody having registered one."""
    known = set(conditions.LABELS)
    bad = sorted({c for domains in specialists.AREA_CONDITIONS.values()
                  for c in domains if c not in known})
    assert not bad, (
        f"{bad} are not condition domains this product defines, so the areas "
        "mapping to them can never resolve a specialist")


# --- driven ----------------------------------------------------------------
#
# Through `make_tandem`, which wires a FakeQRME behind the *real* QRMEClient.
# Setting `app.state.qrme` to the fake directly would test against a stand-in
# for the HTTP boundary while the code under test calls the client's method
# surface — a wiring test that bypasses the wiring.

def _register_specialist(condition=None):
    db.connect().execute(
        "INSERT INTO specialists (condition, mode, label, qrme_profile_id,"
        " created_at) VALUES (?,?,?,?,?)",
        (condition or conditions.ANXIETY, "tandem", "Dr Reyes, anxiety",
         "prf_specialist", db.utcnow()))
    db.connect().commit()


def test_the_coach_offers_a_specialist_and_has_not_sent_anything(make_tandem):
    c = make_tandem()
    uid = enroll(c)
    _register_specialist()
    r = c.post(f"/coach/{uid}",
               json={"area": "mental_health", "message": "I feel awful."})
    assert r.status_code < 300, r.text
    offer = r.json()["specialist_offer"]
    assert offer and offer["available"] is True
    assert offer["sent"] is False, (
        "the coach reply says a specialist has been sent to; it must only "
        "offer, because the thing that would cross is what the person wrote")
    assert "Nothing has been sent" in offer["note"]


def test_an_area_with_no_specialist_offers_nothing(make_tandem):
    """Not an error and not a silence: nutrition maps to no clinical domain on
    purpose, and the coach answering alone is the correct behaviour."""
    c = make_tandem()
    uid = enroll(c)
    _register_specialist()
    r = c.post(f"/coach/{uid}",
               json={"area": "nutrition", "message": "What should I eat?"})
    assert r.status_code < 300
    assert r.json()["specialist_offer"] is None


def test_asking_reaches_the_specialist_and_says_where_the_answer_came_from(
        make_tandem):
    c = make_tandem()
    uid = enroll(c)
    _register_specialist()
    r = c.post(f"/coach/{uid}/specialist",
               json={"area": "mental_health",
                     "message": "Money is keeping me up at night."})
    assert r.status_code < 300, r.text
    body = r.json()
    assert body["delivered"] is True, body
    assert body["content"]
    assert body["specialist_who"]["qrme_profile_id"] == "prf_specialist"
    assert "not by JIM's own model" in body["provenance"]["method"], (
        "the answer does not say it came from outside JIM — a reply that "
        "reads as the Guardian's own when a third party wrote it is the one "
        "thing this path must never do")
    assert "nothing else from your record" in body["provenance"]["shared"]


def test_the_exchange_lands_in_the_same_thread_as_the_rest(make_tandem):
    """A conversation split across two stores is one somebody has to
    reassemble to understand what they were told."""
    c = make_tandem()
    uid = enroll(c)
    _register_specialist()
    c.post(f"/coach/{uid}/specialist",
           json={"area": "mental_health", "message": "Hello there."})
    history = c.get(f"/coach/{uid}?area=mental_health").json()
    assert any(m["content"] == "Hello there." for m in history), (
        "the question the person asked is not in the coach thread")


def test_a_held_reply_is_reported_as_held_rather_than_as_nothing(make_tandem):
    """QRME's moderation can hold a reply for its owner's approval. Reporting
    that as no answer would misdescribe a message that exists and is waiting."""
    c = make_tandem(hold=True)
    uid = enroll(c)
    _register_specialist()
    body = c.post(f"/coach/{uid}/specialist",
                  json={"area": "mental_health", "message": "Hi."}).json()
    assert body["delivered"] is False
    assert body["held_for_owner_approval"] is True


def test_an_area_with_no_specialist_refuses_and_says_so(make_tandem):
    """Somebody who asked a question never ends up with nothing: the refusal
    names its cause and what was used instead."""
    c = make_tandem()
    uid = enroll(c)
    _register_specialist()
    body = c.post(f"/coach/{uid}/specialist",
                  json={"area": "nutrition", "message": "Hello."}).json()
    assert body["delivered"] is False
    assert "no specialist covers this area" in body["reason"]
    assert "Guardian answers this one alone" in body["note"]


def test_an_unknown_area_is_refused_at_the_function_too(make_tandem):
    """The route's own `LifeArea` enum rejects an unknown area with a 422
    before this is reached, which is the right place for it.

    The check inside `ask_specialist` is still tested, directly, because the
    function is importable and a later caller may not come through that route
    — and a specialist resolved for an area that does not exist would be a
    specialist chosen by a typo.
    """
    c = make_tandem()
    uid = enroll(c)
    assert c.post(f"/coach/{uid}/specialist",
                  json={"area": "not_an_area", "message": "Hi."}
                  ).status_code == 422
    out = coach.ask_specialist(uid, "not_an_area", "Hi.", object())
    assert out["delivered"] is False and "unknown area" in out["reason"]


def test_no_tandem_configured_is_a_refusal_and_not_a_crash(client):
    """The standalone app — no QRME wired at all, which is the default
    deployment."""
    uid = enroll(client)
    _register_specialist()
    body = client.post(f"/coach/{uid}/specialist",
                       json={"area": "mental_health", "message": "Hi."}).json()
    assert body["delivered"] is False
    assert "no QRME tandem" in body["reason"]
    assert "Guardian answers this one alone" in body["note"]


def test_the_specialist_is_never_reachable_from_the_escalation_ladder():
    """`handoff.py` states the rule and it holds here for the same reason: an
    escalation that waits on a third party is worse than no escalation.

    Structural, per module, and it is the check that would have caught the
    tempting version of this feature — the one where a coach turn about a
    hard week quietly becomes a tandem call on the emergency path.
    """
    for module in ("escalation", "crashwatch", "relay"):
        path = PACKAGE / f"{module}.py"
        if not path.exists():
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            name = getattr(node.func, "attr", None)
            if name == "ask_specialist":
                pytest.fail(
                    f"{module}.py calls coach.ask_specialist — the emergency "
                    "path must decide in one call and never wait on a "
                    "third-party profile")


def test_the_offer_does_not_leak_what_the_person_wrote():
    """The offer is computed from the area alone. If it ever grew a summary of
    the message it would be a disclosure inside the thing whose whole job is
    to say nothing has been disclosed yet."""
    source = (PACKAGE / "specialists.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in ("offer", "for_area"):
            args = [a.arg for a in node.args.args]
            assert args == ["area"], (
                f"specialists.{node.name} now takes {args}; it may only see "
                "the area, so that it cannot carry what the person wrote")
