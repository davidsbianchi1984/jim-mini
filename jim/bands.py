"""Personal drift bands — *your* normal, and how far from it counts.

Detection (:mod:`jim.conditions`) answers *is this an episode?* against rules
that hold for anybody: a heart rate 30-40 over resting with a fast
respiration, an oxygen saturation under 92. That is the alarm layer, and it
is deliberately conservative, because the top of its ladder is a phone call
to somebody's daughter.

This module is the other question, and the one a person actually asks of a
wearable they sleep in: **am I drifting from my own normal, in either
direction?** A resting heart rate that has climbed six beats over a fortnight
crosses no clinical threshold and is exactly the sort of thing worth
noticing. So is an HRV that has fallen. So is a respiration that has crept
up while the person felt fine.

Three commitments make that a check-in rather than a second alarm system:

* **Both directions, always.** A band has a low edge and a high edge, and
  which one matters is not knowable in advance: for heart rate the climb is
  usually the story, for HRV and oxygen it is the fall, and for temperature
  both. A one-sided band would silently decide that half of a person's
  physiology cannot go wrong.
* **It never escalates.** Crossing a band produces `severity="checkin"`,
  which the Guardian turns into a question. Nothing here rings a phone;
  :mod:`jim.conditions` and :mod:`jim.escalation` remain the only paths to
  an emergency contact, unchanged. A drift notice that could call somebody
  would just be a jumpier alarm with a softer name.
* **It waits for a real baseline.** A band around a number learned from two
  samples is noise with a threshold drawn on it. Until the baseline is
  established (``guardian`` calls it provisional), no drift is reported at
  all — which is also why a new watch's first days are quiet by design.

The bands are the user's to set. Defaults come from the ordinary
within-person variation of each metric — not from population ranges, which
are a different thing entirely — and every one of them is adjustable per
metric, in the unit the metric is measured in, from the app.
"""

from __future__ import annotations

from . import db

# Default half-width of each band, in the metric's own units, and whether a
# direction is worth reporting at all. These are *within-person* margins: how
# far this person's resting value ordinarily wanders before the wandering is
# the news. Deliberately generous — a band that fires on ordinary daily
# variation teaches the person to ignore the one that matters.
# `slider` is (min, max, step) for the console's range control, stated here
# because only the metric knows its own scale. The console used to hardcode
# 0.1–30 with one branch for °C, which was fine while every unit was
# physiological and would have handed a currency or an hour count a
# nonsense range the day one arrived.
DEFAULTS: dict[str, dict] = {
    "heart_rate": {
        "margin": 8.0, "unit": "bpm", "label": "Resting heart rate",
        "slider": (1.0, 30.0, 0.5),
        "watch_high": True, "watch_low": True,
        "high_note": "your resting heart rate has been running above your usual",
        "low_note": "your resting heart rate has dropped below your usual",
    },
    "resting_heart_rate": {
        "margin": 6.0, "unit": "bpm", "label": "Resting heart rate (device)",
        "slider": (1.0, 30.0, 0.5),
        "watch_high": True, "watch_low": True,
        "high_note": "your resting heart rate has been running above your usual",
        "low_note": "your resting heart rate has dropped below your usual",
    },
    "hrv": {
        "margin": 15.0, "unit": "ms", "label": "Heart-rate variability",
        "slider": (2.0, 60.0, 1.0),
        "watch_high": False, "watch_low": True,
        "high_note": "your HRV is unusually high for you",
        "low_note": "your HRV has fallen below your usual — often the first "
                    "sign of strain, poor sleep or a bug coming on",
    },
    "blood_oxygen": {
        "margin": 2.0, "unit": "%", "label": "Blood oxygen",
        "slider": (0.5, 10.0, 0.5),
        "watch_high": False, "watch_low": True,
        "high_note": "your oxygen saturation is above your usual",
        "low_note": "your oxygen saturation has been below your usual",
    },
    "respiratory_rate": {
        "margin": 3.0, "unit": "breaths/min", "label": "Respiration",
        "slider": (0.5, 10.0, 0.5),
        "watch_high": True, "watch_low": True,
        "high_note": "you have been breathing faster than your usual",
        "low_note": "your breathing rate is below your usual",
    },
    "body_temperature": {
        "margin": 0.4, "unit": "°C", "label": "Body temperature",
        "slider": (0.1, 2.0, 0.1),
        "watch_high": True, "watch_low": True,
        "high_note": "you are running warmer than your usual",
        "low_note": "you are running cooler than your usual",
    },
}

METRICS = tuple(DEFAULTS)

# How the sensitivity dial widens or narrows every band. Same dial that
# shifts the alarm thresholds (jim/conditions.py), so a person who wants a
# quieter Guardian gets one consistently rather than in one layer only.
SENSITIVITY_SCALE = {"cautious": 0.75, "balanced": 1.0, "assertive": 1.4}


def _row(user_id: str, metric: str) -> dict | None:
    r = db.connect().execute(
        "SELECT * FROM drift_bands WHERE user_id=? AND metric=?",
        (user_id, metric)).fetchone()
    return dict(r) if r else None


def band_for(user_id: str, metric: str, sensitivity: str = "balanced") -> dict:
    """The band this user actually has for ``metric`` — their setting when
    they have one, the default scaled by their sensitivity otherwise."""
    spec = DEFAULTS.get(metric)
    if spec is None:
        raise ValueError(f"unknown metric {metric!r}")
    lo, hi, step = spec["slider"]
    slider = {"slider_min": lo, "slider_max": hi, "slider_step": step}
    row = _row(user_id, metric)
    if row:
        return {"metric": metric, "label": spec["label"], "unit": spec["unit"],
                "margin": round(row["margin"], 2),
                "watch_high": bool(row["watch_high"]),
                "watch_low": bool(row["watch_low"]),
                "source": "user", **slider}
    scale = SENSITIVITY_SCALE.get(sensitivity, 1.0)
    # A narrower band is a *more* sensitive one: assertive should notice
    # sooner, so it divides rather than multiplies.
    return {"metric": metric, "label": spec["label"], "unit": spec["unit"],
            "margin": round(spec["margin"] / scale, 2),
            "watch_high": spec["watch_high"], "watch_low": spec["watch_low"],
            "source": "default", **slider}


def set_band(user_id: str, metric: str, margin: float | None = None,
             watch_high: bool | None = None,
             watch_low: bool | None = None) -> dict:
    """Adjust one band. Omitted fields keep whatever is in force."""
    if metric not in DEFAULTS:
        raise ValueError(f"metric must be one of {', '.join(METRICS)}")
    current = band_for(user_id, metric)
    margin = current["margin"] if margin is None else float(margin)
    if margin <= 0:
        raise ValueError("a band must have a width above zero")
    watch_high = current["watch_high"] if watch_high is None else bool(watch_high)
    watch_low = current["watch_low"] if watch_low is None else bool(watch_low)
    conn = db.connect()
    conn.execute(
        "INSERT INTO drift_bands (user_id, metric, margin, watch_high,"
        " watch_low, updated_at) VALUES (?,?,?,?,?,?)"
        " ON CONFLICT(user_id, metric) DO UPDATE SET margin=excluded.margin,"
        " watch_high=excluded.watch_high, watch_low=excluded.watch_low,"
        " updated_at=excluded.updated_at",
        (user_id, metric, margin, int(watch_high), int(watch_low), db.utcnow()),
    )
    conn.commit()
    return band_for(user_id, metric)


def reset_band(user_id: str, metric: str) -> dict:
    """Back to the default for this metric."""
    conn = db.connect()
    conn.execute("DELETE FROM drift_bands WHERE user_id=? AND metric=?",
                 (user_id, metric))
    conn.commit()
    return band_for(user_id, metric)


def overview(user_id: str, sensitivity: str = "balanced") -> list[dict]:
    """Every metric: the band, the learned baseline, and the two edges — so
    a screen can show *your normal, and where the edges sit* rather than a
    number with no context."""
    from . import guardian

    learned = {b["metric"]: b for b in guardian.baseline_for(user_id)}
    out = []
    for metric in METRICS:
        band = band_for(user_id, metric, sensitivity)
        base = learned.get(metric)
        band["baseline"] = base["value"] if base else None
        band["samples"] = base["samples"] if base else 0
        band["provisional"] = base["provisional"] if base else True
        if base and not base["provisional"]:
            band["low_edge"] = round(base["value"] - band["margin"], 2)
            band["high_edge"] = round(base["value"] + band["margin"], 2)
        else:
            band["low_edge"] = band["high_edge"] = None
        out.append(band)
    return out


def check(user_id: str, sample: dict, sensitivity: str = "balanced") -> list[dict]:
    """Which metrics in this sample sit outside the person's own band.

    Returns one entry per crossing, each carrying the value, the baseline it
    is being compared against, the edge it crossed and by how much. Nothing
    here is an alarm: the caller turns these into a check-in question.
    """
    from . import guardian

    learned = {b["metric"]: b for b in guardian.baseline_for(user_id)}
    drifts: list[dict] = []
    for metric, spec in DEFAULTS.items():
        value = sample.get(metric)
        if value is None:
            continue
        try:
            value = float(value)
        except (TypeError, ValueError):
            continue
        base = learned.get(metric)
        # A band around a provisional baseline is a threshold drawn on noise.
        if base is None or base["provisional"]:
            continue
        band = band_for(user_id, metric, sensitivity)
        low, high = base["value"] - band["margin"], base["value"] + band["margin"]
        if band["watch_high"] and value > high:
            drifts.append({
                "metric": metric, "label": spec["label"], "unit": spec["unit"],
                "direction": "above", "value": round(value, 2),
                "baseline": round(base["value"], 2),
                "edge": round(high, 2),
                "delta": round(value - base["value"], 2),
                "note": spec["high_note"],
            })
        elif band["watch_low"] and value < low:
            drifts.append({
                "metric": metric, "label": spec["label"], "unit": spec["unit"],
                "direction": "below", "value": round(value, 2),
                "baseline": round(base["value"], 2),
                "edge": round(low, 2),
                "delta": round(value - base["value"], 2),
                "note": spec["low_note"],
            })
    return drifts


def question(drifts: list[dict]) -> str:
    """The check-in a drift earns: what was noticed, in the person's own
    numbers, and a question rather than a verdict. It is not a diagnosis and
    must not read as one — drifting from your own normal has a hundred
    ordinary causes, and the useful move is to ask."""
    if not drifts:
        return ""
    parts = []
    for d in drifts[:3]:
        parts.append(
            f"{d['note']} ({d['value']}{d['unit']} against your usual "
            f"{d['baseline']}{d['unit']})")
    body = "; ".join(parts)
    return (f"Checking in — {body}. Nothing here is an alarm and it may be "
            "sleep, a hard week, a cold coming on, or nothing at all. How "
            "have you been feeling?")
