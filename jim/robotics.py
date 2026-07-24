"""Robotics catalog — the physical helpers the Guardian can direct.

The same registry QRME and PDI carry (each repo ships its own copy so the
projects share no code): supported robot platforms from full humanoids to home
robots to autonomous vacuums. In JIM a bound robot is a **guardian responder**:
it registers as a device (so escalation alerts dispatch to it like any other),
and on an escalation each body gets a role-appropriate directive — a mobile
robot goes to the user; a vacuum docks and stays clear so floors are open for
people and responders.

``llm_capable`` marks platforms that can run an onboard language model; the
binding records which provider (from the ``jim.llm`` registry) is loaded, so
guidance spoken through the robot uses the user's chosen model.
"""

from __future__ import annotations

# (key, label, maker, kind, capabilities, llm_capable)
_ROWS: list[tuple[str, str, str, str, list[str], bool]] = [
    ("isaac_1", "Isaac 1", "Weave Robotics", "home_robot",
     ["mobility", "manipulation", "voice", "vision", "tidying"], True),
    ("neo", "NEO", "1X Technologies", "humanoid",
     ["mobility", "manipulation", "voice", "vision", "chores"], True),
    ("optimus", "Optimus", "Tesla", "humanoid",
     ["mobility", "manipulation", "force_control", "voice", "vision",
      "chores"], True),
    ("figure_03", "Figure 03", "Figure AI", "humanoid",
     ["mobility", "manipulation", "force_control", "voice", "vision"], True),
    ("atlas", "Atlas", "Boston Dynamics", "humanoid",
     ["mobility", "manipulation", "force_control", "vision"], False),
    ("g1", "G1", "Unitree Robotics", "humanoid",
     ["mobility", "manipulation", "voice", "vision"], True),
    ("u1_lite", "UWorld U1 Lite", "UBTech Robotics", "humanoid",
     ["mobility", "voice", "vision"], True),
    ("u1_pro", "UWorld U1 Pro", "UBTech Robotics", "humanoid",
     ["mobility", "manipulation", "voice", "vision"], True),
    ("u1_ultra", "UWorld U1 Ultra", "UBTech Robotics", "humanoid",
     ["mobility", "manipulation", "voice", "vision", "chores"], True),
    ("memo", "Memo", "Sunday Robotics", "home_robot",
     ["mobility", "manipulation", "voice", "vision", "tidying"], True),
    ("saros_20", "Saros 20", "Roborock", "vacuum",
     ["mapping", "navigation", "vacuum", "mop", "camera_patrol"], True),
    ("saros_20_sonic", "Saros 20 Sonic", "Roborock", "vacuum",
     ["mapping", "navigation", "vacuum", "sonic_mop", "camera_patrol"], True),
    ("qrevo_curv_2_flow", "Qrevo Curv 2 Flow", "Roborock", "vacuum",
     ["mapping", "navigation", "vacuum", "mop"], False),
]

BY_KEY: dict[str, dict] = {
    key: {"model": key, "label": label, "maker": maker, "kind": kind,
          "capabilities": caps, "llm_capable": llm}
    for key, label, maker, kind, caps, llm in _ROWS
}

# What each kind of body may be told to do. Everything else is refused.
COMMANDS: dict[str, list[str]] = {
    "humanoid": ["say", "come_here", "follow", "fetch", "tidy", "patrol",
                 "dock", "stop"],
    "home_robot": ["say", "come_here", "follow", "fetch", "tidy", "patrol",
                   "dock", "stop"],
    "vacuum": ["clean", "spot_clean", "patrol", "dock", "locate", "stop"],
}

# First-aid rating per model. "perform" means the platform has certified
# force-controlled manipulation (mechanical-CPR class, like a LUCAS device
# with legs) and may deliver chest compressions once a person on scene
# confirms the need; "assist" means fetch-and-coach only — bring the AED,
# speak the playbook, keep the pace. Vacuums have no rating: their emergency
# job is clearing the floor. NO rating ever authorizes a robot to deliver a
# defibrillator shock — rhythm analysis stays with the AED and the shock
# button stays with a human.
FIRST_AID_RATING: dict[str, str] = {
    "optimus": "perform",
    "figure_03": "perform",
    "atlas": "perform",
    "neo": "assist",
    "g1": "assist",
    "u1_lite": "assist",     # voice only: can coach, cannot carry
    "u1_pro": "assist",
    "u1_ultra": "assist",
    "isaac_1": "assist",
    "memo": "assist",
}

# Extra commands unlocked by the first-aid rating (on top of the kind list).
# auto_defib additionally requires a signed autonomous-resuscitation waiver
# (enforced per-user in guardian.robot_command, since ratings are per-model).
_ASSIST_COMMANDS = ["fetch_aed", "guide_first_aid", "meet_responders"]
_PERFORM_COMMANDS = _ASSIST_COMMANDS + ["perform_cpr", "stop_cpr", "auto_defib"]

# The directive each kind receives when the Guardian escalates: mobile bodies
# converge on the user; vacuums clear the floor and light the way home.
ESCALATION_DIRECTIVE = {
    "humanoid": "navigate_to_user",
    "home_robot": "navigate_to_user",
    "vacuum": "dock_and_clear_floor",
}

# Cardiac escalations override the generic directive with a first-aid role
# matched to the body's rating.
CARDIAC_DIRECTIVE = {
    "perform": "begin_hands_only_cpr_110bpm_until_aed_or_ems",
    "assist": "fetch_aed_and_coach_cpr_pace",
}

# With a signed autonomous-resuscitation waiver on file, a perform-rated body
# escalates straight into the full sequence: compressions plus a fully-
# automatic-AED-class device that shocks on its own analysis (the robot's job
# is stand-clear verification). Assist bodies keep their fetch-and-coach role.
CARDIAC_DIRECTIVE_WAIVED = {
    "perform": "auto_resuscitate_cpr_plus_auto_aed",
    "assist": "fetch_aed_and_coach_cpr_pace",
}


def catalog() -> dict:
    makers: dict[str, list[dict]] = {}
    for row in BY_KEY.values():
        entry = {**row, "first_aid": FIRST_AID_RATING.get(row["model"])}
        makers.setdefault(row["maker"], []).append(entry)
    return {"robots": [{**r, "first_aid": FIRST_AID_RATING.get(r["model"])}
                       for r in BY_KEY.values()],
            "by_maker": makers,
            "commands": COMMANDS,
            "first_aid_ratings": FIRST_AID_RATING,
            "escalation_directives": ESCALATION_DIRECTIVE,
            "cardiac_directives": CARDIAC_DIRECTIVE}


def get(model: str) -> dict | None:
    return BY_KEY.get(model)


def first_aid_rating(model: str) -> str | None:
    return FIRST_AID_RATING.get(model)


def allowed_commands(model: str) -> list[str]:
    spec = BY_KEY.get(model)
    if spec is None:
        return []
    base = COMMANDS.get(spec["kind"], [])
    rating = FIRST_AID_RATING.get(model)
    if rating == "perform":
        return base + _PERFORM_COMMANDS
    if rating == "assist":
        return base + _ASSIST_COMMANDS
    return base


def directive_for(model: str, cardiac: bool = False,
                  waived: bool = False) -> str | None:
    spec = BY_KEY.get(model)
    if spec is None:
        return None
    if cardiac:
        rating = FIRST_AID_RATING.get(model)
        table = CARDIAC_DIRECTIVE_WAIVED if waived else CARDIAC_DIRECTIVE
        if rating in table:
            return table[rating]
    return ESCALATION_DIRECTIVE.get(spec["kind"])
