"""Seeing — what a monitor with a lens perceives, put into words.

The counterpart to :mod:`jim.voice`. That module is this deployment's
ears: recorded speech goes out to be recognised and comes back as text,
and no recording is ever written down here. This is its eyes, on exactly
the same terms — a frame goes out to be described and comes back as one
sentence, and no frame is written down here either.

    asked     what is the monitor looking at
    mattered  does anything but the sentence survive the looking

## Why the words, and not the picture

Half this product's roster promises to keep nothing. `screen` says *what
it notices is offered and dropped*; `room_camera` and `glasses` keep
nothing unless somebody switches keeping on. Those promises are only
worth the paper they are on if the thing that does the noticing does not
quietly need the picture in order to notice.

So the shape is: describe first, in this module, holding the frame for
the length of one HTTP request; hand the *sentence* to
:func:`jim.daybook.sensed`; and let the roster decide whether even that
survives. `jim/cues.py` reads its cues from that sentence before the
retention question is asked, which is what lets a monitor that keeps
nothing still be worth having.

A frame never reaches the database on any path in this codebase. There is
no column to put one in, and `describe` returns a string, so there is
nothing for a caller to accidentally store.

## What leaves the host, and when

Nothing, unless somebody switched a monitor on and something looked. The
call goes through :func:`jim.offline.allow` like every other outbound
path here, so a deployment running with ``JIM_OFFLINE=1`` refuses it by
the same rule that refuses transcription — and says so in a sentence,
rather than sending the frame and hoping.

Where no key is configured the answer is a refusal, not a guess. A
Guardian that invents what it thinks is on a screen is worse than one
that admits it cannot see: the invention would reach `cues.py`, and a
cue read out of a hallucination is an escalation nobody's day contained.
"""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.request

from . import i18n

#: Long enough for a vision model on a busy afternoon, short enough that a
#: screen sampling every few seconds cannot pile requests up behind itself.
_TIMEOUT = int(os.environ.get("JIM_SIGHT_TIMEOUT", "30"))

#: The model asked to look. Overridable because the good one changes every
#: few months and a deployment should not need a new release to follow it.
_MODEL = os.environ.get("JIM_SIGHT_MODEL", "gpt-4o-mini")

#: What the model is told it is doing. Deliberately narrow: this is a
#: health guardian looking at somebody's own screen or room, not a
#: transcription service and not a search engine. One plain sentence is
#: the whole contract — anything longer gets stored nowhere and read by
#: nobody, and anything speculative reaches the cue reader as though it
#: were something that happened.
SYSTEM = (
    "You are the eyes of a personal health guardian, looking at one frame "
    "from a monitor its owner switched on. Say in one plain sentence what "
    "is there — what is happening, and anything a companion would notice "
    "about the person's situation or wellbeing. Describe only what you can "
    "see. Never guess at intent, never read out passwords, card numbers or "
    "anything that looks like a credential, and if the frame shows nothing "
    "worth remarking on, say so plainly."
)


class SightError(Exception):
    """The service was reachable in principle and said no."""


class SightUnavailable(SightError):
    """Nothing is configured to look. A refusal, never a guess."""


def _key() -> str:
    """The key this deployment looks with.

    The same OpenAI key the rest of the house already uses, read from the
    environment rather than given a settings screen of its own: a second
    place to put the same key is a second place for it to be wrong.
    """
    return (os.environ.get("JIM_SIGHT_API_KEY", "")
            or os.environ.get("OPENAI_API_KEY", ""))


def configured() -> bool:
    """Whether anything is set up to look. Read by the posture doors so a
    screen can say *waiting on a key* instead of *sensing*."""
    return bool(_key())


def describe(frame: bytes, asked: str = "", kind: str = "image/jpeg") -> str:
    """One frame, one sentence. The frame is not stored anywhere.

    `asked` narrows the looking for a monitor that has a particular
    question — a room camera watching for a fall asks a different question
    from a screen — and is appended to :data:`SYSTEM` rather than
    replacing it, so no caller can talk the eyes out of their limits.
    """
    key = _key()
    if not key:
        raise SightUnavailable(
            "nothing is set up to look: this deployment has no key for "
            "describing what a camera or a screen sees. The monitor stays "
            "switched on and reports nothing until one is added")
    if not frame:
        raise SightError("there was no frame in that")
    told = SYSTEM + (f" This monitor is watching for: {asked}." if asked else "")
    url = "https://api.openai.com/v1/chat/completions"
    body = json.dumps({
        "model": _MODEL,
        "max_tokens": 160,
        "messages": [
            {"role": "system", "content": told},
            {"role": "user", "content": [{
                "type": "image_url",
                "image_url": {"url": f"data:{kind};base64,"
                                     + base64.b64encode(frame).decode()},
            }]},
        ],
    }).encode()
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"authorization": f"Bearer {key}",
                 "content-type": "application/json"})
    # Before the `try`, deliberately — the same ordering as `voice.transcribe`
    # and for the same reason: a refusal swallowed into the clauses below
    # would read as the service being unreachable rather than as nothing
    # having been sent. The purpose names what actually leaves: one frame,
    # sent to be described.
    from . import offline

    offline.allow(url, "describing one frame from a monitor")
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            data = json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:300]
        raise SightError(i18n.fill(i18n.SIGHT_REFUSED,
                                   code=exc.code, detail=detail))
    except (urllib.error.URLError, TimeoutError) as exc:
        raise SightError(i18n.fill(i18n.SIGHT_UNREACHABLE, why=exc))
    choices = data.get("choices") or [{}]
    said = ((choices[0].get("message") or {}).get("content") or "").strip()
    return said
