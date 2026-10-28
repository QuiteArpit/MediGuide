"""Acceptance tests for the Phase 8 evaluation suite."""

import json
from pathlib import Path

from reports.evaluation_suite import run_evaluation


def test_evaluation_runs_and_emergency_recall_is_100_percent():
    summary = run_evaluation()
    assert summary["triage"]["emergency_expected"] > 0
    assert summary["triage"]["emergency_recall"] == 1.0
    assert summary["triage"]["emergency_detected"] == summary["triage"]["emergency_expected"]


def test_evaluation_summary_is_persisted_with_diet_metrics():
    summary = run_evaluation()
    output = Path(__file__).parents[1] / "reports" / "evaluation_summary.json"
    assert output.is_file()
    persisted = json.loads(output.read_text(encoding="utf-8"))
    assert persisted["diet"]["plans_evaluated"] > 0
    assert 0.0 <= persisted["diet"]["sodium_compliance_rate"] <= 1.0
    assert "confusion_matrix" in persisted["triage"]
