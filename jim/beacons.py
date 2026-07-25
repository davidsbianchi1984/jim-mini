"""Care beacons — a printed code on the things around a watched person.

QRME's desk beacon puts a QR on a shop door and resolves to a real person who
is simply not behind it this minute, with a bell a stranger can ring. There is
no desk in the Guardian, and inventing one would be cargo-culting the feature
rather than porting it. What this product has is **a person somebody is
watching over**, and the physical anchors that person already leaves lying
around: a fridge door, a wristband, a car window, the frame of a walker.

Three decisions carry this module, and each inverts something.

**The alarm comes before the disclosure.** QRME shows the card freely and puts
the bell underneath, because a tradesperson's name and trade is a shop sign.
Health is not, so the order flips. :func:`card` returns a first name, a
sentence and a button; raising the alarm is the act that turns a passer-by into
a responder, and *that* is what earns them the Medical ID in :func:`alarm`.

The friction objection answers itself: the zero-friction path already ships on
the person's own body — that is exactly what ``/medical-id/{token}`` is for —
so the beacon can afford a gate *because* the ungated card exists alongside it.

**A beacon reports watch status, never subject status.** QRME's desk beacon
exists *to* publish presence. This must publish the opposite. No health state,
no colour-coded dot, no "checked in this morning": *is this person OK right
now* is precisely the question a stalker is asking. And no location, ever — a
beacon is *at* a place by definition, so confirming the person is there is the
whole risk in one field.

**The cooldown coalesces rather than drops.** A spammed alarm does not merely
annoy, it trains a family to ignore the one that matters — but two people
finding the same casualty is the case this exists for, so a second alarm
inside the window joins the open one instead of being discarded.

See docs/beacons.md.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from . import db, escalation, family, guardian

KINDS = ("personal", "site")

# A beacon alarm enters the ladder at notify_contact and may not exceed it.
# The ceiling lives in escalation.py; this is the tier it passes in.
ALARM_TIER = "notify_contact"
COOLDOWN_MINUTES = 15

# The positive claim on the page, before anything is tapped. Absence of a
# confirmation is not a disclosure — a stranger cannot infer from silence that
# nobody was alerted, and the worst failure this feature has is somebody
# walking away from a person on the ground believing the QR handled it.
BADGE_BEFORE = "Scanning this did not call for help."
BADGE_AFTER = "The alarm is raised. This is not an emergency service."


class BeaconError(Exception):
    pass


def _row(beacon_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM care_beacons WHERE id=?", (beacon_id,)).fetchone()
    return dict(row) if row else None


def _out(row: dict) -> dict:
    return {
        "id": row["id"],
        "user_id": row["user_id"],
        "label": row["label"],
        "placement": row["placement"],
        "kind": row["kind"],
        "scans": row["scans"],
        "active": bool(row["active"]),
        "created_at": row["created_at"],
        "scan_url": f"/c/{row['id']}",
        "qr_svg": f"/c/{row['id']}/qr.svg",
    }


def _is_minor(user: dict) -> bool:
    bd = user.get("birthdate")
    return bool(bd) and family._age(bd) < 18


def _guardian_of(child_id: str) -> str | None:
    row = db.connect().execute(
        "SELECT guardian_id FROM guardian_links WHERE child_id=?",
        (child_id,)).fetchone()
    return row["guardian_id"] if row else None


def place(user: dict, label: str, placement: str | None = None,
          kind: str = "personal", placed_by: str | None = None) -> dict:
    """Print this person's watch onto something.

    A minor's beacon is **parent-issued only**. A code on a child's backpack
    scanned by a stranger is its own threat model, and the person who should
    decide it exists is the one already accountable for the account.
    """
    if kind not in KINDS:
        raise BeaconError(f"kind must be one of {', '.join(KINDS)}")
    if not label.strip():
        raise BeaconError(
            "a beacon needs a label so its owner can tell their codes apart "
            "once several are printed and stuck to different things")

    if _is_minor(user):
        gid = _guardian_of(user["id"])
        if gid is None:
            raise BeaconError(
                "this account has no guardian link, and a minor cannot place "
                "their own beacon")
        if placed_by != gid:
            raise BeaconError(
                "only this child's guardian can place a beacon for them")

    bid = db.new_id("cbn")
    conn = db.connect()
    conn.execute(
        "INSERT INTO care_beacons (id, user_id, label, placement, kind,"
        " scans, active, created_at) VALUES (?,?,?,?,?,0,1,?)",
        (bid, user["id"], label.strip(), placement, kind, db.utcnow()))
    conn.commit()
    return _out(_row(bid))


def for_user(user_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM care_beacons WHERE user_id=? ORDER BY created_at, rowid",
        (user_id,)).fetchall()
    return [_out(dict(r)) for r in rows]


def get(beacon_id: str) -> dict | None:
    return _row(beacon_id)


def retire(row: dict) -> dict:
    """Peel it off. The code stops resolving; the account is untouched, and a
    Medical ID card on the person's own body keeps working."""
    conn = db.connect()
    conn.execute("UPDATE care_beacons SET active=0 WHERE id=?", (row["id"],))
    conn.commit()
    return {"id": row["id"], "active": False}


def card(beacon_id: str) -> dict | None:
    """Stage one. What a stranger sees before they do anything.

    Returns ``None`` for a code that never existed or has been retired — the
    caller turns both into the same "nothing here" answer, because somebody
    holding a phone at a dead sticker should not learn which.
    """
    row = _row(beacon_id)
    if row is None or not row["active"]:
        return None

    conn = db.connect()
    conn.execute("UPDATE care_beacons SET scans = scans + 1 WHERE id=?",
                 (beacon_id,))
    conn.commit()

    user = guardian.get_user(row["user_id"])
    if user is None:                       # account erased under a live sticker
        return None

    # A first name and nothing else. Enough to speak to them; not enough to
    # learn anything about them.
    first = (user["display_name"] or "").split()[0] if user["display_name"] else None
    out = {
        "beacon": row["id"],
        "first_name": first,
        "watched": True,
        "note": "Someone is watching over this person through a Guardian.",
        "call_first": ("If this is an emergency, call your local emergency "
                       "number first. This page cannot."),
        "badge": BADGE_BEFORE,
        "alarm_url": f"/c/{row['id']}/alarm",
        # Deliberately absent, and named so it reads as a decision rather than
        # an oversight: no health status, no location, no contact, no age.
        "status": None,
        "location": None,
    }
    if row["kind"] == "site":
        out["site"] = True
        out["note"] = ("This person is covered by a workplace Guardian. "
                       "Raising the alarm reaches whoever is on call.")
    return out


def _open_alarm(beacon_id: str) -> dict | None:
    since = (datetime.now(timezone.utc)
             - timedelta(minutes=COOLDOWN_MINUTES)).isoformat()
    row = db.connect().execute(
        "SELECT * FROM beacon_alarms WHERE beacon_id=? AND state='open'"
        " AND created_at >= ? ORDER BY created_at DESC LIMIT 1",
        (beacon_id, since)).fetchone()
    return dict(row) if row else None


def _medical_id_for(user_id: str) -> dict | None:
    user = guardian.get_user(user_id)
    return guardian._medical_id(user_id, user) if user else None


def alarm(beacon_id: str, message: str | None = None,
          qrme=None) -> dict | None:
    """Stage two. A passer-by raises the people who are watching.

    Anyone can call this — that is the point, and the reason the cooldown
    coalesces rather than gating harder. What it returns depends on who the
    beacon belongs to: an adult's opens the Medical ID, a minor's never does.
    """
    row = _row(beacon_id)
    if row is None or not row["active"]:
        return None
    user = guardian.get_user(row["user_id"])
    if user is None:
        return None

    minor = _is_minor(user)
    said = (message or "").strip()

    open_alarm = _open_alarm(beacon_id)
    conn = db.connect()
    if open_alarm:
        # Join the alarm already running. The second finder is not noise.
        msgs = json.loads(open_alarm["messages"])
        if said:
            msgs.append(said)
            conn.execute("UPDATE beacon_alarms SET messages=? WHERE id=?",
                         (json.dumps(msgs), open_alarm["id"]))
            conn.commit()
        alarm_id, tier, joined = open_alarm["id"], open_alarm["tier"], True
    else:
        # A stranger's alarm is not a detection, so it does not go through
        # severity at all: it enters at notify_contact and is capped there.
        decision = escalation.decide(
            "critical", user.get("sensitivity", "balanced"),
            contactable=bool(user.get("emergency_phone")),
            ceiling=ALARM_TIER)
        tier = decision["tier"]
        alarm_id = db.new_id("alrm")
        conn.execute(
            "INSERT INTO beacon_alarms (id, beacon_id, user_id, messages,"
            " state, tier, created_at) VALUES (?,?,?,?, 'open', ?,?)",
            (alarm_id, beacon_id, row["user_id"],
             json.dumps([said] if said else []), tier, db.utcnow()))
        conn.commit()
        # An escalation event, so it reaches the owner's own timeline and a
        # parent's oversight view under the existing alerts_only / full rules.
        guardian._event(
            row["user_id"], "escalation", severity="critical",
            detail={"source": "care_beacon", "beacon": beacon_id,
                    "tier": tier, "alarm": alarm_id})
        joined = False

    out = {
        "alarm": alarm_id,
        "raised": True,
        "joined_existing": joined,
        "tier": tier,
        "badge": BADGE_AFTER,
        "call_emergency_services_yourself": True,
        "note": ("The people watching over this person have been alerted. "
                 "If this is an emergency, call your local emergency number "
                 "— this page cannot."),
    }

    if minor:
        # A minor's beacon never opens the clinical stage, to anyone. A
        # responder needing a child's history has the child's own Medical ID
        # and a parent on the phone within seconds of this alarm; a stranger
        # holding a backpack does not get one for tapping a button.
        out["medical_id"] = None
        out["minor"] = True
        out["routed_to"] = "guardian"
        out["note"] = ("This person's guardian has been alerted. If this is "
                       "an emergency, call your local emergency number.")
    else:
        out["medical_id"] = _medical_id_for(row["user_id"])
    return out


def alarms_for(user_id: str, open_only: bool = False) -> list[dict]:
    sql = "SELECT * FROM beacon_alarms WHERE user_id=?"
    if open_only:
        sql += " AND state='open'"
    sql += " ORDER BY created_at DESC, rowid DESC"
    return [{
        "id": r["id"],
        "beacon_id": r["beacon_id"],
        "messages": json.loads(r["messages"]),
        "state": r["state"],
        "tier": r["tier"],
        "accepted_by": r["accepted_by"],
        "created_at": r["created_at"],
        "cleared_at": r["cleared_at"],
    } for r in db.connect().execute(sql, (user_id,)).fetchall()]


def clear(user_id: str, alarm_id: str) -> dict | None:
    conn = db.connect()
    changed = conn.execute(
        "UPDATE beacon_alarms SET state='cleared', cleared_at=?"
        " WHERE id=? AND user_id=? AND state='open'",
        (db.utcnow(), alarm_id, user_id)).rowcount
    conn.commit()
    if not changed:
        return None
    return {"id": alarm_id, "state": "cleared"}
