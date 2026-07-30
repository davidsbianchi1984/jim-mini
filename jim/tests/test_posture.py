"""Two sentences of the spec that had no code behind them.

Clause 12, second half: the system "may autonomously refine its tone and or
voice interaction style to align with user preferences" — not only when the
user opens a settings screen.

Spec [0019], verbatim: "The guidance provided via the large language model may
be structured to be neutral to a person's background or beliefs, such as
religion, politics, sexual orientation, or the like, and in other examples may
be derived with sensitivity to the user's beliefs taken into account. A user's
age and maturity level may similarly be taken into account, as may a user's
general intelligence or ability to quickly grasp and apply guidance."
"""

from jim import coach, guidance
from jim.tests.conftest import enroll


def test_coach_learns_tone_from_the_prompt_itself(client):
    user = enroll(client)
    body = client.post(f"/coach/{user}", json={
        "area": "career",
        "message": "keep it short please — how do I prep for the interview?",
    }).json()
    assert body["adapted_tone"] == "direct and brief"

    # And it holds: the next turn is shaped without being asked again.
    again = client.post(f"/coach/{user}", json={
        "area": "career", "message": "and the salary question?"}).json()
    assert again["adapted_tone"] is None          # nothing new was learned

    from jim import guardian
    assert guardian.get_user(user)["personality"]["tone"] == "direct and brief"


def test_a_prompt_with_no_style_preference_teaches_nothing(client):
    user = enroll(client)
    body = client.post(f"/coach/{user}", json={
        "area": "finance", "message": "how do I start an emergency fund?"}).json()
    assert body["adapted_tone"] is None


def test_the_tone_table_is_transparent():
    assert coach.tone_from_prompt("Can you be gentle with me today") == \
        "gentle and encouraging"
    assert coach.tone_from_prompt("explain more, I want the detail") == \
        "thorough and detailed"
    assert coach.tone_from_prompt("no jargon please") == \
        "plain language, no jargon"
    assert coach.tone_from_prompt("what's for dinner") is None


def test_guidance_is_belief_neutral_by_default():
    """Neutral is the default *and* it is stated — a companion that quietly
    guesses somebody's religion is the failure this passage prevents."""
    prompt = guidance.personalize({"known_conditions": [], "personality": {}})
    assert "neutral to this person's background and beliefs" in prompt
    assert "never infer their beliefs" in prompt


def test_beliefs_are_honored_only_when_the_user_declares_them():
    sensitive = guidance.personalize({"personality": {
        "beliefs_posture": "sensitive",
        "beliefs": "observant Muslim — fasting during Ramadan"}})
    assert "fasting during Ramadan" in sensitive
    assert "the facts do not bend, the framing may" in sensitive

    # Sensitive with nothing declared falls back to neutral rather than
    # inviting the model to imagine what the beliefs might be.
    empty = guidance.personalize({"personality": {
        "beliefs_posture": "sensitive", "beliefs": "  "}})
    assert "neutral to this person's background" in empty


def test_explain_level_tailors_to_ability_to_grasp():
    plain = guidance.personalize({"personality": {"explain_level": "plain"}})
    assert "short sentences" in plain and "no jargon" in plain
    technical = guidance.personalize({"personality":
                                      {"explain_level": "technical"}})
    assert "grasps and applies guidance quickly" in technical
    # Unset says nothing about comprehension at all.
    assert "short sentences" not in guidance.personalize({"personality": {}})


def test_the_professional_role_shapes_guidance():
    """Clause 11: user-specific models "that adapt to professional roles"."""
    prompt = guidance.personalize({"personality":
                                   {"occupation": "night-shift nurse"}})
    assert "night-shift nurse" in prompt
    assert "demands and hours of that work" in prompt


def test_the_posture_dials_ride_the_personality_route(client):
    user = enroll(client)
    r = client.put(f"/personality/{user}", json={
        "beliefs_posture": "sensitive", "beliefs": "practicing Buddhist",
        "explain_level": "plain"})
    assert r.status_code == 200, r.text
    prefs = r.json()["personality"]
    assert prefs["beliefs_posture"] == "sensitive"
    assert prefs["explain_level"] == "plain"
    # A bad value is refused rather than stored and half-honored.
    assert client.put(f"/personality/{user}",
                      json={"explain_level": "telepathic"}).status_code == 422
