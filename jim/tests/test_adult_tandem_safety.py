"""Adult-mode tandem safety: JIM must never hand a minor (or unknown-age) user
to an age-restricted QRME specialist profile, and must fall back gracefully
rather than crash."""

import pytest
from fastapi.testclient import TestClient

from jim import db as jim_db


class _Resp:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class FakeQRMEProfile:
    """A QRME stand-in exposing a profile card (adult_mode/status) plus the two
    tandem endpoints. ``chat_calls`` records whether a handoff actually
    happened."""

    def __init__(self, adult_mode=True, status="active"):
        self.adult_mode = adult_mode
        self.status = status
        self.chat_calls = 0

    def post(self, path, json=None, headers=None):
        if path == "/interactors":
            return _Resp(201, {"id": "usr_qrme"})
        if path.endswith("/chat"):
            self.chat_calls += 1
            return _Resp(200, {"profile_message": {
                "content": "[QRME specialist] I'm here.",
                "status": "approved", "flag_reason": None}})
        return _Resp(404, {})

    def get(self, path, headers=None):
        if path.startswith("/profiles/"):
            return _Resp(200, {"id": path.split("/")[2],
                               "adult_mode": self.adult_mode,
                               "status": self.status})
        return _Resp(404, {})


def _app(fake, tmp_path, monkeypatch):
    monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
    monkeypatch.setenv("JIM_LLM", "stub")
    jim_db.reset()
    from jim.api import create_app
    from jim.qrme_client import QRMEClient
    c = TestClient(create_app(qrme_client=QRMEClient(client=fake)))
    c.__enter__()
    return c


def _enroll(client, birthdate):
    r = client.post("/enroll", json={
        "display_name": "U", "birthdate": birthdate, "terms_consent": True,
        "guardian_consent": True, "resting_heart_rate": 60, "plan": "pro"})
    body = r.json()
    client.headers["authorization"] = f"Bearer {body['user_token']}"
    return body["id"]


def _register_tandem(client):
    """Attach the tandem specialist, past the door's own standing check.

    `POST /specialists` now refuses a profile that could never answer, so
    that an attach cannot leave somebody believing in a link the delivery
    path only ever steps around. That gate is a good thing, and it is tested
    below in `test_the_attach_door_refuses_one_that_could_never_answer`.

    It is the wrong gate for *these* tests, and the reason is what they are
    about: a specialist does not usually depart before you attach them, it
    departs afterwards. The state modelled here is a link attached while the
    profile was healthy and gone bad since — so it is written the way that
    history leaves it, and the question is what delivery does then. Going
    through the door would test the door instead.
    """
    from jim import guardian
    guardian.register_specialist({
        "condition": "anxiety", "mode": "tandem",
        "qrme_profile_id": "prf_adult", "label": "QRME anxiety specialist"})


def _trigger(client, uid):
    return client.post(f"/monitor/{uid}", json={
        "heart_rate": 110, "respiratory_rate": 22}).json()


def test_minor_is_not_handed_to_an_adult_profile(tmp_path, monkeypatch):
    fake = FakeQRMEProfile(adult_mode=True)
    client = _app(fake, tmp_path, monkeypatch)
    uid = _enroll(client, "2015-01-01")          # a minor
    _register_tandem(client)
    r = _trigger(client, uid)

    assert r["detected"] and r["severity"] == "guidance"
    guidance = r["guidance"]
    assert fake.chat_calls == 0                    # no handoff happened
    assert guidance["source"] == "local"
    assert "age-restricted" in guidance["note"]
    client.__exit__(None, None, None)


def test_adult_is_handed_to_an_adult_profile(tmp_path, monkeypatch):
    fake = FakeQRMEProfile(adult_mode=True)
    client = _app(fake, tmp_path, monkeypatch)
    uid = _enroll(client, "1990-01-01")          # a verified adult
    _register_tandem(client)
    r = _trigger(client, uid)

    assert fake.chat_calls == 1                    # the handoff proceeded
    assert r["guidance"]["source"] == "tandem"
    client.__exit__(None, None, None)


def test_non_active_profile_falls_back(tmp_path, monkeypatch):
    fake = FakeQRMEProfile(adult_mode=False, status="restricted")
    client = _app(fake, tmp_path, monkeypatch)
    uid = _enroll(client, "1990-01-01")
    _register_tandem(client)
    r = _trigger(client, uid)

    assert fake.chat_calls == 0
    assert r["guidance"]["source"] == "local"
    assert "restricted" in r["guidance"]["note"]
    client.__exit__(None, None, None)


def test_departed_specialist_references_its_memorial(tmp_path, monkeypatch):
    fake = FakeQRMEProfile(adult_mode=False, status="departed")
    client = _app(fake, tmp_path, monkeypatch)
    uid = _enroll(client, "1990-01-01")
    _register_tandem(client)
    r = _trigger(client, uid)

    assert fake.chat_calls == 0
    guidance = r["guidance"]
    assert guidance["source"] == "local"       # help still arrives
    # ...and the note points the user at the specialist's memorial.
    assert "memorial" in guidance["note"]
    assert "/profiles/prf_adult/memorial" in guidance["note"]
    client.__exit__(None, None, None)


def test_non_adult_profile_handoff_unaffected(tmp_path, monkeypatch):
    fake = FakeQRMEProfile(adult_mode=False, status="active")
    client = _app(fake, tmp_path, monkeypatch)
    uid = _enroll(client, "2015-01-01")          # minor, but profile is not adult
    _register_tandem(client)
    r = _trigger(client, uid)

    assert fake.chat_calls == 1                    # safe: normal handoff
    assert r["guidance"]["source"] == "tandem"
    client.__exit__(None, None, None)


def test_the_attach_door_refuses_one_that_could_never_answer(tmp_path,
                                                             monkeypatch):
    """The other half of `_register_tandem`'s note.

    Everything above is about a link that went bad after it was made. This is
    the case the attach door can still catch: somebody choosing, right now, a
    profile that has already departed. Before this gate the attach succeeded,
    the bracket listed it as attached, and every delivery afterwards quietly
    took the fallback — a binding that was never a door.
    """
    fake = FakeQRMEProfile(adult_mode=False, status="departed")
    client = _app(fake, tmp_path, monkeypatch)
    r = client.post("/specialists", json={
        "condition": "anxiety", "mode": "tandem",
        "qrme_profile_id": "prf_adult", "label": "QRME anxiety specialist"})
    assert r.status_code == 422, r.text
    assert "departed" in r.json()["detail"]
    client.__exit__(None, None, None)


def test_an_age_restricted_specialist_attaches_and_is_gated_per_delivery(
        tmp_path, monkeypatch):
    """Adults-only is a caveat, not a refusal.

    Whether an age-restricted profile may be used depends on who is asking,
    and the attach bracket is not per-user — so the door lets it through and
    `_tandem_safe` holds the line at each delivery, which the minor case
    above already proves it does.
    """
    fake = FakeQRMEProfile(adult_mode=True, status="active")
    client = _app(fake, tmp_path, monkeypatch)
    r = client.post("/specialists", json={
        "condition": "anxiety", "mode": "tandem",
        "qrme_profile_id": "prf_adult", "label": "QRME anxiety specialist"})
    assert r.status_code == 200, r.text
    client.__exit__(None, None, None)
