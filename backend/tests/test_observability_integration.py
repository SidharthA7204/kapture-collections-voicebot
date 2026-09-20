from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.exception_handlers import (
    unexpected_exception_handler,
)
from app.middleware.request_context import (
    RequestContextMiddleware,
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


def test_exception_request_id_end_to_end(
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

    request_id = "integration-request-001"

    response = client.get(
        "/failure",
        headers={
            "X-Request-ID": request_id,
        },
    )

    assert response.status_code == 500

    assert (
        response.headers["X-Request-ID"]
        == request_id
    )

    assert captured["event"] == (
        "unexpected_exception"
    )

    assert captured["kwargs"]["request_id"] == (
        request_id
    )

    assert captured["kwargs"]["error_type"] == (
        "RuntimeError"
    )

    assert "error" not in captured["kwargs"]

    assert b"secret failure" not in (
        response.content
    )
