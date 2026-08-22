"""The voices offered are this account's voices.

Field report, with the key entered and the picker open: "several names
listed available, I don't see my name among them" — his own cloned voice,
made on the ElevenLabs dashboard.

It could not have been there. `ELEVEN_VOICES` is a hand-copied set of
seven public-library ids, and nothing in this product had ever asked the
account what it holds. A voice made on the dashboard was invisible here by
construction, and the only way to use one was to paste its id by hand.

    asked     is the voice list well-formed
    mattered  is it this account's list

That also sharpens an earlier reading of a different symptom. When the
names rendered against a key that turned out to be wrong, the conclusion
drawn was "the names prove nothing about the key" — correct, and one step
short: they are a *static list*, so they render identically with no key at
all.

## Two rules this file exists to hold

**Gender is a hint, never a gate.** QRME's characters are not all human men
and women — they are devices, drawings, inventions, ideas — and
`qrme/seed.py` already carries a rule for a profile "whose brief states no
gender". A voice whose labels say nothing keeps an empty string, and empty
is a real answer rather than a reason to hide the row.

**A clone of a real person is not a generic voice.** `qrme/voiceprint.py`:
"Enrollment is owner-only and requires an explicit attestation that the
voice belongs to the person consenting. There is no path here for
enrolling a stranger, a celebrity, or a recording of somebody who never
agreed." Handing every account voice to everybody would walk around that
through the side door — a stranger's clone, chosen from a dropdown — so
the `cloned` flag travels with the row and the caller decides.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from jim import voice

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _no_cache():
    voice._library_cache.clear()
    yield
    voice._library_cache.clear()


# -- it asks the account -----------------------------------------------------

def test_a_key_makes_it_ask_rather_than_recite(monkeypatch):
    asked = {}

    class _Resp:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self):
            return json.dumps({"voices": [
                {"voice_id": "v1", "name": "David Bianchi",
                 "category": "cloned", "labels": {"gender": "male"}},
            ]}).encode()

    def _open(req, timeout=0):
        asked["url"] = req.full_url
        asked["key"] = req.headers.get("Xi-api-key")
        return _Resp()

    monkeypatch.setattr(voice.urllib.request, "urlopen", _open)
    got = voice.library("sk_real")
    assert asked["url"] == "https://api.elevenlabs.io/v1/voices"
    assert asked["key"] == "sk_real"
    assert [v["name"] for v in got] == ["David Bianchi"], (
        "the account's own voices did not reach the picker")


def test_a_cloned_voice_is_marked_as_one(monkeypatch):
    """The flag the caller needs to keep a person's clone from being worn
    by a stranger."""
    row = voice._as_voice({"voice_id": "v", "category": "cloned"})
    assert row["cloned"] is True
    assert voice._as_voice({"voice_id": "v", "category": "premade"})["cloned"] \
        is False


def test_a_voice_with_no_gender_keeps_none_and_is_still_offered():
    """A device, a drawing, an idea. Empty is a real answer, not a reason
    to drop the row."""
    row = voice._as_voice({"voice_id": "v", "labels": {"gender": "neutral"}})
    assert row["gender"] == ""
    assert row["id"] == "v"
    assert voice._as_voice({"voice_id": "v"})["gender"] == ""


def test_the_labels_become_the_note_a_person_reads():
    row = voice._as_voice({"voice_id": "v", "name": "N",
                           "labels": {"accent": "british", "age": "young"}})
    assert "british" in row["note"] and "young" in row["note"]


# -- and falls back rather than emptying -------------------------------------

def test_no_key_keeps_the_built_in_seven(monkeypatch):
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    assert voice.library("") == voice.ELEVEN_VOICES


def test_a_provider_having_an_afternoon_does_not_empty_the_picker(monkeypatch):
    """This list feeds the picker for the Guardian speaking to somebody. A
    picker that empties itself is worse than one showing a stale seven."""
    def _boom(req, timeout=0):
        raise OSError("elevenlabs is down")

    monkeypatch.setattr(voice.urllib.request, "urlopen", _boom)
    assert voice.library("sk_real") == voice.ELEVEN_VOICES


def test_an_empty_account_keeps_the_seven(monkeypatch):
    class _Resp:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self): return b'{"voices": []}'

    monkeypatch.setattr(voice.urllib.request, "urlopen",
                        lambda req, timeout=0: _Resp())
    assert voice.library("sk_real") == voice.ELEVEN_VOICES


def test_offline_never_reaches_the_provider(monkeypatch):
    """Offline mode means nothing leaves the host, and a voice picker is
    not an exception to that."""
    monkeypatch.setenv("JIM_OFFLINE", "1")

    def _boom(req, timeout=0):
        raise AssertionError("offline mode opened a socket for the picker")

    monkeypatch.setattr(voice.urllib.request, "urlopen", _boom)
    assert voice.library("sk_real") == voice.ELEVEN_VOICES


def test_the_answer_is_cached_so_a_screen_is_not_a_request_per_render(
        monkeypatch):
    calls = {"n": 0}

    class _Resp:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self):
            return b'{"voices": [{"voice_id": "v", "name": "One"}]}'

    def _open(req, timeout=0):
        calls["n"] += 1
        return _Resp()

    monkeypatch.setattr(voice.urllib.request, "urlopen", _open)
    voice.library("sk_real")
    voice.library("sk_real")
    assert calls["n"] == 1, "the picker asks the provider on every render"


def test_a_different_key_is_a_different_library(monkeypatch):
    """Cached per key, not globally: a person using their own key must not
    be shown the deployment's voices."""
    class _Resp:
        def __init__(self, name): self.name = name
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def read(self):
            return json.dumps({"voices": [
                {"voice_id": self.name, "name": self.name}]}).encode()

    monkeypatch.setattr(voice.urllib.request, "urlopen",
                        lambda req, timeout=0: _Resp(
                            req.headers.get("Xi-api-key")))
    assert voice.library("sk_a")[0]["name"] == "sk_a"
    assert voice.library("sk_b")[0]["name"] == "sk_b"


# -- the settings door hands the picker the real list ------------------------

def test_the_settings_view_passes_the_key_it_resolved():
    src = (REPO / "jim/voice.py").read_text(encoding="utf-8")
    assert 'voices_for(r["provider"], r["api_key"])' in src, (
        "the settings view still asks for voices without a key, so the "
        "picker recites the built-in seven however the account is set up")
