"""Build minimized, server-authoritative evidence for bounded analyst Q&A."""

from __future__ import annotations

import pandas as pd

from propensity_prediction.api.errors import InvalidPortfolioError
from propensity_prediction.api.schemas import AnalystContextRequest, AnalystContextResponse
from propensity_prediction.api.service import ReviewQueueService
from propensity_prediction.explainability.risk_segmentation import (
    assign_risk_bands,
    validation_risk_band_definition,
)


_PAYMENT_STATUS_FIELDS = {"PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"}
_LIMITATIONS = [
    "Predicted probabilities are model estimates, not observed outcomes or expected losses.",
    "Portfolio patterns are descriptive and do not establish causes or intervention effects.",
]


def _metric(
    value: float | int,
    *,
    unit: str,
    scope: str,
    definition: str,
    denominator: int | None,
    source: str,
    limitations: list[str] | None = None,
) -> dict:
    return {
        "value": value,
        "unit": unit,
        "scope": scope,
        "definition": definition,
        "denominator": denominator,
        "source": source,
        "limitations": limitations if limitations is not None else _LIMITATIONS,
    }


class AnalystContextService:
    """Recompute the current portfolio and return only approved aggregates."""

    def __init__(self, review_queue_service: ReviewQueueService) -> None:
        self.review_queue_service = review_queue_service

    def build_context(self, request: AnalystContextRequest) -> AnalystContextResponse:
        queue = self.review_queue_service.build_queue(request)
        source = pd.DataFrame([customer.model_dump() for customer in request.customers])
        scored = source.copy()
        queue_by_id = {item["customer_id"]: item for item in queue["customers"]}
        scored["predicted_default_probability"] = scored["ID"].map(
            lambda customer_id: queue_by_id[int(customer_id)]["predicted_default_probability"]
        )
        scored["selected_for_review"] = scored["ID"].map(
            lambda customer_id: queue_by_id[int(customer_id)]["selected_for_review"]
        )
        if not scored["ID"].is_unique:
            # ReviewQueueService normally raises first; retain this invariant locally.
            raise InvalidPortfolioError("Customer IDs must be unique within a portfolio.")

        risk_definition = validation_risk_band_definition()
        scored["risk_band"] = assign_risk_bands(
            scored["predicted_default_probability"].to_numpy(), risk_definition
        )
        cohort = self._filter_cohort(scored, request)
        count = len(cohort)
        portfolio_count = len(scored)
        capacity = queue["capacity"]

        evidence = {
            "portfolio.customer_count": _metric(
                portfolio_count, unit="customers", scope="full_portfolio",
                definition="Number of validated customer rows scored for this request.",
                denominator=portfolio_count, source="validated_request",
            ),
            "portfolio.mean_predicted_probability": _metric(
                queue["portfolio_summary"]["probability_summary"]["mean"],
                unit="probability", scope="full_portfolio",
                definition="Arithmetic mean of model-estimated default probabilities.",
                denominator=portfolio_count, source="deterministic_scoring_summary",
            ),
            "portfolio.median_predicted_probability": _metric(
                queue["portfolio_summary"]["probability_summary"]["median"],
                unit="probability", scope="full_portfolio",
                definition="Median of model-estimated default probabilities.",
                denominator=portfolio_count, source="deterministic_scoring_summary",
            ),
            "portfolio.percentile_25_predicted_probability": _metric(
                queue["portfolio_summary"]["probability_summary"]["percentile_25"],
                unit="probability", scope="full_portfolio",
                definition="25th percentile of model-estimated default probabilities.",
                denominator=portfolio_count, source="deterministic_scoring_summary",
            ),
            "portfolio.percentile_75_predicted_probability": _metric(
                queue["portfolio_summary"]["probability_summary"]["percentile_75"],
                unit="probability", scope="full_portfolio",
                definition="75th percentile of model-estimated default probabilities.",
                denominator=portfolio_count, source="deterministic_scoring_summary",
            ),
            "portfolio.probability_range": _metric(
                {
                    "minimum": queue["portfolio_summary"]["probability_summary"]["minimum"],
                    "maximum": queue["portfolio_summary"]["probability_summary"]["maximum"],
                },
                unit="probability", scope="full_portfolio",
                definition="Minimum and maximum model-estimated default probabilities.",
                denominator=portfolio_count, source="deterministic_scoring_summary",
            ),
            "queue.requested_capacity": _metric(
                capacity["requested_review_count"], unit="customers", scope="full_portfolio",
                definition="Review count requested by the analyst.", denominator=portfolio_count,
                source="deterministic_queue_summary",
            ),
            "queue.selected_count": _metric(
                capacity["selected_count"], unit="customers", scope="full_portfolio",
                definition="Customers selected by the deterministic tie-aware queue.",
                denominator=portfolio_count, source="deterministic_queue_summary",
            ),
            "queue.unused_capacity": _metric(
                capacity["unused_capacity"], unit="customers", scope="full_portfolio",
                definition="Requested capacity not used because equal-score groups remain together.",
                denominator=capacity["requested_review_count"],
                source="deterministic_queue_summary",
            ),
        }
        for band in queue["portfolio_summary"]["risk_bands"]:
            key = band["label"].lower()
            evidence[f"risk_bands.{key}.customer_count"] = _metric(
                band["customer_count"], unit="customers", scope="full_portfolio",
                definition=(
                    f"Customers assigned to the fixed-reference {band['label']} risk band. "
                    f"Reference: {queue['portfolio_summary']['risk_band_reference']}."
                ), denominator=portfolio_count, source="fixed_validation_risk_bands",
            )
            evidence[f"risk_bands.{key}.portfolio_share"] = _metric(
                band["portfolio_share"], unit="share", scope="full_portfolio",
                definition=(
                    f"Share of the full portfolio in the fixed-reference {band['label']} band; "
                    f"reference: {queue['portfolio_summary']['risk_band_reference']}."
                ), denominator=portfolio_count, source="fixed_validation_risk_bands",
            )
        reason_counts: dict[str, int] = {}
        for item in queue["customers"]:
            code = item["reason_code"]
            reason_counts[code] = reason_counts.get(code, 0) + 1
        for code, value in sorted(reason_counts.items()):
            evidence[f"queue.reason_count.{code}"] = _metric(
                value, unit="customers", scope="full_portfolio",
                definition=f"Portfolio rows carrying deterministic queue reason code {code}.",
                denominator=portfolio_count, source="deterministic_queue_reasons",
            )

        active = {
            "customer_count": _metric(
                count, unit="customers", scope="active_cohort",
                definition="Number of rows matching the submitted allowlisted filters.",
                denominator=portfolio_count, source="server_applied_filters",
            ),
            "filters": self._filter_description(request),
            "mean_predicted_probability": (
                _metric(
                    float(cohort["predicted_default_probability"].mean()),
                    unit="probability", scope="active_cohort",
                    definition="Arithmetic mean of predicted probabilities in the filtered cohort.",
                    denominator=count, source="server_recomputed_cohort_summary",
                ) if count else None
            ),
            "selected_count": _metric(
                int(cohort["selected_for_review"].sum()), unit="customers",
                scope="active_cohort", definition="Selected customers in the filtered cohort.",
                denominator=count, source="server_recomputed_cohort_summary",
            ),
            "risk_band_counts": {
                label: _metric(
                    int((cohort["risk_band"] == label).sum()), unit="customers",
                    scope="active_cohort",
                    definition=f"Filtered cohort members in the fixed-reference {label} band.",
                    denominator=count, source="server_recomputed_cohort_summary",
                )
                for label in risk_definition.labels
            },
        }

        group_summaries = self._group_summary(scored, cohort, request) if request.group_by else None
        local_explanation = self._local_explanation(source, request)
        return AnalystContextResponse(
            evidence=evidence,
            active_cohort=active,
            risk_band_method=queue["portfolio_summary"]["risk_band_method"],
            risk_band_reference=queue["portfolio_summary"]["risk_band_reference"],
            queue_selection_rule="deterministic_risk_rank_with_equal_scores_kept_together",
            group_by=request.group_by,
            group_method=(
                "encoded_category" if request.group_by in _PAYMENT_STATUS_FIELDS
                else "full_portfolio_quartiles" if request.group_by else None
            ),
            group_summaries=group_summaries,
            local_explanation=local_explanation,
        )

    @staticmethod
    def _filter_cohort(scored: pd.DataFrame, request: AnalystContextRequest) -> pd.DataFrame:
        filters = request.filters
        mask = scored["predicted_default_probability"].between(
            filters.minimum_probability, filters.maximum_probability, inclusive="both"
        )
        if filters.risk_band:
            mask &= scored["risk_band"] == filters.risk_band
        if filters.review_status == "selected":
            mask &= scored["selected_for_review"]
        elif filters.review_status == "not-selected":
            mask &= ~scored["selected_for_review"]
        if filters.feature:
            if filters.feature in _PAYMENT_STATUS_FIELDS and filters.category_value is not None:
                mask &= scored[filters.feature] == filters.category_value
            elif filters.feature not in _PAYMENT_STATUS_FIELDS:
                if filters.feature_minimum is not None:
                    mask &= scored[filters.feature] >= filters.feature_minimum
                if filters.feature_maximum is not None:
                    mask &= scored[filters.feature] <= filters.feature_maximum
        return scored.loc[mask]

    @staticmethod
    def _filter_description(request: AnalystContextRequest) -> dict:
        filters = request.filters.model_dump(exclude_none=True)
        return filters

    @staticmethod
    def _group_summary(scored: pd.DataFrame, cohort: pd.DataFrame, request: AnalystContextRequest) -> list[dict]:
        field = request.group_by
        if field in _PAYMENT_STATUS_FIELDS:
            grouped = cohort.groupby(field, sort=True, observed=True)
            return [
                {
                    "group": str(value), "customer_count": int(len(group)),
                    "cohort_share": float(len(group) / len(cohort)) if len(cohort) else 0.0,
                    "mean_predicted_probability": float(group["predicted_default_probability"].mean()),
                    "selected_count": int(group["selected_for_review"].sum()),
                    "scope": "active_cohort",
                    "denominator": len(cohort),
                    "definition": f"Summary for encoded {field} value {value}.",
                    "source": "server_recomputed_group_summary",
                    "limitations": _LIMITATIONS,
                }
                for value, group in grouped
            ]
        boundaries = scored[field].quantile([0.25, 0.5, 0.75]).to_numpy()
        labels = ["Q1", "Q2", "Q3", "Q4"]
        bins = cohort[field].map(
            lambda value: labels[0] if value <= boundaries[0]
            else labels[1] if value <= boundaries[1]
            else labels[2] if value <= boundaries[2]
            else labels[3]
        )
        output = []
        for label in labels:
            group = cohort.loc[bins == label]
            if group.empty:
                continue
            output.append({
                "group": label, "customer_count": int(len(group)),
                "cohort_share": float(len(group) / len(cohort)),
                "mean_predicted_probability": float(group["predicted_default_probability"].mean()),
                "selected_count": int(group["selected_for_review"].sum()),
                "scope": "active_cohort",
                "denominator": len(cohort),
                "definition": (
                    f"Summary for {label}, using {field} quartile boundaries "
                    "computed from the full portfolio."
                ),
                "source": "server_recomputed_group_summary",
                "limitations": _LIMITATIONS,
            })
        return output

    def _local_explanation(self, source: pd.DataFrame, request: AnalystContextRequest) -> dict | None:
        requested_id = request.explain_customer_id
        if requested_id is None:
            return None
        matches = source.loc[source["ID"] == requested_id]
        if matches.empty:
            raise InvalidPortfolioError("The requested explanation customer is not in this portfolio.")
        customer = request.customers[int(matches.index[0])]
        explanation = self.review_queue_service.explain_customer(customer)
        # The customer ID is used only to locate the row and is deliberately discarded.
        return {
            "estimated_default_probability": explanation["estimated_default_probability"],
            "reference_probability": explanation["reference_probability"],
            "difference_from_reference": explanation["difference_from_reference"],
            "method": explanation["method"],
            "background_size": explanation["background_size"],
            "contributions": explanation["contributions"],
            "limitations": explanation["limitations"],
        }
