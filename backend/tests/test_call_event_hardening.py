from datetime import datetime

from app.db.repositories.call_event_repository import (
    CallEventRepository,
)
from app.db.repositories.call_log_repository import (
    CallLogRepository,
)
from app.db.repositories.customer_repository import (
    CustomerRepository,
)
from app.models.call_log import CallLog
from app.models.customer import Customer
from app.services.customer_verification_service import (
    CustomerVerificationService,
)
from app.state.states import CallState

from tests.test_call_event_integration import (
    create_service,
)


def create_call_log(
    db_session,
    call_id: str,
):
    return CallLogRepository(db_session).create(
        CallLog(
            call_id=call_id,
            customer_id=None,
            started_at=datetime.utcnow(),
        )
    )


def move_to_authentication(
    service,
    call_id,
    machine,
):
    for state in (
        CallState.INTRODUCTION,
        CallState.CHECK_PERSON,
        CallState.AUTHENTICATION,
    ):
        service.transition(
            call_id=call_id,
            machine=machine,
            next_state=state,
        )


def test_end_call_creates_single_call_ended_event(
    db_session,
):
    call_id = "audit_hardening_end_001"

    service = create_service(db_session)

    machine, _, _ = service.start_call(
        call_id=call_id,
        customer_id=None,
    )

    move_to_authentication(
        service,
        call_id,
        machine,
    )

    service.end_call(
        call_id=call_id,
        machine=machine,
    )

    events = (
        CallEventRepository(db_session)
        .get_by_call_id(call_id)
    )

    ended_events = [
        event
        for event in events
        if event.event_type == "CALL_ENDED"
    ]

    assert len(ended_events) == 1
    assert ended_events[0].to_state == "END"


def test_repeated_end_call_does_not_duplicate_call_ended_event(
    db_session,
):
    call_id = "audit_hardening_end_002"

    service = create_service(db_session)

    machine, _, _ = service.start_call(
        call_id=call_id,
        customer_id=None,
    )

    move_to_authentication(
        service,
        call_id,
        machine,
    )

    service.end_call(
        call_id=call_id,
        machine=machine,
    )

    restored_machine = service.restore_machine(
        call_id
    )

    service.end_call(
        call_id=call_id,
        machine=restored_machine,
    )

    events = (
        CallEventRepository(db_session)
        .get_by_call_id(call_id)
    )

    ended_events = [
        event
        for event in events
        if event.event_type == "CALL_ENDED"
    ]

    assert len(ended_events) == 1


def test_three_verification_failures_create_three_failure_events(
    db_session,
):
    customer = Customer(
        name="Audit Hardening Customer",
        phone="9876543210",
        dob=datetime(1995, 5, 15),
    )

    CustomerRepository(db_session).create(
        customer
    )

    call_id = "audit_hardening_verify_001"

    service = create_service(db_session)

    machine, _, _ = service.start_call(
        call_id=call_id,
        customer_id=customer.id,
    )

    move_to_authentication(
        service,
        call_id,
        machine,
    )

    for _ in range(3):
        service.verify_customer(
            call_id=call_id,
            machine=machine,
            phone="9999999999",
            dob=datetime(
                1995,
                5,
                15,
            ).date(),
        )

    events = (
        CallEventRepository(db_session)
        .get_by_call_id(call_id)
    )

    verification_failures = [
        event
        for event in events
        if event.event_type
        == "VERIFICATION_FAILED"
    ]

    ended_events = [
        event
        for event in events
        if event.event_type == "CALL_ENDED"
    ]

    assert len(verification_failures) == 3
    assert len(ended_events) == 1

    assert machine.current_state == CallState.END


def test_call_events_are_returned_in_chronological_order(
    db_session,
):
    call_id = "audit_hardening_order_001"

    service = create_service(db_session)

    machine, _, _ = service.start_call(
        call_id=call_id,
        customer_id=None,
    )

    move_to_authentication(
        service,
        call_id,
        machine,
    )

    service.authenticate(
        call_id=call_id,
        machine=machine,
    )

    service.transition(
        call_id=call_id,
        machine=machine,
        next_state=CallState.INTENT_HANDLING,
    )

    service.end_call(
        call_id=call_id,
        machine=machine,
    )

    events = (
        CallEventRepository(db_session)
        .get_by_call_id(call_id)
    )

    assert len(events) == 8

    created_times = [
        event.created_at
        for event in events
    ]

    assert created_times == sorted(created_times)

    assert events[0].event_type == "STATE_CHANGED"
    assert events[-1].event_type == "CALL_ENDED"
    assert events[-1].to_state == "END"
