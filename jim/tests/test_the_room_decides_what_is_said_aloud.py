"""The surface rule stops being a label.

`surfaces()` has reported `reads_health_aloud` since the picker shipped in
0.50.0, and until this round **nothing read it**. Every consumer in the
codebase was a screen rendering the word "shown" or "aloud" next to a button:
the console, three native shells, and nothing else. Grep it and the shape is
plain — a promise stated on the wire with no code path enforcing it.

So a client could have taken a beat about somebody's resting rate and put it
through a living-room speaker, and no part of this product would have stopped
it or known it happened. The picker looked like a safety feature and was a
caption.

This file is the enforcement, and the assertions are in the order they matter:

1. **a shared surface does not speak a vital**, and the response carries no
   spoken line at all — the refusal is a state, not a warning label;
2. **it does still reach the person**, shown rather than spoken, because a
   guardian that goes silently quiet has taken the beat away rather than
   moved it;
3. **a private surface speaks the same beat** — the rule is about the room,
   not about the subject, and a rule that silenced earbuds too would be one
   people turn off;
4. **a harmless line is not withheld on a speaker.** This is the direction
   safety features usually fail: over-withhold, become useless, get disabled.
"""

import pytest

import jim.presence as presence
from jim.tests.conftest import enroll


def _lonely(client) -> str:
    """Somebody with three low check-ins — a beat about their state."""
    user = enroll(client)
    for _ in range(3):
        client.post(f"/checkin/{user}", json={"mood": 1, "energy": 1})
    return user


def test_a_speaker_does_not_read_somebodys_state_into_a_room(client):
    """The assertion this file exists for."""
    user = _lonely(client)
    client.put(f"/presence/{user}/surface", json={"speaks_on": "speaker"})
    body = client.get(f"/presence/{user}/say?slot=morning").json()

    assert body["speak"] is True, "there was no beat to withhold — test is moot"
    assert body["spoken"] is False, (
        "a speaker read somebody's state out loud into a room other people "
        "are in — this is the failure the surface picker claims to prevent")
    assert body["withheld"], "it refused without saying what it was holding"
    assert body["why_not_aloud"]


def test_the_beat_still_reaches_them_on_the_screen(client):
    """Withheld is not deleted.

    A guardian that goes quiet because the room is wrong has taken the beat
    away rather than moved it, and the person never learns there was one.
    """
    user = _lonely(client)
    client.put(f"/presence/{user}/surface", json={"speaks_on": "speaker"})
    body = client.get(f"/presence/{user}/say?slot=morning").json()
    assert body["shown"] is True
    assert body["line_key"] and body["english"]
    assert body["because"], "it withheld the reason along with the voice"


def test_the_same_beat_is_spoken_into_an_ear(client):
    """The rule is about the room, not the subject. A version that silenced
    earbuds too would be one people turn off, and then nothing is protected."""
    user = _lonely(client)
    client.put(f"/presence/{user}/surface", json={"speaks_on": "earbuds"})
    body = client.get(f"/presence/{user}/say?slot=morning").json()
    assert body["spoken"] is True, body
    assert body["withheld"] == []


@pytest.mark.parametrize("surface", ["speaker", "glasses", "ar"])
def test_every_shared_surface_holds_it_back(client, surface):
    """Glasses and AR are the same problem as a speaker with a nicer name:
    audio into a shared space, and a room that did not agree to be in it."""
    user = _lonely(client)
    client.put(f"/presence/{user}/surface", json={"speaks_on": surface})
    body = client.get(f"/presence/{user}/say?slot=morning").json()
    assert body["spoken"] is False, surface
    assert body["surface_is_private"] is False


def test_a_harmless_line_is_not_withheld_on_a_speaker(client):
    """The direction safety features actually fail.

    Over-withholding makes the feature useless, and a useless feature gets
    switched off — taking the real protection with it. "Nice streak on the
    walking" is not a fact about somebody's condition and a speaker may say
    it.
    """
    assert presence.carries("presence.celebrate.streak") == ()
    assert presence.carries("presence.company.here") == ()
    assert presence.carries("presence.curious.open") == ()
    # And a line about the body is not lumped in with them.
    assert "vital" in presence.carries("presence.notice.drift")


def test_a_line_nobody_has_classified_is_withheld_by_default(client):
    """The safe direction to fail in. A beat added in some later round with
    no row in the table is held back on a shared surface until somebody
    decides otherwise — rather than shipping and being read aloud."""
    assert set(presence.carries("presence.some.future.beat")) == \
        set(presence.NOT_ALOUD_IN_COMPANY)


def test_a_surface_with_no_voice_is_not_a_refusal(client):
    """A watch withholds nothing — it simply has no voice. Calling that
    "withheld" would tell somebody their guardian was censoring itself when
    it was only looking at a screen."""
    user = _lonely(client)
    client.put(f"/presence/{user}/surface", json={"speaks_on": "watch"})
    body = client.get(f"/presence/{user}/say?slot=morning").json()
    assert body["spoken"] is False
    assert body["withheld"] == [], (
        "a silent screen is being reported as a withheld secret")
    assert body["surface_has_audio"] is False


def test_silence_is_not_dressed_up_as_a_refusal(client):
    """When there is no beat there is nothing to withhold, and saying
    "withheld" would invent a refusal that never happened."""
    user = enroll(client)
    client.put(f"/presence/{user}/surface", json={"speaks_on": "speaker"})
    body = client.get(f"/presence/{user}/say?slot=morning").json()
    assert body["speak"] is False
    assert body["spoken"] is False
    assert body["withheld"] == []


# --- the hands-free question ------------------------------------------------

def test_a_device_on_a_timer_asks_one_question(client):
    """`/due` is the whole interface for hands-free. The slot comes from the
    hour rather than the caller, so a watch, a pair of earbuds and a speaker
    cannot disagree about what time of day it is for the same person."""
    user = _lonely(client)
    morning = client.get(f"/presence/{user}/due?hour=8").json()
    assert morning["slot_from_hour"] == "morning"
    assert client.get(f"/presence/{user}/due?hour=13").json()["slot_from_hour"] \
        == "midday"
    assert client.get(f"/presence/{user}/due?hour=21").json()["slot_from_hour"] \
        == "evening"
    assert morning["due"] is True


def test_asking_whether_it_is_time_does_not_count_as_being_told(client):
    """A device polling every ten minutes must not burn the day's beat.

    `/due` deliberately does not record: a line somebody never heard, filed
    as said, is a line they never get — and a hands-free product polls a lot.
    """
    user = _lonely(client)
    assert client.get(f"/presence/{user}/due?hour=8").json()["due"] is True
    assert client.get(f"/presence/{user}/due?hour=8").json()["due"] is True, (
        "polling consumed the beat — the person would never hear it")
    # And the real utterance still happens.
    assert client.get(f"/presence/{user}/say?slot=morning").json()["speak"] \
        is True


def test_due_carries_the_surface_decision_with_it(client):
    """So a device does not have to make the call itself. Handing a client
    the line and letting it decide whether the room is safe is how the
    picker became a caption in the first place."""
    user = _lonely(client)
    client.put(f"/presence/{user}/surface", json={"speaks_on": "speaker"})
    body = client.get(f"/presence/{user}/due?hour=8").json()
    assert body["due"] is True
    assert body["spoken"] is False and body["shown"] is True


def test_nothing_speaks_a_beat_without_going_through_the_rule():
    """The guard that keeps this from rotting.

    `voice.speak` is reachable from `POST /voice/speak` with arbitrary text —
    that is a person's own words and not this module's business. What must
    never appear is a presence path that reaches synthesis on its own: the
    moment `presence.py` imports the voice layer, the decision above can be
    skipped, which is exactly how the rule became a label the first time.
    """
    import pathlib
    import re
    src = pathlib.Path(presence.__file__).read_text(encoding="utf-8")
    assert not re.search(r"^\s*(from \. import voice|import voice|from \.voice)",
                         src, re.M), (
        "the presence reaches the voice layer directly — every beat must go "
        "through say(), which is the only thing that knows about the room")


def test_the_rule_is_readable_rather_than_inferred():
    """Every line key the module can emit has a row.

    Inferring from the area was the first draft and it is too coarse in the
    direction that matters: `health_fitness` covers both "your resting rate
    has been high for four days" and "nice streak on the walking". A rule
    treating those the same either leaks the first or silences the second.
    """
    missing = sorted(set(presence.LINES) - set(presence.SPOKEN_CARRIES))
    assert not missing, (
        f"{len(missing)} line(s) have no row in SPOKEN_CARRIES and would be "
        f"withheld everywhere by the safe default: {missing}")
