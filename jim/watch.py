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

**The channel was never Apple-shaped** — it is a URL that accepts JSON,
and any wrist that can reach a phone can reach it. What *was*
Apple-shaped were the instructions and the export parser, which meant a
person with a Pixel Watch or a Fitbit stood in front of a setup card
that only spoke iPhone. :data:`DEVICES` is the fix: one recipe per
wearable family, chosen with ``?device=`` on the setup route, rendered
from the same card. Wear OS watches sync into Health Connect on the
phone, where a free automation app can read the numbers and POST them
on a schedule; Fitbit and Garmin sync to their own clouds, so their
recipes lead with the export — the baseline already happened there too
— and :func:`seed` reads Fitbit's Takeout files alongside Apple's
``export.xml``.

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
    # Joined to `users`, not read from `watch_channels` alone.
    #
    # A channel row outliving its user is a live deposit address for somebody
    # who asked to be forgotten: `delete_user_data` walked eighteen tables and
    # this was not one of them, so after "delete anything, anytime" the wrist
    # went on writing readings back in under the deleted id. The erase now
    # takes the channel down (jim/life.py), and this join is the second stop —
    # any future path that leaves a channel standing still cannot deposit.
    #
    #     asked     is this token a channel
    #     mattered  is there still anybody at the other end of it
    row = db.connect().execute(
        "SELECT c.user_id FROM watch_channels c JOIN users u ON u.id=c.user_id"
        " WHERE c.token=?", (token,)
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

# The words a watch's sensors may deposit alongside the numbers. A fall
# detection arrives as an event, not a measurement, and the numeric pipeline
# below would drop exactly the reading that most needs to arrive — a senior
# on the floor. Whitelisted vocabulary only (the detector's own), never free
# text: the drip is a URL-bearer credential and must stay deposit-only.
_MOVEMENT_EVENTS = {"fall", "collapse", "immobile"}
_PULSE_EVENTS = {"absent", "weak"}


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
        norm = str(key).strip().lower().replace(" ", "_")
        # The fall path (see _MOVEMENT_EVENTS above). "movement": "fall",
        # or the boolean shape Shortcuts produces ("fall_detected": true) —
        # both reach the detector, which already treats a fall as critical
        # and, with the crash watch armed, opens "are you okay?".
        if norm in ("movement", "motion"):
            word = str(raw).strip().lower()
            if word in _MOVEMENT_EVENTS:
                sample["movement"] = word
            continue
        if norm in ("fall", "fall_detected", "falldetected"):
            if raw in (True, 1, "1") or str(raw).strip().lower() in ("true", "yes"):
                sample["movement"] = "fall"
            continue
        if norm == "pulse" and str(raw).strip().lower() in _PULSE_EVENTS:
            sample["pulse"] = str(raw).strip().lower()
            continue
        metric = _ALIAS_INDEX.get(norm)
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
                              "heart_rate, blood_oxygen, respiratory_rate, "
                              "or movement: fall")
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


def _export_xml(data: bytes) -> bytes | None:
    """The upload is export.zip, the bare export.xml inside it — or a
    Fitbit Takeout zip, which is somebody else's history and just as much
    a baseline. None means "this zip is not Apple's; try Fitbit"."""
    if zipfile.is_zipfile(io.BytesIO(data)):
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for name in zf.namelist():
                if name.endswith("export.xml") and "cda" not in name.lower():
                    return zf.read(name)
        return None
    return data


def _fitbit_day(raw: str) -> str | None:
    """Takeout writes dates two ways — ``01/15/24 00:00:00`` in older
    exports, ISO in newer ones. Both are the same day."""
    import datetime

    text = str(raw).strip()
    for fmt in ("%m/%d/%y %H:%M:%S", "%m/%d/%Y %H:%M:%S"):
        try:
            return datetime.datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            pass
    if re.match(r"\d{4}-\d{2}-\d{2}", text):
        return text[:10]
    return None


def _fitbit_days(data: bytes) -> dict:
    """Read a Fitbit Takeout zip into the same ``days`` shape the Apple
    parser produces. Resting heart rate comes from the
    ``resting_heart_rate-*.json`` files; HRV from the daily summary CSVs.
    The continuous ``heart_rate-*.json`` stream is deliberately skipped —
    it includes exercise, and folding it would teach the resting baseline
    a workout, the exact mistake the Apple path's sedentary filter
    exists to prevent."""
    import csv
    import json as _json

    days: dict[tuple[str, str], list[float]] = defaultdict(list)
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        for name in zf.namelist():
            base = name.rsplit("/", 1)[-1].lower()
            if base.startswith("resting_heart_rate-") and \
                    base.endswith(".json"):
                try:
                    rows = _json.loads(zf.read(name))
                except ValueError:
                    continue
                for row in rows if isinstance(rows, list) else []:
                    value = _to_number(
                        (row.get("value") or {}).get("value"))
                    day = _fitbit_day(row.get("dateTime", ""))
                    if value and day:
                        days[(day, "resting_heart_rate")].append(value)
            elif "heart_rate_variability" in base and \
                    base.endswith(".csv") and "summary" in base:
                text = zf.read(name).decode("utf-8", errors="ignore")
                for row in csv.DictReader(io.StringIO(text)):
                    keys = {k.strip().lower(): v for k, v in row.items()
                            if k}
                    value = _to_number(keys.get("rmssd"))
                    day = _fitbit_day(keys.get("timestamp", ""))
                    if value and day:
                        days[(day, "hrv")].append(value)
    return days


def seed(user_id: str, data: bytes) -> dict:
    """Fold a Health export into the baselines: one value per metric per
    day (the median of that day's resting readings), oldest day first, so
    the EMA walks the same road the person did. Baselines only — the
    history writes no events and raises no check-ins."""
    from . import guardian
    if not data:
        raise WatchError(422, "the upload was empty")
    xml = _export_xml(data)
    if xml is None:
        # An Apple-less zip: read it as a Fitbit Takeout export, which
        # carries the same months of history under different filenames.
        days = _fitbit_days(data)
        if not days:
            raise WatchError(
                422, "that zip has no export.xml and no Fitbit files "
                     "inside \u2014 export again from the Health app, or "
                     "from Google Takeout for a Fitbit")
        return _fold(user_id, days, guardian)
    try:
        parser = ET.iterparse(io.BytesIO(xml), events=("end",))
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
    return _fold(user_id, days, guardian)


def _fold(user_id: str, days: dict, guardian) -> dict:
    """One value per metric per day — the median — oldest first, so the
    EMA walks the same road the person did. Shared by the Apple and
    Fitbit paths because the baseline does not care which wrist."""
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
# The setup card: everything the phone needs, spelled out — per wearable

#: The wearables the card knows how to teach. Keys are what ``?device=``
#: accepts; adding a family later is one entry here — the console renders
#: the picker from this list, so no client changes when it grows.
DEVICES = {
    "apple_watch": "Apple Watch (iPhone)",
    "wear_os": "Android watch (Wear OS \u2014 Pixel, Galaxy)",
    "fitbit": "Fitbit",
    "garmin": "Garmin",
}


def _recipe(device: str, drip_url: str) -> dict:
    """The steps and the seed hint for one wearable family.

    Each recipe is honest about its platform: Wear OS numbers live in
    Health Connect on the phone, where an automation app can read and
    POST them; Fitbit and Garmin sync to their own clouds, so their
    recipes lead with the export \u2014 and Garmin's export is not
    parseable here yet, which the hint says instead of hiding.
    """
    if device == "wear_os":
        return {"steps": [
            "On the phone, install a free automation app that can read "
            "Health Connect and make web requests \u2014 MacroDroid and "
            "Tasker both can. Your watch already syncs its readings into "
            "Health Connect.",
            "Create a new macro/task with a Time trigger (say every hour, "
            "or morning and evening).",
            "Add an action to read the latest Heart Rate (and Blood "
            "Oxygen / Respiratory Rate if your watch records them) from "
            "Health Connect. Grant the read permission when the app asks.",
            "Add an HTTP Request action \u2014 Method POST, Content-Type "
            "application/json \u2014 and paste the drip address into the "
            "URL field (THIS is where it goes).",
            "For the body, send a JSON dictionary like "
            '{"heart_rate": 72, "blood_oxygen": 97} using the values '
            "read in the step above. Spelling is forgiving \u2014 hr, "
            "pulse and heartrate all land.",
            "Run the macro once by hand \u2014 this screen shows the "
            "arrival.",
        ], "seed_hint":
            "No bulk export to upload here yet \u2014 Health Connect "
            "keeps recent history on the phone, so let the drip run and "
            "the baseline establishes itself within a few days."}
    if device == "fitbit":
        return {"steps": [
            "The baseline first: Fitbit keeps your history in its own "
            "cloud. Request your data from Google Takeout (takeout."
            "google.com \u2192 deselect all \u2192 Fitbit \u2192 "
            "Export), then upload the zip below \u2014 months of "
            "resting heart rate become the baseline in one step.",
            "For the live drip, install an automation app on the phone "
            "(MacroDroid or Tasker) with a Time trigger.",
            "Add an HTTP Request action \u2014 Method POST, Content-Type "
            "application/json \u2014 and paste the drip address into the "
            "URL field (THIS is where it goes).",
            'Send a JSON dictionary like {"resting_heart_rate": 62} with '
            "the day's number from the Fitbit app \u2014 or type "
            "readings on the Monitor screen; both run the same pipeline.",
            "Run it once by hand \u2014 this screen shows the arrival.",
        ], "seed_hint":
            "Google Takeout \u2192 Fitbit \u2192 Export, then upload "
            "the zip here. The resting heart rate and HRV files inside "
            "become the baseline in one step."}
    if device == "garmin":
        return {"steps": [
            "Garmin syncs to Garmin Connect, its own cloud. For the live "
            "drip, install an automation app on the phone (MacroDroid or "
            "Tasker) with a Time trigger.",
            "Add an HTTP Request action \u2014 Method POST, Content-Type "
            "application/json \u2014 and paste the drip address into the "
            "URL field (THIS is where it goes).",
            'Send a JSON dictionary like {"resting_heart_rate": 60, '
            '"blood_oxygen": 97} with the numbers from the Connect app '
            "\u2014 or type readings on the Monitor screen; both run "
            "the same pipeline.",
            "Run it once by hand \u2014 this screen shows the arrival.",
        ], "seed_hint":
            "Garmin's account export (garmin.com \u2192 Export Your "
            "Data) is not parseable here yet \u2014 the drip carries "
            "the baseline instead, a few days of readings at a time."}
    return {"steps": [
        "On the iPhone, open the Shortcuts app \u2192 Automation tab "
        "\u2192 + New Automation.",
        "Pick 'Time of Day' \u2192 a time you're usually up (say 9:00 "
        "AM) \u2192 Repeat Daily \u2192 'Run Immediately'. (Add a "
        "second automation at an evening time later if you like \u2014 "
        "Shortcuts has no hourly trigger.)",
        "Choose 'New Blank Automation' \u2192 Add Action \u2192 search "
        "'Find Health Samples' \u2192 set type Heart Rate, sorted by "
        "Start Date latest first, limit 1.",
        "Add Action \u2192 'Dictionary' \u2192 add key heart_rate, and "
        "for its value pick the Health Samples variable from the step "
        "above. Add blood_oxygen and respiratory_rate the same way if "
        "the watch records them.",
        "Add Action \u2192 'Get Contents of URL' \u2192 paste the drip "
        "address into the URL field (THIS is where it goes) \u2192 show "
        "more \u2192 Method POST \u2192 Request Body JSON \u2192 add "
        "the Dictionary.",
        "Tap the automation and Run it once by hand \u2014 this screen "
        "shows the arrival.",
    ], "seed_hint":
        "Health app \u2192 your picture \u2192 Export All Health Data, "
        "then upload the export.zip here. Months of watch history become "
        "the baseline in one step."}


def setup(user_id: str, base_url: str,
          device: str = "apple_watch") -> dict:
    """The channel plus the exact recipe for the wearable the person
    actually wears. The steps live here rather than in the console so the
    phone-browser console, the desktop app, and anyone curl-ing the API
    read the same instructions \u2014 and so a new wearable family is one
    dict entry, not four client changes."""
    import os

    from . import mobile as _mobile
    if device not in DEVICES:
        raise WatchError(
            422, "unknown device \u2014 expected one of "
                 + ", ".join(sorted(DEVICES)))
    ch = channel(user_id)
    drip_url = f"{base_url.rstrip('/')}/watch/drip/{ch['token']}"
    # The truth about whether a phone can actually reach that address: a
    # loopback-bound backend serves a LAN URL nothing answers on. The
    # desktop shell sets JIM_HOST when the user flips Wi-Fi access on;
    # the CLI's phone/serve modes set it to how they actually bound.
    reachable = (os.environ.get("JIM_HOST") == "0.0.0.0"
                 or bool(_mobile.public_base()))
    recipe = _recipe(device, drip_url)
    return {
        "drip_url": drip_url,
        "phone_reachable": reachable,
        "last_drip_at": ch["last_drip_at"],
        "drips": ch["drips"],
        "device": device,
        "devices": [{"key": k, "name": n} for k, n in DEVICES.items()],
        "steps": recipe["steps"],
        # The pre-picker name of the same list, kept so nothing that
        # learned the old card breaks.
        "shortcut": recipe["steps"],
        "seed_hint": recipe["seed_hint"],
    }
