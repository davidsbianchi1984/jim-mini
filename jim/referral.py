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

from . import db

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
            qrme) -> dict:
    """Ask QRME to assemble the summary and raise the signature for it.

    Returns the package so the user can read exactly what would go, and the
    challenge their device will sign — **against QRME**, not here.
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

    conn = db.connect()
    conn.execute(
        "INSERT INTO referral_requests (id, user_id, condition, provider_id,"
        " qrme_referral_id, created_at) VALUES (?,?,?,?,?,?)",
        (db.new_id("rrq"), user_id, condition, provider_id,
         out.get("referral_id"), db.utcnow()))
    conn.commit()

    return {
        "prepared": True,
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


def requests_for(user_id: str) -> list[dict]:
    """Referrals this user has prepared through the Guardian."""
    return [{"id": r["id"], "condition": r["condition"],
             "provider_id": r["provider_id"],
             "qrme_referral_id": r["qrme_referral_id"],
             "created_at": r["created_at"]}
            for r in db.connect().execute(
                "SELECT * FROM referral_requests WHERE user_id=?"
                " ORDER BY created_at, rowid", (user_id,)).fetchall()]
