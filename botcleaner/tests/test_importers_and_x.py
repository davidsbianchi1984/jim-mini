import io
import json
import zipfile

import httpx
import pytest

from botcleaner.connectors import x as xapi
from botcleaner.importers import ImportError_, import_export
from botcleaner.models import Direction, Platform

IG_FOLLOWERS = [
    {"title": "", "media_list_data": [], "string_list_data": [
        {"href": "https://www.instagram.com/anna.k", "value": "anna.k", "timestamp": 1690000000}]},
    {"title": "", "media_list_data": [], "string_list_data": [
        {"href": "https://www.instagram.com/bot83749201", "value": "bot83749201", "timestamp": 1700000000}]},
]
IG_FOLLOWING = {"relationships_following": [
    {"title": "natgeo", "string_list_data": [{"href": "https://www.instagram.com/_u/natgeo", "timestamp": 1600000000}]},
]}


def zipped(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for k, v in files.items():
            z.writestr(k, v)
    return buf.getvalue()


def test_instagram_zip_export():
    data = zipped({
        "connections/followers_and_following/followers_1.json": json.dumps(IG_FOLLOWERS).encode(),
        "connections/followers_and_following/following.json": json.dumps(IG_FOLLOWING).encode(),
        "your_activity/likes.json": b"{}",
    })
    conns = import_export(Platform.instagram, "instagram.zip", data)
    by = {(c.handle, c.direction) for c in conns}
    assert ("anna.k", Direction.follower) in by
    assert ("natgeo", Direction.following) in by
    assert all(c.connected_at for c in conns)


def test_facebook_friends_and_following():
    friends = {"friends_v2": [{"name": "Maria GarcÃ­a", "timestamp": 1500000000}, {"name": "Tom Lee", "timestamp": 1600000000}]}
    following = {"following_v3": [{"name": "Local Bakery", "timestamp": 1650000000}]}
    data = zipped({"connections/friends/your_friends.json": json.dumps(friends).encode(),
                   "connections/followers/who_you've_followed.json": json.dumps(following).encode()})
    conns = import_export(Platform.facebook, "fb.zip", data)
    names = {(c.name, c.direction) for c in conns}
    assert ("Maria García", Direction.friend) in names  # mojibake repaired
    assert ("Local Bakery", Direction.following) in names
    ids = [c.account_id for c in conns]
    assert len(ids) == len(set(ids))


def test_tiktok_json_and_txt():
    obj = {"Activity": {"Follower List": {"FansList": [{"Date": "2024-01-02 03:04:05", "UserName": "fan1"}]},
                        "Following List": {"Following": [{"Date": "2024-02-02 03:04:05", "UserName": "creator"}]}}}
    conns = import_export(Platform.tiktok, "user_data.json", json.dumps(obj).encode())
    assert {(c.handle, c.direction) for c in conns} == {("fan1", Direction.follower), ("creator", Direction.following)}
    txt = b"Date: 2024-01-02 03:04:05\nUsername: fan2\n\nDate: 2024-01-03 03:04:05\nUsername: fan3\n"
    conns = import_export(Platform.tiktok, "Follower.txt", txt)
    assert [c.handle for c in conns] == ["fan2", "fan3"]


def test_linkedin_csv_with_notes_header():
    csv = ("Notes:\n\"When exporting your connection data, you may notice...\"\n\n"
           "First Name,Last Name,URL,Email Address,Company,Position,Connected On\n"
           "Ada,Lovelace,https://www.linkedin.com/in/ada-l,,Analytical Engines,Engineer,10 Dec 2022\n"
           "Recruiter,Jobs,https://www.linkedin.com/in/recruiter-jobs-83729,,,,01 Jan 2026\n")
    conns = import_export(Platform.linkedin, "Connections.csv", csv.encode())
    assert conns[0].name == "Ada Lovelace" and conns[0].direction == Direction.friend
    assert conns[0].account_id == "ada-l" and conns[0].connected_at.year == 2022


def test_x_archive():
    js = b'window.YTD.follower.part0 = [{"follower": {"accountId": "123", "userLink": "https://twitter.com/intent/user?user_id=123"}}]'
    conns = import_export(Platform.x, "follower.js", js)
    assert conns[0].account_id == "123" and conns[0].direction == Direction.follower


def test_bad_uploads_are_rejected():
    with pytest.raises(ImportError_):
        import_export(Platform.instagram, "x.json", b"not json")
    with pytest.raises(ImportError_):
        import_export(Platform.instagram, "x.zip", zipped({"readme.txt": b"hi"}))


# ---- X API connector --------------------------------------------------------------------

def mock_x(handler):
    return httpx.Client(transport=httpx.MockTransport(handler), base_url="https://api.x.com")


def test_x_pagination_and_profile_fields():
    calls = []

    def handler(req: httpx.Request):
        calls.append(str(req.url))
        if "followers" in req.url.path:
            if "pagination_token" not in req.url.params:
                return httpx.Response(200, json={"data": [{"id": "1", "username": "a", "name": "A", "created_at": "2020-01-01T00:00:00Z",
                                                           "public_metrics": {"followers_count": 5, "following_count": 10},
                                                           "profile_image_url": "https://abs.twimg.com/sticky/default_profile_images/x.png"}],
                                                 "meta": {"next_token": "p2"}})
            return httpx.Response(200, json={"data": [{"id": "2", "username": "b", "name": "B"}], "meta": {}})
        return httpx.Response(200, json={"data": [{"id": "3", "username": "c", "name": "C"}], "meta": {}})

    c = xapi.XClient("tok", http=mock_x(handler), limiter=xapi.RateLimiter(sleep=lambda s: None))
    conns = c.connections("me")
    assert [(x.account_id, x.direction) for x in conns] == [("1", Direction.follower), ("2", Direction.follower), ("3", Direction.following)]
    assert conns[0].has_default_avatar is True and conns[0].following_count == 10
    assert all("Authorization" not in u for u in calls)


def test_x_unfollow_and_remove_follower_and_fallback():
    seen = []

    def handler(req: httpx.Request):
        seen.append((req.method, req.url.path))
        if req.method == "DELETE" and "/following/" in req.url.path:
            return httpx.Response(200, json={"data": {"following": False}})
        if "blocking" in req.url.path:
            return httpx.Response(200, json={"data": {"blocking": req.method == "POST"}})
        return httpx.Response(404)

    c = xapi.XClient("tok", http=mock_x(handler), limiter=xapi.RateLimiter(sleep=lambda s: None))
    assert c.unfollow("me", "9") is True
    assert c.remove_follower("me", "9") is True
    assert ("POST", "/2/users/me/blocking") in seen and ("DELETE", "/2/users/me/blocking/9") in seen

    forbidden = xapi.XClient("tok", http=mock_x(lambda r: httpx.Response(403, json={"title": "Forbidden"})),
                             limiter=xapi.RateLimiter(sleep=lambda s: None))
    with pytest.raises(xapi.NotPermitted):
        forbidden.remove_follower("me", "9")


def test_x_retries_on_429_and_rate_limiter_paces():
    n = {"i": 0}

    def handler(req):
        n["i"] += 1
        if n["i"] == 1:
            return httpx.Response(429, headers={"x-rate-limit-reset": "0"})
        return httpx.Response(200, json={"data": {"id": "me"}})

    slept = []
    c = xapi.XClient("tok", http=mock_x(handler), limiter=xapi.RateLimiter(sleep=slept.append))
    assert c.me()["id"] == "me" and slept

    t = {"now": 0.0}
    waits = []
    rl = xapi.RateLimiter(per_window=2, window=10, sleep=lambda s: (waits.append(s), t.__setitem__("now", t["now"] + s)),
                          clock=lambda: t["now"])
    for _ in range(3):
        rl.wait("e")
    assert waits == [10]


def test_pkce_and_authorize_url():
    p = xapi.PKCE.new()
    url = xapi.authorize_url("cid", "https://app/cb", p)
    assert "code_challenge_method=S256" in url and p.state in url and "follows.write" in url.replace("+", " ")
    assert p.verifier != p.challenge
