from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app
from app.db.database import get_db


def test_get_call_events_returns_complete_event_contract(
    db_session,
):
    from app.db.repositories.call_log_repository import (
        CallLogRepository,
    )
    from app.db.repositories.call_event_repository import (
        CallEventRepository,
    )
    from app.models.call_log import CallLog
    from app.services.call_event_service import (
        CallEventService,
    )

    call_id = "event_route_contract_001"

    CallLogRepository(db_session).create(
        CallLog(
            call_id=call_id,
            customer_id=None,
            started_at=datetime.utcnow(),
        )
    )

    service = CallEventService(
        CallEventRepository(db_session)
    )

    state_event = service.record_state_change(
        call_id=call_id,
        from_state="CALL_CONNECTED",
        to_state="INTRODUCTION",
    )

    auth_event = service.record_authentication(
        call_id=call_id,
    )

    app.dependency_overrides[get_db] = (
        lambda: db_session
    )

    try:
        client = TestClient(app)

        response = client.get(
            f"/calls/{call_id}/events"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["call_id"] == call_id
        assert len(data["events"]) == 2

        first = data["events"][0]
        second = data["events"][1]

        # Response contract
        assert set(first.keys()) == {
            "id",
            "call_id",
            "event_type",
            "from_state",
            "to_state",
            "created_at",
        }

        assert set(second.keys()) == {
            "id",
            "call_id",
            "event_type",
            "from_state",
            "to_state",
            "created_at",
        }

        # First event
        assert first["id"] == state_event.id
        assert first["call_id"] == call_id
        assert first["event_type"] == "STATE_CHANGED"
        assert first["from_state"] == "CALL_CONNECTED"
        assert first["to_state"] == "INTRODUCTION"
        assert first["created_at"] is not None

        # Second event
        assert second["id"] == auth_event.id
        assert second["call_id"] == call_id
        assert second["event_type"] == "AUTHENTICATION"
        assert second["from_state"] == "AUTHENTICATION"
        assert second["to_state"] == "DISCLOSE_OVERDUE"
        assert second["created_at"] is not None

    finally:
        app.dependency_overrides.clear()


def test_get_call_events_preserves_event_order(
    db_session,
):
    from app.db.repositories.call_log_repository import (
        CallLogRepository,
    )
    from app.db.repositories.call_event_repository import (
        CallEventRepository,
    )
    from app.models.call_log import CallLog
    from app.services.call_event_service import (
        CallEventService,
    )

    call_id = "event_route_order_001"

    CallLogRepository(db_session).create(
        CallLog(
            call_id=call_id,
            customer_id=None,
            started_at=datetime.utcnow(),
        )
    )

    service = CallEventService(
        CallEventRepository(db_session)
    )

    service.record_state_change(
        call_id=call_id,
        from_state="CALL_CONNECTED",
        to_state="INTRODUCTION",
    )

    service.record_state_change(
        call_id=call_id,
        from_state="INTRODUCTION",
        to_state="CHECK_PERSON",
    )

    service.record_state_change(
        call_id=call_id,
        from_state="CHECK_PERSON",
        to_state="AUTHENTICATION",
    )

    app.dependency_overrides[get_db] = (
        lambda: db_session
    )

    try:
        client = TestClient(app)

        response = client.get(
            f"/calls/{call_id}/events"
        )

        assert response.status_code == 200

        events = response.json()["events"]

        assert len(events) == 3

        assert events[0]["from_state"] == "CALL_CONNECTED"
        assert events[0]["to_state"] == "INTRODUCTION"

        assert events[1]["from_state"] == "INTRODUCTION"
        assert events[1]["to_state"] == "CHECK_PERSON"

        assert events[2]["from_state"] == "CHECK_PERSON"
        assert events[2]["to_state"] == "AUTHENTICATION"

        created_at = [
            event["created_at"]
            for event in events
        ]

        assert created_at == sorted(created_at)

    finally:
        app.dependency_overrides.clear()


def test_get_call_events_returns_empty_list(
    db_session,
):
    from app.db.repositories.call_log_repository import (
        CallLogRepository,
    )
    from app.models.call_log import CallLog

    call_id = "event_route_002"

    CallLogRepository(db_session).create(
        CallLog(
            call_id=call_id,
            customer_id=None,
            started_at=datetime.utcnow(),
        )
    )

    app.dependency_overrides[get_db] = (
        lambda: db_session
    )

    try:
        client = TestClient(app)

        response = client.get(
            f"/calls/{call_id}/events"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["call_id"] == call_id
        assert data["events"] == []

    finally:
        app.dependency_overrides.clear()

def test_get_call_events_for_unknown_call_returns_empty_list(
    db_session,
):
    call_id = "event_route_unknown_001"

    app.dependency_overrides[get_db] = (
        lambda: db_session
    )

    try:
        client = TestClient(app)

        response = client.get(
            f"/calls/{call_id}/events"
        )

        assert response.status_code == 200

        data = response.json()

        assert data["call_id"] == call_id
        assert data["events"] == []

    finally:
        app.dependency_overrides.clear()
