"""Typed service errors mapped to stable HTTP responses."""


class InvalidPortfolioError(ValueError):
    """The request is valid JSON but cannot represent a valid portfolio."""


class ModelArtifactUnavailable(RuntimeError):
    """No usable trusted model artifact is available to the API service."""


class AnalystModelUnavailable(RuntimeError):
    """No configured local language model is available for analyst answers."""


class AnalystPolicyUnavailable(RuntimeError):
    """Generation is disabled until a small-cohort policy is configured."""


class AnalystProviderFailure(RuntimeError):
    """The local language-model provider failed without a usable answer."""


class AnalystProviderTimeout(TimeoutError):
    """The local generation provider exceeded its configured time budget."""


class InvalidAnalystOutput(RuntimeError):
    """Provider output failed JSON, schema, or evidence-reference validation."""


class AnalystModelUnavailable(RuntimeError):
    """No configured local language model is available for analyst answers."""


class AnalystPolicyUnavailable(RuntimeError):
    """Generation is disabled until a small-cohort policy is configured."""


class AnalystProviderFailure(RuntimeError):
    """The local language-model provider failed without a usable answer."""


class AnalystProviderTimeout(TimeoutError):
    """The local generation provider exceeded its configured time budget."""


class InvalidAnalystOutput(RuntimeError):
    """Provider output failed JSON, schema, or evidence-reference validation."""
