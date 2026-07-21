"""Shareable Medical ID QR: a first responder scans the code and reads the
condition-level Medical ID without the user's auth token; the user can rotate
or revoke it, and only the hash is stored."""

from jim.tests.conftest import enroll


def _full(client):
    return enroll(client, birthdate="1984-06-01", resting_heart_rate=60,
                  contact_consent=True, emergency_name="Maria",
                  emergency_phone="+15551234567", known_conditions=["anxiety"])


def test_issue_and_scan_the_card(client):
    uid = _full(client)
    issued = client.post(f"/medical-id/qr/{uid}").json()
    assert issued["token"].startswith("med_")
    assert issued["view_url"] == f"/medical-id/{issued['token']}"

    # A responder scans — no auth header at all — and reads the Medical ID.
    med = client.get(issued["view_url"], headers={"authorization": ""}).json()
    assert med["name"] == "Jordan"
    assert "acute anxiety / panic" in med["known_conditions"]
    assert med["emergency_contact"]["name"] == "Maria"
    # Condition-level only: no journal/notes/raw-biometric fields leak.
    assert "note" not in med and "journal" not in med


def test_qr_svg_is_served(client):
    uid = _full(client)
    token = client.post(f"/medical-id/qr/{uid}").json()["token"]
    r = client.get(f"/medical-id/{token}/qr.svg", headers={"authorization": ""})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("image/svg+xml")
    # The URL is encoded in the QR matrix (paths), not as literal SVG text.
    assert b"<svg" in r.content and b"path" in r.content
    # A revoked token no longer renders a code.
    client.delete(f"/medical-id/qr/{uid}")
    assert client.get(f"/medical-id/{token}/qr.svg",
                      headers={"authorization": ""}).status_code == 404


def test_rotation_invalidates_the_old_code(client):
    uid = _full(client)
    old = client.post(f"/medical-id/qr/{uid}").json()["token"]
    new = client.post(f"/medical-id/qr/{uid}").json()["token"]
    assert new != old
    assert client.get(f"/medical-id/{new}", headers={"authorization": ""}).status_code == 200
    # The rotated-out code no longer resolves.
    assert client.get(f"/medical-id/{old}", headers={"authorization": ""}).status_code == 404


def test_revoke_kills_the_card(client):
    uid = _full(client)
    token = client.post(f"/medical-id/qr/{uid}").json()["token"]
    assert client.delete(f"/medical-id/qr/{uid}").status_code == 204
    assert client.get(f"/medical-id/{token}", headers={"authorization": ""}).status_code == 404
    # Nothing to revoke the second time.
    assert client.delete(f"/medical-id/qr/{uid}").status_code == 404


def test_unknown_token_is_not_found(client):
    assert client.get("/medical-id/med_nope",
                      headers={"authorization": ""}).status_code == 404


def test_issue_requires_the_users_own_token(client):
    uid = _full(client)
    enroll(client)                       # switches the client's default token
    assert client.post(f"/medical-id/qr/{uid}").status_code == 403


def test_card_is_stored_hashed_and_erased(client):
    from jim import db
    uid = _full(client)
    token = client.post(f"/medical-id/qr/{uid}").json()["token"]
    rows = [dict(r) for r in db.connect().execute(
        "SELECT * FROM medical_cards WHERE user_id=?", (uid,)).fetchall()]
    assert token not in str(rows)        # plaintext token never persisted
    deleted = client.delete(f"/data/{uid}").json()["deleted"]
    assert deleted["medical_cards"] == 1
