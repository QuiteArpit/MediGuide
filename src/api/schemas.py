"""Pydantic contracts for the MediGuide HTTP API."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


DietPreference = Literal["vegetarian", "non_vegetarian", "any"]


class ScreeningRequest(BaseModel):
    """Answers keyed by questionnaire identifier."""

    model_config = ConfigDict(extra="forbid")
    answers: dict[str, Any] = Field(min_length=1)


class FoodQueryRequest(BaseModel):
    """Food suitability query request."""

    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=1)
    portion: str = Field(min_length=1)
    heart_condition: bool = False
    hypertension: bool = False
    diabetes: bool = False
    diet_preference: DietPreference = "any"
    custom_sodium_limit_mg: float | None = Field(default=None, gt=0)

    @field_validator("query", "portion")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class DietPlanRequest(BaseModel):
    """Daily meal-plan request."""

    model_config = ConfigDict(extra="forbid")
    heart_condition: bool = False
    hypertension: bool = False
    diabetes: bool = False
    diet_preference: DietPreference = "any"
    calorie_target_kcal: float = Field(default=2000, gt=0)
    custom_sodium_limit_mg: float | None = Field(default=None, gt=0)


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class QuestionnaireResponse(BaseModel):
    questions: list[dict[str, Any]]


class ScreeningResponse(BaseModel):
    care_level: str
    recommendation: str
    explanation: str
    red_flags: dict[str, Any]
    concern_score: dict[str, Any] | None
    ml_assessment: dict[str, Any] | None
    disclaimer: str


class FoodQueryResponse(BaseModel):
    food_name: str
    portion_str: str
    suitability: str
    nutrient_impact: dict[str, dict[str, float]]
    advice: str
    healthier_alternatives: list[str]
    disclaimer: str


class DietPlanResponse(BaseModel):
    meals: dict[str, list[dict[str, Any]]]
    total_nutrients: dict[str, float]
    meets_targets: bool
    summary_notes: list[str]
    disclaimer: str

