"""Meal logging: point the camera at the plate, say a few words, done.

The field research was unambiguous — people abandon calorie trackers over
tap-count, and what they ask for is photo logging. The honest offline shape
of that: the **photo is the receipt**, sealed like any capture (metadata
stripped, vaulted when a vault stands, never folded into anything
automatic); the **note is the log**, kept local the way a check-in is, so
the on-device coach's nutrition area can read it with the network cut. When
the online model is available it tidies the note into a coarse structured
log — items and rough portions, never invented precision; the providers are
text-only, so nothing here ever pretends to have seen the pixels.
"""

from __future__ import annotations

import base64

from . import capture, db, life, llm


class MealError(Exception):
    pass


_TIDY_SYSTEM = (
    "You turn a person's short meal note into a coarse food log. List the "
    "items they named and, only where the note itself implies it, a rough "
    "portion. Never invent foods, quantities, or calorie counts the note "
    "does not support — a coarse honest log beats a precise guess. Answer "
    "with the log line only.")


def log(user: dict, note: str | None, photo_b64: str | None,
        pdi=None, cloud=None) -> dict:
    """One meal: seal the photo if given, keep the note as the log, and let
    the online model tidy it when one is standing."""
    user_id = user["id"]
    if not (note or "").strip() and not photo_b64:
        raise MealError("a meal needs a note or a photo — there is nothing "
                        "to log in an empty plate")

    capture_id = None
    if photo_b64:
        # The same sealing walk a clinical photo takes — metadata stripped,
        # vaulted, never handed to anything automatic — but not through the
        # capture door itself: its vocabulary is body sites, and a plate is
        # not one. A photo of somebody's meals is still a photo of their
        # life, so no vault means no photo, exactly as with captures.
        if pdi is None:
            raise capture.VaultRequired(
                "a meal photo needs the vault the clinical captures use — "
                "this deployment has none configured, so log the meal by "
                "note alone")
        try:
            raw = base64.b64decode(photo_b64, validate=True)
        except Exception:
            raise MealError("the photo could not be read — it is not "
                            "base64") from None
        cleaned, _ = capture.strip_metadata(raw)
        capture_id = db.new_id("cap")
        pdi.put(f"jim/{user_id}/meals/{capture_id}",
                base64.b64encode(cleaned).decode())

    logged = (note or "").strip()
    described_by = "note"
    if logged:
        result = llm.generate_for_user(user_id, _TIDY_SYSTEM, logged,
                                       cloud=cloud)
        tidied = (result.get("text") or "").strip()
        if tidied and result.get("provider") not in (None, "stub"):
            logged, described_by = tidied, "model"
    if not logged:
        # A photo with no words is still a meal that happened; the log says
        # exactly what is known, which is only that.
        logged, described_by = "meal photographed, not described", "photo"

    conn = db.connect()
    meal_id = db.new_id("mel")
    conn.execute(
        "INSERT INTO meals (id, user_id, note, logged, described_by,"
        " capture_id, created_at) VALUES (?,?,?,?,?,?,?)",
        (meal_id, user_id, (note or "").strip() or None, logged,
         described_by, capture_id, db.utcnow()))
    conn.commit()

    # The log line reaches the offline coach's nutrition area the way any
    # local context does — deliberately unvaulted, because a coach that
    # cannot read today's meals cannot say anything true about them. The
    # photo stays sealed regardless.
    life.add_context(user_id, "meals", "nutrition_log",
                     {"content": logged}, pdi=None)
    return {"id": meal_id, "logged": logged, "described_by": described_by,
            "photo_sealed": capture_id is not None,
            "capture_id": capture_id}


def board(user_id: str, limit: int = 30) -> list[dict]:
    """Recent meals, newest first — the log lines and whether a sealed
    receipt stands behind each."""
    rows = db.connect().execute(
        "SELECT id, note, logged, described_by, capture_id, created_at"
        " FROM meals WHERE user_id=? ORDER BY created_at DESC, rowid DESC"
        " LIMIT ?", (user_id, limit)).fetchall()
    return [{**dict(r), "photo_sealed": r["capture_id"] is not None}
            for r in rows]
