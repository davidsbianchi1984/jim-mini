"""Speaking and listening.

A Guardian you wear is one you talk to; typing at a wrist mid-panic is not a
plausible interaction. What matters here is that a missing service degrades
to the device's own voice rather than to silence, and that no recording is
ever written down.
"""

from __future__ import annotations

import pytest

from jim import voice


def test_without_configuration_the_device_voice_is_the_answer(client,
                                                              monkeypatch):
    # Both keys cleared explicitly. A host that sets `ELEVENLABS_API_KEY` is
    # *meant* to turn the voice on — see the house-key test below — so this
    # one has to say which world it is asserting about rather than depending
    # on the developer's shell.
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
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


def _answers(payload: dict):
    """A stand-in for ElevenLabs' account read, at the urlopen boundary."""
    import json

    class R:
        def read(self): return json.dumps(payload).encode()
        def __enter__(self): return self
        def __exit__(self, *a): return False
    return lambda req, timeout=0: R()


def _refuses(status: int, body: bytes):
    import io
    import urllib.error

    def raise_it(req, timeout=0):
        raise urllib.error.HTTPError(req.full_url, status, "no", {},
                                     io.BytesIO(body))
    return raise_it


def test_a_host_key_turns_the_voice_on_for_everybody(client, monkeypatch):
    """A deployment that pays for the voice on everyone's behalf.

    `ELEVENLABS_API_KEY` was read and thrown away. `_resolved` defaulted the
    provider to ``device`` and then asked ``_env_key("device")``, which is
    empty by construction, so the branch that falls back to the device voice
    fired every time and the host key was never consulted. Setting it did
    nothing, silently, and the only symptom was a Guardian that kept using
    the device's own voice on a deployment that was paying not to.

        asked     is the environment key read
        mattered  does setting it turn the voice on
    """
    monkeypatch.setenv("ELEVENLABS_API_KEY", "sk_house")
    body = client.get("/settings/voice").json()
    assert body["provider"] == "elevenlabs"
    assert body["key_set"] is True
    assert body["key_source"] == "environment"
    assert body["voice_id"] == voice.DEFAULT_VOICE["elevenlabs"]
    assert "sk_house" not in str(body)


def test_a_language_key_does_not_become_a_speaking_key(client, monkeypatch):
    """Only ElevenLabs is inferred from the environment.

    ``OPENAI_API_KEY`` is the *language* key — `jim/llm.py` reads it to do
    the thinking. A deployment that sets it is buying reasoning, not speech,
    and inferring TTS from it would start spending somebody's tokens on
    audio they never asked for. Choosing OpenAI for speech stays explicit.
    """
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-language-only")
    assert client.get("/settings/voice").json()["provider"] == "device"


def test_the_allowance_is_what_is_left_not_what_was_spent(client, monkeypatch):
    """The provider's field is named for the wrong end of the subtraction.

    ``character_count`` is what has been *used*. Read as a balance — which
    is what the name invites — a fresh account with a large allowance shows
    as nearly out, and a spent one shows as full. So the route publishes
    `left`, already subtracted and floored at zero, because a spent account
    reports a count *above* its limit and a screen doing its own arithmetic
    would print a negative number.
    """
    client.put("/settings/voice", json={
        "provider": "elevenlabs", "api_key": "sk_eleven"})

    monkeypatch.setattr(voice.urllib.request, "urlopen", _answers({
        "tier": "creator", "character_count": 0, "character_limit": 100000,
        "next_character_count_reset_unix": 1788220800}))
    fresh = client.get("/voice/quota").json()
    assert fresh["left"] == 100000 and fresh["used"] == 0
    assert fresh["exhausted"] is False
    assert fresh["resets_at"] == "2026-09-01T00:00:00Z"

    # Spent, and over: the provider reports more used than the limit.
    monkeypatch.setattr(voice.urllib.request, "urlopen", _answers({
        "character_count": 100500, "character_limit": 100000}))
    spent = client.get("/voice/quota").json()
    assert spent["left"] == 0, "a floor at zero, not a negative balance"
    assert spent["exhausted"] is True


def test_nothing_reported_a_spent_allowance_until_this_route(client,
                                                             monkeypatch):
    """The quiet failure this route exists for.

    A spent allowance refuses the send, `speak` raises `VoiceError`, the
    route answers 502, and every client — console, iOS, Android, Windows —
    falls back to the device's own voice on any non-ok status. That fallback
    is right and it is also silent: the Guardian keeps talking in a flatter
    voice and the person paying finds out by noticing.

        asked     does a spent allowance still speak
        mattered  does anybody find out it was spent
    """
    client.put("/settings/voice", json={
        "provider": "elevenlabs", "api_key": "sk_eleven"})
    monkeypatch.setattr(voice.urllib.request, "urlopen", _refuses(
        401, b'{"detail":{"status":"quota_exceeded"}}'))
    # Speaking degrades — the old, silent behaviour, unchanged and correct.
    assert client.post("/voice/speak", json={"text": "hello"}).status_code == 502
    # And now it is also *sayable*, which is the whole of this round.
    assert client.get("/voice/quota").status_code == 502


def test_the_device_voice_has_no_allowance_to_run_out(client, monkeypatch):
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    r = client.get("/voice/quota")
    assert r.status_code == 503
    assert "device" in r.json()["detail"]
    # And the check has nothing to check.
    assert client.post("/settings/voice/check").status_code == 503


def test_a_key_that_is_not_a_key_is_named_at_the_moment_it_is_saved(
        client, monkeypatch):
    """The field bug David hit on the beta, driven from the boundary.

    Saving answered the wrong question. `save_settings` wrote the string and
    the console said **Saved.** — true, and silent about whether what was
    saved could speak. ElevenLabs' dashboard shows each key's **ID**
    permanently, beside its name, and shows the key itself exactly once, at
    creation; so the string in front of you whenever you go looking is the
    wrong one. Pasting it produced a deployment that was configured,
    reported itself configured, and answered this at the moment somebody
    asked to be spoken to, several screens from the field they typed into:

        HTTP 400 {"detail":{"status":"api_key_id_used_as_api_key", ...}}

        asked     was the key saved
        mattered  is the saved key a key

    The verdict is a key on the wire rather than a sentence, so each client
    renders it from its own ten-language table.
    """
    client.put("/settings/voice", json={
        "provider": "elevenlabs", "api_key": "3f9c2a7e1b"})

    monkeypatch.setattr(voice.urllib.request, "urlopen", _refuses(
        400, b'{"detail":{"status":"api_key_id_used_as_api_key","message":'
             b'"key ID used as API key - only valid API keys can be used. '
             b"API keys start with 'sk_' and are shown when the key is "
             b'created or rotated."}}'))
    body = client.post("/settings/voice/check").json()
    assert body["verdict"] == "key.is_an_id", (
        "the one refusal worth telling apart from any other 400 — it names "
        "an action the person can take")
    assert body["ok"] is False and body["checked"] is True
    assert "3f9c2a7e1b" not in str(body), "the key is used, never returned"

    # Any other refusal is still a refusal, and says so plainly.
    monkeypatch.setattr(voice.urllib.request, "urlopen",
                        _refuses(401, b'{"detail":"unauthorized"}'))
    assert client.post("/settings/voice/check").json()["verdict"] == "key.refused"

    # And a key the service accepts is confirmed, rather than assumed.
    monkeypatch.setattr(voice.urllib.request, "urlopen", _answers({
        "tier": "creator", "character_count": 10, "character_limit": 100000}))
    good = client.post("/settings/voice/check").json()
    assert good["verdict"] == "key.works" and good["ok"] is True


def test_every_verdict_a_key_check_can_reach_has_a_sentence():
    """`KEY_VERDICTS` is what each client renders from. A verdict the
    backend can return and no table has a row for is a blank line where an
    instruction should be."""
    for verdict, sentence in voice.KEY_VERDICTS.items():
        assert verdict.startswith("key."), verdict
        assert sentence and sentence[0].islower(), (
            f"{verdict}: these are read as a continuation of the sentence "
            "the screen already started, the way every other refusal in "
            "this product is")


def test_the_voices_we_offer_are_voices_that_exist():
    """Speak one line in every voice in the picker, when a key is here.

    `ELEVEN_VOICES` is a hand-copied set of opaque identifiers belonging to
    somebody else's service. Nothing that reads the list can tell whether an
    entry resolves — the shape is fine, the name is fine, and the id is a
    string either way — so every other test in this file passes over a voice
    that has been withdrawn from the library.

    That is not hypothetical: `VR6AewLTigWG4xSJukFG` ("Arnold") shipped in
    this list, was offered in the picker on the console and all three phones,
    and answers 404 `voice_not_found`. Choosing it failed at the one moment
    the feature exists for — somebody asking to be spoken to.

        asked     is the voice list well-formed
        mattered  does every voice in it answer

    Skipped without a key rather than mocked. A mock of ElevenLabs would
    answer 200 for Arnold too, which is exactly the reassurance that let this
    through; the only thing that settles it is the service saying so.
    """
    import os
    import urllib.error
    import urllib.request

    key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not key:
        pytest.skip("no ELEVENLABS_API_KEY — this one needs the real service")

    # Synthesised rather than looked up. A voice can be absent from the
    # workspace library and still speak, or present and still refuse, so the
    # only question worth asking the service is the one the product asks it:
    # say a word in this voice. Two syllables each, seven calls.
    import json
    missing = []
    for row in voice.ELEVEN_VOICES:
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{row['id']}",
            data=json.dumps({"text": "ok", "model_id": os.environ.get(
                "JIM_ELEVEN_MODEL", "eleven_turbo_v2_5")}).encode(),
            headers={"xi-api-key": key, "content-type": "application/json",
                     "accept": "audio/mpeg"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=60) as answer:
                if not answer.read(1):
                    missing.append(f"{row['name']} ({row['id']}): no audio")
        except urllib.error.HTTPError as exc:
            missing.append(f"{row['name']} ({row['id']}): {exc.code}")
    assert not missing, (
        "voices offered in the picker that the service does not have:\n    "
        + "\n    ".join(missing)
        + "\n  Somebody choosing one of these is refused at the moment they "
          "ask to be spoken to. Replace the row with a voice that answers.")
