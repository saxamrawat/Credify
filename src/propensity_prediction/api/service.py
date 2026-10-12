"""Application service that connects model inference to the review queue."""

from __future__ import annotations

import math

import pandas as pd

from propensity_prediction.api.errors import InvalidPortfolioError
from propensity_prediction.api.repository import ModelArtifactRepository
from propensity_prediction.api.schemas import CustomerInput, ReviewQueueRequest
from propensity_prediction.decision.engine import build_review_queue
from propensity_prediction.explainability.risk_segmentation import (
    VALIDATION_RISK_BAND_METHOD,
    VALIDATION_RISK_BAND_REFERENCE,
    assign_risk_bands,
    validation_risk_band_definition,
)
from propensity_prediction.models.artifact import predict_default_probabilities
from propensity_prediction.explainability.local_explanation import explain_customer_prediction


class ReviewQueueService:
    """Coordinate scoring and deterministic queue construction."""

    def __init__(self, model_repository: ModelArtifactRepository) -> None:
        self.model_repository = model_repository

    def build_queue(self, request: ReviewQueueRequest) -> dict:
        customers = pd.DataFrame(
            [customer.model_dump() for customer in request.customers]
        )
        if customers["ID"].duplicated().any():
            raise InvalidPortfolioError("Customer IDs must be unique within a portfolio.")

        model_artifact = self.model_repository.get_model_artifact()
        probabilities = predict_default_probabilities(model_artifact, customers)
        queue = build_review_queue(
            customer_ids=customers["ID"],
            probabilities=probabilities,
            max_review_count=request.max_review_count,
        )

        risk_band_definition = validation_risk_band_definition()
        assigned_bands = assign_risk_bands(probabilities, risk_band_definition)
        probability_series = pd.Series(probabilities, dtype=float)
        risk_bands = []
        for index, label in enumerate(risk_band_definition.labels):
            customer_count = int((assigned_bands == label).sum())
            lower_edge = risk_band_definition.edges[index]
            upper_edge = risk_band_definition.edges[index + 1]
            risk_bands.append(
                {
                    "label": label,
                    "customer_count": customer_count,
                    "portfolio_share": customer_count / len(customers),
                    "lower_bound_exclusive": (
                        float(lower_edge) if math.isfinite(lower_edge) else None
                    ),
                    "upper_bound_inclusive": (
                        float(upper_edge) if math.isfinite(upper_edge) else None
                    ),
                }
            )
        portfolio_summary = {
            "probability_summary": {
                "minimum": float(probability_series.min()),
                "percentile_25": float(probability_series.quantile(0.25)),
                "median": float(probability_series.median()),
                "mean": float(probability_series.mean()),
                "percentile_75": float(probability_series.quantile(0.75)),
                "maximum": float(probability_series.max()),
            },
            "risk_band_method": VALIDATION_RISK_BAND_METHOD,
            "risk_band_reference": VALIDATION_RISK_BAND_REFERENCE,
            "risk_bands": risk_bands,
        }

        customers_result = [
            {
                "customer_id": int(row.customer_id),
                "predicted_default_probability": float(
                    row.predicted_default_probability
                ),
                "risk_rank": int(row.risk_rank),
                "selected_for_review": bool(row.selected_for_review),
                "reason_code": str(row.reason_code),
                "reason": str(row.reason),
            }
            for row in queue.customers.itertuples(index=False)
        ]
        return {
            "population_count": len(customers),
            "capacity": {
                "requested_review_count": queue.requested_capacity,
                "target_review_count": queue.target_review_count,
                "selected_count": queue.selected_count,
                "unused_capacity": queue.unused_capacity,
            },
            "portfolio_summary": portfolio_summary,
            "customers": customers_result,
        }

    def explain_customer(self, customer: CustomerInput) -> dict:
        """Explain one submitted record against the fixed training reference."""
        artifact = self.model_repository.get_model_artifact()
        row = pd.DataFrame([customer.model_dump()])
        explanation = explain_customer_prediction(
            model=artifact["estimator"],
            customer=row,
            background=self.model_repository.get_explanation_background(),
        )
        return {
            "customer_id": customer.ID,
            "estimated_default_probability": explanation.predicted_probability,
            "reference_probability": explanation.baseline_probability,
            "difference_from_reference": (
                explanation.predicted_probability - explanation.baseline_probability
            ),
            "method": explanation.method,
            "background_size": explanation.background_size,
            "contributions": explanation.contributions.to_dict(orient="records"),
            "limitations": (
                "Grouped model attributions compare this record with a fixed sample "
                "from the training partition. They describe model behavior, not "
                "causes, outcomes, or intervention effects."
            ),
        }
