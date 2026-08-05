"""The watch you actually wear: the picker behind the setup card.

The drip channel was never Apple-shaped — it is a URL that accepts
JSON — but the setup card only spoke iPhone, which meant a person with
a Pixel Watch or a Fitbit stood in front of instructions for a phone
they do not own. The card now asks what you wear and teaches that.

The properties under test: the device list ships with the card (so the
picker renders from the API and a new wearable is one dict entry); each
family's recipe speaks its own platform's truth; a wrong device is a
422 that names every right one; and Fitbit's Takeout export seeds the
same baselines Apple's export.xml does — months of history somebody's
wrist already recorded, regardless of whose logo is on it.
"""

from __future__ import annotations

import io
import json
import zipfile

from jim import guardian, watch

from .test_watch import _auth, _enroll


# ---------------------------------------------------------------------------
# The picker

def test_the_card_lists_every_wearable_it_can_teach(client):
    u = _enroll(client)
    card = client.get(f"/watch/channel/{u['id']}",
                      headers=_auth(u)).json()
    keys = {d["key"] for d in card["devices"]}
    assert {"apple_watch", "wear_os", "fitbit", "garmin"} <= keys
    # Names are for humans; every entry has one.
    assert all(d["name"] for d in card["devices"])
    # The default is what shipped first, so nothing that learned the old
    # card breaks — and `shortcut` still names the same steps.
    assert card["device"] == "apple_watch"
    assert card["steps"] == card["shortcut"]


def test_each_family_gets_its_own_platforms_truth(client):
    u = _enroll(client)

    def steps(device):
        r = client.get(f"/watch/channel/{u['id']}",
                       params={"device": device}, headers=_auth(u))
        assert r.status_code == 200, r.text
        body = r.json()
        assert body["device"] == device
        return " ".join(body["steps"]) + " " + body["seed_hint"]

    assert "Shortcuts" in steps("apple_watch")
    assert "Health Connect" in steps("wear_os")
    assert "Takeout" in steps("fitbit")
    # Garmin's hint is honest that its export is not parseable here yet,
    # rather than promising an upload that would be refused.
    assert "not parseable here yet" in steps("garmin")


def test_a_wrong_device_names_every_right_one(client):
    u = _enroll(client)
    r = client.get(f"/watch/channel/{u['id']}",
                   params={"device": "pebble"}, headers=_auth(u))
    assert r.status_code == 422
    for key in watch.DEVICES:
        assert key in r.json()["message"]


def test_the_drip_does_not_care_whose_logo_is_on_the_wrist(client):
    """The channel is one URL for every family — the picker changes the
    instructions, never the address or the pipeline behind it."""
    u = _enroll(client)
    apple = client.get(f"/watch/channel/{u['id']}",
                       headers=_auth(u)).json()
    wear = client.get(f"/watch/channel/{u['id']}",
                      params={"device": "wear_os"},
                      headers=_auth(u)).json()
    assert apple["drip_url"] == wear["drip_url"]


# ---------------------------------------------------------------------------
# The Fitbit seed

def _takeout(*files):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        for name, payload in files:
            zf.writestr(f"Takeout/Fitbit/Global Export Data/{name}",
                        payload)
    return buffer.getvalue()


def test_a_fitbit_takeout_zip_seeds_the_resting_baseline(client):
    u = _enroll(client)
    rows = [{"dateTime": f"01/{day:02d}/24 00:00:00",
             "value": {"date": f"01/{day:02d}/24", "value": 62.0 + day,
                       "error": 6.0}}
            for day in (1, 2, 3)]
    data = _takeout(("resting_heart_rate-2024-01-01.json",
                     json.dumps(rows)))
    r = client.post(f"/watch/seed/{u['id']}", headers=_auth(u),
                    content=data)
    assert r.status_code == 200, r.text
    seeded = r.json()["seeded"]["resting_heart_rate"]
    assert seeded["days"] == 3
    # The baseline moved off enrollment's 60 toward the history.
    metrics = {b["metric"]: b for b in guardian.baseline_for(u["id"])}
    assert metrics["resting_heart_rate"]["value"] > 60


def test_fitbit_hrv_summaries_fold_and_the_raw_stream_does_not(client):
    """The continuous heart_rate stream includes exercise; folding it
    would teach the resting baseline a workout — the same mistake the
    Apple path's sedentary filter exists to prevent."""
    u = _enroll(client)
    hrv = ("timestamp,rmssd,coverage,low_frequency,high_frequency\n"
           "2024-01-01T00:00:00,45.5,0.9,500,300\n"
           "2024-01-02T00:00:00,47.1,0.9,510,290\n")
    racing = json.dumps([{"dateTime": "01/01/24 10:00:00",
                          "value": {"bpm": 165, "confidence": 3}}])
    data = _takeout(
        ("daily_heart_rate_variability_summary-2024-01-01.csv", hrv),
        ("heart_rate-2024-01-01.json", racing))
    r = client.post(f"/watch/seed/{u['id']}", headers=_auth(u),
                    content=data)
    assert r.status_code == 200, r.text
    seeded = r.json()["seeded"]
    assert seeded["hrv"]["days"] == 2
    # The 165bpm workout reading reached no baseline: not as heart_rate,
    # and not smuggled in as resting either — enrollment's heart_rate row
    # still stands at 60 with zero folds.
    assert "heart_rate" not in seeded
    assert "resting_heart_rate" not in seeded
    metrics = {b["metric"]: b for b in guardian.baseline_for(u["id"])}
    assert metrics["heart_rate"]["samples"] == 0
    assert metrics["heart_rate"]["value"] == 60.0


def test_a_zip_that_is_neither_apple_nor_fitbit_is_refused_kindly(client):
    u = _enroll(client)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as zf:
        zf.writestr("holiday_photos/beach.txt", "not health data")
    r = client.post(f"/watch/seed/{u['id']}", headers=_auth(u),
                    content=buffer.getvalue())
    assert r.status_code == 422
    said = r.json()["message"]
    assert "export.xml" in said and "Fitbit" in said
