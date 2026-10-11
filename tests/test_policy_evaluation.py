import numpy as np
import pytest

from propensity_prediction.decision.policy_evaluation import (
    evaluate_review_capacity_policies,
)


def test_capacity_policies_compare_engine_queue_with_random_expectation():
    outcomes = np.array([1] * 20 + [0] * 80)
    scores = np.arange(100, 0, -1) / 100
    ids = np.arange(100)

    result = evaluate_review_capacity_policies(ids, scores, outcomes)

    scenarios = result.scenario_comparison
    assert result.observation_count == 100
    assert result.default_count == 20
    assert result.population_default_rate == 0.2
    assert scenarios["target_review_count"].tolist() == [5, 10, 20]
    assert scenarios["selected_count"].tolist() == [5, 10, 20]
    assert scenarios["defaults_captured"].tolist() == [5, 10, 20]
    assert scenarios["random_expected_defaults"].tolist() == [1, 2, 4]
    assert scenarios["additional_defaults_vs_random_expectation"].tolist() == [4, 8, 16]
    assert result.queues[0.05].customers.loc[lambda q: q["selected_for_review"], "customer_id"].tolist() == list(range(5))


def test_random_reference_uses_actual_workload_when_tie_causes_underfill():
    ids = np.arange(8)
    probabilities = [0.95, 0.8, 0.8, 0.7, 0.1, 0.05, 0.04, 0.03]
    outcomes = [1, 1, 0, 0, 1, 0, 1, 0]

    result = evaluate_review_capacity_policies(
        ids, probabilities, outcomes, capacities=(0.25, 0.50)
    )

    scenarios = result.scenario_comparison
    assert scenarios["target_review_count"].tolist() == [2, 4]
    assert scenarios["selected_count"].tolist() == [1, 4]
    assert scenarios["capacity_unused_count"].tolist() == [1, 0]
    assert scenarios["defaults_captured"].tolist() == [1, 2]
    assert scenarios["random_expected_defaults"].tolist() == [0.5, 2.0]
    assert scenarios["additional_defaults_vs_random_expectation"].tolist() == [0.5, 0.0]


@pytest.mark.parametrize(
    "ids, scores, outcomes, capacities, message",
    [
        ([1, 2], [0.1, 0.9], [0], (0.5,), "equal non-zero lengths"),
        ([1, 2], [0.1, 0.9], [0, 2], (0.5,), "binary values"),
        ([1, 2], [0.1, 0.9], [0, 1], (), "at least one"),
        ([1, 2], [0.1, 0.9], [0, 1], (0.0,), "capacity"),
        ([1, 2], [0.1, 0.9], [0, 1], (1.1,), "capacity"),
        ([1, 2], [0.1, 0.9], [0, 1], (np.nan,), "capacity"),
    ],
)
def test_policy_evaluation_rejects_invalid_inputs(ids, scores, outcomes, capacities, message):
    with pytest.raises(ValueError, match=message):
        evaluate_review_capacity_policies(ids, scores, outcomes, capacities)


def test_zero_selected_customers_have_undefined_precision():
    result = evaluate_review_capacity_policies(
        [1, 2, 3, 4], [0.9, 0.8, 0.7, 0.6], [1, 0, 1, 0], capacities=(0.1,)
    )

    scenario = result.scenario_comparison.iloc[0]
    assert scenario["target_review_count"] == 0
    assert scenario["selected_count"] == 0
    assert np.isnan(scenario["precision"])
    assert np.isnan(scenario["lift_over_random"])
