"""Robot helpers as guardian responders: binding registers a device, and an
escalation sends role-appropriate directives to every bound body."""


def _enroll(client, **extra):
    body = {"display_name": "Jordan", "birthdate": "1995-05-05",
            "terms_consent": True, "resting_heart_rate": 60}
    body.update(extra)
    r = client.post("/enroll", json=body, headers={})
    assert r.status_code == 201, r.text
    return r.json()


def _auth(u):
    return {"authorization": f"Bearer {u['user_token']}"}


def test_catalog_lists_platforms_and_directives(client):
    cat = client.get("/robotics/catalog").json()
    models = {r["model"] for r in cat["robots"]}
    assert {"isaac_1", "neo", "u1_ultra", "memo", "saros_20",
            "qrevo_curv_2_flow"} <= models
    assert cat["escalation_directives"]["humanoid"] == "navigate_to_user"
    assert cat["escalation_directives"]["vacuum"] == "dock_and_clear_floor"


def test_bind_registers_a_device(client):
    u = _enroll(client)
    r = client.post(f"/robots/{u['id']}",
                    json={"model": "neo", "name": "hall NEO"}, headers=_auth(u))
    assert r.status_code == 201, r.text
    assert r.json()["escalation_directive"] == "navigate_to_user"
    # The robot now exists as a device, so alerts dispatch to it.
    devices = client.get(f"/devices/{u['id']}", headers=_auth(u)).json()
    assert any(d["name"] == "hall NEO" and d["kind"] == "autonomous"
               for d in devices)


def test_escalation_directs_the_robots(client):
    u = _enroll(client, emergency_name="Ma", emergency_phone="555-1",
                contact_consent=True)
    h = _auth(u)
    client.post(f"/robots/{u['id']}", json={"model": "neo"}, headers=h)
    client.post(f"/robots/{u['id']}", json={"model": "saros_20"}, headers=h)

    r = client.post(f"/monitor/{u['id']}", json={"heart_rate": 145},
                    headers=h).json()
    assert r["severity"] == "critical"
    directives = {d["model"]: d["directive"]
                  for d in r["escalation"]["robot_directives"]}
    assert directives["neo"] == "navigate_to_user"
    assert directives["saros_20"] == "dock_and_clear_floor"
    # The robots also got the plain device alert.
    assert "NEO" in r["escalation"]["dispatched_alerts"]

    # And they are marked responding.
    robots = client.get(f"/robots/{u['id']}", headers=h).json()
    assert all(rb["status"] == "responding" for rb in robots)


def test_emergency_button_also_directs_robots(client):
    u = _enroll(client)
    h = _auth(u)
    client.post(f"/robots/{u['id']}", json={"model": "memo"}, headers=h)
    r = client.post(f"/emergency/{u['id']}", json={"situation": "I fell"},
                    headers=h).json()
    assert r["robot_directives"][0]["directive"] == "navigate_to_user"


def test_llm_rules(client):
    u = _enroll(client)
    h = _auth(u)
    # Defaults to the user's model preference.
    client.put(f"/model/{u['id']}", json={"provider": "gemini"}, headers=h)
    r = client.post(f"/robots/{u['id']}", json={"model": "u1_ultra"}, headers=h)
    assert r.json()["llm_provider"] == "gemini"
    # A non-LLM platform refuses a provider.
    bad = client.post(f"/robots/{u['id']}",
                      json={"model": "qrevo_curv_2_flow", "llm_provider": "openai"},
                      headers=h)
    assert bad.status_code == 422


def test_unbind_removes_robot_and_device(client):
    u = _enroll(client)
    h = _auth(u)
    rob = client.post(f"/robots/{u['id']}",
                      json={"model": "isaac_1", "name": "den Isaac"},
                      headers=h).json()
    assert client.delete(f"/robots/{u['id']}/{rob['id']}",
                         headers=h).json()["unbound"] is True
    devices = client.get(f"/devices/{u['id']}", headers=h).json()
    assert not any(d["name"] == "den Isaac" for d in devices)


def test_robot_endpoints_require_the_user_token(client):
    u = _enroll(client)
    assert client.post(f"/robots/{u['id']}", json={"model": "neo"},
                       headers={}).status_code == 401
    assert client.get(f"/robots/{u['id']}", headers={}).status_code == 401
