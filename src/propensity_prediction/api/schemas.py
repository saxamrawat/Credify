"""Pydantic request and response models for the public API contract."""

from __future__ import annotations

from typing import Annotated

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


class ReviewQueueResponse(BaseModel):
    population_count: int
    capacity: CapacitySummary
    customers: list[CustomerQueueItem]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool


class APIErrorBody(BaseModel):
    code: str
    message: str
    details: list[str]


class APIErrorResponse(BaseModel):
    error: APIErrorBody
