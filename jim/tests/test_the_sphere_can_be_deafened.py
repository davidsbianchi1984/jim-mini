"""The sphere can be deafened without being hung up on.

Field report, mid-conversation with the coach sphere:

    "Everything is working flawless except for when I wanna talk to you
     off the side while this is running — I can press the microphone and
     not have to be worried about it picking up my voice."

    asked     can you stop the sphere hearing you
    mattered  without ending the conversation

The only control on that veil was the veil itself, and tapping it calls
`exitTalk` — the conversation ends, the standing turn is gone, and coming
back means starting over. That is the right control for "we're done" and
the wrong one for "hold on."

## Why muted stops the recorder rather than dropping what it hears

An ear that is still running and discarding is a microphone that is still
open. The whole content of the press is that it is not: `flipMuted` stops
the recorder, drops the reference, and bumps `round` so an in-flight
recogniser callback lands orphaned instead of arriving after the mute.

## What muting does NOT do

It does not end the conversation — `talking.current` is untouched, so
unmuting re-opens the ear on the same standing turn. It does not stop the
sphere speaking: being unable to interrupt is a different complaint from
being overheard, and a person who mutes to talk to somebody else may well
still want to hear the answer.

## The gate is a gate

`hear()` returns early while muted. Without that, the silent-stretch
re-open — the loop that keeps a standing conversation standing — would
re-open the microphone a second after the press.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
COACH = (ROOT / "app/src/screens/Coach.tsx").read_text(encoding="utf-8")
CHECKIN = (ROOT / "app/src/screens/Checkin.tsx").read_text(encoding="utf-8")
CSS = (ROOT / "app/src/styles.css").read_text(encoding="utf-8")
L10N = (ROOT / "app/src/l10n.ts").read_text(encoding="utf-8")

SPHERES = {"Coach": COACH, "Checkin": CHECKIN}


def test_both_spheres_carry_the_mute():
    """One surface wearing two names. A control on one and not the other
    is the split this estate keeps finding."""
    for name, src in SPHERES.items():
        assert "voice-orb-mute" in src, f"{name} has no mute"
        assert "function flipMuted()" in src, f"{name} cannot mute"


def test_muting_stops_the_recorder():
    """An ear still running and discarding is a microphone still open."""
    for name, src in SPHERES.items():
        fn = src[src.index("function flipMuted()"):]
        fn = fn[:fn.index("\n  }")]
        assert "recorder.current?.stop()" in fn, (
            f"{name} mutes without stopping the recorder")
        assert "recorder.current = null" in fn
        assert "round.current++" in fn, (
            f"{name} leaves an in-flight recogniser callback able to land "
            "after the mute")


def test_muting_does_not_end_the_conversation():
    """The whole distinction from the veil tap underneath it."""
    for name, src in SPHERES.items():
        fn = src[src.index("function flipMuted()"):]
        fn = fn[:fn.index("\n  }")]
        assert "talking.current = false" not in fn, (
            f"{name}'s mute hangs up, which is what the veil already does")
        assert "exitTalk()" not in fn


def test_the_press_does_not_reach_the_veil():
    """The veil under the button ends the conversation. Without
    `stopPropagation` the press that mutes also hangs up — one gesture,
    two outcomes, and the destructive one wins."""
    for name, src in SPHERES.items():
        block = src[src.index('className={"voice-orb-mute"'):]
        block = block[:block.index("</button>")]
        assert "e.stopPropagation()" in block, f"{name}'s mute also exits"


def test_nothing_reopens_the_ear_while_muted():
    """The silent-stretch re-open is what keeps a standing conversation
    standing; unguarded, it re-opens the microphone a second after the
    press."""
    for name, src in SPHERES.items():
        fn = src[src.index("async function hear()"):]
        fn = fn[:fn.index("const g = ++round.current;")]
        assert "if (muted)" in fn, (
            f"{name} re-opens the microphone while muted")


def test_leaving_clears_the_mute():
    """A muted flag outliving the conversation is a sphere that comes back
    deaf and does not say why."""
    for name, src in SPHERES.items():
        fn = src[src.index("function exitTalk()"):]
        fn = fn[:fn.index("\n  }")]
        assert "setMuted(false)" in fn, f"{name} stays muted after leaving"


def test_the_label_says_it_is_muted_and_still_open():
    """Both halves. A person who muted needs to know the microphone is off
    AND that they have not hung up."""
    row = L10N[L10N.index('"cch.muted"'):]
    row = row[:row.index("},")]
    said = row.lower()
    assert "cannot hear you" in said
    assert "still open" in said


def test_a_muted_microphone_is_unmistakable():
    """The one state worth being loud about is the one somebody is
    trusting — the same argument the room's mute mark makes."""
    block = CSS[CSS.index(".voice-orb-mute.muted"):]
    block = block[:block.index("}")]
    assert "224, 104, 122" in block, "muted does not read as muted"
