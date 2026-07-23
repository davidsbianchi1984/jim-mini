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

# The directive each kind receives when the Guardian escalates: mobile bodies
# converge on the user; vacuums clear the floor and light the way home.
ESCALATION_DIRECTIVE = {
    "humanoid": "navigate_to_user",
    "home_robot": "navigate_to_user",
    "vacuum": "dock_and_clear_floor",
}


def catalog() -> dict:
    makers: dict[str, list[dict]] = {}
    for row in BY_KEY.values():
        makers.setdefault(row["maker"], []).append(row)
    return {"robots": list(BY_KEY.values()), "by_maker": makers,
            "commands": COMMANDS,
            "escalation_directives": ESCALATION_DIRECTIVE}


def get(model: str) -> dict | None:
    return BY_KEY.get(model)


def allowed_commands(model: str) -> list[str]:
    spec = BY_KEY.get(model)
    return COMMANDS.get(spec["kind"], []) if spec else []


def directive_for(model: str) -> str | None:
    spec = BY_KEY.get(model)
    return ESCALATION_DIRECTIVE.get(spec["kind"]) if spec else None
