"""`adaptation.py` said "this is not a weight file". Now one is.

The sibling module builds a per-user profile and is scrupulous about what it
isn't:

    **This is not a weight file.** The transformer stays the vendor's. What JIM
    owns is the state that conditions it, and the profile says so in its own
    ``method`` field rather than letting a reader assume a fine-tune happened.

That was true and it was the right position to hold until it was overruled.
`jim/finetune.py` is the other thing: an offline pass that reads this user's
own answered follow-ups and **trains weights** by gradient descent, on this
machine, with the network blocked.

## Why the tests here are mostly about learning rather than running

A training function that runs, writes a file and reports success is the easiest
thing in this round to fake and the hardest to notice being fake. Weights of
all zeros serialise fine. A loss that never moved serialises fine. So the
central test below does not check that training *happened* — it checks that the
model **learned something a lookup could not have guessed**, by training it on
a corpus with a deliberate signal and asserting the weights recovered it.

## What is deliberately not claimed

Not a transformer fine-tune. The `lora` backend is wired to `transformers`,
`peft` and `torch` and raises when they are absent — and raises again, on
purpose, when they are present but no pass has ever been watched to completion
on this deployment. A training path that reports success without anybody having
seen it work is worse than one that refuses, and the refusal says so in the
message rather than in a comment nobody reads.
"""

import json
import uuid

import pytest

from jim import db, finetune
from jim.tests.conftest import enroll


def _followups(user_id, rows):
    """Write answered follow-ups directly.

    Through the table rather than through the ask/answer routes because the
    corpus is what the trainer reads, and a test that could not place a
    specific signal in it could not check that the signal was learned.
    """
    conn = db.connect()
    for i, (condition, severity, helped) in enumerate(rows):
        conn.execute(
            "INSERT INTO guidance_followups (id, user_id, condition, severity,"
            " asked_at, answered_at, helped) VALUES (?,?,?,?,?,?,?)",
            (f"fu-{uuid.uuid4().hex[:12]}-{i}", user_id, condition, severity,
             db.utcnow(), db.utcnow(), helped))
    conn.commit()


def _split_corpus(user_id, n=8):
    """A corpus with a signal a lookup cannot fake: guidance for `sleep`
    almost always helps, guidance for `stress` almost never does."""
    rows = [("sleep", "mild", 1) for _ in range(n)]
    rows += [("stress", "mild", 0) for _ in range(n)]
    _followups(user_id, rows)


# --- it refuses before it guesses -------------------------------------------

def test_too_little_history_is_a_refusal_not_a_low_confidence_model(client):
    """A model built from four examples is a coincidence with a version
    number, and attaching `confidence: 0.2` to it does not make it less of
    one."""
    user = enroll(client)
    _followups(user, [("sleep", "mild", 1)] * 4)
    with pytest.raises(finetune.TrainingRefused) as exc:
        finetune.train(user)
    assert "floor" in str(exc.value)
    assert exc.value.examples == 4


def test_unanswered_followups_are_not_negative_examples(client):
    """A person who was busy is not a person who said no. Training on silence
    as dissatisfaction is how a model learns to go quiet at exactly the people
    who need it not to."""
    user = enroll(client)
    conn = db.connect()
    for i in range(20):
        conn.execute(
            "INSERT INTO guidance_followups (id, user_id, condition, severity,"
            " asked_at, helped) VALUES (?,?,?,?,?,NULL)",
            (f"quiet-{i}", user, "sleep", "mild", db.utcnow()))
    conn.commit()
    assert finetune.corpus(user) == []


# --- it actually learns -----------------------------------------------------

def test_the_weights_recover_a_signal_a_lookup_could_not_have_guessed(client):
    """The test this module lives or dies by.

    Weights of all zeros serialise as happily as trained ones, and a loss that
    never moved reports success just as well. So: train on a corpus where
    `sleep` helps and `stress` does not, then ask the model. It has to separate
    them, and the separation has to be large.
    """
    user = enroll(client)
    _split_corpus(user)
    art = finetune.train(user)
    finetune.activate(user, True)

    good = finetune.predict(user, "sleep", "mild")
    bad = finetune.predict(user, "stress", "mild")
    assert good["likely_to_help"] > 0.8, good
    assert bad["likely_to_help"] < 0.2, bad
    assert good["likely_to_help"] - bad["likely_to_help"] > 0.6

    # And the optimiser moved: a run that returned its starting point would
    # pass a weaker version of the assertions above by accident.
    assert art["final_loss"] < art["first_loss"] / 2, art


def test_a_condition_never_seen_is_reported_as_never_seen(client):
    """The model answers with the base rate for anything outside its
    vocabulary, and says that is what it did. Silently treating an unknown
    condition as an ordinary prediction is how a confident number gets
    attached to no evidence at all."""
    user = enroll(client)
    _split_corpus(user)
    finetune.train(user)
    finetune.activate(user, True)
    out = finetune.predict(user, "a-condition-nobody-logged", "mild")
    assert out["seen_before"] is False, out


# --- nothing leaves ---------------------------------------------------------

def test_training_runs_with_the_network_blocked(client, monkeypatch):
    """Not a comment claiming the pass is offline — the thing that makes it
    true. A backend reaching for a model hub raises rather than uploading
    somebody's health history."""
    user = enroll(client)
    _split_corpus(user)

    reached = []

    def greedy(rows):
        import urllib.request
        try:
            urllib.request.urlopen("https://example.invalid/model")
        except Exception as exc:      # what a real hub client would do
            reached.append(str(exc))
            raise
        return {"backend": "greedy", "vocab": {}, "weights": [0.0],
                "epochs": 0, "final_loss": 0.0, "first_loss": 0.0}

    monkeypatch.setitem(finetune.BACKENDS, "greedy", greedy)
    with pytest.raises(finetune.TrainingRefused):
        finetune.train(user, backend="greedy")
    assert reached and "example.invalid" in reached[0]


def test_the_block_is_lifted_afterwards(client):
    """A guard that leaked would break every other outbound call in the
    product, and would do it silently in whichever test ran next."""
    import urllib.request
    before = urllib.request.urlopen
    user = enroll(client)
    _split_corpus(user)
    finetune.train(user)
    assert urllib.request.urlopen is before


# --- the artifact says what it is -------------------------------------------

def test_the_artifact_names_its_backend_and_its_evidence(client):
    """A reader must never have to infer whether weights or a prompt came out
    of this — `adaptation.py` next door produces the other one and says the
    opposite about itself."""
    user = enroll(client)
    _split_corpus(user)
    art = finetune.train(user)
    assert art["backend"] == "local-logistic"
    assert art["examples"] == 16
    assert "trained offline on this machine" in art["method"]
    assert "16" in art["method"]
    assert art["digest"]


def test_the_digest_covers_the_weights(client):
    """A digest that did not change when the weights did would be a checksum
    of the paperwork."""
    user = enroll(client)
    _split_corpus(user)
    first = finetune.train(user)
    _followups(user, [("stress", "severe", 1)] * 6)
    second = finetune.train(user)
    assert second["weights"] != first["weights"]
    assert second["digest"] != first["digest"]


# --- training and using are two decisions -----------------------------------

def test_a_trained_model_is_not_used_until_it_is_switched_on(client):
    """Collapsing the two is how somebody ends up answered by a model they
    never agreed to be answered by."""
    user = enroll(client)
    _split_corpus(user)
    finetune.train(user)
    assert finetune.predict(user, "sleep", "mild") is None
    finetune.activate(user, True)
    assert finetune.predict(user, "sleep", "mild") is not None


def test_switching_it_off_restores_the_behaviour_that_predates_it(client):
    """Off is always available and the base behaviour is one switch away.
    `predict` returning None is what makes turning it off safe: the caller
    then does exactly what it did before this module existed."""
    user = enroll(client)
    _split_corpus(user)
    finetune.train(user)
    finetune.activate(user, True)
    assert finetune.predict(user, "sleep", "mild") is not None
    finetune.activate(user, False)
    assert finetune.predict(user, "sleep", "mild") is None


def test_the_switch_has_no_default(client):
    """An empty PUT is not a consent — for a model that answers somebody about
    their health."""
    user = enroll(client)
    assert client.put(f"/finetune/{user}/active", json={}).status_code == 422


# --- the lora backend refuses honestly --------------------------------------

def test_the_lora_backend_refuses_rather_than_falling_back(client):
    """The failure this module exists to make impossible.

    A backend that quietly trained something else and reported success is how
    somebody ends up believing they have a fine-tuned transformer when they
    have a logistic regression. It raises, and the message says what to do.
    """
    user = enroll(client)
    _split_corpus(user)
    with pytest.raises(finetune.TrainingRefused) as exc:
        finetune.train(user, backend="lora")
    said = str(exc.value)
    assert "JIM_FINETUNE_BASE" in said or "libraries" in said, said
    # And nothing was written: a refused run must not leave an artifact
    # somebody could mistake for a trained one.
    assert finetune.latest(user) is None


def test_an_unknown_backend_is_refused(client):
    user = enroll(client)
    _split_corpus(user)
    with pytest.raises(finetune.TrainingRefused):
        finetune.train(user, backend="whatever-is-fashionable")


# --- driven through the routes ----------------------------------------------

def test_the_whole_flow_through_its_own_doors(client):
    user = enroll(client)
    _split_corpus(user)

    r = client.post(f"/finetune/{user}")
    assert r.status_code == 200, r.text
    assert r.json()["backend"] == "local-logistic"

    got = client.get(f"/finetune/{user}")
    assert got.status_code == 200, got.text
    assert got.json()["active"] is False, "trained models start switched off"
    assert got.json()["weights"], "the artifact is readable, weights and all"

    on = client.put(f"/finetune/{user}/active", json={"active": True})
    assert on.status_code == 200, on.text
    assert client.get(f"/finetune/{user}").json()["active"] is True


def test_reading_before_training_is_a_404_not_an_empty_model(client):
    user = enroll(client)
    assert client.get(f"/finetune/{user}").status_code == 404


def test_the_artifact_is_stored_where_the_profile_is_not(client):
    """Two tables on purpose. One holds a profile that conditions a prompt,
    the other holds weights, and a single table with a `kind` column would
    have invited exactly the confusion this module is written to prevent."""
    user = enroll(client)
    _split_corpus(user)
    finetune.train(user)
    row = db.connect().execute(
        "SELECT backend, examples FROM user_finetunes WHERE user_id=?",
        (user,)).fetchone()
    assert row["backend"] == "local-logistic" and row["examples"] == 16
    stored = json.loads(db.connect().execute(
        "SELECT artifact FROM user_finetunes WHERE user_id=?",
        (user,)).fetchone()["artifact"])
    assert stored["weights"]
