"""A switch is not a sensor.

Field report, reading the task window against a house with nothing
paired: "my wrist, ring, glasses, room, camera, speaker, doorway are all
showing sensing, but without actually being able to physically connect
the device via Bluetooth, JIM has no way to actually monitor what I have
stored."

    asked     is this monitor switched on
    mattered  has anything ever arrived from it

Exactly right, and the word was the lie. `switched_on` is a PERMISSION —
this person said this monitor may sense — and every surface was printing
it as a fact about the world. Nothing had arrived from any of them,
because nothing was connected to send it.

"Has anything ever arrived" is the fact these tables can actually
establish, and it is honest for both kinds of monitor: a wrist band that
reports continuously and a doorway that only fires when somebody passes
are both silent until they are real.
"""

from __future__ import annotations

from pathlib import Path

from jim import monitors, underway

from .conftest import enroll

REPO = Path(__file__).resolve().parents[2]


def _wrist(rows: list[dict]) -> dict:
    return next(r for r in rows if r["name"] == "wrist")


def test_a_monitor_nobody_switched_on_is_off(client):
    user = enroll(client)
    assert _wrist(monitors.roster(user))["standing"] in ("off", "waiting")


def test_switching_one_on_does_not_make_it_sense(client):
    """The defect itself. Flipping the switch is permission, and permission
    is not a reading."""
    user = enroll(client)
    monitors.plug_in(user, "wrist", device_name="my watch")
    row = _wrist(monitors.roster(user))
    assert row["on"] is True
    assert row["standing"] == "waiting", (
        "a switched-on monitor with nothing connected still calls itself "
        "sensing — this is the field report, exactly")
    assert row["last_sensed"] is None


def test_something_arriving_is_what_makes_it_sense(client):
    from jim import daybook

    user = enroll(client)
    monitors.plug_in(user, "wrist", device_name="my watch")
    daybook.sensed(user, "wrist", "resting, steady")
    row = _wrist(monitors.roster(user))
    assert row["standing"] == "sensing"
    assert row["last_sensed"], "the roster cannot say when it last heard"


def test_the_window_says_waiting_rather_than_sensing(client):
    """The task window is where the field report read the claim."""
    user = enroll(client)
    monitors.plug_in(user, "wrist", device_name="my watch")
    rows = [r for r in underway.window(user)["underway"]
            if r["kind"] == "monitor"]
    assert rows, "a switched-on monitor left the window entirely"
    assert all(r["why"] == "waiting" for r in rows), (
        "the window still reports every switched-on row as running")


def test_a_waiting_monitor_still_appears(client):
    """It is a thing this person switched on and is owed an answer about.
    Dropping it would hide the very state they need to act on."""
    user = enroll(client)
    monitors.plug_in(user, "ring", device_name="")
    terms = [r["term"] for r in underway.window(user)["underway"]
             if r["kind"] == "monitor"]
    assert "ring" in terms


def test_the_windows_own_word_is_a_noun():
    """`und.kind.monitor` read "sensing", so every row said it before the
    standing was even consulted."""
    l10n = (REPO / "app/src/l10n.ts").read_text(encoding="utf-8")
    block = l10n[l10n.index('"und.kind.monitor"'):]
    block = block[:block.index("},")]
    assert '"sensing"' not in block, (
        "the kind label is a verb again, so the row claims sensing "
        "whatever the standing says")
    assert '"und.why.waiting"' in l10n and '"und.why.sensing"' in l10n, (
        "the standing has no words to print")
