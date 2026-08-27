"""A refused key is a key fact, not a transcription fact.

Field report, from a handheld mid-conversation: a red strip reading
`transcription refused it: HTTP 401 {"detail":{"type":"authentication_
error"...` — the provider's own JSON, raw, on a person's screen. The
401 is not about the recording; it is about the key, and the person
needs the switch: paste a fresh key on the Voice card, or fix the
deployment's. Every provider call in jim/voice.py now turns 401/403
into that sentence, translated, in both directions.
"""

from __future__ import annotations

import io
import urllib.error

import pytest

from jim import i18n, voice


def _http_error(code: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        "https://api.example.test", code, "nope", {},
        io.BytesIO(b'{"detail":{"type":"authentication_error"}}'))


def test_a_401_names_the_switch_not_the_json(monkeypatch):
    monkeypatch.setattr(voice, "_resolved",
                        lambda: {"provider": "elevenlabs", "api_key": "bad",
                                 "voice_id": "x", "model": "m"})
    def refuse(req, timeout=None):
        raise _http_error(401)
    monkeypatch.setattr(voice.urllib.request, "urlopen", refuse)
    with pytest.raises(voice.VoiceError) as caught:
        voice.transcribe(b"\x1aRIFF", "clip.webm")
    said = str(caught.value)
    assert "key was refused" in said, said
    assert "authentication_error" not in said, (
        "the provider's raw JSON reached the sentence a person reads")


def test_other_codes_keep_the_honest_status(monkeypatch):
    monkeypatch.setattr(voice, "_resolved",
                        lambda: {"provider": "elevenlabs", "api_key": "ok",
                                 "voice_id": "x", "model": "m"})
    def refuse(req, timeout=None):
        raise _http_error(429)
    monkeypatch.setattr(voice.urllib.request, "urlopen", refuse)
    with pytest.raises(voice.VoiceError) as caught:
        voice.transcribe(b"\x1aRIFF", "clip.webm")
    assert "HTTP 429" in str(caught.value)


def test_the_key_sentence_speaks_ten_languages():
    filled = i18n.fill(i18n.KEY_REFUSED, provider="elevenlabs")
    for lang in ("es", "fr", "de", "pt", "it", "ja", "zh", "hi", "ar"):
        localized = i18n.localize_detail(filled, lang)
        assert str(localized) != str(filled) or lang == "en", (
            f"the key refusal is English in {lang}")
