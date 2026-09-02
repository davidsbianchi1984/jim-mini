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


def opted_in(user_id: str) -> bool:
    """Whether this person's exchanges are being banked. Default: yes — it is
    their own data for their own offline model. No row means the default."""
    row = db.connect().execute(
        "SELECT enabled FROM corpus_consent WHERE user_id=?",
        (user_id,)).fetchone()
    return True if row is None else bool(row["enabled"])


def set_consent(user_id: str, on: bool) -> dict:
    """Turn banking on or off. Off is honoured at the capture point — nothing
    is stored while it is off — and does not touch what is already banked
    (:func:`purge` does that)."""
    conn = db.connect()
    conn.execute(
        "INSERT INTO corpus_consent (user_id, enabled, updated_at)"
        " VALUES (?,?,?) ON CONFLICT(user_id) DO UPDATE SET"
        " enabled=excluded.enabled, updated_at=excluded.updated_at",
        (user_id, 1 if on else 0, db.utcnow()))
    conn.commit()
    audit.record("corpus.consent", user_id=user_id,
                 ref="on" if on else "off")
    return bank(user_id)


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


def posture(user_id: str, app=None) -> dict:
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
