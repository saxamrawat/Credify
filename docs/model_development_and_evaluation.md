# Phase 5 — Model Development & Evaluation

## Phase overview

- **Status:** Complete.
- **Objective:** Compare, tune, calibrate, and evaluate models for default-risk prediction.
- **Scope:** Engineer historical-behavior features; compare candidate models; tune leading candidates; assess probability quality and generalization.
- **Outcome and evidence:** HistGradientBoosting with engineered features was selected. Untouched test metrics were ROC-AUC 0.7800, PR-AUC 0.5515, and Brier score 0.1352.
- **Limitations:** These metrics describe the historical UCI test population and do not establish performance on a modern or different customer population.

## Contents

- [Objective](#objective)
- [Feature engineering](#feature-engineering)
- [Original versus engineered features](#original-vs-engineered-features)
- [Candidate models](#candidate-models)
- [Hyperparameter tuning](#hyperparameter-tuning)
- [Probability evaluation and calibration](#probability-evaluation-and-calibration)
- [Final model selection](#final-model-selection)
- [Untouched test evaluation](#untouched-test-evaluation)
- [Validation versus test](#validation-vs-test)
- [Reproducibility and validation](#reproducibility-and-validation)
- [Limitations](#limitations)
- [Phase 6 handoff](#phase-6-handoff)
- [Conclusion](#conclusion)

## Objective
Develop, compare, tune, calibrate, and evaluate models for credit-card default prediction, with emphasis on useful risk probabilities and generalization.

**Final model: HistGradientBoosting + engineered features.**

## Feature Engineering
Twenty historical-behavior features were created across repayment status, billing amounts, payment amounts, and payment/billing relationships. The target is not used to create features.

Important interpretation notes:
- Historical billing amounts can be negative; payment-to-bill ratios were not artificially clipped.
- `BILL_TO_LIMIT_MEAN` is a billing-to-limit proxy, not formal credit utilization.

## Original vs Engineered Features

| Feature set | ROC-AUC | PR-AUC | Accuracy | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| Original | 0.7138 | 0.5026 | 0.8084 | 0.6905 | 0.2422 | 0.3586 |
| Engineered | 0.7486 | 0.5128 | 0.8084 | 0.6424 | 0.3015 | 0.4104 |

Engineered features improved ROC-AUC by 0.0348, PR-AUC by 0.0102, recall by 0.0593, and F1 by 0.0518.

## Candidate Models
The phase evaluated Dummy Classifier, Logistic Regression, Decision Tree, Random Forest, Gradient Boosting, and HistGradientBoosting. Random Forest and HistGradientBoosting were the strongest advanced candidates.

## Hyperparameter Tuning
Random Forest and HistGradientBoosting were tuned using 5-fold StratifiedKFold cross-validation. Average Precision / PR-AUC was the primary tuning metric, with preprocessing inside the modeling pipeline.

Final selected parameters:

```text
l2_regularization = 1.0
learning_rate      = 0.05
max_iter           = 100
max_leaf_nodes     = 31
```

## Probability Evaluation and Calibration
Probability quality was evaluated using ROC-AUC, PR-AUC, and Brier score. HistGradientBoosting showed substantially better calibration than Random Forest in the calibration experiment.

| Model | ROC-AUC | PR-AUC | Brier |
|---|---:|---:|---:|
| Tuned Random Forest | 0.7749 | 0.5496 | 0.1703 |
| Tuned HistGradientBoosting | 0.7769 | 0.5452 | 0.1364 |

The operating threshold is not treated as final; business threshold selection belongs to the decision-intelligence phase.

## Final Model Selection

| Model | Feature set | CV PR-AUC | Validation ROC-AUC | Validation PR-AUC | Brier |
|---|---|---:|---:|---:|---:|
| Random Forest | Original | 0.5573 | 0.7749 | 0.5496 | 0.1703 |
| HistGradientBoosting | Original | 0.5631 | 0.7769 | 0.5452 | 0.1364 |
| Random Forest | Engineered | 0.5640 | 0.7756 | 0.5473 | 0.1695 |
| **HistGradientBoosting** | **Engineered** | **0.5656** | **0.7797** | **0.5501** | **0.1358** |

The selected model is HistGradientBoosting with engineered features. Selection used validation results; the test set was not used for selection.

## Untouched Test Evaluation

| Metric | Test |
|---|---:|
| ROC-AUC | **0.7800** |
| PR-AUC | **0.5515** |
| Brier score | **0.1352** |
| Accuracy | **0.8173** |
| Precision | **0.6642** |
| Recall | **0.3534** |
| F1 | **0.4613** |

Confusion matrix at the current 0.5 threshold:

```text
                Predicted
                 0     1
Actual 0       3326   178
Actual 1        644   352
```

The threshold is not a final business threshold because business costs, intervention capacity, and risk priorities have not yet been incorporated.

## Validation vs Test

| Metric | Validation | Test |
|---|---:|---:|
| ROC-AUC | 0.7797 | 0.7800 |
| PR-AUC | 0.5501 | 0.5515 |
| Brier score | 0.1358 | 0.1352 |
| Accuracy | 0.8167 | 0.8173 |
| Precision | 0.6610 | 0.6642 |
| Recall | 0.3508 | 0.3534 |
| F1 | 0.4583 | 0.4613 |

The close agreement indicates consistent generalization to the held-out test population, with no obvious substantial overfitting in this evaluation.

## Reproducibility and Validation
The complete automated suite passed:

**104 passed in 118.50 seconds.**

Coverage includes data loading/cleaning, schema and splitting, preprocessing, baseline models, cross-validation, feature engineering, candidate models, evaluation, calibration, tuning, and final model selection.

The test set remains isolated from tuning and model selection.

## Limitations
- The dataset represents a historical credit-card population and is not universally representative.
- Real financial institutions generally have richer data.
- The model predicts default risk and does not prove intervention effectiveness.
- The 0.5 threshold is not a final business operating threshold.
- Intervention costs, exposure-weighted expected loss, and operational capacity are not yet incorporated.
- This is not a production or regulatory credit approval/rejection system.
- Fairness and responsible-use analysis remain future work.

## Phase 6 Handoff
Phase 5 establishes a tuned, calibrated predictive probability model.

Phase 6 will focus on:
- model explainability
- important risk drivers
- individual prediction explanations
- meaningful risk segmentation

These outputs will later feed the decision-intelligence layer.

## Conclusion
Phase 5 successfully progressed from baseline prediction to a tuned, calibrated, independently tested model.

Final test performance:
- **ROC-AUC: 0.7800**
- **PR-AUC: 0.5515**
- **Brier score: 0.1352**
- **F1: 0.4613**

**Phase 5 is complete.**
