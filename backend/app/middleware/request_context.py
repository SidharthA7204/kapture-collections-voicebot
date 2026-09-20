import re
import time
import uuid

import structlog
from starlette.middleware.base import (
    BaseHTTPMiddleware,
)
from starlette.requests import Request
from starlette.responses import Response


MAX_REQUEST_ID_LENGTH = 128

REQUEST_ID_PATTERN = re.compile(
    r"^[A-Za-z0-9_-]+$"
)

logger = structlog.get_logger()


class RequestContextMiddleware(
    BaseHTTPMiddleware
):
    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:
        incoming_request_id = (
            request.headers.get("X-Request-ID")
        )

        if (
            incoming_request_id
            and len(incoming_request_id)
            <= MAX_REQUEST_ID_LENGTH
            and REQUEST_ID_PATTERN.fullmatch(
                incoming_request_id
            )
        ):
            request_id = incoming_request_id
        else:
            request_id = str(uuid.uuid4())

        structlog.contextvars.clear_contextvars()

        structlog.contextvars.bind_contextvars(
            request_id=request_id,
        )

        request.state.request_id = request_id

        start_time = time.perf_counter()

        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
        )

        try:
            response = await call_next(request)

            duration_ms = round(
                (time.perf_counter() - start_time) * 1000,
                2,
            )

            logger.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

            response.headers[
                "X-Request-ID"
            ] = request_id

            return response

        except Exception as exc:
            duration_ms = round(
                (time.perf_counter() - start_time) * 1000,
                2,
            )

            logger.error(
                "request_failed",
                method=request.method,
                path=request.url.path,
                duration_ms=duration_ms,
                error_type=type(exc).__name__,
            )

            raise

        finally:
            structlog.contextvars.clear_contextvars()
