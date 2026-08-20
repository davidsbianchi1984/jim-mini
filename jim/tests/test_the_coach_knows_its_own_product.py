"""The coach knows its own product.

A field report: asked to "plant a quarter-hour lookout", the coach gave
a graceful shrug. The earlier honesty line fixed "what can you do" — the
engaged-session sentence — but the prompt still carried no map of JIM's
own doors, so the model answered door-shaped requests from what
assistants generally cannot do, with the Watched pages card two scrolls
below the conversation.

    asked     can the coach do this
    mattered  can the product, and where

The map is a deterministic block in the coach context: the doors, named,
each with the screen it lives on, and the instruction to route by name
rather than decline. Short on purpose — a prompt full of manual stops
noticing the person in front of it.
"""

from __future__ import annotations

from jim import coach, llm

from jim.tests.conftest import enroll


def test_the_map_names_the_doors_and_their_screens():
    """The five doors the round was about, each with a real place — the
    exact card names the console renders, so 'that's the Watched pages
    card, below this chat' is a sentence the coach can say truthfully."""
    for door, place in [("lookout", "Watched pages card"),
                        ("check-in", "Check-in screen"),
                        ("weekly letter", "Journal screen"),
                        ("permit", "chip rail"),
                        ("escalation ladder", "Safety screen")]:
        assert door in coach._FEATURE_MAP, door
        assert place in coach._FEATURE_MAP, place
    # The lookout line carries the real interval, so the coach quotes the
    # product's own refusal bounds rather than inventing some.
    assert "quarter-hour and a month" in coach._FEATURE_MAP


def test_the_map_rides_every_coach_turn(client, monkeypatch):
    uid = enroll(client)
    seen: dict = {}

    def capture(user_id, system, message, cloud=None):
        seen["system"] = system
        return {"text": "ok", "provider": "anthropic", "degraded": False,
                "reason": None, "grounded": False, "drew_on": []}

    monkeypatch.setattr(llm, "generate_for_user", capture)
    r = client.post(f"/coach/{uid}", json={
        "area": "personal_growth",
        "message": "can you keep an eye on a page for me?"})
    assert r.status_code == 200, r.text
    assert "Watched pages card" in seen["system"]
    assert "point at it by name instead of declining" in seen["system"]


def test_the_map_is_context_not_instruction_about_safety():
    """The safety line routes to the screen and still puts immediate help
    first — the map must never soften the danger rule above it."""
    assert "urge immediate help first" in coach._FEATURE_MAP
