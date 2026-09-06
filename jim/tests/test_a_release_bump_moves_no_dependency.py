"""A release bump moves the version and nothing else.

Cutting a release means changing one number in three places:
`pyproject.toml`, `app/package.json`, and `app/package-lock.json`. The
lockfile is the one that bites. It carries the project's own version
twice — at the top, and inside `packages[""]` — and it also carries the
resolved version of every dependency in the tree. A blind substitution of
the old number for the new one cannot tell those apart.

## What this found

3.2.0 shipped with `ejs` rewritten from `^3.1.10` to `^3.2.0`, because the
project itself had been at 3.1.10. There is no `ejs@3.2.0`. Every image
build died at `npm ci` with a 404 from the registry, on all three products
at once, and the tag was already published by the time anything ran.

    asked     is the app at the new version
    mattered  is every dependency still at a version that exists

## The shape of this guard

The lockfile is hashed with the project's own two version fields masked
out. A release bump touches only those two, so the fingerprint does not
move when the app's version does — and anything else that changes moves
it. The recorded fingerprint lives in `lockfile_dependencies.txt`, so
changing a dependency on purpose is one deliberate line in a file that
says what moved, and changing one by accident during a version cut is a
red suite before the tag exists.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCK = ROOT / "app" / "package-lock.json"
RECORD = Path(__file__).with_name("lockfile_dependencies.txt")

# Any constant will do. It only has to be the same one every release.
MASK = "the-project-version-lives-in-pyproject"


def _masked(doc: dict) -> dict:
    """The lockfile with the project's own two version fields blanked."""
    doc = copy.deepcopy(doc)
    doc["version"] = MASK
    doc["packages"][""]["version"] = MASK
    return doc


def _hash(doc: dict) -> str:
    canonical = json.dumps(doc, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _fingerprint(doc: dict) -> str:
    return _hash(_masked(doc))


def _lockfile() -> dict:
    return json.loads(LOCK.read_text(encoding="utf-8"))


def _recorded() -> str:
    for line in RECORD.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("SHA256"):
            return stripped.split()[1]
    raise AssertionError(f"{RECORD.name} records no SHA256 line")


def test_a_release_bump_moves_no_dependency():
    """The lockfile's dependencies are the ones this repo wrote down."""
    seen = _fingerprint(_lockfile())
    assert seen == _recorded(), (
        "app/package-lock.json's dependencies are not the recorded ones.\n"
        "\n"
        "If you were cutting a release: you rewrote a dependency that "
        "happened to share the old version number. Rebuild the lockfile "
        "from the previous commit and change only the project's own two "
        "version fields — the top-level one and packages[''].\n"
        "\n"
        "If the change was deliberate: say what moved under CHANGED in "
        f"{RECORD.name}, and record\n"
        f"    SHA256  {seen}"
    )


def test_the_project_version_is_what_the_mask_covers():
    """The mask hides the app's own version, and nothing more than that.

    A guard that masked the whole file would pass forever. This is the
    proof it cannot: moving the project's version leaves the fingerprint
    where it was, and moving any dependency's does not.
    """
    doc = _lockfile()
    before = _fingerprint(doc)

    bumped = copy.deepcopy(doc)
    bumped["version"] = "99.99.99"
    bumped["packages"][""]["version"] = "99.99.99"
    assert _fingerprint(bumped) == before, (
        "a version bump moved the fingerprint — the mask is too narrow"
    )

    moved = copy.deepcopy(doc)
    name = next(k for k in moved["packages"] if k and "version" in moved["packages"][k])
    moved["packages"][name]["version"] = "99.99.99"
    assert _fingerprint(moved) != before, (
        f"moving {name} left the fingerprint alone — the mask is too wide"
    )


def test_the_lockfile_agrees_with_the_manifest():
    """The two versions the mask covers are the app's real version."""
    manifest = json.loads((ROOT / "app" / "package.json").read_text(encoding="utf-8"))
    doc = _lockfile()
    assert doc["version"] == manifest["version"], (
        "package-lock.json's top-level version and package.json's disagree"
    )
    assert doc["packages"][""]["version"] == manifest["version"], (
        "package-lock.json's packages[''] version and package.json's disagree"
    )
