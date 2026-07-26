"""Reaching a real clinician through the tandem.

JIM matches by expertise and locality and asks QRME to assemble the summary.
It never holds the signing credential and never relays the assertion — those
belong to QRME, and the tests below say so out loud, because a guardian
product that could mint the consent for releasing its own user's health
record would be exactly the wrong shape.
"""

import pytest
from fastapi.testclient import TestClient

from jim import db as jim_db
from jim.tests.conftest import _Resp, enroll


class FakeQRMEReferrals:
    """A QRME double speaking the referral surface."""

    def __init__(self, providers=None, prepare_fails=False):
        self.providers = providers if providers is not None else [
            {"id": "prv_near", "name": "Near Cardio", "area": "medical",
             "location": "Leeds", "in_your_area": True,
             "match": "area and location"},
            {"id": "prv_far", "name": "Far Cardio", "area": "medical",
             "location": "Truro", "in_your_area": False,
             "match": "area of expertise"},
        ]
        self.prepare_fails = prepare_fails
        self.token = "itok_1"
        self.match_calls = []
        self.prepared = []

    def post(self, path, json=None, headers=None):
        if path == "/interactors":
            return _Resp(201, {"id": "usr_q1", "token": self.token})
        if path.endswith("/chat"):
            return _Resp(200, {"profile_message": {
                "content": "[QRME specialist] I hear you.",
                "status": "approved", "flag_reason": None}})
        if path == "/referrals/prepare":
            if (headers or {}).get("authorization") != f"Bearer {self.token}":
                return _Resp(403, {"detail": "not authorized"})
            if self.prepare_fails:
                return _Resp(422, {"detail": "nothing to refer yet"})
            self.prepared.append(json)
            return _Resp(201, {
                "referral_id": "ref_1", "clinician": "Near Cardio",
                "area": "medical",
                "package": {"user": "Jordan", "clinician": "Near Cardio",
                            "specialist": {"name": "Dr W", "synthetic": True},
                            "recent_exchange": [{"role": "interactor",
                                                 "content": "tight chest"}]},
                "display_text": "Release 1 message ... to Near Cardio",
                "sign": {"envelope_id": "env_1", "challenge": "Y2g",
                         "tier": "high", "user_verification": "required"},
            })
        return _Resp(404, {})

    def get(self, path, headers=None):
        if path.startswith("/referrals/match"):
            self.match_calls.append(path)
            from urllib.parse import parse_qs, urlparse
            q = parse_qs(urlparse(path).query)
            area = q.get("area", [""])[0]
            return _Resp(200, [p for p in self.providers if p["area"] == area])
        if "/memory/" in path:
            return _Resp(200, [])
        if path.startswith("/profiles/"):
            return _Resp(200, {"adult_mode": False, "status": "active"})
        return _Resp(404, {})


@pytest.fixture()
def tandem(tmp_path, monkeypatch):
    def _make(**kw):
        monkeypatch.setenv("JIM_DB", str(tmp_path / "jim.db"))
        monkeypatch.setenv("JIM_LLM", "stub")
        jim_db.reset()
        from jim.api import create_app
        from jim.qrme_client import QRMEClient

        fake = FakeQRMEReferrals(**kw)
        c = TestClient(create_app(qrme_client=QRMEClient(client=fake)))
        c.__enter__()
        for cond in ("physical_distress", "anxiety"):
            c.post("/specialists", json={"condition": cond, "mode": "tandem",
                                         "label": "Dr W",
                                         "qrme_profile_id": "prf_med"})
        uid = enroll(c)
        # One tandem turn creates the link and its token. `tandem_links` is
        # keyed by user, not by condition, so any tandem guidance will do —
        # these vitals are the pair the suite already uses for anxiety.
        c.post(f"/monitor/{uid}", json={"heart_rate": 120,
                                        "respiratory_rate": 22})
        return c, uid, fake
    yield _make
    jim_db.reset()


# -- locality ---------------------------------------------------------------

def test_locality_is_a_place_name_and_can_be_cleared(tandem):
    client, uid, _ = tandem()
    assert client.put(f"/users/{uid}/locality",
                      json={"locality": "Leeds"}).json()["locality"] == "Leeds"
    assert client.put(f"/users/{uid}/locality",
                      json={"locality": None}).json()["locality"] is None


def test_matching_passes_the_locality_and_the_mapped_area(tandem):
    client, uid, fake = tandem()
    client.put(f"/users/{uid}/locality", json={"locality": "Leeds"})

    out = client.get(
        f"/users/{uid}/referral/clinicians?condition=physical_distress").json()
    assert out["area"] == "medical"
    assert out["locality"] == "Leeds"
    assert [c["name"] for c in out["clinicians"]] == ["Near Cardio",
                                                      "Far Cardio"]
    assert "location=Leeds" in fake.match_calls[-1]


def test_a_mental_health_condition_looks_in_a_different_area(tandem):
    client, uid, fake = tandem()
    out = client.get(
        f"/users/{uid}/referral/clinicians?condition=anxiety").json()
    assert out["area"] == "mental_health"
    # Nothing registered there in the double, and that is said plainly.
    assert out["clinicians"] == []
    assert "no clinician registered" in out["reason"]


def test_no_locality_still_matches_on_expertise(tandem):
    client, uid, fake = tandem()
    out = client.get(
        f"/users/{uid}/referral/clinicians?condition=physical_distress").json()
    assert out["locality"] is None
    assert out["clinicians"]
    assert "location=" not in fake.match_calls[-1]


def test_without_a_tandem_no_clinicians_and_a_reason(client):
    """Standalone JIM. An empty list with a reason, never a traceback — the
    caller is often a screen somebody opened while unwell."""
    uid = enroll(client)
    out = client.get(
        f"/users/{uid}/referral/clinicians?condition=anxiety").json()
    assert out["clinicians"] == []
    assert "no QRME endpoint" in out["reason"]


# -- preparing --------------------------------------------------------------

def test_prepare_returns_the_package_and_the_challenge_but_releases_nothing(tandem):
    client, uid, fake = tandem()
    out = client.post(f"/users/{uid}/referral/prepare", json={
        "condition": "physical_distress", "provider_id": "prv_near"}).json()

    assert out["prepared"] is True
    assert out["clinician"] == "Near Cardio"
    # The user can read exactly what would go, before anything goes.
    assert out["package"]["recent_exchange"]
    assert out["package"]["specialist"]["synthetic"] is True
    assert "Release 1 message" in out["display_text"]
    # And the ceremony is QRME's, not the Guardian's.
    assert out["sign"]["user_verification"] == "required"
    assert out["sign_with"] == "qrme"
    assert "nothing has been released" in out["note"]


def test_jim_never_sees_a_signature_or_a_link(tandem):
    """The assertion goes from the user's device to QRME. JIM keeps a handle
    and nothing that could release anything."""
    client, uid, fake = tandem()
    client.post(f"/users/{uid}/referral/prepare", json={
        "condition": "physical_distress", "provider_id": "prv_near"})

    row = jim_db.connect().execute(
        "SELECT * FROM referral_requests").fetchone()
    stored = dict(row)
    assert stored["qrme_referral_id"] == "ref_1"
    assert "token" not in stored and "signature" not in stored
    blob = " ".join(str(v) for v in stored.values())
    assert "tight chest" not in blob        # not even the summary

    rows = client.get(f"/users/{uid}/referral/requests").json()
    assert rows[0]["qrme_referral_id"] == "ref_1"
    assert "token" not in rows[0]


def test_a_specialist_qrme_refuses_is_reported_plainly(tandem):
    client, uid, fake = tandem(prepare_fails=True)
    out = client.post(f"/users/{uid}/referral/prepare", json={
        "condition": "physical_distress", "provider_id": "prv_near"}).json()
    assert out["prepared"] is False
    assert "could not prepare" in out["reason"]


def test_no_tandem_specialist_means_no_referral(tandem):
    client, uid, fake = tandem()
    out = client.post(f"/users/{uid}/referral/prepare", json={
        "condition": "phobia", "provider_id": "prv_near"}).json()
    assert out["prepared"] is False
    assert "no tandem specialist" in out["reason"]


def test_preparing_standalone_says_so(client):
    uid = enroll(client)
    out = client.post(f"/users/{uid}/referral/prepare", json={
        "condition": "anxiety", "provider_id": "prv_x"}).json()
    assert out["prepared"] is False
    assert "no QRME endpoint" in out["reason"]


# -- it is PHI --------------------------------------------------------------

def test_another_user_cannot_read_or_prepare_yours(tandem):
    client, uid, fake = tandem()
    enroll(client, display_name="Mal")      # client now holds Mal's token
    assert client.get(
        f"/users/{uid}/referral/clinicians?condition=anxiety").status_code == 403
    assert client.put(f"/users/{uid}/locality",
                      json={"locality": "Leeds"}).status_code == 403
    assert client.post(f"/users/{uid}/referral/prepare", json={
        "condition": "physical_distress",
        "provider_id": "prv_near"}).status_code == 403
