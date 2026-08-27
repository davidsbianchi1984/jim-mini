"""A meeting's recording arrives as words, and the roster decides.

The always-on ask, in its own words: *"watch every meeting you're in,
record every call... have perfect accounting and context of your life."*
Daybook wrote down what the literal version would need and could not
decide alone — the roster's promises rewritten, somewhere off-database
for bytes, an answer to two-party consent law. This is the version those
constraints leave standing:

    asked     record every call
    mattered  keep the WORDS of the calls whose monitor may keep, from a
              stretch somebody opened, having told the people in it —
              and never the audio, anywhere, for anyone

The bytes are transcribed on the way through (jim/voice.py holds the
same promise for every clip it hears) and the transcript enters the day
as an ordinary moment on the stretch's own monitor — so the keeping
switch, the others-told claim and every promise in the roster apply to a
meeting exactly as they do to any other sensed thing.
"""

from __future__ import annotations

from jim import db, voice

from jim.tests.conftest import enroll  # noqa: F401
from jim.tests.test_the_day_as_it_was_taken_in import _on


def _stretch(client, uid, monitor="room_speaker", **kw):
    from jim import monitors
    spec = monitors.MONITORS[monitor]
    r = client.post(f"/day/{uid}/stretches", json={
        "monitor": monitor, "about": "the standup",
        "others_told": spec.catches_others, **kw})
    assert r.status_code == 201, r.text
    return r.json()


def test_the_words_survive_as_the_monitor_promises(client, monkeypatch):
    monkeypatch.setattr(voice, "transcribe",
                        lambda audio, filename="x": "we agreed to ship friday")
    uid = enroll(client)
    _on(client, uid, "room_speaker", keeping=True)
    st = _stretch(client, uid)
    r = client.post(f"/day/{uid}/stretches/{st['id']}/heard",
                    content=b"\x1aFAKEWEBM")
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["kept"] is True
    assert out["stretch_id"] == st["id"]
    kept = client.get(f"/day/{uid}").json()["survived"]
    assert any(k["content"] == "we agreed to ship friday" for k in kept)


def test_keeping_off_drops_the_words_and_says_which_switch(client,
                                                           monkeypatch):
    monkeypatch.setattr(voice, "transcribe",
                        lambda audio, filename="x": "private words")
    uid = enroll(client)
    _on(client, uid, "room_speaker")
    st = _stretch(client, uid)
    out = client.post(f"/day/{uid}/stretches/{st['id']}/heard",
                      content=b"\x1aFAKEWEBM").json()
    assert out["kept"] is False
    assert out["dropped_because"] == "keeping_is_off"


def test_the_audio_bytes_are_stored_nowhere(client, monkeypatch):
    """The line daybook drew and this door keeps: it is not a recorder.
    After a recording lands, no table anywhere holds the bytes."""
    marker = b"\x1aNEVERSTOREDBYTES\x99"
    monkeypatch.setattr(voice, "transcribe",
                        lambda audio, filename="x": "the words only")
    uid = enroll(client)
    _on(client, uid, "room_speaker", keeping=True)
    st = _stretch(client, uid)
    client.post(f"/day/{uid}/stretches/{st['id']}/heard", content=marker)
    conn = db.connect()
    for (table,) in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'").fetchall():
        for row in conn.execute(f"SELECT * FROM {table}").fetchall():  # noqa: S608
            for value in tuple(row):
                if isinstance(value, bytes) and marker in value:
                    raise AssertionError(
                        f"the meeting's audio bytes landed in {table}")


def test_a_strangers_recording_is_refused(client, monkeypatch):
    monkeypatch.setattr(voice, "transcribe",
                        lambda audio, filename="x": "words")
    uid = enroll(client)
    _on(client, uid, "room_speaker", keeping=True)
    st = _stretch(client, uid)
    from jim.tests.conftest import user_header
    other = enroll(client)
    r = client.post(f"/day/{uid}/stretches/{st['id']}/heard",
                    content=b"\x1aX")
    # `other` is now the default caller; the stretch is `uid`'s.
    assert r.status_code in (403, 404), r.text


def test_no_ears_is_a_sentence_not_a_crash(client, monkeypatch):
    def refuse(audio, filename="x"):
        raise voice.VoiceUnavailable(
            "no listening service is configured — the app will use the "
            "device's own recogniser")
    monkeypatch.setattr(voice, "transcribe", refuse)
    uid = enroll(client)
    _on(client, uid, "room_speaker", keeping=True)
    st = _stretch(client, uid)
    r = client.post(f"/day/{uid}/stretches/{st['id']}/heard",
                    content=b"\x1aX")
    assert r.status_code == 503
