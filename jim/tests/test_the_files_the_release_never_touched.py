"""Fifty-five releases, and the phones still say they are version 0.1.0.

0.57.6 ended by naming its own next question: *whatever the guard checks, ask
first which files it does not open.* This is that question asked of the
release itself rather than of a guard.

A cut bumps `pyproject.toml`, `<pkg>/api.py`, `app/package.json`, the
lock file, the README banner, the README release row and the changelog. Seven
files, and the number reaches everything a *server* or a *console* reports.
The three native shells report their own version from three build files no
step in that list touches:

    native/ios/project.yml          MARKETING_VERSION: "0.1.0"
    native/android/…/build.gradle.kts   versionName = "0.1.0"
    native/windows/*.csproj         (no <Version> at all)

Nine declarations across three products, every one of them 0.1.0 or absent,
through every release since the shells were written.

    asked     does the product carry the version it cut
    mattered  does the thing a person installs carry it

This is not cosmetic in the way a stale README is. `versionName` is the string
on the Play listing and in Settings › Apps; `MARKETING_VERSION` is the App
Store version and the one a crash report is filed against; the `.csproj`
version is the file version Windows shows in Properties. An install that
reports 0.1.0 cannot be told apart from any other install, so a problem report
from the field names nothing — and this repo *has* a problem collector, which
is the part that makes the omission bite.

`versionCode` is worse still: Android refuses an upload whose code is not
greater than the last one, so a store submission was going to fail on the
first try regardless of what the listing said.

## The other thing these files hold

The same files carry what the shell is allowed to do — the plist usage
strings, the `uses-permission` rows. Those are checked here too, because they
have the identical property: no guard opens them, and getting one wrong is
fatal rather than untidy. iOS **terminates** an app that opens a camera with
no `NSCameraUsageDescription`. Android throws `SecurityException`.

Nothing in this product's shells calls a gated API at all — the sibling
product opens a camera and a microphone on both phones, and this one opens
neither. The check exists so that the first screen here to do it cannot ship
without the sentence that lets it.

### One trap, walked into while writing this

The first pass at the capability check read `LAContext` in QRME's
`Signing.swift` and `BiometricPrompt` in `Signing.kt` and was ready to report
two missing declarations. Both are in **comments** — prose explaining why the
shells use WebAuthn instead, since a local biometric check is the app's own
word about itself and an assertion is not. A guard that counts a mention as a
use invents a defect, which is worse than missing one. Comments are stripped
before anything is counted, and `test_a_platform_api_named_in_a_comment_is_not_a_use`
holds that line.
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
IOS_SPEC = REPO / "native" / "ios" / "project.yml"
GRADLE = (REPO / "native" / "android" / "app" / "build.gradle.kts")
CSPROJ = sorted((REPO / "native" / "windows").glob("*.csproj"))

#: Every platform API that needs a declaration before it may run, and the
#: declaration it needs. Deliberately short: each row is a rule the platform
#: enforces at runtime, not a lint anybody has an opinion about.
IOS_NEEDS = {
    "AVCaptureSession": "NSCameraUsageDescription",
    "AVAudioRecorder": "NSMicrophoneUsageDescription",
    "AVAudioSession": "NSMicrophoneUsageDescription",
    "CLLocationManager": "NSLocationWhenInUseUsageDescription",
    "HKHealthStore": "NSHealthShareUsageDescription",
    "LAContext": "NSFaceIDUsageDescription",
    "CNContactStore": "NSContactsUsageDescription",
    "PHPhotoLibrary": "NSPhotoLibraryUsageDescription",
    "EKEventStore": "NSCalendarsUsageDescription",
    "CMPedometer": "NSMotionUsageDescription",
}
ANDROID_NEEDS = {
    "MediaRecorder": "android.permission.RECORD_AUDIO",
    "AudioRecord": "android.permission.RECORD_AUDIO",
    "ProcessCameraProvider": "android.permission.CAMERA",
    "BiometricPrompt": "android.permission.USE_BIOMETRIC",
    "LocationManager": "android.permission.ACCESS_FINE_LOCATION",
    "HealthConnectClient": "android.permission.health.READ_STEPS",
}


def _version() -> str:
    text = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    return re.search(r'^version = "([^"]+)"$', text, re.M).group(1)


def _code(version: str) -> int:
    """The build number a version implies.

    Android will not accept an upload whose `versionCode` is not greater than
    the last one, and a hand-kept counter beside a hand-kept version string is
    two things to forget instead of one. Derived, so there is nothing to keep:
    0.57.7 is 57007, and every later version is a larger number.
    """
    major, minor, patch = (int(p) for p in version.split(".")[:3])
    return major * 1_000_000 + minor * 1_000 + patch


def _uncommented(path: Path) -> str:
    """Source with comments removed.

    See the docstring: `LAContext` and `BiometricPrompt` both appear in this
    repo only inside prose about why they are *not* used, and reading them as
    calls produced two findings that were the reader's, not the code's.
    """
    src = re.sub(r'/\*.*?\*/', '', path.read_text(encoding="utf-8"), flags=re.S)
    return re.sub(r'^\s*(?://|///|\*)[^\n]*$', '', src, flags=re.M)


def _used(paths, apis) -> dict[str, str]:
    """{api: the file that calls it} for every api in `apis` actually used."""
    found = {}
    for path in paths:
        src = _uncommented(path)
        for api in apis:
            if re.search(r'\b%s\b' % re.escape(api), src):
                found.setdefault(api, path.name)
    return found


# --- the version a person installs -------------------------------------------

def test_the_iphone_ships_the_version_that_shipped():
    """`MARKETING_VERSION` is the App Store version and the one a crash report
    is filed against."""
    spec = IOS_SPEC.read_text(encoding="utf-8")
    marketing = re.search(r'MARKETING_VERSION:\s*"([^"]+)"', spec).group(1)
    assert marketing == _version(), (
        f"the iOS spec says {marketing} and this release is {_version()} — "
        f"the number a person sees in the App Store and the number in a crash "
        f"report are both this one")
    build = re.search(r'CURRENT_PROJECT_VERSION:\s*"([^"]+)"', spec).group(1)
    assert build == str(_code(_version())), (
        f"CURRENT_PROJECT_VERSION is {build}, not {_code(_version())}")


def test_the_android_shell_ships_the_version_that_shipped():
    """`versionName` is the Play listing and Settings › Apps. `versionCode`
    is the one the store refuses an upload over."""
    gradle = GRADLE.read_text(encoding="utf-8")
    name = re.search(r'versionName\s*=\s*"([^"]+)"', gradle).group(1)
    assert name == _version(), (
        f"build.gradle.kts says {name} and this release is {_version()}")
    code = int(re.search(r'versionCode\s*=\s*(\d+)', gradle).group(1))
    assert code == _code(_version()), (
        f"versionCode is {code}, not the {_code(_version())} this version "
        f"implies — Android refuses an upload that does not increase it")


def test_the_windows_shell_ships_the_version_that_shipped():
    """No `<Version>` at all is not a smaller mistake than a wrong one: the
    build defaults to 1.0.0 and every install reports the same thing."""
    assert CSPROJ, "no .csproj under native/windows"
    for path in CSPROJ:
        text = path.read_text(encoding="utf-8")
        found = re.search(r'<Version>([^<]+)</Version>', text)
        assert found, f"{path.name} declares no <Version>"
        assert found.group(1) == _version(), (
            f"{path.name} says {found.group(1)} and this release is "
            f"{_version()}")


def test_the_version_this_asks_about_is_the_one_that_cut():
    """A guard on the guard. Read from `pyproject.toml`, which is what the
    release bumps first, so this cannot pass by comparing three copies of a
    stale number with each other."""
    version = _version()
    assert re.fullmatch(r'\d+\.\d+\.\d+', version), version
    assert version != "0.1.0", "the version this compares against is the placeholder"
    assert _code("0.57.7") == 57_007 and _code("1.0.0") > _code("0.99.999")


# --- what the shell is allowed to do -----------------------------------------

def test_every_ios_capability_used_is_declared():
    """iOS terminates an app that opens a camera or a microphone with no
    usage string. Not a warning — the process is killed on the call."""
    spec = IOS_SPEC.read_text(encoding="utf-8")
    used = _used(sorted(REPO.glob("native/ios/Sources/**/*.swift")), IOS_NEEDS)
    missing = sorted(
        f"{api} in {where} needs {IOS_NEEDS[api]}"
        for api, where in used.items()
        if not re.search(r'\b%s:' % IOS_NEEDS[api], spec))
    assert not missing, (
        "the iOS spec declares no usage string for:\n    "
        + "\n    ".join(missing)
        + "\n  iOS kills the app on the call rather than refusing it.")


def test_every_android_capability_used_is_declared():
    manifest = (REPO / "native" / "android" / "app" / "src" / "main"
                / "AndroidManifest.xml").read_text(encoding="utf-8")
    used = _used(sorted(REPO.glob("native/android/**/*.kt")), ANDROID_NEEDS)
    missing = sorted(
        f"{api} in {where} needs {ANDROID_NEEDS[api]}"
        for api, where in used.items()
        if ANDROID_NEEDS[api] not in manifest)
    assert not missing, (
        "the Android manifest declares no permission for:\n    "
        + "\n    ".join(missing))


# --- the checks have to be able to see, and to fail --------------------------

def test_there_are_build_files_to_read():
    """Three globs and three files. A path that stopped resolving would report
    a clean shell by finding nothing to check, which is the failure this whole
    arc keeps producing."""
    assert IOS_SPEC.exists() and GRADLE.exists() and CSPROJ
    assert len(sorted(REPO.glob("native/ios/Sources/**/*.swift"))) >= 24
    assert len(sorted(REPO.glob("native/android/**/*.kt"))) >= 6


def test_the_capability_check_reaches_the_calls_this_shell_makes():
    """This product's shells call **no** gated platform API — no camera, no
    microphone, no location, no health store — so there is no count to floor
    here, and pretending otherwise would be a floor of zero dressed up.

    What is floored instead is the reading: the tables are non-empty and the
    files they are applied to exist and are numerous. The check earns its
    place by what it will catch, not by what it catches today — the sibling
    product opens a camera and a microphone on both phones, and the first
    screen here to do the same must bring its declaration with it.
    """
    ios = _used(sorted(REPO.glob("native/ios/Sources/**/*.swift")), IOS_NEEDS)
    android = _used(sorted(REPO.glob("native/android/**/*.kt")), ANDROID_NEEDS)
    assert len(IOS_NEEDS) >= 8 and len(ANDROID_NEEDS) >= 5
    assert not ios and not android, (
        "a shell here has started calling a gated platform API — good, but "
        "this floor was written on the fact that none did, so raise it to a "
        f"count now that there is one to count: {ios} {android}")


def test_a_platform_api_named_in_a_comment_is_not_a_use(tmp_path):
    """The mistake this file was one edit away from shipping.

    `LAContext` and `BiometricPrompt` appear in this repo only inside prose
    about why the shells use WebAuthn instead — a local biometric check is the
    app's own word about itself, and an assertion is not. Reported as calls,
    they are two missing declarations that are not missing and not calls.
    """
    swift = tmp_path / "Signing.swift"
    swift.write_text(
        '/// The `LAContext.evaluatePolicy` boolean is the app\'s own word.\n'
        '// so LAContext is not used here\n'
        'struct Signing {\n'
        '    func go() { let s = AVAudioSession.sharedInstance() }\n'
        '}\n')
    used = _used([swift], IOS_NEEDS)
    assert set(used) == {"AVAudioSession"}, used


def test_the_capability_check_can_fail(tmp_path):
    """A camera opened with no usage string, which is a terminated app."""
    swift = tmp_path / "Scanner.swift"
    swift.write_text('let session = AVCaptureSession()\n')
    used = _used([swift], IOS_NEEDS)
    spec = 'info:\n  properties:\n    CFBundleDisplayName: X\n'
    missing = [api for api in used
               if not re.search(r'\b%s:' % IOS_NEEDS[api], spec)]
    assert missing == ["AVCaptureSession"]


def test_the_version_checks_can_fail():
    """The placeholder these three files carried for fifty-five releases."""
    assert "0.1.0" != _version()
    assert _code("0.1.0") != _code(_version())
