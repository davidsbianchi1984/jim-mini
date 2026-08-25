"""The native shells record failures under the same rule as the console.

`app/src/errors.ts` established it: the operation and the status, never the
message, never an unredacted path. The three native shells now do the same —
but in Swift, Kotlin and C#, written by hand, three times.

That is the risk this file exists for. One rule with four implementations
drifts, and it drifts silently: a redaction pattern narrowed on Android leaks
nothing on the desktop, so nothing an ordinary test runs would notice. The
shells have no test runner here at all — the native workflow compiles them and
stops — so the checks below are structural, reading the sources the way
`test_error_report_carries_nothing_private.py` reads the TypeScript.

What they cannot check is behaviour: that Swift's FNV-1a and Kotlin's produce
the same digits is asserted by neither, only that both are FNV-1a with the
same constants. Stated rather than hidden.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from . import ratchets


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()

SHELLS = {
    "ios": REPO / "native/ios/Sources/Problems.swift",
    "android": next(
        (p for p in (REPO / "native/android").rglob("Problems.kt")), None),
    "windows": REPO / "native/windows/Problems.cs",
}

CLIENTS = {
    "ios": REPO / "native/ios/Sources/ApiClient.swift",
    "android": next(
        (p for p in (REPO / "native/android").rglob("ApiClient.kt")), None),
    "windows": REPO / "native/windows/ApiClient.cs",
}

# Words that would mean a shell had started keeping content.
FORBIDDEN = ("message", "detail", "body", "response", "text", "payload",
             "stack", "error")


def _shell(name: str) -> str:
    path = SHELLS[name]
    assert path is not None and path.exists(), f"{name} has no Problems source"
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize("shell", sorted(SHELLS))
def test_the_recorder_has_nowhere_to_put_a_message(shell):
    """The signature is the safeguard, in every language.

    Three parameters — method, path, status — so a caller cannot pass a detail
    string by accident. Kotlin's held an Android `Context` as a fourth at first;
    it now keeps that in the object, which is why all three read the same.
    """
    src = _shell(shell)
    sig = re.search(
        r"(?:static\s+)?(?:public\s+static\s+)?(?:func|fun|void)\s+"
        r"[Rr]ecord\s*\(([^)]*)\)", src)
    assert sig, f"{shell}: no record(...) found"
    params = [p.strip() for p in sig.group(1).split(",") if p.strip()]
    assert len(params) == 3, f"{shell}: record takes {params}"
    leaked = [p for p in params
              if any(w in p.lower() for w in FORBIDDEN)]
    assert not leaked, f"{shell}: a message can arrive through {leaked}"


@pytest.mark.parametrize("shell", sorted(SHELLS))
def test_the_stored_record_has_no_field_that_could_hold_content(shell):
    """What each buffer may contain. The five the console stores, plus the
    `sent` watermark, and nothing that could hold a sentence."""
    src = _shell(shell).lower()
    for field in ("op", "status", "count", "day", "fingerprint", "sent"):
        assert field in src, f"{shell}: no {field} field"
    # `detail`/`message` must not appear as a stored field. They may appear in
    # prose, so this looks for them in the shapes a field takes.
    for word in ("message", "detail"):
        for shape in (f"var {word}", f"val {word}", f"{word}:",
                      f"public string {word}"):
            assert shape not in src, f"{shell}: {shape!r} looks like a stored field"


@pytest.mark.parametrize("shell", sorted(SHELLS))
def test_the_redaction_is_as_wide_as_the_console(shell):
    """The four patterns, present and unnarrowed in every shell.

    The suffix length is the one that has already gone wrong once: requiring
    six hex characters let `cap_9f2`, `req_77aa` and `usr_1` through when the
    console's version was written. A shell that quietly restored that bound
    would leak on that platform alone.
    """
    src = _shell(shell)
    for pattern in (r"\[a-z\]\{2,8\}_\[0-9a-z\]\+",
                    r"\[0-9a-f\]\{8\}-\[0-9a-f\]\{4\}",
                    r"\[0-9\]\+",
                    r"\[A-Za-z0-9_-\]\{24,\}"):
        assert re.search(pattern, src), (
            f"{shell}: the redaction is missing or narrower than the "
            f"console's — no /{pattern}/")


@pytest.mark.parametrize("shell", sorted(SHELLS))
def test_the_fingerprint_is_the_console_s(shell):
    """FNV-1a with the same two constants, so one failure fingerprints the
    same on a phone as on a desktop. A shell with its own hash would split one
    bug into two rows in the aggregate."""
    src = _shell(shell)
    assert "2166136261" in src, f"{shell}: not FNV-1a (offset basis missing)"
    assert "16777619" in src, f"{shell}: not FNV-1a (prime missing)"


def _record_calls(shell: str) -> list[str]:
    """The problem-record calls this client makes, as their argument lists."""
    src = CLIENTS[shell].read_text(encoding="utf-8")
    return re.findall(r"[Pp]roblems\.[Rr]ecord\(([^)]*)\)", src)


@pytest.mark.parametrize("shell", sorted(CLIENTS))
def test_the_client_records_both_kinds_of_failure(shell):
    """Reaching a server and being refused, and never reaching one at all.

    The second is the one an implementation forgets, because it is an
    exception rather than a status — and it is also the most interesting
    signal in the aggregate, since it means the app could not talk to its own
    backend.
    """
    path = CLIENTS[shell]
    assert path is not None and path.exists(), f"{shell}: no ApiClient"
    src = path.read_text(encoding="utf-8")
    calls = _record_calls(shell)
    assert len(calls) >= ratchets.floor(f"problems.recorded.{shell}"), (
        f"{shell}: {len(calls)} record call(s) — expected the refused case "
        "and the never-reached-a-server case")
    # The last argument, whichever way the language spells it: Swift and
    # Kotlin name it (`status: 0`), C# passes it positionally.
    def _status(call: str) -> str:
        last = call.split(",")[-1].strip()
        return last.split(":")[-1].strip()

    assert any(_status(c) == "0" for c in calls), (
        f"{shell}: nothing records status 0, so a request that never reached "
        f"a server is invisible. Calls: {calls}")


def test_the_android_recorder_is_switched_on():
    """Kotlin's recorder needs a context, and something has to give it one.

    This is the check the rest of this file did not have, and its absence was
    not theoretical: every test above passed while `Problems.attach` existed
    in all three products and was called in none of them. The Android shells
    recorded nothing, and recorded it quietly — the recorder refuses to crash
    over a diagnostic, so a missing attach has no symptom at all.

    Worth naming as a class of defect rather than a typo. The checks above ask
    whether each piece is *correct*; correctness of every piece is not the
    same as the feature being *on*. iOS and Windows have no equivalent because
    they have no equivalent step: `UserDefaults` and `%APPDATA%` are reachable
    from anywhere, which is exactly why nobody thought to look for the third
    platform's extra wire.
    """
    activity = next(
        (p for p in (REPO / "native/android").rglob("MainActivity.kt")), None)
    assert activity is not None, "no MainActivity.kt"
    src = activity.read_text(encoding="utf-8")
    assert re.search(r"Problems\.attach\(", src), (
        "MainActivity never calls Problems.attach — the Android shell will "
        "record nothing, and will not say so")


@pytest.mark.parametrize("shell", sorted(CLIENTS))
def test_the_client_never_hands_the_recorder_a_message(shell):
    """The call sites, not just the signature."""
    src = CLIENTS[shell].read_text(encoding="utf-8")
    for args in re.findall(r"[Pp]roblems\.[Rr]ecord\(([^)]*)\)", src):
        parts = [a.strip() for a in args.split(",")]
        assert len(parts) == 3, f"{shell}: record called with {parts}"
        status = parts[2].split(":")[-1].strip().lower()
        assert not any(w in status for w in ("detail", "message",
                                             "text", "body")), (
            f"{shell}: a message is being passed as the status: {parts[2]}")
