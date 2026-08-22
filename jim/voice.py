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
import time
import urllib.error
import urllib.request

from . import db

logger = logging.getLogger("jim.voice")

_TIMEOUT = int(os.environ.get("JIM_VOICE_TIMEOUT", "60"))

# ElevenLabs' public voice library. Male voices first because that is what
# this product is most often asked for; every one is selectable, and a
# custom voice id typed in by hand is honoured too.
#
# **Every id here has been spoken.** This list is a hand-copied set of
# opaque identifiers on somebody else's service: no amount of reading it
# proves an entry resolves, and the suite has no key, so nothing in this
# repo could ever have told us. Checked against a real account on
# 2026-08-14 by synthesising one line per voice — six answered and one did
# not. `VR6AewLTigWG4xSJukFG` ("Arnold") is gone from the library and
# answers 404 `voice_not_found`; it was offered in the picker on the
# console and all three phones, and choosing it produced a failure at the
# moment somebody asked to be spoken to.
#
#     asked     is the voice list well-formed
#     mattered  does every voice in it answer
#
# `test_the_voices_we_offer_are_voices_that_exist` re-runs that check when
# a key is present and skips when there is none, so this is verifiable
# again rather than verified once. Re-run it before adding a row.
ELEVEN_VOICES = [
    {"id": "onwK4e9ZLuTAKqWW03F9", "name": "Daniel", "gender": "male",
     "note": "warm, measured British — the default here"},
    {"id": "pNInz6obpgDQGcFmaJgB", "name": "Adam", "gender": "male",
     "note": "deep, steady American"},
    {"id": "TxGEqnHWrfWFTfGW9XjX", "name": "Josh", "gender": "male",
     "note": "younger, conversational American"},
    {"id": "pqHfZKP75CvOlQylNhV4", "name": "Bill", "gender": "male",
     "note": "steady, plain-spoken American"},
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
    # Stripped here as well as at the point of use, so the stored value is
    # clean rather than merely tolerated. See `_resolved`.
    api_key = (api_key or "").strip()
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


def _house_provider() -> str:
    """The provider a host key implies when nothing has been chosen.

    A deployment that sets ``ELEVENLABS_API_KEY`` is paying for the voice on
    behalf of everyone who opens the app, which was the whole point of a
    house key — and until this function existed the key was read and thrown
    away. ``_resolved`` defaulted the provider to ``device`` and then asked
    ``_env_key("device")``, which is empty by construction, so the branch
    that falls back to the device voice fired every time and the host key
    was never consulted.

        asked     is the environment key read
        mattered  does setting it turn the voice on

    Only ElevenLabs is inferred. ``OPENAI_API_KEY`` is the *language* key
    in :mod:`jim.llm` — a deployment that sets it is buying thinking, not
    speech, and inferring TTS from it would start spending somebody's
    tokens on audio they never asked for. Choosing OpenAI for speech stays
    an explicit act in Settings.
    """
    return "elevenlabs" if os.environ.get("ELEVENLABS_API_KEY", "") else "device"


def _resolved() -> dict:
    row = stored_settings() or {}
    provider = row.get("provider") or _house_provider()
    # Stripped at the point of use, not only where it is stored.
    #
    # A key with a newline on the end is not a bad key — it is a *paste*, and
    # it is what the ElevenLabs dashboard's copy button hands you. It went
    # into an HTTP header verbatim, and `http.client` refuses that with
    # `ValueError: Invalid header value`, which is not a `URLError` and so
    # went straight past both `except` clauses in `_subscription` and out of
    # the route as a 500 — the one shape a person can do nothing with.
    #
    #     asked     is the key a working key
    #     mattered  is the key even sendable
    #
    # Found in the field on the first night `/settings/voice/check` existed,
    # against a key saved from the console — which was the one client of four
    # that did not trim its input. The other three did, so this could only
    # ever have been reproduced the way it was.
    key = (row.get("api_key") or _env_key(provider) or "").strip()
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
        "voices": voices_for(r["provider"], r["api_key"]),
        # The device voice is always available: it is the operating system's
        # own, needs no account, and is what the app falls back to.
        "device_fallback": True,
    }


#: How long a fetched voice library is reused. Opening the Voice screen
#: should not be a request per render, and an account's voices change when
#: somebody makes one — minutes apart, not seconds.
_LIBRARY_TTL = 300.0
_library_cache: dict[str, tuple[float, list[dict]]] = {}


def _as_voice(v: dict) -> dict:
    """One of ElevenLabs' rows in the shape this product's pickers read.

    `gender` is taken from the labels the account itself set and left empty
    when there is none. Empty is a real answer here: a profile can be a
    device, a drawing or an idea, and the picker treats gender as a hint
    for sorting rather than a gate on who may choose what.

    `cloned` is the one that carries a rule. ElevenLabs marks a voice
    `cloned` when somebody enrolled a real person's voice, and
    `qrme/voiceprint.py` is emphatic about what that means: enrollment is
    owner-only and attested, and "there is no path here for enrolling a
    stranger, a celebrity, or a recording of somebody who never agreed".
    Listing every account voice to everybody would walk around that rule
    through the side door — a stranger's clone, picked from a dropdown —
    so the flag travels and the caller decides.
    """
    labels = v.get("labels") or {}
    gender = str(labels.get("gender") or "").strip().lower()
    note = ", ".join(
        str(labels[k]) for k in ("accent", "age", "description", "use case")
        if labels.get(k))
    return {
        "id": v.get("voice_id", ""),
        "name": v.get("name") or v.get("voice_id", ""),
        "gender": gender if gender in ("male", "female") else "",
        "note": note or str(v.get("description") or "").strip(),
        "cloned": v.get("category") in ("cloned", "professional"),
    }


def library(key: str = "") -> list[dict]:
    """The voices this account actually has, or the built-in seven.

    A field report, with the key entered and the picker open: "several
    names listed available, I don't see my name among them" — his own
    cloned voice. It could not have been there. `ELEVEN_VOICES` is a
    hand-copied set of public-library ids, and nothing in this product had
    ever asked the account what it holds, so a voice made on the dashboard
    was invisible here by construction.

        asked     is the voice list well-formed
        mattered  is it this account's list

    Falling back rather than failing is deliberate and is not the usual
    swallow: this list feeds the picker for the Guardian *speaking to
    somebody*, and a picker that empties itself because a provider is
    having an afternoon is worse than one showing a stale seven. A caller
    who needs to know the difference can compare against ELEVEN_VOICES.
    """
    key = (key or _env_key("elevenlabs") or "").strip()
    if not key:
        return ELEVEN_VOICES
    from . import offline
    if offline.enabled():
        return ELEVEN_VOICES
    now = time.monotonic()
    hit = _library_cache.get(key)
    if hit and now - hit[0] < _LIBRARY_TTL:
        return hit[1]
    url = "https://api.elevenlabs.io/v1/voices"
    try:
        offline.allow(url, "listing the voices on this account")
        req = urllib.request.Request(url, headers={"xi-api-key": key})
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            rows = (json.loads(resp.read() or b"{}") or {}).get("voices") or []
    except Exception:
        # Including a refused key: the picker is not where somebody finds
        # out their key is wrong — `check_key` says that in a sentence.
        return ELEVEN_VOICES
    voices = [_as_voice(v) for v in rows if v.get("voice_id")]
    if not voices:
        return ELEVEN_VOICES
    _library_cache[key] = (now, voices)
    return voices


def voices_for(provider: str, key: str = "") -> list[dict]:
    if provider == "elevenlabs":
        return library(key)
    if provider == "openai":
        return OPENAI_VOICES
    return []


def _subscription(key: str, purpose: str) -> dict:
    """ElevenLabs' account row: the allowance, the tier, and — because it
    answers 401 to a key it does not know — whether the key is a key.

    One call, no audio, no spend. Both callers below need exactly this.
    """
    url = "https://api.elevenlabs.io/v1/user/subscription"
    req = urllib.request.Request(url, headers={"xi-api-key": key})
    from . import offline
    offline.allow(url, purpose)
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            return json.loads(resp.read() or b"{}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")[:300]
        raise VoiceError(f"elevenlabs refused it: HTTP {exc.code} {detail}")
    except (urllib.error.URLError, TimeoutError) as exc:
        raise VoiceError(f"could not reach elevenlabs: {exc}")


#: What a key check can conclude, keyed the way `SPECIALIST_STANDING` is in
#: :mod:`jim.i18n` — the key travels on the wire so each client renders the
#: sentence from its own table, and the English lives here in one place.
KEY_VERDICTS: dict[str, str] = {
    "key.works":
        "that key works",
    "key.is_an_id":
        "that is the key's ID, not the key. The dashboard lists the ID "
        "beside every key, and shows the key itself once — when you create "
        "or rotate it. The one you want begins sk_ and is much longer",
    "key.refused":
        "the service did not accept that key",
    "key.unpaid":
        "the key works — the account behind it has an unpaid invoice. "
        "ElevenLabs stops serving until the latest one is settled, and "
        "nothing in this app can change that",
    "key.unchecked":
        "the key is saved, but nothing could be reached to check it — it "
        "will be tried the first time the Guardian speaks",
}


def verify() -> dict:
    """Ask the provider whether the stored key is a working key.

    ## The finding

    Saving a key answered the wrong question. `save_settings` writes the
    string and the console says **Saved.** — which is true, and says nothing
    about whether what was saved is a key. The first time anybody found out
    otherwise was at the moment they asked to be spoken to or listened to,
    several screens away from the field they typed it into, as a raw
    provider error:

        HTTP 400 {"detail":{"status":"api_key_id_used_as_api_key",
        "message":"key ID used as API key — only valid API keys can be
        used. API keys start with 'sk_' and are shown when the key is
        created or rotated."}}

    That is not a rare slip. ElevenLabs' dashboard shows the **key ID** in
    the list of keys, permanently and next to the name, and shows the key
    itself exactly once. The ID is therefore the string in front of you
    every time you go looking, and it is the wrong one — so the obvious
    action produces a deployment that is configured, reports itself
    configured, and cannot speak.

        asked     was the key saved
        mattered  is the saved key a key

    ## Why the check is the subscription call

    It costs nothing, sends no audio, and the provider is the only authority
    on its own keys. Checking the *shape* here instead would encode today's
    format as a rule and refuse tomorrow's — and would still have to guess
    at every other way a key can be wrong. The service is asked, and its
    answer is turned into a sentence naming what to do about it.

    Never raises for a refusal: a refusal is the answer this returns. The
    key is used and never returned.
    """
    r = _resolved()
    if r["provider"] == "device":
        raise VoiceUnavailable(
            "no speaking service is configured — there is no key to check")
    if r["provider"] != "elevenlabs":
        # OpenAI's key is checked by `jim.llm`'s own settings screen, and
        # this one has no cheap read that is certain to be permitted on a
        # key scoped to audio alone. Saying so beats a check that fails for
        # a reason unrelated to the key.
        raise VoiceUnavailable(
            f"{r['provider']} keys are not checked here — this check is the "
            "ElevenLabs account read")
    from . import offline
    try:
        _subscription(r["api_key"], "checking the speaking key")
    except offline.LeftTheHost:
        verdict = "key.unchecked"
    except VoiceError as exc:
        said = str(exc)
        # `payment_issue` is checked before the generic HTTP branch, and the
        # order is the whole point. ElevenLabs answers **401** to an unpaid
        # subscription — the same status as a bad credential — so a
        # classifier that only asks "was there an HTTP error" calls a
        # perfectly good key refused and tells its owner to paste it again.
        #
        #     asked     did the service say no
        #     mattered  did it say no to the key, or to the account
        #
        # Found in the field: the key authenticated, and the answer was
        # "subscription has a failed or incomplete payment". Advice to
        # replace that key would have sent somebody hunting a credential
        # that was never the problem.
        verdict = ("key.is_an_id" if "api_key_id_used_as_api_key" in said
                   else "key.unpaid" if ("payment_issue" in said
                                         or "payment_required" in said)
                   else "key.refused" if "HTTP" in said
                   else "key.unchecked")
    else:
        verdict = "key.works"
    return {
        "provider": r["provider"],
        "ok": verdict == "key.works",
        "checked": verdict != "key.unchecked",
        "verdict": verdict,
        "detail": KEY_VERDICTS[verdict],
    }


def remaining() -> dict:
    """How much speaking this account has left, from the provider itself.

    Nothing in this app read a quota until now, and the failure that hides
    is a quiet one: when an ElevenLabs allowance runs out the send answers
    HTTP 401 with ``quota_exceeded``, :func:`speak` raises
    :class:`VoiceError`, the route answers 502, and every client — console,
    iOS, Android, Windows — falls back to the device's own voice on any
    non-ok status. That fallback is correct and it is also silent. The
    Guardian keeps talking in a flatter voice and nobody is told why, so
    the person paying for the account finds out by noticing.

        asked     does a spent allowance still speak
        mattered  does anybody find out it was spent

    ElevenLabs publishes the numbers on ``/v1/user/subscription``. The one
    trap in that payload is the name: ``character_count`` is what has been
    *used*, not what is left, and reading it as a balance would show a
    fresh account with a large allowance as nearly out. What is left is
    ``character_limit - character_count``, floored at zero — a spent
    account can report a count above its limit.

    Raises :class:`VoiceUnavailable` when this deployment has no speaking
    provider, or has one that publishes no allowance; :class:`VoiceError`
    when the service is unreachable or refuses. The key is used and never
    returned.
    """
    r = _resolved()
    if r["provider"] == "device":
        raise VoiceUnavailable(
            "no speaking service is configured — the device's own voice has "
            "no allowance to run out")
    if r["provider"] != "elevenlabs":
        # OpenAI publishes no per-key balance: the usage endpoints it once
        # had are gone, and the billing figures live behind the dashboard's
        # own session rather than an API key. Saying so is better than
        # inventing a number or showing an empty line.
        raise VoiceUnavailable(
            f"{r['provider']} does not publish a remaining allowance — its "
            "balance is only visible on the provider's own dashboard")
    data = _subscription(r["api_key"], "reading the speaking allowance")
    used = int(data.get("character_count") or 0)
    limit = int(data.get("character_limit") or 0)
    left = max(0, limit - used)
    return {
        "provider": "elevenlabs",
        "tier": data.get("tier") or None,
        "status": data.get("status") or None,
        "used": used,
        "limit": limit,
        "left": left,
        # The question the screen is actually asking. An account with a
        # limit of zero has no allowance at all rather than a spent one,
        # and both of those mean the device voice answers from here.
        "exhausted": left <= 0,
        "resets_at": _reset_time(data.get("next_character_count_reset_unix")),
    }


def _reset_time(unix: object) -> str | None:
    """The allowance refills on a date, and a bare epoch integer on a screen
    is a number nobody can read. Returns UTC ISO-8601, or None when the
    provider did not say."""
    import datetime as _dt

    try:
        seconds = int(unix)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    if seconds <= 0:
        return None
    return (_dt.datetime.fromtimestamp(seconds, _dt.timezone.utc)
            .strftime("%Y-%m-%dT%H:%M:%SZ"))


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
    # Before the `try`, deliberately: the clauses below turn transport errors
    # into a `VoiceError` a screen shows, and a refusal swallowed into one
    # would read as the provider being unreachable rather than as nothing
    # being sent.
    from . import offline
    offline.allow(url, "speaking aloud")
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
    # Before the `try`, deliberately: the clauses below turn transport errors
    # into a `VoiceError` a screen shows, and a refusal swallowed into one
    # would read as the provider being unreachable rather than as nothing
    # being sent. The purpose names what actually leaves: recorded speech,
    # sent to be recognised — this line said "speaking aloud" for versions,
    # which described the other direction.
    from . import offline
    offline.allow(url, "transcribing recorded speech")
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
