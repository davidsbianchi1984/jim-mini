"""The offline coach engine — the patents' add-&-norm stack, run on device.

The shape is the Transformer diagram read as product architecture: the
question arrives as the input, and context joins it as residual **add**
layers — ``[user data]``, then the current readings (``[vitals]``,
``[speech]``, ``[tone]``, ``[environment]``) — each add followed by a
**norm** that beats the block into a fixed, unit-stable shape before the
next layer sees it. Prediction then chooses from the stored knowledge —
the curated pack, what JIM learned on its excursions, and what a paid
model turn deposited — weighted by the normalized context, and the
output side gets its own norm before anything is delivered.

Two hard rules, both load-bearing:

* **This module never touches the network.** No provider import, no
  socket. Its whole world is the local store and the local readings —
  that is what makes the coach always-on and effectively free per turn.
  A guard reads this file's imports and holds the promise.
* **Every layer is recorded.** The reply's provenance names each add and
  each norm that ran, and what it contributed — an adaptation nobody can
  see is an uncanny one, and a pipeline nobody can audit is a claim.
"""

from __future__ import annotations

import json
import re

from . import bands, db, knowledge, life

# The output-side norm shares the coach's own safety line.
from .guidance import _DENY

# Below this score the stack stays silent and the stub's honest fallback
# shows — the same posture the curated pack has always held.
_THRESHOLD = 2

_WS = re.compile(r"\s+")


def _norm_text(s: str) -> str:
    return _WS.sub(" ", (s or "")).strip()


# --------------------------------------------------------------------------- #
# the store: curated pack + learned excursions + deposited model turns
# --------------------------------------------------------------------------- #

def deposit(user_id: str, area: str, topic: str, guidance: str,
            source: str, model: str | None = None) -> dict | None:
    """A paid turn becomes a permanent asset: distill what the model said
    into the store the offline stack predicts from. Deduped on topic — the
    same question twice never buys the same knowledge twice."""
    topic = _norm_text(topic)[:120]
    guidance = _norm_text(guidance)
    if not topic or not guidance:
        return None
    conn = db.connect()
    have = conn.execute(
        "SELECT id FROM deposits WHERE user_id=? AND lower(topic)=lower(?)",
        (user_id, topic)).fetchone()
    if have is not None:
        return None
    did = db.new_id("dep")
    conn.execute(
        "INSERT INTO deposits (id, user_id, area, topic, guidance, source,"
        " model, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (did, user_id, area, topic, guidance, source, model, db.utcnow()))
    conn.commit()
    return {"id": did, "topic": topic, "source": source}


def store(user_id: str) -> dict:
    """Everything the offline coach can draw on for this user, with the
    provenance of every entry: the hand-written pack, JIM's learned
    excursions, and the deposits paid model turns left behind."""
    conn = db.connect()
    # On the wire the entry's text is `lesson`, not `guidance` — `guidance`
    # is already an object type on this API (the coach reply), and one wire
    # name carries one type.
    excursions = [
        {"topic": r["topic"], "lesson": _norm_text(r["findings"]),
         "source": "excursion", "model": None}
        for r in conn.execute(
            "SELECT topic, findings FROM excursions WHERE user_id=? AND"
            " learned=1 AND findings != '' ORDER BY created_at, rowid",
            (user_id,)).fetchall()]
    deposits = [
        {"topic": r["topic"], "lesson": r["guidance"], "area": r["area"],
         "source": r["source"], "model": r["model"]}
        for r in conn.execute(
            "SELECT * FROM deposits WHERE user_id=? ORDER BY created_at, rowid",
            (user_id,)).fetchall()]
    return {"pack": len(knowledge.ENTRIES), "excursions": excursions,
            "deposits": deposits}


def _personal_entries(user_id: str) -> list[dict]:
    """Learned + deposited material shaped like pack entries so one
    predictor scores them all. Keywords are the topic's own words."""
    out = []
    s = store(user_id)
    for row in s["excursions"] + s["deposits"]:
        words = [w for w in re.findall(r"[a-z]{4,}", row["topic"].lower())]
        out.append({"topic": row["topic"], "area": row.get("area"),
                    "keywords": words, "guidance": row["lesson"],
                    "references": [f"learned by JIM ({row['source']})"],
                    "personal": True})
    return out


# --------------------------------------------------------------------------- #
# the stack
# --------------------------------------------------------------------------- #

def run(user_id: str, area: str, message: str) -> dict:
    """The add-&-norm stack over the local store and the current readings.
    Returns the predicted text (or None below threshold) and the full
    layer record."""
    layers: list[dict] = []
    context: list[str] = []

    # -- add [user data] -----------------------------------------------------
    raw: list[str] = []
    recent = life.checkins(user_id)[-1:]
    if recent:
        c = recent[0]
        raw.append(f"mood {c['mood']}/5" + (f", energy {c['energy']}/5"
                                            if c["energy"] else ""))
    for g in [g for g in life.goals(user_id) if g["status"] == "active"][:3]:
        raw.append(f"goal ({g['area']}): {g['title']}")
    from . import meds
    raw.extend(meds.coach_context(user_id))
    layers.append({"layer": "add.user_data", "added": len(raw)})
    # -- norm ----------------------------------------------------------------
    normed = [_norm_text(r) for r in raw if _norm_text(r)]
    context.extend(normed)
    layers.append({"layer": "norm.user_data", "kept": len(normed)})

    # -- add [vitals] --------------------------------------------------------
    vitals = []
    for band in bands.overview(user_id):
        if band["baseline"] is not None:
            vitals.append(f"{band['metric']}: baseline {band['baseline']}"
                          + ("" if band["provisional"] else
                             f" (edges {band['low_edge']}–{band['high_edge']})"))
    layers.append({"layer": "add.vitals", "added": len(vitals)})

    # -- add [speech] & [tone] ----------------------------------------------
    from . import coach, guardian, presence
    speech = [f"register: {presence.bearing(user_id)}"]
    tone_pref = ((guardian.get_user(user_id) or {}).get("personality") or
                 {}).get("tone")
    cue = coach.tone_from_prompt(message)
    tone = [t for t in (f"tone: {cue or tone_pref}",) if cue or tone_pref]
    layers.append({"layer": "add.speech", "added": len(speech)})
    layers.append({"layer": "add.tone", "added": len(tone)})

    # -- add [environment] ---------------------------------------------------
    env_rows = db.connect().execute(
        "SELECT data FROM context_events WHERE user_id=? AND kind='environment'"
        " ORDER BY created_at DESC, rowid DESC LIMIT 1", (user_id,)).fetchall()
    environment = []
    for r in env_rows:
        data = json.loads(r["data"])
        if not data.get("vaulted"):
            environment.append(_norm_text(json.dumps(data)))
    layers.append({"layer": "add.environment", "added": len(environment)})

    # -- norm over the signal block ------------------------------------------
    signals = [_norm_text(s) for s in vitals + speech + tone + environment
               if _norm_text(s)]
    context.extend(signals)
    layers.append({"layer": "norm.signals", "kept": len(signals)})

    # -- add the learned layers (the attention the product already computes) -
    from . import adaptation, continuity
    adaptation.ensure_fresh(user_id)
    learned_lines = (adaptation.prompt_lines(user_id)
                     + continuity.attention_lines(user_id))
    layers.append({"layer": "add.learned", "added": len(learned_lines)})
    normed_learned = [_norm_text(x) for x in learned_lines if _norm_text(x)]
    context.extend(normed_learned)
    layers.append({"layer": "norm.learned", "kept": len(normed_learned)})

    # -- predict -------------------------------------------------------------
    # Transparent scoring over the whole store: +2 per keyword hit in the
    # question, +1 for the asked area, +1 more when the entry is personal
    # (JIM learned it for *this* user), and +2 when a drifting-or-known
    # vital names the entry — the readings steer the choice, which is the
    # whole reason they rode along.
    text = (message or "").lower()
    vital_words = " ".join(vitals).lower()
    best, best_score = None, 0
    for entry in knowledge.ENTRIES + _personal_entries(user_id):
        score = sum(2 for k in entry["keywords"] if k in text)
        if area and entry.get("area") == area:
            score += 1
        if entry.get("personal"):
            score += 1
        if any(k in vital_words for k in entry["keywords"]):
            score += 2
        if score > best_score:
            best, best_score = entry, score
    layers.append({"layer": "predict",
                   "chose": best["topic"] if best else None,
                   "score": best_score})
    if best is None or best_score < _THRESHOLD:
        # A miss is a signal, not just a shrug: record the gap so JIM can
        # study exactly what was missing. The need writes the shopping list.
        _record_gap(user_id, area, message)
        layers.append({"layer": "norm.output", "kept": 0})
        return {"text": None, "entry": None, "layers": layers}

    # -- norm the output -----------------------------------------------------
    out = _norm_text(best["guidance"])
    if _DENY.search(out):
        out = None  # the stub's honest fallback beats an unsafe answer
    layers.append({"layer": "norm.output", "kept": 1 if out else 0})
    return {"text": out, "entry": best, "layers": layers}


def _record_gap(user_id: str, area: str, message: str) -> None:
    question = _norm_text(message)[:120]
    if not question:
        return
    conn = db.connect()
    have = conn.execute(
        "SELECT id FROM gaps WHERE user_id=? AND lower(question)=lower(?)",
        (user_id, question)).fetchone()
    if have is not None:
        return
    conn.execute(
        "INSERT INTO gaps (id, user_id, area, question, filled, created_at)"
        " VALUES (?,?,?,?,0,?)",
        (db.new_id("gap"), user_id, area, question, db.utcnow()))
    conn.commit()


# --------------------------------------------------------------------------- #
# the curriculum: what JIM should study next for this coach
# --------------------------------------------------------------------------- #

def curriculum(user_id: str) -> dict:
    """Where this user actually put the AI in their life — the coach's own
    recorded misses first, then metrics with a learned baseline, areas with
    active goals, a stocked med cabinet — minus what the store already
    covers. Each suggestion names the monitor that asked for it, and feeds
    straight into an excursion topic."""
    covered = {e["topic"].lower() for e in knowledge.ENTRIES}
    s = store(user_id)
    covered |= {r["topic"].lower() for r in s["excursions"] + s["deposits"]}

    suggested = []
    # The misses come first: these are questions actually asked, answered
    # by nothing stored. Filling them is the highest-value study there is.
    for gap in db.connect().execute(
            "SELECT * FROM gaps WHERE user_id=? AND filled=0"
            " ORDER BY created_at, rowid", (user_id,)).fetchall():
        if gap["question"].lower() not in covered:
            suggested.append({"area": gap["area"], "topic": gap["question"],
                              "why": "the coach had no stored answer when "
                                     "this was asked"})
    for band in bands.overview(user_id):
        if band["baseline"] is None:
            continue
        topic = f"living well with your {band['metric'].replace('_', ' ')} trend"
        if topic.lower() not in covered:
            suggested.append({"area": "health_fitness", "topic": topic,
                              "why": f"your {band['metric'].replace('_', ' ')} "
                                     "band has a learned baseline"})
    for g in [g for g in life.goals(user_id) if g["status"] == "active"]:
        topic = f"evidence-based help toward: {g['title']}"
        if topic.lower() not in covered:
            suggested.append({"area": g["area"], "topic": topic,
                              "why": f"active goal in {g['area']}"})
    from . import meds
    if meds.coach_context(user_id):
        topic = "staying steady on a medication routine"
        if topic.lower() not in covered:
            suggested.append({"area": "health_fitness", "topic": topic,
                              "why": "medications on the dose board"})
    return {"suggested": suggested[:8],
            "note": "study any of these with an excursion and learn the "
                    "findings — the offline coach reads them from then on"}
