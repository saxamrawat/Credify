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
from propensity_prediction.limits import MAX_CUSTOMER_ROWS


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
    if len(customers) > MAX_CUSTOMER_ROWS:
        raise CSVInputError(
            f"The CSV contains {len(customers):,} customer rows; the maximum is "
            f"{MAX_CUSTOMER_ROWS:,}. Split the portfolio into smaller files."
        )
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
