"""The Apple Watch bridge — readings reach JIM without an iOS app.

HealthKit only talks to apps installed from the App Store, and JIM does not
have one. What every iPhone *does* have, for free, is two doors out:

* **The drip.** The Shortcuts app can read Health samples and POST them to a
  URL on a personal automation — every hour, on waking, on charge. That is a
  live feed in everything but name. :func:`drip` is the receiving end: a
  per-user token in the URL (a Shortcut is far easier to build without
  custom headers), a forgiving payload shape, and the full Guardian
  pipeline behind it — detection, drift bands, escalation — exactly as if
  the numbers had been typed on the Monitor screen.

* **The seed.** The Health app exports everything it has ever recorded
  (profile picture → *Export All Health Data* → ``export.zip``). Weeks of
  resting heart rate, HRV, oxygen, respiration and temperature are sitting
  in that file — which is to say: **the baseline already happened**. A
  tester should not wear a watch for five quiet days to teach JIM their
  normal when their phone is carrying months of it. :func:`seed` folds the
  export into the baselines and touches nothing else — no events, no
  detection, no check-ins — because history is context, not news. Nobody
  should be woken at enrollment over a heart rate from March.

The two doors are one channel. The drip keeps current what the seed
established.

Payload tolerance is a design position, not sloppiness: the person typing
the Shortcut dictionary is a tester on their lunch break, and the number
arrives as ``72``, ``"72"``, or ``"72 count/min"`` depending on which
Shortcuts block they reached for. All three are the same reading and all
three are accepted. Oxygen is the sharpest case — HealthKit hands
Shortcuts a *fraction* (``0.97``), a person types a percentage (``97``) —
so anything at or below 1 is read as the fraction it is.
"""

from __future__ import annotations

import io
import re
import secrets
import statistics
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict

from . import db


class WatchError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


# ---------------------------------------------------------------------------
# The channel: one drip address per user

def channel(user_id: str) -> dict:
    """The user's drip channel, minted on first ask and stable thereafter."""
    conn = db.connect()
    row = conn.execute("SELECT * FROM watch_channels WHERE user_id=?",
                       (user_id,)).fetchone()
    if row is None:
        token = secrets.token_urlsafe(24)
        conn.execute(
            "INSERT INTO watch_channels (user_id, token, created_at)"
            " VALUES (?,?,?)", (user_id, token, db.utcnow()))
        conn.commit()
        row = conn.execute("SELECT * FROM watch_channels WHERE user_id=?",
                           (user_id,)).fetchone()
    return {"user_id": row["user_id"], "token": row["token"],
            "created_at": row["created_at"], "rotated_at": row["rotated_at"],
            "last_drip_at": row["last_drip_at"], "drips": row["drips"]}


def rotate(user_id: str) -> dict:
    """A new token; the old URL stops working immediately. The recovery from
    a leaked screenshot of the setup screen."""
    conn = db.connect()
    channel(user_id)  # ensure the row exists
    conn.execute(
        "UPDATE watch_channels SET token=?, rotated_at=? WHERE user_id=?",
        (secrets.token_urlsafe(24), db.utcnow(), user_id))
    conn.commit()
    return channel(user_id)


def _user_for_token(token: str) -> str:
    row = db.connect().execute(
        "SELECT user_id FROM watch_channels WHERE token=?", (token,)
    ).fetchone()
    if row is None:
        # 404, not 403: the token *is* the address. A wrong one names
        # nothing, and confirming "that channel exists but isn't yours"
        # would itself be information.
        raise WatchError(404, "no such channel — check the drip URL, or "
                              "rotate the token in Settings and re-copy it")
    return row["user_id"]


# ---------------------------------------------------------------------------
# The drip: live readings from a Shortcut

# What a Shortcuts dictionary may call each metric. Left column is ours;
# the aliases are the names people actually reach for, cased as Shortcuts
# tends to case them. Matching is done lowercase-and-underscored.
_ALIASES = {
    "heart_rate": {"heart_rate", "heartrate", "hr", "pulse"},
    "resting_heart_rate": {"resting_heart_rate", "restingheartrate", "rhr"},
    "hrv": {"hrv", "heart_rate_variability", "heartratevariability",
            "heartratevariabilitysdnn"},
    "blood_oxygen": {"blood_oxygen", "bloodoxygen", "oxygen", "spo2",
                     "oxygen_saturation", "oxygensaturation", "o2"},
    "respiratory_rate": {"respiratory_rate", "respiratoryrate",
                         "respiration", "breathing_rate", "breathingrate"},
    "body_temperature": {"body_temperature", "bodytemperature",
                         "temperature", "temp", "wrist_temperature",
                         "wristtemperature"},
    "activity_level": {"activity_level", "activitylevel", "activity"},
}
_ALIAS_INDEX = {alias: metric for metric, names in _ALIASES.items()
                for alias in names}

_NUMBER = re.compile(r"-?\d+(?:\.\d+)?")


def _to_number(value) -> float | None:
    """``72``, ``"72"``, ``"72 count/min"``, ``"97%"`` — one reading."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    match = _NUMBER.search(str(value))
    return float(match.group()) if match else None


def _normalize(metric: str, value: float) -> float:
    if metric == "blood_oxygen" and value <= 1.0:
        return round(value * 100, 1)      # HealthKit's fraction → percent
    if metric == "body_temperature" and value > 45.0:
        return round((value - 32) * 5 / 9, 2)   # °F typed by a person → °C
    return value


def _clean_sample(payload: dict) -> dict:
    sample: dict = {}
    for key, raw in payload.items():
        metric = _ALIAS_INDEX.get(str(key).strip().lower().replace(" ", "_"))
        if metric is None:
            continue        # unknown keys are ignored, never an error
        value = _to_number(raw)
        if value is None:
            continue
        if metric == "activity_level":
            sample[metric] = value
        else:
            sample[metric] = _normalize(metric, value)
    return sample


def drip(token: str, payload: dict, qrme=None, vault_for=None) -> dict:
    """Accept one POST from the Shortcut: a flat reading or
    ``{"samples": [...]}``. Every sample runs the full Guardian pipeline.

    The reply is deliberately empty of substance — received count and
    whether anything was noticed. The full monitor response carries
    guidance and escalation detail, which must not be readable by a
    URL-bearer credential; anyone who wants the story signs in.
    """
    from . import guardian
    user_id = _user_for_token(token)
    pdi = vault_for(user_id) if vault_for is not None else None
    raw = payload.get("samples") if isinstance(payload.get("samples"), list) \
        else [payload]
    received, noticed = 0, False
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        sample = _clean_sample(entry)
        if not sample:
            continue
        result = guardian.monitor(user_id, sample, None, qrme=qrme, pdi=pdi)
        received += 1
        if result.get("detected") or result.get("drift"):
            noticed = True
    if received == 0:
        raise WatchError(422, "no readings recognized — use keys like "
                              "heart_rate, blood_oxygen, respiratory_rate")
    conn = db.connect()
    conn.execute(
        "UPDATE watch_channels SET last_drip_at=?, drips=drips+? WHERE"
        " user_id=?", (db.utcnow(), received, user_id))
    conn.commit()
    return {"received": received, "noticed": noticed}


# ---------------------------------------------------------------------------
# The seed: the Health export becomes the baseline

# HealthKit record types worth folding, and how their units meet ours.
# Oxygen arrives as a fraction; temperature can arrive in degF.
_HK_TYPES = {
    "HKQuantityTypeIdentifierHeartRate": "heart_rate",
    "HKQuantityTypeIdentifierRestingHeartRate": "resting_heart_rate",
    "HKQuantityTypeIdentifierHeartRateVariabilitySDNN": "hrv",
    "HKQuantityTypeIdentifierOxygenSaturation": "blood_oxygen",
    "HKQuantityTypeIdentifierRespiratoryRate": "respiratory_rate",
    "HKQuantityTypeIdentifierBodyTemperature": "body_temperature",
}

# Raw heart-rate records carry a motion context; only sedentary ones may
# feed a *resting* baseline. Records without the annotation are skipped —
# a walking heart rate folded into "your usual resting rate" would teach
# the bands a normal that isn't, and unlike the drip there is no person
# watching who could notice the number is an exercise reading.
_SEDENTARY = "1"    # HKHeartRateMotionContextSedentary


def _export_xml(data: bytes) -> bytes:
    """The upload is either export.zip or the bare export.xml inside it."""
    if zipfile.is_zipfile(io.BytesIO(data)):
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for name in zf.namelist():
                if name.endswith("export.xml") and "cda" not in name.lower():
                    return zf.read(name)
        raise WatchError(422, "that zip has no export.xml inside — export "
                              "again from the Health app")
    return data


def seed(user_id: str, data: bytes) -> dict:
    """Fold a Health export into the baselines: one value per metric per
    day (the median of that day's resting readings), oldest day first, so
    the EMA walks the same road the person did. Baselines only — the
    history writes no events and raises no check-ins."""
    from . import guardian
    if not data:
        raise WatchError(422, "the upload was empty")
    try:
        parser = ET.iterparse(io.BytesIO(_export_xml(data)), events=("end",))
        days: dict[tuple[str, str], list[float]] = defaultdict(list)
        for _event, elem in parser:
            if elem.tag != "Record":
                continue
            metric = _HK_TYPES.get(elem.get("type", ""))
            if metric is not None:
                value = _to_number(elem.get("value"))
                day = (elem.get("startDate") or "")[:10]
                if value is not None and day:
                    if metric == "heart_rate":
                        context = next(
                            (m.get("value") for m in elem.iter("MetadataEntry")
                             if m.get("key") == "HKMetadataKeyHeartRateMotionContext"),
                            None)
                        if context != _SEDENTARY:
                            elem.clear()
                            continue
                    unit = (elem.get("unit") or "").lower()
                    if metric == "body_temperature" and unit == "degf":
                        value = round((value - 32) * 5 / 9, 2)
                    else:
                        value = _normalize(metric, value)
                    days[(day, metric)].append(value)
            elem.clear()
    except ET.ParseError:
        raise WatchError(422, "that file isn't a Health export — expected "
                              "export.zip or export.xml from the Health app")
    report: dict[str, dict] = {}
    for (day, metric), values in sorted(days.items()):
        folded = guardian.update_baseline(
            user_id, metric, round(statistics.median(values), 2))
        entry = report.setdefault(metric, {"days": 0})
        entry["days"] += 1
        entry["baseline"] = folded["value"]
        entry["provisional"] = folded["provisional"]
    if not report:
        raise WatchError(422, "no usable readings in that export — it may "
                              "predate the watch, or hold only types JIM "
                              "doesn't track")
    return {"seeded": report}


# ---------------------------------------------------------------------------
# The setup card: everything the phone needs, spelled out

def setup(user_id: str, base_url: str) -> dict:
    """The channel plus the exact Shortcut recipe, ready to render. The
    steps live here rather than in the console so the phone-browser
    console, the desktop app, and anyone curl-ing the API read the same
    instructions."""
    import os

    from . import mobile as _mobile
    ch = channel(user_id)
    drip_url = f"{base_url.rstrip('/')}/watch/drip/{ch['token']}"
    # The truth about whether a phone can actually reach that address: a
    # loopback-bound backend serves a LAN URL nothing answers on. The
    # desktop shell sets JIM_HOST when the user flips Wi-Fi access on;
    # the CLI's phone/serve modes set it to how they actually bound.
    reachable = (os.environ.get("JIM_HOST") == "0.0.0.0"
                 or bool(_mobile.public_base()))
    return {
        "drip_url": drip_url,
        "phone_reachable": reachable,
        "last_drip_at": ch["last_drip_at"],
        "drips": ch["drips"],
        "shortcut": [
            "On the iPhone, open the Shortcuts app → Automation tab → "
            "+ New Automation.",
            "Pick 'Time of Day' → a time you're usually up (say 9:00 AM) → "
            "Repeat Daily → 'Run Immediately'. (Add a second automation at "
            "an evening time later if you like — Shortcuts has no hourly "
            "trigger.)",
            "Choose 'New Blank Automation' → Add Action → search 'Find "
            "Health Samples' → set type Heart Rate, sorted by Start Date "
            "latest first, limit 1.",
            "Add Action → 'Dictionary' → add key heart_rate, and for its "
            "value pick the Health Samples variable from the step above. "
            "Add blood_oxygen and respiratory_rate the same way if the "
            "watch records them.",
            "Add Action → 'Get Contents of URL' → paste the drip address "
            "into the URL field (THIS is where it goes) → show more → "
            "Method POST → Request Body JSON → add the Dictionary.",
            "Tap the automation and Run it once by hand — this screen "
            "shows the arrival.",
        ],
        "seed_hint": "Health app → your picture → Export All Health Data, "
                     "then upload the export.zip here. Months of watch "
                     "history become the baseline in one step.",
    }
