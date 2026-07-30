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
    ("crash", "emergency", "unresponsive", "911", "trusted"):
        "The crash watch lives on Your Baseline: arm it with a trusted "
        "person, and if a critical reading goes unanswered too many times, "
        "help is sent the way you programmed.",
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
