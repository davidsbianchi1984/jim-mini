"""Life layer: sources/consent, context insights, check-ins, goals, habits,
coach, and erasure."""

from datetime import date, timedelta

from jim.tests.conftest import enroll


def test_context_requires_source_consent(client):
    user = enroll(client)
    r = client.post(f"/context/{user}", json={
        "source": "spending", "kind": "transaction", "data": {"amount": 250}})
    assert r.status_code == 403

    client.put(f"/sources/{user}", json={"source": "spending", "consented": True})
    r = client.post(f"/context/{user}", json={
        "source": "spending", "kind": "transaction", "data": {"amount": 250}})
    assert r.status_code == 201
    assert client.get(f"/sources/{user}").json() == [
        {"source": "spending", "consented": True}]


def test_spending_alert_insight(client):
    user = enroll(client)
    client.put(f"/sources/{user}", json={"source": "spending", "consented": True})
    body = client.post(f"/context/{user}", json={
        "source": "spending", "kind": "transaction",
        "data": {"amount": 320, "category": "dining out"}}).json()
    assert len(body["insights"]) == 1
    assert body["insights"][0]["kind"] == "alert"
    assert "dining out" in body["insights"][0]["message"]
    # small purchases stay quiet
    quiet = client.post(f"/context/{user}", json={
        "source": "spending", "kind": "transaction", "data": {"amount": 12}}).json()
    assert quiet["insights"] == []


def test_sleep_and_calendar_insights(client):
    user = enroll(client)
    for source in ("wearable", "calendar"):
        client.put(f"/sources/{user}", json={"source": source, "consented": True})
    praise = client.post(f"/context/{user}", json={
        "source": "wearable", "kind": "sleep", "data": {"hours": 8}}).json()
    assert praise["insights"][0]["kind"] == "praise"

    tip = client.post(f"/context/{user}", json={
        "source": "calendar", "kind": "event",
        "data": {"title": "Interview — Acme", "time": "10AM"}}).json()
    assert tip["insights"][0]["area"] == "career"
    assert "10AM" in tip["insights"][0]["message"]


def test_budgeting_plans_speak_when_spending_crosses_them(client):
    """The financial brand card, made real: an AI companion that keeps
    spending aligned with *budgeting plans* — the user's own monthly limits,
    per category and overall — not just a hardcoded alarm."""
    user = enroll(client)
    client.put(f"/sources/{user}", json={"source": "spending", "consented": True})
    r = client.put(f"/budgets/{user}", json={"category": "groceries",
                                             "monthly_limit": 100})
    assert r.status_code == 200 and r.json()["standing"] == "on plan"
    client.put(f"/budgets/{user}", json={"monthly_limit": 500})   # overall

    # 85 of 100: heading past the plan, said with the days left.
    body = client.post(f"/context/{user}", json={
        "source": "spending", "kind": "transaction",
        "data": {"amount": 85, "category": "Groceries"}}).json()
    heads = [i for i in body["insights"] if i["source"] == "budget"]
    assert len(heads) == 1 and "85%" in heads[0]["message"]

    # 20 more crosses the plan itself — an alert, pointing at the coach.
    body = client.post(f"/context/{user}", json={
        "source": "spending", "kind": "transaction",
        "data": {"amount": 20, "category": "groceries"}}).json()
    past = [i for i in body["insights"] if i["source"] == "budget"]
    assert len(past) == 1 and past[0]["kind"] == "alert"
    assert "finance coach" in past[0]["message"]

    view = client.get(f"/budgets/{user}").json()
    by_cat = {b["category"]: b for b in view["budgets"]}
    assert by_cat["groceries"]["standing"] == "past the plan"
    assert by_cat["groceries"]["spent"] == 105
    # The overall plan saw both purchases and is quietly on plan.
    assert by_cat["*"]["spent"] == 105 and by_cat["*"]["standing"] == "on plan"

    assert client.delete(f"/budgets/{user}/groceries").json()["removed"] is True


def test_low_mood_checkin_nudges(client):
    user = enroll(client)
    body = client.post(f"/checkin/{user}", json={"mood": 2, "energy": 2}).json()
    assert any("mindful break" in i["message"] for i in body["insights"])
    fine = client.post(f"/checkin/{user}", json={"mood": 4}).json()
    assert fine["insights"] == []


def test_stress_rides_the_checkin_and_climbing_stress_speaks_up(client):
    """The field promise, second half: "track your mood AND stress levels
    over time". Stress is optional on every check-in, lands in the progress
    report's averages, and three climbing readings ending high produce a
    forecast that points at a concrete strategy — the guided calm sessions —
    not just the bad news."""
    user = enroll(client)
    body = client.post(f"/checkin/{user}", json={
        "mood": 4, "energy": 3, "stress": 2}).json()
    assert body["stress"] == 2 and body["insights"] == []

    client.post(f"/checkin/{user}", json={"mood": 4, "stress": 3})
    body = client.post(f"/checkin/{user}", json={"mood": 4, "stress": 5}).json()
    climbing = [i for i in body["insights"] if "climbing" in i["message"]]
    assert climbing and "box breathing" in climbing[0]["message"]

    report = client.get(f"/report/{user}").json()
    assert report["checkins"]["avg_stress"] == round((2 + 3 + 5) / 3, 2)


def test_a_stressless_checkin_stays_exactly_what_it_was(client):
    """Optional means optional: the old two-slider check-in, and DBs from
    before the column, keep working untouched."""
    user = enroll(client)
    body = client.post(f"/checkin/{user}", json={"mood": 4, "energy": 3}).json()
    assert body["stress"] is None
    assert client.get(f"/report/{user}").json()["checkins"]["avg_stress"] is None
    r = client.post(f"/checkin/{user}", json={"mood": 4, "stress": 9})
    assert r.status_code == 422


def test_crisis_note_in_checkin_escalates(client, mail_server):
    user = enroll(client, emergency_name="Ana", emergency_phone="+1 555 0100", emergency_email="ana@example.com",
                  contact_consent=True)
    body = client.post(f"/checkin/{user}", json={
        "mood": 1, "note": "I don't want to live"}).json()
    guardian = body["guardian"]
    assert guardian["detected"] is True
    assert guardian["severity"] == "critical"
    assert guardian["escalation"]["notified_emergency_contact"] is True


def test_goal_progress_and_completion(client):
    user = enroll(client)
    goal = client.post(f"/goals/{user}", json={
        "area": "finance", "title": "Save $1k emergency fund"}).json()
    half = client.patch(f"/goals/{user}/{goal['id']}", json={"progress": 0.5}).json()
    assert half["status"] == "active" and half["insights"] == []
    done = client.patch(f"/goals/{user}/{goal['id']}", json={"progress": 1}).json()
    assert done["status"] == "completed"
    assert done["insights"][0]["kind"] == "praise"


def test_habit_streaks_and_milestone(client):
    user = enroll(client)
    habit = client.post(f"/habits/{user}", json={"name": "Morning walk"}).json()
    start = date.today() - timedelta(days=6)
    for offset in range(6):
        r = client.post(f"/habits/{user}/{habit['id']}/log",
                        json={"day": (start + timedelta(days=offset)).isoformat()})
        assert r.json()["streak"] == offset + 1
        assert r.json()["insights"] == []
    seventh = client.post(f"/habits/{user}/{habit['id']}/log",
                          json={"day": date.today().isoformat()}).json()
    assert seventh["streak"] == 7
    assert seventh["insights"][0]["kind"] == "milestone"
    assert client.get(f"/habits/{user}").json()[0]["streak"] == 7


def test_streak_breaks_on_gap(client):
    user = enroll(client)
    habit = client.post(f"/habits/{user}", json={"name": "Journal"}).json()
    today = date.today()
    for day in (today - timedelta(days=3), today - timedelta(days=1), today):
        client.post(f"/habits/{user}/{habit['id']}/log", json={"day": day.isoformat()})
    assert client.get(f"/habits/{user}").json()[0]["streak"] == 2


def test_coach_reply_uses_context(client):
    user = enroll(client)
    client.post(f"/checkin/{user}", json={"mood": 3, "energy": 4})
    body = client.post(f"/coach/{user}", json={
        "area": "career", "message": "How do I prep for tomorrow's interview?"}).json()
    assert body["delivered"] is True
    assert body["content"]                      # stub answers offline
    history = client.get(f"/coach/{user}", params={"area": "career"}).json()
    assert [m["role"] for m in history] == ["user", "coach"]


def test_delete_anything_anytime(client):
    user = enroll(client)
    client.put(f"/sources/{user}", json={"source": "wearable", "consented": True})
    client.post(f"/checkin/{user}", json={"mood": 2})
    client.post(f"/goals/{user}", json={"area": "career", "title": "x"})
    habit = client.post(f"/habits/{user}", json={"name": "x"}).json()
    client.post(f"/habits/{user}/{habit['id']}/log", json={})
    deleted = client.delete(f"/data/{user}").json()["deleted"]
    assert deleted["users"] == 1 and deleted["checkins"] == 1
    assert deleted["habit_logs"] == 1
    assert client.get(f"/events/{user}").status_code == 404
