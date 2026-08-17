"""The session you leave running — JIM engaged, acting, and handing back.

## What this is

Until now there was one conversational door in this product, ``POST
/coach/{user_id}``, and it was a *turn*: you said something, JIM said
something, and nothing was left holding. Which model answered depended on
``PUT /model/{user_id}``, so "the online one" and "the offline one" were the
same route with a different provider behind it, and a person could not tell
them apart except by the amber banner when a turn degraded.

    asked     can you talk to it
    mattered  can you stay talking to it

An **engagement** is that missing thing. You open one, it stays open across
turns, and it ends when you sign off — not when you stop typing. Three
consequences, and each is the reason for a section below:

* while it is open, JIM can **do things** rather than describe them;
* every act it takes can be **taken back**;
* signing off is a **handover**, not a close — what the session was about
  goes into the offline store, and anything you named becomes something the
  Guardian watches for while you are gone.

## The reach, and why it is a list

An engaged session carries the person's own token, so it *could* call
anything they can call — including ``DELETE /data/{user_id}``, which ends
them. Nobody who says *sort my week out* means *and be free to erase me if
you misread it*.

So the reach is :data:`TOOLS`, written here, and every row names the route it
resolves to. A guard resolves each one against the app's own route table and
fails if it lands somewhere that is not this user's; a second guard fails if
any row touches the paths in :data:`NEVER`. Adding a row in a hurry cannot
widen the blast radius quietly, and the console renders the ``says`` lines so
*what can this thing do to me* has an answer somebody can finish reading.

## The undo trail

Every writing row declares its own inverse, as data, and there is no way to
add one that does not: ``test_every_act_can_be_taken_back`` reads the
registry. Two shapes cover everything here —

``remove``
    the act created a row; the inverse deletes it, with the new id read out
    of the answer the act returned.

``replace``
    the act overwrote a setting; the prior value is read **before** the act
    and replayed to the same door afterwards.

The trail is a table, not a log line: ``GET /engaged/{user_id}/acts`` lists
what was done and ``POST /engaged/{user_id}/acts/{act_id}/undo`` takes one
back. An agent that edits your medication schedule and then describes the
edit in prose is asking to be believed. One that lists the doors it went
through can be checked, and one that hands you the inverse can be refused
after the fact — which is the only kind of consent that survives being wrong.

### The one act that cannot be taken back, and why it is still here

``ask_specialist`` sends the person's own words to a QRME specialist — a
profile outside this product. Nothing can unsay that. It is in the list
because reaching a specialist was the thing this was for, and it is marked
``irreversible`` with the sentence a person reads before it happens, because
the alternative — quietly filing it under "acts" beside a journal entry that
deletes cleanly — would be a lie told by a data structure.

## What is never in the list

:data:`NEVER` is the carve-out, and it is enforced against the registry
rather than trusted to review. Emergencies, alarms, escalation, the vigil,
the crash watch, the beacon, the referral release, money movement,
membership, erasure. Two different reasons, both absolute:

* **The safety paths are not the agent's to drive.** An assistant that can
  raise an alarm can raise one wrongly, and this product's refusals promise
  in nine languages that emergency paths are never affected by anything.
* **Some doors are the person's alone.** A mandate is a standing
  authorization a human gave; an agent that could grant itself one has
  granted itself everything.

Neither is a check inside a handler. The agent cannot call what is not in
the list.

## What it is never told

The host. Not its name, not its paths, not its environment, not its sibling
services. :data:`SYSTEM` is the whole of what it knows about where it runs,
which is nothing, and a guard reads it — and every ``says`` line — for a
hostname, a filesystem path, an environment variable or a service name. The
obvious way to make an agent more capable is to tell it more about the
machine, and on this machine that is a map of somebody's clinical captures.
"""

from __future__ import annotations

import asyncio
import json
import re
import uuid
from urllib.parse import quote

import httpx

from . import audit, db, permits

# --------------------------------------------------------------------------- #
# The reach
# --------------------------------------------------------------------------- #

#: Path prefixes no row may ever resolve to, whatever it is called.
#:
#: Read by ``test_the_agent_cannot_reach_the_paths_that_are_never_its_to_reach``
#: against every route in :data:`TOOLS`. The list is prefixes rather than exact
#: paths on purpose: a new sub-route under ``/emergency`` is covered the day it
#: is written, without anybody remembering this file exists.
NEVER: tuple[str, ...] = (
    "/emergency",          # summoning help is not the assistant's to do
    "/users/{user_id}/alarms",
    "/c/{bid}/alarm",
    "/crash-watch",
    "/vigil",
    "/escalation-policy",
    "/users/{user_id}/beacons",
    "/users/{user_id}/referral",   # releasing a body to a clinician
    "/users/{user_id}/captures",   # photographs of somebody's body
    "/medical-id",
    # All of it. The mandate is a standing authorization a human gave, and an
    # agent that could grant itself one has granted itself everything; the
    # rest — accounts, links, statements, savings — is the material that
    # mandate operates on. Written as one prefix rather than five paths
    # because the next money route added is covered the day it is written.
    "/money/",
    "/data/",              # erasure
    "/memberships",
    "/waivers",
    "/continuity",
    "/self-profile",       # the synthetic self speaks as them
    "/robots",
    "/guardians",          # another person's child
    "/circle/{user_id}/messages",  # writing to another human as them
    "/community",
    "/social",
    "/settings/mail",
    "/voice/speak",
    "/apps/connector",
    "/auth/",
    "/password",
    "/signup",
    "/signin",
)

#: Everything an engaged session may do, and the door each one goes through.
#:
#: ``acts`` marks a row that changes something. Those must declare ``undo``
#: (or ``irreversible``), and they must go through a door that demands this
#: user's own token — a read need not, because the user in the path is bound
#: by :func:`call` and is never the model's to name.
#:
#: ``says`` is the sentence the console shows a person. It is written for
#: them, not for the model.
TOOLS: tuple[dict, ...] = (
    # ---- looking ---------------------------------------------------------
    {"name": "read_day", "acts": False,
     "route": ("GET", "/presence/{user_id}/day"),
     "says": "read how your day looks — what the Guardian has noticed"},
    {"name": "read_insights", "acts": False,
     "route": ("GET", "/insights/{user_id}"),
     "says": "read what it has noticed about your patterns"},
    {"name": "read_goals", "acts": False,
     "route": ("GET", "/goals/{user_id}"),
     "says": "read your goals and how far along they are"},
    {"name": "read_habits", "acts": False,
     "route": ("GET", "/habits/{user_id}"),
     "says": "read your habits and their streaks"},
    {"name": "read_journal", "acts": False,
     "route": ("GET", "/journal/{user_id}"),
     "says": "read your journal"},
    {"name": "read_meds", "acts": False,
     "route": ("GET", "/meds/{user_id}"),
     "says": "read your medication cabinet"},
    {"name": "read_adherence", "acts": False,
     "route": ("GET", "/meds/{user_id}/adherence"),
     "says": "read how your doses have been going"},
    {"name": "read_bands", "acts": False,
     "route": ("GET", "/bands/{user_id}"),
     "says": "read the personal bands your readings are judged against"},
    {"name": "read_schedule", "acts": False,
     "route": ("GET", "/schedule/{user_id}"),
     "says": "read what you have booked"},
    {"name": "read_care_team", "acts": False,
     "route": ("GET", "/users/{user_id}/care-team"),
     "says": "read who is on your care team"},
    {"name": "read_coach_history", "acts": False,
     "route": ("GET", "/coach/{user_id}"),
     "says": "read what you and the coach have talked about before"},
    {"name": "read_specialists", "acts": False,
     "route": ("GET", "/specialists"),
     "says": "look up which specialists cover which areas"},

    # ---- doing, each with the way back -----------------------------------
    {"name": "write_journal", "acts": True,
     "route": ("POST", "/journal/{user_id}"),
     "says": "write something into your journal",
     "undo": {"kind": "remove",
              "route": ("DELETE", "/journal/{user_id}/{entry_id}"),
              "path_from": {"entry_id": "id"}}},
    {"name": "note_checkin", "acts": True,
     "route": ("POST", "/checkin/{user_id}"),
     "says": "record a check-in for you — mood, energy, stress, a note",
     "undo": {"kind": "remove",
              "route": ("DELETE", "/checkin/{user_id}/{checkin_id}"),
              "path_from": {"checkin_id": "id"}}},
    {"name": "set_goal", "acts": True,
     "route": ("POST", "/goals/{user_id}"),
     "says": "set you a goal",
     "undo": {"kind": "remove",
              "route": ("DELETE", "/goals/{user_id}/{goal_id}"),
              "path_from": {"goal_id": "id"}}},
    {"name": "move_goal", "acts": True,
     "route": ("PATCH", "/goals/{user_id}/{goal_id}"),
     "says": "move a goal along, or park it",
     "undo": {"kind": "replace",
              "before": ("GET", "/goals/{user_id}"),
              "select": "goal_id",
              "fields": ("progress", "status")}},
    {"name": "start_habit", "acts": True,
     "route": ("POST", "/habits/{user_id}"),
     "says": "start you a habit to keep",
     "undo": {"kind": "remove",
              "route": ("DELETE", "/habits/{user_id}/{habit_id}"),
              "path_from": {"habit_id": "id"}}},
    {"name": "log_habit", "acts": True,
     "route": ("POST", "/habits/{user_id}/{habit_id}/log"),
     "says": "tick off a habit for today",
     "undo": {"kind": "remove",
              "route": ("DELETE", "/habits/{user_id}/{habit_id}/log/{day}"),
              "path_from": {"habit_id": "habit_id", "day": "day"}}},
    {"name": "set_bearing", "acts": True,
     "route": ("PUT", "/presence/{user_id}/bearing"),
     "says": "change how it talks to you — companion or professional",
     "undo": {"kind": "replace",
              "before": ("GET", "/presence/{user_id}/bearing"),
              "fields": ("bearing",)}},
    {"name": "set_language", "acts": True,
     "route": ("PUT", "/language/{user_id}"),
     "says": "change the language it answers you in",
     "undo": {"kind": "replace",
              "before": ("GET", "/language/{user_id}"),
              "fields": ("language",)}},
    {"name": "set_model", "acts": True,
     "route": ("PUT", "/model/{user_id}"),
     "says": "change which model answers you",
     "undo": {"kind": "replace",
              "before": ("GET", "/model/{user_id}"),
              "fields": ("provider",)}},
    {"name": "set_band", "acts": True,
     "route": ("PUT", "/bands/{user_id}/{metric}"),
     "says": "adjust one of your personal bands",
     "undo": {"kind": "replace",
              "before": ("GET", "/bands/{user_id}"),
              "select": "metric",
              "fields": ("low", "high", "source")}},
    {"name": "add_med", "acts": True,
     "route": ("POST", "/meds/{user_id}"),
     "says": "add a medication to your cabinet",
     "undo": {"kind": "remove",
              "route": ("DELETE", "/meds/{user_id}/{med_id}"),
              "path_from": {"med_id": "id"}}},
    {"name": "book", "acts": True,
     "route": ("POST", "/schedule/{user_id}"),
     "says": "book something into your schedule",
     "undo": {"kind": "remove",
              "route": ("DELETE", "/schedule/{user_id}/{appointment_id}"),
              "path_from": {"appointment_id": "id"}}},
    {"name": "watch_for", "acts": True,
     "route": ("POST", "/engaged/{user_id}/watches"),
     "says": "put something on the Guardian's list to watch for while you "
             "are away",
     "undo": {"kind": "remove",
              "route": ("DELETE", "/engaged/{user_id}/watches/{watch_id}"),
              "path_from": {"watch_id": "id"}}},

    # ---- the switches, said out loud --------------------------------------
    #
    # These three exist because the menus that hold them were reported as
    # "awful user unfriendly if you don't know what you're doing". Every one
    # of them was already a screen; none of them was a sentence. "Speak
    # through my earbuds, not the speaker" is a thing somebody can say and
    # could not, until now, be *told to*.
    #
    # The two that widen what the Guardian sees or switch parts of the product
    # on and off need their own yes first (`permits.AREAS`); the surface does
    # not, because it belongs to the same "how it speaks to you" group a
    # person already approved by opening the session.
    {"name": "set_surface", "acts": True,
     "route": ("PUT", "/presence/{user_id}/surface"),
     "says": "change which device it speaks through — earbuds, a watch, a "
             "speaker in the room",
     "undo": {"kind": "replace",
              "before": ("GET", "/presence/{user_id}/surfaces"),
              "fields": ("chosen",),
              "as": {"chosen": "speaks_on"}}},
    {"name": "set_source", "acts": True,
     "route": ("PUT", "/sources/{user_id}"),
     "says": "switch one of your sources on or off — changing what the "
             "Guardian is allowed to see",
     "undo": {"kind": "replace",
              "before": ("GET", "/sources/{user_id}"),
              "select": "source",
              "fields": ("source", "consented")}},
    {"name": "set_feature", "acts": True,
     "route": ("PUT", "/circle/{user_id}/features"),
     "says": "switch a part of the product on or off for your account",
     "undo": {"kind": "replace",
              "before": ("GET", "/circle/{user_id}"),
              "in": ("features", "feature"),
              "fields": ("feature", "enabled")}},

    # ---- the two that leave ----------------------------------------------
    # Both reach outside this host, and they reach differently: one carries
    # this person's own words to another person, the other carries a general
    # topic to a model and brings back something the offline coach keeps.
    {"name": "speak_to_their_guardian", "acts": True,
     "route": ("POST", "/liaisons/{user_id}/{link_id}/said"),
     "says": "say something about you to somebody else's guardian",
     "irreversible": "engaged.cannot_unsay"},
    {"name": "study_unattended", "acts": True,
     "route": ("POST", "/errands/{user_id}"),
     "says": "go and study what the coach could not answer, on its own",
     "irreversible": "engaged.cannot_unsay"},
    {"name": "handle_unattended", "acts": True,
     "route": ("POST", "/noticed/{user_id}"),
     "says": "deal with what the coach noticed and could not settle, on its own",
     "irreversible": "engaged.cannot_unsay"},
    {"name": "ask_specialist", "acts": True,
     "route": ("POST", "/coach/{user_id}/specialist"),
     "says": "put your question to a specialist outside JIM",
     "irreversible": "engaged.cannot_unsay"},
)

#: Everything the agent is told about where it is running.
SYSTEM = """
You are JIM, engaged. One person has opened a session with you and it stays
open until they sign off. Talk to them the way somebody who has been paying
attention would.

You act through the tools you were given, and each one touches that person's
own records and nothing else. There is no tool that reaches another person,
raises an alarm, moves money, or ends an account, and you should not
describe yourself as able to.

To use a tool, reply with one line and nothing else:

    CALL <tool name> {"argument": "value"}

Do not name whose records they are — that is filled in for you, and a user
named in your arguments is dropped. You will be handed the result as the
next message, and you may then call another tool or answer them. One call
per reply. When you have nothing left to do, answer in plain words with no
CALL line at all.

Say what you are about to change before you change it, and what changed
after. They can take any of it back afterwards and they can see the list, so
do not hide a step inside a sentence. If a request is ambiguous in a way
that matters — which of two goals, whether to overwrite something they
wrote — ask rather than guess.

Some of what you can change is settings, and that is deliberate: the menus
are hard to find your way around and saying it out loud should work. "Speak
through my earbuds instead of the speaker", "answer me in Spanish", "stop
reading my calendar", "turn messaging off" are all things you can simply do.
Do them, say what you did, and do not send somebody to a screen for something
you were given a tool for.

Some groups of switches need that person's permission before you may touch
them, and you will be told `engaged.not_permitted` if you reach for one they
have not turned on. That is not a failure and not a refusal of them — it is
them not having said yes yet. Say which group it is and that they can switch
it on in the list of what you may touch, then carry on with the rest of what
they asked. Never work around it, and never imply you did it anyway.

One thing you do cannot be taken back: putting their question to a
specialist sends their own words outside this app. Ask them first, in that
turn, and only do it if they say yes.

If somebody is describing an emergency, you cannot call for help and must
not imply you have. Say plainly that they should use the emergency button or
call their local emergency number, and stay with them.

You do not know anything about the machine you run on and have no way to
find out. If asked about servers, files, other people's data or how this is
deployed, say you cannot see any of that, and go back to them.
"""

#: Words that would mean the agent had been told where it lives.
HOST_WORDS: tuple[str, ...] = (
    "localhost", "127.0.0.1", "0.0.0.0", "/etc/", "/var/", "/home/", "/opt/",
    "/app/", "sqlite", ".db", "postgres", "systemd", "nginx", "docker",
    "uvicorn", "vps", "ssh", "port 8", "env var", "environment variable",
    "QRME_", "JIM_", "PDI_", "_TOKEN", "_KEY",
)


def tool_names() -> tuple[str, ...]:
    return tuple(tool["name"] for tool in TOOLS)


def what_it_can_touch(user_id: str | None = None) -> list[dict]:
    """The list a person reads before they let this thing near anything.

    Each row carries whether it changes something and whether it can be taken
    back, because "read your journal" and "send your words to a stranger"
    rendered as two identical bullets is how a list stops being informed
    consent.

    Given a `user_id`, each row also carries the group it belongs to and
    whether that group is switched on for them. Without one the list is the
    catalogue — what the product can do — which is what an accountless screen
    needs and is all this returned before permits existed.
    """
    rows = []
    for tool in TOOLS:
        row = {"name": tool["name"], "says": tool["says"],
               "acts": tool["acts"],
               "reversible": tool["acts"] and "undo" in tool,
               "irreversible_because": tool.get("irreversible"),
               "area": permits.area_of(tool["name"])}
        if user_id is not None:
            row["permitted"] = permits.may(user_id, tool["name"])
        rows.append(row)
    return rows


def mentions_the_host(text: str) -> list[str]:
    """Any word in `text` that would tell the agent where it is running."""
    lowered = (text or "").lower()
    return sorted({word for word in HOST_WORDS if word.lower() in lowered})


def tool(name: str) -> dict:
    for row in TOOLS:
        if row["name"] == name:
            return row
    raise KeyError(name)


_NAME = re.compile(r"^[a-z_]{1,40}$")


def is_a_tool(name: str) -> bool:
    return bool(_NAME.match(name or "")) and name in tool_names()


#: Every refusal this module raises: the status it deserves and the sentence
#: a person reads. Keyed rather than raised as prose, because the same
#: refusals are handed to two different readers — the model, which is told the
#: key and stops asking, and a person, who is told the sentence in their own
#: language through ``i18n.refuse``.
REFUSALS: dict[str, tuple[int, str]] = {
    "engaged.unknown_tool": (
        422, "that is not something an engaged session can do"),
    "engaged.not_permitted": (
        403, "that group of switches has not been turned on for this session "
             "— it is in the list of what it may touch, and switching it on "
             "there is all it needs"),
    "engaged.unreadable_call": (
        422, "the model asked for a tool in a shape this could not read"),
    "engaged.missing_argument": (
        422, "that needs something it was not given"),
    "engaged.tool_failed": (
        502, "that did not go through, and nothing was changed"),
    "engaged.said_nothing": (422, "there was nothing in that message"),
    "engaged.not_engaged": (
        409, "no session is open — engage first, or you are talking to the "
             "coach a turn at a time"),
    "engaged.no_such_act": (404, "no such act on this account"),
    "engaged.already_undone": (409, "that one has already been taken back"),
    "engaged.cannot_be_undone": (
        409, "that one cannot be taken back — it left this app, and nothing "
             "here can unsay it"),
    "engaged.undo_failed": (
        409, "taking that back did not work, so it is still listed as done"),
    "engaged.no_such_watch": (404, "nothing is being watched under that name"),
    "engaged.nothing_to_watch": (422, "name the thing to watch for"),
    "engaged.watching_enough": (
        409, "the watch list is full — clear one before adding another"),
    "engaged.cannot_unsay": (
        409, "a specialist outside JIM has read this; nothing here can "
             "unsay it"),
    "engaged.acted_enough": (
        409, "this session has changed enough for one sitting — sign off and "
             "start another"),
    "engaged.too_many_steps": (
        409, "it kept reaching for things and never answered"),
    "engaged.needs_the_online_model": (
        409, "an engaged session needs the online model — the offline one "
             "can answer you, but it cannot do anything for you. Nothing "
             "was changed."),
}


class EngagedError(Exception):
    """A refusal, as a key.

    ``str(exc)`` is the key, which is what the model is handed and what the
    steps list records. ``status`` and ``message`` are what the route answers
    with, translated on the way out like every other refusal in this product.
    """

    def __init__(self, key: str):
        self.key = key
        self.status, self.message = REFUSALS.get(
            key, (409, "that is not something an engaged session can do"))
        super().__init__(key)


# --------------------------------------------------------------------------- #
# Ceilings
# --------------------------------------------------------------------------- #

#: How many tools it may reach for before it has to say something.
STEPS = 6

#: How much of a tool's answer is handed back to the model. A journal or a
#: medication cabinet is as long as somebody's life has been.
RESULT_BYTES = 4 * 1024

#: How much of the session the model is shown. An engagement is open-ended by
#: design, so this is the ceiling that keeps an open-ended thing affordable.
HISTORY_TURNS = 40
SAID_CHARS = 4000

#: How many acts one engagement may take. Not a cost ceiling — a blast
#: radius. Somebody skimming an undo trail of four hundred rows is not
#: reviewing anything.
ACTS_PER_ENGAGEMENT = 60

_PLACEHOLDER = re.compile(r"\{([a-z_]+)\}")
_CALL = re.compile(r"^\s*CALL\s+([a-z_]{1,40})\s*(\{.*\})?\s*$",
                   re.MULTILINE | re.DOTALL)


def wants_a_tool(text: str) -> tuple[str, dict] | None:
    """The model's reply, read as a tool call — or None, meaning it answered.

    Deliberately strict. A reply that is *mostly* prose with the word CALL in
    it is prose: an agent that acts on a sentence it merely appears in is one
    that acts on a sentence somebody else wrote into a journal it was reading.
    """
    match = _CALL.match((text or "").strip())
    if not match:
        return None
    name, blob = match.group(1), match.group(2)
    try:
        arguments = json.loads(blob) if blob else {}
    except ValueError:
        arguments = None
    if not isinstance(arguments, dict):
        raise EngagedError("engaged.unreadable_call")
    return name, arguments


# --------------------------------------------------------------------------- #
# Making the request
# --------------------------------------------------------------------------- #

def _fill(template: str, user_id: str, args: dict) -> str:
    """Resolve a route template, consuming path arguments out of ``args``.

    ``user_id`` comes from the session and is substituted here. The model is
    never asked for it and cannot supply it; one named in ``args`` is dropped
    by the caller before this runs.
    """
    path = template.replace("{user_id}", quote(str(user_id), safe=""))
    for slot in _PLACEHOLDER.findall(template):
        if slot == "user_id":
            continue
        value = args.pop(slot, None)
        if value is None or not str(value).strip():
            raise EngagedError("engaged.missing_argument")
        path = path.replace("{%s}" % slot, quote(str(value), safe=""))
    return path


def _request(app, method: str, path: str, body: dict | None,
             headers: dict) -> tuple[int, object]:
    """The request itself, in-process — the same transport the suite gateway
    uses for a mounted app. Nothing leaves the host, and no port has to be
    guessable from inside a request."""
    async def go():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport,
                                     base_url="http://engaged") as client:
            return await client.request(method, path, json=body,
                                        headers=headers, timeout=30)

    try:
        response = asyncio.run(go())
    except Exception as exc:                      # noqa: BLE001
        # The exception's own text is not handed on. It is written for an
        # operator reading a log, and this one is read by a model that will
        # repeat it to whoever is driving.
        raise EngagedError("engaged.tool_failed") from exc
    try:
        return response.status_code, response.json()
    except ValueError:
        return response.status_code, None


def _select(answer, key: str, value):
    """Pick one row out of a list-shaped read, by its id."""
    if isinstance(answer, dict):
        for candidate in answer.values():
            if isinstance(candidate, list):
                answer = candidate
                break
    if not isinstance(answer, list):
        return answer if isinstance(answer, dict) else None
    for row in answer:
        if isinstance(row, dict) and str(row.get("id", row.get(key))) == str(value):
            return row
    return None


def _inverse(row: dict, *, user_id: str, path_args: dict, body: dict,
             answer, before) -> dict | None:
    """The request that would take this act back, as data.

    Built at act time rather than at undo time, because the material it needs
    — the id the write returned, the value it overwrote — is only knowable
    now. Stored on the act; replayed verbatim later.
    """
    spec = row.get("undo")
    if spec is None:
        return None

    if spec["kind"] == "remove":
        method, template = spec["route"]
        args = {}
        for slot, source in spec["path_from"].items():
            value = None
            if isinstance(answer, dict):
                value = answer.get(source)
            if value is None:
                value = path_args.get(source, body.get(source))
            if value is None:
                return None
            args[slot] = value
        return {"method": method, "path": _fill(template, user_id, args),
                "body": None}

    # replace: the prior state, replayed to the same door
    #
    # Three shapes of "the prior state", because three shapes of read exist in
    # this API and an undo that only handles one of them is an undo that
    # quietly stops existing for the other two:
    #
    #   whole      the read *is* the setting — `{"bearing": "companion"}`
    #   select     a list of rows, one of which is the setting
    #   in         a map, one key of which is the setting
    #
    # `select` reads its key from the path *or the body*. `/sources/{user_id}`
    # names the source in the body and has no second path slot, so a lookup
    # that only searched the path found nothing and the act came back
    # irreversible — which is worse than failing, because the act still
    # happened and the list said it could not be taken back.
    method, template = row["route"]
    prior = before
    if spec.get("select"):
        key = spec["select"]
        prior = _select(before, key, path_args.get(key, body.get(key)))
    elif spec.get("in"):
        where, names = spec["in"]
        name = body.get(names)
        table = before.get(where) if isinstance(before, dict) else None
        if not isinstance(table, dict) or name not in table:
            return None
        prior = {names: name, spec["fields"][1]: table[name]}
    if not isinstance(prior, dict):
        return None
    payload = {field: prior[field] for field in spec["fields"]
               if field in prior}
    # A read and a write can name the same setting differently. `surfaces`
    # answers with `chosen` and the door takes `speaks_on` — deliberately, so
    # that "surface" does not mean two things across the three products — and
    # replaying `chosen` at a door expecting `speaks_on` is a 422 at undo
    # time, discovered by somebody trying to take something back.
    payload = {spec.get("as", {}).get(k, k): v for k, v in payload.items()}
    if not payload:
        return None
    return {"method": method, "path": _fill(template, user_id, dict(path_args)),
            "body": payload}


def call(name: str, arguments: dict, *, app, user_id: str,
         authorization: str | None) -> dict:
    """Run one tool, through the app's own door — and record the way back.

    Not by calling the module behind the route: by making the request. The
    door is where the token is demanded, where the plan is checked, where the
    offline guarantee is enforced and where the refusal is translated, and an
    agent that reached past all of that to the function underneath would be a
    second, weaker copy of the product.

    The caller's own credential is forwarded rather than a token minted here,
    so the reach is exactly the reach of whoever is driving it: no more, and
    — the part that matters when a session has expired — no longer.

    The permit check sits *above* the request rather than inside the door,
    because it is not the door's question. The door asks whether this token
    may write to this account; this asks whether this person has told their
    own agent it may throw this particular switch on their behalf. Somebody
    with every credential in the world still has not said yes to that, and
    somebody who says no is not losing an ability — they are declining to
    delegate one.
    """
    if not is_a_tool(name):
        raise EngagedError("engaged.unknown_tool")
    if not permits.may(user_id, name):
        raise EngagedError("engaged.not_permitted")
    row = tool(name)
    method, template = row["route"]

    args = dict(arguments or {})
    args.pop("user_id", None)
    consumed = {slot: args.get(slot) for slot in _PLACEHOLDER.findall(template)
                if slot != "user_id"}
    path = _fill(template, user_id, args)

    headers = {"authorization": authorization} if authorization else {}
    body = None if method in ("GET", "DELETE") else args

    # A `replace` cannot be inverted after the fact — the value it overwrote
    # is gone. So the prior state is read first, through the same door, and
    # the act only becomes reversible if that read succeeded.
    before = None
    if row["acts"] and row.get("undo", {}).get("kind") == "replace":
        read_method, read_template = row["undo"]["before"]
        _, before = _request(app, read_method,
                             _fill(read_template, user_id, {}), None, headers)

    status, answer = _request(app, method, path, body, headers)

    undo = None
    if row["acts"] and 200 <= status < 300:
        undo = _inverse(row, user_id=user_id, path_args=consumed,
                        body=body or {}, answer=answer, before=before)
    return {"tool": name, "status": status, "answer": answer,
            "acts": row["acts"], "undo": undo,
            "irreversible": row.get("irreversible")}


def a_result_for_the_model(result: dict) -> str:
    """What the model is told happened. Capped, because a journal and a
    medication cabinet are both as long as somebody wants them to be."""
    blob = json.dumps(result.get("answer"), ensure_ascii=False, default=str)
    if len(blob.encode()) > RESULT_BYTES:
        blob = blob.encode()[:RESULT_BYTES].decode(errors="ignore") + "…"
    return f"RESULT {result['tool']} {result['status']}\n{blob}"


# --------------------------------------------------------------------------- #
# The session
# --------------------------------------------------------------------------- #

def open_session(user_id: str, area: str = "personal_growth") -> dict:
    """Open an engagement, or hand back the one already open.

    Idempotent on purpose. "Engaged" is a state a person is in, not a resource
    they can accumulate: a console that reopens on every mount, or a phone
    coming back from the background, must not leave a trail of half-sessions
    each holding part of a conversation.
    """
    existing = current(user_id)
    if existing is not None:
        return existing
    conn = db.connect()
    engagement_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO engagements (id, user_id, area, opened_at) "
        "VALUES (?,?,?,?)", (engagement_id, user_id, area, db.utcnow()))
    conn.commit()
    return current(user_id)


def current(user_id: str) -> dict | None:
    """The open engagement, with its turns — or None when nobody is engaged."""
    row = db.connect().execute(
        "SELECT * FROM engagements WHERE user_id=? AND signed_off_at IS NULL"
        " ORDER BY opened_at DESC LIMIT 1", (user_id,)).fetchone()
    if row is None:
        return None
    return {"id": row["id"], "user_id": row["user_id"], "area": row["area"],
            "opened_at": row["opened_at"], "engaged": True,
            "turns": turns(row["id"]), "acted": acts(row["id"])}


def turns(engagement_id: str) -> list[dict]:
    return [{"role": r["role"], "content": r["content"],
             "created_at": r["created_at"]}
            for r in db.connect().execute(
                "SELECT role, content, created_at FROM engagement_turns"
                " WHERE engagement_id=? ORDER BY seq", (engagement_id,))]


def _record_turn(engagement_id: str, role: str, content: str) -> None:
    conn = db.connect()
    seq = conn.execute(
        "SELECT COALESCE(MAX(seq), 0) + 1 AS n FROM engagement_turns"
        " WHERE engagement_id=?", (engagement_id,)).fetchone()["n"]
    conn.execute(
        "INSERT INTO engagement_turns (engagement_id, seq, role, content,"
        " created_at) VALUES (?,?,?,?,?)",
        (engagement_id, seq, role, content[:SAID_CHARS], db.utcnow()))
    conn.commit()


def acts(engagement_id: str) -> list[dict]:
    """The undo trail for one engagement, newest last."""
    rows = db.connect().execute(
        "SELECT * FROM engagement_acts WHERE engagement_id=? ORDER BY rowid",
        (engagement_id,)).fetchall()
    return [_act_row(r) for r in rows]


def _act_row(r) -> dict:
    return {"id": r["id"], "tool": r["tool"], "says": r["says"],
            "answered": r["status"], "created_at": r["created_at"],
            "undone_at": r["undone_at"],
            "reversible": bool(r["undo"]) and r["undone_at"] is None,
            "irreversible_because": r["irreversible"]}


def _record_act(engagement_id: str, user_id: str, result: dict) -> None:
    row = tool(result["tool"])
    db.connect().execute(
        "INSERT INTO engagement_acts (id, engagement_id, user_id, tool, says,"
        " status, undo, irreversible, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        (str(uuid.uuid4()), engagement_id, user_id, result["tool"],
         row["says"], result["status"],
         json.dumps(result["undo"]) if result["undo"] else None,
         result.get("irreversible"), db.utcnow()))
    db.connect().commit()
    audit.record("engaged.act", user_id=user_id, ref=result["tool"])


def act_count(engagement_id: str) -> int:
    return db.connect().execute(
        "SELECT COUNT(*) AS n FROM engagement_acts WHERE engagement_id=?",
        (engagement_id,)).fetchone()["n"]


def undo(user_id: str, act_id: str, *, app,
         authorization: str | None) -> dict:
    """Take one act back, through the door that would have undone it by hand.

    Scoped to the user in the path rather than to the act's own row, so an
    act id guessed from somewhere else resolves to nothing. Replays the
    inverse recorded at act time; a replay that fails is reported as a
    failure rather than marked undone, because an undo trail that lies is
    worse than none.
    """
    row = db.connect().execute(
        "SELECT * FROM engagement_acts WHERE id=? AND user_id=?",
        (act_id, user_id)).fetchone()
    if row is None:
        raise EngagedError("engaged.no_such_act")
    if row["undone_at"] is not None:
        raise EngagedError("engaged.already_undone")
    if not row["undo"]:
        raise EngagedError("engaged.cannot_be_undone")

    spec = json.loads(row["undo"])
    headers = {"authorization": authorization} if authorization else {}
    status, answer = _request(app, spec["method"], spec["path"],
                              spec.get("body"), headers)
    if not 200 <= status < 300:
        raise EngagedError("engaged.undo_failed")
    conn = db.connect()
    conn.execute("UPDATE engagement_acts SET undone_at=? WHERE id=?",
                 (db.utcnow(), act_id))
    conn.commit()
    audit.record("engaged.undo", user_id=user_id, ref=row["tool"])
    return {"act_id": act_id, "undone": True, "answered": status,
            "tool": row["tool"], "says": row["says"]}


# --------------------------------------------------------------------------- #
# Standing watches — what the offline Guardian keeps for you
# --------------------------------------------------------------------------- #

#: How many things one person may have on the watch list. A Guardian watching
#: for forty things is watching for nothing, and the point of the list is that
#: it changes what gets raised.
WATCH_CEILING = 12


def watch_for(user_id: str, topic: str, area: str | None = None,
              engagement_id: str | None = None) -> dict:
    topic = (topic or "").strip()[:200]
    if not topic:
        raise EngagedError("engaged.nothing_to_watch")
    open_watches = watches(user_id)
    if len(open_watches) >= WATCH_CEILING:
        raise EngagedError("engaged.watching_enough")
    for existing in open_watches:
        if existing["topic"].lower() == topic.lower():
            return existing
    watch_id = str(uuid.uuid4())
    conn = db.connect()
    conn.execute(
        "INSERT INTO standing_watches (id, user_id, engagement_id, topic,"
        " area, created_at) VALUES (?,?,?,?,?,?)",
        (watch_id, user_id, engagement_id, topic, area, db.utcnow()))
    conn.commit()
    return watch(user_id, watch_id)


def watch(user_id: str, watch_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM standing_watches WHERE id=? AND user_id=?",
        (watch_id, user_id)).fetchone()
    return _watch_row(row) if row else None


def _watch_row(r) -> dict:
    return {"id": r["id"], "topic": r["topic"], "area": r["area"],
            "created_at": r["created_at"], "cleared_at": r["cleared_at"],
            "engagement_id": r["engagement_id"]}


def watches(user_id: str) -> list[dict]:
    """What the Guardian is holding on to while this person is away."""
    return [_watch_row(r) for r in db.connect().execute(
        "SELECT * FROM standing_watches WHERE user_id=? AND cleared_at IS NULL"
        " ORDER BY created_at", (user_id,))]


def clear_watch(user_id: str, watch_id: str) -> dict:
    conn = db.connect()
    row = conn.execute("SELECT * FROM standing_watches WHERE id=? AND user_id=?",
                       (watch_id, user_id)).fetchone()
    if row is None:
        raise EngagedError("engaged.no_such_watch")
    conn.execute("UPDATE standing_watches SET cleared_at=? WHERE id=?",
                 (db.utcnow(), watch_id))
    conn.commit()
    return {"watch_id": watch_id, "cleared": True, "topic": row["topic"]}


def watch_lines(user_id: str) -> list[str]:
    """The watch list as context for the offline coach.

    This is the whole point of the handover: the sentences a person said to
    the online model while they were engaged become sentences the offline one
    is holding after they have gone. Bounded and quoted rather than
    instructed — the coach is told what they are carrying, not told what to
    conclude from it.
    """
    rows = watches(user_id)
    if not rows:
        return []
    lines = ["they asked you to keep an eye on these while they were away:"]
    lines += [f"  — {row['topic']}" for row in rows[:6]]
    return lines


# --------------------------------------------------------------------------- #
# Signing off
# --------------------------------------------------------------------------- #

def sign_off(user_id: str, *, topics: list[str] | None = None) -> dict:
    """End the engagement and hand it to whoever is on afterwards.

    Three things happen, and the order matters: the session closes, what it
    was about is deposited into the store the offline stack predicts from
    (``jim/pipeline.py`` — the same path a paid coach turn already takes), and
    anything named becomes a standing watch.

    A person who signs off has not stopped being looked after. That sentence
    is the feature; this function is where it is true.
    """
    session = current(user_id)
    if session is None:
        raise EngagedError("engaged.not_engaged")

    conn = db.connect()
    conn.execute("UPDATE engagements SET signed_off_at=? WHERE id=?",
                 (db.utcnow(), session["id"]))
    conn.commit()

    said = [t["content"] for t in session["turns"] if t["role"] == "user"]
    deposited = 0
    if said:
        from . import pipeline
        answered = [t["content"] for t in session["turns"]
                    if t["role"] == "assistant"]
        if answered:
            try:
                pipeline.deposit(user_id, session["area"], said[-1],
                                 answered[-1], "engaged", "engaged")
                deposited = 1
            except Exception:                      # noqa: BLE001
                # A store that would not take the deposit must not cost
                # somebody their sign-off. The session is already closed.
                deposited = 0

    kept = []
    for topic in (topics or [])[:WATCH_CEILING]:
        try:
            kept.append(watch_for(user_id, topic, session["area"],
                                  session["id"]))
        except EngagedError:
            break

    return {"engagement_id": session["id"], "signed_off": True,
            "deposited": deposited, "watches": kept or watches(user_id),
            "acted": session["acted"]}


# --------------------------------------------------------------------------- #
# One turn
# --------------------------------------------------------------------------- #

def _transcript(rows: list[dict], said: str) -> str:
    """The session, rendered for a provider whose door takes one string.

    ``llm.Provider.generate`` is ``(system, user)`` because every other caller
    in this product asks one question. Flattening here rather than widening
    that signature keeps eight providers unchanged for one caller's benefit.
    """
    lines = []
    for row in rows[-HISTORY_TURNS:]:
        who = "Them" if row["role"] == "user" else "You"
        lines.append(f"{who}: {str(row.get('content', ''))[:SAID_CHARS]}")
    # Only on the first step of a turn. After a tool call the last thing said
    # is that tool's result, already in `rows`, and appending an empty `Them:`
    # would put a blank line at exactly the point the model is deciding what
    # to do next.
    if said:
        lines.append(f"Them: {said}")
    return "\n".join(lines)


def converse(user_id: str, said: str, *, app, authorization: str | None,
             cloud=None) -> dict:
    """One turn of an engaged session: what they asked, what it did, what it
    said — and, for each act, whether it can be taken back.

    The transcript is kept here rather than by the console, which is the
    opposite of the Studio agent in the sibling product and deliberately so:
    a session you are told stays open until you sign off must survive the app
    being closed, and one held in a browser tab does not.
    """
    from . import i18n, llm

    said = (said or "").strip()[:SAID_CHARS]
    if not said:
        raise EngagedError("engaged.said_nothing")

    session = current(user_id)
    if session is None:
        raise EngagedError("engaged.not_engaged")
    engagement_id = session["id"]

    system = SYSTEM + i18n.directive(i18n.effective_language(user_id))
    watching = watch_lines(user_id)
    if watching:
        system += "\n" + "\n".join(watching)

    _record_turn(engagement_id, "user", said)
    history = list(session["turns"])

    steps: list[dict] = []
    reply, stopped = "", None
    for _ in range(STEPS):
        generated = llm.generate_for_user(
            user_id, system, _transcript(history, said), cloud=cloud)
        text = generated["text"]

        # The one place this surface differs from the coach, and it has to.
        #
        # `coach.reply` degrades gracefully: when the stub answers, the
        # offline pipeline takes over and produces something genuinely
        # useful from the curated pack. That is right for a screen whose
        # job is to *say* something.
        #
        # This screen's job is to *do* something, and the offline stub
        # cannot ask for a tool. Left to fall through, an engaged session on
        # a box with no key would answer in canned prose, take no action,
        # and look exactly like one that had considered the request and
        # decided against it.
        #
        #     asked     did the turn come back with text
        #     mattered  did the model that can act answer it
        #
        # So it stops and says so. The banner names who answered and why,
        # the session stays open, and nothing was changed.
        if generated["provider"] == "stub" or generated.get("degraded"):
            stopped = "engaged.needs_the_online_model"
            break

        try:
            wanted = wants_a_tool(text)
        except EngagedError as exc:
            steps.append({"tool": None, "refused": str(exc)})
            break
        if wanted is None:
            reply = text.strip()
            break
        name, arguments = wanted
        if act_count(engagement_id) >= ACTS_PER_ENGAGEMENT:
            stopped = "engaged.acted_enough"
            break
        try:
            result = call(name, arguments, app=app, user_id=user_id,
                          authorization=authorization)
        except EngagedError as exc:
            # A refused call is a turn in the conversation, not the end of
            # one: it asked for something it does not have, and being told so
            # is how it stops asking.
            steps.append({"tool": name, "answered": None, "refused": str(exc)})
            history += [{"role": "assistant", "content": text},
                        {"role": "user", "content": f"REFUSED {exc}"}]
            said = ""
            continue
        # Only a call that *changed* something goes on the trail. A refused
        # write did nothing, and a row for it would carry an undo button that
        # deletes a record which was never created — at best a 404 reported
        # as "undo failed", at worst somebody else's row of the same shape.
        if result["acts"] and 200 <= result["status"] < 300:
            _record_act(engagement_id, user_id, result)
        steps.append({"tool": name, "answered": result["status"],
                      "says": tool(name)["says"], "acts": result["acts"],
                      "reversible": bool(result["undo"]),
                      "irreversible_because": result.get("irreversible")})
        history += [{"role": "assistant", "content": text},
                    {"role": "user", "content": a_result_for_the_model(result)}]
        said = ""
    else:
        stopped = "engaged.too_many_steps"

    if reply:
        _record_turn(engagement_id, "assistant", reply)
    # `did` rather than `acted`, and `watches` rather than `watching`, both
    # for the same rule: one name may not carry two shapes on the wire.
    # A session's `acted` is the trail of completed changes; a turn's `did` is
    # what it reached for, refusals included — and `watching` was already a
    # boolean on the crash watch. `test_one_name_one_type_on_the_wire` found
    # both.
    return {"engagement_id": engagement_id, "reply": reply, "did": steps,
            "stopped": stopped, "engaged": True,
            "watches": watches(user_id),
            "provenance": {"generated_by": generated["provider"],
                           "degraded": generated.get("degraded", False),
                           "degraded_reason": generated.get("reason")}}
