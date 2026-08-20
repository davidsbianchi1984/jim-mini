"""The state that survives between sessions — a latent continuity vector.

## What was missing

`adaptation.py` builds a **user-specific model**: an offline pass over the
whole of somebody's stored history, producing a versioned profile that
`coach.reply` renders into its system prompt. It is the right artifact and it
is genuinely derived.

Two things were wrong with how it reached a conversation.

**It was a snapshot, and nothing moved between snapshots.** QRME's
`adaptation.py` carries a per-(profile, interactor) latent vector, EMA-updated
after *every* interaction, so cross-session state survives logins, devices and
model calls. JIM had no equivalent. A person could check in every day for a
month and the Guardian would enter each conversation exactly as it entered the
first one.

**And the snapshot was taken by hand.** `rebuild` is called from one place in
the entire product — `POST /adaptation/{user}`, a console button. Nothing calls
it after a check-in, a coach turn or an answered follow-up. `prompt_lines`
returns `[]` when there is no row, and on a user who never pressed that button
there is never a row.

    asked     can a user-specific model be built from the history
    mattered  does anything ever build it

So the clause-11 artifact existed, was correct, was tested, and on nearly every
real user had never been computed. That is not a bug in `adaptation.py`; it is
a missing edge between it and the loop it was built for.

## What this module is

A small named vector per user, in `user_continuity`, updated by
:func:`observe` at the three moments a signal actually arrives — a check-in is
logged, a coach turn happens, a follow-up is answered. Exponential moving
average, so recent evidence moves it and old evidence decays without being
deleted.

:func:`attention_lines` renders it the way QRME's `attention_prompt` does: as
weighting over what the model should attend to, not as instructions about what
to say. Identity, boundaries and safety behaviour are fixed elsewhere and this
never touches them.

## Three rules it keeps

**It carries no content.** Six floats and three counters. Not a phrase, not a
condition name, not a message. The vector is derived from *tallies* — how
many, how recent, how long — and a person reading the whole row learns nothing
about what was said. This matters more here than in the sibling product,
because the thing being counted is somebody's health, and the standing
constraint on this codebase is that nothing private is assumed safe to keep.
`test_the_vector_carries_no_content` holds it to that.

**Confidence is earned from evidence.** `attention_lines` is silent until
there are enough observations to mean anything; `_MIN_OBSERVATIONS` is the
same kind of floor `adaptation._MIN_FOLLOWUPS` sets, for the same reason. An
invented preference is worse than an absent one.

**It is not a weight file.** The transformer stays the vendor's. What this
owns is the state that conditions it, and `state()` says so in its own
`method` field rather than letting a reader assume a fine-tune happened.
"""

from __future__ import annotations

import json

from . import db

#: EMA step. The same 0.3 QRME uses: recent evidence moves the vector by about
#: a third of the distance, so a single unusual day bends it without erasing
#: what came before.
_ALPHA = 0.3

#: Below this, `attention_lines` says nothing at all. Six observations is
#: roughly a week of daily contact — enough that a pattern is a pattern.
_MIN_OBSERVATIONS = 6

#: The named dimensions, all 0..1. Interpretable on purpose: a reader can be
#: told what each one means and check it against their own experience, which
#: an opaque learned representation would not allow.
DIMS = ("engagement", "candor", "strain", "receptiveness", "steadiness",
        "continuity")

_MEANING = {
    "engagement": "how much this person brings to the Guardian unprompted",
    "candor": "how much they say when they do — length, not content",
    "strain": "where their own check-ins have been sitting lately",
    "receptiveness": "whether guidance has been landing, from the follow-ups",
    "steadiness": "how much their check-ins move day to day",
    "continuity": "how long this has been going on",
}


def _default() -> dict:
    # Deliberately mid-range rather than zero. A new user is unknown, not
    # disengaged, and a vector that starts at the floor would have the Guardian
    # treat somebody's first week as evidence of withdrawal.
    return {"engagement": 0.5, "candor": 0.5, "strain": 0.3,
            "receptiveness": 0.5, "steadiness": 0.5, "continuity": 0.0}


def get(user_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM user_continuity WHERE user_id=?", (user_id,)).fetchone()
    if row is None:
        return None
    return {"user_id": user_id, "vector": json.loads(row["vector"]),
            "observations": row["observations"], "version": row["version"],
            "updated_at": row["updated_at"]}


def _target(kind: str, signal: dict) -> dict:
    """Where this one observation says the vector should be.

    `signal` carries numbers only — never the text of anything. Each caller
    passes what it already has; absent keys leave that dimension where it is,
    which is why the target starts as a copy of the default rather than zeros.
    """
    target = _default()

    if kind == "checkin":
        # The check-in scales are 1..5 in this product. Strain reads stress
        # and the inverse of mood, because a flat mood with low stress is not
        # the same state as either one alone.
        stress = signal.get("stress")
        mood = signal.get("mood")
        parts = []
        if stress is not None:
            parts.append((float(stress) - 1) / 4)
        if mood is not None:
            parts.append(1 - (float(mood) - 1) / 4)
        if parts:
            target["strain"] = sum(parts) / len(parts)
        # Logging a check-in at all is engagement.
        target["engagement"] = 0.8

    elif kind == "coach_turn":
        target["engagement"] = 0.9
        # Length, not content: how much somebody chose to write is a signal
        # about the relationship and carries none of what they wrote.
        chars = int(signal.get("length") or 0)
        target["candor"] = min(chars / 400, 1.0)

    elif kind == "followup":
        # The one input that says whether any of this is working.
        target["receptiveness"] = 1.0 if signal.get("helped") else 0.0
        target["engagement"] = 0.8

    return target


def observe(user_id: str, kind: str, **signal) -> dict:
    """Fold one interaction into the vector.

    Called from the loop rather than from a button — that distinction is the
    whole point of this module. `kind` is one of `checkin`, `coach_turn`,
    `followup`; anything else is ignored rather than raising, because a
    telemetry edge must never be able to fail somebody's check-in.
    """
    if kind not in ("checkin", "coach_turn", "followup"):
        return get(user_id) or {}

    current = get(user_id)
    vector = dict(current["vector"]) if current else _default()
    observations = (current["observations"] if current else 0) + 1
    target = _target(kind, signal)

    # Only the dimensions this kind of observation actually speaks to move.
    # A coach turn says nothing about strain, and letting it pull strain back
    # toward the default would quietly launder a bad week into a neutral one.
    speaks_to = {
        "checkin": ("strain", "engagement"),
        "coach_turn": ("engagement", "candor"),
        "followup": ("receptiveness", "engagement"),
    }[kind]
    for dim in speaks_to:
        vector[dim] = round(
            vector[dim] + _ALPHA * (target[dim] - vector[dim]), 4)

    # Continuity and steadiness are properties of the series, not of one
    # observation, so they are computed rather than averaged toward.
    vector["continuity"] = round(min(observations / 30, 1.0), 4)
    vector["steadiness"] = _steadiness(user_id, vector["steadiness"])

    conn = db.connect()
    conn.execute(
        "INSERT INTO user_continuity (user_id, vector, observations, version,"
        " updated_at) VALUES (?,?,?,1,?)"
        " ON CONFLICT (user_id) DO UPDATE SET vector=excluded.vector,"
        " observations=excluded.observations, version=version+1,"
        " updated_at=excluded.updated_at",
        (user_id, json.dumps(vector), observations, db.utcnow()))
    conn.commit()
    return get(user_id)


def _steadiness(user_id: str, fallback: float) -> float:
    """How much this person's own check-ins move, over their last ten.

    Spread of their own readings against their own middle — not against a
    population. The bands module already establishes that a personal baseline
    is the only meaningful comparison in this product, and a steadiness score
    computed against everybody else's mood would be the same mistake one layer
    down.
    """
    rows = db.connect().execute(
        "SELECT mood, energy, stress FROM checkins WHERE user_id=?"
        " ORDER BY rowid DESC LIMIT 10", (user_id,)).fetchall()
    values = [float(r["mood"]) for r in rows if r["mood"] is not None]
    if len(values) < 3:
        return fallback
    middle = sum(values) / len(values)
    spread = sum(abs(v - middle) for v in values) / len(values)
    # Mean absolute deviation on a 1..5 scale tops out around 2.
    return round(max(0.0, 1.0 - spread / 2), 4)


def attention_lines(user_id: str) -> list[str]:
    """The vector, rendered as attention weighting for the coach's prompt.

    Weighting, not instruction. It says which parts of the context to hold
    heavier given where this person has been; it does not say what to
    conclude, and it never touches identity, boundaries or the safety
    behaviour those are fixed by.

    Silent below `_MIN_OBSERVATIONS`, because a vector built from two
    check-ins is a shape in noise, and a Guardian that starts pacing itself
    around one is worse than one that has not started.
    """
    state = get(user_id)
    if state is None or state["observations"] < _MIN_OBSERVATIONS:
        return []
    v = state["vector"]
    weights = {
        "what they told you in earlier sessions":
            round(0.2 + 0.8 * v["continuity"] * v["engagement"], 2),
        "gentleness and pacing": round(v["strain"], 2),
        "concrete next steps rather than exploring":
            round(v["receptiveness"], 2),
        "asking rather than assuming": round(1 - v["candor"], 2),
    }
    rendered = ", ".join(f"{k}: {w}" for k, w in weights.items())
    return [
        f"Cross-session state for this person (continuity vector v"
        f"{state['version']}, {state['observations']} observations). "
        f"Attention weighting for this reply — {rendered}. "
        "Weight your focus accordingly; who you are, what you will not do, "
        "and every safety path stay exactly as they are."
    ]


def state(user_id: str) -> dict:
    """What a person is shown when they ask what the Guardian remembers.

    Named dimensions with their meanings in plain words, because a number
    somebody cannot interpret is not transparency. `carries` is stated
    explicitly rather than left to be inferred from the absence of content.
    """
    row = get(user_id)
    if row is None:
        return {
            "built": False,
            "note": "nothing yet — this fills in as you check in, talk to the "
                    "coach, and answer whether guidance helped",
            "carries": "counts and timings only, never anything you wrote",
        }
    return {
        "built": True,
        "version": row["version"],
        "observations": row["observations"],
        "conditioning": row["observations"] >= _MIN_OBSERVATIONS,
        "vector": row["vector"],
        "meanings": _MEANING,
        "method": "named dimensions, exponential moving average, computed "
                  "on this host from your own history — not a fine-tuned "
                  "model and not a weight file",
        "carries": "counts and timings only, never anything you wrote",
        "updated_at": row["updated_at"],
    }


def forget(user_id: str) -> bool:
    """Drop the vector. Every derived thing in this product has to be
    droppable by the person it was derived from, and one that quietly could
    not be would make the rest of the promise untrue."""
    from . import letter as letter_mod
    letter_mod.mark_forgotten(user_id)
    conn = db.connect()
    cur = conn.execute("DELETE FROM user_continuity WHERE user_id=?", (user_id,))
    conn.commit()
    return cur.rowcount > 0
