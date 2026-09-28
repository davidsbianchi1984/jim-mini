from datetime import datetime, timedelta, timezone

import httpx

from conftest import hdr

NOW = datetime.now(timezone.utc)


def x_user(i, bot):
    if bot:
        return {"id": f"b{i}", "username": f"sasha{83920000 + i}", "name": "Sasha",
                "created_at": (NOW - timedelta(days=9)).isoformat().replace("+00:00", "Z"),
                "description": "Crypto giveaway DM me", "public_metrics": {"followers_count": 1, "following_count": 5200},
                "profile_image_url": "https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png"}
    return {"id": f"r{i}", "username": f"real_person_{i}", "name": f"Real Person {i}",
            "created_at": (NOW - timedelta(days=1500 + i)).isoformat().replace("+00:00", "Z"),
            "description": "Teacher, runner", "public_metrics": {"followers_count": 400, "following_count": 300},
            "profile_image_url": f"https://pbs.twimg.com/profile_images/{i}.jpg"}


class FakeX:
    def __init__(self, block_allowed=True):
        self.followers = [x_user(i, False) for i in range(20)] + [x_user(i, True) for i in range(6)]
        self.following = [x_user(100 + i, False) for i in range(5)]
        self.block_allowed = block_allowed
        self.calls = []

    def __call__(self, req: httpx.Request):
        self.calls.append((req.method, req.url.path))
        p = req.url.path
        if p.endswith("/oauth2/token"):
            return httpx.Response(200, json={"access_token": "at", "refresh_token": "rt"})
        if p == "/2/users/me":
            return httpx.Response(200, json={"data": {"id": "42", "username": "me"}})
        if p == "/2/users/42/followers":
            return httpx.Response(200, json={"data": self.followers, "meta": {}})
        if p == "/2/users/42/following" and req.method == "GET":
            return httpx.Response(200, json={"data": self.following, "meta": {}})
        if "/blocking" in p:
            if not self.block_allowed:
                return httpx.Response(403, json={"title": "Forbidden"})
            if req.method == "DELETE":
                target = p.rsplit("/", 1)[-1]
                self.followers = [u for u in self.followers if u["id"] != target]
            return httpx.Response(200, json={"data": {"blocking": req.method == "POST"}})
        if req.method == "DELETE" and "/following/" in p:
            return httpx.Response(200, json={"data": {"following": False}})
        return httpx.Response(404, json={})


def connect(tmp_path, monkeypatch, fake):
    from fastapi.testclient import TestClient

    from botcleaner.api import create_app

    monkeypatch.setenv("X_CLIENT_ID", "cid")
    monkeypatch.setenv("X_REDIRECT_URI", "https://app.example/api/x/callback")
    app = create_app(str(tmp_path / "x.sqlite3"), worker=False, x_http=httpx.Client(transport=httpx.MockTransport(fake)))
    c = TestClient(app)
    tok = c.post("/api/signup", json={"email": "x@example.com"}).json()["token"]
    u = {"Authorization": f"Bearer {tok}"}
    url = c.get("/api/x/connect", headers=u).json()["authorize_url"]
    state = httpx.URL(url).params["state"]
    r = c.get(f"/api/x/callback?code=abc&state={state}", follow_redirects=False)
    assert r.status_code == 307 and r.headers["location"] == "/?connected=x"
    return c, u, app


def test_x_connect_scan_and_one_click_remove(tmp_path, monkeypatch):
    fake = FakeX()
    c, u, app = connect(tmp_path, monkeypatch, fake)
    dash = c.get("/api/me/dashboard", headers=u).json()
    assert dash["x_connected"] and dash["platforms"]["x"]["directions"]["follower"]["connections"] == 26
    bots = c.get("/api/flags?platform=x&tab=likely_bot", headers=u).json()
    assert {b["account_id"] for b in bots} == {f"b{i}" for i in range(6)}
    assert all(b["preselected"] for b in bots)
    # The token is sealed at rest, never stored in the clear.
    from botcleaner import security as sec

    row = app.state.svc.db.one("SELECT user_id, sealed FROM secrets WHERE name='x_access_token'")
    assert bytes(row["sealed"]) != b"at" and len(row["sealed"]) > 12 + 16
    assert sec.unseal(row["sealed"], f"{row['user_id']}:x_access_token") == "at"

    job = c.post("/api/removals", headers=u, json={"platform": "x", "accounts": [{"account_id": b["account_id"], "direction": "follower"} for b in bots]}).json()
    assert job["mode"] == "one_click"
    j = c.post(f"/api/removals/{job['id']}/run", headers=u).json()
    assert j["state"] == "done" and j["counts"] == {"removed": 6}
    assert ("POST", "/2/users/42/blocking") in fake.calls
    assert len(c.get("/api/flags?tab=removed", headers=u).json()) == 6


def test_x_block_not_permitted_falls_back_to_assisted(tmp_path, monkeypatch):
    fake = FakeX(block_allowed=False)
    c, u, _ = connect(tmp_path, monkeypatch, fake)
    bots = c.get("/api/flags?platform=x&tab=likely_bot", headers=u).json()[:2]
    job = c.post("/api/removals", headers=u, json={"platform": "x", "accounts": [{"account_id": b["account_id"], "direction": "follower"} for b in bots]}).json()
    j = c.post(f"/api/removals/{job['id']}/run", headers=u).json()
    assert {i["mode"] for i in j["items"]} == {"assisted"}
    assert all("Assisted" in i["error"] for i in j["items"])
    nxt = c.get(f"/api/removals/{job['id']}/next", headers=u).json()
    assert nxt["state"] == "open" and nxt["item"]["profile_url"].startswith("https://x.com/")


def test_worker_tick_runs_one_click_jobs(tmp_path, monkeypatch):
    fake = FakeX()
    c, u, app = connect(tmp_path, monkeypatch, fake)
    bots = c.get("/api/flags?platform=x&tab=likely_bot", headers=u).json()
    job = c.post("/api/removals", headers=u, json={"platform": "x", "accounts": [{"account_id": b["account_id"], "direction": "follower"} for b in bots]}).json()
    out = app.state.svc.tick()
    assert out["one_click"] == 1
    assert c.get(f"/api/removals/{job['id']}", headers=u).json()["counts"] == {"removed": 6}
    # Unknown OAuth state is rejected.
    assert c.get("/api/x/callback?code=a&state=forged").status_code == 400
