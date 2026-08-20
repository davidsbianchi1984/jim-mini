"""The lookout grows ears.

The vault's `fetch.listen` (PDI 0.94) seals the words said in a
recording. This round points the lookout at it: planting a URL that *is*
a recording — the media file itself, not a page containing a player —
stands a listening appointment instead of a rendering one, under the
same capture key and change-memory, so everything downstream (the
read-back, the changed_at, the letter's line, the coach's prompt block)
reads a transcript exactly the way it reads a page.

    asked     can JIM keep an ear on a recording for somebody
    mattered  the same lookout, hearing where hearing is what the URL is

Honesty carries over unchanged: a deployment without ears fails the
cycle in words, and the lookout's `trouble` line — fed by the vault's
runs ledger — says why. There is no silent stand-in for hearing.
"""

from __future__ import annotations

from jim import db, letter, lookout

from .conftest import enroll
from .test_the_lookout import StandingVault, _allow_study, _plant


def test_a_recording_url_plants_a_listening_appointment(client):
    uid = enroll(client)
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(client, uid)
    out = _plant(client, uid, url="https://cdn.example/briefing.mp4")
    task = vault.standing[out["task_id"]]
    assert task["plan_steps"] == [
        {"tool": "fetch.listen",
         "args": {"url": "https://cdn.example/briefing.mp4"}}]


def test_the_suffix_is_read_from_the_path_not_the_query(client):
    """`?session=a.html` after an .mp3 is still a recording; an .html
    page that merely mentions media in its query is still a page."""
    uid = enroll(client)
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(client, uid)
    heard = _plant(client, uid,
                   url="https://cdn.example/town-hall.mp3?session=a.html")
    assert (vault.standing[heard["task_id"]]["plan_steps"][0]["tool"]
            == "fetch.listen")
    seen = _plant(client, uid,
                  url="https://example.com/schedule.html?video=talk.mp4")
    assert (vault.standing[seen["task_id"]]["plan_steps"][0]["tool"]
            == "fetch.render")


def test_a_page_still_gets_the_eyes(client):
    """A page containing a player is a page — the eyes render it; only a
    URL that is itself the media file gets the ears."""
    uid = enroll(client)
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(client, uid)
    out = _plant(client, uid, url="https://example.com/live-briefings")
    assert (vault.standing[out["task_id"]]["plan_steps"][0]["tool"]
            == "fetch.render")


def test_the_letter_calls_a_recording_what_it_is(client, monkeypatch):
    """A transcript's change is new words said, not a page edited — the
    letter's watching line says "watched recording", and an ordinary
    page keeps "watched page"."""
    uid = enroll(client)
    vault = StandingVault()
    client.app.state.pdi = vault
    _allow_study(client, uid)
    _plant(client, uid, url="https://cdn.example/briefing.mp4")
    now = db.utcnow()
    monkeypatch.setattr(lookout, "_capture", lambda pdi, tid: {
        "text": "Doors hold.", "transcribed": True,
        "changed_at": now, "fetched_at": now})
    lines = letter._watching_lines(
        uid, "2000-01-01T00:00:00+00:00", vault,
        "2999-01-01T00:00:00+00:00", live=False)
    assert lines == [f"watched recording https://cdn.example/briefing.mp4"
                     f" changed on {now[:10]}"]

    monkeypatch.setattr(lookout, "_capture", lambda pdi, tid: {
        "text": "A page.", "changed_at": now, "fetched_at": now})
    lines = letter._watching_lines(
        uid, "2000-01-01T00:00:00+00:00", vault,
        "2999-01-01T00:00:00+00:00", live=False)
    assert lines[0].startswith("watched page ")
