"""The conversation that survives leaving the app, and what it owes for that.

The console's walk-along strip carries a conversation across a screen change
and stops dead when the browser puts the page away. That is not a shortcoming
of the strip — a backgrounded web page has its recogniser ended by the
browser — and the strip says so on screen rather than pretending otherwise.

    asked     can the conversation survive a screen change
    mattered  can it survive leaving the application

On a phone the answer can be yes, and the price is a foreground service
holding a microphone while the person is somewhere else entirely. That
notification is not a platform tax to be minimised. It is the whole
difference between *the conversation you took with you* and *an app recording
you after you left it*, and the two are the same code with different honesty.

So this file holds the declarations, which is what an environment with no
Android toolchain can actually check — and which is also, conveniently, the
half whose absence is a microphone with no indicator:

  * the permissions are asked for, including the one for the notification;
  * the service is declared, not exported, and typed as a microphone service;
  * the foreground start is made with that type;
  * the notification is ongoing and its first action ends the conversation;
  * nothing restarts the service by itself.

## What this cannot check

Whether it works. There is no compiler here, so the loop — the recogniser,
the turn, the voice — has been reasoned about and not run. The guard says
what it is checking so nobody reads a green suite as a working feature; the
CHANGELOG says the same thing in the reader's direction.
"""

from __future__ import annotations

import re
from pathlib import Path


def _repo() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo()
MANIFEST = REPO / "native/android/app/src/main/AndroidManifest.xml"
SERVICE = REPO / ("native/android/app/src/main/java/app/jim/guardian/"
                  "Walk.kt")


def test_the_service_exists_at_all():
    assert SERVICE.exists(), "the walking service is gone"


def test_the_permissions_the_platform_will_ask_for_are_declared():
    """A foreground microphone service refused at start is a button that
    does nothing, and from Android 14 the typed permission is what the
    system checks the start against."""
    xml = MANIFEST.read_text(encoding="utf-8")
    for perm in ("android.permission.RECORD_AUDIO",
                 "android.permission.FOREGROUND_SERVICE",
                 "android.permission.FOREGROUND_SERVICE_MICROPHONE",
                 # The indicator is itself a permission from Android 13. A
                 # service whose notification can be silently withheld is
                 # exactly the thing this file is careful about.
                 "android.permission.POST_NOTIFICATIONS"):
        assert perm in xml, f"the manifest does not ask for {perm}"


def test_the_service_is_declared_typed_and_not_exported():
    xml = MANIFEST.read_text(encoding="utf-8")
    m = re.search(r"<service\b(.*?)/>", xml, re.S)
    assert m, "no service is declared in the manifest"
    block = m.group(1)
    assert 'android:name=".WalkService"' in block
    assert 'android:foregroundServiceType="microphone"' in block, (
        "the service is not typed as a microphone service; from Android 14 "
        "the start is refused, and before that the person is not told what "
        "kind of service is running")
    assert 'android:exported="false"' in block, (
        "the service is exported — anything on the phone could start this "
        "app's microphone")


def test_the_foreground_start_carries_the_microphone_type():
    src = SERVICE.read_text(encoding="utf-8")
    assert "startForeground(" in src, (
        "the service never goes to the foreground, so the system kills it "
        "and the notification the person is owed never appears")
    assert "FOREGROUND_SERVICE_TYPE_MICROPHONE" in src, (
        "the foreground start does not declare the microphone type")


def test_the_notification_says_it_and_can_end_it():
    """The whole justification for the feature is on this notification."""
    src = SERVICE.read_text(encoding="utf-8")
    assert "setOngoing(true)" in src, (
        "the notification can be swiped away, leaving a microphone open "
        "with nothing on screen saying so")
    assert "addAction(" in src, "the notification offers no way to stop it"
    # The action is the stop, not something else that happens to be an
    # action: it carries `walk.end` and it fires ACTION_STOP.
    m = re.search(r"addAction\((.{0,300}?)\.build\(\)\)", src, re.S)
    assert m and 'L10n.t("walk.end"' in m.group(1), (
        "the notification's action is not the one that ends the "
        "conversation")
    assert 'setAction(ACTION_STOP)' in src, (
        "nothing builds the intent that stops the service")
    assert 'walk.note.body' in src, (
        "the notification never says the microphone is open")


def test_nothing_restarts_it_by_itself():
    """A service the system brings back after killing it is a microphone
    that reopens with nobody pressing anything — the one thing this must
    never be, and a one-word difference in the code."""
    src = SERVICE.read_text(encoding="utf-8")
    assert "START_NOT_STICKY" in src
    assert "START_STICKY" not in src, (
        "the service asks the system to restart it; nothing may reopen this "
        "microphone but a press")
    assert "START_REDELIVER_INTENT" not in src, (
        "the service asks the system to restart it with its arguments, "
        "which is the sticky problem carrying a token with it")


def test_a_superseded_turn_cannot_close_the_one_that_replaced_it():
    """The console's own defect, which cost a release: one shared flag meant
    a late callback from a stale recogniser closed the ear that had replaced
    it, and the microphone died a fifth of a second after it opened."""
    src = SERVICE.read_text(encoding="utf-8")
    assert re.search(r"val mine\s*=\s*\+\+turn", src), (
        "the listener takes no turn number, so a late callback from a "
        "superseded recogniser will act on the one that replaced it")
    assert re.search(r"fun live\(\)\s*=\s*mine == turn", src)
    for handler in ("onResults", "onError"):
        m = re.search(handler + r"\([^)]*\)\s*\{(.{0,120})", src, re.S)
        assert m and "live()" in m.group(1), (
            f"`{handler}` does not check that its session is still the live "
            "one")


def test_quiet_reopens_and_a_refusal_does_not():
    """A standing conversation treats quiet as a pause. Treating a refused
    microphone the same way is a loop that reopens forever with nothing to
    hear, and says nothing about why."""
    src = SERVICE.read_text(encoding="utf-8")
    m = re.search(r"override fun onError\(code: Int\)\s*\{(.*?)\n            \}",
                  src, re.S)
    assert m, "the service has no error handler"
    body = m.group(1)
    assert "ERROR_NO_MATCH" in body and "ERROR_SPEECH_TIMEOUT" in body, (
        "quiet is not separated from failure")
    assert "ERROR_INSUFFICIENT_PERMISSIONS" in body, (
        "a refused microphone is not distinguished, so it reads as quiet "
        "and the loop reopens into nothing")
    assert body.count("close(reason =") >= 3, (
        "the service has one way of failing; the console has already been "
        "caught by exactly that, where a refusal, an unreachable service "
        "and a defect all read the same")


def test_the_button_starts_it_and_the_same_button_ends_it():
    """A control that only starts something sends a person hunting through
    a notification shade for the way back out."""
    ui = (REPO / "native/android/app/src/main/java/app/jim/guardian/ui/"
          "Screens.kt").read_text(encoding="utf-8")
    assert "Walking.start(" in ui, "nothing on any screen starts a walk"
    assert "Walking.stop(" in ui, "the screen offers no way to end one"
    assert 'L10n.t("walk.take"' in ui and 'L10n.t("walk.end"' in ui, (
        "the control is unlabelled or labelled in one language")


def test_the_screen_says_why_it_stopped():
    """The same rule as the console's strip: silence and deafness look
    identical and are opposite facts."""
    ui = (REPO / "native/android/app/src/main/java/app/jim/guardian/ui/"
          "Screens.kt").read_text(encoding="utf-8")
    # The condition AND the render. The first draft asserted the name
    # `Walking.trouble` appeared anywhere in the file, and a sabotage that
    # replaced the condition with `if (false)` — leaving the now-unreachable
    # Text below it — passed happily. A branch that can never be taken is
    # exactly the shape of "shipped and never shown".
    assert re.search(
        r"if \(Walking\.trouble\.isNotEmpty\(\)\)\s*\{\s*\n?\s*"
        r"Text\(Walking\.trouble", ui), (
        "the screen never shows why the conversation stopped, so a refused "
        "microphone and a person pressing End look the same afterwards")
