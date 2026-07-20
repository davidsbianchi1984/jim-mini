"""Cross-product session continuity: a conversation started with a QRME
specialist continues on any JIM device — same thread, same memory."""

import pytest
from fastapi.testclient import TestClient

from jim import db as jim_db
from jim.tests.conftest import _Resp, enroll


class FakeQRMEWithMemory:
    """A QRME double that issues interactor tokens and serves the shared
    thread's memory back — gated on the interactor's own token, like the
    real thing."""

    def __init__(self):
        self.memory = []          # the shared thread
        self.token = "itok_1"

    def post(self, path, json=None, headers=None):
        if path == "/interactors":
            return _Resp(201, {"id": "usr_qrme1", "token": self.token})
        if path.endswith("/chat"):
            msg = (json or {}).get("message", "")
            self.memory.append({"role": "interactor", "content": msg})
            reply = f"[QRME specialist] I hear you. ({msg[:30]})"
            self.memory.append({"role": "profile", "content": reply})
            return _Resp(200, {"profile_message": {
                "content": reply, "status": "approved", "flag_reason": None}})
        return _Resp(404, {})

    def get(self, path, headers=None):
        if "/memory/" in path:
            auth = (headers or {}).get("authorization", "")
            if auth != f"Bearer {self.token}":
                return _Resp(401, {})
            return _Resp(200, list(self.memory))
        if path.startswith("/profiles/"):
            return _Resp(200, {"adult_mode": False, "status": "active"})
        return _Resp(404, {})


@pytest.fixture()
def tandem(tmp_path, monkeypatch):
    monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
    monkeypatch.setenv("JIM_LLM", "stub")
    jim_db.reset()
    from jim.api import create_app
    from jim.qrme_client import QRMEClient
    fake = FakeQRMEWithMemory()
    with TestClient(create_app(qrme_client=QRMEClient(client=fake))) as c:
        yield c, fake
    jim_db.reset()


def test_new_device_session_resumes_the_qrme_thread(tandem):
    jim, fake = tandem
    uid = enroll(jim)
    jim.post("/specialists", json={
        "condition": "anxiety", "mode": "tandem", "qrme_profile_id": "prf_x"})
    # A detection routes guidance through the QRME specialist — the thread
    # begins (from, say, the user's phone).
    jim.post(f"/monitor/{uid}", json={"heart_rate": 120, "respiratory_rate": 22})
    assert len(fake.memory) == 2

    # Later, a *different* device logs in: the session carries the thread.
    s = jim.post(f"/sessions/{uid}", json={"device": "kitchen_console"}).json()
    cont = s["continuity"]
    assert cont["with"] == "qrme_specialist"
    assert cont["qrme_profile_id"] == "prf_x"
    assert [t["role"] for t in cont["recent_turns"]] == ["interactor", "profile"]
    assert "same thread, same memory" in cont["note"]


def test_no_thread_means_no_continuity_block(tandem):
    jim, _ = tandem
    uid = enroll(jim)
    s = jim.post(f"/sessions/{uid}", json={"device": "watch"}).json()
    assert s["continuity"] is None


def test_continuity_is_none_without_tandem(client):
    uid = enroll(client)                       # standalone app, no QRME wired
    s = client.post(f"/sessions/{uid}", json={"device": "watch"}).json()
    assert s["continuity"] is None
