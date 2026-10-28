"""Tests for Phase 4 diet recommendations."""

from src.diet import DietaryProfile, DietEngine, FoodDatabase


def test_suitability_for_high_risk_and_healthy_foods():
    engine = DietEngine(FoodDatabase())
    profile = DietaryProfile(heart_condition=True, hypertension=True, diet_preference="vegetarian")
    assert engine.evaluate_query("samosa", "1 piece", profile).suitability == "unsuitable"
    assert engine.evaluate_query("oats", "200g", profile).suitability == "suitable"
    assert engine.evaluate_query("tadka dal", "1 katori", profile).suitability == "suitable"


def test_high_sodium_or_fried_food_has_healthier_alternatives():
    result = DietEngine().evaluate_query("samosa", "1 piece", DietaryProfile(heart_condition=True))
    assert result.healthier_alternatives
    assert any("heart_healthy" in food.tags for food in result.healthier_alternatives)
    assert result.disclaimer


def test_generated_plan_stays_within_sodium_target():
    plan = DietEngine().generate_plan(DietaryProfile(heart_condition=True, hypertension=True))
    assert plan.total_nutrients.sodium_mg <= 2000
    assert plan.meets_targets
    assert plan.disclaimer


def test_vegetarian_preference_is_enforced():
    plan = DietEngine().generate_plan(DietaryProfile(diet_preference="vegetarian"))
    for entries in plan.meals.values():
        assert all("vegetarian" in entry["food"].tags for entry in entries)


def test_custom_sodium_limit_and_serialization():
    profile = DietaryProfile(custom_sodium_limit_mg=1000)
    result = DietEngine().evaluate_query("namkeen", "30g", profile)
    assert result.nutrient_impact["sodium_mg"]["percent_of_daily_limit"] >= 25
    assert "disclaimer" in result.to_dict()
