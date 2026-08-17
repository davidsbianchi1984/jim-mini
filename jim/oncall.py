"""An aid on the call, and the notice that goes first.

:mod:`jim.mic` lends the agent a second microphone while a call occupies the
first, and it refuses the case this module is for, in as many words:

    not while the call is on speaker. On speaker the watch hears whoever you
    are talking to, and they are not a user here — they were never asked and
    could not revoke it

That refusal is right, and it is not weakened here. What it names is a person
who was never told. This module is the other case: the far side **is** told,
out loud, on the line, before anything listens.

    asked     may the agent be on this call
    mattered  does the other person know it is

## The 800-number shape, and the one place it improves on it

Everybody has heard *this call may be monitored or recorded*. Adopting a form
people already recognise beats inventing a careful new one: no explanation is
needed, and the remedy — hang up — is one they already know they have.

The **may** in that sentence is doing work for the company saying it, not for
the person hearing it. It is vague because the company will not commit. This
one knows exactly what the session is doing at the moment it speaks, so it
says the true sentence instead:

    This call is being monitored by an AI assistant to help. Nothing is
    being recorded.

and when a recording is on, the second sentence changes. :func:`notice_for`
builds it from the session's own state rather than choosing from a list, and a
guard holds that a recording session cannot announce that nothing is recorded.
That is the beacon-alarm rule in a different room: an alarm that says help was
called has to have called it.

## Two channels on one call, and only one of them announces

This is not an alternative to :mod:`jim.mic` — they are the two halves of the
same phone call, and which one is in use decides whether anything is
announced at all.

**Channel 2 is the private half.** The guardian listens on a worn microphone
and answers into an earpiece: the person gets their advice, their prompt,
the thing they had not thought to ask, and the other party hears none of it
and is captured in none of it. Nothing about them is heard, so there is
nothing to disclose and this module is not involved. That is a conversation
somebody is having with their own guardian while a call happens to be going
on, and it is the same act as asking it anything else.

**This module is the shared half.** The agent is on the call's own audio —
the speaker, the car, the conference — where the far side's voice is in the
room. That is a different act with a different obligation, and the notice is
what discharges it.

The line between them is *whether anything of the other person reaches the
agent*, and it is worth stating plainly because the two look identical from
outside: a phone, a person, and something helping. The failure would be to
treat the private half as if it needed announcing, which would tip somebody's
hand for no gain, or the shared half as if it did not.

## Notice, not permission

There is no consent flow here. Nothing waits for the far side to answer,
nothing records their agreement, and there is no state for *they objected* —
the notice plays and staying on the line is theirs to decide, exactly as it is
on every support line. That distinction is why this is five seconds instead of
a negotiation, and it is worth stating because the obvious next feature is a
yes/no prompt that would make the product worse and slower at once.

What *is* enforced is **ordering**. :func:`may_listen` refuses until the
notice has actually gone out, and it is the only door to listening. A call
that started hearing before it spoke is the failure this module exists to make
impossible.

## The far side is a person this product has no other record of

They have no account here and never will. So nothing about them is stored: no
number, no name, no voice print, no transcript attributed to them. What the
row holds is that a notice was given, when, and in what words — the evidence
that they were told, which is the one fact they would ever want established.
"""

from __future__ import annotations

import re

from . import contacts, db, i18n, liaison, schedule

#: What a person reads when something tried to listen too early. The words to
#: play are **not** in this sentence: they are a script for somebody else, in
#: somebody else's language, and they ride beside it as structure.
NOT_ANNOUNCED_YET = ("nothing is listening yet: the other person has not been "
                     "told. Play the notice on the line first")

#: Routes where more than one person can hear the room. This module exists for
#: these; a private route needs no announcement because nobody else is in it,
#: and `mic.handover` already covers that case.
SHARED_ROUTES = ("speaker", "speakerphone", "car", "conference")

#: The notice, in the words everybody has already heard on a support line.
#:
#: Deliberately the familiar script rather than a careful new sentence. A
#: person hearing this does not have to work out what it means or what they
#: can do about it — they have heard it a hundred times, they know it means
#: something is listening, and they know the remedy is to hang up. A better
#: sentence nobody recognises is a worse notice.
NOTICE = "This call may be monitored or recorded to better assist you."


#: Dialling code → the languages likely to be understood on the other end,
#: restricted to the ten this product speaks. A guess from the only clue a
#: call gives before anybody says hello, and treated as one: the clue is
#: recorded beside the notice so it can be seen and argued with.
#:
#: **Several, where the mix is known.** Picking one language for a country
#: that plainly has two is a coin toss with a person's understanding, and the
#: cost of being wrong is that the notice was noise. Saying it twice costs a
#: few seconds. So Switzerland gets German, French and Italian; Québec gets
#: French then English; Morocco gets Arabic then French. Order is *most
#: likely first* — somebody who understands the first one has already stopped
#: listening by the second, and that is fine.
#:
#: Longest prefix wins, because +1 and +1787 are both real answers about the
#: same number and only one of them is right.
_DIALLING: dict[str, tuple[str, ...]] = {
    # +1 is two countries and three languages. The bare code carries the
    # United States' own mix; the area codes below are the places inside it
    # where the answer is plainly something else.
    "1": ("en", "es"),
    "1418": ("fr", "en"), "1438": ("fr", "en"), "1450": ("fr", "en"),
    "1514": ("fr", "en"), "1579": ("fr", "en"), "1581": ("fr", "en"),
    "1819": ("fr", "en"), "1873": ("fr", "en"),               # Québec
    "1787": ("es", "en"), "1939": ("es", "en"),               # Puerto Rico
    "1809": ("es",), "1829": ("es",), "1849": ("es",),        # Dominican Rep.
    "33": ("fr",), "49": ("de",), "43": ("de",),
    "41": ("de", "fr", "it"),                                 # Switzerland
    "32": ("fr", "de"),                                       # Belgium
    "34": ("es",), "51": ("es",), "52": ("es",), "54": ("es",),
    "56": ("es",), "57": ("es",), "58": ("es",), "591": ("es",),
    "593": ("es",), "595": ("es",), "598": ("es",),
    "39": ("it",), "351": ("pt",), "55": ("pt",),
    "244": ("pt",), "258": ("pt",),
    "81": ("ja",), "86": ("zh",), "886": ("zh",),
    "852": ("zh", "en"),                                      # Hong Kong
    "91": ("hi", "en"),                                       # India
    "20": ("ar",), "218": ("ar",),
    "212": ("ar", "fr"), "213": ("ar", "fr"), "216": ("ar", "fr"),
    "962": ("ar",), "963": ("ar",), "964": ("ar",), "965": ("ar",),
    "966": ("ar",), "968": ("ar",), "972": ("ar",), "973": ("ar",),
    "974": ("ar",),
    "971": ("ar", "en"),                                      # UAE
}

#: Where a fallback language is spoken alongside another as a matter of
#: course, both go out. English is the case that matters: an English-speaking
#: deployment answering a number it knows nothing about is very likely
#: reaching somebody in the United States, where saying it in English and
#: Spanish is simply what a support line does. A notice the listener does not
#: speak is not a notice, and the second one costs three seconds.
_PAIRED: dict[str, tuple[str, ...]] = {"en": ("en", "es")}

_DIGITS = re.compile(r"\D+")


def language_for(number: str | None,
                 fallback: str) -> tuple[tuple[str, ...], str]:
    """Which languages to say it in, and what that was inferred from.

    The person who has to understand this notice is the one on the other end
    of the line, not the account holder — so the caller's own language is the
    wrong default and is only the fallback. The number is the one clue a call
    gives before anybody speaks.

    Returns the language and the clue, because a guess presented as knowledge
    is worse than a guess. The clue is what makes it correctable.

    **The number itself is used here and discarded.** It never reaches the
    caller of this function and is never stored — see the module note on the
    far side having no account here.
    """
    spoken = _PAIRED.get(fallback, (fallback,))
    digits = _DIGITS.sub("", number or "").lstrip("0")
    if not digits:
        return spoken, "no number to go on — said in the caller's language"
    for length in range(min(4, len(digits)), 0, -1):
        prefix = digits[:length]
        if prefix in _DIALLING:
            return _DIALLING[prefix], f"+{prefix}"
    return spoken, f"+{digits[:3]} is not one this product has a language for"


class NotAnnounced(RuntimeError):
    """Refused: nothing may listen before the notice has gone out."""


#: There is no such call. Translated rather than recorded: it is the answer
#: to an id that has gone stale, which is a thing a person meets by leaving a
#: screen open, not a thing they did wrong.
NO_SUCH_CALL = "no such call"


class NoSuchCall(ValueError):
    """No such assisted call."""


class NotAShared(ValueError):
    """Refused: that route has nobody else on it to announce to.

    Its own type rather than a bare `ValueError`, and the reason is a guard:
    this refusal carries a built sentence, and `ValueError` is caught in a
    dozen places across `api.py` that pass it on with `str(exc)` — which
    drops the template and sends it out in English. A sentence that knows how
    it was built needs an exception nobody catches by accident.
    """


class NotAShared(ValueError):
    """Refused: that route has nobody else on it to announce to.

    Its own type rather than a bare `ValueError`, and the reason is a guard:
    this refusal carries a built sentence, and `ValueError` is caught in a
    dozen places across `api.py` that pass it on with `str(exc)` — which
    drops the template and sends it out in English. A sentence that knows how
    it was built needs an exception nobody catches by accident.
    """


def notice_for(language: str = i18n.DEFAULT) -> str:
    """The words this call announces, in one language.

    Composed here rather than accepted from a caller: there is no path that
    lets a client decide what the far side is told, which is the whole reason
    this is a function and not a column.

    Said in a language the far side is likely to understand, through the same
    vocabulary every other closed set in this product goes through. A notice
    nobody on the line understands is not a notice; it is a noise that
    happened before listening started.
    """
    return i18n.term(NOTICE, language)


def open(user_id: str, route: str, recording: bool = False,
         number: str | None = None) -> dict:
    """Set up an assisted call. It is **not** listening yet.

    Returns the exact words to play on the line. Nothing here begins hearing
    anything: the session starts in the one state where it cannot, and the
    only way out of it is :func:`announced`.

    ``number`` is read for two things and then dropped. It is still not
    returned, not logged and not stored.

    The first is which language the notice should be spoken in; what the row
    keeps is the language chosen and the clue it came from, so the guess is
    visible and can be argued with.

    The second is **who this is**, asked of :mod:`jim.contacts` — this
    person's own address book, and nothing else. What the row keeps is the id
    of one of their own contacts, never the number, and a call matching
    nobody keeps nothing, exactly as before this existed. Where that contact
    also holds an account here and the two are already mutual contacts, the
    guardians open a link between themselves at dial time rather than waiting
    for somebody to press something.
    """
    if route not in SHARED_ROUTES:
        # Through the template every other closed-set refusal uses. The
        # reason a private route is refused belongs in the docstring and the
        # lesson, not welded onto a sentence somebody meets at a form field.
        raise NotAShared(i18n.fill(i18n.MUST_BE_ONE_OF, field="route",
                                   choices=",".join(SHARED_ROUTES)))
    languages, clue = language_for(number, i18n.get_language(user_id))
    # Who this is, from this person's own book. `known` is a row or None, and
    # None is the ordinary case — most numbers anybody rings are not in it.
    known = contacts.whose(user_id, number)
    # What actually goes out on the line, in order. Joined for the record
    # because the record's job is *what was said*, and what was said is all
    # of it.
    spoken = [{"language": lang, "words": notice_for(lang)}
              for lang in languages]
    said = " ".join(part["words"] for part in spoken)
    call_id = db.new_id("cal")
    conn = db.connect()
    conn.execute(
        "INSERT INTO assisted_calls (id, user_id, route, recording, notice,"
        " language, language_clue, contact_id, announced_at, opened_at)"
        " VALUES (?,?,?,?,?,?,?,?,NULL,?)",
        (call_id, user_id, route, int(recording), said, ",".join(languages),
         clue, known["id"] if known else None, db.utcnow()))
    conn.commit()
    return {"id": call_id, "listening": False, "route": route,
            "recording": recording, "notices": spoken, "said": said,
            "spoken_in": list(languages), "language_from": clue,
            "with_name": known["name"] if known else None,
            "liaison": _link_at_dial_time(user_id, known),
            "note": "play this on the line, then say it went out. Nothing "
                    "listens until it has"}


def _link_at_dial_time(user_id: str, known: dict | None) -> str | None:
    """Open the guardians' own link, where everything already says it may.

    Three conditions, none of them new and none of them asked at dial time:
    this person's book says the far side holds an account here, the two are
    already each other's contacts, and the permit to speak for somebody is
    on. :mod:`jim.liaison` checks the last two itself and refuses otherwise —
    which is why they are caught here rather than re-tested. A link that
    cannot open is not an error on a phone call: it is the ordinary case,
    and the call carries on without one.

    What this adds is only *when*. The link was always openable by hand
    afterwards; doing it here is what makes it true that the guardians were
    working from the moment the call started rather than from the moment
    somebody remembered to say so.
    """
    if not known or not known["jim_user_id"]:
        return None
    try:
        link = liaison.open(user_id, known["jim_user_id"],
                            about=WITH_A_CONTACT)
    except (liaison.NotMutual, liaison.NotAllowed):
        return None
    return link["id"]


#: What a link opened at dial time says it is about, until somebody says
#: otherwise. Not the contact's name: the far side reads their own half of
#: this link, and what one person calls their mother is not a label to hand
#: to somebody else's guardian.
WITH_A_CONTACT = "a call between us"


def get(call_id: str) -> dict:
    row = db.connect().execute(
        "SELECT * FROM assisted_calls WHERE id=?", (call_id,)).fetchone()
    if row is None:
        raise NoSuchCall(NO_SUCH_CALL)
    return dict(row)


def announced(call_id: str) -> dict:
    """The notice went out on the line. Now it may listen.

    Confirmed by the client that played it rather than assumed by the server
    that composed it: the server knows what *should* have been said, and only
    the thing holding the audio knows whether it was.
    """
    row = get(call_id)
    if row["announced_at"] is None:
        conn = db.connect()
        conn.execute("UPDATE assisted_calls SET announced_at=? WHERE id=?",
                     (db.utcnow(), call_id))
        conn.commit()
        row = get(call_id)
    return {"id": call_id, "listening": True,
            "announced_at": row["announced_at"], "said": row["notice"]}


def may_listen(call_id: str) -> None:
    """The chokepoint. One function, and the only door to hearing anything.

    Ordering rather than permission: it does not ask whether the far side
    agreed — they were never asked to — it asks whether they were **told**.
    """
    row = get(call_id)
    if row["announced_at"] is None:
        raise NotAnnounced({
            "reason": "not_announced",
            "message": NOT_ANNOUNCED_YET,
            # The script, in the language it has to be spoken in. Structure
            # rather than prose: a client plays it, a person does not read it.
            "say": row["notice"],
            "spoken_in": row["language"].split(","),
        })


def close(call_id: str, why: str = "ended") -> dict:
    """End it, and say plainly what the far side was told and when."""
    row = get(call_id)
    conn = db.connect()
    conn.execute("UPDATE assisted_calls SET ended_at=?, ended_because=?"
                 " WHERE id=? AND ended_at IS NULL",
                 (db.utcnow(), why, call_id))
    conn.commit()
    return {"id": call_id, "listening": False, "ended_because": why,
            "was_announced": row["announced_at"] is not None,
            "said": row["notice"]}


def _named(user_id: str, contact_id: str | None) -> str | None:
    """The name on a call, where the call had one and the book still does.

    Read at the last moment rather than copied onto the call row, so a
    contact somebody removed stops naming their old calls. The alternative —
    a name frozen into `assisted_calls` — would mean deleting a contact left
    their name behind in a table the person was not looking at.
    """
    if not contact_id:
        return None
    try:
        return contacts.one(user_id, contact_id)["name"]
    except contacts.NoSuchContact:
        return None


def remember(call_id: str, title: str, when: str,
             where: str | None = None) -> dict:
    """Book the thing the call was about, under the person it came from.

    The field ask, in its own words: *your user is on the phone with their
    mom, who doesn't have their own agent, and the mother gives them a date
    and time to be somewhere — so the user doesn't forget, it was being
    monitored and saved and stored under mom in the calendar.*

    That case is the ordinary one and it is why this exists. The far side has
    no account here and never will; what makes the appointment filed *under
    mom* possible is not their guardian but this person's own contact row.

    What survives is the appointment. Not a transcript, not a summary of the
    conversation, not the audio — there is nowhere in this product to put any
    of those, which is the point rather than an omission. A call that
    produced something to do leaves the thing to do.

    Listening rules still hold: this goes through :func:`may_listen`, so a
    call that never announced itself cannot have heard a date to book.
    """
    may_listen(call_id)
    row = get(call_id)
    booked = schedule.book(row["user_id"], {}, title, when, where=where)
    conn = db.connect()
    conn.execute("UPDATE appointments SET from_call_id=? WHERE id=?",
                 (call_id, booked["id"]))
    conn.commit()
    return {"id": booked["id"], "title": booked["title"],
            "when": booked["whenat"], "where": booked["whereat"],
            "from_call": call_id,
            "from_name": _named(row["user_id"], row["contact_id"])}


def left_behind(user_id: str, call_id: str) -> list[dict]:
    """What a call left: the appointments it produced, and nothing else.

    A deliberately short list. If this ever returns something that is not a
    thing to be done at a time, the rule this module is built on has been
    quietly dropped.
    """
    return [{"id": r["id"], "title": r["title"], "when": r["whenat"],
             "where": r["whereat"], "status": r["status"]}
            for r in db.connect().execute(
                "SELECT * FROM appointments WHERE user_id=? AND from_call_id=?"
                " ORDER BY whenat", (user_id, call_id)).fetchall()]


def history(user_id: str, limit: int = 20) -> list[dict]:
    """Assisted calls, newest first — and whether each one announced itself.

    A call that never announced and never listened is a real row and stays
    visible. It is the evidence that the ordering held.
    """
    return [{"id": r["id"], "route": r["route"],
             "recording": bool(r["recording"]), "said": r["notice"],
             "spoken_in": r["language"].split(","),
             "language_from": r["language_clue"],
             "with_name": _named(user_id, r["contact_id"]),
             "announced_at": r["announced_at"],
             "listened": r["announced_at"] is not None,
             "opened_at": r["opened_at"], "ended_at": r["ended_at"],
             "ended_because": r["ended_because"]}
            for r in db.connect().execute(
                "SELECT * FROM assisted_calls WHERE user_id=?"
                " ORDER BY opened_at DESC, rowid DESC LIMIT ?",
                (user_id, limit)).fetchall()]
