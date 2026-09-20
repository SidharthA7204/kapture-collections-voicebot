from datetime import datetime

from app.db.repositories.call_event_repository import (
    CallEventRepository,
)
from app.db.repositories.call_log_repository import (
    CallLogRepository,
)
from app.db.repositories.call_event_repository import (
    CallEventRepository,
)
from app.models.call_event import CallEvent
from app.models.call_log import CallLog
from app.services.call_event_service import (
    CallEventService,
)


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


def test_record_state_change(db_session):
    call_id = "event_service_001"

    create_call_log(db_session, call_id)

    service = CallEventService(
        CallEventRepository(db_session)
    )

    event = service.record_state_change(
        call_id=call_id,
        from_state="CALL_CONNECTED",
        to_state="INTRODUCTION",
    )

    assert event.id is not None
    assert event.call_id == call_id
    assert event.event_type == "STATE_CHANGED"
    assert event.from_state == "CALL_CONNECTED"
    assert event.to_state == "INTRODUCTION"


def test_get_call_events(db_session):
    call_id = "event_service_002"

    create_call_log(db_session, call_id)

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

    events = service.get_call_events(call_id)

    assert len(events) == 2
    assert events[0].to_state == "INTRODUCTION"
    assert events[1].to_state == "CHECK_PERSON"


def test_record_authentication(db_session):
    call_id = "event_service_auth_001"

    create_call_log(db_session, call_id)

    service = CallEventService(
        CallEventRepository(db_session)
    )

    event = service.record_authentication(
        call_id=call_id,
    )

    assert event.id is not None
    assert event.call_id == call_id
    assert event.event_type == "AUTHENTICATION"
    assert event.from_state == "AUTHENTICATION"
    assert event.to_state == "DISCLOSE_OVERDUE"


def test_record_authentication_failed(db_session):
    call_id = "event_service_auth_002"

    create_call_log(db_session, call_id)

    service = CallEventService(
        CallEventRepository(db_session)
    )

    event = service.record_authentication_failed(
        call_id=call_id,
    )

    assert event.id is not None
    assert event.call_id == call_id
    assert event.event_type == "AUTHENTICATION_FAILED"
    assert event.from_state == "AUTHENTICATION"
    assert event.to_state == "END"


def test_record_verification_success(db_session):
    call_id = "event_service_verify_001"

    create_call_log(db_session, call_id)

    service = CallEventService(
        CallEventRepository(db_session)
    )

    event = service.record_verification_success(
        call_id=call_id,
    )

    assert event.id is not None
    assert event.call_id == call_id
    assert event.event_type == "VERIFICATION_SUCCESS"
    assert event.from_state == "AUTHENTICATION"
    assert event.to_state == "DISCLOSE_OVERDUE"


def test_record_verification_failed(db_session):
    call_id = "event_service_verify_002"

    create_call_log(db_session, call_id)

    service = CallEventService(
        CallEventRepository(db_session)
    )

    event = service.record_verification_failed(
        call_id=call_id,
        to_state="AUTHENTICATION",
    )

    assert event.id is not None
    assert event.call_id == call_id
    assert event.event_type == "VERIFICATION_FAILED"
    assert event.from_state == "AUTHENTICATION"
    assert event.to_state == "AUTHENTICATION"


def test_record_call_ended(db_session):
    call_id = "event_service_end_001"

    create_call_log(db_session, call_id)

    service = CallEventService(
        CallEventRepository(db_session)
    )

    event = service.record_call_ended(
        call_id=call_id,
    )

    assert event.id is not None
    assert event.call_id == call_id
    assert event.event_type == "CALL_ENDED"
    assert event.from_state is None
    assert event.to_state == "END"


def test_get_call_events_returns_only_events_for_requested_call(
    db_session,
):
    call_id_one = "event_isolation_001"
    call_id_two = "event_isolation_002"

    create_call_log(
        db_session,
        call_id_one,
    )

    create_call_log(
        db_session,
        call_id_two,
    )

    service = CallEventService(
        CallEventRepository(db_session)
    )

    service.record_state_change(
        call_id=call_id_one,
        from_state="CALL_CONNECTED",
        to_state="INTRODUCTION",
    )

    service.record_state_change(
        call_id=call_id_two,
        from_state="CALL_CONNECTED",
        to_state="INTRODUCTION",
    )

    service.record_authentication(
        call_id=call_id_two,
    )

    events = service.get_call_events(
        call_id_one
    )

    assert len(events) == 1

    assert all(
        event.call_id == call_id_one
        for event in events
    )

    assert events[0].event_type == "STATE_CHANGED"
    assert events[0].to_state == "INTRODUCTION"
