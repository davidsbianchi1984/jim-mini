"""A menu that promises the camera roll must not deliver a directory.

Field report, with the screenshot to match: the composer's + menu offers
Camera, Photos, Microphone — and tapping Photos landed on *Who else is
looking*, the specialists screen. Both picture items navigated to
`attending`, a shortcut wired to the wrong room and never noticed because
the menu itself rendered fine.

    asked     does the menu item open what its label names
    mattered  a label is a promise, and the wrong room breaks it silently

The product's picture surface is the channel screen's camera card — the
one place taking and importing a photograph actually live, body-site
vocabulary and consent included. Camera and Photos land there now, and
`#cam` scrolls the long channel screen to the card itself.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TALK = (REPO / "app/src/screens/Talk.tsx").read_text(encoding="utf-8")
CHANNEL = (REPO / "app/src/screens/Channel.tsx").read_text(encoding="utf-8")


def _menu() -> str:
    m = re.search(r'className="talk-plus" role="menu"(.*?)\n        </div>',
                  TALK, re.S)
    assert m, "the composer's + menu is gone from Talk"
    return m.group(1)


def test_no_picture_item_opens_the_specialists_screen():
    assert 'go("attending")' not in _menu(), (
        "a + menu item navigates to the specialists screen again — the "
        "label promises the camera roll and delivers a directory")


def test_camera_and_photos_land_on_the_camera_card():
    menu = _menu()
    assert menu.count('go("channel")') == 3, (
        "all three + menu items should land on the channel screen, where "
        "the camera card and the microphone both live")
    assert menu.count('window.location.hash = "cam"') == 2, (
        "the two picture items should scroll the channel screen to the "
        "camera card via #cam — landing at the top of that screen is a "
        "scavenger hunt")


def test_the_channel_screen_has_the_card_and_consumes_the_hash():
    assert 'id="cam"' in CHANNEL, (
        "#cam points at nothing — the camera card lost its anchor")
    assert 'window.location.hash === "#cam"' in CHANNEL
    assert "replaceState" in CHANNEL, (
        "the hash is never consumed — every later visit to the channel "
        "screen would jump to the camera card")
