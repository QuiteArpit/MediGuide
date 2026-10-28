"""Portion parsing and unit conversion helpers."""

from __future__ import annotations

import re
from typing import Mapping

from .food_schema import FoodItem, Nutrients, ServingSize, ServingUnit


_PORTION_RE = re.compile(r"^\s*(?P<quantity>\d+(?:\.\d+)?)\s*(?P<unit>[a-zA-Z/]+)\s*$")
_UNIT_ALIASES: Mapping[str, ServingUnit] = {
    "g": ServingUnit.GRAM, "gram": ServingUnit.GRAM, "grams": ServingUnit.GRAM,
    "ml": ServingUnit.ML, "milliliter": ServingUnit.ML, "milliliters": ServingUnit.ML,
    "katori": ServingUnit.KATORI, "katoris": ServingUnit.KATORI, "bowl": ServingUnit.KATORI, "bowls": ServingUnit.KATORI,
    "cup": ServingUnit.CUP, "cups": ServingUnit.CUP,
    "piece": ServingUnit.PIECE, "pieces": ServingUnit.PIECE,
    "piece/roti": ServingUnit.PIECE, "roti": ServingUnit.PIECE,
    "plate": ServingUnit.PLATE, "plates": ServingUnit.PLATE,
    "tbsp": ServingUnit.TABLESPOON, "tablespoon": ServingUnit.TABLESPOON, "tablespoons": ServingUnit.TABLESPOON,
}


def _unit(value: ServingUnit | str) -> ServingUnit:
    if isinstance(value, ServingUnit):
        return value
    try:
        return _UNIT_ALIASES[value.strip().lower()]
    except (KeyError, AttributeError) as exc:
        raise ValueError(f"Unsupported serving unit: {value!r}") from exc


def convert_quantity(quantity: float, unit: ServingUnit | str, serving: ServingSize) -> float:
    """Convert a quantity of a unit to grams using a food's serving definition."""
    if quantity <= 0:
        raise ValueError("Portion quantity must be greater than zero.")
    normalized = _unit(unit)
    if normalized == ServingUnit.GRAM:
        return quantity
    if normalized == serving.unit_name:
        return quantity * serving.grams_equivalent
    # Water-like volume is a safe generic approximation for liquid records.
    if normalized == ServingUnit.ML:
        return quantity
    raise ValueError(
        f"No conversion from {normalized.value!r} to the food's serving "
        f"unit {serving.unit_name.value!r}."
    )


def parse_portion(portion: str, food: FoodItem) -> float:
    """Parse strings such as ``'150g'`` or ``'2 katori'`` into grams."""
    if not isinstance(portion, str):
        raise TypeError("Portion must be a string such as '150g' or '2 katori'.")
    match = _PORTION_RE.fullmatch(portion)
    if not match:
        raise ValueError(f"Invalid portion: {portion!r}")
    return convert_quantity(float(match.group("quantity")), match.group("unit"), food.default_serving)


def nutrients_for_portion(food: FoodItem, portion: str | float, unit: ServingUnit | str | None = None) -> Nutrients:
    """Return nutrients for a portion string or numeric quantity plus unit."""
    if isinstance(portion, str):
        grams = parse_portion(portion, food)
    else:
        if unit is None:
            raise ValueError("A unit is required when portion is numeric.")
        grams = convert_quantity(float(portion), unit, food.default_serving)
    return food.nutrients_for_grams(grams)
