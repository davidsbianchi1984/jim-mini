"""Anonymous by choice — FIG. 2 box 212, "choose name (anonymized)".

Spec [0031]: "The user may be asked to choose a user name at 212, which in
various examples may be **an anonymous user name**, the user's real name, or
left to the user to decide." And [0024]: the user "may … choose to make the
profile(s) anonymous or identifiable, and may elect to leave out certain
elements of their personal history."

QRME has had this since its first round (a listed profile can be anonymous,
with a silhouette and a generated name). JIM never did: enrollment took a
``display_name`` and that was your identity, which quietly excludes the person
the product most wants — somebody willing to tell a machine about their panic
attacks precisely because they are not ready to put their name on it.

So: ``anonymous: true`` at enrollment mints a **pseudonym** and JIM never
learns the real name. Everything the app shows, logs, or contributes uses the
pseudonym.

The one place where a name genuinely matters is an emergency, and the honest
answer there is not to secretly keep one. An anonymous user may optionally
give a ``legal_name`` that is used *only* in an emergency briefing, and if
they don't, the briefing says plainly that no legal name is on record instead
of relaying a pseudonym to a dispatcher as though it were an identity. That
tradeoff belongs to the user, stated up front (:func:`posture`), not to us.
"""

from __future__ import annotations

import secrets

from . import db

# Deliberately warm and obviously-not-a-real-name: a pseudonym should read as
# a pseudonym, so nobody mistakes it for the person's identity.
_ADJECTIVES = ("Quiet", "Steady", "Bright", "Kind", "Patient", "Gentle",
               "Careful", "Willing", "Honest", "Certain", "Open", "Calm")
_NOUNS = ("Heron", "Cedar", "River", "Lantern", "Harbor", "Sparrow", "Compass",
          "Meadow", "Anchor", "Beacon", "Willow", "Ridge")


def _candidate() -> str:
    return (f"{secrets.choice(_ADJECTIVES)} {secrets.choice(_NOUNS)} "
            f"{secrets.randbelow(9000) + 1000}")


def pseudonym() -> str:
    """A fresh pseudonym, checked against the ones already in use."""
    conn = db.connect()
    for _ in range(20):
        name = _candidate()
        taken = conn.execute(
            "SELECT 1 FROM users WHERE display_name=? LIMIT 1", (name,)
        ).fetchone()
        if taken is None:
            return name
    # 144 combinations × 9000 numbers makes this effectively unreachable, but
    # a colliding name is better than a failed enrollment for somebody in
    # distress, so widen rather than raise.
    return f"{_candidate()} {secrets.token_hex(2)}"


def resolve(body: dict) -> tuple[str, str | None, bool]:
    """(display_name, legal_name, anonymous) for an enrollment payload."""
    if not body.get("anonymous"):
        return body["display_name"], None, False
    # The typed display_name is discarded on purpose: an anonymous enrollment
    # that quietly kept the name it was given would be a lie in a field.
    return pseudonym(), (body.get("legal_name") or None), True


def briefing_name(user: dict | None) -> dict:
    """Who to tell a dispatcher this is.

    Never a pseudonym dressed up as an identity: an anonymous user with no
    legal name on record produces an explicit statement of that fact, which
    is what responders need to hear.
    """
    user = user or {}
    if not user.get("anonymous"):
        return {"name": user.get("display_name"), "anonymous": False}
    legal = user.get("legal_name")
    if legal:
        return {"name": legal, "anonymous": True,
                "note": "this person uses the app anonymously; the name given "
                        "here was provided by them for emergencies only"}
    return {"name": None, "anonymous": True,
            "known_as": user.get("display_name"),
            "note": "this person uses the app anonymously and left no legal "
                    "name on record — the app will not invent one; the "
                    "pseudonym in known_as is what they answer to"}


def posture(user: dict | None) -> dict:
    """What anonymity costs and does not cost, said out loud — for the
    settings screen, so the tradeoff is a choice and not a surprise."""
    user = user or {}
    anonymous = bool(user.get("anonymous"))
    return {
        "anonymous": anonymous,
        "known_as": user.get("display_name"),
        "legal_name_on_record": bool(user.get("legal_name")),
        "keeps": ["every emergency path — detection, guidance, escalation and "
                  "the emergency contact work identically",
                  "your own history, baselines and vault records"],
        "costs": ([] if user.get("legal_name") else
                  ["an emergency briefing cannot give responders a legal "
                   "name; add one for emergencies only if you want it to"]),
    }
