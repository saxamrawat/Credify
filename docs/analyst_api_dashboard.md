# Phase 8 — Analyst API and Dashboard

# Phase 8.1 — Application Architecture and Analyst Workflow

## Decision

Build a small Python API with **FastAPI** for model scoring and deterministic
decision logic, and a **Streamlit** dashboard focused on the analyst
experience. The dashboard will call the API over HTTP. The current project
uses Python, pandas, NumPy, and scikit-learn; FastAPI and Streamlit are new
dependencies and have not yet been added.

This is an analyst-facing prototype. It prioritizes review attention using
predicted default risk. It does not choose or execute customer interventions,
approve or reject credit, or claim that an intervention prevents default.

## Why this architecture

The project is predominantly a data-science project, so the dashboard needs
to make portfolio results understandable and useful to explore. A separate
API keeps model inference and queue construction out of the presentation
layer. That boundary also gives the same scoring and decision functions a
reusable interface if another client is added later.

FastAPI and Streamlit keep both application layers in Python and can use the
existing package code. This introduces two runnable components and an HTTP
boundary, but avoids adding a separate JavaScript frontend stack. Visual
design and chart choices will be developed in the Streamlit layer; decision
logic will remain in the existing decision package or API service layer.

## Responsibilities

### FastAPI service

- Validate prediction and queue requests.
- Load and call the approved model pipeline using the project's established
  feature preparation.
- Return predicted probabilities and appropriate model metadata.
- Apply the existing deterministic review-queue engine when a caller
  supplies a review capacity.
- Return structured validation errors and decision outputs.
- Keep observed `DEFAULT` outcomes out of prediction-time inputs.

The service will not invent capacity, treatment cost, loss, or causal-effect
values. It will not make credit decisions or take customer actions.

### Streamlit dashboard

- Provide the analyst-facing workflow and portfolio views.
- Collect or select the inputs and capacity that the API contract supports.
- Call the API and display results such as risk ranking, queue membership,
  capacity usage, and reason codes.
- Explain relevant limitations in the interface.
- Avoid reproducing model or queue-selection logic in dashboard callbacks.

The specific input method (for example, file upload or a sample portfolio),
dashboard pages, filters, and visual design are not decided in this step.
They will be selected when the API contract and dashboard workflow are
specified.

## Request-to-result flow

1. An analyst provides a portfolio and an explicit review capacity through
   the dashboard workflow.
2. Streamlit sends a request to the local FastAPI service.
3. FastAPI validates the request and passes eligible customer predictors to
   the approved model pipeline.
4. The service obtains predicted default probabilities and, when requested,
   applies the deterministic review-queue engine with the supplied capacity.
5. FastAPI returns structured scores and queue results.
6. Streamlit presents the ranking, selection reasons, and capacity results
   for analyst review.

Request and response schemas, endpoint paths, model-artifact format, and
precise input rules remain for later Phase 8 steps. This step establishes
the component boundary and user workflow without prematurely fixing those
contracts.

## Deployment boundary

Development and validation of the API and dashboard will happen before
deployment. Deployment to the user's cloud Droplet is reserved for the
project's **final phase**. That phase will choose and implement the runtime,
network exposure, secure access, configuration, and operational checks
after the local application behavior is settled. This architecture decision
does not deploy anything or assume a particular hosting configuration.

## Alternatives considered

| Approach | Advantages | Trade-offs | Decision |
|---|---|---|---|
| FastAPI + Streamlit over HTTP | Python throughout; reusable service boundary; dashboard can focus on analyst workflow and visualizations. | Two components to run; Streamlit has less visual freedom than a custom frontend. | **Selected** |
| FastAPI + React | Most control over visual design and interactions; clear service boundary. | Adds JavaScript and frontend build tooling to a predominantly Python project. | Not selected for this phase. |
| Streamlit calling Python functions directly | Fastest, simplest local prototype. | No HTTP API for reuse; risks coupling presentation callbacks to model and policy behavior. | Not selected because a reusable API utility is an explicit goal. |

## Phase 8 sequence proposed after this architecture decision

1. Define the API request and response contract and the analyst's portfolio
   workflow.
2. Define model packaging and the reproducible inference path.
3. Implement the FastAPI scoring and queue endpoints.
4. Implement the Streamlit dashboard against those endpoints.
5. Add integration checks, focused tests, setup instructions, and a local
   demonstration workflow.

The final project phase will then prepare and deploy the completed prototype
to the user's cloud Droplet. No later phase should move deployment earlier.

## What this step changed

This step records the selected FastAPI + Streamlit architecture, clarifies
which layer owns each responsibility, and reserves deployment for the final
project phase. It adds no application code or dependencies because interface
contracts and implementation choices belong to subsequent steps.


---

# Phase 8.2 — Batch API Contract

## Purpose

This step defines the JSON contract between the Streamlit dashboard and the
FastAPI service. Streamlit accepts an analyst's CSV, validates its headers,
converts allowed rows to JSON, and sends them to FastAPI. The API remains the
authoritative validator and owns model scoring and review-queue construction.

This step originally specified the contract only. Step 8.4 implements the
FastAPI endpoint, schemas, validation, and error mapping against this design.

## Endpoint

`POST /v1/review-queue`

The endpoint scores one supplied portfolio of 1 to 30,000 customers and constructs one review queue.
The caller supplies an absolute review-count capacity. Percentages are not
accepted by this endpoint; a future dashboard control may translate an
analyst's chosen percentage into a count before sending the request, but that
would need an explicit later decision.

## Request shape

```json
{
  "customers": [
    {
      "ID": 1001,
      "LIMIT_BAL": 50000,
      "AGE": 35,
      "BILL_AMT1": 12000,
      "BILL_AMT2": 11000,
      "BILL_AMT3": 10000,
      "BILL_AMT4": 9000,
      "BILL_AMT5": 8000,
      "BILL_AMT6": 7000,
      "PAY_AMT1": 2000,
      "PAY_AMT2": 1800,
      "PAY_AMT3": 1500,
      "PAY_AMT4": 1200,
      "PAY_AMT5": 1000,
      "PAY_AMT6": 900,
      "SEX": 2,
      "EDUCATION": 2,
      "MARRIAGE": 1,
      "PAY_0": 0,
      "PAY_2": 0,
      "PAY_3": 0,
      "PAY_4": 0,
      "PAY_5": 0,
      "PAY_6": 0
    }
  ],
  "max_review_count": 1
}
```

The sample values illustrate structure only; they are not a realistic
customer profile or a recommendation.

### `customers`

- Required list of 1 to 30,000 customer objects. Larger portfolios are
  rejected by FastAPI validation before model inference.
- Each object has exactly `ID` and the 23 predictor columns listed in the
  canonical schema below.
- `ID` is a unique, non-missing integer within the submitted portfolio. It
  is used for record lookup and returned as `customer_id`; it is never passed
  to the model as a feature.
- Every predictor is required and non-missing. Numeric values must be finite.
- `SEX`, `EDUCATION`, `MARRIAGE`, and the six `PAY_*` status values are
  integer-coded fields. `SEX` accepts the cleaned values 1 or 2;
  `EDUCATION` accepts 0 through 4; `MARRIAGE` accepts 0 through 3. The
  current project does not define an additional allowed-value range for
  `PAY_0`, `PAY_2`, `PAY_3`, `PAY_4`, `PAY_5`, and `PAY_6`; do not invent one
  in the API.
- `LIMIT_BAL` and all six `PAY_AMT*` fields must be non-negative, matching
  the existing cleaned-data checks. No new range restriction is defined here
  for age, bill amounts, or repayment-status values.
- Unknown or extra fields are rejected by the API. In particular, `DEFAULT`
  is forbidden in an API request because it is a historical outcome and not
  an inference-time input.

Canonical predictor columns, matching
[`data/schema.py`](../src/propensity_prediction/data/schema.py):

```text
LIMIT_BAL, AGE,
BILL_AMT1, BILL_AMT2, BILL_AMT3, BILL_AMT4, BILL_AMT5, BILL_AMT6,
PAY_AMT1, PAY_AMT2, PAY_AMT3, PAY_AMT4, PAY_AMT5, PAY_AMT6,
SEX, EDUCATION, MARRIAGE,
PAY_0, PAY_2, PAY_3, PAY_4, PAY_5, PAY_6
```

### `max_review_count`

- Required non-negative integer; booleans are not valid integers for this
  field.
- The requested count may exceed the number of customers. The engine caps
  the target count at the submitted portfolio size, consistent with
  `build_review_queue()`.
- A count of zero is valid and selects nobody.
- If a tied probability group would cross the capacity boundary, the engine
  leaves that whole group out. The actual selected count can therefore be
  lower than the target count.

## CSV-to-JSON conversion in Streamlit

The dashboard will require the CSV to contain `ID` and all 23 canonical
predictor columns, and reject `DEFAULT` or any other unrecognized column.
Real prediction-time data should not contain the future outcome. If a file
contains `DEFAULT`, Streamlit must explain that it is an outcome field and
ask for a prediction-time file without it; it must not silently drop the
column. The API independently rejects `DEFAULT` and any other unrecognized
field. Missing required columns, duplicate IDs, blank cells, invalid numeric
values, or unsupported categorical codes should be reported before the
request is sent, while FastAPI repeats authoritative validation server-side.

The dashboard should select outbound columns from the canonical allowlist;
it should not turn arbitrary CSV columns into prediction features. The
Step 8.6 local benchmark measures the service; the initial row-count maximum
is pending user choice, and target-Droplet size limits remain for deployment.

## Successful response shape

```json
{
  "population_count": 1,
  "capacity": {
    "requested_review_count": 1,
    "target_review_count": 1,
    "selected_count": 1,
    "unused_capacity": 0
  },
  "customers": [
    {
      "customer_id": 1001,
      "predicted_default_probability": 0.7312,
      "risk_rank": 1,
      "selected_for_review": true,
      "reason_code": "SELECTED_BY_RISK_RANKING",
      "reason": "Selected by descending predicted default probability within the stated capacity."
    }
  ]
}
```

The `customers` array contains every submitted customer, sorted by descending
predicted probability. Equal probabilities share a competition rank. Stable
input order may be retained within a tied group, but the API must not imply
that one tied customer has higher risk than another. Each row includes the
existing reason code and text from the deterministic decision engine.

`capacity.requested_review_count` is the caller's count;
`capacity.target_review_count` is `min(requested_review_count,
population_count)`; `selected_count` is the number actually selected after
whole-tie handling; `unused_capacity` is the difference between target and
selected count. These names correspond to `ReviewQueueResult` in
[`decision/engine.py`](../src/propensity_prediction/decision/engine.py).

No observed outcome, intervention recommendation, loss estimate, or causal
effect is returned. A model identifier/version is intentionally omitted
until the model-artifact step defines how that metadata is produced.

## Error response contract

Errors use a stable envelope:

```json
{
  "error": {
    "code": "INVALID_CUSTOMER_SCHEMA",
    "message": "One or more required customer fields are missing.",
    "details": ["customers[0].PAY_0"]
  }
}
```

The implementation uses HTTP 400 for duplicate IDs in an otherwise valid
portfolio, HTTP 422 for request-body type/schema validation, and HTTP 503 if
the model is unavailable. The response body always uses `error.code`,
`error.message`, and `error.details`. Step 8.4 implements the current codes
and mapping; endpoint test coverage remains a separate verification task.

## Contract decisions and deferred questions

Decided in this step:

1. One batch operation scores a portfolio and returns its deterministic
   review queue.
2. The API accepts JSON; Streamlit owns CSV upload and conversion.
3. The identifier plus all 23 canonical predictors are required.
4. `DEFAULT` is forbidden in the uploaded CSV and API request; the dashboard
   rejects it instead of silently stripping it.
5. Capacity is an explicit integer count, not an inferred business value.
6. The response includes the full ranked portfolio and capacity accounting.

Deferred to later steps:

- model artifact reproducibility metadata and loading lifecycle (implemented
  in Step 8.3);
- API schema implementation and exact numeric JSON encoding details
  (implemented in Step 8.4);
- the 30,000-row initial maximum was selected after the Step 8.6 benchmark
  and enforced in Step 8.7; target-Droplet upload and request-size limits
  still need deployment measurement;
- whether to add a separate score-only endpoint (the readiness endpoint is
  implemented as `GET /health` in Step 8.4);
- authentication and network exposure, which belong to final deployment
  planning.

## What this step changed

This step fixed the request, response, validation, and error-envelope design
for FastAPI and Streamlit. It introduced no code or dependencies; Step 8.4
implemented the API and Step 8.5 implemented CSV validation and conversion
against this agreed contract.


---

# Phase 8.3 — Package the Selected Model for Inference

## Goal

Make the selected Phase 5 model available to the future API without running
model selection every time the service starts. The saved estimator includes
its fitted preprocessing pipeline. The API-facing prediction helper applies
the project's existing feature preparation before calling the estimator.

## Why the artifact is rebuilt from the locked configuration

The original fitted `GridSearchCV` estimator was not persisted during Phase 5.
This step therefore refits the already selected HistGradientBoosting model
with the exact recorded parameters on the established 21,000-row training
partition and random state 42. It does **not** rerun candidate selection,
retune parameters, fit on validation or test rows, or calculate new evaluation
metrics. The historical validation and CV metrics in the sidecar are copied
from the Phase 5 report for traceability; they are not measurements from this
export command.

The refit uses the same estimator class, preprocessing pipeline, engineered
feature set, parameters, and training split as the selected Phase 5 model. It
recreates that model reproducibly instead of serializing an in-memory object
that no longer exists.

## What the code does, step by step

1. **Lock the approved model definition.** `LOCKED_MODEL_NAME`,
   `LOCKED_FEATURE_SET`, and `LOCKED_MODEL_PARAMS` identify the selected Phase
   5 configuration. The exporter cannot silently choose a different model.
2. **Load only the established training partition.** It reads the processed
   dataset and calls `split_dataset(random_state=42)`. `DEFAULT` is used only
   by the splitter to make the same stratified partition; it is not added to
   the predictor dataframe.
3. **Prepare model features consistently.** `prepare_model_features()` checks
   for the exact identifier and 23 predictors, rejects `DEFAULT` and extra
   columns, checks IDs, drops `ID`, and adds the 20 established engineered
   features.
4. **Fit the fixed pipeline.** A HistGradientBoosting estimator with the
   locked settings is placed in the same preprocessing pipeline used for
   Phase 5, then fit on training rows only.
5. **Record provenance.** The metadata includes model/feature-set names,
   parameters, the historical selection metrics, training row count, feature
   names, random state, and Python/scientific-library versions.
6. **Save two artifacts.** Joblib stores the fitted pipeline in
   `models/selected_default_risk_model.joblib`; a JSON sidecar stores readable
   metadata at `models/selected_default_risk_model.json`.
7. **Load and score.** The API can load the trusted local joblib file and call
   `predict_default_probabilities()`. The helper uses the feature set recorded
   in metadata, selects the probability column for class `1`, and rejects
   invalid probabilities.

## Generated model record

- Model: `HistGradientBoostingClassifier`
- Feature set: engineered features
- Parameters: `l2_regularization=1.0`, `learning_rate=0.05`, `max_iter=100`,
  `max_leaf_nodes=31`
- Training rows: 21,000
- Random state: 42
- Joblib artifact size: 162 KB
- Test data: not loaded or scored by the export command

The validation and CV figures in the JSON sidecar are historical Phase 5
selection figures, included to identify the selected configuration. They do
not indicate that this step reran validation. The historical test metrics
remain as reported in the Phase 5 and supplementary Phase 7 documents.

## How to rebuild and load the artifact

From the repository root:

```bash
venv/bin/python -m propensity_prediction.models.artifact
```

Rebuilding refits the one locked estimator on the established training
partition. It does not rerun GridSearchCV. The future service can use the
following Python interface:

```python
from propensity_prediction.models.artifact import (
    load_model_artifact,
    predict_default_probabilities,
)

model_artifact = load_model_artifact()
probabilities = predict_default_probabilities(model_artifact, customers)
```

`customers` must contain `ID` plus all 23 canonical predictors, without
`DEFAULT`. The API contract in Step 8.2 defines field and type validation;
FastAPI will provide the request-level error responses in a later step.

## Serialization and compatibility

Joblib uses Python object serialization. Load only the artifact generated by
this project or another trusted source; do not accept user-provided model
files. The JSON sidecar records package versions. The loader warns if the
installed scikit-learn version differs from the version recorded at export,
because scikit-learn does not guarantee serialized estimator compatibility
across versions. The deployment phase must install compatible dependencies
and deliver the artifact with the application.

The artifact is a project output and is kept in the repository so a checkout
contains the model needed by the future local API. The source processed data
and fixed training procedure remain necessary to regenerate it.

## Alternatives and later enhancement

This step uses the selected approach: persist a fixed fitted estimator plus
metadata, with feature preparation remaining in the versioned Python source.
A self-contained custom transformer/pipeline that bundles engineered-feature
construction with the estimator is a possible later enhancement after the
project is complete. That would require a separate refactor and compatibility
review; it is not part of this step.

## Complete code added for this step

### `src/propensity_prediction/models/artifact.py`

The following is the complete source file. The source file remains
authoritative; refresh this listing if it changes.

```python
"""Build and load the selected model artifact for application inference."""

from __future__ import annotations

import json
import warnings
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

from propensity_prediction.data.build import PROCESSED_DATA_PATH
from propensity_prediction.data.schema import get_feature_columns
from propensity_prediction.data.split import split_dataset
from propensity_prediction.models.final_selection import (
    RANDOM_STATE,
    _build_pipeline,
    prepare_model_features,
)


ARTIFACT_FORMAT_VERSION = 1
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODEL_ARTIFACT_PATH = (
    PROJECT_ROOT / "models" / "selected_default_risk_model.joblib"
)
LOCKED_MODEL_NAME = "hist_gradient_boosting"
LOCKED_FEATURE_SET = "engineered"
LOCKED_MODEL_PARAMS = {
    "l2_regularization": 1.0,
    "learning_rate": 0.05,
    "max_iter": 100,
    "max_leaf_nodes": 31,
}


def _package_version(distribution: str) -> str:
    try:
        return version(distribution)
    except PackageNotFoundError:
        return "not-installed"


def _json_value(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Cannot write {type(value).__name__} to model metadata JSON.")


def create_selected_model_artifact() -> dict:
    """Refit the locked Phase 5 winner on train rows and package it."""
    dataset = pd.read_csv(PROCESSED_DATA_PATH)
    split = split_dataset(dataset, random_state=RANDOM_STATE)
    train_X, numerical, categorical, ordinal = prepare_model_features(
        split.X_train,
        use_engineered_features=True,
    )
    estimator = HistGradientBoostingClassifier(random_state=RANDOM_STATE)
    estimator.set_params(**LOCKED_MODEL_PARAMS)
    pipeline = _build_pipeline(
        estimator,
        numerical_features=numerical,
        categorical_features=categorical,
        ordinal_features=ordinal,
    )
    pipeline.fit(train_X, split.y_train)

    metadata = {
        "artifact_format_version": ARTIFACT_FORMAT_VERSION,
        "project_version": "0.1.0",
        "model_name": LOCKED_MODEL_NAME,
        "feature_set": LOCKED_FEATURE_SET,
        "best_params": dict(LOCKED_MODEL_PARAMS),
        "selection_source": "Phase 5 final model selection report",
        "reported_cv_pr_auc": 0.5656,
        "reported_validation_pr_auc": 0.5501,
        "reported_validation_roc_auc": 0.7797,
        "reported_validation_brier_score": 0.1358,
        "random_state": RANDOM_STATE,
        "training_row_count": int(len(split.X_train)),
        "identifier_column": "ID",
        "feature_columns": get_feature_columns(),
        "uses_engineered_features": True,
        "training_boundary": (
            "Rebuilt using the locked Phase 5 parameters on the established "
            "training partition. The validation metrics are historical "
            "selection results; this exporter does not tune or score on the "
            "validation or test partitions."
        ),
        "package_versions": {
            "python": f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}.{__import__('sys').version_info.micro}",
            "numpy": _package_version("numpy"),
            "pandas": _package_version("pandas"),
            "scikit-learn": _package_version("scikit-learn"),
            "joblib": _package_version("joblib"),
        },
    }
    return {"metadata": metadata, "estimator": pipeline}


def save_model_artifact(
    model_artifact: dict,
    path: str | Path = DEFAULT_MODEL_ARTIFACT_PATH,
) -> tuple[Path, Path]:
    """Write the estimator bundle and a human-readable JSON metadata sidecar."""
    artifact_path = Path(path)
    metadata_path = artifact_path.with_suffix(".json")
    artifact_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_artifact = artifact_path.with_name(artifact_path.name + ".tmp")
    temporary_metadata = metadata_path.with_name(metadata_path.name + ".tmp")
    try:
        joblib.dump(model_artifact, temporary_artifact, compress=3)
        temporary_metadata.write_text(
            json.dumps(model_artifact["metadata"], indent=2, default=_json_value)
            + "\n"
        )
        temporary_artifact.replace(artifact_path)
        temporary_metadata.replace(metadata_path)
    finally:
        temporary_artifact.unlink(missing_ok=True)
        temporary_metadata.unlink(missing_ok=True)

    return artifact_path, metadata_path


def export_selected_model_artifact(
    path: str | Path = DEFAULT_MODEL_ARTIFACT_PATH,
) -> dict:
    """Fit the locked model configuration and persist the estimator bundle."""
    model_artifact = create_selected_model_artifact()
    artifact_path, metadata_path = save_model_artifact(model_artifact, path)
    return {
        "artifact_path": artifact_path,
        "metadata_path": metadata_path,
        "metadata": model_artifact["metadata"],
    }


def load_model_artifact(
    path: str | Path = DEFAULT_MODEL_ARTIFACT_PATH,
) -> dict:
    """Load a trusted local artifact and check its format and compatibility."""
    artifact_path = Path(path)
    if not artifact_path.is_file():
        raise FileNotFoundError(f"Model artifact does not exist: {artifact_path}")

    model_artifact = joblib.load(artifact_path)
    if not isinstance(model_artifact, dict):
        raise ValueError("Model artifact must contain a dictionary bundle.")
    if model_artifact.get("metadata", {}).get("artifact_format_version") != ARTIFACT_FORMAT_VERSION:
        raise ValueError("Unsupported model artifact format version.")
    estimator = model_artifact.get("estimator")
    if estimator is None or not hasattr(estimator, "predict_proba"):
        raise ValueError("Model artifact does not contain a probability estimator.")

    trained_sklearn = model_artifact["metadata"].get("package_versions", {}).get("scikit-learn")
    current_sklearn = _package_version("scikit-learn")
    if trained_sklearn and trained_sklearn != current_sklearn:
        warnings.warn(
            "Model artifact was created with scikit-learn "
            f"{trained_sklearn}, but the current environment has {current_sklearn}. "
            "Serialized scikit-learn models are not guaranteed to be compatible "
            "across versions.",
            RuntimeWarning,
            stacklevel=2,
        )
    return model_artifact


def predict_default_probabilities(
    model_artifact: dict,
    customers: pd.DataFrame,
) -> np.ndarray:
    """Score customers using the packaged estimator and matching feature path."""
    metadata = model_artifact.get("metadata", {})
    if metadata.get("artifact_format_version") != ARTIFACT_FORMAT_VERSION:
        raise ValueError("Unsupported model artifact format version.")
    feature_set = metadata.get("feature_set")
    if feature_set not in {"original", "engineered"}:
        raise ValueError("Model artifact has an unsupported feature_set.")

    model_inputs, _, _, _ = prepare_model_features(
        customers,
        use_engineered_features=(feature_set == "engineered"),
    )
    probabilities = np.asarray(
        model_artifact["estimator"].predict_proba(model_inputs),
        dtype=float,
    )
    classes = np.asarray(model_artifact["estimator"].classes_)
    positive_class_indices = np.flatnonzero(classes == 1)
    if probabilities.ndim != 2 or len(positive_class_indices) != 1:
        raise ValueError("Estimator did not return a binary default probability column.")

    scores = probabilities[:, int(positive_class_indices[0])]
    if len(scores) != len(customers) or not np.isfinite(scores).all():
        raise ValueError("Estimator returned invalid prediction probabilities.")
    if ((scores < 0) | (scores > 1)).any():
        raise ValueError("Estimator probabilities must be between 0 and 1.")
    return scores


if __name__ == "__main__":
    export = export_selected_model_artifact()
    print(f"Model artifact: {export['artifact_path']}")
    print(f"Metadata: {export['metadata_path']}")
    print(
        "Selected: "
        f"{export['metadata']['model_name']} "
        f"with {export['metadata']['feature_set']} features"
    )
```

### `prepare_model_features()` in `src/propensity_prediction/models/final_selection.py`

This public helper is the API-safe feature-preparation entry point. The
existing `_prepare_features()` internal name delegates to it, so training and
inference retain one implementation.

```python
def prepare_model_features(
    X: pd.DataFrame,
    use_engineered_features: bool,
):
    """Validate and prepare prediction features and their model schema."""
    if not isinstance(X, pd.DataFrame) or X.empty:
        raise ValueError("Customer data must be a non-empty DataFrame.")
    if "DEFAULT" in X.columns:
        raise ValueError("DEFAULT is an outcome and must not be included in prediction data.")

    expected_columns = set(IDENTIFIER_COLUMNS + get_feature_columns())
    actual_columns = set(X.columns)
    missing_columns = expected_columns - actual_columns
    extra_columns = actual_columns - expected_columns
    if missing_columns:
        raise ValueError(f"Customer data is missing required columns: {sorted(missing_columns)}")
    if extra_columns:
        raise ValueError(f"Customer data contains unsupported columns: {sorted(extra_columns)}")
    if X[IDENTIFIER_COLUMNS[0]].isna().any() or X[IDENTIFIER_COLUMNS[0]].duplicated().any():
        raise ValueError("Customer IDs must be non-missing and unique.")

    X = X.drop(columns=["ID"]).copy()

    if use_engineered_features:
        X = engineer_features(X)

        numerical_features = (
            NUMERICAL_FEATURES + ENGINEERED_FEATURES
        )
    else:
        numerical_features = NUMERICAL_FEATURES

    return (
        X,
        numerical_features,
        CATEGORICAL_FEATURES,
        ORDINAL_FEATURES,
    )


def _prepare_features(
    X: pd.DataFrame,
    use_engineered_features: bool,
):
    """Backward-compatible internal name for model feature preparation."""
    return prepare_model_features(X, use_engineered_features)
```

## What changed and why

Step 8.3 adds a reproducible artifact-generation and loading path for the
Phase 5 winner. It also makes model feature preparation public and strict so
future API requests use the same transformation and cannot accidentally pass
`DEFAULT` or unsupported columns. The joblib file is ready for the future
FastAPI service; no endpoint or dashboard code was added in this step.


---

# Phase 8.4 — FastAPI Scoring and Review-Queue Service

## Goal

Implement the agreed JSON API using a service-repository structure. HTTP routes
validate and dispatch requests, the application service coordinates inference
and queue construction, and a file-backed repository loads the trusted model
artifact into memory. The repository pattern is useful here even without a
database: persistence is still isolated behind one small component, and a
future change in artifact storage will not need to change route or decision
logic.

## Request flow, step by step

1. FastAPI receives `POST /v1/review-queue`. Pydantic validates the payload
against the Step 8.2 contract: one or more customers, all 24 required fields
per row, finite numeric predictors, the documented categorical bounds, no
extra fields such as `DEFAULT`, and a non-negative integer capacity.
2. The application service converts validated customer objects to a DataFrame
   and rejects duplicate IDs across the portfolio.
3. The repository returns the already-loaded model artifact. The artifact is
   loaded once during application startup, not once per row or request.
4. The inference helper applies the project's canonical feature preparation
   and asks the fitted pipeline for default probabilities.
5. The existing decision engine ranks the entire portfolio and applies the
   capacity and whole-tie rule. The service converts the result into the
   response contract.
6. FastAPI validates the outgoing response model and returns JSON. `/health`
   reports `ok` when the artifact loaded and `degraded` when the process is
   available but cannot score.

## Boundaries and why they are separated

- **Schemas** define the public JSON shapes and reject malformed fields before
  application logic runs.
- **Routes** provide HTTP paths, dependency lookup, and response models. They
  do not implement model or ranking logic.
- **Service** translates validated input into the domain operations needed for
  one portfolio request.
- **Repository** owns the artifact path, load lifecycle, and unavailable
  state. It is file-backed because this phase has no database.
- **Existing model and decision modules** remain authoritative for feature
  preparation, probability generation, tie-aware ranking, and capacity
  accounting.
- **Application factory** wires these components, starts the repository once,
  and maps failures to the stable error envelope.

## Error behavior

| Condition | HTTP | Code |
| --- | ---: | --- |
| Invalid JSON fields, types, missing or extra fields | 422 | `INVALID_REQUEST_SCHEMA` |
| Duplicate customer IDs in an otherwise valid portfolio | 400 | `INVALID_PORTFOLIO` |
| Model artifact cannot load or is unavailable | 503 | `MODEL_UNAVAILABLE` |
| Unexpected server failure | 500 | `INTERNAL_SERVER_ERROR` |

Errors use `{ "error": { "code", "message", "details" } }`. The model
artifact is a trusted project file; the API never accepts model files from
callers. The service does not return an intervention recommendation, expected
loss, or causal effect.

## Run locally

Install the project dependencies, then from the repository root run:

```bash
uvicorn propensity_prediction.api.main:app --reload
```

Open `/docs` for the generated OpenAPI interface and call `/health` to see
whether the artifact loaded. The default artifact location is
`models/selected_default_risk_model.joblib`; the application factory accepts a
different path for local wiring or deployment configuration.
The default artifact path resolves from the current working directory's
`models/` folder when present. Set `PROPENSITY_MODEL_ARTIFACT_PATH` when the
artifact is stored elsewhere, such as in the deployment layout on the Droplet.

## Dependency changes

`pyproject.toml` now declares FastAPI, Uvicorn, Pydantic, and the existing
scientific/model packages required at runtime. `requirements.txt` records the
resolved FastAPI stack versions in the repository's existing pinned format.
Streamlit dependencies and dashboard-specific packages belong to the next
implementation step.

## Complete code added or changed for this step

The listings below are the complete API modules and the feature-preparation
helper changed to provide strict inference-time validation. They are copied
from the source at the time this document was written; source files remain
authoritative.

### `src/propensity_prediction/api/__init__.py`

```python
"""HTTP API for model scoring and analyst review prioritization."""

```

### `src/propensity_prediction/api/errors.py`

```python
"""Typed service errors mapped to stable HTTP responses."""


class InvalidPortfolioError(ValueError):
    """The request is valid JSON but cannot represent a valid portfolio."""


class ModelArtifactUnavailable(RuntimeError):
    """No usable trusted model artifact is available to the API service."""

```

### `src/propensity_prediction/api/schemas.py`

```python
"""Pydantic request and response models for the public API contract."""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StrictInt


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

    customers: Annotated[list[CustomerInput], Field(min_length=1)]
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

```

### `src/propensity_prediction/api/repository.py`

```python
"""File-backed repository for the fitted model artifact."""

from __future__ import annotations

import logging
from pathlib import Path

from propensity_prediction.models.artifact import (
    DEFAULT_MODEL_ARTIFACT_PATH,
    load_model_artifact,
)
from propensity_prediction.api.errors import ModelArtifactUnavailable


logger = logging.getLogger(__name__)


class ModelArtifactRepository:
    """Load a trusted local model bundle once and serve it from memory."""

    def __init__(self, path: str | Path = DEFAULT_MODEL_ARTIFACT_PATH) -> None:
        self.path = Path(path)
        self._model_artifact: dict | None = None
        self._load_error: Exception | None = None

    @property
    def is_loaded(self) -> bool:
        return self._model_artifact is not None

    def load(self) -> bool:
        """Load the bundle once; leave the API alive if it is unavailable."""
        try:
            self._model_artifact = load_model_artifact(self.path)
            self._load_error = None
            logger.info("Loaded model artifact from %s", self.path)
            return True
        except Exception as exc:
            self._model_artifact = None
            self._load_error = exc
            logger.exception("Could not load model artifact from %s", self.path)
            return False

    def get_model_artifact(self) -> dict:
        if self._model_artifact is None:
            raise ModelArtifactUnavailable(
                "The model artifact is not available. Check the API logs and artifact path."
            ) from self._load_error
        return self._model_artifact

```

### `src/propensity_prediction/api/service.py`

```python
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

```

### `src/propensity_prediction/api/routes.py`

```python
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

```

### `src/propensity_prediction/api/main.py`

```python
"""FastAPI application factory and stable error response handlers."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from propensity_prediction.api.errors import (
    InvalidPortfolioError,
    ModelArtifactUnavailable,
)
from propensity_prediction.api.repository import ModelArtifactRepository
from propensity_prediction.api.routes import router
from propensity_prediction.api.service import ReviewQueueService
from propensity_prediction.models.artifact import DEFAULT_MODEL_ARTIFACT_PATH


logger = logging.getLogger(__name__)


def _error_response(code: str, message: str, details: list[str]) -> dict:
    return {"error": {"code": code, "message": message, "details": details}}


def create_app(
    artifact_path: str | Path = DEFAULT_MODEL_ARTIFACT_PATH,
) -> FastAPI:
    repository = ModelArtifactRepository(artifact_path)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        repository.load()
        app.state.model_repository = repository
        app.state.review_queue_service = ReviewQueueService(repository)
        yield

    app = FastAPI(
        title="Credit Risk Review Prioritization API",
        version="1.0.0",
        description=(
            "Scores supplied customer predictors and constructs a deterministic "
            "capacity-limited analyst review queue. It does not recommend or "
            "execute customer interventions."
        ),
        lifespan=lifespan,
    )
    app.include_router(router)

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        details = [
            ".".join(str(part) for part in error["loc"] if part != "body")
            + f": {error['msg']}"
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=_error_response(
                "INVALID_REQUEST_SCHEMA",
                "The request does not match the review-queue contract.",
                details,
            ),
        )

    @app.exception_handler(InvalidPortfolioError)
    async def invalid_portfolio_handler(
        request: Request,
        exc: InvalidPortfolioError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content=_error_response(
                "INVALID_PORTFOLIO",
                str(exc),
                [],
            ),
        )

    @app.exception_handler(ModelArtifactUnavailable)
    async def model_unavailable_handler(
        request: Request,
        exc: ModelArtifactUnavailable,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content=_error_response(
                "MODEL_UNAVAILABLE",
                str(exc),
                [],
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        code = "MODEL_UNAVAILABLE" if exc.status_code == 503 else "HTTP_ERROR"
        message = str(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_response(code, message, []),
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.error(
            "Unhandled API error",
            exc_info=(type(exc), exc, exc.__traceback__),
        )
        return JSONResponse(
            status_code=500,
            content=_error_response(
                "INTERNAL_SERVER_ERROR",
                "The API could not complete this request.",
                [],
            ),
        )

    return app


app = create_app()

```

### `src/propensity_prediction/models/final_selection.py` — inference feature preparation

This excerpt contains the complete public validation helper and its backwards-compatible internal wrapper. The rest of this file is unchanged in Step 8.4.

```python
def prepare_model_features(
    X: pd.DataFrame,
    use_engineered_features: bool,
):
    """Validate and prepare prediction features and their model schema."""
    if not isinstance(X, pd.DataFrame) or X.empty:
        raise ValueError("Customer data must be a non-empty DataFrame.")
    if "DEFAULT" in X.columns:
        raise ValueError("DEFAULT is an outcome and must not be included in prediction data.")

    expected_columns = set(IDENTIFIER_COLUMNS + get_feature_columns())
    actual_columns = set(X.columns)
    missing_columns = expected_columns - actual_columns
    extra_columns = actual_columns - expected_columns
    if missing_columns:
        raise ValueError(f"Customer data is missing required columns: {sorted(missing_columns)}")
    if extra_columns:
        raise ValueError(f"Customer data contains unsupported columns: {sorted(extra_columns)}")
    if X[IDENTIFIER_COLUMNS[0]].isna().any() or X[IDENTIFIER_COLUMNS[0]].duplicated().any():
        raise ValueError("Customer IDs must be non-missing and unique.")

    X = X.drop(columns=["ID"]).copy()

    if use_engineered_features:
        X = engineer_features(X)

        numerical_features = (
            NUMERICAL_FEATURES + ENGINEERED_FEATURES
        )
    else:
        numerical_features = NUMERICAL_FEATURES

    return (
        X,
        numerical_features,
        CATEGORICAL_FEATURES,
        ORDINAL_FEATURES,
    )


def _prepare_features(
    X: pd.DataFrame,
    use_engineered_features: bool,
):
    """Backward-compatible internal name for model feature preparation."""
    return prepare_model_features(X, use_engineered_features)
```


---

# Phase 8.5 — Single-Page Streamlit Analyst Dashboard

## Goal and chosen design

Build a single-page analyst flow for uploading and validating a real-world
prediction CSV, setting review capacity, calling the FastAPI scoring endpoint,
reviewing the prioritized queue, and downloading results. A multi-page design
can be added later if the dashboard grows enough to benefit from separate
views.

## User flow, step by step

1. The analyst enters the FastAPI base address. It defaults to
   `http://127.0.0.1:8000` and can be supplied through `PROPENSITY_API_URL`.
2. The analyst uploads a UTF-8 CSV. The application checks its header before
   pandas parses it, so duplicate header names are detected before pandas can
   rename them. The file must contain exactly `ID` and all 23 canonical
   predictors. `DEFAULT` gets a specific explanation because it is a past
   outcome, not a valid inference input.
3. The dashboard checks for non-empty rows, blank cells, finite numeric values,
   integer-coded fields, documented category ranges, non-negative credit
   limits and payments, and unique IDs. It reorders columns canonically after
   validation. Invalid files are explained and never sent to the API.
4. The analyst chooses an absolute review count. The dashboard sends the
   canonical customer rows and count as JSON to `POST /v1/review-queue`.
5. The dashboard presents capacity metrics, a probability distribution,
   selected customers, and the full ranked portfolio. The full ranking can be
   downloaded as CSV. If the upload, API address, or capacity changes, the
   previous result is hidden until scoring is run again.
6. The expandable API status control can call `/health` independently.

## Why the layers are separate

- `csv_input.py` owns upload parsing and user-facing validation. It uses the
  canonical project schema and sends no unknown fields.
- `client.py` owns JSON conversion, HTTP timeouts, transport errors, and
  readable API error messages.
- `streamlit_app.py` composes the one-page experience and displays the API's
  result. It does not implement model scoring or customer ranking.
- FastAPI remains authoritative: it validates the request again, scores the
  rows, and constructs the capacity and tie-aware queue.

## Validation behavior

| Input condition | Dashboard behavior |
| --- | --- |
| `DEFAULT` column | Reject with an explanation; do not silently discard it |
| Missing or unrecognized column | Reject and list the affected names |
| Duplicate header or duplicate ID | Reject before API call |
| Blank, nonnumeric, or infinite value | Reject with the affected column and, for nonnumeric values, example CSV rows |
| Non-integer ID or coded field | Reject |
| `SEX`, `EDUCATION`, `MARRIAGE` outside the contract ranges | Reject |
| Negative `LIMIT_BAL` or `PAY_AMT*` | Reject |
| `AGE`, bill amounts, or `PAY_*` outside a newly invented range | No added range restriction; the agreed contract defines none |

The 30,000-row maximum was selected after Step 8.6 measured a synthetic
30,000-row request at about 4.8 seconds locally. Step 8.7 enforces this limit
in both the CSV validator and API schema. It is an initial operational cap,
not a Droplet performance guarantee; deployment will review upload and
request-size limits on the target server.

## Run locally

Install the project dependencies. Start the API in one terminal:

```bash
venv/bin/uvicorn propensity_prediction.api.main:app --reload
```

Start Streamlit in another terminal from the repository root:

```bash
venv/bin/streamlit run streamlit_app.py
```

The dashboard's default API address is local. Set `PROPENSITY_API_URL` when
the API runs at a different address. Keep both processes running while using
the dashboard.

## Dependencies

`pyproject.toml` now declares Streamlit and Requests alongside the API and
model runtime dependencies. `requirements.txt` records the resolved Streamlit
stack in the existing pinned-dependency format. The dashboard uses Streamlit's
built-in charts and table display; it does not introduce a separate charting
framework.

## Complete code added for this step

The complete source listings follow. The source files remain authoritative; refresh this walkthrough if they change.

### `src/propensity_prediction/dashboard/__init__.py`

```python
"""Streamlit analyst dashboard and API client helpers."""

```

### `src/propensity_prediction/dashboard/csv_input.py`

```python
"""Read and validate inference-time customer CSV files."""

from __future__ import annotations

import csv
from decimal import Decimal, InvalidOperation
from io import StringIO
from typing import BinaryIO

import numpy as np
import pandas as pd

from propensity_prediction.data.schema import (
    CATEGORICAL_FEATURES,
    IDENTIFIER_COLUMNS,
    ORDINAL_FEATURES,
    get_feature_columns,
)


REQUIRED_COLUMNS = IDENTIFIER_COLUMNS + get_feature_columns()
INTEGER_COLUMNS = IDENTIFIER_COLUMNS + CATEGORICAL_FEATURES + ORDINAL_FEATURES
NON_NEGATIVE_COLUMNS = [
    "LIMIT_BAL",
    "PAY_AMT1",
    "PAY_AMT2",
    "PAY_AMT3",
    "PAY_AMT4",
    "PAY_AMT5",
    "PAY_AMT6",
]
INTEGER_RANGES = {
    "SEX": (1, 2),
    "EDUCATION": (0, 4),
    "MARRIAGE": (0, 3),
}


class CSVInputError(ValueError):
    """A user-readable CSV parsing or validation issue."""


def _read_header(upload: BinaryIO) -> list[str]:
    try:
        text = upload.getvalue().decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise CSVInputError("The file must be a UTF-8 encoded CSV.") from exc
    try:
        header = next(csv.reader(StringIO(text)))
    except (csv.Error, StopIteration) as exc:
        raise CSVInputError("The uploaded file is empty or has an invalid CSV header.") from exc
    if not header or all(not column for column in header):
        raise CSVInputError("The uploaded file must include a header row.")
    if len(header) != len(set(header)):
        raise CSVInputError("The CSV contains duplicate column names.")
    if "DEFAULT" in header:
        raise CSVInputError(
            "DEFAULT is a historical outcome, not an input for prediction. "
            "Upload a prediction-time file without this column."
        )
    missing = sorted(set(REQUIRED_COLUMNS) - set(header))
    extra = sorted(set(header) - set(REQUIRED_COLUMNS))
    if missing or extra:
        problems = []
        if missing:
            problems.append(f"Missing required columns: {', '.join(missing)}.")
        if extra:
            problems.append(f"Unrecognized columns: {', '.join(extra)}.")
        raise CSVInputError(" ".join(problems))
    return header


def read_customer_csv(upload: BinaryIO) -> pd.DataFrame:
    """Parse an uploaded CSV and return validated, canonically ordered rows."""
    header = _read_header(upload)
    try:
        upload.seek(0)
        customers = pd.read_csv(
            upload,
            encoding="utf-8-sig",
            dtype={column: "string" for column in INTEGER_COLUMNS},
        )
    except (pd.errors.ParserError, UnicodeDecodeError, ValueError) as exc:
        raise CSVInputError(f"Could not parse this CSV: {exc}") from exc

    if customers.empty:
        raise CSVInputError("The CSV must contain at least one customer row.")
    customers = customers.loc[:, header]
    missing_cells = customers.isna()
    if missing_cells.any().any():
        affected = [
            f"{column} ({int(count)} blank)"
            for column, count in missing_cells.sum().items()
            if count
        ]
        raise CSVInputError("Blank values are not allowed: " + ", ".join(affected) + ".")

    for column in [column for column in REQUIRED_COLUMNS if column not in INTEGER_COLUMNS]:
        values = pd.to_numeric(customers[column], errors="coerce")
        invalid = values.isna() | ~np.isfinite(values)
        if invalid.any():
            rows = (np.flatnonzero(invalid.to_numpy())[:5] + 2).tolist()
            raise CSVInputError(
                f"{column} must contain finite numeric values. Check CSV row(s): {rows}."
            )
        customers[column] = values

    for column in INTEGER_COLUMNS:
        parsed_values = []
        invalid_rows = []
        for row_number, raw_value in enumerate(customers[column], start=2):
            try:
                decimal_value = Decimal(str(raw_value).strip())
                if not decimal_value.is_finite() or decimal_value != decimal_value.to_integral_value():
                    raise InvalidOperation
                parsed_values.append(int(decimal_value))
            except (InvalidOperation, ValueError):
                invalid_rows.append(row_number)
                parsed_values.append(0)
        if invalid_rows:
            raise CSVInputError(
                f"{column} must contain integer values. Check CSV row(s): {invalid_rows[:5]}."
            )
        customers[column] = pd.Series(parsed_values, index=customers.index, dtype=object)

    for column in NON_NEGATIVE_COLUMNS:
        if (customers[column] < 0).any():
            raise CSVInputError(f"{column} must be non-negative.")

    for column, (minimum, maximum) in INTEGER_RANGES.items():
        invalid = ~customers[column].between(minimum, maximum)
        if invalid.any():
            raise CSVInputError(
                f"{column} must use values from {minimum} through {maximum}."
            )

    if customers["ID"].duplicated().any():
        duplicate_ids = customers.loc[
            customers["ID"].duplicated(keep=False), "ID"
        ].astype(str).unique()[:5]
        raise CSVInputError(
            "ID values must be unique. Duplicate example(s): "
            + ", ".join(duplicate_ids)
            + "."
        )

    return customers.loc[:, REQUIRED_COLUMNS]

```

### `src/propensity_prediction/dashboard/client.py`

```python
"""HTTP client for the FastAPI review-queue endpoint."""

from __future__ import annotations

import json
from typing import Any

import pandas as pd
import requests

from propensity_prediction.dashboard.csv_input import INTEGER_COLUMNS


class ReviewQueueAPIError(RuntimeError):
    """A readable API connection or response error."""


def request_review_queue(
    customers: pd.DataFrame,
    max_review_count: int,
    api_base_url: str,
) -> dict[str, Any]:
    """Send canonical customer rows to the API and return its response JSON."""
    customer_records = customers.to_dict(orient="records")
    for record in customer_records:
        for column in customers.columns:
            if column in INTEGER_COLUMNS:
                record[column] = int(record[column])
            else:
                record[column] = float(record[column])
    payload = {
        "customers": customer_records,
        "max_review_count": int(max_review_count),
    }
    endpoint = f"{api_base_url.rstrip('/')}/v1/review-queue"
    try:
        response = requests.post(endpoint, json=payload, timeout=(5, 120))
    except requests.RequestException as exc:
        raise ReviewQueueAPIError(
            f"Could not reach the scoring API at {endpoint}. "
            "Confirm the API is running and the address is correct."
        ) from exc

    try:
        response_body = response.json()
    except requests.JSONDecodeError as exc:
        raise ReviewQueueAPIError(
            f"The scoring API returned an unreadable response (HTTP {response.status_code})."
        ) from exc

    if not response.ok:
        error = response_body.get("error", {}) if isinstance(response_body, dict) else {}
        code = error.get("code", "API_ERROR")
        message = error.get("message", response.text)
        details = error.get("details", [])
        detail_text = " ".join(str(detail) for detail in details)
        suffix = f" {detail_text}" if detail_text else ""
        raise ReviewQueueAPIError(
            f"Scoring API error {code} (HTTP {response.status_code}): {message}{suffix}"
        )

    if not isinstance(response_body, dict):
        raise ReviewQueueAPIError("The scoring API response must be a JSON object.")
    return response_body

```

### `streamlit_app.py`

```python
"""Single-page analyst dashboard for risk scoring and review prioritization."""

from __future__ import annotations

import hashlib
import os

import numpy as np
import pandas as pd
import requests
import streamlit as st

from propensity_prediction.dashboard.client import (
    ReviewQueueAPIError,
    request_review_queue,
)
from propensity_prediction.dashboard.csv_input import (
    CSVInputError,
    read_customer_csv,
)


st.set_page_config(
    page_title="Portfolio Review | Credit Risk",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container { padding-top: 2rem; padding-bottom: 3rem; }
    .hero { padding: 1.4rem 1.6rem; border-radius: 1rem;
            background: linear-gradient(115deg, #10263f, #1c5268);
            color: white; margin-bottom: 1.2rem; }
    .hero h1 { color: white; margin: 0 0 .4rem 0; }
    .hero p { color: #d5e6ed; margin: 0; font-size: 1.05rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <h1>Portfolio review</h1>
      <p>Score a customer file and prioritize a capacity-limited review queue.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.caption(
    "This tool estimates default risk for prioritization. It does not recommend "
    "or execute customer interventions."
)

api_base_url = st.text_input(
    "Scoring API address",
    value=os.getenv("PROPENSITY_API_URL", "http://127.0.0.1:8000"),
    help="Base URL of the FastAPI service. For local use, keep the default.",
)
uploaded_file = st.file_uploader(
    "Upload a prediction-time customer CSV",
    type=["csv"],
    help="Include ID and all 23 predictors. Do not include DEFAULT.",
)

customers = None
upload_digest = None
if uploaded_file is not None:
    file_bytes = uploaded_file.getvalue()
    upload_digest = hashlib.sha256(file_bytes).hexdigest()
    try:
        customers = read_customer_csv(uploaded_file)
    except CSVInputError as exc:
        st.error(str(exc))

if customers is not None:
    st.success(
        f"File validated: {len(customers):,} customer rows and "
        f"{len(customers.columns)} expected columns."
    )
    with st.expander("Preview uploaded data", expanded=False):
        st.dataframe(customers.head(10), width="stretch", hide_index=True)

    control_col, summary_col = st.columns([1, 2])
    with control_col:
        max_review_count = st.number_input(
            "Maximum review count",
            min_value=0,
            value=min(10, len(customers)),
            step=1,
            help=(
                "The API accepts an absolute count. If equal-risk customers "
                "straddle the capacity boundary, the tied group is kept intact."
            ),
        )
    with summary_col:
        st.info(
            f"The model will score all **{len(customers):,}** customers. "
            f"The queue will target up to **{int(max_review_count):,}** reviews."
        )

    request_signature = (upload_digest, int(max_review_count), api_base_url.strip())
    if st.button("Score portfolio and build queue", type="primary", width="stretch"):
        if not api_base_url.strip():
            st.error("Enter the base address of the scoring API.")
        else:
            with st.spinner("Scoring the portfolio and applying the review capacity…"):
                try:
                    queue_response = request_review_queue(
                        customers=customers,
                        max_review_count=int(max_review_count),
                        api_base_url=api_base_url.strip(),
                    )
                    st.session_state["queue_result"] = queue_response
                    st.session_state["queue_signature"] = request_signature
                except ReviewQueueAPIError as exc:
                    st.session_state.pop("queue_result", None)
                    st.session_state.pop("queue_signature", None)
                    st.error(str(exc))

    if st.session_state.get("queue_signature") == request_signature:
        result = st.session_state["queue_result"]
        capacity = result["capacity"]
        metric_cols = st.columns(4)
        metric_cols[0].metric("Scored", f"{result['population_count']:,}")
        metric_cols[1].metric("Selected", f"{capacity['selected_count']:,}")
        metric_cols[2].metric("Target capacity", f"{capacity['target_review_count']:,}")
        metric_cols[3].metric("Unused capacity", f"{capacity['unused_capacity']:,}")

        result_frame = pd.DataFrame(result["customers"])
        selected_frame = result_frame[result_frame["selected_for_review"]]
        st.subheader("Risk distribution")
        histogram, edges = np.histogram(
            result_frame["predicted_default_probability"], bins=10, range=(0, 1)
        )
        chart_frame = pd.DataFrame(
            {"Probability range": [f"{left:.1f}–{right:.1f}" for left, right in zip(edges[:-1], edges[1:])],
             "Customers": histogram}
        ).set_index("Probability range")
        st.bar_chart(chart_frame, color="#168a91")

        st.subheader("Prioritized customer queue")
        if selected_frame.empty:
            st.info("No customers were selected at this capacity.")
        else:
            st.dataframe(
                selected_frame,
                width="stretch",
                hide_index=True,
                column_config={
                    "predicted_default_probability": st.column_config.NumberColumn(
                        "Predicted default probability", format="percent"
                    ),
                    "selected_for_review": st.column_config.CheckboxColumn(
                        "Selected for review"
                    ),
                },
            )

        with st.expander("Full ranked portfolio", expanded=False):
            st.dataframe(
                result_frame,
                width="stretch",
                hide_index=True,
                column_config={
                    "predicted_default_probability": st.column_config.NumberColumn(
                        "Predicted default probability", format="percent"
                    ),
                },
            )

        csv_bytes = result_frame.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download full ranked results (CSV)",
            data=csv_bytes,
            file_name="ranked_review_queue.csv",
            mime="text/csv",
            width="stretch",
        )
    elif st.session_state.get("queue_result") is not None:
        st.caption("Upload, capacity, or API address changed. Run scoring to refresh results.")

if uploaded_file is None:
    st.info("Upload a CSV to validate the portfolio and configure the review queue.")

with st.expander("API status"):
    if st.button("Check API health"):
        try:
            response = requests.get(
                f"{api_base_url.rstrip('/')}/health", timeout=(3, 10)
            )
            if response.ok:
                health = response.json()
                if health.get("model_loaded"):
                    st.success("Scoring API is ready and the model is loaded.")
                else:
                    st.warning("API is reachable, but the model artifact is unavailable.")
            else:
                st.error(f"API health endpoint returned HTTP {response.status_code}.")
        except requests.RequestException as exc:
            st.error(f"Could not reach the scoring API: {exc}")

```


---

# Phase 8.6 — Local Integration and Verification

## Goal

Verify the upload, validation, API, model, and ranked-queue workflow using
automated checks and synthetic data; measure representative request sizes;
and provide a repeatable local demonstration. No real customer records or
`DEFAULT` outcomes are needed for these checks.

## Automated coverage

The new pytest cases cover two boundaries:

- `tests/test_dashboard_csv_input.py` checks canonical reordering, duplicate
  headers, required and extra fields, `DEFAULT`, blank and non-finite values,
  integer and category rules, non-negative amounts, duplicate IDs, and empty
  portfolios.
- `tests/test_api_review_queue.py` checks Pydantic request validation, the
  service response shape, probability ordering, capacity behavior, whole-tie
  handling, duplicate portfolio IDs, and the repository's unavailable state.

Service-level probability values are deterministic test doubles. That makes
ranking and tie-boundary assertions stable. The integration smoke script below
uses the real saved model artifact and real local API.

Run the focused checks:

```bash
venv/bin/pytest -q tests/test_dashboard_csv_input.py tests/test_api_review_queue.py
```

Run all project checks, including prior modeling and decision-engine tests:

```bash
venv/bin/pytest -q
```

The full suite completed with **201 passed**. The three Phase 8 focused files
contribute 25 tests.

## Real local integration check

Start the API in a terminal, bound to loopback for local development:

```bash
venv/bin/uvicorn propensity_prediction.api.main:app --host 127.0.0.1 --port 8000
```

In a second terminal, run the end-to-end dashboard smoke script. It creates
three synthetic records without an outcome, injects them into Streamlit's file
uploader, and checks that the dashboard calls the running API, receives real
model scores, and renders the ranked result.

```bash
venv/bin/python scripts/smoke_test_dashboard.py --api-url http://127.0.0.1:8000 --rows 3
```

To also write a CSV for a visible browser walkthrough:

```bash
venv/bin/python scripts/smoke_test_dashboard.py \
  --api-url http://127.0.0.1:8000 \
  --rows 3 \
  --write-csv /tmp/phase8_synthetic_portfolio.csv
```

Then start the interactive dashboard in another terminal:

```bash
venv/bin/streamlit run streamlit_app.py
```

In the browser, upload the generated CSV, choose a review count, run scoring,
inspect the selected rows and full ranking, and download the result CSV. For
the rejection check, add a `DEFAULT` column to a copy of the synthetic CSV and
upload that copy; the dashboard should explain the issue and should not send
the file to the API. The browser walkthrough is intentionally local; the
deployment phase will separately configure the cloud Droplet.

## Synthetic portfolio performance measurement

Run the benchmark while the API is active:

```bash
venv/bin/python scripts/benchmark_api_batches.py \
  --api-url http://127.0.0.1:8000 \
  --row-counts 100 1000 5000 10000 30000
```

Observed on the local development environment with the saved model and
synthetic rows:

| Rows | JSON request size | Elapsed API time |
| ---: | ---: | ---: |
| 100 | 39,449 bytes | 0.074 s |
| 1,000 | 399,420 bytes | 0.192 s |
| 5,000 | 1,996,940 bytes | 0.927 s |
| 10,000 | 3,993,841 bytes | 1.656 s |
| 30,000 | 11,981,441 bytes | 4.771 s |

These are one-shot local measurements, not a service-level guarantee. Cloud
Droplet hardware, concurrent requests, network transfer, and browser memory
can change the results. The 30,000-row run shows that the current API can
process a portfolio at the source dataset's scale in this environment. The
the user selected 30,000 rows as the initial maximum after reviewing these
measurements. Step 8.7 enforces that ceiling at both the dashboard CSV
validator and the API request schema. Do not interpret benchmark coverage
alone as a universal capacity guarantee.

Streamlit's current default per-file upload limit is 200 MB. This is a
framework default, not a measured application requirement. The deployment
phase should review both file-size and request-size limits on the target
Droplet before exposing the service.

## What these checks establish—and what they do not

- CSV policy matches the Phase 8.2 contract, including explicit rejection of
  `DEFAULT`.
- API schema and application-service behavior match the contract and existing
  deterministic queue engine.
- The saved model can load and score synthetic rows through the API, and
  Streamlit can render the returned queue.
- The measured local timings help choose a starting batch limit; they do not
  replace a target-server capacity check.
- The 30,000-row ceiling is covered at the boundary: exactly 30,000 rows are
  accepted, while 30,001 are rejected in both CSV and API validation.
- The artifact path now supports source checkouts, regular package installs
  launched from the project root, and the `PROPENSITY_MODEL_ARTIFACT_PATH`
  override used by a deployment layout.
- The tests do not assess predictive validity, fairness, causal intervention
  effects, or deployment security. Those remain governed by prior modeling
  analysis and the final deployment phase.

## Code added for this step

The full new tests and repeatable helper scripts follow. Source files remain authoritative; refresh these listings when they change.

### `tests/test_dashboard_csv_input.py`

```python
from __future__ import annotations

from io import BytesIO

import pandas as pd
import pytest

from propensity_prediction.dashboard.csv_input import (
    CSVInputError,
    REQUIRED_COLUMNS,
    read_customer_csv,
)


def _valid_customer_data() -> dict[str, str]:
    row = {column: "100" for column in REQUIRED_COLUMNS}
    row.update(
        {
            "ID": "9001",
            "LIMIT_BAL": "50000",
            "AGE": "35.5",
            "SEX": "2",
            "EDUCATION": "2",
            "MARRIAGE": "1",
            "PAY_0": "0",
            "PAY_2": "0",
            "PAY_3": "0",
            "PAY_4": "0",
            "PAY_5": "0",
            "PAY_6": "0",
        }
    )
    return row


def _upload(frame: pd.DataFrame) -> BytesIO:
    return BytesIO(frame.to_csv(index=False).encode("utf-8"))


def test_valid_csv_is_returned_in_canonical_order_and_typed() -> None:
    row = _valid_customer_data()
    columns = list(reversed(REQUIRED_COLUMNS))
    customers = read_customer_csv(_upload(pd.DataFrame([{key: row[key] for key in columns}])))

    assert customers.columns.tolist() == REQUIRED_COLUMNS
    assert customers.loc[0, "ID"] == 9001
    assert isinstance(customers.loc[0, "ID"], int)
    assert customers.loc[0, "AGE"] == pytest.approx(35.5)


def test_default_outcome_is_rejected_with_explanation() -> None:
    row = _valid_customer_data()
    row["DEFAULT"] = "0"

    with pytest.raises(CSVInputError, match="historical outcome"):
        read_customer_csv(_upload(pd.DataFrame([row])))


def test_missing_and_unknown_columns_are_reported() -> None:
    row = _valid_customer_data()
    row.pop("PAY_6")
    row["extra"] = "1"

    with pytest.raises(CSVInputError, match="Missing required columns: PAY_6") as error:
        read_customer_csv(_upload(pd.DataFrame([row])))

    assert "Unrecognized columns: extra" in str(error.value)


def test_duplicate_headers_are_rejected_before_pandas_renames_them() -> None:
    row = _valid_customer_data()
    values = [row[column] for column in REQUIRED_COLUMNS]
    csv_text = ",".join(REQUIRED_COLUMNS + ["ID"]) + "\n"
    csv_text += ",".join(values + ["9002"]) + "\n"

    with pytest.raises(CSVInputError, match="duplicate column names"):
        read_customer_csv(BytesIO(csv_text.encode("utf-8")))


@pytest.mark.parametrize(
    ("column", "value", "message"),
    [
        ("AGE", "", "Blank values are not allowed"),
        ("AGE", "not-a-number", "finite numeric values"),
        ("BILL_AMT1", "inf", "finite numeric values"),
        ("PAY_0", "1.5", "integer values"),
        ("SEX", "3", "SEX must use values from 1 through 2"),
        ("EDUCATION", "5", "EDUCATION must use values from 0 through 4"),
        ("LIMIT_BAL", "-1", "LIMIT_BAL must be non-negative"),
        ("PAY_AMT4", "-0.01", "PAY_AMT4 must be non-negative"),
    ],
)
def test_invalid_values_are_rejected(column: str, value: str, message: str) -> None:
    row = _valid_customer_data()
    row[column] = value

    with pytest.raises(CSVInputError, match=message):
        read_customer_csv(_upload(pd.DataFrame([row])))


def test_duplicate_customer_ids_are_rejected() -> None:
    first = _valid_customer_data()
    second = _valid_customer_data()
    second["AGE"] = "41"

    with pytest.raises(CSVInputError, match="ID values must be unique"):
        read_customer_csv(_upload(pd.DataFrame([first, second])))


def test_header_only_csv_is_rejected() -> None:
    csv_text = ",".join(REQUIRED_COLUMNS) + "\n"

    with pytest.raises(CSVInputError, match="at least one customer row"):
        read_customer_csv(BytesIO(csv_text.encode("utf-8")))

```

### `tests/test_api_review_queue.py`

```python
from __future__ import annotations

import numpy as np
import pytest
from pydantic import ValidationError

from propensity_prediction.api.errors import (
    InvalidPortfolioError,
    ModelArtifactUnavailable,
)
from propensity_prediction.api.repository import ModelArtifactRepository
from propensity_prediction.api.schemas import ReviewQueueRequest
from propensity_prediction.api.service import ReviewQueueService
from propensity_prediction.data.schema import get_feature_columns


def _customer(customer_id: int) -> dict:
    customer = {column: 100.0 for column in get_feature_columns()}
    customer.update(
        {
            "ID": customer_id,
            "LIMIT_BAL": 50000.0,
            "AGE": 35.0,
            "SEX": 2,
            "EDUCATION": 2,
            "MARRIAGE": 1,
            "PAY_0": 0,
            "PAY_2": 0,
            "PAY_3": 0,
            "PAY_4": 0,
            "PAY_5": 0,
            "PAY_6": 0,
        }
    )
    return customer


class InMemoryModelRepository:
    """Small repository double for deterministic service-level checks."""

    is_loaded = True

    def get_model_artifact(self) -> dict:
        return {"test_double": True}


def _build_service(monkeypatch: pytest.MonkeyPatch, scores: list[float]) -> ReviewQueueService:
    monkeypatch.setattr(
        "propensity_prediction.api.service.predict_default_probabilities",
        lambda _artifact, _customers: np.asarray(scores),
    )
    return ReviewQueueService(InMemoryModelRepository())


def test_request_schema_accepts_contract_customer_and_count() -> None:
    request = ReviewQueueRequest.model_validate(
        {"customers": [_customer(1001)], "max_review_count": 1}
    )

    assert request.customers[0].ID == 1001
    assert request.max_review_count == 1


@pytest.mark.parametrize(
    "payload",
    [
        {"customers": [{**_customer(1001), "DEFAULT": 0}], "max_review_count": 1},
        {
            "customers": [
                {key: value for key, value in _customer(1001).items() if key != "AGE"}
            ],
            "max_review_count": 1,
        },
        {"customers": [_customer(1001)], "max_review_count": True},
    ],
)
def test_request_schema_rejects_outcome_missing_field_and_boolean_count(payload: dict) -> None:
    with pytest.raises(ValidationError):
        ReviewQueueRequest.model_validate(payload)


def test_service_returns_full_portfolio_sorted_with_capacity_summary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _build_service(monkeypatch, [0.2, 0.9, 0.5])
    request = ReviewQueueRequest.model_validate(
        {
            "customers": [_customer(1001), _customer(1002), _customer(1003)],
            "max_review_count": 2,
        }
    )

    result = service.build_queue(request)

    assert result["population_count"] == 3
    assert result["capacity"] == {
        "requested_review_count": 2,
        "target_review_count": 2,
        "selected_count": 2,
        "unused_capacity": 0,
    }
    assert [row["customer_id"] for row in result["customers"]] == [1002, 1003, 1001]
    assert [row["selected_for_review"] for row in result["customers"]] == [True, True, False]


def test_service_does_not_split_equal_score_group_at_capacity_boundary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _build_service(monkeypatch, [0.9, 0.9, 0.2])
    request = ReviewQueueRequest.model_validate(
        {
            "customers": [_customer(1001), _customer(1002), _customer(1003)],
            "max_review_count": 1,
        }
    )

    result = service.build_queue(request)

    assert [row["risk_rank"] for row in result["customers"]] == [1, 1, 3]
    assert result["capacity"]["selected_count"] == 0
    assert all(not row["selected_for_review"] for row in result["customers"])


def test_zero_capacity_is_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    service = _build_service(monkeypatch, [0.2])
    request = ReviewQueueRequest.model_validate(
        {"customers": [_customer(1001)], "max_review_count": 0}
    )

    result = service.build_queue(request)

    assert result["capacity"]["selected_count"] == 0
    assert result["capacity"]["unused_capacity"] == 0


def test_duplicate_portfolio_ids_raise_domain_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _build_service(monkeypatch, [0.2, 0.4])
    request = ReviewQueueRequest.model_validate(
        {
            "customers": [_customer(1001), _customer(1001)],
            "max_review_count": 1,
        }
    )

    with pytest.raises(InvalidPortfolioError, match="IDs must be unique"):
        service.build_queue(request)


def test_repository_reports_missing_artifact_as_unavailable(tmp_path) -> None:
    repository = ModelArtifactRepository(tmp_path / "missing-model.joblib")

    with pytest.raises(ModelArtifactUnavailable, match="artifact is not available"):
        repository.get_model_artifact()

```

### `tests/test_model_artifact_paths.py`

```python
from __future__ import annotations

from pathlib import Path

from propensity_prediction.models.artifact import (
    MODEL_ARTIFACT_RELATIVE_PATH,
    _default_model_artifact_path,
)


def test_artifact_path_can_be_configured_with_environment(
    monkeypatch, tmp_path: Path
) -> None:
    configured_path = tmp_path / "custom" / "risk-model.joblib"
    monkeypatch.setenv("PROPENSITY_MODEL_ARTIFACT_PATH", str(configured_path))

    assert _default_model_artifact_path() == configured_path


def test_regular_package_install_can_find_artifact_from_working_directory(
    monkeypatch, tmp_path: Path
) -> None:
    model_path = tmp_path / MODEL_ARTIFACT_RELATIVE_PATH
    model_path.parent.mkdir(parents=True)
    model_path.write_bytes(b"test bundle placeholder")
    monkeypatch.delenv("PROPENSITY_MODEL_ARTIFACT_PATH", raising=False)
    monkeypatch.chdir(tmp_path)

    assert _default_model_artifact_path() == model_path

```

### `scripts/smoke_test_dashboard.py`

```python
"""Exercise the Streamlit upload flow against a running local FastAPI service."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
from streamlit.testing.v1 import AppTest

from propensity_prediction.data.schema import get_feature_columns


def make_synthetic_portfolio(row_count: int) -> pd.DataFrame:
    """Create schema-valid synthetic rows without an outcome column."""
    rows = []
    for index in range(row_count):
        row = {column: float(100 + (index % 20) * 10) for column in get_feature_columns()}
        row.update(
            {
                "ID": 900_000 + index,
                "LIMIT_BAL": float(30_000 + (index % 10) * 10_000),
                "AGE": float(25 + index % 45),
                "SEX": 1 + index % 2,
                "EDUCATION": index % 5,
                "MARRIAGE": index % 4,
            }
        )
        for column in ("PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"):
            row[column] = (index % 5) - 2
        for column in (
            "PAY_AMT1",
            "PAY_AMT2",
            "PAY_AMT3",
            "PAY_AMT4",
            "PAY_AMT5",
            "PAY_AMT6",
        ):
            row[column] = float(index % 500)
        rows.append(row)
    return pd.DataFrame(rows)[["ID", *get_feature_columns()]]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", default=os.getenv("PROPENSITY_API_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--rows", type=int, default=3)
    parser.add_argument(
        "--write-csv",
        type=Path,
        help="Also save the synthetic CSV so it can be uploaded through a browser.",
    )
    args = parser.parse_args()
    if args.rows < 1:
        parser.error("--rows must be at least 1")

    os.environ["PROPENSITY_API_URL"] = args.api_url
    csv_bytes = make_synthetic_portfolio(args.rows).to_csv(index=False).encode("utf-8")
    if args.write_csv:
        args.write_csv.parent.mkdir(parents=True, exist_ok=True)
        args.write_csv.write_bytes(csv_bytes)
        print(f"Synthetic CSV saved to {args.write_csv}")

    with TemporaryDirectory() as directory:
        app_path = Path(directory) / "synthetic_portfolio.csv"
        app_path.write_bytes(csv_bytes)
        streamlit_script = Path(__file__).resolve().parents[1] / "streamlit_app.py"
        app = AppTest.from_file(streamlit_script).run()
        app.file_uploader[0].set_value(
            (app_path.name, app_path.read_bytes(), "text/csv")
        )
        app.run()
        if app.exception:
            raise AssertionError(f"Dashboard failed while validating the CSV: {app.exception}")
        app.button[0].click().run()
        if app.exception:
            raise AssertionError(f"Dashboard workflow raised an exception: {app.exception}")

        result = app.session_state["queue_result"]
        assert result["population_count"] == args.rows
        assert len(result["customers"]) == args.rows
        assert len(app.dataframe) >= 2
        print(
            "PASS: synthetic CSV upload → validation → API scoring → "
            f"ranked results ({args.rows} rows, {result['capacity']['selected_count']} selected)."
        )


if __name__ == "__main__":
    main()

```

### `scripts/benchmark_api_batches.py`

```python
"""Measure local API latency for synthetic portfolio sizes."""

from __future__ import annotations

import argparse
import os
import time

import requests

from propensity_prediction.data.schema import get_feature_columns


INTEGER_COLUMNS = {
    "ID",
    "SEX",
    "EDUCATION",
    "MARRIAGE",
    "PAY_0",
    "PAY_2",
    "PAY_3",
    "PAY_4",
    "PAY_5",
    "PAY_6",
}


def synthetic_records(row_count: int) -> list[dict]:
    records = []
    for index in range(row_count):
        row = {column: float(100 + (index % 20) * 10) for column in get_feature_columns()}
        row.update(
            {
                "ID": 950_000 + index,
                "LIMIT_BAL": float(30_000 + (index % 10) * 10_000),
                "AGE": float(25 + index % 45),
                "SEX": 1 + index % 2,
                "EDUCATION": index % 5,
                "MARRIAGE": index % 4,
            }
        )
        for column in ("PAY_0", "PAY_2", "PAY_3", "PAY_4", "PAY_5", "PAY_6"):
            row[column] = (index % 5) - 2
        for column in (
            "PAY_AMT1",
            "PAY_AMT2",
            "PAY_AMT3",
            "PAY_AMT4",
            "PAY_AMT5",
            "PAY_AMT6",
        ):
            row[column] = float(index % 500)
        records.append(
            {
                column: int(value) if column in INTEGER_COLUMNS else float(value)
                for column, value in row.items()
            }
        )
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", default=os.getenv("PROPENSITY_API_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--row-counts", type=int, nargs="+", default=[100, 1000, 5000])
    args = parser.parse_args()
    endpoint = f"{args.api_url.rstrip('/')}/v1/review-queue"

    for row_count in args.row_counts:
        payload = {"customers": synthetic_records(row_count), "max_review_count": row_count // 10}
        started = time.perf_counter()
        response = requests.post(endpoint, json=payload, timeout=(5, 180))
        elapsed = time.perf_counter() - started
        response.raise_for_status()
        result = response.json()
        print(
            f"rows={row_count} request_bytes={len(response.request.body)} "
            f"elapsed_seconds={elapsed:.3f} selected={result['capacity']['selected_count']}"
        )


if __name__ == "__main__":
    main()

```

### `src/propensity_prediction/models/artifact.py` — package-safe default artifact path

This is the complete changed constant and helper excerpt. Other model artifact code is documented in Step 8.3.

```python
ARTIFACT_FORMAT_VERSION = 1
PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODEL_ARTIFACT_RELATIVE_PATH = Path("models/selected_default_risk_model.joblib")


def _default_model_artifact_path() -> Path:
    """Resolve the artifact for source checkouts and regular package installs."""
    configured_path = os.getenv("PROPENSITY_MODEL_ARTIFACT_PATH")
    if configured_path:
        return Path(configured_path).expanduser()

    working_directory_path = Path.cwd() / MODEL_ARTIFACT_RELATIVE_PATH
    if working_directory_path.is_file():
        return working_directory_path

    return PROJECT_ROOT / MODEL_ARTIFACT_RELATIVE_PATH


DEFAULT_MODEL_ARTIFACT_PATH = _default_model_artifact_path()
```


---

# Phase 8.7 — Enforce the Initial Portfolio Size Limit

## Goal and decision

The user selected a maximum of 30,000 customers per scoring request after
reviewing the Step 8.6 local benchmark. The benchmark processed 30,000
synthetic rows in 4.771 seconds in the local development environment. This
supports the chosen initial ceiling at the source dataset's scale, but does
not guarantee the same performance on the cloud Droplet. Deployment should
measure the target hardware and review HTTP request and file upload limits.

Files with 30,001 or more customers must be split into smaller portfolios.
The same maximum applies to dashboard CSV uploads and direct API requests.

## One shared limit

`src/propensity_prediction/limits.py` defines the application limit:

```python
MAX_CUSTOMER_ROWS = 30_000
```

Both entry points import this constant so the dashboard and API cannot drift
to different portfolio sizes.

## Dashboard CSV enforcement

`read_customer_csv()` parses the uploaded file, confirms it has at least one
row, then checks its row count before field validation or API conversion:

```python
if len(customers) > MAX_CUSTOMER_ROWS:
    raise CSVInputError(
        f"The CSV contains {len(customers):,} customer rows; the maximum is "
        f"{MAX_CUSTOMER_ROWS:,}. Split the portfolio into smaller files."
    )
```

The dashboard catches `CSVInputError` and displays its message. The file is
not sent to the API. The upload is parsed before the row count is known, so
the separate Streamlit byte-size setting remains relevant and will be
reviewed for the target Droplet during deployment.

## API enforcement

The Pydantic request schema constrains `customers` to 1 through 30,000
objects:

```python
customers: Annotated[
    list[CustomerInput], Field(min_length=1, max_length=MAX_CUSTOMER_ROWS)
]
```

FastAPI rejects an oversized request during request validation, before the
service loads rows for scoring. This check is authoritative even when a
caller bypasses Streamlit and sends JSON directly.

## Boundary verification

Automated checks cover both boundaries in both validators:

- 30,000 rows are accepted by CSV and API validation.
- 30,001 rows are rejected by CSV and API validation.

Run the focused checks from the repository root:

```bash
venv/bin/python -m pytest tests/test_dashboard_csv_input.py tests/test_api_review_queue.py
```

The CSV boundary test stubs the dataframe parser after supplying a valid
header, keeping the test focused on count enforcement. The API test uses a
repeated valid customer record to exercise Pydantic's real list-size
validation without invoking model inference.

## Phase 8 closeout

The 30,000-row cap closes the last Phase 8 decision. Phase 8 is complete;
deployment remains the final project phase and will revisit practical limits
on the user's cloud Droplet.
