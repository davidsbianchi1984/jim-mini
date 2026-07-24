"""Operating the Guardian from a phone.

The console in ``app/`` is a web app, so a phone on the same network can run
it directly from this backend — no app store, no separate dev server. Two
pieces make that work:

* :func:`console_dir` — the built console (``app/dist``), mounted by the API
  at ``/app`` when it has been built. Serving it from the API means the phone
  loads the UI and calls the API on **one origin**, so there is no CORS setup
  and no "which host is the backend?" question: the console defaults to the
  origin it was served from.
* :func:`pairing` — what to type (or scan) on the phone. It resolves the
  machine's LAN address so the answer is a URL the phone can actually reach,
  rather than ``127.0.0.1``, which on a phone means the phone itself.

Nothing here changes the security posture: the API still requires the user's
bearer token for anything personal, and a phone on the LAN is exactly as
authorized as a laptop on the LAN.
"""

from __future__ import annotations

import os
import socket
from pathlib import Path


def console_dir() -> Path | None:
    """The built console directory, or None when it hasn't been built yet
    (``npm --prefix app run build``). Optional by design: the API is fully
    usable headless, and tests run without a front-end build."""
    override = os.environ.get("JIM_CONSOLE_DIR")
    root = Path(override) if override else Path(__file__).resolve().parent.parent / "app" / "dist"
    return root if (root / "index.html").exists() else None


def _probe(target: tuple[str, int]) -> str | None:
    """Which local address the routing table would use to reach ``target``.
    A UDP "connect" sends no packet — it only binds the local end — so this
    is a routing lookup, not network traffic."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(target)
        return sock.getsockname()[0]
    except OSError:
        return None
    finally:
        sock.close()


def lan_address() -> str:
    """This machine's address on the local network — the one a phone can
    actually reach.

    Loopback is the failure case, not a fallback: ``127.0.0.1`` typed into a
    phone means *the phone*, so a loopback answer is worse than none. We probe
    a couple of routes (a reserved address first, then a public resolver, for
    hosts that only have a default route) and take the first real address;
    ``JIM_LAN_HOST`` overrides everything for unusual networks.
    """
    forced = os.environ.get("JIM_LAN_HOST")
    if forced:
        return forced
    candidates = [_probe(("192.0.2.1", 1)),      # TEST-NET-1 (reserved)
                  _probe(("8.8.8.8", 53))]       # default route, if any
    try:
        candidates.append(socket.gethostbyname(socket.gethostname()))
    except OSError:
        pass
    for addr in candidates:
        if addr and not addr.startswith("127."):
            return addr
    return "127.0.0.1"


def pairing(port: int = 8000) -> dict:
    """Everything the phone needs: the console URL on this network, whether
    the console has actually been built, and the same-network caveat."""
    host = lan_address()
    base = f"http://{host}:{port}"
    built = console_dir() is not None
    if not built:
        how = ["Build the console first: npm --prefix app run build",
               "Then restart the API and re-read GET /pair."]
    elif host.startswith("127."):
        # Honest about the one case we can't solve for the user.
        how = ["No local-network address found for this machine — a phone "
               "cannot reach 127.0.0.1.",
               "Check that Wi-Fi is connected, then set JIM_LAN_HOST to this "
               "machine's address and restart the API.",
               "Also start the API on all interfaces: "
               "uvicorn jim.api:app --host 0.0.0.0"]
    else:
        how = ["Put the phone on the same Wi-Fi as this machine.",
               "Start the API on all interfaces if you haven't: "
               "uvicorn jim.api:app --host 0.0.0.0",
               f"Open {base}/app/ in the phone's browser (or scan the QR).",
               "Add to Home Screen — it installs and runs full-screen."]
    return {
        "console_url": f"{base}/app/",
        "api_url": base,
        "console_built": built,
        "reachable": not host.startswith("127."),
        "qr_svg": "/pair/qr.svg",
        "how": how,
        "note": "Local network only — this address is not reachable from the "
                "internet, which is the point: your health data stays on your "
                "own network.",
    }
