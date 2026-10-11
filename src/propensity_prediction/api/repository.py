"""File-backed repository for the fitted model artifact."""

from __future__ import annotations

import logging
from pathlib import Path

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
