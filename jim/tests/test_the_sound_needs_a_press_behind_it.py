"""A phone plays what a press started, and nothing else.

The sibling product got the field report — *"on the mobile device it's not
playing voice audio whatsoever"* — and this one has the same eight lines with
a kinder-looking failure that is arguably worse.

A phone withholds autoplay unless the playback descends from a real press.
The grant lands on an **element** a person started and outlives the gesture,
so one element opened at the door plays every later piece. `speech.ts` built
a `new Audio()` per piece, after an await on the synthesis fetch — by then
the press was over and each new element carried no activation.

Here a refused piece falls back to `sayOnDevice`, so nothing goes silent.
What happens instead is that the configured voice — the one somebody chose,
paid an engine for, in some cases cloned from their own throat — never plays
a single piece on a phone, and the browser's robot reads every reply. The
product looks like it is working. That is why it needed a report from a
person rather than a stack trace.

    asked     which voice is speaking
    mattered  is it the one that was chosen

A laptop allows all of it, which is exactly why this survived every round.
"""

from __future__ import annotations

import re
from pathlib import Path


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
SPEECH = REPO / "app" / "src" / "speech.ts"

#: The only two things this module may build an element around. `SILENCE`
#: is the opener's inaudible clip, played inside a press so the element
#: carries the grant; the bare one stands in for a screen that never
#: pressed. Anything else is a piece being given its own element.
ALLOWED_AUDIO_ARGS = ("", "SILENCE")


def _code() -> str:
    """Source with comments stripped.

    The header above `ear` describes the mistake in the same words the
    code would use, and a reader that counts a mention as a use invents a
    defect out of its own documentation.
    """
    text = SPEECH.read_text(encoding="utf-8")
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    return re.sub(r'^\s*//[^\n]*$', '', text, flags=re.M)


def test_a_piece_is_not_played_through_a_brand_new_element():
    """Stated as a shape, not as a spelling.

    The sibling's first draft of this guard looked for
    `new Audio(URL.createObjectURL(...))` and passed against the source it
    was written to fail, because the blob sat one variable away. Matching
    the defect's spelling catches only the defect already known about.
    """
    built = [a.strip() for a in re.findall(r'new Audio\(([^)]*)\)', _code())]
    wrong = [a for a in built if a not in ALLOWED_AUDIO_ARGS]
    assert not wrong, (
        f"new Audio({wrong[0]}) — an element built around something other "
        f"than {' or '.join(x or 'nothing' for x in ALLOWED_AUDIO_ARGS)}. "
        "If that is a piece, a phone refuses it and the reply falls out of "
        "the chosen voice into the device robot. Set `.src` on the element "
        "a press opened instead.")


def test_the_ear_is_opened_by_a_press_and_reused():
    """One long-lived element, and a press that opens it."""
    code = _code()
    assert "export function openTheEar" in code, (
        "no openTheEar(): the first piece is then the first time this page "
        "asks to make a sound, which is the one moment a phone says no")
    assert re.search(r'^armTheEar\(\);', code, re.M), (
        "openTheEar exists but nothing arms it. Wiring it into each "
        "screen's press handlers is the version that ships with one screen "
        "forgotten; arm it once, on any press.")
    assert re.search(r'audio\.src = ', code), (
        "nothing assigns `.src` — pieces are not played through a reused "
        "element")


def test_the_object_url_of_a_played_piece_is_released():
    """Every URL made for a piece is given back.

    Not the reported defect — found while fixing it. A reply of nine
    sentences made nine blob URLs and released none, and a standing
    conversation makes a reply a minute. The blob cannot be collected while
    a URL for it exists, so this held every clip of a conversation in
    memory until the tab closed.
    """
    code = _code()
    made = len(re.findall(r'URL\.createObjectURL\(', code))
    freed = len(re.findall(r'URL\.revokeObjectURL\(', code))
    assert made and freed >= made, (
        f"{made} object URL(s) made for pieces and {freed} released — a "
        "blob whose URL is still alive cannot be collected, so a standing "
        "conversation keeps every clip it ever played")
