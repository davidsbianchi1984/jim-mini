"""The refusal named a remedy, and the remedy was already switched on.

0.72.2 replaced a raw error code with a sentence: *the operating system
refused the device's recogniser — on iPhone and iPad that is Dictation being
switched off*. It was reported from the field with a screenshot of Settings
showing Dictation **on**.

    asked     does the refusal name a remedy
    mattered  is the remedy the reason

So the person was sent to a switch already thrown, and when throwing it
changed nothing the conclusion available to them was that the product is
broken. That is worse than the code it replaced: a code is unhelpful and
admits it, while a confident wrong diagnosis spends trust as well as time.

`service-not-allowed` is WebKit's answer for *the speech service will not
serve this page*, and Dictation is one of several ways to arrive there —
Screen Time can withhold Siri & Dictation entirely, an embedded web view
never gets the recogniser however the phone is configured, and the service
is a network service that can simply be unreachable. None of those is
readable from a page.

The guard next door asserted only that the word "Dictation" appears, which
the wrong sentence also satisfied. This is the missing half: a refusal may
list causes and must not assert one.
"""

from __future__ import annotations

import re
from pathlib import Path
from . import ratchets

SPEECH = Path(__file__).resolve().parents[2] / "app" / "src" / "speech.ts"


def _refusal() -> str:
    """The body of `platformRefusal`, which is the sentence a person reads."""
    text = SPEECH.read_text(encoding="utf-8")
    start = text.index("export function platformRefusal")
    end = text.index("\n}", start)
    return text[start:end]


def test_it_does_not_assert_one_cause_as_fact():
    """The exact shape of the defect: *that is X* names a single reason for a
    failure with several, and the page cannot tell which one fired."""
    body = _refusal().lower()
    for claim in ("that is dictation", "which is dictation",
                  "because dictation", "means dictation"):
        assert claim not in body, (
            f"the refusal asserts {claim!r} — `service-not-allowed` has "
            "several causes and none of them is visible from a page")


def test_it_still_names_dictation_among_the_places_to_look():
    """Retreating to 'something went wrong' would undo the round that put a
    remedy in the sentence at all. The fix is to stop asserting, not to stop
    helping."""
    body = _refusal()
    assert "Dictation" in body
    assert "Settings" in body


#: The causes this refusal is meant to name. Held here rather than inside the
#: test so the floor under it counts the same three.
CAUSES = ("Enable Dictation", "Screen Time", "unreachable")


def _places_named() -> int:
    """How many of the known causes the sentence actually names."""
    body = _refusal()
    return sum(term in body for term in CAUSES)


def test_it_names_more_than_one_place_to_look():
    """A list of one is an assertion wearing a list's clothes."""
    places = _places_named()
    assert places >= ratchets.floor("refusal.places_named"), (
        f"only {places} of the three known causes are named — the sentence "
        "reads as a diagnosis again")


def test_the_cause_with_a_door_is_named_before_the_one_without():
    """The third report, and the one that ended the hunt.

    Dictation on, Screen Time restrictions switched off entirely, still
    refused — because no transcription key is configured for the app. With
    `knownHasService === false`, `listen()` goes straight to the device
    recogniser, iOS refuses it, and every sentence above is about iOS.

        asked     why did the recogniser refuse
        mattered  which of the reasons can this person act on

    "Add a key in Settings" already existed in this file and was reachable
    only when `deviceRecogniser()` returned null. On iOS Safari the
    constructor exists and always fails, so the branch that would have said
    the useful thing is the branch iOS never takes. The constructor being
    present is not the service being available.
    """
    body = _refusal()
    assert "knownHasService === false" in body, (
        "the refusal does not consider whether a service is configured, so "
        "somebody with no key is told about their phone's settings")
    key_at = body.index("add an OpenAI")
    ios_at = body.index("Enable Dictation")
    assert key_at < ios_at, (
        "the platform's refusal is named before the missing key — one of "
        "those has a door and the other does not, and the one without it "
        "should not be read first")


def test_the_screen_time_pointer_names_the_row_that_governs_dictation():
    """The second half of the same field report. Sent to Screen Time, the
    reporter found **Privacy › Speech Recognition: Allow** and reasonably
    concluded that path was clear too.

    It is a different permission. That row governs whether *apps* may use
    the speech-recognition API; Siri & Dictation lives under Allowed Apps &
    Features — or Intelligence & Siri on newer iOS — and can be withheld
    while the Privacy row still reads Allow.

        asked     does the sentence name Screen Time
        mattered  does it name the row inside it that does this

    A pointer accurate to the screen and wrong about the row sends somebody
    on the same fruitless walk the first wording did, one level deeper.
    """
    body = _refusal()
    assert "Allowed Apps & Features" in body, (
        "the Screen Time pointer stops at the top of the page, where the "
        "row that reads Allow is not the row that governs dictation")
    assert "Intelligence & Siri" in body, (
        "newer iOS moved these; naming only the old location dates the "
        "sentence to the phone it was written on")
    assert "not the Speech Recognition row" in body, (
        "the sentence does not warn off the row a reporter already checked "
        "and found clear — which is the whole of this finding")


def test_it_says_that_tapping_again_will_not_help():
    """The one thing that *is* certain about this error, and the difference
    from `not-allowed`, which a retry can fix."""
    assert re.search(r"tapping again will not help", _refusal())


def test_it_offers_the_way_round():
    """Somebody who cannot fix the microphone can still use the product, and
    a refusal that does not say so reads as a dead end."""
    assert "type instead" in _refusal()


def test_the_one_cause_it_can_see_is_the_one_it_names_outright():
    """An embedded web view is the case no setting fixes, and the only one
    detectable from a page. Naming it as a possibility beside three settings
    would send somebody through all three for nothing."""
    body = _refusal()
    assert "standalone" in body, (
        "nothing distinguishes another app's web view from Safari, so the "
        "one detectable cause is being offered as a guess like the rest")
    assert "Safari" in body
