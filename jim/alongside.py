"""Beside somebody while they write, rather than waiting to be asked.

The field ask, verbatim: *as you're typing out a sales page to a customer, or
writing a strategy doc, to just jump in and say hey you forgot about this, or
here's maybe another idea, or you should consider this, I can do this thing to
help.*

Three remarks, and they are the three in that sentence:

    forgot   something already in this person's own records that the draft
             does not mention
    angle    something the coach knows about the subject that the draft is
             not using
    offer    a thing this product can actually do for the part they are on

    asked     can it answer about a draft
    mattered  does it notice the thing they would have wanted noticing

## It does not decide anything, and it does not touch the draft

Nothing here writes. The draft arrives, remarks come back, and applying one is
the person's own act — there is no path in this module that edits, replaces or
stores what somebody is writing. A guard holds that: this module contains no
`INSERT`, and the routes above it return remarks and nothing else.

**The draft is not kept.** Not in a table, not in a log, not as an embedding.
It is read, remarked on, and dropped. That is the difference between a thing
sitting beside somebody and a thing recording them, and it is worth more than
any feature that keeping it would buy.

## It stays quiet when it has nothing

A companion with a remark on every paragraph is a paperclip, and people turn
those off. :func:`read` returns no remarks rather than filler, with the reason
it found nothing — the same posture :func:`jim.presence.beat` takes, for the
same reason.

## Every remark carries its evidence

*You forgot about this* with nothing under it is a guess wearing a suggestion's
clothes. Each remark names what it came from — the goal, the check-in, the
store entry and where that entry came from — so the person can see whether the
thing being pointed at is really theirs, and dismiss it on the spot when it is
not.

## Local, and this is where that stops being a slogan

Everything here runs on this device: the store the offline coach predicts
from, the person's own goals and check-ins, and nothing else. No provider, no
socket. What somebody is drafting for a customer is the most commercially
sensitive text they own, and the honest way to be trusted with it is to have no
way to send it anywhere.

## What this is not

It is **not** watching a screen. It reads a draft handed to it, in a request
somebody made. A guardian that reads whatever is in front of you, continuously,
is a different thing with a different consent — and where somebody else's words
can end up in the window, a different set of questions again. Nothing here
opens that door.
"""

from __future__ import annotations

import re

from . import knowledge, life, pipeline

#: Below this, say nothing. Two hits on a long draft is noise; the number is
#: small because the cost of a wrong remark is that the next right one is
#: ignored.
_MIN_WORDS = 25

#: What a remark can be. Named here rather than as loose strings, so a client
#: can branch on the kind and a fourth cannot arrive without a decision.
KINDS = ("forgot", "angle", "offer")

_WORD = re.compile(r"[a-z][a-z'-]+")


def _words(text: str) -> set[str]:
    return {w for w in _WORD.findall((text or "").lower()) if len(w) > 3}


def _mentions(draft: set[str], phrase: str) -> bool:
    """Whether the draft already covers this, generously.

    Generous on purpose: the failure that matters is telling somebody they
    forgot a thing that is in their second paragraph. Missing a remark costs
    nothing; making a wrong one costs the next right one.
    """
    keys = _words(phrase)
    if not keys:
        return True
    return len(keys & draft) >= max(1, len(keys) // 2)


def _offers(user_id: str, draft: set[str]) -> list[dict]:
    """Things this product can actually do for the part they are on.

    Only doors that exist. An offer to do something unbuilt is worse than
    silence: it is a promise made by a screen on behalf of code nobody wrote.
    """
    out = []
    if draft & {"interview", "interviews", "candidate", "hiring", "question"}:
        out.append({"kind": "offer", "says": "I can deal you an interview "
                                             "question and read your answer "
                                             "back",
                    "door": "drills", "because": ["the draft is about "
                                                  "interviewing"]})
    if draft & {"week", "weekly", "summary", "recap", "review"}:
        out.append({"kind": "offer", "says": "I can write your week from what "
                                             "you actually logged",
                    "door": "letter", "because": ["the draft is about a week "
                                                  "in review"]})
    return out


def read(user_id: str, draft: str, area: str | None = None) -> dict:
    """Read a draft and say what is worth saying, or say nothing.

    Returns ``remarks`` — possibly empty — and ``quiet_because`` when it is.
    An empty list with no reason would leave a person unable to tell *it had
    nothing to add* from *it did not run*.
    """
    words = _words(draft)
    if len(words) < _MIN_WORDS:
        return {"remarks": [], "quiet_because":
                "there is not enough here yet to have an opinion about"}

    remarks: list[dict] = []

    # -- forgot: their own records, missing from the page --------------------
    for goal in [g for g in life.goals(user_id) if g["status"] == "active"]:
        if area and goal["area"] != area:
            continue
        if _mentions(words, goal["title"]):
            continue
        remarks.append({
            "kind": "forgot", "says": goal["title"],
            "because": [f"an active goal in {goal['area']} that this does "
                        "not mention"]})

    # -- angle: what the coach knows about this subject ----------------------
    store = pipeline.store(user_id)
    for entry in store["excursions"] + store["deposits"]:
        if not (_words(entry["topic"]) & words):
            continue
        if _mentions(words, entry["lesson"][:120]):
            continue
        remarks.append({
            "kind": "angle", "says": entry["topic"],
            # Provenance travels with the remark. "Something I read" and
            # "something a paid model said once" are different claims, and
            # the person deciding whether to use it is entitled to which.
            "because": [f"{entry['source']} — already in what I know"]})
    known = knowledge.search(draft, area)
    if known and not _mentions(words, known["guidance"][:120]):
        remarks.append({"kind": "angle", "says": known["topic"],
                        "because": ["the hand-written pack, on this subject"]})

    remarks.extend(_offers(user_id, words))

    # Three at most. A margin full of remarks is a margin nobody reads, and
    # the fourth-best thing this could say has never been worth the first
    # three being ignored.
    remarks = remarks[:3]
    return {"remarks": remarks,
            "quiet_because": None if remarks else
            "nothing here that you have not already covered"}
