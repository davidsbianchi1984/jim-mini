"""The community layer JIM points at rather than builds — FIG. 2 boxes 222–226.

P001's specification describes a community inside the guidance product:
"interact with others, view and create content" (222), "process user content
for moderation, distribution" (224), "store user content for incorporation
into community interaction" (226), and in [0020] the promise of "our chat
engines, your local events, and forums in all languages".

Every one of those things exists — in QRME. Rooms with channels (chat, voice,
video, AR, VR), a moderated wall, localities drawn from what listings actually
claim, and per-profile language. The two products are designed to run in
tandem, so the honest way to keep this promise is a **door, not a second
implementation**: JIM surfaces QRME's community through the connection the
specialist bracket already uses, and says plainly where the room lives.

Building a parallel social network inside a private health guardian would be
the wrong answer twice over. It would duplicate a moderation stack that is
hard to get right once, and it would put a person's health app and their
public posting in the same database — which is exactly the separation the
suite's architecture exists to preserve. Health data stays in JIM (and the
vault); community lives in QRME under the user's own QRME identity.

So this module is deliberately thin: read the shelf, name the language, and
hand back a URL. It never mirrors a room's contents into JIM's database, and
it never posts on the user's behalf.
"""

from __future__ import annotations

from . import db, i18n


def _room_url(base: str | None, room_id: str) -> str | None:
    return f"{base}/app/#/rooms/{room_id}" if base else None


def view(user_id: str, qrme, locality: str | None = None) -> dict:
    """QRME's community, as JIM can honestly show it.

    ``locality`` filters the places list to a match; rooms are returned as
    QRME serves them, with the language JIM knows this user reads so a client
    can say which rooms are in their tongue.
    """
    rooms = qrme.rooms()
    places = qrme.localities()
    if locality:
        needle = locality.strip().lower()
        places = [p for p in places
                  if needle in str(p.get("locality", "")).lower()]

    language = i18n.effective_language(user_id)
    base = getattr(qrme, "base_url", None)
    return {
        "qrme_url": base,
        "language": language,
        # Rooms are QRME's, passed through whole — topic, channel, heads.
        "rooms": [{**room, "url": _room_url(base, room["id"])}
                  for room in rooms if room.get("id")],
        "places": places,
        "note": ("community lives in QRME, where the moderation, the rooms "
                 "and the languages already are — JIM shows the door and "
                 "keeps your health data out of it. Posting happens there, "
                 "under your own QRME identity"),
        "posture": {
            "mirrored_here": False,
            "posts_on_your_behalf": False,
            "health_data_shared": False,
        },
    }


def note_visit(user_id: str, room_id: str) -> dict:
    """Record that this user opened a community door — an event on their own
    timeline, and nothing else. No room contents, no message bodies: the
    point of the bridge is that the conversation stays in QRME."""
    from . import guardian

    guardian._event(user_id, "community_room_opened",
                    detail={"room_id": room_id, "where": "qrme"})
    return {"noted": True, "room_id": room_id,
            "stored": "the fact that you opened it, nothing from inside"}


def history(user_id: str, limit: int = 20) -> list[dict]:
    rows = db.connect().execute(
        "SELECT detail, created_at FROM events WHERE user_id=?"
        " AND type='community_room_opened'"
        " ORDER BY created_at DESC, rowid DESC LIMIT ?",
        (user_id, limit)).fetchall()
    import json
    return [{**json.loads(r["detail"] or "{}"), "at": r["created_at"]}
            for r in rows]
