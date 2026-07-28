"""Where a plan's data lives, and what that honestly means.

The same two postures as `qrme/storage.py`, drawn on a product where the
payloads are medical. **open_cloud** is the free tier: JIM's own database, in
the clear, no vault at any point. **vault** is Basic and Pro: the sensitive
payloads go to PDI sealed, under a key the person can hold themselves, with a
tamper-evident chain over every access.

**Free and Basic reach the same capabilities.** Twenty dollars buys privacy,
not features — see `jim/tiers.py`, where `guardian` and `emergency` both start
at `free`. A free tier crippled into uselessness teaches nobody anything about
the product; a free tier that is honestly *not private* teaches somebody
exactly what they are choosing between.

**This is not a new behaviour, it is an admission of an old one.** JIM has
always degraded gracefully when no PDI was configured: `life.add_journal`,
`life.check_in` and `guardian._event` all read `if pdi is not None` and fall
back to writing the payload straight into the local table. A deployment
without a vault has been storing check-in notes and medical event details in
the clear the whole time and never said so on any screen. The free plan makes
that the documented posture with a disclosure attached, rather than an
undocumented fallback.

**What free will not hold.** :data:`SENSITIVE` is short, and the test for
membership is not "would the account holder mind" — it is *whose exposure is
it*:

* ``body_image`` — a photograph of somebody's body, taken at home, of the
  thing they are frightened about. `jim/capture.py` already refuses to write
  one without a vault; on the free plan it refuses for the same reason with a
  different remedy.
* ``dependant_record`` — a child's record on a guardian's account. The child
  did not pick the plan, cannot read the pricing page, and will be an adult
  with a searchable medical history somebody else put in the clear.

**And what is deliberately *not* on that list, which is the whole argument.**

Blood oxygen, seizure detections, alarm history, the medical ID a paramedic
scans. These are the most medically sensitive rows in the product and the free
plan stores every one of them in the clear.

Refusing them would mean refusing the emergency path, because they *are* the
emergency path: a sample arrives at `/monitor`, `jim.conditions` asks whether
something is wrong right now, and a critical reading escalates. A storage rule
that declined to write the sample is a paywall in front of an alarm wearing a
privacy argument as a disguise — exactly what `tiers.NEVER_GATED` exists to
prevent, and this module does not get to reintroduce it one layer down. That
list was itself written after a `/monitor` gate returned 402 to somebody
submitting a blood oxygen of 84.

So the free plan holds them, openly, and says so. Somebody in trouble gets an
escalation. That is the trade, it is made deliberately, and
`test_a_free_account_is_never_refused_an_emergency_write` is what keeps it.

**A downgrade never unseals anything**, and **an upgrade does not un-expose**
what was already open — the same two rules as QRME, in the same words, for the
same reason: a billing event that declassified a year of somebody's medical
history would be the worst thing this module could do.
"""

from __future__ import annotations

POSTURES: dict[str, dict] = {
    "open_cloud": {
        "private": False,
        "title": "Open cloud",
        "means": "your record sits in JIM's own database, in the clear",
        "who_can_read": ("you", "anyone you share with",
                         "the people who operate this deployment",
                         "anyone with lawful access to it"),
        "encrypted_at_rest": False,
        "audit_chain": False,
        "you_hold_a_key": False,
    },
    "vault": {
        "private": True,
        "title": "Encrypted vault",
        "means": "journal entries, check-in notes, detection detail and every "
                 "capture are sealed in PDI before they land, under a key you "
                 "can hold yourself",
        "who_can_read": ("you", "anyone you share with"),
        "encrypted_at_rest": True,
        "audit_chain": True,
        "you_hold_a_key": True,
    },
}

# Plan -> posture. The whole of what Basic buys.
BY_PLAN: dict[str, str] = {
    "visitor": "open_cloud",     # a visitor stores nothing; posture is moot
    "free": "open_cloud",
    "basic": "vault",
    "pro": "vault",
}

# What may never sit in the open store, and why — in the words the refusal
# returns.
#
# Both entries are payloads where the person harmed is not the person who
# chose the plan. Nothing is here because it *sounds* sensitive; see the
# module note on why the monitor samples, which are the most medically
# sensitive rows in the product, are deliberately absent.
#
# Only what *this* repository can actually refuse.
# `test_every_sensitive_kind_is_enforced_somewhere` holds that line, because a
# kind named here that nothing here refuses is a claim with no check behind
# it.
SENSITIVE: dict[str, str] = {
    "body_image": "a photograph of somebody's body — it is not going in a "
                  "database anyone who runs this deployment can open",
    "dependant_record": "a child's medical record on your account — they did "
                        "not pick this plan",
}

# Deliberately *not* here, and recorded because it is the argument this module
# turns on: **the monitor samples, alarms, detections and medical ID.**
#
# They are the most medically sensitive rows JIM holds. They are also the
# emergency path itself — a sample arrives, conditions evaluates it, a
# critical reading escalates to a named contact. A storage refusal in front of
# that is a paywall in front of an alarm, whatever the reasoning above it
# says, and `tiers.NEVER_GATED` exists because this codebase already shipped
# that bug once and caught it in a test rather than in the field.
#
# Free stores them in the clear, and the disclosure says so in those words.

FREE_DISCLOSURE = (
    "This account is on the free plan. Your record is stored in the clear — "
    "no vault, no encryption you hold the key to, and the people who run this "
    "deployment can read it. That includes your journal, your check-in notes "
    "and your health readings. Every alarm, escalation and emergency path "
    "works exactly the same, and so does everything else: the only difference "
    "from Basic is where your data lives."
)

# The one sentence that has to survive being skimmed.
EMERGENCY_NOTE = (
    "Emergency paths are never withheld and never refused for storage "
    "reasons, on any plan."
)


class StorageError(ValueError):
    """A payload that cannot be stored under this posture."""


def posture_of(plan: str) -> str:
    """The one place this question is answered."""
    return BY_PLAN.get(plan, "open_cloud")


def is_private(plan: str) -> bool:
    return POSTURES[posture_of(plan)]["private"]


def describe(plan: str) -> dict:
    """What this plan's storage actually is, for a surface to show.

    Returned as a field rather than left to a Terms of Service, because a
    privacy claim nobody reads at the moment it matters is not a claim.
    """
    posture = posture_of(plan)
    spec = POSTURES[posture]
    return {
        "plan": plan,
        "posture": posture,
        "private": spec["private"],
        "not_private": not spec["private"],
        "title": spec["title"],
        "means": spec["means"],
        "who_can_read": list(spec["who_can_read"]),
        "encrypted_at_rest": spec["encrypted_at_rest"],
        "audit_chain": spec["audit_chain"],
        "you_hold_a_key": spec["you_hold_a_key"],
        "disclosure": FREE_DISCLOSURE if not spec["private"] else None,
        "refused_here": sorted(SENSITIVE) if not spec["private"] else [],
        "emergency": EMERGENCY_NOTE,
    }


def may_store(plan: str, kind: str) -> bool:
    """Whether this payload may be stored under this plan's posture."""
    if is_private(plan):
        return True
    return kind not in SENSITIVE


def require(plan: str, kind: str) -> None:
    """Raise unless this payload may be stored. Text meant for a person."""
    if may_store(plan, kind):
        return
    raise StorageError(
        f"{SENSITIVE[kind]}. The free plan stores everything in the clear, "
        "and this is not ours to expose on somebody else's behalf. Basic "
        "seals it in the vault for $20 a month, and the vault itself is free "
        "to host — colocation costs nothing. " + EMERGENCY_NOTE
    )


def upgrade_effect(from_plan: str, to_plan: str) -> dict:
    """What moving up does, and — more importantly — what it does not.

    Sealing content afterwards protects it from here on. It changes nothing
    about the backups, logs and copies that already exist, and a product that
    implied otherwise would be selling absolution rather than encryption.
    """
    was_open = not is_private(from_plan)
    now_private = is_private(to_plan)
    return {
        "from": from_plan,
        "to": to_plan,
        "new_content_sealed": now_private,
        "existing_content_sealed": False,
        "note": (
            "anything written while you were on the free plan was written in "
            "the clear. It can be moved into the vault, and that protects it "
            "from now on — it does not un-expose it. Backups, logs and any "
            "copy taken in the meantime already exist."
            if was_open and now_private else
            "nothing changes about where your existing content lives"),
    }


def downgrade_effect(from_plan: str, to_plan: str) -> dict:
    """What moving down does. It does not unseal anything.

    A downgrade that quietly emptied the vault into the open store would be
    the worst thing this module could do — a billing event silently
    declassifying a year of somebody's medical history. So it does not
    happen, and this function exists to say so rather than to perform it.
    """
    was_private = is_private(from_plan)
    now_open = not is_private(to_plan)
    return {
        "from": from_plan,
        "to": to_plan,
        "existing_stays_sealed": True,
        "new_content_in_the_clear": now_open,
        "note": (
            "everything already in the vault stays in the vault, sealed and "
            "readable. Only what you write from now on goes to the open "
            "store. A lapsed subscription does not declassify your history."
            if was_private and now_open else
            "nothing changes about where your existing content lives"),
    }


def vocabulary() -> dict:
    """Both postures side by side, for a page somebody reads before choosing."""
    return {
        "postures": POSTURES,
        "by_plan": BY_PLAN,
        "sensitive": SENSITIVE,
        "free_disclosure": FREE_DISCLOSURE,
        "emergency": EMERGENCY_NOTE,
        "the_difference": "Free and Basic run the same app. The difference is "
                          "where your data lives.",
    }
