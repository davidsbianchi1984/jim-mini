"""The agent's hands reach the look.

Field report, with the transcript on screen: "I'd like my homepage to be
decorated in black and white", said to an engaged session — which had no
tool for it, refused `update_setting`, and could only promise to keep the
wish in mind for "later in this session". The person had asked for the one
kind of change an assistant should always be able to make: cosmetic, their
own, and reversible.

    asked     can the person have the app look how they want
    mattered  an agent offering to change what it cannot reach is worse
              than a menu

The same report, one breath later: "do not mess with photos or category
tiles". So the setting is colors only — `jim/appearance.py` says so, the
tool's own sentence says so, and the console's theme classes override
tokens without ever filtering an image.
"""

from __future__ import annotations

import re
from pathlib import Path

from jim import appearance, engaged, permits

from .conftest import enroll

REPO = Path(__file__).resolve().parents[2]


def test_the_look_is_a_setting_that_round_trips(client):
    uid = enroll(client)
    r = client.get(f"/appearance/{uid}")
    assert r.status_code == 200, r.text
    assert r.json()["theme"] == appearance.DEFAULT
    r = client.put(f"/appearance/{uid}", json={"theme": "midnight"})
    assert r.status_code == 200, r.text
    assert r.json()["theme"] == "midnight"
    assert client.get(f"/appearance/{uid}").json()["theme"] == "midnight"


def test_a_look_that_does_not_exist_is_refused_with_the_choices(client):
    uid = enroll(client)
    r = client.put(f"/appearance/{uid}", json={"theme": "grayscale"})
    assert r.status_code == 422
    # The refusal lists what there is — an agent (or a person) told only
    # "no" would ask again with another guess.
    for name in appearance.THEMES:
        assert name in r.text


def test_the_agent_has_a_real_hand_for_the_look():
    """The exact failing gesture: the session needed a tool for the look
    and had none. `set_appearance` exists, acts, and can be taken back.

    It shipped one release inside `how_it_speaks`, covered by opening the
    session; the review called it back out. The permits module's own rule
    — consent already given for one thing is not consent for a new thing —
    applied all along, and cosmetic-and-reversible lowered the stakes, not
    the principle. Its own group, its own yes."""
    row = engaged.tool("set_appearance")
    assert row["acts"] and "undo" in row
    assert permits.area_of("set_appearance") == "how_it_looks"
    assert permits.AREAS["how_it_looks"]["standing"] == "asked"


def test_the_asked_for_excursion_is_a_tool_of_its_own():
    """"Go study strength training for me" stands opened where the
    unattended sibling needs its own yes — the axis that separates them
    is who initiated, pinned here so a refactor cannot quietly swap it.

    The review kept the standing and added the question: the agent must
    ask, in that turn, before the topic leaves — in the reviewer's own
    words, verbatim below — and only go on a yes. The sentence lives in
    the system prompt, so this holds the prompt to it."""
    row = engaged.tool("study")
    assert row["route"] == ("POST", "/coach/{user_id}/study")
    area = permits.area_of("study")
    assert permits.AREAS[area]["standing"] == "opened"
    assert permits.AREAS[permits.area_of("study_unattended")][
        "standing"] == "asked"
    assert ("Shall I go online and research more into this topic and "
            "bring back a\n    copy for coach to hold and use while "
            "offline?") in engaged.SYSTEM
    assert "only if they say yes" in engaged.SYSTEM


def test_the_console_offers_the_yes_no_choice():
    """The reviewer asked for the question "with yes/no choice", and the
    choice is buttons: the Engaged screen watches the transcript for the
    verbatim question and offers yes and no. That only works while the
    screen's copy of the sentence and the prompt's stay identical — this
    is the thread holding them together."""
    q = ("Shall I go online and research more into this topic and bring "
         "back a copy for coach to hold and use while offline?")
    assert q in " ".join(engaged.SYSTEM.split())
    src = (REPO / "app/src/screens/Engaged.tsx").read_text(encoding="utf-8")
    # TSX wraps the literal across lines with `" + "`; undo the seams and
    # the wrapping before comparing.
    glued = " ".join(re.sub(r'"\s*\+\s*"', "", src).split())
    assert q in glued, (
        "the Engaged screen's STUDY_ASK no longer matches the prompt's "
        "question — the yes/no buttons will never appear")


def test_the_conversation_bows_out_after_two_quiet_minutes():
    """The reviewer's number for the standing conversation: "at least two
    minutes would be enough". One constant in speech.ts, imported by both
    rooms — a screen with its own copy of the number is a screen that
    drifts."""
    speech = (REPO / "app/src/speech.ts").read_text(encoding="utf-8")
    assert "export const CONVERSATION_IDLE_MS = 120_000" in speech
    for screen in ("Coach", "Talk", "Engaged", "Monitor"):
        src = (REPO / f"app/src/screens/{screen}.tsx").read_text(
            encoding="utf-8")
        assert "CONVERSATION_IDLE_MS" in src, (
            f"{screen} does not read the shared idle ceiling")
        assert not re.search(r"IDLE_MS\s*=\s*\d", src), (
            f"{screen} carries its own copy of the number")


def test_every_theme_the_server_offers_is_painted_by_the_console():
    """The drift guard between the vocabulary and the pixels: a theme the
    route accepts but styles.css does not style would "work" and change
    nothing, which is the agent lying with a 200."""
    css = (REPO / "app/src/styles.css").read_text(encoding="utf-8")
    for name in appearance.THEMES:
        if name == appearance.DEFAULT:
            continue  # the default is the absence of a class
        assert f"body.theme-{name}" in css, (
            f"theme {name!r} is offered on the wire and painted nowhere")
    assert "filter" not in css.split("body.theme-")[-1].split("}")[0], (
        "a theme block filters content — the report said colors only, "
        "never photos")
