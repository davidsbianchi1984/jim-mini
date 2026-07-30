"""A surface the user can see must have a drawing, or be admitted not to.

`test_docs_gallery.py` checks screens against the README in both directions —
a reference with no file, a file with no reference, a gap in the numbering.
All of it starts from the screens. None of it asks the opposite question:
*does this surface have a screen at all?* So a feature can ship with nothing
drawn, nothing taught, and nothing for the in-app helper to point at, and the
suite stays green.

That is not hypothetical. It has happened three times. Voice cloning, the
recoverable watermark and the chat role picker each shipped with no screen and
stayed that way for two versions, needing a dedicated catch-up round. Then the
error-reporting card and its first-run notice went out in 0.19.0 exactly the
same way — while the release notes described the feature at length.

The shape of the flaw is the one this suite has found twice elsewhere: a guard
that only walks the relation in the direction where the answers already exist.
The doorless audit was the same (a route with no client door), and so was the
redaction check that read a shrinking snapshot and would have gone vacuous the
day it emptied.

`ui_screens.txt` is the missing direction, and the test that matters is the
first one below: a component nobody has classified fails, immediately, in the
round that introduces it.
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
# Beside this file rather than under a named `tests/`: the suite lives at
# `tests/` in one repo and `{pkg}/tests/` in the other two, exactly as
# clientpaths.py and the redaction guard already have to account for.
MANIFEST = Path(__file__).resolve().parent / "ui_screens.txt"
SRC = REPO / "app" / "src"

# Top-level .tsx files that are not user-facing surfaces. Named individually
# rather than pattern-matched, so adding one is a decision somebody makes here
# rather than a filename that quietly slips past.
NOT_A_SURFACE = {
    "main",         # the entry point; renders App and nothing of its own
    "App",          # the frame — nav and routing, drawn as part of every screen
    "store",        # a context provider, no markup
    "api",          # not a component at all
    "l10n",         # not a component at all
    "Help",         # the assistant dock, drawn inside the screens it floats over
    "WatchLights",  # the always-on widget; its own gallery lives in the watch faces
    "VersionGuard", # a failure banner, deliberately not part of the tour
}


def _surfaces() -> set[str]:
    """Every component a person can look at."""
    found = {p.stem for p in (SRC / "screens").glob("*.tsx")}
    found |= {p.stem for p in SRC.glob("*.tsx") if p.stem not in NOT_A_SURFACE}
    return found


def _manifest() -> dict[str, str]:
    rows = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if not line:
            continue
        name, _, status = line.partition(" ")
        rows[name.strip()] = status.strip()
    return rows


def test_every_surface_is_accounted_for():
    """The one that would have caught 0.19.0.

    A component nobody has classified is a component nobody has decided about.
    It fails here rather than being noticed two versions later.
    """
    listed, actual = set(_manifest()), _surfaces()
    unlisted = sorted(actual - listed)
    assert not unlisted, (
        f"these surfaces are in the console and not in ui_screens.txt: "
        f"{unlisted}\nGive each one a screen number, or the word 'undrawn' if "
        "it genuinely has no drawing yet — but note that 'undrawn' is "
        "ratcheted, so adding one there fails the next test until the backlog "
        "is paid down elsewhere. That friction is deliberate."
    )


def test_the_manifest_has_not_gone_stale():
    """The other direction: a component that was deleted or renamed leaves an
    entry behind, and a manifest full of ghosts is one nobody trusts."""
    listed, actual = set(_manifest()), _surfaces()
    ghosts = sorted(listed - actual)
    assert not ghosts, (
        f"ui_screens.txt names surfaces that no longer exist: {ghosts}")


def test_every_declared_screen_exists():
    """A mapping that points at nothing is worse than no mapping, because it
    reads as a promise that the surface was drawn."""
    on_disk = {int(m.group(1))
               for p in (REPO / "docs" / "screens").glob("*.svg")
               if (m := re.match(r"(\d+)-", p.name))}
    broken = {}
    for name, status in _manifest().items():
        if status in ("undrawn", "unaudited"):
            continue
        missing = [n for n in status.split(",") if int(n) not in on_disk]
        if missing:
            broken[name] = missing
    assert not broken, f"these entries name screens that do not exist: {broken}"


def _ceilings() -> dict[str, int]:
    """The ratchet's high-water marks, declared by each repo's own manifest.

    Not hardcoded here: this file is byte-identical in three repositories with
    different backlogs, and a single number would be the largest of the three
    — leaving the other two free to grow into the slack, which is the opposite
    of a ratchet.
    """
    text = MANIFEST.read_text(encoding="utf-8")
    match = re.search(r"^#\s*ceiling:\s*undrawn=(\d+)\s+unaudited=(\d+)\s*$",
                      text, re.M)
    assert match, ("ui_screens.txt has no `# ceiling:` line — without one "
                   "nothing bounds the backlog and this whole file is "
                   "decoration")
    return {"undrawn": int(match.group(1)), "unaudited": int(match.group(2))}


def test_the_undrawn_backlog_does_not_grow():
    """The ratchet, and the reason the first test has teeth.

    Without this, classifying a new surface as `undrawn` would silence the
    first test while changing nothing. With it, shipping a surface without a
    drawing costs something — you either draw it, or you draw something else
    first and lower the ceiling.

    Raising the ceiling is possible, deliberately: it is one line in a diff
    that says plainly that the backlog grew, which is the conversation worth
    having rather than one a test can win on its own.
    """
    ceilings = _ceilings()
    for status, limit in ceilings.items():
        count = sum(1 for v in _manifest().values() if v == status)
        assert count <= limit, (
            f"{count} surfaces are '{status}', above the ceiling of {limit} "
            f"declared in ui_screens.txt. Draw one, or raise the ceiling and "
            "say why.")


def test_the_ceiling_is_not_left_slack_after_the_backlog_falls():
    """A ceiling that stays high after the backlog drops is a ratchet that
    stopped ratcheting — it quietly re-opens room to grow back."""
    ceilings = _ceilings()
    for status, limit in ceilings.items():
        count = sum(1 for v in _manifest().values() if v == status)
        assert limit == count, (
            f"the '{status}' ceiling is {limit} but only {count} remain — "
            f"lower it to {count} so the ground gained is kept")


def test_the_statuses_are_ones_this_file_defines():
    """A typo'd status would otherwise read as 'not undrawn' and pass."""
    allowed = re.compile(r"^(undrawn|unaudited|\d+(,\d+)*)$")
    bad = {n: s for n, s in _manifest().items() if not allowed.match(s)}
    assert not bad, (
        f"unrecognised statuses in ui_screens.txt: {bad} — expected a "
        "comma-separated list of screen numbers, 'undrawn', or 'unaudited'")
