"""File-backed repository for the fitted model artifact."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from propensity_prediction.data.build import PROCESSED_DATA_PATH, build_processed_dataset
from propensity_prediction.data.split import split_dataset
from propensity_prediction.models.artifact import (
    DEFAULT_MODEL_ARTIFACT_PATH,
    load_model_artifact,
)
from propensity_prediction.api.errors import ModelArtifactUnavailable


logger = logging.getLogger(__name__)


class ModelArtifactRepository:
    """Load a trusted local model bundle once and serve it from memory."""

    def __init__(self, path: str | Path = DEFAULT_MODEL_ARTIFACT_PATH) -> None:
        self.path = Path(path)
        self._model_artifact: dict | None = None
        self._explanation_background: pd.DataFrame | None = None
        self._load_error: Exception | None = None

    @property
    def is_loaded(self) -> bool:
        return self._model_artifact is not None

    def load(self) -> bool:
        """Load the bundle once; leave the API alive if it is unavailable."""
        try:
            self._model_artifact = load_model_artifact(self.path)
            self._load_error = None
            logger.info("Loaded model artifact from %s", self.path)
            return True
        except Exception as exc:
            self._model_artifact = None
            self._load_error = exc
            logger.exception("Could not load model artifact from %s", self.path)
            return False

    def get_model_artifact(self) -> dict:
        if self._model_artifact is None:
            raise ModelArtifactUnavailable(
                "The model artifact is not available. Check the API logs and artifact path."
            ) from self._load_error
        return self._model_artifact

    def get_explanation_background(self) -> pd.DataFrame:
        """Return the established training partition for local explanations."""
        if self._explanation_background is None:
            dataset = (
                pd.read_csv(PROCESSED_DATA_PATH)
                if PROCESSED_DATA_PATH.is_file()
                else build_processed_dataset()
            )
            split = split_dataset(dataset)
            self._explanation_background = split.X_train.reset_index(drop=True)
        return self._explanation_background
