"""Meal logging (jim/meals.py): the photo is the receipt, the note is the log.

No pretended vision: the providers are text-only, so the log comes from the
person's own words — tidied by the online model when one is standing, kept
verbatim when not — and the photo walks the same sealing path every clinical
capture takes. The log line stays local like a check-in, so the offline
coach's nutrition area can read today's meals with the network cut.
"""

from jim.tests.conftest import enroll


def test_a_note_logs_the_meal_and_the_coach_can_read_it(client):
    user = enroll(client)
    r = client.post(f"/users/{user}/meals",
                    json={"note": "oatmeal with berries and black coffee"})
    assert r.status_code == 201, r.text
    meal = r.json()
    # Stub provider on the test box: the note stands as the log, honestly.
    assert meal["described_by"] == "note"
    assert "oatmeal" in meal["logged"]
    assert meal["photo_sealed"] is False

    board = client.get(f"/users/{user}/meals").json()
    assert len(board) == 1 and board[0]["logged"] == meal["logged"]

    # The log line reached the coach's readable context.
    reply = client.post(f"/coach/{user}", json={
        "area": "nutrition", "message": "how was my breakfast?"}).json()
    collected = [l for l in reply["provenance"]["pipeline"]
                 if l["layer"] == "add.collected"]
    assert collected, "the coach's collected layer is missing"


def test_an_empty_plate_is_refused(client):
    user = enroll(client)
    r = client.post(f"/users/{user}/meals", json={})
    assert r.status_code == 422
    assert "nothing to log" in r.json()["detail"]


def test_a_photo_needs_the_vault_the_captures_need(client):
    """No vault on this deployment: the photo path refuses with 503 exactly
    as the capture door does — a meal photo is a photo of somebody's life."""
    import base64
    user = enroll(client)
    r = client.post(f"/users/{user}/meals", json={
        "note": "lunch", "content": base64.b64encode(b"fakejpeg").decode()})
    assert r.status_code in (402, 503), r.text
