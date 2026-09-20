from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db.database import get_db
from app.db.repositories.call_log_repository import (
    CallLogRepository,
)
from app.db.repositories.session_repository import (
    SessionRepository,
)
from app.main import app


def test_start_call_is_idempotent_for_duplicate_call_id():
    client = TestClient(app)

    payload = {
        "call_id": "duplicate-start-001",
        "customer_id": None,
    }

    first = client.post(
        "/calls/start",
        json=payload,
    )

    second = client.post(
        "/calls/start",
        json=payload,
    )

    assert first.status_code == 200
    assert second.status_code == 200

    assert first.json()["call_id"] == (
        "duplicate-start-001"
    )

    assert second.json()["call_id"] == (
        "duplicate-start-001"
    )


def test_start_call_does_not_create_duplicate_records(
    db_session,
):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        client = TestClient(app)

        call_id = "duplicate-record-check-001"

        payload = {
            "call_id": call_id,
            "customer_id": None,
        }

        first = client.post(
            "/calls/start",
            json=payload,
        )

        second = client.post(
            "/calls/start",
            json=payload,
        )

        assert first.status_code == 200
        assert second.status_code == 200

        session = (
            SessionRepository(db_session)
            .get_by_call_id(call_id)
        )

        call_log = (
            CallLogRepository(db_session)
            .get_by_call_id(call_id)
        )

        assert session is not None
        assert call_log is not None

        session_count = db_session.execute(
            text(
                "SELECT COUNT(*) FROM sessions "
                "WHERE call_id = :call_id"
            ),
            {"call_id": call_id},
        ).scalar_one()

        call_log_count = db_session.execute(
            text(
                "SELECT COUNT(*) FROM call_logs "
                "WHERE call_id = :call_id"
            ),
            {"call_id": call_id},
        ).scalar_one()

        assert session_count == 1
        assert call_log_count == 1

    finally:
        app.dependency_overrides.clear()
