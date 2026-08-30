"""A media query that a later rule overrules is a rule nobody ever runs.

## The defect, three times

Three separate rounds shipped the same mistake, in three different
products, and no test in this estate said a word about any of them:

    .help-fab      (JIM-mini)  lifted clear of the tab bar in an @media
                               block declared two hundred lines above the
                               base rule it was overriding
    .vault-light   (PDI)       the same, under a comment explaining the fix
    .talk-panel    (QRME)      `max-height: none` on a short screen,
                               defeated by a second base `max-height: 60vh`
                               nine hundred lines further down

In each one somebody wrote the override, read it back, and had every
reason to believe it worked. The browser disagreed for a reason that is
one sentence long and easy to forget: **a media query adds no
specificity.** `@media (max-height: 600px) { .talk-panel { ... } }` and
`.talk-panel { ... }` are both `(0, 1, 0)`, so between them the later
source order wins — even though one is a narrow, conditional, obviously
more specific-sounding thing than the other.

    asked     is there a rule that overrides it
    mattered  is that the rule the browser uses

## What this checks, and what it deliberately does not

For every declaration inside an at-rule block, this looks for a
declaration of the *same property* on a *textually identical selector* in
an unconditioned rule *later in the file*. Identical selector text means
identical specificity by construction, so a hit is never a specificity
judgement call — it is always the plain source-order rule, and always a
dead declaration.

It does not compare different selectors. `.talk-panel` inside a media
block and `.chat-rail-dock .talk-panel` after it is a real and correct
pattern — the second is more specific and is *supposed* to win — and a
checker that guessed at specificity across differing selectors would
report those and be ignored within a week.

A declaration marked `!important` inside the at-rule is skipped: it beats
a later plain declaration, so it is not dead.
"""

from __future__ import annotations

import pathlib
import re

HERE = pathlib.Path(__file__).resolve()
CSS = HERE.parent.parent.parent / "app" / "src" / "styles.css"

_COMMENTS = re.compile(r"/\*.*?\*/", re.S)


def _rules(text: str):
    """Every rule in the sheet, as (selector, properties, at_rule, order).

    A hand-rolled walk rather than a CSS library: the estate's suites take
    no dependency a reader cannot install from the standard library, and
    the shape needed here is only "which declarations, under which
    selector, inside or outside an at-rule, in what order".
    """
    text = _COMMENTS.sub("", text)
    out, buf, stack, order = [], [], [], 0
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "{":
            head = "".join(buf).strip()
            buf = []
            stack.append(head)
            i += 1
            continue
        if ch == "}":
            head = stack.pop() if stack else ""
            body = "".join(buf)
            buf = []
            if head and not head.startswith("@"):
                props = []
                for piece in body.split(";"):
                    if ":" not in piece:
                        continue
                    name = piece.split(":", 1)[0].strip().lower()
                    if name and not name.startswith("-"):
                        props.append((name, "!important" in piece.lower()))
                if props:
                    at = next((s for s in stack if s.startswith("@")), None)
                    out.append((_tidy(head), props, at, order))
                    order += 1
            i += 1
            continue
        buf.append(ch)
        i += 1
    return out


def _tidy(selector: str) -> str:
    """One spelling per selector, so identical selectors compare equal."""
    parts = [" ".join(p.split()) for p in selector.split(",")]
    return ", ".join(sorted(p for p in parts if p))


def dead_declarations(text: str) -> list[str]:
    """Every at-rule declaration a later identical selector overrules."""
    rules = _rules(text)
    # Where each selector's *unconditioned* declarations of a property sit.
    plain: dict[tuple[str, str], list[int]] = {}
    for selector, props, at, order in rules:
        if at is not None:
            continue
        for name, _important in props:
            plain.setdefault((selector, name), []).append(order)

    dead = []
    for selector, props, at, order in rules:
        if at is None or not at.startswith("@media"):
            continue
        for name, important in props:
            if important:
                continue
            later = [o for o in plain.get((selector, name), []) if o > order]
            if later:
                dead.append(f"{at.strip()} → {selector} {{ {name} }} "
                            f"is overruled by a later plain "
                            f"`{selector} {{ {name} }}`")

    return dead


def test_no_media_rule_is_defeated_by_a_later_plain_rule():
    dead = dead_declarations(CSS.read_text(encoding="utf-8"))
    assert not dead, (
        "these media-query declarations never apply — a media query adds no "
        "specificity, so a later rule on the identical selector wins on "
        "source order alone:\n  " + "\n  ".join(dead)
        + "\nMove the plain rule above the media block, or fold it into the "
          "base rule the media block is meant to override.")


#: The defect, reduced to the smallest sheet that still has it: an override
#: written inside a media query, and the same selector and property set
#: again afterwards without one.
DEFECTIVE = """
.thing { max-height: 60vh; }
@media (max-height: 600px) {
  .thing { max-height: none; }
}
.thing { max-height: 60vh; overflow-y: auto; }
"""

#: The same sheet with the ordering that works — and nothing else changed.
CORRECTED = """
.thing { max-height: 60vh; overflow-y: auto; }
@media (max-height: 600px) {
  .thing { max-height: none; }
}
"""

#: Not the defect: a *more specific* selector is supposed to win, and a
#: checker that reported these would be switched off inside a week.
INNOCENT = """
.thing { max-height: 60vh; }
@media (max-height: 600px) {
  .thing { max-height: none; }
}
.dock .thing { max-height: 40vh; }
.thing { padding: 4px; }
"""


def test_the_checker_fails_on_a_sheet_that_has_the_defect():
    """The guard above passes on three products. That is either because the
    defect is gone or because the checker stopped working, and those look
    identical from outside. This is the difference.

    Two of this estate's proof tests once passed vacuously, so a checker
    whose only evidence is a green run is not evidence."""
    found = dead_declarations(DEFECTIVE)
    assert len(found) == 1, found
    assert ".thing" in found[0] and "max-height" in found[0]


def test_the_checker_passes_the_same_sheet_reordered():
    assert dead_declarations(CORRECTED) == []


def test_a_more_specific_later_selector_is_not_reported():
    """`.dock .thing` beating `.thing` is the cascade working. Only an
    identical selector — identical specificity by construction — can be
    defeated on source order alone, so only that is reported."""
    assert dead_declarations(INNOCENT) == []
