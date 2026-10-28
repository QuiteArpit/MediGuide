"""Tests for the Phase 3 food-nutrition foundation."""

import pytest

from src.diet import FoodDatabase, Nutrients, ServingSize, ServingUnit, nutrients_for_portion


def test_seed_database_contains_expected_foods_and_categories():
    database = FoodDatabase()
    assert len(database) >= 40
    assert database.get_food("roti").name == "Roti"
    assert database.get_food("Steamed rice").id == "rice"
    assert database.get_food("unknown food") is None


def test_exact_and_fuzzy_food_search():
    database = FoodDatabase()
    assert database.search_foods("samosa")[0].id == "samosa"
    assert any(food.id == "palak_paneer" for food in database.search_foods("paneer"))
    assert any(food.id == "tadka_dal" for food in database.search_foods("dal"))
    assert database.search_foods("") == []


def test_nutrient_scaling_for_two_katori_dal():
    database = FoodDatabase()
    dal = database.get_food("tadka_dal")
    assert dal is not None
    nutrients = nutrients_for_portion(dal, "2 katori")
    expected = dal.nutrients_per_100g.scaled(dal.default_serving.grams_equivalent * 2)
    assert nutrients == expected


def test_metric_and_numeric_portion_conversions():
    database = FoodDatabase()
    rice = database.get_food("rice")
    assert rice is not None
    assert nutrients_for_portion(rice, "150g") == rice.nutrients_per_100g.scaled(150)
    assert nutrients_for_portion(rice, 1, ServingUnit.PIECE) == rice.nutrients_per_100g.scaled(150)


def test_tag_filtering_is_case_insensitive():
    database = FoodDatabase()
    sodium = database.filter_by_tag("HIGH_SODIUM")
    healthy = database.filter_by_tag("heart_healthy")
    assert sodium
    assert healthy
    assert all("high_sodium" in food.tags for food in sodium)
    assert all("heart_healthy" in food.tags for food in healthy)


@pytest.mark.parametrize("portion", ["", "two katori", "0g", "-2g", "3 unknown"])
def test_invalid_portions_fail_safely(portion):
    food = FoodDatabase().get_food("rice")
    assert food is not None
    with pytest.raises((TypeError, ValueError)):
        nutrients_for_portion(food, portion)


def test_schema_rejects_invalid_values_and_zero_servings():
    with pytest.raises(ValueError):
        Nutrients(sodium_mg=-1)
    with pytest.raises(ValueError):
        ServingSize(ServingUnit.CUP, 0)

