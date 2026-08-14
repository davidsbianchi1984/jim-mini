"""The 24/7 life coach — guidance across life areas, not just conditions.

Where ``guidance.py`` answers a *detected condition*, the coach answers the
user directly in a chosen life area (mental health, health & fitness, career,
finance, relationships, personal growth), grounded in their recent check-ins
and active goals. Uses JIM's own LLM provider and the same safety net.
"""

from __future__ import annotations

from . import continuity, db, guardian, life, llm
from .guidance import _DENY, personalize

AREAS = {
    "mental_health": "mental health — support, coping strategies, resources",
    "health_fitness": "health & fitness — workouts, sleep, recovery",
    "nutrition": "nutrition — meal planning, eating patterns, hydration; "
                 "never a diet prescription",
    "career": "career & growth — resume feedback, skills, interview prep",
    "finance": "finance — budgeting, saving, and general money habits",
    "relationships": "relationships — communication and connection",
    "personal_growth": "personal growth — habits, focus, becoming your best self",
}

_SYSTEM = (
    "You are JIM-mini's life coach: calm, evidence-based, warm, and brief. "
    "Coaching area: {area}. Never diagnose; for medical, legal, or investment "
    "decisions, recommend a qualified professional. If the user may be in "
    "danger, urge them to seek immediate help.\n"
    "{context}"
)


def _context(user_id: str) -> str:
    lines = []
    recent = life.checkins(user_id)[-1:]
    if recent:
        c = recent[0]
        lines.append(f"latest check-in: mood {c['mood']}/5"
                     + (f", energy {c['energy']}/5" if c["energy"] else ""))
    active = [g for g in life.goals(user_id) if g["status"] == "active"][:3]
    for g in active:
        lines.append(f"active goal ({g['area']}): {g['title']}"
                     f" — {round(g['progress'] * 100)}% done")
    prior = history(user_id)
    if prior:
        lines.append(f"{len(prior)} prior coach message(s) on record — keep "
                     "continuity with earlier sessions")
    # A coach who chats about your week without noticing you stopped your
    # heart pills isn't paying attention (jim/meds.py). Context, not alarm.
    from . import meds
    lines.extend(meds.coach_context(user_id))
    # Same stance for the care team (jim/careteam.py): a joint plan the
    # whole team wrote deserves a mention, never an assignment.
    from . import careteam
    lines.extend(careteam.coach_context(user_id))
    # The handover (jim/engaged.py). Somebody who signed off from an engaged
    # session named things for the Guardian to keep an eye on while they were
    # gone, and this is the line where that stops being a promise: the coach
    # answering them offline is carrying what they said to the online one.
    from . import engaged
    lines.extend(engaged.watch_lines(user_id))
    # What this product can do, told to the coach rather than left to the
    # model's priors. Asked "are you capable of going online yet", the coach
    # answered that it cannot browse, look anything up, or check anything
    # live. True of *this* turn — and a description of the product as it
    # stood before engaged sessions existed. The button that opens one was
    # in the same navigation bar as the answer.
    #
    #     asked     is the coach honest about what a coach turn can do
    #     mattered  is it honest about what the product can do
    #
    # There was nothing hardcoded to correct: `_SYSTEM` never told the coach
    # what the product was, so the model filled the gap from what assistants
    # generally cannot do. The count is read from the registry the agent
    # actually runs from, so this line cannot drift from the reach it
    # describes.
    lines.append(
        f"this turn cannot browse or look anything up, but the product can "
        f"do more than this turn: an engaged session ({len(engaged.TOOLS)} "
        f"actions — journalling, goals, habits, medications, bookings, how "
        f"you are spoken to) runs on the online model and acts through this "
        f"app's own doors, every act reversible. asked what you are capable "
        f"of, say so — do not answer as though only this turn existed")
    # What the connected apps collected (jim/app_connectors.py) — the
    # sentence under /apps/connector/{cid}/collect says it "now informs
    # guidance", and this line is where that stops being a claim. Unvaulted
    # rows only; sealed ones stay sealed.
    import json as _json
    for r in db.connect().execute(
            "SELECT data FROM context_events WHERE user_id=? AND"
            " kind='linked_context' ORDER BY created_at DESC, rowid DESC"
            " LIMIT 6", (user_id,)).fetchall():
        data = _json.loads(r["data"])
        if not data.get("vaulted") and data.get("content"):
            lines.append(f"collected context: {data['content'][:160]}")
            if sum(l.startswith("collected context:") for l in lines) >= 3:
                break
    return "\n".join(lines) if lines else "no recent check-ins or goals"


# Clause 12, second half: the system "may autonomously refine its tone
# and or voice interaction style to align with user preferences". PUT
# /personality is the explicit door; this is the autonomous one — when the
# prompt itself states a style preference, the coach keeps it from that turn
# on. A transparent phrase table, never a hidden model read, and the reply
# reports what it learned so the adaptation is visible rather than uncanny.
_TONE_CUES: tuple[tuple[tuple[str, ...], str], ...] = (
    (("keep it short", "be brief", "shorter answers", "get to the point",
      "be direct", "less detail", "too wordy"), "direct and brief"),
    (("be gentle", "be kind", "softer", "go easy on me", "gentler",
      "less blunt"), "gentle and encouraging"),
    (("more detail", "explain more", "be thorough", "in depth",
      "go deeper"), "thorough and detailed"),
    (("plain language", "simpler words", "no jargon", "explain like i",
      "in simple terms"), "plain language, no jargon"),
)


def tone_from_prompt(message: str) -> str | None:
    """The autonomous read of clause 12: a style preference stated in the
    prompt. None when the prompt says nothing about how to answer."""
    text = (message or "").lower()
    for cues, tone in _TONE_CUES:
        if any(cue in text for cue in cues):
            return tone
    return None


#: What each bearing adds to the system prompt. Two short paragraphs rather
#: than two personas: the model is being told how to *word* an answer, and
#: nothing here touches what it is allowed to look at or to say. Both end the
#: same way on purpose — the honesty is not a feature of the warm one.
_BEARING_PROMPT: dict[str, str] = {
    "companion": (
        "\nTalk like somebody who knows them. Warmth is allowed, so is a "
        "question they did not ask for, and so is saying nothing much. Do "
        "not perform intimacy and do not claim to be a person."),
    "professional": (
        "\nThey have asked you to keep things serious. Answer what was "
        "asked, say what you noticed and why, and leave the small talk out. "
        "Do not become cold — brief is not the same as clipped. Do not claim "
        "to be a person."),
}


def reply(user_id: str, area: str, message: str) -> dict:
    from . import i18n

    # Autonomous refinement happens *before* the prompt is built, so the very
    # turn that asked for a shorter answer already gets one.
    adapted_tone = tone_from_prompt(message)
    if adapted_tone:
        guardian.set_personality(user_id, {"tone": adapted_tone})

    # The bearing takes the same path, and for the same reason: somebody who
    # says "keep it professional" is asking to be met that way *now*, not
    # after they find a setting. It is a register — it changes how the answer
    # is worded and never what this is willing to look at.
    from . import presence
    adapted_bearing = presence.bearing_from_prompt(message)
    if adapted_bearing:
        presence.set_bearing(user_id, adapted_bearing)
    carried = presence.bearing(user_id)

    system = _SYSTEM.format(area=AREAS[area], context=_context(user_id))
    system += _BEARING_PROMPT[carried]
    system += personalize(guardian.get_user(user_id))
    # The user-specific adaptation profile (jim/adaptation.py, clause 11):
    # what has actually helped this person, derived from their own history.
    from . import adaptation, continuity
    # Build it if the history has moved on since it last was. Until this line
    # existed, `rebuild` was reachable only from a console button, so on a
    # phone-only user the profile below had never been computed and
    # `prompt_lines` returned nothing on every turn forever.
    adaptation.ensure_fresh(user_id)
    learned = adaptation.prompt_lines(user_id)
    if learned:
        system += "\n" + "\n".join(learned)
    # The cross-session state, rendered as attention weighting rather than as
    # instruction (jim/continuity.py). The profile above is a snapshot taken
    # by hand; this is what moves between snapshots, so a person who has been
    # checking in every day for a month is not met the way they were met on
    # the first day.
    #
    # Silent below its evidence floor, and it never touches identity,
    # boundaries or any safety path.
    attention = continuity.attention_lines(user_id)
    if attention:
        system += "\n" + "\n".join(attention)
    language = i18n.effective_language(user_id)
    system += i18n.directive(language)
    gen = llm.generate_for_user(user_id, system, message)
    text = gen["text"]

    # When the stub is what answered, the offline stack answers better: the
    # add-&-norm pipeline (jim/pipeline.py) over the curated pack, JIM's
    # learned excursions and every deposit a paid turn left — chosen by the
    # question *and* the current readings. A real model keeps its nuance;
    # the stack never overrides one.
    knowledge_entry = None
    pipeline_layers = None
    if gen["provider"] == "stub" or gen.get("degraded"):
        from . import pipeline
        ran = pipeline.run(user_id, area, message)
        pipeline_layers = ran["layers"]
        if ran["text"] is not None:
            knowledge_entry = ran["entry"]
            text = ran["text"]
    else:
        # The paid turn becomes a permanent asset: distilled into the store
        # the offline stack predicts from, so the same gap is never bought
        # twice. The user's own words are the topic — it is their store.
        from . import pipeline
        if not _DENY.search(text):
            pipeline.deposit(user_id, area, message, text, "coach",
                             gen["provider"])

    safe = not _DENY.search(text)
    conn = db.connect()
    now = db.utcnow()
    conn.execute(
        "INSERT INTO coach_messages (id, user_id, area, role, content, created_at)"
        " VALUES (?,?,?,?,?,?)",
        (db.new_id("msg"), user_id, area, "user", message, now),
    )
    if safe:
        conn.execute(
            "INSERT INTO coach_messages (id, user_id, area, role, content, created_at)"
            " VALUES (?,?,?,?,?,?)",
            (db.new_id("msg"), user_id, area, "coach", text, now),
        )
    conn.commit()

    # The turn itself is a signal — folded in after the reply is composed and
    # stored, so a model failure cannot cost the observation the person
    # already gave us by writing. Length only: how much somebody chose to say
    # is about the relationship and carries none of what they said.
    continuity.observe(user_id, "coach_turn", length=len(message))

    if not safe:
        return {"delivered": False, "area": area,
                "reason": "coach reply failed safety check", "content": None}
    # Who covers this area, if anybody — an offer, never a send.
    #
    # A QRME specialist was reachable from exactly one place in this product:
    # the monitoring path, where a detection names a condition. This surface —
    # where somebody brings a question in their own words because they chose
    # to — could not name one at all.
    #
    #     asked     can a specialist be reached
    #     mattered  can the person who asks reach one
    #
    # It stays an offer because the material is different in kind: a detection
    # sends a finding, and this would send what the person wrote. That is
    # theirs to disclose.
    from . import specialists
    #
    # Under `specialist_offer`, not `specialist`: the monitoring path's
    # reply already uses `specialist` for the expert's *name*, a string,
    # and all three native shells decode Guidance with `specialist:
    # String?`. An object under that key would have thrown at decode time
    # on every phone, with no compiler in this environment to say so.
    offer = specialists.offer(area)

    return {"delivered": True, "area": area, "content": text,
            "language": language,
            "specialist_offer": offer,
            # What the coach taught itself from this turn (clause 12), so the
            # adaptation is announced rather than silently applied forever.
            "adapted_tone": adapted_tone,
            # And the bearing, on the same principle: an adaptation nobody
            # can see is an uncanny one. `bearing` is what it is carrying
            # now; `adapted_bearing` is set only on the turn that changed it.
            "bearing": carried,
            "adapted_bearing": adapted_bearing,
            "provenance": {
                "method": ("offline pipeline — stored knowledge and current "
                           "readings through an add-and-norm stack, every "
                           "layer on the record; a configured model key "
                           "replaces this with real conversation")
                          if knowledge_entry is not None else
                          "model-generated coaching grounded in this user's "
                          "own check-ins and goals — general habits advice, "
                          "not professional counsel",
                # Who actually answered — not who was picked. The distinction
                # is the whole point: a silent degrade to the stub under a
                # screen that says Claude is how a founder demos canned text
                # to their testers without knowing it.
                "generated_by": gen["provider"],
                "degraded": gen["degraded"],
                "degraded_reason": gen["reason"],
                "evidence": (knowledge_entry or {}).get("references", []),
                # The stack itself, layer by layer, when it ran — each add
                # and each norm with what it contributed. A pipeline nobody
                # can audit is a claim, not a mechanism.
                "pipeline": pipeline_layers,
                "disclaimer": "For medical, legal, or investment decisions, "
                              "consult a qualified professional.",
            }}


def ask_specialist(user_id: str, area: str, message: str, qrme,
                   pdi=None) -> dict:
    """Send this person's own question to the QRME specialist for the area.

    The half of the tandem the coach never had. Until now a specialist was
    reachable only from `guardian._deliver` — the monitoring path — so the
    person whose watch noticed something got the better answer and the person
    who chose to ask got the local model.

        asked     can a specialist be reached
        mattered  can the person who asks reach one

    Called only from the route a person chose. `coach.reply` *offers*; nothing
    here runs on the way to an ordinary answer, and nothing here is reachable
    from escalation — `jim/handoff.py` states the rule and it holds for the
    same reason: a ladder that waits on a third party is worse than no ladder.

    Every refusal below returns rather than raises, and each says what happened
    and what was used instead. Somebody who asked a question gets an answer;
    the worst case is that it came from the Guardian alone.
    """
    from . import specialists

    if area not in AREAS:
        return {"delivered": False, "reason": f"unknown area {area!r}"}

    spec = specialists.for_area(area)
    if spec is None:
        return {"delivered": False, "area": area,
                "reason": "no specialist covers this area",
                "note": "the Guardian answers this one alone"}
    if qrme is None:
        return {"delivered": False, "area": area,
                "reason": "no QRME tandem is configured on this deployment",
                "note": "the Guardian answers this one alone"}

    user = guardian.get_user(user_id)
    if user is None:
        return {"delivered": False, "reason": "unknown user"}

    safe, why = guardian.tandem_safe(user, spec["qrme_profile_id"], qrme)
    if not safe:
        return {"delivered": False, "area": area, "reason": why,
                "note": "the Guardian answers this one alone"}

    interactor_id = guardian.interactor_for(user_id, user, qrme)
    try:
        reply = qrme.specialist_reply(
            spec["qrme_profile_id"], interactor_id, message)
    except RuntimeError as e:
        # QRME refused — its own age gate, its own moderation, its own outage.
        # Never leave somebody who asked a question with nothing.
        return {"delivered": False, "area": area, "reason": str(e),
                "note": "the Guardian answers this one alone"}

    content = reply.get("content")
    now = db.utcnow()
    conn = db.connect()
    # The person's own question and the specialist's answer land in the same
    # thread as the rest of the coaching. A conversation split across two
    # stores is a conversation somebody has to reassemble to understand what
    # they were told.
    conn.execute(
        "INSERT INTO coach_messages (id, user_id, area, role, content, created_at)"
        " VALUES (?,?,?,?,?,?)",
        (db.new_id("msg"), user_id, area, "user", message, now))
    if content:
        conn.execute(
            "INSERT INTO coach_messages (id, user_id, area, role, content, created_at)"
            " VALUES (?,?,?,?,?,?)",
            (db.new_id("msg"), user_id, area, "coach", content, now))
    conn.commit()

    continuity.observe(user_id, "coach_turn", length=len(message))
    guardian._event(user_id, "specialist_asked",
                    detail={"area": area,
                            "qrme_profile_id": spec["qrme_profile_id"],
                            "held": content is None})
    return {
        "delivered": content is not None,
        "area": area,
        "content": content,
        "specialist": {"label": spec["label"],
                       "qrme_profile_id": spec["qrme_profile_id"]},
        # Held rather than refused: QRME's moderation can hold a reply for its
        # owner's approval, and saying "no answer" would misdescribe a message
        # that exists and is waiting.
        "held_for_owner_approval": content is None,
        "provenance": {
            "method": "answered by a QRME specialist profile through the "
                      "tandem, not by JIM's own model",
            "shared": "the message you sent, and nothing else from your "
                      "record — no check-ins, no conditions, no medication",
        },
    }


def companion_checkin(user_id: str) -> dict:
    """An unprompted, ambient check-in: the coach reaches out first,
    grounded in the user's latest mood and goals. Opt-in by nature — it is
    only ever triggered by an explicit API call on the user's behalf."""
    user = guardian.get_user(user_id)
    recent = life.checkins(user_id)[-1:]
    mood_note = (f"their last check-in was mood {recent[0]['mood']}/5"
                 if recent else "they haven't checked in lately")
    system = _SYSTEM.format(
        area="ambient companionship — a brief, warm, unprompted check-in",
        context=_context(user_id))
    system += personalize(user)
    system += (f"\n\nYou are reaching out first ({mood_note}). One or two "
               "sentences, warm and unpressured; invite, never demand.")
    text = llm.provider_for_user(user_id).generate(system, "Reach out and check in.")

    if _DENY.search(text):
        return {"delivered": False, "reason": "failed safety check",
                "content": None}
    conn = db.connect()
    conn.execute(
        "INSERT INTO coach_messages (id, user_id, area, role, content,"
        " created_at) VALUES (?,?,?,?,?,?)",
        (db.new_id("msg"), user_id, "mental_health", "coach", text,
         db.utcnow()),
    )
    conn.commit()
    return {"delivered": True, "unprompted": True, "content": text}


def history(user_id: str, area: str | None = None) -> list[dict]:
    conn = db.connect()
    if area:
        rows = conn.execute(
            "SELECT * FROM coach_messages WHERE user_id=? AND area=?"
            " ORDER BY created_at, rowid", (user_id, area)).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM coach_messages WHERE user_id=?"
            " ORDER BY created_at, rowid", (user_id,)).fetchall()
    return [dict(r) for r in rows]
