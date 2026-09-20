from fastapi.testclient import TestClient

from app.db.database import get_db
from app.main import app
from app.db.repositories.call_log_repository import (
    CallLogRepository,
)


def test_full_call_lifecycle(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        call_id = "full_lifecycle_001"

        # 1. Start call
        response = client.post(
            "/calls/start",
            json={
                "call_id": call_id,
                "customer_id": None,
            },
        )

        assert response.status_code == 200

        data = response.json()

        assert data["call_id"] == call_id
        assert data["current_state"] == "CALL_CONNECTED"
        assert data["authenticated"] is False

        # 2. INTRODUCTION
        response = client.post(
            f"/calls/{call_id}/transition",
            json={
                "next_state": "INTRODUCTION",
            },
        )

        assert response.status_code == 200
        assert response.json()["current_state"] == "INTRODUCTION"

        # 3. CHECK_PERSON
        response = client.post(
            f"/calls/{call_id}/transition",
            json={
                "next_state": "CHECK_PERSON",
            },
        )

        assert response.status_code == 200
        assert response.json()["current_state"] == "CHECK_PERSON"

        # 4. AUTHENTICATION
        response = client.post(
            f"/calls/{call_id}/transition",
            json={
                "next_state": "AUTHENTICATION",
            },
        )

        assert response.status_code == 200
        assert response.json()["current_state"] == "AUTHENTICATION"

        # 5. Authenticate
        response = client.post(
            f"/calls/{call_id}/authenticate"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["call_id"] == call_id
        assert data["authenticated"] is True
        assert data["current_state"] == "DISCLOSE_OVERDUE"

        # 6. INTENT_HANDLING
        response = client.post(
            f"/calls/{call_id}/transition",
            json={
                "next_state": "INTENT_HANDLING",
            },
        )

        assert response.status_code == 200
        assert response.json()["current_state"] == "INTENT_HANDLING"

        # 7. PAYMENT action
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

        # 8. END
        response = client.post(
            f"/calls/{call_id}/end"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["call_id"] == call_id
        assert data["current_state"] == "END"

        # 9. Verify call log
        call_log = (
            CallLogRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert call_log is not None
        assert call_log.disposition == "PAYMENT_INITIATED"
        assert call_log.ended_at is not None

    finally:
        app.dependency_overrides.clear()