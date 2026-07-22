"""Safe knowledge excursions: the Guardian studies a topic without carrying the
user's PHI out, then brings general knowledge back."""

from jim.tests.conftest import enroll


def _enrolled(client):
    return enroll(client, emergency_name="Ana Reyes", emergency_phone="+1 555 0100",
                  contact_consent=True)


def test_brief_redacts_user_and_contact(client):
    uid = _enrolled(client)
    r = client.post(f"/excursions/{uid}", json={
        "topic": "managing type 2 diabetes",
        "question": "Jordan asked how to help; can Ana Reyes be alerted on lows?",
    })
    assert r.status_code == 201, r.text
    exc = r.json()
    assert "Jordan" not in exc["brief"]
    assert "Ana Reyes" not in exc["brief"]
    assert "[private]" in exc["brief"]
    assert exc["redactions"] >= 2
    # General medical topic survives; the person doesn't.
    assert "diabetes" in exc["brief"]
    assert exc["findings"]
    assert "Jordan" not in exc["findings"]


def test_caller_private_terms(client):
    uid = _enrolled(client)
    exc = client.post(f"/excursions/{uid}", json={
        "topic": "sleep hygiene",
        "question": "tips before the Meridian Clinic appointment on account 9921",
        "private": ["Meridian Clinic", "9921"],
    }).json()
    assert "Meridian Clinic" not in exc["brief"]
    assert "9921" not in exc["brief"]


def test_nothing_leaves_by_default_and_offline(client, monkeypatch):
    uid = _enrolled(client)
    exc = client.post(f"/excursions/{uid}",
                      json={"topic": "hydration", "question": "how much water"}).json()
    assert exc["left_host"] is False        # no cloud attached
    monkeypatch.setenv("JIM_OFFLINE", "1")
    exc2 = client.post(f"/excursions/{uid}",
                       json={"topic": "stretching", "question": "morning routine"}).json()
    assert exc2["left_host"] is False
    assert exc2["findings"]                  # still gathered locally


def test_learn_folds_into_context(client):
    uid = _enrolled(client)
    exc = client.post(f"/excursions/{uid}",
                      json={"topic": "vagal tone", "question": "what raises it"}).json()
    r = client.post(f"/excursions/entry/{exc['id']}/learn")
    assert r.status_code == 201, r.text
    assert r.json()["learned"] is True
    assert client.get(f"/excursions/entry/{exc['id']}").json()["learned"] is True
    # Idempotent.
    assert client.post(f"/excursions/entry/{exc['id']}/learn").json()["already_learned"] is True
