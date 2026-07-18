"""Tandem: JIM delegates guidance to a QRME specialist over the HTTP client.

Uses a FakeQRME double (conftest) at the client boundary, so the test is
self-contained — it exercises jim/qrme_client.py + the guardian tandem path
without needing a running QRME. (For a full cross-service run against a real
QRME, point JIM at a live QRME via JIM_QRME_URL.)
"""

from jim.tests.conftest import enroll


def test_health_reports_tandem(make_tandem):
    jim = make_tandem()
    assert jim.get("/health").json()["tandem"] is True


def test_guidance_delegated_to_qrme_specialist(make_tandem):
    jim = make_tandem()
    jim.post("/specialists", json={"condition": "anxiety", "mode": "tandem",
                                   "qrme_profile_id": "prf_anx"})
    user = enroll(jim)
    body = jim.post(f"/monitor/{user}",
                    json={"heart_rate": 120, "respiratory_rate": 22,
                          "note": "my chest is tight"}).json()
    g = body["guidance"]
    assert g["source"] == "tandem"
    assert g["qrme_profile_id"] == "prf_anx"
    assert g["delivered"] is True
    assert g["qrme_status"] == "approved"
    assert "[QRME specialist]" in g["content"]


def test_qrme_moderation_hold_is_surfaced(make_tandem):
    jim = make_tandem(hold=True)   # QRME holds the reply for owner approval
    jim.post("/specialists", json={"condition": "anxiety", "mode": "tandem",
                                   "qrme_profile_id": "prf_anx"})
    user = enroll(jim)
    g = jim.post(f"/monitor/{user}",
                 json={"heart_rate": 120, "respiratory_rate": 22}).json()["guidance"]
    assert g["source"] == "tandem"
    assert g["qrme_status"] == "pending"
    assert g["content"] is None
    assert g["delivered"] is False
