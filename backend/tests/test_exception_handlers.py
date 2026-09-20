from fastapi.testclient import TestClient

from app.db.database import get_db
from app.main import app


def test_invalid_state_transition_returns_structured_error(
    db_session,
):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        call_id = "exception_test_001"

        response = client.post(
            "/calls/start",
            json={
                "call_id": call_id,
                "customer_id": None,
            },
        )

        assert response.status_code == 200

        # CALL_CONNECTED -> END is invalid.
        response = client.post(
            f"/calls/{call_id}/transition",
            json={
                "next_state": "END",
            },
        )

        assert response.status_code == 409

        data = response.json()

        assert data["error"] == (
            "INVALID_STATE_TRANSITION"
        )
        assert "Invalid transition" in data["detail"]

    finally:
        app.dependency_overrides.clear()


def test_session_not_found_returns_structured_error(
    db_session,
):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        response = client.post(
            "/calls/nonexistent_call/end"
        )

        assert response.status_code == 404

        data = response.json()

        assert data["error"] == "NOT_FOUND"
        assert "Session not found" in data["detail"]

    finally:
        app.dependency_overrides.clear()