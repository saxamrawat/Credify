# Phase 4 — Baseline Modeling Report

## Phase overview

- **Status:** Complete.
- **Objective:** Establish simple, defensible predictive baselines and measure their stability before advanced modeling.
- **Scope:** Compare a prior-based dummy model, logistic regression, and a decision tree using the Phase 3 split and training-only cross-validation.
- **Outcome and evidence:** This report establishes the reference performance and modeling boundaries used by later phases. Detailed metrics and fold results follow below.
- **Limitations:** Baseline results are comparative evidence, not a production model recommendation.

## Contents

- [Objective](#1-objective)
- [Data and experimental boundary](#2-data-and-experimental-boundary)
- [Baseline models](#3-baseline-models)
- [Evaluation metrics](#4-evaluation-metrics)
- [Single validation results](#5-single-validation-results)
- [Five-fold cross-validation](#6-five-fold-cross-validation)
- [Fold-level results](#7-fold-level-results)
- [Interpretation](#8-interpretation)
- [What the baseline establishes](#9-what-the-baseline-establishes)
- [Modeling boundary](#10-modeling-boundary)
- [Baseline conclusion](#11-baseline-conclusion)

## 1. Objective

The purpose of Phase 4 baseline modeling is to establish simple, defensible machine-learning baselines before feature engineering, hyperparameter tuning, advanced models, or decision-threshold optimization.

The project predicts the probability that a customer defaults on their credit-card payment in the subsequent month.

The baseline experiment asks whether the prepared dataset contains useful predictive signal, how simple linear and nonlinear classifiers perform, and whether their results are reasonably stable across different training folds.

The baseline models are not treated as final production models.

## 2. Data and Experimental Boundary

The Phase 3 data-preparation pipeline is used.

The dataset is split into:

- Training: 70% — 21,000 observations
- Validation: 15% — 4,500 observations
- Test: 15% — 4,500 observations

The split is stratified on `DEFAULT` and uses `random_state=42`.

The test set is intentionally not used during baseline model development or cross-validation.

For cross-validation, preprocessing is fitted independently inside every fold through a scikit-learn `Pipeline`.

## 3. Baseline Models

### Dummy Classifier

`DummyClassifier(strategy="prior", random_state=42)` provides a no-skill reference based on the observed training-set class distribution.

### Logistic Regression

`LogisticRegression(max_iter=1000, random_state=42)` provides a simple classical classification baseline that produces probabilities.

### Decision Tree

`DecisionTreeClassifier(random_state=42)` provides a simple nonlinear baseline. It is intentionally not tuned at this stage.

## 4. Evaluation Metrics

The recorded metrics are:

- ROC-AUC
- PR-AUC / Average Precision
- Accuracy
- Precision
- Recall
- F1
- Confusion matrix

ROC-AUC and PR-AUC are particularly important because the project ultimately needs useful risk ranking and probability estimates.

Accuracy is not sufficient because the target is imbalanced:

- `DEFAULT = 0`: 77.88%
- `DEFAULT = 1`: 22.12%

The default 0.5 threshold is used only for initial classification metrics. It is not a business decision threshold.

## 5. Single Validation Results

| Model | ROC-AUC | PR-AUC | Accuracy | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| Dummy | 0.5000 | 0.2211 | 0.7789 | 0.0000 | 0.0000 | 0.0000 |
| Logistic Regression | 0.7138 | 0.5026 | 0.8084 | 0.6905 | 0.2422 | 0.3586 |
| Decision Tree | 0.5999 | 0.2783 | 0.7176 | 0.3683 | 0.3879 | 0.3779 |

The dummy classifier provides the expected no-skill reference.

Logistic Regression captures substantially more predictive signal than the dummy reference. At the default 0.5 threshold it has precision 0.6905 and recall 0.2422.

The Decision Tree also performs above the dummy reference but has lower ROC-AUC and PR-AUC in this baseline configuration. Its default-threshold precision is 0.3683 and recall is 0.3879.

These threshold-dependent metrics are descriptive observations, not final business-threshold decisions.

## 6. Five-Fold Cross-Validation

Five-fold stratified cross-validation was performed using only the 70% training portion. Preprocessing was fitted independently within every fold.

| Model | Mean ROC-AUC | ROC-AUC Std | Mean PR-AUC | PR-AUC Std |
|---|---:|---:|---:|---:|
| Dummy | 0.5000 | 0.0000 | 0.2212 | 0.0000 |
| Logistic Regression | 0.7271 | 0.0095 | 0.5080 | 0.0122 |
| Decision Tree | 0.6116 | 0.0093 | 0.2875 | 0.0070 |

## 7. Fold-Level Results

### ROC-AUC

- Dummy: `0.5000, 0.5000, 0.5000, 0.5000, 0.5000`
- Logistic Regression: `0.7364, 0.7408, 0.7180, 0.7186, 0.7219`
- Decision Tree: `0.6198, 0.6173, 0.6196, 0.6047, 0.5966`

### PR-AUC

- Dummy: `0.2212, 0.2212, 0.2212, 0.2212, 0.2212`
- Logistic Regression: `0.5164, 0.5212, 0.4887, 0.5149, 0.4987`
- Decision Tree: `0.2936, 0.2920, 0.2934, 0.2828, 0.2759`

## 8. Interpretation

Logistic Regression is reasonably consistent across the five folds.

ROC-AUC ranges from 0.7180 to 0.7408, with mean 0.7271 and standard deviation 0.0095.

PR-AUC ranges from 0.4887 to 0.5212, with mean 0.5080 and standard deviation 0.0122.

The original held-out validation result was ROC-AUC 0.7138 and PR-AUC 0.5026, which is reasonably aligned with the cross-validation measurements.

The Decision Tree also shows relatively consistent fold-level performance, but its mean ROC-AUC and PR-AUC are lower than those of Logistic Regression in this untuned baseline configuration.

The baseline experiment therefore provides evidence that the prepared feature set contains predictive information and that a simple Logistic Regression model can capture meaningful signal.

## 9. What the Baseline Establishes

The baseline experiment establishes that:

1. The prepared dataset contains predictive signal for subsequent default.
2. A no-skill classifier provides a reference point for performance.
3. Logistic Regression captures useful predictive signal.
4. Logistic Regression behaves reasonably consistently across five training folds.
5. The simple Decision Tree also captures some signal, with different classification behavior.
6. Accuracy alone does not adequately describe this problem.
7. Probability-ranking metrics are important for the project's risk-prioritization objective.

It does not establish:

- the final model
- optimal hyperparameters
- optimal classification or business thresholds
- probability calibration quality
- final risk segmentation
- causal effectiveness of interventions
- production or regulatory suitability

The test set has not been used for final evaluation.

## 10. Modeling Boundary

The project ultimately needs customer risk estimates that can support prioritization. Model output should therefore remain a probability:

`P(DEFAULT = 1 | available customer information)`

rather than immediately becoming a binary decision.

Threshold selection belongs to later decision-intelligence analysis, where false-positive costs, false-negative costs, financial exposure, intervention capacity, and other business assumptions can be considered explicitly.

## 11. Baseline Conclusion

The baseline experiment provides a defensible reference point for subsequent modeling work.

Future feature engineering, model development, tuning, calibration, and decision-layer work should be compared against this preserved baseline while maintaining:

- training/validation/test separation
- leakage-safe preprocessing
- probability-based evaluation
- class-imbalance-aware metrics
- reproducibility
- explicit documentation of assumptions
