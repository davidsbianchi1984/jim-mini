"""Spec [0039]'s closing edge: did the counseling work, and if not, a person.

Verbatim: "If the counseling is effective in managing the known condition or
concern as determined at 310, the personal guidance system may resume
monitoring the user for physical indications. If the counseling provided at
308 is not effective, the personal guidance system may alert a person to
provide live assistance to the user at 312, such as by connecting the user to
a support person associated with the personal guidance system or by
connecting the user with an emergency contact."
"""

from jim import escalation
from jim.tests.conftest import enroll


def _guided(client, **extra):
    """A user who has just been given guidance for an anxiety episode."""
    user = enroll(client, **extra)
    body = client.post(f"/monitor/{user}",
                       json={"heart_rate": 120, "respiratory_rate": 22}).json()
    assert body["guidance"]["delivered"] is True
    return user, body


def test_delivered_guidance_opens_a_followup(client):
    user, body = _guided(client)
    assert body["followup"]["question"] == "Did that help?"
    open_now = client.get(f"/followup/{user}").json()["open"]
    assert len(open_now) == 1 and open_now[0]["condition"] == "anxiety"


def test_it_helped_resumes_monitoring(client):
    user, _ = _guided(client)
    out = client.post(f"/followup/{user}", json={"helped": True}).json()
    assert out["answered"] is True and out["next"] == "monitoring resumes"
    assert "live_assistance" not in out
    # Answered follow-ups leave the queue but stay on the record.
    view = client.get(f"/followup/{user}").json()
    assert view["open"] == []
    assert view["history"][0]["helped"] is True
    assert any(e["type"] == "guidance_effective"
               for e in client.get(f"/events/{user}").json())


def test_it_did_not_help_reaches_a_live_person(client):
    user, _ = _guided(client, emergency_name="Ana",
                      emergency_phone="+1 555 0100", contact_consent=True)
    out = client.post(f"/followup/{user}",
                      json={"helped": False,
                            "note": "the breathing didn't settle me"}).json()
    assert out["next"] == "live assistance"

    # The ladder ran again, one rung above where a guidance event sat.
    decision = out["escalation_decision"]
    assert decision["tier_index"] >= escalation.TIERS.index("check_in")
    assert any("did not help" in step for step in decision["path"])

    # And real humans are named — the crisis line for a psychological
    # condition, and the contact who is on file.
    kinds = {o["kind"] for o in out["live_assistance"]["options"]}
    assert "crisis_line" in kinds and "emergency_contact" in kinds
    # Honest about what an app can and cannot do.
    assert "cannot" in out["live_assistance"]["note"]
    assert any(e["type"] == "guidance_ineffective"
               for e in client.get(f"/events/{user}").json())


def test_unhelped_critical_guidance_goes_all_the_way(client):
    """A critical event already sits at notify_contact; guidance that did not
    help puts it at emergency services — the rung above."""
    user = enroll(client, emergency_name="Ana", emergency_phone="+1 555 0100",
                  contact_consent=True)
    client.post(f"/monitor/{user}", json={"movement": "fall"})
    out = client.post(f"/followup/{user}", json={"helped": False}).json()
    assert out["escalation_decision"]["tier"] == "emergency_services"
    assert out["live_assistance"]["contact_alerted"] is True


def test_answering_nothing_says_so(client):
    user = enroll(client)
    out = client.post(f"/followup/{user}", json={"helped": True}).json()
    assert out["answered"] is False
    assert "waiting" in out["reason"]


def test_the_ineffective_rung_is_a_rung_not_a_jump(client):
    """Unit-level: the modifier lifts one tier with a floor at check_in — a
    breathing exercise that did not land must reach a person, and must not
    dispatch an ambulance on its own."""
    quiet = escalation.decide("info", "balanced", guidance_ineffective=True)
    assert quiet["tier"] == "check_in"
    guided = escalation.decide("guidance", "balanced",
                               guidance_ineffective=True)
    assert guided["tier"] == "check_in"
    cautious = escalation.decide("guidance", "cautious",
                                 guidance_ineffective=True)
    assert cautious["tier"] == "notify_contact"
    # Nothing changes when the guidance did help.
    assert escalation.decide("guidance", "balanced")["tier"] == "self_guidance"
