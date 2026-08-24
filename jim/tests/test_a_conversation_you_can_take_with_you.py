"""The conversation you took with you, and what it owes you for coming.

`{tab === "coach" && <Coach/>}` — the screen unmounts on every tab change and
the voice goes with it. There is an unmount teardown on all five voice
screens for exactly that reason: navigating away mid-reply used to leave a
headless loop, the guardian talking on under a screen that no longer exists.

That teardown is right for navigating away and wrong for walking away on
purpose: the same event to React, opposite events to the person. One means
they left the conversation, the other means they took it.

    asked     did the screen unmount
    mattered  did the person mean to end the conversation

So one ear in this console outlives its screen, and this file holds the
exception to exactly the terms that make it one:

  * nothing starts it but a press;
  * the strip says which of listening, answering and stopped it is;
  * ending it is the first control on the strip;
  * a real failure reads as one rather than as quiet;
  * and when the browser puts the page away and ends the recogniser, the
    strip says *that* rather than going on claiming to listen.

The last one is not decoration. `away.ts` was written because a backgrounded
page stops hearing without saying so, and silence and deafness look identical
on screen while being opposite facts. An ear that survives a screen change
would be the easiest place in the console to reintroduce that.

And one term that is this console's rather than the estate's: the turn is
`speech.ts`'s. That module decides between the service and the device
recogniser, asks the connected earbud for its microphone by name, ends a turn
on two and a half seconds of quiet, refuses to transcribe a recording the
analyser never heard a voice in, and reports being put away as its own
failure. A strip with a recogniser of its own would have none of that and
would drift from the two screens it is carrying.
"""

import re
from pathlib import Path


def _repo() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


APP = _repo() / "app" / "src"
STRIP = (APP / "WalkAlong.tsx").read_text(encoding="utf-8")
SHELL = (APP / "App.tsx").read_text(encoding="utf-8")
STORE = (APP / "walk.ts").read_text(encoding="utf-8")

#: The conversations this console can hand over. Both of them: the front
#: door asks the coach with `area: "general"`, the coach screen asks it with
#: whichever area the person picked, and a walk started from either has to
#: keep asking the way its screen was asking.
SURFACES = ("Talk.tsx", "Coach.tsx")


def _surfaces() -> dict[str, str]:
    return {n: (APP / "screens" / n).read_text(encoding="utf-8")
            for n in SURFACES}


def _braced(src: str, at: int) -> str:
    """The whole `{...}` starting at `at`, brace-matched.

    A regex stopping at the first `}` reads a nested object as the end of
    the call, which in a file like this is most of them.
    """
    depth, j = 0, at
    while j < len(src):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                return src[at:j + 1]
        j += 1
    raise AssertionError("unbalanced braces from the call site")


def test_it_is_mounted_above_the_thing_it_has_to_outlive():
    """Inside the tab switch it would unmount with every other screen, which
    is the whole defect it exists to answer."""
    assert "<WalkAlong />" in SHELL, "the strip is not mounted"
    # Against `<main>` itself, not merely against the first `tab ===` line:
    # the strip moved one line inside the content element would still be
    # before every screen and would still unmount with all of them.
    assert SHELL.index("<WalkAlong />") > SHELL.index("</main>"), (
        "the strip renders inside the content element that holds the tab "
        "switch; it has to be outside it, or it unmounts with the screen it "
        "was meant to survive")


def test_nothing_opens_it_without_a_press():
    """The exception is earned by being asked for. The five unmount
    teardowns exist to prevent a microphone nobody is looking at; a strip
    that started itself would be one of those with a longer life."""
    assert "startWalking" in STORE and "addEventListener" not in STORE, (
        "the walking store subscribes to something; it is meant to be moved "
        "only by a caller")
    assert "startWalking(" not in STRIP, (
        "the strip starts a walk itself — only a screen's button may")
    for name, src in _surfaces().items():
        i = src.index("startWalking({")
        # The press, not an effect: the nearest `onClick` before the call
        # and no `useEffect` between them.
        before = src[:i]
        assert "onClick=" in before, f"{name} starts a walk with no press"
        assert "useEffect" not in before[before.rindex("onClick="):], (
            f"{name} starts a walk from an effect rather than a press")


def test_the_strip_says_which_of_the_four_states_it_is_in():
    for owed in ("walk.listening", "walk.speaking", "walk.quiet",
                 "walk.asleep"):
        assert f'tr("{owed}"' in STRIP, f"the strip never renders {owed}"
    assert STRIP.index('tr("walk.end"') < STRIP.index("walk-who"), (
        "ending the conversation is not the first control on the strip")


def test_a_real_failure_reads_as_one():
    """`speech.ts` writes a sentence saying which of a refused microphone, an
    unreachable service and a fault this was. A strip that dropped it would
    be back to the one-way-of-failing this console has been caught by."""
    m = re.search(r"\(msg\) => \{", STRIP)
    assert m, "the strip passes no error handler to listen"
    body = _braced(STRIP, m.end() - 1)
    assert "heardNothing(msg)" in body, (
        "the strip does not separate quiet from failure — a standing "
        "conversation treats quiet as a pause, and treating a refused "
        "microphone the same way reopens it forever")
    assert "setTrouble(msg)" in body, (
        "the failure message `speech.ts` wrote is never shown, so every way "
        "of failing reads as `not listening`")
    assert "walk-trouble" in STRIP, "nothing renders the failure"


def test_being_put_away_stops_it_and_says_so():
    """The failure `away.ts` was written about, in the one place best placed
    to bring it back."""
    assert "whenPutAway(" in STRIP, "the strip never asks whether it is away"
    # The whole call, paren-matched, rather than a regex that stops at the
    # first `)` — a `listen(who)` inside a braced handler would sail past
    # that, which is the shape this test exists to catch.
    i = STRIP.index("whenPutAway(")
    depth, j = 0, i
    while j < len(STRIP):
        if STRIP[j] == "(":
            depth += 1
        elif STRIP[j] == ")":
            depth -= 1
            if depth == 0:
                break
        j += 1
    call = STRIP[i:j + 1]
    assert "close()" in call, "being put away does not close the ear"
    assert "hear(" not in call, (
        "the put-away handling restarts the ear itself — a microphone that "
        "reopens because a tab regained focus is one nobody pressed for")
    assert 'tr("walk.asleep"' in STRIP, (
        "the strip has no way to say it stopped because the page was put "
        "away — which leaves silence and deafness looking identical again")


def test_the_turn_is_the_consoles_own_and_not_a_second_copy_of_one():
    """A recogniser here would miss the earbud, the silence stop, the voiced
    check and the away report, and would drift from the screens it carries."""
    assert 'from "./speech"' in STRIP and "listen(" in STRIP, (
        "the strip does not listen through `speech.ts`")
    for own in ("webkitSpeechRecognition", "SpeechRecognition",
                "MediaRecorder", "getUserMedia", "SpeechSynthesisUtterance"):
        assert own not in STRIP, (
            f"the strip builds its own `{own}` instead of using the voice "
            "layer the two screens it carries already share")
    # In the comparison, not merely in the import line. The first draft
    # asserted the name appeared anywhere in the file, and a sabotage that
    # replaced the comparison with a bare `120000` — leaving the now-unused
    # import above it — passed happily. A name that is imported and not used
    # is exactly the drift this is about.
    m = re.search(r"\(msg\) => \{", STRIP)
    assert m, "the strip passes no error handler to listen"
    body = _braced(STRIP, m.end() - 1)
    idle = re.search(r"lastHeard\.current\s*>=\s*(\w+)", body)
    assert idle, "the strip has no idle window at all"
    assert idle.group(1) == "CONVERSATION_IDLE_MS", (
        "the strip bows out on a number of its own; the console has already "
        f"answered how long a conversation nobody is in stays open, and "
        f"`{idle.group(1)}` here is a second answer waiting to drift from it")


def test_every_surface_that_offers_the_walk_hands_over_its_own_turn():
    """A caller that starts a walk without a `take` hands the strip a
    conversation it cannot continue — and the strip finds out at the first
    thing the person says, which is the worst moment to find out."""
    for name, src in _surfaces().items():
        for m in re.finditer(r"startWalking\(\{", src):
            call = _braced(src, m.end() - 1)
            assert "take:" in call, (
                f"{name} starts a walk without handing over how to take a "
                "turn")
            assert "shownName:" in call, (
                f"{name} starts a walk without saying who the person is "
                "walking with")


def test_the_screen_stops_its_own_ear_before_handing_over():
    """Two ears on one microphone is the defect turn numbers already fixed
    once inside a single screen. Handing the walk a still-listening screen
    would rebuild it across two components, where no turn number reaches."""
    for name, src in _surfaces().items():
        i = src.index("startWalking({")
        press = src[src.rindex("onClick=", 0, i):i]
        assert "exitTalk()" in press, (
            f"{name} hands the conversation over without ending its own "
            "listening first")


def test_the_coach_walk_carries_the_area_it_was_asked_in():
    """The coach screen is the one that offers the picker. A walk started
    from *mental health* that quietly reverted to the front door's `general`
    would be a different conversation wearing the same name."""
    src = _surfaces()["Coach.tsx"]
    call = _braced(src, src.index("startWalking({") + len("startWalking(") )
    assert '"general"' not in call, (
        "the coach's walk hardcodes the front door's area, discarding the "
        "one the person picked")
    assert re.search(r"area:\s*a\b", call), (
        "the coach's walk does not close over the area it was asked in — a "
        "later change of the picker would silently change what the walk is "
        "about")


def test_both_of_the_consoles_conversations_offer_it():
    for name, src in _surfaces().items():
        assert "startWalking({" in src, (
            f"{name} is a conversation this console can hold and offers no "
            "way to take it along")
        assert 'tr("walk.take"' in src, (
            f"{name}'s walk control is unlabelled or labelled in one "
            "language")
