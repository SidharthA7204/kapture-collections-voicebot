from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.exception_handlers import (
    database_error_handler,
    groq_service_error_handler,
    invalid_state_transition_handler,
    unexpected_exception_handler,
    validation_error_handler,
    value_error_handler,
)
from app.core.config import settings
from app.core.logging import configure_logging, logger
from app.db.database import engine
from app.middleware.request_context import (
    RequestContextMiddleware,
)
from app.routes.ai import router as ai_router
from app.routes.calls import router as calls_router
from app.routes.vapi import router as vapi_router
from app.services.groq_service import GroqServiceError
from app.state.state_machine import InvalidStateTransition


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()

    logger.info(
        "application_started",
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.ENVIRONMENT,
    )

    yield

    logger.info("application_shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Production-oriented AI voice collections backend "
        "with authentication, state control, tools and observability."
    ),
    lifespan=lifespan,
)


app.add_exception_handler(
    ValueError,
    value_error_handler,
)

app.add_exception_handler(
    InvalidStateTransition,
    invalid_state_transition_handler,
)

app.add_exception_handler(
    RequestValidationError,
    validation_error_handler,
)

app.add_exception_handler(
    SQLAlchemyError,
    database_error_handler,
)

app.add_exception_handler(
    GroqServiceError,
    groq_service_error_handler,
)

app.add_exception_handler(
    Exception,
    unexpected_exception_handler,
)

app.add_middleware(
    RequestContextMiddleware
)

app.include_router(calls_router)
app.include_router(vapi_router)
app.include_router(ai_router)


@app.get("/health")
async def health_check():
    database_status = "healthy"

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

    except Exception as exc:
        database_status = "unhealthy"

        logger.error(
            "database_health_check_failed",
            error_type=type(exc).__name__,
        )

    overall_status = (
        "healthy"
        if database_status == "healthy"
        else "unhealthy"
    )

    return {
        "status": overall_status,
        "service": "kapture-collections-backend",
        "version": settings.APP_VERSION,
        "database": database_status,
    }

 
@app.get("/ready")
async def readiness_check():
    database_status = "healthy"

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

    except Exception as exc:
        database_status = "unhealthy"

        logger.error(
            "database_readiness_check_failed",
            error_type=type(exc).__name__,
        )

    response = {
        "status": (
            "ready"
            if database_status == "healthy"
            else "not_ready"
        ),
        "service": "kapture-collections-backend",
        "version": settings.APP_VERSION,
        "database": database_status,
    }

    if database_status != "healthy":
        return JSONResponse(
            status_code=503,
            content=response,
        )

    return response

 

