"""The lookout: a page the vault keeps fresh (jim/lookout.py).

PDI's standing tasks let the vault keep its own appointments; this is
JIM putting them to work. "Keep an eye on this page" becomes one
standing plan whose single fetch step re-seals the current capture
every cycle — JIM never does the watching, and what leaves JIM is the
URL once, at planting.

    asked     can JIM watch a page for somebody
    mattered  who does the watching, and where the page lives

The rules held here: consent before the web (the study permit gates
planting); writes plan-gated, reads and drops on the real vault; the
ledger lets go only after the vault did; honesty at every edge.
"""

from __future__ import annotations

import json

from jim import db, life, lookout

from .conftest import enroll
from .test_the_coach_remembers_through_the_vault import (BrokenVault,
                                                         FakeResidentVault)


class StandingVault(FakeResidentVault):
    """A PDI with standing tasks, the way `lookout` sees one."""

    def __init__(self):
        super().__init__()
        self.standing: dict[str, dict] = {}
        self.cancelled: list[str] = []
        self.runs: dict[str, list] = {}
        self._n = 0

    def resident_stand(self, goal, steps, every_hours):
        self._n += 1
        tid = f"rtk_{self._n:04d}"
        self.standing[tid] = {
            "id": tid, "goal": goal, "status": "planned",
            "every_hours": every_hours,
            "next_run_at": "2999-01-01T00:00:00+00:00",
            "plan_steps": steps}
        return dict(self.standing[tid])

    def resident_cancel(self, task_id):
        if task_id in self.standing:
            del self.standing[task_id]
            self.cancelled.append(task_id)
            return True
        return False

    def resident_tasks(self):
        return [dict(t) for t in self.standing.values()]

    def resident_runs(self, task_id):
        return list(self.runs.get(task_id, []))


class OlderVault(StandingVault):
    """A PDI from before standing tasks: the client answers None."""

    def resident_stand(self, goal, steps, every_hours):
        return None


def _allow_study(client, user_id):
    from jim import errands
    r = client.put(f"/engaged/{user_id}/permits/{errands.PERMIT}",
                   json={"granted": True})
    assert r.status_code == 200, r.text


def _plant(client, uid, url="https://example.com/page", every=24.0):
    r = client.post(f"/lookout/{uid}",
                    json={"url": url, "every_hours": every})
    assert r.status_code == 201, r.text
    return r.json()


# -- planting ----------------------------------------------------------------

def test_planting_needs_the_standing_study_permit(client):
    uid = enroll(client)
    client.app.state.pdi = StandingVault()
    r = client.post(f"/lookout/{uid}",
                    json={"url": "https://example.com", "every_hours": 24})
    assert r.status_code == 403, r.text


def test_a_lookout_is_one_standing_appointment_and_one_ledger_row(client):
    uid = enroll(client)
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(client, uid)
    out = _plant(client, uid)
    assert out["planted"] is True and out["next_run_at"]
    task = vault.standing[out["task_id"]]
    assert task["every_hours"] == 24.0
    assert task["plan_steps"] == [{"tool": "fetch.url",
                                   "args": {"url": "https://example.com/page"}}]
    row = db.connect().execute(
        "SELECT * FROM lookouts WHERE user_id=?", (uid,)).fetchone()
    assert row["task_id"] == out["task_id"]
    assert row["url"] == "https://example.com/page"


def test_planting_is_honest_at_every_edge(client):
    uid = enroll(client)
    _allow_study(client, uid)
    client.app.state.pdi = None
    r = client.post(f"/lookout/{uid}",
                    json={"url": "https://example.com", "every_hours": 24})
    assert r.status_code == 422 and "no vault" in r.text
    client.app.state.pdi = OlderVault()
    r = client.post(f"/lookout/{uid}",
                    json={"url": "https://example.com", "every_hours": 24})
    assert r.status_code == 422 and "standing tasks" in r.text
    client.app.state.pdi = StandingVault()
    r = client.post(f"/lookout/{uid}",
                    json={"url": "ftp://example.com", "every_hours": 24})
    assert r.status_code == 422, r.text
    r = client.post(f"/lookout/{uid}",
                    json={"url": "https://example.com", "every_hours": 0.01})
    assert r.status_code == 422 and "quarter-hour" in r.text
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM lookouts").fetchone()["n"] == 0


# -- the list ----------------------------------------------------------------

def test_the_list_carries_what_the_vault_says(client):
    uid = enroll(client)
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(client, uid)
    planted = _plant(client, uid)
    out = client.get(f"/lookout/{uid}").json()
    assert out["readable"] is True
    assert len(out["lookouts"]) == 1
    watch = out["lookouts"][0]
    assert watch["url"] == "https://example.com/page"
    assert watch["status"] == "planned"
    assert watch["next_run_at"] == vault.standing[planted["task_id"]][
        "next_run_at"]


def test_an_unreached_tandem_lists_without_pretending(client):
    uid = enroll(client)
    client.app.state.pdi = StandingVault()
    _allow_study(client, uid)
    _plant(client, uid)
    client.app.state.pdi = BrokenVault()
    out = client.get(f"/lookout/{uid}").json()
    assert out["readable"] is False
    assert len(out["lookouts"]) == 1
    assert out["lookouts"][0]["status"] is None


# -- the capture -------------------------------------------------------------

def test_the_capture_reads_back_from_the_seal(client):
    uid = enroll(client)
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(client, uid)
    planted = _plant(client, uid)
    # The resident's cycle, simulated: the fetch re-seals the capture
    # under the plan's one key (pdi/resident.py `_tool_fetch`).
    vault.records[lookout.capture_key(planted["task_id"])] = json.dumps(
        {"url": "https://example.com/page", "text": "today's words",
         "fetched_at": "2026-08-19T09:00:00+00:00"})
    out = client.get(f"/lookout/{uid}/{planted['id']}/page").json()
    assert out["readable"] is True
    assert out["text"] == "today's words"
    assert out["chars"] == len("today's words")
    assert out["fetched_at"] == "2026-08-19T09:00:00+00:00"


def test_before_the_first_fetch_the_page_says_so(client):
    uid = enroll(client)
    client.app.state.pdi = StandingVault()
    _allow_study(client, uid)
    planted = _plant(client, uid)
    out = client.get(f"/lookout/{uid}/{planted['id']}/page").json()
    assert out == {"id": planted["id"], "url": "https://example.com/page",
                   "readable": False, "fetched_at": None, "changed_at": None,
                   "chars": 0, "text": None}
    missing = client.get(f"/lookout/{uid}/lkt_nothere/page")
    assert missing.status_code == 404


def test_a_capture_is_a_reading_not_an_archive(client):
    uid = enroll(client)
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(client, uid)
    planted = _plant(client, uid)
    vault.records[lookout.capture_key(planted["task_id"])] = json.dumps(
        {"url": "u", "text": "x" * (lookout.PAGE_CAP * 2),
         "fetched_at": "t"})
    out = lookout.page(uid, planted["id"], pdi=vault)
    assert len(out["text"]) == lookout.PAGE_CAP
    assert out["chars"] == lookout.PAGE_CAP * 2, (
        "the honest size of the seal, beside the capped reading")


# -- the drop ----------------------------------------------------------------

def test_dropping_stops_the_watching_the_whole_way(client):
    uid = enroll(client)
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(client, uid)
    planted = _plant(client, uid)
    vault.records[lookout.capture_key(planted["task_id"])] = "{}"
    r = client.delete(f"/lookout/{uid}/{planted['id']}")
    assert r.status_code == 200, r.text
    assert r.json() == {"removed": True, "id": planted["id"]}
    assert vault.cancelled == [planted["task_id"]], "the appointment stands"
    assert lookout.capture_key(planted["task_id"]) not in vault.records, (
        "the capture survived the drop")
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM lookouts").fetchone()["n"] == 0


def test_a_down_tandem_keeps_the_row_on_the_list(client):
    """The ledger lets go only after the vault did: a row whose
    appointment still stands belongs on the list, not orphaned."""
    uid = enroll(client)
    client.app.state.pdi = StandingVault()
    _allow_study(client, uid)
    planted = _plant(client, uid)
    client.app.state.pdi = BrokenVault()
    r = client.delete(f"/lookout/{uid}/{planted['id']}")
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["removed"] is False and "OSError" in out["why"]
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM lookouts").fetchone()["n"] == 1


# -- erasure -----------------------------------------------------------------

def test_erasure_cancels_every_appointment_and_unseals_every_capture(client):
    uid = enroll(client)
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(client, uid)
    a = _plant(client, uid, url="https://example.com/a")
    b = _plant(client, uid, url="https://example.com/b", every=1.0)
    for planted in (a, b):
        vault.records[lookout.capture_key(planted["task_id"])] = "{}"
    deleted = life.delete_user_data(uid, pdi=vault)["deleted"]
    assert deleted["lookouts_cancelled"] == 2
    assert vault.standing == {}, "an appointment survived erasure"
    assert not any(k.startswith("resident/") for k in vault.records), (
        "a capture survived erasure")
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM lookouts WHERE user_id=?",
        (uid,)).fetchone()["n"] == 0


# -- the payoff: the coach speaks from the capture ---------------------------

def _seal_capture(vault, task_id, text,
                  fetched="2026-08-19T09:00:00+00:00",
                  url="https://example.com/page"):
    vault.records[lookout.capture_key(task_id)] = json.dumps(
        {"url": url, "text": text, "fetched_at": fetched})


def test_the_coach_answers_from_the_current_capture(client, monkeypatch):
    uid = enroll(client)
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(client, uid)
    planted = _plant(client, uid)
    _seal_capture(vault, planted["task_id"],
                  "Pollen count is very high today")
    seen = {}
    orig = lookout.prompt_block

    def spy(user_id, pdi=None):
        out = orig(user_id, pdi)
        seen["block"] = out
        return out

    monkeypatch.setattr(lookout, "prompt_block", spy)
    r = client.post(f"/coach/{uid}", json={
        "area": "health_fitness", "message": "should I run outside today"})
    assert r.status_code == 200, r.text
    assert r.json()["content"]
    assert "Pollen count is very high" in seen["block"]
    assert "captured 2026-08-19" in seen["block"], (
        "a capture must ride the prompt wearing its date")


def test_an_unreadable_tandem_contributes_nothing_not_a_failure(client):
    uid = enroll(client)
    client.app.state.pdi = StandingVault()
    _allow_study(client, uid)
    _plant(client, uid)
    client.app.state.pdi = BrokenVault()
    r = client.post(f"/coach/{uid}", json={
        "area": "health_fitness", "message": "hello there"})
    assert r.status_code == 200, r.text
    assert r.json()["content"]
    assert lookout.prompt_block(uid, BrokenVault()) is None


def test_a_capture_rides_as_a_digest_not_an_archive(client):
    uid = enroll(client)
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(client, uid)
    planted = _plant(client, uid)
    _seal_capture(vault, planted["task_id"], "x" * (lookout.PROMPT_CAP * 5))
    block = lookout.prompt_block(uid, vault)
    assert block is not None
    assert len(block) < lookout.PROMPT_CAP * 2


# -- the change date rides everywhere the capture shows ----------------------

def test_the_list_and_the_page_say_when_the_page_changed(client):
    uid = enroll(client)
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(client, uid)
    planted = _plant(client, uid)
    vault.records[lookout.capture_key(planted["task_id"])] = json.dumps(
        {"url": "https://example.com/page", "text": "words",
         "fetched_at": "2026-08-19T09:00:00+00:00",
         "changed_at": "2026-08-18T07:00:00+00:00"})
    row = client.get(f"/lookout/{uid}").json()["lookouts"][0]
    assert row["changed_at"] == "2026-08-18T07:00:00+00:00"
    got = client.get(f"/lookout/{uid}/{planted['id']}/page").json()
    assert got["changed_at"] == "2026-08-18T07:00:00+00:00"
    block = lookout.prompt_block(uid, vault)
    assert "last changed 2026-08-18" in block


def test_a_capture_before_fingerprints_says_nothing_not_now(client):
    """A seal from before PDI carried change history has no changed_at;
    the list answers None rather than inventing a date."""
    uid = enroll(client)
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(client, uid)
    planted = _plant(client, uid)
    _seal_capture(vault, planted["task_id"], "words")
    row = client.get(f"/lookout/{uid}").json()["lookouts"][0]
    assert row["changed_at"] is None
    got = client.get(f"/lookout/{uid}/{planted['id']}/page").json()
    assert got["readable"] is True and got["changed_at"] is None
    assert "last changed" not in lookout.prompt_block(uid, vault)


# -- the trouble line: why the watching last failed --------------------------

def test_the_list_says_why_the_watching_last_failed(client):
    uid = enroll(client)
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(client, uid)
    planted = _plant(client, uid)
    vault.runs[planted["task_id"]] = [
        {"id": "rrun_2", "ran_at": "2026-08-19T10:00:00+00:00",
         "status": "failed", "note": "ResidentError: the wire is down"},
        {"id": "rrun_1", "ran_at": "2026-08-19T09:00:00+00:00",
         "status": "done", "note": "fetched 12 chars"},
    ]
    row = client.get(f"/lookout/{uid}").json()["lookouts"][0]
    assert row["trouble"] == "ResidentError: the wire is down"


def test_a_recovered_lookout_carries_no_stale_trouble(client):
    """Only the *latest* round speaks: a lookout that failed yesterday
    and ran clean this morning is not in trouble."""
    uid = enroll(client)
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(client, uid)
    planted = _plant(client, uid)
    vault.runs[planted["task_id"]] = [
        {"id": "rrun_2", "ran_at": "2026-08-19T10:00:00+00:00",
         "status": "done", "note": "fetched 12 chars, sealed (unchanged)"},
        {"id": "rrun_1", "ran_at": "2026-08-19T09:00:00+00:00",
         "status": "failed", "note": "ResidentError: the wire is down"},
    ]
    row = client.get(f"/lookout/{uid}").json()["lookouts"][0]
    assert row["trouble"] is None


def test_an_older_vault_without_the_ledger_says_nothing(client):
    uid = enroll(client)

    class NoLedgerVault(StandingVault):
        resident_runs = None

    vault = NoLedgerVault()
    client.app.state.pdi = vault
    _allow_study(client, uid)
    _plant(client, uid)
    row = client.get(f"/lookout/{uid}").json()["lookouts"][0]
    assert row["trouble"] is None
