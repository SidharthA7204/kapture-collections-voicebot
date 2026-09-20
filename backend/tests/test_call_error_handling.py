from fastapi.testclient import TestClient

from app.db.database import get_db
from app.main import app


def test_transition_unknown_call_returns_404(
    db_session,
):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.post(
            "/calls/unknown_call_001/transition",
            json={
                "next_state": "INTRODUCTION",
            },
        )

        assert response.status_code == 404

        data = response.json()

        assert "Session not found" in data["detail"]

    finally:
        app.dependency_overrides.clear()


def test_invalid_transition_returns_409(
    db_session,
):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        call_id = "error_api_001"

        response = client.post(
            "/calls/start",
            json={
                "call_id": call_id,
                "customer_id": None,
            },
        )

        assert response.status_code == 200

        response = client.post(
            f"/calls/{call_id}/transition",
            json={
                "next_state": "DISPOSITION",
            },
        )

        assert response.status_code == 409

        data = response.json()

        assert "Invalid transition" in data["detail"]

    finally:
        app.dependency_overrides.clear()