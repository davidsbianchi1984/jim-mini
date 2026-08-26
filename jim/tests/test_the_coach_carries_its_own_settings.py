"""The four boxes beside the coach conversation.

The estate's owner, having met the rail on QRME's talk face: "those four
extra boxes should be located in all the chats... including JIM-mini,
including coach — users should be able to modify all the settings."

QRME's rail opens panels in place because those settings had no screens
of their own. JIM's settings do — Aims, Journal, Bearing, and what JIM
may do — so JIM's telling of the same rail is four doors: each box opens
the screen the setting already lives on, from the one screen where you
are looking at the coach.
"""

from __future__ import annotations

from pathlib import Path

SRC = Path(__file__).resolve().parents[2] / "app" / "src"
COACH = (SRC / "screens" / "Coach.tsx").read_text(encoding="utf-8")
APP = (SRC / "App.tsx").read_text(encoding="utf-8")


def test_the_coach_screen_carries_the_rail():
    assert "coach-rail" in COACH, "the four boxes are gone from the coach"
    for tab in ('"aims"', '"journal"', '"bearing"', '"permits"'):
        assert tab in COACH, (
            f"the rail no longer reaches {tab} — a setting became "
            "unreachable from the conversation about it")


def test_the_rail_is_wired_not_decorative():
    assert "<Coach go={setTab} />" in APP, (
        "Coach renders without a navigator — four buttons that go nowhere")
