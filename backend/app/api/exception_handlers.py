from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.state.state_machine import InvalidStateTransition
from app.core.error_metrics import (
    AI_SERVICE_ERRORS_TOTAL,
    APPLICATION_ERRORS_TOTAL,
    DATABASE_ERRORS_TOTAL,
    UNEXPECTED_ERRORS_TOTAL,
    VALIDATION_ERRORS_TOTAL,
)
from app.core.logging import logger
from app.services.groq_service import GroqServiceError


def get_request_id(request: Request) -> str | None:
    return getattr(
        request.state,
        "request_id",
        None,
    )


def error_response(
    request: Request,
    status_code: int,
    error: str,
    detail,
):
    request_id = get_request_id(request)

    response = JSONResponse(
        status_code=status_code,
        content={
            "error": error,
            "detail": detail,
        },
    )

    if request_id is not None:
        response.headers["X-Request-ID"] = request_id

    return response


async def value_error_handler(
    request: Request,
    exc: ValueError,
):
    APPLICATION_ERRORS_TOTAL.labels(
        error_type="value_error"
    ).inc()

    logger.warning(
        "value_error",
        error_type=type(exc).__name__,
        method=request.method,
        path=request.url.path,
        request_id=get_request_id(request),
    )

    return error_response(
        request=request,
        status_code=404,
        error="NOT_FOUND",
        detail=str(exc),
    )


async def invalid_state_transition_handler(
    request: Request,
    exc: InvalidStateTransition,
):
    APPLICATION_ERRORS_TOTAL.labels(
        error_type="invalid_state_transition"
    ).inc()

    logger.warning(
        "invalid_state_transition",
        error_type=type(exc).__name__,
        method=request.method,
        path=request.url.path,
        request_id=get_request_id(request),
    )

    return error_response(
        request=request,
        status_code=409,
        error="INVALID_STATE_TRANSITION",
        detail=str(exc),
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
):
    APPLICATION_ERRORS_TOTAL.labels(
        error_type="validation_error"
    ).inc()

    VALIDATION_ERRORS_TOTAL.inc()

    logger.warning(
        "validation_error",
        error_type=type(exc).__name__,
        method=request.method,
        path=request.url.path,
        request_id=get_request_id(request),
    )

    return error_response(
        request=request,
        status_code=422,
        error="VALIDATION_ERROR",
        detail=exc.errors(),
    )


async def database_error_handler(
    request: Request,
    exc: SQLAlchemyError,
):
    request_id = get_request_id(request)

    APPLICATION_ERRORS_TOTAL.labels(
        error_type="database_error"
    ).inc()

    DATABASE_ERRORS_TOTAL.inc()

    logger.error(
        "database_error",
        error_type=type(exc).__name__,
        method=request.method,
        path=request.url.path,
        request_id=request_id,
    )

    return error_response(
        request=request,
        status_code=503,
        error="DATABASE_ERROR",
        detail="Database operation failed.",
    )


async def groq_service_error_handler(
    request: Request,
    exc: GroqServiceError,
):
    request_id = get_request_id(request)

    APPLICATION_ERRORS_TOTAL.labels(
        error_type="ai_service_error"
    ).inc()

    AI_SERVICE_ERRORS_TOTAL.inc()

    logger.error(
        "ai_service_error",
        error_type=type(exc).__name__,
        method=request.method,
        path=request.url.path,
        request_id=request_id,
    )

    return error_response(
        request=request,
        status_code=503,
        error="AI_SERVICE_ERROR",
        detail="AI service is temporarily unavailable.",
    )


async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
):
    request_id = get_request_id(request)

    APPLICATION_ERRORS_TOTAL.labels(
        error_type="unexpected_exception"
    ).inc()

    UNEXPECTED_ERRORS_TOTAL.inc()

    logger.error(
        "unexpected_exception",
        severity="critical",
        error_type=type(exc).__name__,
        method=request.method,
        path=request.url.path,
        request_id=request_id,
    )

    return error_response(
        request=request,
        status_code=500,
        error="INTERNAL_SERVER_ERROR",
        detail="An unexpected error occurred.",
    )

