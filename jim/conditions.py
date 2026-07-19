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

LABELS = {
    ANXIETY: "acute anxiety / panic",
    DEPRESSION: "low mood / depression",
    STRESS: "stress management",
    PHOBIA: "phobia / acute fear",
    FINANCIAL_STRESS: "financial stress",
    RELATIONSHIP: "relationship distress",
    PHYSICAL_DISTRESS: "physical distress",
    PHYSICAL_INJURY: "physical injury — first aid",
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


def detect(sample: dict, text: str | None = None,
           known: list[str] | None = None) -> Detection | None:
    """Return the highest-severity detection for a sample, or None.

    ``known`` is the user's declared known conditions; declaring an
    HR-sensitive condition lowers the heart-rate threshold so episodes are
    caught earlier for users known to be prone to them.
    """
    note = (text or sample.get("note") or "").strip()
    known = known or []

    if note and _CRISIS.search(note):
        return Detection(ANXIETY, "critical",
                         "crisis language detected — immediate escalation",
                         {"text": note})

    movement = (sample.get("movement") or "").lower()
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

    hr = sample.get("heart_rate")
    resting = sample.get("resting_heart_rate", 70)
    rr = sample.get("respiratory_rate")
    threshold = 30 if _HR_SENSITIVE.intersection(known) else 40
    if hr is not None and hr >= resting + threshold and (rr is None or rr >= 20):
        severity = "critical" if hr >= resting + 70 else "guidance"
        return Detection(ANXIETY, severity,
                         f"heart rate {hr} bpm ({hr - resting} over resting"
                         + (", sensitized for a declared condition" if threshold == 30 else "")
                         + ")"
                         + (f", respiratory rate {rr}/min" if rr else ""),
                         {"heart_rate": hr, "resting_heart_rate": resting,
                          "respiratory_rate": rr})

    if note:
        for condition, cues in _TEXT_CUES:
            for cue in cues:
                if re.search(rf"\b{re.escape(cue)}\b", note, re.I):
                    return Detection(condition, "guidance",
                                     f"reported concern matching '{cue}'",
                                     {"text": note})

    return None


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
