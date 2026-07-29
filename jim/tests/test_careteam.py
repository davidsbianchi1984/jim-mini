"""The care team is an organization: linking the user's own QRME org,
manual coordination, and the stacking rule — a drift-band crossing while
medication adherence slips takes the situation to the whole team, at most
once a day, with the user's own credential and never raw readings.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from jim import careteam, db
from jim.qrme_client import QRMEClient
from jim.tests.conftest import FakeQRME, _Resp, enroll


class FakeOrgQRME(FakeQRME):
    """The conftest fake plus QRME's organization surface."""

    def __init__(self, departments=2):
        super().__init__()
        self.departments = departments
        self.coordinations = []

    def get(self, path, headers=None):
        if path.startswith("/organizations/"):
            if (headers or {}).get("authorization") != "Bearer own_good":
                return _Resp(403, {"detail": "not this organization's owner"})
            return _Resp(200, {"id": "org_1", "name": "The Household",
                               "departments": [
                                   {"id": f"dep_{i}", "name": f"Desk {i}",
                                    "role": "cares", "agent": f"A{i}",
                                    "scoped": False}
                                   for i in range(self.departments)]})
        return super().get(path, headers=headers)

    def post(self, path, json=None, headers=None):
        if path.endswith("/coordinate"):
            if (headers or {}).get("authorization") != "Bearer own_good":
                return _Resp(403, {"detail": "not this organization's owner"})
            self.coordinations.append(json)
            return _Resp(201, {"id": f"crd_{len(self.coordinations)}",
                               "goal": json["goal"],
                               "plan": "Desk 0 checks in daily; Desk 1 "
                                       "reviews the doses.",
                               "sealed": True, "status": "completed"})
        return super().post(path, json=json, headers=headers)


def _tandem(make_tandem_client, fake):
    from fastapi.testclient import TestClient
    from jim.api import create_app
    tc = TestClient(create_app(qrme_client=QRMEClient(client=fake)))
    tc.__enter__()
    return tc


def test_linking_validates_the_org_and_department(make_tandem):
    client = make_tandem()
    # Swap in the org-aware fake through the same client boundary.
    fake = FakeOrgQRME()
    client.app.state.qrme = QRMEClient(client=fake)
    user = enroll(client)
    r = client.put(f"/users/{user}/care-team", json={
        "org_id": "org_1", "department_id": "dep_9",
        "owner_token": "own_good"})
    assert r.status_code == 422
    assert "not part of the organization" in r.json()["detail"]
    r = client.put(f"/users/{user}/care-team", json={
        "org_id": "org_1", "department_id": "dep_0",
        "owner_token": "own_good"})
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["linked"] and out["credential_held"] is True
    assert "owner_token" not in out          # the credential never echoes


def test_a_lone_department_is_not_a_team(make_tandem):
    client = make_tandem()
    client.app.state.qrme = QRMEClient(client=FakeOrgQRME(departments=1))
    user = enroll(client)
    r = client.put(f"/users/{user}/care-team", json={
        "org_id": "org_1", "department_id": "dep_0",
        "owner_token": "own_good"})
    assert r.status_code == 422
    assert "at least two departments" in r.json()["detail"]


def test_manual_coordination_lands_a_plan(make_tandem):
    client = make_tandem()
    fake = FakeOrgQRME()
    client.app.state.qrme = QRMEClient(client=fake)
    user = enroll(client)
    client.put(f"/users/{user}/care-team", json={
        "org_id": "org_1", "department_id": "dep_0",
        "owner_token": "own_good"})
    r = client.post(f"/users/{user}/care-team/coordinate",
                    json={"goal": "plan the recovery week"})
    assert r.status_code == 201, r.text
    plan = r.json()
    assert "Desk 1 reviews the doses" in plan["plan"]
    assert plan["sealed_in_qrme_vault"] is True
    assert fake.coordinations[0]["from_department"] == "dep_0"
    listed = client.get(f"/users/{user}/care-team/plans").json()
    assert len(listed) == 1


def test_unlink_deletes_the_credential(make_tandem):
    client = make_tandem()
    client.app.state.qrme = QRMEClient(client=FakeOrgQRME())
    user = enroll(client)
    client.put(f"/users/{user}/care-team", json={
        "org_id": "org_1", "department_id": "dep_0",
        "owner_token": "own_good"})
    assert client.delete(f"/users/{user}/care-team").status_code == 204
    assert client.get(f"/users/{user}/care-team").json() == {"linked": False}
    row = db.connect().execute("SELECT * FROM care_teams").fetchone()
    assert row is None


def _backdate_med(days: int) -> None:
    conn = db.connect()
    stamp = (datetime.now() - timedelta(days=days)).isoformat()
    conn.execute("UPDATE medications SET created_at=?", (stamp,))
    conn.commit()


def test_stacking_rule_fires_once_and_cools_down(make_tandem):
    client = make_tandem()
    fake = FakeOrgQRME()
    qrme = QRMEClient(client=fake)
    client.app.state.qrme = qrme
    user = enroll(client)
    client.put(f"/users/{user}/care-team", json={
        "org_id": "org_1", "department_id": "dep_0",
        "owner_token": "own_good"})
    # A scheduled med, a week old, with no doses logged: adherence 0.
    r = client.post(f"/meds/{user}", json={
        "name": "Lisinopril", "dose": "10mg",
        "schedule": {"times": ["08:00"]}})
    assert r.status_code == 201, r.text
    _backdate_med(7)

    drifts = [{"metric": "resting_heart_rate", "direction": "high"}]
    plan = careteam.consider(user, drifts, qrme)
    assert plan is not None
    assert "Lisinopril at 0%" in plan["goal"]
    assert "resting_heart_rate" in plan["goal"]
    # Summaries cross, never raw readings.
    assert "trigger" in plan and plan["trigger"]["slipping_meds"]

    # Within the cooldown, the same signals do not re-plan.
    assert careteam.consider(user, drifts, qrme) is None
    later = datetime.now() + timedelta(hours=careteam.COOLDOWN_HOURS + 1)
    assert careteam.consider(user, drifts, qrme, now=later) is not None


def test_no_slipping_meds_means_no_coordination(make_tandem):
    client = make_tandem()
    qrme = QRMEClient(client=FakeOrgQRME())
    client.app.state.qrme = qrme
    user = enroll(client)
    client.put(f"/users/{user}/care-team", json={
        "org_id": "org_1", "department_id": "dep_0",
        "owner_token": "own_good"})
    drifts = [{"metric": "resting_heart_rate", "direction": "high"}]
    assert careteam.consider(user, drifts, qrme) is None
