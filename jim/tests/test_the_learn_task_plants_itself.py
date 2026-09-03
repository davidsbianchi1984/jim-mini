"""The learn task plants itself.

PDI 3.0.1 gave the resident `corpus.learn`: index a tandem's sealed
training bundles so grounded answers stand on them. It waited on
somebody planting the task by hand. Now the person's own switch does it:

* turning capture **on** plants a standing `corpus.learn` task in the
  vault, scoped to this person's bundles (`jim/{user}/corpus/`) and
  nothing else, every day;
* turning capture **off** takes the task back — the row lets go only
  after the vault did;
* the bank **archives itself** every `ARCHIVE_EVERY` examples once a
  vault is there, so the task always has bundles to learn from, and the
  first archive plants the task for a person who never touched the
  switch (capture is on by default);
* the posture says what stands, or why nothing does — no vault, an older
  tandem, an unreached one — in words.
"""

from __future__ import annotations

from jim import corpus, db

from .conftest import enroll
from .test_the_lookout import BrokenVault, OlderVault, StandingVault


def _actions(uid):
    return [r["action"] for r in db.connect().execute(
        "SELECT action FROM audit WHERE user_id=? ORDER BY seq", (uid,)).fetchall()]


def _bank(uid, n):
    for i in range(n):
        corpus.capture(uid, "sys", f"question {i}", f"answer {i}", "stub", "coach")


# --- the switch plants and takes back ------------------------------------------

def test_capture_on_plants_a_learn_task_scoped_to_this_person(client):
    uid = enroll(client)
    vault = StandingVault()
    out = corpus.set_consent(uid, True, pdi=vault)
    assert out["learning"]["planted"] is True
    tid = out["learning"]["task_id"]
    task = vault.standing[tid]
    assert task["goal"] == f"learn from the corpus: {uid}"
    assert task["plan_steps"] == [{"tool": "corpus.learn",
                                   "args": {"prefix": f"jim/{uid}/corpus/"}}]
    assert task["every_hours"] == corpus.LEARN_EVERY_HOURS == 24.0
    assert "corpus.planted" in _actions(uid)


def test_a_task_already_standing_is_not_doubled(client):
    uid = enroll(client)
    vault = StandingVault()
    first = corpus.plant_learning(uid, vault)["task_id"]
    second = corpus.plant_learning(uid, vault)["task_id"]
    assert first == second and len(vault.standing) == 1


def test_capture_off_takes_the_task_back(client):
    uid = enroll(client)
    vault = StandingVault()
    tid = corpus.set_consent(uid, True, pdi=vault)["learning"]["task_id"]
    out = corpus.set_consent(uid, False, pdi=vault)
    assert out["capturing"] is False
    assert out["learning"]["planted"] is False
    assert out["learning"]["why"] == "capture is off"
    assert vault.cancelled == [tid]
    assert "corpus.unplanted" in _actions(uid)


def test_the_row_lets_go_only_after_the_vault_did(client):
    uid = enroll(client)
    vault = StandingVault()
    tid = corpus.set_consent(uid, True, pdi=vault)["learning"]["task_id"]
    # The cancel cannot reach the vault: the id stays so the next try can end it.
    out = corpus.unplant_learning(uid, BrokenVault())
    assert out["unplanted"] is False and out["task_id"] == tid
    assert corpus._learn_task_id(uid) == tid
    assert corpus.unplant_learning(uid, vault)["unplanted"] is True
    assert corpus._learn_task_id(uid) is None


# --- honest at the edges ---------------------------------------------------------

def test_no_vault_says_so(client):
    uid = enroll(client)
    out = corpus.set_consent(uid, True, pdi=None)
    assert out["learning"] == {"planted": False, "task_id": None,
                               "every_hours": 24.0, "status": None,
                               "next_run_at": None, "why": "no vault configured"}


def test_an_older_tandem_says_so(client):
    uid = enroll(client)
    got = corpus.plant_learning(uid, OlderVault())
    assert got["planted"] is False
    assert got["why"] == "the vault has no standing tasks (older PDI)"
    assert corpus._learn_task_id(uid) is None


def test_an_unreached_vault_says_so_and_plants_nothing(client):
    uid = enroll(client)
    got = corpus.plant_learning(uid, BrokenVault())
    assert got["planted"] is False and got["why"]
    assert corpus._learn_task_id(uid) is None


def test_the_posture_reads_the_task_as_the_vault_sees_it(client):
    uid = enroll(client)
    vault = StandingVault()
    tid = corpus.set_consent(uid, True, pdi=vault)["learning"]["task_id"]
    vault.standing[tid]["status"] = "done"
    got = corpus.learning(uid, vault)
    assert got["planted"] and got["status"] == "done"
    assert got["next_run_at"] == "2999-01-01T00:00:00+00:00"
    # Gone from the vault: said, not padded.
    del vault.standing[tid]
    assert corpus.learning(uid, vault)["why"] == "the vault no longer holds this task"


# --- the bank archives itself ------------------------------------------------------

def test_the_first_archive_plants_the_task_for_the_untouched_switch(client):
    uid = enroll(client)
    vault = StandingVault()
    _bank(uid, 3)
    out = corpus.archive(uid, pdi=vault)
    assert out["archived"] == 3
    assert corpus._learn_task_id(uid) in vault.standing
    assert corpus.learning(uid, vault)["planted"] is True


def test_the_bank_seals_itself_at_the_threshold(client, monkeypatch):
    uid = enroll(client)
    vault = StandingVault()
    monkeypatch.setattr(corpus, "_vault_for", lambda user_id: vault)
    monkeypatch.setattr(corpus, "ARCHIVE_EVERY", 5)
    _bank(uid, 4)
    assert corpus.bank(uid)["archived"] == 0
    _bank(uid, 1)
    b = corpus.bank(uid)
    assert b["examples"] == 5 and b["archived"] == 5
    bundles = [k for k in vault.records if k.startswith(f"jim/{uid}/corpus/")]
    assert len(bundles) == 1
    # And the learn task now stands, planted by the archive.
    assert corpus.learning(uid, vault)["planted"] is True


def test_without_a_vault_the_bank_keeps_banking_on_this_machine(client, monkeypatch):
    uid = enroll(client)
    monkeypatch.setattr(corpus, "_vault_for", lambda user_id: None)
    monkeypatch.setattr(corpus, "ARCHIVE_EVERY", 3)
    _bank(uid, 7)
    b = corpus.bank(uid)
    assert b["examples"] == 7 and b["archived"] == 0


# --- over HTTP ---------------------------------------------------------------------

def test_the_doors_carry_the_learn_task(client):
    uid = enroll(client)
    vault = StandingVault()
    client.app.state.pdi = vault
    r = client.put(f"/corpus/{uid}/consent", json={"enabled": True})
    assert r.status_code == 200, r.text
    assert r.json()["learning"]["planted"] is True
    p = client.get(f"/corpus/{uid}").json()
    assert p["learning"]["planted"] is True and p["learning"]["task_id"]
    r = client.put(f"/corpus/{uid}/consent", json={"enabled": False})
    assert r.json()["learning"]["planted"] is False
    assert vault.cancelled
