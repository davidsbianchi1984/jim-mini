"""The user-specific model — clause 11, and what it honestly can be.

Clause 11, verbatim: "adapting the large language model based on the received
input comprises **training a user-specific version of the large language
model** based on the received input. The system may generate user-specific
models that adapt to professional roles, workflows, or collaborative
environments. **Training may employ secure, decentralized methods** to ensure
data integrity across distributed networks."

What JIM had until now was the last mile of that: :func:`guidance.personalize`
renders a handful of live preferences into the system prompt. Real, useful,
and not what the claim describes — nothing was *derived* from the history, and
nothing was an artifact you could point at, version, or seal.

This module is the artifact. An offline pass reads the whole of this user's own
stored history — declared conditions, check-in trend, which life areas they
actually bring, what tone they asked for, and (the input that makes this worth
having) **which guidance actually helped them**, from the follow-up record — and
writes a per-user adaptation profile with named, countable dimensions. The
profile is versioned, timestamped, and sealed into the PDI vault when a tandem
is configured; that sealing, with the user holding the keys, is the "secure,
decentralized method" the clause asks for. Nothing is transmitted to any model
vendor in the process.

Two honesty rules, the same ones QRME's ``adaptation.py`` keeps:

- **This is not a weight file.** The transformer stays the vendor's. What JIM
  owns is the state that conditions it, and the profile says so in its own
  ``method`` field rather than letting a reader assume a fine-tune happened.
- **Confidence is earned from evidence, not fluency.** A profile built from
  two check-ins and no follow-ups reports low confidence however tidy it
  looks, and ``prompt_lines`` stays quiet about dimensions with nothing behind
  them — an invented preference is worse than an absent one.
"""

from __future__ import annotations

import json

from . import db

VERSION = 1

# How many answered follow-ups it takes before "this helps you" is a claim
# rather than a coincidence.
_MIN_FOLLOWUPS = 3


def _followup_tallies(user_id: str) -> dict:
    rows = db.connect().execute(
        "SELECT condition, helped, COUNT(*) AS n FROM guidance_followups"
        " WHERE user_id=? AND helped IS NOT NULL GROUP BY condition, helped",
        (user_id,)).fetchall()
    out: dict[str, dict] = {}
    for r in rows:
        # `helped_count` / `answered_count`, not `helped` / `answered`:
        # the follow-up itself answers under those names as booleans, and a
        # count under the same name is the primitive clash
        # `wire_name_collisions.txt` records.
        entry = out.setdefault(r["condition"],
                               {"helped_count": 0, "did_not": 0})
        entry["helped_count" if r["helped"] else "did_not"] += r["n"]
    for entry in out.values():
        total = entry["helped_count"] + entry["did_not"]
        entry["answered_count"] = total
        entry["hit_rate"] = (round(entry["helped_count"] / total, 2)
                             if total else None)
    return out


def _area_counts(user_id: str) -> dict:
    rows = db.connect().execute(
        "SELECT area, COUNT(*) AS n FROM coach_messages"
        " WHERE user_id=? AND role='user' GROUP BY area ORDER BY n DESC",
        (user_id,)).fetchall()
    return {r["area"]: r["n"] for r in rows}


def _checkin_trend(user_id: str) -> dict:
    row = db.connect().execute(
        "SELECT COUNT(*) AS n, AVG(mood) AS mood, AVG(energy) AS energy,"
        " AVG(stress) AS stress FROM checkins WHERE user_id=?",
        (user_id,)).fetchone()
    if not row or not row["n"]:
        return {"count": 0}
    return {"count": row["n"],
            "avg_mood": round(row["mood"], 2) if row["mood"] else None,
            "avg_energy": round(row["energy"], 2) if row["energy"] else None,
            "avg_stress": round(row["stress"], 2) if row["stress"] else None}


def rebuild(user_id: str, pdi=None) -> dict:
    """The offline pass: recompute this user's adaptation profile from the
    whole of their own stored history, then seal it."""
    from . import guardian, life

    user = guardian.get_user(user_id)
    if user is None:
        raise ValueError("unknown user")

    tallies = _followup_tallies(user_id)
    areas = _area_counts(user_id)
    trend = _checkin_trend(user_id)
    personality = user.get("personality") or {}

    # Evidence volume, not model fluency, decides confidence.
    answered = sum(t["answered_count"] for t in tallies.values())
    evidence = answered + trend.get("count", 0) + sum(areas.values())
    confidence = round(min(1.0, evidence / 20), 2)

    profile = {
        "version": VERSION,
        "known_conditions": user.get("known_conditions") or [],
        # What has actually worked for this person, per condition — the
        # "received input" of clause 11 that is worth adapting on.
        "what_helps": tallies,
        "areas_brought": areas,
        "checkins": trend,
        "tone": personality.get("tone"),
        "explain_level": personality.get("explain_level"),
        # "user-specific models that adapt to professional roles" (clause 11).
        "occupation": personality.get("occupation"),
        "beliefs_posture": personality.get("beliefs_posture") or "neutral",
        "evidence_items": evidence,
        "confidence": confidence,
        "method": ("user-specific adaptation profile derived locally from this "
                   "user's own stored history — it conditions the model's "
                   "prompt; the transformer's weights are the vendor's and are "
                   "not modified here"),
    }

    sealed = None
    if pdi is not None:
        # The clause's "secure, decentralized method": the artifact goes into
        # the user's own vault, keys theirs, nothing to a model vendor.
        sealed = life.vault_store(
            pdi, user_id, f"jim/{user_id}/adaptation/v{VERSION}", profile)

    conn = db.connect()
    conn.execute(
        "INSERT OR REPLACE INTO user_models (user_id, version, profile,"
        " evidence_items, confidence, pdi_key, rebuilt_at)"
        " VALUES (?,?,?,?,?,?,?)",
        (user_id, VERSION, json.dumps(profile), evidence, confidence,
         sealed, db.utcnow()),
    )
    conn.commit()

    guardian._event(user_id, "user_model_rebuilt",
                    detail={"version": VERSION, "evidence_items": evidence,
                            "confidence": confidence,
                            "sealed": sealed is not None})
    return {**_row_out(get_row(user_id)), "sealed_key": sealed}


def _evidence_now(user_id: str) -> int:
    """How much history exists to derive from, counted the same way `rebuild`
    counts it. Three cheap COUNTs; no profile is built."""
    tallies = _followup_tallies(user_id)
    return (sum(t["answered_count"] for t in tallies.values())
            + _checkin_trend(user_id).get("count", 0)
            + sum(_area_counts(user_id).values()))


#: How much new history has to arrive before the profile is worth recomputing.
#: Small enough that a person who uses the app for a week has one; large
#: enough that the rebuild is not run on every turn of a conversation.
_REFRESH_AFTER = 5


def ensure_fresh(user_id: str, pdi=None) -> bool:
    """Rebuild the profile if the history has moved on since it was built.

    ## Why this function exists

    `rebuild` had exactly one caller in the whole product — `POST
    /adaptation/{user}`, a button in the desktop console. `coach.reply` reads
    the profile through `prompt_lines` on every turn, and `prompt_lines`
    returns `[]` when there is no row.

        asked     can a user-specific model be built from the history
        mattered  does anything ever build it

    So on every user who never pressed that button — which is every user who
    only ever opened the phone app — the clause-11 artifact had never been
    computed, and the coach ran unadapted forever while the code that would
    have adapted it sat there correct and tested.

    Cheap by construction: three COUNTs on the common path, and a rebuild only
    when `_REFRESH_AFTER` new pieces of evidence have accumulated. Returns
    whether it rebuilt, so a caller can say so if it wants to.

    Never raises. This runs on the path of somebody asking their health
    assistant a question, and a failure to refresh a *derived* artifact must
    not cost them the answer.
    """
    try:
        row = get_row(user_id)
        evidence = _evidence_now(user_id)
        if row is not None and evidence - row["evidence_items"] < _REFRESH_AFTER:
            return False
        if row is None and evidence == 0:
            return False          # nothing to derive from yet
        rebuild(user_id, pdi=pdi)
        return True
    except Exception:
        return False


def get_row(user_id: str):
    return db.connect().execute(
        "SELECT * FROM user_models WHERE user_id=?", (user_id,)).fetchone()


def _row_out(row) -> dict:
    if row is None:
        return {"built": False,
                "note": "no adaptation profile yet — POST /adaptation/{user} "
                        "builds one from the history already on record"}
    return {"built": True, "version": row["version"],
            "profile": json.loads(row["profile"]),
            "evidence_items": row["evidence_items"],
            "confidence": row["confidence"],
            "vaulted": row["pdi_key"] is not None,
            "rebuilt_at": row["rebuilt_at"]}


def get(user_id: str) -> dict:
    return _row_out(get_row(user_id))


def prompt_lines(user_id: str) -> list[str]:
    """The profile, rendered for a system prompt — and silent about anything
    the evidence does not support."""
    row = get_row(user_id)
    if row is None:
        return []
    profile = json.loads(row["profile"])
    lines: list[str] = []
    for condition, tally in sorted(profile.get("what_helps", {}).items()):
        # `.get` with the old names beside the new: this reads a STORED
        # profile, and one built before the rename carries the old keys
        # until the next rebuild. Crashing on history would be worse than
        # the clash was.
        answered = tally.get("answered_count", tally.get("answered", 0))
        helped = tally.get("helped_count", tally.get("helped", 0))
        if answered < _MIN_FOLLOWUPS:
            continue          # a coincidence is not a finding
        if tally["hit_rate"] is not None and tally["hit_rate"] >= 0.6:
            lines.append(f"guidance for {condition} has worked for this "
                         f"person before ({helped} of "
                         f"{answered} times) — stay with what works")
        elif tally["hit_rate"] is not None and tally["hit_rate"] <= 0.34:
            lines.append(f"guidance for {condition} has NOT been landing for "
                         f"this person ({helped} of "
                         f"{answered}) — try a different approach and "
                         f"offer a human")
    areas = profile.get("areas_brought") or {}
    if areas:
        top = max(areas, key=areas.get)
        if areas[top] >= 3:
            lines.append(f"this person most often brings {top} questions")
    return lines
