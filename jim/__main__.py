"""``python -m jim`` — run the Guardian, phone-ready, in one command.

``python -m jim phone`` does everything the README's manual steps do:

1. **Builds the console if it's missing** (``npm --prefix app install`` when
   node_modules is absent, then ``npm --prefix app run build``). Skipped when
   the build already exists — rebuild explicitly with ``--rebuild``.
2. **Prints the pairing block** — the console's URL on your local network,
   plus the same URL as a QR code drawn straight into the terminal, so the
   phone scans it off this very screen.
3. **Starts the API on all interfaces** (``0.0.0.0``), which is what makes
   it reachable from the phone at all.

Flags: ``--port`` (default 8000), ``--rebuild`` (force a console rebuild),
``--no-build`` (never touch npm), ``--print-only`` (steps 1–2 without
starting the server — used by tests and scripts).

Security posture unchanged: the address is local-network only, and every
personal endpoint still requires the user's bearer token.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from . import mobile

REPO = Path(__file__).resolve().parent.parent


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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m jim",
        description="Run the Guardian, phone-ready, in one command.")
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
    args = parser.parse_args(argv)

    if args.command != "phone":
        parser.print_help()
        return 2

    ensure_console(rebuild=args.rebuild, allow_build=not args.no_build)
    print_pairing(args.port)
    if args.print_only:
        return 0

    import uvicorn
    # Import string (not an app object) so the console mount happens after
    # the build above — the app factory checks app/dist at creation time.
    uvicorn.run("jim.api:app", host="0.0.0.0", port=args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
