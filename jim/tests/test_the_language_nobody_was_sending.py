"""The language nobody was sending.

## The finding

JIM's public surface answers people who have no account yet: the sign-up and verification steps, and the routes a person reaches before there is a user to store a language against. Those handlers compose real sentences — what was sent, what is held, what to do next.

Every one of those sentences is chosen from `Accept-Language`. **No native
shell was sending that header.** The browser sends it without being asked,
which is why the console looked correct and the three clients a person is most
likely to be holding were the ones answering in English.

    asked     can the shell say it in the reader's language
    mattered  does the reader's language ever reach the server

## What was missing, and where

Two things, and only the second one is obvious once the first is written down:

* **A language to send.** Each shell's `language` is read from the stored
  account setting and is `"en"` until an account exists. `L10n.deviceLanguage`
  (iOS), `L10n.deviceLanguage()` (Android) and `L10n.DeviceLanguage()`
  (Windows) read what the device has been carrying all along —
  `Locale.preferredLanguages`, the system configuration's locale list,
  `CurrentUICulture` — drop the region, and fall back to English rather than
  guessing.
* **Somewhere to send it.** One line in each shell's shared request helper.

Both halves are checked below, because a header set to a constant looks
identical to a header set correctly from the outside.
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

#: (label, the shell's L10n file, the resolver's name, its platform source,
#:  the shell's HTTP client, the resolver as written at the call site)
SHELLS = (
    ("ios", "native/ios/Sources/L10n.swift", "deviceLanguage",
     "Locale.preferredLanguages", "native/ios/Sources/ApiClient.swift", "L10n.deviceLanguage"),
    ("android", "native/android/app/src/main/java/app/jim/guardian/L10n.kt", "deviceLanguage",
     "Resources.getSystem().configuration.locales", "native/android/app/src/main/java/app/jim/guardian/ApiClient.kt",
     "L10n.deviceLanguage()"),
    ("windows", "native/windows/L10n.cs", "DeviceLanguage",
     "CurrentUICulture", "native/windows/ApiClient.cs", "L10n.DeviceLanguage()"),
)


def _code(path: Path) -> str:
    """Source with comments and doc comments stripped.

    Every one of these resolvers is *described* in the comment above it, so a
    check that searched the whole file would be satisfied by the prose
    explaining the thing rather than the thing.
    """
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"^\s*(///|//|\*)[^\n]*$", "", text, flags=re.M)
    return text


def test_every_shell_can_resolve_a_language_without_an_account():
    """The input that was missing.

    Not "does the shell have an L10n table" — all three did, in ten languages,
    while the only language variable in the app came from an account.
    """
    missing = []
    for name, l10n, symbol, source, _, _ in SHELLS:
        path = REPO / l10n
        if not path.exists():
            continue
        code = _code(path)
        if symbol not in code:
            missing.append(f"{name}: {l10n} has no {symbol}")
        elif source not in code:
            missing.append(
                f"{name}: {symbol} exists but never reads {source} — "
                "it is not asking the device")
    assert not missing, (
        "these shells cannot work out what language their reader speaks "
        "without an account:\n    " + "\n    ".join(missing))


def test_every_shell_tells_the_server_what_language_its_reader_speaks():
    """Both halves. A shell that resolves the language and then sends a
    constant has done the work and thrown it away, and from outside the two
    are indistinguishable."""
    wrong = []
    for name, _, _, _, client, resolver in SHELLS:
        path = REPO / client
        if not path.exists():
            continue
        lines = [ln for ln in _code(path).splitlines()
                 if "accept-language" in ln.lower()]
        if not lines:
            wrong.append(
                f"{name}: {client} never sets an accept-language header, so "
                "every sentence the backend composes for a reader with no "
                "account arrives in English")
        elif [ln for ln in lines if resolver not in ln]:
            # Every line, not any line. PDI's iOS client builds requests in two
            # places — the shared helper and the intake submit the accountless
            # recipient uses — and an `any` here passed an injection that
            # hardcoded "en" on one of them, because the other one was still
            # right. The union hid a surface inside the guard written to stop
            # exactly that.
            #
            #     asked     does this client send the reader's language
            #     mattered  does every request this client makes send it
            bad = len([ln for ln in lines if resolver not in ln])
            wrong.append(
                f"{name}: {bad} of {len(lines)} accept-language header(s) set "
                f"without {resolver} — the header is there and the reader's "
                "language is not in it")
    assert not wrong, "\n    ".join([""] + wrong)


def test_the_files_this_guard_names_are_still_there():
    """A guard on the guard: a renamed client makes both checks above skip
    silently, which reads exactly like passing."""
    for name, l10n, _, _, client, _ in SHELLS:
        for rel in (l10n, client):
            assert (REPO / rel).exists(), (
                f"{name}: {rel} is gone — the checks above skip a shell that "
                "does not exist, so this file would pass on nothing")


def test_the_backend_really_does_read_this_header():
    """The other end of the wire.

    If `negotiate` stopped being called on `Accept-Language`, the shells would
    keep sending a header nothing reads and this file would keep passing.
    """
    text = (REPO / "jim/i18n.py").read_text(encoding="utf-8")
    assert "def negotiate(" in text, (
        "jim/i18n.py has no negotiate() — the header the shells now send is not "
        "being turned into a language by anybody")
    callers = [p for p in (REPO / "jim").rglob("*.py")
               if "negotiate(" in p.read_text(encoding="utf-8")
               and p.name != "i18n.py"]
    assert callers, (
        "nothing outside i18n.py calls negotiate(), so no route chooses a "
        "language from the header these shells now send")
