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
  * and when the page is put away it says so — but it does not stop, which
    reverses what this file first asserted and is explained below.

## The reversal

The first draft held that being put away must close the ear, because
`away.ts` says a backgrounded page has its recogniser ended by the browser.
That is true of the *recogniser* and false of `getUserMedia`: an open capture
keeps the tab alive, keeps recording while the window is minimised, and makes
the browser show its own recording indicator throughout. This console has two
ways of hearing and they behave oppositely when the page goes away; the first
draft guarded them as though they behaved the same, and so shipped a strip
that closed a microphone the browser had not closed.

    asked     does a hidden page stop hearing
    mattered  which of the two ways of hearing was it using

So the strip asks `speech.ts` for the recording path by name, and a
deployment with no transcription service is refused outright rather than
handed a recogniser that will die out there in silence. What survives from
the original terms is the honesty: silence and deafness still must not look
identical, which is now served by saying *still listening while you are
away* rather than by stopping.

And one term that is this console's rather than the estate's: the turn is
`speech.ts`'s. That module decides between the service and the device
recogniser, asks the connected earbud for its microphone by name, ends a turn
on two and a half seconds of quiet, and refuses to transcribe a recording the
analyser never heard a voice in. A strip with a recogniser of its own would
have none of that and would drift from the two screens it is carrying.
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
                 # Not `walk.asleep`: being away no longer stops it, so the
                 # fourth state is *still listening while you are away*.
                 # See the reversal in this file's own docstring.
                 "walk.aloft"):
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


def test_being_put_away_is_noted_and_not_acted_on():
    """The reversal, held in place.

    The strip must still *know* it is away — somebody who minimised the
    window deserves to be told the microphone is open. It must not close
    anything, because the path it runs on did not close; a component that
    invented that failure would be the mirror image of the one this file was
    originally written about.
    """
    assert "whenPutAway(" in STRIP, "the strip never asks whether it is away"
    # The whole call, paren-matched, rather than a regex that stops at the
    # first `)` — a `close()` inside a braced handler would sail past that.
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
    assert "close()" not in call, (
        "being put away closes the ear — the recording path survives it, so "
        "this is the component inventing a failure the browser did not have")
    assert "hear(" not in call, (
        "the put-away handling opens the ear itself — nothing may start a "
        "microphone but a press")
    assert 'tr("walk.aloft"' in STRIP, (
        "the strip has no way to say it is still listening while the page is "
        "away, which leaves somebody who minimised the window with no idea "
        "the microphone is open")


def test_it_asks_for_the_path_that_survives_by_name():
    """Not by hope. The device recogniser dies on a hidden page and does not
    say so, so asking for it there would be choosing the one failure this is
    about."""
    assert "carryWhenAway: true" in STRIP, (
        "the strip takes whichever path `listen` happens to pick, and one of "
        "them stops hearing the moment the window is minimised")
    speech = (APP / "speech.ts").read_text(encoding="utf-8")
    assert "carryWhenAway" in speech, "`listen` does not offer the option"
    # And the refusal. With no transcription service nothing here survives
    # being put away, and a listen that opened a doomed microphone anyway
    # would be the silent failure wearing a different coat.
    # The call, not the name. A sabotage that renamed the export to
    # `NO_EARS_MESSAGE_UNUSED` and deleted the refusal passed a substring
    # check — the name was still there, doing nothing, which is exactly the
    # shape of "declared and never reached".
    assert "fail(NO_EARS_MESSAGE);" in speech, (
        "a deployment with no transcription service is not refused, so the "
        "strip opens a microphone that hears nothing once the page is put "
        "away and never says why")
    assert "export const NO_EARS_MESSAGE" in speech, (
        "the sentence that refusal shows is gone")
    # The device recogniser must be skipped, not merely deprioritised.
    assert re.search(r"if \(!carry && \(preferDevice", speech), (
        "the device recogniser is still reachable while carrying, which is "
        "the path that dies on a hidden page without saying so")


def test_pressing_walk_lands_on_the_front_page():
    """The point of taking a conversation with you is going somewhere, and
    the screen you were on is the one place you have finished with."""
    assert 'setTab("home")' in SHELL, (
        "pressing walk leaves the person on the screen they were trying to "
        "leave, with the strip lit and the first thing to do being finding "
        "their way out of it")
    i = SHELL.index("onWalk((w)")
    assert "if (w)" in SHELL[i:i + 140], (
        "the shell navigates home when a walk *ends* as well as when it "
        "begins, which yanks somebody off whatever screen they walked to")


def test_the_turn_is_the_consoles_own_and_not_a_second_copy_of_one():
    """A recogniser here would miss the earbud, the silence stop, the voiced
    check and the away report, and would drift from the screens it carries."""
    assert 'from "./speech"' in STRIP and "listen(" in STRIP, (
        "the strip does not listen through `speech.ts`")
    # Against the code, with comments stripped. The first draft searched the
    # whole file, and the comment explaining *why* the strip does not build
    # its own `getUserMedia` failed the check that it does not build one — a
    # guard that forbids naming the thing it forbids.
    code = re.sub(r"/\*.*?\*/", "", STRIP, flags=re.S)
    code = re.sub(r"//.*", "", code)
    for own in ("webkitSpeechRecognition", "SpeechRecognition",
                "MediaRecorder", "getUserMedia", "SpeechSynthesisUtterance"):
        assert own not in code, (
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


# ---------------------------------------------------------------------------
# Who answered, when the deployment has no model.
#
# A coach turn already falls back: with no model key, `jim/pipeline.py` answers
# from the curated pack and every deposit a paid turn left. That has been true
# for releases, and nothing on the walking strip ever said so — text written by
# the offline stack read exactly like text written by the model somebody chose.
#
#     asked     did the turn come back
#     mattered  who wrote it
#
# `generated_by` is who *actually* answered rather than who was picked, and
# that distinction is the reason the field exists at all: a silent degrade to
# the stub under a screen naming a real model is how canned text gets demoed as
# conversation. On the walk it matters more than anywhere, because the person
# is on another screen — or another application — and has nothing else to
# notice it with.


def test_the_turn_carries_who_answered_it():
    """`take` returns a shape rather than a string, so the answer can say
    where it came from."""
    store = (APP / "walk.ts").read_text(encoding="utf-8")
    assert "export type Said" in store, (
        "a turn is still a bare string, so nothing can say who wrote it")
    assert "offline?: boolean" in store


def test_the_strip_says_when_the_store_answered():
    assert 'tr("walk.offline"' in STRIP, (
        "the strip never says an answer came from stored knowledge, so a "
        "fallback reads as the model somebody picked")
    assert "setOffline(" in STRIP, "nothing on the strip reads the flag"
    # From the answer, not invented. A strip that decided this itself would
    # be guessing about somebody else's endpoint.
    assert re.search(r"setOffline\(Boolean\(\s*answer\.offline\s*\)\)", STRIP), (
        "the strip sets the flag from something other than what the screen "
        "handed it")


def test_the_rule_is_written_once():
    """Two copies of *who answered* is how the two screens drift, and the
    walk is exactly where a person is least able to notice a drift."""
    store = (APP / "walk.ts").read_text(encoding="utf-8")
    assert "export function answeredOffline" in store, (
        "the offline test is not shared, so each caller has its own")
    for name, src in _surfaces().items():
        # Scoped to the walk's own turn, not the whole screen. Coach.tsx
        # renders provenance on its reply card and reads `generated_by`
        # there legitimately — a guard that banned the string outright
        # would be forbidding the screen from showing what it already
        # shows, which is how a guard gets loosened instead of corrected.
        call = _braced(src, src.index("startWalking({") + len("startWalking("))
        assert "answeredOffline(" in call, (
            f"{name}'s walk works out for itself whether the store "
            "answered, instead of asking the one function that knows")
        assert '"stub"' not in call, (
            f"{name}'s walk carries its own copy of the rule")
