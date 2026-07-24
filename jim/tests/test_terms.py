"""Terms of Service at the gateway: served with a version, required to
enroll, recorded with a receipt."""

from jim import db
from jim.terms import TERMS_VERSION
from jim.tests.conftest import enroll


def test_terms_are_served_versioned(client):
    t = client.get("/terms").json()
    assert t["version"] == TERMS_VERSION
    assert t["document"] == "docs/terms.md"
    assert any("not a medical device" in p for p in t["key_points"])
    assert any("911" in p for p in t["key_points"])


def test_enrollment_requires_and_records_acceptance(client):
    refused = client.post("/enroll", json={
        "display_name": "NoConsent", "birthdate": "1990-01-01",
        "terms_consent": False})
    assert refused.status_code == 403

    user = enroll(client)
    row = db.connect().execute(
        "SELECT terms_version, terms_accepted_at FROM users WHERE id=?",
        (user,)).fetchone()
    assert row["terms_version"] == TERMS_VERSION
    assert row["terms_accepted_at"]      # timestamped receipt
