"""The front door answers.

Field report with a screenshot: typing "hey" on the Talk screen came
back as a red banner reciting the area list. The Talk screen — the
front door — sends every message as area `general`, because making
somebody pick a category before they can type is the menu problem that
screen exists to answer; and the server refused the front door's own
word, on every message, since the screen was built.

    asked     can a person say hello
    mattered  the front door refusing "hey" is the product refusing people

`general` is a real coach area now: in the model's closed set, in the
coach's area map, and in the specialist map as a declared empty tuple
(no clinical domain corresponds to a person who has not yet said what
is on their mind — the Guardian answers alone).
"""

from __future__ import annotations

import re
from pathlib import Path

from jim import coach, specialists

from .conftest import enroll

REPO = Path(__file__).resolve().parents[2]


def test_hey_is_answered(client):
    """The exact failing gesture from the field: one word, area general,
    a 200 with content — never the area list in red."""
    uid = enroll(client)
    r = client.post(f"/coach/{uid}",
                    json={"area": "general", "message": "hey"})
    assert r.status_code == 200, r.text
    assert r.json()["content"]


def test_general_is_a_declared_area_everywhere():
    """The three declared places agree: the coach knows the area, and the
    specialist map holds the explicit empty-tuple decision the guard in
    test_the_person_who_asks_has_the_weaker_path demands."""
    assert "general" in coach.AREAS
    assert specialists.AREA_CONDITIONS["general"] == ()


def test_the_talk_screens_area_is_one_the_server_takes():
    """The drift guard for the gap itself: whatever area literal the Talk
    screen sends must be in the coach's map. `area: "general"` compiled
    for two releases while the server refused it — a wrong literal
    should fail a build or a test, never a person saying hello."""
    src = (REPO / "app/src/screens/Talk.tsx").read_text(encoding="utf-8")
    sent = set(re.findall(r'area:\s*"([a-z_]+)"', src))
    assert sent, "the Talk screen no longer sends an area literal; update me"
    strangers = sorted(sent - set(coach.AREAS))
    assert not strangers, (
        f"the Talk screen sends area(s) {strangers} the coach refuses — "
        "every typed message on the front door answers with the area list")


def test_general_history_filters_like_any_area(client):
    uid = enroll(client)
    client.post(f"/coach/{uid}", json={"area": "general", "message": "hey"})
    rows = client.get(f"/coach/{uid}", params={"area": "general"}).json()
    assert rows and all(r["area"] == "general" for r in rows)
