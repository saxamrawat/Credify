"""HTTP routes for readiness and review-queue requests."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from propensity_prediction.api.schemas import (
    APIErrorResponse,
    HealthResponse,
    ReviewQueueRequest,
    ReviewQueueResponse,
)
from propensity_prediction.api.service import ReviewQueueService


router = APIRouter()


def get_review_queue_service(request: Request) -> ReviewQueueService:
    return request.app.state.review_queue_service


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    repository = request.app.state.model_repository
    return HealthResponse(
        status="ok" if repository.is_loaded else "degraded",
        model_loaded=repository.is_loaded,
    )


@router.post(
    "/v1/review-queue",
    response_model=ReviewQueueResponse,
    responses={
        400: {"model": APIErrorResponse},
        422: {"model": APIErrorResponse},
        503: {"model": APIErrorResponse},
    },
)
def create_review_queue(
    payload: ReviewQueueRequest,
    service: ReviewQueueService = Depends(get_review_queue_service),
) -> dict:
    return service.build_queue(payload)
