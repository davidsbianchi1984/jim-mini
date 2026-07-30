"""The attach bracket's supply line: GET /specialists/catalog.

The field ask, verbatim: "make a bracket for users to click on that can
attach one of those 33 preloaded synthetic profiles from QRME that has
knowledge in their specific industry". The catalog is what the bracket
renders — every condition beside its current attachment, and the QRME
Starter Collection cards to pick a replacement from.
"""

from jim.tests.conftest import FakeQRME


def test_catalog_needs_a_tandem(client):
    """Standalone JIM has no shelf to stock the bracket from — say so
    plainly, pointing at the knob that fixes it."""
    r = client.get("/specialists/catalog")
    assert r.status_code == 409
    assert "JIM_QRME_URL" in r.json()["detail"]


def test_catalog_lists_every_condition_and_the_starter_shelf(make_tandem):
    tc = make_tandem()
    body = tc.get("/specialists/catalog").json()

    # Every condition the guardian routes guidance for, none attached yet.
    conditions = {row["condition"] for row in body["conditions"]}
    assert {"anxiety", "depression", "stress", "phobia", "financial_stress",
            "relationship", "physical_distress", "physical_injury"} == conditions
    assert all(row["attached"] is None for row in body["conditions"])

    # The starter shelf is QRME's own discovery cards, passed through whole
    # — faces, industries, blurbs — so the console renders real cards.
    starters = body["starters"]
    assert len(starters) == len(FakeQRME.starter_handles)
    assert {"profile_id", "display_name", "tags", "blurb", "avatar"} <= set(
        starters[0])
    # And the console can absolutize QRME-relative avatar paths.
    assert body["qrme_url"] is None or body["qrme_url"].startswith("http")
    assert "knowledge pack" in body["note"]


def test_attach_round_trip_shows_in_the_catalog(make_tandem):
    tc = make_tandem()
    r = tc.post("/specialists", json={
        "condition": "anxiety", "mode": "tandem",
        "qrme_profile_id": "prf_dr_lena_whitcomb",
        "label": "dr_lena_whitcomb"})
    assert r.status_code in (200, 201), r.text

    by_condition = {row["condition"]: row["attached"]
                    for row in tc.get("/specialists/catalog").json()["conditions"]}
    attached = by_condition["anxiety"]
    assert attached["mode"] == "tandem"
    assert attached["qrme_profile_id"] == "prf_dr_lena_whitcomb"
    assert by_condition["depression"] is None    # nobody else moved


def test_catalog_survives_a_bare_marketplace(make_tandem, monkeypatch):
    """A QRME that can't serve discovery cards (older build, network blip)
    must not take the whole bracket down — the conditions still list."""
    monkeypatch.setattr(FakeQRME, "get",
                        lambda self, path, headers=None: (_ for _ in ()).throw(
                            ConnectionError("marketplace down")))
    tc = make_tandem()
    body = tc.get("/specialists/catalog").json()
    assert body["starters"] == []
    assert len(body["conditions"]) == 8
