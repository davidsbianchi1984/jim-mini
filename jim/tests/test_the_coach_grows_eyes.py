"""The coach grows eyes — show it a picture, a screenshot, your screen.

The owner's brief, across one evening: "Let's make our own then" (on a
video-watching plugin being sold on a feed), then "eyes that can read
screens both on mobile and computer", then "Agent, synthetic profiles,
coach, Jim-mini all grow eyes."

JIM already had eyes — :mod:`jim.sight`, the monitors' one-sentence
glance — so the coach's eye is the SAME eyes in a second posture:
``SHOWN``, fuller and with the readable text said, because a screenshot
is usually shown FOR its words, and on a phone that cannot hand a live
screen to a web page a screenshot IS the screen being shown. One wire,
two postures, and the frame is stored nowhere on either.
"""

from __future__ import annotations

import base64
from pathlib import Path

import pytest

from jim import sight
from jim.tests.conftest import enroll

REPO = Path(__file__).resolve().parents[2]
SIGHT = (REPO / "jim" / "sight.py").read_text()
COACH_TSX = (REPO / "app" / "src" / "screens" / "Coach.tsx").read_text()
API_TS = (REPO / "app" / "src" / "api.ts").read_text()

#: A one-pixel PNG — a real picture as far as the magic bytes go.
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGNgY"
    "GD4DwABBAEAX+XLSQAAAABJRU5ErkJggg==")


# -- the same eyes, two postures ----------------------------------------------

def test_one_wire_two_postures():
    """`describe` (the monitor's glance) and `read_shown` (the held-up
    picture) share the wire — a second HTTP client would be a second
    place for the credential rule to be forgotten."""
    assert "def _look(" in SIGHT
    assert SIGHT.count("api.openai.com") == 1, (
        "the eyes grew a second wire")
    assert "SHOWN" in SIGHT
    # Both postures keep the credential line.
    assert sight.SYSTEM.count("credential") == 1
    assert sight.SHOWN.count("credential") == 1
    # The glance stays one sentence; the shown picture gets read out.
    assert sight._SHOWN_ROOM > sight._GLANCE_ROOM


def test_the_eyes_know_their_pictures():
    assert sight.image_kind(PNG) == "image/png"
    assert sight.image_kind(b"\xff\xd8\xff\xe0rest") == "image/jpeg"
    assert sight.image_kind(b"RIFF????WEBPrest") == "image/webp"
    # RIFF is shared ground — a WAV is a recording, not a picture.
    assert sight.image_kind(b"RIFF????WAVErest") is None
    assert sight.image_kind(b"GIF89a") is None


def test_no_key_is_a_refusal_not_a_guess(monkeypatch):
    monkeypatch.delenv("JIM_SIGHT_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(sight.SightUnavailable):
        sight.read_shown(PNG, "image/png")


# -- the coach's door ---------------------------------------------------------

def test_junk_base64_is_refused(client):
    user = enroll(client)
    r = client.post(f"/coach/{user}",
                    json={"area": "career", "message": "look",
                          "shown": "not-base64!!!"})
    assert r.status_code == 422


def test_a_file_the_eyes_cannot_read_is_refused(client):
    user = enroll(client)
    r = client.post(f"/coach/{user}",
                    json={"area": "career", "message": "look",
                          "shown": base64.b64encode(b"%PDF-1.7 junk")
                                   .decode("ascii")})
    assert r.status_code == 422
    assert "JPEG, PNG and WebP" in r.json()["detail"]


def test_blind_deployment_says_so_out_loud(client, monkeypatch):
    """A coach that quietly ignores what it was shown is agreeing to a
    lie — the missing key is a 503 with the eyes' own sentence, never a
    reply that pretends the picture was seen."""
    monkeypatch.delenv("JIM_SIGHT_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    user = enroll(client)
    r = client.post(f"/coach/{user}",
                    json={"area": "career", "message": "look",
                          "shown": base64.b64encode(PNG).decode("ascii")})
    assert r.status_code == 503
    assert "nothing is set up to look" in r.json()["detail"]


def test_the_account_rides_with_the_words(client, monkeypatch):
    """Labelled for what it is, after the person's own words — and
    returned beside the reply so they can read exactly what the coach
    was told."""
    monkeypatch.setattr(sight, "read_shown",
                        lambda frame, kind="image/jpeg":
                        "a step counter reading 200 steps")
    user = enroll(client)
    r = client.post(f"/coach/{user}",
                    json={"area": "health_fitness",
                          "message": "is this enough walking?",
                          "shown": base64.b64encode(PNG).decode("ascii")})
    assert r.status_code == 200
    assert r.json()["seen"] == "a step counter reading 200 steps"


def test_an_ordinary_turn_carries_no_sighting(client):
    user = enroll(client)
    r = client.post(f"/coach/{user}",
                    json={"area": "career", "message": "interview prep?"})
    assert r.status_code == 200
    assert r.json()["seen"] is None


# -- the screen grew the doors ------------------------------------------------

def test_the_coach_screen_has_both_show_doors():
    for needle in ("cch.show.pic", "cch.show.screen", "showPick",
                   "getDisplayMedia", "reply.seen"):
        assert needle in COACH_TSX, f"the coach screen lost {needle}"
    assert "shown" in API_TS


def test_a_grab_is_a_frame_not_a_feed():
    grab = COACH_TSX.split("getDisplayMedia", 2)[-1]
    assert ".stop()" in grab[:1600], "the capture was left running"
