"""Offline mode: the zero-internet guarantee, enforced rather than assumed.

Set ``JIM_OFFLINE=1`` and nothing this product sends may leave the machine or
its own network.

`llm.py` has said "**Offline is absolute.** In ``JIM_OFFLINE`` mode every
network provider is bypassed" since the model picker was written, and it was
true of the model picker. It was not true of the product:

* ``voice.py`` posts the Guardian's spoken guidance — health text — to
  ElevenLabs or OpenAI;
* ``notify.py`` posts an incident envelope to an escalation webhook;
* ``mailer.py`` opens SMTP to a configured host;
* ``oauth.py``, ``qrme_client.py`` and ``pdi_client.py`` each call out.

None of them consulted the flag, and the flag itself was a private helper
duplicated in two modules rather than a place a new caller would find.

    asked     is every network *provider* offline
    mattered  is every network *path*

## Local is the test, not silence

Offline means *nothing leaves the machine*, not *nothing opens a socket*. An
Ollama daemon on loopback, an on-prem vault, an escalation webhook on the LAN
are all on this side of the wire. Refusing those outright would silence the
escalation path — and this product's own plan-gate refusal promises, in nine
languages, that emergency paths are never affected.
"""

from __future__ import annotations

import ipaddress
import os
import socket
import urllib.parse

_TRUTHY = {"1", "true", "yes", "on"}


def enabled() -> bool:
    return os.environ.get("JIM_OFFLINE", "").strip().lower() in _TRUTHY


class LeftTheHost(RuntimeError):
    """Refused: this would have sent something to another machine.

    Raised rather than returned. A caller that could ignore the answer is a
    caller that will, and the guarantee this module makes is absolute.
    """


def is_local(host: str | None) -> bool:
    """Is this host the machine we are running on, or its own network?

    Loopback and the private ranges — the on-prem PDI vault, a webhook on the
    LAN, an Ollama daemon on 127.0.0.1. Everything else is another party.

    A name that does not resolve is **not** local. Failing closed is the only
    safe direction: an unresolvable name in offline mode is either a typo or a
    host that is not there, and neither is a reason to try the connection.
    """
    if not host:
        return False
    name = host.strip().strip("[]").lower()
    if name in ("localhost", "localhost.localdomain"):
        return True
    try:
        addresses = [ipaddress.ip_address(name)]
    except ValueError:
        try:
            addresses = [ipaddress.ip_address(info[4][0])
                         for info in socket.getaddrinfo(name, None)]
        except (socket.gaierror, ValueError, UnicodeError):
            return False
    return bool(addresses) and all(
        a.is_loopback or a.is_private or a.is_link_local for a in addresses)


def allow(url: str | None, what: str) -> None:
    """Refuse a URL that would leave this host while offline mode is on.

    ## Why this is a host check and not a blanket refusal

    Offline mode means *nothing leaves the machine*, not *nothing opens a
    socket*. The three things this platform legitimately talks to when offline
    are all on the same side of the wire: an Ollama daemon on loopback, the
    on-prem PDI vault, an escalation webhook on the LAN. Two of those were
    already documented as local, and none of them was checked. They were
    assumptions about how somebody would deploy, written as if they were
    properties of the code.

        asked     is every network provider offline
        mattered  is every network path

    Blanket refusal would also have been wrong in a way that matters: it would
    have silenced the escalation webhook, and this product's own plan-gate
    refusal promises in nine languages that emergency paths are never affected.

    Callers pass the URL they are about to open and a short name for what it
    is; the name is what a person reads in the refusal.
    """
    if not enabled():
        return
    host = urllib.parse.urlsplit(url or "").hostname
    if is_local(host):
        return
    where = host or "an unnamed host"
    raise LeftTheHost(
        f"offline mode is on, so {what} cannot reach {where}. Nothing leaves "
        "this machine while JIM_OFFLINE is set — point it at a host on this "
        "network, or turn offline mode off.")


def allow_host(host: str | None, what: str) -> None:
    """`allow` for the things that are not URLs. SMTP is a host and a port."""
    if not enabled():
        return
    if is_local(host):
        return
    where = host or "an unnamed host"
    raise LeftTheHost(
        f"offline mode is on, so {what} cannot reach {where}. Nothing leaves "
        "this machine while JIM_OFFLINE is set.")


def status(app=None) -> dict:
    """The posture, for a deployment that has to prove it.

    Not routed yet in this product — QRME exposes the equivalent at
    `GET /offline/status` and this one has no endpoint. Written down as a
    function rather than left absent so the answer exists in one place and a
    route can read it, instead of a screen recomputing the guarantee from the
    environment and getting it slightly different.
    """
    off = enabled()
    cloud = getattr(getattr(app, "state", None), "cloud", None)
    return {
        "offline": off,
        "cloud_attached": (cloud is not None) and not off,
        # The core promise, and the one this module was built to make true:
        # while offline mode is on, every path out of this host refuses any
        # address that is not this machine or its own network.
        "external_transmission_possible": not off,
        "local_destinations_allowed": (
            "loopback, private and link-local addresses — an on-prem sibling, "
            "a webhook on the LAN, a model daemon on 127.0.0.1"),
        "guarantees": ([
            "no model API calls",
            "no cloud gateway calls",
            "no third-party speech, mail, sign-in or webhook delivery",
        ] if off else [
            "local provider always available as fallback",
            "outbound use is opt-in and revocable",
        ]),
    }
