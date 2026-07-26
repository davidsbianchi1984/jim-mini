"""How much to trust a biometric sample.

Everything upstream of this module assumed clean input. ``monitor`` took a
sample dict, handed it to :mod:`jim.conditions`, and whatever came back drove
guidance and escalation. :func:`jim.escalation.decide` has always accepted a
``confidence``, but only forecasts ever supplied one — it gated *predictions*
and never *measurements*. So a reading was a fact by virtue of arriving.

Consumer biometrics are not like that. An optical sensor on a wrist loses
contact, a chest strap picks up a motion artifact, a finger clip reads through
nail polish. The characteristic failure is not a small error — it is a
plausible-looking number that is completely wrong, and the alarming direction
is as likely as the reassuring one.

That matters here more than it would in a fitness tracker, because at the top
of this ladder is a phone call to somebody's daughter. A wearable that reports
SpO2 62% during a workout is common enough that a Guardian which escalates
every one of them teaches the emergency contact to ignore it — and an alert
that is usually wrong is worse than no alert, because it consumes the one thing
escalation actually spends, which is somebody's willingness to pick up.

**The response to an untrusted reading is not silence.** Dropping a sample
would be the same mistake pointed the other way: the noisy reading is
sometimes real. So nothing here discards anything. A sample is *graded*, and a
poor grade caps how far the ladder may climb — it turns *"call your daughter"*
into *"we got an odd reading, are you alright?"*, which is the correct thing to
say when the honest answer is that we do not know.

Three rules keep that from becoming a way to miss a real emergency:

1. **Words are never noise.** A sensor can be wrong; a person typing *"I can't
   breathe"* is data of a different kind. Anything the user said travels
   untouched, and :func:`jim.escalation.decide`'s crisis floor is applied after
   the confidence cap and is never clipped by it.
2. **An alarming reading is not a suspicious one.** Confidence drops only on
   positive evidence that the *sensor* misbehaved — a physiologically
   impossible value, a jump no body could make between two readings, or the
   device reporting its own poor contact. A low SpO2 is not evidence of a bad
   sensor; it is the thing this whole system watches for, and an earlier draft
   that treated "clinically abnormal" as "untrustworthy" muted exactly the
   readings the ladder exists to carry.
3. **Corroboration restores trust — but only between *possible* readings.**
   Two impossible ones are not two witnesses, they are one broken device
   agreeing with itself, and nothing a user says can make a heart rate of zero
   true. Their words still escalate — through the crisis floor, which this
   cannot touch.
4. **A fault is reported as a fault.** A heart rate of 0 or an SpO2 of 130 is
   not a health event and should not be phrased as one — it means *check the
   device*. Saying "are you alright?" to somebody whose strap has fallen off
   is how people learn to disbelieve the thing.
"""

from __future__ import annotations

# (hard_low, hard_high, plausible_low, plausible_high)
#
# Hard bounds are the limits of the living: outside them the sensor is broken,
# not the person. Plausible bounds mark the ordinary range and are reported as
# context only — crossing one is what detection is *for*, so it must never by
# itself reduce confidence, or the module mutes the readings it exists to pass
# through.
RANGES: dict[str, tuple[float, float, float, float]] = {
    "heart_rate":        (10, 300, 35, 200),
    "resting_heart_rate": (25, 150, 40, 100),
    "blood_oxygen":      (50, 100, 90, 100),
    "respiratory_rate":  (3, 70, 8, 25),
    "body_temperature":  (30.0, 45.0, 35.5, 38.0),
    "hrv":               (1, 400, 15, 200),
}

# The most a metric can move between consecutive readings before the *change*
# itself is the suspicious part. Generous on purpose: a genuine panic attack
# moves a heart rate fast, and this must not be the thing that muffles one.
MAX_JUMP: dict[str, float] = {
    "heart_rate": 70,
    "blood_oxygen": 12,
    "respiratory_rate": 14,
    "body_temperature": 2.0,
}

GRADES = ("ok", "suspect", "implausible")

# What each grade is worth. `implausible` is deliberately not zero: a broken
# sensor on somebody who is also unwell is a real scenario, and corroboration
# has to be able to lift it.
_GRADE_CONFIDENCE = {"ok": 1.0, "suspect": 0.45, "implausible": 0.15}

# Below this, escalation is capped (see jim/escalation.py). Above it, a sample
# is treated exactly as samples were treated before this module existed.
TRUST_FLOOR = 0.5

FAULT_NOTE = ("that reading is outside what a body can produce, so it is the "
              "sensor rather than you — check the strap, the fit, or the "
              "battery")
SUSPECT_NOTE = ("that reading is unusual and nothing else in the sample agrees "
                "with it, which is what a loose sensor looks like")


def _grade_metric(name: str, value, prior=None) -> tuple[str, str | None]:
    """``(grade, reason)`` for one metric."""
    rng = RANGES.get(name)
    if rng is None or value is None:
        return "ok", None
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "implausible", f"{name}={value!r} is not a number"

    hard_lo, hard_hi, plaus_lo, plaus_hi = rng
    if v < hard_lo or v > hard_hi:
        return "implausible", (f"{name}={v:g} is outside the range a body can "
                               f"produce ({hard_lo:g}–{hard_hi:g})")

    jump = MAX_JUMP.get(name)
    if prior is not None and jump is not None:
        try:
            delta = abs(v - float(prior))
        except (TypeError, ValueError):
            delta = 0.0
        if delta > jump:
            return "suspect", (f"{name} moved {delta:g} since the last reading, "
                               f"more than {jump:g} — a jump that size is "
                               f"usually the sensor losing contact")

    # Deliberately NOT "outside the ordinary range → suspect". Being clinically
    # abnormal is the *signal*, not noise, and an earlier draft of this module
    # conflated the two — which muted a lone SpO2 of 84, the exact reading the
    # escalation ladder exists for. Confidence drops only on positive evidence
    # of a *sensor* problem: an impossible value, an impossible rate of change,
    # or the device saying so itself. An alarming number is just alarming.
    if v < plaus_lo or v > plaus_hi:
        return "ok", None
    return "ok", None


def assess(sample: dict, prior: dict | None = None,
           said_something: bool = False) -> dict:
    """Grade a sample. Never raises, never drops anything.

    ``prior`` is the previous sample for this user, used only for
    rate-of-change. ``said_something`` is whether the user sent words with the
    reading — words are not a sensor, and a sample that arrives with them is
    corroborated by definition.
    """
    prior = prior or {}
    per_metric: dict[str, dict] = {}
    reasons: list[str] = []
    worst = "ok"
    suspect_count = 0
    any_impossible = False

    for name in RANGES:
        if sample.get(name) is None:
            continue
        grade, why = _grade_metric(name, sample[name], prior.get(name))
        per_metric[name] = {"value": sample[name], "grade": grade,
                            "reason": why}
        if why:
            reasons.append(why)
        if grade == "suspect":
            suspect_count += 1
        elif grade == "implausible":
            any_impossible = True
        if GRADES.index(grade) > GRADES.index(worst):
            worst = grade

    confidence = _GRADE_CONFIDENCE[worst]

    # A device that reports its own signal quality is better evidence about
    # itself than any range check. Folded in multiplicatively so a wearable
    # saying "poor contact" can only ever lower trust, never manufacture it.
    quality = sample.get("signal_quality")
    if quality is not None:
        try:
            q = max(0.0, min(1.0, float(quality)))
            confidence *= q
            if q < 0.6:
                reasons.append(f"the device reported its own signal quality as "
                               f"{q:.2f}")
        except (TypeError, ValueError):
            pass

    # Corroboration. One weird number is a sensor; two independently unusual
    # metrics is a person, and a reading that arrives with the user's own words
    # is not in doubt at all.
    #
    # **Only *possible* readings can corroborate anything.** Two impossible
    # ones are not two witnesses, they are one broken device agreeing with
    # itself — and nothing a person says can make a heart rate of zero true.
    # Their words still escalate; they do it through the crisis path, which
    # this cap deliberately cannot touch.
    corroborated = (not any_impossible
                    and (suspect_count >= 2 or said_something))
    if corroborated and worst != "ok":
        confidence = min(1.0, confidence + 0.45)
        reasons.append("corroborated by " + ("the user's own words"
                                             if said_something else
                                             "more than one signal agreeing"))

    confidence = round(max(0.0, min(1.0, confidence)), 2)
    return {
        "confidence": confidence,
        "grade": worst,
        "trusted": confidence >= TRUST_FLOOR,
        "corroborated": corroborated,
        "metrics": per_metric,
        "reasons": reasons,
        # What to *say*. A fault and a doubt are different sentences: telling
        # somebody whose strap fell off that we are worried about them is how
        # they learn to disbelieve the thing.
        "note": (None if confidence >= TRUST_FLOOR else
                 FAULT_NOTE if worst == "implausible" else SUSPECT_NOTE),
    }


def clean(sample: dict) -> dict:
    """The sample with anything outside the *ordinary* range removed.

    Deliberately stricter than :func:`assess`, which only calls a reading
    impossible outside the hard bounds. A baseline is a long-lived average of
    what normal looks like for this person, so it should absorb only readings
    that were normal — a merely-possible 195bpm is a real event worth detecting
    and a terrible thing to average into "resting".

    Used only for *baseline* updates. A rolling baseline is a long-lived
    number, and letting a sensor fault into it corrupts every future comparison
    — the one place where dropping a reading is clearly right, because a
    baseline has no urgency and can simply wait for the next good sample.
    """
    out = dict(sample)
    for name, (_lo, _hi, lo, hi) in RANGES.items():
        v = out.get(name)
        if v is None:
            continue
        try:
            if not (lo <= float(v) <= hi):
                out.pop(name)
        except (TypeError, ValueError):
            out.pop(name)
    return out
