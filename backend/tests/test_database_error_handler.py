from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.exception_handlers import database_error_handler


def test_database_error_handler():
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

    response = __import__(
        "asyncio"
    ).run(
        database_error_handler(
            request,
            SQLAlchemyError("secret database details"),
        )
    )

    assert isinstance(response, JSONResponse)
    assert response.status_code == 503

    assert response.body == (
        b'{"error":"DATABASE_ERROR",'
        b'"detail":"Database operation failed."}'
    )

    assert b"secret database details" not in response.body