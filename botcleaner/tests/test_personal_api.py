import json
from datetime import datetime, timedelta, timezone

import pytest

from botcleaner.models import Connection, Direction, Platform
from conftest import hdr

NOW = datetime.now(timezone.utc)


def ig_export(handles_followers, handles_following=(), ts=None):
    ts = ts or int(NOW.timestamp()) - 86400 * 400
    followers = [{"title": "", "string_list_data": [{"href": f"https://www.instagram.com/{h}", "value": h, "timestamp": t}]}
                 for h, t in ((h if isinstance(h, tuple) else (h, ts)) for h in handles_followers)]
    following = {"relationships_following": [{"title": h, "string_list_data": [{"href": f"https://www.instagram.com/_u/{h}", "timestamp": ts}]}
                                             for h in handles_following]}
    return followers, following


def upload(client, user, followers, following=None, name="followers_1.json"):
    r = client.post("/api/import/instagram", headers=hdr(user),
                    files={"file": (name, json.dumps(followers).encode(), "application/json")})
    assert r.status_code == 200, r.text
    if following is not None:
        r = client.post("/api/import/instagram", headers=hdr(user),
                        files={"file": ("following.json", json.dumps(following).encode(), "application/json")})
    return r.json()


def burst_export():
    """40 real-looking followers spread over years + 12 number-handle bots arriving in one hour."""
    base = int(NOW.timestamp()) - 86400 * 30
    real = [(f"friend.{i}", int(NOW.timestamp()) - 86400 * (100 + 37 * i)) for i in range(40)]
    bots = [(f"lucy{48291730 + i}", base + i * 60) for i in range(12)]
    return real + bots


def flagged(client, user, platform="instagram"):
    out = []
    for tab in ("likely_bot", "suspicious"):
        out += client.get(f"/api/flags?platform={platform}&tab={tab}", headers=hdr(user)).json()
    return out


def test_requires_auth(client):
    assert client.get("/api/me/dashboard").status_code == 401
    assert client.get("/api/flags", headers={"Authorization": "Bearer nope"}).status_code == 401


def test_signup_validation_and_teen_consent(client):
    assert client.post("/api/signup", json={"email": "bad"}).status_code == 400
    r = client.post("/api/signup", json={"email": "parent@example.com", "guardian_of": "teen_kid"})
    assert r.status_code == 400 and "consent" in r.json()["detail"]
    assert client.post("/api/signup", json={"email": "parent@example.com", "guardian_of": "teen_kid", "teen_consent": True}).status_code == 200


def test_import_scan_review_flow(client, user):
    followers, following = ig_export(burst_export(), ["natgeo"])
    upload(client, user, followers, following)
    dash = client.get("/api/me/dashboard", headers=hdr(user)).json()
    ig = dash["platforms"]["instagram"]
    assert ig["directions"]["follower"]["connections"] == 52
    assert ig["flagged"] >= 12

    rows = flagged(client, user)
    handles = {r["handle"] for r in rows}
    assert {f"lucy{48291730 + i}" for i in range(12)} <= handles
    assert not any(h.startswith("friend.") for h in handles)
    r0 = rows[0]
    assert r0["reasons"] and len(r0["reasons"]) <= 3 and r0["profile_url"].startswith("https://www.instagram.com/")
    suspicious = client.get("/api/flags?platform=instagram&tab=suspicious", headers=hdr(user)).json()
    assert suspicious == sorted(suspicious, key=lambda r: -r["score"])

    # direction toggle and reason filter
    assert client.get("/api/flags?platform=instagram&tab=suspicious&direction=following", headers=hdr(user)).json() == []
    by_reason = client.get("/api/flags?tab=all&reason=arrival_burst", headers=hdr(user)).json()
    assert by_reason and all("arrival_burst" in r["reason_codes"] for r in by_reason)


def test_feedback_whitelist_and_retrain(client, user):
    followers, _ = ig_export(burst_export())
    upload(client, user, followers)
    target = client.get("/api/flags?tab=all&reason=arrival_burst", headers=hdr(user)).json()[0]
    r = client.post("/api/feedback", headers=hdr(user), json={"platform": "instagram", "account_id": target["account_id"], "is_bot": False})
    assert r.status_code == 200 and r.json()["learned_from"]
    wl = client.get("/api/flags?tab=whitelisted", headers=hdr(user)).json()
    assert [w["account_id"] for w in wl] == [target["account_id"]]
    # rescans keep the whitelist
    client.post("/api/scan", headers=hdr(user), json={})
    assert client.get("/api/flags?tab=whitelisted", headers=hdr(user)).json()[0]["account_id"] == target["account_id"]
    # whitelisted accounts can't be queued for removal
    r = client.post("/api/removals", headers=hdr(user), json={"platform": "instagram", "mode": "guided",
                    "accounts": [{"account_id": target["account_id"], "direction": "follower"}]})
    assert r.status_code == 400
    # "Definitely a bot" on a real-looking account pins it to Likely bot
    real = client.get("/api/flags?tab=all&platform=instagram", headers=hdr(user)).json()
    friend = next(x for x in real if x["handle"] == "friend.3")
    client.post("/api/feedback", headers=hdr(user), json={"platform": "instagram", "account_id": friend["account_id"], "is_bot": True})
    top = client.get("/api/flags?tab=likely_bot", headers=hdr(user)).json()
    assert friend["account_id"] in {x["account_id"] for x in top}


def test_guided_removal_then_recheck_marks_removed_or_failed(client, user):
    exp = burst_export()
    followers, _ = ig_export(exp)
    upload(client, user, followers)
    bots = flagged(client, user)[:4]
    assert len(bots) == 4
    assert client.get("/api/removals/modes/instagram").json()["modes"] == ["assisted", "guided"]
    r = client.post("/api/removals", headers=hdr(user), json={"platform": "instagram", "mode": "one_click",
                    "accounts": [{"account_id": b["account_id"], "direction": b["direction"]} for b in bots]})
    assert r.status_code == 400  # no one-click on Instagram
    job = client.post("/api/removals", headers=hdr(user), json={"platform": "instagram", "mode": "guided",
                      "accounts": [{"account_id": b["account_id"], "direction": b["direction"]} for b in bots]}).json()
    g = client.get(f"/api/removals/{job['id']}/guided?device=ios", headers=hdr(user)).json()
    assert g["steps"]["remove_follower"]["steps"] and g["steps"]["remove_follower"]["device"] == "ios"
    for i in range(4):
        client.post(f"/api/removals/{job['id']}/items/{i}/confirm", headers=hdr(user), json={"outcome": "done"})
    j = client.get(f"/api/removals/{job['id']}", headers=hdr(user)).json()
    assert j["counts"] == {"pending": 4} and j["state"] == "done"
    assert len(client.get("/api/flags?tab=pending", headers=hdr(user)).json()) == 4

    # Next export: 3 of the 4 are gone, one is still there.
    gone = {b["handle"] for b in bots[:3]}
    followers2, _ = ig_export([e for e in exp if e[0] not in gone])
    res = upload(client, user, followers2)
    assert res["reconciled"] == {"removed": 3, "still_there": 1}
    assert len(client.get("/api/flags?tab=removed", headers=hdr(user)).json()) == 3
    j = client.get(f"/api/removals/{job['id']}", headers=hdr(user)).json()
    assert j["counts"] == {"removed": 3, "failed": 1}
    log = client.get("/api/undo-log?event=removed", headers=hdr(user)).json()
    assert len(log) == 3
    csv_text = client.get("/api/export.csv", headers=hdr(user)).text
    assert csv_text.startswith("date,event,platform") and csv_text.count("removed") >= 3

    # Undo: user re-adds one by mistake -> whitelisted forever.
    x = log[0]
    client.post("/api/undo/readded", headers=hdr(user), json={"platform": x["platform"], "account_id": x["account_id"], "direction": x["direction"]})
    assert x["account_id"] in {w["account_id"] for w in client.get("/api/flags?tab=whitelisted", headers=hdr(user)).json()}


def test_assisted_mode_paces_and_never_auto_clicks(client, user, svc):
    followers, _ = ig_export(burst_export())
    upload(client, user, followers)
    bots = flagged(client, user)[:3]
    job = client.post("/api/removals", headers=hdr(user), json={"platform": "instagram", "mode": "assisted",
                      "accounts": [{"account_id": b["account_id"], "direction": "follower"} for b in bots]}).json()
    first = client.get(f"/api/removals/{job['id']}/next", headers=hdr(user)).json()
    assert first["state"] == "open" and first["item"]["profile_url"] and first["steps"]["steps"]
    assert "yourself" in first["note"]
    # Human pace: asking again straight away makes you wait.
    again = client.get(f"/api/removals/{job['id']}/next", headers=hdr(user)).json()
    assert again["state"] == "waiting" and again["wait_seconds"] > 0
    client.post(f"/api/removals/{job['id']}/items/{first['item']['idx']}/confirm", headers=hdr(user), json={"outcome": "done"})
    # Pause / resume / cancel
    assert client.post(f"/api/removals/{job['id']}/state", headers=hdr(user), json={"state": "paused"}).json()["state"] == "paused"
    assert client.get(f"/api/removals/{job['id']}/next", headers=hdr(user)).json()["state"] == "paused"
    client.post(f"/api/removals/{job['id']}/state", headers=hdr(user), json={"state": "cancelled"})
    j = client.get(f"/api/removals/{job['id']}", headers=hdr(user)).json()
    assert j["counts"] == {"pending": 1, "skipped": 2}


def test_clone_alert_and_cross_user_isolation(client, user, svc):
    uid = user["_id"]
    t = NOW - timedelta(days=800)
    conns = [
        Connection(platform=Platform.facebook, account_id="real-ana", name="Ana Costa", direction=Direction.friend, connected_at=t),
        Connection(platform=Platform.facebook, account_id="fake-ana", name="Ana Costa", direction=Direction.friend, connected_at=NOW - timedelta(days=2)),
    ] + [Connection(platform=Platform.facebook, account_id=f"p{i}", name=f"Person {chr(65 + i)} Number", direction=Direction.friend,
                    connected_at=t + timedelta(days=i)) for i in range(10)]
    svc.personal.store_connections(uid, Platform.facebook, conns)
    svc.personal.scan(uid)
    clones = client.get("/api/flags?tab=clones", headers=hdr(user)).json()
    assert [c["account_id"] for c in clones] == ["fake-ana"] and clones[0]["clone_of"] == "real-ana"
    alerts = client.get("/api/alerts", headers=hdr(user)).json()
    assert alerts and alerts[0]["kind"] == "clone" and "facebook.com" in alerts[0]["link"]
    # Another user sees nothing of this.
    other = client.post("/api/signup", json={"email": "other@example.com"}).json()["token"]
    assert client.get("/api/flags?tab=all", headers={"Authorization": f"Bearer {other}"}).json() == []
    assert client.get("/api/flags/facebook/friend/fake-ana", headers={"Authorization": f"Bearer {other}"}).status_code == 404


def test_raw_data_ttl_and_one_tap_delete(client, user, svc):
    followers, _ = ig_export(burst_export())
    upload(client, user, followers)
    assert svc.personal.purge_raw(NOW + timedelta(hours=1)) == 0
    assert svc.personal.purge_raw(NOW + timedelta(hours=25)) > 0
    # Scores and decisions survive the purge.
    assert flagged(client, user)
    assert client.delete("/api/me", headers=hdr(user)).json() == {"deleted": True}
    assert client.get("/api/me/dashboard", headers=hdr(user)).status_code == 401
    assert svc.db.one("SELECT COUNT(*) n FROM flags")["n"] == 0


def test_scheduled_rescans_send_reminders(client, user, svc):
    assert client.post("/api/rescan", headers=hdr(user), json={"cadence": "weekly"}).json()["rescan"] == "weekly"
    assert svc.personal.due_rescans(NOW + timedelta(days=8)) == [user["_id"]]
    assert svc.personal.due_rescans(NOW + timedelta(days=9)) == []
    assert any(a["kind"] == "rescan" for a in client.get("/api/alerts", headers=hdr(user)).json())
    assert client.post("/api/rescan", headers=hdr(user), json={"cadence": "hourly"}).status_code == 400


def test_instruction_editor_moderation_and_safety(client, user, monkeypatch):
    best = client.get("/api/instructions/best?platform=instagram&device=android&action=remove_follower", headers=hdr(user)).json()
    assert best["source"] == "builtin" and best["steps"]
    bad = client.post("/api/instructions", headers=hdr(user), json={"platform": "instagram", "device": "android", "action": "remove_follower",
                      "steps": ["Go to http://insta-helper.xyz/login and enter your password"]})
    assert bad.status_code == 400 and "password" in bad.json()["detail"].lower()
    mine = client.post("/api/instructions", headers=hdr(user), json={"platform": "instagram", "device": "android", "action": "remove_follower",
                       "steps": ["Open your profile", "Tap followers", "Tap Remove next to the account"], "share": True, "app_version": "352"}).json()
    assert mine["status"] == "pending"
    # The author sees their own steps first; nobody else does until approved.
    assert client.get("/api/instructions/best?platform=instagram&device=android&action=remove_follower", headers=hdr(user)).json()["id"] == mine["id"]
    other = {"Authorization": "Bearer " + client.post("/api/signup", json={"email": "o@example.com"}).json()["token"]}
    assert client.get("/api/instructions/best?platform=instagram&device=android&action=remove_follower", headers=other).json()["source"] == "builtin"
    # Editing creates a new version.
    v2 = client.post("/api/instructions", headers=hdr(user), json={"platform": "instagram", "device": "android", "action": "remove_follower",
                     "steps": ["Open profile", "Followers", "Remove"], "share": True, "replaces": mine["id"]}).json()
    assert v2["id"] == mine["id"] and v2["version"] == 2
    # Moderation requires the admin token.
    assert client.get("/api/admin/instructions/pending").status_code == 401
    # Outdated flags: three different users flag a built-in.
    bid = "builtin:tiktok:web:unfollow"
    for i in range(3):
        u = {"Authorization": "Bearer " + client.post("/api/signup", json={"email": f"f{i}@example.com"}).json()["token"]}
        out = client.post(f"/api/instructions/{bid}/outdated", headers=u).json()
    assert out["outdated"] is True


def test_admin_moderation(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient

    from botcleaner.api import create_app

    monkeypatch.setenv("BOTCLEANER_ADMIN_TOKEN", "adm")
    c = TestClient(create_app(str(tmp_path / "m.sqlite3"), worker=False))
    u = {"Authorization": "Bearer " + c.post("/api/signup", json={"email": "a@example.com"}).json()["token"]}
    s = c.post("/api/instructions", headers=u, json={"platform": "x", "device": "web", "action": "unfollow",
               "steps": ["Open the profile", "Click Following", "Click Unfollow"], "share": True}).json()
    pend = c.get("/api/admin/instructions/pending", headers={"X-Admin-Token": "adm"}).json()
    assert [p["id"] for p in pend] == [s["id"]]
    assert c.post(f"/api/admin/instructions/{s['id']}/moderate", headers={"X-Admin-Token": "adm"}, json={"approve": True}).json()["status"] == "published"
    assert s["id"] in {i["id"] for i in c.get("/api/instructions?platform=x").json()}
    # Tenants need the admin token when one is configured.
    assert c.post("/api/purge/tenants", json={"name": "p"}).status_code == 401


@pytest.mark.parametrize("platform", ["facebook", "tiktok", "linkedin"])
def test_every_export_platform_has_steps_and_help(client, platform):
    help_ = client.get("/api/import/help").json()
    assert help_[platform]
    listed = client.get(f"/api/instructions?platform={platform}").json()
    assert {i["device"] for i in listed} == {"web", "ios", "android"}
