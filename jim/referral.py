"""Finding a real clinician, and getting the user to a sign-off.

The tandem already lets a QRME specialist answer for a condition, and
``jim/handoff.py`` lets one take on multi-step work. Neither reaches a human
being. This does: it matches a real clinician by expertise and locality, then
asks QRME to assemble the summary and raise the signature that would release
it.

**JIM never holds the credential and never performs the ceremony.** The
signature is a WebAuthn assertion against *QRME's* relying party, over a
challenge QRME minted — so the Face ID prompt belongs to QRME and the
assertion travels from the user's device to QRME directly. JIM's part ends at
handing the user the challenge. A guardian product that could mint the consent
for releasing its own user's health record would be exactly the wrong shape,
and routing the assertion through here would put JIM in the middle of the one
exchange that exists to prove the user was present.

**Locality is coarse and self-declared.** ``sources`` already carries a
consented ``location`` feed, and it is deliberately not what this reads: live
position is a stream, and matching a clinic needs a town. A user typing
"Leeds" once is a smaller disclosure than a product inferring it continuously,
and it is the only thing the match can use anyway.

The area a condition maps to is coarse on purpose too. Sending an anxiety
referral to `mental_health` and a cardiac one to `medical` is the whole of the
routing; anything finer would be JIM guessing at a clinical taxonomy it has no
standing to define.
"""

from __future__ import annotations

from . import capture, db


class ReferralError(ValueError):
    """A referral that cannot be acted on. Text meant for a person."""

# Which QRME provider area a condition should look in. Everything not named
# here falls to `medical`, which is the safer default: a physical complaint
# routed to a therapist wastes an appointment, and the reverse can too, but
# `medical` is where an undifferentiated symptom belongs.
AREAS = {
    "anxiety": "mental_health",
    "depression": "mental_health",
    "stress": "mental_health",
    "phobia": "mental_health",
    "relationship": "relationships",
    "financial_stress": "finance",
}
DEFAULT_AREA = "medical"


def area_for(condition: str) -> str:
    return AREAS.get(condition, DEFAULT_AREA)


# --------------------------------------------------------------------------- #
# locality — a town, not a position
# --------------------------------------------------------------------------- #

def set_locality(user_id: str, locality: str | None) -> dict:
    """Record (or clear) the town a referral should search near."""
    conn = db.connect()
    if not locality or not locality.strip():
        conn.execute("DELETE FROM user_locality WHERE user_id=?", (user_id,))
        conn.commit()
        return {"user_id": user_id, "locality": None}
    value = locality.strip()
    conn.execute(
        "INSERT INTO user_locality (user_id, locality, created_at)"
        " VALUES (?,?,?) ON CONFLICT(user_id) DO UPDATE SET"
        " locality=excluded.locality", (user_id, value, db.utcnow()))
    conn.commit()
    return {"user_id": user_id, "locality": value}


def locality(user_id: str) -> str | None:
    row = db.connect().execute(
        "SELECT locality FROM user_locality WHERE user_id=?",
        (user_id,)).fetchone()
    return row["locality"] if row else None


# --------------------------------------------------------------------------- #
# matching and preparing
# --------------------------------------------------------------------------- #

def clinicians(user_id: str, condition: str, qrme) -> dict:
    """Real clinicians for this condition, near this user if we know where.

    An unreachable QRME is an empty list with a reason, never an exception:
    the caller is often a screen somebody opened while unwell.
    """
    area = area_for(condition)
    where = locality(user_id)
    if qrme is None:
        return {"area": area, "locality": where, "clinicians": [],
                "reason": "no QRME endpoint configured"}
    found = qrme.match_clinicians(area, where)
    return {"area": area, "locality": where, "clinicians": found,
            "reason": None if found else
                      "no clinician registered for this area yet"}


def prepare(user_id: str, condition: str, provider_id: str, spec,
            qrme, capture_ids: list[str] | None = None) -> dict:
    """Ask QRME to assemble the summary and raise the signature for it.

    Returns the package so the user can read exactly what would go, and the
    challenge their device will sign — **against QRME**, not here.

    **Captures ride along as metadata, never as bytes.** `jim/capture.py` said
    from its first line that a photograph could "reach a real clinician
    through the referral flow that already exists", and for one release that
    sentence was true of nothing: `attach_to_referral` returned a decision no
    caller consumed, `mark_released` was never called by anything, and
    `prepare` had no idea captures existed. The README, the walkthrough and
    the pull request all repeated the claim. This is the join that makes it
    true, and `test_a_prepared_referral_carries_the_captures` is what keeps it
    from coming apart again.

    What travels is what a clinician needs to know a photograph exists and ask
    for it — kind, site, when, provenance. The bytes stay in the vault and
    come out through `content_for_care` for a person who opens them
    deliberately.
    """
    if qrme is None:
        return {"prepared": False, "reason": "no QRME endpoint configured"}
    if not spec or not spec.get("qrme_profile_id"):
        return {"prepared": False,
                "reason": "no tandem specialist for this condition"}

    link = db.connect().execute(
        "SELECT * FROM tandem_links WHERE user_id=?", (user_id,)).fetchone()
    if link is None or not link["qrme_interactor_token"]:
        return {"prepared": False,
                "reason": "no tandem link yet; talk to the specialist first"}

    out = qrme.prepare_referral(
        spec["qrme_profile_id"], link["qrme_interactor_id"],
        link["qrme_interactor_token"], provider_id)
    if out is None:
        return {"prepared": False,
                "reason": "the specialist could not prepare a referral"}

    # What the user chose to release, filtered by the capture module's own
    # rules — intimate sites never ride in on a match, they are named one at a
    # time or left out. Resolved through `attach_to_referral` rather than
    # re-implemented here, so there is one place that decision is made.
    released, withheld, capture_note = [], [], None
    if capture_ids:
        decision = capture.attach_to_referral(capture_ids, user_id)
        released = [capture.for_clinician(cid) for cid in decision["release"]]
        withheld = decision["explicit"]
        capture_note = decision["note"]

    conn = db.connect()
    request_id = db.new_id("rrq")
    now = db.utcnow()
    conn.execute(
        "INSERT INTO referral_requests (id, user_id, condition, provider_id,"
        " qrme_referral_id, created_at) VALUES (?,?,?,?,?,?)",
        (request_id, user_id, condition, provider_id,
         out.get("referral_id"), now))
    for cap in released:
        conn.execute(
            "INSERT OR IGNORE INTO referral_captures (referral_request_id,"
            " capture_id, created_at) VALUES (?,?,?)",
            (request_id, cap["id"], now))
    conn.commit()

    return {
        "prepared": True,
        "referral_request_id": request_id,
        # Metadata only. A capture's bytes never appear in a package a user
        # reads on screen, and never in one an agent could be handed.
        "captures": released,
        "captures_withheld": withheld,
        "captures_note": capture_note,
        "qrme_referral_id": out.get("referral_id"),
        "clinician": out.get("clinician"),
        "area": out.get("area"),
        # Exactly what would be released, for the user to read first.
        "package": out.get("package"),
        "display_text": out.get("display_text"),
        # The ceremony is QRME's. JIM hands this over and steps out.
        "sign": out.get("sign"),
        "sign_with": "qrme",
        "note": "nothing has been released; sign this on your device to "
                "release it, and the link the clinician gets opens once",
    }


def mark_released(user_id: str, request_id: str) -> dict:
    """Record that the QRME ceremony completed and the captures went.

    **The client reports this; JIM cannot observe it.** The signature is raised
    and verified against QRME's relying party, so the Guardian never sees the
    ceremony — it hands the challenge over and steps out (see `prepare`). This
    is the client coming back to say it succeeded, and it is worth being plain
    that a report is all it is.

    That is also why the capture field is `released_to_clinician` and not
    `seen_by_clinician`, which is what it used to be called. Released is not
    opened. JIM has no way to know whether anybody read the thing, and a field
    implying it did would be inventing a fact about somebody else's behaviour
    — on a record a clinician might later be asked about.
    """
    row = db.connect().execute(
        "SELECT * FROM referral_requests WHERE id=? AND user_id=?",
        (request_id, user_id)).fetchone()
    if row is None:
        raise ReferralError("no such referral request on this account")
    ids = [r["capture_id"] for r in db.connect().execute(
        "SELECT capture_id FROM referral_captures WHERE referral_request_id=?",
        (request_id,)).fetchall()]
    for cid in ids:
        capture.mark_released(cid)
    return {"referral_request_id": request_id, "released": ids,
            "note": "recorded as released. Whether the clinician has opened "
                    "it is not something this app can see."}


def captures_for(request_id: str) -> list[dict]:
    """The metadata a referral released. Never bytes."""
    rows = db.connect().execute(
        "SELECT capture_id FROM referral_captures WHERE referral_request_id=?"
        " ORDER BY created_at", (request_id,)).fetchall()
    return [capture.for_clinician(r["capture_id"]) for r in rows]


def requests_for(user_id: str) -> list[dict]:
    """Referrals this user has prepared through the Guardian."""
    return [{"id": r["id"], "condition": r["condition"],
             "provider_id": r["provider_id"],
             "qrme_referral_id": r["qrme_referral_id"],
             "created_at": r["created_at"]}
            for r in db.connect().execute(
                "SELECT * FROM referral_requests WHERE user_id=?"
                " ORDER BY created_at, rowid", (user_id,)).fetchall()]
