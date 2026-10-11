"""Evaluate capacity-based review queues against random selection."""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Real

import numpy as np
import pandas as pd

from propensity_prediction.decision.engine import (
    ReviewQueueResult,
    build_review_queue,
)
from propensity_prediction.decision.ranking import DEFAULT_CAPACITY_SCENARIOS


@dataclass(frozen=True)
class PolicyEvaluationResult:
    """Scenario comparisons, constructed queues, and population reference."""

    scenario_comparison: pd.DataFrame
    queues: dict[float, ReviewQueueResult]
    population_default_rate: float
    observation_count: int
    default_count: int


def evaluate_review_capacity_policies(
    customer_ids: pd.Series | np.ndarray,
    probabilities: pd.Series | np.ndarray,
    y_true: pd.Series | np.ndarray,
    capacities: tuple[float, ...] = DEFAULT_CAPACITY_SCENARIOS,
) -> PolicyEvaluationResult:
    """Evaluate engine-built queues versus random selection at equal workload.

    Random expected defaults are calculated at the queue's actual selected
    count. This keeps the comparison fair if tied scores cause the queue to
    use less than its requested capacity.
    """
    ids = np.asarray(customer_ids)
    outcomes = np.asarray(y_true)
    scores = np.asarray(probabilities, dtype=float)

    if ids.ndim != 1 or scores.ndim != 1 or outcomes.ndim != 1:
        raise ValueError("customer_ids, probabilities, and y_true must be one-dimensional.")
    if len(outcomes) == 0 or len(outcomes) != len(ids):
        raise ValueError("customer_ids and y_true must have equal non-zero lengths.")
    if pd.isna(outcomes).any() or not np.isin(outcomes, [0, 1]).all():
        raise ValueError("y_true must contain only non-missing binary values 0 and 1.")
    if not capacities:
        raise ValueError("capacities must contain at least one fraction.")
    if any(
        isinstance(capacity, (bool, np.bool_))
        or not isinstance(capacity, Real)
        or not np.isfinite(capacity)
        or capacity <= 0
        or capacity > 1
        for capacity in capacities
    ):
        raise ValueError("each capacity must be a finite fraction greater than 0 and at most 1.")

    outcomes = outcomes.astype(int)
    row_count = len(outcomes)
    default_count = int(outcomes.sum())
    prevalence = default_count / row_count
    outcome_by_id = pd.Series(outcomes, index=ids)
    scenario_rows = []
    queues = {}

    for capacity in capacities:
        capacity = float(capacity)
        target_count = int(np.floor(row_count * capacity))
        queue_result = build_review_queue(ids, scores, target_count)
        queues[capacity] = queue_result

        selected_ids = queue_result.customers.loc[
            queue_result.customers["selected_for_review"], "customer_id"
        ]
        selected_outcomes = outcome_by_id.loc[selected_ids.to_numpy()].to_numpy()
        captured_defaults = int(selected_outcomes.sum())
        selected_count = queue_result.selected_count
        actual_capacity = selected_count / row_count
        precision = captured_defaults / selected_count if selected_count else np.nan
        capture_rate = (
            captured_defaults / default_count
            if default_count
            else np.nan
        )
        lift = precision / prevalence if selected_count and prevalence else np.nan
        random_expected_defaults = actual_capacity * default_count

        scenario_rows.append(
            {
                "target_capacity_fraction": capacity,
                "target_review_count": queue_result.target_review_count,
                "selected_count": selected_count,
                "actual_capacity_fraction": actual_capacity,
                "capacity_unused_count": queue_result.unused_capacity,
                "defaults_captured": captured_defaults,
                "precision": precision,
                "default_capture_rate": capture_rate,
                "lift_over_random": lift,
                "random_expected_defaults": random_expected_defaults,
                "random_expected_capture_rate": actual_capacity,
                "random_expected_precision": prevalence,
                "additional_defaults_vs_random_expectation": (
                    captured_defaults - random_expected_defaults
                ),
            }
        )

    return PolicyEvaluationResult(
        scenario_comparison=pd.DataFrame(scenario_rows),
        queues=queues,
        population_default_rate=prevalence,
        observation_count=row_count,
        default_count=default_count,
    )
