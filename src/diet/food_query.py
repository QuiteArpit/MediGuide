"""Food suitability queries and conservative alternatives."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .diet_profile import DietaryProfile
from .food_database import FoodDatabase
from .food_schema import FoodItem
from .unit_converts import nutrients_for_portion


DIET_DISCLAIMER = (
    "This is general educational nutrition information, not medical advice. "
    "It does not replace advice from a qualified healthcare professional. "
    "Do not change prescribed medicines or fluid instructions based on this result."
)


@dataclass(frozen=True)
class QueryResult:
    """Structured result for a food and portion query."""

    food_name: str
    portion_str: str
    suitability: str
    nutrient_impact: dict[str, dict[str, float]]
    advice: str
    healthier_alternatives: list[FoodItem]
    disclaimer: str = DIET_DISCLAIMER

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly result."""
        return {
            "food_name": self.food_name,
            "portion_str": self.portion_str,
            "suitability": self.suitability,
            "nutrient_impact": self.nutrient_impact,
            "advice": self.advice,
            "healthier_alternatives": [food.name for food in self.healthier_alternatives],
            "disclaimer": self.disclaimer,
        }


def _resolve_food(query: str | FoodItem, database: FoodDatabase) -> FoodItem:
    if isinstance(query, FoodItem):
        return query
    food = database.get_food(query)
    if food is None:
        matches = database.search_foods(query)
        food = matches[0] if matches else None
    if food is None:
        raise ValueError(f"Food not found: {query!r}")
    return food


def _alternatives(food: FoodItem, profile: DietaryProfile, database: FoodDatabase) -> list[FoodItem]:
    candidates = []
    for item in database.filter_by_tag("heart_healthy"):
        if item.id == food.id:
            continue
        if profile.diet_preference == "vegetarian" and "vegetarian" not in item.tags:
            continue
        similarity = 0 if item.category == food.category else 1
        candidates.append((similarity, item.name, item))
    return [item for _, _, item in sorted(candidates)[:3]]


def evaluate_food_query(
    query_text_or_food: str | FoodItem,
    portion_str: str,
    profile: DietaryProfile,
    database: FoodDatabase,
) -> QueryResult:
    """Evaluate a portion against conservative profile targets."""
    food = _resolve_food(query_text_or_food, database)
    nutrients = nutrients_for_portion(food, portion_str)
    targets = profile.daily_targets()
    limits = {
        "calories_kcal": targets.calories_kcal,
        "sodium_mg": targets.sodium_mg,
        "saturated_fat_g": targets.saturated_fat_g,
        "dietary_fiber_g": targets.dietary_fiber_g,
    }
    impact = {
        nutrient: {
            "value": round(getattr(nutrients, nutrient), 2),
            "percent_of_daily_limit": round(getattr(nutrients, nutrient) / limit * 100, 2),
        }
        for nutrient, limit in limits.items()
    }
    concerns: list[str] = []
    if "high_sodium" in food.tags or nutrients.sodium_mg > targets.sodium_mg * 0.25:
        concerns.append("sodium")
    if "fried" in food.tags or "high_saturated_fat" in food.tags or nutrients.saturated_fat_g > targets.saturated_fat_g * 0.25:
        concerns.append("saturated fat or frying")
    if profile.diabetes and nutrients.carbohydrates_g > 30:
        concerns.append("carbohydrate content")
    if concerns:
        suitability = "unsuitable" if len(concerns) >= 2 or "high_sodium" in food.tags and "fried" in food.tags else "caution"
        advice = f"Use this portion cautiously because of {', '.join(concerns)}. Consider a less processed or less fried alternative."
    else:
        suitability = "suitable"
        advice = "This portion fits the general nutrient limits used for this educational screen. Prefer varied, minimally processed foods."
    return QueryResult(food.name, portion_str, suitability, impact, advice, _alternatives(food, profile, database))

