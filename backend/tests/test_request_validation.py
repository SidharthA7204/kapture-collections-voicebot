from fastapi.testclient import TestClient

from app.main import app


def test_start_call_requires_call_id():
    client = TestClient(app)

    response = client.post(
        "/calls/start",
        json={
            "customer_id": None,
        },
    )

    assert response.status_code == 422


def test_start_call_rejects_invalid_customer_id():
    client = TestClient(app)

    response = client.post(
        "/calls/start",
        json={
            "call_id": "validation_001",
            "customer_id": "not-an-integer",
        },
    )

    assert response.status_code == 422


def test_transition_requires_next_state():
    client = TestClient(app)

    response = client.post(
        "/calls/validation_002/transition",
        json={},
    )

    assert response.status_code == 422


def test_transition_rejects_invalid_state():
    client = TestClient(app)

    response = client.post(
        "/calls/validation_003/transition",
        json={
            "next_state": "INVALID_STATE",
        },
    )

    assert response.status_code == 422


def test_customer_verification_requires_phone():
    client = TestClient(app)

    response = client.post(
        "/calls/validation_004/verify-customer",
        json={
            "dob": "1995-05-15",
        },
    )

    assert response.status_code == 422


def test_customer_verification_requires_dob():
    client = TestClient(app)

    response = client.post(
        "/calls/validation_005/verify-customer",
        json={
            "phone": "9876543210",
        },
    )

    assert response.status_code == 422


def test_customer_verification_rejects_invalid_dob():
    client = TestClient(app)

    response = client.post(
        "/calls/validation_006/verify-customer",
        json={
            "phone": "9876543210",
            "dob": "not-a-date",
        },
    )

    assert response.status_code == 422