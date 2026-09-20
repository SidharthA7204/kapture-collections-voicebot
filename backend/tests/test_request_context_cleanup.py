from fastapi import FastAPI
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
        context = (
            structlog.contextvars.get_contextvars()
        )

        return {
            "request_id": context.get(
                "request_id"
            )
        }

    return app


def test_request_context_is_cleared_after_request():
    app = create_test_app()

    client = TestClient(app)

    response = client.get(
        "/test",
        headers={
            "X-Request-ID": "request-one",
        },
    )

    assert response.status_code == 200
    assert response.json()["request_id"] == (
        "request-one"
    )

    context = (
        structlog.contextvars.get_contextvars()
    )

    assert "request_id" not in context


def test_second_request_does_not_reuse_first_request_id():
    app = create_test_app()

    client = TestClient(app)

    first_response = client.get(
        "/test",
        headers={
            "X-Request-ID": "request-one",
        },
    )

    second_response = client.get(
        "/test",
        headers={
            "X-Request-ID": "request-two",
        },
    )

    assert (
        first_response.headers["X-Request-ID"]
        == "request-one"
    )

    assert (
        second_response.headers["X-Request-ID"]
        == "request-two"
    )

    assert (
        first_response.json()["request_id"]
        == "request-one"
    )

    assert (
        second_response.json()["request_id"]
        == "request-two"
    )
