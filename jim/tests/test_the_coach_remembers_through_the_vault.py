"""Long-term memory through the PDI resident (jim/recall.py).

PDI 0.86.0 gave the vault an embedding index that stores a hash of the text
and never the text. This is JIM's side: coach turns, journal entries and
check-in notes are sealed into the vault and indexed under the same key, so
the coach can find the earlier session that is *about* this one. Three
rules, each held here: memory never breaks the doing, no vault means no
memory and no pretending, and one person's memories never surface for
another.
"""

from __future__ import annotations

import json

from jim import coach, errands, life, recall

from .conftest import enroll


class FakeResidentVault:
    """A PDI client the way `recall` sees one: sealed records, an embedding
    index that knows keys and texts, a naive-but-honest search (token
    overlap), and the resident task doors `tabulate` drives."""

    def __init__(self):
        self.records: dict[str, str] = {}
        self.embedded: dict[str, str] = {}
        self.tabulated: list[tuple[str, list, str | None]] = []
        self.has_resident = True

    def put(self, key, value):
        self.records[key] = value

    def get(self, key):
        return self.records.get(key)

    def resident_embed(self, key, text):
        if not self.has_resident:
            return False
        self.embedded[key] = text
        return True

    def delete(self, key):
        return self.records.pop(key, None) is not None

    def resident_forget(self, key, prefix=False):
        doomed = ([k for k in self.embedded if k.startswith(key)]
                  if prefix else [k for k in self.embedded if k == key])
        for k in doomed:
            del self.embedded[k]
        return len(doomed)

    def resident_search(self, query, top_k=5):
        want = set(query.lower().split())
        scored = []
        for key, text in self.embedded.items():
            overlap = len(want & set(text.lower().split()))
            if overlap:
                scored.append((overlap, key))
        scored.sort(reverse=True)
        return [{"key": k, "score": float(s)} for s, k in scored[:top_k]]

    def resident_tabulate(self, dataset, rows, source_ref=None):
        if not self.has_resident:
            return False
        self.tabulated.append((dataset, rows, source_ref))
        return True


class BrokenVault:
    """A tandem that is down: every method raises."""

    def __getattr__(self, name):
        def boom(*a, **k):
            raise OSError("tandem unreachable")
        return boom


# -- remember ----------------------------------------------------------------

def test_a_checkin_note_becomes_a_sealed_indexed_memory(client):
    uid = enroll(client)
    vault = FakeResidentVault()
    out = life.check_in(uid, 3, 2, "shoulder still aches after the fall",
                        pdi=vault)
    key = f"jim/{uid}/memory/checkin/{out['id']}"
    assert key in vault.embedded
    sealed = json.loads(vault.records[key])
    assert sealed["line"] == "shoulder still aches after the fall"
    assert sealed["kind"] == "checkin"


def test_a_journal_entry_is_a_memory_by_definition(client):
    uid = enroll(client)
    vault = FakeResidentVault()
    out = life.add_journal(uid, "started swimming again today", pdi=vault)
    assert f"jim/{uid}/memory/journal/{out['id']}" in vault.embedded


def test_the_coach_turn_remembers_what_the_person_said(client):
    uid = enroll(client)
    vault = FakeResidentVault()
    coach.reply(uid, "health_fitness", "my knee hurts when I run",
                pdi=vault)
    memories = [t for k, t in vault.embedded.items()
                if k.startswith(f"jim/{uid}/memory/coach/")]
    assert memories == ["(health_fitness) my knee hurts when I run"]
    # The reply is derivative and is not indexed.
    assert len(vault.embedded) == 1


# -- recall ------------------------------------------------------------------

def test_the_coach_finds_the_earlier_session_about_this_one(client):
    uid = enroll(client)
    vault = FakeResidentVault()
    life.check_in(uid, 3, 2, "shoulder injury from the ladder", pdi=vault)
    lines = recall.coach_lines(vault, uid,
                               "can I start training my shoulder again")
    assert len(lines) == 1
    assert "shoulder injury from the ladder" in lines[0]
    assert lines[0].startswith("remembered from an earlier checkin")


def test_another_persons_memories_never_surface(client):
    """The second wall behind PDI's tenant fence: one deployment tenant
    holds many people's memories under one token, so recall drops any key
    outside this person's prefix before it fetches a word."""
    alice = enroll(client)
    bob = enroll(client)
    vault = FakeResidentVault()
    life.check_in(alice, 2, 2, "the divorce paperwork is exhausting",
                  pdi=vault)
    assert recall.coach_lines(vault, bob, "divorce paperwork advice") == []


def test_no_vault_means_no_memory_and_no_pretending(client):
    uid = enroll(client)
    out = recall.remember(None, uid, "coach", "x", "words")
    assert out == {"remembered": False, "why": "no vault configured"}
    assert recall.coach_lines(None, uid, "anything") == []
    # And the coach turn still answers.
    answered = coach.reply(uid, "mental_health", "how do I focus better",
                           pdi=None)
    assert "content" in answered


def test_memory_never_breaks_the_doing(client):
    """A check-in that lands and is not remembered beats a check-in refused
    because the tandem was down."""
    uid = enroll(client)
    out = recall.remember(BrokenVault(), uid, "coach", "x", "words")
    assert out["remembered"] is False
    assert "OSError" in out["why"]
    assert recall.coach_lines(BrokenVault(), uid, "anything") == []


def test_an_older_vault_without_the_resident_is_said_not_hidden(client):
    uid = enroll(client)
    vault = FakeResidentVault()
    vault.has_resident = False
    out = recall.remember(vault, uid, "coach", "x", "the words")
    assert out == {"remembered": False,
                   "why": "the vault has no memory index"}
    # Sealed anyway: the words are safe even where they are not findable.
    assert f"jim/{uid}/memory/coach/x" in vault.records


def test_a_memory_is_a_line_not_a_transcript(client):
    uid = enroll(client)
    vault = FakeResidentVault()
    recall.remember(vault, uid, "journal", "j1", "x" * 5000)
    line = json.loads(vault.records[f"jim/{uid}/memory/journal/j1"])["line"]
    assert len(line) == recall.MAX_LINE


# -- tabulate: the errand ledger writes itself into the vault's tables -------

def _allow_study(client, user_id):
    r = client.put(f"/engaged/{user_id}/permits/{errands.PERMIT}",
                   json={"granted": True})
    assert r.status_code == 200, r.text


def test_errand_results_land_as_queryable_rows(client, monkeypatch):
    uid = enroll(client)
    _allow_study(client, uid)
    vault = FakeResidentVault()
    monkeypatch.setattr(errands, "due",
                        lambda user_id, limit=errands.DAILY: [
                            {"topic": "resistance bands", "area": "fitness",
                             "why": "coach_missed"}][:limit])

    def fake_excursion(user_id, topic, cloud=None, learn=True):
        from jim import db
        cid = db.new_id("exc")
        db.connect().execute(
            "INSERT INTO excursions (id, user_id, topic, brief, redactions,"
            " left_host, created_at) VALUES (?,?,?,?,0,0,?)",
            (cid, user_id, topic, topic, db.utcnow()))
        db.connect().commit()
        return cid
    from jim import research
    monkeypatch.setattr(research, "excursion", fake_excursion)

    out = errands.run(uid, pdi=vault)
    assert out["vaulted"] is True
    dataset, rows, source = vault.tabulated[0]
    assert dataset == "jim_errands"
    assert rows[0]["topic"] == "resistance bands"
    assert rows[0]["area"] == "fitness"
    assert source == uid


def test_a_down_tandem_keeps_the_errand_and_says_not_vaulted(client,
                                                             monkeypatch):
    uid = enroll(client)
    _allow_study(client, uid)
    monkeypatch.setattr(errands, "due",
                        lambda user_id, limit=errands.DAILY: [
                            {"topic": "sleep hygiene", "area": "mind",
                             "why": "coach_missed"}][:limit])

    def fake_excursion(user_id, topic, cloud=None, learn=True):
        from jim import db
        cid = db.new_id("exc")
        db.connect().execute(
            "INSERT INTO excursions (id, user_id, topic, brief, redactions,"
            " left_host, created_at) VALUES (?,?,?,?,0,0,?)",
            (cid, user_id, topic, topic, db.utcnow()))
        db.connect().commit()
        return cid
    from jim import research
    monkeypatch.setattr(research, "excursion", fake_excursion)

    out = errands.run(uid, pdi=BrokenVault())
    assert len(out["errands"]) == 1
    assert out["vaulted"] is False


# -- forgetting reaches the vectors ------------------------------------------

def test_deleting_a_journal_entry_unmakes_its_memory(client):
    """The seal, the ledger row, and the vector — all three, so the coach
    stops reciting an entry the person deleted."""
    uid = enroll(client)
    vault = FakeResidentVault()
    out = life.add_journal(uid, "I have been drinking too much", pdi=vault)
    key = f"jim/{uid}/memory/journal/{out['id']}"
    assert key in vault.embedded and key in vault.records
    assert life.remove_journal(uid, out["id"], pdi=vault)
    assert key not in vault.embedded, "the vector survived the delete"
    assert key not in vault.records, "the seal survived the delete"
    from jim import db
    row = db.connect().execute(
        "SELECT COUNT(*) AS n FROM vault_keys WHERE user_id=? AND key=?",
        (uid, key)).fetchone()
    assert row["n"] == 0, "the ledger row survived the delete"
    assert recall.coach_lines(vault, uid, "drinking too much") == []


def test_user_erasure_takes_every_memory_vector_in_one_call(client):
    uid = enroll(client)
    vault = FakeResidentVault()
    life.check_in(uid, 2, 2, "note one about the move", pdi=vault)
    life.add_journal(uid, "note two about the move", pdi=vault)
    assert len(vault.embedded) == 2
    deleted = life.delete_user_data(uid, pdi=vault)["deleted"]
    assert deleted["memory_vectors"] == 2
    assert vault.embedded == {}


def test_an_unreached_tandem_says_so_in_the_erasure_answer(client):
    uid = enroll(client)
    deleted = life.delete_user_data(uid, pdi=BrokenVault())["deleted"]
    assert deleted["memory_vectors"] is None


def test_a_journal_delete_does_not_depend_on_the_tandem(client):
    uid = enroll(client)
    vault = FakeResidentVault()
    out = life.add_journal(uid, "a line to keep then drop", pdi=vault)
    assert life.remove_journal(uid, out["id"], pdi=BrokenVault())
