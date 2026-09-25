from fastapi import Request

from app.api.exception_handlers import (
    unexpected_exception_handler,
    value_error_handler,
)


def create_request():
    return Request(
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


def test_client_error_uses_warning_log(
    monkeypatch,
):
    captured = {}

    def fake_warning(event, **kwargs):
        captured["event"] = event
        captured["kwargs"] = kwargs

    monkeypatch.setattr(
        "app.api.exception_handlers.logger.warning",
        fake_warning,
    )

    import asyncio

    asyncio.run(
        value_error_handler(
            create_request(),
            ValueError("not found"),
        )
    )

    assert captured["event"] == "value_error"
    assert captured["kwargs"]["error_type"] == "ValueError"


def test_unexpected_error_uses_critical_severity(
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

    import asyncio

    asyncio.run(
        unexpected_exception_handler(
            create_request(),
            RuntimeError("secret failure"),
        )
    )

    assert captured["event"] == "unexpected_exception"
    assert captured["kwargs"]["severity"] == "critical"
    assert captured["kwargs"]["error_type"] == "RuntimeError"
    assert "error" not in captured["kwargs"]
