"""Which specialist covers what somebody brought to the coach.

## The finding

A QRME specialist could be reached from exactly one place in this product:
``guardian._deliver`` — the **monitoring** path. Sensors trip, a `Detection`
names a condition, and if a tandem specialist is registered for that condition
the Guardian delegates the guidance.

``coach.reply`` — the surface where a person actually brings something, in
their own words, because they chose to — contained no occurrence of the word
*specialist*. Not a call, not a mention, not a comment.

    asked     can a specialist be reached
    mattered  can the person who asks reach one

The person who asks was on the weaker path than the person whose watch noticed
something. That is backwards on a product whose whole premise is that somebody
is looking after you: bringing a problem yourself is the strongest signal there
is, and it was the one signal that could not summon the better answer.

## Why nothing bridged them

Two vocabularies that never met. ``specialists`` is keyed on **condition** —
the clinical detection domains in `conditions.py` — because the only caller was
a detection. ``coach.AREAS`` is seven **life areas**, because the only caller
was a person choosing a tab. There was no map, so even a coach that wanted a
specialist could not have named one.

`AREA_CONDITIONS` below is that map, and it is **declared rather than
inferred**. A rule like "match on substring" would have quietly paired
*finance* with *financial stress* and left *nutrition* with nothing while
looking like it had worked. Areas with no specialist domain say so by holding
an empty tuple, and `test_every_area_is_accounted_for` refuses a new area that
nobody has decided about.

## Why this offers rather than routes

`handoff.py` already set the rule for the other multi-step path, and it applies
here for a stronger reason:

    A detection can *warrant* a handoff; a person or an operator starts it.

The material is different in kind. A detection sends a *finding* — "the user
shows signs of low mood (resting heart rate elevated for 40 minutes)". A coach
turn would send **the person's own words about their own life**. Routing that
across the tandem automatically would disclose to a third-party profile
something the person said to their Guardian, without ever asking them.

So `for_area` answers *who is available*, the coach puts that in its reply, and
sending happens only from a route the person chose. `docs/tandem.md` governs
what may cross; consent is the thing that decides, not convenience.

Never on the emergency path, for the reason `handoff.py` gives: escalation
decides in one call and must keep doing so.
"""

from __future__ import annotations

from . import conditions, db

#: Life area -> the condition domains a specialist for that area would be
#: registered under. Declared, not matched: see the docstring.
#:
#: An empty tuple is a decision, not an omission — it says this product has no
#: clinical domain that corresponds to the area, so the coach answers it alone
#: and should not imply otherwise.
AREA_CONDITIONS: dict[str, tuple[str, ...]] = {
    # The front door's area (the Talk screen sends everything as
    # "general"): no clinical domain corresponds to a person who has not
    # yet said what is on their mind, so the Guardian answers it alone.
    "general": (),
    "mental_health": (conditions.ANXIETY, conditions.DEPRESSION,
                      conditions.STRESS, conditions.PHOBIA),
    "health_fitness": (conditions.PHYSICAL_DISTRESS, conditions.ERGONOMIC),
    # Nutrition has no detection domain. The coach's own description says it is
    # "never a diet prescription", and inventing a clinical specialist for it
    # would be the product overclaiming in the one area where overclaiming
    # looks most like advice.
    "nutrition": (),
    "career": (conditions.FRUSTRATION,),
    "finance": (conditions.FINANCIAL_STRESS,),
    "relationships": (conditions.RELATIONSHIP,),
    # Personal growth is the catch-all tab. Nothing clinical maps to it, and a
    # specialist reached from "becoming your best self" would be reached from
    # everything.
    "personal_growth": (),
}


def for_area(area: str) -> dict | None:
    """The tandem specialist covering this life area, or None.

    None has three distinct causes and the caller does not need to tell them
    apart: the area maps to no condition, no specialist is registered for the
    ones it maps to, or the registered specialist is local rather than tandem.
    In all three the coach answers alone, which is the standing behaviour.
    """
    domains = AREA_CONDITIONS.get(area, ())
    if not domains:
        return None
    placeholders = ",".join("?" for _ in domains)
    row = db.connect().execute(
        f"SELECT * FROM specialists WHERE condition IN ({placeholders})"
        " AND mode='tandem' AND qrme_profile_id IS NOT NULL"
        " ORDER BY condition LIMIT 1", domains).fetchone()
    if row is None:
        return None
    return {
        "condition": row["condition"],
        "label": row["label"] or conditions.LABELS.get(row["condition"],
                                                       row["condition"]),
        "qrme_profile_id": row["qrme_profile_id"],
    }


def offer(area: str) -> dict | None:
    """What the coach puts in its reply so a person can choose.

    An offer, not a disclosure: it names who is available and says plainly that
    nothing has been sent. The sentence matters as much as the field — a
    surface that lists a third party without saying whether it has already been
    spoken to has answered the wrong question for the reader.
    """
    spec = for_area(area)
    if spec is None:
        return None
    return {
        "available": True,
        "label": spec["label"],
        "qrme_profile_id": spec["qrme_profile_id"],
        "sent": False,
        "note": ("a specialist covers this area. Nothing has been sent — "
                 "asking them shares the message you just wrote with a "
                 "profile outside JIM, and only happens if you say so."),
    }
