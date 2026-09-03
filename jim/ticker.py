"""The ticker — JIM's clock advances without a read.

Every deadline in this product used to move only when something looked:
the crash watch re-asked "are you okay?" and tripped when the console
polled or a status door was read (:func:`jim.crashwatch.sweep`), the vigil
checked the silence when the screen opened (:func:`jim.vigil.sweep`), and a
placed reach-out leg the phone line never reported on was settled by that
same sweep (:func:`jim.reachout.settle_stale`). A collapse at 3 a.m. with
every screen closed waited for morning.

    asked     does the crash watch trip on time
    mattered  does anything have to be watching for it to

This module is one daemon thread that, every ``JIM_TICK_SECONDS``, sweeps
exactly the users whose clocks are running — an open crash-watch question,
an armed vigil, a placed leg still live — through the same functions the
reads call. Nothing new decides anything: a tick is a read that nobody had
to make. Off when the variable is ``0`` (the suite's posture, so no test
ever races a thread); on by default on the box. The posture says which, in
words, on the crash watch's own status so the Safety screen can tell the
person whether JIM checks on its own.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from datetime import datetime

from . import db

log = logging.getLogger("jim.ticker")

DEFAULT_SECONDS = 30
#: A floor under the interval: a tick is a handful of small queries and, at
#: most, one sweep per running clock, but there is no reason to spin.
MIN_SECONDS = 5

_STATE: dict = {"running": False, "every_seconds": 0, "ticks": 0,
                "last_tick_at": None, "last_swept": 0, "last_error": None}
_STOP = threading.Event()
_THREAD: threading.Thread | None = None


def seconds() -> int:
    """The interval, read honestly: blank or unreadable is the default,
    zero or less is off, anything under the floor is the floor."""
    raw = (os.environ.get("JIM_TICK_SECONDS") or "").strip()
    if not raw:
        return DEFAULT_SECONDS
    try:
        got = int(float(raw))
    except ValueError:
        return DEFAULT_SECONDS
    if got <= 0:
        return 0
    return max(got, MIN_SECONDS)


# --------------------------------------------------------------------------- #
# whose clock is running
# --------------------------------------------------------------------------- #

def due_users() -> dict[str, set[str]]:
    """The users a tick sweeps, and why — only clocks that are running.

    ``crash``: an armed watch with an open question not yet tripped (the
    re-ask and the trip are on a deadline). ``vigil``: an armed vigil not
    yet tripped (the silence is measured against now). ``calls``: a placed
    reach-out leg still live (the line may never report on it). A user with
    none of these has nothing a tick could change, and is not touched.
    """
    conn = db.connect()
    crash = {r["user_id"] for r in conn.execute(
        "SELECT user_id FROM crash_watches WHERE enabled=1"
        " AND concern_opened_at IS NOT NULL AND tripped_at IS NULL")}
    vigil = {r["user_id"] for r in conn.execute(
        "SELECT user_id FROM vigils WHERE enabled=1 AND tripped_at IS NULL")}
    calls = {r["user_id"] for r in conn.execute(
        "SELECT DISTINCT user_id FROM reachout_calls WHERE placed=1"
        " AND status IN ('ringing','consented','talking')")}
    return {"crash": crash, "vigil": vigil, "calls": calls}


def tick(now: datetime | None = None) -> dict:
    """One pass: the same sweeps a read would make, for every running clock.
    One user's failure is logged and does not stop the others; the pass
    records what it did and the last thing that went wrong."""
    from . import crashwatch, vigil
    due = due_users()
    swept = 0
    error = None
    # A crash-watch sweep settles stale placed legs first, so a user with a
    # live leg and no open question is swept through the same door.
    for uid in sorted(due["crash"] | due["calls"]):
        try:
            crashwatch.sweep(uid, now=now)
            swept += 1
        except Exception as exc:  # noqa: BLE001 — one clock must not stop the rest
            error = f"crash watch {uid}: {type(exc).__name__}: {exc}"
            log.exception("ticker: crash-watch sweep failed for %s", uid)
    for uid in sorted(due["vigil"]):
        try:
            vigil.sweep(uid)
            swept += 1
        except Exception as exc:  # noqa: BLE001
            error = f"vigil {uid}: {type(exc).__name__}: {exc}"
            log.exception("ticker: vigil sweep failed for %s", uid)
    _STATE.update(ticks=_STATE["ticks"] + 1, last_tick_at=db.utcnow(),
                  last_swept=swept, last_error=error)
    return {"swept": swept, "due": {k: len(v) for k, v in due.items()},
            "error": error}


# --------------------------------------------------------------------------- #
# the thread
# --------------------------------------------------------------------------- #

def start(app=None) -> threading.Thread | None:
    """Start the ticker when the interval is above zero. Idempotent: a
    second start while one runs returns the running thread."""
    global _THREAD
    every = seconds()
    _STATE.update(every_seconds=every)
    if every <= 0:
        _STATE.update(running=False)
        return None
    if _THREAD is not None and _THREAD.is_alive():
        return _THREAD
    _STOP.clear()

    def run() -> None:
        while not _STOP.wait(every):
            try:
                tick()
            except Exception as exc:  # noqa: BLE001 — the thread outlives a bad pass
                _STATE.update(last_error=f"tick: {type(exc).__name__}: {exc}")
                log.exception("ticker: pass failed")
        _STATE.update(running=False)

    _THREAD = threading.Thread(target=run, name="jim-ticker", daemon=True)
    _THREAD.start()
    _STATE.update(running=True)
    if app is not None:
        app.state.ticker = _THREAD
    log.info("ticker started: every %s second(s)", every)
    return _THREAD


def stop() -> None:
    """Ask the thread to end and wait briefly; safe with none running."""
    global _THREAD
    _STOP.set()
    if _THREAD is not None:
        _THREAD.join(timeout=2.0)
    _THREAD = None
    _STATE.update(running=False)


def reset() -> None:
    """Tests: forget the counters between cases."""
    stop()
    _STATE.update(every_seconds=0, ticks=0, last_tick_at=None,
                  last_swept=0, last_error=None)


def posture() -> dict:
    """Whether JIM checks on its own, said plainly for the status a screen
    reads. ``running`` is the thread's fact, not the setting's."""
    every = _STATE["every_seconds"] if _STATE["running"] else seconds()
    running = bool(_STATE["running"] and _THREAD is not None
                   and _THREAD.is_alive())
    if running:
        note = (f"JIM checks on its own every {every} seconds, whether or "
                "not a screen is open")
    elif every <= 0:
        note = ("the ticker is off (JIM_TICK_SECONDS=0): the crash watch, the "
                "vigil and a placed call's silence advance only while a screen "
                "or a status read looks")
    else:
        note = ("the ticker is not running in this process: the clock "
                "advances only while a screen or a status read looks")
    return {"running": running, "every_seconds": every,
            "ticks": _STATE["ticks"], "last_tick_at": _STATE["last_tick_at"],
            "last_swept": _STATE["last_swept"], "last_error": _STATE["last_error"],
            "note": note}
