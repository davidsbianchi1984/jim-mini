"""A gallery row that is longer than its neighbours is a hole in every other row.

Reported from a phone: watch faces 05, 10, 15, 20, 25, 30, 35 and 36 were not
visible in JIM-mini's README. That is exactly the set of cells in the last
column, and the reason was two layers deep.

An HTML table is as wide as its **longest row**. JIM's watch gallery had six
rows of five and one row of six, so the table was six columns wide: every
five-cell row rendered a sixth empty column, and on a phone the whole thing
was clipped past the fourth. This repo's main gallery was worse — one `<tr>`
carrying **fifteen** cells beside rows of three, which made that table fifteen
columns wide and left twelve empty columns on almost every row.

    asked     is every screen in the gallery
    mattered  is every screen in the gallery *on the page*

The gallery guard next door already checks that every drawing is
referenced and every reference resolves, and it passed the whole time. A cell
can be present in the markup and pushed off the visible page by the row it
sits in, which is a thing only the shape of the table can tell you.

## What counts as a gallery here

A `<table>` whose picture cells all point at one folder under `docs/`, with at
least four of them. That deliberately excludes the caption pairs — an image
beside a paragraph — and the hand-composed montage that shows one screen on
three devices at once. Those are layouts, not lists.

Four across is the number, not three or five: four is what fits the phone the
report came from, and a wider grid is the defect being described.
"""

import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
README = REPO / "README.md"
GALLERY = REPO / "docs" / "gallery.md"

TABLE = re.compile(r"<table>(.*?)</table>", re.S)
ROW = re.compile(r"<tr>(.*?)</tr>", re.S)
CELL = re.compile(r"<td\b.*?</td>", re.S)
# The README says `docs/<folder>/…`; the gallery page lives inside docs/
# and says `<folder>/…` — a link is relative to the file it renders from.
PICTURE = re.compile(r'<img src="(?:docs/)?([\w/]+)/')

# Screens and watch faces are small enough to sit four across on a phone.
# Desktop frames are not, and go two.
ACROSS = {"screens": 4, "watch": 4, "desktop": 2}


def _galleries():
    """(folder, [row lengths]) for every table that is a list of pictures."""
    src = (GALLERY.read_text(encoding="utf-8") + "\n"
           + README.read_text(encoding="utf-8"))
    for table in TABLE.findall(src):
        rows = [CELL.findall(r) for r in ROW.findall(table)]
        cells = [c for row in rows for c in row]
        shown = [c for c in cells if PICTURE.search(c)]
        folders = {PICTURE.search(c).group(1) for c in shown}
        if len(shown) < 4 or len(folders) != 1:
            continue
        folder = folders.pop()
        if folder not in ACROSS:
            continue
        yield folder, [len(r) for r in rows], len(cells) - len(shown)


def test_there_are_galleries_to_check():
    """A regex rewrite that matched nothing would report every gallery in
    perfect shape by finding none of them."""
    found = list(_galleries())
    assert len(found) >= 2, (
        f"only {len(found)} gallery table(s) found in the README — the checks "
        f"below are passing on almost nothing")


def test_no_gallery_row_is_wider_than_the_phone_it_is_read_on():
    """Four across. A fifth column is the column that went missing."""
    wrong = [(folder, rows) for folder, rows, _ in _galleries()
             if max(rows) > ACROSS[folder]]
    assert not wrong, "\n    ".join(
        [""] + [f"docs/{f}: rows {r}, widest is {max(r)} — "
                f"{ACROSS[f]} is the limit" for f, r in wrong])


def test_every_gallery_row_is_the_same_length_as_the_one_above_it():
    """The table is as wide as its longest row, so one long row puts a hole in
    every other. Only the last row may be short, because a list rarely ends on
    a round number."""
    ragged = []
    for folder, rows, _ in _galleries():
        body = rows[:-1]
        if body and len(set(body)) > 1:
            ragged.append((folder, rows))
    assert not ragged, "\n    ".join(
        [""] + [f"docs/{f}: rows {r} — every row but the last must match"
                for f, r in ragged])


def test_no_gallery_cell_is_empty():
    """An empty `<td>` in a list of pictures is a blank square on the page,
    and there is never a reason for one: a short last row already ends
    wherever it ends."""
    blanks = [(folder, n) for folder, _, n in _galleries() if n]
    assert not blanks, "\n    ".join(
        [""] + [f"docs/{f}: {n} cell(s) with no picture in them"
                for f, n in blanks])


# --- the checks have to be able to fail --------------------------------------

@pytest.mark.parametrize("rows,widest", [([4, 4, 3], 4), ([5, 5], 5)])
def test_the_width_check_reads_the_widest_row_not_the_first(rows, widest):
    """JIM's watch gallery opened with five rows of five and put the sixth
    cell in the *last* row, so anything reading row one called it fine."""
    assert max(rows) == widest
