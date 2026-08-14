"""The free tier: the same Guardian, with the record in the clear.

Free and Basic reach exactly the same capabilities. Twenty dollars buys the
vault, not a feature — and that only works if "not private" is impossible to
miss and impossible to forget, so the disclosure is a field on every surface
that states a plan rather than a line in a Terms of Service.

Three tests here carry the weight, and all three are about somebody who is not
the person holding the card:

* `test_a_free_account_is_never_refused_an_emergency_write` — the reason the
  monitor samples are deliberately *not* on `SENSITIVE`. A storage rule that
  declined to write a blood oxygen of 84 is a paywall in front of an alarm
  wearing a privacy argument as a disguise. This repository already shipped
  that bug once as a tier gate and caught it in a test.
* `test_a_downgrade_off_basic_does_not_reopen_a_childs_record` — the bypass.
  Enrol the child on Basic, move to Free the next day, and without a check at
  the write the rule holds only for people who never changed their mind.
* `test_every_sensitive_kind_is_enforced_somewhere` — a payload named as too
  sensitive for the open store with nothing refusing it is a claim with no
  check behind it.
"""

import ast
import base64
import inspect
import pathlib

import pytest

from jim import capture, storage, tiers
from jim.tests.conftest import as_user, enroll, user_header


class FakeVault:
    def __init__(self):
        self.store: dict[str, str] = {}

    def put(self, key, value):
        self.store[key] = value

    def get(self, key):
        return self.store.get(key)

    def delete(self, key):
        return self.store.pop(key, None) is not None

    def audit(self):
        return [{"action": "put", "ref": k, "at": "2026-07-28T00:00:00Z"}
                for k in self.store]

    def audit_verify(self):
        return True


@pytest.fixture()
def vaulted(tmp_path, monkeypatch):
    """JIM with a PDI vault configured — the deployment a paying member has."""
    from fastapi.testclient import TestClient

    from jim import db as jim_db

    monkeypatch.setenv("JIM_DB", str(tmp_path / "jim-vaulted.db"))
    monkeypatch.setenv("JIM_LLM", "stub")
    monkeypatch.delenv("JIM_QRME_URL", raising=False)
    jim_db.reset()
    from jim.api import create_app

    with TestClient(create_app(pdi_client=FakeVault())) as c:
        yield c
    jim_db.reset()


def _jpeg() -> str:
    raw = (b"\xff\xd8\xff\xc0" + (11).to_bytes(2, "big")
           + b"\x08\x00\x10\x00\x10\x01\x01\x11\x00"
           + b"\xff\xda\x00\x08pixels\xff\xd9")
    return base64.b64encode(raw).decode()


# -- the difference Basic actually buys ----------------------------------------

def test_free_and_basic_reach_the_same_capabilities(client):
    """The product decision. A free tier crippled into uselessness teaches
    nobody anything about the product."""
    assert tiers.includes("free") == tiers.includes("basic")
    assert tiers.includes("free")            # and it is not empty


def test_what_differs_is_where_the_record_lives(client):
    assert storage.is_private("free") is False
    assert storage.is_private("basic") is True
    assert storage.is_private("pro") is True
    assert storage.posture_of("free") == "open_cloud"
    assert storage.posture_of("basic") == "vault"


def test_the_free_plan_costs_nothing_and_says_what_that_means(client):
    assert tiers.PLANS["free"]["price_usd"] == 0
    page = client.get("/plans").json()
    free = next(p for p in page["plans"] if p["plan"] == "free")
    assert free["storage"]["private"] is False
    assert free["storage"]["not_private"] is True
    assert "in the clear" in free["storage"]["disclosure"]
    assert "where your data lives" in page["the_difference"]


def test_the_open_posture_names_who_can_read_it(client):
    """Vagueness here would be the whole problem. "Industry-standard
    security" is what a product says when it does not want to finish the
    sentence."""
    described = storage.describe("free")
    readers = " ".join(described["who_can_read"]).lower()
    assert "operate this deployment" in readers
    assert "lawful access" in readers
    assert described["encrypted_at_rest"] is False
    assert described["you_hold_a_key"] is False


def test_a_paid_plan_carries_no_free_disclosure(client):
    assert storage.describe("basic")["disclosure"] is None
    assert storage.describe("pro")["refused_here"] == []


def test_the_order_runs_visitor_free_basic_pro(client):
    """The ladder is the ladder whatever the default is.

    `DEFAULT_PLAN` moved to Pro while the beta runs — both paid plans cost
    nothing during it, and somebody who never chose should be testing the
    whole product. The order it sits in did not move, and that is what this
    test is about; it asserts membership rather than a particular rung so
    the two questions stop being one.
    """
    assert tiers.ORDER == ("visitor", "free", "basic", "pro")
    assert tiers.DEFAULT_PLAN in tiers.ORDER
    assert tiers.DEFAULT_PLAN != "visitor"    # never the accountless rung


def test_every_plan_has_a_posture(client):
    """A plan with no entry would fall to open_cloud silently, which is the
    wrong direction to fail in."""
    for plan in tiers.ORDER:
        assert plan in storage.BY_PLAN, plan


# -- the disclosure is structural ----------------------------------------------

def test_a_free_membership_carries_its_posture(client):
    """A field, not a footnote."""
    user = enroll(client, plan="free")
    out = client.get(f"/memberships/{user}").json()
    assert out["storage"]["not_private"] is True
    assert "in the clear" in out["storage"]["disclosure"]


def test_the_disclosure_names_the_health_readings_by_name(client):
    """The free plan stores blood oxygen, seizure detections and alarm history
    in the clear. Burying that under "your data" would be the disclosure doing
    the opposite of its job."""
    text = storage.FREE_DISCLOSURE.lower()
    assert "health readings" in text
    assert "journal" in text
    assert "check-in" in text


def test_every_plan_in_the_catalogue_states_its_posture(client):
    page = client.get("/plans").json()
    for row in page["plans"]:
        assert "storage" in row, row["plan"]
        assert row["storage"]["posture"] in storage.POSTURES


def test_enrolling_without_a_plan_is_told_where_its_record_lives(client):
    """Whichever plan the default is, the posture arrives with it.

    The point has never been the word "free" — it is that nobody writes a
    line into this product without first being told, in the enrolment
    response, whether that line is sealed or in the clear. Read against
    `storage.describe` so this keeps holding when the default moves.
    """
    r = client.post("/enroll", json={
        "display_name": "Sam", "birthdate": "1990-01-01",
        "terms_consent": True, "resting_heart_rate": 60})
    assert r.status_code == 201, r.text
    out = r.json()["membership"]
    assert out["plan"] == tiers.DEFAULT_PLAN
    expected = storage.describe(tiers.DEFAULT_PLAN)
    assert out["storage"]["private"] is expected["private"]
    assert out["storage"]["disclosure"] == expected["disclosure"]


# -- the emergency path is never a storage decision ----------------------------

def test_a_free_account_is_never_refused_an_emergency_write(client):
    """The argument this whole module turns on.

    A blood oxygen of 84 is a critical reading. Free stores it in the clear —
    openly, and the disclosure says so — because the alternative is refusing
    to write it, and a storage refusal in front of an escalation is a paywall
    in front of an alarm however carefully it is reasoned.
    """
    user = enroll(client, plan="free", emergency_name="Pat",
                  emergency_phone="+1-555-0199", contact_consent=True)
    r = client.post(f"/monitor/{user}", json={"blood_oxygen": 84})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["severity"] == "critical"
    assert body["escalation"] is not None


def test_the_medical_readings_are_deliberately_not_on_the_sensitive_list(client):
    """Recorded here because it is the least obvious decision in the module
    and the easiest for a later reader to "fix"."""
    for tempting in ("biometric", "medical", "detection", "alarm",
                     "medical_id", "monitor"):
        assert tempting not in storage.SENSITIVE, (
            f"{tempting!r} on SENSITIVE would put a storage refusal in front "
            "of the emergency path")
    src = inspect.getsource(storage)
    assert "paywall in front of an alarm" in src


def test_a_free_membership_states_the_emergency_rule(client):
    user = enroll(client, plan="free")
    out = client.get(f"/memberships/{user}").json()
    assert "never withheld" in out["storage"]["emergency"]


# -- what the open store will not hold -----------------------------------------

def test_every_sensitive_kind_is_enforced_somewhere(client):
    """A kind named as too sensitive for the open store, with nothing actually
    refusing it, is a claim with no check behind it. This codebase has found
    that gap in itself repeatedly."""
    root = pathlib.Path(__file__).resolve().parent.parent
    body = "\n".join(p.read_text() for p in root.rglob("*.py")
                     if p.name != "storage.py" and "tests" not in p.parts)
    for kind in storage.SENSITIVE:
        assert f'"{kind}"' in body, (
            f"{kind!r} is listed as too sensitive for the open store and "
            "nothing outside storage.py refuses it")


def test_a_body_photograph_is_refused_on_free(client):
    user = enroll(client, plan="free")
    with pytest.raises(storage.StorageError) as exc:
        capture.take({"id": user, "birthdate": "1990-01-01"},
                     "photo", "forearm", _jpeg(), pdi=FakeVault())
    assert "photograph of somebody's body" in str(exc.value)


def test_the_same_photograph_is_fine_on_basic(client):
    user = enroll(client, plan="basic")
    out = capture.take({"id": user, "birthdate": "1990-01-01"},
                       "photo", "forearm", _jpeg(), pdi=FakeVault())
    assert out["id"]


def test_the_route_answers_402_and_stores_nothing(vaulted):
    """Through HTTP, on a deployment that *does* have a vault — otherwise the
    503 below would answer first and this would pass for the wrong reason."""
    user = enroll(vaulted, plan="free")
    r = vaulted.post(f"/users/{user}/captures", json={
        "kind": "photo", "site": "forearm", "content": _jpeg()})
    assert r.status_code == 402, r.text
    assert r.json()["reason"] == "storage_posture"
    assert r.json()["emergency_unaffected"] is True
    assert vaulted.get(f"/users/{user}/captures").json() == []


def test_the_same_route_answers_201_on_basic(vaulted):
    user = enroll(vaulted, plan="basic")
    r = vaulted.post(f"/users/{user}/captures", json={
        "kind": "photo", "site": "forearm", "content": _jpeg()})
    assert r.status_code == 201, r.text


def test_a_missing_vault_is_reported_before_a_price(client):
    """In a deployment with no PDI at all, telling somebody on Free to pay $20
    for the vault sells what this deployment cannot deliver — Basic would seal
    it in a vault that does not exist. The deeper cause is said first."""
    user = enroll(client, plan="free")
    with pytest.raises(capture.VaultRequired):
        capture.take({"id": user, "birthdate": "1990-01-01"},
                     "photo", "forearm", _jpeg(), pdi=None)


def test_a_minors_intimate_site_is_refused_before_any_price(client):
    """A hard line is never answered with a price. QRME hit this exact
    ordering bug and it is asserted here so this module cannot repeat it."""
    user = enroll(client, plan="free", birthdate="2014-03-02",
                  guardian_consent=True)
    with pytest.raises(capture.CaptureError) as exc:
        capture.take({"id": user, "birthdate": "2014-03-02"},
                     "photo", "genital", _jpeg(), pdi=FakeVault(),
                     intimate_consent=True)
    assert not isinstance(exc.value, storage.StorageError)
    assert "under any circumstance" in str(exc.value)


# -- a child's record --------------------------------------------------------

def _guardian_with_child(client, plan):
    guardian = enroll(client, plan=plan, birthdate="1985-04-04")
    r = client.post(f"/guardians/{guardian}/children", json={
        "display_name": "Robin", "birthdate": "2014-03-02",
        "relationship": "parent"})
    return guardian, r


def test_a_child_cannot_be_enrolled_onto_the_open_store(client):
    """The sharpest case in the product. The child did not pick the plan,
    cannot read a pricing page, and will be an adult one day with a medical
    history somebody else left in the clear."""
    guardian, r = _guardian_with_child(client, "free")
    assert r.status_code == 402, r.text
    assert "did not pick this plan" in r.json()["detail"]


def test_the_refusal_leaves_no_half_enrolled_child(client):
    """Checked before the account is created, so nothing is left behind — no
    orphan user, no link, no consent event."""
    guardian, r = _guardian_with_child(client, "free")
    assert r.status_code == 402
    assert client.get(f"/guardians/{guardian}/children").json() == []


def test_a_child_enrols_normally_on_basic(client):
    guardian, r = _guardian_with_child(client, "basic")
    assert r.status_code == 201, r.text
    assert len(client.get(f"/guardians/{guardian}/children").json()) == 1


def test_a_downgrade_off_basic_does_not_reopen_a_childs_record(client):
    """The bypass, and the reason the enrolment check is not enough on its
    own: enrol on Basic, move to Free the next day, and the rule would hold
    only for people who never changed their mind. One API call."""
    guardian, r = _guardian_with_child(client, "basic")
    assert r.status_code == 201, r.text
    child = r.json()["id"]
    child_token = r.json()["child_token"]

    tiers.subscribe(guardian, "free")
    as_user(client, child_token)
    out = client.post(f"/journal/{child}", json={"text": "felt dizzy today"})
    assert out.status_code == 402, out.text
    assert "did not pick this plan" in out.json()["detail"]


def test_the_child_can_still_raise_an_alarm_after_that_downgrade(client):
    """The line the guard must not cross. Everyday writing stops; calling for
    help does not."""
    guardian, r = _guardian_with_child(client, "basic")
    child = r.json()["id"]
    tiers.subscribe(guardian, "free")

    as_user(client, r.json()["child_token"])
    out = client.post(f"/monitor/{child}", json={"blood_oxygen": 84})
    assert out.status_code == 200, out.text
    assert out.json()["severity"] == "critical"


def test_the_guard_covers_the_diary_and_not_the_medical_stream(client):
    """Named explicitly, because "add a check to every write" is the change
    that would quietly reintroduce the paywall-in-front-of-an-alarm bug."""
    tree = ast.parse(pathlib.Path(inspect.getsourcefile(tiers)).read_text())
    assert any(isinstance(n, ast.FunctionDef)
               and n.name == "guard_dependant_write" for n in tree.body)

    from jim import guardian as guardian_mod
    assert "guard_dependant_write" not in inspect.getsource(
        guardian_mod._event), (
        "the medical event stream is the emergency path; a storage refusal "
        "there is a paywall in front of an alarm")


def test_an_adult_on_free_writes_their_own_journal_freely(client):
    """The guard is about *whose* exposure it is. Your own record on the open
    store is yours to choose."""
    user = enroll(client, plan="free")
    r = client.post(f"/journal/{user}", json={"text": "slept badly"})
    assert r.status_code in (200, 201), r.text


def test_a_childs_plan_resolves_to_the_guardians(client):
    """A child account has no card and no membership. Resolving to its own
    would return "visitor", collapse the posture to open cloud, and refuse a
    parent on Basic the ability to photograph their child's rash — exactly
    backwards, since the vault is what they paid for."""
    guardian, r = _guardian_with_child(client, "basic")
    child = r.json()["id"]
    assert tiers.plan_of(child) == "visitor"
    assert tiers.governing_plan(child) == "basic"


def test_a_guardian_on_basic_can_photograph_their_childs_rash(client):
    guardian, r = _guardian_with_child(client, "basic")
    child = r.json()["id"]
    out = capture.take({"id": child, "birthdate": "2014-03-02"},
                       "photo", "forearm", _jpeg(), pdi=FakeVault())
    assert out["id"]


# -- moving between plans ------------------------------------------------------

def test_a_downgrade_never_unseals_anything(client):
    """A billing event that declassified a year of somebody's medical history
    would be the worst thing this module could do."""
    effect = storage.downgrade_effect("pro", "free")
    assert effect["existing_stays_sealed"] is True
    assert effect["new_content_in_the_clear"] is True
    assert "does not declassify your history" in effect["note"]


def test_the_downgrade_helper_performs_nothing(client):
    """It states the rule rather than enacting it — no write, no move."""
    src = inspect.getsource(storage.downgrade_effect)
    for verb in ("INSERT", "UPDATE", "DELETE", "put(", "connect("):
        assert verb not in src, f"downgrade_effect does {verb!r}"


def test_an_upgrade_does_not_un_expose_what_was_already_open(client):
    """Sealing content afterwards protects it from here on. A product that
    implied otherwise would be selling absolution rather than encryption."""
    effect = storage.upgrade_effect("free", "basic")
    assert effect["new_content_sealed"] is True
    assert effect["existing_content_sealed"] is False
    assert "does not un-expose it" in effect["note"]
    assert "Backups" in effect["note"] or "backups" in effect["note"]


def test_moving_between_two_private_plans_changes_nothing(client):
    for effect in (storage.upgrade_effect("basic", "pro"),
                   storage.downgrade_effect("pro", "basic")):
        assert "nothing changes" in effect["note"]


# -- the ladder ----------------------------------------------------------------

def test_a_free_account_still_reaches_the_guardian(client):
    """The point of the tier. If free cannot use the Guardian it is not a free
    version of this product, it is a brochure."""
    user = enroll(client, plan="free")
    r = client.post(f"/monitor/{user}", json={"heart_rate": 72})
    assert r.status_code == 200, r.text
    assert client.post(f"/habits/{user}",
                       json={"name": "walk"}).status_code in (200, 201)


def test_free_is_still_refused_the_paid_capabilities(client, monkeypatch):
    """With the gate enforcing — see `tiers.BETA_EVERYTHING_INCLUDED`.

    The beta stands enforcement down for everybody, which is a posture and
    not a change to what the plans mean. This test is about what Free is
    entitled to, so it asks the question the product will ask again the day
    the beta ends.
    """
    monkeypatch.setattr(tiers, "BETA_EVERYTHING_INCLUDED", False)
    user = enroll(client, plan="free")
    r = client.post(f"/devices/{user}", json={"kind": "watch",
                                              "label": "Wrist"})
    assert r.status_code == 402, r.text
    assert r.json()["detail"]["needs"] == "pro"


# -- platform custody: free never reaches the vault ----------------------------

class CountingVault(FakeVault):
    """A vault that records every write, so a test can assert there were none."""

    def __init__(self):
        super().__init__()
        self.writes: list[str] = []

    def put(self, key, value):
        self.writes.append(key)
        return super().put(key, value)


@pytest.fixture()
def counted(tmp_path, monkeypatch):
    """JIM with a vault that counts writes — a PDI-backed deployment."""
    from fastapi.testclient import TestClient

    from jim import db as jim_db

    monkeypatch.setenv("JIM_DB", str(tmp_path / "jim-counted.db"))
    monkeypatch.setenv("JIM_LLM", "stub")
    monkeypatch.delenv("JIM_QRME_URL", raising=False)
    jim_db.reset()
    from jim.api import create_app

    vault = CountingVault()
    with TestClient(create_app(pdi_client=vault)) as c:
        c.vault = vault
        yield c
    jim_db.reset()


def _exercise(client, user):
    """Everything an ordinary day writes. Each of these used to seal."""
    client.post(f"/monitor/{user}", json={"heart_rate": 72})
    client.post(f"/journal/{user}", json={"text": "slept badly"})
    client.post(f"/checkin/{user}", json={"mood": 3, "energy": 2,
                                          "note": "flat today"})
    client.post(f"/sources/{user}", json={"source": "calendar",
                                          "consented": True})
    client.post(f"/context/{user}", json={"source": "calendar", "kind": "event",
                                          "data": {"title": "dentist"}})


def test_a_free_account_puts_nothing_in_the_vault(counted):
    """The bug this whole round is about.

    Every seal point read `if pdi is not None` — whether the *deployment* has
    a vault, not whether the *account* is on a plan that uses one. So a free
    account on a PDI-backed deployment had its journal, its check-in notes and
    its detection detail sealed into a vault it was not paying for and could
    not hold a key to. Free is platform custody over plain HTTPS.

    Asserted by counting writes rather than by reading call sites, because
    reading call sites is how twenty of them stayed wrong.
    """
    user = enroll(counted, plan="free")
    _exercise(counted, user)
    assert counted.vault.writes == [], (
        "a free account reached the vault at: "
        + ", ".join(counted.vault.writes))


def test_the_same_day_on_basic_fills_the_vault(counted):
    """The other half — otherwise the test above passes if sealing broke
    entirely, which is a different bug wearing the same green tick."""
    user = enroll(counted, plan="basic")
    _exercise(counted, user)
    assert counted.vault.writes, "nothing sealed on a vault plan"
    assert all(k.startswith(f"jim/{user}/") for k in counted.vault.writes)


def test_a_free_account_still_records_everything_locally(counted):
    """Platform custody is not amnesia. The point of the free plan is that we
    hold the record and the person has returning access to it."""
    user = enroll(counted, plan="free")
    _exercise(counted, user)
    entries = counted.get(f"/journal/{user}").json()
    assert entries and any("slept badly" in str(e) for e in entries)


def test_the_vault_gate_asks_about_the_plan_not_the_deployment(client):
    fake = FakeVault()
    assert storage.vault_for("basic", fake) is fake
    assert storage.vault_for("pro", fake) is fake
    assert storage.vault_for("free", fake) is None
    assert storage.vault_for("visitor", fake) is None
    assert storage.vault_for("basic", None) is None


# -- custody is named, and it is custody rather than ownership -----------------

def test_free_is_platform_custody_and_paid_is_the_users(client):
    assert storage.custody_of("free") == "platform"
    assert storage.custody_of("basic") == "user"
    platform = storage.CUSTODY["platform"]
    assert platform["goes_through_a_vault"] is False
    assert platform["user_holds_a_key"] is False
    assert platform["returning_access"] is True
    assert "HTTPS" in platform["transport"]


def test_the_membership_says_who_holds_it(client):
    user = enroll(client, plan="free")
    out = client.get(f"/memberships/{user}").json()
    assert out["storage"]["custody"]["who"] == "platform"
    assert out["storage"]["custody"]["held_by"] == "JIM-mini"
    assert out["storage"]["custody"]["goes_through_a_vault"] is False


def test_custody_is_never_described_as_ownership(client):
    """A product decides who *holds* a record. It does not get to decide away
    somebody's statutory rights over their own personal data — access,
    rectification, erasure, portability survive whatever a plan says — so the
    tier table claims custody and never ownership.

    Checked against the **values a user is shown**, not the module source. The
    first version swept `inspect.getsource(storage)` for ownership phrases and
    failed on the comment that explains why ownership is the wrong word: it
    quotes the phrase in order to reject it. That is the fourth time in this
    session a substring guard has tripped on its own explanation, and the
    lesson has not changed — a guard that punishes documenting the invariant is
    one somebody deletes.
    """
    shown = " ".join(
        str(v) for spec in storage.CUSTODY.values() for v in spec.values()
    ).lower()
    for phrase in ("we own your", "the platform owns", "you do not own",
                   "owns your data", "our property"):
        assert phrase not in shown, (
            f"{phrase!r} is an ownership claim, not a custody one")
    assert "host your record" in shown and "access to it" in shown

    # And the reasoning is written down, so the next person knows it was a
    # decision rather than an oversight.
    assert "statutory rights" in inspect.getsource(storage)


def test_an_open_plan_never_claims_an_empty_access_log_means_nothing_was_read(counted):
    """The comfortable lie this round removed.

    On a vault plan an empty list means nobody touched the records and the
    chain proves it. On an open plan there is no chain, so an empty list means
    nothing was *recorded* — and returning a bare `[]` would read as the first.
    """
    user = enroll(counted, plan="free")
    _exercise(counted, user)
    log = counted.get(f"/access-log/{user}").json()
    assert log["entries"] == []
    assert log["access_record_kept"] is False
    assert log["custody"] == "platform"
    assert "not that" in log["note"] and "nothing was read" in log["note"]


def test_a_vault_plan_still_gets_its_provable_access_log(counted):
    user = enroll(counted, plan="basic")
    _exercise(counted, user)
    log = counted.get(f"/access-log/{user}").json()
    assert log["access_record_kept"] is True
    assert log["custody"] == "user"
    assert log["count"] >= 1


def test_a_downgrade_leaves_the_earlier_chain_readable_and_says_so(counted):
    """The awkward middle: real entries exist for what was sealed on Basic,
    and nothing since is recorded. Both halves get said."""
    user = enroll(counted, plan="basic")
    _exercise(counted, user)
    sealed = list(counted.vault.writes)
    assert sealed

    tiers.subscribe(user, "free")
    log = counted.get(f"/access-log/{user}").json()
    assert log["access_record_kept"] is False
    assert log["sealed_under_a_previous_plan"] is True
    assert "still sealed" in log["note"]


def test_a_downgraded_account_can_still_read_what_was_sealed(counted):
    """Reads keep the real vault. Stranding somebody's history behind a
    billing change would be worse than the bug the write gate fixed."""
    user = enroll(counted, plan="basic")
    counted.post(f"/journal/{user}", json={"text": "sealed while paying"})
    tiers.subscribe(user, "free")
    entries = counted.get(f"/journal/{user}").json()
    assert any("sealed while paying" in str(e) for e in entries)


def test_erasure_still_purges_the_vault_after_a_downgrade(counted):
    """Deletes keep the real vault too. A plan-gated None here would leave
    records nobody can reach and call that erasure."""
    user = enroll(counted, plan="basic")
    _exercise(counted, user)
    assert counted.vault.store
    tiers.subscribe(user, "free")
    out = counted.delete(f"/data/{user}")
    assert out.status_code == 200, out.text
    assert counted.vault.store == {}, "sealed records survived erasure"


# -- the copy cannot go stale behind the list ----------------------------------

_COUNT_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                "six": 6, "seven": 7, "eight": 8}


def test_no_copy_hardcodes_a_stale_count_of_refusals(client):
    """Ported from QRME, where this drift actually shipped.

    `SENSITIVE` gained a third entry there and four pieces of user-facing copy
    went on saying **two** — a screen card, a screen subtitle, the walkthrough
    lesson and a README heading. A number written into prose is a duplicate of
    a list, and duplicates drift silently: nothing fails when a dict grows.

    JIM-mini's count happens to be right today. This is here so it stays right
    the day somebody adds a third.
    """
    import re

    n = len(storage.SENSITIVE)
    root = pathlib.Path(__file__).resolve().parents[2]
    pattern = re.compile(
        # No em dash and a short window: the first version reached across
        # "all three products — never stored, so it cannot disagree", which is
        # a sentence about the agent light. A guard with a false positive gets
        # loosened until it catches nothing.
        r"\b(one|two|three|four|five|six|seven|eight)\b[^.\n\u2014]{0,25}?"
        r"(we refuse|are refused|refused rather|never stored|"
        r"will not leave open|the open store will not hold)",
        re.IGNORECASE)
    for rel in ("jim/tutorial.py", "docs/screens/build.py", "README.md"):
        text = (root / rel).read_text()
        for m in pattern.finditer(text):
            said = _COUNT_WORDS[m.group(1).lower()]
            assert said == n, (
                f"{rel} says {m.group(1)!r} where SENSITIVE holds {n}: "
                f"{m.group(0)!r}")


def test_the_refusal_screen_names_every_kind_on_the_list(client):
    build = (pathlib.Path(__file__).resolve().parents[2]
             / "docs" / "screens" / "build.py").read_text()
    start = build.index("num=80")
    screen = build[start:build.index("], button=", start)].lower()
    for kind, hint in [("body_image", "photo of a body"),
                       ("dependant_record", "child's record")]:
        assert kind in storage.SENSITIVE
        assert hint in screen, (
            f"screen 80 does not name {kind!r} (looked for {hint!r})")


def test_the_walkthrough_says_who_holds_it(client):
    """The custody framing is the point of the plan, so the lesson has to
    carry it rather than only describing encryption."""
    from jim import tutorial

    lesson = next(le for le in tutorial.LESSONS if le["key"] == "storage")
    what = lesson["what"].lower()
    assert "we hold it" in what
    assert "never goes through a vault" in what
    assert "access to it" in what
