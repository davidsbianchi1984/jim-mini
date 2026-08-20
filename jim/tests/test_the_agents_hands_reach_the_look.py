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
    and had none. `set_appearance` exists, acts, can be taken back, and
    sits in a group opening the session already covers — asking out loud
    is not harder than the Settings screen."""
    row = engaged.tool("set_appearance")
    assert row["acts"] and "undo" in row
    assert permits.area_of("set_appearance") == "how_it_speaks"
    assert permits.AREAS["how_it_speaks"]["standing"] == "opened"


def test_the_asked_for_excursion_is_a_tool_of_its_own():
    """"Go study strength training for me" is its own consent, so the
    attended excursion stands opened where the unattended sibling still
    needs its own yes — the axis that separates them is who initiated,
    and it is pinned here so a refactor cannot quietly swap it."""
    row = engaged.tool("study")
    assert row["route"] == ("POST", "/coach/{user_id}/study")
    area = permits.area_of("study")
    assert permits.AREAS[area]["standing"] == "opened"
    assert permits.AREAS[permits.area_of("study_unattended")][
        "standing"] == "asked"


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
