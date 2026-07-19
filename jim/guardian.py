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
        " device_paired, resting_heart_rate, goals, known_conditions, devices,"
        " created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            user_id, body["display_name"],
            body.get("birthdate").isoformat() if body.get("birthdate") else None,
            int(body["terms_consent"]), int(body.get("guardian_consent", False)),
            body.get("emergency_name"), body.get("emergency_phone"),
            int(body.get("contact_consent", False)),
            int(body.get("device_paired", False)),
            body.get("resting_heart_rate"), body.get("goals"),
            json.dumps(body.get("known_conditions") or []),
            json.dumps(body.get("devices") or []), db.utcnow(),
        ),
    )
    conn.commit()
    return get_user(user_id)


def get_user(user_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM users WHERE id=?", (user_id,)
    ).fetchone()
    if row is None:
        return None
    user = dict(row)
    user["known_conditions"] = json.loads(user.get("known_conditions") or "[]")
    user["devices"] = json.loads(user.get("devices") or "[]")
    user["personality"] = json.loads(user["personality"]) if user.get("personality") else None
    return user


def declare_condition(user_id: str, condition: str, note: str | None) -> dict:
    """Clause 1/10: receive an indication of a known condition for a user."""
    user = get_user(user_id)
    known = user["known_conditions"]
    if condition not in known:
        known.append(condition)
        conn = db.connect()
        conn.execute("UPDATE users SET known_conditions=? WHERE id=?",
                     (json.dumps(known), user_id))
        conn.commit()
    _event(user_id, "condition_declared", condition=condition,
           detail={**({"note": note} if note else {}), "known_conditions": known})
    return {"user_id": user_id, "known_conditions": known}


def set_personality(user_id: str, prefs: dict) -> dict:
    """Clause 12: adapt the counselor's personality from user input."""
    user = get_user(user_id)
    merged = {**(user["personality"] or {}),
              **{k: v for k, v in prefs.items() if v is not None}}
    conn = db.connect()
    conn.execute("UPDATE users SET personality=? WHERE id=?",
                 (json.dumps(merged), user_id))
    conn.commit()
    return {"user_id": user_id, "personality": merged}


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


def _prior_heart_rates(user_id: str, pdi=None, limit: int = 4) -> list[int]:
    """Recent heart rates for trend analysis, oldest first — read back from
    the PDI vault when samples are vaulted, from local detail otherwise."""
    rows = db.connect().execute(
        "SELECT detail FROM events WHERE user_id=? AND type='biometric'"
        " ORDER BY created_at DESC, rowid DESC LIMIT ?", (user_id, limit),
    ).fetchall()
    out = []
    for row in rows:
        detail = json.loads(row["detail"])
        if detail.get("vaulted") and pdi is not None:
            raw = pdi.get(detail["pdi_key"])
            detail = json.loads(raw) if raw else {}
        if detail.get("heart_rate") is not None:
            out.append(detail["heart_rate"])
    return list(reversed(out))


def start_session(user_id: str, device: str | None) -> dict:
    """Clause 14/20: a login session; the remembered state is per user, so
    any device that starts a session resumes the same conversational thread."""
    conn = db.connect()
    session_id = db.new_id("ses")
    conn.execute(
        "INSERT INTO sessions (id, user_id, device, started_at) VALUES (?,?,?,?)",
        (session_id, user_id, device, db.utcnow()),
    )
    conn.commit()
    prior = conn.execute(
        "SELECT COUNT(*) AS n FROM sessions WHERE user_id=? AND id != ?",
        (user_id, session_id)).fetchone()["n"]
    return {"id": session_id, "device": device, "prior_sessions": prior,
            "memory": _memory_summary(user_id)}


def end_session(user_id: str, session_id: str) -> dict | None:
    conn = db.connect()
    row = conn.execute("SELECT * FROM sessions WHERE id=? AND user_id=?",
                       (session_id, user_id)).fetchone()
    if row is None:
        return None
    conn.execute("UPDATE sessions SET ended_at=? WHERE id=?",
                 (db.utcnow(), session_id))
    conn.commit()
    return {"id": session_id, "ended": True}


def _active_session(user_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM sessions WHERE user_id=? AND ended_at IS NULL"
        " ORDER BY started_at DESC, rowid DESC LIMIT 1", (user_id,)).fetchone()
    return dict(row) if row else None


def _memory_summary(user_id: str) -> str | None:
    """Clause 13/14: remembered state of prior interactions, so guidance is
    consistent across login sessions and devices."""
    conn = db.connect()
    rows = conn.execute(
        "SELECT condition, severity, created_at FROM events"
        " WHERE user_id=? AND type='guidance'"
        " ORDER BY created_at DESC, rowid DESC LIMIT 3", (user_id,),
    ).fetchall()
    if not rows:
        return None
    latest = rows[0]
    label = conditions.LABELS.get(latest["condition"], latest["condition"])
    logins = conn.execute("SELECT COUNT(*) AS n FROM sessions WHERE user_id=?",
                          (user_id,)).fetchone()["n"]
    return (f"{len(rows)} recent guidance deliverie(s) across "
            f"{max(logins, 1)} login session(s); most recently for "
            f"{label} ({latest['severity']}). Keep continuity with what was "
            "already discussed, regardless of which device the user is on.")


def _delivery_channel(user: dict | None, source_device: str | None = None) -> str:
    """Clause 7/18: counsel via the reporting device, the device of the
    active login session, or a paired device — in that order."""
    if source_device:
        return source_device
    if user:
        session = _active_session(user["id"])
        if session and session.get("device"):
            return session["device"]
    devices = (user or {}).get("devices") or []
    if devices:
        return devices[0]
    if (user or {}).get("device_paired"):
        return "smart_watch"
    return "app"


def monitor(user_id: str, sample: dict, note: str | None, qrme=None,
            pdi=None) -> dict:
    """Ingest one sample; run detection → guidance → escalation."""
    user = get_user(user_id)
    if user and user.get("resting_heart_rate") and "resting_heart_rate" not in sample:
        sample = {**sample, "resting_heart_rate": user["resting_heart_rate"]}

    prior_hrs = _prior_heart_rates(user_id, pdi=pdi)
    _event(user_id, "biometric",
           detail={**sample, **({"note": note} if note else {})},
           pdi=pdi, vault_scope="medical/biometric")

    known = (user or {}).get("known_conditions") or []
    detection = conditions.detect(sample, note, known=known)
    if detection is None:
        # Predictive early warning before a condition manifests (clause 2).
        early = conditions.forecast(
            sample.get("heart_rate"),
            sample.get("resting_heart_rate", 70), prior_hrs)
        result = {"detected": False, "guidance": None, "escalation": None,
                  "forecast": None}
        if early is not None:
            _event(user_id, "forecast", condition=early.condition,
                   severity=early.severity,
                   detail={"reason": early.reason, "signals": early.signals},
                   pdi=pdi, vault_scope="medical/forecast")
            life._insight(
                user_id, "suggestion",
                f"Early warning: {early.reason}. A short pause now may head it off.",
                area="mental_health", source="forecast")
            result["forecast"] = {"condition": early.condition,
                                  "reason": early.reason}
        return result

    _event(user_id, "detection", condition=detection.condition,
           severity=detection.severity,
           detail={"reason": detection.reason, "signals": detection.signals},
           pdi=pdi, vault_scope="medical/detection")

    result = {
        "detected": True, "condition": detection.condition,
        "severity": detection.severity, "reason": detection.reason,
        "guidance": None, "escalation": None,
    }
    result["guidance"] = _deliver(user_id, user, detection, note, qrme,
                                  source_device=sample.get("source_device"))
    if detection.severity == "critical":
        result["escalation"] = _escalate(user_id, user, detection)
    return result


def _deliver(user_id, user, detection, note, qrme, source_device=None) -> dict:
    spec = _specialist(detection.condition)

    if spec and spec["mode"] == "tandem" and spec["qrme_profile_id"] and qrme is not None:
        delivered = _tandem_guidance(user_id, user, detection, note, spec, qrme)
    else:
        delivered = local_guidance.generate(
            detection, note, user=user, memory=_memory_summary(user_id))
        if spec and spec["mode"] == "tandem" and qrme is None:
            delivered["note"] = "tandem specialist registered but no QRME endpoint " \
                                "configured; used standalone guidance"
    delivered["delivered_via"] = _delivery_channel(user, source_device)

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
