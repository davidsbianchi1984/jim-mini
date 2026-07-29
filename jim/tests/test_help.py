"""The help box: written directions about the app, and an honest hand-off."""

from jim.tests.conftest import client  # noqa: F401


def test_directions_are_written_and_matched(client):
    r = client.post("/help", json={"question": "where are my medications?"})
    assert r.status_code == 200
    out = r.json()
    assert "cabinet" in out["answer"] and out["ai"] is False


def test_beyond_the_app_hands_to_the_coach(client):
    out = client.post("/help", json={"question": "should I change careers?"}).json()
    assert "Coach" in out["answer"]


def test_topics_list_and_empty_question(client):
    assert len(client.get("/help/topics").json()["topics"]) >= 10
    out = client.post("/help", json={"question": ""}).json()
    assert "Ask where anything lives" in out["answer"]
