"""Reproducible Phase 8 evaluation for triage, diet plans, and the ML baseline.

Run from the repository root with ``python reports/evaluation_suite.py``.
The evaluator uses the documented Phase 1 workbook and writes
``reports/evaluation_summary.json``.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterator
from zipfile import ZipFile
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.diet import DietaryProfile, FoodDatabase, generate_heart_meal_plan  # noqa: E402
from src.triage import UserAnswers, run_triage  # noqa: E402


WORKBOOK_CANDIDATES = (
    ROOT / "reports" / "phase1_test_scenarios.xlsx",
    ROOT / "docs" / "phase1_test_scenarios.xlsx",
)
CARE_LEVELS = ("emergency", "urgent_consultation", "prompt_consultation", "routine_checkup", "self_monitor")
BASELINE: dict[str, Any] = {
    "Q01": "No", "Q02": "No", "Q03": "No", "Q04": "No", "Q05": "No", "Q06": "No",
    "Q07": "No chest discomfort", "Q09": "A few seconds (less than 1 minute)",
    "Q10": "This was the first time", "Q11": ["No clear trigger"], "Q12": "No",
    "Q13": "None, I breathe normally with everyday activity", "Q14": "No problem",
    "Q15": "Never", "Q16": "Never", "Q17": "No", "Q18": "No swelling", "Q19": 30,
    "Q20": "Prefer not to say", "Q21": "Never", "Q22": "Never", "Q23": "No",
    "Q24": ["None of these"], "Q25": [170, 68],
}


def _column_letter(reference: str) -> int:
    letters = re.match(r"[A-Z]+", reference or "")
    if not letters:
        return 0
    result = 0
    for char in letters.group():
        result = result * 26 + ord(char) - 64
    return result - 1


def _workbook_rows(path: Path) -> Iterator[list[str]]:
    """Read shared-string worksheet cells without requiring openpyxl."""
    namespace = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with ZipFile(path) as archive:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = [
                "".join(t.text or "" for t in item.iter("{%s}t" % namespace["m"]))
                for item in root.findall("m:si", namespace)
            ]
        worksheet = ElementTree.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        for row in worksheet.findall(".//m:sheetData/m:row", namespace):
            cells: dict[int, str] = {}
            for cell in row.findall("m:c", namespace):
                value = cell.find("m:v", namespace)
                text = "" if value is None else value.text or ""
                if cell.attrib.get("t") == "s" and text:
                    text = shared[int(text)]
                cells[_column_letter(cell.attrib.get("r", ""))] = text
            if cells:
                yield [cells.get(index, "") for index in range(max(cells) + 1)]


def find_workbook() -> Path:
    """Return the first available documented scenario workbook."""
    for candidate in WORKBOOK_CANDIDATES:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("No phase1_test_scenarios.xlsx found in reports/ or docs/.")


def load_scenarios(path: Path | None = None) -> list[dict[str, str]]:
    """Load scenario rows as dictionaries keyed by workbook headers."""
    rows = iter(_workbook_rows(path or find_workbook()))
    headers = next(rows, [])
    if "scenario_id" not in headers:
        raise ValueError("Scenario workbook has no scenario_id header.")
    return [
        dict(zip(headers, row))
        for row in rows
        if row and row[0] and row[0] != "scenario_id"
    ]


def _set_answer(answers: dict[str, Any], key: str, value: str) -> None:
    if key == "Q11":
        answers[key] = [part.strip() for part in value.split("+")]
    elif key == "Q24":
        answers[key] = [part.strip() for part in value.split("+")]
    elif key == "Q25":
        match = re.search(r"BMI\s+(\d+(?:\.\d+)?)", value, re.I)
        bmi = float(match.group(1)) if match else 25.0
        answers[key] = [170, round(bmi * 1.7**2, 1)]
    elif key == "Q19":
        answers[key] = int(float(value))
    else:
        answers[key] = value.strip("'")


def scenario_answers(scenario: dict[str, str]) -> UserAnswers:
    """Translate a documented scenario's shorthand into triage answers."""
    answers = dict(BASELINE)
    answers["Q19"] = int(float(scenario.get("age") or 30))
    answers["Q20"] = {"M": "Male", "F": "Female"}.get(scenario.get("sex", ""), "Prefer not to say")
    if scenario.get("known_heart_disease") == "Yes":
        answers["Q24"] = ["Heart disease"]
    text = scenario.get("key answers (unlisted = baseline negative)", "")
    if "Q01-Q06='Not sure'" in text:
        for question_id in ("Q01", "Q02", "Q03", "Q04", "Q05", "Q06"):
            answers[question_id] = "Not sure"
    for match in re.finditer(r"(Q\d{2})=(?:'([^']*)'|([^;]+))", text):
        question_id = match.group(1)
        value = (match.group(2) or match.group(3) or "").strip()
        if value.startswith("includes "):
            value = value.removeprefix("includes ").strip("'")
        if value == "Yes (all others baseline)" or value == "Yes (others baseline)":
            value = "Yes"
        if value in {"Pressure...", "Sharp or stabbing...", "Burning...", "Q24 includes 'Heart disease'"}:
            value = {
                "Pressure...": "Pressure, squeezing, tightness or heaviness",
                "Sharp or stabbing...": "Sharp or stabbing pain lasting only seconds",
                "Burning...": "Burning feeling, often after eating or when lying down",
            }.get(value, value)
        value = {
            "Yes, now or in the last hour": "Yes, now or in the last hour",
            "Happening right now...": "Happening right now and feels very fast or irregular",
            "Often...": "Often, or when exercising, or together with a racing heart",
            "Mild, only sometimes": "Mild, only sometimes",
            "Q24 includes 'Heart disease'": "Heart disease",
            "Q24 includes 'Heart disease' + High BP": "Heart disease+High blood pressure",
            "Q24 includes 'Heart disease' + High cholesterol": "Heart disease+High cholesterol",
            "Q24=High BP": "High blood pressure",
            "Q24=Diabetes": "Diabetes or high blood sugar",
            "Q24=Diabetes + High cholesterol": "Diabetes or high blood sugar+High cholesterol",
            "Q24=High BP + Diabetes": "High blood pressure+Diabetes or high blood sugar",
        }.get(value, value)
        _set_answer(answers, question_id, value)
    # Explicit shorthand forms that are not direct Qxx=value expressions.
    if "Q24 includes 'Heart disease'" in text:
        answers["Q24"] = ["Heart disease"]
    if "Q24=High BP" in text:
        answers["Q24"] = ["High blood pressure"]
    if "Q24=Diabetes" in text:
        answers["Q24"] = ["Diabetes or high blood sugar"]
    if "Q24=Diabetes + High cholesterol" in text:
        answers["Q24"] = ["Diabetes or high blood sugar", "High cholesterol"]
    if "Q24=High BP + Diabetes" in text:
        answers["Q24"] = ["High blood pressure", "Diabetes or high blood sugar"]
    return UserAnswers(answers)


def evaluate_scenarios(scenarios: list[dict[str, str]]) -> dict[str, Any]:
    """Evaluate every scenario with a defined care-level expectation."""
    records: list[dict[str, Any]] = []
    emergency_expected = 0
    emergency_detected = 0
    confusion = {actual: {predicted: 0 for predicted in CARE_LEVELS} for actual in CARE_LEVELS}
    for scenario in scenarios:
        expected = (
            scenario.get("expected care level", "")
            .strip()
            .casefold()
            .replace(" ", "_")
            .replace("-", "_")
        )
        result = run_triage(scenario_answers(scenario))
        predicted = result.care_level
        is_emergency = expected == "emergency"
        if is_emergency:
            emergency_expected += 1
            emergency_detected += int(predicted == "emergency")
        if expected in CARE_LEVELS:
            confusion[expected][predicted] = confusion[expected].get(predicted, 0) + 1
        records.append({
            "scenario_id": scenario.get("scenario_id", ""),
            "expected_care_level": expected or "not_applicable",
            "predicted_care_level": predicted,
            "emergency_detected": predicted == "emergency",
            "agreement": expected == predicted if expected in CARE_LEVELS else None,
        })
    defined = [record for record in records if record["agreement"] is not None]
    non_emergency_defined = [
        record for record in defined if record["expected_care_level"] != "emergency"
    ]
    false_alarms = sum(
        record["predicted_care_level"] == "emergency"
        for record in non_emergency_defined
    )
    true_negatives = len(non_emergency_defined) - false_alarms
    return {
        "scenario_count": len(records),
        "care_level_defined_count": len(defined),
        "care_level_agreement": sum(record["agreement"] for record in defined) / len(defined) if defined else 0.0,
        "emergency_expected": emergency_expected,
        "emergency_detected": emergency_detected,
        "emergency_recall": emergency_detected / emergency_expected if emergency_expected else 0.0,
        "non_emergency_defined": len(non_emergency_defined),
        "false_alarms": false_alarms,
        "specificity": true_negatives / len(non_emergency_defined) if non_emergency_defined else 0.0,
        "confusion_matrix": confusion,
        "scenario_results": records,
    }


def evaluate_diet_plans() -> dict[str, Any]:
    """Generate representative plans and measure target compliance."""
    database = FoodDatabase()
    profiles = [
        DietaryProfile(heart_condition=True, hypertension=True, diet_preference="vegetarian"),
        DietaryProfile(heart_condition=True, diet_preference="non_vegetarian"),
        DietaryProfile(heart_condition=True, diabetes=True, diet_preference="any"),
    ]
    plans = [generate_heart_meal_plan(profile, database) for profile in profiles]
    compliant = sum(plan.total_nutrients.sodium_mg <= 2000 for plan in plans)
    return {
        "plans_evaluated": len(plans),
        "plans_under_2000mg_sodium": compliant,
        "sodium_compliance_rate": compliant / len(plans) if plans else 0.0,
        "plans_meet_all_targets": sum(plan.meets_targets for plan in plans),
        "plan_totals": [plan.total_nutrients.as_dict() for plan in plans],
    }


def evaluate_ml_availability() -> dict[str, Any]:
    """Report whether a persisted ML artifact is available for comparison."""
    artifact_dir = ROOT / "data" / "processed" / "heart_risk_model"
    available = all((artifact_dir / filename).is_file() for filename in ("model.joblib", "scaler.joblib", "metadata.json"))
    return {
        "available": available,
        "finding": (
            "ML artifacts were available for supplementary comparison."
            if available
            else "No persisted ML artifact was available; rule-only evaluation was run."
        ),
        "safety_constraint": "Rule-based red flags remain authoritative and cannot be overridden by ML.",
    }


def run_evaluation() -> dict[str, Any]:
    """Run the full evaluation and persist the JSON summary."""
    scenarios = load_scenarios()
    summary = {
        "evaluation": "MediGuide Phase 8",
        "workbook": str(find_workbook().relative_to(ROOT)),
        "triage": evaluate_scenarios(scenarios),
        "diet": evaluate_diet_plans(),
        "ml_comparison": evaluate_ml_availability(),
    }
    output = ROOT / "reports" / "evaluation_summary.json"
    output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    result = run_evaluation()
    print(json.dumps({
        "emergency_recall": result["triage"]["emergency_recall"],
        "care_level_agreement": result["triage"]["care_level_agreement"],
        "diet_sodium_compliance": result["diet"]["sodium_compliance_rate"],
        "summary_path": "reports/evaluation_summary.json",
    }, indent=2))
