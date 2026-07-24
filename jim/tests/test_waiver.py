"""The autonomous-resuscitation waiver.

Automatic operation — CPR that starts without an on-scene confirmation, and a
fully-automatic AED that shocks on its own rhythm analysis — is locked until
the user signs the liability waiver (typed legal name + explicit acceptance).
Revoking restores confirm-gated operation. Even with a waiver, a shock only
ever follows the AED's analysis — never the robot's own judgement.
"""

from jim.tests.conftest import enroll


def _bind(client, uid, model):
    r = client.post(f"/robots/{uid}", json={"model": model})
    assert r.status_code == 201, r.text
    return r.json()


def _sign(client, uid, name="Jordan"):
    r = client.post(f"/waivers/{uid}",
                    json={"signature": name, "accept": True})
    assert r.status_code == 201, r.text
    return r.json()


def test_waiver_terms_and_unsigned_state(client):
    uid = enroll(client)
    w = client.get(f"/waivers/{uid}").json()
    assert w["signed"] is False
    assert any("waive" in t.lower() for t in w["terms"])
    assert any("only ever delivered when the AED" in t for t in w["terms"])


def test_signing_requires_acceptance_and_matching_name(client):
    uid = enroll(client)
    r = client.post(f"/waivers/{uid}",
                    json={"signature": "Jordan", "accept": False})
    assert r.status_code == 403
    r = client.post(f"/waivers/{uid}",
                    json={"signature": "   ", "accept": True})
    assert r.status_code == 422
    r = client.post(f"/waivers/{uid}",
                    json={"signature": "Someone Else", "accept": True})
    assert r.status_code == 422
    signed = _sign(client, uid)
    assert signed["signed"] is True
    assert client.get(f"/waivers/{uid}").json()["signed"] is True


def test_auto_defib_locked_without_waiver(client):
    uid = enroll(client)
    optimus = _bind(client, uid, "optimus")
    r = client.post(f"/robots/{uid}/{optimus['id']}/command",
                    json={"command": "auto_defib"})
    assert r.status_code == 422
    assert "waiver" in r.json()["detail"]


def test_waiver_unlocks_automatic_operation(client):
    uid = enroll(client)
    optimus = _bind(client, uid, "optimus")
    _sign(client, uid)

    # CPR now starts without the on-scene confirm arg.
    r = client.post(f"/robots/{uid}/{optimus['id']}/command",
                    json={"command": "perform_cpr"}).json()
    assert r["status"] == "compressions_started"
    assert "pre-authorized by waiver" in r["note"]

    # The fully-automatic AED engages; the device stays the only shock
    # decision-maker.
    r = client.post(f"/robots/{uid}/{optimus['id']}/command",
                    json={"command": "auto_defib"}).json()
    assert r["status"] == "auto_resuscitation_engaged"
    assert any("ONLY if the device advises" in s for s in r["sequence"])
    assert any("rhythm analysis" in s for s in r["safeguards"])


def test_waiver_never_unlocks_assist_rated_bodies(client):
    uid = enroll(client)
    neo = _bind(client, uid, "neo")
    _sign(client, uid)
    r = client.post(f"/robots/{uid}/{neo['id']}/command",
                    json={"command": "auto_defib"})
    assert r.status_code == 422           # rating gate is independent


def test_revoking_restores_confirm_gates(client):
    uid = enroll(client)
    optimus = _bind(client, uid, "optimus")
    _sign(client, uid)
    r = client.delete(f"/waivers/{uid}").json()
    assert r["signed"] is False

    r = client.post(f"/robots/{uid}/{optimus['id']}/command",
                    json={"command": "perform_cpr"}).json()
    assert r["status"] == "confirmation_required"
    r = client.post(f"/robots/{uid}/{optimus['id']}/command",
                    json={"command": "auto_defib"})
    assert r.status_code == 422


def test_cardiac_escalation_upgrades_with_waiver(client):
    uid = enroll(client)
    _bind(client, uid, "optimus")
    _bind(client, uid, "neo")

    # Without a waiver: hands-only CPR directive.
    r = client.post(f"/monitor/{uid}", json={"rhythm": "fibrillation"}).json()
    d = {x["model"]: x for x in r["escalation"]["robot_directives"]}
    assert d["optimus"]["directive"].startswith("begin_hands_only_cpr")

    # With a waiver: the full automatic sequence; assist bodies unchanged.
    _sign(client, uid)
    r = client.post(f"/monitor/{uid}", json={"rhythm": "fibrillation"}).json()
    d = {x["model"]: x for x in r["escalation"]["robot_directives"]}
    assert d["optimus"]["directive"] == "auto_resuscitate_cpr_plus_auto_aed"
    assert "pre-authorized" in d["optimus"]["waiver"]
    assert d["neo"]["directive"] == "fetch_aed_and_coach_cpr_pace"
