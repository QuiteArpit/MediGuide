"""Inference wrapper for the saved comparative heart-risk model."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import joblib
import numpy as np
import pandas as pd

from .data_prep import DEFAULT_DATA_PATH, FEATURE_NAMES


DEFAULT_MODEL_DIR = Path(__file__).parents[2] / "data" / "processed" / "heart_risk_model"


class HeartRiskPredictor:
    """Load persisted artifacts and produce supplementary risk estimates."""

    def __init__(self, model_dir: str | Path | None = None) -> None:
        directory = Path(model_dir) if model_dir is not None else DEFAULT_MODEL_DIR
        if not directory.is_dir():
            raise FileNotFoundError(f"Model artifact directory not found: {directory}")
        try:
            self.model = joblib.load(directory / "model.joblib")
            self.scaler = joblib.load(directory / "scaler.joblib")
            self.metadata = json.loads((directory / "metadata.json").read_text(encoding="utf-8"))
        except (OSError, ValueError, EOFError) as exc:
            raise ValueError(f"Could not load model artifacts from {directory}") from exc
        self.feature_names = tuple(self.metadata.get("feature_names", FEATURE_NAMES))
        if not self.feature_names:
            raise ValueError("Model metadata does not contain feature names.")

    def predict_risk(self, input_features: Mapping[str, float]) -> dict[str, Any]:
        """Return probability, qualitative label, and top model features."""
        missing = [name for name in self.feature_names if name not in input_features]
        if missing:
            raise ValueError(f"Missing input features: {missing}")
        try:
            values = [float(input_features[name]) for name in self.feature_names]
        except (TypeError, ValueError) as exc:
            raise ValueError("All clinical model inputs must be numeric.") from exc
        frame = pd.DataFrame([values], columns=self.feature_names)
        scaled = pd.DataFrame(
            self.scaler.transform(frame),
            columns=self.feature_names,
        )
        probability = float(np.clip(self.model.predict_proba(scaled)[0, 1], 1e-9, 1.0 - 1e-9))
        if probability < 1 / 3:
            label = "low"
        elif probability < 2 / 3:
            label = "moderate"
        else:
            label = "high"
        importances = self._feature_importances()
        return {
            "probability": probability,
            "risk_label": label,
            "feature_importances": importances,
            "supplementary_only": True,
            "safety_note": "This estimate cannot override rule-based emergency triage.",
        }

    def _feature_importances(self) -> list[dict[str, float | str]]:
        """Extract normalized absolute importance values where available."""
        if hasattr(self.model, "feature_importances_"):
            raw = np.asarray(self.model.feature_importances_, dtype=float)
        elif hasattr(self.model, "coef_"):
            raw = np.abs(np.asarray(self.model.coef_, dtype=float)[0])
        else:
            raw = np.zeros(len(self.feature_names), dtype=float)
        total = float(raw.sum())
        normalized = raw / total if total else raw
        pairs = [
            {"feature": name, "importance": float(value)}
            for name, value in zip(self.feature_names, normalized)
        ]
        return sorted(pairs, key=lambda item: float(item["importance"]), reverse=True)
