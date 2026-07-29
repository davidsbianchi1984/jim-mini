"""The Apple Watch bridge: the Shortcuts drip and the Health-export seed.

The bridge exists because HealthKit only talks to App-Store apps and JIM
does not have one. The two properties under test everywhere here: the drip
token can deposit readings but never read anything out, and history seeds
baselines without raising a single check-in — enrollment day is quiet.
"""

from __future__ import annotations

import io
import zipfile

from jim import db, guardian, watch


def _enroll(client, name="Dana"):
    r = client.post("/enroll", json={
        "display_name": name, "birthdate": "1990-01-01",
        "terms_consent": True, "resting_heart_rate": 60})
    assert r.status_code == 201
    return r.json()


def _auth(u):
    return {"authorization": f"Bearer {u['user_token']}"}


def _drip_url(client, u):
    r = client.get(f"/watch/channel/{u['id']}", headers=_auth(u))
    assert r.status_code == 200
    return "/watch/drip/" + r.json()["drip_url"].rsplit("/", 1)[1]


def _record(hk_type, value, day, unit="count/min", metadata=""):
    return (f'<Record type="{hk_type}" value="{value}" unit="{unit}" '
            f'startDate="{day} 08:00:00 -0500" '
            f'endDate="{day} 08:00:00 -0500">{metadata}</Record>')


def _export(*records):
    return ("<HealthData locale=\"en_US\">" + "".join(records)
            + "</HealthData>").encode()


_SEDENTARY = ('<MetadataEntry key="HKMetadataKeyHeartRateMotionContext" '
              'value="1"/>')
_ACTIVE = ('<MetadataEntry key="HKMetadataKeyHeartRateMotionContext" '
           'value="2"/>')


# ---------------------------------------------------------------------------
# The channel

def test_the_channel_is_minted_once_and_stable(client):
    u = _enroll(client)
    first = client.get(f"/watch/channel/{u['id']}", headers=_auth(u)).json()
    second = client.get(f"/watch/channel/{u['id']}", headers=_auth(u)).json()
    assert first["drip_url"] == second["drip_url"]
    assert "/watch/drip/" in first["drip_url"]
    assert first["shortcut"]        # the recipe ships with the card


def test_rotate_retires_the_old_address(client):
    u = _enroll(client)
    old = _drip_url(client, u)
    rotated = client.post(f"/watch/channel/{u['id']}/rotate",
                          headers=_auth(u))
    assert rotated.status_code == 200
    new = "/watch/drip/" + rotated.json()["drip_url"].rsplit("/", 1)[1]
    assert new != old
    assert client.post(old, json={"heart_rate": 62}).status_code == 404
    assert client.post(new, json={"heart_rate": 62}).status_code == 200


def test_the_setup_card_requires_the_users_own_token(client):
    u, other = _enroll(client), _enroll(client, "Robin")
    r = client.get(f"/watch/channel/{u['id']}", headers=_auth(other))
    assert r.status_code in (401, 403)


def test_a_wrong_token_is_a_404_not_a_403(client):
    _enroll(client)
    r = client.post("/watch/drip/not-a-real-token", json={"heart_rate": 60})
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# The drip

def test_a_drip_lands_as_a_biometric_event(client):
    u = _enroll(client)
    r = client.post(_drip_url(client, u), json={"heart_rate": 62})
    assert r.status_code == 200
    assert r.json()["received"] == 1
    events = client.get(f"/events/{u['id']}", headers=_auth(u)).json()
    assert any(e["type"] == "biometric" for e in events)


def test_the_drip_reply_carries_no_guidance_or_identity(client):
    """The token is a URL-bearer credential: deposit-only. The full monitor
    response (guidance, escalation, drift detail) must not come back."""
    u = _enroll(client)
    body = client.post(_drip_url(client, u),
                       json={"heart_rate": 62, "blood_oxygen": 97}).json()
    assert set(body) == {"received", "noticed"}


def test_shortcuts_spellings_and_unit_strings_are_understood(client):
    u = _enroll(client)
    r = client.post(_drip_url(client, u), json={
        "heartRate": "71 count/min", "SpO2": 0.97, "Temperature": "98.6 degF"})
    assert r.status_code == 200
    assert r.json()["received"] == 1
    row = db.connect().execute(
        "SELECT detail FROM events WHERE user_id=? AND type='biometric'",
        (u["id"],)).fetchone()
    import json
    detail = json.loads(row["detail"])
    assert detail["heart_rate"] == 71.0
    assert detail["blood_oxygen"] == 97.0      # fraction became a percent
    assert abs(detail["body_temperature"] - 37.0) < 0.1   # degF became degC


def test_a_batch_of_samples_is_counted(client):
    u = _enroll(client)
    r = client.post(_drip_url(client, u), json={"samples": [
        {"heart_rate": 61}, {"heart_rate": 63}, {"heart_rate": 62}]})
    assert r.json()["received"] == 3


def test_an_unrecognizable_payload_is_a_422_with_help(client):
    u = _enroll(client)
    r = client.post(_drip_url(client, u), json={"steps": 4000})
    assert r.status_code == 422
    assert "heart_rate" in r.json()["detail"]


def test_the_drip_feeds_the_baseline(client):
    u = _enroll(client)
    url = _drip_url(client, u)
    for _ in range(6):
        client.post(url, json={"heart_rate": 60, "activity_level": 0})
    metrics = {b["metric"]: b for b in guardian.baseline_for(u["id"])}
    assert metrics["heart_rate"]["samples"] >= 6


def test_an_alarming_drip_is_noticed_but_not_narrated(client):
    u = _enroll(client)
    r = client.post(_drip_url(client, u), json={
        "heart_rate": 130, "respiratory_rate": 28})
    assert r.json()["noticed"] is True
    assert "guidance" not in r.json()


# ---------------------------------------------------------------------------
# The seed

def test_the_export_seeds_baselines_without_a_single_event(client):
    u = _enroll(client)
    xml = _export(*[
        _record("HKQuantityTypeIdentifierRestingHeartRate", 58 + (i % 2),
                f"2026-06-{i:02d}") for i in range(1, 11)])
    before = len(client.get(f"/events/{u['id']}", headers=_auth(u)).json())
    r = client.post(f"/watch/seed/{u['id']}", headers=_auth(u), content=xml)
    assert r.status_code == 200
    report = r.json()["seeded"]["resting_heart_rate"]
    assert report["days"] == 10
    assert report["provisional"] is False      # ten days beats five samples
    assert abs(report["baseline"] - 58.5) < 1.0
    after = len(client.get(f"/events/{u['id']}", headers=_auth(u)).json())
    assert after == before                     # history is context, not news


def test_a_day_of_readings_folds_once_as_its_median(client):
    u = _enroll(client)
    xml = _export(
        _record("HKQuantityTypeIdentifierRespiratoryRate", 14, "2026-06-01"),
        _record("HKQuantityTypeIdentifierRespiratoryRate", 15, "2026-06-01"),
        _record("HKQuantityTypeIdentifierRespiratoryRate", 90, "2026-06-01"))
    client.post(f"/watch/seed/{u['id']}", headers=_auth(u), content=xml)
    metrics = {b["metric"]: b for b in guardian.baseline_for(u["id"])}
    assert metrics["respiratory_rate"]["samples"] == 1
    assert metrics["respiratory_rate"]["value"] == 15.0   # the median held


def test_exercise_heart_rate_never_reaches_the_resting_baseline(client):
    u = _enroll(client)
    xml = _export(
        _record("HKQuantityTypeIdentifierHeartRate", 62, "2026-06-01",
                metadata=_SEDENTARY),
        _record("HKQuantityTypeIdentifierHeartRate", 155, "2026-06-01",
                metadata=_ACTIVE),
        _record("HKQuantityTypeIdentifierHeartRate", 148, "2026-06-01"))
    client.post(f"/watch/seed/{u['id']}", headers=_auth(u), content=xml)
    metrics = {b["metric"]: b for b in guardian.baseline_for(u["id"])}
    # enrollment seeded the row; the only *fold* is the sedentary 62
    assert metrics["heart_rate"]["value"] <= 62.0


def test_oxygen_fraction_and_degf_are_converted(client):
    u = _enroll(client)
    xml = _export(
        _record("HKQuantityTypeIdentifierOxygenSaturation", 0.97,
                "2026-06-01", unit="%"),
        _record("HKQuantityTypeIdentifierBodyTemperature", 98.6,
                "2026-06-01", unit="degF"))
    client.post(f"/watch/seed/{u['id']}", headers=_auth(u), content=xml)
    metrics = {b["metric"]: b for b in guardian.baseline_for(u["id"])}
    assert metrics["blood_oxygen"]["value"] == 97.0
    assert abs(metrics["body_temperature"]["value"] - 37.0) < 0.1


def test_the_seed_accepts_the_zip_the_health_app_actually_makes(client):
    u = _enroll(client)
    xml = _export(_record("HKQuantityTypeIdentifierHeartRateVariabilitySDNN",
                          45, "2026-06-01", unit="ms"))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("apple_health_export/export.xml", xml)
        zf.writestr("apple_health_export/export_cda.xml", "<ClinicalDocument/>")
    r = client.post(f"/watch/seed/{u['id']}", headers=_auth(u),
                    content=buf.getvalue())
    assert r.status_code == 200
    assert "hrv" in r.json()["seeded"]


def test_a_non_export_upload_is_refused_kindly(client):
    u = _enroll(client)
    r = client.post(f"/watch/seed/{u['id']}", headers=_auth(u),
                    content=b"not xml at all")
    assert r.status_code == 422
    assert "Health" in r.json()["detail"]


def test_the_seed_requires_the_users_own_token(client):
    u, other = _enroll(client), _enroll(client, "Robin")
    xml = _export(_record("HKQuantityTypeIdentifierRestingHeartRate", 58,
                          "2026-06-01"))
    r = client.post(f"/watch/seed/{u['id']}", headers=_auth(other),
                    content=xml)
    assert r.status_code in (401, 403)


def test_seeded_history_arms_the_drift_bands(client):
    """The whole point: a tester uploads months of history and the bands are
    armed the same day, instead of five quiet days of 'learning'."""
    u = _enroll(client)
    xml = _export(*[
        _record("HKQuantityTypeIdentifierHeartRateVariabilitySDNN", 45,
                f"2026-06-{i:02d}", unit="ms") for i in range(1, 9)])
    client.post(f"/watch/seed/{u['id']}", headers=_auth(u), content=xml)
    crossings = watch.drip(watch.channel(u["id"])["token"], {"hrv": 20})
    assert crossings["noticed"] is True        # the drop from 45 was seen
