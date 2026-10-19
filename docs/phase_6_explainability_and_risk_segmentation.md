# Phase 6 — Explainability and Risk Segmentation

## Phase overview

- **Status:** Complete.
- **Objective:** Explain the selected model's global patterns and individual predictions, and summarize probabilities with descriptive risk bands.
- **Scope:** Validation-based permutation importance, engineered-feature relationships, local explanations, customer summaries, and risk bands.
- **Outcome and evidence:** Analyst-facing global and local explanations and descriptive validation risk bands were delivered; the phase validation passed 134 tests.
- **Limitations:** Explanations describe model associations, not causes or intervention effects. The held-out test set is excluded from explanation development.

## Contents

- [Purpose and scope](#purpose-and-scope)
- [Step 6.1 — Explainability requirements](#step-6-1)
- [Step 6.2 — Global feature importance](#step-6-2)
- [Step 6.3 — Engineered-feature relationships](#step-6-3)
- [Step 6.4 — Local explanation method](#step-6-4)
- [Step 6.5 — Individual customer explanations](#step-6-5)
- [Step 6.6 — Descriptive risk bands](#step-6-6)
- [Step 6.7 — Phase validation](#step-6-7)
- [Reproduction commands](#reproduction-commands)
- [Phase conclusion and limitations](#phase-conclusion-and-limitations)

## Purpose and scope

Phase 6 explains how the selected credit-default model behaves, investigates
how engineered variables relate to their source inputs, provides local
explanations for individual predictions, and summarizes scores as
descriptive risk bands.

The intended analyst question is: **Which customers should receive
elevated risk-management attention when resources are limited?** The model
estimates the probability of default next month from historical data. It
does not establish that reminders, spending limits, or repayment plans
prevent default. Risk bands are decision-layer summaries, not classes
discovered as objectively true customer types.

The held-out test set is not used for feature importance, relationship
analysis, local explanation, or risk-band construction. The final Phase 5
model and its parameters remain unchanged.

<a id="step-6-1"></a>
## Step 6.1 — Explainability requirements

Global explanations should describe the patterns the model generally uses
to distinguish higher- from lower-risk customers. Local explanations
should describe why a customer received a particular model probability.
Explanations should be analyst-readable, show direction where supported,
provide probability context, and distinguish predictive association from
causation.

<a id="step-6-2"></a>
## Step 6.2 — Global feature importance

Permutation importance was calculated on validation data using Average
Precision, matching the imbalanced classification objective used for
model selection. The model was fitted on training data only. The leading
features were:

| Feature | Mean importance | Standard deviation |
|---|---:|---:|
| `PAY_0` | 0.087000 | 0.006401 |
| `PAY_STATUS_MAX` | 0.084868 | 0.003954 |
| `BILL_TO_LIMIT_MEAN` | 0.007153 | 0.002057 |
| `BILL_AMT_STD` | 0.007094 | 0.001184 |
| `PAYMENT_TO_BILL_MAX` | 0.004540 | 0.005140 |
| `BILL_AMT1` | 0.004103 | 0.002471 |
| `PAY_AMT3` | 0.003913 | 0.001937 |
| `PAY_STATUS_TREND` | 0.003873 | 0.001802 |
| `PAY_AMT_MEAN` | 0.003148 | 0.002584 |
| `PAY_3` | 0.002465 | 0.003632 |

The model relies heavily on repayment-status information, particularly
`PAY_0` and `PAY_STATUS_MAX`; billing- and payment-derived features make
smaller additional contributions. These values are not independent
business-variable importance: engineered features and their source
columns can share information. Near-zero or slightly negative permutation
importance does not mean a feature is protective or causal; it means that
shuffling it did not reduce validation Average Precision in this run.

<a id="step-6-3"></a>
## Step 6.3 — Engineered-feature relationships

The 20 engineered features are deterministic transformations of original
columns. Training-split Spearman correlations describe their pairwise
monotonic associations with source columns. A display threshold of
`|rho| >= 0.70` is used as a scanning aid, not as a statistical test or a
definition of redundancy. Formula-based groupings describe how features
are constructed; they are not discovered customer segments.

Observed relationships include:

- `PAY_STATUS_MAX` is most associated with `PAY_0` (`rho = 0.753`).
- `PAY_STATUS_MEAN` and `PAY_STATUS_MIN` associate strongly with several
  monthly repayment-status fields.
- `BILL_AMT_MEAN`, `BILL_AMT_MAX`, and `BILL_AMT_MIN` associate strongly
  with multiple monthly bill amounts.
- `BILL_TO_LIMIT_MEAN` associates strongly with monthly bill amounts;
  pairwise correlation does not establish whether the limit denominator
  adds conditional signal.
- Payment-to-bill ratios have no single source variable above the display
  threshold. This does not demonstrate unique predictive information.
- Weak pairwise association between a trend or dispersion summary and any
  single source column does not demonstrate independence from all source
  columns.

No engineered feature adds new raw information. Such summaries and ratios
can still provide useful structure to a model. Pairwise correlation does
not estimate conditional predictive contribution. Importance for an
engineered feature and its sources must not be added or described as
independent contributions.

<a id="step-6-4"></a>
## Step 6.4 — Local explanation method

The project uses grouped interventional Shapley values for four disjoint
groups of original predictors:

- `repayment_status_history`: six monthly repayment-status inputs.
- `billing_and_credit_limit`: credit limit and six monthly bill amounts.
- `payment_amount_history`: six monthly payment amounts.
- `customer_profile`: age, sex, education, and marriage.

For each coalition, customer values replace background values for the
selected groups; engineered features are recomputed before scoring. All
coalitions are enumerated for the four groups. Contributions sum to the
customer prediction minus the mean probability for a deterministic
training-background sample (64 rows by default). Grouping prevents
derived fields from being counted as separate additive reasons alongside
their source inputs.

This is an interventional comparison. Replacing groups independently can
break relationships between them and create uncommon combinations.
Correlated groups may share attribution. Contributions describe model
behavior under these comparisons; they are not causes or effects of real
interventions. The background mean is not a business cutoff or an
individual counterfactual outcome.

<a id="step-6-5"></a>
## Step 6.5 — Individual customer explanations

An analyst-facing explanation reports the model's estimated default
probability for next month, the reference-sample mean, the difference in
percentage points, and signed group contributions. Wording identifies
these as model attributions and clarifies that a probability is an
estimate, not certainty about an individual customer.

`explain_validation_customer(customer_id)` locates the ID in the
validation partition, fits the model on training rows, and uses training
rows as the explanation background. ID is used for lookup only and is
excluded from model features. An example validation prediction returned
16.4%, compared with a 25.3% reference-sample mean; its contribution
summary was produced with a 16-row background sample. This is an example
of model output, not a recommendation about that customer.

<a id="step-6-6"></a>
## Step 6.6 — Descriptive risk bands

Four equal-frequency bands are fit from validation probabilities and
labeled `Lower`, `Moderate`, `Elevated`, and `Highest` in ascending score
order. The cut points are approximately `0.0894`, `0.1444`, and `0.2631`.
Tied probabilities stay in the same band; if ties collapse cut points,
the implementation returns fewer bands. Open-ended first and last
intervals allow the fitted definition to assign later scores outside the
validation range.

| Risk band | Customers | Mean predicted probability | Observed default rate |
|---|---:|---:|---:|
| Lower | 1,125 | 0.0631 | 5.42% |
| Moderate | 1,125 | 0.1171 | 13.07% |
| Elevated | 1,125 | 0.1882 | 19.11% |
| Highest | 1,125 | 0.5098 | 50.84% |

Observed default rate increases across these bands in this validation
sample. This supports the bands as a descriptive ranking for this cohort;
it does not set an action policy or guarantee future rates. No business
threshold is inferred because operational capacity, intervention costs,
and a loss function have not been specified. These bands do not imply
that an intervention will reduce default.

<a id="step-6-7"></a>
## Step 6.7 — Phase validation

The completed Phase 6 changes passed the full automated project suite:

```text
134 passed in 132.31 seconds
```

The explainability-specific tests passed (**30 passed**), validation
analysis paths were exercised on the project data, and `git diff --check`
passed. During review, local explanation background sampling was adjusted
to sample by row position so duplicate DataFrame index labels cannot
accidentally duplicate sampled rows.

## Reproduction commands

```bash
# Full project tests
venv/bin/python -m pytest -q

# Explainability-specific tests
venv/bin/python -m pytest \
  tests/test_global_importance.py \
  tests/test_feature_relationships.py \
  tests/test_local_explanation.py \
  tests/test_customer_explanations.py \
  tests/test_risk_segmentation.py -q

# Training-split engineered-feature relationships
PYTHONPATH=src venv/bin/python -m propensity_prediction.explainability.feature_relationships

# Validation risk-band analysis
PYTHONPATH=src venv/bin/python -m propensity_prediction.explainability.risk_segmentation
```

## Phase conclusion and limitations

Phase 6 provides global feature importance, engineered-feature lineage
and association analysis, grouped local probability explanations,
analyst-facing summaries, and validation-based descriptive risk bands.
All findings concern a historical dataset and a predictive model. They
do not establish causality, intervention effectiveness, or a production
or regulatory approval/rejection system. The separate step notes have
been consolidated into this document.
