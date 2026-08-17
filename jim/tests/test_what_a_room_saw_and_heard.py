"""What a room sees and hears, read as cues rather than kept as footage.

The field ask, in its own words: *monitor you from devices in your home such
as cameras, speakers, looking for visual cues and verbal cues.*

    asked     can it read a cue off a camera or a speaker
    mattered  can it do that without keeping what it read the cue from

`jim/monitors.py` said what may sense. `jim/daybook.py` recorded what was taken
in and dropped most of it, because most of the roster promises to hold nothing.
Neither ever read a cue: the camera could be switched on and the room described
to it, and nothing looked at the description.

## What these guards hold

* a cue is read **before** anything is asked about keeping, so a room camera
  with keeping switched off notices a fall exactly as well as one keeping
  everything — and stores exactly as little as it promised. Noticing is free
  of retention, which is the only arrangement under which somebody can switch
  retention off without switching off their guardian;
* the words a cue was read from are never stored. Otherwise this is the back
  door round the roster: read the cue *and* stash the description;
* a monitor only yields cues its own senses can produce — a doorway never
  reports slurred speech, however the text is worded;
* severities are the escalation ladder's own vocabulary, so a cue's urgency is
  decided once rather than translated on the way in;
* and a critical cue reaches a person, because `jim/noticed.py` excludes
  `critical` from the pass that puts things to a model.
"""

from __future__ import annotations

import inspect

import pytest

from jim import cues, daybook, escalation, monitors

from .conftest import enroll


def _on(client, uid, monitor, **body):
    spec = monitors.MONITORS[monitor]
    body.setdefault("others_told", spec.catches_others)
    r = client.put(f"/monitors/{uid}/{monitor}", json=body)
    assert r.status_code == 200, r.text


def _sensed(client, uid, monitor, content):
    r = client.post(f"/monitors/{uid}/{monitor}/sensed",
                    json={"content": content})
    assert r.status_code == 200, r.text
    return r.json()


# --------------------------------------------------------------------------
# Noticing is free of retention. That is the whole arrangement.
# --------------------------------------------------------------------------

def test_it_notices_the_fall_and_keeps_nothing(client):
    """`jim/monitors.py` opens by saying *"it notices you fell" and "it keeps
    the video of you falling" are different agreements*. Until cues existed
    that sentence was honest only because the code did neither."""
    uid = enroll(client)
    _on(client, uid, "room_camera")          # keeping is off by default
    out = _sensed(client, uid, "room_camera",
                  "she is on the floor and not moving")

    assert [c["cue"] for c in out["cues"]] == ["fall", "not_moving"]
    assert out["kept"] is False
    assert out["dropped_because"] == "keeping_is_off"
    assert client.get(f"/day/{uid}").json()["survived"] == []


def test_the_cue_is_read_before_keeping_is_even_asked():
    """Checked in the source, because the other order produces identical
    output on a monitor that keeps things and silently produces nothing on
    one that does not — which is most of the roster."""
    source = inspect.getsource(daybook.sensed)
    assert source.index("cues.seen") < source.index("_may_keep")


def test_keeping_switched_on_changes_what_is_stored_and_not_what_is_noticed(
        client):
    """The same cues either way. If retention changed detection, switching it
    off would quietly switch off the guardian."""
    uid = enroll(client)
    _on(client, uid, "room_camera")
    off = _sensed(client, uid, "room_camera", "he has fallen")
    _on(client, uid, "room_camera", keeping=True)
    on = _sensed(client, uid, "room_camera", "he has fallen")

    assert [c["cue"] for c in off["cues"]] == [c["cue"] for c in on["cues"]]
    assert off["kept"] is False and on["kept"] is True


def test_a_monitor_that_holds_nothing_at_all_still_notices(client):
    """The hardest case for this rule and the one it exists for.

    The earpiece promises *nothing* outright — not *nothing unless* — and it
    is the one row on the roster that both promises nothing and can sense
    something a cue is read from. So it is the proof: a verbal cue read, and
    not one word of what it was read from kept, with no switch anywhere that
    could change either half.
    """
    uid = enroll(client)
    _on(client, uid, "earpiece", keeping=True)
    out = _sensed(client, uid, "earpiece", "help me, i can't get up")

    assert [c["cue"] for c in out["cues"]] == ["calling_for_help"]
    assert out["kept"] is False
    assert out["dropped_because"] == "holds_nothing"
    assert client.get(f"/day/{uid}").json()["survived"] == []


# --------------------------------------------------------------------------
# The words are never what is kept.
# --------------------------------------------------------------------------

def test_the_sentence_a_cue_was_read_from_is_not_stored(client):
    """Otherwise this module is the way round the roster — read the cue and
    stash the description, on a monitor that promised nothing."""
    uid = enroll(client)
    _on(client, uid, "room_speaker")
    secret = "i can't get up and the safe code is 4417"
    _sensed(client, uid, "room_speaker", secret)

    seen = client.get(f"/cues/{uid}").json()["lately"]
    assert [c["cue"] for c in seen] == ["calling_for_help"]
    blob = repr(seen) + repr(client.get(f"/day/{uid}").json())
    assert "4417" not in blob
    assert secret not in blob


def test_nothing_a_cue_writes_carries_the_words(client):
    """The row takes the cue's name, its monitor and its reference. Checked
    against what is actually written rather than against the shape of the
    function, because the detail column is free-form JSON and would take the
    sentence without complaining."""
    import json
    from jim import db
    uid = enroll(client)
    _on(client, uid, "room_speaker")
    said = "somebody help, the pin is 9931"
    _sensed(client, uid, "room_speaker", said)

    rows = db.connect().execute(
        "SELECT condition, detail FROM events WHERE user_id=?"
        " AND type='detection'", (uid,)).fetchall()
    assert [r["condition"] for r in rows] == ["calling_for_help"]
    detail = json.loads(rows[0]["detail"])
    assert "9931" not in json.dumps(detail)
    assert said not in json.dumps(detail)
    # What it does carry: why, which monitor, and the reference behind it.
    assert set(detail) == {"reason", "monitor", "reference", "tier"}


# --------------------------------------------------------------------------
# A monitor only yields cues its own senses can produce.
# --------------------------------------------------------------------------

def test_a_doorway_reports_nothing_however_the_text_reads(client):
    """It senses a presence and nothing else. The cheap version of this
    module — scan every text for every cue — would have it reporting slurred
    speech, and the roster's `senses` column would be decoration."""
    assert cues.for_monitor("doorway") == []
    assert cues.read("doorway", "on the floor, slurred, calling for help") == []


def test_a_camera_does_not_hear_and_a_speaker_does_not_see():
    heard = "i can't get up"
    seen = "lying on the ground"
    assert cues.read("room_camera", heard) == []
    assert cues.read("room_speaker", seen) == []
    assert [c["cue"] for c in cues.read("room_camera", seen)] == ["fall"]
    assert [c["cue"] for c in cues.read("room_speaker", heard)] == [
        "calling_for_help"]


def test_the_sense_filter_reads_the_roster_rather_than_a_second_list():
    assert "spec.senses" in inspect.getsource(cues.for_monitor)


def test_no_cue_is_read_out_of_a_sense_nothing_has():
    """A cue nothing can produce is a row that will never fire, and the
    failure is silent — it does not error, it never appears."""
    assert cues._senses_are_honest() == []


def test_an_unknown_monitor_is_refused_rather_than_scanned():
    with pytest.raises(monitors.NoSuchMonitor):
        cues.read("not_a_monitor", "on the floor")


# --------------------------------------------------------------------------
# One ladder, not two.
# --------------------------------------------------------------------------

def test_every_cue_is_graded_in_the_ladders_own_words():
    """`jim/hazards.py` grades rows critical/warning/notice, which is a good
    scale and is not this one. A cue graded in the wrong vocabulary reaches
    `escalation.decide` as an unknown word and is treated as the mildest
    thing it could be."""
    assert cues._severities_are_the_ladders() == []


def test_a_critical_cue_is_resolved_by_the_ladder_that_already_exists(client):
    uid = enroll(client, emergency_phone="+15550000")
    _on(client, uid, "room_camera")
    out = _sensed(client, uid, "room_camera", "he collapsed")
    fall = next(c for c in out["cues"] if c["cue"] == "fall")
    assert fall["severity"] == "critical"
    assert fall["tier"] in escalation.TIERS
    assert "escalation.decide" in inspect.getsource(cues.seen)


def test_a_critical_cue_never_becomes_a_paid_model_turn(client):
    """The two modules compose without either knowing about the other:
    `noticed.due` selects `info` and `guidance` only, so a critical cue goes
    to a person rather than into the unattended pass."""
    from jim import noticed
    uid = enroll(client)
    _on(client, uid, "room_camera")
    _sensed(client, uid, "room_camera", "she has fallen")
    assert "critical" not in noticed.HANDLES
    assert [d["condition"] for d in noticed.due(uid)] == []


def test_a_guidance_cue_is_something_the_coach_will_try_first(client):
    """The other half of the same composition — an ordinary cue is exactly
    what the free half of the ladder is for."""
    from jim import noticed
    uid = enroll(client)
    _on(client, uid, "room_camera")
    _sensed(client, uid, "room_camera", "he looked unsteady")
    assert "unsteady" in [d["condition"] for d in noticed.due(uid)]


# --------------------------------------------------------------------------
# What a person can be told before switching one on.
# --------------------------------------------------------------------------

def test_a_screen_can_say_what_each_monitor_could_ever_notice(client):
    """*This one can notice you fell; it cannot hear you call out* is the
    honest sentence beside a switch."""
    uid = enroll(client)
    can = client.get(f"/cues/{uid}").json()["can_read"]
    assert can["room_camera"] == ["fall", "not_moving", "unsteady"]
    assert "calling_for_help" in can["room_speaker"]
    assert can["doorway"] == []


def test_every_cue_says_what_it_means_and_where_it_came_from():
    """The same standard `jim/hazards.py` holds: what it flags it can
    explain."""
    for name, cue in cues.CUES.items():
        assert cue["says"], name
        assert cue["reference"], name
        assert cue["phrases"], name
        assert cue["sense"] in cues.SENSES, name


@pytest.mark.parametrize("name", sorted(cues.CUES))
def test_every_cue_is_a_word_somebody_can_read(name):
    assert name and name.replace("_", "").isalpha()


def test_a_stranger_cannot_read_what_a_room_noticed(client):
    a = enroll(client)
    outsider = enroll(client)
    head = {"authorization": client.headers["authorization"]}
    r = client.get(f"/cues/{a}", headers=head)
    assert r.status_code == 403, r.text
