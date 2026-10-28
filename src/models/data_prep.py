"""Data loading and preprocessing for the UCI Cleveland heart dataset."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


FEATURE_NAMES: tuple[str, ...] = (
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
)
TARGET_NAME = "num"
DEFAULT_DATA_PATH = Path(__file__).parents[2] / "data" / "raw" / "uci_heart" / "processed.cleveland.data"


def load_and_clean_uci_data(data_path: str | Path | None = None) -> pd.DataFrame:
    """Load, coerce, impute, and binarize the Cleveland dataset.

    The source file has no header. Missing ``?`` values are converted to NaN
    and median-imputed using the complete dataset before the target is split.
    """
    path = Path(data_path) if data_path is not None else DEFAULT_DATA_PATH
    if not path.is_file():
        raise FileNotFoundError(f"UCI data file not found: {path}")
    frame = pd.read_csv(path, header=None, names=[*FEATURE_NAMES, TARGET_NAME], na_values=["?"])
    if frame.empty or list(frame.columns) != [*FEATURE_NAMES, TARGET_NAME]:
        raise ValueError("The UCI file does not match the expected 14-column schema.")
    for column in frame.columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    if frame[TARGET_NAME].isna().any():
        raise ValueError("The target column contains missing or invalid values.")
    feature_columns = list(FEATURE_NAMES)
    frame[feature_columns] = frame[feature_columns].replace([np.inf, -np.inf], np.nan)
    frame[feature_columns] = frame[feature_columns].fillna(frame[feature_columns].median())
    frame[TARGET_NAME] = (frame[TARGET_NAME] > 0).astype("int64")
    if frame[feature_columns].isna().any().any():
        raise ValueError("Feature cleaning left missing values.")
    return frame


def prepare_train_test_data(
    df: pd.DataFrame,
    test_size: float = 0.2,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, StandardScaler]:
    """Split and standardize numeric features without leaking test statistics."""
    required = [*FEATURE_NAMES, TARGET_NAME]
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"Dataframe is missing columns: {sorted(missing)}")
    if not 0 < test_size < 1:
        raise ValueError("test_size must be between 0 and 1.")
    features = df.loc[:, list(FEATURE_NAMES)].astype(float)
    target = df[TARGET_NAME].astype(int)
    if features.isna().any().any() or target.isna().any():
        raise ValueError("Training data cannot contain missing values.")
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=test_size,
        random_state=random_state,
        stratify=target,
    )
    scaler = StandardScaler()
    x_train_scaled = pd.DataFrame(
        scaler.fit_transform(x_train),
        index=x_train.index,
        columns=FEATURE_NAMES,
    )
    x_test_scaled = pd.DataFrame(
        scaler.transform(x_test),
        index=x_test.index,
        columns=FEATURE_NAMES,
    )
    return x_train_scaled, x_test_scaled, y_train, y_test, scaler


def feature_defaults() -> dict[str, float]:
    """Return a documented, conservative feature template for callers."""
    return {
        "age": 50.0,
        "sex": 1.0,
        "cp": 1.0,
        "trestbps": 130.0,
        "chol": 220.0,
        "fbs": 0.0,
        "restecg": 0.0,
        "thalach": 150.0,
        "exang": 0.0,
        "oldpeak": 0.0,
        "slope": 1.0,
        "ca": 0.0,
        "thal": 3.0,
    }
