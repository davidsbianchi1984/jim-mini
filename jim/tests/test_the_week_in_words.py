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


# -- what the watching noticed ------------------------------------------------

def _watched(client, user, vault, url="https://example.com/clinic",
             changed="2099-01-01T09:00:00+00:00"):
    """A planted lookout whose capture changed at `changed` (default:
    safely inside any week window that includes the test's run)."""
    import json

    from jim import errands, lookout
    client.app.state.pdi = vault
    r = client.put(f"/engaged/{user}/permits/{errands.PERMIT}",
                   json={"granted": True})
    assert r.status_code == 200, r.text
    planted = client.post(f"/lookout/{user}",
                          json={"url": url, "every_hours": 24}).json()
    vault.records[lookout.capture_key(planted["task_id"])] = json.dumps(
        {"url": url, "text": "words", "fetched_at": changed,
         "changed_at": changed})
    return planted


def test_the_letter_mentions_a_page_that_changed_this_week(client):
    from jim.tests.test_the_lookout import StandingVault
    user = enroll(client)
    vault = StandingVault()
    _watched(client, user, vault, changed="2999-01-01T09:00:00+00:00")
    # Nothing else logged: the changed page alone is a real event the
    # person asked to be told about, and it earns the letter.
    r = client.post(f"/users/{user}/letters")
    assert r.status_code == 201, r.text
    letter = r.json()
    assert any("watched page https://example.com/clinic changed on 2999-01-01"
               == line for line in letter["digest"]), letter["digest"]


def test_a_change_before_the_window_stays_out_of_the_letter(client):
    from jim.tests.test_the_lookout import StandingVault
    user = enroll(client)
    vault = StandingVault()
    _watched(client, user, vault, changed="2000-01-01T09:00:00+00:00")
    r = client.post(f"/users/{user}/letters")
    assert r.status_code == 422, "an old change is not this week's news"


def test_the_letter_says_when_the_watch_is_failing(client):
    from jim.tests.test_the_lookout import StandingVault
    user = enroll(client)
    vault = StandingVault()
    planted = _watched(client, user, vault,
                       changed="2000-01-01T09:00:00+00:00")
    vault.runs[planted["task_id"]] = [
        {"id": "rrun_1", "ran_at": "2999-01-01T10:00:00+00:00",
         "status": "failed", "note": "ResidentError: the wire is down"}]
    r = client.post(f"/users/{user}/letters")
    assert r.status_code == 201, r.text
    assert any("the watch on https://example.com/clinic has been failing"
               == line for line in r.json()["digest"])


def test_an_unreached_vault_never_costs_the_letter(client):
    from jim.tests.test_the_lookout import BrokenVault, StandingVault
    user = enroll(client)
    vault = StandingVault()
    _watched(client, user, vault)
    client.app.state.pdi = BrokenVault()
    client.post(f"/checkin/{user}", json={"mood": 4, "energy": 3})
    r = client.post(f"/users/{user}/letters")
    assert r.status_code == 201, r.text
    assert not any("watched page" in line for line in r.json()["digest"])
