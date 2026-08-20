"""The weekly letter: what your numbers meant, written like a person would.

The field research kept circling the same complaint — trackers show charts
and nobody reads charts about themselves. What people asked for is a short
letter: here is what your week actually held, in words. The honest offline
shape of that: the letter is composed **only from what was logged** — a
deterministic digest of the week's check-ins, meals, habit marks, journal
entries and goal movement, with no invented feelings and no coaching
homework. When an online model is standing it turns the digest into warm
prose without adding a single fact the digest doesn't carry; offline, the
digest itself is the letter, plainly labeled. A week with nothing logged
gets no letter — a letter about nothing would have to invent its contents.
"""

from __future__ import annotations

import datetime as _dt

from . import db, llm, offline, research


class LetterError(Exception):
    pass


_PROSE_SYSTEM = (
    "You turn a factual digest of somebody's week into a short, warm letter "
    "addressed to them. Use only the facts in the digest — never invent "
    "events, feelings, numbers or advice the digest does not carry. No "
    "greeting-card filler; three or four honest sentences that tell them "
    "what their week held. Answer with the letter only.")


def _week_window(now: str) -> tuple[str, str]:
    """The seven days ending now: (start_iso, start_date)."""
    end = _dt.datetime.fromisoformat(now)
    start = end - _dt.timedelta(days=7)
    return start.isoformat(), start.date().isoformat()


def _digest(user_id: str, since: str) -> list[str]:
    """Plain-English lines for everything the week actually held — each
    line a fact from a table, none of them a judgement."""
    conn = db.connect()
    lines: list[str] = []

    row = conn.execute(
        "SELECT COUNT(*) AS n, AVG(mood) AS mood, AVG(energy) AS energy,"
        " AVG(stress) AS stress FROM checkins WHERE user_id=? AND"
        " created_at>=?", (user_id, since)).fetchone()
    if row["n"]:
        line = (f"{row['n']} check-in{'s' if row['n'] != 1 else ''},"
                f" average mood {row['mood']:.1f} of 5")
        if row["energy"] is not None:
            line += f", energy {row['energy']:.1f}"
        if row["stress"] is not None:
            line += f", stress {row['stress']:.1f}"
        lines.append(line)

    meals = conn.execute(
        "SELECT logged FROM meals WHERE user_id=? AND created_at>=?"
        " ORDER BY created_at DESC", (user_id, since)).fetchall()
    if meals:
        sample = "; ".join(m["logged"] for m in meals[:3])
        lines.append(f"{len(meals)} meal{'s' if len(meals) != 1 else ''}"
                     f" logged, most recently: {sample}")

    row = conn.execute(
        "SELECT COUNT(*) AS n FROM habit_logs hl JOIN habits h ON"
        " h.id=hl.habit_id WHERE h.user_id=? AND hl.day>=?",
        (user_id, since[:10])).fetchone()
    if row["n"]:
        lines.append(f"{row['n']} habit mark{'s' if row['n'] != 1 else ''}")

    row = conn.execute(
        "SELECT COUNT(*) AS n FROM journal WHERE user_id=? AND"
        " created_at>=?", (user_id, since)).fetchone()
    if row["n"]:
        lines.append(f"{row['n']} journal entr"
                     f"{'ies' if row['n'] != 1 else 'y'}")

    goals = conn.execute(
        "SELECT title, status, progress FROM goals WHERE user_id=? AND"
        " updated_at>=? AND updated_at != created_at", (user_id, since)
    ).fetchall()
    for g in goals:
        if g["status"] == "completed":
            lines.append(f"goal completed: {g['title']}")
        else:
            lines.append(f"goal moved: {g['title']}"
                         f" ({round(g['progress'] * 100)}%)")

    # What JIM went and learned on this person's behalf — a typed
    # question, the coach's study, an unattended errand: all excursions,
    # and all part of their week whether or not they watched it happen.
    studies = conn.execute(
        "SELECT topic FROM excursions WHERE user_id=? AND created_at>=?"
        " ORDER BY created_at DESC", (user_id, since)).fetchall()
    if studies:
        sample = "; ".join(s["topic"] for s in studies[:3])
        lines.append(f"{len(studies)}"
                     f" stud{'ies' if len(studies) != 1 else 'y'} taken,"
                     f" most recently: {sample}")
    return lines


def _watching_lines(user_id: str, since: str, pdi) -> list[str]:
    """What the lookouts noticed this week — a changed page is a real
    event the person asked to be told about, and a failing watch is a
    fact they should not have to open a task window to learn. Both read
    from the vault (the capture's own change date, the runs ledger's
    latest round); no vault, or an unreached one, contributes nothing —
    the letter never fails for its least essential paragraph."""
    if pdi is None:
        return []
    from . import lookout as lookout_mod
    rows = db.connect().execute(
        "SELECT * FROM lookouts WHERE user_id=? ORDER BY created_at, rowid",
        (user_id,)).fetchall()
    lines: list[str] = []
    for r in rows:
        sealed = lookout_mod._capture(pdi, r["task_id"])
        changed = (sealed or {}).get("changed_at")
        if changed and changed >= since:
            lines.append(f"watched page {r['url']} changed on {changed[:10]}")
        if lookout_mod._trouble(pdi, r["task_id"]):
            lines.append(f"the watch on {r['url']} has been failing")
    return lines


def compose(user: dict, cloud=None, pdi=None) -> dict:
    """Write this week's letter from what the week actually held."""
    user_id = user["id"]
    now = db.utcnow()
    since, week_start = _week_window(now)
    lines = _digest(user_id, since) + _watching_lines(user_id, since, pdi)
    if not lines:
        raise LetterError("nothing was logged this week — a letter about "
                          "an empty week would have to invent its contents")

    digest = "\n".join("- " + l for l in lines)
    body, described_by = digest, "digest"
    # The letter is not the looser door. The study path sanitizes what
    # leaves and writes down that it left; the letter — carrying the
    # week's events, watched pages and appointments — reached the same
    # network models with neither. Now a voice that would leave the host
    # gets the *sanitized* digest (the person's own letter keeps the
    # real one), and `left_host` says what happened, in the excursions'
    # own word. The vault's voice and the local ones see the full digest
    # — nothing leaves, and the prose is better for it.
    choice = llm.resolve_choice(llm.get_choice(user_id))
    # The vault's wire to PDI is the facility's own (`network: True` in
    # the registry, honestly — a socket opens), but the excursions set
    # the meaning of `left_host` and it means *left the facility*: the
    # vault branch is explicitly not-leaving there, so it is here.
    left_host = (choice != "vault" and not offline.enabled()
                 and llm.is_network(choice))
    outbound, redactions = (research.sanitize(user_id, digest)
                            if left_host else (digest, 0))
    result = llm.generate_for_user(user_id, _PROSE_SYSTEM, outbound,
                                   cloud=cloud)
    prose = (result.get("text") or "").strip()
    if prose and result.get("provider") not in (None, "stub"):
        body, described_by = prose, "model"

    conn = db.connect()
    letter_id = db.new_id("let")
    conn.execute(
        "INSERT INTO letters (id, user_id, week_start, body, described_by,"
        " digest, left_host, redactions, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        (letter_id, user_id, week_start, body, described_by, digest,
         int(left_host), redactions, now))
    conn.commit()
    return {"id": letter_id, "week_start": week_start, "body": body,
            "described_by": described_by, "digest": lines,
            "left_host": left_host, "redactions": redactions}


def shelf(user_id: str, limit: int = 12) -> list[dict]:
    """Past letters, newest first."""
    rows = db.connect().execute(
        "SELECT id, week_start, body, described_by, left_host, redactions,"
        " created_at FROM letters"
        " WHERE user_id=? ORDER BY created_at DESC, rowid DESC LIMIT ?",
        (user_id, limit)).fetchall()
    return [{**dict(r), "left_host": bool(r["left_host"])} for r in rows]
