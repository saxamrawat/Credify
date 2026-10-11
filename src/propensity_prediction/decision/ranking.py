"""Evaluate whether predicted risk ranks defaults ahead of random selection."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class RankingEvaluation:
    """Cumulative ranking curve and its population-level baseline details."""

    curve: pd.DataFrame
    population_default_rate: float
    observation_count: int
    default_count: int


DEFAULT_CAPACITY_SCENARIOS = (0.05, 0.10, 0.20)


def evaluate_risk_ranking(
    y_true: pd.Series | np.ndarray,
    probabilities: pd.Series | np.ndarray,
) -> RankingEvaluation:
    """Compare top-risk selection with random selection at every score tie.

    The curve advances by groups of equal probability so it never implies
    that customers with tied scores have a meaningful within-tie order.
    """
    outcomes = np.asarray(y_true)
    scores = np.asarray(probabilities, dtype=float)

    if outcomes.ndim != 1 or scores.ndim != 1:
        raise ValueError("y_true and probabilities must be one-dimensional.")
    if len(outcomes) == 0 or len(outcomes) != len(scores):
        raise ValueError("y_true and probabilities must have equal non-zero lengths.")
    if pd.isna(outcomes).any() or not np.isin(outcomes, [0, 1]).all():
        raise ValueError("y_true must contain only non-missing binary values 0 and 1.")
    if not np.isfinite(scores).all() or ((scores < 0) | (scores > 1)).any():
        raise ValueError("probabilities must be finite values between 0 and 1.")

    outcomes = outcomes.astype(int)
    order = np.argsort(-scores, kind="stable")
    sorted_scores = scores[order]
    sorted_outcomes = outcomes[order]
    group_ends = np.r_[
        np.flatnonzero(sorted_scores[:-1] != sorted_scores[1:]) + 1,
        len(sorted_scores),
    ]
    selected = group_ends
    captured_defaults = np.cumsum(sorted_outcomes)[group_ends - 1]
    default_total = int(outcomes.sum())
    row_count = len(outcomes)
    prevalence = default_total / row_count

    capacity = selected / row_count
    precision = captured_defaults / selected
    capture_rate = (
        captured_defaults / default_total
        if default_total
        else np.full(len(selected), np.nan)
    )
    lift = precision / prevalence if prevalence else np.full(len(selected), np.nan)

    curve = pd.DataFrame(
        {
            "selected_count": selected,
            "capacity_fraction": capacity,
            "minimum_selected_probability": sorted_scores[group_ends - 1],
            "defaults_captured": captured_defaults.astype(int),
            "precision": precision,
            "default_capture_rate": capture_rate,
            "lift_over_random": lift,
            "random_expected_defaults": capacity * default_total,
            "random_expected_capture_rate": capacity,
            "random_expected_precision": prevalence,
            "random_expected_lift": np.ones(len(selected)) if prevalence else np.nan,
        }
    )
    curve = pd.concat(
        [
            pd.DataFrame(
                [{
                    "selected_count": 0,
                    "capacity_fraction": 0.0,
                    "minimum_selected_probability": np.nan,
                    "defaults_captured": 0,
                    "precision": np.nan,
                    "default_capture_rate": 0.0 if default_total else np.nan,
                    "lift_over_random": np.nan,
                    "random_expected_defaults": 0.0,
                    "random_expected_capture_rate": 0.0,
                    "random_expected_precision": prevalence,
                    "random_expected_lift": 1.0 if prevalence else np.nan,
                }]
            ),
            curve,
        ],
        ignore_index=True,
    )
    return RankingEvaluation(curve, prevalence, row_count, default_total)


def summarize_capacity_scenarios(
    evaluation: RankingEvaluation,
    capacities: tuple[float, ...] = DEFAULT_CAPACITY_SCENARIOS,
) -> pd.DataFrame:
    """Summarize illustrative queue sizes without splitting tied risk scores.

    For each target capacity, select the largest complete score groups that
    fit within the requested count. The result may use less than the target
    capacity when the next tied group would exceed it.
    """
    if not capacities:
        raise ValueError("capacities must contain at least one fraction.")
    if any(not np.isfinite(value) or value <= 0 or value > 1 for value in capacities):
        raise ValueError("each capacity must be a finite fraction greater than 0 and at most 1.")

    curve = evaluation.curve
    rows = []
    for target_capacity in capacities:
        target_count = int(np.floor(evaluation.observation_count * target_capacity))
        eligible = curve.loc[curve["selected_count"] <= target_count]
        selected = eligible.iloc[-1]
        selected_count = int(selected["selected_count"])
        actual_capacity = selected_count / evaluation.observation_count
        rows.append(
            {
                "target_capacity_fraction": float(target_capacity),
                "target_review_count": target_count,
                "selected_count": selected_count,
                "actual_capacity_fraction": actual_capacity,
                "capacity_unused_count": target_count - selected_count,
                "defaults_captured": int(selected["defaults_captured"]),
                "precision": selected["precision"],
                "default_capture_rate": selected["default_capture_rate"],
                "lift_over_random": selected["lift_over_random"],
                "random_expected_defaults": actual_capacity * evaluation.default_count,
                "random_expected_capture_rate": actual_capacity,
            }
        )
    return pd.DataFrame(rows)


def run_validation_ranking_analysis(selection: dict) -> dict:
    """Evaluate the validation ranking of the model selected by final selection.

    The validation set is used to select the model in ``run_final_selection``;
    therefore this result is a descriptive development diagnostic, not an
    unbiased final performance estimate. The test set is not read or scored.
    """
    from propensity_prediction.data.build import build_processed_dataset
    from propensity_prediction.data.split import split_dataset
    from propensity_prediction.models.final_selection import _prepare_features

    validation_results = selection["validation_results"]
    selected_row = validation_results.sort_values(
        by=["pr_auc", "roc_auc"], ascending=False
    ).iloc[0]
    model_name = selected_row["model"]
    feature_set = selected_row["feature_set"]
    search = selection["searches"][f"{model_name}_{feature_set}"]

    split = split_dataset(build_processed_dataset())
    X_validation, _, _, _ = _prepare_features(
        split.X_validation, feature_set == "engineered"
    )
    probabilities = search.best_estimator_.predict_proba(X_validation)[:, 1]
    evaluation = evaluate_risk_ranking(split.y_validation, probabilities)
    capacity_scenarios = summarize_capacity_scenarios(evaluation)
    return {
        "selected_model": model_name,
        "feature_set": feature_set,
        "validation_selection_metrics": selected_row.to_dict(),
        "evaluation": evaluation,
        "capacity_scenarios": capacity_scenarios,
    }


def run_test_ranking_analysis(selection: dict) -> dict:
    """Score the locked selected model on the held-out test split once here.

    Model choice comes from the validation results in ``selection``. This
    function does not fit, tune, or choose a model using test data. The
    project already reported standard test metrics in Phase 5; this adds a
    secondary ranking analysis of the same held-out split.
    """
    from propensity_prediction.data.build import build_processed_dataset
    from propensity_prediction.data.split import split_dataset
    from propensity_prediction.models.final_selection import (
        _evaluate_probabilities,
        _prepare_features,
    )

    validation_results = selection["validation_results"]
    selected_row = validation_results.sort_values(
        by=["pr_auc", "roc_auc"], ascending=False
    ).iloc[0]
    model_name = selected_row["model"]
    feature_set = selected_row["feature_set"]
    search = selection["searches"][f"{model_name}_{feature_set}"]

    split = split_dataset(build_processed_dataset())
    X_test, _, _, _ = _prepare_features(split.X_test, feature_set == "engineered")
    probabilities = search.best_estimator_.predict_proba(X_test)[:, 1]
    metrics = _evaluate_probabilities(split.y_test, probabilities)
    evaluation = evaluate_risk_ranking(split.y_test, probabilities)
    capacity_scenarios = summarize_capacity_scenarios(evaluation)
    return {
        "selected_model": model_name,
        "feature_set": feature_set,
        "validation_selection_metrics": selected_row.to_dict(),
        "test_metrics": metrics,
        "evaluation": evaluation,
        "capacity_scenarios": capacity_scenarios,
    }
