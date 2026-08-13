"""Meal plans — personalized to the goal and the plate you actually keep.

The field promise: "personalized meal plans that fit your dietary
preferences and goals — lose weight, gain muscle, or just eat healthier."
Built like the calm protocols and the workout table: from curated meal
data, deterministically. A day of food is portions and patterns, and a
model inventing a menu could invent an allergen with it; the Coach (whose
nutrition area ships alongside this module) is where the conversation
happens, and this is where a concrete day comes from.

Honesty rails, in order: this is meal *structure*, not medical nutrition
therapy — the disclaimer rides every plan; preferences are exclusion
filters (vegetarian excludes meat) rather than promises about kitchens and
cross-contact; and calories are round textbook figures for orientation,
never a prescription.
"""

from __future__ import annotations

import json

from . import db

GOALS = ("lose_weight", "gain_muscle", "eat_healthier")
PREFERENCES = ("vegetarian", "vegan", "dairy_free", "gluten_free")

DISCLAIMER = ("Meal structure, not medical nutrition therapy — a "
              "registered dietitian outranks this plan, especially with a "
              "diagnosis in the picture.")

# Each meal: (name, tags, goals it suits). Tags mark what the meal contains
# so preference filters can exclude; goals bias selection, they never
# exclude a meal outright.
_MEALS: dict[str, list[dict]] = {
    "breakfast": [
        dict(name="Greek yogurt with berries and walnuts",
             tags={"dairy"}, protein=True),
        dict(name="Oatmeal with banana and peanut butter", tags={"gluten"}),
        dict(name="Veggie omelette with wholegrain toast",
             tags={"egg", "gluten"}, protein=True),
        dict(name="Tofu scramble with spinach and tomatoes",
             tags=set(), protein=True, plant=True),
        dict(name="Overnight chia pudding with mango", tags=set(),
             plant=True),
    ],
    "lunch": [
        dict(name="Grilled chicken salad with olive-oil dressing",
             tags={"meat"}, protein=True),
        dict(name="Lentil soup with a side salad", tags=set(), plant=True,
             protein=True),
        dict(name="Quinoa bowl with roasted vegetables and feta",
             tags={"dairy"}),
        dict(name="Tuna wholegrain wrap", tags={"fish", "gluten"},
             protein=True),
        dict(name="Chickpea and avocado bowl", tags=set(), plant=True,
             protein=True),
    ],
    "dinner": [
        dict(name="Baked salmon, sweet potato, greens", tags={"fish"},
             protein=True),
        dict(name="Stir-fried tofu with brown rice and broccoli",
             tags=set(), plant=True, protein=True),
        dict(name="Turkey chili with beans", tags={"meat"}, protein=True),
        dict(name="Whole-wheat pasta with tomato and white beans",
             tags={"gluten"}, plant=True),
        dict(name="Bean and vegetable curry with rice", tags=set(),
             plant=True, protein=True),
    ],
    "snack": [
        dict(name="Apple with almond butter", tags=set(), plant=True),
        dict(name="Cottage cheese with pineapple", tags={"dairy"},
             protein=True),
        dict(name="Hummus with carrot sticks", tags=set(), plant=True),
        dict(name="A handful of mixed nuts", tags=set(), plant=True),
        dict(name="Hard-boiled eggs", tags={"egg"}, protein=True),
    ],
}

# preference -> tags it excludes.
_EXCLUDES: dict[str, set[str]] = {
    "vegetarian": {"meat", "fish"},
    "vegan": {"meat", "fish", "dairy", "egg"},
    "dairy_free": {"dairy"},
    "gluten_free": {"gluten"},
}

# goal -> (meals per day, orientation calories, the one-line why)
_SHAPES = {
    "lose_weight": (3, 1600, "three satisfying meals, protein forward, "
                             "no grazing window"),
    "gain_muscle": (4, 2600, "four feeds, protein in every one"),
    "eat_healthier": (3, 2000, "three balanced meals, plants doing most "
                               "of the lifting"),
}


class NutritionError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


def _fits(meal: dict, excluded: set[str]) -> bool:
    return not (meal["tags"] & excluded)


def plan(user_id: str, goal: str, preferences: list[str] | None = None,
         days: int = 1) -> dict:
    if goal not in GOALS:
        raise NutritionError(422, f"goal must be one of {', '.join(GOALS)}")
    preferences = preferences or []
    for p in preferences:
        if p not in PREFERENCES:
            raise NutritionError(
                422, f"unknown preference {p!r}; any of "
                     f"{', '.join(PREFERENCES)}")
    if not (1 <= int(days) <= 7):
        raise NutritionError(422, "days must be between 1 and 7")

    excluded: set[str] = set()
    for p in preferences:
        excluded |= _EXCLUDES[p]
    meals_per_day, calories, why = _SHAPES[goal]
    slots = ["breakfast", "lunch", "dinner", "snack"][:meals_per_day]

    day_plans = []
    for d in range(int(days)):
        meals = []
        for slot in slots:
            pool = [m for m in _MEALS[slot] if _fits(m, excluded)]
            if goal == "gain_muscle":
                protein_pool = [m for m in pool if m.get("protein")]
                pool = protein_pool or pool
            if goal == "eat_healthier":
                plant_pool = [m for m in pool if m.get("plant")]
                # Plants lead, but never to an empty slot.
                pool = plant_pool or pool
            meal = pool[d % len(pool)]
            meals.append({"slot": slot, "name": meal["name"]})
        # `day_number`, not `day`: on this product's wire, `day` is a calendar
        # date string everywhere else (habit logs, problem counters), and a
        # 1-based ordinal wearing the same name forced every reader to hold
        # one name as two types.
        day_plans.append({"day_number": d + 1, "meals": meals})

    out = {
        "goal": goal, "preferences": preferences,
        "shape": {"meals_per_day": meals_per_day,
                  "orientation_calories": calories, "why": why},
        "days": day_plans,
        "disclaimer": DISCLAIMER,
    }
    conn = db.connect()
    conn.execute(
        "INSERT INTO events (id, user_id, type, condition, severity, detail,"
        " created_at) VALUES (?,?,?,?,?,?,?)",
        (db.new_id("evt"), user_id, "meal_plan", goal, "info",
         json.dumps({"days": int(days), "preferences": preferences}),
         db.utcnow()))
    conn.commit()
    return out
