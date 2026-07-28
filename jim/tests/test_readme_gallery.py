import pathlib
"""The README's gallery and the screens on disk, held in step.

This file exists because the defect it catches shipped. Screen 74, *"You're on
Basic"*, was written to `74-you're-on-basic.svg` while the README pointed at
`74-youre-on-basic.svg`, and the gallery drew a broken icon on `main`.

The cause is worth writing down, because it is not "somebody made a typo". QRME
had been bitten by the same class twice — a comma, then a `?` — and gained a
`slug()` function and a test for it. Neither reached this repository. jim-mini
went on slugging titles by hand in the builder, with **nothing checking the
result**, so the first title containing an apostrophe produced a filename the
README could not address and no failure anywhere.

A broken image is invisible to whoever wrote it: it renders on somebody else's
machine, in somebody else's browser, days later. That is exactly the kind of
thing that has to be asserted rather than looked at.
"""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
README = os.path.join(ROOT, "README.md")
SCREENS = os.path.join(ROOT, "docs", "screens")
WATCH = os.path.join(ROOT, "docs", "watch")


def _readme() -> str:
    with open(README, encoding="utf-8") as fh:
        return fh.read()


def _on_disk(folder: str) -> set[str]:
    return {f for f in os.listdir(folder) if f.endswith(".svg")}


def _referenced(folder_name: str) -> list[str]:
    seen: dict[str, None] = {}
    for name in re.findall(rf"docs/{folder_name}/([\w\-.'%]+\.svg)", _readme()):
        seen.setdefault(name, None)
    return list(seen)


def test_no_screen_is_named_something_a_url_cannot_carry():
    """The one that would have caught screen 74.

    An apostrophe is legal in a URL path but GitHub's raw host escapes it to
    `%27`, so a README written with the plain character resolves to nothing.
    A `?` is worse — it starts a query string. Neither belongs in a filename
    that is going to be addressed from markup.
    """
    bad = sorted(f for f in _on_disk(SCREENS) | _on_disk(WATCH)
                 if not re.fullmatch(r"[0-9a-z][0-9a-z\-.]*\.svg", f))
    assert not bad, ("screen files whose names are unsafe in a URL:\n  "
                     + "\n  ".join(bad))


def test_every_referenced_screen_exists():
    """A broken image is invisible to whoever wrote it."""
    missing = sorted(set(_referenced("screens")) - _on_disk(SCREENS))
    assert not missing, ("the README points at screens not on disk:\n  "
                         + "\n  ".join(missing))


def test_every_referenced_watch_face_exists():
    missing = sorted(set(_referenced("watch")) - _on_disk(WATCH))
    assert not missing, ("the README points at watch faces not on disk:\n  "
                         + "\n  ".join(missing))


def test_every_screen_is_shown_somewhere():
    """The other direction: a screen that exists and is in no gallery is one
    nobody can see. Channel 2's screens 65 and 66 went missing once already."""
    unshown = sorted(_on_disk(SCREENS) - set(_referenced("screens")))
    assert not unshown, ("screens exist that the README never shows:\n  "
                         + "\n  ".join(unshown))


def test_the_gallery_skips_no_number():
    """Adding a screen to a full row is how a number stops appearing while
    every file still exists and every link still resolves."""
    numbers: list[int] = []
    for name in _referenced("screens"):
        head = name.split("-", 1)[0]
        if head.isdigit() and int(head) not in numbers:
            numbers.append(int(head))
    expected = list(range(1, max(numbers) + 1))
    assert sorted(numbers) == expected, (
        "the gallery skips: "
        + ", ".join(str(n) for n in expected if n not in numbers))


def test_the_builder_names_files_in_exactly_one_place():
    """The root cause, asserted directly.

    The apostrophe reached a filename because the slug was written out inline
    at the point of writing the file, with no shared function and nothing
    checking it. `filename()` is now the only thing that names a screen.
    """
    with open(os.path.join(ROOT, "docs", "screens", "build.py"),
              encoding="utf-8") as fh:
        src = fh.read()
    assert "def slug(" in src and "def filename(" in src
    assert src.count('.replace(" & ", "-")') == 1, (
        "the slug expression appears more than once — that duplication is how "
        "a comma reached a filename in the sibling repository")


# -- the README's own arithmetic -----------------------------------------------

def test_every_test_count_the_readme_claims_is_true():
    """The README says "`module.py`, N tests" in a dozen places, and five of
    them were wrong when this was written — `storage.py` claimed 23 with 38,
    `dock.py` claimed 30 with 34, and JIM-mini's three were all short.

    A number in prose is a duplicate of something the repository already
    knows, and duplicates drift the moment somebody adds a test. Nothing fails
    when a file grows a function, so nothing did — for several releases, in a
    document whose whole pitch is that its claims are checked.

    The counting is deliberately the dumb kind: `def test_` at column zero, in
    every file matching the module's name. A cleverer measure would be a
    second thing to keep in step.
    """
    import re

    # jim/tests/ -> jim/ -> repo root.
    root = pathlib.Path(__file__).resolve().parents[2]
    readme = (root / "README.md").read_text()
    claims = re.findall(
        r"`((?:qrme|jim)/[\w/]+\.py)`[^\n]{0,40}?(\d+) tests", readme)
    assert claims, "no test-count claims found — has the README format changed?"
    for module, claimed in claims:
        stem = pathlib.Path(module).stem
        files = sorted(root.rglob(f"test_{stem}*.py"))
        assert files, f"README cites {module} but no test_{stem}*.py exists"
        actual = sum(len(re.findall(r"^def test_", f.read_text(), re.M))
                     for f in files)
        assert actual == int(claimed), (
            f"README says {module} has {claimed} tests; "
            f"{', '.join(f.name for f in files)} hold {actual}")


def test_the_desktop_app_version_matches_the_api():
    """Three releases shipped installers labelled 0.3.3 from 0.4.x tags.

    `app/package.json` carries its own version and no cut ever bumped it — the
    0.4.0 and 0.4.1 releases both attached installers named 0.3.3, built from
    the right tag but stamped with the stale number. The filename and the
    About box are cosmetic; the auto-updater is not, because it compares
    package versions and will tell an installed app there is nothing newer.

    Same disease as the stale test counts: a duplicated number with nothing to
    fail when the other copy moves. The versions must move together now.
    """
    import json
    import re

    root = pathlib.Path(__file__).resolve()
    while not (root / "app" / "package.json").exists():
        root = root.parent
    desktop = json.loads((root / "app" / "package.json").read_text())["version"]
    api_src = (root / "jim/api.py").read_text()
    api = re.search(r'version="([\d.]+)"', api_src).group(1)
    assert desktop == api, (
        f"app/package.json says {desktop}, jim/api.py says {api} — the "
        "installer filenames and the auto-updater follow the first, the "
        "release tag follows the second")
