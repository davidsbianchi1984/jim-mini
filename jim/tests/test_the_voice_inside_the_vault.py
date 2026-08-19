"""The voice inside the vault: a coach that speaks through PDI.

PDI 0.88's `/resident/infer` puts the vault's local inference behind a
single door, and `vault` in the provider registry is JIM's side of it: a
person picks "The vault's local model" on the existing model screen and
the coach's words are generated on the facility's own inference server —
the prompt travels the one authenticated channel every seal uses and
goes no further, and PDI's audit line carries its length, never its
words.

    asked     can the coach speak from inside the building
    mattered  does the prompt ever leave it

Honesty rules mirror the QRME twin: a vault with no local model raises
rather than speaking the resident's operational stub sentence in the
coach's voice — the fallback hands the turn to this product's own stub
and `generate_for_user` discloses the degradation; an older tandem
without the voice door does the same; with no tandem the choice is
simply not configured, so a stored preference can never wedge a reply.
"""

from __future__ import annotations

from jim import llm

from jim.tests.conftest import enroll
from jim.tests.test_the_coach_remembers_through_the_vault import (
    FakeResidentVault)


class VoiceVault(FakeResidentVault):
    """A tandem with the voice door: records every prompt it was handed."""

    def __init__(self, model="local:llama3.2",
                 text="A short walk today beats a long one never taken."):
        super().__init__()
        self.model, self.text = model, text
        self.prompts: list[str] = []

    def resident_infer(self, prompt):
        self.prompts.append(prompt)
        return {"model": self.model, "text": self.text, "leaves_host": False}


class DoorlessVault(FakeResidentVault):
    """An older PDI: no /resident/infer, the client answers None."""

    def resident_infer(self, prompt):
        return None


def _choose_vault(client, uid):
    r = client.put(f"/model/{uid}", json={"provider": "vault"})
    assert r.status_code == 200, r.text
    return r.json()


def test_the_coach_speaks_through_the_vault(client):
    uid = enroll(client)
    vault = VoiceVault()
    client.app.state.pdi = vault
    chosen = _choose_vault(client, uid)
    assert chosen["effective"] == "vault"
    r = client.post(f"/coach/{uid}", json={
        "area": "health_fitness", "message": "how far should I walk today"})
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["content"] == vault.text
    assert out["provenance"]["generated_by"] == "vault"
    # The whole turn reached the facility, framed for a completion engine.
    assert "how far should I walk today" in vault.prompts[-1]
    assert vault.prompts[-1].endswith("You: ")


def test_the_models_list_carries_the_vault(client):
    client.app.state.pdi = VoiceVault()
    out = client.get("/models").json()
    row = next(p for p in out["providers"] if p["name"] == "vault")
    assert row["configured"] is True


def test_a_vault_with_no_model_degrades_honestly(client):
    """The resident's stub answers honestly on PDI's own console; in the
    coach's mouth it would be an operational message wearing a voice.
    The turn falls to this product's own stub, and the disclosure says
    who actually answered."""
    uid = enroll(client)
    client.app.state.pdi = VoiceVault(
        model="stub", text="No local model is installed on this host.")
    _choose_vault(client, uid)
    r = client.post(f"/coach/{uid}", json={
        "area": "health_fitness", "message": "hello there"})
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["content"]
    assert "No local model" not in out["content"]
    assert out["provenance"]["generated_by"] == "stub"


def test_an_older_tandem_without_the_door_falls_back_too(client):
    uid = enroll(client)
    client.app.state.pdi = DoorlessVault()
    _choose_vault(client, uid)
    r = client.post(f"/coach/{uid}", json={
        "area": "health_fitness", "message": "hello there"})
    assert r.status_code == 200, r.text
    assert r.json()["content"]


def test_no_tandem_means_the_choice_is_not_configured(client):
    client.app.state.pdi = None
    assert llm.is_configured("vault") is False
    assert llm.resolve_choice("vault") == llm.default_name()
