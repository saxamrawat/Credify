# Credit Card Propensity & Decision Intelligence Platform

A machine learning and decision-intelligence project for estimating credit-card default risk and translating model predictions into actionable risk prioritization.

## Project Overview

This project explores how historical customer and credit-card behavior can be used to estimate the probability of a customer defaulting on their credit-card payment in the subsequent month.

The project goes beyond building a binary classification model. The objective is to build a decision-oriented analytical system that can:

1. Estimate customer default probability.
2. Rank customers according to relative risk.
3. Group customers into meaningful risk segments.
4. Incorporate business considerations such as potential financial exposure, false-positive/false-negative costs, intervention costs, and operational capacity.
5. Translate model outputs into risk-management priorities.

The project is intended as a prototype decision-intelligence system, not as a production banking or automated credit-approval system.

## Business Problem

Credit-risk teams have limited resources and cannot necessarily provide the same level of attention to every customer.

The central question of this project is:

> Which customers should receive elevated risk-management attention given their estimated probability of default and the constraints of the business?

The primary intended user is a:

- Credit Risk Analyst
- Credit Risk Manager

The system is designed around:

```text
Customer historical data
        ↓
Data validation
        ↓
Data understanding & exploration
        ↓
Feature engineering
        ↓
Default probability model
        ↓
Risk probability
        ↓
Customer ranking / segmentation
        ↓
Business constraints & costs
        ↓
Risk-management priority
```

## Prediction Problem

The underlying machine-learning target is binary:

- `0` → customer does not default in the subsequent month
- `1` → customer defaults in the subsequent month

The model's primary output will be:

```text
P(default | available customer information)
```

Risk bands will be constructed at the decision layer from predicted probability and business considerations rather than treated as separate machine-learning classes.

## Decision Intelligence

The model prediction is only one component of the system.

### Prediction

> How likely is this customer to default?

### Risk prioritization

> How does this customer's estimated risk compare with other customers?

### Decision

> Given risk, financial exposure, intervention cost, and available operational capacity, which customers warrant additional attention?

Potential risk-management actions may include:

- payment reminders
- temporary spending restrictions
- structured repayment options
- additional risk-management attention

The dataset does not contain intervention outcomes or causal evidence, so this project will not claim that these interventions prevent default.

## Dataset

This project uses the **UCI Default of Credit Card Clients Dataset**.

Official source:

https://archive.ics.uci.edu/dataset/350/default%2Bof%2Bcredit%2Bcard%2Bclients

The dataset contains historical credit-card customer information, including:

- demographic information
- credit exposure
- repayment-status history
- billing/statement behavior
- payment behavior

The dataset contains approximately 30,000 customer observations and six months of historical information.

The raw dataset is not committed to this repository. Users should obtain it from the official UCI source and place the raw file under:

```text
data/raw/
```

## Temporal Interpretation

The dataset contains historical information covering six months.

For this project, the modeling interpretation is:

```text
Historical information
(April–September 2005)
        ↓
Estimate probability of
subsequent-month default
```

The exact operational prediction timestamp is not available from the dataset documentation and is therefore treated as a modeling assumption.

## Analytical Boundaries

### Historical population

The dataset represents a specific historical population and should not automatically be treated as representative of modern banking customers or customers in other countries or markets.

### Limited available information

Real-world financial institutions typically have access to substantially more information than is available in this dataset.

### Prediction is not causation

A relationship between customer behavior and default probability does not demonstrate that a particular intervention will prevent default.

### Intervention effectiveness

The dataset does not provide information about intervention cost, intervention effectiveness, customer response to intervention, or financial recovery after intervention.

Any business-cost or intervention simulation in this project will therefore be explicitly identified as an assumption-based prototype.

### Production use

This project is not intended to be:

- a production banking system
- an automated credit approval/rejection system
- a regulatory-compliant credit decision system
- evidence that a particular intervention will prevent default

A real-world deployment would require additional data, validation, monitoring, governance, fairness analysis, regulatory considerations, retraining, and potentially architectural changes.

## Repository Structure

```text
credit-card-propensity-and-decision-intelligence-platform/
│
├── data/
│   ├── raw/
│   └── processed/
│
├── docs/
├── models/
├── notebooks/
├── reports/
│
├── src/
│   └── propensity_prediction/
│       ├── data/
│       └── ...
│
├── tests/
│
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md
```

### Directory responsibilities

#### `data/raw/`

Original datasets obtained from external sources. Raw source data is not committed to Git.

#### `data/processed/`

Meaningful processed datasets produced by the project pipeline. These may be committed when useful for reproducibility and inspection.

#### `notebooks/`

Exploratory analysis, investigation, visualization, and experimentation.

#### `src/`

Reusable Python project code, including data loading, validation, preprocessing, feature engineering, modeling, evaluation, and decision-intelligence components.

#### `models/`

Trained model artifacts and related model outputs.

#### `reports/`

Meaningful analytical outputs such as visualizations, evaluation reports, and business-analysis results.

#### `tests/`

Automated tests for reusable project functionality.

#### `docs/`

Project documentation, architectural decisions, methodology, and supporting documentation.

## Environment Setup

### Requirements

The project is developed using Python.

Create a virtual environment in the project root:

```bash
python -m venv .venv
```

Activate it on Linux/macOS:

```bash
source .venv/bin/activate
```

Install project dependencies:

```bash
pip install -r requirements.txt
```

Install the project package in editable mode:

```bash
pip install -e .
```

## Running Tests

Run the complete test suite with:

```bash
pytest tests -v
```

## Dependency Management

Python dependencies are recorded in `requirements.txt`.

The development environment is version-pinned using:

```bash
pip freeze > requirements.txt
```

The project package itself is configured through `pyproject.toml`.

## Project Phases and Status

### Phase 0 — Problem Definition · Complete

Defined the credit-default problem, target, intended user, prediction
objective, business context, dataset, and analytical boundaries.

### Phase 1 — Project and Data Foundation · Complete

Established the repository and Python environment; acquired, loaded, and
validated the source dataset.

### Phase 2 — Data Understanding and Exploration · Complete

Examined dataset semantics, distributions, repayment behavior,
relationships with default, and data-quality considerations.

### Phase 3 — Data Preparation · Complete

Implemented cleaning, validation, feature preparation, and reproducible
train/validation/test splits.

### Phase 4 — Baseline Modeling · Complete

Established baseline classifiers and evaluation practices for comparison
with later models.

### Phase 5 — Model Development and Evaluation · Complete

Compared and tuned candidate models, evaluated probability quality and
calibration, and selected HistGradientBoosting with engineered features.
The untouched test-set ROC-AUC was 0.7800, PR-AUC was 0.5515, and Brier
score was 0.1352.

### Phase 6 — Explainability and Risk Segmentation · Complete

Added global feature importance, engineered-feature relationship
analysis, grouped local explanations, analyst-facing customer summaries,
and descriptive validation risk bands. The full test suite passed with
134 tests.

### Phase 7 — Decision Intelligence and Risk Prioritization · Complete

The agreed objective is to prioritize customers for limited analyst
attention using predicted default risk. The dataset lacks intervention
costs, outcomes, and causal evidence, so the phase will not claim intervention
effectiveness.

- **Complete:** 7.1 define the objective; 7.2 audit available inputs; 7.3
  compare probability ranking with random selection; 7.4 show illustrative
  capacity scenarios; 7.5 implement the deterministic decision engine; 7.6
  evaluate review-policy scenarios; 7.7 document recommendations and limits;
  7.8 run full Phase 7 validation (176 tests passed).
- **Remaining:** None.

See the [complete Phase 7 documentation](docs/decision_intelligence.md) for all step walkthroughs, code listings, analysis, and recommendations in order.

### Phase 8 — Analyst API and Dashboard · Complete

- **Complete:** 8.1 select the FastAPI + Streamlit architecture; 8.2 define
  the batch JSON request and response contract; 8.3 package the locked model
  for reproducible inference; 8.4 implement the FastAPI scoring service and
  review-queue endpoint; 8.5 build the single-page Streamlit CSV upload and
  analyst dashboard; 8.6 add automated CSV/API checks, verify the real-model
  dashboard workflow, and measure synthetic batch sizes.
- **Complete:** 8.7 enforce the agreed 30,000-customer maximum in CSV uploads
  and API requests; verify the accepted and rejected boundaries.
- **Remaining:** None. The 30,000-row limit is an initial operational cap;
  deployment on the target Droplet should review request and upload limits.
- **Deployment:** reserved for the final project phase on the user's cloud
  Droplet (Phase 11).

See the [complete Phase 8 documentation](docs/analyst_api_dashboard.md) for all seven steps in order, including the decisions, detailed code walkthroughs, integration verification, and 30,000-row portfolio cap.

### Phase 9 — Portfolio Insights Dashboard · Complete

Built the custom HTML/CSS/JavaScript analyst dashboard over FastAPI, including
portfolio overview, cohort exploration, review queue, selection profile,
feature insights, customer drilldown, responsible-use safeguards, exports,
and responsive accessibility improvements. Automated validation passed 210
tests. The dashboard describes model estimates and input patterns; it does not
establish outcomes, causes, intervention effects, or fairness.

See the [complete Phase 9 documentation](docs/portfolio_insights_dashboard.md)
for the plan and all 14 step walkthroughs in order.

### Phase 10 — GenAI Analyst Layer · In progress

Add natural-language summaries or portfolio questions only after the
dashboard's calculations, definitions, and workflows are stable.
The proposed sequence is documented in the
[Phase 10 plan](docs/genai_analyst_layer_plan.md): define bounded analyst use
cases; choose the open-model and experimentation strategy; define minimized evidence context;
build deterministic context assembly; add grounded structured generation;
integrate the dashboard experience; add explicit steps to select a Hugging
Face checkpoint, prepare reviewed synthetic fine-tuning examples, build a
Kaggle LoRA workflow, connect the trained artifact to local inference, compare
base and tuned models, and then prepare for Phase 11 deployment. Each step
still requires the user's choice before implementation. Step 10.1 is complete; see the
[use cases and boundaries](docs/phase_10_step_10_1_use_cases_and_boundaries.md).
Step 10.2 is also complete: the user selected an open-weight Hugging Face
approach and Kaggle training. The original prompt-first plan has been updated
to include actual fine-tuning and user-run Kaggle code in Steps 10.8–10.12.
See the [model strategy](docs/phase_10_step_10_2_open_model_and_kaggle_strategy.md)
and [Phase 10 plan](docs/genai_analyst_layer_plan.md).
Step 10.3 is complete: the LLM context is restricted to traceable aggregates
and explicitly requested grouped explanations, with raw rows and identifiers
excluded. See the [trusted context contract](docs/phase_10_step_10_3_trusted_context_contract.md).
Step 10.4 is complete: FastAPI now recomputes and returns typed, minimized
analyst evidence from the validated portfolio and capacity request. It does
not call a language model yet. See the [server context assembly walkthrough](docs/phase_10_step_10_4_server_context_assembly.md).
Step 10.5 is complete: the API now supports locally hosted Hugging Face
generation with structured claims and server-validated evidence references.
It stays disabled until a local model path and the small-cohort policy are
configured. See the [grounded generation walkthrough](docs/phase_10_step_10_5_grounded_generation.md).
Step 10.6 is complete: the Overview now has an optional portfolio brief and
bounded question panel. It shows generated claims with server-attached
evidence, handles unavailable/refused responses, and keeps no conversation
history. Live generation remains gated until a tuned model passes Step 10.12
and a minimum-cell threshold is explicitly approved. See the
[dashboard experience walkthrough](docs/phase_10_step_10_6_dashboard_experience.md).
Step 10.7 is complete for this iteration: 14 synthetic-data checks pass for
evidence references, privacy exclusions, suppression boundaries, and service
failures. The minimum-cell threshold remains unset by decision, so generation
stays disabled. Real-model review and threshold selection are activation
prerequisites once a checkpoint and representative portfolio are available.
See the [evaluation walkthrough](docs/phase_10_step_10_7_evaluation.md).
Step 10.8 is complete: `Qwen/Qwen3-8B` was selected at a pinned revision
under Apache-2.0 for the Kaggle QLoRA workflow. The model was trained in
Kaggle; its adapter and manifest are stored locally. The current DigitalOcean
Droplet (1 vCPU, 1 GB RAM,
25 GB disk) cannot serve it; Phase 11 must plan a resize or another host before
activation. See the
[checkpoint selection walkthrough](docs/phase_10_step_10_8_checkpoint_selection.md).
Step 10.9 is complete: the user chose a hand-authored synthetic instruction
set. Version `finetune_v1` contains 16 training, 4 validation, and 4 held-out
examples; it uses invented aggregate evidence and the API's structured answer
contract. See the [dataset walkthrough](docs/phase_10_step_10_9_synthetic_dataset.md).
Step 10.10 is complete: a Kaggle notebook now runs QLoRA on the pinned
Qwen3-8B checkpoint using only the training and validation files. It saves an
adapter and manifest. The workspace did not run it; the user completed a run
on a Tesla T4. The manifest records 16 train examples and 4 validation
examples. See the
[Kaggle QLoRA walkthrough](docs/phase_10_step_10_10_kaggle_qlora.md) and
[notebook](notebooks/genai_qwen3_8b_qlora.ipynb).
Step 10.11 is complete: the local provider loads the pinned Qwen3-8B base in
4-bit NF4 and attaches the Kaggle PEFT adapter. It checks model provenance
and stays behind the existing policy gate. No base checkpoint was downloaded
in this workspace, and the 1 GB Droplet cannot serve the model. See the
[adapter inference walkthrough](docs/phase_10_step_10_11_adapter_inference.md).
Step 10.12 is in progress: Option B is selected. A nine-case Kaggle notebook
compares the base and tuned model, records automated contract checks and
resource use, and creates a paired analyst-review sheet. Kaggle execution and
human review are pending. See the [model evaluation walkthrough](docs/phase_10_step_10_12_model_evaluation.md)
and [comparison notebook](notebooks/genai_model_comparison_phase10_step10_12.ipynb).

### Phase 11 — Deployment to Cloud Droplet · Planned · Final Phase

Deploy the completed application to the user's cloud Droplet after the
dashboard and GenAI phases are complete. Security, networking, runtime,
monitoring, backup, and production capacity decisions belong here.

## Modeling Principles

The project will prioritize analytical correctness over simply achieving a high accuracy score.

Important considerations include:

- train/validation/test separation
- leakage prevention
- class imbalance
- appropriate baseline models
- probability calibration
- discrimination metrics
- threshold selection
- ranking quality
- false-positive and false-negative costs
- financial exposure
- operational capacity
- model interpretability
- reproducibility

Accuracy alone will not be treated as sufficient evidence of model usefulness.

## Risk Prioritization Strategy

The intended decision layer combines:

```text
Predicted probability
        +
Relative customer ranking
        +
Financial exposure
        +
False-positive / false-negative costs
        +
Intervention cost
        +
Operational capacity
        ↓
Risk-management priority
```

This allows the project to distinguish between:

> Who has the highest predicted probability of default?

and:

> Who should receive limited risk-management resources?

These are related but different questions.

## Future Architecture

The project is expected to evolve toward:

```text
Customer Data
     ↓
Data Ingestion
     ↓
Validation
     ↓
Cleaning / Transformation
     ↓
Exploratory Data Analysis
     ↓
Feature Engineering
     ↓
Machine Learning
     ↓
Model Evaluation
     ↓
Probability / Risk Estimation
     ↓
Explainability
     ↓
Customer Segmentation
     ↓
Decision Intelligence
     ↓
Analytics Interface / API
     ↓
Optional GenAI Interface
```

GenAI, if introduced, will sit above deterministic analytical and decision tools. It will not replace the underlying statistical and business logic.

## Technology Stack

Current technologies:

- Python
- Pandas
- NumPy
- SciPy
- Matplotlib
- Seaborn
- Scikit-learn
- Jupyter
- Pytest

Additional technologies will be introduced only when justified by project requirements.

## Development Philosophy

This project emphasizes:

- reproducibility
- analytical reasoning
- explicit assumptions
- separation of concerns
- testable code
- data-quality validation
- business-aware modeling
- explainability
- responsible interpretation of model outputs

The objective is not simply to train a model.

The objective is to demonstrate how **data, machine learning, and business reasoning can work together to support decisions**.

## License & Dataset Attribution

The dataset is provided by the UCI Machine Learning Repository.

Refer to the official dataset page for the dataset's licensing and attribution requirements:

https://archive.ics.uci.edu/dataset/350/default%2Bof%2Bcredit%2Bcard%2Bclients
