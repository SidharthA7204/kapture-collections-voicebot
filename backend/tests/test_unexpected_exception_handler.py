import asyncio

from fastapi import Request
from fastapi.responses import JSONResponse

from app.api.exception_handlers import (
    unexpected_exception_handler,
)


def test_unexpected_exception_handler_hides_internal_error():
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

    response = asyncio.run(
        unexpected_exception_handler(
            request,
            RuntimeError(
                "SECRET INTERNAL DATABASE FAILURE"
            ),
        )
    )

    assert isinstance(response, JSONResponse)
    assert response.status_code == 500

    assert response.body == (
        b'{"error":"INTERNAL_SERVER_ERROR",'
        b'"detail":"An unexpected error occurred."}'
    )

    assert (
        b"SECRET INTERNAL DATABASE FAILURE"
        not in response.body
    )