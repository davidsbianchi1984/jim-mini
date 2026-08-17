"""Two people on one call, each with their own channel 2.

The field ask, in its own words: *both parties could use it while on the same
call — both have profiles and both could be using them simultaneously.*

    asked     can two people each have channel 2 on one call
    mattered  does each of them know the other's guardian is listening

Two people could already do the first half. `mic.handover` is per person and
always was: on a private route it hears its wearer and not the call, so two of
them on one call never needed permission from each other and never conflicted.
What was missing is that **nothing knew they were the same call** — so somebody
on a call where both guardians were listening had no way to find that out.

## What these guards hold

* a pair is a **disclosure** and nothing else. It carries no audio, no content,
  and nothing either guardian heard;
* pairing never grants listening. A side may only join with a channel it
  already has, so every refusal in `handover` — a private route, a busy
  primary, not the microphone carrying the call, nobody else in earshot — was
  answered before the pair could name the session;
* neither side is ever handed the other's session, device, gain, or what it
  hears. What crosses is that somebody is listening and since when;
* it forms only between people who were already each other's contacts, the
  same gate `jim/liaison.py` opens on;
* and a side stops counting the moment their own channel closes, because a row
  that outlived the session it names would report somebody as listening after
  they hung up.
"""

from __future__ import annotations

import inspect

import pytest

from jim import mic

from .conftest import enroll


def _two(client):
    """Two enrolled people who are already each other's contacts."""
    a = enroll(client)
    a_head = {"authorization": client.headers["authorization"]}
    b = enroll(client)
    b_head = {"authorization": client.headers["authorization"]}
    client.post(f"/circle/{b}/contacts", json={"other_id": a}, headers=b_head)
    client.post(f"/circle/{a}/contacts", json={"other_id": b}, headers=a_head)
    return a, a_head, b, b_head


def _listening(client, uid, head, route="earpiece"):
    """Give this person a channel 2 the honest way — through every refusal."""
    client.post(f"/devices/{uid}", json={"name": "watch", "kind": "wearable"},
                headers=head)
    r = client.put(f"/users/{uid}/mic",
                   json={"device_name": "watch", "mic_type": "watch"},
                   headers=head)
    assert r.status_code == 200, r.text
    r = client.post(f"/users/{uid}/mic/handover",
                    json={"reason": "voice_call", "route": route},
                    headers=head)
    assert r.status_code in (200, 201), r.text
    return r.json()


# --------------------------------------------------------------------------
# Both at once, and each one knows.
# --------------------------------------------------------------------------

def test_both_can_listen_and_each_learns_the_other_is(client):
    """The half that existed and the half that did not."""
    a, a_head, b, b_head = _two(client)
    _listening(client, a, a_head)
    _listening(client, b, b_head)

    client.post(f"/users/{a}/mic/pair", json={"other_id": b}, headers=a_head)
    client.post(f"/users/{b}/mic/pair", json={"other_id": a}, headers=b_head)

    mine = client.get(f"/users/{a}/mic/pair", headers=a_head).json()
    theirs = client.get(f"/users/{b}/mic/pair", headers=b_head).json()
    assert mine["both"] is True and theirs["both"] is True
    assert mine["with"] == b and theirs["with"] == a


def test_one_side_alone_is_an_honest_middle_state(client):
    """This person has said who else is on the call and the other has not
    joined. Reporting that as a pair would be claiming somebody's guardian is
    listening when nothing says it is."""
    a, a_head, b, b_head = _two(client)
    _listening(client, a, a_head)
    _listening(client, b, b_head)

    out = client.post(f"/users/{a}/mic/pair", json={"other_id": b},
                      headers=a_head).json()
    assert out["paired"] is True
    assert out["yours_listening"] is True
    assert out["theirs_listening"] is False
    assert out["both"] is False


def test_the_disclosure_is_on_the_screen_that_asks_what_it_can_hear(client):
    """*Yours hears you* is a true sentence and an incomplete one on a call
    where both guardians are listening."""
    a, a_head, b, b_head = _two(client)
    _listening(client, a, a_head)
    _listening(client, b, b_head)
    client.post(f"/users/{a}/mic/pair", json={"other_id": b}, headers=a_head)
    client.post(f"/users/{b}/mic/pair", json={"other_id": a}, headers=b_head)

    state = client.get(f"/users/{a}/mic", headers=a_head).json()
    assert state["listening"] is True
    assert state["theirs_listening"] is True
    assert "paired" in inspect.getsource(mic.state)


def test_a_side_stops_counting_when_their_own_channel_closes(client):
    """A row that outlived the session it names would report somebody as
    listening after they hung up, which is the one thing this must never
    say."""
    a, a_head, b, b_head = _two(client)
    _listening(client, a, a_head)
    _listening(client, b, b_head)
    client.post(f"/users/{a}/mic/pair", json={"other_id": b}, headers=a_head)
    client.post(f"/users/{b}/mic/pair", json={"other_id": a}, headers=b_head)
    assert client.get(f"/users/{a}/mic/pair",
                      headers=a_head).json()["theirs_listening"] is True

    client.post(f"/users/{b}/mic/release", headers=b_head)
    after = client.get(f"/users/{a}/mic/pair", headers=a_head).json()
    assert after["theirs_listening"] is False
    assert after["both"] is False


# --------------------------------------------------------------------------
# Pairing never grants listening.
# --------------------------------------------------------------------------

def test_a_side_cannot_pair_without_a_channel_it_already_has(client):
    """Pairing is a label on a handover, never a way to get one."""
    a, a_head, b, b_head = _two(client)
    r = client.post(f"/users/{a}/mic/pair", json={"other_id": b},
                    headers=a_head)
    assert r.status_code == 422, r.text
    assert "hand one over first" in r.text


def test_pairing_opens_nothing_and_the_source_shows_it():
    """The cheap version of this would open the channel itself, and would be
    a second door onto the thing `jim/mic.py` spends four screens refusing."""
    source = inspect.getsource(mic.pair)
    assert "_live(user_id)" in source
    assert "INSERT INTO mic_sessions" not in source
    # And it takes no route, gain or device — nothing that could set the
    # terms the handover already settled.
    assert list(inspect.signature(mic.pair).parameters) == [
        "user_id", "other_id", "about"]


def test_the_speakerphone_refusal_is_not_reachable_around(client):
    """The load-bearing refusal in that module. If pairing could be done
    first and the route relaxed after, this whole round would have quietly
    reopened it."""
    a, a_head, b, b_head = _two(client)
    r = client.post(f"/users/{a}/mic/handover",
                    json={"reason": "voice_call", "route": "speaker"},
                    headers=a_head)
    assert r.status_code == 403, r.text
    # And with no channel, there is nothing to pair.
    assert client.post(f"/users/{a}/mic/pair", json={"other_id": b},
                       headers=a_head).status_code == 422


def test_the_request_body_cannot_set_the_terms_of_the_channel():
    from jim.models import MicPair
    assert set(MicPair.model_fields) == {"other_id", "about"}


# --------------------------------------------------------------------------
# The two halves never meet.
# --------------------------------------------------------------------------

def test_neither_side_is_handed_the_others_channel(client):
    """What crosses is that somebody is listening and since when. Their
    device, their gain and what their guardian heard were never this
    person's to read."""
    a, a_head, b, b_head = _two(client)
    _listening(client, a, a_head)
    b_channel = _listening(client, b, b_head)
    client.post(f"/users/{a}/mic/pair", json={"other_id": b}, headers=a_head)
    client.post(f"/users/{b}/mic/pair", json={"other_id": a}, headers=b_head)

    mine = client.get(f"/users/{a}/mic/pair", headers=a_head).json()
    blob = repr(mine)
    assert b_channel["id"] not in blob, "their session id crossed"
    for theirs in ("device", "mic_type", "gain", "effective_gain", "hears",
                   "session_id", "route"):
        assert theirs not in mine, theirs


def test_a_stranger_cannot_pair_with_somebody(client):
    """The same gate the liaison opens on: a stranger who has your number
    should not be able to attach their guardian's session to yours, even as
    a label."""
    a = enroll(client)
    a_head = {"authorization": client.headers["authorization"]}
    b = enroll(client)
    _listening(client, a, a_head)

    r = client.post(f"/users/{a}/mic/pair", json={"other_id": b},
                    headers=a_head)
    assert r.status_code == 409, r.text
    assert "each other's contacts" in r.text


def test_the_gate_is_the_one_the_circle_already_had():
    assert "circle._mutual" in inspect.getsource(mic.pair)


def test_no_audio_column_exists_anywhere_in_the_pair():
    from jim import db
    for table in ("mic_pairs", "mic_pair_sides"):
        columns = {r[1] for r in db.connect().execute(
            f"PRAGMA table_info({table})").fetchall()}
        for theirs in ("audio", "transcript", "recording", "content", "heard"):
            assert theirs not in columns, f"{table}.{theirs}"


# --------------------------------------------------------------------------
# Leaving.
# --------------------------------------------------------------------------

def test_leaving_ends_the_pair_and_leaves_their_channel_alone(client):
    """One person leaving a call is not a reason for somebody else's agent
    to stop listening to them."""
    a, a_head, b, b_head = _two(client)
    _listening(client, a, a_head)
    _listening(client, b, b_head)
    client.post(f"/users/{a}/mic/pair", json={"other_id": b}, headers=a_head)
    client.post(f"/users/{b}/mic/pair", json={"other_id": a}, headers=b_head)

    client.delete(f"/users/{a}/mic/pair", headers=a_head)
    assert client.get(f"/users/{a}/mic/pair",
                      headers=a_head).json()["paired"] is False
    # It ends for both — a pair one side still believed in would be exactly
    # the wrong half to leave standing.
    assert client.get(f"/users/{b}/mic/pair",
                      headers=b_head).json()["paired"] is False
    # And their own channel is untouched.
    assert client.get(f"/users/{b}/mic", headers=b_head).json()["listening"] \
        is True


def test_leaving_when_there_is_nothing_to_leave_is_not_an_error(client):
    a, a_head, _, _ = _two(client)
    out = client.delete(f"/users/{a}/mic/pair", headers=a_head).json()
    assert out["paired"] is False


def test_the_empty_answer_carries_every_key(client):
    """A shape that grew fields only when something was there would have four
    shells reading `undefined` on the case they meet most."""
    a, a_head, b, b_head = _two(client)
    _listening(client, a, a_head)
    _listening(client, b, b_head)
    client.post(f"/users/{a}/mic/pair", json={"other_id": b}, headers=a_head)

    full = set(client.get(f"/users/{a}/mic/pair", headers=a_head).json())
    empty = set(client.get(f"/users/{b}/mic/pair", headers=b_head).json())
    assert full == empty


def test_joining_twice_is_joining_once(client):
    """A person whose channel dropped and came back is naming a new session
    on the same call, not opening a second pair."""
    a, a_head, b, b_head = _two(client)
    _listening(client, a, a_head)
    first = client.post(f"/users/{a}/mic/pair", json={"other_id": b},
                        headers=a_head).json()
    again = client.post(f"/users/{a}/mic/pair", json={"other_id": b},
                        headers=a_head).json()
    assert again["id"] == first["id"]


@pytest.mark.parametrize("ending", mic.PAIR_ENDINGS)
def test_every_ending_is_a_word_somebody_can_read(ending):
    assert ending and ending.replace("_", "").isalpha()
