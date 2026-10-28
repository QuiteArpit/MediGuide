"""Deterministic emergency red-flag evaluation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .symptom_questionnaire import UserAnswers


@dataclass(frozen=True)
class RedFlagResult:
    """Result of evaluating emergency patterns."""

    is_emergency: bool
    triggered_rules: list[str] = field(default_factory=list)
    emergency_message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "is_emergency": self.is_emergency,
            "triggered_rules": list(self.triggered_rules),
            "emergency_message": self.emergency_message,
        }


EMERGENCY_MESSAGE = (
    "Emergency care is recommended now. Call your local emergency number "
    "(112/108 in India) or go to the nearest hospital. Do not drive yourself. "
    "This educational screening tool cannot assess an emergency safely online."
)


def _has(answers: UserAnswers, question_id: str, value: str) -> bool:
    answer = answers.get(question_id)
    if isinstance(answer, (list, tuple, set)):
        return value in answer
    return str(answer).strip().casefold() == value.casefold()


def _contains(answers: UserAnswers, question_id: str, value: str) -> bool:
    answer = answers.get(question_id, [])
    if isinstance(answer, str):
        return value.casefold() in answer.casefold()
    return any(value.casefold() in str(item).casefold() for item in answer)


def evaluate_red_flags(user_answers: UserAnswers) -> RedFlagResult:
    """Evaluate all emergency rules before any scoring or recommendation."""
    q12_positive = str(user_answers.get("Q12", "No"))
    q15_current = _has(user_answers, "Q15", "Happening right now and feels very fast or irregular")
    triggered: list[str] = []
    if _has(user_answers, "Q01", "Yes") and _has(user_answers, "Q02", "Yes"):
        triggered.append("RF-001")
    if _has(user_answers, "Q01", "Yes"):
        triggered.append("RF-002")
    if _has(user_answers, "Q06", "Yes, now or in the last hour"):
        triggered.append("RF-003")
    if _has(user_answers, "Q03", "Yes"):
        triggered.append("RF-004")
    if _has(user_answers, "Q04", "Yes") and (
        _has(user_answers, "Q01", "Yes") or _has(user_answers, "Q03", "Yes")
        or q12_positive != "No" or q15_current
    ):
        triggered.append("RF-005")
    if _has(user_answers, "Q04", "Yes"):
        triggered.append("RF-006")
    if _has(user_answers, "Q05", "Yes"):
        triggered.append("RF-007")
    if q15_current and (
        _has(user_answers, "Q01", "Yes") or _has(user_answers, "Q02", "Yes")
        or _has(user_answers, "Q03", "Yes") or q12_positive != "No"
        or _has(user_answers, "Q16", "Often, or when exercising, or together with a racing heart")
        or _has(user_answers, "Q16", "I fainted in the last 4 weeks (not today)")
    ):
        triggered.append("RF-008")
    if _contains(user_answers, "Q24", "Heart disease") and (
        _has(user_answers, "Q01", "Yes") or _has(user_answers, "Q02", "Yes") or _has(user_answers, "Q04", "Yes")
    ):
        triggered.append("RF-009")
    if any(_has(user_answers, question_id, "Not sure") for question_id in ("Q01", "Q02", "Q03", "Q04", "Q05", "Q06")):
        triggered.append("GR-002")
    # Preserve rule order and avoid duplicate identifiers.
    unique_rules = list(dict.fromkeys(triggered))
    return RedFlagResult(bool(unique_rules), unique_rules, EMERGENCY_MESSAGE if unique_rules else "")
