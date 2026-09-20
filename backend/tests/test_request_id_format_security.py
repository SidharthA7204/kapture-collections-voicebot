from fastapi import FastAPI
from fastapi.testclient import TestClient

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


def test_request_id_with_unsafe_characters_is_replaced():
    app = create_test_app()
    client = TestClient(app)

    unsafe_request_id = (
        "request\r\n"
        "X-Injected-Header: malicious"
    )

    response = client.get(
        "/test",
        headers={
            "X-Request-ID": unsafe_request_id,
        },
    )

    assert response.status_code == 200

    returned_request_id = response.headers.get(
        "X-Request-ID"
    )

    assert returned_request_id is not None
    assert "\r" not in returned_request_id
    assert "\n" not in returned_request_id
    assert returned_request_id != (
        unsafe_request_id
    )


def test_normal_request_id_is_preserved():
    app = create_test_app()
    client = TestClient(app)

    request_id = "request-123_ABC"

    response = client.get(
        "/test",
        headers={
            "X-Request-ID": request_id,
        },
    )

    assert response.status_code == 200

    assert response.headers["X-Request-ID"] == (
        request_id
    )
