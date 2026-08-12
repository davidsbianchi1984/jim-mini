"""The weekly letter (jim/letter.py): what your numbers meant, in words.

The letter is composed only from what was logged — on the test box the
provider is the stub, so the deterministic digest IS the letter and says
so (`described_by: "digest"`). A week with nothing logged gets no letter,
because a letter about an empty week would have to invent its contents.
"""

from jim.tests.conftest import enroll


def test_the_letter_holds_the_week_and_only_the_week(client):
    user = enroll(client)
    r = client.post(f"/checkin/{user}",
                    json={"mood": 4, "energy": 3, "note": "steady"})
    assert r.status_code == 201, r.text
    r = client.post(f"/users/{user}/meals",
                    json={"note": "lentil soup and bread"})
    assert r.status_code == 201, r.text

    r = client.post(f"/users/{user}/letters")
    assert r.status_code == 201, r.text
    letter = r.json()
    assert letter["described_by"] == "digest"
    assert "check-in" in letter["body"]
    assert "lentil soup" in letter["body"]
    # The facts under the words travel with the letter.
    assert any("meal" in line for line in letter["digest"])

    shelf = client.get(f"/users/{user}/letters").json()
    assert len(shelf) == 1 and shelf[0]["body"] == letter["body"]


def test_an_empty_week_gets_no_letter(client):
    user = enroll(client)
    r = client.post(f"/users/{user}/letters")
    assert r.status_code == 422
    assert "nothing was logged" in r.json()["detail"]
