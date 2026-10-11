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
