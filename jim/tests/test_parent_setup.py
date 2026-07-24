"""Family: a parent sets up — and watches over — a child's account.
Consent is a recorded relationship, defaults are protective, oversight is
sized by age and ends at 18, and the auto-resuscitation waiver can never
be signed for a minor."""

from jim.tests.conftest import as_user, enroll


def _guardian(client, name="Morgan Reyes", birthdate="1985-04-04"):
    return enroll(client, display_name=name, birthdate=birthdate,
                  emergency_phone=None), name


def _child(client, gid, name="Riley Reyes", birthdate="2016-09-09", **extra):
    r = client.post(f"/guardians/{gid}/children",
                    json={"display_name": name, "birthdate": birthdate,
                          "guardian_phone": "+1 555 0100", **extra})
    assert r.status_code == 201, r.text
    return r.json()


def test_parent_led_setup_records_consent_and_protective_defaults(client):
    gid, gname = _guardian(client)
    child = _child(client, gid)
    assert child["guardian_consent"] == 1 or child["guardian_consent"] is True
    assert child["sensitivity"] == "cautious"
    assert child["oversight"] == "full"            # 8-year-old
    assert child["emergency_contact"] == gname
    assert child["cloud_contribution"] in (0, False)
    assert child["child_token"]

    # The consent is a recorded event on the child's timeline: who, as what.
    as_user(client, child["child_token"])
    events = client.get(f"/events/{child['id']}").json()
    consent = next(e for e in events if e["type"] == "guardian_consent")
    assert consent["detail"]["guardian_id"] == gid
    assert consent["detail"]["relationship"] == "parent"

    # The child token works like any user's for monitoring.
    r = client.post(f"/monitor/{child['id']}", json={"heart_rate": 96})
    assert r.status_code == 200


def test_only_a_verified_adult_enrolls_only_a_minor(client):
    minor_gid = enroll(client, display_name="Teen", birthdate="2010-01-01",
                       guardian_consent=True)
    r = client.post(f"/guardians/{minor_gid}/children",
                    json={"display_name": "Kid", "birthdate": "2018-01-01"})
    assert r.status_code == 403                    # minor guardian refused

    gid, _ = _guardian(client, name="Alex Adult")
    r = client.post(f"/guardians/{gid}/children",
                    json={"display_name": "Grown", "birthdate": "1990-01-01"})
    assert r.status_code == 422                    # adults enroll themselves
    assert "enrolls themselves" in r.json()["detail"]


def test_oversight_is_sized_by_age(client):
    gid, _ = _guardian(client)
    young = _child(client, gid, name="Riley", birthdate="2016-09-09")
    teen = _child(client, gid, name="Sam Reyes", birthdate="2010-02-02")
    kids = {k["display_name"]: k for k in
            client.get(f"/guardians/{gid}/children").json()}
    assert kids["Riley"]["oversight"] == "full"
    assert kids["Sam Reyes"]["oversight"] == "alerts_only"
    assert young["id"] != teen["id"]


def test_teen_privacy_keeps_daily_life_out_of_the_window(client):
    gid, _ = _guardian(client)
    guardian_token = client.headers["authorization"]
    teen = _child(client, gid, name="Sam Reyes", birthdate="2010-02-02")

    as_user(client, teen["child_token"])
    client.post(f"/checkin/{teen['id']}", json={"mood": 3,
                                                "note": "rough day at school"})
    client.post(f"/monitor/{teen['id']}",
                json={"note": "I don't want to live anymore"})

    client.headers["authorization"] = guardian_token
    window = client.get(f"/guardians/{gid}/children/{teen['id']}").json()
    assert window["oversight"] == "alerts_only"
    assert window["privacy_note"]
    types = {e["type"] for e in window["events"]}
    assert types == {"escalation"}                 # the crisis reaches the
    assert window["critical_events"] >= 1          # parent; the diary doesn't
    assert all("note" not in e for e in window["events"])

    # A young child's window is full — condition-level, still no raw notes.
    young = _child(client, gid, name="Riley", birthdate="2016-09-09")
    as_user(client, young["child_token"])
    client.post(f"/monitor/{young['id']}", json={"heart_rate": 96})
    client.headers["authorization"] = guardian_token
    window = client.get(f"/guardians/{gid}/children/{young['id']}").json()
    assert "biometric" in {e["type"] for e in window["events"]}


def test_oversight_ends_at_eighteen(client):
    gid, _ = _guardian(client)
    teen = _child(client, gid, name="Sam Reyes", birthdate="2010-02-02")
    from jim import db
    conn = db.connect()
    conn.execute("UPDATE users SET birthdate='2000-01-01' WHERE id=?",
                 (teen["id"],))
    conn.commit()
    kids = client.get(f"/guardians/{gid}/children").json()
    assert kids[0]["oversight"] == "ended"
    window = client.get(f"/guardians/{gid}/children/{teen['id']}").json()
    assert window["oversight"] == "ended" and "adult" in window["note"]
    assert "events" not in window                  # the window is closed


def test_the_waiver_is_never_signable_for_a_minor(client):
    gid, _ = _guardian(client)
    child = _child(client, gid, name="Riley Reyes")
    # Not by the child's own token…
    as_user(client, child["child_token"])
    r = client.post(f"/waivers/{child['id']}",
                    json={"signature": "Riley Reyes", "accept": True})
    assert r.status_code == 403 and "never" in r.json()["detail"]
    # …and there is no guardian route around it: the same user record is
    # the gate, whoever holds a token.


def test_unlink_closes_the_window_but_keeps_the_account(client):
    gid, _ = _guardian(client)
    child = _child(client, gid)
    assert client.delete(
        f"/guardians/{gid}/children/{child['id']}").json()["linked"] is False
    assert client.get(f"/guardians/{gid}/children").json() == []
    assert client.get(
        f"/guardians/{gid}/children/{child['id']}").status_code == 404
    # The child account still works.
    as_user(client, child["child_token"])
    assert client.post(f"/monitor/{child['id']}",
                       json={"heart_rate": 92}).status_code == 200
