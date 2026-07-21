"""Known-condition detection.

A transparent rule layer over a biometric sample plus optional free text. It
maps signals to a ``condition`` domain key and a ``severity``:

- ``info``     — noticed, no action beyond logging
- ``guidance`` — deliver guidance
- ``critical`` — deliver guidance AND escalate immediately
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

ANXIETY = "anxiety"
DEPRESSION = "depression"
STRESS = "stress"
PHOBIA = "phobia"
FINANCIAL_STRESS = "financial_stress"
RELATIONSHIP = "relationship"
PHYSICAL_DISTRESS = "physical_distress"
PHYSICAL_INJURY = "physical_injury"
CARDIAC = "cardiac_event"
ENVIRONMENT = "environmental_hazard"
ERGONOMIC = "ergonomic_strain"

LABELS = {
    ANXIETY: "acute anxiety / panic",
    DEPRESSION: "low mood / depression",
    STRESS: "stress management",
    PHOBIA: "phobia / acute fear",
    FINANCIAL_STRESS: "financial stress",
    RELATIONSHIP: "relationship distress",
    PHYSICAL_DISTRESS: "physical distress",
    PHYSICAL_INJURY: "physical injury — first aid",
    CARDIAC: "cardiac emergency — CPR / AED",
    ENVIRONMENT: "environmental hazard",
    ERGONOMIC: "ergonomic risk / physical strain",
}

# Declaring one of these known conditions sensitizes the heart-rate rule
# (an episode is detected earlier for a user known to be prone to one).
_HR_SENSITIVE = {ANXIETY, STRESS, PHOBIA}


@dataclass
class Detection:
    condition: str
    severity: str            # info | guidance | critical
    reason: str
    signals: dict = field(default_factory=dict)


_TEXT_CUES: list[tuple[str, list[str]]] = [
    (ANXIETY, ["panic", "panic attack", "anxious", "anxiety", "can't breathe",
               "racing thoughts", "overwhelmed"]),
    (DEPRESSION, ["hopeless", "worthless", "empty", "no point", "can't get out of bed"]),
    (STRESS, ["burned out", "burnout", "overworked", "too much pressure",
              "deadline", "stressed"]),
    (PHOBIA, ["phobia", "terrified of", "afraid of flying", "afraid of heights"]),
    (FINANCIAL_STRESS, ["broke", "debt", "bankrupt", "can't pay", "financial crisis",
                        "lost my job", "rent", "eviction"]),
    (RELATIONSHIP, ["breakup", "broke up", "divorce", "fight with", "lonely",
                    "my partner", "my ex"]),
    (PHYSICAL_INJURY, ["i fell", "bleeding", "sprained", "burned my", "cut myself",
                       "twisted my ankle", "hit my head"]),
]

_CRISIS = re.compile(
    r"\b(kill myself|end it all|suicide|hurt myself|don't want to live)\b", re.I
)


# How the sensitivity dial shifts the heart-rate thresholds (bpm over resting):
# cautious escalates earlier (lower bar), assertive requires stronger signals.
_SENSITIVITY_DELTA = {"cautious": -10, "balanced": 0, "assertive": 10}


def detect(sample: dict, text: str | None = None,
           known: list[str] | None = None,
           sensitivity: str = "balanced") -> Detection | None:
    """Return the highest-severity detection for a sample, or None.

    ``known`` is the user's declared known conditions; declaring an
    HR-sensitive condition lowers the heart-rate threshold so episodes are
    caught earlier for users known to be prone to them. ``sensitivity``
    (cautious/balanced/assertive) shifts the heart-rate guidance/critical
    boundaries for the whole user.
    """
    note = (text or sample.get("note") or "").strip()
    known = known or []
    delta = _SENSITIVITY_DELTA.get(sensitivity, 0)

    if note and _CRISIS.search(note):
        return Detection(ANXIETY, "critical",
                         "crisis language detected — immediate escalation",
                         {"text": note})

    # Cardiac patterns outrank the generic collapse rule: fibrillation calls
    # for an AED, a collapse with an absent/minimal pulse calls for CPR.
    rhythm = (sample.get("rhythm") or "").lower()
    if rhythm in ("fibrillation", "vfib", "v-fib"):
        return Detection(CARDIAC, "critical",
                         "cardiac fibrillation pattern detected",
                         {"rhythm": rhythm, "pattern": "fibrillation"})

    movement = (sample.get("movement") or "").lower()
    pulse = (sample.get("pulse") or "").lower()
    hr_now = sample.get("heart_rate")
    if movement in ("fall", "collapse") and (
            pulse == "absent" or (hr_now is not None and hr_now < 30)):
        return Detection(CARDIAC, "critical",
                         f"sudden {movement} with absent/minimal pulse — "
                         "suspected cardiac arrest",
                         {"movement": movement, "pulse": pulse or hr_now,
                          "pattern": "arrest"})

    if movement in ("fall", "collapse"):
        return Detection(PHYSICAL_INJURY, "critical",
                         f"sudden {movement} detected by movement sensors",
                         {"movement": movement})
    if movement == "immobile":
        return Detection(PHYSICAL_INJURY, "guidance",
                         "prolonged immobility detected",
                         {"movement": movement})

    speech = (sample.get("speech") or "").lower()
    if speech in ("slurred", "incoherent"):
        return Detection(PHYSICAL_DISTRESS, "critical",
                         f"{speech} speech detected — possible medical emergency",
                         {"speech": speech})

    temp = sample.get("body_temperature")
    if temp is not None and (temp >= 38.5 or temp < 35):
        severity = "critical" if (temp >= 40 or temp < 35) else "guidance"
        kind = "high fever" if temp >= 38.5 else "abnormally low body temperature"
        return Detection(PHYSICAL_DISTRESS, severity,
                         f"{kind} ({temp}°C)", {"body_temperature": temp})

    systolic = sample.get("bp_systolic")
    diastolic = sample.get("bp_diastolic")
    if systolic is not None and (systolic >= 160 or (diastolic or 0) >= 100):
        severity = ("critical"
                    if systolic >= 180 or (diastolic or 0) >= 120 else "guidance")
        return Detection(PHYSICAL_DISTRESS, severity,
                         f"elevated blood pressure ({systolic}/{diastolic or '?'} mmHg)",
                         {"bp_systolic": systolic, "bp_diastolic": diastolic})

    hrv = sample.get("hrv")
    if hrv is not None and hrv < 20:
        return Detection(STRESS, "guidance",
                         f"low heart-rate variability ({hrv} ms) — sustained stress load",
                         {"hrv": hrv})

    spo2 = sample.get("blood_oxygen")
    if spo2 is not None and spo2 < 90:
        return Detection(PHYSICAL_DISTRESS,
                         "critical" if spo2 < 88 else "guidance",
                         f"low blood oxygen (SpO2 {spo2}%)",
                         {"blood_oxygen": spo2})

    # Environmental hazards monitored by connected sensors: smoke or carbon
    # monoxide is a leave-now emergency; merely poor air earns guidance.
    air = (sample.get("air_quality") or "").lower()
    co = sample.get("co_level")
    if air in ("smoke", "co", "carbon_monoxide") or (co is not None and co >= 9):
        return Detection(ENVIRONMENT, "critical",
                         "hazardous air detected"
                         + (f" ({air})" if air else f" (CO {co} ppm)"),
                         {"air_quality": air or None, "co_level": co})
    if air == "poor":
        return Detection(ENVIRONMENT, "guidance",
                         "poor air quality in the environment",
                         {"air_quality": air})

    hr = sample.get("heart_rate")
    resting = sample.get("resting_heart_rate", 70)
    rr = sample.get("respiratory_rate")
    threshold = (30 if _HR_SENSITIVE.intersection(known) else 40) + delta
    critical_over = 70 + delta
    if hr is not None and hr >= resting + threshold and (rr is None or rr >= 20):
        severity = "critical" if hr >= resting + critical_over else "guidance"
        return Detection(ANXIETY, severity,
                         f"heart rate {hr} bpm ({hr - resting} over resting"
                         + (", sensitized for a declared condition" if threshold == 30 else "")
                         + ")"
                         + (f", respiratory rate {rr}/min" if rr else ""),
                         {"heart_rate": hr, "resting_heart_rate": resting,
                          "respiratory_rate": rr})

    # Ergonomic risk factors: sustained bad posture or repetitive motion —
    # a strain injury forming, worth a nudge before it becomes one.
    posture = (sample.get("posture") or "").lower()
    repetitive = sample.get("repetitive_motion_min")
    if posture in ("slouched", "hunched", "awkward") or (
            repetitive is not None and repetitive >= 45):
        return Detection(ERGONOMIC, "guidance",
                         "ergonomic risk factors detected"
                         + (f": {posture} posture" if posture else "")
                         + (f", {repetitive} min of repetitive motion"
                            if repetitive else ""),
                         {"posture": posture or None,
                          "repetitive_motion_min": repetitive})

    if note:
        for condition, cues in _TEXT_CUES:
            for cue in cues:
                if re.search(rf"\b{re.escape(cue)}\b", note, re.I):
                    return Detection(condition, "guidance",
                                     f"reported concern matching '{cue}'",
                                     {"text": note})

    return None


FRUSTRATION = "frustration"
LABELS[FRUSTRATION] = "task frustration / struggle"

# Words that signal frustration in what someone says (or types) while doing a
# task — the "ugh, why won't this work" of a struggle building.
_FRUSTRATION_CUES = [
    "ugh", "argh", "why won't", "why isn't", "come on", "stuck", "frustrat",
    "hate this", "give up", "giving up", "can't figure", "not working",
    "won't work", "doesn't work", "makes no sense", "seriously", "fed up",
]


def detect_ambient(signals: dict, text: str | None = None) -> Detection | None:
    """Ambient struggle detection (the "Jiminy Cricket" jump-in): from the
    signals of an *activity* — repeated attempts, a long stall, frustration in
    what the person says — decide whether help should be offered *before it is
    asked for*. Transparent and additive, like the biometric rules.

    This never escalates on its own (crisis language is handled by ``detect``);
    it only offers proactive guidance. Returns None when nothing rises to the
    level of an intervention.
    """
    activity = signals.get("activity")
    try:
        retries = int(signals.get("retries") or signals.get("errors") or 0)
    except (TypeError, ValueError):
        retries = 0
    try:
        idle = float(signals.get("idle_seconds") or 0)
    except (TypeError, ValueError):
        idle = 0.0
    try:
        duration = float(signals.get("duration_min") or 0)
    except (TypeError, ValueError):
        duration = 0.0
    note = (text or "").lower()

    score, reasons = 0, []
    if retries >= 5:
        score += 2
        reasons.append(f"{retries} repeated attempts")
    elif retries >= 3:
        score += 1
        reasons.append(f"{retries} repeated attempts")
    if any(cue in note for cue in _FRUSTRATION_CUES):
        score += 2
        reasons.append("frustration in what they said")
    if idle >= 120:
        score += 1
        reasons.append("a long pause mid-task")
    if duration >= 45 and retries >= 3:
        score += 1
        reasons.append("a long stretch without progress")

    if score < 2:
        return None
    where = f"while {activity}" if activity else "during this task"
    return Detection(
        FRUSTRATION, "guidance",
        f"struggle detected {where}: " + ", ".join(reasons),
        {"activity": activity, "retries": retries, "idle_seconds": idle,
         "duration_min": duration, "score": score},
    )


def forecast(current_hr: int | None, resting: int,
             prior_hrs: list[int]) -> Detection | None:
    """Predictive early warning (before a condition manifests): a steady
    heart-rate climb that hasn't crossed the detection threshold yet."""
    if current_hr is None or len(prior_hrs) < 2:
        return None
    recent = prior_hrs[-2:] + [current_hr]
    rising = all(b > a for a, b in zip(recent, recent[1:]))
    if rising and current_hr >= resting + 25 and recent[-1] - recent[0] >= 15:
        return Detection(ANXIETY, "info",
                         f"rising heart-rate trend ({' → '.join(map(str, recent))} bpm) "
                         "— a stress or anxiety episode may be building",
                         {"trend": recent, "resting_heart_rate": resting})
    return None
