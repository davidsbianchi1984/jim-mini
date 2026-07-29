"""Every README ends on the rock.

The Matthew 7:24–25 passage closes the root README, and the standing rule
is that it closes *every* README in the repo — the very end, byte-identical
to the root's copy. A rule that lives in someone's memory lasts until the
next README is added; this one lives here instead.
"""

from __future__ import annotations

import pathlib

HEADING = "## Matthew 7:24–25"
SKIP = {".pytest_cache", "node_modules", "dist", "release", ".git"}

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _readmes() -> list[pathlib.Path]:
    return [p for p in ROOT.rglob("README*.md") if not (set(p.parts) & SKIP)]


def test_every_readme_ends_on_the_rock():
    canonical = (ROOT / "README.md").read_text(encoding="utf-8")
    assert HEADING in canonical, "the root README must carry the passage"
    block = canonical[canonical.index(HEADING):].rstrip()
    assert block.endswith("And those with the vision shall enter in.")

    readmes = _readmes()
    assert len(readmes) >= 2, "expected more than just the root README"
    for p in readmes:
        text = p.read_text(encoding="utf-8").rstrip()
        assert text.endswith(block), (
            f"{p.relative_to(ROOT)} must end with the Matthew 7:24–25 "
            "passage, byte-identical to the root README's")
