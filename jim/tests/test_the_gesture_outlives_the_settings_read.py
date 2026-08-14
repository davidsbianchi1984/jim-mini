"""The device recogniser has to start inside the tap that asked for it.

Safari permits `SpeechRecognition.start()` only while the user gesture that
triggered it is still live, and an `async` function holds that gesture
exactly until its first suspension point. So an `await` placed before the
recogniser starts does not merely slow the fallback down — it removes it,
on the platform most people are holding, with `service-not-allowed` and no
prompt to accept.

    asked     is there a device recogniser to fall back to
    mattered  is it started while the browser still permits it

This is a structural guard rather than a behavioural one because the defect
is invisible to any test that can run here: node has no `SpeechRecognition`,
jsdom has no user gesture, and the code is correct on every engine that does
not enforce the rule. What can be checked is the ordering the rule demands,
and ordering is exactly what regressed — the original wrote the settings
read first because reading before deciding is the obvious shape.
"""
from __future__ import annotations

import re
from pathlib import Path

_APP = Path(__file__).resolve().parents[2] / "app" / "src"
_SPEECH = _APP / "speech.ts"


def _listen_body() -> str:
    """The text of `export async function listen(...)`, brace-matched.

    A regex for the whole function would stop at the first `}` inside it.
    """
    text = _SPEECH.read_text(encoding="utf-8")
    start = text.index("export async function listen(")
    open_brace = text.index("{", text.index(")", start))
    depth = 0
    for i in range(open_brace, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[open_brace:i + 1]
    raise AssertionError("listen() has no closing brace")


def test_the_recogniser_starts_before_listen_awaits_anything() -> None:
    body = _listen_body()
    first_device = body.find("deviceListener(")
    first_await = body.find("await ")

    assert first_device != -1, "listen() no longer reaches the device recogniser"
    assert first_await != -1, "listen() no longer awaits — this guard is stale"
    assert first_device < first_await, (
        "listen() awaits before starting the device recogniser. Safari ends "
        "the user gesture at the first suspension point, so the recogniser "
        "is refused with `service-not-allowed` and the fallback this module "
        "promises does not exist on iPhone or iPad. Decide everything "
        "decidable without the network first."
    )


def test_the_flag_that_avoids_the_last_failure_is_read_before_the_await() -> None:
    """`preferDevice` exists so the second tap does not repeat the first.

    It was consulted after the settings read, which meant the retry path —
    the one the error message explicitly invites — spent the gesture in the
    same place and failed identically. A flag whose whole purpose is to
    shorten a path must be read before the path gets long.
    """
    body = _listen_body()
    first_prefer = body.find("preferDevice")
    first_await = body.find("await ")

    assert first_prefer != -1, "listen() no longer consults preferDevice"
    assert first_prefer < first_await, (
        "preferDevice is read after listen() awaits. The tap that follows a "
        "service refusal is exactly the tap that must not await."
    )


def test_every_screen_with_a_microphone_primes_the_voice_settings() -> None:
    """Ordering inside `listen` is only free if the answer is already known.

    `listen` may await when it has never read the settings; the screens
    remove that case by reading on mount. A new microphone screen that
    forgets to prime gets the slow path back on its first tap, silently.
    """
    missing = []
    for screen in sorted((_APP / "screens").glob("*.tsx")):
        text = screen.read_text(encoding="utf-8")
        if "listen(" in text and "primeVoice()" not in text:
            missing.append(screen.name)

    assert not missing, (
        "these screens call listen() without priming the voice settings on "
        f"mount, so their first tap awaits inside the gesture: {missing}"
    )


def test_the_platform_refusal_names_what_to_do_about_it() -> None:
    """`service-not-allowed` is not a code to print at somebody.

    `not-allowed` means a prompt was shown and declined, which the person
    can retry. `service-not-allowed` means no prompt will ever appear —
    tapping again cannot help, and the raw code says nothing about the
    setting that would. Naming the failure without naming the remedy is the
    same defect as a verdict reading "bad key" for an unpaid invoice.
    """
    text = _SPEECH.read_text(encoding="utf-8")
    assert '"service-not-allowed"' in text, (
        "the platform refusal is no longer distinguished from a declined "
        "microphone prompt"
    )
    assert "Dictation" in text, (
        "the `service-not-allowed` branch does not name Dictation, which is "
        "what the person has to switch on"
    )
