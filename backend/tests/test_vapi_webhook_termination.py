from fastapi.testclient import TestClient

from app.db.database import get_db
from app.db.repositories.call_log_repository import (
    CallLogRepository,
)
from app.db.repositories.session_repository import (
    SessionRepository,
)
from app.main import app


def valid_headers():
    return {
        "Authorization": "Bearer local-development-secret",
    }


def ended_payload(call_id: str):
    return {
        "message": {
            "type": "status-update",
            "call": {
                "id": call_id,
                "status": "ended",
            },
        }
    }


def test_vapi_ended_status_ends_call(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        call_id = "vapi-ended-001"

        response = client.post(
            "/vapi/webhook",
            json=ended_payload(call_id),
            headers=valid_headers(),
        )

        assert response.status_code == 200

        session = (
            SessionRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert session is not None
        assert session.current_state == "END"

        call_log = (
            CallLogRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert call_log is not None
        assert call_log.ended_at is not None

    finally:
        app.dependency_overrides.clear()


def test_vapi_repeated_ended_status_is_idempotent(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        call_id = "vapi-ended-idempotent-001"

        first = client.post(
            "/vapi/webhook",
            json=ended_payload(call_id),
            headers=valid_headers(),
        )

        assert first.status_code == 200

        call_log = (
            CallLogRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert call_log is not None
        assert call_log.ended_at is not None

        first_ended_at = call_log.ended_at

        second = client.post(
            "/vapi/webhook",
            json=ended_payload(call_id),
            headers=valid_headers(),
        )

        assert second.status_code == 200

        call_log = (
            CallLogRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert call_log is not None
        assert call_log.ended_at == first_ended_at

    finally:
        app.dependency_overrides.clear()
