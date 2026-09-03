"""The coding assistant's box — where a drafted change is tried before a
person is asked to judge it.

## What this is

The Studio's coding assistant (:func:`jim.appedits.draft`) has a model
write a change and files it for company oversight. Until this module it
wrote text and never ran a line: oversight read a diff and guessed. The
widget box (:mod:`jim.widgets`) already answers the harder question — can
a person run code here without reaching anybody else's — and this is the
same box with a different program in it: the repository, with the draft
applied, running its own tests.

    asked     does the draft work
    mattered  did anything try it, inside walls, before a person was asked

## The four walls, and how each is held here

The program is Python rather than a widget's JavaScript, so the walls are
held by the kernel rather than by a runtime's permission model:

**The network is cut.** ``unshare -rn`` puts the run in a network
namespace with no interfaces — the widget box's own wall, the one that
matters most, and ``JIM_OFFLINE=1`` inside as a belt over the braces.

**The filesystem is one directory.** ``unshare -m`` gives the run its own
mount namespace, and before a test runs a tmpfs is mounted over every
place this product keeps a life — ``/home``, ``/root``, ``/srv``,
``/data`` — so the real repository, the real database and the clinical
captures beside it do not exist inside. What exists is the workroom: a
copy of the source tree with the draft applied, and a scratch directory
beside it.

**Processes are counted.** A test run is one interpreter; ``RLIMIT_NPROC``
holds it to a handful, and nothing inside can reach the network to phone
for more.

**Time and memory are finite.** ``setrlimit`` caps CPU seconds and address
space before the interpreter starts; a wall-clock kill catches the run
that sleeps; the output a person reads is capped at a byte count.

## The refusal that matters

If the namespaces are not available — a kernel without user namespaces, a
container that forbids them — this module **refuses to run anything**. It
does not try the draft with three walls instead of four: a draft tried
outside the box would be a read of the whole disk by whatever the model
wrote, and the refusal is a sentence a person can act on.

## What the box decides

Nothing. A green run is a fact about the tests the draft names; a red one
is a fact about the same tests; both go to oversight beside the diff. The
box never approves, never applies, never touches running code — the
publish-merge is still the only road to production, and oversight still
stands in front of it.
"""

from __future__ import annotations

import json
import os
import re
import resource
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from . import db

REPO = Path(__file__).resolve().parent.parent

#: The ceilings, carried into the child before it starts.
LIMITS = {"wall_seconds": 300, "cpu_seconds": 240,
          "address_space": 2 * 1024 ** 3, "processes": 32,
          "output_bytes": 64 * 1024, "kept_bytes": 8 * 1024}
#: How many times the assistant may try again on a red run before the
#: result goes to oversight as it stands.
MAX_ROUNDS = 3
#: What is hidden inside the box: every place this product keeps a life.
HIDDEN = ("/home", "/root", "/srv", "/data")
#: What is not copied into the workroom.
SKIP = {".git", "node_modules", "dist", "__pycache__", ".pytest_cache",
        ".venv", "venv"}

_UNSHARE = "unshare"
_AVAILABLE: tuple[bool, str] | None = None


# --------------------------------------------------------------------------- #
# is there a box at all
# --------------------------------------------------------------------------- #

def available(force: bool = False) -> tuple[bool, str]:
    """Whether all four walls can be raised on this host, probed once.
    The probe raises every namespace the run needs and mounts a tmpfs the
    way the run will; a host that cannot is refused in a sentence."""
    global _AVAILABLE
    if _AVAILABLE is not None and not force:
        return _AVAILABLE
    if shutil.which(_UNSHARE) is None:
        _AVAILABLE = (False, "the assistant's box is not available on this host")
        return _AVAILABLE
    try:
        probe = subprocess.run(
            [_UNSHARE, "-rmn", "--map-root-user", "sh", "-c",
             "mount -t tmpfs none /home && [ -z \"$(ls -A /home)\" ]"],
            capture_output=True, timeout=10)
        ok = probe.returncode == 0
    except (OSError, subprocess.SubprocessError):
        ok = False
    _AVAILABLE = (ok, "" if ok else
                  "the assistant's box is not available on this host")
    return _AVAILABLE


def base() -> Path:
    """Where workrooms live: outside every hidden place, so the box can
    see its own room and nothing else."""
    root = (os.environ.get("JIM_WORKROOMS") or "").strip()
    return Path(root) if root else Path(tempfile.gettempdir()) / "jim-workrooms"


# --------------------------------------------------------------------------- #
# the draft as a diff
# --------------------------------------------------------------------------- #

_FILE_HEADER = re.compile(r"^\+\+\+ (?:b/)?(\S+)", re.M)
_HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def touched_files(patch: str) -> list[str]:
    """The paths a unified diff changes, in order, without duplicates."""
    seen: list[str] = []
    for m in _FILE_HEADER.finditer(patch or ""):
        path = m.group(1)
        if path != "/dev/null" and path not in seen:
            seen.append(path)
    return seen


def apply_patch(root: Path, patch: str) -> list[str]:
    """Apply a unified diff to the tree under ``root``. Hunks are matched
    by their context, at the stated line first and then anywhere nearby, so
    a draft written against a slightly older file still lands. Raises
    ValueError with a sentence when the draft is not a diff or a hunk does
    not fit."""
    if not _FILE_HEADER.search(patch or ""):
        raise ValueError("the draft is not a unified diff, so the box cannot try it")
    lines = (patch or "").splitlines()
    changed: list[str] = []
    i = 0
    while i < len(lines):
        if not lines[i].startswith("+++ "):
            i += 1
            continue
        path = _FILE_HEADER.match(lines[i]).group(1)
        i += 1
        target = (root / path).resolve()
        if root.resolve() not in target.parents:
            raise ValueError("the draft reaches outside the tree, so the box cannot try it")
        original = target.read_text(encoding="utf-8").splitlines() \
            if target.exists() else []
        out = list(original)
        offset = 0
        while i < len(lines) and lines[i].startswith("@@"):
            m = _HUNK.match(lines[i])
            if not m:
                raise ValueError("the draft's hunk header cannot be read, so the box cannot try it")
            start = int(m.group(1)) - 1
            i += 1
            old_side, new_side = [], []
            while i < len(lines) and not lines[i].startswith(("@@", "--- ", "+++ ")):
                ln = lines[i]
                if ln.startswith("-"):
                    old_side.append(ln[1:])
                elif ln.startswith("+"):
                    new_side.append(ln[1:])
                elif ln.startswith("\\"):
                    pass
                else:
                    body = ln[1:] if ln.startswith(" ") else ln
                    old_side.append(body)
                    new_side.append(body)
                i += 1
            at = _locate(out, old_side, start + offset)
            if at is None:
                raise ValueError("the draft does not fit the file it changes, so the box cannot try it")
            out[at:at + len(old_side)] = new_side
            offset += len(new_side) - len(old_side)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(out) + ("\n" if out else ""), encoding="utf-8")
        changed.append(path)
    return changed


def _locate(haystack: list[str], needle: list[str], guess: int) -> int | None:
    if not needle:
        return max(0, min(guess, len(haystack)))
    span = len(needle)
    order = sorted(range(0, max(1, len(haystack) - span + 1)),
                   key=lambda k: abs(k - guess))
    for k in order:
        if haystack[k:k + span] == needle:
            return k
    return None


# --------------------------------------------------------------------------- #
# the room, and what runs in it
# --------------------------------------------------------------------------- #

def build(patch: str, source: Path | None = None) -> tuple[Path, list[str]]:
    """A fresh workroom: the source tree copied without its git, its node
    modules or its builds, the draft applied. Returns the room and the
    files the draft changed."""
    # A draft that is not a diff is refused before a tree is copied for it.
    if not _FILE_HEADER.search(patch or ""):
        raise ValueError("the draft is not a unified diff, so the box cannot try it")
    src = source or REPO
    root = base()
    root.mkdir(parents=True, exist_ok=True)
    room = Path(tempfile.mkdtemp(prefix="room-", dir=str(root)))
    tree = room / "tree"
    shutil.copytree(src, tree, ignore=shutil.ignore_patterns(*SKIP),
                    symlinks=False)
    (room / "tmp").mkdir()
    changed = apply_patch(tree, patch)
    return room, changed


def tests_for(tree: Path, changed: list[str], target: str = "") -> list[str]:
    """The tests a draft is tried against: every test file whose name
    carries the stem of a changed file or of the target. Named rather than
    the whole suite, because a draft is tried in minutes, not in half an
    hour — and the whole suite still runs before anything merges."""
    stems: set[str] = set()
    for path in list(changed) + ([target] if target else []):
        stem = Path(path).stem
        if stem and not stem.startswith("test_") and stem not in ("__init__",):
            stems.add(stem.lower())
    found: list[str] = []
    tests = tree / "jim" / "tests"
    if tests.is_dir():
        for f in sorted(tests.glob("test_*.py")):
            name = f.stem.lower()
            if any(stem in name for stem in stems):
                found.append(str(f.relative_to(tree)))
    # A test file the draft itself changed is tried whatever its name.
    for path in changed:
        if path.startswith("jim/tests/test_") and path not in found:
            found.append(path)
    return found


def _limits() -> None:                              # pragma: no cover - child
    cpu = LIMITS["cpu_seconds"]
    resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu + 5))
    space = LIMITS["address_space"]
    resource.setrlimit(resource.RLIMIT_AS, (space, space))
    resource.setrlimit(resource.RLIMIT_NPROC, (LIMITS["processes"],) * 2)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def _script(tree: Path, room: Path, tests: list[str]) -> str:
    """What runs inside the namespaces: hide every life on this disk, then
    the tests — or, with none named, the compile of the tree."""
    hide = " && ".join(f"( [ -d {h} ] && mount -t tmpfs none {h} || true )"
                       for h in HIDDEN)
    if tests:
        run = (f"{sys.executable} -m pytest -q -x -p no:cacheprovider "
               + " ".join(tests))
    else:
        run = f"{sys.executable} -m compileall -q jim"
    return f"{hide} && cd {tree} && exec {run}"


def run(room: Path, tests: list[str]) -> dict:
    """Try the room: one test run inside all four walls. Never raises —
    the answer is a status a person can read, whatever happened."""
    ok, why = available()
    if not ok:
        return {"status": "refused", "detail": why, "tests": tests,
                "output": "", "ms": 0}
    tree = room / "tree"
    if any(str(room.resolve()).startswith(h + "/") for h in HIDDEN):
        return {"status": "refused", "tests": tests, "ms": 0, "output": "",
                "detail": "the workroom sits inside a hidden place, so the "
                          "box cannot see it — set JIM_WORKROOMS elsewhere"}
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
           "HOME": str(room), "TMPDIR": str(room / "tmp"),
           "PYTHONPATH": str(tree), "PYTHONDONTWRITEBYTECODE": "1",
           "JIM_OFFLINE": "1", "JIM_LLM": "stub", "JIM_TICK_SECONDS": "0",
           "LANG": "C.UTF-8"}
    started = time.monotonic()
    try:
        done = subprocess.run(
            [_UNSHARE, "-rmn", "--map-root-user", "sh", "-c",
             _script(tree, room, tests)],
            capture_output=True, timeout=LIMITS["wall_seconds"], env=env,
            preexec_fn=_limits, cwd=str(tree))
    except subprocess.TimeoutExpired as exc:
        ms = int((time.monotonic() - started) * 1000)
        out = (exc.stdout or b"")[-LIMITS["kept_bytes"]:].decode("utf-8", "replace")
        return {"status": "timeout", "tests": tests, "ms": ms, "output": out,
                "detail": "the tests ran longer than the box allows"}
    ms = int((time.monotonic() - started) * 1000)
    raw = (done.stdout + done.stderr)[-LIMITS["output_bytes"]:]
    out = raw[-LIMITS["kept_bytes"]:].decode("utf-8", "replace")
    passed, failed = _counts(raw.decode("utf-8", "replace"))
    if done.returncode == 0:
        status = "green"
    elif done.returncode < 0 or done.returncode > 5:
        status = "killed"
    else:
        status = "red"
    return {"status": status, "tests": tests, "ms": ms, "output": out,
            "passed": passed, "failed": failed, "detail": ""}


def _counts(text: str) -> tuple[int, int]:
    passed = failed = 0
    m = re.search(r"(\d+) passed", text)
    if m:
        passed = int(m.group(1))
    m = re.search(r"(\d+) failed", text)
    if m:
        failed = int(m.group(1))
    return passed, failed


def discard(room: Path) -> None:
    shutil.rmtree(room, ignore_errors=True)


# --------------------------------------------------------------------------- #
# the assistant tries, and tries again
# --------------------------------------------------------------------------- #

def try_draft(patch: str, target: str = "", *, source: Path | None = None) -> dict:
    """One round: build the room, apply the draft, run its tests, clear the
    room. The answer says what was tried and what came of it."""
    try:
        room, changed = build(patch, source)
    except ValueError as exc:
        return {"status": "unapplied", "detail": str(exc), "changed": [],
                "tests": [], "output": "", "ms": 0}
    try:
        tests = tests_for(room / "tree", changed, target)
        got = run(room, tests)
    finally:
        discard(room)
    return {**got, "changed": changed}


def iterate(patch: str, target: str, again, *, rounds: int = MAX_ROUNDS,
            source: Path | None = None) -> dict:
    """Try the draft; on a red run, hand the failure back to the assistant
    (``again(patch, output) -> new patch``) and try the new draft, up to
    ``rounds`` times. Every round is kept, so oversight sees the path and
    not just the end of it."""
    history: list[dict] = []
    current = patch
    for n in range(1, max(1, rounds) + 1):
        got = try_draft(current, target, source=source)
        history.append({"round": n, **got, "patch": current})
        if got["status"] != "red" or n == rounds:
            break
        try:
            revised = (again(current, got["output"]) or "").strip()
        except Exception as exc:  # noqa: BLE001 — the assistant failing is a result
            history[-1]["assistant_failed"] = f"{type(exc).__name__}: {exc}"
            break
        if not revised or revised == current:
            break
        current = revised
    last = history[-1]
    return {"status": last["status"], "rounds": history, "patch": current,
            "ran_at": db.utcnow()}


def summary(box: dict | None) -> dict | None:
    """The part of a box record a screen shows: the outcome, the rounds,
    the tests, and the tail of what they said — never the patches again."""
    if not box:
        return None
    rounds = box.get("rounds") or []
    last = rounds[-1] if rounds else {}
    return {"status": box.get("status"), "rounds": len(rounds),
            "tests": last.get("tests") or [], "changed": last.get("changed") or [],
            "passed": last.get("passed"), "failed": last.get("failed"),
            "detail": last.get("detail") or "", "output": last.get("output") or "",
            "ms": last.get("ms"), "ran_at": box.get("ran_at")}


def loads(raw: str | None) -> dict | None:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except ValueError:
        return None
