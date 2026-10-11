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
