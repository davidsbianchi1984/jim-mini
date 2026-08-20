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


def test_the_letter_accounts_for_the_studying(client):
    user = enroll(client)
    r = client.post(f"/excursions/{user}", json={
        "topic": "hydration for older adults",
        "question": "how much water daily"})
    assert r.status_code == 201, r.text
    r = client.post(f"/users/{user}/letters")
    assert r.status_code == 201, r.text
    assert any(
        "1 study taken, most recently: hydration for older adults" == line
        for line in r.json()["digest"]), r.json()["digest"]


def test_a_network_voice_gets_the_sanitized_digest(client, monkeypatch):
    """The letter is not the looser door: the study path sanitizes what
    leaves and says that it left, and the letter now keeps the same
    promise. A week whose meals name the person and their emergency
    contact reaches a network model with those names taken out — while
    their own letter keeps every word."""
    from jim import llm, research
    user = enroll(client, emergency_name="Pat", emergency_phone="+1-555-0199",
                  emergency_email="pat@example.com", contact_consent=True)
    client.post(f"/checkin/{user}", json={"mood": 4, "note": "steady"})
    r = client.post(f"/users/{user}/meals",
                    json={"note": "soup with Pat and Jordan"})
    assert r.status_code == 201, r.text

    sent = {}

    def fake_generate(user_id, system, text, cloud=None):
        sent["content"] = text
        return {"text": "A week, retold without names.",
                "provider": "anthropic", "degraded": False}
    monkeypatch.setattr(llm, "generate_for_user", fake_generate)
    monkeypatch.setattr(llm, "resolve_choice", lambda c: "anthropic")

    r = client.post(f"/users/{user}/letters")
    assert r.status_code == 201, r.text
    letter = r.json()
    assert letter["left_host"] is True
    assert letter["redactions"] >= 2
    assert "Pat" not in sent["content"] and "Jordan" not in sent["content"]
    assert research.REDACTION in sent["content"]
    # Their own letter keeps the real digest — sanitizing is about what
    # leaves, never about what they may read of their own week.
    assert any("Pat" in line for line in letter["digest"])

    shelf = client.get(f"/users/{user}/letters").json()
    assert shelf[0]["left_host"] is True and shelf[0]["redactions"] >= 2


def test_a_voice_that_stays_home_reads_the_full_digest(client, monkeypatch):
    """A local voice sends nothing anywhere: the digest goes to it whole,
    and left_host says so — the same word the excursions use."""
    from jim import llm
    user = enroll(client)
    client.post(f"/checkin/{user}", json={"mood": 4, "note": "steady"})
    monkeypatch.setattr(llm, "resolve_choice", lambda c: "stub")

    r = client.post(f"/users/{user}/letters")
    assert r.status_code == 201, r.text
    letter = r.json()
    assert letter["left_host"] is False and letter["redactions"] == 0
