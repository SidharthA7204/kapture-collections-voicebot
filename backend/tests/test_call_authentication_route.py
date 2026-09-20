from fastapi.testclient import TestClient

from app.db.database import get_db
from app.main import app


def test_authenticate_call_endpoint(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        call_id = "auth_api_001"

        start_response = client.post(
            "/calls/start",
            json={
                "call_id": call_id,
                "customer_id": None,
            },
        )

        assert start_response.status_code == 200

        for state in (
            "INTRODUCTION",
            "CHECK_PERSON",
            "AUTHENTICATION",
        ):
            response = client.post(
                f"/calls/{call_id}/transition",
                json={
                    "next_state": state,
                },
            )

            assert response.status_code == 200
            assert response.json()["current_state"] == state

        authentication_response = client.post(
            f"/calls/{call_id}/authenticate"
        )

        assert authentication_response.status_code == 200

        data = authentication_response.json()

        assert data["call_id"] == call_id
        assert data["authenticated"] is True
        assert data["current_state"] == "DISCLOSE_OVERDUE"

    finally:
        app.dependency_overrides.clear()