from datetime import date

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routes.calls import router


def create_test_app():
    app = FastAPI()
    app.include_router(router)
    return app


def test_verify_customer_rejects_invalid_phone():
    app = create_test_app()
    client = TestClient(app)

    response = client.post(
        "/calls/security-test-001/verify-customer",
        json={
            "phone": "not-a-phone",
            "dob": "1995-05-15",
        },
    )

    assert response.status_code == 422


def test_verify_customer_rejects_invalid_dob():
    app = create_test_app()
    client = TestClient(app)

    response = client.post(
        "/calls/security-test-002/verify-customer",
        json={
            "phone": "9876543210",
            "dob": "2099-01-01",
        },
    )

    assert response.status_code == 422


def test_verify_customer_rejects_missing_phone():
    app = create_test_app()
    client = TestClient(app)

    response = client.post(
        "/calls/security-test-003/verify-customer",
        json={
            "dob": "1995-05-15",
        },
    )

    assert response.status_code == 422
