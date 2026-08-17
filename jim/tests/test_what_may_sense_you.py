"""Somewhere to plug the monitoring in, and what each one costs.

The field ask, in its own words: *cameras, speakers, screens, monitors capable
of monitoring, any type of wearables or stationary systems that can connect to
the human body, always on, always there — and somewhere to plug all of these
remote features and components in.*

Three tables already existed and none of them answered the question a person
actually has before switching one on: `devices` says what is registered,
`sources` says which categories of data may be read, and `mic.MIC_TYPES` says
whether a microphone is worn or pointed at a room.

    asked     can this device sense me
    mattered  who else does it sense, and what does it keep

## What these guards hold

* nothing that senses people who did not choose it is ever on by default, and
  the check reads the table rather than trusting anybody to have read it;
* a stationary monitor cannot claim to catch nobody — a thing bolted to a room
  senses the room, whatever it is called;
* switching one of those on is refused until somebody says the people in that
  space have been told, and that claim is stored as a claim rather than
  dressed up as consent this product collected;
* every row says what it keeps, because *it notices you fell* and *it keeps
  the video of you falling* are different agreements;
* one function is the only door to sensing anything;
* and a switched-off row stays, because when somebody decided is the part
  worth having.
"""

from __future__ import annotations

import inspect

import pytest

from jim import monitors

from .conftest import enroll


def _roster(client, user_id):
    r = client.get(f"/monitors/{user_id}")
    assert r.status_code == 200, r.text
    return {row["name"]: row for row in r.json()}


# --------------------------------------------------------------------------
# The rule that is enforced rather than intended.
# --------------------------------------------------------------------------

def test_nothing_that_senses_other_people_is_on_by_default():
    """The one guard this module exists for. A person who turns a hall camera
    on has decided; a person who finds one already on has been decided
    about, and no amount of usefulness afterwards converts the second into
    the first."""
    assert monitors._defaults_are_honest() == []


def test_a_stationary_monitor_cannot_claim_to_catch_nobody():
    """A thing bolted to a room senses the room, whatever it is called —
    `jim/mic.py` settled that for microphones and it holds for cameras,
    speakers and mattress strips too."""
    assert monitors._placings_are_honest() == []


def test_every_row_says_what_it_keeps():
    """*It notices you fell* and *it keeps the video of you falling* are
    different agreements, and only one of them is what the code does."""
    for row in monitors.MONITORS.values():
        assert row.holds, f"{row.name} says nothing about what it keeps"
        assert row.senses, f"{row.name} senses nothing in particular"
        assert row.placing in monitors.PLACINGS
        for sense in row.senses:
            assert sense in monitors.SENSES


def test_worn_does_not_mean_harmless():
    """Glasses are worn and still pointed outward at whoever is in front of
    you. The field that matters is who it reaches, not where it sits."""
    assert monitors.MONITORS["glasses"].catches_others is True
    assert monitors.MONITORS["wrist"].catches_others is False


# --------------------------------------------------------------------------
# Plugging one in.
# --------------------------------------------------------------------------

def test_the_roster_shows_what_is_off_too(client):
    """A roster showing only what somebody already switched on is a roster
    nobody can add to."""
    user_id = enroll(client)
    rows = _roster(client, user_id)
    assert set(rows) == set(monitors.MONITORS)
    assert rows["room_camera"]["on"] is False
    assert rows["room_camera"]["catches_others"] is True


def test_a_personal_monitor_switches_on_plainly(client):
    user_id = enroll(client)
    r = client.put(f"/monitors/{user_id}/wrist",
                   json={"device_name": "the black watch"})
    assert r.status_code == 200, r.text
    assert _roster(client, user_id)["wrist"]["on"] is True


def test_one_that_catches_others_is_refused_until_somebody_says_they_know(
        client):
    """What this prevents is a hall camera going on with nobody having
    thought about the hall."""
    user_id = enroll(client)
    refused = client.put(f"/monitors/{user_id}/room_camera",
                         json={"device_name": "hall"})
    assert refused.status_code == 409, refused.text
    assert "have been told" in refused.text

    allowed = client.put(f"/monitors/{user_id}/room_camera",
                         json={"device_name": "hall", "others_told": True})
    assert allowed.status_code == 200, allowed.text
    assert _roster(client, user_id)["room_camera"]["on"] is True


def test_the_claim_is_stored_as_a_claim(client):
    """Somebody's assertion with a time on it — not consent this product
    collected, and the row does not pretend otherwise."""
    user_id = enroll(client)
    client.put(f"/monitors/{user_id}/room_speaker",
               json={"others_told": True})
    row = _roster(client, user_id)["room_speaker"]
    assert row["others_told"] is True
    from jim import db
    stored = db.connect().execute(
        "SELECT decided_at FROM monitors WHERE user_id=? AND monitor=?",
        (user_id, "room_speaker")).fetchone()
    assert stored["decided_at"]


def test_keeping_is_its_own_switch(client):
    """Sensing and keeping are two decisions. A camera that watches for a
    fall does not have to be a camera that keeps the fall."""
    user_id = enroll(client)
    client.put(f"/monitors/{user_id}/room_camera",
               json={"others_told": True})
    assert _roster(client, user_id)["room_camera"]["keeping"] is False
    client.put(f"/monitors/{user_id}/room_camera",
               json={"others_told": True, "keeping": True})
    assert _roster(client, user_id)["room_camera"]["keeping"] is True


def test_switching_one_off_leaves_the_decision_behind(client):
    """When somebody decided is the part worth having, so the row stays."""
    user_id = enroll(client)
    client.put(f"/monitors/{user_id}/wrist", json={})
    client.delete(f"/monitors/{user_id}/wrist")
    assert _roster(client, user_id)["wrist"]["on"] is False
    from jim import db
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM monitors WHERE user_id=? AND monitor=?",
        (user_id, "wrist")).fetchone()["n"] == 1


def test_an_invented_monitor_is_refused_by_name(client):
    user_id = enroll(client)
    r = client.put(f"/monitors/{user_id}/mind_reader", json={})
    assert r.status_code == 422, r.text
    assert "room_camera" in r.text


# --------------------------------------------------------------------------
# The one door.
# --------------------------------------------------------------------------

def test_nothing_is_sensed_through_a_monitor_nobody_switched_on(client):
    user_id = enroll(client)
    refused = client.post(f"/monitors/{user_id}/wrist/sensed")
    assert refused.status_code == 403, refused.text

    client.put(f"/monitors/{user_id}/wrist", json={})
    assert client.post(f"/monitors/{user_id}/wrist/sensed").status_code == 200


def test_the_refusal_names_what_it_would_have_done(client):
    """`wrist` is an identifier. *Switch it on* is only actionable if the
    person can tell which thing the sentence is about."""
    user_id = enroll(client)
    with pytest.raises(monitors.NotPluggedIn) as caught:
        monitors.may_sense(user_id, "room_camera")
    said = str(caught.value)
    assert "room_camera" not in said
    assert "see the room" in said


def test_one_function_is_the_only_door():
    """The argument `oncall.may_listen` makes for a call and `offline.allow`
    makes for a socket.

    The door moved one layer in when `jim/daybook.py` arrived: the sensing
    route used to ask `may_sense` itself and now hands the moment to the
    daybook, which asks. So both are read — the rule is unchanged and only
    its address moved, and a guard that kept looking at the old address
    would have gone quietly green while the door was somewhere else.
    """
    from jim import api, daybook
    asks = [m for m in (api, daybook)
            if "monitors.may_sense(" in inspect.getsource(m)]
    assert asks, "nothing on the sensing path asks `may_sense`"
    for module in (api, daybook):
        assert "switched_on" not in inspect.getsource(module), (
            f"{module.__name__} is reading the switch itself instead of "
            "asking `may_sense`")


def test_no_argument_opens_a_monitor_that_is_off():
    """Crude on purpose: every reason to bypass this for one call sounds
    reasonable at the time."""
    assert list(inspect.signature(monitors.may_sense).parameters) == [
        "user_id", "name"]


@pytest.mark.parametrize("name", sorted(monitors.MONITORS))
def test_every_row_can_actually_be_switched_on(client, name):
    """A roster row nothing can turn on is a label on an empty box."""
    user_id = enroll(client)
    r = client.put(f"/monitors/{user_id}/{name}", json={"others_told": True})
    assert r.status_code == 200, r.text
