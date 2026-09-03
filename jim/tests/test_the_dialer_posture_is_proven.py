"""The dialer posture is proven.

`wired` is the configuration question; `standing` is the proof — the voice
door asked whether it answers, is keyed, has a number to ring from, can be
reached by the house's webhooks, and holds the same secret JIM does.
`transport_ready` is true only on a proven `ready`. The proof is cached
briefly, the probe door forces it, and a posture read never raises: a
status door that can take its page down is pointed the wrong way.
"""

from __future__ import annotations

from jim import dialer, telephony

from .conftest import enroll
from .fakevoice import FakeVoice, wire


def test_unwired_is_said_as_unwired(client):
    post = dialer.posture()
    assert post["wired"] is False and post["transport_ready"] is False
    assert post["standing"] is None and post["offline"] is False
    assert post["device_sim_wired"] is False
    assert post["send_enabled"] is False


def test_a_ready_door_proves_the_line(client, monkeypatch):
    fake = wire(monkeypatch)
    post = dialer.posture()
    assert post["wired"] is True and post["transport_ready"] is True
    st = post["standing"]
    assert st == {**st, "word": "ready", "reachable": True,
                  "provider_reported": "twilio", "from_number": True,
                  "webhooks": "reachable", "note": None, "fix": None,
                  "checked_at": "2026-09-03T00:00:00+00:00"}
    assert fake.standing_reads == 1


def test_a_door_that_is_not_ready_says_which_way(client, monkeypatch):
    wire(monkeypatch, word="no_from_number", note="VOICE_FROM is not set",
         fix="set VOICE_FROM to the number the house rings from")
    post = dialer.posture()
    assert post["wired"] is True and post["transport_ready"] is False
    assert post["standing"]["word"] == "no_from_number"
    assert post["standing"]["note"] == "VOICE_FROM is not set"
    assert post["standing"]["fix"].startswith("set VOICE_FROM")


def test_a_door_that_does_not_answer_names_the_address(client, monkeypatch):
    wire(monkeypatch, url="http://voice:8800", down=True)
    post = dialer.posture()                       # no raise
    assert post["transport_ready"] is False
    st = post["standing"]
    assert st["word"] == "unreachable" and st["reachable"] is False
    assert "http://voice:8800" in st["note"]
    assert "JIM_VOICE_URL" in st["fix"]


def test_a_house_keyed_for_another_provider_is_mismatched(client, monkeypatch):
    monkeypatch.setenv("JIM_TELEPHONY_PROVIDER", "vonage")
    wire(monkeypatch, provider="twilio")
    st = dialer.posture()["standing"]
    assert st["word"] == "mismatched"
    assert "keyed for twilio, not vonage" in st["note"]
    assert "JIM_TELEPHONY_PROVIDER" in st["fix"]


def test_a_secret_the_door_could_not_use_on_jim_is_a_mismatch(client, monkeypatch):
    wire(monkeypatch, jim_secret_accepted=False)
    st = dialer.posture()["standing"]
    assert st["word"] == "secret_mismatch"
    assert "JIM_VOICE_SECRET" in st["note"]


def test_a_door_that_refuses_jims_secret_is_a_mismatch(client, monkeypatch):
    wire(monkeypatch, refuse_secret=True)
    st = dialer.posture()["standing"]
    assert st["word"] == "secret_mismatch" and st["reachable"] is False
    assert "JIM_VOICE_SECRET" in st["fix"]


def test_offline_asks_the_door_nothing(client, monkeypatch):
    fake = wire(monkeypatch)
    monkeypatch.setenv("JIM_OFFLINE", "1")
    post = dialer.posture()
    assert post["offline"] is True and post["wired"] is False
    assert post["standing"] is None
    assert telephony.standing()["word"] == "held_offline"
    assert fake.seen == []


def test_the_device_path_is_unwired_not_proven(client, monkeypatch):
    fake = wire(monkeypatch)
    monkeypatch.setenv("JIM_TELEPHONY_KIND", "device_sim")
    post = dialer.posture()
    assert post["wired"] is False and post["device_sim_wired"] is False
    assert telephony.standing()["word"] == "unwired"
    assert fake.seen == []


def test_a_secret_without_an_address_is_unconfigured(client, monkeypatch):
    monkeypatch.setenv("JIM_VOICE_SECRET", "s3cret")
    st = telephony.standing()
    assert st["word"] == "unconfigured"
    assert "JIM_VOICE_URL" in st["fix"]


# --- the cache and the probe -------------------------------------------------------

def test_the_proof_is_believed_briefly(client, monkeypatch):
    fake = wire(monkeypatch)
    dialer.posture()
    dialer.posture()
    assert fake.standing_reads == 1
    telephony.standing(force=True)
    assert fake.standing_reads == 2


def test_the_probe_door_forces_the_proof(client, monkeypatch):
    uid = enroll(client)
    fake = wire(monkeypatch)
    dialer.posture()
    assert fake.standing_reads == 1
    r = client.post(f"/dialer/{uid}/probe")
    assert r.status_code == 200, r.text
    assert fake.standing_reads == 2
    # And the sidecar is told to check now too, not to answer from its cache.
    assert fake.forced_reads == 1
    assert r.json()["transport_ready"] is True
    assert r.json()["standing"]["word"] == "ready"
    # The read door answers the same shape.
    assert set(client.get(f"/dialer/{uid}/posture").json()) == set(r.json())


def test_the_probe_door_is_the_persons_own(client, monkeypatch):
    uid = enroll(client)
    wire(monkeypatch)
    r = client.post(f"/dialer/{uid}/probe", headers={"authorization": ""})
    assert r.status_code == 401
    enroll(client, display_name="Someone Else")    # the client is them now
    r = client.post(f"/dialer/{uid}/probe")
    assert r.status_code == 403


def test_the_standing_never_takes_the_page_down(client, monkeypatch):
    uid = enroll(client)
    wire(monkeypatch, down=True)
    r = client.get(f"/dialer/{uid}/posture")
    assert r.status_code == 200
    assert r.json()["standing"]["word"] == "unreachable"


def test_a_door_that_answers_nonsense_is_not_ready(client, monkeypatch):
    monkeypatch.setenv("JIM_VOICE_URL", "http://voice:8800")
    monkeypatch.setenv("JIM_VOICE_SECRET", "s3cret")
    telephony.forget_standing()
    monkeypatch.setattr(telephony, "_request",
                        lambda *a, **k: (200, {"detail": "<html>"}))
    st = telephony.standing()
    assert st["word"] != "ready"
    assert dialer.posture()["transport_ready"] is False


def test_the_fake_is_the_one_seam(monkeypatch):
    # FakeVoice replaces exactly telephony._request and nothing else.
    fake = FakeVoice(monkeypatch)
    assert telephony._request == fake._request
