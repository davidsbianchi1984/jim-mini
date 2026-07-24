"""Robots as first-aid responders.

Rated platforms assist (fetch the AED, coach the playbook, meet EMS);
perform-rated platforms (mechanical-CPR-class force control) may additionally
deliver chest compressions — but only after a person on scene confirms, and
never a shock: rhythm analysis stays with the AED and the shock button stays
with a human.
"""

from jim.tests.conftest import enroll


def _bind(client, uid, model, name=None):
    body = {"model": model}
    if name:
        body["name"] = name
    r = client.post(f"/robots/{uid}", json=body)
    assert r.status_code == 201, r.text
    return r.json()


# ---- catalog: ratings & allowlists -----------------------------------------

def test_catalog_rates_platforms_for_first_aid(client):
    cat = client.get("/robotics/catalog").json()
    by_model = {r["model"]: r for r in cat["robots"]}
    assert by_model["optimus"]["maker"] == "Tesla"
    assert by_model["optimus"]["first_aid"] == "perform"
    assert by_model["figure_03"]["first_aid"] == "perform"
    assert by_model["atlas"]["first_aid"] == "perform"
    assert by_model["neo"]["first_aid"] == "assist"
    assert by_model["g1"]["first_aid"] == "assist"
    assert by_model["saros_20"]["first_aid"] is None
    assert cat["cardiac_directives"]["perform"].startswith("begin_hands_only_cpr")


def test_rating_gates_the_command_allowlist(client):
    uid = enroll(client)
    optimus = _bind(client, uid, "optimus")
    neo = _bind(client, uid, "neo")
    assert "perform_cpr" in optimus["commands"]
    assert "fetch_aed" in optimus["commands"]
    assert "perform_cpr" not in neo["commands"]
    assert {"fetch_aed", "guide_first_aid", "meet_responders"} <= set(neo["commands"])


# ---- commands ---------------------------------------------------------------

def test_assist_rated_robot_cannot_perform_cpr(client):
    uid = enroll(client)
    neo = _bind(client, uid, "neo")
    r = client.post(f"/robots/{uid}/{neo['id']}/command",
                    json={"command": "perform_cpr", "arg": "confirmed"})
    assert r.status_code == 422
    assert "not permitted" in r.json()["detail"]


def test_perform_cpr_requires_on_scene_confirmation(client):
    uid = enroll(client)
    optimus = _bind(client, uid, "optimus", name="hall Optimus")
    # Step 1: without confirmation nothing starts.
    r = client.post(f"/robots/{uid}/{optimus['id']}/command",
                    json={"command": "perform_cpr"}).json()
    assert r["status"] == "confirmation_required"
    assert "unresponsive" in r["instruction"]
    robots = client.get(f"/robots/{uid}").json()
    assert robots[0]["status"] == "docked"          # untouched

    # Step 2: confirmed — compressions start at the playbook pace.
    r = client.post(f"/robots/{uid}/{optimus['id']}/command",
                    json={"command": "perform_cpr", "arg": "confirmed"}).json()
    assert r["status"] == "compressions_started"
    assert r["pace"]["compressions_per_minute"] == 110
    assert any("never delivers a shock" in s for s in r["safeguards"])
    robots = client.get(f"/robots/{uid}").json()
    assert robots[0]["status"] == "performing_cpr"

    # Stop hands back over.
    r = client.post(f"/robots/{uid}/{optimus['id']}/command",
                    json={"command": "stop_cpr"}).json()
    assert r["status"] == "compressions_stopped"


def test_guide_first_aid_speaks_the_playbook(client):
    uid = enroll(client)
    neo = _bind(client, uid, "neo")
    r = client.post(f"/robots/{uid}/{neo['id']}/command",
                    json={"command": "guide_first_aid", "arg": "aed"}).json()
    assert r["status"] == "coaching"
    assert r["playbook"]["kind"] == "aed"
    assert any("Stand clear" in s for s in r["spoken"])
    # CPR coaching carries the pace cue.
    r = client.post(f"/robots/{uid}/{neo['id']}/command",
                    json={"command": "guide_first_aid"}).json()
    assert r["playbook"]["kind"] == "cpr"
    assert r["playbook"]["pace"]["compressions_per_minute"] == 110


def test_fetch_aed_and_meet_responders(client):
    uid = enroll(client)
    memo = _bind(client, uid, "memo")
    r = client.post(f"/robots/{uid}/{memo['id']}/command",
                    json={"command": "fetch_aed"}).json()
    assert r["status"] == "queued" and "AED" in r["note"]
    r = client.post(f"/robots/{uid}/{memo['id']}/command",
                    json={"command": "meet_responders"}).json()
    assert "EMS" in r["note"]


def test_unknown_command_refused(client):
    uid = enroll(client)
    vac = _bind(client, uid, "saros_20")
    r = client.post(f"/robots/{uid}/{vac['id']}/command",
                    json={"command": "perform_cpr", "arg": "confirmed"})
    assert r.status_code == 422


# ---- cardiac escalation directives ------------------------------------------

def test_cardiac_escalation_assigns_first_aid_roles(client):
    uid = enroll(client, contact_consent=True, emergency_name="Sam",
                 emergency_phone="+1000")
    _bind(client, uid, "optimus")
    _bind(client, uid, "neo")
    _bind(client, uid, "saros_20")

    r = client.post(f"/monitor/{uid}", json={"rhythm": "fibrillation"}).json()
    assert r["condition"] == "cardiac_event"
    directives = {d["model"]: d for d in r["escalation"]["robot_directives"]}
    assert directives["optimus"]["directive"].startswith("begin_hands_only_cpr")
    assert directives["optimus"]["first_aid"] == "perform"
    assert directives["neo"]["directive"] == "fetch_aed_and_coach_cpr_pace"
    assert directives["saros_20"]["directive"] == "dock_and_clear_floor"


def test_non_cardiac_escalation_keeps_generic_directives(client):
    uid = enroll(client, contact_consent=True, emergency_name="Sam",
                 emergency_phone="+1000")
    _bind(client, uid, "optimus")
    r = client.post(f"/monitor/{uid}", json={"heart_rate": 145}).json()
    assert r["condition"] != "cardiac_event"
    directives = {d["model"]: d["directive"]
                  for d in r["escalation"]["robot_directives"]}
    assert directives["optimus"] == "navigate_to_user"


def test_emergency_with_cardiac_signal_directs_first_aid(client):
    uid = enroll(client)
    _bind(client, uid, "figure_03")
    r = client.post(f"/emergency/{uid}", json={
        "situation": "he collapsed and isn't breathing",
        "sample": {"movement": "collapse", "pulse": "absent"}}).json()
    assert r["ai_guidance"]["first_aid"]["kind"] == "cpr"
    d = r["robot_directives"][0]
    assert d["directive"].startswith("begin_hands_only_cpr")
