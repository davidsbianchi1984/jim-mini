"""The care team is an organization: Guardian coordinates the household.

QRME's operational ecosystem gives an account departments staffed by role
agents that coordinate on one goal. This module is JIM's side of that: the
user links their own QRME organization — a meds desk, a mental-health desk,
whatever they staffed — and names which department speaks for the Guardian.
When concerns *stack* (a personal drift band crossing arriving while
medication adherence is slipping), one reading is no longer one question,
and the Guardian takes the situation to the whole care team as a
coordination goal. The joint plan comes back with provenance and lands in
JIM as a care plan the user can read.

Three rules keep this honest:

- **The user's own credential, explicitly given.** QRME's organization
  routes are owner-only on purpose; JIM never sneaks around that. The user
  pastes their QRME owner token when linking, exactly as tandem_links stores
  the interactor token, and unlinking deletes it.
- **Summaries cross, never raw readings.** The goal names the adherence
  percentage and which band drifted — numbers the care team needs — not the
  sample stream. The vault posture stays JIM's.
- **A care team is not an alarm.** Coordination happens on the calm path
  (drift is a question, not an escalation) and at most once a day; anything
  `conditions.detect` flags is already on the escalation ladder, which no
  coordination replaces.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta

from . import db, meds

COOLDOWN_HOURS = 24
ADHERENCE_FLOOR = 0.75      # a med below this is "slipping"


class CareTeamError(ValueError):
    """Refusal with a reason a person can read."""


def link(user_id: str, org_id: str, department_id: str, owner_token: str,
         qrme) -> dict:
    """Link the household's QRME organization. Validated against QRME at
    link time: the org must be readable with this token and must contain
    the named department — a link that fails a year later, at the moment
    the care team is finally needed, is the failure mode this check exists
    to prevent."""
    if qrme is None:
        raise CareTeamError(
            "no QRME tandem configured on this deployment (QRME_URL)")
    org = qrme.org_view(org_id, owner_token)
    if org is None:
        raise CareTeamError(
            "QRME did not recognize that organization with this token")
    departments = {d["id"]: d for d in org.get("departments", [])}
    if department_id not in departments:
        raise CareTeamError(
            "that department is not part of the organization")
    if len(departments) < 2:
        raise CareTeamError(
            "the care team needs at least two departments to coordinate — "
            "staff another desk in QRME first")
    conn = db.connect()
    conn.execute(
        "INSERT INTO care_teams (user_id, org_id, department_id,"
        " owner_token, created_at) VALUES (?,?,?,?,?)"
        " ON CONFLICT (user_id) DO UPDATE SET org_id=excluded.org_id,"
        " department_id=excluded.department_id,"
        " owner_token=excluded.owner_token",
        (user_id, org_id, department_id, owner_token, db.utcnow()))
    conn.commit()
    return status(user_id)


def unlink(user_id: str) -> None:
    """Remove the link and the stored credential with it."""
    conn = db.connect()
    conn.execute("DELETE FROM care_teams WHERE user_id=?", (user_id,))
    conn.commit()


def _link_row(user_id: str):
    return db.connect().execute(
        "SELECT * FROM care_teams WHERE user_id=?", (user_id,)).fetchone()


def status(user_id: str) -> dict:
    row = _link_row(user_id)
    if row is None:
        return {"linked": False}
    latest = db.connect().execute(
        "SELECT * FROM care_plans WHERE user_id=?"
        " ORDER BY created_at DESC, rowid DESC LIMIT 1",
        (user_id,)).fetchone()
    return {
        "linked": True, "org_id": row["org_id"],
        "department_id": row["department_id"],
        # The token itself never leaves; only the fact one is held.
        "credential_held": bool(row["owner_token"]),
        "latest_plan": _plan_out(latest) if latest else None,
    }


def _plan_out(row) -> dict:
    return {"id": row["id"], "goal": row["goal"], "plan": row["plan"],
            "trigger": json.loads(row["trigger"]),
            "sealed_in_qrme_vault": bool(row["sealed"]),
            "created_at": row["created_at"]}


def plans(user_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM care_plans WHERE user_id=?"
        " ORDER BY created_at, rowid", (user_id,)).fetchall()
    return [_plan_out(r) for r in rows]


def _cooled_down(user_id: str, now: datetime) -> bool:
    latest = db.connect().execute(
        "SELECT created_at FROM care_plans WHERE user_id=?"
        " ORDER BY created_at DESC, rowid DESC LIMIT 1",
        (user_id,)).fetchone()
    if latest is None:
        return True
    last = datetime.fromisoformat(latest["created_at"].replace("Z", "+00:00"))
    return (now - last.replace(tzinfo=None)) >= timedelta(hours=COOLDOWN_HOURS)


def _slipping_meds(user_id: str, now: datetime) -> list[dict]:
    board = meds.adherence(user_id, days=7, now=now)
    out = []
    for med in board.get("adherence_rows", []):
        rate = med.get("rate")
        if rate is not None and rate < ADHERENCE_FLOOR:
            out.append({"name": med.get("name"), "rate": rate})
    return out


def run(user_id: str, goal: str, trigger: dict, qrme) -> dict:
    """One coordination, taken to QRME with the user's own credential."""
    row = _link_row(user_id)
    if row is None:
        raise CareTeamError("no care team linked (PUT /users/{id}/care-team)")
    if qrme is None:
        raise CareTeamError(
            "no QRME tandem configured on this deployment (QRME_URL)")
    out = qrme.coordinate(row["org_id"], goal, row["department_id"],
                          row["owner_token"])
    if out is None:
        raise CareTeamError(
            "QRME refused the coordination — the link may be stale; relink "
            "with a fresh owner token")
    conn = db.connect()
    plan_id = db.new_id("cpl")
    conn.execute(
        "INSERT INTO care_plans (id, user_id, coordination_id, goal, plan,"
        " trigger, sealed, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (plan_id, user_id, out.get("id"), goal, out.get("plan"),
         json.dumps(trigger), int(bool(out.get("sealed"))), db.utcnow()))
    conn.commit()
    return _plan_out(conn.execute(
        "SELECT * FROM care_plans WHERE id=?", (plan_id,)).fetchone())


def coach_context(user_id: str,
                  now: "datetime | None" = None) -> list[str]:
    """What the coach should know, one line — a guardian who chats about
    your week without mentioning that your whole care team just wrote you
    a plan isn't paying attention. Context only: the goal, never the plan
    text, and nothing older than a week."""
    now = now or datetime.now()
    latest = db.connect().execute(
        "SELECT goal, created_at FROM care_plans WHERE user_id=?"
        " ORDER BY created_at DESC, rowid DESC LIMIT 1",
        (user_id,)).fetchone()
    if latest is None:
        return []
    landed = datetime.fromisoformat(
        latest["created_at"].replace("Z", "+00:00")).replace(tzinfo=None)
    age = now - landed
    if age > timedelta(days=7):
        return []
    when = "today" if age < timedelta(days=1) else f"{age.days} day(s) ago"
    return [f"their care team wrote a joint plan {when} (goal: "
            f"{latest['goal'][:120]}) — worth walking through together if "
            "it hasn't come up, never presented as homework"]


def consider(user_id: str, drifts: list[dict], qrme,
             now: datetime | None = None) -> dict | None:
    """The stacking rule, called from the Guardian's calm path.

    Fires only when a drift-band crossing arrives while at least one
    medication's adherence is below the floor, at most once per
    :data:`COOLDOWN_HOURS`. Returns the care plan when it ran, None
    otherwise — and never raises into the monitor path: a broken tandem
    must not take down biometric ingest."""
    now = now or datetime.now()
    if not drifts or qrme is None or _link_row(user_id) is None:
        return None
    slipping = _slipping_meds(user_id, now)
    if not slipping:
        return None
    if not _cooled_down(user_id, now):
        return None
    metrics = ", ".join(sorted({d.get("metric", "reading") for d in drifts}))
    meds_line = "; ".join(
        f"{m['name']} at {int(round(m['rate'] * 100))}% over the last week"
        for m in slipping)
    goal = (f"{metrics} is drifting outside the personal band while "
            f"medication adherence is slipping ({meds_line}). Coordinate a "
            "gentle plan: what each desk should do this week, and what to "
            "watch for.")
    trigger = {"drifts": drifts, "slipping_meds": slipping,
               "rule": "drift + adherence below "
                       f"{int(ADHERENCE_FLOOR * 100)}%"}
    try:
        return run(user_id, goal, trigger, qrme)
    except CareTeamError:
        return None
