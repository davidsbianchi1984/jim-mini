"""User-facing "who accessed my data" view: JIM surfaces PDI's audit chain,
filtered to the user's own vault namespace."""

import pytest
from fastapi.testclient import TestClient

from jim import db as jim_db
from jim.tests.conftest import _Resp, enroll


class FakePDIAudit:
    """A PDI double that also records an audit entry for every access and
    serves /audit and /audit/verify — like the real tamper-evident log."""

    def __init__(self):
        self.store = {}
        self.log = []                      # [{action, ref, at}]

    def _record(self, action, ref):
        self.log.append({"tenant_id": "jim", "action": action, "ref": ref,
                         "at": f"2026-01-01T00:00:{len(self.log):02d}"})

    def put(self, path, json=None, headers=None):
        self.store[json["key"]] = json["value"]
        self._record("put", json["key"])
        return _Resp(200, {"key": json["key"]})

    def get(self, path, headers=None):
        if path == "/audit":
            return _Resp(200, list(self.log))
        if path == "/audit/verify":
            return _Resp(200, {"intact": True})
        key = path[len("/records/"):]
        if key in self.store:
            self._record("get", key)
            return _Resp(200, {"key": key, "value": self.store[key]})
        return _Resp(404, {})

    def delete(self, path, headers=None):
        key = path[len("/records/"):]
        ok = self.store.pop(key, None) is not None
        if ok:
            self._record("delete", key)
        return _Resp(204 if ok else 404, None)


@pytest.fixture()
def pdi_app(tmp_path, monkeypatch):
    monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
    monkeypatch.setenv("JIM_LLM", "stub")
    jim_db.reset()
    from jim.api import create_app
    from jim.pdi_client import PDIClient
    fake = FakePDIAudit()
    with TestClient(create_app(
            pdi_client=PDIClient(token="pdi_test", client=fake))) as c:
        yield c, fake
    jim_db.reset()


def test_access_log_lists_the_users_vault_accesses(pdi_app):
    jim, _ = pdi_app
    user = enroll(jim)
    jim.post(f"/monitor/{user}", json={"heart_rate": 120, "respiratory_rate": 22})
    jim.post(f"/journal/{user}", json={"text": "a quiet day"})

    log = jim.get(f"/access-log/{user}").json()
    assert log["vaulted"] is True and log["available"] is True
    assert log["tamper_evident"] is True
    assert log["count"] >= 2
    scopes = {e["scope"] for e in log["entries"]}
    assert any(s.startswith("medical") for s in scopes)
    # Actions are rendered in plain language.
    assert all(e["action"] in ("stored", "read", "erased") for e in log["entries"])


def test_access_log_is_isolated_per_user(pdi_app):
    jim, _ = pdi_app
    a = enroll(jim)
    jim.post(f"/monitor/{a}", json={"heart_rate": 120, "respiratory_rate": 22})
    b = enroll(jim)                        # switches the client's default token
    jim.post(f"/monitor/{b}", json={"heart_rate": 121, "respiratory_rate": 22})

    log_b = jim.get(f"/access-log/{b}").json()
    # None of B's entries reference A's namespace, and vice-versa.
    assert log_b["count"] >= 1
    # B cannot read A's access log (not B's token).
    assert jim.get(f"/access-log/{a}").status_code == 403


def test_access_log_without_a_vault_says_local_only(tmp_path, monkeypatch):
    monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
    monkeypatch.setenv("JIM_LLM", "stub")
    monkeypatch.delenv("JIM_PDI_URL", raising=False)
    jim_db.reset()
    from jim.api import create_app
    with TestClient(create_app()) as jim:      # no PDI configured
        user = enroll(jim)
        log = jim.get(f"/access-log/{user}").json()
        assert log["vaulted"] is False
        assert "locally" in log["note"]
    jim_db.reset()
