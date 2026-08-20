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


def _digest(user_id: str, since: str, until: str) -> list[str]:
    """Plain-English lines for everything the week actually held — each
    line a fact from a table, none of them a judgement. Bounded on both
    sides so a letter rebuilt later reads its own week, not everything
    since."""
    conn = db.connect()
    lines: list[str] = []

    row = conn.execute(
        "SELECT COUNT(*) AS n, AVG(mood) AS mood, AVG(energy) AS energy,"
        " AVG(stress) AS stress FROM checkins WHERE user_id=? AND"
        " created_at>=? AND created_at<?",
        (user_id, since, until)).fetchone()
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
        " AND created_at<? ORDER BY created_at DESC",
        (user_id, since, until)).fetchall()
    if meals:
        sample = "; ".join(m["logged"] for m in meals[:3])
        lines.append(f"{len(meals)} meal{'s' if len(meals) != 1 else ''}"
                     f" logged, most recently: {sample}")

    row = conn.execute(
        "SELECT COUNT(*) AS n FROM habit_logs hl JOIN habits h ON"
        " h.id=hl.habit_id WHERE h.user_id=? AND hl.day>=? AND hl.day<?",
        (user_id, since[:10], until[:10])).fetchone()
    if row["n"]:
        lines.append(f"{row['n']} habit mark{'s' if row['n'] != 1 else ''}")

    row = conn.execute(
        "SELECT COUNT(*) AS n FROM journal WHERE user_id=? AND"
        " created_at>=? AND created_at<?",
        (user_id, since, until)).fetchone()
    if row["n"]:
        lines.append(f"{row['n']} journal entr"
                     f"{'ies' if row['n'] != 1 else 'y'}")

    goals = conn.execute(
        "SELECT title, status, progress FROM goals WHERE user_id=? AND"
        " updated_at>=? AND updated_at<? AND updated_at != created_at",
        (user_id, since, until)).fetchall()
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
        " AND created_at<? ORDER BY created_at DESC",
        (user_id, since, until)).fetchall()
    if studies:
        sample = "; ".join(s["topic"] for s in studies[:3])
        lines.append(f"{len(studies)}"
                     f" stud{'ies' if len(studies) != 1 else 'y'} taken,"
                     f" most recently: {sample}")
    return lines


def _watching_lines(user_id: str, since: str, pdi, until: str,
                    live: bool = True) -> list[str]:
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
        if changed and since <= changed < until:
            # A transcript's change is new words said, not a page edited —
            # the letter calls the watched thing what it is.
            what = ("recording" if (sealed or {}).get("transcribed")
                    else "page")
            lines.append(f"watched {what} {r['url']} changed on"
                         f" {changed[:10]}")
        # "Has been failing" is a fact about *now*; a letter rebuilt for
        # an old week can only honestly restate what is still derivable,
        # and this line is not.
        if live and lookout_mod._trouble(pdi, r["task_id"]):
            lines.append(f"the watch on {r['url']} has been failing")
    return lines


def _write_body(user_id: str, lines: list[str], cloud=None) -> dict:
    """Turn a week's digest lines into the letter's body, keeping every
    promise at once: the chosen voice writes it, the digest is sanitized
    before any voice that would leave the host (the letter is not the
    looser door), and `left_host` says what happened in the excursions'
    own word. The vault's wire to PDI is the facility's own (`network:
    True` in the registry, honestly — a socket opens), but the
    excursions set the meaning of `left_host` and it means *left the
    facility*."""
    digest = "\n".join("- " + l for l in lines)
    body, described_by = digest, "digest"
    choice = llm.resolve_choice(llm.get_choice(user_id))
    left_host = (choice != "vault" and not offline.enabled()
                 and llm.is_network(choice))
    outbound, redactions = (research.sanitize(user_id, digest)
                            if left_host else (digest, 0))
    result = llm.generate_for_user(user_id, _PROSE_SYSTEM, outbound,
                                   cloud=cloud)
    prose = (result.get("text") or "").strip()
    if prose and result.get("provider") not in (None, "stub"):
        body, described_by = prose, "model"
    return {"body": body, "described_by": described_by, "digest": digest,
            "left_host": left_host, "redactions": redactions}


def mark_forgotten(user_id: str) -> None:
    """Every forgetting door calls this: the letters are cached views of
    the tables, and this is the cache's invalidation — a letter built
    before the last forgetting rebuilds from what the tables still hold
    the next time the shelf is read (the letter does not outlive the
    memory)."""
    conn = db.connect()
    conn.execute("UPDATE users SET forgot_at=? WHERE id=?",
                 (db.utcnow(), user_id))
    conn.commit()


def compose(user: dict, cloud=None, pdi=None) -> dict:
    """Write this week's letter from what the week actually held."""
    user_id = user["id"]
    now = db.utcnow()
    since, week_start = _week_window(now)
    lines = _digest(user_id, since, now) + _watching_lines(
        user_id, since, pdi, now, live=True)
    if not lines:
        raise LetterError("nothing was logged this week — a letter about "
                          "an empty week would have to invent its contents")
    made = _write_body(user_id, lines, cloud=cloud)
    conn = db.connect()
    letter_id = db.new_id("let")
    conn.execute(
        "INSERT INTO letters (id, user_id, week_start, body, described_by,"
        " digest, left_host, redactions, built_at, created_at)"
        " VALUES (?,?,?,?,?,?,?,?,?,?)",
        (letter_id, user_id, week_start, made["body"], made["described_by"],
         made["digest"], int(made["left_host"]), made["redactions"],
         now, now))
    conn.commit()
    return {"id": letter_id, "week_start": week_start, "body": made["body"],
            "described_by": made["described_by"], "digest": lines,
            "left_host": made["left_host"],
            "redactions": made["redactions"]}


def shelf(user_id: str, limit: int = 12, cloud=None, pdi=None) -> list[dict]:
    """Past letters, newest first — and none of them outliving the
    memory they were made from. A letter is a cached view of its week's
    tables: when any forgetting has touched this person since a letter
    was built, the letter rebuilds from what the tables still hold —
    its own week window, both bounds — before it is shown. A week whose
    facts are gone loses its letter with them; that is the design, not
    a failure. Untouched letters read straight from the cache and never
    change under the reader."""
    conn = db.connect()
    u = conn.execute("SELECT forgot_at FROM users WHERE id=?",
                     (user_id,)).fetchone()
    forgot_at = u["forgot_at"] if u else None
    rows = conn.execute(
        "SELECT * FROM letters"
        " WHERE user_id=? ORDER BY created_at DESC, rowid DESC LIMIT ?",
        (user_id, limit)).fetchall()
    out: list[dict] = []
    for r in rows:
        r = dict(r)
        built_at = r["built_at"] or r["created_at"]
        if forgot_at and forgot_at > built_at:
            until = r["created_at"]
            since = (_dt.datetime.fromisoformat(until)
                     - _dt.timedelta(days=7)).isoformat()
            lines = _digest(user_id, since, until) + _watching_lines(
                user_id, since, pdi, until, live=False)
            if not lines:
                conn.execute("DELETE FROM letters WHERE id=?", (r["id"],))
                conn.commit()
                continue
            made = _write_body(user_id, lines, cloud=cloud)
            stamp = db.utcnow()
            conn.execute(
                "UPDATE letters SET body=?, described_by=?, digest=?,"
                " left_host=?, redactions=?, built_at=? WHERE id=?",
                (made["body"], made["described_by"], made["digest"],
                 int(made["left_host"]), made["redactions"], stamp,
                 r["id"]))
            conn.commit()
            r.update(made, built_at=stamp)
            r["left_host"] = int(made["left_host"])
        out.append({"id": r["id"], "week_start": r["week_start"],
                    "body": r["body"], "described_by": r["described_by"],
                    "left_host": bool(r["left_host"]),
                    "redactions": r["redactions"],
                    "created_at": r["created_at"]})
    return out
