from fastapi.testclient import TestClient

from app.db.database import get_db
from app.main import app


def test_payment_action_endpoint(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        call_id = "action_api_001"

        response = client.post(
            "/calls/start",
            json={
                "call_id": call_id,
                "customer_id": None,
            },
        )

        assert response.status_code == 200

        for state in (
            "INTRODUCTION",
            "CHECK_PERSON",
            "AUTHENTICATION",
            "DISCLOSE_OVERDUE",
            "INTENT_HANDLING",
        ):
            response = client.post(
                f"/calls/{call_id}/transition",
                json={
                    "next_state": state,
                },
            )

            assert response.status_code == 200
            assert response.json()["current_state"] == state

        response = client.post(
            f"/calls/{call_id}/action",
            json={
                "action": "PAYMENT",
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["call_id"] == call_id
        assert data["disposition"] == "PAYMENT_INITIATED"

    finally:
        app.dependency_overrides.clear()