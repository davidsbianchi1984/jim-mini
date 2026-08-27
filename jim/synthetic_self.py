"""The one QRME profile that is the user, and what JIM may tell it.

Every other link between these products reaches *somebody else's* profile. A
tandem specialist belongs to a clinician; a coordination runs in the care-team
org; a delegated workflow has an owner who is not the JIM user. In all of it
the JIM user meets QRME as an **interactor** — `tandem_links` maps them to a
`usr_` id and a capability token — which is to say, as a stranger.

QRME has always had the other thing. `ProfileKind` is
`self | other_person | fictional | hybrid`, and a `self` profile speaks *as*
the person. JIM had no column, module or route that knew it existed.

    asked     does JIM reference synthetic profiles
    mattered  does JIM reference this person's own

`docs/tandem.md` carries the contract this file implements, byte-identical in
all three repositories. The short version, and the reasons:

* **An owner token, not an interactor token.** The point of a self-profile is
  that it is not a stranger to them.
* **`kind` must be `self`.** A `fictional` profile briefed with somebody's
  medication schedule is a different product with the same code, so the link
  is refused rather than trusted.
* **An enumerated allowlist, empty by default.** Nothing crosses until the
  person has seen the exact brief and answered — the gate the contribution
  preview and the problem-report notice already use. A switch defaulting to on
  is a decision made on somebody's behalf.
* **The brief is composed *from* the allowlist**, not filtered down to it. A
  category nobody has written a builder for cannot cross by a future route,
  because there is no code path that would carry it.
* **A standing, not a history.** The current value of each consented category,
  replaced on each brief. A self-profile briefed continuously would be a
  health record with a conversational interface, reachable by anyone the
  profile talks to.

## The one category made of the person's own words

`medication` carries the names in their cabinet, and those are free text by
design: `meds.py` refuses a medication with no name and invites their own
wording — *"the little white one, 10 mg"*. A name can also carry more than a
name; *"the pill for my HIV"* is a diagnosis typed into a field asking for a
drug. So consenting to this category is consenting to a self-profile that can
be asked about those strings by anyone it talks to, and `preview()` shows the
strings rather than a count of them, because that is the only form in which
the decision is real.

Journal entries, check-in notes and transcripts never cross, under any
consent, by any route. There is no builder for them, which is the enforcement.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from . import db

#: Every category that may cross, and nothing else can. Each name maps to a
#: builder below; `CATEGORIES` is derived from that mapping rather than
#: repeated, so a name here without a builder is impossible by construction.
#:
#: Adding one is a deliberate act with a guard attached — see
#: `test_the_synthetic_self_says_only_what_it_was_told_to`, which fails on any
#: category this file grows without the contract growing with it.
_BUILDERS: dict[str, str] = {
    "language": "The code they set. Product vocabulary.",
    "wellbeing": "settled | unsettled. Derived, never a reading.",
    "conditions": "JIM's own condition keys, never the person's words.",
    "medication": "The names in their cabinet, and adherence standing.",
    "continuity": "Whether a vigil is armed. Nothing about who holds it.",
}


def _link_row(user_id: str) -> dict | None:
    row = db.connect().execute(
        "SELECT * FROM self_links WHERE user_id=?", (user_id,)).fetchone()
    return dict(row) if row else None


def link(user_id: str, profile_id: str, owner_token: str, qrme) -> dict:
    """Bind a user to their own QRME `self` profile.

    Refuses anything QRME does not report as `kind == "self"`, and refuses to
    guess when QRME cannot be reached: a link that cannot be verified is a link
    that might be to a fictional profile, and this is the one place where
    finding out later is too late.
    """
    info = qrme.profile_info(profile_id) if qrme else None
    if info is None:
        raise SelfLinkError(
            404, "that profile could not be read — check the id, and that "
                 "JIM is configured with a QRME endpoint")
    if info.get("kind") != "self":
        raise SelfLinkError(
            409, "that profile is not the person's own. Only a profile QRME "
                 "reports as kind 'self' may be briefed by the Guardian.")
    conn = db.connect()
    conn.execute(
        "INSERT INTO self_links (user_id, qrme_profile_id, owner_token,"
        " consented, created_at) VALUES (?,?,?,'[]',?)"
        " ON CONFLICT(user_id) DO UPDATE SET"
        " qrme_profile_id=excluded.qrme_profile_id,"
        " owner_token=excluded.owner_token, consented='[]'",
        (user_id, profile_id, owner_token, db.utcnow()))
    conn.commit()
    return status(user_id)


def link_with_qrme_account(user_id: str, email: str, password: str,
                           profile_id: str | None, qrme) -> dict:
    """Link by signing in to QRME, rather than by pasting two secrets.

        asked     how do I get a token
        mattered  there was no answer, and the screen asked anyway

    `link` above wants a `prf_…` id and an owner token. Both are real, and
    neither is findable: the owner token is minted once, in QRME's create
    response, and handed to whichever client did the creating. A field report
    put it exactly — *I could try to go look for a PRF. How do I get a token?
    Shouldn't it be just like a password instead.* It should.

    So this asks for the credential a person actually has. JIM signs in to
    QRME with the email and password, lists what that account holds, and mints
    the owner token for the profile that is *them*.

    **The password is not stored and neither is the account token.** The
    password lives for the length of one HTTP call. The account token is
    broader than the owner token it mints — it reaches every profile on that
    account and the billing — so it is used here and dropped; what lands in
    `self_links` is the same owner token the paste-it flow stored, and nothing
    besides.

    **`profile_id` is how a second call answers the question the first asked.**
    One `self` profile is the ordinary case and links immediately. Several
    means the person has to choose, and the caller re-sends the password with
    the choice — no ticket, no half-session, nothing stored between the two
    calls. Re-sending costs the person nothing: the form still holds what they
    typed.
    """
    if qrme is None:
        raise SelfLinkError(
            502, "this deployment has no QRME endpoint configured, so there "
                 "is nothing to sign in to")
    from .qrme_client import QRMESignInError

    try:
        session = qrme.account_signin(email, password)
        account_id = session.get("account_id")
        account_token = session.get("account_token")
        if not account_id or not account_token:
            raise SelfLinkError(
                502, "QRME accepted the sign-in and did not return an "
                     "account token")
        held = qrme.account_profiles(account_id, account_token)
    except QRMESignInError as exc:
        raise SelfLinkError(exc.status, exc.message) from None

    # Only a `self` profile may be briefed, and `link` refuses anything else
    # anyway. Filtering here rather than relying on that means the person is
    # never offered a choice that would be rejected after they made it.
    mine = [p for p in held if p.get("kind") == "self"]
    if not mine:
        raise SelfLinkError(
            409, "that QRME account has no profile of the person themselves. "
                 "Make one in QRME first — only a profile QRME reports as "
                 "kind 'self' may be briefed by the Guardian.")

    if profile_id is None and len(mine) > 1:
        # Not a refusal: the caller asked what there was, and this is the
        # answer. `linked` says plainly that nothing has happened yet.
        return {"linked": False,
                "choose": [{"profile_id": p.get("profile_id"),
                            "shown_as": p.get("shown_as"),
                            "kind": p.get("kind")} for p in mine]}

    chosen = profile_id or mine[0].get("profile_id")
    if chosen not in {p.get("profile_id") for p in mine}:
        # Same answer whether the id belongs to another account or was
        # invented — this must not become a way to ask which ids are real.
        raise SelfLinkError(404, "that profile is not on this QRME account")

    try:
        owner_token = qrme.mint_owner_token(account_id, chosen, account_token)
    except QRMESignInError as exc:
        raise SelfLinkError(exc.status, exc.message) from None

    # Through `link` rather than around it: the kind check, the refusal when
    # QRME cannot be read, and the consent reset all live there, and a second
    # path into `self_links` is how those three drift apart.
    return link(user_id, chosen, owner_token, qrme)


def unlink(user_id: str) -> dict:
    """Drop the link, the credential and the consent in one statement.

    Not three, and not a flag: a revoked link that keeps the owner token is a
    credential nobody is watching any more.
    """
    conn = db.connect()
    dropped = conn.execute("DELETE FROM self_links WHERE user_id=?",
                           (user_id,)).rowcount
    conn.commit()
    return {"linked": False, "was_linked": bool(dropped)}


def consent(user_id: str, categories: list[str]) -> dict:
    """Replace the consented set. Unknown names are refused, not dropped.

    Dropping them silently would let a client ask for something this file does
    not carry and be told yes.
    """
    row = _link_row(user_id)
    if row is None:
        raise SelfLinkError(404, "no self profile is linked")
    unknown = sorted(set(categories) - set(_BUILDERS))
    if unknown:
        raise SelfLinkError(
            422, f"not something the Guardian can share: {', '.join(unknown)}")
    conn = db.connect()
    conn.execute("UPDATE self_links SET consented=? WHERE user_id=?",
                 (json.dumps(sorted(set(categories))), user_id))
    conn.commit()
    return status(user_id)


def status(user_id: str) -> dict:
    row = _link_row(user_id)
    if row is None:
        return {"linked": False, "categories": _BUILDERS, "consented": []}
    return {"linked": True, "profile_id": row["qrme_profile_id"],
            "consented": json.loads(row["consented"]),
            "categories": _BUILDERS, "created_at": row["created_at"]}


# --- the builders ----------------------------------------------------------
#
# One per category. Each returns a value or None, and none of them takes a
# string from a caller: the signature is the safeguard, the way
# `Problems.record` takes a method and a path and has no parameter a message
# could arrive through.

def _language(user_id: str):
    from . import i18n
    return i18n.get_language(user_id)


def _wellbeing(user_id: str):
    """settled | unsettled, from whether anything severe happened this week.

    A grade, not a reading. The numbers stay here.
    """
    since = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    row = db.connect().execute(
        "SELECT COUNT(*) AS n FROM events WHERE user_id=? AND created_at>=?"
        " AND severity IN ('high','critical')", (user_id, since)).fetchone()
    return "unsettled" if row["n"] else "settled"


def _conditions(user_id: str):
    """The condition keys seen this month — `cardiac_event`, `anxiety`.

    JIM's own vocabulary from `conditions.py`, which is the product's word for
    a domain and never the person's word for their life.
    """
    since = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    rows = db.connect().execute(
        "SELECT DISTINCT condition FROM events WHERE user_id=? AND"
        " created_at>=? AND condition IS NOT NULL", (user_id, since)).fetchall()
    from . import conditions as vocab
    return sorted(r["condition"] for r in rows if r["condition"] in vocab.LABELS)


def _medication(user_id: str):
    """The cabinet's names, and how the week went.

    The one builder that carries the person's own words. See this module's
    docstring, and `docs/tandem.md`: a medication name is free text by design,
    and can be a diagnosis in disguise.
    """
    from . import meds
    report = meds.adherence(user_id, days=7)
    rows = report.get("adherence_rows") or []
    if not rows:
        return None
    rated = [r["rate"] for r in rows if r.get("rate") is not None]
    standing = "on_schedule"
    if rated and min(rated) < 0.8:
        standing = "behind"
    return {"names": sorted(r["name"] for r in rows), "standing": standing}


def _continuity(user_id: str):
    from . import vigil
    return "armed" if vigil.status(user_id).get("armed") else "off"


_BUILD = {"language": _language, "wellbeing": _wellbeing,
          "conditions": _conditions, "medication": _medication,
          "continuity": _continuity}


def preview(user_id: str) -> dict:
    """Exactly what would be sent, built by the code that sends it.

    Not a description of the brief and not a summary of it — the brief. A
    preview composed separately is a preview free to disagree with the payload,
    which is the shape of every "we only share anonymous data" claim that
    turned out to be false.
    """
    row = _link_row(user_id)
    if row is None:
        return {"linked": False, "brief": None}
    consented = json.loads(row["consented"])
    brief = {}
    for name in consented:
        value = _BUILD[name](user_id)
        if value is not None:
            brief[name] = value
    return {"linked": True, "profile_id": row["qrme_profile_id"],
            "consented": consented, "brief": brief,
            "empty": not brief}


def send(user_id: str, qrme) -> dict:
    """Post the brief to the self profile, as its owner.

    Refuses on an empty consent set rather than sending `{}`: a request that
    says nothing still tells QRME this person exists and uses JIM, and there is
    no reason to say that to anybody who has not asked for it.
    """
    shown = preview(user_id)
    if not shown["linked"]:
        raise SelfLinkError(404, "no self profile is linked")
    if shown["empty"]:
        raise SelfLinkError(
            409, "nothing has been consented, so there is nothing to send")
    row = _link_row(user_id)
    if qrme is None:
        raise SelfLinkError(
            503, "JIM is not configured with a QRME endpoint (JIM_QRME_URL)")
    answer = qrme.brief_self(row["qrme_profile_id"], row["owner_token"],
                             shown["brief"])
    return {"sent": bool(answer), "brief": shown["brief"],
            "profile_id": row["qrme_profile_id"]}


class SelfLinkError(Exception):
    """A refusal with the status the caller should see.

    Carries `status` and `message` the way the eight health-domain errors do,
    so `api.py` routes it through `i18n.refuse` with everything else and the
    sentence arrives in the reader's language.
    """

    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


#: Derived, never repeated. A name in `_BUILDERS` with no builder in `_BUILD`
#: would be a category the product offers and cannot compose.
CATEGORIES = tuple(sorted(_BUILDERS))
