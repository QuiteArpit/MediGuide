"""Human-readable, safety-oriented explanations."""

from __future__ import annotations

from .concern_score import ConcernScoreResult
from .red_flag_rules import RedFlagResult


DISCLAIMER = (
    "This is educational screening information and not a substitute for "
    "examination or advice from a healthcare professional."
)


def generate_explanation(red_flags: RedFlagResult, score: ConcernScoreResult) -> str:
    """Explain the selected care level without making a clinical claim."""
    if red_flags.is_emergency:
        rules = ", ".join(red_flags.triggered_rules)
        return f"Emergency warning pattern(s) triggered: {rules}. Seek emergency care now. {DISCLAIMER}"
    if score.triggered_factors:
        reasons = "; ".join(score.triggered_factors)
        return f"The recommendation is based on: {reasons}. Please consult a healthcare professional as indicated. {DISCLAIMER}"
    return f"No concern factors were selected in the answers provided. Continue routine health checks and monitor for changes. {DISCLAIMER}"
