"""What this product is, told to the things that talk for it.

A field report asked the coach to "plant a quarter-hour lookout" and got a
graceful shrug: the model knew what assistants generally cannot do and
nothing about the card two scrolls below the conversation. That was answered
once with five hand-written doors. Then somebody walking about the app with
the conversation in their pocket asked where the medication list was, and the
same shrug came back from a screen that has existed for a year.

    asked     can this assistant do it
    mattered  can the product, and where is it

Five doors was a patch on one field report. This is the whole console: every
surface the census in `ui_screens.txt` knows about has a row here, and a test
holds the two together in both directions. A screen added without a row fails
the suite — which is the point, because the failure mode this answers is a
capability shipping and nothing that speaks for the product ever hearing
about it.

## Why it is selected rather than sent

Thirty-two doors is a manual, and a prompt full of manual stops noticing the
person in front of it. So a turn carries three things:

  * the **core** — the handful of doors that are load-bearing on any turn
    (safety, the permits, the daily check-in, the journal, the lookout),
    which are there whether or not the message mentions them;
  * the **relevant** — the doors whose own words appear in what the person
    just said, most-matched first, capped;
  * the **index** — the names of everything else, and nothing about them.

The index is the part that makes the shrug impossible. It is not the manual;
it is a table of contents, and an assistant that can see a door's name can
say *there is a screen for that, it is called Medications* instead of *I
cannot do that*, which is the difference the field report was about.

## What a row is not

It is not permission. Nothing here lets an assistant change anything: the
permits screen and the delegation policy decide that, and a door named in a
prompt is a direction, the same as a signpost is not a key.
"""

from __future__ import annotations

import re
from typing import NamedTuple


class Door(NamedTuple):
    """One surface of the console, as something that talks can describe it."""

    #: The component, exactly as `ui_screens.txt` names it. The join key —
    #: a row for a surface that no longer exists, or a surface with no row,
    #: is what the guard next to this file fails on.
    surface: str
    #: What the person taps, in the words the console itself renders. Said
    #: back to somebody, this has to match what they are looking at.
    place: str
    #: What it is for, in one line.
    what: str
    #: The person's own words for it. Matched against the message, so these
    #: are what somebody would *say*, not what the code calls it.
    cues: tuple[str, ...]
    #: On every turn regardless of the message. Reserved for the doors whose
    #: absence is a safety or consent failure rather than an inconvenience.
    always: bool = False


#: The console, door by door. Ordered as the navigation orders it, so the
#: index reads like the menu the person is looking at.
DOORS: tuple[Door, ...] = (
    Door("Home", "Overview tab",
         "the front page — today at a glance, and the Guardian's calendar",
         ("overview", "front page", "home screen", "dashboard",
          "calendar")),
    Door("Watch", "Watch tab (it takes the whole screen)",
         "the wrist face — thirty-six of them, each a working screen",
         ("watch face", "wrist", "smartwatch", "my watch", "band")),
    Door("Monitor", "Live Monitoring screen",
         "heart rate, pulse and what the connected sensors see right now",
         ("heart rate", "pulse", "bpm", "vital", "live monitor",
          "sensor", "wearable", "oxygen")),
    Door("Safety", "Safety screen",
         "emergencies, the escalation ladder, who gets alerted, and the "
         "CPR pace — urge immediate help first, the screen second",
         ("emergency", "escalation ladder", "911", "collapse", "crisis",
          "who gets alerted", "ambulance", "danger"),
         always=True),
    Door("Baseline", "Your Baseline screen",
         "what your own normal is and how far from it counts — the vigil, "
         "sensitivity and spending limits live here",
         ("baseline", "normal for me", "sensitivity", "threshold",
          "how alert", "spending limit", "budget")),
    Door("Meds", "Medications screen",
         "the medicine cabinet — what you take, what you have stopped, and "
         "in your own words rather than a formulary",
         ("medication", "medicine", "pill", "prescription", "dose",
          "pharmacy", "refill", "tablet")),
    Door("CareTeam", "Care Team screen",
         "the clinicians and family who share a written plan with you",
         ("care team", "doctor", "clinician", "nurse", "shared plan",
          "caregiver")),
    Door("SelfProfile", "Your own profile screen",
         "the one QRME profile that is this person",
         ("my profile", "own profile", "qrme", "my account")),
    Door("Coach", "Coach screen",
         "this conversation, its areas, the unattended study, and the "
         "Watched pages card below this chat — a lookout repeats between a "
         "quarter-hour and a month",
         ("lookout", "url", "keep an eye on", "coach", "study",
          "this page", "this site"),
         always=True),
    Door("Talk", "JIM-mini tab — the front door",
         "talking to JIM, and the rail that opens every other screen",
         ("talk to jim", "front door", "ask jim", "jim-mini")),
    Door("Engaged", "What-JIM-can-touch screen, also on the chip rail",
         "the permit switches — what the assistant may change on its own, "
         "every act reversible",
         ("permit", "let it change", "allowed", "permission",
          "consent", "what can it touch"),
         always=True),
    Door("Wellness", "Wellness screen",
         "breathing sessions the app paces aloud, workout plans and meal "
         "plans — protocols, not inventions",
         ("breathing", "workout", "exercise", "meal plan", "meditate",
          "relax", "stretch", "calm")),
    Door("Checkin", "Check-in screen",
         "the daily check-in — mood, energy and stress",
         ("check-in", "check in", "mood", "feeling", "energy",
          "stress"),
         always=True),
    Door("Journal", "Journal screen",
         "your own words to JIM, typed or spoken, and the weekly letter "
         "about what the week actually held",
         ("journal", "weekly letter", "diary", "write it down",
          "entry"),
         always=True),
    Door("Aims", "What-you're-working-on screen",
         "goals, habits, and what the month costs",
         ("goal", "habit", "target", "working on", "streak",
          "monthly budget")),
    Door("Wards", "Who-you-watch screen",
         "a child's account and what an adult may see of it",
         ("child", "kid", "minor", "ward", "parental", "my son",
          "my daughter")),
    Door("Attending", "Who-else-is-looking screen",
         "the specialists JIM can hand a thing to, and the full escalation "
         "ladder shown rather than summarised",
         ("specialist", "who else is looking", "hand it to", "referral",
          "second opinion", "escalate")),
    Door("Reach", "What-reaches-out screen",
         "the things that cross out of this window — a body that moves "
         "through the house, a printed code somebody can scan, an account "
         "on a platform JIM does not run, and an excursion that goes and "
         "asks the open web",
         # Short and atomic on purpose. The first draft asked for whole
         # phrases — "look it up online" — and "can you look something up
         # online for me" reached nothing at all. A cue table written as
         # sentences only fires for people who happen to phrase it the way
         # it was typed.
         ("excursion", "online", "the web", "internet", "look up",
          "browse", "robot", "printed code", "qr code", "post for me")),
    Door("Hands", "Hands screen",
         "permission for the Guardian to work a screen on a machine you "
         "own — which apps, which moves, for how many minutes, and the "
         "one press that takes it all back",
         ("hands", "press for me", "click for me", "type for me",
          "work my screen", "drive my computer", "do it on my phone",
          "take over my screen", "fill it in for me")),
    Door("Capabilities", "Capabilities screen",
         "the register of every faculty this Guardian can be given — what "
         "each one currently is, the permission it rests on, and the "
         "screen that withdraws it; it reads and routes, and grants "
         "nothing itself",
         ("capabilities", "what can it do", "what can you do",
          "what is it allowed to do", "permissions", "what did i agree to",
          "what can it see", "what can it hear", "can it move",
          "what is switched on", "how do i turn it off")),
    Door("Bearing", "Bearing screen",
         "how it speaks (language, tone, sensitivity, voice), what it was "
         "told about you, and what it made of that",
         ("tone", "how you speak", "language", "voice", "personality",
          "what you know about me", "insight", "event log")),
    Door("Community", "Community screen",
         "a door to QRME's rooms and local places, opened under this "
         "person's own QRME identity",
         ("community", "forum", "local event", "other people", "room")),
    Door("Presence", "Speaks-first screen",
         "the coach that starts things — what it noticed, unprompted",
         ("speaks first", "unprompted", "reach out to me", "check on me",
          "notice")),
    Door("Feed", "Feed screen",
         "QRME's public stream, shown here",
         ("feed", "stream", "what's new", "post")),
    Door("Channel", "Channel & camera screen",
         "the two ways JIM takes something in — the microphone and the "
         "clinical camera that photographs the body",
         ("camera", "photo", "picture", "microphone", "record",
          "show you", "video", "scan my")),
    Door("Held", "What's-held-about-you screen",
         "what is held, who holds it, who has read it, and the button that "
         "makes it stop being held",
         # Short and atomic on purpose. The first draft asked for whole
         # phrases — "delete my data" — and "delete everything you have on
         # me" reached nothing at all. A cue table written as sentences only
         # fires for people who happen to phrase it the way it was typed.
         ("delete", "erase", "wipe", "held about me", "who read",
          "export", "forget me", "what you have on me")),
    Door("Access", "Accessibility screen",
         "what the product does about blind, deaf, mute, motor, cognitive, "
         "dyslexia and motion needs — all of it works without an account",
         # The needs, and how somebody actually describes having one.
         # Nobody says "accessibility" — they say they cannot see it.
         ("accessibility", "screen reader", "blind", "deaf", "caption",
          "large text", "motion", "dyslexia", "one hand",
          "read it to me", "can't see", "cannot see", "hard to see",
          "hard to hear", "too small")),
    Door("Settings", "Privacy screen",
         "what this deployment can and cannot reach, offline mode "
         "included, readable rather than merely set",
         ("privacy", "offline", "what can this reach", "setting",
          "cloud")),
    Door("Studio", "Widgets screen",
         "tools this person writes for themselves — a function in a box "
         "with no network",
         ("widget", "my own tool", "studio", "little program", "script")),
    Door("Problems", "Report-a-problem screen",
         "what went wrong and exactly what leaves this device, shown as "
         "the report itself rather than a description of it",
         ("report a problem", "bug", "broke", "crash", "not working",
          "broken")),
    Door("Onboarding", "the sign-up flow",
         "signing up, and the age bar the backend applies",
         ("sign up", "create an account", "get started", "register",
          "how old", "birthday")),
    Door("ProviderTiles", "the model tiles, on the Privacy screen",
         "which model answers — tiles, not a dropdown",
         ("which model", "provider", "openai", "anthropic", "model")),
    Door("PaceCue", "the pace circle on Safety",
         "the CPR pace, cued as a flashing light and a tick at 110 a "
         "minute",
         ("cpr", "compression", "metronome", "pace")),
    Door("ProblemNotice", "the first-run notice before anything is sent",
         "what a problem report contains, said once before the first one "
         "goes",
         ("what gets sent", "before i report", "first run notice",
          "leaves this device")),
)

#: How many message-matched doors a turn may carry beyond the core. Six is
#: the number that keeps the block shorter than the context above it, which
#: is what stops the manual from crowding out the person.
LIMIT = 6

_HEAD = ("the product's own doors, and where each lives in this app — when a "
         "request belongs to one, point at it by name instead of declining:")
_FOOT = ("answer questions about this product from these lines rather than "
         "from what assistants generally can or cannot do")
_INDEX = ("the rest of this console, by name only — if one of these is what "
          "they are after, say so and name it rather than declining: ")


#: The endings a single-word cue may wear. Written out rather than stemmed
#: because a stemmer would need a dependency and would still be guessing:
#: this is the closed set of things English does to the handful of verbs and
#: nouns anybody uses to ask for a screen. It exists because a table matched
#: on the exact word only fires for people who happen to speak the way it was
#: typed — `follower` missed "who is following me", `medication` missed
#: "my medications", and each one landed the person in the index instead of
#: on the screen that was sitting in the navigation bar.
_ENDINGS = r"(?:e?s|ing|ed|er|ers)?"


def _row(d: Door) -> str:
    return f"- {d.what}: {d.place}"


def _hits(d: Door, said: str) -> int:
    n = 0
    for cue in d.cues:
        # Whole words, so a short cue does not fire inside an unrelated
        # word — with the plural allowed, because the first draft had
        # `medication` and somebody asking "where are my medications" got
        # the index instead of the screen. A cue list written in the
        # singular and matched in the singular is a table that only works
        # when people happen to speak the way it was typed.
        pattern = (r"\b" + re.escape(cue) + _ENDINGS + r"\b") \
            if " " not in cue else re.escape(cue)
        if re.search(pattern, said):
            n += 1
    return n


def core() -> str:
    """The doors that ride every turn, message or no message.

    Safety, the permits, the check-in, the journal and the lookout: the
    first two because getting them wrong is a harm rather than a
    disappointment, the last three because they are what a coach turn is
    usually about.
    """
    rows = [_row(d) for d in DOORS if d.always]
    return "\n".join([_HEAD, *rows, _FOOT])


def selected(message: str, limit: int = LIMIT) -> list[Door]:
    """The doors this message is about, most-matched first.

    Ties keep the navigation's order, so the answer does not reshuffle
    between two turns that said the same thing.
    """
    # The contract, checked where it is broken rather than three frames
    # down. A caller once handed this a list — a local variable in the
    # prompt builder shadowed the parameter — and the failure surfaced as
    # `'list' object has no attribute 'lower'` inside the selector, which
    # says nothing about where the mistake was.
    if message is not None and not isinstance(message, str):
        raise TypeError(
            f"the message selecting doors must be text, not "
            f"{type(message).__name__} — something upstream is passing the "
            "wrong thing, and the door selection is only where it shows")
    said = (message or "").lower()
    if not said:
        return []
    scored = []
    for i, d in enumerate(DOORS):
        if d.always:
            continue
        n = _hits(d, said)
        if n:
            scored.append((-n, i, d))
    scored.sort()
    return [d for _, _, d in scored[:limit]]


def index(exclude: set[str] | None = None) -> str:
    """Everything else, by name only.

    The line that makes *I cannot do that* wrong when a screen for it is in
    the navigation bar. Names and nothing more: a door somebody can name is
    a door somebody can be walked to on the next turn.
    """
    skip = exclude or set()
    names = [d.place for d in DOORS if d.surface not in skip and not d.always]
    return _INDEX + "; ".join(names)


def lines(message: str = "", limit: int = LIMIT) -> list[str]:
    """The whole block for one turn: core, then relevant, then the index."""
    picked = selected(message, limit)
    out = [core()]
    if picked:
        out.append("also relevant to what they just said:\n"
                   + "\n".join(_row(d) for d in picked))
    out.append(index({d.surface for d in picked}))
    return out
