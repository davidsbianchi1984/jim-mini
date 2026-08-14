"""Membership: what a person has paid for, and what that entitles them to.

The same plans as QRME, drawn on a line that suits this product. **Free** is
the whole Guardian — conditions, guidance, the journal, habits and goals —
with the record stored in the clear. **Basic** ($20/month) is that same
Guardian with the record sealed in the PDI vault. **Pro** ($130/month) adds
the wrist, proactive monitoring, the specialist marketplace, and the synthetic
agents summoned through the QRME tandem.

**Free and Basic reach identical capabilities on purpose.** `includes("free")`
and `includes("basic")` are the same list, and a test asserts it. What $20
buys is `jim/storage.py`'s vault posture, not a feature — a free tier crippled
into uselessness teaches nobody anything about the product, and a free tier
that is honestly *not private* teaches somebody exactly what they are choosing
between.

**Nothing that answers an emergency is ever behind a paywall**, and that is
the rule this module exists to keep rather than a caveat on it.

JIM-mini is a guardian for people with known conditions. A lapsed card is a
billing event; a seizure is not. So :data:`NEVER_GATED` names the alarm path,
escalation, the medical ID a paramedic scans, incident history and the
guidance a person receives *during* an alarm — and a test asserts none of them
can be reached by any pattern in :data:`GATED`. The check is written against
the patterns rather than trusted to review, because the failure mode is silent:
a paywall in front of an alarm looks exactly like a paywall in front of
anything else until the day it matters, and on that day nobody is reading the
table.

The same logic sets the floor. `monitoring` being a Pro capability means a
Basic member does not get *predictive* early warning — the model watching for a
pattern before anything has happened. It does not and must not mean that
somebody in trouble cannot raise an alarm, be escalated, or have a responder
read their medical ID.

**Money here is simulated**, as everywhere in these three products: subscribing
writes a row and moves no real funds, and every response naming a price says
so.

**Enforcement is one table and one chokepoint** — see `qrme/tiers.py`, whose
shape this deliberately matches. A capability cannot be added and forgotten at
one of its routes, because no route opts in.
"""

from __future__ import annotations

from fastapi import HTTPException, Request

from . import db, storage

PLANS: dict[str, dict] = {
    "visitor": {
        "price_usd": 0,
        "period": None,
        "title": "Visitor",
        "means": "read a shared page or a scanned medical ID. No account "
                 "needed, and none is asked for.",
    },
    "free": {
        "price_usd": 0,
        "period": None,
        "title": "Free",
        "means": "the whole Guardian, with your record stored in the clear. "
                 "Same features as Basic; no vault, and nothing private.",
    },
    # Beta pricing: both paid plans are $0 while the beta runs. The tiers
    # keep their names and their gates — what a tester chooses is still
    # recorded and enforced — but nobody pays to test. The intended prices
    # ($20 Basic, $130 Pro) return when the beta ends, and each plan's own
    # copy says so, at the moment of choosing rather than in a footnote.
    "basic": {
        "price_usd": 0,
        "period": "month",
        "title": "Basic",
        "means": "the same Guardian as Free, with your record sealed in the "
                 "encrypted vault under a key you can hold yourself. Free "
                 "during the beta; $20/month when the beta ends.",
    },
    "pro": {
        "price_usd": 0,
        "period": "month",
        "title": "Pro",
        "means": "everything in Basic, plus the watch, proactive monitoring, "
                 "the specialist marketplace, and synthetic agents. Free "
                 "during the beta; $130/month when the beta ends.",
    },
}
ORDER = ("visitor", "free", "basic", "pro")

#: What an account that never chose gets. Pro while the beta runs, because
#: both paid plans cost nothing during it and somebody who did not choose
#: should be testing the whole product rather than the bottom of it. A plan
#: chosen deliberately is still honoured — this is only the answer when
#: nobody answered.
DEFAULT_PLAN = "pro"

#: While the beta runs, no capability gate refuses anybody, whatever plan
#: their account records.
#:
#: `DEFAULT_PLAN` alone would have reached only accounts created after it
#: changed. Everybody already testing is recorded as Free, from the days when
#: that was the default, and would have gone on meeting a paywall quoting a
#: price of $0 — the worst of both readings, since it withholds a feature and
#: cannot even say what withholding it is worth.
#:
#:     asked     does a new account start on the best plan
#:     mattered  can the people already testing use it
#:
#: So enforcement stands down without one stored membership being rewritten:
#: nobody's recorded choice is edited on their behalf, and the day this flips
#: back, the plan each person actually holds is the plan that applies.
#:
#: `entitles` is deliberately untouched. The pricing page must keep saying
#: what each tier means, because that is what it will cost — a beta that
#: quietly reports everything as included in Free would be advertising a
#: product that does not exist.
#:
#: Storage posture is a separate question and is deliberately not covered;
#: see `jim/storage.py`. Whether a record is sealed in the vault or kept in
#: the clear is about where bytes live rather than what somebody may press,
#: and flipping it under an account that has already written in the clear
#: would move nothing already written while implying that it had.
BETA_EVERYTHING_INCLUDED = True

CAPABILITIES: dict[str, dict] = {
    # `guardian` and `emergency` both start at **free**, and that is the whole
    # shape of the free tier: it reaches exactly what Basic reaches. Twenty
    # dollars buys the vault, not a feature — see `jim/storage.py`.
    "guardian": {
        "from": "free",
        "is": "the Guardian — conditions, guidance, journal, habits and goals",
    },
    "emergency": {
        # Free, and it would be visitor if a stranger could raise an alarm on
        # somebody else's behalf. Listed as a capability rather than left out
        # so that the pricing page states it: every plan that exists includes
        # the emergency path, and a reader should not have to infer that.
        "from": "free",
        "is": "alarms, escalation, the medical ID and incident history — "
              "never withheld for non-payment",
    },
    "watch": {
        "from": "pro",
        "is": "paired wearables, the watch face, and lending the Guardian "
              "your microphone",
    },
    "monitoring": {
        "from": "pro",
        "is": "early warning — the trend model that says something is about "
              "to go wrong before any threshold is crossed. Evaluating a "
              "sample you just submitted is not this, and is never withheld",
    },
    "marketplace": {
        "from": "pro",
        "is": "specialists and the connected-apps marketplace",
    },
    "synthetic_agents": {
        "from": "pro",
        "is": "summoning a QRME synthetic agent, and excursions",
    },
}

# Path pattern -> capability. Patterns rather than prefixes, because most of
# what is paid for here hangs off `/users/{id}/`.
GATED: tuple[tuple[str, str], ...] = (
    (r"^/devices(/|$)", "watch"),
    (r"^/users/[^/]+/mic(/|$)", "watch"),
    (r"^/guardians/[^/]+/watch(/|$)", "watch"),
    # The *predictive* surface, not the reactive one. `/monitor` is on the
    # never-gated list below; see the note there, which is the most important
    # paragraph in this file.
    (r"^/insights(/|$)", "monitoring"),
    (r"^/sensitivity(/|$)", "monitoring"),
    (r"^/specialists(/|$)", "marketplace"),
    (r"^/users/[^/]+/specialist-tasks(/|$)", "synthetic_agents"),
    (r"^/excursions(/|$)", "synthetic_agents"),
    # An engaged session (jim/engaged.py) is the same family as an excursion
    # or a specialist task: a model doing work on the account rather than
    # answering a question.
    #
    # Three exemptions, and they are the same shape as `/monitor` on the
    # never-gated list below — a paywall in the wrong place here does not
    # withhold a feature, it strands somebody inside one:
    #
    #   reach     how a person decides whether to open a session at all. A
    #             list of what a feature would be allowed to touch is not
    #             the feature.
    #   sign-off  a plan that lapses mid-session must not leave the session
    #             open forever, undeposited, with the handover never made.
    #             The exit is not the product.
    #   undo      taking back what the agent already did. Charging for the
    #             way out of a change somebody did not want is the one
    #             version of this that could not be defended.
    (r"^/engaged/(?!reach$)(?![^/]+/(sign-off|acts/[^/]+/undo)$)",
     "synthetic_agents"),
)

# Where reading is gated too, because the read *is* the feature.
#
# `/insights` is the one. Everywhere else in these three products a GET stays
# open so somebody can see what they would be buying — but an insight is not a
# shop window, it *is* the predictive product, and handing it over on a GET
# would be giving the feature away at the only door it has.
READ_ALSO_GATED: tuple[str, ...] = (r"^/insights(/|$)",)

OPEN: tuple[tuple[str, str], ...] = (
    # Operator setup, not a member purchase — this stocks the deployment's
    # specialist catalogue, which a subscription is later spent *in*.
    ("POST", "/specialists/seed"),
    ("POST", "/specialists/seed/tandem"),
)

# The paths no plan may ever stand in front of.
#
# Asserted against GATED by test rather than trusted to review. The failure
# mode is silent: a paywall in front of an alarm looks like any other paywall
# until the day it matters, and on that day nobody is reading this file.
NEVER_GATED: tuple[str, ...] = (
    # `/monitor` is here, and it is the entry this list was almost written
    # without. The first draft of GATED had it as the "proactive monitoring"
    # capability, which reads correctly and is wrong: `/monitor` is not the
    # predictive feature, it is the *ingest*. A sample arrives here,
    # `jim.conditions` asks "is something wrong right now", and a critical
    # reading escalates to the emergency contact.
    #
    # Gating it meant a Basic member submitting a blood oxygen of 84 received
    # a 402 instead of an escalation — the paywall standing between somebody
    # and an emergency, indirectly but completely. The suite caught it in
    # `test_critical_escalates_to_emergency_contact`, which is the only reason
    # this comment exists rather than the bug.
    #
    # What Pro buys is `jim.earlywarning`: the trend model that says something
    # is *about to* go wrong before any threshold is crossed. That is a real
    # feature and a fair thing to charge for. Evaluating a sample somebody
    # just submitted is not.
    r"^/monitor(/|$)",
    r"^/emergency(/|$)",
    r"^/users/[^/]+/alarms(/|$)",
    r"^/alarms/[^/]+/guidance(/|$)",
    r"^/c/[^/]+/alarm(/|$)",
    r"^/escalation-policy(/|$)",
    r"^/medical-id(/|$)",
    r"^/users/[^/]+/incidents(/|$)",
    r"^/waivers(/|$)",
)

# Concrete paths standing for each never-gated pattern, so the test can check
# what the gate *does* rather than only comparing two regexes to each other.
NEVER_GATED_SAMPLES: tuple[str, ...] = (
    "/monitor/usr_1",
    "/emergency/usr_1",
    "/users/usr_1/alarms",
    "/users/usr_1/alarms/alm_1/escalate",
    "/alarms/alm_1/guidance",
    "/c/bcn_1/alarm",
    "/escalation-policy/usr_1",
    "/medical-id/qr/usr_1",
    "/medical-id/tok_1",
    "/users/usr_1/incidents",
    "/waivers/usr_1",
)

WRITE_METHODS = ("POST", "PUT", "PATCH", "DELETE")


class TierError(ValueError):
    """A capability this person's plan does not include."""


def _rank(plan: str) -> int:
    return ORDER.index(plan) if plan in ORDER else 0


def plan_of(account_id: str) -> str:
    row = db.connect().execute(
        "SELECT plan FROM memberships WHERE account_id=? AND ended_at IS NULL",
        (account_id,)).fetchone()
    return row["plan"] if row else "visitor"


def governing_plan(user_id: str) -> str:
    """Whose plan decides what may be stored for this user.

    Their own, unless they are a child with no membership of their own — in
    which case it is the guardian's, because the guardian is the one who
    chose it. A child account has no card and no pricing page; resolving it to
    `plan_of(child)` would return "visitor", collapse the posture to the open
    cloud, and refuse a parent on Basic the ability to photograph their own
    child's rash. That is exactly backwards: the guardian paid for the vault
    precisely so the child's record would be in it.

    The mirror of :func:`account_of`, which resolves a *request* to the adult
    who pays rather than to the child being acted for.
    """
    plan = plan_of(user_id)
    if plan != "visitor":
        return plan
    row = db.connect().execute(
        "SELECT guardian_id FROM guardian_links WHERE child_id=?"
        " ORDER BY created_at", (user_id,)).fetchone()
    if row is None:
        return plan
    return plan_of(row["guardian_id"])


def is_dependant(user_id: str) -> bool:
    """Whether this account is a minor linked to a guardian."""
    return db.connect().execute(
        "SELECT 1 FROM guardian_links WHERE child_id=?",
        (user_id,)).fetchone() is not None


def guard_dependant_write(user_id: str) -> None:
    """Refuse an everyday write to a linked minor's record on an open store.

    The enrolment refusal in `family.enroll_child` is not enough on its own,
    because a guardian can enrol on Basic and move to Free the next day. That
    is a real path, not a hypothetical: it is one API call, and without this
    the rule would hold only for people who never changed their mind.

    What it covers is the child's *diary* — journal entries, check-in notes,
    context events. What it deliberately does not cover is
    `guardian._event`: biometrics, detections and escalations are the
    emergency path, and refusing to write one is a paywall in front of an
    alarm however it is dressed up. See the note in `jim/storage.py`; that
    argument is the reason `NEVER_GATED` exists and this module does not get
    to reintroduce the bug one layer down.

    A guardian is never trapped into paying. They can move to Free whenever
    they like — the vault keeps everything already in it (see
    :func:`storage.downgrade_effect`), and what stops is new everyday writing
    to a child's record, not their access to it and not their ability to call
    for help.
    """
    if not is_dependant(user_id):
        return
    storage.require(governing_plan(user_id), "dependant_record")


def entitles(plan: str, capability: str) -> bool:
    if capability not in CAPABILITIES:
        raise TierError(f"unknown capability {capability!r}")
    return _rank(plan) >= _rank(CAPABILITIES[capability]["from"])


def includes(plan: str) -> list[str]:
    return [c for c in CAPABILITIES if entitles(plan, c)]


def may(account_id: str, capability: str) -> bool:
    return entitles(plan_of(account_id), capability)


def refusal(plan: str, capability: str):
    """Why this was refused, what would fix it, and that the alarm still works.

    `tests/refusals_untranslated.txt` named this as the one sentence it would
    not half-do: an f-string whose slots are a capability description and a
    billing period, both English prose, so translating the frame alone would
    have produced a sentence half in each language at the one moment in this
    product that stands between somebody and a decision to pay.

        asked     can the frame be translated
        mattered  can the slots be

    Both are `i18n.Term` now — a closed set this product authors, so each has a
    translation and none of it is guessed. An unmapped one keeps the whole
    sentence English rather than mixing.

    The emergency clause is part of the frame rather than appended to it. A
    person meeting this refusal needs to know the alarm still works, and that
    reassurance arriving in English at the end of a Portuguese sentence is
    exactly the shape this mechanism exists to prevent.

    The plan titles stay untranslated: `Basic` and `Pro` are what the product
    is called on the pricing page and on a receipt.
    """
    from . import i18n
    need = CAPABILITIES[capability]["from"]
    spec = PLANS[need]
    return i18n.fill(
        i18n.PLAN_GATE,
        capability=i18n.Opening(CAPABILITIES[capability]["is"]),
        needs=spec["title"], price=spec["price_usd"],
        period=i18n.Term(spec["period"]), have=PLANS[plan]["title"])


def enforcing() -> bool:
    """Whether a capability gate may refuse anybody right now.

    Both enforcement points ask this rather than each testing the flag
    themselves, and the reason is the mistake that produced this function:
    the beta stand-down went into `require` first, every tier test still
    passed, and nothing changed for the person who reported the problem —
    because `gate`, the application-wide chokepoint and the only one a
    person actually meets, had been calling `entitles` on its own all along.

        asked     is the gate stood down
        mattered  is the gate a person meets stood down

    Two places deciding the same thing is how one of them gets missed. This
    is that decision, once.
    """
    return not BETA_EVERYTHING_INCLUDED


def require(account_id: str, capability: str) -> None:
    if not enforcing():
        return
    plan = plan_of(account_id)
    if not entitles(plan, capability):
        raise TierError(refusal(plan, capability))


def is_never_gated(path: str) -> bool:
    """Whether this path is on the list no plan may stand in front of."""
    import re

    return any(re.search(p, path) for p in NEVER_GATED)


def capability_for(method: str, path: str) -> str | None:
    """The capability a request needs, or None.

    The safety list is checked **first**, so a pattern added to `GATED` that
    happens to cover an emergency path cannot gate it. Belt as well as braces:
    the test asserts the two lists do not overlap, and this makes the overlap
    harmless if one is ever added.
    """
    import re

    if is_never_gated(path):
        return None
    if (method.upper(), path) in OPEN:
        return None
    for pattern, capability in GATED:
        if re.search(pattern, path):
            if method.upper() in WRITE_METHODS or pattern in READ_ALSO_GATED:
                return capability
            return None
    return None


def account_of(request: Request) -> str | None:
    """Whose membership governs this request.

    A user token's subject is the user id, and here that *is* the account —
    unlike QRME, where an owner token's subject is a profile and the account
    sits behind it. A guardian acting for a child is deliberately not resolved
    to the child's membership: the adult who pays is the one whose plan
    applies, and billing a child's account for their parent's action would be
    the wrong answer in both directions.
    """
    from . import auth

    who = auth.principal(request)
    if who is None or who.get("role") != "user":
        return None
    return who["subject_id"]


def gate(request: Request) -> None:
    """The chokepoint. Installed once, application-wide."""
    if not enforcing():
        return
    capability = capability_for(request.method, request.url.path)
    if capability is None:
        return
    account = account_of(request)
    if account is None:
        return                # authorization is the route's own business
    plan = plan_of(account)
    if not entitles(plan, capability):
        raise HTTPException(402, {
            "reason": "plan",
            "capability": capability,
            "needs": CAPABILITIES[capability]["from"],
            "have": plan,
            "price_usd": PLANS[CAPABILITIES[capability]["from"]]["price_usd"],
            "period": PLANS[CAPABILITIES[capability]["from"]]["period"],
            "message": refusal(plan, capability),
            "billing": "simulated — no real funds move",
            "emergency_unaffected": True,
        })


def subscribe(account_id: str, plan: str) -> dict:
    if plan not in PLANS or plan == "visitor":
        raise TierError(
            f"unknown plan {plan!r}; one of "
            f"{', '.join(p for p in PLANS if p != 'visitor')}")
    conn = db.connect()
    now = db.utcnow()
    conn.execute(
        "UPDATE memberships SET ended_at=? WHERE account_id=? AND"
        " ended_at IS NULL", (now, account_id))
    conn.execute(
        "INSERT INTO memberships (id, account_id, plan, started_at)"
        " VALUES (?,?,?,?)",
        (db.new_id("mem"), account_id, plan, now))
    conn.commit()
    return membership(account_id)


def cancel(account_id: str) -> dict:
    """End it. The person keeps their record, their conditions and every
    emergency path — a lapsed subscription must not quietly remove somebody's
    ability to call for help."""
    conn = db.connect()
    conn.execute(
        "UPDATE memberships SET ended_at=? WHERE account_id=? AND"
        " ended_at IS NULL", (db.utcnow(), account_id))
    conn.commit()
    return membership(account_id)


def membership(account_id: str) -> dict:
    plan = plan_of(account_id)
    spec = PLANS[plan]
    return {
        "account_id": account_id,
        "plan": plan,
        "title": spec["title"],
        "price_usd": spec["price_usd"],
        "period": spec["period"],
        "includes": includes(plan),
        "locked": [c for c in CAPABILITIES if not entitles(plan, c)],
        # A field, not a footnote. See `jim/storage.py`: a privacy claim that
        # lives in a Terms of Service and not in the response body is a claim
        # nobody reads at the moment it matters.
        "storage": storage.describe(plan),
        "billing": "simulated — no real funds move; the subscription is a row",
        "emergency": "never withheld for non-payment, on any plan",
    }


def catalogue() -> dict:
    return {
        "plans": [
            {"plan": p, **PLANS[p], "includes": includes(p),
             "locked": [c for c in CAPABILITIES if not entitles(p, c)],
             "storage": storage.describe(p)}
            for p in ORDER],
        "capabilities": CAPABILITIES,
        "never_gated": list(NEVER_GATED_SAMPLES),
        "storage": storage.vocabulary(),
        "the_difference": "Free and Basic run the same app. The difference is "
                          "where your data lives.",
        "billing": "simulated — no real funds move; the subscription is a row",
        "emergency": "never withheld for non-payment, on any plan",
    }
