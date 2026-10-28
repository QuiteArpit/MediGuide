"""Dietary profile and conservative daily nutrient targets."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DietaryProfile:
    """Preferences and health context used for general diet education."""

    heart_condition: bool = False
    hypertension: bool = False
    diabetes: bool = False
    high_cholesterol: bool = False
    diet_preference: str = "any"
    calorie_target_kcal: float = 2000.0
    custom_sodium_limit_mg: float | None = None

    def __post_init__(self) -> None:
        if self.diet_preference not in {"vegetarian", "non_vegetarian", "any"}:
            raise ValueError("diet_preference must be vegetarian, non_vegetarian, or any.")
        if self.calorie_target_kcal <= 0:
            raise ValueError("calorie_target_kcal must be greater than zero.")
        if self.custom_sodium_limit_mg is not None and self.custom_sodium_limit_mg <= 0:
            raise ValueError("custom_sodium_limit_mg must be greater than zero.")

    def daily_targets(self) -> "DailyTargets":
        """Calculate conservative targets for general educational use."""
        return DailyTargets(
            calories_kcal=self.calorie_target_kcal,
            sodium_mg=self.custom_sodium_limit_mg or 2000.0,
            saturated_fat_g=15.0,
            dietary_fiber_g=25.0,
        )


@dataclass(frozen=True)
class DailyTargets:
    """Daily nutrient boundaries used by the recommendation engine."""

    calories_kcal: float = 2000.0
    sodium_mg: float = 2000.0
    saturated_fat_g: float = 15.0
    dietary_fiber_g: float = 25.0

