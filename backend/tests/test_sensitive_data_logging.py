import asyncio

from fastapi import Request

from app.api.exception_handlers import (
    unexpected_exception_handler,
)


def test_unexpected_exception_log_does_not_contain_sensitive_data(
    monkeypatch,
):
    request = Request(
        scope={
            "type": "http",
            "method": "POST",
            "path": "/calls/test/verify-customer",
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

    sensitive_phone = "9876543210"
    sensitive_dob = "1995-05-15"

    asyncio.run(
        unexpected_exception_handler(
            request,
            RuntimeError(
                f"verification failed for phone "
                f"{sensitive_phone} and dob "
                f"{sensitive_dob}"
            ),
        )
    )

    logged_values = str(
        captured["kwargs"]
    )

    assert sensitive_phone not in logged_values
    assert sensitive_dob not in logged_values
