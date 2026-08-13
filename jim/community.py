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

import os

from . import db, i18n


def _public_qrme(qrme) -> str | None:
    """The QRME address a *person's browser* can reach, not the tandem's.

    ``qrme.base_url`` is how this backend talks to QRME — on a composed
    deployment that is an internal hostname (``http://qrme:8000``) which a
    phone cannot resolve. A field report tapped "Open it in QRME" and landed
    somewhere wrong, because the link carried the backend's own address.

    ``JIM_QRME_PUBLIC_URL`` names the public one (``https://sntheticprofiles
    .com`` on the beta). Unset, the tandem address stands — the self-hosted
    single-machine case, where the two are genuinely the same.
    """
    public = os.environ.get("JIM_QRME_PUBLIC_URL", "").strip().rstrip("/")
    return public or getattr(qrme, "base_url", None)


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
    base = _public_qrme(qrme)
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
            "records": [
                "that you opened a community room — the room's id and the "
                "time, on your own timeline, and nothing from inside it"],
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


def feed(user_id: str, qrme, cursor: str | None = None) -> dict:
    """QRME's public feed, shown through the same door the rooms use.

    The same argument this module opens with, applied to video: QRME already
    has the wall, the moderation, the desks and the rooms, and building a
    second stream inside a private health guardian would put somebody's
    medical timeline and their public watching in one database.

    So this is thin on purpose. It passes QRME's cards through unchanged —
    including ``plays``, which is QRME's promise that footage it does not
    hold makes no request until somebody presses it — and adds only what JIM
    knows and QRME does not: which language this user reads, and where the
    door goes.

    **JIM cannot post to it.** There is no write path here and there is not
    going to be one: publishing happens in QRME, under the user's own QRME
    identity, which is the whole point of showing a door instead of building
    a room.
    """
    page = qrme.feed(cursor=cursor)
    base = _public_qrme(qrme)
    items = page.get("items") or []
    return {
        "qrme_url": base,
        "language": i18n.effective_language(user_id),
        "items": items,
        "cursor": page.get("cursor"),
        "counts": page.get("counts") or {},
        "rules": page.get("rules") or {},
        "open_in_qrme": f"{base}/app/#/feed" if base else None,
        "note": ("this feed is QRME's. JIM shows it and keeps your health "
                 "data out of it — watching here tells QRME nothing about "
                 "your guardian, and no card you scroll past is stored in "
                 "JIM. Opening a room is the one thing that is: see "
                 "`records`"),
        "posture": {
            "mirrored_here": False,
            "posts_on_your_behalf": False,
            "can_post_from_jim": False,
            "health_data_shared": False,
            "watching_stored_here": False,
            "records": [
                "that you opened a community room — the room's id and the "
                "time, on your own timeline, and nothing from inside it"],
        },
    }
