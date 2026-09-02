"""Every screen this product has, known to the things that speak for it.

The coach shrugged at "plant a quarter-hour lookout", and the answer was five
hand-written doors in the prompt. That fixed the five. Twenty-seven other
screens stayed invisible to it, and the same shrug was available for any of
them the day somebody asked.

    asked     can this assistant do it
    mattered  can the product, and where is it

`ui_screens.txt` already answers *does this surface have a drawing*. This
file answers the other half — *does anything that talks for the product know
what it is for* — off the same list, so the two cannot drift. A screen added
without a row fails here, which is the friction the census was built for
pointed at a second thing that goes stale silently.

## Why the shape is core / relevant / index

A prompt full of manual stops noticing the person in front of it, so the turn
does not carry thirty-two doors. It carries the load-bearing ones always, the
ones this message is about, and the *names* of the rest.

The index is the part under test here more than anywhere else. It is what
makes "I cannot do that" wrong when the screen is in the navigation bar — a
model that can read `Medications screen` in a list will name it, and naming
it is the whole of what the field report wanted.
"""

from __future__ import annotations

import re
from pathlib import Path

from jim import coach, llm, productmap

from jim.tests.conftest import enroll

MANIFEST = Path(__file__).resolve().parent / "ui_screens.txt"


def _census() -> set[str]:
    out = set()
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if line:
            out.add(line.split()[0])
    return out


def test_every_surface_the_census_knows_has_a_row():
    """The failure this file exists for: a screen ships and nothing that
    speaks for the product ever hears about it."""
    missing = sorted(_census() - {d.surface for d in productmap.DOORS})
    assert not missing, (
        "these surfaces are in ui_screens.txt and not in productmap.DOORS: "
        f"{missing}\nGive each one a place, a line saying what it is for, "
        "and the words somebody would use to ask for it. A screen nothing "
        "can name is a screen the coach will decline to open.")


def test_the_map_names_no_surface_that_is_gone():
    """The other direction. A row for a screen that moved is a door the
    coach will send somebody to and they will not find."""
    stale = sorted({d.surface for d in productmap.DOORS} - _census())
    assert not stale, f"rows for surfaces no longer in the census: {stale}"


def test_no_surface_is_described_twice():
    seen = [d.surface for d in productmap.DOORS]
    dupes = sorted({s for s in seen if seen.count(s) > 1})
    assert not dupes, f"two rows for one surface: {dupes}"


def test_every_row_says_where_it_is_and_what_it_is_for():
    for d in productmap.DOORS:
        assert d.place.strip(), f"{d.surface} has no place"
        assert d.what.strip(), f"{d.surface} says nothing about what it is for"
        assert d.cues, (
            f"{d.surface} has no cues, so nothing a person says can ever "
            "reach it — it lives in the index and nowhere else")


def test_a_cue_is_something_a_person_could_actually_say():
    """Cues are matched against a lowercased message with a word boundary
    either side. A capital never fires, and a cue that opens or closes on a
    non-word character has no boundary to match on."""
    for d in productmap.DOORS:
        for cue in d.cues:
            assert cue == cue.lower(), (
                f"{d.surface}: cue {cue!r} has a capital and can never match")
            assert re.match(r"^\w", cue) and re.search(r"\w$", cue), (
                f"{d.surface}: cue {cue!r} begins or ends on a non-word "
                "character, so the word boundary around it cannot match")


def test_the_core_is_the_doors_that_cannot_be_missed():
    """Safety and the permits ride every turn because getting them wrong is
    a harm rather than a disappointment."""
    always = {d.surface for d in productmap.DOORS if d.always}
    assert {"Safety", "Engaged"} <= always, (
        "safety and the permit switches are not on every turn; a coach that "
        "has to be reminded about them is one that will not mention them on "
        "the turn where it matters")
    assert always < {d.surface for d in productmap.DOORS}, (
        "every door is marked always, which is the manual-in-the-prompt this "
        "selection exists to avoid")
    core = productmap.core()
    for surface in always:
        row = next(d for d in productmap.DOORS if d.surface == surface)
        assert row.place in core, f"{surface} is marked always and is not in the core"


def test_the_turn_never_carries_the_whole_manual():
    """Selection, not a dump. The cap is the number this is held to, and a
    message that matches everything must still respect it."""
    everything = " ".join(cue for d in productmap.DOORS for cue in d.cues)
    picked = productmap.selected(everything)
    assert len(picked) <= productmap.LIMIT, (
        f"{len(picked)} doors selected against a cap of {productmap.LIMIT}")
    # And the block itself: core, the selected rows, the index of names —
    # never every door's `what` line.
    block = "\n".join(productmap.lines(everything))
    described = sum(1 for d in productmap.DOORS if d.what in block)
    assert described <= productmap.LIMIT + sum(
        1 for d in productmap.DOORS if d.always), (
        f"{described} doors arrived with their full description; the block "
        "is meant to be the core, the relevant ones, and names")


def test_what_somebody_says_reaches_the_screen_they_meant():
    """The table is only worth carrying if the words people use find it."""
    for said, surface in [
            ("where are my medications", "Meds"),
            ("what's my heart rate right now", "Monitor"),
            ("I want to delete everything you have on me", "Held"),
            ("do you have captions", "Access"),
            ("can you look something up online for me", "Reach"),
            ("show me my goals", "Aims"),
            ("I want a breathing session", "Wellness"),
            ("which model is answering me", "ProviderTiles"),
            ("take a picture of this", "Channel"),
            ("how do I change your tone", "Bearing")]:
        picked = [d.surface for d in productmap.selected(said)]
        assert surface in picked, (
            f"{said!r} did not reach {surface} — it reached {picked}")


def test_the_index_names_the_screens_this_message_did_not():
    """A door nobody asked about is still a door the coach can name, which
    is the difference between routing and declining."""
    idx = productmap.index()
    for surface in ("Meds", "Wellness", "Access", "Studio", "Watch"):
        row = next(d for d in productmap.DOORS if d.surface == surface)
        assert row.place in idx, f"{surface} is missing from the index"
    # Names only. If a door's `what` line is in the index, the index has
    # become the manual it exists instead of.
    leaked = [d.surface for d in productmap.DOORS if d.what in idx]
    assert not leaked, (
        f"the index carries full descriptions for {leaked}; it is meant to "
        "be a table of contents")


def test_the_whole_map_rides_every_coach_turn(client, monkeypatch):
    """End to end, through the route, with the message steering it."""
    uid = enroll(client)
    seen: dict = {}

    def capture(user_id, system, message, cloud=None, source=None):
        seen["system"] = system
        return {"text": "ok", "provider": "anthropic", "degraded": False,
                "reason": None, "grounded": False, "drew_on": []}

    monkeypatch.setattr(llm, "generate_for_user", capture)
    r = client.post(f"/coach/{uid}", json={
        "area": "general",
        "message": "where do I see what medications I am taking?"})
    assert r.status_code == 200, r.text
    system = seen["system"]
    # The screen they asked about, named.
    assert "Medications screen" in system
    # The core, whether or not they asked.
    assert "Safety screen" in system
    # And the index, so the door they ask about next turn is already known.
    assert "Wellness screen" in system


def test_a_screen_nobody_asked_about_is_still_reachable(client, monkeypatch):
    """The shrug this round is about: the message mentions no door at all,
    and the coach still has the console in front of it."""
    uid = enroll(client)
    seen: dict = {}

    def capture(user_id, system, message, cloud=None, source=None):
        seen["system"] = system
        return {"text": "ok", "provider": "anthropic", "degraded": False,
                "reason": None, "grounded": False, "drew_on": []}

    monkeypatch.setattr(llm, "generate_for_user", capture)
    r = client.post(f"/coach/{uid}", json={"area": "general",
                                           "message": "hey"})
    assert r.status_code == 200, r.text
    named = sum(1 for d in productmap.DOORS if d.place in seen["system"])
    assert named == len(productmap.DOORS), (
        f"only {named} of {len(productmap.DOORS)} doors are named on a turn "
        "that mentioned none of them; the rest are screens this coach would "
        "decline to open")
