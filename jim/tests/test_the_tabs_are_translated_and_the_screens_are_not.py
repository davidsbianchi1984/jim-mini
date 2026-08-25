"""The tab bar answers in your language. Everything behind it does not.

## The finding

`test_the_nav_is_translated_and_nothing_behind_it_is.py` in the sibling
product found this in a **console**: forty-six translated sidebar labels, and
1577 English strings on the screens they open. Its docstring says why that is
worse than no translation at all —

    A uniformly English console tells a Spanish reader the truth on the first
    screen they see. This one puts *Mercado*, *Amigos* and *Ajustes* in the
    sidebar — the app apparently answering in their language — and then hands
    them English the moment they click.

Three products ship three native shells each. All nine have a translated tab
bar. Nobody had ever counted what is behind them.

| product | iOS | Android | Windows |
|---|---|---|---|
| QRME | 2.4% | 3.8% | **0.6%** |
| JIM-mini | 13.0% | 14.2% | 9.7% |
| PDI | 8.9% | 10.2% | 3.5% |

    asked     is the console's nav-vs-behind gap measured
    mattered  is the phones' too

Nine surfaces, and the guard existed for one of them — the same shape the last
five rounds each turned up, which is why it is now ported to all three repos
in the same round it was written.

## Why the alarm surface was fixed and the rest was recorded

1813 strings cannot be hand-translated in one round, and this repo's own rule
forbids the other kind: `jim/i18n.py` says safety text is *"never
machine-mangled"*. So this round takes the subset where English is a hazard
rather than a discourtesy, and records the rest honestly.

The **alarm surface** is that subset — fourteen strings, translated into ten
languages, wired into all three shells:

* the question the crash watch asks (*"JIM is asking: are you okay?"*) and its
  answer, on a screen whose whole premise is that silence sends help;
* the three answers to an open alarm — *I have this — I'm going*, *Nobody can
  go — escalate*, *It's over — clear it* — one of which decides whether a
  ladder keeps climbing toward emergency services;
* *"This is not an emergency service. If it is one, call your local emergency
  number — this screen cannot."*

A Spanish speaker was being shown *Seguridad* on the tab and then asked, in
English, whether they were alright, with three English buttons deciding what
happens next. The backend already refuses in nine languages and promises in
all of them that emergency paths are never affected.

    asked     is the chrome localized
    mattered  is the decision localized

All three shells or none, for the reason `native_untranslated.txt` already
gives: porting one puts the responder on a localized iPhone and an English
Android, which is the per-client mistake this audit is named for, made on
purpose.

## What this file checks

Three things, and only the first is a measurement:

1. **the count only shrinks** — per shell, against `native_screens_untranslated.txt`;
2. **the extraction still matches** — every false pass in this audit came from
   a pattern that quietly stopped finding anything;
3. **every slot survives translation** — a row whose English carries `{name}`
   and whose German does not renders a sentence with the person's name missing
   from the middle of an alarm. The backend has had this check for its own
   templates since the stranger's-language round; the shells never did.
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
RECORD = Path(__file__).resolve().parent / "native_screens_untranslated.txt"

#: Files whose literals are not screen text. Named individually rather than
#: pattern-matched, so adding one is a decision somebody makes here rather
#: than a filename that quietly slips past a wildcard.
#:
#: `JimMiniOSMark` draws the brand lockup — "jim-mini", "OS", and the letters
#: of the amulet. This ratchet counts how much of a shell a non-English reader
#: cannot read, and none of those three is something a reader reads: they are
#: the drawing. Counting them would put two points of localization debt on
#: every shell that nobody could ever pay down, because translating a logo is
#: not a thing anybody wants done. The tab *beside* the mark is translated and
#: stays measured, which is where the promise actually lives.
NOT_SCREEN_TEXT = ("JimMiniOSMark",)

_BLOCK = re.compile(r"/\*.*?\*/", re.S)
_LINE = re.compile(r"//[^\n]*")
_HAS_LETTER = re.compile(r"[A-Za-z]")

#: What is a hole rather than a word: Swift `\(expr)`, Kotlin `${expr}` and
#: `$name`, XAML `{Binding Foo}`. Stripped before the letter test.
#:
#: The first version of this counted any literal containing a letter, and so
#: counted `"\(dim): \(n)%"` as an English string — a format fragment whose
#: only letters are variable names nobody reads. The ratchet then fired on a
#: card that had just been fully localized, which is a measurement telling the
#: opposite of the truth.
#:
#:     asked     does this literal contain letters
#:     mattered  does this literal contain words a reader reads
#:
#: `\uXXXX` is on the list for the same reason and was added at 0.47.6:
#: a button whose whole label is `"↻"` is a **refresh arrow**, and the
#: four hex digits of its escape are not words a reader reads.
#:
#: **XML character references, for the same reason as `\uXXXX`.**
#:
#: XAML spells a glyph the only way an attribute value can — `&#x26A0;` for
#: ⚠ — and that fragment carries the letters `x` and `A`, so a warning icon
#: read as an untranslated English string and pushed the Windows ratchet
#: above its floor. Nobody reads `&#x26A0;`; the person sees a triangle. The
#: named forms (`&amp;`, `&quot;`) are stripped alongside it, being the same
#: thing spelled with letters instead of digits.
#:
#:     asked     does this literal contain letters
#:     mattered  does a reader ever see them
_HOLE = re.compile(
    r"\\\([^)]*\)|\$\{[^}]*\}|\$[A-Za-z_]\w*|\{[A-Za-z]\w*[^}]*\}"
    r"|\\u[0-9a-fA-F]{4}|&#[Xx]?[0-9A-Fa-f]+;|&[A-Za-z]{2,8};")

#: What puts a string in front of a person, per shell. Deliberately a list of
#: named constructs rather than "every literal": an icon name, a JSON key and
#: a date format are all string literals and none of them are read by anybody.
_SWIFT = [
    r'\bText\(\s*"([^"]{2,})"', r'\bButton\(\s*"([^"]{2,})"',
    r'\bTextField\(\s*"([^"]{2,})"', r'\bSecureField\(\s*"([^"]{2,})"',
    r'\bToggle\(\s*"([^"]{2,})"', r'\bSection\(\s*"([^"]{2,})"',
    r'\bLabel\(\s*"([^"]{2,})"', r'\.navigationTitle\(\s*"([^"]{2,})"',
]
#: **The sixth shape: a string literal inside a Swift interpolation.**
#:
#: `[^"]` stops at the first quote it meets, and in Swift that quote is not
#: always the end of the string — an interpolation may contain a literal of
#: its own:
#:
#:     Text("\(m.kind ?? "—") · \(m.alt ?? m.name ?? m.id ?? "—")")
#:
#: The pattern captured `\(m.kind ?? `, which is not a string and is not
#: English. `_HOLE` could not strip it either, because the fragment has no
#: closing paren, so the letters left behind were a *property name* — and the
#: row was counted as an untranslated sentence on a card that has none. That
#: is the same false reading the `"\(dim): \(n)%"` note above records, arrived
#: at from the other side.
#:
#:     asked     does the pattern find a literal
#:     mattered  does it find the whole literal
#:
#: Blanking interpolations before matching would have fixed the false count
#: and opened a worse hole: a label whose *only* English sits inside one —
#: `Text("\(name ?? "nobody")")` — would then strip to nothing and pass. So
#: the literal is scanned rather than matched: interpolations are replaced by
#: a hole for the outer test, and each literal nested inside them is returned
#: as a candidate in its own right.
_SWIFT_OPENERS = [re.compile(p.replace('"([^"]{2,})"', '"'))
                  for p in _SWIFT]


def _swift_strings(text: str) -> set[str]:
    """Every on-screen Swift literal, whole, plus the literals nested in its
    interpolations."""
    out: set[str] = set()
    for opener in _SWIFT_OPENERS:
        for head in opener.finditer(text):
            outer: list[str] = []
            depth = 0          # how deep inside `\(` … `)` we are
            i = head.end()     # first character after the opening quote
            while i < len(text):
                ch = text[i]
                if ch == "\\" and text[i:i + 2] == "\\(":
                    depth += 1
                    # One hole for the whole interpolation, in the shape
                    # `_HOLE` already knows how to strip.
                    if depth == 1:
                        outer.append("\\(x)")
                    i += 2
                    continue
                if ch == "\\":                      # any other escape
                    i += 2
                    continue
                if depth and ch == ")":
                    depth -= 1
                elif depth and ch == "(":
                    depth += 1
                elif ch == '"':
                    if depth == 0:                  # the literal ends here
                        break
                    nested, i = _swift_nested(text, i)
                    if nested is None:
                        break
                    if len(nested) >= 2:
                        out.add(nested)
                    continue
                elif depth == 0:
                    outer.append(ch)
                i += 1
            whole = "".join(outer)
            if len(whole) >= 2:
                out.add(whole)
    return out


def _swift_nested(text: str, i: int) -> tuple[str | None, int]:
    """The literal starting at the quote `text[i]`, and the index after it.
    `(None, i)` when it never closes — an unterminated literal is a parse this
    scanner should abandon rather than guess at."""
    body: list[str] = []
    i += 1
    while i < len(text):
        if text[i] == "\\":
            i += 2
            continue
        if text[i] == '"':
            return "".join(body), i + 1
        if text[i] == "\n":
            return None, i
        body.append(text[i])
        i += 1
    return None, i


_KOTLIN = [r'\bText\(\s*"([^"]{2,})"']
_XAML = [r'\bText="([^"]{2,})"', r'\bContent="([^"]{2,})"',
         r'\bHeader="([^"]{2,})"', r'\bPlaceholderText="([^"]{2,})"']

#: **Added in 0.47.6, in QRME, and ported here in the same round.** It is the
#: reason `_KOTLIN` above is one entry long and `_SWIFT` is eight.
#:
#: Compose has no `Button(text)`. A button on this shell is a `Box` with a
#: `Text` inside it, written once as a private composable and called by name.
#: On this shell those names are `SmallAction`, `BrandButton`, `RobotAction`,
#: `labeledField`, `medRow`, `ratingRow` and `sliderRow` — and none of their
#: call sites start with `Text(`, so this file read none of them while the
#: Android record was ground from 603 down to 48.
#:
#: What that hid here is the worst of the three products. `RobotAction` is the
#: **resuscitation surface**: *Start CPR (pre-authorized)*, *Confirm:
#: unresponsive, not breathing*, *Auto-resuscitate*, *Coach CPR*, *Fetch AED*,
#: *Meet EMS*, *Stop CPR*. Nine buttons, in English, on the screen this file's
#: own opening section names as the case where English is a hazard rather than
#: a discourtesy — beside `medRow`, which labels the age, conditions and
#: resting heart rate a responder reads off the same screen.
#:
#:     asked     does the string start a `Text(`
#:     mattered  does the string end up inside one
#:
#: The rule derives the list from the shell rather than naming a construct: a
#: function with a `String` parameter whose body renders that parameter through
#: `Text(` is, by construction, something that puts a string in front of a
#: person, and the argument at that parameter's **position** is that string.
#: Not `[A-Z]\w*` — `labeledField` and `medRow` break the capitalization
#: convention — and not argument zero, because `labeledField` renders both its
#: label and its placeholder.
#: **0.47.7 — the same rule in the other two syntaxes.** 0.47.6 derived this
#: for Kotlin and left `_SWIFT` at eight hard-coded constructs. SwiftUI does
#: have `Button(_:)`, so the miss here is smaller than Compose's — but this
#: shell wraps it anyway, and what it wrapped is not small.
#:
#: `answerButton` is the pair a person taps to say whether the help helped.
#: `row` is the **medical card** — *Age*, *Conditions*, *Resting HR*,
#: *Contact* — the iPhone half of exactly the card whose Android half
#: (`medRow`) was localized last round. `rating` names what is being rated
#: (*Mood*, *Energy*) and `slider` names the vital being reported (*Heart
#: rate*, *Stress*). Fixing one shell and leaving the other two is the
#: per-client mistake this audit is named for, and last round made it.
#:
#: Swift's parameter list carries an argument label before the name
#: (`func row(_ title: String, _ value: String)`), so the name to look for in
#: the body is the *last* identifier before the colon.
_DECL = {
    ".kt": re.compile(r'\bfun\s+(\w+)\s*\(([^)]*)\)', re.S),
    ".swift": re.compile(r'\bfunc\s+(\w+)\s*\(([^)]*)\)', re.S),
}


def _label_positions(base: Path, suffix: str) -> dict[str, set[int]]:
    """{function name: argument positions it renders through `Text(`}."""
    out: dict[str, set[int]] = {}
    for path in sorted(base.rglob("*" + suffix)):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for m in _DECL[suffix].finditer(text):
            name, params = m.group(1), m.group(2)
            # The declaration's own body, bounded rather than parsed: a view
            # that renders its label does so within a few lines, and a
            # brace-matcher here would be a parser for one regex's sake.
            body = text[m.end():m.end() + 1600]
            for i, decl in enumerate(params.split(",")):
                head, _, kind = decl.partition(":")
                if kind.strip().split(" ")[0].rstrip("?") != "String":
                    continue
                # `_ title` and `title` both bind `title` inside the body.
                names = head.split()
                if not names:
                    continue
                if re.search(r"\bText\(\s*%s\b" % re.escape(names[-1]), body):
                    out.setdefault(name, set()).add(i)
    return out


def _kotlin_call_args(text: str, name: str):
    """Top-level argument slices of every `name(…)` call in `text`.

    Written out rather than regexed because the arguments here contain commas
    inside lambdas, nested calls and strings — `split(",")` on the call site
    would put `Modifier.padding(4.dp, 8.dp)` in two different positions.
    """
    for m in re.finditer(r"\b%s\s*\(" % re.escape(name), text):
        i, depth, cur, parts, quote = m.end(), 1, "", [], None
        while i < len(text) and depth:
            ch = text[i]
            if quote:
                if ch == "\\":
                    cur += text[i:i + 2]
                    i += 2
                    continue
                if ch == quote:
                    quote = None
            elif ch in "\"'":
                quote = ch
            elif ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
                if not depth:
                    break
            elif ch == "," and depth == 1:
                parts.append(cur)
                cur = ""
                i += 1
                continue
            cur += ch
            i += 1
        parts.append(cur)
        yield parts


_KOTLIN_LITERAL = re.compile(r'^\s*"((?:[^"\\]|\\.){2,})"\s*$')


def _kotlin_labels(text: str, positions: dict[str, set[int]]) -> set[str]:
    """Every literal this file hands to a label position."""
    found = set()
    for name, wanted in positions.items():
        for args in _kotlin_call_args(text, name):
            for i in wanted:
                if i < len(args):
                    lit = _KOTLIN_LITERAL.match(args[i])
                    if lit:
                        found.add(lit.group(1))
    return found


#: **Added in 0.47.0**, in the sibling repo, and ported here in the same round
#: because these three files are one guard copied twice: a blind spot in one
#: is a blind spot in all three by construction.
#:
#: A string chosen by a ternary is not at the start of an argument list, so
#: none of the patterns above could see it. `Text(cond ? "Verifies" : "Does
#: not verify")` was invisible on every shell of every product.
#:
#:     asked     is this literal the first thing in a Text(...)
#:     mattered  does a person read it
#:
#: Only phrases, deliberately. A lone token inside a ternary is as often an
#: API value (`"on"`, `"pre"`), a symbol name (`"star.fill"`) or a table key
#: as it is a word, and the conservative direction for a rule that *raises* a
#: ratcheted count is to under-count.
_TERNARY = [r'\?\s*"([^"]{2,})"\s*:\s*"([^"]{2,})"',
            r'\bif\s*\([^)]*\)\s*"([^"]{2,})"\s*else\s*"([^"]{2,})"']
_PHRASE = re.compile(r"\S\s\S")

#: **0.47.7 — the Windows half of the same blind spot.** `_XAML` reads
#: attributes: `Text="…"`, `Content="…"`. Half of this shell's labels are not
#: written in XAML at all. The settled idiom here is `x:Name` on the element
#: and `Foo.Text = L10n.T("key")` in a `Localize()` the constructor calls, so
#: a label that was never localized is sitting in the code-behind as
#: `Foo.Text = "…"` — an assignment, which `Text="` cannot match.
#:
#:     asked     is this an attribute on an element
#:     mattered  does this end up as the words on an element
#:
#: What it hid here is the desktop half of the surface whose Android half was
#: localized last round: **Confirm the person is unresponsive and not
#: breathing normally.**, both waiver verdicts (*automatic resuscitation
#: pre-authorized* / *confirm-gated operation restored*), **A responder needs
#: a name.** and **Issue Medical ID**.
#:
#: Phrases only, and for the reason `_TERNARY` already gives: a lone token in
#: an assignment is as often an API value as a word, and a rule that raises a
#: ratcheted count under-counts on purpose.
_ASSIGNED = [r'\.(?:Text|Content|Header|PlaceholderText)\s*=\s*'
             r'"((?:[^"\\]|\\.){2,})"']

#: **0.47.9 — the fifth shape, and the Swift twin of the fourth.** 0.47.6 found
#: that Compose builds a tab strip out of a `listOf` and renders it in a loop,
#: so the strings never start a `Text(`. SwiftUI does the same thing with an
#: array literal handed to `ForEach`, and that had never been read.
#:
#: What it hid was one screen, and the screen was the voiceprint consent block:
#: the heading came from the table, and the three sentences underneath it —
#: what a voiceprint permission actually *holds* — were English array elements.
#: The rows existed. Both sibling shells were already asking for them. This
#: shell showed the heading and then said, in English only, the three things
#: that heading promises.
#:
#:     asked     is this literal the first thing in a `Text(`
#:     mattered  does a loop put it on the screen
#:
#: Phrases only, the rule `_TERNARY` set: an array of API values (`["on",
#: "off"]`) is as common as an array of sentences, and a rule that raises a
#: ratcheted count under-counts on purpose.
_ARRAY = [r'\[\s*((?:"[^"]{2,}"\s*,\s*){1,}"[^"]{2,}"\s*,?)\s*\]']
_ELEMENT = re.compile(r'"([^"]{2,})"')

#: **0.47.7 — the Windows half of the same blind spot.** `_XAML` reads
#: attributes: `Text="…"`, `Content="…"`. Half of this shell's labels are not
#: written in XAML at all. The settled idiom here is `x:Name` on the element
#: and `Foo.Text = L10n.T("key")` in a `Localize()` the constructor calls, so
#: a label that was never localized is sitting in the code-behind as
#: `Foo.Text = "…"` — an assignment, which `Text="` cannot match.
#:
#:     asked     is this an attribute on an element
#:     mattered  does this end up as the words on an element
#:
#: What it hid: the sibling product's resuscitation confirmation (*Confirm the
#: person is unresponsive and not breathing normally.*), both waiver verdicts,
#: *A responder needs a name.* and *Issue Medical ID* — the desktop half of
#: the surface whose Android half was localized last round.
#:
#: Phrases only, and for the reason `_TERNARY` already gives: this shell sets
#: `Box.Text = "advance"` and `Box.Text = "bottom_right"` as *default values*
#: in input boxes, which are API tokens a person edits rather than prose a
#: person reads. A rule that raises a ratcheted count under-counts on purpose.
_ASSIGNED = [r'\.(?:Text|Content|Header|PlaceholderText)\s*=\s*'
             r'"((?:[^"\\]|\\.){2,})"']

SHELLS = {
    "ios": ("native/ios", {".swift"}, _SWIFT, r"\bL10n\s*\.\s*t\s*\("),
    "android": ("native/android", {".kt"}, _KOTLIN, r"\bL10n\s*\.\s*t\s*\("),
    "windows": ("native/windows", {".cs", ".xaml"}, _XAML,
                r"\bL10n\s*\.\s*T\s*\("),
}


def _code(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    # XAML comments are `<!-- -->`; the `//` stripper would eat URLs in it.
    return text if path.suffix == ".xaml" else _LINE.sub("", _BLOCK.sub("", text))


def _measure(shell: str) -> tuple[int, int]:
    """(English literals, localizer calls) for one shell."""
    rel, suffixes, patterns, call = SHELLS[shell]
    base = REPO / rel
    if not base.exists():
        return 0, 0
    derive = {"android": ".kt", "ios": ".swift"}.get(shell)
    positions = _label_positions(base, derive) if derive else {}
    english = calls = 0
    for path in sorted(base.rglob("*")):
        if (path.suffix not in suffixes or "L10n" in path.name
                or path.name.startswith(NOT_SCREEN_TEXT)):
            continue
        text = _code(path)
        # Swift is scanned rather than matched — see `_swift_strings`. A
        # regex cannot find the end of a literal whose interpolation holds a
        # literal of its own, and Swift's does.
        raw = (_swift_strings(text) if shell == "ios"
               else {s for pat in patterns for s in re.findall(pat, text)})
        found = {s for s in raw if _HAS_LETTER.search(_HOLE.sub("", s))}
        # `re.findall` on a two-group pattern yields tuples, one per branch.
        found |= {s for pat in _TERNARY for pair in re.findall(pat, text)
                  for s in pair
                  if _PHRASE.search(_HOLE.sub("", s).strip())
                  and _HAS_LETTER.search(_HOLE.sub("", s))}
        found |= {s for s in _kotlin_labels(text, positions)
                  if _HAS_LETTER.search(_HOLE.sub("", s))}
        if path.suffix == ".cs":
            found |= {s for pat in _ASSIGNED for s in re.findall(pat, text)
                      if _PHRASE.search(_HOLE.sub("", s).strip())
                      and _HAS_LETTER.search(_HOLE.sub("", s))}
        found |= {s for pat in _ARRAY for body in re.findall(pat, text)
                  for s in _ELEMENT.findall(body)
                  if _PHRASE.search(_HOLE.sub("", s).strip())
                  and _HAS_LETTER.search(_HOLE.sub("", s))}
        english += len(found)
        calls += len(re.findall(call, text))
    return english, calls


def _recorded() -> dict[str, int]:
    out = {}
    for line in RECORD.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        shell, count = line.split(":", 1)
        out[shell.strip()] = int(count.strip())
    return out


@pytest.mark.parametrize("shell", sorted(SHELLS))
def test_the_english_behind_the_tabs_only_shrinks(shell):
    """A ratchet, not a claim of localization. It says somebody knows how much
    of this shell a non-English reader cannot read, and by how much — the same
    thing `console_untranslated.txt` says about the console."""
    english, _ = _measure(shell)
    ceiling = _recorded()[shell]
    assert english <= ceiling, (
        f"{shell} now shows {english} English strings behind a translated tab "
        f"bar, above the {ceiling} recorded. Translate them or leave them, but "
        "the number does not go up: the tab bar is a promise the screens have "
        "to keep.")


@pytest.mark.parametrize("shell", sorted(SHELLS))
def test_the_record_is_not_stale(shell):
    """The other direction. A record left above the real number is a ceiling
    somebody can drift back up into without the ratchet ever firing."""
    english, _ = _measure(shell)
    ceiling = _recorded()[shell]
    assert ceiling - english <= 20, (
        f"{shell} is at {english} against a recorded {ceiling} — {ceiling - english} "
        "of slack. Lower the record to what is actually there, or the ratchet "
        "is holding a line nobody is near.")


@pytest.mark.parametrize("shell", sorted(SHELLS))
def test_the_measurement_still_measures(shell):
    """A guard on the guard. A pattern that stopped matching reports a shell
    with no untranslated strings, which is exactly the answer this file exists
    to refuse to give by accident."""
    english, calls = _measure(shell)
    assert english + calls >= ratchets.floor(f"tabs.onscreen.{shell}"), (
        f"only {english + calls} on-screen strings found in {shell} — the "
        "extraction has stopped matching, and the ratchet above would pass on "
        "nothing")
    assert calls >= ratchets.floor(f"tabs.localizer_calls.{shell}"), (
        f"{shell} makes no localizer calls at all — either the call pattern "
        "broke or the shell lost its localization entirely")


def test_the_swift_scan_reads_past_a_literal_inside_an_interpolation():
    """A guard on the sixth widening, in both directions.

    The regex it replaced stopped at the first quote inside `\\(…)` and
    handed back `\\(m.kind ?? ` — not a string, not English, and counted as
    an untranslated sentence because the property name in it has letters.

    The obvious repair is to blank interpolations before matching, and it is
    wrong in the more dangerous direction: it makes a label whose only
    English lives *inside* one disappear, so the ratchet would have passed on
    a sentence no non-English reader can read. Both are asserted here, which
    is the only reason this test is worth its length.
    """
    counted = lambda src: {s for s in _swift_strings(src)
                           if _HAS_LETTER.search(_HOLE.sub("", s))}

    # The row that produced the false count: an em-dash fallback, a kind and
    # an alt text. Every letter belongs to a property name.
    assert counted(r'Text("\(m.kind ?? "—") · \(m.alt ?? m.name ?? "—")")') == set()

    # The hole blanking would have opened: the sentence is only inside.
    assert counted(r'Text("\(name ?? "nobody has said")")') == {"nobody has said"}

    # Outside and inside at once — both are read by somebody, both counted.
    assert counted(r'Button("Save \(what ?? "it") now")') == {"Save \\(x) now", "it"}

    # And the two findings this file already records still hold: a plain
    # label counts, a format fragment does not.
    assert counted('Text("Put a photograph up")') == {"Put a photograph up"}
    assert counted(r'Text("\(dim): \(n)%")') == set()


def test_the_ternary_scan_can_find_one():
    """A guard on the widening. `_TERNARY` was added because a string chosen
    by a condition was invisible to every other pattern here; a version of it
    that matches nothing would restore exactly the blind spot it was written
    to close, and would do it quietly."""
    swift = 'Label(ok ? "It verifies fine" : "It does not verify", x)'
    kotlin = 'Text(if (ok) "It verifies fine" else "It does not verify")'
    for source in (swift, kotlin):
        found = {s for pat in _TERNARY for pair in re.findall(pat, source)
                 for s in pair}
        assert found == {"It verifies fine", "It does not verify"}, (source, found)


def test_a_lone_token_in_a_ternary_is_not_counted():
    """The other half of that rule, stated as a test rather than a comment.
    `cond ? "on" : "off"` is as likely to be an API value as a word, and this
    rule raises a ratcheted number - so it counts phrases and says so."""
    source = 'Text(on ? "on" : "off") + Text(x ? "star.fill" : "star")'
    counted = {s for pat in _TERNARY for pair in re.findall(pat, source)
               for s in pair if _PHRASE.search(_HOLE.sub("", s).strip())}
    assert counted == set(), counted


def test_the_shell_declares_the_buttons_this_rule_reads(tmp_path):
    """A guard on the derivation. `_label_positions` returning nothing
    restores the exact blind spot it was written to close — every button on
    the shell invisible — and would do it while every other test here passed,
    which is how the blind spot lasted as long as it did."""
    (tmp_path / "Widgets.kt").write_text(
        "private fun SmallAction(text: String, onClick: () -> Unit) {\n"
        "    Box(Modifier.clip(RoundedCornerShape(50))) { Text(text) }\n"
        "}\n"
        "internal fun labeledField(label: String, value: String,\n"
        "                          placeholder: String, onChange: (String) -> Unit) {\n"
        "    Column { Text(label)\n"
        "        OutlinedTextField(value = value, onValueChange = onChange,\n"
        "            placeholder = { Text(placeholder) }) }\n"
        "}\n"
        "private fun icon(name: String) { Image(painterResource(name)) }\n",
        encoding="utf-8")
    positions = _label_positions(tmp_path, ".kt")
    assert positions == {"SmallAction": {0}, "labeledField": {0, 2}}, positions
    # A function that takes a String and never renders it is not a label.
    assert "icon" not in positions, positions
    source = ('SmallAction("Send") { go() }\n'
              'labeledField("Desk id", deskId, "dsk_…") { deskId = it }\n')
    assert _kotlin_labels(source, positions) == {"Send", "Desk id", "dsk_…"}


def test_a_comma_inside_an_argument_does_not_shift_the_positions():
    """The reason `_kotlin_call_args` is a scanner and not a `split(",")`.
    Getting this wrong reads a colour or a lambda as the label and reports a
    localized screen — the quiet direction, again."""
    positions = {"labeledField": {0, 2}}
    source = ('labeledField("Price (USD)", price, "0.00") { price = it }\n'
              'labeledField(t(k, l), v, join(a, b)) { v = it }\n'
              'row(Modifier.padding(4.dp, 8.dp), "not a label")\n')
    assert _kotlin_labels(source, positions) == {"Price (USD)", "0.00"}


def test_the_real_android_shell_has_label_wrappers():
    """The same guard against this repo's own sources rather than a fixture.
    Compose has no `Button(text)`; if this shell suddenly declares no
    label-bearing composable at all, the derivation has stopped deriving."""
    base = REPO / "native/android"
    if not base.exists():
        pytest.skip("no android shell in this repo")
    assert _label_positions(base, ".kt"), (
        "no label-bearing composable found in the Android shell — every "
        "button on it is now invisible to the ratchet above")


# --- the slots, which are the part that breaks silently -------------------

_TABLES = {
    "ios": REPO / "native/ios/Sources/L10n.swift",
    "android": next(iter((REPO / "native/android").rglob("L10n.kt")), None),
    "windows": REPO / "native/windows/L10n.cs",
}
#: Where a row starts, and which bracket closes it. The body is then scanned
#: with `_body_at` rather than a character class.
#:
#: The first version of this used `[^)]*` for Kotlin and `[^}]*` for C#, and
#: could not read four of the fourteen alarm rows — because their text
#: contains `({concern})` and `(relayed as a request — …)`. It reported them
#: missing from tables they were sitting in.
#:
#:     asked     does the row match a pattern for a row
#:     mattered  does the row end where the pattern says it does
#:
#: The rows most likely to carry a bracket are the ones carrying a slot, which
#: are precisely the rows the slot check exists for.
_ROW = {
    "ios": (re.compile(r'"([\w.]+)":\s*\['), "[",
            re.compile(r'"(\w\w)":\s*"((?:[^"\\]|\\.)*)"')),
    "android": (re.compile(r'"([\w.]+)"\s+to\s+mapOf\('), "(",
                re.compile(r'"(\w\w)"\s+to\s+"((?:[^"\\]|\\.)*)"')),
    "windows": (re.compile(r'\["([\w.]+)"\]\s*=\s*new\(\)\s*\{'), "{",
                re.compile(r'\["(\w\w)"\]\s*=\s*"((?:[^"\\]|\\.)*)"')),
}
_SLOT = re.compile(r"\{(\w+)\}")
_CLOSING = {"[": "]", "(": ")", "{": "}"}


def _body_at(text: str, open_at: int, opener: str) -> str:
    """The row body starting at its opening bracket, string-aware.

    Depth counted only for this bracket kind, and characters inside a quoted
    string ignored entirely — a translation is allowed to contain any bracket
    it likes, and several of them do.
    """
    depth, i, quote = 0, open_at, ""
    while i < len(text):
        c = text[i]
        if quote:
            if c == "\\":
                i += 2
                continue
            if c == quote:
                quote = ""
        elif c in "\"'":
            quote = c
        elif c == opener:
            depth += 1
        elif c == _CLOSING[opener]:
            depth -= 1
            if depth == 0:
                return text[open_at + 1:i]
        i += 1
    return ""


def _rows(shell: str) -> dict[str, dict[str, str]]:
    path = _TABLES[shell]
    if path is None or not path.exists():
        return {}
    row_pat, opener, lang_pat = _ROW[shell]
    text = path.read_text(encoding="utf-8")
    out: dict[str, dict[str, str]] = {}
    for m in row_pat.finditer(text):
        body = _body_at(text, m.end() - 1, opener)
        out[m.group(1)] = dict(lang_pat.findall(body))
    return out


@pytest.mark.parametrize("shell", sorted(_TABLES))
def test_every_slot_survives_every_translation(shell):
    """A row whose English says `{name} was contacted` and whose Portuguese
    forgot the hole renders an alarm with the person's name missing from the
    middle of it. Nothing else in this repo would notice: the string is
    present, the language is right, and the sentence is wrong.

    **Skipped, loudly, in a shell whose table holds no slotted row at all.** A
    check over an empty set is the failure mode this whole audit is named
    after, and a skip says so in the run output where a green dot would not.
    """
    rows = _rows(shell)
    if not any(_SLOT.search(r.get("en", "")) for r in rows.values()):
        pytest.skip(f"{shell}'s table holds no slotted row, so this check has "
                    f"nothing to prove here ({len(rows)} rows read)")
    broken = []
    for key, row in _rows(shell).items():
        want = set(_SLOT.findall(row.get("en", "")))
        for lang, text in row.items():
            if lang != "en" and set(_SLOT.findall(text)) != want:
                broken.append(f"{key}/{lang}: has "
                              f"{sorted(set(_SLOT.findall(text)))}, "
                              f"English has {sorted(want)}")
    assert not broken, (
        f"{shell}: {len(broken)} translation(s) lost or invented a slot:\n    "
        + "\n    ".join(broken[:20]))


@pytest.mark.parametrize("shell", sorted(_TABLES))
def test_the_row_parser_reads_the_table(shell):
    """A guard on the guard, and the floor is deliberately the smallest real
    table across the three products rather than a comfortable number. The
    check above skips a shell with no slotted rows; this one is what catches a
    parser that has stopped reading rows at all."""
    rows = _rows(shell)
    assert len(rows) >= ratchets.floor(f"tabs.table_rows.{shell}"), (
        f"only {len(rows)} rows parsed from {shell}'s table — the row pattern "
        "has stopped matching, and the slot check would pass on nothing")
    assert all(r.get("en") for r in rows.values()), (
        f"{shell}: a row parsed with no English text, so the language pattern "
        "is matching row headers rather than their contents")


def test_the_alarm_surface_is_translated_on_every_shell():
    """The part of this round that is a fix rather than a measurement.

    Named keys rather than a count, because this is the set where a missing
    translation is a person not understanding a question about whether they
    need help. All three shells or none.
    """
    keys = {"alarm.none", "alarm.lead", "alarm.raised", "alarm.attending",
            "alarm.going", "alarm.cannot_go", "alarm.clear",
            "alarm.not_emergency", "alarm.asking", "alarm.concern",
            "alarm.im_okay", "alarm.tripped", "alarm.armed", "alarm.ems"}
    langs = {"en", "es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar"}
    problems = []
    for shell in sorted(_TABLES):
        rows = _rows(shell)
        for key in sorted(keys):
            if key not in rows:
                problems.append(f"{shell}: {key} is not in the table")
                continue
            missing = sorted(langs - set(rows[key]))
            if missing:
                problems.append(f"{shell}: {key} lacks {missing}")
    assert not problems, "\n    ".join(problems[:20])


def test_the_shells_ask_for_the_alarm_keys_they_hold():
    """Holding them is not showing them. The screens have to read them, and
    this audit has been caught by exactly that distinction before."""
    screens = {
        "ios": REPO / "native/ios/Sources/Views/SafetyView.swift",
        "android": next(iter((REPO / "native/android").rglob("Screens.kt")), None),
        "windows": REPO / "native/windows/Views/SafetyPage.xaml.cs",
    }
    thin = []
    for shell, path in screens.items():
        if path is None or not path.exists():
            thin.append(f"{shell}: no safety screen found")
            continue
        used = set(re.findall(r'"(alarm\.\w+)"', _code(path)))
        if len(used) < 14:
            thin.append(f"{shell}: reads {len(used)} of the 14 alarm keys")
    assert not thin, "\n    ".join(thin)
