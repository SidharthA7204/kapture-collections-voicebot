from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.api.exception_handlers import (
    database_error_handler,
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
        SQLAlchemyError,
        database_error_handler,
    )

    @app.get("/database-failure")
    async def database_failure_endpoint():
        raise SQLAlchemyError(
            "secret database failure"
        )

    return app


def test_database_error_request_id_end_to_end(
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

    request_id = "database-request-001"

    response = client.get(
        "/database-failure",
        headers={
            "X-Request-ID": request_id,
        },
    )

    assert response.status_code == 503

    assert (
        response.headers["X-Request-ID"]
        == request_id
    )

    assert captured["event"] == (
        "database_error"
    )

    assert captured["kwargs"]["request_id"] == (
        request_id
    )

    assert captured["kwargs"]["error_type"] == (
        "SQLAlchemyError"
    )

    assert "error" not in captured["kwargs"]

    assert b"secret database failure" not in (
        response.content
    )
