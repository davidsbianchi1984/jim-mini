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


# ---------------------------------------------------------------------------
# Who answered, out where there is no screen.
#
# A deployment with no model key still answers — the offline stack does, from
# stored knowledge — and that has been true for releases. On the phone the
# person is in another application entirely, so the notification is the only
# surface they have and the only place this can be said.
#
#     asked     did the turn come back
#     mattered  who wrote it


def test_the_service_reads_who_answered():
    src = SERVICE.read_text(encoding="utf-8")
    assert "generatedBy" in src, (
        "the service never reads who wrote the turn, so a fallback answer "
        "is spoken as though the chosen model wrote it")
    assert 'generatedBy == "stub"' in src


def test_the_notification_says_it_and_stops_saying_it():
    src = SERVICE.read_text(encoding="utf-8")
    assert 'L10n.t("walk.offline"' in src, (
        "the notification never says the answer came from stored knowledge")
    # One notification, not one per turn: rewritten under the same id, and
    # only when the answer actually changed hands.
    assert "if (fromStore != Walking.offline)" in src, (
        "the notification is rebuilt on every turn rather than when the "
        "answerer changes, which is a notification that flickers all day")
    assert "Walking.offline = false" in src, (
        "the flag outlives the walk, so the next one starts by claiming a "
        "fallback answered a turn that has not happened yet")


# ---------------------------------------------------------------------------
# The other two shells.
#
# Three platforms, three different bargains, and the differences are the
# point rather than an inconvenience:
#
#   * **Android** suspends an app the moment it leaves the screen, so the
#     conversation needs a foreground service and pays for it with a
#     notification that cannot be dismissed.
#   * **iOS** does the same and takes the `audio` background mode instead,
#     paying with the orange indicator the system draws itself — better,
#     because a person learns one indicator for every app rather than one
#     per app.
#   * **Windows** does not suspend a minimised window at all, and this shell
#     is unpackaged so it does not even take the packaged app lifecycle.
#     There was never an operating system to satisfy; what was missing was a
#     voice loop.
#
#     asked     can the conversation survive a screen change
#     mattered  what does this platform charge for it
#
# None of this is compiled here — no Swift toolchain, no .NET SDK, and the
# proxy refuses `dl.google.com` so there is no Android SDK either. These read
# the declarations, which is where the absence of an indicator would live.

IOS_SPEC = REPO / "native/ios/project.yml"
IOS_WALK = REPO / "native/ios/Sources/Walk.swift"
WIN_WALK = REPO / "native/windows/Walk.cs"


def test_ios_declares_the_background_mode_and_both_permissions():
    spec = IOS_SPEC.read_text(encoding="utf-8")
    assert "UIBackgroundModes" in spec and "- audio" in spec, (
        "iOS is not declared as a background audio app, so the session is "
        "torn down the moment the app leaves the screen and the walk ends "
        "without saying why")
    assert "NSMicrophoneUsageDescription" in spec
    assert "NSSpeechRecognitionUsageDescription" in spec, (
        "speech recognition is its own permission on iOS, and an app that "
        "asks for it without a string is killed on the spot")
    # The microphone string has to describe the walking case too. It is what
    # somebody reads in Settings months later, and describing only the
    # push-to-talk half would be true of the gentler feature and false of
    # the product.
    m = re.search(r"NSMicrophoneUsageDescription: \"([^\"]*)\"", spec)
    assert m and "other apps" in m.group(1), (
        "the microphone permission string describes only the hold-to-talk "
        "case; the app also listens while the person is elsewhere, and the "
        "string is where they find that out")


def _swift_code(path: Path) -> str:
    """Swift with its comments removed.

    Every check in this file that searched a whole source file has been
    caught at least once finding the thing it forbids inside the comment
    explaining it. The prose in these files is deliberately thorough, which
    makes searching it for API names useless.
    """
    src = path.read_text(encoding="utf-8")
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return re.sub(r"//.*", "", src)


def test_ios_opens_and_gives_back_the_audio_session():
    src = _swift_code(IOS_WALK)
    assert ".playAndRecord" in src, (
        "the session is not record-and-play, so the reply cannot play while "
        "the microphone is open — and a conversation that cannot be "
        "interrupted is a broadcast")
    # Inside the options list itself. A sabotage that emptied the list while
    # leaving the comment above it naming both options passed a
    # whole-file search — the fourth time in this round that a guard found
    # what it forbade inside the prose forbidding it.
    m = re.search(r"options: \[([^\]]*)\]", src, re.S)
    assert m, "the session takes no options at all"
    assert ".mixWithOthers" in m.group(1) and ".duckOthers" in m.group(1), (
        "the session stops whatever the person was listening to dead rather "
        "than ducking it")
    assert "setActive(true" in src, "the session is never activated"
    assert "setActive(\n            false" in src or "setActive(false" in src, (
        "the session is never deactivated, so the orange indicator stays lit "
        "over an app that has stopped listening — an indicator that lies is "
        "worse than none")
    assert "supportsOnDeviceRecognition" in src, (
        "recognition is not kept on the device where the phone allows it, so "
        "the walk stops working in the one place it is for — out of the app "
        "and out of signal")


def test_ios_scopes_its_turns_like_the_others():
    src = _swift_code(IOS_WALK)
    assert re.search(r"let mine = turn", src), (
        "the iOS listener takes no turn number, so a late callback from a "
        "superseded recogniser acts on the one that replaced it")
    assert "func live() -> Bool { mine == turn && wants }" in src


def test_windows_says_why_it_needs_no_permission():
    """The one shell with nothing to declare. That is a fact about the
    platform and has to be written down, or the next person reads the
    absence as an oversight and adds a service Windows never wanted."""
    src = WIN_WALK.read_text(encoding="utf-8")
    assert "unpackaged" in src, (
        "nothing in the Windows walk explains why it needs no background "
        "declaration, so its absence reads as a gap rather than a fact")
    assert "SpeechRecognizer" in src, (
        "the Windows shell still has no voice loop, so there is nothing to "
        "carry however long the window stays open")


def test_windows_scopes_its_turns_and_gives_the_microphone_back():
    src = WIN_WALK.read_text(encoding="utf-8")
    assert "var mine = ++_turn" in src, (
        "the Windows loop takes no turn number")
    assert "_recogniser?.Dispose()" in src, (
        "the recogniser is never disposed, so the tray indicator stays lit "
        "over an app that has stopped listening")
    assert "TimeoutExceeded" in src, (
        "quiet is not separated from failure, so a refusal reopens the "
        "microphone forever with nothing to hear")


def test_all_three_shells_land_on_the_front_page():
    """The point of taking a conversation with you is going somewhere."""
    android = SERVICE.read_text(encoding="utf-8")
    assert "Walking.landings += 1" in android
    assert "Walking.landings" in (
        REPO / "native/android/app/src/main/java/app/jim/guardian/"
        "MainActivity.kt").read_text(encoding="utf-8")
    assert "landings += 1" in IOS_WALK.read_text(encoding="utf-8")
    assert "walking.$landings" in (
        REPO / "native/ios/Sources/JimGuardianApp.swift").read_text(
            encoding="utf-8")
    assert "Landings += 1" in WIN_WALK.read_text(encoding="utf-8")
    # And the Windows shell reads it. The first draft checked only that the
    # counter was incremented, which passes with nothing on the other end —
    # a number nobody looks at is the same as no number.
    shell = (REPO / "native/windows/Views/ShellPage.xaml.cs").read_text(
        encoding="utf-8")
    assert "Walking.Landings" in shell and "OverviewPage" in shell, (
        "the Windows shell never navigates on a walk, so the counter is a "
        "number nothing reads")
