"""Error-report intake: what a crash report may say, and what is kept of it.

`app/src/errors.ts` records failed requests as an operation and a status —
never a message, never an id, because the backends put what people typed
straight into their error messages, and in this product that can be health
content. Until now the only place the batch could go was the Cloud Model
Gateway, a separate deployment most installs never configure; a field report
on the sibling product read the console's admission ("no collector
configured, so nothing is sent anywhere") and asked why the failures don't
funnel back to where corrections get made. Same answer here: the product's
own backend accepts the same report at the same path.

The intake is a **whitelist**, the same one the gateway enforces (kept in
step by the tests rather than by an import — this repo does not ship the
gateway). Anything outside it is refused with a 422 naming the field, never
quietly trimmed: a client whose redaction has stopped working needs to hear
about it, and the operator of that deployment is the only person who can fix
it. Nothing is stored as a report — rows fold into counters keyed by
(source, version, platform, op, status), because every extra dimension
narrows a row towards a single install, and a row that identifies one person
is what this whole design exists to avoid.
"""

from __future__ import annotations

import re

from . import db

TOP_LEVEL = {"source", "app_version", "platform", "language", "problems"}
PROBLEM_FIELDS = {"op", "status", "count", "day", "fingerprint"}
SOURCES = {"qrme", "jim-mini", "pdi"}

MAX_PROBLEMS = 50          # the console's own LIMIT; a larger batch is a bug
MAX_SHORT = 64             # version, platform, language

# `POST /users/{id}/checkins`. The verb list is the one the products serve.
# Every pattern ends `\Z`, never `$`: Python's `$` also matches before a
# trailing newline, which would admit "Win32\n" while the error messages
# promised otherwise.
_OP = re.compile(r"^(GET|POST|PUT|PATCH|DELETE) (/[A-Za-z0-9{}_\-./]*)\Z")

# A segment that survived redaction and should not have. Mirrors ID_LIKE in
# errors.ts — deliberately, so the two can be compared when either changes.
_ID_LIKE = (
    re.compile(r"^[a-z]{2,8}_[0-9a-z]+$", re.I),
    re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}"
               r"-[0-9a-f]{4}-[0-9a-f]{12}$", re.I),
    re.compile(r"^\d+$"),
    re.compile(r"^[A-Za-z0-9_-]{24,}$"),
)

_SHORT = re.compile(r"^[A-Za-z0-9 ._\-()/;:+]{1,%d}\Z" % MAX_SHORT)
_DAY = re.compile(r"^\d{4}-\d{2}-\d{2}\Z")
_FINGERPRINT = re.compile(r"^[0-9a-f]{8}\Z")


class Rejected(Exception):
    """The report was refused. The message names the offending field, so the
    deployment that sent it can find the bug."""


def _check_short(name: str, value: object) -> str:
    if not isinstance(value, str) or not _SHORT.match(value):
        raise Rejected(
            f"{name!r} must be a short plain string (≤{MAX_SHORT} chars, no "
            f"newlines or punctuation beyond ._-()/;:+) — got {value!r}")
    return value


def _check_op(value: object) -> str:
    if not isinstance(value, str):
        raise Rejected("'op' must be a string")
    m = _OP.match(value)
    if not m:
        raise Rejected(
            f"'op' must look like 'VERB /template/path' — got {value!r}")
    for segment in m.group(2).split("/"):
        if segment in ("", "{id}") or segment.startswith("{"):
            continue
        for pattern in _ID_LIKE:
            if pattern.match(segment):
                raise Rejected(
                    f"'op' contains a segment that looks like an identifier "
                    f"({segment!r}) — the client's redaction has stopped "
                    f"working, and accepting this would hide that")
    return value


def screen(payload: object) -> dict:
    """Raise :class:`Rejected` unless this is exactly an error report."""
    if not isinstance(payload, dict):
        raise Rejected("an error report is an object")

    extra = sorted(set(payload) - TOP_LEVEL)
    if extra:
        raise Rejected(
            f"unknown top-level keys {extra} — this intake accepts exactly "
            f"{sorted(TOP_LEVEL)}. A new key is refused rather than ignored: "
            "silently dropping it would let a client start sending content "
            "and never learn that nobody wanted it.")
    missing = sorted(TOP_LEVEL - set(payload))
    if missing:
        raise Rejected(f"missing keys {missing}")

    if payload["source"] not in SOURCES:
        raise Rejected(f"'source' must be one of {sorted(SOURCES)}")
    _check_short("app_version", payload["app_version"])
    _check_short("platform", payload["platform"])
    _check_short("language", payload["language"])  # validated, then unused

    problems = payload["problems"]
    if not isinstance(problems, list) or not problems:
        raise Rejected("'problems' must be a non-empty list")
    if len(problems) > MAX_PROBLEMS:
        raise Rejected(f"at most {MAX_PROBLEMS} problems per report")
    for p in problems:
        if not isinstance(p, dict):
            raise Rejected("each problem is an object")
        extra = sorted(set(p) - PROBLEM_FIELDS)
        if extra:
            raise Rejected(f"unknown problem keys {extra}")
        missing = sorted(PROBLEM_FIELDS - set(p))
        if missing:
            raise Rejected(f"problem missing keys {missing}")
        _check_op(p["op"])
        if not isinstance(p["status"], int) or not 0 <= p["status"] <= 599:
            raise Rejected("'status' must be an HTTP status code (0 for no "
                           "answer)")
        if not isinstance(p["count"], int) or not 1 <= p["count"] <= 100_000:
            raise Rejected("'count' must be a positive integer")
        if not isinstance(p["day"], str) or not _DAY.match(p["day"]):
            raise Rejected("'day' must be YYYY-MM-DD")
        if (not isinstance(p["fingerprint"], str)
                or not _FINGERPRINT.match(p["fingerprint"])):
            raise Rejected("'fingerprint' must be 8 hex characters")
    return payload


def add(payload: dict) -> int:
    """Fold a screened report into the counters. Returns failures folded."""
    conn = db.connect()
    folded = 0
    for p in payload["problems"]:
        conn.execute(
            "INSERT INTO problem_reports (source, app_version, platform, op,"
            " status, day, count, last_seen) VALUES (?,?,?,?,?,?,?,?)"
            " ON CONFLICT(source, app_version, platform, op, status)"
            " DO UPDATE SET count = count + excluded.count,"
            " day = excluded.day, last_seen = excluded.last_seen",
            (payload["source"], payload["app_version"], payload["platform"],
             p["op"], p["status"], p["day"], p["count"], db.utcnow()))
        folded += p["count"]
    conn.commit()
    return folded


def rows() -> list[dict]:
    """The aggregate, worst first — for whoever is fixing the bugs.

    `status_code` on the wire, not `status`: one name, one type, in every
    product — `status` is a string on a dozen other payloads, and the native
    readers declare their fields.
    """
    return [
        {k: v for k, v in {**dict(r), "status_code": r["status"]}.items()
         if k != "status"} for r in db.connect().execute(
            "SELECT * FROM problem_reports"
            " ORDER BY count DESC, last_seen DESC").fetchall()]
