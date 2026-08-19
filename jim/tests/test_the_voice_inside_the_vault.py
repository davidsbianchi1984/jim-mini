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


class GroundedVault(VoiceVault):
    """A PDI with the ask door: retrieval and generation both inside."""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.asked: list[dict] = []

    def resident_ask(self, question, prefix=None, system=None):
        self.asked.append({"question": question, "prefix": prefix,
                           "system": system})
        return {"model": self.model, "text": self.text,
                "leaves_host": False,
                "drew_on": [f"{prefix}checkin/x1"] if prefix else []}


def test_the_coach_answers_grounded_in_the_vault(client):
    """Retrieval and generation both inside the facility: the vault ranks
    this person's own seals against the question and answers from them —
    the prefix is the per-person wall inside the shared tenant, and the
    provenance says the grounding actually happened."""
    uid = enroll(client)
    vault = GroundedVault()
    client.app.state.pdi = vault
    _choose_vault(client, uid)
    r = client.post(f"/coach/{uid}", json={
        "area": "health_fitness", "message": "can I train my shoulder"})
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["content"] == vault.text
    assert out["provenance"]["grounded_in_vault"] is True
    ask = vault.asked[-1]
    assert ask["question"] == "can I train my shoulder"
    assert ask["prefix"] == f"jim/{uid}/memory/"
    assert ask["system"], "the persona was dropped on the way to the vault"


def test_recall_steps_aside_when_the_vault_grounds(client):
    """The resident reads the same seals the client-side recall would —
    fetching the lines here too would say them twice."""
    uid = enroll(client)
    vault = GroundedVault()
    client.app.state.pdi = vault
    client.post(f"/checkin/{uid}", json={
        "mood": 3, "energy": 2, "note": "shoulder aches after the fall"})
    _choose_vault(client, uid)
    client.post(f"/coach/{uid}", json={
        "area": "health_fitness", "message": "can I train my shoulder"})
    assert "remembered from an earlier" not in vault.asked[-1]["system"], (
        "the lines were recalled client-side AND grounded vault-side")


def test_an_older_pdi_speaks_ungrounded_and_says_so(client):
    """A PDI with the voice door but not the ask door still speaks —
    ungrounded, and the provenance says so rather than pretending."""
    uid = enroll(client)
    vault = VoiceVault()          # has resident_infer, no resident_ask
    client.app.state.pdi = vault
    _choose_vault(client, uid)
    r = client.post(f"/coach/{uid}", json={
        "area": "health_fitness", "message": "hello there"})
    assert r.status_code == 200, r.text
    out = r.json()
    assert out["content"] == vault.text
    assert out["provenance"]["grounded_in_vault"] is False


# -- the study speaks with the same voice ------------------------------------

def _study(client, uid):
    r = client.post(f"/excursions/{uid}", json={
        "topic": "hydration",
        "question": "how much water does an older adult need daily",
    })
    assert r.status_code == 201, r.text
    return r.json()


def test_the_excursion_studies_inside_when_the_person_chose_the_vault(
        client):
    """The choice made for the coach is a choice about where this
    person's words are made — the study path gets no different answer.
    The brief goes to the resident, the cloud sees nothing, and
    left_host says so."""
    uid = enroll(client)
    vault = VoiceVault(text="About two litres a day, spread out.")
    client.app.state.pdi = vault
    _choose_vault(client, uid)

    calls = {"n": 0}

    class Cloud:
        def generate(self, system, prompt):
            calls["n"] += 1
            return "cloudy findings"
    client.app.state.cloud = Cloud()

    exc = _study(client, uid)
    assert exc["findings"] == "About two litres a day, spread out."
    assert exc["left_host"] is False, (
        "a brief answered inside the facility did not leave the host")
    assert calls["n"] == 0, "the cloud must see nothing"
    assert any("hydration" in p for p in vault.prompts)


def test_an_older_vault_studies_at_home_never_by_shipping_anyway(client):
    """The honest fallback for "never send it out" is a worse answer
    made at home — the deterministic local provider — not a better one
    made by quietly using the cloud after all."""
    uid = enroll(client)
    client.app.state.pdi = DoorlessVault()
    _choose_vault(client, uid)

    calls = {"n": 0}

    class Cloud:
        def generate(self, system, prompt):
            calls["n"] += 1
            return "cloudy findings"
    client.app.state.cloud = Cloud()

    exc = _study(client, uid)
    assert exc["findings"]
    assert exc["findings"] != "cloudy findings"
    assert exc["left_host"] is False
    assert calls["n"] == 0, "the cloud must see nothing"
