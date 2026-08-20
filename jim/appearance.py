"""How the console looks, as a setting the person — or their agent — can set.

Field report, verbatim enough: "I'd like my homepage to be decorated in
black and white", said to an engaged session — which had no tool for it,
refused `update_setting`, and could only promise to keep it in mind. The
person had asked for the one kind of change an assistant should always be
able to make: cosmetic, their own, and reversible.

    asked     can the person have the app look how they want
    mattered  the agent offering to change what it cannot reach is worse
              than a menu

Three looks, named for what they are rather than a mood:

    standard   the palette the product ships with
    midnight   black background, white text — the look the report asked for
    paper      white background, black text

A theme changes surface colors only. It never touches photos, tiles, or
what any screen shows — the same field report said, in so many words, "do
not mess with photos or category tiles" — and it is a register, never a
capability: nothing is seen or watched differently in any of the three.
"""

from __future__ import annotations

from . import db

DEFAULT = "standard"

#: Theme -> the sentence a person (and the agent) reads about it.
THEMES: dict[str, str] = {
    "standard": "the palette the product ships with",
    "midnight": "black background, white text — photos and tiles untouched",
    "paper": "white background, black text — photos and tiles untouched",
}


def theme(user_id: str) -> str:
    row = db.connect().execute(
        "SELECT theme FROM appearance WHERE user_id=?",
        (user_id,)).fetchone()
    return row["theme"] if row else DEFAULT


def set_theme(user_id: str, value: str) -> dict:
    if value not in THEMES:
        raise ValueError(
            f"no look called {value!r} — it is one of "
            + ", ".join(THEMES))
    conn = db.connect()
    conn.execute(
        "INSERT INTO appearance (user_id, theme, created_at)"
        " VALUES (?,?,?) ON CONFLICT (user_id) DO UPDATE SET"
        " theme=excluded.theme, created_at=excluded.created_at",
        (user_id, value, db.utcnow()))
    conn.commit()
    return view(user_id)


def view(user_id: str) -> dict:
    return {
        "user_id": user_id,
        "theme": theme(user_id),
        "default": DEFAULT,
        "choices": dict(THEMES),
    }
