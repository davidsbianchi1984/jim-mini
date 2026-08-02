"""Did the counseling work? — and what happens when it didn't.

Spec [0039], read as written: "If the counseling is effective in managing the
known condition or concern as determined at 310, the personal guidance system
may resume monitoring the user for physical indications. If the counseling
provided at 308 is not effective, the personal guidance system may alert a
person to provide **live assistance** to the user at 312, such as by
connecting the user to a support person associated with the personal guidance
system or by connecting the user with an emergency contact."

Everything before this module answered the first half of the loop: detect,
guide, escalate. The loop had no closing edge — guidance went out and the
product never asked whether it landed. So a person could be told to breathe,
not get better, and nothing in the system knew.

Now every delivered guidance opens a follow-up. The user answers it in one
tap, and the two answers do different things:

- **it helped** → recorded, and monitoring simply resumes. The record matters
  on its own: guidance that works for this person is worth knowing.
- **it didn't** → the escalation ladder runs again with the
  ``guidance_ineffective`` rung applied, and the reply names the humans who
  can be reached right now — the deployment's own support channel, the crisis
  line when the condition is psychological, the care team, and the emergency
  contact when the tier reaches them.

The honesty rule from the rest of the Guardian holds here too: this app does
not itself place a call, and says so. It hands over names, numbers, and a
briefing, and it tells the truth about which of those actually went out.
"""

from __future__ import annotations

import os

from . import db, escalation

# The deployment's own live-support channel — a real human on the operator's
# side, which is exactly the "support person associated with the personal
# guidance system" the spec names. Unset in a personal deployment, where the
# care team and the emergency contact are the humans available.
_SUPPORT_NAME = os.environ.get("JIM_LIVE_SUPPORT_NAME", "")
_SUPPORT_CHANNEL = os.environ.get("JIM_LIVE_SUPPORT_CHANNEL", "")

# Published crisis lines, for the conditions where the right human is a
# trained one. Not a substitute for emergency services; offered beside them.
_CRISIS_LINE = {"name": "988 Suicide & Crisis Lifeline (US)",
                "channel": "call or text 988",
                "note": "free, 24/7, confidential — trained counselors"}

_PSYCHOLOGICAL = {"anxiety", "depression", "stress", "phobia",
                  "financial_stress", "relationship", "frustration"}


def record(user_id: str, condition: str, severity: str) -> dict:
    """Open a follow-up for guidance just delivered."""
    conn = db.connect()
    row_id = db.new_id("fup")
    conn.execute(
        "INSERT INTO guidance_followups (id, user_id, condition, severity,"
        " asked_at) VALUES (?,?,?,?,?)",
        (row_id, user_id, condition, severity, db.utcnow()),
    )
    conn.commit()
    return {"id": row_id, "condition": condition, "severity": severity,
            "question": "Did that help?"}


def open_for(user_id: str) -> list[dict]:
    """Unanswered follow-ups, newest first — what the app should be asking."""
    rows = db.connect().execute(
        "SELECT id, condition, severity, asked_at FROM guidance_followups"
        " WHERE user_id=? AND answered_at IS NULL"
        " ORDER BY asked_at DESC, rowid DESC", (user_id,)).fetchall()
    return [{**dict(r), "question": "Did that help?"} for r in rows]


def history(user_id: str, limit: int = 20) -> list[dict]:
    rows = db.connect().execute(
        "SELECT id, condition, severity, asked_at, answered_at, helped, note,"
        " escalated_to FROM guidance_followups WHERE user_id=?"
        " ORDER BY asked_at DESC, rowid DESC LIMIT ?", (user_id, limit)).fetchall()
    return [{**dict(r),
             "helped": None if r["helped"] is None else bool(r["helped"])}
            for r in rows]


def live_assistance(user_id: str, condition: str, *,
                    notify_contact: bool, user: dict | None = None) -> dict:
    """The humans reachable right now, and which of them were actually told.

    Named separately from the escalation decision because the decision is a
    tier and this is a list of people — the spec's "support person associated
    with the personal guidance system **or** … emergency contact" is two
    doors, and a person in distress should be shown both.
    """
    from . import guardian, relay

    user = user or guardian.get_user(user_id)
    options: list[dict] = []
    if _SUPPORT_NAME and _SUPPORT_CHANNEL:
        options.append({"kind": "support_person", "name": _SUPPORT_NAME,
                        "channel": _SUPPORT_CHANNEL,
                        "note": "a person on this deployment's own support "
                                "team"})
    if condition in _PSYCHOLOGICAL:
        options.append({"kind": "crisis_line", **_CRISIS_LINE})
    # On a site deployment the nearest human is whoever is actually on shift
    # (jim/rota.py knows the difference between the roster and 2am).
    if relay.available():
        for name in relay.roster():
            options.append({"kind": "site_responder", "name": name,
                            "channel": "",
                            "note": "on shift now, in the order the relay "
                                    "works through"})
    contact_name = (user or {}).get("emergency_name")
    if contact_name:
        options.append({
            "kind": "emergency_contact", "name": contact_name,
            "channel": (user or {}).get("emergency_phone") or "",
            "note": ("alerted" if notify_contact else
                     "on file — not alerted at this tier"),
        })
    return {
        "options": options,
        "contact_alerted": bool(notify_contact and contact_name),
        # The same honesty the companion briefing carries: an app hands over
        # names and a briefing; a phone call is a person's act.
        "note": "these are people, not automations — this app can prepare and "
                "relay information through configured channels, but it cannot "
                "itself place a voice call",
    }


def answer(user_id: str, helped: bool, note: str | None = None) -> dict:
    """Close the newest open follow-up. Not-helped runs the ladder again."""
    from . import guardian

    conn = db.connect()
    row = conn.execute(
        "SELECT id, condition, severity FROM guidance_followups"
        " WHERE user_id=? AND answered_at IS NULL"
        " ORDER BY asked_at DESC, rowid DESC LIMIT 1", (user_id,)).fetchone()
    if row is None:
        return {"answered": False,
                "reason": "no guidance is waiting on an answer"}

    user = guardian.get_user(user_id)
    decision = assistance = None
    escalated_to = None
    if not helped:
        contactable = bool(user and user.get("contact_consent")
                           and user.get("emergency_phone"))
        decision = escalation.decide(
            row["severity"],
            (user or {}).get("sensitivity") or "balanced",
            condition=row["condition"],
            known=(user or {}).get("known_conditions") or [],
            contactable=contactable, guidance_ineffective=True)
        escalated_to = decision["tier"]
        assistance = live_assistance(user_id, row["condition"],
                                     notify_contact=decision["notify_contact"],
                                     user=user)

    conn.execute(
        "UPDATE guidance_followups SET answered_at=?, helped=?, note=?,"
        " escalated_to=? WHERE id=?",
        (db.utcnow(), 1 if helped else 0, note, escalated_to, row["id"]),
    )
    conn.commit()

    guardian._event(
        user_id,
        "guidance_effective" if helped else "guidance_ineffective",
        condition=row["condition"], severity=row["severity"],
        detail={**({"note": note} if note else {}),
                **({"escalated_to": escalated_to} if escalated_to else {})},
    )

    # Whether guidance landed is the one input that says if any of this is
    # working, so it is also the strongest thing the continuity vector reads.
    # The boolean only — never the note, never the condition.
    from . import continuity
    continuity.observe(user_id, "followup", helped=helped)

    out = {"answered": True, "id": row["id"], "helped": helped,
           "condition": row["condition"]}
    if helped:
        # The spec's own words for the effective branch: resume monitoring.
        out["next"] = "monitoring resumes"
        return out
    out["next"] = "live assistance"
    out["escalation_decision"] = decision
    out["live_assistance"] = assistance
    return out
