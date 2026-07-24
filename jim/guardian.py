"""Guardian orchestration: enroll → monitor → guide → escalate.

Runs standalone by default. If a tandem specialist is registered for a
condition and a QRME client is configured, guidance for that condition is
delegated to the QRME specialist profile over HTTP; otherwise JIM generates its
own guidance.
"""

from __future__ import annotations

import hashlib
import json
import secrets
from datetime import date

from . import (conditions, db, earlywarning, escalation,
               guidance as local_guidance, i18n, life, llm, robotics, terms)


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
        " terms_version, terms_accepted_at,"
        " provider_consent, cloud_contribution, guardian_consent,"
        " emergency_name, emergency_phone, contact_consent, device_paired,"
        " resting_heart_rate, goals, known_conditions, devices, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            user_id, body["display_name"],
            body.get("birthdate").isoformat() if body.get("birthdate") else None,
            int(body["terms_consent"]),
            terms.TERMS_VERSION if body["terms_consent"] else None,
            db.utcnow() if body["terms_consent"] else None,
            int(body.get("provider_consent", False)),
            int(body.get("cloud_contribution", False)),
            int(body.get("guardian_consent", False)),
            body.get("emergency_name"), body.get("emergency_phone"),
            int(body.get("contact_consent", False)),
            int(body.get("device_paired", False)),
            body.get("resting_heart_rate"), body.get("goals"),
            json.dumps(body.get("known_conditions") or []),
            json.dumps(body.get("devices") or []), db.utcnow(),
        ),
    )
    conn.commit()
    # Seed the heart-rate baseline from the enrolled resting rate; resting
    # samples will fold in from here (and it stays provisional until enough do).
    if body.get("resting_heart_rate"):
        _seed_baseline(user_id, "heart_rate", float(body["resting_heart_rate"]))
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


SENSITIVITY_LEVELS = ("cautious", "balanced", "assertive")


def set_sensitivity(user_id: str, level: str) -> dict:
    """Tune how readily the Guardian escalates (cautious/balanced/assertive)."""
    if level not in SENSITIVITY_LEVELS:
        raise ValueError(
            f"sensitivity must be one of {', '.join(SENSITIVITY_LEVELS)}")
    conn = db.connect()
    conn.execute("UPDATE users SET sensitivity=? WHERE id=?", (level, user_id))
    conn.commit()
    return {"user_id": user_id, "sensitivity": level}


# -- rolling per-metric baselines (EMA) -------------------------------------

_BASELINE_ALPHA = 0.05
_BASELINE_MIN_SAMPLES = 5      # provisional until this many resting samples


def _is_resting(sample: dict) -> bool:
    """A resting-state reading: low/absent activity level. Only these fold into
    the baseline, so exertion doesn't inflate someone's 'resting' rate.
    ``activity_level`` is the 0 (sedentary) .. 10 (intense) scale; ≤3 counts as
    at-rest. Strings are tolerated for robustness."""
    level = sample.get("activity_level")
    if level is None:
        return True
    if isinstance(level, str):
        return level.lower() in ("low", "rest", "resting", "sedentary", "idle")
    try:
        return float(level) <= 3
    except (TypeError, ValueError):
        return True


def _baseline_row(user_id: str, metric: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM baselines WHERE user_id=? AND metric=?",
        (user_id, metric)).fetchone()
    return dict(row) if row else None


def _seed_baseline(user_id: str, metric: str, value: float) -> None:
    conn = db.connect()
    conn.execute(
        "INSERT OR IGNORE INTO baselines (user_id, metric, value, samples,"
        " updated_at) VALUES (?,?,?,0,?)", (user_id, metric, value, db.utcnow()))
    conn.commit()


def update_baseline(user_id: str, metric: str, value: float) -> dict:
    """Fold a resting sample into the metric's EMA baseline."""
    conn = db.connect()
    row = _baseline_row(user_id, metric)
    if row is None:
        new_val, samples = float(value), 1
        conn.execute(
            "INSERT INTO baselines (user_id, metric, value, samples, updated_at)"
            " VALUES (?,?,?,?,?)",
            (user_id, metric, new_val, samples, db.utcnow()))
    else:
        new_val = row["value"] + _BASELINE_ALPHA * (value - row["value"])
        samples = row["samples"] + 1
        conn.execute(
            "UPDATE baselines SET value=?, samples=?, updated_at=?"
            " WHERE user_id=? AND metric=?",
            (new_val, samples, db.utcnow(), user_id, metric))
    conn.commit()
    return {"metric": metric, "value": round(new_val, 2), "samples": samples,
            "provisional": samples < _BASELINE_MIN_SAMPLES}


def baseline_for(user_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM baselines WHERE user_id=? ORDER BY metric",
        (user_id,)).fetchall()
    return [{"metric": r["metric"], "value": round(r["value"], 2),
             "samples": r["samples"],
             "provisional": r["samples"] < _BASELINE_MIN_SAMPLES} for r in rows]


def _effective_resting_hr(user_id: str, user: dict | None,
                          sample: dict) -> int | None:
    """The resting HR detection should compare against: the learned baseline
    once it is established, otherwise the enrolled seed."""
    if "resting_heart_rate" in sample:
        return sample["resting_heart_rate"]
    bl = _baseline_row(user_id, "heart_rate")
    if bl and bl["samples"] >= _BASELINE_MIN_SAMPLES:
        return round(bl["value"])
    if user and user.get("resting_heart_rate"):
        return user["resting_heart_rate"]
    return None


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


def register_device(user_id: str, body: dict) -> dict:
    """Clause 16: a physical embodiment — wearable, stationary system, or
    networked autonomous device, optionally carrying its own LLM."""
    conn = db.connect()
    device_id = db.new_id("dev")
    conn.execute(
        "INSERT INTO devices (id, user_id, name, kind, transport, has_llm,"
        " linked_to, created_at) VALUES (?,?,?,?,?,?,?,?)",
        (device_id, user_id, body["name"], body["kind"], body.get("transport"),
         int(body.get("has_llm", False)), body.get("linked_to"), db.utcnow()),
    )
    conn.commit()
    return device_lookup(user_id, body["name"])


# ---- robot helpers (jim/robotics.py catalog) -------------------------------

def bind_robot(user_id: str, model: str, name: str | None,
               llm_provider: str | None) -> dict:
    """Bind a catalog robot as a guardian responder. Registers a matching
    devices row so escalation alerts dispatch to the body like any other
    device; the robot additionally receives a role-appropriate directive."""
    spec = robotics.get(model)
    if spec is None:
        raise ValueError(f"unknown robot model '{model}'")
    provider = None
    if spec["llm_capable"]:
        provider = llm_provider or llm.get_choice(user_id)
        if provider not in llm.CHOICES:
            raise ValueError(
                f"llm_provider must be one of {', '.join(llm.CHOICES)}")
    elif llm_provider:
        raise ValueError(f"{spec['label']} cannot run an onboard LLM")

    robot_name = name or spec["label"]
    conn = db.connect()
    robot_id = db.new_id("rob")
    conn.execute(
        "INSERT INTO robots (id, user_id, model, name, llm_provider, status,"
        " created_at) VALUES (?,?,?,?,?,'docked',?)",
        (robot_id, user_id, model, robot_name, provider, db.utcnow()))
    conn.commit()
    register_device(user_id, {
        "name": robot_name, "kind": "autonomous", "transport": "wifi",
        "has_llm": spec["llm_capable"]})
    return {"id": robot_id, "user_id": user_id, "model": model,
            "label": spec["label"], "maker": spec["maker"],
            "kind": spec["kind"], "name": robot_name,
            "llm_provider": provider,
            "escalation_directive": robotics.directive_for(model),
            "first_aid": robotics.first_aid_rating(model),
            "commands": robotics.allowed_commands(model)}


def robots_for(user_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM robots WHERE user_id=? ORDER BY created_at, rowid",
        (user_id,)).fetchall()
    return [{**dict(r),
             "escalation_directive": robotics.directive_for(r["model"]),
             "first_aid": robotics.first_aid_rating(r["model"]),
             "commands": robotics.allowed_commands(r["model"])} for r in rows]


def unbind_robot(user_id: str, robot_id: str) -> dict | None:
    conn = db.connect()
    row = conn.execute(
        "SELECT * FROM robots WHERE id=? AND user_id=?",
        (robot_id, user_id)).fetchone()
    if row is None:
        return None
    conn.execute("DELETE FROM robots WHERE id=?", (robot_id,))
    conn.execute("DELETE FROM devices WHERE user_id=? AND name=?",
                 (user_id, row["name"]))
    conn.commit()
    return {"id": robot_id, "unbound": True}


# ---- autonomous-resuscitation waiver ----------------------------------------
#
# Automatic operation — CPR without an on-scene confirmation, and a fully-
# automatic-AED-class device that delivers a shock on its own rhythm analysis
# — is locked behind a signed liability waiver. Signing is explicit (typed
# legal name + acceptance), revocable at any time, and audited. Without a
# waiver on file, the confirm-gated behavior stands and no shock is ever
# delivered.

WAIVER_KIND = "autonomous_resuscitation"

WAIVER_TERMS = [
    "I authorize my bound, CPR-rated robots to begin hands-only CPR "
    "automatically when a cardiac arrest is detected, without waiting for "
    "an on-scene confirmation.",
    "I authorize the use of a fully-automatic AED: the device analyzes my "
    "heart rhythm and delivers a shock on its own analysis after the robot "
    "verifies everyone is clear — no button press.",
    "I understand a shock is only ever delivered when the AED's rhythm "
    "analysis advises it — never on the robot's own judgement.",
    "I accept liability for automatic operation and waive claims arising "
    "from resuscitation performed in good faith under this authorization.",
    "Emergency services are always called first; automatic operation ends "
    "the moment human responders take over.",
    "I may revoke this waiver at any time, restoring confirm-gated "
    "operation.",
]


def waiver_for(user_id: str) -> dict | None:
    """The active (signed, unrevoked) autonomous-resuscitation waiver."""
    row = db.connect().execute(
        "SELECT * FROM waivers WHERE user_id=? AND kind=? AND revoked=0"
        " ORDER BY signed_at DESC, rowid DESC LIMIT 1",
        (user_id, WAIVER_KIND)).fetchone()
    return dict(row) if row else None


def sign_waiver(user_id: str, signature: str) -> dict:
    conn = db.connect()
    waiver_id = db.new_id("wvr")
    conn.execute(
        "INSERT INTO waivers (id, user_id, kind, signature, signed_at,"
        " revoked) VALUES (?,?,?,?,?,0)",
        (waiver_id, user_id, WAIVER_KIND, signature, db.utcnow()))
    conn.commit()
    _event(user_id, "waiver_signed",
           detail={"kind": WAIVER_KIND, "signature": signature})
    return {"id": waiver_id, "kind": WAIVER_KIND, "signature": signature,
            "signed": True, "terms": WAIVER_TERMS}


def revoke_waiver(user_id: str) -> bool:
    conn = db.connect()
    changed = conn.execute(
        "UPDATE waivers SET revoked=1 WHERE user_id=? AND kind=? AND revoked=0",
        (user_id, WAIVER_KIND)).rowcount
    conn.commit()
    if changed:
        _event(user_id, "waiver_revoked", detail={"kind": WAIVER_KIND})
    return bool(changed)


def _robot_directives(user_id: str, cardiac: bool = False) -> list[dict]:
    """On an escalation, every bound robot gets its role's directive: mobile
    bodies converge on the user, vacuums dock and clear the floor. A cardiac
    escalation upgrades first-aid-rated bodies to their rescue role — perform-
    rated platforms begin hands-only CPR, assist-rated ones fetch the AED and
    coach the pace. Delivering a shock is never a directive: the AED analyzes
    the rhythm and a human presses the button."""
    directives = []
    conn = db.connect()
    waived = cardiac and waiver_for(user_id) is not None
    for r in robots_for(user_id):
        directive = robotics.directive_for(r["model"], cardiac=cardiac,
                                           waived=waived)
        if directive is None:
            continue
        conn.execute("UPDATE robots SET status='responding' WHERE id=?",
                     (r["id"],))
        entry = {"robot": r["name"], "model": r["model"],
                 "directive": directive}
        rating = robotics.first_aid_rating(r["model"])
        if cardiac and rating:
            entry["first_aid"] = rating
            if waived and rating == "perform":
                entry["waiver"] = "autonomous resuscitation pre-authorized"
        directives.append(entry)
    conn.commit()
    return directives


# Commands a robot accepts outside its kind/rating allowlist are refused; the
# first-aid set behaves as follows. Without a signed waiver, starting
# compressions is deliberately a two-step (nobody is touched until someone on
# scene confirms) and no shock is ever delivered. A signed autonomous-
# resuscitation waiver pre-authorizes automatic operation: compressions start
# on detection, and a fully-automatic-AED-class device may shock — but only
# on the AED's own rhythm analysis, after the robot verifies the scene is
# clear.
def _cpr_safeguards(waived: bool) -> list[str]:
    base = ["emergency services are called before compressions begin",
            "compressions pause the moment the AED analyzes or a human "
            "takes over"]
    if waived:
        return base + [
            "automatic operation pre-authorized by the signed "
            "autonomous-resuscitation waiver",
            "a shock is delivered only when the AED's rhythm analysis "
            "advises it, after stand-clear verification — never on the "
            "robot's own judgement",
        ]
    return base + [
        "a person on scene confirmed the need (unresponsive, not breathing "
        "normally)",
        "the robot never delivers a shock — the AED analyzes and a human "
        "presses the button",
    ]


def robot_command(user_id: str, robot_id: str, command: str,
                  arg: str | None = None) -> dict | None:
    """Send one allowlisted command to a bound robot. Returns None when the
    robot doesn't exist; raises ValueError for a command outside the body's
    allowlist or rating."""
    conn = db.connect()
    row = conn.execute("SELECT * FROM robots WHERE id=? AND user_id=?",
                       (robot_id, user_id)).fetchone()
    if row is None:
        return None
    robot = dict(row)
    model = robot["model"]
    allowed = robotics.allowed_commands(model)
    if command not in allowed:
        spec = robotics.get(model) or {}
        raise ValueError(
            f"'{command}' is not permitted for {spec.get('label', model)}; "
            f"allowed: {', '.join(allowed)}")

    waived = waiver_for(user_id) is not None

    result: dict
    status = "active"
    if command == "perform_cpr":
        # Rating already enforced by the allowlist. Without a waiver, the
        # confirm gate is the human-in-the-loop: no compressions until
        # someone on scene says so. A signed waiver pre-authorizes starting.
        if not waived and arg != "confirmed":
            result = {
                "status": "confirmation_required",
                "instruction": "Confirm the person is unresponsive and not "
                               "breathing normally, then resend perform_cpr "
                               "with arg='confirmed'. Compressions never "
                               "start on the robot's own judgement. (A "
                               "signed autonomous-resuscitation waiver "
                               "pre-authorizes automatic starts.)",
                "safeguards": _cpr_safeguards(False),
            }
            status = robot["status"]     # unchanged — nothing was started
        else:
            pace = local_guidance.playbook("cpr")["pace"]
            result = {
                "status": "compressions_started",
                "pace": pace,
                "note": ("pre-authorized by waiver — " if waived and
                         arg != "confirmed" else "")
                        + "hands-only CPR at "
                        f"{pace['compressions_per_minute']}/min; pausing for "
                        "AED analysis and stopping when a human takes over",
                "safeguards": _cpr_safeguards(waived),
            }
            status = "performing_cpr"
    elif command == "auto_defib":
        # Fully-automatic AED: the device decides, the robot clears the
        # scene. Locked behind the signed waiver — without it, defibrillation
        # stays with a semi-automatic AED and a human's button press.
        if not waived:
            raise ValueError(
                "auto_defib requires a signed autonomous-resuscitation "
                "waiver; without one, use fetch_aed / guide_first_aid — the "
                "AED advises and a human presses the button")
        result = {
            "status": "auto_resuscitation_engaged",
            "sequence": [
                "emergency services called",
                "fully-automatic AED pads attached",
                "device analyzing rhythm — compressions paused",
                "robot verifying everyone is clear (vision + audible "
                "warning)",
                "shock delivered automatically ONLY if the device advises "
                "it; otherwise compressions resume",
            ],
            "note": "the AED's rhythm analysis is the only shock decision — "
                    "the robot's role is scene safety",
            "safeguards": _cpr_safeguards(True),
        }
        status = "performing_cpr"
    elif command == "stop_cpr":
        result = {"status": "compressions_stopped",
                  "note": "handed over to the AED / human rescuer"}
        status = "responding"
    elif command == "fetch_aed":
        result = {"status": "queued", "action": "fetch_aed",
                  "note": "retrieving the nearest AED and bringing it to "
                          "the user"}
        status = "responding"
    elif command == "guide_first_aid":
        kind = arg if arg in ("cpr", "aed") else "cpr"
        # Coach in the user's language: the playbook is hand-localized.
        pb = i18n.localize_playbook(local_guidance.playbook(kind),
                                    i18n.effective_language(user_id))
        result = {"status": "coaching", "playbook": pb,
                  "spoken": pb["steps"],
                  "note": ("coaching aloud with the pace cue"
                           if kind == "cpr" else
                           "reading the AED prompts aloud — analysis and "
                           "shock stay with the device and the human")}
        status = "responding"
    elif command == "meet_responders":
        result = {"status": "queued", "action": "meet_responders",
                  "note": "waiting at the entrance to guide EMS to the user"}
        status = "responding"
    else:
        # Generic motion/utility commands are queued for the vendor bridge.
        result = {"status": "queued", "action": command, "arg": arg}
        status = "docked" if command in ("dock", "stop") else "active"

    conn.execute("UPDATE robots SET status=? WHERE id=?", (status, robot_id))
    conn.commit()
    _event(user_id, "robot_command",
           detail={"robot": robot["name"], "model": model,
                   "command": command, "arg": arg, "result": result})
    return {"robot_id": robot_id, "robot": robot["name"], "model": model,
            "command": command, "robot_status": status, **result}


def devices_for(user_id: str) -> list[dict]:
    rows = db.connect().execute(
        "SELECT * FROM devices WHERE user_id=? ORDER BY created_at, rowid",
        (user_id,)).fetchall()
    return [{**dict(r), "has_llm": bool(r["has_llm"])} for r in rows]


def device_lookup(user_id: str, name: str | None) -> dict | None:
    if not name:
        return None
    row = db.connect().execute(
        "SELECT * FROM devices WHERE user_id=? AND name=?"
        " ORDER BY created_at DESC, rowid DESC LIMIT 1",
        (user_id, name)).fetchone()
    if row is None:
        return None
    device = dict(row)
    device["has_llm"] = bool(device["has_llm"])
    return device


def start_session(user_id: str, device: str | None, qrme=None) -> dict:
    """Clause 14/20: a login session; the remembered state is per user, so
    any device that starts a session resumes the same conversational thread —
    including a thread started with a QRME specialist from another product."""
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
            "memory": _memory_summary(user_id),
            "continuity": _tandem_continuity(user_id, qrme)}


def _tandem_continuity(user_id: str, qrme) -> dict | None:
    """Cross-product continuity: if this user already has a conversation
    thread with a QRME specialist, hand the new device the recent turns so
    the same conversation — same interactor, same memory — picks up here."""
    if qrme is None:
        return None
    link = db.connect().execute(
        "SELECT * FROM tandem_links WHERE user_id=?", (user_id,)).fetchone()
    if link is None:
        return None
    spec = db.connect().execute(
        "SELECT qrme_profile_id FROM specialists WHERE mode='tandem'"
        " AND qrme_profile_id IS NOT NULL LIMIT 1").fetchone()
    if spec is None:
        return None
    recent = qrme.thread_memory(spec["qrme_profile_id"],
                                link["qrme_interactor_id"],
                                link["qrme_interactor_token"])
    if not recent:
        return None
    return {
        "with": "qrme_specialist",
        "qrme_profile_id": spec["qrme_profile_id"],
        "qrme_interactor_id": link["qrme_interactor_id"],
        "recent_turns": [{"role": m["role"], "content": m["content"]}
                         for m in recent],
        "note": "the conversation continues here — same thread, same memory",
    }


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
    active login session, or a registered/paired device — in that order."""
    if source_device:
        return source_device
    if user:
        session = _active_session(user["id"])
        if session and session.get("device"):
            return session["device"]
        registered = devices_for(user["id"])
        if registered:
            return registered[0]["name"]
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
    resting = _effective_resting_hr(user_id, user, sample)
    if resting is not None and "resting_heart_rate" not in sample:
        sample = {**sample, "resting_heart_rate": resting}

    prior_hrs = _prior_heart_rates(user_id, pdi=pdi)
    _event(user_id, "biometric",
           detail={**sample, **({"note": note} if note else {})},
           pdi=pdi, vault_scope="medical/biometric")

    known = (user or {}).get("known_conditions") or []
    sensitivity = (user or {}).get("sensitivity") or "balanced"
    detection = conditions.detect(sample, note, known=known,
                                  sensitivity=sensitivity)
    if detection is None:
        # A calm resting-state reading nudges the rolling baseline (clause 2).
        if sample.get("heart_rate") and _is_resting(sample):
            update_baseline(user_id, "heart_rate", sample["heart_rate"])
        # Predictive early warning before a condition manifests (clause 2).
        early = conditions.forecast(
            sample.get("heart_rate"),
            sample.get("resting_heart_rate", 70), prior_hrs)
        result = {"detected": False, "guidance": None, "escalation": None,
                  "forecast": None}
        # Physical abnormality forming: a blood-oxygen slide is flagged while
        # it is still above the detection threshold.
        if sample.get("blood_oxygen") is not None:
            life._trend_point(user_id, "blood_oxygen", sample["blood_oxygen"])
            slipping = life.forecast_spo2(user_id)
            if slipping:
                result["forecast"] = {"condition": "physical_distress",
                                      "reason": slipping["message"]}
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
        # Predictive trend model (jim.earlywarning): project the recent vitals
        # toward their danger thresholds and, when a crossing is coming inside
        # the sensitivity lead-time window, enrich the forecast with a risk
        # score, minutes-to-threshold, and the fit confidence. It reuses the
        # exact heart-rate series the rule above saw so the two agree.
        hr_series = [*prior_hrs, sample["heart_rate"]] if sample.get("heart_rate") else []
        history = {"heart_rate": hr_series,
                   "blood_oxygen": life._recent(user_id, "blood_oxygen", 6)}
        fc = earlywarning.assess(
            history, resting=sample.get("resting_heart_rate", 70),
            sensitivity=sensitivity)
        if fc is not None:
            if result["forecast"] is None:
                # A trend the single-signal rules missed (e.g. a clean HRV or
                # SpO2 slide) — surface it, and note the projected tier.
                decision = escalation.decide(
                    "info", sensitivity, condition=fc.condition, known=known,
                    confidence=fc.confidence)
                result["forecast"] = {"condition": fc.condition,
                                      "reason": fc.reason,
                                      "projected_tier": decision["tier"]}
                _event(user_id, "forecast", condition=fc.condition,
                       severity="info",
                       detail={"reason": fc.reason, **fc.as_dict()},
                       pdi=pdi, vault_scope="medical/forecast")
            # Enrich whatever forecast we have with the quantified trend.
            result["forecast"].update(
                {"risk": fc.as_dict()["risk"],
                 "horizon_min": fc.as_dict()["horizon_min"],
                 "confidence": fc.as_dict()["confidence"]})
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
    # Guardian pause / quiet hours hold *everyday* guidance for a child —
    # critical detections never check the hold: safety never pauses.
    guidance_hold = None
    if detection.severity != "critical":
        from . import family
        guidance_hold = family.hold_reason(user_id)
    if guidance_hold:
        result["guidance"] = {"delivered": False, "held": True,
                              "source": "held", "note": guidance_hold}
        _event(user_id, "guidance_held", condition=detection.condition,
               severity=detection.severity, detail={"reason": guidance_hold})
    else:
        result["guidance"] = _deliver(user_id, user, detection, note, qrme,
                                      source_device=sample.get("source_device"),
                                      pdi=pdi)

    # The escalation decision tree (jim.escalation) resolves this detection to a
    # tier for the user's sensitivity — surfaced on every detection so the UI
    # and the audit trail can see what was chosen and why, escalated or not.
    contactable = bool(user and user.get("contact_consent")
                       and user.get("emergency_phone"))
    crisis = "crisis language" in detection.reason
    decision = escalation.decide(
        detection.severity, sensitivity, condition=detection.condition,
        known=known, contactable=contactable, crisis=crisis)
    result["escalation_decision"] = decision

    # Critical always escalates. In cautious mode, a guidance-level event for a
    # condition the user has *declared* also reaches out — catching it early for
    # someone known to be prone to it.
    cautious_early = (sensitivity == "cautious"
                      and detection.severity == "guidance"
                      and detection.condition in known)
    if detection.severity == "critical" or cautious_early:
        result["escalation"] = _escalate(user_id, user, detection,
                                         decision=decision)
        if cautious_early:
            result["escalation"]["reason"] += " (cautious-mode early outreach)"
    return result


def _age_from(birthdate: str | None) -> int | None:
    if not birthdate:
        return None
    try:
        b = date.fromisoformat(birthdate)
    except ValueError:
        return None
    today = date.today()
    return today.year - b.year - ((today.month, today.day) < (b.month, b.day))


def _medical_id(user_id: str, user: dict | None) -> dict | None:
    """A first-responder Medical ID: condition-level facts, no notes or raw
    biometrics. Available to the user in an emergency without a provider
    consent gate — it is their own information."""
    if not user:
        return None
    bl = _baseline_row(user_id, "heart_rate")
    resting = (round(bl["value"]) if bl and bl["samples"] >= _BASELINE_MIN_SAMPLES
               else user.get("resting_heart_rate"))
    recent = db.connect().execute(
        "SELECT condition, severity, created_at FROM events"
        " WHERE user_id=? AND type='detection'"
        " ORDER BY created_at DESC, rowid DESC LIMIT 5", (user_id,)).fetchall()
    contact = None
    if user.get("emergency_phone"):
        contact = {"name": user.get("emergency_name"),
                   "phone": user["emergency_phone"]}
    return {
        "name": user["display_name"],
        "age": _age_from(user.get("birthdate")),
        "known_conditions": [conditions.LABELS.get(c, c)
                             for c in (user.get("known_conditions") or [])],
        "resting_heart_rate": resting,
        "emergency_contact": contact,
        "recent_detections": [dict(r) for r in recent],
    }


def _card_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def issue_medical_card(user_id: str) -> str:
    """Mint (or rotate) the user's Medical ID card token. Returns the plaintext
    token once; only its hash is stored, and rotating invalidates the old QR."""
    token = "med_" + secrets.token_urlsafe(18)
    conn = db.connect()
    conn.execute(
        "INSERT INTO medical_cards (user_id, token_hash, created_at)"
        " VALUES (?,?,?) ON CONFLICT (user_id) DO UPDATE SET"
        " token_hash=excluded.token_hash, created_at=excluded.created_at",
        (user_id, _card_hash(token), db.utcnow()),
    )
    conn.commit()
    return token


def revoke_medical_card(user_id: str) -> bool:
    conn = db.connect()
    changed = conn.execute("DELETE FROM medical_cards WHERE user_id=?",
                           (user_id,)).rowcount
    conn.commit()
    return changed > 0


def resolve_medical_card(token: str) -> dict | None:
    """Resolve a scanned card token to the Medical ID — no auth token needed
    (the card is the credential). None if the token is unknown/revoked."""
    row = db.connect().execute(
        "SELECT user_id FROM medical_cards WHERE token_hash=?",
        (_card_hash(token),)).fetchone()
    if row is None:
        return None
    return _medical_id(row["user_id"], get_user(row["user_id"]))


def emergency(user_id: str, situation: str | None = None,
              location: str | None = None, sample: dict | None = None,
              qrme=None, pdi=None) -> dict:
    """Emergency mode — one coordinated response mirroring the Emergency
    screen: reach emergency services, share location, contact family, surface
    the Medical ID, and deliver step-by-step AI first-aid guidance, while
    alerting every connected device."""
    user = get_user(user_id)
    known = (user or {}).get("known_conditions") or []
    sensitivity = (user or {}).get("sensitivity") or "balanced"

    # AI guidance: run detection over whatever signal we have, then deliver the
    # matching first-aid guidance. Fall back to general steps when a situation
    # is described but nothing specific is detected — help is never withheld.
    guidance, detection = None, None
    if sample or situation:
        detection = conditions.detect(sample or {}, situation, known=known,
                                      sensitivity=sensitivity)
        if detection is not None:
            guidance = _deliver(user_id, user, detection, situation, qrme,
                                pdi=pdi)
        elif situation:
            guidance = {
                "delivered": True, "source": "local", "content": (
                    "Stay with the person and keep calm. Do not move them "
                    "unless they are in danger. Follow the emergency "
                    "operator's instructions until help arrives."),
                "first_aid": None}

    contact = None
    if user and user.get("emergency_phone"):
        contact = {"name": user.get("emergency_name"),
                   "phone": user["emergency_phone"], "notified": True}
    share = None
    if location:
        share = {"location": location,
                 "shared_with": ([contact["name"] or "emergency contact"]
                                 if contact else []) + ["emergency services"]}
    dispatched = [d["name"] for d in devices_for(user_id)]

    # A deliberate Emergency press is the top of the ladder by definition — the
    # user has declared the emergency — so the decision is resolved at
    # emergency_services with a crisis floor, and its path is returned for audit.
    decision = escalation.decide(
        "critical", sensitivity,
        condition=(detection.condition if detection else None),
        known=known, contactable=contact is not None, crisis=True)

    result = {
        "emergency": True,
        "call_emergency_services": {
            "action": "call emergency services",
            "number": "911",
            "note": "dial your local emergency number if outside the US"},
        "share_location": share,
        "contact_family": contact,
        "medical_id": _medical_id(user_id, user),
        "ai_guidance": guidance,
        "dispatched_alerts": dispatched,
        "robot_directives": _robot_directives(
            user_id,
            cardiac=(detection is not None
                     and detection.condition == conditions.CARDIAC)),
        "escalation_decision": decision,
        # The ordered steps the Emergency screen drives, on the watch or phone.
        "flow": [
            {"step": "armed", "label": "Emergency armed",
             "detail": "press-and-hold confirmed"},
            {"step": "call", "label": "Calling emergency services",
             "detail": "911 (or your local number)"},
            {"step": "notify", "label": "Alerting your emergency contact",
             "detail": (contact["name"] or "emergency contact")
                       if contact else "no contact on file"},
            {"step": "locate", "label": "Sharing your location",
             "detail": location or "location unavailable"},
            {"step": "medical_id", "label": "Surfacing your Medical ID",
             "detail": "shown to responders"},
            {"step": "guide", "label": "First-aid guidance",
             "detail": "step-by-step until help arrives"},
        ],
    }
    _event(user_id, "emergency",
           condition=(detection.condition if detection else None),
           severity="critical",
           detail={"situation": situation, "location_shared": bool(location),
                   "contact_notified": contact is not None,
                   "devices_alerted": dispatched},
           pdi=pdi, vault_scope="medical/emergency")
    return result


def observe_activity(user_id: str, activity: str | None, signals: dict,
                     note: str | None, qrme=None, pdi=None) -> dict:
    """Ambient background observation (the "Jiminy Cricket" jump-in): watch what
    someone is *doing* — editing a video, fixing a car, wrestling with a form —
    and offer help before they ask when a struggle is building.

    Safety first: crisis language in what they say escalates exactly as it does
    from ``monitor``. Otherwise, an ambient struggle raises a *proactive*
    intervention; a calm signal is simply logged (JIM is watching, quietly)."""
    user = get_user(user_id)
    known = (user or {}).get("known_conditions") or []
    _event(user_id, "activity",
           detail={"activity": activity, **signals,
                   **({"note": note} if note else {})},
           pdi=pdi, vault_scope="context/activity")

    # Crisis in the note is handled by the same pipeline as everywhere else.
    crisis = conditions.detect({}, note, known=known) if note else None
    if crisis is not None and crisis.severity == "critical":
        guidance = _deliver(user_id, user, crisis, note, qrme, pdi=pdi)
        escalation = _escalate(user_id, user, crisis)
        return {"activity": activity, "proactive": True, "source": "crisis",
                "condition": crisis.condition, "reason": crisis.reason,
                "intervention": guidance, "escalation": escalation}

    detection = conditions.detect_ambient(signals, note)
    if detection is None:
        return {"activity": activity, "proactive": False, "intervention": None,
                "watching": True}

    _event(user_id, "detection", condition=detection.condition,
           severity=detection.severity,
           detail={"reason": detection.reason, "signals": detection.signals,
                   "proactive": True})
    guidance = _deliver(user_id, user, detection, note, qrme, pdi=pdi)
    life._insight(
        user_id, "suggestion",
        f"I noticed you might be stuck — {detection.reason}. Offered a hand.",
        area="personal_growth", source="ambient")
    return {"activity": activity, "proactive": True, "source": "ambient",
            "condition": detection.condition, "reason": detection.reason,
            "intervention": guidance}


def _user_is_adult(user: dict | None) -> bool:
    bd = (user or {}).get("birthdate")
    if not bd:
        return False                       # unknown age → not a verified adult
    try:
        b = date.fromisoformat(bd)
    except ValueError:
        return False
    today = date.today()
    return today.year - b.year - ((today.month, today.day) < (b.month, b.day)) >= 18


def _tandem_safe(user, profile_id, qrme) -> tuple[bool, str | None]:
    """Whether it is safe to hand this user to a QRME specialist profile. A
    minor (or unknown-age) user must never be connected to an age-restricted
    profile; a non-active profile isn't used. Undeterminable → allowed, because
    QRME's own age-gate is the backstop (JIM passes the user's birthdate)."""
    info = qrme.profile_info(profile_id)
    if info is None:
        return True, None
    if info.get("status") == "departed":
        # The specialist has departed — its QRME memorial remains; JIM points
        # the user there while carrying the guidance itself.
        return (False, "the specialist profile has departed; its memorial "
                       f"remains at /profiles/{profile_id}/memorial — "
                       "used standalone guidance")
    if info.get("status") not in (None, "active"):
        return (False, f"specialist profile is {info.get('status')}; "
                       "used standalone guidance")
    if info.get("adult_mode") and not _user_is_adult(user):
        return (False, "specialist is age-restricted and the user is not a "
                       "verified adult; used standalone guidance")
    return True, None


def _deliver(user_id, user, detection, note, qrme, source_device=None,
             pdi=None) -> dict:
    spec = _specialist(detection.condition)
    wants_tandem = bool(
        spec and spec["mode"] == "tandem" and spec["qrme_profile_id"])

    safety_note = None
    use_tandem = wants_tandem and qrme is not None
    if use_tandem:
        safe, reason = _tandem_safe(user, spec["qrme_profile_id"], qrme)
        if not safe:
            use_tandem, safety_note = False, reason

    delivered = None
    if use_tandem:
        try:
            delivered = _tandem_guidance(user_id, user, detection, note, spec,
                                         qrme, pdi=pdi)
        except RuntimeError:
            # QRME refused (e.g. its own age-gate) — never leave the user
            # without help; fall back to local guidance.
            delivered = None
            safety_note = ("specialist declined the handoff; used standalone "
                           "guidance")
    if delivered is None:
        delivered = local_guidance.generate(
            detection, note, user=user, memory=_memory_summary(user_id))
        if safety_note:
            delivered["note"] = safety_note
        elif wants_tandem and qrme is None:
            delivered["note"] = "tandem specialist registered but no QRME endpoint " \
                                "configured; used standalone guidance"
    # Name the domain expert standing behind this condition (starter
    # registry or operator-registered), for both local and tandem modes.
    if spec and spec.get("label"):
        delivered["specialist"] = spec["label"]
    channel = _delivery_channel(user, source_device)
    delivered["delivered_via"] = channel
    embodiment = device_lookup(user_id, channel) if user else None
    if embodiment:
        # Clause 16: the embodiment's transport (e.g. Bluetooth relay through
        # a linked device) and whether it answers with its own on-device LLM.
        delivered["delivery"] = {
            "kind": embodiment["kind"], "transport": embodiment["transport"],
            "linked_to": embodiment["linked_to"],
            "on_device_llm": embodiment["has_llm"],
        }

    _event(user_id, "guidance", condition=detection.condition,
           severity=detection.severity, detail=delivered)
    return delivered


def _tandem_guidance(user_id, user, detection, note, spec, qrme,
                     pdi=None) -> dict:
    """Delegate guidance to a QRME specialist profile over HTTP."""
    conn = db.connect()
    link = conn.execute(
        "SELECT qrme_interactor_id FROM tandem_links WHERE user_id=?", (user_id,)
    ).fetchone()
    if link is None:
        interactor_id, token = qrme.ensure_interactor(
            user["display_name"], user["birthdate"])
        conn.execute(
            "INSERT INTO tandem_links (user_id, qrme_interactor_id,"
            " qrme_interactor_token, created_at) VALUES (?,?,?,?)",
            (user_id, interactor_id, token, db.utcnow()),
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
    out = {
        "delivered": reply["content"] is not None,
        "source": "tandem",
        "qrme_profile_id": spec["qrme_profile_id"],
        "condition": detection.condition,
        "content": reply["content"],           # None if QRME held it for approval
        "qrme_status": reply["status"],
        "qrme_flag_reason": reply.get("flag_reason"),
    }
    if pdi is not None:
        # Provable custody: the full exchange with the QRME specialist is
        # sealed in the PDI vault under a jim/ key (which PDI's provenance
        # attributes to JIM Guardian), hash-chained in its audit log, and
        # registered locally so user erasure purges it too. A vault outage
        # must never cost the user their guidance — sealing failure is
        # reported, not raised.
        exchange_id = db.new_id("txc")
        key = (f"jim/{user_id}/tandem/{spec['qrme_profile_id']}/{exchange_id}")
        try:
            life.vault_store(pdi, user_id, key, {
                "condition": detection.condition,
                "specialist": spec.get("label"),
                "qrme_profile_id": spec["qrme_profile_id"],
                "qrme_interactor_id": interactor_id,
                "message": message,
                "reply": reply["content"],
                "reply_status": reply["status"],
                "at": db.utcnow(),
            })
            out["custody"] = {"vaulted": True, "pdi_key": key}
        except Exception:
            out["custody"] = {
                "vaulted": False,
                "note": "PDI vault unreachable; exchange not sealed"}
    return out


def _escalate(user_id, user, detection, decision=None) -> dict:
    contact = None
    if user and user.get("contact_consent") and user.get("emergency_phone"):
        contact = {"name": user.get("emergency_name"), "phone": user["emergency_phone"]}
    # Autonomous coordinated response: every connected system the user has
    # registered (wearable, stationary console, autonomous device) receives
    # the alert, so whichever is nearest can surface the guidance.
    dispatched = [d["name"] for d in devices_for(user_id)]
    # Resolve (or reuse) the escalation tier so the response carries an explicit,
    # auditable decision path — not just "escalated: true".
    if decision is None:
        sensitivity = (user or {}).get("sensitivity") or "balanced"
        decision = escalation.decide(
            detection.severity, sensitivity, condition=detection.condition,
            known=(user or {}).get("known_conditions") or [],
            contactable=contact is not None,
            crisis="crisis language" in detection.reason)
    result = {
        "escalated": True, "condition": detection.condition,
        "reason": detection.reason,
        "notified_emergency_contact": contact is not None,
        "emergency_contact": contact, "live_support": True,
        "dispatched_alerts": dispatched,
        # Bound robots respond by role: mobile bodies converge on the user,
        # vacuums dock and clear the floor for people and responders. A
        # cardiac event upgrades first-aid-rated bodies to their rescue role.
        "robot_directives": _robot_directives(
            user_id, cardiac=detection.condition == conditions.CARDIAC),
        "tier": decision["tier"],
        "actions": decision["actions"],
        "rationale": decision["rationale"],
        "decision_path": decision["path"],
    }
    _event(user_id, "escalation", condition=detection.condition,
           severity="critical", detail=result)
    return result


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
