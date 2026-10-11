import numpy as np
import pandas as pd
import pytest

from propensity_prediction.decision.engine import (
    BELOW_CAPACITY_REASON,
    SELECTED_REASON,
    TIE_BOUNDARY_REASON,
    ZERO_CAPACITY_REASON,
    build_review_queue,
)


def test_review_queue_ranks_descending_and_selects_within_capacity():
    result = build_review_queue(
        customer_ids=["a", "b", "c", "d", "e"],
        probabilities=[0.2, 0.9, 0.9, 0.8, 0.7],
        max_review_count=3,
    )

    queue = result.customers
    assert queue["customer_id"].tolist() == ["b", "c", "d", "e", "a"]
    assert queue["risk_rank"].tolist() == [1, 1, 3, 4, 5]
    assert queue["selected_for_review"].tolist() == [True, True, True, False, False]
    assert queue["reason_code"].tolist() == [
        SELECTED_REASON,
        SELECTED_REASON,
        SELECTED_REASON,
        BELOW_CAPACITY_REASON,
        BELOW_CAPACITY_REASON,
    ]
    assert result.target_review_count == 3
    assert result.selected_count == 3
    assert result.unused_capacity == 0


def test_tied_group_is_not_split_when_it_crosses_capacity_boundary():
    result = build_review_queue(
        customer_ids=["a", "b", "c", "d", "e"],
        probabilities=[0.95, 0.8, 0.8, 0.7, 0.1],
        max_review_count=2,
    )

    queue = result.customers
    assert queue["customer_id"].tolist() == ["a", "b", "c", "d", "e"]
    assert queue["risk_rank"].tolist() == [1, 2, 2, 4, 5]
    assert queue["selected_for_review"].tolist() == [True, False, False, False, False]
    assert queue["reason_code"].tolist() == [
        SELECTED_REASON,
        TIE_BOUNDARY_REASON,
        TIE_BOUNDARY_REASON,
        BELOW_CAPACITY_REASON,
        BELOW_CAPACITY_REASON,
    ]
    assert result.selected_count == 1
    assert result.unused_capacity == 1
    assert result.selected_count <= result.target_review_count


def test_zero_capacity_selects_no_customer_and_still_assigns_tied_ranks():
    result = build_review_queue(["a", "b", "c"], [0.4, 0.9, 0.9], 0)

    assert result.customers["risk_rank"].tolist() == [1, 1, 3]
    assert not result.customers["selected_for_review"].any()
    assert result.customers["reason_code"].eq(ZERO_CAPACITY_REASON).all()
    assert result.selected_count == 0
    assert result.unused_capacity == 0


def test_capacity_larger_than_population_selects_everyone():
    result = build_review_queue([10, 11], [0.2, 0.8], np.int64(10))

    assert result.target_review_count == 2
    assert result.requested_capacity == 10
    assert result.customers["selected_for_review"].all()
    assert result.unused_capacity == 0


@pytest.mark.parametrize(
    "ids, scores, capacity, message",
    [
        (["a", "b"], [0.2], 1, "equal non-zero lengths"),
        ([["a", "b"]], [[0.2, 0.8]], 1, "one-dimensional"),
        (["a", None], [0.2, 0.8], 1, "missing values"),
        (["a", "a"], [0.2, 0.8], 1, "unique"),
        (["a", "b"], [0.2, np.nan], 1, "finite values"),
        (["a", "b"], [0.2, 1.1], 1, "between 0 and 1"),
        (["a", "b"], [0.2, 0.8], -1, "non-negative integer"),
        (["a", "b"], [0.2, 0.8], 1.5, "non-negative integer"),
        (["a", "b"], [0.2, 0.8], True, "non-negative integer"),
    ],
)
def test_review_queue_rejects_invalid_inputs(ids, scores, capacity, message):
    with pytest.raises(ValueError, match=message):
        build_review_queue(ids, scores, capacity)
