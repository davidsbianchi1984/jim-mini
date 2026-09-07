"""The condition network (claims 22 and 26): attention layers over the
reading history, conditioned by the known condition, the trust in each
reading and the degree of engagement; trained offline on encrypted weights;
run on the coach, the companion check-in and the engaged session.

    asked     condition the inference using attention layers based on the
              degree of engagement; fine-tune offline, encrypted
    mattered  the attention is JIM's own and gradient-checked here, its
              conditioning is a printed number on every turn, the row it
              leaves carries no health values, and the training runs with
              the network blocked
"""

from __future__ import annotations

import numpy as np
import pytest

from jim import condition_net as cn, db, engaged
from jim.tests.conftest import enroll

READINGS = [
    {"heart_rate": 62, "hrv": 55, "signal_confidence": 1.0},
    {"heart_rate": 71, "hrv": 40, "stress_level": 0.3, "signal_confidence": 0.9},
    {"heart_rate": 118, "hrv": 18, "stress_level": 0.8, "note": "chest tight",
     "signal_quality": 0.4, "signal_confidence": 0.45,
     "signal_grade": "suspect"},
    {"heart_rate": 66, "hrv": 50, "signal_confidence": 1.0},
    {"heart_rate": 64, "signal_confidence": 1.0},
    {"heart_rate": 90, "respiratory_rate": 22, "stress_level": 0.6,
     "signal_confidence": 1.0},
]


def _forward(p, details, known=(), sensitivity="balanced", trust=None, tau=None):
    trust = np.array([cn.trust_of(d) for d in details]) if trust is None else trust
    tau = tau or cn.temperature(sensitivity, details[-1].get("stress_level") or 0)
    return cn.forward(p, cn.features(details, 60), cn.context(list(known), sensitivity),
                      trust, tau)


# -- the network itself -------------------------------------------------------

def test_every_gradient_matches_finite_differences():
    p = cn.init_params(5)
    details = READINGS[:5]
    t_dev, t_emph = 0.62, np.array([0.0, 1.0, 0.0, 1.0])
    g = cn.backward(p, _forward(p, details, known=["anxiety"]), t_dev, t_emph)

    def loss():
        return cn.loss_of(_forward(p, details, known=["anxiety"]), t_dev, t_emph)

    h = 1e-6
    for name in p:
        flat = p[name].reshape(-1)
        for idx in range(0, flat.size, max(1, flat.size // 24)):
            old = flat[idx]
            flat[idx] = old + h
            up = loss()
            flat[idx] = old - h
            down = loss()
            flat[idx] = old
            numeric, analytic = (up - down) / (2 * h), g[name].reshape(-1)[idx]
            assert abs(numeric - analytic) <= 1e-6 + 1e-4 * abs(numeric), (
                name, idx, numeric, analytic)


def test_attention_is_conditioned_by_trust_condition_and_engagement():
    p = cn.init_params(5)
    details = READINGS[:5]
    base = _forward(p, details)["layers"][-1]["A"][:, -1, :]

    # A reading the wearable took badly draws less of the row.
    trust = np.array([cn.trust_of(d) for d in details])
    doubted = trust.copy()
    doubted[1] = 0.15
    shifted = _forward(p, details, trust=doubted)["layers"][-1]["A"][:, -1, :]
    assert not np.allclose(base, shifted)
    assert shifted[:, 1].mean() < base[:, 1].mean()

    # The declared condition rides every position and moves the attention.
    with_condition = _forward(p, details, known=["anxiety"])["layers"][-1]["A"][:, -1, :]
    assert not np.allclose(base, with_condition)

    # The dial and the current state set the temperature: a cautious dial
    # under stress looks sharply, an assertive calm one looks wide.
    assert cn.temperature("cautious", 0.9) < cn.temperature("balanced", 0.0) \
        < cn.temperature("assertive", 0.0)
    sharp = _forward(p, details, tau=cn.temperature("cautious", 0.9))
    wide = _forward(p, details, tau=cn.temperature("assertive", 0.0))
    assert (sharp["layers"][-1]["A"][:, -1, :].max(axis=1).mean()
            > wide["layers"][-1]["A"][:, -1, :].max(axis=1).mean())


def test_the_weights_are_ciphertext_and_bound_to_their_user(monkeypatch, tmp_path):
    monkeypatch.setenv("JIM_DB", str(tmp_path / "w.db"))
    p = cn.init_params(1)
    blob = cn.seal("usr_a", p)
    assert b'"names"' not in blob and b"W_in" not in blob
    back = cn.unseal("usr_a", blob)
    assert all(np.array_equal(p[k], back[k]) for k in p)
    from cryptography.exceptions import InvalidTag
    with pytest.raises(InvalidTag):
        cn.unseal("usr_b", blob)
    monkeypatch.setenv("JIM_MODEL_KEY", "another install")
    with pytest.raises(InvalidTag):
        cn.unseal("usr_a", blob)


# -- on the product's doors ---------------------------------------------------

def _read(client, user, n):
    for i in range(n):
        sample = {k: v for k, v in READINGS[i % len(READINGS)].items()
                  if k not in ("signal_confidence", "signal_grade")}
        r = client.post(f"/monitor/{user}", json=sample)
        assert r.status_code == 200, r.text


def test_a_coach_turn_is_conditioned_and_the_record_carries_no_values(client):
    user = enroll(client, known_conditions=["anxiety"])
    _read(client, user, 3)
    r = client.post(f"/coach/{user}", json={"area": "general",
                                            "message": "how am I doing?"})
    assert r.status_code == 200, r.text
    status = client.get(f"/condition-net/{user}").json()
    assert status["trained"] is False and status["weights_build"] == 0
    assert status["encrypted_at_rest"] is True
    rows = [x for x in status["recent_conditioning"] if x["surface"] == "coach"]
    assert rows, status["recent_conditioning"]
    row = rows[0]
    assert len(row["attention"]) == 3
    # Indices, weights, trust and times only — never a reading's value.
    assert {k for a in row["attention"] for k in a} == {"reading", "weight",
                                                         "trust", "read_at"}
    assert set(row["emphases"]) == set(cn.EMPHASES)
    # The third reading arrived suspect; it is trusted less than the first.
    assert row["attention"][2]["trust"] < row["attention"][0]["trust"]


def test_the_prompt_line_names_the_condition_the_dial_and_the_state(client):
    user = enroll(client, known_conditions=["anxiety"])
    assert client.put(f"/sensitivity/{user}",
                      json={"level": "cautious"}).status_code == 200
    _read(client, user, 3)
    (line,) = cn.prompt_lines(user, "coach")
    assert "Condition-conditioned attention" in line
    assert "cautious dial" in line and "1 declared condition" in line
    assert "attends most to" in line and "Emphases for this reply" in line
    assert "every safety path stay exactly as they are" in line


def test_the_engaged_session_is_conditioned_under_its_own_surface(client):
    user = enroll(client)
    _read(client, user, 2)
    assert client.post(f"/engaged/{user}",
                       json={"area": "personal_growth"}).status_code == 201
    r = client.post(f"/engaged/{user}/turn", json={"message": "hello there"})
    assert r.status_code == 200, r.text
    surfaces = [x["surface"] for x in cn.conditioning_of(user)]
    assert "engaged" in surfaces


def test_nothing_is_said_before_the_first_reading(client):
    user = enroll(client)
    assert cn.prompt_lines(user, "coach") == []
    assert client.get(f"/condition-net/{user}").json()["recent_conditioning"] == []


# -- training (claim 26) -----------------------------------------------------

def test_training_fits_the_weights_here_and_seals_them(client, monkeypatch):
    user = enroll(client, known_conditions=["anxiety"])
    _read(client, user, 6)
    before = cn.load(user)[0]

    r = client.post(f"/condition-net/{user}/train")
    assert r.status_code == 201, r.text
    net = r.json()
    assert net["trained"] is True and net["samples"] == 5 and net["training_steps"] > 0
    assert net["loss_after"] < net["loss_before"]
    assert net["external_transmission"] is False and net["weights_build"] == 1

    after, version = cn.load(user)
    assert version == 1
    assert any(not np.array_equal(before[k], after[k]) for k in before)
    blob = db.connect().execute(
        "SELECT blob FROM condition_weights WHERE user_id=?",
        (user,)).fetchone()["blob"]
    assert b'"names"' not in bytes(blob)

    # The next turn is conditioned by the trained weights, and says so.
    client.post(f"/coach/{user}", json={"area": "general", "message": "and now?"})
    status = client.get(f"/condition-net/{user}").json()
    assert status["trained"] is True
    assert status["recent_conditioning"][0]["weights_version"] == 1
    assert client.post(f"/condition-net/{user}/train").json()["weights_build"] == 2


def test_training_refuses_to_reach_the_network(client, monkeypatch):
    """The pass runs under finetune's block: a backend that phoned home
    would raise rather than upload, so a model call inside it is refused."""
    import urllib.request
    user = enroll(client)
    _read(client, user, 3)
    seen = {}

    def spying_mean_loss(p, samples):
        try:
            urllib.request.urlopen("https://example.invalid/weights")
        except Exception as exc:  # noqa: BLE001
            seen["refused"] = type(exc).__name__
        return 0.5

    monkeypatch.setattr(cn, "_mean_loss", spying_mean_loss)
    cn.train(user)
    assert seen["refused"] == "TrainingRefused"
    assert urllib.request.urlopen.__name__ != "blocked"   # restored after


def test_ingest_trains_on_its_own_every_sixteenth_reading(client):
    user = enroll(client)
    _read(client, user, 15)
    assert client.get(f"/condition-net/{user}").json()["trained"] is False
    _read(client, user, 1)
    status = client.get(f"/condition-net/{user}").json()
    assert status["trained"] is True and status["trained_on"] == 15


def test_training_before_two_readings_says_why(client):
    user = enroll(client)
    _read(client, user, 1)
    net = client.post(f"/condition-net/{user}/train").json()
    assert net["trained"] is False and net["training_steps"] == 0
    assert "two readings" in net["reason"]


def test_erasing_the_person_takes_the_weights_and_the_record(client):
    user = enroll(client)
    _read(client, user, 3)
    client.post(f"/condition-net/{user}/train")
    client.post(f"/coach/{user}", json={"area": "general", "message": "hi"})
    conn = db.connect()
    for table in ("condition_weights", "condition_conditioning"):
        assert conn.execute(f"SELECT COUNT(*) FROM {table} WHERE user_id=?",
                            (user,)).fetchone()[0] >= 1
    r = client.delete(f"/data/{user}")
    assert r.status_code in (200, 204), r.text
    for table in ("condition_weights", "condition_conditioning"):
        assert conn.execute(f"SELECT COUNT(*) FROM {table} WHERE user_id=?",
                            (user,)).fetchone()[0] == 0


def test_the_engaged_module_exposes_the_turn_it_conditions():
    """`engaged.converse` is the agent's one speaking path; the line is
    appended there and nowhere else, so a second agent surface would have
    to go through it."""
    import inspect
    assert "condition_net.prompt_lines(user_id, \"engaged\")" in inspect.getsource(
        engaged.converse)
