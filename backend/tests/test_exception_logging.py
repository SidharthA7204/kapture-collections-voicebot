import asyncio

from fastapi import Request

from app.api.exception_handlers import (
    unexpected_exception_handler,
)


def test_unexpected_exception_is_logged(
    monkeypatch,
):
    request = Request(
        scope={
            "type": "http",
            "method": "GET",
            "path": "/test",
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

    asyncio.run(
        unexpected_exception_handler(
            request,
            RuntimeError("secret failure"),
        )
    )

    assert captured["event"] == (
        "unexpected_exception"
    )

    assert captured["kwargs"]["error_type"] == (
        "RuntimeError"
    )

    assert captured["kwargs"]["method"] == "GET"

    assert captured["kwargs"]["path"] == (
        "/test"
    )

    assert "error" not in captured["kwargs"]
