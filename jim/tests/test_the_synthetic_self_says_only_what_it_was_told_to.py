"""The one profile that is the user, and the boundary around what it hears.

`docs/tandem.md` carries the contract; `jim/synthetic_self.py` implements it.
This file is what stops the two from drifting apart, and most of it is aimed
at a single failure mode: a category crossing that nobody consented to, on a
profile that answers strangers.

    asked     does JIM reference synthetic profiles
    mattered  does JIM reference this person's own

The structural checks come first because they are the ones that survive
somebody adding a sixth category in a hurry. A driven test covers the five
that exist; only a check built from the module's own tables covers the next
one.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from jim import synthetic_self


class FakeQRME:
    """A QRME that answers about a profile and remembers what it was told."""

    def __init__(self, kind: str = "self", reachable: bool = True):
        self.kind = kind
        self.reachable = reachable
        self.posted: list[tuple] = []

    def profile_info(self, profile_id: str):
        if not self.reachable:
            return None
        return {"id": profile_id, "kind": self.kind, "display_name": "Ada"}

    def brief_self(self, profile_id: str, owner_token: str, brief: dict):
        self.posted.append((profile_id, owner_token, brief))
        return {"id": "src_1"}


@pytest.fixture()
def linked(client):
    """An enrolled user with their own self profile bound, nothing consented."""
    made = client.post("/enroll", json={
        "display_name": "Ada", "birthdate": "1950-03-01",
        "terms_consent": True})
    assert made.status_code == 201, made.text
    user = made.json()
    head = {"authorization": f"Bearer {user['user_token']}"}
    fake = FakeQRME()
    client.app.state.qrme = fake
    bound = client.post(f"/self-profile/{user['id']}", json={
        "profile_id": "prf_ada", "owner_token": "own_secret"}, headers=head)
    assert bound.status_code == 201, bound.text
    assert bound.json()["consented"] == [], (
        "a fresh link arrived with something already consented. Nothing "
        "crosses until the person has seen the brief and answered.")
    return user["id"], head, fake


# --- the boundary, checked structurally ------------------------------------

def test_every_category_has_a_builder_and_nothing_else_does():
    """The allowlist is the code path, not a filter over one.

    `CATEGORIES` is derived from the described set, and `_BUILD` is what can
    actually compose. A name in one and not the other is either a category the
    product offers and cannot produce, or — the dangerous direction — a builder
    that can produce something nobody described or consented to.
    """
    described = set(synthetic_self._BUILDERS)
    buildable = set(synthetic_self._BUILD)
    assert described == buildable, (
        f"described but not buildable: {sorted(described - buildable)}; "
        f"buildable but not described: {sorted(buildable - described)}")
    assert set(synthetic_self.CATEGORIES) == described


def test_the_categories_are_the_ones_the_contract_names():
    """The contract and the code, checked against each other.

    `docs/tandem.md` is byte-identical in three repositories and is where the
    decision about what may cross was written down. A category added to this
    module without being added there is a decision made in an implementation.
    """
    contract = (Path(__file__).resolve().parents[2] / "docs" / "tandem.md"
                ).read_text(encoding="utf-8")
    assert "The synthetic self" in contract, (
        "the tandem contract no longer describes the synthetic self, and this "
        "module implements a boundary nothing states")
    assert set(synthetic_self.CATEGORIES) == {
        "language", "wellbeing", "conditions", "medication", "continuity"}, (
        f"the allowlist is now {sorted(synthetic_self.CATEGORIES)}. Adding a "
        "category is a decision for docs/tandem.md first — in all three "
        "repositories — and then for this assertion.")


def test_there_is_no_builder_for_anything_a_person_wrote():
    """Journal entries, check-in notes and transcripts never cross.

    Not filtered out — *absent*. There is no code path that would carry them,
    which is the difference between a rule and a rule somebody has to remember.
    The one category made of the person's own words is `medication`, and it is
    named in the contract for exactly that reason.
    """
    forbidden = {"journal", "notes", "note", "checkin", "check_in",
                 "transcript", "conversation", "messages", "chat"}
    overlap = forbidden & set(synthetic_self.CATEGORIES)
    assert not overlap, (
        f"{sorted(overlap)} can now cross to a profile that answers "
        "strangers. Those are open fields whose contents nobody can predict.")


# --- the boundary, driven --------------------------------------------------

def test_nothing_crosses_before_somebody_has_answered(linked):
    """Empty is the default and a valid answer, and it refuses rather than
    sending `{}`: a request that says nothing still tells QRME this person
    exists and uses JIM."""
    user_id, head, fake = linked
    preview = _preview(linked)
    assert preview["brief"] == {} and preview["empty"] is True
    with pytest.raises(synthetic_self.SelfLinkError) as refused:
        synthetic_self.send(user_id, fake)
    assert refused.value.status == 409
    assert not fake.posted, "a brief was posted with nothing consented"


def _preview(linked):
    user_id, _, _ = linked
    return synthetic_self.preview(user_id)


def test_only_consented_categories_appear(client, linked):
    """The whole boundary in one assertion.

    Everything that could cross is present in the store — a medication, a
    language, a week's events — and only what was consented is in the brief.
    """
    user_id, head, fake = linked
    client.post(f"/meds/{user_id}", json={
        "name": "the little white one, 10 mg", "dose": "10 mg",
        "schedule": {"times": ["08:00"]}}, headers=head)
    client.put(f"/self-profile/{user_id}/consent",
               json={"categories": ["language"]}, headers=head)

    brief = synthetic_self.preview(user_id)["brief"]
    assert set(brief) == {"language"}, (
        f"the brief carried {sorted(brief)} on a consent set of ['language']")
    assert "the little white one, 10 mg" not in json.dumps(brief)


def test_medication_names_cross_only_under_their_own_consent(client, linked):
    """The category made of the person's own words.

    `meds.py` invites their wording — *"the little white one, 10 mg"* — so a
    name is free text, and a name can be a diagnosis: *"the pill for my HIV"*
    is one typed into a field asking for a drug. It crosses because the owner
    asked for it to, and only then, and the preview shows the string rather
    than a count of them so the decision is made with it visible.
    """
    user_id, head, fake = linked
    client.post(f"/meds/{user_id}", json={
        "name": "the pill for my HIV", "dose": "1 tablet",
        "schedule": {"times": ["21:00"]}}, headers=head)

    without = synthetic_self.preview(user_id)["brief"]
    assert "the pill for my HIV" not in json.dumps(without)

    client.put(f"/self-profile/{user_id}/consent",
               json={"categories": ["medication"]}, headers=head)
    shown = client.get(f"/self-profile/{user_id}/preview", headers=head).json()
    assert shown["brief"]["medication"]["names"] == ["the pill for my HIV"], (
        "the preview does not show the exact string that would be sent, so "
        "the person cannot see what they are agreeing to")

    sent = synthetic_self.send(user_id, fake)
    assert sent["brief"] == shown["brief"], (
        "the preview and the payload disagree. They are composed by the same "
        "function precisely so they cannot.")


def test_the_preview_is_the_payload(client, linked):
    """Composed by the code that sends, not described alongside it.

    A preview built separately is a preview free to drift from what goes, and
    that is the shape of every *we only share anonymous data* claim that turned
    out to be false.
    """
    user_id, head, fake = linked
    client.put(f"/self-profile/{user_id}/consent",
               json={"categories": list(synthetic_self.CATEGORIES)},
               headers=head)
    shown = client.get(f"/self-profile/{user_id}/preview", headers=head).json()
    client.post(f"/self-profile/{user_id}/brief", headers=head)
    assert fake.posted, "nothing was posted"
    assert fake.posted[-1][2] == shown["brief"]


def test_an_unknown_category_is_refused_not_dropped(client, linked):
    """Dropping it silently would let a client ask for something this module
    does not carry and be told yes."""
    user_id, head, _ = linked
    refused = client.put(f"/self-profile/{user_id}/consent",
                         json={"categories": ["language", "journal"]},
                         headers=head)
    assert refused.status_code == 422, refused.text
    assert synthetic_self.status(user_id)["consented"] == [], (
        "a refused consent set was partly applied")


# --- the link itself -------------------------------------------------------

def test_only_a_self_profile_may_be_linked(client):
    """A `fictional` profile briefed with somebody's medication schedule is a
    different product with the same code."""
    user = client.post("/enroll", json={
        "display_name": "B", "birthdate": "1960-01-01",
        "terms_consent": True}).json()
    head = {"authorization": f"Bearer {user['user_token']}"}
    client.app.state.qrme = FakeQRME(kind="fictional")
    refused = client.post(f"/self-profile/{user['id']}", json={
        "profile_id": "prf_f", "owner_token": "t"}, headers=head)
    assert refused.status_code == 409, refused.text


def test_an_unreachable_qrme_refuses_rather_than_assumes(client):
    """A link that cannot be verified might be to a fictional profile, and
    this is the one place where finding out later is too late."""
    user = client.post("/enroll", json={
        "display_name": "C", "birthdate": "1960-01-01",
        "terms_consent": True}).json()
    head = {"authorization": f"Bearer {user['user_token']}"}
    client.app.state.qrme = FakeQRME(reachable=False)
    refused = client.post(f"/self-profile/{user['id']}", json={
        "profile_id": "prf_x", "owner_token": "t"}, headers=head)
    assert refused.status_code == 404, refused.text


def test_unlinking_takes_the_credential_and_the_consent_with_it(client, linked):
    """Not a flag. A revoked link that keeps the owner token is a credential
    nobody is watching any more."""
    user_id, head, _ = linked
    client.put(f"/self-profile/{user_id}/consent",
               json={"categories": ["language"]}, headers=head)
    gone = client.delete(f"/self-profile/{user_id}", headers=head)
    assert gone.status_code == 200 and gone.json()["was_linked"] is True

    from jim import db
    rows = db.connect().execute(
        "SELECT COUNT(*) AS n FROM self_links WHERE user_id=?",
        (user_id,)).fetchone()
    assert rows["n"] == 0, "the row survived, and with it the owner token"
    assert synthetic_self.status(user_id)["consented"] == []


def test_relinking_starts_from_nothing_consented(client, linked):
    """Consent belongs to a link, not to a person.

    Pointing at a different profile and inheriting the old answers would brief
    a profile nobody agreed to brief.
    """
    user_id, head, _ = linked
    client.put(f"/self-profile/{user_id}/consent",
               json={"categories": ["medication"]}, headers=head)
    again = client.post(f"/self-profile/{user_id}", json={
        "profile_id": "prf_other", "owner_token": "own_2"}, headers=head)
    assert again.status_code == 201
    assert again.json()["consented"] == [], (
        "a new profile inherited the consent given for the previous one")


def test_the_brief_is_a_standing_and_not_a_history(client, linked):
    """Replaced on each brief, never accumulated.

    A self-profile briefed continuously would be a health record with a
    conversational interface, reachable by anyone the profile talks to.
    """
    user_id, head, fake = linked
    client.put(f"/self-profile/{user_id}/consent",
               json={"categories": ["wellbeing"]}, headers=head)
    for _ in range(3):
        client.post(f"/self-profile/{user_id}/brief", headers=head)
    assert len(fake.posted) == 3
    assert all(set(p[2]) == {"wellbeing"} for p in fake.posted), (
        "a brief grew as it was repeated")
    assert all(isinstance(p[2]["wellbeing"], str) for p in fake.posted)


def test_the_owner_token_is_what_is_sent(client, linked):
    """Not the interactor token `tandem_links` holds.

    The point of a self-profile is that it is not a stranger to them, and
    QRME's `POST /profiles/{id}/sources` is `require_owner` — an interactor
    token would be refused there, silently, on every brief.
    """
    user_id, head, fake = linked
    client.put(f"/self-profile/{user_id}/consent",
               json={"categories": ["language"]}, headers=head)
    client.post(f"/self-profile/{user_id}/brief", headers=head)
    assert fake.posted[-1][1] == "own_secret"
    assert fake.posted[-1][0] == "prf_ada"
