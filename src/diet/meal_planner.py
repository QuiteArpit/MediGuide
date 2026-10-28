"""Deterministic heart-conscious meal plan generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .diet_profile import DietaryProfile
from .food_database import FoodDatabase
from .food_schema import FoodItem, Nutrients
from .unit_converts import nutrients_for_portion
from .food_query import DIET_DISCLAIMER


@dataclass(frozen=True)
class MealPlan:
    """A general educational daily meal plan."""

    meals: dict[str, list[dict[str, Any]]]
    total_nutrients: Nutrients
    meets_targets: bool
    summary_notes: list[str]
    disclaimer: str = DIET_DISCLAIMER

    def to_dict(self) -> dict[str, Any]:
        """Return a serializable meal plan."""
        meals: dict[str, list[dict[str, Any]]] = {}
        for meal, entries in self.meals.items():
            meals[meal] = [
                {**entry, "food": entry["food"].name, "nutrients": entry["nutrients"].as_dict()}
                for entry in entries
            ]
        return {
            "meals": meals,
            "total_nutrients": self.total_nutrients.as_dict(),
            "meets_targets": self.meets_targets,
            "summary_notes": list(self.summary_notes),
            "disclaimer": self.disclaimer,
        }


def _foods(database: FoodDatabase, ids: list[str]) -> list[FoodItem]:
    result: list[FoodItem] = []
    for food_id in ids:
        food = database.get_food(food_id)
        if food is None:
            raise ValueError(f"Seed food is missing from database: {food_id}")
        result.append(food)
    return result


def generate_heart_meal_plan(profile: DietaryProfile, database: FoodDatabase) -> MealPlan:
    """Generate a low-sodium plan from the seed foods.

    Portions are explicit grams so the plan does not depend on ambiguous
    household measures. The output is educational and not an individualized
    prescription.
    """
    selected = {
        "breakfast": [("oats", "200g"), ("banana", "120g")],
        "lunch": [("roti", "80g"), ("tadka_dal", "150g"), ("mix_veg", "150g")],
        "dinner": [("moong_dal", "150g"), ("rice", "150g"), ("bhindi", "150g")],
        "snacks": [("apple", "150g"), ("dahi", "150g")],
    }
    if profile.diet_preference == "vegetarian":
        selected = {meal: entries for meal, entries in selected.items()}
    elif profile.diet_preference == "non_vegetarian":
        selected["dinner"] = [("grilled_fish", "120g"), ("rice", "150g"), ("mix_veg", "150g")]

    meals: dict[str, list[dict[str, Any]]] = {}
    total = Nutrients()
    for meal, entries in selected.items():
        meal_entries: list[dict[str, Any]] = []
        for food_id, portion in entries:
            food = _foods(database, [food_id])[0]
            nutrients = nutrients_for_portion(food, portion)
            meal_entries.append({"food": food, "portion": portion, "nutrients": nutrients})
            total = total + nutrients
        meals[meal] = meal_entries

    targets = profile.daily_targets()
    meets = (
        total.calories_kcal <= targets.calories_kcal
        and total.sodium_mg <= targets.sodium_mg
        and total.saturated_fat_g <= targets.saturated_fat_g
        and total.dietary_fiber_g >= targets.dietary_fiber_g
    )
    notes = [
        "Choose fresh, minimally processed foods and avoid adding extra salt.",
        "Portions are examples for education; adjust with a healthcare professional or dietitian when needed.",
        "No medication changes or fluid restrictions are included.",
    ]
    return MealPlan(meals, total, meets, notes)

