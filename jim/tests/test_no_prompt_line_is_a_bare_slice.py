"""A line built for a prompt is not shortened with a bare slice.

    asked     does the text fit
    mattered  what does the part that fits say

QRME's wall learned this for posts somebody writes — *a cut inside a word is
the one outcome this refuses*. Nothing here had learned it at all, and this
is the product where the material being cut is somebody's health.

`_context` assembled collected context as `data['content'][:160]`: bare,
mid-word, silent. Collected context is whatever a person or a monitor put
there, which on this product means a symptom, a dose, a reading. Cutting
*"the pain is not radiating down the left arm"* at the wrong character hands
the coach the opposite of the sentence.

The word boundary is the smaller half. *"The pain is not radiating"* is a
clean whole-word cut and still inverts, so the marker is what does the work —
and this file checks for both, because a fix that only rounded the cut to a
word would look like a fix.

The guard reads the prompt builder rather than a list of known lines. A list
is a second place to update, and the day somebody forgets is the day a new
line goes in bare.
"""

from __future__ import annotations

import inspect
import re

from jim import coach
from jim.text import clipped

#: A slice with a number big enough to be prose rather than an index or a
#: date. `at[:10]` is a date; `content[:160]` is a sentence being guillotined.
_BARE_SLICE = re.compile(r"\[:\s*(\d{2,})\s*\]")

#: Cuts that are not prose and are allowed to stay bare, with the reason.
_NOT_PROSE = {
    # `created_at[:10]` — an ISO date trimmed to its day. Fixed width, no
    # words in it, and nothing to be cut in half.
    10,
}


def test_the_coach_context_shortens_at_a_boundary():
    source = inspect.getsource(coach._context)
    bare = [int(n) for n in _BARE_SLICE.findall(source)
            if int(n) not in _NOT_PROSE]
    assert not bare, (
        f"the coach's context still cuts with a bare slice at {bare} — a "
        "symptom or a dose shortened mid-word, silently, and a negation can "
        "sit in the half that went"
    )
    assert "clipped(" in source, (
        "nothing in the coach's context shortens at a boundary"
    )


def test_a_shortened_context_line_says_a_negation_may_be_missing():
    """The half that matters. A boundary-safe cut still inverts — "the pain
    is not radiating" is a clean whole-word cut — so something has to say
    the sentence continues."""
    source = inspect.getsource(coach._context)
    assert "negation or qualification" in source, (
        "context is cut at a word boundary and says nothing, which reads to "
        "the model as a complete short note rather than an opening fragment"
    )


def test_a_note_that_fits_is_left_exactly_alone():
    short = "Slept badly, headache since morning."
    assert clipped(short, 160) == (short, False)


def test_a_word_is_never_cut_in_half():
    """Swept across every cap rather than checked at one.

    The first version of this test picked 30 and passed against a build with
    the boundary search removed, because 30 happened to land on a space in
    that sentence. A single cap tests the sentence as much as the code; the
    sweep tests the code.
    """
    line = "The pain is not radiating down the left arm and settled quickly."
    for cap in range(10, len(line)):
        out, cut = clipped(line, cap)
        assert cut is True and line.startswith(out), cap
        assert line[len(out)] in " .", (
            f"cap {cap} cut inside a word: {out!r}"
        )


def test_an_unbroken_run_is_cut_at_the_ceiling_rather_than_looping():
    out, cut = clipped("x" * 400, 40)
    assert cut is True and len(out) == 40


def test_both_products_agree_on_where_it_is_safe_to_stop():
    """The two ladders are kept identical on purpose. A coach and a profile
    disagreeing about what a safe place to stop is would be two answers to
    one question, and the wrong one would be whichever nobody looked at."""
    from jim.text import _BREAKS

    assert _BREAKS == ("\n\n", "\n", ". ", " ")
