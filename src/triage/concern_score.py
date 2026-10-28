"""Non-emergency concern scoring and care-level mapping."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .symptom_questionnaire import UserAnswers


CARE_LEVELS = ("self_monitor", "routine_checkup", "prompt_consultation", "urgent_consultation")


@dataclass(frozen=True)
class ConcernScoreResult:
    score: int
    care_level: str
    triggered_factors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"score": self.score, "care_level": self.care_level, "triggered_factors": list(self.triggered_factors)}


def _has(answers: UserAnswers, question_id: str, value: str) -> bool:
    answer = answers.get(question_id)
    if isinstance(answer, (list, tuple, set)):
        return value in answer
    return str(answer).casefold() == value.casefold()


def _contains(answers: UserAnswers, question_id: str, value: str) -> bool:
    answer = answers.get(question_id, [])
    return value.casefold() in str(answer).casefold()


def risk_factor_count(user_answers: UserAnswers) -> int:
    age = user_answers.get("Q19", 0)
    try:
        age_value = float(age)
    except (TypeError, ValueError):
        age_value = 0
    count = sum((
        age_value >= 55,
        _has(user_answers, "Q21", "Yes, currently"),
        _has(user_answers, "Q23", "Yes"),
        _contains(user_answers, "Q24", "High blood pressure"),
        _contains(user_answers, "Q24", "Diabetes"),
        _contains(user_answers, "Q24", "High cholesterol"),
        _contains(user_answers, "Q24", "Kidney disease"),
    ))
    height_weight = user_answers.get("Q25")
    if isinstance(height_weight, (list, tuple)) and len(height_weight) == 2:
        try:
            height, weight = float(height_weight[0]), float(height_weight[1])
            if height > 0 and weight / ((height / 100) ** 2) >= 25:
                count += 1
        except (TypeError, ValueError):
            pass
    return int(count)


def calculate_concern_score(user_answers: UserAnswers) -> ConcernScoreResult:
    """Calculate a transparent score; emergency rules are evaluated separately."""
    score = 0
    factors: list[str] = []
    def add(points: int, reason: str) -> None:
        nonlocal score
        score += points
        factors.append(reason)

    q07 = str(user_answers.get("Q07", "No chest discomfort"))
    if q07 in {"Pressure, squeezing, tightness or heaviness", "Not sure / something else"}:
        add(4, "pressure-type or unclear chest discomfort")
    elif q07 != "No chest discomfort":
        add(1, "chest discomfort pattern")
    if _has(user_answers, "Q09", "10 to 30 minutes") or _has(user_answers, "Q09", "More than 30 minutes"):
        add(3, "longer chest discomfort episodes")
    if _has(user_answers, "Q10", "Getting more frequent or easier to trigger recently"):
        add(4, "worsening symptom pattern")
    if _has(user_answers, "Q12", "Yes, often or getting worse"):
        add(4, "breathlessness at rest")
    if _has(user_answers, "Q13", "Walking on flat ground or climbing one flight of stairs"):
        add(6, "breathlessness with ordinary activity")
    elif _has(user_answers, "Q13", "Very light activity (a few steps, dressing, bathing)"):
        add(5, "breathlessness with very light activity")
    if _has(user_answers, "Q14", "I wake up at night gasping or breathless") or _has(user_answers, "Q14", "I cannot lie flat at all"):
        add(4, "breathing difficulty when lying down")
    if _has(user_answers, "Q15", "Frequent, or lasts several minutes"):
        add(3, "frequent or prolonged palpitations")
    if _has(user_answers, "Q16", "Often, or when exercising, or together with a racing heart") or _has(user_answers, "Q16", "I fainted in the last 4 weeks (not today)"):
        add(3, "concerning dizziness or recent fainting")
    if _has(user_answers, "Q17", "Severe tiredness that limits daily tasks"):
        add(3, "severe fatigue")
    if _has(user_answers, "Q18", "Both legs swollen most of the day, or swelling is increasing") or _has(user_answers, "Q18", "Only ONE leg is swollen, painful or red"):
        add(4, "significant or one-sided leg swelling")
    factors_count = risk_factor_count(user_answers)
    if factors_count:
        add(min(factors_count, 4), f"{factors_count} cardiovascular risk factor(s)")

    if factors_count and score == factors_count:
        level = "routine_checkup"
    elif score >= 8:
        level = "urgent_consultation"
    elif score >= 5:
        level = "prompt_consultation"
    elif score >= 2:
        level = "routine_checkup"
    else:
        level = "self_monitor"
    return ConcernScoreResult(score, level, factors)
