"""Family controls: guardian pause & quiet hours (safety never pauses),
the parent's watch face with per-child lights, and the consent record
sealed in the PDI vault when one is configured."""

import json

from jim.tests.conftest import as_user, enroll
from jim.tests.test_pdi_tandem import pdi_pair  # noqa: F401 (fixture)


def _family(client, child_birthdate="2016-09-09"):
    gid = enroll(client, display_name="Morgan Reyes", birthdate="1985-04-04")
    guardian_token = client.headers["authorization"]
    child = client.post(f"/guardians/{gid}/children",
                        json={"display_name": "Riley Reyes",
                              "birthdate": child_birthdate,
                              "guardian_phone": "+1 555 0100"}).json()
    return gid, guardian_token, child


def test_pause_holds_guidance_but_never_safety(client):
    gid, guardian_token, child = _family(client)
    r = client.put(f"/guardians/{gid}/children/{child['id']}/controls",
                   json={"paused": True})
    assert r.status_code == 200 and r.json()["paused"] is True

    as_user(client, child["child_token"])
    # An everyday detection: guidance is held, the detection still lands.
    body = client.post(f"/monitor/{child['id']}",
                       json={"note": "so stressed about the deadline"}).json()
    assert body["detected"] is True
    assert body["guidance"]["held"] is True
    assert "guardian pause" in body["guidance"]["note"]
    types = [e["type"] for e in client.get(f"/events/{child['id']}").json()]
    assert "guidance_held" in types and "detection" in types

    # A crisis never checks the hold: full guidance and escalation.
    body = client.post(f"/monitor/{child['id']}",
                       json={"note": "I don't want to live anymore"}).json()
    assert body["severity"] == "critical"
    assert body["guidance"]["delivered"] is True
    assert body["escalation"]["escalated"] is True


def test_quiet_hours_hold_and_release(client):
    from datetime import datetime, timedelta

    gid, guardian_token, child = _family(client)
    now = datetime.now()
    inside = ((now - timedelta(hours=1)).strftime("%H:%M"),
              (now + timedelta(hours=1)).strftime("%H:%M"))
    client.put(f"/guardians/{gid}/children/{child['id']}/controls",
               json={"quiet_start": inside[0], "quiet_end": inside[1]})
    as_user(client, child["child_token"])
    body = client.post(f"/monitor/{child['id']}",
                       json={"note": "so stressed about the deadline"}).json()
    assert body["guidance"]["held"] is True
    assert "quiet hours" in body["guidance"]["note"]

    # Move the window elsewhere: guidance flows again.
    client.headers["authorization"] = guardian_token
    outside = ((now + timedelta(hours=2)).strftime("%H:%M"),
               (now + timedelta(hours=3)).strftime("%H:%M"))
    client.put(f"/guardians/{gid}/children/{child['id']}/controls",
               json={"quiet_start": outside[0], "quiet_end": outside[1]})
    as_user(client, child["child_token"])
    body = client.post(f"/monitor/{child['id']}",
                       json={"note": "so stressed about the deadline"}).json()
    assert body["guidance"].get("held") is None
    assert body["guidance"]["delivered"] is True


def test_guardian_watch_lights_and_haptic(client):
    gid, guardian_token, child = _family(client)
    teen = client.post(f"/guardians/{gid}/children",
                       json={"display_name": "Sam Reyes",
                             "birthdate": "2010-02-02",
                             "guardian_phone": "+1 555 0100"}).json()

    face = client.get(f"/guardians/{gid}/watch").json()
    assert all(c["light"] == "green" for c in face["children"])
    assert face["haptic"] is None

    # The teen hits a crisis: their light goes red, the wrist taps.
    as_user(client, teen["child_token"])
    client.post(f"/monitor/{teen['id']}",
                json={"note": "I don't want to live anymore"})
    client.headers["authorization"] = guardian_token
    client.put(f"/guardians/{gid}/children/{child['id']}/controls",
               json={"paused": True})
    face = client.get(f"/guardians/{gid}/watch").json()
    lights = {c["display_name"]: c for c in face["children"]}
    assert lights["Sam Reyes"]["light"] == "red"
    assert lights["Sam Reyes"]["critical_24h"] >= 1
    assert lights["Riley Reyes"]["light"] == "green"
    assert lights["Riley Reyes"]["paused"] is True
    assert face["haptic"] == "alert"


def test_consent_record_is_sealed_in_the_vault(pdi_pair):
    jim, fake = pdi_pair
    gid = enroll(jim, display_name="Morgan Reyes", birthdate="1985-04-04")
    child = jim.post(f"/guardians/{gid}/children",
                     json={"display_name": "Riley Reyes",
                           "birthdate": "2016-09-09"}).json()
    key = next(k for k in fake.store
               if k.startswith(f"jim/{child['id']}/family/consent/"))
    sealed = json.loads(fake.store[key])
    assert sealed["guardian_id"] == gid
    assert sealed["relationship"] == "parent"
    # Locally only the vault reference remains.
    as_user(jim, child["child_token"])
    events = jim.get(f"/events/{child['id']}").json()
    consent = next(e for e in events if e["type"] == "guardian_consent")
    assert consent["detail"] == {"vaulted": True, "pdi_key": key}
