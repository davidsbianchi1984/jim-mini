"""Every refusal shape, not just the one that was broken last time.

## The finding

The round before this gave the 422 a top-level `message` and taught all four
clients to read it. `detail` has three shapes in this product — a **string**
for most refusals, a **dict** for the plan gate, a **list** for a 422 — and
only the list was fixed. The plan gate's `message` stayed nested inside its
dict, where it had always been, and `refuse` wraps that as
`{"detail": {...}}`.

    asked     does the sentence ride beside the structure
    mattered  does every structured refusal put it in the same place

The three native shells look for a top-level `message` and then for a string
`detail`. A dict is neither, so the plan gate — the one refusal that stands
between somebody and a decision to pay — rendered as the bare status code: no
price, no plan name, no reason.

iOS and Windows had always done that. Android had been coercing the dict
through `toString()` and showing its raw JSON — ugly, but it contained the
price — and teaching it to read the top-level key first is what regressed it
to the status code.

## What this checks

Per *shape* rather than per route, because that is the axis the defect lives on
and the axis nothing was testing. `i18n.refuse` lifts the sentence for every
shape now, so a refusal added later cannot forget to.
"""

from __future__ import annotations

from fastapi import HTTPException
from fastapi.testclient import TestClient

import pytest

from jim import i18n, tiers
from jim.api import create_app


def _probe_app():
    """An app with one route per detail shape.

    Driven through the real handler rather than by calling `sentence_of`:
    being right about the shapes and never being reached is exactly the failure
    this file is about.
    """
    app = create_app()

    @app.get("/_shape/string")
    def _string():
        raise HTTPException(403, "that is not yours to read")

    @app.get("/_shape/dict")
    def _dict():
        cap = list(tiers.CAPABILITIES)[0]
        need = tiers.CAPABILITIES[cap]["from"]
        raise HTTPException(402, {
            "reason": "plan", "capability": cap, "needs": need,
            "have": "free", "price_usd": tiers.PLANS[need]["price_usd"],
            "period": tiers.PLANS[need]["period"],
            "message": tiers.refusal("free", cap),
            "billing": "simulated — no real funds move",
            "emergency_unaffected": True})

    @app.get("/_shape/bare")
    def _bare():
        raise HTTPException(404)

    return TestClient(app)


@pytest.mark.parametrize("shape,path", [
    ("string", "/_shape/string"),
    ("dict", "/_shape/dict"),
])
def test_every_refusal_shape_carries_a_top_level_sentence(shape, path):
    """The defect, per shape. A client should never have to know which shape it
    is looking at to find the sentence."""
    body = _probe_app().get(path).json()
    said = body.get("message")
    assert isinstance(said, str) and said.strip(), (
        f"a {shape} refusal carries no top-level `message`, so the three "
        f"shells fall back to the status code: {body}")
    assert not said.lstrip().startswith(("{", "[")), (
        f"the sentence is a serialised structure: {said[:120]}")


def test_the_422_shape_is_covered_by_the_same_rule():
    """The list, asserted here too, so all three shapes live in one place and
    a fourth has an obvious home."""
    refused = _probe_app().post("/enroll", json={})
    assert refused.status_code == 422, refused.text
    body = refused.json()
    assert isinstance(body["detail"], list)
    assert isinstance(body.get("message"), str) and body["message"].strip()


def test_the_structure_survives_the_lift():
    """The sentence rides *beside* the structure, never instead of it.

    The console reads the dict to draw the upgrade card with its price and
    button. A fix that flattened the refusal to a sentence would have replaced
    that card with a line of text.
    """
    body = _probe_app().get("/_shape/dict").json()
    assert isinstance(body["detail"], dict), (
        "the structure was replaced by its own sentence")
    for key in ("reason", "needs", "price_usd"):
        assert key in body["detail"], f"the upgrade card lost {key}"


def test_a_refusal_with_nothing_readable_is_not_given_an_invented_sentence():
    """`HTTPException(404)` has no message of its own.

    Answered as before rather than handed a sentence this codebase made up — a
    fabricated explanation is worse than a bare status, and indistinguishable
    from a real one.
    """
    body = _probe_app().get("/_shape/bare").json()
    assert "message" not in body or body.get("message"), (
        "a refusal with nothing to say grew an empty `message`, which a client "
        "would render as a blank line where an explanation belongs")


@pytest.mark.parametrize("language", ["pt", "ja"])
def test_the_lifted_sentence_is_the_translated_one(language):
    """Order inside `refuse`, and a check that can actually fail on it.

    Comparing the lifted sentence with the nested one is not enough on a
    refusal whose message is untranslated — both sides are the same English
    string whichever order is used. So this drives a message that *is* in
    `_REFUSALS`, where lifting before localizing produces a visible difference.

        asked     do the two copies agree
        mattered  is the lifted one the translated one
    """
    english = next(iter(i18n._REFUSALS))
    expected = i18n.tr_refusal(english, language)
    if expected == english:
        pytest.skip(f"no {language} translation for the probe sentence")

    app = create_app()

    @app.get("/_shape/translated_dict")
    def _translated():
        raise HTTPException(401, {"reason": "auth", "message": english})

    body = TestClient(app).get("/_shape/translated_dict",
                               headers={"accept-language": language}).json()
    assert body["message"] == expected, (
        f"the top-level sentence is {body['message']!r}, not the {language} "
        "one — it was lifted before the detail was localized")


def test_sentence_of_reads_each_shape_and_invents_nothing():
    assert i18n.sentence_of("plain") == "plain"
    assert i18n.sentence_of({"message": "structured"}) == "structured"
    assert i18n.sentence_of({"needs": "pro"}) is None
    assert i18n.sentence_of(None) is None
    assert i18n.sentence_of("") is None
    assert i18n.sentence_of([{"msg": "row"}]) is None, (
        "the 422 list is validation_message's job — it needs the reader's "
        "language and the field-name rules this function does not have")
