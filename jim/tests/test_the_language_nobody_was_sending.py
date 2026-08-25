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

from . import ratchets


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

#: Where a request actually leaves the shell. Not the same question as "does
#: this file mention the header" — see the check below.
DISPATCH = {
    "ios": r'URLSession\.shared\.(?:data|upload|bytes)\(',
    "android": r'\.openConnection\(\)',
    "windows": r'_http\.SendAsync\(',
}


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


def test_every_place_a_request_leaves_the_shell_carries_the_header():
    """0.57.9. The half the two checks above cannot see.

    They ask *is the header set with the resolver*, which is answered by the
    one line in the shared helper. They cannot ask **how many requests never
    go through that helper** — and in this estate the answer was most of them:

        QRME      Windows 21 of 22 sends, iOS 3 of 4, Android 1 of 2
        JIM-mini  Windows 15 of 16, iOS 1 of 2, Android 4 of 5
        PDI       Windows 3 of 4

    Uploads, streams and raw-response reads, every one of them building its
    own request beside the funnel. Those calls carry a token, so a *valid*
    token still picks the owner's stored language — but an expired one is not
    a principal, and the refusal falls back to the header that was not there.

        asked     does this client set the header with the resolver
        mattered  does every request this client makes carry it

    The fix was a dispatcher per shell rather than a line per call site,
    because a line per call site is the thing that was missing twenty-one
    times.
    """
    uncovered = []
    for name, _, _, _, client, _ in SHELLS:
        path = REPO / client
        if not path.exists():
            continue
        src = _code(path)
        for m in re.finditer(DISPATCH[name], src):
            # The window is the request's own construction, not the file: a
            # header set four hundred characters earlier belongs to a
            # different request.
            before = src[max(0, m.start() - 900):m.start()]
            after = src[m.end():m.end() + 500]
            if "accept-language" not in (before + after).lower():
                line = src[:m.start()].count("\n") + 1
                uncovered.append(f"{name}: {client}:{line} sends a request "
                                 "that carries no accept-language")
    assert not uncovered, (
        "these requests leave the shell without the reader's language:\n    "
        + "\n    ".join(uncovered)
        + "\n  Route them through the shell's dispatcher rather than adding "
          "a line to each.")


#: Where a request is *built*. Used only as the reach floor — after the fix
#: the Windows shell has exactly one place a request *leaves* from, which is
#: the point of the fix and useless as evidence that the file was read.
BUILT = {
    "ios": r'URLRequest\(',
    "android": r'\.openConnection\(\)',
    "windows": r'new HttpRequestMessage\(',
}


def test_the_scan_reaches_every_client():
    """A pattern that stopped matching would report every shell clean by
    finding no requests at all — the failure this arc keeps producing.

    Counted on requests *built* rather than requests *sent*: consolidating
    the sends behind one dispatcher is exactly what this round did, so a floor
    on send sites would now be a floor of one.
    """
    seen = {}
    for name, _, _, _, client, _ in SHELLS:
        path = REPO / client
        if not path.exists():
            continue
        seen[name] = len(re.findall(BUILT[name], _code(path)))
    assert len(seen) == 3, f"only found {sorted(seen)}"
    for name, n in seen.items():
        assert n >= ratchets.floor(f"language.requests_built.{name}"), (
            f"{name}: only {n} request(s) built — the pattern has ")


#: Where the console attaches a header to every request it makes. The three
#: shells are checked against *this* rather than against a list written here,
#: so a header added to the console cannot quietly stay console-only.
CONSOLE = "app/src/api.ts"

#: A header the console sends that a phone has no business sending. Empty on
#: purpose so far — every entry needs a reason, and "the phone does not do
#: that" is usually a defect rather than a reason.
CONSOLE_ONLY: set[str] = set()


def _console_headers() -> set[str]:
    """Headers the console's shared `req` helper sets on every call.

    Read from the helper rather than the whole file: the file also builds
    the odd one-off request, and a header set on one of those is not a
    promise the shells have to match.
    """
    src = (REPO / CONSOLE).read_text(encoding="utf-8")
    i = src.index("async function req<T>(")
    body = src[i:src.index("\n}", i)]
    return {h.lower() for h in re.findall(r'headers\[\s*"([\w-]+)"\s*\]', body)}


def _shell_headers(client: str, shell: str) -> set[str]:
    src = _code(REPO / client)
    pat = {"ios": r'forHTTPHeaderField:\s*"([\w-]+)"',
           "android": r'setRequestProperty\(\s*"([\w-]+)"',
           "windows": r'Headers\.(?:TryAddWithoutValidation|Add)\(\s*"([\w-]+)"'}[shell]
    return {h.lower() for h in re.findall(pat, src)}


def test_every_header_the_console_sends_the_shells_send_too():
    """0.58.0. The generalisation of the round before this one.

    0.57.9 asked whether every *request* carried the header the helper set.
    This asks the prior question: **is the set of headers the same at all?**
    It was not. `x-llm-api-key` — the person's own model key, which the
    backend reads per request and never stores — was sent by the console and
    by no shell, so a key set on the desktop was used there and the
    deployment's key used on the phone, on the same account, with nothing
    saying so.

        asked     does every request carry the headers this client sends
        mattered  does this client send the headers the product has

    Read from the console's own helper rather than from a list here, so a
    header added there cannot quietly stay there.
    """
    expected = _console_headers() - CONSOLE_ONLY
    missing = []
    for name, _, _, _, client, _ in SHELLS:
        if not (REPO / client).exists():
            continue
        for header in sorted(expected - _shell_headers(client, name)):
            missing.append(f"{name}: {client} never sends {header!r}, which "
                           f"the console sends on every request")
    assert not missing, "\n    ".join([""] + missing)


def test_the_console_helper_is_still_being_read():
    """A helper that moved or was renamed would make the check above compare
    the shells against an empty set, which reads exactly like passing."""
    found = _console_headers()
    assert len(found) >= ratchets.floor("console.request_headers"), found
    assert "authorization" in found
