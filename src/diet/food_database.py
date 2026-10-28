"""In-memory food knowledge base seeded with common Indian foods."""

from __future__ import annotations

import re
from collections.abc import Iterable

from .food_schema import FoodItem, Nutrients, ServingSize, ServingUnit


_SOURCE = "MediGuide Phase 3 seed data; estimated values for educational use"


def _food(
    food_id: str,
    name: str,
    category: str,
    grams: float,
    nutrients: tuple[float, ...],
    tags: Iterable[str],
    variants: tuple[str, ...] = (),
    unit: ServingUnit | None = None,
) -> FoodItem:
    if unit is None:
        unit = {
            "dal_pulses": ServingUnit.KATORI,
            "vegetables": ServingUnit.KATORI,
            "beverages": ServingUnit.CUP,
            "dairy": ServingUnit.CUP,
        }.get(category, ServingUnit.PIECE)
    return FoodItem(
        food_id, name, category, variants, ServingSize(unit, grams),
        Nutrients(*nutrients), frozenset(tags), _SOURCE, True,
    )


def seed_foods() -> tuple[FoodItem, ...]:
    """Return the versioned starter set of common Indian foods."""
    low = {"vegetarian"}
    foods = [
        ("roti", "Roti", "staples", 40, (120, 180, 0.4, 3, 2.5, 20, 4, 120), {"vegetarian", "high_fiber", "heart_healthy"}),
        ("rice", "Steamed rice", "staples", 150, (130, 1, 0.1, 0.3, 0.4, 28, 2.7, 35), low),
        ("paratha", "Plain paratha", "staples", 80, (260, 420, 3, 12, 3, 35, 6, 100), {"vegetarian", "high_sodium"}),
        ("idli", "Idli", "staples", 50, (145, 230, 0.2, 1, 1.5, 28, 4, 90), {"vegetarian", "heart_healthy"}),
        ("dosa", "Plain dosa", "staples", 100, (168, 240, 1, 5, 1.5, 28, 3.5, 90), {"vegetarian"}),
        ("poha", "Poha", "staples", 150, (150, 260, 1, 4, 2, 25, 3, 120), {"vegetarian", "heart_healthy"}),
        ("tadka_dal", "Tadka dal", "dal_pulses", 150, (125, 280, 1.5, 5, 5, 18, 6, 260), {"vegetarian", "high_fiber", "heart_healthy"}),
        ("rajma", "Rajma curry", "dal_pulses", 150, (140, 250, 0.5, 4, 6, 21, 8, 320), {"vegetarian", "high_fiber", "heart_healthy"}),
        ("chana", "Chana masala", "dal_pulses", 150, (165, 300, 1, 5, 7, 24, 8, 300), {"vegetarian", "high_fiber"}),
        ("moong_dal", "Moong dal", "dal_pulses", 150, (105, 220, 0.5, 3, 5, 15, 7, 280), {"vegetarian", "high_fiber", "heart_healthy"}),
        ("chole", "Chole", "dal_pulses", 150, (165, 330, 1.2, 6, 6, 24, 8, 300), {"vegetarian", "high_fiber"}),
        ("dal_makhani", "Dal makhani", "dal_pulses", 150, (180, 360, 3, 8, 5, 22, 7, 260), {"vegetarian", "high_saturated_fat"}),
        ("aloo_gobi", "Aloo gobi", "vegetables", 150, (110, 250, 1, 5, 3, 16, 3, 300), {"vegetarian"}),
        ("bhindi", "Bhindi masala", "vegetables", 150, (115, 230, 0.8, 5, 4, 14, 3, 350), {"vegetarian", "high_fiber"}),
        ("palak_paneer", "Palak paneer", "vegetables", 150, (180, 320, 5, 12, 3, 10, 8, 300), {"vegetarian", "high_saturated_fat"}),
        ("mix_veg", "Mixed vegetable curry", "vegetables", 150, (95, 220, 0.5, 4, 4, 13, 3, 330), {"vegetarian", "heart_healthy", "high_fiber"}),
        ("baingan_bharta", "Baingan bharta", "vegetables", 150, (100, 230, 0.7, 4, 4, 12, 2, 300), {"vegetarian", "high_fiber"}),
        ("lauki", "Lauki curry", "vegetables", 150, (70, 180, 0.3, 2, 2, 10, 2, 260), {"vegetarian", "heart_healthy"}),
        ("samosa", "Samosa", "snacks", 60, (260, 480, 4, 16, 2, 30, 5, 170), {"vegetarian", "fried", "high_sodium"}),
        ("pakora", "Pakora", "snacks", 100, (280, 520, 3, 18, 3, 28, 6, 180), {"vegetarian", "fried", "high_sodium"}),
        ("biscuit", "Salted biscuit", "packaged_snacks", 30, (480, 650, 6, 20, 2, 68, 7, 120), {"vegetarian", "processed", "high_sodium"}),
        ("namkeen", "Namkeen mixture", "packaged_snacks", 30, (520, 900, 7, 30, 4, 52, 12, 350), {"vegetarian", "processed", "high_sodium", "fried"}),
        ("chips", "Potato chips", "packaged_snacks", 30, (540, 500, 7, 34, 4, 50, 6, 450), {"vegetarian", "processed", "high_sodium", "fried"}),
        ("roasted_makhana", "Roasted makhana", "snacks", 30, (350, 180, 0.5, 1, 7, 78, 9, 500), {"vegetarian", "high_fiber", "heart_healthy"}),
        ("peanuts", "Roasted peanuts", "snacks", 30, (567, 5, 6, 49, 9, 16, 26, 700), {"vegetarian", "high_fiber", "heart_healthy"}),
        ("dahi", "Plain curd", "dairy", 150, (60, 45, 1.5, 3, 0, 5, 3.5, 155), {"vegetarian", "heart_healthy"}),
        ("milk", "Low-fat milk", "dairy", 200, (50, 50, 1.5, 2, 0, 5, 3.4, 150), {"vegetarian"}),
        ("paneer", "Paneer", "dairy", 50, (265, 22, 18, 20, 0, 4, 18, 100), {"vegetarian", "high_saturated_fat"}),
        ("masala_chai", "Masala chai with milk", "beverages", 200, (45, 35, 1.5, 1.5, 0, 8, 2, 90), {"vegetarian"}),
        ("lassi", "Sweet lassi", "beverages", 250, (80, 45, 2.5, 3, 0, 12, 3, 140), {"vegetarian"}),
        ("buttermilk", "Buttermilk", "beverages", 250, (25, 55, 0.5, 0.8, 0, 3, 1.5, 100), {"vegetarian", "heart_healthy"}),
        ("coconut_water", "Coconut water", "beverages", 250, (19, 105, 0, 0, 1.1, 4, 0.7, 250), {"vegetarian", "heart_healthy"}),
        ("apple", "Apple", "fruits", 150, (52, 1, 0, 0.2, 2.4, 14, 0.3, 107), {"vegetarian", "high_fiber", "heart_healthy"}),
        ("banana", "Banana", "fruits", 120, (89, 1, 0.1, 0.3, 2.6, 23, 1.1, 358), {"vegetarian", "high_fiber", "heart_healthy"}),
        ("orange", "Orange", "fruits", 150, (47, 0, 0, 0.1, 2.4, 12, 0.9, 181), {"vegetarian", "high_fiber", "heart_healthy"}),
        ("guava", "Guava", "fruits", 100, (68, 2, 0.3, 1, 5.4, 14, 2.6, 417), {"vegetarian", "high_fiber", "heart_healthy"}),
        ("almonds", "Almonds", "nuts", 30, (579, 1, 4.5, 50, 12.5, 22, 21, 733), {"vegetarian", "high_fiber", "heart_healthy"}),
        ("walnuts", "Walnuts", "nuts", 30, (654, 2, 6, 65, 6.7, 14, 15, 441), {"vegetarian", "high_fiber", "heart_healthy"}),
        ("flaxseeds", "Flaxseeds", "seeds", 15, (534, 30, 3.7, 42, 27, 29, 18, 813), {"vegetarian", "high_fiber", "heart_healthy"}),
        ("oats", "Oats porridge", "breakfast", 200, (70, 30, 0.5, 2, 2, 12, 2.5, 100), {"vegetarian", "high_fiber", "heart_healthy"}),
        ("upma", "Vegetable upma", "breakfast", 150, (140, 230, 1, 4, 2, 24, 4, 130), {"vegetarian"}),
        ("sprouts", "Moong sprouts", "breakfast", 100, (30, 10, 0.1, 0.2, 1.8, 6, 3, 150), {"vegetarian", "high_fiber", "heart_healthy"}),
        ("chicken_curry", "Chicken curry", "non_vegetarian", 150, (180, 320, 3, 11, 0, 5, 20, 260), {"high_sodium"}),
        ("grilled_fish", "Grilled fish", "non_vegetarian", 120, (150, 180, 2, 7, 0, 0, 22, 350), {"heart_healthy"}),
        ("egg", "Boiled egg", "non_vegetarian", 50, (155, 125, 3.3, 11, 0, 1, 13, 126), set()),
    ]
    return tuple(_food(*entry) for entry in foods)


def _normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


class FoodDatabase:
    """Searchable in-memory repository of :class:`FoodItem` records."""

    def __init__(self, foods: Iterable[FoodItem] | None = None) -> None:
        records = tuple(foods) if foods is not None else seed_foods()
        self._foods = {food.id: food for food in records}
        if len(self._foods) != len(records):
            raise ValueError("Food identifiers must be unique.")

    def get_food(self, food_id_or_name: str) -> FoodItem | None:
        """Return an exact id/name match, or ``None`` if it is not found."""
        if not isinstance(food_id_or_name, str) or not food_id_or_name.strip():
            return None
        key = _normalize(food_id_or_name)
        for food in self._foods.values():
            if _normalize(food.id) == key or _normalize(food.name) == key:
                return food
        return None

    def search_foods(self, query: str) -> list[FoodItem]:
        """Return exact, prefix, or substring matches ordered by relevance."""
        if not isinstance(query, str) or not query.strip():
            return []
        needle = _normalize(query)
        scored: list[tuple[int, FoodItem]] = []
        for food in self._foods.values():
            candidates = (_normalize(food.id), _normalize(food.name), *(_normalize(v) for v in food.variants))
            score: int | None = None
            if needle in candidates:
                score = 0
            elif any(candidate.startswith(needle) for candidate in candidates):
                score = 1
            elif any(needle in candidate for candidate in candidates):
                score = 2
            if score is not None:
                scored.append((score, food))
        return [food for _, food in sorted(scored, key=lambda pair: (pair[0], pair[1].name))]

    def filter_by_tag(self, tag: str) -> list[FoodItem]:
        """Return all foods carrying a case-insensitive nutritional tag."""
        if not isinstance(tag, str) or not tag.strip():
            return []
        normalized = tag.strip().lower()
        return sorted((food for food in self._foods.values() if normalized in food.tags), key=lambda food: food.name)

    def __len__(self) -> int:
        return len(self._foods)
