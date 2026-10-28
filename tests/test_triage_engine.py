"""Unit and scenario tests for the Phase 2 triage implementation."""

from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree

import pytest

from src.triage import UserAnswers, calculate_concern_score, evaluate_red_flags, run_triage


def baseline(**answers):
    values = {
        "Q01": "No", "Q02": "No", "Q03": "No", "Q04": "No", "Q05": "No", "Q06": "No",
        "Q07": "No chest discomfort", "Q09": "A few seconds (less than 1 minute)",
        "Q10": "This was the first time", "Q11": ["No clear trigger"], "Q12": "No",
        "Q13": "None, I breathe normally with everyday activity", "Q14": "No problem",
        "Q15": "Never", "Q16": "Never", "Q17": "No", "Q18": "No swelling", "Q19": 30,
        "Q20": "Prefer not to say", "Q21": "Never", "Q23": "No", "Q24": ["None of these"],
    }
    values.update(answers)
    return UserAnswers(values)


@pytest.mark.parametrize(("field", "value", "rule"), [
    ("Q01", "Yes", "RF-002"), ("Q03", "Yes", "RF-004"), ("Q04", "Yes", "RF-006"),
    ("Q05", "Yes", "RF-007"), ("Q06", "Yes, now or in the last hour", "RF-003"),
])
def test_each_primary_red_flag_returns_emergency(field, value, rule):
    result = evaluate_red_flags(baseline(**{field: value}))
    assert result.is_emergency
    assert rule in result.triggered_rules


def test_not_sure_red_flag_is_handled_conservatively():
    result = run_triage(baseline(Q01="Not sure"))
    assert result.care_level == "emergency"
    assert "GR-002" in result.red_flags.triggered_rules
    assert result.concern_score is None


@pytest.mark.parametrize(("answers", "level"), [
    ({}, "self_monitor"),
    ({"Q21": "Yes, currently"}, "routine_checkup"),
    ({"Q13": "Walking on flat ground or climbing one flight of stairs"}, "prompt_consultation"),
    ({"Q12": "Yes, often or getting worse", "Q13": "Walking on flat ground or climbing one flight of stairs"}, "urgent_consultation"),
])
def test_concern_score_maps_to_expected_level(answers, level):
    assert calculate_concern_score(baseline(**answers)).care_level == level


def test_emergency_overrides_non_emergency_scoring():
    result = run_triage(baseline(Q01="Yes", Q19=80, Q21="Yes, currently", Q24=["Heart disease"]))
    assert result.care_level == "emergency"
    assert result.concern_score is None
    assert "diagnose" not in result.to_json().lower()
    assert "confirm" not in result.to_json().lower()


def test_recommendations_have_disclaimer_and_structured_json():
    result = run_triage(baseline())
    payload = result.to_dict()
    assert payload["disclaimer"]
    assert payload["explanation"]
    assert result.to_json().startswith("{")


def test_phase1_workbook_is_available_for_data_driven_extension():
    workbook = Path(__file__).parents[1] / "docs" / "phase1_test_scenarios.xlsx"
    assert workbook.exists()


def _scenario_rows(workbook: Path):
    """Read the scenario sheet without requiring an optional spreadsheet package."""
    ns = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with ZipFile(workbook) as archive:
        shared_root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
        shared = ["".join(t.text or "" for t in item.iter("{%s}t" % ns["m"])) for item in shared_root.findall("m:si", ns)]
        sheet = ElementTree.fromstring(archive.read("xl/worksheets/sheet1.xml"))
        for row in sheet.findall(".//m:sheetData/m:row", ns):
            values = []
            for cell in row.findall("m:c", ns):
                value = cell.find("m:v", ns)
                text = "" if value is None else value.text or ""
                if cell.attrib.get("t") == "s":
                    text = shared[int(text)]
                values.append(text)
            if values and values[0].startswith("E"):
                yield values


@pytest.mark.parametrize("scenario", list(_scenario_rows(Path(__file__).parents[1] / "docs" / "phase1_test_scenarios.xlsx")))
def test_all_documented_emergency_scenarios_are_detected(scenario):
    """The documented emergency set must never be downgraded."""
    answer_text = scenario[6]
    answers = {}
    if "Q01=Yes" in answer_text or "Q01='Not sure'" in answer_text:
        answers["Q01"] = "Not sure" if "Q01='Not sure'" in answer_text else "Yes"
    if "Q02=Yes" in answer_text:
        answers["Q02"] = "Yes"
    if "Q03=Yes" in answer_text:
        answers["Q03"] = "Yes"
    if "Q04=Yes" in answer_text:
        answers["Q04"] = "Yes"
    if "Q05=Yes" in answer_text:
        answers["Q05"] = "Yes"
    if "Q06='Yes, now or in the last hour'" in answer_text:
        answers["Q06"] = "Yes, now or in the last hour"
    if "Q15='Happening right now" in answer_text:
        answers["Q15"] = "Happening right now and feels very fast or irregular"
    if "Q16='Often" in answer_text:
        answers["Q16"] = "Often, or when exercising, or together with a racing heart"
    if "Q12='Mild" in answer_text:
        answers["Q12"] = "Mild, only sometimes"
    result = run_triage(baseline(**answers))
    assert scenario[8] == "Emergency"
    assert result.care_level == "emergency", scenario[0]
