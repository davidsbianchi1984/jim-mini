"""Care beacons and the workplace relay.

Three claims carry this feature, and most of what follows is an attempt to
break one:

* **A beacon publishes watch status, never subject status.** So the tests read
  the whole stage-one card as one string and look for the birthdate, the
  contact number, the placement note and the label in it, rather than checking
  the handful of fields somebody remembered to omit.
* **A stranger's tap can never dispatch an ambulance.** So the tests push a
  ``critical`` alarm — which bases at ``emergency_services`` — through the
  ceiling and assert where it lands.
* **The relay sees the incident, never the person.** Same whole-string check,
  against the payload the roster would be handed.
"""

import json

import pytest

from jim import beacons, escalation, relay


def _adult(client, name="Ada Byron", **extra):
    # Basic rather than the free default: two tests below enrol a child, and a
    # child's record does not go in the open store. See jim/storage.py.
    body = {"display_name": name, "birthdate": "1970-04-02",
            "terms_consent": True, "resting_heart_rate": 60,
            "emergency_name": "Kin", "emergency_phone": "+15555550123",
            "contact_consent": True, "plan": "basic"}
    body.update(extra)
    r = client.post("/enroll", json=body, headers={})
    assert r.status_code == 201, r.text
    return r.json()


def _auth(tok):
    return {"Authorization": f"Bearer {tok}"}


def _place(client, uid, tok, **body):
    body.setdefault("label", "fridge door")
    r = client.post(f"/users/{uid}/beacons", json=body, headers=_auth(tok))
    assert r.status_code == 201, r.text
    return r.json()


# --- stage one: what a stranger sees before doing anything ----------------

def test_the_card_names_a_person_and_says_nothing_about_them(client):
    u = _adult(client)
    b = _place(client, u["id"], u["user_token"],
               label="fridge door", placement="kitchen, ground floor")

    card = client.get(f"/c/{b['id']}/card").json()
    assert card["first_name"] == "Ada"       # enough to speak to them
    assert card["watched"] is True
    assert card["status"] is None            # never how they are
    assert card["location"] is None          # never where they are
    assert "did not call for help" in card["badge"]

    # The whole card, not three chosen fields: nothing in it is about them.
    blob = json.dumps(card).lower()
    for leak in ("1970", "byron", "5555550123", "kin", "kitchen", "fridge"):
        assert leak not in blob, f"the card leaked {leak!r}"


def test_the_badge_is_a_claim_rather_than_a_silence(client):
    """The worst failure this feature has is somebody walking away believing
    the QR handled it, so the page says so before the tap and after it."""
    u = _adult(client)
    b = _place(client, u["id"], u["user_token"])
    assert client.get(f"/c/{b['id']}/card").json()["badge"] == beacons.BADGE_BEFORE
    raised = client.post(f"/c/{b['id']}/alarm", json={}).json()
    assert raised["badge"] == beacons.BADGE_AFTER
    assert "not an emergency service" in raised["badge"]


def test_scans_are_counted_for_the_owner(client):
    u = _adult(client)
    b = _place(client, u["id"], u["user_token"])
    for _ in range(3):
        client.get(f"/c/{b['id']}/card")
    mine = client.get(f"/users/{u['id']}/beacons",
                      headers=_auth(u["user_token"])).json()
    assert mine[0]["scans"] == 3


def test_a_retired_code_is_indistinguishable_from_one_that_never_existed(client):
    u = _adult(client)
    b = _place(client, u["id"], u["user_token"])
    assert client.delete(f"/beacons/{b['id']}",
                         headers=_auth(u["user_token"])).status_code == 200

    retired = client.get(f"/c/{b['id']}/card")
    never = client.get("/c/cbn_neverexisted/card")
    assert retired.status_code == never.status_code == 404
    assert retired.json() == never.json()


# --- stage two: the alarm is what buys the Medical ID ---------------------

def test_raising_the_alarm_is_what_opens_the_medical_id(client):
    u = _adult(client, known_conditions=["anxiety"])
    b = _place(client, u["id"], u["user_token"])

    # Before: nothing clinical anywhere on the page.
    assert "medical_id" not in client.get(f"/c/{b['id']}/card").json()

    out = client.post(f"/c/{b['id']}/alarm",
                      json={"message": "collapsed in the hall"}).json()
    assert out["raised"] is True
    assert out["medical_id"] is not None
    assert out["medical_id"]["emergency_contact"]["phone"] == "+15555550123"


def test_an_alarm_cannot_dispatch_an_ambulance(client):
    """A critical severity bases at emergency_services. The ceiling is the
    only thing standing between an anonymous tap and a dispatch."""
    u = _adult(client)
    b = _place(client, u["id"], u["user_token"])
    out = client.post(f"/c/{b['id']}/alarm", json={}).json()

    assert out["tier"] == "notify_contact"
    assert out["tier"] != "emergency_services"
    # The need did not vanish — it moved to the person standing there.
    assert out["call_emergency_services_yourself"] is True


def test_the_second_finder_joins_rather_than_being_dropped(client):
    """A spammed alarm trains a family to ignore the one that matters — but
    two people finding the same casualty is the case this exists for."""
    u = _adult(client)
    b = _place(client, u["id"], u["user_token"])

    first = client.post(f"/c/{b['id']}/alarm", json={"message": "he's down"}).json()
    second = client.post(f"/c/{b['id']}/alarm",
                         json={"message": "ambulance called"}).json()

    assert second["joined_existing"] is True
    assert second["alarm"] == first["alarm"]

    alarms = client.get(f"/users/{u['id']}/alarms",
                        headers=_auth(u["user_token"])).json()
    assert len(alarms) == 1
    assert alarms[0]["alert_texts"] == ["he's down", "ambulance called"]


def test_an_alarm_lands_in_the_owners_event_timeline(client):
    u = _adult(client)
    b = _place(client, u["id"], u["user_token"])
    client.post(f"/c/{b['id']}/alarm", json={})

    events = client.get(f"/events/{u['id']}", headers=_auth(u["user_token"])).json()
    escalations = [e for e in events if e["type"] == "escalation"]
    assert escalations, "a beacon alarm is an escalation and belongs on the timeline"


def test_alarms_belong_to_the_person_they_are_about(client):
    mine = _adult(client, name="Mine")
    theirs = _adult(client, name="Theirs")
    b = _place(client, mine["id"], mine["user_token"])
    client.post(f"/c/{b['id']}/alarm", json={})

    r = client.get(f"/users/{mine['id']}/alarms",
                   headers=_auth(theirs["user_token"]))
    assert r.status_code == 403


def test_clearing_an_alarm_is_idempotent(client):
    u = _adult(client)
    b = _place(client, u["id"], u["user_token"])
    a = client.post(f"/c/{b['id']}/alarm", json={}).json()

    first = client.post(f"/users/{u['id']}/alarms/{a['alarm']}/clear",
                        headers=_auth(u["user_token"]))
    assert first.status_code == 200 and first.json()["state"] == "cleared"
    again = client.post(f"/users/{u['id']}/alarms/{a['alarm']}/clear",
                        headers=_auth(u["user_token"]))
    assert again.status_code == 404


# --- children --------------------------------------------------------------

def _child(client, parent):
    r = client.post(f"/guardians/{parent['id']}/children",
                    json={"display_name": "Sam Byron", "birthdate": "2015-06-01",
                          "guardian_phone": "+15555550999"},
                    headers=_auth(parent["user_token"]))
    assert r.status_code == 201, r.text
    return r.json()


def test_a_minors_beacon_is_placed_by_their_guardian(client):
    parent = _adult(client, name="Parent One")
    child = _child(client, parent)
    kid_id = child["id"]

    r = client.post(f"/users/{kid_id}/beacons", json={"label": "backpack"},
                    headers=_auth(parent["user_token"]))
    assert r.status_code == 201, r.text
    assert r.json()["user_id"] == kid_id


def test_a_minors_beacon_never_opens_the_clinical_stage(client):
    """A stranger holding a backpack does not get a child's medical history
    for tapping a button. The guardian is raised instead."""
    parent = _adult(client, name="Parent Two")
    child = _child(client, parent)
    kid_id = child["id"]
    b = client.post(f"/users/{kid_id}/beacons", json={"label": "backpack"},
                    headers=_auth(parent["user_token"])).json()

    out = client.post(f"/c/{b['id']}/alarm", json={"message": "lost child"}).json()
    assert out["raised"] is True
    assert out["minor"] is True
    assert out["medical_id"] is None
    assert out["routed_to"] == "guardian"

    # And the card before it was no more forthcoming.
    card = client.get(f"/c/{b['id']}/card").json()
    assert card["status"] is None and card["location"] is None


# --- the ceiling, as a unit -----------------------------------------------

def test_the_ceiling_is_the_only_rule_that_lowers_a_tier(client):
    high = escalation.decide("critical", "cautious", contactable=True)
    assert high["tier"] == "emergency_services"

    capped = escalation.decide("critical", "cautious", contactable=True,
                               ceiling="notify_contact")
    assert capped["tier"] == "notify_contact"
    assert capped["clipped_by_ceiling"] is True
    assert capped["call_emergency_services_yourself"] is True
    assert any("ceiling" in step for step in capped["path"])


def test_the_ceiling_binds_even_the_crisis_floor(client):
    """The hardest floor in the module, and the ceiling still holds — because
    the alternative is an anonymous tap dispatching an ambulance. The result
    says so out loud rather than quietly returning a lower tier."""
    capped = escalation.decide("critical", crisis=True, contactable=True,
                               ceiling="notify_contact")
    assert capped["tier"] == "notify_contact"
    assert capped["call_emergency_services"] is False
    assert capped["call_emergency_services_yourself"] is True


def test_without_a_ceiling_nothing_moved(client):
    """Regression: the ceiling is opt-in, and every existing caller passes
    none. Their behaviour must be byte-identical."""
    for sev in ("info", "guidance", "critical"):
        for sens in ("cautious", "balanced", "assertive"):
            d = escalation.decide(sev, sens, contactable=True)
            assert d["clipped_by_ceiling"] is False
            assert d["call_emergency_services_yourself"] is False
    assert escalation.decide("critical", contactable=True)["tier"] == \
        "emergency_services"


def test_the_ceiling_is_published_next_to_the_floors(client):
    """A user can see how their dial behaves before anything happens; the
    ceiling belongs in the same place, for the same reason."""
    u = _adult(client)
    body = client.get(f"/escalation-policy/{u['id']}",
                      headers=_auth(u["user_token"])).json()
    assert "anonymous_beacon_alarm" in body["ceilings"]
    assert "notify_contact" in body["ceilings"]["anonymous_beacon_alarm"]
    assert body["safety_floors"]["crisis_language"] == "emergency_services"


# --- the workplace relay ---------------------------------------------------

def test_a_personal_deployment_has_no_relay(client, monkeypatch):
    monkeypatch.delenv("JIM_SITE_ROSTER", raising=False)
    body = client.get("/relay/roster").json()
    assert body["configured"] is False
    assert body["ceiling"] == "notify_contact"
    # Unset is not broken — it is a home, where notify_contact is the answer.
    assert body["roster"] == list(relay.DEFAULT_ROSTER)


def test_the_relay_works_the_roster_in_order_and_does_not_repeat(client, monkeypatch):
    monkeypatch.setenv("JIM_SITE_ROSTER", "night-tech,supervisor,site-lead")
    u = _adult(client, name="Lone Worker")
    b = _place(client, u["id"], u["user_token"], label="plant room", kind="site")
    a = client.post(f"/c/{b['id']}/alarm", json={"message": "man down"}).json()
    A = _auth(u["user_token"])

    seen = []
    for _ in range(3):
        out = client.post(
            f"/users/{u['id']}/alarms/{a['alarm']}/escalate", headers=A).json()
        seen.append(out["notified"])
    assert seen == ["night-tech", "supervisor", "site-lead"]

    # Roster exhausted: not an error, not silent, and still no dispatch.
    out = client.post(f"/users/{u['id']}/alarms/{a['alarm']}/escalate",
                      headers=A).json()
    assert out["exhausted"] is True
    assert out["tried"] == seen
    assert out["call_emergency_services_yourself"] is True


def test_accepting_is_not_the_same_as_clearing(client, monkeypatch):
    """Accepting says somebody is coming; clearing says it is over.
    Conflating them is how an alarm gets marked handled by being seen."""
    monkeypatch.setenv("JIM_SITE_ROSTER", "night-tech")
    u = _adult(client, name="Lone Worker")
    b = _place(client, u["id"], u["user_token"], label="plant room", kind="site")
    a = client.post(f"/c/{b['id']}/alarm", json={}).json()
    A = _auth(u["user_token"])

    out = client.post(f"/users/{u['id']}/alarms/{a['alarm']}/accept",
                      json={"responder": "R. Okafor"}, headers=A).json()
    assert out["accepted_by"] == "R. Okafor"
    assert out["state"] == "open"

    alarms = client.get(f"/users/{u['id']}/alarms", headers=A).json()
    assert alarms[0]["state"] == "open"
    assert alarms[0]["accepted_by"] == "R. Okafor"


def test_an_anonymous_acceptance_is_refused(client, monkeypatch):
    monkeypatch.setenv("JIM_SITE_ROSTER", "night-tech")
    u = _adult(client, name="Lone Worker")
    b = _place(client, u["id"], u["user_token"], label="plant room", kind="site")
    a = client.post(f"/c/{b['id']}/alarm", json={}).json()

    r = client.post(f"/users/{u['id']}/alarms/{a['alarm']}/accept",
                    json={"responder": "   "}, headers=_auth(u["user_token"]))
    assert r.status_code == 422
    assert "needs a name" in r.text


def test_an_accepted_incident_leaves_the_queue(client, monkeypatch):
    monkeypatch.setenv("JIM_SITE_ROSTER", "night-tech")
    u = _adult(client, name="Lone Worker")
    b = _place(client, u["id"], u["user_token"], label="plant room", kind="site")
    a = client.post(f"/c/{b['id']}/alarm", json={}).json()
    A = _auth(u["user_token"])

    assert len(client.get(f"/users/{u['id']}/incidents", headers=A).json()) == 1
    client.post(f"/users/{u['id']}/alarms/{a['alarm']}/accept",
                json={"responder": "R. Okafor"}, headers=A)
    assert client.get(f"/users/{u['id']}/incidents", headers=A).json() == []


def test_the_incident_carries_nothing_about_the_worker(client, monkeypatch):
    """The employer bought the deployment. That does not entitle them to what
    is inside it — so the payload is built from the incident, not the person."""
    monkeypatch.setenv("JIM_SITE_ROSTER", "night-tech")
    u = _adult(client, name="Rosa Delgado", known_conditions=["anxiety"])
    b = _place(client, u["id"], u["user_token"], label="plant room", kind="site")
    client.post(f"/c/{b['id']}/alarm", json={"message": "man down in the plant room"})

    incidents = client.get(f"/users/{u['id']}/incidents",
                           headers=_auth(u["user_token"])).json()
    assert len(incidents) == 1
    assert incidents[0]["scope"] == "incident"

    blob = json.dumps(incidents[0]).lower()
    for leak in ("rosa", "delgado", "anxiety", "1970", "5555550123", u["id"]):
        assert leak not in blob, f"the incident leaked {leak!r}"


def test_a_personal_beacon_is_not_a_site_incident(client, monkeypatch):
    monkeypatch.setenv("JIM_SITE_ROSTER", "night-tech")
    u = _adult(client)
    home = _place(client, u["id"], u["user_token"], label="fridge")
    client.post(f"/c/{home['id']}/alarm", json={})
    assert client.get(f"/users/{u['id']}/incidents",
                      headers=_auth(u["user_token"])).json() == []


def test_guidance_falls_back_to_the_one_instruction_that_is_always_right(client):
    out = client.post("/alarms/alrm_x/guidance",
                      json={"question": "he is not responding"}).json()
    assert out["source"] == "local"
    assert "emergency number" in out["answer"]


def test_guidance_routes_through_qrme_when_tandem_is_configured(make_tandem,
                                                               monkeypatch):
    monkeypatch.setenv("JIM_SITE_FIRSTAID_PROFILE", "@dr_amara_osei")
    c = make_tandem()
    out = c.post("/alarms/alrm_x/guidance",
                 json={"question": "he is not responding"}).json()
    assert out["source"] == "qrme"
    assert out["ai"] is True
    assert "[QRME specialist]" in out["answer"]


# --- the page a phone actually opens ---------------------------------------

def test_the_scan_url_serves_a_page_not_json(client):
    """A QR is pointed at by a person holding a phone. It used to answer JSON
    and show a neighbour a wall of braces."""
    u = _adult(client)
    b = _place(client, u["id"], u["user_token"])

    page = client.get(f"/c/{b['id']}")
    assert page.status_code == 200
    assert page.headers["content-type"].startswith("text/html")
    assert "<!doctype html>" in page.text.lower()
    assert client.get(f"/c/{b['id']}/card").json()["beacon"] == b["id"]


def test_the_page_is_one_self_contained_document(client):
    """Somebody may be reading this kneeling next to a person on the floor,
    on cellular, from a cold start."""
    u = _adult(client)
    b = _place(client, u["id"], u["user_token"])
    html = client.get(f"/c/{b['id']}").text
    for external in ('src="http', 'href="http', "@import", "<link"):
        assert external not in html, f"page reaches out for {external!r}"


def test_the_page_carries_a_first_name_and_nothing_else_about_them(client):
    u = _adult(client, known_conditions=["anxiety"])
    b = _place(client, u["id"], u["user_token"],
               label="fridge door", placement="kitchen")

    html = client.get(f"/c/{b['id']}").text
    assert "Ada" in html
    for leak in ("byron", "1970", "5555550123", "kitchen", "fridge",
                 "anxiety"):
        assert leak not in html.lower(), f"the page leaked {leak!r}"


def test_the_medical_id_is_not_on_the_page_before_the_alarm(client):
    """It arrives in the alarm's own response, so there is nothing on the page
    to reveal early even by mistake.

    The *label* "MEDICAL ID" does appear — inside the script that builds stage
    two once the alarm returns. That scaffolding holds no data, and asserting
    against it would be testing the wrong thing. The claim is about the
    values.
    """
    u = _adult(client, known_conditions=["anxiety"], resting_heart_rate=58)
    b = _place(client, u["id"], u["user_token"])
    html = client.get(f"/c/{b['id']}").text

    for value in ("Ada Byron", "58 bpm", "anxiety", "+15555550123",
                  "Kin"):
        assert value not in html, f"stage one already carried {value!r}"


def test_the_page_tells_them_to_dial_before_it_offers_the_button(client):
    """The one mistake that matters here is somebody waiting for this page
    instead of calling, so the instruction comes first in the document."""
    u = _adult(client)
    b = _place(client, u["id"], u["user_token"])
    html = client.get(f"/c/{b['id']}").text
    assert html.index("call your local") < html.index("Raise the alarm")
    assert beacons.BADGE_BEFORE in html


def test_the_alarm_posts_to_a_relative_url(client):
    u = _adult(client)
    b = _place(client, u["id"], u["user_token"])
    html = client.get(f"/c/{b['id']}").text
    assert f'"/c/{b["id"]}/alarm"' in html
    assert "https://jim.app" not in html


def test_a_dead_code_renders_a_page_too(client):
    r = client.get("/c/cbn_neverexisted")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("text/html")
    assert "call your local emergency number" in r.text


def test_the_page_does_not_depend_on_an_animation_to_be_visible(client):
    u = _adult(client)
    b = _place(client, u["id"], u["user_token"])
    html = client.get(f"/c/{b['id']}").text
    assert "prefers-reduced-motion" in html
    assert "opacity:0" not in html.replace(" ", "")


# --- the page behind the sentence -----------------------------------------
#
# The finder's note used to be one unconditional claim — "the people watching
# over this person have been alerted" — capping a function that sent nothing
# to anyone. These tests hold the sentence to what actually happened.

def _mail_spy(monkeypatch):
    from jim import mailer
    sent: list[dict] = []

    def fake_deliver(to, subject, body):
        sent.append({"to": to, "subject": subject, "body": body})
        return "smtp"

    monkeypatch.setattr(mailer, "deliver", fake_deliver)
    monkeypatch.setattr(mailer, "configured_transport", lambda: "smtp")
    return sent


def test_a_phone_only_contact_makes_the_page_a_queued_row(client, monkeypatch):
    """`Kin` is a phone number, and this product sends mail. The sentence
    says no message went out, and the ledger records the attempt that could
    not be made — the row the morning most needs to see."""
    _mail_spy(monkeypatch)
    u = _adult(client)
    b = _place(client, u["id"], u["user_token"])
    r = client.post(f"/c/{b['id']}/alarm", json={"message": "on the floor"})
    assert r.status_code == 201
    body = r.json()
    assert body["message_sent"] is False
    assert "No message went out from this page" in body["note"]
    pages = client.get(f"/users/{u['id']}/pages",
                       headers=_auth(u["user_token"])).json()
    mine = [p for p in pages if p["alarm"] == body["alarm"]]
    assert len(mine) == 1
    assert mine[0]["responder"] == "Kin"
    assert mine[0]["state"] == "queued"


def test_an_armed_watch_makes_the_beacon_page_real(client, monkeypatch):
    """The trusted channel the user armed their crash watch with is the
    person they designated to be woken — a beacon alarm wakes them too."""
    from jim import crashwatch
    sent = _mail_spy(monkeypatch)
    u = _adult(client)
    crashwatch.arm(u["id"], "Rosa", "rosa@example.test")
    b = _place(client, u["id"], u["user_token"], label="front door")
    r = client.post(f"/c/{b['id']}/alarm", json={"message": "collapsed"})
    body = r.json()
    assert body["message_sent"] is True
    assert "A message has been sent" in body["note"]
    assert len(sent) == 1
    assert sent[0]["to"] == "rosa@example.test"
    assert "front door" in sent[0]["body"]
    pages = client.get(f"/users/{u['id']}/pages",
                       headers=_auth(u["user_token"])).json()
    mine = [p for p in pages if p["alarm"] == body["alarm"]]
    assert mine and mine[0]["state"] == "sent"


def test_the_stranger_is_never_told_who_was_woken(client, monkeypatch):
    """The name lives in the ledger, for the owner. A passer-by learns that
    a message went out, never to whom."""
    from jim import crashwatch
    _mail_spy(monkeypatch)
    u = _adult(client)
    crashwatch.arm(u["id"], "Rosa", "rosa@example.test")
    b = _place(client, u["id"], u["user_token"])
    r = client.post(f"/c/{b['id']}/alarm", json={"message": "hello"})
    assert "Rosa" not in json.dumps(r.json())
    assert "rosa@example.test" not in json.dumps(r.json())


def test_a_minors_alarm_mails_the_consent_inbox(client, monkeypatch):
    """A child's page goes to the guardian address that verified their
    consent — and the clinical stage stays shut exactly as before."""
    from jim import db
    sent = _mail_spy(monkeypatch)
    parent = _adult(client, name="Parent Page")
    child = _child(client, parent)
    conn = db.connect()
    conn.execute("UPDATE users SET guardian_email=? WHERE id=?",
                 ("parent@example.test", child["id"]))
    conn.commit()
    r = client.post(f"/users/{child['id']}/beacons", json={"label": "backpack"},
                    headers=_auth(parent["user_token"]))
    b = r.json()
    out = client.post(f"/c/{b['id']}/alarm", json={"message": "lost"}).json()
    assert out["message_sent"] is True
    assert "guardian has been sent a message" in out["note"]
    assert out["medical_id"] is None
    assert sent and sent[0]["to"] == "parent@example.test"


def test_a_second_finder_reads_what_actually_went_out(client, monkeypatch):
    """The cooldown coalesces the second press into the open alarm: one
    message per alarm, and the second finder's sentence reports the truth
    of the first send rather than a fresh claim."""
    from jim import crashwatch
    sent = _mail_spy(monkeypatch)
    u = _adult(client)
    crashwatch.arm(u["id"], "Rosa", "rosa@example.test")
    b = _place(client, u["id"], u["user_token"])
    first = client.post(f"/c/{b['id']}/alarm", json={"message": "one"}).json()
    second = client.post(f"/c/{b['id']}/alarm", json={"message": "two"}).json()
    assert second["joined_existing"] is True
    assert second["alarm"] == first["alarm"]
    assert second["message_sent"] is True
    assert len(sent) == 1


def test_nobody_configured_means_no_row_and_an_honest_sentence(client,
                                                               monkeypatch):
    """No contact, no watch: nothing to attempt, so the ledger stays empty
    and the finder is told to call for help themselves."""
    _mail_spy(monkeypatch)
    u = _adult(client, emergency_name=None, emergency_phone=None)
    b = _place(client, u["id"], u["user_token"])
    body = client.post(f"/c/{b['id']}/alarm", json={"message": "hm"}).json()
    assert body["message_sent"] is False
    assert "No message went out from this page" in body["note"]
    pages = client.get(f"/users/{u['id']}/pages",
                       headers=_auth(u["user_token"])).json()
    assert [p for p in pages if p["alarm"] == body["alarm"]] == []


def test_a_site_incident_never_pages_the_workers_family(client, monkeypatch):
    """The relay module draws this line and the raise respects it: a
    workplace incident is worked through the site roster, not sent to the
    worker's personal emergency contact."""
    from jim import crashwatch
    sent = _mail_spy(monkeypatch)
    u = _adult(client)
    crashwatch.arm(u["id"], "Rosa", "rosa@example.test")
    b = _place(client, u["id"], u["user_token"], kind="site",
               label="plant room 2")
    body = client.post(f"/c/{b['id']}/alarm", json={"message": "down"}).json()
    assert sent == []
    assert body["message_sent"] is False
    pages = client.get(f"/users/{u['id']}/pages",
                       headers=_auth(u["user_token"])).json()
    assert [p for p in pages if p["alarm"] == body["alarm"]] == []
