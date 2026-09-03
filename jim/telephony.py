"""The JIM side of the phone line — the voice door, and the number rules.

The reach-out cascade (:mod:`jim.reachout`) was built to the ring and held
there: every contact call came back *prepared* because no telephony
transport was wired. This is the transport's JIM half. The vendor — the
phone house that actually rings a number, speaks, listens and reports —
lives one hop away in the stack's **voice sidecar** (`docker/voice` in the
compose stack), the same shape as the camera and the ears: JIM speaks one
small protocol to it and never a vendor SDK, the vendor's credential never
enters this process, and swapping the house is a change in one file over
there.

    asked     can JIM ring an emergency contact
    mattered  does anything here pretend it did

## What this module is, and is not

It is the only code in JIM that talks to the voice door: :func:`place` hands
a prepared contact call over and answers with the house's reference for it;
:func:`standing` proves — not reads off the environment — that the door
answers, is keyed, has a number to ring from, can be reached by the house's
webhooks, and holds the same secret JIM does; :func:`line` is the envelope
every spoken sentence rides in, so the sidecar composes no prose of its own.

It is not the 911 dialer. :func:`jim.dialer.place` never touches this
module — a test pins that by reading the source — and
:func:`refuse_unless_dialable` refuses an emergency short code before a
request is ever built, the lock above the sidecar's own refusal and beneath
the dialer's held send. Three refusals, each tested; none of them a setting.

## Honest at every edge

No door configured, offline mode on, or the device path chosen: nothing is
attempted and :func:`why_not` says which. The door configured but not
answering: :class:`SidecarUnreachable`, which the dialer raises as its loud
`DialerArmedWithoutTransport` — the cascade records the leg as *unplaced*
and moves on, never a pretended ring. The house refusing a number, the
adapter refusing JIM's secret, a provider mismatch: :class:`NotPlaced`,
carrying the sentence the sidecar said, onto the leg's record.
"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request

from . import dialer, i18n, offline
from .dialer import CallNotPlaced

#: Product-side ceilings, carried in every placement so the house never
#: decides them — the film sidecar's discipline.
RING_SECONDS = 25
MAX_CALL_SECONDS = 600
MAX_TURNS = 12
MACHINE_DETECTION = True
#: How long a proven standing is believed before the door is asked again.
STANDING_CACHE_S = 30
#: The wire's budget. The sidecar gives the house 8 s to take a call and
#: its own cold proof up to three 3 s probes; JIM waits longer than either,
#: so a slow answer is never recorded as no answer — a leg the house rang
#: after JIM gave up on it would be a second contact rung in parallel. The
#: whole chain still fits inside the 15 s a house gives a webhook.
PLACE_TIMEOUT_S = 10.0
STANDING_TIMEOUT_S = 10.0

#: Short codes this transport will never ring, with or without a leading 1
#: or a plus. The dialer holds 911 in source; this is the lock above the
#: sidecar's own, for every emergency number a contact's channel could hold.
EMERGENCY_NUMBERS = frozenset(
    {"911", "112", "999", "000", "111", "119", "110", "122", "15", "17", "18"})

#: The `then` words a line envelope may carry — the whole of what the
#: sidecar's line machine understands.
THEN = ("gather_digit", "speak_first", "gather_speech", "hangup")


class RefusedNumber(CallNotPlaced):
    """The channel is not a number this transport will dial."""


class NotPlaced(CallNotPlaced):
    """The voice door answered, and the answer was not a call."""


class SidecarUnreachable(CallNotPlaced):
    """The voice door did not answer at all."""


# --------------------------------------------------------------------------- #
# configuration, said honestly
# --------------------------------------------------------------------------- #

def url() -> str | None:
    return (os.environ.get("JIM_VOICE_URL") or "").strip().rstrip("/") or None


def secret() -> str | None:
    return (os.environ.get("JIM_VOICE_SECRET") or "").strip() or None


def configured() -> str | None:
    """The voice door's address when a call may actually go out: door and
    secret set, the online kind chosen, and offline mode off. None otherwise
    — and :func:`why_not` says which."""
    if offline.enabled():
        return None
    if dialer.chosen_kind() != "online":
        return None
    if not url() or not secret():
        return None
    return url()


def why_not() -> str | None:
    if offline.enabled():
        return ("offline mode is on, so the contact call stays home — nothing "
                "leaves this machine while JIM_OFFLINE is set")
    if dialer.chosen_kind() != "online":
        return ("the device path (calling through the person's own phone) is "
                "not wired this round")
    if not url() or not secret():
        return "no telephony transport is configured"
    return None


# --------------------------------------------------------------------------- #
# the number rules
# --------------------------------------------------------------------------- #

def normalize(to: str) -> str:
    """A channel as the house wants it: no spaces, dashes, dots or
    parentheses; `00` becomes `+`; a bare North American number gets its
    `+1`."""
    raw = re.sub(r"[\s\-.()]", "", (to or "").strip())
    if raw.startswith("00"):
        raw = "+" + raw[2:]
    digits = raw[1:] if raw.startswith("+") else raw
    if not raw.startswith("+") and len(digits) == 10 and digits.isdigit():
        return "+1" + digits
    if not raw.startswith("+") and len(digits) == 11 and digits.startswith("1") \
            and digits.isdigit():
        return "+" + digits
    return raw


def refuse_unless_dialable(to: str) -> str:
    """The normalised number, or a refusal in words. An email is not a
    number; an emergency short code is never rung by this transport."""
    if "@" in (to or ""):
        raise RefusedNumber(
            "the contact's channel is not a phone number this transport can dial")
    number = normalize(to)
    digits = number[1:] if number.startswith("+") else number
    # Checked on the raw digits too, before the `00` rule could turn a short
    # code into something that merely looks unroutable.
    bare = re.sub(r"[^0-9]", "", to or "")
    for candidate in (digits, bare):
        if candidate in EMERGENCY_NUMBERS or (
                candidate.startswith("1") and candidate[1:] in EMERGENCY_NUMBERS):
            raise RefusedNumber(
                "this transport carries calls to people, never to emergency "
                "services")
    # ASCII digits only: str.isdigit accepts other scripts' numerals, and a
    # house does not.
    if not re.fullmatch(r"[0-9]{7,15}", digits):
        raise RefusedNumber(
            "the contact's channel is not a phone number this transport can dial")
    return number


# --------------------------------------------------------------------------- #
# the wire — one function opens it
# --------------------------------------------------------------------------- #

def _request(method: str, path: str, body: dict | None = None,
             timeout: float = 5.0) -> tuple[int, dict]:
    """One request to the voice door. The single monkeypatch point, and the
    one place a socket opens — past the offline gate, with the bearer."""
    base = url()
    if not base:
        raise SidecarUnreachable("no telephony transport is configured")
    target = base + path
    offline.allow(target, "placing a contact call")
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        target, data=data, method=method,
        headers={"authorization": f"Bearer {secret() or ''}",
                 "content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            status = resp.status
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace") if exc.fp else ""
        status = exc.code
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        raise SidecarUnreachable(
            f"the voice door at {base} did not answer: {exc}") from None
    try:
        parsed = json.loads(raw) if raw else {}
    except ValueError:
        parsed = {"detail": raw[:200]}
    if not isinstance(parsed, dict):
        parsed = {"detail": str(parsed)[:200]}
    if status >= 500:
        raise SidecarUnreachable(
            f"the voice door at {base} answered {status}: "
            f"{parsed.get('detail') or raw[:200]}")
    return status, parsed


def place(call_id: str, to: str, opening: str, language: str = "en") -> dict:
    """Hand a prepared contact call to the voice door.

    Refuses the number first (no request for an email or an emergency
    code); then anything but a 201 that says `placed` with a reference is
    :class:`NotPlaced` carrying the door's sentence, and a door that does not
    answer is :class:`SidecarUnreachable`.
    """
    number = refuse_unless_dialable(to)
    status, body = _request("POST", "/calls", {
        "call_id": call_id, "to": number, "opening": opening,
        "language": language, "provider": dialer.chosen_provider(),
        "limits": {"ring_seconds": RING_SECONDS,
                   "max_call_seconds": MAX_CALL_SECONDS,
                   "machine_detection": MACHINE_DETECTION}},
        timeout=PLACE_TIMEOUT_S)
    if status != 201 or not body.get("placed") or not body.get("provider_call_id"):
        raise NotPlaced(str(body.get("detail") or
                            "the voice door answered without a call to follow"))
    return {"provider": body.get("provider") or dialer.chosen_provider(),
            "provider_call_id": str(body["provider_call_id"])}


# --------------------------------------------------------------------------- #
# the proof
# --------------------------------------------------------------------------- #

_STANDING: dict = {"at": 0.0, "value": None}


def _held(word: str, note: str, fix: str | None = None) -> dict:
    return {"word": word, "reachable": False, "authenticated": None,
            "provider_reported": None, "from_number": False, "webhooks": None,
            "note": note, "fix": fix, "checked_at": None}


def standing(force: bool = False) -> dict:
    """Whether the line would ring, proven at the read and cached briefly —
    PDI's `model_standing` shape. Never raises: this feeds a posture read,
    and a status door that can take its page down is pointed the wrong way."""
    if offline.enabled():
        return _held("held_offline", why_not() or "offline mode is on")
    if dialer.chosen_kind() != "online":
        return _held("unwired", why_not() or "the device path is not wired")
    if not configured():
        return _held("unconfigured", why_not() or "no telephony transport is "
                     "configured",
                     "set JIM_VOICE_URL and JIM_VOICE_SECRET")
    now = time.monotonic()
    if not force and _STANDING["value"] is not None and \
            now - _STANDING["at"] < STANDING_CACHE_S:
        return dict(_STANDING["value"])
    try:
        # A forced read forces the sidecar's own probes too, not just this
        # cache — "Check the line" means check it now.
        status, body = _request("GET", "/standing?force=1" if force else
                                "/standing", timeout=STANDING_TIMEOUT_S)
    except SidecarUnreachable as exc:
        value = _held("unreachable", str(exc),
                      "check the voice container is running and JIM_VOICE_URL "
                      "points at it")
    else:
        if status in (401, 403):
            value = _held("secret_mismatch",
                          "the adapter refused JIM's secret — JIM_VOICE_SECRET "
                          "differs between the jim and voice containers",
                          "set the same JIM_VOICE_SECRET for both containers "
                          "and restart them")
        else:
            word = str(body.get("word") or "unreachable")
            reported = body.get("provider")
            note = body.get("detail")
            fix = body.get("fix")
            if word == "ready" and reported and reported != dialer.chosen_provider():
                word = "mismatched"
                note = (f"the adapter is keyed for {reported}, not "
                        f"{dialer.chosen_provider()}")
                fix = "set JIM_TELEPHONY_PROVIDER to match"
            if word == "ready" and body.get("jim_secret_accepted") is False:
                word = "secret_mismatch"
                note = ("the adapter's probe of JIM's own door was refused — "
                        "JIM_VOICE_SECRET differs between the jim and voice "
                        "containers")
                fix = ("set the same JIM_VOICE_SECRET for both containers and "
                       "restart them")
            value = {"word": word, "reachable": True,
                     "authenticated": body.get("authenticated"),
                     "provider_reported": reported,
                     "from_number": bool(body.get("from_number")),
                     "webhooks": body.get("webhooks"),
                     "note": None if word == "ready" else note,
                     "fix": None if word == "ready" else fix,
                     "checked_at": body.get("checked_at")}
    _STANDING.update(at=now, value=value)
    return dict(value)


def forget_standing() -> None:
    _STANDING.update(at=0.0, value=None)


# --------------------------------------------------------------------------- #
# the words the line speaks on its own
# --------------------------------------------------------------------------- #

def phrases(language: str = "en") -> dict:
    """The fixed sentences the sidecar may speak without asking JIM — the
    re-prompt, the opt-out, the no-choice, the silence prompt, the closing,
    and the trouble line — in the given language."""
    lang = language if language in i18n.SUPPORTED else "en"
    return {key: (rows.get(lang) or rows["en"])
            for key, rows in i18n._SPOKEN_LINES.items()}


def line(then: str, say: str, language: str = "en", *,
         again: str | None = None, close: str | None = None,
         trouble: str | None = None) -> dict:
    """The envelope every spoken sentence rides in. `then` names what the
    sidecar does after saying it; `again`, `close` and `trouble` are the
    sidecar-only branches' words, so it never composes prose of its own."""
    if then not in THEN:
        # A programmer's mistake, never a person's — not a refusal a route
        # stringifies, so not a ValueError: the four words are THEN.
        raise LookupError("a line's then is not one of the four then words")
    return {"say": say, "then": then, "language": language,
            "again": again, "close": close,
            "trouble": trouble if trouble is not None
            else phrases(language)["trouble"]}
