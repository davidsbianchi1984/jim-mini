"""Environmental hazards, seen before they become injuries.

P001 clause 2's extension names the job: "ergonomic risk factors,
environmental hazards, and physiological stress levels monitored by input
or output devices ... predictive algorithms to identify potential
abnormalities before they manifest." The environment items connected apps
collect describe the room; this module reads them for the room's dangers
and answers with referenced first-aid-adjacent advice, in English like all
safety text.

The scan is deliberately a plain keyword table, not a model call: hazard
detection must work with the network cut, cost nothing, and be auditable
line by line. Every entry carries the reference its advice is drawn from.
"""

from __future__ import annotations

# hazard -> (keywords that indicate it, severity, advice, reference)
HAZARDS: dict[str, dict] = {
    "gas_leak": {
        "keywords": ("smell of gas", "smells of gas", "gas leak",
                     "rotten egg smell", "sulfur smell"),
        "severity": "critical",
        "advice": ("Do not use switches, flames, or phones inside. Open "
                   "doors and windows on the way out, leave immediately, "
                   "and call the gas emergency line from outside."),
        "reference": "US CPSC — natural gas leak safety",
    },
    "carbon_monoxide": {
        "keywords": ("carbon monoxide", "co alarm", "co detector beeping",
                     "generator running indoors"),
        "severity": "critical",
        "advice": ("Get everyone to fresh air immediately and call "
                   "emergency services. Do not re-enter until cleared. "
                   "Headache, dizziness and nausea in several people at "
                   "once are classic signs."),
        "reference": "CDC — carbon monoxide poisoning prevention",
    },
    "smoke_or_fire": {
        "keywords": ("smoke in", "smoky", "burning smell", "fire alarm",
                     "smoke alarm"),
        "severity": "critical",
        "advice": ("Leave low under the smoke, close doors behind you, and "
                   "call emergency services from outside. Never re-enter "
                   "for belongings."),
        "reference": "NFPA — home fire escape planning",
    },
    "fall_risk": {
        "keywords": ("wet floor", "loose rug", "cluttered floor",
                     "cables across", "icy steps", "poor lighting on stairs",
                     "dark stairs"),
        "severity": "warning",
        "advice": ("Clear or mark the walking path before anything else — "
                   "falls are the leading cause of injury at home for "
                   "older adults. Dry wet floors, tape or reroute cables, "
                   "and light the stairs."),
        "reference": "CDC STEADI — older adult fall prevention",
    },
    "extreme_heat": {
        "keywords": ("very hot indoors", "no air conditioning", "heat wave",
                     "stifling", "sweltering"),
        "severity": "warning",
        "advice": ("Drink water on a schedule rather than by thirst, use "
                   "fans with a cracked window, and move to the coolest "
                   "room. Watch for confusion or hot dry skin — that is "
                   "heat stroke: call emergency services."),
        "reference": "CDC — extreme heat guidance",
    },
    "extreme_cold": {
        "keywords": ("freezing indoors", "no heating", "very cold inside",
                     "unheated"),
        "severity": "warning",
        "advice": ("Layer clothing including a hat, close off unused "
                   "rooms, and never heat with an oven or outdoor "
                   "appliance — that trades cold for carbon monoxide."),
        "reference": "CDC — winter weather indoor safety",
    },
    "ergonomic_strain": {
        "keywords": ("hunched over", "screen too low", "no back support",
                     "standing all day on concrete", "repetitive lifting"),
        "severity": "notice",
        "advice": ("Raise the screen to eye height, support the lower "
                   "back, and break static postures every 30–45 minutes — "
                   "strain injuries build silently before they hurt."),
        "reference": "OSHA — computer workstation ergonomics",
    },
    "air_quality": {
        "keywords": ("mold on", "moldy", "musty smell", "heavy dust",
                     "poor ventilation", "wildfire smoke"),
        "severity": "warning",
        "advice": ("Ventilate or filter the air, and fix the moisture "
                   "source before cleaning mold. Anyone with asthma should "
                   "avoid the room until it clears."),
        "reference": "EPA — indoor air quality and mold",
    },
}


def scan(text: str) -> list[dict]:
    """Every hazard the text indicates, worst first. Deterministic, offline,
    and exactly as good as its table — which is the point: what it flags it
    can explain, and what it misses a person still can."""
    found = []
    lowered = (text or "").lower()
    for name, entry in HAZARDS.items():
        if any(k in lowered for k in entry["keywords"]):
            found.append({"hazard": name, "severity": entry["severity"],
                          "advice": entry["advice"],
                          "reference": entry["reference"]})
    order = {"critical": 0, "warning": 1, "notice": 2}
    found.sort(key=lambda h: order[h["severity"]])
    return found
