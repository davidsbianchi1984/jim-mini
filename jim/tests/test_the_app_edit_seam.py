"""App edits, held at apply — and the model menu that is a loadout per region.

The owner's ask, pinned: a person can propose a change to the app itself and
have an assistant write it; on their own server they have free rein, on the
hosted cloud it is held for company oversight; either way an approved edit is
queued to ride the next publish-merge and nothing here applies it to running
code. And the model the assistant writes with is the person's pick from a
per-region loadout — American-led with a curated few foreign for a US
account, its own loadout elsewhere, and a one-line lever to taper the
American-region menu if the government asks.
"""

import pytest

from jim import appedits, db, llm, loadouts
from jim.tests.conftest import enroll


def _actions(uid):
    return [r["action"] for r in db.connect().execute(
        "SELECT action FROM audit WHERE user_id=? ORDER BY seq", (uid,)).fetchall()]


# --- the loadouts -----------------------------------------------------------

def test_the_registry_is_wide_and_every_provider_names_its_home():
    real = [n for n, s in llm._REGISTRY.items() if s.get("origin") not in ("local", "any")]
    from . import ratchets
    assert len(real) >= ratchets.floor("llm.real_providers"), (
        f"only {len(real)} real providers on the menu")
    for name, spec in llm._REGISTRY.items():
        assert spec.get("origin"), f"{name} has no origin"


def test_a_us_account_is_american_led_with_a_curated_few_foreign(client):
    uid = enroll(client)
    assert loadouts.region_of(uid) == "us"
    names = loadouts.providers_for(uid)
    assert names[0] == "anthropic"                 # the beta default leads
    assert "deepseek" in names and "mistral" in names   # a curated few foreign
    assert "zhipu" not in names                    # not every foreign one


def test_a_chinese_account_leads_with_its_home_providers(client):
    uid = enroll(client)
    loadouts.set_region(uid, "cn")
    names = loadouts.providers_for(uid)
    assert names[0] == "qwen" and "zhipu" in names
    assert "anthropic" in names                     # and still offers American
    assert "region.set" in _actions(uid)


def test_the_american_lever_tapers_only_the_us_region(client, monkeypatch):
    uid = enroll(client)
    monkeypatch.setenv("JIM_MODEL_POLICY", "american")
    us = loadouts.providers_for(uid)
    assert all(llm.origin_of(n) in ("US", "local", "any") for n in us)
    assert "deepseek" not in us
    # Another region is not bound by it.
    loadouts.set_region(uid, "eu")
    assert "mistral" in loadouts.providers_for(uid)


def test_a_region_the_menu_does_not_know_is_refused(client):
    uid = enroll(client)
    with pytest.raises(ValueError):
        loadouts.set_region(uid, "mars")


def test_offered_rows_carry_their_origin(client):
    uid = enroll(client)
    rows = loadouts.offered(uid)
    assert rows and all("origin" in r for r in rows)
    assert {r["name"] for r in rows} == set(loadouts.providers_for(uid))


def test_the_video_menu_is_the_same_shape(client):
    uid = enroll(client)
    us = [p["name"] for p in loadouts.video_providers_for(uid)]
    assert "runway" in us and "higgsfield" in us and "kling" in us
    assert "seedance" not in us
    loadouts.set_region(uid, "cn")
    assert [p["name"] for p in loadouts.video_providers_for(uid)][0] == "kling"


# --- the seam ---------------------------------------------------------------

def test_on_the_cloud_an_edit_is_held_for_oversight(client, monkeypatch):
    monkeypatch.delenv("JIM_SELF_HOSTED", raising=False)
    uid = enroll(client)
    e = appedits.propose(uid, title="Bigger check-in button",
                         description="the button is too small on a phone")
    assert e["lane"] == "cloud" and e["state"] == "proposed"
    assert appedits.posture()["held_for_approval"] is True
    assert appedits.posture()["apply_wired"] is False
    assert "appedit.proposed" in _actions(uid)
    assert "appedit.approved" not in _actions(uid)


def test_on_a_self_hosted_server_free_rein_approves_on_arrival(client, monkeypatch):
    monkeypatch.setenv("JIM_SELF_HOSTED", "1")
    uid = enroll(client)
    e = appedits.propose(uid, title="My own tweak", description="my server")
    assert e["lane"] == "self_hosted" and e["state"] == "approved"
    assert appedits.posture()["free_rein"] is True
    assert "appedit.approved" in _actions(uid)


def test_oversight_approves_or_rejects_and_the_queue_shows_it(client, monkeypatch):
    monkeypatch.delenv("JIM_SELF_HOSTED", raising=False)
    uid = enroll(client)
    a = appedits.propose(uid, title="A", description="first")
    b = appedits.propose(uid, title="B", description="second")
    assert {x["id"] for x in appedits.queue()["awaiting"]} == {a["id"], b["id"]}
    ok = appedits.decide(a["id"], "approve", by="oversight", note="good")
    no = appedits.decide(b["id"], "reject", by="oversight", note="not now")
    assert ok["state"] == "approved" and no["state"] == "rejected"
    q = appedits.queue()
    assert [x["id"] for x in q["queued"]] == [a["id"]] and not q["awaiting"]
    with pytest.raises(ValueError):
        appedits.decide(a["id"], "approve", by="oversight")   # already decided
    with pytest.raises(ValueError):
        appedits.decide(b["id"], "maybe", by="oversight")


def test_the_assistant_drafts_and_files_it(client, monkeypatch):
    monkeypatch.delenv("JIM_SELF_HOSTED", raising=False)
    uid = enroll(client)
    e = appedits.draft(uid, target="app/src/screens/Checkin.tsx",
                       instruction="make the check-in button larger on phones")
    assert e["state"] == "proposed" and e["patch"]
    assert e["model"]                           # who wrote it is recorded
    assert "appedit.drafted" in _actions(uid)
    # The exchange was banked for the offline corpus, tagged.
    assert db.connect().execute(
        "SELECT COUNT(*) AS n FROM training_examples WHERE user_id=? AND"
        " source='appedit'", (uid,)).fetchone()["n"] == 1


def test_the_assistant_will_not_draft_with_a_model_off_the_menu(client):
    uid = enroll(client)                          # a US account
    with pytest.raises(ValueError):
        appedits.draft(uid, instruction="anything", model="zhipu")


# --- the doors --------------------------------------------------------------

def test_the_menu_and_region_doors_are_the_owners(client):
    uid = enroll(client)
    m = client.get(f"/models/{uid}").json()
    assert m["region"] == "us" and m["providers"][0]["name"] == "anthropic"
    assert client.put(f"/users/{uid}/region", json={"region": "eu"}).status_code == 200
    assert client.get(f"/models/{uid}").json()["region"] == "eu"
    assert client.put(f"/users/{uid}/region", json={"region": "mars"}).status_code == 422
    assert client.get(f"/video/providers/{uid}").json()["providers"]


def test_choosing_a_model_off_the_menu_is_refused(client):
    uid = enroll(client)
    r = client.put(f"/model/{uid}", json={"provider": "zhipu"})   # not on the US menu
    assert r.status_code == 422
    assert client.put(f"/model/{uid}", json={"provider": "anthropic"}).status_code == 200


def test_the_edit_doors_are_the_owners_and_oversight_is_the_reviewer(client, monkeypatch):
    monkeypatch.delenv("JIM_SELF_HOSTED", raising=False)
    uid = enroll(client)
    got = client.post(f"/appedits/{uid}", json={
        "title": "Bigger button", "description": "too small on a phone"})
    assert got.status_code == 201 and got.json()["state"] == "proposed"
    eid = got.json()["id"]
    assert client.get(f"/appedits/{uid}").json()["posture"]["held_for_approval"] is True
    drafted = client.post(f"/appedits/{uid}/draft", json={"instruction": "larger button"})
    assert drafted.status_code == 201 and drafted.json()["patch"]
    # Oversight needs the deployment's reviewer token, not a user's.
    monkeypatch.setenv("JIM_ADMIN_TOKEN", "rev-secret")
    assert client.get("/appedits/oversight/queue").status_code in (401, 403)
    hdr = {"Authorization": "Bearer rev-secret"}
    q = client.get("/appedits/oversight/queue", headers=hdr)
    assert q.status_code == 200 and any(x["id"] == eid for x in q.json()["awaiting"])
    d = client.post(f"/appedits/oversight/{eid}/decide", headers=hdr,
                    json={"action": "approve", "note": "ship it"})
    assert d.status_code == 200 and d.json()["state"] == "approved"
    assert client.get(f"/appedits/{uid}").json()["edits"][0]["state"] in ("approved", "proposed")
