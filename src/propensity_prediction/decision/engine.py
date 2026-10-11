"""Deterministic capacity-limited customer review queue construction."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


SELECTED_REASON = "SELECTED_BY_RISK_RANKING"
BELOW_CAPACITY_REASON = "NOT_SELECTED_BELOW_CAPACITY_BOUNDARY"
TIE_BOUNDARY_REASON = "NOT_SELECTED_TIED_GROUP_EXCEEDS_CAPACITY"
ZERO_CAPACITY_REASON = "NOT_SELECTED_ZERO_CAPACITY"


@dataclass(frozen=True)
class ReviewQueueResult:
    """Sorted customer queue and capacity accounting."""

    customers: pd.DataFrame
    requested_capacity: int
    target_review_count: int
    selected_count: int
    unused_capacity: int


def build_review_queue(
    customer_ids: pd.Series | np.ndarray,
    probabilities: pd.Series | np.ndarray,
    max_review_count: int,
) -> ReviewQueueResult:
    """Rank customers by probability and select whole score groups up to capacity.

    Customers with the same probability share a competition rank. If a tied
    group would exceed the remaining capacity, that entire group and all
    lower-risk groups are left out so the queue never invents a within-tie
    order or exceeds the capacity.
    """
    ids = np.asarray(customer_ids)
    scores = np.asarray(probabilities, dtype=float)

    if ids.ndim != 1 or scores.ndim != 1:
        raise ValueError("customer_ids and probabilities must be one-dimensional.")
    if len(ids) == 0 or len(ids) != len(scores):
        raise ValueError("customer_ids and probabilities must have equal non-zero lengths.")
    if pd.isna(ids).any():
        raise ValueError("customer_ids must not contain missing values.")
    if pd.Index(ids).has_duplicates:
        raise ValueError("customer_ids must be unique.")
    if not np.isfinite(scores).all() or ((scores < 0) | (scores > 1)).any():
        raise ValueError("probabilities must be finite values between 0 and 1.")
    if (
        isinstance(max_review_count, (bool, np.bool_))
        or not isinstance(max_review_count, (int, np.integer))
        or max_review_count < 0
    ):
        raise ValueError("max_review_count must be a non-negative integer.")

    row_count = len(ids)
    target_count = min(int(max_review_count), row_count)
    order = np.argsort(-scores, kind="stable")
    sorted_ids = ids[order]
    sorted_scores = scores[order]
    group_starts = np.r_[
        0,
        np.flatnonzero(sorted_scores[:-1] != sorted_scores[1:]) + 1,
    ]
    group_ends = np.r_[group_starts[1:], row_count]

    ranks = np.empty(row_count, dtype=int)
    selected = np.zeros(row_count, dtype=bool)
    reason_codes = np.empty(row_count, dtype=object)

    if target_count == 0:
        reason_codes[:] = ZERO_CAPACITY_REASON
    else:
        selected_count = 0
        capacity_boundary_reached = False
        for start, end in zip(group_starts, group_ends):
            ranks[start:end] = start + 1
            group_size = end - start
            if capacity_boundary_reached:
                reason_codes[start:end] = BELOW_CAPACITY_REASON
            elif selected_count + group_size <= target_count:
                selected[start:end] = True
                reason_codes[start:end] = SELECTED_REASON
                selected_count += group_size
            else:
                if group_size > 1 and selected_count < target_count:
                    reason_codes[start:end] = TIE_BOUNDARY_REASON
                else:
                    reason_codes[start:end] = BELOW_CAPACITY_REASON
                capacity_boundary_reached = True

    if target_count == 0:
        ranks[:] = np.repeat(group_starts, group_ends - group_starts) + 1

    reason_text = {
        SELECTED_REASON: (
            "Selected by descending predicted default probability within the stated capacity."
        ),
        BELOW_CAPACITY_REASON: (
            "Not selected because this lower-risk score group falls beyond the capacity boundary."
        ),
        TIE_BOUNDARY_REASON: (
            "Not selected because keeping this equal-probability group intact would exceed capacity."
        ),
        ZERO_CAPACITY_REASON: "Not selected because review capacity is zero.",
    }
    customers = pd.DataFrame(
        {
            "customer_id": sorted_ids,
            "predicted_default_probability": sorted_scores,
            "risk_rank": ranks,
            "selected_for_review": selected,
            "reason_code": reason_codes,
        }
    )
    customers["reason"] = customers["reason_code"].map(reason_text)
    selected_count = int(selected.sum())
    return ReviewQueueResult(
        customers=customers,
        requested_capacity=int(max_review_count),
        target_review_count=target_count,
        selected_count=selected_count,
        unused_capacity=target_count - selected_count,
    )
