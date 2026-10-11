import numpy as np
import pandas as pd
import pytest
from types import SimpleNamespace

from propensity_prediction.decision.ranking import (
    DEFAULT_CAPACITY_SCENARIOS,
    evaluate_risk_ranking,
    run_test_ranking_analysis,
    summarize_capacity_scenarios,
)


def test_ranking_curve_compares_risk_order_with_random_selection():
    result = evaluate_risk_ranking(
        y_true=np.array([1, 0, 1, 0]),
        probabilities=np.array([0.9, 0.8, 0.4, 0.1]),
    )

    curve = result.curve
    assert result.observation_count == 4
    assert result.default_count == 2
    assert result.population_default_rate == 0.5
    assert curve["capacity_fraction"].iloc[0] == 0.0
    assert curve["capacity_fraction"].iloc[-1] == 1.0
    assert curve["defaults_captured"].tolist() == [0, 1, 1, 2, 2]
    assert curve["default_capture_rate"].iloc[1] == 0.5
    assert curve["random_expected_capture_rate"].tolist() == [0, .25, .5, .75, 1]
    assert curve["lift_over_random"].iloc[1] == 2.0
    assert curve["lift_over_random"].iloc[-1] == 1.0


def test_equal_scores_are_kept_as_one_selection_group():
    result = evaluate_risk_ranking(
        pd.Series([1, 0, 1, 0]), pd.Series([0.8, 0.8, 0.2, 0.2])
    )

    assert result.curve["selected_count"].tolist() == [0, 2, 4]
    assert result.curve["defaults_captured"].tolist() == [0, 1, 2]
    assert result.curve["capacity_fraction"].tolist() == [0.0, 0.5, 1.0]


@pytest.mark.parametrize(
    "outcomes, scores, message",
    [
        ([0, 1], [0.2], "equal non-zero lengths"),
        ([0, 2], [0.2, 0.8], "binary values"),
        ([0, 1], [0.2, np.nan], "finite values"),
        ([0, 1], [0.2, 1.2], "between 0 and 1"),
        ([[0, 1]], [[0.2, 0.8]], "one-dimensional"),
    ],
)
def test_ranking_evaluation_rejects_invalid_inputs(outcomes, scores, message):
    with pytest.raises(ValueError, match=message):
        evaluate_risk_ranking(outcomes, scores)


def test_no_default_population_has_undefined_capture_and_lift():
    result = evaluate_risk_ranking([0, 0, 0], [0.9, 0.5, 0.1])

    assert result.default_count == 0
    assert result.curve["default_capture_rate"].isna().all()
    assert result.curve["lift_over_random"].isna().all()


def test_default_capacity_scenarios_compare_with_random_at_each_capacity():
    outcomes = np.array([1] * 20 + [0] * 80)
    scores = np.arange(100, 0, -1) / 100
    evaluation = evaluate_risk_ranking(outcomes, scores)

    scenarios = summarize_capacity_scenarios(evaluation)

    assert DEFAULT_CAPACITY_SCENARIOS == (0.05, 0.10, 0.20)
    assert scenarios["target_review_count"].tolist() == [5, 10, 20]
    assert scenarios["selected_count"].tolist() == [5, 10, 20]
    assert scenarios["defaults_captured"].tolist() == [5, 10, 20]
    assert scenarios["default_capture_rate"].tolist() == [0.25, 0.5, 1.0]
    assert scenarios["random_expected_defaults"].tolist() == [1, 2, 4]
    assert scenarios["lift_over_random"].tolist() == [5, 5, 5]


def test_capacity_scenario_does_not_split_a_score_tie_or_exceed_capacity():
    outcomes = [1, 0, 1, 0, 1, 0, 1, 0]
    scores = [0.9, 0.9, 0.9, 0.9, 0.5, 0.5, 0.1, 0.1]
    evaluation = evaluate_risk_ranking(outcomes, scores)

    scenarios = summarize_capacity_scenarios(evaluation, (0.25, 0.50))

    assert scenarios["target_review_count"].tolist() == [2, 4]
    assert scenarios["selected_count"].tolist() == [0, 4]
    assert scenarios["capacity_unused_count"].tolist() == [2, 0]
    assert (scenarios["selected_count"] <= scenarios["target_review_count"]).all()


@pytest.mark.parametrize("capacities", [(), (0.0,), (1.1,), (np.nan,)])
def test_capacity_scenarios_reject_invalid_capacity_values(capacities):
    evaluation = evaluate_risk_ranking([0, 1], [0.2, 0.8])

    with pytest.raises(ValueError, match="capacit"):
        summarize_capacity_scenarios(evaluation, capacities)


def test_test_analysis_uses_selected_model_and_test_partition_only(monkeypatch):
    from propensity_prediction.data import build, split
    from propensity_prediction.models import final_selection

    X_test = pd.DataFrame({"ID": np.arange(20)})
    y_test = pd.Series([1] * 6 + [0] * 14, name="DEFAULT")
    dataset_split = SimpleNamespace(X_test=X_test, y_test=y_test)

    class FixedProbabilityModel:
        def predict_proba(self, X):
            scores = np.linspace(0.99, 0.01, len(X))
            return np.column_stack([1 - scores, scores])

    selection = {
        "validation_results": pd.DataFrame(
            [{"model": "chosen", "feature_set": "original", "pr_auc": 0.5, "roc_auc": 0.7}]
        ),
        "searches": {
            "chosen_original": SimpleNamespace(best_estimator_=FixedProbabilityModel())
        },
    }
    monkeypatch.setattr(build, "build_processed_dataset", lambda: object())
    monkeypatch.setattr(split, "split_dataset", lambda _: dataset_split)
    monkeypatch.setattr(
        final_selection,
        "_prepare_features",
        lambda X, use_engineered: (X.copy(), [], [], []),
    )

    result = run_test_ranking_analysis(selection)

    assert result["selected_model"] == "chosen"
    assert result["feature_set"] == "original"
    assert result["evaluation"].observation_count == len(X_test)
    assert result["evaluation"].default_count == int(y_test.sum())
    assert result["test_metrics"]["roc_auc"] == 1.0
    assert result["capacity_scenarios"]["target_review_count"].tolist() == [1, 2, 4]
