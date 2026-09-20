from fastapi.testclient import TestClient

from app.main import app


def test_validation_error_has_standard_error_code():
    client = TestClient(app)

    response = client.post(
        "/calls/start",
        json={},
    )

    assert response.status_code == 422

    data = response.json()

    assert data["error"] == "VALIDATION_ERROR"
    assert isinstance(data["detail"], list)


def test_invalid_state_validation_has_standard_error_code():
    client = TestClient(app)

    response = client.post(
        "/calls/validation_error_001/transition",
        json={
            "next_state": "NOT_A_REAL_STATE",
        },
    )

    assert response.status_code == 422

    data = response.json()

    assert data["error"] == "VALIDATION_ERROR"
    assert isinstance(data["detail"], list)