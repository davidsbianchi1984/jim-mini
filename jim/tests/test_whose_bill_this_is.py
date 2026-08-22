"""Entering your own key says you start paying for it.

David, on the beta's arrangement, in his own words:

    "I want all devices that use this app or website to default and
     mandatorily use my personal API keys we are currently using and
     passwords, allowing users for the time being to use my API keys and
     password for beta testing... notified them that they will be charging
     their own accounts instead of using these free API keys and passwords
     that I'm letting them use to pay a test on my dollar."

    asked     can somebody use their own key
    mattered  do they know what changes when they do

The default is deliberate: the deployment's own keys, spent by its owner,
so a tester can try the thing without producing a card. Nothing about
that is a secret and nothing about it is a trap — until somebody types
their own key into the box and the bill silently moves to them.

So the sentence lives **at the box**, not in terms nobody opens. It is
one paragraph under the input, and it says three things: whose keys you
are on now, that their owner is paying, and that the charges become yours
from the moment you save your own.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SETTINGS = (ROOT / "app/src/screens/Settings.tsx").read_text(encoding="utf-8")
L10N = (ROOT / "app/src/l10n.ts").read_text(encoding="utf-8")

KEY = "set.key.whosebill"


def test_the_sentence_sits_at_every_box():
    """Under each input it is about, where a person deciding what to type
    is already looking.

    There are two key boxes on this screen — the model's and the voice's —
    and this guard exists because the first pass at it only did the second
    one. Somebody who reads the notice at one box and not the other has
    been told half of what changed about their bill."""
    boxes = [m.start() for m in re.finditer(r'tr\("set\.key\.label"', SETTINGS)]
    assert len(boxes) >= 2, "this screen used to have two key boxes"
    for at in boxes:
        block = SETTINGS[at:]
        block = block[:block.index("</div>")]
        assert KEY in block, (
            "a key box takes somebody's own key without saying what that "
            "changes about who is billed")


def test_it_says_the_charges_move():
    """A sentence that only says "you may enter a key" is the notice not
    being given."""
    row = L10N[L10N.index(f'"{KEY}"'):]
    row = row[:row.index("},")]
    english = re.search(r'en: "([^"]+)"', row)
    assert english, "no English copy for the notice"
    said = english.group(1).lower()
    assert "beta" in said
    assert "paying" in said or "pays" in said
    assert "yours" in said or "your own" in said


def test_every_language_carries_it():
    """A notice about money that only exists in English is not a notice
    for the nine other languages this console ships."""
    row = L10N[L10N.index(f'"{KEY}"'):]
    row = row[:row.index("},")]
    for lang in ("en", "es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar"):
        assert re.search(rf'\b{lang}: "', row), f"{KEY} has no {lang}"


def test_the_notice_is_not_a_secret_shaped_thing():
    """The one thing this paragraph must never do is quote a key. It talks
    about whose key is in use, never about which key it is."""
    row = L10N[L10N.index(f'"{KEY}"'):]
    row = row[:row.index("},")]
    assert "sk-" not in row
    assert not re.search(r"[A-Za-z0-9_-]{24,}", json.dumps(row))
