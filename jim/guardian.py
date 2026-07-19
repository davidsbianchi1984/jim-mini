"""Guardian orchestration: enroll → monitor → guide → escalate.

Runs standalone by default. If a tandem specialist is registered for a
condition and a QRME client is configured, guidance for that condition is
delegated to the QRME specialist profile over HTTP; otherwise JIM generates its
own guidance.
"""

from __future__ import annotations

import json

from . import conditions, db, guidance as local_guidance, life


def _event(user_id, type_, *, condition=None, severity=None, detail=None,
           pdi=None, vault_scope=None):
    conn = db.connect()
    event_id = db.new_id("ev")
    stored = detail or {}
    if pdi is not None and vault_scope and stored:
        # Medical payloads go to the PDI vault; only the key stays local.
        key = life.vault_store(
            pdi, user_id, f"jim/{user_id}/{vault_scope}/{event_id}", stored)
        stored = {"vaulted": True, "pdi_key": key}
    conn.execute(
        "INSERT INTO events (id, user_id, type, condition, severity, detail,"
        " created_at) VALUES (?,?,?,?,?,?,?)",
        (event_id, user_id, type_, condition, severity,
         json.dumps(stored), db.utcnow()),
    )
    conn.commit()
    return {"id": event_id, "type": type_, "condition": condition,
            "severity": severity, "detail": detail or {}}


def enroll(body: dict) -> dict:
    conn = db.connect()
    user_id = db.new_id("usr")
    conn.execute(
        "INSERT INTO users (id, display_name, birthdate, terms_consent,"
        " guardian_consent, emergency_name, emergency_phone, contact_consent,"
        " device_paired, resting_heart_rate, goals, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            user_id, body["display_name"],
            body.get("birthdate").isoformat() if body.get("birthdate") else None,
            int(body["terms_consent"]), int(body.get("guardian_consent", False)),
            body.get("emergency_name"), body.get("emergency_phone"),
            int(body.get("contact_consent", False)),
            int(body.get("device_paired", False)),
            body.get("resting_heart_rate"), body.get("goals"), db.utcnow(),
        ),
    )
    conn.commit()
    return get_user(user_id)


def get_user(user_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM users WHERE id=?", (user_id,)
    ).fetchone()
    return dict(row) if row else None


def register_specialist(body: dict) -> dict:
    conn = db.connect()
    conn.execute(
        "INSERT INTO specialists (condition, mode, label, qrme_profile_id, created_at)"
        " VALUES (?,?,?,?,?)"
        " ON CONFLICT (condition) DO UPDATE SET mode=excluded.mode,"
        " label=excluded.label, qrme_profile_id=excluded.qrme_profile_id",
        (body["condition"], body.get("mode", "local"), body.get("label"),
         body.get("qrme_profile_id"), db.utcnow()),
    )
    conn.commit()
    return dict(conn.execute(
        "SELECT * FROM specialists WHERE condition=?", (body["condition"],)
    ).fetchone())


def _specialist(condition: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM specialists WHERE condition=?", (condition,)
    ).fetchone()
    return dict(row) if row else None


def monitor(user_id: str, sample: dict, note: str | None, qrme=None,
            pdi=None) -> dict:
    """Ingest one sample; run detection → guidance → escalation."""
    user = get_user(user_id)
    if user and user.get("resting_heart_rate") and "resting_heart_rate" not in sample:
        sample = {**sample, "resting_heart_rate": user["resting_heart_rate"]}

    _event(user_id, "biometric",
           detail={**sample, **({"note": note} if note else {})},
           pdi=pdi, vault_scope="medical/biometric")

    detection = conditions.detect(sample, note)
    if detection is None:
        return {"detected": False, "guidance": None, "escalation": None}

    _event(user_id, "detection", condition=detection.condition,
           severity=detection.severity,
           detail={"reason": detection.reason, "signals": detection.signals},
           pdi=pdi, vault_scope="medical/detection")

    result = {
        "detected": True, "condition": detection.condition,
        "severity": detection.severity, "reason": detection.reason,
        "guidance": None, "escalation": None,
    }
    result["guidance"] = _deliver(user_id, user, detection, note, qrme)
    if detection.severity == "critical":
        result["escalation"] = _escalate(user_id, user, detection)
    return result


def _deliver(user_id, user, detection, note, qrme) -> dict:
    spec = _specialist(detection.condition)

    if spec and spec["mode"] == "tandem" and spec["qrme_profile_id"] and qrme is not None:
        delivered = _tandem_guidance(user_id, user, detection, note, spec, qrme)
    else:
        delivered = local_guidance.generate(detection, note)
        if spec and spec["mode"] == "tandem" and qrme is None:
            delivered["note"] = "tandem specialist registered but no QRME endpoint " \
                                "configured; used standalone guidance"

    _event(user_id, "guidance", condition=detection.condition,
           severity=detection.severity, detail=delivered)
    return delivered


def _tandem_guidance(user_id, user, detection, note, spec, qrme) -> dict:
    """Delegate guidance to a QRME specialist profile over HTTP."""
    conn = db.connect()
    link = conn.execute(
        "SELECT qrme_interactor_id FROM tandem_links WHERE user_id=?", (user_id,)
    ).fetchone()
    if link is None:
        interactor_id = qrme.ensure_interactor(user["display_name"], user["birthdate"])
        conn.execute(
            "INSERT INTO tandem_links (user_id, qrme_interactor_id, created_at)"
            " VALUES (?,?,?)", (user_id, interactor_id, db.utcnow()),
        )
        conn.commit()
    else:
        interactor_id = link["qrme_interactor_id"]

    label = conditions.LABELS.get(detection.condition, detection.condition)
    message = (
        f"[Guardian monitoring] The user shows signs of {label} "
        f"({detection.reason})."
        + (f' They said: "{note}".' if note else "")
        + " Please offer brief, supportive guidance."
    )
    reply = qrme.specialist_reply(spec["qrme_profile_id"], interactor_id, message)
    return {
        "delivered": reply["content"] is not None,
        "source": "tandem",
        "qrme_profile_id": spec["qrme_profile_id"],
        "condition": detection.condition,
        "content": reply["content"],           # None if QRME held it for approval
        "qrme_status": reply["status"],
        "qrme_flag_reason": reply.get("flag_reason"),
    }


def _escalate(user_id, user, detection) -> dict:
    contact = None
    if user and user.get("contact_consent") and user.get("emergency_phone"):
        contact = {"name": user.get("emergency_name"), "phone": user["emergency_phone"]}
    escalation = {
        "escalated": True, "condition": detection.condition,
        "reason": detection.reason,
        "notified_emergency_contact": contact is not None,
        "emergency_contact": contact, "live_support": True,
    }
    _event(user_id, "escalation", condition=detection.condition,
           severity="critical", detail=escalation)
    return escalation


def events(user_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM events WHERE user_id=? ORDER BY created_at, rowid", (user_id,)
    ).fetchall()
    out = []
    for row in rows:
        item = dict(row)
        item["detail"] = json.loads(item["detail"])
        out.append(item)
    return out
