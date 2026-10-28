"""Train, compare, evaluate, and persist baseline heart-risk models."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_validate

from .data_prep import FEATURE_NAMES


def _models(random_state: int = 42) -> dict[str, Any]:
    models: dict[str, Any] = {
        "logistic_regression": LogisticRegression(max_iter=2000, random_state=random_state),
        "random_forest": RandomForestClassifier(
            n_estimators=300, random_state=random_state, class_weight="balanced", n_jobs=-1
        ),
    }
    try:
        from xgboost import XGBClassifier

        models["xgboost"] = XGBClassifier(
            n_estimators=150,
            max_depth=3,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            eval_metric="logloss",
            random_state=random_state,
            n_jobs=1,
        )
    except ImportError:
        pass
    return models


def _probabilities(model: Any, x_test: pd.DataFrame) -> np.ndarray:
    probabilities = model.predict_proba(x_test)
    return np.asarray(probabilities)[:, 1]


def train_and_evaluate_models(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
) -> dict[str, Any]:
    """Train available baseline models with stratified five-fold CV.

    Returns per-model metrics plus the selected fitted model under the
    ``best_model`` and ``best_model_name`` keys.
    """
    if len(X_train) < 10 or len(X_test) < 2:
        raise ValueError("Insufficient rows for model training and evaluation.")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    results: dict[str, Any] = {}
    fitted: dict[str, Any] = {}
    for name, model in _models().items():
        scores = cross_validate(
            model,
            X_train,
            y_train,
            cv=cv,
            scoring={"roc_auc": "roc_auc", "recall": "recall"},
            error_score="raise",
        )
        model.fit(X_train, y_train)
        probabilities = _probabilities(model, X_test)
        predictions = (probabilities >= 0.5).astype(int)
        metrics = {
            "accuracy": float(accuracy_score(y_test, predictions)),
            "precision": float(precision_score(y_test, predictions, zero_division=0)),
            "recall": float(recall_score(y_test, predictions, zero_division=0)),
            "f1": float(f1_score(y_test, predictions, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_test, probabilities)),
            "cv_roc_auc": float(np.mean(scores["test_roc_auc"])),
            "cv_recall": float(np.mean(scores["test_recall"])),
        }
        results[name] = metrics
        fitted[name] = model
    best_name = max(
        results,
        key=lambda name: (results[name]["cv_roc_auc"], results[name]["cv_recall"]),
    )
    results["best_model_name"] = best_name
    results["best_model"] = fitted[best_name]
    results["models"] = fitted
    return results


def save_model_artifacts(
    model: Any,
    scaler: Any,
    feature_names: list[str] | tuple[str, ...],
    metrics: dict[str, Any],
    save_dir: str | Path,
) -> Path:
    """Save model, scaler, and JSON metadata in a portable artifact directory."""
    directory = Path(save_dir)
    directory.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, directory / "model.joblib")
    joblib.dump(scaler, directory / "scaler.joblib")
    serializable_metrics = {
        key: value for key, value in metrics.items()
        if key not in {"best_model", "models"} and isinstance(value, (dict, str, int, float, bool, list, tuple))
    }
    metadata = {
        "feature_names": list(feature_names),
        "metrics": serializable_metrics,
        "model_type": type(model).__name__,
        "supplementary_only": True,
        "safety_note": "This model must not override rule-based emergency triage.",
    }
    (directory / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return directory

