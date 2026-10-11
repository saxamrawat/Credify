"""HTTP client for the FastAPI review-queue endpoint."""

from __future__ import annotations

import json
from typing import Any

import pandas as pd
import requests

from propensity_prediction.dashboard.csv_input import INTEGER_COLUMNS


class ReviewQueueAPIError(RuntimeError):
    """A readable API connection or response error."""


def request_review_queue(
    customers: pd.DataFrame,
    max_review_count: int,
    api_base_url: str,
) -> dict[str, Any]:
    """Send canonical customer rows to the API and return its response JSON."""
    customer_records = customers.to_dict(orient="records")
    for record in customer_records:
        for column in customers.columns:
            if column in INTEGER_COLUMNS:
                record[column] = int(record[column])
            else:
                record[column] = float(record[column])
    payload = {
        "customers": customer_records,
        "max_review_count": int(max_review_count),
    }
    endpoint = f"{api_base_url.rstrip('/')}/v1/review-queue"
    try:
        response = requests.post(endpoint, json=payload, timeout=(5, 120))
    except requests.RequestException as exc:
        raise ReviewQueueAPIError(
            f"Could not reach the scoring API at {endpoint}. "
            "Confirm the API is running and the address is correct."
        ) from exc

    try:
        response_body = response.json()
    except requests.JSONDecodeError as exc:
        raise ReviewQueueAPIError(
            f"The scoring API returned an unreadable response (HTTP {response.status_code})."
        ) from exc

    if not response.ok:
        error = response_body.get("error", {}) if isinstance(response_body, dict) else {}
        code = error.get("code", "API_ERROR")
        message = error.get("message", response.text)
        details = error.get("details", [])
        detail_text = " ".join(str(detail) for detail in details)
        suffix = f" {detail_text}" if detail_text else ""
        raise ReviewQueueAPIError(
            f"Scoring API error {code} (HTTP {response.status_code}): {message}{suffix}"
        )

    if not isinstance(response_body, dict):
        raise ReviewQueueAPIError("The scoring API response must be a JSON object.")
    return response_body
