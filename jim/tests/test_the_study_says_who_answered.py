"""The study says who answered.

The excursion row was already the audit trail for what could have left —
the sanitized brief, the redaction count, `left_host`. What it could not
say was who wrote what came back: a study whose model degraded to the
stub, or whose vault turned out to be an older tandem, was recorded
exactly like one the chosen model answered.

    asked     which model was this study sent to
    mattered  which model actually wrote these findings

`answered_by` closes that gap with the letter's own honesty rules: the
name on the record is whoever wrote the words — the model's registry
name, `vault` for the resident, `stub` when a degrade or a keyless
machine left them to the local deterministic provider — read from the
provider that generated, duck-typed the way `generate_for_user` reads
it, never from the choice that was asked for.
"""

from __future__ import annotations

from jim import llm

from jim.tests.conftest import enroll
from jim.tests.test_the_voice_inside_the_vault import (DoorlessVault,
                                                       VoiceVault,
                                                       _choose_vault)


def _study(client, uid):
    r = client.post(f"/excursions/{uid}", json={
        "topic": "hydration",
        "question": "how much water does an older adult need daily",
    })
    assert r.status_code == 201, r.text
    return r.json()


class _Speaks:
    def generate(self, system, user):
        return "General notes on the topic."


class _Refuses:
    def generate(self, system, user):
        raise RuntimeError("expired key")


def test_the_local_study_is_named_stub(client):
    """No cloud, no keys: the deterministic provider answers, and the
    record names it as itself rather than leaving the reader to guess."""
    uid = enroll(client)
    exc = _study(client, uid)
    assert exc["answered_by"] == "stub"
    listed = client.get(f"/excursions/{uid}").json()
    assert listed[-1]["answered_by"] == "stub"


def test_a_models_study_carries_the_models_name(client, monkeypatch):
    uid = enroll(client)
    provider = llm.FallbackProvider("anthropic", _Speaks(),
                                    llm.StubProvider())
    monkeypatch.setattr(llm, "get_provider", lambda *a, **k: provider)
    exc = _study(client, uid)
    assert exc["answered_by"] == "anthropic"


def test_a_degraded_study_is_not_dressed_as_the_model(client, monkeypatch):
    """The point of the round: an expired key used to leave a row
    indistinguishable from one the chosen model wrote. The record now
    names the stub that actually answered."""
    uid = enroll(client)
    provider = llm.FallbackProvider("anthropic", _Refuses(),
                                    llm.StubProvider())
    monkeypatch.setattr(llm, "get_provider", lambda *a, **k: provider)
    exc = _study(client, uid)
    assert exc["answered_by"] == "stub"
    assert exc["findings"], "the degrade still brought findings home"


def test_the_vault_study_is_named_vault(client):
    uid = enroll(client)
    client.app.state.pdi = VoiceVault(text="Notes made inside the facility.")
    _choose_vault(client, uid)
    exc = _study(client, uid)
    assert exc["answered_by"] == "vault"
    assert exc["left_host"] is False


def test_an_older_tandem_is_not_dressed_as_the_vault(client):
    """A doorless PDI falls to the local provider — and the record calls
    that what it is, never the vault the person chose."""
    uid = enroll(client)
    client.app.state.pdi = DoorlessVault()
    _choose_vault(client, uid)
    exc = _study(client, uid)
    assert exc["answered_by"] == "stub"


def test_one_studys_author_does_not_describe_the_next(client, monkeypatch):
    """Two studies on one request context: the second gather's record
    replaces the first cleanly — cleared before, read after, put back."""
    uid = enroll(client)
    provider = llm.FallbackProvider("anthropic", _Speaks(),
                                    llm.StubProvider())
    monkeypatch.setattr(llm, "get_provider",
                        lambda *a, **k: provider)
    first = _study(client, uid)
    assert first["answered_by"] == "anthropic"
    monkeypatch.setattr(llm, "get_provider",
                        lambda *a, **k: llm.StubProvider())
    second = _study(client, uid)
    assert second["answered_by"] == "stub"
