"""Nothing the console pins to the bottom of the glass may cover the menu.

## The report

    "It seems to be blocking the PDI menus"

A photograph of the PDI beta on a phone: the vault light sitting squarely
over the first three tabs of the bottom bar, taking the taps. A second
photograph, one state along — *"Same thing with the small green circle when
minimized"* — showed the minimized light doing it as a 40px disc.

This console's corner widgets were moved above the tab bar in an earlier
round, after the same complaint about the agent lights and the help bubble.
The behaviour was right here and the question was not asked here, which is
the shape `guard_divergences.txt` exists to catch: a fix that travelled and
a guard that did not. The stylesheet is now read in all three products.

## Why nothing caught it

Both halves were correct on their own. The light is `position: fixed` at
`bottom: 22px`, which on a desktop is empty page margin. The sidebar becomes
a bottom bar under `@media (max-width: 760px)`, which is the ordinary way to
put navigation on a phone. Neither rule knows about the other, and no test
in this suite had ever read the stylesheet — the console's guards all ask
what a screen *says*, and this was a question about where a thing *sits*.

    asked     is every screen wired, translated and reachable
    mattered  can the person's thumb reach the tab under the light

## What this checks

The bar's height is read out of the stylesheet rather than written here, so
the clearance tracks the bar: if somebody makes the tap targets taller, this
recomputes and the light has to move with them. Anything fixed to the bottom
of the viewport must, inside the mobile block, clear that height.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
CSS = REPO / "app" / "src" / "styles.css"

#: The breakpoint at which the sidebar becomes a bottom bar.
_MOBILE_HEAD = "@media (max-width: 760px) {"


def _stylesheet() -> str:
    """The stylesheet with its comments removed.

    Prose is not a selector, and this file's comments contain commas — the
    first draft split a selector list on them and read half a sentence as a
    rule name.
    """
    return re.sub(r"/\*.*?\*/", "", CSS.read_text(encoding="utf-8"), flags=re.S)


def _braced(text: str, head: str) -> str:
    """The body of a `head { … }` block, counting braces rather than
    stopping at the first `}` — a media query is full of nested rules, and
    the first draft of this guard read one of them and called it the block.
    """
    start = text.index(head) + len(head)
    depth, i = 1, start
    while depth:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return text[start:i - 1]


def _mobile_block() -> str:
    """Every block written at the breakpoint, joined.

    A stylesheet may open the same media query more than once — the corner
    widgets in two of these consoles are styled in a block of their own at
    the bottom of the file, on purpose, so that the cascade gives them the
    win. Reading only the first block would measure a rule that a later one
    overrides and call it the answer.
    """
    css = _stylesheet()
    assert _MOBILE_HEAD in css, (
        "the mobile media query is gone from styles.css, so this guard is "
        "reading nothing — find the breakpoint and re-point it")
    blocks, rest = [], css
    while _MOBILE_HEAD in rest:
        body = _braced(rest, _MOBILE_HEAD)
        blocks.append(body)
        rest = rest.split(_MOBILE_HEAD + body + "}", 1)[1]
    return "\n".join(blocks)


def _base() -> str:
    """The stylesheet with its media queries removed, so a rule read here is
    the one that applies on a desktop."""
    css = _stylesheet()
    while _MOBILE_HEAD in css:
        body = _braced(css, _MOBILE_HEAD)
        css = css.replace(_MOBILE_HEAD + body + "}", "", 1)
    return re.sub(r"@media[^{]*\{", "", css)


def _rule(block: str, selector: str) -> str | None:
    """Every declaration written for one selector, or None when absent.

    A selector may be written more than once — the light's mobile rules are
    a shared `bottom` and its own `max-width` — so the readings are merged
    rather than taking the first and calling the rest absent.
    """
    found = [m.group(2) for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", block)
             if selector in [s.strip() for s in m.group(1).split(",")]]
    return " ".join(found) if found else None


def _declared() -> dict[str, str]:
    """What `:root` declares, so a value written as a variable can be read.

    The clearance is no longer a literal: the bar measures itself and
    publishes `--tabbar-h`, and `:root` declares the height a browser
    without a ResizeObserver gets. That declaration is the floor this guard
    can check — the measured value is only ever the true height, and the
    true height is what the rule is trying to clear.
    """
    root = re.search(r":root\s*\{([^}]*)\}", _stylesheet())
    body = root.group(1) if root else ""
    return dict(re.findall(r"(--[a-z0-9-]+)\s*:\s*([^;]+);", body))


def _resolve(value: str) -> str:
    """`var(--x)` replaced by what `:root` says, or by its own fallback."""
    declared = _declared()
    return re.sub(
        r"var\((--[a-z0-9-]+)(?:,\s*([^()]*))?\)",
        lambda m: declared.get(m.group(1), m.group(2) or ""), value)


def _px(declarations: str, prop: str) -> float | None:
    m = re.search(rf"\b{prop}:\s*([^;]+);", declarations)
    if not m:
        return None
    value = _resolve(m.group(1))
    # `calc(var(--tabbar-h) + 12px + env(safe-area-inset-bottom))` — every
    # term adds, and the safe-area term is a phone's home indicator, so the
    # px terms summed are the floor of what the rule reserves. Reading only
    # the first px here read the 12px gap as the whole clearance and called
    # a rule that clears the bar by 88px a lid on the menu.
    if " - " not in value and "min(" not in value and "max(" not in value:
        terms = re.findall(r"(\d+(?:\.\d+)?)px", value)
        if terms:
            return sum(float(t) for t in terms)
    px = re.search(r"(\d+(?:\.\d+)?)px", value)
    return float(px.group(1)) if px else None


def _bar_height() -> float:
    """What the bottom bar occupies, from the stylesheet's own numbers."""
    block = _mobile_block()
    item = _rule(block, ".nav-item")
    sidebar = _rule(block, ".sidebar")
    assert item and sidebar, (
        "the bottom bar's rules have been renamed — this guard measures the "
        "bar out of `.sidebar` and `.nav-item`, and cannot see them")
    tap = _px(item, "min-height")
    assert tap, ".nav-item no longer declares a min-height to measure"
    pad = re.search(r"padding:\s*(\d+(?:\.\d+)?)px", sidebar)
    assert pad, ".sidebar no longer declares padding to measure"
    # Padding is shorthand: the first number is the top, and the bottom is
    # the same number plus the safe-area inset.
    return tap + 2 * float(pad.group(1))


#: ## The third shape
#:
#: The widgets were then folded into one thing, as QRME's were before them.
#: Four corners — the help bubble, the Guardian's lights, the task window
#: and the footsteps chip — became one stack of tabs on the right edge, the
#: *edge dock*, after the owner read the console and said JIM "still has all
#: the circle running lights, the help tabs and the count ... needs to be
#: tabs off to the side, just like QRME".
#:
#: The question survives the redesign in a new shape. Nothing pinned to the
#: glass may sit *over* the menu, which is a question of stacking rather
#: than of height; the tabs are tap targets, so they must be thumb-sized on
#: a phone; and the panels must stay inside the glass rather than push the
#: page sideways. The names below are kept although the corners are gone,
#: deliberately: the three products carry these guards by name, and a
#: renamed guard reads as a missing one in the divergence ledger.
#:
#: Everything the shell pins to the glass. A new one is a new row here,
#: which is the point: the question is asked of the class of thing, not of
#: the one that was reported.
BOTTOM_FIXED = (".edge-dock", ".edge-panel")


def test_the_stylesheet_still_pins_these_to_the_bottom():
    """The guard on the guard. If the dock stopped being fixed — or was
    renamed — every assertion below would pass on an empty reading."""
    css = _base()
    rule = _rule(css, ".edge-dock")
    assert rule, ".edge-dock is not in styles.css any more"
    assert "position: fixed" in rule and re.search(r"\bright:\s*0", rule), (
        ".edge-dock is no longer fixed to the right edge of the viewport — "
        "either this list is stale or the dock moved, and both want a "
        "person to look")
    panel = _rule(css, ".edge-panel")
    assert panel and "position: absolute" in panel, (
        ".edge-panel no longer hangs off the dock — where it opens is "
        "somebody's decision again")


@pytest.mark.parametrize("selector", BOTTOM_FIXED)
def test_nothing_fixed_to_the_bottom_covers_the_bar(selector):
    """The defect, in the menu's current shape.

    A pinned widget can no longer sit *beside* the navigation — it can only
    sit *over* it, by stacking higher. Each therefore has to stay below the
    bar's own level, wherever it declares one; a widget declaring none
    stacks at auto, which the fixed bar already beats.

    The name is kept although the widgets moved, deliberately: the three
    products carry this guard by name. What is asked is the same question
    the field report asked — can the person's thumb reach the menu under
    the light.
    """
    css = _base() if selector == ".edge-dock" else _stylesheet()
    rule = _rule(css, selector)
    assert rule, f"{selector} is not in styles.css any more"

    if selector != ".edge-dock":
        return  # the panel hangs off the dock; the dock is what is pinned

    # QRME could answer this in CSS because its navigation became a drawer
    # and the question turned into stacking. Here the sidebar is still the
    # bottom tab bar, so the original question stands in its original form —
    # and it cannot be answered in the stylesheet, because the dock's top is
    # a percentage a person drags and the bar is as tall as its labels in
    # whichever of ten languages they read. The dock measures both and
    # clamps itself; this reads that it still does.
    src = (REPO / "app" / "src" / "EdgeDock.tsx").read_text(encoding="utf-8")
    assert "--tabbar-h" in src, (
        "the dock no longer reads the bar's published height, so how far it "
        "may be dragged is a guess again — which is the defect this guard "
        'was written for: "It seems to be blocking the PDI menus"')
    assert "offsetHeight" in src, (
        "the dock no longer measures its own stack, so a third tab makes it "
        "taller than the clamp believes and the bottom tab is over the bar")
    assert re.search(r'addEventListener\(\s*"resize"', src), (
        "the clamp is measured once and never again — a phone turned "
        "sideways, or a label that wraps, moves the bar under a dock that "
        "does not know it moved")


#: What the minimized light may occupy on a phone, and how solid it may be.
#: Both numbers are QRME's, which arrived at them after the same report
#: about the same widget.
DOT_MAX_PX, DOT_MAX_OPACITY = 24.0, 0.9

#: What a thumb has to be able to hit. The blanket
#: `button { min-height: 44px }` in the phone block is where this
#: number comes from, and the dot is a button like any other.
TAP_MIN_PX = 44.0


def test_the_minimized_light_is_a_dot_and_not_a_disc():
    """The second half of the same field report, asked of the light's new
    home.

    The first photograph showed the light covering the tabs; lifting it
    answered that. The next one — *"Same thing with the small green circle
    when minimized"* — showed the minimized state, and it was not small: a
    40px solid disc with a heavy shadow, sitting over the screen's own
    content at full strength.

        asked     does the minimized light clear the menu
        mattered  is the minimized light small enough to be minimized

    Minimizing is the reader saying *get out of the way*. The dock answers
    that differently and better: there is no minimized state to get wrong,
    because the closed state *is* the tab. So what this asks now is that
    the tab is a real tap target — it loses its word on a phone and keeps
    only its glyph, which is exactly the control a thumb misses — and that
    the disc has not come back.

    `min-height` beats `height`, and the base rule sets both to 36, so both
    have to be raised in the phone block. Reading only one of them is how
    the first version of this guard passed on an ellipse for two releases.
    """
    rule = _rule(_mobile_block(), ".edge-tab")
    assert rule, (
        ".edge-tab has no rule at the mobile breakpoint, so it keeps its "
        "desktop size on a phone")
    for prop in ("height", "min-height"):
        size = _px(rule, prop)
        assert size is not None and size >= TAP_MIN_PX, (
            f"a dock tab is {size}px {prop} on a phone, under the "
            f"{TAP_MIN_PX}px every other control here gets")

    css = _stylesheet()
    for gone in (".wl-dot-face", ".wl-min", ".uw-min"):
        assert gone not in css, (
            f"{gone} is back in the stylesheet — the minimized disc and the "
            "buttons that produced it were retired with the corners")

    src = (REPO / "app" / "src" / "GuardianLights.tsx").read_text(encoding="utf-8")
    assert "🚦" in src, "the lights' tab lost its stoplight glyph"
    assert "borderColor: COLORS[tone]" in src, (
        "the tab no longer wears the worst light's colour — a stoplight "
        "that is the same on a red day and a green one says nothing")


def test_the_light_stays_inside_the_glass():
    """A panel wider than the phone pushes the page sideways, which is the
    other way a fixed element takes a screen over."""
    rule = _rule(_base(), ".help-panel")
    assert rule and ("max-width" in rule or "width: min(" in rule), (
        "the help panel has no width limit, so on a narrow phone it can "
        "widen past the viewport and push the page sideways")
