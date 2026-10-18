"""HTTP routes for readiness and review-queue requests."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from propensity_prediction.api.analyst_answer import AnalystAnswerService
from propensity_prediction.api.analyst_context import AnalystContextService
from propensity_prediction.api.schemas import (
    APIErrorResponse,
    AnalystAnswerResponse,
    AnalystContextRequest,
    AnalystContextResponse,
    CustomerExplanationResponse,
    CustomerInput,
    DashboardConfigResponse,
    HealthResponse,
    ReviewQueueRequest,
    ReviewQueueResponse,
)
from propensity_prediction.api.service import ReviewQueueService
from propensity_prediction.explainability.global_importance_reference import (
    GLOBAL_FEATURE_IMPORTANCE_REFERENCE,
)
from propensity_prediction.limits import MAX_CUSTOMER_ROWS


router = APIRouter()


def get_review_queue_service(request: Request) -> ReviewQueueService:
    return request.app.state.review_queue_service


def get_analyst_context_service(request: Request) -> AnalystContextService:
    return AnalystContextService(get_review_queue_service(request))


def get_analyst_answer_service(request: Request) -> AnalystAnswerService:
    return request.app.state.analyst_answer_service


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    repository = request.app.state.model_repository
    return HealthResponse(
        status="ok" if repository.is_loaded else "degraded",
        model_loaded=repository.is_loaded,
    )


@router.get("/v1/dashboard-config", response_model=DashboardConfigResponse)
def dashboard_config() -> DashboardConfigResponse:
    """Expose upload rules so the browser uses the API's schema and row cap."""
    return DashboardConfigResponse(
        max_customer_rows=MAX_CUSTOMER_ROWS,
        required_columns=list(CustomerInput.model_fields),
        model_feature_importance=GLOBAL_FEATURE_IMPORTANCE_REFERENCE,
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


@router.post(
    "/v1/analyst-context",
    response_model=AnalystContextResponse,
    responses={
        400: {"model": APIErrorResponse},
        422: {"model": APIErrorResponse},
        503: {"model": APIErrorResponse},
    },
)
def build_analyst_context(
    payload: AnalystContextRequest,
    service: AnalystContextService = Depends(get_analyst_context_service),
) -> AnalystContextResponse:
    """Recompute and return allowlisted aggregates for a future GenAI adapter."""
    return service.build_context(payload)


@router.post(
    "/v1/analyst-answer",
    response_model=AnalystAnswerResponse,
    responses={
        400: {"model": APIErrorResponse},
        422: {"model": APIErrorResponse},
        502: {"model": APIErrorResponse},
        503: {"model": APIErrorResponse},
        504: {"model": APIErrorResponse},
    },
)
def create_analyst_answer(
    payload: AnalystContextRequest,
    service: AnalystAnswerService = Depends(get_analyst_answer_service),
) -> AnalystAnswerResponse:
    """Answer one bounded question from fresh server-built evidence."""
    return service.answer(payload)


@router.post("/v1/customer-explanation", response_model=CustomerExplanationResponse)
def explain_customer(
    customer: CustomerInput,
    service: ReviewQueueService = Depends(get_review_queue_service),
) -> dict:
    """Return grouped model attributions for one prediction-time input row."""
    return service.explain_customer(customer)
