"""Speaking and listening.

A Guardian you wear is one you talk to; typing at a wrist mid-panic is not a
plausible interaction. What matters here is that a missing service degrades
to the device's own voice rather than to silence, and that no recording is
ever written down.
"""

from __future__ import annotations

from jim import voice


def test_without_configuration_the_device_voice_is_the_answer(client):
    body = client.get("/settings/voice").json()
    assert body["provider"] == "device"
    assert body["device_fallback"] is True
    assert body["key_set"] is False
    # Speaking answers 503 — a signal to read it aloud locally, not an error
    # the person should ever see.
    r = client.post("/voice/speak", json={"text": "hello"})
    assert r.status_code == 503
    assert "device" in r.json()["detail"]


def test_male_voices_are_offered_for_each_speaking_provider():
    for provider in ("elevenlabs", "openai"):
        males = [v for v in voice.voices_for(provider) if v["gender"] == "male"]
        assert males, f"{provider} offers no male voice"
        assert all(v["id"] and v["name"] for v in males)


def test_configuring_a_provider_needs_a_key_and_never_returns_it(client):
    r = client.put("/settings/voice", json={"provider": "elevenlabs"})
    assert r.status_code == 422           # no key, no provider

    r = client.put("/settings/voice", json={
        "provider": "elevenlabs", "api_key": "sk-eleven-secret",
        "voice_id": "onwK4e9ZLuTAKqWW03F9"})
    assert r.status_code == 200, r.text
    body = client.get("/settings/voice").json()
    assert body["provider"] == "elevenlabs"
    assert body["key_set"] is True
    assert "sk-eleven-secret" not in str(body)
    assert body["voice_id"] == "onwK4e9ZLuTAKqWW03F9"


def test_speaking_returns_audio_from_the_configured_provider(client, monkeypatch):
    client.put("/settings/voice", json={
        "provider": "elevenlabs", "api_key": "sk-eleven-secret"})
    seen = {}

    def fake_urlopen(req, timeout=0):
        seen["url"] = req.full_url
        seen["key"] = req.headers.get("Xi-api-key")

        class R:
            headers = {"content-type": "audio/mpeg"}
            def read(self): return b"ID3-audio-bytes"
            def __enter__(self): return self
            def __exit__(self, *a): return False
        return R()

    monkeypatch.setattr(voice.urllib.request, "urlopen", fake_urlopen)
    r = client.post("/voice/speak", json={"text": "How are you feeling?"})
    assert r.status_code == 200, r.text
    assert r.content == b"ID3-audio-bytes"
    assert r.headers["content-type"].startswith("audio/")
    assert "text-to-speech" in seen["url"]
    assert seen["key"] == "sk-eleven-secret"


def test_a_refused_send_reports_what_the_service_said(client, monkeypatch):
    client.put("/settings/voice", json={
        "provider": "openai", "api_key": "sk-openai"})

    def refuse(text, voice_id=None):
        raise voice.VoiceError("openai refused it: HTTP 401 bad key")

    monkeypatch.setattr(voice, "speak", refuse)
    r = client.post("/voice/speak", json={"text": "hello"})
    assert r.status_code == 502
    assert "401" in r.json()["detail"]


def test_transcription_turns_speech_into_words(client, monkeypatch):
    import base64

    client.put("/settings/voice", json={
        "provider": "openai", "api_key": "sk-openai"})
    monkeypatch.setattr(voice, "transcribe",
                        lambda audio, filename="x": "my chest feels tight")
    r = client.post("/voice/transcribe", json={
        "audio_base64": base64.b64encode(b"webm-bytes").decode()})
    assert r.status_code == 200, r.text
    assert r.json()["text"] == "my chest feels tight"


def test_recorded_audio_is_never_written_down(client, monkeypatch):
    """The audio is sent to be recognised and kept nowhere."""
    import base64

    from jim import db

    client.put("/settings/voice", json={
        "provider": "openai", "api_key": "sk-openai"})
    monkeypatch.setattr(voice, "transcribe", lambda audio, filename="x": "hello")
    payload = base64.b64encode(b"secret-recording-bytes").decode()
    client.post("/voice/transcribe", json={"audio_base64": payload})
    dump = "\n".join(db.connect().iterdump())
    assert "secret-recording-bytes" not in dump
    assert payload not in dump


def test_rubbish_audio_is_refused_before_any_service_is_called(client):
    client.put("/settings/voice", json={
        "provider": "openai", "api_key": "sk-openai"})
    r = client.post("/voice/transcribe", json={"audio_base64": "not base64!!"})
    assert r.status_code == 422


def test_a_provider_whose_key_vanished_falls_back_to_the_device(client):
    """Configured for ElevenLabs, key later removed: the device voice answers
    rather than the app going mute."""
    client.put("/settings/voice", json={
        "provider": "elevenlabs", "api_key": "sk-eleven"})
    conn = __import__("jim.db", fromlist=["db"]).connect()
    conn.execute("UPDATE voice_settings SET api_key='' WHERE id=1")
    conn.commit()
    assert client.get("/settings/voice").json()["provider"] == "device"
