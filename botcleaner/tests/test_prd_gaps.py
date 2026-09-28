"""Section 10 metrics, section 7.5 red team, the client SDK signal, and the Discord/Discourse adapters."""
import json
from datetime import datetime, timedelta, timezone

import httpx
import pytest

from botcleaner import evaluation as ev
from botcleaner.purge.adapters import DiscordAdapter, DiscourseAdapter
from botcleaner.purge.signals import SiteAccount, SiteScorer
from botcleaner.scoring import Scorer
from conftest import hdr
from test_personal_api import burst_export, flagged, ig_export, upload

NOW = datetime(2026, 6, 1, tzinfo=timezone.utc)


def test_red_team_levels_one_and_two_caught_without_false_flags():
    net, level = ev.red_team_network()
    rep = ev.red_team_report(Scorer(now=NOW).score(net.conns), net.truth, level)
    assert rep["level1_recall"] >= 0.9 and rep["level2_recall"] >= 0.9
    assert rep["false_flag_rate"] <= ev.GATES_A["false_flag_rate_max"]


def test_scheduling_tool_regularity_alone_is_not_flagged():
    from botcleaner.models import Connection, Direction, Platform

    # A real small business posting via a scheduler: roughly (not perfectly) regular.
    ts = [NOW - timedelta(hours=24 * k, minutes=(k * 7) % 60) for k in range(20)]
    c = Connection(platform=Platform.x, account_id="bakery", handle="cornerbakery", name="Corner Bakery",
                   direction=Direction.following, created_at=NOW - timedelta(days=1500), followers_count=900,
                   following_count=300, bio="Fresh bread daily", post_timestamps=ts)
    [r] = Scorer(now=NOW).score([c])
    assert r.score < 60


def test_form_speed_signal():
    fast, slow = SiteScorer().score([SiteAccount(account_id="a", form_fill_ms=400), SiteAccount(account_id="b", form_fill_ms=40_000)])
    assert "form_speed" in {x.code for x in fast.reasons} and not slow.reasons


def test_sdk_is_served(client):
    js = client.get("/static/sdk.js").text
    assert "BotCleaner" in js and "honeypot_filled" in js and "form_fill_ms" in js


def test_product_metrics(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient

    from botcleaner.api import create_app

    monkeypatch.setenv("BOTCLEANER_ADMIN_TOKEN", "adm")
    c = TestClient(create_app(str(tmp_path / "m.sqlite3"), worker=False))
    A = {"X-Admin-Token": "adm"}
    assert c.get("/api/admin/metrics").status_code == 401
    empty = c.get("/api/admin/metrics", headers=A).json()
    assert empty["flag_confirmation_rate"] is None and empty["met"]["platform_restrictions"] is True

    u = {"Authorization": "Bearer " + c.post("/api/signup", json={"email": "m@example.com"}).json()["token"]}
    exp = burst_export()
    upload(c, u, ig_export(exp)[0])
    bots = flagged(c, u)
    # User removes 9, says one is a real person.
    job = c.post("/api/removals", headers=u, json={"platform": "instagram", "mode": "guided",
                 "accounts": [{"account_id": b["account_id"], "direction": "follower"} for b in bots[:9]]}).json()
    for i in range(9):
        c.post(f"/api/removals/{job['id']}/items/{i}/confirm", headers=u, json={"outcome": "done"})
    c.post("/api/feedback", headers=u, json={"platform": "instagram", "account_id": bots[9]["account_id"], "is_bot": False})
    # A second user scans but never removes anything.
    u2 = {"Authorization": "Bearer " + c.post("/api/signup", json={"email": "n@example.com"}).json()["token"]}
    upload(c, u2, ig_export(exp)[0])

    m = c.get("/api/admin/metrics", headers=A).json()
    assert m["flag_decisions"] == 10 and m["flag_confirmation_rate"] == 0.9 and m["met"]["flag_confirmation_rate"] is True
    assert m["users_scanned"] == 2 and m["first_scan_completion_rate"] == 0.5
    assert m["scan_to_clean_samples"] == 1 and m["median_scan_to_clean_minutes"] is not None
    assert m["met"]["median_scan_to_clean_minutes"] is True

    c.post("/api/me/restriction-report", headers=u, json={"platform": "instagram", "note": "action blocked"})
    m = c.get("/api/admin/metrics", headers=A).json()
    assert m["platform_restrictions"] == 1 and m["met"]["platform_restrictions"] is False


# ---- adapters -------------------------------------------------------------------------

class FakeDiscourse:
    def __init__(self):
        self.calls = []

    def __call__(self, req: httpx.Request):
        assert req.headers["Api-Key"] == "dk" and req.headers["Api-Username"] == "system"
        self.calls.append((req.method, req.url.path))
        if req.url.path == "/admin/users/list/active.json":
            if req.url.params["page"] == "1":
                return httpx.Response(200, json=[
                    {"id": 1, "username": "mod", "admin": True, "created_at": "2020-01-01T00:00:00Z", "active": True},
                    {"id": 2, "username": "xk7q9zzqwp", "email": "a@mailinator.com", "created_at": "2026-05-30T00:00:00Z",
                     "active": False, "registration_ip_address": "45.1.1.1"},
                ])
            return httpx.Response(200, json=[])
        if req.method in ("PUT", "DELETE"):
            return httpx.Response(200, json={"success": "OK"})
        return httpx.Response(404)


def test_discourse_adapter_import_and_enforce(client, svc):
    fake = FakeDiscourse()
    svc.purge.http = httpx.Client(transport=httpx.MockTransport(fake))
    key = client.post("/api/purge/tenants", json={"name": "Forum"}).json()["api_key"]
    H = {"X-API-Key": key}
    assert client.put("/api/purge/adapter", json={"kind": "discourse", "secret": "dk"}, headers=H).status_code == 400
    r = client.put("/api/purge/adapter", json={"kind": "discourse", "secret": "dk", "base_url": "https://forum.example"}, headers=H)
    assert r.status_code == 200 and "secret" not in r.text and "dk" not in json.dumps(r.json())
    assert client.post("/api/purge/adapter/sync", headers=H).json() == {"ingested": 2, "source": "discourse"}
    client.post("/api/purge/scan", headers=H)
    accs = {a["account_id"]: a for a in client.get("/api/purge/accounts?min_score=0", headers=H).json()["accounts"]}
    assert accs["1"]["exempt"]  # admins arrive tagged as staff

    dry = client.post("/api/purge/dry-run", json={"rules": [{"name": "suspend 2", "min_score": 0, "tier": 3}]}, headers=H).json()
    assert [i["account_id"] for i in dry["items"]] == ["2"]
    client.post(f"/api/purge/batches/{dry['batch_id']}/execute", headers=H)
    assert ("PUT", "/admin/users/2/suspend") in fake.calls
    client.post(f"/api/purge/batches/{dry['batch_id']}/rollback", headers=H)
    assert ("PUT", "/admin/users/2/unsuspend") in fake.calls
    # The stored credential is sealed.
    row = svc.db.one("SELECT sealed FROM t_adapters")
    assert b"dk" not in bytes(row["sealed"])


def test_discord_adapter_mapping():
    calls = []

    def handler(req: httpx.Request):
        calls.append((req.method, req.url.path, json.loads(req.content) if req.content else None,
                      req.headers.get("X-Audit-Log-Reason")))
        if req.url.path.endswith("/members") and req.method == "GET":
            if req.url.params["after"] == "0":
                return httpx.Response(200, json=[
                    {"user": {"id": "175928847299117063", "username": "old"}},
                    {"user": {"id": "1250000000000000000", "username": "helperbot", "bot": True}},
                ])
            return httpx.Response(200, json=[])
        return httpx.Response(204)

    d = DiscordAdapter("g1", "tok", verify_role_id="r9", http=httpx.Client(transport=httpx.MockTransport(handler)))
    accs = d.fetch_accounts()
    assert accs[0].created_at.year == 2016 and accs[1].tags == ["integration"]
    d.enforce("u1", "restricted", {"what_happened": "Paused"})
    method, path, body, reason = calls[-1]
    assert method == "PATCH" and path == "/api/v10/guilds/g1/members/u1" and body["communication_disabled_until"] and reason == "Paused"
    d.enforce("u1", "suspended")
    assert calls[-1][:2] == ("PUT", "/api/v10/guilds/g1/bans/u1")
    d.enforce("u1", "challenged")
    assert calls[-1][:2] == ("PUT", "/api/v10/guilds/g1/members/u1/roles/r9")
    n = len(calls)
    d.enforce("u1", "active")
    undo = {(m, p) for m, p, _, _ in calls[n:]}
    assert ("DELETE", "/api/v10/guilds/g1/bans/u1") in undo and ("PATCH", "/api/v10/guilds/g1/members/u1") in undo


def test_discourse_removed_deletes_user():
    calls = []
    a = DiscourseAdapter("https://f.example", "k", http=httpx.Client(transport=httpx.MockTransport(
        lambda r: (calls.append((r.method, r.url.path)), httpx.Response(200, json={}))[1])))
    a.enforce("7", "removed")
    a.enforce("7", "restricted", {"what_happened": "x", "appeal_url": "https://a/b"})
    assert calls == [("DELETE", "/admin/users/7.json"), ("PUT", "/admin/users/7/silence")]
    with pytest.raises(Exception):
        a.enforce("7", "bogus")


# ---- Assisted-mode extension guard ------------------------------------------------------

def test_extension_never_automates_the_platform_page():
    import re
    from pathlib import Path

    ext = Path(__file__).resolve().parents[1] / "extension"
    manifest = json.loads((ext / "manifest.json").read_text())
    assert manifest["manifest_version"] == 3
    # No permission that could drive or script a page, and no blanket host access up front.
    assert set(manifest["permissions"]) <= {"storage", "tabs"}
    assert "host_permissions" not in manifest
    overlay = (ext / "overlay.js").read_text()
    code = re.sub(r"//.*", "", overlay)  # the safety comment names the forbidden things
    for forbidden in (".click(", "dispatchEvent", ".submit(", "querySelector", "getElementsBy", "execCommand", "KeyboardEvent", "MouseEvent"):
        assert forbidden not in code, forbidden
    background = (ext / "background.js").read_text()
    assert "chrome.scripting" not in background and "chrome.debugger" not in background
