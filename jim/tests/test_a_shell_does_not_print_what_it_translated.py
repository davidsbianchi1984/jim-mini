"""English on a screen that the same shell already translates.

The shape 0.47.9 found in the iPhone's voiceprint consent block, and 0.54.0
found again in the Windows beacon list:

    Detail = $"{b.Location ?? "—"} · {b.Scans} scan(s)"
             + (b.Active ? "" : " · picked up"),

while `nmg.beacon.scans` — *"{n} scan(s)"* — and `nmg.beacon.pickedup` —
*"picked up"* — sat in that same shell's table, translated into ten languages,
asked for by nothing. An owner reading the app in German was shown

    Garten · 3 scan(s) · picked up

which is the worst version of a localized product: translated chrome around
the two words that carry the meaning, so the screen looks finished and reads
as broken.

## Why the dead-key guard did not catch it

`test_a_shell_asks_for_a_key_it_has` sees a row nothing asks for and records
it. That is the right measurement and it is one step short: it cannot tell a
row **waiting for a screen that does not exist** from a row whose screen
exists and is printing the English by hand. Both look like silence from the
table's side. The 335-row backlog held both kinds, and only reading the
screens told them apart.

So this asks the other question: is any string a shell **shows** identical to
the English of a row that shell **holds**?

## What it deliberately does not flag

A literal in a display position is a bug. A literal anywhere else is usually a
protocol value — a JSON field name, a default a form posts back, a `kind` the
API matches on — and translating one of those breaks the request rather than
the reader. `DockStateBox.Text = "handle"` reads like a label and is a value
this page sends; it stays English on purpose.

That is why this greps **assignment into a display property**, not the whole
source. The first version of this check greped everything, reported 88 hits
across three shells, and 86 of them were protocol values. A guard that cries
wolf 86 times out of 88 is one nobody reads.

## 0.57.8 — the rows this skipped, and why they were the interesting ones

For four releases `_rows` opened with

    if "{" in english:
        continue

and every row with a slot in it went unchecked. That is not a small corner of
the table: a row with a slot is a row about *something*, which is most of what
a screen actually says. And a sentence assembled around a value is the one a
screen is most likely to hand-build, because building it is what the code is
already doing:

    ? $"closest overlap {best}, below the {th} threshold for naming anyone"

against `ns.who.below` — *"closest overlap {best}, below the {threshold}
threshold for naming anyone"* — the same sentence, hole for hole, sitting in
that same shell's table in ten languages.

    asked     does a screen print a whole English row verbatim
    mattered  does a screen print an English row the reader will never see
              translated, however it is spelled

Found from the other side, and by accident: 0.57.7 was fixing a Windows page
that would not parse, read the code-behind while deciding a rename, and saw
seven of these on one screen. This closes the general case rather than the
seven.

### How a slotted row is compared

Not by rebuilding the sentence — the shell's holes are not the table's, and
`{en.Seconds:F1}s` is not `{secs}`. The row is split at its slots and the
**literal fragments between them** are compared: a fragment of a row that
appears verbatim inside a string a screen shows is that row being printed in
English.

Fragments shorter than a phrase are dropped. `Built {date}` contributes only
*"Built"*, which is a word that turns up in prose that has nothing to do with
it, and a guard that reports that is one nobody reads — the same lesson as
the eighty-six protocol values. So this misses short rows, deliberately, and
says so.
"""

import pathlib
import re
from . import ratchets

def _repo_root() -> pathlib.Path:
    for d in pathlib.Path(__file__).resolve().parents:
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


REPO = _repo_root()

#: Per shell: its table, the screens it draws, and how a row looks in it.
#:
#: The root is the **view** directory, not the whole shell. `ApiClient` names
#: routes and JSON fields that read like English sentences, and scanning it
#: produced hundreds of matches on words like "Password" that were never on a
#: screen.
SHELLS = {
    "ios": {
        "table": "native/ios/Sources/L10n.swift",
        "views": "native/ios/Sources/Views",
        "exts": (".swift",),
        "row": r'"([\w.]+)":\s*\[\s*"en":\s*"((?:[^"\\]|\\.)*)"',
    },
    "android": {
        "table": "native/android/app/src/main/java/app/jim/guardian/L10n.kt",
        "views": "native/android/app/src/main/java/app/jim/guardian/ui",
        "exts": (".kt",),
        "row": r'"([\w.]+)"\s+to\s+mapOf\(\s*"en"\s+to\s+"((?:[^"\\]|\\.)*)"',
    },
    "windows": {
        "table": "native/windows/L10n.cs",
        "views": "native/windows/Views",
        "exts": (".cs", ".xaml"),
        "row": r'\["([\w.]+)"\]\s*=\s*new\(\)\s*\{\s*\["en"\]\s*=\s*"((?:[^"\\]|\\.)*)"',
    },
}

#: The record. Each row is a literal a shell shows that its own table already
#: translates, kept with the reason it is still there. Ratcheted: the list may
#: shrink and never grow.
#:
#: This product got the guard at 0.57.8, four releases after QRME, and the
#: first run split the same way QRME's did: the words a reader sees became
#: keys, and the words a route matches on are below. Every row here is a
#: **value** — a string this shell posts back or compares against — and
#: translating one turns a working screen into a 422 or a dead branch.
#: Two kinds, and both were read rather than skipped:
#:
#:   * **the sensitivity ladder** — `cautious`, `balanced`, `assertive` — and
#:     the severity ladder's `critical`. These are the values the crash-watch
#:     policy API stores and compares against; the shells hold them in a
#:     `ForEach`/`listOf` and render each through `sensitivityLabel`, which
#:     *does* go to the table. The word beside the tag is already translated;
#:     the tag is the wire.
#:   * **four SwiftUI enum raw values** — `Check-in` and `Presence` in
#:     `CareView.Tab`, `Schedule` in `LifeView`, `Med ID` in `SafetyView`.
#:     The raw value is the stored identity of the selected tab and each enum
#:     already carries a `label(_ lang:)` that reads the row. Renaming one
#:     changes what a restored selection means; it changes nothing a reader
#:     sees.
#:
#:   * **the letters of the amulet** — `ABRACADABRA`, in each shell's
#:     `JimMiniOSMark`. This one is neither a value nor a label; it is the
#:     drawing. The mark is the word arranged in a descending triangle, and
#:     the triangle is the shape the word makes — transliterate the letters
#:     and there is nothing left to look at. The *tab* beside it is
#:     translated and always was: `eng.tab` carries ABRACADABRA verbatim in
#:     the Latin scripts and transliterates into Japanese, Chinese, Hindi and
#:     Arabic, which is the right treatment for a name and the wrong one for
#:     a talisman.
#:
#: The first two kinds are **values** — translating one turns a working screen
#: into a dead branch or a 422. The third is a picture that happens to be made
#: of letters, which is why it needed a paragraph of its own rather than a
#: place in the list above.
RECORDED = {
    ('android', 'ABRACADABRA'),
    ('ios', 'ABRACADABRA'),
    ('windows', 'ABRACADABRA'),
    ('android', 'assertive'),
    ('android', 'balanced'),
    ('android', 'cautious'),
    ('android', 'critical'),
    ('ios', 'Check-in'),
    ('ios', 'Med ID'),
    ('ios', 'Presence'),
    ('ios', 'Schedule'),
    ('ios', 'assertive'),
    ('ios', 'balanced'),
    ('ios', 'cautious'),
    ('ios', 'critical'),
    ('windows', 'assertive'),
    ('windows', 'cautious'),
    ('windows', 'critical'),
}


def _strip_comments(text: str) -> str:
    """Comments are prose about the code, and prose quotes the strings it
    discusses. Reading them was what produced most of the first draft's noise.
    """
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return "\n".join(line for line in text.splitlines()
                     if not line.lstrip().startswith(("//", "///", "*")))


def _rows(spec) -> dict[str, str]:
    """English → key, for whole rows worth checking.

    Skips anything with a slot in it — those go to :func:`_fragments`, which
    compares them a piece at a time — and anything both short and
    single-word: `kind`, `handle`, `basic` and their kin are almost always
    protocol values, and a guard that reports eighty of those is one nobody
    reads.
    """
    text = (REPO / spec["table"]).read_text(encoding="utf-8")
    out = {}
    for key, english in re.findall(spec["row"], text):
        if "{" in english:
            continue
        if " " in english or len(english) >= 8:
            out[english] = key
    return out


#: A slot, in every spelling these three shells write one: `{n}` in a table
#: row and a C# interpolation, `\(x)` in Swift, `${x}` in Kotlin.
_HOLE = re.compile(r'\\?\{[^{}]*\}|\\\([^()]*\)|\$\{[^{}]*\}')


def _fragments(spec) -> dict[str, str]:
    """literal fragment → key, for the rows `_rows` skips.

    A slotted row is not compared whole: the shell's holes are not the
    table's, so `{en.Seconds:F1}s` will never equal `{secs}` and matching on
    the assembled sentence finds nothing. What does survive assembly is the
    text *between* the holes, and that text is the part a reader reads.

    Fragments shorter than a phrase are dropped. `Built {date}` contributes
    only "Built", and a guard that reports every occurrence of a word like
    that is the eighty-six-out-of-eighty-eight guard again.
    """
    text = (REPO / spec["table"]).read_text(encoding="utf-8")
    out = {}
    for key, english in re.findall(spec["row"], text):
        if "{" not in english:
            continue
        for part in _HOLE.split(english):
            part = part.strip(" \u00b7\u2014-:;,.")
            if (" " in part and len(part) >= 6) or len(part) >= 10:
                out.setdefault(part, key)
    return out


def _shown(spec) -> set[tuple[str, str]]:
    """Every string literal these screens contain, with its file.

    Extracted as literals rather than searched for as substrings, and taken
    from anywhere in the literal — including the pieces of an interpolation.
    The first version of this guard only looked at assignments into display
    properties, and so could not see

        Detail = $"{b.Location} · {b.Scans} scan(s)"

    which is the exact line it was written for. It reported the shells clean
    and the injection pass caught it.
    """
    found = set()
    for path in (REPO / spec["views"]).rglob("*"):
        if path.suffix not in spec["exts"]:
            continue
        src = _strip_comments(path.read_text(encoding="utf-8", errors="ignore"))
        for literal in re.findall(r'"((?:[^"\\\n]|\\.)*)"', src):
            found.add((literal.strip(" \u00b7\u2014-"), path.name))
    return found


def _live() -> set[tuple[str, str, str]]:
    out = set()
    for shell, spec in SHELLS.items():
        rows = _rows(spec)
        for literal, filename in _shown(spec):
            if literal in rows:
                out.add((shell, literal, filename))
    return out


#: A localization key, in the one spelling all three tables use: lower-case,
#: dotted, no spaces. `"cw.sensitivity"` is not something a reader sees.
_KEYLIKE = re.compile(r'[a-z][\w]*(?:\.[\w]+)+\Z')


def _display(literal: str) -> str | None:
    """What a reader would actually see of `literal`, or None if nobody sees it.

    Two things had to come out, and both were this check's own defects on its
    first run against the sibling products:

    * **the interpolation holes.** The row is split at its slots, so the shown
      string has to be as well — otherwise the *expression* inside the hole is
      compared as if it were prose, and
      `$"{(int)Math.Round(p.Confidence * 100)}"` matched the row *"Confidence
      {pct}% — earned from…"* on the word `Confidence`, which is a C#
      property here and a heading there.
    * **key names.** `L10n.t("cw.sensitivity", …)` is a literal in the source
      and the fragment *"sensitivity"* is inside it, so asking for a row was
      reported as printing one.

    Two findings, both of them the reader's own, and both in a round whose
    subject is a guard that measured slightly the wrong thing. The lesson has
    not changed: strip what is not prose before comparing prose.
    """
    if _KEYLIKE.match(literal):
        return None
    return _HOLE.sub(" ", literal)


def _live_fragments() -> set[tuple[str, str, str, str]]:
    """(shell, key, fragment, file) for each slotted row a screen spells out.

    Matched as a substring rather than by equality, because the shell's string
    carries the surrounding sentence and the values spliced into it — the
    fragment is what is left of the row after assembly, and :func:`_display`
    is what is left of the screen's string after the same removal.
    """
    out = set()
    for shell, spec in SHELLS.items():
        pieces = _fragments(spec)
        for literal, filename in _shown(spec):
            shown = _display(literal)
            if shown is None:
                continue
            for fragment, key in pieces.items():
                if fragment in shown:
                    out.add((shell, key, fragment, filename))
    return out


def test_no_new_screen_prints_english_it_already_holds_translated():
    """The ratchet. A row translated ten ways and then typed out in English on
    the screen beside it is a translation nobody will ever read."""
    appeared = sorted((s, lit, fn) for s, lit, fn in _live()
                      if (s, lit) not in RECORDED)
    assert not appeared, "\n    ".join(
        [""] + [f"{s}: {fn} shows {lit!r}, which {s}'s own table translates"
                for s, lit, fn in appeared]) + (
        "\n  Use the key, or record it — but recording is ratcheted.")


def test_the_record_has_not_gone_stale():
    """A recorded row that is no longer shown is a note about a line somebody
    already fixed, and it makes the next reader trust the list less."""
    live = {(s, lit) for s, lit, _ in _live()}
    stale = sorted(RECORDED - live)
    assert not stale, "\n    ".join(
        [""] + [f"{s}: {lit!r} is recorded and no longer shown" for s, lit in stale]
    ) + "\n  Strike it from RECORDED."


def test_no_screen_spells_out_a_row_that_has_a_slot_in_it():
    """The half `if "{" in english: continue` skipped for four releases.

    A sentence assembled around a value is the one a screen is most likely to
    hand-build, because building it is what the code is already doing.
    """
    loose = sorted(_live_fragments())
    assert not loose, "\n    ".join(
        [""] + [f"{s}: {fn} spells out {frag!r}, which is {key} in {s}'s "
                f"own table" for s, key, frag, fn in loose]) + (
        "\n  Fill the row instead — L10n.fill/Fill takes the key and the "
        "values.")


def test_the_scan_can_still_see_a_screen():
    """A guard nobody has watched fail is a guard nobody should trust.

    Every shell puts a great many strings on screens, so a scan reporting a
    handful is far more likely to be broken than to be good news — which is
    what a rewrite of one of these regexes would produce.
    """
    for shell, spec in SHELLS.items():
        assert len(_shown(spec)) >= ratchets.floor(f"shell.shown.{shell}"), (
            f"{shell}: the scan found only {len(_shown(spec))} literal(s) on "
            f"any screen — the extractor has stopped matching")
        assert _rows(spec), f"{shell}: no rows parsed out of its table"
        assert len(_fragments(spec)) >= ratchets.floor(f"shell.fragments.{shell}"), (
            f"{shell}: only {len(_fragments(spec))} fragment(s) out of its "
            f"slotted rows — the split has stopped finding slots, and the "
            f"check above would pass on nothing")


def test_a_slotted_row_is_compared_by_its_fragments():
    """The reason this is not an equality test, written out.

    The shell's holes are not the table's. Rebuilding the sentence and
    comparing it finds nothing at all, which is what a green run would have
    meant.
    """
    row = "closest overlap {best}, below the {threshold} threshold for naming anyone"
    parts = [p.strip(" \u00b7\u2014-:;,.") for p in _HOLE.split(row)]
    keep = [p for p in parts if (" " in p and len(p) >= 6) or len(p) >= 10]
    assert keep == ["closest overlap", "below the",
                    "threshold for naming anyone"]
    shown = '$"closest overlap {best}, below the {th} threshold for naming anyone"'
    assert all(f in shown for f in keep)
    assert row not in shown, "the assembled sentences are not equal — that is the point"


def test_a_word_on_its_own_is_not_a_fragment():
    """`Built {date}` contributes only "Built", and reporting every "Built" in
    the sources is the eighty-six-out-of-eighty-eight guard again."""
    parts = [p.strip(" \u00b7\u2014-:;,.") for p in _HOLE.split("Built {date}")]
    assert not [p for p in parts if (" " in p and len(p) >= 6) or len(p) >= 10]


def test_a_key_is_not_something_a_reader_sees():
    """`L10n.t("cw.sensitivity")` is a screen *asking* for a row. Reported as
    printing one, it is a finding about the guard."""
    assert _display("cw.sensitivity") is None
    assert _display("nsig.level.basic") is None
    assert _display("Talking with someone") == "Talking with someone"


def test_the_expression_inside_a_hole_is_not_prose():
    """`{(int)Math.Round(p.Confidence * 100)}` is a C# property, and matching
    a row's heading against it is matching prose against code."""
    assert _display("{(int)Math.Round(p.Confidence * 100)}").strip() == ""
    assert "Confidence" not in _display("{(int)Math.Round(p.Confidence * 100)}")
    kept = _display("closest overlap {best}, below the {th} threshold for naming anyone")
    assert "closest overlap" in kept and "threshold for naming anyone" in kept


def test_every_spelling_of_a_slot_is_recognised(tmp_path):
    """Three shells, three syntaxes. A hole this does not know is a fragment
    that swallows the value name and matches nothing."""
    assert _HOLE.split("a {n} b") == ["a ", " b"]
    assert _HOLE.split("a \\(n) b") == ["a ", " b"]
    assert _HOLE.split("a ${n} b") == ["a ", " b"]
