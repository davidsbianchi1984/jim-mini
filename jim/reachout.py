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

## Built against the seam

No real call leaves the building yet: :func:`jim.dialer.call_contact` returns
each call *prepared*, because no telephony transport is wired (that is the
owner's provider step). Everything else — the consent gate, the spoken
conversation, the opt-out, the advance-on-no-reach, the exhaust into the held
911 rung, and the documentation — runs and is testable now by driving the
handlers the provider's webhooks will one day call. When a transport is wired,
only :func:`jim.dialer.call_contact` changes; this cascade does not.

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

from . import audit, db, dialer, llm


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


def _place_next(reachout: dict) -> dict:
    """Ring the next contact, or — spent — reach the held 911 rung."""
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
    prepared = dialer.call_contact(contact["channel"], _opening(situation),
                                   call_id=cid)
    audit.record("contact.called", user_id=reachout["user_id"],
                 ref=contact["name"])
    return {"status": "calling", "call": _call(cid), "dialer": prepared,
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
    treated as no consent and also advances."""
    call = _call(call_id)
    reachout = _load(call["reachout_id"])
    if digit == "1":
        _call_set(call_id, status="consented")
        return {"status": "consented", "call": _call(call_id),
                "say": _opening_line_after_consent()}
    if digit == "2":
        db.connect().execute(
            "INSERT OR IGNORE INTO do_not_call (user_id, channel, at)"
            " VALUES (?,?,?)",
            (call["user_id"], call["channel"], db.utcnow()))
        db.connect().commit()
        _call_set(call_id, status="declined")
        audit.record("contact.declined", user_id=call["user_id"],
                     ref=call["name"])
        return _place_next(reachout)
    # No clear choice — not consent. Treat as unreached and move on.
    return unreached(call_id)


def say(call_id: str, heard: str) -> dict:
    """One turn of the conversation: what the contact said, and JIM's grounded
    spoken reply. The turn is appended to the call's transcript."""
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
    _call_set(call_id, status="talking", transcript=json.dumps(transcript))
    return {"status": "talking", "said": reply, "call": _call(call_id)}


def reached(call_id: str) -> dict:
    """The contact received the message and the exchange is done — the cascade
    has reached a person, and stops here."""
    call = _call(call_id)
    _call_set(call_id, status="reached")
    _set(call["reachout_id"], status="reached")
    audit.record("contact.reached", user_id=call["user_id"], ref=call["name"])
    return {"status": "reached", "call": _call(call_id)}


def unreached(call_id: str) -> dict:
    """No answer, or no consent — this contact is not reached; ring the next,
    or reach the held 911 rung if the list is spent."""
    call = _call(call_id)
    _call_set(call_id, status="unreached")
    audit.record("contact.unreached", user_id=call["user_id"], ref=call["name"])
    return _place_next(_load(call["reachout_id"]))


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


def status(reachout_id: str) -> dict:
    r = _load(reachout_id)
    calls = [dict(c) for c in db.connect().execute(
        "SELECT id, name, status FROM reachout_calls WHERE reachout_id=?"
        " ORDER BY created_at", (reachout_id,)).fetchall()]
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
