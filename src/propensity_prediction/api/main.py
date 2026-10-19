"""FastAPI application factory and stable error response handlers."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from propensity_prediction.api.errors import (
    InvalidPortfolioError,
    ModelArtifactUnavailable,
)
from propensity_prediction.api.repository import ModelArtifactRepository
from propensity_prediction.api.routes import router
from propensity_prediction.api.service import ReviewQueueService
from propensity_prediction.dashboard import STATIC_ASSETS_DIRECTORY
from propensity_prediction.models.artifact import DEFAULT_MODEL_ARTIFACT_PATH


logger = logging.getLogger(__name__)


def _error_response(code: str, message: str, details: list[str]) -> dict:
    return {"error": {"code": code, "message": message, "details": details}}


def create_app(
    artifact_path: str | Path = DEFAULT_MODEL_ARTIFACT_PATH,
) -> FastAPI:
    repository = ModelArtifactRepository(artifact_path)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        repository.load()
        app.state.model_repository = repository
        app.state.review_queue_service = ReviewQueueService(repository)
        yield

    app = FastAPI(
        title="Credit Risk Review Prioritization API",
        version="1.0.0",
        description=(
            "Scores supplied customer predictors and constructs a deterministic "
            "capacity-limited analyst review queue. It does not recommend or "
            "execute customer interventions."
        ),
        lifespan=lifespan,
    )
    app.include_router(router)
    app.mount(
        "/",
        StaticFiles(directory=STATIC_ASSETS_DIRECTORY, html=True),
        name="dashboard",
    )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        details = [
            ".".join(str(part) for part in error["loc"] if part != "body")
            + f": {error['msg']}"
            for error in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content=_error_response(
                "INVALID_REQUEST_SCHEMA",
                "The request does not match the review-queue contract.",
                details,
            ),
        )

    @app.exception_handler(InvalidPortfolioError)
    async def invalid_portfolio_handler(
        request: Request,
        exc: InvalidPortfolioError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content=_error_response(
                "INVALID_PORTFOLIO",
                str(exc),
                [],
            ),
        )

    @app.exception_handler(ModelArtifactUnavailable)
    async def model_unavailable_handler(
        request: Request,
        exc: ModelArtifactUnavailable,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content=_error_response(
                "MODEL_UNAVAILABLE",
                str(exc),
                [],
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        code = "MODEL_UNAVAILABLE" if exc.status_code == 503 else "HTTP_ERROR"
        message = str(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_response(code, message, []),
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.error(
            "Unhandled API error",
            exc_info=(type(exc), exc, exc.__traceback__),
        )
        return JSONResponse(
            status_code=500,
            content=_error_response(
                "INTERNAL_SERVER_ERROR",
                "The API could not complete this request.",
                [],
            ),
        )

    return app


app = create_app()
