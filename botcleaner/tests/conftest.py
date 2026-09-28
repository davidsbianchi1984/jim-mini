import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("BOTCLEANER_SECRET", "test-secret-not-for-production")

from fastapi.testclient import TestClient  # noqa: E402

from botcleaner.api import create_app  # noqa: E402


@pytest.fixture
def app(tmp_path):
    return create_app(str(tmp_path / "t.sqlite3"), worker=False)


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def svc(app):
    return app.state.svc


@pytest.fixture
def user(client):
    r = client.post("/api/signup", json={"email": "me@example.com"})
    assert r.status_code == 200, r.text
    tok = r.json()["token"]
    return {"Authorization": f"Bearer {tok}", "_id": r.json()["user_id"]}


def hdr(u):
    return {k: v for k, v in u.items() if not k.startswith("_")}
