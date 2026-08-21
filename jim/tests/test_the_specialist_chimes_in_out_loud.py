"""The specialist chimes in out loud.

Field report: blood oxygen dropped, the attached doctor profile chimed in
— with text. Correct text, correct call door beside it, and easy to
scroll past at exactly the moment it should not be. The monitor screen
now opens her own sphere, speaks the guidance, and holds the microphone
open for a discussion at her own door.

    asked     was the chime-in heard
    mattered  guidance that can be missed is guidance that was not given

The server's half of that is an address: the monitoring path names who
spoke (`specialist`) and now also the life area that leads back to them
(`specialist_area`), because the discussion door speaks in areas and the
console should never have to guess the inverse of a private map.
"""

from __future__ import annotations

import re
from pathlib import Path

from jim import specialists

REPO = Path(__file__).resolve().parents[2]


def test_every_condition_leads_back_to_its_area():
    """The inverse read agrees with the declared map, both directions:
    every condition in an area's tuple resolves to that area, and a
    condition nobody declared resolves to None rather than a guess."""
    for area, domains in specialists.AREA_CONDITIONS.items():
        for condition in domains:
            assert specialists.area_for_condition(condition) == area
    assert specialists.area_for_condition("no_such_condition") is None


def test_the_offer_carries_its_own_door():
    """`offer` names the area it was asked about, so a surface holding an
    offer can address a follow-up without reconstructing the question."""
    import inspect
    src = inspect.getsource(specialists.offer)
    assert '"area": area' in src


def test_the_monitor_screen_speaks_and_discusses():
    """The console's half, held by drift guards: the sphere exists, the
    guidance is spoken, the discussion goes to the specialist's area when
    the server named one, and the sphere names who is speaking."""
    src = (REPO / "app/src/screens/Monitor.tsx").read_text(encoding="utf-8")
    assert "voice-orb-veil" in src, "the sphere never opens"
    assert "specialist_area" in src, (
        "the discussion cannot find the specialist's door")
    assert "coachSpecialist" in src, (
        "the discussion never reaches the specialist")
    assert "voice-orb-who" in src, (
        "the sphere does not say whose voice it is")
    # The chime rides detection + guidance, never a calm reading.
    assert re.search(r"detected\s*&&\s*r\.guidance\?\.content", src)
