"""How old is the reading, and am I allowed to act on something that old.

The claim under audit is "real-time", and real-time is a network word.
Between the wrist and the decision there is BLE to a phone, radio to a
tower, backhaul, peering, ingress, and the vault round-trip — each hop can
add hundreds of milliseconds or stall for ninety seconds, and none of them
is visible from inside this code. So this module stops the application
asking *what is the reading* and makes it ask *how old is the reading,
and am I allowed to act on something that old*.

That is a staleness contract. Three parts, the design read's own words.

## Part 1 — timestamp at the source

Every reading may carry ``observed_at`` (the device's clock, at the moment
of measurement) and ``device_now`` (the same clock, at the moment of
sending). Stamping on arrival instead is measuring your own ingest queue
and calling it physiology: a reading that sat in a phone's outbox through
a dead-zone walk arrives four minutes old and looks newborn.

The skew measurement rides the same pair: ``skew_ms = device_now -
received_at`` is the device-vs-server offset at this very ingress, and the
age computes as ``device_now - observed_at`` — the device's own clock on
both ends, so its skew cancels out of the age entirely. What the skew is
still for is honesty about the *unknown* transit leg, carried as
``uncertainty_ms`` rather than folded silently into the number.

Two edge cases, written down because they will bite. A reading whose
``observed_at`` is in the future is a skew measurement that failed — it is
kept with unknown age, never clamped to zero. And a burst (a phone
flushing its outbox when signal returns) is one fresh reading and many
pieces of history; each row carries its own age, so a consumer averaging
them unweighted is a consumer this module can now catch lying.

## Part 2 — every consumer declares a freshness window

No code path reads a biometric value without saying, in that same path,
the maximum age it will act on. Per consumer, because the windows
genuinely differ — a number on a screen implies *now*; a trend is
supposed to age. Past the window the consumer does not guess and does not
silently reuse the last value: it gets a named state — ``fresh``,
``stale``, ``unreachable`` — on the record.

Every read through :func:`read` also records the age it decided on, which
is Part 4 in disguise: **the number you can produce on demand** when
somebody finally asks what "real-time" means is the 95th percentile age
at the moment of decision — measured, not designed.

## Part 3 — separate the two silences

A heartbeat from the wrist channel, independent of the readings
themselves. Readings stop while the heartbeat continues: that is the
person (the watch is off the wrist, the sensor is dry). Both stop: that
is the network. The heartbeat continues but ages past its own window:
that is the phone, sitting between them. Three different silences, three
different ladders — and until now this product had one silence and called
it all the same thing.
"""

from __future__ import annotations

from datetime import datetime, timezone

from . import db

#: Per-consumer freshness windows, in milliseconds. The design read's own
#: table: a live display implies now; conditioning acts on a person's
#: state, where the wrong state is worse than no state; a trend is
#: supposed to age; an escalation wakes a person up.
WINDOWS: dict[str, int] = {
    "display": 5_000,
    "conditioning": 30_000,
    "escalation": 60_000,
    "trend": 900_000,
}

#: The heartbeat's own window — past this, the channel itself is the
#: silence, whatever the readings are doing.
HEARTBEAT_MS = 90_000

#: How many decision ages are kept per consumer, enough for an honest p95
#: without a table that grows forever.
_KEPT = 500


def _ms(iso: str | None) -> float | None:
    if not iso:
        return None
    try:
        stamp = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return None
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)
    return stamp.timestamp() * 1000.0


def _now_ms() -> float:
    return datetime.now(timezone.utc).timestamp() * 1000.0


def noted(user_id: str, observed_at: str | None,
          device_now: str | None) -> dict:
    """A reading crossed the ingress: stamp it, measure the skew, keep it.

    Returns the freshness facts for the door's answer. A reading with no
    source timestamp is kept too — its age is *unknown*, which every
    consumer treats as stale rather than as fresh; the absence is the
    honest datum.
    """
    received = _now_ms()
    observed = _ms(observed_at)
    sent = _ms(device_now)
    skew_ms = (sent - received) if sent is not None else None
    if observed is not None and sent is not None:
        age_ms = sent - observed
        if age_ms < 0:
            # A future observed_at is a skew measurement that failed.
            # Logged as unknown, never clamped to zero.
            age_ms = None
    else:
        age_ms = None
    uncertainty = abs(skew_ms) if skew_ms is not None else None
    conn = db.connect()
    conn.execute(
        "INSERT INTO freshness_readings (user_id, observed_at, received_at,"
        " skew_ms, age_ms) VALUES (?,?,?,?,?)",
        (user_id, observed_at, db.utcnow(), skew_ms, age_ms))
    conn.execute(
        "DELETE FROM freshness_readings WHERE user_id=? AND rowid NOT IN"
        " (SELECT rowid FROM freshness_readings WHERE user_id=?"
        "  ORDER BY rowid DESC LIMIT ?)", (user_id, user_id, _KEPT))
    conn.commit()
    return {"age_ms": age_ms, "skew_ms": skew_ms,
            "uncertainty_ms": uncertainty}


def beat(user_id: str, device_now: str | None) -> dict:
    """The wrist channel says it is alive — no reading attached, which is
    the whole point: this is the pulse of the *channel*, so its silence
    and the readings' silence can finally mean different things."""
    received = _now_ms()
    sent = _ms(device_now)
    skew_ms = (sent - received) if sent is not None else None
    conn = db.connect()
    conn.execute(
        "INSERT INTO freshness_heartbeats (user_id, received_at, skew_ms)"
        " VALUES (?,?,?)", (user_id, db.utcnow(), skew_ms))
    conn.execute(
        "DELETE FROM freshness_heartbeats WHERE user_id=? AND rowid NOT IN"
        " (SELECT rowid FROM freshness_heartbeats WHERE user_id=?"
        "  ORDER BY rowid DESC LIMIT 50)", (user_id, user_id))
    conn.commit()
    return {"skew_ms": skew_ms}


def _latest_age(user_id: str) -> float | None:
    """The newest reading's age as of *now* — its age at ingress plus the
    time it has sat here since."""
    row = db.connect().execute(
        "SELECT received_at, age_ms FROM freshness_readings WHERE user_id=?"
        " ORDER BY rowid DESC LIMIT 1", (user_id,)).fetchone()
    if row is None:
        return None
    since = _now_ms() - (_ms(row["received_at"]) or _now_ms())
    if row["age_ms"] is None:
        return None
    return row["age_ms"] + max(0.0, since)


def read(user_id: str, consumer: str) -> dict:
    """The reading's standing for one declared consumer, on the record.

    ``fresh`` — a reading of known age inside the consumer's window.
    ``stale`` — a reading exists but is past the window, or its age is
    unknown (unmeasured skew is unknown age, and unknown is stale, never
    fresh). ``unreachable`` — no reading has ever arrived.

    Every call records the age it decided on, which is what makes the
    p95-at-decision a measured number rather than a designed one.
    """
    if consumer not in WINDOWS:
        raise KeyError(f"undeclared consumer {consumer!r} — add it to "
                       "freshness.WINDOWS with the maximum age it acts on")
    window = WINDOWS[consumer]
    have = db.connect().execute(
        "SELECT COUNT(*) AS n FROM freshness_readings WHERE user_id=?",
        (user_id,)).fetchone()["n"]
    age = _latest_age(user_id)
    if not have:
        state = "unreachable"
    elif age is None or age > window:
        state = "stale"
    else:
        state = "fresh"
    conn = db.connect()
    conn.execute(
        "INSERT INTO freshness_decisions (user_id, consumer, age_ms, state,"
        " decided_at) VALUES (?,?,?,?,?)",
        (user_id, consumer, age, state, db.utcnow()))
    conn.execute(
        "DELETE FROM freshness_decisions WHERE user_id=? AND consumer=?"
        " AND rowid NOT IN (SELECT rowid FROM freshness_decisions"
        "  WHERE user_id=? AND consumer=? ORDER BY rowid DESC LIMIT ?)",
        (user_id, consumer, user_id, consumer, _KEPT))
    conn.commit()
    return {"state": state, "age_ms": age, "window_ms": window}


def silences(user_id: str) -> dict:
    """Which silence this is — the person, the network, or the phone.

    ``alive`` — readings inside the conditioning window.
    ``person-quiet`` — the channel's heartbeat is current and the readings
    are not: the watch is off the wrist. The clinical ladder's business.
    ``phone-between`` — a heartbeat exists but has aged past its own
    window while newer than the darkest reading: the phone is sitting
    between the wrist and the wire. Ops, but the near end.
    ``network-dark`` — no current heartbeat and no current readings: the
    wire itself. The ops ladder, and never a clinical alarm.
    """
    beat_row = db.connect().execute(
        "SELECT received_at FROM freshness_heartbeats WHERE user_id=?"
        " ORDER BY rowid DESC LIMIT 1", (user_id,)).fetchone()
    beat_age = (_now_ms() - (_ms(beat_row["received_at"]) or 0)
                if beat_row else None)
    reading_age = _latest_age(user_id)
    readings_current = (reading_age is not None
                        and reading_age <= WINDOWS["conditioning"])
    if readings_current:
        verdict = "alive"
    elif beat_age is not None and beat_age <= HEARTBEAT_MS:
        verdict = "person-quiet"
    elif beat_age is not None and beat_age <= HEARTBEAT_MS * 4:
        verdict = "phone-between"
    else:
        verdict = "network-dark"
    return {"verdict": verdict,
            "reading_age_ms": reading_age,
            "heartbeat_age_ms": beat_age}


def _p95(values: list[float]) -> float | None:
    if not values:
        return None
    values = sorted(values)
    return values[min(len(values) - 1, int(0.95 * len(values)))]


def stats(user_id: str) -> dict:
    """The dashboard's numbers: age distribution at ingress, and — the one
    somebody will eventually demand in a deposition — the p95 age at the
    moment of decision, per consumer. Measured, not designed."""
    conn = db.connect()
    ingress = [r["age_ms"] for r in conn.execute(
        "SELECT age_ms FROM freshness_readings WHERE user_id=?"
        " AND age_ms IS NOT NULL", (user_id,)).fetchall()]
    unknown = conn.execute(
        "SELECT COUNT(*) AS n FROM freshness_readings WHERE user_id=?"
        " AND age_ms IS NULL", (user_id,)).fetchone()["n"]
    per_consumer = {}
    for consumer in WINDOWS:
        ages = [r["age_ms"] for r in conn.execute(
            "SELECT age_ms FROM freshness_decisions WHERE user_id=?"
            " AND consumer=? AND age_ms IS NOT NULL",
            (user_id, consumer)).fetchall()]
        states = {r["state"]: r["n"] for r in conn.execute(
            "SELECT state, COUNT(*) AS n FROM freshness_decisions"
            " WHERE user_id=? AND consumer=? GROUP BY state",
            (user_id, consumer)).fetchall()}
        per_consumer[consumer] = {
            "window_ms": WINDOWS[consumer],
            "p95_age_at_decision_ms": _p95(ages),
            "decisions": states,
        }
    return {
        "ingress": {"p95_age_ms": _p95(ingress),
                    "readings": len(ingress) + unknown,
                    "unknown_age": unknown},
        "consumers": per_consumer,
        **silences(user_id),
    }
