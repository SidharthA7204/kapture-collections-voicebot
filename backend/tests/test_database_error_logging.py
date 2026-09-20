from fastapi import Request
from sqlalchemy.exc import SQLAlchemyError

from app.api.exception_handlers import (
    database_error_handler,
)


def test_database_error_is_logged(
    monkeypatch,
):
    request = Request(
        scope={
            "type": "http",
            "method": "POST",
            "path": "/calls/test/end",
            "headers": [],
            "query_string": b"",
            "server": ("testserver", 80),
            "client": ("testclient", 50000),
        }
    )

    captured = {}

    def fake_error(event, **kwargs):
        captured["event"] = event
        captured["kwargs"] = kwargs

    monkeypatch.setattr(
        "app.api.exception_handlers.logger.error",
        fake_error,
    )

    response = __import__(
        "asyncio"
    ).run(
        database_error_handler(
            request,
            SQLAlchemyError(
                "secret database failure"
            ),
        )
    )

    assert response.status_code == 503

    assert captured["event"] == (
        "database_error"
    )

    assert captured["kwargs"]["error_type"] == (
        "SQLAlchemyError"
    )

    assert captured["kwargs"]["method"] == (
        "POST"
    )

    assert captured["kwargs"]["path"] == (
        "/calls/test/end"
    )

    assert "error" not in captured["kwargs"]

    assert b"secret database failure" not in (
        response.body
    )
