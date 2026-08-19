"""The lookout: a page the vault keeps fresh on the person's behalf.

PDI's standing tasks (0.88) let the vault keep its own appointments —
plan a fetch, give it an interval, and the resident re-runs it inside
the facility with no cron, no worker, no caller. This module is JIM's
side of that bargain: "keep an eye on this page" becomes one standing
plan whose single `fetch.url` step re-seals the current capture under
the same key every cycle, so the vault always holds today's page and
never a growing archive of yesterday's.

    asked     can JIM watch a page for somebody
    mattered  who does the watching, and where the page lives

JIM does not do the watching. The resident fetches from inside the
vault's own host, the capture is sealed there (AES-256-GCM, one key per
lookout, overwritten each cycle), and JIM reads it back through the
same authenticated channel every seal uses. What leaves JIM is the URL
once, at planting.

## The rules, inherited from the errands and memory rounds

**Consent before the web.** Planting requires the same standing permit
the study errands need (`errands.PERMIT`): the resident leaves its host
on this person's behalf, and that is theirs to allow.

**Writes are plan-gated; reads and deletes keep the real vault.**
Planting seals things and takes the write vault; the list, the page
read-back and the drop take `app.state.pdi`, because a member who moved
to an open plan still has lookouts to see, read and stop.

**The ledger lets go only after the vault did.** A drop cancels the
standing task first, then unseals the capture, then deletes the local
row — a row whose appointment still stands belongs on the list, not
orphaned. Erasure walks the same path for every lookout the person has.

**Honesty at every edge.** No vault, an older tandem without standing
tasks, an unreached tandem: each answers in words, never a pretend
success — and the list says `readable: false` rather than inventing
statuses it could not fetch.
"""

from __future__ import annotations

import json

from . import db

#: The vault key a lookout's capture lives under: position 01 of the one-step
#: plan, re-sealed by the resident every cycle (see pdi/resident.py's
#: `_tool_fetch`).
_CAPTURE = "resident/{task_id}/01-fetch"

#: The interval window mirrors PDI's own (a quarter-hour to a month), so the
#: refusal is local, translatable, and identical to what the tandem would say.
MIN_HOURS, MAX_HOURS = 0.25, 744

#: How much of a capture one read returns. The seal holds the whole page;
#: a JIM screen needs the reading, not the archive.
PAGE_CAP = 20000

#: How the captures ride the coach's prompt: the latest few pages, each
#: at a digest's length. A prompt full of pages is a coach that stops
#: noticing the person in front of it.
PROMPT_PAGES = 3
PROMPT_CAP = 700


def capture_key(task_id: str) -> str:
    return _CAPTURE.format(task_id=task_id)


def plant(user_id: str, url: str, every_hours: float, pdi=None) -> dict:
    """One standing appointment in the vault, one ledger row here."""
    url = (url or "").strip()
    if not url.startswith(("http://", "https://")):
        return {"planted": False, "why": "a lookout needs an http(s) url"}
    try:
        every_hours = float(every_hours)
    except (TypeError, ValueError):
        return {"planted": False,
                "why": "a lookout repeats on a number of hours"}
    if not MIN_HOURS <= every_hours <= MAX_HOURS:
        return {"planted": False,
                "why": "a lookout repeats between a quarter-hour and a month"}
    if pdi is None:
        return {"planted": False, "why": "no vault configured"}
    try:
        task = pdi.resident_stand(
            goal=f"lookout: {url}",
            steps=[{"tool": "fetch.url", "args": {"url": url}}],
            every_hours=every_hours)
    except Exception as exc:  # noqa: BLE001 — said, never crashed through
        return {"planted": False, "why": f"{type(exc).__name__}: {exc}"[:200]}
    if task is None:
        return {"planted": False,
                "why": "the vault has no standing tasks (older PDI)"}
    conn = db.connect()
    lookout_id = db.new_id("lkt")
    conn.execute(
        "INSERT INTO lookouts (id, user_id, url, every_hours, task_id,"
        " created_at) VALUES (?,?,?,?,?,?)",
        (lookout_id, user_id, url, every_hours, task["id"], db.utcnow()))
    conn.commit()
    return {"planted": True, "id": lookout_id, "url": url,
            "every_hours": every_hours, "task_id": task["id"],
            "next_run_at": task.get("next_run_at")}


def watches(user_id: str, pdi=None) -> dict:
    """This person's lookouts, with what the vault says about each.

    The rows are the local ledger; status and the next appointment come
    from the tandem in one trip. Unreached, the list still stands with
    `readable: false` — "I hold three lookouts I cannot ask about right
    now" and "I hold nothing" are different answers.
    """
    rows = db.connect().execute(
        "SELECT * FROM lookouts WHERE user_id=? ORDER BY created_at, rowid",
        (user_id,)).fetchall()
    statuses, readable = {}, pdi is not None
    if pdi is not None and rows:
        try:
            statuses = {t["id"]: t for t in pdi.resident_tasks()}
        except Exception:  # noqa: BLE001
            readable = False
    out = []
    for r in rows:
        task = statuses.get(r["task_id"], {})
        # When the page last actually changed, from the capture's own
        # fingerprint history (PDI 0.89's fetch) — None when the tandem
        # cannot be read, nothing was fetched yet, or the capture
        # predates fingerprints. Absence stays absence, never a guess.
        sealed = _capture(pdi, r["task_id"]) if pdi is not None else None
        out.append({"id": r["id"], "url": r["url"],
                    "every_hours": r["every_hours"],
                    "status": task.get("status"),
                    "next_run_at": task.get("next_run_at"),
                    "changed_at": (sealed or {}).get("changed_at"),
                    "trouble": _trouble(pdi, r["task_id"]),
                    "created_at": r["created_at"]})
    return {"lookouts": out, "readable": readable}


def _trouble(pdi, task_id: str) -> str | None:
    """Why the watching last failed, from the vault's runs ledger
    (PDI 0.89) — the latest round's note when that round failed, else
    None. None also for an older PDI or an unreached one: absence stays
    absence, and a lookout in trouble should not make the list fail."""
    runs_door = getattr(pdi, "resident_runs", None)
    if runs_door is None:
        return None
    try:
        rounds = runs_door(task_id)
    except Exception:  # noqa: BLE001
        return None
    if not rounds:
        return None
    latest = rounds[0]
    if latest.get("status") != "failed":
        return None
    return latest.get("note")


def _row(user_id: str, lookout_id: str):
    return db.connect().execute(
        "SELECT * FROM lookouts WHERE id=? AND user_id=?",
        (lookout_id, user_id)).fetchone()


def page(user_id: str, lookout_id: str, pdi=None) -> dict | None:
    """The current capture, read back from the seal. None: no such
    lookout. `readable: false`: the lookout stands but the tandem could
    not be reached, or the resident has not fetched yet."""
    row = _row(user_id, lookout_id)
    if row is None:
        return None
    out = {"id": row["id"], "url": row["url"], "readable": False,
           "fetched_at": None, "changed_at": None, "chars": 0, "text": None}
    if pdi is None:
        return out
    sealed = _capture(pdi, row["task_id"])
    if sealed is None:
        return out
    text = sealed.get("text") or ""
    out.update({"readable": True, "fetched_at": sealed.get("fetched_at"),
                "changed_at": sealed.get("changed_at"),
                "chars": len(text), "text": text[:PAGE_CAP]})
    return out


def _capture(pdi, task_id: str) -> dict | None:
    try:
        raw = pdi.get(capture_key(task_id))
    except Exception:  # noqa: BLE001
        return None
    if not raw:
        return None
    try:
        return json.loads(raw)
    except ValueError:
        return None


def prompt_block(user_id: str, pdi=None) -> str | None:
    """The watched pages as their current captures, worded for the
    coach's prompt — context the model may draw on, never an
    instruction, and honest about its age. Contributes nothing rather
    than failing: a turn that lands without the pages beats a turn
    refused for them."""
    if pdi is None:
        return None
    rows = db.connect().execute(
        "SELECT * FROM lookouts WHERE user_id=?"
        " ORDER BY created_at DESC, rowid DESC LIMIT ?",
        (user_id, PROMPT_PAGES)).fetchall()
    parts = []
    for r in rows:
        sealed = _capture(pdi, r["task_id"])
        if sealed is None:
            continue
        text = (sealed.get("text") or "").strip()
        if not text:
            continue
        when = f"captured {sealed.get('fetched_at')}"
        if sealed.get("changed_at"):
            when += f", last changed {sealed['changed_at']}"
        parts.append(f"{r['url']} ({when}):\n" + text[:PROMPT_CAP])
    if not parts:
        return None
    return ("Pages you keep an eye on for this person, as their current "
            "captures — draw on them when they are relevant, say when a "
            "page did not carry an answer, and never present a capture as "
            "older or newer than its date:\n\n" + "\n\n".join(parts))


def drop(user_id: str, lookout_id: str, pdi=None) -> dict | None:
    """Stop the watching the whole way: the appointment, the seal, the
    row — in that order, because a row whose appointment still stands
    belongs on the list, not orphaned. None: no such lookout."""
    row = _row(user_id, lookout_id)
    if row is None:
        return None
    if pdi is None:
        return {"removed": False, "why": "no vault configured"}
    try:
        pdi.resident_cancel(row["task_id"])
        pdi.delete(capture_key(row["task_id"]))
    except Exception as exc:  # noqa: BLE001
        return {"removed": False,
                "why": f"{type(exc).__name__}: {exc}"[:200]}
    conn = db.connect()
    conn.execute("DELETE FROM lookouts WHERE id=? AND user_id=?",
                 (lookout_id, user_id))
    conn.commit()
    return {"removed": True, "id": lookout_id}


def drop_all(user_id: str, pdi=None) -> int | None:
    """Erasure's call: every appointment cancelled, every capture
    unsealed. None when the tandem could not be reached — the erasure
    answer says so, and the rows die with the user's tables either way."""
    rows = db.connect().execute(
        "SELECT task_id FROM lookouts WHERE user_id=?",
        (user_id,)).fetchall()
    if pdi is None:
        return None
    cancelled = 0
    try:
        for r in rows:
            if pdi.resident_cancel(r["task_id"]):
                cancelled += 1
            pdi.delete(capture_key(r["task_id"]))
    except Exception:  # noqa: BLE001
        return None
    return cancelled
