"""What an engaged session may change, grouped the way a person thinks about it.

## Where this came from

Field report, verbatim: *these menus and settings are awful user unfriendly if
you don't know what you're doing … I want users to be able to verbally
communicate with JIM what they would like to have on or off and JIM to be able
to make edits and changes to their accounts within the app or website* — and,
in the next breath, the shape it should take: *kinda like I gave you permission
and connections to my ElevenLabs account … after they opened the connectors and
approved permissions per app in the same menus*.

So: not a new kind of session, and not a wider agent. A **grant**, given once,
in a list a person reads, revocable, with the reach stated in their own words
before they say yes — exactly the shape `app_connectors.py` already uses for a
third-party app, turned around to face this account's own settings.

    asked     may this session act
    mattered  may it act *here*

## Why the old reach is not re-asked for

Twenty-six tools already act. Opening an engagement has always been the consent
for them: `engaged.what_it_can_touch()` is, in its own docstring, "the list a
person reads before they let this thing near anything", and the console shows
it at the door. Retroactively demanding a second yes for reach somebody already
approved would be a product that got *more* annoying by adding a permission
screen, which is the opposite of the report.

The reverse is equally true and is the whole reason this module exists:
**consent already given for one thing is not consent for a new thing.** The
settings tools arriving in this release reach places nothing reached before —
which sources the Guardian may read from, which features of the product are
switched on — so they get their own yes, and do not get to ride in on the old
one.

Each area therefore carries a `standing`:

    opened   granted by opening the session, because it always was
    asked    needs its own yes, because it never did

`asked` areas start refused. A refusal names the area and the door to open it,
because an agent that says "I cannot do that" without saying where the switch
is has reproduced the menu problem inside the conversation.

## What this is not

Not a second authorization layer. The token still decides *whose* records; the
door still decides whether the plan allows it; the offline guarantee still
holds. This decides only which of one person's own switches their own agent may
touch on their behalf, and every act it lets through is still recorded on the
engagement and still reversible.
"""

from __future__ import annotations

from . import audit, db

#: Every acting tool, in the group a person would look for it in — and whether
#: that group is covered by opening a session or needs its own yes.
#:
#: The reading tools are deliberately absent. A read changes nothing, is
#: already bounded to this person's own records by the token, and putting it
#: behind a switch would produce a list nobody finishes.
AREAS: dict[str, dict] = {
    "your_records": {
        "standing": "opened",
        "says": "write in your journal, log a check-in, set goals and habits, "
                "add a medication, book something in",
        "tools": ("write_journal", "note_checkin", "set_goal", "move_goal",
                  "start_habit", "log_habit", "add_med", "book", "watch_for"),
    },
    "how_it_speaks": {
        "standing": "opened",
        "says": "change how it talks to you, what language it answers in, "
                "which model answers, and which device it speaks through",
        "tools": ("set_bearing", "set_language", "set_model", "set_surface"),
    },
    "your_own_normal": {
        "standing": "opened",
        "says": "adjust the bands your readings are judged against",
        "tools": ("set_band",),
    },
    "what_it_may_read": {
        "standing": "asked",
        "says": "switch a source of yours on or off — a calendar, a watch, a "
                "connected app — changing what the Guardian is allowed to see",
        "tools": ("set_source",),
    },
    "what_is_switched_on": {
        "standing": "asked",
        "says": "switch parts of the product on or off for your account",
        "tools": ("set_feature",),
    },
    "outside_this_app": {
        "standing": "opened",
        "says": "put your question to a specialist outside JIM — the one "
                "thing here that cannot be taken back",
        "tools": ("ask_specialist",),
    },
}

#: Tool name → the area it belongs to. Built rather than written, because two
#: lists of the same names is one list and one place for them to disagree.
AREA_OF: dict[str, str] = {
    tool: area for area, spec in AREAS.items() for tool in spec["tools"]
}


def area_of(tool: str) -> str | None:
    """The area a tool sits in, or None for one that needs no grant.

    None is the honest answer for a read: it is not ungranted, it is
    ungoverned by this module, and a caller that treats "no area" as "not
    permitted" would switch every read off.
    """
    return AREA_OF.get(tool)


def _rows(user_id: str) -> dict[str, dict]:
    return {r["area"]: dict(r) for r in db.connect().execute(
        "SELECT * FROM engaged_permits WHERE user_id=?", (user_id,)).fetchall()}


def granted(user_id: str, area: str) -> bool:
    """Whether this person has said yes to this area.

    An `opened` area is yes unless they have explicitly said no — the switch
    exists in both directions, so somebody who wants their journal left alone
    can say so without giving up the rest of the session.
    """
    spec = AREAS.get(area)
    if spec is None:
        return False
    row = _rows(user_id).get(area)
    if row is None:
        return spec["standing"] == "opened"
    return bool(row["granted"])


def may(user_id: str, tool: str) -> bool:
    """Whether this session may run this tool for this person."""
    area = area_of(tool)
    return True if area is None else granted(user_id, area)


def set_grant(user_id: str, area: str, on: bool) -> dict:
    """Say yes or no to an area. Idempotent, and dated.

    The date is kept because a grant is a thing somebody did, not a flag: the
    list shows *when* they said yes, which is what makes "I never agreed to
    that" answerable.
    """
    if area not in AREAS:
        raise ValueError(f"no permit area called {area!r}")
    conn = db.connect()
    conn.execute(
        "INSERT INTO engaged_permits (user_id, area, granted, created_at)"
        " VALUES (?,?,?,?) ON CONFLICT (user_id, area) DO UPDATE SET"
        " granted=excluded.granted, created_at=excluded.created_at",
        (user_id, area, 1 if on else 0, db.utcnow()))
    conn.commit()
    audit.record("grant.open" if on else "grant.close",
                 user_id=user_id, ref=area)
    return one(user_id, area)


def one(user_id: str, area: str) -> dict:
    spec = AREAS[area]
    row = _rows(user_id).get(area)
    return {
        "area": area,
        "says": spec["says"],
        "standing": spec["standing"],
        "granted": granted(user_id, area),
        "decided_at": row["created_at"] if row else None,
        "tools": list(spec["tools"]),
    }


def permits(user_id: str) -> dict:
    """The list a person reads, and the switches they throw.

    Ordered as declared rather than alphabetically: the areas covered by
    opening a session come first and the two that need their own yes come
    after, so the screen reads as *here is what it already does, and here is
    what it will do if you let it* rather than as six equivalent rows.
    """
    return {
        "user_id": user_id,
        # `groups` and not `areas`: the presence already puts an `areas`
        # on the wire and it is a map of life areas, not a list of permit
        # groups. One name carrying two shapes is a name a typed client
        # cannot declare — and the copy calls these groups anyway.
        "groups": [one(user_id, a) for a in AREAS],
        "note": ("Every one of these can be switched off again, and anything "
                 "done under one is listed and can be taken back."),
    }


def refusal_for(tool: str) -> str:
    """The sentence a person gets when a tool is reached for without its grant.

    It names the area rather than the tool, because the switch is per area and
    a refusal that names something the screen does not show is a refusal with
    nowhere to go.
    """
    area = area_of(tool)
    spec = AREAS.get(area or "", {})
    return (f"that needs your permission first — it is in the "
            f"'{(area or '').replace('_', ' ')}' group, which covers "
            f"{spec.get('says', 'this')}. You can switch it on where the "
            f"session lists what it may touch, and off again afterwards.")
