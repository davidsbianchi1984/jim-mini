"""Interview drills (jim/drills.py): practice the answer before the room
is real.

The bank is local and the drill works with the network cut: on the test
box the provider is the stub, so the reading is the probe checklist
itself, plainly labeled — a mirror, not a pretended judge.
"""

from jim.tests.conftest import enroll


def test_the_drill_deals_reads_and_reaches_the_coach(client):
    user = enroll(client)
    r = client.post(f"/users/{user}/drills", json={"kind": "behavioral"})
    assert r.status_code == 201, r.text
    drill = r.json()
    assert drill["kind"] == "behavioral"
    assert drill["question"] and len(drill["probes"]) == 3

    r = client.post(f"/users/{user}/drills/{drill['id']}/answer",
                    json={"answer": "Once our launch slipped and I owned "
                                    "the missed handoff, then rebuilt the "
                                    "checklist we ship with."})
    assert r.status_code == 200, r.text
    read = r.json()
    # Stub provider: the checklist stands in, and says so.
    assert read["described_by"] == "checklist"
    assert read["critique"] is None
    assert read["probes"] == drill["probes"]

    # Answering twice is refused; the drill is one question, one answer.
    r = client.post(f"/users/{user}/drills/{drill['id']}/answer",
                    json={"answer": "again"})
    assert r.status_code == 422

    board = client.get(f"/users/{user}/drills").json()
    assert len(board) == 1 and board[0]["answered_at"]

    # The practice reached the career area's readable context.
    reply = client.post(f"/coach/{user}", json={
        "area": "career", "message": "how is my interview prep going?"}).json()
    collected = [l for l in reply["provenance"]["pipeline"]
                 if l["layer"] == "add.collected"]
    assert collected, "the coach's collected layer is missing"


def test_an_empty_answer_and_a_strange_kind_are_refused(client):
    user = enroll(client)
    r = client.post(f"/users/{user}/drills", json={"kind": "astrology"})
    assert r.status_code == 422
    assert "this bank holds" in r.json()["detail"]

    r = client.post(f"/users/{user}/drills", json={})
    drill = r.json()
    r = client.post(f"/users/{user}/drills/{drill['id']}/answer",
                    json={"answer": "   "})
    assert r.status_code == 422
    assert "empty answer" in r.json()["detail"]
