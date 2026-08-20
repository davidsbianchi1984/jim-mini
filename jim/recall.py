"""The coach's long-term memory, held beside the data it is made of.

PDI's resident intelligence gave the vault an embedding index and a vector
search that store a hash of the text and never the text (`pdi/resident.py`).
This module is JIM's side of that bargain: the moments worth remembering —
what somebody told the coach, wrote in the journal, put in a check-in note —
are **sealed into the vault** under a memory key and **embedded** under the
same key, so the coach can later find them by meaning rather than by
recency. The vector index knows only hashes; the words themselves sit
AES-256-GCM sealed in the tandem, which is the only place this product lets
sensitive material live.

    asked     does the coach keep continuity with earlier sessions
    mattered  can it find the earlier session that is *about* this one

`continuity.py` already carries how the relationship has moved — attention
weights, never content. This carries the content, on the vault's terms: a
person who mentioned a shoulder injury in March and asks about training in
August gets a coach who remembers the shoulder, because the question's
vector lands near the memory's.

## The rules

**Memory never breaks the doing.** Every function here returns rather than
raises: a check-in that lands and is not remembered beats a check-in
refused because the tandem was down. What happened is said in the return —
`remembered: False` and a reason — never papered over.

**No vault, no memory, no pretending.** With no PDI configured the coach
works exactly as before; recall contributes nothing and says nothing. The
same is true offline: the PDI client consults `offline.allow` at its
socket, and the refusal surfaces here as one more "not remembered".

**One person's memories.** Keys carry the user id and recall drops any
match outside `jim/{user}/memory/` before it fetches a word — a second wall
behind PDI's tenant fence, because this deployment's tenant holds many
people's memories under one token.
"""

from __future__ import annotations

import json

from . import db

#: How much of a moment is kept. A memory is a line, not a transcript —
#: recall folds these into a prompt, and a prompt full of pages is a coach
#: who stops noticing what is in front of it.
MAX_LINE = 400

#: How many remembered lines a coach turn may carry.
RECALLED = 3


def _key(user_id: str, kind: str, ref: str) -> str:
    # Inside the user's own `jim/{user}/` namespace, deliberately: the
    # erasure sweep purges the vault from the `vault_keys` ledger, and the
    # storage-posture guard holds every write to one namespace per person.
    # A memory prefix of its own would be the 0.59.9 defect again — data a
    # wipe was never told about.
    return f"jim/{user_id}/memory/{kind}/{ref}"


def remember(pdi, user_id: str, kind: str, ref: str, text: str) -> dict:
    """Seal one moment and index it. Non-fatal by design."""
    text = (text or "").strip()[:MAX_LINE]
    if pdi is None or not text:
        return {"remembered": False,
                "why": "no vault configured" if pdi is None else "nothing said"}
    key = _key(user_id, kind, ref)
    try:
        # Through `life.vault_store`, never a bare put: the seal and the
        # `vault_keys` row land together, so erasure knows this key exists.
        from . import life
        life.vault_store(pdi, user_id, key,
                         {"line": text, "kind": kind, "at": db.utcnow()})
        indexed = pdi.resident_embed(key, text)
    except Exception as exc:  # noqa: BLE001 — memory never breaks the doing
        return {"remembered": False, "why": f"{type(exc).__name__}: {exc}"[:200]}
    if not indexed:
        # Sealed but not findable — an older PDI without the resident. The
        # words are safe; recall simply will not surface them.
        return {"remembered": False, "why": "the vault has no memory index"}
    return {"remembered": True, "key": key}


def recall(pdi, user_id: str, query: str, top_k: int = RECALLED) -> list[dict]:
    """The moments nearest this question, this person's only."""
    query = (query or "").strip()
    if pdi is None or not query:
        return []
    prefix = f"jim/{user_id}/memory/"
    try:
        matches = pdi.resident_search(query, top_k=top_k * 4)
    except Exception:  # noqa: BLE001
        return []
    out = []
    for m in matches:
        if not m.get("key", "").startswith(prefix):
            continue
        try:
            raw = pdi.get(m["key"])
        except Exception:  # noqa: BLE001
            continue
        if not raw:
            continue
        try:
            entry = json.loads(raw)
        except ValueError:
            continue
        out.append({"kind": entry.get("kind", "memory"),
                    "line": entry.get("line", ""), "score": m.get("score")})
        if len(out) >= top_k:
            break
    return out


def coach_lines(pdi, user_id: str, message: str) -> list[str]:
    """Recall, worded for the prompt: context the model may use, never an
    instruction — the same posture as `continuity.attention_lines`."""
    found = recall(pdi, user_id, message)
    return [f"remembered from an earlier {m['kind']}: {m['line']}"
            for m in found if m["line"]]


def shelf(pdi, user_id: str) -> dict:
    """Every moment the coach remembers about this person, read back.

    The keys come from the local `vault_keys` ledger — the same rows
    erasure walks — and the lines from the vault, so the answer is exactly
    what recall can actually surface, not a claim about it. A tandem that
    cannot be reached answers `readable: false` with whatever keys exist,
    because "I hold twelve memories I cannot show you right now" and "I
    hold nothing" are different answers.
    """
    prefix = f"jim/{user_id}/memory/"
    rows = db.connect().execute(
        "SELECT key FROM vault_keys WHERE user_id=?"
        " ORDER BY rowid", (user_id,)).fetchall()
    keys = [r["key"] for r in rows if r["key"].startswith(prefix)]
    moments, readable = [], pdi is not None
    for key in keys:
        tail = key[len(prefix):]
        kind, _, ref = tail.partition("/")
        entry = {}
        if pdi is not None:
            try:
                raw = pdi.get(key)
                entry = json.loads(raw) if raw else {}
            except Exception:  # noqa: BLE001
                readable = False
        moments.append({"kind": kind, "ref": ref,
                        "line": entry.get("line"),
                        "at": entry.get("at")})
    return {"memories": moments, "readable": readable,
            "held": len(moments)}


def forget(pdi, user_id: str, kind: str, ref: str) -> dict:
    """Unmake one memory: the vector, the seal, and the ledger row — so a
    deleted entry stops being findable, not merely stops being readable.
    Non-fatal like everything here; the caller reports what happened."""
    from . import letter as letter_mod
    letter_mod.mark_forgotten(user_id)
    if pdi is None:
        return {"forgotten": False, "why": "no vault configured"}
    key = _key(user_id, kind, ref)
    try:
        removed = pdi.resident_forget(key)
        pdi.delete(key)
        conn = db.connect()
        conn.execute("DELETE FROM vault_keys WHERE user_id=? AND key=?",
                     (user_id, key))
        conn.commit()
    except Exception as exc:  # noqa: BLE001
        return {"forgotten": False,
                "why": f"{type(exc).__name__}: {exc}"[:200]}
    return {"forgotten": True, "vectors_removed": removed}


def forget_all(pdi, user_id: str) -> int | None:
    """Erasure's call: every vector under this person's memory prefix, in
    one trip. None when the tandem could not be reached — the erasure
    answer says so rather than counting what it cannot see."""
    from . import letter as letter_mod
    letter_mod.mark_forgotten(user_id)
    if pdi is None:
        return None
    try:
        return pdi.resident_forget(f"jim/{user_id}/memory/", prefix=True)
    except Exception:  # noqa: BLE001
        return None


def tabulate(pdi, dataset: str, rows: list[dict],
             source_ref: str | None = None) -> bool:
    """Structured results into a vault table the PDI console can query.

    One resident plan with one `table.append` step, run in the same breath —
    the errand ledger writing itself into the tenant's own shelf. Non-fatal
    like everything here; the caller says `vaulted: False` when this
    answers it.
    """
    if pdi is None or not rows:
        return False
    try:
        return pdi.resident_tabulate(dataset, rows, source_ref=source_ref)
    except Exception:  # noqa: BLE001
        return False
