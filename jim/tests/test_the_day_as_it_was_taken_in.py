"""The day as it was actually taken in, and what survived of it.

The field ask, in its own words: *watches computer or phone screen all the
time, watch every meeting you're in, record every call, stream, etc., have
perfect accounting and context of your life.*

    asked     is the day captured
    mattered  does what survives match what was promised before it was switched on

`jim/monitors.py` built the consent and stopped at the door: the roster said
what may sense and what each row holds, `POST /monitors/{name}/sensed` ran the
permission check, and then returned `{"sensing": true}` and recorded nothing.
The permission to capture the day had shipped; the capture had not.

## What these guards hold

* the roster decides what is kept and the caller never does — a screen monitor
  drops its content whatever is passed and whatever is switched on, because
  that is what its row promised the person who switched it on;
* there is no argument anywhere that overrides it, and this file asserts the
  absence rather than trusting it;
* the promise in words (`holds`) and the rule in code (`keeps`) are the same
  promise, and a guard holds them together — two spellings of one promise is
  two places for it to drift;
* every moment leaves a row whether or not its content survived, and says
  which promise dropped it. An accounting listing only what survived would be
  a record with its own omissions edited out;
* opening a meeting on a monitor that catches other people demands the claim
  that they were told, asked again rather than inherited from the switch;
* and forgetting a moment drops the content and keeps the fact, because a
  record that quietly loses its own entries is the thing this is not.
"""

from __future__ import annotations

import inspect

import pytest

from jim import daybook, monitors

from .conftest import enroll


def _on(client, uid, monitor, **body):
    """Switch a monitor on. Anything that catches others has to say so."""
    spec = monitors.MONITORS[monitor]
    body.setdefault("others_told", spec.catches_others)
    r = client.put(f"/monitors/{uid}/{monitor}", json=body)
    assert r.status_code == 200, r.text


def _sensed(client, uid, monitor, content="", stretch_id=None):
    r = client.post(f"/monitors/{uid}/{monitor}/sensed",
                    json={"content": content, "stretch_id": stretch_id})
    assert r.status_code == 200, r.text
    return r.json()


# --------------------------------------------------------------------------
# The roster decides what is kept. The caller never does.
# --------------------------------------------------------------------------

def test_a_monitor_that_promised_nothing_keeps_nothing(client):
    """The screen row says *nothing — what it notices is offered and
    dropped*. That sentence was written to be read by somebody deciding
    whether to switch it on, so it is what the code does."""
    uid = enroll(client)
    _on(client, uid, "screen")
    out = _sensed(client, uid, "screen", "a private email, in full")
    assert out["kept"] is False
    assert out["dropped_because"] == "holds_nothing"
    assert client.get(f"/day/{uid}").json()["survived"] == []


def test_switching_keeping_on_cannot_reach_a_monitor_that_holds_nothing(client):
    """`keeping` is the switch for the rows that say *nothing unless you
    switch keeping on*. It is not a way round the rows that say *nothing*."""
    uid = enroll(client)
    _on(client, uid, "screen", keeping=True)
    assert _sensed(client, uid, "screen", "still private")["kept"] is False


def test_a_row_that_keeps_your_own_history_keeps_it(client):
    """The wrist reads one pulse and the readings are the person's own
    history — which is what they switched it on for."""
    uid = enroll(client)
    _on(client, uid, "wrist")
    assert _sensed(client, uid, "wrist", "hr 62")["kept"] is True
    kept = client.get(f"/day/{uid}").json()["survived"]
    assert [(k["monitor"], k["content"]) for k in kept] == [("wrist", "hr 62")]


def test_a_conditional_row_waits_for_the_switch(client):
    """*Nothing unless you switch keeping on* means exactly that, and the
    refusal says which switch, because it is one the person can go and
    change."""
    uid = enroll(client)
    _on(client, uid, "room_camera")
    first = _sensed(client, uid, "room_camera", "somebody crossed the room")
    assert first["kept"] is False
    assert first["dropped_because"] == "keeping_is_off"

    _on(client, uid, "room_camera", keeping=True)
    assert _sensed(client, uid, "room_camera", "and again")["kept"] is True


def test_nothing_lets_a_caller_ask_for_content_to_be_kept():
    """The absence is the feature. The moment a caller can say *keep this
    anyway*, every promise in the roster becomes a default."""
    from jim.models import Sensed
    assert "keep" not in inspect.signature(daybook.sensed).parameters
    assert not [f for f in Sensed.model_fields if "keep" in f]
    # And the decision is taken from the roster, in one place.
    assert "monitors.MONITORS[monitor]" in inspect.getsource(daybook._may_keep)


def test_the_promise_in_words_and_the_rule_in_code_are_the_same_promise():
    """Two spellings of one promise is two places for it to drift, and the
    drift would be silent in the direction that matters — a sentence saying
    *nothing* over code that kept everything."""
    assert monitors._keeping_is_honest() == []


@pytest.mark.parametrize("name", sorted(monitors.MONITORS))
def test_every_row_declares_what_it_keeps(name):
    assert monitors.MONITORS[name].keeps in monitors.KEEPS


def test_a_screen_can_read_the_promise_beside_the_switch(client):
    """Both travel: the sentence for a person, the rule for a client that
    wants to branch on it."""
    uid = enroll(client)
    row = next(m for m in client.get(f"/monitors/{uid}").json()
               if m["name"] == "screen")
    assert row["keeps"] == "nothing"
    assert row["holds"].startswith("nothing")


# --------------------------------------------------------------------------
# Perfect accounting means the drops are in it too.
# --------------------------------------------------------------------------

def test_a_dropped_moment_is_still_a_moment(client):
    """An accounting that listed only what survived would be a record with
    its own omissions edited out."""
    uid = enroll(client)
    _on(client, uid, "screen")
    for _ in range(3):
        _sensed(client, uid, "screen", "something")

    day = client.get(f"/day/{uid}").json()["account"]
    assert day["sensed"] == 3
    assert day["kept"] == 0
    screen = next(m for m in day["monitors"] if m["monitor"] == "screen")
    assert screen["dropped"] == 3
    assert screen["because"] == ["holds_nothing"]
    # And the sentence the person was promised, beside the count.
    assert screen["holds"] == monitors.MONITORS["screen"].holds


def test_one_monitor_can_drop_for_two_reasons_in_a_day(client):
    """Keeping switched off in the morning and on by the afternoon is an
    ordinary thing to do, so `because` is a list."""
    uid = enroll(client)
    _on(client, uid, "room_camera")
    _sensed(client, uid, "room_camera", "before")
    _on(client, uid, "room_camera", keeping=True)
    _sensed(client, uid, "room_camera")           # kept, but nothing in it

    day = client.get(f"/day/{uid}").json()["account"]
    cam = next(m for m in day["monitors"] if m["monitor"] == "room_camera")
    assert sorted(cam["because"]) == ["keeping_is_off", "nothing_to_keep"]


def test_nothing_sensed_is_stated_rather_than_inferred(client):
    uid = enroll(client)
    day = client.get(f"/day/{uid}").json()["account"]
    assert day["quiet"] is True
    assert day["monitors"] == [] and day["sensed"] == 0


def test_the_day_is_counted_per_monitor_rather_than_listed(client):
    """*The screen noticed four hundred things and kept none of them* is an
    ordinary working day, and four hundred rows is not a thing anybody
    reads."""
    uid = enroll(client)
    _on(client, uid, "screen")
    for _ in range(40):
        _sensed(client, uid, "screen", "a window changed")
    day = client.get(f"/day/{uid}").json()["account"]
    assert len(day["monitors"]) == 1
    assert day["monitors"][0]["sensed"] == 40


def test_a_monitor_nobody_switched_on_records_nothing(client):
    """The one door, unchanged. Capture did not become a way round it."""
    uid = enroll(client)
    r = client.post(f"/monitors/{uid}/screen/sensed", json={"content": "x"})
    assert r.status_code == 403, r.text
    assert client.get(f"/day/{uid}").json()["account"]["sensed"] == 0


# --------------------------------------------------------------------------
# Meetings, and the people in them who never chose this.
# --------------------------------------------------------------------------

def test_a_meeting_on_a_monitor_that_catches_others_asks_again(client):
    """Consent to a room speaker in a quiet house is not consent to it
    through an hour with four other people in the room."""
    uid = enroll(client)
    _on(client, uid, "room_speaker")          # switched on, others told
    r = client.post(f"/day/{uid}/stretches",
                    json={"monitor": "room_speaker", "about": "the standup"})
    assert r.status_code == 409, r.text

    ok = client.post(f"/day/{uid}/stretches",
                     json={"monitor": "room_speaker", "about": "the standup",
                           "others_told": True})
    assert ok.status_code == 201, ok.text
    assert ok.json()["others_told"] is True
    assert ok.json()["catches_others"] is True


def test_the_claim_is_asked_again_rather_than_read_off_the_switch():
    """Checked in the source, because inheriting it would be the easy thing
    to do and would look identical from outside."""
    source = inspect.getsource(daybook.open_stretch)
    assert "catches_others" in source and "others_told" in source


def test_a_meeting_on_a_monitor_that_catches_nobody_just_opens(client):
    uid = enroll(client)
    _on(client, uid, "wrist")
    r = client.post(f"/day/{uid}/stretches", json={"monitor": "wrist"})
    assert r.status_code == 201, r.text


def test_a_meeting_gathers_the_moments_that_fell_inside_it(client):
    uid = enroll(client)
    _on(client, uid, "wrist")
    met = client.post(f"/day/{uid}/stretches",
                      json={"monitor": "wrist", "about": "a walk"}).json()
    _sensed(client, uid, "wrist", "hr 71", stretch_id=met["id"])
    _sensed(client, uid, "wrist", "hr 74", stretch_id=met["id"])

    closed = client.delete(f"/day/{uid}/stretches/{met['id']}").json()
    assert closed["running"] is False
    assert closed["moments"] == 2 and closed["kept"] == 2


def test_closing_twice_is_closing_once(client):
    uid = enroll(client)
    _on(client, uid, "wrist")
    met = client.post(f"/day/{uid}/stretches", json={"monitor": "wrist"}).json()
    first = client.delete(f"/day/{uid}/stretches/{met['id']}").json()
    again = client.delete(f"/day/{uid}/stretches/{met['id']}").json()
    assert again["ended_at"] == first["ended_at"]


def test_a_stranger_cannot_read_or_close_somebody_elses_meeting(client):
    uid = enroll(client)
    _on(client, uid, "wrist")
    met = client.post(f"/day/{uid}/stretches", json={"monitor": "wrist"}).json()
    outsider = enroll(client)
    head = {"authorization": client.headers["authorization"]}
    r = client.delete(f"/day/{outsider}/stretches/{met['id']}", headers=head)
    assert r.status_code == 403, r.text


def test_a_moment_cannot_join_somebody_elses_meeting(client):
    """Found by trying it rather than by reading the code.

    A stranger handing in moments against another person's stretch does not
    leak anything — the row carries its own `user_id` — but it inflated that
    meeting's counts with moments from somebody who was never in it, and a
    record anybody can add to is not one its owner can rely on.
    """
    a = enroll(client)
    a_head = {"authorization": client.headers["authorization"]}
    _on(client, a, "wrist")
    met = client.post(f"/day/{a}/stretches", json={"monitor": "wrist"},
                      headers=a_head).json()

    b = enroll(client)
    b_head = {"authorization": client.headers["authorization"]}
    client.put(f"/monitors/{b}/wrist", json={}, headers=b_head)
    r = client.post(f"/monitors/{b}/wrist/sensed",
                    json={"content": "not theirs", "stretch_id": met["id"]},
                    headers=b_head)
    assert r.status_code == 403, r.text

    closed = client.delete(f"/day/{a}/stretches/{met['id']}",
                           headers=a_head).json()
    assert closed["moments"] == 0


# --------------------------------------------------------------------------
# Forgetting keeps the fact and drops the content.
# --------------------------------------------------------------------------

def test_forgetting_a_moment_leaves_the_moment(client):
    """A record that quietly loses its own entries is the thing this module
    exists not to be."""
    uid = enroll(client)
    _on(client, uid, "wrist")
    moment = _sensed(client, uid, "wrist", "hr 62")
    client.delete(f"/day/{uid}/moments/{moment['id']}")

    day = client.get(f"/day/{uid}").json()
    assert day["survived"] == []
    assert day["account"]["sensed"] == 1, "the moment is still counted"
    wrist = next(m for m in day["account"]["monitors"] if m["monitor"] == "wrist")
    assert wrist["because"] == ["forgotten"]


@pytest.mark.parametrize("reason", daybook.DROPPED)
def test_every_reason_a_moment_was_dropped_is_a_word_somebody_can_read(reason):
    assert reason and reason.replace("_", "").isalpha()


# --------------------------------------------------------------------------
# What this deliberately is not.
# --------------------------------------------------------------------------

def test_no_bytes_ever_reach_this_table():
    """It is not a recorder. Turning it into one needs the roster's promises
    rewritten, somewhere to put the bytes that is not this database, and an
    answer to two-party consent law that a checkbox is not — none of which
    this round did or could decide alone."""
    from jim import db
    columns = {r[1] for r in db.connect().execute(
        "PRAGMA table_info(day_moments)").fetchall()}
    for theirs in ("audio", "video", "image", "pixels", "frames", "blob"):
        assert theirs not in columns
