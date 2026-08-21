"""The console listens for the cue words, and the vocabulary stays home.

A field request: while monitoring is on and the app is open, the microphone
should be listening for the words the cues know — "help me", "call an
ambulance" — without anybody holding a button. The obvious build copies the
word list into the client and spots keywords there. That build is wrong
twice: the copy drifts from the list that decides (jim/cues.py), and a
client that sends only the words it recognised has quietly become the judge
of what counts as a call for help.

    asked     does the console hear the words the cues know
    mattered  who decides what a call for help sounds like

So the ear sends everything it hears through the monitor door
(`POST /monitors/{uid}/{name}/sensed`), the server matches the vocabulary,
and the roster's consent rules gate every submission the same as any other
sensing. This file pins the edges that made that shape honest.
"""

from __future__ import annotations

import re
from pathlib import Path

from jim import cues

REPO = Path(__file__).resolve().parents[2]
EAR = (REPO / "app/src/ear.ts").read_text(encoding="utf-8")
WIDGET = (REPO / "app/src/GuardianLights.tsx").read_text(encoding="utf-8")
SPEECH = (REPO / "app/src/speech.ts").read_text(encoding="utf-8")
L10N = (REPO / "app/src/l10n.ts").read_text(encoding="utf-8")

LANGS = ("en", "es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar")


def test_the_ear_goes_through_the_monitor_door():
    """Everything heard is submitted through the binding the roster already
    gates — not a new route, and never a client-side verdict."""
    assert "api.monitorSensed(" in EAR
    assert not re.search(r"req[<(]", EAR), (
        "the ear calls the transport directly — that is a new door")


def test_no_cue_phrase_lives_on_the_client():
    """The vocabulary that decides is the server's copy, and there is no
    other. Any phrase from jim/cues.py appearing in the client would be the
    start of the drifting duplicate this build refused to make."""
    client = (EAR + WIDGET).lower()
    for cue in cues.CUES.values():
        for phrase in cue["phrases"]:
            assert phrase.lower() not in client, (
                f"the cue phrase {phrase!r} is written into the client — "
                "the vocabulary lives in jim/cues.py and only there")


def test_a_voice_does_not_testify_about_itself():
    """The Guardian's replies come out of the speaker the microphone faces.
    A coach saying "call an ambulance if this worsens" is advice; sensed
    back through the door it would be a cue. Everything heard while the
    console is speaking is dropped before submission."""
    m = re.search(r"onresult = (.*?)\n    \};", EAR, re.S)
    assert m, "the ear no longer has an onresult to check"
    body = m.group(1)
    assert "speakingNow()" in body
    assert body.index("speakingNow()") < body.index("api.monitorSensed("), (
        "the speaking check comes after the submission it exists to stop")


def test_speaking_now_ends_when_the_reply_does():
    """`speakingNow()` reads the module's `current` audio, and `current`
    used to stand until the next say() or hush(). Between replies the ear
    would have stayed deaf — so a played-out reply clears it."""
    assert "speakingNow" in SPEECH
    assert re.search(r"if \(current === audio\) current = null;", SPEECH), (
        "a reply that played out still counts as speaking — the ear is "
        "deaf between replies")


def test_the_ear_stands_back_up():
    """Recognisers end themselves on silence timeouts and service hiccups.
    A standing ear restarts on onend; only stop() and a refusal end it."""
    assert "continuous = true" in EAR
    m = re.search(r"onend = (.*?)\n    \};", EAR, re.S)
    assert m and "start" in m.group(1) and "stopped" in m.group(1), (
        "onend does not re-arm — the first silence timeout ends the ear")


def test_only_a_refusal_stops_it_for_good():
    m = re.search(r"onerror = (.*?)\n    \};", EAR, re.S)
    assert m, "the ear no longer has an onerror to check"
    body = m.group(1)
    for refusal in ("not-allowed", "service-not-allowed"):
        assert refusal in body
    assert "stopped = true" in body, (
        "a refusal does not stop the ear — it will re-ask for the "
        "microphone every 400ms forever")


def test_the_row_needs_a_plugged_sound_monitor():
    """No ear without a door to bring sound to: the row appears only when a
    sound-sensing monitor is on, so what is heard always lands where the
    roster's consent rules (`may_sense`, `others_told`) already govern."""
    assert re.search(r"r\.on && r\.senses\.includes\(\"sound\"\)", WIDGET), (
        "the ear row is not gated on a plugged sound monitor")
    assert "standEar(" in WIDGET


def test_the_switch_is_a_choice_this_browser_remembers():
    """On is something the person did, never a default: the toggle writes
    localStorage and the ear stands only while it reads back on."""
    assert 'localStorage.getItem(EAR_KEY) === "1"' in WIDGET
    assert "localStorage.removeItem(EAR_KEY)" in WIDGET


def test_every_word_the_ear_shows_is_on_the_table():
    for key in ("lights.ear", "lights.ear.start", "lights.ear.stop",
                "lights.ear.on", "lights.ear.refused", "lights.ear.none"):
        block = re.search(rf'"{re.escape(key)}":\s*\{{(.*?)\n  \}}', L10N, re.S)
        assert block, f"{key} is not on the console's table"
        for lang in LANGS:
            assert re.search(rf"\b{lang}:", block.group(1)), (
                f"{key} has no {lang} translation")
