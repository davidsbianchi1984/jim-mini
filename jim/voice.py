"""Speaking and listening — the Guardian with a voice.

A health companion you wear is one you talk to. Typing at a wrist during a
panic attack is not a plausible interaction, and reading a paragraph of
guidance while short of breath is worse; the whole point of a Guardian that
notices something is that it can *say* so.

Two directions, each a small provider layer in the shape the rest of this
codebase already uses (see :mod:`jim.llm`, :mod:`jim.mailer`):

* **Speaking** (text → audio). **ElevenLabs** for the natural voices,
  including the male ones a lot of people prefer for this product;
  **OpenAI** (``tts-1``) as the alternative when somebody already has that
  key; **none** otherwise, in which case the app falls back to the voice
  built into the operating system — the browser's own speech synthesis,
  which costs nothing and needs no account.
* **Listening** (audio → text). **OpenAI Whisper** or **ElevenLabs**
  transcription when a key is present, and the browser's own recogniser
  otherwise. Audio is sent to be turned into words and is never stored:
  this module holds no recordings, and no route here writes one down.

Configuration lives with the deployment (``voice_settings``, one row), set
from the app's own Settings screen exactly like mail — because an
environment variable is not a thing a person installing a desktop app is
ever going to set.
"""

from __future__ import annotations

import base64
import json
import logging
import os
import urllib.error
import urllib.request

from . import db

logger = logging.getLogger("jim.voice")

_TIMEOUT = int(os.environ.get("JIM_VOICE_TIMEOUT", "60"))

# ElevenLabs' public voice library. Male voices first because that is what
# this product is most often asked for; every one is selectable, and a
# custom voice id typed in by hand is honoured too.
ELEVEN_VOICES = [
    {"id": "onwK4e9ZLuTAKqWW03F9", "name": "Daniel", "gender": "male",
     "note": "warm, measured British — the default here"},
    {"id": "pNInz6obpgDQGcFmaJgB", "name": "Adam", "gender": "male",
     "note": "deep, steady American"},
    {"id": "TxGEqnHWrfWFTfGW9XjX", "name": "Josh", "gender": "male",
     "note": "younger, conversational American"},
    {"id": "VR6AewLTigWG4xSJukFG", "name": "Arnold", "gender": "male",
     "note": "firm, direct"},
    {"id": "JBFqnCBsd6RMkjVDRZzb", "name": "George", "gender": "male",
     "note": "older, calm, unhurried"},
    {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Sarah", "gender": "female",
     "note": "soft, reassuring"},
    {"id": "XrExE9yKIg1WjnnlVkGX", "name": "Matilda", "gender": "female",
     "note": "warm, friendly"},
]

# OpenAI's fixed voice set (tts-1). onyx and echo are the male ones.
OPENAI_VOICES = [
    {"id": "onyx", "name": "Onyx", "gender": "male", "note": "deep, even"},
    {"id": "echo", "name": "Echo", "gender": "male", "note": "lighter, brisk"},
    {"id": "fable", "name": "Fable", "gender": "neutral", "note": "expressive"},
    {"id": "alloy", "name": "Alloy", "gender": "neutral", "note": "plain"},
    {"id": "nova", "name": "Nova", "gender": "female", "note": "bright"},
    {"id": "shimmer", "name": "Shimmer", "gender": "female", "note": "gentle"},
]

DEFAULT_VOICE = {"elevenlabs": "onwK4e9ZLuTAKqWW03F9", "openai": "onyx"}

PROVIDERS = ("elevenlabs", "openai", "device")


def stored_settings() -> dict | None:
    try:
        row = db.connect().execute(
            "SELECT * FROM voice_settings WHERE id=1").fetchone()
    except Exception:  # noqa: BLE001 — a database older than this table
        return None
    return dict(row) if row else None


def save_settings(provider: str, api_key: str = "", voice_id: str = "",
                  speak_replies: bool | None = None) -> dict:
    if provider not in PROVIDERS:
        raise ValueError(f"provider must be one of {', '.join(PROVIDERS)}")
    current = stored_settings() or {}
    if provider != "device" and not (api_key or current.get("api_key")
                                     or _env_key(provider)):
        raise ValueError(f"{provider} needs an API key")
    conn = db.connect()
    conn.execute(
        "INSERT INTO voice_settings (id, provider, api_key, voice_id,"
        " speak_replies, updated_at) VALUES (1,?,?,?,?,?)"
        " ON CONFLICT(id) DO UPDATE SET provider=excluded.provider,"
        " api_key=excluded.api_key, voice_id=excluded.voice_id,"
        " speak_replies=excluded.speak_replies, updated_at=excluded.updated_at",
        (provider, api_key or current.get("api_key", ""),
         voice_id or current.get("voice_id") or DEFAULT_VOICE.get(provider, ""),
         int(current.get("speak_replies", 1) if speak_replies is None
             else speak_replies),
         db.utcnow()),
    )
    conn.commit()
    logger.info("voice settings saved: provider=%s", provider)
    return describe_settings()


def clear_settings() -> dict:
    conn = db.connect()
    conn.execute("DELETE FROM voice_settings WHERE id=1")
    conn.commit()
    return describe_settings()


def _env_key(provider: str) -> str:
    return {
        "elevenlabs": os.environ.get("ELEVENLABS_API_KEY", ""),
        "openai": os.environ.get("OPENAI_API_KEY", ""),
    }.get(provider, "")


def _resolved() -> dict:
    row = stored_settings() or {}
    provider = row.get("provider") or "device"
    key = row.get("api_key") or _env_key(provider)
    if provider != "device" and not key:
        # Configured for a provider whose key has since gone: the device
        # voice still works, and silence would be the wrong failure.
        provider = "device"
    return {
        "provider": provider,
        "api_key": key,
        "voice_id": row.get("voice_id") or DEFAULT_VOICE.get(provider, ""),
        "speak_replies": bool(row.get("speak_replies", 1)),
    }


def describe_settings() -> dict:
    """What the API may say — never the key itself."""
    r = _resolved()
    row = stored_settings() or {}
    return {
        "provider": r["provider"],
        "voice_id": r["voice_id"],
        "speak_replies": r["speak_replies"],
        "key_set": bool(r["api_key"]),
        "key_source": ("environment" if not row.get("api_key") and r["api_key"]
                       else ("settings" if row.get("api_key") else "none")),
        "voices": voices_for(r["provider"]),
        # The device voice is always available: it is the operating system's
        # own, needs no account, and is what the app falls back to.
        "device_fallback": True,
    }


def voices_for(provider: str) -> list[dict]:
    if provider == "elevenlabs":
        return ELEVEN_VOICES
    if provider == "openai":
        return OPENAI_VOICES
    return []


def speak(text: str, voice_id: str | None = None) -> tuple[bytes, str]:
    """Turn ``text`` into audio. Returns ``(audio_bytes, media_type)``.

    Raises :class:`VoiceUnavailable` when this deployment has no speaking
    provider — the caller then lets the device's own voice read the text,
    which is a real answer rather than an error.
    """
    r = _resolved()
    if r["provider"] == "device":
        raise VoiceUnavailable(
            "no speaking service is configured — the app will use the "
            "device's own voice")
    voice = voice_id or r["voice_id"]
    if r["provider"] == "elevenlabs":
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
        body = json.dumps({
            "text": text,
            "model_id": os.environ.get("JIM_ELEVEN_MODEL", "eleven_turbo_v2_5"),
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
        }).encode()
        headers = {"xi-api-key": r["api_key"], "content-type": "application/json",
                   "accept": "audio/mpeg"}
    else:  # openai
        url = "https://api.openai.com/v1/audio/speech"
        body = json.dumps({
            "model": os.environ.get("JIM_OPENAI_TTS_MODEL", "tts-1"),
            "voice": voice or "onyx", "input": text,
        }).encode()
        headers = {"authorization": f"Bearer {r['api_key']}",
                   "content-type": "application/json"}
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            return resp.read(), resp.headers.get("content-type", "audio/mpeg")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:300]
        raise VoiceError(f"{r['provider']} refused it: HTTP {exc.code} {detail}")
    except (urllib.error.URLError, TimeoutError) as exc:
        raise VoiceError(f"could not reach {r['provider']}: {exc}")


def transcribe(audio: bytes, filename: str = "speech.webm") -> str:
    """Turn recorded speech into text. The audio is sent to be recognised
    and is never written down here."""
    r = _resolved()
    key = r["api_key"] or _env_key("openai")
    if not key:
        raise VoiceUnavailable(
            "no listening service is configured — the app will use the "
            "device's own recogniser")
    if r["provider"] == "elevenlabs":
        url = "https://api.elevenlabs.io/v1/speech-to-text"
        headers = {"xi-api-key": key}
        fields = {"model_id": "scribe_v1"}
    else:
        url = "https://api.openai.com/v1/audio/transcriptions"
        headers = {"authorization": f"Bearer {key}"}
        fields = {"model": os.environ.get("JIM_STT_MODEL", "whisper-1")}
    boundary = "----jim" + base64.urlsafe_b64encode(os.urandom(9)).decode()
    parts = []
    for name, value in fields.items():
        parts.append(f"--{boundary}\r\nContent-Disposition: form-data; "
                     f'name="{name}"\r\n\r\n{value}\r\n'.encode())
    parts.append(
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; "
        f'filename="{filename}"\r\nContent-Type: audio/webm\r\n\r\n'.encode())
    parts.append(audio)
    parts.append(f"\r\n--{boundary}--\r\n".encode())
    body = b"".join(parts)
    headers["content-type"] = f"multipart/form-data; boundary={boundary}"
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            data = json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:300]
        raise VoiceError(f"transcription refused it: HTTP {exc.code} {detail}")
    except (urllib.error.URLError, TimeoutError) as exc:
        raise VoiceError(f"could not reach the transcription service: {exc}")
    return (data.get("text") or "").strip()


class VoiceError(Exception):
    """The service was reachable in principle and said no."""


class VoiceUnavailable(Exception):
    """Nothing is configured — the device's own voice is the answer."""
