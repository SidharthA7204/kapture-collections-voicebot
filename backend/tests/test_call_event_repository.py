from datetime import datetime

from app.db.repositories.call_event_repository import (
    CallEventRepository,
)
from app.db.repositories.call_log_repository import (
    CallLogRepository,
)

from app.models.call_event import CallEvent
from app.models.call_log import CallLog


def create_call_log(
    db_session,
    call_id: str,
):
    return CallLogRepository(db_session).create(
        CallLog(
            call_id=call_id,
            started_at=datetime.now(),
        )
    )


def test_create_call_event(db_session):
    call_id = "event_repo_001"

    create_call_log(
        db_session,
        call_id,
    )

    repository = CallEventRepository(db_session)

    event = CallEvent(
        call_id=call_id,
        event_type="STATE_CHANGED",
        from_state="CALL_CONNECTED",
        to_state="INTRODUCTION",
    )

    created = repository.create(event)

    assert created.id is not None
    assert created.call_id == call_id
    assert created.event_type == "STATE_CHANGED"
    assert created.from_state == "CALL_CONNECTED"
    assert created.to_state == "INTRODUCTION"


def test_get_events_by_call_id(db_session):
    call_id = "event_repo_002"

    create_call_log(
        db_session,
        call_id,
    )

    repository = CallEventRepository(db_session)

    repository.create(
        CallEvent(
            call_id=call_id,
            event_type="STATE_CHANGED",
            from_state="CALL_CONNECTED",
            to_state="INTRODUCTION",
        )
    )

    repository.create(
        CallEvent(
            call_id=call_id,
            event_type="STATE_CHANGED",
            from_state="INTRODUCTION",
            to_state="CHECK_PERSON",
        )
    )

    events = repository.get_by_call_id(
        call_id
    )

    assert len(events) == 2

    assert (
        events[0].from_state
        == "CALL_CONNECTED"
    )

    assert (
        events[0].to_state
        == "INTRODUCTION"
    )

    assert (
        events[1].from_state
        == "INTRODUCTION"
    )

    assert (
        events[1].to_state
        == "CHECK_PERSON"
    )