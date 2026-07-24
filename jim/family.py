"""Family: a parent setting up — and watching over — a child's account.

A verified-adult guardian enrolls their child; the consent that a bare
``guardian_consent: true`` flag used to assert is now a *recorded
relationship*: who consented, as what (parent / legal guardian), and when.
The child account starts with protective defaults — ``cautious``
sensitivity, the guardian as the consented emergency contact, cloud
contribution and provider access hard-off — and the guardian gets an
oversight window sized to the child's age:

- **full** (under 13): the whole condition-level event timeline;
- **alerts_only** (13–17): escalations and critical detections only —
  a teenager's check-ins, notes, and everyday guidance stay private.

Two lines never move: the autonomous-resuscitation waiver can never be
signed for a minor — not by the child, not by the guardian — and the
oversight link expires by itself the day the child turns 18.
"""

from __future__ import annotations

import json
from datetime import date, datetime

from . import db, guardian

RELATIONSHIPS = ("parent", "legal_guardian")

# Guardian-consented enrollment still requires the guardian to accept the
# same terms the child cannot: recorded, not implied.
CONSENT_NOTE = ("guardian accepted the terms of use and monitoring consent "
                "on the child's behalf")


def _age(birthdate: str) -> int:
    born = date.fromisoformat(birthdate)
    today = datetime.now().date()
    return today.year - born.year - (
        (today.month, today.day) < (born.month, born.day))


def oversight_for(age: int) -> str:
    return "full" if age < 13 else "alerts_only"


def enroll_child(guardian_user: dict, body: dict) -> dict:
    """The parent-led setup: verify the guardian is an adult, the enrollee a
    minor, then create the child account with protective defaults and the
    recorded consent link."""
    if not guardian_user.get("birthdate") or _age(
            guardian_user["birthdate"]) < 18:
        raise ValueError("only a verified-adult guardian can enroll a child")
    if not body.get("birthdate"):
        raise ValueError("the child's birthdate is required")
    child_age = _age(body["birthdate"].isoformat())
    if child_age >= 18:
        raise ValueError("an adult enrolls themselves — guardian setup is "
                         "for under-18s")
    relationship = body.get("relationship", "parent")
    if relationship not in RELATIONSHIPS:
        raise ValueError("relationship must be parent or legal_guardian")

    child = guardian.enroll({
        "display_name": body["display_name"],
        "birthdate": body["birthdate"],
        "terms_consent": True,             # accepted by the guardian, below
        "guardian_consent": True,
        # Protective defaults: the guardian is the consented emergency
        # contact; data never leaves for the cloud or a provider.
        "emergency_name": guardian_user["display_name"],
        "emergency_phone": body.get("guardian_phone"),
        "contact_consent": bool(body.get("guardian_phone")),
        "provider_consent": False,
        "cloud_contribution": False,
        "resting_heart_rate": body.get("resting_heart_rate"),
        "known_conditions": body.get("known_conditions") or [],
    })
    conn = db.connect()
    conn.execute("UPDATE users SET sensitivity='cautious' WHERE id=?",
                 (child["id"],))
    oversight = oversight_for(child_age)
    conn.execute(
        "INSERT INTO guardian_links (guardian_id, child_id, relationship,"
        " oversight, created_at) VALUES (?,?,?,?,?)",
        (guardian_user["id"], child["id"], relationship, oversight,
         db.utcnow()))
    conn.commit()
    guardian._event(child["id"], "guardian_consent", detail={
        "guardian_id": guardian_user["id"],
        "guardian_name": guardian_user["display_name"],
        "relationship": relationship, "note": CONSENT_NOTE})
    return {**child, "sensitivity": "cautious", "oversight": oversight,
            "relationship": relationship,
            "emergency_contact": guardian_user["display_name"]}


def _link(guardian_id: str, child_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM guardian_links WHERE guardian_id=? AND child_id=?",
        (guardian_id, child_id)).fetchone()
    return dict(row) if row else None


def children_of(guardian_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT l.*, u.display_name, u.birthdate, u.sensitivity FROM"
        " guardian_links l JOIN users u ON u.id = l.child_id"
        " WHERE l.guardian_id=? ORDER BY l.created_at", (guardian_id,)
    ).fetchall()
    out = []
    for r in rows:
        age = _age(r["birthdate"])
        out.append({
            "child_id": r["child_id"], "display_name": r["display_name"],
            "age": age, "relationship": r["relationship"],
            "sensitivity": r["sensitivity"],
            # Oversight follows the child's *current* age, and ends at 18.
            "oversight": ("ended" if age >= 18 else oversight_for(age)),
        })
    return out


# What each oversight tier may see. Teen privacy is the point of the
# narrower list: escalations reach the parent, everyday life does not.
_FULL_EVENTS = ("biometric", "detection", "guidance", "escalation",
                "forecast", "guardian_consent")
_ALERT_EVENTS = ("escalation",)


def child_overview(guardian_id: str, child_id: str) -> dict | None:
    """The guardian's window, sized by oversight tier. None when no link;
    an 'ended' marker once the child is 18 — the window closes itself."""
    link = _link(guardian_id, child_id)
    if link is None:
        return None
    child = guardian.get_user(child_id)
    age = _age(child["birthdate"])
    if age >= 18:
        return {"oversight": "ended", "child_id": child_id,
                "note": "this person is now an adult; guardian oversight "
                        "has ended — the account is theirs alone"}
    oversight = oversight_for(age)
    allowed = _FULL_EVENTS if oversight == "full" else _ALERT_EVENTS
    conn = db.connect()
    events = []
    for row in conn.execute(
            "SELECT type, condition, severity, created_at FROM events"
            " WHERE user_id=? ORDER BY created_at DESC, rowid DESC LIMIT 50",
            (child_id,)).fetchall():
        if row["type"] not in allowed:
            continue
        # Condition-level facts only — never raw notes or payloads.
        events.append(dict(row))
    critical = conn.execute(
        "SELECT COUNT(*) AS n FROM events WHERE user_id=? AND"
        " severity='critical'", (child_id,)).fetchone()["n"]
    return {
        "child_id": child_id, "display_name": child["display_name"],
        "age": age, "oversight": oversight,
        "relationship": link["relationship"],
        "sensitivity": child["sensitivity"],
        "critical_events": critical,
        "events": events,
        "privacy_note": (None if oversight == "full" else
                         "alerts only — this teenager's check-ins, notes, "
                         "and everyday guidance stay private"),
    }


def unlink(guardian_id: str, child_id: str) -> bool:
    """The guardian steps back. The child account (and the recorded consent
    event) remain — only the oversight window closes."""
    conn = db.connect()
    changed = conn.execute(
        "DELETE FROM guardian_links WHERE guardian_id=? AND child_id=?",
        (guardian_id, child_id)).rowcount
    conn.commit()
    return changed > 0
