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


def test_request_id_has_reasonable_max_length():
    app = create_test_app()
    client = TestClient(app)

    oversized_request_id = "a" * 500

    response = client.get(
        "/test",
        headers={
            "X-Request-ID": oversized_request_id,
        },
    )

    assert response.status_code == 200

    returned_request_id = response.headers.get(
        "X-Request-ID"
    )

    assert returned_request_id is not None
    assert len(returned_request_id) <= 128


def test_empty_request_id_is_replaced():
    app = create_test_app()
    client = TestClient(app)

    response = client.get(
        "/test",
        headers={
            "X-Request-ID": "",
        },
    )

    assert response.status_code == 200

    returned_request_id = response.headers.get(
        "X-Request-ID"
    )

    assert returned_request_id is not None
    assert len(returned_request_id) > 0
    assert returned_request_id != ""
