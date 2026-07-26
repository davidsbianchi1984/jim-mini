"""Handing a QRME specialist a *task* rather than a turn.

``guardian._tandem_guidance`` already delegates across the tandem: it sends one
message and gets one reply, which is the right shape for *"say something
supportive about what the sensors just saw"*. It is the wrong shape for work
that takes several steps and has to survive the user putting their phone down
— *"read what we have about this condition, draft the summary they asked for,
and hold it until somebody confirms"*.

QRME runs that as a **workflow** (`research → draft → review → send →
confirm`), carrying each phase's output into the next, staying in the
specialist's persona throughout, and persisting between calls so a phase that
waits on the outside world resumes in a later session. This module is the
JIM-side half: it starts one, tracks it locally, and reports on it.

Three things are deliberately true.

**A task handoff is never on the emergency path.** :mod:`jim.escalation`
decides in one call and must keep doing so. Multi-step work is by definition
slower than the thing it would be blocking, and an escalation ladder that
waits on a `research` phase is worse than no ladder. Nothing here is reachable
from ``monitor`` — a handoff is started explicitly, by somebody who decided it
was worth starting.

**Starting one is explicit, not automatic.** The temptation is to have a
detection kick off a workflow by itself, which reads well and is the wrong
default: it would let a noisy reading commit a specialist to unattended
multi-phase work over the user's vaulted material. A detection can *warrant* a
handoff; a person or an operator starts it.

**A specialist that has not been opted in is not an error.** QRME's delegated
surface is off until a profile's owner turns it on, so :func:`available` asks
first and an unavailable specialist produces a plain answer rather than a
failure in the middle of something.
"""

from __future__ import annotations

from . import db

# What JIM asks a specialist for. Narrower than QRME's full phase set on
# purpose: JIM has no use for a `send` it cannot deliver, and the owner's
# policy narrows this further still — whichever set is smaller wins.
DEFAULT_PLAN = ["research", "draft", "review", "confirm"]


def _link(user_id: str):
    return db.connect().execute(
        "SELECT * FROM tandem_links WHERE user_id=?", (user_id,)).fetchone()


def available(qrme, spec) -> dict:
    """Whether this specialist accepts delegated work, and which phases.

    Asked before attempting anything. An unreachable QRME reads as "no", which
    is the safe direction — JIM does the work standalone rather than waiting.
    """
    if qrme is None or not spec or not spec.get("qrme_profile_id"):
        return {"available": False, "phases": [], "reason": "no tandem specialist"}
    offer = qrme.delegation_offer(spec["qrme_profile_id"])
    if not offer.get("delegation"):
        return {"available": False, "phases": [],
                "reason": "this specialist does not accept delegated work"}
    return {"available": True, "phases": offer.get("phases", []),
            "reason": None}


def start(user_id: str, goal: str, spec, qrme,
          plan: list[str] | None = None) -> dict:
    """Hand the specialist a task. Never raises — a refused handoff is an
    answer, and the caller may still have somebody in front of them.

    The plan sent is the intersection of what JIM wants and what the owner
    permits, so a narrower policy quietly narrows the work instead of failing
    it. An empty intersection is a refusal, because a workflow with no phases
    would complete instantly and look like success.
    """
    offer = available(qrme, spec)
    if not offer["available"]:
        return {"started": False, "reason": offer["reason"]}

    link = _link(user_id)
    if link is None or not link["qrme_interactor_token"]:
        return {"started": False,
                "reason": "no tandem link yet; talk to the specialist first"}

    wanted = plan or DEFAULT_PLAN
    agreed = [p for p in wanted if p in offer["phases"]]
    if not agreed:
        return {"started": False,
                "reason": f"specialist permits only {', '.join(offer['phases'])}, "
                          f"none of which this task needs"}

    wf = qrme.start_workflow(spec["qrme_profile_id"],
                             link["qrme_interactor_id"],
                             link["qrme_interactor_token"], goal, agreed)
    if wf is None:
        return {"started": False, "reason": "the specialist declined the task"}

    task_id = db.new_id("stk")
    conn = db.connect()
    conn.execute(
        "INSERT INTO specialist_tasks (id, user_id, qrme_profile_id,"
        " qrme_workflow_id, goal, status, created_at, updated_at)"
        " VALUES (?,?,?,?,?,?,?,?)",
        (task_id, user_id, spec["qrme_profile_id"], wf["id"], goal,
         wf.get("status", "running"), db.utcnow(), db.utcnow()),
    )
    conn.commit()
    return {"started": True, "id": task_id, "goal": goal,
            "qrme_profile_id": spec["qrme_profile_id"],
            "specialist": spec.get("label"),
            "plan": agreed, "status": wf.get("status"),
            "next_phase": wf.get("next_phase")}


def _row(user_id: str, task_id: str):
    return db.connect().execute(
        "SELECT * FROM specialist_tasks WHERE id=? AND user_id=?",
        (task_id, user_id)).fetchone()


def _sync(task_id: str, wf: dict) -> None:
    conn = db.connect()
    conn.execute(
        "UPDATE specialist_tasks SET status=?, updated_at=? WHERE id=?",
        (wf.get("status", "running"), db.utcnow(), task_id))
    conn.commit()


def _shape(row, wf: dict | None) -> dict:
    """One response shape whether QRME answered or not.

    JIM keeps only the *status* of a handed-off task, never its working
    memory: the drafts live in QRME, under the specialist's own moderation and
    the user's own capability token. Mirroring them here would quietly make
    JIM a second copy of somebody's generated health correspondence.
    """
    out = {"id": row["id"], "goal": row["goal"],
           "qrme_profile_id": row["qrme_profile_id"],
           "status": row["status"], "created_at": row["created_at"]}
    if wf is None:
        out["reachable"] = False
        out["note"] = "the specialist could not be reached; last known status"
        return out
    out["reachable"] = True
    out["status"] = wf.get("status", row["status"])
    out["next_phase"] = wf.get("next_phase")
    out["awaiting"] = wf.get("awaiting")
    out["phases_done"] = sorted(wf.get("memory", {}))
    return out


def advance(user_id: str, task_id: str, qrme) -> dict | None:
    """Run the specialist's next phase. None if there is no such task."""
    row = _row(user_id, task_id)
    if row is None:
        return None
    link = _link(user_id)
    token = link["qrme_interactor_token"] if link else None
    wf = qrme.advance_workflow(row["qrme_profile_id"],
                               row["qrme_workflow_id"], token) if qrme else None
    if wf is not None:
        _sync(task_id, wf)
        row = _row(user_id, task_id)
    return _shape(row, wf)


def status(user_id: str, task_id: str, qrme) -> dict | None:
    row = _row(user_id, task_id)
    if row is None:
        return None
    link = _link(user_id)
    token = link["qrme_interactor_token"] if link else None
    wf = qrme.workflow_status(row["qrme_profile_id"],
                              row["qrme_workflow_id"], token) if qrme else None
    if wf is not None:
        _sync(task_id, wf)
        row = _row(user_id, task_id)
    return _shape(row, wf)


def list_for(user_id: str) -> list[dict]:
    """Local view of every task handed off, newest last. Deliberately does not
    call QRME once per row — a list screen should not fan out."""
    return [{"id": r["id"], "goal": r["goal"], "status": r["status"],
             "qrme_profile_id": r["qrme_profile_id"],
             "created_at": r["created_at"], "updated_at": r["updated_at"]}
            for r in db.connect().execute(
                "SELECT * FROM specialist_tasks WHERE user_id=?"
                " ORDER BY created_at, rowid", (user_id,)).fetchall()]
