"""The turn ends when the talking does, and the voice follows the earbud.

Two field reports off the same session. First, the pause: five seconds of
silence before a turn was judged over read as "still a long delay while
waiting for a response", and the reviewer's number is 2.5. Second, the
route: an earbud connected to the phone, and the conversation came out of
the phone's own speaker while the built-in microphone listened — the
person had to disconnect the earbud to hear their guardian.

    asked     does the conversation use the device already connected
    mattered  nobody connects an earbud hoping the speaker answers

A page cannot re-route the operating system, but it can ask by name: the
connected headset's microphone in getUserMedia (on iOS that request is
also what moves the whole audio session), and the headset speaker via
setSinkId where the platform exposes it. This file pins the number, the
asking, and the two honesty rules that keep the asking from becoming a
refusal: `ideal` rather than `exact`, and a missing setSinkId skipped
rather than crashed on.
"""

from __future__ import annotations

import re
from pathlib import Path

SPEECH = (Path(__file__).resolve().parents[2] / "app/src/speech.ts"
          ).read_text(encoding="utf-8")


def test_the_silence_window_is_the_reviewers_number():
    m = re.search(r"const SILENCE_STOP_MS = (\d+);", SPEECH)
    assert m, "the silence window is gone from speech.ts"
    assert m.group(1) == "2500", (
        f"the silence window is {m.group(1)}ms — the reviewer asked for "
        "2.5 seconds, twice: five was already sent back as too long")


def test_the_microphone_asks_for_the_connected_earbud():
    assert "connectedEar(" in SPEECH
    assert re.search(r'connectedEar\("audioinput"\)', SPEECH), (
        "listen() no longer asks which input is the earbud")
    assert "deviceId: { ideal: mic }" in SPEECH, (
        "the earbud's microphone must be `ideal`, not `exact` — an earbud "
        "that vanished mid-session should degrade to the built-in mic, "
        "not refuse to listen at all")


def test_the_reply_is_pointed_at_the_earbud_where_possible():
    assert re.search(r'connectedEar\("audiooutput"\)', SPEECH), (
        "say() no longer asks which output is the earbud")
    assert '"setSinkId" in audio' in SPEECH, (
        "setSinkId is called unguarded — iOS has no such method and the "
        "reply would die before it played")


def test_a_refused_enumeration_is_the_old_behavior_not_a_failure():
    m = re.search(r"async function connectedEar(.*?)\n\}", SPEECH, re.S)
    assert m and "catch" in m.group(1) and "return null" in m.group(1), (
        "device enumeration can be absent or refused, and the defaults "
        "are what everybody had before this existed — not an error")
