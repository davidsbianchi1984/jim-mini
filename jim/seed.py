"""The starter specialists: one named domain expert per condition.

A fresh JIM deployment has an empty specialist registry — guidance works,
but no named expert stands behind any condition domain. Seeding fixes the
cold start: a curated specialist persona for every condition the Guardian
can detect, registered in ``local`` mode so guidance immediately carries a
"specialist" attribution. Deployments that also run QRME can later upgrade
any entry to ``tandem`` with a QRME profile id (several labels intentionally
match the QRME Starter Collection personas), routing guidance through the
live synthetic specialist.

Seeding is idempotent — conditions that already have a specialist are
skipped — so it is safe to run at every deploy:

    python -m jim.seed          # or POST /specialists/seed
"""

from __future__ import annotations

from . import conditions

# condition -> specialist label (persona + credential, in one line)
SPECIALISTS: dict[str, str] = {
    conditions.ANXIETY:
        "Dr. Lena Whitcomb — clinical psychologist, anxiety & panic",
    conditions.DEPRESSION:
        "Dr. Marcus Adeyemi — psychiatrist, mood disorders",
    conditions.STRESS:
        "Yuki Tanaka — occupational health counselor, stress & burnout",
    conditions.PHOBIA:
        "Dr. Ines Beltran — behavioral therapist, gradual exposure",
    conditions.FINANCIAL_STRESS:
        "Marcus Bell — retired fee-only financial planner",
    conditions.RELATIONSHIP:
        "Dr. Priya Nair — family & couples therapist",
    conditions.PHYSICAL_DISTRESS:
        "Dr. Amara Osei — family physician & health educator",
    conditions.PHYSICAL_INJURY:
        "Sgt. Cole Brennan (ret.) — paramedic, trauma first aid",
    conditions.CARDIAC:
        "Dr. Elena Rios — cardiologist, resuscitation science",
    conditions.ENVIRONMENT:
        "Chief Dana Okafor — fire & hazmat safety officer",
    conditions.ERGONOMIC:
        "Ravi Menon — physical therapist, workplace ergonomics",
    conditions.FRUSTRATION:
        "Sam Porter — productivity coach, focus & flow",
}


# condition -> QRME Starter Collection @handle. Only conditions whose starter
# specialist has a genuine domain counterpart in the QRME collection are
# wired; the rest stay local. Handles (not profile ids) are the stable
# cross-product names — ids differ per QRME deployment, so each link is
# resolved live at hookup time.
TANDEM_HANDLES: dict[str, str] = {
    conditions.FINANCIAL_STRESS: "marcus_bell",
    conditions.PHYSICAL_DISTRESS: "dr_amara_osei",
    conditions.ANXIETY: "dr_lena_whitcomb",
    conditions.DEPRESSION: "dr_marcus_adeyemi",
    conditions.RELATIONSHIP: "dr_priya_nair",
}


def seed() -> dict:
    """Register the starter specialists (idempotent: covered conditions
    skip)."""
    from . import guardian

    created, skipped = [], []
    for condition, label in SPECIALISTS.items():
        if guardian._specialist(condition) is not None:
            skipped.append(condition)
            continue
        guardian.register_specialist(
            {"condition": condition, "mode": "local", "label": label})
        created.append({"condition": condition, "label": label})
    return {"created": len(created), "skipped": len(skipped),
            "conditions": len(SPECIALISTS), "specialists": created}


def seed_tandem(qrme) -> dict:
    """Upgrade starter specialists to tandem mode where the QRME Starter
    Collection carries the same expert, resolving each @handle against the
    connected QRME deployment. Idempotent: a condition already wired to a
    QRME profile (by an operator or a prior run) is kept as-is; a handle
    that doesn't resolve leaves its specialist local."""
    from . import guardian

    linked, unresolved, kept = [], [], 0
    for condition, handle in TANDEM_HANDLES.items():
        spec = guardian._specialist(condition)
        if spec and spec["mode"] == "tandem" and spec["qrme_profile_id"]:
            kept += 1
            continue
        card = qrme.resolve_handle(handle)
        if not card or not card.get("profile_id"):
            unresolved.append({"condition": condition, "handle": f"@{handle}"})
            continue
        guardian.register_specialist({
            "condition": condition, "mode": "tandem",
            "label": (spec or {}).get("label") or SPECIALISTS[condition],
            "qrme_profile_id": card["profile_id"]})
        linked.append({"condition": condition, "handle": f"@{handle}",
                       "qrme_profile_id": card["profile_id"]})
    return {"linked": len(linked), "kept": kept,
            "unresolved": unresolved, "links": linked}


if __name__ == "__main__":
    import json
    import os

    out = seed()
    if os.environ.get("JIM_QRME_URL"):
        from .qrme_client import QRMEClient
        out["tandem"] = seed_tandem(
            QRMEClient(base_url=os.environ["JIM_QRME_URL"]))
    print(json.dumps(out, indent=2))
