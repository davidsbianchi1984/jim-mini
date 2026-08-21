"""The screen is really seen.

`monitors.py` has promised since it was written that the screen monitor
can "see what is on your screen while you work", holding nothing — "what
it notices is offered and dropped". A field report read the roster
against a house where nothing was connected and named the gap: every row
said sensing, and nothing was sensing anything.

    asked     may JIM see this screen
    mattered  has it ever been shown one

For the wearables the missing half is hardware. For this one it never was:
the browser has had `getDisplayMedia` for years and this console had never
called it, and the server had no way to turn a picture into the words the
day is made of.

The load-bearing decision is *where* the describing happens. Half this
roster promises to keep nothing, and those promises only hold if the
noticing does not need the picture. So the frame is described on the
server, for the length of one request, and the sentence — not the frame —
is what reaches `daybook.sensed`, the cue reader, and the day.
"""

from __future__ import annotations

import base64
from pathlib import Path

import pytest

from jim import monitors, sight

from .conftest import enroll

REPO = Path(__file__).resolve().parents[2]
# A frame's worth of bytes. Never described in these tests — every path
# below either refuses before looking or has the looking monkeypatched,
# because a suite that reaches a vision provider is a suite that fails
# whenever somebody else's service is having an afternoon.
FRAME = base64.b64encode(b"\xff\xd8\xff\xe0jpeg-ish-frame-bytes").decode()


def _watching(client):
    uid = enroll(client)
    monitors.plug_in(uid, "screen")
    return uid


# -- the frame becomes words, and only words --------------------------------

def test_a_frame_is_described_and_the_sentence_is_what_lands(client,
                                                             monkeypatch):
    monkeypatch.setattr(sight, "describe",
                        lambda *a, **k: "a spreadsheet, and a cup of tea")
    uid = _watching(client)
    r = client.post(f"/monitors/{uid}/screen/sensed",
                    json={"frame_base64": FRAME})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["sensing"] is True
    # Offered — the person is looking at their own screen and asked for
    # this — and dropped, because the roster says this monitor keeps
    # nothing. Both halves in one answer.
    assert body["described"] == "a spreadsheet, and a cup of tea"
    assert body["kept"] is False


def test_the_frame_itself_reaches_no_table(client, monkeypatch):
    """The promise the whole design hangs on. If a frame could be stored,
    every `keeps: nothing` row in the roster would be a maybe."""
    from jim import db

    monkeypatch.setattr(sight, "describe", lambda *a, **k: "a login page")
    uid = _watching(client)
    client.post(f"/monitors/{uid}/screen/sensed", json={"frame_base64": FRAME})
    conn = db.connect()
    tables = [r["name"] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")]
    for table in tables:
        cols = [c["name"] for c in conn.execute(f"PRAGMA table_info({table})")]
        assert not [c for c in cols if "frame" in c or "image" in c], (
            f"{table} has somewhere to put a frame — the screen monitor's "
            "promise to keep nothing is one INSERT away from being false")


def test_the_words_are_dropped_too_on_a_monitor_that_keeps_nothing(
        client, monkeypatch):
    monkeypatch.setattr(sight, "describe", lambda *a, **k: "an email draft")
    uid = _watching(client)
    client.post(f"/monitors/{uid}/screen/sensed", json={"frame_base64": FRAME})
    day = client.get(f"/day/{uid}").json()
    kept = [m for m in day.get("kept", []) if m.get("monitor") == "screen"]
    assert kept == [], (
        "the screen monitor kept the description — its own row says it "
        "holds nothing")


# -- the refusals ------------------------------------------------------------

def test_a_screen_nobody_switched_on_is_not_looked_at(client, monkeypatch):
    monkeypatch.setattr(sight, "describe", lambda *a, **k: "anything at all")
    uid = enroll(client)                      # never plugged in
    r = client.post(f"/monitors/{uid}/screen/sensed",
                    json={"frame_base64": FRAME})
    assert r.status_code == 403


def test_a_moment_is_the_words_or_the_frame_but_not_both(client):
    """Two accounts of one moment is not a moment this product can
    honestly record, so it refuses rather than quietly preferring one."""
    uid = _watching(client)
    r = client.post(f"/monitors/{uid}/screen/sensed",
                    json={"frame_base64": FRAME, "content": "I typed this"})
    assert r.status_code == 422


def test_a_deployment_with_no_eyes_says_so(client):
    """No key, no guessing. An invented description would reach the cue
    reader, and a cue read out of a hallucination is an escalation
    nobody's day contained."""
    uid = _watching(client)
    r = client.post(f"/monitors/{uid}/screen/sensed",
                    json={"frame_base64": FRAME})
    assert r.status_code == 503, r.text
    assert "nothing is set up to look" in r.text


def test_rubbish_in_the_frame_field_is_refused(client):
    uid = _watching(client)
    r = client.post(f"/monitors/{uid}/screen/sensed",
                    json={"frame_base64": "not base64 at all!!"})
    assert r.status_code == 422


# -- the eyes themselves -----------------------------------------------------

def test_the_eyes_refuse_rather_than_guess_without_a_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("JIM_SIGHT_API_KEY", raising=False)
    assert sight.configured() is False
    with pytest.raises(sight.SightUnavailable):
        sight.describe(b"\xff\xd8\xff")


def test_a_caller_cannot_talk_the_eyes_out_of_their_limits():
    """`watching_for` narrows the looking. It is appended to the system
    sentence, never substituted for it, so no monitor can ask the eyes to
    read out a password by asking nicely."""
    src = (REPO / "jim/sight.py").read_text(encoding="utf-8")
    assert "told = SYSTEM +" in src, (
        "the caller's question replaces the eyes' own instructions instead "
        "of narrowing them")
    assert "credential" in sight.SYSTEM


# -- and the console actually looks -----------------------------------------

def test_the_console_calls_the_browsers_own_chooser():
    src = (REPO / "app/src/watching.ts").read_text(encoding="utf-8")
    assert "getDisplayMedia" in src, (
        "nothing in the console asks the browser for a screen — this is "
        "the gap the field report found")
    assert "audio: false" in src, (
        "a screen share that also grabs the system's sound is a different "
        "capture with a different consent")
    assert 'addEventListener("ended", stop)' in src, (
        "the browser's own stop-sharing bar must end the watching, or the "
        "console goes on believing it can see a screen it cannot")
    assert "looking" in src, (
        "without a one-in-flight guard a slow line becomes a backlog of "
        "stale pictures of somebody's screen")
