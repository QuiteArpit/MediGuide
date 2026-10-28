"""HTTP contract tests for the FastAPI backend."""

from fastapi.testclient import TestClient

from src.api import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_questions_endpoint_returns_structured_questions():
    response = client.get("/questions")
    assert response.status_code == 200
    body = response.json()
    assert body["questions"]
    assert {"question_id", "text", "options"} <= body["questions"][0].keys()


def test_screening_emergency_returns_immediate_safe_response():
    response = client.post("/screening", json={"answers": {"Q01": "Yes"}})
    assert response.status_code == 200
    body = response.json()
    assert body["care_level"] == "emergency"
    assert body["red_flags"]["is_emergency"] is True
    assert body["ml_assessment"] is None
    assert "overrides" in body["explanation"]


def test_screening_non_emergency_has_score_and_optional_model():
    response = client.post("/screening", json={"answers": {"Q01": "No", "Q07": "No chest discomfort"}})
    assert response.status_code == 200
    body = response.json()
    assert body["care_level"] in {"self_monitor", "routine_checkup", "prompt_consultation", "urgent_consultation"}
    assert body["concern_score"] is not None
    assert "disclaimer" in body


def test_food_query_and_missing_food_errors():
    response = client.post("/food-query", json={"query": "samosa", "portion": "1 piece"})
    assert response.status_code == 200
    assert response.json()["suitability"] in {"suitable", "caution", "unsuitable"}
    missing = client.post("/food-query", json={"query": "does not exist", "portion": "1 piece"})
    assert missing.status_code == 404
    assert "error" in missing.json()


def test_diet_plan_returns_structured_low_sodium_plan():
    response = client.post("/diet-plan", json={"heart_condition": True, "hypertension": True, "diet_preference": "vegetarian"})
    assert response.status_code == 200
    body = response.json()
    assert body["meals"]
    assert body["total_nutrients"]["sodium_mg"] <= 2000
    assert body["disclaimer"]


def test_invalid_requests_return_422():
    assert client.post("/food-query", json={"query": "", "portion": "1 piece"}).status_code == 422
    assert client.post("/diet-plan", json={"diet_preference": "invalid"}).status_code == 422
    assert client.post("/screening", json={"answers": {}}).status_code == 422
