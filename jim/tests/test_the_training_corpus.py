"""The offline training corpus: every exchange banked so the local model grows.

`offline.py` makes offline *safe* — nothing leaves the machine. This makes it
*capable*: every generated exchange is banked as a training example at the one
place they all pass through, so a local model trained from it grows able enough
to actually answer offline. These tests pin the shape:

* capture happens at `llm.generate_for_user` and tags where it came from;
* it is the person's own — consent off stops it, purge clears it, and a full
  account erase reaches it with no line of its own (the schema-erase guard);
* archive seals it into the vault, and is honest when there is no vault;
* the posture is honest that a local *language* model is not wired yet.
"""

import pytest

from jim import corpus, db, llm
from jim.tests.conftest import enroll


def _count(user_id):
    return db.connect().execute(
        "SELECT COUNT(*) AS n FROM training_examples WHERE user_id=?",
        (user_id,)).fetchone()["n"]


def test_a_generation_is_banked_with_its_source(client):
    uid = enroll(client)
    before = _count(uid)
    out = llm.generate_for_user(uid, "You are a test.", "hello", source="probe")
    assert out["text"]
    assert _count(uid) == before + 1
    ex = corpus.export(uid)[-1]
    assert ex["prompt"] == "hello" and ex["completion"] == out["text"]
    assert ex["source"] == "probe" and ex["provider"]


def test_capture_off_banks_nothing(client):
    uid = enroll(client)
    corpus.set_consent(uid, False)
    assert corpus.opted_in(uid) is False
    before = _count(uid)
    llm.generate_for_user(uid, "sys", "hi", source="probe")
    assert _count(uid) == before, "an exchange was banked while capture was off"
    # Turning it back on resumes capture.
    corpus.set_consent(uid, True)
    llm.generate_for_user(uid, "sys", "hi again", source="probe")
    assert _count(uid) == before + 1


def test_the_bank_counts_by_source_and_provider(client):
    uid = enroll(client)
    llm.generate_for_user(uid, "sys", "one", source="coach")
    llm.generate_for_user(uid, "sys", "two", source="coach")
    llm.generate_for_user(uid, "sys", "three", source="mailbox")
    b = corpus.bank(uid)
    assert b["examples"] == 3
    assert b["by_source"]["coach"] == 2 and b["by_source"]["mailbox"] == 1
    assert sum(b["by_provider"].values()) == 3
    assert b["ready_to_train"] is False   # three is not two hundred


def test_the_posture_is_honest_that_no_local_language_model_is_wired(client):
    uid = enroll(client)
    p = corpus.posture(uid)
    assert p["local_language_model_ready"] is False
    assert "offline" in p and "external_transmission_possible" in p["offline"]
    assert "banked on this machine" in p["note"]


def test_purge_is_the_forget_door(client):
    uid = enroll(client)
    llm.generate_for_user(uid, "sys", "remember me", source="probe")
    assert _count(uid) == 1
    out = corpus.purge(uid)
    assert out["purged"] >= 1
    assert _count(uid) == 0
    assert "corpus.purged" in [r["action"] for r in db.connect().execute(
        "SELECT action FROM audit WHERE user_id=?", (uid,)).fetchall()]


def test_archive_without_a_vault_is_honest(client):
    uid = enroll(client)
    llm.generate_for_user(uid, "sys", "seal me", source="probe")
    out = corpus.archive(uid, pdi=None)
    assert out["archived"] == 0 and "no vault" in out["reason"]


class _FakeVault:
    """A vault the way `life.vault_store` sees one: it seals by key."""
    def __init__(self):
        self.records = {}
    def put(self, key, value):
        self.records[key] = value


def test_archive_with_a_vault_seals_and_marks(client):
    uid = enroll(client)
    llm.generate_for_user(uid, "sys", "seal me", source="probe")
    pdi = _FakeVault()
    out = corpus.archive(uid, pdi=pdi)
    assert pdi.records, "nothing was sealed into the vault"
    assert out["archived"] >= 1 and out["bundle"]
    # A second archive has nothing new.
    assert corpus.archive(uid, pdi=pdi)["archived"] == 0
    assert corpus.bank(uid)["archived"] >= 1


# --- the owner's doors ------------------------------------------------------

def test_the_corpus_doors_are_the_owners(client):
    uid = enroll(client)
    llm.generate_for_user(uid, "sys", "hi", source="probe")
    assert client.get(f"/corpus/{uid}").json()["examples"] >= 1
    assert corpus.export(uid)      # the library export feeds a training run
    off = client.put(f"/corpus/{uid}/consent", json={"enabled": False})
    assert off.status_code == 200 and off.json()["capturing"] is False
    assert client.delete(f"/corpus/{uid}").json()["purged"] >= 1


def test_the_corpus_is_not_reachable_without_the_owners_token(client):
    uid = enroll(client)
    other = enroll(client)   # client now carries other's token
    assert other != uid
    assert client.get(f"/corpus/{uid}").status_code == 403
