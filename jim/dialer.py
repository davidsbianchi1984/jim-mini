"""The emergency dialer — built to the send, and held shut there.

For everything above it, the emergency path is complete: a critical reading
goes unanswered, the companion assembles a dispatcher-ready briefing (who,
conditions, medications, vitals, the life-saving steps in progress), and it
is relayed to the trusted person and every connected device. The one thing
that never happened was a machine reaching a dispatcher directly. Every layer
said so in the same words — *this app cannot itself place a voice call*.

This module is that last piece, built the way the rest of the ladder is built
— it assembles the connection, chooses the number, and routes it — with one
line held: **the send does not send.** The owner's decision, in their words:
build it out so JIM can make the connections, but the dialer must not actually
place the call.

## The invariant, and where it lives

`SEND_ENABLED` is a source constant, and it is `False`. Not an environment
variable, not a database column, not a plan tier, not a waiver — a line in
this file, changed only by someone editing this file under review. The three
things that *do* gate the rest of the ladder (the ticked box, the crash-watch
arming, the account's plan) reach the assembly and the routing and stop at the
door of `place()`, which reads only this constant.

## Held, and loud — never silent

`place()` assembles the call and, with the send held, records a `dial.held`
event and returns a receipt that says plainly no call went out. It does **not**
quietly succeed and it does **not** quietly drop the intent: the connection is
real, the record is real, only the transmission is withheld.

And if the constant is ever flipped without a transport actually wired, the
send **raises** rather than pretends. There is no code path in this module
that emits to a network — a real dial needs a provider deliberately added
here, under the scrutiny the owner named. Flipping the flag alone buys a loud
failure, never a silent, unmonitored call. That is the safe direction for a
mistake to fall: a 911 line that fails closed, never one that dials open.
"""

from __future__ import annotations

import os

from . import audit

#: The one line. Real dialing is off, and turning it on is a source edit made
#: under review — never a runtime, waiver, or per-account decision. See the
#: module docstring: the rest of the ladder gates the assembly; only this
#: gates the send.
SEND_ENABLED = False

#: The North American emergency number JIM would reach. Kept as a named
#: constant rather than written into the call site so the one place a reader
#: checks "what would it dial" is unmistakable. It is never dialled today.
EMERGENCY_NUMBER = "911"

#: How a call can be carried. Two kinds, because the owner named two:
#:   * ``online`` — a VoIP/telephony provider places the call from the cloud.
#:     Dependable and headless (the "foolproof" path), and it bills per
#:     minute; it is the default for that reason.
#:   * ``device_sim`` — the call is placed through the user's own phone, on
#:     the SIM and cellular plan they already pay for. Near-free, but bound
#:     to that device being present and able.
TRANSPORT_KINDS = ("online", "device_sim")
DEFAULT_TRANSPORT_KIND = "online"

#: The online providers the seam can be pointed at — the outside services that
#: ring a phone, play speech, capture a keypad press, and stream a voice back.
#: The owner picks one; the code stays provider-agnostic so the choice is an
#: edit, not a rewrite.
PROVIDERS = ("twilio", "signalwire", "telnyx", "vonage", "plivo")

#: The default online provider, chosen to best suit an LLM voice agent that
#: needs outbound calls, spoken playback, two-way media, and DTMF (keypad)
#: capture with webhooks back into JIM. Twilio Programmable Voice covers all
#: of that with the widest support; the others are drop-in alternatives.
#: Set JIM_TELEPHONY_PROVIDER to switch, JIM_TELEPHONY_KIND to change kind.
DEFAULT_PROVIDER = "twilio"


def chosen_kind() -> str:
    picked = (os.environ.get("JIM_TELEPHONY_KIND") or "").strip().lower()
    return picked if picked in TRANSPORT_KINDS else DEFAULT_TRANSPORT_KIND


def chosen_provider() -> str:
    picked = (os.environ.get("JIM_TELEPHONY_PROVIDER") or "").strip().lower()
    return picked if picked in PROVIDERS else DEFAULT_PROVIDER


def transport_ready() -> bool:
    """Whether a real telephony transport is actually wired.

    False everywhere today: choosing a kind and a provider names *how* a call
    would go out, not that anything can yet — the online path needs the
    provider's SDK, credentials, and a number; the device path needs the
    phone's own dialer reached. That is the owner's infrastructure step. Kept
    as one honest question so no path pretends a call went out.
    """
    return False


class DialerArmedWithoutTransport(RuntimeError):
    """`SEND_ENABLED` was turned on, but no telephony transport is wired.

    Raised instead of dialing, so arming the flag on its own can only ever
    produce a loud failure — never a silent, unmonitored call. Wiring a real
    provider is a deliberate, reviewed act that adds a transport below; until
    then, on is a bug and this says so.
    """


def _transmit(connection: dict) -> dict:  # pragma: no cover - never reached
    """The seam a real telephony provider would fill.

    There is no provider today, on purpose. This function is only reached
    when `SEND_ENABLED` is True, and with nothing wired it refuses. A future
    integration replaces this body — and only this body — under the review
    the owner named, so the choke point stays exactly one function wide.
    """
    raise DialerArmedWithoutTransport(
        "the dialer is armed but no telephony transport is wired; refusing to "
        "pretend a call was placed")


def would_dial() -> str:
    """The number a call would reach, for a screen that wants to show the
    person what is held rather than only that something is."""
    return EMERGENCY_NUMBER


def place(connection: dict, *, user_id: str | None = None) -> dict:
    """Make the emergency connection — up to, and not including, the send.

    ``connection`` is the assembled, dispatcher-ready briefing the ladder
    built (who, situation, vitals, channels). This routes it to the number
    and then reads the one gate that matters:

    * held (today, always): record `dial.held`, return a receipt that says
      no call was placed and names what a person must do instead;
    * armed without a transport: raise, rather than pretend.

    The receipt never claims a call happened. A caller that wants to tell
    somebody help is coming has to reach a person the honest way — this
    returns the truth of what the machine did, which is: everything but dial.
    """
    routed = {
        "to": EMERGENCY_NUMBER,
        "briefing": connection,
        # A record a reader can replay: the connection was assembled and
        # routed, and the send was held. Not "nothing happened" — "everything
        # but the send happened".
        "assembled": True,
        "routed": True,
    }
    if not SEND_ENABLED:
        audit.record("dial.held", user_id=user_id, ref=EMERGENCY_NUMBER)
        return {
            **routed,
            "placed": False,
            "held": True,
            "reason": "the dialer is built and the connection is made, but "
                      "its send is held shut — this app does not place the "
                      "call. If this is an emergency, call your local "
                      "emergency number yourself.",
        }
    # Only reached if the source constant was flipped. With no transport
    # wired, this raises rather than dialing — the safe direction.
    result = _transmit(routed)
    return {**routed, "placed": True, "held": False, "transport": result}


def call_contact(to: str, opening: str, *, call_id: str | None = None) -> dict:
    """Place a call to a trusted emergency contact — a person, never 911.

    This is the allowed path: an emergency contact may actually be called,
    hear a JIM-composed opening, and answer. It is *not* policy-held the way
    :func:`place` is — there is no line here that must stay shut. What holds
    it today is only that no telephony transport is wired yet
    (:func:`transport_ready` is False): the call is assembled and routed to
    the chosen kind and provider, and returned as *prepared* with an id the
    response handlers key on, so the whole cascade runs and is documented
    while the literal ring waits on the transport the owner sets up.

    When a transport is wired, this is the one function that changes — it
    hands ``to`` and ``opening`` to the provider (or the device's own dialer)
    and returns the live call's id. The cascade above it does not change.
    """
    prepared = {
        "call_id": call_id,
        "to": to,
        "kind": chosen_kind(),
        "provider": chosen_provider() if chosen_kind() == "online" else None,
        "opening": opening,
        "assembled": True,
        "routed": True,
    }
    if transport_ready():  # pragma: no cover - no transport wired yet
        raise DialerArmedWithoutTransport(
            "a telephony transport reports ready but none is wired; refusing "
            "to pretend a contact call was placed")
    where = (chosen_provider() if chosen_kind() == "online"
             else "the user's own phone")
    return {**prepared, "placed": False, "prepared": True,
            "reason": f"the contact call is composed and routed via "
                      f"{chosen_kind()} ({where}); the ring waits on a "
                      "telephony transport being wired."}


def posture() -> dict:
    """What the dialer is, said plainly for a status screen or a reviewer.

    A screen can show that the connection is built, how a call would be
    carried, and that the 911 send stays shut — without implying any call
    will go out.
    """
    return {
        "built": True,
        "send_enabled": SEND_ENABLED,
        "would_reach": EMERGENCY_NUMBER,
        "transport_kind": chosen_kind(),
        "transport_kinds": list(TRANSPORT_KINDS),
        "provider": chosen_provider(),
        "providers": list(PROVIDERS),
        "transport_ready": transport_ready(),
        "note": "emergency contacts may be called once a telephony transport "
                "is wired; the 911 send is held shut in source and cannot be "
                "opened by a setting, a plan, or a waiver — only by a reviewed "
                "change to jim/dialer.py that also wires a transport.",
    }
