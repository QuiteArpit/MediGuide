"""Public API for MediGuide's food-nutrition knowledge base."""

from .food_database import FoodDatabase, seed_foods
from .diet_engine import DietEngine, evaluate_query, generate_plan
from .diet_profile import DailyTargets, DietaryProfile
from .food_query import DIET_DISCLAIMER, QueryResult, evaluate_food_query
from .food_schema import FoodItem, Nutrients, ServingSize, ServingUnit
from .meal_planner import MealPlan, generate_heart_meal_plan
from .unit_converts import convert_quantity, nutrients_for_portion, parse_portion

__all__ = [
    "DIET_DISCLAIMER",
    "DailyTargets",
    "DietEngine",
    "DietaryProfile",
    "FoodDatabase",
    "FoodItem",
    "MealPlan",
    "Nutrients",
    "QueryResult",
    "ServingSize",
    "ServingUnit",
    "convert_quantity",
    "evaluate_food_query",
    "evaluate_query",
    "generate_heart_meal_plan",
    "generate_plan",
    "nutrients_for_portion",
    "parse_portion",
    "seed_foods",
]
