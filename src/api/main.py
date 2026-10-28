"""FastAPI application for MediGuide screening and diet services."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from src.diet import DietEngine, DietaryProfile
from src.models import HeartRiskPredictor
from src.triage import DEFAULT_QUESTIONNAIRE, UserAnswers, run_triage

from .schemas import (
    DietPlanRequest,
    DietPlanResponse,
    FoodQueryRequest,
    FoodQueryResponse,
    HealthResponse,
    QuestionnaireResponse,
    ScreeningRequest,
    ScreeningResponse,
)


APP_VERSION = "0.1.0"
app = FastAPI(
    title="MediGuide API",
    version=APP_VERSION,
    description="Educational cardiovascular screening and heart-diet guidance API.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://0.0.0.0:5500",
    ],
    allow_origin_regex=r"http://(localhost|127\.0\.0\.1|0\.0\.0\.0):\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_diet_engine = DietEngine()


def _profile_from_request(request: FoodQueryRequest | DietPlanRequest) -> DietaryProfile:
    return DietaryProfile(
        heart_condition=request.heart_condition,
        hypertension=request.hypertension,
        diabetes=request.diabetes,
        diet_preference=request.diet_preference,
        calorie_target_kcal=getattr(request, "calorie_target_kcal", 2000.0),
        custom_sodium_limit_mg=request.custom_sodium_limit_mg,
    )


def _optional_ml_assessment(answers: dict[str, Any]) -> dict[str, Any] | None:
    """Use ML only when trained artifacts and all model features are supplied."""
    try:
        predictor = HeartRiskPredictor()
        return predictor.predict_risk(answers)
    except (FileNotFoundError, ValueError, KeyError, TypeError, OSError):
        return None


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Return a consistent error envelope for application errors."""
    detail = exc.detail if isinstance(exc.detail, dict) else {"message": str(exc.detail)}
    return JSONResponse(status_code=exc.status_code, content={"error": detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Return validation failures in the same structured error envelope."""
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed.",
                "details": exc.errors(),
            }
        },
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return API liveness information."""
    return HealthResponse(status="ok", service="mediguide-api", version=APP_VERSION)


@app.get("/questions", response_model=QuestionnaireResponse)
def questions() -> QuestionnaireResponse:
    """Return the public questionnaire structure."""
    question_list = []
    for question in DEFAULT_QUESTIONNAIRE.questions.values():
        question_list.append({
            "question_id": question.question_id,
            "text": question.text,
            "answer_type": question.answer_type,
            "options": [option.value for option in question.options],
            "required": question.required,
            "help_text": question.help_text,
        })
    return QuestionnaireResponse(questions=question_list)


@app.post("/screening", response_model=ScreeningResponse)
def screening(request: ScreeningRequest) -> ScreeningResponse:
    """Run red-flag triage before optionally attaching a model estimate."""
    result = run_triage(UserAnswers(request.answers))
    payload = result.to_dict()
    ml_assessment = None if result.red_flags.is_emergency else _optional_ml_assessment(request.answers)
    if result.red_flags.is_emergency:
        payload["explanation"] += " Emergency status overrides any supplementary model estimate."
    return ScreeningResponse(
        care_level=payload["care_level"],
        recommendation=payload["recommendation"],
        explanation=payload["explanation"],
        red_flags=payload["red_flags"],
        concern_score=payload["concern_score"],
        ml_assessment=ml_assessment,
        disclaimer=payload["disclaimer"],
    )


@app.post("/food-query", response_model=FoodQueryResponse)
def food_query(request: FoodQueryRequest) -> FoodQueryResponse:
    """Evaluate the requested food portion."""
    try:
        result = _diet_engine.evaluate_query(
            request.query,
            request.portion,
            _profile_from_request(request),
        )
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=404, detail={"code": "food_query_failed", "message": str(exc)}) from exc
    payload = result.to_dict()
    return FoodQueryResponse(**payload)


@app.post("/diet-plan", response_model=DietPlanResponse)
def diet_plan(request: DietPlanRequest) -> DietPlanResponse:
    """Generate an educational daily meal plan."""
    try:
        result = _diet_engine.generate_plan(_profile_from_request(request))
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail={"code": "diet_plan_failed", "message": str(exc)}) from exc
    return DietPlanResponse(**result.to_dict())
