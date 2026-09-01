"""The medicine cabinet: tracked in the user's words, never a pharmacist.

The properties under test: one slot has one correctable answer, the grace
period is generous, a missed dose never escalates, the as-needed ceiling
refuses rather than records, and a dose logged is a sign of life.
"""

from __future__ import annotations

from datetime import datetime

from jim import meds, vigil


def _enroll(client, name="Ada"):
    r = client.post("/enroll", json={
        "display_name": name, "birthdate": "1950-03-01",
        "terms_consent": True, "resting_heart_rate": 62})
    assert r.status_code == 201
    return r.json()


def _auth(u):
    return {"authorization": f"Bearer {u['user_token']}"}


def _med(client, u, **over):
    body = {"name": "Lisinopril", "dose": "10 mg",
            "schedule": {"times": ["08:00", "20:00"]},
            "purpose": "blood pressure", "critical": True}
    body.update(over)
    r = client.post(f"/meds/{u['id']}", json=body, headers=_auth(u))
    assert r.status_code == 201, r.text
    return r.json()


def test_a_medication_needs_a_name_a_dose_and_a_real_schedule(client):
    u = _enroll(client)
    r = client.post(f"/meds/{u['id']}", json={
        "name": "", "dose": "", "schedule": {"times": ["08:00"]}},
        headers=_auth(u))
    assert r.status_code == 422
    r = client.post(f"/meds/{u['id']}", json={
        "name": "X", "dose": "1", "schedule": {"times": ["8 o'clock"]}},
        headers=_auth(u))
    assert r.status_code == 422
    assert "HH:MM" in r.json()["detail"]


def test_the_board_knows_upcoming_due_and_missed_with_grace(client):
    u = _enroll(client)
    _med(client, u)
    noon = datetime(2026, 7, 29, 12, 0)
    b = meds.board(u["id"], now=noon)
    slots = {s["slot"]: s["status"]
             for s in b["medications"][0]["slots"]}
    assert slots["08:00"] == "missed"      # noon is past 8:00 + grace
    assert slots["20:00"] == "upcoming"
    at_eight_thirty = meds.board(u["id"], now=datetime(2026, 7, 29, 8, 30))
    assert at_eight_thirty["medications"][0]["slots"][0]["status"] == "due"
    # 9:07 for the 8:00 pill is still "due" — a board that says "missed"
    # seven minutes late teaches the person to ignore it.
    at_nine = meds.board(u["id"], now=datetime(2026, 7, 29, 9, 7))
    assert at_nine["medications"][0]["slots"][0]["status"] == "due"


def test_one_slot_one_answer_and_it_is_correctable(client):
    u = _enroll(client)
    m = _med(client, u)
    mid = m["medications"][0]["id"] if "medications" in m else m["id"]
    client.post(f"/meds/{u['id']}/{mid}/log",
                json={"action": "skipped", "slot": "08:00",
                      "note": "felt dizzy"}, headers=_auth(u))
    b = client.post(f"/meds/{u['id']}/{mid}/log",
                    json={"action": "taken", "slot": "08:00",
                          "note": "found it in my pocket"},
                    headers=_auth(u)).json()
    slot = b["medications"][0]["slots"][0]
    assert slot["status"] == "taken"
    assert "pocket" in slot["note"]
    week = client.get(f"/meds/{u['id']}/adherence", headers=_auth(u)).json()
    assert all(x["taken"] <= x["expected"] for x in week["adherence_rows"])


def test_a_missed_critical_dose_is_a_checkin_not_an_alarm(client):
    u = _enroll(client)
    _med(client, u, critical=True)
    noon = datetime(2026, 7, 29, 12, 0)
    b = meds.board(u["id"], now=noon)
    assert b["missed_critical"] and b["missed_critical"][0]["slot"] == "08:00"
    events = client.get(f"/events/{u['id']}", headers=_auth(u)).json()
    assert not [e for e in events if e["type"] == "escalation"]
    lines = meds.coach_context(u["id"], now=noon)
    assert any("critical" in ln for ln in lines)
    assert any("never scolding" in ln for ln in lines)


def test_the_as_needed_ceiling_refuses_rather_than_records(client):
    u = _enroll(client)
    m = _med(client, u, name="Ibuprofen", dose="200 mg",
             schedule={"as_needed": True, "max_per_day": 2}, critical=False)
    mid = m["id"]
    for _ in range(2):
        r = client.post(f"/meds/{u['id']}/{mid}/log",
                        json={"action": "taken"}, headers=_auth(u))
        assert r.status_code == 200
    r = client.post(f"/meds/{u['id']}/{mid}/log",
                    json={"action": "taken"}, headers=_auth(u))
    assert r.status_code == 409
    assert "prescriber" in r.json()["detail"]


def test_a_dose_logged_is_a_sign_of_life(client):
    """The pillbox keeps watch: for the person whose only daily interaction
    is their medication, taking it stands a tripped vigil down."""
    from datetime import timedelta, timezone

    from jim import db
    u = _enroll(client)
    m = _med(client, u)
    vigil.arm(u["id"], "Sam", "sam@example.com", quiet_days=1)
    client.post(f"/monitor/{u['id']}", json={"heart_rate": 62},
                headers=_auth(u))
    then = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    conn = db.connect()
    conn.execute("UPDATE events SET created_at=? WHERE user_id=?"
                 " AND type != 'vigil'", (then, u["id"]))
    conn.commit()
    vigil.sweep(u["id"])
    assert vigil.status(u["id"])["tripped"] is True
    client.post(f"/meds/{u['id']}/{m['id']}/log",
                json={"action": "taken", "slot": "08:00"}, headers=_auth(u))
    assert vigil.status(u["id"])["tripped"] is False


def test_archive_stops_the_board_but_keeps_the_history(client):
    u = _enroll(client)
    m = _med(client, u)
    client.post(f"/meds/{u['id']}/{m['id']}/log",
                json={"action": "taken", "slot": "08:00"}, headers=_auth(u))
    client.delete(f"/meds/{u['id']}/{m['id']}", headers=_auth(u))
    b = client.get(f"/meds/{u['id']}", headers=_auth(u)).json()
    assert b["medications"] == []
    from jim import db
    kept = db.connect().execute(
        "SELECT COUNT(*) AS n FROM med_logs WHERE med_id=?",
        (m["id"],)).fetchone()["n"]
    assert kept == 1


def test_adherence_counts_whole_days_only(client):
    u = _enroll(client)
    _med(client, u)
    a = meds.adherence(u["id"], days=7)
    med = a["adherence_rows"][0]
    assert med["expected"] == 0        # created today; yesterday it didn't exist
    assert med["rate"] is None


def test_the_board_carries_the_not_a_pharmacist_line(client):
    u = _enroll(client)
    _med(client, u)
    b = client.get(f"/meds/{u['id']}", headers=_auth(u)).json()
    assert "pharmacist" in b["disclaimer"]


def test_meds_require_the_users_own_token(client):
    u, other = _enroll(client), _enroll(client, "Robin")
    m = _med(client, u)
    assert client.get(f"/meds/{u['id']}",
                      headers=_auth(other)).status_code in (401, 403)
    r = client.post(f"/meds/{u['id']}/{m['id']}/log",
                    json={"action": "taken", "slot": "08:00"},
                    headers=_auth(other))
    assert r.status_code in (401, 403)


def test_another_users_medication_id_is_a_404(client):
    u, other = _enroll(client), _enroll(client, "Robin")
    m = _med(client, u)
    r = client.post(f"/meds/{other['id']}/{m['id']}/log",
                    json={"action": "taken", "slot": "08:00"},
                    headers=_auth(other))
    assert r.status_code == 404
