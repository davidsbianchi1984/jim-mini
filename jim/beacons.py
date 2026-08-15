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

# What the finder reads after pressing the button — derived from what
# actually happened, never asserted. This used to be one unconditional
# sentence, "the people watching over this person have been alerted", while
# the function it capped sent nothing to anyone: no mail, no page, no ledger
# row — the alert only existed inside an app the contact may never open. A
# stranger who walks away from a person on the ground believing help is
# coming, because a QR page said so, is the worst failure this feature has.
NOTE_SENT = ("A message has been sent to the people watching over this "
             "person. If this is an emergency, call your local emergency "
             "number — this page cannot.")
NOTE_MINOR_SENT = ("This person's guardian has been sent a message. If this "
                   "is an emergency, call your local emergency number.")
# One sentence for every way a message can fail to go out — contact set but
# unreachable from here, mail undelivered, or nobody set up at all. The
# difference matters to the owner, who reads it in the pages ledger; telling
# a stranger at the door which of the three it was would publish how watched
# this person is, which is the question a beacon must never answer.
NOTE_UNSENT = ("No message went out from this page — the alarm is recorded "
               "on this person's account. If this is an emergency, call "
               "your local emergency number yourself; this page cannot "
               "call anyone.")


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


def _reachable(user: dict, minor: bool) -> tuple[str | None, str | None]:
    """Who to page for this person, and a mailable address when one exists.

    The name is for the ledger, never for the stranger. A minor's page goes
    to the guardian inbox that verified their consent; an adult's goes to
    the trusted channel they armed their own crash watch with — the person
    they themselves designated to be woken. An emergency contact who is
    only a phone number is still a name worth recording an attempt against,
    because the morning-after ledger exists precisely to show the message
    that never went out.
    """
    if minor:
        email = (user.get("guardian_email") or "").strip()
        return (user.get("emergency_name") or "guardian",
                email if "@" in email else None)
    from . import crashwatch
    watch = crashwatch.status(user["id"])
    channel = (watch.get("trusted_channel") or "").strip()
    if watch.get("armed") and "@" in channel:
        return watch["trusted_name"], channel
    if user.get("emergency_name") or user.get("emergency_phone"):
        return (user.get("emergency_name") or "emergency contact"), None
    return None, None


def _page_out(alarm_id: str, user_id: str, responder: str,
              address: str | None, user: dict, label: str,
              role: str) -> str:
    """One attempt to reach the person the note talks about, in the ledger.

    The same ledger the workplace relay and the crash watch write, with this
    alarm's real id — so "What went out" shows a beacon's page beside
    everybody else's, and a page that could not be sent is a `queued` row
    rather than a silence.
    """
    from . import mailer
    name = user.get("display_name") or "someone"
    delivery = "queued"
    if address and mailer.configured_transport() == "smtp":
        body = (f"This is {name}'s JIM Guardian. A passer-by pressed the "
                f"alarm on their care beacon '{label}'. They asked that you "
                "be contacted when exactly this happens — please treat it "
                "as real until they tell you otherwise. If you believe this "
                "is an emergency, call your local emergency number "
                "yourself; this message cannot.")
        try:
            mailer.deliver(address, f"{name} may need help — a care beacon "
                           "was pressed", body)
            delivery = "sent"
        except Exception:  # noqa: BLE001 — the alarm stands, undelivered
            delivery = "failed"
    conn = db.connect()
    now = db.utcnow()
    conn.execute(
        "INSERT INTO relay_pages (id, alarm_id, user_id, responder, role,"
        " on_shift, state, attempts, last_error, created_at, sent_at)"
        " VALUES (?,?,?,?,?,1,?,?,NULL,?,?)",
        (db.new_id("page"), alarm_id, user_id, responder, role, delivery,
         1 if delivery != "queued" else 0, now,
         now if delivery == "sent" else None))
    conn.commit()
    return delivery


def _ever_sent(alarm_id: str) -> bool:
    """Whether any page for this alarm actually left the building — what a
    second finder is told, instead of a recount of the first one's raise."""
    return db.connect().execute(
        "SELECT 1 FROM relay_pages WHERE alarm_id=? AND state='sent'"
        " LIMIT 1", (alarm_id,)).fetchone() is not None


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
        # Actually try to reach somebody, and record the attempt either way.
        # The cooldown coalesces a second finder into the open alarm above,
        # so the page goes out once per alarm rather than once per press.
        # Never for a site beacon: a worker's personal emergency contact is
        # the wrong recipient for a workplace incident (see jim/relay.py) —
        # the roster relay is that deployment's answer, worked through its
        # own escalate loop.
        if row["kind"] != "site":
            responder, address = _reachable(user, minor)
            if responder:
                _page_out(alarm_id, row["user_id"], responder, address, user,
                          row["label"], "guardian" if minor
                          else "emergency contact")

    sent = _ever_sent(alarm_id)
    out = {
        "alarm": alarm_id,
        "raised": True,
        "joined_existing": joined,
        "tier": tier,
        "badge": BADGE_AFTER,
        "call_emergency_services_yourself": True,
        "message_sent": sent,
        "note": NOTE_SENT if sent else NOTE_UNSENT,
    }

    if minor:
        # A minor's beacon never opens the clinical stage, to anyone. A
        # responder needing a child's history has the child's own Medical ID
        # and a parent on the phone within seconds of this alarm; a stranger
        # holding a backpack does not get one for tapping a button.
        out["medical_id"] = None
        out["minor"] = True
        out["routed_to"] = "guardian"
        out["note"] = NOTE_MINOR_SENT if sent else NOTE_UNSENT
    else:
        out["medical_id"] = _medical_id_for(row["user_id"])
    return out


def alarms_for(user_id: str, open_only: bool = False) -> list[dict]:
    """Every alarm this beacon owner has had, for the answering queue.

    The rows carry ``call_emergency_services_yourself`` for the same reason
    :func:`alarm` hands it to the stranger: a beacon alarm is ceilinged at
    :data:`ALARM_TIER` and this product cannot place a call at any tier. The
    finder's page has said so since it shipped; the queue the *carer* reads
    showed a tier and never mentioned the ceiling that produced it. One alarm,
    two readers, and only one of them was told.
    """
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
        # Structural rather than a judgement about this particular alarm.
        "call_emergency_services_yourself": True,
        "clipped_by_ceiling": r["tier"] == ALARM_TIER,
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
