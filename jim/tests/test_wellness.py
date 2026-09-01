"""Guided wellness — calm protocols, workout plans, meal plans: the
on-purpose half of guidance, deterministic where a generation would only
add risk.
"""

from jim.tests.conftest import enroll


def test_calm_catalog_is_public_and_sessions_are_protocols(client):
    kinds = {s["kind"] for s in client.get("/calm").json()["sessions"]}
    assert {"quick_reset", "box_breathing", "deep_breathing",
            "meditation"} <= kinds
    user = enroll(client)
    r = client.post(f"/calm/{user}/box_breathing")
    assert r.status_code == 201, r.text
    out = r.json()
    # Box breathing is 4-4-4-4 across four rounds — sixteen timed steps,
    # every count exactly four seconds. A protocol, not a generation.
    assert len(out["calm_steps"]) == 16
    assert all(s["seconds"] == 4 for s in out["calm_steps"])
    assert out["total_seconds"] == 64
    r = client.post(f"/calm/{user}/screaming")
    assert r.status_code == 422
    hist = client.get(f"/calm/{user}/history").json()
    assert len(hist) == 1 and hist[0]["kind"] == "box_breathing"


def test_workout_plans_adapt_to_minutes_and_level(client):
    user = enroll(client)
    quick = client.post(f"/fitness/{user}/plan", json={
        "minutes": 10, "level": "beginner", "focus": "full_body"}).json()
    full = client.post(f"/fitness/{user}/plan", json={
        "minutes": 45, "level": "advanced", "focus": "cardio"}).json()
    # Warm-up and cool-down are non-negotiable on both.
    for p in (quick, full):
        assert p["blocks"][0]["name"] == "Warm-up"
        assert p["blocks"][-1]["name"] == "Cool-down"
    # More minutes buys more working blocks; the level scales the doses.
    assert len(full["blocks"]) > len(quick["blocks"])
    assert full["blocks"][1]["seconds"] > quick["blocks"][1]["seconds"]
    # Refusals a person can read.
    r = client.post(f"/fitness/{user}/plan", json={
        "minutes": 10, "level": "olympian", "focus": "cardio"})
    assert r.status_code == 422
    r = client.post(f"/fitness/{user}/plan", json={
        "minutes": 300, "level": "beginner", "focus": "cardio"})
    assert r.status_code == 422


def test_meal_plans_respect_preferences_and_goals(client):
    user = enroll(client)
    vegan = client.post(f"/nutrition/{user}/plan", json={
        "goal": "eat_healthier", "preferences": ["vegan"],
        "days": 3}).json()
    for day in vegan["days"]:
        for meal in day["meals"]:
            name = meal["name"].lower()
            for word in ("chicken", "salmon", "tuna", "turkey", "yogurt",
                         "feta", "cottage", "egg", "omelette"):
                assert word not in name, (word, name)
    assert "not medical nutrition therapy" in vegan["disclaimer"]

    muscle = client.post(f"/nutrition/{user}/plan", json={
        "goal": "gain_muscle"}).json()
    assert muscle["shape"]["meals_per_day"] == 4

    r = client.post(f"/nutrition/{user}/plan", json={"goal": "get_swole"})
    assert r.status_code == 422
    r = client.post(f"/nutrition/{user}/plan", json={
        "goal": "eat_healthier", "preferences": ["carnivore"]})
    assert r.status_code == 422


def test_the_coach_speaks_nutrition_as_its_own_area(client):
    user = enroll(client)
    r = client.post(f"/coach/{user}", json={
        "area": "nutrition", "message": "help me plan better lunches"})
    assert r.status_code == 200, r.text
