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

import json
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
    """This test's first draft said the shells call **no** gated platform
    API, and told whoever falsified that to raise the floor to a count. The
    voice round falsified it: the Talk cards open the microphone on both
    phones, so the count is now the record — the exact APIs, in the exact
    files, each covered by the declaration tests above. A new gated call
    shows up here by name, with its declaration, or not at all.
    """
    ios = _used(sorted(REPO.glob("native/ios/Sources/**/*.swift")), IOS_NEEDS)
    android = _used(sorted(REPO.glob("native/android/**/*.kt")), ANDROID_NEEDS)
    assert len(IOS_NEEDS) >= 8 and len(ANDROID_NEEDS) >= 5
    assert ios == {"AVAudioRecorder": "TalkCard.swift",
                   "AVAudioSession": "TalkCard.swift"}, ios
    assert android == {"MediaRecorder": "Screens.kt"}, android


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


# --- the fields a release has to write ---------------------------------------
#
# `release_fields.txt` is byte-identical in all three products. It exists
# because 0.60.7 was bumped from a prose list that named Android's two fields
# and left iOS's unnamed, and the iOS build code is invisible to a search for
# the version being replaced. The guards below read the file rather than
# trusting that anybody read it: the first checks every field the checklist
# names, the second checks that the checklist names every version a native
# shell ships.

FIELDS = Path(__file__).resolve().parent / "release_fields.txt"


def _field_rows() -> list[tuple[str, str, str, str]]:
    """`(glob, field, shape, locator)` for each row of the checklist."""
    rows = []
    for line in FIELDS.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = [p.strip() for p in line.split("|")]
        assert len(parts) == 4, f"malformed checklist row: {line!r}"
        rows.append((parts[0], parts[1], parts[2], parts[3]))
    return rows


def _paths_for(glob: str) -> list[Path]:
    """Files a checklist glob names, less any ` !path` it excludes."""
    parts = glob.split(" !")
    dropped = {p.strip() for p in parts[1:]}
    return [p for p in sorted(REPO.glob(parts[0].strip()))
            if str(p.relative_to(REPO)) not in dropped]


def _shaped(shape: str, version: str) -> str:
    return {"version": version,
            "code": str(_code(version)),
            "version.0": f"{version}.0",
            "vversion": f"v{version}"}[shape]


def _read_field(path: Path, locator: str) -> list[str]:
    """Every value `locator` finds in `path`.

    A `$.` path rather than a regex for JSON, because `"version"` appears once
    per dependency in `package-lock.json` and a regex would read all of them.
    """
    if locator.startswith("$."):
        node = json.loads(path.read_text(encoding="utf-8"))
        for part in locator[2:].split("."):
            key = "" if part == "<root>" else part
            if not isinstance(node, dict) or key not in node:
                return []
            node = node[key]
        return [str(node)]
    return [m if isinstance(m, str) else m[0]
            for m in re.findall(locator, path.read_text(encoding="utf-8"), re.M)]


def test_the_release_checklist_is_readable():
    """A guard on the guard. A checklist that parsed to nothing would let the
    forward half below pass while checking no field at all — the shape of
    failure this suite is most often bitten by.

    The count it compares against lives in the file's own header rather than
    in a number written here, so there is nothing to register as a floor and
    nothing to drift: the row count and the stated count are edited together
    or they disagree.

    Emptying the checklist entirely does not get past this pair either. The
    reverse guard reads the native shells for versions no row names, so a
    checklist with no rows fails there naming every field it stopped
    covering."""
    rows = _field_rows()
    stated = int(re.search(r"^# status: manifest — (\d+) fields$",
                           FIELDS.read_text(encoding="utf-8"), re.M).group(1))
    assert stated == len(rows), (
        f"the checklist says {stated} fields and carries {len(rows)}")
    assert {s for _, _, s, _ in rows} <= {"version", "code", "version.0",
                                          "vversion"}, "unknown shape"


def test_every_field_the_checklist_names_carries_this_version():
    """The forward half: what the checklist names must exist, and be current.

    A field named here and absent from the file is as much a failure as a
    field carrying the wrong number — it means the checklist is describing a
    release process that no longer matches the tree.
    """
    version = _version()
    problems = []
    for glob, field, shape, locator in _field_rows():
        paths = _paths_for(glob)
        if not paths:
            problems.append(f"{glob} — the checklist names it, the tree has no such file")
            continue
        want = _shaped(shape, version)
        for path in paths:
            found = _read_field(path, locator)
            rel = path.relative_to(REPO)
            if not found:
                problems.append(f"{rel}: {field} — named here, not found in the file")
                continue
            for got in found:
                if got != want:
                    problems.append(f"{rel}: {field} is {got!r}, this release is {want!r}")
    assert not problems, (
        f"{len(problems)} release field(s) do not carry {version}:\n    "
        + "\n    ".join(problems)
        + "\n  Every field above is one a person installs or a store reads.")


def test_every_version_a_native_shell_ships_is_named_here():
    """The reverse half: a native shell may not carry a version this file has
    not been told about.

    This is what makes the checklist keep up. Adding a shell, or a fourth
    version field to an existing one, fails here until the row is written —
    which is the failure that did not happen when `CURRENT_PROJECT_VERSION`
    was added to the iOS spec and no list gained a line.
    """
    version = _version()
    code = str(_code(version))
    # A locator is matched here with a word-boundary guard in front of it,
    # which the forward half does not need and this half cannot work without.
    # `MARKETING_VERSION:\s*"..."` is a substring of `WATCH_MARKETING_VERSION:
    # "..."`, so a bare search reads a brand-new unnamed field as one the
    # checklist already covers. The injection that added exactly that field
    # passed this guard until the lookbehind was put in. A plain `\b` will not
    # do the job: it is false before the `<` of `<Version>`.
    locators = [r"(?<![A-Za-z0-9_])(?:" + loc + r")"
                for _, _, _, loc in _field_rows() if not loc.startswith("$.")]
    problems = []
    for path in [IOS_SPEC, GRADLE, *CSPROJ]:
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if version not in line and code not in line:
                continue
            if line.lstrip().startswith(("#", "//", "<!--")):
                continue
            if any(re.search(loc, line) for loc in locators):
                continue
            problems.append(f"{path.relative_to(REPO)}:{n}: {line.strip()}")
    assert not problems, (
        f"{len(problems)} line(s) in a native shell carry this release's "
        f"version or build code and no row of release_fields.txt names "
        f"them:\n    " + "\n    ".join(problems)
        + "\n  Add the field to the checklist — an unnamed version field is "
          "one the next bump will not know to write.")
