"""Versioned Phase 6 global feature-importance reference for the dashboard."""

from __future__ import annotations


# These values are the documented results of the locked Phase 6 model on its
# validation cohort. They are a reference explanation, not recomputed for an
# uploaded portfolio. Update this snapshot only alongside a reviewed model
# version and its validation report.
GLOBAL_FEATURE_IMPORTANCE_REFERENCE = {
    "method": "permutation_importance",
    "scoring_metric": "average_precision",
    "evaluation_reference": (
        "Phase 6 validation cohort · locked HistGradientBoosting model"
    ),
    "repeats": 10,
    "random_state": 42,
    "features": [
        {
            "feature": "PAY_0",
            "description": "Repayment status code, September 2005",
            "importance_mean": 0.087000,
            "importance_std": 0.006401,
        },
        {
            "feature": "PAY_STATUS_MAX",
            "description": "Maximum repayment status code across April–September 2005",
            "importance_mean": 0.084868,
            "importance_std": 0.003954,
        },
        {
            "feature": "BILL_TO_LIMIT_MEAN",
            "description": "Mean bill amount relative to credit limit across six records",
            "importance_mean": 0.007153,
            "importance_std": 0.002057,
        },
        {
            "feature": "BILL_AMT_STD",
            "description": "Variation in bill statement amounts across six records",
            "importance_mean": 0.007094,
            "importance_std": 0.001184,
        },
        {
            "feature": "PAYMENT_TO_BILL_MAX",
            "description": "Maximum payment-to-bill ratio across six records",
            "importance_mean": 0.004540,
            "importance_std": 0.005140,
        },
        {
            "feature": "BILL_AMT1",
            "description": "Bill statement amount, September 2005",
            "importance_mean": 0.004103,
            "importance_std": 0.002471,
        },
        {
            "feature": "PAY_AMT3",
            "description": "Previous payment amount, July 2005",
            "importance_mean": 0.003913,
            "importance_std": 0.001937,
        },
        {
            "feature": "PAY_STATUS_TREND",
            "description": "Linear trend in repayment status codes across six records",
            "importance_mean": 0.003873,
            "importance_std": 0.001802,
        },
        {
            "feature": "PAY_AMT_MEAN",
            "description": "Mean previous payment amount across six records",
            "importance_mean": 0.003148,
            "importance_std": 0.002584,
        },
        {
            "feature": "PAY_3",
            "description": "Repayment status code, July 2005",
            "importance_mean": 0.002465,
            "importance_std": 0.003632,
        },
    ],
}
