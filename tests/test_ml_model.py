"""Tests for the UCI heart-risk comparative model baseline."""

from pathlib import Path

import numpy as np

from src.models import (
    HeartRiskPredictor,
    load_and_clean_uci_data,
    prepare_train_test_data,
    save_model_artifacts,
    train_and_evaluate_models,
)


def _trained_artifacts(tmp_path: Path) -> Path:
    frame = load_and_clean_uci_data()
    x_train, x_test, y_train, y_test, scaler = prepare_train_test_data(frame)
    results = train_and_evaluate_models(x_train, x_test, y_train, y_test)
    save_model_artifacts(
        results["best_model"], scaler, list(x_train.columns), results, tmp_path
    )
    return tmp_path


def test_clean_loading_has_no_missing_values_and_binarizes_target():
    frame = load_and_clean_uci_data()
    assert not frame.isna().any().any()
    assert set(frame["num"].unique()) == {0, 1}
    assert len(frame) == 303


def test_training_produces_five_fold_and_holdout_metrics():
    frame = load_and_clean_uci_data()
    x_train, x_test, y_train, y_test, _ = prepare_train_test_data(frame)
    results = train_and_evaluate_models(x_train, x_test, y_train, y_test)
    model_names = {"logistic_regression", "random_forest"}
    assert model_names.issubset(results)
    for name in model_names:
        metrics = results[name]
        assert 0.0 <= metrics["cv_roc_auc"] <= 1.0
        assert 0.0 <= metrics["cv_recall"] <= 1.0
        assert 0.0 <= metrics["roc_auc"] <= 1.0
        assert 0.0 <= metrics["recall"] <= 1.0
    assert results["best_model_name"] in results["models"]


def test_saved_model_can_be_loaded_and_predicts_bounded_probability(tmp_path):
    artifact_dir = _trained_artifacts(tmp_path)
    predictor = HeartRiskPredictor(artifact_dir)
    result = predictor.predict_risk({
        "age": 55, "sex": 1, "cp": 2, "trestbps": 135, "chol": 230,
        "fbs": 0, "restecg": 0, "thalach": 145, "exang": 0, "oldpeak": 1.0,
        "slope": 2, "ca": 0, "thal": 3,
    })
    assert 0.0 < result["probability"] < 1.0
    assert result["risk_label"] in {"low", "moderate", "high"}
    assert result["feature_importances"]
    assert result["supplementary_only"] is True


def test_predictor_rejects_missing_features(tmp_path):
    predictor = HeartRiskPredictor(_trained_artifacts(tmp_path))
    try:
        predictor.predict_risk({"age": 50})
    except ValueError as exc:
        assert "Missing input features" in str(exc)
    else:
        raise AssertionError("Missing features should be rejected.")
