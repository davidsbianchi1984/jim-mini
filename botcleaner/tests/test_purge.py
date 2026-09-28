from datetime import datetime, timedelta, timezone

import pytest

from botcleaner import evaluation as ev
from botcleaner.purge.signals import SiteAccount, SiteScorer


def test_seeded_site_passes_module_b_gates():
    for seed in (11, 12):
        accs, truth = ev.seeded_site(seed=seed)
        m = ev.metrics_b(SiteScorer().score(accs), truth)
        assert all(ev.gates_b(m).values()), m.as_dict()


def test_common_phrases_are_not_templated_spam():
    now = datetime(2026, 6, 1, tzinfo=timezone.utc)
    accs = [SiteAccount(account_id=f"u{i}", created_at=now - timedelta(days=i * 20), posts=["Great write-up, thanks so much!"])
            for i in range(50)]
    assert all(r.score < 40 for r in SiteScorer().score(accs))


def test_rings_group_shared_devices():
    accs, _ = ev.seeded_site(n_real=200, n_bots=60)
    res = SiteScorer().score(accs)
    rings = {r.ring_id for r in res if r.ring_id}
    assert 1 <= len(rings) <= 6
    assert not any(r.ring_id for r in res if r.account_id.startswith("u"))


@pytest.fixture
def tenant(client):
    r = client.post("/api/purge/tenants", json={"name": "Forumly", "config": {"batch_size": 50, "appeal_base_url": "https://forumly.example/appeal"}})
    assert r.status_code == 200, r.text
    key = r.json()["api_key"]
    accs, truth = ev.seeded_site(n_real=400, n_bots=120, seed=5, now=datetime.now(timezone.utc))
    body = [a.model_dump(mode="json") for a in accs]
    assert client.post("/api/purge/accounts", json=body, headers={"X-API-Key": key}).json() == {"ingested": 520}
    scan = client.post("/api/purge/scan", headers={"X-API-Key": key}).json()
    assert scan["scanned"] == 520 and scan["rings"] >= 1
    return {"X-API-Key": key, "_truth": truth}


def H(t):
    return {"X-API-Key": t["X-API-Key"]}


def test_explorer_rings_sample(client, tenant):
    r = client.get("/api/purge/accounts?min_score=95", headers=H(tenant)).json()
    assert r["total"] >= 100 and all(tenant["_truth"][a["account_id"]] for a in r["accounts"])
    assert all(len(a["reasons"]) <= 3 for a in r["accounts"])
    by_reason = client.get("/api/purge/accounts?reason=honeypot&min_score=0", headers=H(tenant)).json()
    assert by_reason["total"] > 0 and all("honeypot" in a["reason_codes"] for a in by_reason["accounts"])
    rings = client.get("/api/purge/rings", headers=H(tenant)).json()
    assert rings[0]["size"] >= 3 and rings[0]["top_reasons"]
    s = client.get("/api/purge/sample?per_label=5", headers=H(tenant)).json()
    assert len(s["tier3"]) == 5


def test_dry_run_is_exact_then_execute_notice_appeal_restore(client, tenant, svc):
    staff = client.get("/api/purge/accounts?min_score=0&max_score=100", headers=H(tenant)).json()
    dry = client.post("/api/purge/dry-run", json={}, headers=H(tenant)).json()
    hit = {i["account_id"] for i in dry["items"]}
    assert dry["total"] == len(hit) >= 100
    assert all(tenant["_truth"][a] for a in hit)                   # no real users in the plan
    assert not any(a["account_id"] in hit for a in staff["accounts"] if "staff" in a["tags"])
    # Nothing changed yet.
    assert client.get("/api/purge/accounts?state=suspended&min_score=0", headers=H(tenant)).json()["total"] == 0

    # Execute in batches of 50.
    st = client.post(f"/api/purge/batches/{dry['batch_id']}/execute", headers=H(tenant)).json()
    assert st["state"] == "running" and st["applied"] == 50
    st = client.post(f"/api/purge/batches/{dry['batch_id']}/pause", headers=H(tenant)).json()
    assert st["state"] == "paused"
    assert client.post(f"/api/purge/batches/{dry['batch_id']}/step", headers=H(tenant)).json()["applied"] == 50  # paused: no-op
    client.post(f"/api/purge/batches/{dry['batch_id']}/execute", headers=H(tenant))
    while client.get(f"/api/purge/batches/{dry['batch_id']}", headers=H(tenant)).json()["state"] == "running":
        client.post(f"/api/purge/batches/{dry['batch_id']}/step", headers=H(tenant))
    st = client.get(f"/api/purge/batches/{dry['batch_id']}", headers=H(tenant)).json()
    assert st["state"] == "done" and st["applied"] == dry["total"]

    # The platform's enforcement feed carries each action with its notice and appeal link.
    feed = client.get("/api/purge/feed", headers=H(tenant)).json()
    assert len(feed) == dry["total"]
    victim = feed[0]
    n = victim["notice"]
    assert n["appeal_url"].startswith("https://forumly.example/appeal/") and n["why"] and n["what_happened"]
    token = n["appeal_url"].rsplit("/", 1)[-1]

    # Public appeals portal: no auth, token only.
    view = client.get(f"/api/appeal/{token}").json()
    assert view["can_appeal"] and "appeal_token" not in view
    assert client.get("/api/appeal/" + token[:-2] + "xx").status_code == 404
    assert client.post(f"/api/appeal/{token}", json={"statement": "short"}).status_code == 400
    ap = client.post(f"/api/appeal/{token}", json={"statement": "I'm a real person, I run the knitting sub-forum.", "contact": "me@x.org"}).json()
    assert ap["status"] == "open"
    assert client.post(f"/api/appeal/{token}", json={"statement": "Appealing a second time please"}).status_code == 400

    # Reviewer queue and decision -> auto-restore.
    rv = client.post("/api/purge/reviewers", json={"name": "Dana"}, headers=H(tenant)).json()
    R = {"X-API-Key": rv["key"]}
    assert client.post("/api/purge/dry-run", json={}, headers=R).status_code == 403  # reviewers can't act
    q = client.get("/api/purge/appeals", headers=R).json()
    assert [a["id"] for a in q] == [ap["appeal_id"]] and q[0]["account"]["reasons"]
    d = client.post(f"/api/purge/appeals/{ap['appeal_id']}/decide", json={"approve": True, "note": "Sorry!"}, headers=R).json()
    assert d["status"] == "approved" and d["reviewer"] == "reviewer:Dana"
    acc = client.get(f"/api/purge/accounts?min_score=0&state=active", headers=H(tenant)).json()
    assert victim["account_id"] in {a["account_id"] for a in acc["accounts"]}
    assert client.get(f"/api/appeal/{token}").json()["appeal"]["status"] == "approved"
    # Restored accounts are exempt: a fresh dry run won't hit them again.
    again = client.post("/api/purge/dry-run", json={}, headers=H(tenant)).json()
    assert victim["account_id"] not in {i["account_id"] for i in again["items"]}

    rep = client.get("/api/purge/report", headers=H(tenant)).json()
    assert rep["appeals"] == {"approved": 1} and rep["overturn_rate"] == 1.0 and rep["overturn_target_met"] is False
    assert rep["accounts_by_state"]["suspended"] >= 100

    # Audit log is complete and tamper-evident.
    v = client.get("/api/purge/audit/verify", headers=H(tenant)).json()
    assert v["ok"] and v["entries"] > 10
    kinds = {e["kind"] for e in client.get("/api/purge/audit", headers=H(tenant)).json()}
    assert {"dry_run", "account.action", "appeal.submitted", "appeal.decided", "account.restored"} <= kinds
    import sqlite3

    with pytest.raises(sqlite3.DatabaseError):
        svc.db.x("UPDATE t_audit SET actor='nobody' WHERE seq=1")
    with pytest.raises(sqlite3.DatabaseError):
        svc.db.x("DELETE FROM t_audit WHERE seq=1")


def test_rollback_restores_everything(client, tenant):
    dry = client.post("/api/purge/dry-run", json={"only_tiers": [3]}, headers=H(tenant)).json()
    client.post(f"/api/purge/batches/{dry['batch_id']}/execute", headers=H(tenant))
    rb = client.post(f"/api/purge/batches/{dry['batch_id']}/rollback", headers=H(tenant)).json()
    assert rb["restored"] == rb["applied"] == 50 and rb["state"] == "rolled_back"
    assert client.get("/api/purge/accounts?state=suspended&min_score=0", headers=H(tenant)).json()["total"] == 0
    feed = client.get("/api/purge/feed", headers=H(tenant)).json()
    assert all(f["rolled_back"] and f["state"] == "active" for f in feed)


def test_rules_builder_tiers_exemptions(client, tenant):
    bad = client.post("/api/purge/rules", json={"name": "nuke", "min_score": 50, "tier": 4}, headers=H(tenant))
    assert bad.status_code == 422
    client.post("/api/purge/rules", json={"name": "honeypot is always suspend", "reasons_any": ["honeypot"], "tier": 3}, headers=H(tenant))
    client.post("/api/purge/rules", json={"name": "soften disposable", "reasons_any": ["disposable_email"], "tier": 1}, headers=H(tenant))
    dry = client.post("/api/purge/dry-run", json={}, headers=H(tenant)).json()
    causes = dry["by_cause"]
    assert causes.get("rule:honeypot is always suspend", 0) > 0 and causes.get("rule:soften disposable", 0) > 0
    # Dry-run-only rules via the request body don't persist.
    dry2 = client.post("/api/purge/dry-run", json={"rules": [{"name": "exempt all", "min_score": 0, "tier": 0, "exempt": True}]}, headers=H(tenant)).json()
    assert dry2["total"] == 0
    assert len(client.get("/api/purge/rules", headers=H(tenant)).json()) == 2


def test_plan_skips_accounts_that_changed_since_dry_run(client, tenant):
    dry = client.post("/api/purge/dry-run", json={}, headers=H(tenant)).json()
    target = dry["items"][0]["account_id"]
    client.post(f"/api/purge/accounts/{target}/review", json={"is_bot": False, "note": "known user"}, headers=H(tenant))
    client.post(f"/api/purge/batches/{dry['batch_id']}/execute", headers=H(tenant))
    acc = client.get(f"/api/purge/accounts?min_score=0&state=active", headers=H(tenant)).json()
    assert target in {a["account_id"] for a in acc["accounts"]}


def test_tier4_needs_window_and_reviewer(client, tenant, svc):
    dry = client.post("/api/purge/dry-run", json={"only_tiers": [3]}, headers=H(tenant)).json()
    client.post(f"/api/purge/batches/{dry['batch_id']}/execute", headers=H(tenant))
    suspended = [i["account_id"] for i in dry["items"][:50]]
    # Inside the appeal window nothing is eligible, and forcing it is refused.
    assert client.get("/api/purge/removal-candidates", headers=H(tenant)).json() == []
    r = client.post("/api/purge/remove-permanently", json={"account_ids": suspended[:3]}, headers=H(tenant)).json()
    assert r["removed"] == [] and len(r["refused"]) == 3
    # One user appeals (still open) before the window closes.
    tid = client.get("/api/purge/me", headers=H(tenant)).json()["tenant_id"]
    token = svc.purge.appeal_token(tid, svc.purge.notice_for_account(tid, suspended[0])["notice_id"])
    client.post(f"/api/appeal/{token}", json={"statement": "Please look again, I'm a person."})
    # Jump past the 30-day window.
    later = datetime.now(timezone.utc) + timedelta(days=31)
    svc.purge.clock = lambda: later
    cands = {c["account_id"] for c in client.get("/api/purge/removal-candidates", headers=H(tenant)).json()}
    assert suspended[0] not in cands and set(suspended[1:]) <= cands
    assert client.post(f"/api/appeal/{token}", json={"statement": "late appeal text here"}).status_code == 400
    r = client.post("/api/purge/remove-permanently", json={"account_ids": suspended}, headers=H(tenant)).json()
    assert len(r["removed"]) == 49 and r["refused"] == [suspended[0]]
    row = svc.db.one("SELECT data_json, state FROM t_accounts WHERE account_id=?", (suspended[1],))
    assert row["state"] == "removed" and row["data_json"] == "{}"  # data deleted per retention


def test_tenant_isolation(client, tenant):
    other = client.post("/api/purge/tenants", json={"name": "Other"}).json()["api_key"]
    O = {"X-API-Key": other}
    assert client.get("/api/purge/accounts?min_score=0", headers=O).json()["total"] == 0
    dry = client.post("/api/purge/dry-run", json={}, headers=H(tenant)).json()
    assert client.get(f"/api/purge/batches/{dry['batch_id']}", headers=O).status_code == 404
    assert client.post(f"/api/purge/batches/{dry['batch_id']}/execute", headers=O).status_code == 404
    assert client.get("/api/purge/audit", headers=O).json()[0]["kind"] == "tenant.created"
    assert client.get("/api/purge/accounts", headers={"X-API-Key": "bcp_wrong"}).status_code == 401


def test_verification_restores_challenged(client, tenant):
    dry = client.post("/api/purge/dry-run", json={"rules": [{"name": "challenge all", "min_score": 60, "tier": 1}]}, headers=H(tenant)).json()
    client.post(f"/api/purge/batches/{dry['batch_id']}/execute", headers=H(tenant))
    target = dry["items"][0]["account_id"]
    r = client.post(f"/api/purge/accounts/{target}/verified", headers=H(tenant)).json()
    assert r["state"] == "active" and r["exempt"]
    assert client.post(f"/api/purge/accounts/{target}/verified", headers=H(tenant)).status_code == 400


def test_realtime_signup_gate(client, tenant):
    ok = client.post("/api/purge/gate", json={"account_id": "new1", "email": "sam.lee@gmail.com", "signup_ip": "81.2.69.160",
                                              "captcha_solve_ms": 6000, "device_fingerprint": "fpA"}, headers=H(tenant)).json()
    assert ok["decision"] == "allow"
    decisions = []
    for i in range(8):
        decisions.append(client.post("/api/purge/gate", json={
            "account_id": f"farm{i}", "email": f"deal{i}@mailinator.com", "signup_ip": "45.1.1.1", "device_fingerprint": "farmX",
            "user_agent": "HeadlessChrome/126", "captcha_solve_ms": 300, "honeypot_filled": True}, headers=H(tenant)).json())
    assert decisions[-1]["decision"] == "block" and decisions[-1]["reasons"]
    rep = client.get("/api/purge/report", headers=H(tenant)).json()
    assert rep["signup_gate"]["block"] >= 1 and rep["signup_gate"]["allow"] >= 1


def test_config_validation_and_csv_ingest(client, tenant):
    assert client.patch("/api/purge/config", json={"appeal_window_days": 3}, headers=H(tenant)).status_code == 400
    assert client.patch("/api/purge/config", json={"tier1_min": 90, "tier2_min": 80}, headers=H(tenant)).status_code == 400
    cfg = client.patch("/api/purge/config", json={"appeal_window_days": 14}, headers=H(tenant)).json()
    assert cfg["appeal_window_days"] == 14
    csv = ("account_id,username,email,created_at,signup_ip,posts,tags,honeypot_filled\n"
           "c1,alice,alice@example.org,2024-01-01T00:00:00Z,1.2.3.4,hello world|second post,staff,false\n"
           "c2,zqxwvbnm8812,x1@mailinator.com,2026-01-01T00:00:00Z,5.6.7.8,,,true\n")
    r = client.post("/api/purge/accounts/csv", files={"file": ("users.csv", csv.encode(), "text/csv")}, headers=H(tenant))
    assert r.json() == {"ingested": 2}
    client.post("/api/purge/scan", headers=H(tenant))
    acc = {a["account_id"]: a for a in client.get("/api/purge/accounts?min_score=0", headers=H(tenant)).json()["accounts"]}
    assert acc["c1"]["exempt"] and acc["c2"]["score"] >= 85
