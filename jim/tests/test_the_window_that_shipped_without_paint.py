"""A pinned widget rendered nine class names that no stylesheet knew.

The task window shipped, its tests passed, its rows polled — and a field
screenshot read "sensingwrist": every `uw-*` class it renders existed in
no CSS rule at all, so the spans ran together bare and the "pinned"
window sprawled unstyled across the page foot. The suite checked the
window's data, its doors and its words, and never that it had paint.

    asked     does the widget render
    mattered  does anything style what it renders

The same sweep found a second ghost: `var(--muted)` appeared in seven
rules and was defined in none, so seven "muted" things silently inherited
full-strength color. Both defects are one family — a name used somewhere
and defined nowhere — and this file pins the family, not the instances:
every class the two pinned widgets render must have a rule, and every CSS
variable the stylesheet reads must be a variable it defines.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CSS = (REPO / "app/src/styles.css").read_text(encoding="utf-8")


def _classes(rel: str) -> set[str]:
    """Every literal class token a component's className strings carry."""
    src = (REPO / rel).read_text(encoding="utf-8")
    out: set[str] = set()
    # The attribute's own value only — a plain string or one braced
    # expression. The first draft read to the end of the line and collected
    # `role="status"` as a class named status.
    for m in re.finditer(r'className=(?:"([^"]*)"|\{([^}]*)\})', src):
        block = m.group(1) if m.group(1) is not None else m.group(2)
        for lit in re.findall(r'"([^"]*)"', block) or [block]:
            out |= {w for w in lit.split()
                    if re.fullmatch(r"[a-z][a-z0-9-]*", w)}
    return out


def test_the_pinned_widgets_are_painted():
    for rel in ("app/src/Underway.tsx", "app/src/GuardianLights.tsx"):
        missing = sorted(c for c in _classes(rel)
                         if not re.search(rf"\.{re.escape(c)}\b", CSS))
        assert not missing, (
            f"{rel} renders classes no stylesheet rule styles:\n    "
            + "\n    ".join(missing)
            + "\n  This is how the task window shipped as bare spans "
              "reading \"sensingwrist\".")


def test_every_variable_the_stylesheet_reads_is_one_it_defines():
    used = set(re.findall(r"var\((--[a-z0-9-]+)[),]", CSS))
    defined = set(re.findall(r"(--[a-z0-9-]+)\s*:", CSS))
    ghosts = sorted(used - defined)
    assert not ghosts, (
        "CSS variables read and never defined — the browser falls back "
        "silently, which is how seven muted things rendered at full "
        "strength:\n    " + "\n    ".join(ghosts))
