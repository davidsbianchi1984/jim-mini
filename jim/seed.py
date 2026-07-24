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


if __name__ == "__main__":
    import json
    print(json.dumps(seed(), indent=2))
