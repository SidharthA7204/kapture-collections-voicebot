from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
import structlog

from app.middleware.request_context import (
    RequestContextMiddleware,
)


def create_test_app():
    app = FastAPI()

    app.add_middleware(
        RequestContextMiddleware
    )

    @app.get("/test")
    async def test_endpoint():
        return {"status": "ok"}

    return app


def test_request_id_is_generated():
    app = create_test_app()
    client = TestClient(app)

    response = client.get("/test")

    assert response.status_code == 200

    request_id = response.headers.get(
        "X-Request-ID"
    )

    assert request_id is not None
    assert len(request_id) > 0


def test_existing_request_id_is_preserved():
    app = create_test_app()
    client = TestClient(app)

    request_id = "test-request-123"

    response = client.get(
        "/test",
        headers={
            "X-Request-ID": request_id,
        },
    )

    assert response.status_code == 200

    assert (
        response.headers["X-Request-ID"]
        == request_id
    )


def test_request_id_is_available_on_request_state():
    app = FastAPI()

    app.add_middleware(
        RequestContextMiddleware
    )

    @app.get("/test")
    async def test_endpoint(
        request: Request,
    ):
        return {
            "request_id": request.state.request_id
        }

    client = TestClient(app)

    response = client.get("/test")

    assert response.status_code == 200

    assert response.json()["request_id"] == (
        response.headers["X-Request-ID"]
    )


def test_request_id_is_bound_to_structlog_context():
    app = FastAPI()

    app.add_middleware(
        RequestContextMiddleware
    )

    @app.get("/test")
    async def test_endpoint():
        context = (
            structlog.contextvars.get_contextvars()
        )

        return {
            "request_id": context.get(
                "request_id"
            )
        }

    client = TestClient(app)

    response = client.get("/test")

    assert response.status_code == 200

    request_id = response.headers.get(
        "X-Request-ID"
    )

    assert request_id is not None

    assert response.json()["request_id"] == (
        request_id
    )

def test_request_failed_log_does_not_contain_exception_details(
    monkeypatch,
):
    app = FastAPI()

    app.add_middleware(
        RequestContextMiddleware
    )

    sensitive_message = (
        "database password=super-secret "
        "phone=9876543210"
    )

    @app.get("/test")
    async def failing_endpoint():
        raise RuntimeError(sensitive_message)

    captured = {}

    def fake_error(event, **kwargs):
        captured["event"] = event
        captured["kwargs"] = kwargs

    monkeypatch.setattr(
        "app.middleware.request_context.logger.error",
        fake_error,
    )

    client = TestClient(
        app,
        raise_server_exceptions=False,
    )

    response = client.get("/test")

    assert response.status_code == 500

    assert captured["event"] == "request_failed"

    assert captured["kwargs"]["error_type"] == (
        "RuntimeError"
    )

    logged_values = str(
        captured["kwargs"]
    )

    assert sensitive_message not in logged_values
    assert "super-secret" not in logged_values
    assert "9876543210" not in logged_values
    assert "error" not in captured["kwargs"]
