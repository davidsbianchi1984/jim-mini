"""Predictive early warnings beyond the heart-rate climb: a sliding mood,
accumulating sleep debt, and accelerating spending — each flagged before it
becomes a crisis, from bare local numbers (payloads stay in the vault)."""

from jim.tests.conftest import enroll


def _allow(client, uid, source):
    client.put(f"/sources/{uid}", json={"source": source, "consented": True})


def test_sliding_mood_is_forecast(client):
    uid = enroll(client)
    for mood in (5, 4, 3):                     # strictly declining, ending low
        r = client.post(f"/checkin/{uid}", json={"mood": mood}).json()
    forecasts = [i for i in r["insights"] if i["kind"] == "forecast"]
    assert len(forecasts) == 1
    assert "sliding" in forecasts[0]["message"]
    assert forecasts[0]["area"] == "mental_health"


def test_stable_mood_is_not_forecast(client):
    uid = enroll(client)
    for mood in (4, 4, 3):                     # not strictly declining
        r = client.post(f"/checkin/{uid}", json={"mood": mood}).json()
    assert all(i["kind"] != "forecast" for i in r["insights"])


def test_sleep_debt_accumulates_into_a_forecast(client):
    uid = enroll(client)
    _allow(client, uid, "health")
    for hours in (6, 5.5, 5):                  # three short nights
        r = client.post(f"/context/{uid}", json={
            "source": "health", "kind": "sleep",
            "data": {"hours": hours}}).json()
    forecasts = [i for i in r["insights"] if i["kind"] == "forecast"]
    assert len(forecasts) == 1
    assert "sleep debt" in forecasts[0]["message"]
    # One good night breaks the streak — no forecast.
    good = client.post(f"/context/{uid}", json={
        "source": "health", "kind": "sleep", "data": {"hours": 8}}).json()
    assert all(i["kind"] != "forecast" for i in good["insights"])


def test_spending_acceleration_is_forecast_below_the_alert_bar(client):
    uid = enroll(client)
    _allow(client, uid, "spending")
    # Six purchases, all below the single-purchase alert threshold; the last
    # three together are more than double the prior three.
    r = None
    for amount in (20, 25, 30, 60, 70, 80):
        r = client.post(f"/context/{uid}", json={
            "source": "spending", "kind": "transaction",
            "data": {"amount": amount, "category": "coffee"}}).json()
    kinds = [i["kind"] for i in r["insights"]]
    assert "forecast" in kinds and "alert" not in kinds
    forecast = next(i for i in r["insights"] if i["kind"] == "forecast")
    assert "accelerating" in forecast["message"]


def test_forecast_data_is_numbers_only_and_erased(client):
    from jim import db
    uid = enroll(client)
    _allow(client, uid, "spending")
    client.post(f"/context/{uid}", json={
        "source": "spending", "kind": "transaction",
        "data": {"amount": 42, "category": "secret hobby"}}).json()
    rows = [dict(r) for r in db.connect().execute(
        "SELECT * FROM trend_points WHERE user_id=?", (uid,)).fetchall()]
    # Only a metric name and a number — no category or payload survives.
    assert rows[0]["metric"] == "spend_amount" and rows[0]["value"] == 42
    assert "secret hobby" not in str(rows)
    # Erasure removes trend points (and baselines) with everything else.
    deleted = client.delete(f"/data/{uid}").json()["deleted"]
    assert deleted["trend_points"] == 1
    assert "baselines" in deleted
