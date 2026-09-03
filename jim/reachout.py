"""The reach-out cascade: JIM calling emergency contacts, one after another.

The ladder the owner drew, from the person outward:

1. JIM calls the first emergency contact. Before anything else the contact
   chooses on the keypad — **1** to hear the message, **2** to never be called
   for this person again.
2. On **1**, JIM — the language model — actually talks: it tells them what is
   happening, what it is about, and what to do, and it answers what they ask.
   The exchange is documented.
3. On **2**, or on no answer, that contact is done: a **2** is remembered so
   the number is never rung again; either way the cascade moves to the next
   contact.
4. When the contacts are exhausted and the situation is life-threatening, the
   cascade reaches the last rung — the 911 dialer — which is **built and held
   shut** (:mod:`jim.dialer`). The connection is assembled and routed; the
   send does not go out.

## Built against the seam, and now through it

Every contact call goes out through :func:`jim.dialer.call_contact`, and that
function rings through the voice door (:mod:`jim.telephony`) when a
transport is wired and ready. When none is — today's box, every test
environment, offline mode — the call comes back *prepared*: the leg is
assembled and documented, its row says ``placed`` is false, and the cascade
waits there rather than pretending. This module keeps one shape either way:
the consent gate, the spoken conversation, the opt-out, the advance-on-no-
reach, the exhaust into the held 911 rung, and the documentation run the same
whether the sidecar's webhooks or a test drive the handlers.

## Reached is decided by the line, not by the caller

A contact is *reached* when they pressed 1, heard at least one spoken turn,
and the line then ended. The phone line's word on a leg arrives at
:func:`event`, and that is the one place the decision is made: a pickup that
never pressed 1, a keypad choice with nothing spoken after it, a voicemail, a
busy tone, no answer — unreached, with the word for how it ended on the row.
Every row is its own mutex (:func:`_claim`), so a house that retries a status
callback or delivers events out of order advances the cascade once. A placed
leg the line never reports on is settled by :func:`settle_stale`, from the
crash watch's sweep and nowhere else — a read never settles a call, and the
ticker (:mod:`jim.ticker`) makes that sweep on its own clock, so the
settlement never waits on somebody looking.

## The conversation is objective-driven

The message is not one fixed script. :func:`_opening` and :func:`say` build
the model's side from the *situation* handed to :func:`begin` — for the
guardian that is the emergency and what to do about it, and the same shape
carries an ordinary work objective when this cascade is later lifted into a
general calling layer. The model speaks in the caller's own words for the
person on the line.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone

from . import audit, db, dialer, llm, telephony

log = logging.getLogger("jim.reachout")

#: A leg the line may still speak about, and the ones it has finished with.
LIVE = ("ringing", "consented", "talking")
TERMINAL = ("reached", "unreached", "declined", "unplaced")
#: The line's own words for how a leg ended — JIM's vocabulary, whatever the
#: house called it; the sidecar maps each house's words onto these.
TERMINAL_EVENTS = ("completed", "voicemail", "no-answer", "busy", "failed",
                   "canceled")
EVENTS = ("answered",) + TERMINAL_EVENTS
#: How long past its ceiling a placed leg may go unreported before the sweep
#: settles it — a ringing leg past its ring time, a conversation past its
#: call time since the last turn.
STALE_RING_GRACE_S = 90
STALE_TALK_GRACE_S = 60


def opted_out(user_id: str, channel: str) -> bool:
    return db.connect().execute(
        "SELECT 1 FROM do_not_call WHERE user_id=? AND channel=?",
        (user_id, channel)).fetchone() is not None


def _opening(situation: dict) -> str:
    """The words the call opens with, before the keypad choice — composed
    from the situation so an emergency and a work objective each sound like
    themselves."""
    who = situation.get("who") or "someone"
    about = situation.get("about") or situation.get("concern") or "a situation"
    return (f"This is JIM calling on behalf of {who} about {about}. "
            "Press 1 to hear the message, or 2 to not be called this way "
            "again.")


def _system(situation: dict) -> str:
    """The model's standing instruction for this call — grounded in the
    situation, honest about what it is and is not."""
    who = situation.get("who") or "the person JIM watches over"
    about = situation.get("about") or situation.get("concern") or "a concern"
    what_to_do = situation.get("what_to_do") or ""
    lines = [
        f"You are JIM, calling a trusted contact of {who} on the phone.",
        f"Why you are calling: {about}.",
        "Tell them plainly what is happening, answer what they ask, and say "
        "what would help. Be brief and calm; this is a phone call, not an "
        "essay.",
        "You cannot yourself place a 911 call. If they ask you to call "
        "emergency services, tell them to dial their local emergency number "
        "themselves.",
    ]
    if what_to_do:
        lines.append(f"What to advise if they can act: {what_to_do}")
    return "\n".join(lines)


def _next_contact(reachout: dict) -> dict | None:
    """The next contact not opted out, advancing the cursor past any that
    are. Returns the contact dict, or None when the list is spent."""
    contacts = json.loads(reachout["contacts"])
    idx = reachout["idx"]
    while idx < len(contacts):
        c = contacts[idx]
        idx += 1
        if not opted_out(reachout["user_id"], c["channel"]):
            _set(reachout["id"], idx=idx)
            return c
        _set(reachout["id"], idx=idx)
    return None


def _set(reachout_id: str, **cols) -> None:
    if not cols:
        return
    cols["updated_at"] = db.utcnow()
    sets = ", ".join(f"{k}=?" for k in cols)
    db.connect().execute(
        f"UPDATE reachouts SET {sets} WHERE id=?",
        (*cols.values(), reachout_id))
    db.connect().commit()


def _call_set(call_id: str, **cols) -> None:
    cols["updated_at"] = db.utcnow()
    sets = ", ".join(f"{k}=?" for k in cols)
    db.connect().execute(
        f"UPDATE reachout_calls SET {sets} WHERE id=?",
        (*cols.values(), call_id))
    db.connect().commit()


def _claim(call_id: str, from_statuses: tuple[str, ...], to_status: str,
           **cols) -> bool:
    """Move a leg from one of ``from_statuses`` to ``to_status`` in a single
    statement, and say whether this caller was the one who did.

    The row is its own mutex. A second arrival — a house retrying its status
    callback, a completed racing the last keypad gather — finds the status
    already moved, gets False, and changes nothing; the cascade advances
    once. There is deliberately no read-then-write here to lose a race in.
    """
    cols["status"] = to_status
    cols["updated_at"] = db.utcnow()
    sets = ", ".join(f"{k}=?" for k in cols)
    marks = ",".join("?" for _ in from_statuses)
    conn = db.connect()
    cur = conn.execute(
        f"UPDATE reachout_calls SET {sets} WHERE id=? AND status IN ({marks})",
        (*cols.values(), call_id, *from_statuses))
    conn.commit()
    return cur.rowcount == 1


def _log_event(call: dict, event: str, seconds: int = 0, detail: str = "",
               note: str = "") -> None:
    """The line's word, written down verbatim and in order beside the
    decision it fed — so a reviewer can read both."""
    conn = db.connect()
    conn.execute(
        "INSERT INTO reachout_call_events (id, call_id, user_id, event,"
        " seconds, detail, note, at) VALUES (?,?,?,?,?,?,?,?)",
        (db.new_id("rce"), call["id"], call["user_id"], event,
         int(seconds or 0), detail or "", note or "", db.utcnow()))
    conn.commit()


def _already(call: dict) -> dict:
    """The leg had already ended when this arrived. Nothing moves."""
    return {"status": call["status"], "already": True, "call": call,
            "reachout_id": call["reachout_id"]}


def _place_next(reachout: dict) -> dict:
    """Ring the next contact, or — spent — reach the held 911 rung.

    A door that refuses the number, refuses JIM's secret, or does not
    answer means this leg was never rung: the row says *unplaced* with the
    door's sentence, and the next person is rung. Never a pretended ring.
    """
    contact = _next_contact(_load(reachout["id"]))
    if contact is None:
        return _exhaust(_load(reachout["id"]))
    situation = json.loads(reachout["situation"])
    cid = db.new_id("rcl")
    now = db.utcnow()
    db.connect().execute(
        "INSERT INTO reachout_calls (id, reachout_id, user_id, name, channel,"
        " status, transcript, created_at, updated_at)"
        " VALUES (?,?,?,?,?, 'ringing', '[]', ?, ?)",
        (cid, reachout["id"], reachout["user_id"], contact["name"],
         contact["channel"], now, now))
    db.connect().commit()
    try:
        placed = dialer.call_contact(contact["channel"], _opening(situation),
                                     call_id=cid)
    except dialer.CallNotPlaced as exc:
        _call_set(cid, status="unplaced", placement=str(exc))
        audit.record("contact.unplaced", user_id=reachout["user_id"],
                     ref=contact["name"])
        log.warning("reach-out %s: %s not rung — %s",
                    reachout["id"], contact["name"], exc)
        return _place_next(_load(reachout["id"]))
    except Exception as exc:  # noqa: BLE001 — a stranded leg is the worse outcome
        # Anything else the wire can throw is still not a ring. The leg says
        # so and the next person is rung; a row left "ringing" with no line
        # behind it would re-fire on every sweep and never advance.
        _call_set(cid, status="unplaced",
                  placement=f"the transport failed before the call was placed: "
                            f"{type(exc).__name__}: {exc}")
        audit.record("contact.unplaced", user_id=reachout["user_id"],
                     ref=contact["name"])
        log.exception("reach-out %s: %s not rung", reachout["id"], contact["name"])
        return _place_next(_load(reachout["id"]))
    if placed.get("placed"):
        _call_set(cid, placed=1, provider=placed.get("provider"),
                  provider_call_id=placed.get("provider_call_id"),
                  placed_at=db.utcnow())
    audit.record("contact.called", user_id=reachout["user_id"],
                 ref=contact["name"])
    return {"status": "calling", "call": _call(cid), "dialer": placed,
            "reachout_id": reachout["id"]}


def _exhaust(reachout: dict) -> dict:
    """The contacts are spent. If the situation is life-threatening, the last
    rung is the 911 dialer — assembled, routed, and held shut."""
    _set(reachout["id"], status="exhausted")
    audit.record("reachout.exhausted", user_id=reachout["user_id"],
                 ref=reachout["id"])
    situation = json.loads(reachout["situation"])
    nin911 = None
    if reachout["life_threat"]:
        # The held door. dialer.place assembles and routes, and holds the
        # send — no call goes out (jim/dialer.py).
        nin911 = dialer.place(
            {"who": situation.get("who"), "about": situation.get("about"),
             "reached_no_contact": True},
            user_id=reachout["user_id"])
    return {"status": "exhausted", "reachout_id": reachout["id"],
            "life_threatening": bool(reachout["life_threat"]),
            "emergency_services": nin911}


# --------------------------------------------------------------------------- #
# the doors the cascade turns on
# --------------------------------------------------------------------------- #

def begin(user_id: str, contacts: list[dict], situation: dict,
          life_threatening: bool = False) -> dict:
    """Open a cascade and ring the first reachable contact.

    ``contacts`` is the ordered list of emergency people, each
    ``{"name", "channel"}``; the caller assembles it (the crash watch's
    trusted person first, then the rest). Ones that opted out are skipped.
    """
    clean = [c for c in contacts
             if (c.get("name") or "").strip() and (c.get("channel") or "").strip()]
    if not clean:
        raise ValueError("a reach-out needs at least one emergency contact")
    rid = db.new_id("rch")
    now = db.utcnow()
    db.connect().execute(
        "INSERT INTO reachouts (id, user_id, situation, life_threat, status,"
        " idx, contacts, created_at, updated_at)"
        " VALUES (?,?,?,?, 'calling', 0, ?, ?, ?)",
        (rid, user_id, json.dumps(situation), 1 if life_threatening else 0,
         json.dumps(clean), now, now))
    db.connect().commit()
    return _place_next(_load(rid))


def consent(call_id: str, digit: str) -> dict:
    """The keypad choice, before the message. ``1`` opens the conversation;
    ``2`` opts the number out and moves to the next contact; anything else is
    treated as no consent and also advances. A choice that arrives after the
    leg ended changes nothing and says ``already``."""
    call = _call(call_id)
    reachout = _load(call["reachout_id"])
    if digit == "1":
        if not _claim(call_id, ("ringing",), "consented"):
            return _already(_call(call_id))
        return {"status": "consented", "call": _call(call_id),
                "say": _opening_line_after_consent()}
    if digit == "2":
        if not _claim(call_id, ("ringing",), "declined", ended="declined"):
            return _already(_call(call_id))
        db.connect().execute(
            "INSERT OR IGNORE INTO do_not_call (user_id, channel, at)"
            " VALUES (?,?,?)",
            (call["user_id"], call["channel"], db.utcnow()))
        db.connect().commit()
        audit.record("contact.declined", user_id=call["user_id"],
                     ref=call["name"])
        return _place_next(reachout)
    # No clear choice — not consent. Treat as unreached and move on.
    return unreached(call_id, ended="no-choice")


def say(call_id: str, heard: str) -> dict:
    """One turn of the conversation: what the contact said, and JIM's grounded
    spoken reply. The turn is appended to the call's transcript, and the
    turn count on the row is what the line's ceiling reads."""
    call = _call(call_id)
    if call["status"] not in ("consented", "talking"):
        raise ValueError("this call is not in a conversation")
    reachout = _load(call["reachout_id"])
    situation = json.loads(reachout["situation"])
    gen = llm.generate_for_user(call["user_id"], _system(situation),
                                heard or "(the contact said nothing yet)",
                                source="reachout")
    reply = gen["text"]
    transcript = json.loads(call["transcript"])
    transcript.append({"heard": heard, "said": reply})
    # A claim, not a write: the line may have ended while the model was
    # composing, and a terminal leg must never be pulled back to talking.
    if not _claim(call_id, ("consented", "talking"), "talking",
                  transcript=json.dumps(transcript), turns=len(transcript)):
        raise ValueError("this call is not in a conversation")
    log.info("reach-out call %s: turn %d", call_id, len(transcript))
    return {"status": "talking", "said": reply, "call": _call(call_id)}


def reached(call_id: str, ended: str | None = None, *,
            only_from: tuple[str, ...] = LIVE) -> dict:
    """The contact received the message and the exchange is done — the cascade
    has reached a person, and stops here. ``ended`` is the line's word for
    how the leg closed, when the line said one; ``only_from`` narrows the
    claim to the status the decision was made from."""
    call = _call(call_id)
    extra = {"ended": ended} if ended else {}
    if not _claim(call_id, only_from, "reached", **extra):
        return _already(_call(call_id))
    _set(call["reachout_id"], status="reached")
    audit.record("contact.reached", user_id=call["user_id"], ref=call["name"])
    return {"status": "reached", "call": _call(call_id),
            "reachout_id": call["reachout_id"]}


def unreached(call_id: str, ended: str | None = None, *,
              only_from: tuple[str, ...] = LIVE) -> dict:
    """No answer, or no consent — this contact is not reached; ring the next,
    or reach the held 911 rung if the list is spent. ``ended`` is the word
    for why, kept on the row; ``only_from`` narrows the claim to the status
    the decision was made from."""
    call = _call(call_id)
    extra = {"ended": ended} if ended else {}
    if not _claim(call_id, only_from, "unreached", **extra):
        return _already(_call(call_id))
    audit.record("contact.unreached", user_id=call["user_id"], ref=call["name"])
    return _place_next(_load(call["reachout_id"]))


def event(call_id: str, event: str, seconds: int = 0, detail: str = "") -> dict:
    """The phone line's word on a leg — and the one place reached versus
    unreached is decided.

    ``answered`` is noted: the pickup time goes on the row and the keypad
    choice is the contact's now. A terminal word decides by where the leg
    stood: *talking* (they pressed 1 and heard at least one turn) is
    reached; *consented* with nothing spoken is unreached
    ``consented-unspoken``; *ringing* is unreached with the line's word, or
    ``completed-without-consent`` for a pickup that never pressed 1. A word
    for a leg that already ended is written down with the note ``late`` and
    moves nothing — the cascade advances once, however many times a house
    repeats itself.
    """
    if event not in EVENTS:
        raise ValueError("that is not an event the phone line reports")
    call = _call(call_id)
    if call["status"] in TERMINAL:
        _log_event(call, event, seconds, detail, note="late")
        return {**_already(call), "decided": "already"}
    _log_event(call, event, seconds, detail)
    if event == "answered":
        if not call["answered_at"]:
            _call_set(call_id, answered_at=db.utcnow())
            audit.record("contact.answered", user_id=call["user_id"],
                         ref=call["name"])
        return {"status": call["status"], "decided": "noted",
                "call": _call(call_id), "reachout_id": call["reachout_id"]}
    # Decide from the status the claim is made from — never from a status
    # read a moment earlier. A turn that lands between the read and the
    # claim moves the leg on; the claim then fails and the decision is
    # made again from where the leg actually stands.
    for _ in range(3):
        where = call["status"]
        if where in TERMINAL:
            return {**_already(call), "decided": "already"}
        if where == "talking":
            out = reached(call_id, ended=event, only_from=("talking",))
            decided = "reached"
        elif where == "consented":
            out = unreached(call_id, ended="consented-unspoken",
                            only_from=("consented",))
            decided = "unreached"
        else:
            out = unreached(call_id, ended=("completed-without-consent"
                                            if event == "completed" else event),
                            only_from=("ringing",))
            decided = "unreached"
        if not out.get("already"):
            return {**out, "decided": decided}
        call = _call(call_id)
    return {**_already(call), "decided": "already"}


def settle_stale(user_id: str, now: datetime | None = None) -> list[str]:
    """Placed legs the line never reported on, settled as unreached
    ``no-report`` and the cascade advanced — a ring nobody reported on is
    not a reached person.

    A *ringing* leg is stale past its ring time (plus grace) since it was
    placed; a *consented* or *talking* leg past the call ceiling (plus grace)
    since its last turn, so a live conversation — whose row moves on every
    turn — is never settled under. A leg that was only prepared (``placed``
    false) has no line to go quiet and is never settled. Called from
    :func:`jim.crashwatch.sweep` and nowhere else; a read never settles.
    """
    t = now or datetime.now(timezone.utc)
    ring_cutoff = t - timedelta(seconds=telephony.RING_SECONDS
                                + STALE_RING_GRACE_S)
    talk_cutoff = t - timedelta(seconds=telephony.MAX_CALL_SECONDS
                                + STALE_TALK_GRACE_S)
    rows = db.connect().execute(
        "SELECT id, status, placed_at, updated_at FROM reachout_calls"
        " WHERE user_id=? AND placed=1 AND status IN ('ringing','consented',"
        "'talking') ORDER BY created_at", (user_id,)).fetchall()
    settled: list[str] = []
    for r in rows:
        if r["status"] == "ringing":
            stamp, cutoff = r["placed_at"], ring_cutoff
        else:
            stamp, cutoff = r["updated_at"], talk_cutoff
        when = _parse(stamp)
        if when is None or when >= cutoff:
            continue
        out = unreached(r["id"], ended="no-report")
        if not out.get("already"):
            settled.append(r["id"])
            log.warning("reach-out call %s: no report from the line, settled "
                        "unreached", r["id"])
    return settled


def _parse(stamp: str | None) -> datetime | None:
    if not stamp:
        return None
    try:
        when = datetime.fromisoformat(stamp)
    except ValueError:
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    return when


# --------------------------------------------------------------------------- #
# reads
# --------------------------------------------------------------------------- #

def _opening_line_after_consent() -> str:
    return ("Thank you. I'll tell you what's happening, and you can ask me "
            "anything.")


def _load(reachout_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM reachouts WHERE id=?", (reachout_id,)).fetchone()
    if row is None:
        raise ValueError("no such reach-out")
    return dict(row)


def _call(call_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM reachout_calls WHERE id=?", (call_id,)).fetchone()
    if row is None:
        raise ValueError("no such call")
    return dict(row)


def events(call_id: str) -> list[dict]:
    """What the line said about a leg, in order — the record beside the
    decision."""
    return [dict(r) for r in db.connect().execute(
        "SELECT event, seconds, detail, note, at FROM reachout_call_events"
        " WHERE call_id=? ORDER BY at, rowid", (call_id,)).fetchall()]


def status(reachout_id: str) -> dict:
    """The cascade as it stands. A read: it settles nothing."""
    r = _load(reachout_id)
    calls = [dict(c) for c in db.connect().execute(
        "SELECT id, name, status, placed, provider, provider_call_id, ended,"
        " placement, turns, answered_at FROM reachout_calls"
        " WHERE reachout_id=? ORDER BY created_at", (reachout_id,)).fetchall()]
    for c in calls:
        c["placed"] = bool(c["placed"])
        c["turns"] = int(c["turns"] or 0)
    situation = json.loads(r["situation"])
    return {"id": r["id"], "user_id": r["user_id"], "status": r["status"],
            "life_threatening": bool(r["life_threat"]),
            "about": situation.get("about"),
            "started_at": r["created_at"], "calls": calls}


def for_user(user_id: str, limit: int = 20) -> list[dict]:
    """Every reach-out this user has, newest first — the operator screen's
    read. Each is the same shape :func:`status` returns, so the screen renders
    one thing whether the cascade was started by hand or by a crash-watch
    trip."""
    rows = db.connect().execute(
        "SELECT id FROM reachouts WHERE user_id=? ORDER BY created_at DESC"
        " LIMIT ?", (user_id, int(limit))).fetchall()
    return [status(r["id"]) for r in rows]
