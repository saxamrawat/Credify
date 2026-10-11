"""Application service that connects model inference to the review queue."""

from __future__ import annotations

import pandas as pd

from propensity_prediction.api.errors import InvalidPortfolioError
from propensity_prediction.api.repository import ModelArtifactRepository
from propensity_prediction.api.schemas import ReviewQueueRequest
from propensity_prediction.decision.engine import build_review_queue
from propensity_prediction.models.artifact import predict_default_probabilities


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
            "customers": customers_result,
        }
