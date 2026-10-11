import numpy as np
import pandas as pd

from sklearn.ensemble import (
    HistGradientBoostingClassifier,
    RandomForestClassifier,
)
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from propensity_prediction.features.engineering import engineer_features
from propensity_prediction.models.feature_experiment import ENGINEERED_FEATURES

from propensity_prediction.data.schema import (
    IDENTIFIER_COLUMNS,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    ORDINAL_FEATURES,
    get_feature_columns,
)

from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline

from propensity_prediction.data.build import build_processed_dataset
from propensity_prediction.data.preprocessing import create_preprocessor
from propensity_prediction.data.split import split_dataset


RANDOM_STATE = 42


HIST_GRADIENT_PARAMS = {
    "model__max_iter": [100, 200],
    "model__learning_rate": [0.05, 0.1],
    "model__max_leaf_nodes": [15, 31],
    "model__l2_regularization": [0.0, 1.0],
}


RANDOM_FOREST_PARAMS = {
    "model__n_estimators": [200, 300],
    "model__max_depth": [None, 12],
    "model__min_samples_leaf": [3, 5, 10],
    "model__max_features": ["sqrt", 0.8],
}


def get_final_model_configurations() -> dict:
    """Return final candidate models and their tuning grids."""
    return {
        "random_forest": {
            "estimator": RandomForestClassifier(
                class_weight="balanced",
                random_state=RANDOM_STATE,
                n_jobs=1,
            ),
            "param_grid": RANDOM_FOREST_PARAMS,
        },
        "hist_gradient_boosting": {
            "estimator": HistGradientBoostingClassifier(
                random_state=RANDOM_STATE,
            ),
            "param_grid": HIST_GRADIENT_PARAMS,
        },
    }


def _build_pipeline(
    estimator,
    numerical_features,
    categorical_features,
    ordinal_features,
) -> Pipeline:
    """Create preprocessing + model pipeline for a feature set."""
    return Pipeline(
        steps=[
            (
                "preprocessor",
                create_preprocessor(
                    numerical_features=numerical_features,
                    categorical_features=categorical_features,
                    ordinal_features=ordinal_features,
                ),
            ),
            ("model", estimator),
        ]
    )


def prepare_model_features(
    X: pd.DataFrame,
    use_engineered_features: bool,
):
    """Validate and prepare prediction features and their model schema."""
    if not isinstance(X, pd.DataFrame) or X.empty:
        raise ValueError("Customer data must be a non-empty DataFrame.")
    if "DEFAULT" in X.columns:
        raise ValueError("DEFAULT is an outcome and must not be included in prediction data.")

    expected_columns = set(IDENTIFIER_COLUMNS + get_feature_columns())
    actual_columns = set(X.columns)
    missing_columns = expected_columns - actual_columns
    extra_columns = actual_columns - expected_columns
    if missing_columns:
        raise ValueError(f"Customer data is missing required columns: {sorted(missing_columns)}")
    if extra_columns:
        raise ValueError(f"Customer data contains unsupported columns: {sorted(extra_columns)}")
    if X[IDENTIFIER_COLUMNS[0]].isna().any() or X[IDENTIFIER_COLUMNS[0]].duplicated().any():
        raise ValueError("Customer IDs must be non-missing and unique.")

    X = X.drop(columns=["ID"]).copy()

    if use_engineered_features:
        X = engineer_features(X)

        numerical_features = (
            NUMERICAL_FEATURES + ENGINEERED_FEATURES
        )
    else:
        numerical_features = NUMERICAL_FEATURES

    return (
        X,
        numerical_features,
        CATEGORICAL_FEATURES,
        ORDINAL_FEATURES,
    )


def _prepare_features(
    X: pd.DataFrame,
    use_engineered_features: bool,
):
    """Backward-compatible internal name for model feature preparation."""
    return prepare_model_features(X, use_engineered_features)


def _evaluate_probabilities(
    y_true: pd.Series,
    probabilities: np.ndarray,
) -> dict:
    """Evaluate probability predictions."""
    predictions = (probabilities >= 0.5).astype(int)

    return {
        "roc_auc": roc_auc_score(
            y_true,
            probabilities,
        ),
        "pr_auc": average_precision_score(
            y_true,
            probabilities,
        ),
        "brier_score": brier_score_loss(
            y_true,
            probabilities,
        ),
        "accuracy": accuracy_score(
            y_true,
            predictions,
        ),
        "precision": precision_score(
            y_true,
            predictions,
            zero_division=0,
        ),
        "recall": recall_score(
            y_true,
            predictions,
            zero_division=0,
        ),
        "f1": f1_score(
            y_true,
            predictions,
            zero_division=0,
        ),
        "confusion_matrix": confusion_matrix(
            y_true,
            predictions).tolist(),
    }


def _tune_candidate(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    estimator,
    param_grid: dict,
    numerical_features,
    categorical_features,
    ordinal_features,
):
    """Tune one candidate using training-only cross-validation."""
    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    search = GridSearchCV(
        estimator=_build_pipeline(
            estimator,
            numerical_features,
            categorical_features,
            ordinal_features,
        ),
        param_grid=param_grid,
        scoring="average_precision",
        cv=cv,
        n_jobs=-1,
        refit=True,
        return_train_score=False,
        error_score="raise",
    )

    search.fit(X_train, y_train)

    return search


def run_final_selection() -> dict:
    """
    Compare tuned models with original and engineered features.

    Validation data is used for model selection.
    Test data is not used.
    """
    df = build_processed_dataset()
    split = split_dataset(df)

    configurations = get_final_model_configurations()

    results = []

    searches = {}

    for feature_set_name, use_engineered in [
        ("original", False),
        ("engineered", True),
    ]:
        (
            X_train,
            numerical_features,
            categorical_features,
            ordinal_features,
        ) = _prepare_features(
            split.X_train,
            use_engineered,
        )

        (
            X_validation,
            _,
            _,
            _,
        ) = _prepare_features(
            split.X_validation,
            use_engineered,
        )

        for model_name, configuration in configurations.items():
            search = _tune_candidate(
                X_train,
                split.y_train,
                configuration["estimator"],
                configuration["param_grid"],
                numerical_features,
                categorical_features,
                ordinal_features,
            )

            searches[
                f"{model_name}_{feature_set_name}"
            ] = search

            probabilities = search.best_estimator_.predict_proba(
                X_validation
            )[:, 1]

            metrics = _evaluate_probabilities(
                split.y_validation,
                probabilities,
            )

            results.append(
                {
                    "model": model_name,
                    "feature_set": feature_set_name,
                    "cv_pr_auc": search.best_score_,
                    "best_params": search.best_params_,
                    **metrics,
                }
            )

    return {
        "validation_results": pd.DataFrame(results),
        "searches": searches,
    }

def evaluate_selected_model_on_test(
    validation_results: pd.DataFrame,
    searches: dict,
) -> dict:
    """
    Evaluate the selected model once on the untouched test set.

    The selected model is determined from validation results.
    The test set is never used for model selection.
    """
    selected_row = validation_results.sort_values(
        by=["pr_auc", "roc_auc"],
        ascending=False,
    ).iloc[0]

    model_name = selected_row["model"]
    feature_set = selected_row["feature_set"]

    search_key = f"{model_name}_{feature_set}"
    selected_search = searches[search_key]

    df = build_processed_dataset()
    split = split_dataset(df)

    X_test, _, _, _ = _prepare_features(
        split.X_test,
        feature_set == "engineered",
    )

    probabilities = selected_search.best_estimator_.predict_proba(
        X_test
    )[:, 1]

    metrics = _evaluate_probabilities(
        split.y_test,
        probabilities,
    )

    predictions = (probabilities >= 0.5).astype(int)

    return {
        "selected_model": model_name,
        "feature_set": feature_set,
        "best_params": selected_search.best_params_,
        "validation_metrics": selected_row.to_dict(),
        "test_metrics": metrics,
        "test_probabilities": probabilities,
        "test_predictions": predictions,
    }
