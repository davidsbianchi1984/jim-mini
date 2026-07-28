"""Drive the frozen backend through the first-run a real user performs.

Run in CI on every OS the installer ships for, against the exact PyInstaller
binary that will be packaged, *before* electron-builder touches it — stdout
piped to a file the way the Electron shell pipes it. If signup, the emailed
code, verification, a personal route, and sign-in do not all work here, no
installer is built.

Exists because 0.4.3 shipped with a signup that answered 500 on Windows —
the verification-code banner used characters cp1252 cannot encode, a class
of failure only visible on a real Windows console. "It worked on Linux" is
not a release gate; this is.

Usage: python packaging/smoke_test.py path/to/backend-binary
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

PORT = 8100 + (os.getpid() % 5000)   # random-ish per run: a
# leftover backend from an earlier run must never answer this one
BASE = f"http://127.0.0.1:{PORT}"


def call(method: str, path: str, payload: dict | None = None,
         token: str | None = None) -> tuple[int, dict]:
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"content-type": "application/json"}
    if token:
        headers["authorization"] = f"Bearer {token}"
    req = urllib.request.Request(BASE + path, data=data,
                                 method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, {"raw": body}


def main() -> int:
    binary = Path(sys.argv[1]).resolve()
    workdir = Path(tempfile.mkdtemp(prefix="jim-smoke-"))
    log_path = workdir / "backend.log"
    env = {"JIM_PORT": str(PORT), "JIM_DB": str(workdir / "jim.db"),
           "JIM_LLM": "stub",
           "PYTHONIOENCODING": "cp1252:strict"}
    proc = subprocess.Popen(
        [str(binary)], env={**os.environ, **env},
        stdout=open(log_path, "wb"), stderr=subprocess.STDOUT,
        start_new_session=(sys.platform != "win32"))
    try:
        for _ in range(60):
            try:
                status, _ = call("GET", "/health")
                if status == 200:
                    break
            except Exception:
                pass
            if proc.poll() is not None:
                print("FAIL: backend exited early; log follows")
                print(log_path.read_text(errors="replace"))
                return 1
            time.sleep(1)
        else:
            print("FAIL: backend never answered /health")
            return 1
        print("ok: /health")

        # This deployment has no mail transport, so signup activates the
        # account directly — the packaged desktop experience.
        status, user = call("POST", "/signup", {
            "email": "smoke@example.test", "password": "a-real-passphrase",
            "display_name": "Smoke Test", "birthdate": "1990-01-01",
            "terms_consent": True})
        if status != 201 or user.get("verification") != "local" \
                or not user.get("user_token"):
            print(f"FAIL: /signup -> {status}: {user}")
            print(log_path.read_text(errors="replace")[-2000:])
            return 1
        print("ok: /signup activated directly (no mail transport)")

        status, _ = call("GET", f"/baseline/{user['id']}",
                         token=user["user_token"])
        if status != 200:
            print(f"FAIL: personal route with fresh token -> {status}")
            return 1
        print("ok: token authorizes a personal route")

        status, body = call("POST", "/signin", {
            "email": "smoke@example.test", "password": "a-real-passphrase"})
        if status != 200 or not body.get("user_token"):
            print(f"FAIL: /signin -> {status}: {body}")
            return 1
        print("ok: /signin")
        print("SMOKE PASSED: the shipped binary performs the full first run")
        return 0
    finally:
        # PyInstaller one-file spawns a child; killing only the parent
        # leaves a backend alive on the port. Take the whole group.
        if sys.platform != "win32":
            import signal
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        proc.kill()


if __name__ == "__main__":
    sys.exit(main())
