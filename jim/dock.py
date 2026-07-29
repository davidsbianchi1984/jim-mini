"""The helper dock: the wrist's glances, cast into a pane inside the app.

The same idea as `qrme/dock.py`, and deliberately the same shape — a small pane
in the bottom corner of the app, no watch frame around it, tucked behind the
helper button until wanted. JIM-mini has thirty-six watch faces and the watch is
a **Pro** capability, so the people most in need of a glance without a wrist are
exactly the ones who do not have one.

**It shows, and it routes. It never acts**, for the reason QRME's gives and one
more that is specific here: the surfaces this floats over include a live alarm.
A control in a 168px box hovering beside the button that clears an escalation is
not a convenience, it is a mis-tap during the worst minute of somebody's week.

**But it is never silent about an alarm.** That is the one place this module
departs from QRME's. QRME's dock tucks itself away on a surface being broadcast,
because a pane pinned to the frame is inside every screenshot. The same rule
here would hide the thing a person most needs to see, so :data:`ALWAYS_SHOWN`
names the alarm face and it opens regardless — the dock may be tucked, hidden,
or on another face entirely, and an active alarm still surfaces it.

That is not a privacy compromise. An alarm belongs to the person holding the
phone, and JIM-mini has no broadcast surface to leak it into: nothing here
streams, and the screen-share case that drives QRME's rule does not exist in a
guardian app. Where the two products' reasoning genuinely differs, the rule
differs, rather than being copied because the module next door has one.

**It is still inside every screenshot**, so :data:`NEVER` holds the vault list —
journal entries, the medical record, guidance text, family members' names.
"""

from __future__ import annotations

import json

from . import db

CORNERS: dict[str, str] = {
    "bottom_right": "the default — under the right thumb",
    "bottom_left": "for a left-handed grip, or to uncover something",
}
DEFAULT_CORNER = "bottom_right"

STATES: dict[str, str] = {
    "hidden": "nothing in the corner at all",
    "handle": "the helper button only — tucked away",
    "open": "the pane, showing one face",
}
DEFAULT_STATE = "handle"

BOX = {"width": 168, "height": 132, "handle": 44, "inset": 16}

# The faces the pane can carry, and what each is for. Short on purpose: a
# guardian app's glance question is "is anything wrong", not "show me
# everything".
FACES: dict[str, str] = {
    "helper": "the guide — ask it anything, or let it show you around",
    "alarm": "an active alarm, and the way to accept or escalate it",
    "vitals": "the last reading, and whether it was believed",
    "agents": "the status lights and their counts — no agent names",
    "today": "what the Guardian has suggested today",
    "mic": "whether channel 2 is lent, and the way back",
    "careteam": "whether a joint care plan is waiting to be read — never "
                "its contents",
}
DEFAULT_FACE = "helper"

# The face that opens whatever the pane is set to. See the module note: the
# rule QRME uses would hide the one thing a person most needs to see.
ALWAYS_SHOWN: tuple[str, ...] = ("alarm",)

# What may never appear in the pane. A pane pinned to the frame is in every
# screenshot somebody takes and every photo somebody else takes of the screen.
NEVER: dict[str, str] = {
    "journal": "what somebody wrote about their own day is not a glance",
    "medical_record": "the record belongs behind an unlock, not in a corner",
    "guidance_text": "guidance is a conversation, and a fragment of one reads "
                     "worse than none",
    "family_names": "who is on somebody's escalation tree is theirs",
    "tokens": "nothing that authorises anything belongs on a captured surface",
}

# Faces that are about a particular thing rather than about the account.
PER_SURFACE: tuple[str, ...] = ("alarm",)

# Where the full screen for each face lives — the dock's routing half, and the
# table the assistant's directions read.
ROUTES: dict[str, dict] = {
    "helper": {"screen": 60, "path": "/guide", "title": "Guided Tour"},
    "alarm": {"screen": 13, "path": "/alarms", "title": "Alarm"},
    "vitals": {"screen": 4, "path": "/vitals", "title": "Vitals"},
    "agents": {"screen": 67, "path": "/agents", "title": "Agents"},
    "today": {"screen": 10, "path": "/today", "title": "Today"},
    "mic": {"screen": 65, "path": "/mic", "title": "Channel 2"},
    "careteam": {"screen": 86, "path": "/care-team", "title": "Care Team"},
}


class DockError(ValueError):
    """A dock that cannot be drawn. Text meant for a person."""


def vocabulary() -> dict:
    return {
        "faces": FACES,
        "corners": CORNERS,
        "states": STATES,
        "box": BOX,
        "never": NEVER,
        "always_shown": list(ALWAYS_SHOWN),
        "per_surface": list(PER_SURFACE),
        "routes": ROUTES,
        "acts": False,
    }


def route(face: str) -> dict:
    if face not in ROUTES:
        raise DockError(f"no such face {face!r}; one of {', '.join(FACES)}")
    return {"face": face, **ROUTES[face], "opens_dock_face": face}


def _check_face(face: str) -> None:
    if face not in FACES:
        raise DockError(f"no such face {face!r}; one of {', '.join(FACES)}")


def settings(user_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM dock_prefs WHERE user_id=?", (user_id,)).fetchone()
    if row is None:
        return {"user_id": user_id, "corner": DEFAULT_CORNER,
                "state": DEFAULT_STATE, "face": DEFAULT_FACE,
                "faces": list(FACES), "set": False}
    return {"user_id": user_id, "corner": row["corner"], "state": row["state"],
            "face": row["face"], "faces": json.loads(row["faces"]),
            "set": True}


def configure(user_id: str, corner: str | None = None,
              state: str | None = None, face: str | None = None,
              faces: list[str] | None = None) -> dict:
    now = settings(user_id)
    corner = now["corner"] if corner is None else corner
    state = now["state"] if state is None else state
    face = now["face"] if face is None else face
    chosen = list(now["faces"] if faces is None else faces)

    if corner not in CORNERS:
        raise DockError(
            f"the pane sits in a bottom corner — {', '.join(CORNERS)}")
    if state not in STATES:
        raise DockError(f"unknown state {state!r}; one of {', '.join(STATES)}")
    for f in chosen:
        _check_face(f)
    if not chosen:
        raise DockError("a pane with no faces is the helper button on its own "
                        "— set the state to 'handle' instead")
    _check_face(face)
    if face not in chosen:
        raise DockError(f"{face!r} is not one of the faces this dock carries")
    for must in ALWAYS_SHOWN:
        if must not in chosen:
            raise DockError(
                f"{must!r} cannot be removed from the pane — it is the face "
                "that appears when something is wrong, and a pane somebody "
                "configured out of the way months ago is not a decision they "
                "made about the day it fires")

    conn = db.connect()
    conn.execute(
        "INSERT INTO dock_prefs (user_id, corner, state, face, faces,"
        " updated_at) VALUES (?,?,?,?,?,?)"
        " ON CONFLICT (user_id) DO UPDATE SET corner=excluded.corner,"
        " state=excluded.state, face=excluded.face, faces=excluded.faces,"
        " updated_at=excluded.updated_at",
        (user_id, corner, state, face, json.dumps(chosen), db.utcnow()))
    conn.commit()
    return settings(user_id)


def opens_as(user_id: str, alarm_active: bool = False) -> dict:
    """The state the pane should draw in, here, right now.

    Where :data:`ALWAYS_SHOWN` is applied. The owner's preference is returned
    alongside as `wanted`, in the same shape QRME reports a tucked pane and
    `mic.py` reports a capped gain: a preference that was overridden is still
    theirs, and silently rewriting it would mean the settings screen and the
    pane disagreed about what was chosen.
    """
    now = settings(user_id)
    wanted = now["state"]
    if alarm_active:
        return {
            **now,
            "wanted": wanted,
            "state": "open",
            "face": "alarm",
            "forced": True,
            "why": "an alarm is active — the pane opens on it whatever it was "
                   "set to, and goes back afterwards",
        }
    return {**now, "wanted": wanted, "forced": False, "why": None}


def face(user_id: str, name: str, surface_id: str | None = None) -> dict:
    """One face, as the pane would draw it. Read-only by construction."""
    _check_face(name)
    if name in PER_SURFACE and not surface_id:
        raise DockError(
            f"the {name} face is about a particular one — tell it which")
    return {
        "face": name,
        "shows": FACES[name],
        "user_id": user_id,
        "surface_id": surface_id,
        "route": route(name),
        "acts": False,
        "box": BOX,
        "never": list(NEVER),
    }
