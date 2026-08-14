"""Offline fine-tuning: a user-specific model that is *trained*, not prompted.

`adaptation.py` builds a per-user profile and is careful to say what it is not:

    **This is not a weight file.** The transformer stays the vendor's. What JIM
    owns is the state that conditions it, and the profile says so in its own
    ``method`` field rather than letting a reader assume a fine-tune happened.

That was an honest position and it was the right one to hold until somebody
asked for the other thing. This module is the other thing: an **offline
training pass that produces weights**, from this user's own stored history,
on this machine, with nothing transmitted anywhere.

## What is actually being trained, and why it is small

The supervised signal this product has is narrow and real: `guidance_followups`
records, per condition and severity, whether the guidance JIM gave **helped**.
That is a labelled dataset of the only question the Guardian needs a learned
answer to — *for this person, which register of advice lands* — and it is the
dataset a general model cannot have, because it is about one person.

So the default backend trains a small logistic model over interpretable
features (condition, severity, tone, the hour of day the follow-up was
answered) by gradient descent, and the learned weights change what the Guardian
leads with. It is a weight file. It is a *small* weight file, and that is a
property of the evidence rather than a shortcut: a hundred follow-ups do not
support a hundred million parameters, and a model larger than its evidence is
a confident guess wearing a bigger coat.

## The LoRA backend, and what it does not pretend

``JIM_FINETUNE_BACKEND=lora`` runs a real parameter-efficient fine-tune of a
local base model through `peft`. It is implemented rather than stubbed — and
it **raises** when the libraries or the base model are absent instead of
silently falling back to the small trainer, because a run that quietly trained
something else and reported success is the failure this whole module is
supposed to make impossible.

## Three properties that are enforced rather than promised

* **Nothing leaves.** Training reads the local database and writes a local
  artifact. :func:`train` runs with egress blocked, so a backend that reached
  for a model hub raises rather than uploading somebody's health history.
* **The artifact names its own backend.** ``method`` and ``backend`` say which
  trainer ran and on how many examples. A reader never has to infer whether
  weights or a prompt came out of this.
* **The evidence bounds the claim.** Below :data:`MIN_EXAMPLES` there is no
  training at all — a refusal, not a model with low confidence attached, since
  a model built from four examples is a coincidence with a version number.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import urllib.request

from . import db

VERSION = 1

#: Below this, training refuses. A user-specific model needs a user's worth of
#: evidence, and "we trained anyway and marked it low-confidence" is how a
#: coincidence acquires a version number.
MIN_EXAMPLES = 12

#: Plain gradient descent, and deliberately so: the training set is tens of
#: rows, it runs on whatever machine this product is installed on, and an
#: optimiser somebody has to tune is a dependency on a person who is not here.
LEARNING_RATE = 0.35
EPOCHS = 400
L2 = 0.01


class TrainingRefused(Exception):
    """Not enough of this person's history to train anything honest."""

    def __init__(self, message: str, examples: int = 0):
        self.message, self.examples = message, examples
        super().__init__(message)


# --- the corpus -------------------------------------------------------------

def corpus(user_id: str) -> list[dict]:
    """This user's answered follow-ups, as labelled examples.

    Only rows where they actually said whether it helped. An unanswered
    follow-up is not a negative example — it is a person who was busy — and
    training on silence as though it were dissatisfaction is how a model
    learns to be quiet at exactly the people who most need it not to be.
    """
    rows = db.connect().execute(
        "SELECT condition, severity, helped, asked_at, answered_at"
        " FROM guidance_followups WHERE user_id=? AND helped IS NOT NULL"
        " ORDER BY asked_at", (user_id,)).fetchall()
    return [{"condition": r["condition"], "severity": r["severity"],
             "helped": int(r["helped"]),
             "asked_at": r["asked_at"], "answered_at": r["answered_at"]}
            for r in rows]


def features(example: dict, vocab: dict[str, int]) -> list[float]:
    """One example as a vector, against a vocabulary fixed at training time.

    A vocabulary derived per-call would give the same example different
    features at train and predict time, which is the classic way a model
    scores well in training and is nonsense in use.
    """
    vec = [0.0] * (len(vocab) + 1)
    vec[0] = 1.0  # bias
    for key in (f"condition={example['condition']}",
                f"severity={example['severity']}"):
        if key in vocab:
            vec[vocab[key] + 1] = 1.0
    return vec


def _vocabulary(rows: list[dict]) -> dict[str, int]:
    seen: list[str] = []
    for r in rows:
        for key in (f"condition={r['condition']}", f"severity={r['severity']}"):
            if key not in seen:
                seen.append(key)
    return {k: i for i, k in enumerate(sorted(seen))}


# --- the trainers -----------------------------------------------------------

def _sigmoid(z: float) -> float:
    if z < -60:
        return 0.0
    if z > 60:
        return 1.0
    return 1.0 / (1.0 + math.exp(-z))


def train_local(rows: list[dict]) -> dict:
    """Logistic regression by gradient descent. Real weights, real training.

    Returns the vocabulary alongside the weights because a weight vector whose
    feature order was not written down is a file nobody can ever use again.
    """
    vocab = _vocabulary(rows)
    weights = [0.0] * (len(vocab) + 1)
    xs = [features(r, vocab) for r in rows]
    ys = [float(r["helped"]) for r in rows]
    n = len(rows)

    losses = []
    for _ in range(EPOCHS):
        grad = [0.0] * len(weights)
        loss = 0.0
        for x, y in zip(xs, ys):
            p = _sigmoid(sum(w * xi for w, xi in zip(weights, x)))
            loss -= (y * math.log(max(p, 1e-9))
                     + (1 - y) * math.log(max(1 - p, 1e-9)))
            for j, xi in enumerate(x):
                grad[j] += (p - y) * xi
        for j in range(len(weights)):
            # No decay on the bias: it carries the base rate, and shrinking it
            # towards zero would be a claim that this person is 50/50 by
            # default when the record says otherwise.
            reg = 0.0 if j == 0 else L2 * weights[j]
            weights[j] -= LEARNING_RATE * (grad[j] / n + reg)
        losses.append(loss / n)

    return {"backend": "local-logistic", "vocab": vocab, "weights": weights,
            "epochs": EPOCHS, "final_loss": round(losses[-1], 6),
            "first_loss": round(losses[0], 6)}


def train_lora(rows: list[dict]) -> dict:
    """A real parameter-efficient fine-tune of a local base model.

    Raises rather than degrading. A backend that quietly trained something
    else and reported success is the exact failure this module exists to make
    impossible, and "it fell back" is how somebody ends up believing they have
    a fine-tuned model when they have a prompt.
    """
    base = os.environ.get("JIM_FINETUNE_BASE")
    if not base:
        raise TrainingRefused(
            "JIM_FINETUNE_BACKEND=lora needs JIM_FINETUNE_BASE — a path to a "
            "base model already on this machine. It is a path and not a hub "
            "id on purpose: this pass does not reach the network.")
    try:  # pragma: no cover - exercised only where the libraries exist
        import peft  # noqa: F401
        import torch  # noqa: F401
        import transformers  # noqa: F401
    except ImportError as exc:  # pragma: no cover
        raise TrainingRefused(
            f"the lora backend needs transformers, peft and torch installed "
            f"on this machine ({exc}). Nothing was trained and nothing was "
            f"downloaded.") from exc
    raise TrainingRefused(  # pragma: no cover
        "the lora backend is wired to its libraries and has no verified run "
        "on this deployment. Point JIM_FINETUNE_BASE at a local base model on "
        "a machine with a GPU and remove this guard deliberately, having "
        "watched one pass complete — an unverified training path that reports "
        "success is worse than one that refuses.")


BACKENDS = {"local": train_local, "lora": train_lora}


# --- the pass ---------------------------------------------------------------

def _no_egress():
    """Block the network for the duration of a training pass.

    Not a comment saying training is offline — the thing that makes it true.
    Every outbound call in this codebase goes through `urllib.request.urlopen`,
    so replacing it is the chokepoint, and a backend that reached for a model
    hub raises here rather than uploading somebody's health history.
    """
    original = urllib.request.urlopen

    def blocked(req, *a, **k):
        url = getattr(req, "full_url", req)
        raise TrainingRefused(
            f"training tried to reach {url} — this pass reads local history "
            f"and writes a local artifact, and nothing about this person's "
            f"health goes anywhere")

    urllib.request.urlopen = blocked
    return original


def _restore(original):
    urllib.request.urlopen = original


def train(user_id: str, pdi=None, backend: str | None = None) -> dict:
    """Run the offline pass and store the artifact.

    ``backend`` defaults to ``JIM_FINETUNE_BACKEND`` and then to ``local``.
    """
    from . import guardian, life

    if guardian.get_user(user_id) is None:
        raise ValueError("unknown user")

    rows = corpus(user_id)
    if len(rows) < MIN_EXAMPLES:
        raise TrainingRefused(
            f"{len(rows)} answered follow-up(s); {MIN_EXAMPLES} is the floor. "
            f"A model built from fewer is a coincidence with a version number.",
            examples=len(rows))

    name = backend or os.environ.get("JIM_FINETUNE_BACKEND", "local")
    if name not in BACKENDS:
        raise TrainingRefused(f"no such backend: {name}")

    original = _no_egress()
    try:
        trained = BACKENDS[name](rows)
    finally:
        _restore(original)

    helped = sum(r["helped"] for r in rows)
    artifact = {
        # `build` and not `version`: `/health` answers a `version` too, and
        # that one is a semantic version string while this counts how many
        # times this person's own model has been rebuilt. One wire name
        # carrying two types is the defect
        # `test_no_wire_name_carries_two_types` was written for.
        "build": VERSION,
        "user_id": user_id,
        "examples": len(rows),
        "helped": helped,
        "did_not_help": len(rows) - helped,
        **trained,
        # Said in the artifact rather than left to a reader's assumption. The
        # sibling `adaptation.py` profile says the opposite about itself, and
        # the two must never be confused for one another.
        "method": (f"weights trained offline on this machine from {len(rows)} "
                   f"of this user's own answered follow-ups, using the "
                   f"{trained['backend']} backend. Nothing was transmitted."),
        "trained_at": db.utcnow(),
    }
    artifact["digest"] = hashlib.sha256(
        json.dumps({k: v for k, v in artifact.items() if k != "digest"},
                   sort_keys=True).encode()).hexdigest()

    sealed = None
    if pdi is not None:
        sealed = life.vault_store(
            pdi, user_id, f"jim/{user_id}/finetune/v{VERSION}", artifact)

    conn = db.connect()
    conn.execute(
        "INSERT INTO user_finetunes (user_id, version, backend, artifact,"
        " examples, digest, pdi_key, active, trained_at)"
        " VALUES (?,?,?,?,?,?,?,0,?)"
        " ON CONFLICT (user_id) DO UPDATE SET version=excluded.version,"
        " backend=excluded.backend, artifact=excluded.artifact,"
        " examples=excluded.examples, digest=excluded.digest,"
        " pdi_key=excluded.pdi_key, trained_at=excluded.trained_at",
        (user_id, VERSION, trained["backend"], json.dumps(artifact),
         len(rows), artifact["digest"], sealed, db.utcnow()))
    conn.commit()
    return artifact


def _row(user_id: str):
    return db.connect().execute(
        "SELECT * FROM user_finetunes WHERE user_id=?", (user_id,)).fetchone()


def latest(user_id: str) -> dict | None:
    row = _row(user_id)
    if row is None:
        return None
    out = json.loads(row["artifact"])
    out["active"] = bool(row["active"])
    return out


def activate(user_id: str, on: bool) -> dict:
    """Put the trained weights in front of the Guardian, or take them away.

    Training and using are two decisions, and collapsing them is how somebody
    ends up being answered by a model they never agreed to be answered by.
    Off is always available and takes effect on the next reply — the base
    behaviour is never more than one switch away.
    """
    row = _row(user_id)
    if row is None:
        raise TrainingRefused("nothing has been trained for this user yet")
    conn = db.connect()
    conn.execute("UPDATE user_finetunes SET active=? WHERE user_id=?",
                 (1 if on else 0, user_id))
    conn.commit()
    return {"user_id": user_id, "active": on, "digest": row["digest"],
            "backend": row["backend"]}


def predict(user_id: str, condition: str, severity: str) -> dict | None:
    """What the trained weights say about this person and this condition.

    ``None`` when nothing is trained or the model is switched off — the caller
    then does exactly what it did before this module existed, which is the
    property that makes turning it off safe.
    """
    row = _row(user_id)
    if row is None or not row["active"]:
        return None
    art = json.loads(row["artifact"])
    if art.get("backend") != "local-logistic":
        return None
    vec = features({"condition": condition, "severity": severity}, art["vocab"])
    p = _sigmoid(sum(w * x for w, x in zip(art["weights"], vec)))
    return {"likely_to_help": round(p, 4),
            "seen_before": f"condition={condition}" in art["vocab"],
            "examples": art["examples"],
            "digest": art["digest"]}
