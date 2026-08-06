import pytest
from fastapi.testclient import TestClient

from jim import db as jim_db


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """JIM-mini running standalone (no tandem)."""
    monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
    monkeypatch.setenv("JIM_LLM", "stub")
    monkeypatch.delenv("JIM_QRME_URL", raising=False)
    jim_db.reset()
    from jim.api import create_app

    with TestClient(create_app()) as c:
        yield c
    jim_db.reset()


class _Resp:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self._payload = payload

    def json(self):
        return self._payload


class FakeQRME:
    """A stand-in for a running QRME service, at the HTTP-client boundary.

    Implements just the two endpoints jim/qrme_client.py calls: create an
    interactor and chat with a specialist profile. ``hold=True`` simulates a
    QRME profile whose moderation holds the reply for owner approval.
    """

    def __init__(self, hold=False):
        self.hold = hold
        self._n = 0

    def post(self, path, json=None, headers=None):
        if path == "/interactors":
            self._n += 1
            return _Resp(201, {"id": f"usr_fake{self._n}"})
        if path.startswith("/profiles/") and path.endswith("/chat"):
            if self.hold:
                return _Resp(200, {"profile_message": {
                    "content": None, "status": "pending",
                    "flag_reason": "owner approval required"}})
            msg = (json or {}).get("message", "")
            return _Resp(200, {"profile_message": {
                "content": f"[QRME specialist] I hear you. ({msg[:40]})",
                "status": "approved", "flag_reason": None}})
        return _Resp(404, {})

    # The QRME Starter Collection handles this fake can resolve, mirroring
    # the real deployment's seeded marketplace.
    starter_handles = ("marcus_bell", "dr_amara_osei", "dr_lena_whitcomb",
                       "dr_marcus_adeyemi", "dr_priya_nair")

    def get(self, path, headers=None):
        if path.startswith("/summon"):
            from urllib.parse import parse_qs, urlparse
            ref = parse_qs(urlparse(path).query).get("ref", [""])[0]
            handle = ref.lstrip("@")
            if handle in self.starter_handles:
                return _Resp(200, {"type": "handle", "profile": {
                    "profile_id": f"prf_{handle}",
                    "display_name": handle, "chat": True}})
            return _Resp(404, {"detail": "unknown handle"})
        if path == "/rooms":
            # Shaped like QRME's real GET /rooms.
            return _Resp(200, [
                {"id": "rm_night", "topic": "Night shift, still awake",
                 "channel": "chat", "participants": 4,
                 "created_at": "2026-07-30T00:00:00+00:00"},
                {"id": "rm_walk", "topic": "Tuesday walking group — Bend",
                 "channel": "voice", "participants": 7,
                 "created_at": "2026-07-29T00:00:00+00:00"},
            ])
        if path == "/feed" or path.startswith("/feed?"):
            # Shaped like QRME's real GET /feed, including the two fields
            # JIM must pass through rather than recompute: `plays`, and the
            # sentence a room or a desk says before it is pressed.
            return _Resp(200, {
                "items": [
                    {"kind": "video", "id": "pst_bench", "plays": True,
                     "loop": True, "src": "/media/med_bench",
                     "title": "The bench, finished",
                     "profile": {"profile_id": "prf_otis", "name": "Otis"},
                     "reason": "posted publicly on the wall",
                     "note": "This deployment holds this file, so it plays here.",
                     "at": "2026-08-06T10:00:00+00:00"},
                    {"kind": "offsite", "id": "pst_song", "plays": False,
                     "loop": False, "title": "A song",
                     "facade": {"platform": "youtube",
                                "platform_name": "YouTube",
                                "video_id": "dQw4w9WgXcQ",
                                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"},
                     "reason": "posted publicly on the wall",
                     "note": "It stays a card until you press play.",
                     "at": "2026-08-06T09:00:00+00:00"},
                    {"kind": "room", "id": "rm_night", "plays": False,
                     "topic": "Night shift, still awake", "channel": "chat",
                     "people": 4, "display_name": "Otis Marsh",
                     "entering": "Walking in puts you in the room with the "
                                 "people already there.",
                     "enter": "/rooms/rm_night/join", "reason": "live right now",
                     "at": "2026-08-06T08:00:00+00:00"},
                    {"kind": "desk", "id": "dsk_otis", "plays": False,
                     "display_name": "Otis Marsh", "trade": "Carpentry",
                     "presence": "attended", "human": True, "ai": False,
                     "ringing": "Ringing reaches a person.",
                     "ring": "/desks/dsk_otis/bell",
                     "shop": {"shop_id": "shp_1", "name": "Marsh & Daughter",
                              "offerings": [{"id": "off_1", "kind": "goods",
                                             "title": "Oak bench",
                                             "price": 240.0,
                                             "currency": "USD"}],
                              "open": "/shops/shp_1"},
                     "reason": "a person is at this desk",
                     "at": "2026-08-06T07:00:00+00:00"},
                ],
                "cursor": None,
                "counts": {"video": 1, "offsite": 1, "room": 1, "desk": 1},
                "rules": {"plays": "QRME holds it, so it plays.",
                          "facade": "Anything it does not hold stays a card.",
                          "public": "Everything here was posted publicly."},
            })
        if path == "/marketplace/localities":
            return _Resp(200, [{"locality": "Bend, OR", "listings": 3},
                               {"locality": "Portland, OR", "listings": 11}])
        if path == "/marketplace" or path.startswith("/marketplace?"):
            # Discovery cards shaped like QRME's real /marketplace response.
            return _Resp(200, [
                {"profile_id": f"prf_{h}", "display_name": h,
                 "purpose": "starter specialist", "tags": ["mental_health"],
                 "blurb": "a QRME Starter Collection expert",
                 "avatar": f"/photos/starters/{h}.png",
                 "avatar_kind": "ai"}
                for h in self.starter_handles])
        return _Resp(404, {})


@pytest.fixture()
def make_tandem(tmp_path, monkeypatch):
    """Factory: a JIM app wired to a FakeQRME through the real QRMEClient."""
    created = []

    def _make(hold=False):
        monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
        monkeypatch.setenv("JIM_LLM", "stub")
        jim_db.reset()
        from jim.api import create_app
        from jim.qrme_client import QRMEClient

        tc = TestClient(create_app(qrme_client=QRMEClient(client=FakeQRME(hold=hold))))
        tc.__enter__()
        created.append(tc)
        return tc

    yield _make
    for tc in created:
        tc.__exit__(None, None, None)
    jim_db.reset()


def enroll(client, **extra):
    # Pro, where the product default is Basic, and deliberately so: most tests
    # here exercise paid capabilities — the watch, early warning, specialists,
    # the QRME tandem — and an account entitled to them is what a real user of
    # those features holds. The gate itself is tested in test_tiers.py, on
    # accounts that are explicitly Basic. Pass plan="basic" to opt back down.
    body = {"display_name": "Jordan", "birthdate": "1995-05-05",
            "terms_consent": True, "resting_heart_rate": 60, "plan": "pro"}
    body.update(extra)
    r = client.post("/enroll", json=body)
    assert r.status_code == 201, r.text
    out = r.json()
    # Hold the user capability so subsequent per-user calls authorize. The
    # most-recently enrolled user's token becomes the client default; tests
    # with several users switch with as_user()/user_header().
    client.headers["authorization"] = f"Bearer {out['user_token']}"
    return out["id"]


def user_header(client_response_or_token) -> dict:
    """Authorization header from a raw user token."""
    return {"authorization": f"Bearer {client_response_or_token}"}


def as_user(client, token) -> None:
    """Make ``token``'s user the client's default caller."""
    client.headers["authorization"] = f"Bearer {token}"
