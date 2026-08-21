"""A wrist that reports stops saying `waiting`.

The roster used to print `sensing` over every switched-on row, and a field
report caught it against a house where nothing was connected: "all showing
sensing, but without actually being able to physically connect the device,
JIM has no way to actually monitor what I have stored." So `roster` learned
to derive that word from moments actually recorded — off, waiting, sensing.

Which left the same lie facing the other way, and building a watch is what
walked into it. Readings arrive through `POST /monitor/{uid}`, that door
recorded no moment, and nothing else on the wrist path did either. A watch
posting a pulse every sixty seconds would leave the wrist row reading
`waiting` forever.

    asked     did a reading arrive
    mattered  can the roster tell

## The decision that took the thinking

The reading is **not** gated on the switch. The vitals ladder is not the
monitor roster and never has been: `/monitor/{uid}` has accepted samples
since long before monitors existed, and refusing to notice a dangerous
heart rate because a settings toggle is off would be a safety regression
dressed as consistency.

What the switch decides is whether the *day* gets to remember it — the
roster's own promise, enforced where it always was, in `daybook.sensed`
through `monitors.may_sense`. So a reading off an unswitched row is graded
exactly as before and the answer says `off`, which is the same word the
roster prints about the same fact.
"""

from __future__ import annotations

from jim import monitors

from .conftest import enroll


def _sample(client, uid, **kw):
    return client.post(f"/monitor/{uid}", json={"heart_rate": 72, **kw})


# -- the reading is recorded, and the roster can tell -------------------------

def test_a_named_reading_turns_the_row_from_waiting_to_sensing(client):
    uid = enroll(client)
    monitors.plug_in(uid, "wrist")

    row = [m for m in client.get(f"/monitors/{uid}").json()
           if m["name"] == "wrist"][0]
    assert row["standing"] == "waiting", (
        "a monitor switched on and never reported is waiting, not sensing")

    r = _sample(client, uid, monitor="wrist")
    assert r.status_code == 200, r.text
    assert r.json()["standing"] == "sensing"

    row = [m for m in client.get(f"/monitors/{uid}").json()
           if m["name"] == "wrist"][0]
    assert row["standing"] == "sensing"
    assert row["last_sensed"]


def test_an_unnamed_reading_changes_nothing_about_the_roster(client):
    """Every client that ever posted a sample keeps working, and keeps
    claiming nothing. Optional means optional."""
    uid = enroll(client)
    monitors.plug_in(uid, "wrist")
    r = _sample(client, uid)
    assert r.status_code == 200
    assert "standing" not in r.json()
    row = [m for m in client.get(f"/monitors/{uid}").json()
           if m["name"] == "wrist"][0]
    assert row["standing"] == "waiting"


# -- and the ladder is not gated on a switch ---------------------------------

def test_a_reading_off_a_row_nobody_switched_on_is_still_graded(client):
    """The load-bearing one. A settings toggle must never be the reason a
    dangerous reading goes ungraded."""
    uid = enroll(client)                       # wrist never switched on
    r = _sample(client, uid, heart_rate=178, monitor="wrist")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["standing"] == "off", (
        "the day should not remember a monitor nobody switched on")
    # Whatever the ladder decided, it decided something — the sample went
    # through `guardian.monitor` exactly as an unnamed one would.
    assert set(body) - {"monitor", "standing"}, (
        "naming a monitor swallowed the reading's own answer")


def test_the_two_doors_print_one_word_about_one_fact(client):
    """`standing` here means what `standing` means on the roster. A second
    vocabulary for the same fact is how a screen ends up disagreeing with
    the screen next to it."""
    uid = enroll(client)
    monitors.plug_in(uid, "wrist")
    said = _sample(client, uid, monitor="wrist").json()["standing"]
    row = [m for m in client.get(f"/monitors/{uid}").json()
           if m["name"] == "wrist"][0]
    assert said == row["standing"]


def test_a_monitor_that_does_not_exist_is_refused(client):
    """Not silently ignored: a client naming a row that is not on the roster
    has a bug, and swallowing it would let that bug ship to a wrist."""
    uid = enroll(client)
    r = _sample(client, uid, monitor="left_elbow")
    assert r.status_code == 422
    assert "monitor" in r.text


def test_the_reading_is_the_moment_and_carries_no_content(client):
    """`daybook.sensed` is called with no content on purpose. A heart rate
    is a number the vitals history already keeps; writing it into the day's
    content as well would put a reading in two places and make forgetting
    it a two-step job."""
    uid = enroll(client)
    monitors.plug_in(uid, "wrist")
    _sample(client, uid, monitor="wrist")
    day = client.get(f"/day/{uid}").json()
    for moment in day.get("kept", []):
        if moment.get("monitor") == "wrist":
            assert not moment.get("content"), (
                "the reading was written into the day's content as well as "
                "the vitals history")
