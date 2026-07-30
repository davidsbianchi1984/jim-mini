"""Clause 11: a user-specific version of the model, trained on received input.

"…adapting the large language model based on the received input comprises
training a user-specific version of the large language model based on the
received input. The system may generate user-specific models that adapt to
professional roles, workflows, or collaborative environments. Training may
employ secure, decentralized methods to ensure data integrity across
distributed networks."

The artifact JIM builds is an adaptation profile derived locally from the
user's own history — honest that it conditions the vendor's transformer rather
than replacing its weights, and sealed in the user's vault when a PDI tandem
is configured.
"""

from jim import adaptation
from jim.tests.conftest import enroll
from jim.tests.test_pdi_tandem import pdi_pair            # noqa: F401  (fixture)


def _unhelpful_round(client, user):
    """One guidance delivered and reported as not helping."""
    client.post(f"/monitor/{user}", json={"heart_rate": 120,
                                          "respiratory_rate": 22})
    client.post(f"/followup/{user}", json={"helped": False})


def _helpful_round(client, user):
    client.post(f"/monitor/{user}", json={"heart_rate": 120,
                                          "respiratory_rate": 22})
    client.post(f"/followup/{user}", json={"helped": True})


def test_nothing_built_yet_says_so(client):
    user = enroll(client)
    body = client.get(f"/adaptation/{user}").json()
    assert body["built"] is False and "POST /adaptation" in body["note"]


def test_the_profile_is_derived_from_the_users_own_history(client):
    user = enroll(client, known_conditions=["anxiety"])
    for _ in range(3):
        _helpful_round(client, user)
    client.post(f"/checkin/{user}", json={"mood": 4, "energy": 3, "stress": 2})
    client.post(f"/coach/{user}", json={"area": "career",
                                        "message": "interview prep?"})

    built = client.post(f"/adaptation/{user}").json()
    assert built["built"] is True and built["version"] == adaptation.VERSION
    profile = built["profile"]
    assert profile["known_conditions"] == ["anxiety"]
    assert profile["what_helps"]["anxiety"]["helped"] == 3
    assert profile["what_helps"]["anxiety"]["hit_rate"] == 1.0
    assert profile["checkins"]["count"] == 1
    assert profile["areas_brought"]["career"] == 1
    # Honest about what it is.
    assert "not modified here" in profile["method"]


def test_confidence_is_earned_from_evidence_not_fluency(client):
    thin = enroll(client)
    client.post(f"/checkin/{thin}", json={"mood": 3})
    lean = client.post(f"/adaptation/{thin}").json()
    assert lean["confidence"] < 0.2

    fat = enroll(client)
    for _ in range(5):
        _helpful_round(client, fat)
    for _ in range(6):
        client.post(f"/checkin/{fat}", json={"mood": 4})
    for _ in range(5):
        client.post(f"/coach/{fat}", json={"area": "finance",
                                           "message": "budget help"})
    rich = client.post(f"/adaptation/{fat}").json()
    assert rich["confidence"] > lean["confidence"]


def test_a_coincidence_is_not_a_finding(client):
    """Two answered follow-ups say nothing; the prompt stays quiet until the
    evidence threshold is met."""
    user = enroll(client)
    for _ in range(2):
        _helpful_round(client, user)
    client.post(f"/adaptation/{user}")
    assert adaptation.prompt_lines(user) == []

    _helpful_round(client, user)          # the third answer earns the claim
    client.post(f"/adaptation/{user}")
    lines = adaptation.prompt_lines(user)
    assert any("has worked for this person before" in line for line in lines)


def test_guidance_that_keeps_missing_changes_the_approach(client):
    user = enroll(client)
    for _ in range(3):
        _unhelpful_round(client, user)
    client.post(f"/adaptation/{user}")
    lines = adaptation.prompt_lines(user)
    assert any("NOT been landing" in line and "offer a human" in line
               for line in lines)


def test_the_artifact_seals_into_the_vault(pdi_pair):
    """The clause's "secure, decentralized methods": the profile goes into the
    user's own PDI vault, and the row records that it was sealed."""
    client, fake = pdi_pair
    user = enroll(client)
    client.post(f"/checkin/{user}", json={"mood": 3})
    built = client.post(f"/adaptation/{user}").json()
    assert built["vaulted"] is True
    assert built["sealed_key"].startswith(f"jim/{user}/adaptation/")
    assert built["sealed_key"] in fake.store
