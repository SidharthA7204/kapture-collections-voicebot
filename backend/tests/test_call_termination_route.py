from fastapi.testclient import TestClient

from app.db.database import get_db
from app.db.repositories.call_log_repository import (
    CallLogRepository,
)
from app.main import app


def test_repeated_end_call_endpoint_is_idempotent(
    db_session,
):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        call_id = "api_termination_001"

        response = client.post(
            "/calls/start",
            json={
                "call_id": call_id,
                "customer_id": None,
            },
        )

        assert response.status_code == 200

        # Move through valid states before ending.
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

        # First termination.
        response = client.post(
            f"/calls/{call_id}/end"
        )

        assert response.status_code == 200

        first_data = response.json()

        assert first_data["call_id"] == call_id
        assert first_data["current_state"] == "END"

        call_log = (
            CallLogRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert call_log is not None
        assert call_log.ended_at is not None

        first_ended_at = call_log.ended_at

        # Second termination.
        response = client.post(
            f"/calls/{call_id}/end"
        )

        assert response.status_code == 200

        second_data = response.json()

        assert second_data["call_id"] == call_id
        assert second_data["current_state"] == "END"

        call_log = (
            CallLogRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert call_log.ended_at == first_ended_at

    finally:
        app.dependency_overrides.clear()