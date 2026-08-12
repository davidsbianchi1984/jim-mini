"""The help box — where does a thing live, in one written sentence.

QRME's helper answers questions about QRME; this is JIM's own. It is a
table of written directions, one per door in the app, matched by keyword —
deliberately not a model call: a lost person needs the name of a tab, not
a paragraph, and a written answer cannot hallucinate a feature that isn't
there. Anything past the app itself is the Coach's job, and the fallback
says exactly that instead of guessing.
"""

from __future__ import annotations

DISCLOSURE = ("Written directions about this app. For guidance about your "
              "life or health, ask the Coach — that's what it's for.")

# keyword tuple -> the one-sentence direction. First match wins; keywords
# are matched case-insensitively against the whole question.
DIRECTIONS: dict[tuple[str, ...], str] = {
    ("overview", "home", "start"):
        "Overview is the first tab — your day at a glance: readings, "
        "check-ins, and anything the Guardian wants you to see.",
    ("monitor", "reading", "heart", "vitals", "sample"):
        "Live Monitoring takes readings — typed by hand or dripped from a "
        "watch — and every one runs through detection before anything else.",
    ("baseline", "band", "drift", "normal"):
        "Your Baseline shows the bands drawn around your own normal, per "
        "metric, each one adjustable — a crossing becomes a question, "
        "never an alarm.",
    ("crash", "emergency", "unresponsive", "911", "trusted", "sos",
     "collapse", "get help now"):
        "Safety → Get help now is your own press: one button reaches your "
        "emergency contact, your Medical ID, first aid and every connected "
        "device — and says plainly that JIM cannot dial 911 itself. The "
        "crash watch is the automatic path when you cannot press anything: "
        "arm it on Your Baseline with a trusted person, and its status "
        "shows on Safety.",
    ("med", "pill", "dose", "cabinet", "prescription"):
        "Medications is the cabinet: what you take in your own words, the "
        "day's dose board, and adherence — a missed dose is a check-in, "
        "never an alarm.",
    ("care team", "careteam", "organization", "household", "desk"):
        "Care Team links your own QRME organization so the Guardian can "
        "take stacked concerns to the whole team — link it with your QRME "
        "owner token, then coordinate by hand any time.",
    ("coach", "advice", "talk", "voice", "speak"):
        "Coach is the 24/7 conversation — type or press “Talk to "
        "it” and speak; it answers out loud when you spoke first.",
    ("check-in", "checkin", "mood", "energy"):
        "Check-in is the daily minute: mood, energy, and a note if you "
        "want — the Guardian reads it the way it reads a reading.",
    ("journal", "diary", "entry", "write"):
        "Journal is your own words, typed or spoken — entries are sealed "
        "in your vault on a private plan, newest first.",
    ("privacy", "settings", "vault", "plan", "data", "delete"):
        "Privacy holds the controls: your plan and its storage posture, "
        "the vigil, connections, and the delete-everything door.",
    ("watch", "apple watch", "wearable", "drip"):
        "The watch bridge is in Privacy → Apple Watch: a drip address "
        "an iPhone Shortcut deposits readings at.",
    ("version", "not found", "update", "backend"):
        "If screens answer “Not Found”, two versions of JIM are "
        "probably running — the red banner names them; quit the older app "
        "or press “Use this app's own backend”.",
    ("did that help", "follow up", "followup", "it did not help",
     "guidance did not work", "ask me again"):
        "Guidance that goes out gets one question on Monitor: did that "
        "help? Saying it did not runs the escalation ladder again and names "
        "the people reachable now — it is not filed away as a complaint.",
    ("what it learned", "what jim knows about me", "my profile",
     "adaptation", "personalised", "personalized", "learned about me"):
        "Settings → What JIM has learned about you: which guidance has "
        "actually worked for you and how often, shown as counts rather than "
        "a score. Built here from your own history — no vendor saw it.",
    ("anonymous", "pseudonym", "my name", "hide my name", "real name",
     "legal name"):
        "Settings → Your name here. You can be known by a pseudonym; every "
        "emergency path still works, and the one cost — no legal name for "
        "responders unless you leave one — is stated there.",
    ("community", "rooms", "forum", "local events", "meet people",
     "other people"):
        "Connect → Community. The rooms and local events live in QRME and "
        "JIM opens the door; nothing is mirrored back, nothing posts as "
        "you, and no health data crosses over.",
    # The words somebody uses when something has just broken, and the ones
    # they use when they have noticed the reporting and want it stopped.
    ("what went wrong", "error", "errors", "it failed", "something broke",
     "bug", "report a bug", "crash", "stop sending", "stop reporting",
     "opt out", "diagnostics"):
        "Privacy → What went wrong. Failed requests are kept as the operation "
        "and the status code — never the error message, which quotes what you "
        "typed, and never an id, which would name a capture of you. The card "
        "shows the exact payload before anything leaves, and the switch beside "
        "it stops the sending for good.",
    # Six doors that existed only on the phone until 0.22.0. A person who
    # went looking for one of these on the desktop was told, correctly, that
    # it was beyond the app's own doors — which it was.
    ("goal", "goals", "habit", "habits", "budget", "spending", "streak"):
        "What you're working on: goals, habits and a monthly budget. A goal "
        "is read by the Coach and the daily suggestion, and a budget is how "
        "the Guardian learns the shape of financial stress.",
    ("child", "children", "my kid", "my son", "my daughter", "guardian of",
     "parental", "quiet hours"):
        "Who you watch: link a child, see their light and their events, and "
        "set quiet hours. Pausing holds everyday guidance only — monitoring, "
        "crisis escalation and the emergency path never pause.",
    ("who has read", "access log", "custody", "provenance", "my record",
     "what do you have on me", "erase everything", "consent a source"):
        "What's held about you: whether it is sealed, whether anybody's "
        "reading of it is even being written down, which sources you have "
        "allowed, and the erase-everything door.",
    ("specialist", "specialists", "referral", "clinician", "relay", "rota",
     "on call", "ladder", "escalation"):
        "Who else is looking: the specialists a thing can be handed to, the "
        "clinicians a referral reaches, and the full escalation ladder with "
        "its floors and its one ceiling.",
    ("robot", "robots", "humanoid", "care code", "beacon", "qr", "mastodon",
     "excursion", "post for me"):
        "What reaches out: a bound robot and its first-aid rating, a placed "
        "code a stranger can scan, accounts on platforms JIM does not run, "
        "and excursions — which report what was redacted on the way out.",
    ("tone", "how it talks", "sensitivity", "language", "translate",
     "what it made of me", "insights", "my report", "the dock", "corner"):
        "Bearing: what you set (language, tone, sensitivity), what you told "
        "it (conditions, context, sources), and what it made of that — the "
        "insights and follow-ups it wrote about you.",
    ("meal", "plate", "what i ate", "food photo", "log a meal", "ate today"):
        "Journal → Meals: photograph the plate and say a sentence about it "
        "— the photo seals like a clinical capture, the note is the log the "
        "offline coach reads, and the day's meals read back newest first.",
    ("weekly letter", "letter", "my week in words", "week in review"):
        "Journal → Weekly letter: a short letter composed only from what "
        "you actually logged that week — check-ins, meals, habits, journal "
        "entries, goal movement — and a week with nothing in it says so "
        "rather than inventing one.",
    ("interview", "drill", "drills", "practice an answer",
     "rehearse an answer", "job question"):
        "Aims → Interview drills: a question dealt from a local bank with "
        "three probes under it, and an honest reading of your answer — a "
        "model's when one is reachable, a written checklist's when not, "
        "and it says which.",
    ("statement", "bank", "aggregator", "plaid", "csv", "link my bank"):
        "Settings → Money: drop a CSV statement into the vault — the "
        "reading is deterministic and the closing balance wakes the same "
        "warning ladder as spending — and record a bank-link consent "
        "beside it; sync answers honestly that this deployment holds no "
        "aggregator credentials rather than inventing a balance.",
    ("hazard", "carbon monoxide", "gas leak", "smoke", "air quality",
     "is my room safe", "dangers at home"):
        "Connected apps' room readings are scanned on arrival by an "
        "offline hazard table — gas, carbon monoxide, smoke, falls, heat, "
        "cold, strain, air quality — each warning carrying the reference "
        "it draws on, landing as Life insights worst first.",
    ("guardian consent", "parent consent", "activation code", "minor",
     "under 18", "my parent"):
        "A minor's signup asks for a parent or guardian address distinct "
        "from their own — the activation code and link go to that inbox, "
        "and activation records whose address consented and when.",
}


def topics() -> list[str]:
    return [answer for answer in DIRECTIONS.values()]


def ask(question: str) -> dict:
    """One written direction, or an honest hand-off. Never writes anything,
    never calls a model — see the module docstring."""
    q = (question or "").strip().lower()
    if not q:
        return {"answer": "Ask where anything lives in this app — "
                          "“where are my medications?” works.",
                "source": "written", "ai": False, "disclosure": DISCLOSURE}
    for keywords, answer in DIRECTIONS.items():
        if any(k in q for k in keywords):
            return {"answer": answer, "source": "written", "ai": False,
                    "disclosure": DISCLOSURE}
    return {"answer": "That's beyond the app's own doors — ask the Coach "
                      "(the Coach tab), which is the half of JIM built for "
                      "open questions.",
            "source": "written", "ai": False, "disclosure": DISCLOSURE}
