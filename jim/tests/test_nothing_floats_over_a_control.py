"""Two things that float, sitting on two things a person has to press.

Both were found by looking at a photograph, which is the whole problem.

    asked     does the console render
    mattered  can a person reach every control on it

## What was wrong

On a phone the sidebar becomes the bottom tab bar, and everything that
floats — the help button, the Guardian lights, the task window — was told
to sit `76px` up from the bottom to stay off it. That number is a guess
about how tall the bar is, and the bar is as tall as its labels. *Live
Monitoring* and *Your Baseline* wrap to two lines and push it past 76, so
the help button came to rest on top of a tab. Every label here is
translated into ten languages, and the ones with longer words wrap sooner.

The task window was worse: it had no phone rule at all, kept its desktop
`bottom: 84px`, and floated in the middle of the screen — over the move
checkboxes on the Hands screen, which are the controls that card exists to
offer. Floating over everything is what that window is *for*; floating
over a form control is not.

## The rule that was right and never ran

The first version of this file checked that a phone rule *exists* for each
float. It passed on the broken stylesheet, because the rule did exist — in
the layout media block near the top, two hundred lines above the base
`.help-fab { bottom: 22px }`. Same specificity, later wins. The lift had
never once applied, and the comment above it explained why it had been
added.

    asked     is there a rule that lifts it
    mattered  is that the rule the browser uses

So the check is about **order**, not presence. A phone override that is
declared before the base rule it means to override is not a fix; it is a
comment that reads like one, which is worse than nothing because the next
person believes it.

## Why this file rather than three fixes

The fixes are a few lines of CSS. The reason they were needed is that
nothing here can see a rectangle, and nothing here read the cascade. Every
guard in this suite reads source for what it says; this one reads it for
what wins.

It is deliberately narrow. It does not judge whether the console is well
laid out — a guard that tried would fail on every deliberate overlay (the
takeover screens, the modal, the room's own chrome) and be switched off
within a month. It holds one line: a float clears the bar by measuring it,
with a rule that actually applies.
"""

from __future__ import annotations

import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
CSS = REPO / "app" / "src" / "styles.css"
APP = REPO / "app" / "src" / "App.tsx"

#: The floating things, by class. Each is `position: fixed`, and each has
#: to clear the bottom bar on a phone.
FLOATS = (".help-fab", ".help-panel", ".watch-lights", ".wl-dot",
          ".underway", ".uw-dot")


def _blocks() -> list[tuple[int, str]]:
    """Every `max-width: 760px` block, with where in the file it starts."""
    text = CSS.read_text(encoding="utf-8")
    out, at = [], 0
    while True:
        start = text.find("@media (max-width: 760px) {", at)
        if start < 0:
            return out
        depth, i = 0, start
        while i < len(text):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        out.append((start, text[start:i + 1]))
        at = i + 1


def _winning_rule(name: str) -> tuple[int, str]:
    """The phone rule for `name` that the browser actually uses: the last
    one declared, since every rule here carries the same specificity."""
    found = [(at, block) for at, block in _blocks() if name + " " in block
             or name + "," in block or name + "\n" in block]
    assert found, f"no phone rule for {name} at all"
    at, block = found[-1]
    rule = block[block.index(name):]
    return at, rule[:rule.index("}")]


def _base_at(name: str) -> int:
    """Where the desktop rule for `name` is declared."""
    text = CSS.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith(name + " {") or line.startswith(name + ","):
            return text.index(line)
    raise AssertionError(f"no base rule for {name}")


def _phone_block() -> str:
    """Every phone block joined — for the presence checks below."""
    return "\n".join(block for _, block in _blocks())


def test_every_floating_thing_clears_the_bar_on_a_phone():
    """A float with no phone rule keeps its desktop offset, which is where
    the task window was: `bottom: 84px`, in the middle of a phone screen,
    on top of the Hands screen's checkboxes."""
    block = _phone_block()
    adrift = [name for name in FLOATS if name not in block]
    assert not adrift, (
        f"{len(adrift)} floating element(s) have no phone rule and keep "
        f"their desktop offset: {adrift}. On a phone the bottom of the "
        "screen is the tab bar, so a float placed against the bottom on a "
        "desktop is placed against the menu here.")


def test_the_phone_rule_is_declared_after_the_rule_it_overrides():
    """The one that would have caught it.

    `.help-fab` had a phone rule lifting it clear of the tab bar, and the
    base `bottom: 22px` was declared two hundred lines later. Same
    specificity, later wins, so the lift never applied — while the comment
    above it explained why it had been added.
    """
    late = []
    for name in FLOATS:
        if name in (".help-panel",):        # no desktop rule of its own
            continue
        try:
            base = _base_at(name)
        except AssertionError:
            continue
        at, _ = _winning_rule(name)
        if at < base:
            late.append(f"{name} (phone rule at {at}, base at {base})")
    assert not late, (
        "these phone rules are declared BEFORE the rule they override, so "
        "the browser uses the desktop one and the override does nothing:\n"
        "    " + "\n    ".join(late)
        + "\n  Same specificity means later wins. Move them below the base "
          "rules — a rule that cannot win is a comment that reads like a fix.")


def test_the_clearance_is_measured_rather_than_guessed():
    """`76px` was a guess about the bar's height. The bar is as tall as its
    labels, and its labels are translated into ten languages."""
    for name in FLOATS:
        _, rule = _winning_rule(name)
        assert "--tabbar-h" in rule, (
            f"{name} clears the bar by a hard-coded number rather than by "
            "`--tabbar-h`. That number is a guess about how tall the bar "
            "is; the bar is as tall as its labels, and a language with "
            "longer words wraps them sooner.")


def test_the_bar_actually_publishes_its_height():
    """The custom property is only worth reading if something writes it. A
    stylesheet full of `var(--tabbar-h, 76px)` with nothing setting it is
    the same hard-coded 76 with more steps."""
    app = APP.read_text(encoding="utf-8")
    assert "--tabbar-h" in app, (
        "nothing sets --tabbar-h, so every float silently falls back to "
        "the guess this round replaced")
    assert "ResizeObserver" in app, (
        "the height is set once rather than observed — the bar's height "
        "changes when the language changes and when the viewport turns")
    assert re.search(r"ref=\{bar\}", app), (
        "the observer has nothing to watch: the sidebar carries no ref")


def test_the_fallback_is_the_number_it_replaced():
    """A browser with no ResizeObserver is exactly the case the old guess
    was written for, so that is what it falls back to — not zero, which
    would drop every float onto the bar."""
    block = _phone_block()
    assert "var(--tabbar-h, 76px)" in block, (
        "the fallback is missing or different — without one, a browser "
        "that cannot observe the bar puts the help button on the menu")
