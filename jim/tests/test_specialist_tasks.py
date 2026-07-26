"""Handing a QRME specialist a task rather than a turn.

`_tandem_guidance` sends one message and gets one reply. That is right for
"say something supportive" and wrong for work with several steps that has to
survive the user putting the phone down. These cover the second shape.
"""

import pytest
from fastapi.testclient import TestClient

from jim import db as jim_db
from jim.tests.conftest import _Resp, enroll


class FakeQRMEWithWorkflows:
    """A QRME double speaking the delegated-workflow surface.

    ``phases`` is what the profile's *owner* permits — the whole point of the
    delegated routes is that this is not the caller's choice.
    """

    def __init__(self, phases=("research", "draft", "review", "confirm"),
                 delegation=True, refuse_start=False):
        self.phases = list(phases)
        self.delegation = delegation
        self.refuse_start = refuse_start
        self.token = "itok_1"
        self.started = []
        self.workflows = {}

    def post(self, path, json=None, headers=None):
        if path == "/interactors":
            return _Resp(201, {"id": "usr_q1", "token": self.token})
        if path.endswith("/chat"):
            return _Resp(200, {"profile_message": {
                "content": "[QRME specialist] I hear you.",
                "status": "approved", "flag_reason": None}})

        if path.endswith("/delegated-workflows"):
            if (headers or {}).get("authorization") != f"Bearer {self.token}":
                return _Resp(403, {"detail": "not authorized"})
            if self.refuse_start:
                return _Resp(403, {"detail": "declined"})
            plan = (json or {}).get("plan") or list(self.phases)
            outside = [p for p in plan if p not in self.phases]
            if outside:
                return _Resp(403, {"detail": f"does not permit: {outside}"})
            wid = f"wfl_{len(self.workflows) + 1}"
            self.workflows[wid] = {"id": wid, "plan": plan, "cursor": 0,
                                   "memory": {}, "status": "running",
                                   "awaiting": None,
                                   "next_phase": plan[0]}
            self.started.append((json or {}).get("goal"))
            return _Resp(201, self.workflows[wid])

        if "/delegated-workflows/" in path and path.endswith("/advance"):
            wid = path.split("/delegated-workflows/")[1].split("/")[0]
            wf = self.workflows.get(wid)
            if wf is None:
                return _Resp(404, {})
            phase = wf["plan"][wf["cursor"]]
            if phase == "confirm":
                wf["status"] = "awaiting_input"
                wf["awaiting"] = "external confirmation"
                return _Resp(200, wf)
            wf["memory"][phase] = f"<{phase} output>"
            wf["cursor"] += 1
            wf["next_phase"] = (wf["plan"][wf["cursor"]]
                                if wf["cursor"] < len(wf["plan"]) else None)
            if wf["next_phase"] is None:
                wf["status"] = "completed"
            return _Resp(200, wf)
        return _Resp(404, {})

    def get(self, path, headers=None):
        if path.endswith("/delegation"):
            if not self.delegation:
                return _Resp(200, {"delegation": False, "phases": []})
            return _Resp(200, {"delegation": True, "phases": self.phases})
        if "/delegated-workflows/" in path:
            wid = path.rsplit("/", 1)[1]
            wf = self.workflows.get(wid)
            return _Resp(200, wf) if wf else _Resp(404, {})
        if "/memory/" in path:
            return _Resp(200, [])
        if path.startswith("/profiles/"):
            return _Resp(200, {"adult_mode": False, "status": "active"})
        return _Resp(404, {})


@pytest.fixture()
def tandem(tmp_path, monkeypatch):
    """A JIM app wired to a workflow-speaking QRME, with a tandem specialist
    registered and the link established."""
    def _make(**kw):
        monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
        monkeypatch.setenv("JIM_LLM", "stub")
        jim_db.reset()
        from jim.api import create_app
        from jim.qrme_client import QRMEClient

        fake = FakeQRMEWithWorkflows(**kw)
        c = TestClient(create_app(qrme_client=QRMEClient(client=fake)))
        c.__enter__()
        c.post("/specialists", json={"condition": "anxiety", "mode": "tandem",
                                     "label": "Dr Whitcomb",
                                     "qrme_profile_id": "prf_anx"})
        uid = enroll(c)
        # One tandem guidance turn is what creates the link (and its token).
        c.post(f"/monitor/{uid}", json={"heart_rate": 120,
                                        "respiratory_rate": 22})
        return c, uid, fake
    yield _make
    jim_db.reset()


# -- the happy path ----------------------------------------------------------

def test_a_task_runs_through_its_phases_and_pauses_to_confirm(tandem):
    client, uid, fake = tandem()

    started = client.post(f"/users/{uid}/specialist-tasks", json={
        "condition": "anxiety",
        "goal": "summarize my last month of episodes for my GP"}).json()
    assert started["started"] is True
    assert started["specialist"] == "Dr Whitcomb"
    assert started["plan"] == ["research", "draft", "review", "confirm"]
    tid = started["id"]

    for expected in ("draft", "review", "confirm"):
        out = client.post(
            f"/users/{uid}/specialist-tasks/{tid}/advance").json()
        assert out["next_phase"] == expected

    paused = client.post(f"/users/{uid}/specialist-tasks/{tid}/advance").json()
    assert paused["status"] == "awaiting_input"
    assert paused["awaiting"] == "external confirmation"
    assert paused["phases_done"] == ["draft", "research", "review"]


def test_the_task_survives_being_put_down(tandem):
    """The point of a workflow over a chat turn: status is readable later,
    from a fresh call, without holding anything in memory."""
    client, uid, fake = tandem()
    tid = client.post(f"/users/{uid}/specialist-tasks", json={
        "condition": "anxiety", "goal": "draft a letter"}).json()["id"]
    client.post(f"/users/{uid}/specialist-tasks/{tid}/advance")

    later = client.get(f"/users/{uid}/specialist-tasks/{tid}").json()
    assert later["status"] == "running"
    assert later["next_phase"] == "draft"
    assert later["goal"] == "draft a letter"


def test_listing_tasks_does_not_fan_out_to_qrme(tandem):
    client, uid, fake = tandem()
    client.post(f"/users/{uid}/specialist-tasks",
                json={"condition": "anxiety", "goal": "one"})
    client.post(f"/users/{uid}/specialist-tasks",
                json={"condition": "anxiety", "goal": "two"})

    rows = client.get(f"/users/{uid}/specialist-tasks").json()
    assert [r["goal"] for r in rows] == ["one", "two"]


# -- the owner's envelope wins -----------------------------------------------

def test_the_plan_is_narrowed_to_what_the_owner_permits(tandem):
    """JIM asks for four phases; this owner allows two. The narrower set wins
    rather than the handoff failing."""
    client, uid, fake = tandem(phases=("research", "draft"))
    started = client.post(f"/users/{uid}/specialist-tasks", json={
        "condition": "anxiety", "goal": "a short brief"}).json()
    assert started["started"] is True
    assert started["plan"] == ["research", "draft"]


def test_no_overlap_with_the_policy_is_a_refusal_not_an_empty_task(tandem):
    """An empty intersection would create a workflow with no phases, which
    completes instantly and reads as success."""
    client, uid, fake = tandem(phases=("send",))
    out = client.post(f"/users/{uid}/specialist-tasks", json={
        "condition": "anxiety", "goal": "x", "plan": ["research"]}).json()
    assert out["started"] is False
    assert "permits only send" in out["reason"]
    assert fake.started == []


def test_a_specialist_that_has_not_opted_in_is_answered_not_errored(tandem):
    client, uid, fake = tandem(delegation=False)
    out = client.post(f"/users/{uid}/specialist-tasks", json={
        "condition": "anxiety", "goal": "x"})
    assert out.status_code == 201
    body = out.json()
    assert body["started"] is False
    assert "does not accept delegated work" in body["reason"]
    assert fake.started == []          # never even attempted


def test_a_declined_start_is_reported_plainly(tandem):
    client, uid, fake = tandem(refuse_start=True)
    body = client.post(f"/users/{uid}/specialist-tasks", json={
        "condition": "anxiety", "goal": "x"}).json()
    assert body["started"] is False
    assert "declined" in body["reason"]


def test_no_tandem_specialist_means_no_handoff(tandem):
    client, uid, fake = tandem()
    body = client.post(f"/users/{uid}/specialist-tasks", json={
        "condition": "insomnia", "goal": "x"}).json()   # no such specialist
    assert body["started"] is False
    assert "no tandem specialist" in body["reason"]


# -- boundaries --------------------------------------------------------------

def test_jim_keeps_status_never_the_specialists_drafts(tandem):
    """The drafts live in QRME under its own moderation and the user's token.
    Mirroring them into JIM would make it a second store of generated health
    correspondence."""
    client, uid, fake = tandem()
    tid = client.post(f"/users/{uid}/specialist-tasks", json={
        "condition": "anxiety", "goal": "draft a letter"}).json()["id"]
    client.post(f"/users/{uid}/specialist-tasks/{tid}/advance")

    row = jim_db.connect().execute(
        "SELECT * FROM specialist_tasks WHERE id=?", (tid,)).fetchone()
    stored = " ".join(str(v) for v in dict(row).values())
    assert "<research output>" not in stored

    # The phase names are visible; their contents are not.
    out = client.get(f"/users/{uid}/specialist-tasks/{tid}").json()
    assert out["phases_done"] == ["research"]
    assert "memory" not in out


def test_an_unreachable_specialist_reports_last_known_status(tandem):
    client, uid, fake = tandem()
    tid = client.post(f"/users/{uid}/specialist-tasks", json={
        "condition": "anxiety", "goal": "x"}).json()["id"]

    fake.workflows.clear()             # QRME forgets it / is unreachable
    out = client.get(f"/users/{uid}/specialist-tasks/{tid}").json()
    assert out["reachable"] is False
    assert out["status"] == "running"
    assert "last known status" in out["note"]


def test_another_user_cannot_read_or_advance_a_task(tandem):
    client, uid, fake = tandem()
    tid = client.post(f"/users/{uid}/specialist-tasks", json={
        "condition": "anxiety", "goal": "private"}).json()["id"]

    enroll(client, display_name="Mal")       # client now holds Mal's token
    assert client.get(f"/users/{uid}/specialist-tasks/{tid}").status_code == 403
    assert client.post(
        f"/users/{uid}/specialist-tasks/{tid}/advance").status_code == 403


def test_an_unknown_task_is_404(tandem):
    client, uid, fake = tandem()
    assert client.get(
        f"/users/{uid}/specialist-tasks/stk_nope").status_code == 404
