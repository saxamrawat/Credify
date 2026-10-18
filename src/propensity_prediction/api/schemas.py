"""Pydantic request and response models for the public API contract."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    field_validator,
    model_validator,
)

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


AnalystField = Literal[
    "LIMIT_BAL",
    "AGE",
    "BILL_AMT1",
    "BILL_AMT2",
    "BILL_AMT3",
    "BILL_AMT4",
    "BILL_AMT5",
    "BILL_AMT6",
    "PAY_AMT1",
    "PAY_AMT2",
    "PAY_AMT3",
    "PAY_AMT4",
    "PAY_AMT5",
    "PAY_AMT6",
    "PAY_0",
    "PAY_2",
    "PAY_3",
    "PAY_4",
    "PAY_5",
    "PAY_6",
]


class AnalystCohortFilters(BaseModel):
    """Allowlisted Explore filters; identifiers and demographic fields are excluded."""

    model_config = ConfigDict(extra="forbid", strict=True, allow_inf_nan=False)

    minimum_probability: Annotated[float, Field(ge=0, le=1)] = 0
    maximum_probability: Annotated[float, Field(ge=0, le=1)] = 1
    risk_band: Literal["Lower", "Moderate", "Elevated", "Highest"] | None = None
    review_status: Literal["selected", "not-selected"] | None = None
    feature: AnalystField | None = None
    category_value: StrictInt | None = None
    feature_minimum: float | None = None
    feature_maximum: float | None = None

    @model_validator(mode="after")
    def validate_filter_bounds(self) -> "AnalystCohortFilters":
        if self.minimum_probability > self.maximum_probability:
            raise ValueError("minimum_probability must not exceed maximum_probability")
        if self.feature_minimum is not None and self.feature_maximum is not None:
            if self.feature_minimum > self.feature_maximum:
                raise ValueError("feature_minimum must not exceed feature_maximum")
        if self.category_value is not None and self.feature not in {
            "PAY_0",
            "PAY_2",
            "PAY_3",
            "PAY_4",
            "PAY_5",
            "PAY_6",
        }:
            raise ValueError("category_value is supported only for PAY status fields")
        if (
            self.feature_minimum is not None or self.feature_maximum is not None
        ) and self.feature in {
            "PAY_0",
            "PAY_2",
            "PAY_3",
            "PAY_4",
            "PAY_5",
            "PAY_6",
        }:
            raise ValueError("PAY status fields require category_value, not a numeric range")
        return self


class AnalystContextRequest(ReviewQueueRequest):
    """Stateless input from which the server rebuilds approved analyst evidence."""

    filters: AnalystCohortFilters = Field(default_factory=AnalystCohortFilters)
    question: Annotated[str, Field(min_length=1, max_length=1000)]
    group_by: AnalystField | None = None
    explain_customer_id: StrictInt | None = None

    @field_validator("question")
    @classmethod
    def strip_question(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("question must contain non-whitespace text")
        return cleaned


class EvidenceMetric(BaseModel):
    value: int | float | dict[str, float]
    unit: str
    scope: str
    definition: str
    denominator: int | None
    source: str
    limitations: list[str]


class AnalystGroupSummary(BaseModel):
    group: str
    customer_count: int = Field(ge=0)
    cohort_share: float = Field(ge=0, le=1)
    mean_predicted_probability: float = Field(ge=0, le=1)
    selected_count: int = Field(ge=0)
    scope: Literal["active_cohort"]
    denominator: int = Field(ge=0)
    definition: str
    source: Literal["server_recomputed_group_summary"]
    limitations: list[str]


class ActiveCohortContext(BaseModel):
    customer_count: EvidenceMetric
    filters: dict
    mean_predicted_probability: EvidenceMetric | None
    selected_count: EvidenceMetric
    risk_band_counts: dict[str, EvidenceMetric]


class AnalystContextResponse(BaseModel):
    """Minimized deterministic evidence. Contains no customer-level identifiers."""

    context_version: Literal["1"] = "1"
    evidence: dict[str, EvidenceMetric]
    active_cohort: ActiveCohortContext
    risk_band_method: Literal["fixed_validation_cohort_quantiles"]
    risk_band_reference: str
    queue_selection_rule: Literal[
        "deterministic_risk_rank_with_equal_scores_kept_together"
    ]
    group_by: AnalystField | None = None
    group_method: Literal["encoded_category", "full_portfolio_quartiles"] | None = None
    group_summaries: list[AnalystGroupSummary] | None = None
    local_explanation: dict | None = None


class AnalystClaim(BaseModel):
    """One generated sentence whose evidence keys are checked by the API."""

    model_config = ConfigDict(extra="forbid", strict=True)

    kind: Literal["fact", "interpretation"]
    text: Annotated[str, Field(min_length=1, max_length=600)]
    evidence_refs: Annotated[list[str], Field(min_length=1, max_length=8)]


class AnalystAnswerDraft(BaseModel):
    """Untrusted JSON draft emitted by the language model."""

    model_config = ConfigDict(extra="forbid", strict=True)

    status: Literal["answered", "refused"]
    claims: Annotated[list[AnalystClaim], Field(max_length=6)]
    refusal_code: Literal[
        "unsupported_request", "insufficient_evidence", "model_uncertainty"
    ] | None = None

    @model_validator(mode="after")
    def validate_answer_state(self) -> "AnalystAnswerDraft":
        if self.status == "answered" and (not self.claims or self.refusal_code is not None):
            raise ValueError("answered output requires claims and no refusal_code")
        if self.status == "refused" and (self.claims or self.refusal_code is None):
            raise ValueError("refused output requires refusal_code and no claims")
        for claim in self.claims:
            if len(set(claim.evidence_refs)) != len(claim.evidence_refs):
                raise ValueError("evidence_refs must be unique within a claim")
        return self


class AnalystEvidenceCitation(BaseModel):
    key: str
    value: Any
    unit: str
    scope: str
    definition: str
    denominator: int | None
    source: str
    limitations: list[str]


class AnalystAnswerResponse(BaseModel):
    status: Literal["answered", "refused"]
    claims: list[AnalystClaim]
    citations: list[AnalystEvidenceCitation]
    refusal_code: str | None = None
    disclaimer: str = (
        "Generated commentary based on the supplied deterministic evidence; "
        "it is not an outcome, cause, or recommendation."
    )


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
