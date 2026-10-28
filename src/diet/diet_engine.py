"""Unified API for Phase 4 diet recommendations."""

from __future__ import annotations

from .diet_profile import DietaryProfile
from .food_database import FoodDatabase
from .food_query import QueryResult, evaluate_food_query
from .meal_planner import MealPlan, generate_heart_meal_plan
from .food_schema import FoodItem


class DietEngine:
    """Facade combining food queries and meal-plan generation."""

    def __init__(self, database: FoodDatabase | None = None) -> None:
        self.database = database or FoodDatabase()

    def evaluate_query(
        self,
        query_text_or_food: str | FoodItem,
        portion_str: str,
        profile: DietaryProfile,
    ) -> QueryResult:
        """Evaluate one food portion."""
        return evaluate_food_query(query_text_or_food, portion_str, profile, self.database)

    def generate_plan(self, profile: DietaryProfile) -> MealPlan:
        """Generate one general daily plan."""
        return generate_heart_meal_plan(profile, self.database)


def evaluate_query(
    query_text_or_food: str | FoodItem,
    portion_str: str,
    profile: DietaryProfile,
    database: FoodDatabase | None = None,
) -> QueryResult:
    """Functional convenience wrapper for food queries."""
    return DietEngine(database).evaluate_query(query_text_or_food, portion_str, profile)


def generate_plan(profile: DietaryProfile, database: FoodDatabase | None = None) -> MealPlan:
    """Functional convenience wrapper for meal plans."""
    return DietEngine(database).generate_plan(profile)

