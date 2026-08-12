"""The offline coach stack (jim/pipeline.py): the always-on half of the
product. The coach answers from stored knowledge and current readings
through an add-&-norm stack that never touches the network; JIM's online
moments — excursions, paid model turns — exist to deepen the store that
stack predicts from. Every layer is on the record, every deposit carries
provenance, and the curriculum is read off where the user actually put
the AI in their life.
"""

import pathlib

import pytest

from jim import db, llm, pipeline
from jim.tests.conftest import enroll


def _reply(client, user, message, area="mental_health"):
    return client.post(f"/coach/{user}", json={
        "area": area, "message": message}).json()


def test_the_stack_runs_and_records_every_layer(client):
    user = enroll(client)
    body = _reply(client, user, "I keep having panic attacks and my pulse races")
    assert body["delivered"] is True
    layers = [l["layer"] for l in body["provenance"]["pipeline"]]
    # The diagram's discipline: adds and norms alternate blockwise, the
    # stack begins with the user's own data and ends with a normed output.
    assert layers[0] == "add.user_data" and layers[1] == "norm.user_data"
    assert layers[-2] == "predict" and layers[-1] == "norm.output"
    for name in ("add.vitals", "add.speech", "add.tone", "add.environment",
                 "norm.signals", "add.learned", "norm.learned"):
        assert name in layers, name
    # Each add block is followed (not necessarily adjacently) by a norm.
    assert layers.index("norm.signals") > layers.index("add.environment")
    assert layers.index("norm.learned") > layers.index("add.learned")


def test_the_pipeline_never_imports_the_network():
    """The always-on half is cheap *by construction*: the stack's whole
    world is the local store and the local readings. No provider, no
    socket, no HTTP — held here, on the file's own imports."""
    src = pathlib.Path(pipeline.__file__).read_text()
    for forbidden in ("import llm", "from . import llm", "from .llm",
                      "import urllib", "import http", "import requests",
                      "import socket", "import httpx"):
        assert forbidden not in src, forbidden


def test_a_learned_excursion_reaches_the_offline_answer(client):
    """The note under /excursions/entry/{cid}/learn says the local model
    uses the findings. Until this round nothing read them — the claim now
    has behavior: learned findings enter the store and the stack predicts
    from them."""
    user = enroll(client)
    exc = client.post(f"/excursions/{user}", json={
        "topic": "cold plunge recovery routines",
        "question": "what does the evidence say about cold plunges?",
        "private": []}).json()
    client.post(f"/excursions/entry/{exc['id']}/learn")
    store = client.get(f"/coach/{user}/store").json()
    assert any(e["topic"] == "cold plunge recovery routines"
               for e in store["excursions"])
    body = _reply(client, user,
                  "thinking about cold plunge recovery again",
                  area="health_fitness")
    assert body["delivered"] is True
    prov = body["provenance"]
    assert "offline pipeline" in prov["method"]
    assert any("learned by JIM" in r for r in prov["evidence"])


def test_a_paid_turn_becomes_a_deposit_the_offline_stack_answers_from(client):
    """The economics of the product in one test: a model turn is spent
    once, deposited, and the same ground is offline forever after."""
    user = enroll(client)
    taught = ("Progressive overload with two rest days beats daily "
              "maxing; log every session and add load only when form holds.")

    def fake_model(user_id, system, message, cloud=None):
        return {"text": taught, "provider": "anthropic",
                "degraded": False, "reason": None}

    # A private patch rather than the fixture's monkeypatch: undoing that
    # one would also undo the client fixture's JIM_DB, swapping databases
    # mid-test.
    mp = pytest.MonkeyPatch()
    mp.setattr(llm, "generate_for_user", fake_model)
    paid = _reply(client, user, "how should I structure barbell training",
                  area="health_fitness")
    assert paid["provenance"]["generated_by"] == "anthropic"
    mp.undo()

    store = client.get(f"/coach/{user}/store").json()
    dep = [d for d in store["deposits"] if d["source"] == "coach"]
    assert dep and dep[0]["model"] == "anthropic"
    assert "barbell" in dep[0]["topic"]

    offline = _reply(client, user,
                     "remind me how to structure barbell training",
                     area="health_fitness")
    assert offline["provenance"]["generated_by"] == "stub"
    assert "offline pipeline" in offline["provenance"]["method"]
    assert offline["content"] == pipeline._norm_text(taught)


def test_the_same_question_never_buys_the_same_knowledge_twice(client):
    user = enroll(client)
    first = pipeline.deposit(user, "career", "acing a panel interview",
                             "Research every panelist and prepare one "
                             "question each.", "coach", "anthropic")
    second = pipeline.deposit(user, "career", "acing a panel interview",
                              "Different words, same gap.", "coach",
                              "anthropic")
    assert first is not None and second is None
    rows = db.connect().execute(
        "SELECT COUNT(*) AS n FROM deposits WHERE user_id=?",
        (user,)).fetchone()
    assert rows["n"] == 1


def test_the_curriculum_reads_the_monitored_surface(client):
    """Where the user put the AI is the syllabus: active goals and the
    dose board each ask for study, a topic already learned drops out, and
    every suggestion says which monitor asked for it."""
    user = enroll(client)
    client.post(f"/goals/{user}", json={
        "area": "finance", "title": "save a three-month emergency fund"})
    cur = client.get(f"/coach/{user}/curriculum").json()
    topics = {s["topic"] for s in cur["suggested"]}
    goal_topic = "evidence-based help toward: save a three-month emergency fund"
    assert goal_topic in topics
    assert any("active goal in finance" in s["why"] for s in cur["suggested"])

    # Study it, learn it, and the curriculum stops asking.
    exc = client.post(f"/excursions/{user}", json={
        "topic": goal_topic, "question": "how do people actually do this?",
        "private": []}).json()
    client.post(f"/excursions/entry/{exc['id']}/learn")
    cur2 = client.get(f"/coach/{user}/curriculum").json()
    assert goal_topic not in {s["topic"] for s in cur2["suggested"]}


def test_a_miss_becomes_a_gap_and_one_press_of_study_fills_it(client):
    """JIM imports knowledge as the coach needs it: a question nothing
    stored could answer is recorded as a gap, the gap heads the
    curriculum, and one press of study learns it into the store and
    closes it."""
    user = enroll(client)
    body = _reply(client, user, "how do I winterize a backyard beehive",
                  area="personal_growth")
    assert body["delivered"] is True     # the stub's honest text still shows
    cur = client.get(f"/coach/{user}/curriculum").json()
    assert cur["suggested"], "the miss should have entered the curriculum"
    top = cur["suggested"][0]
    assert "beehive" in top["topic"]
    assert "no stored answer" in top["why"]

    studied = client.post(f"/coach/{user}/study", json={}).json()
    assert studied["folded"] is True
    assert "beehive" in studied["studied"]

    cur2 = client.get(f"/coach/{user}/curriculum").json()
    assert not any("beehive" in s["topic"] for s in cur2["suggested"])
    store = client.get(f"/coach/{user}/store").json()
    assert any("beehive" in e["topic"] for e in store["excursions"])
