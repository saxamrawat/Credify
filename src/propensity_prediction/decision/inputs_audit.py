"""Audit available data inputs for risk-prioritization decisions."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from propensity_prediction.data.build import PROCESSED_DATA_PATH
from propensity_prediction.data.schema import (
    CATEGORICAL_FEATURES,
    IDENTIFIER_COLUMNS,
    NUMERICAL_FEATURES,
    ORDINAL_FEATURES,
)
from propensity_prediction.data.split import split_dataset


@dataclass(frozen=True)
class DecisionInputAudit:
    """Data profiles and missing-input inventory for decision analysis."""

    field_profiles: pd.DataFrame
    decision_input_gaps: pd.DataFrame
    training_row_count: int


DECISION_INPUT_GAPS = pd.DataFrame(
    [
        {
            "input": "Predicted default probability",
            "availability": "Derived from the selected model",
            "decision_role": "Primary risk-ranking signal",
            "limitation": "A predictive estimate, not an intervention effect or certainty.",
        },
        {
            "input": "Observed next-month default",
            "availability": "Historical target available",
            "decision_role": "Retrospective evaluation only",
            "limitation": "Not available as an input for a future customer prediction.",
        },
        {
            "input": "Analyst review capacity",
            "availability": "Not in dataset",
            "decision_role": "Scenario parameter to be supplied",
            "limitation": "Capacity levels will be assumptions until operational data is supplied.",
        },
        {
            "input": "Customer contactability and channel",
            "availability": "Not in dataset",
            "decision_role": "Operational input unavailable",
            "limitation": "Cannot determine which customers can be reached or by what channel.",
        },
        {
            "input": "Intervention cost and outcomes",
            "availability": "Not in dataset",
            "decision_role": "Unavailable for cost-effectiveness analysis",
            "limitation": "No intervention outcome or causal evidence is recorded.",
        },
        {
            "input": "Exposure at default and loss given default",
            "availability": "Not established in dataset",
            "decision_role": "Unavailable for expected-loss prioritization",
            "limitation": "Credit limits and historical bill amounts are not validated EAD or LGD measures.",
        },
    ]
)


_FIELD_DESCRIPTIONS: dict[str, tuple[str, str, str]] = {
    "ID": (
        "Identifier",
        "Record lookup only",
        "Excluded from model features and risk scoring.",
    ),
    "LIMIT_BAL": (
        "Credit limit",
        "Model predictor; limited proxy",
        "A credit limit, not current exposure at default.",
    ),
    "AGE": (
        "Customer profile",
        "Model predictor",
        "A model input, not an exposure or operational capacity measure.",
    ),
    "SEX": (
        "Customer profile",
        "Model predictor",
        "A coded profile field; not a standalone prioritization rule.",
    ),
    "EDUCATION": (
        "Customer profile",
        "Model predictor",
        "A coded profile field; not a standalone prioritization rule.",
    ),
    "MARRIAGE": (
        "Customer profile",
        "Model predictor",
        "A coded profile field; not a standalone prioritization rule.",
    ),
}


def _field_description(field: str) -> tuple[str, str, str]:
    if field in _FIELD_DESCRIPTIONS:
        return _FIELD_DESCRIPTIONS[field]
    if field.startswith("PAY_") and field[4:].isdigit():
        return (
            "Historical repayment status",
            "Model predictor",
            "Historical behavior associated with default risk; not causal evidence.",
        )
    if field.startswith("BILL_AMT"):
        return (
            "Historical billing amount",
            "Model predictor; limited proxy",
            "Historical statement amount; not confirmed exposure at default.",
        )
    if field.startswith("PAY_AMT"):
        return (
            "Historical payment amount",
            "Model predictor",
            "Historical payment behavior; not intervention cost or outcome.",
        )
    raise ValueError(f"No decision-input description is defined for {field}.")


def audit_decision_inputs(
    X_train: pd.DataFrame,
    y_train: pd.Series,
) -> DecisionInputAudit:
    """Profile known fields using training rows only.

    The outcome must be supplied separately from predictors to make its
    evaluation-only role explicit. Continuous fields receive 5th,
    50th, and 95th percentiles; low-cardinality fields receive value
    counts. No validation or test rows are needed by this function.
    """
    if not isinstance(X_train, pd.DataFrame) or X_train.empty:
        raise ValueError("X_train must be a non-empty DataFrame.")
    if "DEFAULT" in X_train.columns:
        raise ValueError("DEFAULT must be supplied separately as y_train, not in X_train.")
    if not isinstance(y_train, pd.Series) or y_train.empty:
        raise ValueError("y_train must be a non-empty Series.")
    if len(X_train) != len(y_train):
        raise ValueError("X_train and y_train must have equal lengths.")
    if y_train.isna().any() or not y_train.isin([0, 1]).all():
        raise ValueError("y_train must contain only non-missing binary values 0 and 1.")

    model_columns = NUMERICAL_FEATURES + CATEGORICAL_FEATURES + ORDINAL_FEATURES
    required_columns = IDENTIFIER_COLUMNS + model_columns
    missing = sorted(set(required_columns) - set(X_train.columns))
    if missing:
        raise ValueError(f"X_train is missing required columns: {missing}")

    rows = []
    for field in required_columns + ["DEFAULT"]:
        values = y_train if field == "DEFAULT" else X_train[field]
        role, availability, limitation = (
            (
                "Historical target",
                "Retrospective evaluation only",
                "Not a predictor or future decision-time input.",
            )
            if field == "DEFAULT"
            else _field_description(field)
        )
        clean_values = values.dropna()
        low_cardinality = field in CATEGORICAL_FEATURES + ORDINAL_FEATURES or field == "DEFAULT"
        value_counts = ""
        q05 = median = q95 = np.nan
        if low_cardinality:
            value_counts = "; ".join(
                f"{value}: {int(count)}"
                for value, count in values.value_counts(dropna=False).sort_index().items()
            )
        elif field != "ID" and pd.api.types.is_numeric_dtype(clean_values):
            quantiles = clean_values.quantile([0.05, 0.50, 0.95])
            q05, median, q95 = (float(quantiles.loc[q]) for q in [0.05, 0.50, 0.95])

        rows.append(
            {
                "field": field,
                "role": role,
                "availability": availability,
                "dtype": str(values.dtype),
                "training_rows": int(len(values)),
                "missing_count": int(values.isna().sum()),
                "missing_rate": float(values.isna().mean()),
                "distinct_values": int(clean_values.nunique()),
                "q05": q05,
                "median": median,
                "q95": q95,
                "value_counts": value_counts,
                "interpretation_limit": limitation,
            }
        )

    return DecisionInputAudit(
        field_profiles=pd.DataFrame(rows),
        decision_input_gaps=DECISION_INPUT_GAPS.copy(),
        training_row_count=len(X_train),
    )


def audit_training_split() -> DecisionInputAudit:
    """Load the processed data and audit only its training partition."""
    dataset = pd.read_csv(PROCESSED_DATA_PATH)
    split = split_dataset(dataset)
    return audit_decision_inputs(split.X_train, split.y_train)


if __name__ == "__main__":
    audit = audit_training_split()
    print(f"Training rows audited: {audit.training_row_count}")
    print("\nAvailable field profiles:")
    print(audit.field_profiles.to_string(index=False))
    print("\nDecision inputs not established by this dataset:")
    print(audit.decision_input_gaps.to_string(index=False))
