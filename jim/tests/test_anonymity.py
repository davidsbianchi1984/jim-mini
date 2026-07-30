"""FIG. 2 box 212 — "choose name (anonymized)".

Spec [0031]: "The user may be asked to choose a user name at 212, which in
various examples may be **an anonymous user name**, the user's real name, or
left to the user to decide." [0024] says the same of profiles: anonymous or
identifiable, with the user free to "leave out certain elements of their
personal history".

QRME has had anonymity since its first round. JIM took a display_name and
that was that — which excluded the person the product most wants: somebody
willing to tell a machine about their panic attacks precisely because they are
not ready to put their name on it.
"""

from jim import guardian, identity
from jim.tests.conftest import enroll


def test_a_named_enrollment_is_unchanged(client):
    user = enroll(client, display_name="Jordan Vale")
    row = guardian.get_user(user)
    assert row["display_name"] == "Jordan Vale"
    assert row["anonymous"] is False and row["legal_name"] is None


def test_anonymous_enrollment_discards_the_typed_name(client):
    """The app must not quietly keep the name it was given — an anonymous
    enrollment that stored the real name would be a lie in a field."""
    user = enroll(client, display_name="Jordan Vale", anonymous=True)
    row = guardian.get_user(user)
    assert row["anonymous"] is True
    assert row["display_name"] != "Jordan Vale"
    assert row["legal_name"] is None
    # The pseudonym reads as one, so nobody mistakes it for an identity.
    assert row["display_name"].split()[-1].isdigit()


def test_pseudonyms_do_not_collide(client):
    names = {guardian.get_user(
        enroll(client, display_name="x", anonymous=True))["display_name"]
        for _ in range(12)}
    assert len(names) == 12


def test_every_emergency_path_still_works_anonymously(client):
    """The point of the tradeoff: anonymity costs a name in a briefing and
    nothing else. Detection, guidance and escalation are untouched."""
    user = enroll(client, display_name="Jordan", anonymous=True,
                  emergency_name="Ana", emergency_phone="+1 555 0100",
                  contact_consent=True)
    body = client.post(f"/monitor/{user}", json={"blood_oxygen": 85}).json()
    assert body["severity"] == "critical"
    assert body["escalation"]["notified_emergency_contact"] is True
    assert body["guidance"]["content"]


def test_the_briefing_will_not_invent_an_identity(client):
    user = enroll(client, display_name="Jordan", anonymous=True,
                  emergency_name="Ana", emergency_phone="+1 555 0100",
                  contact_consent=True)
    briefing = client.post(f"/monitor/{user}", json={"blood_oxygen": 85}
                           ).json()["escalation"]["companion"]["relaying"]["briefing"]
    assert briefing["who"] is None                     # no name is claimed
    told = briefing["identity"]
    assert told["anonymous"] is True
    assert "left no legal name on record" in told["note"]
    assert told["known_as"] == guardian.get_user(user)["display_name"]


def test_a_legal_name_left_for_emergencies_is_used_only_there(client):
    user = enroll(client, display_name="Jordan", anonymous=True,
                  legal_name="Jordan Vale", emergency_name="Ana",
                  emergency_phone="+1 555 0100", contact_consent=True)
    row = guardian.get_user(user)
    assert row["display_name"] != "Jordan Vale"        # not in the app
    briefing = client.post(f"/monitor/{user}", json={"blood_oxygen": 85}
                           ).json()["escalation"]["companion"]["relaying"]["briefing"]
    assert briefing["who"] == "Jordan Vale"            # but yes to responders
    assert "for emergencies only" in briefing["identity"]["note"]


def test_the_tradeoff_is_stated_not_hidden(client):
    """A checkbox with unstated consequences is not a choice."""
    plain = enroll(client, display_name="Jordan")
    assert client.get(f"/anonymity/{plain}").json()["anonymous"] is False

    user = enroll(client, display_name="Jordan", anonymous=True)
    posture = client.get(f"/anonymity/{user}").json()
    assert posture["anonymous"] is True
    assert posture["legal_name_on_record"] is False
    assert any("emergency path" in k for k in posture["keeps"])
    assert any("legal name" in c for c in posture["costs"])

    named = enroll(client, display_name="Jordan", anonymous=True,
                   legal_name="Jordan Vale")
    assert client.get(f"/anonymity/{named}").json()["costs"] == []


def test_resolve_is_the_whole_rule():
    assert identity.resolve({"display_name": "Ada"}) == ("Ada", None, False)
    name, legal, anon = identity.resolve(
        {"display_name": "Ada", "anonymous": True, "legal_name": "Ada L"})
    assert anon is True and legal == "Ada L" and name != "Ada"
