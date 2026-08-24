"""A microphone that has stopped must not still be drawn as listening.

A field report, with a photograph: tabs dropping into the background
mid-conversation. What happens underneath is not a crash. The browser
throttles a hidden page's timers, suspends its audio, and ends its speech
recogniser; a frozen tab stops running at all. None of that arrives as an
error, so the console keeps every light it had lit — the green orb, the
standing ear's pill, the line saying the room is hearing you — over a
microphone that stopped some minutes ago.

    asked     does the console stop listening when it is put away
    mattered  does it stop *saying* it is listening

The first half already happened, without being asked and without being
reported. The second is the defect, and it is the same shape as three
earlier ones this suite has caught: a failure that is both total and
unreported survives, and the unreported half is what lets it. Silence and
deafness look identical on screen and are opposite facts — one means
nobody spoke, the other means nobody could be heard.

The standing ear made it worse than merely quiet. Its restart-on-`onend`
contract stood a fresh recogniser every 400ms into a page that could not
run one, all night if the tab was left that way, with the pill reading
*listening for the words that call for help* throughout. An ear for
somebody who might be calling for help is the last place a lit light may
mean nothing.

These guards hold the rule at the two places it can be broken: a listen
that does not notice being put away, and a relight loop that restarts
without asking.

## The one exception, added later

Everything above is about the *recogniser*, which a hidden page really does
have ended under it. It is not true of `getUserMedia`: on a desktop and on
Android an open capture keeps recording while the window is minimised, and
the browser shows its own recording indicator throughout. The two ways this
console hears behave oppositely when the page goes away, and for a while they
were guarded as though they behaved the same.

The qualifier in that sentence was added after the fact. It read as a
universal for two releases, and iOS Safari is the platform it is false about:
it suspends the whole page, capture included, and reports nothing. A caller
carrying a conversation out there cannot be protected from that by anything in
this module, so it is expected to ask `live()` on the way back instead — see
`test_the_strip_finds_out_when_the_capture_did_not_survive` in the
walk-along suite.

    asked     does a hidden page stop hearing
    mattered  which of the two ways of hearing was it using

So a caller carrying a conversation out of the page — the walk-along strip,
and nothing else — asks for the recording path by name and is not guarded,
because guarding it would close a microphone the browser had not closed.
That is this defect's mirror image, not this defect. The device recogniser
is refused outright in that mode, so no unguarded path can hand back a
recogniser: the protection is intact and narrower, and the guards below say
where the line is.
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
SRC = REPO / "app" / "src"
AWAY = SRC / "away.ts"
SPEECH = SRC / "speech.ts"
EAR = SRC / "ear.ts"
LIGHTS = SRC / "GuardianLights.tsx"


def _stripped(path: Path) -> str:
    """Source with comments gone.

    Every file here documents the mistake in the words the fix uses, and a
    guard that counts a mention as a use invents a defect out of the
    documentation written to prevent it — this suite has already had one
    guard trip on its own docstring.
    """
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"^\s*//.*$", "", text, flags=re.M)


def test_the_console_has_somewhere_to_ask_whether_it_was_put_away() -> None:
    """One module answers it, so no screen has to remember the answer."""
    assert AWAY.exists(), "app/src/away.ts is where the suspension says its name"
    code = _stripped(AWAY)
    assert "export function putAway" in code, "nothing can ask *am I away now*"
    assert "export function whenPutAway" in code, (
        "nothing can be told when that changes")
    assert "visibilitychange" in code, (
        "a page that never listens for its own suspension cannot report it")
    # The subscription hands back its own release. An ear that cannot let go
    # is the headless loop the unmount teardowns were written to end, one
    # layer further down.
    assert "removeEventListener" in code, (
        "whenPutAway must hand back a release, or every listen leaks a watcher")


def test_no_path_out_of_listen_keeps_a_microphone_the_sleeping_tab_owns() -> None:
    """Six screens listen through this one function.

    They inherit the fix or they do not get it, and a seventh screen
    written next year inherits it without being told. That only holds if
    *every* way out of `listen` goes through the guard: the two device
    recognisers, the microphone that was refused, and the recording one. A
    path that forgot would be a microphone a sleeping tab keeps.
    """
    code = _stripped(SPEECH)
    body = code[code.index("export async function listen("):]
    end = body.index("\n}\n")
    body = body[:end]
    handed_back = re.findall(r"^\s*(?:if \(dev\) )?return (.+?);?$",
                             body, flags=re.M)
    # A stub that does nothing needs no guard, and it is recognised by what
    # its `stop` does rather than by how the object is spelled. The literal
    # `"{ stop: () => {} }"` used to stand here, and stopped matching the
    # day `Listener` grew a second member — the exemption widened to cover
    # every returned object, silently, because a substring that is absent
    # excludes nothing.
    #
    #     asked     is this the no-op stub, spelled the way I remember
    #     mattered  does this listener hold a microphone
    noop = re.compile(r"stop:\s*\(\)\s*=>\s*\{\s*\}")
    listeners = [r for r in handed_back if r not in ("", "null")
                 and not noop.search(r)]
    assert listeners, "listen hands back no Listener at all — read the shape again"
    for r in listeners:
        assert "hold(" in r, (
            f"`return {r}` leaves listen without the put-away guard — that "
            "microphone survives the tab going to sleep")
    # And `hold` is the guard, conditionally. The one exception is named
    # here rather than left to be discovered:
    #
    # `getUserMedia` is not ended by a hidden page on a desktop or on
    # Android. An open capture keeps recording while the window is minimised
    # and the browser shows its own recording indicator throughout, so a
    # caller carrying a conversation out of the page asks for the recording
    # path *by name* and is not guarded — guarding it would close a
    # microphone the browser had not closed, which is this defect's mirror
    # image rather than this defect.
    #
    #     asked     does a hidden page stop hearing
    #     mattered  which of the two ways of hearing was it using
    #
    # The device recogniser, which IS ended, is refused outright while
    # carrying. So no unguarded path can ever hand back a recogniser — the
    # protection this file was written for is intact, and narrower.
    #
    # iOS Safari is the third answer neither question anticipated: it
    # suspends the whole page, capture included, and tells nobody. Nothing
    # in `listen` can prevent that and this guard does not pretend to — the
    # caller is expected to ask `live()` on the way back, which is what
    # `test_the_strip_finds_out_when_the_capture_did_not_survive` checks.
    assert "const hold = (inner: Listener) => away ? away.hold(inner) : inner;" \
        in body, (
        "`hold` is not the conditional guard, so either every path is "
        "unguarded or the carried conversation is closed by a page change "
        "the browser did not act on")
    assert "const away = carry ? null : awayGuard(onError);" in body, (
        "the guard is skipped on something other than the explicit carry "
        "option — it may only be skipped for the path that survives")
    assert re.search(r"if \(!carry && \(preferDevice", body), (
        "the device recogniser is reachable while carrying, and that is the "
        "path a hidden page ends without a word")


def test_being_put_away_is_not_reported_as_quiet() -> None:
    """The distinction the whole fix rests on.

    A standing conversation treats `heardNothing` as a pause and opens the
    microphone again. Report the suspension that way and the console
    re-opens a microphone into a sleeping tab — over and over, hearing
    nothing, orb lit the entire time. That is the bug wearing the fix's
    clothes.
    """
    code = _stripped(SPEECH)
    assert "PUT_AWAY_MESSAGE" in code, "the suspension has no message of its own"
    said = re.search(r'export const PUT_AWAY_MESSAGE\s*=\s*(.+?);',
                     code, flags=re.S)
    assert said, "PUT_AWAY_MESSAGE is not a plain string constant any more"
    message = " ".join(re.findall(r'"([^"]*)"', said.group(1)))
    quiet = re.search(r"export function heardNothing.*?\n}", code, flags=re.S)
    assert quiet, "heardNothing moved — this guard reads it by name"
    for phrase in re.findall(r'"([^"]*)"', quiet.group(0)):
        assert phrase not in message, (
            f"the put-away message contains {phrase!r}, which heardNothing "
            "matches — a standing conversation would re-open the microphone "
            "into a sleeping tab and never stop")


def test_the_guard_silences_what_the_stopped_recogniser_says_next() -> None:
    """Stopping is itself an event that speaks.

    A MediaRecorder torn down mid-recording reports *nothing was recorded*,
    which is `heardNothing`, which is what a standing conversation re-opens
    on. One honest stop would become the very loop this fixes unless
    everything after it is dropped.
    """
    code = _stripped(SPEECH)
    guard = re.search(r"function awayGuard\(.*?\n}\n", code, flags=re.S)
    assert guard, "awayGuard is gone — listen has no way to drop late callbacks"
    assert "gone" in guard.group(0), (
        "the guard keeps no record of having fired, so late callbacks pass")
    body = code[code.index("export async function listen("):]
    body = body[:body.index("\n}\n")]
    # The two wrappers are the only place the caller's own callbacks may be
    # named, and each is gated on the guard not having fired. Read them out,
    # check the gate, and then nothing else in the body may name them.
    wrappers = re.findall(
        r"const (?:text|fail) = \([^)]*\) => \{([^}]*)\};", body)
    assert len(wrappers) == 2, (
        "listen no longer wraps onText and onError — the caller hears the "
        "stopped recogniser directly")
    for w in wrappers:
        # `away?.gone()`, optional. When a conversation is being carried out
        # of the page there is no guard to ask — see the note above — and
        # `undefined` there means *not put down*, which is the truth for the
        # recording path. For every other caller this is the same check it
        # has always been.
        assert "away?.gone()" in w or "away.gone()" in w, (
            f"the wrapper `{w.strip()}` passes callbacks through without "
            "asking whether the microphone was already put down")
    rest = re.sub(r"const (?:text|fail) = \([^)]*\) => \{[^}]*\};", "", body)
    assert "onText(" not in rest and "onError(" not in rest, (
        "listen still calls the caller's callbacks directly somewhere — those "
        "are the ones that speak after the microphone was put down")


def test_the_standing_ear_does_not_restart_into_a_sleeping_tab() -> None:
    """The 400ms restart loop, and the two ways into it.

    `onend` fires when the browser ends the recogniser, and a hidden page
    is one of the reasons it does. Restarting there without asking is the
    loop that ran all night. `start()` is the other door: a room re-entered
    on a page already in the background reaches it without passing `onend`
    at all.
    """
    code = _stripped(EAR)
    onend = re.search(r"r\.onend = \(\) => \{(.*?)\};", code, flags=re.S)
    assert onend, "the standing ear's onend moved — this guard reads it by name"
    assert "dozing" in onend.group(1), (
        "onend restarts the ear without asking whether the page is away — "
        "that is a fresh recogniser every 400ms into a tab that cannot run one")
    start = re.search(r"const start = \(\) => \{(.*?)\n    const r = new SR",
                      code, flags=re.S)
    assert start, "the standing ear's start() moved — this guard reads it by name"
    assert "putAway()" in start.group(1), (
        "start() stands an ear into a page that is already asleep")
    assert "whenPutAway" in code, "nothing tells the ear the page came back"
    assert "release()" in code, (
        "stop() does not release the visibility watch, so a switched-off ear "
        "keeps waking up")


def test_the_pill_says_asleep_rather_than_saying_nothing_is_wrong() -> None:
    """An unhandled state falls through to the wrong sentence.

    The pill read three states and let everything else land on *this browser
    has no recogniser to listen with*. A new state added without its own
    branch would tell somebody their browser cannot listen — permanent,
    unfixable, and false — when the truth is that they switched tabs.
    """
    assert '"asleep"' in _stripped(EAR), "EarState has no word for being put away"
    lights = _stripped(LIGHTS)
    assert 'ear === "asleep"' in lights, (
        "the pill has no branch for the asleep ear, so it falls through to "
        "the no-recogniser sentence and blames the browser")
    assert "lights.ear.asleep" in lights, "the asleep branch shows no sentence"
