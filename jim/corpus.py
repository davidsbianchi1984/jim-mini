"""The offline training corpus — every exchange banked so the local model grows.

`offline.py` makes the zero-egress guarantee: with `JIM_OFFLINE` set, nothing
leaves the machine. That makes offline mode *safe*. It does not make it
*capable* — a sealed machine with no local model to fall back on answers with
the stub. This module is the other half: it banks every exchange the agents
have — JIM, the coach, the mailbox, the reach-out cascade, and (when this seam
is lifted into QRME) a synthetic profile — as a training example, so that the
local model trained from it grows able enough for a person to actually run
offline.

## Captured at the one place every exchange passes

:func:`jim.llm.generate_for_user` is the choke point every generated word goes
through. :func:`capture` is called there, so the corpus is complete by
construction rather than by remembering to log at each call site — the same
reasoning the erase cascade uses to read the schema instead of a hand list.

## The person owns it, and can end it

Capture is on by default — it is the person's own data, banked for their own
offline model, the same posture the memory vault takes. But it is theirs:
:func:`set_consent` turns it off, :func:`purge` clears it, and — because the
table is `user_id`-scoped — a full account erase reaches it with no line of its
own (jim/life.py reads the schema). Nothing is captured while capture is off.

## The vault learns it on its own (3.0.7)
Turning capture on plants a **standing learn task** in the tandem vault —
PDI's `corpus.learn`, scoped to this person's bundles and nothing else —
so the resident indexes what is banked every day without anybody pressing
anything, and the coach's grounded answers stand on it. Turning capture off
takes the task back. The bank archives itself every :data:`ARCHIVE_EVERY`
examples once a vault is there, so the bundles the task learns from exist
without a press either. All of it honest at the edges: no vault, an older
tandem, or an unreached one each say so in `why` rather than pretending a
task stands.

## Honest about what is wired

The corpus banks now. Training a local language model from it, and serving that
model when offline, is the infrastructure step — :func:`posture` says how many
examples are banked and whether that model is actually wired yet (it is not),
the same way the telephony and mail seams name their transports. The corpus
filling is what that step waits on.
"""

from __future__ import annotations

import json

from . import audit, db

#: A single example's text is capped so one runaway prompt cannot bloat the
#: bank. Generous enough for a real exchange; the cap is a guard, not a budget.
MAX_CHARS = 8000

#: The corpus size at which training a local model from it starts to be worth
#: doing. A heuristic, and named here rather than buried: below it, a local
#: model would be a coincidence with a version number (jim/finetune.py holds
#: the same line for the clinical model, at its own smaller scale).
READY_AT = 200
#: The bank seals itself into the vault every this-many un-archived examples
#: (best-effort, at the capture point), so the standing learn task always has
#: bundles to learn from without a press.
ARCHIVE_EVERY = 50
#: How often the vault's standing learn task cycles.
LEARN_EVERY_HOURS = 24.0


def _bundle_prefix(user_id: str) -> str:
    return f"jim/{user_id}/corpus/"


def _learn_task_id(user_id: str) -> str | None:
    row = db.connect().execute(
        "SELECT learn_task_id FROM corpus_consent WHERE user_id=?",
        (user_id,)).fetchone()
    return row["learn_task_id"] if row and row["learn_task_id"] else None


def _set_learn_task_id(user_id: str, task_id: str | None) -> None:
    conn = db.connect()
    conn.execute(
        "INSERT INTO corpus_consent (user_id, enabled, updated_at, learn_task_id)"
        " VALUES (?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET"
        " learn_task_id=excluded.learn_task_id, updated_at=excluded.updated_at",
        (user_id, 1, db.utcnow(), task_id))
    conn.commit()


def plant_learning(user_id: str, pdi=None) -> dict:
    """Plant the standing learn task in the vault: PDI's `corpus.learn`,
    scoped to this person's bundles, every :data:`LEARN_EVERY_HOURS`. One
    per person — a task already standing is reported, not doubled. Every
    edge says why in words: no vault, an older tandem, an unreached one."""
    standing = _learn_task_id(user_id)
    if standing:
        return {"planted": True, "task_id": standing,
                "every_hours": LEARN_EVERY_HOURS, "why": None}
    if pdi is None:
        return {"planted": False, "task_id": None,
                "every_hours": LEARN_EVERY_HOURS, "why": "no vault configured"}
    try:
        task = pdi.resident_stand(
            goal=f"learn from the corpus: {user_id}",
            steps=[{"tool": "corpus.learn",
                    "args": {"prefix": _bundle_prefix(user_id)}}],
            every_hours=LEARN_EVERY_HOURS)
    except Exception as exc:  # noqa: BLE001 — said, never crashed through
        return {"planted": False, "task_id": None,
                "every_hours": LEARN_EVERY_HOURS,
                "why": f"{type(exc).__name__}: {exc}"[:200]}
    if task is None:
        return {"planted": False, "task_id": None,
                "every_hours": LEARN_EVERY_HOURS,
                "why": "the vault has no standing tasks (older PDI)"}
    _set_learn_task_id(user_id, task["id"])
    audit.record("corpus.planted", user_id=user_id, ref=task["id"])
    return {"planted": True, "task_id": task["id"],
            "every_hours": LEARN_EVERY_HOURS, "why": None}


def unplant_learning(user_id: str, pdi=None) -> dict:
    """Take the standing learn task back. The row lets go only after the
    vault did — a cancel that cannot reach the vault leaves the id so the
    next try can still end the task."""
    standing = _learn_task_id(user_id)
    if not standing:
        return {"unplanted": False, "task_id": None, "why": "nothing planted"}
    if pdi is None:
        return {"unplanted": False, "task_id": standing,
                "why": "no vault configured to cancel it in"}
    try:
        pdi.resident_cancel(standing)
    except Exception as exc:  # noqa: BLE001
        return {"unplanted": False, "task_id": standing,
                "why": f"{type(exc).__name__}: {exc}"[:200]}
    _set_learn_task_id(user_id, None)
    audit.record("corpus.unplanted", user_id=user_id, ref=standing)
    return {"unplanted": True, "task_id": standing, "why": None}


def learning(user_id: str, pdi=None) -> dict:
    """The standing learn task as the vault sees it now — or why there is
    none. Reads keep the real vault; an unreached one is said."""
    standing = _learn_task_id(user_id)
    out = {"planted": bool(standing), "task_id": standing,
           "every_hours": LEARN_EVERY_HOURS, "status": None,
           "next_run_at": None, "why": None}
    if not standing:
        out["why"] = ("capture is off" if not opted_in(user_id)
                      else "no vault configured" if pdi is None
                      else "not planted yet — archiving plants it")
        return out
    if pdi is None:
        out["why"] = "planted, but no vault is configured to read it from"
        return out
    try:
        found = {t["id"]: t for t in pdi.resident_tasks()}
    except Exception as exc:  # noqa: BLE001
        out["why"] = f"{type(exc).__name__}: {exc}"[:200]
        return out
    task = found.get(standing)
    if task is None:
        out["why"] = "the vault no longer holds this task"
        return out
    out["status"] = task.get("status")
    out["next_run_at"] = task.get("next_run_at")
    return out


def _vault_for(user_id: str):
    """The plan-gated write vault for a person, reached without a request —
    the capture point has no `app`. None on an open plan or no tandem."""
    try:
        from . import pdi_client, storage, tiers
        return storage.vault_for(tiers.governing_plan(user_id),
                                 pdi_client.active())
    except Exception:  # noqa: BLE001 — a bank that could break a turn is not worth having
        return None


def _unarchived(user_id: str) -> int:
    return db.connect().execute(
        "SELECT COUNT(*) AS n FROM training_examples WHERE user_id=?"
        " AND archived_at IS NULL", (user_id,)).fetchone()["n"]


def opted_in(user_id: str) -> bool:
    """Whether this person's exchanges are being banked. Default: yes — it is
    their own data for their own offline model. No row means the default."""
    row = db.connect().execute(
        "SELECT enabled FROM corpus_consent WHERE user_id=?",
        (user_id,)).fetchone()
    return True if row is None else bool(row["enabled"])


def set_consent(user_id: str, on: bool, pdi=None) -> dict:
    """Turn banking on or off. Off is honoured at the capture point — nothing
    is stored while it is off — and does not touch what is already banked
    (:func:`purge` does that). On plants the vault's standing learn task;
    off takes it back."""
    conn = db.connect()
    conn.execute(
        "INSERT INTO corpus_consent (user_id, enabled, updated_at)"
        " VALUES (?,?,?) ON CONFLICT(user_id) DO UPDATE SET"
        " enabled=excluded.enabled, updated_at=excluded.updated_at",
        (user_id, 1 if on else 0, db.utcnow()))
    conn.commit()
    audit.record("corpus.consent", user_id=user_id,
                 ref="on" if on else "off")
    if on:
        plant_learning(user_id, pdi)
    else:
        unplant_learning(user_id, pdi)
    return {**bank(user_id), "learning": learning(user_id, pdi)}


def capture(user_id: str, system: str, prompt: str, completion: str,
            provider: str, source: str | None = None) -> None:
    """Bank one exchange, best-effort. Never raises into the generation path:
    a corpus that could break a reply is not worth having. Skips when the
    person has capture off, and when there is nothing to learn from."""
    try:
        completion = (completion or "").strip()
        if not completion or not opted_in(user_id):
            return
        conn = db.connect()
        conn.execute(
            "INSERT INTO training_examples (id, user_id, source, provider,"
            " system, prompt, completion, created_at)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (db.new_id("tex"), user_id, (source or "").strip(),
             (provider or "").strip(), (system or "")[:MAX_CHARS],
             (prompt or "")[:MAX_CHARS], completion[:MAX_CHARS], db.utcnow()))
        conn.commit()
        # The bank seals itself: every ARCHIVE_EVERY un-archived examples,
        # a bundle lands in the vault for the standing learn task to learn
        # from. Plan-gated like every other seal, and best-effort like the
        # capture around it.
        if _unarchived(user_id) >= ARCHIVE_EVERY:
            pdi = _vault_for(user_id)
            if pdi is not None:
                archive(user_id, pdi=pdi)
    except Exception:  # noqa: BLE001 — capture is never allowed to break a turn
        pass


def bank(user_id: str) -> dict:
    """The corpus, counted: how much is banked, from where, by whom, and how
    much has been archived to the vault."""
    conn = db.connect()
    total = conn.execute(
        "SELECT COUNT(*) AS n FROM training_examples WHERE user_id=?",
        (user_id,)).fetchone()["n"]
    archived = conn.execute(
        "SELECT COUNT(*) AS n FROM training_examples WHERE user_id=?"
        " AND archived_at IS NOT NULL", (user_id,)).fetchone()["n"]
    by_source = {r["source"] or "other": r["n"] for r in conn.execute(
        "SELECT source, COUNT(*) AS n FROM training_examples WHERE user_id=?"
        " GROUP BY source", (user_id,)).fetchall()}
    by_provider = {r["provider"] or "unknown": r["n"] for r in conn.execute(
        "SELECT provider, COUNT(*) AS n FROM training_examples WHERE user_id=?"
        " GROUP BY provider", (user_id,)).fetchall()}
    return {"examples": total, "archived": archived,
            "by_source": by_source, "by_provider": by_provider,
            "capturing": opted_in(user_id),
            "ready_to_train": total >= READY_AT, "ready_at": READY_AT}


def posture(user_id: str, app=None, pdi=None) -> dict:
    """What the corpus is and what offline capability still waits on — the
    bank, the sealing guarantee, and whether a local model is actually wired."""
    from . import finetune, offline
    trained = finetune.latest(user_id)
    b = bank(user_id)
    return {
        **b,
        # The zero-egress guarantee this corpus makes worth having.
        "offline": offline.status(app),
        # The clinical model finetune.py already trains from this person's
        # answered follow-ups — a real local weight file, at its own scale.
        "local_clinical_model": (
            {"version": trained["version"], "backend": trained["backend"],
             "examples": trained["examples"], "active": bool(trained["active"])}
            if trained else None),
        # The honest seam: a local *language* model trained from this corpus,
        # and served when offline, is the infrastructure step. False until one
        # is wired; the corpus filling is what it waits on.
        "local_language_model_ready": False,
        # The vault's standing learn task for this corpus — the resident
        # indexes it on its own — or why there is none.
        "learning": learning(user_id, pdi),
        "note": ("every exchange is banked on this machine as training data; a "
                 "local language model trained from it — and served when "
                 "offline — is the next step, and grows more capable as the "
                 "corpus fills. Capture is the person's own, and off stops it."),
    }


def export(user_id: str, limit: int = 5000) -> list[dict]:
    """The corpus as training examples — the shape a training run consumes.
    Newest last, so a reader sees the person's history in the order it
    happened."""
    rows = db.connect().execute(
        "SELECT source, provider, system, prompt, completion, created_at"
        " FROM training_examples WHERE user_id=? ORDER BY created_at LIMIT ?",
        (user_id, int(limit))).fetchall()
    return [{"system": r["system"], "prompt": r["prompt"],
             "completion": r["completion"], "source": r["source"],
             "provider": r["provider"], "at": r["created_at"]} for r in rows]


def archive(user_id: str, pdi=None) -> dict:
    """Seal the un-archived corpus into the vault as one bundle, so it survives
    this machine and rides the same erasure the rest of the vault does. A
    no-op with nothing to archive; honest when no vault is configured."""
    conn = db.connect()
    rows = conn.execute(
        "SELECT id, source, provider, system, prompt, completion, created_at"
        " FROM training_examples WHERE user_id=? AND archived_at IS NULL"
        " ORDER BY created_at", (user_id,)).fetchall()
    if not rows:
        return {"archived": 0, "reason": "nothing new to archive"}
    if pdi is None:
        return {"archived": 0, "reason": "no vault configured — the corpus is "
                "kept on this machine until one is"}
    bundle = [{"system": r["system"], "prompt": r["prompt"],
               "completion": r["completion"], "source": r["source"],
               "provider": r["provider"], "at": r["created_at"]} for r in rows]
    run_id = db.new_id("cor")
    from . import life
    # Through vault_store, never a bare put: the seal and the vault_keys row
    # land together, so an erase knows this bundle exists (jim/recall.py).
    life.vault_store(pdi, user_id, f"jim/{user_id}/corpus/{run_id}",
                     {"examples": bundle, "count": len(bundle),
                      "at": db.utcnow()})
    # A bundle in the vault is what the standing learn task learns from;
    # make sure one stands — a person who never touched the switch (capture
    # is on by default) gets the task on their first archive.
    if opted_in(user_id):
        plant_learning(user_id, pdi)
    now = db.utcnow()
    conn.executemany(
        "UPDATE training_examples SET archived_at=? WHERE id=?",
        [(now, r["id"]) for r in rows])
    conn.commit()
    audit.record("corpus.archived", user_id=user_id, ref=f"{len(rows)}")
    return {"archived": len(rows), "bundle": run_id}


def purge(user_id: str) -> dict:
    """Clear this person's banked corpus — the forget door for training data,
    distinct from a full account erase (which reaches it too). What is already
    archived in the vault is cleared by the vault's own forget path."""
    conn = db.connect()
    n = conn.execute(
        "SELECT COUNT(*) AS n FROM training_examples WHERE user_id=?",
        (user_id,)).fetchone()["n"]
    conn.execute("DELETE FROM training_examples WHERE user_id=?", (user_id,))
    conn.commit()
    audit.record("corpus.purged", user_id=user_id, ref=f"{n}")
    return {"purged": n}
