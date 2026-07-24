"""The starter specialists: one named domain expert per condition, seeded
so a fresh Guardian deployment attributes guidance to a specialist from
day one instead of an anonymous registry."""

from jim import conditions
from jim.seed import SPECIALISTS
from jim.tests.conftest import enroll

ALL_CONDITIONS = {
    conditions.ANXIETY, conditions.DEPRESSION, conditions.STRESS,
    conditions.PHOBIA, conditions.FINANCIAL_STRESS, conditions.RELATIONSHIP,
    conditions.PHYSICAL_DISTRESS, conditions.PHYSICAL_INJURY,
    conditions.CARDIAC, conditions.ENVIRONMENT, conditions.ERGONOMIC,
    conditions.FRUSTRATION,
}


def test_starters_cover_every_condition():
    assert set(SPECIALISTS) == ALL_CONDITIONS
    labels = list(SPECIALISTS.values())
    assert len(labels) == len(set(labels))            # distinct experts
    assert all(" — " in label for label in labels)    # name + credential


def test_seed_registers_and_lists(client):
    r = client.post("/specialists/seed")
    assert r.status_code == 201, r.text
    out = r.json()
    assert out["created"] == len(SPECIALISTS) and out["skipped"] == 0

    rows = client.get("/specialists").json()
    assert {row["condition"] for row in rows} == ALL_CONDITIONS
    by_condition = {row["condition"]: row for row in rows}
    cardiac = by_condition[conditions.CARDIAC]
    assert cardiac["label"] == SPECIALISTS[conditions.CARDIAC]
    # Local mode: attribution without requiring a QRME deployment.
    assert all(row["mode"] == "local" for row in rows)


def test_seed_is_idempotent_and_preserves_operator_overrides(client):
    client.post("/specialists/seed")
    # Operator upgrades one entry to tandem with a QRME profile.
    client.post("/specialists", json={
        "condition": conditions.ANXIETY, "mode": "tandem",
        "label": "Dr. Lena Whitcomb — clinical psychologist, anxiety & panic",
        "qrme_profile_id": "prf_custom"})
    second = client.post("/specialists/seed").json()
    assert second["created"] == 0
    assert second["skipped"] == len(SPECIALISTS)
    upgraded = {row["condition"]: row
                for row in client.get("/specialists").json()}
    assert upgraded[conditions.ANXIETY]["mode"] == "tandem"
    assert upgraded[conditions.ANXIETY]["qrme_profile_id"] == "prf_custom"


def test_guidance_names_the_seeded_specialist(client):
    client.post("/specialists/seed")
    user = enroll(client)
    body = client.post(f"/monitor/{user}",
                       json={"rhythm": "fibrillation"}).json()
    assert body["condition"] == conditions.CARDIAC
    g = body["guidance"]
    assert g["source"] == "local"
    assert g["specialist"] == SPECIALISTS[conditions.CARDIAC]


def test_unseeded_guidance_carries_no_specialist(client):
    user = enroll(client)
    g = client.post(f"/monitor/{user}",
                    json={"heart_rate": 130, "respiratory_rate": 24}
                    ).json()["guidance"]
    assert "specialist" not in g
