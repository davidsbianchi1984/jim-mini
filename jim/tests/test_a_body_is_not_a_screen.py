"""A robot is another motor on the same wire, and the safety margin is not.

`jim/robotics.py` has carried a catalogue of bodies for several releases —
platforms, kinds, a per-kind command allowlist, and a first-aid rating that
decides whether a body may deliver chest compressions. None of it was ever
attached to a grant, a reach, a ledger or a refusal. The hands built all
four for screens. Wiring them together is a short afternoon and the wrong
one to have.

    asked     can the Guardian work a body the way it works a screen
    mattered  what does not carry over

Everything that bounds a screen bounds it because a mis-click is undone with
a keystroke. Four of those bounds mean something different, or nothing, on
something that can move in a room:

    a list of app names          is not a place a body may be
    a step budget                does not say how hard a step is
    a corner of the screen       is not within reach of somebody standing
                                 beside a robot
    the motor's own word         is a restatement of the request, not
                                 evidence that anything happened

This product has a sharper reason than its sibling. A body here is in
somebody's home, often near somebody who is already unwell, and the person
who would be standing next to it is the person the whole product exists to
look after.

So `body` is a surface here, `watching` on one is allowed, and `acting` is
refused with all four named. Shipping the transmit path first and the
envelope afterwards is how the envelope ends up shaped by whatever was easy
to transmit.
"""

from __future__ import annotations

import pytest

from jim import hands, robotics

from .conftest import enroll


def _grant(user_id, **kw):
    kw.setdefault("surface", "body")
    kw.setdefault("places", ["optimus"])
    kw.setdefault("verbs", ["look"])
    return hands.grant(user_id, user_id, **kw)


def test_a_body_is_a_surface_this_product_admits_to(client):
    """A surface a product silently does not support is indistinguishable
    from one it forgot about."""
    assert "body" in hands.SURFACES


def test_moving_a_body_is_refused_and_says_all_four_reasons(client):
    user_id = enroll(client)
    granted = _grant(user_id)
    with pytest.raises(hands.HandError) as raised:
        hands.open_reach(user_id, granted["id"], errand="fetch the post",
                         platform="linux", mode="acting")
    said = raised.value.message
    assert raised.value.status == 403
    for reason in hands.BODY_UNDECIDED:
        assert reason in said, f"the refusal does not mention: {reason}"
    # And it says what it *can* do, so the answer is not just "no".
    assert "watch" in said


def test_the_refusal_reaches_the_door_a_person_is_standing_at(client):
    """The module refusing is only half of it. A console that got a 500,
    or a 201 followed by nothing moving, would teach the reader that the
    feature is broken rather than that it is bounded."""
    user_id = enroll(client)
    granted = _grant(user_id)
    opened = client.post(f"/profiles/{user_id}/hands/reaches",
                         json={"grant_id": granted["id"],
                               "errand": "fetch the post",
                               "platform": "linux", "mode": "acting"})
    assert opened.status_code == 403, opened.text
    assert "body" in opened.json()["detail"]


def test_watching_through_a_body_is_allowed(client):
    """Seeing through a robot and saying what is there carries none of the
    four. Refusing it too would be caution aimed at nothing."""
    user_id = enroll(client)
    granted = _grant(user_id)
    reach = hands.open_reach(user_id, granted["id"],
                            errand="what is in the kitchen",
                            platform="linux", mode="watching")
    assert reach["state"] == "open"
    assert reach["surface"] == "body"


def test_the_four_reasons_are_about_bodies_and_not_screens(client):
    """Each one has to be a bound that a screen genuinely does not need, or
    the list is padding and a reader will learn to skim it."""
    said = " ".join(hands.BODY_UNDECIDED)
    assert "app names" in said        # places mean something else here
    assert "force" in said            # a step budget is not a force cap
    assert "stop" in said             # the mouse corner is out of reach
    assert "sensor" in said           # the mover is not a witness
    assert len(hands.BODY_UNDECIDED) == 4


def test_the_vocabulary_says_a_body_will_not_move(client):
    """Published, not merely enforced — the door a client reads to know
    what this product will not do."""
    out = client.get("/hands/vocabulary").json()
    assert "body" in out["surfaces"]
    assert any("body" in line for line in out["never"])


def test_the_catalogue_is_still_the_only_list_of_bodies(client):
    """The bodies a grant can name are the catalogue's, and the commands are
    its per-kind allowlist. A second list would be a second answer to the
    question of what a vacuum can be told to do."""
    assert robotics.COMMANDS["vacuum"] == ["clean", "spot_clean", "patrol",
                                           "dock", "locate", "stop"]
    assert "fetch" not in robotics.COMMANDS["vacuum"]
    # Nothing here has quietly grown a second vocabulary.
    assert "clean" not in hands.VERBS


def test_the_first_aid_commands_did_not_become_hand_verbs(client):
    """The sharpest reason this refusal exists in this product.

    `robotics` rates some bodies as able to deliver chest compressions.
    That rating is reached through the escalation ladder, where a person on
    scene confirms the need. A hand grant is a different thing entirely —
    written ahead of time, by somebody at a keyboard — and if the two
    vocabularies ever merged, an errand typed into a text box would be able
    to start CPR on somebody.
    """
    for command in ("perform_cpr", "auto_defib", "stop_cpr"):
        assert command not in hands.VERBS, (
            f"{command!r} is now reachable from a hand grant — a first-aid "
            "action must stay on the ladder, where a person on scene "
            "confirms it")
