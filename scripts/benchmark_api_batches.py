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
