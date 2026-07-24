import pytest
from fastapi.testclient import TestClient

from jim import db as jim_db


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """JIM-mini running standalone (no tandem)."""
    monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
    monkeypatch.setenv("JIM_LLM", "stub")
    monkeypatch.delenv("JIM_QRME_URL", raising=False)
    jim_db.reset()
    from jim.api import create_app

    with TestClient(create_app()) as c:
        yield c
    jim_db.reset()


class _Resp:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class FakeQRME:
    """A stand-in for a running QRME service, at the HTTP-client boundary.

    Implements just the two endpoints jim/qrme_client.py calls: create an
    interactor and chat with a specialist profile. ``hold=True`` simulates a
    QRME profile whose moderation holds the reply for owner approval.
    """

    def __init__(self, hold=False):
        self.hold = hold
        self._n = 0

    def post(self, path, json=None, headers=None):
        if path == "/interactors":
            self._n += 1
            return _Resp(201, {"id": f"usr_fake{self._n}"})
        if path.startswith("/profiles/") and path.endswith("/chat"):
            if self.hold:
                return _Resp(200, {"profile_message": {
                    "content": None, "status": "pending",
                    "flag_reason": "owner approval required"}})
            msg = (json or {}).get("message", "")
            return _Resp(200, {"profile_message": {
                "content": f"[QRME specialist] I hear you. ({msg[:40]})",
                "status": "approved", "flag_reason": None}})
        return _Resp(404, {})

    # The QRME Starter Collection handles this fake can resolve, mirroring
    # the real deployment's seeded marketplace.
    starter_handles = ("marcus_bell", "dr_amara_osei")

    def get(self, path, headers=None):
        if path.startswith("/summon"):
            from urllib.parse import parse_qs, urlparse
            ref = parse_qs(urlparse(path).query).get("ref", [""])[0]
            handle = ref.lstrip("@")
            if handle in self.starter_handles:
                return _Resp(200, {"type": "handle", "profile": {
                    "profile_id": f"prf_{handle}",
                    "display_name": handle, "chat": True}})
            return _Resp(404, {"detail": "unknown handle"})
        return _Resp(404, {})


@pytest.fixture()
def make_tandem(tmp_path, monkeypatch):
    """Factory: a JIM app wired to a FakeQRME through the real QRMEClient."""
    created = []

    def _make(hold=False):
        monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
        monkeypatch.setenv("JIM_LLM", "stub")
        jim_db.reset()
        from jim.api import create_app
        from jim.qrme_client import QRMEClient

        tc = TestClient(create_app(qrme_client=QRMEClient(client=FakeQRME(hold=hold))))
        tc.__enter__()
        created.append(tc)
        return tc

    yield _make
    for tc in created:
        tc.__exit__(None, None, None)
    jim_db.reset()


def enroll(client, **extra):
    body = {"display_name": "Jordan", "birthdate": "1995-05-05",
            "terms_consent": True, "resting_heart_rate": 60}
    body.update(extra)
    r = client.post("/enroll", json=body)
    assert r.status_code == 201, r.text
    out = r.json()
    # Hold the user capability so subsequent per-user calls authorize. The
    # most-recently enrolled user's token becomes the client default; tests
    # with several users switch with as_user()/user_header().
    client.headers["authorization"] = f"Bearer {out['user_token']}"
    return out["id"]


def user_header(client_response_or_token) -> dict:
    """Authorization header from a raw user token."""
    return {"authorization": f"Bearer {client_response_or_token}"}


def as_user(client, token) -> None:
    """Make ``token``'s user the client's default caller."""
    client.headers["authorization"] = f"Bearer {token}"
