"""The tandem hookup: starter specialists wired to their QRME Starter
Collection counterparts, resolved live by @handle, so seeded guidance can
route through the matching synthetic persona."""

from jim import conditions
from jim.seed import SPECIALISTS, TANDEM_HANDLES, seed_tandem
from jim.tests.conftest import enroll


def test_tandem_map_targets_matching_starters():
    assert TANDEM_HANDLES == {
        conditions.FINANCIAL_STRESS: "marcus_bell",
        conditions.PHYSICAL_DISTRESS: "dr_amara_osei",
    }
    # Each handle's persona is the same named expert as the local starter.
    assert "Marcus Bell" in SPECIALISTS[conditions.FINANCIAL_STRESS]
    assert "Dr. Amara Osei" in SPECIALISTS[conditions.PHYSICAL_DISTRESS]


def test_tandem_seed_links_matching_starters(make_tandem):
    jim = make_tandem()
    jim.post("/specialists/seed")
    r = jim.post("/specialists/seed/tandem")
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["linked"] == 2 and out["unresolved"] == []

    rows = {row["condition"]: row for row in jim.get("/specialists").json()}
    fin = rows[conditions.FINANCIAL_STRESS]
    assert fin["mode"] == "tandem"
    assert fin["qrme_profile_id"] == "prf_marcus_bell"
    assert fin["label"] == SPECIALISTS[conditions.FINANCIAL_STRESS]
    # Conditions without a QRME counterpart stay local.
    assert rows[conditions.CARDIAC]["mode"] == "local"


def test_tandem_seed_is_idempotent_and_keeps_operator_links(make_tandem):
    jim = make_tandem()
    jim.post("/specialists/seed")
    # An operator has already wired physical distress to a custom profile.
    jim.post("/specialists", json={
        "condition": conditions.PHYSICAL_DISTRESS, "mode": "tandem",
        "label": SPECIALISTS[conditions.PHYSICAL_DISTRESS],
        "qrme_profile_id": "prf_custom"})
    first = jim.post("/specialists/seed/tandem").json()
    assert first["linked"] == 1 and first["kept"] == 1
    second = jim.post("/specialists/seed/tandem").json()
    assert second["linked"] == 0 and second["kept"] == 2
    rows = {r["condition"]: r for r in jim.get("/specialists").json()}
    assert rows[conditions.PHYSICAL_DISTRESS]["qrme_profile_id"] == "prf_custom"


def test_financial_stress_routes_through_the_qrme_starter(make_tandem):
    jim = make_tandem()
    jim.post("/specialists/seed")
    jim.post("/specialists/seed/tandem")
    user = enroll(jim)
    body = jim.post(f"/monitor/{user}",
                    json={"note": "I lost my job and can't pay rent"}).json()
    assert body["condition"] == conditions.FINANCIAL_STRESS
    g = body["guidance"]
    assert g["source"] == "tandem"
    assert g["qrme_profile_id"] == "prf_marcus_bell"
    assert g["specialist"] == SPECIALISTS[conditions.FINANCIAL_STRESS]
    assert "[QRME specialist]" in g["content"]


def test_tandem_seed_without_qrme_endpoint_conflicts(client):
    client.post("/specialists/seed")
    r = client.post("/specialists/seed/tandem")
    assert r.status_code == 409
    assert "JIM_QRME_URL" in r.json()["detail"]


def test_unresolved_handles_leave_specialists_local(client):
    client.post("/specialists/seed")

    class _Unreachable:
        def resolve_handle(self, handle):
            return None

    out = seed_tandem(_Unreachable())
    assert out["linked"] == 0 and len(out["unresolved"]) == 2
    rows = {r["condition"]: r for r in client.get("/specialists").json()}
    assert rows[conditions.FINANCIAL_STRESS]["mode"] == "local"
