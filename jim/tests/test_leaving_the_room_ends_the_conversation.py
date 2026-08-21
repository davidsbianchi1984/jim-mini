"""Leaving the room ends the conversation.

    asked     what happens to the voice when the screen goes away
    mattered  a conversation with no screen is a hot microphone

None of the five conversation screens had an unmount teardown.
Navigating away mid-reply left a headless loop: the reply kept
speaking, and the standing conversation — whose whole design is to
re-open the microphone after each turn — kept doing exactly that under
a screen that no longer exists. The person is on the Baseline screen;
the Guardian is still listening to the kitchen.

Every screen that runs the standing conversation now tears it down on
unmount through its own `exitTalk()` — the same door the veil tap uses,
so there is exactly one way a conversation ends.
"""

from __future__ import annotations

import re
from pathlib import Path

APP = Path(__file__).resolve().parents[2] / "app/src/screens"

# Every screen wearing the standing-conversation machinery. Engaged and
# Checkin joined the roster when the voice conversation reached them —
# a new screen that gains `exitTalk` must join this list.
SCREENS = ("Coach", "Talk", "Engaged", "Monitor", "Checkin")


def test_every_conversation_screen_tears_down_on_unmount():
    for screen in SCREENS:
        src = (APP / f"{screen}.tsx").read_text(encoding="utf-8")
        assert re.search(r"useEffect\(\(\) => \(\) => exitTalk\(\), \[\]\)",
                         src), (
            f"{screen}.tsx has no unmount teardown — navigating away "
            "mid-conversation leaves the voice talking and the standing "
            "loop re-opening the microphone with no screen behind it")


def test_no_screen_grew_the_machinery_without_joining_the_roster():
    for path in sorted(APP.glob("*.tsx")):
        src = path.read_text(encoding="utf-8")
        if "function exitTalk" in src:
            assert path.stem in SCREENS, (
                f"{path.name} runs a standing conversation but is not in "
                "this guard's roster — add it, and give it the unmount "
                "teardown")


def test_the_one_shot_dictation_lets_go_of_the_microphone_too():
    """Journal's mic is one listen, not a standing loop — but on a
    platform without the silence watcher, an abandoned recording held
    the microphone open until somebody came back to tap it."""
    src = (APP / "Journal.tsx").read_text(encoding="utf-8")
    assert re.search(
        r"useEffect\(\(\) => \(\) => \{ recorder\.current\?\.stop\(\)", src), (
        "Journal.tsx no longer stops its recorder on unmount")
