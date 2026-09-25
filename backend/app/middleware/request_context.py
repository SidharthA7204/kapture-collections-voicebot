import re
import time
import uuid

import structlog
from starlette.middleware.base import (
    BaseHTTPMiddleware,
)
from starlette.requests import Request
from starlette.responses import Response

from app.core.metrics import (
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_IN_PROGRESS,
    HTTP_REQUESTS_TOTAL,
)


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

        method = request.method
        path = request.url.path

        HTTP_REQUESTS_IN_PROGRESS.inc()

        logger.info(
            "request_started",
            method=method,
            path=path,
        )

        try:
            response = await call_next(request)

            duration_seconds = (
                time.perf_counter() - start_time
            )

            duration_ms = round(
                duration_seconds * 1000,
                2,
            )

            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                path=path,
                status=str(response.status_code),
            ).inc()

            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method,
                path=path,
            ).observe(duration_seconds)

            logger.info(
                "request_completed",
                method=method,
                path=path,
                status_code=response.status_code,
                duration_ms=duration_ms,
            )

            response.headers[
                "X-Request-ID"
            ] = request_id

            return response

        except Exception as exc:
            duration_seconds = (
                time.perf_counter() - start_time
            )

            duration_ms = round(
                duration_seconds * 1000,
                2,
            )

            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                path=path,
                status="500",
            ).inc()

            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method,
                path=path,
            ).observe(duration_seconds)

            logger.error(
                "request_failed",
                method=method,
                path=path,
                duration_ms=duration_ms,
                error_type=type(exc).__name__,
            )

            raise

        finally:
            HTTP_REQUESTS_IN_PROGRESS.dec()
            structlog.contextvars.clear_contextvars()
