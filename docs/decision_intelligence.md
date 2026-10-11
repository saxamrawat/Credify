# Phase 7 — Decision Intelligence and Risk Prioritization

This document brings together the complete written records for Phase 7. The original step documents are presented in phase order; the supplementary holdout analysis appears between Steps 7.4 and 7.5 to reflect when it was performed. Content is retained, including original code listings and reproduction instructions. Internal links between the former documents now point to the corresponding section in this document.

## Contents

- [Phase 7.2 — Decision-Input Audit](#phase-7-2-decision-input-audit)
- [Phase 7.3 — Risk Ranking Compared with Random Selection](#phase-7-3-risk-ranking-compared-with-random-selection)
- [Phase 7.4 — Illustrative Review-Capacity Scenarios](#phase-7-4-illustrative-review-capacity-scenarios)
- [Supplementary Phase 7 Analysis — Holdout Ranking Diagnostic](#supplementary-phase-7-holdout-ranking-diagnostic)
- [Phase 7.5 — Deterministic Review-Queue Engine](#phase-7-5-deterministic-review-queue-engine)
- [Phase 7.6 — Evaluate Review-Policy Scenarios](#phase-7-6-evaluate-review-policy-scenarios)
- [Phase 7.7 — Decision Recommendations and Limits](#phase-7-7-decision-recommendations-and-limits)

---

<a id="phase-7-2-decision-input-audit"></a>

# Phase 7.2 — Decision-Input Audit

## 1. Purpose and method

This audit inventories fields available for the agreed goal of ranking
customers for limited analyst attention. `audit_training_split()` reads
the existing processed dataset, creates the established stratified split,
and profiles the training partition only. `DEFAULT` is passed separately
as the outcome and appears in the report only as a retrospective
evaluation target. `ID` is profiled for record lookup and is not a model
input. No validation or test data is used for the audit.

For each available field, the audit reports its role, data type, training
row count, missingness, distinct count, and either compact value counts
for low-cardinality fields or 5th/50th/95th percentiles for continuous
fields. It also records interpretation limits. A separate inventory
lists important decision inputs absent from the dataset.

## 2. Available information

The dataset provides:

- historical repayment-status, billing, and payment fields used as model
  predictors;
- profile fields used by the current model;
- `LIMIT_BAL`, which is a credit limit and only a limited proxy for
  financial context;
- `DEFAULT`, a historical outcome for retrospective evaluation; and
- `ID`, an identifier for record lookup only.

The training partition contains **21,000 rows**. The audit found **no
missing values** in the identifier, 23 predictor fields, or target. The
training target contains 4,645 defaults (22.12%) and 16,355 non-defaults.
These are training-split counts, not estimates of future default prevalence.

Selected training-split profiles:

| Field | 5th percentile | Median | 95th percentile | Audit classification |
|---|---:|---:|---:|---|
| `LIMIT_BAL` | 20,000 | 140,000 | 440,000 | Credit-limit predictor; limited proxy |
| `BILL_AMT1` | 0 | 22,225.5 | 201,176.75 | Historical billing predictor; limited proxy |
| `PAY_AMT1` | 0 | 2,118.5 | 18,213.05 | Historical payment predictor |

Categorical and repayment-status fields are reported as value counts by
the audit utility instead of numeric percentiles, because their integer
codes are categories or ordered statuses rather than continuous amounts.

Historical bill amounts are not established exposure at default.
Historical payment amounts do not describe intervention costs or
outcomes. The audit does not promote either into an exposure or value
measure.

## 3. Inputs not established by the data

The dataset does not provide analyst review capacity, customer
contactability/channel, intervention costs or outcomes, exposure at
default (EAD), or loss given default (LGD). Capacity may be varied as an
explicit scenario in later analysis. Cost-effectiveness, expected-loss
prioritization, and intervention selection are unsupported unless the
missing data or clearly labeled assumptions are added.

The predicted default probability is a derived model output and will be
the primary ranking signal. Observed default is for retrospective
evaluation only; it must not be supplied as a prediction-time input.

## 4. How the audit works, step by step

The implementation is in
[`inputs_audit.py`](../src/propensity_prediction/decision/inputs_audit.py),
with focused checks in
[`test_decision_inputs_audit.py`](../tests/test_decision_inputs_audit.py).
The package initializer is
[`__init__.py`](../src/propensity_prediction/decision/__init__.py). The
source files are authoritative; complete listings are included below.

### Step 1 — Keep the target separate from predictors

The project split function returns `X_train` (candidate inputs) and
`y_train` (the historical outcome) separately. The audit accepts these as
separate arguments and rejects a `DEFAULT` column inside `X_train`. This
helps prevent the target from being treated as a future decision-time
input or included in the predictor profile.

### Step 2 — Define what each field can mean

`DECISION_INPUT_GAPS` inventories information that is derived, available
only for retrospective evaluation, absent, or not established.
`_FIELD_DESCRIPTIONS` explicitly describes fields that need care, such as
`LIMIT_BAL` and profile attributes. `_field_description()` handles
repeated field families by prefix: `PAY_*`, `BILL_AMT*`, and `PAY_AMT*`.
For each field it supplies a business role, availability classification,
and interpretation limit.

The model can use historical bill amounts as predictors without those
amounts becoming validated exposure-at-default measures. Historical
payment amounts likewise are not intervention costs or outcomes.

### Step 3 — Validate inputs before profiling

`audit_decision_inputs()` checks that `X_train` is a non-empty DataFrame,
`y_train` is a non-empty Series, `DEFAULT` is separate, row counts match,
the target is binary and non-missing, and all schema fields are present.
These checks prevent silent auditing of an incomplete or mis-specified
training table.

### Step 4 — Profile each field appropriately

The field order follows the canonical schema: identifier, numerical
features, categorical features, ordinal features, and target. Each row
reports role, availability, data type, training-row count, missing count
and rate, distinct-value count, and an interpretation limit.

Categorical and ordinal integer codes are reported as value counts, not
continuous quantities. Continuous numeric fields receive the 5th
percentile, median, and 95th percentile. ID receives a distinct count but
no quantiles. The target receives value counts and is marked
retrospective-only.

### Step 5 — Return a structured result

`DecisionInputAudit` contains the field-profile table, the decision-input
gap table, and the number of training rows audited. The gap table is
copied before it is returned so callers cannot mutate the module-level
definition through the result.

### Step 6 — Use the established training split

`audit_training_split()` reads the processed CSV, calls the project's
existing `split_dataset()`, and passes only `split.X_train` and
`split.y_train` to the audit. The profiling function receives no
validation or test rows. A focused test mocks the split and verifies that
only training rows appear in the profile.

### Step 7 — Print the report

The `if __name__ == "__main__"` block is the command-line entry point. It
prints the training-row count, field profiles, and decision-input gaps.
Importing the module does not run the audit; executing it with
`python -m` does.

## 5. What the focused tests verify

[`test_decision_inputs_audit.py`](../tests/test_decision_inputs_audit.py)
uses a small synthetic table with the same schema as the real data:

1. **Field profiles and target separation:** checks the expected schema,
   identifier and target roles, category counts, and missingness.
2. **Unavailable decision inputs:** checks review capacity, intervention
   costs/outcomes, and validated exposure/loss measures.
3. **Leakage guard:** confirms that putting `DEFAULT` in `X_train` raises
   an error.
4. **Input validation:** checks missing columns, mismatched lengths, and
   invalid target values.
5. **Training-only flow:** mocks the reader and split, then confirms that
   profiles use only the mocked training rows.

The tests check audit behavior. The 21,000-row results below come from
running the audit command against the processed project data.

## 6. Complete code listings

The listings are reproduced from the implementation files at the time
this step was completed. The source files are authoritative; refresh
these listings whenever the implementation changes.

### `src/propensity_prediction/decision/__init__.py`

```python
"""Decision-intelligence analysis utilities."""
```

### `src/propensity_prediction/decision/inputs_audit.py`

```python
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
```

### `tests/test_decision_inputs_audit.py`

```python
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from propensity_prediction.data.schema import (
    CATEGORICAL_FEATURES,
    IDENTIFIER_COLUMNS,
    NUMERICAL_FEATURES,
    ORDINAL_FEATURES,
)
from propensity_prediction.decision import inputs_audit


def _training_data(n=6):
    index = np.arange(n)
    X = pd.DataFrame({"ID": index + 10})
    for column in NUMERICAL_FEATURES:
        X[column] = index.astype(float) * 100 + 100
    for column in CATEGORICAL_FEATURES:
        X[column] = index % 2 + 1
    for column in ORDINAL_FEATURES:
        X[column] = index % 4 - 1
    y = pd.Series(index % 2, name="DEFAULT")
    return X, y


def test_audit_profiles_available_fields_and_separates_target():
    X, y = _training_data()

    result = inputs_audit.audit_decision_inputs(X, y)

    profiles = result.field_profiles.set_index("field")
    assert result.training_row_count == len(X)
    assert set(profiles.index) == set(
        IDENTIFIER_COLUMNS
        + NUMERICAL_FEATURES
        + CATEGORICAL_FEATURES
        + ORDINAL_FEATURES
        + ["DEFAULT"]
    )
    assert profiles.loc["ID", "availability"] == "Record lookup only"
    assert profiles.loc["DEFAULT", "availability"] == "Retrospective evaluation only"
    assert profiles.loc["DEFAULT", "value_counts"] == "0: 3; 1: 3"
    assert "not current exposure" in profiles.loc[
        "LIMIT_BAL", "interpretation_limit"
    ].lower()
    assert profiles["missing_count"].sum() == 0


def test_audit_inventories_missing_operational_inputs():
    X, y = _training_data()
    result = inputs_audit.audit_decision_inputs(X, y)

    gaps = result.decision_input_gaps.set_index("input")
    assert gaps.loc["Analyst review capacity", "availability"] == "Not in dataset"
    assert gaps.loc["Intervention cost and outcomes", "availability"] == "Not in dataset"
    assert "not validated" in gaps.loc[
        "Exposure at default and loss given default", "limitation"
    ]


def test_audit_rejects_target_in_predictor_frame():
    X, y = _training_data()
    X["DEFAULT"] = y.to_numpy()

    with pytest.raises(ValueError, match="supplied separately"):
        inputs_audit.audit_decision_inputs(X, y)


def test_audit_rejects_missing_fields_invalid_target_and_length_mismatch():
    X, y = _training_data()
    with pytest.raises(ValueError, match="missing required columns"):
        inputs_audit.audit_decision_inputs(X.drop(columns="PAY_0"), y)
    with pytest.raises(ValueError, match="equal lengths"):
        inputs_audit.audit_decision_inputs(X, y.iloc[:-1])
    with pytest.raises(ValueError, match="binary values"):
        inputs_audit.audit_decision_inputs(X, pd.Series([0, 1, 0, 1, 0, 2]))


def test_training_audit_uses_training_partition_only(monkeypatch):
    X, y = _training_data(n=8)
    train_X, train_y = X.iloc[:5].copy(), y.iloc[:5].copy()
    split = SimpleNamespace(X_train=train_X, y_train=train_y)
    monkeypatch.setattr(inputs_audit.pd, "read_csv", lambda _: pd.DataFrame({"unused": []}))
    monkeypatch.setattr(inputs_audit, "split_dataset", lambda _: split)

    result = inputs_audit.audit_training_split()

    assert result.training_row_count == 5
    assert result.field_profiles["training_rows"].eq(5).all()
    assert result.field_profiles.loc[
        result.field_profiles["field"] == "ID", "distinct_values"
    ].iloc[0] == 5
```

## 7. Reproduction

```bash
PYTHONPATH=src venv/bin/python -m propensity_prediction.decision.inputs_audit
venv/bin/python -m pytest tests/test_decision_inputs_audit.py -q
```

---

<a id="phase-7-3-risk-ranking-compared-with-random-selection"></a>

# Phase 7.3 — Risk Ranking Compared with Random Selection

## Goal and decision

This step asks whether ordering customers by predicted default probability
places more observed defaults near the top of a review queue than selecting
customers at random. The comparison covers every distinct probability score,
from the highest-risk group through the full validation population. It does
not set an operational cutoff or claim that review changes customer outcomes.

The random reference answers: if we selected the same fraction of customers
without using the model, what share of defaults would we expect to capture?
The reference is descriptive, not a forecast about the next population.

## Process, step by step

1. **Get outcomes and scores.** `run_validation_ranking_analysis()` takes the
   result of the existing final model-selection process. That process has
   already fit candidate models using training data and selected among them
   using validation metrics. This function takes the selected estimator,
   recreates the project's fixed split, and scores the validation features.
2. **Keep the target out of prediction inputs.** `DEFAULT` is passed only to
   the evaluation function as the historical outcome. The prediction inputs
   are the validation features after the same preparation used by final
   selection (including `ID` removal and optional engineered features).
3. **Validate the evaluation inputs.** `evaluate_risk_ranking()` requires
   equal, non-empty, one-dimensional arrays; binary observed outcomes; and
   finite probabilities from zero to one. Invalid values fail with a clear
   `ValueError`.
4. **Sort by predicted risk.** Rows are ordered from highest to lowest
   probability. Equal scores are kept together as one group. This avoids
   pretending that tied customers have a meaningful order.
5. **Measure each cumulative selection.** At the end of each score group, the
   function reports the selected count and capacity fraction, minimum score
   selected, number of observed defaults captured, precision, default-capture
   rate, and lift over the validation population's default rate.
6. **Add a random-selection reference.** At the same capacity, expected
   random defaults are `capacity × total defaults`; expected random capture
   rate is the capacity fraction; expected random precision is the population
   default rate; and random lift is one. These are expectations, so
   `random_expected_defaults` can be fractional.
7. **Add the zero-capacity point.** The curve begins at zero selected rows.
   Precision and lift are undefined there and are represented as missing.
   When there are no observed defaults, capture and lift are undefined.
8. **Return a development diagnostic.** The runner returns the selected model
   and feature set, its selection metrics, and the curve. It does not read or
   score the test split.

## Important interpretation limit

The validation split was also used to select the best model by PR-AUC and
ROC-AUC. Consequently this ranking curve is a **development diagnostic** and
may be optimistic; it is not an unbiased estimate of future performance.
The test split remains untouched. A final, unbiased ranking assessment should
be reserved for a later, explicitly approved evaluation step using the
selected model and test data once, after development decisions are complete.
This retrospective comparison also does not prove that analyst attention
prevents default.

No fixed capacity has been chosen. The curve lets a later step discuss
workload scenarios without treating a hypothetical capacity as an observed
business constraint.

## How to run it

Run final selection as the project already does, then pass its result to the
ranking runner:

```python
from propensity_prediction.decision.ranking import run_validation_ranking_analysis
from propensity_prediction.models.final_selection import run_final_selection

selection = run_final_selection()
analysis = run_validation_ranking_analysis(selection)
print(analysis["evaluation"].curve.to_string(index=False))
```

`run_final_selection()` performs grid search and can take time. The helper
does not retrain candidates; it uses the estimators returned by that run.

## Focused tests

[`test_decision_ranking.py`](../tests/test_decision_ranking.py) verifies the
ranking math on small known examples, random-reference values, tied-score
grouping, invalid inputs, and behavior when no defaults occur. Run it with:

```bash
venv/bin/pytest -q tests/test_decision_ranking.py
```

Result for this step: **8 passed**.

## Complete implementation

The source files are authoritative. These complete listings explain and
preserve the code created for this step.

### `src/propensity_prediction/decision/ranking.py`

```python
"""Evaluate whether predicted risk ranks defaults ahead of random selection."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class RankingEvaluation:
    """Cumulative ranking curve and its population-level baseline details."""

    curve: pd.DataFrame
    population_default_rate: float
    observation_count: int
    default_count: int


def evaluate_risk_ranking(
    y_true: pd.Series | np.ndarray,
    probabilities: pd.Series | np.ndarray,
) -> RankingEvaluation:
    """Compare top-risk selection with random selection at every score tie.

    The curve advances by groups of equal probability so it never implies
    that customers with tied scores have a meaningful within-tie order.
    """
    outcomes = np.asarray(y_true)
    scores = np.asarray(probabilities, dtype=float)

    if outcomes.ndim != 1 or scores.ndim != 1:
        raise ValueError("y_true and probabilities must be one-dimensional.")
    if len(outcomes) == 0 or len(outcomes) != len(scores):
        raise ValueError("y_true and probabilities must have equal non-zero lengths.")
    if pd.isna(outcomes).any() or not np.isin(outcomes, [0, 1]).all():
        raise ValueError("y_true must contain only non-missing binary values 0 and 1.")
    if not np.isfinite(scores).all() or ((scores < 0) | (scores > 1)).any():
        raise ValueError("probabilities must be finite values between 0 and 1.")

    outcomes = outcomes.astype(int)
    order = np.argsort(-scores, kind="stable")
    sorted_scores = scores[order]
    sorted_outcomes = outcomes[order]
    group_ends = np.r_[
        np.flatnonzero(sorted_scores[:-1] != sorted_scores[1:]) + 1,
        len(sorted_scores),
    ]
    selected = group_ends
    captured_defaults = np.cumsum(sorted_outcomes)[group_ends - 1]
    default_total = int(outcomes.sum())
    row_count = len(outcomes)
    prevalence = default_total / row_count

    capacity = selected / row_count
    precision = captured_defaults / selected
    capture_rate = (
        captured_defaults / default_total
        if default_total
        else np.full(len(selected), np.nan)
    )
    lift = precision / prevalence if prevalence else np.full(len(selected), np.nan)

    curve = pd.DataFrame(
        {
            "selected_count": selected,
            "capacity_fraction": capacity,
            "minimum_selected_probability": sorted_scores[group_ends - 1],
            "defaults_captured": captured_defaults.astype(int),
            "precision": precision,
            "default_capture_rate": capture_rate,
            "lift_over_random": lift,
            "random_expected_defaults": capacity * default_total,
            "random_expected_capture_rate": capacity,
            "random_expected_precision": prevalence,
            "random_expected_lift": np.ones(len(selected)) if prevalence else np.nan,
        }
    )
    curve = pd.concat(
        [
            pd.DataFrame(
                [{
                    "selected_count": 0,
                    "capacity_fraction": 0.0,
                    "minimum_selected_probability": np.nan,
                    "defaults_captured": 0,
                    "precision": np.nan,
                    "default_capture_rate": 0.0 if default_total else np.nan,
                    "lift_over_random": np.nan,
                    "random_expected_defaults": 0.0,
                    "random_expected_capture_rate": 0.0,
                    "random_expected_precision": prevalence,
                    "random_expected_lift": 1.0 if prevalence else np.nan,
                }]
            ),
            curve,
        ],
        ignore_index=True,
    )
    return RankingEvaluation(curve, prevalence, row_count, default_total)


def run_validation_ranking_analysis(selection: dict) -> dict:
    """Evaluate the validation ranking of the model selected by final selection.

    The validation set is used to select the model in ``run_final_selection``;
    therefore this result is a descriptive development diagnostic, not an
    unbiased final performance estimate. The test set is not read or scored.
    """
    from propensity_prediction.data.build import build_processed_dataset
    from propensity_prediction.data.split import split_dataset
    from propensity_prediction.models.final_selection import _prepare_features

    validation_results = selection["validation_results"]
    selected_row = validation_results.sort_values(
        by=["pr_auc", "roc_auc"], ascending=False
    ).iloc[0]
    model_name = selected_row["model"]
    feature_set = selected_row["feature_set"]
    search = selection["searches"][f"{model_name}_{feature_set}"]

    split = split_dataset(build_processed_dataset())
    X_validation, _, _, _ = _prepare_features(
        split.X_validation, feature_set == "engineered"
    )
    probabilities = search.best_estimator_.predict_proba(X_validation)[:, 1]
    evaluation = evaluate_risk_ranking(split.y_validation, probabilities)
    return {
        "selected_model": model_name,
        "feature_set": feature_set,
        "validation_selection_metrics": selected_row.to_dict(),
        "evaluation": evaluation,
    }
```

### `tests/test_decision_ranking.py`

```python
import numpy as np
import pandas as pd
import pytest

from propensity_prediction.decision.ranking import evaluate_risk_ranking


def test_ranking_curve_compares_risk_order_with_random_selection():
    result = evaluate_risk_ranking(
        y_true=np.array([1, 0, 1, 0]),
        probabilities=np.array([0.9, 0.8, 0.4, 0.1]),
    )

    curve = result.curve
    assert result.observation_count == 4
    assert result.default_count == 2
    assert result.population_default_rate == 0.5
    assert curve["capacity_fraction"].iloc[0] == 0.0
    assert curve["capacity_fraction"].iloc[-1] == 1.0
    assert curve["defaults_captured"].tolist() == [0, 1, 1, 2, 2]
    assert curve["default_capture_rate"].iloc[1] == 0.5
    assert curve["random_expected_capture_rate"].tolist() == [0, .25, .5, .75, 1]
    assert curve["lift_over_random"].iloc[1] == 2.0
    assert curve["lift_over_random"].iloc[-1] == 1.0


def test_equal_scores_are_kept_as_one_selection_group():
    result = evaluate_risk_ranking(
        pd.Series([1, 0, 1, 0]), pd.Series([0.8, 0.8, 0.2, 0.2])
    )

    assert result.curve["selected_count"].tolist() == [0, 2, 4]
    assert result.curve["defaults_captured"].tolist() == [0, 1, 2]
    assert result.curve["capacity_fraction"].tolist() == [0.0, 0.5, 1.0]


@pytest.mark.parametrize(
    "outcomes, scores, message",
    [
        ([0, 1], [0.2], "equal non-zero lengths"),
        ([0, 2], [0.2, 0.8], "binary values"),
        ([0, 1], [0.2, np.nan], "finite values"),
        ([0, 1], [0.2, 1.2], "between 0 and 1"),
        ([[0, 1]], [[0.2, 0.8]], "one-dimensional"),
    ],
)
def test_ranking_evaluation_rejects_invalid_inputs(outcomes, scores, message):
    with pytest.raises(ValueError, match=message):
        evaluate_risk_ranking(outcomes, scores)


def test_no_default_population_has_undefined_capture_and_lift():
    result = evaluate_risk_ranking([0, 0, 0], [0.9, 0.5, 0.1])

    assert result.default_count == 0
    assert result.curve["default_capture_rate"].isna().all()
    assert result.curve["lift_over_random"].isna().all()
```

---

<a id="phase-7-4-illustrative-review-capacity-scenarios"></a>

# Phase 7.4 — Illustrative Review-Capacity Scenarios

## Purpose and selected option

This step makes the continuous ranking comparison easier to discuss by
showing three illustrative review capacities: 5%, 10%, and 20% of the
validation population. They are examples only. The dataset contains no
analyst workload or capacity information, so these percentages do not
represent an operational commitment or recommendation.

For each scenario, the code reports the target review count, actual selected
count, defaults captured, precision, default capture rate, lift, and the
random-selection expectation at the **actual** selected capacity. These
metrics answer how the historical validation ranking behaved; they do not
estimate intervention impact or future results.

## Process, step by step

1. **Start from Step 7.3's curve.** The existing evaluation already groups
   customers with identical predicted probabilities and calculates
   cumulative performance at the end of each score group.
2. **Convert capacity to a count.** For a validation set with `n` rows, a
   target fraction `c` becomes `floor(n × c)` rows. Flooring ensures the
   scenario's stated maximum is not exceeded.
3. **Respect ties at the boundary.** The scenario takes the largest complete
   score group whose cumulative selected count is at most the target count.
   If the next score group would exceed capacity, it is not split. The queue
   may therefore be smaller than the target. `capacity_unused_count` makes
   this visible.
4. **Read ranking metrics at the actual selection.** Defaults captured,
   precision, default-capture rate, and lift come from that curve row. If no
   group fits, zero customers are selected; precision and lift are undefined.
5. **Compare with random selection at the same actual size.** Expected
   defaults are `actual capacity × total validation defaults`; expected
   capture rate is the actual capacity fraction. Comparing against the
   requested size instead would overstate the random baseline when ties force
   the risk-ranked queue to underfill.
6. **Return results from the runner.** The Step 7.3 runner now includes a
   `capacity_scenarios` DataFrame alongside its full curve. It uses the same
   validation diagnostic and does not read or score the test split.

## Interpreting the comparison

- `precision` is the share of selected customers who later defaulted in the
  historical validation data.
- `default_capture_rate` is the share of all observed validation defaults
  included in the selected queue.
- `lift_over_random` is precision divided by the validation population's
  default rate. A value of 1 matches the random-selection expectation.
- `random_expected_defaults` is an expectation and can be fractional.
- `capacity_unused_count` is unused headroom caused by flooring or by
  keeping a tied score group intact.

The model was selected using validation metrics, and these scenarios use
that same validation population. Treat the results as development examples,
not an unbiased performance estimate. The test split remains untouched for
a separately approved final assessment. No single scenario is selected as
an operational cutoff.

## Validation illustration from the selected model

The selected HistGradientBoosting model with engineered features was fit
using the training partition and the documented final parameters. Its
validation partition contains 4,500 rows, including 995 observed defaults
(22.11%). At each example capacity, the score groups fit the target exactly,
so no capacity was left unused:

| Illustrative capacity | Customers selected | Defaults captured | Capture rate | Precision | Random expected defaults | Lift over random |
|---:|---:|---:|---:|---:|---:|---:|
| 5% | 225 | 167 | 16.78% | 74.22% | 49.75 | 3.36× |
| 10% | 450 | 312 | 31.36% | 69.33% | 99.50 | 3.14× |
| 20% | 900 | 506 | 50.85% | 56.22% | 199.00 | 2.54× |

For example, at 10% the ranked group contains 312 of the 995 historical
validation defaults. Random selection of the same 450 customers would be
expected to contain 99.5 defaults. This comparison is retrospective and
does not establish that analyst review would prevent any of those defaults.

## How to use it

The usual Step 7.3 call returns the scenarios automatically:

```python
analysis = run_validation_ranking_analysis(selection)
print(analysis["capacity_scenarios"].to_string(index=False))
```

The default fractions are defined by `DEFAULT_CAPACITY_SCENARIOS`. The
summary function also accepts another tuple of illustrative fractions for
analysis, but that does not turn those values into known business capacity.

Focused checks:

```bash
venv/bin/pytest -q tests/test_decision_ranking.py
```

Result after this step: **14 passed**. The selected model was also fit on
training data and scored on validation data to produce the table above; the
test set was not used.

## Complete implementation and tests

The complete files below show the implementation after Step 7.4. Source
files are authoritative and should be consulted if they change later.

### `src/propensity_prediction/decision/ranking.py`

```python
"""Evaluate whether predicted risk ranks defaults ahead of random selection."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class RankingEvaluation:
    """Cumulative ranking curve and its population-level baseline details."""

    curve: pd.DataFrame
    population_default_rate: float
    observation_count: int
    default_count: int


DEFAULT_CAPACITY_SCENARIOS = (0.05, 0.10, 0.20)


def evaluate_risk_ranking(
    y_true: pd.Series | np.ndarray,
    probabilities: pd.Series | np.ndarray,
) -> RankingEvaluation:
    """Compare top-risk selection with random selection at every score tie.

    The curve advances by groups of equal probability so it never implies
    that customers with tied scores have a meaningful within-tie order.
    """
    outcomes = np.asarray(y_true)
    scores = np.asarray(probabilities, dtype=float)

    if outcomes.ndim != 1 or scores.ndim != 1:
        raise ValueError("y_true and probabilities must be one-dimensional.")
    if len(outcomes) == 0 or len(outcomes) != len(scores):
        raise ValueError("y_true and probabilities must have equal non-zero lengths.")
    if pd.isna(outcomes).any() or not np.isin(outcomes, [0, 1]).all():
        raise ValueError("y_true must contain only non-missing binary values 0 and 1.")
    if not np.isfinite(scores).all() or ((scores < 0) | (scores > 1)).any():
        raise ValueError("probabilities must be finite values between 0 and 1.")

    outcomes = outcomes.astype(int)
    order = np.argsort(-scores, kind="stable")
    sorted_scores = scores[order]
    sorted_outcomes = outcomes[order]
    group_ends = np.r_[
        np.flatnonzero(sorted_scores[:-1] != sorted_scores[1:]) + 1,
        len(sorted_scores),
    ]
    selected = group_ends
    captured_defaults = np.cumsum(sorted_outcomes)[group_ends - 1]
    default_total = int(outcomes.sum())
    row_count = len(outcomes)
    prevalence = default_total / row_count

    capacity = selected / row_count
    precision = captured_defaults / selected
    capture_rate = (
        captured_defaults / default_total
        if default_total
        else np.full(len(selected), np.nan)
    )
    lift = precision / prevalence if prevalence else np.full(len(selected), np.nan)

    curve = pd.DataFrame(
        {
            "selected_count": selected,
            "capacity_fraction": capacity,
            "minimum_selected_probability": sorted_scores[group_ends - 1],
            "defaults_captured": captured_defaults.astype(int),
            "precision": precision,
            "default_capture_rate": capture_rate,
            "lift_over_random": lift,
            "random_expected_defaults": capacity * default_total,
            "random_expected_capture_rate": capacity,
            "random_expected_precision": prevalence,
            "random_expected_lift": np.ones(len(selected)) if prevalence else np.nan,
        }
    )
    curve = pd.concat(
        [
            pd.DataFrame(
                [{
                    "selected_count": 0,
                    "capacity_fraction": 0.0,
                    "minimum_selected_probability": np.nan,
                    "defaults_captured": 0,
                    "precision": np.nan,
                    "default_capture_rate": 0.0 if default_total else np.nan,
                    "lift_over_random": np.nan,
                    "random_expected_defaults": 0.0,
                    "random_expected_capture_rate": 0.0,
                    "random_expected_precision": prevalence,
                    "random_expected_lift": 1.0 if prevalence else np.nan,
                }]
            ),
            curve,
        ],
        ignore_index=True,
    )
    return RankingEvaluation(curve, prevalence, row_count, default_total)


def summarize_capacity_scenarios(
    evaluation: RankingEvaluation,
    capacities: tuple[float, ...] = DEFAULT_CAPACITY_SCENARIOS,
) -> pd.DataFrame:
    """Summarize illustrative queue sizes without splitting tied risk scores.

    For each target capacity, select the largest complete score groups that
    fit within the requested count. The result may use less than the target
    capacity when the next tied group would exceed it.
    """
    if not capacities:
        raise ValueError("capacities must contain at least one fraction.")
    if any(not np.isfinite(value) or value <= 0 or value > 1 for value in capacities):
        raise ValueError("each capacity must be a finite fraction greater than 0 and at most 1.")

    curve = evaluation.curve
    rows = []
    for target_capacity in capacities:
        target_count = int(np.floor(evaluation.observation_count * target_capacity))
        eligible = curve.loc[curve["selected_count"] <= target_count]
        selected = eligible.iloc[-1]
        selected_count = int(selected["selected_count"])
        actual_capacity = selected_count / evaluation.observation_count
        rows.append(
            {
                "target_capacity_fraction": float(target_capacity),
                "target_review_count": target_count,
                "selected_count": selected_count,
                "actual_capacity_fraction": actual_capacity,
                "capacity_unused_count": target_count - selected_count,
                "defaults_captured": int(selected["defaults_captured"]),
                "precision": selected["precision"],
                "default_capture_rate": selected["default_capture_rate"],
                "lift_over_random": selected["lift_over_random"],
                "random_expected_defaults": actual_capacity * evaluation.default_count,
                "random_expected_capture_rate": actual_capacity,
            }
        )
    return pd.DataFrame(rows)


def run_validation_ranking_analysis(selection: dict) -> dict:
    """Evaluate the validation ranking of the model selected by final selection.

    The validation set is used to select the model in ``run_final_selection``;
    therefore this result is a descriptive development diagnostic, not an
    unbiased final performance estimate. The test set is not read or scored.
    """
    from propensity_prediction.data.build import build_processed_dataset
    from propensity_prediction.data.split import split_dataset
    from propensity_prediction.models.final_selection import _prepare_features

    validation_results = selection["validation_results"]
    selected_row = validation_results.sort_values(
        by=["pr_auc", "roc_auc"], ascending=False
    ).iloc[0]
    model_name = selected_row["model"]
    feature_set = selected_row["feature_set"]
    search = selection["searches"][f"{model_name}_{feature_set}"]

    split = split_dataset(build_processed_dataset())
    X_validation, _, _, _ = _prepare_features(
        split.X_validation, feature_set == "engineered"
    )
    probabilities = search.best_estimator_.predict_proba(X_validation)[:, 1]
    evaluation = evaluate_risk_ranking(split.y_validation, probabilities)
    capacity_scenarios = summarize_capacity_scenarios(evaluation)
    return {
        "selected_model": model_name,
        "feature_set": feature_set,
        "validation_selection_metrics": selected_row.to_dict(),
        "evaluation": evaluation,
        "capacity_scenarios": capacity_scenarios,
    }
```

### `tests/test_decision_ranking.py`

```python
import numpy as np
import pandas as pd
import pytest

from propensity_prediction.decision.ranking import (
    DEFAULT_CAPACITY_SCENARIOS,
    evaluate_risk_ranking,
    summarize_capacity_scenarios,
)


def test_ranking_curve_compares_risk_order_with_random_selection():
    result = evaluate_risk_ranking(
        y_true=np.array([1, 0, 1, 0]),
        probabilities=np.array([0.9, 0.8, 0.4, 0.1]),
    )

    curve = result.curve
    assert result.observation_count == 4
    assert result.default_count == 2
    assert result.population_default_rate == 0.5
    assert curve["capacity_fraction"].iloc[0] == 0.0
    assert curve["capacity_fraction"].iloc[-1] == 1.0
    assert curve["defaults_captured"].tolist() == [0, 1, 1, 2, 2]
    assert curve["default_capture_rate"].iloc[1] == 0.5
    assert curve["random_expected_capture_rate"].tolist() == [0, .25, .5, .75, 1]
    assert curve["lift_over_random"].iloc[1] == 2.0
    assert curve["lift_over_random"].iloc[-1] == 1.0


def test_equal_scores_are_kept_as_one_selection_group():
    result = evaluate_risk_ranking(
        pd.Series([1, 0, 1, 0]), pd.Series([0.8, 0.8, 0.2, 0.2])
    )

    assert result.curve["selected_count"].tolist() == [0, 2, 4]
    assert result.curve["defaults_captured"].tolist() == [0, 1, 2]
    assert result.curve["capacity_fraction"].tolist() == [0.0, 0.5, 1.0]


@pytest.mark.parametrize(
    "outcomes, scores, message",
    [
        ([0, 1], [0.2], "equal non-zero lengths"),
        ([0, 2], [0.2, 0.8], "binary values"),
        ([0, 1], [0.2, np.nan], "finite values"),
        ([0, 1], [0.2, 1.2], "between 0 and 1"),
        ([[0, 1]], [[0.2, 0.8]], "one-dimensional"),
    ],
)
def test_ranking_evaluation_rejects_invalid_inputs(outcomes, scores, message):
    with pytest.raises(ValueError, match=message):
        evaluate_risk_ranking(outcomes, scores)


def test_no_default_population_has_undefined_capture_and_lift():
    result = evaluate_risk_ranking([0, 0, 0], [0.9, 0.5, 0.1])

    assert result.default_count == 0
    assert result.curve["default_capture_rate"].isna().all()
    assert result.curve["lift_over_random"].isna().all()


def test_default_capacity_scenarios_compare_with_random_at_each_capacity():
    outcomes = np.array([1] * 20 + [0] * 80)
    scores = np.arange(100, 0, -1) / 100
    evaluation = evaluate_risk_ranking(outcomes, scores)

    scenarios = summarize_capacity_scenarios(evaluation)

    assert DEFAULT_CAPACITY_SCENARIOS == (0.05, 0.10, 0.20)
    assert scenarios["target_review_count"].tolist() == [5, 10, 20]
    assert scenarios["selected_count"].tolist() == [5, 10, 20]
    assert scenarios["defaults_captured"].tolist() == [5, 10, 20]
    assert scenarios["default_capture_rate"].tolist() == [0.25, 0.5, 1.0]
    assert scenarios["random_expected_defaults"].tolist() == [1, 2, 4]
    assert scenarios["lift_over_random"].tolist() == [5, 5, 5]


def test_capacity_scenario_does_not_split_a_score_tie_or_exceed_capacity():
    outcomes = [1, 0, 1, 0, 1, 0, 1, 0]
    scores = [0.9, 0.9, 0.9, 0.9, 0.5, 0.5, 0.1, 0.1]
    evaluation = evaluate_risk_ranking(outcomes, scores)

    scenarios = summarize_capacity_scenarios(evaluation, (0.25, 0.50))

    assert scenarios["target_review_count"].tolist() == [2, 4]
    assert scenarios["selected_count"].tolist() == [0, 4]
    assert scenarios["capacity_unused_count"].tolist() == [2, 0]
    assert (scenarios["selected_count"] <= scenarios["target_review_count"]).all()


@pytest.mark.parametrize("capacities", [(), (0.0,), (1.1,), (np.nan,)])
def test_capacity_scenarios_reject_invalid_capacity_values(capacities):
    evaluation = evaluate_risk_ranking([0, 1], [0.2, 0.8])

    with pytest.raises(ValueError, match="capacit"):
        summarize_capacity_scenarios(evaluation, capacities)
```

---

The original supplementary assessment below predates completion of Steps 7.5–7.7. Its statement that Step 7.5 remained to be done is preserved as part of the original record; the completed Step 7.5 implementation and later recommendation are documented in their sections below.

<a id="supplementary-phase-7-holdout-ranking-diagnostic"></a>

# Supplementary Phase 7 Analysis — Holdout Ranking Diagnostic

## Purpose and boundary

This supplementary analysis evaluates the already selected HistGradientBoosting model with
engineered features on the held-out 15% test split. Model choice and
hyperparameters remain those established in Phase 5. The test data is used
here once to calculate ranking and capacity metrics; it is not used to
retune the model or change the 5%, 10%, and 20% illustrative scenarios.

This is **not a numbered step in the original Phase 7 plan**. It adds ranking
metrics to the Phase 5 holdout results. Original Step 7.5, implementing the
deterministic decision engine, remains to be done.

**Qualification:** [Phase 5's report](model_development_and_evaluation.md)
already reports standard metrics on this same test split. Therefore this is
not the first use of the holdout and is not an independent replication. The
model was selected using validation results, and the capacity percentages
were fixed before this supplementary analysis, so it does not select a new
model or capacity using test outcomes. Treat the new ranking metrics as a
secondary analysis of the existing holdout. Any future decisions informed
by these results would require a new independent evaluation population for
an unbiased final assessment.

The evaluation covers both overall model performance and risk-prioritization
performance. The capacity results compare the selected queue to random
selection at the same actual size. This is a historical ranking assessment,
not evidence that analyst review prevents default or that the example
capacities are operationally suitable.

## Runner process, step by step

1. **Use the established model selection.** The runner sorts the supplied
   `validation_results` by PR-AUC and then ROC-AUC, matching the established
   final model-selection rule. It retrieves the already fitted best estimator
   from the matching `searches` entry. The test set is not involved in this
   choice.
2. **Recreate the fixed split.** `build_processed_dataset()` and
   `split_dataset()` use the project's existing data pipeline and random
   state. Only `X_test` and `y_test` are passed to this evaluation.
3. **Prepare the test predictors consistently.** `_prepare_features()` drops
   the identifier and applies engineered features when the selected feature
   set requires them. The target is not included in the predictor frame.
4. **Score the test split once.** The selected fitted estimator generates
   default probabilities for `X_test`. No estimator is fit or tuned in this
   runner.
5. **Calculate standard test metrics.** The project's existing
   `_evaluate_probabilities()` calculates ROC-AUC, PR-AUC, Brier score, and
   threshold-dependent classification metrics at 0.5. The 0.5 values remain
   descriptive and are not an operational review threshold.
6. **Build ranking and capacity reports.** `evaluate_risk_ranking()` computes
   the complete test ranking curve, and `summarize_capacity_scenarios()`
   reports the previously fixed capacity examples. Tied scores remain
   indivisible and the queue cannot exceed a target capacity.
7. **Return one final report.** The returned dictionary includes selected
   model metadata, validation selection metrics (for traceability), test
   metrics, ranking curve, and capacity scenarios. It does not return or
   expose test outcomes as future prediction inputs.

## Test-set results

The test partition contains **4,500 rows**, of which **996** defaulted
(22.13%). Overall metrics:

| Metric | Test result |
|---|---:|
| ROC-AUC | 0.7800 |
| PR-AUC | 0.5515 |
| Brier score | 0.1352 |
| Accuracy at 0.5 | 0.8173 |
| Precision at 0.5 | 0.6642 |
| Recall at 0.5 | 0.3534 |
| F1 at 0.5 | 0.4613 |

Confusion matrix at 0.5 (rows are actual `0`, `1`; columns are predicted
`0`, `1`):

```text
[[3326, 178],
 [ 644, 352]]
```

Ranking results for the illustrative capacities:

| Illustrative capacity | Customers selected | Defaults captured | Capture rate | Precision | Random expected defaults | Lift over random |
|---:|---:|---:|---:|---:|---:|---:|
| 5% | 225 | 169 | 16.97% | 75.11% | 49.80 | 3.39× |
| 10% | 450 | 313 | 31.43% | 69.56% | 99.60 | 3.14× |
| 20% | 900 | 512 | 51.41% | 56.89% | 199.20 | 2.57× |

All three capacities were attained exactly; no score tie crossed a capacity
boundary in this split. For example, the 10% ranked queue captured 313 of
the 996 historical test defaults, compared with 99.6 expected under random
selection of 450 customers. That difference describes ranking performance;
it does not estimate an intervention's effect.

The test metrics are close to the earlier validation metrics. This supports
the model's ranking behavior on this particular held-out sample, but does
not establish performance on modern customers, other populations, or future
time periods.

## How to run it

After the established model-selection process returns its `selection`
dictionary, run the final assessment once:

```python
from propensity_prediction.decision.ranking import run_test_ranking_analysis
from propensity_prediction.models.final_selection import run_final_selection

selection = run_final_selection()
test_report = run_test_ranking_analysis(selection)
print(test_report["test_metrics"])
print(test_report["capacity_scenarios"].to_string(index=False))
```

The selection process may take time because it runs cross-validated model
searches. The test runner uses its selected, already fitted estimator and
does not search or fit again. After the final assessment, test metrics should
not guide additional model or scenario choices; further development would
require a new independent test population for a fresh final assessment.

## Focused tests

The runner test in
[`test_decision_ranking.py`](../tests/test_decision_ranking.py) supplies a
mock model and split. It checks that the selected model is used, test-row
counts and defaults are reported, a known perfect ordering yields ROC-AUC
1.0, and all three capacity scenarios are returned. The ranking and scenario
math tests also cover ties, invalid data, and random references.

Run the decision-focused tests:

```bash
venv/bin/pytest -q tests/test_decision_ranking.py tests/test_decision_inputs_audit.py
```

Result for the decision-focused test suite: **20 passed**. The real report above was calculated
by fitting the already selected configuration on training data and scoring
the test split once for this supplementary ranking analysis. Phase 5 had
already published standard metrics for this holdout.

## Complete code added for this supplementary analysis

The source file is authoritative. The code below is the complete new runner
added for this analysis; earlier ranking and capacity functions are documented in
[`risk_ranking_baseline.md`](#phase-7-3-risk-ranking-compared-with-random-selection) and
[`capacity_scenarios.md`](#phase-7-4-illustrative-review-capacity-scenarios).

### `run_test_ranking_analysis()` in `src/propensity_prediction/decision/ranking.py`

```python
def run_test_ranking_analysis(selection: dict) -> dict:
    """Score the locked selected model on the held-out test split once here.

    Model choice comes from the validation results in ``selection``. This
    function does not fit, tune, or choose a model using test data. The
    project already reported standard test metrics in Phase 5; this adds a
    secondary ranking analysis of the same held-out split.
    """
    from propensity_prediction.data.build import build_processed_dataset
    from propensity_prediction.data.split import split_dataset
    from propensity_prediction.models.final_selection import (
        _evaluate_probabilities,
        _prepare_features,
    )

    validation_results = selection["validation_results"]
    selected_row = validation_results.sort_values(
        by=["pr_auc", "roc_auc"], ascending=False
    ).iloc[0]
    model_name = selected_row["model"]
    feature_set = selected_row["feature_set"]
    search = selection["searches"][f"{model_name}_{feature_set}"]

    split = split_dataset(build_processed_dataset())
    X_test, _, _, _ = _prepare_features(split.X_test, feature_set == "engineered")
    probabilities = search.best_estimator_.predict_proba(X_test)[:, 1]
    metrics = _evaluate_probabilities(split.y_test, probabilities)
    evaluation = evaluate_risk_ranking(split.y_test, probabilities)
    capacity_scenarios = summarize_capacity_scenarios(evaluation)
    return {
        "selected_model": model_name,
        "feature_set": feature_set,
        "validation_selection_metrics": selected_row.to_dict(),
        "test_metrics": metrics,
        "evaluation": evaluation,
        "capacity_scenarios": capacity_scenarios,
    }
```

### New test in `tests/test_decision_ranking.py`

```python
def test_test_analysis_uses_selected_model_and_test_partition_only(monkeypatch):
    from propensity_prediction.data import build, split
    from propensity_prediction.models import final_selection

    X_test = pd.DataFrame({"ID": np.arange(20)})
    y_test = pd.Series([1] * 6 + [0] * 14, name="DEFAULT")
    dataset_split = SimpleNamespace(X_test=X_test, y_test=y_test)

    class FixedProbabilityModel:
        def predict_proba(self, X):
            scores = np.linspace(0.99, 0.01, len(X))
            return np.column_stack([1 - scores, scores])

    selection = {
        "validation_results": pd.DataFrame(
            [{"model": "chosen", "feature_set": "original", "pr_auc": 0.5, "roc_auc": 0.7}]
        ),
        "searches": {
            "chosen_original": SimpleNamespace(best_estimator_=FixedProbabilityModel())
        },
    }
    monkeypatch.setattr(build, "build_processed_dataset", lambda: object())
    monkeypatch.setattr(split, "split_dataset", lambda _: dataset_split)
    monkeypatch.setattr(
        final_selection,
        "_prepare_features",
        lambda X, use_engineered: (X.copy(), [], [], []),
    )

    result = run_test_ranking_analysis(selection)

    assert result["selected_model"] == "chosen"
    assert result["feature_set"] == "original"
    assert result["evaluation"].observation_count == len(X_test)
    assert result["evaluation"].default_count == int(y_test.sum())
    assert result["test_metrics"]["roc_auc"] == 1.0
    assert result["capacity_scenarios"]["target_review_count"].tolist() == [1, 2, 4]
```

---

<a id="phase-7-5-deterministic-review-queue-engine"></a>

# Phase 7.5 — Deterministic Review-Queue Engine

## Purpose and selected approach

The engine translates a list of customer identifiers, predicted default
probabilities, and an explicit review-count capacity into a reproducible
review queue. It implements the agreed probability-only prioritization rule.
It does not fit a model, use observed `DEFAULT`, recommend an intervention,
or estimate financial loss.

The selected design keeps every equal-probability group together. If the
next group would exceed the remaining capacity, that group and all lower
probability groups are left out. This keeps the queue within capacity and
avoids claiming that one customer is riskier than another when their scores
are identical. The tradeoff is that capacity can be unused at a tie boundary.

## Process, step by step

1. **Keep model and decision code separate.** `build_review_queue()` accepts
   identifiers and probabilities supplied by a caller. It has no estimator
   argument and cannot retrain or alter the selected model. `DEFAULT` is not
   an input to the function.
2. **Check the input contract.** IDs and scores must be one-dimensional,
   equally sized, non-empty arrays. IDs must be present and unique. Scores
   must be finite probabilities from zero to one. Capacity must be a
   non-negative integer.
3. **Sort by risk.** Customers are sorted from highest to lowest predicted
   probability. A stable sort preserves the input order within equal-score
   groups, but that order does not affect rank or queue inclusion.
4. **Assign shared ranks.** All customers with the same score receive the
   same competition rank. For example, if two customers tie at the top,
   both have rank 1 and the next group starts at rank 3.
5. **Apply the capacity.** Complete score groups are included if they fit.
   The first group that does not fit is left out, followed by all lower
   groups. This rule ensures a lower-risk customer cannot displace a
   higher-risk customer.
6. **Explain each result.** Each customer gets a boolean selection field, a
   machine-readable reason code, and a human-readable reason. The result
   summary includes requested capacity, capacity available in this
   population, selected count, and unused capacity.
7. **Return an auditable queue.** The queue includes the customer ID,
   probability, shared rank, selection status, and reason. It has no
   observed outcome, exposure proxy, or intervention recommendation.

## Reason codes

| Code | Meaning |
|---|---|
| `SELECTED_BY_RISK_RANKING` | The complete score group fits within the review capacity. |
| `NOT_SELECTED_TIED_GROUP_EXCEEDS_CAPACITY` | Including this tied group intact would exceed the remaining capacity. |
| `NOT_SELECTED_BELOW_CAPACITY_BOUNDARY` | This lower-risk group falls after the capacity boundary. |
| `NOT_SELECTED_ZERO_CAPACITY` | The caller supplied zero review capacity. |

## Example use

The function takes a count, not a percentage. For the 4,500-row validation
split, the illustrative 5%, 10%, and 20% counts are 225, 450, and 900:

```python
from propensity_prediction.decision.engine import build_review_queue

queue_5_percent = build_review_queue(
    customer_ids=validation_ids,
    probabilities=validation_probabilities,
    max_review_count=225,
)
print(queue_5_percent.customers.head())
print(queue_5_percent.selected_count, queue_5_percent.unused_capacity)
```

Run the function separately for the other capacities. These remain
illustrative scenarios, not known analyst capacity. For the held-out test
results, use the same call shape with probabilities and IDs aligned to the
test rows; do not pass test outcomes into the engine.

## Focused tests

[`test_decision_engine.py`](../tests/test_decision_engine.py) checks descending
ranking, shared ranks for tied probabilities, capacity enforcement, precise
reason codes, zero and oversized capacities, and rejection of malformed
inputs. It also verifies that a tie crossing the capacity boundary is not
split.

Run the focused tests with:

```bash
venv/bin/pytest -q tests/test_decision_engine.py
```

Result: **13 passed**.

## Complete implementation

The implementation source is authoritative. This listing contains the
complete engine added in this step.

### `src/propensity_prediction/decision/engine.py`

```python
"""Deterministic capacity-limited customer review queue construction."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


SELECTED_REASON = "SELECTED_BY_RISK_RANKING"
BELOW_CAPACITY_REASON = "NOT_SELECTED_BELOW_CAPACITY_BOUNDARY"
TIE_BOUNDARY_REASON = "NOT_SELECTED_TIED_GROUP_EXCEEDS_CAPACITY"
ZERO_CAPACITY_REASON = "NOT_SELECTED_ZERO_CAPACITY"


@dataclass(frozen=True)
class ReviewQueueResult:
    """Sorted customer queue and capacity accounting."""

    customers: pd.DataFrame
    requested_capacity: int
    target_review_count: int
    selected_count: int
    unused_capacity: int


def build_review_queue(
    customer_ids: pd.Series | np.ndarray,
    probabilities: pd.Series | np.ndarray,
    max_review_count: int,
) -> ReviewQueueResult:
    """Rank customers by probability and select whole score groups up to capacity.

    Customers with the same probability share a competition rank. If a tied
    group would exceed the remaining capacity, that entire group and all
    lower-risk groups are left out so the queue never invents a within-tie
    order or exceeds the capacity.
    """
    ids = np.asarray(customer_ids)
    scores = np.asarray(probabilities, dtype=float)

    if ids.ndim != 1 or scores.ndim != 1:
        raise ValueError("customer_ids and probabilities must be one-dimensional.")
    if len(ids) == 0 or len(ids) != len(scores):
        raise ValueError("customer_ids and probabilities must have equal non-zero lengths.")
    if pd.isna(ids).any():
        raise ValueError("customer_ids must not contain missing values.")
    if pd.Index(ids).has_duplicates:
        raise ValueError("customer_ids must be unique.")
    if not np.isfinite(scores).all() or ((scores < 0) | (scores > 1)).any():
        raise ValueError("probabilities must be finite values between 0 and 1.")
    if (
        isinstance(max_review_count, (bool, np.bool_))
        or not isinstance(max_review_count, (int, np.integer))
        or max_review_count < 0
    ):
        raise ValueError("max_review_count must be a non-negative integer.")

    row_count = len(ids)
    target_count = min(int(max_review_count), row_count)
    order = np.argsort(-scores, kind="stable")
    sorted_ids = ids[order]
    sorted_scores = scores[order]
    group_starts = np.r_[
        0,
        np.flatnonzero(sorted_scores[:-1] != sorted_scores[1:]) + 1,
    ]
    group_ends = np.r_[group_starts[1:], row_count]

    ranks = np.empty(row_count, dtype=int)
    selected = np.zeros(row_count, dtype=bool)
    reason_codes = np.empty(row_count, dtype=object)

    if target_count == 0:
        reason_codes[:] = ZERO_CAPACITY_REASON
    else:
        selected_count = 0
        capacity_boundary_reached = False
        for start, end in zip(group_starts, group_ends):
            ranks[start:end] = start + 1
            group_size = end - start
            if capacity_boundary_reached:
                reason_codes[start:end] = BELOW_CAPACITY_REASON
            elif selected_count + group_size <= target_count:
                selected[start:end] = True
                reason_codes[start:end] = SELECTED_REASON
                selected_count += group_size
            else:
                if group_size > 1 and selected_count < target_count:
                    reason_codes[start:end] = TIE_BOUNDARY_REASON
                else:
                    reason_codes[start:end] = BELOW_CAPACITY_REASON
                capacity_boundary_reached = True

    if target_count == 0:
        ranks[:] = np.repeat(group_starts, group_ends - group_starts) + 1

    reason_text = {
        SELECTED_REASON: (
            "Selected by descending predicted default probability within the stated capacity."
        ),
        BELOW_CAPACITY_REASON: (
            "Not selected because this lower-risk score group falls beyond the capacity boundary."
        ),
        TIE_BOUNDARY_REASON: (
            "Not selected because keeping this equal-probability group intact would exceed capacity."
        ),
        ZERO_CAPACITY_REASON: "Not selected because review capacity is zero.",
    }
    customers = pd.DataFrame(
        {
            "customer_id": sorted_ids,
            "predicted_default_probability": sorted_scores,
            "risk_rank": ranks,
            "selected_for_review": selected,
            "reason_code": reason_codes,
        }
    )
    customers["reason"] = customers["reason_code"].map(reason_text)
    selected_count = int(selected.sum())
    return ReviewQueueResult(
        customers=customers,
        requested_capacity=int(max_review_count),
        target_review_count=target_count,
        selected_count=selected_count,
        unused_capacity=target_count - selected_count,
    )
```

### `tests/test_decision_engine.py`

```python
import numpy as np
import pandas as pd
import pytest

from propensity_prediction.decision.engine import (
    BELOW_CAPACITY_REASON,
    SELECTED_REASON,
    TIE_BOUNDARY_REASON,
    ZERO_CAPACITY_REASON,
    build_review_queue,
)


def test_review_queue_ranks_descending_and_selects_within_capacity():
    result = build_review_queue(
        customer_ids=["a", "b", "c", "d", "e"],
        probabilities=[0.2, 0.9, 0.9, 0.8, 0.7],
        max_review_count=3,
    )

    queue = result.customers
    assert queue["customer_id"].tolist() == ["b", "c", "d", "e", "a"]
    assert queue["risk_rank"].tolist() == [1, 1, 3, 4, 5]
    assert queue["selected_for_review"].tolist() == [True, True, True, False, False]
    assert queue["reason_code"].tolist() == [
        SELECTED_REASON,
        SELECTED_REASON,
        SELECTED_REASON,
        BELOW_CAPACITY_REASON,
        BELOW_CAPACITY_REASON,
    ]
    assert result.target_review_count == 3
    assert result.selected_count == 3
    assert result.unused_capacity == 0


def test_tied_group_is_not_split_when_it_crosses_capacity_boundary():
    result = build_review_queue(
        customer_ids=["a", "b", "c", "d", "e"],
        probabilities=[0.95, 0.8, 0.8, 0.7, 0.1],
        max_review_count=2,
    )

    queue = result.customers
    assert queue["customer_id"].tolist() == ["a", "b", "c", "d", "e"]
    assert queue["risk_rank"].tolist() == [1, 2, 2, 4, 5]
    assert queue["selected_for_review"].tolist() == [True, False, False, False, False]
    assert queue["reason_code"].tolist() == [
        SELECTED_REASON,
        TIE_BOUNDARY_REASON,
        TIE_BOUNDARY_REASON,
        BELOW_CAPACITY_REASON,
        BELOW_CAPACITY_REASON,
    ]
    assert result.selected_count == 1
    assert result.unused_capacity == 1
    assert result.selected_count <= result.target_review_count


def test_zero_capacity_selects_no_customer_and_still_assigns_tied_ranks():
    result = build_review_queue(["a", "b", "c"], [0.4, 0.9, 0.9], 0)

    assert result.customers["risk_rank"].tolist() == [1, 1, 3]
    assert not result.customers["selected_for_review"].any()
    assert result.customers["reason_code"].eq(ZERO_CAPACITY_REASON).all()
    assert result.selected_count == 0
    assert result.unused_capacity == 0


def test_capacity_larger_than_population_selects_everyone():
    result = build_review_queue([10, 11], [0.2, 0.8], np.int64(10))

    assert result.target_review_count == 2
    assert result.requested_capacity == 10
    assert result.customers["selected_for_review"].all()
    assert result.unused_capacity == 0


@pytest.mark.parametrize(
    "ids, scores, capacity, message",
    [
        (["a", "b"], [0.2], 1, "equal non-zero lengths"),
        ([["a", "b"]], [[0.2, 0.8]], 1, "one-dimensional"),
        (["a", None], [0.2, 0.8], 1, "missing values"),
        (["a", "a"], [0.2, 0.8], 1, "unique"),
        (["a", "b"], [0.2, np.nan], 1, "finite values"),
        (["a", "b"], [0.2, 1.1], 1, "between 0 and 1"),
        (["a", "b"], [0.2, 0.8], -1, "non-negative integer"),
        (["a", "b"], [0.2, 0.8], 1.5, "non-negative integer"),
        (["a", "b"], [0.2, 0.8], True, "non-negative integer"),
    ],
)
def test_review_queue_rejects_invalid_inputs(ids, scores, capacity, message):
    with pytest.raises(ValueError, match=message):
        build_review_queue(ids, scores, capacity)
```

---

<a id="phase-7-6-evaluate-review-policy-scenarios"></a>

# Phase 7.6 — Evaluate Review-Policy Scenarios

## Purpose and scope

This step applies the deterministic queue engine from Step 7.5 to the
validation population and compares each review queue with random selection
at the same actual workload. It evaluates the agreed 5%, 10%, and 20%
capacity examples. No new probability threshold, exposure proxy, or
intervention is introduced.

The random benchmark is calculated as an expectation, rather than by
generating one arbitrary random sample. If the queue actually selects `k`
customers from `n`, random selection is expected to capture
`k × observed_default_rate` defaults. Using the actual queue size keeps the
comparison fair if a tied score group makes the engine underfill a target.

This validation analysis is descriptive. The selected model was selected
using validation metrics, and this same split was used for ranking
development. Results may therefore be optimistic and do not establish
future performance or the effect of analyst review.

## Process, step by step

1. **Supply aligned inputs.** Customer IDs, predicted probabilities, and
   observed validation outcomes must be in the same row order. The target
   is passed separately and is used only to evaluate the resulting queue.
2. **Validate outcomes and capacity scenarios.** Outcomes must be binary
   and non-missing; capacity fractions must be finite numbers in `(0, 1]`.
   The queue engine validates IDs, probabilities, and the integer capacity.
3. **Convert each fraction to a maximum count.** For a validation set of
   `n` customers and capacity `c`, the target count is `floor(n × c)`.
4. **Build each queue with the Step 7.5 engine.** The engine ranks by
   probability and keeps equal-score groups together. A group that crosses
   the boundary is left out, as are lower-risk groups.
5. **Look up outcomes only after queue selection.** The evaluator maps
   selected IDs back to observed validation outcomes. These outcomes never
   enter the queue engine or affect ranking.
6. **Calculate queue performance.** Each scenario reports target and
   selected counts, actual capacity, unused capacity, defaults captured,
   precision, capture rate, and lift over random.
7. **Calculate the random reference at actual workload.** Expected random
   defaults are `selected_count × validation_default_rate`. The table also
   reports additional observed defaults above that expectation.
8. **Return the queues and summary.** The result includes each full queue
   as well as one scenario comparison DataFrame, allowing an analyst to
   inspect both the aggregate and customer-level policy output.

## Validation results

The validation partition contains **4,500 rows** and **995 defaults**; its
default rate is 22.11%. The engine filled each of the three example
capacities exactly in this split:

| Capacity | Customers selected | Defaults captured | Capture rate | Precision | Random expected defaults | Additional defaults vs random expectation | Lift |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 5% | 225 | 167 | 16.78% | 74.22% | 49.75 | 117.25 | 3.36× |
| 10% | 450 | 312 | 31.36% | 69.33% | 99.50 | 212.50 | 3.14× |
| 20% | 900 | 506 | 50.85% | 56.22% | 199.00 | 307.00 | 2.54× |

For example, the 10% queue selected 450 customers and included 312 of the
995 observed defaults. A random group of 450 customers would be expected to
include 99.5 defaults. This is a retrospective comparison of predicted-risk
ranking; it is not an estimate of defaults prevented by review.

The fact that all three capacities were filled exactly is a result of these
validation scores. Other data may have a tie at a capacity boundary, in
which case the queue can underfill; the random expectation will then use
that smaller actual selected count.

## How to run it

After producing validation probabilities from the selected model, call:

```python
from propensity_prediction.decision.policy_evaluation import (
    evaluate_review_capacity_policies,
)

result = evaluate_review_capacity_policies(
    customer_ids=validation_ids,
    probabilities=validation_probabilities,
    y_true=validation_defaults,
)
print(result.scenario_comparison.to_string(index=False))
print(result.queues[0.10].customers.head())
```

The default scenarios are imported from
`decision.ranking.DEFAULT_CAPACITY_SCENARIOS`. You can pass a different
tuple for a clearly labeled analysis; those values remain assumptions until
real operating capacity is supplied.

## Focused tests

[`test_policy_evaluation.py`](../tests/test_policy_evaluation.py) checks
expected random counts at equal workloads, scenario output, tied-score
underfill, validation of targets and capacity fractions, and the zero-row
selection case. The existing decision-engine tests check customer-level
queue construction and reason codes.

Run all decision-focused tests with:

```bash
venv/bin/pytest -q tests/test_policy_evaluation.py tests/test_decision_engine.py tests/test_decision_ranking.py tests/test_decision_inputs_audit.py
```

Result: **42 passed**.

## Complete implementation

The implementation source is authoritative. This is the complete evaluator
created for Step 7.6.

### `src/propensity_prediction/decision/policy_evaluation.py`

```python
"""Evaluate capacity-based review queues against random selection."""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Real

import numpy as np
import pandas as pd

from propensity_prediction.decision.engine import (
    ReviewQueueResult,
    build_review_queue,
)
from propensity_prediction.decision.ranking import DEFAULT_CAPACITY_SCENARIOS


@dataclass(frozen=True)
class PolicyEvaluationResult:
    """Scenario comparisons, constructed queues, and population reference."""

    scenario_comparison: pd.DataFrame
    queues: dict[float, ReviewQueueResult]
    population_default_rate: float
    observation_count: int
    default_count: int


def evaluate_review_capacity_policies(
    customer_ids: pd.Series | np.ndarray,
    probabilities: pd.Series | np.ndarray,
    y_true: pd.Series | np.ndarray,
    capacities: tuple[float, ...] = DEFAULT_CAPACITY_SCENARIOS,
) -> PolicyEvaluationResult:
    """Evaluate engine-built queues versus random selection at equal workload.

    Random expected defaults are calculated at the queue's actual selected
    count. This keeps the comparison fair if tied scores cause the queue to
    use less than its requested capacity.
    """
    ids = np.asarray(customer_ids)
    outcomes = np.asarray(y_true)
    scores = np.asarray(probabilities, dtype=float)

    if ids.ndim != 1 or scores.ndim != 1 or outcomes.ndim != 1:
        raise ValueError("customer_ids, probabilities, and y_true must be one-dimensional.")
    if len(outcomes) == 0 or len(outcomes) != len(ids):
        raise ValueError("customer_ids and y_true must have equal non-zero lengths.")
    if pd.isna(outcomes).any() or not np.isin(outcomes, [0, 1]).all():
        raise ValueError("y_true must contain only non-missing binary values 0 and 1.")
    if not capacities:
        raise ValueError("capacities must contain at least one fraction.")
    if any(
        isinstance(capacity, (bool, np.bool_))
        or not isinstance(capacity, Real)
        or not np.isfinite(capacity)
        or capacity <= 0
        or capacity > 1
        for capacity in capacities
    ):
        raise ValueError("each capacity must be a finite fraction greater than 0 and at most 1.")

    outcomes = outcomes.astype(int)
    row_count = len(outcomes)
    default_count = int(outcomes.sum())
    prevalence = default_count / row_count
    outcome_by_id = pd.Series(outcomes, index=ids)
    scenario_rows = []
    queues = {}

    for capacity in capacities:
        capacity = float(capacity)
        target_count = int(np.floor(row_count * capacity))
        queue_result = build_review_queue(ids, scores, target_count)
        queues[capacity] = queue_result

        selected_ids = queue_result.customers.loc[
            queue_result.customers["selected_for_review"], "customer_id"
        ]
        selected_outcomes = outcome_by_id.loc[selected_ids.to_numpy()].to_numpy()
        captured_defaults = int(selected_outcomes.sum())
        selected_count = queue_result.selected_count
        actual_capacity = selected_count / row_count
        precision = captured_defaults / selected_count if selected_count else np.nan
        capture_rate = (
            captured_defaults / default_count
            if default_count
            else np.nan
        )
        lift = precision / prevalence if selected_count and prevalence else np.nan
        random_expected_defaults = actual_capacity * default_count

        scenario_rows.append(
            {
                "target_capacity_fraction": capacity,
                "target_review_count": queue_result.target_review_count,
                "selected_count": selected_count,
                "actual_capacity_fraction": actual_capacity,
                "capacity_unused_count": queue_result.unused_capacity,
                "defaults_captured": captured_defaults,
                "precision": precision,
                "default_capture_rate": capture_rate,
                "lift_over_random": lift,
                "random_expected_defaults": random_expected_defaults,
                "random_expected_capture_rate": actual_capacity,
                "random_expected_precision": prevalence,
                "additional_defaults_vs_random_expectation": (
                    captured_defaults - random_expected_defaults
                ),
            }
        )

    return PolicyEvaluationResult(
        scenario_comparison=pd.DataFrame(scenario_rows),
        queues=queues,
        population_default_rate=prevalence,
        observation_count=row_count,
        default_count=default_count,
    )
```

### `tests/test_policy_evaluation.py`

```python
import numpy as np
import pytest

from propensity_prediction.decision.policy_evaluation import (
    evaluate_review_capacity_policies,
)


def test_capacity_policies_compare_engine_queue_with_random_expectation():
    outcomes = np.array([1] * 20 + [0] * 80)
    scores = np.arange(100, 0, -1) / 100
    ids = np.arange(100)

    result = evaluate_review_capacity_policies(ids, scores, outcomes)

    scenarios = result.scenario_comparison
    assert result.observation_count == 100
    assert result.default_count == 20
    assert result.population_default_rate == 0.2
    assert scenarios["target_review_count"].tolist() == [5, 10, 20]
    assert scenarios["selected_count"].tolist() == [5, 10, 20]
    assert scenarios["defaults_captured"].tolist() == [5, 10, 20]
    assert scenarios["random_expected_defaults"].tolist() == [1, 2, 4]
    assert scenarios["additional_defaults_vs_random_expectation"].tolist() == [4, 8, 16]
    assert result.queues[0.05].customers.loc[lambda q: q["selected_for_review"], "customer_id"].tolist() == list(range(5))


def test_random_reference_uses_actual_workload_when_tie_causes_underfill():
    ids = np.arange(8)
    probabilities = [0.95, 0.8, 0.8, 0.7, 0.1, 0.05, 0.04, 0.03]
    outcomes = [1, 1, 0, 0, 1, 0, 1, 0]

    result = evaluate_review_capacity_policies(
        ids, probabilities, outcomes, capacities=(0.25, 0.50)
    )

    scenarios = result.scenario_comparison
    assert scenarios["target_review_count"].tolist() == [2, 4]
    assert scenarios["selected_count"].tolist() == [1, 4]
    assert scenarios["capacity_unused_count"].tolist() == [1, 0]
    assert scenarios["defaults_captured"].tolist() == [1, 2]
    assert scenarios["random_expected_defaults"].tolist() == [0.5, 2.0]
    assert scenarios["additional_defaults_vs_random_expectation"].tolist() == [0.5, 0.0]


@pytest.mark.parametrize(
    "ids, scores, outcomes, capacities, message",
    [
        ([1, 2], [0.1, 0.9], [0], (0.5,), "equal non-zero lengths"),
        ([1, 2], [0.1, 0.9], [0, 2], (0.5,), "binary values"),
        ([1, 2], [0.1, 0.9], [0, 1], (), "at least one"),
        ([1, 2], [0.1, 0.9], [0, 1], (0.0,), "capacity"),
        ([1, 2], [0.1, 0.9], [0, 1], (1.1,), "capacity"),
        ([1, 2], [0.1, 0.9], [0, 1], (np.nan,), "capacity"),
    ],
)
def test_policy_evaluation_rejects_invalid_inputs(ids, scores, outcomes, capacities, message):
    with pytest.raises(ValueError, match=message):
        evaluate_review_capacity_policies(ids, scores, outcomes, capacities)


def test_zero_selected_customers_have_undefined_precision():
    result = evaluate_review_capacity_policies(
        [1, 2, 3, 4], [0.9, 0.8, 0.7, 0.6], [1, 0, 1, 0], capacities=(0.1,)
    )

    scenario = result.scenario_comparison.iloc[0]
    assert scenario["target_review_count"] == 0
    assert scenario["selected_count"] == 0
    assert np.isnan(scenario["precision"])
    assert np.isnan(scenario["lift_over_random"])
```

---

<a id="phase-7-7-decision-recommendations-and-limits"></a>

# Phase 7.7 — Decision Recommendations and Limits

## Recommendation

Use the predicted-default-probability ranking as a **prototype aid for
analyst attention**. If an analyst team wants to inspect a limited number of
historical-style cases, the deterministic queue can rank the supplied
customers and apply an explicitly supplied review capacity. Treat the 5%,
10%, and 20% scenarios as examples for discussion, not as recommended
operating levels.

The score estimates relative default risk from the model's available
historical information. It does not say that a customer will default with
certainty. Queue inclusion means “ranked within this stated review
capacity,” not “take a particular action.”

## Evidence from the completed analysis

The validation split contains 4,500 customers and 995 observed defaults
(22.11%). The test split contains 4,500 customers and 996 defaults
(22.13%). The engine kept the score groups intact and attained the requested
counts in both splits.

| Split | Capacity | Customers selected | Defaults captured | Capture rate | Precision | Random expected defaults | Lift over random |
|---|---:|---:|---:|---:|---:|---:|---:|
| Validation | 5% | 225 | 167 | 16.78% | 74.22% | 49.75 | 3.36× |
| Validation | 10% | 450 | 312 | 31.36% | 69.33% | 99.50 | 3.14× |
| Validation | 20% | 900 | 506 | 50.85% | 56.22% | 199.00 | 2.54× |
| Test | 5% | 225 | 169 | 16.97% | 75.11% | 49.80 | 3.39× |
| Test | 10% | 450 | 313 | 31.43% | 69.56% | 99.60 | 3.14× |
| Test | 20% | 900 | 512 | 51.41% | 56.89% | 199.20 | 2.57× |

In these samples, selecting a larger share captured more defaults while
precision and lift decreased. The random reference is an expected count at
the same workload, not a simulated intervention outcome or a statistical
confidence interval.

The model's test ROC-AUC was 0.7800, PR-AUC 0.5515, and Brier score 0.1352.
The 0.5-threshold classification metrics in the Phase 5 report are not
business cutoffs and should not be used to define this queue's capacity.

## Limits that change how to use this result

1. **Historical population:** The data describes a specific historical
   credit-card customer population. Results do not establish performance
   for a current portfolio, another market, or a future period.
2. **Validation selection:** Validation outcomes were involved in model
   selection and ranking development. The validation scenario results are
   descriptive and may be optimistic.
3. **Repeated holdout analysis:** Phase 5 already reported standard metrics
   on this test split. The Step 7 supplementary ranking assessment reuses
   that same split, so it is not a fresh independent replication. Do not
   treat the test table as evidence from a new population.
4. **No intervention evidence:** The data does not record what action was
   taken, its cost, customer response, or resulting outcome. The ranking
   cannot establish that review or any intervention prevents default.
5. **No verified loss amount:** `LIMIT_BAL` is a credit limit, and historical
   bill amounts are not validated exposure at default. Expected-loss ranking
   is unsupported without established exposure and loss-given-default.
6. **No operating capacity data:** The 5%, 10%, and 20% capacities are
   hypothetical. The engine needs a count supplied by the caller; it does
   not discover a business capacity.
7. **Other operating controls:** Contactability, channel, analyst workload,
   fairness, governance, monitoring, and current-population validation have
   not been established by this analysis.

## What the project can and cannot recommend

**Supported by this prototype:**

- order customers by the selected model's predicted default probability;
- apply a stated review-count capacity reproducibly;
- explain queue inclusion with a risk-ranking reason code;
- compare the observed validation ranking with a random-selection
  expectation at the same workload.

**Not supported by this dataset:**

- a final operational capacity or probability cutoff;
- which customer intervention to take;
- intervention effectiveness or causal impact;
- expected financial loss or recovery value;
- automated credit approval, rejection, or account restriction.

Before any real operational use, the institution would need a current,
representative evaluation population; documented capacity and contactability
inputs; governance and fairness review; and intervention outcome and cost
data if actions or financial value are to be compared. A future independent
evaluation should use data that has not informed model, policy, or capacity
choices.

## How this recommendation was assembled

This brief consolidates the agreed objective and the evidence from the
preceding Phase 7 steps. It does not introduce a new scoring formula or
policy:

1. Step 7.1 established analyst-attention prioritization as the objective.
2. Step 7.2 audited available decision inputs and identified missing
   capacity, intervention, and validated exposure data.
3. Step 7.3 compared the probability ranking with random selection.
4. Step 7.4 added explicitly illustrative capacity scenarios.
5. Step 7.5 implemented a deterministic queue using the agreed ranking and
   capacity inputs.
6. Step 7.6 evaluated the engine-built queues on validation outcomes.
7. The supplementary holdout assessment extended the ranking comparison to
   the already reported Phase 5 test split; it was not a separate step in
   the original plan.

The recommendation is deliberately limited to analyst-attention
prioritization. It does not convert predictive association into a causal
claim or an intervention rule.

## Related project records

- [Decision-input audit](#phase-7-2-decision-input-audit)
- [Risk-ranking baseline](#phase-7-3-risk-ranking-compared-with-random-selection)
- [Capacity-scenario walkthrough](#phase-7-4-illustrative-review-capacity-scenarios)
- [Deterministic decision-engine walkthrough](#phase-7-5-deterministic-review-queue-engine)
- [Policy-scenario evaluation](#phase-7-6-evaluate-review-policy-scenarios)
- [Supplementary holdout ranking assessment](#supplementary-phase-7-holdout-ranking-diagnostic)
- [Phase 5 model development and evaluation](model_development_and_evaluation.md)
