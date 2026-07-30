"""Escalation decision tree.

Detection and forecasting decide *what* is happening; this module decides *what
to do about it* — and does so as an explicit, auditable ladder rather than a
tangle of ``if`` statements scattered through the Guardian.

The ladder, lowest to highest:

    0  log                 record the event, nothing more
    1  self_guidance       deliver AI guidance to the user
    2  check_in            proactively ask if they're OK
    3  notify_contact      alert the registered emergency contact
    4  emergency_services  call emergency services + full coordinated response

:func:`decide` maps a situation to a tier. It starts from the detection
severity, shifts by the user's sensitivity, and applies a handful of explicit
modifiers (declared condition, forecast confidence, crisis language, whether a
contact is even reachable). Every step is appended to ``path`` so the resulting
decision can be replayed and defended.

**Safety floors that no dial can lower:** crisis language always lands at
``emergency_services``; a ``critical`` detection never falls below
``notify_contact``, whatever the sensitivity.

**And one ceiling.** Every other rule here is a floor. ``ceiling`` is the
exception, and it exists for a caller who is not the user: a stranger who
scanned a care beacon (:mod:`jim.beacons`) raises an alarm capped at
``notify_contact``, because a passer-by's tap must never dispatch an ambulance
on somebody else's behalf — a false dispatch is a real one not going somewhere
else.

When a ceiling clips a floor the result says so out loud (``clipped_by_ceiling``
and ``call_emergency_services_yourself``) rather than quietly returning a lower
tier. The intent behind the floor is not discarded; it is handed to the person
standing there, who can dial faster than any escalation could anyway.
"""

from __future__ import annotations

TIERS = ["log", "self_guidance", "check_in", "notify_contact",
         "emergency_services"]

# Concrete actions each tier performs, cumulative with everything below it.
_ACTIONS = {
    "log": ["record the event"],
    "self_guidance": ["deliver AI guidance"],
    "check_in": ["proactive check-in: ask if they're OK"],
    "notify_contact": ["alert the emergency contact"],
    "emergency_services": ["call emergency services", "share location",
                           "surface Medical ID", "alert connected devices"],
}

# Where a severity starts before any adjustment.
_SEVERITY_BASE = {"info": 1, "guidance": 1, "critical": 4}

# Sensitivity shifts the whole ladder: cautious escalates one rung earlier,
# assertive one rung later.
_SENSITIVITY_SHIFT = {"cautious": +1, "balanced": 0, "assertive": -1}


def _clamp(i: int) -> int:
    return max(0, min(len(TIERS) - 1, i))


def decide(severity: str, sensitivity: str = "balanced", *,
           condition: str | None = None, known: list[str] | None = None,
           confidence: float = 1.0, contactable: bool = False,
           crisis: bool = False, ceiling: str | None = None,
           guidance_ineffective: bool = False) -> dict:
    """Resolve a situation to an escalation tier + concrete actions.

    Parameters
    ----------
    severity      "info" | "guidance" | "critical" (from detection/forecast).
    sensitivity   "cautious" | "balanced" | "assertive".
    condition     the domain key, e.g. "anxiety" (for the declared-condition bump).
    known         the user's declared known conditions.
    confidence    0..1 — for a forecast, how sure we are (gates predictive bumps).
    contactable   whether a reachable emergency contact exists.
    crisis        crisis / self-harm language present (hard safety floor).
    ceiling       a tier this decision may not exceed, for a caller who is not
                  the user (an anonymous beacon alarm). Applied after the
                  floors, and recorded when it clips one.
    guidance_ineffective
                  the user has told us the guidance we already delivered did
                  not help (jim/followup.py). Spec [0039]: unhelped counseling
                  escalates toward a live person rather than repeating itself.
    """
    known = known or []
    path: list[str] = []

    idx = _SEVERITY_BASE.get(severity, 0)
    path.append(f"severity '{severity}' → base tier {TIERS[idx]}")

    shift = _SENSITIVITY_SHIFT.get(sensitivity, 0)
    if shift:
        idx = _clamp(idx + shift)
        path.append(f"sensitivity '{sensitivity}' shifts {shift:+d} → {TIERS[idx]}")

    # A guidance-level event for a condition the user has *declared* is more
    # meaningful than a stranger's — bump it toward a personal check-in.
    if severity == "guidance" and condition in known:
        idx = _clamp(idx + 1)
        path.append(f"declared condition '{condition}' bumps +1 → {TIERS[idx]}")

    # A low-confidence forecast should not, by itself, drive an intrusive
    # escalation — cap predictive (info) warnings at self_guidance when unsure.
    if severity == "info" and confidence < 0.5:
        idx = min(idx, 1)
        path.append(f"low forecast confidence {confidence:.2f} caps at self_guidance")

    # …and neither should a reading we do not believe. This gate used to cover
    # predictions only, so a *measurement* was a fact by virtue of arriving: a
    # wearable reporting SpO2 62% through a motion artifact went straight to
    # the critical floor below and rang somebody's daughter. See jim/signal.py.
    #
    # It caps at check_in rather than silencing. "We got an odd reading, are
    # you alright?" is the honest sentence when the honest answer is that we do
    # not know, and asking is also how the reading gets corroborated. The
    # crisis floor below is applied after this and is deliberately not
    # conditioned on it — what somebody *says* is never a sensor artifact.
    unbelieved = severity in ("guidance", "critical") and confidence < 0.5
    if unbelieved:
        idx = min(idx, 2)
        path.append(f"low signal confidence {confidence:.2f} caps at check_in — "
                    f"ask rather than escalate on a reading we do not trust")

    # Guidance we already gave, that the person tells us did not help. Spec
    # [0039]: the answer is a live human, not the same advice louder. One rung
    # up from wherever this event landed, floored at check_in — so an unhelped
    # guidance-level event reaches out, and an unhelped critical one (already
    # at notify_contact) goes all the way to emergency services.
    #
    # Deliberately a rung and not a jump to the top: "the breathing exercise
    # didn't settle me" is a real signal and must be answered by a person, but
    # it is not a reason to dispatch an ambulance on its own.
    if guidance_ineffective:
        idx = _clamp(max(idx + 1, 2))
        path.append("the user says the guidance did not help: +1 rung, floor "
                    f"at check_in → {TIERS[idx]} (a live person, not the same "
                    "advice again)")

    # Safety floors — applied last so nothing above can undercut them.
    if severity == "critical" and not unbelieved:
        idx = max(idx, 3)
        path.append("critical floor: never below notify_contact")
    if crisis:
        idx = len(TIERS) - 1
        path.append("crisis language: hard floor at emergency_services — "
                    "what somebody says is never a sensor artifact")

    # The ceiling — last, so it binds even the floors above. It is the only
    # rule in this module that lowers a tier, and it only ever applies to a
    # caller who is not the user.
    clipped = False
    if ceiling is not None:
        cap = TIERS.index(ceiling)
        if idx > cap:
            clipped = True
            path.append(
                f"ceiling '{ceiling}': an anonymous caller cannot raise this "
                f"above {ceiling} — tell them to call emergency services")
            idx = cap

    tier = TIERS[idx]

    # Assemble cumulative actions, then reconcile with reality: if the ladder
    # wants to notify a contact but none is reachable, keep the intent visible
    # but mark it unmet (and, when critical, emergency services still go).
    actions: list[str] = []
    for t in TIERS[: idx + 1]:
        actions.extend(_ACTIONS[t])
    notify = idx >= TIERS.index("notify_contact")
    call_services = idx >= TIERS.index("emergency_services")
    if notify and not contactable:
        path.append("no reachable emergency contact — notify recorded as unmet")

    return {
        "tier": tier,
        "tier_index": idx,
        "actions": actions,
        "notify_contact": notify and contactable,
        "notify_contact_intended": notify,
        "call_emergency_services": call_services,
        "clipped_by_ceiling": clipped,
        # When the ceiling clipped a floor, the need did not go away — it moved
        # to the person standing there, who is faster than any escalation.
        "call_emergency_services_yourself": clipped,
        "sensitivity": sensitivity,
        "severity": severity,
        "rationale": path[-1],
        "path": path,
    }


def policy(sensitivity: str = "balanced") -> dict:
    """The tier a given severity resolves to under a sensitivity, for the
    transparency endpoint — so a user can see exactly how their dial behaves
    before anything happens."""
    return {
        "sensitivity": sensitivity,
        "ladder": TIERS,
        "by_severity": {
            sev: decide(sev, sensitivity, contactable=True)["tier"]
            for sev in ("info", "guidance", "critical")
        },
        "safety_floors": {
            "crisis_language": "emergency_services",
            "critical_detection": "notify_contact (minimum)",
        },
        "ceilings": {
            "anonymous_beacon_alarm": (
                "notify_contact (maximum) — a stranger who scanned a care "
                "beacon can raise the people watching, never an ambulance"),
        },
    }
