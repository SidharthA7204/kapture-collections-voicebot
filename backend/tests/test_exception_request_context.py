from fastapi import FastAPI
from fastapi.testclient import TestClient
import structlog

from app.middleware.request_context import (
    RequestContextMiddleware,
)
from app.api.exception_handlers import (
    unexpected_exception_handler,
)


def create_test_app():
    app = FastAPI()

    app.add_middleware(
        RequestContextMiddleware
    )

    app.add_exception_handler(
        Exception,
        unexpected_exception_handler,
    )

    @app.get("/failure")
    async def failure_endpoint():
        raise RuntimeError(
            "secret failure"
        )

    return app


def test_exception_log_contains_request_id(
    monkeypatch,
):
    captured = {}

    def fake_error(event, **kwargs):
        captured["event"] = event
        captured["kwargs"] = kwargs

    monkeypatch.setattr(
        "app.api.exception_handlers.logger.error",
        fake_error,
    )

    app = create_test_app()

    client = TestClient(
        app,
        raise_server_exceptions=False,
    )

    request_id = "exception-request-001"

    response = client.get(
        "/failure",
        headers={
            "X-Request-ID": request_id,
        },
    )

    assert response.status_code == 500

    assert captured["event"] == (
        "unexpected_exception"
    )

    context = (
        structlog.contextvars.get_contextvars()
    )

    assert (
        captured["kwargs"].get("request_id")
        == request_id
        or context.get("request_id")
        == request_id
    )
