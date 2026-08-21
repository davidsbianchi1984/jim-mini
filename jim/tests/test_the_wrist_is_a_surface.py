"""The wrist is a surface.

The console has thirty-six watch faces drawn at wrist size and the iPhone
app has a `WatchCard`. A field report asked whether the watch screens
worked for people who had attached watches, and the honest answer was that
nothing on any wrist could reach the Guardian: there was no watch target.

    asked     do the watch screens look right
    mattered  is there a watch

`native/wear/` is the target. It cannot be compiled in this environment —
there is no Android SDK here — so this file is what stands in for a build:
it checks the things a compiler would not catch anyway, which are the ones
that actually go wrong when a client is written against a server from
memory.

## What this guards, and what it deliberately does not

`jim/tests/clientpaths.py` walks the three phone shells and asks, of every
published route, whether each can reach it. That guard is right about
phones and would be wrong here — the wrist is *deliberately* incomplete,
and a completeness rule would push routes onto a watch to satisfy a test.
So the wear app is its own Gradle project, outside that accounting, and
what holds it honest instead is the opposite question:

* every path the watch calls must be a route the server really publishes;
* the pairing chain must be walked in the order the server requires, or
  the first refusal is one no user can act on;
* the sensor and the microphone must both be let go when the screen goes.

The third is the rule every voice screen in the console learned the hard
way: a thing left open by a screen nobody is on is a thing nobody switched
on.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
WEAR = REPO / "native/wear"
API = WEAR / "app/src/main/java/app/jim/wear/WearApi.kt"
STATE = WEAR / "app/src/main/java/app/jim/wear/WatchState.kt"
SCREENS = WEAR / "app/src/main/java/app/jim/wear/MainActivity.kt"
MANIFEST = WEAR / "app/src/main/AndroidManifest.xml"


def _api_src() -> str:
    return API.read_text(encoding="utf-8")


def _called_paths() -> set[str]:
    """Every server path `WearApi` builds, with the interpolations blanked.

    `"/monitors/$uid"` becomes `/monitors/{}` — the shape a route table can
    be compared against without pretending to know what a Kotlin string
    template held at runtime.
    """
    out = set()
    for raw in re.findall(r'call\(\s*"([^"]+)"', _api_src()):
        out.add(re.sub(r"\$\{?[A-Za-z_][A-Za-z0-9_.]*\}?", "{}", raw))
    return out


def _published() -> set[str]:
    """The same shape, read off the route decorators in jim/api.py."""
    src = (REPO / "jim/api.py").read_text(encoding="utf-8")
    out = set()
    for path in re.findall(r'@app\.(?:get|post|put|delete)\(\s*"([^"]+)"', src):
        out.add(re.sub(r"\{[^}]+\}", "{}", path))
    return out


# -- the doors are real ------------------------------------------------------

def test_the_watch_exists_at_all():
    assert API.exists(), (
        "there is no wear target — the watch screens are drawings again")
    for f in (STATE, SCREENS, MANIFEST,
              WEAR / "app/src/main/res/values/strings.xml",
              WEAR / "settings.gradle.kts", WEAR / "README.md"):
        assert f.exists(), f"{f.relative_to(REPO)} is missing"


def test_every_path_the_watch_calls_is_a_route_the_server_publishes():
    """The defect a compiler cannot see. A Kotlin client compiles perfectly
    against a URL that 404s, and nobody finds out until somebody is standing
    in a kitchen pressing a button on their wrist."""
    published = _published()
    for path in sorted(_called_paths()):
        assert path in published, (
            f"the watch calls {path!r} and jim/api.py publishes no such "
            "route — this compiles and 404s at the wrist")


def test_the_watch_reaches_only_what_a_wrist_is_for():
    """The other direction, and the point of not registering this as a
    fourth shell: the wrist should stay small on purpose."""
    called = _called_paths()
    assert len(called) <= 14, (
        f"the watch now reaches {len(called)} routes — a wrist that can "
        "reach everything is a phone with a worse screen")
    for path in called:
        assert not any(word in path for word in
                       ("billing", "subscription", "admin", "provider",
                        "export", "report")), (
            f"{path} is not something anybody does at their wrist")


# -- the chain is walked in the order the server requires ---------------------

def test_the_watch_registers_before_it_attaches_a_microphone():
    """`mic.attach` refuses a microphone on a device that is not on the
    account. A watch that attached first would show somebody "no device
    called 'smart_watch' on this account" as their very first screen."""
    src = STATE.read_text(encoding="utf-8")
    order = [m for m in re.findall(
        r"WearApi\.(register|attachMic|plugIn)\b", src)]
    assert order[:3] == ["register", "attachMic", "plugIn"], (
        f"the pairing chain runs {order[:3]} — the server requires "
        "register, then attach, then switch the monitor on")


def test_the_watch_delivers_under_the_name_it_was_lent():
    """`mic.heard` refuses a delivery under a name the channel was not lent
    to, so the audit line — which device heard this — is never a guess.
    That refusal is only useful if the watch names itself the same way at
    every one of the three doors."""
    src = _api_src()
    assert 'const val DEVICE_NAME = "smart_watch"' in src
    # No hand-written device name anywhere else: one constant, or the
    # refusal above becomes a bug report nobody can reproduce.
    stray = [m for m in re.findall(r'"(smart_watch|watch|wrist)"', src)]
    assert stray.count("smart_watch") == 1, (
        "the watch spells its own device name more than once — the three "
        "doors can now disagree")


def test_the_pulse_names_the_row_it_came_off():
    assert '.put("monitor", "wrist")' in _api_src(), (
        "the watch posts a pulse without naming the roster row, so the "
        "wrist row goes on saying `waiting` while the wrist reports")


def test_the_watch_sends_words_and_never_audio():
    """The privacy half of the design, and the reason the wear target was
    worth building before an audio one."""
    src = _api_src()
    assert '.put("words", words)' in src
    assert "audio_base64" not in src, (
        "the watch has learned to upload audio — the promise that nothing "
        "but text leaves the wrist is now false")
    assert "MediaRecorder" not in (SCREENS.read_text(encoding="utf-8") + src)


# -- and it lets go ----------------------------------------------------------

def test_leaving_the_screen_releases_the_sensor_and_the_microphone():
    src = SCREENS.read_text(encoding="utf-8")
    # `onDispose`, not `DisposableEffect` — the import line matches the
    # latter and a scan that starts there reads the import block as the
    # teardown and passes on nothing.
    at = src.find("onDispose")
    assert at > 0, "nothing tears down when the watch screen goes away"
    teardown = src[at:at + 400]
    for call in ("ear.stop()", "wrist.stop()", "releaseMic"):
        assert call in teardown, (
            f"{call} is not in the teardown — a sensor or a microphone left "
            "open by a screen nobody is on is one nobody switched on")


def test_the_permissions_are_asked_at_the_switch_not_at_launch():
    """A permission asked before there is anything to do with it is one
    somebody grants without a reason, which is the opposite of what every
    switch in this product is supposed to mean."""
    src = SCREENS.read_text(encoding="utf-8")
    assert "rememberLauncherForActivityResult" in src
    # Neither request may sit in a launch-time effect.
    launch = re.search(r"LaunchedEffect\(Unit\)\s*\{([^}]*)\}", src)
    assert launch, "no launch effect to check"
    assert "askBody" not in launch.group(1)
    assert "askMic" not in launch.group(1)


def test_the_watch_declares_the_permissions_it_asks_for():
    manifest = MANIFEST.read_text(encoding="utf-8")
    for perm in ("INTERNET", "BODY_SENSORS", "RECORD_AUDIO"):
        assert perm in manifest, f"{perm} is requested and never declared"
    assert "android.hardware.type.watch" in manifest, (
        "without this the Play Store offers this app to phones")


def test_the_refusal_that_reaches_the_wrist_is_the_servers_own_sentence():
    """Every refusal in this product is written to be read by a person and
    translated into their language. Showing `HTTP 403` on a watch throws
    away the one thing that makes a refusal useful at arm's length."""
    src = _api_src()
    assert 'o.optString("message")' in src and 'o.optString("detail")' in src
    assert "class Refused" in src and "val sentence: String" in src


# -- the wear target stays outside the phone-shell accounting -----------------

def test_the_wrist_is_not_counted_as_a_phone_shell():
    """Its own Gradle project, deliberately — a wear module nested inside
    `native/android/` would let a watch-only door satisfy a phone shell's
    door requirement, and the completeness guard would stop meaning what it
    says."""
    assert (WEAR / "settings.gradle.kts").exists()
    assert not list((REPO / "native/android").rglob("*/wear/*.kt")), (
        "a wear source has appeared inside the Android shell's tree")
    from .clientpaths import NATIVE

    for lang in NATIVE:
        assert "wear" not in str(lang.root), (
            "the wear app is being walked as a phone shell")
