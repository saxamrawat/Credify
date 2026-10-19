# EDA Findings & Data Quality Decisions

## Purpose

This document records the findings from the initial exploratory data analysis and defines the data-quality decisions that will be carried into preprocessing.

The raw dataset remains unchanged. These decisions apply to the future processed dataset and modeling pipeline.

---

## 1. Dataset-Level Findings

The raw dataset contains:

- 30,000 customer observations
- 25 columns in the loaded MultiIndex representation
- 24 semantic variables plus the spreadsheet identifier column
- no missing values
- no duplicate complete rows
- a binary target
- no negative `LIMIT_BAL` values
- no negative previous-payment amounts
- observed age range of 21–79

The target distribution is:

| Target | Count | Proportion |
|---:|---:|---:|
| 0 | 23,364 | 77.88% |
| 1 | 6,636 | 22.12% |

The target is therefore imbalanced. Model evaluation must not rely on accuracy alone.

---

## 2. Identifier Decision

### `ID`

`ID` is a customer identifier rather than a behavioral or financial predictor.

**Decision:**

- Preserve `ID` in the processed data for traceability.
- Exclude `ID` from model features.
- Do not perform predictive transformations on `ID`.

---

## 3. Target Decision

### `default payment next month`

The target is binary:

- `0` — no default
- `1` — default

**Decision:**

- Preserve the target as a binary variable.
- Do not convert the target into risk bands during preprocessing.
- Risk bands will be created later at the decision layer from model probabilities.

---

## 4. Missing-Value Decision

The validation and EDA stages found no missing values.

**Decision:**

No imputation strategy is required for the current raw dataset.

The preprocessing pipeline should still contain validation checks so that unexpected missing values are detected if the dataset changes.

---

## 5. Duplicate Decision

No complete duplicate rows were observed.

`ID` is also intended to uniquely identify customer observations.

**Decision:**

- Do not remove rows based on duplicate-row logic because no duplicate complete rows were found.
- Retain an explicit identifier-uniqueness validation check in preprocessing.

---

## 6. Demographic Variables

### `SEX`

Observed values conform to the documented categories:

- `1`
- `2`

**Decision:**

Treat `SEX` as a categorical feature rather than a continuous numerical variable.

### `EDUCATION`

The documented categories are:

- `1` — Graduate school
- `2` — University
- `3` — High school
- `4` — Others

The raw data also contains observed values:

- `0`
- `5`
- `6`

These values are outside the documented category definitions.

**Decision:**

Do not silently assign meanings to `0`, `5`, or `6`.

During preprocessing, these undocumented values will be consolidated into an explicit **unknown/other** category rather than being treated as ordered numerical values.

The transformation must be documented so that the original raw values remain recoverable.

### `MARRIAGE`

The documented categories are:

- `1` — Married
- `2` — Single
- `3` — Others

The raw data also contains `0`.

**Decision:**

Treat `0` as an unknown/other category during preprocessing.

The original raw value will remain unchanged in the raw dataset.

---

## 7. Repayment-Status Variables

The six repayment-status variables represent historical repayment behavior:

```text
PAY_0 → September 2005
PAY_2 → August 2005
PAY_3 → July 2005
PAY_4 → June 2005
PAY_5 → May 2005
PAY_6 → April 2005
```

These variables contain ordered behavioral information rather than ordinary continuous measurements.

**Decision:**

- Preserve their temporal ordering.
- Do not treat them as generic nominal categories without further analysis.
- Investigate their exact observed encoding during preprocessing.
- Evaluate whether an ordinal/numerical representation is appropriate for candidate models.
- Do not create transformations solely because the variables are stored as integers.

---

## 8. Billing / Statement Variables

The billing variables represent historical statement amounts:

```text
BILL_AMT1 → September 2005
BILL_AMT2 → August 2005
BILL_AMT3 → July 2005
BILL_AMT4 → June 2005
BILL_AMT5 → May 2005
BILL_AMT6 → April 2005
```

EDA shows that these variables have financial distributions with potentially substantial spread.

**Decision:**

- Retain the variables.
- Do not interpret them as "principal remaining."
- Investigate skewness and extreme observations during preprocessing.
- Do not remove observations solely because they are large without establishing a justified rule.

---

## 9. Previous-Payment Variables

The previous-payment variables represent historical payment amounts:

```text
PAY_AMT1 → September 2005
PAY_AMT2 → August 2005
PAY_AMT3 → July 2005
PAY_AMT4 → June 2005
PAY_AMT5 → May 2005
PAY_AMT6 → April 2005
```

EDA shows that payment amounts have highly uneven distributions and different scales.

**Decision:**

- Retain the variables.
- Investigate skewness and extreme values during preprocessing.
- Consider transformations or scaling only after evaluating candidate models.
- Do not remove large payment values without a documented rule.

---

## 10. Scale and Distribution Findings

The financial variables operate on substantially different numerical scales.

The dataset also contains variables with distributions that are not symmetric.

**Decision:**

Scaling and distribution transformations will be evaluated during preprocessing rather than applied during EDA.

The choice will depend on the model family:

- tree-based models generally do not require feature scaling
- linear models may benefit from scaling
- transformations may be useful for strongly skewed financial variables

No transformation is committed at this stage.

---

## 11. Class Imbalance Decision

The default rate is approximately:

```text
22.12%
```

while the non-default class represents approximately:

```text
77.88%
```

**Decision:**

Model evaluation will include metrics that distinguish the two classes.

Candidate metrics include:

- ROC-AUC
- PR-AUC
- precision
- recall
- F1
- confusion matrix
- probability calibration

Accuracy may be reported for context but will not be the sole model-selection criterion.

---

## 12. Target Relationship Findings

EDA indicates that repayment behavior, financial variables, demographic variables, and credit exposure can be examined for associations with the default outcome.

These relationships are **descriptive associations**, not causal conclusions.

For example:

```text
Feature behavior
      ↓
Observed association
      ↓
Potential predictive signal
```

This does not imply:

```text
Changing the feature
      ↓
Causes default probability to change
```

The dataset does not provide intervention outcomes that would support such causal claims.

---

## 13. Leakage Considerations

The historical variables cover April through September 2005, while the target represents subsequent-month default.

The project will therefore evaluate every feature according to whether it would reasonably have been available at the assumed prediction point.

**Decision:**

- Do not remove a feature merely because it is strongly associated with the target.
- Remove or modify a feature if it represents information that would not have been available at prediction time.
- Preserve the temporal ordering of historical variables throughout feature engineering.

The exact operational prediction timestamp is not specified by the dataset and remains a documented modeling assumption.

---

## 14. Raw vs Processed Data

The raw UCI file is treated as immutable source data.

**Decision:**

```text
data/raw/
    ↓
Validation
    ↓
Cleaning / transformation
    ↓
data/processed/
```

No cleaning decision should modify the raw source file.

---

## 15. Decisions Carried Forward to Preprocessing

The following decisions are now established:

| Area | Decision |
|---|---|
| Raw data | Preserve unchanged |
| `ID` | Keep for traceability, exclude from model features |
| Target | Keep binary |
| Missing values | No imputation currently required |
| Duplicate rows | No removal required |
| `SEX` | Categorical |
| `EDUCATION` | Undocumented values → explicit unknown/other category |
| `MARRIAGE` | `0` → explicit unknown/other category |
| Repayment status | Preserve temporal/ordered behavior; investigate encoding |
| Billing amounts | Retain; investigate skew/extremes |
| Payment amounts | Retain; investigate skew/extremes |
| Scaling | Model-dependent; decide during preprocessing |
| Class imbalance | Use imbalance-aware evaluation |
| Leakage | Evaluate based on prediction-time availability |
| Causality | Do not infer causal effects from associations |

---

## 16. Scope Boundary

This document records decisions for the **current dataset**.

It does not establish:

- production credit policy
- regulatory approval criteria
- universal risk thresholds
- causal intervention effectiveness
- universal population-level conclusions

Those decisions require additional evidence and, in a real deployment, substantially richer operational data.
