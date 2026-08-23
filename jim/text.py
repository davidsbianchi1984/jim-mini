"""Shortening text without lying about it.

QRME's wall learned this first, for posts a person writes: *a cut inside a
word is what was reported and is the one outcome this refuses*. Nothing in
this repository had learned it at all, and this is the product where the
material being cut is somebody's health.

    asked     does the text fit
    mattered  what does the part that fits say

`jim/coach.py` assembled collected context with `data['content'][:160]` — a
bare slice, mid-word, silent. Collected context is whatever a person or a
monitor put there, which on this product means a symptom, a dose, a reading.
Cutting *"pain is not radiating down the left arm"* at the wrong character
hands the coach the opposite of the sentence, and nothing anywhere says the
sentence was cut.

A word boundary is the smaller half of the fix and the marker is the larger:
*"no history of"* and *"pain is not"* are both clean whole-word cuts that
invert. So this returns whether it cut, and the caller says so in words that
suit where the text is going.
"""

from __future__ import annotations

#: Boundaries to prefer, largest first — the same ladder QRME's `wall.parts`
#: walks, kept identical on purpose: the two products should not disagree
#: about what a safe place to stop is.
_BREAKS = ("\n\n", "\n", ". ", " ")


def clipped(text: str, cap: int) -> tuple[str, bool]:
    """`(text, was_cut)` — shortened at a boundary, never inside a word."""
    text = (text or "").strip()
    if len(text) <= cap:
        return text, False
    window = text[:cap]
    # Two passes. The first prefers a boundary in the second half, so what
    # comes back is not a stub. The second accepts a boundary ANYWHERE,
    # because a short honest clip beats a broken word — this is a clip, not
    # a split into parts, and nothing downstream needs the piece to be a
    # certain size. Written as two passes after a sweep across every cap
    # caught the single-pass version cutting "The patien" out of "The
    # patient": with no space past the halfway mark it fell straight through
    # to the raw cut, so the guarantee this function is named for was false
    # exactly where the text was shortest.
    for floor in (cap // 2, -1):
        for mark in _BREAKS:
            cut = window.rfind(mark)
            if cut > floor:
                return window[:cut].rstrip(), True
    # One unbroken run longer than the cap — a URL, a drug name, an
    # identifier. Cutting at the ceiling is what is left, and the caller's
    # marker is what keeps it honest.
    return window.rstrip(), True
