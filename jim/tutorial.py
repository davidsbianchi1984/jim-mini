"""The Guardian, walking you through JIM-mini.

QRME's walkthrough is deliberately faceless: on a platform whose subject is
synthetic people, a guide with a persona would be the most convincing one on
it. **Here the opposite is true**, and the difference is worth stating because
the two products share almost everything else.

JIM-mini has exactly one voice — the Guardian — and it is not pretending to be
anybody. It is the thing that watches your signals, notices a condition and
speaks up. A separate faceless guide would be a *second* voice in a product
built on there being one, and the first thing a new user learned would be that
JIM-mini talks to them from two places. So **the Guardian gives the tour**,
because being shown around by the thing that will be looking after you is the
introduction.

Everything else is the same shape as `qrme/tutorial.py`, for the same reasons:

* **It never taps anything for you.** No lesson triggers an escalation, sends
  to an emergency contact, or files a condition "to show you how". In a product
  whose actions reach a real person's phone at three in the morning, a
  demonstration that fires for real is not a demonstration.
* **It works with no model configured** — written prose, no provider.
* **Voice and text are one lesson rendered twice**, and voice matters more here
  than in QRME: this is a product used hands-free, by people who may be unwell.
* **It cannot fall behind the app**: each lesson names its screens and a test
  holds them against the gallery.
"""

from __future__ import annotations

from . import db

GUIDE = ("This is your Guardian — the same one that watches your signals and "
         "speaks up when something changes. It is showing you around because "
         "being introduced by the thing that will be looking after you is the "
         "introduction.")

LESSONS: tuple[dict, ...] = (
    dict(key="what", chapter="Getting started", title="What JIM-mini is",
         what="It watches the signals you allow it — from a watch, a band, a "
              "phone — notices when a condition you have told it about is "
              "starting, and says something before it becomes an emergency.",
         screens=(1, 2, 3, 4, 5), try_it="Open the home screen and read the "
                                         "signals it is using."),
    dict(key="signup", chapter="Getting started", title="Signing up",
         what="Your name, your birthdate, what the Guardian may see, who to "
              "ring if something is wrong — and then a plan. Basic is the "
              "Guardian itself and every emergency path; Pro adds the watch "
              "and the model that looks ahead. The plan step comes straight "
              "after the emergency contacts on purpose: you have just told us "
              "who to ring, so the next screen says plainly that no plan "
              "withholds that. Billing is simulated and no real funds move.",
         screens=(72, 73, 74, 75),
         try_it="Open Pick a Plan and read the third card."),
    dict(key="consent", chapter="Getting started", title="What it may see",
         what="Every source is one you turned on, and every one can be turned "
              "off in the same place. Nothing is read that you did not hand "
              "over.",
         screens=(6, 7, 8, 9, 10, 11, 12),
         try_it="Open your sources and switch one off."),
    dict(key="conditions", chapter="Being watched over",
         title="Conditions it knows",
         what="You tell it what to watch for — the ones you live with, in your "
              "own words. It matches signals against those, and nothing else.",
         screens=(13, 14, 15, 16, 17, 18, 19, 20),
         try_it="Add a condition and see which signals it will use."),
    dict(key="guidance", chapter="Being watched over", title="What it says",
         what="Guidance is written for the moment it fires — short, and it "
              "tells you what it saw. It never diagnoses and it says so.",
         screens=(21, 22, 23, 24, 25, 26, 27, 28),
         try_it="Read a piece of guidance and the reason under it."),
    dict(key="escalate", chapter="Being watched over",
         title="When it gets serious",
         what="On a critical event it reaches your emergency contact, and then "
              "live help. You choose who, and you can see every time it did.",
         screens=(29, 30, 31, 32, 33, 34, 35, 36),
         try_it="Set an emergency contact, and read the escalation log."),
    dict(key="life", chapter="The life layer", title="Check-ins and goals",
         what="Mood and energy, smart goals, habit streaks, and a coach across "
              "six life areas. The part that is not about emergencies.",
         screens=(37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48),
         try_it="Do one check-in and set one goal."),
    dict(key="people", chapter="The life layer", title="Family and helpers",
         what="The people who can see how you are doing, and exactly how much "
              "each one sees. A guardian's view is not the same as a friend's.",
         screens=(49, 50, 51, 52, 53, 54, 55, 56),
         try_it="Invite somebody and choose what they get."),
    dict(key="tandem", chapter="Beyond the app", title="The tandem",
         what="When configured, JIM-mini hands a question to a QRME specialist "
              "profile and brings the answer back — moderated, and marked as "
              "AI. Your vault stays yours.",
         screens=(57, 58, 59, 60), try_it="Open the tandem settings."),
    dict(key="referral", chapter="Beyond the app",
         title="Reaching a real clinician",
         what="A referral is signed for with your face or your fingerprint, "
              "not a checkbox — and the link opens once. The clinician writes "
              "back once, attributed to them by name.",
         screens=(61, 62, 63, 64), try_it="Read what a referral package "
                                          "contains before you sign one."),
    dict(key="mic", chapter="Beyond the app", title="The second microphone",
         what="While you are on a call your phone's microphone is busy, which "
              "is exactly when you might want to ask the Guardian something. "
              "This lends it the one on your watch — yours, near-field, and "
              "yours to take back.",
         screens=(65, 66), try_it="Lend it, then take it back."),
    dict(key="agents", chapter="Beyond the app", title="What is running",
         what="Green, amber, red: working, needs you, stopped. One question — "
              "does this need me right now — answered on the wrist and in the "
              "app.",
         screens=(67, 68), try_it="Open Agents and find the amber one."),
    dict(key="plans", chapter="Beyond the app", title="What it costs",
         what="Basic is $20 a month: the Guardian itself — your conditions, "
              "guidance, the journal, habits and goals — and every emergency "
              "path. Pro is $130 a month and adds the watch, early warning "
              "that looks ahead of a threshold, specialists and synthetic "
              "agents. Nothing on the alarm path is ever behind either price: "
              "a reading you submit is answered, an escalation still fires, "
              "and a responder can still read your medical ID, on any plan or "
              "none. Billing here is simulated and no real funds move.",
         screens=(69, 70),
         try_it="Open Choose a Plan and read what is never gated."),
    dict(key="dock", chapter="Beyond the app", title="The pane in the corner",
         what="A small pane in the bottom corner of the app carrying the "
              "glances a watch would — the last reading, what is running, "
              "whether channel 2 is lent — for the people who do not have a "
              "wrist, which on Basic is everyone. It shows and it points at "
              "the real screen; it never acts. And when an alarm is live it "
              "opens on the alarm whatever you had it set to.",
         screens=(71,),
         try_it="Tap the helper button and cycle the faces."),
)

CHAPTERS = tuple(dict.fromkeys(le["chapter"] for le in LESSONS))
MODES = ("text", "voice")


class TutorialError(ValueError):
    """A step that does not exist. Text meant for a person."""


def _index(key: str) -> int:
    for i, le in enumerate(LESSONS):
        if le["key"] == key:
            return i
    raise TutorialError(f"no such step {key!r}")


def say(lesson: dict, mode: str = "text") -> dict:
    """One lesson, for reading or for listening.

    Voice matters more here than in QRME: this is a product used hands-free,
    often by somebody who is not well, and a spoken screen number is noise.
    """
    if mode not in MODES:
        raise TutorialError(f"unknown mode {mode!r} — one of {', '.join(MODES)}")
    out = {"key": lesson["key"], "chapter": lesson["chapter"],
           "title": lesson["title"], "try_it": lesson["try_it"], "mode": mode}
    if mode == "voice":
        out["speak"] = f"{lesson['title']}. {lesson['what']} {lesson['try_it']}"
        out["screens"] = []
    else:
        out["what"] = lesson["what"]
        out["screens"] = list(lesson["screens"])
    return out


def outline(mode: str = "text") -> dict:
    return {
        "guide": GUIDE,
        "chapters": [{"chapter": c,
                      "steps": [say(le, mode) for le in LESSONS
                                if le["chapter"] == c]} for c in CHAPTERS],
        "steps": len(LESSONS),
    }


def _done(learner_id: str) -> set[str]:
    rows = db.connect().execute(
        "SELECT lesson FROM tutorial_progress WHERE learner_id=?",
        (learner_id,)).fetchall()
    return {r["lesson"] for r in rows}


def where(learner_id: str, mode: str = "text") -> dict:
    done = _done(learner_id)
    remaining = [le for le in LESSONS if le["key"] not in done]
    return {
        "learner_id": learner_id, "guide": GUIDE,
        "step": None if not remaining else say(remaining[0], mode),
        "done": len(done), "total": len(LESSONS), "finished": not remaining,
        "note": ("that is all of it — ask the Guardian for any part again"
                 if not remaining else
                 f"step {len(done) + 1} of {len(LESSONS)}"),
    }


def start(learner_id: str, mode: str = "text") -> dict:
    conn = db.connect()
    conn.execute("DELETE FROM tutorial_progress WHERE learner_id=?",
                 (learner_id,))
    conn.commit()
    return where(learner_id, mode)


def mark(learner_id: str, key: str, mode: str = "text") -> dict:
    _index(key)
    conn = db.connect()
    conn.execute(
        "INSERT INTO tutorial_progress (learner_id, lesson, done_at)"
        " VALUES (?,?,?) ON CONFLICT (learner_id, lesson) DO NOTHING",
        (learner_id, key, db.utcnow()))
    conn.commit()
    return where(learner_id, mode)


def step(key: str, mode: str = "text") -> dict:
    return say(LESSONS[_index(key)], mode)


def for_screen(number: int, mode: str = "text") -> dict | None:
    for lesson in LESSONS:
        if number in lesson["screens"]:
            return say(lesson, mode)
    return None
