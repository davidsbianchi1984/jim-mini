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

**The network is cut.** ``unshare -n`` puts the run in a network
namespace with no interfaces — the widget box's own wall, the one that
matters most, and ``JIM_OFFLINE=1`` inside as a belt over the braces.

**The filesystem is one directory.** ``unshare -m`` gives the run its own
mount namespace, and before a test runs a small, size-capped tmpfs is
mounted over every place this product keeps a life — ``/home``,
``/root``, ``/srv``, ``/data``, and wherever the database, the checkout
and the console actually sit on this host — so the real repository, the
real database and the clinical captures beside it do not exist inside.
What exists is the workroom: a copy of the source tree with the draft
applied (the database, its journals and every ``.env`` are never copied),
and a scratch directory beside it. A mount that cannot be raised aborts
the run before a test starts.

**Processes are counted.** ``unshare -p --fork --kill-child`` makes the
run pid 1 of its own pid namespace, so nothing it starts outlives it —
a detached grandchild dies with the run. ``RLIMIT_NPROC`` holds the
count; because the kernel does not count root's processes, a server
running as root drops the run to ``nobody`` first, and the probe forks
past the ceiling to prove the count holds before the box is offered.

**Time and memory are finite.** ``setrlimit`` caps CPU seconds, address
space, and file size before the interpreter starts; a wall-clock kill
catches the run that sleeps; the output a person reads is written to a
file the kernel bounds, never buffered by the server, and the tail is
what is kept.

## The refusal that matters

If a wall cannot be raised — a kernel without user namespaces, a
container that forbids them, a process count that does not hold, a
workroom inside a hidden place — this module **refuses to run anything**.
It does not try the draft with three walls instead of four: a draft tried
outside the box would be a read of the whole disk by whatever the model
wrote, and the refusal is a sentence a person can act on. The probe is
the run's own script with the interpreter in place of the tests, so what
it proves is what the run will do.

## What the box decides

Nothing. A green run is a fact about the tests the draft names; a red one
is a fact about the same tests; both go to oversight beside the diff. The
box never approves, never applies, never touches running code — the
publish-merge is still the only road to production, and oversight still
stands in front of it.
"""

from __future__ import annotations

import json
import logging
import os
import pwd
import re
import resource
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from . import db, i18n

log = logging.getLogger("jim.workroom")

REPO = Path(__file__).resolve().parent.parent

#: The ceilings, carried into the child before it starts.
LIMITS = {"wall_seconds": 300, "cpu_seconds": 240,
          "address_space": 2 * 1024 ** 3, "processes": 32,
          "file_bytes": 16 * 1024 ** 2,
          "output_bytes": 64 * 1024, "kept_bytes": 8 * 1024}
#: How many tries of the draft in all: the first, then a revision on each
#: red run — so at most ``MAX_ROUNDS - 1`` revisions.
MAX_ROUNDS = 3
#: What is hidden inside the box: every place this product keeps a life.
#: The database's directory, the checkout and the console are added at run
#: time wherever this host keeps them.
HIDDEN = ("/home", "/root", "/srv", "/data")
#: What is not copied into the workroom: the git history, the builds, and
#: every runtime file and secret — the database, its journals, ``.env``.
SKIP = {".git", "node_modules", "dist", "__pycache__", ".pytest_cache",
        ".venv", "venv", "*.db", "*.db-wal", "*.db-shm", "*.sqlite3",
        ".env", ".env.*"}
#: The size of the empty mount over each hidden place.
MOUNT = "size=64m,nr_inodes=4k"
#: Who the run is when the server is root: the kernel does not count
#: root's processes, so root is not a uid the box can run as.
NOBODY = "nobody"

_UNSHARE = "unshare"
_UNSHARE_ARGS = ["-rmnp", "--fork", "--kill-child=SIGKILL", "--map-root-user"]
_OPEN = "__JIM_BOX_OPEN__"
_NOT_HERE = "the assistant's box is not available on this host"
_TIMEOUT = "the tests ran longer than the box allows"
_NOTHING = "the named tests collected nothing, so nothing was tried"
_AVAILABLE: tuple[bool, str] | None = None


# --------------------------------------------------------------------------- #
# what is hidden, and where the room is
# --------------------------------------------------------------------------- #

def lives() -> list[Path]:
    """Every place this deployment keeps a life: the database's directory,
    the checkout, the console build if it is somewhere else."""
    out = [Path(db.db_path()).resolve().parent, REPO.resolve()]
    console = (os.environ.get("JIM_CONSOLE_DIR") or "").strip()
    if console:
        out.append(Path(console).resolve())
    return out


def hidden() -> list[str]:
    """The fixed places and the lives, as the mount script sees them."""
    seen: list[str] = []
    for p in [Path(h) for h in HIDDEN] + lives():
        s = str(p)
        if s != "/" and s not in seen:
            seen.append(s)
    return seen


def _under(path: Path, places: list[str]) -> bool:
    s = str(path.resolve())
    return any(s == h or s.startswith(h + "/") for h in places)


def base() -> Path:
    """Where workrooms live: outside every hidden place, so the box can
    see its own room and nothing else."""
    root = (os.environ.get("JIM_WORKROOMS") or "").strip()
    return Path(root) if root else Path(tempfile.gettempdir()) / "jim-workrooms"


# --------------------------------------------------------------------------- #
# is there a box at all
# --------------------------------------------------------------------------- #

_PROBE = r"""
import os, sys, time
import pytest
for place in sys.argv[1:]:
    if os.path.isdir(place) and os.listdir(place):
        sys.exit("a hidden place is not empty: " + place)
kids = []
held = False
try:
    for _ in range(200):
        pid = os.fork()
        if pid == 0:
            time.sleep(20)
            os._exit(0)
        kids.append(pid)
except OSError:
    held = True
for pid in kids:
    os.kill(pid, 9)
    os.waitpid(pid, 0)
if not held:
    sys.exit("the process count does not hold")
print("probe ok")
"""


def available(force: bool = False) -> tuple[bool, str]:
    """Whether all four walls can be raised on this host, probed once.
    The probe is the run's own script with the interpreter in place of
    the tests: it raises every namespace, mounts every hidden place and
    checks each is empty, imports pytest from inside, and forks past the
    process ceiling to prove the count holds. A host that cannot is
    refused in a sentence; the reason is logged for the operator."""
    global _AVAILABLE
    if _AVAILABLE is not None and not force:
        return _AVAILABLE
    _AVAILABLE = (False, _NOT_HERE)
    if shutil.which(_UNSHARE) is None:
        log.warning("the assistant's box: no `unshare` on this host")
        return _AVAILABLE
    if _under(base(), hidden()):
        log.warning("the assistant's box: JIM_WORKROOMS=%s sits inside a "
                    "hidden place; set it elsewhere", base())
        return _AVAILABLE
    if os.geteuid() == 0 and _nobody() is None:
        log.warning("the assistant's box: the server is root and there is "
                    "no `%s` to run the box as", NOBODY)
        return _AVAILABLE
    try:
        base().mkdir(parents=True, exist_ok=True)
        room = Path(tempfile.mkdtemp(prefix="probe-", dir=str(base())))
    except OSError as exc:
        log.warning("the assistant's box: cannot make a room under %s (%s)",
                    base(), type(exc).__name__)
        return _AVAILABLE
    try:
        (room / "tree").mkdir()
        (room / "tmp").mkdir()
        (room / "probe.py").write_text(_PROBE, encoding="utf-8")
        _own(room)
        places = hidden()
        program = (f"{sys.executable} {room / 'probe.py'} "
                   + " ".join(places))
        got = _invoke(room, room / "tree", _script(room / "tree", places, program))
    finally:
        discard(room)
    ok = got["status"] == "green" and "probe ok" in got["output"]
    if not ok:
        log.warning("the assistant's box: the probe failed (%s): %s",
                    got["status"], got["output"][-400:].strip())
    _AVAILABLE = (ok, "" if ok else _NOT_HERE)
    return _AVAILABLE


def _nobody():
    try:
        return pwd.getpwnam(NOBODY)
    except KeyError:
        return None


# --------------------------------------------------------------------------- #
# the draft as a diff
# --------------------------------------------------------------------------- #

_OLD_HEADER = re.compile(r"^--- (?:a/)?(\S+)")
_NEW_HEADER = re.compile(r"^\+\+\+ (?:b/)?(\S+)")
_FILE_HEADER = re.compile(r"^--- (?:a/)?\S+\n\+\+\+ (?:b/)?(\S+)", re.M)
_HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")

_NOT_A_DIFF = "the draft is not a unified diff, so the box cannot try it"
_OUTSIDE = "the draft reaches outside the tree, so the box cannot try it"
_BAD_HUNK = "the draft's hunk header cannot be read, so the box cannot try it"
_NO_FIT = "the draft does not fit the file it changes, so the box cannot try it"


def touched_files(patch: str) -> list[str]:
    """The paths a unified diff changes, in order, without duplicates."""
    seen: list[str] = []
    for m in _FILE_HEADER.finditer(patch or ""):
        path = m.group(1)
        if path != "/dev/null" and path not in seen:
            seen.append(path)
    return seen


def _inside(root: Path, path: str) -> Path:
    target = (root / path).resolve()
    if root.resolve() not in target.parents:
        raise ValueError(_OUTSIDE)
    return target


def _read(target: Path) -> list[str]:
    if target.is_dir():
        raise ValueError(_NO_FIT)
    if not target.exists():
        return []
    try:
        return target.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        raise ValueError(_NO_FIT) from None


def apply_patch(root: Path, patch: str) -> list[str]:
    """Apply a unified diff to the tree under ``root``. A file is named by
    a ``---``/``+++`` pair; each hunk is bounded by the counts in its
    header, so the next file's headers, a closing fence or trailing prose
    are never read as context; hunks are matched by their content, at the
    stated line first and then nearby, so a draft written against a
    slightly older file still lands. ``+++ /dev/null`` deletes the file
    the ``---`` line named. Raises ValueError with a constant sentence
    when the draft is not a diff or a hunk does not fit."""
    if not _FILE_HEADER.search(patch or ""):
        raise ValueError(_NOT_A_DIFF)
    lines = (patch or "").splitlines()
    changed: list[str] = []
    i = 0
    while i < len(lines):
        old = _OLD_HEADER.match(lines[i])
        new = _NEW_HEADER.match(lines[i + 1]) if old and i + 1 < len(lines) else None
        if not (old and new):
            i += 1
            continue
        i += 2
        path = new.group(1)
        if path == "/dev/null":
            path = old.group(1)
            if path == "/dev/null":
                raise ValueError(_NO_FIT)
            target = _inside(root, path)
            if not target.is_file():
                raise ValueError(_NO_FIT)
            # The hunk that removes every line is the whole file; read past
            # it rather than apply it.
            while i < len(lines) and not _OLD_HEADER.match(lines[i]):
                i += 1
            target.unlink()
            changed.append(path)
            continue
        target = _inside(root, path)
        out = _read(target)
        offset = 0
        hunks = 0
        while i < len(lines) and lines[i].startswith("@@"):
            m = _HUNK.match(lines[i])
            if not m:
                raise ValueError(_BAD_HUNK)
            old_left = int(m.group(2)) if m.group(2) is not None else 1
            new_left = int(m.group(4)) if m.group(4) is not None else 1
            # An empty old range names the line before the insertion.
            start = int(m.group(1)) - (0 if old_left == 0 else 1)
            i += 1
            hunks += 1
            old_side, new_side = [], []
            while i < len(lines) and (old_left > 0 or new_left > 0):
                ln = lines[i]
                if ln.startswith("\\"):
                    i += 1
                    continue
                if ln.startswith("-"):
                    old_side.append(ln[1:]); old_left -= 1
                elif ln.startswith("+"):
                    new_side.append(ln[1:]); new_left -= 1
                else:
                    body = ln[1:] if ln.startswith(" ") else ln
                    old_side.append(body); new_side.append(body)
                    old_left -= 1; new_left -= 1
                i += 1
            if old_left != 0 or new_left != 0:
                raise ValueError(_NO_FIT)
            at = _locate(out, old_side, start + offset)
            if at is None:
                raise ValueError(_NO_FIT)
            out[at:at + len(old_side)] = new_side
            offset += len(new_side) - len(old_side)
        if not hunks:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("\n".join(out) + ("\n" if out else ""), encoding="utf-8")
        changed.append(path)
    if not changed:
        raise ValueError(_NOT_A_DIFF)
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
    modules, its builds, its database or its secrets, the draft applied.
    Returns the room and the files the draft changed. A draft that does
    not apply leaves no room behind."""
    # A draft that is not a diff is refused before a tree is copied for it.
    if not _FILE_HEADER.search(patch or ""):
        raise ValueError(_NOT_A_DIFF)
    src = source or REPO
    root = base()
    root.mkdir(parents=True, exist_ok=True)
    room = Path(tempfile.mkdtemp(prefix="room-", dir=str(root)))
    try:
        tree = room / "tree"
        skip = set(SKIP) | {Path(db.db_path()).name}
        shutil.copytree(src, tree, ignore=shutil.ignore_patterns(*skip),
                        symlinks=True)
        (room / "tmp").mkdir()
        changed = apply_patch(tree, patch)
        _own(room)
    except BaseException:
        discard(room)
        raise
    return room, changed


def _own(room: Path) -> None:
    """The room belongs to whoever the run will be."""
    if os.geteuid() != 0:
        return
    who = _nobody()
    if who is None:
        return
    for dirpath, dirnames, filenames in os.walk(room):
        os.chown(dirpath, who.pw_uid, who.pw_gid)
        for f in filenames:
            p = os.path.join(dirpath, f)
            if not os.path.islink(p):
                os.chown(p, who.pw_uid, who.pw_gid)


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
        if path.startswith("jim/tests/test_") and path not in found \
                and (tree / path).exists():
            found.append(path)
    return found


def _limits() -> None:                              # pragma: no cover - child
    cpu = LIMITS["cpu_seconds"]
    resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu + 5))
    space = LIMITS["address_space"]
    resource.setrlimit(resource.RLIMIT_AS, (space, space))
    resource.setrlimit(resource.RLIMIT_FSIZE, (LIMITS["file_bytes"],) * 2)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    if os.geteuid() == 0:
        who = pwd.getpwnam(NOBODY)
        os.setgroups([])
        os.setgid(who.pw_gid)
        os.setuid(who.pw_uid)
    resource.setrlimit(resource.RLIMIT_NPROC, (LIMITS["processes"],) * 2)


def _script(tree: Path, places: list[str], program: str) -> str:
    """What runs inside the namespaces: hide every life on this disk — a
    mount that fails aborts the run — say the box is open, then the
    program."""
    hide = " && ".join(
        f"( [ ! -d {h} ] || mount -t tmpfs -o {MOUNT} none {h} )"
        for h in places)
    return f"{hide} && cd {tree} && echo {_OPEN} && exec {program}"


def _program(tests: list[str]) -> str:
    if tests:
        return (f"{sys.executable} -m pytest -q -x -p no:cacheprovider "
                + " ".join(tests))
    return f"{sys.executable} -m compileall -q jim"


def _invoke(room: Path, tree: Path, script: str) -> dict:
    """One process inside all four walls, its output on a file the kernel
    bounds, its tail read back. Never raises."""
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
           "HOME": str(room), "TMPDIR": str(room / "tmp"),
           "PYTHONPATH": str(tree), "PYTHONDONTWRITEBYTECODE": "1",
           "JIM_OFFLINE": "1", "JIM_LLM": "stub", "JIM_TICK_SECONDS": "0",
           "LANG": "C.UTF-8"}
    logfile = room / "run.log"
    started = time.monotonic()
    timed_out = False
    try:
        with open(logfile, "wb") as fh:
            done = subprocess.run(
                [_UNSHARE, *_UNSHARE_ARGS, "sh", "-c", script],
                stdout=fh, stderr=subprocess.STDOUT,
                timeout=LIMITS["wall_seconds"], env=env,
                preexec_fn=_limits, cwd=str(room))
        code = done.returncode
    except subprocess.TimeoutExpired:
        timed_out = True
        code = None
    except OSError as exc:
        return {"status": "refused", "detail": _NOT_HERE, "ms": 0,
                "output": f"{type(exc).__name__}"}
    ms = int((time.monotonic() - started) * 1000)
    # The box says it is open before the program starts, so the word is at
    # the head of the log; what the tests said is at the tail.
    opened = _OPEN in _head(logfile, 4096).decode("utf-8", "replace")
    text = _tail(logfile, LIMITS["output_bytes"]).decode("utf-8", "replace")
    out = text.split(_OPEN, 1)[1] if _OPEN in text else text
    out = out[-LIMITS["kept_bytes"]:]
    if not opened:
        return {"status": "refused", "detail": _NOT_HERE, "ms": ms,
                "output": out}
    if timed_out:
        return {"status": "timeout", "detail": _TIMEOUT, "ms": ms, "output": out}
    passed, failed = _counts(out)
    if code == 0:
        status, detail = "green", ""
    elif code == 5:
        status, detail = "red", _NOTHING
    elif code is not None and 0 < code <= 4:
        status, detail = "red", ""
    else:
        status, detail = "killed", ""
    return {"status": status, "detail": detail, "ms": ms, "output": out,
            "passed": passed, "failed": failed}


def _head(path: Path, n: int) -> bytes:
    try:
        with open(path, "rb") as fh:
            return fh.read(n)
    except OSError:
        return b""


def _tail(path: Path, n: int) -> bytes:
    try:
        with open(path, "rb") as fh:
            fh.seek(0, os.SEEK_END)
            size = fh.tell()
            fh.seek(max(0, size - n))
            return fh.read()
    except OSError:
        return b""


def run(room: Path, tests: list[str]) -> dict:
    """Try the room: one test run inside all four walls. Never raises —
    the answer is a status a person can read, whatever happened."""
    ok, why = available()
    if not ok:
        return {"status": "refused", "detail": why, "tests": tests,
                "output": "", "ms": 0}
    places = hidden()
    if _under(room, places):
        # The room cannot be inside what the box hides: the box would not
        # see it. available() refuses the configured base for this; a room
        # that landed here anyway is refused the same way.
        return {"status": "refused", "detail": _NOT_HERE, "tests": tests,
                "output": "", "ms": 0}
    tree = room / "tree"
    got = _invoke(room, tree, _script(tree, places, _program(tests)))
    if got["status"] == "refused":
        # The box did not open for this run: look again, so the posture
        # says so until it does.
        available(force=True)
    return {**got, "tests": tests}


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
        return {"status": "unapplied", "detail": i18n.raised(exc), "changed": [],
                "tests": [], "output": "", "ms": 0}
    try:
        tests = tests_for(room / "tree", changed, target)
        got = run(room, tests)
    finally:
        discard(room)
    return {**got, "changed": changed}


def iterate(patch: str, target: str, again, *, rounds: int = MAX_ROUNDS,
            source: Path | None = None) -> dict:
    """Try the draft; on a red run with something to say, hand the failure
    back to the assistant (``again(patch, output) -> new patch`` or
    ``(new patch, who)``) and try the new draft, up to ``rounds`` tries in
    all. Every round is kept, so oversight sees the path and not just the
    end of it. The patch handed back is the last one that applied: a
    revision that was not a diff stays on the record and never replaces
    the draft on file."""
    history: list[dict] = []
    current, kept, kept_by, who = patch, patch, "", ""
    for n in range(1, max(1, rounds) + 1):
        got = try_draft(current, target, source=source)
        history.append({"round": n, **got, "patch": current, "model": who})
        if got["status"] not in ("unapplied", "refused"):
            kept, kept_by = current, who
        if got["status"] != "red" or got.get("detail") or n == rounds:
            break
        try:
            answer = again(current, got["output"])
        except Exception as exc:  # noqa: BLE001 — the assistant failing is a result
            history[-1]["assistant_failed"] = f"{type(exc).__name__}: {exc}"
            break
        who = ""
        if isinstance(answer, tuple):
            answer, who = answer
        revised = (answer or "").strip()
        if not revised or revised == current.strip():
            break
        current = revised
    last = history[-1]
    return {"status": last["status"], "rounds": history, "patch": kept,
            "model": kept_by, "ran_at": db.utcnow()}


def summary(box: dict | None, language: str = i18n.DEFAULT) -> dict | None:
    """The part of a box record a screen shows: the outcome, the rounds,
    the tests, and the tail of what they said — never the patches again.
    The sentence, if there is one, in the reader's language."""
    if not box:
        return None
    rounds = box.get("rounds") or []
    last = rounds[-1] if rounds else {}
    return {"status": box.get("status"), "rounds": len(rounds),
            "tests": last.get("tests") or [], "changed": last.get("changed") or [],
            "passed": last.get("passed"), "failed": last.get("failed"),
            "detail": i18n.tr_refusal(last.get("detail") or "", language),
            "output": last.get("output") or "",
            "ms": last.get("ms"), "ran_at": box.get("ran_at")}


def loads(raw: str | None) -> dict | None:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except ValueError:
        return None
