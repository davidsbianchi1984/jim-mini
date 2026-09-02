"""The moderated mailbox — the coach agent's correspondence, held at the send.

The owner's line, the same one the dialer holds: build the machinery so the
agent can actually carry on email — read what comes in, draft a reply, answer
back and forth — but **nothing leaves without a person approving it.** Every
message the agent would send is composed as a *draft* and held in a moderation
queue; a human approves, edits, or discards it, and only an approval sends.

## Two directions, one gate

* **Inbound** is taken into a thread by :func:`receive` — today from the
  operator ingesting a message they hold, tomorrow from a provider's inbound
  webhook or an IMAP poll (the wiring step named in :func:`posture`). Either
  way it lands as a read-only record the agent can answer.
* **Outbound** is always a draft first. :func:`draft` has the language model
  compose a reply grounded in the thread and the mailbox's *role*; :func:`compose`
  starts an outbound message the same way. Neither sends. :func:`moderate` is
  the only path that sends, and it sends through :mod:`jim.mailer` — real SMTP
  when configured, and *staged* (composed and held, never dropped, never
  claimed sent) when nothing is wired.

## The role is the voice

A mailbox has a ``role``. For the guardian that is ``coach`` — JIM's life
coach, warm and brief, never diagnosing. The same machinery carries a
different voice when this seam is lifted into QRME: a synthetic profile
answers its correspondence *in its profession*, and the role is the profession.
:func:`_system` is the one place the voice is chosen, so the lift is a role, not
a rewrite.
"""

from __future__ import annotations

from . import audit, db, llm, mailer

#: The mailbox roles this build knows. ``coach`` is JIM's life coach; the
#: seam is written so a profession name drops in unchanged when QRME lifts it.
DEFAULT_ROLE = "coach"


def posture() -> dict:
    """What the mailbox is, for the operator screen: which way mail can carry,
    and that every send waits on a person.

    Outbound is as wired as the deployment's mail is (:mod:`jim.mailer`) — SMTP
    when configured, otherwise staged to the console. Inbound is *not* wired to
    arrive on its own yet: a provider's inbound webhook or an IMAP poll is the
    owner's step, the same shape the telephony transport waits on. What never
    waits and never changes is the gate — a draft is held until a person
    approves it.
    """
    transport = mailer.configured_transport()
    return {
        "built": True,
        "outbound_transport": transport,
        "outbound_ready": transport == "smtp",
        "inbound_ready": False,
        "moderated": True,
        "directions": ["read", "draft", "reply", "moderate"],
        "note": ("the agent reads, drafts, and replies, but every message it "
                 "would send is held for a person to approve — nothing leaves "
                 "on its own. Outbound sends over SMTP when configured and is "
                 "otherwise staged (composed and held); inbound arrives "
                 "automatically once a provider webhook or IMAP poll is wired."),
    }


# --------------------------------------------------------------------------- #
# reads
# --------------------------------------------------------------------------- #

def _thread(user_id: str, thread_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM mail_threads WHERE id=? AND user_id=?",
        (thread_id, user_id)).fetchone()
    if row is None:
        raise ValueError("no such mail thread")
    return dict(row)


def _message(user_id: str, message_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM mail_messages WHERE id=? AND user_id=?",
        (message_id, user_id)).fetchone()
    if row is None:
        raise ValueError("no such mail message")
    return dict(row)


def _messages_of(thread_id: str) -> list[dict]:
    return [dict(r) for r in db.connect().execute(
        "SELECT * FROM mail_messages WHERE thread_id=? ORDER BY created_at",
        (thread_id,)).fetchall()]


def inbox(user_id: str, limit: int = 50) -> list[dict]:
    """Every thread on this account, newest activity first, each with its
    messages — the operator screen's read. Held drafts sit in the thread they
    belong to, next to the message they answer."""
    threads = db.connect().execute(
        "SELECT * FROM mail_threads WHERE user_id=? ORDER BY updated_at DESC"
        " LIMIT ?", (user_id, int(limit))).fetchall()
    out = []
    for t in threads:
        msgs = _messages_of(t["id"])
        out.append({
            "id": t["id"], "role": t["role"], "correspondent": t["correspondent"],
            "subject": t["subject"], "status": t["status"],
            "updated_at": t["updated_at"],
            "held_drafts": sum(1 for m in msgs if m["state"] == "draft"),
            "messages": [_public(m) for m in msgs],
        })
    return out


def _public(m: dict) -> dict:
    """A message as a screen reads it — no user_id echoed back on every row."""
    return {"id": m["id"], "direction": m["direction"], "state": m["state"],
            "from_addr": m["from_addr"], "to_addr": m["to_addr"],
            "subject": m["subject"], "body": m["body"],
            "created_at": m["created_at"]}


# --------------------------------------------------------------------------- #
# the doors
# --------------------------------------------------------------------------- #

def receive(user_id: str, *, from_addr: str, subject: str, body: str,
            role: str = DEFAULT_ROLE) -> dict:
    """Take an inbound email into a thread. Groups with an open thread from the
    same correspondent on the same role, or opens a new one."""
    from_addr = (from_addr or "").strip()
    body = (body or "").strip()
    if not from_addr:
        raise ValueError("an inbound email needs a sender address")
    if not body:
        raise ValueError("an inbound email needs a body")
    subject = (subject or "").strip() or "(no subject)"
    role = (role or DEFAULT_ROLE).strip() or DEFAULT_ROLE
    now = db.utcnow()
    conn = db.connect()
    existing = conn.execute(
        "SELECT id FROM mail_threads WHERE user_id=? AND role=? AND"
        " correspondent=? AND status='open' ORDER BY updated_at DESC LIMIT 1",
        (user_id, role, from_addr)).fetchone()
    if existing:
        tid = existing["id"]
        conn.execute("UPDATE mail_threads SET updated_at=? WHERE id=?",
                     (now, tid))
    else:
        tid = db.new_id("mth")
        conn.execute(
            "INSERT INTO mail_threads (id, user_id, role, correspondent,"
            " subject, status, created_at, updated_at)"
            " VALUES (?,?,?,?,?, 'open', ?, ?)",
            (tid, user_id, role, from_addr, subject, now, now))
    mid = db.new_id("mim")
    conn.execute(
        "INSERT INTO mail_messages (id, thread_id, user_id, direction, state,"
        " from_addr, to_addr, subject, body, created_at, updated_at)"
        " VALUES (?,?,?, 'inbound', 'received', ?, '', ?, ?, ?, ?)",
        (mid, tid, user_id, from_addr, subject, body, now, now))
    conn.commit()
    audit.record("mail.received", user_id=user_id, ref=from_addr)
    return {"thread_id": tid, "message": _public(_message(user_id, mid))}


def draft(user_id: str, message_id: str) -> dict:
    """Have the agent compose a reply to an inbound message. The reply is held
    as a draft — it is not sent, and cannot be, until a person approves it."""
    incoming = _message(user_id, message_id)
    thread = _thread(user_id, incoming["thread_id"])
    reply_body = _compose_reply(user_id, thread, incoming["body"])
    subject = incoming["subject"]
    if not subject.lower().startswith("re:"):
        subject = f"Re: {subject}"
    mid = _hold_draft(user_id, thread, to_addr=thread["correspondent"],
                      subject=subject, body=reply_body)
    audit.record("mail.drafted", user_id=user_id, ref=thread["correspondent"])
    return {"thread_id": thread["id"], "draft": _public(_message(user_id, mid))}


def compose(user_id: str, *, to: str, subject: str, objective: str,
            role: str = DEFAULT_ROLE) -> dict:
    """Start an outbound message the agent originates. ``objective`` is what the
    message should accomplish, in the operator's words; the agent writes the
    email and it is held as a draft for approval, same as a reply."""
    to = (to or "").strip()
    if not to:
        raise ValueError("an outbound email needs a recipient address")
    subject = (subject or "").strip() or "(no subject)"
    role = (role or DEFAULT_ROLE).strip() or DEFAULT_ROLE
    now = db.utcnow()
    tid = db.new_id("mth")
    db.connect().execute(
        "INSERT INTO mail_threads (id, user_id, role, correspondent, subject,"
        " status, created_at, updated_at) VALUES (?,?,?,?,?, 'open', ?, ?)",
        (tid, user_id, role, to, subject, now, now))
    db.connect().commit()
    thread = _thread(user_id, tid)
    body = _compose_reply(user_id, thread, objective, originating=True)
    mid = _hold_draft(user_id, thread, to_addr=to, subject=subject, body=body)
    audit.record("mail.drafted", user_id=user_id, ref=to)
    return {"thread_id": tid, "draft": _public(_message(user_id, mid))}


def moderate(user_id: str, draft_id: str, action: str,
             edited: str | None = None) -> dict:
    """A person's decision on a held draft. ``approve`` sends it (over SMTP if
    configured, otherwise staged and held — never dropped, never claimed sent);
    ``edit`` replaces the body and keeps it held; ``discard`` throws it away and
    sends nothing."""
    draft = _message(user_id, draft_id)
    if draft["direction"] != "outbound" or draft["state"] != "draft":
        raise ValueError("this message is not a draft awaiting moderation")
    thread = _thread(user_id, draft["thread_id"])
    if action == "edit":
        new_body = (edited or "").strip()
        if not new_body:
            raise ValueError("an edited reply needs a body")
        _message_set(draft_id, body=new_body)
        return {"status": "held", "draft": _public(_message(user_id, draft_id))}
    if action == "discard":
        _message_set(draft_id, state="discarded")
        audit.record("mail.discarded", user_id=user_id,
                     ref=thread["correspondent"])
        return {"status": "discarded",
                "message": _public(_message(user_id, draft_id))}
    if action == "approve":
        return _send(user_id, thread, draft)
    raise ValueError("a moderation action is approve, edit, or discard")


def _send(user_id: str, thread: dict, draft: dict) -> dict:
    """Carry an approved draft out. SMTP when wired; staged and held otherwise
    — the honest receipt names which, and never claims a send that did not
    happen."""
    transport = mailer.configured_transport()
    if transport == "smtp":
        mailer.deliver(draft["to_addr"], draft["subject"], draft["body"])
        _message_set(draft["id"], state="sent")
        audit.record("mail.sent", user_id=user_id, ref=thread["correspondent"])
        return {"status": "sent", "transport": "smtp",
                "message": _public(_message(user_id, draft["id"]))}
    _message_set(draft["id"], state="staged")
    audit.record("mail.staged", user_id=user_id, ref=thread["correspondent"])
    return {
        "status": "staged", "transport": "none",
        "reason": "the reply is approved and composed, but no mail transport "
                  "is configured, so it is held rather than sent — configure "
                  "SMTP on the Settings screen to carry it.",
        "message": _public(_message(user_id, draft["id"])),
    }


# --------------------------------------------------------------------------- #
# the voice, and the plumbing under it
# --------------------------------------------------------------------------- #

def _system(user_id: str, role: str, thread: dict) -> str:
    """The model's standing instruction for this mailbox — its voice chosen by
    the role, and the language chosen by the user. The one place a profession
    would drop in when this seam is lifted into QRME."""
    from . import guardian, i18n
    from .guidance import personalize
    if role == DEFAULT_ROLE:
        base = (
            "You are JIM-mini's life coach, writing an email reply on behalf "
            "of the person you support. Be warm, brief, and specific. Never "
            "diagnose; for medical, legal, or financial decisions, point them "
            "to a qualified professional. If someone may be in danger, urge "
            "them to seek immediate help. Write a complete email — a greeting, "
            "the message, and a sign-off — in plain text.")
    else:
        base = (
            f"You are a professional whose role is: {role}. You are writing an "
            "email reply in that professional capacity, as part of your work. "
            "Be courteous, precise, and helpful; stay within your role, and "
            "write a complete email — a greeting, the message, and a sign-off "
            "— in plain text.")
    base += personalize(guardian.get_user(user_id))
    base += f"\nThe email thread is with {thread['correspondent']}, subject: " \
            f"{thread['subject']}."
    language = i18n.effective_language(user_id)
    base += i18n.directive(language)
    return base


def _compose_reply(user_id: str, thread: dict, prompt: str,
                   originating: bool = False) -> str:
    """One model turn: the agent's email body, grounded in the thread so far.
    ``prompt`` is the inbound message to answer, or — when originating — what
    the outbound message should accomplish."""
    history = _messages_of(thread["id"])
    lines = []
    for m in history:
        if m["state"] == "discarded":
            continue
        who = "Them" if m["direction"] == "inbound" else "You"
        lines.append(f"{who}: {m['body']}")
    transcript = "\n\n".join(lines)
    if originating:
        user_turn = (f"Write an email that accomplishes this: {prompt}")
    else:
        user_turn = (f"Reply to the latest email.\n\nThe thread so far:\n"
                     f"{transcript}\n\nThe email to answer:\n{prompt}")
    gen = llm.generate_for_user(user_id, _system(user_id, thread["role"], thread),
                                user_turn, source="mailbox")
    return gen["text"].strip()


def _hold_draft(user_id: str, thread: dict, *, to_addr: str, subject: str,
                body: str) -> str:
    now = db.utcnow()
    mid = db.new_id("mim")
    conn = db.connect()
    conn.execute(
        "INSERT INTO mail_messages (id, thread_id, user_id, direction, state,"
        " from_addr, to_addr, subject, body, created_at, updated_at)"
        " VALUES (?,?,?, 'outbound', 'draft', '', ?, ?, ?, ?, ?)",
        (mid, thread["id"], user_id, to_addr, subject, body, now, now))
    conn.execute("UPDATE mail_threads SET updated_at=? WHERE id=?",
                 (now, thread["id"]))
    conn.commit()
    return mid


def _message_set(message_id: str, **cols) -> None:
    cols["updated_at"] = db.utcnow()
    sets = ", ".join(f"{k}=?" for k in cols)
    db.connect().execute(
        f"UPDATE mail_messages SET {sets} WHERE id=?",
        (*cols.values(), message_id))
    db.connect().commit()
