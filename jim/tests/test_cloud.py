"""Cloud Model Gateway: greater-model guidance with local fallback, and the
opt-in, anonymized contribution of guidance outcomes."""

import json

import pytest
from fastapi.testclient import TestClient

from jim import db as jim_db
from jim.cloud import CloudModelClient, CloudProvider
from jim.tests.conftest import _Resp, enroll


class FakeCloudHttp:
    def __init__(self, fail=False):
        self.fail = fail
        self.contributions = []

    def post(self, path, json=None, headers=None):
        if path == "/v1/generate":
            if self.fail:
                return _Resp(503, {})
            return _Resp(200, {"content": "[cloud:claude-fable-5] I'm here.",
                               "model": "claude-fable-5"})
        if path == "/v1/contributions":
            self.contributions.append(json)
            return _Resp(202, {"accepted": True})
        return _Resp(404, {})

    def get(self, path, headers=None):
        return _Resp(200, {"model": "claude-fable-5", "tier": "cloud"})


def test_cloud_provider_and_fallback():
    class LocalStub:
        def generate(self, system, user):
            return "[local] steady breaths"

    up = CloudProvider(CloudModelClient(token="t", client=FakeCloudHttp()),
                       fallback=LocalStub())
    assert up.generate("sys", "help") == "[cloud:claude-fable-5] I'm here."

    down = CloudProvider(
        CloudModelClient(token="t", client=FakeCloudHttp(fail=True)),
        fallback=LocalStub())
    assert down.generate("sys", "help") == "[local] steady breaths"


@pytest.fixture()
def cloud_pair(tmp_path, monkeypatch):
    monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
    monkeypatch.setenv("JIM_LLM", "stub")
    monkeypatch.delenv("JIM_QRME_URL", raising=False)
    jim_db.reset()
    from jim.api import create_app

    fake = FakeCloudHttp()
    with TestClient(create_app(
            cloud_client=CloudModelClient(token="cld", client=fake))) as c:
        yield c, fake
    jim_db.reset()


def test_guidance_outcome_contribution(cloud_pair):
    jim, fake = cloud_pair
    assert jim.get("/health").json()["cloud"] is True
    assert jim.get("/cloud/status").json()["model"]["model"] == "claude-fable-5"

    consenting = enroll(jim, cloud_contribution=True)
    jim.post(f"/monitor/{consenting}",
             json={"heart_rate": 120, "respiratory_rate": 22,
                   "note": "my chest is tight"})
    r = jim.post(f"/feedback/{consenting}", json={"rating": "up"}).json()
    assert r["contributed"] is True
    payload = fake.contributions[0]
    assert payload == {"source": "jim-mini", "kind": "guidance_outcome",
                       "condition": "anxiety", "severity": "guidance",
                       "rating": "up"}
    assert consenting not in json.dumps(payload)   # no user id
    assert "chest" not in json.dumps(payload)      # no notes

    # Without consent, nothing leaves.
    private = enroll(jim)
    jim.post(f"/monitor/{private}",
             json={"heart_rate": 120, "respiratory_rate": 22})
    r = jim.post(f"/feedback/{private}", json={"rating": "up"}).json()
    assert r["contributed"] is False
    assert len(fake.contributions) == 1
