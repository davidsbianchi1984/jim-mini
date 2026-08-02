"""The console speaks one language. Its own phones speak ten.

## The finding

JIM's native shells each carry an `L10n` table in ten languages, and a round
two releases ago gave all three of them a `deviceLanguage` resolver so the
accountless screen could use it. The desktop console has **no `l10n.ts` at
all** — no table, no language type, no negotiation, nothing reading
`navigator.languages`. Every string on it is English and can only be English.

That is not a gap somebody left half-open. It is a surface nobody ever asked
the question of, and the reason is worth naming: QRME's console was audited
for language because QRME's console *had* a table to audit. The check followed
the infrastructure rather than the reader.

    asked     is the localized surface complete
    mattered  which surfaces were never localized at all

Fifty-eight English strings sit on the screen a person meets before any
account exists — the sign-up form, the verification flow, the password reset,
every refusal in between.

## What this file is, and is not

It is a measurement, ratcheted. Building a localization layer for a whole
console is not one round, and pretending otherwise by translating a handful of
buttons would leave the same screen half-English with nothing recording which
half. So the count is written down and can only go down, which is the same
ratchet `native_untranslated.txt` uses for the shells.

It does **not** claim the console is localized. It claims somebody knows it is
not, and by how much.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


def _repo_root() -> Path:
    for d in Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()
SNAPSHOT = Path(__file__).resolve().parent / "console_untranslated.txt"
#: Every screen the console renders, not just the pre-session one.
#:
#: This file measured `Onboarding.tsx` alone for two releases, which is how
#: seven hundred English strings on nineteen gated screens stayed out of the
#: count while the record said the console's backlog was thirty-five.
#:
#:     asked     is the pre-session screen localized
#:     mattered  is the console localized
#:
#: The gated screens are a different argument from the accountless one — their
#: reader has a language setting the server already honours — which is why the
#: nav is localized this round and the screen bodies are recorded rather than
#: half-done.
PRE_SESSION = tuple(
    f"screens/{p.name}" for p in
    sorted((Path(__file__).resolve().parents[2] / "app" / "src"
            / "screens").glob("*.tsx")))


def _prose() -> list[str]:
    """User-visible English, from TypeScript's own parser.

    A regex over the source would miss any chunk carrying an interpolation and
    report the brace-free scraps of sentences it could not cross. QRME learned
    that three times; this borrows the extractor rather than the lesson.
    """
    proc = subprocess.run(
        ["node", "scripts/jsx-text.mjs"] + [f"src/{p}" for p in PRE_SESSION],
        cwd=REPO / "app", capture_output=True, text=True)
    assert proc.returncode == 0, (
        "the JSX text extractor failed, so this check would report a "
        f"comfortable zero:\n{proc.stderr}")
    found = json.loads(proc.stdout)
    # Prefixed by screen, the way QRME's record is. With one screen the bare
    # string was enough; across twenty it is the difference between a record
    # somebody can act on and six hundred lines of loose sentences.
    #
    # **A separator is not prose.** Fragments left between two interpolations
    # — a bare `:`, a `·`, a `%` — carry no word anybody reads, and counting
    # them made this guard fire on a card whose every sentence had just been
    # localized. That is the same mistake the shells' version of this made
    # with `"\(dim): \(n)%"`, one file over and one release later.
    #
    #     asked     did the extractor find a string here
    #     mattered  did it find a word a reader reads
    return sorted({f"{screen.split('/')[-1].removesuffix('.tsx')}: {text}"
                   for screen in PRE_SESSION
                   for text in found[f"src/{screen}"]
                   if re.search(r"[A-Za-z]", text)})


def _recorded() -> set[str]:
    return {line.strip() for line in
            SNAPSHOT.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")}


def test_the_english_that_is_there_is_written_down():
    """Both directions, so the file cannot rot into a list of things that were
    true once — and so translating something shows up as progress rather than
    as a mismatch nobody explains."""
    actual, recorded = set(_prose()), _recorded()
    appeared = sorted(actual - recorded)
    resolved = sorted(recorded - actual)
    problems = []
    if appeared:
        problems.append(
            f"{len(appeared)} English string(s) on the pre-session surface "
            "that nobody has decided about:\n    "
            + "\n    ".join(s[:90] for s in appeared))
    if resolved:
        problems.append(
            f"{len(resolved)} recorded string(s) are gone — strike them from "
            f"{SNAPSHOT.name}:\n    " + "\n    ".join(s[:90] for s in resolved))
    assert not problems, "\n\n".join(problems)


def test_the_backlog_only_shrinks():
    ceiling = int(re.search(r"# ceiling: (\d+)",
                            SNAPSHOT.read_text(encoding="utf-8")).group(1))
    assert len(_recorded()) <= ceiling, (
        f"{len(_recorded())} untranslated strings, above the {ceiling} this "
        "guard started at")


def test_the_extractor_can_still_see():
    """A guard on the guard, against a fixture whose answer is known.

    Everything above trusts a subprocess. If node disappears or the parser
    stops recognising `JsxText`, `_prose()` returns an empty list and the
    backlog looks solved. Pointing this at a real screen would not do: its
    answer changes with the product copy.
    """
    proc = subprocess.run(
        ["node", "scripts/jsx-text.mjs", "scripts/jsx-text.fixture.tsx"],
        cwd=REPO / "app", capture_output=True, text=True)
    assert proc.returncode == 0, f"the extractor will not run:\n{proc.stderr}"
    found = json.loads(proc.stdout)["scripts/jsx-text.fixture.tsx"]
    assert found == [
        "A heading",
        "A paragraph that runs across several lines of source and is "
        "nonetheless one sentence to whoever reads it.",
        "Wrapped around",
        "an interpolated value.",
        "a placeholder",
        "a title",
        "an aria label",
        "A button",
    ], f"the extractor no longer reads the fixture as documented:\n{found}"


def test_the_shells_that_do_have_a_table_still_have_one():
    """The comparison the finding rests on.

    If the native tables were themselves gone, this file would be recording a
    console that is no worse than anything else — which is a different
    situation and a different round.
    """
    tables = [
        "native/ios/Sources/L10n.swift",
        "native/android/app/src/main/java/app/jim/guardian/L10n.kt",
        "native/windows/L10n.cs",
    ]
    present = [t for t in tables if (REPO / t).exists()]
    assert len(present) == 3, (
        f"only {len(present)} of the three shells still carry an L10n table "
        f"({present}). This file's whole premise is that the phones speak ten "
        "languages and the console speaks one.")


# --- the layer this round added -------------------------------------------

SRC = REPO / "app" / "src"


def _languages() -> list[str]:
    text = (SRC / "l10n.ts").read_text(encoding="utf-8")
    union = re.search(r"export type Lang =([^;]+);", text).group(1)
    return re.findall(r'"(\w+)"', union)


def test_every_key_is_translated_everywhere():
    """No partial rows.

    The reader of this screen has no account to fall back to a setting from,
    so English here is not a default — it is a guess about who is reading.
    """
    text = (SRC / "l10n.ts").read_text(encoding="utf-8")
    langs = _languages()
    gaps = {}
    for match in re.finditer(r'"([\w.]+)":\s*\{(.*?)\n  \},', text, re.S):
        present = set(re.findall(r"(\w+):", match.group(2)))
        missing = [c for c in langs if c not in present]
        if missing:
            gaps[match.group(1)] = missing
    assert not gaps, (
        "these console strings are missing languages:\n    "
        + "\n    ".join(f"{k}: {', '.join(v)}" for k, v in sorted(gaps.items())))


def test_there_are_keys_at_all():
    """A guard on the guard: an empty table reports a perfect zero."""
    keys = re.findall(r'^  "([\w.]+)":', (SRC / "l10n.ts").read_text("utf-8"),
                      re.M)
    assert len(keys) >= 15, (
        f"only {len(keys)} keys found — the pattern has stopped matching, so "
        "the completeness check above would pass on nothing")
    assert len(_languages()) == 10


def test_the_screen_asks_the_visitor_and_not_a_stored_setting():
    """The whole reason this layer exists.

    Every other localization path in this product takes a user id. The screen
    a person meets before they have one is exactly where that cannot work, and
    reading a stored language here would read the default every time.
    """
    code = re.sub(r"/\*.*?\*/|//[^\n]*", "",
                  (SRC / "screens" / "Onboarding.tsx").read_text("utf-8"),
                  flags=re.S)
    assert "visitorLang(" in code, (
        "Onboarding no longer asks visitorLang() — every visitor is back to "
        "English no matter what their browser asked for")
    fn = (SRC / "l10n.ts").read_text("utf-8")
    fn = fn[fn.index("export function visitorLang"):]
    assert 'split("-")' in fn, (
        "visitorLang no longer drops the region, so es-419 and es-ES stop "
        "matching es")
    assert 'return "en"' in fn, (
        "visitorLang no longer falls back to English for an unrecognised tag "
        "— it should fall back, never guess")


def test_no_key_is_translated_into_ten_languages_and_used_nowhere():
    """A key in the table that no screen looks up.

    This has now shipped twice: two keys in QRME's 0.27.0 and eight in JIM's
    0.28.0, all translated into ten languages, all wired to nothing. The
    strings stayed English on screen while the table said otherwise, and every
    completeness check passed — because they check that a key *has* its ten
    languages, never that anything asks for it.

        asked     is every key in the table complete
        mattered  does every key in the table reach a screen

    A dead key is not merely waste. It is a translation somebody paid
    attention to, sitting next to the English it was supposed to replace, with
    nothing to say which of the two a reader will actually get.
    """
    table = set(re.findall(r'^  "([\w.]+)":', (SRC / "l10n.ts").read_text("utf-8"),
                           re.M))
    used, prefixes = set(), set()
    for screen in list(SRC.rglob("*.tsx")) + list(SRC.rglob("*.ts")):
        text = screen.read_text(encoding="utf-8")
        used |= set(re.findall(r'\b(?:t|tr|L)\(\s*"([\w.]+)"', text))
        # A key can also be built: `t(`nav.${n.id}`, lang)`. The literal head
        # of such a template covers every key under it.
        #
        # The first version of this check read literal keys only and called
        # all fifty-three `nav.*` keys dead — every one of them live, on the
        # console's own navigation. A guard against dead translations that
        # would have had somebody delete the working ones.
        #
        #     asked     is this key looked up by a literal string
        #     mattered  is this key reachable
        prefixes |= {p for p in re.findall(r'\b(?:t|tr|L)\(\s*`([\w.]+)\$\{',
                                           text)}
    dead = sorted(k for k in table - used
                  if not any(k.startswith(p) for p in prefixes))
    assert not dead, (
        f"{len(dead)} key(s) are translated and looked up by nothing:\n    "
        + "\n    ".join(dead)
        + "\n  Wire them, or delete them — but a translated string nobody "
          "reads is the English still being read instead.")
