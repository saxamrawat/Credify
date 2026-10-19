"""Pydantic request and response models for the public API contract."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt

from propensity_prediction.limits import MAX_CUSTOMER_ROWS


class CustomerInput(BaseModel):
    """One customer row: identifier plus the 23 canonical predictors."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        allow_inf_nan=False,
    )

    ID: StrictInt
    LIMIT_BAL: Annotated[float, Field(ge=0)]
    AGE: float
    BILL_AMT1: float
    BILL_AMT2: float
    BILL_AMT3: float
    BILL_AMT4: float
    BILL_AMT5: float
    BILL_AMT6: float
    PAY_AMT1: Annotated[float, Field(ge=0)]
    PAY_AMT2: Annotated[float, Field(ge=0)]
    PAY_AMT3: Annotated[float, Field(ge=0)]
    PAY_AMT4: Annotated[float, Field(ge=0)]
    PAY_AMT5: Annotated[float, Field(ge=0)]
    PAY_AMT6: Annotated[float, Field(ge=0)]
    SEX: Annotated[StrictInt, Field(ge=1, le=2)]
    EDUCATION: Annotated[StrictInt, Field(ge=0, le=4)]
    MARRIAGE: Annotated[StrictInt, Field(ge=0, le=3)]
    PAY_0: StrictInt
    PAY_2: StrictInt
    PAY_3: StrictInt
    PAY_4: StrictInt
    PAY_5: StrictInt
    PAY_6: StrictInt


class ReviewQueueRequest(BaseModel):
    """Batch request to score a portfolio and apply a review-count limit."""

    model_config = ConfigDict(extra="forbid", strict=True)

    customers: Annotated[
        list[CustomerInput], Field(min_length=1, max_length=MAX_CUSTOMER_ROWS)
    ]
    max_review_count: Annotated[StrictInt, Field(ge=0)]


class CapacitySummary(BaseModel):
    requested_review_count: int
    target_review_count: int
    selected_count: int
    unused_capacity: int


class CustomerQueueItem(BaseModel):
    customer_id: int
    predicted_default_probability: float = Field(ge=0, le=1)
    risk_rank: int = Field(ge=1)
    selected_for_review: bool
    reason_code: str
    reason: str


class ProbabilitySummary(BaseModel):
    minimum: float = Field(ge=0, le=1)
    percentile_25: float = Field(ge=0, le=1)
    median: float = Field(ge=0, le=1)
    mean: float = Field(ge=0, le=1)
    percentile_75: float = Field(ge=0, le=1)
    maximum: float = Field(ge=0, le=1)


class RiskBandSummary(BaseModel):
    label: str
    customer_count: int = Field(ge=0)
    portfolio_share: float = Field(ge=0, le=1)
    lower_bound_exclusive: float | None = Field(default=None, ge=0, le=1)
    upper_bound_inclusive: float | None = Field(default=None, ge=0, le=1)


class PortfolioSummary(BaseModel):
    probability_summary: ProbabilitySummary
    risk_band_method: Literal["fixed_validation_cohort_quantiles"]
    risk_band_reference: str
    risk_bands: list[RiskBandSummary]


class ReviewQueueResponse(BaseModel):
    population_count: int
    capacity: CapacitySummary
    portfolio_summary: PortfolioSummary
    customers: list[CustomerQueueItem]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool


class ModelFeatureImportanceItem(BaseModel):
    feature: str
    description: str
    importance_mean: float
    importance_std: float = Field(ge=0)


class ModelFeatureImportanceReference(BaseModel):
    method: Literal["permutation_importance"]
    scoring_metric: Literal["average_precision"]
    evaluation_reference: str
    repeats: int = Field(ge=1)
    random_state: int
    features: list[ModelFeatureImportanceItem]


class DashboardConfigResponse(BaseModel):
    max_customer_rows: int = Field(ge=1)
    required_columns: list[str]
    model_feature_importance: ModelFeatureImportanceReference


class LocalContribution(BaseModel):
    feature_group: str
    contribution: float
    direction: str


class CustomerExplanationResponse(BaseModel):
    customer_id: int
    estimated_default_probability: float = Field(ge=0, le=1)
    reference_probability: float = Field(ge=0, le=1)
    difference_from_reference: float
    method: str
    background_size: int = Field(ge=1)
    contributions: list[LocalContribution]
    limitations: str


class APIErrorBody(BaseModel):
    code: str
    message: str
    details: list[str]


class APIErrorResponse(BaseModel):
    error: APIErrorBody
