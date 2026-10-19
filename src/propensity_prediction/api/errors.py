"""Typed service errors mapped to stable HTTP responses."""


class InvalidPortfolioError(ValueError):
    """The request is valid JSON but cannot represent a valid portfolio."""


class ModelArtifactUnavailable(RuntimeError):
    """No usable trusted model artifact is available to the API service."""
