from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError

from propensity_prediction.api.errors import (
    InvalidPortfolioError,
    ModelArtifactUnavailable,
)
from propensity_prediction.api.repository import ModelArtifactRepository
from propensity_prediction.api.schemas import CustomerInput, ReviewQueueRequest, ReviewQueueResponse
from propensity_prediction.api.service import ReviewQueueService
from propensity_prediction.data.schema import get_feature_columns
from propensity_prediction.explainability.risk_segmentation import (
    VALIDATION_RISK_BAND_CUT_POINTS,
    fit_risk_bands,
    validation_risk_band_definition,
)
from propensity_prediction.limits import MAX_CUSTOMER_ROWS
from propensity_prediction.data.build import build_processed_dataset
from propensity_prediction.data.split import split_dataset
from propensity_prediction.models.artifact import (
    load_model_artifact,
    predict_default_probabilities,
)


def _customer(customer_id: int) -> dict:
    customer = {column: 100.0 for column in get_feature_columns()}
    customer.update(
        {
            "ID": customer_id,
            "LIMIT_BAL": 50000.0,
            "AGE": 35.0,
            "SEX": 2,
            "EDUCATION": 2,
            "MARRIAGE": 1,
            "PAY_0": 0,
            "PAY_2": 0,
            "PAY_3": 0,
            "PAY_4": 0,
            "PAY_5": 0,
            "PAY_6": 0,
        }
    )
    return customer


class InMemoryModelRepository:
    """Small repository double for deterministic service-level checks."""

    is_loaded = True

    def get_model_artifact(self) -> dict:
        return {"estimator": "model-double"}

    def get_explanation_background(self):
        return "training-reference"


def _build_service(monkeypatch: pytest.MonkeyPatch, scores: list[float]) -> ReviewQueueService:
    monkeypatch.setattr(
        "propensity_prediction.api.service.predict_default_probabilities",
        lambda _artifact, _customers: np.asarray(scores),
    )
    return ReviewQueueService(InMemoryModelRepository())


def test_request_schema_accepts_contract_customer_and_count() -> None:
    request = ReviewQueueRequest.model_validate(
        {"customers": [_customer(1001)], "max_review_count": 1}
    )

    assert request.customers[0].ID == 1001
    assert request.max_review_count == 1


@pytest.mark.parametrize(
    "payload",
    [
        {"customers": [{**_customer(1001), "DEFAULT": 0}], "max_review_count": 1},
        {
            "customers": [
                {key: value for key, value in _customer(1001).items() if key != "AGE"}
            ],
            "max_review_count": 1,
        },
        {"customers": [_customer(1001)], "max_review_count": True},
    ],
)
def test_request_schema_rejects_outcome_missing_field_and_boolean_count(payload: dict) -> None:
    with pytest.raises(ValidationError):
        ReviewQueueRequest.model_validate(payload)


def test_request_schema_accepts_maximum_portfolio_size() -> None:
    customer = _customer(1001)
    request = ReviewQueueRequest.model_validate(
        {"customers": [customer] * MAX_CUSTOMER_ROWS, "max_review_count": 1}
    )
    assert len(request.customers) == MAX_CUSTOMER_ROWS


def test_request_schema_rejects_portfolio_above_maximum() -> None:
    customer = _customer(1001)
    with pytest.raises(ValidationError, match="at most 30000 items"):
        ReviewQueueRequest.model_validate(
            {"customers": [customer] * (MAX_CUSTOMER_ROWS + 1), "max_review_count": 1}
        )


def test_service_returns_full_portfolio_sorted_with_capacity_summary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _build_service(monkeypatch, [0.2, 0.9, 0.5])
    request = ReviewQueueRequest.model_validate(
        {
            "customers": [_customer(1001), _customer(1002), _customer(1003)],
            "max_review_count": 2,
        }
    )

    result = service.build_queue(request)
    response = ReviewQueueResponse.model_validate(result)

    assert response.population_count == 3
    assert result["capacity"] == {
        "requested_review_count": 2,
        "target_review_count": 2,
        "selected_count": 2,
        "unused_capacity": 0,
    }
    assert result["portfolio_summary"]["probability_summary"] == {
        "minimum": 0.2,
        "percentile_25": 0.35,
        "median": 0.5,
        "mean": pytest.approx(0.5333333333333333),
        "percentile_75": 0.7,
        "maximum": 0.9,
    }
    assert result["portfolio_summary"]["risk_band_method"] == "fixed_validation_cohort_quantiles"
    assert [band["label"] for band in result["portfolio_summary"]["risk_bands"]] == [
        "Lower", "Moderate", "Elevated", "Highest"
    ]
    assert [band["customer_count"] for band in result["portfolio_summary"]["risk_bands"]] == [
        0, 0, 1, 2
    ]
    assert sum(
        band["portfolio_share"] for band in result["portfolio_summary"]["risk_bands"]
    ) == pytest.approx(1.0)
    assert [row["customer_id"] for row in result["customers"]] == [1002, 1003, 1001]
    assert [row["selected_for_review"] for row in result["customers"]] == [True, True, False]


def test_service_does_not_split_equal_score_group_at_capacity_boundary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _build_service(monkeypatch, [0.9, 0.9, 0.2])
    request = ReviewQueueRequest.model_validate(
        {
            "customers": [_customer(1001), _customer(1002), _customer(1003)],
            "max_review_count": 1,
        }
    )

    result = service.build_queue(request)

    assert [row["risk_rank"] for row in result["customers"]] == [1, 1, 3]
    assert result["capacity"]["selected_count"] == 0
    assert all(not row["selected_for_review"] for row in result["customers"])


def test_zero_capacity_is_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    service = _build_service(monkeypatch, [0.2])
    request = ReviewQueueRequest.model_validate(
        {"customers": [_customer(1001)], "max_review_count": 0}
    )

    result = service.build_queue(request)

    assert result["capacity"]["selected_count"] == 0
    assert result["capacity"]["unused_capacity"] == 0


def test_customer_explanation_reuses_grouped_explainer_and_training_reference(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured = {}

    def fake_explainer(**kwargs):
        captured.update(kwargs)
        return type(
            "Explanation",
            (),
            {
                "predicted_probability": 0.42,
                "baseline_probability": 0.25,
                "method": "grouped interventional Shapley values",
                "background_size": 64,
                "contributions": pd.DataFrame(
                    [{"feature_group": "repayment_status_history", "contribution": 0.17, "direction": "higher than baseline"}]
                ),
            },
        )()

    monkeypatch.setattr(
        "propensity_prediction.api.service.explain_customer_prediction",
        fake_explainer,
    )
    repository = InMemoryModelRepository()
    service = ReviewQueueService(repository)

    result = service.explain_customer(CustomerInput.model_validate(_customer(1001)))

    assert result["customer_id"] == 1001
    assert result["estimated_default_probability"] == 0.42
    assert result["reference_probability"] == 0.25
    assert result["difference_from_reference"] == pytest.approx(0.17)
    assert captured["model"] == "model-double"
    assert captured["background"] == "training-reference"
    assert "not causes" in result["limitations"]


def test_duplicate_portfolio_ids_raise_domain_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _build_service(monkeypatch, [0.2, 0.4])
    request = ReviewQueueRequest.model_validate(
        {
            "customers": [_customer(1001), _customer(1001)],
            "max_review_count": 1,
        }
    )

    with pytest.raises(InvalidPortfolioError, match="IDs must be unique"):
        service.build_queue(request)


def test_repository_reports_missing_artifact_as_unavailable(tmp_path) -> None:
    repository = ModelArtifactRepository(tmp_path / "missing-model.joblib")

    with pytest.raises(ModelArtifactUnavailable, match="artifact is not available"):
        repository.get_model_artifact()


def test_fixed_risk_bands_match_documented_validation_definition() -> None:
    definition = validation_risk_band_definition()

    assert definition.cut_points == VALIDATION_RISK_BAND_CUT_POINTS
    assert definition.labels == ("Lower", "Moderate", "Elevated", "Highest")


def test_packaged_model_reproduces_phase_6_validation_risk_band_cut_points() -> None:
    split = split_dataset(build_processed_dataset())
    artifact = load_model_artifact()
    probabilities = predict_default_probabilities(artifact, split.X_validation)

    fitted_reference = fit_risk_bands(probabilities)

    assert np.allclose(
        fitted_reference.cut_points,
        VALIDATION_RISK_BAND_CUT_POINTS,
        rtol=0,
        atol=1e-12,
    )
