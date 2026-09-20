import asyncio

from fastapi import Request
from sqlalchemy.exc import SQLAlchemyError

from app.api.exception_handlers import (
    database_error_handler,
    invalid_state_transition_handler,
    unexpected_exception_handler,
    value_error_handler,
)
from app.state.state_machine import InvalidStateTransition


def create_request(
    method="GET",
    path="/test",
):
    return Request(
        scope={
            "type": "http",
            "method": method,
            "path": path,
            "headers": [],
            "query_string": b"",
            "server": ("testserver", 80),
            "client": ("testclient", 50000),
        }
    )


def test_value_error_contract():
    response = asyncio.run(
        value_error_handler(
            create_request(),
            ValueError("not found"),
        )
    )

    assert response.status_code == 404
    assert response.body == (
        b'{"error":"NOT_FOUND",'
        b'"detail":"not found"}'
    )


def test_invalid_state_transition_contract():
    response = asyncio.run(
        invalid_state_transition_handler(
            create_request(),
            InvalidStateTransition(
                "invalid transition"
            ),
        )
    )

    assert response.status_code == 409
    assert response.body == (
        b'{"error":"INVALID_STATE_TRANSITION",'
        b'"detail":"invalid transition"}'
    )


def test_database_error_contract():
    response = asyncio.run(
        database_error_handler(
            create_request(),
            SQLAlchemyError(
                "secret database failure"
            ),
        )
    )

    assert response.status_code == 503
    assert response.body == (
        b'{"error":"DATABASE_ERROR",'
        b'"detail":"Database operation failed."}'
    )


def test_unexpected_exception_contract():
    response = asyncio.run(
        unexpected_exception_handler(
            create_request(),
            RuntimeError(
                "secret internal failure"
            ),
        )
    )

    assert response.status_code == 500
    assert response.body == (
        b'{"error":"INTERNAL_SERVER_ERROR",'
        b'"detail":"An unexpected error occurred."}'
    )