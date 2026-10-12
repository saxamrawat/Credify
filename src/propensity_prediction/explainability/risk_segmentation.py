"""Descriptive risk bands for ranking model probability estimates."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from propensity_prediction.data.build import build_processed_dataset
from propensity_prediction.data.split import split_dataset
from propensity_prediction.explainability.global_importance import (
    build_final_model,
    prepare_engineered_features,
)


DEFAULT_N_BANDS = 4
VALIDATION_RISK_BAND_CUT_POINTS = (
    0.08940226956400625,
    0.1444458140540088,
    0.26307539734969276,
)
VALIDATION_RISK_BAND_LABELS = (
    "Lower",
    "Moderate",
    "Elevated",
    "Highest",
)
VALIDATION_RISK_BAND_REFERENCE = (
    "Phase 6 validation probabilities from the locked HistGradientBoosting "
    "engineered-feature model"
)
VALIDATION_RISK_BAND_METHOD = "fixed_validation_cohort_quantiles"
RISK_LABELS_BY_COUNT = {
    1: ("Single score band",),
    2: ("Lower", "Higher"),
    3: ("Lower", "Moderate", "Higher"),
    4: ("Lower", "Moderate", "Elevated", "Highest"),
}


@dataclass(frozen=True)
class RiskBandDefinition:
    """Quantile-derived score cut points, fitted on a reference cohort."""

    edges: tuple[float, ...]
    labels: tuple[str, ...]
    requested_bands: int

    @property
    def cut_points(self) -> tuple[float, ...]:
        """Interior score boundaries, excluding open-ended endpoints."""
        return self.edges[1:-1]


def validation_risk_band_definition() -> RiskBandDefinition:
    """Return the fixed Phase 6 validation-cohort bands for inference scores.

    These descriptive cut points were fitted using validation predictions
    from the selected HistGradientBoosting model and verified against the
    packaged inference artifact. They do not define an action threshold.
    """
    return RiskBandDefinition(
        edges=(-np.inf, *VALIDATION_RISK_BAND_CUT_POINTS, np.inf),
        labels=VALIDATION_RISK_BAND_LABELS,
        requested_bands=DEFAULT_N_BANDS,
    )


@dataclass(frozen=True)
class RiskSegmentationResult:
    """Customer-level bands and descriptive validation summaries."""

    definition: RiskBandDefinition
    assignments: pd.DataFrame
    summary: pd.DataFrame


def fit_risk_bands(
    probabilities,
    n_bands: int = DEFAULT_N_BANDS,
) -> RiskBandDefinition:
    """Fit equal-frequency probability bands while keeping tied scores whole.

    Quantile cut points are calculated from the supplied reference
    probabilities (validation predictions in the phase workflow). If
    ties collapse quantiles, the actual number of bands is reduced.
    Open-ended first/last intervals make the definition usable for later
    scores outside the reference cohort's observed range.
    """
    scores = _validate_probabilities(probabilities)
    if n_bands <= 0 or n_bands > len(RISK_LABELS_BY_COUNT[4]):
        raise ValueError("n_bands must be between 1 and 4.")

    quantiles = np.linspace(0, 1, n_bands + 1)[1:-1]
    candidates = np.unique(np.quantile(scores, quantiles))
    interior = candidates[(candidates > scores.min()) & (candidates < scores.max())]
    edges = (-np.inf, *[float(value) for value in interior], np.inf)
    n_actual_bands = len(edges) - 1
    labels = RISK_LABELS_BY_COUNT[n_actual_bands]

    return RiskBandDefinition(
        edges=tuple(edges),
        labels=labels,
        requested_bands=n_bands,
    )


def assign_risk_bands(probabilities, definition: RiskBandDefinition) -> pd.Series:
    """Assign scores using a previously fitted definition."""
    scores = _validate_probabilities(probabilities)
    bands = pd.cut(
        scores,
        bins=definition.edges,
        labels=definition.labels,
        include_lowest=True,
        right=True,
        ordered=True,
    )
    return pd.Series(bands, name="risk_band")


def summarize_risk_bands(
    y_true,
    probabilities,
    definition: RiskBandDefinition,
    customer_ids=None,
) -> RiskSegmentationResult:
    """Create per-customer assignments and observed validation summaries."""
    scores = _validate_probabilities(probabilities)
    target = pd.Series(y_true).reset_index(drop=True)
    band_values = assign_risk_bands(scores, definition).reset_index(drop=True)
    if len(target) != len(scores):
        raise ValueError("y_true and probabilities must have equal lengths.")
    if target.isna().any() or not target.isin([0, 1]).all():
        raise ValueError("y_true must contain only non-missing binary values 0 and 1.")

    assignments = pd.DataFrame(
        {
            "probability": scores,
            "risk_band": band_values,
            "actual_default": target.astype(int),
        }
    )
    if customer_ids is not None:
        ids = pd.Series(customer_ids).reset_index(drop=True)
        if len(ids) != len(scores):
            raise ValueError("customer_ids must have the same length as probabilities.")
        assignments.insert(0, "ID", ids)

    summary = (
        assignments.groupby("risk_band", observed=True, sort=False)
        .agg(
            customer_count=("probability", "size"),
            min_predicted_probability=("probability", "min"),
            max_predicted_probability=("probability", "max"),
            mean_predicted_probability=("probability", "mean"),
            observed_default_count=("actual_default", "sum"),
            observed_default_rate=("actual_default", "mean"),
        )
        .reset_index()
    )
    return RiskSegmentationResult(
        definition=definition,
        assignments=assignments,
        summary=summary,
    )


def segment_validation_set(
    n_bands: int = DEFAULT_N_BANDS,
) -> RiskSegmentationResult:
    """Fit the selected model on training data and segment validation scores.

    The test partition is not accessed. The quantile definition and
    observed band rates are descriptive outputs on the validation set.
    """
    split = split_dataset(build_processed_dataset())
    model = build_final_model()
    X_train = prepare_engineered_features(split.X_train)
    X_validation = prepare_engineered_features(split.X_validation)
    model.fit(X_train, split.y_train)
    probabilities = model.predict_proba(X_validation)[:, 1]

    definition = fit_risk_bands(probabilities, n_bands=n_bands)
    result = summarize_risk_bands(
        split.y_validation.reset_index(drop=True),
        probabilities,
        definition,
        customer_ids=split.X_validation["ID"].reset_index(drop=True),
    )
    return RiskSegmentationResult(
        definition=definition,
        assignments=result.assignments,
        summary=result.summary,
    )


def _validate_probabilities(probabilities) -> np.ndarray:
    scores = np.asarray(probabilities, dtype=float).reshape(-1)
    if len(scores) == 0:
        raise ValueError("probabilities must contain at least one score.")
    if not np.isfinite(scores).all() or ((scores < 0) | (scores > 1)).any():
        raise ValueError("probabilities must be finite values between 0 and 1.")
    return scores


if __name__ == "__main__":
    result = segment_validation_set()
    print("Cut points:", result.definition.cut_points)
    print(result.summary.to_string(index=False))
