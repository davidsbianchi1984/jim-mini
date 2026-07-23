"""Predictive early-warning algorithm.

Where :mod:`jim.conditions` answers *"is something wrong right now?"* from a
single sample, this module answers *"is something **about to** go wrong?"* from
a short history of samples — so the Guardian can nudge before a threshold is
crossed rather than after.

It is deliberately **transparent**, not a black box: for each vital it fits a
least-squares trend line over the recent points, projects when that line would
cross the vital's danger threshold, and warns when the projected crossing falls
inside a sensitivity-tuned lead-time window. Every warning carries the trend,
the projected minutes-to-threshold, and a confidence (the fit's R²), so a
clinician — or the user — can audit exactly why it fired.

The sensitivity dial sets how far ahead we look and how clean the trend must be:

    cautious   → look 30 min ahead, accept a noisier trend (warn early/often)
    balanced   → 20 min, moderate fit required
    assertive  → 10 min, only a clean, strong trend (warn late/rarely)
"""

from __future__ import annotations

from dataclasses import dataclass

# Per-vital danger model. ``danger`` is a callable of the resting heart rate
# (only heart_rate uses it) returning the threshold; ``direction`` is which way
# is dangerous. Thresholds mirror jim.conditions' detection boundaries so the
# forecast lines up with the reactive rule it is trying to pre-empt.
SIGNALS: dict[str, dict] = {
    "heart_rate": {"direction": "up", "danger": lambda resting: resting + 40,
                   "condition": "anxiety", "unit": "bpm"},
    "respiratory_rate": {"direction": "up", "danger": lambda _r: 20,
                         "condition": "anxiety", "unit": "/min"},
    "hrv": {"direction": "down", "danger": lambda _r: 20,
            "condition": "stress", "unit": "ms"},
    "blood_oxygen": {"direction": "down", "danger": lambda _r: 90,
                     "condition": "physical_distress", "unit": "%"},
}

# Sensitivity → (lead-time window in minutes, minimum fit quality R²).
_WINDOW = {
    "cautious": (30.0, 0.35),
    "balanced": (20.0, 0.55),
    "assertive": (10.0, 0.75),
}

# Default spacing between samples when we can't infer it from timestamps.
_DEFAULT_STEP_MIN = 5.0


@dataclass
class Forecast:
    signal: str
    condition: str
    risk: float            # 0..1 — sooner projected crossing ⇒ higher
    horizon_min: float     # projected minutes until the danger threshold
    confidence: float      # 0..1 — R² of the trend fit
    trend: list[float]
    reason: str

    def as_dict(self) -> dict:
        return {
            "signal": self.signal,
            "condition": self.condition,
            "risk": round(self.risk, 2),
            "horizon_min": round(self.horizon_min, 1),
            "confidence": round(self.confidence, 2),
            "trend": self.trend,
            "reason": self.reason,
        }


def _linfit(series: list[float]) -> tuple[float, float]:
    """Least-squares slope (per step) and intercept over x = 0..n-1."""
    n = len(series)
    xs = range(n)
    mean_x = (n - 1) / 2
    mean_y = sum(series) / n
    sxx = sum((x - mean_x) ** 2 for x in xs)
    sxy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, series))
    slope = sxy / sxx if sxx else 0.0
    return slope, mean_y - slope * mean_x


def _r2(series: list[float], slope: float, intercept: float) -> float:
    """Coefficient of determination — how well the line explains the points."""
    mean_y = sum(series) / len(series)
    ss_tot = sum((y - mean_y) ** 2 for y in series)
    if ss_tot == 0:
        return 1.0  # a flat series is perfectly explained (by a flat line)
    ss_res = sum((y - (slope * x + intercept)) ** 2
                 for x, y in enumerate(series))
    return max(0.0, 1.0 - ss_res / ss_tot)


def _project(series: list[float], danger: float, direction: str,
             step_min: float) -> tuple[float | None, float, float]:
    """Return (horizon_min_to_danger, slope, r2). ``horizon`` is None when the
    series is not trending toward danger (or already past it)."""
    slope, intercept = _linfit(series)
    r2 = _r2(series, slope, intercept)
    last = series[-1]
    toward = (slope > 0 if direction == "up" else slope < 0)
    if not toward or slope == 0:
        return None, slope, r2
    # Steps from the last point until the fitted line reaches ``danger``.
    steps = (danger - last) / slope
    if steps <= 0:
        return None, slope, r2   # already at/over the threshold — not a forecast
    return steps * step_min, slope, r2


def assess(history: dict[str, list[float]], *, resting: float = 70.0,
           sensitivity: str = "balanced",
           step_min: float = _DEFAULT_STEP_MIN) -> Forecast | None:
    """Assess every tracked vital's recent history and return the most urgent
    forecast (soonest projected crossing that clears the sensitivity gate), or
    ``None`` if nothing is trending toward danger in the lookahead window.

    ``history`` maps a signal name to its recent values, oldest first. A signal
    needs at least three points to establish a trend.
    """
    window, min_r2 = _WINDOW.get(sensitivity, _WINDOW["balanced"])
    best: Forecast | None = None

    for signal, spec in SIGNALS.items():
        series = [float(v) for v in history.get(signal, []) if v is not None]
        if len(series) < 3:
            continue
        danger = float(spec["danger"](resting))
        horizon, slope, r2 = _project(series, danger, spec["direction"], step_min)
        if horizon is None or horizon > window or r2 < min_r2:
            continue
        # Sooner crossing ⇒ higher risk; clamp away from the extremes so a
        # forecast never reads as a certainty.
        risk = max(0.1, min(0.99, 1.0 - horizon / window))
        arrow = "rising" if spec["direction"] == "up" else "falling"
        reason = (
            f"{signal.replace('_', ' ')} {arrow} "
            f"~{abs(slope):.1f} {spec['unit']}/reading "
            f"({' → '.join(f'{v:g}' for v in series[-3:])}) — projected to cross "
            f"{danger:g} {spec['unit']} in ~{horizon:.0f} min"
        )
        fc = Forecast(signal, spec["condition"], risk, horizon, r2,
                      [round(v, 1) for v in series[-4:]], reason)
        if best is None or fc.horizon_min < best.horizon_min:
            best = fc
    return best
