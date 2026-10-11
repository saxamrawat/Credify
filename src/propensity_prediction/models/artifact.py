"""Build and load the selected model artifact for application inference."""

from __future__ import annotations

import json
import os
import warnings
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

from propensity_prediction.data.build import PROCESSED_DATA_PATH
from propensity_prediction.data.schema import get_feature_columns
from propensity_prediction.data.split import split_dataset
from propensity_prediction.models.final_selection import (
    RANDOM_STATE,
    _build_pipeline,
    prepare_model_features,
)


ARTIFACT_FORMAT_VERSION = 1
PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_ARTIFACT_RELATIVE_PATH = Path("models/selected_default_risk_model.joblib")


def _default_model_artifact_path() -> Path:
    """Resolve the artifact for source checkouts and regular package installs."""
    configured_path = os.getenv("PROPENSITY_MODEL_ARTIFACT_PATH")
    if configured_path:
        return Path(configured_path).expanduser()

    working_directory_path = Path.cwd() / MODEL_ARTIFACT_RELATIVE_PATH
    if working_directory_path.is_file():
        return working_directory_path

    return PROJECT_ROOT / MODEL_ARTIFACT_RELATIVE_PATH


DEFAULT_MODEL_ARTIFACT_PATH = _default_model_artifact_path()
LOCKED_MODEL_NAME = "hist_gradient_boosting"
LOCKED_FEATURE_SET = "engineered"
LOCKED_MODEL_PARAMS = {
    "l2_regularization": 1.0,
    "learning_rate": 0.05,
    "max_iter": 100,
    "max_leaf_nodes": 31,
}


def _package_version(distribution: str) -> str:
    try:
        return version(distribution)
    except PackageNotFoundError:
        return "not-installed"


def _json_value(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Cannot write {type(value).__name__} to model metadata JSON.")


def create_selected_model_artifact() -> dict:
    """Refit the locked Phase 5 winner on train rows and package it."""
    dataset = pd.read_csv(PROCESSED_DATA_PATH)
    split = split_dataset(dataset, random_state=RANDOM_STATE)
    train_X, numerical, categorical, ordinal = prepare_model_features(
        split.X_train,
        use_engineered_features=True,
    )
    estimator = HistGradientBoostingClassifier(random_state=RANDOM_STATE)
    estimator.set_params(**LOCKED_MODEL_PARAMS)
    pipeline = _build_pipeline(
        estimator,
        numerical_features=numerical,
        categorical_features=categorical,
        ordinal_features=ordinal,
    )
    pipeline.fit(train_X, split.y_train)

    metadata = {
        "artifact_format_version": ARTIFACT_FORMAT_VERSION,
        "project_version": "0.1.0",
        "model_name": LOCKED_MODEL_NAME,
        "feature_set": LOCKED_FEATURE_SET,
        "best_params": dict(LOCKED_MODEL_PARAMS),
        "selection_source": "Phase 5 final model selection report",
        "reported_cv_pr_auc": 0.5656,
        "reported_validation_pr_auc": 0.5501,
        "reported_validation_roc_auc": 0.7797,
        "reported_validation_brier_score": 0.1358,
        "random_state": RANDOM_STATE,
        "training_row_count": int(len(split.X_train)),
        "identifier_column": "ID",
        "feature_columns": get_feature_columns(),
        "uses_engineered_features": True,
        "training_boundary": (
            "Rebuilt using the locked Phase 5 parameters on the established "
            "training partition. The validation metrics are historical "
            "selection results; this exporter does not tune or score on the "
            "validation or test partitions."
        ),
        "package_versions": {
            "python": f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}.{__import__('sys').version_info.micro}",
            "numpy": _package_version("numpy"),
            "pandas": _package_version("pandas"),
            "scikit-learn": _package_version("scikit-learn"),
            "joblib": _package_version("joblib"),
        },
    }
    return {"metadata": metadata, "estimator": pipeline}


def save_model_artifact(
    model_artifact: dict,
    path: str | Path = DEFAULT_MODEL_ARTIFACT_PATH,
) -> tuple[Path, Path]:
    """Write the estimator bundle and a human-readable JSON metadata sidecar."""
    artifact_path = Path(path)
    metadata_path = artifact_path.with_suffix(".json")
    artifact_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_artifact = artifact_path.with_name(artifact_path.name + ".tmp")
    temporary_metadata = metadata_path.with_name(metadata_path.name + ".tmp")
    try:
        joblib.dump(model_artifact, temporary_artifact, compress=3)
        temporary_metadata.write_text(
            json.dumps(model_artifact["metadata"], indent=2, default=_json_value)
            + "\n"
        )
        temporary_artifact.replace(artifact_path)
        temporary_metadata.replace(metadata_path)
    finally:
        temporary_artifact.unlink(missing_ok=True)
        temporary_metadata.unlink(missing_ok=True)

    return artifact_path, metadata_path


def export_selected_model_artifact(
    path: str | Path = DEFAULT_MODEL_ARTIFACT_PATH,
) -> dict:
    """Fit the locked model configuration and persist the estimator bundle."""
    model_artifact = create_selected_model_artifact()
    artifact_path, metadata_path = save_model_artifact(model_artifact, path)
    return {
        "artifact_path": artifact_path,
        "metadata_path": metadata_path,
        "metadata": model_artifact["metadata"],
    }


def load_model_artifact(
    path: str | Path = DEFAULT_MODEL_ARTIFACT_PATH,
) -> dict:
    """Load a trusted local artifact and check its format and compatibility."""
    artifact_path = Path(path)
    if not artifact_path.is_file():
        raise FileNotFoundError(f"Model artifact does not exist: {artifact_path}")

    model_artifact = joblib.load(artifact_path)
    if not isinstance(model_artifact, dict):
        raise ValueError("Model artifact must contain a dictionary bundle.")
    if model_artifact.get("metadata", {}).get("artifact_format_version") != ARTIFACT_FORMAT_VERSION:
        raise ValueError("Unsupported model artifact format version.")
    estimator = model_artifact.get("estimator")
    if estimator is None or not hasattr(estimator, "predict_proba"):
        raise ValueError("Model artifact does not contain a probability estimator.")

    trained_sklearn = model_artifact["metadata"].get("package_versions", {}).get("scikit-learn")
    current_sklearn = _package_version("scikit-learn")
    if trained_sklearn and trained_sklearn != current_sklearn:
        warnings.warn(
            "Model artifact was created with scikit-learn "
            f"{trained_sklearn}, but the current environment has {current_sklearn}. "
            "Serialized scikit-learn models are not guaranteed to be compatible "
            "across versions.",
            RuntimeWarning,
            stacklevel=2,
        )
    return model_artifact


def predict_default_probabilities(
    model_artifact: dict,
    customers: pd.DataFrame,
) -> np.ndarray:
    """Score customers using the packaged estimator and matching feature path."""
    metadata = model_artifact.get("metadata", {})
    if metadata.get("artifact_format_version") != ARTIFACT_FORMAT_VERSION:
        raise ValueError("Unsupported model artifact format version.")
    feature_set = metadata.get("feature_set")
    if feature_set not in {"original", "engineered"}:
        raise ValueError("Model artifact has an unsupported feature_set.")

    model_inputs, _, _, _ = prepare_model_features(
        customers,
        use_engineered_features=(feature_set == "engineered"),
    )
    probabilities = np.asarray(
        model_artifact["estimator"].predict_proba(model_inputs),
        dtype=float,
    )
    classes = np.asarray(model_artifact["estimator"].classes_)
    positive_class_indices = np.flatnonzero(classes == 1)
    if probabilities.ndim != 2 or len(positive_class_indices) != 1:
        raise ValueError("Estimator did not return a binary default probability column.")

    scores = probabilities[:, int(positive_class_indices[0])]
    if len(scores) != len(customers) or not np.isfinite(scores).all():
        raise ValueError("Estimator returned invalid prediction probabilities.")
    if ((scores < 0) | (scores > 1)).any():
        raise ValueError("Estimator probabilities must be between 0 and 1.")
    return scores


if __name__ == "__main__":
    export = export_selected_model_artifact()
    print(f"Model artifact: {export['artifact_path']}")
    print(f"Metadata: {export['metadata_path']}")
    print(
        "Selected: "
        f"{export['metadata']['model_name']} "
        f"with {export['metadata']['feature_set']} features"
    )
