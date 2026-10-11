from __future__ import annotations

from io import BytesIO

import pandas as pd
import pytest

from propensity_prediction.dashboard.csv_input import (
    CSVInputError,
    REQUIRED_COLUMNS,
    read_customer_csv,
)
from propensity_prediction.limits import MAX_CUSTOMER_ROWS


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


@pytest.mark.parametrize("row_count", [MAX_CUSTOMER_ROWS, MAX_CUSTOMER_ROWS + 1])
def test_csv_enforces_maximum_portfolio_size(
    monkeypatch: pytest.MonkeyPatch, row_count: int
) -> None:
    row = _valid_customer_data()
    upload = _upload(pd.DataFrame([{key: row[key] for key in REQUIRED_COLUMNS}]))
    parsed = pd.DataFrame([row] * row_count)
    parsed["ID"] = range(row_count)
    monkeypatch.setattr(pd, "read_csv", lambda *_args, **_kwargs: parsed.copy())

    if row_count == MAX_CUSTOMER_ROWS:
        assert len(read_customer_csv(upload)) == MAX_CUSTOMER_ROWS
    else:
        with pytest.raises(CSVInputError, match="maximum is 30,000"):
            read_customer_csv(upload)
