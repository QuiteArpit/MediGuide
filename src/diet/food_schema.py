"""Typed schema objects for the food and nutrition knowledge base."""

from __future__ import annotations

from dataclasses import dataclass, fields
from enum import Enum
from typing import Any, Mapping


class ServingUnit(str, Enum):
    """Supported household and metric serving units."""

    GRAM = "gram"
    ML = "ml"
    KATORI = "katori"
    CUP = "cup"
    PIECE = "piece"
    PLATE = "plate"
    TABLESPOON = "tablespoon"


@dataclass(frozen=True)
class Nutrients:
    """Heart-relevant nutrients represented per 100 grams of food."""

    calories_kcal: float = 0.0
    sodium_mg: float = 0.0
    saturated_fat_g: float = 0.0
    total_fat_g: float = 0.0
    dietary_fiber_g: float = 0.0
    carbohydrates_g: float = 0.0
    protein_g: float = 0.0
    potassium_mg: float = 0.0

    def __post_init__(self) -> None:
        if any(value < 0 for value in self.as_dict().values()):
            raise ValueError("Nutrient values cannot be negative.")

    def scaled(self, grams: float) -> "Nutrients":
        """Return nutrients for ``grams`` of this food."""
        if grams < 0:
            raise ValueError("A portion cannot have negative grams.")
        factor = grams / 100.0
        return Nutrients(*(getattr(self, field.name) * factor for field in fields(self)))

    def as_dict(self) -> dict[str, float]:
        """Return nutrient names and values as a serializable mapping."""
        return {field.name: float(getattr(self, field.name)) for field in fields(self)}

    def __add__(self, other: "Nutrients") -> "Nutrients":
        if not isinstance(other, Nutrients):
            return NotImplemented
        return Nutrients(*(getattr(self, field.name) + getattr(other, field.name) for field in fields(self)))


@dataclass(frozen=True)
class ServingSize:
    """A named serving and its gram equivalent."""

    unit_name: ServingUnit | str
    grams_equivalent: float

    def __post_init__(self) -> None:
        if self.grams_equivalent <= 0:
            raise ValueError("A serving must have a positive gram equivalent.")
        object.__setattr__(self, "unit_name", ServingUnit(self.unit_name))


@dataclass(frozen=True)
class FoodItem:
    """A food record with nutrients, portions, and searchable metadata."""

    id: str
    name: str
    category: str
    variants: tuple[str, ...]
    default_serving: ServingSize
    nutrients_per_100g: Nutrients
    tags: frozenset[str]
    source: str
    is_estimated: bool = True

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.name.strip():
            raise ValueError("Food id and name are required.")
        object.__setattr__(self, "variants", tuple(self.variants))
        object.__setattr__(self, "tags", frozenset(tag.strip().lower() for tag in self.tags if tag.strip()))

    def nutrients_for_grams(self, grams: float) -> Nutrients:
        """Calculate nutrients for a custom gram quantity."""
        return self.nutrients_per_100g.scaled(grams)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-friendly representation of this food."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "variants": list(self.variants),
            "default_serving": {
                "unit_name": self.default_serving.unit_name.value,
                "grams_equivalent": self.default_serving.grams_equivalent,
            },
            "nutrients_per_100g": self.nutrients_per_100g.as_dict(),
            "tags": sorted(self.tags),
            "source": self.source,
            "is_estimated": self.is_estimated,
        }


def nutrients_from_mapping(values: Mapping[str, float]) -> Nutrients:
    """Build nutrients from a mapping while accepting only schema fields."""
    allowed = {field.name for field in fields(Nutrients)}
    unknown = set(values) - allowed
    if unknown:
        raise ValueError(f"Unknown nutrient fields: {sorted(unknown)}")
    return Nutrients(**{key: float(value) for key, value in values.items()})

