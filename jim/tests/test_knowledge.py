"""The offline knowledge pack: the floor under the coach when no model key
is configured — curated, referenced, transparent about being itself, and
silent rather than wrong-topic.
"""

from jim import knowledge
from jim.tests import ratchets
from jim.tests.conftest import enroll


def test_the_stub_coach_answers_from_the_pack(client):
    user = enroll(client)
    body = client.post(f"/coach/{user}", json={
        "area": "mental_health",
        "message": "I keep having panic attacks and my pulse races"}).json()
    assert body["delivered"] is True
    assert "false alarm" in body["content"]
    prov = body["provenance"]
    assert "offline pipeline" in prov["method"]
    assert any("panic" in r.lower() for r in prov["evidence"])


def test_below_the_threshold_the_pack_stays_silent(client):
    """A wrong-topic answer is worse than a plain one — an unmatched
    question falls back to the stub's honest text, and the provenance
    never claims the pack."""
    user = enroll(client)
    body = client.post(f"/coach/{user}", json={
        "area": "career",
        "message": "What do you think about my plan for tomorrow?"}).json()
    assert body["delivered"] is True
    assert "offline pipeline" not in body["provenance"]["method"]


def test_every_entry_carries_references_and_stays_on_the_guidance_side():
    assert len(knowledge.ENTRIES) >= ratchets.floor("knowledge.entries")
    for e in knowledge.ENTRIES:
        assert e["references"], e["topic"]
        assert e["area"] in {"mental_health", "health_fitness", "nutrition",
                             "career", "finance", "relationships"}, e["topic"]
    cat = knowledge.catalog()
    # All six industries covered — and each with a real shelf, not a token
    # row. The owner's word for the target was "jampacked"; five per area
    # is the floor that holds it.
    assert set(cat["areas"]) == {"mental_health", "health_fitness",
                                 "nutrition", "career", "finance",
                                 "relationships"}
    for topics in cat["areas"].values():
        assert len(topics) >= ratchets.floor("knowledge.thinnest_area")
