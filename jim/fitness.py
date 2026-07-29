"""Workout plans — tailored to the minutes you have and the level you're at.

The field promise: "a quick ten-minute session or a full workout, adapted
to your fitness level and schedule, step by step, beginner yoga to
advanced cardio." Built the same way the calm protocols are: from a
curated exercise table, deterministically — a workout is sets and seconds,
and a model that invented a rep count would add nothing but risk. The
Coach remains the place to *talk* about training; this is the place a plan
comes from.

Adaptation without a questionnaire: the plan scales to the minutes asked
for, the level chosen, and the focus picked. Every plan opens with a
warm-up and closes with a cool-down — non-negotiable, both of them,
because the ten-minute user is exactly the one who would skip them.

Plans are logged as events (type ``workout``), so the insights layer sees
training the way it sees check-ins, and an active fitness goal
(jim/life.py) shows up beside the plan the way the coach's context does.
"""

from __future__ import annotations

import json

from . import db

LEVELS = ("beginner", "intermediate", "advanced")
FOCUSES = ("full_body", "cardio", "strength", "yoga", "mobility")

# focus -> level -> the exercise pool, in order of appearance. Each entry:
# (name, seconds at beginner, cue). Intermediate runs 1.5x the seconds,
# advanced 2x — time under work scales; the movement quality cue does not.
_POOLS: dict[str, dict[str, list[tuple[str, int, str]]]] = {
    "full_body": {
        "beginner": [
            ("March in place", 40, "knees easy, arms swinging"),
            ("Chair squats", 40, "sit back, stand tall"),
            ("Wall push-ups", 40, "body in one line"),
            ("Standing row with towel", 40, "squeeze the shoulder blades"),
            ("Glute bridge", 40, "press through the heels"),
        ],
        "intermediate": [
            ("Jumping jacks", 40, "soft landings"),
            ("Bodyweight squats", 40, "chest up, knees tracking toes"),
            ("Push-ups", 40, "elbows at forty-five degrees"),
            ("Reverse lunges", 40, "back knee kisses the floor"),
            ("Plank", 40, "long line, no sag"),
        ],
        "advanced": [
            ("Burpees", 40, "land soft, stand tall"),
            ("Jump squats", 40, "full hip extension"),
            ("Decline push-ups", 40, "control down, drive up"),
            ("Bulgarian split squats", 40, "each side"),
            ("Plank to push-up", 40, "hips quiet"),
        ],
    },
    "cardio": {
        "beginner": [
            ("Brisk march", 60, "pump the arms"),
            ("Step touches", 60, "wide and springy"),
            ("Low-impact jacks", 60, "step out, reach up"),
        ],
        "intermediate": [
            ("Jog in place", 60, "quick light feet"),
            ("High knees", 45, "drive the knees"),
            ("Skaters", 45, "push side to side"),
            ("Mountain climbers", 45, "hips level"),
        ],
        "advanced": [
            ("Sprint in place", 45, "arms at speed"),
            ("Tuck jumps", 30, "land like a cat"),
            ("Burpee broad jumps", 45, "explode forward"),
            ("Fast mountain climbers", 45, "breathe on rhythm"),
        ],
    },
    "strength": {
        "beginner": [
            ("Chair squats", 45, "slow down, quick up"),
            ("Incline push-ups", 45, "hands on a counter"),
            ("Hip hinges", 45, "flat back, push the hips"),
            ("Dead bug", 45, "low back stays down"),
        ],
        "intermediate": [
            ("Tempo squats", 45, "three seconds down"),
            ("Push-ups", 45, "full range"),
            ("Single-leg glute bridge", 45, "each side"),
            ("Side plank", 30, "each side"),
        ],
        "advanced": [
            ("Pistol squat progressions", 45, "each side, use a doorframe"),
            ("Archer push-ups", 45, "shift the load"),
            ("Nordic curl negatives", 30, "slow as you can"),
            ("Hollow body hold", 40, "ribs down"),
        ],
    },
    "yoga": {
        "beginner": [
            ("Cat–cow", 60, "move with the breath"),
            ("Child's pose", 60, "long arms, heavy hips"),
            ("Low lunge", 45, "each side"),
            ("Legs up the wall", 90, "let the floor hold you"),
        ],
        "intermediate": [
            ("Sun salutation A", 90, "one breath per movement"),
            ("Warrior II", 45, "each side, front knee stacked"),
            ("Triangle", 45, "each side, long spine"),
            ("Pigeon", 60, "each side, soften"),
        ],
        "advanced": [
            ("Sun salutation B", 90, "float where you can"),
            ("Half moon", 45, "each side, reach both ways"),
            ("Crow", 45, "knees high on the arms"),
            ("Wheel", 45, "press evenly"),
        ],
    },
    "mobility": {
        "beginner": [
            ("Neck circles", 40, "slow, both ways"),
            ("Shoulder rolls", 40, "big and unhurried"),
            ("Hip circles", 40, "both directions"),
            ("Ankle rocks", 40, "each side"),
        ],
        "intermediate": [
            ("World's greatest stretch", 60, "each side"),
            ("90/90 hip switches", 60, "tall spine"),
            ("Thoracic rotations", 45, "each side"),
            ("Deep squat hold", 45, "heels down"),
        ],
        "advanced": [
            ("Cossack squats", 60, "each side, slow"),
            ("Jefferson curls", 45, "one vertebra at a time"),
            ("Loaded ankle stretch", 45, "each side"),
            ("Bridge-ups", 45, "open the front line"),
        ],
    },
}

_WARMUP = ("Warm-up", 120, "easy movement until you're warm — marching, "
                           "arm circles, gentle twists")
_COOLDOWN = ("Cool-down", 120, "slow everything: long breaths, easy "
                               "stretching of whatever worked hardest")
_SCALE = {"beginner": 1.0, "intermediate": 1.5, "advanced": 2.0}


class FitnessError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


def plan(user_id: str, minutes: int, level: str, focus: str) -> dict:
    """One session, adapted to the minutes, level and focus asked for.
    Warm-up and cool-down are always present; the working blocks cycle the
    focus pool until the time is spent."""
    if not (5 <= int(minutes) <= 90):
        raise FitnessError(422, "minutes must be between 5 and 90")
    if level not in LEVELS:
        raise FitnessError(422, f"level must be one of {', '.join(LEVELS)}")
    if focus not in FOCUSES:
        raise FitnessError(422, f"focus must be one of {', '.join(FOCUSES)}")

    pool = _POOLS[focus][level]
    scale = _SCALE[level]
    budget = int(minutes) * 60 - (_WARMUP[1] + _COOLDOWN[1])
    blocks: list[dict] = [
        {"name": _WARMUP[0], "seconds": _WARMUP[1], "cue": _WARMUP[2]}]
    i, spent = 0, 0
    rest = 15 if level == "beginner" else 10
    while spent < budget:
        name, base, cue = pool[i % len(pool)]
        work = int(base * scale)
        if spent + work > budget:
            break
        blocks.append({"name": name, "seconds": work, "cue": cue})
        spent += work + rest
        i += 1
    blocks.append(
        {"name": _COOLDOWN[0], "seconds": _COOLDOWN[1], "cue": _COOLDOWN[2]})

    total = sum(b["seconds"] for b in blocks) + rest * max(0, i - 1)
    out = {
        "minutes_asked": int(minutes), "level": level, "focus": focus,
        "rest_seconds_between_blocks": rest,
        "blocks": blocks, "total_seconds": total,
        "note": "curated movements, deterministic doses — talk to the "
                "Coach about how it felt, and stop on pain, always",
    }
    conn = db.connect()
    conn.execute(
        "INSERT INTO events (id, user_id, type, condition, severity, detail,"
        " created_at) VALUES (?,?,?,?,?,?,?)",
        (db.new_id("evt"), user_id, "workout", focus, "info",
         json.dumps({"level": level, "minutes": int(minutes),
                     "blocks": len(blocks)}), db.utcnow()))
    conn.commit()
    return out
