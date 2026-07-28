"""``python -m jim`` — run the Guardian your way, in one command.

Bare ``python -m jim`` prints the launcher menu: every way to run the
product, so the user chooses the device — phone, this PC, a packaged
installer, or a headless API — and each choice is one command:

* ``python -m jim phone``    — build the console if needed, print the phone
  URL with a QR drawn into the terminal, serve on the local network.
* ``python -m jim desktop``  — the Electron desktop app on this PC (builds
  the console first when needed); without npm it points at the packaged
  installers instead.
* ``python -m jim serve``    — the headless API alone (localhost by
  default), for scripts, development, or fronting with your own client.

Flags on ``phone``: ``--port``, ``--rebuild``, ``--no-build``,
``--print-only`` (pairing block without the server — used by tests).
``serve`` takes ``--host`` and ``--port``.

Security posture unchanged everywhere: the phone address is local-network
only, and every personal endpoint still requires the user's bearer token.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from . import mobile

REPO = Path(__file__).resolve().parent.parent
RELEASES = "https://github.com/davidsbianchi1984/jim-mini/releases/latest"

MENU = f"""
JIM-mini (Guardian) — choose how to run it:

  On your phone       python -m jim phone
                      builds the console, prints a scannable QR, and serves
                      on your Wi-Fi — Add to Home Screen and it's an app.

  On this PC          python -m jim desktop
                      the desktop app in an Electron window (needs npm).

  Packaged installer  {RELEASES}
                      .dmg / .exe / .AppImage built by the release workflow
                      — no toolchain needed, just download and install.

  Headless API        python -m jim serve
                      the backend alone on localhost, for scripts and
                      development (add --host 0.0.0.0 to expose it).

Every option runs the same backend with the same data and the same token
checks — pick per device, switch whenever.
"""


def ensure_console(rebuild: bool = False, allow_build: bool = True) -> bool:
    """Make sure app/dist exists, building it when possible. Returns whether
    a console is available. Headless is not an error — the API works without
    it — but the pairing block will say what's missing."""
    if mobile.console_dir() is not None and not rebuild:
        return True
    if not allow_build:
        return mobile.console_dir() is not None
    npm = shutil.which("npm")
    app = REPO / "app"
    if npm is None or not (app / "package.json").exists():
        return mobile.console_dir() is not None
    if not (app / "node_modules").exists():
        print("• installing console dependencies (first run only)…")
        subprocess.run([npm, "--prefix", str(app), "install"], check=True)
    print("• building the console…")
    subprocess.run([npm, "--prefix", str(app), "run", "build"], check=True)
    return mobile.console_dir() is not None


def print_pairing(port: int) -> dict:
    """The pairing block: URL, instructions, and a terminal-drawn QR."""
    info = mobile.pairing(port=port)
    print()
    print("─" * 62)
    print("  JIM Guardian — open on your phone (same Wi-Fi):")
    print(f"  {info['console_url']}")
    print("─" * 62)
    if info["console_built"] and info["reachable"]:
        import segno
        qr = segno.make(info["console_url"], error="q")
        try:
            qr.terminal(compact=True)
        except TypeError:      # older segno without compact rendering
            qr.terminal()
        print("  Scan the QR, then Add to Home Screen.")
    else:
        for step in info["how"]:
            print(f"  - {step}")
    print(f"  ({info['note']})")
    print()
    return info


def run_phone(args: argparse.Namespace) -> int:
    ensure_console(rebuild=args.rebuild, allow_build=not args.no_build)
    print_pairing(args.port)
    if args.print_only:
        return 0
    import uvicorn
    # Import string (not an app object) so the console mount happens after
    # the build above — the app factory checks app/dist at creation time.
    uvicorn.run("jim.api:app", host="0.0.0.0", port=args.port)
    return 0


def run_desktop(args: argparse.Namespace) -> int:
    """The desktop app on this PC. With npm: build the console if needed and
    open the Electron window. Without: point at the packaged installers —
    that's the no-toolchain way to run on a PC."""
    npm = shutil.which("npm")
    if npm is None:
        print("npm isn't installed, so the from-source desktop app can't "
              "start here.")
        print(f"Grab the packaged installer instead: {RELEASES}")
        return 1
    if not ensure_console():
        print("The console failed to build — see the npm output above.")
        return 1
    app = REPO / "app"
    if not (app / "node_modules").exists():
        subprocess.run([npm, "--prefix", str(app), "install"], check=True)
    print("• opening the desktop app (it starts its own backend probe)…")
    return subprocess.run(
        [npm, "--prefix", str(app), "run", "electron:start"]).returncode


def run_serve(args: argparse.Namespace) -> int:
    import os

    import uvicorn

    # The packaged console (the installer's .exe/.dmg window) calls this API
    # from its own origin, so a serve meant to stand behind it needs CORS —
    # off, the console's every request dies as "Failed to fetch". Default it
    # open for a loopback bind: the in-app hint has always said
    # ``JIM_CORS_ORIGINS=* uvicorn jim.api:app``, so this is the documented
    # posture made the default, and every personal endpoint still requires
    # the user's bearer token. ``--no-cors`` restores the closed posture.
    if not args.no_cors and not os.environ.get("JIM_CORS_ORIGINS") \
            and args.host in {"127.0.0.1", "localhost", "::1"}:
        os.environ["JIM_CORS_ORIGINS"] = "*"
        print("• CORS open for the local console (JIM_CORS_ORIGINS=*); "
              "pass --no-cors or set JIM_CORS_ORIGINS to restrict.")
    uvicorn.run("jim.api:app", host=args.host, port=args.port)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m jim",
        description="Run the Guardian your way — phone, desktop, installer, "
                    "or headless API.")
    sub = parser.add_subparsers(dest="command")

    phone = sub.add_parser(
        "phone", help="build the console if needed, print the QR, serve on "
                      "the local network")
    phone.add_argument("--port", type=int, default=8000)
    phone.add_argument("--rebuild", action="store_true",
                       help="rebuild the console even if a build exists")
    phone.add_argument("--no-build", action="store_true",
                       help="never run npm; serve whatever exists")
    phone.add_argument("--print-only", action="store_true",
                       help="print the pairing block and exit (no server)")

    sub.add_parser("desktop",
                   help="open the desktop app on this PC (or point at the "
                        "packaged installers)")

    serve = sub.add_parser("serve", help="run the headless API alone")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--no-cors", action="store_true",
                       help="keep CORS closed even on loopback (the packaged "
                            "console will not be able to connect)")

    args = parser.parse_args(argv)
    if args.command == "phone":
        return run_phone(args)
    if args.command == "desktop":
        return run_desktop(args)
    if args.command == "serve":
        return run_serve(args)
    # No subcommand: the launcher menu — the choice is the point.
    print(MENU)
    return 0


if __name__ == "__main__":
    sys.exit(main())
