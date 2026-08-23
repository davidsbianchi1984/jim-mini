"""Every released version is a link, and `[Unreleased]` points somewhere.

A Keep a Changelog heading is a *reference* link — `## [1.5.0]` renders as
the literal text `[1.5.0]` unless a definition exists at the bottom of the
file. Nothing in a build complains: the file parses, the page renders, and
the damage sits hundreds of lines away from the heading that caused it.

    asked     does the changelog have an entry for this version
    mattered  can a reader get from the entry to what changed

`docs/releasing.md` has warned about this step for a long time — *this is
the step that gets missed, because nothing complains* — and being warned
was not enough. When this guard was written, **170 of the 256 headings in
this file had no definition**, in all three products at once: every version
from 0.20.0 to 0.68.0 and every one from 1.0.0 to 1.5.0. `[Unreleased]`
had no definition at all, in any of the three.

A warning in prose is a thing a person has to remember. This is the same
sentence in a form that fails the suite.
"""

import re
from pathlib import Path


def _repo() -> Path:
    for d in [Path(__file__).resolve()] + list(Path(__file__).resolve().parents):
        if (d / "pyproject.toml").exists():
            return d
    raise RuntimeError("no pyproject.toml above this test")


CHANGELOG = _repo() / "CHANGELOG.md"


def _text() -> str:
    return CHANGELOG.read_text(encoding="utf-8")


def test_every_released_heading_has_a_link_definition():
    """A version somebody can read about is a version they can click."""
    s = _text()
    heads = re.findall(r"^## \[([0-9][0-9.]*)\]", s, re.M)
    assert heads, "no version headings found — the parse is wrong, not the file"
    defined = set(re.findall(r"^\[([0-9][0-9.]*)\]:", s, re.M))
    missing = [h for h in heads if h not in defined]
    assert not missing, (
        f"{len(missing)} of {len(heads)} version headings render as literal "
        f"text for want of a link definition at the bottom of CHANGELOG.md: "
        f"{missing[:12]}{' …' if len(missing) > 12 else ''}")


def test_unreleased_points_at_the_newest_release():
    """`[Unreleased]` diffs against the version above it, not a tag three
    releases old — the failure this file's own history is made of."""
    s = _text()
    m = re.search(r"^\[Unreleased\]: (\S+)$", s, re.M)
    assert m, "[Unreleased] has no link definition"
    newest = re.search(r"^## \[([0-9][0-9.]*)\]", s, re.M).group(1)
    assert m.group(1).endswith(f"app-v{newest}...HEAD"), (
        f"[Unreleased] compares against {m.group(1)!r}, but the newest "
        f"released version in this file is {newest}")


def test_no_definition_is_written_for_a_version_with_no_entry():
    """The other direction: a definition with no heading is a link to a
    release this changelog never describes."""
    s = _text()
    heads = set(re.findall(r"^## \[([0-9][0-9.]*)\]", s, re.M))
    orphans = [d for d in re.findall(r"^\[([0-9][0-9.]*)\]:", s, re.M)
               if d not in heads]
    assert not orphans, f"link definitions with no changelog entry: {orphans}"
