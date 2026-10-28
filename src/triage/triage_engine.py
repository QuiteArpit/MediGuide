"""Top-level orchestration for cardiovascular screening."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from .concern_score import ConcernScoreResult, calculate_concern_score
from .explanation_generator import DISCLAIMER, generate_explanation
from .red_flag_rules import RedFlagResult, evaluate_red_flags
from .symptom_questionnaire import UserAnswers


@dataclass(frozen=True)
class TriageResult:
    """Structured output for an individual screening session."""

    care_level: str
    recommendation: str
    explanation: str
    red_flags: RedFlagResult
    concern_score: ConcernScoreResult | None
    disclaimer: str = DISCLAIMER

    def to_dict(self) -> dict[str, Any]:
        return {
            "care_level": self.care_level,
            "recommendation": self.recommendation,
            "explanation": self.explanation,
            "red_flags": self.red_flags.to_dict(),
            "concern_score": self.concern_score.to_dict() if self.concern_score else None,
            "disclaimer": self.disclaimer,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


def run_triage(user_answers: UserAnswers) -> TriageResult:
    """Run red flags first, returning immediately for emergency patterns."""
    red_flags = evaluate_red_flags(user_answers)
    if red_flags.is_emergency:
        explanation = generate_explanation(red_flags, ConcernScoreResult(0, "urgent_consultation"))
        return TriageResult("emergency", red_flags.emergency_message, explanation, red_flags, None)
    score = calculate_concern_score(user_answers)
    recommendation = {
        "self_monitor": "Self-monitor and continue routine health checks.",
        "routine_checkup": "Arrange a routine checkup with a healthcare professional.",
        "prompt_consultation": "Arrange a prompt consultation with a healthcare professional.",
        "urgent_consultation": "Seek urgent medical assessment from a healthcare professional.",
    }[score.care_level]
    return TriageResult(score.care_level, recommendation, generate_explanation(red_flags, score), red_flags, score)

